<a id="building-highly-available-applications-using-kubernetes-new-multi-zone-clusters-aka-ubernetes-lite"></a>
# The label in this post is still served, the name is gone, and the spreading it calls automatic is not a guarantee

**Post** — [Building highly available applications using Kubernetes new multi-zone clusters (a.k.a. 'Ubernetes Lite')](https://kubernetes.io/blog/2016/03/building-highly-available-applications-using-kubernetes-new-multi-zone-clusters-aka-ubernetes-lite/),
2016-03-29, Kubernetes v1.2 — the third post in that release's five-day series.

**As written** — a single cluster can now span failure zones, and it costs you nothing:

> Multi-zone clusters are deliberately simple, and by design, very easy to use — no Kubernetes API
> changes were required, and no application changes either. You simply deploy your existing
> Kubernetes application into a new-style multi-zone cluster, and your application automatically
> becomes resilient to zone failures.

The mechanism is labels the system adds for you. "Today, when nodes are started, labels are added
to every node in the system. With Ubernetes Lite, the system has been extended to also add
information about the zone it's being run in" — `failure-domain.beta.kubernetes.io/zone` and
`failure-domain.beta.kubernetes.io/region`, visible in `kubectl get nodes --show-labels` alongside
`beta.kubernetes.io/instance-type`. Three moving parts read them:

- the scheduler, "via `SelectorSpreadPriority`", makes "a best-effort placement to spread across
  zones as well";
- the `PersistentVolumeLabel` admission controller "automatically adds zone labels" to
  PersistentVolumes as they are created;
- the scheduler again, "via the `VolumeZonePredicate` predicate", keeps a pod claiming a volume in
  that volume's zone, "as volumes cannot be attached across zones."

You build the cluster with `kube-up`, one zone at a time:

```
curl -sS https://get.k8s.io | MULTIZONE=true KUBERNETES_PROVIDER=gce
KUBE_GCE_ZONE=us-central1-a NUM_NODES=3 bash
```

```
KUBE_USE_EXISTING_MASTER=true MULTIZONE=true KUBERNETES_PROVIDER=gce
KUBE_GCE_ZONE=us-central1-b NUM_NODES=3 kubernetes/cluster/kube-up.sh
```

Then `kubectl create -f guestbook-go/` — a ReplicationController of size 3 — and "You're done! Your
application is now spread across all 3 zones," proved with
`kubectl describe pod -l app=guestbook | grep Node`.

Two forecasts sit in the prose. Multi-zone is "the first step in a broader effort to allow
federating multiple Kubernetes clusters together (sometimes referred to by the affectionate
nickname 'Ubernetes')", with a SIG, a Slack channel and a weekly hangout. And: "In a future
iteration of Ubernetes Lite, we'll support a HA control plane, where the master components are
replicated across zones."

**As it runs now** — four fates, and only one of them is a straight rename:

1. **The installer is gone, and the pinned documentation has not noticed.** `verify-kubectl.md` at
   the pin still says a kubeconfig "is created automatically when you create a cluster using
   [kube-up.sh]", linking `kubernetes/kubernetes/blob/master/cluster/kube-up.sh`. Step 1 has you
   resolve that link yourself, because this tree cannot: the pin is a snapshot of the *website*, and
   what it says about another repository is a claim, not evidence.
2. **The labels still resolve, and nothing sets them.** `failure-domain.beta.kubernetes.io/zone` is
   in the pinned label reference under a heading that reads `(deprecated)` — "Starting in v1.17,
   this label is deprecated in favor of `topology.kubernetes.io/zone`" — deprecated for twenty
   releases and still documented, still accepted. But on this lab there is no cloud provider, so
   neither key appears on any node: the pin says of the new one, "This will be set only if you are
   using a cloud provider. However, you can consider setting this on nodes if it makes sense in
   your topology." The post's "labels are added to every node in the system" was never a property
   of Kubernetes; it was a property of `kube-up` on GCE.
3. **The scheduler plugin was removed, and its replacement is on by default.**
   `SelectorSpreadPriority` is gone; the pin's scheduler-config reference records the break at the
   config API boundary — "The scheduler plugin `SelectorSpread` is removed, instead, use the
   `PodTopologySpread` plugin (enabled by default) to achieve similar behavior." *Similar* is doing
   real work in that sentence, and step 5 is where it stops being similar.
4. **The admission controller is not in the reference at all, and two other pages still describe
   it.** `PersistentVolumeLabel` appears nowhere in the pin's admission-controllers reference, while
   `labels-annotations-taints/_index.md` explains what to do "If `PersistentVolumeLabel` does not
   support automatic labeling of your PersistentVolumes" and kubeadm's `implementation-details.md`
   links to `admission-controllers/#persistentvolumelabel` — an anchor on a page that no longer has
   it. Step 6 follows that link. `VolumeZonePredicate`, meanwhile, is still there under a shorter
   name: `VolumeZone`, "Checks that volumes requested satisfy any zone requirements they have."

**The diff, and why** — the feature survived; the sentence promising it was free did not.

The rename is the least of it, though it is worth counting: the *key* went
`failure-domain.beta.kubernetes.io/zone` → `topology.kubernetes.io/zone`, the *plugin* went
`SelectorSpreadPriority` → `PodTopologySpread`, the *predicate* went `VolumeZonePredicate` →
`VolumeZone`, and the *feature's name* — "Ubernetes Lite" — went nowhere at all. What changed
underneath is that best-effort spreading became a **field you write**, with a skew you choose and a
say in whether violating it is an error:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.16 – v1.17 |
| beta | `true` | — | v1.18 – v1.18 |
| stable | `true` | — | v1.19 – v1.21 |

`EvenPodsSpread`, the gate for `pod.spec.topologySpreadConstraints`, and it declares `removed: true`
— declared in the file, not inferred from the terminal `toVersion`. One release of beta, which is
the shortest beta anywhere in this year's exercises. That gate gave you the field. A second one
made the field's behaviour the default, and it is the one that actually replaces the post's
`SelectorSpreadPriority`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.19 – v1.19 |
| beta | `true` | — | v1.20 – v1.23 |
| stable | `true` | — | v1.24 – v1.25 |

`DefaultPodTopologySpread`, also `removed: true`. Read the two together and the sequence is legible:
v1.19 shipped the explicit field as stable and the implicit default as alpha *in the same release*,
so for five releases a cluster had the new field and the old plugin's defaults. The gates are gone
because both won.

What they defaulted to is the payload. Absent any configuration, the pin says kube-scheduler
"acts as if you specified the following default topology constraints" — `maxSkew: 3` on
`kubernetes.io/hostname` and `maxSkew: 5` on `topology.kubernetes.io/zone`, both
`whenUnsatisfiable: ScheduleAnyway`. A skew of five across zones is not a spreading policy for a
three-replica app; it is a policy that any placement satisfies. So the post's promise —
"automatically becomes resilient to zone failures" — is now delivered by a default that will
cheerfully put all three replicas in one zone, and the thing that usually saves you is the
*hostname* row, not the zone row. Step 5 separates them by giving two nodes the same zone.

The pin also names the failure mode this creates on a cluster like the lab's: "The
`PodTopologySpread` plugin does not score the nodes that don't have the topology keys specified in
the spreading constraints. This might result in a different default behavior compared to the legacy
`SelectorSpread` plugin when using the default topology constraints… If your nodes are not expected
to have **both** `kubernetes.io/hostname` and `topology.kubernetes.io/zone` labels set, define your
own constraints instead of using the Kubernetes defaults." An unlabelled node is not spread across;
it is not scored. Step 2 is a cluster in exactly that state.

Of the two forecasts, one landed and one did not, and the post cannot tell them apart. The HA
control plane arrived — this exercise runs on three stacked control planes, and
[the leader election exercise](01-simple-leader-election-with-kubernetes.md) is what makes that
survivable. Federation did not. Searched at the pin, the word "Ubernetes" appears in **zero** files
under `content/en/docs`, and the word "federation" appears in exactly **one**: the contributor style
guide, as an example of a sentence that should not begin "The new Federation feature provides…".
The only trace left of the broader effort is an instruction on how not to describe it. That is the
shape to notice — the post is not describing an old world, it is describing a future, and the half
that survived is the half it called *Lite*.

Release facts and the pressure behind each one are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

**Topology** — [`ha`](../../strands/lab-topologies.md#ha): three untainted nodes, which is the
smallest cluster on which "spread across zones" can be wrong. If
[the leader election exercise](01-simple-leader-election-with-kubernetes.md) left the guests up,
reuse them. Otherwise bring them up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting `topology=ha`,
install Kubernetes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), then
`ssh zain@10.10.10.150`.

**Do**

1. Settle the installer without running it. **Do not pipe the post's first command to `bash`** —
   it builds a billable cloud cluster, and that is not what is being tested here.

   ```sh
   curl -sSI https://get.k8s.io | head -3
   curl -sSI https://github.com/kubernetes/kubernetes/blob/master/cluster/kube-up.sh | head -3
   ```

   The second URL is the one the pinned docs hand a reader today. Record both statuses.

2. Look for the labels the post says appear by themselves:

   ```sh
   kubectl get nodes --show-labels
   kubectl get nodes -o json | grep -c 'failure-domain.beta.kubernetes.io/zone'
   kubectl get nodes -o json | grep -c 'topology.kubernetes.io/zone'
   kubectl get nodes -o json | grep -o 'node.kubernetes.io/instance-type[^,"]*'
   ```

3. Build the topology by hand, deliberately lopsided — two nodes in one zone, one in another,
   which is the case the post warns about in passing ("if the zones in your cluster are
   heterogenous … you may not be able to achieve even spreading"):

   ```sh
   N=($(kubectl get nodes -o jsonpath='{.items[*].metadata.name}'))
   kubectl label node ${N[0]} topology.kubernetes.io/zone=lab-a
   kubectl label node ${N[1]} topology.kubernetes.io/zone=lab-a
   kubectl label node ${N[2]} topology.kubernetes.io/zone=lab-b
   kubectl label node ${N[2]} failure-domain.beta.kubernetes.io/zone=lab-b
   kubectl get nodes -L topology.kubernetes.io/zone,failure-domain.beta.kubernetes.io/zone
   ```

   The fourth command writes the post's deprecated key on one node on purpose. Note whether the API
   server complains, warns, or says nothing.

4. Deploy the post's shape — a ReplicationController of three — and ask where it landed, by zone
   rather than by node:

   ```sh
   kubectl create -f - <<'YAML'
   apiVersion: v1
   kind: ReplicationController
   metadata:
     name: guestbook
   spec:
     replicas: 3
     selector: {app: guestbook}
     template:
       metadata:
         labels: {app: guestbook}
       spec:
         containers:
         - name: web
           image: registry.k8s.io/pause:3.10
   YAML
   kubectl get pods -l app=guestbook -o custom-columns=POD:.metadata.name,NODE:.spec.nodeName
   for n in $(kubectl get pods -l app=guestbook -o jsonpath='{.items[*].spec.nodeName}'); do
     kubectl get node $n -o jsonpath='{.metadata.labels.topology\.kubernetes\.io/zone}{"\n"}'
   done | sort | uniq -c
   ```

5. **Ask for the guarantee the post says you already have.** Scale to six, then declare the
   constraint explicitly and watch what the default was not doing:

   ```sh
   kubectl scale rc guestbook --replicas=6
   kubectl get pods -l app=guestbook -o jsonpath='{range .items[*]}{.spec.nodeName}{"\n"}{end}' | sort | uniq -c
   kubectl create -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata:
     name: strict
     labels: {app: guestbook}
   spec:
     topologySpreadConstraints:
     - maxSkew: 1
       topologyKey: topology.kubernetes.io/zone
       whenUnsatisfiable: DoNotSchedule
       labelSelector:
         matchLabels: {app: guestbook}
     containers:
     - name: web
       image: registry.k8s.io/pause:3.10
   YAML
   kubectl get pod strict
   kubectl describe pod strict | tail -6
   ```

6. Follow the documentation's own dead end. In the pinned tree, `PersistentVolumeLabel` is
   described in the label reference and linked from kubeadm's implementation details, and is absent
   from the admission-controllers reference it is linked into. Check what the API server on this
   cluster actually enables:

   ```sh
   kubectl -n kube-system get pod -l component=kube-apiserver \
     -o jsonpath='{.items[0].spec.containers[0].command}' | tr ',' '\n' | grep -i admission
   ```

   Then open <https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#persistentvolumelabel>
   and record what you land on. One of the three pages is right; say which, and how you decided.

7. Do the storage half the way it is done now — the zone as a field on the volume rather than a
   label an admission controller guesses:

   ```sh
   kubectl create -f - <<'YAML'
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: zoned
   spec:
     capacity: {storage: 1Gi}
     accessModes: [ReadWriteOnce]
     persistentVolumeReclaimPolicy: Delete
     storageClassName: manual
     local: {path: /tmp/zoned}
     nodeAffinity:
       required:
         nodeSelectorTerms:
         - matchExpressions:
           - key: topology.kubernetes.io/zone
             operator: In
             values: [lab-b]
   YAML
   kubectl create -f - <<'YAML'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: zoned
   spec:
     accessModes: [ReadWriteOnce]
     storageClassName: manual
     resources: {requests: {storage: 1Gi}}
   YAML
   kubectl run pinned --image=registry.k8s.io/pause:3.10 --restart=Never --overrides='
   {"spec":{"nodeSelector":{"topology.kubernetes.io/zone":"lab-a"},
    "volumes":[{"name":"v","persistentVolumeClaim":{"claimName":"zoned"}}],
    "containers":[{"name":"pinned","image":"registry.k8s.io/pause:3.10",
      "volumeMounts":[{"name":"v","mountPath":"/data"}]}]}}'
   kubectl describe pod pinned | tail -8
   ```

**Expect** — step 1: whatever the two statuses are, write them down before reading on; the point of
the step is that this repository could not answer it for you and the pinned docs asserted it anyway.

Step 2 counts **zero** for both zone keys. `instance-type` is absent too. Nothing in the post's
"Nodes are labeled" section describes this cluster, and no version of Kubernetes ever would have —
the labels came from the cloud provider, through `kube-up`.

Step 3 is accepted silently on both keys, including the one the reference marks deprecated: a
deprecated label is a *documented convention*, not a validated field, so there is nothing in the API
server that could object.

Step 4 lands one pod per node, hence two in `lab-a` and one in `lab-b`. This looks like the post
being right and is not: the placement came from the `kubernetes.io/hostname` default row and the
scheduler's own node balancing, not from zone spreading. Nothing zone-shaped happened.

Step 5 is the exercise. At six replicas you get roughly two per node — four in `lab-a`, two in
`lab-b`, a zone skew of two — and the default constraint's `maxSkew: 5` was satisfied throughout, so
the scheduler never had an opinion. Then `strict` goes **Pending**, and `describe` names the reason
in the scheduler's own words: `didn't satisfy pod topology spread constraints`. Same cluster, same
pods, same labels; the difference is that one of them asked. Note also *which* zone `strict` would
have had to land in, and why one of the two zones has no capacity problem at all.

Step 6: kubeadm enables `NodeRestriction` and nothing else on the command line, so
`PersistentVolumeLabel` is not running here whatever its status upstream — and the doc link resolves
to the top of the admission-controllers page with no matching anchor, because the section is gone.
Two pinned pages describe a controller the pinned reference does not list.

Step 7: `pinned` stays **Pending** with an event containing
`node(s) had volume node affinity conflict`. That is `VolumeZonePredicate`'s job, done by the
successor plugin `VolumeZone` against a field on the PersistentVolume — the same guarantee the post
describes, moved out of an admission controller and into the object, where you can read it.

**Read on** — [KEP-895, *Pod Topology Spread*](https://github.com/kubernetes/enhancements/tree/master/keps/sig-scheduling/895-pod-topology-spread):
find its stated reason for `whenUnsatisfiable: ScheduleAnyway` being an option at all, and say what
that reason implies about the built-in `maxSkew: 5` default. Then find whether the KEP claims to
replace `SelectorSpreadPriority` or to sit beside it — the answer dates the removal that the
scheduler-config reference records at the `v1beta3 → v1` boundary.

**Teardown** — `kubectl delete rc guestbook; kubectl delete pod strict pinned; kubectl delete pvc
zoned; kubectl delete pv zoned`, and remove the labels you invented:
`kubectl label nodes --all topology.kubernetes.io/zone- failure-domain.beta.kubernetes.io/zone-`.
The labels are the only state this exercise added, so the cluster is reusable as it stands — or take
the topology down with [teardown](../../strands/lab-topologies.md#teardown), since every exercise in
this tree names the topology it wants.
