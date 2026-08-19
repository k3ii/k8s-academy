<a id="the-upgrade-that-drops-nothing"></a>
# Capstone 2a — a minor-version upgrade with 0 5xx across the whole window, proven by the load generator's own log

**Artifact** — the load generator's log showing **0 dropped requests / 0 5xx** across a real minor-version upgrade of `workhorse`, drained one node at a time so the other two keep serving — a re-readable file, the "file:line" of an operation that has no source line. Not "it looked fine": the log is the artifact, and you can name which node was draining at each moment it stayed clean.

**Rests on** — [the joined trace](07-the-joined-trace-terminal-to-container.md) (you have cited what each node runs and why draining one keeps the other two serving) and [the botched-rollout rehearsal](10-11c2-a-botched-rollout-and-the-incident-note.md) (the failure mode you are about to run past). This is the first of the two operations [the phase's second capstone](../../phases/11-synthesis.md#capstone) asks for.

**Topology** — [`workhorse`](../../strands/lab-topologies.md#workhorse), and here is the switch the phase is built around: [`pair`](../../strands/lab-topologies.md#pair) goes, `workhorse` comes up. Three nodes because a zero-downtime upgrade means draining one while the other two keep serving — [two nodes cannot demonstrate that honestly](../../phases/11-synthesis.md). Its two workers have [1 core each](../../strands/lab-topologies.md#workhorse) by design, so contention during the drain is real.

**Setup** — destroy `pair`, provision `workhorse`, and stand up the workload and its load generator:

```sh
just tofu labs destroy                                  # release pair
just tofu labs apply -var 'topology=workhorse'          # .140 CP, .141/.142 workers
just gate 140 && just gate 141 && just gate 142 && just play
kubectl create deployment web --image=nginx --replicas=6   # spread across both workers
kubectl expose deployment web --port=80
kubectl create poddisruptionbudget web-pdb --selector=app=web --min-available=4
```

**Do** — start a load generator that logs every non-200, then upgrade one minor version, draining a node at a time and watching `kubectl drain` fight the PDB:

```sh
# a load generator that records return codes to a re-readable log:
kubectl run load --image=fortio/fortio --restart=Never -- \
  load -c 8 -qps 200 -t 900s -json /dev/stdout http://web
# then, on the control plane, the standard kubeadm path — note where k0s differs:
#   kubeadm upgrade plan; kubeadm upgrade apply vX.Y.Z
#   kubectl drain 10.10.10.141 --ignore-daemonsets --delete-emptydir-data
#   (upgrade kubelet/kubectl on the node) ; kubectl uncordon 10.10.10.141
#   repeat for .142
```

Drain one node at a time; the PDB (`min-available=4` of 6) forces the drain to wait rather than evict below the floor, which is exactly the fight [manual-drills #4/#7](../../strands/chaos.md#manual-drills) names.

**Verify from outside** — the load generator's JSON log has zero entries in the 5xx bucket across the entire window, and you can state which node was cordoned at each timestamp. A clean run you cannot attribute to a drain sequence is luck, not proof; the artifact is the log *and* the node-by-node narration.

**Expect** — the drain to *block* on the PDB until pods reschedule onto the other worker, then proceed — that pause is the system keeping your SLO, not a stall. Expect 0 5xx if the PDB and replica count leave a serving majority at every step; a single 5xx means a node drained below the floor, and that is the finding, not a rounding error.

**Write down** — the load-generator log (kept as a file), the drain order with timestamps, and one line on where k0s's upgrade path differs from kubeadm's. This is [the gate's upgrade condition](../../phases/11-synthesis.md#gate).

**Footprint note** — [`workhorse` at 7.0GB](../../strands/lab-topologies.md#workhorse) against [the 9.5GB ceiling](../../strands/lab-topologies.md#ceiling), 2.5GB of margin — comfortable, because unlike [P5's split](../../strands/build-mechanics.md#p5-split) no build guest sits alongside it; this phase compiles nothing.

**Teardown** — delete nothing yet: [the scale capstone](12-scale-under-load-narrated-by-component.md) runs on this same upgraded `workhorse`, and the load generator can keep running into it. **The topology stays** until the scale run ends it.
