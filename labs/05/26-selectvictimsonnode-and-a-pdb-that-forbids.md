<a id="selectvictimsonnode-and-a-pdb-that-forbids"></a>
# A PodDisruptionBudget that makes preemption fail, and says so

**Claim** — `selectVictimsOnNode` accounts for `PodDisruptionBudget`s while choosing victims, and a budget that forbids the only viable eviction turns a preemption into a **refusal with an event** rather than a violated budget or a silent success; the preemptor stays pending and the running pods stay running.

**Rests on** — [the nomination mechanism](25-priority-and-the-nominated-node.md), where preemption succeeded. This is the same submission with one object added, and the negative result is the point.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, still filled with `academy-low` pods.

**Do**

1. **Read before you run.** Both files, in the order [the area gives them](../../strands/source-reading.md#area-3-scheduler):

   ```sh
   grep -n 'func .*selectVictimsOnNode' pkg/scheduler/framework/plugins/defaultpreemption/default_preemption.go
   sed -n '/func .*selectVictimsOnNode/,/^}/p' pkg/scheduler/framework/plugins/defaultpreemption/default_preemption.go
   grep -n 'pdb\|PodDisruptionBudget\|DisruptionsAllowed' pkg/scheduler/framework/preemption/preemption.go | head
   ```

   Answer three questions in writing: in what order are candidate pods considered for eviction; what makes a set of victims *sufficient*; and — the module's question — **where** the budget is accounted for. That last one has a surprising answer about *when*, which is worth stating precisely.

2. Note the two-pass structure. The algorithm removes a set of pods, checks, and then tries to put some back. Say what putting them back is for, in one sentence; the answer is the difference between a correct preemption and a wasteful one.

3. Make the budget. Cover the ballast pods with a budget that permits no disruption at all:

   ```sh
   kubectl -n sched-lab apply -f - <<'EOF'
   apiVersion: policy/v1
   kind: PodDisruptionBudget
   metadata: {name: no-disruption}
   spec:
     minAvailable: 3
     selector: {matchLabels: {app: ballast}}
   EOF
   kubectl -n sched-lab get pdb no-disruption
   ```

   Check `ALLOWED DISRUPTIONS` is zero before continuing. If it is not, the budget does not match what you think it matches, and the experiment would produce a successful preemption you would then misread.

4. Submit the same preemptor as before:

   ```sh
   kubectl -n sched-lab run bully --image=registry.k8s.io/pause:3.9 --restart=Never \
     --overrides='{"spec":{"priorityClassName":"academy-high","containers":[{"name":"pause","image":"registry.k8s.io/pause:3.9","resources":{"requests":{"cpu":"600m"}}}]}}'
   kubectl -n sched-lab describe pod bully | sed -n '/Events/,$p'
   kubectl -n sched-lab get pod bully -o jsonpath='{.status.nominatedNodeName}{"\n"}'
   kubectl -n sched-lab get pods -l app=ballast
   ```

5. Now relax the budget by one and watch the same submission succeed:

   ```sh
   kubectl -n sched-lab patch pdb no-disruption --type=merge -p '{"spec":{"minAvailable":2}}'
   kubectl -n sched-lab get pod bully -o wide -w
   ```

6. Answer the harder question the code raises: is a `PodDisruptionBudget` a **guarantee** here or a preference? Find the answer in the source rather than the documentation — look at what happens when no set of victims satisfies both the budget and the resource requirement.

**Observe** — `ALLOWED DISRUPTIONS` before and after, the preemptor's event and nomination field in the forbidden case, and the ballast pods' ages throughout.

**Expect** — with the budget at zero, no eviction, no nomination, and a `FailedScheduling` event whose wording is about preemption not helping rather than about resources. That message is a third distinct sentence to add to your collection from [exercise 6](06-three-rejections-three-plugins.md), and it is the one that most often gets misdiagnosed as a capacity problem: **the cluster is full, preemption is enabled, priority is high, and nothing happens.**

Expect the ballast pods' ages to be unchanged, which is the check that the budget was respected rather than the preemption merely being slow.

Expect step 5 to succeed within a second of the patch — the budget changing is a cluster event, and the preemptor is sitting in the queue waiting for exactly that class of news.

Expect the answer to step 6 to be more nuanced than "guarantee". Write down what the scheduler does when respecting the budget makes preemption impossible, and separately what the *eviction API* does with the same budget, because those are two different enforcement points and only one of them is in this phase.

**Write down** — the three answers from step 1 with `file:line` (the `selectVictimsOnNode` citation is what [the capstone](37-the-capstone-narrative.md) asks you to narrate from), the sentence from step 2, the refusal message verbatim, and your answer to step 6.

**Footprint note** — one PDB and one extra pod on an already-full `pair`. Nothing new runs; the interesting case is the one where nothing happens at all. 7.5GB total.

**Teardown** — `kubectl -n sched-lab delete pdb no-disruption`, `kubectl -n sched-lab delete pod bully --ignore-not-found`. Keep the ballast and the PriorityClasses. **The topology stays.**
