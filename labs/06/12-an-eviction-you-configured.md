<a id="an-eviction-you-configured"></a>
# Set the threshold yourself, cross it on purpose, read the decision back

**Claim** — every step `synchronize()` takes is visible in the kubelet's log and in the pod's status, in the order you read it from the source — and the eviction you get is the one *you* configured, down to which pod goes and how much it reclaims before it stops.

**Rests on** — [the comparator sequence](11-synchronize-and-the-ranking.md). You are scoring that pseudocode against a real decision, so have it open.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Only the worker `.131` is reconfigured; the control plane keeps its defaults so the contrast stays available.

**Setup — reconfigure the worker's kubelet**

```sh
ssh zain@10.10.10.131 'sudo cp /var/lib/kubelet/config.yaml /var/lib/kubelet/config.yaml.orig'
ssh zain@10.10.10.131 'sudo tee -a /var/lib/kubelet/config.yaml >/dev/null <<EOF2
evictionHard:
  memory.available: "700Mi"
  nodefs.available: "10%"
  imagefs.available: "15%"
  nodefs.inodesFree: "5%"
evictionPressureTransitionPeriod: "30s"
evictionMinimumReclaim:
  memory.available: "100Mi"
EOF2
sudo systemctl restart kubelet'
kubectl get node pair-worker -o jsonpath='{.status.conditions[?(@.type=="MemoryPressure")]}{"\n"}' | jq
```

`700Mi` on a 2048MB node is aggressive on purpose: it leaves a few hundred MB of headroom above the system daemons, so the manager fires while the node is still healthy and long before the kernel has an opinion. Confirm the kubelet took the whole block, rather than assuming it:

```sh
kubectl get --raw "/api/v1/nodes/pair-worker/proxy/configz" | jq '.kubeletconfig | {evictionHard, evictionMinimumReclaim, evictionPressureTransitionPeriod}'
```

**Do**

1. Start a slow allocator with no limits — BestEffort by construction, and it allocates through a memory-backed `emptyDir` so the growth is in 32MB steps you can watch:

   ```sh
   kubectl create ns evict
   kubectl -n evict apply -f - <<'EOF2'
   apiVersion: v1
   kind: Pod
   metadata: {name: slow-hog}
   spec:
     nodeName: pair-worker
     containers:
     - name: c
       image: busybox:1.36
       command: ["sh","-c","i=0; while true; do dd if=/dev/zero of=/fill/$i bs=1M count=32 2>/dev/null; i=$((i+1)); sleep 5; done"]
       volumeMounts: [{name: fill, mountPath: /fill}]
     volumes:
     - name: fill
       emptyDir: {medium: Memory}
   EOF2
   ```

2. Watch three things at once. In one shell:

   ```sh
   kubectl get node pair-worker -w -o custom-columns=NAME:.metadata.name,MEM:'.status.conditions[?(@.type=="MemoryPressure")].status'
   ```

   In a second, on the worker: `sudo journalctl -u kubelet -f | grep -i -e eviction -e threshold -e 'attempting to reclaim'`.

   In a third: `kubectl -n evict get pods -w`.

3. When it fires, collect the evidence:

   ```sh
   kubectl -n evict get pod slow-hog -o jsonpath='{.status.phase}{"\t"}{.status.reason}{"\t"}{.status.message}{"\n"}'
   kubectl -n evict get events --sort-by=.lastTimestamp | tail -10
   kubectl get node pair-worker -o jsonpath='{range .status.conditions[*]}{.type}={.status} {.reason}{"\n"}{end}'
   ```

**Observe** — the kubelet log lines, in sequence, against your pseudocode from [exercise 11](11-synchronize-and-the-ranking.md): the observed signal value, the threshold it was compared against, the statement that it is attempting to reclaim, the ranking, and the single pod name. Match each line to the step in `synchronize()` that emitted it and note the `file:line`.

**Expect** — `MemoryPressure=True` on the node before the pod dies, and the pod ending as `Failed` with `status.reason: Evicted` and a message naming the signal and the threshold. **The pod object stays** — it is not deleted, which is what makes eviction forensically different from every other way a pod ends; a controller-owned pod would already have a replacement while this corpse sits there holding its own explanation.

Expect exactly **one** pod evicted per pass, and `MemoryPressure` to stay `True` for at least `evictionPressureTransitionPeriod` after the memory came back — the flap damper you configured, and the reason a node can report pressure it no longer has.

Expect the reclaim to overshoot the threshold by roughly your `evictionMinimumReclaim`. That is the answer to [exercise 10's](10-the-signals-before-the-code.md) second question, arriving as a number.

**Write down** — [the module's write-down](../../phases/06-kubelet-node.md#m6-3): the signal, the configured threshold, the observed value at the crossing, the victim and the comparator that chose it, each with a citation into `eviction_manager.go` or `defaults_linux.go`.

**Footprint note** — the hog is capped by the node, not by you: `emptyDir: {medium: Memory}` with no `sizeLimit` grows until the kubelet stops it, which on a 2048MB worker is the whole point and is contained to that guest. **This is the exercise where the cramped lab is the instrument.** On a 32GB node you would wait a very long time for the same lesson, or never see it. `pair` at 5.0GB plus `forge` at 1536MB is unchanged at 6.5GB against [the ceiling](../../strands/lab-topologies.md#ceiling).

**Teardown** — delete the namespace, but **leave the kubelet configuration in place**: [exercises 13](13-faster-than-housekeeping.md) and [14](14-evicted-or-oomkilled.md) both drive this same threshold, and [exercise 20](20-the-node-refuses-what-the-scheduler-allowed.md) restores it.

```sh
kubectl delete ns evict
```

**The topology stays.**
