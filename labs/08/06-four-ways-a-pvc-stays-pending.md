<a id="four-ways-a-pvc-stays-pending"></a>
# Induce all four causes of a Pending PVC, then diagnose each in 90 seconds

**Artifact** — four induced failures and four diagnoses made from `kubectl describe` output alone, each **under 90 seconds**, timed. This is the drill behind [the checklist item](../../phases/08-storage.md#checklist) and it is the single most useful diagnostic reflex in the phase.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [the zone mismatch](05-zone-mismatch-by-construction.md).

**Do**

Build each state deliberately, one at a time, and have someone — or a shuffled script — present them to you unlabelled afterwards.

1. **No matching PV.** A static claim whose size or access mode nothing satisfies.
2. **No provisioner.** A claim naming a `storageClassName` that does not exist, and a second naming a class whose provisioner is not installed. These produce different events; note which.
3. **`WaitForFirstConsumer` with an unschedulable pod.** The pod's affinity cannot be satisfied, so the binding decision never comes. The PVC is `Pending` for a reason that is not about storage at all.
4. **Exhausted capacity.** The provisioner accepts the claim and fails to fulfil it.

Then, cold: `describe` the PVC, start the clock, and say the cause and the fix.

**Observe**

```sh
kubectl describe pvc <name>
kubectl get events --field-selector involvedObject.name=<pvc> --sort-by=.lastTimestamp
kubectl get storageclass
```

**Expect** — case 3 is the one that costs people hours, because every symptom points at storage and the fault is in the pod. The tell is `waiting for first consumer` **plus** a pod that is itself `Pending`; either alone means something else.

**Write down** — a four-row table: symptom in `describe` → cause → fix. Keep it; it is exam material and incident material both.

**Teardown** — delete the four PVCs. Leave the cluster up for [the mount trace](07-volume-to-mount-trace.md).
