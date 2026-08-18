<a id="6c1-the-node-vanishes"></a>
# 6.C1 — Power off the machine and measure the two timers nobody notices until now

**Claim** — hard node loss and a stopped kubelet look identical to the API server for the first forty seconds and then diverge completely, and the difference is entirely in what happens to the pods: one set comes back, the other set is stuck until something forces it.

**Rests on** — [6.C2](22-6c2-the-kubelet-stops-the-pods-do-not.md), which is the control for this experiment; run them in this order or the comparison is not available. This is [6.C1](../../phases/06-kubelet-node.md#chaos).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. The worker is powered off mid-exercise and brought back.

**Setup** — [Chaos Mesh has no node-failure kind and the fault here is the hypervisor](../../strands/chaos.md#cannot-express). Put a Deployment on the worker as in 6.C2, plus one bare pod with no controller, so you can watch a replacement happen and not happen side by side:

```sh
kubectl create ns c1
kubectl -n c1 create deployment web --image=registry.k8s.io/e2e-test-images/agnhost:2.47 --replicas=2 -- /agnhost netexec --http-port=8080
kubectl -n c1 patch deployment web -p '{"spec":{"template":{"spec":{"nodeSelector":{"kubernetes.io/hostname":"pair-worker"}}}}}'
kubectl -n c1 run orphan --image=registry.k8s.io/pause:3.10 --overrides='{"spec":{"nodeName":"pair-worker"}}'
kubectl -n c1 get pods -o wide
```

**Do**

1. Start a clock and pull the power. From `hopper`:

   ```sh
   ssh hopper
   qm list | grep -i worker      # the vmid is the node's last octet
   date +%T; qm stop <worker-vmid>
   ```

2. Mark five moments with timestamps:

   ```sh
   kubectl get nodes -w -o custom-columns=NAME:.metadata.name,READY:'.status.conditions[?(@.type=="Ready")].status'
   kubectl get node pair-worker -o jsonpath='{range .spec.taints[*]}{.key}:{.effect}{"\n"}{end}'
   kubectl -n c1 get pods -o wide -w
   kubectl -n c1 get pod orphan -o jsonpath='{.metadata.deletionTimestamp}{"\t"}{.status.phase}{"\n"}'
   ```

   The five: node `Ready=Unknown`; the `not-ready` taint; the `unreachable` taint; the deployment's pods gaining a `deletionTimestamp`; a replacement pod appearing on the control plane (or not, and why).

3. Bring the machine back and time the other direction:

   ```sh
   date +%T; qm start <worker-vmid>
   ```

**Observe** — what happens to the pods that were marked for deletion while the node was gone, at the moment the node returns. And separately: whether the *replacement* pods were ever created, or whether the Deployment sat at reduced replicas throughout.

**Expect** — the first forty seconds to be **indistinguishable from 6.C2**: the same `Unknown`, the same reason, the same taints, at the same times. The lease stops being renewed for the same reason in both cases and the control plane cannot tell a dead machine from a dead process. That equivalence is the drill's first finding and it is worth stating plainly, because half of production node debugging is people assuming the cluster has more information than it does.

Then expect the divergence: pods on an unreachable node get a `deletionTimestamp` from the taint-based eviction after the toleration expires — a timer measured in **minutes**, not seconds — and then sit in `Terminating` indefinitely, because the only component that can confirm a container is gone is the one on the powered-off machine. The Deployment creates replacements without waiting for that confirmation; the bare `orphan` pod has nobody to replace it and is simply gone.

Expect the return to be fast and undramatic: the kubelet starts, finds the pods marked for deletion, confirms them, and they disappear. **The stuck deletions unstick themselves** — which is why forcing them is so often the wrong reflex.

**Write down** — the two timelines side by side, 6.C2 against 6.C1, with the divergence point marked and the timer named for each interval. Add the answer [the chaos table asks for](../../phases/06-kubelet-node.md#chaos): the detection latency, explained from the lease mechanism rather than measured and left unexplained.

**Footprint note** — `qm stop` frees 2048MB for the duration, which is the wrong direction to be useful; the phase's ceiling was never the constraint here. What matters is that the control plane guest keeps the API server, so the whole drill is observable from `kubectl` on a cluster that is half dead — which is exactly the position you would be in at work.

**Teardown**

```sh
kubectl delete ns c1
kubectl get nodes
```

Confirm the worker is back `Ready` and that Chaos Mesh's daemon rejoined: `kubectl -n chaos-mesh get pods -o wide`. **The topology stays.**
