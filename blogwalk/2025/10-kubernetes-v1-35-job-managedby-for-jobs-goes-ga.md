<a id="kubernetes-v1-35-job-managedby-for-jobs-goes-ga"></a>

# The extensive validation rules this post sends you to a KEP to read are in the tree already, as sentences inside six cells of one generated table; the sentence saying which values the field accepts is wrong on both pages that carry it; and its reference link survives on a redirect

**Post** — [Kubernetes v1.35: Job Managed By Goes
GA](https://kubernetes.io/blog/2025/12/18/kubernetes-v1-35-job-managedby-for-jobs-goes-ga/),
2025-12-18.

6,281 bytes, 93 lines, 717 words of body — fourth-smallest of 2025's twelve `walk` posts, and tenth
of the twelve by publication date. Two authors at two organisations. Six `##` headings, no `###`
headings, and not one fenced block: no YAML, no command, nothing to copy. Twenty-three markdown
links, of which nineteen leave kubernetes.io, three point into the documentation and one jumps
within the page. Two of those three documentation links go to the same concept page, one of them to
a section anchor; the third points at a path no page occupies at the pin.

**As written**

`:11` announces that specifying an external Job controller through `.spec.managedBy` graduates to
General Availability in v1.35, and `:13` says the feature lets external controllers take full
responsibility for Job reconciliation, naming multi-cluster dispatching with MultiKueue as the
pattern it unlocks.

`:15-25` gives the motivation. A Management Cluster dispatches Jobs without executing them: it
accepts the objects so it can track status, but skips creating Pods. Worker Clusters receive the
dispatched Jobs and run them as ordinary Jobs with no `.spec.managedBy` set. Users talk to the
Management Cluster and watch progress live, because the MultiKueue controller copies status back
from the mirror Job on the worker.

`:27-29` answers the obvious objection under the heading *Why not just disable the Job controller?*
— two numbered reasons. Managed control planes do not let users touch controller manager flags, and
a hybrid cluster needs to dispatch heavy work remotely while still running small Jobs locally, which
is a per-Job decision rather than a per-cluster one.

`:31-35` states the mechanism as two modes. Standard is unset, or set to the reserved value
`kubernetes.io/job-controller`, and the built-in controller reconciles as usual. Delegation is any
other value, and the built-in controller "skips reconciliation entirely for that Job". `:37` says
the field is immutable "to prevent orphaned Pods or resource leaks" — you cannot transfer a running
Job from one controller to another.

`:39-41` is the part this exercise is built on. An external controller has to be conformant with the
Job API, and to enforce that conformance "a significant part of the effort was to introduce the
extensive Job status validation rules". The sentence does not say what those rules are; it points at
the *How can you learn more?* section, which points at a KEP.

`:43-54` lists five projects adding the field or an equivalent — JobSet, Kubeflow Trainer, KubeRay,
AppWrapper and Tekton Pipelines — and calls `.spec.managedBy` "the standard interface for delegating
control in the Kubernetes batch ecosystem". `:54` adds a caveat worth keeping: building a custom Job
controller from scratch on top of this field is possible, but "we haven't observed that yet".

`:56-69` is the reading list: three documentation links, the KEP for the managed-by mechanism
including its Job status validation rules, the Kueue KEP for MultiKueue, and a MultiKueue task
guide. `:71` and `:81` are acknowledgments and the usual invitation to the batch working group.

**As it runs now**

**The whole documented surface of this field is one section and one table row.** `managedBy` occurs
in exactly two files under `docs`. One is the Job concept page, where `job.md:1303` opens
*Delegation of managing a Job object to external controller*, `:1305` carries the feature-state
marker, and the section runs twenty-eight lines to `:1330` — of which nineteen are notes. The other
is the generated Job reference, where `job-v1.md:92-93` is one row of the JobSpec table. A GA field
announced as the standard interface for an ecosystem has two mentions, and one of them is generated
from a Go comment.

**The rules the post sends you to a KEP for are in the tree, as sentences inside a table.** The
JobStatus table at `job-v1.md:139` has eleven rows, and six of them state a rule rather than
describe a field. `:157` says the completion time "is set when the job finishes successfully, and
only then", that it "cannot be updated or removed", and that it "indicates the same or later point
in time as the startTime field". `:161` says a Job "cannot have both the 'Complete' and 'Failed'
conditions" and additionally "cannot be in the 'Complete' and 'FailureTarget' conditions". `:177`
says `startTime` "can only be removed when the job is suspended" and "cannot be modified while the
job is unsuspended or finished". `:165` and `:181` say `failed` and `succeeded` increase
monotonically, and `:169` says failed and completed indexes cannot overlap. That is the conformance
contract, written down, in the tree, on the page the post links.

**The phrase the post uses for those rules appears nowhere in the documentation.** `status
validation` occurs twice in the whole checkout, at post `:40` and post `:66`, and in no file under
`docs`. There is no page called *Job status validation*, no list of the rules as rules, and no
pointer from the concept page to the six table cells that hold them. A reader who searches the site
for the thing the post says was a significant part of the work finds the post.

**Both prose descriptions of which values the field accepts are wrong, and wrong the same way.**
Post `:35` says delegation is "any other value"; `job.md:1311-1312` says "any value other than
`kubernetes.io/job-controller`". The rule is at `job-v1.md:93`: the value "must be a valid
domain-prefixed path (e.g. acme.io/foo)", every character before the first `/` must be a valid RFC
1123 subdomain, every character after it must be a valid RFC 3986 HTTP path character, and the whole
string "cannot exceed 63 characters". `foo` is a value other than the reserved one and it is not a
domain-prefixed path. Step 2 puts sixteen spellings through a server-side dry run and reads the
boundary off the API server instead of off either sentence.

**The concept page drops one of the three cases the reference states.** `job-v1.md:93` says the
built-in controller reconciles Jobs "which don't have this field at all or the field value is the
reserved string", and skips the rest: three cases, two of them standard. The post gives all three at
`:34`. `job.md:1310-1312` gives only the contrast between a custom value and the reserved string,
and never says that leaving the field unset is the standard case — which is the case every Job on
every cluster is actually in.

**The gate this post announces as stable is offered two screens earlier as a switch, next to a gate
that cannot be switched.** `job.md:836-839` says that from v1.31 the controller adds the terminal
conditions only after every Pod has terminated, and then says "You can control this behavior by
using the `JobManagedBy` and the `JobPodReplacementPolicy` (both enabled by default) feature gates".
`JobPodReplacementPolicy.md` takes its stable rung at 1.34 with `locked: true`, so at the lab's
v1.35 that gate cannot be set to anything but `true` and the sentence offers a control that half of
it no longer provides.

**The same sentence gives the gate a second meaning that its own file does not mention.** The body
of `JobManagedBy.md` is one line: "Allows to delegate reconciliation of a Job object to an external
controller." Nothing about terminal conditions, nothing about Pod termination ordering. `job.md:838`
has the same gate governing when `Complete` and `Failed` are added to a Job the built-in controller
is reconciling — a behaviour that only exists when the field is *not* set. The two pages describe
the same switch as controlling two unrelated things, and neither mentions the other's reading.

**A field the reference calls beta-level is populated under a gate that has been locked stable for
two releases.** `job-v1.md:185` describes `status.terminating` as "beta-level" and says the Job
controller populates it "when the feature gate JobPodReplacementPolicy is enabled (enabled by
default)". That gate has been stable and locked since 1.34. The sentence is generated from the Go
comment, so the field's own description is the last place in the tree still calling it beta.

**The one Job API link the post gives points at a path no page occupies.** Post `:39` links
`/docs/reference/kubernetes-api/workload-resources/job-v1/`. At the pin the file is
`docs/reference/kubernetes-api/batch/job-v1.md`, and the old path survives only because
`static/_redirects.base:569` sends it to the new one — one of twenty `workload-resources/*` lines in
that block. The concept page the post also links repeats the retired path at `job.md:1324`, in the
note telling external controller authors to review the API in detail. Two other files still use it:
`JobReadyPods.md:27` and the 2022 Job-tracking announcement at `:122`. [The exercise that owns the
redirect file](02-endpoints-deprecation.md) covers what that file is and what happens when a line
leaves it.

**One string is four different things, and the reference says one of the four stopped mattering nine
releases ago.** `batch.kubernetes.io/job-tracking` matches seven lines in three files under `docs`.
It is an annotation in two captured sample outputs at `job.md:69` and `:102`; it is the finalizer
the built-in controller puts on every Pod it creates at `:1222`; it is a finalizer "reserved for the
built-in controller" that external controllers must not use at `:1329`; and it is inside the help
text of the beta metric `job_controller_terminated_pods_tracking_finalizer_total` at
`metrics.md:512`. Meanwhile `labels-annotations-taints/_index.md:1781-1792` heads the annotation
"(deprecated)" and says at `:1791` that "Adding or removing this annotation no longer has an effect
(Kubernetes v1.27 and later)". The concept page's own sample output still prints it.

**Those two sample outputs were captured three years apart, and one of them is not valid YAML.** The
describe tab opens at `job.md:62` and its `Start Time:` at `:72` reads `Mon, 02 Dec 2019`; the YAML
tab opens at `:98` and its `creationTimestamp` at `:104` reads `2022-11-10`. Inside the second,
`:102` is `annotations: batch.kubernetes.io/job-tracking: ""` — a mapping value where a mapping was
expected, which a YAML parser rejects outright. The tab is declared `codelang="bash"`, so nothing
checks it. `:103` is one of eighteen lines in the file carrying trailing whitespace.

**Nothing anywhere says what a delegated Job does with the rest of its own spec.** A Job carries
`activeDeadlineSeconds`, `backoffLimit`, `ttlSecondsAfterFinished`, `suspend`, `podFailurePolicy`,
`successPolicy` and `parallelism`, and every one of them is implemented by the controller being told
to stand down. The delegation section says nothing about any of them. The fields stay settable, the
API server accepts them, and they mean nothing. Steps 5 and 9 measure four of them.

**The note hedges what the post states flatly.** `job.md:1314-1317` warns that if the named
controller is not installed then the Job "may not be reconciled at all". The post at `:35` says the
built-in controller "skips reconciliation entirely". Those are different claims: one says the
outcome is uncertain, the other says the mechanism is unconditional. Step 4 settles it by creating a
Job whose named controller does not exist and watching what the cluster does with it.

**The reason the feature exists is not in the tree at all.** `kueue` matches no file under `docs`,
case-insensitively, so neither Kueue nor MultiKueue — the architecture the post spends its first
eleven lines on — is documented on the site. Of the five adopters it names, `jobset` matches five
files and `kubeflow` one; `kuberay`, `appwrapper` and `tekton` match none. Nineteen of the post's
twenty-three links leave kubernetes.io, which for a GA announcement is the shape of a feature whose
users are all somewhere else.

**The page already had a delegation story, and never connects the two.** `job.md:1113-1117` says the
`suspend` field "is the first step towards achieving those semantics" and "allows a custom queue
controller to decide when a job should start", then notes that once a Job is unsuspended the queue
controller has no influence over placement. That is the same problem `managedBy` solves, one section
earlier and many releases older. The suspend sections never mention `managedBy`; the delegation
section never mentions suspend. A reader arriving at either has no way to learn the other exists.

**"Reserved for the built-in controller" is advice, not admission control.** `job.md:1329` tells
external controller authors not to use the `batch.kubernetes.io/job-tracking` finalizer. Nothing in
the tree describes a webhook, a validation rule or a policy that enforces that, and step 6 checks
whether anything does by putting that exact finalizer on a Pod that no Job owns.

**What this exercise does not cover, and where it lives**

Finalizers as a mechanism — what one does to a delete, the three cascade modes, the
`foregroundDeletion` name and the orphan case — belong to [the exercise built on the finalizers
tutorial](../2021/03-using-finalizers-to-control-deletion.md), and step 6 below leans on that rather
than repeating it. The rest of the Job page's failure machinery — `podFailurePolicy`, the four
actions, the `DisruptionTarget` condition and the terminal conditions the built-in controller writes
— belongs to [the exercise on the pod failure policy
announcement](../2024/09-pod-failure-policy-for-jobs-goes-ga.md), which at its `:181` explicitly
sets `managedBy` aside as a separate feature. That is the line this exercise picks up. CronJob's own
graduation, its schedule handling and the deleted gate behind it belong to [the CronJob GA
exercise](../2021/01-kubernetes-release-1-21-cronjob-ga.md); step 9 uses a CronJob only as an
instrument. The `.spec.scheduling` block that v1.35 adds to the Job API is a different feature in
the same release and is not touched here.

**The diff, and why** — four of the seven cases.

**Wrong when it was published: the sentence that says which values are accepted.** "If set to any
other value" was not true on the day it was written and is not true now. The field takes a
domain-prefixed path of at most sixty-three characters, and the post, like the concept page it sends
you to, describes a much larger set. A reader following the post literally will try `mine` or
`my-controller`, get a validation error, and have nothing on either page to explain it. The rule
exists, in the generated reference, in the same sentence that gives the example `acme.io/foo`.

**Never absorbed: the validation contract, as a contract.** The post's own framing is that the
significant work was the status validation rules, and that an external controller must be conformant
with them. Those rules are in the tree, six of them, as prose inside table cells generated from Go
comments. No page collects them. The concept page, which is the page an external controller author
will actually read, states none of them and does not mention that they exist. The post links a KEP
instead, which is the honest move and also the measure of the gap.

**Still right: the mechanism.** Set the field to a value nothing is listening for and the Job does
nothing, forever, with no Pods, no events and no status — exactly as `:35` says. The immutability
holds in both directions. The reserved value behaves as the standard case. Five releases after the
alpha rung opened, the one-paragraph description of how the field works is accurate, and it is the
description of *behaviour* rather than of *values* that is accurate.

**Overtaken by stasis: the page around the new section.** The delegation section was added to a page
whose sample outputs date from 2019 and 2022, still print an annotation deprecated in v1.27, and
include a YAML block that does not parse. Two sections earlier the page offers a feature gate as a
switch beside a gate that has been locked for two releases. None of that was made wrong by this
post; none of it was touched by it either. The newest section on the page sits in the oldest part of
it.

**The ladder**

`JobManagedBy.md` is a three-rung ladder, parsed from its frontmatter: alpha with `defaultValue:
false` from 1.30 to 1.31, beta with `defaultValue: true` from 1.32 to 1.34, and stable with
`defaultValue: true` from 1.35 with no `toVersion` and, unlike most graduations worth noticing, no
`locked` key at all. The lab runs v1.35, so this is the first release in which the gate is stable,
and it can still be turned off.

Three numbers put that ladder in context. Six gate files take a stable rung at 1.35, and three of
the six — this one, `ImageMaximumGCAge` and `InformerResourceVersion` — leave that rung unlocked, so
the field the post announces as generally available is one an operator can still remove from the
API. Of the 278 gate files that carry a stable rung, 47 mark it `locked: true`, so an unlocked
stable rung is the common case and not the story; the story is that the post never mentions a gate
at all, and neither does the section it links. And the graduation was quick: of the 242 gates whose
frontmatter carries both an alpha and a stable rung, this one's five-release span from 1.30 to 1.35
is beaten by 110 and matched by 25 others, which puts it comfortably in the faster half.

One of those 25 is `JobBackoffLimitPerIndex`, another batch feature announced in this same
directory, and another is `SidecarContainers`. The comparison worth keeping is not with them but
with the exercise immediately before this one, where a nine-release alpha and a locked stable rung
produced a post that also named no gate. Two consecutive graduations, opposite ladders, and the same
silence about where the switch is.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180`, Kubernetes v1.35,
[provisioned](../../strands/lab-topologies.md#provision) and
[baselined](../../strands/lab-topologies.md#node-baseline-steps) as usual. Everything below lives in
a namespace called `bw-managedby`, and *Teardown* is one `kubectl delete namespace` plus one
directory. Nothing is installed: the external controller this exercise is about is played by you,
with `kubectl patch --subresource=status`, which is the whole point — the feature's contract is a
set of writes the API server will accept, and a human with a shell can make every one of them. No
CSI driver, no webhook, no second node. Steps 1 to 9 run from wherever you run `kubectl`, with a
scratch directory at `/tmp/bw-managedby`; step 10 runs offline against a checkout of
`kubernetes/website` at the pin, with `W` set to its `content/en` directory. Steps 5 and 9 wait:
sixty seconds in one and about three and a half minutes in the other, both of them waiting for
something that is not going to happen.

**Do**

1. Ask the API server for the field and for the rules, before reading either page again. `kubectl
   explain` is generated from the same OpenAPI schema as the reference table, so whatever the table
   says about validation, the server will say too — and the two gate names from `job.md:838` can be
   checked against the cluster in the same breath:

   ```sh
   kubectl version -o json | grep -m2 gitVersion
   kubectl create namespace bw-managedby
   mkdir -p /tmp/bw-managedby
   kubectl explain job.spec.managedBy
   kubectl explain job.status.terminating
   kubectl explain job.status.completionTime
   kubectl explain job.status.startTime
   kubectl explain job.status.conditions | sed -n '1,20p'
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' \
     | grep -E 'JobManagedBy|JobPodReplacementPolicy'
   ```

2. Find the boundary the prose does not describe. Sixteen candidate values, each one sent through a
   server-side dry run so the API server's own validation answers rather than the client's. Four of
   them are in the documentation, four are shapes the RFC 1123 half should reject, four test the RFC
   3986 half, and four test the length cap and the empty case:

   ```sh
   cd /tmp/bw-managedby
   cat > job-tmpl.yaml <<'EOF'
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: PROBE
     namespace: bw-managedby
   spec:
     managedBy: "MANAGEDBY"
     backoffLimit: 0
     template:
       spec:
         restartPolicy: Never
         containers:
         - name: c
           image: registry.k8s.io/e2e-test-images/agnhost:2.53
           args: ["entrypoint-tester"]
   EOF
   { echo 'acme.io/foo'
     echo 'kubernetes.io/job-controller'
     echo 'kubernetes.io/foo'
     echo 'k8s.io/foo'
     echo 'foo'
     echo '/foo'
     echo 'Example.com/foo'
     echo 'example_com/foo'
     echo 'example.com/a/b/c'
     echo 'example.com/foo%20bar'
     echo 'example.com/foo?x=1'
     echo 'example.com/foo bar'
     echo 'example.com/'
     echo ''
     printf 'example.com/%s\n' "$(printf 'a%.0s' $(seq 1 51))"
     printf 'example.com/%s\n' "$(printf 'a%.0s' $(seq 1 52))"
   } > values.txt
   awk '{ printf "%2d chars  %s\n", length, $0 }' values.txt
   ```

   Then run the census. Nothing is created: `--dry-run=server` runs admission and validation and
   throws the object away.

   ```sh
   i=0
   while IFS= read -r V; do
     i=$((i + 1))
     sed -e "s|PROBE|probe-$i|" -e "s|MANAGEDBY|$V|" job-tmpl.yaml > probe.yaml
     R=$(kubectl create --dry-run=server -f probe.yaml 2>&1 | head -1)
     printf '%2d  %-30s %s\n' "$i" "${V:-(empty string)}" "$(echo "$R" | cut -c1-96)"
   done < values.txt
   ```

3. Create the three Jobs the rest of the exercise runs on, then test the immutability claim in every
   direction it can be tested. `runner` is the control with no field at all, `reserved` carries the
   reserved value, and `sitter` names a controller that does not exist:

   ```sh
   for NAME in runner:'' reserved:kubernetes.io/job-controller sitter:acme.io/bw; do
     N=${NAME%%:*}; M=${NAME#*:}
     if [ -z "$M" ]; then SPEC=""; else SPEC="  managedBy: \"$M\""; fi
     cat <<EOF | kubectl apply -f -
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: $N
     namespace: bw-managedby
   spec:
   $SPEC
     backoffLimit: 0
     template:
       spec:
         restartPolicy: Never
         containers:
         - name: c
           image: registry.k8s.io/e2e-test-images/agnhost:2.53
           args: ["entrypoint-tester"]
   EOF
   done
   kubectl get jobs -n bw-managedby -o custom-columns=\
   NAME:.metadata.name,MANAGEDBY:.spec.managedBy,COMPLETIONS:.status.succeeded
   ```

   Five patches, five different transitions. Adding the field to a Job that never had it, moving off
   the reserved value, moving between two custom values, clearing the field, and setting it to the
   value it already has:

   ```sh
   try() {
     printf '%-34s %s\n' "$1" \
       "$(kubectl patch job "$2" -n bw-managedby --type=merge -p "$3" 2>&1 \
          | head -1 | cut -c1-92)"
   }
   try 'unset -> custom'          runner   '{"spec":{"managedBy":"acme.io/bw"}}'
   try 'reserved -> custom'       reserved '{"spec":{"managedBy":"acme.io/bw"}}'
   try 'custom -> other custom'   sitter   '{"spec":{"managedBy":"other.io/bw"}}'
   try 'custom -> unset'          sitter   '{"spec":{"managedBy":null}}'
   try 'custom -> the same value' sitter   '{"spec":{"managedBy":"acme.io/bw"}}'
   ```

4. Look at what the three Jobs have done. This is the whole behavioural claim of the post, and it
   takes four commands to settle. Read the Pod list first, because it is the shortest answer:

   ```sh
   kubectl get pods -n bw-managedby -o wide
   kubectl get jobs -n bw-managedby
   for J in runner reserved sitter; do
     printf '=== %s\n' "$J"
     kubectl get job "$J" -n bw-managedby -o jsonpath='{.status}'; echo
   done
   kubectl get events -n bw-managedby --sort-by=.lastTimestamp \
     -o custom-columns=OBJECT:.involvedObject.name,REASON:.reason,FROM:.source.component
   kubectl describe job sitter -n bw-managedby | tail -8
   ```

   Then leave it alone for a minute and check that nothing changed while you were not watching,
   which is the part a one-shot read cannot establish:

   ```sh
   sleep 60
   kubectl get job sitter -n bw-managedby -o jsonpath='{.status}'; echo
   kubectl get job sitter -n bw-managedby -o jsonpath='{.metadata.managedFields[*].manager}'; echo
   ```

5. Set the fields that only the built-in controller implements, on a Job the built-in controller is
   not reconciling. `activeDeadlineSeconds: 10` should kill the Job ten seconds after it starts;
   `ttlSecondsAfterFinished: 5` should delete it five seconds after it finishes; `suspend` should
   add a condition and an event. All three are accepted by the API server without complaint:

   ```sh
   cat <<'EOF' | kubectl apply -f -
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: deadline
     namespace: bw-managedby
   spec:
     managedBy: acme.io/bw
     activeDeadlineSeconds: 10
     ttlSecondsAfterFinished: 5
     backoffLimit: 0
     parallelism: 4
     completions: 4
     template:
       spec:
         restartPolicy: Never
         containers:
         - name: c
           image: registry.k8s.io/e2e-test-images/agnhost:2.53
           args: ["entrypoint-tester"]
   EOF
   sleep 60
   kubectl get job deadline -n bw-managedby
   kubectl get job deadline -n bw-managedby -o jsonpath='{.status}'; echo
   ```

   Then toggle `suspend` twice on `sitter` and look for the condition and the two events that
   `job.md:1074-1098` says toggling it produces:

   ```sh
   kubectl patch job sitter -n bw-managedby --type=strategic \
     -p '{"spec":{"suspend":true}}'
   kubectl get job sitter -n bw-managedby -o jsonpath='{.status.conditions}'; echo
   kubectl patch job sitter -n bw-managedby --type=strategic \
     -p '{"spec":{"suspend":false}}'
   kubectl get events -n bw-managedby --field-selector involvedObject.name=sitter
   ```

6. Take the three meanings of `batch.kubernetes.io/job-tracking` apart. First the finalizer, on a
   Pod belonging to a Job the built-in controller *is* reconciling, which has to be caught while the
   Pod is still alive — so this one sleeps rather than exits:

   ```sh
   cat <<'EOF' | kubectl apply -f -
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: tracked
     namespace: bw-managedby
   spec:
     backoffLimit: 0
     template:
       spec:
         restartPolicy: Never
         containers:
         - name: c
           image: busybox:1.36
           command: ["sh", "-c", "sleep 600"]
   EOF
   kubectl wait --for=condition=ready pod -n bw-managedby \
     -l batch.kubernetes.io/job-name=tracked --timeout=90s
   kubectl get pods -n bw-managedby -l batch.kubernetes.io/job-name=tracked \
     -o jsonpath='{range .items[*]}{.metadata.name}{"  "}{.metadata.finalizers}{"\n"}{end}'
   kubectl get job tracked -n bw-managedby -o jsonpath='{.metadata.annotations}'; echo
   ```

   Then the annotation, added by hand to both a normal Job and a delegated one, to see whether the
   string the reference calls deprecated does anything to either:

   ```sh
   kubectl annotate job tracked -n bw-managedby batch.kubernetes.io/job-tracking=""
   kubectl annotate job sitter  -n bw-managedby batch.kubernetes.io/job-tracking=""
   sleep 10
   kubectl get job sitter -n bw-managedby -o jsonpath='{.status}'; echo
   kubectl get job tracked -n bw-managedby -o jsonpath='{.status}'; echo
   ```

   Then the claim that the finalizer is reserved. Put that exact string on a Pod no Job owns and see
   whether anything stops you, then take it back off so the namespace can be deleted later:

   ```sh
   cat <<'EOF' | kubectl apply -f -
   apiVersion: v1
   kind: Pod
   metadata:
     name: squatter
     namespace: bw-managedby
     finalizers:
     - batch.kubernetes.io/job-tracking
   spec:
     restartPolicy: Never
     containers:
     - name: c
       image: registry.k8s.io/e2e-test-images/agnhost:2.53
       args: ["entrypoint-tester"]
   EOF
   kubectl get pod squatter -n bw-managedby -o jsonpath='{.metadata.finalizers}'; echo
   kubectl delete pod squatter -n bw-managedby --wait=false
   kubectl get pod squatter -n bw-managedby \
     -o jsonpath='{.metadata.deletionTimestamp}{"\n"}'
   kubectl patch pod squatter -n bw-managedby --type=merge \
     -p '{"metadata":{"finalizers":null}}'
   kubectl get pod squatter -n bw-managedby 2>&1 | tail -1
   ```

7. Be the missing controller. Everything the external controller is responsible for is a write to
   the status subresource, and every one of those writes can be made from a shell. Drive `sitter`
   from nothing to complete, reading the `kubectl get` columns after each write:

   ```sh
   T0=$(date -u +%Y-%m-%dT%H:%M:%SZ)
   kubectl patch job sitter -n bw-managedby --subresource=status --type=merge \
     -p "{\"status\":{\"startTime\":\"$T0\",\"active\":1,\"ready\":0}}"
   kubectl get job sitter -n bw-managedby
   sleep 5
   T1=$(date -u +%Y-%m-%dT%H:%M:%SZ)
   COND() { printf '{"type":"%s","status":"True","lastProbeTime":"%s","lastTransitionTime":"%s"}' \
     "$1" "$T1" "$T1"; }
   kubectl patch job sitter -n bw-managedby --subresource=status --type=merge \
     -p "{\"status\":{\"active\":0,\"succeeded\":1,\"completionTime\":\"$T1\",\
   \"conditions\":[$(COND SuccessCriteriaMet),$(COND Complete)]}}"
   kubectl get job sitter -n bw-managedby
   kubectl wait --for=condition=complete job/sitter -n bw-managedby --timeout=5s
   kubectl get pods -n bw-managedby | grep -c sitter || true
   ```

8. Now find the rules. Eight writes that the six sentences in the JobStatus table say should be
   refused, made against a fresh delegated Job, and then two of the same writes against the Job the
   built-in controller ran, to see whether the contract is one the whole API enforces or one that
   arrived with this feature:

   ```sh
   cat <<'EOF' | kubectl apply -f -
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: judge
     namespace: bw-managedby
   spec:
     managedBy: acme.io/bw
     backoffLimit: 0
     completions: 2
     parallelism: 2
     template:
       spec:
         restartPolicy: Never
         containers:
         - name: c
           image: registry.k8s.io/e2e-test-images/agnhost:2.53
           args: ["entrypoint-tester"]
   EOF
   NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
   PAST=$(date -u -d '-1 hour' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null \
     || date -u -v-1H +%Y-%m-%dT%H:%M:%SZ)
   C() { printf '{"type":"%s","status":"True","lastProbeTime":"%s","lastTransitionTime":"%s"}' \
     "$1" "$NOW" "$NOW"; }
   st() {
     printf '%-34s %-7s %s\n' "$1" "$2" \
       "$(kubectl patch job "$2" -n bw-managedby --subresource=status --type=merge \
          -p "$3" 2>&1 | head -1 | cut -c1-84)"
   }
   kubectl patch job judge -n bw-managedby --subresource=status --type=merge \
     -p "{\"status\":{\"startTime\":\"$NOW\",\"active\":2}}" >/dev/null
   st 'Complete and Failed together' judge "{\"status\":{\"conditions\":[$(C Complete),$(C Failed)]}}"
   st 'Complete and FailureTarget'   judge "{\"status\":{\"conditions\":[$(C Complete),$(C FailureTarget)]}}"
   st 'completionTime, no condition' judge "{\"status\":{\"completionTime\":\"$NOW\"}}"
   st 'completionTime before start'  judge "{\"status\":{\"completionTime\":\"$PAST\",\"conditions\":[$(C Complete)]}}"
   st 'startTime cleared'            judge '{"status":{"startTime":null}}'
   st 'active negative'              judge '{"status":{"active":-1}}'
   st 'succeeded above completions'  judge '{"status":{"succeeded":9}}'
   st 'ready above active'           judge '{"status":{"ready":7}}'
   st 'Complete and Failed together' runner "{\"status\":{\"conditions\":[$(C Complete),$(C Failed)]}}"
   st 'succeeded above completions'  runner '{"status":{"succeeded":9}}'
   ```

9. Hand a CronJob a job template nothing is listening for. The CronJob controller tracks its
   children through `.status.active` and clears an entry when the child finishes; a delegated child
   never finishes. With `concurrencyPolicy: Forbid` that is not a slow leak, it is a permanent stop
   — and nothing in the two files that mention `managedBy` says so:

   ```sh
   cat <<'EOF' | kubectl apply -f -
   apiVersion: batch/v1
   kind: CronJob
   metadata:
     name: holder
     namespace: bw-managedby
   spec:
     schedule: "* * * * *"
     concurrencyPolicy: Forbid
     jobTemplate:
       spec:
         managedBy: acme.io/bw
         backoffLimit: 0
         template:
           spec:
             restartPolicy: Never
             containers:
             - name: c
               image: registry.k8s.io/e2e-test-images/agnhost:2.53
               args: ["entrypoint-tester"]
   EOF
   sleep 200
   kubectl get cronjob holder -n bw-managedby
   kubectl get jobs -n bw-managedby -o name | grep holder
   kubectl get cronjob holder -n bw-managedby -o jsonpath='{.status.active}'; echo
   kubectl get events -n bw-managedby --field-selector involvedObject.name=holder \
     -o custom-columns=REASON:.reason,COUNT:.count,MESSAGE:.message
   ```

   Then remove the child by hand and give the schedule one more minute, which is the only way to
   tell a stopped CronJob from a broken one:

   ```sh
   for J in $(kubectl get jobs -n bw-managedby -o name | grep holder); do
     kubectl delete "$J" -n bw-managedby
   done
   sleep 70
   kubectl get cronjob holder -n bw-managedby
   kubectl get jobs -n bw-managedby -o name | grep -c holder || true
   kubectl delete cronjob holder -n bw-managedby
   ```

10. Count the documentation, offline, in the checkout at the pin. Every claim in *As it runs now*
    above is one of these commands:

    ```sh
    cd /path/to/kubernetes/website/content/en
    W=$(pwd)
    grep -rn 'managedBy' "$W/docs"
    grep -rn 'JobManagedBy' "$W/docs" | grep -v command-line-tools-reference
    grep -rn 'status validation' "$W/docs" "$W/blog" | wc -l
    grep -rn 'workload-resources/job-v1' "$W/docs" "$W/blog"
    grep -n 'workload-resources/job-v1' "$W/../../static/_redirects.base"
    grep -rn 'batch.kubernetes.io/job-tracking' "$W/docs"
    grep -rli 'kueue' "$W/docs" | wc -l
    for T in jobset kubeflow kuberay appwrapper tekton; do
      printf '%-12s %s\n' "$T" "$(grep -rli "$T" "$W/docs" | wc -l | tr -d ' ')"
    done
    ```

    Then read the two places the rules and the ladder actually live, and count the trailing
    whitespace on the page the post sends you to:

    ```sh
    sed -n '139,192p' "$W/docs/reference/kubernetes-api/batch/job-v1.md" \
      | sed 's/<[^>]*>//g' | grep -v '^ *$'
    sed -n '/^stages:/,/^---$/p' \
      "$W/docs/reference/command-line-tools-reference/feature-gates/JobManagedBy.md"
    sed -n '/^stages:/,/^---$/p' \
      "$W/docs/reference/command-line-tools-reference/feature-gates/JobPodReplacementPolicy.md"
    grep -c ' $' "$W/docs/concepts/workloads/controllers/job.md"
    sed -n '98,105p' "$W/docs/concepts/workloads/controllers/job.md"
    ```

**Expect**

Step 1 prints v1.35 twice and then hands you the validation rule in the server's own words. `kubectl
explain job.spec.managedBy` should repeat `job-v1.md:93` almost exactly, domain-prefixed path and
sixty-three characters and immutability included, which settles immediately that the rule is not a
website detail but part of the schema. `job.status.terminating` should still call itself beta-level
and still name `JobPodReplacementPolicy`. The two `kubernetes_feature_enabled` samples should both
report `1`; the label to read is `stage`, which should say `STABLE` for both, and the one that
matters is that the server exposes a gate for a field whose announcement never mentions one.

Step 2 is the measurement the post's sentence needs. `acme.io/foo` and
`kubernetes.io/job-controller` are accepted, and that second acceptance is the reserved case, not a
delegation. `foo` and `/foo` have no valid subdomain before the first slash and should be rejected;
so should `Example.com/foo` and `example_com/foo`, since RFC 1123 allows neither uppercase nor an
underscore. The sixty-three-character value should pass and the sixty-four-character one should
fail, which is the cap stated as an exact boundary rather than as a round number. Four cases the
prose does not settle are the interesting ones: `kubernetes.io/foo` and `k8s.io/foo` are
domain-prefixed paths under a domain the project owns, `example.com/` has nothing after the slash,
and the empty string is neither set nor a path. Read those four off the output rather than
predicting them; the point of the step is that the two sentences in the documentation predict all
sixteen the same way, and the server does not.

Step 3 creates three Jobs and then refuses four patches out of five. Adding the field to `runner`,
moving `reserved` off the reserved value, moving `sitter` between two custom values and clearing
`sitter` should all come back with an immutability error naming `spec.managedBy`; setting `sitter`
to the value it already carries should succeed silently, because no-op writes are not changes. The
`custom-columns` read before the patches is worth keeping: `reserved` shows the string in the
`MANAGEDBY` column and behaves like `runner`, which is the third case the concept page never states.

Step 4 is the answer the whole post rests on. The Pod list has Pods for `runner` and `reserved` and
none for `sitter`. `kubectl get jobs` shows completions for the first two and, for `sitter`, a
`COMPLETIONS` column that stays empty or shows `0/1` with no duration. The three `jsonpath` reads
should show real status objects for the first two and, for `sitter`, an empty object or nothing at
all — no `startTime`, no `active`, no conditions, no `uncountedTerminatedPods`. The event list has
`SuccessfulCreate` and `Completed` from `job-controller` for the other two and not one line naming
`sitter`; `kubectl describe` ends with `Events: <none>`. After the sleep, everything is identical.
That is what "skips reconciliation entirely" means, and it is stronger than `job.md:1315`'s "may not
be reconciled at all": the outcome is not uncertain. The `managedFields` read should name only
`kubectl-client-side-apply` or `kubectl-patch` — no controller has ever written to this object.

Step 5 takes a minute to produce nothing, which is the result. Ten seconds after creation a Job with
`activeDeadlineSeconds: 10` should have been failed with reason `DeadlineExceeded`, and five seconds
after that a Job with `ttlSecondsAfterFinished: 5` should have been deleted. Sixty seconds later
`deadline` is still listed, still has an empty status, and has four Pods fewer than its
`parallelism` asked for. Suspending `sitter` should add a `Suspended` condition and produce
`Suspended` and `Resumed` events, per `job.md:1074-1098`; the condition read should come back empty
and the event list should stay silent. Three fields, three separate controllers' worth of behaviour,
all of them accepted by validation and none of them implemented for this object. Nothing on either
page that mentions `managedBy` says this.

Step 6 separates a name from its three jobs. The Pod belonging to `tracked` should carry exactly one
finalizer, `batch.kubernetes.io/job-tracking`, which is `job.md:1222` demonstrated. The Job's own
annotations should not contain that string at all — the annotation `job.md:69` and `:102` still
print is not written by anything at the pin, exactly as `labels-annotations-taints/_index.md:1791`
says. Adding it by hand to `tracked` changes nothing, and adding it to `sitter` changes nothing
either: ten seconds later `sitter` still has no status, so the annotation does not wake the built-in
controller up. Then `squatter` is accepted with the reserved finalizer on it, because "reserved" is
a sentence in a note and not an admission rule; the delete leaves a `deletionTimestamp` and the Pod
stays; clearing the finalizer lets it go and the last command reports it not found. If you skip that
patch, the namespace will not delete in *Teardown*.

Step 7 turns the status columns on by hand. After the first write `kubectl get job sitter` should
show a duration counting from `$T0` and an active Pod that does not exist, which is the honest
picture of a mirror Job: the numbers are a report from somewhere else. After the second write the
Job reads as complete, `kubectl wait --for=condition=complete` returns immediately instead of timing
out, and the Pod count is still zero. Nothing was scheduled, nothing ran, and a client watching this
cluster cannot tell. That is the feature working, and it is also the reason the validation rules in
step 8 exist.

Step 8 is the conformance contract, enforced. `Complete` and `Failed` together, and `Complete` with
`FailureTarget`, should both be refused with a message close to `job-v1.md:161`'s wording.
`completionTime` without a `Complete` condition and a `completionTime` earlier than `startTime`
should both be refused, per `:157`. Clearing `startTime` on an unsuspended Job should be refused,
per `:177`. A negative `active` is plain field validation. The two counting cases — `succeeded`
above `completions` and `ready` above `active` — are the ones to read rather than predict: the table
states monotonicity for `succeeded` but never states a ceiling, so whichever way the server answers,
it is telling you something the documentation does not. The last two lines are the control: if the
same two writes are refused on `runner`, the rules are the Job API's and the post's framing of them
as the enabling work for `managedBy` is about why they were written, not about where they apply.

Step 9 shows the cost of a listener that never arrives. Three and a bit minutes in, the CronJob has
exactly one child, created on the first tick, and `.status.active` still holds it. `LAST SCHEDULE`
should keep moving while no new Job appears, and the event list should carry a repeated skip whose
message names the concurrency policy, with a `count` in the twos or threes. Deleting the child by
hand should let the next tick through, so after seventy seconds there is one Job again and the
CronJob is running normally — which proves the stop was the child and not the schedule. A CronJob
whose template delegates and whose delegate is absent runs exactly once, ever, and the only mention
of `managedBy` in the tree is a Job-page section that never mentions CronJob.

Step 10 is the census. `managedBy` should print exactly two lines from two files. `JobManagedBy`
should print two lines from one file, which are the feature-state marker and the sentence offering
it as a switch. `status validation` should count two, both of them in the post. The retired
reference path should appear in four places — the post, `job.md:1324`, `JobReadyPods.md:27` and the
2022 Job-tracking announcement — and once more in `_redirects.base`, which is the only reason any of
them resolve. `batch.kubernetes.io/job-tracking` should print seven lines across three files, the
third of them a metric help string. `kueue` should print `0`, and of the five named adopters only
`jobset` and `kubeflow` should return anything. The `sed` through the JobStatus table is worth
reading in full once: it is the validation contract, and it is shorter than the note that tells you
to go and read a KEP. The frontmatter reads give the two ladders side by side, one locked and one
not, and `job.md` should report eighteen lines with trailing whitespace, one of which is inside the
sample output the last command prints.

**Read on**

11. [The exercise that owns the other half of this
    page](../2024/09-pod-failure-policy-for-jobs-goes-ga.md), where `podFailurePolicy` reaches GA,
    the four actions are checked against the API, and a reason string the post invents turns out to
    be spelled a way nothing else in the tree spells it. Its `:181` is the line that hands
    `managedBy` to this exercise, and its subject is the machinery a delegated Job switches off.

12. [The exercise where a finalizer is the
    subject](../2021/03-using-finalizers-to-control-deletion.md) rather than an instrument, for what
    step 6's `squatter` is really demonstrating: what a finalizer does to a delete, the three
    cascade modes, and the two names the tree gives the same foreground finalizer.

13. [The exercise that owns the redirect file](02-endpoints-deprecation.md), for what
    `_redirects.base` is and what a line in it is holding up. The Job API reference is one of twenty
    pages that moved out of `workload-resources`, and four links in the tree — including the one
    this post gives and the one the concept page repeats — are still pointed at where it used to be.

14. [The exercise on the CronJob graduation](../2021/01-kubernetes-release-1-21-cronjob-ga.md), for
    the controller step 9 borrows: how it schedules, what it counts as active, and the gate behind
    it that was deleted for winning. Step 9 uses `concurrencyPolicy: Forbid` as a detector; that
    exercise is where the policy itself is established.

15. *Unanswerable from the pin.* The post says at `:40` that "a significant part of the effort was
    to introduce the extensive Job status validation rules" and links a KEP section for them. Six of
    those rules are in the tree, in the JobStatus table, and step 8 exercises eight writes against
    them — but whether six is the whole set, whether the rules apply only to Jobs with `managedBy`
    set, and what the KEP calls extensive are all outside the checkout. Nothing in `docs` names the
    rules as a group, states a count, or says which of them arrived with this feature. The step 8
    control writes against `runner` answer the second question for one cluster; the first and third
    cannot be answered from the pin at all.

**Teardown**

One namespace and one scratch directory. Nothing cluster-scoped is created, nothing is written to
the node, and the checkout at the pin is only read. The one thing that can wedge the delete is
`squatter`: if step 6's last patch did not run, the Pod still carries the reserved finalizer and the
namespace will sit in `Terminating` until it is cleared, so the first line below clears it whether
or not it is needed.

```sh
kubectl patch pod squatter -n bw-managedby --type=merge \
  -p '{"metadata":{"finalizers":null}}' 2>/dev/null || true
kubectl delete namespace bw-managedby
rm -rf /tmp/bw-managedby
```

The status subresource writes in steps 7 and 8 live on objects inside the namespace and go with it.
The CronJob is deleted at the end of step 9, but if you stopped partway it is in the namespace too.
If a later exercise on this cluster finds a Job called `sitter` reporting itself complete with no
Pods to its name, this is where it came from.
