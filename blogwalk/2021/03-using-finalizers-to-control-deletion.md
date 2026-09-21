<a id="using-finalizers-to-control-deletion"></a>

# Nine tenths of this tutorial still runs exactly as printed, which is what makes the rest worth an hour: one sentence was already false on the day it published, one field stopped being printed, and the one modern switch that promises to ignore finalizer constraints refuses this object

**Post** — [Using Finalizers to Control
Deletion](https://kubernetes.io/blog/2021/05/14/using-finalizers-to-control-deletion/), 2021-05-14,
by Aaron Alpar (Kasten) — one author, one vendor, and no release announcement attached: 269 lines,
12,396 bytes, no `k8s` version in the frontmatter and none in the body. The census row leaves the
version column empty because there is nothing to put in it. This is a tutorial about a mechanism
that was already old in 2021, and it is the only 2021 post in this year's shelf whose commands you
can run without translating them first.

**As written**

The post opens on a complaint rather than a feature: `Deleting objects in Kubernetes can be
challenging. You may think you've deleted something, only to find it still persists.` Four questions
are listed at `:14-17` — what properties of a resource govern deletion, how finalizers and owner
references impact deletion, how the propagation policy changes the order of deletions, and how
deletion works with examples. Then the constraint that makes the whole thing reproducible, at `:19`:
`all examples will use ConfigMaps and basic shell commands`.

The basic `delete` comes first, as four separate fences at `:27-46` — create a ConfigMap, `get` it,
delete it, `get` it again and read `Error from server (NotFound)`. The prose at `:48` calls that
last result `an HTTP 404 error`, and says `Shell commands preceded by $ are followed by their
output`, which is a convention the post then never uses: not one command in any fence carries a
prompt. A state diagram follows as an image, and the section closes by naming the two things that
complicate the picture — finalizers and owner references.

The definition at `:61` is the one the exercise is built on. Finalizers `are keys on resources that
signal pre-delete operations`, they `control the garbage collection on resources`, and they `are
designed to alert controllers what cleanup operations to perform prior to removing a resource`. Then
the sentence that makes the rest of the tutorial possible: `they don't necessarily name code that
should be executed; finalizers on resources are basically just lists of keys much like annotations.
Like annotations, they can be manipulated.` Two real ones are named at `:65-66`,
`kubernetes.io/pv-protection` and `kubernetes.io/pvc-protection`, both described as preventing
accidental deletion of volumes.

The demonstration at `:72-81` creates a ConfigMap carrying a single finalizer, the bare word
`kubernetes`. The post is explicit about why it chose that word: `The configmap resource controller
doesn't understand what to do with the kubernetes finalizer key. I term these "dead" finalizers for
configmaps as it is normally used on namespaces.` A delete is then issued in the background with
`&`, `jobs` shows it still running, and the object comes back from the API server with
`deletionGracePeriodSeconds: 0`, a `deletionTimestamp`, the finalizer list intact — and, at `:107`,
a `selfLink`. The reading at `:111` is exact: `the object was updated, not deleted`, because
`Kubernetes saw that the object contained finalizers and blocked removal of the object from etcd`.

The way out, at `:116-118`, is a JSON patch that removes `/metadata/finalizers`. The backgrounded
delete then reports `Done` and the object is gone. A second state diagram follows, and `:130` states
the rule: the object `will remain in finalization until the controller has removed the finalizer
keys or the finalizers are removed using Kubectl`.

Owner references are next, at `:134-136`: `properties on resources that specify the relationship to
one another, so entire trees of resources can be deleted`, where `An owner reference consists of a
name and a UID`, they `link resources within the same namespace`, and `it also needs a UID for that
reference to work`. Two experiments follow, both with ConfigMaps and both reproduced character for
character in step 8 below. Deleting the child leaves the parent. Deleting the parent takes both.
`:193` names that `cascade`, says the default is `true`, offers `--cascade=orphan` as the way out,
and then carries an inline correction: `*Update: starting with kubectl v1.20, the default for
cascade is background.*`

The last mechanism is the propagation policy, reached at `:212-231` through `kubectl proxy` and a
`curl -X DELETE` carrying a `DeleteOptions` body. The three values are listed at `:235-237` —
`Foreground: Children are deleted before the parent (post-order)`, `Background: Parent is deleted
before the children (pre-order)`, `Orphan: Owner references are ignored`. The sentence introducing
them, at `:231`, is the one claim in this post that does not survive contact with the post itself:
`Note that the propagation policy cannot be specified on the command line using kubectl. You have to
specify it using a custom API call.`

Then a coda that is in a different register from everything before it. `:241-263` shows how to force
a namespace out of `Terminating` by `PUT`ing to the namespace's `finalize` subresource with
`spec.finalizers` set to `null`, and immediately warns that this `may delete the namespace only and
leave orphan objects within the, now non-exiting, namespace - a confusing state for Kubernetes`. The
Key Takeaways at `:267` close on caution — `there is a reason for adding a finalizer into the code,
so you should always investigate before manually deleting it` — followed by an embedded conference
talk, which is the only part of the post this lab cannot reproduce.

**As it runs now** — almost all of it, and the exceptions are precise enough to be worth naming one
at a time. This is the rare post that the documentation did not overtake, absorb or quietly
contradict; it is the post the documentation points at.

**The tree cites this post, and it is the only blog post the finalizers concept page cites.**
`concepts/overview/working-with-objects/finalizers.md:100` is the whole of that page's whatsnext: a
single bullet reading `Read Using Finalizers to Control Deletion on the Kubernetes blog`. Across the
pinned docs tree the post's slug occurs exactly once, and that is where. 102 files under
`content/en/docs` mention a finalizer — 105 if you count the three feature-gate files — so the
subject is everywhere, and the one place the tree hands a reader off to a blog post for it is the
concept page that defines the word.

**Every sentence of the post's definition is now in the concept page, in the post's own order.**
`finalizers.md:15-18` carries `Finalizers don't usually specify the code to execute. Instead, they
are typically lists of keys on a specific resource similar to annotations` — the post's `:61` with
the hedging removed. `:22-30` turns the post's observed behaviour into three stated guarantees: the
API server adds `metadata.deletionTimestamp`, prevents removal until the `finalizers` field is
empty, and returns `a 202 status code (HTTP "Accepted")`. `:32-38` is the controller loop the post
describes from the outside. And `:40-46` promotes the post's first named example,
`kubernetes.io/pv-protection`, to the page's only worked example.

**The one claim that broke was already broken when it was published, and the post breaks it
itself.** `:231` says the propagation policy cannot be given on the command line. `:193`, two
paragraphs earlier, says the default value of `--cascade` became `background` — a propagation policy
name, as a flag value — as of kubectl v1.20, which the post dates before its own publication. And
`:204` runs `kubectl delete --cascade=orphan`. At the pin the flag takes all three:
`tasks/administer-cluster/use-cascading-deletion.md:61`, `:119` and `:168` give
`--cascade=foreground`, `--cascade=background` and `--cascade=orphan` as the first of two documented
routes, with the post's `curl` as the second.

**The default the post corrected itself about belongs to the client, not to the API.**
`reference/kubectl/generated/kubectl_delete/_index.md:101` is where `background` actually lives:
`--cascade string[="background"]` with `Default: "background"`. The API's own account is different.
`reference/kubernetes-api/definitions/delete-options-v1-meta.md` says of `propagationPolicy` that
`The default policy is decided by the existing finalizer set in the metadata.finalizers and the
resource-specific default policy`. Both sentences are true and they are about different programs.

**One line of the post's printed output is no longer printed.** The YAML at `:95-109` includes
`selfLink: /api/v1/namespaces/default/configmaps/mymap`.
`reference/kubernetes-api/definitions/object-meta-v1-meta.md:92` now reads `Deprecated: selfLink is
a legacy read-only field that is no longer populated by the system`, and says the same thing about
list metadata at `list-meta-v1-meta.md:52`. Everything else in that block — the timestamps, the
grace period, the finalizer list, the `uid`, the `resourceVersion` — comes back unchanged.

**The field the post's `curl` was built to avoid is still deprecated toward a release that happened
nineteen releases ago.** `DeleteOptions` still carries `orphanDependents`, and its description still
reads `Deprecated: please use the PropagationPolicy, this field will be deprecated in 1.7`. That
sentence occurs 136 times across 69 files in the pinned API reference, in a tree whose newest
release is v1.37. The post never mentions the field, which is the right call, and the tree has not
been able to stop mentioning it.

**The three options became two types and an override.**
`concepts/architecture/garbage-collection.md:58-67` says there are `two types of cascading deletion`
and lists Foreground and Background. Orphaning gets its own subsection at `:110-114`, as a behaviour
you override rather than a policy you choose. The API has not changed — `propagationPolicy` still
takes the post's three words — so this is a taxonomy edit, and it is the only place where reading
the pin first would leave you worse prepared for the post than reading the post first.

**The tree names the foreground finalizer twice and spells it two different ways.**
`garbage-collection.md:80-81` says the API server sets `metadata.finalizers` to
`foregroundDeletion`, and `use-cascading-deletion.md:80-94` shows it inside a captured API response,
so that spelling is attested by an actual server. `owners-dependents.md:79` says `it adds the
foreground finalizer`. Step 9 reads the name off your own cluster, which is the only way to settle
it from inside the lab.

**The glossary calls a finalizer a namespaced key; the tree shows three that are not.**
`reference/glossary/finalizer.md:6` and `:13` both say `namespaced keys`, and `finalizers.md:59-60`
sharpens it into a rule: `Custom finalizer names must be publicly qualified finalizer names, such as
example.com/finalizer-name`, and `the API server rejects writes to objects where the change does not
use qualified finalizer names for any custom finalizer`. The word carrying that sentence is
*custom*. The post's `kubernetes` is not custom, and neither are the `foregroundDeletion` and
`orphan` that `use-cascading-deletion.md:87` and `:180` show the server writing by itself. Step 2
walks the boundary with three names.

**Two rules the post demonstrates without stating are now stated.** `finalizers.md:49-55`: once the
deletion timestamp is set the API server `immediately starts to restrict changes to the
.metadata.finalizers field`, so `You can remove existing finalizers ... but you cannot add a new
finalizer`, you `cannot modify the deletionTimestamp`, and `After the deletion is requested, you can
not resurrect this object`. The post's patch works because removal is the one edit still allowed.

**Finalizer ordering is documented now, and the reason is the post's own failure mode.**
`reference/using-api/api-concepts.md:1126-1143` says external controllers may act `at any time, in
any order`, that order is `not enforced between finalizers because it would introduce significant
risk of stuck .metadata.finalizers`, and that the list `is shared: any actor with permission can
reorder it`. The deadlock it describes — one finalizer's owner waiting on a signal from another's —
is the multi-holder version of the single dead key the post invents by hand.

**The owner reference grew a field, a guard and a failure mode.**
`concepts/overview/working-with-objects/owners-dependents.md:33-44` documents
`ownerReferences.blockOwnerDeletion`, set to `true` automatically when a controller writes the owner
reference, and says `A Kubernetes admission controller controls user access to change this field for
dependent resources, based on the delete permissions of the owner`. `:46-62` — repeated word for
word at `garbage-collection.md:40-56` — turns the post's `link resources within the same namespace`
into enforcement: cross-namespace owner references are `disallowed by design`, a namespaced owner
`must exist in the same namespace as the dependent`, and if it does not, `the owner reference is
treated as absent, and the dependent is subject to deletion once all owners are verified absent`.
Since v1.20 a warning Event with the reason `OwnerRefInvalidNamespace` is reported for the invalid
dependent.

**The post's last technique is the only thing in it the tree does not document at all.** The
`finalize` subresource occurs exactly once in `content/en` at the pin, and the occurrence is this
post. No task page, no concept page and no API reference page in the tree shows a reader how to
force a namespace out of `Terminating`, and `finalizers.md:89-96` says the opposite in a note: `In
cases where objects are stuck in a deleting state, avoid manually removing finalizers to allow
deletion to continue ... This should only be done when the purpose of the finalizer is understood
and is accomplished in another way`. That is the post's own Key Takeaways, promoted into the
documentation and then pointed back at the post that carries the recipe it warns you about.

**There is now a gated, permissioned, audited way to ignore finalizers, and it will refuse this
post's object.** `api-concepts.md:1145-1185` adds a *Force deletion* section: the delete option
`ignoreStoreReadErrorWithClusterBreakingPotential`, available `since Kubernetes v1.37` by default,
which `ignores finalizer constraints, and skips precondition checks`. It needs both the **delete**
and **unsafe-delete-ignore-read-errors** verbs on the resource. It applies only to a resource that
`can not be successfully retrieved from the storage` — decryption failure or a decode failure — and
`:1182-1185` closes the door on everything else: `If the user issues a delete request with
ignoreStoreReadErrorWithClusterBreakingPotential set to true on an otherwise readable resource, the
API server aborts the request with an error.` A ConfigMap held by a dead finalizer is perfectly
readable.

**What this exercise does not cover.** The conference talk embedded at `:269` is outside the pin's
text. The two state diagrams are images, and this lab replaces them with the API responses they
draw. `kubernetes.io/pvc-protection`, the post's second named finalizer, is already walked in [the
CSI beta exercise](../2018/02-container-storage-interface-beta.md), and the finalizer that makes a
PersistentVolume's reclaim policy honour its claim is the subject of a later row in this same year —
that row owns it, and this exercise stays on ConfigMaps, exactly as the post does. Release facts and
the pressure behind each are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

**The diff, and why** — four of the seven cases, and the dominant one is the one this archive
records least often.

**What is still right is almost everything, and it is right in the strongest available sense: the
documentation now says it.** The mechanism, the vocabulary, the worked example and the escape hatch
all survived from 2021 to v1.37 without a rename, a group change or a gate. Every command in the
post's finalizer sections runs verbatim, and the tree's own concept page ends by sending its reader
here. In an archive where most five-year-old posts need translating before they can be executed,
this is the control case — the one that shows how much of the churn elsewhere was churn rather than
progress.

**It was also, three times over, load-bearing.** Three later posts in the blog archive — the
December 2021 PersistentVolume leak announcement, the 2024 beta announcement and the 2025 GA
announcement for the same fix — each end their finalizer paragraph with a character-identical
sentence: `To learn more about finalizers, please refer to Using Finalizers to Control Deletion.`
Four years apart, copied unchanged, because the thing being explained did not change either. That is
the test for the *never absorbed* case run in reverse, and this post fails it in the best way: it
was absorbed, it is cited inline, and the citation is load-bearing.

**Wrong when it was published** is the rarest case in this archive, and it applies to exactly one
sentence here. `:231` tells the reader that the propagation policy `cannot be specified on the
command line using kubectl`, in a post whose own inline update names a propagation policy as the
default value of a `kubectl` flag, and which runs that flag with a policy name twenty lines earlier.
It is not a claim that aged: it contradicted the adjacent paragraph on the day of publication. What
makes it worth an hour is why it survived review — the API-first route was true, complete and
demonstrable, and nobody checks a sentence that introduces a working example.

**The post broke in one line of output and nowhere else.** `selfLink` was a real field in 2021 and
is a tombstone in the API reference at the pin. Nothing the post teaches depends on it; it is simply
there in the printed block, and a reader diffing their terminal against the page will find it
missing and have to go and discover why. That is the whole of the *broke* case for this post, which
is a remarkable sentence to be able to write about a 2021 tutorial.

**Overtaken by stasis** attaches to `orphanDependents`, the field the post's `curl` route exists to
replace. It has been deprecated `in 1.7` for nineteen releases, the deprecation notice is still
copied into 69 files of generated API reference, and nothing has removed it. The post routed around
a field that was already legacy and is still legacy; the propagation policy it recommended instead
is now the documented default route in `kubectl` as well, which is the shape of a recommendation
that won without anything being deleted.

**The ladder**

Two gates, transcribed from their `stages:` lists parsed as YAML. Neither is the post's — the post
has no gate and never could, because finalizers are not a feature you enable. Both are gates the pin
added to the machinery the post describes, and both are readable only because the exercise provokes
them.

```
AllowUnsafeMalformedObjectDeletion  alpha  false  1.32 - 1.36
                                    beta   true   1.37 -
OrderedNamespaceDeletion            beta   false  1.30 - 1.32
                                    beta   true   1.33 - 1.33
                                    stable true   1.34 -        locked
```

The first gate is the one the *Force deletion* section depends on, and the pin catches it mid step:
five releases of alpha, then the beta row whose `fromVersion` is `1.37`, the newest release the pin
knows. Read that as an instruction to check your own server before you predict step 6's result — on
v1.36 the option is not there at all, and on v1.37 it is there and refuses you. Its body text is the
plainest statement in the directory of what it buys: `Enables the cluster operator to identify
corrupt resource(s) using the list operation, and introduces an option
ignoreStoreReadErrorWithClusterBreakingPotential that the operator can set to perform unsafe and
force delete operation of such corrupt resource(s) using the Kubernetes API.`

The second gate has the shape worth learning to recognise: two consecutive `beta` rows whose only
difference is `defaultValue`, then `stable` with `locked` — the switch exists, then it is on, then
it is welded on. `locked` is the key the pin actually uses, on 51 stage entries across 50 of the 487
gate files, and the reason the distinction matters is walked in [the PID-limiting
exercise](../2019/05-pid-limiting.md). Its body is one sentence: `While deleting namespace, the pods
resources is going to be deleted before the rest of resources.` Typo and all, that is the only
account the tree gives of the ordering, and it is the ordering step 10 leans on when a namespace
refuses to finish.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`, 4096MB, 4
CPUs, 25G. The post's own constraint at `:19` is the lab's: `all examples will use ConfigMaps and
basic shell commands`, so nothing here schedules a Pod, pulls an image or sends a packet between
nodes. Every observation is a decision kube-apiserver or kube-controller-manager makes about an
object's `metadata`, which means one node with no workloads is the entire rig and the control-plane
taint can stay exactly where it is. If the guest from the previous exercise in this year is still
up, keep it; if you are starting here, bring it up with [the five provision
steps](../../strands/lab-topologies.md#provision), substituting `topology=solo`, then `ssh
zain@10.10.10.180`.

**Do**

1. Establish that the post's opening still holds, command for command. These are the four fences at
   `:27-46`, unchanged:

   ```sh
   kubectl create configmap mymap
   kubectl get configmap/mymap
   kubectl delete configmap/mymap
   kubectl get configmap/mymap
   ```

2. Walk the boundary of the rule at `finalizers.md:59-60` with three names. The first block is the
   post's `:72-81`, character for character; the other two change one word each:

   ```sh
   cat <<EOF | kubectl create -f -
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: mymap
     finalizers:
     - kubernetes
   EOF
   cat <<EOF | kubectl create -f -
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: bare-custom
     finalizers:
     - mycompany
   EOF
   cat <<EOF | kubectl create -f -
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: qualified-custom
     finalizers:
     - example.com/finalizer-name
   EOF
   ```

3. Start the proxy the post needs later, delete in the background exactly as `:86-89` does, and then
   read the status code the concept page promises at `finalizers.md:30` — once against an object
   that has a finalizer and once against one that does not:

   ```sh
   kubectl proxy --port=8080 &
   kubectl delete configmap/mymap &
   jobs
   kubectl create configmap plain
   curl -s -o /dev/null -w 'plain: %{http_code}\n' -X DELETE \
     localhost:8080/api/v1/namespaces/default/configmaps/plain
   curl -s -o /dev/null -w 'qualified-custom: %{http_code}\n' -X DELETE \
     localhost:8080/api/v1/namespaces/default/configmaps/qualified-custom
   ```

4. Read the object the post says was updated rather than deleted, and diff the block you get against
   the post's `:95-109` line by line:

   ```sh
   kubectl get configmap/mymap -o yaml
   kubectl get configmap/mymap -o yaml | grep selfLink || echo "no selfLink in the output"
   kubectl get configmap/mymap \
     -o jsonpath='{.metadata.deletionTimestamp}{"  grace="}{.metadata.deletionGracePeriodSeconds}{"  finalizers="}{.metadata.finalizers}{"\n"}'
   ```

5. Test the two restrictions the post never states and `finalizers.md:49-55` does. Both of these are
   edits to an object that is already pending deletion:

   ```sh
   kubectl patch configmap/mymap --type merge \
     -p '{"metadata":{"finalizers":["kubernetes","example.com/second"]}}'
   kubectl patch configmap/mymap --type merge \
     -p '{"metadata":{"deletionTimestamp":null}}'
   kubectl get configmap/mymap -o jsonpath='{.metadata.finalizers}{"\n"}'
   ```

6. Reach for the only switch in the API that advertises ignoring finalizer constraints. Check your
   server's release against the ladder first, because the option's availability is the ladder's top
   row:

   ```sh
   kubectl version -o yaml | grep -A5 serverVersion
   kubectl auth can-i unsafe-delete-ignore-read-errors configmaps
   curl -s -X DELETE localhost:8080/api/v1/namespaces/default/configmaps/mymap \
     -H "Content-Type: application/json" \
     -d '{"kind":"DeleteOptions","apiVersion":"v1","ignoreStoreReadErrorWithClusterBreakingPotential":true}'
   ```

7. Finish the delete the post's way. This is `:116-118` verbatim, and `jobs` is the point of it:

   ```sh
   kubectl patch configmap/mymap \
       --type json \
       --patch='[ { "op": "remove", "path": "/metadata/finalizers" } ]'
   kubectl get configmap/mymap -o yaml
   jobs
   ```

8. Run the post's two owner-reference experiments, then a third it sets up and never tries. The
   first block is `:141-159` and `:164-175`; the second re-creates the pair and deletes from the
   top; the third gives a child a `uid` that belongs to nothing:

   ```sh
   cat <<EOF | kubectl create -f -
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: mymap-parent
   EOF
   CM_UID=$(kubectl get configmap mymap-parent -o jsonpath="{.metadata.uid}")

   cat <<EOF | kubectl create -f -
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: mymap-child
     ownerReferences:
     - apiVersion: v1
       kind: ConfigMap
       name: mymap-parent
       uid: $CM_UID
   EOF
   kubectl get configmap
   kubectl delete configmap/mymap-child
   kubectl get configmap
   ```

   Then the same pair again, deleted from the parent, and finally the orphan case:

   ```sh
   cat <<EOF | kubectl create -f -
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: mymap-child
     ownerReferences:
     - apiVersion: v1
       kind: ConfigMap
       name: mymap-parent
       uid: $CM_UID
   EOF
   kubectl delete configmap/mymap-parent
   kubectl get configmap
   cat <<'EOF' | kubectl create -f -
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: no-such-owner
     ownerReferences:
     - apiVersion: v1
       kind: ConfigMap
       name: ghost
       uid: 00000000-0000-0000-0000-000000000000
   EOF
   sleep 30
   kubectl get configmap no-such-owner
   kubectl get events -A --field-selector=reason=OwnerRefInvalidNamespace
   ```

9. Put both halves of the post together and make a foreground delete hang, which is the only way to
   read the finalizer the API server writes for itself. The child here carries both a dead finalizer
   and `blockOwnerDeletion`:

   ```sh
   kubectl create configmap owner
   UID=$(kubectl get configmap owner -o jsonpath="{.metadata.uid}")
   cat <<EOF | kubectl create -f -
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: blocker
     finalizers:
     - example.com/never-clears
     ownerReferences:
     - apiVersion: v1
       kind: ConfigMap
       name: owner
       uid: $UID
       blockOwnerDeletion: true
   EOF
   kubectl delete configmap owner --cascade=foreground --wait=false
   kubectl get configmap owner -o jsonpath='{.metadata.finalizers}{"\n"}'
   kubectl get configmap owner blocker
   kubectl patch configmap/blocker --type json \
       --patch='[ { "op": "remove", "path": "/metadata/finalizers" } ]'
   kubectl get configmap
   ```

10. Run the coda. A namespace with one stuck object in it, and then the `PUT` from `:246-260`, which
    is the one technique in this post that appears nowhere in the pinned documentation:

    ```sh
    kubectl create namespace test
    cat <<'EOF' | kubectl create -f -
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: stuck
      namespace: test
      finalizers:
      - example.com/never-clears
    EOF
    kubectl delete namespace test --wait=false
    kubectl get namespace test \
      -o jsonpath='{.status.phase}{"  spec.finalizers="}{.spec.finalizers}{"\n"}'
    cat <<EOF | curl -X PUT \
      localhost:8080/api/v1/namespaces/test/finalize \
      -H "Content-Type: application/json" \
      --data-binary @-
    {
      "kind": "Namespace",
      "apiVersion": "v1",
      "metadata": {
        "name": "test"
      },
      "spec": {
        "finalizers": null
      }
    }
    EOF
    kubectl get namespace test
    kubectl get configmap -n test
    kubectl create namespace test
    kubectl get configmap -n test
    ```

**Expect**

Step 1 reproduces exactly, including the column headers. `NAME DATA AGE` with `mymap 0` and an age
in seconds is what the post printed and what you get, and the last command prints `Error from server
(NotFound): configmaps "mymap" not found` — the same string, five years and sixteen releases later.
The post calls that `an HTTP 404 error`; `kubectl` does not print a code, and step 3 is where you
get to see one.

Step 2 is the rule at `finalizers.md:59-60` held against three inputs, and the sentence's weight is
on the word *custom*. `mymap` with the bare word `kubernetes` is the post's own manifest and the
census row's claim that it still applies verbatim; `qualified-custom` carries the exact form the
page recommends. `bare-custom` is the one under test: an unqualified name that no part of Kubernetes
owns. Write down which of the three the API server takes and quote the error for any it refuses,
because that message is the only statement of the rule you will get from a running cluster — the
tree states it in prose, on one page, in a note.

Step 3: `jobs` shows two entries now, the proxy and the delete, and the delete stays `Running`
exactly as `:89` shows. The two status codes are the finding. Deleting `plain`, which has no
finalizer, completes; deleting `qualified-custom`, which has one, returns `202` — the `202 status
code (HTTP "Accepted")` that `finalizers.md:30` promises and that no `kubectl` output in the post
could have shown you. That is the difference between *deleted* and *accepted for deletion*, printed
as a number.

Step 4 is the diff the exercise exists for. `deletionGracePeriodSeconds: 0`, a `deletionTimestamp`,
`finalizers: [kubernetes]`, `name`, `namespace`, `resourceVersion`, `uid` — all present, all in the
post's own shape. The `grep` fires its fallback: `selfLink` is gone, because the API reference at
`object-meta-v1-meta.md:92` marks it a legacy field `no longer populated by the system`. One line of
a fourteen-line block, and it is the only line of the post's output that a current cluster will not
give you.

Step 5: both patches are refused, and the reasons are different. Adding `example.com/second` to an
object that already has a `deletionTimestamp` runs into the restriction at `finalizers.md:49-53` —
removal is allowed, addition is not — and clearing the timestamp runs into the next clause of the
same note. The third command confirms the list is untouched. Read that pair as the reason the post's
escape hatch is a *remove* operation and not an *edit*: there is exactly one legal move on a dying
object, and the post found it.

Step 6 is the modern hammer refusing to be one. If `serverVersion` reads v1.37 or later the gate is
on by default, `can-i` answers `yes` for a cluster-admin, the option is accepted by the decoder —
and the request still fails, because `api-concepts.md:1182-1185` says the API server `aborts the
request with an error` when the target is readable. Your ConfigMap is readable; it is held by a key,
not by a corrupt row in etcd. On a server older than v1.37 you get a different refusal, from the
gate rather than from the check. Either way the sentence to carry out of this step is that the one
documented way to `ignore finalizer constraints` is scoped to objects the API server cannot decode,
and there is still no API for the post's problem.

Step 7 is the post's ending and it is unchanged. The JSON patch returns `configmap/mymap patched`,
the backgrounded delete from step 3 reports `Done`, and the `get` returns `NotFound`. Two commands,
one of which was already running, and the object leaves etcd — `:130` in prose, on your terminal,
verbatim.

Step 8: the first block prints both ConfigMaps, deletes the child, and leaves `mymap-parent` alone,
exactly as `:164-175` shows. The second deletes the parent and takes the child with it — `No
resources found in default namespace.` is the post's line and it is still the output. The third is
the experiment the post sets up with `it also needs a UID for that reference to work` and never
runs: a child whose owner does not exist is deleted by the garbage collector within a minute,
unasked, because `owners-dependents.md:50-51` treats an unresolvable reference as an absent owner
and an object with no owners as garbage. The Event query returns nothing here — that reason is
reserved for cross-namespace and cluster-scoped mistakes, not for a `uid` that matches nothing — and
a `get` that returns `NotFound` on an object you just created is the point. The post's owner
references are not a link to a parent; they are a claim to be checked, and failing the check is
fatal.

Step 9 settles the spelling. `owner` goes into foreground deletion, and its own `finalizers` list
comes back holding one entry written by the API server, not by you. Two of the three places the tree
names it — `garbage-collection.md:80-81` and the captured response at
`use-cascading-deletion.md:80-94` — say `foregroundDeletion`; `owners-dependents.md:79` says
`foreground`. Your cluster is the tiebreaker, and it is also the answer to the sentence at `:231`:
the flag you just used put a propagation policy on the command line, which the post says you cannot
do. Both objects stay listed until you remove the child's dead finalizer, and then both disappear in
the same second — post-order deletion, demonstrated by preventing it.

Step 10 ends somewhere the documentation will not follow you. The namespace goes to `Terminating`
with `spec.finalizers` still `["kubernetes"]`, and it stays there, because the namespace controller
cannot finish while one ConfigMap inside it is held by a key nothing will remove. The `PUT` returns
the namespace object with `spec.finalizers` cleared, and the namespace disappears from `get
namespace` — the whole of the post's recipe, working. Then read the next two lines carefully and
write down what they say, because that state is the post's own warning at `:263` made real: an
object with a `deletionTimestamp`, a finalizer and a namespace that does not exist. Recreating the
namespace is the last command, and whether your ConfigMap comes back into view is the question the
post leaves open with `sometimes`. Either way you now own the mess that [the namespaces
exercise](../2015/08-using-kubernetes-namespaces-to-manage.md) declined to make, and its advice —
look for the finalizer before you look for a bigger hammer — reads differently from this side of it.

**Read on**

1. `reference/using-api/api-concepts.md:1126-1143` is the paragraph the post could not have written:
   why finalizer processing has no defined order, and why giving it one would create stuck objects
   rather than prevent them. Read it with step 5 in mind. The post's single dead key is the
   degenerate case of a deadlock between two live ones, and the reason the API server refuses to let
   you add a finalizer after the timestamp is set is the reason that deadlock has to be resolved by
   the holders rather than by the server.

2. `concepts/overview/working-with-objects/owners-dependents.md:33-44` and
   `concepts/architecture/garbage-collection.md:90-94` are the two reasons a foreground delete
   stalls that the post never mentions — a dependent with `blockOwnerDeletion: true`, and a
   dependent the garbage collection controller's cache does not hold because its type `cannot be
   listed / watched successfully`. Step 9 builds the first on purpose. The second is what a stuck
   delete looks like when nobody did anything wrong.

3. The citation chain is worth following outside this exercise. Three release announcements in the
   blog archive — December 2021, 2024 and 2025, all three about making a PersistentVolume's reclaim
   policy survive an out-of-order delete — end their finalizer paragraph with the same sentence
   pointing here, byte for byte identical across four years. The 2021 one is a `walk` in this very
   year and a later row owns it. Read `finalizers.md:89-96` before you get there, because the note
   that tells you to avoid removing finalizers by hand is the post's Key Takeaways promoted to
   documentation, and the feature those three posts announce is a finalizer added specifically so
   that nobody has to.

4. `kubernetes.io/pvc-protection`, the second finalizer the post names at `:66`, is walked where it
   belongs — in [the CSI beta exercise](../2018/02-container-storage-interface-beta.md), where a
   half-deleted PersistentVolume is a thing you have to clean up rather than a name in a list. The
   namespace half of step 10 is walked backwards in [the namespaces
   exercise](../2015/08-using-kubernetes-namespaces-to-manage.md), which reads `.spec.finalizers`
   and `.status.phase` on a namespace that is deleting properly. Between them and this exercise,
   every finalizer the post names has been seen doing its job.

5. Unanswerable from the pin: which unqualified finalizer names the API server accepts. The tree
   shows three — `kubernetes` in this post, `orphan` and `foregroundDeletion` in the captured
   responses on `use-cascading-deletion.md` — and states the rule only for the *custom* case, so
   whether those three are a closed set, and what the error is for a fourth, is something step 2
   measures and no page at the pin declares. Also unanswerable: which `kubectl` release turned
   `--cascade` into a string taking policy names, the fact that would date the wrong sentence at
   `:231` precisely. The pin's own task page carries an unresolved authoring note asking exactly
   that, which [the StatefulSets and DaemonSets
   exercise](../2017/04-kubernetes-statefulsets-daemonsets.md) reads in place.

**Teardown**

One object here cannot be deleted the ordinary way, which is the exercise's own fault and the right
place to finish: patch the finalizer off the orphan from step 10 first, then let the namespace go
normally.

```bash
kubectl patch configmap/stuck -n test --type json \
    --patch='[ { "op": "remove", "path": "/metadata/finalizers" } ]'
kubectl delete namespace test
kubectl delete configmap --all
jobs
kill %1
kubectl get configmap,namespaces
```

If the `patch` reports that the ConfigMap is not found, the re-created namespace never brought it
back into view and it left with the namespace; either result is a finding worth keeping. `kill %1`
stops the proxy. Nothing else on the node was touched, and no Pod ever ran — leave the guest up, the
next exercise in this year reuses it.
