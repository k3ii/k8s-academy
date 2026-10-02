<a id="w05"></a>
# W5 — A rolling update, paused mid-roll, then resumed

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Workloads and Scheduling / Rolling updates

> **`kubectl rollout pause` freezes the Deployment controller, not the pods.** A paused Deployment accepts edits and acts on none of them, which is exactly what you want when several changes must land together — and exactly what makes a forgotten pause look like a broken controller. Both halves are worth having felt.

**Do**

1. A Deployment with enough replicas that a roll takes visible time — six or so, with a readiness probe that is not instant, or the whole update finishes before you can watch it.
2. Change the image and **watch** with `kubectl get pods -w` in one pane and `kubectl rollout status` in another. Count how many pods exist beyond the desired replica count; that surplus is `maxSurge`.
3. **Pause mid-roll.** Pods stop changing. The old ReplicaSet and the new one both sit at partial counts. Read `kubectl get rs` and see the split — this is the clearest view of what a Deployment actually is: a controller over two ReplicaSets.
4. **Edit while paused.** Change the image again, and an env var. Nothing happens. Resume, and both land in a **single** roll rather than two. That is the real use of pause.
5. **Then the trap.** Leave it paused and try to scale it. Scaling works — pause blocks *rollouts*, not replica changes. Then apply a change and watch it not take, which is what a paused Deployment looks like to someone who did not pause it. `kubectl rollout status` reports it plainly; `kubectl get deploy` does not.
6. Read `.status.conditions` and find `Progressing` with its reason. Then set `progressDeadlineSeconds` low, roll a bad image, and watch the condition flip to `ProgressDeadlineExceeded` — a failed roll does **not** roll back on its own.

**Observe**

```sh
kubectl rollout status deploy/web
kubectl rollout pause deploy/web
kubectl get rs -o wide                 # two ReplicaSets, split counts
kubectl set image deploy/web web=nginx:1.27 && kubectl set env deploy/web K=v
kubectl rollout resume deploy/web      # one roll, both changes
kubectl get deploy web -o jsonpath='{.status.conditions}' | python3 -m json.tool
```

**Done when** — you can pause, batch two changes, resume into one roll, and recognise a paused Deployment from its symptoms alone.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Roll, pause, batch, resume, read the ReplicaSets. | 10 min |
| **2** | A Deployment someone already paused. Diagnose, then finish the roll. | 8 min |
| **3** | Cold, no notes. Roll an image and report the status without `-w`. | 5 min |

**Teardown** — delete the namespace. A paused Deployment left running is a trap for your future self.

**See also** — **W6** is the undo; **W7** tunes the surge and unavailability numbers you counted here.
