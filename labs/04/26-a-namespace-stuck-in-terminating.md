<a id="a-namespace-stuck-in-terminating"></a>
# A namespace that will not go, and the condition that says why

**Claim** — a namespace stuck in `Terminating` reports its own cause in `status.conditions`, and the condition you get distinguishes *an object's finalizer is blocking* from *the API server cannot enumerate what is in here*. You can produce the first, name the condition, and say what the second would look like — which matters because they need opposite responses.

**Rests on** — [4.C2](25-4c2-a-finalizer-that-never-completes.md), whose broken cleanup this reuses one level up, and [module 4.4's](../../phases/04-controllers.md#m4-4) namespace-controller reading question. This is [objective 6](../../phases/04-controllers.md#objectives).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with the in-cluster operator running.

**Setup**

```sh
kubectl create namespace academy-doomed
kubectl -n academy-doomed apply -f - <<'EOF'
apiVersion: academy.k3ii.dev/v1alpha1
kind: Ensemble
metadata: {name: resident}
spec: {voices: 2, registryNamespace: academy-registry}
EOF
```

The operator is a ClusterRole holder, so it reconciles this namespace too. Confirm the children and the registry key exist before breaking anything.

**Do**

1. Read the two questions from source first:

   ```sh
   cd ~/src/kubernetes
   git grep -n 'NamespaceFinalizersRemaining\|NamespaceContentRemaining\|NamespaceDeletionContentFailure\|NamespaceDeletionDiscoveryFailure' \
     -- pkg/controller/namespace/
   ```

   - **What must be empty before the namespace controller removes the `kubernetes` finalizer**, and how does it find out what is in the namespace at all?
   - From **KEP-5080**: what ordering did ordered namespace deletion introduce, and which security failure was it fixing? The answer is about pods outliving the policies that constrained them.

2. Break the operator's cleanup again, the same one-word edit as [4.C2](25-4c2-a-finalizer-that-never-completes.md), then delete the namespace:

   ```sh
   kubectl delete namespace academy-doomed --timeout=20s
   ```

3. Diagnose without guessing:

   ```sh
   kubectl get namespace academy-doomed -o jsonpath='{range .status.conditions[*]}{.type}: {.status} — {.message}{"\n"}{end}'
   ```

4. Only then go looking for the object, using the hunt that works when the condition does not name it for you:

   ```sh
   kubectl api-resources --verbs=list --namespaced -o name \
     | xargs -n1 kubectl get --show-kind --ignore-not-found -n academy-doomed
   ```

5. Fix it the right way: restore the ClusterRole and watch the namespace leave on its own.

**Observe** — the conditions in step 3, and the time between the fix and the namespace disappearing.

**Expect** — a condition naming remaining finalizers and, usually, the resource holding them. The namespace does not disappear and *nothing is retrying urgently* — the namespace controller re-checks on an interval, so the fix does not take effect instantly and the delay is not a sign the fix failed.

The step-4 hunt is the reflex worth building, because the condition tells you a finalizer remains and does not always tell you on what. That one-liner enumerates every namespaced resource the API server currently serves and asks each one, and it is the same command whether the culprit is your CRD, a `PersistentVolumeClaim`, or something a service mesh installed.

**The other condition is the one you have already met from the other side.** If a namespace cannot be enumerated at all — because an `APIService` in the aggregation layer is unreachable — the namespace controller cannot prove the namespace is empty and refuses to finish, reporting a discovery failure rather than a finalizer. That failure was produced deliberately in [P3's aggregation module](../../phases/03-api-machinery.md#m3-4), and the response is the opposite of this one: nothing in the namespace is wrong, and the repair is elsewhere in the cluster entirely. **Two identical symptoms, two conditions, two unrelated repairs** — which is why reading the condition first is worth the ten seconds.

The wrong fix at the namespace level deserves naming because it is the single most-copied command on the internet: editing a namespace's `spec.finalizers` through the `finalize` subresource. It works, it strands every object still in the namespace as unreachable garbage in etcd, and unlike [4.C2's](25-4c2-a-finalizer-that-never-completes.md) leak you cannot go and look at what you stranded, because the namespace they are in no longer exists.

**Write down** — the condition text verbatim, the step-4 command as a reusable snippet, the KEP-5080 ordering answer, and one line contrasting the finalizer condition with the discovery-failure condition.

**Footprint note** — nothing new.

**Teardown** — confirm `academy-doomed` is gone and the ClusterRole is the restored one. **The topology stays.**
