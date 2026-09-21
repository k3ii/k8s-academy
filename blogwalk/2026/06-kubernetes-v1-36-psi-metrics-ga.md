<a id="kubernetes-v1-36-psi-metrics-ga"></a>

# The page that teaches you to read the number disagrees with itself by a factor of ten, the JSON sample it disagrees inside is not JSON and is printed byte for byte in two files, the schema link beside it points at a page the pin does not contain, and four cores can check the graphs

**Post** — [Kubernetes v1.36: PSI Metrics for Kubernetes Graduates to GA](https://kubernetes.io/blog/2026/05/12/kubernetes-v1-36-psi-metrics-ga/),
2026-05-12.

92 lines, 9,469 bytes, one author — Maria Fernanda Romano Silva, Google Cloud — one fenced block,
four figures and no tables. The thirty-seventh of 2026's fifty-nine published rows and the sixth
`walk` among them. It is the only walk of the year whose central claim is a performance measurement,
and the only evidence it offers for that claim is four line graphs.

**As written**

The opening is two paragraphs. `:9-12` dates Pressure Stall Information to its 2018 implementation
in the Linux kernel and says it provides *the high-fidelity signals needed to identify resource
saturation before it becomes an outage*; unlike utilisation metrics, PSI *tells the story of tasks
stalled and time lost, all in nicely-packaged percentages of time across the CPU, memory, and I/O*.
`:14` announces the graduation in v1.36 — *a stable, reliable interface to observe resource
contention at the node, pod, and container levels* — and promises a dive into *the improvements and
performance testing that proved its readiness for production*.

`:16-20` is the case for the metric. `:18` says monitoring CPU or memory usage alone can mislead,
because *a node may report XX% (below 100%) CPU utilization while certain tasks are experiencing
severe latency due to scheduling delays*. The two bullets at `:19-20` are what PSI adds: *Cumulative
Totals*, the absolute time spent stalled, and *Moving Averages* over 10s, 60s and 300s windows,
which let an operator *distinguish between transient spikes and sustained resource tension*.

`:22-28` sets up the testing. The concern named at `:24` is the resource overhead of collecting and
serving the metrics, and the answer is *extensive performance validation on high-density workloads
(80+ pods) across various machine types* run by SIG Node. `:26-28` splits it in two: scenario 1
holds kernel PSI on and toggles the kubelet feature, isolating the kubelet's cost; scenario 2 holds
the kubelet feature on and toggles kernel PSI, isolating the kernel's.

Scenario 1 is `:30-37`. `:31` reports four-core machines with the kernel already tracking pressure
by default (`psi=1`), the `KubeletPSI` gate toggled, *synchronized bursts* that are *practically
identical in both magnitude and frequency*, and a conclusion: the collection logic is lightweight,
stays *within the normal 0.1 cores or 2.5% of the total node capacity*, and is safe for production.
The figure at `:33` is titled *(Case 1) Kubelet CPU Usage Rate Comparison* and captioned *Figure 2*.
`:35` turns to system CPU in the same run, says the enabled line follows the same pattern as the
disabled one *with a slight expected increase from the baseline*, and concludes that once the OS is
tracking PSI, *at around 2.5 cores*, the act of reading those cgroup metrics is *negligible to
performance*. The figure at `:37` is titled *(Case 1) System CPU Usage Rate Comparison* and
captioned *Figure 1*.

Scenario 2 is `:39-46`, also on a four-core machine. `:40` compares a cluster booted `psi=1`
(described as the COS default) against one booted `psi=0` at 80-pod density under heavy I/O and CPU
load, and gives the system CPU delta as *consistently between 0.037 cores and 0.125 cores or 0.925%
- 3.125% of the total node capacity*, with *a single spike to 0.225 cores, or 5.6%*, brought back
down within seconds. The figure at `:42` is *Figure 3*. `:44` zooms in on the kubelet process, which
*serves as the primary collector for these metrics*, and reports that its usage never exceeds *0.25
cores or 6.25% of total capacity* for longer than a second; the figure at `:46` is *Figure 4*.

`:48-50` is the section titled *Improvements between beta (1.34) and stable (1.36)*, and it holds
one bullet. Previously, if the feature was on in Kubernetes but the kernel did not support PSI
(`psi=0`), the kubelet *would emit misleading zero-valued metrics*, which *could trigger false
alarms when read as real metrics instead of missing values*. In v1.36 the kubelet *detects OS-level
PSI support via cgroup configurations before reporting*, so pressure metrics are only collected and
emitted where they are supported.

`:52-70` is Getting started. Two requirements at `:56-57`: a Linux kernel 4.20 or later on cgroup
v2, and PSI enabled at the OS level, meaning `CONFIG_PSI=y` and no `psi=0` on the kernel command
line. `:59` says that as of v1.36 the metrics are generally available and *you do not need to opt in
to any feature gate*. `:61` tells you to scrape `/metrics/cadvisor` with a Prometheus-compatible
monitoring solution or query the Summary API, and notes that Windows nodes simply omit the metrics.
`:63` offers the API server's kubelet proxy as a way to see real-time pressure data, `:65` cautions
that proxying to the kubelet is a privileged operation, and `:67-70` is the post's only fenced
block: a `kubectl get --raw .../proxy/stats/summary` piped into a `jq` filter that selects one
container by name and prints `{name, cpu: .cpu.psi, memory: .memory.psi, io: .io.psi}`.

The tail is `:72-91`. Further reading at `:74-77` names the kernel's own PSI documentation, the
*Understanding PSI* page in the Kubernetes documentation, and cAdvisor's `prometheus.go`. `:81`
thanks SIG Node and dates the journey *from alpha in v1.33, through beta in v1.34, to GA in v1.36*.
`:83-91` is two sets of contact details for the same group.

**As it runs now**

**The page the post sends you to for the interpretation disagrees with itself by a factor of ten.**
`docs/reference/instrumentation/understand-psi-metrics.md` is the *Understanding PSI* page named at
`:76`. Its `:40` states the rule: the `avg` values *represent the percentage of wall-clock time that
tasks were stalled* over 10-second, 60-second and 5-minute moving averages. Its `:95` applies the
rule to a worked number: a `cpu.some` `avg10` of `0.74` means a task was stalled *for 0.74% of the
time (0.0074 seconds or 74 milliseconds)*. Nought point seven four per cent of ten seconds is 0.074
seconds, which is 74 milliseconds. The two figures inside one parenthesis are ten times apart, and
only the second of them follows from the rule the same page gives five paragraphs earlier. Step 7
settles it against the counter that is not a percentage.

**The sample it says that about is not JSON, and the identical bytes are printed in a second file.**
The block at `understand-psi-metrics.md:46-93` carries six trailing commas and eleven closing braces
against ten opening ones, so `python3 -m json.tool` refuses it at the fifteenth line and, once the
commas are removed, refuses it again at the thirty-first, where the extra brace ends the object and
leaves the `io` section outside it. The page introduces the block at `:42-44` as what a `jq` filter
returns, and `jq` does not emit a trailing comma. The same block appears at
`docs/concepts/cluster-administration/system-metrics.md:210-257`, byte for byte, and the three
paragraphs of interpretation under it are byte-identical too, except that the second page adds one
sentence about Prometheus rate calculations. Two pages, one broken sample, and it is the only sample
of this API's PSI output in the tree.

**The schema those samples are samples of is a link to a page the pin does not contain.**
`understand-psi-metrics.md:19` calls the Summary API *the kubelet's Summary API* and links
`/docs/reference/config-api/kubelet-stats.v1alpha1/`. No file under `content/en` renders that path:
`docs/reference/config-api/` holds twenty-three files at the pin and none of them is the kubelet's
stats API. The same dead link occurs four times across three files —
`docs/reference/instrumentation/node-metrics.md:13` and `:53`,
`docs/reference/instrumentation/cri-pod-container-metrics.md:55`, and the PSI page. So the JSON
block that does not parse is not a convenience beside the schema. It is the schema.

**A placeholder made it into the argument.** Back in the post, `:18` reads *a node may report XX%
(below 100%) CPU utilization while certain tasks are experiencing severe latency due to scheduling
delays*. That sentence is the case for the whole feature, and its one number is the one nobody
filled in.

**Figure 2 is printed above Figure 1.** The figure at `:33` carries `caption="Figure 2: Kubelet CPU
Usage Rate Comparison"` and the figure at `:37` carries `caption="Figure 1: Node System CPU Usage
Rate Comparison"`, while the prose at `:35` introduces the second of them as *the following graph*.
Both are titled *(Case 1)* although the heading above them at `:30` says *Scenario 1*, and the same
mismatch holds for `:39` and the two *(Case 2)* figures below it. All four image files exist in the
pinned tree under `static/images`, so the figures render; it is their numbering that does not
survive being read in order.

**Every percentage in the post divides by four cores, and the one number given without a percentage
is the one where that arithmetic would look strange.** `0.1` cores is `2.5%`, `0.037` is `0.925%`,
`0.125` is `3.125%`, `0.225` is `5.6%` and `0.25` is `6.25%` — five conversions, all of them correct
for a four-core machine, which is the machine `:31` and `:40` both name. The exception is `:35`,
where system CPU is *at around 2.5 cores* and no percentage follows. On the same four cores that is
62.5%. The sentence is almost certainly describing the level both clusters sat at rather than the
cost of the feature, but it is the one place the post asks you to supply the reading, and it sits in
the paragraph that concludes the collection is negligible.

**The improvement the GA release is named for cannot be observed on a release that has it.** `:50`
says the kubelet used to emit zero-valued metrics on a node whose kernel had PSI off, and now
detects OS support before reporting. From v1.36 the gate is locked on and the detection is
unconditional, so the behaviour the bullet describes is unreachable from the release that describes
it. v1.35 is the last release that can show you the zeros, and the kernel gives a narrower lever
than a boot parameter: `cgroup.pressure`, one file per cgroup, which turns accounting off for a
subtree without rebooting anything. Step 8 uses it on one Pod.

**Getting started is the beta announcement's Getting started with the gate step taken out.** The
beta post of 2025-09-04 carries a two-item list at its `:55-56` whose second item is *Enable the
`KubeletPSI` feature gate on the kubelet*; this post's list at `:56-57` keeps the first item word
for word and replaces the second with the OS-level requirement. The paragraph under it is the same
paragraph: this post's `:61` is the beta post's `:58` with *Once enabled* changed to *Once the OS
prerequisites are met* and the closing clause about Windows nodes reworded. The beta announcement is
a `read` row in [2025's census](../2025/README.md), which is why it has no exercise of its own and
why this one carries the comparison.

**Three releases end to end, and the middle one is named nowhere.** The post's `:81` dates the
journey alpha v1.33, beta v1.34, GA v1.36, and the heading at `:48` calls the gap *Improvements
between beta (1.34) and stable (1.36)*. The gate file
`command-line-tools-reference/feature-gates/KubeletPSI.md` records beta as running 1.34 to 1.35, so
beta lasted two releases and not one. v1.35 is the release the clusters in this lab run, and the
post's account of the feature skips straight over it.

**This gate really is locked, and the file says so.** `KubeletPSI.md` carries `locked: true` on its
stable stage, and two prose pages agree in the same words: *Starting with Kubernetes v.1.36, the
`KubeletPSI` feature gate is locked to true and cannot be disabled* (`understand-psi-metrics.md:16`
and `node-metrics.md:54`). That is worth saying plainly because the other v1.36 kubelet post of this
year, published eighteen days earlier, makes the identical claim about a gate whose file carries no
such key — [the fine-grained kubelet authorization
row](05-kubernetes-v1-36-fine-grained-kubelet-authorization-ga.md) counts how many files do. The
post at `:59` puts it the other way round and is also right: there is nothing left to opt into.

**The two sentences that say so carry the same typo, and a third page carries another.** Both write
*v.1.36* with a full stop after the `v`, in a tree where the convention is `v1.36`;
`system-metrics.md:265` offers *realitime* in a sentence that appears nowhere else. The three PSI
passages — `node-metrics.md:46-64`, `understand-psi-metrics.md:11-29` and
`system-metrics.md:178-265` — each open with the same `feature-state` shortcode for the same gate,
each carry a Requirements list of the same two or four bullets, and two of them close with the same
whatsnext sentence, word for word, down to *a metrics pipeline that rely on these data*.

**The endpoint the post tells you to scrape is the one the pin has begun to deprecate.** Its `:61`
and `:76` both send a reader to `/metrics/cadvisor`, and [the 2016 node dashboard
row](../2016/12-visualize-kubelet-performance-with-node-dashboard.md) reads the pinned notice that
cAdvisor-based pod and container metrics collection in the kubelet is deprecated as of v1.37, to be
served instead from the CRI runtime under the same endpoint path and the same metric names. Nothing
in the tree says whether a CRI runtime supplies `container_pressure_*`. The six names are written in
exactly two files, `system-metrics.md:190-195` and the beta announcement's own list, and neither of
those is `docs/reference/instrumentation/metrics.md`, which is where the pin keeps the metrics
reference and which does not contain the string `container_pressure` at all.

**The examples that generate the pressure pin an image three tags behind the newest the same tree
names.** `understand-psi-metrics.md:120`, `:178` and `:232` all run
`registry.k8s.io/e2e-test-images/agnhost:2.47`. Four tags of that image appear under
`content/en/docs` — 2.40, 2.45, 2.47 and 2.53 — and the newest of them is used once, in
`concepts/workloads/pods/advanced-pod-config.md:113`. The PSI page also states at its `:104` that
the image *includes the `stress` tool* and then passes `stress` as the container's first argument,
which is not how a tool inside an image is usually invoked and is not written down anywhere else in
the tree. That Pod is applied exactly as printed in step 3, and what happens to it is the finding.

**The one command the requirements give you for checking the kernel needs a kernel option the same
page never mentions.** `understand-psi-metrics.md:27` and
`docs/reference/node/kernel-version-requirements.md:68` both say to run `zgrep CONFIG_PSI
/proc/config.gz`. That file exists only where the kernel was built with its configuration embedded
and the module that exposes it is loaded, which is a second requirement, unstated, and a different
one from `CONFIG_PSI`. Step 1 runs the documented check and the one that works on the node beside
it.

**What this exercise does not cover, and where it lives.** cAdvisor, the Summary API,
`metrics-server` and the four endpoints the kubelet serves are [the 2015 resource usage
row](../2015/02-resource-usage-monitoring-kubernetes.md), and the deprecation of cAdvisor-based
collection, the gate that decides which collector answers on `/metrics/cadvisor`, and the metric
that tells you which one did are [the 2016 node dashboard
row](../2016/12-visualize-kubelet-performance-with-node-dashboard.md). cgroup v2 as a requirement,
and the kernel-floor page this post's requirements are drawn from, are [the 2024 cgroup v1
maintenance row](../2024/05-cgroup-v1-maintenance-mode.md), which already reads the sentence at
`understand-psi-metrics.md:29`. Turning a kubelet feature gate off on a v1.35 node, and the count of
gate files that carry a lock, belong to [the fine-grained kubelet authorization
row](05-kubernetes-v1-36-fine-grained-kubelet-authorization-ga.md); step 9 reuses the mechanics and
does not re-derive them. Nothing here reproduces the post's graphs: four line charts over an 80-pod,
4-core load test are not a thing one afternoon on one node can redraw, and step 9 measures a single
number in the same units instead.

**The diff, and why**

**Wrong when it was published.** The sentence the reader needs most is off by ten. A `cpu.some`
`avg10` of 0.74 is 74 milliseconds of stall in the trailing ten seconds, not 7.4, and the page the
post names for interpretation prints both numbers inside one pair of brackets. Beside it sits a
sample of the API output that no JSON parser accepts, and beside that a link to the schema that
resolves to nothing in the pinned tree. In the post itself, the motivating figure is still `XX%`,
the two figures of Scenario 1 are captioned in the reverse of the order they appear, and the Getting
started section is the beta announcement's with its second step swapped out. None of this waited on
a later release to go wrong.

**Still right.** The measurement stands up. Every percentage the post quotes is the quoted core
count divided by four, and four is the core count its own methodology section gives, so the
arithmetic is internally consistent and the overhead it reports is small enough that a reader is
right to stop worrying about it. The metric names are correct, the endpoint it names does serve them
at the pin, the some-versus-full distinction is the kernel's own, and the claim that Windows nodes
simply omit the series is repeated in three places with nothing anywhere contradicting it. The lock
it asserts is in the gate file this time. Step 9 reproduces the shape of the finding on one node
rather than eighty pods across a fleet, and the expectation is that it agrees.

**Overtaken by stasis.** The improvement the release is proudest of is unobservable from the release
that ships it. A gate locked on at v1.36 cannot be turned off to show you the zero-valued metrics it
stopped emitting, and no page in the pin tells a reader how else to get a node into that state; the
kernel's own `cgroup.pressure` switch, which does it per cgroup and without a reboot, is not written
down anywhere under `content/en`. Meanwhile the endpoint all four pages send you to is the one the
pin has already announced will stop being served by the collector that fills it, one release later.
The documentation for this feature was finished at the moment it became hardest to demonstrate.

**Never absorbed.** Four pages tell this story and none of them is the reference. The six Prometheus
series are written in `system-metrics.md` and in a blog post, and `container_pressure` does not
occur in `docs/reference/instrumentation/metrics.md` at all, which is where the tree keeps the list
of what the components expose. The GA graduation added a stable stage to a gate file that is never
rendered, and the same two sentences with the same `v.1.36` typo to two prose pages. What a reader
coming to PSI cold actually finds is one page repeated three times, a sample that does not parse,
and a dead schema link in four places.

**The ladder**

`KubeletPSI`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.33 |
| beta | `true` | — | v1.34 – v1.35 |
| stable | `true` | `true` | v1.36 – |

Three releases end to end. That is short: the pin's gate files record twenty-one releases for the
longest ladder in the tree, and this one is done in three. The shortness constrains the lab in one
specific way. The clusters run v1.35, the last release in which the gate is settable, so step 9 can
measure the kubelet with PSI collection on and with it off and subtract. From v1.36 the stable row
is the only row and it carries the lock, so that subtraction is not repeatable on a newer cluster —
which is also, exactly, why the post's own Scenario 1 could be run before the feature graduated and
not after.

The `locked` column is filled in here, and it is worth being precise about what fills it: the key is
in the gate file's stable stage, the file is marked `render: false` so nothing on the site displays
it, and two prose pages assert the lock in their own words. That is three sources agreeing, which is
three more than the other v1.36 kubelet feature of this year has.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180`, 4096MB, 4
CPUs, 25G, [provisioned](../../strands/lab-topologies.md#provision) and
[baselined](../../strands/lab-topologies.md#node-baseline-steps) as usual, running Kubernetes v1.35.
The core count is not incidental: the post's machines have four cores, every percentage it prints is
a core figure divided by four, and a node with the same four cores is what lets step 9 quote its
result in the post's units and compare. One node is also the only honest topology here, because
pressure is a property of one kernel's cgroups and adding a second machine would only give you a
second, unrelated set of numbers. Everything created lives in a namespace called `bw-psi`, except
one appended block in the kubelet's configuration file and one write to a cgroup control file, which
*Teardown* undoes. Steps 1 to 9 run on the node over `ssh zain@10.10.10.180`; step 10 runs offline
against a checkout of `kubernetes/website` at the pin, with `W` set to its `content/en` directory.

**Do**

1. Establish that the kernel underneath is one that can answer at all, using the check the
   documentation gives and the check that works. Open one session with `ssh zain@10.10.10.180` and
   stay in it; every fence up to step 10 is written as though you are already there. Write down the
   three `total` figures from `/proc/pressure` — step 7 comes back for them.

   ```sh
   kubectl version -o json | grep gitVersion
   N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}'); echo "node $N"
   nproc; uname -r
   zgrep CONFIG_PSI /proc/config.gz || echo "no /proc/config.gz on this node"
   grep -E '^CONFIG_PSI' /boot/config-$(uname -r)
   grep -w psi /proc/cmdline || echo "no psi= parameter on the kernel command line"
   stat -f -c %T /sys/fs/cgroup
   for r in cpu memory io; do echo "== $r"; cat /proc/pressure/$r; done
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" \
     | grep 'kubernetes_feature_enabled.*KubeletPSI'
   kubectl create namespace bw-psi
   ```

2. Read the same numbers one layer down, where the kubelet reads them, before any workload of yours
   exists. The per-cgroup files carry the same four fields as the per-node ones and one extra
   control file that step 8 uses.

   ```sh
   C=/sys/fs/cgroup/kubepods.slice
   ls -1 $C | head -20
   for r in cpu memory io; do echo "== $r"; cat $C/$r.pressure; done
   cat $C/cgroup.pressure
   grep -c . /proc/pressure/cpu
   ```

3. Apply the Pod the documentation itself prints for generating CPU pressure, exactly as written,
   and find out whether the argument it passes is a thing. The image tag is the one the page pins,
   three tags behind the newest the same tree names elsewhere.

   ```sh
   cat <<'EOF' | kubectl -n bw-psi apply -f -
   apiVersion: v1
   kind: Pod
   metadata:
     name: cpu-pressure-pod
   spec:
     restartPolicy: Never
     containers:
     - name: cpu-stress
       image: registry.k8s.io/e2e-test-images/agnhost:2.47
       args:
       - "stress"
       - "--cpus"
       - "1"
       resources:
         limits:
           cpu: "500m"
         requests:
           cpu: "500m"
   EOF
   sleep 20
   kubectl -n bw-psi get pod cpu-pressure-pod -o wide
   kubectl -n bw-psi logs cpu-pressure-pod --tail=20 || true
   kubectl -n bw-psi get pod cpu-pressure-pod \
     -o jsonpath='{.status.containerStatuses[0].state}{"\n"}'
   ```

4. Generate the pressure with an image whose arguments are not in question, and watch the number
   move. One container throttled to a quarter of a core, four busy loops inside it: the stall is
   manufactured by the cgroup limit, not by the machine being busy.

   ```sh
   kubectl -n bw-psi delete pod cpu-pressure-pod --ignore-not-found --wait=true
   cat <<'EOF' | kubectl -n bw-psi apply -f -
   apiVersion: v1
   kind: Pod
   metadata:
     name: bw-psi-load
   spec:
     containers:
     - name: burn
       image: busybox:1.36
       command: ["sh","-c","for i in 1 2 3 4; do while :; do :; done & done; sleep 3600"]
       resources:
         limits:
           cpu: "250m"
   EOF
   kubectl -n bw-psi wait --for=condition=Ready pod/bw-psi-load --timeout=60s
   U=$(kubectl -n bw-psi get pod bw-psi-load -o jsonpath='{.metadata.uid}')
   D=$(find /sys/fs/cgroup/kubepods.slice -type d | grep -E "$U|${U//-/_}" | head -1); echo "$D"
   for i in 1 2 3; do cat $D/cpu.pressure; sleep 10; done
   ```

5. Run the one-liner the post sends you to, against the container you just made stall, and ask a
   parser what it thinks of the result. The filter is the page's; the validation is not.

   ```sh
   N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw "/api/v1/nodes/$N/proxy/stats/summary" > /tmp/bw-summary.json
   jq empty /tmp/bw-summary.json && echo "summary parses"
   jq '.pods[] | select(.podRef.name=="bw-psi-load") | .containers[].cpu' /tmp/bw-summary.json
   jq '.pods[] | select(.podRef.name=="bw-psi-load")
       | {name: .podRef.name, cpu: .cpu.psi, memory: .memory.psi, io: .io.psi}' /tmp/bw-summary.json
   jq '[paths | select(.[-1]=="psi")] | length' /tmp/bw-summary.json
   ```

6. Ask the Prometheus endpoint for the same thing under its other set of names, and ask the kubelet
   which collector answered. Six series names are what the pin writes down; count what the node
   serves.

   ```sh
   N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics/cadvisor" > /tmp/bw-cadvisor.txt
   grep -c '^container_pressure' /tmp/bw-cadvisor.txt
   grep '^# TYPE container_pressure' /tmp/bw-cadvisor.txt
   grep '^container_pressure_cpu_stalled_seconds_total' /tmp/bw-cadvisor.txt \
     | grep 'pod="bw-psi-load"'
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" | grep -E '^kubelet_metrics_provider' || \
     echo "no kubelet_metrics_provider series on this release"
   grep -o 'container_pressure_[a-z_]*' /tmp/bw-cadvisor.txt | sort -u
   ```

7. Settle the factor of ten. `avg10` is a percentage of the trailing ten seconds and `total` is a
   monotonic microsecond counter of the same stall, so the difference in `total` across exactly ten
   seconds, divided by ten seconds, is the same quantity computed two ways. Read them off the same
   file in the same breath and do the arithmetic.

   ```sh
   U=$(kubectl -n bw-psi get pod bw-psi-load -o jsonpath='{.metadata.uid}')
   D=$(find /sys/fs/cgroup/kubepods.slice -type d | grep -E "$U|${U//-/_}" | head -1)
   psi() { tr '=' ' ' < $D/cpu.pressure | awk 'NR==1{print $3, $9}'; }
   set -- $(psi); A0=$1; T0=$2
   sleep 10
   set -- $(psi); A1=$1; T1=$2
   echo "avg10 now: $A1 %   delta total: $((T1-T0)) us over 10 s"
   awk -v d=$((T1-T0)) 'BEGIN{printf "that is %.4f s stalled, or %.2f%% of 10 s\n", d/1e6, d/1e5}'
   awk -v a=$A1 'BEGIN{printf "%.2f%% of 10 s is %.4f s = %.1f ms\n", a, a/100*10, a/100*10000}'
   awk 'BEGIN{printf "the page: 0.74%% of 10 s is %.4f s = %.1f ms\n", 0.0074*10, 0.0074*10000}'
   ```

8. Reproduce the state the GA release stopped emitting misleading numbers for, on a release that
   still can. Turning accounting off for one cgroup is the narrow version of booting with `psi=0`:
   the files stay, the numbers stop.

   ```sh
   U=$(kubectl -n bw-psi get pod bw-psi-load -o jsonpath='{.metadata.uid}')
   D=$(find /sys/fs/cgroup/kubepods.slice -type d | grep -E "$U|${U//-/_}" | head -1)
   cat $D/cpu.pressure
   echo 0 | sudo tee $D/cgroup.pressure
   sleep 15
   cat $D/cpu.pressure
   N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw "/api/v1/nodes/$N/proxy/stats/summary" \
     | jq '.pods[] | select(.podRef.name=="bw-psi-load") | .cpu.psi'
   echo 1 | sudo tee $D/cgroup.pressure
   ```

9. Measure what the post measured, in the post's units. Eighty pods is the load its Scenario 1 used;
   the kubelet's own CPU counter is the overhead. Run it with collection on, turn the gate off, run
   it again, and divide by four cores to get a percentage.

   ```sh
   N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl -n bw-psi create deployment bw-psi-fill --image=registry.k8s.io/pause:3.10 --replicas=80
   kubectl -n bw-psi rollout status deployment/bw-psi-fill --timeout=300s
   K() { kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" \
     | awk '/^process_cpu_seconds_total/{print $2}'; }
   A=$(K); sleep 120; B=$(K)
   awk -v a=$A -v b=$B 'BEGIN{printf "gate on:  %.4f cores, %.2f%% of 4\n",(b-a)/120,(b-a)/120/4*100}'
   sudo cp /var/lib/kubelet/config.yaml /var/lib/kubelet/config.yaml.bw
   printf 'featureGates:\n  KubeletPSI: false\n' | sudo tee -a /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet; sleep 60
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics/cadvisor" | grep -c '^container_pressure' || true
   A=$(K); sleep 120; B=$(K)
   awk -v a=$A -v b=$B 'BEGIN{printf "gate off: %.4f cores, %.2f%% of 4\n",(b-a)/120,(b-a)/120/4*100}'
   ```

10. Leave the cluster and count the documentation. Run this in a checkout of `kubernetes/website` at
    the pin, with `W` set to `content/en`. Every number the *As it runs now* section claims is here;
    the first command is the one that decides whether the sample a reader is meant to learn from is
    data or prose.

    ```sh
    cd /path/to/kubernetes/website/content/en
    W=$(pwd)
    sed -n '47,92p' $W/docs/reference/instrumentation/understand-psi-metrics.md > /tmp/a.json
    sed -n '211,256p' $W/docs/concepts/cluster-administration/system-metrics.md > /tmp/b.json
    python3 -m json.tool < /tmp/a.json || echo "the sample does not parse"
    python3 -c "import re,json,sys; t=re.sub(r',(\s*[}\]])',r'\1',open('/tmp/a.json').read()); json.loads(t)"
    cmp /tmp/a.json /tmp/b.json && echo "byte identical"
    python3 -c "import re; s=open('/tmp/a.json').read(); print(len(re.findall(r',\s*[}\]]',s)))"
    grep -o '{' /tmp/a.json | wc -l; grep -o '}' /tmp/a.json | wc -l
    grep -rn 'kubelet-stats.v1alpha1' $W --include='*.md' | wc -l
    grep -rln 'v\.1\.36' $W --include='*.md'
    grep -c 'container_pressure' $W/docs/reference/instrumentation/metrics.md
    grep -rho 'agnhost:2\.[0-9]*' $W/docs --include='*.md' | sort | uniq -c
    grep -n 'XX%' $W/blog/_posts/2026/psi-metrics-ga.md
    ```

**Expect**

Step 1 prints `v1.35.x`, four cores and a Debian kernel well past 4.20. The documented check fails:
`/proc/config.gz` does not exist on a stock Debian cloud image, because the kernel is built without
`CONFIG_IKCONFIG_PROC`, which is a different option from the one the command is grepping for and
which the pin never mentions. The `/boot/config-$(uname -r)` line is the one that answers, and it
prints `CONFIG_PSI=y`; `CONFIG_PSI_DEFAULT_DISABLED` will be there too, set to `n`, which is what
makes the absent `psi=` parameter harmless. `stat -f` prints `cgroup2fs`. All three `/proc/pressure`
files answer with a `some` line and, for memory and io, a `full` line; `cpu` has a `full` line as
well on a recent kernel and its values will be zero. The `kubernetes_feature_enabled` series reports
`KubeletPSI` at `1` — it is beta and defaults on at v1.35 — and the node is idle enough that every
`avg` figure is `0.00`.

Step 2 shows the same four fields per cgroup. `cpu.pressure`, `memory.pressure` and `io.pressure`
all exist under `kubepods.slice`, which is the answer to whether the kernel is accounting per cgroup
and not just per node, and `cgroup.pressure` contains `1`. On an idle node the `kubepods.slice`
figures are zero or very close to it. `grep -c .` on the node-level cpu file prints `2` on a kernel
new enough to report `full` for CPU and `1` on an older one; either is fine and nothing downstream
depends on it.

Step 3 is the one prediction here that could go either way, and the prediction is that it fails.
`stress` is not an agnhost subcommand the pin documents anywhere else, and a binary that dispatches
on its first argument normally exits non-zero on an argument it does not know, printing the list it
does know. With `restartPolicy: Never` the Pod does not loop: it goes straight to `Failed`, with
`terminated` and a non-zero exit code in the container state, within a second or two of starting.
The logs are the evidence either way. If instead the container stays up and burns half a core, the
page is right and this exercise is wrong about it — write down which happened, because it is the one
claim in this file that cannot be settled by reading the pin.

Step 4 is where the number first moves. Four spin loops inside a container limited to 250 millicores
means the cgroup is throttled roughly fifteen sixteenths of the time, so `cpu.pressure`'s `some
avg10` climbs within one ten-second window and settles somewhere above 80. The three prints ten
seconds apart should show it rising and then flat. `full` for CPU will be well above zero too,
because every task in the cgroup is stalled at once when the quota is exhausted, which is exactly
what `full` means and is the distinction the pin explains but never demonstrates.

Step 5 produces real output in the shape the broken sample is trying to show. The summary parses —
`jq empty` is silent — and the container's `cpu` object carries a `psi` sibling alongside
`usageNanoCores`. The count of `psi` keys in the document is one per resource per container, plus
one per resource per pod, plus one per resource for the node: on a cluster with a handful of pods it
is a two-digit number, and the point of printing it is that every one of those objects has the
structure the documented sample fails to close a brace on.

Step 6 answers with the Prometheus spelling. The count of `container_pressure` lines is non-zero and
the `# TYPE` lines name the six series the pin writes down — stalled and waiting, for cpu, memory
and io — as counters in seconds rather than the kernel's microseconds, and the sorted list at the
end of the step prints exactly those six and nothing more. The `bw-psi-load` line has a value that
keeps climbing between scrapes. `kubelet_metrics_provider` will almost certainly not be there: it
belongs to the CRI-collection path and this node is on the cAdvisor one, which is the path the
post's instructions assume and the path the pin has announced it is moving off.

Step 7 is the whole question in nine lines. `total` is microseconds and ten seconds is ten million
of them, so the delta expressed as a percentage of ten million is the same quantity `avg10` reports,
and the two will agree to within the sampling jitter — for a cgroup stalling this hard, both land in
the eighties. Follow the same arithmetic down to the page's worked figure: 0.74% of ten seconds is
0.074 seconds, and the last line prints `74.0 ms`. The printed `0.0074 seconds` in the pinned page
is ten times smaller than the `74 milliseconds` it is offered as a restatement of, and the counter
says which one is right.

Step 8 reproduces the zeros. Writing `0` to `cgroup.pressure` stops accounting for that cgroup; the
file stays readable and its `avg` fields decay to `0.00` within the first ten-second window while
the container carries on being throttled exactly as hard as before. `total` freezes rather than
resetting. The Summary API then reports a `psi` object full of zeros for a container that is
stalling constantly — which is precisely the misleading output the v1.36 note says the kubelet
stopped producing, obtained on a release that still produces it, at cgroup granularity instead of
node granularity. Writing `1` back restores accounting and `avg10` climbs again.

Step 9 should land where the post landed. Eighty `pause` pods on four cores is a lot of bookkeeping
and very little work, so the kubelet's own CPU sits in the low hundredths of a core in both runs and
the difference between them is smaller than the noise of a single 120-second sample. Expect
something in the region of 0.03 to 0.06 cores, which is 0.75% to 1.5% of four — the same range the
post's figures fall in — and expect the gate-off run to be lower by an amount you would not bet on.
The `container_pressure` count with the gate off is `0`, which is the one unambiguous confirmation
that the flip took. The kubelet restarts once here and once more in *Teardown*; on a single-node
cluster each restart is a short outage of the only node and nothing else.

Step 10 confirms the documentation findings offline. `json.tool` refuses the sample at line 15
column 5, and with the six trailing commas properly removed the second command still refuses it, at
line 31 column 4, where the extra closing brace ends the object and leaves `io` outside it. The two
extracted blocks are byte identical, so `cmp` is silent; the trailing-comma count prints `6` and the
brace counts `10` and `11`. The dead schema link appears four times. The `v.1.36` grep names two
files. `container_pressure` in the metrics reference counts `0`. The agnhost tally puts `2.47` at
three occurrences, all in the PSI page, against one occurrence of the newer `2.53` elsewhere in the
tree. And `XX%` is still there in the post.

**Read on**

11. [Resource Usage Monitoring in Kubernetes](../2015/02-resource-usage-monitoring-kubernetes.md) —
    cAdvisor, the Summary API and the four endpoints the kubelet serves, which is where
    `/stats/summary` and `/metrics/cadvisor` come from and why they carry different spellings of the
    same data.

12. [Visualize Kubelet Performance with Node
    Dashboard](../2016/12-visualize-kubelet-performance-with-node-dashboard.md) — the deprecation
    that moves pod and container metrics collection from cAdvisor to the CRI runtime, the gate that
    decides which one answers, and the series that tells you which one did.

13. [cgroup v1 maintenance mode](../2024/05-cgroup-v1-maintenance-mode.md) — why cgroup v2 is a
    requirement rather than a preference, and the kernel-floor page this post's requirements list is
    drawn from.

14. [Fine-grained kubelet API
    authorization](05-kubernetes-v1-36-fine-grained-kubelet-authorization-ga.md) — appending a
    `featureGates` block to a kubelet configuration and restarting into it, and the count of gate
    files that carry a lock on their stable stage.

15. Unanswerable from the pin: whether the `container_pressure_*` series survive the move to CRI
    collection. The deprecation notice promises the same endpoint and the same metric names from the
    runtime instead of cAdvisor, and PSI arrives at the kubelet through cAdvisor's cgroup reader. No
    page in the tree says which of the six names a CRI runtime is expected to supply, and no
    runtime's documentation is in reach of the pin to check.

**Teardown**

The namespace takes the two pods and the eighty-replica deployment. The one thing that outlives it
is the appended `featureGates` block in the kubelet's configuration file: step 9 takes the backup
and never puts it back, so the restore below is the only thing that does. Run it even if step 9 was
interrupted, because a node left in that state collects no pressure metrics at all. The last command
is the check that it worked — a non-zero count.

```sh
ssh zain@10.10.10.180 "kubectl delete namespace bw-psi --wait; \
  sudo mv -f /var/lib/kubelet/config.yaml.bw /var/lib/kubelet/config.yaml; \
  sudo systemctl restart kubelet; sleep 30; \
  kubectl get --raw /api/v1/nodes/\$(kubectl get nodes \
    -o jsonpath='{.items[0].metadata.name}')/proxy/metrics/cadvisor \
    | grep -c '^container_pressure'"
```

The `cgroup.pressure` write from step 8 needs no undoing beyond the `1` the step already puts back,
and it disappears with the cgroup when the namespace goes. The node itself is
[destroyed](../../strands/lab-topologies.md#teardown) in the usual way when you are finished with
it.
