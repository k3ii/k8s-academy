<a id="kubernetes-v1-34-recover-expansion-failure"></a>

# Neither manifest in this post can be applied, because the storage suffix both of them use is not one the quantity parser accepts, the status field it says to watch is spelled in the singular by the reference page whose heading spells it plural, and the quota promise is one table cell

**Post** — [Kubernetes v1.34: Recovery From Volume Expansion Failure
(GA)](https://kubernetes.io/blog/2025/09/19/kubernetes-v1-34-recover-expansion-failure/),
2025-09-19.

5,408 bytes, 97 lines, 708 words of body — the smallest of 2025's twelve `walk` posts, and ninth of
the twelve by publication date. One author, one vendor. Two `##` headings and three `###`, two
fenced YAML blocks, and one line carrying trailing whitespace. Nine markdown links across nine
distinct targets: six GitHub profiles, two issue trackers, and one documentation page. That last
link is the only pointer to Kubernetes documentation anywhere in the post, and the post names no
feature gate and no KEP.

**As written**

The hook is a typo. `:10-11` asks whether you have ever meant to specify `2TB` and specified `20TiB`
instead, calls the problem "kinda hard to fix", and says it took the project almost five years.
`:12-13` says automated recovery from storage expansion has been in beta for a while and has
graduated to general availability in v1.34, linking the concept page's recovery section. `:15` adds
that manual recovery was always possible but "usually required cluster-admin access and was tedious
to do".

`:17-21` is the promise, and it has four parts: you can reduce the requested size of a
PersistentVolumeClaim; this works as long as the expansion to the previously requested size has not
finished; any quota consumed by the failed expansion will be returned to the user; and the
PersistentVolume should end up resized to the latest size you specified.

*Reducing PVC size to recover from failed expansion* (`:25-66`) walks one scenario. You are out of
disk space on a database server, you mean to go from `10TB` to `100TB`, and you type `1000TB`
(`:27-28`). A four-field PersistentVolumeClaim manifest follows at `:30-41`, its one interesting
line `storage: 1000TB # newly specified size - but incorrect!`. `:43` says to assume the expansion
will never succeed. `:45-47` gives the correction rule — request a size smaller than the mistake but
still larger than the original size of the actual PersistentVolume — and `:49-61` repeats the
manifest with `storage: 100TB # Corrected size; has to be greater than 10TB.` and a second comment
line saying you cannot shrink the volume below its actual size. `:63` says this requires no admin
intervention and that surplus quota is automatically returned. `:65-66` states the caveat in its
strongest form: whatever size you specify **must** still be higher than the original size in
`.status.capacity`, because Kubernetes does not support shrinking PersistentVolume objects.

*Improved error handling and observability of volume expansion* (`:68-92`) is three subsections.
`:74-81` says to query `.status.allocatedResourceStatus['storage']` to monitor progress, that a
typical block volume transitions between `ControllerResizeInProgress`, `NodeResizePending` and
`NodeResizeInProgress` before becoming nil, that an infeasible expansion lands in
`ControllerResizeInfeasible` or `NodeResizeInfeasible`, and that `pvc.status.allocatedResources`
shows the size Kubernetes is working towards. `:83-87` says failed expansions are now retried at a
slower rate with fewer requests to both the storage system and the API server, and that errors are
reported as conditions with the keys `ControllerResizeError` or `NodeResizeError`. `:89-92` credits
the rewrite with fixing long-standing bugs and links one Kubernetes issue. The close thanks five
contributors by handle.

**As it runs now**

**The suffix both manifests use is not a suffix.** A Kubernetes quantity takes one of three suffix
forms, and the generated grammar at `quantity-resource.md:39` writes all three out: `<suffix> ::=
<binarySI> | <decimalExponent> | <decimalSI>`, where `<binarySI>` is `Ki | Mi | Gi | Ti | Pi | Ei`
and `<decimalSI>`, on `:43`, is `m | "" | k | M | G | T | P | E`. `TB` is in neither list.
`manage-resources-containers.md:179-186` says the same thing in prose and adds the warning that
matters here, that `M` means megabytes and `m` means millibytes. So neither of the post's two
manifests can be applied to any Kubernetes cluster: not to v1.34, not to the v1.35 in this lab, not
to the v1.23 where the feature was first available. The refusal comes from the quantity parser
before any PersistentVolumeClaim validation runs, which is why the error says nothing about volumes,
expansion, or the feature the post is announcing.

**`TB` as a storage quantity appears nowhere else in the pinned tree.** A search of `docs`,
`examples` and the whole blog archive for a digit followed by `TB` returns seven lines. Five are in
this post — `:10`, `:28`, `:40`, `:43` and `:59` — and the other two are prose in posts from 2017
and 2020, using `TB` as an English unit of data, which is correct and irrelevant to YAML. Narrow the
search to `storage: ` followed by a number and `TB` and it returns two lines, both of them the one
line of each of this post's two manifests. No example manifest anywhere in the checkout writes a
storage request with a `B` in it.

**The hook's typo is not a typo the parser would produce either.** `:10-11` contrasts `2TB` with
`20TiB`, and `TiB` is not a suffix any more than `TB` is — the binary form is `Ti`. The nearest
legal spellings of what the sentence means are `2T`, two decimal terabytes, and `20Ti`, twenty
tebibytes, which is about 21.99 decimal terabytes. The mistake the hook describes is therefore not a
factor of ten but a factor of about eleven, and the two-character difference the sentence is built
on changes both the digit count and the base. The walkthrough then abandons those numbers entirely
and uses `10TB`, `100TB` and `1000TB` instead, so the post's two halves never share an example.

**The status field the post tells you to watch is spelled in the singular, and the API spells it in
the plural.** The field is `allocatedResourceStatuses`. The post writes
`.status.allocatedResourceStatus['storage']` at `:76`. Across `content/en` the singular form occurs
six times and the plural three: one singular here and five in the generated API reference, against
one plural on the concept page and two in that same reference. The spelling a reader is most likely
to meet is the one that does not exist, and `kubectl explain` will tell them so.

**The reference page disagrees with itself about the name of the field it is documenting.** This is
a statement about the documentation rather than about the post, so it belongs here.
`persistent-volume-claim-v1.md:125` gives the field's name as `allocatedResourceStatuses` in the
cell that names it, and the description in the cell beside it, `:126`, works through an example
using `pvc.status.allocatedResourceStatus['storage']` five times in five consecutive lines. The
heading and the worked example in one table row do not agree, the page is generated from the Go
source, and the disagreement is therefore upstream of the website: the field's own doc comment
contains the typo the post repeats.

**Two of the five states the post names are not in the documented set.** `:79` says an infeasible
expansion lands in `ControllerResizeInfeasible` or `NodeResizeInfeasible`. The reference at `:126`
enumerates the states a `ClaimResourceStatus` can take, and there are five:
`ControllerResizeInProgress`, `ControllerResizeFailed`, `NodeResizePending`, `NodeResizeInProgress`
and `NodeResizeFailed`. The three the post names for the happy path match. The two it names for the
unhappy path do not appear in `docs` at all — not on the concept page, not in the reference, not in
any task page. Whether the API server accepts them is a question this exercise answers rather than
assumes, because a state a document does not list is not thereby a state an API rejects.

**Neither condition key the post names appears anywhere in the documentation.** `:87` says
Kubernetes populates `pvc.status.conditions` with `ControllerResizeError` or `NodeResizeError`. Both
return zero hits across `docs`. The gap is wider than those two names. The only condition string the
reference offers at all is `Resizing`, at `:138` and `:229`, and [the exercise that owns the 1.24
graduation](../2022/01-volume-expansion-ga.md) works through which of the two places means the
condition's type and which means its reason. Beyond that one word, no PersistentVolumeClaim
condition type is written down anywhere under `docs`: the only one in the whole pinned checkout is
`FileSystemResizePending`, in a blog post from 2018. Seven years of expansion vocabulary have
reached readers through blog posts or not at all.

**The feature gate's name appears in exactly one file in the tree.** `RecoverVolumeExpansionFailure`
occurs in `feature-gates/RecoverVolumeExpansionFailure.md` and nowhere else under `content/en` — not
in the release announcement, not on the concept page whose section documents the behaviour, not in
the API reference, and not in the post. A reader who wants to know which switch this is, or whether
it can still be turned off, has to know the gate's name before they can find the page that has it.

**The post rounds the ladder to a duration the pin cannot check.** `:11` says the fix took the
project "almost 5 years", and nothing in the checkout dates a Kubernetes release, so that figure is
unverifiable here. What the checkout does carry is the version range, in two places that agree: the
gate file's three rungs, parsed below, and the release announcement at
`kubernetes-v1-34-release/index.md:100`, which says the feature was introduced as alpha in v1.23 and
graduated to stable in v1.34. Neither number reaches the post. The gate file itself carries trailing
whitespace on two of its frontmatter lines, after `stage: alpha` and after `fromVersion: "1.34"`.

**The post names no KEP and the release announcement beside it names one twice.** `:91` links a
Kubernetes issue as the example of a long-standing bug fixed, and that is the only enhancement
reference in the post. `kubernetes-v1-34-release/index.md:102` says the work was done as part of KEP
1790 led by SIG Storage, and `:463` lists it again in the release's enhancement index. Both are in
the pinned archive, three weeks before this post, under a `skip` verdict — which means the number a
reader needs is in the checkout, and the post that would most want to cite it does not.

**The page the post links leads with the procedure it says you no longer need.**
`persistent-volumes.md:453` is the section, and `:460` opens a tabbed block whose first tab, named
at `:461`, is "Manually with Cluster Administrator access": a five-step drill at `:468-476` that
marks the PersistentVolume `Retain`, deletes the claim, edits `claimRef` out of the volume,
recreates the claim smaller with `volumeName` set, and restores the reclaim policy. The tab the post
is about, "By requesting expansion to smaller size", is second, at `:479`. The post's `:15` calls
the first route tedious and cluster-admin-only and sends the reader to this page for more
information, so the more information they find is the tedious route, on top.

**The section that documents a v1.34 graduation carries no feature-state marker.** Its parent, `###
Expanding Persistent Volumes Claims` at `:377`, carries `{{< feature-state for_k8s_version="v1.24"
state="stable" >}}` on `:379`. Two of its three subsections carry their own markers. `####
Recovering from Failure when Expanding Volumes` carries none, so nothing on the page records that
the behaviour it describes was beta when the page was last touched and is stable now, and nothing on
the page records which release changed that.

**The concept page states the rule more narrowly than the post does.** `:481-487` frames reducing
the request as a retry — retry expansion with a smaller size, useful if the larger value failed
because of a capacity constraint — and tells you to watch `.status.allocatedResourceStatuses` and
events. `:490-493` gives the caveat in the same words the post uses: the new value must still be
higher than `.status.capacity`, and Kubernetes does not support shrinking a claim below its current
size. What the page never says is the thing the post leads with, that this no longer needs a cluster
administrator; and what the post never says is the thing the page leads with, that the manual route
still exists and is still documented first.

**The quota promise is written down once in the whole tree, in a table cell for a different field.**
`persistent-volume-claim-v1.md:130` documents `allocatedResources`, and inside that cell is the only
sentence in `content/en` that connects storage quota to volume expansion: *"For storage quota, the
larger value from allocatedResources and PVC.spec.resources is used. If allocatedResources is not
set, PVC.spec.resources alone is used for quota calculation. If a volume expansion capacity request
is lowered, allocatedResources is only lowered if there are no expansion operations in progress and
if the actual volume capacity is equal or lower than the requested capacity."* That is the mechanism
behind "any quota consumed by failed expansion will be returned to the user", and it is three
sentences in a generated table.

**The two pages that would say it do not.** `resource-quotas.md` documents `requests.storage` at
`:181` and never uses the words expansion, expand or resize anywhere in the file.
`persistent-volumes.md` never uses the word quota anywhere in its twelve hundred lines, including in
the recovery section. The only two files under `docs` that mention both volume expansion and quota
are the API reference above and the admission-controller reference. A reader following the post's
quota claim into the documentation has one place to land and no path that leads there.

**"Automatically returned" has three conditions attached.** The rule quoted above returns quota by
lowering `allocatedResources`, and it lowers it only when `allocatedResources` is set at all, only
when no expansion operation is in progress, and only when the actual volume capacity is at or below
the new request. On a cluster with no CSI driver the first condition is never met, so quota follows
`spec` directly and the post's promise appears to hold for a reason that has nothing to do with the
feature. Steps 7 and 8 below separate those two cases by writing the field by hand.

**One author link is malformed, and the post carries three other surface defects.** `:97` links
`[@liggitt]` to `https://github.comliggitt` — no slash, no separator — and a search of `content/en`
for `https://github.com` followed immediately by a letter returns that one line and nothing else.
`:15` writes "aformentioned" and `:87` writes "observerd", each the only occurrence of its spelling
in the checkout. `:70` ends with a trailing space. None of these change what the post claims; all
four are the kind of thing a reader trips over in the first minute and then wonders what else was
not checked.

**What this exercise does not cover, and where it lives.** Expansion itself is already walked twice
in this repo and neither is repeated here. [The 1.24 graduation
exercise](../2022/01-volume-expansion-ga.md) owns the three feature gates that became one, what a
cluster with no CSI driver does with an expansion request, the two StorageClasses that provision
nothing, the validation boundary around shrinking a bound claim, and the resize controller's two
names; step 6 of that exercise is where the API's own limits on reducing a request are established,
and this one takes them as given. [The two-phase storage
lab](../../labs/08/09-expansion-two-phase.md) owns the recovery drill itself, run on a `pair`
topology behind a working CSI driver, where a volume actually grows and a filesystem actually
follows. This exercise is neither: it is about whether the post's own text survives contact with an
API server, and about the one consequence nobody has walked — what storage quota does while a claim
is asking for a size it will never get. [The exercise that owns quota scoped to a volume attributes
class](../2023/12-kubernetes-1-29-volume-attributes-class.md) covers the other way a
PersistentVolumeClaim meets a ResourceQuota, and the two do not overlap.

**The diff, and why** — four of the seven cases.

**Wrong when it was published: both manifests.** The post's two YAML blocks could not be applied on
the day they were published, and could not have been applied at any point in the eleven releases the
feature took to graduate. `TB` has never been a Kubernetes quantity suffix. This is not a case of
the world moving on: the example was broken at rest, in a post whose entire subject is a mistake in
a size field, and the mistake it demonstrates is not the one it means to demonstrate.

**Never absorbed: the vocabulary and the quota rule.** Five of the strings the post teaches have no
home in the documentation — two allocation states, two condition keys, and the feature gate that
controls all of it. The quota behaviour the post promises is documented once, inside a generated
table cell belonging to a different field, and neither the quota page nor the concept page links to
it. A reader who takes this post as a starting point and goes looking for more will find the page it
links, which does not mention quota, and then stop.

**Still right: the rule and its caveat.** Reducing the request works, the floor is
`.status.capacity`, and the concept page at `:490-493` says so in almost the post's own words. The
gate has been stable and locked since 1.34, so there is no switch to check and nothing a cluster
operator can do to take the behaviour away. Eleven releases after the alpha rung opened, the
sentence a user needs is short and it is correct.

**Overtaken by stasis: the page the post points at.** The post's argument is that recovery no longer
needs a cluster administrator. The page it links still leads with the cluster administrator's
five-step drill, still carries no feature-state marker on the section, and still frames the
reduction as a retry rather than as a correction. Nothing on that page was wrong before the post and
nothing on it is wrong after; it simply did not move, and the post's one documentation link lands on
the half of the page it was written to replace.

**The ladder**

`RecoverVolumeExpansionFailure.md` is a three-rung ladder, parsed from its frontmatter: alpha with
`defaultValue: false` from 1.23 to 1.31, beta with `defaultValue: true` from 1.32 to 1.33, and
stable with `locked: true` and `defaultValue: true` from 1.34 with no `toVersion`. The lab runs
v1.35, so the gate is on, locked, and cannot be turned off — which is why no step below touches a
feature-gate flag and why the exercise spends its time on vocabulary and quota instead.

Two numbers put that ladder in context. Of the 487 gate files that carry a stage table, 49 carry a
rung marked `locked: true`, so a locked gate is uncommon rather than routine, and this one is locked
in its first stable release rather than one or two later. And a nine-release alpha is long: of the
347 gates whose alpha rung has a `toVersion` and can therefore be measured, only 23 spent nine
releases or more there, and this gate ranks twenty-second among them. The post's "almost 5 years" is
the only place either fact is stated, and it is stated as a feeling rather than as a version range.

Twenty-six gates take a stable rung from 1.34, and one of the other twenty-five is the subject of
[the exercise before this one](08-kubernetes-v1-34-dra-updates.md). Both posts announce a
graduation, both name no gate, and both leave the reader with no way to find the switch from the
text. The difference is that the dynamic resource allocation gate is named in nine files under
`docs` and this one is named in none.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180`, Kubernetes v1.35,
[provisioned](../../strands/lab-topologies.md#provision) and
[baselined](../../strands/lab-topologies.md#node-baseline-steps) as usual. Every object below lives
in a namespace called `bw-recover` except one PersistentVolume, one StorageClass and one
ClusterRole-free ServiceAccount binding, all of which *Teardown* removes. The volume is a 1Ti
`hostPath` declaration over a directory the node creates, so nothing on the node is formatted,
mounted or filled: the number is a claim about capacity that no filesystem is asked to honour, which
is exactly the condition under which the post's promise is interesting. No CSI driver is installed
and none is needed. Steps 1 to 9 run from wherever you run `kubectl`, with one `ssh` to create the
directory; step 10 runs offline against a checkout of `kubernetes/website` at the pin, with `W` set
to its `content/en` directory.

**Do**

1. Ask the cluster what it calls the fields the post names. `kubectl explain` reads the API server's
   own schema, so this is not a documentation lookup — it is the same source the reference page is
   generated from, asked directly:

   ```sh
   kubectl version -o json | grep -m2 gitVersion
   kubectl create namespace bw-recover
   kubectl explain persistentvolumeclaim.status | sed -n '1,30p'
   kubectl explain persistentvolumeclaim.status.allocatedResourceStatuses | sed -n '1,20p'
   kubectl explain persistentvolumeclaim.status.allocatedResourceStatus 2>&1 | tail -2
   kubectl explain persistentvolumeclaim.status.allocatedResources | sed -n '1,12p'
   ```

2. Apply the post's two manifests exactly as written. The first is copied character for character
   from `:30-41`; the second is the same file with the one line the post changes. Both go to the API
   server rather than to a client-side parser, and then the first one goes to the client-side parser
   as well, so you can see which of the two refuses it:

   ```sh
   mkdir -p /tmp/bw-recover
   cat > /tmp/bw-recover/post-first.yaml <<'YAML'
   kind: PersistentVolumeClaim
   apiVersion: v1
   metadata:
     name: myclaim
   spec:
     accessModes:
       - ReadWriteOnce
     resources:
       requests:
         storage: 1000TB # newly specified size - but incorrect!
   YAML
   sed 's|storage: 1000TB.*|storage: 100TB # Corrected size; has to be greater than 10TB.|' \
     /tmp/bw-recover/post-first.yaml > /tmp/bw-recover/post-second.yaml
   kubectl -n bw-recover apply --dry-run=server -f /tmp/bw-recover/post-first.yaml 2>&1 | tail -3
   kubectl -n bw-recover apply --dry-run=server -f /tmp/bw-recover/post-second.yaml 2>&1 | tail -3
   kubectl -n bw-recover apply --dry-run=client -f /tmp/bw-recover/post-first.yaml 2>&1 | tail -3
   ```

3. Census the suffixes. Sixteen spellings, each one submitted to the API server and each one either
   accepted or refused, including the two the post uses, the two its hook uses, and the pair that
   differ only in the case of one letter:

   ```sh
   for Q in 1000TB 100TB 2TB 20TiB 1000T 100T 2T 20Ti 1Ti 1024Gi 1e12 1000G 1000k 1000K 1000m 1000; do
     printf 'apiVersion: v1\nkind: PersistentVolumeClaim\nmetadata: { name: probe }\nspec:\n  accessModes: ["ReadWriteOnce"]\n  resources: { requests: { storage: %s } }\n' "$Q" \
       > /tmp/bw-recover/probe.yaml
     printf '%-8s %s\n' "$Q" \
       "$(kubectl -n bw-recover apply --dry-run=server -f /tmp/bw-recover/probe.yaml 2>&1 | tail -1 | cut -c1-96)"
   done
   ```

4. Read back what the server stores. A quantity remembers the kind of suffix it was written with and
   re-emits itself in canonical form, so the accepted spellings do not all come back the way they
   went in. Then do the arithmetic the post's hook implies:

   ```sh
   for Q in 2T 20Ti 1500m 1.5Gi 129e6 1024Gi; do
     printf 'apiVersion: v1\nkind: PersistentVolumeClaim\nmetadata: { name: probe }\nspec:\n  accessModes: ["ReadWriteOnce"]\n  resources: { requests: { storage: %s } }\n' "$Q" \
       > /tmp/bw-recover/probe.yaml
     printf '%-8s -> %s\n' "$Q" \
       "$(kubectl -n bw-recover apply --dry-run=server -o jsonpath='{.spec.resources.requests.storage}' \
          -f /tmp/bw-recover/probe.yaml 2>&1 | tail -1)"
   done
   python3 -c 'print("2T  =", 2*10**12, "bytes"); print("20Ti=", 20*2**40, "bytes"); print("ratio", round(20*2**40/(2*10**12), 2))'
   ```

5. Build the ground: a quota that counts storage, a class that allows expansion, a volume whose
   capacity is a declaration rather than a filesystem, and the claim the post names. Nothing here
   provisions anything, and the node is asked only for a directory:

   ```sh
   ssh zain@10.10.10.180 'sudo mkdir -p /srv/bw-recover'
   kubectl apply -f - <<'YAML'
   apiVersion: v1
   kind: ResourceQuota
   metadata: { name: bw-recover, namespace: bw-recover }
   spec:
     hard:
       requests.storage: 50Ti
       persistentvolumeclaims: "2"
   ---
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata: { name: bw-recover }
   provisioner: kubernetes.io/no-provisioner
   allowVolumeExpansion: true
   ---
   apiVersion: v1
   kind: PersistentVolume
   metadata: { name: bw-recover }
   spec:
     capacity: { storage: 1Ti }
     accessModes: ["ReadWriteOnce"]
     persistentVolumeReclaimPolicy: Retain
     storageClassName: bw-recover
     hostPath: { path: /srv/bw-recover }
   ---
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata: { name: myclaim, namespace: bw-recover }
   spec:
     accessModes: ["ReadWriteOnce"]
     storageClassName: bw-recover
     volumeName: bw-recover
     resources: { requests: { storage: 1Ti } }
   YAML
   sleep 5
   kubectl -n bw-recover get pvc myclaim -o jsonpath='req={.spec.resources.requests.storage} cap={.status.capacity.storage} phase={.status.phase}{"\n"}'
   kubectl -n bw-recover get resourcequota bw-recover -o jsonpath='hard={.status.hard.requests\.storage} used={.status.used.requests\.storage}{"\n"}'
   ```

6. Make the post's mistake three times, in three different sizes, and collect three different
   answers. The first is the mistake as the post spells it. The second is the same mistake spelled
   legally and inside the quota. The third is the same mistake spelled legally and outside it:

   ```sh
   kubectl -n bw-recover patch pvc myclaim --type=merge \
     -p '{"spec":{"resources":{"requests":{"storage":"1000TB"}}}}' 2>&1 | tail -2
   kubectl -n bw-recover patch pvc myclaim --type=merge \
     -p '{"spec":{"resources":{"requests":{"storage":"40Ti"}}}}' 2>&1 | tail -2
   sleep 10
   kubectl -n bw-recover describe resourcequota bw-recover | sed -n '1,8p'
   kubectl -n bw-recover patch pvc myclaim --type=merge \
     -p '{"spec":{"resources":{"requests":{"storage":"100Ti"}}}}' 2>&1 | tail -2
   kubectl -n bw-recover get pvc myclaim -o jsonpath='req={.spec.resources.requests.storage} cap={.status.capacity.storage}{"\n"}'
   ```

7. Correct it, and watch the quota. This is the post's promise, executed: reduce the request to
   something above `.status.capacity` and below the mistake, and see what the quota controller does
   with the difference:

   ```sh
   kubectl -n bw-recover patch pvc myclaim --type=merge \
     -p '{"spec":{"resources":{"requests":{"storage":"2Ti"}}}}'
   sleep 15
   kubectl -n bw-recover get resourcequota bw-recover \
     -o jsonpath='used={.status.used.requests\.storage}{"\n"}'
   kubectl -n bw-recover get pvc myclaim -o jsonpath='req={.spec.resources.requests.storage} cap={.status.capacity.storage} alloc={.status.allocatedResources.storage} statuses={.status.allocatedResourceStatuses}{"\n"}'
   kubectl -n bw-recover get events --field-selector involvedObject.name=myclaim | tail -5
   ```

8. Write the field the quota rule actually reads. The reference says quota uses the larger of
   `allocatedResources` and `spec.resources`, and on a cluster with no driver nothing ever sets the
   first — so set it by hand through the status subresource, and find out whether usage follows a
   field that admission never saw. Then try the five documented states, the two the post names that
   are not among them, and one that is not a state at all:

   ```sh
   kubectl -n bw-recover patch pvc myclaim --subresource=status --type=merge \
     -p '{"status":{"allocatedResources":{"storage":"40Ti"}}}' 2>&1 | tail -2
   sleep 20
   kubectl -n bw-recover get resourcequota bw-recover \
     -o jsonpath='used={.status.used.requests\.storage} hard={.status.hard.requests\.storage}{"\n"}'
   for S in ControllerResizeInProgress NodeResizeFailed ControllerResizeInfeasible NodeResizeInfeasible NotAState; do
     printf '%-28s %s\n' "$S" \
       "$(kubectl -n bw-recover patch pvc myclaim --subresource=status --type=merge \
          -p "{\"status\":{\"allocatedResourceStatuses\":{\"storage\":\"$S\"}}}" 2>&1 | tail -1 | cut -c1-90)"
   done
   kubectl -n bw-recover patch pvc myclaim --subresource=status --type=merge \
     -p '{"status":{"allocatedResources":null,"allocatedResourceStatuses":null}}' 2>&1 | tail -2
   sleep 20
   kubectl -n bw-recover get resourcequota bw-recover \
     -o jsonpath='used={.status.used.requests\.storage}{"\n"}'
   ```

9. Measure "this requires no admin intervention". Give an identity the one permission the correction
   needs, then ask it for every permission the five-step drill on the linked page needs, and then
   have it perform the correction:

   ```sh
   U=system:serviceaccount:bw-recover:tenant
   kubectl -n bw-recover create serviceaccount tenant
   kubectl -n bw-recover create role pvc-editor \
     --verb=get,list,watch,patch,update --resource=persistentvolumeclaims
   kubectl -n bw-recover create rolebinding tenant-pvc \
     --role=pvc-editor --serviceaccount=bw-recover:tenant
   for V in "patch persistentvolumeclaims" "update persistentvolumeclaims" \
            "create persistentvolumeclaims" "delete persistentvolumeclaims"; do
     printf '%-34s %s\n' "$V" "$(kubectl auth can-i --as=$U -n bw-recover $V)"
   done
   for V in "patch persistentvolumes" "get persistentvolumes" "delete persistentvolumes"; do
     printf '%-34s %s\n' "$V" "$(kubectl auth can-i --as=$U $V)"
   done
   kubectl -n bw-recover patch pvc myclaim --as=$U --type=merge \
     -p '{"spec":{"resources":{"requests":{"storage":"40Ti"}}}}'
   kubectl -n bw-recover patch pvc myclaim --as=$U --type=merge \
     -p '{"spec":{"resources":{"requests":{"storage":"3Ti"}}}}'
   kubectl -n bw-recover get pvc myclaim -o jsonpath='req={.spec.resources.requests.storage}{"\n"}'
   ```

10. Offline, in the pinned checkout, count the six things the sections above assert. Every number
    here is one the exercise depends on, so produce them rather than trusting them:

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -rn 'storage: [0-9]*TB' docs examples blog --include='*.md'
    grep -rno "allocatedResourceStatus\['storage'\]" docs blog --include='*.md' | sed 's/:[0-9]*:.*//' | sort | uniq -c
    grep -rno 'allocatedResourceStatuses' docs --include='*.md' | sed 's/:[0-9]*:.*//' | sort | uniq -c
    for S in ControllerResizeInfeasible NodeResizeInfeasible ControllerResizeError \
             NodeResizeError ControllerResizeFailed RecoverVolumeExpansionFailure; do
      printf '%-32s docs=%s blog=%s\n' "$S" \
        "$(grep -rl "$S" docs --include='*.md' | wc -l | tr -d ' ')" \
        "$(grep -rl "$S" blog --include='*.md' | wc -l | tr -d ' ')"
    done
    printf 'quota in persistent-volumes.md: %s\n' "$(grep -c -i quota docs/concepts/storage/persistent-volumes.md)"
    printf 'expand/resize in resource-quotas.md: %s\n' "$(grep -c -i 'expan\|resiz' docs/concepts/policy/resource-quotas.md)"
    sed -n '453,461p;479p' docs/concepts/storage/persistent-volumes.md
    grep -rn 'https://github\.com[a-z]' . --include='*.md'
    ```

**Expect**

Step 1 prints v1.35 twice and then answers the vocabulary question without any reference to the
website. `kubectl explain persistentvolumeclaim.status` lists `allocatedResourceStatuses` and
`allocatedResources` among its fields; the singular spelling the post uses returns an error saying
the field does not exist. The reward is in the description text: the schema the API server serves
for `allocatedResourceStatuses` is the same string the generated reference page prints, typo and
all, so the five occurrences of `pvc.status.allocatedResourceStatus['storage']` come back out of
your own cluster. The disagreement is not the website's; it is in the field's doc comment, and every
consumer of the OpenAPI schema inherits it.

Step 2 refuses both manifests. The message comes from the quantity parser and names a regular
expression rather than a field, a resource or a feature — read it and note what it does not say: no
mention of PersistentVolumeClaim, of storage classes, of expansion, or of the size being too large.
`1000TB` and `100TB` fail for the same reason `hello` would. The client-side dry run is the control:
it does not decode into the typed object, so it reports the claim as configured and tells you
nothing. The post's example is not one a reader can copy, correct, and learn from — it is one that
never reaches the code the post is about.

Step 3 sorts the sixteen spellings into two groups. Refused: `1000TB`, `100TB`, `2TB` and `20TiB`,
because `B` is not part of any suffix. Accepted: `1000T`, `100T`, `2T`, `20Ti`, `1Ti`, `1024Gi`,
`1e12`, `1000G`, `1000k`, `1000m` and the bare `1000`. `1000K` is the one to watch, because it
differs from the accepted `1000k` in the case of a single letter; expect it to be refused, and if
your cluster takes it, that is the more interesting result and worth recording. `1000m` is the other
one worth stopping on: it is accepted, and it asks for one byte. The warning that belongs beside
this feature is not that you might type an extra zero — it is that two of the legal spellings of a
large number differ from a legal spelling of a very small one by a shift key.

Step 4 shows the canonicaliser. `2T` and `20Ti` come back as they went in, because a quantity
remembers which family of suffix it was written with. `1.5Gi` comes back as `1536Mi` and `129e6`
comes back as `129M`, both of them re-expressed with no fractional part and the largest suffix that
loses no precision; `1024Gi` comes back as `1Ti`. The reference predicts the first of those by name
at `quantity-resource.md:53-61`. Then the arithmetic: `20Ti` is 21,990,232,555,520 bytes and `2T` is
2,000,000,000,000, a ratio of 11.0. The post's opening sentence describes a typo that multiplies a
request by eleven, and calls it the difference between two and twenty.

Step 5 binds immediately, because the claim names its volume. The claim's `.status.capacity.storage`
is `1Ti`, copied from the volume rather than measured from anything, and the quota reports `1Ti`
used of `50Ti`. Nothing was provisioned, nothing was formatted, and the directory on the node is
empty. That is the point: every number from here on is an accounting number, and the accounting is
what the post's quota promise is about.

Step 6 collects three answers to one mistake. The literal `1000TB` is refused by the quantity
parser, exactly as in step 2 and with the same message, which is worth seeing on an object that
already exists. `40Ti` is accepted and the quota's `Used` column moves to `40Ti` within a few
seconds. `100Ti` is refused by quota admission, and that message names the ResourceQuota object, the
resource, the amount requested and the limit — a refusal produced entirely inside the API server,
with no storage system consulted and no expansion attempted. The claim's request stays at `40Ti`.
Two of the three ways to get this wrong never reach the feature the post is announcing.

Step 7 is the promise, and it holds. `2Ti` is accepted because it is above `.status.capacity`, and
the quota's used value falls back to `2Ti` — immediately on the next controller sync, not after any
interaction with storage. Read the last two fields carefully: `.status.allocatedResources.storage`
is empty and `.status.allocatedResourceStatuses` is empty, and they have been empty throughout,
because no driver ever started an expansion. The events list has nothing about resizing. So on this
cluster the quota came back for a reason that has nothing to do with the feature: usage followed
`spec` down because `allocatedResources` was never set. The post's sentence is true here, and true
by accident.

Step 8 supplies the missing half. After writing `allocatedResources` to `40Ti` through the status
subresource, the quota's used value should rise to `40Ti` while the claim's `spec` still says `2Ti`
— the "larger value from allocatedResources and PVC.spec.resources" rule, visible. Record whether
that write is accepted, and whether usage can be driven above `hard` this way: admission guards
`spec` on the main resource, and the quota controller computes usage from the stored object, so the
two do not necessarily agree. The five-way state loop answers a different question. If
`ControllerResizeInfeasible`, `NodeResizeInfeasible` and even `NotAState` are all accepted, the list
in the reference is documentation and not validation, and the two names the post invents are
undocumented rather than wrong. If any of them is refused, the reference's five are the whole set
and the post is naming states that cannot exist. Then clearing both fields should return usage to
`2Ti`; if the API refuses to clear `allocatedResources`, that refusal is the finding, because it is
the field the rule says is "only lowered" under conditions.

Step 9 measures the headline claim and finds it correct. The ServiceAccount can `patch` and `update`
PersistentVolumeClaims and can do nothing else: `create` and `delete` on claims are refused, and all
three verbs on PersistentVolumes are refused. Lay that against the five-step drill at
`persistent-volumes.md:468-476` and three of its steps are unavailable to this identity — the two
that edit the volume and the one that deletes the claim. Then both patches succeed, the mistake and
its correction, under an identity with one role, one resource and four verbs. "This requires no
admin intervention" is not marketing: it is the difference between a namespaced `patch` and a
cluster-scoped `delete`, and this step is the measurement.

Step 10 should reproduce every count this file asserts. Two lines matching `storage:` and a number
and `TB`, both in the post. The singular field name five times in the reference and once in the
post; the plural twice in that same reference and once on the concept page. Four of the six strings
at `docs=0`, each with `blog=1` and that one blog being this post; `ControllerResizeFailed` and
`RecoverVolumeExpansionFailure` at `docs=1` and `blog=0`. Zero occurrences of "quota" in the whole
of `persistent-volumes.md` and zero occurrences of "expan" or "resiz" in the whole of
`resource-quotas.md`. The two tab names in the order the page gives them. And one malformed GitHub
URL in the entire tree.

**Read on**

11. [The exercise that owns the gates this one never has to
    check](../2022/01-volume-expansion-ga.md), where expansion reaches GA as three switches instead
    of one, a cluster with no driver accepts an expansion request and does nothing with it forever,
    and the validation boundary around reducing a bound claim is established step by step. Its step
    6 is the floor that step 7 above stands on.

12. [The lab where a volume actually grows](../../labs/08/09-expansion-two-phase.md), on two nodes
    with a working CSI driver, for the half of this story no single node can show: which phase sets
    the pending condition, which clears it, and what the two fields watched above look like when
    something is genuinely resizing.

13. [The other way a claim meets a quota](../2023/12-kubernetes-1-29-volume-attributes-class.md),
    where a ResourceQuota is scoped by volume attributes class rather than by storage class, and an
    unbound claim against no driver is counted anyway — the same accounting machinery this exercise
    drives from the other end.

14. [The other v1.34 graduation that names no gate](08-kubernetes-v1-34-dra-updates.md), published
    eighteen days earlier, where the missing pointer is a documentation page that moved rather than
    a feature-gate file nothing links to. Two graduation announcements in one release, and between
    them not one gate name, KEP number or version range a reader could look up.

15. *Unanswerable from the pin.* `:85` says Kubernetes now retries failed expansions "at slower
    rate" and makes fewer requests to the storage system and the API server. Nothing in the checkout
    gives a number: not the old interval, not the new one, not the backoff shape, not a flag that
    tunes it, and not a metric that exposes it. `persistent-volumes.md:455-458` says only that
    expansion "will be continuously retried". The one sentence in the post that a cluster operator
    could act on is the one with no measurement behind it anywhere in the tree.

**Teardown**

One namespace and two cluster-scoped objects, plus a directory on the node. The volume's reclaim
policy is `Retain`, so deleting the namespace releases it rather than removing it and it has to be
deleted by name; nothing was ever written into it. The status subresource writes in step 8 live on
an object inside the namespace and go with it. The checkout at the pin was only read.

```sh
kubectl delete namespace bw-recover
kubectl delete pv bw-recover
kubectl delete storageclass bw-recover
rm -rf /tmp/bw-recover
ssh zain@10.10.10.180 'sudo rm -rf /srv/bw-recover'
```

If step 8 left `allocatedResources` set and the API refused to clear it, deleting the claim with its
namespace is what clears the quota, and the `ResourceQuota` object goes at the same time, so nothing
is left counting. If a later exercise on this cluster finds a StorageClass called `bw-recover` that
provisions nothing, this is where it came from.
