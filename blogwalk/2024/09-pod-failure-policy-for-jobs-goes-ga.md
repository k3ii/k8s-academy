<a id="kubernetes-1-31-pod-failure-policy-for-jobs-goes-ga"></a>

# The reason string this post gives for scheduler preemption is spelled a way nothing else in the pinned tree spells it, the second rule of its worked example matches a condition no Kubernetes component sets, and both gates behind the feature were deleted after it went stable

**Post** — [Kubernetes 1.31: Pod Failure Policy for Jobs Goes GA](https://kubernetes.io/blog/2024/08/19/kubernetes-1-31-pod-failure-policy-for-jobs-goes-ga/),
2024-08-19.

9,951 bytes over 189 lines, thirtieth of the fifty-four 2024 posts by size and third-largest of the
thirteen the year marks `walk`. The byline at `:6-8` names two people, Michał Woźniak and Shannon
Kularathna, both at Google; the acknowledgments that close it at `:162-189` are written in the first
person singular — *I would love to thank everyone who was involved in this project over the years* —
and list twenty-one named contributors, one of whom is the second author, credited for docs reviews.
One fenced block in the whole post, at `:104-117`, thirteen lines of YAML that are not a manifest
but a fragment: a bare `podFailurePolicy` with three rules and no Job around it.

**As written**

The argument opens on cost. `:18-24` sets up `backoffLimit` as the only dial a Job has for
tolerating failure, and then says what is wrong with it: set it large and *you might notice
unnecessary increases in operating costs as Pods restart excessively until the backoffLimit is met*.
`:26-27` scales the problem — *thousands of long-running Pods across thousands of nodes* — and
`:29-33` names the two things a failure policy buys you, failing fast on a failure that will never
succeed, and not counting one that was never the workload's fault. `:35-37` gives the concrete
purchase: run on spot machines and ignore the failures that graceful node shutdown causes.

`:41-50` describes the mechanism. A policy is a list of rules; each rule matches on one of two
properties, `onExitCodes` or `onPodConditions`. `:52-58` lists four actions — `Ignore`, `FailJob`,
`FailIndex`, `Count` — and marks `Count` the default. `:60-63` fixes evaluation order: rules are
matched *in the specified order*, and the first match wins. `:65-67` adds the one constraint the
post states as a constraint, that the Pod template must carry `restartPolicy: Never`, with a reason
attached: *this prevents race conditions between the kubelet and the Job controller when counting
Pod failures*.

`:69-98` is the companion feature, and it is the half of the post this exercise spends most of its
time on. To give `onPodConditions` something to match, the work introduced a `DisruptionTarget`
condition, added to any Pod — *regardless of whether it's managed by a Job controller* — that is
about to be deleted for a reason Kubernetes itself chose. `:81-93` enumerates the five reasons:
`PreemptionByKubeScheduler`, `DeletionByTaintManager`, `EvictionByEvictionAPI`, `DeletionByPodGC`
and `TerminationByKubelet`. `:95-98` draws the line the whole design rests on — every other way a
Pod can die gets no condition, *because the disruptions were likely caused by the Pod and would
reoccur on retry*.

`:100-127` is the worked example. Three rules: `Ignore` on `DisruptionTarget`, `FailJob` on a
condition called `ConfigIssue`, and `FailJob` on exit code 42. The prose that follows describes four
behaviours, the fourth being the default the fragment does not spell. `:123-124` is honest about
where the middle rule's input comes from: the `ConfigIssue` condition is *custom user-supplied*,
*added either by a custom controller or webhook*.

`:129-138` points at four places to read further, including the KEP directory
`keps/sig-apps/3329-retriable-and-non-retriable-failures`. `:140-146` is a `Related work` list of
four things *in progress*, which is the post's own statement that the feature it has just called
stable is a foundation rather than a finished shape. `:148-160` credits the batch working group with
SIG Apps, SIG Node and SIG Scheduling.

**As it runs now**

**Both gates are gone, and they left one release apart.** `JobPodFailurePolicy.md` records alpha at
v1.25, beta from v1.26 to v1.30, stable from v1.31 to v1.32, and then `removed: true`.
`PodDisruptionConditions.md` records the same alpha and the same beta, stable from v1.31 to v1.33,
and `removed: true`. Neither file writes a `locked` key on any stage. That is not unusual: of the
230 gate files at the pin that declare themselves removed, 182 reached stable, and 179 of those 182
never recorded a `locked` stage. Removal after stable, with no locked row in between, is the
ordinary ending. What is worth noticing is the one-release gap — the condition outlived the policy
that consumes it.

**Three pages still render a feature-state banner keyed to one of the two deleted gates.**
`job.md:609` and `tasks/job/pod-failure-policy.md:8` both carry `{{< feature-state
feature_gate_name="JobPodFailurePolicy" >}}`, and `disruptions.md:236` carries the same shortcode
for `PodDisruptionConditions`. Both gate files are built with `list: never` and `render: false`, so
the record they read from is present and unpublished.

**The reason string the post gives for preemption appears nowhere else in the pinned tree.**
`PreemptionByKubeScheduler` occurs exactly once across `content/en`, at this post's `:81`. Three
other files carry the same five-reason list and all three spell it `PreemptionByScheduler`:
`disruptions.md:244`, `pod-condition.md:143`, and `pod-group-v1alpha2.md:114`, which is a `v1alpha2`
PodGroup type that borrowed the condition wholesale. Whether the string was renamed after August
2024 or was never right is not answerable from this checkout — the sparse clone is one commit deep
and carries no history. It is answerable from the cluster, which is step 5.

**The reason list is printed twice, byte for byte.** `disruptions.md:244-264` and
`pod-condition.md:143-163` are twenty-one identical lines: the same five definition-list entries,
the same glossary shortcodes, the same closing paragraph about all other disruption scenarios. The
only difference between the two copies anywhere is the sentence that introduces them. Both copies
link graceful node shutdown at `/docs/concepts/architecture/nodes/#graceful-node-shutdown`, a
fragment that page does not have; the whole of `nodes.md` mentions shutdown once, at `:307`, and
that mention is itself a link pointing away to `cluster-administration/node-shutdown.md`. That dead
fragment is counted and owned elsewhere in the archive, by [the exercise on the taint the
non-graceful shutdown post
introduces](../2022/03-kubernetes-1-24-non-graceful-node-shutdown-alpha.md); what belongs here is
the direction of the drift. On this one link the 2024 blog post is current and the two documentation
pages are stale — `:36` and `:91` both point at
`cluster-administration/node-shutdown/#graceful-node-shutdown`, which is where the section lives.

**Nothing in Kubernetes will ever set `ConfigIssue`.** The middle rule of the post's worked example
is inert on a cluster with no extra software on it. The documentation ships a runnable Job that
matches on it, `examples/controllers/job-pod-failure-policy-config-issue.yaml`, and a procedure for
producing the condition by hand at `tasks/job/pod-failure-policy.md:195-216`: `kubectl patch pod
--subresource=status` with a literal condition block. The task page says plainly at `:241-244` that
in a production environment those steps *should be automated by a user-provided controller*. Two
years after the announcement, the answer to *who writes the condition* is still you.

**The docs' own canonical example is not the post's example.**
`examples/controllers/job-pod-failure-policy-example.yaml` is the file `job.md:632-634` embeds, and
it carries two rules, not three: `FailJob` on exit code 42 first, `Ignore` on `DisruptionTarget`
second. The post's fragment has the same two in the opposite order with `ConfigIssue` between them.
Order is load-bearing under the first-match rule at `:60-63`, and here it does not change the
outcome, because no Pod can satisfy both an exit-code requirement and a condition requirement in a
way that makes the pair race — but the two documents present different orderings of nominally the
same example and neither says why. The shipped file also carries a comment at `:25` reading `# one
of: Ignore, FailJob, Count`, three of the four actions that `job.md:676-682` and the post's own
`:52-58` both list. `FailIndex` is missing from the enum the docs annotate.

**The concept page's list of API requirements omits the one requirement validation enforces.**
`job.md:661-682` is headed *some requirements and semantics of the API* and gives four bullets:
`restartPolicy: Never`, first-match ordering, the optional `containerName`, and the four actions. It
never says that a rule may carry `onExitCodes` or `onPodConditions` but not both. That sentence
exists only in the generated reference, at `job-v1.md:327`. Step 7 submits the rule the concept page
does not forbid.

**A field the post never mentions constrains the field it announces.** `job.md:1269-1276` says that
for Jobs with a Pod failure policy set the default `podReplacementPolicy` is `Failed` *and no other
value is permitted*; `job-v1.md:113` says the same thing and contains a typo while saying it,
*Failed is the the only allowed value*. The gate behind that field, `JobPodReplacementPolicy`, was
beta at v1.29 when this post shipped and reached stable and locked at v1.34. So a Job written from
this post acquires a replacement policy it never asked for, and cannot be given a different one.
That is the third submission step 7 makes.

**The fourth action still depends on a feature that was not stable when the post called the policy
stable.** `:53-54` names `FailIndex` and links backoff limit per index, which is the honest thing to
do. `JobBackoffLimitPerIndex.md` records beta from v1.29 to v1.32 and stable with `locked: true`
from v1.33. The post's own GA announcement therefore lists four actions of which one worked only
against a beta feature, and that feature got its own GA post in the archive two years later, in
2025.

**The extension the post files under `Related work` has added nothing to the API.** `:143` links
enhancement 4443, *Pod failure policy extension to add more granular failure reasons*. At the pin
`job-v1.md:325-348` still describes a `PodFailurePolicyRule` with the same three fields — `action`,
`onExitCodes`, `onPodConditions` — and `job-v1.md:336` still closes the action enum with *Additional
values are considered to be added in the future. Clients should react to an unknown action by
skipping the rule.* The extension point is still a sentence.

**The task page declares three different floors on one page.** `tasks/job/pod-failure-policy.md:4`
sets `min-kubernetes-server-version: v1.25` in front matter, `:8` renders a feature-state banner
reading off a record whose stable range starts at v1.31, and `:154` notes that one of the page's
four scenarios *works since version 1.27*. A v1.35 cluster satisfies all three, so nothing you can
run on this lab decides which one the page means. Cite all three and leave them standing.

**The mechanism itself is intact.** Four of the five Jobs the documentation ships for this feature
run unchanged at v1.35 and do what their pages say. That is the finding the other ten are measured
against: the drift here is all in the naming, the gate records and the prose, and none of it in the
controller.

**And the thing the documentation cannot settle with itself.** The note at `disruptions.md:266-272`,
repeated verbatim at `pod-condition.md:165-171`, says that a disruption may be interrupted, that the
`DisruptionTarget` condition *might be added to a Pod, but that Pod might then not actually be
deleted*, and that *after some time, the Pod disruption condition will be cleared*. Set that beside
`job.md:684-689`, which says the Job controller matches only Pods in the `Failed` phase, and beside
this post's `:95-98`, which reads the presence of the condition as a statement about blame. If a Pod
can wear the condition without being disrupted, then a Pod that acquires it, keeps it for the length
of *some time*, and fails inside that window for its own reasons matches an `Ignore` rule written to
excuse a disruption that did not happen. Neither page gives a duration for *some time*, and neither
says whether the Job controller re-reads the condition at the moment of failure or trusts what the
Pod status carries. You cannot interrupt a disruption on demand, so one node cannot decide it. Both
halves are quoted here and neither is picked.

**What this exercise does not cover, and where it lives**

The dead documentation fragment that both copies of the reason list point at is counted and
explained by [the exercise on the taint the non-graceful shutdown post
introduces](../2022/03-kubernetes-1-24-non-graceful-node-shutdown-alpha.md), which also holds the
census of the other files following it; this exercise only notes which way the drift runs.
Preemption mechanics — how a victim is chosen, what the nominated node is, what happens when a
budget forbids the eviction — belong to [the lab on the claim the preemptor gets instead of the
node](../../labs/05/25-priority-and-the-nominated-node.md), [the one that names the pod that
died](../../labs/05/35-5c2-preemption-with-real-victims.md) and [the one where a budget makes
preemption fail out loud](../../labs/05/26-selectvictimsonnode-and-a-pdb-that-forbids.md). Step 5
here uses preemption only as an instrument for producing one condition and reading one string off
it. How a gate file's ladder is read, and what the removed-gate population looks like, is set out in
[the exercise on the gate that went alpha to deleted in four
releases](../2022/04-service-ip-dynamic-and-static-allocation.md). Job tracking with finalizers,
`successPolicy` and `managedBy` are named nowhere below; they are separate features that happen to
live on the same page.

**The diff, and why**

**Still right.** The mechanism the post describes is the mechanism the cluster runs. Two matchers,
four actions, first match wins, `restartPolicy: Never` required. Steps 3, 4, 7 and 8 exercise all of
it and none of it has moved. This is the ordinary outcome for a GA post and it is worth saying out
loud before the rest.

**Retired by being agreed with.** Both gates were deleted, and deleted for the reason gates are
usually deleted: nobody was turning them off. The post is the announcement that the switch had
stopped mattering, and the gate files are the record of the switch being taken away one and two
releases later. Step 1 asks the API server whether either name is still reported and expects
silence.

**Broke, or was wrong on the day — and the archive cannot tell you which.** The reason string at
`:81` is not the reason string the cluster writes. That much step 5 settles in one command. What the
checkout cannot settle is whether `PreemptionByKubeScheduler` was correct in August 2024 and was
renamed afterwards, or was never correct. The pin is one commit deep. The honest form of this
finding is the pair: the post says one thing, the cluster says another, and the direction of the
error is outside what a frozen tree can answer. Write down both and move on.

**Never absorbed.** `ConfigIssue` was a custom condition in the post and is a custom condition now.
The documentation still ships a Job that waits for it, still walks you through patching it in by
hand, and still tells you at `tasks/job/pod-failure-policy.md:241-244` to go and write the
controller. The `Related work` list at `:140-146` is the same shape: four items *in progress* in
2024, and at the pin the API they would extend is unchanged. Nothing here was rejected; it was
simply never picked up. Step 6 runs the hand-patched version so you can see exactly how much
software the second rule of the post's example is waiting on.

**Overtaken by stasis.** The reason list is now duplicated across two documentation pages,
twenty-one lines each, and the copies agree with each other and disagree with the post. A fact
stored twice is a fact that will eventually be updated once — here it has been updated in both
copies and in neither the blog post nor, on the shutdown link, correctly. The post is the only file
in the archive still carrying the old string, and it is also one of the few carrying the current
link.

**The ladder**

Two gates, one feature, and they left the tree one release apart. Neither is settable at the pin;
both are transcribed here because the exercise owns them and nothing else in the archive does.

`JobPodFailurePolicy` — the policy itself:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.25 |
| beta | `true` | — | v1.26 – v1.30 |
| stable | `true` | — | v1.31 – v1.32 |

`PodDisruptionConditions` — the condition the policy matches on:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.25 |
| beta | `true` | — | v1.26 – v1.30 |
| stable | `true` | — | v1.31 – v1.33 |

Both files carry `removed: true` and no `locked` key on any stage. Read the beta rows together: they
are identical, which is the record of two gates moved as one unit by one KEP. Read the stable rows
apart: the policy's record stops at v1.32 and the condition's at v1.33. The consumer was removed
before the thing it consumes, which is the opposite of the order you would guess, and the reason is
visible in the post — `:75-77` says the condition is added to *any Pod, regardless of whether it's
managed by a Job controller*. It was never only a Job feature, so it was never only this post's to
lose.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 cores, at `10.10.10.180`,
running Kubernetes v1.35. Bring it up with [the provision
steps](../../strands/lab-topologies.md#provision) and install Kubernetes with [the node baseline
procedure](../../strands/lab-topologies.md#node-baseline-steps). One node is the right shape here:
step 4 drains the only node in the cluster and uncordons it again, which is exactly the disruption
the post's spot-machine argument is about, and step 5 needs a node small enough that two 2Gi
requests cannot both fit. Everything lands in a namespace called `bw-pfp`. The offline reads are
against the pinned checkout at `/path/to/kubernetes/website/content/en`; `W` below is that path and
`C` is `$W/examples/controllers`.

**Do**

1. Ground the cluster and ask it about the two gates. `kubectl explain` is the question *does the
   field exist without being switched on*, and the metrics endpoint is the question *does the server
   still know either name*.

   ```sh
   kubectl version -o json | grep -E '"gitVersion"'
   kubectl create namespace bw-pfp
   kubectl explain job.spec.podFailurePolicy.rules.onPodConditions
   kubectl explain job.spec.podFailurePolicy.rules.action | head -20
   kubectl get --raw /metrics | grep -c '^kubernetes_feature_enabled' || true
   kubectl get --raw /metrics | grep -iE 'jobpodfailurepolicy|poddisruptionconditions' \
     || echo 'neither gate name is reported by the API server'
   ```

2. Start the counterfactual before anything else, because it is the slowest thing here and it runs
   unattended. This is the docs' `failjob` Job with the policy cut off — `podFailurePolicy` is the
   last block in the file, so deleting from that line to the end leaves a valid Job — under a
   different name, so it can sit in the same namespace as the real one.
   `tasks/job/pod-failure-policy.md:71-75` claims that without the policy this shape takes *at least
   9 minutes* to fail. Step 9 reads the answer.

   ```sh
   W=/path/to/kubernetes/website/content/en
   C=$W/examples/controllers
   sed -e 's/job-pod-failure-policy-failjob/bw-nopolicy/' \
       -e '/^  podFailurePolicy:/,$d' \
       $C/job-pod-failure-policy-failjob.yaml | tee /tmp/bw-nopolicy.yaml | tail -8
   kubectl -n bw-pfp apply -f /tmp/bw-nopolicy.yaml
   date -u +%FT%TZ | tee /tmp/bw-nopolicy-start
   ```

3. Now the same Job with the policy, verbatim from the checkout. Read the condition the Job
   controller writes, and read its message: `tasks/job/pod-failure-policy.md:66-69` says it names
   the container, the exit code and the index of the rule that matched.

   ```sh
   W=/path/to/kubernetes/website/content/en
   C=$W/examples/controllers
   kubectl -n bw-pfp apply -f $C/job-pod-failure-policy-failjob.yaml
   kubectl -n bw-pfp wait --for=condition=Failed job/job-pod-failure-policy-failjob --timeout=300s
   kubectl -n bw-pfp get job job-pod-failure-policy-failjob \
     -o jsonpath='{range .status.conditions[*]}{.type}{"\t"}{.reason}{"\t"}{.message}{"\n"}{end}'
   kubectl -n bw-pfp get job job-pod-failure-policy-failjob \
     -o jsonpath='failed={.status.failed} succeeded={.status.succeeded}{"\n"}'
   ```

4. The `Ignore` rule, against a real disruption. The docs' Job sleeps 90 seconds and exits 0, with
   `backoffLimit: 0`, so a single counted failure would end it. Drain runs in the background because
   the condition it writes lives only as long as the Pod's grace period, and the foreground loop is
   what reads it. Uncordon afterwards or nothing else in this exercise will schedule.

   ```sh
   W=/path/to/kubernetes/website/content/en
   C=$W/examples/controllers
   kubectl -n bw-pfp apply -f $C/job-pod-failure-policy-ignore.yaml
   kubectl -n bw-pfp wait --for=condition=Ready \
     pod -l batch.kubernetes.io/job-name=job-pod-failure-policy-ignore --timeout=180s
   NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl drain "$NODE" --ignore-daemonsets --delete-emptydir-data --force --timeout=180s &
   for i in $(seq 1 20); do
     kubectl -n bw-pfp get pod -l batch.kubernetes.io/job-name=job-pod-failure-policy-ignore \
       -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.status.phase}{" "}{range .status.conditions[?(@.type=="DisruptionTarget")]}{.reason}{end}{"\n"}{end}'
     sleep 2
   done
   wait
   kubectl uncordon "$NODE"
   kubectl -n bw-pfp get job job-pod-failure-policy-ignore \
     -o jsonpath='failed={.status.failed} active={.status.active}{"\n"}'
   ```

5. The one command that settles the string. A low-priority Job Pod asks for 2Gi and gets it; a
   high-priority Pod asks for 2Gi on a 4096MB node and cannot have it until the scheduler takes the
   first one. The victim carries a two-minute grace period so the condition is readable at leisure
   rather than in a two-second window. Compare what you read against `:81` of the post and against
   `disruptions.md:244`.

   ```sh
   kubectl create priorityclass bw-low --value=1000
   kubectl create priorityclass bw-high --value=100000
   kubectl apply -f - <<'YAML'
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: bw-victim
     namespace: bw-pfp
   spec:
     backoffLimit: 0
     template:
       spec:
         restartPolicy: Never
         priorityClassName: bw-low
         terminationGracePeriodSeconds: 120
         containers:
         - name: main
           image: registry.k8s.io/pause:3.10
           resources:
             requests:
               memory: 2Gi
     podFailurePolicy:
       rules:
       - action: Ignore
         onPodConditions:
         - type: DisruptionTarget
   YAML
   kubectl -n bw-pfp wait --for=condition=Ready pod -l batch.kubernetes.io/job-name=bw-victim --timeout=180s
   kubectl -n bw-pfp apply -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata:
     name: bw-preemptor
   spec:
     priorityClassName: bw-high
     containers:
     - name: main
       image: registry.k8s.io/pause:3.10
       resources:
         requests:
           memory: 2Gi
   YAML
   sleep 20
   kubectl -n bw-pfp get pod -l batch.kubernetes.io/job-name=bw-victim \
     -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .status.conditions[?(@.type=="DisruptionTarget")]}reason={.reason} message={.message}{end}{"\n"}{end}'
   kubectl -n bw-pfp get events --field-selector reason=Preempted -o wide
   ```

6. The rule nothing will fire for you. Apply the Job whose image does not exist, wait for a Pod to
   sit in `ImagePullBackOff`, then be the controller the post says you need: write the condition
   onto the Pod's status subresource, and delete the Pod so the kubelet moves it to a terminal phase
   where the Job controller will look at it. This is `tasks/job/pod-failure-policy.md:148-254`
   compressed; the note at `:153-157` says the scenario needs v1.27 or newer.

   ```sh
   W=/path/to/kubernetes/website/content/en
   C=$W/examples/controllers
   kubectl -n bw-pfp apply -f $C/job-pod-failure-policy-config-issue.yaml
   sleep 40
   POD=$(kubectl -n bw-pfp get pod -l batch.kubernetes.io/job-name=job-pod-failure-policy-config-issue \
           -o jsonpath='{.items[0].metadata.name}')
   kubectl -n bw-pfp get pod "$POD" \
     -o jsonpath='{.status.phase}{"\t"}{.status.containerStatuses[0].state.waiting.reason}{"\n"}'
   cat > /tmp/bw-config-issue.yaml <<'YAML'
   status:
     conditions:
     - type: ConfigIssue
       status: "True"
       lastTransitionTime: "2024-08-19T00:00:00Z"
       reason: NonExistingImage
       message: the image referenced by the Pod template does not exist
   YAML
   kubectl -n bw-pfp patch pod "$POD" --subresource=status --patch-file=/tmp/bw-config-issue.yaml
   kubectl -n bw-pfp get pod "$POD" -o jsonpath='{range .status.conditions[*]}{.type}={.status} {end}{"\n"}'
   kubectl -n bw-pfp delete pod "$POD" --grace-period=0 --force
   kubectl -n bw-pfp wait --for=condition=Failed job/job-pod-failure-policy-config-issue --timeout=180s
   kubectl -n bw-pfp get job job-pod-failure-policy-config-issue \
     -o jsonpath='{range .status.conditions[*]}{.type}{"\t"}{.reason}{"\t"}{.message}{"\n"}{end}'
   ```

7. Three submissions that should not be accepted. The first is the constraint the post states at
   `:65-67`. The second is the constraint only `job-v1.md:327` states, and which `job.md:661-682`
   leaves out of its own list of requirements. The third is the field the post never mentions,
   constrained at `job.md:1269-1276` and at `job-v1.md:113`. Read all three errors; they are the
   answer.

   ```sh
   kubectl -n bw-pfp apply --dry-run=server -f - <<'YAML'
   apiVersion: batch/v1
   kind: Job
   metadata: {name: bw-reject-restartpolicy}
   spec:
     template:
       spec:
         restartPolicy: OnFailure
         containers: [{name: main, image: registry.k8s.io/pause:3.10}]
     podFailurePolicy:
       rules:
       - action: FailJob
         onExitCodes: {operator: In, values: [42]}
   YAML
   kubectl -n bw-pfp apply --dry-run=server -f - <<'YAML'
   apiVersion: batch/v1
   kind: Job
   metadata: {name: bw-reject-bothmatchers}
   spec:
     template:
       spec:
         restartPolicy: Never
         containers: [{name: main, image: registry.k8s.io/pause:3.10}]
     podFailurePolicy:
       rules:
       - action: FailJob
         onExitCodes: {operator: In, values: [42]}
         onPodConditions: [{type: DisruptionTarget}]
   YAML
   kubectl -n bw-pfp apply --dry-run=server -f - <<'YAML'
   apiVersion: batch/v1
   kind: Job
   metadata: {name: bw-reject-replacement}
   spec:
     podReplacementPolicy: TerminatingOrFailed
     template:
       spec:
         restartPolicy: Never
         containers: [{name: main, image: registry.k8s.io/pause:3.10}]
     podFailurePolicy:
       rules:
       - action: FailJob
         onExitCodes: {operator: In, values: [42]}
   YAML
   ```

8. The fourth action, which needs a second feature to mean anything. The docs' indexed Job fails
   index 0 with exit 1 — a counted failure, retried once under `backoffLimitPerIndex` — and index 1
   with exit 42, which the `FailIndex` rule turns into a dead index with no retry. The image is
   `docker.io/library/python:3` and it is large; pull it before timing anything.

   ```sh
   W=/path/to/kubernetes/website/content/en
   C=$W/examples/controllers
   kubectl -n bw-pfp apply -f $C/job-backoff-limit-per-index-failindex.yaml
   kubectl -n bw-pfp wait --for=condition=Failed \
     job/job-backoff-limit-per-index-failindex --timeout=600s
   kubectl -n bw-pfp get job job-backoff-limit-per-index-failindex \
     -o jsonpath='failedIndexes={.status.failedIndexes} failed={.status.failed} succeeded={.status.succeeded}{"\n"}'
   kubectl -n bw-pfp get pods -l batch.kubernetes.io/job-name=job-backoff-limit-per-index-failindex \
     -o custom-columns='NAME:.metadata.name,INDEX:.metadata.annotations.batch\.kubernetes\.io/job-completion-index,PHASE:.status.phase,EXIT:.status.containerStatuses[0].state.terminated.exitCode'
   ```

9. Read the counterfactual started in step 2 and price it. The task page says at least nine minutes;
   the Job in step 3 failed in well under one. The difference between those two numbers is the whole
   argument of `:18-33`, measured once on one node.

   ```sh
   kubectl -n bw-pfp wait --for=condition=Failed job/bw-nopolicy --timeout=900s
   cat /tmp/bw-nopolicy-start
   date -u +%FT%TZ
   kubectl -n bw-pfp get job bw-nopolicy \
     -o jsonpath='start={.status.startTime} failed={.status.failed}{"\n"}'
   kubectl -n bw-pfp get job bw-nopolicy \
     -o jsonpath='{range .status.conditions[*]}{.type}{"\t"}{.reason}{"\t"}{.lastTransitionTime}{"\n"}{end}'
   ```

10. Offline, against the pinned checkout. Six reads: the two gate records whole, the census of the
    reason string in both spellings, the diff that shows the reason list is duplicated byte for
    byte, the three feature-state banners keyed to deleted gates, the comment in the shipped example
    that enumerates three of four actions, and the three version floors on the task page.

    ```sh
    cd /path/to/kubernetes/website/content/en
    sed -n '/^stages:/,$p' docs/reference/command-line-tools-reference/feature-gates/JobPodFailurePolicy.md
    sed -n '/^stages:/,$p' docs/reference/command-line-tools-reference/feature-gates/PodDisruptionConditions.md
    grep -rn 'PreemptionByKubeScheduler' . --include='*.md'
    grep -rn 'PreemptionByScheduler' . --include='*.md' | grep -v KubeScheduler
    diff <(sed -n '244,264p' docs/concepts/workloads/pods/disruptions.md) \
         <(sed -n '143,163p' docs/concepts/workloads/pods/pod-condition.md) \
      && echo 'the two copies are identical'
    grep -rn 'feature_gate_name="JobPodFailurePolicy"\|feature_gate_name="PodDisruptionConditions"' docs
    sed -n '24,28p' examples/controllers/job-pod-failure-policy-example.yaml
    sed -n '4p;8p;154p' docs/tasks/job/pod-failure-policy.md
    sed -n '325,348p' docs/reference/kubernetes-api/batch/job-v1.md
    ```

**Expect**

Step 1 prints `v1.35` and creates the namespace. `kubectl explain` describes `onPodConditions` and
`action` with no mention of a feature gate, because there is none left to mention: the field is part
of `batch/v1` unconditionally. The count of `kubernetes_feature_enabled` series is a few hundred,
and the filtered grep prints nothing, so the fallback message fires. That silence is the first
finding — a GA post whose subject is now invisible to the switch that once guarded it. If either
name does appear, stop and read the cluster's version, because something older than the pin is
running.

Step 2 writes `/tmp/bw-nopolicy.yaml` and the `tail -8` shows the file ending on the container's
`args` line with `backoffLimit: 6` beneath it and no `podFailurePolicy` block. The Job is accepted.
Nothing else happens for several minutes; that is the point. The timestamp written to
`/tmp/bw-nopolicy-start` is what step 9 subtracts against.

Step 3 finishes fast. The Job's first Pod sleeps thirty seconds and exits 42, the rule matches, and
the controller writes two conditions: `FailureTarget` first, then `Failed`, both with reason
`PodFailurePolicy`. The message names the container, the namespace, the Pod, the exit code and the
rule index — the shape at `tasks/job/pod-failure-policy.md:66-69`, something close to *Container
main for pod bw-pfp/job-pod-failure-policy-failjob-xxxxx failed with exit code 42 matching FailJob
rule at index 0*. `failed=1`, and `succeeded` is empty. One failure ended an eight-completion Job
with a `backoffLimit` of 6.

Step 4 is the one with moving parts. The first Pod goes `Ready`, drain starts evicting, and the
foreground loop catches the Pod carrying a `DisruptionTarget` condition with reason
`EvictionByEvictionAPI` — drain is an API-initiated eviction, which is the third entry in the post's
list at `:87-88`. Then the Pod is gone and the loop prints nothing, because the node is cordoned and
the replacement cannot be placed. After `uncordon` the Job's `failed` count is `0` and `active`
climbs back. That zero is the whole `Ignore` rule: a Job with `backoffLimit: 0` survived a failure
because the failure was not charged to it. If `failed` reads `1`, the eviction landed outside the
loop's window and the condition was never observed — re-run the step rather than reasoning about it.

Step 5 is the settlement. The victim schedules, the preemptor cannot, the scheduler picks the
victim, and the victim carries `DisruptionTarget` for two minutes. The reason printed is
`PreemptionByScheduler`, not the `PreemptionByKubeScheduler` the post gives at `:81`. The
`Preempted` event says the same thing from the scheduler's side. That is the finding stated three
ways — post, documentation, cluster — with the cluster agreeing with the documentation and both
disagreeing with the post. Note what the exercise still cannot say: whether the post was wrong in
August 2024 or was overtaken. Write down the string and leave the history alone.

Step 6 needs your hands. The Pod sits `Pending` with a waiting reason of `ErrImagePull` or
`ImagePullBackOff`; the image genuinely does not exist. The status patch is accepted — the API
server puts no vocabulary on condition types, which is exactly why the post could invent one — and
the condition list afterwards shows `ConfigIssue=True` beside the built-in ones. Force-deleting the
Pod moves it to `Failed`, the Job controller finally sees a Pod in the phase `job.md:684-689` says
it looks at, the second rule matches, and the Job fails with reason `PodFailurePolicy` and a message
naming the condition. Count the commands that were needed to make a rule fire that a cluster will
never fire by itself.

Step 7 prints three errors and creates nothing. The first names `spec.template.spec.restartPolicy`
and says the policy requires `Never`. The second names `spec.podFailurePolicy.rules[0]` and says
specifying both `onExitCodes` and `onPodConditions` is not supported — the sentence from
`job-v1.md:327`, enforced, that `job.md:661-682` never wrote down. The third names
`spec.podReplacementPolicy` and says `Failed` is the only value allowed when a Pod failure policy is
set. Three rejections, of which the post prepared you for one.

Step 8 takes the longest, mostly pulling `python:3`. When it ends, `failedIndexes` is `0,1` and
`failed` is `3`: index 0 ran twice, because exit 1 matches no rule and `backoffLimitPerIndex: 1`
allows one retry, and index 1 ran once, because exit 42 matched `FailIndex` and the index died with
no retry. `succeeded` is `2`, for indexes 2 and 3. The per-Pod table shows the exit codes that
produced those numbers. The Job-level `backoffLimit: 6` was never reached; per-index accounting
ended it.

Step 9 is the price. The no-policy Job fails after somewhere around nine to eleven minutes — seven
Pods, thirty seconds of sleep each plus the controller's backoff between them, against a
`backoffLimit` of 6 — where step 3 failed in under a minute on the same shape. Compare the two
`lastTransitionTime` values against the two start times. The task page's *at least 9 minutes* at
`:71-75` was written about a gate you can no longer disable, but the number survives the gate,
because the arithmetic was never about the gate.

Step 10 is all reading. The two gate blocks print their stages and `removed: true`, with no `locked`
key on either, and `PodDisruptionConditions` shows a trailing space after `alpha` on its first stage
line that is visible only if you look for it. The census of the reason string returns exactly one
hit for `PreemptionByKubeScheduler` — this post — and three for `PreemptionByScheduler` in
`disruptions.md`, `pod-condition.md` and `pod-group-v1alpha2.md`. The `diff` is empty and prints its
message: twenty-one lines held twice. Three feature-state shortcodes name deleted gates. The shipped
example's comment lists `Ignore, FailJob, Count` and stops. And the task page's line 4, line 8 and
line 154 give v1.25, a banner reading v1.31, and v1.27. Nothing on this lab decides which of the
three the page means, and this exercise does not pick one.

**Read on**

11. [The exercise on the taint the non-graceful shutdown post
    introduces](../2022/03-kubernetes-1-24-non-graceful-node-shutdown-alpha.md) — it owns the dead
    documentation fragment that both copies of the reason list still point at, and counts the other
    files following it.

12. [The exercise on the gate that went alpha to deleted in four
    releases](../2022/04-service-ip-dynamic-and-static-allocation.md) — for how a removed gate's
    ladder is read, and what the removed-gate population at the pin looks like as a population.

13. [The exercise on the CronJob GA post whose census row promises a manifest it does not
    contain](../2021/01-kubernetes-release-1-21-cronjob-ga.md) — the archive's other batch-API GA
    announcement, and a second worked example of a post outliving the gate it announced.

14. [The lab that names the pod that died, on which node, and
    why](../../labs/05/35-5c2-preemption-with-real-victims.md) — step 5 above uses preemption as an
    instrument and reads one field off it; that lab is the mechanism.

15. [The lab where a PodDisruptionBudget makes preemption fail and says
    so](../../labs/05/26-selectvictimsonnode-and-a-pdb-that-forbids.md) — the case where the
    disruption Kubernetes wanted to cause does not happen, which is the live end of the note at
    `disruptions.md:266-272` that this exercise leaves unsettled.

**Teardown**

```sh
kubectl delete namespace bw-pfp --wait=true
kubectl delete priorityclass bw-low bw-high --ignore-not-found
kubectl uncordon "$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')" 2>/dev/null || true
rm -f /tmp/bw-nopolicy.yaml /tmp/bw-nopolicy-start /tmp/bw-config-issue.yaml
kubectl get nodes -o wide
```
