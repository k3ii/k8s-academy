<a id="what-a-strategy-decides"></a>
# The fields the generic path could not have known to drop

**Claim** — a `RESTCreateStrategy` silently discards parts of the object you submitted, and which parts is per-resource information the generic store does not carry. Submit a Pod with a populated `status` and the stored object's status is empty; submit the same status through the `status` subresource and it is kept.

**Rests on** — [the call-order note](08-the-order-of-calls-in-create-go.md), which established that `BeforeCreate` runs inside `storage.Create`. `BeforeCreate` is where the strategy is consulted, so this exercise is the contents of a box that note left closed. [Module 3.1's strategy question](../../phases/03-api-machinery.md#m3-1).

**Topology** — **none.** `forge`, [the running apiserver](05-hand-start-an-apiserver.md).

**Do**

1. Read `pkg/registry/core/pod/strategy.go`, and answer three questions before running anything:
   - What does `PrepareForCreate` do to `pod.Status`, in one line of code?
   - What does `PrepareForUpdate` protect that `PrepareForCreate` does not have to?
   - `Canonicalize`, `AllowCreateOnUpdate`, `AllowUnconditionalUpdate` — for Pods, what does each return, and what would change if `AllowCreateOnUpdate` were true?

2. Submit a Pod that lies about its own status:

   ```sh
   kubectl --context=admin create -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata: {name: liar, namespace: default}
   spec:
     nodeName: nodeX
     containers: [{name: c, image: busybox}]
   status:
     phase: Running
     message: "I am definitely running"
     podIP: 10.0.0.99
   YAML
   ```

3. Ask for it back, and read what survived.

4. Now write the same status through the subresource, which is a *different endpoint with a different strategy*:

   ```sh
   kubectl --context=admin patch pod liar --subresource=status --type=merge \
     -p '{"status":{"phase":"Running","message":"I am definitely running","podIP":"10.0.0.99"}}'
   ```

5. Try the reverse asymmetry: patch `spec.containers[0].image` through the main resource (allowed), and then patch `spec.nodeName` (not).

   ```sh
   kubectl --context=admin patch pod liar --type=merge -p '{"spec":{"containers":[{"name":"c","image":"alpine"}]}}'
   kubectl --context=admin patch pod liar --type=merge -p '{"spec":{"nodeName":"nodeY"}}'
   ```

**Observe**

```sh
kubectl --context=admin get pod liar -o jsonpath='{.status}{"\n"}'
kubectl --context=admin get pod liar -o jsonpath='{.spec.containers[0].image}{"\n"}'
etcdctl --endpoints=http://127.0.0.1:2379 get /registry/pods/default/liar | strings | grep -i running
```

**Expect** — after step 2 the stored `status.phase` is `Pending` and `message` and `podIP` are gone. Nothing rejected your input and no error was returned: **the write succeeded and part of it was dropped**, which is a materially different contract from validation and is the single most common surprise for anyone writing a controller.

After step 4 the status is exactly what you asked for. Same object, same fields, different endpoint — and the difference is entirely in which strategy the registry consulted.

Step 5's second patch is *rejected*, not dropped: `spec: Forbidden: pod updates may not change fields other than ...`. Three different behaviours for three writes to the same object — kept, silently dropped, explicitly refused — and being able to say which is which without experimenting is what a strategy is for.

The image patch is the one to be careful about reading. It succeeds, and it is the only `spec` field on a Pod that may be changed after creation for reasons that are historical rather than principled; do not generalise from it.

**Write down** — the three-behaviour table (field · endpoint · kept / dropped / refused), the one line of `PrepareForCreate` that does the dropping, and one sentence naming what the generic store would have had to be told in order to do this itself. That sentence is the answer to *"what does a strategy decide that the generic path cannot?"*

**Teardown** — `kubectl --context=admin delete pod liar --force --grace-period=0`. **The apiserver and etcd stay up** — [module 3.2](../../phases/03-api-machinery.md#m3-2) runs on the same pair of processes. **No topology is up.**
