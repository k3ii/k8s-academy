<a id="kubernetes-v1-35-introducing-workload-aware-scheduling"></a>

# Every identifier in this post's two YAML blocks is a dead spelling at the pin: the API group has worn four version strings, two of the three gates are among the shortest-lived the project has ever shipped, and the link from a group to its template has two shapes that cannot both be right

**Post** — [Kubernetes v1.35: Introducing Workload Aware Scheduling](https://kubernetes.io/blog/2025/12/29/kubernetes-v1-35-introducing-workload-aware-scheduling/),
2025-12-29.

8,928 bytes, 183 lines, four fenced blocks, eleven links. Five of the links point into kubernetes.io
documentation and six leave it: four to `kubernetes/enhancements` or `kubernetes/kubernetes`, one to
a Slack channel. Two authors, both at Google.

**As written**

The post announces the `Workload` API, a new object that describes how the Pods of a multi-Pod
application should be scheduled together. Its argument is that the scheduler has only ever seen one
Pod at a time, and that AI and batch workloads need it to see a set: if a training job needs four
workers and only three fit, binding three of them wastes the nodes and starves everyone else.

It gives the API in two blocks. The first, at `:51-64`, is a `Workload` in
`scheduling.k8s.io/v1alpha1` whose `spec.podGroups` is a list, each entry carrying a `name` and a
`policy` with `gang.minCount: 4`. The second, at `:68-79`, is a Pod, and its prose at `:66`
introduces it as "the new `workloadRef` field": `spec.workloadRef` with a `name` naming the Workload
and a `podGroup` naming the group inside it.

The mechanism is described at `:90-103` in three numbered steps. The scheduler counts the Pods that
reference a group; when the count reaches `minCount` it tries to place them all; and each Pod that
finds a node is held at the `Permit` extension point, with a timeout the post gives as five minutes,
until every member of the gang has one. The post names one plugin, `GangScheduling`, as the thing
doing this.

A second feature rides along. Opportunistic batching, described at `:112-119`, reuses the
feasibility calculations from one scheduling cycle for the equivalent Pods behind it, and the post
says it is Beta in v1.35, on by default, with no opt-in. Its restrictions are at `:126-131`.

The `Getting started` section at `:157-167` names three feature gates. `GenericWorkload` on both
`kube-apiserver` and `kube-scheduler`, plus the `scheduling.k8s.io/v1alpha1` API group.
`GangScheduling` on `kube-scheduler` only, and it requires the first. `OpportunisticBatching`, which
you turn on by doing nothing and off by setting it false. The post closes with a north star vision
at `:141-148`: seven bullets of work not done yet, including topology-aware placement,
workload-aware preemption, and integration with dynamic resource allocation.

**As it runs now**

**The API group has worn four version strings, and three of them are live in the tree at once.** The
post writes `scheduling.k8s.io/v1alpha1` at `blog/_posts/2025/gang-scheduling.md:40` and `:161`.
That string occurs nowhere under `docs`. What does occur: the generated reference serves `v1alpha2`,
at `reference/kubernetes-api/scheduling/workload-v1alpha2.md:24` and `pod-group-v1alpha2.md:24`; the
concept pages write `v1beta1` in their YAML, eleven times across seven files; and `v1alpha3` appears
nine times, for the hierarchical types. Three releases, four spellings, and not one of them is the
post's.

**A group-version this documentation teaches is one the same documentation says stopped being
served.** `reference/using-api/deprecation-guide.md:290` says that the `scheduling.k8s.io/v1beta1`
API version of PriorityClass is no longer served as of v1.22. That is true of the kind it names. It
is the same group-version the concept pages now ask you to write in every `Workload` and `PodGroup`
manifest. Nothing on either page acknowledges the other.

**Both identifiers in the post's Workload block were renamed.** `spec.podGroups` became
`spec.podGroupTemplates`, and the `policy` key inside each entry became `schedulingPolicy`.
`concepts/workloads/workload-api/_index.md:61-81` carries the replacement, and the list it heads is
no longer a list of groups but a list of templates: `:27-30` says a `Workload` is "a static,
long-lived policy template" that "does not track runtime state itself", and that runtime state now
lives in separate `PodGroup` objects created from those templates. The post's object described the
gang. The pin's object describes what a gang would look like.

**The Pod-side field the post introduces as new does not exist on a Pod at the pin, in any
spelling.** `workloadRef` occurs twelve times under `docs` and not once on a `Pod`: it is a field of
`PodGroup` and `CompositePodGroup`. What a Pod carries instead is `spec.schedulingGroup`, documented
at `concepts/workloads/pods/scheduling-group.md:20-34` and present in the Pod reference at
`reference/kubernetes-api/core/pod-v1.md:196` as a `PodSchedulingGroup`. Its one field is
`podGroupName`. So the post's two-level reference from a Pod into a named group inside a Workload
became a one-level reference from a Pod to a `PodGroup` object, and the Workload dropped out of the
Pod's view entirely.

**The link from a group back to its template has two incompatible shapes, and both are in current
concept documentation.** `concepts/workloads/podgroup-api/_index.md:55-59` and `:197-200` write
`spec.podGroupTemplateRef.workload.{workloadName, podGroupTemplateName}` — three levels. The
topology page at `concepts/workloads/workload-api/topology-aware-scheduling.md:174-176` and every
example on `concepts/workloads/compositepodgroup-api/_index.md` write
`spec.workloadRef.{workloadName, templateName}` — two levels, a different field name, and a
different name for the inner key. `concepts/workloads/workload-api/_index.md:44` sides with the
first in prose; `concepts/workloads/controllers/job.md:400` sides with the second. Only one of them
can be the API.

**The generated reference settles it, and settles it against the pages with more examples.**
`reference/kubernetes-api/scheduling/pod-group-v1alpha2.md:76` documents `podGroupTemplateRef` and
nothing named `workloadRef`; its sub-fields, listed further down the same page, are `workloadName`
and `podGroupTemplateName`. Every `PodGroup` manifest on the topology and CompositePodGroup pages is
therefore a manifest the API as documented would reject. That is seven examples across two pages.

**A kind with five worked examples has no reference page at all.** `CompositePodGroup` occurs zero
times in the whole of `reference/kubernetes-api`. There are 284 lines of concept documentation for
it across `concepts/workloads/compositepodgroup-api/_index.md` and its `lifecycle.md`, five YAML
blocks, a nesting-depth limit and a list cap — and no generated type page, because the generator
runs against `v1alpha2` and `CompositePodGroup` is `v1alpha3`. The reference does not lag the
concept pages by a revision here. It is a version behind on purpose and nothing says so.

**One field's values are spelled five different ways.** `disruptionMode` appears as a lowercase map
key, `all: {}`, in the YAML at `concepts/workloads/workload-api/_index.md:79-80` and again at
`concepts/workloads/podgroup-api/_index.md:76-77`. Prose on the first of those pages, at `:135`,
calls the values `Single` or `All`. `concepts/workloads/controllers/job.md:345` calls them `single`
and `all`. The Go helper at `concepts/workloads/workload-api/workloadbuilder.md:220` names them
`SingleMode` and `AllMode`. And the generated reference, at
`reference/kubernetes-api/scheduling/pod-group-v1alpha2.md:73`, says the field is an enum of `Pod`
and `PodGroup`, defaulting to `Pod`. Not two of these five agree.

**The scheduling mechanism the post describes was replaced, and the pin names it as the thing that
was replaced.** There is no `Permit` gate in the gang path any more and no five-minute timeout:
`timeout` occurs zero times across the gang, PodGroup, Workload and CompositePodGroup pages.
`concepts/scheduling-eviction/podgroup-scheduling.md:30` opens the explanation with "Instead of
processing Pods individually and holding them at a `WaitOnPermit` gate", then describes a whole new
cycle that snapshots cluster state once, evaluates the group, and goes straight to binding. The
post's step three is the pin's counterexample.

**The new cycle brought a new extension point, and the page that enumerates extension points has
never heard of it.** `PlacementFeasible` occurs in exactly two files,
`concepts/scheduling-eviction/gang-scheduling.md` and `podgroup-scheduling.md`.
`concepts/scheduling-eviction/scheduling-framework.md` carries sixteen `###` headings, one per
extension point, and contains zero occurrences of `PlacementFeasible`, `PodGroup`, `Workload` or
`gang`. `reference/config-api/kube-scheduler-config.v1.md` contains zero occurrences of
`PlacementFeasible` and zero of `GangScheduling`. The framework grew a stage and the framework
reference does not mention it.

**Two of the post's three gates were removed within two releases, and they are the shortest-lived
removals in the tree.** 230 gate files carry `removed: true`. Ranked by the span from first stage to
last, `WorkloadAwarePreemption` — 1.36 to 1.36 — is one of six that lasted a single release, and the
only one of the six from after v1.19; the others are `Accelerators`,
`DynamicProvisioningScheduling`, `Initializers`, `MountContainers` and
`ResourceLimitsPriorityFunction`, all 1.11 to 1.19. `GangScheduling` — 1.35 to 1.36 — is one of four
that lasted two. Both were removed for the same reason, and their files say so: each ends with a
sentence that the gate "was removed in 1.37 and merged together with the `GenericWorkload` feature
gate".

**A gate that is still alive reached beta and stayed off.** `GenericWorkload` runs alpha at 1.35 and
1.36, then beta from 1.37 with `defaultValue: false`. Of the 258 gate files that do not carry
`removed: true`, six sit at beta-and-off as their current stage, and two of the six are this feature
area: `GenericWorkload` and `DRAWorkloadResourceClaims`. Reaching beta normally means the thing is
on unless you say otherwise. Here it means the gate list stopped growing, not that the feature
arrived.

**A live documentation page links a gate anchor that moved to the removed-gates page.**
`concepts/workloads/workload-api/_index.md:54` links
`/docs/reference/command-line-tools-reference/feature-gates/#WorkloadAwarePreemption`, in a note
explaining that the gate was merged away. The gate's file carries `_build: list: never, render:
false` and `removed: true`, which puts it under `feature-gates-removed`, not `feature-gates`. The
note is correct about the merge and wrong about where to read it.

**Two of the post's five documentation links no longer land.** `:162` links
`feature-gates/#GangScheduling`, and that gate is on the removed page now. `:142` links
`/docs/concepts/scheduling-eviction/dynamic-resource-allocation/`, which is not a file at the pin —
dynamic resource allocation lives under `concepts/resource-management/` — and
`static/_redirects.base` carries no rule for the old path. The remaining three, `#GenericWorkload`,
`#OpportunisticBatching` and the `scheduler-perf-tuning` anchor, all resolve:
`concepts/scheduling-eviction/scheduler-perf-tuning.md:162` is still `## Enabling Opportunistic
Batching`.

**The one feature the post said needed no action needed none.** `OpportunisticBatching` is beta with
`defaultValue: true` from 1.35 and carries no `toVersion`, so it has not moved at all in two
releases. The post's sentence at `:165-167` — on by default, disable it on `kube-scheduler` if you
must — is the only operational instruction in `Getting started` that is still exactly true.

**One identifier survived every rename.** `minCount` occurs 51 times under `docs`, is a required
field on the generated `PodGroup` type at
`reference/kubernetes-api/scheduling/pod-group-v1alpha2.md:171`, and appears in
`concepts/workloads/workload-api/policies.md:52-56` with the same value the post used, `4`. Around
it the group version changed three times, the enclosing list was renamed, the policy key was
renamed, the Pod field was replaced and the scheduling mechanism was rebuilt.

**A 183-line post grew 5,184 lines of documentation in two releases.** Nine concept files under
`concepts/workloads/` for the three new kinds, four more under `concepts/scheduling-eviction/`, and
two generated reference pages: 2,301 concept lines and 2,883 reference lines. Five of the concept
files carry trailing whitespace — `workloadbuilder.md` on five lines, `podgroup-scheduling.md` on
six, and three others on one or two each — and
`concepts/scheduling-eviction/workload-aware-preemption.md:30` opens a markdown link bracket it
never closes, so the page renders a literal `[` before the group name. The post itself carries one
trailing-whitespace line, at `:161`.

**The Job controller now builds all of this for you, and the page describing it uses the singular.**
`concepts/workloads/controllers/job.md:320-350` documents `.spec.scheduling` on a Job, gated by
`WorkloadWithJob`, which compiles into `Workload` and `PodGroup` objects before any Pod is created.
`:391` says the `Workload` contains "a `podGroupTemplate` compiled from `.spec.scheduling`"; the
field is `podGroupTemplates`. `:442` records the one case where the controller creates nothing: a
Pod template that already sets `.spec.template.spec.schedulingGroup`.

**What this exercise does not cover, and where it lives**

The `PreEnqueue` extension point itself belongs to [the 2022 scheduling-readiness
row](../2022/13-pod-scheduling-readiness-alpha.md), which created it and which says at its `:93-95`
and `:508-513` that what occupies it at the pin is gang scheduling and that a later year's row owns
that. This is that row. Nothing below re-derives what `PreEnqueue` is or how scheduling gates work;
step 9 counts the two mechanisms against each other and leaves the older one where it is written
down.

Asking an API server for an alpha group through `--runtime-config` is a mechanism [the 2019
API-removals row](../2019/08-api-deprecations-in-1-16.md) teaches at length, and [the 2022 dynamic
resource allocation row](../2022/12-dynamic-resource-allocation.md) has already made the point at
its `:24` and `:68` that an alpha group has to be asked for by name. Step 3 uses the flag and does
not explain it. Dynamic resource allocation itself, including what a `ResourceClaim` is, belongs to
that row; `DRAWorkloadResourceClaims` is named here only as one of the five gates that did not exist
when the post was published.

Admission plugin lists drifting away from the API server's own help text is settled by [the 2021 Pod
Security admission row](../2021/09-pod-security-admission-beta.md) at its `:113-119`, which counts
the gap exactly. Two of the nine names it lists as newly added, `PodGroupProtection` and
`PodGroupWorkloadExists`, are this feature area's, and that is the whole of what is said about them
here.

Job status, `.spec.managedBy` and what happens when nothing reconciles a Job belong to [the exercise
immediately before this one](10-kubernetes-v1-35-job-managedby-for-jobs-goes-ga.md), published in
the same month of the same release. `.spec.scheduling` on a Job is named in *As it runs now* and
read offline in step 10, but no Job in the steps below sets it: the objects here are made by hand,
because the point is which spellings the API server accepts, not which controller writes them.

The v1.36 and v1.37 instalments of this same series are `read` verdicts in the 2026 census, and both
of their `why` entries defer the API to this exercise. What they add — a release of field churn each
— is deliberately not chased here. The pin is one commit, and what it shows is the state after two
releases, not the path through them.

**The diff, and why**

***Broke.*** Every identifier in the post's two YAML blocks is a dead spelling. The group version,
the `podGroups` list, the `policy` key inside it, the Pod's `workloadRef` field and both of that
field's children. Copy either block into a cluster at the pin and nothing about it is right except
`kind: Workload`, `kind: Pod` and `minCount: 4`. This is the ordinary fate of an alpha API announced
in its first release, and the post says as much at `:44-45` — but the post also frames the two
blocks as what you should write, and a reader who writes them gets nothing back.

***A plan the project abandoned.*** The three-step mechanism at `:90-103` is not how gang scheduling
works at the pin and never became how it works. Holding placed Pods at `Permit` with a five-minute
timeout is a design; evaluating the whole group in one cycle against a single snapshot and going
straight to binding is a different design, and
`concepts/scheduling-eviction/podgroup-scheduling.md:30` introduces the second by naming the first
as what it replaced. The post is the only surviving description of the abandoned plan, and it does
not know that is what it is.

***Still right.*** Opportunistic batching, in every particular. Beta, on by default, no opt-in,
disable it on `kube-scheduler` if it gets in the way — the gate file has not gained a rung in two
releases. `minCount` survived intact, with the same name, the same meaning and the same example
value. The post's motivating argument survived too: nothing at the pin disputes that binding three
Pods of a four-Pod gang wastes the nodes.

***Retired by being agreed with.*** The north star at `:141-148` is seven bullets of work not done
yet. At the pin, topology-aware scheduling has two concept pages, workload-aware preemption has one
and a gate that has already been merged away for being uncontroversial, hierarchical groups have a
kind of their own, DRA integration has a gate, and the Job controller compiles Jobs into `Workload`
objects. The section that reads most like speculation is the section that dated fastest, and it
dated by being built. What it cost was the vocabulary: almost none of it arrived under the names the
post used.

**The ladder**

Eight gate files describe this feature area at the pin, and reading their frontmatter in one pass is
the fastest way to see two releases of churn. `GenericWorkload` is alpha with `defaultValue: false`
from 1.35 to 1.36, then beta from 1.37, still `false`. `OpportunisticBatching` is beta with
`defaultValue: true` from 1.35 and has no second rung. `GangScheduling` is alpha from 1.35 to 1.36
and then `removed: true`. `WorkloadAwarePreemption` is alpha at 1.36 only, then `removed: true`.
`TopologyAwareWorkloadScheduling` and `WorkloadWithJob` are alpha from 1.36; `CompositePodGroup` and
`PodGroupPreemptionPolicy` are alpha from 1.37. `DRAWorkloadResourceClaims` is alpha at 1.36 and
beta, off, from 1.37.

Of those, the post names three. Five did not exist when it was published, and one of the five,
`CompositePodGroup`, describes a kind the post's model has no room for. The lab runs v1.35, which is
the post's own release, so the ladder the cluster can show you is the first rung of each — and for
two of the eight gates, the first rung is the only rung there will ever be.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180`, Kubernetes v1.35,
[provisioned](../../strands/lab-topologies.md#provision) and
[baselined](../../strands/lab-topologies.md#node-baseline-steps) as usual. The version matters more
here than in most rows: v1.35 is the release this post announces, so the cluster is the one the post
was written for, and steps 2 to 7 are the post's own instructions carried out on its own release.
Everything lives in a namespace called `bw-workload`, with a scratch directory at
`/tmp/bw-workload`. Step 3 edits two static Pod manifests on the node over `ssh zain@10.10.10.180`
and restarts the control plane by doing so; *Teardown* puts both back from the backups step 3 takes
first, and a `solo` node that will not come back is one
[re-provision](../../strands/lab-topologies.md#provision) away. Steps 8 to 10 are offline, against a
checkout of `kubernetes/website` at the pin, with `W` set to its `content/en` directory.

**Do**

1. What this cluster serves, before the post is opened. The point of doing this first is that every
   later refusal has to be read against it.

   ```sh
   mkdir -p /tmp/bw-workload && cd /tmp/bw-workload
   kubectl version
   kubectl create namespace bw-workload

   kubectl api-versions | grep -i scheduling
   kubectl api-resources --api-group=scheduling.k8s.io
   kubectl get --raw /apis/scheduling.k8s.io | tr ',' '\n' | grep -i version

   for FLD in schedulingGroup workloadRef; do
     echo "--- pod.spec.$FLD"
     kubectl explain "pod.spec.$FLD" 2>&1 | head -6
   done

   kubectl -n kube-system get pod -l component=kube-scheduler \
     -o jsonpath='{.items[0].spec.containers[0].command}' | tr ',' '\n' | grep -i 'feature\|config' || echo "no feature-gates flag on kube-scheduler"
   kubectl -n kube-system get pod -l component=kube-apiserver \
     -o jsonpath='{.items[0].spec.containers[0].command}' | tr ',' '\n' | grep -i 'feature\|runtime-config' || echo "no feature-gates flag on kube-apiserver"
   ```

2. The post's two blocks, copied out of `:51-64` and `:68-79` without a character changed except
   one. The Pod block ends in a literal `...` where its containers would be, so it gets a container;
   nothing else is touched, and in particular the `apiVersion` line stays as the post wrote it.

   ```sh
   cd /tmp/bw-workload
   cat > post-workload.yaml <<'EOF'
   apiVersion: scheduling.k8s.io/v1alpha1
   kind: Workload
   metadata:
     name: training-job-workload
     namespace: bw-workload
   spec:
     podGroups:
     - name: workers
       policy:
         gang:
           # The gang is schedulable only if 4 pods can run at once
           minCount: 4
   EOF

   cat > post-pod.yaml <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: worker-0
     namespace: bw-workload
   spec:
     workloadRef:
       name: training-job-workload
       podGroup: workers
     containers:
     - name: worker
       image: registry.k8s.io/e2e-test-images/agnhost:2.53
       command: ["sleep", "3600"]
   EOF

   for F in post-workload.yaml post-pod.yaml; do
     echo "=== $F"
     kubectl apply -f "$F" --dry-run=server 2>&1 | head -8
   done
   ```

3. Turn on what `:157-164` tells you to turn on. Both gates, both components, plus the API group,
   which the post mentions in half a sentence and which is a separate flag. Back the manifests up
   first: step 3 is the only step that can leave the node without a control plane.

   ```sh
   ssh zain@10.10.10.180 "sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/bw-apiserver.yaml.bak \
     && sudo cp /etc/kubernetes/manifests/kube-scheduler.yaml /tmp/bw-scheduler.yaml.bak \
     && ls -l /tmp/bw-*.bak"

   ssh zain@10.10.10.180 "sudo sed -i '/- kube-apiserver\$/a\\    - --feature-gates=GenericWorkload=true' /etc/kubernetes/manifests/kube-apiserver.yaml \
     && sudo sed -i '/- kube-apiserver\$/a\\    - --runtime-config=scheduling.k8s.io/v1alpha1=true' /etc/kubernetes/manifests/kube-apiserver.yaml \
     && sudo grep -n 'feature-gates\|runtime-config' /etc/kubernetes/manifests/kube-apiserver.yaml"

   ssh zain@10.10.10.180 "sudo sed -i '/- kube-scheduler\$/a\\    - --feature-gates=GenericWorkload=true,GangScheduling=true' /etc/kubernetes/manifests/kube-scheduler.yaml \
     && sudo grep -n 'feature-gates' /etc/kubernetes/manifests/kube-scheduler.yaml"

   echo "waiting for the API server"
   until kubectl version >/dev/null 2>&1; do sleep 5; done
   kubectl -n kube-system get pods -l 'component in (kube-apiserver,kube-scheduler)'
   ssh zain@10.10.10.180 "sudo crictl ps -a --name kube-scheduler | head -5"
   ```

4. Ask the same questions as step 1, then retry the post's own blocks against the release the post
   was written for. Record exactly what changed and what did not.

   ```sh
   cd /tmp/bw-workload
   kubectl api-versions | grep -i scheduling
   kubectl api-resources --api-group=scheduling.k8s.io

   for F in post-workload.yaml post-pod.yaml; do
     echo "=== $F"
     kubectl apply -f "$F" --dry-run=server 2>&1 | head -12
   done

   kubectl explain workload 2>&1 | head -20
   kubectl explain workload.spec 2>&1 | head -20
   ```

5. The pin's spelling of the same idea, from `concepts/workloads/workload-api/_index.md:61-81`,
   `concepts/workloads/podgroup-api/_index.md:192-215` and
   `concepts/workloads/pods/scheduling-group.md:22-34`. The `GROUP` variable holds whatever step 4
   found the cluster actually serves, so the three manifests are the pin's shapes on the cluster's
   version. Every field the server strips or refuses is the answer.

   ```sh
   cd /tmp/bw-workload
   GROUP=$(kubectl api-versions | grep '^scheduling.k8s.io/' | grep -v 'scheduling.k8s.io/v1$' | head -1)
   echo "GROUP=$GROUP"

   cat > pin-workload.yaml <<EOF
   apiVersion: $GROUP
   kind: Workload
   metadata:
     name: training-policy
     namespace: bw-workload
   spec:
     controllerRef:
       apiGroup: batch
       kind: Job
       name: training-job
     podGroupTemplates:
     - name: worker
       schedulingPolicy:
         gang:
           minCount: 4
   EOF

   kubectl apply -f pin-workload.yaml --dry-run=server -o yaml 2>&1 | head -30
   kubectl apply -f pin-workload.yaml 2>&1 | head -5
   kubectl get workload -n bw-workload -o yaml 2>&1 | grep -v 'managedFields' | head -40
   ```

6. The two shapes of the template link, one after the other, against the same server. Only one of
   them can be the API, and the concept pages are split between them:
   `concepts/workloads/podgroup-api/_index.md:197-200` writes the first,
   `concepts/workloads/workload-api/topology-aware-scheduling.md:174-176` writes the second.

   ```sh
   cd /tmp/bw-workload
   GROUP=$(kubectl api-versions | grep '^scheduling.k8s.io/' | grep -v 'scheduling.k8s.io/v1$' | head -1)

   cat > ref-a.yaml <<EOF
   apiVersion: $GROUP
   kind: PodGroup
   metadata:
     name: shape-a
     namespace: bw-workload
   spec:
     podGroupTemplateRef:
       workload:
         workloadName: training-policy
         podGroupTemplateName: worker
     schedulingPolicy:
       gang:
         minCount: 4
   EOF

   cat > ref-b.yaml <<EOF
   apiVersion: $GROUP
   kind: PodGroup
   metadata:
     name: shape-b
     namespace: bw-workload
   spec:
     workloadRef:
       workloadName: training-policy
       templateName: worker
     schedulingPolicy:
       gang:
         minCount: 4
   EOF

   for F in ref-a.yaml ref-b.yaml; do
     echo "=== $F"
     kubectl apply -f "$F" --dry-run=server --validate=strict 2>&1 | head -8
   done

   kubectl explain podgroup.spec 2>&1 | head -25
   ```

7. `disruptionMode`, one spelling at a time. Five places in the pinned tree name this field's values
   and no two of them agree; the server accepts at most one set. `--validate=strict` matters here,
   because without it an unknown key is dropped in silence and every spelling looks correct.

   ```sh
   cd /tmp/bw-workload
   GROUP=$(kubectl api-versions | grep '^scheduling.k8s.io/' | grep -v 'scheduling.k8s.io/v1$' | head -1)

   cat > dm-tmpl.yaml <<EOF
   apiVersion: $GROUP
   kind: PodGroup
   metadata:
     name: dm-probe
     namespace: bw-workload
   spec:
     schedulingPolicy:
       gang:
         minCount: 2
     disruptionMode: MODEVALUE
   EOF

   for V in 'Pod' 'PodGroup' 'Single' 'All' 'single' 'all'; do
     echo "--- disruptionMode: $V"
     sed "s|MODEVALUE|$V|" dm-tmpl.yaml | kubectl apply -f - --dry-run=server --validate=strict 2>&1 | head -3
   done

   echo "--- disruptionMode as a map, the shape the YAML examples use"
   sed 's|  disruptionMode: MODEVALUE|  disruptionMode:\n    all: {}|' dm-tmpl.yaml \
     | kubectl apply -f - --dry-run=server --validate=strict 2>&1 | head -3
   ```

8. Offline from here. `W` is the `content/en` directory of a checkout of `kubernetes/website` at the
   pin. The eight gate files of this feature area, their ladders read straight out of the
   frontmatter, and then the two removals placed against every other removal in the tree.

   ```sh
   W=/path/to/kubernetes/website/content/en
   G=$W/docs/reference/command-line-tools-reference/feature-gates

   for N in GenericWorkload OpportunisticBatching GangScheduling WorkloadAwarePreemption \
            TopologyAwareWorkloadScheduling WorkloadWithJob CompositePodGroup \
            PodGroupPreemptionPolicy DRAWorkloadResourceClaims; do
     echo "=== $N"
     sed -n '/^stages:/,/^---$/p' "$G/$N.md" | grep 'stage:\|defaultValue\|Version' | tr -d ' '
     grep -H '^removed:\|^locked:' "$G/$N.md" 2>/dev/null | sed "s|$G/||"
   done

   echo "--- gate files carrying removed: true"
   grep -rl '^removed: true' "$G" | wc -l
   echo "--- gate files without it"
   ls "$G"/*.md | wc -l

   echo "--- every removed gate whose first stage is 1.30 or later"
   for F in $(grep -rl '^removed: true' "$G"); do
     FV=$(grep -m1 'fromVersion' "$F" | tr -d ' "' | cut -d: -f2)
     case "$FV" in 1.3*) echo "$FV $(basename $F .md)";; esac
   done | sort -t. -k2 -n

   echo "--- the merge sentence, and who else carries one like it"
   grep -rn 'merged together with' "$G" | sed "s|$G/||"
   ```

9. Where the mechanism went. The post's `Permit`-and-timeout design against the pin's
   group-scheduling cycle, and the extension point the new cycle added against the page that
   enumerates extension points.

   ```sh
   W=/path/to/kubernetes/website/content/en
   cd "$W"

   echo "--- the post's own words"
   grep -n 'Permit\|timeout\|5 minutes' blog/_posts/2025/gang-scheduling.md

   echo "--- Permit and WaitOnPermit under docs"
   grep -rn 'WaitOnPermit' docs | sed 's/:.*//' | sort | uniq -c
   grep -rln 'Permit' docs/concepts docs/reference/scheduling 2>/dev/null | sort

   echo "--- the sentence that names the replaced mechanism"
   sed -n '28,33p' docs/concepts/scheduling-eviction/podgroup-scheduling.md

   echo "--- timeout anywhere in the new pages"
   grep -rc -i 'timeout' docs/concepts/scheduling-eviction/gang-scheduling.md \
     docs/concepts/scheduling-eviction/podgroup-scheduling.md \
     docs/concepts/workloads/podgroup-api/*.md docs/concepts/workloads/workload-api/*.md

   echo "--- extension points the framework page lists"
   grep -c '^### ' docs/concepts/scheduling-eviction/scheduling-framework.md
   grep -n '^### ' docs/concepts/scheduling-eviction/scheduling-framework.md | tail -5

   echo "--- what the framework page has never heard of"
   for T in PlacementFeasible PodGroup Workload gang; do
     printf '%-20s framework=%s config-api=%s\n' "$T" \
       "$(grep -c "$T" docs/concepts/scheduling-eviction/scheduling-framework.md)" \
       "$(grep -c "$T" docs/reference/config-api/kube-scheduler-config.v1.md)"
   done
   grep -rl 'PlacementFeasible' docs
   ```

10. The three counts that size the gap: how many version strings the group wears, whether the post's
    five documentation links still land, and how much documentation grew out of 183 lines.

    ```sh
    W=/path/to/kubernetes/website/content/en
    cd "$W"

    echo "--- every version string the group wears, by file"
    grep -rn 'scheduling\.k8s\.io/v1[a-z0-9]*' docs \
      | sed 's/\(^[^:]*\):.*\(scheduling\.k8s\.io\/v1[a-z0-9]*\).*/\2 \1/' \
      | sort | uniq -c | sort -k2
    echo "--- and what the post writes"
    grep -n 'scheduling\.k8s\.io/v1[a-z0-9]*' blog/_posts/2025/gang-scheduling.md

    echo "--- the post's five docs links, resolved against the tree"
    for L in 'concepts/scheduling-eviction/dynamic-resource-allocation' \
             'concepts/scheduling-eviction/scheduler-perf-tuning' \
             'reference/command-line-tools-reference/feature-gates/GangScheduling' \
             'reference/command-line-tools-reference/feature-gates/GenericWorkload' \
             'reference/command-line-tools-reference/feature-gates/OpportunisticBatching'; do
      if [ -f "docs/$L.md" ] || [ -f "docs/$L/_index.md" ]; then S=present; else S=MISSING; fi
      printf '%-8s %s\n' "$S" "$L"
    done
    grep -c 'dynamic-resource-allocation' ../../static/_redirects.base
    grep -n '^removed: true' docs/reference/command-line-tools-reference/feature-gates/GangScheduling.md
    grep -rn 'feature-gates/#GangScheduling\|feature-gates/#WorkloadAwarePreemption' docs

    echo "--- how much grew"
    wc -l blog/_posts/2025/gang-scheduling.md
    wc -l docs/concepts/workloads/workload-api/*.md docs/concepts/workloads/podgroup-api/*.md \
          docs/concepts/workloads/compositepodgroup-api/*.md \
          docs/concepts/workloads/pods/scheduling-group.md \
          docs/concepts/scheduling-eviction/gang-scheduling.md \
          docs/concepts/scheduling-eviction/podgroup-scheduling.md \
          docs/concepts/scheduling-eviction/topology-aware-scheduling.md \
          docs/concepts/scheduling-eviction/workload-aware-preemption.md | tail -1
    wc -l docs/reference/kubernetes-api/scheduling/workload-v1alpha2.md \
          docs/reference/kubernetes-api/scheduling/pod-group-v1alpha2.md \
          docs/reference/kubernetes-api/definitions/typed-local-object-reference-v1alpha2-scheduling.md | tail -1
    grep -rc 'CompositePodGroup' docs/reference/kubernetes-api/scheduling/*.md

    echo "--- and what it costs to read it"
    for F in docs/concepts/workloads/workload-api/workloadbuilder.md \
             docs/concepts/workloads/podgroup-api/_index.md \
             docs/concepts/scheduling-eviction/podgroup-scheduling.md \
             docs/concepts/scheduling-eviction/topology-aware-scheduling.md \
             docs/concepts/scheduling-eviction/workload-aware-preemption.md; do
      printf '%2s %s\n' "$(grep -c ' $' $F)" "$F"
    done
    sed -n '30p' docs/concepts/scheduling-eviction/workload-aware-preemption.md
    ```

**Expect**

Step 1 establishes the floor. `kubectl version` prints v1.35 on both client and server. `kubectl
api-versions | grep -i scheduling` prints `scheduling.k8s.io/v1` and nothing else, because the only
kind in that group a default kubeadm cluster serves is `PriorityClass` — `kubectl api-resources
--api-group=scheduling.k8s.io` shows exactly one row. `kubectl explain pod.spec.schedulingGroup` and
`pod.spec.workloadRef` both fail: the first because the field is gated, the second because at no
version does a Pod have it. Neither control-plane component carries a `--feature-gates` flag,
because kubeadm does not add one, so the two `||` branches fire and print their fallbacks. Record
the one served version string; steps 4 and 5 are read against it.

Step 2 is refused twice, and the two refusals are different in kind. The Workload is rejected before
validation with a message about no matches for kind `Workload` in version
`scheduling.k8s.io/v1alpha1` — the API server has no such group-version, so there is nothing to
validate against. The Pod is rejected by validation, with `unknown field "spec.workloadRef"`,
because a Pod is a kind the server knows and `workloadRef` is a key on it that it does not.
Server-side apply is strict about unknown fields by default, which is why this fails without
`--validate=strict`; note that, because step 7 needs the flag and step 2 does not, and the
difference is the whole reason step 7 needs it.

Step 3 takes about a minute. The backups land in `/tmp` on the node; check the `ls -l` output before
going further, because *Teardown* depends on them. The three `sed` insertions each add one line
after the command name, and the `grep -n` after each confirms it: one `--feature-gates` and one
`--runtime-config` line on the API server, one `--feature-gates` line on the scheduler. The kubelet
notices the manifest change within about twenty seconds and restarts both static Pods, so `kubectl
version` fails for a while — that is what the `until` loop is for. If it never comes back, the API
server is refusing a flag; `sudo crictl logs` on the exited container says which, and *Teardown*
restores the backups. Expect the scheduler to restart cleanly whatever the API server does, because
the scheduler does not parse `--runtime-config`.

Step 4 is where the post either comes back to life or does not, and both outcomes are findings. If
the group is served, `kubectl api-versions` now prints a second `scheduling.k8s.io` entry alongside
`v1`, `api-resources` grows rows for `workloads` and `podgroups`, and the post's Workload applies
cleanly under `--dry-run=server` while the post's Pod still does not, because `spec.workloadRef` on
a Pod is not a field the v1.35 API server has either. If the version string the server exposes is
not the `v1alpha1` the post wrote, both blocks still fail and the reason has changed: the post is
now wrong about the version, not about the shape. `kubectl explain workload.spec` settles it either
way, and whichever list of fields it prints is the one step 5 builds against.

Step 5 hands the decision to the server. `GROUP` picks the first non-`v1` version the cluster
advertises, so the manifest is the pin's field names on the cluster's version string. Expect
`podGroupTemplates` and `schedulingPolicy` to be accepted if the group is served at all — these are
the names the API has carried since the shape settled, and the pin's YAML at
`concepts/workloads/workload-api/_index.md:61-81` is the same shape. The interesting output is the
round trip: `kubectl get workload -o yaml` prints what the server stored, and any field it dropped
in silence was never a field. Compare its `apiVersion` line with the one the manifest asked for.

Step 6 is the one that cannot be argued with. Both manifests are the same object with the same
policy and two different ways of naming the template it came from, and `--validate=strict` means
neither can succeed by having its unknown key dropped. One is accepted and the other is refused with
`unknown field`. Whichever wins, five to seven published examples in the pinned concept
documentation are written the other way — `concepts/workloads/podgroup-api/_index.md` uses the
three-level form twice, and `topology-aware-scheduling.md` and `compositepodgroup-api/_index.md`
between them use the two-level form seven times. `kubectl explain podgroup.spec` names the survivor
without ambiguity.

Step 7 prints seven results and at most one of them is an acceptance. The generated reference says
the values are `Pod` and `PodGroup`; the concept prose says `Single` and `All`; the Job page says
`single` and `all`; and the YAML examples on two concept pages write the field as a map with an
`all: {}` key, which is not a string at all and will fail differently — a type error rather than an
enum error, and the message says so. Read the failures, not just the count: an enum rejection lists
the permitted values, and that list is the field's real contract.

Step 8 prints nine ladders. `GenericWorkload` shows three lines of stage data and no `removed` or
`locked` key. `OpportunisticBatching` shows one rung, beta, `defaultValue: true`, from 1.35, and no
`toVersion` — the only gate of the nine that has not moved. `GangScheduling` and
`WorkloadAwarePreemption` each end with `removed: true`. The removal count is 230 and the surviving
count is 258. The 1.3x filter prints a short list, and only three entries in it are from 1.35 or
later: `AppArmorFields` at 1.30, `GangScheduling` at 1.35 and `WorkloadAwarePreemption` at 1.36. The
last grep finds the merge sentence in exactly the two files, worded the same way in both.

Step 9 is the archaeology. The post's grep finds `Permit` and the five-minute timeout in its own
prose. Under `docs`, `WaitOnPermit` survives in two files and `timeout` appears zero times in any of
the gang, PodGroup or Workload pages, so the post's timeout was never documented outside the post.
`podgroup-scheduling.md:30` prints the sentence that names `WaitOnPermit` as what the new cycle
replaced. The framework page lists sixteen `###` headings, ending at `PostBind`, and the four counts
that follow are all zero on both files — `PlacementFeasible`, `PodGroup`, `Workload` and `gang` are
absent from both the framework page and the scheduler config reference. The final grep finds
`PlacementFeasible` in two files, both of them concept pages.

Step 10 closes the loop. The version census prints `v1alpha2` from the two generated reference pages
and one definitions page, `v1alpha3` from the hierarchical pages, `v1beta1` from the concept YAML
and `job.md`, and `v1` from `PriorityClass` — four strings past `v1`, and the post's `v1alpha1`
appears only in the post, twice. Of the five link targets, `dynamic-resource-allocation` under
`scheduling-eviction` prints `MISSING` and the redirect count for it is zero, so that link is a dead
path rather than a moved one; the other four are present as files, but `GangScheduling.md` carries
`removed: true`, which takes its anchor off the page the post links to. The last grep finds four
in-tree references to the two removed anchors, three of them blog posts and one a live concept page.
The line counts come to 183 for the post against 2,301 concept lines and 2,883 reference lines,
`CompositePodGroup` counts zero in both reference pages, and the five trailing-whitespace tallies
and the unclosed bracket on `workload-aware-preemption.md:30` are what reading all of it costs.

**Read on**

11. [The 2022 scheduling-readiness row](../2022/13-pod-scheduling-readiness-alpha.md), which built
    the extension point this feature occupies and says three times that a later year's row owns gang
    scheduling. Read it first if `PreEnqueue` is new; read its `:508-513` afterwards, because it
    warns that taking the two mechanisms in the wrong order makes gang scheduling look like the
    reason `PreEnqueue` exists, which is backwards by several releases.

12. [The 2022 dynamic resource allocation row](../2022/12-dynamic-resource-allocation.md), for what
    an alpha API group costs to switch on and for the shape of the same story one feature over: an
    alpha API announced in its first release, renamed before it stabilised. Its step 2 and step 3 do
    to that post's YAML what steps 2 and 4 do to this one's.

13. [The Job `managedBy` row from the same
    month](10-kubernetes-v1-35-job-managedby-for-jobs-goes-ga.md), which is the other half of
    v1.35's batch story: this post hands scheduling to the scheduler, that one hands the whole Job
    to something outside the cluster. `concepts/workloads/controllers/job.md` carries both, at
    `:320-350` and `:1303-1330`, and neither section mentions the other.

14. [The 2019 API removals row](../2019/08-api-deprecations-in-1-16.md), for `--runtime-config` as a
    subject rather than a tool, and for the older half of the story this exercise is the newer half
    of: a group-version that stopped being served, written down in a guide that the pages teaching
    the same group-version today do not link.

15. *Unanswerable from the pin.* Which of the two template-reference shapes was the API and which
    was a documentation error, at the moment each page was written. The generated reference is
    regenerated from the types at every release, so it is right about `v1alpha2` today; the concept
    pages are written by hand and may have been right about an earlier or a later version. A
    one-commit sparse checkout carries no history, so the only thing answerable here is which shape
    the running server accepts, which is step 6.

**Teardown**

```sh
ssh zain@10.10.10.180 "sudo cp /tmp/bw-apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml \
  && sudo cp /tmp/bw-scheduler.yaml.bak /etc/kubernetes/manifests/kube-scheduler.yaml \
  && sudo rm -f /tmp/bw-apiserver.yaml.bak /tmp/bw-scheduler.yaml.bak"
until kubectl version >/dev/null 2>&1; do sleep 5; done
kubectl delete namespace bw-workload
rm -rf /tmp/bw-workload
```
