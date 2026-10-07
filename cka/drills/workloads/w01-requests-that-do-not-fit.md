<a id="w01"></a>
# W1 — Requests that fit, then don't, and the event that says so

**Reflex** · **Core** · **10 min** · [`workhorse`](../../../strands/lab-topologies.md#workhorse) · Workloads and Scheduling / Pod admission and scheduling

> **The scheduler packs against `requests`, never against actual usage.** A node with 2 CPU and 50 MiB of real load will refuse a pod requesting 3 CPU, and a node pinned at 100% will happily take a pod that requests nothing. Internalising that one sentence resolves most scheduling questions.

**Do**

1. **Read the allocatable first**, do not assume it. `allocatable` is capacity minus reservations, and it is the number the scheduler uses. Note how much is already requested by what is running.
2. A pod requesting a comfortable fraction. It schedules. Read `kubectl describe node` and find your request added to the node's totals.
3. **Then one that cannot fit anywhere.** It stays `Pending`. Read the `FailedScheduling` event and the per-node reason — `Insufficient cpu`, with a count of nodes that failed each way. Learn to read that line; on the exam it is the answer, not a clue.
4. **Separate requests from limits.** Set a limit far above the request and watch it schedule on the request alone. Then exceed the memory limit inside the container and watch `OOMKilled` with a restart. CPU over-limit *throttles* instead of killing — different consequence, and the difference is asked.
5. **QoS class falls out of the two numbers.** Check `status.qosClass` on three pods: no requests or limits → `BestEffort`; requests equal to limits on every resource → `Guaranteed`; anything else → `Burstable`. That class decides eviction order under node pressure, which is the only reason it matters.
6. Scale a Deployment past what the cluster can hold and watch some replicas schedule and the rest sit `Pending`. A partly-scheduled Deployment is a normal state, not a broken one.

**Observe**

```sh
kubectl describe node <n> | sed -n '/Allocatable/,/Allocated resources/p'
kubectl describe node <n> | sed -n '/Allocated resources/,$p'
kubectl get pod big -o jsonpath='{.status.qosClass}{"\n"}'
kubectl describe pod big | sed -n '/Events/,$p'
kubectl get events --field-selector reason=FailedScheduling
```

**Done when** — you predict schedulable or not from the requests and the allocatable alone, and you reach for the event rather than the logs when a pod is `Pending`.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Fits, doesn't fit, read the event, all three QoS classes. | 10 min |
| **2** | A cluster already half-full. Work out what will fit before applying. | 8 min |
| **3** | Cold, no notes. Given a `Pending` pod, name the cause in one command. | 5 min |

**Teardown** — delete the namespace. Leave no pod holding a large request; it will quietly distort every later drill.

**See also** — **W2** and **W3** are the other two reasons a pod stays `Pending`; **TS1** is `Pending` met as a fault with the cause unknown.
