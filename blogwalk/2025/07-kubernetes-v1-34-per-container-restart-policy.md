<a id="kubernetes-v1-34-per-container-restart-policy"></a>

# The API reference calls `Restart` the only possible action while four pinned files use a second one that is on by default, the concept page says it too and then contradicts itself twice on one page, and the post's opening premise was already false two releases before it was published

**Post** — [Kubernetes v1.34: Finer-Grained Control Over Container Restarts](https://kubernetes.io/blog/2025/08/29/kubernetes-v1-34-per-container-restart-policy/),
2025-08-29.

8,374 bytes, 203 lines, 1,125 words of body; one author, Yuan Wang, given as a GitHub handle with no
employer beside it. Three of 2025's twelve `walk` posts omit the affiliation and this is the only
one of the three whose byline is a single named person. Seven `##` headings and six `###`, three
fenced YAML blocks, no Hugo shortcodes, no trailing whitespace on any line, and seven markdown links
across seven distinct targets, one of which spells the GitHub organisation `Kubernetes` with a
capital letter. Seventh of the twelve by publication date and sixth by size, seventeen bytes below
the post above it in a range that runs from 5,408 to 13,166.

**As written**

The post announces one alpha feature gate, `ContainerRestartRules`, and two fields behind it: a
`restartPolicy` on each container that overrides the Pod's, and a `restartPolicyRules` list that
decides on the exit code (`:10-16`). Its framing is a single sentence at `:23-24` — "Before this
feature, the `restartPolicy` was set at the Pod level. This meant that all containers in a Pod
shared the same restart policy (`Always`, `OnFailure`, or `Never`)" — followed at `:28-31` by the
case it says was impossible: a Pod whose main container always restarts and whose init container
runs once and never does.

Three use cases carry the argument. In-place restarts for training jobs (`:45-59`): ML workloads
fail, rescheduling a Pod "consumes a significant amount of time and resources", and a container that
exits with a retriable code should come back "quickly" without the Pod moving. Try-once init
containers (`:61-70`): initialisation that fails should fail the Pod rather than be retried. Pods
with multiple containers (`:72-80`): different containers, different requirements. The mechanism
section at `:82-87` gives the one operational instruction — enable the gate "on your Kubernetes
cluster control-plane and worker nodes running Kubernetes 1.34+".

Then three manifests, each a complete Pod. Example 1 at `:100-119` is `restart-on-exit-codes`:
Pod-level `Never`, container-level `Never`, one rule with `action: Restart` and `exitCodes` `In
[42]`, and a `kubernetes.io/description` annotation reading "This Pod only restart the container
only when it exits with code 42." Example 2 at `:131-149` is `fail-pod-if-init-fails`: Pod-level
`Always`, an init container with `restartPolicy: Never` whose command exits 1, a main container that
sleeps. Example 3 at `:158-175` is `on-failure-pod`: two containers, one `OnFailure` and one
`Always`, and no Pod-level `restartPolicy` at all. The post closes with two links, a Roadmap
paragraph at `:186-189` promising that support for restarting the entire Pod is being planned and
discussed, and a request for feedback on an alpha feature.

**As it runs now**

**The sentence the whole post is built on was already false when it was published, and the page the
post links to says so.** `:23-24` dates the one-policy-per-Pod world to "before this feature".
`pod-lifecycle.md:275-277`, which is the target of the post's own documentation link, states the
opposite as a definition: sidecar containers "ignore the Pod-level `restartPolicy` field: in
Kubernetes, a sidecar is defined as an entry inside `initContainers` that has its container-level
`restartPolicy` set to `Always`." The gate that made that legal, `SidecarContainers`, was alpha at
1.28, beta and on by default from 1.29 through 1.32, and stable and locked from 1.33 — one release
before the release this post announces. A container-level `restartPolicy` had been GA for a release
and on by default for five when the post said it did not exist.

**Both release announcements carrying the feature repeat the same claim, in stronger words each
time.** The v1.34 announcement at `kubernetes-v1-34-release/index.md:414`: "Currently, all
containers within a Pod will follow the same `.spec.restartPolicy` when exited or crashed." The
v1.35 announcement at `kubernetes-v1-35-release/index.md:203`: "Historically, the `restartPolicy`
field was defined strictly at the Pod level, forcing the same behavior on all containers within a
Pod." Three pinned blog posts assert it and one pinned concept page denies it, and the denial is the
one the three posts send readers to.

**The generated API reference says there is one action; four other pinned files use a second one.**
`pod-v1.md:902` describes `ContainerRestartRule.action` as: "Specifies the action taken on a
container exit if the requirements are satisfied. The only possible value is \"Restart\" to restart
the container." The string `RestartAllContainers` does not occur anywhere in `pod-v1.md`. It occurs
in `pod-lifecycle.md:490-546`, in `node-declared-features.md:88-104`, in
`examples/pods/restart-policy/restart-all-containers.yaml:20`, and in a 2026 blog post with its own
census row. The gate behind it, `RestartAllContainersOnContainerExits`, is alpha at 1.35 and beta
and on by default from 1.36, so at the pin's v1.37 the reference's "only possible value" is wrong on
every cluster that has not gone out of its way to turn the second action off.

**The concept page states the same thing, then contradicts itself twice on its own page.**
`pod-lifecycle.md:415-416` — "The supported action is `Restart`, which means the container will be
restarted" — and seventy-five lines later `:490-496` opens a section documenting
`RestartAllContainers` "as an action in `restartPolicyRules` at container level". The second
contradiction is a Pod condition: `:515` says the kubelet sets `PodRestartInPlace` on the Pod
status, and the page's own list of the conditions the kubelet manages, at `:608-619`, names eight
and not that one. `PodRestartInPlace` occurs in exactly one file in the pinned tree, and that file
is this one.

**Half the operator set lives in one sentence of the API reference and has no example anywhere.**
`pod-v1.md:923` gives two: `In`, satisfied when the exit code is in the set, and `NotIn`, satisfied
when it is not. `pod-lifecycle.md:415-416` describes the condition as one that "compares the exit
code of the container with a list of given values" and never mentions that the comparison can be
negated. No file in the tree contains an exit-code rule with `operator: NotIn` — every example in
every page, the code sample, and all three of the post's manifests use `In`.

**Four constraints on the rules are stated once and repeated nowhere.** `pod-v1.md:766`: at most 20
rules are allowed; rules can have the same action; identical rules are not forbidden in validation;
and "When rules are specified, container MUST set RestartPolicy explicitly even it if matches the
Pod's RestartPolicy", typo included. `:927` adds a fifth: at most 255 exit-code values. The concept
page carries only the `restartPolicy` requirement, at `:412-413`, and none of the numbers.

**The speed the headline use case is built on is governed by a delay the post never mentions.**
`:49-54` asks for a container that "restart[s] quickly without rescheduling the entire Pod" because
in-place restarts are "critical for better utilization of compute resources".
`pod-lifecycle.md:405`: "The container restarts will follow the same exponential backoff as pod
restart policy described above." Above, at `:385-389`, that schedule is 10s, 20s, 40s and so on,
capped at 300 seconds, with the timer reset only after ten clean minutes. A training container that
exits with a retriable code four times in a row waits longer each time, and nothing in the post says
so.

**The Roadmap paragraph was overtaken in the next release.** `:186-189` says that support for
restarting the entire Pod is coming, that "planning and discussions on these features are in
progress", and invites feedback. `RestartAllContainersOnContainerExits` is alpha from 1.35 — the
release immediately after the one the post announces — and beta and on by default from 1.36. The
plan was stated as a plan in a post that was one release old by the time the code was in a default
cluster.

**The successor got a version-skew guard that this feature never got.** The post's one operational
instruction is to enable the gate on the control plane and on worker nodes, and it says nothing
about what happens if you enable it on some nodes and not others. At the pin, `NodeDeclaredFeatures`
is stable and locked from 1.37, and `node-declared-features.md:66-104` uses
`RestartAllContainersOnContainerExits` as its one worked example: a node that supports it lists it
in `.status.declaredFeatures`, and the scheduler refuses to place a Pod requiring it on a node that
does not. `ContainerRestartRules` is not a declarable feature. A Pod carrying a plain `Restart` rule
still has nothing stopping it from landing on a kubelet that ignores the rule.

**The v1.34 announcement hands a different feature this feature's KEP number.**
`kubernetes-v1-34-release/index.md:416` closes the container-restart-rules section with "This work
was done as part of [KEP \#5307](https://kep.k8s.io/5307)", which agrees with the KEP directory this
post links at `:181-182`. Fifteen lines later, `:431` closes the `EnvFiles` section with "This work
was done as part of [KEP \#5307](https://kep.k8s.io/3721)" — the label from the section above and a
target from somewhere else. The v1.35 announcement gets it right at `:209`.

**One feature, three container image coordinates, and one Pod name used twice for opposite
manifests.** The post writes `docker.io/library/busybox:1.28` five times. The concept page, the code
sample and the node-declared-features page write `registry.k8s.io/busybox:1.27.2` nine times. Two
further examples on the concept page, outside this feature, write a bare `busybox:1.28`. Separately,
`on-failure-pod` names two different Pods: the post's at `:158-175`, which sets no Pod-level
`restartPolicy` and therefore gets `Always`, and `pod-lifecycle.md:424-439`, which sets `OnFailure`
and has different containers in it. Apply both and the second is not an update of the first.

**The post's leading example carries an annotation that its own command makes unreachable.** The
`kubernetes.io/description` at `:105-106` says the Pod "only restart the container only when it
exits with code 42", and the command at `:112` is `sleep 60 && exit 0`. The rule matches 42 and the
container is built never to produce it, so the manifest demonstrates the absence of the feature. The
copy on `pod-lifecycle.md:466-483` drops the annotation and keeps the command.

**What this exercise does not cover, and where it lives**

The container-level `restartPolicy` field has a history, and it is not this post's. [The
announcement that introduced the field as a property of init
containers](../2023/09-native-sidecar-containers.md) owns its sidecar meaning, the three values it
accepts, the shape of a rule, and the observation that the manifest on `pod-lifecycle.md:466-483`
exits 0 and therefore never fires the rule it carries; that exercise also runs the corrected version
that exits 42, so this one does not. [The four ordering experiments run against a started sidecar
that is not yet ready](05-start-sidecar-first.md) owns what a sidecar's restarts do to the container
beside it. `EnvFiles`, the feature on the receiving end of the misdirected KEP link, is described in
[the exercise for a 2016 post about configuration in
containers](../2016/05-configuration-management-with-containers.md). The in-place restart of a whole
Pod is a 2026 subject with a `read` verdict of its own, and appears here only as the release the
Roadmap paragraph was overtaken by.

**The diff, and why**

**Wrong when it was published.** The post's premise sentence at `:23-24` was false on the day it
went out, by two releases and five, depending on whether you date container-level `restartPolicy`
from `SidecarContainers` going stable at 1.33 or from it going on by default at 1.29. This is not a
detail in the middle of the argument; it is the argument. Every one of the three use cases is
introduced as something that "wasn't possible" or is "now possible", and the third one — different
restart policies on different containers — was possible before, for the specific pair of a sidecar
and a main container. What was genuinely new is narrower: `OnFailure` and `Never` as container-level
values, those values on regular app containers, and rules that read the exit code.

**Broke.** The one operational instruction, at `:84-86`, is to enable the `ContainerRestartRules`
gate. There is nothing to enable. It is beta and on by default from 1.35, which is what the lab
cluster runs, and a reader who takes the instruction at face value on a modern cluster goes looking
for a kubelet flag that has no effect and a control-plane flag that has no effect either. The post
is one release old at the point where its setup step stops being a step.

**Still right.** The mechanics are unchanged and every field the post names still parses, validates
and behaves as written. Rules are evaluated in order, the first match wins, an unmatched exit falls
through to the container's `restartPolicy`, and an init container with `restartPolicy: Never` fails
its Pod rather than being retried. The three examples run — with the caveat that the first of them
is built never to reach its own rule.

**Retired by being agreed with.** The Roadmap at `:186-189` asked for restarting the entire Pod and
said the planning was in progress. It shipped as `RestartAllContainersOnContainerExits` in the very
next release, on by default two releases after that, with a Pod condition, a node-declared feature
to guard version skew, a concept-page section and a code sample. The paragraph is the shortest-lived
roadmap in the 2025 census: it was overtaken before the post's own gate left alpha.

**The ladder**

`ContainerRestartRules.md` is a two-rung ladder, parsed from its frontmatter: alpha with
`defaultValue: false` from 1.34 to 1.34, then beta with `defaultValue: true` from 1.35 with no
`toVersion`. Three releases into beta at the pin's v1.37, with no stable rung and no removal date.
The lab runs v1.35, the first release where the gate is on without being asked, so every step below
runs with nothing flipped.

Two neighbouring gates put that pace in context, and both of them are the successor's. Its own gate,
`RestartAllContainersOnContainerExits.md`, is alpha from 1.35 to 1.35 and beta on by default from
1.36 — one release behind, and the same shape. The gate it depends on, `NodeDeclaredFeatures.md`, is
alpha from 1.35 to 1.35, beta on by default from 1.36 to 1.36, and stable with `locked: true` from
1.37. The dependency of the follow-on feature is finished; the feature this post announces is not.
Where `RestartAllContainersOnContainerExits.md:20` names its two prerequisites and warns that
"kubelet startup can fail" without them, `ContainerRestartRules.md` names nothing it needs and
nothing that needs it.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180`, Kubernetes v1.35,
[provisioned](../../strands/lab-topologies.md#provision) and
[baselined](../../strands/lab-topologies.md#node-baseline-steps) as usual. Nothing on the node is
flipped or restarted: every step is a Pod or a dry run, and the whole exercise lives in one
namespace. Step 6 measures delays that grow to forty seconds and step 7 waits on a failing init
container, so budget about ten minutes of wall clock for those two and run them on an otherwise idle
cluster. Pull the one image once, in step 1, before anything is timed.

**Do**

1. Set up, and test the one constraint both the API reference and the concept page state — that a
   container carrying rules must also carry a `restartPolicy` — together with the one the reference
   states and nobody repeats, that two identical rules are legal.

   ```sh
   kubectl version -o yaml | grep gitVersion
   kubectl create namespace bw-restart
   mkdir -p /tmp/bw-restart
   kubectl -n bw-restart run pull --image=busybox:1.36 --restart=Never --command -- sh -c 'exit 0'
   kubectl -n bw-restart wait --for=jsonpath='{.status.phase}'=Succeeded pod/pull --timeout=180s
   kubectl -n bw-restart apply --dry-run=server -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: no-policy }
   spec:
     restartPolicy: Never
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh", "-c", "exit 0"]
         restartPolicyRules:
           - action: Restart
             exitCodes: { operator: In, values: [42] }
   EOF
   kubectl -n bw-restart apply --dry-run=server -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: twice }
   spec:
     restartPolicy: Never
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh", "-c", "exit 0"]
         restartPolicy: Never
         restartPolicyRules:
           - action: Restart
             exitCodes: { operator: In, values: [42] }
           - action: Restart
             exitCodes: { operator: In, values: [42] }
   EOF
   ```

2. Put numbers on the two limits that exist in one sentence of the API reference and nowhere else:
   twenty rules and two hundred and fifty-five exit codes. Each pair submits the allowed count and
   then one more.

   ```sh
   rules() {
     cat <<EOF
   apiVersion: v1
   kind: Pod
   metadata: { name: rules-$1 }
   spec:
     restartPolicy: Never
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh", "-c", "exit 0"]
         restartPolicy: Never
         restartPolicyRules:
   EOF
     i=1
     while [ "$i" -le "$1" ]; do
       printf '        - action: Restart\n          exitCodes: { operator: In, values: [%d] }\n' "$i"
       i=$((i + 1))
     done
   }
   values() {
     V=$(seq 0 "$(( $1 - 1 ))" | paste -sd, -)
     cat <<EOF
   apiVersion: v1
   kind: Pod
   metadata: { name: values-$1 }
   spec:
     restartPolicy: Never
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh", "-c", "exit 0"]
         restartPolicy: Never
         restartPolicyRules:
           - action: Restart
             exitCodes: { operator: In, values: [$V] }
   EOF
   }
   for n in 20 21; do rules "$n" | kubectl -n bw-restart apply --dry-run=server -f -; done
   for n in 255 256; do values "$n" | kubectl -n bw-restart apply --dry-run=server -f -; done
   ```

3. Ask the API server itself which actions it will take, and compare its answer with the reference's
   "only possible value". Three submissions: the documented one, the one the concept page documents
   and the reference does not know about, and one that is not an action at all.

   ```sh
   for a in Restart RestartAllContainers Reschedule; do
     echo "--- action: $a"
     kubectl -n bw-restart apply --dry-run=server -f - <<EOF 2>&1 | tail -3
   apiVersion: v1
   kind: Pod
   metadata: { name: action-probe }
   spec:
     restartPolicy: Never
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh", "-c", "exit 0"]
         restartPolicy: Never
         restartPolicyRules:
           - action: $a
             exitCodes: { operator: In, values: [42] }
   EOF
   done
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' \
     | grep -E 'RestartAllContainersOnContainerExits|NodeDeclaredFeatures' \
     || echo "neither successor gate is reported by this API server"
   ```

4. Run the half of the operator set that has no example in the pinned tree, and put the documented
   ordering rule in a position where it could be observed. Two containers: one exits 0 under a
   `NotIn [0]` rule, one exits 7 under two rules that both match it.

   ```sh
   kubectl -n bw-restart apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: notin }
   spec:
     restartPolicy: Never
     containers:
       - name: clean
         image: busybox:1.36
         command: ["sh", "-c", "echo clean; sleep 5; exit 0"]
         restartPolicy: Never
         restartPolicyRules:
           - action: Restart
             exitCodes: { operator: NotIn, values: [0] }
       - name: dirty
         image: busybox:1.36
         command: ["sh", "-c", "echo dirty; sleep 5; exit 7"]
         restartPolicy: Never
         restartPolicyRules:
           - action: Restart
             exitCodes: { operator: In, values: [7] }
           - action: Restart
             exitCodes: { operator: NotIn, values: [0] }
   EOF
   sleep 90
   kubectl -n bw-restart get pod notin \
     -o jsonpath='{range .status.containerStatuses[*]}{.name} restarts={.restartCount} state={.state}{"\n"}{end}'
   ```

5. Show that the rule list is a layer on top of the container policy and not a replacement for it,
   by arranging for no rule to match. The container exits 7, the only rule names 42, and the
   container policy says `Always`.

   ```sh
   kubectl -n bw-restart apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: fallthrough }
   spec:
     restartPolicy: Never
     containers:
       - name: c
         image: busybox:1.36
         command: ["sh", "-c", "echo attempt; sleep 5; exit 7"]
         restartPolicy: Always
         restartPolicyRules:
           - action: Restart
             exitCodes: { operator: In, values: [42] }
   EOF
   sleep 60
   kubectl -n bw-restart get pod fallthrough \
     -o jsonpath='phase={.status.phase} restarts={.status.containerStatuses[0].restartCount}{"\n"}'
   kubectl -n bw-restart logs fallthrough --tail=5
   ```

6. Measure the delay the post's headline use case never mentions, and check the concept page's claim
   that a rule-driven restart is on the same clock as a policy-driven one. Two containers in one
   Pod, each exiting after a second, one restarted by a rule and one by its policy. Let it run for
   three and a half minutes.

   ```sh
   kubectl -n bw-restart apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: backoff }
   spec:
     restartPolicy: Never
     containers:
       - name: ruled
         image: busybox:1.36
         command: ["sh", "-c", "sleep 1; exit 42"]
         restartPolicy: Never
         restartPolicyRules:
           - action: Restart
             exitCodes: { operator: In, values: [42] }
       - name: policied
         image: busybox:1.36
         command: ["sh", "-c", "sleep 1; exit 1"]
         restartPolicy: Always
   EOF
   i=1
   while [ "$i" -le 14 ]; do
     printf '%s ' "$(date -u +%H:%M:%S)"
     kubectl -n bw-restart get pod backoff \
       -o jsonpath='{range .status.containerStatuses[*]}{.name}={.restartCount} {end}{"\n"}'
     sleep 15
     i=$((i + 1))
   done
   kubectl -n bw-restart get pod backoff -o jsonpath='{range .status.containerStatuses[*]}{.name} reason={.lastState.terminated.reason} exit={.lastState.terminated.exitCode}{"\n"}{end}'
   ```

7. Run the post's second example, shape unchanged from its `:131-149` with an image the lab pulls,
   and watch a Pod whose declared restart policy is `Always` refuse to retry its own initialisation.

   ```sh
   kubectl -n bw-restart apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: fail-pod-if-init-fails
     annotations:
       kubernetes.io/description: "This Pod has an init container that runs only once."
   spec:
     restartPolicy: Always
     initContainers:
       - name: init-once
         image: busybox:1.36
         command: ["sh", "-c", 'echo "Failing initialization" && sleep 10 && exit 1']
         restartPolicy: Never
     containers:
       - name: main-container
         image: busybox:1.36
         command: ["sh", "-c", "sleep 1800 && exit 0"]
   EOF
   sleep 45
   kubectl -n bw-restart get pod fail-pod-if-init-fails \
     -o jsonpath='phase={.status.phase} initRestarts={.status.initContainerStatuses[0].restartCount}{"\n"}'
   kubectl -n bw-restart get pod fail-pod-if-init-fails \
     -o jsonpath='{range .status.conditions[*]}{.type}={.status} {end}{"\n"}'
   ```

8. Apply the two manifests that share the name `on-failure-pod` — the post's at `:158-175` and the
   concept page's at `pod-lifecycle.md:424-439` — one after the other, in that order, into the same
   namespace.

   ```sh
   kubectl -n bw-restart apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: on-failure-pod }
   spec:
     containers:
       - name: restart-on-failure
         image: busybox:1.36
         command: ["sh", "-c", 'echo "Not restarting after success" && sleep 10 && exit 0']
         restartPolicy: OnFailure
       - name: restart-always
         image: busybox:1.36
         command: ["sh", "-c", 'echo "Always restarting" && sleep 1800 && exit 0']
         restartPolicy: Always
   EOF
   kubectl -n bw-restart get pod on-failure-pod -o jsonpath='podPolicy={.spec.restartPolicy}{"\n"}'
   kubectl -n bw-restart apply -f - <<'EOF' 2>&1 | tail -4
   apiVersion: v1
   kind: Pod
   metadata: { name: on-failure-pod }
   spec:
     restartPolicy: OnFailure
     containers:
       - name: try-once-container
         image: busybox:1.36
         command: ["sh", "-c", 'echo "Only running once" && sleep 10 && exit 1']
         restartPolicy: Never
       - name: on-failure-container
         image: busybox:1.36
         command: ["sh", "-c", 'echo "Keep restarting" && sleep 1800 && exit 1']
   EOF
   ```

9. Ask the node what features it declares, which is the guard the successor feature depends on and
   this one does not have. The answer on a v1.35 cluster is the point of the step.

   ```sh
   kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name} declared={.status.declaredFeatures}{"\n"}{end}'
   NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/metrics" | grep '^kubernetes_feature_enabled' \
     | grep -E 'ContainerRestartRules|NodeDeclaredFeatures' \
     || echo "the kubelet reports neither gate"
   kubectl -n bw-restart get events --sort-by=.lastTimestamp \
     --field-selector reason=BackOff -o wide | tail -5
   ```

10. Offline, in a checkout of `kubernetes/website` at the pin, read the four files that describe one
    feature and count how many of them agree. The last two commands are the two mis-citations.

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -n 'only possible value' docs/reference/kubernetes-api/core/pod-v1.md
    grep -rn 'RestartAllContainers' docs examples | grep -v command-line-tools-reference
    sed -n '415,416p;490,496p;608,619p' docs/concepts/workloads/pods/pod-lifecycle.md
    grep -rn "operator: NotIn" docs examples || echo "no NotIn exit-code example in the tree"
    grep -rhoE '[a-z./]*busybox:[0-9.]+' docs/concepts/workloads/pods/pod-lifecycle.md \
      examples/pods/restart-policy/restart-all-containers.yaml \
      docs/concepts/scheduling-eviction/node-declared-features.md \
      blog/_posts/2025/per-container-restart-policy.md | sort | uniq -c
    sed -n '414p;416p;431p' blog/_posts/2025/kubernetes-v1-34-release/index.md
    sed -n '203p' blog/_posts/2025/kubernetes-v1-35-release/index.md
    ```

**Expect**

Step 1 prints a `gitVersion` of `v1.35.x`, creates the namespace, and runs the `pull` Pod to
`Succeeded` — that Pod exists only so that no later step is timing an image pull. The `no-policy`
Pod is refused, and the message names the requirement: rules without a container `restartPolicy` are
not a valid container. The `twice` Pod, carrying the same rule twice over, is accepted and reported
as `configured (dry run)`. That acceptance is the whole of the evidence for `pod-v1.md:766`'s
"Identical rules are not forbidden in validations" — no page a user is likely to read says it, and
nothing but the API server will confirm it.

Step 2 accepts `rules-20` and refuses `rules-21`, then accepts `values-255` and refuses
`values-256`, with messages that should name the limit each time. If either boundary turns out to
sit somewhere else, believe the API server: `pod-v1.md` is generated from the Go doc comments on the
types, and a doc comment and a validation function can drift apart without anything noticing. Note
which of the two numbers the message quotes, because that is the only place in this exercise where
the pinned documentation can be checked against the code that enforces it.

Step 3 accepts `Restart` and refuses `Reschedule`, and the refusal is the interesting output: the
message lists the values the API server will take, and that list is the one `pod-v1.md:902` should
have carried. `RestartAllContainers` is the third submission and the cluster is a release too early
for it — `RestartAllContainersOnContainerExits` is alpha and off at 1.35 — so expect a refusal; what
is worth reading is whether the server refuses it as an unknown value or as a gated one, because
those are two different statements about when the reference sentence became wrong. The metrics grep
may print `NodeDeclaredFeatures` at 0 and is likely to print nothing for the other gate, which is a
kubelet gate rather than an API server one.

Step 4 puts a number on the operator the tree has no example for. `clean` exits 0, `NotIn [0]` does
not match it, the rule list falls through to `restartPolicy: Never`, and the container ends
`terminated` with `restartCount=0`. `dirty` exits 7, the first rule matches, and its `restartCount`
climbs. The second half of the step is a negative result worth keeping: both of `dirty`'s rules
match an exit of 7, both carry the same action, and nothing in the Pod status records which rule
fired. The ordering guarantee at `pod-v1.md:766` is real in the code and unobservable from outside
while `Restart` is the only action this cluster will accept.

Step 5 exits 7 against a rule that names 42. No rule matches, the container's own `Always` takes
over, `restartCount` climbs and the phase stays `Running` — and the Pod-level `Never` sitting above
it never gets a say. The rule list is an override layered on the container policy, which is layered
on the Pod policy, and this is the step that shows all three layers at once.

Step 6 is the measurement the post's first use case needs and does not have. Both counters climb,
and the interval between climbs grows: expect roughly ten seconds, then twenty, then forty, over the
three and a half minutes of sampling, with `restartCount` reaching about five or six on each
container rather than about twenty. Whether `ruled` and `policied` stay in step with each other is
the point of running them side by side: `pod-lifecycle.md:405` says they are on the same schedule,
and two columns of counters printed from one command is the cheapest way to find out. The closing
`jsonpath` should show `reason=Error` with `exit=42` for `ruled` and `exit=1` for `policied`.

Step 7 is the post's own second example and it behaves exactly as the post says. The init container
prints `Failing initialization`, sleeps ten seconds, exits 1, and is not retried: `initRestarts=0`,
and the Pod settles in phase `Failed` with `Initialized=False` among its conditions. The Pod-level
`Always` never reaches the init container, which is the narrow thing this feature actually made
possible and the thing the post's premise sentence buries under a much larger claim.

Step 8 creates a Pod named `on-failure-pod` whose Pod-level policy prints as `Always`, because the
post's manifest sets none and `Always` is the default — a Pod named for a policy it does not have.
The second apply, carrying the concept page's Pod of the same name, is refused: a Pod's spec is
immutable apart from a short list of fields, and container commands and restart policies are not on
it. Two pinned documents describing one feature use one name for two incompatible Pods, and a reader
following both in order finds out at the second `apply`.

Step 9 prints `declared=` with nothing after it. `NodeDeclaredFeatures` is alpha and off at 1.35, so
the node publishes no `.status.declaredFeatures`, and `ContainerRestartRules` would not appear there
in any case because it is not a declarable feature at the pin either. The kubelet's own metrics
should show `ContainerRestartRules` at 1. This is the part the lab cannot demonstrate: the guard
that keeps a Pod off a node that would ignore its restart rules exists only for the successor
action, and seeing it work needs at least two nodes with different gates, which the `solo` topology
does not have. Record the empty field rather than skipping the step — the absence is the finding.
The `BackOff` events at the end are step 6's delays in the form the cluster reports them.

Step 10 is the count. The first grep prints the "only possible value" sentence; the second prints
`RestartAllContainers` from the concept page, the node-declared-features page and the code sample,
and from nothing under `docs/reference/kubernetes-api`. The `sed` prints the two contradicting
paragraphs and the condition list that omits `PodRestartInPlace`. The `NotIn` grep should print
nothing at all. The image count should come out three ways for one feature. The last two `sed`
commands print the premise sentence from each release announcement and, between them, the line where
`\#5307` points at `kep.k8s.io/3721`.

**Read on**

11. [The other list of rules in Kubernetes that reads an exit code and decides what happens
    next](../2024/09-pod-failure-policy-for-jobs-goes-ga.md), reached GA for Jobs two releases
    before containers got a list of their own, with a reason string nothing else in the tree spells
    the same way.

12. [The two Pod conditions that did make it onto the page's own
    list](../2023/07-in-place-pod-resize-alpha.md), added by a feature whose status field the post
    explained in four values that did not survive as four.

13. [The alpha gate that changes the numbers step 6
    measures](04-kubernetes-v1-33-updates-to-container-lifecycle.md) — one of the eighteen counted
    there, and the reason the backoff schedule quoted on the concept page is a default rather than a
    constant.

14. [A reference page generated from Go comments that disagrees with the page it points
    at](../2024/13-kubeadm-v1beta4.md), where the fully populated example does not parse and the
    prose misspells a field the post gets right — the same failure mode as `pod-v1.md:902`, from the
    other end.

15. *Unanswerable from the pin.* Nothing in the tree records why `pod-v1.md` never learned about the
    second action. The sentence is generated from a doc comment on the Go type, so either the
    comment was not updated when `RestartAllContainers` landed or the field's validation genuinely
    still rejects it and the concept page is describing a kubelet behaviour the API does not model.
    The two readings have opposite consequences for anyone writing a rule, and the checkout contains
    no Go source to settle it.

**Teardown**

One namespace holds every object this exercise created, and no step changed anything on the node.
The dry runs in steps 1 to 3 wrote nothing at all.

```sh
kubectl delete namespace bw-restart
rm -rf /tmp/bw-restart
```

The checkout of `kubernetes/website` at the pin was only read, so nothing there needs undoing. If
you want step 6's numbers again, delete the `backoff` Pod and recreate it rather than reusing it:
the kubelet resets a container's backoff timer only after ten clean minutes, and a Pod that has
already climbed to a forty-second delay will keep climbing from there.
