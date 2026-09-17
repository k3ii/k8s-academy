<a id="kubernetes-1-31-prevent-persistentvolume-leaks-when-deleting-out-of-order"></a>

# Every one of the fifty lines inside this post's twelve code fences was copied from the edition published three years earlier, the paragraph the rewrite deleted is the prediction that the one sentence it added refutes, and the set that new sentence describes is empty at the pin

**Post** — [Kubernetes 1.31: Prevent PersistentVolume Leaks When Deleting out of
Order](https://kubernetes.io/blog/2024/08/16/kubernetes-1-31-prevent-persistentvolume-leaks-when-deleting-out-of-order/),
2024-08-16.

7,760 bytes, 196 lines, one author: Deepak Kinni, of Broadcom. Thirty-fifth of 2024's 54 posts by
size, 3,008 below the year's mean of 10,768, and ninth of the thirteen in this year's `walk` set.
Twelve links: six into `/docs/`, of which two are the same finalizer concept page cited twice; one
into `/blog/`; and five to github.com, two of them the references at the foot. The author has
published three posts on this blog in its entire history and all three announce the same KEP, 2644,
at three different stages — alpha in December 2021, beta here, general availability in May 2025.

**As written**

`:10-16` opens with the vocabulary. A PersistentVolume is associated with a reclaim policy, and that
policy determines `the actions that need to be taken by the storage backend on deletion of the PVC
Bound to a PV`. Where the policy is `Delete` the backend `releases the storage resource allocated
for the PV`, and so `the reclaim policy needs to be honored on PV deletion`. Two sentences, two
different objects whose deletion triggers the backend: the PVC in the first, the PV in the second.
`:18-19` announces the fix — with v1.31, `a beta feature lets you configure your cluster to behave
that way and honor the configured reclaim policy`.

`:22-31` sets the bug up. A PVC is `a user's request for storage`; a PV and a PVC are `Bound` if a
newly created PV or a matching PV is found; the PVs `are backed by volumes allocated by the storage
backend`. Then the sentence the post turns on: `there are no restrictions on deleting a PV before
deleting a PVC`. Nothing stops you doing it in the wrong order, and the wrong order is the one an
administrator reaches for when they are cleaning up storage rather than cleaning up an application.

`:33-95` is the reproduction. `:35-45` retrieves a bound PVC, `example-vanilla-block-pvc`, holding a
5Gi `ReadWriteOnce` volume from the class `example-vanilla-block-sc`, bound 19 seconds ago. `:47-59`
deletes the PV it is bound to: `the kubectl session blocks`, the tool `does not return back control
to the shell`, and the transcript ends in a typed `^C` under a line claiming the PV was `deleted`.
`:61-70` shows the PV in `Terminating`. `:72-92` deletes the PVC, which returns at once, and then
fails to find the PV: `Error from server (NotFound)`. `:94-95` supplies the point — `Although the PV
is deleted, the underlying storage resource is not deleted and needs to be removed manually.`
`:97-102` states it in the abstract: for a `Bound` pair the ordering decides whether the policy is
honoured, and when it is not, `the associated storage asset in the external infrastructure is not
removed`. That is a leak with no error, no event and no object left behind to find it by.

`:104-111` announces the new behaviour and how to get it. Two conditions, no third: upgrade the
cluster to v1.31, and run the CSI `external-provisioner` at `version 5.0.1 or later`. `:113-117` is
the mechanism — `For CSI volumes`, the behaviour is achieved by adding a finalizer,
`external-provisioner.volume.kubernetes.io/finalizer`, to new and existing PVs, removed `only after
the storage from the backend is deleted`. `:117` is a single backtick on a line of its own.

`:119-162` prints a real PV carrying it: provisioned by `csi.vsphere.vmware.com`,
`persistentVolumeReclaimPolicy: Delete` at `:157`, and two finalizers at `:132-134` with the old
`kubernetes.io/pv-protection` above the new one. Its `creationTimestamp` at `:131` is
`2021-11-17T19:28:56Z`. `:164-168` explains what the finalizer buys and sends the reader to [the
finalizer tutorial](../2021/03-using-finalizers-to-control-deletion.md) for the mechanism in
general. `:170` is one sentence on its own: `Similarly, the finalizer kubernetes.io/pv-controller is
added to dynamically provisioned in-tree plugin volumes.`

`:172-178` closes the technical half in four lines. The fix `applies to CSI migrated volumes as
well`, and the one caveat is that it `does not apply to statically provisioned in-tree plugin
volumes`. `:180-183` cites KEP-2644 in `sig-storage` and the volume leak issue,
`kubernetes-csi/external-provisioner` number 546. `:185-196` is the invitation and the thanks, to
Fan Baofa, Jan Šafránek, Xing Yang and Matthew Wong.

**As it runs now** — the post is a revision of an earlier post, the revision is where a prediction
quietly died, and the one sentence it gained describes a class of volume that no longer exists.

**It is the same document as the alpha announcement, edited.** `diff` between this file and
`2021/prevent-persistentvolume-leaks-when-deleting-out-of-order.md` removes 46 lines and adds 43,
against 199 lines and 196. Strip the prose and the overlap is total: extract the contents of the
twelve fenced blocks from each file and the two extracts are byte-identical, 50 lines each. The
`kubectl` commands, the `NAME STATUS VOLUME` table, the `^C`, the `Error from server (NotFound)` and
the thirty-six-line PV dump are all the 2021 capture. Nothing was re-run for this edition, and the
PV whose finalizers the post prints was created on `2021-11-17`, a month before the *first* post and
eight releases before the one this edition is about.

**Two of the archive's 765 posts sit on both sides of a near-duplicate pair, and this is one of
them.** Reduce every post to its set of stripped lines of forty characters or more, keep the files
with at least twenty such lines — 668 of them — and exactly six pairs share more than half of the
smaller file's set. The six pairs are four chains: the dockershim FAQ and its update, two releases
of mutable CSI node allocatable counts, volume group snapshots at alpha then beta then `v1beta2`,
and this one at alpha then beta then general availability. This post is in two of the six pairs —
behind it the 2021 alpha post at 0.54, ahead of it the 2025 GA post at 0.57 — and the only other
post in the archive with a predecessor and a successor both is `volume-group-snapshot-beta`,
published in the same year by the same SIG.

**The rewrite deleted the feature gate and did not replace it.** The 2021 edition named
`HonorPVReclaimPolicy`, linked the feature-gates reference, and told you to set the gate in two
places. This edition contains the string `HonorPVReclaimPolicy` zero times, the phrase `feature
gate` zero times, and the word `beta` exactly once, at `:18`. What is left at `:110-111` is two
version floors. A reader who starts here has no name to look up, which matters more at the pin than
it did in 2024: the gate went stable and locked at v1.33 and its file records a last stage ending at
v1.35, so the switch is gone and the behaviour is unconditional. [The alpha
exercise](../2021/10-prevent-persistentvolume-leaks.md) transcribes that ladder and puts the removed
name on a control-plane command line to watch it fail; none of that is repeated here.

**The paragraph it deleted is the prediction that the sentence it added refutes.** The 2021 edition
said, in three lines, that `the Kubernetes project doesn't have a current plan to fix the bug for
in-tree storage drivers: the future of those in-tree drivers is deprecation and migration to CSI.`
This edition deletes that paragraph and adds `:170`, which says the in-tree half was fixed after
all, by a second finalizer, `kubernetes.io/pv-controller`. The two edits are in the same pass by the
same author, and nothing in the post marks the reversal — no `previously`, no `we said`, no
strikethrough. The retraction is visible only by diffing the two editions, which is what step 7
does.

**The set that new sentence describes is empty at the pin.** `:170` covers `dynamically provisioned
in-tree plugin volumes`. `persistent-volumes.md:499-509` lists the six plugin types still supported
and only one of them, `csi`, provisions dynamically at all. `:511-530` lists the eight that are
deprecated but present, and seven carry **migration on by default** from a named release — `cinder`
at v1.21, `awsElasticBlockStore`, `azureDisk` and `gcePersistentDisk` at v1.23, `azureFile` at
v1.24, `vsphereVolume` at v1.25, `portworxVolume` at v1.31 — while the eighth, `flexVolume`, has `no
migration plan` and provisions nothing dynamically. `:321-323` then says that where migration is on
for a plugin, `the kubernetes.io/pv-controller finalizer is replaced by the
external-provisioner.volume.kubernetes.io/finalizer finalizer`. Every in-tree plugin that could earn
the finalizer `:170` announces has already had it taken away again.

**The one caveat is now the documentation's own sentence.** The post's `:178` says the fix `does not
apply to statically provisioned in-tree plugin volumes`. `persistent-volumes.md:262-264` says the
`kubernetes.io/pv-controller` finalizer is `added to dynamically provisioned in-tree plugin volumes
and skipped for statically provisioned in-tree plugin volumes`. Same boundary, same words, opposite
framing. The 2021 edition's two caveats were both about the *alpha gate* and neither survives; the
sentence that replaced them is the only line in the post that a reader can check against the pin and
find agreed with, word for word.

**The pinned documentation disagrees with itself about its own worked example, and no command here
can settle it.** `persistent-volumes.md:266-291` prints `an example of dynamically provisioned
in-tree plugin volume`: a `describe` of a vSphere VMDK volume annotated
`pv.kubernetes.io/provisioned-by: kubernetes.io/vsphere-volume`, carrying `Finalizers:
[kubernetes.io/pv-protection kubernetes.io/pv-controller]`. The same page says at `:529-530` that
`vsphereVolume` has had **migration on by default** since v1.25, and at `:321-323` that under
migration the second of those two finalizers is replaced by the CSI one. The finalizer in the
example was introduced at v1.31, six releases after the migration it is shown surviving. Either the
example predates the rule and was never re-captured, or the rule has an exception the page does not
state; the page gives no way to choose, and this cluster has no vSphere to ask.

**A single backtick, at this post's `:117`, survives at the pin, and it is not the only place it
survives.** The 2021 edition carried the finalizer sentence as one long line. The rewrite split it
in two, added a link, and left an orphan `` ` `` on the line below. Of the 765 post files in the
pin, exactly two contain a line that is a single backtick and nothing else: this one and the 2025
general availability post, which inherited it along with everything else. Nothing under `docs/`
links this post, or either of the other two; the only inbound link anywhere in the pinned tree is
from the 2025 post's own further reading, where `:114` calls this one the `Beta Release Blog`.

**What this exercise does not cover, and where it lives** — the bug itself is [the alpha
exercise](../2021/10-prevent-persistentvolume-leaks.md): the transcript reproduced on a `hostPath`
volume, the gate's thirteen-release ladder, the removed name put on a control-plane command line,
and the finalizer added and stripped by hand. Nothing in that list is repeated here. What a
finalizer *is* belongs to [the finalizer
tutorial](../2021/03-using-finalizers-to-control-deletion.md), which this post links at `:168`. The
three reclaim policies, and why a released PV does not return to the pool, are [the
released-not-available drill](../../labs/08/02-released-not-available.md); stripping a finalizer and
then going to find the orphan it left is [the finalizer
deadlock](../../labs/08/11-finalizer-deadlock.md). The general case of a claim naming a class whose
provisioner is not installed is case 2 of [the four-ways-Pending
drill](../../labs/08/06-four-ways-a-pvc-stays-pending.md); step 6 below tests one specific
provisioner name for one specific reason. What the `external-provisioner` sidecar actually is, and
what else rides beside it, is [the driver-with-sidecars
build](../../labs/08/13-csi-driver-in-cluster.md). The general availability announcement of this
same feature is a later year's row and is named below without a link, because it is only reachable
forwards.

**The diff, and why**

**Wrong when it was published: the first paragraph, after the copy-edit.** The 2021 edition said the
reclaim policy determines what the backend does `on deletion of the PV`. This edition changed that
to `on deletion of the PVC Bound to a PV` — and then kept the next sentence unchanged, `the reclaim
policy needs to be honored on PV deletion`. Two sentences apart, the post defines the policy as a
rule about deleting claims and then demands it be honoured when you delete volumes, which is the
exact case the first sentence now excludes. The edit was made in the release that fixed the bug, and
it narrowed the definition back to the half that was never broken. `:18-19` carries the same kind of
leftover: `a beta feature lets you configure your cluster` is true of the 2021 edition, where a gate
was named and two components had to be told about it, and is false here, where nothing is configured
and the feature is on because it reached beta.

**A plan the project abandoned, recorded by its own deletion.** The strongest sentence in the 2021
edition was that there was `no current plan to fix the bug for in-tree storage drivers`. This
edition is where that stopped being true, and it says so by removing the paragraph and adding
`:170`. Both halves of the old prediction can now be scored: the fix did reach in-tree storage, in
the very release this post announces, and the migration it offered instead also finished — all
fifteen `CSIMigration*` gate files in the pin declare `removed: true`, and
`persistent-volumes.md:511-530` records seven plugin types with migration on by default and
`:532-549` eight more simply **not available**. The clause that was wrong was fixed; the clause that
was right emptied the fix of its subject.

**Overtaken by stasis: everything inside the fences.** Fifty lines of transcript and YAML, captured
in 2021 against a vSphere cluster, republished unchanged in 2024 under the heading `How did reclaim
work in previous Kubernetes releases?`. They did not need re-capturing, because the behaviour they
show is still the behaviour of a statically provisioned volume with no external provisioner watching
it, which is what step 4 demonstrates on this cluster and what [the alpha
exercise](../2021/10-prevent-persistentvolume-leaks.md) demonstrates on a `hostPath` one. The
evidence is five years old and correct, and the reason it is correct is that the case it uses was
never in scope for the fix.

**Still right: the caveat, and the mechanism it bounds.** The post's `:178` is one line — the fix
does not apply to statically provisioned in-tree plugin volumes — and the pin agrees with it at
`persistent-volumes.md:262-264`. The post's `:115-116` says the finalizer is added for CSI volumes
and removed only after the backend delete; `persistent-volumes.md:255-260` and `:325-328` say the
same thing in the project's own words, including the guarantee the title promises — the volume is
deleted from the backend `irrespective of the order of deletion of PV and PVC`. Nothing in the
mechanical half of this post needs translating.

**Never absorbed: the document.** Nothing under `docs/` links any of the three editions. The concept
section that carries the mechanism cites the feature gate, not the announcement, and the gate file
cites the concept section. The only inbound link in the entire pinned tree points backwards from the
2025 successor. Three posts, one author, one KEP, and by the pin the chain is legible only to
someone who goes looking for it — which is what the offline half of this exercise is.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180` running Kubernetes v1.35,
provisioned with [the standard steps](../../strands/lab-topologies.md#provision) and [the node
baseline](../../strands/lab-topologies.md#node-baseline-steps). Nothing here runs a Pod, mounts a
volume or pulls an image; every live step is an API object and an event, so one node is enough and a
second would tell you nothing. What makes this cluster the right instrument is what it is missing —
no CSI driver is installed, no `external-provisioner` sidecar is running, and no in-tree cloud
provider is configured — because the post's subject is a finalizer that a component you do not have
is supposed to add. Cluster work happens in a namespace called `bw-pvrev`; the PersistentVolumes and
the StorageClass are cluster-scoped and are named with the same prefix so teardown can find them.
Steps 7 to 10 are offline reads of the pinned checkout and need no cluster at all.

**Do**

1. Ground the cluster and record what it does not have. The last command makes the namespace.

   ```sh
   kubectl version -o json | sed -n '/serverVersion/,/}/p'
   kubectl get storageclass
   kubectl get csidrivers
   kubectl get pv -o custom-columns=NAME:.metadata.name,POLICY:.spec.persistentVolumeReclaimPolicy,FIN:.metadata.finalizers
   kubectl create namespace bw-pvrev
   ```

2. Create a statically provisioned CSI PersistentVolume naming a driver that does not exist, and a
   claim that binds to it by name. Then read the PV's finalizer list against
   `persistent-volumes.md:258-260`.

   ```sh
   cat > /tmp/bw-pvrev-delete.yaml <<'YAML'
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: bw-pvrev-delete
   spec:
     capacity:
       storage: 1Gi
     accessModes: [ReadWriteOnce]
     persistentVolumeReclaimPolicy: Delete
     storageClassName: ""
     csi:
       driver: bw.example.invalid
       volumeHandle: bw-pvrev-handle-1
   ---
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: bw-pvrev-delete
     namespace: bw-pvrev
   spec:
     accessModes: [ReadWriteOnce]
     storageClassName: ""
     volumeName: bw-pvrev-delete
     resources:
       requests:
         storage: 1Gi
   YAML
   kubectl apply -f /tmp/bw-pvrev-delete.yaml
   kubectl get pvc -n bw-pvrev bw-pvrev-delete
   kubectl get pv bw-pvrev-delete -o jsonpath='{.metadata.finalizers}{"\n"}'
   ```

3. Register a `CSIDriver` object under that name, so the API server now knows the driver exists, and
   read the finalizer list again.

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: storage.k8s.io/v1
   kind: CSIDriver
   metadata:
     name: bw.example.invalid
   spec:
     attachRequired: false
     podInfoOnMount: false
   YAML
   kubectl get csidrivers
   kubectl get pv bw-pvrev-delete -o jsonpath='{.metadata.finalizers}{"\n"}'
   ```

4. Delete in the post's order — the PersistentVolume first, while the claim still exists, then the
   claim. This is the sequence the post's transcript runs, on a CSI volume rather than a vSphere
   one.

   ```sh
   kubectl delete pv bw-pvrev-delete --wait=false
   kubectl get pv bw-pvrev-delete -o custom-columns=NAME:.metadata.name,PHASE:.status.phase,DELETING:.metadata.deletionTimestamp,FIN:.metadata.finalizers
   kubectl delete pvc -n bw-pvrev bw-pvrev-delete
   kubectl get pv bw-pvrev-delete
   kubectl get events -n bw-pvrev --sort-by=.lastTimestamp | tail -5
   ```

5. Do it again with the other reclaim policy. Only three strings change, so derive the manifest from
   the one you already have rather than retyping it.

   ```sh
   sed -e 's/bw-pvrev-delete/bw-pvrev-retain/g' \
       -e 's/bw-pvrev-handle-1/bw-pvrev-handle-2/' \
       -e 's/persistentVolumeReclaimPolicy: Delete/persistentVolumeReclaimPolicy: Retain/' \
       /tmp/bw-pvrev-delete.yaml > /tmp/bw-pvrev-retain.yaml
   kubectl apply -f /tmp/bw-pvrev-retain.yaml
   kubectl delete pv bw-pvrev-retain --wait=false
   kubectl get pv bw-pvrev-retain -o custom-columns=NAME:.metadata.name,PHASE:.status.phase,DELETING:.metadata.deletionTimestamp
   kubectl delete pvc -n bw-pvrev bw-pvrev-retain
   kubectl get pv bw-pvrev-retain
   ```

6. Now the in-tree half that `:170` claims. Ask for a dynamically provisioned in-tree volume by
   naming the vSphere Cloud Provider provisioner from `storage-classes.md:290`, and read the event
   the claim collects. Read the event text before you read the next paragraph; it has two possible
   shapes and which one you get is the finding.

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: bw-pvrev-vcp
   provisioner: kubernetes.io/vsphere-volume
   reclaimPolicy: Delete
   ---
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: bw-pvrev-intree
     namespace: bw-pvrev
   spec:
     accessModes: [ReadWriteOnce]
     storageClassName: bw-pvrev-vcp
     resources:
       requests:
         storage: 1Gi
   YAML
   sleep 30
   kubectl get pvc -n bw-pvrev bw-pvrev-intree
   kubectl describe pvc -n bw-pvrev bw-pvrev-intree | sed -n '/Events:/,$p'
   ```

7. Offline. Put the two editions side by side and measure how much of this one is new. The
   fence-stripping `awk` matches three backticks, not one, and that is deliberate: the post contains
   a line that is a single backtick, and a looser pattern would toggle on it.

   ```sh
   cd /path/to/kubernetes/website/content/en
   A=blog/_posts/2021/prevent-persistentvolume-leaks-when-deleting-out-of-order.md
   B=blog/_posts/2024/honor-pv-reclaim-policy-beta.md
   echo "removed $(diff $A $B | grep -c '^<')   added $(diff $A $B | grep -c '^>')"
   awk '/^```/{f=!f; next} f' $A > /tmp/bw-fences-2021.txt
   awk '/^```/{f=!f; next} f' $B > /tmp/bw-fences-2024.txt
   wc -l /tmp/bw-fences-2021.txt /tmp/bw-fences-2024.txt
   diff /tmp/bw-fences-2021.txt /tmp/bw-fences-2024.txt && echo 'fence contents identical'
   grep -n 'creationTimestamp' $B
   ```

8. Offline. Ask how unusual that is across the whole archive. Reduce each post to its set of
   stripped lines of forty characters or more, drop the files with fewer than twenty such lines, and
   print every pair sharing more than half of the smaller set.

   ```sh
   cd /path/to/kubernetes/website/content/en
   python3 - <<'PY'
   import os
   sets = {}
   for root, _, files in os.walk("blog/_posts"):
       for fn in files:
           if not fn.endswith(".md"):
               continue
           p = os.path.join(root, fn)
           s = {l.strip() for l in open(p, encoding="utf-8") if len(l.strip()) >= 40}
           if len(s) >= 20:
               sets[p] = s
   ks = sorted(sets)
   print(len(ks), "files kept")
   for i in range(len(ks)):
       for j in range(i + 1, len(ks)):
           a, b = sets[ks[i]], sets[ks[j]]
           r = len(a & b) / min(len(a), len(b))
           if r > 0.5:
               print(round(r, 2), ks[i], ks[j])
   PY
   ```

9. Offline. Read what the rewrite took out and what it put in, then census the words it dropped.

   ```sh
   cd /path/to/kubernetes/website/content/en
   A=blog/_posts/2021/prevent-persistentvolume-leaks-when-deleting-out-of-order.md
   B=blog/_posts/2024/honor-pv-reclaim-policy-beta.md
   diff $A $B | grep '^<' | grep -i 'in-tree\|feature-gate\|HonorPVReclaimPolicy\|deprecation'
   diff $A $B | grep '^>' | grep -i 'pv-controller\|CSI migrated\|statically provisioned'
   grep -c 'HonorPVReclaimPolicy' $A $B
   grep -in 'feature gate\|beta' $B
   grep -rln '^`$' --include='*.md' blog/_posts
   ```

10. Offline. Take the concept page's worked example and hold it against the concept page's own
    rules, then count the gates those rules depend on.

    ```sh
    cd /path/to/kubernetes/website/content/en
    P=docs/concepts/storage/persistent-volumes.md
    sed -n '252,264p' $P
    sed -n '266,291p' $P
    sed -n '321,328p' $P
    sed -n '511,530p' $P
    G=docs/reference/command-line-tools-reference/feature-gates
    ls $G | grep -c '^CSIMigration'
    grep -l 'removed: true' $G/CSIMigration*.md | wc -l
    grep -rn 'prevent-persistentvolume-leaks-when-deleting-out-of-order' --include='*.md' docs blog
    ```

**Expect**

Step 1 prints `v1.35`, then three inventories that are almost all empty. `kubectl get storageclass`
reports no resources found — the house build installs no dynamic provisioner — and so does `kubectl
get csidrivers`. The PV listing is empty too. Record that emptiness; it is the experimental control
for everything that follows. The post is about a finalizer added by the `external-provisioner`
sidecar, and this cluster has no sidecar to add it.

Step 2's claim binds immediately: a PVC that names `volumeName` and an empty `storageClassName` is a
pre-bound static pair, and the control plane only has to agree. The finalizer read is the point of
the step, and it prints `["kubernetes.io/pv-protection"]` — one finalizer, the ordinary one, and not
the one the post is about. `persistent-volumes.md:258-260` says
`external-provisioner.volume.kubernetes.io/finalizer` `is added to both dynamically provisioned and
statically provisioned CSI volumes`, in the passive voice and with no actor named. The actor is the
sidecar, and the sentence is true only on a cluster that runs one. This is a CSI volume, statically
provisioned, and the finalizer is absent.

Step 3 changes nothing, which is the finding. `kubectl get csidrivers` now lists
`bw.example.invalid`, so the API server knows the name; the PV's finalizer list is still
`["kubernetes.io/pv-protection"]`. A `CSIDriver` object is a registration record read by the kubelet
and the attach-detach controller — it does not start a sidecar, and nothing in the control plane
takes over the sidecar's job in its absence. Knowing the driver exists and having the driver running
are two different cluster states, and only the second one adds the finalizer.

Step 4 reproduces the 2021 transcript without a 2021 cluster. The `delete pv` returns at once
because of `--wait=false`, and the read shows the PV with a `deletionTimestamp` set, still holding
`kubernetes.io/pv-protection`, and — depending on how quickly the controller reacts — either `Bound`
or `Released`. Deleting the claim releases the protection finalizer, and the last `get pv` prints
`Error from server (NotFound)`. The API object is gone. There was never a real volume behind
`bw-pvrev-handle-1`, but had there been one, nothing in this sequence would have deleted it and
nothing would have recorded that it was left behind — which is exactly the leak the post's title
names. The events list holds nothing about the PV; PersistentVolumes are cluster-scoped and their
events do not land in the namespace.

Step 5 gives a byte-for-byte identical outcome with `Retain` in place of `Delete`. The PV enters
`Terminating`, waits for the claim, and vanishes. That identity is the definition of `not honoured`:
the reclaim policy is a field with no reader on this cluster, so setting it to either value produces
the same result. On a cluster with a driver installed the two diverge, and the finalizer added in
step 2's absence is what makes them diverge. The three reclaim policies and what `Released` means
for a PV that survives its claim are [the released-not-available
drill](../../labs/08/02-released-not-available.md), not this one.

Step 6's claim stays `Pending` for as long as you leave it, and the event is the instrument. Expect
one of two messages, and read the provisioner name in it. If it says `waiting for a volume to be
created, either by external provisioner "csi.vsphere.vmware.com" or manually created by system
administrator`, then CSI migration translated the in-tree name on the way through and the claim is
waiting for a driver nobody installed. If instead it says `no volume plugin matched name:
kubernetes.io/vsphere-volume`, the in-tree plugin is not compiled into this control plane at all.
Either way `:170`'s `dynamically provisioned in-tree plugin volumes` cannot be produced here, and
`persistent-volumes.md:529-530` says why: vSphere migration has been on by default since v1.25, six
releases before the finalizer `:170` announces. The general case of a claim naming a class whose
provisioner is not installed is case 2 of [the four-ways-Pending
drill](../../labs/08/06-four-ways-a-pvc-stays-pending.md); what is specific here is the provisioner
name.

Step 7 prints `removed 46 added 43` against files of 199 and 196 lines, so about a fifth of the
document changed. Then the two fence extracts come out at 50 lines each and `diff` says nothing, so
`fence contents identical` prints: every command, every column heading, every YAML key and the whole
thirty-six-line `kubectl get pv -o yaml` dump is the 2021 capture, republished. The last command
prints `131: creationTimestamp: "2021-11-17T19:28:56Z"` — the PersistentVolume whose finalizers this
post shows you was created a month before the first edition was published and eight releases before
the one this edition announces.

Step 8 prints `668 files kept` and then six pairs. Two of them have this post on one side: `0.54`
with the 2021 alpha announcement behind it and `0.57` with the 2025 general availability
announcement ahead of it. Scan the other four and they fall into three chains — the dockershim FAQ
and its 2022 update at `0.69`, volume group snapshots at `0.65` and `0.74`, and two 2025 releases of
mutable CSI node allocatable counts at `0.56`. Only two files in the whole archive appear twice in
this list: this post, and `2024/volume-group-snapshot-beta.md`. Republishing an announcement with
edits is rare; doing it three times, as this KEP's author did, is unique in the archive.

Step 9's first `diff` prints the paragraph that is gone: the 2021 edition's statement that the
project had no current plan to fix the bug for in-tree storage drivers, and that their future was
deprecation and migration to CSI. The second prints what replaced it — `:170`'s
`kubernetes.io/pv-controller` sentence, `:174`'s claim about CSI migrated volumes, and `:178`'s
caveat. `grep -c 'HonorPVReclaimPolicy'` prints `1` for the 2021 file and `0` for this one: the
feature gate's name does not survive the rewrite. The case-insensitive search finds `beta` at `:18`
and nowhere else, and no occurrence of `feature gate` at all. The last command lists exactly two
markdown files in the entire archive containing a line that is one backtick — this post and its 2025
successor. The `diff` output above shows that line among the *added* lines, so the stray backtick
was introduced by this rewrite and then inherited.

Step 10 lays the documentation's disagreement out in reading order. `:252-264` gives the two rules;
`:266-291` gives a worked example of a dynamically provisioned in-tree vSphere volume carrying
`Finalizers: [kubernetes.io/pv-protection kubernetes.io/pv-controller]`; `:321-323` says that when
migration is enabled for a plugin, `kubernetes.io/pv-controller` is replaced by the
external-provisioner finalizer; `:511-530` says vSphere migration has been on by default since
v1.25. The example therefore shows a state that the page's own rules forbid, on a plugin the page
itself lists as migrated, using a finalizer introduced six releases after the migration. Cite both
halves; no command available here settles which half is wrong, because the cluster this exercise
runs on cannot produce either state. Then the counts: 15 `CSIMigration*` gate files, and 15 of them
carrying `removed: true` — the condition `:321-323` places on the rule refers to switches that no
longer exist. The final search returns four lines, all inside `blog/_posts`: three `slug:` fields
and the 2025 post's `:114` reference. Nothing under `docs/` links any edition of this post.

**Read on**

1. `docs/concepts/storage/persistent-volumes.md:252-328` — the deletion protection finalizer section
   whole, including both worked examples. It is the page that absorbed this post's mechanism, and it
   is also the page step 10 catches disagreeing with itself. Read it once for the rule and once for
   the example.

2. `docs/concepts/storage/persistent-volumes.md:497-549` — the three lists of plugin types:
   supported, deprecated-but-present with migration dates, and gone. Twenty-two names and one date
   each is the shortest account in the pin of what happened to in-tree storage, and it is what
   empties `:170`.

3. `docs/reference/command-line-tools-reference/feature-gates/HonorPVReclaimPolicy.md` — the gate
   this post declines to name, with its stages. Short, and the only place in the pin that records
   when the behaviour stopped being optional.

4. [The alpha announcement of the same fix, three years and one author-revision
   earlier](../2021/10-prevent-persistentvolume-leaks.md) — the exercise that walks the bug, the
   reproduction and the ladder. Read it after step 7, not before: the diff is more legible once you
   have seen which half of it that exercise already owns.

5. Unanswerable from the pin: who removed the in-tree prediction, and whether they knew they were
   retracting it. The paragraph's deletion and `:170`'s addition are one commit's worth of editing
   by one author, and the pinned tree carries only the result. Git history would show the commit; it
   would not show whether the reversal was noticed or merely tidied.

**Teardown**

```sh
kubectl delete namespace bw-pvrev --wait=true
kubectl delete pv bw-pvrev-delete bw-pvrev-retain --ignore-not-found
kubectl delete storageclass bw-pvrev-vcp --ignore-not-found
kubectl delete csidriver bw.example.invalid --ignore-not-found
rm -f /tmp/bw-pvrev-delete.yaml /tmp/bw-pvrev-retain.yaml
rm -f /tmp/bw-fences-2021.txt /tmp/bw-fences-2024.txt
kubectl get pv,storageclass,csidrivers
```

The last line is the check that matters. PersistentVolumes, StorageClasses and CSIDrivers are
cluster-scoped, so deleting the namespace does not touch them, and a PV left behind with a
`deletionTimestamp` and a finalizer would sit there indefinitely. If steps 4 and 5 ran to
completion, both PVs are already gone and the `--ignore-not-found` deletes are no-ops. If the final
listing still shows `bw-pvrev-delete` or `bw-pvrev-retain`, the claim was never deleted; delete the
claim, not the volume, and the volume will follow. Nothing in this exercise edited a file on the
node or restarted a service, so there is nothing else to restore.
