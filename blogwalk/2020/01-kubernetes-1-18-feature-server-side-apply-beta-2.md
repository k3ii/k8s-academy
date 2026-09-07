<a id="Kubernetes-1.18-Feature-Server-side-Apply-Beta-2"></a>

# Of this post's two important limitations one is still conceded in the last note on the feature's own reference page, which two hundred lines earlier builds its longest worked example on that limitation being false, and the other was answered by a flag that page never mentions

**Post** — [Kubernetes 1.18 Feature Server-side Apply Beta
2](https://kubernetes.io/blog/2020/04/01/Kubernetes-1.18-Feature-Server-side-Apply-Beta-2/), 1 April
2020, by Antoine Pelisse (Google). 51 lines and 3,632 bytes, the second-smallest `walk` in 2020's
census. Seven headings, every one of them a question, every one answered in a paragraph: what the
feature is, how it works, why it is beta a second time, how to use it, what it cannot do, what comes
next, and how to help.

It is an announcement with a confession in the middle of it. Read for the announcement it is thin —
one flag and one flag's escape hatch. Read for the confession, and for the two sentences under
*Current limitations*, and it is the only part of the post that still describes the pin. Work it in
that order.

**As written** — the feature is *"an important effort to migrate “kubectl apply” to the apiserver"*
(`:11`), started in 2018 by the Apply working group. Three challenges are given as its motivation
(`:15-19`): that a client wanting to apply *"needs to use the kubectl go code, or they have to shell
out to kubectl"*; that strategic merge-patch, *"the patch format used by kubectl, grew organically
and was challenging to fix while maintaining compatibility with various api-server versions"*; and
that *"some features are hard to implement directly on the client, for example, unions"*. Against
those three, the answer is a new merging algorithm plus field-ownership tracking, both running in
the API server, and conflict detection as the visible payoff (`:22`).

The mechanism is one paragraph (`:25`). The server diffs every update, records which actor changed
which field and when, and stores all of it in `managedFields` in the object's metadata — *"since
objects can have many fields, this field can be quite large"*. On an apply, that record is what
produces conflicts and steers the merge (`:27`).

Then the confession, under *Wasn't it already Beta before 1.18?* (`:29-30`): yes, beta since 1.16,
*"but it didn't track the owner for fields associated with objects that had not been applied. This
means that most objects didn't have the managedFields metadata stored, and conflicts for these
objects cannot be resolved."* With 1.18, *"all new objects will have the managedFields attached to
them and provide accurate information on conflicts."* A beta reissued because the first one did not
do the thing the feature was for.

Using it is two flags (`:33`): `kubectl apply --server-side`, which *"is likely to show conflicts
with other actors, including client-side apply"*, and `--force-conflicts`, *"which will grab the
ownership for the fields that have changed"*.

*Current limitations* (`:35-36`) names two, *"especially with sub-resources"*. First: *"if you apply
with a status, the status is going to be ignored. We are still going to try and acquire the fields,
which may lead to invalid conflicts."* Second: *"we do not update the managedFields on some
sub-resources, including scale, so you may not see information about a horizontal pod autoscaler
changing the number of replicas."*

*What's next?* is two sentences (`:39`): work on the kubectl experience, *"we are trying to make it
the default"*, and improving the migration from client-side to server-side. *Can I help?* (`:42`)
gives the working group's Slack channel, a mailing list — the post's only link — and a fortnightly
Zoom call. The post closes on six names thanked for the beta (`:46-51`).

**As it runs now** — the pin is `kubernetes/website` at `7c76070faf9b19e6a417c446043dbafd10a7aa1d`,
newest release v1.37, and the feature has its own 638-line reference page, `server-side-apply.md`.
Almost everything the post announces is on it. The interesting part is which sentences of the post
it kept, which it dropped, and which it kept and then contradicted.

**The headline became one sentence with no history in it.** `server-side-apply.md:41` opens *Field
management* with *"The Kubernetes API server tracks managed fields for all newly created objects."*
That is the whole of what the post is announcing — the difference between beta 1 and beta 2 —
rendered as a property of the API server with no release attached and no indication that it was ever
otherwise. Nothing on the page says a beta shipped twice.

**The premise that you can go and look at the record is now hedged by a default.**
`server-side-apply.md:93-96` is a note: *"kubectl get omits managed fields by default. Add
`--show-managed-fields` to show `managedFields` when the output format is either `json` or `yaml`."*
That flag is on 64 files at the pin, and 63 of them are generated command references — tables of
flags, no prose. `server-side-apply.md:95` is the only hand-written line in the tree that tells you
the flag exists. The record the post says is there is there; the command the post assumes you will
use to see it has been silently changed under the sentence. What the record contains once you ask
for it, and how the manager names read, is [already
walked](../2019/01-apiserver-dry-run-and-kubectl-diff.md); step 2 measures only the hiding.

**The first challenge was answered by a media type.** `server-side-apply.md:189-201` gives the
protocol: apply bodies are YAML with the media type `application/apply-patch+yaml`, and *"whether
you are submitting JSON data or YAML data, use `application/apply-patch+yaml` as the `Content-Type`
header value"*. `:232-234` adds that every apply must carry a `fieldManager` query parameter, which
is optional for an **update**. So no Go code and no shelling out: a `PATCH`, a header, and a query
parameter. `:206-216` even prints a two-line body — `{"apiVersion": "v1", "kind": "ConfigMap"}` —
and says it *"would make a no-change update, provided that it was sent as the body of a **patch**
request to a valid `v1/configmaps` resource"*. Step 4 sends exactly that body with `curl`.

**The second challenge was answered by naming the algorithm and keeping the old one.** The new merge
is `sigs.k8s.io/structured-merge-diff`, cited once, at `server-side-apply.md:291`, and its tunables
are four markers in a table at `:299-304`: `listType`, `listMapKey`, `mapType`, `structType`.
Meanwhile the thing the post calls organically grown is still doctrine. The task page a reader lands
on for `kubectl apply` — `declarative-config.md`, *Declarative Management of Kubernetes Objects
Using Configuration Files* — runs to 1,076 lines at the pin, says `last-applied` thirty times, and
devotes `:486-618` to *How apply calculates differences and merges changes* plus `:619-804` to how
each kind of field is merged. It mentions server-side apply once, at `:86`, as an implementation
detail of `kubectl diff`.

**The third challenge was answered somewhere else entirely.** Unions exist at the pin, as
`+k8s:unionDiscriminator` and `+k8s:unionMember`, both marked *Stable*, in
`declarative-validation.md:83-84` — a beta mechanism for v1.33 in which API authors write Go comment
tags and a generator, `validation-gen`, compiles them into validation code. The post's complaint was
that unions are *"hard to implement directly on the client"*; the answer was neither the client nor
the merge algorithm but more Go, one layer down. There is no union row in
`server-side-apply.md:299-304` and no `x-kubernetes-union` extension anywhere in the tree.

**The migration itself has three tenses in one documentation tree.**
`labels-annotations-taints/_index.md:1695-1697` is in the past: the `last-applied-configuration`
annotation is *"a legacy mechanism to track changes"* and *"that mechanism has been superseded by
Server-side apply"*. `server-side-apply.md:489-490` is in the subjunctive: the feature *"is meant
both as a replacement for the original client-side implementation of the `kubectl apply`
subcommand"*. And `declarative-config.md` is in the present, for a thousand lines, teaching the
mechanism the first page calls superseded. Three pages, one question, three answers, all current.

**And on the central premise the two pages flatly disagree.** `server-side-apply.md:16-17` opens
*"Kubernetes supports multiple appliers collaborating to manage the fields of a single object."*
`declarative-config.md:995` says *"Kubernetes objects should be managed using only one method at a
time."* The second page then spends `:972-991` on *How to change ownership of a field between the
configuration file and direct imperative writers*, whose two permitted writers are `kubectl apply`
and *"write directly to the live configuration without modifying the configuration file: for
example, use `kubectl scale`"*, and whose procedure for moving a field the other way is dated: *"As
of Kubernetes 1.5, changing ownership of a field from a configuration file to an imperative writer
requires manual steps"* (`:987`). Collaboration between appliers is the feature's first sentence and
a rule violation on the task page. Neither page cites the other.

**Limitation one was answered by a flag the feature's own page never mentions.** `kubectl apply` has
a `--subresource` flag at the pin, `kubectl_apply/_index.md:210-213`, described as *"if specified,
apply will operate on the subresource of the requested object. Only allowed when using
--server-side."* The convention page explains it — `conventions.md:23-33`, under a heading called
*Subresources*: the argument works with *"get, patch, edit, apply and replace"*, and *"only the
`status`, `scale` and `resize` subresources are supported"*, with `kubectl edit` excepted for
`scale`. `update-api-object-kubectl-patch.md:430-512` works a full example of it. The string
`subresource` does not appear once in the 638 lines of `server-side-apply.md`.

**Limitation two is still conceded, in the last note on the page.** `server-side-apply.md:627-632`:
*"Server-Side Apply does not correctly track ownership on sub-resources that don't receive the
resource object type. If you are using Server-Side Apply with such a sub-resource, the changed
fields may not be tracked."* That is the post's second limitation, six years on, generalised from
*scale* to a category and left in place. Note where it sits: at the foot of `## Clearing
managedFields`, four sections past `## Operations in scope for field management` (`:219-235`), which
is the section that undertakes to enumerate where field management applies, gives two operations —
apply and **update** — and says nothing about sub-resources at all.

**And here the pin contradicts itself about that concession.** Two hundred lines before the note,
`server-side-apply.md:393-477` is the page's longest worked example: transferring ownership of
`.spec.replicas` from a user to the HorizontalPodAutoscaler controller. Its whole argument depends
on the HPA's write being tracked. `:431-433` offers the basic solution — *"leave `replicas` in the
configuration; when the HPA eventually writes to that field, the system gives the user a conflict
over it"* — and `:475-477` closes the advanced one: *"whenever the HPA controller sets the
`replicas` field to a new value, the temporary field manager will no longer own any fields and will
be automatically deleted."* The HPA sets `.spec.replicas` through the `scale` sub-resource, and
`scale` does not receive the Deployment object type: `update-api-object-kubectl-patch.md:473` prints
what comes back from such a write, `scale.autoscaling/nginx-deployment patched`. So the note says
the write may not be tracked and the worked example needs it tracked. A command settles it, and it
is step 7.

**One command in the pin cannot run at all.** `management.md:227` tells you to ensure a Deployment
has one replica with `kubectl scale --replicas 1 deployments/my-nginx --subresource='scale'
--type='merge' -p '{"spec":{"replicas": 1}}'`, and prints `deployment.apps/my-nginx scaled`
underneath as though it had. `kubectl scale` accepts none of `--subresource`, `--type` or `-p`: its
flag table, `kubectl_scale/_index.md`, runs from `--all` to `--warnings-as-errors` without them. The
command that does work is `update-api-object-kubectl-patch.md:467`, which is the same arguments
given to `kubectl patch`. The next command on that page, `management.md:238`, names no resource.
Step 8 runs both.

**What this exercise does not cover, and where it lives.** How `managedFields` reads once you have
asked for it, and the two published defaults for `--field-manager`, belong to [the dry-run
post](../2019/01-apiserver-dry-run-and-kubectl-diff.md), which transcribes the `ServerSideApply`
ladder as well; this exercise takes the manager names as given and spends its steps on ownership and
on sub-resources. How the merge markers behave on a custom resource is [walked with the structural
schema](../2019/06-crd-structural-schema.md), and `server-side-apply.md:315-377` is left alone here.
Why an autoscaler decides to change `.spec.replicas` is [walked with
autoscaling](../2016/07-autoscaling-in-kubernetes.md); step 7 writes the field by hand, because a
one-node cluster with no metrics pipeline cannot make the HPA do it.

**The diff, and why** — five cases land, and the shortest section of the post carries two of them.

**Retired by being agreed with.** The announcement — beta 2 tracks ownership for objects that were
never applied — is now `server-side-apply.md:41`, one sentence, present tense, no release number.
The project agreed so completely that it removed the evidence there had ever been a question, which
is why a reader who arrives at the reference page cannot tell that the post exists or what it was
for.

**Still right, and the only part of the post that is.** *Current limitations* is two sentences long
and both are still live: one as a category the feature's own page concedes at `:627-632`, the other
as the reason a flag had to be added to `kubectl apply` to get at a sub-resource on purpose. The
parts of the post that read as substantial in 2020 — the mechanism, the two flags, the three
challenges — are all either institutionalised or rehoused. The part that reads as a footnote is the
part still doing work.

**The post broke, on its own forecast.** *"We are trying to make it the default"* did not happen,
and the pin says so twice over: `kubectl apply`'s `--field-manager` default is the string
`kubectl-client-side-apply` (`kubectl_apply/_index.md:98`), and the task page that teaches apply
never switches. This is not the same as a feature failing. The mechanism went stable in v1.22 and
the gate that carried it was deleted; what did not arrive is the demotion of the thing it was built
to replace.

**A plan the project carried out.** The other half of *What's next* — improving the migration from
client-side to server-side — is `server-side-apply.md:516-565`, two subsections, both directions,
with a caution at `:530-538` naming the exact failure mode: keep the annotation up to date, because
*"if you used `kubectl scale` to update the replicas field after client-side apply, then this field
is not owned by client-side apply and creates conflicts on `kubectl apply --server-side`"*. The
migration path the post promised exists, and the example chosen to warn about it is the sub-resource
from the post's second limitation.

**Overtaken by a different mechanism.** Unions, the third challenge, were delivered by declarative
validation rather than by server-side apply, which means the argument the post makes for its own
existence is now only two-thirds load-bearing. Nothing was abandoned; the work went to a generator.

**The ladder** — the gate is `ServerSideApply`, and its three rows are transcribed in [the dry-run
exercise](../2019/01-apiserver-dry-run-and-kubectl-diff.md), which reached them first and holds
them: alpha at v1.14, beta from v1.16 to v1.21, stable from v1.22 to v1.31, with `removed: true`
under them. Read them there. The reason they are worth going back for is what they cannot say. The
post announces a change in behaviour between v1.16 and v1.18. The ladder has one beta row spanning
v1.16 to v1.21 with `defaultValue: true` on it throughout, so the event the post exists to report is
invisible in the gate's own history — no rung, no default change, no version boundary. A gate
records whether a feature is switched on. It has no way to record that a feature was switched on and
did not yet work.

What the stable row's `toVersion: "1.31"` means exactly is a question the pin answers twice in one
bullet. `feature-gates-removed/index.md:25-26` says the *To* column *"contains the last Kubernetes
release in which you can still use a feature gate"*, which puts the removal in v1.32. The next
clause, `:26-27`, says that if the stage is *"Deprecated"* or *"GA"* then *To* *"is the Kubernetes
release when the feature is removed"*, which puts it in v1.31. The gate is stable, not deprecated,
so both halves of the bullet claim it; the pin is v1.37 and the name is unrecognised either way, so
nothing in the lab can settle which reading the table was built on.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`,
provisioned by the [steps in the topologies note](../../strands/lab-topologies.md#provision). Every
question here is answered by the API server about objects it is holding, and by `kubectl` about its
own flags; the second node would watch. What one node cannot show is the thing the feature is for.
Two appliers here are two invocations of `kubectl` a second apart, driven by the same person, and a
controller that writes a field on a schedule of its own — the case `server-side-apply.md:390-391`
calls out when it recommends controllers always force conflicts — is not reproduced. Step 7 writes
`.spec.replicas` by hand because there is no metrics pipeline to make an autoscaler write it, so
what the step measures is the sub-resource path, not the race.

Nothing in this exercise edits a static pod manifest or restarts a component. Everything runs as
`zain` against the running cluster in one namespace, and the teardown is a namespace deletion and a
killed proxy.

**Do** — ten steps in one namespace on the one node. Steps 5 to 10 reuse the objects steps 1 and 7
create, so run them in order. Two readers are used repeatedly and are set up as shell variables in
step 1; `kubectl -o jsonpath` is no use here, because `managedFields` entries are maps keyed by
field path and `jsonpath` renders a map as Go's `map[...]`.

1. Make a namespace and a manifest, apply it the old way, and look at both records.

   ```
   kubectl create namespace ssa
   cat > /tmp/cm.yaml <<'EOF'
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: house
     namespace: ssa
     labels:
       test-label: test
   data:
     key: some value
   EOF
   OWN='import sys,json; o=json.load(sys.stdin); print("data:", o.get("data")); [print(" ", e["manager"], e["operation"], "subresource="+e.get("subresource","-"), sorted(e.get("fieldsV1",{}).get("f:data",{}).keys())) for e in o["metadata"].get("managedFields",[])]'
   ANN='import sys,json; m=json.load(sys.stdin)["metadata"]; print("annotations:", sorted((m.get("annotations") or {}).keys())); print("last-applied:", (m.get("annotations") or {}).get("kubectl.kubernetes.io/last-applied-configuration","<absent>"))'
   kubectl apply -f /tmp/cm.yaml
   kubectl -n ssa get cm house -o json --show-managed-fields | python3 -c "$OWN"
   kubectl -n ssa get cm house -o json --show-managed-fields | python3 -c "$ANN"
   ```

2. Ask what `kubectl get` shows by default, in both output formats the note names.

   ```
   kubectl -n ssa get cm house -o yaml | wc -l
   kubectl -n ssa get cm house -o yaml --show-managed-fields | wc -l
   for flag in "" "--show-managed-fields"; do
     for fmt in json yaml; do
       printf '%-22s %-5s ' "${flag:--none-}" "$fmt"
       kubectl -n ssa get cm house -o $fmt $flag | grep -c managedFields
     done
   done
   ```

3. Take the object over server-side, change it, and check the claim that the old
   annotation is kept up to date.

   ```
   kubectl apply --server-side -f /tmp/cm.yaml
   kubectl -n ssa get cm house -o json --show-managed-fields | python3 -c "$OWN"
   sed -i 's/some value/other value/' /tmp/cm.yaml
   kubectl apply --server-side -f /tmp/cm.yaml
   kubectl -n ssa get cm house -o json --show-managed-fields | python3 -c "$OWN"
   kubectl -n ssa get cm house -o json | python3 -c "$ANN"
   ```

4. Apply without kubectl. The body is the one the reference page prints; send it three
   ways and read what comes back.

   ```
   kubectl proxy --port=8001 &
   sleep 2
   printf '{\n  "apiVersion": "v1",\n  "kind": "ConfigMap"\n}\n' > /tmp/nochange.json
   B=http://127.0.0.1:8001/api/v1/namespaces/ssa/configmaps/house
   MSG='import json; d=json.load(open("/tmp/out.json")); print("   ", d.get("message", d.get("kind")))'
   for t in application/apply-patch+yaml application/merge-patch+json; do
     printf '%-34s ' "$t"
     curl -s -o /tmp/out.json -w '%{http_code}\n' -X PATCH -H "Content-Type: $t" \
       --data-binary @/tmp/nochange.json "$B?fieldManager=curl"
     python3 -c "$MSG"
   done
   printf '%-34s ' 'no fieldManager'
   curl -s -o /tmp/out.json -w '%{http_code}\n' -X PATCH \
     -H 'Content-Type: application/apply-patch+yaml' \
     --data-binary @/tmp/nochange.json "$B"
   python3 -c "$MSG"
   kubectl -n ssa get cm house -o json --show-managed-fields | python3 -c "$OWN"
   ```

5. Make a conflict, and read what it says.

   ```
   sed 's/other value/alice value/' /tmp/cm.yaml > /tmp/cm-alice.yaml
   kubectl apply --server-side --field-manager=alice -f /tmp/cm-alice.yaml
   ```

6. Resolve it the three ways the page offers, in the reverse of the page's order —
   forcing has to come last, because it ends the conflict for good. Read ownership after
   each.

   ```
   # become a shared manager: apply the value that is already live
   kubectl apply --server-side --field-manager=alice -f /tmp/cm.yaml
   kubectl -n ssa get cm house -o json --show-managed-fields | python3 -c "$OWN"
   # give up the claim: drop the field from alice's copy
   python3 -c 'open("/tmp/cm-none.yaml","w").write(open("/tmp/cm.yaml").read().split("\ndata:")[0])'
   kubectl apply --server-side --field-manager=alice -f /tmp/cm-none.yaml
   kubectl -n ssa get cm house -o json --show-managed-fields | python3 -c "$OWN"
   # overwrite the value and become sole manager
   kubectl apply --server-side --force-conflicts --field-manager=alice -f /tmp/cm-alice.yaml
   kubectl -n ssa get cm house -o json --show-managed-fields | python3 -c "$OWN"
   ```

7. The sub-resource question. Apply a Deployment server-side, write `.spec.replicas`
   through `scale`, and see whether the write is tracked.

   ```
   cat > /tmp/dep.yaml <<'EOF'
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: pause
     namespace: ssa
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: pause
     template:
       metadata:
         labels:
           app: pause
       spec:
         containers:
         - name: pause
           image: registry.k8s.io/pause:3.10
   EOF
   REP='import sys,json; o=json.load(sys.stdin); print("spec.replicas:", o["spec"]["replicas"]); [print(" ", e["manager"], e["operation"], "subresource="+e.get("subresource","-"), "owns-spec.replicas" if "f:replicas" in e.get("fieldsV1",{}).get("f:spec",{}) else "") for e in o["metadata"]["managedFields"]]'
   kubectl apply --server-side -f /tmp/dep.yaml
   kubectl -n ssa get deploy pause -o json --show-managed-fields | python3 -c "$REP"
   kubectl -n ssa scale deployment pause --replicas=3
   kubectl -n ssa get deploy pause -o json --show-managed-fields | python3 -c "$REP"
   ```

8. Run the two commands the pin gives for that same write, one from a concept page and
   one from a task page, verbatim as printed, and then ask for a sub-resource a
   Deployment does not have.

   ```
   kubectl scale --replicas 1 deployments/my-nginx --subresource='scale' --type='merge' -p '{"spec":{"replicas": 1}}'
   kubectl -n ssa patch deployment pause --subresource='scale' --type='merge' -p '{"spec":{"replicas":4}}'
   kubectl -n ssa get deploy pause -o json --show-managed-fields | python3 -c "$REP"
   kubectl -n ssa patch deployment pause --subresource='resize' --type='merge' -p '{"spec":{"replicas":4}}'
   ```

9. Limitation one. Apply a manifest that carries a status, then apply the same file at
   the status sub-resource on purpose.

   ```
   cp /tmp/dep.yaml /tmp/dep-status.yaml
   cat >> /tmp/dep-status.yaml <<'EOF'
   status:
     replicas: 99
     readyReplicas: 99
   EOF
   STAT='import sys,json; o=json.load(sys.stdin); print("status.replicas:", o["status"].get("replicas")); [print(" ", e["manager"], "subresource="+e.get("subresource","-"), "owns-status" if "f:status" in e.get("fieldsV1",{}) else "") for e in o["metadata"]["managedFields"]]'
   kubectl apply --server-side -f /tmp/dep-status.yaml
   kubectl -n ssa get deploy pause -o json --show-managed-fields | python3 -c "$STAT"
   kubectl apply --server-side --subresource=status -f /tmp/dep-status.yaml
   kubectl -n ssa get deploy pause --subresource=status -o json \
     | python3 -c 'import sys,json; print(json.load(sys.stdin)["status"])'
   ```

10. Clear the record two ways, and see which one the API server honours.

    ```
    COUNT='import sys,json; print("entries:", len(json.load(sys.stdin)["metadata"].get("managedFields",[])))'
    kubectl -n ssa patch cm house --type=merge -p '{"metadata":{"managedFields":[{}]}}'
    kubectl -n ssa get cm house -o json --show-managed-fields | python3 -c "$COUNT"
    kubectl apply --server-side -f /tmp/cm.yaml
    kubectl -n ssa patch cm house --type=merge -p '{"metadata":{"managedFields":[]}}'
    kubectl -n ssa get cm house -o json --show-managed-fields | python3 -c "$COUNT"
    ```

**Expect**

Step 1 is the post's headline, visible on a write that never went near server-side apply. The
annotation is there, and so is one `managedFields` entry, on an object created by plain `kubectl
apply -f`. Its `operation` reads `Update` rather than `Apply`, which `server-side-apply.md:126-128`
explains: the value is `Apply` only when *"the request that last changed that field was a
Server-Side Apply patch"*. Record the manager string — the flag's documented default is
`kubectl-client-side-apply` — and note that `subresource` is empty. Beta 2 was the release that made
this entry exist; nothing on the object says so.

Step 2 should print two different line counts and then a four-row table reading `0`, `0`, `1`, `1`.
The note at `server-side-apply.md:93-96` says the flag is needed for `json` or `yaml`, and both
halves of that hold. The post's sentence *"all this information is stored in the managedFields in
the metadata of objects"* is exactly true and no longer sufficient: the information is stored, and
the default view of the object does not have it.

Step 3's first apply should not conflict. `server-side-apply.md:527-528` promises that: *"by
default, field management of the object transfers from client-side apply to kubectl server-side
apply, without encountering conflicts"*. The entry's `operation` should flip to `Apply`, and the
manager string may or may not change with it — that pair is the dry-run exercise's question. What is
this exercise's question is the last line: `server-side-apply.md:554-556` says downgrading back to
client-side works *"because kubectl Server-Side Apply keeps the `last-applied-configuration`
annotation up-to-date if you use `kubectl apply`"*. Read the annotation and record whether it says
`other value`. If it does, the object is carrying two complete records of the same intent, in two
formats, for the benefit of a downgrade.

Step 4 is the first challenge, tested. Record three status codes and three messages. The
`application/apply-patch+yaml` request is the mechanism reached with no Go code at all — a `PATCH`,
a header, and a query parameter. The `application/merge-patch+json` request sends the identical body
down the old path, and what the server does with it is worth writing down beside the first. The
third request omits `fieldManager`, which `server-side-apply.md:232-234` says is required for apply
and optional for **update**; record the code and the message text, because the message is where the
requirement is actually enforced. Then record whether a manager called `curl` appears at all: an
apply that specifies no fields is asking to own nothing.

Step 5 must fail. Record the whole message: how many conflicts it counts, which manager it names,
which field path, which API version it attributes to that manager, and what it suggests you do. This
is the payoff sentence of the post — *"Server-side Apply enables new features like conflict
detection, so the system knows when two actors are trying to edit the same field"* — and step 5 is
the only place in the exercise where you see it in the form a user would.

Step 6 should give three different ownership pictures for one field. Applying the live value makes
both managers own it: `server-side-apply.md:66-68` says *"when two or more appliers set a field to
the same value, they share ownership of that field"*. Dropping the field from alice's copy leaves
the value alone and removes it from alice's entry only — `:162-166`, the resolution the page lists
second. Forcing changes the value, moves the field to alice alone, and removes it from every other
manager's entry (`:155-160`). Read the `data:` line each time as well: two of the three resolutions
leave it untouched, which is the point of listing three.

Step 7 is the exercise. Before the scale write there should be one entry, `kubectl`, `Apply`, no
sub-resource, owning `f:spec.f:replicas`. After `kubectl scale --replicas=3`, `spec.replicas` reads
`3` and the pin has committed to two incompatible predictions about the rest.
`server-side-apply.md:627-632` says the change *"may not be tracked"*. `:431-433` and `:475-477`
require it to be tracked, or the HPA handover they document cannot work. Record which happened:
whether a second entry appeared, whether it carries a `subresource` key and what the key says,
whether `f:spec.f:replicas` moved out of `kubectl`'s entry, and whether the two entries now share
it. Whichever answer the server gives, one of those two passages is wrong, and the exercise is
finished the moment you can say which.

Step 8's first command must fail, and it fails on flag parsing rather than on the missing
Deployment, so the wrong object name never matters. Record which of `--subresource`, `--type` and
`-p` the error names first: `kubectl_scale/_index.md` offers none of the three, and
`management.md:227` prints `deployment.apps/my-nginx scaled` under the command as though it had run.
The second command is the same request routed through `kubectl patch` and should print
`scale.autoscaling/pause patched`, naming the object type the write actually landed on —
`update-api-object-kubectl-patch.md:473` prints the same line. Read `$REP` again and compare it with
step 7: `kubectl scale` and `kubectl patch --subresource=scale` are two front doors to one endpoint,
and whether they leave the same trace is worth knowing. The `resize` request should be refused;
`update-api-object-kubectl-patch.md:509-511` says the API server returns 404 for a sub-resource the
resource does not have, so record the code and whether the message names the resource or the
sub-resource.

Step 9 is limitation one, and every line of it is a record rather than an expectation. Does the
apply with a `status:` block warn, error, or say nothing? Does `status.replicas` become `99`, or
does the field stay whatever the Deployment controller last wrote? Does any manager acquire
`f:status` — the post's *"we are still going to try and acquire the fields, which may lead to
invalid conflicts"*? Then the same file at `--subresource=status`: accepted or refused, and if
accepted, how long `99` survives before the controller writes over it. Write all five answers down,
because the page that owns this feature does not contain the word `subresource` and cannot be
consulted for any of them.

Step 10 should print `entries: 0` and then a number greater than zero.
`server-side-apply.md:616-620` explains both halves: a list containing one empty entry strips the
field entirely, and *"setting the `managedFields` to an empty list will not reset the field. This is
on purpose, so `managedFields` never get stripped by clients not aware of the field."* The record
the post announces can be deleted by any client that knows the trick and cannot be deleted by
accident, and the same page that documents the trick cautions at `:143-146` that you *"should avoid
updating it manually"*.

**Read on** — four questions the pin can answer, and one it cannot.

1. Read `declarative-config.md:486-618` beside `server-side-apply.md:277-313`. The second gives four
   merge-strategy markers; the first describes merging with none of them. Work out which of the four
   has a counterpart in the client-side account, and what the client-side account uses in place of
   the other three.

2. `conventions.md:27-28` says kubectl supports `--subresource` for `status`, `scale` and `resize`.
   `declarative-validation.md:682-712` shows the validation framework learning about sub-resources
   one package tag at a time, with `/status` and `/scale` as its worked pair. Decide from the two
   pages whether those are the same list, and where `resize` gets its entry.

3. The post's third challenge was unions. `declarative-validation.md:715-792` holds the two tags
   that answered it, both `Stable`. Read them, then read the four-row marker table at
   `server-side-apply.md:299-304` and say which row would have to change, and how, for a union to be
   expressible as a merge strategy rather than as a validation rule.

4. `labels-annotations-taints/_index.md:1695-1697` says the annotation mechanism *"has been
   superseded"*. Go through `declarative-config.md`'s thirty mentions of `last-applied` and sort
   them into descriptions of how the old mechanism works and instructions to use it. The ratio
   decides whether *superseded* is a claim about the code or a claim about the documentation.

5. Unanswerable from the pin: `server-side-apply.md:629` scopes its concession to *"sub-resources
   that don't receive the resource object type"*. Nowhere in the tree is there a list of which
   sub-resources those are. `status` takes the object's own type and `scale` takes `autoscaling/v1
   Scale`, but the only place the pin lets that slip is a line of sample output on another page for
   another reason. A reader holding a controller and a sub-resource cannot tell from the
   documentation whether their writes are tracked; step 7 is the only way to find out, and it
   answers for one sub-resource on one resource on one release.

**Teardown** — one namespace, one backgrounded proxy and seven files.

```
kill %1 2>/dev/null; pkill -f 'kubectl proxy --port=8001'
kubectl delete namespace ssa
rm -f /tmp/cm.yaml /tmp/cm-alice.yaml /tmp/cm-none.yaml /tmp/nochange.json /tmp/out.json \
      /tmp/dep.yaml /tmp/dep-status.yaml
kubectl get ns ssa 2>&1 | tail -1
```

No component was reconfigured and no manifest under `/etc/kubernetes/manifests` was touched, so
there is nothing to restore. Take the guest down with the [teardown
steps](../../strands/lab-topologies.md#teardown) when you are done with it.
