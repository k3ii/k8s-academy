<a id="the-hand-wired-loop"></a>
# Build artifact 1: every moving part wired by hand

**Artifact** — the phase's centre: a `client-go` operator in `build/04-operator-clientgo/` reconciling `Ensemble` objects, with informer, lister, rate-limiting workqueue, key-enqueuing handlers, `syncHandler`, finalizer and status subresource **all written by you**, running as `go run` against a live cluster. This is [stage 1](../../strands/build-mechanics.md#two-stages); [stage 2](19-stage-2-and-the-role-you-write-yourself.md) is a separate exercise and deliberately not a tax paid on every keystroke.

**Rests on** — [the generated clientset](14-generate-the-clientset.md) for the typed client, lister and informer; [the workqueue measurements](07-the-hot-loop-and-the-backoff-that-hides-it.md) for the retry policy; and [4.C4](12-4c4-act-before-the-cache-is-synced.md) for the one line that must come before the first reconcile.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with the `Ensemble` CRD installed. The operator runs on [`forge`](../../strands/lab-topologies.md#build-guest) against the cluster's API, which as far as the API server is concerned is indistinguishable from a controller running inside it.

**Build**

```
build/04-operator-clientgo/
  cmd/operator/main.go     flags, clients, informer factory, signal handling, Run
  pkg/controller/
    controller.go          the struct, NewController, Run, runWorker, processNextItem
    sync.go                syncHandler: the reconcile
    children.go            the desired ConfigMap set, and the owner reference
    registry.go            the cross-namespace entry, and its removal
    status.go              conditions, observedGeneration, readyVoices
```

What it must satisfy, as an interface rather than an implementation:

1. **Two event sources, one queue.** A handler on `Ensemble` that enqueues the object's own key, and a handler on `ConfigMap` that maps a child back to its owner and enqueues *that* key. The second is the one that makes [the stomp](05-stomp-it-back.md) work, and it must ignore ConfigMaps whose controller owner reference is missing or points elsewhere.

2. **`WaitForCacheSync` before the first `Get` from the queue.** One line, for [the reason you constructed](12-4c4-act-before-the-cache-is-synced.md).

3. **A `syncHandler(key string) error` that is a pure function of the cluster's state** — it reads the `Ensemble` from the lister, computes the desired child set from `spec.voices`, and creates or deletes to close the gap. It never reads which delta woke it and never carries state between calls. Children are named deterministically; that choice is load-bearing and [exercise 22](22-expectations-or-over-create.md) is where it is cashed in.

4. **The `NotFound` branch.** A key can arrive for an object that no longer exists. That is normal, it is not an error, and returning an error there produces [the hot loop you measured](07-the-hot-loop-and-the-backoff-that-hides-it.md) against an object nobody can fix.

5. **A finalizer**, `academy.k3ii.dev/registry-cleanup`, added on first reconcile and removed only after the registry entry is gone. The ordering is the whole content of the pattern: on a delete, `deletionTimestamp` is set and the object stays; you do the cleanup; you remove the finalizer; the API server then actually deletes it. Getting the order wrong leaks the entry, and [4.C2](25-4c2-a-finalizer-that-never-completes.md) is the failure of the step in the middle.

6. **A status write through the subresource**, carrying `readyVoices`, `observedGeneration` and a `Ready` condition with a reason. It must be a `.Status().Update()` or a status patch — writing status through the main resource is the bug [exercise 16](16-envtest-is-a-real-apiserver.md) catches.

7. **Requeue on error, `Forget` on success**, through the rate-limiting queue. This is the single line [the capstone](../../phases/04-controllers.md#capstone) asks you to cite, so put it somewhere you can point at.

**Do**

```sh
cd ~/src/k8s-academy/build/04-operator-clientgo
go run ./cmd/operator --kubeconfig=$HOME/.kube/config -v=2
```

```sh
kubectl create namespace academy-registry
kubectl -n academy-lab apply -f - <<'EOF'
apiVersion: academy.k3ii.dev/v1alpha1
kind: Ensemble
metadata: {name: alpha}
spec: {voices: 3, registryNamespace: academy-registry}
EOF
kubectl -n academy-lab get configmaps
kubectl -n academy-registry get configmap ensemble-registry -o yaml
kubectl -n academy-lab patch ensemble alpha --type=merge -p '{"spec":{"voices":5}}'
kubectl -n academy-lab delete configmap alpha-voice-2
kubectl -n academy-lab get ensemble alpha -o yaml
```

**Gate** — [`envtest`](../../strands/build-mechanics.md#gates), and it is [the next exercise](16-envtest-is-a-real-apiserver.md). A `go run` that behaves is evidence; the gate is a harness.

**Expect** — three ConfigMaps, then five, then the hand-deleted one back within a second. `status.readyVoices` tracks, `status.conditions[Ready]` flips with a reason, and the registry ConfigMap in the other namespace has one key. Deleting the `Ensemble` removes the three children **by garbage collection, not by your code** — you never wrote a delete for them — and removes the registry key **by your code**, because nothing else can.

That asymmetry is the exercise's real observable and it is worth stating out loud in the write-up: **the two cleanups look identical from outside and are done by different machines**, one of which is the cluster's and one of which is yours.

**Write down** — [the checklist's](../../phases/04-controllers.md#checklist) 4.3 artifact: the five hand-wired parts mapped to their `sample-controller` equivalents, and the requeue line with its `file:line` in your own code.

**Footprint note** — one more Go process on `forge`, in the shape [the strand measured at 564 MiB peak while linking](../../strands/build-mechanics.md#measurements) and a fraction of that while running. `pair` gains a handful of ConfigMaps. No change to the phase's 6.5GB steady state.

**Teardown** — leave the operator, the `Ensemble` and both namespaces in place; the next four exercises all drive this artifact. **The topology stays.**
