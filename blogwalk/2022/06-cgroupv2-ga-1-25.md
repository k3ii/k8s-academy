<a id="cgroupv2-ga-1-25"></a>

# Fifteen of this post's twenty-three bullets sit on the concept page four years later, word for word, and the eight that do not are the whole of this exercise: a Go package version, a Node.js release line, and a marker deprecating the cgroup version the post was written to replace

**Post** — [Kubernetes 1.25: cgroup v2 graduates to GA](https://kubernetes.io/blog/2022/08/31/cgroupv2-ga-1-25/),
2022-08-31.

7,689 bytes, 159 lines, two authors: David Porter of Google and Mrunal Patel of Red Hat. Sixth of
the thirteen `walk` verdicts in 2022, and the first of them that announces 1.25 rather than 1.24.

**As written**

A graduation announcement with almost no announcement in it. The post spends three lines, `:11-13`,
saying cgroup v2 is stable in 1.25 and then turns into instructions. `:15-29` explains what cgroups
are. `:31-58` explains what cgroup v2 is and lists six improvements. `:60-98` tells you how to get
it: six distributions that ship it by default, five requirements to meet, and a paragraph insisting
that the kubelet and the container runtime both use the systemd cgroup driver so that there is a
single cgroup manager on the machine. `:100-123` is the migration section, and it is the one that
matters here.

That section makes a promise and then qualifies it. `:106-108`: *In most cases, you won't see a
difference in the user experience when you switch to using cgroup v2 unless your users access the
cgroup file system directly.* Then `:110-112` widens the qualification to programs — applications
that read the cgroup filesystem *either on the node or from inside a container* must be updated —
and `:114-123` gives the list of who those are: third-party monitoring and security agents, cAdvisor
before v0.43.0, and three families of Java runtime named down to the patch version.

The post does not keep its own how-to-check instructions. `:78` sends you to
`/docs/concepts/architecture/cgroups/#check-cgroup-version` instead, and that page is where the
whole post ended up.

**As it runs now**

`concepts/architecture/cgroups.md` at the pin is 148 lines and is, in its bones, this post. Four of
its lists are the post's four lists. Step 8 measures the overlap mechanically: the post has **23**
bullets across those four lists, the page has **26**, and **15** of them are identical once links
and whitespace are normalised away. The improvements list matches five of six — the page writes
*network memory, kernel memory* where the post wrote *network and kernel memory*. The distribution
list matches four of six, the two misses being a lowercased *bullseye* and Ubuntu gaining *22.04+
recommended*. The migration list matches five of eight.

The list that matches *worst* is the requirements list: one bullet of five. It was rewritten from
second person into declarative form — *Your Linux distribution enables cgroup v2 on kernel version
5.8 or later* became two bullets, *OS distribution enables cgroup v2* and *Linux Kernel version is
5.8 or later*; *containerd v1.4 or later* became *containerd v1.4 and later*. Nothing in it changed.
Eleven releases after 1.25, the kernel floor, the two runtime floors and the systemd driver
requirement are the same four facts in different words.

The page is not a copy that was made once. It has been maintained, and what four years of
maintenance added is the interesting part: a manual GRUB route at `:78-83` for enabling cgroup v2 on
a distribution that does not, two new migration bullets at `:109-117`, and a section at `:134-142`
that the post could not have written, marking cgroup v1 deprecated.

**What this exercise does not cover, and where it lives**

The deprecation section is the headline anyone would reach for, and it is already owned. [The one
configuration value this post documents does not parse at the pin, the default it names in
parentheses is not the default any more, and both rows of its cgroups table are void — while three
of its six caveat sentences are now documentation, character for
character](../2021/05-run-nodes-with-swap-alpha.md) cites `cgroups.md:134-142` and the
`failCgroupV1` field in `kubelet-config.v1beta1.md`, and reads the field off a running kubelet. Step
10 here counts how far that field has spread through the tree; it does not re-explain it.

MemoryQoS is the post's only named example of a feature that needs cgroup v2 (`:53-58`), and it
belongs to [Fifteen releases in alpha, beta on the newest release the pin carries, a throttling
formula replaced by a different one, a default factor documented twice with two different answers,
and the `memory.min` this post is built around is now set only by a field the post never
names](../2021/08-qos-memory-resources.md). Nothing here ladders that gate.

Reading cgroup files is lab ground. [Walk from the node's root cgroup down to one container, naming
every level](../../labs/06/15-the-cgroup-tree-under-one-pod.md) maps the tree, and [Membership is a
write to a file](../../labs/00/05-move-a-process-into-a-cgroup.md) explains why a container's
`cgroup.controllers` is empty until a parent delegates downward. This exercise reads three files,
once, to put numbers next to what a language runtime believes; it does not walk anything.

That a pod sees the node's cores rather than its own CPU limit is observed already, from the other
end, in [Measure the marginal pod: what one sidecar costs, four times over, on a node you can
exhaust](../../labs/09/19-what-a-sidecar-costs.md). Step 4 here prints the same number for a
different reason.

**The diff, and why**

*Retired by being agreed with, and then maintained without it.*

Fifteen of the post's twenty-three bullets are on the concept page word for word. The page never
cites the post. Step 9 runs the citation half of the seventh case's test: no page under
`content/en/docs` links this post, and the one file in the entire pinned tree that does is another
blog post, not documentation. The absorption is complete enough that the post's own instructions now
point *into* the page that replaced it — `:78` links
`/docs/concepts/architecture/cgroups/#check-cgroup-version`, and that anchor is still there, at
`cgroups.md:119`. The post is a redirect with a byline.

*Still right, in the list that was rewritten hardest.*

The requirements list scores worst on the word-for-word test and best on the substance test. Kernel
5.8, containerd v1.4, cri-o v1.20, systemd cgroup driver on both the kubelet and the runtime: four
floors set in 2022 and not raised once in eleven releases. Step 1 measures all four against a lab
node. If a requirements list can be reworded from top to bottom without a single threshold moving,
the rewriting was editorial, and the exercise is to notice that a low overlap score does not mean a
change.

*Broke, in the sentence that was most cheerful.*

`:62-64`: *Many Linux distributions are switching to cgroup v2 by default; you might start using it
the next time you update the Linux version of your control plane and nodes!* At the pin that reads
backwards. `cgroups.md:134-142` marks cgroup v1 deprecated as of v1.35 and the kubelet refuses to
start on a v1 node by default. What the post describes as something that might happen to you
incidentally is now the condition for the kubelet booting at all. The field, its default and its
citation belong to the 2021 swap exercise; step 10 measures only how many files in the tree carry
it.

*Right, and then made specific twice by people who hit it.*

The post's escape clause at `:106-108` — no difference *unless your users access the cgroup file
system directly* — survives on the page at `:93-95` as its own thesis. What the page added
underneath it are two bullets naming programs that do exactly that without anyone thinking of it as
accessing the cgroup filesystem. `:109-110`: `uber-go/automaxprocs` must be v1.5.1 or higher.
`:111-117`: Node.js reads cgroup v2 memory limits through libuv only from v20.3.0, the v18 line does
not do it reliably, and a version that misses it *may read the host's total memory instead of the
limit applied to the pod, which can lead to an incorrectly sized heap and out-of-memory (OOM)
terminations*. Neither is a Kubernetes component. Both are what a Go scheduler and a JavaScript heap
sizer do when nobody told them a container is a cgroup. Steps 3 to 6 put the numbers side by side
and then drive the failure the page describes.

**The ladder**

There is no ladder, and that is worth stating rather than skipping. cgroup v2 support never had a
feature gate: it is a property of the kernel the node booted, not a switch in a component, and step
2 confirms it by finding nothing. Of the 487 gate files at the pin, exactly one has `cgroup` in its
name, `KubeletCgroupDriverFromCRI`, and it belongs to the post's third requirement rather than to
cgroup v2 itself — it is why the kubelet may now ask the runtime which driver to use instead of
reading its own setting. Its full ladder, and the four places in the pin that disagree about whether
it is in effect, are in [The project this post announces survives in the pinned documentation as a
tab id, a PNG filename and an AppArmor profile; the runtime it was written to displace has six
migration pages, a glossary entry and a note saying it does not implement CRI at all; and of this
curriculum's two hand-edits to `config.toml` one is gone because two defaults agreed, and the other
is the answer the kubelet now asks for instead of reading its own
setting](../2017/08-containerd-container-runtime-options-kubernetes.md).

What this post has instead of a gate ladder is two stage markers on one page, pointing opposite
ways. `cgroups.md:24` carries `{{< feature-state for_k8s_version="v1.25" state="stable" >}}` — the
line this post was written to announce. `cgroups.md:136` carries `{{< feature-state
for_k8s_version="v1.35" state="deprecated" >}}`, ten releases later, on the other version. A single
concept page holding a stable marker and a deprecated marker for the two halves of the same
migration is the whole arc of this post in two shortcodes.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 vCPU, at `10.10.10.180`. One
node is enough: everything measured here is a property of one kernel, one kubelet and two
containers. The node's memory size matters, though, because step 4 turns on the gap between 4096MB
and a 256Mi limit, so if your guest is sized differently, record its size and expect different
numbers rather than the ones written here. Provision with
[`provision`](../../strands/lab-topologies.md#provision) if the guest is not up.

Two images this curriculum does not otherwise use are needed: `node:20-alpine` and `node:18-alpine`.
The page names release lines, not behaviours, so the only way to check its claim is to run both
lines.

**Do**

1. Measure the post's requirements list against the node. Four floors were set in 2022; check all
   four, and check the thing the page's own one-liner checks.

   ```sh
   ssh zain@10.10.10.180 'stat -fc %T /sys/fs/cgroup/; uname -r; \
     containerd --version; grep -w cgroup2 /proc/mounts'
   ```

2. Look for a switch. cgroup v2 has no feature gate, so the interesting output is an empty one — and
   the node's own version strings are what you will compare the page's markers against.

   ```sh
   kubectl version
   kubectl get nodes -o custom-columns='NODE:.metadata.name,KUBELET:.status.nodeInfo.kubeletVersion,OS:.status.nodeInfo.osImage,RUNTIME:.status.nodeInfo.containerRuntimeVersion'
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' | grep -i cgroup \
     || echo 'no feature gate with cgroup in its name is reported'
   ```

3. Put two Node.js release lines under the same limits. Both pods sleep; every measurement is an
   `exec`, so the container stays alive between steps.

   ```sh
   kubectl create ns cg
   for tag in 20 18; do
   kubectl -n cg apply -f - <<EOF
   apiVersion: v1
   kind: Pod
   metadata:
     name: n$tag
   spec:
     containers:
     - name: n
       image: node:$tag-alpine
       command: ["sleep", "900"]
       resources:
         limits:
           memory: 256Mi
           cpu: 500m
   EOF
   done
   kubectl -n cg wait --for=condition=Ready pod/n20 pod/n18 --timeout=180s
   ```

4. Ask each runtime what it believes about the machine it is on. Three numbers: total memory, the
   heap ceiling V8 derived from it, and the core count.

   ```sh
   for p in n20 n18; do
     echo "== $p"
     kubectl -n cg exec $p -- node -e '
   const v8 = require("v8"), os = require("os");
   const mib = b => (b / 1048576).toFixed(0) + " MiB";
   console.log("version         ", process.version);
   console.log("os.totalmem     ", mib(os.totalmem()));
   console.log("heap_size_limit ", mib(v8.getHeapStatistics().heap_size_limit));
   console.log("os.cpus().length", os.cpus().length);'
   done
   ```

5. Now read what the kernel actually promised those containers. These are the files the post says an
   application must be updated to read.

   ```sh
   for p in n20 n18; do
     echo "== $p"
     kubectl -n cg exec $p -- sh -c \
       'cat /sys/fs/cgroup/memory.max /sys/fs/cgroup/cpu.max; nproc'
   done
   ```

6. Drive the failure the page names. Grow the JS heap until something stops it, and compare what
   stopped it in each pod. The pods themselves survive, because the process being killed is the one
   you exec'd, not the container's `sleep`.

   ```sh
   for p in n20 n18; do
     echo "== $p"
     kubectl -n cg exec $p -- node -e 'const a=[]; for(;;) a.push(new Array(1000000).fill(0));' \
       > /tmp/$p.out 2>&1
     echo "exit $?"
     tail -4 /tmp/$p.out
   done
   kubectl -n cg get pod -o custom-columns='NAME:.metadata.name,RESTARTS:.status.containerStatuses[0].restartCount,READY:.status.containerStatuses[0].ready'
   ```

7. Look at the post's second improvement bullet — *safer sub-tree delegation to containers* — from
   both sides. The container and the node are looking at the same cgroup and will not print the same
   path.

   ```sh
   kubectl -n cg exec n20 -- sh -c \
     'cat /proc/self/cgroup; cat /sys/fs/cgroup/cgroup.controllers'
   ssh zain@10.10.10.180 "sudo find /sys/fs/cgroup -maxdepth 1 -type d -name 'kubepods*'
     sudo find /sys/fs/cgroup/kubepods.slice -type d -name '*.scope' | head -3"
   ```

8. Offline, in a checkout of `kubernetes/website` at the pin. Measure the absorption: pull the four
   lists out of both documents, normalise links and whitespace away, and count what survived
   verbatim.

   ```sh
   cd /path/to/kubernetes/website/content/en
   python3 - <<'PY'
   import re
   def bullets(path, lo, hi):
       out = []
       for l in open(path).read().split("\n")[lo-1:hi]:
           if re.match(r'^\s*[-*] ', l):
               out.append(re.sub(r'^\s*[-*] ', '', l).strip())
           elif l.strip() and out:
               out[-1] += " " + l.strip()
       clean = lambda t: " ".join(
           re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t).replace("`", "").split())
       return [clean(x) for x in out]
   P = "blog/_posts/2022/cgroupv2-ga.md"
   G = "docs/concepts/architecture/cgroups.md"
   lists = [("improvements", (46, 51), (32, 37)),
            ("distributions", (70, 75), (63, 73)),
            ("requirements", (86, 90), (56, 61)),
            ("migration", (116, 123), (101, 117))]
   tp = tg = ts = 0
   for name, (a, b), (c, d) in lists:
       post, page = bullets(P, a, b), bullets(G, c, d)
       same = [x for x in post if x in page]
       tp += len(post); tg += len(page); ts += len(same)
       print("%-14s post %2d  page %2d  identical %2d" % (name, len(post), len(page), len(same)))
       for x in post:
           if x not in page: print("    only in the post:", x[:90])
       for x in page:
           if x not in post: print("    only in the page:", x[:90])
   print("totals: post %d, page %d, identical %d" % (tp, tg, ts))
   PY
   ```

9. Still offline. Run both halves of the citation test on the post, and check that the one link the
   post makes into the documentation still lands.

   ```sh
   grep -rln 'cgroupv2-ga-1-25' --include='*.md' docs \
     || echo 'no page under docs/ links the post'
   grep -rn 'cgroupv2-ga-1-25' --include='*.md' . \
     | grep -v 'blog/_posts/2022/cgroupv2-ga.md'
   grep -n '{#check-cgroup-version}' docs/concepts/architecture/cgroups.md
   sed -n '77,79p' blog/_posts/2022/cgroupv2-ga.md
   ```

10. Last offline step. Read the three things four years of maintenance added to the page, and count
    how far the one field this exercise deliberately does not explain has spread.

    ```sh
    sed -n '78,83p'   docs/concepts/architecture/cgroups.md
    sed -n '109,117p' docs/concepts/architecture/cgroups.md
    sed -n '134,142p' docs/concepts/architecture/cgroups.md
    grep -rl 'ailCgroupV1' --include='*.md' . | sort
    grep -rl 'failCgroupV1' --include='*.md' . | wc -l
    grep -rl 'FailCgroupV1' --include='*.md' . | wc -l
    ```

**Expect**

Step 1 prints `cgroup2fs`, a kernel well clear of 5.8, a containerd well clear of v1.4, and one line
in `/proc/mounts` showing `cgroup2` mounted at `/sys/fs/cgroup` and nothing else mounted there. Read
the mount options on that line before moving on: `nsdelegate` is the kernel option behind the post's
second improvement bullet, and step 7 is about what it does. All four of the post's floors pass, on
a node built four years after the post was written, without anyone having checked.

Step 2 reports a v1.35 server. The metric grep prints the fallback line and nothing else. Read that
result precisely: `/metrics` on the API server lists the gates that component knows about, and a
kubelet-only gate would not appear there in any case — but the zero result is still the right answer
for this post, because cgroup v2 itself has no gate in any component. Compare the server version
against `cgroups.md:136`: v1.35 is exactly the release that page marks cgroup v1 deprecated, so this
cluster is standing on the line. Record `osImage` and `containerRuntimeVersion`; they are the two
things step 1 measured, restated by the node object.

Step 3 leaves both pods Ready inside the timeout, after two image pulls. No requests are set, only
limits, so the kubelet fills requests in from limits and both pods land in the `Guaranteed` QoS
class — which step 7 will read back out of a directory name.

Step 4 prints two version strings, `v20.x` and `v18.x`. `os.totalmem` reports roughly 4096 MiB in
both pods, because it reads `/proc/meminfo` and `/proc/meminfo` is not namespaced — a container
asking the ordinary question gets the node's answer. `os.cpus().length` reports 4 in both, for the
same reason, and that number is the whole of the `automaxprocs` bullet: a Go runtime sizing its
thread pool from it on this pod would build four schedulers to run half a core.

Step 5 prints `268435456` — 256 MiB to the byte — and `50000 100000`, which is 50ms of CPU per 100ms
period, the `500m` limit written the way the kernel writes it. `nproc` still says 4: it reads CPU
affinity, not the quota, so it agrees with `os.cpus().length` and disagrees with `cpu.max`. These
three files are the cgroup v2 API the post tells applications to be updated for. Put them next to
step 4's numbers and note which of the two runtimes, if either, found them.

Step 6 is the step the page's Node.js bullet predicts, so read it carefully and believe your own
output over this paragraph. The failure the page describes is a heap sized from the host's memory
and then killed by the kernel when it outgrows the limit: that shows up as exit 137, with little or
no JavaScript error text, because the process was killed rather than stopped. A runtime that read
the limit instead stops itself first, with V8's `JavaScript heap out of memory` and a stack trace,
at exit 134. If both pods give you the same exit code, that is a result, not a failed step — record
it, and say which code. The pods should stay Ready with zero restarts, because the process the
kernel chose is the exec'd one and not the container's `sleep`; if a restart count moved, the kernel
chose PID 1 instead, and that is worth recording too.

Step 7 prints `0::/` in the container — one line, one hierarchy, and a root that claims to be the
top of the tree. The node prints `/sys/fs/cgroup/kubepods.slice` and paths ending in
`cri-containerd-<id>.scope` underneath it. Same cgroup, two names, and the container's name is the
shorter one because it was handed a namespaced view of a subtree. That is safer sub-tree delegation
to containers as an output rather than a bullet. The `.slice` and `.scope` suffixes are also the
post's third requirement made visible: those are systemd unit names, so the systemd cgroup driver is
in effect, and `cgroup.controllers` inside the pod lists what the kubelet delegated down.

Step 8 prints post 23, page 26, identical 15. Per list: improvements 6 / 6 / 5, distributions 6 / 6
/ 4, requirements 5 / 6 / 1, migration 6 / 8 / 5. The three near-misses are a comma (*network
memory, kernel memory* for *network and kernel memory*), a capital letter (*bullseye* for
*Bullseye*) and a real edit (*Ubuntu (since 21.10, 22.04+ recommended)*). The requirements list
scores 1 of 5 and has not changed a single threshold. The migration list's two page-only bullets are
`automaxprocs` and Node.js — steps 4 to 6 were those two bullets.

Step 9 prints `no page under docs/ links the post`, then exactly one hit elsewhere in the tree, and
it is in a blog post rather than in documentation. The anchor the post sends readers to is alive at
`cgroups.md:119`. So no page of documentation cites this post, and it is not orphaned by neglect —
it is orphaned because the page it points at absorbed it. A post whose only surviving citation is
from another post, and whose content is on a documentation page that never names it, is retired by
agreement.

Step 10 prints the GRUB paragraph, which tells you how to turn on the thing the post assumed your
distribution would turn on for you; the two bullets steps 4 to 6 measured; and the deprecation
section, nine lines, which makes the post's whole framing conditional in the other direction.
`ailCgroupV1` matches six files; `failCgroupV1` matches four and `FailCgroupV1` matches three, so
one file spells it both ways. Do not chase that field here — read the 2021 swap exercise for what it
is and what it does. The point of the count is the shape: one concept page in 2022, six files across
concepts, reference, two upgrade tasks and two release posts by 2026.

**Read on**

1. [The one configuration value this post documents does not parse at the pin, the default it names
   in parentheses is not the default any more, and both rows of its cgroups table are void — while
   three of its six caveat sentences are now documentation, character for
   character](../2021/05-run-nodes-with-swap-alpha.md) — read it straight after step 10. It is the
   other side of the same page: this exercise is about what `cgroups.md` absorbed, that one is about
   what `cgroups.md` grew that no post ever said.

2. [The project this post announces survives in the pinned documentation as a tab id, a PNG filename
   and an AppArmor profile; the runtime it was written to displace has six migration pages, a
   glossary entry and a note saying it does not implement CRI at all; and of this curriculum's two
   hand-edits to `config.toml` one is gone because two defaults agreed, and the other is the answer
   the kubelet now asks for instead of reading its own
   setting](../2017/08-containerd-container-runtime-options-kubernetes.md) — the post's third
   requirement, five years older and with a gate on it. Step 7 sees the systemd driver in a
   directory name; that exercise explains why the kubelet may no longer be the one choosing it.

3. [Chaos drill 0.C1 — OOMKilled while the host barely
   notices](../../labs/00/06-oom-inside-a-wall.md) — step 6 from the kernel's side, on a bare host
   with no Kubernetes in the way. Exit 137 means the same thing there as here, and seeing it without
   a kubelet or a pod object nearby is the cheapest way to stop reading it as a Kubernetes event.

4. `docs/concepts/architecture/cgroups.md` in the pinned tree, read end to end next to the post
   rather than in the diff form step 8 prints. 148 lines, two feature-state markers pointing
   opposite ways, and a migration list that grew by two bullets in four years. It is what absorption
   looks like when it goes well: the post is not contradicted anywhere, it is simply no longer the
   copy anyone maintains.

5. Unanswerable from the pin: which patch releases of the Node.js v18 line, if any, read the cgroup
   v2 memory limit. The page says the line *does not reliably detect* it, and names a single version
   for v20 — v20.3.0 — but no patch versions for v18 at all. Compare that with the Java bullet
   directly above it, which names jdk8u372, 11.0.16 and 15. One bullet is precise to the patch and
   the other names no versions at all, and nothing at the pin explains the difference. Step 6
   measures the tag you pulled on the day you pulled it; it cannot tell you what `node:18-alpine`
   did last month.

**Teardown**

```sh
kubectl delete ns cg
rm -f /tmp/n20.out /tmp/n18.out
```

Nothing on the node was changed, so there is nothing to put back: every command outside the
namespace was a read. The two Node images stay in the node's image store, which is worth knowing
before the next exercise measures disk. If you want them gone, remove them through the runtime on
the node rather than by recreating the guest.
