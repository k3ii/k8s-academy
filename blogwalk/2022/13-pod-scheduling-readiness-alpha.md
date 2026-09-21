<a id="pod-scheduling-readiness-alpha"></a>

# The post describes its new extension point twice and the two descriptions disagree, the pin matches neither, the feature reached stable four releases later and was never locked, and the use case the post was written to serve appears in exactly one file in the tree, which is this post

**Post** — [Kubernetes 1.26: Pod Scheduling Readiness](https://kubernetes.io/blog/2022/12/26/pod-scheduling-readiness-alpha/),
2022-12-26.

5,465 bytes over 129 lines, by Wei Huang (Apple) and Abdullah Gharaibeh (Google): the last `walk`
post of the year, and the fourth-shortest of its thirteen. It introduces one Pod field, draws the
same queue twice in mermaid, gives one use case, and points at the concept page and a KEP.

**As written**

Scheduling gates are *keys* that tell the scheduler when a Pod is ready to be considered (`:11-12`).
The problem they solve is stated as cost: the scheduler picks up every Pod the moment it is created,
a scheduling cycle *may take ≅20ms or more* (`:19-20`), and a Pod that cannot possibly run yet burns
one cycle after another being found unschedulable. The first mermaid diagram (`:24-47`) draws those
wasted cycles as a loop.

A Pod with a non-empty `spec.schedulingGates` is declared not ready, and *those Pods will also be
ignored by Cluster Autoscaler* (`:49-52`). Clearing the gates is explicitly *the responsibility of
external controllers* (`:54-55`) — the post proposes the mechanism and hands the policy to somebody
else. The second mermaid diagram (`:57-85`) redraws the queue with the gate in it, and its three
decisive edges are `queue==>|PreEnqueue check|popout`, `popout-->|Yes|sched_cycle` and
`popout==>|No|queue` (`:66-68`): the check happens when a Pod comes *out* of the queue, and failing
it puts the Pod back.

The field behaves *very similar to Finalizers* (`:89`). More than one gate can be added, *but they
all should be added upon Pod creation (e.g., you can add them as part of the spec or via a mutating
webhook)* (`:91-92`). A gated Pod shows `SchedulingGated` in `kubectl get pods` (`:94-97`). Gates
*do not need to be removed all at once, but only when all the gates are removed the scheduler will
start to consider the Pod for scheduling* (`:99-101`). Then the implementation note: *scheduling
gates are implemented as a PreEnqueue scheduler plugin, a new scheduler framework extension point
that is invoked at the beginning of each scheduling cycle* (`:103-104`).

One use case is given, and the post calls it *an important use case this feature enables*: dynamic
quota management (`:106-118`). ResourceQuota is enforced by the API server at Pod creation, so an
over-quota Pod is rejected outright and whoever created it must keep retrying — *a delay between
resources becoming available and the Pod actually running*, or load on the API server from constant
attempts. The proposal is an external quota manager that adds an `example.com/quota-check` gate to
every Pod through a mutating webhook and removes it when quota exists. To try any of it, the
`PodSchedulingReadiness` gate must be enabled *in the API Server and scheduler* (`:120-121`), and
the post closes by pointing at the concept page and KEP-3521 (`:125-129`).

**As it runs now**

There is nothing to enable. `PodSchedulingReadiness` went alpha in v1.26 for exactly one release,
beta and on by default in v1.27, and stable in v1.30; the gate file declares no `locked:` and no
`removed:`, so on the lab's v1.35 cluster the field is simply part of the Pod API. The instruction
at `:120-121` is the one line of the post a reader can no longer carry out, and the reason is that
it succeeded.

The mechanism is unchanged and the post's description of it still reads as current. The status
string is still the literal `SchedulingGated`. Gates can still be removed one at a time with no
effect until the last one goes. The creation-only rule the post states as advice is stated by the
pin as a rule: *SchedulingGates can only be set at pod creation time, and be removed only
afterwards* (`pod-v1.md:193`). The concept page the post points at is still there, still named
`pod-scheduling-readiness.md`, and carries `{{< feature-state for_k8s_version="v1.30" state="stable"
>}}` at `:9`.

The extension point is also unchanged, and this is where the post and the pin part company.
`scheduling-framework.md:58-67` gives `PreEnqueue` a section of its own: *These plugins are called
prior to adding Pods to the internal active queue, where Pods are marked as ready for scheduling*,
and *only when all PreEnqueue plugins return `Success`, the Pod is allowed to enter the active
queue. Otherwise, it's placed in the internal unschedulable Pods list, and doesn't get an
`Unschedulable` condition* (`:60-64`). Before the queue, not at the start of a cycle, and not on the
way out of the queue either — so the post's prose and the post's own diagram are both describing
something other than what the pin describes, and they are not describing the same wrong thing as
each other.

A fourth thing belongs here and is not a behaviour: the pin disagrees with itself about which Pod
fields you may change after creation. `pods/_index.md:247-249` gives a closed list — *Pod updates
may not change fields other than `spec.containers[*].image`, `spec.initContainers[*].image`,
`spec.activeDeadlineSeconds`, `spec.terminationGracePeriodSeconds`, `spec.tolerations` or
`spec.schedulingGates`* — and `.spec.nodeSelector` and `.spec.affinity` are not in it. Elsewhere in
the same tree, `pod-scheduling-readiness.md:94-113` says you may mutate both while a Pod is gated,
under four numbered rules, the first of which is *for `.spec.nodeSelector`, only additions are
allowed. If absent, it will be allowed to be set* (`:99`). A reader who trusts the Pod page will not
attempt the patch the scheduling page documents. One `kubectl patch` settles which page is right,
and it is step 4.

**What this exercise does not cover, and where it lives**

The observable shape of a gated Pod is already a lab. [A pod the scheduler declines to look
at](../../labs/05/24-a-pod-that-is-never-considered.md) owns the `PodScheduled=False` condition with
reason `SchedulingGated`, the `scheduler_pending_pods{queue="gated"}` gauge, the *absence* of any
`FailedScheduling` event, the refusal when a gate is added to a Pod that is already gated, the
sub-second requeue when the last gate goes, the `PreEnqueue` source reading under `pkg/scheduler/`,
and the motivating question in KEP-3521. Nothing below re-derives any of that: *Do* spends its
refusals on two cases the lab does not hold, a Pod that never had a gate and a Pod that has finished
being gated.

What holds Pods at the `PreEnqueue` extension point at the pin is gang scheduling, and that belongs
to a later year's row, which owns it. The absence of Kueue from the documentation tree belongs to
this year's *Introducing Kueue* row, which owns it. Step 9 counts both; it does not explain either.

**The diff, and why**

**Wrong when it was published.** The post describes its own extension point twice and the two
descriptions do not agree. The prose says the `PreEnqueue` plugin *is invoked at the beginning of
each scheduling cycle* (`:103-104`). The diagram says the check happens on the way out of the queue,
and that failing it puts the Pod back: `queue==>|PreEnqueue check|popout`, `popout==>|No|queue`
(`:66-68`). The pin says neither — *prior to adding Pods to the internal active queue*, and a Pod
that fails *is placed in the internal unschedulable Pods list, and doesn't get an `Unschedulable`
condition* (`scheduling-framework.md:60-64`). The difference is the whole argument of the post. A
check at the beginning of a scheduling cycle is a check that has already cost a scheduling cycle,
which is the ≅20ms the post opens by objecting to (`:19-20`); the diagram's placement still pops the
Pod before deciding; only the pin's placement means the Pod is never queued and no cycle is spent.
The prose is not a later drift, because the diagram beside it already disagreed on the day it
published. Step 7 prints all three.

The same section understates one rule into advice. Gates *should be added upon Pod creation*
(`:91-92`), on the model of Finalizers — but Finalizers can be added at any time and gates cannot.
`pod-v1.md:193` states it as a refusal, not a convention, and a reader who took the post's "should"
at face value would build the controller the post itself proposes at `:115-118` and discover the API
will not have it. Step 6 collects the refusal from both sides: a Pod that never had a gate, and a
Pod that has finished being gated.

**Still right.** The mechanism is intact, down to the strings. `SchedulingGated` is still what
`kubectl get pods` prints (step 2). Gates still come off one at a time with no effect until the last
one (`:99-101`, step 3). The field is still list-of-names and still only initialisable at creation.
The Finalizers analogy still holds for the removal half even though it fails for the addition half.
And the one claim here about something outside the tree was not left to rot: *those Pods will also
be ignored by Cluster Autoscaler* (`:49-52`) is repeated and sharpened by the stable announcement
sixteen months later, where gating *doesn't just cut the load on the scheduler, it can also save
money*, because *without scheduling gates, the autoscaler might otherwise launch a node that doesn't
need to be started* (`kubernetes-v1-30-release.md:95-98`). The pin cannot verify a component it does
not contain; what it shows is that the claim was made twice, four releases apart.

**Never absorbed.** The post gives exactly one use case and calls it *an important use case this
feature enables*: dynamic quota management by an external manager that adds
`example.com/quota-check` through a mutating webhook. At the pin the phrase *quota manager* appears
in one file in the whole of `content/en`, and it is this post; under `docs/` it appears zero times,
and the feature's own concept page contains the word *quota* zero times. The field was absorbed
completely and its reason for existing was not absorbed at all. Step 9 counts it. Naming only *still
right* here would record a feature that graduated and miss that the argument for it never reached
the documentation — and what does hold Pods at `PreEnqueue` in the pinned tree arrived from
somewhere else entirely, which is a later year's row and it owns that.

**Retired by being agreed with.** `PodSchedulingReadiness` was alpha for a single release, beta the
next, and stable four releases after this post. It was never locked and never removed; its file
records three stages and nothing else. The stronger evidence is where the field turned up: it is now
one of six names in the general rule for what a Pod update may change, sitting beside
`spec.tolerations` on the Pod concept page (`pods/_index.md:247-249`), which is not where features
live. And the posts stopped. Four posts in the archive have ever named `schedulingGates` — the 1.26
release note, this one, the 1.27 note that took it to beta, and the 1.30 note that took it to stable
— and the last of them is 2024-04-17, two years and four months before the pin. Step 10 lists all
four.

The subject is one gate and it climbed without a detour.

`PodSchedulingReadiness`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.26 – v1.26 |
| beta | `true` | — | v1.27 – v1.29 |
| stable | `true` | — | v1.30 – |

No file-level fact sits under this table: `PodSchedulingReadiness.md` declares no `removed:`, no
`locked:` on any stage, and no `former_titles:`. The one-release alpha is not unusual on its own —
151 of the 487 gate files at the pin have `fromVersion` equal to `toVersion` on some stage — but
taken with the rest of the row it is the shape of a feature nobody argued about.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 vCPU, at `10.10.10.180`,
running Kubernetes v1.35. One node is the right number: a gated Pod is not rejected by a node, it is
never offered to one, so a second node would add nothing to watch. Steps 1 to 6 run against the
cluster in a namespace called `gates`; steps 7 to 10 are offline and read the pinned checkout.

**Do**

1. The field, before the post is opened.

   ```sh
   kubectl explain pod.spec.schedulingGates
   kubectl explain pod.spec.schedulingGates.name
   kubectl create ns gates
   ```

2. The pin's own example, applied without a character changed —
   `examples/pods/pod-with-scheduling-gates.yaml`, which is the post's manifest with a name on it.

   ```sh
   kubectl -n gates apply -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata:
     name: test-pod
   spec:
     schedulingGates:
     - name: example.com/foo
     - name: example.com/bar
     containers:
     - name: pause
       image: registry.k8s.io/pause:3.6
   YAML
   kubectl -n gates get pod test-pod
   ```

3. The post's claim at `:99-101`: gates come off one at a time and nothing happens until the last.

   ```sh
   kubectl -n gates patch pod test-pod --type=json \
     -p '[{"op":"remove","path":"/spec/schedulingGates/1"}]'
   kubectl -n gates get pod test-pod -o jsonpath='{.spec.schedulingGates}'; echo
   kubectl -n gates get pod test-pod
   ```

4. Which of the two pages is right. `pods/_index.md:247-249` says `.spec.nodeSelector` may not be
   changed after creation; `pod-scheduling-readiness.md:99` says it may, on a gated Pod, as long as
   you only add. Ask the cluster.

   ```sh
   kubectl -n gates patch pod test-pod --type=merge \
     -p '{"spec":{"nodeSelector":{"kubernetes.io/os":"linux"}}}'
   echo "add exit $?"
   kubectl -n gates patch pod test-pod --type=merge \
     -p '{"spec":{"nodeSelector":{"kubernetes.io/os":"windows"}}}'
   echo "change exit $?"
   kubectl -n gates get pod test-pod -o jsonpath='{.spec.nodeSelector}'; echo
   ```

5. Remove the last gate.

   ```sh
   kubectl -n gates patch pod test-pod --type=json \
     -p '[{"op":"remove","path":"/spec/schedulingGates"}]'
   kubectl -n gates wait --for=condition=Ready pod/test-pod --timeout=60s
   kubectl -n gates get pod test-pod -o wide
   ```

6. The one-way door, from the two sides the lab does not hold: a Pod that never had a gate, and a
   Pod that has finished being gated.

   ```sh
   kubectl -n gates run ungated --image=registry.k8s.io/pause:3.10 --restart=Never
   kubectl -n gates wait --for=condition=Ready pod/ungated --timeout=60s
   kubectl -n gates patch pod ungated --type=merge \
     -p '{"spec":{"schedulingGates":[{"name":"example.com/late"}]}}'
   echo "never-gated exit $?"
   kubectl -n gates patch pod test-pod --type=merge \
     -p '{"spec":{"schedulingGates":[{"name":"example.com/again"}]}}'
   echo "once-gated exit $?"
   ```

7. Offline from here. The extension point, described three times.

   ```sh
   cd /path/to/kubernetes/website/content/en
   echo "--- the post says ---"
   sed -n '103,104p' blog/_posts/2022/pod-scheduling-readiness.md
   echo "--- the post draws ---"
   sed -n '66,68p' blog/_posts/2022/pod-scheduling-readiness.md
   echo "--- the pin says ---"
   sed -n '58,64p' docs/concepts/scheduling-eviction/scheduling-framework.md
   ```

8. Every page that names the field, and the two rules that disagree.

   ```sh
   cd /path/to/kubernetes/website/content/en
   unwrap() { tr '\n' ' ' | tr -s ' ' | sed 's/^ //' | fold -s -w 92 | sed 's/ *$//'; echo; }
   echo "--- pages naming the field ---"
   grep -rl 'schedulingGates' --include='*.md' . | sed 's|^\./||' | sort
   echo "--- the general Pod-update rule ---"
   sed -n '247,249p' docs/concepts/workloads/pods/_index.md | unwrap
   echo "--- the feature page, on the gates ---"
   sed -n '24,27p' docs/concepts/scheduling-eviction/pod-scheduling-readiness.md | unwrap
   echo "--- the feature page, on everything else ---"
   sed -n '94,99p' docs/concepts/scheduling-eviction/pod-scheduling-readiness.md | unwrap
   echo "--- the API reference ---"
   sed -n '193p' docs/reference/kubernetes-api/core/pod-v1.md | sed 's/<[^>]*>//g' | unwrap
   ```

9. What the extension point holds Pods for now, and what became of the use case.

   ```sh
   cd /path/to/kubernetes/website/content/en
   echo "--- every page that names the extension point ---"
   grep -rlw 'PreEnqueue' --include='*.md' . | sed 's|^\./||' | sort
   echo "--- what it holds Pods for at the pin ---"
   grep -nw 'PreEnqueue' docs/concepts/scheduling-eviction/gang-scheduling.md | cut -c1-92
   echo "--- the use case the post gives, counted ---"
   printf 'quota manager, docs       %s\n' "$(grep -rli 'quota manager' --include='*.md' docs | wc -l | tr -d ' ')"
   printf 'quota manager, content/en %s\n' "$(grep -rli 'quota manager' --include='*.md' . | wc -l | tr -d ' ')"
   printf 'Kueue, docs               %s\n' "$(grep -rl 'Kueue' --include='*.md' docs | wc -l | tr -d ' ')"
   printf 'Kueue, content/en         %s\n' "$(grep -rl 'Kueue' --include='*.md' . | wc -l | tr -d ' ')"
   ```

10. The ladder, the trail of posts, and the drawings.

    ```sh
    cd /path/to/kubernetes/website/content/en
    echo "--- the ladder ---"
    sed -n '/^stages:/,/^---/p' \
      docs/reference/command-line-tools-reference/feature-gates/PodSchedulingReadiness.md | sed 's/ *$//'
    echo "--- every post that names the field, in date order ---"
    for f in $(grep -rl 'schedulingGates' --include='*.md' blog/_posts); do
      printf '%s  %s\n' "$(grep -m1 '^date:' "$f" | sed 's/^date: *//')" "${f#blog/_posts/}"
    done | sort
    echo "--- and the drawings ---"
    printf 'posts in the archive containing "mermaid"  %s\n' \
      "$(grep -rl 'mermaid' --include='*.md' blog/_posts | wc -l | tr -d ' ')"
    printf '{{< mermaid >}} blocks in this post        %s\n' \
      "$(grep -c '{{< mermaid >}}' blog/_posts/2022/pod-scheduling-readiness.md | tr -d ' ')"
    printf '{{< figure >}} blocks on the feature page  %s\n' \
      "$(grep -c '{{< figure' docs/concepts/scheduling-eviction/pod-scheduling-readiness.md | tr -d ' ')"
    ```

**Expect**

Step 1 finds the field already there. `kubectl explain` answers for both paths without a word about
a feature gate, and the description it prints for `schedulingGates` is the sentence step 8 pulls out
of the API reference — the same text, because `explain` reads the OpenAPI schema that page is
generated from. Nothing in the post's closing instruction (`:120-121`) applies to this cluster:
there is no gate to enable, and no flag to pass to the scheduler.

Step 2 reproduces `:94-97` exactly. `test-pod` is `0/1`, `SchedulingGated`, `0` restarts. No node is
assigned, no event is emitted, and the Pod will sit there indefinitely. The manifest is the pin's
example file unchanged, which means it still pins `registry.k8s.io/pause:3.6` while the rest of this
repository has moved to `3.10`; leave it, because the image is not what is being tested and changing
it would make the manifest no longer the pin's.

Step 3 is the post's sentence at `:99-101` made visible. The JSON patch removes index 1, the
jsonpath prints a one-element list holding `example.com/foo`, and `get pod` still says
`SchedulingGated`. One gate removed changed nothing, because the test is emptiness and not count.

Step 4 settles the disagreement, and the scheduling page wins. The first patch succeeds and prints
`pod/test-pod patched`, with `add exit 0`: `.spec.nodeSelector` was absent, so it was allowed to be
set, exactly as `pod-scheduling-readiness.md:99` says. The second patch is rejected by the Pod
update validator and `change exit` is non-zero, because changing `linux` to `windows` is not an
addition. The jsonpath then prints `{"kubernetes.io/os":"linux"}` — the value from the first patch,
untouched. So `pods/_index.md:247-249` is not the closed list it reads as; a gated Pod has a wider
mutable surface than the Pod page describes, and a reader who trusted that page would never have
tried.

Step 5 schedules. Removing the whole field leaves nothing to test for emptiness, the scheduler takes
the Pod, and `wait` returns `pod/test-pod condition met` in about a second. `get pod -o wide` shows
`Running` with the node name filled in; the `kubernetes.io/os=linux` selector added in step 4
matches, so the tightening did not cost anything.

Step 6 collects two refusals that say the same thing. `ungated` reaches `Running` normally, and
patching a gate onto it is rejected — `never-gated exit` is non-zero. Patching a gate back onto
`test-pod`, which had two gates a minute ago and now has none, is rejected the same way, and
`once-gated exit` is non-zero as well. There is no state in which a gate can be added to an existing
Pod. That is the hard version of the post's *they all should be added upon Pod creation* (`:91-92`),
and the reason the Finalizers analogy at `:89` only half works: Finalizers can be added at any time.

Step 7 prints the three placements next to each other.

```
--- the post says ---
Under the hood, scheduling gates are implemented as a PreEnqueue scheduler plugin, a new scheduler
framework extension point that is invoked at the beginning of each scheduling cycle.
--- the post draws ---
    queue==>|PreEnqueue check|popout
    popout-->|Yes|sched_cycle
    popout==>|No|queue
--- the pin says ---
### PreEnqueue {#pre-enqueue}

These plugins are called prior to adding Pods to the internal active queue, where Pods are marked as
ready for scheduling.

Only when all PreEnqueue plugins return `Success`, the Pod is allowed to enter the active queue.
Otherwise, it's placed in the internal unschedulable Pods list, and doesn't get an `Unschedulable` condition.
```

Read the three as a sequence and the post argues against itself. Its prose puts the check at the
*beginning of each scheduling cycle*, which is a check that has already paid for the cycle. Its
diagram puts the check on the edge out of the queue — `queue==>|PreEnqueue check|popout` — which
still pops the Pod first. The pin puts it before the queue, where the Pod is never made a candidate
and the cycle is never started, and adds the detail neither version of the post gives: a Pod that
fails the check *doesn't get an `Unschedulable` condition*, which is why a gated Pod has nothing to
show for itself in its events. Only the third placement saves the ≅20ms the post was written about.

Step 8 shows how small the field's footprint is, and prints the two rules in full.

```
--- pages naming the field ---
blog/_posts/2022/kubernetes-1.26-blog.md
blog/_posts/2022/pod-scheduling-readiness.md
blog/_posts/2023/kubernetes-1.27-release.md
blog/_posts/2024/kubernetes-v1-30-release.md
docs/concepts/scheduling-eviction/pod-scheduling-readiness.md
docs/concepts/workloads/pods/_index.md
docs/reference/command-line-tools-reference/feature-gates/PodSchedulingReadiness.md
docs/reference/kubernetes-api/core/pod-v1.md
--- the general Pod-update rule ---
- Pod updates may not change fields other than `spec.containers[*].image`,
`spec.initContainers[*].image`, `spec.activeDeadlineSeconds`,
`spec.terminationGracePeriodSeconds`, `spec.tolerations` or `spec.schedulingGates`. For
`spec.tolerations`, you can only add new entries.
--- the feature page, on the gates ---
The `schedulingGates` field contains a list of strings, and each string literal is
perceived as a criteria that Pod should be satisfied before considered schedulable. This
field can be initialized only when a Pod is created (either by the client, or mutated
during admission). After creation, each schedulingGate can be removed in arbitrary order,
but addition of a new scheduling gate is disallowed.
--- the feature page, on everything else ---
You can mutate scheduling directives of Pods while they have scheduling gates, with certain
constraints. At a high level, you can only tighten the scheduling directives of a Pod. In
other words, the updated directives would cause the Pods to only be able to be scheduled on
a subset of the nodes that it would previously match. More concretely, the rules for
updating a Pod's scheduling directives are as follows: 1. For `.spec.nodeSelector`, only
additions are allowed. If absent, it will be allowed to be set.
--- the API reference ---
SchedulingGates is an opaque list of values that if specified will block scheduling the
pod. If schedulingGates is not empty, the pod will stay in the SchedulingGated state and
the scheduler will not attempt to schedule the pod. SchedulingGates can only be set at pod
creation time, and be removed only afterwards.
```

Eight files in the whole tree, four of them posts and four of them documentation, and the four posts
are this one plus three release notes. The two rules are worth reading against each other slowly.
The Pod page's list is grammatically closed — *may not change fields other than* — and
`.spec.nodeSelector` is not on it. The feature page opens a second, wider door that exists only
while a Pod is gated. Both can be true at once — gating is itself a Pod state, and the two pages
write their rules at different scopes, one per state and one per field — but neither page says so,
and neither links to the other. Step 4 is the only thing in this file that tells you which page to
believe.

Step 9 is where the post's argument and the post's mechanism separate.

```
--- every page that names the extension point ---
blog/_posts/2022/pod-scheduling-readiness.md
blog/_posts/2024/scheduler-queueinghint/index.md
blog/_posts/2026/workload-aware-scheduling-1-36.md
docs/concepts/scheduling-eviction/gang-scheduling.md
docs/concepts/scheduling-eviction/scheduling-framework.md
docs/reference/config-api/kube-scheduler-config.v1.md
--- what it holds Pods for at the pin ---
35:1. The scheduler holds Pods in the `PreEnqueue` phase until:
80:queue in the `PreEnqueue` phase until it satisfies the **hierarchical quorum**. This quor
--- the use case the post gives, counted ---
quota manager, docs       0
quota manager, content/en 1
Kueue, docs               0
Kueue, content/en         11
```

The extension point this post introduced is in the config API and has its own section in the
framework reference, so it was not a one-feature hook. What holds Pods there in the pinned
documentation is gang scheduling, waiting on a quorum — an in-tree scheduler feature that arrived
years later and belongs to a later year's row, which owns it. The last four lines are the post's use
case, counted. *Quota manager* occurs in exactly one file in all of `content/en`, and that file is
this post, at `:55` and `:115`; under `docs/` it occurs zero times, and the feature's own concept
page does not contain the word *quota* at all. The project that did build queueing on top of the
idea appears in eleven files in `content/en` and none under `docs/`, which this year's *Introducing
Kueue* row already owns. The mechanism graduated; the reason given for it never got written down
anywhere but here.

Step 10 prints the ladder, the trail, and the drawings.

```
--- the ladder ---
stages:
  - stage: alpha
    defaultValue: false
    fromVersion: "1.26"
    toVersion: "1.26"
  - stage: beta
    defaultValue: true
    fromVersion: "1.27"
    toVersion: "1.29"
  - stage: stable
    defaultValue: true
    fromVersion: "1.30"
---
--- every post that names the field, in date order ---
2022-12-09  2022/kubernetes-1.26-blog.md
2022-12-26  2022/pod-scheduling-readiness.md
2023-04-11  2023/kubernetes-1.27-release.md
2024-04-17  2024/kubernetes-v1-30-release.md
--- and the drawings ---
posts in the archive containing "mermaid"  11
{{< mermaid >}} blocks in this post        2
{{< figure >}} blocks on the feature page  1
```

Three stages, no `locked:` on any of them, and the trailing `---` is the gate file's own front
matter ending — there is nothing after the ladder to print. The trail is four posts across sixteen
months and then nothing for the two years and four months to the pin, which for a Pod field that
every cluster now carries is the quiet ending rather than the loud one. The last three lines are a
smaller observation with the same shape: this post drew its queue twice in mermaid, one of eleven
posts in the whole archive to use the shortcode at all, and the concept page that inherited the
feature drew it once as a checked-in SVG. The diagrams did not survive the move either; only the
field did.

**Read on**

1. `docs/concepts/scheduling-eviction/scheduling-framework.md:58-67`, the whole `PreEnqueue`
   section. Ten lines, and they contain the correction to this post's `:103-104` plus one fact the
   post never had a reason to mention: a Pod rejected here is put on an internal unschedulable list
   and given no condition. Read it before reading any of the post's two diagrams again.

2. `docs/concepts/scheduling-eviction/pod-scheduling-readiness.md:92-113`, the four rules for
   mutating a gated Pod's scheduling directives. Rule 3 (`:103-109`) is the one worth the time: it
   allows additions to `matchExpressions` but no changes to existing ones, and then gives the reason
   — the terms in `nodeSelectorTerms` are ORed while the expressions inside a term are ANDed, so
   adding a term widens and adding an expression narrows. Step 4 only tests rule 1.

3. `blog/_posts/2024/kubernetes-v1-30-release.md:93-102`, the stable announcement. It makes the cost
   argument this post only gestures at, and makes it in a currency: not ≅20ms of scheduler time but
   a node the autoscaler starts for a Pod that was never going to run. It is also the last time any
   post in the archive names the field.

4. `docs/concepts/scheduling-eviction/gang-scheduling.md:28-51`, named and not explained here. It is
   what occupies the extension point this post created, and a later year's row owns it. Reading the
   two mechanisms in the wrong order makes gang scheduling look like the reason `PreEnqueue` exists,
   which is backwards by several releases.

5. *Unanswerable from the pin:* whether any external quota manager was ever built on the gate. The
   post proposes one at `:115-118` and calls the use case important; four years later the phrase
   appears nowhere in the tree but in this post. The pin is one revision of a documentation tree, so
   it cannot distinguish between an idea nobody implemented, an idea implemented out of tree by
   people who never wrote it up, and an idea overtaken by Kueue before anyone finished. What it can
   tell you is that the field outlived the argument for it by a wide margin, and that the argument
   was never restated.

**Teardown**

```sh
kubectl delete ns gates
```
