<a id="w06"></a>
# W6 — Roll back to a named revision, and read the history

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Workloads and Scheduling / Rollbacks

> **The rollout history is the ReplicaSets, and it is as shallow as `revisionHistoryLimit` says.** Default ten. A revision you need that has aged out is simply gone — there is no deeper store. Knowing where the history physically lives tells you immediately why `undo --to-revision` sometimes cannot.

**Do**

1. Three distinct image versions, applied in turn, so there is a history with three entries. `kubectl rollout history deploy/web` shows them.
2. **The `CHANGE-CAUSE` column is empty, and that is the default.** It is populated from the `kubernetes.io/change-cause` annotation, which nothing sets for you. Set it on one revision — `kubectl annotate deploy/web kubernetes.io/change-cause="…"` — and see it appear. Thirty seconds of habit that makes the history readable.
3. `kubectl rollout history deploy/web --revision=2` for the full pod template of one revision. That is how you find out what you are rolling back *to* before you do it.
4. `kubectl rollout undo deploy/web` returns to the previous revision. Note what it does to the numbering: the restored revision gets a **new, higher** number. The history is append-only; rolling back moves forward.
5. `--to-revision=1` for a specific one. Then try a revision number that does not exist and read the error.
6. **Set `revisionHistoryLimit: 2`** and roll a few more times. Watch old ReplicaSets get deleted and the corresponding revisions vanish from the history. Then try to roll back to one of them.
7. Note what is *not* versioned: a ConfigMap the Deployment mounts. Rolling back the Deployment does not roll back the config, which is a real production trap and the reason for hashed ConfigMap names.

**Observe**

```sh
kubectl rollout history deploy/web
kubectl rollout history deploy/web --revision=2
kubectl rollout undo deploy/web --to-revision=1
kubectl get rs -o custom-columns=NAME:.metadata.name,REV:.metadata.annotations.deployment\\.kubernetes\\.io/revision,DESIRED:.spec.replicas
```

**Done when** — you roll back to a specific revision from memory, and can say why a given revision is or is not still available.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Three revisions, annotate, undo both ways, trim the limit. | 10 min |
| **2** | A Deployment mid-roll on a broken image. Roll back without waiting for it. | 8 min |
| **3** | Cold, no notes. Undo to a named revision and prove it took. | 5 min |

**Teardown** — delete the namespace.

**See also** — **W5** is the roll this undoes; **TS4** is a bad rollout met as a fault.
