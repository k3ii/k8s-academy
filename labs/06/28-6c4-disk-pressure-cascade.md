<a id="6c4-disk-pressure-cascade"></a>
# 6.C4 — Fill the disk and watch the kubelet try three things before it evicts anyone

**Claim** — disk-pressure eviction is not memory eviction with a different signal. The kubelet has reclaim actions available for disk that it has none of for memory, it takes them first, and only when they are exhausted does it start ranking pods — so the cascade has a preamble that the memory path does not.

**Rests on** — [the ranking](11-synchronize-and-the-ranking.md) for the comparators, [the slope](27-an-eviction-as-a-slope.md) for the dashboard, and [exercise 10's fourth question](10-the-signals-before-the-code.md), which asked what disk reclaim has that memory reclaim does not. This is [6.C4](../../phases/06-kubelet-node.md#chaos), and it is deliberately the last drill because **it is only legible on a time series**.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, stack up. The worker's 20G disk is the subject.

**Setup**

1. Find out whether this node even has two disk signals, before designing an experiment around them:

   ```sh
   kubectl get --raw "/api/v1/nodes/pair-worker/proxy/stats/summary" \
     | jq '{nodefs: .node.fs, imagefs: .node.runtime.imageFs}'
   ssh zain@10.10.10.131 'df -h /var/lib/kubelet /var/lib/containerd /'
   ```

2. Add two panels to the dashboard: `node_filesystem_avail_bytes` for the worker's root filesystem, and `kubelet_evictions_total` if the kubelet exposes it on this version — check the `kubelet` scrape job for eviction series with `curl -s localhost:9090/api/v1/label/__name__/values | jq -r '.[]' | grep evict`.

3. Give the kubelet something to garbage-collect first, so the preamble has material to work with:

   ```sh
   for i in busybox:1.35 busybox:1.34 alpine:3.20 alpine:3.19 nginx:1.27 nginx:1.26; do
     ssh zain@10.10.10.131 "sudo crictl pull $i"
   done
   ssh zain@10.10.10.131 'sudo crictl images | wc -l'
   ```

**Do** — two pods that use ephemeral storage at different rates, so the ranking has a decision to make:

```sh
kubectl create ns disk
kubectl -n disk apply -f - <<'EOF2'
apiVersion: v1
kind: Pod
metadata: {name: greedy}
spec:
  nodeName: pair-worker
  containers:
  - name: c
    image: busybox:1.36
    command: ["sh","-c","i=0; while true; do dd if=/dev/zero of=/data/$i bs=1M count=512 2>/dev/null; i=$((i+1)); sleep 10; done"]
    volumeMounts: [{name: d, mountPath: /data}]
  volumes: [{name: d, emptyDir: {}}]
---
apiVersion: v1
kind: Pod
metadata: {name: modest}
spec:
  nodeName: pair-worker
  containers:
  - name: c
    image: busybox:1.36
    command: ["sh","-c","dd if=/dev/zero of=/data/one bs=1M count=256 2>/dev/null; sleep infinity"]
    volumeMounts: [{name: d, mountPath: /data}]
    resources: {requests: {ephemeral-storage: 1Gi}}
  volumes: [{name: d, emptyDir: {}}]
EOF2
```

Watch four things: `df` on the node, the node's `DiskPressure` condition, `crictl images | wc -l`, and the two pods.

```sh
kubectl get node pair-worker -w -o custom-columns=NAME:.metadata.name,DISK:'.status.conditions[?(@.type=="DiskPressure")].status'
ssh zain@10.10.10.131 'sudo journalctl -u kubelet -f | grep -i -e "image garbage" -e "disk" -e eviction'
```

**Expect** — the preamble first: as the threshold approaches, the kubelet deletes **dead containers and then unused images** before it touches a single running pod. `crictl images | wc -l` drops. That is the answer to exercise 10's fourth question arriving as an observation, and it is the reason a node under disk pressure can recover with no workload impact at all — an outcome the memory path can never produce, because there is no such thing as an unused megabyte of RAM the kubelet may reclaim on your behalf.

Then, when the images are gone and the disk keeps filling: `DiskPressure=True`, and `greedy` evicted rather than `modest` — not because it is greedier in absolute terms, but because it has **no ephemeral-storage request** and therefore exceeds its request by everything it has written. Check that reasoning against the comparator sequence you wrote down; if `modest` had gone first you would need a different explanation, and the point of giving it a request is that it makes the two candidate explanations disagree.

Expect `DiskPressure` to also stop new pods being scheduled there — the taint appears, as it did for [6.C2](22-6c2-the-kubelet-stops-the-pods-do-not.md) — and expect it to clear slowly, on the same transition period.

Expect `nodefs` and `imagefs` to be **the same filesystem on this node**, if step 1 says so. Then say what that means rather than pretending otherwise: the two thresholds are watching one device, whichever is stricter effectively governs, and the separate `imagefs` signal only earns its keep on a node where the image store has its own disk. **Do not add a disk to chase the distinction** — the cascade is fully observable as it is, and the honest note is worth more than the second device.

**Write down** — the timeline against the graph: image GC starting, images deleted, threshold crossed, taint, victim, recovery. Name the reclaim actions in order, name the comparator that chose the victim, and state whether this node has one disk signal or two. [The chaos table's 6.C4 row](../../phases/06-kubelet-node.md#chaos) asks for the ranking and the threshold that fired.

**Footprint note — this is the one drill that can damage the guest rather than just stress it, and the containment is the threshold itself.** The kubelet's `nodefs.available` hard default fires with a couple of gigabytes still free on a 20G disk, so `greedy` is stopped well before the filesystem is full. If it is not — if `df` reaches 100% and containerd starts failing — you have found something worth writing down, and the recovery is `kubectl delete ns disk` followed by `ssh zain@10.10.10.131 'sudo systemctl restart kubelet containerd'`. RAM is unchanged at 6.5GB; this drill costs disk, which is the *other* half of [the one-topology-at-a-time rule](../../strands/lab-topologies.md#ceiling) and the only exercise in the phase that tests it.

**Teardown**

```sh
kubectl delete ns disk
ssh zain@10.10.10.131 'df -h /; sudo crictl images | wc -l'
kubectl get node pair-worker -o jsonpath='{range .status.conditions[*]}{.type}={.status}{"\n"}{end}'
```

All conditions `False` except `Ready`, and the disk back where it started. **The topology stays** for [the capstone](29-the-capstone-trace.md).
