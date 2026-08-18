<a id="what-assume-buys"></a>
# The node that fits ten times because the cache has not caught up

**Claim** — a scheduler that computes fit from its informer cache alone will overcommit a node under a burst, because the pods it bound moments ago are not in that cache yet; the real scheduler avoids this with one step you did not implement, and the failure shows up not as a scheduling error but as a **kubelet rejection**, several seconds later, on the wrong side of the system.

**Rests on** — [the from-scratch scheduler](09-two-hundred-lines-that-schedule.md) — specifically its `fit.go`, which reads assigned pods from the lister. This is module 5.2's write-down and the reason [the boundary you drew](03-two-cycles-not-one.md) has a cache operation on it.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with your scheduler running under its own name.

**Setup** — make the arithmetic tight enough that being wrong once is visible. Find the worker's allocatable CPU and pick a request that divides it into a small number:

```sh
kubectl get node <worker-node> -o jsonpath='{.status.allocatable.cpu}{"\n"}{.status.allocatable.memory}{"\n"}'
kubectl -n sched-lab get pods -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName,CPU:'.spec.containers[*].resources.requests.cpu'
```

**Do**

1. Submit the burst in **one** write, so that every pod appears in the informer within the same few milliseconds:

   ```sh
   kubectl -n sched-lab apply -f - <<'EOF'
   apiVersion: apps/v1
   kind: Deployment
   metadata: {name: burst}
   spec:
     replicas: 12
     selector: {matchLabels: {app: burst}}
     template:
       metadata: {labels: {app: burst}}
       spec:
         schedulerName: toy-scheduler
         containers:
         - name: pause
           image: registry.k8s.io/pause:3.9
           resources: {requests: {cpu: 400m, memory: 128Mi}}
   EOF
   ```

2. Watch where they land and what happens to them next:

   ```sh
   kubectl -n sched-lab get pods -o wide -w
   ```

3. Add up what your scheduler put on each node and compare it with what the node has:

   ```sh
   kubectl describe node <worker-node> | sed -n '/Allocated resources/,/^Events/p'
   kubectl -n sched-lab get pods -o wide | grep -c <worker-node>
   ```

4. Read the status of any pod that did not start:

   ```sh
   kubectl -n sched-lab get pods -o custom-columns=NAME:.metadata.name,PHASE:.status.phase,REASON:.status.reason,MSG:.status.message | grep -v Running
   ```

5. Now find the step you are missing. In the real scheduler, look for the call made **between** choosing a node and returning from the scheduling cycle:

   ```sh
   grep -n 'assume\|Assume' pkg/scheduler/schedule_one.go | head
   grep -n 'func (cache \*cacheImpl) AssumePod\|forgetPod\|finishBinding' pkg/scheduler/backend/cache/cache.go | head
   ```

   Answer three questions from that code: what the cache holds for an assumed pod; what removes it if the bind fails; and what removes it in the normal case, given that the bind succeeded and the pod will arrive through the informer under its own steam. The third has a subtlety worth writing down — the assumed entry has to survive until the *real* one arrives, and something has to notice that it did.

6. Fix your own scheduler with the smallest possible version: a map from node name to the requests of pods you have bound but not yet seen in the lister, added at bind time and removed when the informer delivers the pod with that node set. Re-run step 1.

**Observe** — the placement counts before and after step 6, and the phase and reason of every pod that failed to start in the first run.

**Expect** — the first run to put far more on one node than fits, and the excess pods to reach `Failed` with a reason from the **kubelet**, not the scheduler: the node admits pods only up to its own accounting, and rejects the rest after they have already been bound to it. That is the shape of the bug: the scheduler was satisfied, the API server was satisfied, and the component that said no is the one that cannot reschedule anything.

Expect step 6 to fix it completely on a two-node cluster, and expect to be able to state precisely why the real scheduler's version is more complicated than yours: yours is a map that a single goroutine reads and writes, and [the binding cycle runs concurrently](03-two-cycles-not-one.md).

Expect one further consequence to fall out for free — with the assumed-pods map in place, the *time* your scheduler takes per pod is unchanged, but the number of pods it places correctly per burst is not. **`assume` is a correctness mechanism that looks like a performance one.**

**Write down** — the two placement counts, the kubelet's rejection reason verbatim, the answers to the three source questions from step 5 with `file:line`, and one sentence naming what would go wrong with your map if the bind POST failed and you did not remove the entry.

**Footprint note** — twelve pause pods, deliberately over-requesting. No build beyond your own artifact. 7.5GB total.

**Teardown** — `kubectl -n sched-lab delete deployment burst`, and delete any pod left in `Failed`: `kubectl -n sched-lab delete pod --field-selector status.phase=Failed`. Failed pods are not garbage-collected promptly and they will distort the counts in [module 5.3](12-one-pod-through-schedule-one.md). **The topology stays.**
