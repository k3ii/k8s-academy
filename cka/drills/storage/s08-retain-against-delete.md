<a id="s08"></a>
# S8 — `Retain` against `Delete`, then recover a `Released` PV

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Storage / Reclaim policies

> **A `Released` PV does not rebind, and that surprises everyone once.** `Retain` keeps the data and leaves the PV holding a stale `claimRef` to a PVC that no longer exists — so a new PVC with the same name will **not** pick it up. Recovering it means clearing that one field. Knowing which field is the whole drill.

**Do**

1. Two classes, same provisioner, differing only in `reclaimPolicy` — `Delete` and `Retain`. (**S4** is where you built that.) A PVC and a pod against each, with a distinguishable file written into both.
2. **Delete both PVCs.** The `Delete` PV disappears and takes its data with it. The `Retain` PV survives and goes to `Released`.
3. Confirm the data really is still on the node for the retained one, over ssh. "Retain" is only interesting if you have seen the bytes still there.
4. **Try the naive recovery**: create a new PVC with the same name and class. It stays `Pending`; the `Released` PV is not offered to it. Watch that happen rather than reading about it.
5. **The actual recovery.** The PV's `spec.claimRef` still points at the deleted PVC. Clear it:

   ```sh
   kubectl patch pv <name> -p '{"spec":{"claimRef":null}}'
   ```

   The PV goes to `Available` and the waiting PVC binds. Mount it and read the original file back. That full cycle — `Bound` → `Released` → patched → `Available` → `Bound` — is what to have in your fingers.
6. **The targeted alternative**: instead of clearing `claimRef`, set it to the *new* PVC's namespace, name and uid, which pre-binds the PV to exactly that claim and nothing else. Worth writing once; it is how you hand a specific volume to a specific claim.
7. Change a live PV's policy with `kubectl patch pv … persistentVolumeReclaimPolicy` and confirm it takes — the PV's own policy is mutable even though its class's is not, which is the emergency lever when something is about to be deleted.

**Observe**

```sh
kubectl get pv -o custom-columns=NAME:.metadata.name,POLICY:.spec.persistentVolumeReclaimPolicy,STATUS:.status.phase,CLAIM:.spec.claimRef.name
kubectl patch pv <name> -p '{"spec":{"claimRef":null}}'
kubectl get pv    # Released -> Available
ssh -F ssh/config -J factory zain@10.10.10.131 'sudo ls -R /opt/local-path-provisioner'
```

**Done when** — you recover a `Released` PV with its data intact, from memory, in under two minutes.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Both policies, the failed naive recovery, the patch. | 10 min |
| **2** | A `Released` PV you did not create. Recover it without losing the data. | 8 min |
| **3** | Cold, no notes, clock visible. `Released` to `Bound`. | 5 min |

**Teardown** — delete the PVCs, **then the retained PVs by hand**, then check the node directory is clean. `Retain` means nothing cleans up for you, including after a drill.

**See also** — **S4** is where the two classes come from; **S1** is the `Delete` path taken for granted.
