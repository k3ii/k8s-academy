<a id="kubernetes-1-29-volume-attributes-class"></a>

# Every manifest in this post is refused by the API server it names, the second of the two types it announces was never in the group at all, and the page that inherited its examples still promises an option to turn the feature off that the gate file withdrew one release before the pin

**Post** — [Kubernetes 1.29: VolumeAttributesClass for Volume Modification](https://kubernetes.io/blog/2023/12/15/kubernetes-1-29-volume-attributes-class/),
2023-12-15.

177 lines, 5,390 bytes, by Sunny Song (Google). Twelfth of this year's thirteen walks in publication
order and the fourth-shortest of them by byte count. It is short because its `:59-149` — half the
file — is a six-step user flow made almost entirely of YAML, and those six steps are the part that
no longer runs.

**As written**

The post announces an alpha in v1.29 that lets you change a volume's attributes — anything other
than its capacity — by editing one field on a PersistentVolumeClaim. Its `:10-14` frames the win as
not having to go through a provider's own API to do it. Its `:16-17` offers a choice: read the usage
details *"in the Kubernetes documentation"* or read on. That sentence names no page and carries no
link; it is the only pointer in the post to the page that now holds all of this, and it is not a
pointer you can follow.

Its `:22` is the load-bearing claim: *"The new `storage.k8s.io/v1alpha1` API group provides two new
types"*. The two are `VolumeAttributesClass` at `:24-28`, a named bag of mutable attributes a CSI
driver understands, and `ModifyVolumeStatus` at `:30-32`, *"the status object of
`ControllerModifyVolume` operation"*. Then `:34-40` gives the mechanism: the class name is applied
at `CreateVolume` alongside the StorageClass parameters, and when the name changes afterwards the
external-resizer sidecar sees an informer event and calls `ControllerModifyVolume`. `:41` cites
KEP-3751 by URL and `:153` cites it again as `kep.k8s.io/3751`.

Its `:45-51` says how to switch it on: `--feature-gates="...,VolumeAttributesClass=true"` on the
`kube-controller-manager` and the `kube-apiserver`, two components and no third. `:54` adds the
condition that no flag can satisfy — the CSI driver has to have implemented the `ModifyVolume` API.
The user flow at `:59-149` is six steps: define a StorageClass and a `silver` class, create a PVC
naming it, check the PVC, define a `gold` class, edit the PVC's `volumeAttributesClassName` to
`gold`, and describe the PVC. `:155-157` closes with a call for beta feedback.

**As it runs now**

The mechanism survived and the spelling did not. `storage.k8s.io/v1alpha1` occurs zero times under
`docs/` and zero times under `examples/` in the pinned tree; every occurrence anywhere in it is
inside a blog post. The reference page is `volume-attributes-class-v1.md`, and its `:3` and `:24`
both declare `apiVersion: storage.k8s.io/v1`. Two of this post's five YAML blocks carry the alpha
group in their `apiVersion` line, and those two are the only ones the API server will refuse.

The second type is the more interesting loss, because it is not a rename. The reference page for the
group has three `##` headings — `VolumeAttributesClass` at its `:29`, `VolumeAttributesClassList` at
`:62`, and `Operations` at `:92`. There is no `ModifyVolumeStatus` in it. The name does exist, in a
different group: `persistent-volume-claim-v1.md:185-187` defines `ModifyVolumeStatus` as a nested
schema of `core/v1`, reachable only as `status.modifyVolumeStatus` on a PVC, per that page's
`:145-146`. It is not a resource, it has no `apiVersion`, and you cannot `kubectl get` it. So the
group the post names provides one type and the list of it, and the post's second type was always
somewhere else.

What the post got right is the part it explained least. Its `:38-40` — change the name in the PVC
spec, the external-resizer sidecar takes the informer event and calls `ControllerModifyVolume` — is
still the mechanism, restated at `volume-attributes-classes.md:67-73` under a heading called
*Resizer*. That page also inherited the post's examples wholesale, including the six-step flow's
`silver` and `gold` classes.

Three rules the post never mentions now govern every step of that flow, and all three are on
`volume-attributes-class-v1.md`. Its `:43-44` makes `driverName` immutable. Its `:56` makes
`parameters` immutable, required, and at least one key/value pair, with a ceiling of 512 parameters
and 256K of cumulative size. The same sentence says an invalid parameter set puts the target PVC
into an `Infeasible` state in `modifyVolumeStatus`. The post's step 4 — create a *new* class called
`gold` rather than edit `silver` — is a direct consequence of that immutability, and the post
presents it as a plot development rather than a constraint. `persistent-volume-claim-v1.md:97` adds
the escape it implies: a PVC stuck in `Infeasible` can have `volumeAttributesClassName` reset to its
previous value, including nil, to cancel the modification.

One whole surface arrived after the post and has nothing to do with CSI at all.
`VolumeAttributesClass` is now a ResourceQuota scope: `resource-quotas.md:439` lists it in the scope
table and its `:763-788` defines it, matching PVCs on `spec.volumeAttributesClassName`,
`status.currentVolumeAttributesClassName` or
`status.modifyVolumeStatus.targetVolumeAttributesClassName`, and restricting a quota so scoped to
`persistentvolumeclaims` and `requests.storage` only. Two runnable files ship for it —
`examples/policy/quota-vac.yaml` and `examples/policy/gold-vac-pvc.yaml`. That machinery is pure API
server admission; it needs no driver, and it is the one part of this post's subject a single node
with no storage at all can exercise end to end.

And the pinned documentation contradicts itself about whether you can still turn any of this off.
`volume-attributes-classes.md:11` opens with a `feature-state` shortcode that reads the gate file
for its banner. Twelve lines later, its `:23` says in hand-written prose: *"This feature is
generally available (GA) as of version 1.34, and users have the option to disable it."* The gate
file's fourth stage writes `locked: true` from v1.36, and v1.37 is the newest release in the pinned
tree. Both halves are on the same page, both describe the same switch, and they disagree. A command
settles half of it — the repo's clusters run v1.35, the last release in which that sentence is true
— and that command is step 10.

**What this exercise does not cover, and where it lives**

The attribute change itself. Every step below stops at the API server, because
`volume-attributes-classes.md:25-27` says the feature works only with storage backed by CSI and only
where the driver implements `ModifyVolume`, and no topology in this repo runs a CSI driver. Nothing
here calls `ControllerModifyVolume`, nothing watches a disk change its IOPS, and
`status.modifyVolumeStatus` will stay empty throughout. That wall is not new to this post: the
snapshot exercise from 2018, on [CRDs that do not arrive with the
driver](../2018/08-volume-snapshot-alpha.md), and the 2020 exercise on [storage capacity tracking
whose demonstration cannot run](../2020/05-ephemeral-volumes-with-storage-capacity-tracking.md),
both end at the same place. What is left on this side of the wall turns out to be most of the post's
factual claims, and all of the ones that are wrong.

**The diff, and why**

**Four of the seven cases, and the interesting one is the third.** This post ***broke***; it
is ***still right***; it was ***wrong when it was published***; and one defect was ***never
absorbed*** — copied forward rather than corrected.

It broke in the ordinary way an alpha post breaks: the group version in two of its five YAML blocks
is not served by any supported release, so the six-step flow cannot be typed in as printed. It is
still right about the mechanism, which is the part it spent four lines on and which the concept page
now restates almost word for word. It was wrong on publication day about its own API surface — the
group it announced never provided `ModifyVolumeStatus`, which lives in `core/v1` and is not a
resource, so the post's `:22` did not become false, it started false. And the defect that was never
absorbed is not a claim at all but a pair of YAML blocks: the post's `silver` at its `:82-84` uses
the parameter names `provisioned-iops` and `provisioned-throughput`, its `gold` at `:121-123` uses
`iops` and `throughput`, and both name `driverName: pd.csi.storage.gke.io`. The concept page copied
both blocks verbatim — `volume-attributes-classes.md:46-47` and its `:97-98` — so one page now shows
four parameter names for one driver. Its `:120-121` then explains two of them, *"the value `4000`,
for the parameter `iops`, and the parameter `throughput` are specific to GCE PD"*, and never
mentions the other two.

It is not the ***overtaken by stasis*** case, and the distinction is worth naming because the post's
closing paragraph invites it. Its `:155-157` asks for feedback in order to move the feature towards
beta. That worked: beta at v1.31, stable at v1.34, locked at v1.36. Seven releases and four rungs is
not stasis; the call to action was answered, and the post is out of date because the thing
succeeded.

**The ladder**

`VolumeAttributesClass`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.29 – v1.30 |
| beta | `false` | — | v1.31 – v1.33 |
| stable | `true` | — | v1.34 – v1.35 |
| stable | `true` | `true` | v1.36 – |

The file writes no `removed` key, so the gate is live at the pin. Two rows deserve reading twice.
The beta row's `defaultValue` is `false`, which makes this another instance of the shape that [the
swap post found](08-swap-linux-beta.md) — three releases of beta that you still had to ask for, and
a stage column that says nothing about it. And the table repeats `stable`, which is how these files
record a change that is not a change of stage; here the change is `locked: true`, written on the
fourth row only, making this one of the 49 gate files in the pinned tree that write it at all. The
body of the file is two sentences: *"Enable support for VolumeAttributesClasses."* and a link to the
concept page.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo), one node, and one node is not a compromise here.
Every step below is an API server admission decision or a read of the pinned tree. There is no
scheduling, no volume, no second node for anything to be attached to, and the CSI driver that would
make any of it real is absent by design — see the section above. Provision it with
[provision](../../strands/lab-topologies.md#provision) and the [node
baseline](../../strands/lab-topologies.md#node-baseline-steps).

**Do**

1. Stand the cluster up with `kubeadm init` and Flannel's CIDR as in [the provisioning
   lab](../../labs/01/01-provision-and-kubeadm-init.md), then take the one backup everything after
   step 9 depends on, and write down which release you are on. The release number matters more in
   this exercise than in most.

   ```sh
   ssh zain@10.10.10.180
   kubectl get nodes -o wide
   kubectl version -o yaml | grep gitVersion
   sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml ~/apiserver.yaml.bak
   ```

2. Put the post's group version to the API server. Its `:22` names `storage.k8s.io/v1alpha1` and its
   `:77` and `:116` write it into two manifests.

   ```sh
   kubectl api-versions | grep '^storage.k8s.io'
   kubectl api-resources --api-group=storage.k8s.io
   kubectl get volumeattributesclasses.v1alpha1.storage.k8s.io 2>&1 | tail -2
   ```

3. Look for the post's second type. It claims the group provides two; ask the server for the list,
   then ask it where the other name lives.

   ```sh
   kubectl api-resources --api-group=storage.k8s.io -o name
   kubectl explain modifyvolumestatus 2>&1 | tail -2
   kubectl explain persistentvolumeclaim.status.modifyVolumeStatus
   kubectl explain persistentvolumeclaim.status.currentVolumeAttributesClassName
   ```

4. Type the post's `silver` class exactly as its `:77-84` prints it, then change one line and type
   it again. Nothing else about the object changes.

   ```sh
   kubectl apply -f - <<'EOF' 2>&1 | tail -2
   apiVersion: storage.k8s.io/v1alpha1
   kind: VolumeAttributesClass
   metadata:
     name: silver
   driverName: pd.csi.storage.gke.io
   parameters:
     provisioned-iops: "3000"
     provisioned-throughput: "50"
   EOF
   kubectl apply -f - <<'EOF'
   apiVersion: storage.k8s.io/v1
   kind: VolumeAttributesClass
   metadata:
     name: silver
   driverName: pd.csi.storage.gke.io
   parameters:
     provisioned-iops: "3000"
     provisioned-throughput: "50"
   EOF
   ```

5. Create the post's `gold` from its `:116-123` on the served group, then create a third class that
   differs from it only in having nothing in `parameters`. The post never says that field is
   required; `volume-attributes-class-v1.md:56` does.

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: storage.k8s.io/v1
   kind: VolumeAttributesClass
   metadata:
     name: gold
   driverName: pd.csi.storage.gke.io
   parameters:
     iops: "4000"
     throughput: "60"
   EOF
   kubectl apply -f - <<'EOF' 2>&1 | tail -2
   apiVersion: storage.k8s.io/v1
   kind: VolumeAttributesClass
   metadata:
     name: bronze
   driverName: pd.csi.storage.gke.io
   parameters: {}
   EOF
   kubectl get volumeattributesclass
   ```

6. Try to edit `silver` instead of creating `gold` — the thing the post's step 4 quietly works
   around. Both fields the class carries are immutable, per `volume-attributes-class-v1.md:43-44`
   and its `:56`, and the server should say so twice.

   ```sh
   kubectl patch volumeattributesclass silver --type=merge \
     -p '{"parameters":{"provisioned-iops":"9000"}}' 2>&1 | tail -2
   kubectl patch volumeattributesclass silver --type=merge \
     -p '{"driverName":"ebs.csi.aws.com"}' 2>&1 | tail -2
   ```

7. Create the post's PVC from its `:91-102`. The StorageClass it names does not exist on this node
   and no provisioner is running, which is the point: watch which of the claim's two class names the
   API server keeps anyway.

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: test-pv-claim
   spec:
     storageClassName: csi-sc-example
     volumeAttributesClassName: silver
     accessModes:
       - ReadWriteOnce
     resources:
       requests:
         storage: 64Gi
   EOF
   kubectl get pvc test-pv-claim
   kubectl get pvc test-pv-claim -o jsonpath='{.spec.volumeAttributesClassName}{"\n"}'
   kubectl get pvc test-pv-claim -o jsonpath='{.status.modifyVolumeStatus}{"\n"}'
   ```

8. Perform the post's step 5 — the edit the whole feature exists for — and then attempt the same
   edit on the other class field beside it. `volume-attributes-classes.md:37` says one of these two
   is mutable in a PVC and the other is not.

   ```sh
   kubectl patch pvc test-pv-claim --type=merge \
     -p '{"spec":{"volumeAttributesClassName":"gold"}}'
   kubectl patch pvc test-pv-claim --type=merge \
     -p '{"spec":{"storageClassName":"csi-sc-other"}}' 2>&1 | tail -2
   kubectl get pvc test-pv-claim \
     -o jsonpath='{.spec.storageClassName}{" / "}{.spec.volumeAttributesClassName}{"\n"}'
   ```

9. Exercise the surface the post never mentions, from the pinned tree itself. Do this part offline,
   in a clone checked out at the pin, and apply the two shipped example files into a namespace of
   their own.

   ```sh
   cd /path/to/kubernetes/website/content/en
   kubectl create namespace vac-quota
   kubectl -n vac-quota apply -f examples/policy/quota-vac.yaml
   kubectl -n vac-quota apply -f examples/policy/gold-vac-pvc.yaml
   kubectl -n vac-quota describe resourcequota pvcs-gold  | sed -n '1,12p'
   kubectl -n vac-quota describe resourcequota pvcs-silver | sed -n '1,12p'
   ```

10. The rung. `volume-attributes-classes.md:23` says users have the option to disable this feature;
    the gate file says that stopped being true at v1.36. You are on v1.35, so take the option while
    it exists and record exactly what it removes.

    ```sh
    sudo sed -i '/- kube-apiserver/a\    - --feature-gates=VolumeAttributesClass=false' \
      /etc/kubernetes/manifests/kube-apiserver.yaml
    sleep 60
    kubectl api-resources --api-group=storage.k8s.io
    kubectl get pvc test-pv-claim -o yaml | grep -i attributesclass || echo "field gone from the object"
    sudo cp ~/apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml
    ```

**Expect**

Step 1 gives you a one-node cluster and a printed `gitVersion`. It should read v1.35, which is the
release `strands/lab-topologies.md:298` fixes for this repo's clusters. Write it down. Two of the
steps below have an answer that is specific to v1.35 and different at v1.36, and the exercise is
only interesting if you know which release produced the output.

Step 2 prints one version line for the group and it is `storage.k8s.io/v1`. The third command fails,
because the version the post writes is not one the server offers: `kubectl` cannot resolve a
resource qualified by a group version that does not exist. Note the exact version line your server
prints rather than taking it from the reference page — `volume-attributes-class-v1.md:3` describes
v1.37, and the point of the next few steps is that this feature's spelling has moved before.

Step 3 answers the post's `:22` in two halves. `kubectl api-resources --api-group=storage.k8s.io -o
name` lists the group's resources and `volumeattributesclasses.storage.k8s.io` is among them;
nothing called `modifyvolumestatus` is, and `kubectl explain modifyvolumestatus` fails to find a
resource by that name because there is no such resource in any group. The third command succeeds and
prints a nested object with the two fields `persistent-volume-claim-v1.md:195` and its `:199`
document — a required `status` string and a `targetVolumeAttributesClassName` — and its parent is
`core/v1`, not the group the post names. The fourth prints the other status field the post never
mentions.

Step 4 is the clean break. The first apply fails with a no-matches-for-kind error naming
`storage.k8s.io/v1alpha1`; the second, differing from it only in the group version on its
`apiVersion` line, creates the object. Everything else in the post's manifest — `driverName`, both
parameters, the `silver` name — the server takes without comment. The post is not wrong about the
shape of the object, only about where to send it.

Step 5 creates `gold` and refuses `bronze`. The refusal cites the parameters field:
`volume-attributes-class-v1.md:56` states that it *"is required and must contain at least one
key/value pair"*, and an empty map is not one. The post's `:45-54` lists the prerequisites for using
the feature and this is not among them, which is the small version of the same problem as the group
version — the post describes the feature, and the API reference describes the object. Then `kubectl
get volumeattributesclass` shows two objects, `silver` and `gold`, carrying four distinct parameter
names between them for one `driverName`. That is the pair of blocks the concept page copied.

Step 6 fails twice, and the two messages are not the same shape. The parameters patch is refused
because `volume-attributes-class-v1.md:56` makes the field immutable and tells you what to do
instead — create a new class and point the PVC at it. The `driverName` patch is refused by the
blunter rule at its `:43-44`, *"This field is immutable."* Together they explain why the post's
six-step flow has to invent `gold` at step 4: not because the story needed a second class, but
because there is no way to change the first one.

Step 7 creates the claim and it sits in `Pending`. Nothing provisions it — there is no
`csi-sc-example` StorageClass on this node and no provisioner to answer if there were — and that is
the expected outcome, not a failure of the step. What matters is the two reads that follow.
`spec.volumeAttributesClassName` comes back `silver`, stored on an unbound claim by a server with no
CSI driver anywhere near it, and `status.modifyVolumeStatus` comes back empty, which
`persistent-volume-claim-v1.md:145-146` says is exactly what an unset value means: no `ModifyVolume`
operation is being attempted.

Step 8 succeeds and then fails, which is the whole distinction the post never draws. The
`volumeAttributesClassName` patch is accepted on an existing claim, because
`volume-attributes-classes.md:37` says that name is mutable in a PVC; the `storageClassName` patch
is rejected, because it is not. `persistent-volume-claim-v1.md:97` states the contrast directly —
the new field *"has a different purpose than storageClassName, it can be changed after the claim is
created"*. The final read prints `csi-sc-example / gold`: one class name frozen at creation, one
changed afterwards, on the same object.

Step 9 is the only place in this exercise where something is actually enforced. `pvcs-gold` reports
one of ten claims used and 2Gi of its 10Gi, because `gold-vac-pvc.yaml:12` asks for `gold` and
`quota-vac.yaml:9-13` scopes that quota to it; `pvcs-silver` reports zero of everything, because its
scope selector does not match. Both descriptions show only `persistentvolumeclaims` and
`requests.storage`, which is what `resource-quotas.md:782-785` says a quota scoped this way is
restricted to tracking. The claim itself stays `Pending` for the same reason step 7's did. No
driver, no storage, and the quota still counted it.

Step 10 is the rung, and it is the one output worth keeping. The API server takes the flag: at v1.35
the gate's stable row carries no `locked` key, so setting it to `false` is a legal thing to ask, and
after the kubelet restarts the static pod the cluster comes back. What you are measuring is what
went away — whether `volumeattributesclasses` has left the group listing, and what the server now
says about the field already stored on `test-pv-claim`. Record both, because v1.35 is the last
release in which this command means anything. From v1.36 the fourth row of the ladder above carries
a lock, and the same edit against a locked gate does not disable a feature, it stops the API server
from starting at all — which is the ending [the in-place resize
exercise](07-in-place-pod-resize-alpha.md) reaches by a different road. Restore the backup and wait
for the server to come back before moving on.

**Read on**

11. [The default that arrives after the claim](01-retroactive-default-storage-class.md) — the other
    2023 post about a class name on a PersistentVolumeClaim, and the one that turns on the
    difference between a field that is absent and a field that is empty. Read the two together and
    the PVC's two class fields stop looking like variations on one idea.

12. [The instruction the API server refuses](07-in-place-pod-resize-alpha.md) — step 10 above ends
    where that exercise begins. It is the locked rung met head-on, on a gate that reached it a
    release earlier than this one.

13. [Storage capacity tracking, whose demonstration cannot
    run](../2020/05-ephemeral-volumes-with-storage-capacity-tracking.md) — the same wall in the same
    group, three years earlier, and a post whose paragraphs became the documentation rather than the
    other way round.

14. [The snapshot CRDs that do not arrive with the driver](../2018/08-volume-snapshot-alpha.md) —
    for what the CSI side of this exercise would cost to set up, and why no topology here pays it.

15. [The namespace boundary and where it
    leaks](../../labs/12/11-a-tenancy-boundary-and-where-it-leaks.md) — for ResourceQuota as a
    tenancy instrument rather than a storage one. Step 9 is the same object with a scope selector on
    it.

**Teardown**

Restore the API server manifest first if step 10 left it edited, then take the objects down in the
order that leaves nothing referencing a class that is gone.

```sh
sudo cp ~/apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml
sleep 60
kubectl delete pvc test-pv-claim --ignore-not-found
kubectl delete namespace vac-quota --ignore-not-found
kubectl delete volumeattributesclass silver gold --ignore-not-found
rm -f ~/apiserver.yaml.bak
exit
just tofu labs destroy
```
