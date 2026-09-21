<a id="kubescape-validating-admission-policy-library"></a>

# All three manifests are written at an API version that no longer exists, the binding names a policy the post's own YAML never creates, and the cost the authors predicted for themselves — grouping three expressions into one object — is the one thing the pinned tree still proves

**Post** — [Kubernetes Validating Admission Policies: A Practical Example](https://kubernetes.io/blog/2023/03/30/kubescape-validating-admission-policy-library/),
2023-03-30.

12,890 bytes over 236 lines, by Craig Box (ARMO) and Ben Hirschberg (ARMO), fourteenth of the year's
seventy-eight posts by size. It is a guest post: two maintainers of a CNCF security scanner
describing what happened when they ported their rule library from one policy language to another,
three months after the mechanism they ported it to went alpha.

**As written**

The case against admission webhooks is made first, in three sentences at `:23-28`: a webhook is
production infrastructure you have to run, its failure mode is a choice between refusing writes and
not enforcing the policy, and the network hop is charged to every matching request. Validating
admission policies are offered at `:30-42` as the compromise — CEL expressions evaluated inside the
API server, alpha in v1.26 — with a note that CEL reached Kubernetes first as CRD validation rules
in v1.23.

The body of the post is one worked example. Kubescape's controls are written in Rego (`:44-55`); the
team ported them to CEL and published a library (`:63-66`); control C-0017, which requires every
container to run with a read-only root filesystem, is the one the post prints. The post is careful
to say at `:68-73` that this is a best practice from the NSA hardening guidance and *"is not
currently required as a part of any of the pod security standards"*.

The policy itself is at `:77-105`. Its `matchConstraints` name three API groups — core `v1` for
pods, `apps/v1` for the four workload controllers, `batch/v1` for jobs and cronjobs (`:107-108`) —
and a note at `:110-115` explains that `matchConstraints` converts the object to the matched
version, so a rule written against `apps/v1` cannot be evaded by submitting `apps/v1beta1`. Its
`validations` hold three expressions, one per place a pod spec can sit: at the root of the object,
under `template`, or under `jobTemplate` (`:117-123`).

Then a note the authors wrote against themselves, at `:125-130`. The three expressions are grouped
into one policy object so that they can be enabled and disabled atomically, and the post says
plainly what that costs: *"Breaking them into separate policies would allow us access to
improvements targeted for the 1.27 release, including type checking."* They say they are talking to
SIG API Machinery about it before the APIs reach `v1`.

The rest is operational. A `minikube start` line at `:142` turns on both switches the feature needed
— the `ValidatingAdmissionPolicy` feature gate and the `admissionregistration.k8s.io/v1alpha1` group
version. Three `kubectl apply` lines at `:147-153` install the library from a release URL. A binding
at `:161-172` scopes control C-0017 to namespaces labelled `policy=enforced`, a namespace is created
and labelled at `:174-177`, and `:182-185` runs the command that is supposed to fail. The refusal is
printed at `:189-191`. A second binding at `:204-217` shows how a policy reads its configuration
from a separate object through `paramRef`. The summary at `:219-236` says the feature is alpha, not
production-ready, and that the authors look forward to beta and GA.

**As it runs now**

The feature gate is gone. `ValidatingAdmissionPolicy` went alpha in v1.26, beta in v1.28, stable in
v1.30, and its file records `removed: true` — CEL admission is not something you can turn off at the
pin, and the `--feature-gates` half of the post's `minikube` line at `:142` names a gate the API
server will not accept.

The API version is gone too, and it is named in four separate places: the policy at `:78`, both
bindings at `:162` and `:205`, and the `--runtime-config` half of `:142`. In the whole of `docs/`
only two occurrences of `admissionregistration.k8s.io/v1alpha1` survive — against 124 of
`admissionregistration.k8s.io/v1`, counting the literal string where the next character is not part
of a longer version name — and both survivors are stale prose rather than live API — they are read
in [the 2018 admission exercise](../2018/01-extensible-admission-is-beta.md), which found them.

The binding grew two required fields the post's bindings do not carry.
`validating-admission-policy.md:93-94` says each binding *"must specify one or more
`validationActions`"*; neither binding in this post has one, and neither does either binding in the
December 2022 alpha announcement, which is how you can tell the field was not required when this was
written rather than that the authors dropped it. `paramRef` grew `parameterNotFoundAction`, and the
post's `paramRef` at `:211-212` carries only a name.

And the pinned tree disagrees with itself about that second field. `:274` lists
`parameterNotFoundAction` as **(Required)**. Nine lines later `:283` repeats *"the
`parameterNotFoundAction` field in `paramRef` is **required**"* and then, in the same sentence,
describes what happens when it is absent: *"If not specified, the policy binding may be considered
invalid and will be ignored or could lead to unexpected behavior."* A field the API server requires
cannot be absent from a stored object, so at most one of those two halves is describing this
cluster; and `:291-293` narrows the field's purpose again, to the case where `paramRef` uses a
selector, while `:280` allows a plain `name`. Step 9 asks the server which it is.

**What this exercise does not cover, and where it lives**

The ValidatingAdmissionPolicy apparatus itself — a policy, a binding, a replica count refused with
no webhook server anywhere — is built in [the 2018 admission
exercise](../2018/01-extensible-admission-is-beta.md), which also walks both stale `v1alpha1`
survivors and the admission-controller list they sit in. The three `validationActions` and what each
one does to the same evaluation belong to [the policy
lab](../../labs/03/16-a-policy-with-no-webhook.md) and, for the `Warn` action's history, [the 2020
warnings exercise](../2020/07-warnings.md). CEL's other Kubernetes home, `x-kubernetes-validations`
on a CRD, is [the 2022 validation-rules exercise](../2022/09-crd-validation-rules-beta.md). Where
`readOnlyRootFilesystem` goes in a pod spec, and the post that put it in the wrong place, is [the
2016 hardening exercise](../2016/08-security-best-practices-kubernetes-deployment.md). This exercise
runs the manifests this post prints, and nothing else.

**The diff, and why**

**The copy-and-paste path was broken on publication day, and not by time.** The policy at `:81` is
named `kubescape-c-0017-deny-resources-with-mutable-container-filesystem`. The binding at `:167`
names `kubescape-c-0017-deny-mutable-container-filesystem`, and the refusal printed at `:190` quotes
that second, shorter name. A reader who applies what the post prints, in the order the post prints
it, ends up with a policy nobody binds and a binding that points at nothing. The post does not
notice, because its own worked example is not running against the YAML it printed: `:147-153`
downloads the library, and the name at `:167` is the library's. Everything in the post is internally
consistent except the one manifest a reader would actually copy.

**The policy broke by version, not by meaning.** Substitute `v1` for `v1alpha1` in the policy and
the server takes it unaltered: every field name, all three `resourceRules` entries and all three CEL
expressions survived alpha to stable without an edit. That is a strong result for a manifest written
against a three-month-old alpha API, and it is worth stating separately from the two bindings, which
need new fields as well as a new version.

**The authors' own prediction is the part the pin proves.** `:125-130` said grouping the three
expressions into one object would cost them type checking. At the pin, type checking exists, runs
when the policy is written, and reports per matched type (`validating-admission-policy.md:474-482`,
`:501-507`). Apply this policy and the server hands you the bill in `status.typeChecking`: the first
expression is typed against the six non-pod kinds this policy matches, the second against the pod
kind, and each mismatch is listed by group and kind. The policy still works — `:529-530` says type
checking never changes behaviour — so what you are reading is exactly the diagnostic the authors
said they had chosen to forgo.

**Still right, and never absorbed, which are two findings and not one.** The claim at `:72-73` that
a read-only root filesystem is required by no pod security standard is still true at the pin:
`readOnlyRootFilesystem` does not appear in `pod-security-standards.md` at all. And the shape the
post uses to handle that gap — one policy, three expressions, dispatching on `object.kind` to reach
the pod spec wherever it sits — has no counterpart anywhere in the pinned documentation. The one
example in the tree that names more than one kind, `typechecking-multiple-match.yaml`, matches two
kinds with the same spec shape and is deliberately wrong, because its job is to produce a type
error; the one that spans groups, `validating-admission-policy-match-conditions.yaml`, does it with
`["*"]`, which `:525-526` excludes from type checking altogether. Naming *still right* on its own
would tell a reader they can move on from a post that is still the only worked example of the thing.

The gate that carried all of this has been deleted, and its whole life fits in six releases.

`ValidatingAdmissionPolicy`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.26 – v1.27 |
| beta | `false` | — | v1.28 – v1.29 |
| stable | `true` | — | v1.30 – v1.31 |

The file carries `removed: true` and no `locked` key. The beta row is the one to look at twice: a
default of `false` at beta means that when this post's authors wrote *"We look forward to watching
it move to Beta"* at `:229`, beta did not mean on. Two more releases passed before the feature was
reachable without a flag.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), fresh. One node is enough: every
refusal here happens in the API server, and the two pods that do get created are `pause` containers
that exist only to prove the controller-created ones were admitted too. Bring the guest up with [the
five provision steps](../../strands/lab-topologies.md#provision), install Kubernetes with [the node
baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), then `ssh
zain@10.10.10.180`. Steps 1 to 9 need the cluster; step 10 needs only the pinned tree.

**Do**

1. Establish the two things the post had to arrange and you cannot. The gate first, then the group
   versions the API server serves, then the absence of any webhook at all — the last is the baseline
   the census asks this exercise to prove.

   ```sh
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' | grep -i validatingadmissionpolicy \
     || echo "no gate by that name"
   kubectl api-versions | grep '^admissionregistration'
   kubectl get validatingwebhookconfigurations,mutatingwebhookconfigurations
   ```

2. Write the post's policy to a file exactly as printed at `:77-105`, `v1alpha1` and all, and apply
   it.

   ```sh
   cat > /tmp/c0017.yaml <<'YAML'
   apiVersion: admissionregistration.k8s.io/v1alpha1
   kind: ValidatingAdmissionPolicy
   metadata:
     name: "kubescape-c-0017-deny-resources-with-mutable-container-filesystem"
   spec:
     failurePolicy: Fail
     matchConstraints:
       resourceRules:
       - apiGroups:   [""]
         apiVersions: ["v1"]
         operations:  ["CREATE", "UPDATE"]
         resources:   ["pods"]
       - apiGroups:   ["apps"]
         apiVersions: ["v1"]
         operations:  ["CREATE", "UPDATE"]
         resources:   ["deployments","replicasets","daemonsets","statefulsets"]
       - apiGroups:   ["batch"]
         apiVersions: ["v1"]
         operations:  ["CREATE", "UPDATE"]
         resources:   ["jobs","cronjobs"]
     validations:
       - expression: "object.kind != 'Pod' || object.spec.containers.all(container, has(container.securityContext) && has(container.securityContext.readOnlyRootFilesystem) &&  container.securityContext.readOnlyRootFilesystem == true)"
         message: "Pods having containers with mutable filesystem not allowed! (see more at https://hub.armosec.io/docs/c-0017)"
       - expression: "['Deployment','ReplicaSet','DaemonSet','StatefulSet','Job'].all(kind, object.kind != kind) || object.spec.template.spec.containers.all(container, has(container.securityContext) && has(container.securityContext.readOnlyRootFilesystem) &&  container.securityContext.readOnlyRootFilesystem == true)"
         message: "Workloads having containers with mutable filesystem not allowed! (see more at https://hub.armosec.io/docs/c-0017)"
       - expression: "object.kind != 'CronJob' || object.spec.jobTemplate.spec.template.spec.containers.all(container, has(container.securityContext) && has(container.securityContext.readOnlyRootFilesystem) &&  container.securityContext.readOnlyRootFilesystem == true)"
         message: "CronJob having containers with mutable filesystem not allowed! (see more at https://hub.armosec.io/docs/c-0017)"
   YAML
   kubectl apply -f /tmp/c0017.yaml
   ```

3. Change one string — the API version — and apply the same file again. Then read what the server
   wrote back into the object's status.

   ```sh
   sed -i 's|admissionregistration.k8s.io/v1alpha1|admissionregistration.k8s.io/v1|' /tmp/c0017.yaml
   kubectl apply -f /tmp/c0017.yaml
   kubectl get validatingadmissionpolicy \
     kubescape-c-0017-deny-resources-with-mutable-container-filesystem \
     -o yaml | sed -n '/^status:/,$p'
   ```

   This is the bill from `:125-130`. Read it before going on: which expression index each warning is
   filed under, which group and kind it was typed against, and which field CEL says is undefined.

4. Count what the policy matches, and put the count beside the limit the pinned page sets.

   ```sh
   kubectl get validatingadmissionpolicy \
     kubescape-c-0017-deny-resources-with-mutable-container-filesystem \
     -o jsonpath='{range .spec.matchConstraints.resourceRules[*]}{.apiGroups}{" -> "}{.resources}{"\n"}{end}'
   ```

   `validating-admission-policy.md:527-528` caps type checking at ten matched combinations and says
   the eleventh onward are ignored in ascending group, version and resource order. Work out how many
   combinations these three rules produce, and decide whether this policy would have been fully
   checked.

5. Apply the post's binding from `:161-172`, changed only in its API version, then create and label
   the namespace exactly as `:174-177` does, then run the command at `:184` that the post says will
   fail.

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: admissionregistration.k8s.io/v1
   kind: ValidatingAdmissionPolicyBinding
   metadata:
     name: c0017-binding
   spec:
     policyName: kubescape-c-0017-deny-mutable-container-filesystem
     matchResources:
       namespaceSelector:
         matchLabels:
           policy: enforced
   YAML
   ```

   If that is refused, add the field the server names and apply again, then carry on. The namespace,
   the label and the pod are the post's own three lines.

   ```sh
   kubectl create namespace policy-example
   kubectl label namespace policy-example 'policy=enforced'
   kubectl -n policy-example run nginx --image=nginx --restart=Never
   ```

6. Ask the two objects what they are called, and make them agree.

   ```sh
   kubectl -n policy-example delete pod nginx --ignore-not-found
   kubectl get validatingadmissionpolicy -o name
   kubectl get validatingadmissionpolicybinding c0017-binding -o jsonpath='{.spec.policyName}{"\n"}'
   kubectl patch validatingadmissionpolicybinding c0017-binding --type=merge \
     -p '{"spec":{"policyName":"kubescape-c-0017-deny-resources-with-mutable-container-filesystem"}}'
   kubectl -n policy-example run nginx --image=nginx --restart=Never
   ```

   Compare the refusal string you get with the one the post prints at `:190`, word for word,
   including which name appears between the single quotes.

7. Now the two expressions a pod never reaches. A Deployment carries its containers under
   `template`, a CronJob under `jobTemplate`, and the post wrote one expression for each.

   ```sh
   kubectl -n policy-example create deployment web --image=registry.k8s.io/pause:3.10
   kubectl -n policy-example create cronjob tick --image=registry.k8s.io/pause:3.10 \
     --schedule='*/5 * * * *' -- /pause
   kubectl -n policy-example apply -f - <<'YAML'
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: web
   spec:
     replicas: 1
     selector:
       matchLabels: {app: web}
     template:
       metadata:
         labels: {app: web}
       spec:
         containers:
         - name: pause
           image: registry.k8s.io/pause:3.10
           securityContext:
             readOnlyRootFilesystem: true
   YAML
   kubectl -n policy-example get pods
   kubectl get validatingwebhookconfigurations,mutatingwebhookconfigurations
   ```

8. The whole policy dispatches on `object.kind`, so find out what that actually holds. Write a
   second policy that always fails, give it a message expression that prints the two properties
   `validating-admission-policy.md:352-353` guarantees, and bind it with `Warn` in a namespace of
   its own so nothing is refused.

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: admissionregistration.k8s.io/v1
   kind: ValidatingAdmissionPolicy
   metadata:
     name: report-typemeta
   spec:
     failurePolicy: Fail
     matchConstraints:
       resourceRules:
       - apiGroups:   [""]
         apiVersions: ["v1"]
         operations:  ["CREATE"]
         resources:   ["pods"]
       - apiGroups:   ["apps"]
         apiVersions: ["v1"]
         operations:  ["CREATE"]
         resources:   ["deployments"]
     validations:
       - expression: "false"
         message: "typemeta probe"
         messageExpression: "'kind=[' + object.kind + '] apiVersion=[' + object.apiVersion + ']'"
   ---
   apiVersion: admissionregistration.k8s.io/v1
   kind: ValidatingAdmissionPolicyBinding
   metadata:
     name: probe-binding
   spec:
     policyName: report-typemeta
     validationActions: [Warn]
     matchResources:
       namespaceSelector:
         matchLabels:
           policy: probe
   YAML
   kubectl create namespace probe
   kubectl label namespace probe 'policy=probe'
   kubectl -n probe run one --image=registry.k8s.io/pause:3.10 --restart=Never
   kubectl -n probe create deployment two --image=registry.k8s.io/pause:3.10
   ```

9. Settle the disagreement from *As it runs now*. A policy that takes a parameter, then the same
   binding twice, differing in one field.

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: admissionregistration.k8s.io/v1
   kind: ValidatingAdmissionPolicy
   metadata:
     name: param-probe
   spec:
     failurePolicy: Fail
     paramKind:
       apiVersion: v1
       kind: ConfigMap
     matchConstraints:
       resourceRules:
       - apiGroups:   [""]
         apiVersions: ["v1"]
         operations:  ["CREATE"]
         resources:   ["configmaps"]
     validations:
       - expression: "true"
         message: "never fires"
   YAML
   kubectl apply -f - <<'YAML'
   apiVersion: admissionregistration.k8s.io/v1
   kind: ValidatingAdmissionPolicyBinding
   metadata:
     name: param-probe-binding
   spec:
     policyName: param-probe
     validationActions: [Deny]
     paramRef:
       name: basic-control-configuration
       namespace: default
     matchResources:
       namespaceSelector:
         matchLabels:
           policy: probe
   YAML
   ```

   Whatever the server says, apply it again with `parameterNotFoundAction: Deny` added under
   `paramRef` and compare. One of the two claims at `:274` and `:283` describes your cluster and the
   other does not; write down which, and which sentence you would delete.

10. Offline, from the pinned tree. Four checks, in the order the exercise made them.

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -c readOnlyRootFilesystem docs/concepts/security/pod-security-standards.md || echo "zero"
    grep -rln 'admissionregistration.k8s.io/v1alpha1' docs --include='*.md'
    grep -c validationActions blog/_posts/2022/validating-admission-policies-alpha/index.md || echo "zero"
    sed -n '523,531p' docs/reference/access-authn-authz/validating-admission-policy.md
    cat docs/reference/command-line-tools-reference/feature-gates/ValidatingAdmissionPolicy.md
    ```

**Expect**

Step 1 prints nothing for the gate, because a removed gate is not exported: the `|| echo` branch
fires. `kubectl api-versions` shows which `admissionregistration.k8s.io` versions this server still
serves — record the list rather than predicting it: the two versions this post needs are not the
only ones the group has ever served. Both webhook configuration lists are empty, and they stay empty
for the whole exercise. That is the census's claim in one line: everything that follows is enforced
by the API server process.

Step 2 is refused. The server has no `ValidatingAdmissionPolicy` kind at
`admissionregistration.k8s.io/v1alpha1`, and that refusal is the only thing the four places naming
it have in common.

Step 3 creates the policy — one substituted string and every other line of the post's YAML accepted
unchanged, three years and five months on. The `status` block is the finding. Expect
`typeChecking.expressionWarnings` with an entry for each of `spec.validations[0]`,
`spec.validations[1]` and `spec.validations[2]`, each warning naming several group-kind pairs,
because `:501-507` checks an expression against every type the policy matches. The first expression
reads `object.spec.containers`, which only a Pod has, so it is typed against Deployment, ReplicaSet,
DaemonSet, StatefulSet, Job and CronJob and found undefined in all six. The second reads
`object.spec.template`, which neither a Pod nor a CronJob has. The third reads
`object.spec.jobTemplate`, which only a CronJob has, so it fails against the other six. Every
expression in this policy is undefined for most of what the policy matches, and every one of them is
still correct at run time, because CEL's `||` short-circuits before the undefined field is touched —
and type checking is not run time, which is the distinction `:529-530` draws when it says type
checking does not affect behaviour in any way. This is the exact diagnostic `:125-130` chose to give
up.

Step 4 prints three lines and they sum to seven combinations: one core group with `pods`, the `apps`
group with four resources, the `batch` group with two. Seven is under the limit of ten, so the
policy was checked in full — but the margin is three, and naming a second `apiVersions` entry on any
one of the three rules would have spent it. The limitation at `:527-528` is silent when it fires,
which means a policy can be under-checked without anything saying so.

Step 5's binding is refused if `validationActions` is required, and the message names the field. Add
`validationActions: [Deny]` and it is created. Then the namespace and the label go in, and the
post's last line — the one at `:184` that `:179-180` promises will fail — creates the pod. Nothing
is enforcing anything. The binding exists, the policy exists, the namespace carries the label the
binding selects, and the two objects have never referred to each other. If your server accepts the
binding without `validationActions`, that is the finding instead, and `:93-94` is prose the API does
not enforce; say which happened.

Step 6 prints the two names side by side and they differ by the word `resources`. After the patch
the same `kubectl run` is refused, and the message is the post's message text with the policy's real
name in the quotes. The post's `:190` shows the short name. Both refusals are real; they come from
different objects, and only one of those objects is in the post.

Step 7: both `create` commands are refused, the Deployment by the second expression and the CronJob
by the third, each with its own message. The applied Deployment is admitted, and so are the pods the
ReplicaSet controller creates from it — which is worth watching, because those pods are submitted by
a controller and not by you, and the policy matched them on their namespace, not on their author.
The two webhook lists are still empty.

Step 8 produces a `Warning:` line on both creates, and that line is the answer. If it reads
`kind=[Pod]` and `kind=[Deployment]`, `object.kind` is populated and every dispatch in the post's
policy works as written. If either bracket is empty, the first expression's `object.kind != 'Pod'`
is true for everything and the pod rule enforces nothing at all. `:352-353` says CEL guarantees
access to `apiVersion`, `kind`, `metadata.name` and `metadata.generateName` for any Kubernetes
object; guaranteed access and a populated value are different claims, and only one of them is
written down.

Step 9 gives you one of two outcomes and both are publishable. Either the binding without
`parameterNotFoundAction` is refused, in which case `:274` is right, the field is required, and
`:283`'s clause about what happens *"if not specified"* describes a state the API server will not
store; or it is accepted, in which case `:283`'s clause is the accurate half and the *(Required)*
marker at `:274` is wrong. The post's own `paramRef` at `:211-212` is the manifest under test: it
has a `name` and nothing else.

Step 10, in order: `readOnlyRootFilesystem` does not occur in `pod-security-standards.md`, so the
claim at `:72-73` has survived three years and five months unamended. Two files in `docs` still
carry `admissionregistration.k8s.io/v1alpha1`. `validationActions` does not occur in the December
2022 alpha announcement either, which is the evidence that this post's bindings were complete when
they were written. And the gate file is twenty-four lines with `removed: true` near the bottom — the
whole life of the mechanism this post is a practical example of, in six releases.

**Read on**

1. `validating-admission-policy.md:474-531` — type checking end to end, including the three
   limitations. `:523-531` is the part to read twice: no wildcard matching, a cap of ten matched
   types, and no effect on behaviour.

2. The December 2022 alpha announcement,
   `blog/_posts/2022/validating-admission-policies-alpha/index.md`, in full. It is the post this one
   is the practical example of. Its 161 lines carry four manifests, and they are the control group
   for every version and field difference found here.

3. `validating-admission-policy.md:569-606` — the kinds no policy can validate, and why. Policies
   and bindings exempt themselves to avoid a lock-out, six virtual authentication and authorization
   kinds are exempt from everything, and `:604-606` records that admission webhooks only started
   excluding those six by default in v1.37.

4. `kubernetes-1.26-blog.md:180-187` — the release note that put both switches in one sentence. It
   is the shortest statement in the tree of what this post's `minikube` line was for.

5. *Unanswerable from the pin:* whether the two names at `:81` and `:167` ever agreed. The library
   is fetched from a release URL at `:147-153`, outside the pinned tree, so nothing here can say
   whether a policy called `kubescape-c-0017-deny-mutable-container-filesystem` exists in it — only
   that the post never prints one.

**Teardown** — `kubectl delete ns policy-example probe; kubectl delete
validatingadmissionpolicybinding c0017-binding probe-binding param-probe-binding; kubectl delete
validatingadmissionpolicy kubescape-c-0017-deny-resources-with-mutable-container-filesystem
report-typemeta param-probe; rm -f /tmp/c0017.yaml`. Delete the bindings before the policies: a
binding left pointing at a deleted policy is legal and silently does nothing, which is the state
step 5 arrived at by accident. Then [tear the guest down](../../strands/lab-topologies.md#teardown).
