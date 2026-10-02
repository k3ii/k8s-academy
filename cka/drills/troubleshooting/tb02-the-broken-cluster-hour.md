<a id="tb02"></a>
# TB2 — The broken-cluster hour: five faults, one hour, and something you deliberately do not fix

**Build** · **Pinned** · **60 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Troubleshooting / Triage across all five

> **The only object in the plan that drills triage as a distinct skill.** Five faults planted at once, one in each Troubleshooting sub-competency. Every individual fault here is something you have already drilled. What you have never drilled is choosing the order — and the exam is won and lost on that choice far more often than on any single repair.

> **Not a simulator sitting.** The simulator is the full paper across all five domains. This is 30% of it at four times the density, and [the plan](../../plan.md#simulators) deliberately keeps the two non-adjacent so that a bad hour here does not contaminate a scored sitting two days later.

**Do**

1. **Read all five before touching anything.** Ten minutes of pure reconnaissance, no edits. This feels like waste and is the highest-value part of the hour: faults interact, and the second one you find often explains the first.
2. **Bank the cheap ones.** Rank by cost-to-fix, not by severity. A thirty-second fix taken early is thirty seconds; taken last, after you have burned forty minutes on something hard, it is often not taken at all.
3. **Flag and skip the expensive one, out loud, on paper.** Write down what it is, what you think it needs, and why you are not doing it now. This is the skill. Most people do not skip anything and run out of clock with four tasks half-done, which scores worse than three done and one untouched.
4. **Watch for the fault that is not a fault.** A cluster with five live faults produces secondary symptoms that look like a sixth. Chasing one costs you a repair you could have banked.
5. **At the end, report.** What you fixed, what you deliberately did not, and what it would have taken. A triage exercise with no report has not been done.

**Observe**

```sh
kubectl get nodes
kubectl get pods -A --field-selector=status.phase!=Running
kubectl get events -A --sort-by=.lastTimestamp | tail -40
kubectl -n kube-system get pods
./scripts/cka-inject.sh status
```

Those five commands, in that order, are the ten-minute reconnaissance. Learn them as a block.

**Done when** — you have a written triage list made **before** the first edit, you fixed things in cost order rather than discovery order, and you can name the one you skipped and justify it.

**Done in one sitting.** It is an hour by construction. Overrunning is itself the result the drill is measuring, and should be recorded rather than absorbed.

**Teardown** — `cka-inject.sh revert`, then verify from the cluster that it is clean, not just from the state file. **Five faults is where the state file and reality are most likely to disagree.**

**See also** — **TB1** is the harness. Every TS object is one of the five you will meet here.
