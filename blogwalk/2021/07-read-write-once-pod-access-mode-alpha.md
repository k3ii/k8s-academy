<a id="read-write-once-pod-access-mode-alpha"></a>

# The access mode's own gate was deleted after v1.30, its migration recipe was promoted into a task page with the cat pictures intact, the eighty-seven lines written for storage vendors left no trace anywhere, and a second gate named after it went stable one release before the pin

**Post** — [Introducing Single Pod Access Mode for
PersistentVolumes](https://kubernetes.io/blog/2021/09/13/read-write-once-pod-access-mode-alpha/),
2021-09-13, by Chris Henzie (Google) — 287 lines, 15,963 bytes. A fourth access mode for
PersistentVolumes and PersistentVolumeClaims, `ReadWriteOncePod`, which restricts a volume to one
Pod in the whole cluster rather than one node. Alpha at v1.22. Roughly a third of the post is
addressed to cluster operators; the rest is addressed to the people who write CSI drivers, and the
two halves have had completely different fates.

**As written**

The post starts from the three access modes that existed before v1.22 (`:37-41`): `ReadWriteOnce` —
`the volume can be mounted as read-write by a single node`; `ReadOnlyMany` — `the volume can be
mounted read-only by many nodes`; `ReadWriteMany` — `the volume can be mounted as read-write by many
nodes`. `:43` says these `are enforced by Kubernetes components like the kube-controller-manager and
kubelet to ensure only certain pods are allowed to access a given PersistentVolume`. The new fourth
mode is one line at `:49`: `ReadWriteOncePod – the volume can be mounted as read-write by a single
pod`, `that you can use for CSI volumes` (`:47`).

`:51-61` states the guarantee and shows how it is enforced. `If you create a pod with a PVC that
uses the ReadWriteOncePod access mode, Kubernetes ensures that pod is the only pod across your whole
cluster that can read that PVC or write to it`, and a second Pod referencing the same claim `will
fail to start`. The proof is a pasted Events block (`:56-61`) whose one warning reads `0/1 nodes are
available: 1 node has pod using PersistentVolumeClaim with the same name and ReadWriteOncePod access
mode.` — a scheduler message, from a one-node cluster.

`### How is this different than the ReadWriteOnce access mode?` (`:63-69`) is the argument.
`ReadWriteOnce` `restricts volume access to a single *node*, which means it is possible for multiple
pods on the same node to read from and write to the same volume`, which `could potentially be a
major problem for some applications, especially if they require at most one writer for data safety
guarantees`. The fix is stated as absolute: `Set the access mode on your PVC, and Kubernetes
guarantees that only a single pod has access.`

`## How do I use it?` (`:71-160`) is the operator's half. Enable the `ReadWriteOncePod` feature gate
`for kube-apiserver, kube-scheduler, and kubelet` by passing
`--feature-gates="...,ReadWriteOncePod=true"` (`:74-79`); update three CSI sidecars to
`csi-provisioner:v3.0.0+`, `csi-attacher:v3.3.0+` and `csi-resizer:v1.3.0+` (`:81-85`); then write a
claim whose only access mode is `ReadWriteOncePod` (`:91-102`). `#### Migrating existing
PersistentVolumes` (`:106-158`) walks an existing "cat-pictures-pv" and "cat-pictures-pvc" through
five patches: set the reclaim policy to `Retain`, scale the writer to zero and delete the claim,
clear `spec.claimRef.uid`, replace the access modes, recreate the claim with `spec.volumeName` set,
and put the reclaim policy back. A note at `:135-138` says the mode `cannot be combined with other
access modes` and that a PersistentVolume update mixing them `will fail`.

`## What volume plugins support this?` (`:162-166`) is three sentences: only CSI drivers; `SIG
Storage does not plan to support this for in-tree plugins because they are being deprecated as part
of CSI migration`; and `Support may be considered for beta for users that prefer to use the legacy
in-tree volume APIs with CSI migration enabled.`

Then `## As a storage vendor, how do I add support for this access mode to my CSI driver?`
(`:168-254`) — eighty-seven lines, a third of the post, addressed to a different audience entirely.
The CSI specification gained two access modes, `SINGLE_NODE_SINGLE_WRITER` and
`SINGLE_NODE_MULTI_WRITER`, to disambiguate the legacy `SINGLE_NODE_WRITER` (`:173-174`); a driver
must advertise the `SINGLE_NODE_MULTI_WRITER` capability on both the controller and node services
(`:175`); and two `diff` blocks against the GCP PD CSI driver (`:190-204`, `:212-240`) show the
exact two-line and four-line edits. `:256-259` closes with what comes next: `As part of the beta
graduation for this feature, SIG Storage plans to update the Kubernetes scheduler to support pod
preemption in relation to ReadWriteOncePod storage` — the higher-priority Pod wins the claim and the
lower-priority Pod is preempted. `:263` names KEP-2485.

**As it runs now** — the mode is stable and unchanged; everything around it moved.

**The access mode is exactly what the post describes.** `concepts/storage/persistent-volumes.md`
carries all four modes at `:625-640`, with `ReadWriteOncePod` marked `stable` for v1.29 by a
`feature-state` shortcode at `:637` and defined as `the volume can be mounted as read-write by a
single Pod. Use ReadWriteOncePod access mode if you want to ensure that only one pod across the
whole cluster can read that PVC or write to it.` The definition of `ReadWriteOnce` at `:625-628` was
rewritten around it: it now says in its own entry that the mode `still can allow multiple pods to
access (read from or write to) that volume when the pods are running on the same node. For single
pod access, please see ReadWriteOncePod.` The post's argument became the older mode's own
documentation.

**The gate is gone, and the post's first instruction now stops whichever component you give it to.**
`ReadWriteOncePod` ran alpha at v1.22, beta at v1.27, stable at v1.29, and its gate file declares
`removed: true` with `toVersion: "1.30"`. A v1.37 kube-apiserver, kube-scheduler or kubelet does not
recognise the name. This is the second time in this year that the first line of a post's enablement
recipe has become the line that breaks the cluster — [the seccomp exercise](06-seccomp-default.md)
measures the same shape on a kubelet — so it is worth doing once here by asking each component what
gates it knows rather than by breaking three of them.

**The migration recipe was promoted into the documentation, unchanged, cat pictures included.**
`tasks/administer-cluster/change-pv-access-mode-readwriteoncepod.md` is a task page whose subject is
the post's `:106-158`: the same "cat-pictures-pv" and "cat-pictures-pvc", the same
"cat-pictures-writer" Deployment, the same five patches in the same order, and the same note that
the mode `cannot be combined with other access modes` (`:153-157`). The page adds three things the
post did not have: a statement at `:52-54` that `Only migrations from ReadWriteOnce to
ReadWriteOncePod are supported`, the full text of the PVC and Deployment the post only named
(`:75-120`), and a caution at `:133-135` to avoid other changes such as volume resizes until the
migration is complete. Its front matter still reads `min-kubernetes-server-version: v1.22`.

**The post's `## How is this different` section became the task page's `## Why should I use
ReadWriteOncePod?`** (`:36-46`), which restates the single-node limitation and the data-safety risk
in new words and ends `If ensuring single-writer access is critical for your workloads, consider
migrating your volumes to ReadWriteOncePod.` The recommendation went further than that: two example
pages now carry the identical note — `concepts/workloads/controllers/statefulset.md:121-125` and
`tutorials/configuration/configure-persistent-volume-storage.md:101-105` both say `This example uses
the ReadWriteOnce access mode, for simplicity. For production use, the Kubernetes project recommends
using the ReadWriteOncePod access mode instead.` An alpha announcement's argument is now stamped on
two of the project's own teaching examples, apologising for the mode those examples still use.

**The CSI caveats survived word for word, including the version floors.** The note at
`persistent-volumes.md:642-652` still says the mode `is only supported for CSI volumes and
Kubernetes version 1.22+` and still lists `csi-provisioner:v3.0.0+`, `csi-attacher:v3.3.0+` and
`csi-resizer:v1.3.0+`; the task page repeats the same three lines at `:24-34`. Four years and
fifteen releases later, the minimum sidecar versions from the post are still the minimum sidecar
versions in the documentation.

**The eighty-seven lines written for storage vendors left no trace at all.**
`SINGLE_NODE_SINGLE_WRITER` and `SINGLE_NODE_MULTI_WRITER` appear **zero** times anywhere under
`content/en/docs` at the pin. Neither does the `SINGLE_NODE_MULTI_WRITER` controller or node
capability, nor the `NodePublishVolume` behaviour the post sends drivers to the CSI spec to read.
That half of the post was never a candidate for absorption: it documents the CSI specification,
which is a different project with a different repository, and kubernetes.io does not restate it. The
post is the only place the two audiences were ever addressed together.

**The mode is named in thirteen files, and four of them are about SELinux.** The full list is
`concepts/storage/persistent-volumes.md`,
`tasks/administer-cluster/change-pv-access-mode-readwriteoncepod.md`,
`concepts/workloads/controllers/statefulset.md`,
`tutorials/configuration/configure-persistent-volume-storage.md`,
`tasks/configure-pod-container/security-context.md`, `reference/kubernetes-api/core/pod-v1.md`,
`reference/kubernetes-api/storage/csi-driver-v1.md`, `reference/instrumentation/metrics.md`, and
five feature-gate files. Neither `persistent-volume-v1.md` nor `persistent-volume-claim-v1.md` is
among them: the generated API reference documents `accessModes` as a `string array` and links out to
the concept page rather than naming the four values (`persistent-volume-v1.md:72-73`). The only
place the CLI abbreviation `RWOP` appears in the whole tree is `persistent-volumes.md:659`.

**The second-order finding: a different feature took this access mode as its beachhead, and outlived
it.** `SELinuxMountReadWriteOncePod` is a gate that `speeds up container startup by allowing kubelet
to mount volumes for a Pod directly with the correct SELinux label instead of changing each file on
the volumes recursively`, and whose own file records that `The initial implementation focused on
ReadWriteOncePod volumes.` It went alpha at v1.25 — before `ReadWriteOncePod` itself was stable —
and stable at **v1.36**, one release before the pin, six releases after the gate it is named for was
deleted. The reason for the coupling is the guarantee: if exactly one Pod can mount the volume,
there is exactly one SELinux context to mount it with, so the optimisation is safe there and nowhere
else. `pod-v1.md:2290` still encodes it as a fallback — with `SELinuxMount` disabled, `MountOption`
is used for ReadWriteOncePod volumes and `Recursive` for all other volumes.

**Three kubelet metrics exist only to count what will break when that coupling is removed.**
`metrics.md:3997-3998`, `:4011-4012` and `:4025-4026` define
`volume_manager_selinux_container_warnings_total`,
`volume_manager_selinux_pod_context_mismatch_warnings_total` and
`volume_manager_selinux_volume_context_mismatch_warnings_total`, each of whose help text ends `they
will become real errors when SELinuxMountReadWriteOncePod feature is expanded to all volume access
modes.` Three of the six `volume_manager_selinux_*` metrics are counting a future. The access mode's
real legacy at the pin is not the single-writer guarantee; it is being the one place where a
mount-time optimisation was known to be safe.

**The plugin table did not keep up.** The access-modes table at `persistent-volumes.md:674-686`
still has rows for `CephFS` and `RBD`, which the same page says at `:534-535` and `:544-545` are

**not available** starting v1.31, and rows for `FlexVolume`, `AzureFile`, `VsphereVolume` and
`PortworxVolume`, which `:511-530` lists as deprecated. The `PortworxVolume` row has six cells where
the header has five. Every one of those rows carries `-` in the `ReadWriteOncePod` column, which is
true but no longer interesting; the only row that answers the question is `CSI`, which says `depends
on the driver`. `hostPath` is in the table with a `-`; `local` is not in the table at all.

**The scheduler is where the enforcement the post shows actually lives.**
`reference/scheduling/config.md:166-168` lists the plugin: `VolumeRestrictions: Checks that volumes
mounted in the node satisfy restrictions that are specific to the volume provider`, with one
extension point, `filter`. That description is the pin's whole account of the mechanism behind the
post's Events block; the words `ReadWriteOncePod` do not appear on that page. The promise at
`:256-259` — scheduler preemption for `ReadWriteOncePod` at beta graduation — is nowhere in the
documentation either: `concepts/scheduling-eviction/pod-priority-preemption.md` contains no mention
of volumes, storage or access modes at all, and no page in the tree puts `preempt` and
`ReadWriteOncePod` in the same file. Whether it shipped is a question the pin cannot answer, so this
exercise asks the cluster instead.

**The in-tree question answered itself by subtraction.** The post leaves open at `:166` that support
`may be considered for beta for users that prefer to use the legacy in-tree volume APIs with CSI
migration enabled`. Beta came at v1.27. By then the legacy APIs were going: `cephfs`, `rbd` and
several others are `not available` from the versions listed at `:532-549`, and the rest are marked

**migration on by default**. There was no constituency left to consider. The migration itself is a
`read` row in this archive rather than an exercise, because watching it needs a cloud provider's
disks; what is walkable here is its end state, which is that `kubectl get csidrivers` on a lab
cluster returns nothing and the post's precondition is unmet by construction.

**The diff, and why** — five cases, and the loudest one is a promotion rather than a breakage.

**Retired by being agreed with, completely.** Operators got a task page that is the post's migration
section with the example names intact, two teaching examples that recommend the mode by name, and a
rewritten definition of `ReadWriteOnce` that points at it. There is no daylight between what the
post asked for and what the documentation now says. This is the cleanest instance of the pattern in
the archive so far: not a caveat absorbed or a warning restated, but a whole procedure lifted, cat
pictures and all.

**Broke: the gate, and only the gate.** `--feature-gates="...,ReadWriteOncePod=true"` on any of the
three components the post names is a startup failure at the pin. Everything else in the operator's
half — the manifest, the migration patches, the combination rule, the guarantee — runs unchanged.
The post's instructions are therefore wrong in exactly one line out of roughly ninety, and that line
is the one a reader would run first. The shape is now familiar enough in this year to be worth
naming as a rule rather than rediscovering: an alpha-era enablement step ages out, the feature it
enables does not.

**Never absorbed: the vendor half.** A third of the post, addressed to CSI driver authors, has no
counterpart in kubernetes.io and never will, because it documents a specification the project does
not own. This is not the documentation disagreeing or forgetting; it is a boundary. It is worth
noticing because the post is one artifact and reads as one argument, while the tree it landed in has
a seam running through the middle of it. Half of a blog post can be promoted into the docs and the
other half be structurally ineligible.

**A promise the documentation never recorded.** The post's `What's next` says the scheduler would
gain preemption for `ReadWriteOncePod` at beta. Beta came and went, stable came and went, the gate
was deleted — and no page at the pin connects the two ideas. That is not evidence the work was
skipped; scheduler behaviour is frequently undocumented at this level of detail. It is evidence that
a blog post's forward-looking section is not a commitment the documentation is obliged to close out,
which is why this walk tests the behaviour on a cluster rather than reading for it.

**Overtaken by a use the post did not imagine.** `ReadWriteOncePod` was proposed as a data-safety
guarantee: one writer, no corruption. Its most durable consequence at the pin is a performance
optimisation — mount-time SELinux labelling — that borrowed the guarantee because the guarantee made
the optimisation provably safe, took the access mode's name into its own gate, and went stable six
releases after the access mode's gate was deleted. Three metrics are keeping score against the day
that coupling is loosened. A feature's best-known effect is not always the effect it was argued for.

**The ladder**

Two gates, both transcribed from their `stages:` lists parsed as YAML. The first is the subject's
own.

```
ReadWriteOncePod  alpha  false  1.22 - 1.26
                  beta   true   1.27 - 1.28
                  stable true   1.29 - 1.30
                  removed: true
```

Nine releases end to end, and an unusually long alpha: five releases on the first rung before beta
at v1.27, which is where the post said preemption would arrive. The body text is two lines —
`Enables the usage of ReadWriteOncePod PersistentVolume access mode.` — and `locked` never appears,
because a gate that governs whether an API value is accepted has nothing to lock; when it went, the
value simply became part of the API. The second gate is named after the first, and has not finished.

```
SELinuxMountReadWriteOncePod  alpha  false  1.25 - 1.26
                              beta   false  1.27 - 1.27
                              beta   true   1.28 - 1.35
                              stable true   1.36 -
```

Twelve releases and four stages, including the uncommon pair of beta rows: one release of beta
defaulting to `false` at v1.27, then eight of beta defaulting to `true`. There is no `removed: true`
and no `toVersion` on the stable row, so at the pin this gate is still listed. Read the two ladders
together and the arithmetic is the finding: the second gate reached alpha at v1.25, while the access
mode it is named for was still alpha, and reached stable at v1.36, six releases after that access
mode's gate had been deleted from the tree.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`, brought
up with [the five provision steps](../../strands/lab-topologies.md#provision). One node is not a
simplification here, it is the experiment. The difference between `ReadWriteOnce` and
`ReadWriteOncePod` is only visible when two Pods land on the *same* node; on two nodes the second
Pod of the `ReadWriteOnce` case might be rejected for node affinity instead, and the contrast would
prove nothing. The storage is a directory-backed `local` PersistentVolume behind a
`kubernetes.io/no-provisioner` StorageClass, which is [the raw block
exercise](../2019/03-raw-block-volume-support-to-beta.md)'s idiom and [the dynamic provisioning
exercise](../2016/10-dynamic-provisioning-and-storage-in-kubernetes.md)'s subject. No CSI driver is
installed, and that is deliberate: the post's precondition is that only CSI volumes support this
mode, and the first thing worth finding out is what "support" is actually a statement about.

**Do**

1. Ask the cluster what it has and what it knows. The last two lines ask the kube-apiserver which
   feature gates it recognises, by name:

   ```sh
   kubectl get csidrivers
   kubectl get storageclass
   kubectl explain pv.spec.accessModes
   kubectl get --raw /metrics | grep 'kubernetes_feature_enabled{name="ReadWriteOncePod"' \
     || echo "kube-apiserver: ReadWriteOncePod is not a gate it knows"
   kubectl get --raw /metrics | grep 'kubernetes_feature_enabled{name="SELinuxMount'
   ```

2. Ask the other two components the post names the same question. The scheduler serves its metrics
   on 10259 behind authentication, so reach it with the control plane's own client certificate; the
   kubelet is reachable through the API server's node proxy:

   ```sh
   N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}'); echo "$N"
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" \
     | grep 'kubernetes_feature_enabled{name="\(ReadWriteOncePod\|SELinuxMountReadWriteOncePod\)"'
   sudo curl -sk --cert /etc/kubernetes/pki/apiserver-kubelet-client.crt \
     --key /etc/kubernetes/pki/apiserver-kubelet-client.key \
     https://127.0.0.1:10259/metrics | grep 'kubernetes_feature_enabled' | grep -i 'readwriteoncepod' \
     || echo "kube-scheduler: no gate with that name in either spelling"
   ```

3. Build the `ReadWriteOnce` case and show what the post says is wrong with it: two Pods, one node,
   one claim, both writing:

   ```sh
   sudo mkdir -p /mnt/rwo-disk /mnt/rwop-disk
   kubectl apply -f - <<EOF
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: single-node
   provisioner: kubernetes.io/no-provisioner
   volumeBindingMode: WaitForFirstConsumer
   ---
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: rwo-pv
   spec:
     capacity: {storage: 1Gi}
     accessModes: [ReadWriteOnce]
     persistentVolumeReclaimPolicy: Retain
     storageClassName: single-node
     local: {path: /mnt/rwo-disk}
     nodeAffinity:
       required:
         nodeSelectorTerms:
           - matchExpressions:
               - {key: kubernetes.io/hostname, operator: In, values: [$N]}
   ---
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: rwo-claim
   spec:
     accessModes: [ReadWriteOnce]
     storageClassName: single-node
     resources: {requests: {storage: 1Gi}}
   EOF
   for i in 1 2; do
     kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Pod
   metadata:
     name: rwo-writer-$i
   spec:
     containers:
       - name: w
         image: busybox:1.36
         command: ["sh","-c","echo pod-$i >> /data/log; sleep 3600"]
         volumeMounts: [{name: d, mountPath: /data}]
     volumes:
       - name: d
         persistentVolumeClaim: {claimName: rwo-claim}
   EOF
   done
   sleep 20; kubectl get pods -o wide; sudo cat /mnt/rwo-disk/log
   ```

4. Test the combination rule the post states at `:135-138` and the task page repeats at `:153-157`.
   Nothing is created here; the API server's refusal is the whole reading:

   ```sh
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: mixed-pv
   spec:
     capacity: {storage: 1Gi}
     accessModes: [ReadWriteOnce, ReadWriteOncePod]
     storageClassName: single-node
     local: {path: /mnt/rwop-disk}
     nodeAffinity:
       required:
         nodeSelectorTerms:
           - matchExpressions:
               - {key: kubernetes.io/hostname, operator: In, values: [$N]}
   EOF
   ```

5. Now the same pair of objects with `ReadWriteOncePod` as the only mode, on a volume type the
   documentation's table does not list. Read the `ACCESS MODES` column afterwards:

   ```sh
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: rwop-pv
   spec:
     capacity: {storage: 1Gi}
     accessModes: [ReadWriteOncePod]
     persistentVolumeReclaimPolicy: Retain
     storageClassName: single-node
     local: {path: /mnt/rwop-disk}
     nodeAffinity:
       required:
         nodeSelectorTerms:
           - matchExpressions:
               - {key: kubernetes.io/hostname, operator: In, values: [$N]}
   ---
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: rwop-claim
   spec:
     accessModes: [ReadWriteOncePod]
     storageClassName: single-node
     resources: {requests: {storage: 1Gi}}
   EOF
   kubectl get pv rwop-pv rwo-pv
   ```

6. Repeat step 3's two Pods against the new claim, and read the second one's events against the
   block the post pasted at `:56-61`:

   ```sh
   for i in 1 2; do
     kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Pod
   metadata:
     name: rwop-writer-$i
   spec:
     containers:
       - name: w
         image: busybox:1.36
         command: ["sh","-c","echo pod-$i >> /data/log; sleep 3600"]
         volumeMounts: [{name: d, mountPath: /data}]
     volumes:
       - name: d
         persistentVolumeClaim: {claimName: rwop-claim}
   EOF
   done
   sleep 25; kubectl get pods -o wide
   kubectl describe pod rwop-writer-2 | sed -n '/^Events:/,$p'
   ```

7. Show that the constraint is on concurrent use rather than on the claim itself. Delete the holder
   and watch the refused Pod schedule without being touched:

   ```sh
   kubectl delete pod rwop-writer-1 --wait
   kubectl wait --for=condition=Ready pod/rwop-writer-2 --timeout=120s
   kubectl get pod rwop-writer-2 -o wide
   sudo cat /mnt/rwop-disk/log
   ```

8. Test the post's `What's next` promise from `:256-259` directly. A low-priority Pod holds the
   claim; a high-priority Pod asks for it. Preemption, if it is implemented, evicts the holder:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: scheduling.k8s.io/v1
   kind: PriorityClass
   metadata: {name: rwop-low}
   value: 100
   ---
   apiVersion: scheduling.k8s.io/v1
   kind: PriorityClass
   metadata: {name: rwop-high}
   value: 1000000
   EOF
   kubectl delete pod rwop-writer-2 --wait --ignore-not-found
   for pair in "low rwop-low" "high rwop-high"; do
     set -- $pair
     kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Pod
   metadata:
     name: prio-$1
   spec:
     priorityClassName: $2
     containers:
       - name: w
         image: busybox:1.36
         command: ["sh","-c","sleep 3600"]
         volumeMounts: [{name: d, mountPath: /data}]
     volumes:
       - name: d
         persistentVolumeClaim: {claimName: rwop-claim}
   EOF
     sleep 20
   done
   kubectl get pods -o wide
   kubectl describe pod prio-high | sed -n '/^Events:/,$p'
   kubectl get events --field-selector reason=Preempted -A
   ```

9. Read the second-order feature that took this access mode's name. The three counters are on the
   kubelet, the policy field is on the Pod, and the driver field that would make any of it apply is
   on an object this cluster does not have:

   ```sh
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" \
     | grep '^volume_manager_selinux' | sort
   kubectl explain pod.spec.seLinuxChangePolicy
   kubectl explain csidriver.spec.seLinuxMount
   kubectl get csidrivers -o name | wc -l
   ```

10. Offline, count what the feature left behind and check the concept page against itself:

    ```sh
    cd /path/to/kubernetes/website
    grep -rl --include='*.md' 'ReadWriteOncePod' content/en/docs | wc -l
    grep -rn --include='*.md' 'SINGLE_NODE_SINGLE_WRITER\|SINGLE_NODE_MULTI_WRITER\|RWOP' content/en/docs
    grep -c 'removed: true' content/en/docs/reference/command-line-tools-reference/feature-gates/ReadWriteOncePod.md
    grep -c 'removed: true' content/en/docs/reference/command-line-tools-reference/feature-gates/SELinuxMountReadWriteOncePod.md
    sed -n '674,686p' content/en/docs/concepts/storage/persistent-volumes.md
    sed -n '532,549p' content/en/docs/concepts/storage/persistent-volumes.md
    diff <(sed -n '106,158p' content/en/blog/_posts/2021/read-write-once-pod-access-mode-alpha.md) \
         <(sed -n '122,181p' content/en/docs/tasks/administer-cluster/change-pv-access-mode-readwriteoncepod.md)
    ```

**Expect**

Step 1 prints `No resources found` for `csidrivers`, an empty or near-empty StorageClass list, the
`accessModes` description from the API — which names no values — and then the answer that matters:
no `kubernetes_feature_enabled` series named `ReadWriteOncePod`, and one named
`SELinuxMountReadWriteOncePod` with `stage="STABLE"`. The metric is documented at
`metrics.md:546-551` with labels `name` and `stage` and is served by six components including all
three the post names. A gate that has been deleted has no series at all, which is a cheaper and
safer way to establish "this flag would fail" than giving the flag to the API server and finding
out.

Step 2 gives the same two answers from the kubelet and the scheduler. Both know
`SELinuxMountReadWriteOncePod`; neither knows `ReadWriteOncePod`. The `curl` needs
`apiserver-kubelet-client.crt`, which is in the `system:masters` group, because the scheduler's
metrics endpoint authenticates and authorises like any other; if your cluster was not built by
`kubeadm` the certificate path will differ. All three components the post's `:74` names are now
unanimous, and the post's `--feature-gates` line has nothing left to enable.

Step 3 shows both Pods `Running` on the one node, and `/mnt/rwo-disk/log` containing two lines. That
is `ReadWriteOnce` working exactly as designed and exactly as the post complains: the access mode
restricted the volume to one *node*, and two Pods on that node both mounted it read-write. If your
application is one that `require[s] at most one writer for data safety guarantees`, this is the
failure the post was written about, and it takes twenty seconds to produce.

Step 4 is refused by the API server. The message names the field and the rule — a PersistentVolume
may not combine `ReadWriteOncePod` with any other access mode — and no object is created; `kubectl
get pv mixed-pv` afterwards returns `NotFound`. This is validation rather than scheduling, it needs
no driver and no gate, and it is the one part of the post's mechanism that is enforced before
anything is scheduled anywhere.

Step 5 creates both objects and prints `RWOP` in the `ACCESS MODES` column next to `rwo-pv`'s `RWO`.
Two things are worth recording. The abbreviation is documented in exactly one line of the whole
tree, `persistent-volumes.md:659`. And the API accepted `ReadWriteOncePod` on a `local`
PersistentVolume, although `persistent-volumes.md:643-645` says the mode `is only supported for CSI
volumes` and the table at `:674-686` does not list `local` at all. Nothing here contradicts the
documentation yet — "supported" may be a claim about enforcement rather than about validation. Step
6 is what decides that.

Step 6 is the payload. Expect `rwop-writer-1` `Running` and `rwop-writer-2` `Pending`, with an event
whose text is close to the post's: a `FailedScheduling` warning from `default-scheduler` saying the
one node has a Pod using the PersistentVolumeClaim with the same name and the `ReadWriteOncePod`
access mode. Copy the exact wording; the phrasing of scheduler messages changes between releases and
the post's `:60` is from v1.22. What this establishes is where the guarantee lives: no CSI driver is
installed, no kubelet-side check ran, and the refusal still happened — because the
`VolumeRestrictions` scheduler plugin (`reference/scheduling/config.md:166-168`) reads the claim's
access modes and knows nothing about volume types. The documentation's `only supported for CSI
volumes` is therefore a statement about the driver-side half of the contract, not about this half.
If instead your cluster schedules the second Pod, that is the more interesting result: record it,
because it would mean the scheduler-side check is conditioned on something this lab does not have.

Step 7 shows `rwop-writer-2` going `Running` within a few seconds of `rwop-writer-1` being deleted,
on the same node, against the same claim, with `/mnt/rwop-disk/log` now holding two lines written at
different times. The mode constrains concurrent mounts, not ownership: the claim is not bound to a
Pod, it is refused to a second one while a first holds it. That is worth seeing because the post's
wording — `the pod will fail to start because the PVC is already in use by another pod` — describes
a state, and states end.

Step 8 is the open question. If preemption for `ReadWriteOncePod` shipped as `:258-259` promised,
`prio-low` is evicted, an event with reason `Preempted` appears, and `prio-high` runs. If it did
not, `prio-high` stays `Pending` with the same `FailedScheduling` message as step 6 and priority
buys it nothing. Either outcome is a finding, because the pin's documentation records neither: no
page mentions preemption and `ReadWriteOncePod` together, and
`concepts/scheduling-eviction/pod-priority-preemption.md` does not mention volumes at all. Write
down which you got and against which version; this is one of the few places in this year where the
archive can answer a question the documentation left open.

Step 9 prints six `volume_manager_selinux_*` counters, all at zero on a cluster with no SELinux
labels in play, and the three `_warnings_total` ones carry the help text from `metrics.md:3998`,
`:4012` and `:4026` about becoming real errors `when SELinuxMountReadWriteOncePod feature is
expanded to all volume access modes`. `kubectl explain pod.spec.seLinuxChangePolicy` describes the
`MountOption`/`Recursive` choice and — matching `pod-v1.md:2290` — the fallback in which
`ReadWriteOncePod` volumes get the fast path and everything else does not. The `csidriver` count is
`0`, so none of it applies on this cluster: the field that would switch it on, `spec.seLinuxMount`,
lives on an object that does not exist here.

Step 10 confirms the counts: thirteen files name the access mode; `SINGLE_NODE_SINGLE_WRITER` and
`SINGLE_NODE_MULTI_WRITER` return nothing at all while `RWOP` returns exactly one line; the first
gate file has `removed: true` and the second does not. The two `sed` blocks print the access-modes
table and the plugin-types list from the same page, sixty lines apart, disagreeing about whether
CephFS and RBD exist. The final `diff` is the point of the whole step: the post's migration section
and the task page's are close enough that the differences fit on a screen, and every one of them is
an addition.

**Read on**

1. `tasks/administer-cluster/change-pv-access-mode-readwriteoncepod.md` in full, read as the post's
   own text with four years of edits applied. Pay attention to what was added rather than changed:
   the one-directional migration statement at `:52-54`, the dynamic-provisioning name lookup at
   `:60-69`, and the resize caution at `:133-135`. Each is a thing someone got wrong following the
   blog post.

2. `concepts/storage/persistent-volumes.md:614-686` is the access-modes section entire: the four
   definitions, the CSI note with its sidecar floors, the CLI abbreviations, the warning at
   `:661-669` that access modes `do not enforce write protection once the storage has been mounted`
   for the other three modes, and the plugin table with its stale rows. The warning is the sharpest
   sentence on the page and explains why `ReadWriteOncePod` had to be a scheduling constraint rather
   than a mount flag.

3. `tasks/configure-pod-container/security-context.md:693-772` is where the second gate is
   documented as a user-facing feature rather than as a name: the SELinux mount optimisation, its
   interaction with `seLinuxChangePolicy`, and the note at `:763` that
   `SELinuxMountReadWriteOncePod` `enables the optimization for volumes with accessModes:
   ["ReadWriteOncePod"]`. Read it with `reference/kubernetes-api/storage/csi-driver-v1.md:93`, which
   is the driver's side of the same bargain.

4. The storage machinery this exercise borrows belongs to earlier rows. [The raw block
   exercise](../2019/03-raw-block-volume-support-to-beta.md) owns the `no-provisioner` StorageClass
   and the node-affinity-pinned `local` PersistentVolume used here. [The dynamic provisioning
   exercise](../2016/10-dynamic-provisioning-and-storage-in-kubernetes.md) owns provisioning and
   binding as subjects. [The CSI beta exercise](../2018/02-container-storage-interface-beta.md) owns
   the `CSIDriver` object whose absence shapes step 9. [The seccomp exercise](06-seccomp-default.md)
   is the other removed-gate measurement in this year, done the expensive way on a live kubelet.
   Release timing is in
   [`research/blog-era-translation.md`](../../research/blog-era-translation.md).

5. Unanswerable from the pin: whether scheduler preemption for `ReadWriteOncePod` was ever
   implemented. The post promises it for beta, the gate reached beta at v1.27 and stable at v1.29,
   and the documentation at the pin connects preemption to this access mode nowhere — so step 8 is a
   measurement of the cluster, not a check against a source. Two smaller ones go the same way: what
   `only supported for CSI volumes` was intended to exclude, given that the scheduler-side check
   needs no driver; and why the access-modes table still carries rows for plugins the same page says
   were removed at v1.31.

**Teardown**

This exercise created one StorageClass, three PersistentVolumes, two claims, up to six Pods, two
PriorityClasses and two directories on the node. The reclaim policy is `Retain`, so the
PersistentVolumes outlive their claims and have to be removed by name:

```bash
kubectl delete pod rwo-writer-1 rwo-writer-2 rwop-writer-1 rwop-writer-2 prio-low prio-high --ignore-not-found
kubectl delete pvc rwo-claim rwop-claim --ignore-not-found
kubectl delete pv rwo-pv rwop-pv mixed-pv --ignore-not-found
kubectl delete storageclass single-node --ignore-not-found
kubectl delete priorityclass rwop-low rwop-high --ignore-not-found
sudo rm -rf /mnt/rwo-disk /mnt/rwop-disk
kubectl get pv,pvc,sc,priorityclass -A
```

The last command should list nothing but the built-in `system-cluster-critical` and
`system-node-critical` priority classes. Nothing was installed on the node and no component
configuration was changed, so the guest is back to where the provision steps left it; leave it up if
the next row in this year wants it, or [destroy it](../../strands/lab-topologies.md#teardown).
