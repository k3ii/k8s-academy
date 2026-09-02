<a id="dynamic-provisioning-and-storage-classes-kubernetes"></a>
# The four cases in this post are now five, the fifth is described by two reference pages that contradict each other about whether it can happen, and the whole table of cloud defaults died on one schedule

**Post** — [Dynamic Provisioning and Storage Classes in Kubernetes](https://kubernetes.io/blog/2017/03/dynamic-provisioning-and-storage-classes-kubernetes/),
2017-03-29, Kubernetes v1.6 — Saad Ali, Michelle Au and Matthew De Lio of Google, part of *Five Days
of Kubernetes 1.6*. This is the sequel to
[2016's dynamic-provisioning post](../2016/10-dynamic-provisioning-and-storage-in-kubernetes.md):
that one announced beta, this one announces stable. The two posts share a title and almost nothing
else, and the division of labour between the two exercises follows that.

**As written** — the headline is one clause: *"dynamic provisioning has been promoted to stable
(having entered beta in 1.4)"*. Then a warning, in bold, which is what the post is really for:

> With all of these benefits, **there are a few important user-facing changes (discussed below) that
> are important to understand before using Kubernetes 1.6**.

The changes are a **matrix**, and it is the post's own contribution. Four cases, on what a
PersistentVolumeClaim's `storageClassName` is set to:

| the PVC says | the post's rule |
|---|---|
| nothing | *"the **default storage class will be used** for provisioning"*, and *"Existing, "Available", PVs that do not have the default storage class label **will not be considered** for binding"* |
| an empty string `''` | *"no storage class will be used (i.e.; dynamic provisioning is disabled for this PVC)"*, and existing classless PVs *"**will be considered** for binding"* |
| a specific value | the matching class is used, and matching `Available` PVs are considered |
| a specific value with no such class | *"the PVC will fail"* |

Bracketing the matrix are two migration statements for readers arriving from v1.5: PVs already
`Bound` *"will remain bound with the move to 1.6"* and *"will not have a StorageClass associated with
them unless the user manually adds it"*.

Next the post's second contribution, a table of what the installers now give you for free:

> To reduce the burden of setting up default StorageClasses in a cluster, beginning with 1.6,
> Kubernetes installs (via the add-on manager) default storage classes for several cloud providers.

| Cloud Provider | Default StorageClass Name | Default Provisioner |
|---|---|---|
| Amazon Web Services | gp2 | aws-ebs |
| Microsoft Azure | standard | azure-disk |
| Google Cloud Platform | standard | gce-pd |
| OpenStack | standard | cinder |
| VMware vSphere | thin | vsphere-volume |

Then reclaim policy, stated as a consequence of the feature's own goal:

> Since the goal of dynamic provisioning is to completely automate the lifecycle of storage
> resources, the default reclaim policy for dynamically provisioned volumes is "delete". [...] If
> this is not the desired behavior, the user must change the reclaim policy on the corresponding
> PersistentVolume (PV) object after the volume is provisioned.

And an FAQ, with two answers worth holding onto. On removing the defaults:

> You cannot delete the default storage class objects provided. Since they are installed as cluster
> addons, they will be recreated if they are deleted.

And on checking for one, with the output the post captured:

```
$ kubectl get sc

NAME                 TYPE

gold                 kubernetes.io/gce-pd   

standard (default)   kubernetes.io/gce-pd
```

**As it runs now** — the matrix is still the right way to think about this, and every one of its
four rows now needs a footnote. Start with the case the post does not have.

The pin's PersistentVolumes page reorganises the matrix around a *condition the post never mentions*
— whether the `DefaultStorageClass` admission plugin is on — and inside the first branch it adds a
fifth case:

> * If the admission plugin is turned on, the administrator may specify a default StorageClass.
>   All PVCs that have no `storageClassName` can be bound only to PVs of that default. [...]
>   If the administrator does not specify a default, the cluster responds to PVC creation as if the
>   admission plugin were turned off.
>   If more than one default StorageClass is specified, the newest default is used when the PVC is
>   dynamically provisioned.
> * If the admission plugin is turned off, there is no notion of a default StorageClass.
>   All PVCs that have `storageClassName` set to `""` can be bound only to PVs that have
>   `storageClassName` also set to `""`.
>   However, PVCs with missing `storageClassName` can be updated later once default StorageClass
>   becomes available. If the PVC gets updated it will no longer bind to PVs that have
>   `storageClassName` also set to `""`.
>
> — `docs/concepts/storage/persistent-volumes.md:883-895`

Read the second bullet twice. Its first clause is *"there is no notion of a default StorageClass"*
and its third sentence begins *"However, PVCs with missing `storageClassName` can be updated later
once default StorageClass becomes available."* The bullet contradicts its own premise. Its second
sentence has a different problem: the `""` rule it states is not conditional on the plugin at all —
eleven lines above, the same page states it unconditionally (*"A PVC with its `storageClassName` set
equal to `""` is always interpreted to be requesting a PV with no class"*, `:875-877`). So one of the
two bullets is filed under a condition that does not govern it, and the other describes behaviour its
own opening sentence denies.

The fifth case — more than one default class, newest wins — is stated three times at the pin, in
`persistent-volumes.md:888-889`, in `admission-controllers.md:222-224`, and in
`dynamic-provisioning.md:126-129`. The task page adds the tie-break's least obvious consequence:

> Please note you can have multiple `StorageClass` marked as default. If more than one
> `StorageClass` is marked as default, a `PersistentVolumeClaim` without an explicitly defined
> `storageClassName` will be created using the most recently created default `StorageClass`.
> When a `PersistentVolumeClaim` is created with a specified `volumeName`, it remains in a pending
> state if the static volume's `storageClassName` does not match the `StorageClass` on the
> `PersistentVolumeClaim`.
>
> — `docs/tasks/administer-cluster/change-default-storage-class.md:76-82`

That last sentence is a sixth case, and it is the trap: naming a PV by `volumeName` does not exempt
the claim from defaulting, so a hand-made classless PV plus a default class equals a claim that
never binds to the volume it named.

**Two reference pages disagree about whether an existing claim can acquire a class.** The admission
controller's own page says it cannot:

> This admission controller ignores any `PersistentVolumeClaim` updates; it acts only on creation.
>
> — `docs/reference/access-authn-authz/admission-controllers.md:226`

The PersistentVolumes page says the control plane does exactly that:

> When a default StorageClass becomes available, the control plane identifies any existing PVCs
> without `storageClassName`. For the PVCs that either have an empty value for `storageClassName`
> or do not have this key, the control plane then updates those PVCs to set `storageClassName` to
> match the new default StorageClass.
>
> — `docs/concepts/storage/persistent-volumes.md:922-926`

Both sentences are true and neither page says how. The admission plugin is a mutating webhook on
`CREATE`; the retroactive assignment is done afterwards by a controller, on the same field.
[2016's exercise](../2016/10-dynamic-provisioning-and-storage-in-kubernetes.md) walks the gate that
made that behaviour stable and the claim-that-arrives-too-early case it covers. What is new here is
only that the two pages can be read in opposite directions, and that a reader who reaches the
admission page first concludes the behaviour the other page documents is impossible. Step 6 makes
the update happen and reads the field afterwards.

The post's fourth case is now milder than the post says. *"If no corresponding storage class exists,
the PVC will fail"* — no page at the pin says a PVC fails. A claim naming a class that does not
exist stays `Pending`, indefinitely and recoverably, and the pin's language throughout is `Pending`
rather than failure. Step 4 tests it.

Now the table, which has died completely. All five provisioners in the post's third column are
in-tree volume plugins, and all five are gone. Two of the five have no occurrences at all under
`docs/`: `kubernetes.io/aws-ebs` and `kubernetes.io/azure-disk`. The other three survive only in
places where nobody meant to leave them:

- `kubernetes.io/gce-pd` — four times in the sample outputs of `change-default-storage-class.md`
  (`:47`, `:48`, `:94`, `:95`), and twice as the worked example of `dynamic-provisioning.md`
  (`:57`, `:70`), which is the concept page for this post's own subject.
- `kubernetes.io/vsphere-volume` — as a documented provisioner with parameters at
  `storage-classes.md:290-327`, and inside a `pv.kubernetes.io/provisioned-by` annotation at
  `persistent-volumes.md:274`.
- `kubernetes.io/cinder` — once, at `labels-annotations-taints/_index.md:1350`, as the example value
  of `storage.alpha.kubernetes.io/migrated-plugins`, which is the annotation that records a plugin
  *having been* migrated away from.

So the only one of the five whose surviving mention describes it accurately is the one that appears
as an example of a plugin that no longer runs. The post's link to the out-of-tree provisioners that
replaced them — `github.com/kubernetes-incubator/external-storage` — is doubly dead: both
`kubernetes-incubator` and `external-storage` have zero occurrences at the pin.

Two smaller things, both about the FAQ.

The post's *"You cannot delete the default storage class objects provided"* is now conditional, and
the pin says so without saying on what:

> Deleting the default StorageClass may not work, as it may be re-created automatically by the
> addon manager running in your cluster. Please consult the docs for your installation for details
> about addon manager and how to disable individual addons.
>
> — `docs/tasks/administer-cluster/change-default-storage-class.md:31-33`

*"May not work"*, *"may be re-created"*, *"consult the docs for your installation"* — three hedges in
three lines, because the addon manager the post treats as part of Kubernetes was always part of the
installer. `kubeadm` has no addon manager, so on the lab's own cluster the post's impossible
operation is unremarkable. Step 8 does it.

And the reclaim-policy instruction is now avoidable. The post says *"the user must change the reclaim
policy on the corresponding PersistentVolume (PV) object after the volume is provisioned"*. At the
pin the class carries the field:

> PersistentVolumes that are dynamically created by a StorageClass will have the reclaim policy
> specified in the `reclaimPolicy` field of the class, which can be either `Delete` or `Retain`. If
> no `reclaimPolicy` is specified when a StorageClass object is created, it will default to
> `Delete`.
>
> — `docs/concepts/storage/storage-classes.md:128-132`

`reclaimPolicy` is listed at `storage-classes.md:34-36` as one of the three fields *"each
StorageClass contains"*. The post's default is unchanged and its remedy is obsolete: you declare the
policy on the class up front instead of editing each PV after the fact. The post's own manifest for
the `gold` class has no `reclaimPolicy`, so it gets `Delete` — which is what the post then tells you
to go and fix by hand.

Finally the output block, which is stale in a way that has spread. The post prints two columns,
`NAME` and `TYPE`. The pin's task page prints three, `NAME PROVISIONER AGE`
(`change-default-storage-class.md:45-49`). Neither matches what `kubectl get sc` prints today, which
step 1 asks you to count. Two documents ten years apart, two different wrong column sets, and the
newer one is the one a reader is following step by step.

**The diff, and why** — the post is a stable announcement, so its job was to tell you what would
change under your feet. It did that well, and the reason it aged unevenly is that its two halves
document two different kinds of thing: one is a *semantics*, the other is an *inventory*.

The matrix is semantics, and semantics accrete. Nothing in the post's four rows is now wrong; three
more rows have been added around them, and each addition is a case somebody hit in production. More
than one default class, because installers started shipping one and administrators wanted their own.
A claim created while no default exists, because the safe way to swap defaults is to delete the old
one first. `volumeName` plus defaulting, because the two features were designed separately and
compose badly. This is the ordinary way a rule set grows: not by revision, but by exception. The
post's matrix is the trunk and the pin's is the trunk plus three branches, which is why the post
still reads as correct while being an incomplete guide.

The table is inventory, and inventory does not accrete — it is replaced. Five rows naming five
in-tree provisioners, and the entire in-tree provisioner mechanism was a bet that Kubernetes should
carry storage-vendor code in its own tree. That bet was reversed by CSI, and the reversal took the
whole table at once rather than row by row, which the ladder below shows precisely: five gates, five
identical stage lists, one release of birth and one of death. An inventory dies on the schedule of
the decision that created it, not on the schedule of its individual entries.

That difference explains the survivals. `kubernetes.io/gce-pd` is still in `dynamic-provisioning.md`
because a concept page needs *a* provisioner in its example and any real name would have needed
replacing with another real name; the page is illustrating the shape of a StorageClass, and a dead
provisioner illustrates the shape as well as a live one. That is a defensible choice nobody wrote
down, and it is indistinguishable, to a reader, from neglect. The vSphere case at
`storage-classes.md:290-327` is not defensible in the same way: it documents parameters, which are
only useful if you intend to type them.

Which brings the contradiction about updates into focus, because it has the same cause as everything
else here. `DefaultStorageClass` was specified as an admission plugin — one hook, on `CREATE`, and
the sentence on its reference page is an accurate description of that plugin. Retroactive assignment
was specified nine years later as controller behaviour, and the sentence on its page is an accurate
description of that controller. Both pages describe their own component correctly. Nobody owns the
sentence that would say *which* component sets the field, because no component does it alone, and
the reader who needs that sentence is the one holding a Pending claim. This is the recurring failure
of a documentation set organised by component: a behaviour split across two components is described
twice and explained nowhere.
[2016's exercise 10](../2016/10-dynamic-provisioning-and-storage-in-kubernetes.md) found the same
split from the storage side. Here you can watch the field change under a claim that already exists,
on a page that says it cannot.

**The ladder** — the post's table, one gate per row.

Four of the five provisioners in the post's third column, each with its own gate, and the four
ladders are the same ladder:

## InTreePluginAWSUnregister
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.21 – v1.30 |

## InTreePluginAzureDiskUnregister
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.21 – v1.30 |

## InTreePluginOpenStackUnregister
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.21 – v1.30 |

## InTreePluginvSphereUnregister
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.21 – v1.30 |

All four carry `removed: true` at file level. All four appeared at v1.21, stayed alpha and off for
ten releases, and were deleted at v1.30 without ever being promoted or defaulted on. The fifth row
of the post's table, `gce-pd`, has an identical gate —
[2016's exercise 10](../2016/10-dynamic-provisioning-and-storage-in-kubernetes.md) transcribes it
alongside the two `CSIMigrationGCE` gates that made the switch, so it is not repeated here.

A gate that is alpha and off for its whole life sounds like a feature nobody shipped, and reading
these four that way gets them backwards. The switch these gates control is *un*-registration: turned
on, the in-tree plugin stops being available early. Nobody needed to turn it on, because the
migration to CSI removed the plugin on its own schedule, at which point the gate had nothing left to
unregister and was deleted. So the ladder records an escape hatch for administrators who wanted to
go faster than the project, and the flat `false` across ten releases means the project's own schedule
was the one that ran.

Two gates from the same family show the uniformity was a choice rather than a rule:

## InTreePluginRBDUnregister
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.23 – v1.27 |
| deprecated | `false` | — | v1.28 – v1.30 |

## InTreePluginPortworxUnregister
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.23 – v1.35 |

Both `removed: true`. Neither provisioner is in the post's table. RBD's gate is the only one in the
family with a `deprecated` stage, and Portworx's ran five releases past the batch that was deleted
together at v1.30. The post's five rows sharing one ladder is therefore a fact about the post's five
rows, not about in-tree plugins in general.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), fresh. One node is enough: nothing in
this exercise schedules a pod, and every behaviour under test is the control plane deciding what a
claim's class is. Bring the guest up with
[the five provision steps](../../strands/lab-topologies.md#provision), install Kubernetes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), and confirm the
single node is Ready.

Nothing here provisions real storage. Every StorageClass below uses
`provisioner: kubernetes.io/no-provisioner`, so no volume is ever created and each claim's fate is
decided entirely by class assignment and binding — which is the post's subject. Where the post's
text depends on a working provisioner, the step says so.

**Do**

1. Establish the baseline, and count the columns the post and the pin's task page both get wrong:

   ```sh
   kubectl get storageclass
   kubectl get storageclass -o wide
   kubectl api-resources | grep storageclass
   kubectl -n kube-system get pod -l component=kube-apiserver -o yaml | grep -o "enable-admission-plugins=[^ ]*"
   ```

   A `kubeadm` cluster has no StorageClass at all, which is already a departure from the post's
   world. Compare the header line of the first command against the post's two columns
   (`NAME TYPE`) and against `change-default-storage-class.md:45-49`'s three
   (`NAME PROVISIONER AGE`). Record how many columns there actually are, and which of the two
   documents is closer.

   The last command is the one that matters for everything after it. `DefaultStorageClass` is on the
   pin's recommended list at `admission-controllers.md:130`, but that list is a recommendation to
   whoever assembles an apiserver. Say whether your cluster passes the flag at all, and what
   `admission-controllers.md:119-124` tells you to run if it does not.

2. Build the post's matrix a case at a time. First two classes and one classless PV, so every row
   has something to bind to:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata: { name: gold }
   provisioner: kubernetes.io/no-provisioner
   volumeBindingMode: Immediate
   reclaimPolicy: Retain
   ---
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata: { name: standard }
   provisioner: kubernetes.io/no-provisioner
   volumeBindingMode: Immediate
   ---
   apiVersion: v1
   kind: PersistentVolume
   metadata: { name: pv-classless }
   spec:
     capacity: { storage: 1Gi }
     accessModes: ["ReadWriteOnce"]
     persistentVolumeReclaimPolicy: Retain
     hostPath: { path: /mnt/classless }
   EOF
   kubectl get sc
   kubectl get pv pv-classless -o jsonpath='{.spec.storageClassName}|{.status.phase}{"\n"}'
   ```

   Note what the `storageClassName` of that PV is. There is no default class yet, so no case in the
   post's matrix has fired.

3. Now the post's second row, the empty string, which is the only one of the four whose rule the pin
   states unconditionally:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata: { name: pvc-empty }
   spec:
     accessModes: ["ReadWriteOnce"]
     storageClassName: ""
     resources: { requests: { storage: 1Gi } }
   EOF
   kubectl get pvc pvc-empty
   ```

   It should bind to `pv-classless`. Read `persistent-volumes.md:875-877` and say why this row does
   not depend on the admission plugin, then check that against which of the pin's two bullets the
   rule is actually printed under.

4. The post's fourth row, where the post says the claim *fails*:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata: { name: pvc-nosuchclass }
   spec:
     accessModes: ["ReadWriteOnce"]
     storageClassName: platinum
     resources: { requests: { storage: 1Gi } }
   EOF
   kubectl get pvc pvc-nosuchclass
   kubectl describe pvc pvc-nosuchclass | tail -8
   ```

   Report the `STATUS` column and the events. Then state the difference between what the post
   predicted and what happened, and say which of the two a script that polls for `Bound` would
   handle correctly.

5. The post's first row needs a default class, so mark one and watch a *new* claim get mutated:

   ```sh
   kubectl patch storageclass standard \
     -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
   kubectl get sc
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata: { name: pvc-unset }
   spec:
     accessModes: ["ReadWriteOnce"]
     resources: { requests: { storage: 1Gi } }
   EOF
   kubectl get pvc pvc-unset -o jsonpath='{.spec.storageClassName}|{.status.phase}{"\n"}'
   ```

   The manifest has no `storageClassName` and the stored object does. That is the admission plugin,
   acting on creation exactly as its page describes. Confirm that `pvc-unset` did **not** bind to
   `pv-classless`, and quote the clause in the post that predicted that.

6. Now the case the two reference pages disagree about. Make a claim while there is no default, then
   create one:

   ```sh
   kubectl patch storageclass standard \
     -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata: { name: pvc-early }
   spec:
     accessModes: ["ReadWriteOnce"]
     resources: { requests: { storage: 2Gi } }
   EOF
   kubectl get pvc pvc-early -o jsonpath='class=[{.spec.storageClassName}] phase={.status.phase}{"\n"}'
   kubectl patch storageclass gold \
     -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
   kubectl get pvc pvc-early -o jsonpath='class=[{.spec.storageClassName}] phase={.status.phase}{"\n"}'
   ```

   The field was empty and is now `gold`, on an object that already existed. Put that beside
   `admission-controllers.md:226` — *"This admission controller ignores any `PersistentVolumeClaim`
   updates; it acts only on creation"* — and beside `persistent-volumes.md:922-926`. Then answer the
   question neither page answers: name the component that changed the field, and say how a reader
   holding only the admission page could have found out.

7. The fifth case, which the post's matrix has no row for. Add a second default and see which wins:

   ```sh
   kubectl patch storageclass standard \
     -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
   kubectl get sc
   kubectl get sc -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.creationTimestamp}{"\n"}{end}'
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata: { name: pvc-twodefaults }
   spec:
     accessModes: ["ReadWriteOnce"]
     resources: { requests: { storage: 1Gi } }
   EOF
   kubectl get pvc pvc-twodefaults -o jsonpath='{.spec.storageClassName}{"\n"}'
   ```

   Two classes are now marked default. The pin says the newest wins. Check the class you got against
   the two `creationTimestamp` values, and note that both were created in the same `kubectl apply`
   in step 2 — say what the tie-break has to fall back on when the timestamps have one-second
   resolution and both classes share a value.

   Then the sixth case, from `change-default-storage-class.md:80-82`:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata: { name: pvc-byname }
   spec:
     accessModes: ["ReadWriteOnce"]
     volumeName: pv-classless
     resources: { requests: { storage: 1Gi } }
   EOF
   kubectl get pvc pvc-byname -o jsonpath='class=[{.spec.storageClassName}] phase={.status.phase}{"\n"}'
   ```

   The claim names its volume directly and still does not get it. Explain that in terms of step 5's
   result rather than in terms of `volumeName`, and say what one field you would add to make it bind.

8. Test the FAQ answer the post states as impossible:

   ```sh
   kubectl delete storageclass standard
   kubectl get sc
   sleep 30
   kubectl get sc
   ```

   The post says these objects *"will be recreated if they are deleted"*. Read
   `change-default-storage-class.md:31-33` and say which word in the pin's version makes the post's
   sentence conditional, and what specifically about your cluster decides the outcome. Then say
   whether the post was wrong in 2017.

9. Test the reclaim-policy instruction, which is the one piece of the post's advice that is now
   unnecessary rather than incorrect:

   ```sh
   kubectl get sc gold -o jsonpath='{.reclaimPolicy}{"\n"}'
   kubectl get sc -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.reclaimPolicy}{"\n"}{end}'
   kubectl apply -f - <<'EOF'
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata: { name: nopolicy }
   provisioner: kubernetes.io/no-provisioner
   EOF
   kubectl get sc nopolicy -o jsonpath='{.reclaimPolicy}{"\n"}'
   ```

   You never set `reclaimPolicy` on `nopolicy`. Read what came back against
   `storage-classes.md:128-132`, then read the post's `gold` manifest and its FAQ answer about
   changing the policy. State the one line you would add to the post's manifest to make its FAQ
   answer unnecessary, and say which of the two the post's own default forces on you.

10. Close on the table, which needs no cluster — only the pin. Take the post's five provisioner
    names and find each one:

    ```sh
    # in a checkout of kubernetes/website at the pin, from content/en:
    for p in aws-ebs azure-disk gce-pd cinder vsphere-volume; do
      printf '%-16s %s\n' "$p" "$(grep -rc -- "kubernetes.io/$p" docs 2>/dev/null | grep -v ':0$' | tr '\n' ' ')"
    done
    ```

    Two of the five have no mention anywhere. For each of the other three, open the file and decide
    which of these it is: an example that would work as well with any name, an instruction somebody
    would type, or a record of the plugin's own removal. Then answer the question the ladder above
    sets up: all five gates ran from v1.21 to v1.30 and were never defaulted on, so name what
    actually removed the plugins, and say why an administrator would ever have enabled one of those
    gates.

**Expect**

```sh
kubectl get sc
kubectl get pvc
kubectl get pv
kubectl get pvc pvc-early -o jsonpath='{.spec.storageClassName}{"\n"}'
kubectl get pvc pvc-byname -o jsonpath='phase={.status.phase}{"\n"}'
```

One StorageClass or two depending on step 8, one `Bound` claim from step 3, several `Pending` ones,
`gold` on a claim whose manifest set no class, and a claim that named its volume and never got it.

By the end you should be able to state the post's matrix with three rows added, name the component
that fills in a class on a claim that already exists, and say which of the post's five cloud
defaults still appears in the documentation in a form somebody would type.

**Read on** — the pin's
[StorageClass concept page](https://kubernetes.io/docs/concepts/storage/storage-classes/) lists the
provisioners it still documents. Read it against the post's table and answer: of the five rows the
post printed, which one still has its parameters documented, and does that page say anywhere that
the provisioner it is describing no longer ships?

**Teardown** — `kubectl delete pvc --all; kubectl delete pv pv-classless; kubectl delete sc --all`
— and note which of those three must go first, since step 6 left a claim holding a class. Then
[the teardown step](../../strands/lab-topologies.md#teardown).
