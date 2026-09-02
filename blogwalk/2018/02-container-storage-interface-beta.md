<a id="container-storage-interface-beta"></a>
# Of this post's four manifests, three still apply byte for byte and the fourth has never parsed — a missing colon, not a version — and every one of the four limitations the post records against beta was closed in a release you can name, including the one about a sidecar needing write access to every Node object, which is gone from the pinned documentation so completely that the object built to replace it is governed by a feature gate naming an API group that does not exist

**Post** — [Container Storage Interface (CSI) for Kubernetes Goes Beta](https://kubernetes.io/blog/2018/04/10/container-storage-interface-beta/),
2018-04-10, Kubernetes v1.10. It carries no author frontmatter and no editor's note; the credit is
two contributor lists at the end, fifteen names in all. The census marks its own alpha post from
three months earlier `read`, so this is the CSI post the sweep walks.

**As written** — an announcement built as a FAQ, nine questions with headings, and the answers to
four of them are manifests you are meant to copy.

The argument first. *"Because volume plugins are currently “in-tree”—volume plugins are part of the
core Kubernetes code and shipped with the core Kubernetes binaries—vendors wanting to add support
for their storage system to Kubernetes (or even fix a bug in an existing volume plugin) must align
themselves with the Kubernetes release process."* CSI ends that: *"Third party storage developers
can now write and deploy volume plugins exposing new storage systems in Kubernetes without ever
having to touch the core Kubernetes code."*

Then nine bullets under *"What's new in Beta?"*, opening with the one that matters most to a
reader: *"With the promotion to beta CSI is now enabled by default on standard Kubernetes
deployments instead of being opt-in."* Six of the remaining eight are API facts, and each names a
thing:

- Kubernetes moved from CSI spec v0.1 to v0.2, and *"There were breaking changes between the CSI
  spec v0.1 and v0.2, so existing CSI drivers must be updated to be 0.2 compatible before use with
  Kubernetes 1.10.0+."*
- Mount propagation, *"a feature that allows bidirectional mounts between containers and host (a
  requirement for containerized CSI drivers), has also moved to beta."*
- *"The Kubernetes `VolumeAttachment` object, introduced in v1.9 in the storage v1alpha1 group, has
  been added to the storage v1beta1 group."*
- `CSIPersistentVolumeSource` promoted to beta, and *"A `VolumeAttributes` field was added … (in
  alpha this was passed around via annotations)."*
- *"Node authorizer has been updated to limit access to `VolumeAttachment` objects from kubelet."*
- `fsType` can now be passed in, *"previously always assumed to be `ext4`"*.
- And a new optional CSI call: *"`NodeStageVolume`, has been added to the CSI spec, and the
  Kubernetes CSI volume plugin has been modified to call `NodeStageVolume` during `MountDevice` (in
  alpha this step was a no-op)."*

The flag requirement is stated once and hedged once: CSI *"may require the following flag"* on
*"API server binary and kubelet binaries"*, namely `--allow-privileged=true`, because *"Most CSI
plugins will require bidirectional mount propagation, which can only be enabled for privileged
pods. Privileged pods are only permitted on clusters where this flag has been set to true (this is
the default in some environments like GCE, GKE, and kubeadm)."*

Then the four manifests. A StorageClass:

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: fast-storage
provisioner: com.example.csi-driver
parameters:
  type: pd-ssd
  csiProvisionerSecretName: mysecret
  csiProvisionerSecretNamespace: mynamespace
```

with a claim about two of those keys: *"New for beta, the default CSI external-provisioner reserves
the parameter keys `csiProvisionerSecretName` and `csiProvisionerSecretNamespace`. If specified, it
fetches the secret and passes it to the CSI driver during provisioning."* A PersistentVolumeClaim,
five lines of spec, `storageClassName: fast-storage`. A pre-provisioned PersistentVolume, whose
`csi:` block is the longest artefact in the post and carries all three of the secret references the
beta added. And a Pod, ten lines, an `nginx` container with a `volumeMounts` entry and a
`persistentVolumeClaim` volume.

For deployment the post is honest that it cannot tell you much: *"CSI plugin authors must provide
their own instructions for deploying their plugin on Kubernetes."* What it can offer is the
sidecar list, four helper containers *"the Kubernetes team provides"* as part of the suggested
deployment process: `external-attacher`, which *"watches Kubernetes `VolumeAttachment` objects and
triggers `ControllerPublish` and `ControllerUnpublish` operations against a CSI endpoint"*;
`external-provisioner`, which watches PersistentVolumeClaims and triggers `CreateVolume` and
`DeleteVolume`; `driver-registrar`, which *"registers the CSI driver with kubelet (in the future)
and adds the drivers custom `NodeId` (retrieved via `GetNodeID` call against the CSI endpoint) to
an annotation on the Kubernetes Node API Object"*; and `livenessprobe`. The pitch for the set is a
sentence: *"Storage vendors can build Kubernetes deployments for their plugins using these
components, while leaving their CSI driver completely unaware of Kubernetes."*

The comparison with FlexVolume is the post's sharpest passage, and it is an argument about
deployment rather than about interfaces. FlexVolume *"requires files for third party driver
binaries (or scripts) to be copied to a special plugin directory on the root filesystem of every
node (and, in some cases, master) machine. This requires a cluster admin to have write access to
the host filesystem for each node and some external mechanism to ensure that the driver file is
recreated if deleted, just to deploy a volume plugin."* And: *"Flex did not address the pain of
plugin dependencies: Volume plugins tend to have many external requirements (on mount and
filesystem tools, for example). These dependencies are assumed to be available on the underlying
host OS, which is often not the case."*

It ends with two forecasts and four limitations. The forecasts: *"Once CSI reaches stability, we
plan to migrate most of the in-tree volume plugins to CSI"*, and *"the Kubernetes team plans to
push the CSI implementation to GA in 1.12."* The limitations, verbatim, because each one has a
release attached to it now:

> * Block volumes are not supported; only file.
> * CSI drivers must be deployed with the provided external-attacher sidecar plugin, even if they
>   don't implement `ControllerPublishVolume`.
> * Topology awareness is not supported for CSI volumes, including the ability to share information
>   about where a volume is provisioned (zone, regions, etc.) with the Kubernetes scheduler to allow
>   it to make smarter scheduling decisions, and the ability for the Kubernetes scheduler or a
>   cluster administrator or an application developer to specify where a volume should be
>   provisioned.
> * `driver-registrar` requires permissions to modify all Kubernetes node API objects which could
>   result in a compromised node gaining the ability to do the same.

**As it runs now** — three of the four manifests apply unchanged, so the interesting question is
not what broke but what the post's own limitation list turned into.

*The Pod, the PVC and the StorageClass are all still exactly right.* The Pod is ten lines of
`persistentVolumeClaim` reference and nothing in it has moved. The PVC's `accessModes`,
`resources.requests.storage` and `storageClassName` are unchanged. The StorageClass is still
`storage.k8s.io/v1` — a group version that was already `v1` when the post was written and is `v1`
now — with `provisioner` and an opaque `parameters` map.

*The StorageClass applies, and two of its keys mean nothing.* `csiProvisionerSecretName` and
`csiProvisionerSecretNamespace`, the two keys the post says the external-provisioner reserves as
new for beta, do not appear anywhere in the pinned documentation. Neither does the string
`provisioner-secret-name`. The prefix that does exist, `csi.storage.k8s.io/`, is used for something
else entirely: pod-identity keys the kubelet passes as volume context when a CSIDriver sets
`podInfoOnMount`, and a service-account-token key (`csi-driver-v1.md:81`, `:105`). The post's two
keys still apply, because `parameters` is a free-form string map that nothing validates. They are
stored, and no component in the pinned tree is documented as reading them.

*The PersistentVolume has never parsed.* Line 119 of the post's source is `nodePublishSecretRef`
with no colon, followed by two indented keys. It is not a version problem, a field rename or an
escaping artefact — it is a missing character, and it means the longest and most instructive
manifest in the post has never been applyable, on any release, including the one it was written
for. Add the colon and it applies at the pin unchanged: `driver`, `volumeHandle`, `readOnly`,
`fsType`, `volumeAttributes`, `controllerPublishSecretRef`, `nodeStageSecretRef` and
`nodePublishSecretRef` are all still fields of `PersistentVolumeSpec.csi`
(`volumes.md:1013-1042`), described in the same terms.

*And the API has grown two more secret references the post could not have.*
`controllerExpandSecretRef` and `nodeExpandSecretRef` (`persistent-volume-v1.md:364`, `:380`) exist
because volumes can now be resized, which was not a thing CSI did in v1.10. The pin's own list of
those fields carries a defect worth seeing: at `volumes.md:1027-1032` a bullet about enabling the
`CSINodeExpandSecret` feature gate sits at the top level of the field list, as though the gate were
a field of the `csi` block. That gate's ladder is beta-and-on from v1.27 and stable from v1.29, and
the file is marked `removed: true`; the bullet's own last sentence says as much. So it is an
instruction that retracts itself, indented one level too shallow.

*`storage/v1beta1` is the one version claim that broke.* The post's `VolumeAttachment` bullet tracks
the object from `storage v1alpha1` in v1.9 to `storage v1beta1` in v1.10. That `v1beta1` stopped
being served at v1.22, for `VolumeAttachment` along with `CSIDriver`, `CSINode` and `StorageClass`,
and `VolumeAttachment` has been in `storage.k8s.io/v1` since v1.13
(`deprecation-guide.md:298-306`). The post's StorageClass, written against `v1`, was already on the
right side of that; its narrative bullet was not.

*The CSI spec version the post announces is deprecated, and has been for twelve releases.*
`volumes.md:959-962` still carries this note: *"Support for CSI spec versions 0.2 and 0.3 is
deprecated in Kubernetes v1.13 and will be removed in a future release."* The post's headline
compatibility fact — v0.2, up from v0.1, with breaking changes in between — is the subject of a
deprecation notice whose promised future release has not arrived in twenty-four releases.

*The four sidecars are down to one mention.* `driver-registrar` and `livenessprobe` appear nowhere
in the pinned documentation. `external-attacher` and `external-provisioner` appear only as version
pins in unrelated pages and as a `SecretReference` description. The one survivor is
`node-driver-registrar`, and it is named exactly once, inside the CSINode API description:
*"CSI drivers do not need to create the CSINode object directly. As long as they use the
node-driver-registrar sidecar container, the kubelet will automatically populate the CSINode object
for the CSI driver as part of kubelet plugin registration"* (`csi-node-v1.md:31`). The whole
deployment story the post spends a third of its length on now lives outside the tree, at the
project's separate CSI site.

**The diff, and why** — this post is the rare case where the diff is almost entirely the post's own
closing list coming true. Four limitations, four releases, and one of them is the reason a new API
object exists.

*The plan was carried out, which is not the same as the post being right.* *"Once CSI reaches
stability, we plan to migrate most of the in-tree volume plugins to CSI"* happened, on a mechanism
with its own name and its own gate. `CSIMigration` went stable at v1.25 and redirects operations
against in-tree plugins to the corresponding CSI driver, so *"operators do not have to make any
configuration changes to existing Storage Classes, PersistentVolumes, or PersistentVolumeClaims"*
(`volumes.md:1082-1090`). What it cost is stated in the same section, in bold: as part of that
migration you *"**must** have installed and configured the appropriate CSI driver for that storage.
The core of Kubernetes does not install that software for you"* (`:1097-1098`). The in-tree plugin
the post's own StorageClass parameters imitate is the clearest case: *"In Kubernetes v1.37, all
operations for the in-tree `gcePersistentDisk` type are redirected to the `pd.csi.storage.gke.io`
CSI driver. The `gcePersistentDisk` in-tree storage driver was deprecated in the Kubernetes v1.17
release and then removed entirely in the v1.28 release"* (`volumes.md:297-301`). And yet
`gcePersistentDisk` is still a field of `PersistentVolumeSpec`
(`persistent-volume-v1.md:120-121`), marked Deprecated, describing its own redirection. A driver
removed entirely and a field still served are not a contradiction, but the two pages never say
which of the two they are talking about, so read them together.

*The GA forecast missed by one release, and the gate says so.* The post says GA in v1.12. Here is
the ladder for `CSIPersistentVolume`, the feature gate for the mechanism this post announces:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.9 – v1.9 |
| beta | `true` | — | v1.10 – v1.12 |
| stable | `true` | — | v1.13 – v1.16 |

The file declares `removed: true`. One release of alpha, three of beta, four of stable, then the
gate was deleted — and stable arrived at v1.13, not v1.12. The gate's body describes what it
switched: *"Enable discovering and mounting volumes provisioned through a CSI (Container Storage
Interface) compatible volume plugin."* The `beta` row's `default: true` is the post's headline
sentence about being enabled by default rather than opt-in, in table form.

*Limitation one, block volumes, closed at v1.18.* `CSIBlockVolume`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.11 – v1.13 |
| beta | `true` | — | v1.14 – v1.17 |
| stable | `true` | — | v1.18 – v1.21 |

Alpha in v1.11, the release immediately after this post. `persistent-volumes.md:1014-1021` now
lists CSI first among the plugins supporting raw block volumes, at `state="stable"` for v1.18, and
tells you to set up the PV and PVC *"as usual, without any CSI-specific changes"*.

*Limitation two, the mandatory attacher, closed by an object rather than a release.* The post says
drivers must ship the external-attacher *"even if they don't implement `ControllerPublishVolume`"*.
The pin's answer is a field: `attachRequired` on CSIDriver, which *"indicates this CSI volume driver
requires an attach operation (because it implements the CSI ControllerPublishVolume() method) …
If the value is specified to false, the attach operation will be skipped"*
(`csi-driver-v1.md:69`). The object that field lives on did not exist when the post was written.
`CSIDriverRegistry`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.12 – v1.13 |
| beta | `true` | — | v1.14 – v1.17 |
| stable | `true` | — | v1.18 – v1.21 |

`removed: true`. CSIDriver now carries twelve spec fields (`csi-driver-v1.md:68-108`), of which the
post's world had none.

*Limitation three, topology, was half-shipped before the post was published.* Here is
`VolumeScheduling`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.9 – v1.9 |
| beta | `true` | — | v1.10 – v1.12 |
| stable | `true` | — | v1.13 – v1.16 |

That is the same ladder, release for release, as the post's own gate: beta and default-on in v1.10.
What it carries is `volumeBindingMode: WaitForFirstConsumer`, which *"will delay the binding and
provisioning of a PersistentVolume until a Pod using the PersistentVolumeClaim is created"* so that
volumes are *"selected or provisioned conforming to the topology that is specified by the Pod's
scheduling constraints"* (`storage-classes.md:183-187`), plus `allowedTopologies` for the cases
where that is not enough (`:212-220`). At the pin, CSI is the **only** plugin listed as supporting
`WaitForFirstConsumer` with dynamic provisioning (`:193-195`). So the scheduler-side mechanism the
post's third limitation describes was already beta and on in the post's release; what CSI lacked was
somewhere to report a node's topology from. `CSINodeInfo`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.12 – v1.13 |
| beta | `true` | — | v1.14 – v1.16 |
| stable | `true` | — | v1.17 – v1.22 |

`removed: true`. Two releases after the post, and the missing half arrived. Read the two ladders
side by side before accepting the post's limitation at face value: it reads like a feature that had
not been built, and it was closer to two features that had not been connected.

*Limitation four is the one that changed the API, and it is this exercise's title.* The post records
its own sidecar as a security problem: `driver-registrar` *"requires permissions to modify all
Kubernetes node API objects which could result in a compromised node gaining the ability to do the
same."* Read that against the post's own FlexVolume complaint — that Flex *"requires a cluster admin
to have write access to the host filesystem for each node"* — and the symmetry is unmissable. The
post argues that Flex is unacceptable because deploying it needs write access to every node's
filesystem, and then records that its own recommended deployment needs write access to every node's
API object. What closed it is the `CSINode` object: same name as the Node, owned by it through an
OwnerReference, populated by the kubelet as part of plugin registration rather than by a sidecar
writing Node annotations (`csi-node-v1.md:31`). The registrar no longer writes to Nodes because it
no longer writes to the API at all; it talks to the kubelet, and the kubelet writes the object.

*And the sidecar's replacement is governed by a gate that names a group which does not exist.* Both
`CSIDriverRegistry` and `CSINodeInfo` describe their objects as living in `csi.storage.k8s.io` —
*"Enable all logic related to the CSINodeInfo API object in `csi.storage.k8s.io`"*. There is no such
API group at the pin. `group-versions.md:34` lists `storage.k8s.io` with `v1, v1beta1`, and no
`csi.storage.k8s.io` row exists anywhere; `csi-node-v1.md:3` gives the object's version as
`storage.k8s.io/v1`. The gate files also keep the object's old name: the API kind is `CSINode`, and
`CSINodeInfo` survives only as the name of a switch that was removed after v1.22.

*The post is still right about privileged mounts, and the page it rests on now argues with itself.*
`Bidirectional` mount propagation *"can be dangerous. It can damage the host operating system, and
therefore, it is allowed only in privileged containers"* (`volumes.md:1191-1193`), and *"A typical
use case for this mode is a Pod with a FlexVolume or CSI driver"* (`:1184`) — the post's flag
requirement, unchanged, still naming the mechanism the post spends a section arguing against. But
the same section opens with a caution: mount propagation *"is a low-level feature that does not work
consistently on all volume types. The Kubernetes project recommends only using mount propagation
with `hostPath` or memory-backed `emptyDir` volumes"* (`:1141-1144`). Forty lines apart, in one section, the
page names CSI as a typical use case and recommends against using the feature for anything but two
volume types that are not CSI. Both are in the pin. This exercise cites both and does not resolve
them.

*One limitation the post does not list has been reopened as a feature.* The number of volumes a node
can take was fixed at registration time; `MutableCSINodeAllocatableCount` makes it adjustable at
runtime:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.33 – v1.33 |
| beta | `false` | — | v1.34 – v1.34 |
| beta | `true` | — | v1.35 – v1.35 |
| stable | `true` | — | v1.36 – |

Four rows for four releases, because the beta stage changed its default halfway through — the one
ladder in this exercise where two rows carry the same stage name, and the reason `default` is a
column. It is stable and on from v1.36, and `storage-limits.md:75` still says *"you must enable the
`MutableCSINodeAllocatableCount` feature gate"* on kube-apiserver and kubelet. The gate file has no
`removed:` key, so the gate does exist; its stage says the feature does not need it. Neither
component's own flag reference lists it: `MutableCSINodeAllocatableCount` has zero occurrences in
`kube-apiserver.md` and zero in `kubelet.md`, while `CSIVolumeHealth` is in the kube-apiserver
`--feature-gates` list as `(ALPHA - default=false)`. So the page names two components and a gate
that those two components no longer offer. Both cited, said to disagree.

*And one thing has not moved in sixteen releases.* `CSIVolumeHealth`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.21 – |

Alpha, off, from v1.21, with no upper bound and no `removed:` key. Volume health monitoring on the
node has been one release away for longer than CSI itself took to go from alpha to the removal of
its own gate.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair): a control-plane node at
`10.10.10.130` and a worker at `10.10.10.131`. The second node is not decoration. The post's fourth
limitation is about *all* Node objects, so the test of what a kubelet may write needs a Node that
is not its own; and `kubectl get csinodes` is only interesting when it has more than one row. Bring
it up with [the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=pair`, then [the node baseline](../../strands/lab-topologies.md#node-baseline-steps) on
both, then `ssh zain@10.10.10.130`.

Say plainly what this topology cannot show. No CSI driver is installed, so nothing here calls
`CreateVolume`, stages a device or mounts anything. Every PVC in this exercise stays `Pending` and
that is the point: the objects, the schema and the authorizer are all testable with no storage
backend at all, and the post's own limitation list turns out to be readable entirely from the API.

**Do**

1. Check the post's version claim about its own group.

   ```
   kubectl api-versions | grep storage
   kubectl api-resources --api-group=storage.k8s.io
   ```

   `group-versions.md:34` lists two versions for `storage.k8s.io`. `deprecation-guide.md:298` says
   the `v1beta1` forms of `VolumeAttachment`, `CSIDriver`, `CSINode` and `StorageClass` stopped being
   served at v1.22. Note which kinds your cluster actually serves under `v1beta1`, and which of the
   two pages that leaves standing.

2. Look at what a cluster with no CSI driver already holds.

   ```
   kubectl get csidrivers
   kubectl get csinodes -o wide
   kubectl get volumeattachments
   ```

   Note how many `csinodes` rows there are and what is in their `spec.drivers`.

3. Apply the post's StorageClass verbatim, then read back what the API server kept.

   ```
   kubectl apply -f post-storageclass.yaml
   kubectl get storageclass fast-storage -o yaml
   ```

   All three `parameters` keys survive, including the two the post says the external-provisioner
   reserves. Search the pinned tree for either of them before deciding what that means.

4. Apply the post's PersistentVolumeClaim verbatim and find out why it does not bind.

   ```
   kubectl apply -f post-pvc.yaml
   kubectl describe pvc my-request-for-storage
   ```

5. Apply the post's PersistentVolume verbatim, exactly as printed.

   ```
   kubectl apply -f post-pv.yaml
   ```

   Read the error and find the character it is complaining about. Then add that character and apply
   again.

6. Apply the post's Pod verbatim and note which of the two pending objects the scheduler blames.

   ```
   kubectl apply -f post-pod.yaml
   kubectl get pod my-pod -o wide
   kubectl describe pod my-pod | tail -5
   ```

7. Compare the post's `csi:` block against the current field list.

   ```
   kubectl explain persistentvolume.spec.csi | grep -E '^\s+[a-z]'
   ```

   Eight of these fields are in the post. Name the two that are not, and say what changed about
   volumes between v1.10 and now that required them.

8. Now the title's question. Ask the API server, as the worker's kubelet, what it may do.

   ```
   N=$(kubectl get nodes -o name | sed -n 2p | cut -d/ -f2); echo "$N"
   for r in nodes csinodes volumeattachments; do
     for v in get list update patch create; do
       printf '%-18s %-7s ' "$r" "$v"
       kubectl auth can-i "$v" "$r" --as="system:node:$N" --as-group=system:nodes
     done
   done
   ```

   This runs a SubjectAccessReview per line, so the answer comes from the cluster's own authorizer
   chain rather than from a page. Read the results against the Node authorizer's documented lists
   (`node.md:21-40`) and note which of the three resources that page names at all.

9. Ask the same question about a Node the kubelet does not own, and about the object owned by it.

   ```
   C=$(kubectl get nodes -o name | sed -n 1p | cut -d/ -f2)
   kubectl auth can-i patch node/"$C" --as="system:node:$N" --as-group=system:nodes
   kubectl get csinode "$N" -o jsonpath='{.metadata.ownerReferences}' ; echo
   ```

   The second command is the mechanism that closed the post's fourth limitation. Say what owning the
   object buys that annotating the Node did not.

10. Read the field that closed the post's second limitation, and the eleven others beside it.

    ```
    kubectl explain csidriver.spec | grep -E '^\s+[a-z]'
    kubectl explain csidriver.spec.attachRequired
    ```

11. Read the two fields that closed the third limitation, then create a StorageClass that uses one.

    ```
    kubectl explain storageclass.volumeBindingMode
    kubectl explain storageclass.allowedTopologies
    kubectl create -f wait-storageclass.yaml
    kubectl apply -f wait-pvc.yaml
    kubectl get pvc
    ```

    Use the post's StorageClass with `volumeBindingMode: WaitForFirstConsumer` added and a different
    name, and a PVC pointing at it. Compare this PVC's events with step 4's.

12. Test the first limitation.

    ```
    kubectl explain persistentvolumeclaim.spec.volumeMode
    kubectl apply -f block-pvc.yaml
    ```

    Use the post's PVC with `volumeMode: Block` added and a different name. Note whether the API
    server takes it.

13. Test the post's flag requirement, twice — once against the cluster, once against the reference.

    ```
    kubectl apply -f bidir-pod.yaml
    tr ' ' '\n' < /proc/"$(pgrep kube-apiserver)"/cmdline | grep -i privileged
    ```

    `bidir-pod.yaml` is a one-container Pod with a `hostPath` volume mounted at `mountPropagation:
    Bidirectional` and **no** `securityContext.privileged`. Then set `privileged: true` and apply
    again. `kube-apiserver.md:87-90` still documents `--allow-privileged` with `[default=false]`, and
    `kubeadm/implementation-details.md:314` says kubeadm sets it to `true` unconditionally,
    *"(required e.g. by kube proxy)"*. Say which of those two your own control plane matches.

14. Last, the migration the post forecast.

    ```
    kubectl explain persistentvolume.spec.gcePersistentDisk
    kubectl explain persistentvolume.spec.flexVolume
    kubectl get storageclass
    ```

    `volumes.md:301` says the in-tree `gcePersistentDisk` driver was *"removed entirely in the v1.28
    release"*. Reconcile that with what `kubectl explain` prints, then say what a manifest setting
    that field would do on this cluster.

**Expect**

Step 1 — `storage.k8s.io/v1` certainly. If `v1beta1` is also served, check which kinds sit under it:
the four the deprecation guide names should not be among them, so a non-empty `v1beta1` is a
different resource, not a contradiction of `deprecation-guide.md:298`.

Step 2 — no `csidrivers` and no `volumeattachments`. For `csinodes`, either no resources at all or
one object per node with an empty or absent `spec.drivers`; `csi-node-v1.md:31` says a missing
object means *"there are no CSI Drivers available on the node"*, so whichever you see, the cluster
is telling you the same thing two ways. Note which way yours does it.

Step 3 — `storageclass.storage.k8s.io/fast-storage created`, and all three parameters present in the
read-back, unchanged, including `csiProvisionerSecretName: mysecret`. No warning, no validation, no
component that reads them. `parameters` is `map[string]string` and the API server checks nothing
beyond that.

Step 4 — `Pending`, with an event of the form `waiting for a volume to be created, either by
external provisioner "com.example.csi-driver" or manually by system administrator`. Note that the
provisioner name comes straight out of the post.

Step 5 — a YAML error naming a line in the `csi:` block, something like `error converting YAML to
JSON: yaml: line 24: could not find expected ':'`. The reported line number is your file's, not the
post's; the missing colon is on the post's line 119. After adding it,
`persistentvolume/my-manually-created-pv created`, and `kubectl get pv` shows it `Available` — the
PV binds to nothing, because its capacity and access mode match the pending claim but its
`storageClassName` is unset while the claim asks for `fast-storage`.

Step 6 — `Pending`, and the reason names the claim, not the volume: `pod has unbound immediate
PersistentVolumeClaims`. The Pod manifest itself is accepted without complaint, which is the
byte-for-byte-still-correct manifest in this post.

Step 7 — ten fields. Eight are the post's; the two extra are `controllerExpandSecretRef` and
`nodeExpandSecretRef`.

Step 8 — `nodes` readable and writable; `csinodes` and `volumeattachments` **not** listed in
`node.md` at all, so whatever your cluster answers for them is information the Node authorizer page
does not carry. Record the answers rather than predicting them: this is the step where the cluster
is a better source than the documentation.

Step 9 — the `patch` on the control-plane Node is where `NodeRestriction` earns its place;
`node.md:36-37` says the plugin is what limits *"a kubelet to modify its own node"*, so the answer
depends on whether your control plane enables it. Reads are limited elsewhere: `node.md:32` says
*"Kubelets are limited to reading their own Node objects"*, under the `AuthorizeNodeWithSelectors`
gate rather than under the plugin, so a `get` and a `patch` on another node's object can be refused
by two different mechanisms. Note which one your cluster uses for which. The `csinode` ownerReferences output is a single reference with
`kind: Node`, the node's own name, and `uid` matching `kubectl get node "$N" -o jsonpath='{.metadata.uid}'`.

Step 10 — twelve fields: `attachRequired`, `fsGroupPolicy`, `nodeAllocatableUpdatePeriodSeconds`,
`podInfoOnMount`, `preventPodSchedulingIfMissing`, `requiresRepublish`, `seLinuxMount`,
`serviceAccountTokenInSecrets`, `storageCapacity`, `tokenRequests`, `volumeLifecycleModes`, and
whichever your version adds. `attachRequired` is described as immutable.

Step 11 — the new StorageClass is created, and its PVC stays `Pending` with a **different** event
from step 4's: `waiting for first consumer to be created before binding`. The claim is not waiting
for a provisioner; it is waiting for a Pod. That difference is the post's third limitation, closed.

Step 12 — accepted. `volumeMode` takes `Filesystem` or `Block`, the PVC is created, and it stays
`Pending` for step 4's reason rather than for anything to do with block.

Step 13 — the non-privileged Pod is **rejected** by validation, with a message naming the field:
`spec.containers[0].volumeMounts[0].mountPropagation: Forbidden: Bidirectional mount propagation is
available only to privileged containers`. With `privileged: true` it is created. This is the post's
`--allow-privileged` sentence, still exactly true, enforced by API validation rather than by the
flag. Whether the flag itself appears in your API server's arguments is the second half of the step,
and either answer is worth writing down.

Step 14 — both fields exist and both are described as deprecated in favour of CSI. A PV setting
`gcePersistentDisk` is accepted by the API server; nothing on this cluster can act on it, because
the in-tree driver is gone and no `pd.csi.storage.gke.io` driver is installed. `kubectl get
storageclass` shows only what you created.

**Read on** — three questions against the pinned tree, and one that the tree cannot settle.

1. `volumes.md:959-962` says support for CSI spec v0.2 and v0.3 was deprecated in v1.13 and *"will
   be removed in a future release"*. The pin is v1.37. Read the note next to it — *"CSI drivers may
   not be compatible across all Kubernetes releases"* (`:964-968`) — and ask what a deprecation with
   no removal release, kept for twenty-four releases, is actually promising a driver author.
2. `csi-driver-v1.md:97` describes `serviceAccountTokenInSecrets`, added because *"sensitive tokens
   were being logged as part of volume context"*. Read it against `:105`, which documents the
   original `tokenRequests` behaviour of passing tokens in `VolumeContext`, and ask why the fix is
   an opt-in boolean rather than a change of default — then check `podInfoOnMount` at `:81` for what
   else travels through the same field.
3. `storage-limits.md:132-136` says to set `preventPodSchedulingIfMissing` to `true` only when
   cluster autoscaler runs with `--enable-csi-node-aware-scheduling=true`, because otherwise its
   scheduling simulations *"do not include the required `CSINode` information for new nodes"*. Trace
   that back to the object in step 9 and ask what it means that a node's CSI registration state is
   now load-bearing for a component outside the cluster's control plane.
4. The unanswerable one. The post's four limitations were all closed, and its migration plan was
   carried out — so this post is now history in the strongest sense available: not wrong, not
   deprecated, but finished. What the pinned tree cannot tell you is whether the fourth limitation
   was closed *because* the post wrote it down. `CSINode` exists, the registrar no longer writes to
   Nodes, and the two pages that document the object never mention the annotation it replaced or the
   permission problem that made it necessary. The post is the only place in this corpus where the
   defect and the fix appear in the same lineage, and the link between them is not recorded anywhere
   the archive can reach. That is a different shape from a post that broke: this one was retired by
   being agreed with.

Sibling exercises worth reading first, both backward and both about the machinery this post plugs
into. Dynamic provisioning arrived as annotations in 2016
([`../2016/10-dynamic-provisioning-and-storage-in-kubernetes.md`](../2016/10-dynamic-provisioning-and-storage-in-kubernetes.md)),
and the StorageClass this post's first manifest writes is the object that replaced them. A year
later the cloud-provider StorageClass table became the subject of its own post
([`../2017/01-dynamic-provisioning-and-storage-classes-kubernetes.md`](../2017/01-dynamic-provisioning-and-storage-classes-kubernetes.md)),
and every provisioner in that table is one of the in-tree plugins this post promises to migrate.
Read the three in order and the migration stops being a plan in a closing paragraph: it is the
table from 2017 emptying out.

**Teardown** — delete what this exercise created before you leave, because two of the objects have
finalizers and one has a `Retain` reclaim policy, so a half-deleted PV will still be there when you
next bring `pair` up:

```
kubectl delete pod my-pod --ignore-not-found
kubectl delete pvc --all
kubectl delete pv my-manually-created-pv --ignore-not-found
kubectl delete storageclass fast-storage --ignore-not-found
```

If the PVCs sit in `Terminating`, it is the `kubernetes.io/pvc-protection` finalizer waiting for the
Pod to go first; delete the Pod and they clear. Then
[tear the topology down](../../strands/lab-topologies.md#teardown) — the next exercise wants a
cluster with no storage objects on it at all.
