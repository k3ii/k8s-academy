<a id="kubernetes-1-31-moving-cgroup-v1-support-maintenance-mode"></a>

# The state this post announces, and links to its own definition of, appears nowhere in the pinned documentation; the one sentence that carries the idea calls it something else on a page about kernel version floors; and what is left of it on a node is a kubelet field with no flag

**Post** — [Kubernetes 1.31: Moving cgroup v1 Support into Maintenance Mode](https://kubernetes.io/blog/2024/08/14/kubernetes-1-31-moving-cgroup-v1-support-maintenance-mode/),
2024-08-14.

4,742 bytes, 102 lines, one author: Harshal Patil. Forty-seventh of 2024's 54 posts by size, 6,026
below the year's mean of 10,768, and the shortest post in this year's `walk` set. Eleven links, of
which two reach kubernetes.io and both of those are in *Further reading*; three go to github.com;
two to the kernel's own cgroup documentation; two to `man7.org`; one to `systemd.io`; and one is an
in-page anchor to the post's own definition of its subject. The KEP this post exists to announce,
4569, is not among them — the only KEP it links is 2033, for rootless kubelets, cited in passing for
one of cgroup v2's benefits.

**As written**

`:9-15` states the decision in one sentence and immediately links
`#what-does-maintenance-mode-mean`, an anchor inside the post itself. That link is the shape of the
whole piece: the term is new, the post knows it is new, and the post is where it will be defined.

`:17-32` is a primer. Control groups are a Linux kernel feature for allocating, prioritising,
denying and managing CPU, memory, disk I/O and network bandwidth among processes, which matters most
in multi-tenant environments. Then the flat claim at `:27-29`: *There are two versions of cgroups:
v1 and v2*, each linked to its own kernel documentation. v1 *provided sufficient capabilities* and
*had limitations that led to the development of cgroup v2*.

`:34-50` puts that in Kubernetes terms. Each container is placed in its own cgroup, which is how
limits get enforced, usage gets monitored, and distribution stays fair. `:43-50` is a definition
list of three terms — Resource Allocation, Isolation, Monitoring — and it is the only formatted
structure in the post that is not a numbered list.

`:52-65` is the direction of travel. The Linux community focuses new work on v2; major distributions
and systemd are transitioning; v2 brings a unified hierarchy, an improved interface, better resource
control, a cgroup-aware OOM killer and rootless support. Two of those five are linked to GitHub
rather than to documentation — a pull request and a KEP README anchor. `:63-65` says Kubernetes is
making the move too, carefully, *to avoid disrupting existing workloads*.

`:67-86` is the announcement. `:71-76` defines the term in three numbered promises: **Feature
Freeze**, no new features added to cgroup v1 support; **Security Fixes**, critical ones still
provided; **Best-Effort Bug Fixes**, major bugs fixed if feasible. `:78-86` gives the reason and
then the reassurance the rest of this exercise is about: *It's important to note that maintenance
mode does not mean deprecation; cgroup v1 will continue to receive critical security fixes and major
bug fixes as needed.*

`:88-96` is the instruction to administrators — two numbered items, upgrade the operating systems
and container runtimes, test the workloads — and `:98-102` is three further-reading links. There is
no feature gate named anywhere in the post, no `{{< feature-state >}}` marker, no version skew
table, and no command. Nothing in it is switchable.

**As it runs now**

The subject of this post is a word. So the first question is what happened to the word, and the
pinned tree answers it precisely.

**The phrase never entered the documentation.** At the pin, *maintenance mode* occurs twelve times
in `content/en`, in exactly two files: nine times in this post and three times in
`blog/_posts/2024/kubernetes-v1-31-release.md` (`:235`, `:249`, `:251`), which is the release
announcement of the same release. Under `docs/` the count is zero. The idea survives in the
reference documentation as one sentence, `docs/reference/node/kernel-version-requirements.md:58-59`,
under a heading called `## Version 2 control groups`: *Kubernetes cgroup v1 support is in maintained
mode starting from Kubernetes v1.31; using cgroup v2 is recommended.* The word is not *maintenance*,
it is *maintained*, and none of the three promises travelled with it. What the sentence gained
instead is a recommendation the post never makes in those words, and it sits on a page about kernel
version floors, between a paragraph on kube-proxy's nftables mode and one on Pressure Stall
Information.

**The one *maintenance mode* under `docs/` belongs to something else entirely.** Searched with a
hyphen instead of a space, the phrase does appear:
`docs/concepts/workloads/autoscaling/horizontal-pod-autoscale.md:653` is a heading reading *Implicit
maintenance-mode deactivation*, and `:655-660` defines it as an operator setting a workload's
replica count to zero so the HorizontalPodAutoscaler stops adjusting it. That is a different
subsystem, a different meaning and a different mechanism. It is the only thing in the Kubernetes
documentation that calls itself a maintenance mode, and it has nothing to do with this post.

**The reassurance became the thing it was distinguished from.** `concepts/architecture/cgroups.md`
carries a section marking cgroup v1 deprecated as of v1.35, four releases after this post. The
section and the kubelet field behind it belong elsewhere in this collection and are not re-explained
here; the line that matters for this exercise is `cgroups.md:139` — *Removal will follow [Kubernetes
deprecation policy]* — because it is a link, and following it is what settles the post's central
claim. `docs/reference/using-api/deprecation-policy.md:366-370` opens the rules for deprecating *a
feature or behavior of the system that is not controlled by the API or CLI*, which is exactly what
cgroup v1 support is. Rule #7 at `:372-373`: *Deprecated behaviors must function for no less than 1
year after their announced deprecation.* The lifecycle the policy names, at `:412-417`, has four
stages — alpha, beta, GA, and GA with the deprecation window complete — and a deprecation section at
`:419`. There is no maintenance mode in it, and there is no stage between supported and deprecated.
So the four releases this post bought started no clock under the policy the deprecation notice
points at; the one-year guarantee begins at v1.35, not at v1.31. The only part of the policy that
contemplates a state it has not defined is `## Exceptions` at `:493-502`, which says such situations
*should be discussed with SIGs and project leaders* and that *Exceptions will always be announced in
all relevant release notes* — which is, in policy terms, an accurate description of what this post
is.

**The feature freeze held, and it is legible only from the v2 side.** Nothing in the pinned tree
records a feature being added to cgroup v1 and nothing records one being taken away, because that is
not how a freeze shows up in documentation. It shows up as capabilities that only ever existed on
the other version. Four places under `docs/` say so in those terms:
`docs/reference/instrumentation/understand-psi-metrics.md:29` requires a cgroup v2 node;
`docs/tasks/configure-pod-container/resize-container-resources.md:59` requires it for resizing
memory-backed `emptyDir` volumes and `:193` is the only sentence in the tree that says what a cgroup
v1 node does instead — *in-place volume resize requests are rejected as infeasible*;
`docs/tasks/administer-cluster/kubelet-in-userns.md:131` requires it for running node components in
a user namespace; and `docs/concepts/workloads/pods/pod-qos.md:195` requires it for Memory QoS. All
four describe work that landed at or after the release this post announces.

**And the documentation disagrees with itself about the one field that is left.** The single place
in the whole configuration API where cgroup v1's behaviour survives as something you can ask for is
`docs/reference/config-api/kubelet-config.v1beta1.md:984-994`, the kubelet's `singleProcessOOMKill`.
Its own description says what it is for, at `:988-990`: setting it true prevents `memory.oom.group`
from being set on container cgroups under cgroup v2, so processes are OOM-killed individually rather
than as a group, and *the behavior aligns with the behavior of cgroups v1*. Then three consecutive
sentences. `:991`: *The default value is determined automatically when you don't specify.* `:993`:
*On cgroup v1 linux, only null / absent and true are allowed.* `:994`: *On cgroup v2 linux, null /
absent, true and false are allowed. The default value is false.* The first sentence says there is no
fixed default; the last says the default is `false`. They are reconcilable only if the last one is
scoped to cgroup v2 and the automatic default on cgroup v1 is `true`, which the page never states.
Do not pick a reading from the page. Step 4 reads the value off a running kubelet and settles it.

One smaller thing, since the post is about what a policy change costs an administrator: the field
has no command-line flag. `docs/reference/command-line-tools-reference/kubelet.md` lists
`--fail-cgroupv1` and `--oom-score-adj` and nothing for this one, so the only way to keep cgroup
v1's OOM semantics is to edit the kubelet configuration file and restart the kubelet. Step 6 does
exactly that.

**What this exercise does not cover, and where it lives**

cgroup v2 itself — the concept page, its requirements list, its distribution table, and the two
opposing `feature-state` markers the page carries for the two versions — belongs to [Fifteen bullets
absorbed word for word, and the eight the page added since](../2022/06-cgroupv2-ga-1-25.md). That
exercise also runs the citation test on its own post and reads `cgroup.controllers`, `memory.max`
and `cpu.max` from inside a container. Nothing here repeats any of it.

The `failCgroupV1` kubelet field, its documented default, and reading it off a running kubelet
belong to [The one configuration value this post documents does not parse at the pin, the default it
names in parentheses is not the default any more, and both rows of its cgroups table are
void](../2021/05-run-nodes-with-swap-alpha.md). This exercise reads a different field off the same
endpoint and does not touch that one. Memory QoS, `memory.min` and the reservation policy that sets
it belong to [Fifteen releases in alpha, beta on the newest release the pin
carries](../2021/08-qos-memory-resources.md), and the cgroup driver question — which component
decides whether the driver is `systemd` or `cgroupfs` — belongs to [The project this post announces
survives in the pinned documentation as a tab id, a PNG filename and an AppArmor
profile](../2017/08-containerd-container-runtime-options-kubernetes.md).

Which task inside a cgroup the kernel picks when memory runs out, and the arithmetic that decides
it, are lab ground: [The kernel kills the fattest process in the cgroup, and the pod is only marked
OOMKilled when that process happens to be the container's
init](../../labs/06/09-6c3-who-killed-the-pod.md) produces both outcomes on one pod spec, and [the
`oom_score_adj` each QoS class gets, from the
formula](../../labs/06/07-oom-score-adj-from-the-formula.md) computes the values it reads. Step 5
here reads the one file that decides whether that question has one victim or a whole cgroup of them;
it does not run the drill. Walking the cgroup tree from the node root down to a container is [Walk
from the node's root cgroup down to one container, naming every
level](../../labs/06/15-the-cgroup-tree-under-one-pod.md), and reading the kernel's pressure figures
is [the housekeeping drill](../../labs/06/13-faster-than-housekeeping.md). Pressure Stall
Information is named once below, as one of four counted requirements, and its own arc through alpha,
beta and GA is a later year's subject, not this one's.

**The diff, and why**

***Never absorbed.*** The post coins a term, links to its own definition of it, and the term went
nowhere. Zero occurrences under `docs/`; the only survivor is one sentence on a kernel-requirements
page that spells it differently and keeps none of the three promises. The absorption test's other
half gives the same answer: nothing in the pinned tree links this post. Not the concept page it
points at, not the kernel-requirements page that carries its one surviving sentence, and not the
release announcement for its own release, which cites the enhancement issue instead. Step 10 runs
both halves. This is the seventh case in its cleanest form — a post that was read, acted on, and
then left behind without a citation.

***Broke.*** `:84-86` is the sentence the post wrote in order to be reassuring: *maintenance mode
does not mean deprecation.* It is false at the pin, and the way it is false is worse than a simple
reversal. Because maintenance mode was not deprecation, Rule #7's one-year clock did not start when
this post was published; it started four releases later when the deprecation was actually declared.
The sentence was true as written and the four releases of grace it describes bought no guaranteed
time at all. An administrator who read `:84-86` in August 2024 and concluded there was no schedule
to plan against was reading it correctly, and that is exactly the problem.

***Still right.*** The freeze was real. No feature has been added to cgroup v1 support in the pinned
tree, and the four capabilities counted above all exist on v2 only. The post's one instruction to
administrators, at `:93-96` — make sure the operating system and the container runtime support
cgroup v2, then test the workloads — is still the entire migration, and step 7 runs it as a
checklist against a node. What the post could not say is that the second half of its own definition,
*critical security fixes* and *best-effort bug fixes*, is unobservable: there is no place in the
documentation, no field, and no metric that records whether either promise was kept. Only the first
promise left a trace.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180` running Kubernetes v1.35,
provisioned with [the standard steps](../../strands/lab-topologies.md#provision) and [the node
baseline](../../strands/lab-topologies.md#node-baseline-steps). One node is enough: everything here
is either a file the kernel exposes, a field the kubelet reads at startup, or a read of the pinned
checkout. The node runs cgroup v2, which is what makes it the right place to ask what is left of v1
— you are not looking for a cgroup v1 machine, you are looking for cgroup v1's remains on a machine
that does not use it. Cluster work happens in a namespace called `bw-cg1`. Step 6 edits the kubelet
configuration file and restarts the kubelet, so take the backup the step names before you run it.

**Do**

1. Ground the node, and note that the kernel still registers both filesystems. The post's subject is
   a version the node does not use, so start by confirming the node does not use it and that the
   kernel has not forgotten how.

   ```sh
   ssh zain@10.10.10.180
   kubectl version -o json | jq -r '.serverVersion.gitVersion'
   uname -r
   systemctl --version | head -1
   findmnt -no FSTYPE /sys/fs/cgroup
   grep cgroup /proc/filesystems
   ```

2. Read the v1 controller table. `/proc/cgroups` is cgroup v1's own interface and it is present on
   every kernel that has cgroups at all, whichever hierarchy is mounted. Four columns: the
   controller name, the hierarchy id it is attached to, how many cgroups use it, and whether it is
   enabled.

   ```sh
   cat /proc/cgroups
   awk 'NR>1 {n++; if ($4==1) e++; if ($2!=0) h++} END {
     printf "%d controllers listed, %d enabled, %d attached to a numbered hierarchy\n", n, e, h}' /proc/cgroups
   ```

3. Ask the kernel for a cgroup v1 hierarchy by hand. This is the difference between *frozen* and
   *gone*: a controller that is enabled in the table above may still be unavailable, because
   something else already holds it. Mount it in a scratch directory, read the answer, and put it
   back.

   ```sh
   sudo mkdir -p /mnt/bw-cg1
   sudo mount -t cgroup -o memory none /mnt/bw-cg1; echo "mount exit=$?"
   findmnt /mnt/bw-cg1 || echo 'nothing mounted at /mnt/bw-cg1'
   sudo umount /mnt/bw-cg1 2>/dev/null; sudo rmdir /mnt/bw-cg1
   ```

4. Ask the running kubelet what `singleProcessOOMKill` is on this node. Three sentences of the
   configuration reference disagree about the default; this is the command that settles them. Read
   the configuration file too, so you can tell a value the kubelet computed from a value somebody
   wrote.

   ```sh
   NODE=$(kubectl get node -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" \
     | jq '.kubeletconfig | {present: has("singleProcessOOMKill"), value: .singleProcessOOMKill}'
   sudo grep -n singleProcessOOMKill /var/lib/kubelet/config.yaml || echo 'not set in the config file'
   ```

5. Read the file the field controls, from inside a container. A container gets its own cgroup
   namespace, so `/sys/fs/cgroup` inside the pod is the container's own cgroup and no tree walk is
   needed. `memory.oom.group` exists only under cgroup v2; a `1` means the kernel kills every task
   in the cgroup together, a `0` means it picks one.

   ```sh
   kubectl create namespace bw-cg1
   kubectl -n bw-cg1 run g1 --image=busybox:1.36 --restart=Never -- sleep 3600
   kubectl -n bw-cg1 wait --for=condition=Ready pod/g1 --timeout=120s
   kubectl -n bw-cg1 exec g1 -- cat /sys/fs/cgroup/memory.oom.group
   kubectl -n bw-cg1 exec g1 -- sh -c 'ls /sys/fs/cgroup/ | head -20'
   ```

6. Now ask for cgroup v1's behaviour back. Take the backup first. The field has no command-line
   flag, so this is the whole procedure: one line in the configuration file, a kubelet restart, and
   a fresh pod — the setting is applied when a container's cgroup is created, so the pod from step 5
   will not change. Read the file again, then restore.

   ```sh
   sudo cp -a /var/lib/kubelet/config.yaml /var/lib/kubelet/config.yaml.bw-cg1.bak
   printf 'singleProcessOOMKill: true\n' | sudo tee -a /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet
   sleep 15
   kubectl -n bw-cg1 run g2 --image=busybox:1.36 --restart=Never -- sleep 3600
   kubectl -n bw-cg1 wait --for=condition=Ready pod/g2 --timeout=180s
   kubectl -n bw-cg1 exec g1 -- cat /sys/fs/cgroup/memory.oom.group
   kubectl -n bw-cg1 exec g2 -- cat /sys/fs/cgroup/memory.oom.group
   NODE=$(kubectl get node -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" | jq '.kubeletconfig.singleProcessOOMKill'
   sudo cp -a /var/lib/kubelet/config.yaml.bw-cg1.bak /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet
   ```

7. Run the post's instruction to administrators as a checklist. `:93-96` asks for two things: that
   the operating system and the container runtime support cgroup v2, and that the workloads are
   tested. The first half is four commands, and this is the runtime's side of it rather than the
   kernel's.

   ```sh
   grep '^PRETTY_NAME' /etc/os-release
   containerd --version
   runc --version | head -1
   sudo containerd config dump | grep -i 'systemd_cgroup\|SystemdCgroup'
   kubectl get node -o jsonpath='{.items[0].status.nodeInfo.containerRuntimeVersion}{"\n"}'
   ```

8. Offline, in a checkout of `kubernetes/website` at the pin. Census the phrase. Count it in the
   whole tree, count it under `docs/`, list the files that carry it, then find the sentence that
   survived and the unrelated thing that shares the name.

   ```sh
   cd /path/to/kubernetes/website/content/en
   grep -rn -i 'maintenance mode' . | wc -l
   grep -rn -i 'maintenance mode' docs/ | wc -l
   grep -rln -i 'maintenance mode' .
   grep -rn -i 'maintained mode' .
   grep -rn -i 'maintenance-mode' docs/
   sed -n '56,62p' docs/reference/node/kernel-version-requirements.md
   sed -n '653,660p' docs/concepts/workloads/autoscaling/horizontal-pod-autoscale.md
   ```

9. Still offline. Follow the link the deprecation notice points at and read what the policy actually
   offers. One line from the concept page, then the rules for deprecating a behaviour, then the only
   lifecycle the policy names, then the section that covers a state it has not defined.

   ```sh
   cd /path/to/kubernetes/website/content/en
   sed -n '139p' docs/concepts/architecture/cgroups.md
   sed -n '366,373p' docs/reference/using-api/deprecation-policy.md
   sed -n '409,418p' docs/reference/using-api/deprecation-policy.md
   sed -n '493,502p' docs/reference/using-api/deprecation-policy.md
   grep -c -i 'maintenance\|maintained' docs/reference/using-api/deprecation-policy.md || echo 0
   ```

10. Last offline step. Run the absorption test's citation half, read the field's paragraph in full,
    and count the four requirements that only the other version can meet.

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -rn 'kubernetes-1-31-moving-cgroup-v1-support-maintenance-mode' . | grep -v '^./blog/_posts/2024/moving-cgroup' || echo 'no inbound reference'
    grep -rn '2024/08/14' . || echo 'nothing links the post by URL'
    sed -n '984,995p' docs/reference/config-api/kubelet-config.v1beta1.md
    sed -n '29p' docs/reference/instrumentation/understand-psi-metrics.md
    sed -n '59p;193p' docs/tasks/configure-pod-container/resize-container-resources.md
    sed -n '131p' docs/tasks/administer-cluster/kubelet-in-userns.md
    sed -n '195p' docs/concepts/workloads/pods/pod-qos.md
    grep -c 'single-process-oom-kill' docs/reference/command-line-tools-reference/kubelet.md || echo 0
    ```

**Expect**

Step 1. v1.35, a 6.12 kernel, systemd 257, and `cgroup2` as the filesystem type at `/sys/fs/cgroup`.
The line that matters is the last one: `/proc/filesystems` lists **both** `cgroup` and `cgroup2`.
The kernel this node booted has cgroup v1 compiled in and registered as a mountable filesystem, and
nothing about the node using v2 changes that. Frozen is not the same as absent, and this is the
first place you can see the difference.

Step 2. `/proc/cgroups` prints a header and a row per controller — on a Trixie kernel expect
thirteen or fourteen of them, `cpuset` through `misc`. Every row should read `1` in the `enabled`
column and `0` in the hierarchy column. Those two numbers together are the whole state of cgroup v1
on this machine: the kernel offers every controller, and not one of them is attached to a v1
hierarchy, because the unified hierarchy has them. `num_cgroups` sitting at `1` for each is the root
cgroup and nothing else. The post's `:27-29` says there are two versions of cgroups; this file is
the first one, still exporting its interface to a node that has never used it.

Step 3. Expect the mount to fail, and expect the reason to be `device or resource busy` rather than
an unknown filesystem type. That distinction is the finding. The kernel understands the request; it
refuses because the memory controller is already bound to the unified hierarchy, and a controller
can be attached to one hierarchy at a time. So cgroup v1 on this node is not deprecated, not removed
and not disabled — it is unreachable, and it is unreachable because of a boot-time decision made by
systemd rather than by anything in Kubernetes. If the mount instead succeeds, the node did not put
every controller on the unified hierarchy and you have just created a live cgroup v1 hierarchy in
maintenance mode with one command; unmount it and record that, because it changes what every later
step means.

Step 4. Expect `present: true` and `value: false`, and expect the configuration file not to mention
the field at all. That settles the three sentences. `:991`'s *determined automatically* is the
operative rule — nobody wrote this value — and `:994`'s *The default value is false* describes what
the automatic determination produces **on a cgroup v2 node**, which is the scoping the page leaves
implicit. If instead `present` comes back `false`, the kubelet is not serialising a computed default
and `:991` is the only sentence in effect; either way, the reading in which `:994` is an
unconditional statement about all nodes is the one the node rules out, because `:993` forbids
`false` on cgroup v1 and a single unconditional default cannot be both legal and illegal.

Step 5. `memory.oom.group` prints `1`. The kubelet set it, because `singleProcessOOMKill` is false,
and a `1` means the kernel treats the container as a unit when it runs out of memory: every task in
the cgroup dies together. The listing shows the other half of what changed between the versions — a
flat set of interface files, `memory.max` and `cpu.max` and `pids.max` and `cgroup.controllers`,
with no per-controller subdirectory anywhere, because the unified hierarchy has one tree instead of
one per controller. Take the `1` and hold on to it; the next step is about turning it off.

Step 6. `g1` should still print `1` and `g2` should print `0`, and `configz` should now report
`true`. What you are looking at in `g2` is cgroup v1's OOM semantics running on a cgroup v2 node, a
release after cgroup v1 was deprecated and four after it was frozen, reachable because somebody
wrote one field for it — a field with no command-line flag, no feature gate and no `feature-state`
marker. That is what maintenance mode turned into where it is observable: not a mode, a
compatibility switch. If `g1` also flips to `0`, the kubelet rewrote an existing container's cgroup
on restart rather than deciding at creation time; record which happened, because the reference text
says only that the flag is *set for container cgroups* and does not say when. The last two commands
put the configuration back; the teardown checks that they did.

Step 7. Debian Trixie, containerd 2.2.1, runc 1.5.1, `SystemdCgroup = true`, and a runtime version
on the Node object matching the binary. Both of the post's instructions to administrators are
already satisfied and were satisfied before you started, which is the ordinary case at the pin and
the reason the post reads as advice addressed to somebody else. The post could not have known that;
in August 2024 the migration it describes was real work for a large number of clusters. What the
exercise records is that the advice outlived the situation it was written for by a wide margin.

Step 8. Twelve, then zero. Two files carry the phrase and both are blog posts from the same release.
`maintained mode` returns exactly one line, `docs/reference/node/kernel-version-requirements.md:58`,
and reading `:56-62` around it shows how small the landing was: a heading, that sentence, a note
about `cpu.stat` in Linux 5.8, and a note about runc's freezer. The hyphenated search returns the
HorizontalPodAutoscaler's *Implicit maintenance-mode deactivation*, which is an operator setting
replicas to zero. A term the post defined for the project is not in the project's documentation, and
the one phrase that looks like it belongs to a different subsystem.

Step 9. `cgroups.md:139` is a single sentence and it is a link. Rule #7 gives one year from
*announced deprecation*, and the deprecation was announced at v1.35, so the guarantee this post's
readers actually have started four releases after they read it. The lifecycle list names alpha,
beta, GA and GA-with-the-window-complete, and nothing between supported and deprecated. The last
count should print `0`: the deprecation policy does not contain the word *maintenance* or the word
*maintained* anywhere in its 502 lines. `## Exceptions` is the only part that anticipates a state
the policy has not defined, and its answer — discuss it with the SIGs, announce it in the release
notes — is a fair description of how this post came to exist.

Step 10. No inbound reference and nothing linking the post by URL: the citation half of the
absorption test comes back empty from a tree of 767 posts and several thousand documentation files.
The field's twelve lines are worth reading in one piece rather than as quotations. The four
requirement sentences are the freeze seen from the far side, and `resize-container-resources.md:193`
is the only one that says what happens on a cgroup v1 node instead of what is needed on a v2 one.
The last count is `0`: there is no command-line flag for the one field that preserves the behaviour
of the version this post was written about.

**Read on**

1. `docs/reference/using-api/deprecation-policy.md:366-450` — the behaviour half of the policy, read
   whole. Rules #7, #8, #9 and #10, the feature-gate lifecycle, and the deprecation section. It is
   the document that decides what a status announcement is worth, and it is short.

2. `docs/reference/node/kernel-version-requirements.md` — the page the post's idea ended up on.
   Reading it end to end is the quickest way to see why one sentence about a support status looks
   out of place between a kube-proxy kernel floor and a note about `CONFIG_PSI`.

3. `docs/reference/config-api/kubelet-config.v1beta1.md:984-994` — `singleProcessOOMKill` in full,
   including the two sentences step 4 settles and the one about non-Linux nodes that neither of them
   covers.

4. [Fifteen bullets absorbed word for word, and the eight the page added
   since](../2022/06-cgroupv2-ga-1-25.md) — the other side of this migration, from the release that
   declared cgroup v2 generally available. Read together, the two posts are the same arc from both
   ends, and neither is cited by the page that replaced them both.

5. Unanswerable from the pin: whether the second and third promises were kept. *Critical security
   fixes* and *best-effort bug fixes* leave no trace in documentation — no field records them, no
   metric counts them, and no page says whether a cgroup v1 bug was fixed or declined between v1.31
   and v1.35. Only the freeze left evidence, and only because new work went somewhere else.

**Teardown**

```sh
kubectl delete namespace bw-cg1 --wait=true
sudo cmp /var/lib/kubelet/config.yaml /var/lib/kubelet/config.yaml.bw-cg1.bak && echo 'kubelet config restored'
sudo rm -f /var/lib/kubelet/config.yaml.bw-cg1.bak
findmnt /mnt/bw-cg1 || echo 'no stray cgroup v1 mount'
systemctl is-active kubelet
```

The `cmp` is the important line. Step 6 appended to the kubelet's configuration file and restored it
from a copy; if the two files differ, something else wrote to the file in between and the node is
not in the state it started in. If step 3's mount succeeded and was not unmounted, `findmnt` will
say so — leaving a cgroup v1 hierarchy mounted on a node whose kubelet expects v2 is the one way
this exercise can damage a cluster. If the node was untainted during provisioning and the taint is
wanted back:

```sh
kubectl taint node --all node-role.kubernetes.io/control-plane=:NoSchedule
```
