<a id="validating-admission-policy-ga"></a>

# The only Go source file in the whole blog archive dereferences a pointer it has just finished proving is nil, the post never once sends the input that would reveal that, and the loose end its own narrative leaves behind is settled only by the monitoring appendix at the bottom

**Post** — [Kubernetes 1.30: Validating Admission Policy Is Generally Available](https://kubernetes.io/blog/2024/04/24/validating-admission-policy-ga/),
2024-04-24.

13,509 bytes, 287 lines, one author: Jiahui Feng of Google. Sixteenth of 2024's 54 posts by size,
2,741 bytes above the year's mean of 10,768. It is a directory bundle with exactly one companion
file, `webhook.go` at 2,819 bytes — the only Go source file among the 245 non-markdown files in the
whole `blog/_posts` tree, which is otherwise 137 PNGs, 85 SVGs, 15 JPEGs and a scattering of diagram
and YAML sources. It is also the only one of the tree's 765 post files whose frontmatter opens with
six hyphens instead of three, at `:1`. Six `##` sections, ten fenced blocks, and one relative link
to a file the reader is expected to compile.

**As written**

The frame is set at `:10-18`: ValidatingAdmissionPolicy has reached general availability in v1.30,
the reader is pointed back at the December 2022 alpha post, and the demonstration is announced as a
replacement — "let's have a taste of a ValidatingAdmissionPolicy, by replacing a simple webhook."
Everything that follows is that one substitution, carried out step by step.

`:20-52` is the webhook being replaced. A 24-line Go function, `verifyDeployment`, walks a
Deployment's containers and appends an error for each of four `securityContext` fields set to
anything but the least permissive value: `runAsNonRoot`, `readOnlyRootFilesystem`,
`allowPrivilegeEscalation`, `privileged`. `:52` offers "the full code of this webhook to follow
along with this walkthrough" as a relative link to `webhook.go`, and the excerpt is byte-identical
to that file's own `:16-39`.

`:54-125` is the policy, twice. The first version at `:56-78` matches `apps/v1` Deployments on
CREATE and UPDATE with `failurePolicy: Fail` and four CEL expressions, each pairing a `has()` guard
with a field read. `:79` creates it — "Great, no complain so far" — and then `:80-96` reads
`status.typeChecking` back and finds one warning: `spec.validations[3].expression` accessed an
undefined field `Privileged`. `:97-100` reads the warning correctly, names the matched type as
`apps/v1.Deployment`, notes that indexing starts at zero, and diagnoses a copy-and-paste error.
`:102-124` is the same policy with `privileged` in lowercase, and `:125` says the warnings clear.

`:127-180` runs both enforcers at once. A namespace `policy-test`, a binding with
`validationActions: ["Warn"]` selected by the namespace's own `kubernetes.io/metadata.name` label,
and a Deployment with one nginx container that sets `privileged: true` and
`allowPrivilegeEscalation: true` and nothing else. The output at `:173-179` is five lines: four
`Warning:` lines from the policy, one per expression, and then an `Error from server` line from the
webhook naming all four failures at once. `:180` draws the conclusion — "the policy and the webhook
give equivalent results."

`:181-267` is the cleanup. Two complaints at `:183-184`: every expression repeats the walk to
`object.spec.template.spec.containers` and each `securityContext`, and the presence-then-access
pattern is verbose. `:186-188` names the two features that fix them, both from v1.28 — variable
composition, and CEL's optional library. `:191-218` is the refactor: two variables, `containers` and
`securityContexts`, the latter built with `map(c, c.?securityContext)`, and four validations that
compare optionals with `optional.of(true)`. `:222-235` flips the binding to `Deny`, `:236-265`
removes the webhook and re-sends the same Deployment, and the output is now a single line.
`:266-267` explains why: by design a policy stops evaluating after the first expression that denies,
which is different from what happens when the expressions only warn.

`:269-287` is a monitoring appendix. A policy is not a process, so it has no metrics of its own; use
the API server's. Two PromQL examples follow — a 95th-percentile of
`apiserver_validating_admission_policy_check_duration_seconds_bucket` filtered by `policy`, and a
rate of `apiserver_validating_admission_policy_check_total` filtered the same way. `:286-287` is the
post's only forecast: the metrics "are currently in alpha, and more and better metrics will come
while the stability graduates in the future release."

**As it runs now**

Four things have moved, and the fourth is not a behaviour.

**The metrics graduated, and the rest of that sentence did not.** `:286-287` predicted two things.
The first happened: `docs/reference/instrumentation/metrics.md:385-397` lists both
`apiserver_validating_admission_policy_check_duration_seconds` and
`apiserver_validating_admission_policy_check_total` at stability level BETA. The second did not. Two
years and seven releases past the post, there are still exactly two metrics for this feature, with
the same names and the same four labels — `enforcement_action`, `error_type`, `policy`,
`policy_binding` — so both of the post's PromQL examples still run verbatim. What "more and better
metrics" actually produced is a mirrored pair at `:1407-1414` for a feature that did not exist when
this post was written. Step 9 reads the labels.

**The two cleanup features became a documented section with semantics the post does not state.**
`:186-188` introduces variable composition and the optional library as conveniences. At the pin,
`docs/reference/access-authn-authz/validating-admission-policy.md:533-567` opens a variable
composition section that adds four properties the refactored policy silently depends on: a variable
is lazily evaluated when first referred to (`:548`), both its result and its error are memoised and
count once towards runtime cost (`:549-550`), order matters because a variable may refer only to
variables defined before it, and that ordering is what prevents circular references (`:552-553`).
The post's `securityContexts` variable is built from its `containers` variable, so it relies on all
four. Step 8 tests the ordering rule directly.

**The warning the post fixes and walks past is explicitly non-binding.** `:79` reports no complaint
when the broken policy is created, and `:125` reports the warnings cleared once it is fixed; between
the two the post never binds the broken version, so it never has to say what a live expression with
an undefined field does. The pin says who decides: `validating-admission-policy.md:529-530` — type
checking does not affect policy behaviour in any way, the policy continues to evaluate, and if
errors occur during evaluation the failure policy decides the outcome. With `failurePolicy: Fail` at
`:62`, that sentence has consequences the post's narrative never reaches. Steps 4 and 5 reach them.

**The reference page disagrees with itself about whether a bad expression is rejected.**
`validating-admission-policy.md:476-477` says that when a policy definition is created or updated
the validation process parses its expressions and reports any syntax errors, "rejecting the
definition if any errors are found". Fifty lines later `:529-530` says type checking does not affect
the policy behaviour in any way and that even if it detects errors the policy will continue to
evaluate. Read `:476-479` alone and an undefined field is a rejection; read `:529-530` alone and it
is a warning and nothing more. The seam is at `:478`, where the sentence switches from syntax errors
to type errors without saying that the first sentence's "rejecting" stops applying. Cite both
halves. Step 4 settles it, by creating exactly the policy the post creates at `:79`.

**What this exercise does not cover, and where it lives**

The `ValidatingAdmissionPolicy` feature gate and its whole six-release life are laddered in [the
2023 policy-library exercise](../2023/02-kubescape-validating-admission-policy-library.md), which
also owns type checking read as a per-matched-type diagnostic across many kinds. The apparatus
itself — a policy, a binding, and a refusal with no webhook server anywhere — is built in [the 2018
admission exercise](../2018/01-extensible-admission-is-beta.md). The three `validationActions` and
what each does to one evaluation belong to [the policy
lab](../../labs/03/16-a-policy-with-no-webhook.md), and the `Warn` action's own history to [the 2020
warnings exercise](../2020/07-warnings.md). CEL on a CRD is [the 2022 validation-rules
exercise](../2022/09-crd-validation-rules-beta.md).

Webhook plumbing as a subject — a CA, a serving certificate, the SANs the API server checks, what a
corrupt `caBundle` does — is the build track's, in [the certificate
exercise](../../labs/03/17-a-ca-and-a-serving-cert-by-hand.md) and [the webhook the apiserver
dials](../../labs/03/18-the-webhook-the-apiserver-dials.md), and the four-way comparison of a policy
against a webhook of identical semantics is [the comparison
exercise](../../labs/03/20-the-same-rejection-twice.md). This exercise builds a webhook only because
the post ships one, runs only the code the post ships, and asks only the question the post's own
walkthrough leaves open.

**The diff, and why**

***Wrong when it was published.*** The webhook the post offers as the thing being replaced cannot
handle a container without a `securityContext`. `:31-33` appends the error "container %q does not
have SecurityContext" when `c.SecurityContext` is nil, and then `:34` — the very next statement,
with no `continue` between them — reads `c.SecurityContext.RunAsNonRoot`. That is a nil pointer
dereference on the exact input the branch above it has just finished identifying. The policy beside
it has no such hole: every expression at `:70-77` opens with `has(c.securityContext)` and short
circuits. So `:180`'s claim that "the policy and the webhook give equivalent results" is false, and
it is false in the direction that matters — the webhook is the fragile one. The post never finds
out, because the only Deployment it ever sends, at `:149-171`, sets a `securityContext`. One input
the post does not try separates the two enforcers completely, and step 3 sends it.

***Wrong when it was published***, a second time and for a different reason. `:52` tells the reader
to use the full code "to follow along with this walkthrough", and `:236` tells them to "remove the
webhook". Following along requires installing one. The post prints no
`ValidatingWebhookConfiguration`, no certificate, no Service and no container image, and
`webhook.go` supplies only three flags — `-addr`, `-cert`, `-key`, at its own `:84-86`. Yet the
rejection at `:178` is attributed to `admission webhook "webhook.example.com"`, so a registered
webhook was certainly running when the screenshot was taken. The walkthrough is not reproducible as
printed, and the missing piece is the half the post spends its first section on. Step 2 writes it.

***Retired by being agreed with.*** The GA this post announces held: the gate reached stable in
v1.30, and the 2023 exercise's ladder shows it deleted two releases later, which is what happens to
a gate that has nothing left to switch. The metrics' stability graduated exactly as `:286` hoped.
And the two features `:186-188` recommends in passing are now a reference section with stated
semantics. A post is retired by agreement when the project does the thing; three separate promises
in this one were kept.

***Overtaken by stasis.*** "More and better metrics will come while the stability graduates in the
future release" is half a forecast and half a wish, and only the half about stability came true. At
the pin there are the same two series, the same four labels, and nothing else — no per-expression
counter, no evaluation-error series distinct from the `error_type` label, nothing that would let an
operator tell a denied request from an errored one without parsing labels. That matters here
specifically: the only instrument that answers the question this post leaves open in step 5 is the
`error_type` label on a metric the post calls alpha and treats as an afterthought.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180` running Kubernetes v1.35,
provisioned with [the standard steps](../../strands/lab-topologies.md#provision) and [the node
baseline](../../strands/lab-topologies.md#node-baseline-steps). One node is enough and is also
necessary: the webhook runs as a plain process on the same host as the API server, registered by
`clientConfig.url` rather than a Service, so nothing here needs a second machine or a working CNI
path to a Pod. Go is needed on the node, once, to build the post's file. All cluster work happens in
a namespace called `bw-vap`, and all host state under `/var/tmp/bw-vap`.

**Do**

1. Ground the node and put a Go toolchain on it. Record the server version, because every claim in
   this exercise is about a feature that went GA five minor releases ago and has not moved since.

   ```sh
   ssh zain@10.10.10.180
   kubectl version -o json | jq -r '.serverVersion.gitVersion'
   sudo apt-get update && sudo apt-get install -y golang-go openssl
   go version
   kubectl taint node --all node-role.kubernetes.io/control-plane- 2>/dev/null || true
   kubectl create namespace bw-vap
   kubectl label namespace bw-vap bw=vap
   mkdir -p /var/tmp/bw-vap && cd /var/tmp/bw-vap
   ```

2. Build and register the half the post left out. Copy `webhook.go` from the pinned tree unchanged —
   do not fix anything in it — give it a module, a self-signed certificate naming the node's own
   address, and the `ValidatingWebhookConfiguration` the post never prints. Keep the server in the
   foreground in one terminal; open a second for everything that follows.

   ```sh
   cd /var/tmp/bw-vap
   # copy webhook.go from the pinned checkout, byte for byte, then:
   go mod init bwvap
   go get k8s.io/api@v0.35.0 k8s.io/apimachinery@v0.35.0
   go mod tidy
   openssl req -x509 -newkey rsa:2048 -nodes -days 30 \
     -keyout key.pem -out cert.pem -subj '/CN=bw-vap-webhook' \
     -addext 'subjectAltName=IP:10.10.10.180'
   go run . --addr 10.10.10.180:8443 --cert cert.pem --key key.pem
   ```

   In the second terminal, register it against the namespace and nothing else:

   ```sh
   tee /var/tmp/bw-vap/webhookconfig.yaml <<YAML | kubectl apply -f -
   apiVersion: admissionregistration.k8s.io/v1
   kind: ValidatingWebhookConfiguration
   metadata: {name: bw-vap-webhook}
   webhooks:
     - name: webhook.example.com
       admissionReviewVersions: ["v1"]
       sideEffects: None
       failurePolicy: Fail
       clientConfig:
         url: https://10.10.10.180:8443/
         caBundle: $(base64 -w0 /var/tmp/bw-vap/cert.pem)
       rules:
         - apiGroups: ["apps"]
           apiVersions: ["v1"]
           operations: ["CREATE", "UPDATE"]
           resources: ["deployments"]
       namespaceSelector:
         matchLabels: {bw: vap}
   YAML
   ```

3. Send the one input the post never sends. A Deployment whose container declares no
   `securityContext` at all — the case `:31-33` writes an error message for. Watch the webhook's
   terminal while this runs.

   ```sh
   kubectl create -n bw-vap -f - <<'EOF'
   apiVersion: apps/v1
   kind: Deployment
   metadata: {name: nosc, labels: {app: nosc}}
   spec:
     selector: {matchLabels: {app: nosc}}
     template:
       metadata: {labels: {app: nosc}}
       spec:
         containers:
           - {image: nginx, name: nginx}
   EOF
   ```

4. Create the post's first policy, typo and all, exactly as printed at `:56-78`. Then read the
   status back the way `:81` does. This is the command that settles which half of the reference page
   to believe.

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: admissionregistration.k8s.io/v1
   kind: ValidatingAdmissionPolicy
   metadata:
     name: "pod-security.policy.example.com"
   spec:
     failurePolicy: Fail
     matchConstraints:
       resourceRules:
       - apiGroups:   ["apps"]
         apiVersions: ["v1"]
         operations:  ["CREATE", "UPDATE"]
         resources:   ["deployments"]
     validations:
     - expression: object.spec.template.spec.containers.all(c, has(c.securityContext) && has(c.securityContext.runAsNonRoot) && c.securityContext.runAsNonRoot)
       message: 'all containers must set runAsNonRoot to true'
     - expression: object.spec.template.spec.containers.all(c, has(c.securityContext) && has(c.securityContext.readOnlyRootFilesystem) && c.securityContext.readOnlyRootFilesystem)
       message: 'all containers must set readOnlyRootFilesystem to true'
     - expression: object.spec.template.spec.containers.all(c, !has(c.securityContext) || !has(c.securityContext.allowPrivilegeEscalation) || !c.securityContext.allowPrivilegeEscalation)
       message: 'all containers must NOT set allowPrivilegeEscalation to true'
     - expression: object.spec.template.spec.containers.all(c, !has(c.securityContext) || !has(c.securityContext.Privileged) || !c.securityContext.Privileged)
       message: 'all containers must NOT set privileged to true'
   YAML
   echo "create exit=$?"
   kubectl get validatingadmissionpolicies/pod-security.policy.example.com \
     -o jsonpath='{.status.typeChecking}{"\n"}' | jq .
   ```

5. Bind the broken policy and find out what a live undefined field does. Delete the webhook
   registration first so the only enforcer is the policy, bind with `Deny`, and then send a
   Deployment that satisfies all four rules honestly. Read the metric the post's appendix names,
   with its labels intact, before and after.

   ```sh
   kubectl delete validatingwebhookconfiguration bw-vap-webhook
   kubectl get --raw /metrics | grep '^apiserver_validating_admission_policy_check_total' || true
   kubectl apply -f - <<'YAML'
   apiVersion: admissionregistration.k8s.io/v1
   kind: ValidatingAdmissionPolicyBinding
   metadata: {name: "pod-security.policy-binding.example.com"}
   spec:
     policyName: "pod-security.policy.example.com"
     validationActions: ["Deny"]
     matchResources:
       namespaceSelector:
         matchLabels: {bw: vap}
   YAML
   kubectl create -n bw-vap -f - <<'EOF'
   apiVersion: apps/v1
   kind: Deployment
   metadata: {name: good, labels: {app: good}}
   spec:
     selector: {matchLabels: {app: good}}
     template:
       metadata: {labels: {app: good}}
       spec:
         containers:
           - image: nginx
             name: nginx
             securityContext:
               runAsNonRoot: true
               readOnlyRootFilesystem: true
               allowPrivilegeEscalation: false
               privileged: false
   EOF
   kubectl get --raw /metrics | grep '^apiserver_validating_admission_policy_check_total'
   ```

6. Fix the typo the way `:102-124` does, re-register the webhook, and reproduce the post's own
   five-line output. Only one character changes in the policy. The binding goes to `Warn` so that
   both enforcers speak on the same request, which is the whole point of `:147-179`.

   ```sh
   kubectl patch validatingadmissionpolicy pod-security.policy.example.com --type=json \
     -p '[{"op":"replace","path":"/spec/validations/3/expression","value":"object.spec.template.spec.containers.all(c, !has(c.securityContext) || !has(c.securityContext.privileged) || !c.securityContext.privileged)"}]'
   kubectl get validatingadmissionpolicies/pod-security.policy.example.com -o jsonpath='{.status.typeChecking}{"\n"}'
   kubectl patch validatingadmissionpolicybinding pod-security.policy-binding.example.com --type=merge \
     -p '{"spec":{"validationActions":["Warn"]}}'
   kubectl apply -f /var/tmp/bw-vap/webhookconfig.yaml
   tee /var/tmp/bw-vap/nginx.yaml <<'EOF' | kubectl create -n bw-vap -f -
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     labels: {app: nginx}
     name: nginx
   spec:
     selector: {matchLabels: {app: nginx}}
     template:
       metadata: {labels: {app: nginx}}
       spec:
         containers:
         - image: nginx
           name: nginx
           securityContext:
             privileged: true
             allowPrivilegeEscalation: true
   EOF
   ```

7. Count the messages in each direction. `:266-267` makes a claim about short circuiting that is
   easy to state and easy to check: with `Deny` the evaluation stops at the first failing
   expression, with `Warn` it does not. Remove the webhook so nothing else is speaking, then run the
   same Deployment under each action and count lines.

   ```sh
   kubectl delete validatingwebhookconfiguration bw-vap-webhook
   kubectl patch validatingadmissionpolicybinding pod-security.policy-binding.example.com --type=merge \
     -p '{"spec":{"validationActions":["Deny"]}}'
   kubectl create -n bw-vap -f /var/tmp/bw-vap/nginx.yaml 2>&1 | tee /tmp/deny.txt | wc -l
   kubectl patch validatingadmissionpolicybinding pod-security.policy-binding.example.com --type=merge \
     -p '{"spec":{"validationActions":["Warn"]}}'
   kubectl create -n bw-vap -f /var/tmp/bw-vap/nginx.yaml 2>&1 | tee /tmp/warn.txt | grep -c '^Warning:'
   cat /tmp/deny.txt /tmp/warn.txt
   kubectl -n bw-vap delete deployment nginx --ignore-not-found
   ```

8. Refactor to the post's final policy, then break its one undocumented rule on purpose. The policy
   at `:191-218` replaces four long expressions with two variables and four short ones. Apply it,
   confirm the behaviour is unchanged, then reorder the two variables so `securityContexts` is
   defined before the `containers` it refers to — the ordering rule at
   `validating-admission-policy.md:552-553` says that is what prevents circular references, and the
   post never mentions it.

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: admissionregistration.k8s.io/v1
   kind: ValidatingAdmissionPolicy
   metadata:
     name: "pod-security.policy.example.com"
   spec:
     failurePolicy: Fail
     matchConstraints:
       resourceRules:
       - apiGroups:   ["apps"]
         apiVersions: ["v1"]
         operations:  ["CREATE", "UPDATE"]
         resources:   ["deployments"]
     variables:
     - name: containers
       expression: object.spec.template.spec.containers
     - name: securityContexts
       expression: 'variables.containers.map(c, c.?securityContext)'
     validations:
     - expression: variables.securityContexts.all(c, c.?runAsNonRoot == optional.of(true))
       message: 'all containers must set runAsNonRoot to true'
     - expression: variables.securityContexts.all(c, c.?readOnlyRootFilesystem == optional.of(true))
       message: 'all containers must set readOnlyRootFilesystem to true'
     - expression: variables.securityContexts.all(c, c.?allowPrivilegeEscalation != optional.of(true))
       message: 'all containers must NOT set allowPrivilegeEscalation to true'
     - expression: variables.securityContexts.all(c, c.?privileged != optional.of(true))
       message: 'all containers must NOT set privileged to true'
   YAML
   kubectl get validatingadmissionpolicies/pod-security.policy.example.com -o jsonpath='{.status.typeChecking}{"\n"}'
   kubectl create -n bw-vap -f /var/tmp/bw-vap/nginx.yaml 2>&1 | grep -c '^Warning:'
   kubectl -n bw-vap delete deployment nginx --ignore-not-found
   kubectl get validatingadmissionpolicy pod-security.policy.example.com -o json \
     | jq '.spec.variables |= reverse' | kubectl apply -f - ; echo "reordered exit=$?"
   kubectl create -n bw-vap -f /var/tmp/bw-vap/nginx.yaml 2>&1 | tail -3
   ```

9. Read the appendix's two metrics with their labels showing. The post's PromQL filters on `policy`
   alone; the series carry three more labels, and one of them is the instrument step 5 needed.

   ```sh
   kubectl get --raw /metrics | grep '^apiserver_validating_admission_policy_check_total'
   kubectl get --raw /metrics | grep '^apiserver_validating_admission_policy_check_duration_seconds_count'
   kubectl get --raw /metrics | grep -c '^apiserver_validating_admission_policy_check_duration_seconds_bucket'
   kubectl get --raw /metrics | grep -o 'error_type="[^"]*"' | sort | uniq -c
   kubectl get --raw /metrics | grep -c '^apiserver_mutating_admission_policy' || true
   ```

10. Read the pin, then count the post's own bundle. Run this on the machine holding the checkout,
    not on the node.

    ```sh
    cd /path/to/kubernetes/website/content/en
    sed -n '474,482p;523,532p' docs/reference/access-authn-authz/validating-admission-policy.md
    sed -n '533,567p' docs/reference/access-authn-authz/validating-admission-policy.md
    sed -n '313,322p' docs/reference/access-authn-authz/validating-admission-policy.md
    sed -n '385,398p' docs/reference/instrumentation/metrics.md
    sed -n '1407,1414p' docs/reference/instrumentation/metrics.md
    head -1 blog/_posts/2024/validating-admission-policy-ga/index.md | cat -v
    find blog/_posts -type f ! -name '*.md' | sed 's/.*\.//' | sort | uniq -c | sort -rn
    diff <(sed -n '25,48p' blog/_posts/2024/validating-admission-policy-ga/index.md) \
         <(sed -n '16,39p' blog/_posts/2024/validating-admission-policy-ga/webhook.go) && echo identical
    ```

**Expect**

Step 1. `kubectl version` reports v1.35. `go version` reports whatever Debian Trixie ships, which is
well past anything `webhook.go` needs — the file uses no generics, no new standard library and three
Kubernetes packages that have not changed shape in years. The namespace carries the label `bw=vap`,
which is what both the webhook registration and the policy binding will select on; the post used
`kubernetes.io/metadata.name` for the same purpose, and either works.

Step 2. `go mod tidy` pulls `k8s.io/api` and `k8s.io/apimachinery` and their transitive
dependencies, and the build succeeds without touching a line of the post's code. The server prints
nothing and holds the terminal. The registration applies cleanly: note that the API server is being
told to dial an IP address on the node it is running on, over a certificate whose only SAN is that
same address, with the certificate itself serving as its own CA bundle. That is the shortest legal
path to a working webhook and it is deliberately not how a real one is deployed — the point here is
to get the post's binary answering, not to learn webhook plumbing.

Step 3. The Deployment is refused, and the refusal is the finding. The message does not name any of
the four rules `verifyDeployment` writes; it is a transport failure, in which the API server reports
that it failed calling the webhook named `webhook.example.com`, followed by `EOF` or a connection
reset. In the webhook's terminal there is a Go panic: the runtime error for an invalid memory
address, which is how Go reports a nil pointer dereference, with `verifyDeployment` in the stack.
The process survives, because the standard library's HTTP server recovers a panicking handler and
drops that one connection, so the next step still has a webhook to talk to. Two things follow.
First, `:180`'s equivalence claim does not hold: the policy answers this input with a sentence a
user can act on, and the webhook answers it by dying. Second, the rejection here is an accident of
`failurePolicy: Fail`. Set it to `Ignore` and the same Deployment is admitted, with no
`securityContext` at all — the exact object the webhook exists to stop.

Step 4. The policy is created. Exit code zero, no error, exactly as `:79` reports. Then
`.status.typeChecking` comes back non-empty, with one entry whose `fieldRef` is
`spec.validations[3].expression` and whose `warning` names `apps/v1, Kind=Deployment` and an
undefined field `Privileged`, twice, once per column position. That is
`validating-admission-policy.md:529-530` winning over a plain reading of `:476-477`: the definition
was not rejected, because the error was a type error and not a syntax error, and the page only says
so fifty lines later. The two column markers in the warning are worth reading — they point at
character 76 and character 128 of the expression, which are the two places `Privileged` appears.

Step 5. This step has two possible outcomes and the point is to find out which one this cluster
gives you, because the post never says. Either the fourth expression errors at evaluation, in which
case `failurePolicy: Fail` turns that error into a denial and a Deployment that satisfies all four
rules is refused anyway, with a message that is not one of the four; or the expression evaluates
against the request object as an untyped map, in which case `has(c.securityContext.Privileged)` is
simply false, the `!has(...)` disjunct is true, the whole expression is true for every input, and
the Deployment is created while the fourth rule silently enforces nothing. The metric decides:
compare the `apiserver_validating_admission_policy_check_total` lines before and after and read the
`error_type` label. A non-empty `error_type` is the first outcome; an empty one with the counter
advancing is the second. Both are bad and they are bad in opposite directions — one takes the
resource offline, the other removes a security rule without saying so — and the post's narrative,
which fixes the typo and moves on, never tells a reader which risk they were running while the
warning sat unread.

Step 6. One character changes and `.status.typeChecking` comes back empty, which
`validating-admission-policy.md:481-482` says is how a clean result is reported: the field's
presence means checking finished, its emptiness means nothing was found. Then the post's own output
at `:173-179` reproduces: four `Warning:` lines, one per expression, each naming the policy and the
binding, followed by one `Error from server` line from the webhook that lists all four failures in a
single bracketed message. Five lines, two enforcers, identical semantics — this is the screenshot
the post is built around, and on this input it is completely accurate. Keep it beside step 3's
output; the difference between the two is one absent field in the manifest.

Step 7. One line under `Deny`, four under `Warn`. The `Deny` message quotes only the first failing
expression's message, `all containers must set runAsNonRoot to true`, exactly as `:264` shows, and
stops there. The `Warn` run produces four `Warning:` lines because nothing short circuits: warnings
are collected from every expression and the request proceeds. `:266-267` is right, and the asymmetry
has a practical consequence the post states in one sentence and does not dwell on — a policy under
`Deny` will only ever tell a user about one thing at a time, so fixing four violations takes four
round trips, which is precisely why the post developed against `Warn` first at `:131-133`.

Step 8. The refactored policy applies, `.status.typeChecking` is empty, and the `Warn` run produces
the same four warnings as step 7 — the `c.?securityContext` and `optional.of(true)` form is
equivalent to the `has()` form for this rule. Then the reordered version is refused: the API server
rejects the policy because `securityContexts` refers to `variables.containers` before it is defined,
which is the ordering rule at `validating-admission-policy.md:552-553` doing the work it is there to
do. If your cluster accepts the reordered policy instead, that is the more interesting result and
the page is wrong; check `.status.typeChecking` and then send the Deployment, because an
accepted-but-broken variable reference lands you back in step 5's two outcomes.

Step 9. Both series are present with four labels each: `enforcement_action`, `error_type`, `policy`,
`policy_binding`. The `policy` label holds the full name `pod-security.policy.example.com`, so the
post's two PromQL examples at `:277` and `:282` would match unchanged. The `enforcement_action`
label distinguishes the `Deny` runs from the `Warn` runs of steps 6 to 8, which means one metric
tells you both how often a policy fired and what the cluster did about it. The bucket count on the
histogram is the usual fixed ladder, not one bucket per policy. The last grep finds the mutating
counterparts, which exist at the pin and belong to a feature this post could not have known about.

Step 10. `:476-482` and `:523-532` read back to back are the disagreement in full: the first says a
definition with errors is rejected, the second says type checking never affects behaviour. The
variable composition section carries the four semantics the post's refactor leans on without naming.
`:313-322` is the `failurePolicy` definition that makes step 5's first outcome possible — `Fail`
means an error *calling* the policy rejects the request, and an expression that errors counts as
that. The metrics blocks show BETA on both. `head -1` on the post prints six hyphens where every
other post in the tree prints three, and the file-extension census prints `1 go` — the whole archive
ships exactly one program, and it is the one that crashes in step 3. The final `diff` is empty: the
excerpt at `:25-48` and the file at its own `:16-39` are the same 24 lines, so the defect is in both
places a reader could find it.

**Read on**

1. `docs/reference/access-authn-authz/validating-admission-policy.md:474-532` — the type checking
   section end to end, including the four limitations. The one about CRDs at `:531` is the one most
   likely to surprise someone who has just watched type checking work on a Deployment.

2. `docs/reference/access-authn-authz/validating-admission-policy.md:327-390` — the variables a CEL
   expression can reach: `object`, `oldObject`, `request`, `params`, `namespaceObject` and
   `authorizer`. The post uses one of the six.

3. `docs/reference/instrumentation/metrics.md:385-397` — the two series, their help text, their type
   and their labels, as generated from the API server's own registry. Worth reading beside the
   post's appendix to see how little of a metric a PromQL example actually uses.

4. [The 2023 policy-library exercise](../2023/02-kubescape-validating-admission-policy-library.md) —
   the same feature one year earlier, at `v1alpha1`, with the gate's ladder and a policy whose
   expressions survived alpha to stable without an edit.

5. Unanswerable from the pin: why `webhook.go` was published with this defect and never corrected.
   The file is a page resource in a bundle, it is linked from the post's own prose, and nothing in
   the pinned tree tracks blog assets for correctness. There is no errata mechanism for a Kubernetes
   blog post anywhere in this checkout.

**Teardown**

```sh
kubectl delete validatingadmissionpolicybinding pod-security.policy-binding.example.com --ignore-not-found
kubectl delete validatingadmissionpolicy pod-security.policy.example.com --ignore-not-found
kubectl delete validatingwebhookconfiguration bw-vap-webhook --ignore-not-found
kubectl delete namespace bw-vap --wait=true
# stop the foreground `go run .` with Ctrl-C in its terminal, then:
rm -rf /var/tmp/bw-vap /tmp/deny.txt /tmp/warn.txt
kubectl get validatingadmissionpolicy,validatingwebhookconfiguration
```

Delete the binding before the policy. The other order leaves a binding pointing at nothing, which is
legal and silently enforces nothing — worth seeing once, but not worth leaving behind. If the node
was untainted in step 1 and the taint is wanted back:

```sh
kubectl taint node --all node-role.kubernetes.io/control-plane=:NoSchedule
```
