<a id="w03"></a>
# W3 — Taints and tolerations, including a `NoExecute` eviction

**Reflex** · **Core** · **10 min** · [`workhorse`](../../../strands/lab-topologies.md#workhorse) · Workloads and Scheduling / Pod admission and scheduling

> **Affinity is the pod choosing a node; a taint is the node refusing pods.** They are independent, and a toleration is permission to ignore a taint, not a request to be placed on it. A pod tolerating `gpu=true:NoSchedule` may still land on any other node — tolerating is not preferring, and that distinction is a reliable exam question.

**Do**

1. **Read the taint that is already there.** The control-plane node carries `node-role.kubernetes.io/control-plane:NoSchedule`, which is why ordinary pods avoid it and why DaemonSet pods do not. Find the toleration on a `kube-system` DaemonSet pod that lets it through.
2. Taint a worker with `NoSchedule`. New pods avoid it; **pods already running stay**. Confirm the running ones stay before moving on.
3. Toleration on a new pod — matching key, value and effect. It can now be scheduled there. Then prove the other half: it may still be put elsewhere. Pair it with a `nodeAffinity` if you actually want it pinned, and note that it takes *both*.
4. **`NoExecute` is the one that evicts.** Apply it and watch pods without a matching toleration leave the node immediately. Then add `tolerationSeconds` to a toleration and watch that pod survive exactly that long. This is the mechanism behind the five-minute delay before pods leave a `NotReady` node — go and read `node.kubernetes.io/not-ready` on any pod's spec; the kubelet adds it for you.
5. The three effects together: `NoSchedule` (new pods only), `PreferNoSchedule` (a soft filter, like preferred affinity), `NoExecute` (new pods and existing ones).
6. **The empty-value and empty-key forms.** `operator: Exists` with no value tolerates any value of a key; `operator: Exists` with no key at all tolerates *everything*, which is what a monitoring DaemonSet does. Write the all-tolerating form once so you recognise it.

**Observe**

```sh
kubectl describe node pair-cp | grep -i taint
kubectl taint node <n> gpu=true:NoSchedule
kubectl taint node <n> gpu=true:NoExecute        # watch pods leave
kubectl get pods -o wide -w
kubectl get pod <p> -o jsonpath='{.spec.tolerations}' | python3 -m json.tool
kubectl taint node <n> gpu-                      # trailing dash removes
```

**Done when** — all three effects behave as you predicted, and you can explain why a tolerating pod is not necessarily placed on the tainted node.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Three effects, `tolerationSeconds`, the existing control-plane taint. | 10 min |
| **2** | Live workload on the node. Taint it `NoExecute` and keep one pod alive deliberately. | 8 min |
| **3** | Cold, no notes. Taint, tolerate, evict. | 5 min |

**Teardown** — **remove every taint you added.** A left-behind `NoExecute` is the single most disruptive piece of litter in these drills; `kubectl describe node | grep -i taint` across all nodes before you stop.

**See also** — **TS3** drains a node, which uses the same machinery from the other end; **W2** is the pod's side of placement.
