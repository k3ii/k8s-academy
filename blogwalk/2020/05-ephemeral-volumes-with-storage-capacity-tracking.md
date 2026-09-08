<a id="ephemeral-volumes-with-storage-capacity-tracking"></a>

# Three of this post's paragraphs are now the documentation and its author is a listed reviewer of the page that carries them, the 188 lines that demonstrate anything cannot run at all, and the API reference documents a way out of the one failure the concept page says has none

**Post** — [Ephemeral volumes with storage capacity tracking: EmptyDir on
steroids](https://kubernetes.io/blog/2020/09/01/ephemeral-volumes-with-storage-capacity-tracking/),
1 September 2020, by Patrick Ohly (Intel). 394 lines and 16,001 bytes, the longest walk in the year.
Two alpha features announced together: generic ephemeral volumes, which are a Pod-shaped
PersistentVolumeClaim, and CSI storage capacity tracking, which is how the scheduler learns whether
the claim can be satisfied where it is about to put the Pod.

Almost every other post in this year is measured by what broke. This one is measured by what was
adopted. Its explanation of the feature is now the explanation on
`concepts/storage/ephemeral-volumes.md`, in one place sentence for sentence, and one sentence of it
grew into three paragraphs and a caution. What did not survive is everything downstream of the two
feature gates: the whole worked example, every API-reference link, and the alpha group-version the
second feature shipped in. Read the first half as doctrine and the second half as an artefact.

**As written**

The post opens on a gap. `EmptyDir` gives a Pod scratch space with no size and no choice of driver;
CSI ephemeral volumes, from the January post in this same year, give a Pod a driver-served volume
that cannot participate in scheduling. `Kubernetes 1.19 introduces two new alpha features for
volumes that are conceptually more like the EmptyDir volumes`, and the advantages list runs to seven
bullets, of which the load-bearing ones are that storage `can be local or network-attached`, that
`volumes can have a fixed size that applications are never able to exceed`, and that `the Kubernetes
scheduler itself picks suitable nodes, i.e. there is no need anymore to implement and configure
scheduler extenders and mutating webhooks`.

The mechanism is one new volume source. The post's own example manifest, from the PMEM-CSI branch it
tells you to clone, carries it:

```yaml
  volumes:
  - name: my-csi-volume
    ephemeral:
      volumeClaimTemplate:
        spec:
          accessModes:
          - ReadWriteOnce
          resources:
            requests:
              storage: 4Gi
          storageClassName: pmem-csi-sc-late-binding
```

Four claims are made about what happens next, and all four are the subject of this exercise. First,
`a new controller in the kube-controller-manager waits for Pods which embed such a volume source and
then creates a PVC for that pod`, and `to a CSI driver deployment, that PVC looks like any other, so
no special support is needed`. Second, the name of that PVC is fixed: `Naming of the automatically
created PVCs is deterministic: the name is a combination of Pod name and volume name, with a hyphen
(-) in the middle`, with a stated downside — `The downside is that the name might be in use already.
This is detected by Kubernetes and then blocks Pod startup.` Third, the lifetime is enforced by
ownership: `To ensure that the volume gets deleted together with the pod, the controller makes the
Pod the owner of the volume claim. When the Pod gets deleted, the normal garbage-collection
mechanism also removes the claim and thus the volume.` Fourth, the object is a real claim while it
lives: `As long as these PVCs exist, they can be used like any other volume claim. In particular,
they can be referenced as data source in volume cloning or snapshotting. The PVC object also holds
the current status of the volume.`

On binding mode the post makes a recommendation rather than a rule: both are supported, but `for
ephemeral volumes it makes more sense to use WaitForFirstConsumer: then Pod scheduling can take into
account both node utilization and availability of storage when choosing a node. This is where the
other new feature comes in.`

That other feature is a new object. `The new CSIStorageCapacity alpha API allows storing the
necessary information in etcd where it is available to the scheduler.` Unlike the first feature it
is not free: `storage capacity tracking must be enabled when deploying a CSI driver` — the
`external-provisioner` sidecar has to be told to publish what `GetCapacity` returns — and the driver
must also set `CSIDriver.storageCapacity`. The scheduler then `automatically filters out nodes that
do not have access to enough storage capacity`, which works for generic ephemeral and persistent
volumes but `not for CSI ephemeral volumes because the parameters of those are opaque for
Kubernetes`. The post is careful that this is a probability and not a guarantee: `Because the
Kubernetes scheduler must act on potentially outdated information, it cannot be ensured that the
capacity is still available when a volume is to be created.`

Then a security section, which is the most consequential paragraph in the post. `If users have
permission to create a Pod (directly or indirectly), then they can also create generic ephemeral
volumes even when they do not have permission to create a volume claim. That's because RBAC
permission checks are applied to the controller which creates the PVC, not the original user.` For
the capacity objects the guarantee is weaker still: they are namespaced and RBAC can be scoped, but
`Kubernetes does not check that`, so `drivers are expected to behave and not publish incorrect
data`.

The remaining 188 lines are one worked example on a QEMU cluster brought up from a branch of
`intel/pmem-csi`, with both feature gates set in one environment variable and persistent memory in
the hardware, printing `CSIStorageCapacity` objects through a Go template, one `describe`, the Pod,
the PVC, and the PVC's `ownerReferences`. The post closes with `Both features are under development`
and two KEPs.

**As it runs now**

**The volume source still has exactly one field, and it is the post's field.** At the pin
`EphemeralVolumeSource` is a one-field type — `reference/kubernetes-api/core/pod-v1.md:1344-1358`
lists `volumeClaimTemplate` and nothing else — and generic ephemeral volumes carry `{{<
feature-state for_k8s_version="v1.23" state="stable" >}}` at
`concepts/storage/ephemeral-volumes.md:145`. Everything under `ephemeral:` in the post's manifest is
applied verbatim in the *Do* block below. The pin's own example at `:165-191` is the same
construction with `metadata.labels` added and a `busybox` image in place of the driver test image.

**Three of the post's paragraphs are now that page.** Compare the post's fourth claim with
`ephemeral-volumes.md:220-223`. The pin reads `While these PVCs exist, they can be used like any
other PVC. In particular, they can be referenced as data source in volume cloning or snapshotting.
The PVC object also holds the current status of the volume.` Two edits in three sentences: `As long
as` became `While`, and `any other volume claim` became `any other PVC`. The naming paragraph at
`:227-232` is the post's naming paragraph with `Pod name` given an article and one worked name
inserted. The ownership paragraph at `:211-218` is the post's, restated through the
garbage-collection concept page. This is not a post that agrees with the documentation. It is a post
the documentation was written from.

**And the author is a listed reviewer of both pages whose prose came from this post.** `pohly` is
the fifth name in the `reviewers:` list of `ephemeral-volumes.md:2-7` and the fifth name in
`storage-capacity.md:2-7`. That is worth naming because it explains the shape of everything above:
the absorption was not a coincidence of good phrasing, and the parts of the post that rotted are
exactly the parts no page owns.

**One sentence of the post became three paragraphs and a caution.** The post's stated downside was
two sentences long. At the pin it is `:234-248`: the collision is worked out with names — `a Pod
"pod-a" with volume "scratch" and another Pod with name "pod" and volume "a-scratch" both end up
with the same PVC name "pod-a-scratch"` — the detection mechanism is named (`This check is based on
the ownership relationship`), the consequence is stated (`without the right PVC, the Pod cannot
start`), and a `caution` shortcode tells you to take care when naming. The post said the name might
be in use. The pin says it might be in use *because of another Pod*, which the post did not.

**And the API reference gives you a way out of that collision which the concept page says does not
exist.** `ephemeral-volumes.md:239-243` is flat: `An existing PVC is not overwritten or modified.
But this does not resolve the conflict because without the right PVC, the Pod cannot start.`
`pod-v1.md:1355` is not: `An existing PVC with that name that is not owned by the pod will *not* be
used for the pod to avoid using an unrelated volume by mistake. Starting the pod is then blocked
until the unrelated PVC is removed. If such a pre-created PVC is meant to be used by the pod, the
PVC has to updated with an owner reference to the pod once the pod exists.` Missing verb reproduced
as written. Two documents, one field, and one of them documents a recovery the other denies. This is
the cheapest disagreement in the year to settle and the *Do* block settles it.

**The page now tells you how to keep the volume after the claim dies, and names the value wrong.**
`:216-218` adds a sentence the post has no equivalent of: `You can create quasi-ephemeral local
storage using a StorageClass with a reclaim policy of retain: the storage outlives the Pod, and in
this case you need to ensure that volume clean up happens separately.` The field takes `Delete` or
`Retain` — `concepts/storage/storage-classes.md:130` — and lower-case `retain` in backticks occurs
exactly once in the pinned tree, here. A reader who copies it gets a rejection, and the *Do* block
collects it.

**The claim template's metadata is restricted, and the restriction is documented where the post's
readers would not look.** `pod-v1.md:1882`: `May contain labels and annotations that will be copied
into the PVC when creating it. No other fields are allowed and will be rejected during validation.`
The post's manifest has no `metadata` at all, so it never met this; the pin's example has labels, so
it never meets it either. It is a validation rule with no example that trips it.

**Both gates are gone, which makes the post's example unrunnable rather than merely dated.**
`GenericEphemeralVolume` reached stable in 1.23 and is `removed: true`; `CSIStorageCapacity` reached
stable in 1.24 and is `removed: true`. The post's setup line sets both to `true` in one environment
variable that a 1.19 test harness passes through to the components. A v1.37 component handed an
unrecognised gate does not ignore it, and the last *Do* step shows what it does instead.

**The capacity object changed group-version twice and gained a field the post's object did not
have.** The post links the alpha object as `csistoragecapacity-v1alpha1-storage-k8s-io`. At the pin
the only page is `reference/kubernetes-api/storage/csi-storage-capacity-v1.md`, the `v1` API has
been available since v1.24, and `reference/using-api/deprecation-guide.md:55-61` records that
`storage.k8s.io/v1beta1` stopped being served at v1.27 with `No notable changes`. The alpha version
the post used has no entry in that guide at all, for the reason the sibling exercise on [the most
churned API in the archive](03-kubernetes-1-18-feature-api-priority-and-fairness-alpha.md)
establishes. The new field is `maximumVolumeSize` (`csi-storage-capacity-v1.md:59-60`), reported per
CSI spec 1.4.0, sitting beside a `capacity` field whose own description is still pinned to `CSI spec
1.2`.

**And the concept page describes the comparison the scheduler no longer makes first.**
`storage-capacity.md:63-66` says the check `only compares the size of the volume against the
capacity listed in CSIStorageCapacity objects with a topology that includes the node`.
`csi-storage-capacity-v1.md:39` says `The scheduler compares the MaximumVolumeSize against the
requested size of pending volumes to filter out unsuitable nodes. If MaximumVolumeSize is unset, it
falls back to a comparison against the less precise Capacity.` The concept page is describing the
fallback as the rule.

**The half of the post that says it is under development still is, under a third name.** The filter
the post describes shipped. The scoring did not. `VolumeCapacityPriority` sat at alpha, default
false, from 1.21 to 1.32 — twelve releases — and is `removed: true` with the note `This feature is
renamed to StorageCapacityScoring in v1.33`. `StorageCapacityScoring` is alpha from 1.33 to 1.36 and
beta, default true, from 1.37, which is the pin's own release. `storage-capacity.md` does not
mention it once; the only prose is `concepts/scheduling-eviction/scheduling-framework.md:126-136`
and a note at `reference/scheduling/config.md:161-165`, and that note describes the older behaviour
— it `prioritizes the smallest PVs that can fit the requested volume size`, where the gate file's
own body says the rename `added support to dynamically provisioned storage`.

**One line of the post's sample output can no longer be produced by any cluster.** The `describe`
output prints `Self Link: /apis/storage.k8s.io/v1alpha1/namespaces/default/...`.
`reference/kubernetes-api/definitions/object-meta-v1-meta.md:92` reads `Deprecated: selfLink is a
legacy read-only field that is no longer populated by the system.` The gate that blanked it,
`RemoveSelfLink`, went stable in 1.24 and is itself `removed: true` — a field removed by a gate that
has since been removed for having finished.

**The list of ephemeral volume kinds the post opens against grew by one.**
`ephemeral-volumes.md:42-56` now lists five kinds, and the one the post has no equivalent of is
`image` at `:49-50`, which `allows mounting container image files or artifacts, directly to a Pod`.
The post's framing — Kubernetes' built-in ephemeral volumes are `limited to what is implemented
inside Kubernetes` — is still the framing, and the project has since implemented one more thing
inside Kubernetes.

**The security warning survived intact and acquired the mitigation the post left out.** `:252-256`
carries the post's escalation in the pin's words, and the post's link to
`/docs/concepts/storage/ephemeral-volumes#security` still resolves to it. Then `:258-260` adds: `The
normal namespace quota for PVCs still applies, so even if users are allowed to use this new
mechanism, they cannot use it to circumvent other policies.` The word `still` is doing the work
there — it reads as continuity, not as an addition — so this is most likely a mitigation that
existed on the day the post was published and went unmentioned. The *Do* block measures whether the
quota bites on a v1.37 cluster; what a 1.19 cluster would have done is not answerable from the pin.

**What this exercise does not cover, and where it lives.** Dynamic provisioning, the `provisioner`
field and what a class that provisions nothing is for belong to [the 2016 post that also became the
documentation almost word for word](../2016/10-dynamic-provisioning-and-storage-in-kubernetes.md),
and the four-case matrix of how a claim acquires a class belongs to [the 2017 post on storage
classes](../2017/01-dynamic-provisioning-and-storage-classes-kubernetes.md). Snapshotting and
cloning an ephemeral volume's claim — which the post's fourth claim says you can do — is the subject
of [the 2018 snapshot post, whose finding is that a cluster can lack the `VolumeSnapshot` kind
entirely](../2018/08-volume-snapshot-alpha.md), and is read here, not run for that reason. CSI
ephemeral volumes, the feature this post positions itself against, are the January 2020 post in this
year's census, which carries a `read` verdict and no exercise; the distinction between the two
volume kinds is stated here only as far as the pin states it at `ephemeral-volumes.md:62-69`.

**The diff, and why**

The archive has a case for a post that was retired by being agreed with, and [the 2016 post on
dynamic provisioning](../2016/10-dynamic-provisioning-and-storage-in-kubernetes.md) already carries
it: a post whose prose became the current documentation almost word for word. This post is the same
case with one thing added that the 2016 one cannot show. There, the absorption had to be inferred
from the wording. Here the post's author is on the reviewer list of the page that carries those
paragraphs (`ephemeral-volumes.md:7`, `storage-capacity.md:7`), so the route from post to page is
visible in the file. That is the useful lesson for reading the rest of the archive: when a 2020 post
reads like documentation, check the `reviewers:` block of the page it reads like before concluding
anything about influence.

What is still right is nearly all of the API half. One field on the volume source, the controller
that watches for it, the Pod as owner, the hyphenated name, the claim usable like any other claim:
all of it holds at v1.37, and the feature has been stable since v1.23. The post named a gap in what
Kubernetes could do, described the mechanism that closed it, and the mechanism is the mechanism. Six
of its nine internal links still resolve, including the `#security` anchor into a section that has
since grown a paragraph, and `persistent-volumes.md:1115` for the snapshot support its fourth claim
promises.

What broke is the demonstration, and it broke completely rather than partially. 188 of the post's
394 lines are an example driven by a test harness at a tag, against a driver that needs persistent
memory, with two feature gates that no longer exist. A removed gate is not an ignored gate. Its
three broken links are the three API-reference links, and they fail three different ways:
`/docs/reference/generated/` is not a path the pin has at all, two of the three hardcode `v1.19`
into the URL, and the third names `ephemeralvolumesource-v1alpha1-core` when `v1alpha1-core` has
zero occurrences in the whole pinned documentation tree. Separately, the `Self Link:` line in its
sample output cannot be produced by any supported cluster, because a gate went stable to blank that
field and has itself since been removed for having finished. There is also an HTML comment at `:145`
of the published post, `TODO: update the link with a revision once ... pull/450 is merged`, which is
visible in the source of the page and has been there for six years. None of this touches the API
half. It is worth separating the two, because a reader who tries the example and fails will conclude
the feature is broken, and the feature is stable.

What was overtaken by stasis is the sentence the post ends on: `Both features are under
development.` For the two APIs that resolved — 1.23 and 1.24. For the scheduler behaviour that the
capacity data was collected to enable, it did not. `VolumeCapacityPriority` was alpha and off by
default from 1.21 through 1.32, twelve consecutive releases, and left not by graduating but by being
renamed. Its successor `StorageCapacityScoring` is alpha from 1.33 and beta from 1.37, so at the pin
the answer to `under development` is still yes, under a name that did not exist when the question
was asked. The concept page for storage capacity does not mention the successor once. Six years of
development are recorded in two gate files and a paragraph of the scheduling framework page, and
nowhere on the page a reader of this post would open.

And then the fourth thing, which the sibling exercise on [the API that changed shape three times in
three releases](03-kubernetes-1-18-feature-api-priority-and-fairness-alpha.md) found first and which
this post multiplies: the pin disagrees with itself. Five times, on one feature. The API reference
documents an owner-reference recovery from a naming collision that the concept page says is not
possible. The concept page says the scheduler compares the volume size against `capacity`, while the
API reference says it compares `maximumVolumeSize` first and only falls back to `capacity`. The
concept page spells the reclaim policy `retain` where the field takes `Retain`. The scheduler
configuration page describes `StorageCapacityScoring` in the terms of the predecessor it replaced.
And two fields of one object are documented against two different versions of the CSI specification,
1.2 and 1.4.0, one line apart. Four of the five are on hand-written pages, which is where a reader
looks first. The pattern across this year's exercises so far is now clear enough to state plainly:
on a feature that has been revised for six years, the concept page is the oldest text in the set,
and where it conflicts with the generated API reference the API reference is the one that was
regenerated.

The exercise is built around the one disagreement that a two-node cluster can actually settle.
Everything about capacity tracking needs a CSI driver that implements `GetCapacity`, and the lab has
none, so that half is read. The naming collision, the owner-reference recovery, the garbage
collection, the reclaim-policy spelling, the security escalation and its quota mitigation all need
nothing but a claim and a Pod, and the lab has both.

**The ladder**

Five gates, and they end in three different states. Transcribed from
`reference/command-line-tools-reference/feature-gates/`:

```
GenericEphemeralVolume    alpha  false  1.19 - 1.20
                          beta   true   1.21 - 1.22
                          stable true   1.23 - 1.24   removed: true

CSIStorageCapacity        alpha  false  1.19 - 1.20
                          beta   true   1.21 - 1.23
                          stable true   1.24 - 1.27   removed: true

VolumeCapacityPriority    alpha  false  1.21 - 1.32   removed: true

StorageCapacityScoring    alpha  false  1.33 - 1.36
                          beta   true   1.37 -        (no removed key)

RemoveSelfLink            alpha  false  1.16 - 1.19
                          beta   true   1.20 - 1.23
                          stable true   1.24 - 1.29   removed: true
```

The two gates the post asks you to set are the top two, and they are the ordinary shape: alpha off,
beta on, stable on, retired. Read the `fromVersion` of their alpha rows against the post's date. The
1.19 release announcement is `Kubernetes 1.19: Accentuate the Paw-sitive`, dated 2020-08-26 in this
year's census — six days before this post. So both gates became settable at all the week the post
was written, which is what makes the demonstration's death total rather than partial: nothing in it
predates the gate.

The third and fourth rows are the shape this year has not produced before. `VolumeCapacityPriority`
has one stage. Alpha, default false, `fromVersion: "1.21"`, `toVersion: "1.32"` — twelve releases in
a row without a promotion — and then `removed: true`. Every other removed gate in this exercise
earned its removal by reaching stable and staying there long enough to be unconditional. This one
was removed while still alpha, and the body says why in one sentence: `This feature is renamed to
StorageCapacityScoring in v1.33.` The successor's file carries no `removed:` key at all and its beta
row has no `toVersion`, which is how the pin writes *this is where the feature is now*: alpha 1.33
to 1.36, beta and default true from 1.37, the pin's own release. So the behaviour is one release
into beta, sixteen releases after it first appeared as alpha, and the gate history reads as two
features because the name changed halfway.

That is worth naming as a distinct rung, because a reader reconstructing a feature's history from
gate files alone would count these as separate features and conclude that the first one failed. It
did not fail. It was renamed, and the only record of the continuity is one sentence in the body of
the file for the name that went away — a file whose `_build:` block says `list: never` and `render:
false`, so it is not on the feature-gate page a reader would search. The rule this yields for the
rest of the archive: when a gate is `removed: true` without ever having reached stable, read its
body before concluding the feature was dropped.

The fifth row is in the ladder for a reason that has nothing to do with storage. It is the gate that
blanked the `Self Link:` field the post's own sample output prints. It went stable at 1.24 and was
removed after 1.29, so at the pin the gate that removed the field is itself gone, and the field is
still in the API — `object-meta-v1-meta.md:92` still documents `selfLink`, as `Deprecated: selfLink
is a legacy read-only field that is no longer populated by the system.` A ladder can therefore
explain a difference between a post's output and the reader's output while leaving no trace in
either the API or the gate list.

What no ladder in this set can say: whether capacity-aware scheduling ever did anything on a real
cluster. The gates record when the API and the filter became available. Nothing here records
adoption, and the concept page for storage capacity is silent on the scoring successor, so the only
statement the pin supports is that the plumbing is stable and the behaviour that consumes it is in
beta.

**Topology**

[`pair`](../../strands/lab-topologies.md#pair): a control-plane node at `10.10.10.130` and one
worker at `10.10.10.131`. Two nodes, because the interesting half of the mechanism is *which* node
the volume picks. A claim in `WaitForFirstConsumer` mode binds when a Pod that uses it is scheduled,
and with one node that is not a choice; with a worker holding the only local volume, the Pod goes
where the storage is, and you can read the node out of the Pod and the node out of the volume and
see that they agree. `lab-topologies.md` calls this row the daily driver.

The post's own example cannot be run and this exercise does not try. It needs the `pmem-csi` driver
at a branch tag, persistent memory on the node, and a 1.19 test harness. What replaces it is the
smallest apparatus that satisfies the API: a StorageClass whose `provisioner` is
`kubernetes.io/no-provisioner`, `volumeBindingMode: WaitForFirstConsumer`, and one `local`
PersistentVolume on the worker pinned there by `nodeAffinity` — the same construction [the 2019
exercise on raw block volumes](../2019/03-raw-block-volume-support-to-beta.md) builds and [the 2016
dynamic-provisioning exercise](../2016/10-dynamic-provisioning-and-storage-in-kubernetes.md)
explains. Be clear about what that costs. `pod-v1.md:3056` lists as one condition for using a
generic ephemeral volume that `the storage driver supports dynamic volume provisioning through a
PersistentVolumeClaim`, and a class that provisions nothing does not. Nothing in the steps below
depends on it: the controller creates the PVC whether or not anything can provision for it, and a
pre-created `local` PV satisfies the claim in its place. The one thing you lose is the case where
the claim cannot be satisfied at all, and step 6 produces that case deliberately.

Capacity tracking is read, not run, for the same reason at one remove: a `CSIStorageCapacity` object
is published by a CSI driver that implements the `GetCapacity` call, and this cluster runs no CSI
driver. Step 1 confirms that the API is served and that nothing is publishing into it, which is the
honest end of that thread on this hardware.

The control-plane node in this row carries the default `NoSchedule` taint and nothing below
tolerates it, so every Pod lands on the worker. That is wanted here — it is what makes the volume's
node affinity and the Pod's node the same answer — but it means the `Pending` states you read in
steps 6 and 7 are about claims, not about taints. Check the reason before concluding either way.

Provision with the five steps at [`#provision`](../../strands/lab-topologies.md#provision), then the
node baseline at [`#node-baseline-steps`](../../strands/lab-topologies.md#node-baseline-steps), then
`ssh zain@10.10.10.130`. Step 10 edits the apiserver's static Pod manifest and restores it; if you
stop before the restore, the control plane stays down.

**Do**

1. Ask the cluster what it serves for the capacity half before building anything, because the answer
   is the whole of that half. Four questions: is the kind there, which group-version, does it carry
   the field the post's object did not have, and is anything publishing into it.

   ```bash
   kubectl api-resources --api-group=storage.k8s.io -o wide | grep -i capacity
   kubectl get --raw /apis/storage.k8s.io/ | python3 -c 'import json,sys
   for v in json.load(sys.stdin)["versions"]: print(v["groupVersion"])'
   kubectl get --raw /apis/storage.k8s.io/v1beta1 2>&1 | head -2
   kubectl explain csistoragecapacity --recursive 2>&1 | grep -iE 'maximumVolumeSize|capacity|nodeTopology'
   kubectl get csistoragecapacities -A
   ```

2. Build the apparatus. A namespace to keep the whole exercise in, a class that provisions nothing
   and binds late, a directory per volume on the worker, and five `local` PersistentVolumes pinned
   to it with `Retain`. Five, because a released `Retain` volume does not go back into the pool and
   no step below reuses one. Set `W` to your worker's node name as `kubectl get nodes` prints it.

   ```bash
   ssh zain@10.10.10.131 'for i in 1 2 3 4 5; do sudo mkdir -p /mnt/bw-eph/vol$i; done; ls /mnt/bw-eph'
   kubectl create namespace bw-eph
   W=$(kubectl get nodes -o json | python3 -c 'import json,sys
   print([n["metadata"]["name"] for n in json.load(sys.stdin)["items"]
          if "node-role.kubernetes.io/control-plane" not in n["metadata"]["labels"]][0])')
   echo "worker is $W"
   kubectl apply -f - <<YAML
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: bw-eph
   provisioner: kubernetes.io/no-provisioner
   volumeBindingMode: WaitForFirstConsumer
   reclaimPolicy: Retain
   YAML
   for i in 1 2 3 4 5; do
     kubectl apply -f - <<YAML
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: bw-eph-vol$i
   spec:
     capacity:
       storage: 1Gi
     accessModes: ["ReadWriteOnce"]
     persistentVolumeReclaimPolicy: Retain
     storageClassName: bw-eph
     local:
       path: /mnt/bw-eph/vol$i
     nodeAffinity:
       required:
         nodeSelectorTerms:
         - matchExpressions:
           - key: kubernetes.io/hostname
             operator: In
             values: ["$W"]
   YAML
   done
   kubectl get pv -o wide
   ```

3. Apply the post's manifest, translated only in the ways it has to be: the driver's image becomes
   `busybox`, the driver's class becomes `bw-eph`, and the request shrinks to fit a 1Gi volume.
   Everything under `ephemeral:` is the post's shape. Then ask four questions of the cluster that
   the post answers in prose: what is the claim called, who owns it, what did it bind to, and where
   did the Pod land.

   ```bash
   kubectl -n bw-eph apply -f - <<YAML
   kind: Pod
   apiVersion: v1
   metadata:
     name: bw-app
   spec:
     containers:
     - name: my-frontend
       image: busybox
       command: ["sleep", "3600"]
       volumeMounts:
       - mountPath: "/data"
         name: scratch
     volumes:
     - name: scratch
       ephemeral:
         volumeClaimTemplate:
           spec:
             accessModes: ["ReadWriteOnce"]
             storageClassName: bw-eph
             resources:
               requests:
                 storage: 1Gi
   YAML
   kubectl -n bw-eph get pvc
   OWN='
   import json,sys
   o=json.load(sys.stdin)
   m=o["metadata"]
   print("pvc:", m["name"])
   for r in m.get("ownerReferences") or [{}]:
       print("  owner:", r.get("kind"), r.get("name"), "controller=%s" % r.get("controller"),
             "blockOwnerDeletion=%s" % r.get("blockOwnerDeletion"))
   print("  volume:", o["spec"].get("volumeName"), "phase:", o["status"]["phase"])
   '
   kubectl -n bw-eph get pvc bw-app-scratch -o json | python3 -c "$OWN"
   kubectl -n bw-eph get pod bw-app -o json | python3 -c 'import json,sys
   print("pod node:", json.load(sys.stdin)["spec"]["nodeName"])'
   kubectl get pv -o json | python3 -c 'import json,sys
   for p in json.load(sys.stdin)["items"]:
       c=p["spec"].get("claimRef") or {}
       if c: print(p["metadata"]["name"], "->", c.get("namespace","")+"/"+c.get("name",""),
                   p["status"]["phase"])'
   ```

4. The title's payload. Write something into the volume, delete the Pod, and watch three different
   lifetimes come apart: the claim is garbage-collected because the Pod owned it, the volume is not
   deleted because the class says `Retain`, and the bytes are still on the worker's disk because
   nothing was ever asked to remove them. Note the volume name from step 3 as `V` before you start.

   ```bash
   kubectl -n bw-eph exec bw-app -- sh -c 'echo "written by bw-app at $(date)" > /data/hello; cat /data/hello'
   V=$(kubectl -n bw-eph get pvc bw-app-scratch -o jsonpath='{.spec.volumeName}')
   kubectl -n bw-eph delete pod bw-app --wait=true
   sleep 10
   kubectl -n bw-eph get pvc
   kubectl get pv $V -o custom-columns='NAME:.metadata.name,PHASE:.status.phase,POLICY:.spec.persistentVolumeReclaimPolicy,CLAIM:.spec.claimRef.name'
   P=$(kubectl get pv $V -o jsonpath='{.spec.local.path}')
   echo "backing directory is $P"
   ssh zain@10.10.10.131 "sudo cat $P/hello"
   ```

5. Settle the reclaim-policy spelling. `ephemeral-volumes.md:217` tells you to use a class with a
   reclaim policy of `retain`; the enum at `storage-classes.md:130` is `Delete` or `Retain`. Apply
   the page's spelling and then the enum's, and record which of the two the apiserver keeps and what
   it says about the other. Name the component that answered.

   ```bash
   kubectl apply -f - <<YAML
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: bw-eph-lower
   provisioner: kubernetes.io/no-provisioner
   volumeBindingMode: WaitForFirstConsumer
   reclaimPolicy: retain
   YAML
   kubectl apply -f - <<YAML
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: bw-eph-upper
   provisioner: kubernetes.io/no-provisioner
   volumeBindingMode: WaitForFirstConsumer
   reclaimPolicy: Retain
   YAML
   kubectl get storageclass | grep bw-eph
   ```

6. Reproduce the collision the pin works out by name. `ephemeral-volumes.md:234-237` says a Pod
   `pod-a` with volume `scratch` and a Pod `pod` with volume `a-scratch` both end up with the same
   PVC name `pod-a-scratch`. Create them in that order and read why the second one does not start.
   The distinction to hold on to: the claim exists and is `Bound`, so this is not a storage
   shortage. `$OWN` is the reader defined in step 3 and the next three steps reuse it, so stay in
   one shell.

   ```bash
   for spec in "pod-a scratch" "pod a-scratch"; do
     set -- $spec
     kubectl -n bw-eph apply -f - <<YAML
   kind: Pod
   apiVersion: v1
   metadata:
     name: $1
   spec:
     containers:
     - name: c
       image: busybox
       command: ["sleep", "3600"]
       volumeMounts:
       - mountPath: "/data"
         name: $2
     volumes:
     - name: $2
       ephemeral:
         volumeClaimTemplate:
           spec:
             accessModes: ["ReadWriteOnce"]
             storageClassName: bw-eph
             resources:
               requests:
                 storage: 1Gi
   YAML
     sleep 15
   done
   kubectl -n bw-eph get pod pod-a pod -o wide
   kubectl -n bw-eph get pvc pod-a-scratch -o json | python3 -c "$OWN"
   kubectl -n bw-eph get events --field-selector involvedObject.name=pod -o custom-columns='REASON:.reason,MSG:.message'
   ```

7. The centrepiece, and the one disagreement in the pin a two-node cluster can settle.
   `ephemeral-volumes.md:239-243` says an existing PVC `is not overwritten or modified` and that
   this `does not resolve the conflict because without the right PVC, the Pod cannot start`.
   `pod-v1.md:1355` says that `if such a pre-created PVC is meant to be used by the pod, the PVC has
   to updated with an owner reference to the pod once the pod exists` — missing verb as written —
   and that this `may be useful when manually reconstructing a broken cluster`. So: create the PVC
   first, create the Pod, confirm it does not start, then add the owner reference by hand and see
   which document was right. The `uid` matters; an owner reference with the wrong `uid` is not the
   same Pod.

   ```bash
   kubectl -n bw-eph apply -f - <<YAML
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: bw-recover-scratch
   spec:
     accessModes: ["ReadWriteOnce"]
     storageClassName: bw-eph
     resources:
       requests:
         storage: 1Gi
   YAML
   kubectl -n bw-eph apply -f - <<YAML
   kind: Pod
   apiVersion: v1
   metadata:
     name: bw-recover
   spec:
     containers:
     - name: c
       image: busybox
       command: ["sleep", "3600"]
       volumeMounts:
       - mountPath: "/data"
         name: scratch
     volumes:
     - name: scratch
       ephemeral:
         volumeClaimTemplate:
           spec:
             accessModes: ["ReadWriteOnce"]
             storageClassName: bw-eph
             resources:
               requests:
                 storage: 1Gi
   YAML
   sleep 20
   kubectl -n bw-eph get pod bw-recover -o wide
   kubectl -n bw-eph get events --field-selector involvedObject.name=bw-recover -o custom-columns='REASON:.reason,MSG:.message'
   U=$(kubectl -n bw-eph get pod bw-recover -o jsonpath='{.metadata.uid}')
   kubectl -n bw-eph patch pvc bw-recover-scratch --type=merge -p "{\"metadata\":{\"ownerReferences\":[{\"apiVersion\":\"v1\",\"kind\":\"Pod\",\"name\":\"bw-recover\",\"uid\":\"$U\",\"controller\":true,\"blockOwnerDeletion\":true}]}}"
   sleep 30
   kubectl -n bw-eph get pod bw-recover -o wide
   kubectl -n bw-eph get pvc bw-recover-scratch -o json | python3 -c "$OWN"
   ```

8. The security claim, which is the part of the post the documentation kept word for word.
   `ephemeral-volumes.md:252-253` says users who can create Pods can create PVCs indirectly `even if
   they do not have permission to create PVCs directly`, because the permission check falls on the
   controller. Give a ServiceAccount Pods and nothing else, confirm with `auth can-i` that it cannot
   create a claim, then have it create a Pod that creates a claim.

   ```bash
   kubectl -n bw-eph create serviceaccount bw-user
   kubectl -n bw-eph create role bw-pods-only --verb=create,get,list,watch,delete --resource=pods
   kubectl -n bw-eph create rolebinding bw-user-pods --role=bw-pods-only --serviceaccount=bw-eph:bw-user
   SA=system:serviceaccount:bw-eph:bw-user
   kubectl -n bw-eph auth can-i create pods --as=$SA
   kubectl -n bw-eph auth can-i create persistentvolumeclaims --as=$SA
   kubectl -n bw-eph apply --as=$SA -f - <<YAML
   kind: Pod
   apiVersion: v1
   metadata:
     name: bw-esc
   spec:
     containers:
     - name: c
       image: busybox
       command: ["sleep", "3600"]
       volumeMounts:
       - mountPath: "/data"
         name: scratch
     volumes:
     - name: scratch
       ephemeral:
         volumeClaimTemplate:
           spec:
             accessModes: ["ReadWriteOnce"]
             storageClassName: bw-eph
             resources:
               requests:
                 storage: 1Gi
   YAML
   sleep 15
   kubectl -n bw-eph get pvc bw-esc-scratch -o json | python3 -c "$OWN"
   ```

9. The mitigation the post did not mention and the page added. `ephemeral-volumes.md:258-260` says
   the namespace quota for PVCs `still applies`, so the escalation in step 8 cannot be used to get
   round other policies. Set a per-class claim quota of zero — the resource name comes from
   `resource-quotas.md:184` — delete the Pod from step 8 and its claim, and try again as the same
   ServiceAccount. What you are recording is where the refusal surfaces: the Pod is admitted by a
   policy the quota does not cover, and the claim is created by a controller the user is not.

   ```bash
   kubectl -n bw-eph delete pod bw-esc --wait=true
   sleep 10
   kubectl -n bw-eph apply -f - <<YAML
   apiVersion: v1
   kind: ResourceQuota
   metadata:
     name: bw-no-eph-claims
   spec:
     hard:
       bw-eph.storageclass.storage.k8s.io/persistentvolumeclaims: "0"
   YAML
   kubectl -n bw-eph describe resourcequota bw-no-eph-claims
   kubectl -n bw-eph apply --as=$SA -f - <<YAML
   kind: Pod
   apiVersion: v1
   metadata:
     name: bw-esc2
   spec:
     containers:
     - name: c
       image: busybox
       command: ["sleep", "3600"]
       volumeMounts:
       - mountPath: "/data"
         name: scratch
     volumes:
     - name: scratch
       ephemeral:
         volumeClaimTemplate:
           spec:
             accessModes: ["ReadWriteOnce"]
             storageClassName: bw-eph
             resources:
               requests:
                 storage: 1Gi
   YAML
   sleep 20
   kubectl -n bw-eph get pod bw-esc2 -o wide
   kubectl -n bw-eph get pvc | grep bw-esc2 || echo "no claim for bw-esc2"
   kubectl -n bw-eph get events --field-selector involvedObject.name=bw-esc2 -o custom-columns='REASON:.reason,MSG:.message'
   ```

10. The guardrail, and the reason the post's example is not merely dated. Hand the apiserver the
    post's own gate line and read what a v1.37 component does with two names that no longer exist.
    Back the manifest up first. The restore at the end is not optional.

    ```bash
    kubectl get --raw /metrics | grep -oE "GenericEphemeralVolume|CSIStorageCapacity" | sort -u || echo "not reported here"
    sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/kube-apiserver.yaml.bak
    sudo sed -i '/- kube-apiserver$/a\    - --feature-gates=CSIStorageCapacity=true,GenericEphemeralVolume=true' /etc/kubernetes/manifests/kube-apiserver.yaml
    grep -c feature-gates /etc/kubernetes/manifests/kube-apiserver.yaml
    sleep 30
    kubectl get --raw /readyz 2>&1 | head -2
    sudo crictl logs --tail 15 $(sudo crictl ps -a --name kube-apiserver -q | head -1) 2>&1 | tail -15
    sudo cp /root/kube-apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml
    sleep 30
    kubectl get --raw /readyz
    ```

**Expect**

Step 1 is the end of the capacity thread and should be read as an answer, not a disappointment. The
kind should be served, the group listing should show `v1` among the storage group-versions, and
`v1beta1` should refuse — `deprecation-guide.md:55-61` records that it stopped being served at v1.27
with `No notable changes`, so the alpha version the post links is a version behind a version that
has itself been retired. The `explain` output is the point: record whether `maximumVolumeSize` is
there. It is the field the post's object did not have and the field `csi-storage-capacity-v1.md:39`
says the scheduler now compares first. The last command should list nothing at all, in any
namespace. No CSI driver here implements `GetCapacity`, so nothing publishes, and an empty list is
what a cluster with no capacity-aware driver looks like. Everything the post says about scheduling
on capacity is unobservable from here and stays unobserved.

Step 2 should print five `Available` volumes and one class. If `kubectl get pv` shows them as
`Pending` or shows nothing, the class name in the PV and the class name in the StorageClass have
drifted apart. The `$W` extraction picks the first node without the control-plane label; on `pair`
there is exactly one, and if it prints an index error your worker is labelled unusually and you
should set `W` by hand.

Step 3 is the post's four prose claims turned into four printed facts, and all four should hold. The
claim should be called `bw-app-scratch`, which is the Pod name and the volume name with a hyphen
between them. Its single owner reference should be `Pod bw-app` with `controller=True` and
`blockOwnerDeletion=True`. It should be `Bound` to one of the five volumes. And the Pod's node and
that volume's `nodeAffinity` target should be the same machine, which is the whole reason for two
nodes. Note the volume name; step 4 needs it. What you will not see is any trace of who created the
claim: the owner reference names the Pod, not the controller that acted, so the security consequence
in step 8 is invisible in the object it applies to.

Step 4 is three lifetimes coming apart in one screen, and it is worth reading them separately. After
the Pod is deleted, `kubectl get pvc` should be empty — the garbage collector removed the claim
because the Pod owned it, which is `ephemeral-volumes.md:211-216` behaving as written. The volume
should not be gone: expect a phase of `Released` and a `claimRef` still naming a claim that no
longer exists, because the class says `Retain`. And the file should still be readable over `ssh`,
because `Retain` means nobody was asked to remove anything. That third fact is what
`ephemeral-volumes.md:216-218` is pointing at when it says the storage outlives the Pod and clean up
is now yours. A `Released` volume with a stale `claimRef` is not available to the next claim either,
which is why step 2 built five.

Step 5 should end with exactly one of the two classes present. Record which. Whatever the apiserver
says about the other, the message is coming from validation in the apiserver and not from the
`kubectl` in your hand, and if the lower-case spelling is the one that lost, note that the page
which sent you to it is a concept page while the enum lives on a different concept page. One
sentence of documentation, one lower-case letter, and a class that never gets created.

Step 6: `pod-a` should be `Running` and `pod` should not. The claim `pod-a-scratch` should be
`Bound` with `pod-a` as its owner, and that is the point — there is a healthy claim of the right
name in the namespace, four unused volumes beside it, and a Pod that cannot start anyway. Read the
events on `pod` and record the wording. Then hold the two facts together: the conflict is decided by
ownership, and ownership is decided by which Pod got there first. Nothing about the second Pod is
wrong.

Step 7 is the disagreement, and the sequence matters more than the result. Before the patch,
`bw-recover` should not be running, and the events should say something about the claim not being
owned by the Pod — that much both documents agree on. After the patch, record what happens.
`ephemeral-volumes.md:239-243` predicts nothing changes: the Pod cannot start without the right PVC,
full stop. `pod-v1.md:1355` predicts the Pod starts, because a pre-created PVC with an owner
reference to the Pod is the documented recovery. One of those two pages is wrong about the software
in front of you, and after this step you will know which. Give it the full thirty seconds; the
kubelet is not watching the PVC, so the Pod has to be re-evaluated before anything moves. If it does
start, the concept page's flat denial is the error, and the caution at `:245-248` telling you to
avoid the collision is advice given because the recovery went unmentioned rather than because none
exists.

Step 8 should show `no` for claims and `yes` for Pods, and then a claim called `bw-esc-scratch`
owned by `Pod bw-esc`. Two commands that contradict each other, and both are correct: the
ServiceAccount cannot create a claim, and a claim exists because of something the ServiceAccount
did. This is the post's own security paragraph, carried into the documentation and still there six
years later, and it takes four commands to see. Note that the claim's owner reference names `bw-esc`
and says nothing about `bw-user`, so an audit of the claim alone does not lead back to the account
that caused it.

Step 9 is where to be careful about what has been shown. Record three things separately: whether the
Pod was admitted, whether a claim appeared, and what the events on the Pod say. The quota is a
per-class claim count of zero, so the mechanism `ephemeral-volumes.md:258-260` calls `the normal
namespace quota for PVCs` has nothing left to grant. If the Pod is admitted and then stays stuck
with the claim refused, that is the mitigation working the way the sentence implies, and it also
means the refusal arrives after admission rather than at it. Whether a 1.19 cluster would have
behaved this way is not answerable from the pin; the word `still` in that sentence reads like
continuity, but the pin carries no history for it.

Step 10 should refuse. Two names that no longer exist in the binary, handed to a component that
validates its gate list at startup, and the `/readyz` request afterwards should fail to connect
rather than answer `ok`. The `crictl logs` output is what to record: note whether the unrecognised
gate names appear in it, and whether the message treats an unknown gate as fatal rather than as
something to warn about and continue. That is the difference between the post's example being dated
and being unrunnable — a 1.19 harness passing that line to a v1.37 apiserver does not get a cluster
with the features off, it gets no cluster. The metrics grep may print nothing; either answer is
fine, and it is asked only so you do not conclude from the failure that the gates were never there.
After the restore, `/readyz` should answer `ok` again. If it does not, the manifest is still wrong:
`/root/kube-apiserver.yaml.bak` is the known-good copy and the kubelet re-reads the directory on its
own.

**Read on**

1. The post's fourth claim says the automatically created PVC can be referenced as a data source in
   volume cloning or snapshotting, and the pin repeats it at `ephemeral-volumes.md:220-223`. Neither
   says what happens to a snapshot whose source claim is garbage-collected with its Pod. The
   snapshot side of this is [the 2018 snapshot post's
   exercise](../2018/08-volume-snapshot-alpha.md), which finds that the `VolumeSnapshot` kind may
   not exist on the cluster at all; `concepts/storage/volume-pvc-datasource.md` is the cloning side,
   and both are worth reading against step 4's three lifetimes.

2. `StorageCapacityScoring` went to beta at v1.37, the pin's own release, so its documentation is
   the youngest text touched by this exercise.
   `concepts/scheduling-eviction/scheduling-framework.md:126-136` and the note at
   `reference/scheduling/config.md:161-165` are the only two places it is described, and they do not
   describe the same behaviour. Read them together before believing either.

3. Everything on the driver's side of the capacity API is out of reach here and documented
   independently: `CSIDriverSpec.StorageCapacity` at `concepts/storage/storage-capacity.md:47`, the
   three scheduling conditions at `:53-60`, the rescheduling behaviour at `:79-89`, and the
   multi-volume limitation at `:91-104`, which describes a permanent failure rather than a retry.
   That limitation is the strongest argument in the pin for why the post's `WaitForFirstConsumer`
   advice was not a preference.

4. The `image` volume kind at `ephemeral-volumes.md:49-50` is the one thing added to the list this
   post opens against. The post's framing is that Kubernetes' own ephemeral volumes are limited to
   what is implemented inside Kubernetes; a kind that mounts container image content is a new answer
   to that framing rather than a new instance of the old one.

5. Unanswerable from the pin: whether `VolumeCapacityPriority` spent twelve releases in alpha
   because the behaviour was wrong, because nobody drove it, or because the CSI drivers that would
   have consumed it never arrived. The gate file records only the versions and the rename. The
   pinned tree carries no design document, and this repo does not write a KEP number it has not been
   shown.

**Teardown**

The namespace takes the Pods, the claims, the ServiceAccount, the Role, the RoleBinding and the
quota with it. The volumes, the classes and the worker's directories do not go with it, and neither
does the apiserver backup.

```bash
kubectl delete namespace bw-eph --wait=true
kubectl delete pv bw-eph-vol1 bw-eph-vol2 bw-eph-vol3 bw-eph-vol4 bw-eph-vol5 --ignore-not-found
kubectl delete storageclass bw-eph bw-eph-lower bw-eph-upper --ignore-not-found
ssh zain@10.10.10.131 'sudo rm -rf /mnt/bw-eph'
sudo rm -f /root/kube-apiserver.yaml.bak
kubectl get pv,storageclass
kubectl get --raw /readyz
```

Delete the namespace before the volumes. A `Retain` volume whose claim is gone keeps a stale
`claimRef` and will not release on its own, but deleting the PV object while a Pod still mounts it
leaves the mount behind on the worker. The last two commands are the check that matters: nothing of
this exercise left in the cluster, and a control plane that answers.
