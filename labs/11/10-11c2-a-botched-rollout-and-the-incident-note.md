<a id="11c2-a-botched-rollout-and-the-incident-note"></a>
# 11.C2 — a rollout you break on purpose, recognised from the controller's behaviour, and the one-page incident note it produces

**Artifact** — a one-page incident write-up in [the P1/P6/P8 escalated format](../../phases/01-operate-shallow.md): symptom, the objects you inspected *in order*, the mechanism cited to source, the fix — produced from a rollout you wedge with your own YAML (a bad image, an impossible readiness probe, or a request no node can satisfy), recognised from the Deployment/ReplicaSet controller's behaviour, and rolled back with `kubectl rollout undo`. This is the rehearsal [the upgrade capstone](11-the-upgrade-that-drops-nothing.md) assembles: a botched rollout is the failure mode most likely to bite *during* the upgrade window, so you meet it here first, in isolation.

**Rests on** — [P1's incident note](../../phases/01-operate-shallow.md), the format this escalates; and [P4's controller reading](../../phases/04-controllers.md), which is where the ReplicaSet/Deployment reconcile behaviour you diagnose from was read.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), the last exercise on it before the switch. A wedged rollout needs a Deployment, not a third node.

**Read** — [the drill's chaos-table row](../../phases/11-synthesis.md#chaos) and [manual-drills #5](../../strands/chaos.md#manual-drills). By hand — the fault is your own YAML, and the skill is recognising the wedge from `kubectl rollout status` and the controller's events rather than from an injected signal.

**Do** — deploy something healthy, then push a revision that cannot become ready, and diagnose the stall before undoing it:

```sh
kubectl create deployment app --image=nginx --replicas=3
kubectl rollout status deployment/app          # healthy baseline
# wedge it: an image tag that does not exist (or an impossible readiness probe)
kubectl set image deployment/app nginx=nginx:this-tag-does-not-exist
kubectl rollout status deployment/app --timeout=60s   # hangs; the new ReplicaSet cannot progress
kubectl get rs -l app=app -o wide              # old RS still serving, new RS stuck
kubectl describe deployment app | sed -n '/Conditions/,$p'
kubectl rollout undo deployment/app            # back to the last good revision
```

**Observe** — the old ReplicaSet keeps serving while the new one cannot reach its ready count, so the Service never loses endpoints — the rollout is wedged, not down. The controller's *behaviour* (a paused progression, `ProgressDeadlineExceeded`, an unavailable new RS) is what names the fault, not a log line you injected.

**Expect** — a stalled rollout with the application still up, and a clean `rollout undo`. If the app went *down*, your PDB or replica math is the second finding — write it in the note.

**Write down** — the one-page incident note: symptom, objects inspected in order (deployment → rollout status → replicaset → events), the mechanism (why the new RS could not progress and why traffic stayed up), and the fix. A note another person could follow to reproduce your diagnosis — [the P1 standard](../../phases/01-operate-shallow.md).

**Teardown** — delete the Deployment and Service; **the topology stays** for one more exercise's worth of continuity, then [the upgrade capstone](11-the-upgrade-that-drops-nothing.md) tears `pair` down and brings up `workhorse`:

```sh
kubectl delete deployment app --ignore-not-found
```
