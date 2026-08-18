<a id="reinvocation-observed"></a>
# The webhook that has to run twice, and the pod that proves it

**Claim** — with two mutating webhooks where the second adds a container the first would have modified, `reinvocationPolicy: Never` produces a pod that violates the rule the first webhook exists to enforce, and `IfNeeded` produces one that does not. Your prediction table from the reading either survives this or does not.

**Rests on** — [the written prediction table](15-why-a-mutating-webhook-reruns.md), which must be written *before* this exercise is run, and [the mutating webhook](22-the-mutating-webhook-cert-manager-signs.md).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [the mutating webhook](22-the-mutating-webhook-cert-manager-signs.md).

**Setup**

Add a second route to the **same** mutating binary — no new artifact, no new image tag beyond a rebuild:

- `/mutate-sidecar` — appends a container named `sidecar`, image `busybox`, **with no resource limits**, to any pod that does not already have one.

Register it as a second `MutatingWebhookConfiguration` named `academy-sidecar`, reusing the same Service, Secret and `inject-ca-from` annotation. Order it **after** `academy-mutator`: webhook configurations are invoked in lexical order of the configuration object's name, so the names have to be chosen, not assumed.

**Do**

1. Confirm the order before relying on it:

   ```sh
   kubectl get mutatingwebhookconfigurations -o name | sort
   ```

2. With `academy-mutator` at its default `reinvocationPolicy` (`Never`), create a bare pod:

   ```sh
   kubectl -n tenant run r1 --image=busybox --restart=Never
   ```

3. Set `reinvocationPolicy: IfNeeded` on `academy-mutator` only, and repeat with a new name.

4. Now the case that tests the *"at most once more"* half: set `IfNeeded` on **both**, and create a third pod. Predict, before running it, whether this loops.

**Observe**

```sh
kubectl -n tenant get pod r1 -o jsonpath='{range .spec.containers[*]}{.name}={.resources.limits.memory}{"\n"}{end}'
kubectl -n tenant get pod r2 -o jsonpath='{range .spec.containers[*]}{.name}={.resources.limits.memory}{"\n"}{end}'
kubectl -n academy-build logs deploy/academy-mutator | grep -c 'path=/mutate-pods'
kubectl -n academy-build logs deploy/academy-mutator | grep 'uid=' | awk '{print $0}' | sort | uniq -c
```

The last line is the measurement that matters: **count the calls per `AdmissionReview` uid**, not the calls in total.

**Expect** — `r1` has two containers and only one of them has a memory limit. The sidecar was added after `academy-mutator` had already run, `Never` meant it did not run again, and the resulting pod is exactly the object the first webhook exists to prevent. Note that the validating webhook then *rejects* it, so `r1` may not exist at all — which is the correct and slightly disorienting outcome: **the two mutating webhooks produced an object the validating webhook refused, and no single component was wrong.**

`r2` has two containers, both with `64Mi`, and the log shows `/mutate-pods` called **twice** for one uid.

Step 4 does not loop. The second pass is the last pass regardless of what happens during it, and the mechanism you named in [the reading](15-why-a-mutating-webhook-reruns.md) is what stops it — if your answer there was "it stops when nothing changes", this is where that answer is corrected, because nothing about the second pass is conditional on the object having stabilised.

**Write down** — the per-uid call counts, whether your three-row prediction table was right, and if it was wrong, **which of the three rows and why**. Then one sentence for a webhook author: what must be true of a handler for `IfNeeded` to be safe to set.

**Teardown** — delete the pods and the `academy-sidecar` webhook configuration; set `academy-mutator` back to `reinvocationPolicy: Never` so later exercises have one fewer moving part. Keep the `/mutate-sidecar` route in the code. **The topology stays.**
