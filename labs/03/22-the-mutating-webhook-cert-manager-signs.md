<a id="the-mutating-webhook-cert-manager-signs"></a>
# The second webhook, with the certificate handled for you

**Artifact** — the phase's second build-track artifact: a **mutating** admission webhook in `build/03-mutating-webhook/` that injects a default memory limit into any container lacking one, deployed in `academy-build`, with its serving certificate issued by `cert-manager` and its `caBundle` written into the webhook configuration by `ca-injector` — not by you.

**Rests on** — [the hand-certed webhook](21-the-webhook-behind-a-service.md). The automation only teaches anything against the shape you already built by hand; [the strand puts `openssl` first for exactly this reason](../../strands/build-mechanics.md#webhook-tls) and the reason is not repeated here.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [stage 2](21-the-webhook-behind-a-service.md).

**Setup**

Install `cert-manager` from its release manifest, and read the footprint note below first.

```sh
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
kubectl -n cert-manager rollout status deploy/cert-manager-webhook --timeout=5m
```

Note before you go further: **`cert-manager` ships its own admission webhook.** You now have a cluster in which installing a tool that helps you run webhooks required running a webhook, and if it is unhealthy, `Certificate` objects cannot be created. Say that out loud once.

**Build**

```
build/03-mutating-webhook/
  go.mod
  main.go          TLS server, one route: /mutate-pods
  mutate.go        the patch construction
  mutate_test.go   table test: input pod → expected JSON Patch
```

What it must implement:

1. **A JSON Patch, not a modified object.** The response carries `patchType: JSONPatch` and `patch` as base64 of an RFC 6902 document. Build the patch by *diffing intent*, not by serialising the whole pod — a webhook that returns a patch replacing `/spec` will fight every other webhook in the chain.
2. **The rule**: for each container with no `resources.limits.memory`, add one of `64Mi`. Containers that already have one are untouched, and the patch must be **empty** when nothing needs changing — an empty patch and no patch are different responses and only one of them is correct.
3. **Idempotency, deliberately.** Applying your own output to your own input must produce an empty patch. [The reinvocation reading](15-why-a-mutating-webhook-reruns.md) said this was a requirement rather than good manners; this is where it is enforced, and `mutate_test.go` should have a case that runs the handler twice.
4. **The same request log** as [the validating webhook](18-the-webhook-the-apiserver-dials.md): path, namespace, name, and whether a patch was produced. [The next exercise](23-reinvocation-observed.md) reads only this.

Certificate, the `cert-manager` way — a self-signed issuer, a `Certificate`, and the annotation that injects the bundle:

```sh
kubectl -n academy-build apply -f - <<'YAML'
apiVersion: cert-manager.io/v1
kind: Issuer
metadata: {name: selfsigned}
spec: {selfSigned: {}}
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata: {name: academy-mutator}
spec:
  secretName: academy-mutator-tls
  issuerRef: {name: selfsigned, kind: Issuer}
  dnsNames:
    - academy-mutator.academy-build.svc
    - academy-mutator.academy-build.svc.cluster.local
YAML
```

and on the `MutatingWebhookConfiguration`, in place of a `caBundle` you computed:

```yaml
metadata:
  annotations:
    cert-manager.io/inject-ca-from: academy-build/academy-mutator
```

Order the webhook so it runs **before** the validating one — which needs no configuration at all, and being able to say *why* is half of this exercise.

**Gate** — [tier 2](../../strands/build-mechanics.md#gates). The claim: **"a mutating webhook's patch is applied to the object before the next mutating webhook sees it, and before any validating webhook sees it — cited to ⟨`file:function`⟩ — which is why this webhook needs no configuration to run before the validating one."** Test it by temporarily making the validating webhook log the object it receives, and confirming the injected limit is present in it.

**Expect** — a pod with no memory limit is now **created successfully**, with `64Mi` on it, in the same namespace where [stage 1](18-the-webhook-the-apiserver-dials.md) refused it. The validating webhook still runs and still says yes, because by the time it looks, the object satisfies its rule. Two webhooks, no coordination, and a cooperative outcome that falls straight out of the two-phase ordering.

`ca-injector` writes `caBundle` within seconds of the `Certificate` becoming ready. Watch the field appear:

```sh
kubectl get mutatingwebhookconfiguration academy-mutator \
  -o jsonpath='{.webhooks[0].clientConfig.caBundle}' | head -c 40; echo
kubectl -n academy-build get certificate,secret
kubectl -n academy-build logs deploy/academy-mutator | tail
```

Compare that blob to `~/webhook-pki/ca.b64` from [the hand-certed path](17-a-ca-and-a-serving-cert-by-hand.md): different CA, identical shape, identical field. **The annotation automated a thing you can still do by hand in four commands**, which is a materially different relationship to a tool than treating it as opaque.

The first failure to expect is the annotation namespace: `inject-ca-from` takes `namespace/name` of the **Certificate**, and getting it wrong leaves `caBundle` empty, which fails as `x509: certificate signed by unknown authority` — [a string you have already met twice](19-change-one-san.md) arriving from a third cause.

**Write down** — the ordering claim with its citation, the four `openssl` commands the annotation replaced, and one sentence on what `cert-manager` adds that you cannot do by hand at all. (Rotation is the answer, and *why* rotation is hard by hand is the sentence.)

**Footprint note** — `cert-manager` is three Deployments: controller, webhook and cainjector, roughly **200–300Mi total** on a quiet cluster. Against the 2.0GB margin at `pair` + `forge` 2560MB it is affordable, and it is the only third-party install in the phase. Confirm rather than trust:

```sh
kubectl -n cert-manager top pod
```

If it lands materially above 300Mi, the smallest change is to scale `cert-manager-cainjector` to zero **after** the `caBundle` has been written — the injection is a one-off here and nothing re-triggers it. Record the number either way; it is the kind of figure [the topology strand does not yet have](../../strands/lab-topologies.md#unverified).

**Teardown** — delete the test pods. **Keep the mutating webhook, `cert-manager`, and both webhook configurations** — [reinvocation](23-reinvocation-observed.md) needs both webhooks and adds a third. **The topology stays.**
