<a id="new-cgroup-v1-to-v2-cpu-conversion-formula"></a>

# The curve is built to cross one CPU at exactly the default weight and the post prints 102 instead, the many-to-one band it warns tool authors about is wrong at both ends, and the pinned tree names three cgroup v1 control files and not one of the v2 files that replaced them

**Post** — [New Conversion from cgroup v1 CPU Shares to v2 CPU Weight](https://kubernetes.io/blog/2026/01/30/new-cgroup-v1-to-v2-cpu-conversion-formula/),
2026-01-30.

185 lines, 8,148 bytes, the twelfth of 2026's fifty-nine published rows and the third `walk` among
them. One author, Itamar Holder of Red Hat, writing for SIG Node. It is a page bundle rather than a
single file, because it carries three plotted PNGs, and its front matter sets `math: true` — one of
two posts in the whole 767-row archive that does, the other being 2025's HPA tolerance announcement.
The census gives it no Kubernetes version at all.

**As written**

Kubernetes was designed against cgroup v1, where a container's CPU request became a share count by a
formula the post states at `:18-23`: `cpu.shares = milliCPU × 1024/1000`. The 1024 is cgroup v1's
own default share value and has nothing to do with millicores, which `:25` says in as many words.
`:27-28` works two examples: 1000m gives 1024 shares, 100m gives 102.

cgroup v2 replaced shares with weight, and the two scales do not match. `:30-33` gives the ranges —
shares run 2 to 262144, or two to the first through two to the eighteenth; weight runs 1 to 10000,
or ten to the zeroth through ten to the fourth. `:35-38` names KEP-2254 as the place a conversion
was first defined, and states it: `cpu.weight = (1 + ((cpu.shares - 2) * 9999) / 262142)`. `:40`
describes what that does — it maps the share range onto the weight range linearly — and `:42` plots
it.

Two problems follow, and the post numbers them. The first, at `:51-69`, is priority against
everything outside Kubernetes. In cgroup v1 a container asking for one CPU landed on 1024 shares,
which was also the default, so it competed with system daemons as an equal. Under the linear map
that same container lands on weight 39 against a cgroup v2 default of 100, so it competes at under
forty per cent. The post calls this a de-facto demotion of every Kubernetes workload on the host and
says it bites hardest where many daemons live outside the cluster's scope.

The second, at `:71-92`, is granularity. 100m becomes 102 shares becomes weight 4, and four units is
not enough resolution to subdivide among sub-cgroups inside the container. `:76` and `:90` both
point at KEP #5474, writable cgroups for unprivileged containers, as the reason this is about to
matter more than it did.

The replacement, at `:100-102`, is quadratic in the logarithm: `cpu.weight = ⌈10^(L²/612 + 125L/612
− 7/34)⌉`, where `L = log₂(cpu.shares)`. `:104-107` explains the design directly — the curve was
chosen to cross three points, the minimum pair (2, 1), the default pair (1024, 100), and the maximum
pair (262144, 10000). `:111` and `:115` plot it twice, once whole and once zoomed. `:117-119` calls
it close to linear but carefully placed.

`:121-132` claims the two fixes. One CPU now gets `cpu.weight = 102`, which the post describes as
close to the default of 100; 100m now gets 17, with a Go playground link for the arithmetic.

`:135-143` is the part that decides who sees any of this: the change was made at the OCI layer, not
in Kubernetes, so adoption depends entirely on the runtime. runc carries it from 1.3.2, crun from
1.23. `:145-166` warns the people who will be hurt — tools that predict weights, monitoring that
asserts on them — and adds that reversing weight back to milliCPU is lossy twice over, once in the
integer truncation on the way into shares and once because the shares-to-weight map is many-to-one,
with milliCPU 90 through 109 all landing on weight 17. `:165-166` recommends testing outside
production before upgrading a runtime. `:172-178` offers three places to learn more, the last of
which is the resource management concept page, described as current guidance.

**As it runs now** — it runs, and it runs on the lab node without anybody opting in. What does not
survive contact is the arithmetic. Two of the post's printed numbers are wrong, one of them the
headline result, and the consequence the post never mentions is larger than either.

**The node you would reproduce this on already writes the new numbers.** The baseline procedure pins
its runtime versions at `strands/lab-topologies.md:330`, and the line reads `CD=2.2.1; RUNC=1.5.1`.
runc 1.5.1 is two minor releases past the 1.3.2 the post names at `:142`, so a guest brought up the
usual way has been converting shares to weight the new way since the day it was baselined. There is
no gate to turn on and no version to upgrade to. To see the old behaviour you have to go backwards,
and the exercise does: step 6 drops the node to runc 1.3.1, the patch release immediately before the
change.

**The three design points are exact, and not approximations.** Put `L = log₂(1024) = 10` into the
exponent and every term is a fraction over 612: `100/612 + 1250/612 − 126/612 = 1224/612 = 2`. Ten
squared is one hundred, and the ceiling of an integer is that integer. The same check at the other
two points gives an exponent of 0 at shares 2 and 4 at shares 262144. The curve does not pass near
its three points; it passes through them.

**Which makes the post's headline result disagree with the post's own design.** `:106` lists (1024,
100) as a point the curve crosses. `:22` gives the formula that turns 1000m into 1024 shares and
`:27` states that result in words. `:124` then says a container requesting one CPU will now get
`cpu.weight = 102`, and calls 102 close to the default of 100. It is not close to 100. It is 100.
The fix the post announces is exactly as good as it was designed to be, and the sentence announcing
it understates it by describing an approximation that the formula was built to avoid.

**And 102 is not a rounding artefact, because 102 is already on the page.** It is the share count
for 100m — printed at `:28` in the background section, and again at `:80` in the granularity
example. The number in the claim about the first problem is the number from the second problem's
shares column. Whatever produced it, it was not this formula at this input.

**The true answer is also one bit away from being 101, which is worth knowing before you read the
node's.** Exact arithmetic gives 100. IEEE-754 double arithmetic does not: evaluate `10**(L*L/612 +
125*L/612 - 7/34)` with `L` a float and the result is 99.99999999999994, six parts in ten to the
fifteenth below the integer. The ceiling of that is 100, so the design point survives — but it
survives by rounding down. Had the last bits fallen the other way the ceiling would have returned
101, and the curve's most-quoted point would have missed. Step 9 reads what the node's runc actually
wrote and settles it from the other side.

**The band the post hands tool authors is wrong at both ends.** `:160-161` warns that the
shares-to-weight map is many-to-one and gives the example: milliCPU 90 through 109 all map to
`cpu.weight = 17`. Run the post's own two formulas across that range and the bands are 85m to 92m on
weight 16, 93m to 100m on weight 17, 101m to 108m on weight 18, and 109m to 116m on weight 19. The
warning is right and the numbers under it are not, at the low end by three and at the high end by
nine: twelve of the twenty values the post names land on a different weight. Step 8 submits the
whole range to the node and reads the answer off the cgroup tree.

**The granularity claim underneath that band is right, and by more than the post says.** The old
linear map compressed 262142 share values into 10000 weights at a constant rate, so every weight
covered the same width — 25 milliCPU, everywhere. Weight 4 covered 80m to 104m; weight 17 covered
413m to 437m; weight 39 covered 976m to 1000m. The new map is finer everywhere it matters: weight 4
covers 10m to 14m, weight 17 covers 93m to 100m, weight 100 covers 989m to 1000m. Five, eight and
twelve milliCPU per weight against a flat twenty-five. The post argues granularity from a single
value being too small to subdivide; the measurable result is a resolution improvement of two to five
times across the range a cluster actually uses.

**The change the post announces is not the only change it makes.** Both problems at `:51-92` are
stated against processes outside Kubernetes: a container asking for one CPU should compete with a
system daemon on equal terms, and the linear map broke that. The new curve restores it. Nothing in
the post asks what the same curve does to two Kubernetes containers competing with each other, and
the answer is that it changes that too.

**Proportionality between containers survived the old formula and does not survive the new one.**
Under cgroup v1 the shares were the request, scaled: 100m and 1000m sat at 102 and 1024, a ratio of
0.0996. The linear map preserved that to within about three per cent above 100m — weights 4, 10, 20,
39 and 79 against a 1000m baseline of 39 give ratios of 0.103, 0.256, 0.513, 1.000 and 2.026 for
requests of 0.10, 0.25, 0.50, 1.00 and 2.00. The quadratic map does not preserve it. The same
requests give weights 17, 35, 59, 100 and 174, and ratios of 0.170, 0.350, 0.590, 1.000 and 1.740. A
100m container now carries seventy per cent more weight against its 1000m neighbour than its request
says it should, and a 2000m container carries thirteen per cent less. Under contention that is a
redistribution of CPU time between Pods that nobody edited, shipped by a runtime upgrade. Steps 5
and 7 measure it rather than arguing it.

**The pin's one sentence about any of this is the sentence the change makes vaguer.**
`docs/concepts/configuration/manage-resources-containers.md:273-275` says the CPU request typically
defines a weighting, and that on a contended system workloads with larger requests are allocated
more CPU time than workloads with small ones. That is still true. It was also true before, and it
was true in a stronger form that the page never claimed — proportionally more — which has now
stopped being the case. The hedge in *typically* is carrying weight it was not written to carry.

**The same page says CPU is never relative a hundred lines above saying it is a weighting.**
`:164-165` reads: CPU resource is always specified as an absolute amount of resource, never as a
relative amount, and 500m represents roughly the same computing power on a single-core machine as on
a forty-eight-core one. `:273` says the request typically defines a weighting. Both sentences are
defensible on their own — the first is about the unit, the second about the enforcement — and the
page never reconciles them. A reader working out why their 500m container is being starved next to a
100m one has to notice unaided that an absolute unit is enforced as a relative weight, and that the
conversion between the two is not on this page or any other.

**The pinned tree names three cgroup v1 control files and none of their v2 replacements.** Count
them under `content/en/docs`: `cpu.shares` has exactly one occurrence,
`docs/concepts/scheduling-eviction/pod-overhead.md:123`. `cpu.cfs_quota_us` has one, at `:119` on
the same page. `memory.limit_in_bytes` has two, at `:120` and inside a cgroup path in the worked
example at `:186`. `cpu.weight` has zero and `cpu.max` has zero. So the only passage in the
documentation that shows a resource number becoming a kernel setting is written entirely in the
vocabulary of the cgroup version the same tree deprecates — [the cgroup v2 GA
walk](../2022/06-cgroupv2-ga-1-25.md) establishes that `cgroups.md:134-142` marks cgroup v1
deprecated at v1.35 and that the kubelet will not start on such a node by default. [The RuntimeClass
walk](../2018/09-runtimeclass.md) noticed the v1 path at `pod-overhead.md:186` and deferred the
version question to the cgroup rows in later years; this is one of them, and the answer is that the
vocabulary problem is not confined to the worked example.

**`cpu.weight` is written in one post out of 767, and this is the post.** Eight occurrences, all
here. `cpu.shares` is the same story on the blog side — nine occurrences, all in this post — so the
two file names that the conversion maps between appear together nowhere else in twelve years of
announcements. `cpu.max` appears in no post and on no documentation page. A reader who wants to know
what number their request became has this post, the kernel documentation, and the runtime's source.

**The post's own pointer to further reading lands on the page that does not contain its subject.**
`:177` offers `manage-resources-containers.md` as current resource management guidance. Neither
formula is on it. Neither file name is on it. The single sentence that touches the mechanism is the
hedged one at `:273-275`. Following the post's link to learn more teaches nothing more about what
the post is about.

**The version floor that decides the behaviour is a kind of fact the tree does record, and it does
not record this one.** Four OCI-runtime floors sit in the pinned documentation, all for other
features: runc since v1.1 and crun since v1.8.6 at `docs/concepts/storage/volumes.md:1325-1326`, and
runc 1.2 with crun 1.9 — 1.13 recommended — at
`docs/concepts/workloads/pods/user-namespaces.md:52-53`. None is anywhere near 1.3.2 or 1.23. Worse,
the requirements list for cgroup v2 itself at `docs/concepts/architecture/cgroups.md:52-61` names a
kernel version, containerd v1.4, cri-o v1.20 and the systemd cgroup driver, and names no OCI runtime
at all. The layer this post says owns the behaviour is missing from the page that lists what the
feature needs.

**There is no gate, no release note and no version skew to hang any of this on.** The cgroup v2 GA
walk already establishes that cgroup v2 itself has no feature gate; this goes further. Nothing in
`content/en/docs` gates the conversion, no Kubernetes minor changes it, and two nodes in one cluster
running different runc patch releases will give identical Pods different weights. The census marks
the Kubernetes column `—` for exactly this reason, and calls it the first walk whose discontinuity
ships entirely outside Kubernetes.

**One small thing about the file itself.** The front matter sets `math: true` at `:5`, which two
posts in the archive do — this one and 2025's HPA tolerance announcement. Forty of the post's 185
lines carry trailing whitespace, a hard-wrapped draft that nobody ran a linter over, which is worth
knowing only because it tells you how much of the text was hand-shaped rather than generated from
the KEP.

**What this exercise does not cover, and where it lives.** Nothing here touches `cpu.max`, the quota
pair that enforces a CPU *limit*: weight decides who wins a contended CPU, quota decides when a
container is stopped regardless, and the two are independent. The cgroup v2 filesystem itself, what
the kubelet writes into it and how a container sees it, is [the cgroup v2 GA
walk](../2022/06-cgroupv2-ga-1-25.md); the deprecation timeline that ends cgroup v1 is [the
maintenance-mode walk](../2024/05-cgroup-v1-maintenance-mode.md); the QoS slices above the Pod and
the memory keys written into them are [the memory QoS walk](../2021/08-qos-memory-resources.md),
whose UID-to-cgroup-path helper at `:302-312` this exercise reuses rather than re-deriving. crun is
not installed by the node baseline and this exercise does not install it, so the 1.23 half of the
adoption story is out of reach here for [the reason the user-namespace walk
gives](../2024/02-userns-beta.md). Running any of this on a cgroup v1 node is not possible at the
pin, because the kubelet refuses to start on one. And KEP #5474, writable cgroups for unprivileged
containers, is a plan the post cites as motivation; it ships nothing at the pin and nothing here
tests it.

**The diff, and why**

**Wrong when it was published.** Two numbers. `:124` says one CPU now gets `cpu.weight = 102` and
calls that close to the default of 100, when the curve at `:100-102` was designed at `:106` to cross
(1024, 100) and does so in exact arithmetic. `:160-161` says milliCPU 90 through 109 all map to
weight 17 when the band is 93 through 100. Neither is a stale fact that time overtook — both were
false on 2026-01-30 against the formula printed eighty lines above them, and both are checkable in
thirty seconds with a calculator. The second is the more damaging, because it is addressed
explicitly to the people writing tools against these values.

**Still right.** The mechanism, the motivation and the adoption story all hold. The linear map
really did put one CPU at weight 39 against a default of 100 — the exercise reads exactly that
number off a downgraded node in step 6. The granularity argument holds and the measurement is
stronger than the argument: the new curve resolves 100m to within eight milliCPU where the old one
resolved it to twenty-five. `:135-139` is right that this is not a Kubernetes change, and the lab
proves it the hard way, by changing the numbers on a node whose Kubernetes version never moves.

**Never absorbed.** The pin has nothing. `cpu.weight` has zero occurrences under `content/en/docs`
and one in 767 blog posts, which is this post. No page gained a sentence, no reference page gained a
row, no feature gate exists to list. That is not neglect — there is no Kubernetes artifact to
document, because the behaviour belongs to a binary the project does not ship. It is still a gap for
a reader, because the question *what number did my request become* has no answer anywhere on the
site.

**Overtaken by stasis.** The one page a reader would reach for has aged into the wrong vocabulary.
`pod-overhead.md:118-124` explains how requests and limits become kernel settings using
`cpu.shares`, `cpu.cfs_quota_us` and `memory.limit_in_bytes`, three cgroup v1 filenames, in a tree
that deprecates cgroup v1 at `cgroups.md:134-142` and refuses to start a kubelet on such a node.
Nothing about that page is newly wrong; it simply stopped being about the cgroup version the
documentation now requires, and this post is what the paragraph would have to say if anybody rewrote
it.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180`, 4096MB, 4
CPUs, 25G, [provisioned](../../strands/lab-topologies.md#provision) and
[baselined](../../strands/lab-topologies.md#node-baseline-steps) as usual, running Kubernetes v1.35
on containerd 2.2.1 and runc 1.5.1. One node is right and a second would be noise: every number this
exercise reads is a file in this node's own cgroup tree, and every number it measures is two
processes on this node's four CPUs competing for them. The four CPUs matter, because the contention
steps need more runnable threads than cores and the arithmetic of the split depends on knowing how
many cores there are. Everything lives in a namespace called `bw-weight` except the runc binary,
which steps 6 and 8 move and restore; `/usr/local/sbin/runc` is backed up to `/root/runc-1.5.1.bak`
before anything touches it, and *Teardown* puts it back whether or not step 8 ran. Steps 1 to 9 run
on the node over `ssh zain@10.10.10.180`; step 10 runs offline against a checkout of
`kubernetes/website` at the pin, with `W` set to its `content/en` directory.

**Do**

1. Find out which formula this node runs, before touching anything. Open one session with `ssh
   zain@10.10.10.180` and stay in it; every fence up to step 10 is written as though you are already
   there. The last two lines are the point of the step: the interface files present in the tree are
   the v2 set, and the file the documentation talks about is not there at all.

   ```sh
   stat -fc %T /sys/fs/cgroup/                 # cgroup2fs, or stop here
   uname -r
   containerd --version
   runc --version
   grep -n 'SystemdCgroup' /etc/containerd/config.toml
   kubectl get nodes -o wide
   kubectl create namespace bw-weight
   ls /sys/fs/cgroup/kubepods.slice/ | grep '^cpu'
   ls -l /sys/fs/cgroup/kubepods.slice/cpu.weight /sys/fs/cgroup/kubepods.slice/cpu.shares 2>&1
   ```

2. Six requests, six Pods, and read what the kernel was told. All six are Burstable with a CPU
   request and no limit, so nothing here is capped — only weighted. The helper is [the memory QoS
   walk's](../2021/08-qos-memory-resources.md) UID-to-path find at `:302-312`, pointed at a
   different file.

   ```sh
   for m in 10 100 250 500 1000 2000; do
     cat <<EOF | kubectl -n bw-weight apply -f -
   apiVersion: v1
   kind: Pod
   metadata: {name: cw-${m}m, labels: {app: cw}}
   spec:
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh","-c","sleep 3600"]
         resources:
           requests: {cpu: "${m}m"}
   EOF
   done
   kubectl -n bw-weight wait --for=condition=Ready pod -l app=cw --timeout=180s

   cw() {
     U=$(kubectl -n bw-weight get pod "$1" -o jsonpath='{.metadata.uid}' | tr '-' '_')
     P=$(sudo find /sys/fs/cgroup -type d -name "*${U}*" | head -1)
     [ -n "$P" ] || { echo "$1: no cgroup"; return; }
     printf '%-10s pod=%-6s' "$1" "$(sudo cat "$P/cpu.weight")"
     for D in $(sudo find "$P" -mindepth 1 -maxdepth 1 -type d); do
       printf ' %s=%s' "$(basename "$D" | cut -c1-20)" "$(sudo cat "$D/cpu.weight")"
     done
     echo
   }
   for m in 10 100 250 500 1000 2000; do cw cw-${m}m; done
   ```

3. Compute both formulas on the node and diff them against what you just read. `awk` is used rather
   than a language with a `ceil`, for two reasons: it is certainly installed on the guest, and its
   `int()` truncates toward zero exactly as the Go the runtime is written in does.

   ```sh
   calc() { awk -v m="$1" 'BEGIN{
     s = int(m*1024/1000); if (s < 2) s = 2;
     o = 1 + int((s-2)*9999/262142);
     L = log(s)/log(2);
     e = (L*L)/612 + (125*L)/612 - 7/34;
     w = exp(e*log(10));
     n = int(w); if (w > n) n = n + 1;
     printf "%6d %8d %6d %6d   raw %.12f\n", m, s, o, n, w }'; }
   printf '%6s %8s %6s %6s\n' milli shares old new
   for m in 10 100 250 500 1000 2000; do calc $m; done
   ```

4. Now the question the post never asks: what happened to the relationship between two Kubernetes
   containers. Take the 1000m row as the baseline and print every column as a ratio against it. The
   request column and the shares column are the same numbers; the two weight columns are not.

   ```sh
   awk 'BEGIN{
     split("10 100 250 500 1000 2000", M, " ");
     for (i in M) {
       m = M[i]; s = int(m*1024/1000); if (s < 2) s = 2;
       o = 1 + int((s-2)*9999/262142);
       L = log(s)/log(2); e = (L*L)/612 + (125*L)/612 - 7/34;
       w = exp(e*log(10)); n = int(w); if (w > n) n = n + 1;
       ss[m] = s; oo[m] = o; nn[m] = n;
     }
     printf "%6s %9s %9s %9s %9s\n", "milli", "req", "shares", "old", "new";
     split("10 100 250 500 1000 2000", K, " ");
     for (i = 1; i <= 6; i++) { m = K[i];
       printf "%6d %9.3f %9.3f %9.3f %9.3f\n",
         m, m/1000, ss[m]/ss[1000], oo[m]/oo[1000], nn[m]/nn[1000]; }
   }'
   ```

5. Measure the split rather than believing the table. Two Pods, 1000m and 100m, each spinning one
   busy loop per core on a four-core node, so eight runnable threads chase four CPUs and the weights
   have to arbitrate. Read `usage_usec` from each Pod's `cpu.stat` before and after a minute.
   `kubectl` will feel slow while this runs, because the control plane is competing too; that is the
   measurement working, not a fault.

   ```sh
   N=$(nproc)
   for p in hi:1000 lo:100; do
     cat <<EOF | kubectl -n bw-weight apply -f -
   apiVersion: v1
   kind: Pod
   metadata: {name: cw-${p%%:*}, labels: {app: spin}}
   spec:
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh","-c","i=0; while [ \$i -lt $N ]; do (while :; do :; done) & i=\$((i+1)); done; wait"]
         resources:
           requests: {cpu: "${p##*:}m"}
   EOF
   done
   kubectl -n bw-weight wait --for=condition=Ready pod -l app=spin --timeout=180s

   usec() {
     U=$(kubectl -n bw-weight get pod "$1" -o jsonpath='{.metadata.uid}' | tr '-' '_')
     P=$(sudo find /sys/fs/cgroup -type d -name "*${U}*" | head -1)
     sudo awk '/^usage_usec/{print $2}' "$P/cpu.stat"
   }
   a1=$(usec cw-hi); b1=$(usec cw-lo); sleep 60; a2=$(usec cw-hi); b2=$(usec cw-lo)
   awk -v a=$((a2-a1)) -v b=$((b2-b1)) 'BEGIN{
     printf "hi %d us   lo %d us   hi:lo %.2f\n", a, b, a/b }'
   cw cw-hi; cw cw-lo
   ```

6. Go backwards one patch release. runc 1.3.1 is the release immediately before the change and is
   still past containerd 2.x's floor of 1.2.0, so the node keeps working; the only thing that moves
   is the arithmetic. Kubernetes does not move, the manifests do not move, and the Pods have to be
   recreated because a container's cgroup is written when the container is created.

   ```sh
   sudo cp -a /usr/local/sbin/runc /root/runc-1.5.1.bak
   cd /tmp
   curl -fsSLO https://github.com/opencontainers/runc/releases/download/v1.3.1/runc.amd64
   curl -fsSL https://github.com/opencontainers/runc/releases/download/v1.3.1/runc.sha256sum \
     | grep ' runc.amd64$' | sha256sum -c -
   sudo install -m 755 /tmp/runc.amd64 /usr/local/sbin/runc
   runc --version
   sudo systemctl restart containerd
   sleep 20; systemctl is-active containerd kubelet

   kubectl -n bw-weight delete pod -l app=cw --wait
   for m in 10 100 250 500 1000 2000; do
     cat <<EOF | kubectl -n bw-weight apply -f -
   apiVersion: v1
   kind: Pod
   metadata: {name: cw-${m}m, labels: {app: cw}}
   spec:
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh","-c","sleep 3600"]
         resources:
           requests: {cpu: "${m}m"}
   EOF
   done
   kubectl -n bw-weight wait --for=condition=Ready pod -l app=cw --timeout=180s
   for m in 10 100 250 500 1000 2000; do cw cw-${m}m; done
   ```

7. Re-run the contention measurement with nothing changed except the binary that wrote the weights.
   Delete and recreate the two spinners so their cgroups are written by runc 1.3.1, then take the
   same minute.

   ```sh
   kubectl -n bw-weight delete pod -l app=spin --wait
   N=$(nproc)
   for p in hi:1000 lo:100; do
     cat <<EOF | kubectl -n bw-weight apply -f -
   apiVersion: v1
   kind: Pod
   metadata: {name: cw-${p%%:*}, labels: {app: spin}}
   spec:
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh","-c","i=0; while [ \$i -lt $N ]; do (while :; do :; done) & i=\$((i+1)); done; wait"]
         resources:
           requests: {cpu: "${p##*:}m"}
   EOF
   done
   kubectl -n bw-weight wait --for=condition=Ready pod -l app=spin --timeout=180s
   a1=$(usec cw-hi); b1=$(usec cw-lo); sleep 60; a2=$(usec cw-hi); b2=$(usec cw-lo)
   awk -v a=$((a2-a1)) -v b=$((b2-b1)) 'BEGIN{
     printf "hi %d us   lo %d us   hi:lo %.2f\n", a, b, a/b }'
   cw cw-hi; cw cw-lo
   kubectl -n bw-weight delete pod -l app=spin --wait
   ```

8. Put the node back, then test the claim the post makes to tool authors. Twenty-two containers in
   one Pod, one per milliCPU value from 89 to 110, is the cheapest way to read twenty-two weights
   written by the same runtime at the same instant. The sum of the requests is 2189m, which fits
   alongside the control plane on four CPUs.

   ```sh
   sudo install -m 755 /root/runc-1.5.1.bak /usr/local/sbin/runc
   runc --version
   sudo systemctl restart containerd
   sleep 20; systemctl is-active containerd kubelet

   { printf 'apiVersion: v1\nkind: Pod\nmetadata: {name: cw-band}\nspec:\n  containers:\n'
     for m in $(seq 89 110); do
       printf '    - {name: c%s, image: "busybox:1.36", command: ["sh","-c","sleep 3600"], ' "$m"
       printf 'resources: {requests: {cpu: "%sm"}}}\n' "$m"
     done
   } | kubectl -n bw-weight apply -f -
   kubectl -n bw-weight wait --for=condition=Ready pod/cw-band --timeout=300s

   U=$(kubectl -n bw-weight get pod cw-band -o jsonpath='{.metadata.uid}' | tr '-' '_')
   P=$(sudo find /sys/fs/cgroup -type d -name "*${U}*" | head -1)
   for m in $(seq 89 110); do
     ID=$(kubectl -n bw-weight get pod cw-band \
           -o jsonpath="{.status.containerStatuses[?(@.name=='c$m')].containerID}" | sed 's|.*/||')
     D=$(sudo find "$P" -type d -name "*${ID}*" | head -1)
     printf '%4sm %s\n' "$m" "$(sudo cat "$D/cpu.weight")"
   done
   ```

9. The knife-edge. The exponent at 1024 shares is a fraction over 612 that reduces to exactly 2, so
   the exact answer is 100 and the ceiling changes nothing. Floating point does not get exactly 2.
   Print the intermediate values to seventeen significant figures, and put them next to the number
   runc wrote for the 1000m Pod in step 6's re-read — one is arithmetic and the other is evidence.

   ```sh
   awk 'BEGIN{
     L = log(1024)/log(2);
     e = (L*L)/612 + (125*L)/612 - 7/34;
     w = exp(e*log(10));
     printf "L        = %.17g\n", L;
     printf "e        = %.17g   (exact: 1224/612 = 2)\n", e;
     printf "10^e     = %.17g   (exact: 100)\n", w;
     printf "ceil     = %d\n", (w > int(w)) ? int(w)+1 : int(w);
   }'
   calc 1000; calc 1001
   cw cw-1000m
   ```

10. Offline, in a checkout of `kubernetes/website` at the pin, with `W` set to its `content/en`
    directory. Count the vocabulary, then read the four passages the exercise rests on in the order
    a confused reader would reach them.

    ```sh
    for k in cpu.weight cpu.shares cpu.max cpu.cfs_quota_us memory.limit_in_bytes; do
      printf '%-22s docs=%-3s posts=%s\n' "$k" \
        "$(grep -r --include='*.md' -oF "$k" $W/docs | wc -l | tr -d ' ')" \
        "$(grep -r --include='*.md' -oF "$k" $W/blog/_posts | wc -l | tr -d ' ')"
    done
    sed -n '116,126p' $W/docs/concepts/scheduling-eviction/pod-overhead.md
    sed -n '186p'     $W/docs/concepts/scheduling-eviction/pod-overhead.md
    sed -n '164,165p;273,275p' $W/docs/concepts/configuration/manage-resources-containers.md
    sed -n '52,61p;134,142p'   $W/docs/concepts/architecture/cgroups.md
    sed -n '1325,1326p'        $W/docs/concepts/storage/volumes.md
    sed -n '52,53p'            $W/docs/concepts/workloads/pods/user-namespaces.md
    grep -rl '^math: true' $W/blog/_posts | wc -l
    grep -c ' $' $W/blog/_posts/2026/new-cgroup-v1-to-v2-conversion-formula/index.md
    ```

**Expect**

Step 1 answers the exercise's first question before any Pod exists. `stat` prints `cgroup2fs`; the
kernel is a 6.x Debian trixie kernel, comfortably past the 5.8 floor that `cgroups.md:52-61` sets;
`containerd --version` prints 2.2.1 and `runc --version` prints 1.5.1, which is two minor releases
past the 1.3.2 the post names at `:142`. So this node has been writing the new weights since it was
baselined, and everything the post frames as a coming change is already behind you. The `ls` shows
the cgroup v2 CPU interface — `cpu.max`, `cpu.pressure`, `cpu.stat`, `cpu.weight` and
`cpu.weight.nice` among them. The last line is the one to keep: `cpu.weight` has a size and a
timestamp, and `cpu.shares` prints `No such file or directory`. The single passage in the pinned
documentation that explains how a request reaches the kernel names the file that is not there.

Step 2 prints the six weights. Pod-level values are 4, 17, 35, 59, 100 and 174 for requests of 10m,
100m, 250m, 500m, 1000m and 2000m. Two directories appear under each Pod slice, one for the
`busybox` container and one for the sandbox; the container's weight matches the Pod's, because each
Pod has exactly one container and the kubelet sums requests to get the Pod value. The 1000m row is
the one to stare at: the node wrote 100, and `:124` says the answer is 102.

Step 3 shows where 102 could not have come from. The table reads 10/10/1/4, 100/102/4/17,
250/256/10/35, 500/512/20/59, 1000/1024/39/100 and 2000/2048/79/174 across milliCPU, shares, old
weight and new weight. Every new-weight column matches what step 2 read off the kernel. The `old`
column is the post's problem statement reproduced exactly — 39 for one CPU and 4 for 100m, the two
numbers `:63` and `:81` complain about. And 102 appears in the table once, in the shares column of
the 100m row, which is where the post picked it up. The `raw` column prints `100.000000000000` for
the 1000m row, which is true to twelve places and hides what step 9 is for.

Step 4 is the finding the post does not have. The request column and the shares column agree to
three decimal places at every row — 0.010, 0.100, 0.250, 0.500, 1.000, 2.000 — because shares were
the request scaled by a constant. The old-weight column tracks them to within about three per cent
above 100m: 0.026, 0.103, 0.256, 0.513, 1.000, 2.026. The new-weight column does not track them at
all: 0.040, 0.170, 0.350, 0.590, 1.000, 1.740. Small requests gain and large requests lose, and the
error is worst exactly where clusters put most of their Pods. A 100m container is weighted at
seventeen per cent of a 1000m one, not ten.

Step 5 turns that ratio into CPU time. With four spinners in each Pod on four cores, the
`usage_usec` deltas over a minute come out around five to six to one rather than the ten to one the
requests describe. The exact number moves run to run — the control plane is competing for the same
cores, and the sandbox containers contribute a little — so read the magnitude and not the decimals.
What matters is that it sits near the new weight ratio of 100 to 17 and nowhere near 10 to 1.

Step 6 is the whole exercise in one command. `runc --version` prints 1.3.1; containerd restarts; the
Pods are deleted and recreated from byte-identical manifests against an unchanged Kubernetes v1.35
control plane. The six weights come back 1, 4, 10, 20, 39 and 79. Nothing about the cluster changed.
A 47KB binary changed, and every CPU priority on the node changed with it. Note also that the Pods
you did not delete — everything in `kube-system` — are still carrying weights written by 1.5.1,
because a container's cgroup is written once, at creation. A node part way through a rolling restart
runs both formulas at the same time.

Step 7 measures the old split. The `usage_usec` ratio moves up to roughly eight or nine to one,
against a weight ratio of 39 to 4, and the two Pods' `cpu.weight` files now read 39 and 4. Put the
two measurements side by side: the same two manifests, the same node, the same minute of wall clock,
and the 100m Pod gets about half again as much CPU under the new formula as it did under the old
one. The post's `:147-154` warns tool authors that their predicted numbers will change. The thing
that actually changed is how much CPU the workloads get.

Step 8 settles the band. After the restore, `runc --version` prints 1.5.1 again. The twenty-two
containers report 16 for 89m through 92m, 17 for 93m through 100m, 18 for 101m through 108m, and 19
for 109m and 110m. The post's claim at `:160-161` is that 90m through 109m all give 17. Of the
twenty values it names, three give 16, eight give 18 and one gives 19; only the eight from 93m to
100m give what the post says. A monitoring rule written from that sentence mis-buckets twelve times
out of twenty.

Step 9 shows why the number everybody quotes is lucky. `L` prints as exactly 10, and `e` prints as 2
or within an ulp or two of it depending on your platform's `log` and `exp`. In exact arithmetic the
exponent is 1224/612, which is 2 with nothing left over, and the answer is 100 with no rounding
involved. In doubles the answer lands a few parts in ten to the fifteenth away from 100, and the
ceiling decides. If your `awk` lands below, `10^e` prints as `99.999999999999943` and the ceiling
gives 100, agreeing with the node. If it lands above, `awk` prints 101 while runc wrote 100, and you
have found the same knife-edge from the other side — a curve whose most-quoted design point depends
on which way the last bit fell in whichever implementation you ask. `calc 1001` gives 101, so 1000m
is the last request in its bucket as well as the exact crossing point.

Step 10 is the pin's side of it. `cpu.weight` reads `docs=0 posts=8`; `cpu.shares` reads `docs=1
posts=9`, and both post counts are this one file; `cpu.max` reads zero and zero; `cpu.cfs_quota_us`
reads `docs=1 posts=0`; `memory.limit_in_bytes` reads `docs=2 posts=2`. Then the passages.
`pod-overhead.md:118-124` explains the conversion in three cgroup v1 file names, and `:186` reads
one of them out of a cgroup v1 path — a page [the RuntimeClass walk](../2018/09-runtimeclass.md)
already flagged and handed forward. `manage-resources-containers.md:164-165` says CPU is never a
relative amount and `:273-275` says the request typically defines a weighting, a hundred lines apart
on the page this post recommends as current guidance. `cgroups.md:52-61` lists what cgroup v2 needs
and names no OCI runtime; `:134-142` deprecates cgroup v1 anyway. `volumes.md:1325-1326` and
`user-namespaces.md:52-53` show that the tree does record runc and crun floors when a Kubernetes
feature depends on them — v1.1, v1.8.6, 1.2 and 1.9 — and none of the four is close to 1.3.2 or
1.23. The last two lines: two posts in the archive set `math: true`, and forty of this one's 185
lines end in a space.

**Read on**

11. [The cgroup v2 GA walk](../2022/06-cgroupv2-ga-1-25.md), for the filesystem this exercise reads
    and for the requirements list that does not mention a runtime.

12. [The cgroup v1 maintenance-mode walk](../2024/05-cgroup-v1-maintenance-mode.md), for the
    deprecation that makes `pod-overhead.md:118-124` a page written in a dead vocabulary.

13. [The memory QoS walk](../2021/08-qos-memory-resources.md), for the QoS slices above the Pod, for
    the helper this exercise borrows at `:302-312`, and for the memory half of the same story.

14. [The RuntimeClass walk](../2018/09-runtimeclass.md), which found the cgroup v1 path in
    `pod-overhead.md` at `:186` and deferred the version question to the cgroup rows.

15. Unanswerable from the pin: where the 102 at `:124` came from. It is the share count for 100m,
    printed twice elsewhere in the same post, so a transcription is the obvious guess — but the post
    also links a Go playground program and a Kubernetes issue for the arithmetic, and neither is in
    the pinned tree. The node can tell you what runc computes. It cannot tell you what the author
    ran.

**Teardown**

The namespace takes the Pods. The one thing that is not in the namespace is the runc binary, so run
the restore whether or not step 8 completed — a node left on 1.3.1 will quietly hand every later
exercise the old weights.

```sh
ssh zain@10.10.10.180 "sudo install -m 755 /root/runc-1.5.1.bak /usr/local/sbin/runc; \
  runc --version; \
  sudo systemctl restart containerd; \
  kubectl delete namespace bw-weight --wait; \
  sudo rm -f /root/runc-1.5.1.bak /tmp/runc.amd64"
```
