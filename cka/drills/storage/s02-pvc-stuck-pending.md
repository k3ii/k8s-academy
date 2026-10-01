<a id="s02"></a>
# S2 — A PVC stuck `Pending`: no class, no capacity, wrong access mode

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Storage / Manage PVs and PVCs

> **`Pending` has one display and four causes, and `describe pvc` names the cause every time.** The skill is not diagnosis, it is the reflex of reading the event instead of guessing. Create each cause deliberately so the four event texts are familiar before one of them arrives as a fault.

> **Read this before scoring yourself.** On this cluster `local-path` binds `WaitForFirstConsumer` **and is not marked as the default class**. So a PVC is `Pending` both when something is wrong *and* when everything is right but no pod has claimed it yet, and a PVC with no `storageClassName` gets no class at all rather than the obvious one. Both are normal here and neither is normal everywhere — know which you are looking at.

**Do**

Produce each cause, read each event, then fix it:

1. **Waiting for a consumer.** The benign one. `WaitForFirstConsumer` with no pod. Event: `waiting for first consumer to be created`. Fix: create a pod.
2. **No class.** A PVC with `storageClassName` omitted on a cluster with no default. It stays `Pending` with no provisioner ever looking at it — and the event is *quiet*, which is the giveaway. Confirm with `kubectl get sc` that nothing carries the default annotation. Fix: name the class, or make one default (**S5**).
3. **A class that does not exist.** A typo'd `storageClassName`. Different event text from the previous case, and worth seeing side by side, because they present almost identically in `get pvc`.
4. **No matching PV, for a static claim.** Create a PV by hand, then a PVC asking for **more capacity** than it offers, and one asking for an **access mode** it does not have. Both stay `Pending`. Matching is on capacity, access mode, class **and** selector — all four, and all four must pass.
5. **`storageClassName: ""`** explicitly: that means "no dynamic provisioning, static PVs only", which is different from omitting the field. Write it and prove the difference, because it is the idiomatic way to force a static bind.
6. For each, say the command that would have told you in one step. That command is `kubectl describe pvc`, every time.

**Observe**

```sh
kubectl get pvc
kubectl describe pvc <name> | sed -n '/Events/,$p'
kubectl get sc -o custom-columns=NAME:.metadata.name,DEFAULT:.metadata.annotations.storageclass\\.kubernetes\\.io/is-default-class
kubectl get pv -o custom-columns=NAME:.metadata.name,CAP:.spec.capacity.storage,MODES:.spec.accessModes,CLASS:.spec.storageClassName,STATUS:.status.phase
```

**Done when** — you have produced all five `Pending` states deliberately and can name the cause from the event text alone.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Build all five, fix all five. | 10 min |
| **2** | Someone else's `Pending` PVC with no context. Diagnose cold. | 8 min |
| **3** | No notes, clock visible. One `Pending` PVC, cause named in under a minute. | 5 min |

**Teardown** — delete the namespace **and** any hand-made PVs; a `Released` PV outlives its namespace.

**See also** — **S5** is the default-class half of this; **S1** is the happy path.
