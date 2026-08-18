<a id="two-hundred-lines-that-schedule"></a>
# Build artifact 1: a scheduler with no framework in it

**Artifact** — `build/05-scheduler-clientgo/`: a scheduler in plain `client-go` that watches for pods naming it, picks a node that fits, and binds. [Stage 1](../../strands/build-mechanics.md#two-stages) — `go run` on [`forge`](../../strands/lab-topologies.md#build-guest) against the live cluster's API, with [stage 2](30-a-second-scheduler-by-schedulername.md) a separate exercise.

**Rests on** — [the one POST](08-bind-a-pod-with-one-post.md) for the output side, and [the call path](01-the-sig-tour-in-call-order.md) for the shape it is deliberately *not* copying. This is the phase's centre: everything in modules 5.3 and 5.4 is the answer to "what does the real one do that this does not?"

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with [`forge` at 2560MB](07-fifteen-thirty-six-will-not-link-a-scheduler.md).

**Build**

```
build/05-scheduler-clientgo/
  cmd/toy-scheduler/main.go    flags, client, informers, signal handling, Run
  pkg/sched/
    scheduler.go               the loop: next pod, choose, bind, report
    fit.go                     the fit predicate, and nothing more
    bind.go                    the Binding POST and the event
```

What it must satisfy, as an interface rather than an implementation:

1. **A pod informer with a filter that is two conditions**: `spec.schedulerName` equals this scheduler's name (a flag, defaulting to `toy-scheduler`), and `spec.nodeName` is empty. A pod that fails either is not this program's business. Getting the second condition wrong is how you write a program that tries to bind pods that are already running, and the 409 from [exercise 8](08-bind-a-pod-with-one-post.md) is what you will see.

2. **A node informer and a lister**, not a `List` call per pod. The scheduler asks about every node for every pod and doing that against the API server would make its rate a function of node count times pod count.

3. **A fit predicate that only counts CPU and memory requests** against the node's allocatable, minus the requests of pods already assigned to that node. Nothing else — no taints, no affinity, no ports. The gaps are the point; you will name them in the write-up.

4. **A choice among the nodes that fit**, by a rule you can state in one sentence and defend. First-fit is acceptable. Whatever you pick, it must be *stated*, because [module 5.6](34-placement-that-differs-measurably.md) compares it against a real scoring plugin.

5. **The bind, and an event.** POST the `Binding`, and emit a `Scheduled` event on success and a `FailedScheduling` event with a reason on failure, so the pod is diagnosable with `kubectl describe` exactly as it was in [exercise 6](06-three-rejections-three-plugins.md).

6. **No retry cleverness, deliberately.** If no node fits, log it, emit the event, and drop the pod. Do not queue it, do not back off, do not re-enqueue on node changes. That absence is what [module 5.4](18-find-the-queue-yourself.md) is for, and building the queue now would rob it of its subject.

7. **A `--dry-run` flag** that does everything except the POST. You will want it in [exercise 10](10-5c4-two-schedulers-one-pod.md).

**Do**

```sh
cd ~/src/k8s-academy/build/05-scheduler-clientgo
go build ./... && go run ./cmd/toy-scheduler --kubeconfig=$HOME/.kube/config -v=2
```

```sh
kubectl -n sched-lab apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata: {name: mine}
spec:
  replicas: 4
  selector: {matchLabels: {app: mine}}
  template:
    metadata: {labels: {app: mine}}
    spec:
      schedulerName: toy-scheduler
      containers:
      - name: pause
        image: registry.k8s.io/pause:3.9
        resources: {requests: {cpu: 200m, memory: 64Mi}}
EOF
kubectl -n sched-lab get pods -o wide -w
```

Then two negative cases, both of which your program handles badly on purpose:

```sh
kubectl -n sched-lab scale deployment mine --replicas=40      # more than fits
kubectl -n sched-lab describe pod <one that stayed Pending> | sed -n '/Events/,$p'
```

**Gate** — [a falsifiable written claim](../../strands/build-mechanics.md#gates), which is this artifact's tier and the honest one for it: there is no upstream harness for a scheduler you invented. Write the claim so a hostile reader could check it and find it wrong. It must be about *this code against that cluster*, with a `file:line` in your source and a command that produces the counter-evidence if you are wrong. The strongest form is a statement about what your scheduler does that the default one does not, or does not do that the default one does — you will have several candidates by the end of step 3 below.

**Expect** — four pods placed within a second or so, spread according to whatever rule you chose. At forty replicas, the ones that do not fit get a `FailedScheduling` event **once** and are then ignored forever, even after you delete the running pods and free the whole cluster. That permanence is the finding, and it is the difference between a scheduler and a scheduling *loop*: nothing in your program is watching the world for reasons to reconsider.

Expect the placement to look wrong compared with the default scheduler, in a way you can defend. First-fit will pile everything onto one node until it is full. That is a legitimate scheduler; it is just a bad one.

Expect at least one pod to be placed on a node the default scheduler would have refused, because you did not implement taints. Confirm it, since it is the most concrete possible statement of what the default plugin set is worth.

**Write down** — the gate claim with its citation; the one-sentence statement of your choice rule; and the list of things the default set checks that your `fit.go` does not, taken from [your mapping](04-what-actually-runs-by-default.md) rather than from memory. That list is the spine of [the capstone](37-the-capstone-narrative.md).

**Footprint note** — one Go process on `forge`, of the shape [the strand measured at 564 MiB linking](../../strands/build-mechanics.md#measurements) — this artifact is `client-go` only and never links `k/k`, so it would in fact fit at 1536MB. The guest is at 2560MB anyway because [exercise 28](28-the-out-of-tree-plugin.md) genuinely needs it and resizing twice costs a reboot each time. `pair` gains a handful of pause pods. 7.5GB total, 2.0GB of margin.

**Teardown** — leave the scheduler running and the Deployment in place at 4 replicas; the next two exercises drive this artifact. Delete the excess: `kubectl -n sched-lab scale deployment mine --replicas=4`. **The topology stays.**
