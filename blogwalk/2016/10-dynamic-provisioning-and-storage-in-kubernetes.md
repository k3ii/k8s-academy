<a id="dynamic-provisioning-and-storage-in-kubernetes"></a>
# This post became the current documentation almost word for word, and both annotations it printed outlived the removal notice it printed for one of them

**Post** — [Dynamic Provisioning and Storage Classes in Kubernetes](https://kubernetes.io/blog/2016/10/dynamic-provisioning-and-storage-in-kubernetes/),
2016-10-07, Kubernetes v1.4 — Saad Ali of Google, announcing `StorageClass` and the promotion of
dynamic provisioning from alpha to beta. It is the rare post whose text you can still find at the
pin, because the pin's concept page is this post with two edits.

**As written** — the post's frame is a promotion, and it explains the alpha it is replacing:

> The alpha version of dynamic provisioning only allowed a single, hard-coded provisioner to be used
> in a cluster at once. [...] The provisioner to use was inferred based on the cloud environment -
> EBS for AWS, Persistent Disk for Google Cloud, Cinder for OpenStack, and vSphere Volumes on
> vSphere. Furthermore, the parameters used to provision new storage volumes were fixed: only the
> storage size was configurable.

Then the beta, in one sentence that is still the design:

> The beta version of dynamic provisioning, new in Kubernetes 1.4, introduces a new API object,
> StorageClass. Multiple StorageClass objects can be defined each specifying a volume plugin (aka
> provisioner) to use to provision a volume and the set of parameters to pass to that provisioner
> when provisioning.

Two admin manifests, `slow` and `fast`:

```
kind: StorageClass
apiVersion: storage.k8s.io/v1beta1
metadata:
  name: fast
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
```

and a user request, written as JSON rather than YAML, asking for the class by **annotation**:

```
{
  "kind": "PersistentVolumeClaim",
  "apiVersion": "v1",
  "metadata": {
    "name": "claim1",
    "annotations": {
        "volume.beta.kubernetes.io/storage-class": "fast"
    }
  },
  "spec": {
    "accessModes": [ "ReadWriteOnce" ],
    "resources": { "requests": { "storage": "30Gi" } }
  }
}
```

Defaulting is a third annotation, on the class rather than the claim —
`storageclass.beta.kubernetes.io/is-default-class` — plus a new admission controller,
`DefaultStorageClass`, which the post says *"automatically adds the class annotation pointing to
the default storage class."*

Then the section this exercise is named for. The post keeps the older annotation working and says
what will happen to it:

> Kubernetes 1.4 maintains backwards compatibility with the alpha version of the dynamic
> provisioning feature to allow for a smoother transition to the beta version. The alpha behavior is
> triggered by the existence of the alpha dynamic provisioning annotation
> (volume.**alpha**.kubernetes.io/storage-class). Keep in mind that if the beta annotation
> (volume.**beta**.kubernetes.io/storage-class) is present, it takes precedence, and triggers the
> beta behavior.
>
> Support for the alpha version is deprecated and will be removed in a future release.

And a *"What's Next?"* with two candidate directions, both hedged: standard cloud provisioners
(*"we are considering"*, *"It is also being debated whether these provisioners should be marked as
default"*) and out-of-tree provisioners (*"whether Kubernetes storage plugins should live 'in-tree'
or 'out-of-tree'"*, with the implementation *"still in the air"*).

**As it runs now** — start with what did not change, because it is most of the post.

The pin's `docs/concepts/storage/dynamic-provisioning.md` is this post. Not its subject — its
sentences. Compare the post's design paragraph with the pin's, which reproduces its second half
verbatim:

> This design also ensures that end users don't have to worry about the complexity and nuances of
> how storage is provisioned, but still have the ability to select from multiple storage options.
>
> — `docs/concepts/storage/dynamic-provisioning.md:33-35`, and the post

The classes are still called `slow` and `fast`, still provisioned by `kubernetes.io/gce-pd`, still
parameterised `pd-standard` and `pd-ssd`. The claim is still `claim1`, still `ReadWriteOnce`, still
`30Gi`. The post's closing sentence on that claim —

> This claim will result in an SSD-like Persistent Disk being automatically provisioned. When the
> claim is deleted, the volume will be destroyed.

— appears at the pin with two tenses shifted:

> This claim results in an SSD-like Persistent Disk being automatically provisioned. When the claim
> is deleted, the volume is destroyed.
>
> — `docs/concepts/storage/dynamic-provisioning.md:102-103`

Against ten years, the page carries exactly three mechanical edits: `storage.k8s.io/v1beta1` became
`storage.k8s.io/v1`, the claim's annotation became `storageClassName: fast` in the spec, and
`storageclass.beta.kubernetes.io/is-default-class` lost its `beta.`

Each of those three has a different afterlife.

**The group-version was withdrawn, on the record.** The pin's deprecation guide dates it:

> The **storage.k8s.io/v1beta1** API version of CSIDriver, CSINode, StorageClass, and
> VolumeAttachment is no longer served as of v1.22.
>
> — `docs/reference/using-api/deprecation-guide.md:298`

so the post's two admin manifests are rejected at admission, not warned about.

**The class-level annotation died completely.** `storageclass.beta.kubernetes.io/is-default-class`
has **zero** occurrences anywhere at the pin. Its unprefixed successor,
`storageclass.kubernetes.io/is-default-class`, appears in five files, and the mechanism the post
described is intact down to the admission controller's name — with one behaviour the post could not
have promised:

> Note that if you set the `storageclass.kubernetes.io/is-default-class` annotation to true on more
> than one StorageClass in your cluster, and you then create a `PersistentVolumeClaim` with no
> `storageClassName` set, Kubernetes uses the most recently created default StorageClass.
>
> — `docs/concepts/storage/dynamic-provisioning.md:126-129`

**The claim-level annotations both outlived the post's forecast, and they outlived it in opposite
directions.**

The alpha annotation — the one the post said *"is deprecated and will be removed in a future
release"* — was never removed from the corpus. It survives at the pin in exactly one place, and it
is not a deprecation note. It is a live tutorial explaining its own manifest:

> The `volumeClaimTemplates` field of the `zk` StatefulSet's `spec` specifies a PersistentVolume
> provisioned for each Pod.
>
> ```yaml
> volumeClaimTemplates:
>   - metadata:
>       name: datadir
>       annotations:
>         volume.alpha.kubernetes.io/storage-class: anything
>     spec:
>       accessModes: [ "ReadWriteOnce" ]
>       resources:
>         requests:
>           storage: 20Gi
> ```
>
> — `docs/tutorials/stateful-application/zookeeper.md:409-422`

Two things are wrong with that snippet and only one of them is about the annotation. The manifest
the tutorial actually tells you to apply is
`examples/application/zookeeper/zookeeper.yaml`, whose `volumeClaimTemplates` carries **no
annotations at all** and requests **10Gi**, not 20Gi. So a page that says *"specifies"* prints
something its own example file does not say, in a block that hands the reader an annotation with
the literal value `anything` — a value that was always a placeholder, because under the alpha
behaviour the string was never read.

The beta annotation went the other way. It is still honoured, and the pin says it wins:

> When both the `storageClassName` attribute and the `volume.beta.kubernetes.io/storage-class`
> annotation are specified, the annotation `volume.beta.kubernetes.io/storage-class` takes
> precedence over the `storageClassName` attribute.
>
> — `docs/reference/labels-annotations-taints/_index.md:1281-1284`

Ten years after being replaced, the post's annotation still outranks the field that replaced it.

And the corpus cannot agree on what state it is in. Four statements, at the pin, about one
annotation:

| source | what it says |
|---|---|
| `docs/concepts/storage/dynamic-provisioning.md:79-81` | *"this annotation is deprecated since v1.9"* |
| `docs/reference/labels-annotations-taints/_index.md:1272` | heading reads **(deprecated)**; body: *"This annotation has been deprecated."* |
| `docs/concepts/storage/persistent-volumes.md:697-699` | *"This annotation is still working; however, it will become fully deprecated in a future Kubernetes release."* |
| `docs/concepts/storage/persistent-volumes.md:910-912` | *"This annotation is still working; however, it won't be supported in a future Kubernetes release."* |

Deprecated seven years ago, deprecated, not-yet-deprecated, and about-to-be-unsupported. The last
two are near-duplicate paragraphs in the same file, 213 lines apart, disagreeing about whether the
future event is a deprecation or a removal. This is the year's second such split;
[07](07-autoscaling-in-kubernetes.md) found the same shape in a scheduler message frozen in three
eras across four pages.

**One more disagreement, and this one is about the post's own example.** The pin's reference page
for provisioners lists eleven volume plugins in an *Internal Provisioner* column, and says what
that column means:

> You are not restricted to specifying the "internal" provisioners listed here (whose names are
> prefixed with "kubernetes.io" and shipped alongside Kubernetes).
>
> — `docs/concepts/storage/storage-classes.md:110-112`

Three of the eleven still carry a tick: AzureFile, PortworxVolume, VsphereVolume — and two of those
three have *(deprecated)* in their own parameter headings. **GCE PD is not in the table at all.** It
is, however, the provisioner in both examples on the dynamic-provisioning page. So the pin teaches
`provisioner: kubernetes.io/gce-pd` on the concept page and omits it from the reference table of
internal provisioners on the next page over. Cite both; do not pick.

**The diff, and why** — this is the post that was right, and the interesting failure is that its one
prediction about itself was the thing that did not happen.

The design held because it put the variability in an object instead of in the cluster's
environment. The alpha inferred the provisioner from the cloud; the beta made the provisioner a
field on a named object with free-form `parameters`. That is why the post's paragraph is still the
documentation: nothing since has needed to change the *shape* of the answer, only the plugins
plugged into it. Both of the post's hedged *"What's Next?"* items landed, and neither needed a new
object. Standard cloud provisioners became normal — the pin's own guide to changing the default
class is written as if a cloud-installed default is what you will find. Out-of-tree provisioners
became CSI, and the post's *"still in the air"* is the last moment at which that was an open
question.

What went wrong is smaller and more instructive: **the post promised a removal it did not control.**
*"Support for the alpha version is deprecated and will be removed in a future release"* is a
sentence about a code path, written by someone who could see the code path. What survived is not
the code path — the alpha annotation is inert, and a PVC carrying it gets no class at all rather
than an error. What survived is the **string**, in a tutorial, in a snippet that drifted from the
manifest it claims to describe. A deprecation notice can retire an implementation. It cannot retire
a copy of the annotation living in prose, and prose is where readers find it.

The beta annotation is the opposite lesson. It was never load-bearing for long — `storageClassName`
arrived in v1.6, two releases later — and it is still honoured, still precedence-holding, and still
documented four different ways. Backward compatibility that is cheap to keep gets kept
indefinitely, and the cost lands on the documentation rather than on the code.

**The ladder** — dynamic provisioning's own gate, and the gates for the two directions the post
guessed at.

The feature itself:

## DynamicVolumeProvisioning
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `true` | — | v1.3 – v1.7 |
| stable | `true` | — | v1.8 – v1.12 |

`removed: true` is declared at file level. Note two things a reader chasing this post will trip on.
The gate's alpha **defaults on**, which is unusual, and it never records a beta stage at all — yet
this post exists to announce a promotion to beta in v1.4, squarely inside the alpha row. The gate
tracked whether the code path was compiled in; the post's alpha and beta describe which annotation
the code path honoured. They are not the same axis, and the gate file does not say so.

The post's first *"What's Next?"*, topology-aware provisioning, is two gate files in sequence, and
the first hands off to the second in its own body:

## DynamicProvisioningScheduling
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.11 – v1.11 |
| deprecated | — | — | v1.12 – |

## VolumeScheduling
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.9 – v1.9 |
| beta | `true` | — | v1.10 – v1.12 |
| stable | `true` | — | v1.13 – v1.16 |

Both declare `removed: true`. `DynamicProvisioningScheduling`'s description says *"This feature was
superseded by the `VolumeScheduling` feature in v1.12"* — which is why its second row is a
`deprecated` stage with **no default value and no closing release**. A `stages:` entry is not
obliged to carry a `defaultValue`, and a `deprecated` stage does not: deprecation is not a default.
Transcribed losslessly, that cell is empty, and the em-dash above is the absence, not a `false`.

The post's second *"What's Next?"*, out-of-tree plugins, is the CSI migration, and for the post's
own provisioner it is three gates:

## CSIMigrationGCE
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.14 – v1.16 |
| beta | `false` | — | v1.17 – v1.22 |
| beta | `true` | — | v1.23 – v1.24 |
| stable | `true` | — | v1.25 – v1.27 |

## CSIMigrationGCEComplete
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.17 – v1.20 |
| deprecated | — | — | v1.21 – v1.21 |

## InTreePluginGCEUnregister
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.21 – v1.30 |

All three declare `removed: true`. The repeated `beta` row in `CSIMigrationGCE` is a
`defaultValue` change, not a re-promotion: the gate stayed at beta from v1.17 to v1.24 and flipped
from off to on in v1.23. `CSIMigrationGCEComplete`'s body names its own replacement — *"This flag
has been deprecated in favor of the `InTreePluginGCEUnregister` feature flag"* — so the three files
are one migration told in three overlapping windows.

Finally, the post's defaulting behaviour got a later gate of its own, for the case the post did not
consider — a claim created *before* any default class exists:

## RetroactiveDefaultStorageClass
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.25 – v1.25 |
| beta | `true` | — | v1.26 – v1.27 |
| stable | `true` | — | v1.28 – v1.28 |

`removed: true` at file level. Its behaviour is on the pin's PersistentVolumes page under
*Retroactive default StorageClass assignment*, marked stable for v1.28.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), fresh. Two nodes are needed for the
one thing this exercise measures that a single node cannot show: `WaitForFirstConsumer` binding,
where the choice of node and the choice of volume are made together. There is no cloud here, so
nothing in this exercise dynamically provisions anything — which is the point of step 8. Bring the
topology up with [the five provision steps](../../strands/lab-topologies.md#provision) using
`topology=pair`, install Kubernetes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), then
`ssh zain@10.10.10.130`.

**Do**

1. Apply the post's `fast` class exactly as printed, group-version and all:

   ```sh
   kubectl apply -f - <<'EOF'
   kind: StorageClass
   apiVersion: storage.k8s.io/v1beta1
   metadata:
     name: fast
   provisioner: kubernetes.io/gce-pd
   parameters:
     type: pd-ssd
   EOF
   ```

   It is refused. Establish which half is refused, by asking the server what it serves:

   ```sh
   kubectl api-versions | grep storage
   kubectl api-resources --api-group=storage.k8s.io
   ```

2. Fix only the group-version and apply again. It is **accepted** — with a provisioner no plugin in
   this cluster implements and parameters nobody will read. Confirm the object exists and that
   nothing has happened:

   ```sh
   kubectl get storageclass fast -o yaml
   ```

   A `StorageClass` naming an absent provisioner is a valid object. Say what that implies about
   where the validation of `provisioner` lives.

3. Now the post's claim, translated to YAML but keeping its annotation:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: claim-beta
     annotations:
       volume.beta.kubernetes.io/storage-class: fast
   spec:
     accessModes: ["ReadWriteOnce"]
     resources:
       requests:
         storage: 1Gi
   EOF
   kubectl get pvc claim-beta -o jsonpath='{.spec.storageClassName}{"\n"}'
   ```

   Watch for two things. Whether the apply printed a warning at all — the corpus disagrees about
   this annotation's status, so measure your server rather than trusting any of the four pages. And
   whether `.spec.storageClassName` came back populated, which tells you the annotation was read and
   translated rather than merely stored.

4. Test the precedence claim the pin makes. One claim carrying both, and they must disagree:

   ```sh
   kubectl create -f - <<'EOF'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: claim-both
     annotations:
       volume.beta.kubernetes.io/storage-class: fast
   spec:
     storageClassName: slow-does-not-exist
     accessModes: ["ReadWriteOnce"]
     resources:
       requests:
         storage: 1Gi
   EOF
   kubectl get pvc claim-both -o jsonpath='{.spec.storageClassName}{"\n"}'
   ```

   The pin says the annotation wins. Record what your server did. If it does not match, you have
   found a fifth statement about this annotation to add to the table above.

5. Now the alpha annotation, the one the post retired in 2016:

   ```sh
   kubectl create -f - <<'EOF'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: claim-alpha
     annotations:
       volume.alpha.kubernetes.io/storage-class: anything
   spec:
     accessModes: ["ReadWriteOnce"]
     resources:
       requests:
         storage: 1Gi
   EOF
   kubectl get pvc claim-alpha -o yaml | grep -A4 'storageClassName\|annotations'
   ```

   Compare with step 3. One annotation was translated into a field; the other was stored and
   ignored. Neither produced an error. Note that the value here — `anything` — is the value the
   pin's ZooKeeper tutorial still prints.

6. Read that drift for yourself, since it is the exercise's finding rather than a claim to take on
   trust:

   ```sh
   curl -s https://k8s.io/examples/application/zookeeper/zookeeper.yaml \
     | grep -A8 volumeClaimTemplates
   ```

   Two differences from the snippet quoted above. Both are in the tutorial's favour or against it —
   decide which, and decide which of the two a reader is more likely to be harmed by.

7. Build the class the post could not: no provisioner, lazy binding. This is the pin's own
   `local-storage` example:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: local-storage
   provisioner: kubernetes.io/no-provisioner
   volumeBindingMode: WaitForFirstConsumer
   EOF
   ```

   `provisioner` is a required field, so a class that provisions nothing still has to name a
   provisioner that provisions nothing. Say what the field is doing in that manifest.

8. Make a PV by hand on the worker, and a claim for it:

   ```sh
   ssh zain@10.10.10.131 'sudo mkdir -p /mnt/disks/vol1'
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: local-pv1
   spec:
     capacity:
       storage: 1Gi
     accessModes: ["ReadWriteOnce"]
     persistentVolumeReclaimPolicy: Retain
     storageClassName: local-storage
     local:
       path: /mnt/disks/vol1
     nodeAffinity:
       required:
         nodeSelectorTerms:
           - matchExpressions:
               - key: kubernetes.io/hostname
                 operator: In
                 values: ["<the worker's node name>"]
   EOF
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: local-claim
   spec:
     storageClassName: local-storage
     accessModes: ["ReadWriteOnce"]
     resources:
       requests:
         storage: 1Gi
   EOF
   kubectl get pvc local-claim
   ```

   The claim sits `Pending`. `kubectl describe pvc local-claim` says why in one event, and the
   reason is not that anything is missing.

9. Create the consumer and watch both decisions land at once:

   ```sh
   kubectl run pvuser --image=busybox --restart=Never \
     --overrides='{"spec":{"volumes":[{"name":"v","persistentVolumeClaim":{"claimName":"local-claim"}}],"containers":[{"name":"pvuser","image":"busybox","command":["sleep","3600"],"volumeMounts":[{"name":"v","mountPath":"/data"}]}]}}'
   kubectl get pvc local-claim -w
   ```

   The claim binds and the pod schedules in the same moment, on the node the PV's `nodeAffinity`
   named. This is the post's *"What's Next?"* topology item, delivered — and the reason it needed
   delivering is in the pin's own sentence about `Immediate` mode: binding before the Pod's
   scheduling requirements are visible produces unschedulable pods. Construct the failure: what
   would have happened here with `volumeBindingMode` left unset?

10. Finally, take the post's defaulting behaviour and its modern annotation:

    ```sh
    kubectl patch storageclass local-storage -p \
      '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
    kubectl get storageclass
    kubectl create -f - <<'EOF'
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: claim-defaulted
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
    EOF
    kubectl get pvc claim-defaulted -o jsonpath='{.spec.storageClassName}{"\n"}'
    ```

    The `DefaultStorageClass` admission controller filled the field in. The post said it *"adds the
    class annotation"*; check which of the two it actually added, and confirm the controller is on:

    ```sh
    sudo grep enable-admission-plugins /etc/kubernetes/manifests/kube-apiserver.yaml || \
      echo 'not listed — so it is on by default'
    ```

**Expect**

```sh
kubectl get storageclass
kubectl get pvc
kubectl get pv
kubectl get pvc -o custom-columns='NAME:.metadata.name,CLASS:.spec.storageClassName,ANNOT:.metadata.annotations'
```

Five claims, of which one is `Bound` and four are `Pending`, and the four are pending for three
different reasons: a class whose provisioner does not exist, a class name that does not exist, and
no class at all. The last column is the exercise: for each claim, whether the class arrived as an
annotation, as a field the reader wrote, or as a field admission wrote — and for `claim-alpha`,
neither.

The post's two admin manifests do not apply and its user request does. That asymmetry is the whole
story: the object was versioned and the annotation was not, so the versioned thing was withdrawn on
a published schedule and the unversioned thing is still here, still winning ties, and described four
incompatible ways in one corpus.

**Read on** — the pin's
[volume binding mode section](https://kubernetes.io/docs/concepts/storage/storage-classes/#volume-binding-mode)
carries a note that step 9 sidesteps: with `WaitForFirstConsumer`, *"do not use `nodeName` in the
Pod spec"*, because *"the scheduler will be bypassed and PVC will remain in `pending` state"*. Read
it and answer: which component in step 9 actually moved the claim from `Pending` to `Bound`, and why
does naming the node directly stop it rather than help it?

**Teardown** — [the teardown step](../../strands/lab-topologies.md#teardown). The PV in step 8 has
`persistentVolumeReclaimPolicy: Retain`, so `/mnt/disks/vol1` on the worker survives the claim; the
guests are what you throw away.
