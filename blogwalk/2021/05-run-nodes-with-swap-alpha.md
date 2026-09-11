<a id="run-nodes-with-swap-alpha"></a>

# The one configuration value this post documents does not parse at the pin, the default it names in parentheses is not the default any more, and both rows of its cgroups table are void — while three of its six caveat sentences are now documentation, character for character

**Post** — [New in Kubernetes v1.22: alpha support for using swap
memory](https://kubernetes.io/blog/2021/08/09/run-nodes-with-swap-alpha/), 2021-08-09, by Elana
Hashman (Red Hat) — 142 lines, 7,143 bytes. The first announcement of node swap support, written at
alpha, and the only exercise in this sweep where the post's central YAML block is rejected by the
software it configures. Everything the post says about *danger* is still true, and most of it is now
in the documentation word for word. Everything it says about *configuration* has been replaced.

**As written**

The opening states the prior position and why it was held. `:13-17`: `In prior releases, Kubernetes
did not support the use of swap memory on Linux, as it is difficult to provide guarantees and
account for pod memory utilization when swap is involved. As part of Kubernetes' earlier design,
swap support was considered out of scope, and a kubelet would by default fail to start if swap was
detected on a node.` `:19-23` lists the use cases — node stability, applications with `high memory
overhead but smaller working sets`, memory-constrained devices, memory flexibility — and `:25-30`
frames the release as `our first milestone towards this goal`.

`## How does it work?` at `:32-54` gives the design in three bullets (`:39-43`): the kubelet can
start with swap on, it directs the container runtime to allocate `zero swap memory to Kubernetes
workloads by default`, and you can configure swap utilization `for the entire node`. `:45-48` names
the knob — `memorySwap` in the KubeletConfiguration, set through `memorySwap.swapBehavior` — and
`:50-54` names the plumbing: a new `memory_swap_limit_in_bytes` field in the container runtime
interface, written by the runtime to `the container level cgroup`.

`## How do I use it?` at `:56-87` is the operational half, and it is four instructions. Enable the
`NodeSwap` feature gate on the kubelet (`:58-59`). Disable `failSwapOn` in the configuration or
`--fail-swap-on` on the command line (`:60-61`). Optionally set `memorySwap.swapBehavior`, in a
four-line YAML block at `:66-69` whose value is `LimitedSwap`. And choose between the two documented
values at `:73-76`: `LimitedSwap (default): Kubernetes workloads are limited in how much swap they
can use. Workloads on the node not managed by Kubernetes can still swap.` and `UnlimitedSwap:
Kubernetes workloads can use as much swap memory as they request, up to the system limit.` `:78-80`
adds that an unset `memorySwap` behaves as `LimitedSwap`, and `:82-87` makes `LimitedSwap` mean two
different things depending on the node: on cgroups v1, `Kubernetes workloads can use any combination
of memory and swap, up to the pod's memory limit, if set`; on cgroups v2, `Kubernetes workloads
cannot use swap memory`.

`### Caveats` at `:89-109` is six sentences of warning and one request. Swap reduces predictability;
its performance is worse than memory `sometimes by many orders of magnitude`; it changes behaviour
under memory pressure and `applications cannot directly control what portions of their memory usage
are swapped out`; it raises the risk of `noisy neighbours and unexpected packing configurations, as
the scheduler cannot account for swap memory usage`; performance depends on the backing storage and
is `significantly worse in an I/O operations per second (IOPS) constrained environment`. Then the
recommendation at `:106-109`: benchmark before production, and `we need your help` with that.

`## Looking ahead` at `:111-124` commits to beta `in the 1.23 release`, with three pieces of work:
Pod-level swap consumption control via cgroups, including `the ability to set a system-reserved
quantity of swap from what kubelet detects on the host`; a set of metrics `for node QoS in order to
evaluate the performance and stability of nodes with and without swap enabled`; and feedback
collection, which `will consider introducing new configuration modes for swap, such as a node-wide
swap limit for workloads`. `:126-133` sends readers to the documentation and to KEP-2400, and
`:135-142` to SIG Node.

**As it runs now** — the feature is stable and on by default, and almost none of the post's
configuration survives. Sorting which sentences are which is the exercise.

**The value at the centre of the post does not exist.** `UnlimitedSwap` appears nowhere in
`content/en/docs` at the pin — not in the reference, not in the concept page, not in the gate file.
Its eight occurrences in the whole pinned site are all in the blog archive: this post, the beta
announcement two years later, and two 2025 posts. What the kubelet accepts is in
`reference/config-api/kubelet-config.v1beta1.md:2409-2411`, and it is a closed list: `swapBehavior
configures swap memory available to container workloads. May be one of "", "NoSwap": workloads can
not use swap, default option. "LimitedSwap": workload swap usage is limited. The swap limit is
proportionate to the container's memory request.` Two values and the empty string. Setting the
post's other one is step 2.

**The default moved, and it moved to a value that did not exist when the post was written.**
`reference/node/swap-behavior.md:13-17` gives `NoSwap` the parenthesis: `(default) Workloads running
as Pods on this node do not and cannot use swap. However, processes outside of Kubernetes' scope,
such as system daemons (including the kubelet itself!) can utilize swap.`
`concepts/cluster-administration/swap-memory-management.md:53-57` says the same in the short form.
So the post's `LimitedSwap (default)` is wrong twice over at the pin: it is not the default, and the
thing that is the default is a third option the post never mentions. The reason is not in the
documentation, which never discusses `UnlimitedSwap` at all; the only account in the pinned site is
a 2025 announcement, a later row of this sweep, which says the behaviour `was removed since it might
compromise the node's health`.

**Both rows of the cgroups table are void, for different reasons.** The cgroups v1 row describes a
node the kubelet will not start on: `concepts/architecture/cgroups.md:134-142` marks cgroup v1
deprecated as of v1.35 and states `Kubelet will no longer start on a cgroup v1 node by default`,
with `failCgroupV1` as the override — a field `kubelet-config.v1beta1.md:1803-1807` documents as
`Default: true`, meaning `the kubelet will not start on cgroup v1 hosts unless this option is
explicitly disabled`. The cgroups v2 row — `Kubernetes workloads cannot use swap memory` — is now
the definition of a different setting: it is what `NoSwap` means. On cgroup v2 at the pin,
`LimitedSwap` is precisely the configuration under which workloads *can* swap. The table has not
drifted; it has inverted.

**`LimitedSwap` was not adjusted, it was replaced by a formula.**
`swap-memory-management.md:359-369` restricts it by QoS class: Pods that are not Burstable —
`BestEffort` and `Guaranteed` — are `prohibited from utilizing swap memory`, and so are containers
in high-priority Pods. For the Burstable containers that remain, `:371-381` gives the arithmetic:
with `nodeTotalMemory` the node's physical memory and `totalPodsSwapAvailable` the swap not reserved
for the system, a container's limit is ( `containerMemoryRequest` / `nodeTotalMemory` ) ×
`totalPodsSwapAvailable`. `:383-385` adds the only Pod-level control there is: set memory requests
equal to memory limits and the container gets no swap. Nothing here is configured; all of it is
computed. The post's `limited in how much swap they can use` is true and tells you nothing about how
much.

**The one instruction that still works verbatim is the one about `failSwapOn`.**
`kubelet-config.v1beta1.md:1384-1385` still reads `failSwapOn tells the Kubelet to fail to start if
swap is enabled on the node. Default: true`, unchanged in sixteen releases, and it is still the
first thing you have to turn off. The alternative the post offers in the same sentence has aged: the
`--fail-swap-on` flag exists at `reference/command-line-tools-reference/kubelet.md:368-371` and
carries `(DEPRECATED: This parameter should be set via the config file specified by the Kubelet's
--config flag.)`. The command-line half of the post's instruction is the half that decayed, which is
a pattern the [dynamic-kubelet-configuration exercise](../2018/05-dynamic-kubelet-configuration.md)
walks from the other end.

**The metrics the post promised arrived, and there are more of them than it asked for.**
`reference/instrumentation/metrics.md` carries four swap series — `node_swap_usage_bytes` (`:3346`),
`pod_swap_usage_bytes` (`:3395`), `container_swap_usage_bytes` (`:1862`) and
`container_swap_limit_bytes` (`:1855`), each noted as `Reported only on non-windows systems`. The
concept page lists three of the four at `:89-92` and adds cadvisor's `machine_swap_bytes` at
`:85-86`. Beyond metrics, the API grew a field: `node.status.nodeInfo.swap.capacity`, a
`NodeSwapStatus` with a single member, `Total amount of swap memory in bytes`
(`reference/kubernetes-api/core/node-v1.md:473-487` and `:536`). And `kubectl top` grew
`--show-swap` (`:94-131`). The forecast that was hardest to state precisely is the one that
over-delivered.

**The two forecasts about configuration both went the other way.** Pod-level control via cgroups did
not become a knob — it became the formula above, with the requests-equal-limits opt-out as its only
user-facing switch. The `system-reserved quantity of swap` survives as a *concept*, named as
`totalPodsSwapAvailable` at `:373` and explained under `Unutilized swap space` as an emergent
property rather than a setting: because Guaranteed Pods may not swap, `the amount of swap that's
proportional to the memory request for Guaranteed pods would remain unused by Kubernetes workloads`
(`:279-280`), which `effectively keeps some system-reserved amount of swap memory` (`:283`). And the
promise to `consider introducing new configuration modes` resolved by subtraction: the option set is
still two values, but one of the post's two was withdrawn and a stricter one added.

**The caveats are the part of this post that became the documentation.** Of the six sentences in
`### Caveats`, three appear on `swap-memory-management.md` character for character: `Having swap
available on a system reduces predictability.` (`:187`), `The performance of a node with swap memory
enabled depends on the underlying physical storage.` (`:199`), and the whole IOPS sentence
(`:200-203`). The other three are rewritten while keeping the claim, and one rewrite is worth the
whole comparison. The post wrote `as the scheduler cannot account for swap memory usage`; the page
writes `the scheduler currently does not account for swap memory usage` (`:194-196`). A permanent
limitation was restated as a temporary one.

**That softened sentence is still true at v1.37, and the page says so in the first person.**
`swap-memory-management.md:328-332` — where the release number is a `skew` shortcode that renders as
whichever version you are reading — says the project `does not support allocating Pods to nodes in a
way that accounts for swap memory usage. The scheduler typically uses requests for infrastructure
resources to guide Pod placement, and Pods do not request swap space; they just request memory. This
means that the scheduler does not consider swap memory when making scheduling decisions. While this
is something we are actively working on, it is not yet implemented.` The recommended workaround at
`:334-337` is to taint the swap-enabled nodes. Sixteen releases after the post named this as a
caveat, the fix is still described as in progress, and step 9 measures why: there is no swap
quantity anywhere in the scheduler's inputs.

**The post's subject outgrew its documentation link.** What `:128-129` calls `the current
documentation` is one anchor on the node concept page. At the pin the subject is three pages: a
394-line concept page (`concepts/cluster-administration/swap-memory-management.md`), a 22-line
reference page whose only job is to define the two behaviours (`reference/node/swap-behavior.md`),
and a tutorial that provisions swap with `kubeadm`
(`tutorials/cluster-management/provision-swap-memory.md`, carrying `min-kubernetes-server-version:
"1.33"`). The anchor the post links to is a separate finding, and it belongs to the beta
announcement's row later in this sweep, which reads it where the gate file repeats it.

**What this exercise does not cover.** The gate's beta window and the two consecutive `beta` rows
are the beta announcement's story, two years later in the archive, and the Pod-level reading of swap
behaviour off a running Burstable workload belongs there with it. This exercise stops at the node:
the values the kubelet accepts, the arithmetic it would apply, and the caveats. Kubelet
configuration mechanics — the drop-in directory, rollback, what happens to a kubelet that cannot
parse its own config — are [the dynamic-kubelet-configuration
exercise](../2018/05-dynamic-kubelet-configuration.md). Reading a `locked` stable stage is [the
PID-limiting exercise](../2019/05-pid-limiting.md). The `/metrics/resource` path these swap series
ride on is [the resource-monitoring exercise](../2015/02-resource-usage-monitoring-kubernetes.md).
Release dates and the pressure behind each are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

**The diff, and why** — four cases, cleanly separated by which half of the post they touch.

**Broke: the configuration.** One of the two values in the post's own list is not accepted, the
default is a value the post does not name, the YAML block at `:66-69` parses only because the value
in it happens to be the surviving one, and both rows of the `LimitedSwap` table describe situations
that no longer arise. This is unusual for this archive. Announcements normally break at the edges —
a flag renamed, a group-version moved — and here the failure is at the centre: the post's job was to
tell you what to write in the kubelet's configuration file, and at the pin it gets that wrong in
three of four particulars. Alpha is the honest explanation and the post says so at `:29-30`, calling
this `our first milestone`. That is the thing worth carrying: an alpha announcement's
*configuration* has a half-life measured in releases, and its *reasoning* does not.

**Retired by being agreed with.** The caveats were absorbed. Three sentences moved without a
character changing, two were rewritten with the same claim, and one was rewritten in a way that
weakened it. Nothing on the concept page credits the post, and nothing needs to: the argument for
why swap is dangerous, made in a blog post at alpha, is now the `Risks and caveats` section of a
concept page four times its length, which then goes further than the post did — eviction thresholds
against `vm.min_free_kbytes` (`:238-262`), `tmpfs` volumes that must not swap (`:208-236`), swap on
control-plane nodes (`:310-314`), encrypted swap as a recommendation (`:318`).

**Overtaken by stasis.** Swap-aware scheduling was named as a caveat in 2021 and is described at the
pin as active work that is `not yet implemented`. The wording drifted in one direction only: the
post's `cannot` became the page's `currently does not`, and the page then admits in the same section
that nothing has changed. A limitation that gets softer language and no fix over sixteen releases is
worth recognising as a shape, because the softer wording is the thing that misleads — `currently`
implies a schedule that the page does not claim to have.

**A plan the project abandoned, and a schedule it missed.** The post commits to beta `in the 1.23
release`. The gate went beta at v1.28, five releases later, and the promise of `new configuration
modes for swap, such as a node-wide swap limit for workloads` produced nothing: no node-wide limit
exists at the pin, and the per-container limit is computed rather than configured. The one concrete
promise in `## Looking ahead` that did land is the metrics work, which landed larger than promised.
Read the three forecasts together and the pattern is that the observability promise was kept, the
schedule slipped, and the configuration promises were replaced by decisions to configure less.

**The ladder**

One gate, transcribed from its `stages:` list parsed as YAML. It is the post's own gate, and it is
the only gate in this exercise — there is no second gate anywhere near swap at the pin.

```
NodeSwap  alpha  false  1.22 - 1.27
          beta   false  1.28 - 1.29
          beta   true   1.30 - 1.33
          stable true   1.34 -        locked
```

The row this post announces is the first one, and its span is the finding: six releases of alpha,
off by default, against a post that expected beta in the next release. The two `beta` rows that
follow are the shape the beta announcement's exercise is built on, so read them there and not here.
The last row is `stable` with `locked`, which is the point at which `failSwapOn` and `memorySwap`
stop being gated at all — at v1.34 the gate cannot be turned off, so at the pin there is nothing to
enable and step 1 will find no `NodeSwap` anywhere in the kubelet's configuration. The gate's body
text is one sentence plus a requirement: `Enable the kubelet to allocate swap memory for Kubernetes
workloads on a node. Must be used with KubeletConfiguration.failSwapOn set to false.` That
requirement survives verbatim from 2021 and is the only sentence about swap that the gate file, the
concept page and the post all agree on.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`, 4096MB, 4
CPUs, 25G. One node is right for two reasons. Swap is a per-node property, so a second node would
only give you a second place to run the same commands; and this exercise restarts the kubelet with
configuration the kubelet may refuse, which on a single-node cluster means the control plane and the
workload node fail together and you can see it from the host. Provision 4096MB and 25G as written —
step 4 writes a 1GiB swap file, which the 25G disk has room for. If the guest from the previous
exercise in this year is still up, keep it; otherwise bring it up with [the five provision
steps](../../strands/lab-topologies.md#provision), substituting `topology=solo`, then `ssh
zain@10.10.10.180`.

**Do**

1. Start by asking the node what it currently believes about swap, before changing anything. Three
   sources that can disagree — the file, the running kubelet's own view of its configuration, and
   the kernel:

   ```sh
   sudo grep -n -i 'swap' /var/lib/kubelet/config.yaml || echo "no swap key in the config file"
   NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" \
     | python3 -c 'import sys,json; c=json.load(sys.stdin)["kubeletconfig"]; print("failSwapOn:", c.get("failSwapOn")); print("memorySwap:", c.get("memorySwap")); print("featureGates:", c.get("featureGates", {}))'
   swapon --show || echo "no swap devices"
   free -h | grep -i swap
   ```

2. Now the post's central configuration, exactly as `:66-69` gives it, with the value from `:75`.
   Back the file up first — you are going to need the backup:

   ```sh
   sudo cp /var/lib/kubelet/config.yaml /var/lib/kubelet/config.yaml.bak
   printf 'memorySwap:\n  swapBehavior: UnlimitedSwap\n' | sudo tee -a /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet; sleep 10
   systemctl is-active kubelet; echo "exit=$?"
   sudo journalctl -u kubelet --since '-2min' --no-pager | grep -i -m5 'swap\|unsupported\|invalid'
   ```

3. Change one word and restart again. This is the same file, the same shape, the same indentation —
   only the value differs, and only one of the post's two values is still a value:

   ```sh
   sudo sed -i 's/swapBehavior: UnlimitedSwap/swapBehavior: LimitedSwap/' /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet; sleep 10
   systemctl is-active kubelet
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" \
     | python3 -c 'import sys,json; print(json.load(sys.stdin)["kubeletconfig"].get("memorySwap"))'
   ```

4. Provision swap the way `tutorials/cluster-management/provision-swap-memory.md:73-86` does, scaled
   down to 1GiB, and restart the kubelet *without* touching `failSwapOn`. The post's `:16-17` claim
   about the prior behaviour is a claim you can still test:

   ```sh
   sudo fallocate --length 1GiB /swapfile && sudo chmod 600 /swapfile
   sudo mkswap /swapfile >/dev/null && sudo swapon /swapfile
   swapon --show; free -h | grep -i swap
   sudo systemctl restart kubelet; sleep 10
   systemctl is-active kubelet
   sudo journalctl -u kubelet --since '-2min' --no-pager | grep -i -m3 'swap'
   ```

5. Turn off the check the post tells you to turn off, and watch the node report something it could
   not report in 2021:

   ```sh
   printf 'failSwapOn: false\n' | sudo tee -a /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet; sleep 15
   systemctl is-active kubelet
   kubectl get node "$NODE" -o jsonpath='{.status.nodeInfo.swap}{"\n"}'
   kubectl get nodes -o go-template='{{range .items}}{{.metadata.name}}: {{if .status.nodeInfo.swap.capacity}}{{.status.nodeInfo.swap.capacity}}{{else}}<unknown>{{end}}{{"\n"}}{{end}}'
   ```

6. Read the metrics `## Looking ahead` asked for, straight from the kubelet. No metrics-server is
   needed for this — the series are on the kubelet's own endpoint, and going there directly is the
   difference between measuring and trusting:

   ```sh
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/metrics/resource" | grep -i swap
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/stats/summary" \
     | python3 -c 'import sys,json; d=json.load(sys.stdin); print("node swap:", d["node"].get("swap")); print("pods reporting swap:", sum(1 for p in d.get("pods",[]) if p.get("swap")))'
   kubectl top nodes --show-swap 2>&1 | head -3
   ```

7. Settle which row of the post's cgroups table your node is on, and find out what the pin does with
   the other one:

   ```sh
   stat -fc %T /sys/fs/cgroup
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" \
     | python3 -c 'import sys,json; c=json.load(sys.stdin)["kubeletconfig"]; print("failCgroupV1:", c.get("failCgroupV1")); print("cgroupDriver:", c.get("cgroupDriver"))'
   sudo journalctl -u kubelet --no-pager | grep -ci 'cgroup v1' || echo 0
   ```

8. Do the arithmetic the pin substituted for the post's table. You now have both inputs, so compute
   what a Burstable container asking for 512Mi would actually be given — no Pod required, and no Pod
   wanted, because the running behaviour belongs to a later exercise:

   ```sh
   NODEMEM=$(kubectl get node "$NODE" -o jsonpath='{.status.capacity.memory}')
   SWAPCAP=$(kubectl get node "$NODE" -o jsonpath='{.status.nodeInfo.swap.capacity}')
   echo "nodeTotalMemory=$NODEMEM  swapCapacity=$SWAPCAP"
   python3 -c "
   req = 512 * 1024**2
   total = int('${NODEMEM}'.rstrip('Ki')) * 1024
   swap = int('${SWAPCAP}' or 0)
   print('proportional swap limit for a 512Mi request: %.1f MiB' % (req / total * swap / 1024**2))
   print('the same container with requests == limits: 0')
   "
   ```

9. Measure why the scheduler cannot help. The claim on the concept page is that Pods request memory
   and never swap, so look for a swap quantity anywhere in the places the scheduler reads:

   ```sh
   kubectl get node "$NODE" -o jsonpath='{.status.capacity}{"\n"}' | tr ',' '\n' | grep -i swap || echo "no swap in node capacity"
   kubectl get node "$NODE" -o jsonpath='{.status.allocatable}{"\n"}' | tr ',' '\n' | grep -i swap || echo "no swap in allocatable"
   kubectl explain pod.spec.containers.resources.requests | head -12
   kubectl explain node.status.nodeInfo.swap
   ```

10. Read the thing the post never mentions: the kubelet's own swap. `swap-behavior.md:14-15` says
    system daemons `including the kubelet itself!` can use swap whatever the workload setting is,
    and `swap-memory-management.md:288-294` recommends setting `memory.swap.max=0` on the system
    slice because of it. Ask the cgroup, not the documentation:

    ```sh
    cat /sys/fs/cgroup/system.slice/memory.swap.max 2>/dev/null || echo "no limit set on system.slice"
    cat /sys/fs/cgroup/system.slice/kubelet.service/memory.swap.current 2>/dev/null \
      || sudo find /sys/fs/cgroup -maxdepth 3 -name 'memory.swap.current' -path '*kubelet*' 2>/dev/null | head -3
    cat /sys/fs/cgroup/kubepods.slice/memory.swap.max 2>/dev/null || echo "no limit on kubepods.slice"
    cat /proc/sys/vm/min_free_kbytes
    ```

**Expect**

Step 1 finds nothing: no swap key in `/var/lib/kubelet/config.yaml`, `failSwapOn: true` in the
running configuration, `memorySwap: None`, and no `NodeSwap` in `featureGates` — because at v1.34
the gate went `stable` and `locked`, so there is no gate left to set. `swapon --show` prints nothing
and `free -h` shows a zero swap row. That is the starting state the post assumes you are *not* in:
it is written for someone who already has swap provisioned.

Step 2 is the measurement the census row asks for, and the kubelet should refuse to start. Expect
`systemctl is-active kubelet` to print something other than `active`, and the journal to name the
field — the wording varies by release, and what matters is that the failure is configuration
validation rather than anything to do with swap: there is no swap on this node yet, and the kubelet
never gets far enough to care. If your release instead starts and logs a complaint, record that
instead; either way, write down the exact text, because it is the only artifact in this sweep where
a post's own example is rejected by the thing it configures. Note also what you did *not* have to
do: you never set a feature gate. The post's first instruction is now unnecessary, and the second
one is what is failing.

Step 3 starts cleanly. `is-active` prints `active`, and `configz` now shows `{'swapBehavior':
'LimitedSwap'}`. One word separated a kubelet that would not start from a kubelet that does, and the
word that works is the one the post presented as the default while the one that fails was its
alternative.

Step 4 refuses, and this time it is swap the kubelet is objecting to. With 1GiB of swap active and
`failSwapOn` still at its default of `true`, the kubelet exits and the journal says so — exactly the
behaviour the post describes at `:16-17` as `Kubernetes' earlier design`. Five years and one stable
feature later, this is unchanged; `kubelet-config.v1beta1.md:1385` still says `Default: true`.
Everything about swap is opt-in at the node, which is the reason the post's whole `## How do I use
it?` section still has the right shape even though three of its four instructions have decayed.

Step 5 succeeds, and the node reports a field that did not exist when the post was written:
`{"capacity":1073741824}`, one GiB in bytes. The `go-template` is the one from
`swap-memory-management.md:139` and it prints your node name and the capacity; a node without swap
prints `<unknown>`, which the note at `:151-153` explains. The post asked for `a set of metrics for
node QoS`; the project answered with an API field on every Node object as well.

Step 6 prints the series. Expect `node_swap_usage_bytes` and, once anything is running,
`container_swap_usage_bytes` and `container_swap_limit_bytes` from `/metrics/resource`, and a `swap`
object in the `/stats/summary` node section. Most usage figures will be `0`: `LimitedSwap` forbids
swap to `BestEffort` and `Guaranteed` Pods and to high-priority Pods, and on a fresh single-node
cluster nearly everything running is one of those. A limit that is set and a usage that is zero is
the correct reading, not a failure. `kubectl top nodes --show-swap` will fail on this cluster unless
you have installed metrics-server — the `--show-swap` flag exists, the Metrics API behind it does
not, and that distinction is the [resource-monitoring
exercise](../2015/02-resource-usage-monitoring-kubernetes.md)'s subject.

Step 7 prints `cgroup2fs`, which puts your node on the second row of the post's table — the row that
says Kubernetes workloads cannot use swap. They can, and step 8's arithmetic is how much. The
`configz` read shows `failCgroupV1` as `true` or absent — absent still means `true`, which is the
documented default — and the journal count for `cgroup v1` should be zero. To be on the post's
*first* row at the pin you would have to boot a kernel into cgroup v1 and then set `failCgroupV1:
false` to get the kubelet to start at all, on a node whose cgroup version the project deprecated at
v1.35.

Step 8 gives a number around 128 MiB for a 512Mi request on a 4096MB node with 1GiB of swap, less
whatever the kubelet holds back as unavailable to Pods. The point is not the figure, it is the
shape: the limit is a fraction of node memory applied to node swap, so the same manifest gets a
different swap limit on every differently-sized node, and no manifest anywhere states it. Then read
the second line: the opt-out at `:383-385` means a Burstable Pod becomes swap-free by making its
requests equal its limits, which is also the change that makes it `Guaranteed`. Swap eligibility is
a side effect of QoS class, and QoS class is a side effect of how you wrote requests and limits.

Step 9 finds no swap quantity in either `capacity` or `allocatable`, and `kubectl explain
pod.spec.containers.resources.requests` describes a map of compute resources with no swap among
them. `kubectl explain node.status.nodeInfo.swap` does resolve — the reporting field from step 5 —
which is the whole asymmetry in two commands: the node can tell you how much swap it has, and
nothing in the scheduling path can ask for any of it. That is `swap-memory-management.md`'s `Pods do
not request swap space; they just request memory` (`:329-330`), and it is why the page's advice is
to taint instead.

Step 10 is the post's blind spot. `system.slice/memory.swap.max` is normally `max` — no limit — so
the kubelet, containerd and systemd may all swap freely, on a node whose Pods mostly may not.
`kubepods.slice/memory.swap.max` is where the workload ceiling lives. Read those two numbers
together and the default posture is the inverse of what an operator reading the post would assume:
`NoSwap` protects the workloads from swap and leaves the control plane exposed to it, and the
documentation's own recommendation (`:288-294`) is to go and set `memory.swap.max=0` on the system
slice by hand. `min_free_kbytes` is the number the eviction-threshold advice at `:257-262` is
measured against; write it down, because a swap-enabled node whose eviction threshold sits above it
will evict Pods rather than let them swap, and that is the failure mode the post's caveats do not
cover.

**Read on**

1. `concepts/cluster-administration/swap-memory-management.md:238-262` is the caveat the post does
   not have, and the one most likely to bite: with swap enabled, an eviction threshold set the usual
   way — a little below node memory capacity — can mean `workloads never being able to swap out
   during node memory pressure`, while one set too high hands the node to the OOM killer. The advice
   is to sit just under `vm.min_free_kbytes`, which you read in step 10.

2. `swap-memory-management.md:208-236` is the risk nothing in the post hints at. Memory-backed
   volumes — `secret` mounts and `emptyDir` with `medium: Memory` — are `tmpfs`, and `tmpfs` pages
   can be swapped to disk, so the kubelet mounts them with the `noswap` option and falls back to a
   warning when the kernel is too old to support it. The version floor is Linux 6.3, recorded in
   `reference/node/kernel-version-requirements.md`, and the detection is a dummy mount at startup.

3. `reference/node/swap-behavior.md` is 22 lines long and is the whole of the reference: two
   behaviours, one parenthesised default, one sentence about what the kubelet itself may still do.
   Read it next to the post's `:71-87` and count what the pin needed to say to replace seventeen
   lines of blog with eight lines of reference — then read `swap-memory-management.md:286-346` for
   the practices that have no home in either.

4. Three pieces of this exercise's machinery are walked elsewhere. [The
   dynamic-kubelet-configuration exercise](../2018/05-dynamic-kubelet-configuration.md) is kubelet
   configuration as a subject in itself, including the drop-in directory that is the modern way to
   make the edits step 2 makes by hand. [The PID-limiting exercise](../2019/05-pid-limiting.md)
   reads a `locked` stable stage and explains why `locked` is the key that matters. [The
   resource-monitoring exercise](../2015/02-resource-usage-monitoring-kubernetes.md) is the Metrics
   API path that `kubectl top --show-swap` needs and this cluster does not have.

5. Unanswerable from the pin: the schedule. The post commits to beta in v1.23 and the gate file
   records beta at v1.28, but nothing in the tree says what happened in between, and the gate file
   carries no history beyond its four stage rows. The same goes for the `node-wide swap limit for
   workloads` — the pin records that no such setting exists, not that it was ever designed. The one
   question of this kind the pin *does* answer is why `UnlimitedSwap` went away, and it answers it
   in the blog archive rather than the documentation: a 2025 post says the behaviour was removed
   because it `might compromise the node's health`. Note where that leaves a reader who only has the
   documentation — `UnlimitedSwap` is not deprecated there, or removed there, it simply never
   existed.

**Teardown**

This exercise changed the node's configuration and added a swap file, so the teardown is longer than
usual and the order matters — restore the kubelet first, then take the swap away:

```bash
sudo mv /var/lib/kubelet/config.yaml.bak /var/lib/kubelet/config.yaml
sudo systemctl restart kubelet; sleep 15
systemctl is-active kubelet
sudo grep -c -i swap /var/lib/kubelet/config.yaml || echo "0 swap keys, as it started"
sudo swapoff /swapfile && sudo rm -f /swapfile
swapon --show || echo "no swap devices"
kubectl get node -o jsonpath='{.items[0].status.nodeInfo.swap}{"\n"}'
kubectl get nodes
```

The last two commands are the check that matters. With the swap file gone and the kubelet restarted,
`status.nodeInfo.swap` goes back to empty and the node returns to `Ready` with `failSwapOn` at its
default — which also means the node is back in the state the post assumes nobody is in. Nothing was
ever added to the API and no workload ran, so a `kubectl get nodes` that prints one `Ready` node is
a complete teardown. Leave the guest up for the next exercise in this year.
