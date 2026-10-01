<a id="n11"></a>
# N11 — Debug a distroless pod with an ephemeral container

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Servicing and Networking / Pod connectivity

> **`kubectl exec` into a distroless image fails, and the failure message is unhelpful.** There is no shell to exec — no `/bin/sh`, no `ls`, no `curl`. `kubectl debug` attaches a container that *does* have a shell into the running pod's namespaces. Recognising the "executable file not found" error as "wrong tool" rather than "broken pod" is the point.

**Do**

1. Run a distroless pod — `gcr.io/distroless/static` with a sleep-less workload, or any image with no shell. Try `kubectl exec -it … -- sh` and read the exact error.
2. `kubectl debug -it <pod> --image=busybox --target=<container>`. You get a shell that shares the target's **process** namespace, so you can see its processes, and its **network** namespace, so `wget localhost:8080` reaches it.
3. **Know what `--target` buys you**, because it is the flag people drop. Without it you share the network namespace but not the process namespace — so you can curl the app but not see its process or its `/proc`. Run it both ways and compare `ps`.
4. **The filesystem is not shared.** `/` inside the debug container is busybox's, not the target's. To read the target's files go through `/proc/1/root/…` with process-namespace sharing. Try it; this surprises people under time pressure.
5. Then the other two forms, so the three are not confused:
   - `kubectl debug <pod> --copy-to=<new> --set-image=…` — a *copy* with a changed image. The original keeps running.
   - `kubectl debug node/<node> -it --image=busybox` — a pod on the node with the host filesystem under `/host`. This is the node-level rescue tool and it is worth knowing before a node breaks.
6. Note that ephemeral containers **cannot be removed** and have no restart policy of their own; they live until the pod dies. Check `kubectl get pod -o yaml` and find yours under `ephemeralContainers`.

**Observe**

```sh
kubectl exec -it web -- sh                       # fails; read it
kubectl debug -it web --image=busybox --target=web
kubectl debug -it web --image=busybox            # no --target; compare ps
kubectl get pod web -o jsonpath='{.spec.ephemeralContainers[*].name}'
kubectl debug node/pair-w1 -it --image=busybox   # /host is the node
```

**Done when** — all three `kubectl debug` forms run from memory, and you can say for each what is shared and what is not.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. All three forms. | 10 min |
| **2** | A crash-looping distroless pod — debug a container that will not stay up. | 8 min |
| **3** | Cold, no notes. Shell inside a distroless pod's network namespace. | 5 min |

**Teardown** — delete the pods, including any `--copy-to` copies, which are easy to leave behind.

**See also** — **TS2** and **TS3** both end up here when the container has no shell.
