<a id="kubernetes-1-23-prevent-persistentvolume-leaks-when-deleting-out-of-order"></a>

# The gate this post tells you to set in two places is gone from the half Kubernetes owns, the transcript of the bug still reproduces step for step on the only volume a single node can make by hand, and the fix the post says will never reach in-tree storage arrived eight releases later

**Post** — [Kubernetes 1.23: Prevent PersistentVolume leaks when deleting out of
order](https://kubernetes.io/blog/2021/12/15/kubernetes-1-23-prevent-persistentvolume-leaks-when-deleting-out-of-order/),
2021-12-15, by Deepak Kinni (VMware) — 199 lines, 8,471 bytes, one author and one vendor. Half of it
is a transcript of a bug, reproduced at a shell prompt; the other half announces the alpha gate that
fixes it. That gate went on to spend eight releases at alpha, which only two of the gates the pin
has since deleted ever beat.

**As written**

`:10-16` sets up the vocabulary and the expectation. A PersistentVolume is associated with a reclaim
policy; where that policy is `Delete`, `the expectation is that the storage backend releases the
storage resource that was allocated for the PV`, and so `the reclaim policy needs to honored on PV
deletion` — the missing `be` is in the pin. `:18-19` announces the fix as an alpha feature in v1.23
that `lets you configure a cluster to behave that way`.

`:22-31` is the setup for the bug. A PV and a PVC are `Bound`; the PVs themselves `are backed by a
volume allocated by the storage backend`; and then the sentence the whole post turns on: `there are
no restrictions to delete a PV prior to deleting a PVC`. Nothing stops you doing it in the wrong
order, and the wrong order is the one an administrator reaches for when they are cleaning up storage
rather than cleaning up an application.

`:33-95` is the reproduction, and it is the part worth running. `:35-45` retrieves a bound PVC,
`example-vanilla-block-pvc`, holding a 5Gi `ReadWriteOnce` volume from the class
`example-vanilla-block-sc`. `:47-59` deletes the PV that PVC is bound to: the cluster blocks, `the
kubectl tool does not return back control to the shell`, and the transcript ends with a typed `^C`
under a line claiming the PV was `deleted`. `:61-70` shows the PV afterwards, in `Terminating`.
`:72-92` deletes the PVC — which succeeds immediately — and then shows that the PV is gone too:
`Error from server (NotFound)`. `:94-95` supplies the point: `Although the PV is deleted the
underlying storage resource is not deleted, and needs to be removed manually.`

`:97-102` states the defect in the abstract. The reclaim policy `is currently ignored under certain
circumstance`; for a bound pair `the ordering of deletion determines whether the PV reclaim policy
is honored`; delete the PVC first and it is honoured, delete the PV first and it is not, and `the
associated storage asset in the external infrastructure is not removed`. That is a leak with no
error, no event and no object left behind to find it by.

`:104-106` announces the new behaviour: the underlying storage object `is deleted from the backend
when users attempt to delete a PV manually`. `:108-113` is the enablement instruction, and it has
three parts — upgrade to v1.23, run the CSI `external-provisioner` at `version 4.0.0, or later`, and
enable the `HonorPVReclaimPolicy` feature gate in two places, `for the external-provisioner and for
the kube-controller-manager`. `:115-117` then rules a whole class of storage out of the fix: `If
you're not using a CSI driver to integrate with your storage backend, the fix isn't available`,
because `the Kubernetes project doesn't have a current plan to fix the bug for in-tree storage
drivers: the future of those in-tree drivers is deprecation and migration to CSI.`

`:119-171` is the mechanism. `:121` names it: a finalizer,
`external-provisioner.volume.kubernetes.io/finalizer`, added `on new and existing PVs`, and `only
removed after the storage from backend is deleted`. `:129-166` prints a real PV carrying it —
provisioned by `csi.vsphere.vmware.com`, `persistentVolumeReclaimPolicy: Delete` at `:161`, and two
finalizers at `:136-138`, the old `kubernetes.io/pv-protection` above the new one. `:168-171`
explains what that buys and sends the reader to [the finalizer
tutorial](03-using-finalizers-to-control-deletion.md) for the general mechanism, seven months older
and three rows up this year's shelf.

`:173-177` covers CSI migrated volumes: the fix applies to them, but if `HonorPVReclaimPolicy` is
enabled on 1.23 while CSI Migration is disabled, `the finalizer is removed from the PV object if it
exists`. `:179-182` gives the two caveats — the fix is for CSI and migrated volumes only, `In-tree
volumes will exhibit older behavior`, and the gate is alpha in the external-provisioner, `disabled
by default, and needs to be enabled explicitly`. `:184-187` cites KEP-2644 in `sig-storage` and the
volume leak issue, `kubernetes-csi/external-provisioner` number 546. `:189-199` is the usual
invitation and the thanks, to Jan Šafránek, Xing Yang and Matthew Wong.

**As it runs now** — the bug is fixed, the gate that fixed it has been deleted, and the reproduction
at `:33-95` still runs unchanged on the one kind of volume a single-node cluster can make without
installing anything.

**The gate was removed in the release before the pin.** `HonorPVReclaimPolicy` went stable at v1.33
and its file records a last stage ending at v1.35, so it is gone from v1.36 onward. Of the 230 gate
files in the pin that declare `removed: true`, only five have a last stage ending later than v1.34,
and only three end at v1.35: this one, `CSIMigrationPortworx` and `InTreePluginPortworxUnregister`.
The other two are the last of the in-tree migration switches. The release that finished retiring
this post's fix is the release that finished the migration the post said would happen instead of the
fix.

**Half of the enablement instruction now stops the control plane.** `:112-113` says to enable the
gate `for the kube-controller-manager`. Give kube-controller-manager
`--feature-gates=HonorPVReclaimPolicy=true` on a v1.37 cluster and it does not start; the name is
not unknown in the sense of a typo, it is a name the binary used to accept and no longer does. Step
2 does this on purpose, because the failure is the clearest available statement of what `removed:
true` means.

**The other half was never Kubernetes' to give, and the pin cannot tell you about it.** The CSI
`external-provisioner` is a separate binary from a separate repository, with its own release stream
and its own `--feature-gates` flag. `:111` pins it at `version 4.0.0, or later`; nothing in the
pinned website tree states which version of it carries the feature, what its default is now, or
whether the flag still exists there. A cluster with no CSI driver installed has no place to put the
second half of the instruction at all.

**The reproduction still reproduces, and the documentation supplies the apparatus.**
`persistent-volumes.md:123-176` is the Storage Object in Use Protection section, and `:136` gives
the rule that makes the leak possible: `PV removal is postponed until the PV is no longer bound to a
PVC.` Postponed, not cancelled — the deletion is already recorded, so the moment the claim goes the
PV object goes with it, before anything has reclaimed anything. The page's worked example at
`:158-176` is a `hostPath` PersistentVolume with `Reclaim Policy: Delete` sitting in `Terminating`
with `Finalizers: [kubernetes.io/pv-protection]`, which is the post's `:61-70` with the vSphere
taken out.

**The fix the post ruled out for in-tree storage arrived eight releases later.**
`persistent-volumes.md:262-264` names a second finalizer, `kubernetes.io/pv-controller`, `introduced
in v1.31`, `added to dynamically provisioned in-tree plugin volumes and skipped for statically
provisioned in-tree plugin volumes`. v1.31 is the release `HonorPVReclaimPolicy` went beta. The
project did not stand by `doesn't have a current plan to fix the bug for in-tree storage drivers`;
it shipped the in-tree half of the fix in the same release it promoted the CSI half, and left the
static case out on purpose.

**Which makes the class of volume that finalizer applies to almost empty by the pin.**
`persistent-volumes.md:499-509` lists the plugin types still supported — `csi`, `fc`, `hostPath`,
`iscsi`, `local`, `nfs` — and exactly one in-tree provisioner name survives anywhere in
`storage-classes.md`: `kubernetes.io/vsphere-volume`, at `:290`, `:313` and `:327`, for a type that
sits in the next list down and has been migrating since v1.25. `storage-classes.md:478` says `local`
volumes do not support dynamic provisioning at all. `persistent-volumes.md:511-530` lists eight more
that are deprecated but present, and seven of the eight carry `migration on by default` from a named
release, the latest being `portworxVolume` at v1.31. `:532-549` lists eight that are simply `not
available`. And `:321-323` closes the loop: when migration is enabled for an in-tree plugin, `the
kubernetes.io/pv-controller finalizer is replaced by the
external-provisioner.volume.kubernetes.io/finalizer finalizer`. A finalizer for in-tree dynamic
volumes, in a release where in-tree dynamic volumes are all migrating to CSI.

**The mechanism sentence is now the documentation's sentence.** `:121` says the behaviour is
achieved by adding the finalizer to new and existing PVs and removing it only after the backend
delete; `persistent-volumes.md:255-260` says finalizers ensure PVs with `Delete` `are deleted only
after the backing storage are deleted`, and names the same finalizer as `introduced in v1.31` for
`both dynamically provisioned and statically provisioned CSI volumes`. The post's YAML at `:136-138`
appears at `persistent-volumes.md:300` as a one-line `Finalizers:` field in the same order, in a
`describe` of another vSphere CSI volume. `:325-328` states the guarantee the post's title promises,
in the project's own words: the volume is deleted from the backend `irrespective of the order of
deletion of PV and PVC`.

**One version number in the post disagrees with the page that replaced it.** `:121` says the
finalizer is added `on new and existing PVs` and gives no version, because in December 2021 the
answer was v1.23 behind an alpha gate. `persistent-volumes.md:258-260` now dates the same finalizer
`introduced in v1.31`, the beta release, not the alpha one. Both statements are true of their own
moment and the later one is the one a reader will find first.

**The outbound link at `:171` still resolves, and the target points back.** `:171` sends the reader
to `Using Finalizers to Control Deletion`, the May 2021 post that is [row 03 of this same
year](03-using-finalizers-to-control-deletion.md). `finalizers.md:100` ends the concept page by
sending its reader to that same post. Between them, the two halves of this exercise's subject — what
a finalizer is, and what this particular finalizer is for — are one click apart in the pin and were
written seven months apart in 2021.

**Three typographical errors survive intact.** `:16` has `needs to honored`, `:35` has `Retrieve an
PVC`, and `:41` has `it's Bound PV`. None was ever corrected. The post has been superseded twice by
later announcements of the same feature and nobody went back.

**The diff, and why** — five of the seven cases, and the two that matter most point in opposite
directions: the instruction broke completely, and the bug it was written about did not move at all.

**Broke: the enablement instruction, in both of its halves.** `:112-113` names two places to set
`HonorPVReclaimPolicy`. One of them is a Kubernetes component that now refuses the flag outright.
The other is a third-party binary whose current behaviour the pin does not document and which a
cluster without a CSI driver does not run. A reader following `:108-113` in order gets as far as
`upgraded your cluster to the v1.23 release` before every remaining sentence is either impossible or
unanswerable.

**Overtaken by stasis: the bug.** The transcript at `:33-95` is five years old and reproduces step
for step on the pin, provided the volume is a statically created in-tree one — which is the only
kind this exercise's cluster can make without installing a driver. `persistent-volumes.md:264` says
the in-tree finalizer is `skipped for statically provisioned in-tree plugin volumes`, so the skip is
deliberate and current. The post described a defect, the project fixed the defect for the storage
that mattered, and the original demonstration is still a working demonstration because the case it
happens to use was never in scope.

**The plan the project abandoned.** `:115-117` is the strongest prediction in the post and it was
wrong within eight releases. There was no plan to fix in-tree storage; v1.31 added
`kubernetes.io/pv-controller` for dynamically provisioned in-tree volumes anyway. The half of the
prediction that held is the other clause — `the future of those in-tree drivers is deprecation and
migration to CSI` — which `persistent-volumes.md:511-530` and `:532-549` record in detail, sixteen
plugin types deprecated or gone. Both halves in one sentence, and the confident half is the one that
broke.

**Still right: the mechanism, down to the field order.** `:121` and `:168-171` describe a finalizer
that blocks removal of the API object until the backend delete succeeds, and that is exactly what
the pin describes at `persistent-volumes.md:255-260` and `:325-328`. The two-element `finalizers`
list at `:136-138` is the same list, in the same order, as the `describe` output at
`persistent-volumes.md:300`. Nothing here needs translating.

**Retired by being agreed with.** The post's `How does it work?` section is now
`persistent-volumes.md:252-328`, a titled subsection of the concept page, and the gate file itself
sends its reader there — `HonorPVReclaimPolicy.md:26-28` is a link to
`#persistentvolume-deletion-protection-finalizer` and nothing else. The gate page for a gate that no
longer exists exists to point at the documentation that absorbed it. What the documentation added on
the way is the third finalizer, which the post could not have named.

**The ladder**

One gate, transcribed from its `stages:` list parsed as YAML, plus the file-level flag that ends it.

```
HonorPVReclaimPolicy  alpha  false  1.23 - 1.30
                      beta   true   1.31 - 1.32
                      stable true   1.33 - 1.35   locked: true
                      removed: true
```

Thirteen releases end to end, eight of them at alpha. Measured across the pin's feature-gate
directory, 230 gate files declare `removed: true` and 147 of those carry a plain alpha-beta-stable
ladder; their median time at alpha is two releases and their median total life is eight. Exactly two
of the 147 spent longer at alpha — `ServiceNodeExclusion` at eleven and `TTLAfterFinished` at nine —
and one tied, `BoundServiceAccountTokenVolume`. Twelve of the 147 reached six. That population is
gates that finished, which is why [the memory QoS exercise](08-qos-memory-resources.md) can count
fifteen releases on the first rung without appearing here: its gate reached beta on the pin's own
release and was never removed, so there is no total life to measure. Read against [the Pod Security
exercise](09-pod-security-admission-beta.md), whose gate opened and closed its alpha stage inside a
single release, this is the same archive's other extreme, and the two posts are six days apart.

The `locked: true` on the stable row is the first this year's set has had to account for. It means
the gate could still be named on a command line but could not be set to anything but `true`, so for
three releases the flag existed only to fail loudly if you tried to turn the feature off. 49 of the
pin's 487 gate files carry `locked` on some stage, but only three of the 230 removed ones do: this
gate, `ComponentSLIs` and `SizeMemoryBackedVolumes`. A locked stable stage is how a project says the
argument is over while the argument's vocabulary is still being printed in help text.

The gate's body text is one sentence — `Honor persistent volume reclaim policy when it is Delete
irrespective of PV-PVC deletion ordering.` — and then a link to the concept section. It never
mentions CSI, which is the one qualification the post spends two paragraphs on.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`, 4096MB, 4
vCPU, 25G, brought up with [the provisioning sequence](../../strands/lab-topologies.md#provision).
Everything below is API objects, one static directory on the node and one edit to a control-plane
manifest; nothing is scheduled and no image is pulled. A second node would add nothing, because
`hostPath` volumes are single-node by definition — `persistent-volumes.md:503-505` says so in the
plugin list itself.

**Do**

1. Ask the cluster for the switch the post tells you to throw. Three components, one question, and
   the fourth command counts how many gates each of them still admits to having so that the zero
   means something:

   ```sh
   kubectl version -o json | python3 -c 'import json,sys
   print("server:", json.load(sys.stdin)["serverVersion"]["gitVersion"])'
   kubectl get --raw /metrics | grep 'kubernetes_feature_enabled' | grep -i honorpv \
     || echo "kube-apiserver: no gate by that name"
   CERT="--cert /etc/kubernetes/pki/apiserver-kubelet-client.crt \
     --key /etc/kubernetes/pki/apiserver-kubelet-client.key"
   sudo curl -sk $CERT https://127.0.0.1:10257/metrics \
     | grep 'kubernetes_feature_enabled' | grep -i honorpv \
     || echo "kube-controller-manager: no gate by that name"
   sudo curl -sk $CERT https://127.0.0.1:10257/metrics \
     | grep -c '^kubernetes_feature_enabled'
   kubectl get --raw /metrics | grep -c '^kubernetes_feature_enabled'
   ```

2. Now set it anyway, because `:112-113` tells you to. Back the manifest up first; the static pod
   restarts the moment the file is written, so the failure arrives within seconds and the recovery
   is a file copy:

   ```sh
   sudo cp /etc/kubernetes/manifests/kube-controller-manager.yaml /root/kcm.yaml.bak
   sudo sed -i '/- kube-controller-manager/a\    - --feature-gates=HonorPVReclaimPolicy=true' \
     /etc/kubernetes/manifests/kube-controller-manager.yaml
   sudo grep -n 'feature-gates' /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 20
   sudo crictl ps -a --name kube-controller-manager --no-trunc | head -5
   sudo crictl logs "$(sudo crictl ps -a -q --name kube-controller-manager | head -1)" 2>&1 | tail -5
   kubectl -n kube-system get pods -l component=kube-controller-manager
   sudo cp /root/kcm.yaml.bak /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 25
   kubectl -n kube-system get pods -l component=kube-controller-manager
   ```

3. Build the apparatus the post's transcript needs, using the only volume type this cluster can back
   without installing a driver. One directory on the node, one PersistentVolume with the reclaim
   policy the post is about, one claim that binds to it, and one file standing in for the data the
   post's storage backend holds:

   ```sh
   sudo mkdir -p /srv/bw-pvleak
   echo "this is the storage resource" | sudo tee /srv/bw-pvleak/canary
   kubectl apply -f - <<YAML
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: bw-pvleak
   spec:
     capacity:
       storage: 1Gi
     accessModes: ["ReadWriteOnce"]
     persistentVolumeReclaimPolicy: Delete
     storageClassName: bw-pvleak
     hostPath:
       path: /srv/bw-pvleak
   ---
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: bw-pvleak
     namespace: default
   spec:
     accessModes: ["ReadWriteOnce"]
     storageClassName: bw-pvleak
     resources:
       requests:
         storage: 1Gi
   YAML
   sleep 5
   kubectl get pv,pvc
   kubectl get pv bw-pvleak -o jsonpath='{.metadata.finalizers}'; echo
   kubectl get pvc bw-pvleak -o jsonpath='{.metadata.finalizers}'; echo
   ```

4. Run the post's reproduction, in the post's order. `:47-59` types `^C` because the delete does not
   return; `timeout` does the same job and records how long it waited. Read the finalizer list at
   every stage, because the finalizer list is the whole explanation:

   ```sh
   timeout 20 kubectl delete pv bw-pvleak; echo "delete exit: $?"
   kubectl get pv bw-pvleak
   kubectl get pv bw-pvleak -o jsonpath='{.metadata.deletionTimestamp}{"\n"}{.metadata.finalizers}'
   echo
   kubectl delete pvc bw-pvleak
   sleep 5
   kubectl get pv bw-pvleak
   sudo ls -l /srv/bw-pvleak
   sudo cat /srv/bw-pvleak/canary
   ```

5. Read the rule that produced that, and the two sentences in the pin that say the case you just ran
   is out of scope on purpose. No cluster needed for the second half:

   ```sh
   cd /path/to/kubernetes/website
   sed -n '133,136p' content/en/docs/concepts/storage/persistent-volumes.md
   sed -n '158,176p' content/en/docs/concepts/storage/persistent-volumes.md
   sed -n '255,264p' content/en/docs/concepts/storage/persistent-volumes.md
   grep -rn 'kubernetes.io/pv-controller' content/en/docs --include='*.md'
   ```

6. Rebuild the pair and put the post's finalizer on it by hand. There is no CSI driver here to add
   it, which is the point: a finalizer is a list entry, not code, and [the finalizer
   tutorial](03-using-finalizers-to-control-deletion.md) is where this archive establishes that you
   may write one yourself. Compare what you get against the post's `:129-166`:

   ```sh
   kubectl apply -f - <<YAML
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: bw-pvleak
   spec:
     capacity:
       storage: 1Gi
     accessModes: ["ReadWriteOnce"]
     persistentVolumeReclaimPolicy: Delete
     storageClassName: bw-pvleak
     hostPath:
       path: /srv/bw-pvleak
   ---
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: bw-pvleak
     namespace: default
   spec:
     accessModes: ["ReadWriteOnce"]
     storageClassName: bw-pvleak
     resources:
       requests:
         storage: 1Gi
   YAML
   sleep 5
   kubectl patch pv bw-pvleak --type=json -p='[{"op":"add",
     "path":"/metadata/finalizers/-",
     "value":"external-provisioner.volume.kubernetes.io/finalizer"}]'
   kubectl get pv bw-pvleak -o jsonpath='{.metadata.finalizers}'; echo
   kubectl describe pv bw-pvleak | sed -n '1,10p'
   ```

7. Delete in the wrong order again, with the finalizer in place. Nothing about the cluster has
   changed except one string on one object. Give it two minutes, not ten seconds, because the claim
   you are testing is that nothing will ever come:

   ```sh
   timeout 20 kubectl delete pv bw-pvleak; echo "delete exit: $?"
   kubectl delete pvc bw-pvleak
   sleep 10
   kubectl get pv bw-pvleak
   kubectl get pv bw-pvleak -o jsonpath='{.metadata.finalizers}'; echo
   sleep 120
   kubectl get pv bw-pvleak
   kubectl get events -A --field-selector involvedObject.name=bw-pvleak
   sudo ls -l /srv/bw-pvleak
   ```

8. Take it off by hand, which is the thing the documentation tells you not to do, and watch the
   object go the instant the list empties. Then read the rule you just broke and the reason it is
   written the way it is:

   ```sh
   kubectl patch pv bw-pvleak --type=json -p='[{"op":"replace","path":"/metadata/finalizers","value":[]}]'
   kubectl get pv bw-pvleak; echo "get exit: $?"
   sudo ls -l /srv/bw-pvleak
   cd /path/to/kubernetes/website
   sed -n '89,96p' content/en/docs/concepts/overview/working-with-objects/finalizers.md
   sed -n '325,328p' content/en/docs/concepts/storage/persistent-volumes.md
   ```

9. Take the census of all three finalizers in the pinned tree, then write the taxonomy out. Three
   names, three classes of volume, three different components adding them, and exactly one of the
   three that this cluster can produce without help:

   ```sh
   cd /path/to/kubernetes/website
   for F in kubernetes.io/pv-protection kubernetes.io/pv-controller \
            external-provisioner.volume.kubernetes.io/finalizer; do
     printf '%-52s docs=%s blog=%s\n' "$F" \
       "$(grep -rl "$F" content/en/docs --include='*.md' | wc -l | tr -d ' ')" \
       "$(grep -rl "$F" content/en/blog --include='*.md' | wc -l | tr -d ' ')"
   done
   sed -n '497,530p' content/en/docs/concepts/storage/persistent-volumes.md
   sed -n '321,323p' content/en/docs/concepts/storage/persistent-volumes.md
   ```

10. Offline, in the pinned checkout, measure what is left of the announcement itself — the gate
    page, the two links, the three uncorrected typographical errors, and the one number that says
    how completely the gate's name has left the archive:

    ```sh
    cd /path/to/kubernetes/website
    P=content/en/blog/_posts/2021/prevent-persistentvolume-leaks-when-deleting-out-of-order.md
    wc -l -c $P
    grep -n 'needs to honored\|Retrieve an PVC\|and it.s ' $P
    grep -n '2644-honor-pv-reclaim-policy\|external-provisioner/issues' $P
    sed -n '8,28p' \
      content/en/docs/reference/command-line-tools-reference/feature-gates/HonorPVReclaimPolicy.md
    grep -rl 'HonorPVReclaimPolicy' content/en/docs content/en/blog --include='*.md'
    grep -n 'Using Finalizers' content/en/docs/concepts/overview/working-with-objects/finalizers.md
    ```

**Expect**

Step 1 prints a v1.37 server and then falls through to both `no gate by that name` lines, while the
two counts that follow are large. That combination is the point: each component will list every gate
it knows about, in the hundreds, and neither of them knows this one. The post's subject is a gate,
and the cluster has no opinion about it because there is nothing left to have an opinion about.

Step 2 should leave you without a controller manager. `crictl ps -a` shows the container in `Exited`
and being recreated, the log's last lines name the flag and the gate, and `kubectl -n kube-system
get pods` shows the static pod restarting. Nothing else on the cluster notices for the twenty
seconds it is down. The restore brings it back within one kubelet sync period; if it does not, check
that the `sed` inserted the flag under the command and not under a volume mount. Do not skip the
restore — steps 3 and onward need the PersistentVolume controller, which lives in the binary you
just stopped.

Step 3 gives you a `Bound` pair, `kubernetes.io/pv-protection` on the volume and
`kubernetes.io/pvc-protection` on the claim, and nothing else on either. That is the complete
finalizer state of a statically created in-tree volume on a v1.37 cluster, and it is the same list
the documentation prints at `persistent-volumes.md:163`.

Step 4 is the post, five years on. Expect `delete exit: 124`, which is `timeout` reporting that
`kubectl` never returned — the same fact the post records as a typed `^C` at `:58`. Expect the PV to
come back as `Terminating`, which is what the post shows at `:69` and what
`persistent-volumes.md:155-156` gives as the sign that a volume is protected, with a
`deletionTimestamp` already set and `kubernetes.io/pv-protection` still on it. Then expect deleting
the claim to take the volume with it, leaving `Error from server (NotFound)`, exactly as at `:91`.
And expect `canary` to still be on the node. That file is the leak: the API forgot the volume, the
storage still has it, and no event anywhere recorded the difference.

Step 5 explains it in four lines. `persistent-volumes.md:133-136` says PV removal is `postponed
until the PV is no longer bound to a PVC` — postponed, so the delete you typed is still pending and
fires the instant the claim goes, ahead of any reclaim. `:158-176` is the same object you just made,
printed by the documentation as its worked example. `:255-264` is the fix and its exclusion in five
sentences, and the `grep` returns three lines from one file, which is every word the pin has about
`kubernetes.io/pv-controller`.

Steps 6 and 7 are the pair this exercise is built on. Expect step 6 to print the post's `:136-138`
back at you, two finalizers, the protection one first. Expect step 7's delete to time out again and
the claim's deletion to remove `kubernetes.io/pv-protection` and nothing else, leaving a
`Terminating` PersistentVolume with exactly one finalizer on it. Then expect it to still be there
two minutes later, with no events, because the component that removes that finalizer is the CSI
`external-provisioner` and this cluster has never run one. The post's mechanism is intact and half
of it is missing, which is a more useful thing to see than a working demonstration would have been.

Step 8 removes it and the object disappears in the same round trip — `get exit: 1` — and `canary` is
still on the node. Read that carefully, because it is the sentence the whole feature turns on: the
finalizer never deleted any storage. It holds the API object open so that something else can delete
the storage first. Take it off by hand and you have not leaked a volume by accident, you have leaked
one on purpose, which is why `finalizers.md:89-96` tells you to understand the finalizer's purpose
before you remove it, and `persistent-volumes.md:325-328` states the guarantee you just discarded.

Step 9's census should give `kubernetes.io/pv-protection` four docs files and five blog posts,
`kubernetes.io/pv-controller` one and two, and `external-provisioner.volume.kubernetes.io/finalizer`
one and three. That last pair, four files total, is the whole footprint of the thing this post
announces. The three blog posts are this one, the 2024 beta announcement and the 2025 GA
announcement — the same feature announced three times across four years, which is a later row's work
in two later years of this walk. Then read the plugin list: six types supported, eight deprecated
with migration dates, eight gone, and `persistent-volumes.md:321-323` saying that where migration is
on, the in-tree finalizer is replaced by the CSI one. Write down which of the three names this
cluster can produce on its own. There is only one, and you saw it in step 3.

Step 10 prints `198` lines from `wc` for a 199-line file, because the post has no trailing newline —
the byte count, 8471, is the one to trust. The three typographical errors are all still there. The
gate transcription should match the ladder above line for line, `locked: true` included. And the
last `grep` should return three paths and only three: the gate's own page, the concept page that
uses it in a `feature-state` shortcode, and this post. Neither of the two later announcements of the
same feature names the gate at all.

**Read on**

1. `concepts/storage/persistent-volumes.md:123-176` and `:252-328` are the two finalizer sections of
   the same page, a hundred and thirty lines apart in a page of 1,234. The first is protection
   against deleting something in use; the second is protection against deleting something in the
   wrong order. Read them together and the three finalizer names sort themselves into a table you
   can hold in your head.

2. [The finalizer tutorial](03-using-finalizers-to-control-deletion.md) is where the mechanism
   belongs, and `:171` of this post sends you there itself. `finalizers.md:80-96` is the concept
   page's warning about removing finalizers by hand, which step 8 ignores deliberately; read it
   after step 8 rather than before, because the warning means more once you have watched the object
   vanish.

3. [The CSI beta exercise](../2018/02-container-storage-interface-beta.md) holds the other half of
   the machinery this post depends on: what the `external-provisioner` sidecar is, what it watches,
   and what `kubernetes.io/pvc-protection` does to a claim that is still in use. This post's fix is
   a string that sidecar writes and erases; that exercise is where the sidecar itself is walked.

4. [`research/blog-era-translation.md`](../../research/blog-era-translation.md) carries the release
   facts for this feature at `:440`, including the KEP number, which `:186` of the post also gives:
   `sig-storage/2644-honor-pv-reclaim-policy`. The KEP text is outside the pin and is not read here.

5. Unanswerable from the pin: which release of the CSI `external-provisioner` carries this feature
   now, what its default is, and whether its `--feature-gates` flag still accepts the name — `:111`
   pins it at `4.0.0, or later` and the pinned website tree documents none of it, because it is a
   different project's binary. Two smaller ones go the same way. Which in-tree plugin can still
   dynamically provision a volume with migration disabled, and therefore still earn
   `kubernetes.io/pv-controller`, cannot be settled from the plugin list alone. And whether the
   in-tree `hostPath` plugin would ever delete the directory under a `Delete` reclaim policy is not
   stated anywhere in the pin; step 4 measures the outcome without answering the question.

**Teardown**

This exercise edited a control-plane manifest, created a directory on the node and left an object
that was removed by hand, so the teardown checks the manifest first and the directory second:

```sh
sudo grep -c 'feature-gates' /etc/kubernetes/manifests/kube-controller-manager.yaml || echo 0
kubectl -n kube-system get pods -l component=kube-controller-manager
kubectl delete pv bw-pvleak --ignore-not-found
kubectl delete pvc bw-pvleak --ignore-not-found
sudo rm -rf /srv/bw-pvleak /root/kcm.yaml.bak
kubectl get pv,pvc -A
kubectl get nodes
```

The flag count should be `0` and the controller manager should be `Running` with a restart count
that matches the one failure you caused. If `kubectl delete pv` hangs here, something is still bound
and the `--ignore-not-found` will not save you — find the claim first. Nothing else survives this
exercise, and the node stays up for the last row of this year.
