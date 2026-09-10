<a id="pid-limiting"></a>

# This post became a documentation page that replaced all three of its numbers and links back to it through a path the pinned tree does not serve, both features it announces reached stable and then lost their gates, and the fork bomb it describes still works on a fresh cluster

**Post** — [Process ID Limiting for Stability Improvements in Kubernetes 1.14](https://kubernetes.io/blog/2019/04/15/pid-limiting/),
15 April 2019, by Derek Carr (Red Hat). 32 lines, 3,458 bytes. Frontmatter carries a title, a date
and an author, and nothing else — no `k8s` version. The version is in the title.

This is the shortest post the year sends to `walk`. It has no commands, no YAML, no output and no
code fences at all: four short prose sections, one release link and a bio. Everything a reader
could run has to be built from the pinned tree rather than lifted from the post. That is the
opposite of the usual problem, and it makes this exercise a reading of what the project did with
the post afterwards — which turns out to be more than it did with almost any other. The prose was
moved into the documentation tree, kept nearly word for word, and had every number in it replaced.

**As written** — a metaphor, a failure mode, a fix, and a forecast.

The opener at `:8` is about cookies: someone who "grabs a half dozen fresh baked chocolate chip
chunk morsels and skitters off like Cookie Monster." `:10` turns it into the resource: "With each
Pod and Node, there comes a finite number of possible process IDs (PIDs) for all applications to
share," rare for one process to take them all, but "some users were experiencing resource
starvation due to this type of behavior. So in Kubernetes 1.14, we introduced an enhancement to
mitigate the risk of a single pod monopolizing all of the PIDs available."

`:12-16`, under *Can You Spare Some PIDs?*, is the failure mode. `:14` locates it in clusters
"where testing is taking place," so "some wildly non-production-ready activity is happening."
`:16` describes the shape: "something akin to a fork bomb taking place inside a node," resources
eroding under "some zombie-like process that continually spawns children," other workloads getting
"bumped in favor of this inflating balloon of wasted processing power." Two consequences, one
inside the Pod and one across the cluster: other processes "on the same pod being starved of their
needed PIDs," and a node failing so that "a replica of that pod is scheduled to a new machine where
the process repeats across your entire cluster."

`:18-22`, under *Fixing the Problem*, is the announcement, and it announces two things. The first,
at `:20`: "in Kubernetes 1.14, we have added a feature that allows for the configuration of a
kubelet to limit the number of PIDs a given pod can consume." Then the worked example, which is the
only arithmetic in the post: "If that machine supports 32,768 PIDs and 100 pods, one can give each
pod a budget of 300 PIDs to prevent total exhaustion of PIDs." Overcommit is allowed "with some
additional risks." The claim: "Either way, no one pod can bring the whole machine down. This will
generally prevent against simple fork bombs from taking over your cluster."

The second, at `:22`, is scoped smaller and stated as unfinished. Limiting one Pod "does not ensure
if all pods on the machine can protect the node, and the node agents themselves from falling over,"
so the release also carries "a feature in this release in alpha form that provides isolation of
PIDs from end user workloads on a pod from the node agents (kubelet, runtime, etc.)." The admin can
"reserve a specific number of PIDs--similar to how one reserves CPU or memory today--and ensure
they are never consumed by pods on that machine." And then the forecast, which is the sentence this
exercise is built around: "Once that graduates from alpha, to beta, then stable in future releases
of Kubernetes, we'll have protection against an easily starved Linux resource."

`:24` links the v1.14.0 release tag. `:26-28` points at SIG Node. `:30-31` is the author bio. There
is nothing else. No flag is named, no configuration key is named, no default is stated, and neither
feature is given a name a reader could search for.

**As it runs now** — the post is still in the tree twice: once as a blog post, and once as the
documentation page it was turned into. Reading the two side by side is most of the work here,
because the second one is where the numbers, the keys and the caveats live, and it disagrees with
the rest of the pin about two of them.

**The post is now a documentation page.** `concepts/policy/pid-limiting.md` is 111 lines and opens
at `:11` with `{{< feature-state for_k8s_version="v1.20" state="stable" >}}`. Two of its paragraphs
are this post's two announcement paragraphs, lightly edited. Post `:20` becomes `:37-44`; post
`:22`'s first sentence becomes `:46-48`. The page then adds what the post left out — where the
setting lives, what the reservation flag is called, how eviction relates to it — and closes at
`:108-109` with "For historical context, read [Process ID Limiting for Stability Improvements in
Kubernetes 1.14]". The post was not summarised and it was not superseded: it was rewritten into the
documentation tree and is now cited from there as its own history.

**Every number in the post's worked example was replaced, and the post's node capacity became a
warning.** The post at `:20` reasons from 32,768 PIDs, 100 pods and a 300-PID budget. The page at
`:37-44` reasons from the same shape and none of the same figures: "if your node's host OS is set to
use a maximum of `262144` PIDs and expect to host less than `250` Pods, one can give each Pod a
budget of `1000` PIDs." A factor of eight on the node, two and a half on the pods, more than three
on the budget. The post's own starting figure has not vanished, though — it moved up the page and
changed sides. `:32-35` is a note: "On certain Linux installations, the operating system sets the
PIDs limit to a low default, such as `32768`. Consider raising the value of
`/proc/sys/kernel/pid_max`." The number the post used to demonstrate that the arithmetic works is
now the number you are told to fix.

**The page's link back to the post is not a path the pinned tree serves.** `:109` points at
`/blog/2019/04/15/process-id-limiting-for-stability-improvements-in-kubernetes-1.14/`. The post
file is `2019/pid-limiting.md` and its frontmatter has no `slug:`, so the path built from the
filename is `/blog/2019/04/15/pid-limiting/` — which is what this exercise's *Post* line above uses,
and what the manifest records. Searched across the whole checkout, the long string occurs exactly
once: on the line that links it. Whether the live site papers over it with a redirect is not
something the pin can tell you; what the pin can tell you is that nothing in the tree renders there.

**Both features climbed exactly the ladder the post hoped for, and then both gates were deleted.**
The forecast at `:22` — alpha, then beta, then stable — is not a hope that went unmet or a plan that
was quietly dropped. It happened, on that order, and the gate files record it release by release
before declaring themselves removed. The tables are in *The ladder* below.

**The feature the post says was "added" in v1.14 had been in the tree since v1.10.**
`SupportPodPidsLimit` reads `alpha` with `defaultValue: false` from v1.10 to v1.13 — four releases
before this post. What v1.14 did was flip it on: the same gate's next row is `beta` with
`defaultValue: true`. "We have added a feature" at `:20` is the sentence a release announcement
writes when a gate defaults to true, and it is not what happened in the tree. The other half of the
post is precise where this half is loose: `:22` says the node-level feature is arriving "in this
release in alpha form", and `SupportNodePidsLimit` is indeed `alpha` for exactly v1.14.

**At the pin, the Pod-level limit is off.** `kubelet-config.v1beta1.md:1121-1125` gives
`podPidsLimit int64`, "podPidsLimit is the maximum number of PIDs in any pod", **Default: -1**, and
the worked sample configuration at `kubelet-config-file.md:234` writes `"podPidsLimit": -1`
explicitly. `kubelet.md:683-684` says the same for the flag: `--pod-max-pids int  Default: -1`, and
"If -1, the kubelet defaults to the node allocatable pid capacity." So a cluster brought up by
`kubeadm` and left alone gives every Pod the whole node's PID budget, which is the state the post
opens by describing. The feature is stable, ungated, documented, and not in effect until someone
sets a number.

**`pid.available` is an eviction signal that is in nobody's defaults, and the pin cannot agree on
how many defaults there are.** `node-pressure-eviction.md:80` defines it as
`node.stats.rlimit.maxpid` minus `node.stats.rlimit.curproc`, and `:282` maps it to the
`PIDPressure` node condition, which `node-status.md:50` describes as "`True` if pressure exists on
the processes." The default thresholds are where it stops. `node-pressure-eviction.md:234-241`
lists six of them — `memory.available`, `nodefs.available`, `imagefs.available`,
`nodefs.inodesFree`, `imagefs.inodesFree`, and a Windows-specific `memory.available` — and
`kubelet-config.v1beta1.md:1239-1243` lists four, keeping `nodefs.inodesFree` but dropping
`imagefs.inodesFree` and the Windows figure. Neither list contains `pid.available`. The concept
page is candid about what that leaves you at `:93-95`: "even with the hard eviction policy, if the
number of PIDs growing very fast, node can still get into unstable state by hitting the node PIDs
limit. Eviction signal value is calculated periodically and
does NOT enforce the limit." Two lists that disagree about their own length is the kind of question
`configz` settles in one command, and *Do* asks it.

**The pin also disagrees with itself about whether `pid` is a reservable resource at all.** Three
places say it is. `pid-limiting.md:69-71`: use "the parameter `pid=<number>` in the
`--system-reserved` and `--kube-reserved` command line options to the kubelet."
`reserve-compute-resources.md:82-84` and `:113-115`, once for each half: "In addition to `cpu`,
`memory`, and `ephemeral-storage`, `pid` may be specified to reserve the specified number of process
IDs." And `SupportNodePidsLimit`'s own gate body says it too. One place says it is not.
`kubelet-config.v1beta1.md:1454`, on `systemReserved`: "Currently only cpu and memory are
supported." `:1465`, on `kubeReserved`: "Currently cpu, memory and local storage for root file
system are supported." The config API reference is the schema the kubelet parses, so this is not a
tie; but it is also a doc comment, and a doc comment can be stale in either direction. The kubelet
answers it, and *Do* makes it answer.

**Two of the pin's keys are capitalised as if they were Go fields.** `pid-limiting.md:82` tells you
to "set `PodPidsLimit` in the kubelet configuration file". The key in the file is `podPidsLimit`
(`kubelet-config.v1beta1.md:1121`). The same drift sits eight lines from the eviction-defaults list
that this exercise already reads: `node-pressure-eviction.md:248` writes "the kubelet config
MergeDefaultEvictionSettings", where `kubelet-config.v1beta1.md:1299` has
`mergeDefaultEvictionSettings`. Both pages are prose pages naming a YAML key, and both reached for
the exported Go identifier instead. This matters more here than a typo usually does, because the
kubelet does not reject unknown keys the way a schema-validated API object would; *Do* checks what
happens when you paste the page's spelling.

**The same sentence recommends a deprecated flag first.** `pid-limiting.md:81-83` offers two ways
to set the limit and puts the flag ahead of the file: "you can specify the command line parameter
`--pod-max-pids` to the kubelet, or set `PodPidsLimit` in the kubelet configuration file."
`kubelet.md:683-684` carries the standard appended sentence on that flag: "(DEPRECATED: This
parameter should be set via the config file specified by the Kubelet's --config flag." So one
sentence gets both of its two halves wrong in two different ways — the recommended option is
deprecated and the alternative is misspelled.

**The reservation example is written in the flag's notation inside the config file's map.**
`reserve-compute-resources.md:74`, under a bullet labelled **KubeletConfiguration Setting**, gives
`kubeReserved: {}` with "Example value `{cpu: 100m, memory: 100Mi, ephemeral-storage: 1Gi,
pid=1000}`", and `:104` repeats it verbatim for `systemReserved`. Three entries use `:` and the
fourth uses `=`. The `=` form is not invented: it is the flag's form, which `kubelet.md:494` and
`:858` both declare as `<comma-separated 'key=value' pairs>`, and which the config API's own doc
comment reaches for as well at `:1452` ("a set of ResourceName=ResourceQuantity (e.g.
cpu=200m,memory=150G)"). What has happened is that the flag's notation leaked into a YAML map
literal, twice, on the page whose whole subject is node reservation.

**And the node condition the second feature drives is not implemented on Windows.**
`windows/intro.md:157`, in a list of what a Windows kubelet does not do: "The `PIDPressure`
Condition is not implemented." The line above it, `:151`, adds that "Eviction by using
`--enforce-node-allocable` is not implemented" — with the flag misspelled, missing its `t`. The
post's second feature is a Linux resource protected by a Linux mechanism, which `:22` says outright
when it calls it "an easily starved Linux resource," and seven years on the other node platform
still reports nothing about it.

**What this exercise does not cover, and where it lives** — how a kubelet's configuration is
changed at all belongs to [the dynamic kubelet configuration
exercise](../2018/05-dynamic-kubelet-configuration.md): `--config`, the `--config-dir` drop-in
directory and the flag that has to be added by hand to turn it on, the pin's two contradictory
statements about drop-in ordering, and the census of how many kubelet flags carry the same
`DEPRECATED` sentence. This exercise borrows that scaffolding rather than rebuilding it, and *Do*
says where to get it if you have not done that exercise yet. Node allocatable as a whole — what
`capacity` minus reservations minus eviction thresholds actually produces, and the
`enforceNodeAllocatable` cgroup machinery at `reserve-compute-resources.md:86-88` and `:117-119` —
is read here only where `pid` is involved. The cgroup interface the limit is finally written to,
and the difference between the v1 and v2 hierarchies, is a subject a later year's post owns; this
exercise reads `pids.max` from inside a container without explaining where that file comes from.

**The diff, and why** — four of the seven cases, and one of them in its purest form yet.

**Retired by being agreed with.** This is the case the post's last sentence sets up and the pin
closes. `:22` says: "Once that graduates from alpha, to beta, then stable in future releases of
Kubernetes, we'll have protection against an easily starved Linux resource." The gate file for that
feature records `alpha` at v1.14, `beta` at v1.15, `stable` at v1.20, and then `removed: true` — the
forecast, in order, with no detour, followed by the deletion of the switch that made it optional.
Other exercises in this archive read gates that stalled, reversed, or outlived their features. This
one reads a gate that did exactly what was predicted and was thrown away for it. The post is
not wrong and it is not still needed; it has been agreed with, and the agreement is why nothing
in the current tree needs the post to explain it.

**Still right.** The diagnosis at `:14-16` did not need editing to become documentation. The pin's
page carries it forward at `:37-48` and adds nothing to the mechanism, only to the numbers. And the
weaker claim at `:22` — that limiting a Pod protects other Pods but not the node — is still the
pin's own framing, split across two headings (`## Pod PID limits`, `## Node PID limits`) that exist
because the distinction the post drew is the distinction the feature still has.

**Wrong when it was published.** "In Kubernetes 1.14, we have added a feature" at `:20` describes
something that had been in the tree, behind a gate, since v1.10. Nothing was added in v1.14 except
a default. This is the ordinary shape of the mistake in release-announcement posts, and it is worth
naming because the same post gets the other half right in the very next paragraph: `:22` says
"in this release in alpha form" about a feature whose gate really does start at v1.14.

**Overtaken by stasis.** Three things have not moved and one of them is the post's whole subject.
`podPidsLimit` still defaults to `-1`, so the fork bomb at `:16` still runs to the node's limit on a
cluster nobody has configured. `pid.available` is still absent from every default eviction
threshold list the pin publishes, so the second line of defence is also off until asked for. And
`PIDPressure` is still unimplemented on Windows nodes. The features shipped, graduated and lost
their gates; the defaults they would need in order to matter never changed. That is the reading this
exercise is for, and it is not visible from either the post or the page — only from a cluster.

**The ladder** — two gates, one per feature, both removed. Neither is transcribed anywhere else in
the archive.

`SupportPodPidsLimit`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.10 – v1.13 |
| beta | `true` | — | v1.14 – v1.19 |
| stable | `true` | — | v1.20 – v1.23 |

`SupportNodePidsLimit`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.14 – v1.14 |
| beta | `true` | — | v1.15 – v1.19 |
| stable | `true` | — | v1.20 – v1.23 |

Both files declare `removed: true` and carry the heading `# Removed from Kubernetes`. Neither
declares `former_titles`. Neither declares `lockToDefault` on any stage, which is why the `locked`
column is empty rather than `false`. Both also carry `_build: list: never` and `render: false`,
so neither page is published at all: they exist in the tree as a record and nowhere on the site.

Four readings.

**The post sits on a different rung of each ladder, in the same release.** v1.14 is `beta` and
default-`true` for `SupportPodPidsLimit` and `alpha` and default-`false` for
`SupportNodePidsLimit`. The post says as much at `:20` and `:22` without naming either gate, and
the two sentences are doing different jobs: one announces a default, the other announces an
experiment. A reader in 2019 with only the post to go on could act on the first and not the second,
and the post gives them no name to switch the second on with.

**The node-level gate had the shortest possible alpha.** `fromVersion: 1.14`, `toVersion: 1.14`:
one release. The Pod-level gate had four. The feature that the post presents as the tentative one,
the one whose graduation it hopes for, is the one that graduated fastest.

**The ladders converge and then run four more releases.** Both reach `stable` at v1.20 and both
sit there through v1.23 before the files declare themselves removed. Four releases of a stable,
default-`true`, `lockToDefault`-less gate is four releases in which the switch existed and turning
it off was possible but pointless. The gate outlived the decision by a full year.

**And what the gates gated is not what you now set.** Neither gate name appears in any command a
reader would run at the pin: the controls are `podPidsLimit` in the kubelet's configuration file and
`pid` inside `kubeReserved` or `systemReserved`. The gate is the thing that got removed; the
setting is the thing that stayed, and the setting is off by default. *Do* asks the kubelet about
both gate names first, precisely so the reader sees that the answer is nothing, and then goes to
the settings.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair): a control-plane node at
`10.10.10.130` and a worker at `10.10.10.131`, brought up with [the five provision
steps](../../strands/lab-topologies.md#provision). Two nodes are not a convenience here, they are
the subject. `pid-limiting.md:61-65` carries a caution — "the limit that applies to a Pod may be
different depending on where the Pod is scheduled. To make things simple, it's easiest if all Nodes
use the same PID resource limits and reservations" — and that is a claim about a cluster with more
than one node, which a single-node topology cannot show. The limit is set on the worker only, so
the same Pod manifest lands under a limit on one node and no limit on the other, which is exactly
what the caution says will happen. Everything is driven from the control-plane host; the worker is
reached over `ssh zain@10.10.10.131` for the kubelet's own files.

What the topology cannot show is a real fork bomb. On a 2048MB worker, a process that spawns
children without bound will take the node's memory before it takes the node's PIDs, and a node that
has to be power-cycled has stopped being an instrument. So the spawning in *Do* is bounded: a fixed
count of backgrounded `sleep` processes, chosen to sit above the limit that gets set and far below
anything the kernel would notice. That means the exercise demonstrates the enforcement boundary and
not the failure the post opens with. The starvation at `:16` — a node degrading, workloads getting
bumped, a replica rescheduling and repeating it elsewhere — stays a description you read rather than
a thing you watch, and it is worth being clear that the two are different. What you can watch is
the moment `fork` starts returning an error, which is the mechanism the whole feature consists of.

**Do**

1. Get the two numbers the post's arithmetic needs, from your own nodes rather than from the page.
   `pid_max` is the node's whole supply; `allocatable.pods` is the divisor:

   ```sh
   cat /proc/sys/kernel/pid_max
   ssh zain@10.10.10.131 'cat /proc/sys/kernel/pid_max'
   kubectl get nodes -o custom-columns='NODE:.metadata.name,CAP:.status.capacity.pods,ALLOC:.status.allocatable.pods'
   python3 -c 'p=int(open("/proc/sys/kernel/pid_max").read()); print("pid_max", p, "| post divisor 100 ->", p//100, "| page divisor 250 ->", p//250)'
   ```

2. Ask both kubelets whether either gate the post announces still exists. Two names, and the
   effective feature-gate map for comparison:

   ```sh
   sudo kubelet --feature-gates=SupportPodPidsLimit=true --help 2>&1 | head -3
   sudo kubelet --feature-gates=SupportNodePidsLimit=true --help 2>&1 | head -3
   kubectl get --raw "/api/v1/nodes/k8s-worker/proxy/configz" \
     | python3 -c 'import sys,json; print("featureGates:", json.load(sys.stdin)["kubeletconfig"].get("featureGates"))'
   ```

3. Read the effective Pod limit on both nodes, and check whether the flag the page recommends first
   is set on either:

   ```sh
   for N in k8s-cp k8s-worker; do echo "== $N"; kubectl get --raw "/api/v1/nodes/$N/proxy/configz" \
     | python3 -c 'import sys,json; c=json.load(sys.stdin)["kubeletconfig"]; print("  podPidsLimit:", c.get("podPidsLimit")); print("  kubeReserved:", c.get("kubeReserved")); print("  systemReserved:", c.get("systemReserved"))'; done
   ps -o args= -C kubelet | tr ' ' '\n' | grep -- '--pod-max-pids' || echo "--pod-max-pids is not set"
   ```

4. Establish the baseline the post describes: a Pod on the worker with no limit on it. Read the
   cgroup's own view of its ceiling from inside the container, then start more processes than any
   limit you are about to set:

   ```sh
   kubectl run pidtest --image=busybox --restart=Never \
     --overrides='{"spec":{"nodeName":"k8s-worker"}}' --command -- sleep 3600
   kubectl wait --for=condition=Ready pod/pidtest --timeout=90s
   kubectl exec pidtest -- sh -c 'cat /sys/fs/cgroup/pids.max 2>/dev/null || cat /sys/fs/cgroup/pids/pids.max'
   kubectl exec pidtest -- sh -c 'i=0; while [ $i -lt 150 ]; do sleep 300 & i=$((i+1)); done; sleep 2; echo asked=150; cat /sys/fs/cgroup/pids.current' 2>&1 | tail -6
   ```

5. Set the Pod limit on the worker only, through the drop-in directory. If the second command
   reports that `--config-dir` is unset, [the dynamic kubelet configuration
   exercise](../2018/05-dynamic-kubelet-configuration.md) puts the flag in place; this exercise
   assumes it is already there and only checks:

   ```sh
   ssh zain@10.10.10.131 'sudo mkdir -p /etc/kubernetes/kubelet.conf.d && \
     printf "apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\npodPidsLimit: 100\n" \
     | sudo tee /etc/kubernetes/kubelet.conf.d/20-pids.conf'
   ssh zain@10.10.10.131 'sudo grep -o -- "--config-dir=[^ ]*" /var/lib/kubelet/kubeadm-flags.env || echo "--config-dir is not set"'
   ssh zain@10.10.10.131 'sudo systemctl restart kubelet; sleep 20; systemctl is-active kubelet'
   kubectl get --raw "/api/v1/nodes/k8s-worker/proxy/configz" \
     | python3 -c 'import sys,json; print("podPidsLimit:", json.load(sys.stdin)["kubeletconfig"]["podPidsLimit"])'
   ```

6. Run the same Pod again on the same node and watch the ceiling arrive. The Pod manifest has not
   changed; nothing about the Pod asked for this:

   ```sh
   kubectl delete pod pidtest --wait=true
   kubectl run pidtest --image=busybox --restart=Never \
     --overrides='{"spec":{"nodeName":"k8s-worker"}}' --command -- sleep 3600
   kubectl wait --for=condition=Ready pod/pidtest --timeout=90s
   kubectl exec pidtest -- sh -c 'cat /sys/fs/cgroup/pids.max 2>/dev/null || cat /sys/fs/cgroup/pids/pids.max'
   kubectl exec pidtest -- sh -c 'i=0; while [ $i -lt 150 ]; do sleep 300 & i=$((i+1)); done; sleep 2; echo asked=150; cat /sys/fs/cgroup/pids.current' 2>&1 | tail -6
   ```

7. Now the caution at `pid-limiting.md:61-65`, which is the reason this is a two-node exercise. Put
   the identical Pod on the control plane and read the same file:

   ```sh
   kubectl run pidtest-cp --image=busybox --restart=Never \
     --overrides='{"spec":{"nodeName":"k8s-cp","tolerations":[{"operator":"Exists"}]}}' --command -- sleep 3600
   kubectl wait --for=condition=Ready pod/pidtest-cp --timeout=90s
   kubectl exec pidtest-cp -- sh -c 'cat /sys/fs/cgroup/pids.max 2>/dev/null || cat /sys/fs/cgroup/pids/pids.max'
   kubectl get pods -o custom-columns='POD:.metadata.name,NODE:.spec.nodeName'
   ```

8. Settle the capitalisation. Write the key as `pid-limiting.md:82` instructs it, `PodPidsLimit`,
   into a second drop-in that sorts after the first, and find out whether the kubelet reads it,
   ignores it, or refuses to start:

   ```sh
   ssh zain@10.10.10.131 'printf "apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nPodPidsLimit: 50\n" \
     | sudo tee /etc/kubernetes/kubelet.conf.d/30-capital.conf'
   ssh zain@10.10.10.131 'sudo systemctl restart kubelet; sleep 20; systemctl is-active kubelet'
   ssh zain@10.10.10.131 'sudo journalctl -u kubelet --no-pager -n 15 | tail -15'
   kubectl get --raw "/api/v1/nodes/k8s-worker/proxy/configz" \
     | python3 -c 'import sys,json; print("podPidsLimit:", json.load(sys.stdin)["kubeletconfig"]["podPidsLimit"])'
   ssh zain@10.10.10.131 'sudo rm -f /etc/kubernetes/kubelet.conf.d/30-capital.conf && sudo systemctl restart kubelet; sleep 20; systemctl is-active kubelet'
   ```

9. Count the default hard eviction thresholds, since the pin gives two different lists, and look for
   `pid.available` in the answer. Then read the condition it would drive:

   ```sh
   kubectl get --raw "/api/v1/nodes/k8s-worker/proxy/configz" \
     | python3 -c 'import sys,json; e=json.load(sys.stdin)["kubeletconfig"].get("evictionHard") or {}; [print("  ", k, "=", e[k]) for k in sorted(e)]; print("count:", len(e), "| pid.available present:", "pid.available" in e)'
   kubectl get node k8s-worker -o json \
     | python3 -c 'import sys,json; [print(c["type"], c["status"], c["reason"]) for c in json.load(sys.stdin)["status"]["conditions"]]'
   ```

10. The reservation half, and the one place the pin contradicts itself about the schema. Try the
    page's example notation first, literally, then the notation YAML requires. A bad drop-in can
    stop the kubelet, so the last command in each block is the one that tells you:

    ```sh
    ssh zain@10.10.10.131 'printf "apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nkubeReserved:\n  cpu: 100m\n  memory: 100Mi\n  pid=1000\n" | sudo tee /etc/kubernetes/kubelet.conf.d/40-reserve.conf'
    ssh zain@10.10.10.131 'sudo systemctl restart kubelet; sleep 20; systemctl is-active kubelet; sudo journalctl -u kubelet --no-pager -n 8 | tail -8'
    ssh zain@10.10.10.131 'printf "apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nkubeReserved:\n  cpu: \"100m\"\n  memory: \"100Mi\"\n  pid: \"1000\"\n" | sudo tee /etc/kubernetes/kubelet.conf.d/40-reserve.conf'
    ssh zain@10.10.10.131 'sudo systemctl restart kubelet; sleep 20; systemctl is-active kubelet; sudo journalctl -u kubelet --no-pager -n 8 | tail -8'
    kubectl get node k8s-worker -o json \
      | python3 -c 'import sys,json; s=json.load(sys.stdin)["status"]; print("capacity:", s["capacity"]); print("allocatable:", s["allocatable"])'
    kubectl get --raw "/api/v1/nodes/k8s-worker/proxy/configz" \
      | python3 -c 'import sys,json; print("kubeReserved:", json.load(sys.stdin)["kubeletconfig"].get("kubeReserved"))'
    ```

**Expect**

Step 1 is the only place the post's arithmetic can be checked, and the number that matters is your
own `pid_max`. Record it. If it reads `32768`, the note at `pid-limiting.md:32-35` is describing
your node and not a hypothetical one, and the post's own worked example is your cluster's real
budget. If it reads in the millions, as most current distributions ship it, then the page's `262144`
is the conservative figure and the divisor is what constrains you rather than the supply. Either way
the divisor is yours to compare against theirs: whatever `allocatable.pods` reports on an untouched
node, it is neither the post's 100 nor the page's 250.

Step 2 should fail twice. Both gates are `removed: true` at the pin, so the kubelet should reject
each name before it prints any help at all. Record the exact wording, because it names the gate back
to you and that is the clearest evidence available that the switch the post's second feature waited
on no longer exists. The `featureGates` map from `configz` is the other half of the same answer: it
carries whatever your cluster set explicitly, and neither of these two names can be among them.

Step 3 should report `podPidsLimit: -1` on both nodes, `kubeReserved` and `systemReserved` empty,
and no `--pod-max-pids` on either command line. That is a cluster in the state the post opens by
describing: the feature is stable and ungated, and nothing is limited. `kubelet.md:683-684` says
`-1` means "the kubelet defaults to the node allocatable pid capacity", so this is not the same as
"no limit" in principle — which is what step 4 checks.

Step 4 is the step whose answer is not predictable from the documentation, and it is the one worth
recording most carefully. `pids.max` inside an unlimited Pod either reads `max`, meaning the cgroup
carries no ceiling at all, or reads a number, meaning the kubelet has written the node's allocatable
PID capacity into it as `kubelet.md:683-684` claims. Those are two different clusters. Whichever you
get, 150 backgrounded `sleep` processes are far below either, so `pids.current` should come back at
roughly 153 and no fork should fail.

Step 5 should report `podPidsLimit: 100` from `configz` and an active kubelet. If `--config-dir`
turns out not to be set, the drop-in you just wrote is inert and every reading after this point will
be the same as before it — which is a real outcome and not a mistake, but you will want the flag in
place before continuing.

Step 6 is the enforcement boundary. `pids.max` should now read `100`, from a Pod whose manifest is
byte-identical to step 4's: the limit came from the node, which is the whole point of
`pid-limiting.md:55-59` ("rather than defining a Pod's resource limit in the `.spec` for a Pod, you
configure the limit as a setting on the kubelet"). Asking for 150 processes inside a ceiling of 100
should fail partway, `pids.current` should stop at `100`, and the shell should print a fork failure
for each attempt past it. Record what busybox says; that message is the entire user-visible surface
of the feature, and `pid-limiting.md:97-98` describes it in the abstract — "workload will start
experiencing failures when trying to get a new PID" — without ever showing it.

Step 7 should show the unlimited value from step 4 on the control-plane Pod while the worker's Pod
sits at `100`. Two Pods, one manifest apart from their node, two different ceilings. That is
`pid-limiting.md:61-65` reproduced, and it is also the reason the same page's advice is to keep
every node the same: there is no field on the Pod that records which ceiling it got, and nothing in
`kubectl describe pod` will tell you either.

Step 8 has three possible answers and the pin does not say which. `configz` may report `100`,
meaning the kubelet parsed the file and silently ignored a key it did not recognise; or `50`,
meaning it is more permissive about case than the config API suggests; or the kubelet may refuse to
start, meaning the drop-in is rejected as invalid and `systemctl is-active` reports a failure with
the reason in the journal. Record which. If it is the first, then `pid-limiting.md:82`'s spelling
is a silent no-op, and a reader who follows that page exactly gets a cluster that looks configured
and is not — which is the most expensive of the three outcomes and the least visible.

Step 9 answers the disagreement about the default thresholds directly: the count is either four, as
`kubelet-config.v1beta1.md:1239-1243` says, or six, as `node-pressure-eviction.md:234-241` says, or
zero if your kubelet was handed an explicit `evictionHard`. `pid.available` should be absent in
every case. The node's conditions should show `PIDPressure` present and `False` — the signal is
wired all the way through to a condition the scheduler can taint on, and it is not being watched
against any threshold. `PIDPressure` reading `False` because nothing is configured looks exactly
like `PIDPressure` reading `False` because everything is fine.

Step 10's first block should stop the kubelet. `pid=1000` on its own line inside a block mapping is
not valid YAML, so the drop-in cannot be parsed at all, and `systemctl is-active` should report
something other than `active` with a parse error in the journal. That is
`reserve-compute-resources.md:74` and `:104` tried literally, and it is the one defect in this
exercise that costs a reader a node rather than a misunderstanding. The second block is the schema
question: if the kubelet comes back up with `kubeReserved` carrying a `pid` key in `configz`, then
`pid-limiting.md:69-71` is right and `kubelet-config.v1beta1.md:1454` is a stale doc comment; if it
rejects the key, the doc comment is the truth and three pages of the pin are wrong. Then look at the
Node's `capacity` and `allocatable`: neither map has a `pid` entry for a reservation to subtract
from, so whatever the kubelet does with the number, it does not surface it the way `cpu` and
`memory` reservations surface. The reservation is real inside the kubelet and invisible from the
API, which is why the post's `:22` promise — "ensure they are never consumed by pods on that
machine" — has no `kubectl` command that confirms it.
**Read on** — four questions the pinned tree can answer, and one it cannot.

1. `pid-limiting.md:11` marks the page `stable` at v1.20, which is the release both gates reached
   `stable`. Read `:37-44` against post `:20` clause by clause. Three numbers change and one
   comparison flips direction ("less than `250` Pods" where the post says "100 pods"), but the
   sentence to look at is the last one: the post says the feature "will generally prevent against
   simple fork bombs from taking over your cluster" and the page says it "helps to prevent simple
   fork bombs from affecting operation of an entire cluster". Then do the same for post `:22`
   against `:46-48`, where one sentence became three. Decide which of the two rewrites weakened a
   claim and which only split one.

2. `reserve-compute-resources.md:96-100` says the kubelet "**does not** create
   `kubeReservedCgroup`" and "will fail to start if an invalid cgroup is specified", and `:86-88`
   tells you to set `kubeReservedCgroup` and add `kube-reserved` to `enforceNodeAllocatable` in
   order to enforce the reservation rather than merely declare it. Work out from those three
   passages what a reader who wants the `pid` reservation *enforced*, rather than merely accounted,
   has to build first — and note that nothing on the page says the reservation does anything at all
   without it.

3. `node-pressure-eviction.md:243-250` says the default hard eviction thresholds "will only be set
   if none of the parameters is changed", and that changing one sets the others to zero unless
   `mergeDefaultEvictionSettings` is true. Decide what that means for a reader who wants to add a
   `pid.available` threshold to a `kubeadm` cluster: how many values they now have to write, and
   which page tells them what those values should be.

4. `windows/intro.md:157` says `PIDPressure` is not implemented and `:151` says eviction by
   `--enforce-node-allocable` is not implemented, spelling the flag without its `t`.
   `kubelet.md:277` has the real name. Check whether the misspelling appears anywhere else in the
   tree, and whether the working name appears anywhere on the Windows page.

5. The unanswerable one. The pinned tree does not say why `podPidsLimit` still defaults to `-1`
   seven years after the feature reached stable, when the whole argument of the post is that the
   unlimited default is the problem. The gate went to `stable` and then away, the page went to
   `stable`, and the hazard the post opens with stayed exactly where it was. Whether that is a
   compatibility promise, an admission that no single number is right for every node, or simply
   nobody's ticket, the tree does not record. The page at `:63-64` gives the only hint — "it's
   easiest if all Nodes use the same PID resource limits" — which is advice to an administrator,
   not a reason for a default.

**Teardown** — undo the node's files before the objects, because a worker whose kubelet will not
start is a worker that cannot delete a Pod for you. A cluster left with `podPidsLimit: 100` on one
node and not the other is not broken, but it is not what the next exercise expects either, and the
difference is invisible from `kubectl`.

```sh
ssh zain@10.10.10.131 'sudo rm -f /etc/kubernetes/kubelet.conf.d/20-pids.conf /etc/kubernetes/kubelet.conf.d/30-capital.conf /etc/kubernetes/kubelet.conf.d/40-reserve.conf'
ssh zain@10.10.10.131 'sudo systemctl restart kubelet; sleep 20; systemctl is-active kubelet'
kubectl get --raw "/api/v1/nodes/k8s-worker/proxy/configz" \
  | python3 -c 'import sys,json; c=json.load(sys.stdin)["kubeletconfig"]; print("podPidsLimit:", c.get("podPidsLimit"), "| kubeReserved:", c.get("kubeReserved"))'
kubectl delete pod pidtest pidtest-cp --ignore-not-found
kubectl get nodes -o custom-columns='NODE:.metadata.name,READY:.status.conditions[?(@.type=="Ready")].status'
```

The `--config-dir` flag in `/var/lib/kubelet/kubeadm-flags.env` is left in place: it was not added
by this exercise, it points at a directory that is now empty, and an empty drop-in directory changes
nothing. If the kubelet does not come back after the first two commands, the drop-in directory is
the only thing this exercise touched on the node, so an empty directory and a restart is the whole
recovery.
