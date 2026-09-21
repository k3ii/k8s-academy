<a id="pod-has-network-condition"></a>

# The one gate file in 487 that records its former name is the same file that still links through that name into a heading nobody kept, the post's single correction reached one of its eighteen uses of the name, and five generated reference pages still have the gate a stage behind

**Post** — [Kubernetes 1.25: PodHasNetwork Condition for Pods](https://kubernetes.io/blog/2022/09/14/pod-has-network-condition/),
2022-09-14.

5,892 bytes, 138 lines, one author: Deep Debroy of Apple. Eighth of 2022's thirteen `walk` verdicts.
Every identifier it names has since been renamed, and the post knows: it carries a correction, added
later by somebody else, saying so. The correction is four lines long and sits at `:25-30`, above 108
lines that were never touched.

**As written**

The announcement is at `:10-23`. Kubernetes 1.25 introduces alpha support for a new condition in the
status field of a pod, `PodHasNetwork`, behind a kubelet feature gate called
`PodHasNetworkCondition`. The kubelet sets it once the pod's runtime sandbox exists with networking
configured, which is the moment after which the kubelet can start pulling images and creating
containers, including init containers. Two consumers are named for it: monitoring services that want
to generate pod-startup Service Level Indicators, `:17-21`, and runtimes that want to optimise what
they do at pod start, `:21-23`.

The case for a new condition takes the whole of `:32-56`, and it is an argument against the one that
already existed. `Initialized` tracks init containers, so its meaning depends on what the pod author
wrote. If a pod has init containers, they are user code and may crash or carry a bad image, and
their number varies by workload, so no cluster-wide infrastructural SLI can rest on the condition
that waits for them, `:37-43`. If a pod has none, the condition is worse than unhelpful:

> If a pod does not specify init containers, the status of the `Initialized`
> condition in the pod status is set to `"True"` very early in the lifecycle of
> the pod. This occurs before the kubelet initiates any pod runtime sandbox
> creation and network configuration steps.

That is the sentence the exercise is built to reproduce. A pod with no init containers reports
`Initialized` as true before anything has been asked of the container runtime, and will keep
reporting it even if the sandbox never comes up at all, `:49-51`. The new condition is offered as
the accurate reading of the same moment, `:53-56`.

Two special cases follow at `:58-71`. A pod with `hostNetwork` set to true gets the condition from
sandbox creation alone, because the runtime typically skips network configuration for it, `:60-64`.
And a node agent that reconfigures a pod's interfaces later, by watching annotations such as
`k8s.v1.cni.cncf.io/networks`, does not move the condition at all, because the condition describes
the sandbox the kubelet set up and nothing after it, `:66-71`.

The `### Try out the PodHasNetwork condition for pods` section, `:73-112`, is the part the reader
would copy. Enable the gate on the kubelet, and `kubectl describe pod` reports the condition. Two
transcripts are given, one for a pod whose sandbox came up and one for a pod whose sandbox did not,
and both print the same five conditions in the same order:

> Conditions:
>   Type              Status
>   PodHasNetwork     True
>   Initialized       True
>   Ready             True
>   ContainersReady   True
>   PodScheduled      True

The second transcript, `:100-112`, differs in exactly one interesting way: `PodHasNetwork` is
`False` while `Initialized` is `True`. It is the argument of `:45-51` printed as terminal output,
and step 3 below produces it from a live cluster four years later, under a different name.

Then the forecast, `:116-117`: depending on feedback and adoption, the project plans to push the
reporting of the condition to beta in 1.26 or 1.27. And a pointer, `:121-124`, to
`/docs/concepts/workloads/pods/pod-lifecycle/` with no anchor on it — the only link in this story
that still lands where it was aimed.

The correction is `:25-30`, a section heading reading `### Updates for Kubernetes 1.28` and four
lines of prose. It says the condition has been renamed to `PodReadyToStartContainers`, that the gate
has been replaced by `PodReadyToStartContainersCondition`, and that the new gate is the one to set
from v1.28.0 onward. It is accurate. It is also the only place in the post that knows. The post uses
the string `PodHasNetwork` twenty times, two of those as the gate name; of the eighteen uses of the
bare condition name, the correction accounts for one. Seventeen were left standing, including the
title at `:3`, the section heading at `:73`, the instruction to enable the old gate at `:75-77`, and
both terminal transcripts.

The placement is why. The archive's usual shape for a correction is a note above the article, and
there are twenty such blocks across all 767 posts — counted in [the exercise for the gRPC probes
post](02-grpc-probes-now-in-beta.md), which owns that census. This is not one of them. It is a body
heading, and it is the only heading of its kind in the archive: a reader who opens the post for its
*Try out* section, which is what a *Try out* section is for, scrolls past `:25-30` without being
required to read it and lands on an instruction naming a gate that has not existed since 1.28.

**As it runs now**

Both names are gone from the running system and from most of the tree. The condition is
`PodReadyToStartContainers` and the gate is `PodReadyToStartContainersCondition`. Step 10 counts the
four strings across `content/en`: the old gate name survives in two documentation files and one blog
post, the old condition name in four and one, and both of those documentation counts are made up
entirely of files whose job is to record the rename. The new names are in eight and nine
documentation files respectively, and two blog posts.

The rename produced two feature-gate files, not one. `PodHasNetworkCondition.md` holds a single
alpha stage across 1.25 to 1.27 and declares `removed: true`; its body says the gate was renamed in
1.28. `PodReadyToStartContainersCondition.md` holds three stages beginning at alpha 1.28, and its
frontmatter carries a field no other file in the directory carries:

> former_titles:
>   - PodHasNetworkCondition

Step 8 counts it: 487 gate files, one declaring `former_titles`. That field is the whole reason this
rename is legible at all. Nothing else in the tree connects the two gate names except prose, and
prose is what goes stale. A name that simply vanishes from a directory of 487 files leaves no trace
you can grep for, because the thing you would grep for is the string that is no longer there.

The file that keeps the receipt is also the file that never finished the rename. Both gate files
point their reader at the same place,
`/docs/concepts/workloads/pods/pod-lifecycle/#pod-has-network`, and the second does it while the
visible link text says `PodReadyToStartContainers`. That anchor does not exist. The heading is `Pod
readiness to start containers {#pod-ready-to-start-containers}`, an H3 at `pod-lifecycle.md:688`,
and the string `pod-has-network` occurs in exactly three files at the pin: the two gate files, as
this link, and the blog post, as its slug. Step 9 puts that in proportion — the gate directory
carries 129 anchored links into the documentation and 24 of them resolve to no heading, so a dead
anchor here is a habit rather than an oversight. These two are the only ones dead because of a
rename the same files record.

The condition is documented twice, and the two pages disagree about what it means.
`pod-lifecycle.md:609-610` says the sandbox has been created, networking configured, storage volumes
mounted, and any dynamic resources allocated; it says it again at `:696-703` and `:717-719`, and its
account has the kubelet mounting volumes before the sandbox is built at all, `:696-697`.
`pod-condition.md:58` says the sandbox has been created and networking configured, full stop, and
says it again at `:127`. Neither page mentions volumes or dynamic resources in the other's terms.
Both carry the same note about the old name, at `pod-lifecycle.md:692-694` and
`pod-condition.md:110`, and both give their section the identical anchor
`{#pod-ready-to-start-containers}`. The post is not wrong about either: it predates both additions.
What it describes is the condition's 1.25 scope, and the condition outgrew its second name as well
as its first.

The two pages also disagree about how to state the maturity, in a way that predicts which one will
go stale next. `pod-condition.md:107` writes the shortcode as `{{< feature-state
feature_gate_name="PodReadyToStartContainersCondition" >}}`, which reads the gate file.
`pod-lifecycle.md:690` writes `{{< feature-state for_k8s_version="v1.37" state="stable" >}}`, which
is a release number typed by hand into a page that has already been wrong about this feature once.

And the generated command-line reference has not caught up at all. Step 10 prints the gate out of
the five `--feature-gates` help texts under `command-line-tools-reference` — `kube-apiserver.md`,
`kube-controller-manager.md`, `kube-proxy.md`, `kube-scheduler.md` and `kubelet.md` — and all five
say `BETA - default=true` for a gate whose own file says stable, locked, from 1.37, which is the
pin's release. [The certificate exercise](../2015/07-strong-simple-ssl-for-kubernetes.md) met the
same disagreement on three gates and told the reader to believe the cluster. What this row adds is
the size of it: of the 149 gates named in the apiserver's help text, 34 disagree with their gate
file on stage or default, and 26 of those 34 have a final stage beginning at 1.37. The reference is
one release behind. Four of the thirty-four are not explained by that, and are left here as a
pointer rather than a claim.

The feature itself arrived, whole. It reached beta at 1.29 — announced in [a 2023
post](https://kubernetes.io/blog/2023/12/19/pod-ready-to-start-containers-condition-now-in-beta/)
that the census marks `read` and defers to this exercise — and stable and locked at 1.37. That is
thirteen releases from this post to the end, against a forecast of one or two. The pinned tree names
no KEP for any of it.

**What this exercise does not cover, and where it lives**

Making a sandbox fail on purpose by naming a RuntimeClass handler the node does not have is [the
RuntimeClass exercise](../2018/09-runtimeclass.md), steps 6 and 7. Writing a value into `status` by
hand and timing the controller that corrects it is [Write a lie into status and time the
correction](../../labs/01/07-stomp-the-status.md). Counting the CRI calls that one pod costs is
[Predict the CRI calls that start one pod, then count
them](../../labs/06/02-one-pod-is-how-many-cri-calls.md). The archive's twenty editorial update
notes are counted in [the gRPC probes exercise](02-grpc-probes-now-in-beta.md), and this exercise
takes that number as given rather than recounting it. Moving a conflist out of `/etc/cni/net.d` to
see what the kubelet does without a plugin belongs to the CNI module. Dynamic resource allocation is
named here only as scope the condition acquired after this post; its own ladder is not this row's.

**The diff, and why**

**Broke, in both halves.** Nothing the *Try out* section tells you to do works. The gate it names
was removed after 1.27, so a kubelet at the pin rejects it; the condition it tells you to look for
has not been emitted under that name since 1.28. Both transcripts print output no cluster produces
now. This is the plainest kind of break, and it is entirely a naming break: run the same section
with the two strings replaced and every word of it is still true, which step 3 demonstrates.

**Retired by being agreed with.** The argument at `:32-56` is now the documentation's argument. Two
concept pages carry the distinction between `Initialized` and this condition, and the gate reached
stable with `locked: true` at 1.37, which means the behaviour can no longer be turned off. The post
asked for a condition the kubelet would set from its own knowledge rather than from the pod
author's, and got it permanently. A reader who wants to know whether the post won should look at the
`locked` column and not at the words.

**A forecast the rename invalidated.** `:116-117` predicts beta in 1.26 or 1.27. Beta came at 1.29.
The gap is not neglect: the alpha clock restarted. The feature spent 1.25 to 1.27 in alpha under the
first gate and then 1.28 in alpha again under the second, which is a stage repeated rather than a
stage skipped, and the ladder below is the only place you can see that, because it takes two tables
to show it. A forecast made before a rename is a forecast made in the wrong units.

**Overtaken by its own growth.** The condition now covers storage volume mounting and dynamic
resource allocation, neither of which existed in this post's account of it, and one of the two pages
documenting it has not noticed. `PodReadyToStartContainers` is now the second name that is too
narrow for what the condition does: nothing in it says volumes or devices either. The post is not
wrong about 1.25. It is a description of a scope that has twice been outgrown, and the second time
nobody renamed anything.

**The ladder**

Two gates, one feature. The ladder is per gate, so it is two tables, and the relationship between
them is the argument.

`PodHasNetworkCondition`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.25 – v1.27 |

`PodReadyToStartContainersCondition`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.28 – v1.28 |
| beta | `true` | — | v1.29 – v1.36 |
| stable | `true` | `true` | v1.37 – |

The first declares `removed: true`. The second declares `former_titles`, naming the first, and is
the only file of the 487 that declares that field at all — a file-level fact, not a stage, which is
why it is a sentence here and not a column. Step 8 prints both frontmatters and the count.

The two tables are contiguous and not continuous. There is no gap: 1.27 ends one and 1.28 begins the
other. But the stage restarts, so read as one ladder the feature is alpha for four releases across
two names, beta for eight, and stable from 1.37 with the gate locked. Thirteen releases end to end.
A single table cannot say this without lying about one of the two files, which is the case for
laddering per gate rather than per feature.

The lab matters here because it is not the pin. The clusters in this repo run v1.35, where the gate
is beta and defaults to `true` and is **not** locked — so the condition is there without anyone
asking for it, and it can still be switched off. Step 7 switches it off. At the pin that step is
impossible, and this is the last window in which it is not.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 cores, at `10.10.10.180`. Steps
1 to 5 run wherever `kubectl` is. Steps 6 and 7 need a root shell on the node itself: `ssh
zain@10.10.10.180`. Everything is created in a namespace called `psn`, except step 7, which appends
two lines to the kubelet's configuration file and restarts the kubelet, and puts the file back in
the same step. Steps 8 to 10 need no cluster at all; they read the pinned checkout.

**Do**

1. Establish the ground before touching anything: the release the cluster is on, and which pod
   conditions it actually emits. The second command is the whole rename, read off a running system.

   ```sh
   kubectl version -o json | jq -r '.serverVersion.gitVersion'
   kubectl get pods -A -o json \
     | jq -r '.items[].status.conditions[].type' | sort | uniq -c | sort -rn
   kubectl get pods -A -o json | grep -c PodHasNetwork || true
   ```

2. Read the gate off the kubelet that is running, not off a file. An empty or absent `featureGates`
   map means nobody set it, which at v1.35 means the beta default is what you are watching.

   ```sh
   N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw "/api/v1/nodes/$N/proxy/configz" \
     | jq '.kubeletconfig.featureGates'
   ```

3. Reproduce the post's argument. Two pods, one with no init container and one with an init
   container that sleeps, and four timestamps each. Predict in writing, before you run it, which of
   `Initialized` and `PodReadyToStartContainers` is stamped first in each pod.

   ```sh
   kubectl create ns psn
   kubectl -n psn run plain --image=registry.k8s.io/pause:3.10
   kubectl -n psn apply -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata:
     name: withinit
   spec:
     initContainers:
     - name: wait
       image: busybox:1.36
       command: ["sh", "-c", "sleep 20"]
     containers:
     - name: app
       image: registry.k8s.io/pause:3.10
   YAML
   sleep 45
   for POD in plain withinit; do
     echo "== $POD"
     kubectl -n psn get pod $POD -o json \
       | jq -r '.status.conditions[] | [.type, .status, .lastTransitionTime] | @tsv'
   done
   ```

4. Test the first special case, `:60-64`. A `hostNetwork` pod gets the condition from sandbox
   creation alone, because the runtime skips network setup for it. Compare its timestamps with
   `plain` and note the pod IP it reports.

   ```sh
   kubectl -n psn apply -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata:
     name: hostnet
   spec:
     hostNetwork: true
     containers:
     - name: app
       image: registry.k8s.io/pause:3.10
   YAML
   sleep 20
   kubectl -n psn get pod hostnet -o json \
     | jq -r '.status.conditions[] | [.type, .status, .lastTransitionTime] | @tsv'
   kubectl -n psn get pod hostnet -o jsonpath='{.status.podIP} {.status.hostIP}'; echo
   ```

5. Find the condition's upper edge. A pod whose image cannot be pulled has a sandbox and will never
   have a container. Two conditions should disagree, and which two is the point of the exercise.

   ```sh
   kubectl -n psn run nopull --image=registry.k8s.io/pause:3.10-no-such-tag
   sleep 40
   kubectl -n psn get pod nopull -o json \
     | jq -r '.status.conditions[] | [.type, .status] | @tsv'
   kubectl -n psn get pod nopull \
     -o jsonpath='{.status.containerStatuses[0].state.waiting.reason}'; echo
   ```

6. Find its lower edge, on the node. `pod-lifecycle.md:705-715` says the condition goes back to
   `False` when the kubelet finds a pod without a sandbox — it names a node reboot and a runtime-VM
   reboot. Destroy the sandbox under a running pod and see whether the third case behaves like the
   two that are documented. Poll fast; the answer may be a window you can miss.

   ```sh
   ssh zain@10.10.10.180
   SB=$(sudo crictl pods --namespace psn --name plain -q)
   echo "sandbox $SB"
   sudo crictl rmp -f $SB
   for I in 1 2 3 4 5 6 7 8 9 10; do
     kubectl -n psn get pod plain -o json \
       | jq -r '.status.conditions[]
                | select(.type == "PodReadyToStartContainers")
                | [.status, .lastTransitionTime] | @tsv'
     sleep 2
   done
   ```

7. Turn the condition off. This works because the lab is at v1.35, where the gate is beta and
   unlocked; at the pin's v1.37 it is locked and this step has no equivalent. If the file already
   has a `featureGates:` key, put the entry under the existing one instead of appending a second
   block.

   ```sh
   ssh zain@10.10.10.180
   sudo cp /var/lib/kubelet/config.yaml /var/lib/kubelet/config.yaml.orig
   grep -n featureGates /var/lib/kubelet/config.yaml || true
   sudo tee -a /var/lib/kubelet/config.yaml >/dev/null <<'EOF'
   featureGates:
     PodReadyToStartContainersCondition: false
   EOF
   sudo systemctl restart kubelet
   sleep 20
   kubectl -n psn run gateoff --image=registry.k8s.io/pause:3.10
   sleep 20
   kubectl -n psn get pod gateoff -o json | jq -r '.status.conditions[].type'
   sudo cp /var/lib/kubelet/config.yaml.orig /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet
   ```

8. Offline, against the pinned checkout. Print both ladders out of the frontmatter, as YAML, and
   count how many of the 487 gate files declare a former title. Do not grep for the stages; the
   field you want on the last row is one that most files do not have.

   ```sh
   cd /path/to/kubernetes/website/content/en
   python3 - <<'PY'
   import yaml, glob, os
   G = "docs/reference/command-line-tools-reference/feature-gates"
   def front(p):
       return yaml.safe_load(open(p).read().split("---")[1])
   for name in ("PodHasNetworkCondition", "PodReadyToStartContainersCondition"):
       f = front(G + "/" + name + ".md")
       print(name)
       for s in f["stages"]:
           print("  %-7s default=%-5s locked=%-5s %s - %s" % (
               s["stage"].strip(), s["defaultValue"], s.get("locked", ""),
               s["fromVersion"], s.get("toVersion", "")))
       print("  removed:", f.get("removed"), " former_titles:", f.get("former_titles"))
   n = tot = 0
   for p in sorted(glob.glob(G + "/*.md")):
       if os.path.basename(p) == "index.md":
           continue
       tot += 1
       if front(p).get("former_titles"):
           n += 1
   print("gate files: %d, declaring former_titles: %d" % (tot, n))
   PY
   ```

9. Offline. Follow every anchored link the gate files make into the documentation and see which ones
   land on a heading. Two of the failures are this feature's, and the rest are the context that
   tells you whether to call them a lapse.

   ```sh
   cd /path/to/kubernetes/website/content/en
   python3 - <<'PY'
   import os, re, glob
   G = "docs/reference/command-line-tools-reference/feature-gates"
   def anchors(path):
       out = set()
       for line in open(path, encoding="utf-8", errors="replace"):
           if not line.startswith("#"):
               continue
           m = re.search(r"\{#([a-z0-9-]+)\}", line)
           if m:
               out.add(m.group(1))
           h = re.sub(r"\{#[a-z0-9-]+\}|\{\{<[^>]*>\}\}|[`*\[\]]", "", line.lstrip("#"))
           out.add(re.sub(r"[^a-z0-9]+", "-", h.lower()).strip("-"))
       return out
   links, dead = [], []
   for p in sorted(glob.glob(G + "/*.md")):
       if os.path.basename(p) == "index.md":
           continue
       text = open(p, encoding="utf-8", errors="replace").read()
       for m in re.finditer(r"\]\((/docs/[^)#]*)#([a-z0-9-]+)\)", text):
           links.append((os.path.basename(p), m.group(1), m.group(2)))
   for fn, url, anc in links:
       rel = url.strip("/")
       tgt = next((c for c in (rel + ".md", rel + "/index.md", rel + "/_index.md")
                   if os.path.exists(c)), None)
       if tgt is None or anc not in anchors(tgt):
           dead.append((fn, url + "#" + anc))
   print("anchored links in gate files: %d, unresolved: %d" % (len(links), len(dead)))
   for fn, u in dead:
       if "pod-lifecycle" in u:
           print("  %s -> %s" % (fn, u))
   PY
   ```

10. Offline. Measure how far the rename travelled: through the tree, through the post that announced
    it, and through the generated reference.

    ```sh
    cd /path/to/kubernetes/website/content/en
    P=blog/_posts/2022/pod-has-network-condition.md
    R=docs/reference/command-line-tools-reference
    for S in PodHasNetworkCondition PodReadyToStartContainersCondition \
             PodHasNetwork PodReadyToStartContainers; do
      printf '%-36s docs=%s blog=%s\n' "$S" \
        "$(grep -rl "$S" docs --include='*.md' | wc -l | tr -d ' ')" \
        "$(grep -rl "$S" blog --include='*.md' | wc -l | tr -d ' ')"
    done
    echo "uses in the post: $(grep -o PodHasNetwork $P | wc -l | tr -d ' ')"
    echo "of them the gate name: $(grep -o PodHasNetworkCondition $P | wc -l | tr -d ' ')"
    grep -n 'Updates for Kubernetes' $P
    grep -ho 'PodReadyToStartContainersCondition=true|false ([A-Z]* - default=[a-z]*)' \
      $R/*.md | sort | uniq -c
    ```

**Expect**

Step 1 prints a v1.35 server. The condition census should return five types, and
`PodReadyToStartContainers` should be one of them with a count close to the others — note any pod
that is missing it rather than assuming none is. The third command is the rename stated as a number:
zero matches, and an exit status of 1, which is what the `|| true` is absorbing. Nothing on this
cluster has ever heard of the name in the post's title.

Step 2 should print `null` or an empty object. That is the answer worth having: at v1.35 the gate is
beta and defaults to `true`, so the condition you are about to watch is switched on by a default
nobody in this lab chose, and the configuration file has nothing to say about it. Write down the
server version next to the ladder above, and place the lab between the beta row and the stable one.

Step 3 is the post's argument, and the two pods should answer it in opposite orders. For `plain`,
which has no init containers, `Initialized` is stamped no later than `PodReadyToStartContainers`,
because the kubelet sets it before it asks the runtime for anything; the two may land in the same
second, and if they do, say so rather than reading an order into a tie. For `withinit`,
`PodReadyToStartContainers` comes first and `Initialized` follows about twenty seconds later, when
the init container's sleep ends. Same cluster, same condition, and the relative order of two
timestamps flipped by a field in the pod spec. That is `:37-51` in four lines of `@tsv`, and it is
why a cluster-wide SLI cannot be built on `Initialized`.

Step 4 should show `hostnet` with `PodReadyToStartContainers` `True` and a `podIP` equal to its
`hostIP`. The post's claim at `:60-64` is about what the condition is derived from rather than about
timing, and on a one-node cluster the timing difference against `plain` may be smaller than the
one-second resolution of `lastTransitionTime`. Record the gap you get; do not report a difference
the clock cannot express.

Step 5 is the upper edge and should split the conditions cleanly: `PodReadyToStartContainers`
`True`, `Initialized` `True`, `PodScheduled` `True`, and both `ContainersReady` and `Ready` `False`,
with a waiting reason of `ErrImagePull` or `ImagePullBackOff` — report which. The sandbox exists and
is networked; no container will ever run in it. The condition is about the room, not the occupant,
and this is the pod that proves it says nothing about whether your workload works.

Step 6 is the lower edge and the one place this exercise will not tell you the answer in advance.
The documentation names two ways a sandbox disappears under a live pod and yours is a third. The
kubelet will rebuild the sandbox within a sync period; whether it writes `False` on the way, or
whether the rebuild completes inside one sync and the condition never moves, is a race you are
sampling at two-second intervals. Record the `lastTransitionTime` before and after. If it did not
change, you have not proved the condition stayed `True` — you have proved your sampling missed, or
that it did.

Step 7 should print four condition types for `gateoff` and not five, with
`PodReadyToStartContainers` absent. Check `plain` as well, and report whether a pod that already
carried the condition still carries it after a kubelet restart with the gate off: a field the
kubelet stops setting is not the same as a field the kubelet removes. Then confirm the restore took,
by re-running step 2 and seeing the `featureGates` map go back to what it was. This step is the
reason to do this exercise now. Once a cluster is at v1.37 the gate is `locked: true` and there is
no version of step 7 to run.

Step 8 prints the two ladders and one count:

```
PodHasNetworkCondition
  alpha   default=False locked=      1.25 - 1.27
  removed: True  former_titles: None
PodReadyToStartContainersCondition
  alpha   default=False locked=      1.28 - 1.28
  beta    default=True  locked=      1.29 - 1.36
  stable  default=True  locked=True  1.37 -
  removed: None  former_titles: ['PodHasNetworkCondition']
gate files: 487, declaring former_titles: 1
```

The blank `locked` on five of the six rows is the field being absent rather than false, and the one
`True` is the end of the story: from 1.37 the condition cannot be switched off. The last line is the
one to keep. One file in 487 declares what it used to be called, and it is this one.

Step 9 prints `anchored links in gate files: 129, unresolved: 24`, and three of the unresolved land
on `pod-lifecycle`:

```
  PodHasNetworkCondition.md -> /docs/concepts/workloads/pods/pod-lifecycle/#pod-has-network
  PodReadyToStartContainersCondition.md -> /docs/concepts/workloads/pods/pod-lifecycle/#pod-has-network
  StartupProbe.md -> /docs/concepts/workloads/pods/pod-lifecycle/#when-should-you-use-a-startup-probe
```

Nineteen per cent of the gate directory's anchored links point at headings that are not there, so
the two on this page are not a special failure. What is special is the direction: `StartupProbe`
points at a heading the page renamed, while these two point at a heading that was never there under
that name after the feature was renamed — and the second of them is the file that carries
`former_titles`. The file that remembers the old name is the one still using it.

Step 10 prints the four counts as `docs=2 blog=1`, `docs=8 blog=2`, `docs=4 blog=1` and `docs=9
blog=2`, then twenty uses of `PodHasNetwork` in the post of which two are the gate name, then the
correction at line 25, then `5 PodReadyToStartContainersCondition=true|false (BETA - default=true)`.
Three things to take from it. The four documentation files still naming the old condition are the
two gate files and the two concept pages, which is to say the rename survives only where it is being
recorded. Eighteen of the post's uses are the bare condition name, and the correction block accounts
for exactly one of them: `grep` finds its heading at line 25 of 138, and the sentence naming the old
condition sits at line 27. The other seventeen stand as written. And the reference is unanimous and
wrong: five pages, one stage behind the file they describe.

**Read on**

1. [The post that announced
   beta](https://kubernetes.io/blog/2023/12/19/pod-ready-to-start-containers-condition-now-in-beta/),
   2023-12-19, which the census marks `read` because this row owns the rename. Read it against this
   one and note two things: it restates the motivation in cluster-administrator terms rather than
   SLI terms, and its link into the concept page carries the anchor `#pod-conditions`, which
   resolves. The successor post fixed the link the gate files still have wrong.

2. `pod-condition.md` and `pod-lifecycle.md`, the two pages that document this condition. Read
   `pod-condition.md:40-60` and `:105-130` against `pod-lifecycle.md:601-616` and `:688-725`, and
   decide which you would cite. They share an anchor id, a note, and a subject, and they do not
   share a definition.

3. The archive's own habit, now that it has a positive case. Several exercises record that a gate
   declares no former title — [the 1.1 release
   exercise](../2015/10-kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community.md)
   at `:173` and [the PID limiting exercise](../2019/05-pid-limiting.md) at `:238` among them. Those
   sentences were worth writing because of this file. A field that one file in 487 carries is an
   instrument, and an instrument is worth naming every time it reads zero.

4. The thirty-four gates whose generated help text disagrees with their own file, and the four of
   them a one-release lag does not explain. Step 10 prints only this feature's row; the script in
   step 9 is the shape to reuse if you want the rest. Start from whether the disagreement is in the
   stage, the default, or both.

5. *Unanswerable from the pin:* whether a sandbox destroyed under a running pod moves the condition
   at all. `pod-lifecycle.md:705-715` names a node reboot and a runtime virtual machine reboot, and
   step 6 is neither; nothing in the pinned tree says what the kubelet does in the third case, and
   the only source for it is your own cluster. Also unanswerable: why the second name was chosen. It
   covers volumes and dynamic resources today and says neither, and the pinned tree names no KEP for
   the feature in any of its releases.

**Teardown**

```sh
kubectl delete ns psn
```

And, if step 7 was interrupted before its last two lines, put the kubelet's configuration back and
confirm with step 2:

```sh
ssh zain@10.10.10.180 'sudo cp /var/lib/kubelet/config.yaml.orig /var/lib/kubelet/config.yaml'
ssh zain@10.10.10.180 'sudo systemctl restart kubelet'
```
