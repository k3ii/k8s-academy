<a id="swap-linux-beta"></a>

# The word beta in this post's title meant a gate that stayed off by default for two more releases, its most technical section is now the concept page with one phrase deleted and one restriction added, and three of its pointers lead to pages where the word swap no longer appears

**Post** — [Kubernetes 1.28: Beta support for using swap on Linux](https://kubernetes.io/blog/2023/08/24/swap-linux-beta/),
2023-08-24.

Itamar Holder (Red Hat). 248 lines, 12,802 bytes — the longest post in this year's thirteen walks.
It graduates the feature announced two years earlier in [the alpha swap
post](../2021/05-run-nodes-with-swap-alpha.md), which is where the node-level half of this subject
is walked; this exercise picks up exactly where that one stops.

**As written**

The opening is a history in three paragraphs. Before v1.22 "Kubernetes did not provide support for
swap memory on Linux systems", because of "the inherent difficulty in guaranteeing and accounting
for pod memory utilization when swap memory was involved", and so "the default behavior of a kubelet
was to fail to start if swap memory was detected on a node" (`:15-19`). v1.22 brought alpha, which
"was not fully developed and had several issues, including inadequate support for cgroup v2,
insufficient metrics and summary API statistics, inadequate testing, and more" (`:21-25`). Now, in
v1.28, "support for swap on Linux nodes has graduated to Beta, along with many new improvements"
(`:10-13`), and the graduation "represents a crucial step towards achieving the goal of fully
supporting swap in Kubernetes" (`:31-32`).

*How do I use it?* is four instructions. Activate the `NodeSwap` feature gate on the kubelet;
disable `failSwapOn`, "or the deprecated `--fail-swap-on` command line flag must be deactivated";
set `memorySwap.swapBehavior`, for which the post prints a three-line YAML fragment whose value is
`UnlimitedSwap`; and know that of the two available options, `UnlimitedSwap` is "(default)" and lets
workloads "use as much swap memory as they request, up to the system limit", while `LimitedSwap`
limits them and permits only Burstable QoS Pods to swap at all (`:34-57`). A closing note:
`NodeSwap` "is supported for cgroup v2 only" (`:59-60`), a restriction the post prints in bold.

*Install a swap-enabled cluster with kubeadm* is the post's practical half. Create 4GiB of
unencrypted swap with `dd`, `chmod`, `mkswap`, `swapon` (`:71-83`); then hand `kubeadm` a
configuration file that carries two documents, an `InitConfiguration` at `apiVersion:
"kubeadm.k8s.io/v1beta3"` and a `KubeletConfiguration` carrying `failSwapOn: false`, `featureGates:
NodeSwap: true` and `memorySwap.swapBehavior: LimitedSwap`; then `kubeadm init --config
kubeadm-config.yaml` (`:85-105`).

*How is the swap limit being determined with LimitedSwap?* is the technical centre. Swap
configuration "is prone to misconfiguration, but as a system-level property, any misconfiguration
could potentially compromise the entire node rather than just a specific workload", so "we have
implemented Swap in Beta with automatic configuration of limitations" (`:109-113`). Pods outside the
Burstable class are prohibited from swapping, with a reason for each: `BestEffort` Pods "exhibit
unpredictable memory consumption patterns", and `Guaranteed` Pods are "typically employed for
applications that rely on the precise allocation of resources specified by the workload, with memory
being immediately available" (`:115-123`). Three terms are defined — `nodeTotalMemory`,
`totalPodsSwapAvailable`, `containerMemoryRequest` — and the limit is `(containerMemoryRequest /
nodeTotalMemory) × totalPodsSwapAvailable` (`:125-135`). A container in a Burstable Pod can opt out
entirely "by specifying memory requests that are equal to memory limits" (`:137-139`).

*How does it work?* describes the kubelet directing the CRI to write cgroup v2 parameters "such as
`memory.swap.max`" (`:141-160`). *How can I monitor swap?* answers the alpha's worst deficiency: the
beta kubelet "now collects node-level metric statistics", readable at `/metrics/resource` and
`/stats/summary`, and "a `machine_swap_bytes` metric has been added to cadvisor" (`:162-174`).
*Caveats* is three paragraphs on unpredictability, IOPS-constrained storage and noisy neighbours,
then a *Security risk* subsection: unencrypted swap risks writing out "volumes that represent
Kubernetes Secrets", the project "strongly recommends that you encrypt your swap space", and
"handling encrypted swap is not within the scope of kubelet" (`:176-213`). *Looking ahead* forecasts
three things: system-reserved swap, Pod-level swap control via cgroups ("still under discussion"),
and possibly "new configuration modes for swap, such as a node-wide swap limit for workloads"
(`:215-226`).

**As it runs now**

The title says beta and the gate file says otherwise. `NodeSwap` carries two consecutive `beta`
stages: `defaultValue: false` for v1.28 and v1.29, then `defaultValue: true` from v1.30. So for the
release this post announces, and the one after it, beta meant a feature you still had to ask for by
name. The post is not wrong about this — its first instruction is to activate the gate — but nothing
in it tells you that the instruction would have been unnecessary at any other beta in this archive.
The gate reached `stable` with `locked: true` at v1.34, which is why the instruction is unnecessary
now: there is no gate left to set, and setting it is not possible either.

The one YAML fragment in *How do I use it?* is void. `UnlimitedSwap` occurs zero times under
`content/en/docs` at the pin; the eight occurrences left in the tree are all in blog posts, this one
among them. The two behaviours a node can pick are now `NoSwap`, which is the default, and
`LimitedSwap` (`swap-behavior.md:13-20`) — so the post's default has been deleted and replaced by
its own opposite, a behaviour under which "workloads running as Pods on this node do not and cannot
use swap". That the kubelet refuses to parse the post's value is the alpha exercise's finding and is
not re-argued here; what belongs here is that the post's sentence "If configuration for `memorySwap`
is not specified and the feature gate is enabled, by default the kubelet will apply the same
behaviour as the `UnlimitedSwap` setting" now describes the opposite of what an unconfigured node
does.

The technical centre survived almost intact, and the exceptions are countable. Lay the post's
`:109-139` beside `swap-memory-management.md:353-385` and the two are the same prose in the same
order, with four differences, three of them trivial. "We have implemented Swap in Beta with
automatic configuration of limitations" lost the two words *in Beta* that dated it; `Qos` was
corrected to `QoS`; and the formula lost the backticks that wrapped the whole expression and gained
them around each of its three terms. The fourth difference is a sentence added at `:368-369`: "In
addition, high-priority pods are not permitted to use swap in order to ensure the memory they
consume always resides in RAM, hence ready to use." That is the only line in the entire pinned
documentation tree that ties swap to priority, and it defines neither *high-priority* nor a
threshold. Step 6 is the only way to find out what it means.

The kubeadm half has no successor. The page that replaced it,
`tutorials/cluster-management/provision-swap-memory.md`, carries `min-kubernetes-server-version:
"1.33"` and is still titled for kubeadm, but its kubeadm content is now one prerequisite line: the
configuration it gives you at `:120-141` is a kubelet configuration fragment — `failSwapOn: false`
and `memorySwap.swapBehavior: LimitedSwap` — applied by editing the kubelet's own file and
restarting the service. No `kubeadm-config.yaml`, no `featureGates`, no `kubeadm init --config`. The
post's config file also names a schema that the pin marks for removal:
`kubeadm-config.v1beta3.md:257-258` says "v1beta3 is deprecated in favor of v1beta4 and will be
removed in a future release, 1.34 or later", which the lab's v1.35 and the pin's v1.37 are both
past, while the reference page itself is still published. Step 8 asks the binary rather than the
page.

Three of the post's pointers, and one of the pin's own, now lead to pages that do not mention the
subject. The post's "current documentation" link at `:230` is
`/docs/concepts/architecture/nodes/#swap-memory`; `nodes.md` at the pin contains the word *swap*
zero times. That link is not only the post's: four pinned documentation pages still carry it,
including the gate file itself at `NodeSwap.md:29` and the resize page this year's [previous
exercise](07-in-place-pod-resize-alpha.md) reads at `resize-container-resources.md:191-192`. The
post's security link at `:203` is `secret.md#information-security-for-secrets`; that heading is
still there, at `secret.md:641`, and `secret.md` contains *swap* zero times — the material moved to
`secrets-good-practices.md:90-93` and `linux-security.md:21-28`. And the post sends monitoring
readers to `node-metrics.md` at `:169`, which contains *swap* zero times, as does the pin's own
concept page when it repeats the same pointer at `swap-memory-management.md:87` for the same
purpose. Four pages, four dead ends, one subject.

What did arrive is more observability than the post asked for. Beyond the two endpoints it names,
the pin documents three named series — `node_swap_usage_bytes`, `container_swap_usage_bytes`,
`container_swap_limit_bytes` (`swap-memory-management.md:89-92`) — plus `kubectl top --show-swap`
(`:94-131`), a Node status field `.status.nodeInfo.swap.capacity` (`:133-155`), and swap discovery
via Node Feature Discovery (`:157-176`). Of the three forecasts in *Looking ahead*, the
system-reserved quantity is described as an accident rather than a setting (`:269-284`), Pod-level
swap control is absent, and swap-aware scheduling — which the post lists under *Caveats* rather than
*Looking ahead* — is still "not yet implemented" at `:328-332`.

The security risk the post raises got an answer it did not forecast. The post's position is that
encrypted swap "is not within the scope of kubelet; rather, it is a general OS configuration
concern", and it is the administrator's problem. That sentence survives verbatim at
`swap-memory-management.md:234-236`. But the specific danger it names — Secret volumes reaching the
disk — was answered inside the kubelet after all: memory-backed volumes are mounted with the `tmpfs`
`noswap` option, supported by the Linux kernel from version 6.3, and a kubelet that cannot use it
logs a warning and continues (`:208-231`). Step 9 checks the mount rather than the claim.

**What this exercise does not cover, and where it lives**

Everything at the node level belongs to [the alpha swap
exercise](../2021/05-run-nodes-with-swap-alpha.md) and is not repeated: the `NodeSwap` ladder
itself, the kubelet's refusal to parse `UnlimitedSwap`, `failSwapOn`, the arithmetic worked without
a Pod, the cgroup v1 rows, and the kubelet's own swap on the system slice. That exercise stops at
the node and says so; this one starts at the Pod. cgroup v2 as a mechanism is [the version that went
GA in 1.25](../2022/06-cgroupv2-ga-1-25.md).

**The diff, and why**

The post ***broke*** in its second half and nowhere else. The kubeadm recipe no longer matches any
documented path: the gate in it cannot be set, the schema it is written in is marked for removal in
a release two behind the lab, and the page that replaced it configures the kubelet directly. The one
YAML fragment in its first half prints a value that no longer exists. Both failures are
configuration, and both are the kind an announcement written at a stage boundary is most exposed to.

The technical centre is ***still right***, and the interesting thing is *how* right. The whole of
*How is the swap limit being determined with LimitedSwap?* is now the *Swap behavior details*
section of a 394-line concept page, with two words removed, one typo fixed and one restriction
added. The post was not superseded; it was promoted — ***retired by being agreed with*** in its
cleanest form. Nothing on the concept page credits it, and nothing needs to — but a reader who knows
only the page will not know that a restriction was added to it, and a reader who knows only the post
will not know that priority now excludes a Pod from swapping.

The title is the part worth carrying. *Beta support* is a phrase readers price as *on unless you
turn it off*, and for two releases it was not. The gate file is the only place that says so, because
the post could not have: at publication the second `beta` row did not exist. An announcement can
only describe the stage it is written at, and a stage is not a promise about defaults — which is the
whole reason this archive ladders gates instead of trusting titles.

The `NodeSwap` ladder is transcribed in full by the alpha exercise linked above, including the two
`beta` rows argued here. Nothing here re-ladders that gate.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 vCPU, 25G, at `10.10.10.180`.
Swap is a per-node property and every measurement here is taken on the node, so a second node would
only provide a second place to run the same commands. Provision with the [standard
steps](../../strands/lab-topologies.md#provision) and the [node
baseline](../../strands/lab-topologies.md#node-baseline-steps), then `ssh zain@10.10.10.180`. Step 2
writes a 1GiB swap file, which the 25G disk has room for; if the guest from the alpha swap exercise
is still up with swap already provisioned, step 2 is idempotent and will tell you so.

Every Pod here runs `registry.k8s.io/pause:3.10` and consumes nothing. That is deliberate: the
numbers you read are limits the kubelet computed and wrote, not usage a workload produced, and the
whole question is what it decided to write.

**Do**

1. Ask the node what it believes before changing anything, and confirm there is no gate left to set.

   ```sh
   kubectl version | head -2
   NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' | grep -i nodeswap
   swapon --show || echo "no swap devices"
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" | python3 -c \
     'import sys,json; c=json.load(sys.stdin)["kubeletconfig"]; print("failSwapOn:", c.get("failSwapOn"), "memorySwap:", c.get("memorySwap"))'
   ```

2. Provision swap and configure the kubelet the way the pin's tutorial does at
   `provision-swap-memory.md:73-86` and `:120-141`, scaled to 1GiB. Nothing from the post's kubeadm
   section is used.

   ```sh
   sudo swapon --show | grep -q /swapfile || {
     sudo fallocate --length 1GiB /swapfile && sudo chmod 600 /swapfile
     sudo mkswap /swapfile >/dev/null && sudo swapon /swapfile; }
   sudo cp -n /var/lib/kubelet/config.yaml /var/lib/kubelet/config.yaml.bak
   grep -q failSwapOn /var/lib/kubelet/config.yaml \
     || printf 'failSwapOn: false\nmemorySwap:\n  swapBehavior: LimitedSwap\n' | sudo tee -a /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet; sleep 20
   systemctl is-active kubelet
   kubectl get node "$NODE" -o jsonpath='swapCapacity={.status.nodeInfo.swap.capacity}{"\n"}'
   ```

3. Create one Pod per QoS class, plus the opt-out the post describes at `:137-139`: Burstable in
   shape, but with memory request equal to memory limit.

   ```sh
   kubectl create ns swapdemo
   cat > /tmp/swapdemo.yaml <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: burstable, namespace: swapdemo }
   spec:
     containers:
       - name: app
         image: registry.k8s.io/pause:3.10
         resources:
           requests: { cpu: 50m, memory: 512Mi }
           limits: { cpu: 200m, memory: 1Gi }
   ---
   apiVersion: v1
   kind: Pod
   metadata: { name: guaranteed, namespace: swapdemo }
   spec:
     containers:
       - name: app
         image: registry.k8s.io/pause:3.10
         resources:
           requests: { cpu: 100m, memory: 512Mi }
           limits: { cpu: 100m, memory: 512Mi }
   ---
   apiVersion: v1
   kind: Pod
   metadata: { name: besteffort, namespace: swapdemo }
   spec:
     containers:
       - name: app
         image: registry.k8s.io/pause:3.10
   ---
   apiVersion: v1
   kind: Pod
   metadata: { name: optout, namespace: swapdemo }
   spec:
     containers:
       - name: app
         image: registry.k8s.io/pause:3.10
         resources:
           requests: { cpu: 50m, memory: 512Mi }
           limits: { cpu: 200m, memory: 512Mi }
   EOF
   kubectl apply -f /tmp/swapdemo.yaml
   kubectl -n swapdemo wait --for=condition=Ready pod --all --timeout=90s
   kubectl -n swapdemo get pods -o custom-columns=NAME:.metadata.name,QOS:.status.qosClass
   ```

4. Read what the kubelet actually wrote into each container's cgroup. This is the CRI round trip
   from the post's `:156-160`, seen from the other end.

   ```sh
   cat > /tmp/swapmax.sh <<'EOF'
   #!/bin/sh
   for p in "$@"; do
     u=$(kubectl -n swapdemo get pod "$p" -o jsonpath='{.metadata.uid}' | tr '-' '_')
     d=$(sudo find /sys/fs/cgroup/kubepods.slice -maxdepth 2 -type d -name "*$u*" | head -1)
     [ -n "$d" ] || { echo "$p: no cgroup found"; continue; }
     for c in "$d"/*.scope; do
       printf '%-11s swap.max=%-12s memory.max=%s\n' "$p" \
         "$(sudo cat "$c/memory.swap.max" 2>/dev/null)" "$(sudo cat "$c/memory.max" 2>/dev/null)"
     done
   done
   EOF
   chmod +x /tmp/swapmax.sh
   /tmp/swapmax.sh burstable guaranteed besteffort optout
   ```

5. Do the arithmetic the pin gives at `swap-memory-management.md:371-381` and compare it with the
   number you just read.

   ```sh
   NODEMEM=$(kubectl get node "$NODE" -o jsonpath='{.status.capacity.memory}')
   SWAPCAP=$(kubectl get node "$NODE" -o jsonpath='{.status.nodeInfo.swap.capacity}')
   echo "nodeTotalMemory=$NODEMEM totalSwap=$SWAPCAP"
   python3 -c "
   total = int('${NODEMEM}'.rstrip('Ki')) * 1024
   swap  = int('${SWAPCAP}' or 0)
   req   = 512 * 1024**2
   print('predicted swap.max for a 512Mi request: %d bytes (%.1f MiB)' % (req/total*swap, req/total*swap/1024**2))"
   ```

6. Settle the one sentence the pin added to the post's section. `swap-memory-management.md:368-369`
   says high-priority Pods may not swap, and defines neither the word nor a threshold.

   ```sh
   kubectl create priorityclass swap-high --value=1000000000 \
     --description='deliberately high, to test the rule at swap-memory-management.md:368'
   kubectl -n swapdemo run highprio --image=registry.k8s.io/pause:3.10 \
     --overrides='{"spec":{"priorityClassName":"swap-high","containers":[{"name":"app","image":"registry.k8s.io/pause:3.10","resources":{"requests":{"cpu":"50m","memory":"512Mi"},"limits":{"cpu":"200m","memory":"1Gi"}}}]}}'
   kubectl -n swapdemo wait --for=condition=Ready pod/highprio --timeout=60s
   kubectl -n swapdemo get pod highprio -o jsonpath='qos={.status.qosClass} priority={.spec.priority}{"\n"}'
   /tmp/swapmax.sh burstable highprio
   ```

7. Read the three series the pin names, straight off the kubelet, and check them against the cgroup.

   ```sh
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/metrics/resource" | grep -i swap | head -12
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/stats/summary" | python3 -c \
     'import sys,json; d=json.load(sys.stdin); print("node swap:", d["node"].get("swap"));
   [print(" ", p["podRef"]["name"], p.get("swap")) for p in d.get("pods",[]) if p["podRef"]["namespace"]=="swapdemo"]'
   ```

8. Hand the post's kubeadm configuration to the kubeadm you actually have, unchanged from `:89-101`.

   ```sh
   cat > /tmp/post-kubeadm-config.yaml <<'EOF'
   ---
   apiVersion: "kubeadm.k8s.io/v1beta3"
   kind: InitConfiguration
   ---
   apiVersion: kubelet.config.k8s.io/v1beta1
   kind: KubeletConfiguration
   failSwapOn: false
   featureGates:
     NodeSwap: true
   memorySwap:
     swapBehavior: LimitedSwap
   EOF
   kubeadm version -o short
   sudo kubeadm config migrate --old-config /tmp/post-kubeadm-config.yaml 2>&1 | head -20
   ```

9. Check the mitigation the post says is not the kubelet's job. Mount both kinds of memory-backed
   volume and ask the mount table, not the documentation.

   ```sh
   kubectl -n swapdemo create secret generic demo --from-literal=k=v
   kubectl -n swapdemo run tmpfs --image=registry.k8s.io/pause:3.10 --overrides='{"spec":{"containers":[{"name":"app","image":"registry.k8s.io/pause:3.10","volumeMounts":[{"name":"s","mountPath":"/s"},{"name":"m","mountPath":"/m"}]}],"volumes":[{"name":"s","secret":{"secretName":"demo"}},{"name":"m","emptyDir":{"medium":"Memory"}}]}}'
   kubectl -n swapdemo wait --for=condition=Ready pod/tmpfs --timeout=60s
   uname -r
   findmnt -t tmpfs -o TARGET,OPTIONS | grep -E 'secret|empty' | head -6
   sudo journalctl -u kubelet --no-pager | grep -ci noswap || echo "no noswap log lines"
   ```

10. Offline, in a checkout of `kubernetes/website` at the pin, read the four pointers and the one
    added sentence.

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -ci swap docs/concepts/architecture/nodes.md
    grep -rn 'architecture/nodes/#swap-memory' --include='*.md' docs | wc -l
    grep -ci swap docs/reference/instrumentation/node-metrics.md docs/concepts/configuration/secret.md
    grep -rn 'UnlimitedSwap' --include='*.md' docs | wc -l
    sed -n '353,385p' docs/concepts/cluster-administration/swap-memory-management.md
    sed -n '257,258p' docs/reference/config-api/kubeadm-config.v1beta3.md
    cat docs/reference/command-line-tools-reference/feature-gates/NodeSwap.md
    ```

**Expect**

Step 1 finds a node that has never seen swap, and a gate that is not there to be set. The metric
grep prints `NodeSwap` at stage `STABLE` with value 1, or nothing at all if your build has already
dropped locked gates from the series; either way there is nothing to enable. `swapon --show` is
empty and `configz` reports `failSwapOn: True` with `memorySwap: None`. That is the state the post
assumes you are *not* in.

Step 2 brings the node up with 1GiB of swap and a kubelet that tolerates it. `is-active` prints
`active`, and the Node object reports `swapCapacity=1073741824`. Note what you did not write: no
feature gate, and no kubeadm configuration file. Two of the post's four instructions are now empty
and the other two are one file away from each other.

Step 3 prints the three classes plainly — `burstable`, `guaranteed` and `besteffort` in their
matching QoS classes, and `optout` as `Burstable`, because its CPU request is still below its CPU
limit even though its memory request equals its memory limit. That last one is the whole of the
post's `:137-139` in one manifest.

Step 4 is the measurement the census row asks for, and it should read like the post's own rules
written in bytes. `burstable` carries a `memory.swap.max` in the region of 140–150 MiB. `guaranteed`
and `besteffort` carry `0`. `optout` carries `0` as well, which is the post's opt-out working
exactly as described, on a Pod that is otherwise identical to the one that got swap. Four Pods, one
kubelet, four different answers, and every one of them follows from a sentence written in 2023.

Step 5 should land on `burstable`'s number. With a 3.8GiB-capacity node and 1GiB of swap, a 512Mi
request predicts roughly 138 MiB. Expect the prediction and the cgroup to agree to within the
difference between the node's `capacity.memory` and the kubelet's `totalPodsSwapAvailable`, which is
not the same quantity — the pin defines the latter as swap "available for use by Pods (some swap
memory may be reserved for system use)" (`swap-memory-management.md:373`) and never says how much is
reserved. If the two numbers differ, that gap is the reservation, and it is the only way the pin
lets you see it.

Step 6 answers a question the documentation does not. `highprio` is Burstable, with the same
requests and limits as `burstable`, and differs only in `.spec.priority`. If its `memory.swap.max`
is `0` while `burstable`'s is not, the rule at `swap-memory-management.md:368-369` is live and the
threshold is at or below the value `1000000000`. If both carry the same non-zero limit, the sentence
is documentation ahead of the code at this version, and that is worth writing down just as plainly.
Do not resolve it by reasoning; the number is on the node.

Step 7 prints `container_swap_limit_bytes` and `container_swap_usage_bytes` per container and
`node_swap_usage_bytes` once. The limits should match step 4 exactly, because they are the same
kernel file read by a different route. The usages are `0` — `pause` never allocates, so nothing can
be paged out, and a swap limit is a ceiling rather than a reservation. The summary API reports the
same pods with a `swap` block each.

Step 8 is the post's configuration file meeting the tool it was written for, three years and seven
releases later. Either `kubeadm` migrates it and prints a `v1beta4` document — in which case the
deprecation notice at `kubeadm-config.v1beta3.md:257-258` is still ahead of the binary, three
releases after the removal it names — or it refuses the API version outright, in which case the
post's recipe cannot be run at all and the reference page publishing the schema is the thing that is
stale. Record which, and the exact message. Either result is the finding.

Step 9 is the answer the post did not forecast. `uname -r` on a Trixie guest reports a 6.x kernel
well past the 6.3 the `noswap` option needs, and `findmnt` should show both the Secret mount and the
memory-backed `emptyDir` as `tmpfs` carrying `noswap` among their options. The post told you that
keeping Secrets out of swap was the administrator's job; the kubelet took the specific case and left
the general one — encrypted swap — exactly where the post put it.

Step 10 is the whole finding in seven commands. `nodes.md` returns `0` for *swap* and the anchor
count returns `4`, so four pinned pages point readers at a page that has nothing to say to them;
`node-metrics.md` and `secret.md` both return `0` for the same reason; `UnlimitedSwap` returns `0`
under `docs`, which is the post's default erased. The two `sed` ranges print the section that was
promoted and the deprecation notice that was not acted on, and the gate file — twenty-nine lines —
prints the two consecutive `beta` rows that the title of this post could not have known about.

**Read on**

1. `swap-memory-management.md:238-267`, on eviction thresholds against `vm.min_free_kbytes`. It is
   the longest passage on the page with no ancestor in either swap post, and it describes a way to
   misconfigure a node that neither announcement mentions.

2. `swap-memory-management.md:326-337`, swap-aware scheduling, beside the post's `:180-184`. The
   post lists it as a caveat; the page lists it as work in progress and suggests tainting nodes as
   the workaround, which is the same admission in a different mood.

3. `provision-swap-memory.md:47-70`, the encrypted-swap tab. It is the one part of the post's
   *Security risk* section that the project answered by writing instructions rather than by changing
   the kubelet.

4. `secrets-good-practices.md:90-93` and `linux-security.md:21-28`, the two pages that now hold what
   the post's security link pointed at. Read them together and note that neither cites the other's
   mechanism.

5. *Unanswerable from the pin.* What counts as a high-priority Pod for the purposes of
   `swap-memory-management.md:368-369`. The sentence occurs once in the tree, names no threshold, no
   PriorityClass and no field, and no other page under `content/en` mentions swap and priority
   together.

**Teardown**

```sh
kubectl delete ns swapdemo --ignore-not-found
kubectl delete priorityclass swap-high --ignore-not-found
rm -f /tmp/swapdemo.yaml /tmp/post-kubeadm-config.yaml /tmp/swapmax.sh
sudo cp /var/lib/kubelet/config.yaml.bak /var/lib/kubelet/config.yaml
sudo systemctl restart kubelet; sleep 15
sudo swapoff /swapfile && sudo rm -f /swapfile
systemctl is-active kubelet
```

The order matters: restore the kubelet configuration before removing the swap file, or you will
restart a kubelet that has `failSwapOn: false` withdrawn while swap is still active and watch it
refuse to start for a reason that has nothing to do with this exercise. Then return the guest with
the [standard teardown](../../strands/lab-topologies.md#teardown), or leave it up.

Back to the [2023 census](README.md).
