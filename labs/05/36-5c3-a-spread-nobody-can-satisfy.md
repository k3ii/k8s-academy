<a id="5c3-a-spread-nobody-can-satisfy"></a>
# 5.C3 — unschedulable for a reason that is not scarcity, and says so

**Claim** — a `topologySpreadConstraints` that no node can satisfy produces a pod stuck `Unschedulable` on a cluster with plenty of free capacity, and the event message distinguishes it from resource starvation without any further investigation; the same is true of a pod anti-affinity that cannot be met. The diagnostic skill is reading one sentence, and the drill is proving you can.

**Rests on** — [the rejection strings](06-three-rejections-three-plugins.md) and [the backlog drill](22-5c1-an-unschedulable-backlog.md), where every cause was ultimately about resources. This is [drill 5.C3](../../phases/05-scheduler.md#chaos) and it is the deliberate contrast.

**Topology** — [`workhorse`](../../strands/lab-topologies.md#workhorse), continued and **empty**. The emptiness is the experimental control: any refusal here cannot be about capacity.

**Setup** — label the two workers into zones so that spreading has a topology to spread over:

```sh
kubectl label node <worker-1> topology.kubernetes.io/zone=za-a --overwrite
kubectl label node <worker-2> topology.kubernetes.io/zone=za-b --overwrite
kubectl get nodes -L topology.kubernetes.io/zone
kubectl describe node <worker-1> | grep -A6 'Allocated resources'
```

**Do**

1. **A spread that can be satisfied**, first, so the failing case has a control:

   ```sh
   kubectl -n sched-lab apply -f - <<'EOF'
   apiVersion: apps/v1
   kind: Deployment
   metadata: {name: spread-ok}
   spec:
     replicas: 4
     selector: {matchLabels: {app: spread-ok}}
     template:
       metadata: {labels: {app: spread-ok}}
       spec:
         topologySpreadConstraints:
         - maxSkew: 1
           topologyKey: topology.kubernetes.io/zone
           whenUnsatisfiable: DoNotSchedule
           labelSelector: {matchLabels: {app: spread-ok}}
         containers: [{name: pause, image: registry.k8s.io/pause:3.9}]
   EOF
   kubectl -n sched-lab get pods -l app=spread-ok -o wide
   ```

2. **Now make it unsatisfiable** by asking for a third zone that does not exist. Copy the Deployment, add a `nodeAffinity` requiring `topology.kubernetes.io/zone=za-c`, and submit it.

3. **And unsatisfiable a second way**, which produces a *different* sentence: three replicas with a required pod anti-affinity on the hostname, on a cluster with two schedulable nodes:

   ```sh
   kubectl -n sched-lab apply -f - <<'EOF'
   apiVersion: apps/v1
   kind: Deployment
   metadata: {name: anti}
   spec:
     replicas: 3
     selector: {matchLabels: {app: anti}}
     template:
       metadata: {labels: {app: anti}}
       spec:
         affinity:
           podAntiAffinity:
             requiredDuringSchedulingIgnoredDuringExecution:
             - topologyKey: kubernetes.io/hostname
               labelSelector: {matchLabels: {app: anti}}
         containers: [{name: pause, image: registry.k8s.io/pause:3.9}]
   EOF
   ```

4. **Read all three messages side by side** and put them next to the resource message from [5.C1](22-5c1-an-unschedulable-backlog.md):

   ```sh
   for d in spread-ok spread-bad anti; do
     echo "--- $d"
     kubectl -n sched-lab get pods -l app=$d --field-selector spec.nodeName= -o name \
       | head -1 | xargs -r -I{} kubectl -n sched-lab describe {} | sed -n '/Events/,$p' | tail -4
   done
   ```

5. **Confirm the cluster is not full**, which is the whole point and takes one command:

   ```sh
   kubectl describe node <worker-1> <worker-2> | grep -A6 'Allocated resources'
   ```

6. **Change the failure into a preference** and watch the same pods schedule:

   ```sh
   kubectl -n sched-lab patch deployment spread-bad --type=json \
     -p '[{"op":"replace","path":"/spec/template/spec/topologySpreadConstraints/0/whenUnsatisfiable","value":"ScheduleAnyway"}]'
   ```

7. Read the two plugins that produced these messages, and answer why each needs a `PreFilter`:

   ```sh
   ls pkg/scheduler/framework/plugins/podtopologyspread/ pkg/scheduler/framework/plugins/interpodaffinity/
   grep -n 'ErrReason\|func (pl \*PodTopologySpread) PreFilter' pkg/scheduler/framework/plugins/podtopologyspread/*.go | head
   ```

   [KEP-895 and KEP-3022](../../strands/source-reading.md#area-3-scheduler) are the background; the question to answer from the code is what the `PreFilter` computes once that the `Filter` would otherwise recompute per node, and why anti-affinity is the more expensive of the two.

8. **Note the third case that is not a scheduler problem at all**: with anti-affinity, the third replica is unschedulable *forever* on a two-node cluster, and adding a node fixes it. With the zone spread, adding a node fixes nothing unless it carries the missing label. Say which of the two is a capacity incident and which is a configuration incident, from the message alone.

**Observe** — the three event messages verbatim, the node allocation showing free capacity, and which pods schedule after step 6.

**Expect** — messages that name the constraint rather than a resource: one about node topology spread skew, one about pod anti-affinity rules, and neither containing the word `Insufficient`. **That single distinction — a plugin name and a constraint versus a resource name and a number — is the drill's entire deliverable**, and it is what stops an on-call engineer from adding nodes to fix a configuration error.

Expect step 6 to schedule everything immediately, because `ScheduleAnyway` makes the constraint a score rather than a filter. Note what that trades away: the pods now run, unevenly, and nothing tells you the constraint was violated except the distribution itself.

Expect anti-affinity's `PreFilter` to be doing real work — it has to account for every existing pod matching the selector across the whole cluster, which is why the area flags this pair as the expensive plugins and why they are the ones large clusters tune first.

**Write down** — the four messages together (both from this drill, one from [5.C1](22-5c1-an-unschedulable-backlog.md), one from [26](26-selectvictimsonnode-and-a-pdb-that-forbids.md)) as a diagnostic table: message shape, plugin, what it means, and the smallest fix. That table is a page you will use again, and it is the phase's most portable artifact.

**Footprint note** — around ten pause pods with no resource requests on an otherwise empty cluster; most stay pending. Deliberately the lightest exercise in module 5.6, because the finding is a sentence rather than a load. 8.5GB total, 1.0GB margin.

**Teardown** — `kubectl -n sched-lab delete deployment spread-ok spread-bad anti` and remove the zone labels:

```sh
kubectl label node <worker-1> <worker-2> topology.kubernetes.io/zone-
```

Leave the labels in place only if [the capstone](37-the-capstone-narrative.md) narrative needs them — decide now rather than later. **The topology stays** — the capstone is the last exercise on it.
