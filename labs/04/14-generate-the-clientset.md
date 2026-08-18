<a id="generate-the-clientset"></a>
# The API type you write, and the four things generated from it

**Artifact** — `build/04-operator-clientgo/` initialised: the `Ensemble` API type, its CRD manifest, and a `pkg/generated/` tree produced by `code-generator` containing a typed clientset, listers, informers and deepcopy functions. **No controller yet** — this exercise is the API and its plumbing, and separating them is what makes [module 4.6's diff](33-the-diff.md) readable.

**Rests on** — [module 4.3's](../../phases/04-controllers.md#m4-3) `code-generator` reading. Everything generated here is a hand-written file you are choosing not to write, and the point of generating it *now* is that you will be able to name what each one replaced.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, for the CRD only. The generation itself runs on [`forge`](../../strands/lab-topologies.md#build-guest) with no cluster involved.

**Build**

```
build/04-operator-clientgo/
  go.mod
  hack/update-codegen.sh
  pkg/apis/academy/v1alpha1/
    doc.go            // +k8s:deepcopy-gen=package  // +groupName=academy.k3ii.dev
    types.go          Ensemble, EnsembleSpec, EnsembleStatus, EnsembleList
    register.go       SchemeBuilder, AddToScheme, SchemeGroupVersion
  config/crd.yaml     the CRD, with a status subresource
  pkg/generated/      written by the generators, never by you
```

**The type, fixed here and unchanged for the rest of the phase**, because two artifacts and eleven exercises compare against it:

```go
type EnsembleSpec struct {
    Voices            int32  `json:"voices"`            // 1..8, validated in the CRD schema
    RegistryNamespace string `json:"registryNamespace"`  // a namespace that is NOT this one
}
type EnsembleStatus struct {
    ObservedGeneration int64              `json:"observedGeneration,omitempty"`
    ReadyVoices        int32              `json:"readyVoices"`
    Conditions         []metav1.Condition `json:"conditions,omitempty"`
}
```

An `Ensemble` named `alpha` with `voices: 3` means: three ConfigMaps `alpha-voice-1..3` in the `Ensemble`'s own namespace, each owned by it, **and** one entry under the key `alpha` in a ConfigMap named `ensemble-registry` in `spec.registryNamespace`.

**That second half is not decoration.** Owner references cannot cross namespaces, so the registry entry is an object the garbage collector will never clean up for you — which is the honest, non-contrived reason a finalizer exists, and the thing [drill 4.C2](25-4c2-a-finalizer-that-never-completes.md) breaks. **This CRD-plus-children shape is also the referent [P8](../../phases/08-storage.md) points back at** when `external-snapshotter` turns out to be the same pattern with a CSI call in the middle: keep the artifact, and keep the write-up describing it.

**Do**

1. Write `types.go`, `register.go` and `doc.go` with the generator tags. Four tags carry all the weight — `+genclient`, `+genclient:noStatus` (or its absence), `+k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object`, and `+groupName`. For each of the four, write one line on what it changes in the output *before* you run anything.

2. Run the generators through `kube_codegen.sh` from `k8s.io/code-generator`, into `pkg/generated/`.

3. Apply the CRD and confirm the API server serves it with a status subresource:

   ```sh
   kubectl apply -f config/crd.yaml
   kubectl get --raw /apis/academy.k3ii.dev/v1alpha1 | jq '.resources[].name'
   ```

   The subresource is a separate entry in that list. If `ensembles/status` is missing, the CRD lacks `subresources: {status: {}}` and every status write you make later will bump `metadata.generation` — which is the bug [exercise 16](16-envtest-is-a-real-apiserver.md) asserts against.

4. Answer, from the generated tree rather than from documentation: **which generated package would you have to hand-write to make a typed `Get` work, and which one would you have to hand-write to make an informer work?** Name the file in each.

**Expect** — `pkg/generated/` holds four things: `clientset/`, `listers/`, `informers/`, and a `zz_generated.deepcopy.go` beside your types. The deepcopy file is the one that surprises people by being necessary: `runtime.Object` requires `DeepCopyObject()`, and without it your type cannot go into a scheme, a cache, or a watch — which means the informer machinery is unavailable to a type you *could* otherwise happily marshal.

**Write down** — the four-tag table from step 1, and a first version of the mapping table [the diff](33-the-diff.md) will finish: *generated file → what it replaces → who writes it in the `kubebuilder` version*. The third column is empty for now; it is filled in at [exercise 31](31-scaffold-the-same-operator.md).

**Footprint note** — generation is a compile of the four generators plus your package; well under [the 564 MiB the strand measured](../../strands/build-mechanics.md#measurements) for the shape this artifact belongs to. `forge` stays at 1536MB for this phase.

**Teardown** — nothing to delete; **keep the CRD installed**, everything from here needs it. **The topology stays.**
