<a id="upcoming-changes-in-kubernetes-1-22"></a>

# The announcement lists eight removals where the guide it links to at the anchor it links to records twelve, its rehearsal recipe omits exactly the three of those it forgot, and the API version at the top of its own list is still what the apiserver sends to webhooks by default

**Post** — [Kubernetes API and Feature Removals In 1.22: Here's What You Need To
Know](https://kubernetes.io/blog/2021/07/14/upcoming-changes-in-kubernetes-1-22/), 2021-07-14, by
Krishna Kilari (Amazon Web Services) and Tim Bannister (The Scale Factory) — 277 lines, 14,618
bytes, published three weeks before the release it warns about. This is the removal notice for the
largest removal event in the archive, and the exercise is not about the twelve APIs it covers.
Almost all of them are walked elsewhere in this sweep, one at a time, in the years they were
introduced. This exercise is about the announcement.

**As written**

The framing arrives in the first nine lines and it governs everything after. `:11-12`: `As the
Kubernetes API evolves, APIs are periodically reorganized or upgraded. When APIs evolve, the old
APIs they replace are deprecated, and eventually removed.` Then the scope, at `:16-19`: `These are
beta APIs that you can use in current, supported Kubernetes versions, and they are already
deprecated. The reason for all of these removals is that they have been superseded by a newer,
stable ("GA") API.` An inline update at `:23-25` points at the release announcement that landed
three weeks later.

The list is at `:34-41`, under a `<!-- sorted by API group -->` comment, and it is eight bullets:
beta `ValidatingWebhookConfiguration` and `MutatingWebhookConfiguration`, beta
`CustomResourceDefinition`, beta `APIService`, beta `TokenReview`, the beta `SubjectAccessReview`
trio, beta `CertificateSigningRequest`, beta `Lease`, and `All beta Ingress APIs (the
extensions/v1beta1 and networking.k8s.io/v1beta1 API versions)`. Immediately beneath, at `:43-45`,
the post hands its reader to the documentation: `The Kubernetes documentation covers these API
removals for v1.22 and explains how each of those APIs change between beta and stable.` The link
carries the anchor `#v1-22`.

`## What to do` at `:47` promises to `run through each of the resources that are affected by these
removals`, and does, as a definition list of eight terms in a different order from the list above —
`Ingress` first, at `:52-72`, with three times the text of any other entry and the post's only
callout box, `ⓘ` at `:69`, telling you to check that every ingress controller you run supports the
v1 API. Each entry names its destination group and the release that destination became available:
v1.19 for Ingress, v1.16 for the webhooks and CRDs, v1.10 for APIService and TokenReview, v1.6 for
the authorization trio, v1.19 for CSR, v1.14 for Lease. The `Ingress` entry also tells you to
abandon the `kubernetes.io/ingress.class` annotation for `.spec.ingressClassName` (`:59-61`) and to
replace the `ImplementationSpecific` path type with `Prefix` or `Exact` (`:66-67`).

`### kubectl convert` at `:127-150` introduces the plugin as `an official plugin that you can
download as part of Kubernetes` and gives it one worked invocation. `### Rehearse for the upgrade`
at `:152-167` is the post's most operational paragraph and the reason it was worth writing: if you
run your own apiserver you can turn the doomed APIs off before you upgrade, with one
`--runtime-config` argument, given in full at `:159` as nine `<group>/<version>=false` pairs. `:161`
adds a parenthetical warning that this `also turns off v1beta1 of EndpointSlice - watch out for that
when you're testing`, and `:164-167` makes the case: you can test your clients, and `you can revert
if you need to without having to plan a more disruptive downgrade`. `### Advice for software
authors` at `:171-190` turns the same technique on addon vendors.

`## Kubernetes API removals` at `:192-235` is the background half, and it is the part of the post
that reads least like an announcement. `:197-201` cites the deprecation policy and states the
promise: the policy `allows for replacing stable ("GA") APIs from Kubernetes. Importantly, this
policy means that a stable API only be deprecated when a newer stable version of that same API is
available.` `:203-205` says why that matters: `if you're using a stable Kubernetes API, there won't
ever be a new version released that forces you to switch to an alpha or beta feature.` Alpha and
beta are described at `:207-213`, and then `:215-224` block-quotes the 2020 beta policy — a
beta-quality API gets `three releases` to reach GA or be replaced by a new beta — and `:226-230`
adds the post's own arithmetic in italics: three releases used to be about nine months, the cadence
then changed to three releases a year, `so the countdown period is now roughly twelve calendar
months`.

`### Looking ahead` at `:237-265` does two things. First, at `:239-247`, a setting: `A future
Kubernetes release will switch to sending TokenReview objects to webhooks using the
authentication.k8s.io/v1 API by default. At the moment, the default is to send
authentication.k8s.io/v1beta1 TokenReviews to webhooks, and that's still the default for Kubernetes
v1.22.` You can opt in early with `--authentication-token-webhook-version=v1`. Second, at
`:252-265`, the next removal wave: v1.25 will stop serving several APIs and will `**remove**
PodSecurityPolicy`, with the official list given as four bullets — beta `CronJob` (`batch/v1beta1`),
beta `EndpointSlice` (`networking.k8s.io/v1beta1`), beta `PodDisruptionBudget` and
`PodSecurityPolicy` (both `policy/v1beta1`). `## Want to know more?` closes at `:267-277` with three
CHANGELOG links and the deprecation policy.

**As it runs now** — the eight bullets are all correct, and the release did exactly what the post
said it would. The interesting part is what the post does not say, and one thing it promises that
has still not happened five years later.

**The post lists eight removals. The page it links to, at the anchor it links to, records twelve.**
`reference/using-api/deprecation-guide.md:166-307` is the `### v1.22` section, and it holds twelve
`####` entries: Webhook resources, CustomResourceDefinition, APIService, TokenReview,
SubjectAccessReview resources, CertificateSigningRequest, Lease, Ingress, IngressClass, RBAC
resources, PriorityClass, Storage resources. The post's eight bullets cover the first eight. The
four it never names as removals are `IngressClass` (`:271-277`), `RBAC resources` (`:279-286` —
ClusterRole, ClusterRoleBinding, Role and RoleBinding at `rbac.authorization.k8s.io/v1beta1`),
`PriorityClass` (`:288-294`, `scheduling.k8s.io/v1beta1`) and `Storage resources` (`:296-306` —
CSIDriver, CSINode, StorageClass and VolumeAttachment at `storage.k8s.io/v1beta1`). IngressClass is
in the post, but only at `:56-58`, as `The related API ... designed to complement the Ingress
concept` — a migration destination, not a thing being taken away.

**The rehearsal recipe omits exactly three of those four.** `:159` is the one complete
`--runtime-config` line anywhere in this archive, and it disables nine group-versions:
`admissionregistration.k8s.io/v1beta1`, `apiextensions.k8s.io/v1beta1`,
`apiregistration.k8s.io/v1beta1`, `authentication.k8s.io/v1beta1`, `authorization.k8s.io/v1beta1`,
`certificates.k8s.io/v1beta1`, `coordination.k8s.io/v1beta1`, `extensions/v1beta1/ingresses` and
`networking.k8s.io/v1beta1`. The last of those covers IngressClass as a side effect, because
IngressClass and beta Ingress shared a group-version. `rbac.authorization.k8s.io/v1beta1`,
`scheduling.k8s.io/v1beta1` and `storage.k8s.io/v1beta1` are absent. A reader who did exactly what
`### Rehearse for the upgrade` says got a clean rehearsal and then an upgrade that stopped serving
three group-versions nobody had told them about.

**The one thing the post says about EndpointSlice is wrong, and it says it twice.** `:161` warns
that turning off `networking.k8s.io/v1beta1` `also turns off v1beta1 of EndpointSlice`, and `:263`
lists `The beta EndpointSlice API (**networking.k8s.io/v1beta1**)` in the v1.25 forecast.
EndpointSlice has never been in that group. `deprecation-guide.md:97` is unambiguous: `The
discovery.k8s.io/v1beta1 API version of EndpointSlice is no longer served as of v1.25`. The record
of that group-version belongs to [the EndpointSlices
exercise](../2020/06-scaling-kubernetes-networking-with-endpointslices.md), which reads it against
the API it announces; what is this post's is the misattribution, and it is the kind of error that a
rehearsal would not catch, because turning off `networking.k8s.io/v1beta1` really does break
something — just not that.

**Seven of the post's eight "available since" versions match the guide exactly. The eighth is
TokenReview.** `:102` says the `authentication.k8s.io/v1` TokenReview API has been `available since
v1.10`; `deprecation-guide.md:220` says `available since v1.6`. Every other destination lines up to
the release — webhooks and CRD at v1.16 (`:175`, `:191`), APIService at v1.10 (`:212`), the
authorization trio at v1.6 (`:228`), CSR at v1.19 (`:236`), Lease at v1.14 (`:253`), Ingress at
v1.19 (`:261`). Four releases is not much of an error and nothing depends on it, but it lands on the
one entry in the list that has another problem.

**The API version at the top of the post's own list is still the default wire format the apiserver
sends to webhooks.** This is the finding. `authentication.k8s.io/v1beta1` TokenReview stopped being
*served* in v1.22, exactly as announced. It is still what kube-apiserver *sends*.
`reference/access-authn-authz/authentication.md:968-969` documents
`--authentication-token-webhook-version` as determining `whether to use
authentication.k8s.io/v1beta1 or authentication.k8s.io/v1 TokenReview objects to send/receive
information from the webhook` and finishes the sentence `Defaults to v1beta1.` The note at
`:1015-1016` says it again: `The Kubernetes API server defaults to sending
authentication.k8s.io/v1beta1 token reviews for backwards compatibility. To opt into receiving
authentication.k8s.io/v1 token reviews, the API server must be started with
--authentication-token-webhook-version=v1.` The post said `A future Kubernetes release will switch`.
The pin is v1.37, fifteen releases after v1.22, and the switch has not happened.

**The v1.25 forecast named four APIs and the release removed seven.** The guide's `### v1.25`
section (`:83-165`) has seven entries: CronJob (`:87`), EndpointSlice (`:95`), Event (`:106`),
HorizontalPodAutoscaler (`:128`), PodDisruptionBudget (`:137`), PodSecurityPolicy (`:148`) and
RuntimeClass (`:158`). The post named four of them, and every one of the four landed — including the
one it got the group wrong for. `events.k8s.io/v1beta1`, `autoscaling/v2beta1` and
`node.k8s.io/v1beta1` are not in the post at all. The pattern from the v1.22 list repeats one
release later and at the same rate: the forecast under-counts, and nothing it does say is wrong
about *whether*.

**The PodSecurityPolicy prediction is the post's most load-bearing sentence and it came true without
qualification.** `:254-257` says the v1.25 release will remove PodSecurityPolicy, `which is
deprecated and won't graduate to stable`, and sends readers to the April 2021 deprecation post.
`deprecation-guide.md:148-156` confirms it in the past tense and adds what the post could not: the
admission controller went too, and the migration target is Pod Security Admission. That
replacement's own arrival is a later row in this same year and belongs to it, so it is named here
and not read.

**The arithmetic the post added in italics is now the rule as written.** The block quote at
`:219-224` gives a beta API `three releases`; the post's note at `:226-230` points out that three
releases stopped meaning nine months once the cadence changed, and calls the real period `roughly
twelve calendar months`. `reference/using-api/deprecation-policy.md:84-85` now states Rule #4a as
`Beta API versions are deprecated no more than 9 months or 3 minor releases after introduction
(whichever is longer), and are no longer served 9 months or 3 minor releases after deprecation
(whichever is longer)`. Both halves carry the parenthesis, and at three releases a year the longer
of the two is always the release count — twelve months, which is the post's figure. The `whichever
is longer` clause is the post's objection, resolved in the post's favour.

**The stability promise holds, and the policy page states it more carefully than the post does.**
`:199-201`'s `a stable API only be deprecated when a newer stable version of that same API is
available` is Rule #3 at `deprecation-policy.md:75-79`, which puts it as a constraint on direction
rather than on availability: `An API version in a given track may not be deprecated in favor of a
less stable API version`, with GA able to replace beta and alpha, beta unable to replace GA. The
other half of the promise is Rule #4a at `:83`: GA versions `may be marked as deprecated, but must
not be removed within a major version of Kubernetes`. The note at `:93` then closes the remaining
gap the post's reader might worry about: `There are no current plans for a major version revision of
Kubernetes that removes GA APIs.`

**One sentence on the policy page is still written in the future tense about a migration this post's
release finished.** `deprecation-policy.md:59-61`: `For historical reasons, there are 2 "monolithic"
API groups - "core" (no group name) and "extensions". Resources will incrementally be moved from
these legacy API groups into more domain-specific API groups.` v1.22 removed the last thing
`extensions/v1beta1` served. The emptiness of that group is measured in [the 1.16 deprecations
exercise](../2019/08-api-deprecations-in-1-16.md); what is left here is the core group, which has
moved nothing and is the half of that sentence step 10 counts.

**The group the post retires survives in the pinned tree as a teaching example, on the page for the
first item in its own list.** `extensions/v1beta1` appears in six files under `content/en/docs`, and
five of them use it as a string rather than an API. The most useful is
`reference/access-authn-authz/extensible-admission-controllers.md:815-836`, which explains
`matchPolicy: Exact` versus `Equivalent` using a request made `via another API group/version (like
extensions/v1beta1)`, and notes at `:836` that `extensions/v1beta1 deployments were first deprecated
and then removed (in Kubernetes v1.16)`. That is the same page a reader of this post's first bullet
has to migrate against, and `deprecation-guide.md:179` records that the v1 webhook API flipped
`matchPolicy` from `Exact` to `Equivalent` by default — so the example and the default change each
explain the other.

**What this exercise does not cover, and where each piece lives.** The twelve APIs are walked
individually, in the years they were announced, and this exercise does not repeat any of them. The
webhook migration — the required `sideEffects` and `admissionReviewVersions`, and the flipped
`failurePolicy`, `matchPolicy` and `timeoutSeconds` defaults — is [the extensible-admission
exercise](../2018/01-extensible-admission-is-beta.md), with the `sideEffects` field itself in [the
dry-run exercise](../2019/01-apiserver-dry-run-and-kubectl-diff.md). The CustomResourceDefinition
refusal and the structural-schema requirement that came with v1 are [the structural-schemas
exercise](../2019/06-crd-structural-schema.md). The `--runtime-config` rehearsal technique, run
rather than read, and `kubectl convert`'s absence from `kubectl` are [the 1.16 deprecations
exercise](../2019/08-api-deprecations-in-1-16.md). The RBAC entry is RBAC's only dated record
anywhere in the tree, and it is read as such in [the RBAC GA
exercise](../2017/06-using-rbac-generally-available-18.md). Ingress's field renames belong to [the
1.18 Ingress exercise](../2020/02-improvements-to-the-ingress-api-in-kubernetes-1-18.md), and the
client warnings that find beta API users belong to [the warnings exercise](../2020/07-warnings.md).
Release facts and the pressure behind each are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

**The diff, and why** — four cases, and the two that matter both concern things the post did not say
rather than things it got wrong.

**Wrong when it was published, twice, and the smaller error is the obvious one.** EndpointSlice's
beta group is misnamed at `:161` and `:263`; it was `discovery.k8s.io/v1beta1` on both dates and the
post's own link target said so. That is a slip. The consequential error is the list: eight bullets
and a rehearsal recipe that between them leave a reader unwarned about three group-versions the
release stopped serving, on a page whose entire purpose is to warn them. Nothing about v1.22 was
uncertain when this was published three weeks ahead of it — the guide entries for RBAC,
PriorityClass and Storage resources describe removals that had been scheduled for releases, and the
post links to the section that holds them. The announcement and its own citation disagree, and the
citation is right.

**Overtaken by stasis, in the strongest form this archive has found.** An API version that a release
stopped serving is still, five years and fifteen releases later, the default version the apiserver
*sends* to webhook authenticators. TokenReview is the fourth bullet of the post's list, so the post
is simultaneously correct that the API was removed and correct that the default had not yet changed
— and its own forecast, `A future Kubernetes release will switch`, is the sentence that aged. Two
pinned pages document `v1beta1` as the default, one of them calling it `backwards compatibility`,
and neither names a release. A removal notice that had to include a paragraph explaining that one of
its removals is still the default for the one thing that produces it is the clearest evidence in the
sweep that *removal* and *disuse* are different events.

**Retired by being agreed with.** The post did not accept the beta countdown as quoted; it added an
italic note that the arithmetic no longer worked, and gave the right figure. The policy page now
carries `whichever is longer` twice, which produces the post's twelve months at the current cadence.
The post's objection is not cited anywhere and does not need to be: it is in the rule.

**Still right, and that is most of it.** All eight bullets. Seven of eight destination releases.
Every claim in `## Kubernetes API removals`, now stated more precisely by the policy page than by
the post. All four v1.25 predictions, including the removal of PodSecurityPolicy and its admission
controller. The `ⓘ` warning at `:69` about ingress controllers, which is the only advice in the post
about software the reader does not control, and the reason the `Ingress` entry is three times longer
than any other. An announcement whose body is accurate and whose list is short is a particular kind
of failure, and it is the one worth an hour.

**No gate** — there is no feature gate anywhere near this post, and there cannot be: an API removal
is not a feature you enable, and nothing in the pin's 487 gate files touches any of the twelve
entries. The instruments are the two pages the post itself cites.
`reference/using-api/deprecation-guide.md` is the record — `## Removed APIs by release` at `:21`,
with `### v1.22` at `:166` and `### v1.25` at `:83`, each entry naming the group-version that
stopped being served and the destination that replaced it.
`reference/using-api/deprecation-policy.md` is the rule — the tracks table, Rule #3 at `:75-79` and
Rule #4a at `:81-90`. Between them they date everything in this exercise, and the only thing they
cannot tell you is what any announcement said, which is why the post is the evidence for its own
omissions and the guide is the evidence for what was omitted.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`, 4096MB, 4
CPUs, 25G. Nothing in this exercise creates an object — every manifest here is refused, which is the
measurement — so there is no workload, no image pull and no second node to want. What the exercise
does need is an apiserver you can read the command line of, which rules out a managed control plane
and is the reason the lab guest exists. If the guest from the previous exercise in this year is
still up, keep it; if you are starting here, bring it up with [the five provision
steps](../../strands/lab-topologies.md#provision), substituting `topology=solo`, then `ssh
zain@10.10.10.180`.

**Do**

1. Ask the cluster about all twelve group-versions the guide's `### v1.22` section names, in the
   guide's order. Four of these are not in the post:

   ```sh
   for GV in admissionregistration.k8s.io/v1beta1 apiextensions.k8s.io/v1beta1 \
             apiregistration.k8s.io/v1beta1 authentication.k8s.io/v1beta1 \
             authorization.k8s.io/v1beta1 certificates.k8s.io/v1beta1 \
             coordination.k8s.io/v1beta1 extensions/v1beta1 \
             networking.k8s.io/v1beta1 rbac.authorization.k8s.io/v1beta1 \
             scheduling.k8s.io/v1beta1 storage.k8s.io/v1beta1; do
     printf '%-40s %s\n' "$GV" \
       "$(kubectl get --raw "/apis/$GV" >/dev/null 2>&1 && echo served || echo 'not served')"
   done
   ```

2. Do what the census row asks: take each row of the post's list, apply the old apiVersion, and
   record the refusal. One manifest at a time, eight of them, minimal on purpose — the name and the
   kind are all the refusal needs:

   ```sh
   while read -r AV KIND; do
     printf 'apiVersion: %s\nkind: %s\nmetadata:\n  name: probe\n' "$AV" "$KIND" \
       | kubectl create -f - 2>&1 | head -1 | sed "s|^|$KIND: |"
   done <<'EOF'
   admissionregistration.k8s.io/v1beta1 ValidatingWebhookConfiguration
   admissionregistration.k8s.io/v1beta1 MutatingWebhookConfiguration
   apiextensions.k8s.io/v1beta1 CustomResourceDefinition
   apiregistration.k8s.io/v1beta1 APIService
   authentication.k8s.io/v1beta1 TokenReview
   authorization.k8s.io/v1beta1 SelfSubjectAccessReview
   certificates.k8s.io/v1beta1 CertificateSigningRequest
   coordination.k8s.io/v1beta1 Lease
   networking.k8s.io/v1beta1 Ingress
   EOF
   ```

3. Now the four the post never names as removals. Same loop, same refusal, and no warning anywhere
   in the announcement that any of these were coming:

   ```sh
   while read -r AV KIND; do
     printf 'apiVersion: %s\nkind: %s\nmetadata:\n  name: probe\n' "$AV" "$KIND" \
       | kubectl create -f - 2>&1 | head -1 | sed "s|^|$KIND: |"
   done <<'EOF'
   networking.k8s.io/v1beta1 IngressClass
   rbac.authorization.k8s.io/v1beta1 Role
   rbac.authorization.k8s.io/v1beta1 ClusterRoleBinding
   scheduling.k8s.io/v1beta1 PriorityClass
   storage.k8s.io/v1beta1 StorageClass
   storage.k8s.io/v1beta1 VolumeAttachment
   EOF
   ```

4. Read the rehearsal recipe rather than running it — running it is [the 1.16
   exercise](../2019/08-api-deprecations-in-1-16.md)'s job. Put the nine group-versions from `:159`
   against the twelve from step 1 and print the difference:

   ```sh
   cat > /tmp/post-159.txt <<'EOF'
   admissionregistration.k8s.io/v1beta1
   apiextensions.k8s.io/v1beta1
   apiregistration.k8s.io/v1beta1
   authentication.k8s.io/v1beta1
   authorization.k8s.io/v1beta1
   certificates.k8s.io/v1beta1
   coordination.k8s.io/v1beta1
   extensions/v1beta1
   networking.k8s.io/v1beta1
   EOF
   cat > /tmp/guide-v122.txt <<'EOF'
   admissionregistration.k8s.io/v1beta1
   apiextensions.k8s.io/v1beta1
   apiregistration.k8s.io/v1beta1
   authentication.k8s.io/v1beta1
   authorization.k8s.io/v1beta1
   certificates.k8s.io/v1beta1
   coordination.k8s.io/v1beta1
   extensions/v1beta1
   networking.k8s.io/v1beta1
   rbac.authorization.k8s.io/v1beta1
   scheduling.k8s.io/v1beta1
   storage.k8s.io/v1beta1
   EOF
   comm -13 <(sort /tmp/post-159.txt) <(sort /tmp/guide-v122.txt)
   ```

5. Send a real TokenReview at the version that survived, then the same one at the version the post's
   list removed. A deliberately invalid token is enough — the answer is in the response, not in the
   verdict:

   ```sh
   cat <<'EOF' | kubectl create -o yaml -f - | grep -A4 '^status:'
   apiVersion: authentication.k8s.io/v1
   kind: TokenReview
   spec:
     token: not-a-real-token
   EOF
   cat <<'EOF' | kubectl create -f - 2>&1 | head -1
   apiVersion: authentication.k8s.io/v1beta1
   kind: TokenReview
   spec:
     token: not-a-real-token
   EOF
   ```

6. Ask the apiserver which TokenReview version it would *send*. The flag is the whole finding, and
   an absent flag is the answer:

   ```sh
   sudo ps -eo args | grep '[k]ube-apiserver' | tr ' ' '\n' \
     | grep 'authentication-token-webhook' || echo "no webhook-version flag set"
   kubectl get --raw /apis/authentication.k8s.io | python3 -m json.tool | grep -A3 versions
   ```

7. Check the post's v1.25 forecast against the cluster — the four it named, then the three it did
   not:

   ```sh
   for GV in batch/v1beta1 discovery.k8s.io/v1beta1 policy/v1beta1 \
             events.k8s.io/v1beta1 autoscaling/v2beta1 node.k8s.io/v1beta1; do
     printf '%-32s %s\n' "$GV" \
       "$(kubectl get --raw "/apis/$GV" >/dev/null 2>&1 && echo served || echo 'not served')"
   done
   kubectl api-resources --api-group=policy
   kubectl get clusterrole 2>/dev/null | grep -i podsecuritypolicy || echo "no PSP clusterrole"
   ```

8. Test the sentence at `:161` directly. It says turning off `networking.k8s.io/v1beta1` takes
   EndpointSlice with it, which requires EndpointSlice to be in that group:

   ```sh
   kubectl api-resources --api-group=networking.k8s.io
   kubectl api-resources --api-group=discovery.k8s.io
   kubectl get --raw /apis/networking.k8s.io/v1 \
     | python3 -c 'import json,sys; print(sorted(r["kind"] for r in json.load(sys.stdin)["resources"]))'
   ```

9. Hold Rule #4a against the cluster. The rule says a beta API version is deprecated no more than
   nine months or three releases after it arrives, whichever is longer — so list every beta the
   apiserver still serves and ask how that squares:

   ```sh
   kubectl version -o yaml | grep -A5 serverVersion
   kubectl api-versions | grep -c beta
   kubectl api-versions | grep beta | sort
   ```

10. Count the other half of the sentence at `deprecation-policy.md:59-61`. It says resources `will
    incrementally be moved` out of both monolithic groups; one of the two is now empty, and this is
    the other:

    ```sh
    kubectl api-resources --api-group='' --no-headers | wc -l
    kubectl api-resources --api-group='' --no-headers | awk '{print $1}' | sort | column -c 100
    kubectl api-resources --no-headers | awk '{print $NF}' | sort | uniq -c | sort -rn | head -5
    ```

**Expect**

Step 1 prints twelve lines and every one of them says `not served`. That is the release doing
exactly what the post promised, and it is also the shape of the problem: the four lines at the
bottom — `rbac.authorization.k8s.io/v1beta1`, `scheduling.k8s.io/v1beta1`, `storage.k8s.io/v1beta1`
and, by sharing a group-version with beta Ingress, `networking.k8s.io/v1beta1`'s IngressClass — are
indistinguishable from the eight above them. The cluster has no idea which removals were announced.

Step 2 prints nine refusals, one per manifest, and they all come from the same place: the client's
RESTMapper, which builds itself from the apiserver's discovery document and cannot find a mapping.
Expect `error: resource mapping not found for name: "probe" ... no matches for kind "..." in version
"..."` on each line. Note that this is a refusal *before the request* — no beta object is rejected
by validation, because there is nothing left to send it to. The guide's per-entry `Notable changes`
lists, which are what validation would object to if the version still existed, are walked in the
exercises named above.

Step 3 prints six more refusals in the same form, and this is the centre of the exercise. Read them
next to the post one more time and confirm that nothing at `:34-41`, nothing in `## What to do`, and
nothing in `:159` mentions Role, ClusterRoleBinding, PriorityClass, StorageClass, VolumeAttachment
or IngressClass. Then work out what a 2021 cluster with beta RBAC manifests in source control would
have experienced: a rehearsal that passed, an upgrade that broke, and an announcement that had
linked them to the page which would have told them.

Step 4 prints exactly three lines: `rbac.authorization.k8s.io/v1beta1`, `scheduling.k8s.io/v1beta1`,
`storage.k8s.io/v1beta1`. `comm -13` shows what is in the guide's twelve and not in the post's nine.
IngressClass does not appear, because `networking.k8s.io/v1beta1=false` disables it along with beta
Ingress — the one of the four omissions the rehearsal would have caught by accident.

Step 5: the v1 TokenReview is accepted, processed, and comes back with a status saying
`authenticated: false` and an error about the token. It is a real API call against a real resource
that the post's list did not remove. The v1beta1 copy of the same three lines is refused by the
mapper, exactly like step 2. Keep both outputs — step 6 is about a third TokenReview that neither of
these commands can produce.

Step 6 is the sentence that did not age. `grep` finds no `--authentication-token-webhook-version` on
the apiserver command line, because no lab tool sets it, which means the default is in force — and
`authentication.md:969` says that default is `v1beta1`. The `--raw` call shows the group serving
`v1` only. So: a webhook authenticator registered against this v1.37 cluster would receive
TokenReview objects with `apiVersion: authentication.k8s.io/v1beta1`, a version this cluster refuses
to serve, refuses to accept in step 5, and stopped serving in the release this post announces. The
post's `A future Kubernetes release will switch` is still pending after fifteen of them, and the pin
names no target release for it.

Step 7: `batch/v1beta1`, `discovery.k8s.io/v1beta1`, `policy/v1beta1`, `events.k8s.io/v1beta1`,
`autoscaling/v2beta1` and `node.k8s.io/v1beta1` all print `not served`. The post predicted the first
three of those group-versions and PodSecurityPolicy; the last three it never mentioned, and they
went in the same release. `api-resources --api-group=policy` returns `poddisruptionbudgets` on
`policy/v1` and no `podsecuritypolicies` row at all, and the ClusterRole grep finds nothing — the
admission controller went with the API, which is more than the post claimed and exactly what
`deprecation-guide.md:150-151` records.

Step 8 settles the misattribution with three commands. `networking.k8s.io` serves `ingressclasses`,
`ingresses`, `ipaddresses` and `servicecidrs` — the exact list depends on your release, and
EndpointSlice is not on it and never was. `discovery.k8s.io` serves `endpointslices`. The JSON print
is the same answer from the discovery document rather than from `kubectl`'s formatting, in case you
suspect the table. The post's parenthetical warning at `:161` was aimed at a real hazard in the
wrong group.

Step 9 is the rule meeting the cluster, and the count is the interesting part. A v1.37 server still
serves a double-digit number of `beta` group-versions — record the number and the list. Rule #4a
does not say a beta cannot exist for long; it says a beta version must be *deprecated* within nine
months or three releases of arriving, and then stops being served nine months or three releases
after that. So every beta on your list is either younger than its deadline or already deprecated and
counting down. Pick one you recognise and try to date it from the pin alone; the guide only records
removals, so for a beta that has not been removed there is often nothing to read.

Step 10 counts the core group: somewhere around fifty resources, the number depending on your
release, with `pods`, `services`, `configmaps`, `secrets`, `nodes`, `namespaces`,
`persistentvolumes` and `events` among them. Nothing has been moved out of it. The third command
groups every resource on the cluster by kind and shows how few of them are in `v1` with no group at
all. Then read `deprecation-policy.md:59-61` once more: `Resources will incrementally be moved from
these legacy API groups into more domain-specific API groups` is present tense about a plan, one of
whose two groups was emptied by the release this post announces and the other of which has not
changed. Whether that is a plan the project abandoned or one it never set a date for is not
something the pin will tell you.

**Read on**

1. `reference/access-authn-authz/extensible-admission-controllers.md:815-836` teaches `matchPolicy:
   Exact` versus `Equivalent` with a worked example built on a group-version that was removed two
   releases before this post — and says so at `:836`. Read it against `deprecation-guide.md:179`,
   which records that v1 flipped the `matchPolicy` default from `Exact` to `Equivalent`. Together
   they explain why migrating a webhook from beta to v1 can change which requests reach it, without
   any rule in the manifest changing.

2. `reference/using-api/deprecation-policy.md:147-203` draws a hypothetical API's whole life as a
   release-by-release table: which versions are served, which is the storage version, and what the
   release notes must say at each step. It is the rule the post block-quotes at `:219-224`, worked
   out in full, and the fastest way to see why a beta that reaches GA still has to be served for a
   while afterwards.

3. Three pieces of this post's subject are read elsewhere and are worth reading in this order. [The
   1.16 deprecations exercise](../2019/08-api-deprecations-in-1-16.md) is the previous removal wave
   and runs the `--runtime-config` rehearsal for real, including what the flag does with a
   granularity the documentation does not offer. [The warnings exercise](../2020/07-warnings.md) is
   the mechanism `deprecation-guide.md:392` sends you to for finding out who is still calling a
   deprecated API — the step this post does not have. [The RBAC GA
   exercise](../2017/06-using-rbac-generally-available-18.md) reads the guide entry for the first of
   this post's four omissions, from the other side.

4. `reference/access-authn-authz/authentication.md:960-1058` is the whole of the webhook token
   authentication contract: the three flags, the requirement that a webhook `must respond with a
   TokenReview object of the same version as the request`, and the two tabbed request bodies — one
   per API version, with the `v1` tab carrying the note that says `v1beta1` is the default. Read it
   as the answer to step 6 and as the reason the default is hard to move: changing it changes what
   every existing authenticator receives.

5. Unanswerable from the pin: why the list stops at eight. The guide records what was removed, never
   what any announcement said, so there is nothing to read about the four omissions as omissions.
   The obvious theory does not survive measurement either — if the missing four were the ones whose
   GA replacements were oldest and therefore least newsworthy, their destination releases would
   cluster early, and they do not: the guide dates IngressClass's v1 to v1.19 (`:275`), RBAC's to
   v1.8 (`:284`), PriorityClass's to v1.14 (`:292`), and the four storage kinds' to anywhere between
   v1.6 and v1.19 (`:301-304`) — the same span as the eight that were named, two of which are v1.6.
   Also unanswerable: which release will switch the TokenReview webhook default, since `A future
   Kubernetes release` at `:240` is the most specific statement anyone has made about it and the pin
   adds nothing.

**Teardown**

This exercise created one thing: two text files in `/tmp`. Everything else was refused, which is the
finding, so the teardown is a check that nothing slipped through:

```bash
rm -f /tmp/post-159.txt /tmp/guide-v122.txt
kubectl get role,clusterrolebinding,priorityclass,storageclass,volumeattachment,ingressclass \
  -A 2>/dev/null | grep -i probe || echo "nothing named probe exists"
kubectl api-versions | grep -c 'v1beta1$'
```

The `grep` should find nothing — every manifest in steps 2 and 3 was refused before it reached the
apiserver. The last count is worth writing next to step 9's: it is the number of `v1beta1`
group-versions a v1.37 cluster still serves, which is the population the next removal notice will be
written about. The guest is untouched and no workload ever ran on it, so leave it up for the next
exercise in this year.
