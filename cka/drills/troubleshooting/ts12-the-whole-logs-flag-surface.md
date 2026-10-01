<a id="ts12"></a>
# TS12 — The whole `kubectl logs` flag surface, in one pass

**Reflex** · **Pinned** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Troubleshooting / Manage and evaluate container output streams

> **This is a vocabulary drill, not a diagnosis drill.** Every flag here is trivial once known and unguessable under time pressure, and the one that matters most — `--previous` — is needed exactly when you are most rushed, because the container you want to read is already dead.

> **Pinned because the gap rule cannot see it.** [The diagnostic](../../plan.md#diagnostic) touches logs only inside one task, which measures a single read rather than the flag surface, so a score there says nothing about this sub-competency either way.

**Do**

Build one pod that exercises all of it: an init container, two named containers, and a main container that crashes once and then runs. Then read it eight ways, in one unbroken pass, without the help.

1. `-c <name>` — a named container. Without it, a multi-container pod errors and lists the names, which is a usable way to discover them.
2. `-c <init>` — **an init container is addressed the same way**, and this surprises people. Init container logs are where a pod stuck in `Init:` explains itself.
3. `--previous` — the instance before the current one. Only exists if the container restarted; a pod that was *deleted and recreated* has no previous, and the error says so.
4. `--since=10m` and `--since-time=<RFC3339>` — relative and absolute. Know both; the relative one is what you want under time pressure.
5. `--tail=50` — and know that the default is all of it, which on a chatty pod is how you lose thirty seconds to a scrollback.
6. `--timestamps` — not on by default, and essential the moment you are correlating two containers.
7. `-l app=x` with `--max-log-requests` — across every pod matching a label. Note that `kubectl logs deploy/x` is **not** this: it picks one pod and does not tell you which.
8. `--all-containers` and `-f`.

**Observe**

```sh
kubectl logs <pod>                      # errors usefully on a multi-container pod
kubectl logs <pod> -c <init> --timestamps
kubectl logs <pod> -c app --previous --tail=50
kubectl logs -l app=web --all-containers --since=10m --prefix
kubectl logs deploy/web                 # one pod, unnamed -- know the difference
```

**Done when** — all eight run first time, from memory, in one pass under ten minutes, and you can say without checking whether `--previous` will have anything to show for a given pod.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Build the pod, work the list with the help open. | 10 min |
| **2** | No help. `kubectl logs --help` is allowed in the exam, so pass 2 measures whether reading it costs you thirty seconds or three minutes. | 8 min |
| **3** | Cold, clock visible. All eight, no reference. | **5 min** |

**Teardown** — delete the namespace.

**See also** — **TS13** is the case where every one of these flags returns nothing because the process writes to a file. **TS14** is where those logs live on disk when `kubectl` is not available at all.
