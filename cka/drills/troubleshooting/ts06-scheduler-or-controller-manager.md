<a id="ts06"></a>
# TS6 — Scheduler or controller-manager: name which from the symptom alone

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Troubleshooting / Troubleshoot cluster components

> **With either of these down, `kubectl` keeps working perfectly and the cluster simply stops doing things.** No errors, no events, no complaints — objects are accepted and nothing acts on them. The diagnosis is by *absence*, and the two components fail in distinguishable ways. Learn to name which before opening a manifest; it is a two-second test and it is the whole drill.

**Break it** — *pass 1 only.* **F05** covers the family; here you choose the component deliberately.

Move `kube-scheduler.yaml` out of `/etc/kubernetes/manifests` — **to a directory outside it**, or the kubelet will keep running it. Later, do the same for `kube-controller-manager.yaml`.

**Work it** — the discriminating test first:

- **Scheduler down**: create a pod. It is accepted, stays `Pending` **with no events at all** — not `FailedScheduling`, *nothing*, because nothing is even looking. An existing pod keeps running. Contrast that silence with **W1**'s `Insufficient cpu`: an unschedulable pod *complains*; an unscheduled pod is silent. That is the tell.
- **Controller-manager down**: create a Deployment. The Deployment object exists and **no ReplicaSet appears**. Delete a pod belonging to an existing ReplicaSet and it is not replaced. Also: a new namespace will not finish terminating, and a ServiceAccount gets no token. Anything that is a controller loop stops; anything that is an API write still works.
- **The one-line test**: `kubectl create deployment x --image=nginx` then `kubectl get rs`. No ReplicaSet → controller-manager. ReplicaSet with `Pending` pods and no events → scheduler. Have that in your fingers.
- **Then confirm from the node**: `crictl ps` for the missing container, and `kubectl -n kube-system get pods` — which *does* still list static pods, because the kubelet keeps mirroring them to the API. A mirror pod disappearing from that list is itself a signal.
- **Fix** by putting the manifest back, and watch the backlog drain: every `Pending` pod schedules at once, every missing ReplicaSet appears. That burst is satisfying and is also confirmation.
- Note the leader election both components run, and that on a single control plane it is a formality — but their logs mention it constantly, so it is worth recognising as noise rather than as a fault.

**Observe**

```sh
kubectl -n kube-system get pods | grep -E 'scheduler|controller-manager'
kubectl create deployment probe --image=nginx && kubectl get rs
kubectl describe pod <pending> | sed -n '/Events/,$p'     # silence
sudo crictl ps | grep -E 'scheduler|controller'
sudo ls /etc/kubernetes/manifests/
```

**Done when** — you name the component from one `kubectl` command, before looking at any manifest, both times.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Break each in turn, name each from the symptom. | 10 min |
| **2** | Live workload present, so some things still work. Name it anyway. | 8 min |
| **3** | **Injected.** **F05**, component unknown. | **5 min** |

**Teardown** — `cka-inject.sh revert`, confirm four manifests present, all four components `Running`, and delete the probe Deployment.

**See also** — **TS5** is the same family with `kubectl` itself dead; **W1** is the complaining `Pending` this must be told apart from.
