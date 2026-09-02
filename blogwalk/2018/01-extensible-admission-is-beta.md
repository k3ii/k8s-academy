<a id="extensible-admission-is-beta"></a>
# The manifest at the centre of this post cannot be pasted at all — not because of its API version, which is the smaller problem, but because Blogger's escaping and a line-number gutter are inside the code fence — and once you have retyped it the API server rejects it on two fields that did not exist in 2018, defaults four more against it, tells you nothing about the one rule shape that has silently stopped matching, and would have you register a webhook the project's own guidance now says to reach for last

**Post** — [Extensible Admission is Beta](https://kubernetes.io/blog/2018/01/extensible-admission-is-beta/),
2018-01-11, Kubernetes v1.9. Part of the *Five Days of Kubernetes 1.9* series whose index post the
census marks `skip`. It carries no author frontmatter; the credit is a sentence in its last
paragraph — *"this work, driven by both Red Hat and Google"* — and the reviewer list on the pinned
page that replaced it is where you can still read who owned this area.

**As written** — the post is an explainer, not a walkthrough, and it has exactly one artefact you
are meant to copy. Everything before that artefact exists to make it legible.

It sets the stage first. *"The admission stage of API server processing is one of the most powerful
tools for securing a Kubernetes cluster by restricting the objects that can be created, but it has
always been limited to compiled code. In 1.9, we promoted webhooks for admission to beta, allowing
you to leverage admission from outside the API server process."*

Then the two-phase model, which the post states as a rule:

> 1. Mutation, which allows modification of the body content itself as well as rejection of an API
>    request.
> 2. Validation, which allows introspection queries and rejection of an API request.
>
> An admission plugin can be in both phases, but all mutation happens before validation.

Its worked example of a plugin in both phases is `PodNodeSelector`, and the post describes it
twice. In the mutation phase it *"uses an annotation on a namespace
`namespace.annotations[“scheduler.alpha.kubernetes.io/node-selector”]` to find a label selector and
add it to the `pod.spec.nodeselector` field."* In the validation phase the same plugin *"ensures
that all pods’ `spec.nodeSelector` fields are constrained by the node selector restrictions on the
namespace. Even if a mutating admission plugin tries to change the `spec.nodeSelector` field after
the PodNodeSelector runs in the mutating chain, the PodNodeSelector in the validating chain
prevents the API resource from being created because it fails validation."* Its two other named
compiled plugins are `PodSecurityPolicy` (*"prevents escalating containers"*) and `ResourceQuota`.

Four use cases follow, numbered, and they are the post's argument for why you would want this:

> 1. Mutation of resources like pods. Istio has talked about doing this to inject side-car
>    containers into pods. You could also write a plugin which forcefully resolves image tags into
>    image SHAs.
> 2. Name restrictions. On multi-tenant systems, reserving namespaces has emerged as a use-case.
> 3. Complex CustomResource validation. Because the entire object is visible, a clever admission
>    plugin can perform complex validation on dependent fields (A requires B) and even external
>    resources (compare to LimitRanges).
> 4. Security response. If you forced image tags into image SHAs, you could write an admission
>    plugin that prevents certain SHAs from running.

Then registration, five things a webhook must declare — how to connect, how to verify the server,
which URL path, which resources and verbs, and *"What an API server should do on connection
failures"* — and the manifest. This is reproduced here exactly as the pinned source carries it,
because how it is carried is half the exercise:

```
1 apiVersion: admissionregistration.k8s.io/v1beta1  
2 kind: ValidatingWebhookConfiguration  
3 metadata:  
4   name: namespacereservations.admission.online.openshift.io  
5 webhooks:  
6 - name: namespacereservations.admission.online.openshift.io  
7   clientConfig:  
8     service:  
9       namespace: default  
10      name: kubernetes  
11     path: /apis/admission.online.openshift.io/v1alpha1/namespacereservations  
12    caBundle: KUBE\_CA\_HERE  
13  rules:  
14  - operations:  
15    - CREATE  
16    apiGroups:  
17    - ""  
18    apiVersions:  
19    - "\*"  
20    resources:  
21    - namespaces  
22  failurePolicy: Fail
```

Four of those twenty-two lines are then annotated by number, and the last annotation is the one the
post cares most about: *"Line 22: `failurePolicy` - says what to do if the webhook admission server
is unavailable. Choices are “Ignore” (fail open) or “Fail” (fail closed). Failing open makes for
unpredictable behavior for all clients."* The manifest sets `Fail`, which in v1beta1 was not the
default, so this is a deliberate choice the post argues for.

It closes on topology, and here it is at its most confident. The recommendation is to build your
webhook server as an *extension API server* and aggregate it:

> ### Simple, secure, portable, zero-config topology
>
> If you build your webhook admission server to also be an extension API server, it becomes
> possible to aggregate it as a normal API server.

Four advantages are listed for that shape — the webhook becomes reachable at
`kubernetes.default.svc` so *"you can test using `kubectl`"*; it inherits in-cluster authentication
and authorization *"(without any config)"*; extension API servers reach it with their own
in-cluster credentials, also without config; and *"Extension API servers do not leak their service
account token to your webhook because they go through kube-apiserver, which is a secure front
proxy."* The section ends: *"The topology above is zero-config and portable to every Kubernetes
cluster."* For the alternatives the post is blunt — *"Other topologies are possible but require
additional manual configuration as well as a lot of effort to create a secure setup"* — and for
externally hosted webhooks it says flatly that *"there is really no alternative to configuring that
file manually."*

Two libraries are offered to make the 200-line server real, `generic-admission-apiserver` and
`kubernetes-namespace-reservation`, both `openshift/`. The manifest's names —
`namespacereservations.admission.online.openshift.io`, and a `clientConfig.service.path` under
`/apis/admission.online.openshift.io/v1alpha1/` — are that second project, so the manifest is not
an invented illustration. It is the registration record of a webhook that was running in
production somewhere, pasted into a blog post.

**As it runs now** — five distinct failures, and the difference between them is the exercise.

*It cannot be copied.* The fence above is verbatim from the pinned source. The gutter `1`–`22` is
*inside* the fence, and so are Blogger's escapes: `KUBE\_CA\_HERE` on line 12, `"\*"` on line 19.
Markdown does not process escapes inside a fenced block, so a reader on kubernetes.io today sees
the backslashes and the numbers on the page. Nothing about this is an API question; the manifest
has to be retyped before any version of Kubernetes can reject it. The same class of artefact is in
the prose — the curly quotes inside the inline code span
`namespace.annotations[“scheduler.alpha.kubernetes.io/node-selector”]` are the annotation key with
two characters that are not in it.

*It errors, first on the group version.* `admissionregistration.k8s.io/v1beta1` has not been served
since v1.22 (`deprecation-guide.md:172-175`), so a retyped manifest fails on the kind before any
field is looked at.

*It errors again, on two fields that did not exist when it was written.* Change the version to `v1`
and the API server rejects the object for missing `admissionReviewVersions` and `sideEffects`.
Neither word appears anywhere in the post. `extensible-admission-controllers.md:353` states the
first one as flatly as it can be stated — *"`admissionReviewVersions` is a required field when
creating webhook configurations"* — and the API reference marks it required with a bare asterisk
(`validating-webhook-configuration-v1.md:97`). `sideEffects` is required and constrained: only
`None` and `NoneOnDryRun` are permitted for `v1` (`deprecation-guide.md:183-184`), which means the
post's webhook must now declare something the post never asks it to consider.

*It errors a third time, on a placeholder.* `caBundle: KUBE\_CA\_HERE` is not valid base64. It is
also not required: *"caBundle is a PEM encoded CA bundle which will be used to validate the
webhook's server certificate. If unspecified, system trust roots on the apiserver are used"*
(`webhook-client-config-v1-admissionregistration.md:40`). So the field can be deleted rather than
filled, and deleting it changes the trust model without saying so.

*Then it succeeds, and four things you did not write are now true.* A registration that clears all
of the above is accepted, and reading it back shows defaults the post's era did not have.
`failurePolicy` is the one the post chose, so it looks unchanged — but it is now also the default
(`extensible-admission-controllers.md:1154`), which means it is no longer evidence of a decision.
`matchPolicy` defaults to `Equivalent` where v1beta1 defaulted to `Exact`; `timeoutSeconds` is 10
where v1beta1 gave 30 (`extensible-admission-controllers.md:1080`); `scope` is `"*"`. All four
crossings are recorded in one place, `deprecation-guide.md:178-186`, and the *why* for each is in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md) rather than re-derived
here.

*And one thing succeeds while doing nothing, silently.* The post's rule names `namespaces` in the
core group explicitly, so it still matches. But a rule of the shape the pinned page itself now
prints as an example — `apiGroups: ["*"]`, `resources: ["*"]` — no longer reaches TokenReview,
SubjectAccessReview, SelfSubjectReview, LocalSubjectAccessReview, SelfSubjectAccessReview or
SelfSubjectRulesReview, as of v1.37 (`extensible-admission-controllers.md:680-717`). A rule that
names one of them outright gets a warning; a wildcard that used to cover them gets nothing, and the
page says why: *"Rules that match these resources only through a wildcard (`"*"`) in `apiGroups` or
`resources` are not flagged, because their intent is ambiguous"* (`:707-709`).

**The diff, and why** — this post is on the winning side of its own argument and it is still almost
entirely unusable, which is a combination the verdict vocabulary has no word for. Five things moved,
in four different directions.

*The post broke, and the release is v1.22.* Nothing about admission webhooks was withdrawn; the
group version was. `admissionregistration.k8s.io/v1` has been available since v1.16
(`deprecation-guide.md:175`) and v1beta1 stopped being served in v1.22. The five field-level
crossings at `deprecation-guide.md:178-186` are not a rename — each one is a default the project
decided had been wrong, and
[`research/blog-era-translation.md`](../../research/blog-era-translation.md) names the pressure:
`Ignore` by default meant a security webhook failed open, and `Exact` meant a webhook registered
for one group version never saw the same object submitted under another. The post is a casualty of
its own case being accepted. It argued for fail-closed in a release where fail-open was the
default, and four releases later fail-closed *was* the default — which is why the one field the
post sets by hand is the only one a reader today would not think to check.

*The post was wrong when it was published, in the smallest possible way.* Line numbers and
backslashes inside a code fence are not a Kubernetes fact and no release fixed them, because there
is nothing in Kubernetes to fix. The post's only artefact never worked as printed, and a reader who
assumes it did will read the resulting parse error as a cluster problem. The precedent for treating
this as a diff rather than a typo is [#67](https://github.com/k3ii/k8s-academy/issues/67), which
found two 2019 posts with typographic quotes in code fences; this is the same failure a year
earlier, in a different flavour, on a post whose fence is the whole reason it earned a `walk`.

*The project abandoned the plan, and the plan was the topology.* The post's *"simple, secure,
portable, zero-config"* recommendation — make the webhook server an aggregated extension API server
— has no counterpart in the pinned tree. Neither `extensible-admission-controllers.md` nor
`admission-webhooks-good-practices.md` mentions aggregation as a webhook deployment shape at all;
the single occurrence of the word in either page is about aggregated API servers *calling* webhooks
(`extensible-admission-controllers.md:243`). What replaced it is not a better version of the same
idea. `admission-webhooks-good-practices.md` tells you to run the webhook as an ordinary Service
with several backends behind it, in a high-availability deployment, with a small timeout
(`:209-237`) — the
shape the post dismissed as *"a lot of effort to create a secure setup"*. And the post's flat claim
that manual kubeconfig is the only option for external webhooks is now merely almost true: v1.37
added an alpha mechanism for the API server to issue short-lived ServiceAccount tokens bound to a
specific webhook configuration and scoped by API group. Read the note that ships with it before
counting it as the answer, though — *"Automatic token acquisition and presentation by the
`kube-apiserver` and aggregated API servers when calling webhooks, along with a webhook-side token
verification library, are not part of this mechanism"* (`:241-245`). The mechanism issues the
token. Nothing yet carries it.

*The post is still right about the thing it was not aware it was arguing.* Its rule that *"all
mutation happens before validation"* holds, and the pinned page turns it into advice: *"Admission
webhooks that need to guarantee they see the final state of the object in order to enforce policy
should use a validating admission webhook, since objects can be modified after being seen by
mutating webhooks"* (`extensible-admission-controllers.md:33-34`). But the mechanism the post names
for controlling order within the mutating phase is gone from the documentation. The post says of
the webhook `name` field: *"For mutating webhooks, these are sorted to provide ordering."* No page
in the pinned admission set says that. What they say instead is *"A single ordering of mutating
admissions plugins (including webhooks) does not work for all cases"*
(`extensible-admission-controllers.md:1084`) and *"Mutating admission webhooks don't run in a
consistent order"* (`admission-webhooks-good-practices.md:465`). The replacement is
`reinvocationPolicy`, defaulting to `Never`, with three warnings attached, of which the sharpest is
that *"The number of additional invocations is not guaranteed to be exactly one"*
(`:1101`). So the post's ordering rule survived and the post's ordering *mechanism* was
withdrawn — and a reader who takes the naming advice will build a dependency on something that is
now documented as unreliable.

*And the post's own worked example has been overtaken by stasis.* `PodNodeSelector` is still
`{{< feature-state for_k8s_version="v1.5" state="alpha" >}}` at the pin
(`admission-controllers.md:682`) — alpha since the release before this post's predecessor,
still disabled by default, still keyed on `scheduler.alpha.kubernetes.io/node-selector`
(`:718`), and its configuration file still carries the promise that *"the configuration file format
will move to a versioned file in a future release"* (`:694`). Nine years of future releases have
gone by. And the pin disagrees with the post about what the plugin does: the post puts it in both
chains, while the page labels it **Type: Validating** (`:684`) one line before describing it as one
that *"defaults and limits what node selectors may be used within a namespace"* (`:686`) —
defaulting being mutation. The post and the label cannot both be right, and the pinned page
contradicts itself in two consecutive lines, so this exercise records the disagreement rather than
resolving it. The post's second named plugin fared worse: `PodSecurityPolicy` appears once in the
whole pinned tree, in a sentence about its own replacement (`admission-controllers.md:762`).

*The use cases are the measuring instrument.* The post's four reasons to want a webhook, read
against the pin one at a time, are what tell you how far this went:

| # | the post's use case | at the pin |
|---|---|---|
| 1 | Mutate pods — *"Istio has talked about doing this to inject side-car containers"* | Still a webhook case, and named as one: *"Make complex modifications that require advanced logic, like calling external APIs"* (`admission-webhooks-good-practices.md:99-100`). Istio appears five times in the pinned docs and not once in connection with admission (glossary, ingress controllers, a sidecar-conversation link) |
| 2 | Name restrictions — reserving namespaces | A ValidatingAdmissionPolicy, with no server, no Service, no CA bundle and no failure-mode decision to make |
| 3 | Complex CustomResource validation | Told not to: *"don't use admission webhooks to validate values in CustomResource specifications or to set default values for fields"* (`admission-webhooks-good-practices.md:146-147`), because CRDs carry validation rules and defaulting themselves |
| 4 | Security response — block particular image SHAs | Never modernised in-tree. `ImagePolicyWebhook` is still documented, still disabled by default, still configured by a file on the API server's disk (`admission-controllers.md:323-329`) |

And the pinned guidance closes the argument the post opened. Its four-mechanism table
(`admission-webhooks-good-practices.md:83-134`) is followed by one sentence: *"The Kubernetes
project recommends that you use CEL-based admission control when possible"* (`:139-140`). The post
made admission extensible from outside the API server process. The project then spent six releases
building a way to do most of it back inside.

**No gate** — for the post's subject, and this is the finding rather than a gap in the search.
There is no feature gate for admission webhooks. No file in the 487 under `feature-gates/` is named
for `MutatingAdmissionWebhook`, `ValidatingAdmissionWebhook`, dynamic admission or extensible
admission; the mechanism went from beta in v1.9 to a served `v1` in v1.16 and its history is
readable only from `deprecation-guide.md:172-186` and from the fact that both plugins ship in the
default-enabled set — which `admission-controllers.md:916-918` asserts without printing (*"The
recommended admission controllers are enabled by default"*, the list itself deferred to the
kube-apiserver options reference; the v1.37 list is in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md)). The two plugin
sections are `admission-controllers.md:519` and `:897`. Five gate files mention
admission webhooks in their bodies. Every one of them is for something built around the mechanism
after this post, and their ladders are below.

The three that replace it. `ValidatingAdmissionPolicy`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.26 – v1.27 |
| beta | `false` | — | v1.28 – v1.29 |
| stable | `true` | — | v1.30 – v1.31 |

The file declares `removed: true` — the gate is gone, the feature is unconditional, and
`validating-admission-policy.md:12` carries `state="stable" for_k8s_version="v1.30"` to match.
`MutatingAdmissionPolicy`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.30 – v1.33 |
| beta | `false` | — | v1.34 – v1.35 |
| stable | `true` | — | v1.36 – |

No `removed:`, so this gate still exists at the pin even though its stage is stable. And the body
of the gate file carries a fact the table cannot hold: *"For Kubernetes v1.30 and v1.31, this
feature gate existed but had no effect."* Two of the four releases in the alpha row are a gate you
could set that did nothing.
[`research/blog-era-translation.md`](../../research/blog-era-translation.md) dates this feature's
alpha to v1.32 from KEP-3962, which is the first release the gate did anything; the gate file dates
it to v1.30, which is the first release the gate existed. Both are recorded; they are answering
different questions. `ManifestBasedAdmissionControlConfig`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.36 – v1.36 |
| beta | `true` | — | v1.37 – |

One release of alpha, then on by default (`manifest-admission-control.md:26`). This is the newest
mechanism in the pin and the one that most directly answers the post's *"Registration"* section:
webhook configurations and CEL policies can be loaded from files on disk instead of from the API,
which the page justifies with three limitations of API registration — a bootstrap gap, a
self-protection gap, and an etcd dependency (`:32-46`). The post's fifth registration fact was what
the API server should do on connection failures. The pin's answer includes not having to be
registered through the API at all.

The two that modify it. `AdmissionWebhookMatchConditions`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.27 – v1.27 |
| beta | `true` | — | v1.28 – v1.29 |
| stable | `true` | — | v1.30 – v1.32 |

`removed: true`. This is the only one of the five that changes the post's own `rules` block: a
second filter, up to 64 CEL expressions per webhook, evaluated before the call
(`extensible-admission-controllers.md:861-950`). Its cost validation has its own gate,
`StrictCostEnforcementForWebhooks` — beta `false` v1.31, stable `true` from v1.32 — which is a
gate for the enforcement of a limit on a filter on the mechanism the post announces, three
removes from the post. And `ExcludeAdmissionWebhookVirtualResources`:

| stage | default | locked | releases |
|---|---|---|---|
| beta | `true` | — | v1.37 – |

Straight to beta and on, in the pin's own release, with the deprecation of the old behaviour dated
in prose rather than in the ladder: *"Webhook interception of these virtual resources is deprecated
as of Kubernetes v1.37"*, and the gate *"is planned to be locked to enabled when this feature
graduates to stable"* (`extensible-admission-controllers.md:711-717`). A `locked` column that is
`—` today with a stated plan to become `true` is the clearest reading in this file of why `locked`
is a column and not a suffix.

Read the five together and the shape is this: the post's mechanism has no gate because it is
finished, and everything gated around it is either a way to call it less often or a way not to call
it at all.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`. Every
step below is an API-server decision — registration validation, defaulting, admission-time
rejection — and none of it needs a second node or a running Pod. Bring it up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, then
[the node baseline](../../strands/lab-topologies.md#node-baseline-steps), then
`ssh zain@10.10.10.180`.

Say plainly what this topology cannot show. It never runs a webhook server, so nothing here
observes an `AdmissionReview` on the wire or a webhook returning `allowed: false`. That is
deliberate and it is the exercise's title: every failure below lands before the call. A webhook that
is never reached is the post's own `failurePolicy` sentence, tested.

**Do**

1. Confirm which versions of the post's API group your cluster serves, and compare against the
   pinned reference.

   ```
   kubectl api-versions | grep admissionregistration
   kubectl api-resources --api-group=admissionregistration.k8s.io
   ```

   `group-versions.md:13` lists three versions for this group — `v1, v1beta1, v1alpha1`. Note which
   of them your cluster answers for, and note that all six kinds in
   `docs/reference/kubernetes-api/admissionregistration/` are `-v1` pages.

2. Retype the post's manifest into `post-webhook.yaml`, without the gutter and without the
   backslashes, changing nothing else. Then apply it.

   ```
   kubectl apply -f post-webhook.yaml
   ```

3. Change only `apiVersion` to `admissionregistration.k8s.io/v1` and apply again. Read the error to
   the end and count the field paths it names.

4. Add the two required fields and nothing else — `admissionReviewVersions: ["v1"]` and
   `sideEffects: None` on the webhook entry — and apply again.

5. Delete the `caBundle` line entirely and apply again. Before you do, decide what deleting it
   changes about who the API server will trust, then check your answer against
   `webhook-client-config-v1-admissionregistration.md:40`.

6. Read back what the API server stored, and diff it against what you sent.

   ```
   kubectl get validatingwebhookconfiguration \
     namespacereservations.admission.online.openshift.io \
     -o yaml | grep -E 'failurePolicy|matchPolicy|timeoutSeconds|scope|sideEffects|admissionReviewVersions'
   ```

   Four of these you did not write. One of them the post wrote by hand for a reason it explains.
   Say which is which, then find all five in `deprecation-guide.md:178-186`.

7. Now find out what the registered webhook costs. The rule is `CREATE` on core `namespaces`, the
   `failurePolicy` is `Fail`, and `clientConfig.service` points at the `kubernetes` Service in
   `default` at an OpenShift path that has never existed on your cluster.

   ```
   kubectl create namespace probe
   ```

8. Undo it, and confirm the cluster is whole again.

   ```
   kubectl delete validatingwebhookconfiguration \
     namespacereservations.admission.online.openshift.io
   kubectl create namespace probe && kubectl delete namespace probe
   ```

9. Re-register the webhook with one `matchConditions` entry that is valid CEL and evaluates false
   for this namespace — for example a condition named `only-team-namespaces` with the expression
   `object.metadata.name.startsWith("team-")` — then create a namespace whose name does not start
   with `team-`. The configuration is registered, the rule matches, and the request succeeds.
   Explain, from `extensible-admission-controllers.md:945-950`, why a request that matched the rule
   was admitted without the webhook being contacted, and what would have happened instead if the
   expression had errored rather than returned false. Then delete the configuration.

10. Register a webhook whose rule explicitly names `subjectaccessreviews` in the
    `authorization.k8s.io` group, and read what `kubectl` prints alongside the success.

    ```
    kubectl apply -f sar-webhook.yaml
    ```

    Then change that rule to `apiGroups: ["*"], resources: ["*"]` and apply again. One of these two
    tells you the rule has no effect and the other does not, and the reason is at
    `extensible-admission-controllers.md:703-710`. Delete the configuration.

11. Do the post's use case 2 with no webhook server at all. Apply the pinned tree's own
    ValidatingAdmissionPolicy pair from
    `content/en/examples/validatingadmissionpolicy/basic-example-policy.yaml` and
    `basic-example-binding.yaml` — a policy requiring `object.spec.replicas <= 5` on `apps/v1`
    deployments, bound to namespaces labelled `environment: test`. Label a namespace to match, then
    test both sides against the server without scheduling anything:

    ```
    kubectl label namespace default environment=test
    kubectl create deployment six --image=registry.k8s.io/pause:3.10 --replicas=6 --dry-run=server
    kubectl create deployment four --image=registry.k8s.io/pause:3.10 --replicas=4 --dry-run=server
    ```

    `--dry-run=server` runs the full admission chain, which is why step 4's `sideEffects: None`
    matters: a webhook that has not declared itself dry-run-safe is not sent dry-run requests at
    all (`extensible-admission-controllers.md:1039-1040`). Note that no Service, no certificate and
    no `failurePolicy` decision was involved in any of this.

12. Find the two places the pinned tree contradicts itself about the mechanism from step 11.
    `admission-controllers.md:894` says ValidatingAdmissionPolicy *"is enabled when both feature
    gate `validatingadmissionpolicy` and `admissionregistration.k8s.io/v1alpha1` group/version are
    enabled"*, while its gate file records `stable` from v1.30 and `removed: true`. And
    `validating-admission-policy.md:298`, on the stable page, gives a
    `ValidatingAdmissionPolicyBinding` example at `admissionregistration.k8s.io/v1alpha1` where
    every other example on the page uses `v1`. Apply that one example and see what your cluster
    says.

13. Ask the list where the fourth mechanism went.

    ```
    kubectl api-resources --api-group=admissionregistration.k8s.io -o name
    ```

    `admission-controllers.md:43-46` claims to list the admission controllers in this Kubernetes
    version, and `:50-54` names exactly three extension points — MutatingAdmissionWebhook,
    ValidatingAdmissionWebhook and ValidatingAdmissionPolicy. `MutatingAdmissionPolicy` appears
    nowhere in that file. Its gate says `stable`, `true`, from v1.36.

14. Last, the post's worked example, which needs no cluster change to check.

    ```
    kubectl get --raw /metrics | grep -c apiserver_admission_webhook_rejection_count
    tr ' ' '\n' < /proc/"$(pgrep kube-apiserver)"/cmdline | grep -E 'admission|feature-gates'
    ```

    Then read `admission-controllers.md:680-694` and answer whether `PodNodeSelector` is running on
    your cluster, whether it could be, and how many releases have passed since the note about the
    versioned configuration file was written.

**Expect**

Step 1 — `admissionregistration.k8s.io/v1` at minimum, and six resources:
`mutatingwebhookconfigurations`, `validatingwebhookconfigurations`, `validatingadmissionpolicies`,
`validatingadmissionpolicybindings`, `mutatingadmissionpolicies`, `mutatingadmissionpolicybindings`.
Alpha group versions are not served unless enabled (`using-api/_index.md:108-116`), so if
`v1alpha1` is absent from `api-versions` while `group-versions.md:13` lists it, you have found the
difference between what the API can serve and what your API server was started with.

Step 2 — a failure naming the kind, of the form
`error: resource mapping not found for name: "namespacereservations.admission.online.openshift.io"
... no matches for kind "ValidatingWebhookConfiguration" in version
"admissionregistration.k8s.io/v1beta1"`. Not a field error. The object was never parsed as a
webhook configuration.

Step 3 — a validation error naming exactly two paths,
`webhooks[0].sideEffects` and `webhooks[0].admissionReviewVersions`, each `Required value`. If you
see three, you left the `caBundle` placeholder in and the third is `webhooks[0].clientConfig.caBundle`
failing to decode.

Step 4 — either success, or the `caBundle` error alone.

Step 5 — `validatingwebhookconfiguration.admissionregistration.k8s.io/namespacereservations.admission.online.openshift.io
created`.

Step 6 — `failurePolicy: Fail`, `matchPolicy: Equivalent`, `timeoutSeconds: 10`, `scope: '*'`,
plus the two fields you added. The post wrote one of those five values; the API server chose the
other four.

Step 7 — the namespace is **not** created, and the error names the webhook rather than the
namespace: `Error from server (InternalError): Internal error occurred: failed calling webhook
"namespacereservations.admission.online.openshift.io"`. Read the tail of that message for whether
the API server got a connection error or an HTTP status, and match it against the four error
classes at `extensible-admission-controllers.md:1131-1136`.

Step 8 — the delete succeeds, and so does the namespace. If the delete had also been blocked you
would have found the failure mode `manifest-admission-control.md:40-43` calls the self-protection
gap; it is not blocked here because the post's rule is scoped to `namespaces`.

Step 9 — `namespace/probe created`, with the webhook configuration still registered and still
`failurePolicy: Fail`. The webhook was skipped, not called and not failed.

Step 10 — the explicit rule is accepted **with** a warning that the rule has no effect; the wildcard
rule is accepted silently. Both webhooks are registered and neither will ever see a
SubjectAccessReview.

Step 11 — the six-replica dry run is denied with a message of the form `ValidatingAdmissionPolicy
'demo-policy.example.com' with binding 'demo-binding-test.example.com' denied request: failed
expression: object.spec.replicas <= 5` (`validating-admission-policy.md:85-87`); the four-replica
dry run reports `deployment.apps/four created (server dry run)`.

Step 12 — the `v1alpha1` binding does not create anything on a default cluster. Whether the error
names the version or the kind tells you which of the two claims in this step is stale prose and
which is a live API question.

Step 13 — six resource names including `mutatingadmissionpolicies`, from a group whose reference
list of admission controllers does not mention the kind.

Step 14 — a non-zero count for the rejection-count metric line, and no `PodNodeSelector` in the API
server's arguments. It is disabled by default and kubeadm does not enable it.

**Read on** — four questions. Three are answerable from the pinned tree; the fourth is the one to
carry.

1. `manifest-admission-control.md:341` cites KEP-5793 for manifest-based admission control. Read
   the three limitations of API-registered admission at `:31-47` and ask which of them the post's
   own manifest is an instance of — it registers a webhook whose `clientConfig` points at the
   `kubernetes` Service in `default`, so the webhook that gates namespace creation is reached
   through the same API server whose availability it depends on.
2. `extensible-admission-controllers.md:1082-1121` is the replacement for the post's sentence about
   webhook names being sorted. Read the section and ask why `reinvocationPolicy` defaults to
   `Never` when the problem it solves — a mutating webhook not seeing a later webhook's changes —
   is the exact problem the post's ordering advice was for.
3. `admission-webhooks-good-practices.md:398-418` tells you to set `failurePolicy: Ignore` on
   mutating webhooks and validate the final state separately. The post says *"Failing open makes
   for unpredictable behavior for all clients"*, and v1 made `Fail` the default
   (`extensible-admission-controllers.md:1154`). Both are in the pin. Work out what distinction
   reconciles them, and which of the two the post's own `ValidatingWebhookConfiguration` falls
   under.
4. The unanswerable one. The post's recommended topology — the webhook as an aggregated extension
   API server — is not deprecated anywhere in the pinned tree, is not argued against anywhere, and
   is not mentioned. `admission-webhooks-good-practices.md` is 651 lines of deployment advice for a
   shape the post called *"a lot of effort"*. Nothing in the pin records a decision to stop
   recommending aggregation; the recommendation simply is not there. Whether it was withdrawn, or
   whether the page that would have carried it was written by people who had never read this post,
   is not in the pinned tree. It is the difference between a plan the project abandoned and a plan
   the project forgot, and the archive can tell you which only by not finding it.

Sibling exercises worth reading first, both backward: RBAC went GA one release before this post
([`../2017/06-using-rbac-generally-available-18.md`](../2017/06-using-rbac-generally-available-18.md)),
and admission runs after authorization, so the `authorizer` CEL variable in step 9's mechanism and
the `attest` permission the v1.37 token mechanism requires are both RBAC objects. And the post's
fourth use case — blocking particular image SHAs — was already a forecast in 2016
([`../2016/08-security-best-practices-kubernetes-deployment.md`](../2016/08-security-best-practices-kubernetes-deployment.md)),
where it appears as *"image authorization plugins (expected in Kubernetes 1.4)"* with a link to an
open pull request. Reading them in order gives you the same feature promised in 2016, offered as a
use case in 2018, and still an off-by-default file-configured plugin at the pin.

**Teardown** — leave the cluster up. The next exercise in this year's table needs a worker node, so
`solo` goes away when you get there; until then this cluster is the cheapest place to keep poking at
admission. Delete every object this exercise created first — both webhook
configurations, the policy, the binding and the `environment` label on `default` — because a
`failurePolicy: Fail` webhook left registered will make the next exercise's first `kubectl apply`
fail for a reason that has nothing to do with storage:

```
kubectl delete validatingwebhookconfiguration --all
kubectl delete validatingadmissionpolicybinding demo-binding-test.example.com
kubectl delete validatingadmissionpolicy demo-policy.example.com
kubectl label namespace default environment-
```

When you are done with `solo` entirely, [tear it down](../../strands/lab-topologies.md#teardown).
