<a id="5c2-preemption-with-real-victims"></a>
# 5.C2 — a real eviction: which pod died, on which node, and why that one

**Claim** — with two single-core workers genuinely full, one high-priority pod causes the scheduler to choose a node, choose a **minimal** set of victims on it, and evict them; the choice of node and the choice of victims are separately explicable from `selectVictimsOnNode`, and you can predict both before submitting the pod.

**Rests on** — [the nomination mechanism](25-priority-and-the-nominated-node.md) and [the victim-selection reading](26-selectvictimsonnode-and-a-pdb-that-forbids.md), both done on two nodes where there was only ever one candidate. This is [drill 5.C2](../../phases/05-scheduler.md#chaos) and [the capstone's core](37-the-capstone-narrative.md): the scarcity is real, not arranged, because [the lab ceiling produced it](../../strands/chaos.md#principle).

**Topology** — [`workhorse`](../../strands/lab-topologies.md#workhorse), continued.

**Setup** — fill the two workers **unevenly and with mixed priorities**, so that victim selection has something to choose between. Create the PriorityClasses from [exercise 25](25-priority-and-the-nominated-node.md) again on this cluster, plus one in between:

```sh
kubectl apply -f - <<'EOF'
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata: {name: academy-mid}
value: 5000
EOF
```

Then place, by hand and with `nodeName` where necessary, a mix on each worker: several `academy-low` pods of different sizes, and one or two `academy-mid`. Record the exact inventory — name, node, priority, CPU request — as a table before you start. **That table is the input to your prediction and the drill is worthless without it.**

**Do**

1. **Predict, in writing, all three answers**: which node the preemptor will take, which pods on it will be evicted, and how many. Then state the rule you used for each. If your rule for the victim set is "the smallest number of pods" you should also say what happens when two sets tie.

2. **Start the observers** — three sessions, because the drill is a sequence and the sequence is what the capstone narrates:

   ```sh
   kubectl -n sched-lab get pods -o wide -w
   kubectl get events -A -w --field-selector reason=Preempted
   while :; do date +%T.%N; kubectl -n sched-lab get pod raider \
     -o jsonpath='{.status.nominatedNodeName}{" "}{.spec.nodeName}{"\n"}' 2>/dev/null; sleep 0.2; done
   ```

3. **Submit the preemptor**, sized so that it fits on exactly one of the two workers after eviction:

   ```sh
   kubectl -n sched-lab run raider --image=registry.k8s.io/pause:3.9 --restart=Never \
     --overrides='{"spec":{"priorityClassName":"academy-high","containers":[{"name":"pause","image":"registry.k8s.io/pause:3.9","resources":{"requests":{"cpu":"700m"}}}]}}'
   ```

4. **Capture the queue transitions**, which is the part [the module asks you to narrate](../../phases/05-scheduler.md#m5-6) and the part that is gone in thirty seconds:

   ```sh
   kubectl get --raw /metrics | grep -E '^scheduler_pending_pods|^scheduler_preemption'
   kubectl -n sched-lab describe pod raider | sed -n '/Events/,$p'
   ```

   Take that metrics sample repeatedly through the sequence, not once at the end.

5. **Follow the victims.** A preempted pod owned by a Deployment gets replaced; a bare pod does not. Note which of yours were which, and where the replacements went:

   ```sh
   kubectl -n sched-lab get pods -o wide
   kubectl get events -A --field-selector reason=Preempted -o custom-columns=\
   TIME:.lastTimestamp,OBJ:.involvedObject.name,MSG:.message
   ```

6. **Score your prediction**, and where it was wrong, find the reason in the code you already read rather than in the event. The two most common surprises are the node choice (there is a scoring step among *candidate nodes* that most people forget) and a victim set larger than the minimum (because the pods do not divide evenly).

7. **Answer the capstone question now, while it is in front of you**: when did `raider` leave the unschedulable set, and was it moved by the victims' deletion or by the periodic flush? The metric labels from [exercise 23](23-the-hint-that-decides-a-retry.md) answer this and nothing else does.

**Observe** — the full timestamped sequence: nomination, `Preempted` events, victim termination, replacement pods being scheduled, preemptor bound.

**Expect** — a minimal victim set on one node, not a clearing of both. Expect the evicted pods to be the **lowest priority** ones that free enough, and expect the tie-break between equal-priority candidates to be a rule you can find rather than randomness.

Expect a replacement storm: victims owned by Deployments are recreated immediately and are then themselves unschedulable, so the cluster ends with the preemptor running and a new backlog of low-priority pods. **Preemption does not reduce demand; it re-orders it**, and a cluster that is permanently over-subscribed will preempt continuously. Note whether any replacement landed on the *other* worker, which is the only place the pressure could go.

Expect the handoff to be event-driven rather than flush-driven, and expect that to be checkable rather than assumed — the difference is between a second and several minutes, and it is the sharpest evidence in the phase that the hint machinery is doing real work.

**Write down** — the starting inventory table, your three predictions with the rules, the timestamped sequence, the scored result with a `selectVictimsOnNode` citation for each surprise, and the answer to step 7. This is the raw material for [the capstone](37-the-capstone-narrative.md); write it as if you will not remember any of it, because you will not.

**Footprint note** — the cluster is deliberately full, which is what the drill is. Both workers at their CPU limit means new pods will not schedule, including anything you forget to account for. `workhorse` 7.0GB plus `forge` 1536MB = 8.5GB, 1.0GB margin.

**Teardown** — `kubectl -n sched-lab delete pod --all` and `kubectl -n sched-lab delete deployment --all`, then confirm both workers are empty. Keep the three PriorityClasses. **The topology stays** — [5.C3](36-5c3-a-spread-nobody-can-satisfy.md) needs the same three nodes.
