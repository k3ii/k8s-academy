<a id="crd-structural-schema"></a>

# Every plan this post makes for `apiextensions.k8s.io/v1` was carried out, and the pin now states its three rules as four with one banned keyword traded for another, names the condition reporting violations once in the tree, and misnames the extension that replaces the opt-out

**Post** — [Future of CRDs: Structural Schemas](https://kubernetes.io/blog/2019/06/20/crd-structural-schema/),
20 June 2019, by Stefan Schimanski (Red Hat). 245 lines, 10,704 bytes. Frontmatter carries
`slug: crd-structural-schema`, which is why the URL says nothing about the future of anything; 23 of
this year's 52 posts set a slug that way. No `k8s` version, but the post dates itself repeatedly:
Kubernetes 1.15 at `:39`, `:222` and `:237`, and 1.16 at `:43`.

This is the post that decides what a CustomResourceDefinition is allowed to be, and it is the only
one in the year whose worked example is an attack. It also has the year's worst code fences: eight
YAML blocks, of which four cannot be parsed at all and two more parse into values that are not the
values shown. Both facts matter, because a reader who tries to follow this post by pasting from it
gets errors before they get to the argument, and the argument is sound.

**As written** — an attack, a gap, a definition, an algorithm, three extensions and a plan.

`:10` sets up the history: CRDs arrived "roughly two years ago" storing arbitrary JSON, with only
`kind`, `apiVersion` and `metadata` required to follow the API conventions, and Kubernetes 1.8 gave
them "an optional OpenAPI v3 based validation schema". `:12` names the gap that leaves. Because an
OpenAPI specification describes "only what must be there, not what shouldn't", and may itself be
incomplete, "the Kubernetes API server never knew the complete structure of CustomResource
instances", so kube-apiserver "stores all JSON data received in an API request (if it validates
against the OpenAPI spec). This especially includes anything that is not specified in the OpenAPI
schema."

`:14-33`, under *The story of malicious, unspecified data*, turns that into the exercise's subject.
A CRD for nightly maintenance jobs run as a service user; a submitted object at `:18-27` whose
`spec.shell` appends a line to `/etc/passwd` and which also carries `privileged: true`. `:29`: the
field "is not specified by the operations team. Their controller does not know it, and their
validating admission webhook does not know about it either. Nevertheless, kube-apiserver persists
this suspicious, but unknown field without ever validating it." `:31` says the job is harmless for
now, because the service user cannot write `/etc/passwd`. `:33` is the payload of the whole post:
the team later adds `privileged` support, carefully authorised so that only a few people may create
privileged jobs — "That malicious job though has long been persisted to etcd. The next night
arrives and the malicious job is executed." The vulnerability is a field that was stored before it
meant anything and became meaningful afterwards.

`:35-45`, under *Towards complete knowledge of the data structure*, is the fix and the plan. `:37`:
"we cannot trust CustomResource data in etcd. Without having complete knowledge about the JSON
structure, the kube-apsierver cannot do anything to prevent persistence of unknown data" — with
`kube-apsierver` misspelled. `:39` announces that "Kubernetes 1.15 introduces the concept of a
(complete) structural OpenAPI schema". `:41` says non-structural schemas are reported "in a
`NonStructural` condition in the CRD". `:43` is the plan, and it is exact: "A structural schema for
CRDs in `apiextensions.k8s.io/v1beta1` will not be required. But we plan to require structural
schemas for every CRD created in `apiextensions.k8s.io/v1`, targeted for 1.16."

`:47-120`, under *Structural Schema*, is the definition. `:49-57` gives the core as seven constructs
— `properties`, `items`, `additionalProperties`, `type`, `nullable`, `title`, `descriptions` — the
last written in the plural here and in the singular at `:116`, where the same list is restated.
`:59` adds that "all types must be non-empty, and in each sub-schema only one of `properties`,
`additionalProperties` or `items` may be used." `:63-77` is a structural example; `:79` says why;
`:81` notes that "we leave out `apiVersion`, `kind` and `metadata`. These are implicitly defined for
each object."

`:83` then allows the core to be "enhanced for value validation purposes with nearly all other
OpenAPI constructs", shows one at `:85-106`, and constrains it at `:110-111`: "the last 5 of the
core constructs are not allowed: `additionalProperties`, `type`, `nullable`, `title`,
`description`", and "every properties field mentioned, must also show up in the core (without the
blue value validations)" — a reference to a colour that nothing in the rendered post applies. `:113`
allows `oneOf`, `allOf`, `anyOf` and `not`. `:115-120` restates the whole definition as three
numbered rules, the third carrying two sub-clauses, and `:122-159` makes the same example
non-structural on purpose and keys its three violations to those rules: "rule 2", "rule 3-i", "rule
3-ii".

`:161` is the turn: having shown that a structural schema cannot forbid a field, "the good news is
that we don't have to explicitly attempt to forbid unwanted fields in advance." `:163-196`, under
*Pruning*, says how. `:165` promises pruning by default in `apiextensions.k8s.io/v1` "with ways to
opt-out of it", and shows the beta opt-in at `:167-173`. `:175` requires a structural schema for
pruning to be enabled at all. `:177-183` gives the algorithm's three assumptions and its three
trigger points: API request data, after conversion and admission, and when reading from etcd.
`:185-196` re-shows the malicious object with `privileged` pruned.

`:198-218`, under *Extensions*, adds three vendor extensions for the shapes a structural schema
cannot otherwise express — `intstr.IntOrString`, `runtime.RawExtension` and pure JSON (`:200`).
`x-kubernetes-embedded-resource: true` at `:204`, `x-kubernetes-int-or-string: true` at `:206-214`
with a permitted `oneOf` pattern, and `x-kubernetes-preserve-unknown-fields: true` at `:216-218`,
which "can be combined with `x-kubernetes-embedded-resource`" and which, at the root, restores "the
traditional CRD behaviour that nothing is pruned".

`:220-244` is the conclusion. Three bullets at `:224-226`: structural schemas optional in v1beta1,
pruning requires a structural schema, violations signalled by the `NonStructural` condition. `:228`
and `:235` note that a two-line schema of `type: object` plus
`x-kubernetes-preserve-unknown-fields: true` is itself structural and "will lead to the old
schema-less behaviour". `:237-242` lists four features that from 1.15 onward will require a
structural schema, each with its state: OpenAPI publishing and `kubectl explain` (beta), CRD
conversion (beta), CRD defaulting (alpha), and server-side apply (alpha, "CRD support pending").
`:244` points at the 1.15 documentation.

**As it runs now** — the plan was carried out in full. Every promise at `:43`, `:165` and `:224-226`
is now the documented behaviour of `apiextensions.k8s.io/v1`, and the post's own subject was never
gated: **zero of the pin's 488 feature-gate files mention structural schemas or pruning**. What did
not survive is the naming. Three of the identifiers this post uses are wrong, and the page that
replaced it has an invented one of its own.

**The post's YAML mostly does not parse.** There are eight fenced blocks: `:18-27`, `:63-77`,
`:85-106`, `:124-153`, `:167-173`, `:187-196`, `:208-212` and `:230-233`. Fed to a YAML parser, four
of them fail. `:63-77`, `:85-106` and `:124-153` all fail the same way, on `properties` written
without its colon at `:68`, `:90` and `:128` — the parser reports `while scanning a simple key`.
`:167-173` fails on the bare ellipsis at `:171` with `mapping values are not allowed here`. The four
that do parse include both versions of the malicious object, `:18-27` and `:187-196` — but twelve
lines across the post carry typographic quotes instead of ASCII ones (`:24`, `:25`, `:101`,
`:103-105`, `:139`, `:144`, `:148`, `:152`, `:193`, `:194`), and inside a plain YAML scalar a curly
quote is an ordinary character. Those blocks parse into values that are not the values the post is
showing. The first Do step is to watch this happen rather than take my word for it.

**Three rules became four, and one banned keyword was traded for another.** The post's definition at
`:115-120` is three rules. The pin states it at
`tasks/extend-kubernetes/custom-resources/custom-resource-definitions.md:209-220` as four. Rule 1 is
the post's non-empty-type requirement, now with two written exceptions — nodes carrying
`x-kubernetes-int-or-string: true` or `x-kubernetes-preserve-unknown-fields: true`. Rule 2 is the
post's 3-ii. Rule 3 is the post's 3-i, and its list has changed: the pin forbids `description`,
`type`, `default`, `additionalProperties` and `nullable` inside the junctors, where the post forbids
`additionalProperties`, `type`, `nullable`, `title` and `description`. `title` came out and
`default` went in — which follows, since `default` was not yet a thing a CRD schema could contain
when the post was written. Rule 4 has no counterpart at all: "if `metadata` is specified, then only
restrictions on `metadata.name` and `metadata.generateName` are allowed". The post's advice at `:81`
was to leave `metadata` out; the pin now says what happens if you do not.

**`spec.preserveUnknownProperties` never existed.** The post names the pruning opt-out three times.
At `:172`, inside YAML, it is `preserveUnknownFields: false`, which is right. At `:218` and `:225`,
in prose, it is `spec.preserveUnknownProperties: false`, which is not a field the API has ever had.
Searched across the whole pinned checkout, `preserveUnknownProperties` occurs on exactly those two
lines of this post and nowhere else — not in the API reference, not in the CRD task page, not in any
other blog post in eleven years of archive.

**And `apiextensions/v1beta1` is not an API group.** The opt-in YAML at `:168` reads `apiVersion:
apiextensions/v1beta1`, missing the `.k8s.io`. It is one of the four blocks that does not parse
anyway, so the error a reader hits is the ellipsis on the next line, not this.

**The int-or-string pattern the post permits is not one the pin accepts.** `:206-214` shows
`x-kubernetes-int-or-string: true` beside a `oneOf` of `type: integer` and `type: string`, and calls
the `oneOf` "permitted, though optional". The pin gives two patterns for that extension, at
`custom-resource-definitions.md:483-487` and `:493-499`, and neither is the post's: one is a bare
`anyOf` of `type: integer` and `type: string`, the other an `allOf` wrapping that same `anyOf`. The
page says at `:479-480` that a schema must use "exactly those, without variations in order to
additional fields" — a sentence with its own missing word. The post's `oneOf` is a variation.
Whether the API server actually refuses it is Do step 9.

**The condition that reports violations is named once in the entire documentation tree.**
`NonStructural` appears at `custom-resource-definitions.md:325` and on no other line of
`content/en/docs`. It is not in the API reference's own list:
`reference/kubernetes-api/apiextensions/custom-resource-definition-v1.md:246` says "Types include
Established, NamesAccepted and Terminating". There is a reason to suspect that is not an oversight.
If a structural schema is mandatory at v1, a non-structural v1 CRD should be rejected at admission
rather than accepted and flagged, which would make the condition unreachable for anything created at
v1. Do step 5 tests that, and the answer decides whether `:41` and `:226` are still true or have
quietly become v1beta1-only.

**The reference names a replacement extension that does not exist either.**
`custom-resource-definition-v1.md:84-85` still carries `preserveUnknownFields` as a v1 field and
describes it as "deprecated in favor of setting `x-preserve-unknown-fields` to true in
`spec.versions[*].schema.openAPIV3Schema`". The extension is `x-kubernetes-preserve-unknown-fields`.
`x-preserve-unknown-fields` occurs exactly once in the pinned tree — on that line. So the post gets
the opt-out's name wrong in prose, and the page that outlived it gets the opt-out's replacement
wrong in prose, in the same field's documentation.

**One of the four dependent features is still documented behind a gate that has been removed.**
`:237-242` lists OpenAPI publishing, conversion, defaulting and server-side apply as the features
that will require a structural schema, with defaulting alpha in 1.15.
`custom-resource-definition-v1.md:472-474` still says "Defaulting is a beta feature under the
CustomResourceDefaulting feature gate. Defaulting requires spec.preserveUnknownFields to be false."
`CustomResourceDefaulting` went beta in v1.16, stable in v1.17, and its gate file is marked removed.
Half that sentence is nine releases stale; the other half is the post's argument, still correct.

**What is still exactly right is the part that reads like a story.** `:29-33` — a field nobody
specified, persisted unvalidated, harmless until the day the team implements it — is the reason the
whole mechanism exists, and the pin makes the same case in `custom-resource-definitions.md:334-348`:
CRDs converted up from v1beta1 may lack a structural schema and carry `spec.preserveUnknownFields`
true (`:334-335`), and for those legacy objects `:341-342` states two consequences as bullets:
"Pruning is not enabled." and "You can store arbitrary data." The algorithm's three trigger points
at `:177-183` are still the three; the pin states the effect at `:396` as "By default, all
unspecified fields for a custom resource, across all versions, are pruned", and the sub-tree opt-out
at `:397-398` is the post's `x-kubernetes-preserve-unknown-fields: true`.

**The page's own pasted output is older than the post.** The worked pruning example at
`custom-resource-definitions.md:350-392` shows a created object whose `creationTimestamp` at `:375`
is `2017-05-31T12:56:35Z` and whose uid at `:380` is from the same era — output pasted at least two
years before this post was published and carried unchanged to a 2026 pin. The command above it, at
`:366`, is `kubectl create --validate=false -f my-crontab.yaml -o yaml`;
`reference/kubectl/generated/kubectl_create/_index.md:156-159` gives `--validate` a default of
`strict` since well after that output was captured, so a reader who drops the flag gets a
client-side rejection instead of a pruned object. `:509` has a doubled slash in a link path. The
prose on that page has been maintained; the terminal blocks in it have not.

**What this exercise does not cover, and where it lives.** OpenAPI publishing, `kubectl explain`
against a custom resource, and the `CustomResourcePublishOpenAPI` ladder belong to [the OpenAPI
exercise](../2016/15-kubernetes-supports-openapi.md), which also creates a CRD at
`apiextensions.k8s.io/v1` and points forward to this page's structural-schema section. Server-side
apply, `ServerSideFieldValidation`, `--dry-run` and what `--validate` does on the client are [the
dry-run and diff exercise](../2019/01-apiserver-dry-run-and-kubectl-diff.md); this file uses
`--validate` only where the post's own YAML is the thing being validated. The pin's advice not to
use admission webhooks to validate CustomResource specs — the advice this post's attack story is the
argument for — is [the extensible admission exercise](../2018/01-extensible-admission-is-beta.md).
Conversion webhooks are read here only as a ladder row; nothing in this exercise runs one.

**The diff, and why** — four of the six cases, and the dominant one is the rare one. What happened
to this post is that it was **retired by being agreed with**. `:43` plans mandatory structural
schemas for `apiextensions.k8s.io/v1` "targeted for 1.16"; v1 arrived in 1.16 and
`custom-resource-definitions.md:205-207` now states the requirement in the past tense. `:165` plans
pruning by default at v1 with an opt-out; `:396` states it as the default and `:397-398` gives the
opt-out. `:224`'s "not required in v1beta1" was made moot from a different direction:
`reference/using-api/deprecation-guide.md:189` records that `apiextensions.k8s.io/v1beta1` has not
been served since v1.22, and `:203` adds that `spec.preserveUnknownFields: true` is disallowed when
creating a v1 object at all. There is nothing left of the escape route the post was careful to
leave open, because the version it led out of was withdrawn.

**Still right** is the argument. The attack at `:29-33` is not a 2019 problem that got fixed; it is
the reason the fix is shaped the way it is, and the pin makes the identical case for legacy objects
at `:334-348`. Everything in *Pruning* that is not a version number still describes what the API
server does.

**The post broke** in its code. Four of eight YAML blocks will not parse, two more parse into
mangled values, and the int-or-string pattern it says is permitted is a variation on the two the pin
says are the only ones allowed. None of that was true when it was written — the missing colons and
curly quotes are damage from the rendering pipeline the post passed through, and the `oneOf` was
presumably right in 1.15. The reader still hits all of it.

**Wrong when it was published** is the naming. `spec.preserveUnknownProperties` at `:218` and `:225`
was never a field; the correct `preserveUnknownFields` appears once, at `:172`, inside a block that
does not parse, so the only place the post gets the name right is the one place a reader cannot run.
`apiVersion: apiextensions/v1beta1` at `:168` was never an API group. Both are prose slips rather
than design errors, which is what makes them worth an exercise: the mechanism this post describes is
intact seven years on, and the identifiers it hands you are not.

**The ladder** — the post's own subject has no gate. Searched across all 488 feature-gate files at
the pin, **none** mentions structural schemas or pruning: the requirement arrived attached to an API
version, not to a switch, which is why there is no `--feature-gates` line anywhere in this exercise
and why the only way to observe the change is to try both API versions. Two of the four dependent
features at `:237-242` do have ladders that nothing else in this archive transcribes.

`CustomResourceWebhookConversion`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.13 – v1.14 |
| beta | `true` | — | v1.15 – v1.15 |
| stable | `true` | — | v1.16 – v1.18 |

Body: "Enable webhook-based conversion on resources created from CustomResourceDefinition." Beta in
v1.15 is exactly what `:239` claims for it. Note the length of that beta: one release. It went
stable in v1.16, the same release that made structural schemas mandatory, which is the post's
sentence about conversion requiring a structural schema arriving as a single change rather than two.

`CustomResourceDefaulting`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.15 – v1.15 |
| beta | `true` | — | v1.16 – v1.16 |
| stable | `true` | — | v1.17 – v1.18 |

Body: "Enable CRD support for default values in OpenAPI v3 validation schemas." Alpha in v1.15 is
what `:241` claims. One release at alpha, one at beta, stable by v1.17 — and this is the gate that
`custom-resource-definition-v1.md:473-474` still describes as governing "a beta feature", nine
releases after it stopped doing so and several after it was deleted.

Both files are marked `removed: true` and carry `_build: {list: never, render: false}`, so neither
renders on the website; both were read from the pinned source. Neither sets `lockToDefault`, and
neither repeats a stage, so both climb once and stop — and in both cases stopping meant the gate
file was retained as a tombstone rather than the feature regressing. What the tables cannot show is
that removal of the gate did not remove the requirement: unlike the pid limits in [the PID-limiting
exercise](05-pid-limiting.md), where the gates went and the settings stayed off, here the gate went
and the behaviour became unconditional.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`, 4096MB, 4
CPUs, 25G. Everything this exercise touches is decided inside kube-apiserver before anything is
persisted, so a second node would observe nothing a first does not. No workload runs: the custom
resources created here have no controller, which is the point — the post's malicious object is
dangerous precisely because it sits in etcd waiting for one. What the topology cannot show is the
half of the story that needs time: a field persisted under one schema and executed months later
under another. The nearest this can get is Do step 3 and step 4, which persist an object and then
read it back, and the gap between them is a shell prompt rather than a night.

**Do**

1. Start by finding out that you cannot follow this post by pasting from it. `:63-77` is the post's own
   structural example; it is reproduced here character for character. `:85-106` and `:124-153` fail
   the same way, on the same missing colon, and `:167-173` fails differently:

   ```sh
   cat > /tmp/post-63.yaml <<'EOF'
   type: object
   properties:
     spec:
       type: object
       properties
         command:
           type: string
         shell:
           type: string
         machines:
           type: array
           items:
             type: string
   EOF
   kubectl create --dry-run=client -f /tmp/post-63.yaml 2>&1 | head -4
   cat > /tmp/post-167.yaml <<'EOF'
   apiVersion: apiextensions/v1beta1
   kind: CustomResourceDefinition
   spec:
     …
     preserveUnknownFields: false
   EOF
   kubectl create --dry-run=client -f /tmp/post-167.yaml 2>&1 | head -4
   ```

2. Now build the CRD the post is describing, correctly. This is `:63-77` with the colon restored and
   nothing else changed, wrapped in the `apiextensions.k8s.io/v1` envelope the post was planning
   for. Note what is absent from the schema: `privileged`, exactly as in the post's story — the
   operations team has not implemented it yet:

   ```yaml
   # /tmp/mnj-crd.yaml
   apiVersion: apiextensions.k8s.io/v1
   kind: CustomResourceDefinition
   metadata:
     name: maintenancenightlyjobs.blogwalk.example
   spec:
     group: blogwalk.example
     scope: Namespaced
     names:
       plural: maintenancenightlyjobs
       singular: maintenancenightlyjob
       kind: MaintenanceNightlyJob
       shortNames: ["mnj"]
     versions:
     - name: v1
       served: true
       storage: true
       schema:
         openAPIV3Schema:
           type: object
           properties:
             spec:
               type: object
               properties:
                 command:
                   type: string
                 shell:
                   type: string
                 machines:
                   type: array
                   items:
                     type: string
   ```

   ```sh
   kubectl create -f /tmp/mnj-crd.yaml
   kubectl get crd maintenancenightlyjobs.blogwalk.example \
     -o jsonpath='{.spec.preserveUnknownFields}{"\n"}'
   kubectl get crd maintenancenightlyjobs.blogwalk.example \
     -o json | python3 -c 'import sys,json; print([c["type"] for c in json.load(sys.stdin)["status"]["conditions"]])'
   ```

3. Submit the post's malicious object, copied from `:18-27` with the `apiVersion` changed to name the
   group you just created and nothing else touched. Use the pin's own `--validate=false` from
   `custom-resource-definitions.md:366` so that the client gets out of the way and the API server's
   behaviour is what you see:

   ```sh
   cat > /tmp/mnj-object.yaml <<'EOF'
   apiVersion: blogwalk.example/v1
   kind: MaintenanceNightlyJob
   metadata:
     name: nightly
   spec:
     shell: >
       grep backdoor /etc/passwd ||
       echo “backdoor:76asdfh76:/bin/bash” >> /etc/passwd || true
     machines: [“az1-master1”,”az1-master2”,”az2-master3”]
     privileged: true
   EOF
   kubectl create --validate=false -f /tmp/mnj-object.yaml
   kubectl get mnj nightly -o json \
     | python3 -c 'import sys,json; print(json.dumps(json.load(sys.stdin)["spec"], indent=2, ensure_ascii=False))'
   ```

4. Read the same object again through the two things the post's story turns on: whether the field
   survived, and what the post's own typography did to the fields that did. The payload is a shell
   command; look at the characters in it:

   ```sh
   kubectl get mnj nightly -o json \
     | python3 -c 'import sys,json; s=json.load(sys.stdin)["spec"]; print("privileged present:", "privileged" in s); print("machines:", s.get("machines")); print("curly quotes in shell:", sum(s["shell"].count(c) for c in "\u201c\u201d"))'
   ```

5. Delete that object and submit it again without the flag, so the client behaves the way a reader in
   2026 will find it behaving by default. `kubectl`'s own default for `--validate` is `strict`
   (`reference/kubectl/generated/kubectl_create/_index.md:156-159`), which is a different mechanism
   from pruning and produces a different result:

   ```sh
   kubectl delete mnj nightly
   kubectl create -f /tmp/mnj-object.yaml 2>&1 | head -4
   kubectl create --validate=warn -f /tmp/mnj-object.yaml 2>&1 | head -4
   kubectl get mnj nightly -o json \
     | python3 -c 'import sys,json; print("privileged present:", "privileged" in json.load(sys.stdin)["spec"])'
   ```

6. Now the question the post's `:41` and `:226` leave open. Submit the post's deliberately
   non-structural schema from `:124-153`, keeping one instance of each of the three violations it
   names at `:157-159` and nothing else wrong with it, as a v1 CRD — and find out whether v1
   reports it or refuses it:

   ```sh
   cat > /tmp/mnj-nonstructural.yaml <<'EOF'
   apiVersion: apiextensions.k8s.io/v1
   kind: CustomResourceDefinition
   metadata:
     name: badjobs.blogwalk.example
   spec:
     group: blogwalk.example
     scope: Namespaced
     names: {plural: badjobs, singular: badjob, kind: BadJob}
     versions:
     - name: v1
       served: true
       storage: true
       schema:
         openAPIV3Schema:
           properties:
             spec:
               type: object
               properties:
                 command:
                   type: string
                   minLength: 1
               oneOf:
               - properties:
                   command:
                     type: string
                 required: ["command"]
               not:
                 properties:
                   privileged: {}
           required: ["spec"]
   EOF
   kubectl create -f /tmp/mnj-nonstructural.yaml 2>&1 | head -20
   kubectl get crd badjobs.blogwalk.example -o json 2>/dev/null \
     | python3 -c 'import sys,json; print([(c["type"], c["status"]) for c in json.load(sys.stdin)["status"]["conditions"]])' \
     || echo "not created"
   ```

7. Try the API version the post is writing about. `:43` and `:224` are careful to say that structural
   schemas are not required in `apiextensions.k8s.io/v1beta1`, which was true and is now unreachable
   (`reference/using-api/deprecation-guide.md:189`):

   ```sh
   sed 's|apiextensions.k8s.io/v1$|apiextensions.k8s.io/v1beta1|' /tmp/mnj-nonstructural.yaml \
     | kubectl create -f - 2>&1 | head -4
   kubectl api-versions | grep apiextensions
   kubectl api-resources --api-group=apiextensions.k8s.io
   ```

8. Test both names the post gives the opt-out. `spec.preserveUnknownFields: true` is the field that
   exists and that `deprecation-guide.md:203` says is disallowed at v1;
   `spec.preserveUnknownProperties: false` is the name at `:218` and `:225`, which exists nowhere.
   Send each and compare the two failures:

   ```sh
   for FIELD in 'preserveUnknownFields: true' 'preserveUnknownProperties: false'; do
     echo "== $FIELD"
     printf 'apiVersion: apiextensions.k8s.io/v1\nkind: CustomResourceDefinition\nmetadata:\n  name: probes.blogwalk.example\nspec:\n  group: blogwalk.example\n  scope: Namespaced\n  names: {plural: probes, singular: probe, kind: Probe}\n  %s\n  versions:\n  - name: v1\n    served: true\n    storage: true\n    schema:\n      openAPIV3Schema:\n        type: object\n' "$FIELD" \
       | kubectl create --dry-run=server -f - 2>&1 | head -4
   done
   ```

9. Test both names for the pruning escape hatch: the extension the post names correctly at `:216-218`,
   and the one `custom-resource-definition-v1.md:85` says has replaced it. Only one of the two
   occurs anywhere in the pin outside that line:

   ```sh
   for EXT in x-kubernetes-preserve-unknown-fields x-preserve-unknown-fields; do
     echo "== $EXT"
     printf 'apiVersion: apiextensions.k8s.io/v1\nkind: CustomResourceDefinition\nmetadata:\n  name: exts.blogwalk.example\nspec:\n  group: blogwalk.example\n  scope: Namespaced\n  names: {plural: exts, singular: ext, kind: Ext}\n  versions:\n  - name: v1\n    served: true\n    storage: true\n    schema:\n      openAPIV3Schema:\n        type: object\n        %s: true\n' "$EXT" \
       | kubectl create --dry-run=server -f - 2>&1 | head -4
   done
   ```

10. Last, the two patterns. `:206-214` says a `oneOf` of `type: integer` and `type: string` beside
    `x-kubernetes-int-or-string: true` is "permitted, though optional";
    `custom-resource-definitions.md:479-480` says only the two forms at `:483-487` and `:493-499`
    are allowed, "exactly those, without variations". Send both. Then add a `default:`, which needed
    a gate when the post was written, and ask the API server whether it still knows that gate's
    name:

    ```sh
    for FORM in oneOf anyOf; do
      echo "== $FORM"
      printf 'apiVersion: apiextensions.k8s.io/v1\nkind: CustomResourceDefinition\nmetadata:\n  name: intstrs.blogwalk.example\nspec:\n  group: blogwalk.example\n  scope: Namespaced\n  names: {plural: intstrs, singular: intstr, kind: IntStr}\n  versions:\n  - name: v1\n    served: true\n    storage: true\n    schema:\n      openAPIV3Schema:\n        type: object\n        properties:\n          port:\n            x-kubernetes-int-or-string: true\n            %s:\n            - type: integer\n            - type: string\n' "$FORM" \
        | kubectl create --dry-run=server -f - 2>&1 | head -4
    done
    kubectl patch crd maintenancenightlyjobs.blogwalk.example --type=json \
      -p '[{"op":"add","path":"/spec/versions/0/schema/openAPIV3Schema/properties/spec/properties/command/default","value":"/bin/true"}]'
    printf 'apiVersion: blogwalk.example/v1\nkind: MaintenanceNightlyJob\nmetadata:\n  name: defaulted\nspec:\n  shell: /bin/date\n' \
      | kubectl create -f -
    kubectl get mnj defaulted -o jsonpath='{.spec.command}{"\n"}'
    kubectl get --raw /metrics | grep kubernetes_feature_enabled | grep -i customresource
    ```

**Expect**

1. Both files fail before `kubectl` looks at `kind` at all: the error is YAML syntax, not a schema
   complaint. `/tmp/post-63.yaml` fails on the line after `properties`, because without its colon
   `properties` and the key below it read as one scalar; `/tmp/post-167.yaml` fails on the ellipsis.
   Record the exact wording of each — the two errors are different, and neither points at the line a
   reader would suspect.

2. The CRD is created. `spec.preserveUnknownFields` prints empty or `false`: at v1 there is nothing to
   set, because `:165`'s forecast is now the default. The condition list should be `NamesAccepted`
   and `Established`, which is what `custom-resource-definition-v1.md:246` names. `NonStructural` is
   not there, and this schema is structural, so that proves nothing yet — step 6 is the test.

3. The object is created, and the `spec` you read back has `shell` and `machines` and no `privileged`.
   You did not ask for that. This is `:187-196`, and the post's whole argument, working by default
   seven years later on a schema that never mentioned the field.

4. `privileged present: False`. `machines` comes back as three strings, each still carrying a
   typographic quote inside the value, and `curly quotes in shell:` reports 2. Worth sitting with:
   the post's payload, exactly as printed, would append a line containing curly quotes to
   `/etc/passwd`, which is not a line that does what the post says it does. Pruning removes unknown
   fields; it has no opinion about bad values in known ones.

5. Without the flag, `kubectl` refuses the file client-side and names `privileged` as unknown; the
   object is not created. With `--validate=warn` you get the same information as a warning and the
   object is created anyway, pruned. So a reader in 2026 meets two mechanisms where the post
   describes one, and the difference matters: strict validation tells you the field was dropped,
   pruning does not. Record both messages.

6. Genuinely open, and the most interesting step here. Three outcomes are possible. Rejected at
   admission with the violations named: then a non-structural schema cannot exist at v1,
   `NonStructural` is unreachable for anything created at v1, and the fact that the pin names it
   once in the whole tree is explained. Created with a `NonStructural` condition: then `:41` and
   `:226` are still literally true and the condition is simply undocumented. Created silently: then
   the requirement at `custom-resource-definitions.md:205-207` is not enforced where the page says
   it is. Record which, and if the error names rule numbers, record whether they are the post's
   three or the pin's four.

7. `no matches for kind "CustomResourceDefinition" in version "apiextensions.k8s.io/v1beta1"`, and
   `apiextensions.k8s.io/v1` as the only line from `api-versions`. The version this post spends four
   paragraphs being careful about cannot be reached from this cluster.

8. Two different failures, from two different places. `preserveUnknownFields: true` is a real field
   carrying a value `deprecation-guide.md:203` says is disallowed at v1, so expect the rejection to
   come from the server and to say so. `preserveUnknownProperties: false` is not a field at all, so
   expect strict client-side validation to stop it before the server is involved. The post gives the
   second name twice, in prose, in its conclusion.

9. `x-kubernetes-preserve-unknown-fields: true` beside `type: object` should be accepted: that is
   exactly the two-line schema `:230-233` calls valid and structural. `x-preserve-unknown-fields:
   true` should be rejected as unknown. If it is instead accepted, record that, because it would
   mean the name `custom-resource-definition-v1.md:85` tells you to use is accepted and ignored,
   which is worse than being rejected.

10. `anyOf` should be accepted. Whether `oneOf` is rejected is open: the pin says only those two forms
    are allowed and the post says `oneOf` is permitted, and one of them is describing something the
    implementation does not do. Record which. The `default` should come back as `/bin/true` on an
    object that never set `command`, with no feature gate involved anywhere — which is the answer to
    `:241`. The metric grep may print nothing; a removed gate has no reason to appear, and finding a
    `kubernetes_feature_enabled` series for `CustomResourceDefaulting` would be the surprise, not
    the absence.

**Read on** — four of these the pin will answer, and one it will not.

1. Put post `:115-120` beside `custom-resource-definitions.md:209-220` and account for every
   difference: the two exceptions added to rule 1, `title` leaving rule 3's list, `default` joining
   it, and rule 4 appearing from nowhere. Then read post `:81` again and decide whether it is advice
   or a warning.

2. `custom-resource-definitions.md:394-465` works pruning through four examples. Find the one where
   pruning restarts inside a preserved sub-tree for each property that is specified, and work out
   what it means for a schema that specifies `spec` but says nothing about what is inside it.

3. `custom-resource-definitions.md:507-536` on `RawExtension`. `:533-534` says pairing
   `x-kubernetes-embedded-resource` with the preserve extension is optional; `:536` says
   `apiVersion`, `kind` and `metadata` are implicitly specified and validated. Post `:204` says
   those three "are not pruned and are automatically validated". Are those the same claim?

4. Search `reference/kubernetes-api/apiextensions/custom-resource-definition-v1.md` for `NonStructural`
   and note what you find. Then read `:246` and decide whether step 6's outcome explains the absence
   or contradicts it.

5. Unanswerable from the pin: why `preserveUnknownFields` remains a field on the v1 type at
   `custom-resource-definition-v1.md:84-85` at all, when `deprecation-guide.md:203` disallows the
   only value that ever made it do anything. The reference says the field is deprecated and names
   its replacement wrongly; it does not say why the field is still there.

**Teardown** — two CRDs at most were created; the `--dry-run=server` probes in steps 8, 9 and 10
persisted nothing, so nothing needs undoing for those. Deleting a CRD deletes its objects with it:

```sh
kubectl delete crd maintenancenightlyjobs.blogwalk.example --ignore-not-found
kubectl delete crd badjobs.blogwalk.example --ignore-not-found
kubectl get crd | grep blogwalk.example || echo "no blogwalk.example CRDs remain"
rm -f /tmp/post-63.yaml /tmp/post-167.yaml /tmp/mnj-crd.yaml /tmp/mnj-object.yaml /tmp/mnj-nonstructural.yaml
```

Nothing was changed on the node, no kubelet was restarted and no feature gate was set, which is the
shape of an exercise about a requirement that arrived attached to an API version. The one thing
worth keeping is your record of step 6.
