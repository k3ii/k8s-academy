<a id="openapi-v3-field-validation-ga"></a>

# Every claim this post makes about the wire is still exact and both gates that carried those claims have been deleted, its account of when its own subject reached alpha is two releases out, and the level it never demonstrates is the one that still reproduces the outage it opens with

**Post** — [Kubernetes 1.27: Server Side Field Validation and OpenAPI V3 move to GA](https://kubernetes.io/blog/2023/04/24/openapi-v3-field-validation-ga/),
2023-04-24.

134 lines, 5,697 bytes, by Jeffrey Ying and Antoine Pelisse, both of Google. Two features, two
graduations, one announcement — and at the pin both of the gates that carried them have been deleted
from the tree, while every sentence the post writes about what travels over the wire is still
literally true.

**As written**

The post opens with an outage. Before v1.8, `:11-15` says, a typo like forgetting the trailing s in
`replica: 1000` *"could cause an outage, because the value would be ignored and missing, forcing a
reset of replicas back to 1"*. The fix was to fetch the OpenAPI v2 document in `kubectl` and check
fields against it before applying. Then CRDs arrived. The validation code had been written when they
did not exist, and `:19-22` says its inflexibility *"forced some hard decisions in the way CRDs
exposed their schema, leaving us in a cycle of bad validation causing bad OpenAPI and vice-versa"*.
The two graduations announced here are offered as the end of that cycle.

Two histories are given, one per feature. Server Side Field Validation *"was added to Kubernetes in
v1.25, beta in v1.26 and is now GA in v1.27"* and *"provides all the functionality of kubectl
validate on the server side"* (`:25-28`). OpenAPI V3 *"was added in Kubernetes in v1.23, moved to
beta in v1.24 and is now GA in v1.27"* (`:35-37`).

The mechanics are four paragraphs. `:63-70` gives the three endpoint forms — a discovery root, a
per-group-version document, and the legacy group's document. `:79-82` names the query parameter,
`fieldValidation`, and says that if it is not passed the server is in `Warn` mode. `:84-87` lists
the three levels: *Strict* errors on failure, *Warn* returns the same findings as warnings and does
not fail, *Ignore* performs no server-side validation at all. `:89-91` says `kubectl` *"will skip
client side validation and will automatically use server side field validation in `Strict` mode"*
while *"Controllers by default use server side field validation in `Warn` mode"*. `:93-95` explains
why the old client had to be generous: *"we had to be extra lenient because some fields were missing
from OpenAPI V2 and we didn't want to reject possibly valid objects"*.

It closes forward. `:101-106` offers a guarantee — *"we guarantee a full lossless schema published
by OpenAPI"* — so that clients are *"free to implement their own validation if necessary (to 'shift
things left')"*, and `:108-111` names what was still coming: CEL validation and admission, *"along
with OpenAPI annotations on built-in types"*.

**As it runs now**

*Both switches are gone, and the behaviour is unconditional.* `ServerSideFieldValidation.md` and
`OpenAPIV3.md` both carry `removed: true` at file level. Nothing on the command line turns either
feature on or off, and step 1 confirms the server reports no `kubernetes_feature_enabled` row under
either name.

*Everything the post says about the wire is still exact.* `api-concepts.md:1250` still calls the
parameter `fieldValidation`. `api-concepts.md:1228-1230` still lists `Ignore`, `Warn` and `Strict`
and still marks `Warn` as the server's default. `api-concepts.md:1266-1270` still gives `kubectl` a
`--validate` flag whose default is strict. Three years on, a reader can take the post's paragraph
and type it.

*Two things the pin documents that the post never mentions.* The first is duplication.
`api-concepts.md:1214-1222` says there are two situations in which the API server drops fields you
supplied: the field is not in the schema, or *"the field is duplicated in the object"*, and the
section heading at `:1224` names both — *Validation for unrecognized or duplicate fields*. The post
speaks only of the first. The second is a hole in the reporting. `api-concepts.md:1252-1257` says
that if a request carries an unrecognised field *and* is invalid for some other reason, the server
answers 400 and *"will not provide any information on unknown or duplicate fields (only which fatal
error it encountered first)"* — and `:1259` adds that this happens *"no matter what field validation
level you requested"*. The level you chose stops mattering exactly when there is more than one thing
wrong.

*Where the pinned documentation disagrees with itself.* The successor mechanism has four metric
names for two counters. `declarative-validation.md:33` and `:100` tell an administrator to watch
`declarative_validation_mismatch_total` and `declarative_validation_panic_total`, and the two gate
files repeat those names — `DeclarativeValidation.md:20` and
`DeclarativeValidationTakeover.md:25-26`. The metrics reference publishes neither. `metrics.md:399`
and `:406` carry `apiserver_validation_declarative_validation_mismatch_total` and
`apiserver_validation_declarative_validation_panic_total` at BETA; `metrics.md:1645` and `:1652`
carry `apiserver_validation_declarative_validation_panics_total` — plural — and
`apiserver_validation_declarative_validation_parity_discrepancies_total` at ALPHA, the second
described as *"Number of discrepancies between declarative and handwritten validation"* against the
BETA counter's *"Number of times declarative validation results differed from handwritten validation
results"*. Cite both halves; a command settles this one, and it is step 8. A second disagreement the
lab cannot settle sits beside it: `declarative-validation.md:25` says `DeclarativeValidation` is
*"GA in v1.36, Default: `true`, LockToDefault: `true`"*, and `DeclarativeValidation.md` writes no
`locked:` key at all.

**What this exercise does not cover, and where it lives**

The `--validate` flag as a `kubectl` user meets it — strict rejecting an unknown field where warn
prunes it, and what a pruned field costs — belongs to the exercise on [the RBAC rule naming an API
group that now serves nothing](../2017/06-using-rbac-generally-available-18.md), which works that
split through three manifests. The OpenAPI endpoints themselves, the hash in the group-version URL,
the losses the v2 conversion takes and the pin's warning that a published schema is not a complete
account of what the server enforces all belong to [the endpoint that has moved
twice](../2016/15-kubernetes-supports-openapi.md). Neither gate is laddered here: `OpenAPIV3` is
transcribed in that same 2016 exercise, and `ServerSideFieldValidation` in the one on [the gate that
is absent because the feature can no longer be switched
off](../2019/01-apiserver-dry-run-and-kubectl-diff.md). Nothing here re-ladders either.

**The diff, and why**

***Still right.*** This is the dominant case and it deserves saying first. The parameter name, the
three level names, the server default, the client default and the sentence about controllers are all
still accurate at the pin. Steps 2 and 6 are there to confirm it rather than to catch it out.

***Wrong when it was published.*** The post gets its own subject's history wrong, in the paragraph
that announces it. `ServerSideFieldValidation.md` records alpha from v1.23 to v1.24, beta from v1.25
to v1.26, stable from v1.27 to v1.31. The post's *"added to Kubernetes in v1.25"* is the release the
gate reached beta, two after it was added; *"beta in v1.26"* is the second release of a beta that
had already run one; only *"is now GA in v1.27"* is right. In the paragraph that follows, the
OpenAPI V3 history at `:35-37` matches `OpenAPIV3.md` exactly — alpha v1.23, beta v1.24, stable
v1.27. Two histories, side by side, written for the same announcement, and one of them is off by two
releases. The same paragraph offers *"all the functionality of kubectl validate"*; there is no
`kubectl validate` subcommand at the pin, and the only other occurrence of that string in the whole
archive is a 2015 release note proposing it as a cluster health check.

***Retired by being agreed with.*** Both gates are `removed: true`. Nobody argued the behaviour back
out; it simply stopped being optional and the switches were deleted. The residue is visible:
`api-concepts.md:1226` still stamps its field-validation section with a `feature-state` shortcode
naming `ServerSideFieldValidation`, and `kubernetes-api.md:204` still stamps its OpenAPI V3 section
with one naming `OpenAPIV3`. Two live pages wear badges cut from gate files that are marked removed
and set `render: false`.

***Never absorbed.*** What vanished is not a mechanism but the explanation joining the post's two
halves — that CRDs arrived after a client-side validator written on the assumption they never would,
and that the resulting leniency is why the schema itself had to be republished. Four measurements
place it. No file under `content/en` cites this post. The string `lenien` occurs nowhere under
`docs`. The field-validation section of `api-concepts.md`, running `:1200-1286`, says *OpenAPI*
exactly once, at `:1219`, and never names a version of it. And `kubernetes-api.md`, the page that
owns OpenAPI at the pin, contains no occurrence of `fieldValidation` or of the phrase *field
validation* at all. The two subjects this post welded into one announcement are now documented on
two pages that do not mention each other's, and the weld — the reason they were ever one story — is
written down nowhere.

What the post's closing paragraph pointed at did arrive, and it is what this exercise ladders.
*"OpenAPI annotations on built-in types"* became Go comment tags compiled by a generator, and
`api-concepts.md:1283-1286` places that mechanism as the continuation of the very section the post
sends you to — *"Starting from v1.33, Kubernetes offers a way to define field validations using
declarative tags"*. It arrived with three gates.

`DeclarativeValidation`

| stage | default | locked | releases |
|---|---|---|---|
| beta | `true` | — | v1.33 – v1.35 |
| stable | `true` | — | v1.36 – |

`DeclarativeValidationBeta`

| stage | default | locked | releases |
|---|---|---|---|
| beta | `true` | — | v1.36 – |

`DeclarativeValidationTakeover`

| stage | default | locked | releases |
|---|---|---|---|
| beta | `false` | — | v1.33 – v1.35 |
| deprecated | `false` | — | v1.36 – |

None of the three writes a `locked` key and none carries `removed: true`, so all three are still
listed and none is pinned to its default by the file. The third is one of 44 gates of 487 whose
stages include a `deprecated` stage, and one of the 14 of those 44 that are not also removed: its
body says it is deprecated in favour of `DeclarativeValidationBeta` and that it *"can still be set
to prevent 'gate not recognized' errors"*. Read the three tables against the release your lab is on.
Your cluster runs v1.35, which is the last release of the first gate's beta, the release before the
second gate exists at all, and the last release in which the third does anything — so of the three
rows in the family, your server should recognise exactly two, and one of them should be off.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — a single fresh node. Everything here happens at the
API server; there is no storage, no workload and no second node. Provision with
[`provision`](../../strands/lab-topologies.md#provision) and the [node
baseline](../../strands/lab-topologies.md#node-baseline-steps), then `ssh zain@10.10.10.180`. Steps
1 to 9 run on the node; step 10 runs offline against a checkout of the pinned website tree. Step 9
edits the API server's static Pod manifest, and the restore is in Teardown.

**Do**

1. What the server knows these two names to be. Ask it for both of the post's gates, then for the
   family that replaced them.

   ```sh
   kubectl version -o json | python3 -c 'import json,sys;print(json.load(sys.stdin)["serverVersion"]["gitVersion"])'
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' \
     | grep -Ei 'serversidefieldvalidation|openapiv3' || echo "neither of the post's gates is reported"
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' \
     | grep -i declarativevalidation || echo "no declarative validation gate is reported"
   ```

2. The three levels, asked for by name. Send the same unknown field four times, once with no
   parameter and once at each level, straight at the API so that no client default stands between
   you and the answer.

   ```sh
   for LV in none Warn Strict Ignore; do
     Q=""
     if [ "$LV" != none ]; then Q="?fieldValidation=$LV"; fi
     LC=$(echo "$LV" | tr 'A-Z' 'a-z')
     printf '{"apiVersion":"v1","kind":"ConfigMap","metadata":{"name":"fv-%s"},"data":{"a":"1"},"datum":{"b":"2"}}\n' "$LC" > /tmp/body.json
     echo "--- $LV"
     kubectl create --raw "/api/v1/namespaces/default/configmaps$Q" -f /tmp/body.json 2>&1 | head -3
   done
   kubectl get cm -o name | grep '^configmap/fv-' || echo "nothing was created"
   ```

   Record the exact warning text and the exact error text. They are the same finding rendered twice,
   and the difference between them is the whole of what *Warn* and *Strict* mean.

3. The half the post never mentions, and the question this exercise is named for. A duplicated key
   is the second thing the API server drops. Send one over the wire as JSON, then send the same
   duplication as YAML through `kubectl apply`, and find out which side of the wire ever sees it.

   ```sh
   printf '{"apiVersion":"v1","kind":"ConfigMap","metadata":{"name":"dup-raw"},"data":{"a":"1"},"data":{"a":"2"}}\n' > /tmp/dup.json
   kubectl create --raw '/api/v1/namespaces/default/configmaps?fieldValidation=Strict' -f /tmp/dup.json 2>&1 | head -4
   cat > /tmp/dup.yaml <<'YAML'
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: dup-apply
   data:
     a: "1"
   data:
     a: "2"
   YAML
   kubectl apply -f /tmp/dup.yaml 2>&1 | head -4
   kubectl get cm dup-apply -o jsonpath='{.data}' 2>/dev/null; echo
   ```

4. The hole in the reporting. One body carrying both an unrecognised field and a fatal type error,
   sent at all three levels. `api-concepts.md:1252-1259` says the level stops mattering here.

   ```sh
   for LV in Ignore Warn Strict; do
     LC=$(echo "$LV" | tr 'A-Z' 'a-z')
     printf '{"apiVersion":"v1","kind":"ConfigMap","metadata":{"name":"both-%s"},"data":{"a":1},"datum":"x"}\n' "$LC" > /tmp/both.json
     echo "--- $LV"
     kubectl create --raw "/api/v1/namespaces/default/configmaps?fieldValidation=$LV" -f /tmp/both.json 2>&1 | head -3
   done
   ```

5. The outage the post opens with, reconstructed. `replica` without its s is an unrecognised field
   on a Deployment. Ask for each level in turn and read the replica count the cluster ends up with.

   ```sh
   cat > /tmp/dep.json <<'JSON'
   {"apiVersion":"apps/v1","kind":"Deployment",
    "metadata":{"name":"replica-typo"},
    "spec":{"replica":1000,
            "selector":{"matchLabels":{"app":"rt"}},
            "template":{"metadata":{"labels":{"app":"rt"}},
                        "spec":{"containers":[{"name":"c","image":"registry.k8s.io/pause:3.10"}]}}}}
   JSON
   for LV in Strict Warn Ignore; do
     echo "--- $LV"
     kubectl create --raw "/apis/apps/v1/namespaces/default/deployments?fieldValidation=$LV" -f /tmp/dep.json 2>&1 | head -3
     kubectl get deploy replica-typo -o jsonpath='{.spec.replicas}' 2>/dev/null && echo " <- replicas"
     kubectl delete deploy replica-typo --ignore-not-found >/dev/null
   done
   ```

6. What `kubectl` puts on the wire for each spelling of `--validate`. `api-concepts.md:1266-1270`
   gives an alias table; read it back off the request instead of off the page.

   ```sh
   for V in "" "--validate=true" "--validate=false" "--validate=strict" "--validate=warn" "--validate=ignore"; do
     echo "--- kubectl apply ${V:-(no flag)}"
     kubectl apply -f /tmp/dep.json $V --dry-run=server -v=8 2>&1 \
       | grep -o 'fieldValidation=[A-Za-z]*' | head -1 || echo "no fieldValidation parameter was sent"
   done
   ```

   Six invocations, five distinct flag values and one absence. Write down how many distinct
   parameter values came back.

7. What the published schema cannot tell a client. Fetch the v3 document for `apps/v1` and read the
   schema for `spec.replicas`, then send a value the schema permits and the server does not.

   ```sh
   kubectl proxy --port=8001 >/dev/null 2>&1 &
   sleep 3
   U=$(curl -s 127.0.0.1:8001/openapi/v3 | python3 -c 'import json,sys;print(json.load(sys.stdin)["paths"]["apis/apps/v1"]["serverRelativeURL"])')
   curl -s "127.0.0.1:8001$U" | python3 -c 'import json,sys;print(json.dumps(json.load(sys.stdin)["components"]["schemas"]["io.k8s.api.apps.v1.DeploymentSpec"]["properties"]["replicas"],indent=1))'
   sed 's/"replica":1000/"replicas":-1/' /tmp/dep.json > /tmp/neg.json
   kubectl create --raw '/apis/apps/v1/namespaces/default/deployments?fieldValidation=Ignore' -f /tmp/neg.json 2>&1 | head -3
   ```

8. Which of the four names the server actually prints. Four names are published for two counters
   across two pages; one grep settles it.

   ```sh
   kubectl get --raw /metrics | grep -o '^[a-z_]*declarative_validation[a-z_]*' | sort -u \
     || echo "the server exposes no metric containing declarative_validation"
   kubectl get --raw /metrics | grep -c '^apiserver_validation' || true
   ```

9. Hand the server the third gate and read what changes. At v1.35 `DeclarativeValidationTakeover` is
   still settable, and its own file warns that *"the exact description of error messages may differ
   between the two approaches"*. Back the manifest up first; the restore is in Teardown and is not
   optional.

   ```sh
   sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/kube-apiserver.yaml.bak
   sudo sed -i '/- kube-apiserver$/a\    - --feature-gates=DeclarativeValidationTakeover=true' /etc/kubernetes/manifests/kube-apiserver.yaml
   sleep 45
   kubectl get --raw /readyz 2>&1 | head -2
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' | grep -i declarativevalidation
   kubectl create --raw '/apis/apps/v1/namespaces/default/deployments?fieldValidation=Ignore' -f /tmp/neg.json 2>&1 | head -3
   kubectl get --raw /metrics | grep -o '^[a-z_]*declarative_validation[a-z_]*' | sort -u || echo "still nothing"
   ```

   Put the error text beside the one step 7 recorded. If the two strings are identical, that is the
   finding, and it is the one the gate exists to produce.

10. Offline. Seven reads against a checkout of the pinned website tree, four of which are the
    measurements the *never absorbed* paragraph rests on.

    ```sh
    cd /path/to/kubernetes/website/content/en
    sed -n '1208,1230p' docs/reference/using-api/api-concepts.md
    sed -n '1252,1274p' docs/reference/using-api/api-concepts.md
    sed -n '12,35p' docs/reference/using-api/declarative-validation.md
    grep -n 'declarative_validation' docs/reference/instrumentation/metrics.md
    cat docs/reference/command-line-tools-reference/feature-gates/ServerSideFieldValidation.md
    grep -rl 'lenien' --include='*.md' docs || echo "lenien: nowhere under docs"
    grep -c 'fieldValidation\|field validation' docs/concepts/overview/kubernetes-api.md || true
    ```

**Expect**

Step 1 should print a v1.35 server, then one silence, then a short list. Neither `OpenAPIV3` nor
`ServerSideFieldValidation` should appear in the second grep, because a removed gate is not a gate
the server has heard of. The third grep is the one to write down: at v1.35, `DeclarativeValidation`
should be present and `true`, `DeclarativeValidationTakeover` should be present and `false`, and
`DeclarativeValidationBeta` should be absent, because it does not exist until v1.36. That is the
family's ladder read off a running server rather than off a table.

Step 2 is the post's paragraph, confirmed. The first two invocations — no parameter, and `Warn` by
name — should behave identically: a warning naming the unknown field `datum`, and a ConfigMap
created anyway. `Strict` should fail with an error carrying the same field name and no object
created. `Ignore` should say nothing at all and create the object. Three ConfigMaps should exist at
the end, `fv-none`, `fv-warn` and `fv-ignore`, and `fv-strict` should not. The default and the level
are the same thing said two ways, which is exactly what `api-concepts.md:1228-1230` claims.

Step 3 is the step this exercise is named for and the one with a genuinely open answer. The JSON
body sent through `--raw` duplicates `data`, and at `Strict` the server has a rule for that —
`api-concepts.md:1222` makes duplication the second of its two drop conditions — so expect the
duplication to be named in the failure. The YAML path is the interesting half: `kubectl` converts
YAML to JSON before anything is sent, and whether the duplicate survives that conversion decides
whether the server is ever given the chance to object. Read the output of the `jsonpath` command. If
it prints the second value with no complaint from either side, then a duplicate key in a YAML
manifest is caught by nobody, and the answer to *which side of the wire* is *neither*. Record what
you see rather than what you expected; this is a measurement, not a prediction.

Step 4 should print the same 400 three times. The body carries an integer where `data` requires a
string and an unrecognised `datum` alongside it, and `api-concepts.md:1252-1257` says the answer
will name only the first fatal error. `datum` should appear in none of the three responses.
`Ignore`, `Warn` and `Strict` should be indistinguishable. This is the one place in the whole
mechanism where asking for strict validation buys you nothing, and it is a note in a box rather than
a line in the level table.

Step 5 is the pre-v1.8 failure reconstructed on a v1.35 cluster. At `Strict` the create should fail
on `spec.replica`. At `Warn` it should warn and create. At `Ignore` it should create in silence. In
both of the cases where the object is created, the replica count should read `1` — the default,
because the field carrying 1000 was dropped before defaulting ran. That is precisely the outage the
post's `:11-15` describes, still available, still one query parameter away. The post says the
problem was solved; what was solved is that you have to ask for it now.

Step 6 should return a table you can lay beside `api-concepts.md:1266-1270`. No flag and
`--validate=true` and `--validate=strict` should all put `fieldValidation=Strict` on the wire;
`--validate=false` and `--validate=ignore` should both put `fieldValidation=Ignore`;
`--validate=warn` should put `fieldValidation=Warn`. Five spellings, three values. Note that the
default here is strict while the server's own default is `Warn` — `api-concepts.md:1262-1264` says
in one sentence that tools set their own defaults, and this is the sentence made visible.

Step 7 is the boundary the post's guarantee does not cross. The schema for `replicas` should come
back as an integer of format `int32` with a description and no `minimum`. Then the create at
`Ignore` — the level that performs no field validation whatsoever — should still be refused, with a
message about `spec.replicas` having to be greater than or equal to zero. Nothing was validated
against the schema and the object was still rejected, because the range check is not in the schema
and never was. A client holding the lossless document the post guarantees cannot reach this answer;
`declarative-validation.md:547` shows the tag that now expresses it, `+k8s:minimum`, whose payload
is documented as *"This field must be greater than or equal to x"*.

Step 8 settles the disagreement. Expect the grep to return the names with the
`apiserver_validation_` prefix or to return nothing at all, and either outcome is an answer: the
names the concept page and the two gate files tell an administrator to watch are not the names the
metrics reference publishes, and the server prints one set or neither. If nothing comes back, that
is not a failure of the command — a counter that has never been incremented may not be registered,
and you have learned that the advice at `declarative-validation.md:43` to act on a high mismatch
rate cannot be followed on a cluster where nothing mismatches.

Step 9 has two possible shapes and both are worth having. The API server may come back healthy with
the gate reported `true`, in which case the `replicas: -1` refusal is now being produced by
generated code rather than hand-written code, and the question is whether the string changed. Or the
static Pod may refuse to start, in which case `/readyz` will not answer and you have learned that a
gate listed as settable at this release is not settable here. Either way the manifest goes back in
Teardown. The gate's own body says declarative validation *"aims for functional equivalence"* while
warning that error descriptions may differ; an identical string is evidence for the first half and a
changed one is evidence for the second.

Step 10 should end with two counts, and they are the load-bearing ones. `grep -rl 'lenien'` should
list no file, and the count of `fieldValidation` and *field validation* in `kubernetes-api.md`
should be `0`. The first says the post's explanation of why the old client had to be generous
survives nowhere in the pinned documentation. The second says the page that owns OpenAPI at the pin
has nothing to say about the parameter this post announced beside it.

**Read on**

1. `api-concepts.md:1276-1281` records that before v1.25 `--validate` was a boolean toggling
   client-side validation on and off. Read it beside `:1266-1270`, which gives `false` as an alias
   for `ignore`. Work out what a script written in v1.24 with `--validate=false` in it does today,
   and whether it is doing what its author meant.

2. `declarative-validation.md:37-49` tells an administrator when to disable
   `DeclarativeValidationBeta` and then describes a downgrade case in which an object accepted by a
   buggy declarative rule can no longer be updated once the gate is turned off. Decide, from the
   three triggers listed at `:41-43`, which of them your cluster could actually observe given what
   step 8 returned.

3. `DeclarativeValidationBeta.md` lists three classes of tag and what each does when the gate is on
   or off, and `declarative-validation.md:61-62` gives the two lifecycle tags. Work out which of the
   three classes a v1.35 server can enforce, and which it can only shadow, and then say what
   `DeclarativeValidationTakeover` was for that the new gate is not.

4. `metrics.md:399-411` and `metrics.md:1645-1657` describe the same subject with four metric names
   at two stability levels, and the ALPHA pair carries a `validation_identifier` label the BETA pair
   does not. Read all four help strings and decide which pair is the replacement for which, then say
   what the label buys an administrator that the unlabelled counter does not.

5. *Unanswerable from the pin.* `api-concepts.md:1272-1274` says `kubectl` falls back to client-side
   validation when it cannot reach an API server that supports field validation, and that
   client-side validation *"will be removed entirely in a future version of kubectl"*. The pin does
   not name that version, and there is no pre-v1.27 server in this topology to make the fallback
   fire. Whether the fallback code is still present in the `kubectl` on your node is not decidable
   from the documentation tree.

**Teardown**

```sh
sudo cp /root/kube-apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml
sleep 45
kubectl get --raw /readyz
pkill -f 'kubectl proxy' || true
kubectl delete cm --ignore-not-found fv-none fv-warn fv-ignore dup-raw dup-apply
kubectl delete deploy --ignore-not-found replica-typo
rm -f /tmp/body.json /tmp/dup.json /tmp/dup.yaml /tmp/both.json /tmp/dep.json /tmp/neg.json
```

Then release the node with the [topology teardown](../../strands/lab-topologies.md#teardown).
