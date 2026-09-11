<a id="qos-memory-resources"></a>

# Fifteen releases in alpha, beta on the newest release the pin carries, a throttling formula replaced by a different one, a default factor documented twice with two different answers, and the `memory.min` this post is built around is now set only by a field the post never names

**Post** — [Quality-of-Service for Memory
Resources](https://kubernetes.io/blog/2021/11/26/qos-memory-resources/), 2021-11-26, by Tim Xu
(Tencent Cloud) — 118 lines, 8,366 bytes, plus five SVG images that carry the arithmetic. An alpha
feature in v1.22 that makes the kubelet write a Pod's memory requests and limits into the cgroup v2
memory controller, so that memory requests stop being a scheduling hint and start being a
kernel-enforced reservation.

**As written**

The complaint comes first. `:12` says that in prior releases `Kubernetes did not support memory
quality guarantees`, and `:30-34` explains why. `spec.containers[].resources.requests` `is designed
for scheduling`; `spec.containers[].resources.limits` `is passed to the container runtime when the
kubelet starts a container`. CPU is `compressible` — hit the limit and you are throttled, not
killed. Memory is not: `:34` says that in cgroup v1 `the container runtime never took into account
and effectively ignored spec.containers[].resources.requests["memory"]`, and that `memory actually
can't be compressed in cgroup v1. Because there is no way to throttle memory usage, if a container
goes past its memory limit it will be terminated by the kernel with an OOM (Out of Memory) kill.` So
a memory request bought you a place on a node and nothing after that.

`:36` names the fix: cgroup v2, whose memory controller can do both reservation and throttling, and
with it `quality-of-service for pods and containers extends to cover not just CPU time but memory as
well`. That sentence links the QoS *task* page, which matters later.

`## How does it work?` (`:38-90`) is the mechanism, and it is two files. `:39` states the mapping:
`Memory requests and limits of containers in pod are used to set specific interfaces memory.min and
memory.high provided by the memory controller. When memory.min is set to memory requests, memory
resources are reserved and never reclaimed by the kernel; this is how Memory QoS ensures the
availability of memory for Kubernetes pods.` A two-row table at `:45-66` defines both files from the
kernel's own documentation, and the italic lines under each are the Kubernetes half: under
`memory.min`, `We map it to the container's memory request` (`:55`); under `memory.high`, `We use a
formula to calculate memory.high, depending on container's memory limit or node allocatable memory
(if container's memory limit is empty) and a throttling factor. Please refer to the KEP for more
details on the formula.` (`:63`).

The formula the post does give in prose is at `:85`: `A throttling factor is introduced as a
multiplier (default is 0.8). If the result of multiplying memory limits by the factor is greater
than memory requests, kubelet will set memory.high to the value and use Unified via CRI. And if the
container does not specify memory limits, kubelet will use node allocatable memory instead.` Limit
times factor, with the request as a floor.

`:68` and `:73-83` are the plumbing. The kubelet passes `memory.min` to the CRI runtime `via the
Unified field in CRI during container creation`; because `the memory.min interface requires that the
ancestor cgroup directories are all set, the pod and node cgroup directories need to be set
correctly`; and `Kubelet will manage the cgroup hierarchy of the pod level and node level cgroups
directly using runc libcontainer library, while container cgroup limits are managed by the container
runtime.` Four of the post's five images are the summations that follow from that — container, pod
and node level `memory.min`, and container level `memory.high` — which means the post's arithmetic
is not text. It is in SVG files, so no search of the blog archive will ever find it.

`## How do I use it?` (`:92-102`) is four prerequisites: Kubernetes since v1.22; runc since
v1.0.0-rc93, containerd since 1.4, cri-o since 1.20; `Linux kernel minimum version: 4.15,
recommended version: 5.2+`; and a cgroup v2 image. `:100` adds a status report with a shelf life —
the containerd PR `has been merged and will be released in containerd 1.6`, while the CRI-O one `is
still in WIP` — and `:102` ends the operator's half by pointing at the kubelet config file. `:107`
names KEP-2570.

**As it runs now** — the feature shipped, four years late, and almost none of the detail survived
the wait.

**The gate finally moved, on the newest release the pin carries.** `MemoryQoS` ran alpha from v1.22
to v1.36 and beta, defaulting to `true`, from v1.37. Fifteen releases on the first rung. The gate's
own body text at the pin is worth reading beside the post, because it describes a feature with two
switches where the post had one: the kubelet sets `memory.high` `when memoryThrottlingFactor is
set`, and sets `memory.min` and `memory.low` `for tiered memory protection when
memoryReservationPolicy is set to TieredReservation`, and the whole thing `requires both - feature
gate enablement and kubelet configuration setting`. Turning the gate on, which v1.37 does for you,
changes nothing by itself.

**The throttling formula is not the post's formula.** `concepts/workloads/pods/pod-qos.md:119-121`
gives it as a single line:

```
memory.high = requests + memoryThrottlingFactor * (limits - requests)
```

That is an interpolation between the request and the limit. The post's is a multiplication of the
limit alone, floored at the request. They agree only when the request is zero. `:123-124` works an
example — factor `0.9`, a `256 MiB` request and a `1 GiB` limit give `memory.high` `set to roughly
947 MiB` — and the post's rule on the same inputs gives 921.6 MiB. Twenty-five and a half mebibytes
apart, on numbers the documentation chose. A reader who took the arithmetic from the blog post and
went looking for it in a cgroup file would not find it.

**The default factor is documented twice at the pin, with two different answers.**
`pod-qos.md:110-113` says `memoryThrottlingFactor` `Its default value is nil, which means that the
kubelet does not set memory.high. To enable memory throttling, set memoryThrottlingFactor to a value
greater than 0 and less than or equal to 1.` The generated config reference for the same field,
`reference/config-api/kubelet-config.v1beta1.md:1714-1723`, ends `Default: 0.9`. One of those pages
says the feature is off until you configure it and the other says it has a value out of the box.
They cannot both be right, and the kubelet's own effective configuration is the arbiter, which is
why this exercise asks it before it asks anything else. The post's `0.8` is neither answer.

**`memory.min` is no longer part of the default behaviour at all.** The post's central claim is that
memory requests become `memory.min`. At the pin that happens only when the kubelet is given
`memoryReservationPolicy: TieredReservation`, a field the post never mentions, whose default is
`None` — under which, per `pod-qos.md:138-139`, `the kubelet does not set memory.min or memory.low
for containers and pods. No memory is hard-locked by the kernel.` Three of the post's five images
are `memory.min` summations for a configuration nobody gets by default.

**And when it is switched on, it is not the mapping the post describes.** `pod-qos.md:140-146`
splits by QoS class: Guaranteed Pods get `memory.min` set to memory requests, `Burstable` Pods get
`memory.low` set to memory requests — `the kernel preferentially retains this memory but may reclaim
it under extreme pressure` — and `BestEffort` Pods get nothing. `memory.low` is a third cgroup file
the post never names, and the tiering it implements is a v1.36 addition. The post said `memory.min`
is the container's memory request, full stop, for every container.

**The ancestor rule was promoted into documentation almost unchanged.** The post's `:73` said the
`memory.min` interface requires the ancestor directories to be set. `pod-qos.md:162-167` now says
`Because cgroup v2 memory protection is hierarchical, the kubelet also configures the ancestor
cgroups. It sets memory.min on the kubepods root cgroup to the sum of the memory requests for
Guaranteed and Burstable Pods. It sets memory.low on the kubepods root cgroup and the Burstable QoS
cgroup to the sum of the memory requests for Burstable Pods. Without this ancestor coverage, the
per-Pod and per-container protection would be ineffective.` The post's three summation images are
the only part of its arithmetic that survived, and they survived as prose.

**The selling point acquired a warning.** `pod-qos.md:169-176` is a caution: for a Guaranteed Pod
requests equal limits, so with `TieredReservation` `memory.min therefore equals memory.max`, and
`For a workload that uses a large page cache, the kernel might be unable to reclaim enough page
cache before the cgroup reaches memory.max, which can result in an OOM kill. Size the memory limit
to include sufficient headroom for page cache.` The post sold `never reclaimed by the kernel` as the
guarantee. The documentation now sells the same sentence as the hazard, on exactly the QoS class the
post's own example Pod at `:14-29` belongs to.

**The kernel floor moved, for a reason the post could not have known.** The post asked for 4.15
minimum and 5.2+ recommended. `concepts/architecture/cgroups.md:52-61` now requires kernel 5.8 or
later for cgroup v2 at all, and `pod-qos.md:193-199` recommends 5.9 or higher specifically `because
memory.high throttling on older kernels can trigger a known livelock bug`, with a link to the kernel
mailing list thread. The mechanism the post recommends had a livelock in it on the kernels the post
recommends, and the kubelet now logs a warning at startup if you enable the gate on one.

**The rollback path is documented, and it is not symmetric.** `pod-qos.md:178-191` says that on
restart the kubelet resets `memory.min` and `memory.low` on the kubepods root cgroup and
`memory.low` on the Burstable QoS cgroup to zero, but that `Pod-level and container-level memory.min
and memory.low values can remain, but they are ineffective because the corresponding ancestor
protection is zero`; and that `memory.high` returns to `max` only when the runtime next applies a
resource configuration, so `An already running container that is not restarted or resized can retain
its previous memory.high value`. Turning the feature off leaves numbers behind in the cgroup tree.
That is a claim with a file you can `cat`, which is what step 9 does.

**The CRI half left no trace.** The field itself is never named at the pin:
`LinuxContainerResources` appears zero times under `content/en/docs`, and the two occurrences of
`Unified` in the tree — `concepts/architecture/cgroups.md:36` on memory accounting and
`concepts/scheduling-eviction/podgroup-scheduling.md:165` on scheduler snapshots — are ordinary
English with no connection to CRI. The runtime-spec field, the CRI change, the containerd PR and the
CRI-O PR that was `still in WIP` are all outside what kubernetes.io documents, and nothing at the
pin records how that WIP ended. What did survive is one sentence in
`concepts/configuration/manage-resources-containers.md:276-278`, hedged to the point of being a
different claim: on a cgroups v2 node `the container runtime might use the memory request as a hint
to set memory.min and memory.low`.

**The feature landed on a different page than the post pointed at.** `:36` links
`tasks/configure-pod-container/quality-service-pod.md`. That page is 302 lines long at the pin and
mentions Memory QoS, `MemoryQoS` and `memory.high` a combined zero times. All of it went to the
concept page, `concepts/workloads/pods/pod-qos.md:96-199`, as a section appended after the three QoS
class definitions.

**Two things at the pin exist that the post has no room for.**
`reference/instrumentation/metrics.md:2576-2577` and `:2583-2584` define
`kubelet_memory_qos_node_memory_low_bytes` and `kubelet_memory_qos_node_memory_min_bytes` — `Total
cgroup v2 memory.low in bytes for Burstable pods` and `Total cgroup v2 memory.min in bytes for
Guaranteed pods` — both `ALPHA`, both kubelet-only, and both instrumenting the tiered policy rather
than the throttling the post was about. And
`reference/node/kubelet-config-directory-merging.md:99-155` uses `MemoryQoS` as its worked example
of how `featureGates` maps merge across configuration files: `:113` sets it `true` in the main file,
`:128` sets it `false` in a drop-in, and `:145` shows the drop-in winning. The gate this post
announced is now best known, on that page, as the value being turned off.

**The diff, and why** — the feature arrived; the post's description of it did not.

**Broke: the arithmetic.** Both numbers a reader would carry away — the `0.8` default and `limit ×
factor` — are wrong at the pin, and they are wrong independently, so correcting one does not rescue
the other. This is the most concrete kind of drift in the archive: not a flag that no longer parses,
but a formula that still parses and produces a different answer. The only place the post warns you
is `:63`, which sends you to the KEP for the formula. That sentence turned out to be the most
durable line in the post.

**Overtaken by a redesign.** The two-switch shape at the pin — `memoryThrottlingFactor` for
throttling, `memoryReservationPolicy` for reservation, both off by default, the gate gating only
whether either can be used — is not a refinement of the post's design. In the post, reservation and
throttling are one feature with one switch, and `memory.min` follows automatically from every
container's memory request. At the pin they are separable, and the reservation half is tiered by QoS
class across two kernel files instead of one. Fifteen releases in alpha is the visible cost of that
rework, and it is not a gate that sat forgotten: it is a gate that was rebuilt underneath its own
name while the announcement stayed up.

**Retired by being agreed with.** The ancestor-cgroup requirement and the `memory.min` summations
are now the project's own prose, and the mapping from the memory controller's files to Kubernetes
concepts — which the post had to invent a table for — is a standing section of the QoS concept page.
The post's structural insight was right; only its numbers aged.

**Turned into a caution.** `never reclaimed by the kernel` is the same fact in the post and in the
pin, and its sign is reversed. This is a pattern worth naming, because it is not the documentation
disagreeing with the post: it is four years of people running the thing. An announcement gets to say
what a mechanism is for. Documentation has to say what it does to you.

**Never absorbed: the runtime plumbing.** The `Unified` paragraph and the two PR status lines are
the most perishable kind of content a release announcement carries, and they perished completely. No
page at the pin mentions the field; no page records whether CRI-O finished. This is not a boundary
of ownership like a specification in another repository — it is a status report, true on the day,
and nothing inherits a status report.

**The ladder**

One gate, transcribed from its `stages:` list parsed as YAML.

```
MemoryQoS  alpha false 1.22 - 1.36
           beta  true  1.37 -
```

Fifteen releases alpha, then beta and on by default on v1.37, which is the newest release the pin
carries. `locked` does not appear and there is no `removed: true`. Two things are worth measuring
rather than assuming about that fifteen. First, across the pin's feature-gate directory, 401 gates
have an alpha stage and **eight** of them sat alpha for longer than `MemoryQoS` did — `QOSReserved`
(27 releases, alpha since v1.11 and still alpha), `CustomCPUCFSQuotaPeriod` (26, still alpha),
`HPAScaleToZero` (21), `WinDSR` (19), `ProcMountType` (19), `StorageVersionAPI` (18, still alpha),
`CSIVolumeHealth` (17, still alpha) and `LocalStorageCapacityIsolationFSQuotaMonitoring` (16). Four
of the eight eventually graduated. So fifteen is the longest first rung this census walks, not the
longest in the tree; the honest claim is that it is the longest belonging to a feature that a blog
post announced and this archive then had to wait out. Second, v1.37 is where several of these were
cleared at once: nineteen gates begin a beta stage at v1.37, `HPAScaleToZero` and
`KubeletInUserNamespace` among them. `MemoryQoS` was not promoted alone.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`, 4096MB, 4
CPUs, 25G, brought up with [the five provision steps](../../strands/lab-topologies.md#provision).
One node is enough and a second would be noise: every value this exercise reads is a file in the
node's own cgroup tree, written by that node's kubelet. The 4096MB matters twice — node allocatable
is the stand-in for a missing memory limit, so it appears in the `BestEffort` arithmetic, and the
three workload Pods together ask for well under a quarter of it, so nothing here is under memory
pressure while you measure. The node must be on cgroup v2; [the swap
exercise](05-run-nodes-with-swap-alpha.md) establishes that it is, and the same guest serves both.

**Do**

1. Establish the four things this post's prerequisites are about, before touching anything. The last
   command asks the kubelet itself whether it knows the gate and at what stage:

   ```sh
   NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}'); echo "$NODE"
   kubectl version -o json | python3 -c 'import sys,json; print("server:", json.load(sys.stdin)["serverVersion"]["gitVersion"])'
   stat -fc %T /sys/fs/cgroup
   uname -r
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/metrics" | grep 'kubernetes_feature_enabled{name="MemoryQoS"'
   ```

2. Settle the contradiction between the two pages that document the same field. `configz` returns
   the kubelet's effective configuration, so whatever it prints is the answer:

   ```sh
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" \
     | python3 -c 'import sys,json; c=json.load(sys.stdin)["kubeletconfig"];
   print("memoryThrottlingFactor:", c.get("memoryThrottlingFactor"));
   print("memoryReservationPolicy:", c.get("memoryReservationPolicy"));
   print("featureGates:", c.get("featureGates"));
   print("cgroupDriver:", c.get("cgroupDriver"))'
   ```

3. Create one Pod per QoS class and read the four cgroup files for each, before any configuration
   change. The `mq` function stays defined for the rest of the exercise:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: {name: mq-guaranteed, labels: {app: mq}}
   spec:
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh","-c","sleep 3600"]
         resources:
           requests: {memory: "256Mi", cpu: "100m"}
           limits: {memory: "256Mi", cpu: "100m"}
   ---
   apiVersion: v1
   kind: Pod
   metadata: {name: mq-burstable, labels: {app: mq}}
   spec:
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh","-c","sleep 3600"]
         resources:
           requests: {memory: "256Mi"}
           limits: {memory: "1Gi"}
   ---
   apiVersion: v1
   kind: Pod
   metadata: {name: mq-besteffort, labels: {app: mq}}
   spec:
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh","-c","sleep 3600"]
   EOF
   kubectl wait --for=condition=Ready pod -l app=mq --timeout=120s
   kubectl get pod -l app=mq -o custom-columns=NAME:.metadata.name,QOS:.status.qosClass

   mq() {
     U=$(kubectl get pod "$1" -o jsonpath='{.metadata.uid}' | tr '-' '_')
     P=$(sudo find /sys/fs/cgroup -type d -name "*${U}*" | head -1)
     [ -n "$P" ] || { echo "$1: no cgroup found"; return; }
     for D in "$P" $(sudo find "$P" -mindepth 1 -type d); do
       echo "== ${D#/sys/fs/cgroup/}"
       for k in memory.max memory.high memory.min memory.low; do
         printf '   %-12s %s\n' "$k" "$(sudo cat "$D/$k" 2>/dev/null || echo ABSENT)"
       done
     done
   }
   for x in mq-guaranteed mq-burstable mq-besteffort; do echo "### $x"; mq $x; done
   ```

4. Turn on throttling the way the pin documents it — the gate and the factor together, in a kubelet
   configuration drop-in. [The PID limiting exercise](../2019/05-pid-limiting.md) owns this
   mechanism, including what to do when `--config-dir` is not set:

   ```sh
   sudo grep -o -- '--config-dir=[^ ]*' /var/lib/kubelet/kubeadm-flags.env || echo "--config-dir is NOT set"
   sudo mkdir -p /etc/kubernetes/kubelet.conf.d
   printf 'apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nfeatureGates:\n  MemoryQoS: true\nmemoryThrottlingFactor: 0.9\n' \
     | sudo tee /etc/kubernetes/kubelet.conf.d/20-memory-qos.conf
   sudo systemctl restart kubelet; sleep 20; systemctl is-active kubelet
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" \
     | python3 -c 'import sys,json; c=json.load(sys.stdin)["kubeletconfig"]; print(c.get("memoryThrottlingFactor"), c.get("featureGates"))'
   kubectl delete pod -l app=mq --wait; kubectl apply -f /dev/stdin <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: {name: mq-burstable, labels: {app: mq}}
   spec:
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh","-c","sleep 3600"]
         resources:
           requests: {memory: "256Mi"}
           limits: {memory: "1Gi"}
   EOF
   kubectl wait --for=condition=Ready pod/mq-burstable --timeout=120s
   mq mq-burstable
   ```

5. Do both arithmetics against the number the kernel actually holds. The first is the pin's, the
   second is the post's `:85`:

   ```sh
   python3 - <<'EOF'
   req, lim, factor = 256*1024*1024, 1024*1024*1024, 0.9
   print("pin  (pod-qos.md:120):  %d bytes  %.1f MiB" % (req + factor*(lim-req), (req + factor*(lim-req))/1048576))
   print("post (index.md:85):     %d bytes  %.1f MiB" % (factor*lim, (factor*lim)/1048576))
   print("difference:             %.1f MiB" % ((req + factor*(lim-req) - factor*lim)/1048576))
   EOF
   ```

6. Bring back the other two Pods and read the two cases the post's prose does not cover: a
   `Guaranteed` container, whose request equals its limit, and a `BestEffort` container, which has
   neither. Node allocatable is the second half of the `BestEffort` answer:

   ```sh
   kubectl get node "$NODE" -o jsonpath='{.status.allocatable.memory}{"\n"}'
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: {name: mq-guaranteed, labels: {app: mq}}
   spec:
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh","-c","sleep 3600"]
         resources:
           requests: {memory: "256Mi", cpu: "100m"}
           limits: {memory: "256Mi", cpu: "100m"}
   ---
   apiVersion: v1
   kind: Pod
   metadata: {name: mq-besteffort, labels: {app: mq}}
   spec:
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh","-c","sleep 3600"]
   EOF
   kubectl wait --for=condition=Ready pod -l app=mq --timeout=120s
   for x in mq-guaranteed mq-besteffort; do echo "### $x"; mq $x; done
   ```

7. Now the half the post thought was the whole feature. Add the reservation policy, restart, and
   read the same files again — this time watching which of `memory.min` and `memory.low` each QoS
   class gets:

   ```sh
   printf 'apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nmemoryReservationPolicy: TieredReservation\n' \
     | sudo tee /etc/kubernetes/kubelet.conf.d/21-memory-reservation.conf
   sudo systemctl restart kubelet; sleep 20; systemctl is-active kubelet
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" \
     | python3 -c 'import sys,json; print(json.load(sys.stdin)["kubeletconfig"].get("memoryReservationPolicy"))'
   kubectl delete pod -l app=mq --wait
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: {name: mq-guaranteed, labels: {app: mq}}
   spec:
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh","-c","sleep 3600"]
         resources:
           requests: {memory: "256Mi", cpu: "100m"}
           limits: {memory: "256Mi", cpu: "100m"}
   ---
   apiVersion: v1
   kind: Pod
   metadata: {name: mq-burstable, labels: {app: mq}}
   spec:
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh","-c","sleep 3600"]
         resources:
           requests: {memory: "256Mi"}
           limits: {memory: "1Gi"}
   ---
   apiVersion: v1
   kind: Pod
   metadata: {name: mq-besteffort, labels: {app: mq}}
   spec:
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh","-c","sleep 3600"]
   EOF
   kubectl wait --for=condition=Ready pod -l app=mq --timeout=120s
   for x in mq-guaranteed mq-burstable mq-besteffort; do echo "### $x"; mq $x; done
   ```

8. Read the ancestors the post said had to be set, and the two metrics that count them. The kubepods
   root and the Burstable QoS slice carry sums, not per-Pod values:

   ```sh
   for D in kubepods.slice kubepods.slice/kubepods-burstable.slice kubepods.slice/kubepods-besteffort.slice; do
     echo "== $D"
     for k in memory.min memory.low memory.max memory.high; do
       printf '   %-12s %s\n' "$k" "$(sudo cat /sys/fs/cgroup/$D/$k 2>/dev/null || echo ABSENT)"
     done
   done
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/metrics" | grep '^kubelet_memory_qos'
   kubectl get pods -A -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,QOS:.status.qosClass --no-headers | sort -k3
   ```

9. Test the rollback claims at `pod-qos.md:178-191` one at a time: the ancestors reset, the per-Pod
   values linger, and a container that is neither restarted nor resized keeps its `memory.high`:

   ```sh
   sudo rm -f /etc/kubernetes/kubelet.conf.d/21-memory-reservation.conf
   printf 'apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nfeatureGates:\n  MemoryQoS: false\n' \
     | sudo tee /etc/kubernetes/kubelet.conf.d/20-memory-qos.conf
   sudo systemctl restart kubelet; sleep 25; systemctl is-active kubelet
   for k in memory.min memory.low; do
     printf 'kubepods.slice %-12s %s\n' "$k" "$(sudo cat /sys/fs/cgroup/kubepods.slice/$k)"
     printf 'burstable      %-12s %s\n' "$k" "$(sudo cat /sys/fs/cgroup/kubepods.slice/kubepods-burstable.slice/$k)"
   done
   for x in mq-guaranteed mq-burstable; do echo "### $x (not restarted, not resized)"; mq $x; done
   kubectl delete pod mq-burstable --wait
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: {name: mq-burstable, labels: {app: mq}}
   spec:
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh","-c","sleep 3600"]
         resources:
           requests: {memory: "256Mi"}
           limits: {memory: "1Gi"}
   EOF
   kubectl wait --for=condition=Ready pod/mq-burstable --timeout=120s
   echo "### mq-burstable (recreated)"; mq mq-burstable
   ```

10. Offline, count what the post left in the tree and what it did not:

    ```sh
    cd /path/to/kubernetes/website
    grep -rn 'Unified' content/en/docs --include='*.md'
    grep -rc 'LinuxContainerResources' content/en/docs --include='*.md' | grep -v ':0$' || echo "LinuxContainerResources: 0 files"
    grep -rn --include='*.md' 'memoryThrottlingFactor' content/en/docs | grep -i 'default'
    grep -c 'MemoryQoS\|memory\.high\|Memory QoS' content/en/docs/tasks/configure-pod-container/quality-service-pod.md
    sed -n '99,155p' content/en/docs/reference/node/kubelet-config-directory-merging.md
    sed -n '52,61p' content/en/docs/concepts/architecture/cgroups.md
    python3 - <<'EOF'
    import glob, os, re
    G = "content/en/docs/reference/command-line-tools-reference/feature-gates"
    PIN, rows = 37, []
    for p in sorted(glob.glob(G + "/*.md")):
        if os.path.basename(p) == "index.md": continue
        stages, cur = [], None
        for line in open(p).read().split("---", 2)[1].split("\n"):
            m = re.match(r'\s*- stage: "?(\w+)"?', line)
            if m: cur = {"stage": m.group(1)}; stages.append(cur); continue
            m = re.match(r'\s+(fromVersion|toVersion): "?1\.(\d+)"?', line)
            if m and cur: cur[m.group(1)] = int(m.group(2))
        al = [x for x in stages if x["stage"] == "alpha" and "fromVersion" in x]
        if not al: continue
        span = max(x.get("toVersion", PIN) for x in al) - min(x["fromVersion"] for x in al) + 1
        rows.append((span, os.path.basename(p)[:-3], any(x["stage"] != "alpha" for x in stages)))
    rows.sort(key=lambda r: (-r[0], r[1]))
    mine = [r for r in rows if r[1] == "MemoryQoS"][0]
    longer = [r for r in rows if r[0] > mine[0]]
    print("gates with an alpha stage:", len(rows))
    print("MemoryQoS:", mine[0], "releases; longer:", len(longer),
          "of which graduated:", sum(1 for r in longer if r[2]))
    for r in longer: print("%3d  %-46s graduated=%s" % r)
    print("tied at %d:" % mine[0], [r[1] for r in rows if r[0] == mine[0]])
    EOF
    ```

**Expect**

Step 1 prints your server version, `cgroup2fs`, a kernel release, and one
`kubernetes_feature_enabled` series for `MemoryQoS`. The stage label is the interesting part and it
depends on what you installed: on v1.37 the gate is `BETA` and enabled without you asking, on
anything older it is `ALPHA` and disabled. Check the kernel against both numbers the pin gives —
`cgroups.md:57` requires 5.8 for cgroup v2 and `pod-qos.md:195-197` recommends 5.9 for `memory.high`
throttling — and note which side of the post's `4.15 minimum, 5.2+ recommended` you are on. Any
current distribution image clears all of them; the point is that the post's floor would not have.

Step 2 is the arbiter. Expect `memoryThrottlingFactor: None` and `memoryReservationPolicy: None` on
a default kubeadm node, which makes `pod-qos.md:111` right and `kubelet-config.v1beta1.md:1723`'s
`Default: 0.9` wrong — the value is a pointer that is nil until set, and the generated reference is
describing the constant the kubelet would use if the field were populated. Record whichever you get,
with your version; this is the exercise's one live documentation defect and it is cheap to re-check.

Step 3 shows three Pods, one per QoS class, and the `QOS` column confirms the classification the
manifests were built for. In the cgroup dump, `memory.max` is `268435456` for the Guaranteed
container, `1073741824` for the Burstable one and `max` for the BestEffort one — the limit, working
exactly as it did before this feature existed. Every `memory.high` is `max`, and every `memory.min`
and `memory.low` is `0`. That is the post's `:34` complaint, still true on a cgroup v2 node in 2026:
the memory request is in the API, the scheduler used it, and the kernel has not been told.

Step 4 restarts the kubelet with the gate and the factor, and `configz` echoes `0.9` back. The
Burstable container's `memory.high` should now be about `993210368` — roughly `947 MiB`, the
documentation's own worked example at `:123-124`. If `--config-dir` is not set on your node, the
drop-in is ignored and `configz` still says `None`; append the same two keys to
`/var/lib/kubelet/config.yaml` instead, with a backup first, the way [the swap
exercise](05-run-nodes-with-swap-alpha.md) does.

Step 5 prints the two candidate answers: `993211187` bytes (947.2 MiB) from the pin's formula and
`966367641` bytes (921.6 MiB) from the post's. Compare both with the number step 4 read out of the
kernel. The kernel's value will be rounded down to a page boundary, so match on the mebibyte, not
the byte. The pin's formula wins, and the post's is off by 25.6 MiB — about 2.5% of the limit, which
is small enough to look like rounding and large enough to be the difference between a container that
throttles when you expect and one that does not.

Step 6 gives the two cases the post's prose skips. The Guaranteed container has no `memory.high` —
it stays `max` — because `pod-qos.md:130-131` says requests equal limits leaves nothing to
interpolate. The BestEffort container gets a `memory.high` computed from a request of zero and node
allocatable in place of the limit, so on a 4096MB guest with allocatable around `3.7Gi` expect
roughly `3.3Gi`. Notice what that means: the Pod that asked for nothing is the one that got a
throttling threshold, and the Pod that asked for exactly what it needs got none.

Step 7 is the tiering. With `memoryReservationPolicy: TieredReservation` the Guaranteed Pod's
`memory.min` becomes `268435456` and the Burstable Pod's `memory.low` becomes `268435456`, while the
BestEffort Pod gets neither. Put the Guaranteed Pod's two numbers side by side: `memory.min` and
`memory.max` are the same value, which is the caution at `pod-qos.md:169-176` in one `cat`. Nothing
will OOM here — a `sleep` has no page cache — but the shape of the hazard is visible, and it is the
direct consequence of the post's `memory.min` equals memory request rule meeting the Guaranteed
class where requests equal limits.

Step 8 reads the ancestors. `kubepods.slice/memory.min` should equal the sum of memory requests
across Guaranteed *and* Burstable Pods, and `memory.low` on both the root and the Burstable slice
should equal the Burstable sum. On a single-node cluster the control plane's static Pods are in
those sums, so the numbers will be well above your three workload Pods — the last command lists
every Pod's QoS class so you can do the addition. Then the two metrics: expect
`kubelet_memory_qos_node_memory_min_bytes` and `kubelet_memory_qos_node_memory_low_bytes` to agree
with the files you just read. If a metric is absent, the kubelet build predates them; they are
`ALPHA` and arrived with the tiered policy.

Step 9 tests three claims. The ancestors go to zero — `kubepods.slice/memory.min`,
`kubepods.slice/memory.low` and the Burstable slice's `memory.low` all read `0` after the restart.
The two untouched Pods keep their per-container `memory.min`, `memory.low` and `memory.high` values,
because nothing reapplied a resource configuration to them; the documentation says so explicitly and
it is the surprising half. And the recreated Burstable Pod comes back with `memory.high` at `max`,
because the runtime applied a fresh configuration with the feature off. Leftover numbers in a cgroup
tree are harmless here precisely because the ancestors are zero, which is the argument
`pod-qos.md:183-185` makes.

Step 10 gives the counts. The first search returns two lines and neither is the CRI field —
`cgroups.md:36` on memory accounting and `podgroup-scheduling.md:165` on scheduler snapshots are
ordinary English — while `LinuxContainerResources` returns nothing at all, so the post's plumbing
paragraph has no descendant in the documentation. The `memoryThrottlingFactor` grep prints the one
line that says `Default: 0.9`, which you can now set against what `configz` told you. The task page
the post linked scores `0`. The merging reference prints its worked example with `MemoryQoS` as the
gate being toggled. And the census should report 401 gates with an alpha stage, eight of them longer
than fifteen releases and four of those eight since graduated, with `CPUManagerPolicyAlphaOptions`
and `KubeletInUserNamespace` tied with `MemoryQoS` at fifteen — the measurement behind this
exercise's claim that fifteen is the longest first rung this archive walks rather than the longest
anywhere.

**Read on**

1. `concepts/workloads/pods/pod-qos.md:96-199` is the whole feature in one section, and it is short
   enough to read against the post line by line. The three subsections that have no counterpart in
   the post — `Configuring memory reservation`, `Disabling or rolling back Memory QoS` and `System
   requirements` — are where four years went.

2. `reference/config-api/kubelet-config.v1beta1.md:1714-1737` is the two fields as the API declares
   them, with the `MemoryReservationPolicy` type spelled out at `:2377` onward. Read it beside
   `pod-qos.md:104-113` and decide for yourself which page you would trust about a default; then
   check `reference/command-line-tools-reference/kubelet.md`, which has no flag for either field, so
   the kubelet configuration file is the only way in.

3. `concepts/architecture/cgroups.md` is 148 lines and is the prerequisite the post compressed into
   one bullet: the requirements at `:52-61`, the distribution list at `:63-73`, and at `:39-42` the
   project's own statement that Memory QoS is one of the features that exist only on cgroup v2. It
   also carries the check for which version a node is on, which is the first thing to run on any
   node where this exercise behaves unexpectedly.

4. Three pieces of machinery here belong to earlier rows. [The swap
   exercise](05-run-nodes-with-swap-alpha.md) owns QoS classes as an eligibility rule, the cgroup
   version check, and editing the kubelet's configuration in place. [The PID limiting
   exercise](../2019/05-pid-limiting.md) owns the `--config-dir` drop-in and what to do when it is
   absent. [The CRI exercise](../2016/13-container-runtime-interface-cri-in-kubernetes.md) owns the
   interface this post passes `Unified` across. Release timing is in
   [`research/blog-era-translation.md`](../../research/blog-era-translation.md).

5. Unanswerable from the pin: why fifteen releases. The documentation records the end state and none
   of the argument — no page says why `memory.min` for every container became `memory.min` for
   Guaranteed Pods and `memory.low` for Burstable ones, or why throttling and reservation were split
   into two independently-settable fields. KEP-2570, named at `index.md:107` and again at
   `kubelet-config.v1beta1.md:1722`, is where that history lives, and it is outside the pin. Two
   smaller ones go the same way: whether the CRI-O work the post called `still in WIP` was ever
   finished, and whether the kernel livelock the pin cites is the reason the feature waited.

**Teardown**

This exercise wrote two kubelet configuration drop-ins and left one of them holding `MemoryQoS:
false`, so the teardown is to remove both and restart — the kubelet then falls back to whatever your
version's default is, which is the state step 1 measured:

```bash
sudo rm -f /etc/kubernetes/kubelet.conf.d/20-memory-qos.conf /etc/kubernetes/kubelet.conf.d/21-memory-reservation.conf
sudo systemctl restart kubelet; sleep 25
systemctl is-active kubelet
kubectl delete pod -l app=mq --ignore-not-found
NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" \
  | python3 -c 'import sys,json; c=json.load(sys.stdin)["kubeletconfig"]; print(c.get("memoryThrottlingFactor"), c.get("memoryReservationPolicy"))'
sudo cat /sys/fs/cgroup/kubepods.slice/memory.min /sys/fs/cgroup/kubepods.slice/memory.low
kubectl get nodes
```

The `configz` read should print the pair you saw in step 2 and both kubepods files should read `0`.
No swap file, no storage and no API objects were created beyond three Pods, so a `Ready` node with
those two zeroes is a complete teardown. Leave the guest up for the next exercise in this year.
