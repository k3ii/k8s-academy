<a id="object-chain"></a>
# Pass 0 — Deployment, ReplicaSet, Pod: what is actually connected to what

**Pass 0** · **untimed** · [`pair`](../../strands/lab-topologies.md#pair) · Workloads and Scheduling · prerequisite for **W5**, **W6**

> **Worked live on 2 Oct**, in the format [pass 0](../learning-pass.md#shape) specifies. Everything below was observed on `pair` rather than recalled, and one claim in it was checked **because** it was a recollection — see [§5](#released).
>
> **Done when** you can explain, terminal closed, why `kubectl delete pod` on a crash-looping pod is worse than doing nothing.

---

<a id="fixture"></a>
## 1. The fixture

```sh
k create ns basics
k config set-context --current --namespace=basics
k create deployment web --image=nginx --replicas=2
k get deploy,rs,pods
```

Nothing is rigged. The lesson is in the ordinary case.

---

<a id="chain"></a>
## 2. You asked for one object and got three layers

```
Deployment  web                      ← what you asked for: "2 of these, this version"
   └─ ReplicaSet  web-5fc9f4bf66     ← one per version. Its job: keep the count at 2.
        ├─ Pod  web-5fc9f4bf66-mvshc ← a running instance
        └─ Pod  web-5fc9f4bf66-vhlhw
```

**A Deployment does not manage Pods. It manages ReplicaSets.** Change the pod template and the Deployment creates a **new** ReplicaSet, then shifts the replica count from the old one to the new one. The old ReplicaSet is kept, at zero replicas.

That is what a rollback *is*: the previous ReplicaSet is still present, so rolling back means scaling it from 0 back to 2. Nothing is rebuilt, re-pulled or reconstructed. **W6** is this fact with a command attached.

`5fc9f4bf66` is **a hash of the pod template**, not a random string. Same template, same hash. It appears in the ReplicaSet's name and in every pod's name, so a pod's parentage reads straight off its name: `<replicaset>-<5 random chars>`.

---

<a id="columns"></a>
## 3. Reading the three outputs

**Deployment — `READY 1/2 · UP-TO-DATE 2 · AVAILABLE 1`**

| Column | Means |
|---|---|
| `READY` | how many pods are **ready to take traffic** — not how many exist |
| `UP-TO-DATE` | how many run the template you last asked for |
| `AVAILABLE` | how many have been ready long enough to count |

**ReplicaSet — `DESIRED 2 · CURRENT 2 · READY 1`**

The ReplicaSet's whole job in three numbers. **DESIRED** is what it was told; **CURRENT** is how many exist; its only purpose is to make them equal. **READY is not its concern** — that belongs to the containers. A ReplicaSet can be perfectly satisfied while nothing works.

**Pod — `0/1`, `2/2`**

Containers **ready** / containers **total**, in that pod. [TS12](../drills/troubleshooting/ts12-the-whole-logs-flag-surface.md)'s fixture reads `2/2` with three containers defined, because `seed` is an **init container**: init containers run, finish and exit. They are never ready, they are done.

---

<a id="selector"></a>
## 4. Nothing is connected — there is only a query

The ReplicaSet holds **no list of its pods**. It holds a label selector and continuously asks the API how many pods match it. Fewer than DESIRED, it creates one; more, it deletes one.

```sh
k get pods --show-labels
k describe rs web-5fc9f4bf66 | head -8
```

```
Selector:  app=web,pod-template-hash=5fc9f4bf66
```

Note the selector carries **the template hash as well as the app label**. That is how two ReplicaSets belonging to the same Deployment run side by side during a rolling update without stealing each other's pods — which is **W5**.

**Delete a pod and watch:**

```sh
k delete pod web-5fc9f4bf66-lzmq8
k get pods
# web-5fc9f4bf66-vhlhw   1/1   Running   0   3s
```

Nothing was repaired. `lzmq8` is gone permanently and a **different pod** was created, because the count no longer matched. Same hash, new random suffix, `RESTARTS 0`, `AGE 3s`.

| | What survives | `RESTARTS` |
|---|---|---|
| **A container crashes** | the **Pod** survives; a new container is placed in it | **increments** |
| **A pod is deleted** | nothing; a **new Pod** appears | **resets to 0** — different pod |

<a id="delete-pod"></a>
### Why this makes `kubectl delete pod` the wrong move

On a crash-looping pod it is worse than doing nothing, for two independent reasons:

1. The ReplicaSet builds the replacement **from the same template**, so the fault returns unchanged.
2. The dead container's output belonged to the **old pod**, which no longer exists — so `kubectl logs --previous` now has nothing to read. You destroyed the evidence and kept the bug.

---

<a id="released"></a>
## 5. What failure looks like — a label drifts

Labels are load-bearing; **names are cosmetic**. Nothing in Kubernetes matches on a name.

```sh
k label pod web-5fc9f4bf66-mvshc app=orphan --overwrite
k get pods --show-labels
```

Three pods. `mvshc` still *named* `web-5fc9f4bf66-mvshc`, so it still looks like part of the Deployment — and is managed by nothing. A replacement was created to restore the count.

**`k get deploy` reports `2/2`. Healthy.** The Deployment has its two matching pods and is satisfied. Nothing anywhere reports a fault. The orphan keeps consuming CPU and memory, survives a scale-to-zero, and is replaced by nobody when it dies. The only signal is that `k get pods` shows three while `k get deploy` shows two.

<a id="ownerref"></a>
### The claim that was checked rather than recalled

Pods carry `ownerReferences`, shown by `describe` as `Controlled By:`. The recollection was that the controller *releases* a pod that stops matching. **Measured:**

```sh
k describe pod web-5fc9f4bf66-mvshc | grep -i -A1 'controlled by'   # (empty)
k describe pod web-5fc9f4bf66-n2pvc | grep -i -A1 'controlled by'
# Controlled By:  ReplicaSet/web-5fc9f4bf66
```

Confirmed. Ownership runs **both** ways: a pod that starts matching is **adopted** and has the reference written; a pod that stops matching is **released** and has it removed. Membership is recomputed from labels continuously — there is no list, at any point, anywhere.

<a id="rescue"></a>
### Rescuing it, and what that proves

```sh
k label pod web-5fc9f4bf66-mvshc app=web --overwrite
```

Adopted immediately; the ReplicaSet then found **three** matches against a DESIRED of 2 and deleted one. **Observed: the newest pod was deleted** — `n2pvc` at 4m34s went, while the 15-minute-old rescued pod stayed. Consistent with a scale-down ordering of unready before ready and newer before older, but that is **one observation and not a proof**; treat it as a plausible rule, not a fact, until it is seen several more times.

The pod set ended as `mvshc + vhlhw`, having started as `lzmq8 + mvshc`:

> The cluster reached the state that was **described** without restoring the state that **was**. Nothing attempted to. Individual pods are interchangeable and disposable; the declared shape is the only thing that persists.

---

<a id="teardown"></a>
## 6. Teardown

```sh
k delete ns basics
```

<a id="next"></a>
## 7. What was deliberately not done

Rolling out a second version and rolling it back — watching the second ReplicaSet appear and the count shift between them. That is **W5** and **W6**, and it is [diagnostic](../plan.md#diagnostic) task W1 almost exactly. Teaching the structure is foundations; rehearsing the task before it is measured is marking your own homework.
