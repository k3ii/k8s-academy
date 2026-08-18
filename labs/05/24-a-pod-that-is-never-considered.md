<a id="a-pod-that-is-never-considered"></a>
# `SchedulingGated` — a pod the scheduler declines to look at

**Claim** — a pod carrying `spec.schedulingGates` never enters the active queue at all: it is held before any filter runs, it reports a distinct phase reason, it appears in a distinct queue in the metrics, and it produces **no** `FailedScheduling` event — which makes it the one pending state that cannot be confused with "the cluster is full".

**Rests on** — [the backlog drill](22-5c1-an-unschedulable-backlog.md), where every pending pod had a reason with a plugin's name on it. This one has no plugin, because the extension point that held it runs before the plugins that could refuse.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. Create a gated pod on an **empty** cluster, so there is no resource story at all:

   ```sh
   kubectl -n sched-lab scale deployment ballast --replicas=0
   kubectl -n sched-lab apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: {name: gated}
   spec:
     schedulingGates:
     - name: academy.k3ii.dev/not-yet
     containers: [{name: pause, image: registry.k8s.io/pause:3.9}]
   EOF
   kubectl -n sched-lab get pod gated
   kubectl -n sched-lab describe pod gated | sed -n '/Events/,$p'
   ```

2. Find it in the metrics, and note which gauge it is in:

   ```sh
   kubectl get --raw /metrics | grep '^scheduler_pending_pods'
   ```

3. Find the extension point that held it, and confirm from the source that it runs before the queue rather than inside the scheduling cycle:

   ```sh
   grep -rn 'PreEnqueue' pkg/scheduler/framework/interface.go pkg/scheduler/backend/queue/*.go | head
   grep -rn 'schedulingGates' pkg/scheduler/framework/plugins/schedulinggates/*.go
   ```

   Answer: which queue does a pod that fails `PreEnqueue` sit in, and what wakes it?

4. Try to modify the gates on the existing pod, and read the error:

   ```sh
   kubectl -n sched-lab patch pod gated --type=merge \
     -p '{"spec":{"schedulingGates":[{"name":"academy.k3ii.dev/not-yet"},{"name":"academy.k3ii.dev/second"}]}}'
   ```

5. Now remove the gate — the only mutation the API allows — and time what happens:

   ```sh
   date +%T.%N
   kubectl -n sched-lab patch pod gated --type=merge -p '{"spec":{"schedulingGates":null}}'
   kubectl -n sched-lab get pod gated -o wide
   ```

6. Read [KEP-3521](../../strands/source-reading.md#area-3-scheduler) for the motivation and answer the module's question: what class of problem needs a pod to exist, be visible to controllers, and be *unschedulable by construction* — rather than simply not being created until it is ready?

**Observe** — the pod's `status.conditions` while gated, the gauge it occupies, the API's response to step 4, and the delay in step 5.

**Expect** — a `PodScheduled=False` condition with reason `SchedulingGated`, its own entry in the pending-pods gauge, and **no event at all**. That silence is the diagnostic: a pod with no `FailedScheduling` event has either not been seen by any scheduler (the case in [exercise 8](08-bind-a-pod-with-one-post.md)) or has been gated. Two causes, one symptom, and the condition reason is what separates them.

Expect step 4 to be refused. Gates may be **removed** and not added or reordered on an existing pod, and the reason is exactly the reason a one-way door is safe: a controller can be trusted to open a gate, and a controller that could add one could strand a running workload's replacement forever.

Expect step 5 to be sub-second. Removing the last gate is a pod update that puts it straight into the active queue, and there is no backoff because there was never an attempt.

Expect the answer to step 6 to be about something that must exist before it can be scheduled — quota accounting, a batch queue that admits jobs in order, a resource that another controller has to provision first. Name one concrete case, and say what the alternative — simply not creating the pod until it is ready — would cost the controller that has to remember it instead.

**Write down** — the condition reason verbatim, the gauge label, the API's refusal message from step 4, the answer to step 3 with `file:line`, and your concrete case from step 6.

**Footprint note** — one pause pod, and a cluster deliberately emptied first so the negative result is unambiguous. 7.5GB total.

**Teardown** — `kubectl -n sched-lab delete pod gated ballast --ignore-not-found` and `kubectl -n sched-lab delete deployment ballast --ignore-not-found`. Module 5.5 wants a cluster with capacity, and every pod left here is capacity you will spend the next exercise wondering about. **The topology stays.**
