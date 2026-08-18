<a id="bind-a-pod-with-one-post"></a>
# Scheduling, minus the scheduler: one POST to a subresource

**Claim** — everything a scheduler does ends in a single write, and that write is a `Binding` POSTed to the pod's `binding` subresource; a pod nobody is scheduling will start running the moment you send it by hand, and the kubelet cannot tell the difference between your `curl` and `kube-scheduler`.

**Rests on** — [`pair`](06-three-rejections-three-plugins.md) being up. Nothing else. This is deliberately the smallest possible thing before [the from-scratch scheduler](09-two-hundred-lines-that-schedule.md), so that the program you write next is demystified before it exists.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup** — a pod that no scheduler will ever touch, because it names one that does not exist:

```sh
kubectl -n sched-lab apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata: {name: manual}
spec:
  schedulerName: nobody-at-all
  containers: [{name: pause, image: registry.k8s.io/pause:3.9}]
EOF
kubectl -n sched-lab get pod manual -o wide
kubectl -n sched-lab describe pod manual | sed -n '/Events/,$p'
```

**Do**

1. Confirm the negative result first: the pod is `Pending`, `spec.nodeName` is empty, and there is **no `FailedScheduling` event** — nothing refused it, because nothing looked at it. That absence is a different state from [the three refusals](06-three-rejections-three-plugins.md) and telling them apart on sight is worth thirty seconds now.

2. Send the binding:

   ```sh
   NODE=<worker-node>
   cat > /tmp/binding.json <<EOF
   {"apiVersion":"v1","kind":"Binding",
    "metadata":{"name":"manual","namespace":"sched-lab"},
    "target":{"apiVersion":"v1","kind":"Node","name":"$NODE"}}
   EOF
   kubectl create --raw /api/v1/namespaces/sched-lab/pods/manual/binding -f /tmp/binding.json
   ```

3. Watch what happens without touching anything else:

   ```sh
   kubectl -n sched-lab get pod manual -o wide -w
   ```

4. Send it a second time, to the *other* node:

   ```sh
   sed -i "s/$NODE/<cp-node>/" /tmp/binding.json
   kubectl create --raw /api/v1/namespaces/sched-lab/pods/manual/binding -f /tmp/binding.json
   ```

5. Find where the API server implements this, so the subresource is a code path rather than a URL:

   ```sh
   grep -rn 'Binding' pkg/registry/core/pod/storage/storage.go | head -20
   ```

   Answer one question from it: what does the handler set on the pod, and what does it refuse to do if that field is already set?

**Observe** — `spec.nodeName` before and after, the transition from `Pending` to `ContainerCreating` to `Running`, and the exact HTTP status of the second POST.

**Expect** — a pod running within a couple of seconds of a POST that carries no scheduling logic whatsoever. The second POST fails with **409 Conflict** and a message saying the pod is already assigned; that refusal is the API server's, not the scheduler's, and it is the entire mechanism that makes running two schedulers merely wasteful rather than corrupting. [Exercise 10](10-5c4-two-schedulers-one-pod.md) is where that matters.

Expect the storage code to show `binding` as a write of one field with a precondition on it, which is the same shape as [the conflict machinery met in P3](../../phases/03-api-machinery.md#m3-5) rather than anything scheduler-specific.

**Write down** — the 409's full message, and one sentence naming what a scheduler is, given this exercise: *a program that decides which node name to put in that JSON.* Everything else in this phase is about how that decision is made well and fast.

**Footprint note** — one pause pod. No build. `pair` 5.0GB plus `forge` 2560MB, unchanged from [exercise 7](07-fifteen-thirty-six-will-not-link-a-scheduler.md).

**Teardown** — `kubectl -n sched-lab delete pod manual`, `rm /tmp/binding.json`. **The topology stays.**
