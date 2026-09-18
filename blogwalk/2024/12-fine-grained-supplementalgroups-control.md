<a id="fine-grained-supplementalgroups-control"></a>

# The generated API reference calls this field alpha, its own gate record calls it beta, the project announced it stable in the release this lab runs, and the two `kubectl apply` commands the post gives you are the only ones in the whole blog archive whose path has never existed

**Post** — [Kubernetes 1.31: Fine-grained SupplementalGroups control](https://kubernetes.io/blog/2024/08/22/fine-grained-supplementalgroups-control/),
2024-08-22.

6,981 bytes over 164 lines, the seventh of the thirteen 2024 walks by size, which makes it the
median one exactly. One author, Shingo Omura, writing from Woven By Toyota. It is a page bundle
rather than a single file: the directory also holds `implicit-groups.yaml` and
`strict-supplementalgroups-policy.yaml`, pulled in at `:20` and `:72` by `code_sample`, and those
two files are why this post can be run from the pinned checkout without retyping anything. Seven
fenced blocks, two notes, one trailing space at `:91`, and one HTML comment at `:155` carrying a
link to the documentation pull request that accompanied it, left in the published text.

**As written**

`:14-16` states the behaviour the post exists to name, and it is one most people have never noticed:
Kubernetes *merges* group information from the Pod with the group information defined in
`/etc/group` inside the container image. `:18-20` gives a Pod that sets `runAsUser: 1000`,
`runAsGroup: 3000` and `supplementalGroups: [4000]`, and `:22` asks the question the whole post
turns on — what does `id` print in that container?

`:37-39` answers it: `uid=1000 gid=3000 groups=3000,4000,50000`. `:41` asks where `50000` came from,
since it appears nowhere in the manifest, and `:43-52` shows the answer by reading `/etc/group` out
of the image: `group-defined-in-image:x:50000:user-defined-in-image`. `:54` says where the behaviour
came from and how long it stood: *this was a design decision the current CRI implementations
inherited from Docker, and the community never really reconsidered it until now*.

`:56-58` is the case for change, and it has two halves. File permissions in Linux are decided by uid
and gid, so an unasked-for group is a volume-access problem; and *the implicit gids from
`/etc/group` can not be detected/validated by any policy engines because there is no clue for the
implicit group information in the manifest*. The second half is the one worth holding on to. It is
an argument about what admission control can see.

`:60-72` introduces the fix: a new `supplementalGroupsPolicy` field on the Pod's
`.spec.securityContext`, with two values. `Merge` keeps the old behaviour and is the default.
`Strict` attaches only the group IDs named in `fsGroup`, `supplementalGroups` or `runAsGroup`.
`:74-89` runs the same Pod with `Strict` and gets `uid=1000 gid=3000 groups=3000,4000`. `:91`: *You
can see `Strict` policy can exclude group `50000` from `groups`!*

`:93` is the recommendation, and it is conditional: *ensuring `supplementalGroupsPolicy: Strict`
(enforced by some policy mechanism) helps prevent the implicit supplementary groups in a Pod.* The
note at `:95-97` immediately qualifies even that — a container with enough privilege can change its
own identity afterwards.

`:99-123` adds the other half of the feature: `.status.containerStatuses[].user.linux`, which
reports the uid, gid and supplementary groups actually attached to the first process, so that
implicit group IDs become visible after the fact. The note at `:119-123` says plainly that this is
the *firstly attached* identity and that `setuid(2)`, `setgid(2)` and `setgroups(2)` can move it
afterwards.

`:125-143` is *Feature availability*: Kubernetes v1.31 or later with the `SupplementalGroupsPolicy`
feature gate enabled, *as of v1.31, the gate is marked as alpha*; containerd v2.0 or later, or CRI-O
v1.31 or later; and a per-node answer readable at `.status.features.supplementalGroupsPolicy`.
`:145-151` hopes for beta and eventually GA, and `:153-158` points at the security-context task page
and at KEP-3619.

**As it runs now**

**The section that introduces the field names a field that has never existed.** `:60` reads `##
Fine-grained SupplementalGroups control in a Pod: ` followed by `SupplementaryGroupsPolicy` in
backticks. The field is `supplementalGroupsPolicy`; the gate is `SupplementalGroupsPolicy`.
*Supplementary* appears in that spelling exactly once in the whole of `content/en`, and it is this
heading. Two lines later, `:62`, the post spells it correctly. Step 10 does the census.

**The two commands the post gives you for creating its example Pods point at a path that has never
existed.** `:26` and `:76` both read `kubectl apply -f
https://k8s.io/blog/2024-08-22-Fine-grained-SupplementalGroups-control/<file>`. The post is
published under the slug `fine-grained-supplementalgroups-control`, its source bundle is
`blog/_posts/2024/fine-grained-supplementalgroups-control/`, and nothing anywhere in the blog tree
is named for that datestamp-and-title form. Those two lines are also the only two `kubectl apply -f
https://k8s.io/blog/` commands in the entire archive of 767 posts: every other post that ships a
manifest either inlines it or sends you to `k8s.io/examples/`, which does resolve. Step 9 checks
both ends.

**Three files in one checkout put this field at three different stages.** `pod-v1.md:2306` describes
`supplementalGroupsPolicy` and then says *(Alpha) Using the field requires the
SupplementalGroupsPolicy feature gate to be enabled*. The gate record `SupplementalGroupsPolicy.md`
declares alpha from v1.31 to v1.32 and beta, defaulting true, from v1.33 — with no stable stage at
all — so the banner at `security-context.md:235`, which reads that record, renders beta. And the
project's own announcement of general availability for this feature sits in the same checkout:
`blog/_posts/2025/fine-grained-supplementalgroups-control-ga.md`, whose title line names v1.35 — the
release this lab runs — and whose `:13` recites the whole ladder, alpha at v1.31, beta at v1.33, GA
now. The pin is v1.37. Nothing here is a matter of interpretation: one of the three is current and
the other two were never updated.

**The task page still tells you to turn on a gate that has been on by default for four releases.**
`security-context.md:237-239`: *this feature can be enabled by setting the
`SupplementalGroupsPolicy` feature gate for kubelet and kube-apiserver*. Since v1.33 the gate
defaults to `true`, so on any cluster at the pin, or on this lab's v1.35, the only thing you have to
do is set the field. Step 1 confirms the gate's value without touching a flag.

**And the same page narrates the alpha in the present tense.** `security-context.md:340` opens *At
this alpha release(from v1.31 to v1.32)* and describes the silent fallback to `Merge` on a node
whose runtime cannot do it. `:342` then describes the beta behaviour that replaced it, where the
kubelet rejects the Pod with `reason=SupplementalGroupsPolicyNotSupported`. Both are in one note;
only the second can happen at the pin; the first is written as though it still could.

**The remedy the post recommends is not available in any built-in policy.** `:93` asks you to
enforce `Strict` with *some policy mechanism*, and `:58` argued that the problem is precisely that
admission cannot see the implicit groups. At the pin, `supplementalGroups` occurs zero times in
`pod-security-standards.md`: the field is in no profile, at any level. The whole feature appears in
exactly three files under `docs`, two of which are generated API references. The one thing that does
expose the merged groups, `.status.containerStatuses[].user.linux`, is status, written after the Pod
is admitted, which is the one place an admission controller cannot read. Step 8 builds a Pod that
satisfies `restricted` completely and still comes up carrying a group nobody granted.

**The demonstration depends on a property of one image tag, not on Kubernetes.** Both bundled
manifests, and the task page's `security-context-6.yaml`, pin
`registry.k8s.io/e2e-test-images/agnhost:2.45`. Group `50000` is in that image's `/etc/group`; it is
not in the API, the kubelet or the runtime. This repository's house tag is `agnhost:2.53`, eight
releases along. Step 3 runs the identical manifest at both tags, because if the entry has been
dropped the post's central output has quietly stopped being reproducible, and if it survives that is
worth knowing too.

**The node-support boolean is named for one feature and defined as covering two.** `node-v1.md:425`
reads *SupplementalGroupsPolicy is set to true if the runtime supports SupplementalGroupsPolicy and
ContainerUser.* `ContainerUser` is the status type at `pod-v1.md:1037-1049`, holding a single
`linux` field of type `LinuxContainerUser` (`pod-v1.md:1779-1799`: `uid`, `gid`,
`supplementalGroups`). It is also, unrelatedly, the name of one of the two default Windows container
accounts at `windows-security.md:35`, on a feature that `pod-v1.md:149` will not let you set when
`spec.os.name` is `windows`. One identifier, two meanings, one tree.

**Everything the feature actually promises works, on the first try, with nothing enabled.** `Strict`
excludes `50000`. `Merge` keeps it. The status field reports what was attached. The node answers
`true`. The lab's containerd is 2.2.1, comfortably past the v2.0 floor `:131` names, and its runc is
1.5.1. Steps 2, 4, 5 and 7 are four confirmations in a row, and they should be read before the rest
of this.

**And the thing the documentation cannot settle with itself.** `node-v1.md:425` makes
`.status.features.supplementalGroupsPolicy` a single boolean answering for two capabilities;
`security-context.md:329-338` presents the same boolean as answering for one, and `:252-254` ties
the `user.linux` exposure to the feature gate rather than to the node. What a runtime that
implements one and not the other should report, nothing says. Nor can this lab find out: the note at
`security-context.md:339-356` gives two different answers for a node that reports `false`, one keyed
to the alpha and one to the beta, and this node reports `true`. Producing a `false` would mean
running a second runtime at a version deliberately behind the one the lab's install procedure pins,
which is a different exercise. Both halves are recorded here and neither is chosen.

**What this exercise does not cover, and where it lives**

`fsGroup` — what it does to volume ownership, what `fsGroupChangePolicy` and a CSI driver's
`fsGroupPolicy` change about the cost of applying it — belongs to [the exercise on granular control
of volume permission
changes](../2020/09-kubernetes-release-1-20-fsgroupchangepolicy-fsgrouppolicy.md). Step 7 below sets
`fsGroup` once, only to see whether `Strict` counts it as a source of supplementary groups, and
reads nothing about volumes. The security-context task page's *first* example, and what Pod Security
Admission does when handed it, belong to [the exercise on the runc container breakout
CVE](../2019/02-runc-cve-2019-5736.md); step 8 here deliberately builds a Pod that `restricted`
accepts, which is the opposite direction. How `restricted` phrases a refusal is [the lab that makes
it name every missing field](../../labs/10/06-restricted-rejects-a-pod-you-can-name.md). The shape
of `.status.features` against the differently-shaped `.status.runtimeHandlers` beside it is read in
[the recursive read-only mounts exercise](03-recursive-read-only-mounts.md), which reserved this
field for this row. And uid and gid mapping as a containment boundary, rather than as a merge rule,
is [the user namespaces beta exercise](02-userns-beta.md).

**The diff, and why**

**Still right.** The mechanism, both policies, the status field, the node boolean and the runtime
floors are all exactly as described, and all of it works without enabling anything. For a post whose
subject is a security default that had stood since Docker, that is the headline, and the rest of
this section is about the pages around it rather than the thing itself.

**Retired by being agreed with.** The post's *What's next?* at `:145-149` hoped for beta and
eventually GA so that *users no longer need to enable the feature gate manually*. That happened:
beta in v1.33 with the gate defaulting on, and the project announced general availability in v1.35.
The sentence got what it asked for, and the instruction it was asking to make unnecessary is still
printed on the task page at `:237-239`.

**Overtaken by stasis.** Three artifacts did not move when the feature did. The gate record never
gained a stable stage, so the feature-state banner on its own task page still says beta. The
generated API reference still carries `(Alpha)` in the field description, which is upstream's Go
comment rather than the website's text, and which `kubectl explain` therefore repeats back to you
from a v1.35 server. And the task page's note still narrates the v1.31-to-v1.32 alpha in the present
tense. Step 1 and step 10 put all three side by side.

**Wrong when it was published.** The heading at `:60` names `SupplementaryGroupsPolicy`, and the two
`kubectl apply` URLs at `:26` and `:76` name a directory that has never existed under
`k8s.io/blog/`. Neither is drift: both were wrong on 2024-08-22 and both are still there. They are
also the two things in this post a reader is most likely to copy.

**Never absorbed.** `:58` says the trouble with implicit groups is that no policy engine can see
them, and `:93` tells you to enforce `Strict` with *some policy mechanism*. Two years and a GA
later, the built-in mechanism has no control for it: `supplementalGroups` does not appear in the Pod
Security Standards at all, so the strictest profile Kubernetes ships admits a Pod that will be given
a group the manifest never mentions. The feature gave operators a field. It did not give them a way
to require it.

**The ladder**

`SupplementalGroupsPolicy`, from its gate record:

| stage | default | locked | releases |
| --- | --- | --- | --- |
| alpha | `false` | — | v1.31 – v1.32 |
| beta | `true` | — | v1.33 – |

The record stops there. It has never been locked, and it has no stable row, which is the whole of
the three-file disagreement above: a feature the project announced as generally available in v1.35
is carried at the pin, two releases later, by a record whose newest stage is beta. Every page that
renders a feature-state banner for this feature reads that record and repeats it.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 cores, at `10.10.10.180`,
running Kubernetes v1.35. Bring it up with [the provision
steps](../../strands/lab-topologies.md#provision) and install Kubernetes with [the node baseline
procedure](../../strands/lab-topologies.md#node-baseline-steps). One node is enough, and one node is
also the limitation: every step below depends on the runtime answering that it supports the feature,
and the baseline procedure installs containerd 2.2.1 and runc 1.5.1, so it does. Everything runs in
a namespace called `bw-sgp` except step 8, which needs a second namespace with a Pod Security
Admission label on it. No step changes a node flag, edits a kubelet config or restarts anything. The
offline reads are against the pinned checkout at `/path/to/kubernetes/website/content/en`; `W` below
is that path.

**Do**

1. Ground three claims at once: what the server says the field's stage is, what the gate is set to
   without anyone setting it, and what the node says about its runtime.

   ```sh
   kubectl version -o json | grep -E '"gitVersion"'
   kubectl explain pod.spec.securityContext.supplementalGroupsPolicy
   kubectl get --raw /metrics \
     | grep -o 'kubernetes_feature_enabled{name="SupplementalGroupsPolicy",stage="[^"]*"} [0-9]*'
   kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.features}{"\t"}{.status.nodeInfo.containerRuntimeVersion}{"\n"}{end}'
   kubectl create namespace bw-sgp
   ```

2. The post's first manifest, taken from the checkout rather than retyped, and the two commands
   `:32` and `:46` run against it. Then the half the post did not have in 2024: the status field.

   ```sh
   W=/path/to/kubernetes/website/content/en
   B=$W/blog/_posts/2024/fine-grained-supplementalgroups-control
   cat $B/implicit-groups.yaml
   kubectl -n bw-sgp apply -f $B/implicit-groups.yaml
   kubectl -n bw-sgp wait --for=condition=Ready pod/implicit-groups --timeout=180s
   kubectl -n bw-sgp exec implicit-groups -- id
   kubectl -n bw-sgp exec implicit-groups -- cat /etc/group
   kubectl -n bw-sgp get pod implicit-groups -o jsonpath='{.status.containerStatuses[0].user.linux}{"\n"}'
   kubectl -n bw-sgp get pod implicit-groups -o jsonpath='{.spec.securityContext.supplementalGroupsPolicy}{"\n"}'
   ```

3. The same manifest at this repository's image tag instead of the post's. Eight releases of agnhost
   separate them, and the entire demonstration rests on one line of one image's `/etc/group`.

   ```sh
   W=/path/to/kubernetes/website/content/en
   B=$W/blog/_posts/2024/fine-grained-supplementalgroups-control
   sed -e 's/agnhost:2.45/agnhost:2.53/' -e 's/name: implicit-groups/name: implicit-groups-253/' \
     $B/implicit-groups.yaml | kubectl -n bw-sgp apply -f -
   kubectl -n bw-sgp wait --for=condition=Ready pod/implicit-groups-253 --timeout=180s
   kubectl -n bw-sgp exec implicit-groups-253 -- id
   kubectl -n bw-sgp exec implicit-groups-253 -- grep 50000 /etc/group
   kubectl -n bw-sgp get pod implicit-groups-253 -o jsonpath='{.status.containerStatuses[0].user.linux}{"\n"}'
   ```

4. The post's second manifest, verbatim. One field changes; one group disappears.

   ```sh
   W=/path/to/kubernetes/website/content/en
   B=$W/blog/_posts/2024/fine-grained-supplementalgroups-control
   diff $B/implicit-groups.yaml $B/strict-supplementalgroups-policy.yaml
   kubectl -n bw-sgp apply -f $B/strict-supplementalgroups-policy.yaml
   kubectl -n bw-sgp wait --for=condition=Ready pod/strict-supplementalgroups-policy --timeout=180s
   kubectl -n bw-sgp exec strict-supplementalgroups-policy -- id
   kubectl -n bw-sgp exec strict-supplementalgroups-policy -- cat /etc/group
   kubectl -n bw-sgp get pod strict-supplementalgroups-policy \
     -o jsonpath='{.status.containerStatuses[0].user.linux}{"\n"}'
   ```

5. Now the task page's version of the same Pod, pulled over the network from the URL scheme the
   documentation uses. Compare what it contains with the post's bundled file, and compare the status
   it reports with the YAML the post prints at `:104-117`.

   ```sh
   kubectl -n bw-sgp apply -f https://k8s.io/examples/pods/security/security-context-6.yaml
   kubectl -n bw-sgp wait --for=condition=Ready pod/security-context-demo --timeout=180s
   kubectl -n bw-sgp exec security-context-demo -- id
   kubectl -n bw-sgp get pod security-context-demo -o jsonpath='{.status.containerStatuses[0].user}{"\n"}'
   W=/path/to/kubernetes/website/content/en
   diff $W/examples/pods/security/security-context-6.yaml \
        $W/blog/_posts/2024/fine-grained-supplementalgroups-control/strict-supplementalgroups-policy.yaml
   ```

6. Three submissions the API server should refuse, one at a time, none of them creating anything. A
   value that is not in the enum; the field on a Windows Pod; and the field on a container rather
   than on the Pod.

   ```sh
   cat <<'YAML' | kubectl -n bw-sgp apply --dry-run=server --validate=strict -f -
   apiVersion: v1
   kind: Pod
   metadata: {name: bw-bad-enum}
   spec:
     securityContext: {runAsUser: 1000, supplementalGroupsPolicy: Stricter}
     containers: [{name: ctr, image: registry.k8s.io/e2e-test-images/agnhost:2.53, command: ["sleep","1h"]}]
   YAML
   cat <<'YAML' | kubectl -n bw-sgp apply --dry-run=server --validate=strict -f -
   apiVersion: v1
   kind: Pod
   metadata: {name: bw-windows}
   spec:
     os: {name: windows}
     securityContext: {supplementalGroupsPolicy: Strict}
     containers: [{name: ctr, image: registry.k8s.io/e2e-test-images/agnhost:2.53, command: ["sleep","1h"]}]
   YAML
   cat <<'YAML' | kubectl -n bw-sgp apply --dry-run=server --validate=strict -f -
   apiVersion: v1
   kind: Pod
   metadata: {name: bw-container-level}
   spec:
     containers:
     - name: ctr
       image: registry.k8s.io/e2e-test-images/agnhost:2.53
       command: ["sleep","1h"]
       securityContext: {supplementalGroupsPolicy: Strict}
   YAML
   ```

7. `Strict` is documented as attaching the IDs named in `fsGroup`, `supplementalGroups` or
   `runAsGroup`. Neither the post nor the task page sets `fsGroup`, so this is the one field in that
   list neither example exercises.

   ```sh
   W=/path/to/kubernetes/website/content/en
   B=$W/blog/_posts/2024/fine-grained-supplementalgroups-control
   sed -e 's/name: strict-supplementalgroups-policy/name: strict-with-fsgroup/' \
       -e 's/^    supplementalGroups: \[4000\]/    supplementalGroups: [4000]\n    fsGroup: 2000/' \
       $B/strict-supplementalgroups-policy.yaml | tee /tmp/strict-fsgroup.yaml | grep -A5 securityContext
   kubectl -n bw-sgp apply -f /tmp/strict-fsgroup.yaml
   kubectl -n bw-sgp wait --for=condition=Ready pod/strict-with-fsgroup --timeout=180s
   kubectl -n bw-sgp exec strict-with-fsgroup -- id
   kubectl -n bw-sgp get pod strict-with-fsgroup -o jsonpath='{.status.containerStatuses[0].user.linux}{"\n"}'
   ```

8. The claim at `:93`, tested against the strictest thing Kubernetes ships. This Pod satisfies every
   `restricted` control and sets no `supplementalGroupsPolicy`, so it defaults to `Merge`.

   ```sh
   kubectl create namespace bw-sgp-restricted
   kubectl label namespace bw-sgp-restricted \
     pod-security.kubernetes.io/enforce=restricted pod-security.kubernetes.io/enforce-version=latest
   cat <<'YAML' | kubectl -n bw-sgp-restricted apply -f -
   apiVersion: v1
   kind: Pod
   metadata:
     name: compliant-and-merged
   spec:
     securityContext:
       runAsNonRoot: true
       runAsUser: 1000
       runAsGroup: 3000
       supplementalGroups: [4000]
       seccompProfile: {type: RuntimeDefault}
     containers:
     - name: ctr
       image: registry.k8s.io/e2e-test-images/agnhost:2.53
       command: ["sh", "-c", "sleep 1h"]
       securityContext:
         allowPrivilegeEscalation: false
         capabilities: {drop: ["ALL"]}
   YAML
   kubectl -n bw-sgp-restricted wait --for=condition=Ready pod/compliant-and-merged --timeout=180s
   kubectl -n bw-sgp-restricted exec compliant-and-merged -- id
   kubectl -n bw-sgp-restricted get pod compliant-and-merged \
     -o jsonpath='{.status.containerStatuses[0].user.linux}{"\n"}'
   ```

9. Both URL schemes, side by side. One is the documentation's and resolves to a file; the other is
   this post's, twice, and resolves to nothing.

   ```sh
   for u in \
     'https://k8s.io/examples/pods/security/security-context-6.yaml' \
     'https://k8s.io/blog/2024-08-22-Fine-grained-SupplementalGroups-control/implicit-groups.yaml' \
     'https://k8s.io/blog/2024-08-22-Fine-grained-SupplementalGroups-control/strict-supplementalgroups-policy.yaml' \
     'https://k8s.io/blog/2024/08/22/fine-grained-supplementalgroups-control/implicit-groups.yaml'; do
     printf '%s  %s\n' "$(curl -sSL -o /dev/null -w '%{http_code}' "$u")" "$u"
   done
   ```

10. Offline, against the pinned checkout. The spelling census, the three stages in three files, the
    zero the Pod Security Standards return, and the two definitions of the node boolean.

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -rn 'SupplementaryGroups' --include='*.md' . | wc -l
    grep -rn 'SupplementaryGroups' --include='*.md' .
    grep -n '(Alpha)' docs/reference/kubernetes-api/core/pod-v1.md | grep -i supplemental | sed -e 's/<[^>]*>//g' | cut -c1-200
    cat docs/reference/command-line-tools-reference/feature-gates/SupplementalGroupsPolicy.md
    grep -rn 'supplementalGroupsPolicy' --include='*.md' docs | cut -d: -f1 | sort -u
    grep -c 'supplementalGroups' docs/concepts/security/pod-security-standards.md
    sed -n '235,239p;329,342p' docs/tasks/configure-pod-container/security-context.md
    sed -n '424,425p' docs/reference/kubernetes-api/core/node-v1.md | sed -e 's/<[^>]*>//g'
    grep -rn 'kubectl apply -f https://k8s.io/blog/' --include='*.md' blog | wc -l
    sed -n '3p;13p' blog/_posts/2025/fine-grained-supplementalgroups-control-ga.md
    ```

**Expect**

Step 1 prints `v1.35`. `kubectl explain` describes the field, gives `Merge` and `Strict`, and — this
is the thing to notice — includes the string *(Alpha)* in the description it got from the server's
own OpenAPI. The metrics line reports the gate at stage `BETA` with value `1`, which nobody set. The
node prints `map[supplementalGroupsPolicy:true]` and a `containerRuntimeVersion` of
`containerd://2.2.1`. Three different answers about the same feature's maturity, from one cluster,
before anything has been created.

Step 2 reproduces `:38` exactly: `uid=1000 gid=3000 groups=3000,4000,50000`. `/etc/group` ends with
`group-defined-in-image:x:50000:user-defined-in-image`, matching `:48-49`. The
`supplementalGroupsPolicy` read-back is empty, because the manifest does not set it and the API
server does not default it into the spec — `Merge` is the behaviour, not a stored value. The status
field, which the post prints at `:104-117` only for the `Strict` Pod, here reports
`{"gid":3000,"supplementalGroups":[3000,4000,50000],"uid":1000}`: the group nobody granted, named in
the API, on the object. That is the detection the post's `:58` said was impossible — and it is on
`.status`, after admission.

Step 3 tells you whether the post can still be run as written. If `agnhost:2.53` still carries the
`50000` entry, `id` prints the same three groups and the post's demonstration is intact eight image
releases on. If it does not, the `grep` finds nothing, `id` prints `groups=3000,4000`, and the
post's headline output has become unreproducible for anyone who updates the image — while looking
exactly like a `Strict` result. Record which happened; everything else in this exercise works either
way, and step 8 uses `2.53` deliberately.

Step 4 gives `uid=1000 gid=3000 groups=3000,4000`, matching `:88`. The `diff` should show two
differences and no more: the Pod name, and the single added line `supplementalGroupsPolicy: Strict`.
`/etc/group` inside the container is unchanged — the entry is still there, and the container's user
still belongs to that group as far as the file is concerned; only the process's attached group list
is different. The status field reports `{"gid":3000,"supplementalGroups":[3000,4000],"uid":1000}`.

Step 5 is the same Pod under a different name, fetched over the network. The `diff` should report
exactly two differing lines, the `metadata.name` and the container `name`, which is worth seeing:
the task page and the post ship byte-identical demonstrations under two names, both pinned to
`agnhost:2.45`. The `id` output matches step 4's, the `.user` read-back prints a single `linux` key
— the `ContainerUser` wrapper of `pod-v1.md:1037-1049` — and the apply succeeded, which is the
control for step 9.

Step 6 should produce three refusals and create nothing. The first names the field and lists the two
values it accepts. The second refuses because `spec.os.name: windows` forbids this part of the Pod
security context, the restriction `pod-v1.md:149` describes in general. The third is refused by
`--validate=strict` as an unknown field on a container's security context, because
`supplementalGroupsPolicy` exists only at Pod level — which is also why *fine-grained* in the title
means per-Pod and not per-container. If any of the three is accepted, note which, because two of
them are enum and schema checks that do not depend on the gate at all.

Step 7 answers a question neither example asks. `fsGroup: 2000` is a source of supplementary groups
under `Strict` by the field's own documentation, so expect `id` to print `uid=1000 gid=3000
groups=2000,3000,4000` and the status to list all three. The ordering may differ. What this does not
show is anything about volumes, which is [the 2020
exercise's](../2020/09-kubernetes-release-1-20-fsgroupchangepolicy-fsgrouppolicy.md) subject; there
is no volume here on purpose.

Step 8 is the point of the exercise. The namespace label is accepted, and so is the Pod: no warning,
no rejection, nothing in the events about security context. `restricted` is satisfied. And `id`
prints `groups=3000,4000,50000` — assuming step 3 found the entry present in `2.53` — with the
status field naming `50000` outright. The strictest policy Kubernetes ships has admitted a Pod
carrying a group that appears in no manifest, no namespace label and no policy, because there is no
control for it to check. That is `:58` and `:93` of the post, unresolved, two years and one GA
later.

Step 9 prints four status codes. The documentation's `k8s.io/examples/` URL answers `200`. The
post's two answer `404`, or whatever the site returns for an unmapped blog path. The fourth line is
the guess at what the post probably meant — the published slug plus the file name — and it is there
to show that even the charitable reading does not resolve, because page-bundle resources are not
served from the post's URL. If any of the three answers `200`, the site has grown a redirect since
the pin and the finding narrows to the source tree, which step 10's last line measures instead. If
the node has no egress, skip this step and rely on step 10.

Step 10 is all reading. The spelling census returns `1`, and the single line is the post's own `:60`
heading. The `(Alpha)` grep returns the `supplementalGroupsPolicy` row of `pod-v1.md`. The gate
record prints with an alpha stage, a beta stage and no stable stage. The file list returns exactly
three paths — `node-v1.md`, `pod-v1.md`, `security-context.md` — for a GA feature. The Pod Security
Standards count is `0`. The task-page extract shows the feature-state shortcode reading the gate by
name, the instruction to enable it, and the note that still describes the alpha in the present tense
alongside the beta behaviour that replaced it. `node-v1.md:425` gives the one boolean for two
features. The final count is `2`: both in this post. And the last two lines are the project
announcing, in the release this cluster is running, that the feature whose gate record you just
printed is generally available.

**Read on**

11. [The exercise on granular control of volume permission
    changes](../2020/09-kubernetes-release-1-20-fsgroupchangepolicy-fsgrouppolicy.md) — `fsGroup` in
    full, including what it costs to apply and which driver capability decides whether it is applied
    at all.

12. [The exercise on the runc container breakout CVE](../2019/02-runc-cve-2019-5736.md) — the
    security-context task page's first example, and the same Pod shape being refused by `restricted`
    for every reason except the one this exercise is about.

13. [The exercise on recursive read-only mounts](03-recursive-read-only-mounts.md) — the other half
    of the node status read in step 1, and the row that reserved this field for this one.

14. [The user namespaces beta exercise](02-userns-beta.md) — uid and gid treated as a containment
    boundary rather than as a merge rule, and the other 2024 feature whose availability is gated on
    a runtime version.

15. [The lab where `restricted` names every field a pod is
    missing](../../labs/10/06-restricted-rejects-a-pod-you-can-name.md) — how Pod Security Admission
    phrases a refusal, which is the direction step 8 above deliberately does not go.

**Teardown**

```sh
kubectl delete namespace bw-sgp bw-sgp-restricted --wait=true
rm -f /tmp/strict-fsgroup.yaml
kubectl get nodes -o wide
```
