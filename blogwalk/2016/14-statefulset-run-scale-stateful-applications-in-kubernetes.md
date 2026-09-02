<a id="statefulset-run-scale-stateful-applications-in-kubernetes"></a>
# Nothing in the documentation admits PetSet ever existed, and the smaller rename inside this post's own tutorial was left half-done in a sentence that still names an object nobody creates

**Post** — [StatefulSet: Run and Scale Stateful Applications Easily in Kubernetes](https://kubernetes.io/blog/2016/12/statefulset-run-scale-stateful-applications-in-kubernetes/),
2016-12-20, Kubernetes v1.5 — Kenneth Owens and Eric Tune of Google, also part of the *Five Days of
Kubernetes 1.5* series. The post announces a **rename** and a promotion in the same sentence, which
is why it is the right place in this year to look at what a rename costs.

**As written** — the opening sentence is the whole subject:

> In the latest release, Kubernetes 1.5, we've moved the feature formerly known as PetSet into beta
> as StatefulSet. There were no major changes to the API Object, other than the community selected
> name, but we added the semantics of "at most one pod per index" for deployment of the Pods in the
> set.

Four properties are claimed — *"ordered deployment, ordered termination, unique network names, and
persistent stable storage"* — with an explicit disclaimer of completeness and a compatibility
promise: *"we can extend the API in a backwards-compatible way as we progress toward an eventual GA
release."*

Then four questions a reader should ask before adopting it (remote versus local storage, whether
scaling is a problem you actually have, whether predictable performance matters, whether you need
specialised hardware), and one worked example: a three-server ZooKeeper ensemble, in a manifest the
post links and quotes throughout. The manifest creates four objects:

```
service "zk-headless" created
configmap "zk-config" created
poddisruptionbudget "zk-budget" created
statefulset "zk" created
```

The demonstrations are the interesting part, because each one is a claim you can still test. Pods
appear in order and each waits for its predecessor to be Ready. Hostnames carry ordinals — `zk-0`,
`zk-1`, `zk-2` — and ZooKeeper's `myid` files are *"populated by adding one to the ordinal extracted
from the Pods' hostnames"*. Each pod has a stable FQDN under the headless Service. Deleting the
StatefulSet terminates pods in reverse ordinal order. And then the payoff:

> If you use the "zkCli.sh" script to get the value entered prior to deleting the StatefulSet, you
> will find that the ensemble still serves the data.

The maintenance section prints the disruption budget:

```
$ kubectl get poddisruptionbudget zk-budget
NAME        MIN-AVAILABLE   ALLOWED-DISRUPTIONS   AGE
zk-budget   2               1                     2h
```

and the anti-affinity rule that keeps two ensemble members off one node:

```
{
  "podAntiAffinity": {
    "requiredDuringSchedulingRequiredDuringExecution": [{
      "labelSelector": { "matchExpressions": [{
        "key": "app", "operator": "In", "values": ["zk-headless"] }] },
      "topologyKey": "kubernetes.io/hostname"
    }]
  }
}
```

The post closes with a backlog — *"support for rolling updates, better integration with node
upgrades, and using fast local storage"* — a design principle, *"we avoided implementing
StatefulSets in a way that relied on hidden mechanisms or inaccessible features. Anyone can write a
controller that works similarly to StatefulSets. We call this 'making it forkable'"* — and a
forecast that per-application operators would arrive alongside it.

**As it runs now** — start with the rename, because the result is total. Grep the pin for `PetSet`,
case-insensitively, across every page under `docs/`: **zero occurrences**. Not a deprecation note,
not a migration page, not a glossary stub, not a redirect. The name the feature shipped under in
v1.3 and v1.4 is absent from the corpus. So is the word the post coined for its design principle:
`forkable` has zero occurrences too.

What the corpus does record is the API version, and it records it as a removal rather than a
rename:

> The **apps/v1beta1** and **apps/v1beta2** API versions of StatefulSet are no longer served as of
> v1.16. [...] `spec.updateStrategy.type` now defaults to `RollingUpdate` (the default in
> `apps/v1beta1` was `OnDelete`)
>
> — `docs/reference/using-api/deprecation-guide.md:351-359`

That second clause is the post's own backlog item arriving: *"support for rolling updates"* did not
merely ship, it became the default, and the default change is filed as a migration hazard for
anybody moving off the API version the post announced.

Now the manifest. Every object in the post's four-line creation output has been renamed or deleted,
and the current example — `content/en/examples/application/zookeeper/zookeeper.yaml` — reads:

| the post's object | at the pin |
|---|---|
| `zk-headless`, one headless Service | `zk-hs` headless **plus** `zk-cs`, a second Service for clients |
| `zk-config`, a ConfigMap | gone; configuration is `start-zookeeper` command-line arguments in the container's `command` |
| `zk-budget`, `minAvailable: 2` | `zk-pdb`, `apiVersion: policy/v1`, `maxUnavailable: 1` |
| `statefulset zk` | `apps/v1`, with `updateStrategy: RollingUpdate` and `podManagementPolicy: OrderedReady` written out explicitly |

`zk-headless` and `zk-config` have zero occurrences at the pin. `zk-budget` has **one**, and it is
the finding this exercise is built on:

> You cannot drain the third node because evicting `zk-2` would violate `zk-budget`. However, the
> node will remain cordoned.
>
> — `docs/tutorials/stateful-application/zookeeper.md:1046`

Every other mention in that file — the overview at `:87`, the instruction at `:906`, the command
`kubectl get pdb zk-pdb`, the sample output at `:917` — says `zk-pdb`. The manifest creates `zk-pdb`.
One sentence, in the middle of the maintenance walkthrough, still names the object from the post.
A reader following the tutorial and hitting that line has nothing to check it against, because the
object it names does not exist in their cluster.

The anti-affinity rule was wrong when the post published it, in a way worth being exact about. The
field name the post prints, `requiredDuringSchedulingRequiredDuringExecution`, has **zero**
occurrences at the pin, and so does the fragment `RequiredDuringExecution` on its own. What the
current manifest uses is a different word in the second half:

> ```yaml
>       affinity:
>         podAntiAffinity:
>           requiredDuringSchedulingIgnoredDuringExecution:
>             - labelSelector:
>                 matchExpressions:
>                   - key: "app"
>                     operator: In
>                     values:
>                     - zk
>               topologyKey: "kubernetes.io/hostname"
> ```
>
> — `content/en/examples/application/zookeeper/zookeeper.yaml`, and explained at
> `docs/tutorials/stateful-application/zookeeper.md:868-880`

Two differences, not one. `Required` became `Ignored` — the scheduler enforces the rule when
placing a pod and does not evict a pod whose placement later stops satisfying it. And the selector's
value changed from `zk-headless` to `zk`, because the post was matching on the *Service* name while
the pods are labelled `app: zk`. The post's rule, transcribed literally into a v1.5 cluster, would
have selected nothing even if the field name had been accepted.

Two of the post's sample outputs also date the tutorial precisely. `zookeeper.md:538` prints a
ZooKeeper log line stamped `2016-12-06`, and `:1058` prints a ZNode `ctime` of
`Wed Dec 07 00:08:59 UTC 2016`. Both predate the post itself. The prose around them has been
revised repeatedly — `policy/v1`, `apps/v1`, the new Service, the corrected affinity field — and the
captured output has not been regenerated since the fortnight before publication.

The disruption budget's own sample shows the change of idiom:

> ```
> NAME      MIN-AVAILABLE   MAX-UNAVAILABLE   ALLOWED-DISRUPTIONS   AGE
> zk-pdb    N/A             1                 1
> ```
>
> — `docs/tutorials/stateful-application/zookeeper.md:916-918`

The post set `minAvailable: 2` and read the guarantee off the left-hand column. The pin sets
`maxUnavailable: 1` and that column now reads `N/A`. Both express "one member may be down at a
time" for a three-member ensemble, and they diverge the moment you change `replicas` — which is the
substantive difference, not a cosmetic one. Note also that the header has four columns and the row
has three values.

Finally, the post's forecast about operators. `operator` as the post means it is now the pattern
documented at `docs/concepts/extend-kubernetes/operator/`, built on CustomResourceDefinitions rather
than on the *"forkable"* argument the post made — the post's claim was that anyone could write a
controller *like* StatefulSet by reading its source; what shipped was a mechanism for registering
your own kinds, which is a stronger answer to the same question and does not require the reading.

**The diff, and why** — the post is right about almost everything it claims and wrong about almost
everything it prints, and both facts follow from what a rename actually is.

Take the erasure first, because it looks like carelessness and is not. `PetSet` appearing zero times
is a *decision*: the project chose not to carry the old name forward in prose at all. Compare what
it did carry forward — `apps/v1beta1`, in a deprecation guide, with the default-value change spelled
out, because an *API version* is something a stored object can be written in and a client can
request. A **kind name** in a pre-1.0-style beta group is not. There was no conversion to write,
because there was nothing to convert *to* while remaining the same object: `PetSet` and
`StatefulSet` were different resources in the same group, and the migration was delete-and-recreate,
performed by whoever ran the cluster in 2016, once. Ten years later there is nobody left to inform.
So the documentation is not hiding the rename; it has finished with it. This is the honest shape of
a successful rename — no migration note, no compatibility shim, and no evidence.

The post's own sentence, read carefully, already says so: *"There were no major changes to the API
Object, other than the community selected name."* The name was the change. The reason there is
nothing to migrate is that the only thing that moved is the thing no stored object can preserve.

Now hold that against `zk-budget` surviving in one line of the tutorial. Same feature, same
documentation, a rename two orders of magnitude smaller — one object in one example — and it was not
completed. This is the failure mode that actually bites readers, and it is worth naming as a general
property rather than as a typo: **a rename is only as complete as the mechanism that enforces it.**
The `PetSet` rename was enforced by the API server, which will not serve a kind that does not exist;
every stale reference broke loudly and immediately in 2016 and was fixed. The `zk-budget` rename was
enforced by nothing — prose does not fail to compile — so one sentence kept the old name and has
kept it through every subsequent revision of the surrounding page. The corpus's most reliable text
is the text something checks.

The same reading explains the affinity block. `requiredDuringSchedulingRequiredDuringExecution` was
never a field the API server accepted; it was the name of a *planned* enforcement mode that appeared
in design discussion and never shipped, and the post printed it inside a JSON blob in an annotation,
where nothing validated it. An annotation's value is an opaque string. A wrong field name in
`spec.affinity` is rejected at admission; a wrong field name inside an annotation is stored
faithfully and ignored. So the post's manifest could carry a non-existent field and a selector
matching a label nothing had, and still apply cleanly. That is not a mistake the post's authors
were careless to make — it is the mistake the mechanism of the day made available, and it is exactly
why affinity was promoted out of annotations into typed fields. [10](10-dynamic-provisioning-and-storage-in-kubernetes.md)
watched the same promotion happen to storage classes and found the annotation still outranking its
replacement; here the annotation form is simply gone, and the field is checked.

What survives untouched, then, is the part of the post that was never printed: the four semantic
properties. Ordered deployment, ordered termination, ordinal-stable hostnames, and storage that
outlives the pod are all still true, all still the reason to reach for a StatefulSet, and all still
described in almost the post's words. Its four adoption questions have aged best of anything in this
year's fifteen posts — *"Is scaling your storage application a problem that you actually have?"*
needs no revision at all. The prose was right; the YAML was a snapshot. That asymmetry is the
recurring lesson of this whole walk, and this post is the cleanest instance of it in 2016.

The ladders below are where the four properties have since been qualified, and every one of them
adds an "unless".

**The ladder** — four gates, each amending one of the post's four claims, plus two that arrived at
the pin itself.

The post's *"persistent stable storage"* survives the StatefulSet's deletion — that is the
demonstration the post ends its ZooKeeper walk on. This gate makes that conditional:

## StatefulSetAutoDeletePVC
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.23 – v1.26 |
| beta | `true` | — | v1.27 – v1.31 |
| stable | `true` | — | v1.32 –  |

Stable and on. It does not change the default behaviour — it adds
`spec.persistentVolumeClaimRetentionPolicy`, whose `whenDeleted` and `whenScaled` fields both
default to `Retain`. So the post's demonstration still works, and now works *because a field says
so* rather than because there was no alternative. A reader who sets `whenDeleted: Delete` gets the
opposite of the post's closing paragraph, from the same manifest.

The post's *"ordered deployment"* during an update:

## MaxUnavailableStatefulSet
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.24 – v1.34 |
| beta | `true` | — | v1.35.0 – v1.35.3 |
| beta | `false` | — | v1.35.4 – v1.36 |
| beta | `true` | — | v1.37 –  |

Read the version strings, because this ladder is the only one in this year's fifteen exercises that
uses **patch-level** granularity. Eleven releases at alpha, then beta defaulting on at v1.35.0 —
and off again at v1.35.**4**, a patch release, then on again at v1.37. Something shipped enabled,
was disabled four patches later, and was re-enabled a release after that. Whatever the reason, the
observable consequence for a reader is sharp: two clusters both running "v1.35" can disagree about
whether this feature is on, and the minor version does not tell them apart.

The post's *ordinals*, on which its entire ZooKeeper identity scheme rests — `myid` is the ordinal
plus one:

## StatefulSetStartOrdinal
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.26 – v1.26 |
| beta | `true` | — | v1.27 – v1.30 |
| stable | `true` | — | v1.31 –  |

`spec.ordinals.start` moves the first ordinal off zero. The post's arithmetic — *"populated by
adding one to the ordinal extracted from the Pods' hostnames"* — is unchanged in the tutorial and
silently assumes a start of `0`. It is correct at the default and wrong at any other value, and
nothing in the tutorial says which assumption it is making.

Two gates arrived at or just before the pinned release and are worth transcribing because a reader
checking this post's claims today is checking them against these:

## StatefulSetRecreateStrategy
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.37 –  |

## StaleControllerConsistencyStatefulSet
| stage | default | locked | releases |
|---|---|---|---|
| beta | `true` | — | v1.36 –  |

The first is one release old and off. The second enters the ladder at **beta** with no alpha stage —
the same unusual shape [13](13-container-runtime-interface-cri-in-kubernetes.md) found in
`StreamingProxyRedirects`.

One gate from the same family has been through the whole ladder and out:

## StatefulSetMinReadySeconds
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.22 – v1.22 |
| beta | `true` | — | v1.23 – v1.24 |
| stable | `true` | — | v1.25 – v1.26 |

`removed: true` at file level. The field it gated, `spec.minReadySeconds`, is permanent; the gate is
gone. This is the ordinary end state, and it is the one none of the post's four properties has a gate
for — because they were never gated at all.

**Topology** — [`workhorse`](../../strands/lab-topologies.md#workhorse), fresh. Three nodes: a
control plane and two workers, which is what the anti-affinity and drain steps need. Bring all three
guests up with [the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=workhorse`, install Kubernetes on each with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), bring the
cluster up as usual, and confirm three nodes with two of them schedulable before starting.

The post's ZooKeeper ensemble is deliberately **not** what runs here. It needs three schedulable
nodes for its anti-affinity rule and four for the maintenance walk the tutorial describes, which is
past what this curriculum provisions; and quorum behaviour is ZooKeeper's subject, not the
StatefulSet's. What runs instead is a two-replica StatefulSet of `agnhost` containers with local
PersistentVolumes, which exhibits all four of the post's claimed properties and nothing else. Where
a step cannot show you something on two workers, it says so.

**Do**

1. Establish the erasure, so the rest of the exercise has a baseline:

   ```sh
   kubectl api-resources | grep -i -e petset -e statefulset
   kubectl explain petset 2>&1 | head -3
   kubectl explain statefulset.spec.ordinals
   kubectl explain statefulset.spec.persistentVolumeClaimRetentionPolicy
   ```

   One kind, three short names, and two fields the post did not have. The `explain` output for the
   two new fields is the API server's own account of the two gates above; read what it says the
   defaults are before step 7 relies on them.

2. Provide storage the post's demonstration needs, one volume per worker. On each worker:

   ```sh
   sudo mkdir -p /mnt/sts && sudo chmod 777 /mnt/sts
   ```

   then from the control plane, with `W1` and `W2` set to your two worker names:

   ```sh
   kubectl apply -f - <<EOF
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: local-sts
   provisioner: kubernetes.io/no-provisioner
   volumeBindingMode: WaitForFirstConsumer
   EOF
   for n in $W1 $W2; do
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: pv-$n
   spec:
     capacity: { storage: 1Gi }
     accessModes: ["ReadWriteOnce"]
     persistentVolumeReclaimPolicy: Retain
     storageClassName: local-sts
     local: { path: /mnt/sts }
     nodeAffinity:
       required:
         nodeSelectorTerms:
           - matchExpressions:
               - { key: kubernetes.io/hostname, operator: In, values: ["$n"] }
   EOF
   done
   ```

3. Create the StatefulSet, carrying the post's anti-affinity rule with both of its errors corrected,
   and watch the ordering claim:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Service
   metadata: { name: sts-hs, labels: { app: sts } }
   spec:
     clusterIP: None
     selector: { app: sts }
     ports: [{ port: 8080, name: http }]
   ---
   apiVersion: apps/v1
   kind: StatefulSet
   metadata: { name: sts }
   spec:
     serviceName: sts-hs
     replicas: 2
     podManagementPolicy: OrderedReady
     selector: { matchLabels: { app: sts } }
     template:
       metadata: { labels: { app: sts } }
       spec:
         affinity:
           podAntiAffinity:
             requiredDuringSchedulingIgnoredDuringExecution:
               - labelSelector:
                   matchExpressions:
                     - { key: app, operator: In, values: ["sts"] }
                 topologyKey: kubernetes.io/hostname
         containers:
           - name: c
             image: registry.k8s.io/e2e-test-images/agnhost:2.53
             args: ["netexec", "--http-port=8080"]
             readinessProbe:
               httpGet: { path: /healthz, port: 8080 }
               initialDelaySeconds: 5
             volumeMounts: [{ name: data, mountPath: /data }]
     volumeClaimTemplates:
       - metadata: { name: data }
         spec:
           accessModes: ["ReadWriteOnce"]
           storageClassName: local-sts
           resources: { requests: { storage: 1Gi } }
   EOF
   kubectl get pods -w -l app=sts
   ```

   Compare what scrolls past with the post's `kubectl get -w -l app=zk` transcript. `sts-1` must not
   appear before `sts-0` is Ready. Say which field in the manifest above is making that true, and
   what the pin says happens if you change it.

4. Check the post's *"unique network names"* claim against the two mechanisms that produce it:

   ```sh
   for i in 0 1; do kubectl exec sts-$i -- hostname; done
   for i in 0 1; do kubectl exec sts-$i -- hostname -f; done
   kubectl run dnsprobe --rm -it --restart=Never --image=registry.k8s.io/e2e-test-images/agnhost:2.53 \
     -- nslookup sts-hs.default.svc.cluster.local
   ```

   The FQDNs should match the post's shape exactly, ten years on. The last command is the one the
   post does not run: it asks the headless Service for its membership. Report how many A records
   come back and in what order, and say which of the post's four properties that ordering is *not*
   a guarantee of.

5. Prove the ordinal is the identity, by writing it to disk the way the post's `myid` files work:

   ```sh
   for i in 0 1; do kubectl exec sts-$i -- sh -c 'echo $((${HOSTNAME##*-}+1)) > /data/myid'; done
   for i in 0 1; do echo "myid sts-$i"; kubectl exec sts-$i -- cat /data/myid; done
   ```

   That arithmetic is the post's, verbatim in intent. Now read `kubectl explain
   statefulset.spec.ordinals.start` again and state what this loop would write if `start` were `1`,
   and whether the tutorial's version of it says anything about that.

6. Test the post's *"at most one pod per index"* semantics — the thing v1.5 actually added — by
   trying to violate it:

   ```sh
   kubectl get pods -l app=sts -o wide
   kubectl delete pod sts-0 --wait=false
   kubectl get pods -l app=sts -w
   ```

   The replacement takes the same name, the same PVC and the same node. Explain why it must take the
   same node here, in terms of the PV you created in step 2 rather than in terms of the StatefulSet,
   and say which of the two would have pinned it if the other had not.

7. Run the post's closing demonstration, and then run it again with the field that reverses it:

   ```sh
   kubectl exec sts-0 -- sh -c 'echo hello-from-the-post > /data/hello'
   kubectl delete statefulset sts
   kubectl get pvc -l app=sts
   ```

   The PVCs survive. Re-create the StatefulSet from step 3 and read the file back:

   ```sh
   kubectl exec sts-0 -- cat /data/hello
   ```

   That is the post's *"the ensemble still serves the data"*, reproduced. Now make the same manifest
   behave the opposite way:

   ```sh
   kubectl patch statefulset sts --type=merge \
     -p '{"spec":{"persistentVolumeClaimRetentionPolicy":{"whenDeleted":"Delete","whenScaled":"Retain"}}}'
   kubectl get statefulset sts -o jsonpath='{.spec.persistentVolumeClaimRetentionPolicy}{"\n"}'
   kubectl get pvc -l app=sts -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.ownerReferences[*].kind}{"\n"}{end}'
   ```

   Do not delete it yet. The `ownerReferences` on the PVCs are the whole mechanism; say what changed
   on them and what will therefore happen when the StatefulSet goes. Then decide whether the post's
   final paragraph is still a property of StatefulSets or now a property of one field's default.

8. Reproduce the post's maintenance scenario as far as two workers allow, and find where it stops:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: policy/v1
   kind: PodDisruptionBudget
   metadata: { name: sts-pdb }
   spec:
     maxUnavailable: 1
     selector: { matchLabels: { app: sts } }
   EOF
   kubectl get pdb sts-pdb
   ```

   Compare that output's columns against the post's `MIN-AVAILABLE 2 / ALLOWED-DISRUPTIONS 1` and
   against the pin's `N/A / 1 / 1` at `zookeeper.md:917`. Then drain one worker and try the other:

   ```sh
   kubectl drain $W1 --ignore-daemonsets --delete-emptydir-data --timeout=120s
   kubectl get pods -l app=sts -o wide
   kubectl drain $W2 --ignore-daemonsets --delete-emptydir-data --timeout=60s
   ```

   The second drain fails, with the message the tutorial quotes. Note carefully that with two
   replicas on two workers the *first* drain also cannot fully succeed in the way the post's does —
   say why, and what a third schedulable node would have changed.

9. Uncordon and settle, then look at the two errors in the post's affinity block by reintroducing
   them deliberately — the second one first, because it fails quietly:

   ```sh
   kubectl uncordon $W1 $W2
   kubectl patch statefulset sts --type=json -p='[{"op":"replace",
     "path":"/spec/template/spec/affinity/podAntiAffinity/requiredDuringSchedulingIgnoredDuringExecution/0/labelSelector/matchExpressions/0/values",
     "value":["sts-hs"]}]'
   kubectl rollout status statefulset/sts --timeout=180s
   kubectl get pods -l app=sts -o wide
   ```

   That is the post's selector — matching the Service's name instead of the pods' label. The
   StatefulSet accepts it and the rule now constrains nothing. Confirm from the node column that the
   pods are no longer being kept apart by it, then say what would still be keeping them apart in
   this particular cluster.

10. Now the first error, which fails loudly, and that difference is the exercise's point:

    ```sh
    kubectl patch statefulset sts --type=json -p='[{"op":"move",
      "from":"/spec/template/spec/affinity/podAntiAffinity/requiredDuringSchedulingIgnoredDuringExecution",
      "path":"/spec/template/spec/affinity/podAntiAffinity/requiredDuringSchedulingRequiredDuringExecution"}]' ; echo "exit=$?"
    kubectl annotate statefulset sts \
      'scheduler.alpha.kubernetes.io/affinity={"podAntiAffinity":{"requiredDuringSchedulingRequiredDuringExecution":[{"topologyKey":"kubernetes.io/hostname"}]}}'
    kubectl get statefulset sts -o jsonpath='{.metadata.annotations}{"\n"}'
    ```

    The patch is refused and names the field. The annotation is accepted, stored verbatim, and does
    nothing at all. Put the two results side by side and state the general rule they demonstrate
    about where a wrong name is caught — then apply that rule to `zk-budget` surviving in one line of
    the pin's tutorial.

**Expect**

```sh
kubectl get statefulset sts -o wide
kubectl get pods -l app=sts -o wide
kubectl get pvc -l app=sts
kubectl get pdb sts-pdb
kubectl api-resources | grep -ci petset
```

Two pods with ordinal names on two different workers, two bound PVCs, a budget allowing one
disruption, and a zero from the last command. Every property the post claims should be visible in
that output; nothing the post *prints* should be.

By the end you should be able to say which of the post's four promises are still enforced by the
controller, which are now defaults of a field you can change, and why the project owed nobody a
migration note for `PetSet` while owing its own tutorial a one-line fix it has not made.

**Read on** — the pin's
[StatefulSet concept page](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
has a *Limitations* section the post's disclaimer (*"we don't claim that the feature is 100%
complete"*) grew into. Read it and answer: which single limitation on that list would have made the
post's ZooKeeper example impossible to write as a StatefulSet at all if it had not been solved, and
is it listed as solved or as still standing?

**Teardown** — `kubectl delete statefulset sts; kubectl delete svc sts-hs; kubectl delete pdb
sts-pdb; kubectl delete pvc -l app=sts; kubectl delete pv pv-$W1 pv-$W2; kubectl delete sc
local-sts` — and note which of those deletions blocks on another, since step 7 changed the ownership
that decides it. Then [the teardown step](../../strands/lab-topologies.md#teardown).
