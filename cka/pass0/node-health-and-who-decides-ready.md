<a id="node-health"></a>
# Pass 0 — node health: who decides a node is `Ready`

**Pass 0** · **untimed** · [`pair`](../../strands/lab-topologies.md#pair) · Troubleshooting · prerequisite for **TS01**, **TS02**, **TS04**

> **Worked live on 5 Oct**, from the [diagnostic](../plan.md#diagnostic)'s tasks T1 and T3, which landed together and interfered. Written in the shape [pass 0](../learning-pass.md#shape) specifies.
>
> **Done when** you can say who *writes* a node's `Ready` condition, and why a node with a dead kubelet reported `Ready` for six minutes.

---

<a id="fixture"></a>
## 1. The fixture

Two faults, planted independently in the same run, which is how the interesting part happened:

- **On `pair-w1`:** `systemctl stop kubelet`. The node's agent is gone. Nothing on that node is being managed any more.
- **On `pair-cp`:** `kube-controller-manager` crash-looping on a rejected flag — see [static pods](static-pods-and-the-control-plane.md).

The expected symptom of the first is `pair-w1  NotReady`. **It did not appear.** `k get nodes` reported both nodes `Ready` for as long as the second fault was in place, and flipped within about a minute of the controller-manager coming back:

```
NAME      STATUS     ROLES           AGE   VERSION
pair-cp   Ready      control-plane   32d   v1.37.0
pair-w1   NotReady   <none>          32d   v1.37.0
```

Understanding why is the whole document.

---

<a id="kubelet"></a>
## 2. The kubelet is not a pod

Everything else you work with is a pod. The kubelet is not.

```sh
systemctl status kubelet
sudo journalctl -u kubelet -n 50 --no-pager
```

It is an **ordinary systemd service running on the host**, and that is structural rather than incidental: the kubelet is the thing that *runs* pods. It cannot be one. It reads its configuration from local disk (`/var/lib/kubelet/config.yaml`) and its credentials from `/etc/kubernetes/kubelet.conf`, and it needs no cluster to start.

Three consequences:

- **It is invisible to `kubectl`.** There is no pod to describe, no logs to fetch. You find out about the kubelet by going to the node.
- **Its failure is silent from the control plane's point of view** — covered below.
- **Restarting it is `systemctl restart kubelet`**, not anything in `kubectl`. This is the single most common fix for a `NotReady` node and the ladder in [TS01](../drills/troubleshooting/ts01-node-notready-ladder.md) ends there more often than not.

---

<a id="lease"></a>
## 3. How a node says "I'm alive"

Not by being asked. The kubelet **renews a Lease object**, in a namespace that exists for nothing else:

```sh
$ k get lease -n kube-node-lease
NAME      HOLDER    AGE
pair-cp   pair-cp   33d
pair-w1   pair-w1   32d
```

```sh
$ k get lease -n kube-node-lease pair-w1 -o jsonpath='{.spec.leaseDurationSeconds}'
40
```

One lease per node, named after the node, renewed every few seconds. **It is a heartbeat, and it is the only thing a healthy kubelet is obliged to keep doing.** A lease is tiny — a name, a holder, a timestamp — precisely so that thousands of nodes can renew constantly without flooding `etcd`.

Nothing polls the node. Nothing pings it. **If the kubelet stops renewing, the only evidence is a timestamp that stops advancing**, and somebody has to be looking at it for that to mean anything.

---

<a id="conditions"></a>
## 4. The conditions, and who writes them

A node carries a list of conditions, read live from `pair-w1`:

```
NetworkUnavailable   False   FlannelIsUp
MemoryPressure       False   KubeletHasSufficientMemory
DiskPressure         False   KubeletHasNoDiskPressure
PIDPressure          False   KubeletHasSufficientPID
Ready                True    KubeletReady
```

`k get nodes` prints **one** of these — `Ready` — as the `STATUS` column. The other four never appear there, which is why `k describe node` is the real read and `k get nodes` is only the alarm. A node under `DiskPressure` will still show `Ready` until it gets bad enough to matter, while the scheduler has quietly stopped sending it work. See [TS02](../drills/troubleshooting/ts02-disk-and-memory-pressure.md).

**Now the important part.** The four pressure conditions are reported by the kubelet about itself. But `Ready` going **False** is not:

> **The `Ready` condition is written by the *node lifecycle controller*, which runs inside `kube-controller-manager`.**

The sequence:

1. The kubelet renews its lease, every few seconds.
2. The node lifecycle controller — a loop inside `kube-controller-manager` — watches every node's lease.
3. When a lease stops advancing for longer than the grace period, **the controller** writes `Ready: False` onto the node object.

The node does not report that it is down. **A third party notices and records a verdict.** That is the fact everything below follows from.

---

<a id="centre"></a>
## 5. The one that matters — `Ready` is a cached verdict, not a probe

Put steps 1–3 together with the fixture and the mystery dissolves:

- Step 1 had stopped: kubelet dead, lease frozen.
- Steps 2 and 3 had **also** stopped: `kube-controller-manager` was crash-looping, so the loop that writes the verdict was not running.

So the `Ready: True` on `pair-w1` was **a 32-day-old value that had simply stopped being maintained**. Nothing refreshed it, nothing contradicted it, and `k get nodes` rendered it exactly as it renders a healthy one. There is no visual difference between a fresh verdict and a stale one.

The moment `kube-controller-manager` came back, it read the frozen lease, applied the grace period, and wrote `NotReady` — within about a minute of the repair, observed.

**Two rules come out of this, and they generalise well past nodes:**

> **1. `Ready` means "the last controller to look thought so."** It is a stored field on an object, produced by a control loop at some point in the past. The same is true of nearly every `status` block in Kubernetes: you are reading what a controller wrote, not measuring the thing itself. If the controller is down, the field freezes at its last value and still renders beautifully.
>
> **2. Faults mask faults.** Two unrelated problems produced one visible symptom. When a symptom you are confident should be present is *absent*, consider that something upstream has stopped reporting, before concluding you are wrong about the symptom.

**A dead `kube-controller-manager` does not make a cluster look broken. It makes it look frozen** — nothing reconciles, nothing scales, no node ever goes `NotReady`, and every existing object keeps reporting the last thing it was told to say. Stillness reads as health.

---

<a id="consequences"></a>
## 6. What `NotReady` sets in motion

Once the verdict is written, the cluster acts on it automatically:

- The node is **tainted** `node.kubernetes.io/not-ready:NoExecute`, and `node.kubernetes.io/unreachable:NoExecute` if the kubelet is unreachable rather than merely unhealthy.
- Pods carry a default toleration for those taints of **300 seconds**. So for five minutes, nothing happens — **the pods stay `Running`** in `kubectl`, even though nothing on that node is being managed.
- After five minutes, eviction begins and controllers reschedule the replicas elsewhere, if there is anywhere to put them.

**Which explains the other confusing read:** a dead node whose pods still say `Running`. They are not running. The kubelet that would have reported otherwise is gone, so the last status it wrote stands — the same cached-verdict problem one level down. A pod's `status` is written by the kubelet on its node; kill the kubelet and the status freezes with it.

---

<a id="failure"></a>
## 7. What failure looks like

The ladder, and what each rung distinguishes:

```sh
k get nodes                                  # the alarm -- Ready only
k describe node pair-w1                      # all five conditions, plus Events
ssh pair-w1
systemctl status kubelet                     # running? dead? restarting in a loop?
sudo journalctl -u kubelet -n 50 --no-pager  # why
```

| What you see | What it means |
|---|---|
| `NotReady`, kubelet **inactive (dead)** | Stopped and not restarting. `systemctl restart kubelet`, then check it stays up. This was T1. |
| `NotReady`, kubelet **active but flapping** (restart count climbing) | It starts and dies. Its config or certificates are broken — `journalctl` carries the reason. This is the only thing separating it from the case above without reading the journal. |
| `NotReady`, `NetworkUnavailable: True` | The kubelet is fine; the CNI is not. Look at the `kube-flannel` DaemonSet, not the kubelet. |
| `Ready`, but pods are not scheduling there | A **pressure** condition or a **taint**. `k describe node` shows both; `k get nodes` shows neither. |
| Node **absent** from `k get nodes` entirely | It was deleted, or never joined. Different problem — see [TS04](../drills/troubleshooting/ts04-a-node-is-gone.md). |
| Everything `Ready`, and you do not believe it | **Check that `kube-controller-manager` is running.** If it is down, every node's `Ready` is a stale cache and `k get nodes` is telling you nothing at all. |

That last row is the lesson of the whole night, and it is cheap to check:

```sh
k get pods -n kube-system | grep -E 'controller-manager|scheduler|apiserver|etcd'
```

**When the cluster looks fine and something is clearly wrong, confirm that the things which do the looking are alive.**

---

<a id="say"></a>
## 8. Done when

With the terminal closed, you can say:

- why the kubelet cannot be a pod, and where you go to inspect it;
- what a Lease is, which namespace holds them, and what stops when a kubelet dies;
- which component **writes** the `Ready` condition, and why that makes `Ready` a cached verdict;
- why a node with a dead kubelet reported `Ready`, and why its pods still said `Running`;
- what `NotReady` triggers, and why nothing visible happens for five minutes.

**See also** — [TS01](../drills/troubleshooting/ts01-node-notready-ladder.md), the reflex drill for the ladder; [static pods](static-pods-and-the-control-plane.md) for the component that was masking this; and [the API surface](the-api-surface.md) for the other two ways to get a clean empty answer that means nothing.
