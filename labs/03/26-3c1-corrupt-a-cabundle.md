<a id="3c1-corrupt-a-cabundle"></a>
# 3.C1 — a flipped byte that blocks the write that would fix it

**Claim** — corrupting one byte of `caBundle` on a `failurePolicy: Fail` webhook produces an outage you can diagnose from the apiserver log alone, and — if the webhook selects the namespace its own Deployment lives in — an outage in which the repair is itself blocked. The escape hatch has to be named before the byte is flipped.

**Rests on** — [the match conditions](24-matchconditions-stop-the-call.md), where the `academy-build` exclusion was added deliberately, and [the two `x509` strings](19-change-one-san.md). This drill **originates in this phase** and is [borrowed by the chaos strand](../../strands/chaos.md#borrowed-drills); the mechanism lives here.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [the plugin](25-a-kubectl-plugin.md).

**Setup — the escape hatch, written down first**

Before touching anything, write the three ways out, in the order you would try them, and keep the note somewhere that is not the cluster:

1. Delete the `ValidatingWebhookConfiguration`. It is a cluster-scoped object and nothing about a broken webhook prevents deleting its own registration.
2. Narrow it — add or restore a `namespaceSelector` / `matchConditions` exclusion so the repair path is not intercepted.
3. Flip `failurePolicy` to `Ignore`.

All three are single-object edits and all three require the apiserver to accept an edit to an `admissionregistration.k8s.io` object — which your webhook does not match, because its `rules` name `pods`. **Say why that matters**: a webhook whose rules include `*` on `*` has no escape hatch of this kind, which is the actual reason clusters die this way.

Then take the sharp version seriously: **remove the `academy-build` exclusion** you added in [the match conditions exercise](24-matchconditions-stop-the-call.md), and set `namespaceSelector: {}` so the webhook matches every namespace including its own.

**Do**

1. Record the good bundle's length, then corrupt one byte in the middle of it:

   ```sh
   kubectl get validatingwebhookconfiguration academy-memlimit \
     -o jsonpath='{.webhooks[0].clientConfig.caBundle}' > /tmp/good.b64
   wc -c /tmp/good.b64
   python3 - <<'PY' > /tmp/bad.b64
   b = open('/tmp/good.b64').read().strip()
   i = len(b)//2
   c = 'A' if b[i] != 'A' else 'B'
   print(b[:i] + c + b[i+1:], end='')
   PY
   kubectl patch validatingwebhookconfiguration academy-memlimit --type=json \
     -p "[{\"op\":\"replace\",\"path\":\"/webhooks/0/clientConfig/caBundle\",\"value\":\"$(cat /tmp/bad.b64)\"}]"
   ```

2. Diagnose **from the apiserver log only**. Start a clock.

   ```sh
   kubectl -n tenant run casualty --image=busybox --restart=Never
   ```

3. Now attempt the repairs that a reflex would reach for first, in this order, and note which are blocked:
   - `kubectl -n academy-build rollout restart deploy/academy-webhook`
   - `kubectl -n academy-build delete pod -l app=academy-webhook`
   - `kubectl -n academy-build scale deploy/academy-webhook --replicas=2`
   - re-applying the good `caBundle`

4. Recover by whichever hatch you reach for. Then put the cluster back.

**Observe**

```sh
ssh zain@10.10.10.130 'sudo crictl logs $(sudo crictl ps -q --name kube-apiserver) 2>&1 | tail -20'
kubectl whoadmits pods -n academy-build --verb=create
kubectl get validatingwebhookconfiguration academy-memlimit -o jsonpath='{.webhooks[0].failurePolicy}{"\n"}'
```

**Expect** — `x509: certificate signed by unknown authority`, the same string [the wrong-CA certificate produced](19-change-one-san.md), from a third distinct cause: the bundle no longer decodes to a certificate that signed the serving cert. **Three causes, one string.** That is the drill's teaching point and the reason the log alone is not always enough — the log tells you *the trust relationship is broken*, not *which side of it you broke*.

The three repairs in step 3 divide cleanly: **anything that creates a Pod is blocked** — the rollout restart, the delete (which creates a replacement), the scale. Re-applying the `caBundle` is **not** blocked, because it is a write to a `ValidatingWebhookConfiguration` and the webhook's rules do not match that resource. That asymmetry is the whole escape-hatch argument, and having it in your hands rather than in a paragraph is why this drill exists.

`kubectl whoadmits` earns itself here: it answers *"what would block this"* without attempting the write, which during an outage is the difference between a diagnosis and another failed command.

The trap is the byte you flip. Base64 is four-characters-to-three-bytes, so a single character change may corrupt the certificate structure entirely (`failed to parse`) rather than merely producing a different valid-looking CA. Both are instructive; record which you got, and check `wc -c` against the number you wrote down in [the CA exercise](17-a-ca-and-a-serving-cert-by-hand.md) to prove it was a flip and not a truncation.

**Write down** — the apiserver log line, the four-row repair table (attempted · blocked? · why), which hatch you used and how long the whole thing took, and the sentence [the phase file's chaos section asks for](../../phases/03-api-machinery.md#chaos): why a broken admission webhook can wedge *every* write including the one that fixes it. Add the third cause to [the running list of identical-looking failures](04-mis-sign-a-client-cert.md) — it is now five entries and one of the strings appears three times.

**Teardown** — restore the good `caBundle` from `/tmp/good.b64`, restore the `academy-build` exclusion and the `academy: "yes"` `namespaceSelector`, delete `/tmp/good.b64` and `/tmp/bad.b64`, and confirm the webhook admits and denies correctly again. Delete any pods. **The topology stays** — [the CRD module](27-a-two-version-crd.md) continues on it, and both webhooks stay up because [the conversion webhook](28-the-conversion-webhook.md) is deployed beside them.
