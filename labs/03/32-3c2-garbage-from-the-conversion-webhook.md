<a id="3c2-garbage-from-the-conversion-webhook"></a>
# 3.C2 — every read of one resource type fails

**Claim** — a conversion webhook returning malformed objects breaks *reads*, not writes; the failure is scoped to one CRD and does not touch anything else in the cluster; and the repair is available because the broken path is not on the way to fixing it — which is exactly the property [3.C1](26-3c1-corrupt-a-cabundle.md) did not have.

**Rests on** — [3.C1](26-3c1-corrupt-a-cabundle.md), which this is the deliberate contrast to, and [the conversion webhook](28-the-conversion-webhook.md), which is the thing being broken. [The drill's framing](../../phases/03-api-machinery.md#chaos) sets the question.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [the aggregation exercise](31-an-apiservice-routes-out-of-process.md).

**Setup — write the escape hatch down first, as always.** Before breaking anything, establish and record the two exits:

1. `kubectl patch crd widgets.academy.k3ii.dev --type=merge -p '{"spec":{"conversion":{"strategy":"None"}}}'` — takes the webhook off the path entirely. Verify **now**, while everything works, that you can run this. Then set it back.
2. The Deployment rollback: `kubectl -n academy-build rollout undo deploy/academy-converter`.

Then populate: ten Widgets through `v1`, ten through `v2`. Confirm all twenty read cleanly through both versions.

**Do**

1. Break the handler. Pick **one** and note which — they fail differently, and choosing is part of the drill:

   | Break | One-line change |
   |---|---|
   | Wrong count | return `convertedObjects` with the last element dropped |
   | Wrong kind | set `kind: Gadget` on every converted object |
   | Dropped metadata | return the converted `spec` on a fresh object with empty `metadata` |
   | Invalid JSON | write a trailing `}` into the response body |

   Rebuild, push, `kubectl rollout restart deploy/academy-converter`, and wait for it to be `Available`.

2. Read. Then read wider, and keep a note of the first command in this list that fails:

   ```sh
   kubectl -n tenant get widgets.v2.academy.k3ii.dev
   kubectl -n tenant get widgets.v1.academy.k3ii.dev    # the storage version
   kubectl -n tenant get widget one-name -o yaml
   kubectl get widgets -A
   kubectl get pods -A
   kubectl get all -n tenant
   ```

3. Write. Predict first: does creating a **new** `v1` Widget succeed?

4. Delete one. Predict first.

5. Find the blast radius from the apiserver's side, on `.130`:

   ```sh
   ssh zain@10.10.10.130 'sudo crictl logs $(sudo crictl ps -q --name kube-apiserver) 2>&1 | tail -60'
   kubectl get --raw /metrics | grep -E 'apiserver_request_total\{.*widgets' | head
   kubectl get --raw /metrics | grep apiextensions
   ```

6. Repair with exit 2. Then, separately, ask what would have happened if the conversion webhook had been serving the CRD that stored your `cert-manager` `Certificate` objects.

**Observe** — the exact error text, which of the six commands in step 2 failed, and whether the failure is per-object or per-list.

**Expect** — reads through the **non-storage** version fail. Reads through the storage version may succeed, and whether they do depends on which break you chose — the conversion webhook is invoked when the requested version differs from the stored one, so a `v1` read of a `v1`-stored object can bypass it entirely. That asymmetry is the finding; the drill's framing says "every read of that CRD's objects" and the truth is narrower and more useful.

`kubectl get pods`, `kubectl get all -n tenant` and everything outside the group keep working. Compare against [step 4 of the aggregation exercise](31-an-apiservice-routes-out-of-process.md), where one broken component *did* break unrelated discovery: an `APIService` participates in discovery, a CRD's conversion does not. Two extension mechanisms, two blast radii.

Writes: a create through `v1` while `v1` is the storage version does **not** call the conversion webhook and succeeds. A create through `v2` fails. Deletes succeed, and `kubectl delete widget x` may still print an error because it fetched the object first — the delete happened anyway. Check that rather than believing the exit code.

The repair works, and the reason it works is worth stating explicitly next to 3.C1: `Deployment`, `ReplicaSet` and `Pod` are not `Widget`s, so nothing on the path to the fix passes through the broken conversion. **A broken extension is survivable exactly when it does not sit under its own repair path.** Step 6's question is the general form of that, and the answer is why [the self-exclusion](24-matchconditions-stop-the-call.md) is a habit rather than a trick.

**Write down** — which break you chose and its exact error, the first-failing command from step 2, the storage-version asymmetry, the write and delete results against your predictions, and one sentence stating the survivability rule. Add the new error text to [the running list of look-alike failures](04-mis-sign-a-client-cert.md) if it belongs there — decide, and say why either way.

**Teardown** — restore the handler, redeploy, confirm all twenty Widgets read cleanly through both versions. Delete the Widgets, the `Widget` CRD, the `APIService`, and the three webhook Deployments with their configurations — **module 3.4's whole apparatus goes here**, because [module 3.5](33-overflow-the-ring.md) needs a cluster whose watch traffic is yours and not your webhooks'. **The topology stays.**
