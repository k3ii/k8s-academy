<a id="statefulset-start-ordinal"></a>

# The ranges this post splits across two clusters are arithmetic that nothing in the API ever checks, the field it patches onto a live StatefulSet re-allocates identities rather than renaming them, and the one page that still states the guarantee scopes it to a single cluster

**Post** — [Kubernetes 1.27: StatefulSet Start Ordinal Simplifies Migration](https://kubernetes.io/blog/2023/04/28/statefulset-start-ordinal/),
2023-04-28.

Peter Schuurman (Google), 223 lines, 11,508 bytes. The file at the pin is
`blog/_posts/2023/statefulset-migration.md`; the slug the URL is built from is
`statefulset-start-ordinal`. The two names describe the two halves of the post, and only one of them
reached the title.

**As written**

Kubernetes v1.26 shipped an alpha field that controls the ordinal numbering of StatefulSet Pod
replicas, and as of v1.27 it is beta: *"Ordinals can start from arbitrary non-negative numbers"*
(`:10-15`).

The Background at `:19-43` builds the case. Under `OrderedReady` Pod management, Pods are created
from ordinal `0` up to `N-1`. Migrating a StatefulSet across clusters is hard: backup and restore
solutions *"require the application to be scaled down to zero replicas prior to migration"*, and
cascading delete or on-delete migration of individual Pods is *"error prone and tedious to manage"*
and costs you the controller's self-healing. The new field changes the shape of the problem. You can
*"scale down a range {0..k-1} in a source cluster, and scale up the complementary range {k..N-1} in
a destination cluster, while maintaining application availability"*, and that *"enables you to
retain *at most one* semantics (meaning there is at most one Pod with a given identity running in a
StatefulSet)"* along with rolling-update behaviour.

Four reasons to want it, at `:49-59`: scalability, isolation, cluster configuration, control plane
upgrades. The second is worth holding on to — *"You're running a StatefulSet in a cluster that is
accessed by multiple users, and namespace isolation isn't sufficient"* (`:52-53`). The post is
explicit that a namespace boundary is not the boundary it means.

How to use it is two sentences: *"Enable the `StatefulSetStartOrdinal` feature gate on a cluster,
and create a StatefulSet with a customized `.spec.ordinals.start`"* (`:63-64`). The rest of the post
is a demonstration.

That demonstration needs two clusters called `source` and `destination`, `yq`, `helm`, and the
Bitnami `redis-cluster` chart (`:66-76`). Its prerequisites at `:83-91` are four: the gate on both
clusters, admin `kubectl` configuration for both, the same default StorageClass on both provisioning
storage *"accessible from either or both clusters"*, and *"a flat network topology"*. Then nine
steps. Deploy six Redis replicas in the source and none in the destination; scale the source down by
one (`:140`); export the vacated PVC, its PV and the shared Secret through `yq`, stripping `uid`,
`resourceVersion`, `annotations`, `finalizers`, `claimRef` and `status` (`:157-160`); create those
three objects in the destination (`:172-176`); then patch the destination with `{"spec":
{"ordinals": {"start": 5}, "replicas": 1}}` (`:182`). Step 9 says repeat until the source is at zero
and the destination is healthy at six.

What's Next (`:211-223`) is careful about what has been delivered. The feature *"provides a building
block for a StatefulSet to be split up across clusters, but does not prescribe the mechanism as to
how the StatefulSet should be migrated"*. Migration needs coordination of replicas with storage and
network, and most StatefulSets are run by operators, which *"adds another layer of complexity"*. Go
help SIG Multicluster.

**As it runs now**

The field is exactly where the post leaves it. `statefulset.md:178` heads a section *Start ordinal*,
`:180` carries the feature-state shortcode driven by the gate name, and `:182-188` gives the rule:
`.spec.ordinals` is optional and defaults to nil, and if `.spec.ordinals.start` is set, *"Pods will
be assigned ordinals from `.spec.ordinals.start` up through `.spec.ordinals.start + .spec.replicas -
1`"*. That is the post's sentence with the arithmetic spelled out. The gate reached stable at v1.31
and carries neither `removed:` nor `locked:`; the [StatefulSet family
ladder](../2017/04-kubernetes-statefulsets-daemonsets.md) already transcribes it and already states
what not being locked costs you. Nothing here re-ladders it.

The demonstration does not run at the pin, and not because anything about it broke. It needs two
clusters sharing a default StorageClass whose backing storage both can reach, a flat Pod network,
`yq`, `helm` and a third-party chart. The repo's topologies provision none of that:
`strands/lab-topologies.md:121` lists `nested` as the multi-cluster escape hatch, but no procedure
in this repo installs kind, helm or `yq`, and no walk has used that topology yet. So this exercise
puts a namespace boundary where the post puts a cluster boundary, runs the same nine steps against
it, and stops at the exact point where the substitution stops being faithful — which turns out to be
the most informative point in the procedure.

The use case survived in one place, and not the one you would guess. `statefulset.md:182-188`
documents the field and names no use for it at all. The API reference does: `stateful-set-v1.md:270`
says `start` *"may be used to number replicas from an alternate index (eg: 1-indexed) over the
default 0-indexed names, or to orchestrate progressive movement of replicas from one StatefulSet to
another"*. One StatefulSet to another — not one cluster to another. The reference kept the motion
and dropped the boundary.

Two places where the pinned tree disagrees with itself, both of them on this post's subject.

The first is about who guarantees what. `force-delete-stateful-set-pod.md:30-32` says the controller
*"tries to ensure that the specified number of Pods from ordinal 0 through N-1 are alive and ready"*
and that *"StatefulSet ensures that, at any time, there is at most one Pod with a given identity
running in a cluster"*. Both halves of that sentence are contradicted elsewhere in the same tree:
`statefulset.md:186-188` says the range is `start` through `start + replicas - 1`, and
`stateful-set-v1.md:270` names movement between StatefulSets as a purpose of the field. So one page
scopes the guarantee to a cluster and the range to zero, while two others describe a field whose
whole point is to move identities between sets that may not share a cluster. No command settles
which the project means; both statements stand at the pin.

The second is about a gate, and a command does settle part of it. `statefulset.md:259-260` says
*"the feature gate `PodIndexLabel` is enabled and locked by default for this feature, in order to
disable it, users will have to use server emulated version v1.31"*. The gate file writes no
`locked:` on either of its stages. `labels-annotations-taints/_index.md:276` heads the label
*"(beta)"* while the gate file has it stable from v1.32. And `_index.md:289-290`,
`_index.md:1628-1630` and `job.md:296-297` all present the gate as something that *"must be
enabled"* — three pages describing a switch, one page describing a switch that is welded shut, and a
gate file that records neither. Step 9 asks the control plane.

**What this exercise does not cover, and where it lives**

PersistentVolume and claim binding, the difference between `Released` and `Available`, and clearing
a stale `claimRef` are the subject of [released, not
available](../../labs/08/02-released-not-available.md) and [the claimRef
rewrite](../../labs/08/03-rewrite-a-claimref.md); step 6 walks past that door without opening it.
`.spec.ordinals.start` read against `partition`, and the ladders for both StatefulSet gates the post
touches, belong to [the StatefulSets and DaemonSets
walk](../2017/04-kubernetes-statefulsets-daemonsets.md). What becomes of claims when a set is scaled
down or deleted is [the PVC auto-deletion walk](../2021/11-statefulset-pvc-auto-deletion.md).
`maxUnavailable` is [the maxUnavailable walk](../2022/05-maxunavailable-for-statefulset.md).

**The diff, and why**

Three cases, and the order matters: ***still right***, ***wrong when it was published***, and

***never absorbed***.

***Still right*** covers everything the post says about the field. The stages it announces are the
stages the gate file records. The arithmetic it describes is the arithmetic `statefulset.md:186-188`
documents. `ordinals.start` occurs in three files at the pin — the post, `statefulset.md` and
`stateful-set-v1.md` — and the two documentation files restate the post's formula without amending
it. Three years on, nothing about the mechanism needs correcting.

***Wrong when it was published*** is step 6, and it was wrong on the day. The source half of the
hand-off at `:157-160` is three `kubectl get` commands piped through `yq` into `/tmp`. It reads; it
deletes nothing. The destination half at `:172-176` is three `kubectl create` commands. Yet the note
sitting above them at `:151-155` tells you that if your StorageClass has `reclaimPolicy: Delete` you
*"should patch the PVs in `source` with `reclaimPolicy: Retain` prior to deletion"* — a deletion no
step in the post performs. Run the nine steps exactly as printed and the source cluster finishes
holding a `Bound` PVC and a `Bound` PV for every replica it gave away, each naming the same backing
volume the destination has just claimed through a copy of that PV object. The post opens by
promising that the split preserves *at most one* semantics; its own procedure, as printed, leaves
two live claims per volume behind it. That is not staleness. Nothing changed underneath it.

***Never absorbed*** takes two greps. No file under `content/en` cites this post: the only
occurrence of the slug `statefulset-start-ordinal` anywhere in the tree is in the post's own front
matter. And the only token the post names that occurs nowhere else under `content/en` is `kep-3335`,
the namespace it tells you to create at `:96` — a pointer to the enhancement rather than a name for
anything the API has. So the post introduced no identifier the docs could have taken, which is
exactly why what went missing is not a mechanism.

What went missing is the argument. The docs took the knob: `statefulset.md:182-188` describes the
field and stops. The API reference took a narrowed version of the use: `stateful-set-v1.md:270` says
*"from one StatefulSet to another"* and leaves out the cluster boundary that made the field worth
building. Nobody took the reasoning — that *at most one* is the property a migration has to
preserve, that complementary ranges are how you preserve it, and that across a boundary the
controller cannot see, the ranges are arithmetic somebody does by hand. The single page at the pin
that names the guarantee, `force-delete-stateful-set-pod.md:30-35`, states it in the two forms the
post's technique invalidates: ordinals 0 through N-1, and one cluster. Reading this post as *still
right* alone would record that the field works and lose the only thing the field was for.

One gate does bear on the split, and it is not the one the post names. When the StatefulSet
controller creates a Pod it labels that Pod with the Pod's ordinal, and once `start` is non-zero
that label is the only place the ordinal is readable without parsing a name. The label has a gate of
its own, and no other walk in this corpus ladders it.

`PodIndexLabel`

| stage | default | locked | releases |
|---|---|---|---|
| beta | `true` | — | v1.28 – v1.31 |
| stable | `true` | — | v1.32 – |

The file records no alpha stage: the gate enters the ladder already at beta, which is unusual enough
to notice. It writes no `locked:` on either row — the half of `statefulset.md:259` that step 9
settles — and no `removed:`, so it is still a gate you can name at the pin.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — a single fresh node. Two namespaces on one cluster
stand in for the post's two clusters, and twelve hand-made `hostPath` volumes stand in for the
shared StorageClass the post requires. Provision with
[`provision`](../../strands/lab-topologies.md#provision) and the [node
baseline](../../strands/lab-topologies.md#node-baseline-steps), then `ssh zain@10.10.10.180`. Steps
1 to 9 run on the node; step 10 runs offline against a checkout of the pinned website tree. Step 9
edits the controller manager's static Pod manifest, and the restore is in Teardown.

**Do**

1. Confirm both gates are present before assuming either. The first is the post's; the second is the
   one the ladder above transcribes.

   ```sh
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' \
     | grep -iE 'startordinal|podindexlabel' || echo "no gate by those names"
   kubectl version -o json | grep gitVersion
   ```

2. Build the substitute for the post's prerequisites: two namespaces instead of two clusters, and
   twelve retained volumes instead of a shared default StorageClass.

   ```sh
   kubectl create ns src
   kubectl create ns dst
   sudo mkdir -p /mnt/kep3335
   for i in $(seq 0 11); do
     printf 'apiVersion: v1\nkind: PersistentVolume\nmetadata: { name: pv-%s }\nspec:\n  capacity: { storage: 64Mi }\n  accessModes: ["ReadWriteOnce"]\n  persistentVolumeReclaimPolicy: Retain\n  storageClassName: ""\n  hostPath: { path: /mnt/kep3335/%s, type: DirectoryOrCreate }\n---\n' "$i" "$i"
   done > /tmp/pvs.yaml
   kubectl apply -f /tmp/pvs.yaml
   kubectl get pv
   ```

3. Deploy the source set at six replicas, the post's starting size. `Parallel` Pod management is
   here so the whole range exists at once rather than one Pod at a time; the post runs
   `OrderedReady` and says so at `:19-21`.

   ```sh
   cat > /tmp/web.yaml <<'YAML'
   apiVersion: v1
   kind: Service
   metadata: { name: web }
   spec:
     clusterIP: None
     selector: { app: web }
     ports: [{ port: 80 }]
   ---
   apiVersion: apps/v1
   kind: StatefulSet
   metadata: { name: web }
   spec:
     serviceName: web
     podManagementPolicy: Parallel
     replicas: 6
     selector: { matchLabels: { app: web } }
     template:
       metadata: { labels: { app: web } }
       spec:
         containers:
         - name: c
           image: registry.k8s.io/pause:3.10
           volumeMounts: [{ name: data, mountPath: /data }]
     volumeClaimTemplates:
     - metadata: { name: data }
       spec:
         accessModes: ["ReadWriteOnce"]
         storageClassName: ""
         resources: { requests: { storage: 64Mi } }
   YAML
   kubectl -n src apply -f /tmp/web.yaml
   sleep 25
   kubectl -n src get pods -L apps.kubernetes.io/pod-index
   kubectl -n src get pvc
   ```

4. Deploy the destination set at zero replicas, which is what the post's step 4 does with `--set
   cluster.nodes=0`. Note what the destination holds before anything is handed to it.

   ```sh
   sed 's/replicas: 6/replicas: 0/' /tmp/web.yaml | kubectl -n dst apply -f -
   kubectl -n dst get sts web -o jsonpath='{.spec.replicas}{"\n"}'
   kubectl -n dst get pods,pvc
   ```

5. Perform one iteration of the hand-off — the post's steps 5 and 7 — and then ask the question the
   census row asks: do the two halves ever claim the same PVC name?

   ```sh
   kubectl -n src patch sts web -p '{"spec": {"replicas": 5}}'
   kubectl -n dst patch sts web -p '{"spec": {"ordinals": {"start": 5}, "replicas": 1}}'
   sleep 25
   kubectl -n src get pvc -o name | sort > /tmp/src.txt
   kubectl -n dst get pvc -o name | sort > /tmp/dst.txt
   comm -12 /tmp/src.txt /tmp/dst.txt
   kubectl -n src get pods
   kubectl -n dst get pods -L apps.kubernetes.io/pod-index
   ```

6. Release the claim the post never releases, and ask the question again.

   ```sh
   kubectl -n src get pvc data-web-5 \
     -o custom-columns='NAME:.metadata.name,PHASE:.status.phase,PV:.spec.volumeName'
   kubectl -n src delete pvc data-web-5
   sleep 5
   kubectl -n src get pvc -o name | sort > /tmp/src.txt
   comm -12 /tmp/src.txt /tmp/dst.txt
   kubectl get pv
   ```

   Then read the post's `:151-155` and `:157-160` together and decide, in one sentence, whether the
   missing deletion is an oversight or an assumption that somebody else tidies the source.

7. Move the destination's range while it has a Pod running. Every patch at the post's `:182` lands
   on a set that was scaled up from zero; this one does not. Predict the Pod list before you look.

   ```sh
   kubectl -n dst patch sts web -p '{"spec": {"ordinals": {"start": 4}, "replicas": 1}}'
   sleep 25
   kubectl -n dst get pods -L apps.kubernetes.io/pod-index
   kubectl -n dst get pvc
   ```

8. Give the two halves overlapping ranges, which is the one thing the post's technique must never
   do, and see what the cluster says about it.

   ```sh
   kubectl -n dst patch sts web -p '{"spec": {"ordinals": {"start": 2}, "replicas": 3}}'
   sleep 25
   kubectl -n src get pods -o name | sort > /tmp/sp.txt
   kubectl -n dst get pods -o name | sort > /tmp/dp.txt
   comm -12 /tmp/sp.txt /tmp/dp.txt
   kubectl -n dst get events --sort-by=.lastTimestamp | tail -5
   ```

9. Read the pod-index label under a non-zero start, then try to switch off the gate that writes it.
   The API server is left alone on purpose; the label is written by the controller manager.

   ```sh
   kubectl -n dst get pods -L apps.kubernetes.io/pod-index
   sudo cp /etc/kubernetes/manifests/kube-controller-manager.yaml /root/kcm.yaml.bak
   sudo sed -i '/- kube-controller-manager/a\    - --feature-gates=PodIndexLabel=false' \
     /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 30
   kubectl -n kube-system get pods -l component=kube-controller-manager
   sudo crictl logs "$(sudo crictl ps -a -q --name kube-controller-manager | head -1)" 2>&1 | tail -6
   ```

10. Offline, against a checkout of the pinned tree: `cd /path/to/kubernetes/website/content/en`.

    ```sh
    sed -n '171,188p' docs/concepts/workloads/controllers/statefulset.md
    sed -n '252,260p' docs/concepts/workloads/controllers/statefulset.md
    sed -n '262,267p' docs/concepts/workloads/controllers/statefulset.md
    sed -n '27,35p' docs/tasks/run-application/force-delete-stateful-set-pod.md
    sed -n '276,290p' docs/reference/labels-annotations-taints/_index.md
    cat docs/reference/command-line-tools-reference/feature-gates/PodIndexLabel.md
    grep -rn 'ordinals.start' docs --include='*.md'
    grep -rln 'statefulset-start-ordinal' . --include='*.md'
    ```

**Expect**

Step 1 prints two rows, each ending `1`, one per gate. Record what the `stage` label says on each:
the two gates are at different stages at the pin, and the metric is the cheapest place to see that
without opening a file. The version line reads v1.35, four releases past the one in which
`StatefulSetStartOrdinal` went stable.

Step 2 gives twelve `Available` volumes with an empty `STORAGECLASS` column, which is what
`storageClassName: ""` looks like from the outside. Nothing is bound: a `volumeClaimTemplate` does
not create claims when the StatefulSet is created.

Step 3 creates six Pods at once — `web-0` through `web-5`, not in sequence, because
`podManagementPolicy: Parallel` is set — and six claims, `data-web-0` through `data-web-5`, each
`Bound`. The `POD-INDEX` column reads 0 through 5. Notice the claim name: it is the
`volumeClaimTemplate` name, the StatefulSet name and the ordinal, joined by hyphens. That string is
the only place an ordinal is written into storage, and it is the whole of what the post's migration
has to keep disjoint.

Step 4 reports `0` replicas, no Pods and — the part worth pausing on — no claims at all. The
destination holds nothing that could collide with anything yet, because claims arrive with Pods, not
with the set.

Step 5 leaves the source with five Pods and six claims: the controller deleted `web-5` and left
`data-web-5` exactly where it was. The destination gains one Pod, `web-5`, whose `POD-INDEX` column
reads `5`. So `comm -12` prints one line, `persistentvolumeclaim/data-web-5`, and the answer to the
census row's question is no: the two halves do claim the same name. Here that is only a name,
because the two claims are in different namespaces and bind different volumes. In the post's setting
the two claims are in different clusters and, because step 6 copied the PV object across without
deleting anything in the source, they name one backing volume. The shared-storage prerequisite at
`:86-88` is what converts a name collision into a data collision, and it is the one prerequisite
this topology cannot supply.

Step 6 shows the claim `Bound` to a named volume; deleting it moves that volume to `Released` rather
than back to `Available`, which is somebody else's subject and not this one. `comm -12` now prints
nothing. The two sentences you are weighing are a warning about reclaim policy *"prior to deletion"*
and a procedure with no deletion in it.

Step 7 is the sharpest result here. The destination's `web-5` is deleted and a `web-4` is created in
its place, with `POD-INDEX` reading 4. `data-web-5` is still there, claimed by nothing, and a new
`data-web-4` is bound to a different volume. Changing `start` on a live set is not a rename. The
controller computes the desired set of ordinals and reconciles to it; an identity that drops out of
that set takes its Pod with it and leaves its volume behind. The post never does this,
`statefulset.md:182-188` never says what happens if you do, and the failure is silent.

Step 8 prints three Pod names in common — `web-2`, `web-3`, `web-4` — and the event list holds
nothing about it. No warning, no rejected field, no admission complaint. Neither namespace can see
the other, and that is the honest shape of the two-cluster case as well: `{0..k-1}` and `{k..N-1}`
are the operator's arithmetic, and there is no component anywhere in the system whose job is to
check that they do not overlap. Read `force-delete-stateful-set-pod.md:30-32` against what you just
did.

Step 9 has two answers. The label reads the global ordinal rather than the position within the set:
`web-4` carries `4` even though it is the only Pod its StatefulSet has. Then the controller manager
either refuses the flag and restarts, in which case `statefulset.md:259` is right and the gate file
is missing a `locked:` key, or it starts with the gate off, in which case the gate file is right and
four sentences across three pages are describing a lock that is not there. Write down which happened
and which of the pinned statements it leaves standing; the restore is in Teardown either way.

Step 10 should confirm every citation above, and one thing not yet named: `statefulset.md:262-267`
lists the deployment and scaling guarantees as `{0..N-1}` and `{N-1..0}`, five lines below the
section that defines ordinals as starting wherever you say. That is a third place on that page
assuming zero, and the last grep should return exactly one file — the post itself.

**Read on**

1. `statefulset.md:262-267`, the Deployment and Scaling Guarantees. Read each of the four bullets
   and mark which of them is still literally true on a set with `ordinals.start: 5`.

2. `stateful-set-v1.md:270`, the API's own description of `start`. It is one long line; it is also
   the only sentence at the pin that names moving replicas between StatefulSets as a purpose of the
   field.

3. `force-delete-stateful-set-pod.md:80-89`, on what force deletion frees and what the page asks you
   to assert before doing it. The name is the identity; that is why the migration is a naming
   problem.

4. `job.md:292-298`, the other controller that writes an index onto its Pods, under a different
   label and the same gate — with a sentence about that gate that does not match the one on the
   StatefulSet page.

5. *Unanswerable from the pin.* What the post intends to happen to the source cluster's PVC and PV
   objects once a replica has been handed over. The procedure never deletes them, the note at
   `:151-155` implies a deletion, and no page in the tree describes an end state for the cluster
   being migrated away from.

**Teardown**

```sh
sudo cp /root/kcm.yaml.bak /etc/kubernetes/manifests/kube-controller-manager.yaml
sleep 30
kubectl -n kube-system get pods -l component=kube-controller-manager
kubectl delete ns src dst
kubectl delete pv --ignore-not-found $(seq -f 'pv-%g' 0 11)
sudo rm -rf /mnt/kep3335
rm -f /tmp/pvs.yaml /tmp/web.yaml /tmp/src.txt /tmp/dst.txt /tmp/sp.txt /tmp/dp.txt
```

Then release the node with the [topology teardown](../../strands/lab-topologies.md#teardown).
