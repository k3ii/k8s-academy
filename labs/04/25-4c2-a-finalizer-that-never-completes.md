<a id="4c2-a-finalizer-that-never-completes"></a>
# 4.C2 — stuck in `Terminating`, cleared twice, once wrongly

**Claim** — an object wedged by a finalizer is diagnosable in three commands, and the two ways out are not equivalent: force-removing the finalizer deletes the object and **leaves behind exactly the thing the finalizer existed to remove**, which you can go and find afterwards. Fixing the cleanup deletes the object and the leftover. The visible outcome is identical.

**Rests on** — [the finalizer](15-the-hand-wired-loop.md), [the ClusterRole you discovered](19-stage-2-and-the-role-you-write-yourself.md) — which is what this drill breaks — and [the cross-namespace event](23-one-owner-may-be-the-controller.md) that justified the finalizer in the first place.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. **The operator must be the in-cluster one for this drill**, because the break is an authorisation failure and the `go run` copy uses your admin kubeconfig, which cannot be made to fail this way:

```sh
kubectl -n academy-build scale deploy academy-operator --replicas=1
# and stop the go run copy on forge
```

**Setup — the escape hatch, saved before anything breaks:**

```sh
kubectl get clusterrole academy-operator -o yaml > ~/academy-operator-clusterrole.bak.yaml
```

One `kubectl apply -f` of that file undoes the entire drill. Test it now.

Create two identical victims:

```sh
for n in wrongfix rightfix; do
  kubectl -n academy-lab apply -f - <<EOF
apiVersion: academy.k3ii.dev/v1alpha1
kind: Ensemble
metadata: {name: $n}
spec: {voices: 2, registryNamespace: academy-registry}
EOF
done
kubectl -n academy-registry get configmap ensemble-registry -o jsonpath='{.data}' ; echo
```

Both keys are in the registry. That is the state the finalizer is responsible for.

**Do**

1. **Break it.** Remove the verb the cleanup needs — `update` on `configmaps` — from the ClusterRole, leaving everything else intact. This is a one-word edit and it is the most common real cause of this failure.

2. Delete both objects:

   ```sh
   kubectl -n academy-lab delete ensemble wrongfix --timeout=15s
   kubectl -n academy-lab delete ensemble rightfix --timeout=15s
   ```

3. **Diagnose, in three commands, before fixing anything.** Write the answer to each before running the next:

   ```sh
   kubectl -n academy-lab get ensemble
   kubectl -n academy-lab get ensemble wrongfix -o jsonpath='{.metadata.deletionTimestamp}{"\n"}{.metadata.finalizers}{"\n"}'
   kubectl -n academy-build logs deploy/academy-operator --tail=30
   ```

4. **The wrong fix**, on `wrongfix` only:

   ```sh
   kubectl -n academy-lab patch ensemble wrongfix --type=merge -p '{"metadata":{"finalizers":null}}'
   ```

5. **The right fix**, on `rightfix`:

   ```sh
   kubectl apply -f ~/academy-operator-clusterrole.bak.yaml
   ```

6. Go and look for the damage:

   ```sh
   kubectl -n academy-registry get configmap ensemble-registry -o jsonpath='{.data}' ; echo
   ```

**Observe** — the `deletionTimestamp` and `finalizers` on a wedged object; the operator's 403; the registry contents after each fix.

**Expect** — both objects sit in `Terminating` with a `deletionTimestamp` in the past and one finalizer remaining. **The delete already happened as far as the client is concerned** — the request succeeded, the object is marked, and what remains is the cluster refusing to finish. This is the state to recognise: `deletionTimestamp` set plus a non-empty `finalizers` list is a complete diagnosis of *what*, and the finalizer's name is the complete diagnosis of *who*.

After step 4, `wrongfix` disappears instantly and its key is still in the registry ConfigMap, with nothing left in the cluster that refers to it. After step 5, `rightfix` disappears within a reconcile and **its key is gone**. Both look the same from `kubectl get ensemble`. The difference is only visible in the other namespace, which is the definition of a leak.

Force-removing a finalizer is sometimes the right call — when the controller is gone for good and the object is blocking something. **The rule to write down is that it is a decision to accept the leak, and it is only defensible once you have named what leaks.** Here you can name it exactly.

**Write down** — [the checklist's](../../phases/04-controllers.md#checklist) `Terminating` diagnosis: which finalizer, why it blocked, the three-command sequence that identified it, and the leaked key you found after the wrong fix. Keep the operator's 403 line verbatim; it names the verb, the resource and the ServiceAccount, and it is the fastest path from symptom to cause you will ever get for this failure.

**Footprint note** — nothing new.

**Teardown** — confirm the ClusterRole is restored and `kubectl -n academy-lab get ensemble` shows only `alpha`. Manually remove the leaked `wrongfix` key from `ensemble-registry`, by hand, which is the operational tax the wrong fix charged. **The topology stays** — [the namespace version of this failure](26-a-namespace-stuck-in-terminating.md) is next.
