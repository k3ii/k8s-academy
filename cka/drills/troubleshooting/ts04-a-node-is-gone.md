<a id="ts04"></a>
# TS4 — A node is simply gone: the taint, the timers, and what became of its pods

**Reflex** · **Core** · **10 min** · [`workhorse`](../../../strands/lab-topologies.md#workhorse) · Troubleshooting / Troubleshoot clusters and nodes

> **Nothing happens for five minutes, and then everything happens at once.** A vanished node is marked `NotReady` after its heartbeats stop, tainted `NoExecute`, and its pods are evicted only after each pod's `tolerationSeconds` — 300 by default — expires. Knowing that number stops you debugging a cluster that is behaving exactly as designed.

**Break it** — *pass 1 only.* This is **F03**, the one fault that needs Proxmox rather than ssh, because the point is a node that cannot be asked anything.

Power the node off at the hypervisor. Not a shutdown — a power-off, so nothing drains and nothing says goodbye.

**Work it**

- **Watch the clock from the start.** Note the time the node died. `node-monitor-grace-period` (40s by default) is how long before `Ready` goes `Unknown` — note `Unknown`, not `False`; that distinction *is* the signature of a node that stopped talking rather than one reporting trouble.
- **Find the taint that appears.** `node.kubernetes.io/unreachable:NoExecute`. Then look at a pod on *any* node and find the matching toleration with `tolerationSeconds: 300` that the admission controller added for you. That is the five minutes, written down in a place most people never look. (**W3** is the mechanism.)
- **Classify the pods, because they do not all behave the same.** Deployment-managed pods are recreated elsewhere once eviction fires. **StatefulSet** pods are **not** — the controller cannot know whether the old one is really dead, and will not risk two pods with the same identity. They sit `Terminating` indefinitely. That asymmetry is the most valuable thing in this drill.
- **The `Terminating` pods never finish**, because nothing on the dead node can confirm the deletion. Know the force-delete (`--force --grace-period=0`) and know that it is a **statement you are making**, not a fix: you are asserting the pod is gone. On a StatefulSet with attached storage that assertion is how split-brain happens.
- **Bring it back.** Power on, watch it rejoin: heartbeats resume, taint removed, and pods are *not* automatically rebalanced back — the scheduler does not relocate running pods. The cluster stays lopsided until something restarts.

**Observe**

```sh
kubectl get nodes -w
kubectl get pods -A -o wide | grep <node>
kubectl describe node <n> | grep -i -A3 taint
kubectl get pod <p> -o jsonpath='{.spec.tolerations}' | python3 -m json.tool
kubectl get events -A --sort-by=.lastTimestamp | tail -20
```

**Done when** — you can state, for a node that died ninety seconds ago, exactly what will happen and when, and you can say why the StatefulSet pod is still `Terminating`.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. A Deployment and a StatefulSet on the node. Watch both. | 10 min |
| **2** | A pod with a custom `tolerationSeconds`. Predict its eviction time. | 8 min |
| **3** | **Injected.** **F03**, cause unknown — and the node cannot be asked. | **5 min** |

**Teardown** — `cka-inject.sh revert` and power the node back on. Confirm every node is `Ready`, no `unreachable` taint survives, and no pod is left `Terminating`.

**See also** — **TS1** is the node that is sick rather than absent; **W3** is the taint-and-toleration machinery this runs on; **TS3** is doing it deliberately and politely.
