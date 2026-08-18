<a id="a-second-scheduler-by-schedulername"></a>
# Stage 2, shape one: your scheduler as a Deployment nobody privileged

**Artifact** — [build artifact 1](09-two-hundred-lines-that-schedule.md) moved inside the cluster: an image in [the `forge` registry](../../strands/build-mechanics.md#registry), a ServiceAccount, the **smallest ClusterRole that lets it work**, and a Deployment in `academy-build` serving pods that name it in `spec.schedulerName`. This is [stage 2](../../strands/build-mechanics.md#two-stages) for the from-scratch scheduler, and the first of the phase's two deployment shapes.

**Rests on** — [the from-scratch scheduler](09-two-hundred-lines-that-schedule.md), running correctly outside. Nothing about the code changes here; everything about its identity does.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. **Derive the permissions before writing them.** Go through your own source and list every API call it makes, with verb and resource. There are fewer than ten. For each, say why it is needed; the list is the ClusterRole and anything you cannot justify is a permission to delete.

2. **Write the ClusterRole from that list**, and *only* from it. The one that people get wrong is the binding: it is a **subresource** of pods, and the verb is `create`, not `update` — which follows directly from [the POST you sent by hand](08-bind-a-pod-with-one-post.md).

3. Build and push, following [the image conventions](../../strands/build-mechanics.md#base-image) and [the identity conventions](../../strands/build-mechanics.md#identity):

   ```sh
   cd ~/src/k8s-academy/build/05-scheduler-clientgo
   docker buildx build --platform linux/amd64 -t forge.lab:5000/academy/toy-scheduler:v1 --push .
   ```

4. Deploy it with **no in-cluster kubeconfig**, so it must use its ServiceAccount token:

   ```sh
   kubectl -n academy-build apply -f deploy/
   kubectl -n academy-build get deploy,pod
   kubectl -n academy-build logs -l app=toy-scheduler --tail=20
   ```

   The flag your `main.go` takes for a kubeconfig must be *absent* here. If it works with the flag and fails without it, the in-cluster configuration path is not wired and the rest of this exercise is measuring the wrong thing.

5. **Prove least privilege by breaking it.** Remove one rule, apply, restart, and watch it fail; then put it back:

   ```sh
   kubectl auth can-i --as=system:serviceaccount:academy-build:toy-scheduler create pods/binding
   kubectl auth can-i --as=system:serviceaccount:academy-build:toy-scheduler delete pods
   ```

   The second must be **no**. A scheduler that can delete pods is a scheduler that could preempt, and yours has no business doing that.

6. Drive it:

   ```sh
   kubectl -n sched-lab create deployment inside --image=registry.k8s.io/pause:3.9 --replicas=4 \
     --dry-run=client -o yaml \
     | sed 's/^      containers:/      schedulerName: toy-scheduler\n      containers:/' \
     | kubectl -n sched-lab apply -f -
   kubectl -n sched-lab get pods -l app=inside -o wide
   ```

7. **Kill it and watch what replaces it.** Delete the pod, not the Deployment:

   ```sh
   kubectl -n academy-build delete pod -l app=toy-scheduler
   kubectl -n sched-lab scale deployment inside --replicas=8
   ```

**Observe** — the ClusterRole's final rule count, the two `auth can-i` answers, and how long pods wait while the scheduler is being rescheduled.

**Expect** — a ClusterRole with a handful of rules, of which exactly one is a subresource. Expect the identity change to be the only real work: [the API server cannot tell the difference](../../strands/build-mechanics.md#two-stages) between this and the `go run`, which is precisely why stage 1 was not a simulation.

Expect step 7 to expose the circularity worth noticing: your scheduler's own replacement pod is scheduled by the **default** scheduler, because it does not name itself in `schedulerName`. Check that it does not. A scheduler that schedules itself cannot start on an empty cluster, and the same argument is why the real `kube-scheduler` is a static pod rather than a Deployment.

Expect a gap of some seconds during which pods naming your scheduler simply wait. Nothing errors; they are pending with no event, which is [the silence you learned to read](24-a-pod-that-is-never-considered.md).

**Write down** — the API-call-to-rule derivation table, the rule you removed and the exact error it produced, and one sentence on why the real scheduler is not a Deployment.

**Footprint note** — one small Go process now runs *inside* `pair` rather than on `forge`, which moves a few tens of MiB from one budget to the other and changes nothing at the ceiling. 7.5GB total.

**Teardown** — leave it running; [the lease exercise](32-the-lease-changes-hands.md) scales this same Deployment to two. `kubectl -n sched-lab delete deployment inside`. **The topology stays.**
