<a id="raw-block-volume-support-to-beta"></a>

# Both of this post's manifests were wrong on the day it was published and only one of them has since become loud, the capability its single gotcha tells you to grant appears nowhere in the pinned docs, and one page still calls this feature beta seven years after it went stable

**Post** — [Raw Block Volume support to Beta](https://kubernetes.io/blog/2019/03/07/raw-block-volume-support-to-beta/),
7 March 2019, by Ben Swartzlander (NetApp) and Saad Ali (Google). 131 lines, 7,052 bytes.
Kubernetes v1.13.

Most posts in this walk age in their prose: a claim was true and stopped being true. This one is
the other shape. Its prose is almost entirely still correct, and both of its two code fences were
broken before anybody read them. That makes it the cleanest instance in the year of a defect that
has nothing to do with Kubernetes at all — and the most useful, because the two fences are broken
in two different ways, and seven years of API hardening has moved exactly one of them from silently
wrong to rejected outright. The other still applies, still schedules, still starts, and still
fails, because the thing wrong with it is not a field an API server has ever been able to see.

**As written** — v1.13 *"moves raw block volume support to beta"*, and the feature *"allows
persistent volumes to be exposed inside containers as a block device instead of as a mounted file
system"* (`:9`). The post then lists, under the heading *"Which volume plugins support raw
blocks?"*, the nine *"in-tree volumes types"* that do so *"as of the publishing of this blog"*
(`:13`): AWS EBS, Azure Disk, Cinder, Fibre Channel, GCE PD, iSCSI, Local volumes, RBD (Ceph) and
Vsphere (`:15-23`). Out-of-tree drivers *"may also support raw block volumes"*, but
*"Kubernetes CSI support for raw block volumes is currently alpha"* (`:25`).

The API section gives two differences from an ordinary volume. First, you *"must set
`volumeMode = "Block"` in the `PersistentVolumeClaimSpec`"*, blank means `"Filesystem"`, and
*"`"Block"` type PVCs can only bind to `"Block"` type PVs"* (`:31`). Second, in the Pod you *"must
specify a `VolumeDevice` in the Container portion of the `PodSpec` rather than a `VolumeMount`"*,
because *"`VolumeDevices` have `devicePaths` instead of `mountPaths`"* (`:33`) — and then
applications *"open, read, and write to the device node inside the container just like they would
interact with any block device on a system in a non-containerized or virtualized context"* (`:35`).

Then the two fences. The PVC (`:57-70`) is unindented apart from one level, and its last two keys
sit at the same depth: `requests:` at `:68` and `storage: 1Gi` at `:69` are both indented four
spaces under `resources:`. As printed, `resources` has two children — an empty `requests` and a
`storage` that no PVC has ever had. The Pod (`:76-96`) is correctly indented throughout, including
the `volumeDevices` list at `:88-90` that is the whole point of the post, and its only fault is one
character repeated twice: `:87` is `- “3600”`, in U+201C and U+201D rather than ASCII quotes.

The gotchas are the part of the post with the longest reach. Block devices are devices, so
*"it's possible to do low-level actions on them from inside containers that wouldn't be possible
with file system volumes"*, and SCSI disks *"support sending SCSI commands to the device using
Linux ioctls"* (`:105`). To do that from inside a container *"you must grant the `SYS_RAWIO`
capability to the container security context"*, with a link to the capabilities section of the
security-context task page (`:107`). And the caveat that outlives the rest: while Kubernetes
*"is guaranteed to deliver a block device to the container, there's no guarantee that it's actually
a SCSI disk or any other kind of disk for that matter"* (`:109`). The reader must therefore
*"either ensure that the desired disk type is used with his pods, or only deploy applications that
can handle a variety of block device types"*.

One last line is worth reading because it dates the post more precisely than its version number
does. Under *"How can I learn more?"*, `:113` offers *"additional documentation on the snapshot
feature here"* and links the raw-block section of the persistent-volumes page — a section that
has never documented snapshots. Snapshots went alpha one release earlier, in v1.12, and the
sentence travelled here from that announcement without its link.

**As it runs now** — start with the part that did not move, because it is unusually large. The
pinned `persistent-volumes.md` carries the same feature under the same name at `:1014`, marked
`{{< feature-state for_k8s_version="v1.18" state="stable" >}}` at `:1016`. Its PVC example at
`:1046-1060` is the post's fence with the indentation corrected — `resources:` at `:1057`,
`requests:` at `:1058`, `storage: 10Gi` at `:1059` — and nothing else about it has changed in seven
years. Its Pod example at `:1062-1082` uses `volumeDevices` with `name` and `devicePath` exactly as
the post describes, and the note beneath it at `:1084-1087` restates the post's `:33` almost word
for word: *"When adding a raw block device for a Pod, you specify the device path in the container
instead of a mount path."* The binding rule the post gives at `:31` has its own subsection at
`:1089`. On the prose, this post needs no translation at all.

The plugin list is the one claim that moved, and it moved by changing shape rather than length.
The pinned page now sorts PersistentVolume types into three tiers instead of one list: currently
supported (`:501-509`), *"deprecated but still available"* with a per-plugin release at which
*"migration on by default"* began (`:511-530`), and the types *"Older versions of Kubernetes also
supported"*, each with a release at which it became *"not available"* (`:532-549`). Sorting the
post's nine into those tiers is the whole version diff, and it comes out three, five and one:
`fc` (`:502`), `iscsi` (`:506`) and `local` (`:507-508`) are still first-class; AWS EBS, Azure Disk,
Cinder, GCE PD and vSphere are all in the middle tier, with migration on by default from v1.21 to
v1.25 depending on the plugin; and RBD alone is gone, *"not available"* from v1.31 (`:544-545`).
The raw-block section's own list at `:1018-1024` agrees exactly: CSI *"(including some CSI migrated
volume types)"*, FC, iSCSI and Local volume. So eight of the post's nine can still back a raw block
volume — three by the route the post describes, five by a route it does not mention, and one not at
all.

The gotcha is the surprise. `SYS_RAWIO` occurs **once** in the whole of `content/en` at the pin,
and that occurrence is this post. It is not in the security-context task page the post links, not
in the capabilities reference, not in the pod-security pages, not anywhere in `content/en/docs`.
The link itself still resolves — `security-context.md:467` is `## Set capabilities for a Container`,
and the anchor the post built in 2019 still lands on it. What the reader arrives at is a page that
explains how to add a capability and never names the one they came for. Nothing contradicts the
post. The documentation simply stopped saying it, which leaves the post as the tree's only record
of a thing that is presumably still true of Linux.

**And the tree disagrees with itself about the state of the feature this post announces.**
`persistent-volumes.md:1016` marks raw block volume support stable as of v1.18. In the Windows
section, `windows/intro.md:252-253` lists `volumeDevices` among the Pod fields Windows does not
implement, and describes it as *"a beta feature, and is not implemented on Windows. Windows cannot
attach raw block devices to pods."* Both sentences are in the pinned tree, and neither is a note
about the other. The second is the post's own title, still standing, seven years after the first says it
stopped being accurate — and the reader is in no position to pick between two pages, so the way to
settle it is to read the gate, which is a step in *Do*.

**What this exercise does not cover, and where it lives.** `volumeMode` as a field, `CSIMigration`,
the `CSIBlockVolume` gate and CSI's arrival at the head of the raw-block list all belong to
[the CSI beta post](../2018/02-container-storage-interface-beta.md), which reads the same section of
the same page from the other side. The mechanics of a static `local` PersistentVolume — the
no-provisioner StorageClass, `WaitForFirstConsumer`, and the `nodeAffinity` that
`volumes.md:693` makes mandatory — are built and explained in
[the StatefulSet post](../2016/14-statefulset-run-scale-stateful-applications-in-kubernetes.md);
this exercise uses that scaffolding without re-deriving it. Field validation as a mechanism, and
the general case of a key indented as a sibling rather than a child, are
[the RBAC post](../2017/06-using-rbac-generally-available-18.md)'s, and the
`ServerSideFieldValidation` ladder that dates the change is in
[this year's first exercise](01-apiserver-dry-run-and-kubectl-diff.md).
Typographic quotes in code fences as a recurring failure across the corpus belong to
[the extensible-admission post](../2018/01-extensible-admission-is-beta.md), which took the
precedent from [#67](https://github.com/k3ii/k8s-academy/issues/67). What is left here is this
post's own two fences, and they are enough.

**The diff, and why** — four cases, and the first is the reason this post earns a `walk` at all.

*The post was wrong when it was published, twice, and the two are not the same kind of wrong.*
Neither fence has ever applied to any cluster, and no release could have fixed either, because
there is nothing in Kubernetes to fix. But they fail at different layers, and only one layer has
been hardened since. The PVC's `storage` is a field name at a depth where no such field exists, so
it was always a validation question — and in 2019 the API server dropped unknown fields without
comment, so whatever the reader was told, they were not told which key they had mistyped. Today the
same file is refused on submission with that key named in the error. The Pod's `“3600”` is a valid
YAML string containing two characters that are not quotes, so there is nothing for any validator to
object to: the Pod is admitted today exactly as it would have been in 2019, is scheduled, pulls,
starts, and then `sleep` is handed an argument that is not a number. Seven years of API hardening
made one of these two loud. It could never have touched the other, and the reason it could not is
worth more than either fence.

*The post is still right, and here that is the headline rather than the footnote.* Every API claim
in `:29-35` holds verbatim, the plugin list is still accurate about what supports raw block once
you allow for CSI migration, and the caveat at `:109` — a block device is delivered, its kind is
not promised — is as true at the pin as it was written, and still undocumented anywhere else.

*Overtaken by stasis, in two places.* `SYS_RAWIO` was not deprecated, contradicted or replaced.
The documentation stopped mentioning it, while continuing to host the page the post sends you to.
And `windows/intro.md:252` was not corrected when v1.18 made the feature stable; it was simply not
revisited, so the post's headline survives as a stale clause in the Windows section of a page about
something else.

*Retired by being agreed with.* `BlockVolume` is the gate this post announces reaching beta, and it
is `removed: true` at the pin. It was not removed because raw block volumes were abandoned. It was
removed because the answer became unconditional: once a feature is stable and locked, the switch
has nothing left to select, and the project deletes it. The gate's disappearance is the strongest
evidence in the tree that the post's subject won.

**The ladder** — one gate. `BlockVolume`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.9 – v1.12 |
| beta | `true` | — | v1.13 – v1.17 |
| stable | `true` | — | v1.18 – v1.21 |

The beta row opens at v1.13, which is the release this post announces, so the post's title is the
second row of its own gate's table. The file carries `removed: true`, a `# Removed from Kubernetes`
comment on the line above its title, and `_build:` keys setting `list: never` and `render: false` —
it exists in the repository, is excluded from the published site, and is reachable only by reading
the tree. Its body is two sentences and points at the same `persistent-volumes.md` section the post
does.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`, guest
`zain`. Raw block needs a block device, and none of the three surviving plugins has hardware here,
so the exercise makes one: a file, a loop device over it, and a `local` PersistentVolume with
`volumeMode: Block` — which `volumes.md:697-698` explicitly sanctions as the way to *"expose the
local volume as a raw block device"*. Everything else is `kubectl` and two greps.

**Do**

1. Reproduce the post's PVC byte for byte, including the indentation, and offer it to the server.

   ```sh
   cat > /tmp/post-pvc.yaml <<'EOF'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: my-pvc
   spec:
     accessModes:
       - ReadWriteMany
     volumeMode: Block
     storageClassName: my-sc
     resources:
       requests:
       storage: 1Gi
   EOF
   kubectl apply -f /tmp/post-pvc.yaml --dry-run=server
   ```

   Nothing reaches etcd. Read the error and say how much of the reader's mistake it names.

2. Ask the API what belongs at that depth, then at the depth below it.

   ```sh
   kubectl explain persistentvolumeclaim.spec.resources
   kubectl explain persistentvolumeclaim.spec.resources.requests
   ```

3. Ask the same server the same question with field validation turned down, and then off. These are
   the answers a 2019 reader could have got.

   ```sh
   kubectl apply -f /tmp/post-pvc.yaml --dry-run=server --validate=warn
   kubectl apply -f /tmp/post-pvc.yaml --dry-run=server --validate=ignore
   ```

   Two runs, and between them a difference that matters more than the pass/fail. Write down which
   message came from which mode, and which of the three modes leaves the reader holding an
   objection that is real and says nothing about what they got wrong.

4. Correct the indentation and nothing else, and see what the server objects to next.

   ```sh
   sed 's/^    storage: 1Gi/      storage: 1Gi/' /tmp/post-pvc.yaml > /tmp/indent-fixed.yaml
   diff /tmp/post-pvc.yaml /tmp/indent-fixed.yaml
   kubectl apply -f /tmp/indent-fixed.yaml --dry-run=server
   ```

   One line of diff, and the server's answer changes completely. Say what a 2019 reader got in
   place of a working PersistentVolumeClaim, and what they had to go on.

5. Make a block device, because none of the three surviving plugins has hardware here.

   ```sh
   sudo fallocate -l 1G /var/tmp/rawblock.img
   sudo losetup -f --show /var/tmp/rawblock.img
   LOOP=$(sudo losetup -j /var/tmp/rawblock.img -O NAME -n | tr -d ' '); echo "$LOOP"
   ls -l "$LOOP"
   ```

   The first character of the `ls -l` mode is the point of the whole post. Say what it is and what
   it would be for every other volume you have used in this corpus.

6. Publish it as a `Block` PersistentVolume and claim it.

   ```sh
   N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}'); echo "$N"
   kubectl apply -f - <<EOF
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: rawblock
   provisioner: kubernetes.io/no-provisioner
   volumeBindingMode: WaitForFirstConsumer
   ---
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: rawblock-pv
   spec:
     capacity:
       storage: 1Gi
     volumeMode: Block
     accessModes:
       - ReadWriteOnce
     persistentVolumeReclaimPolicy: Retain
     storageClassName: rawblock
     local:
       path: $LOOP
     nodeAffinity:
       required:
         nodeSelectorTerms:
           - matchExpressions:
               - key: kubernetes.io/hostname
                 operator: In
                 values:
                   - $N
   EOF
   cat > /tmp/lab-pvc.yaml <<'EOF'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: my-pvc
   spec:
     accessModes:
       - ReadWriteOnce
     volumeMode: Block
     storageClassName: rawblock
     resources:
       requests:
         storage: 1Gi
   EOF
   diff /tmp/post-pvc.yaml /tmp/lab-pvc.yaml
   kubectl apply -f /tmp/lab-pvc.yaml
   kubectl get pvc my-pvc -o wide
   ```

   Three hunks in that diff. Exactly one of the three is the post's fault; name it, and say what the
   other two are for.

7. Now the second fence, byte for byte, quotes included, straight at the server.

   ```sh
   cat > /tmp/post-pod.yaml <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: my-pod
   spec:
     containers:
       - name: my-container
         image: busybox
         command:
           - sleep
           - “3600”
         volumeDevices:
           - devicePath: /dev/block
             name: my-volume
         imagePullPolicy: IfNotPresent
     volumes:
       - name: my-volume
         persistentVolumeClaim:
           claimName: my-pvc
   EOF
   kubectl apply -f /tmp/post-pod.yaml --dry-run=server -o name
   kubectl apply -f /tmp/post-pod.yaml
   kubectl get pvc my-pvc
   ```

   The strictest validation the API server has says nothing. Say why, in terms of what a validator
   is looking at.

8. Watch the failure arrive from somewhere with no view of your YAML, and read what the API stored.

   ```sh
   kubectl get pod my-pod -o wide
   kubectl logs my-pod
   kubectl get pod my-pod -o json | python3 -c 'import json,sys
   c = json.load(sys.stdin)["spec"]["containers"][0]
   print("command:", [repr(a) for a in c["command"]])
   print("devices:", c["volumeDevices"])'
   ```

   Three layers agreed to run this Pod. Name the first one in the chain that was in a position to
   object, and what it would have had to be to do so.

9. Fix the two characters, prove the volume is a device and not a filesystem, and write to it.

   ```sh
   sed 's/“3600”/"3600"/' /tmp/post-pod.yaml > /tmp/lab-pod.yaml
   diff /tmp/post-pod.yaml /tmp/lab-pod.yaml
   kubectl delete pod my-pod --wait
   kubectl apply -f /tmp/lab-pod.yaml
   kubectl wait --for=condition=Ready pod/my-pod --timeout=120s
   kubectl exec my-pod -- ls -l /dev/block
   kubectl exec my-pod -- sh -c 'mount | grep /dev/block || echo "not mounted anywhere"'
   kubectl exec my-pod -- sh -c 'dd if=/dev/zero of=/dev/block bs=1k count=1 2>&1 | tail -1'
   kubectl exec my-pod -- sh -c 'awk "/CapEff/{print \$2}" /proc/self/status'
   ```

   Keep the last value. It is the baseline for the next step.

10. Grant the capability the post's gotcha names, and check whether it arrived. This is the one
    piece of the post's advice you cannot look up.

    ```sh
    kubectl explain pod.spec.containers.securityContext.capabilities
    cat > /tmp/cap-pod.yaml <<'EOF'
    apiVersion: v1
    kind: Pod
    metadata:
      name: my-pod
    spec:
      containers:
        - name: my-container
          image: busybox
          command:
            - sleep
            - "3600"
          securityContext:
            capabilities:
              add: ["SYS_RAWIO"]
          volumeDevices:
            - devicePath: /dev/block
              name: my-volume
          imagePullPolicy: IfNotPresent
      volumes:
        - name: my-volume
          persistentVolumeClaim:
            claimName: my-pvc
    EOF
    kubectl delete pod my-pod --wait
    kubectl apply -f /tmp/cap-pod.yaml
    kubectl wait --for=condition=Ready pod/my-pod --timeout=120s
    C=$(kubectl exec my-pod -- sh -c 'awk "/CapEff/{print \$2}" /proc/self/status'); echo "$C"
    python3 -c "v=int('$C',16); print('CAP_SYS_RAWIO (bit 17) set:', bool(v >> 17 & 1))"
    ```

    Compare the mask with the one from step 9 and say which bit moved. Then, separately, say what
    would have happened to this Pod in each of the three namespaces you labelled in
    [the runc bulletin's exercise](02-runc-cve-2019-5736.md), and why the post's advice is
    unusable under two of the three profiles.

11. Settle the two pages, and count how many of the post's nine survive as fields rather than as
    prose.

    ```sh
    kubectl get --raw /metrics | grep -c 'kubernetes_feature_enabled{name="BlockVolume"' ; true
    kubectl get --raw /metrics | grep -o 'kubernetes_feature_enabled{name="[A-Za-z]*"' | wc -l
    NINE='awsElasticBlockStore|azureDisk|cinder|fc|gcePersistentDisk|iscsi|local|rbd|vsphereVolume'
    kubectl explain persistentvolume.spec | grep -E "^ +($NINE)\b"
    kubectl explain pod.spec.containers.volumeDevices
    ```

    The first two commands settle it between `persistent-volumes.md:1016` and
    `windows/intro.md:252`: a gate the server no longer carries is not a gate that is still in
    beta, and nothing you set in steps 6 through 9 switched this feature on. The third is a count to
    write down — and the thing to record is not the number but the question it raises, because
    `persistent-volumes.md:532-549` says a plugin is *"not available"*, which is not the same
    statement as a field being gone from the API.
    The last command is the field the whole post is about; note what it says about maturity.

**Expect**

Step 1: refused before validation begins, with a strict decoding error naming `spec.resources.storage`
as an unknown field. This is the whole of the reader's mistake, stated in the reader's own vocabulary
— which is the thing that was not available in 2019.

Step 2: `resources` takes two fields and neither is `storage`. It takes `limits` and `requests`, both
maps. Going one level down shows why: `storage` is not a field at any depth of a
PersistentVolumeClaim. It is a *key* in the `requests` map, alongside the other resource names, and a
key cannot be misindented into a field. The post's fence promoted a map key to a struct field, which
is why the error at step 1 can be so precise.

Step 3: `--validate=warn` reports the unknown field as a warning and then fails anyway; the failure
is not about `storage` but about a storage request being required. `--validate=ignore` gives the
second message with no warning at all. Copy both messages down. The required-value complaint is
correct, is what the reader in 2019 had, and points at the field the reader *did* write rather than
the one they wrote by mistake — so it sends them to check `requests`, which looks fine, because the
key that should be inside it is sitting next to it.

Step 4: one line changes, from four leading spaces to six, and the server accepts the claim. That
single line is the entire distance between "refused" and "created" — and in 2019 both sides of it
were "created", one of them into an object with no storage request, which is why this fence could
sit in a published post for seven years without anyone reporting it.

Step 5: `losetup -f --show` prints a path like `/dev/loop0`, and `ls -l` on it begins with `b`:
`brw-rw---- 1 root disk 7, 0`. Every other volume in this corpus has begun with `d`. That one
character is what the post means by *"a block device instead of as a mounted file system"*, and the
major number `7` names the loop driver.

Step 6: the StorageClass and the PersistentVolume are created, the `diff` shows three hunks —
`ReadWriteMany` to `ReadWriteOnce`, `my-sc` to `rawblock`, and the indentation — and the claim comes
back `Pending`. Only the third hunk is the post's fault. The first is the lab's: a `local` volume is
one node's disk, so it cannot be `ReadWriteMany`. The second is the lab's too: `my-sc` was a
placeholder and always was. `Pending` is not a failure either; the StorageClass asks for
`WaitForFirstConsumer`, so the binding is waiting for step 7.

Step 7: `--dry-run=server -o name` prints `pod/my-pod`. The strictest field validation the API server
has raises nothing, because `“3600”` is a well-formed YAML scalar in a field typed as a list of
strings — the validator's question is *"is this a string?"* and the answer is yes. The Pod is then
created for real, and `kubectl get pvc` now shows `Bound` to `rawblock-pv`: the scheduler placed the
Pod, which is what the claim was waiting for.

Step 8: the Pod is `Error` or `CrashLoopBackOff`, `kubectl logs` gives one line from busybox refusing
the argument with the two curly quotes visible inside the message, and the JSON read-back shows the
command stored exactly as written — two strings, the second six characters long, its first and last
characters not being `"`. Three components agreed to run this: the API server admitted it, the
scheduler placed it, the kubelet started it. None of them was in a position to object, because none
of them knows what `sleep` expects. The first thing in the chain able to object is the program, and
it objects at runtime, in a log, on a node, which is the most expensive place to find a typo.

Step 9: one line of diff, the Pod reaches `Ready`, and `ls -l /dev/block` inside the container gives
a `b` and the same major number you saw on the node in step 5. `mount` has no line for it — this is
the post's `:35` demonstrated: there is no filesystem, so there is nothing to mount, and `dd` reports
`1024 bytes` copied straight to the device. The `CapEff` mask is a sixteen-digit hex value; keep it.

Step 10: `capabilities` takes `add` and `drop`, both plain string arrays, so the API server accepts
`SYS_RAWIO` without knowing anything about it. The Pod reaches `Ready`, the new `CapEff` differs from
step 9's in exactly one bit, and the Python check prints `True`. The capability arrived, it does what
the post says it does, and no page in the pinned tree told you its name. Under Pod Security it is a
different story in two of the three namespaces: `SYS_RAWIO` is in neither profile's allowed list, so
`baseline` refuses it — its allowed list at `pod-security-standards.md:121-134` is *Undefined/nil*
plus thirteen names, and this is not one of them — and `restricted` refuses it too. The post's one
piece of hands-on security advice is now admissible only under `privileged`.

Step 11: the first count is `0` — the server carries no `BlockVolume` gate — while the second shows
how many gates it does carry, so the zero is a measurement and not a broken grep. Together with the
fact that nothing in steps 6 through 9 switched anything on, that settles it against
`windows/intro.md:252`: a feature with no gate is not a feature in beta. The field listing is the
number to write down, along with the reason it does not answer the question by itself. And
`kubectl explain pod.spec.containers.volumeDevices` reports *"volumeDevices is the list of block
devices to be used by the container"* and says nothing about maturity at all — the API's own
description of the field has been maturity-free for longer than the Windows page has been wrong.

**Read on**

- [The CSI beta post](../2018/02-container-storage-interface-beta.md) reads the same
  `persistent-volumes.md` section from the CSI side. After step 11's field count, say which of the
  post's five middle-tier plugins that exercise's `CSIMigration` ladder covers, and which release
  made the route the post describes stop being the route.
- [The StatefulSet post](../2016/14-statefulset-run-scale-stateful-applications-in-kubernetes.md)
  builds static `local` PersistentVolumes on the `pair` topology. Its volumes are `Filesystem`. Take
  its PV manifest and say what would have to change for it to serve a `Block` claim, and what would
  have to change on its nodes.
- [This year's first exercise](01-apiserver-dry-run-and-kubectl-diff.md) has the
  `ServerSideFieldValidation` ladder. Read step 1's error against it and give the earliest release in
  which a reader typing this post's PVC would have been told about `storage`.
- [The RBAC post](../2017/06-using-rbac-generally-available-18.md) has the other sibling-instead-of-
  child fence in this corpus. One of the two is caught by strict field validation and one is not.
  Say which, and why the difference is about the shape of the schema rather than the size of the
  mistake.

**Teardown**

```sh
kubectl delete pod my-pod --ignore-not-found
kubectl delete pvc my-pvc --ignore-not-found
kubectl delete pv rawblock-pv --ignore-not-found
kubectl delete storageclass rawblock --ignore-not-found
sudo losetup -d "$(sudo losetup -j /var/tmp/rawblock.img -O NAME -n | tr -d ' ')"
sudo rm -f /var/tmp/rawblock.img
rm -f /tmp/post-pvc.yaml /tmp/indent-fixed.yaml /tmp/lab-pvc.yaml /tmp/post-pod.yaml \
      /tmp/lab-pod.yaml /tmp/cap-pod.yaml
```

Delete in that order. The claim will not go while the Pod holds it, and the volume's reclaim policy
is `Retain`, so the PersistentVolume outlives the claim and has to be removed by name — which is the
same manual cleanup `volumes.md:712-716` warns about for every static `local` volume. Detach the loop
device before deleting its backing file, or the kernel keeps the file alive with no name. Nothing
else on the node changed: no capability was granted outside a container, and the only thing written
to the disk was one kilobyte of zeroes into a file that is now gone.
