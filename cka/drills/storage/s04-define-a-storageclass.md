<a id="s04"></a>
# S4 — Define a StorageClass and provision through it

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Storage / Storage classes · dynamic provisioning

> **A StorageClass is a named set of instructions for a provisioner that already exists.** Writing one does not install anything. The fields are few and the exam asks you to write one from scratch, so the drill is: write it, provision through it, and know what each field changes.

> **This cluster has exactly one provisioner**, `rancher.io/local-path`, behind the `local-path` class. You will write **new classes against that same provisioner** — which is realistic, because that is what classes are for: several policies over one backend.

**Do**

1. Read the existing class as a template, then write your own with a different name and a different `reclaimPolicy`. Four fields carry the meaning:
   - `provisioner` — who acts. Immutable; a typo means a PVC that waits forever with no error.
   - `reclaimPolicy` — `Delete` or `Retain`, what happens to the PV when the PVC goes (**S8**).
   - `volumeBindingMode` — `Immediate` or `WaitForFirstConsumer` (**S6**).
   - `allowVolumeExpansion` — whether a bound PVC can grow. The installed class does **not** set it, so resizing is unavailable here until a class does.
   - and `parameters`, which are provisioner-specific and are the one part you cannot guess.
2. Provision a PVC through your class and confirm the PV carries your policy, not the original's.
3. **Prove classes are immutable where it counts.** Edit the `provisioner` of a live class and read the rejection. The workflow is delete-and-recreate, and existing PVs keep the old behaviour because the policy was copied onto the PV at creation — check that. A class is consulted once, not continuously.
4. Write a class naming a provisioner that does **not** exist. The PVC sits `Pending` in near-silence. This is worth doing once so the silence is recognisable.
5. Set `allowVolumeExpansion: true` on your new class and provision through it. Whether a resize then succeeds depends on the provisioner, not the class — the class only grants permission. **S3** takes that further.

**Observe**

```sh
kubectl get sc local-path -o yaml | grep -v -e creationTimestamp -e resourceVersion -e uid
kubectl get sc
kubectl get pv <name> -o jsonpath='{.spec.persistentVolumeReclaimPolicy}{"\n"}'
kubectl describe pvc <name> | sed -n '/Events/,$p'
```

**Done when** — you write a working StorageClass from memory and can say what each of its five fields changes.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Write one, provision through it, try to edit it. | 10 min |
| **2** | Two classes with different reclaim policies, one PVC each, compare the PVs. | 8 min |
| **3** | Cold, no notes. Class plus PVC plus pod, bound. | 5 min |

**Teardown** — delete your classes and their PVCs. **Leave `local-path` alone**; every other storage drill binds against it.

**See also** — **S5** is which class gets used when the PVC does not say; **S8** is the reclaim policy in action.
