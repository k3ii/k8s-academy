<a id="ts11"></a>
# TS11 — A pod was OOMKilled: prove it, then right-size it

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Troubleshooting / Monitor cluster and application resource usage

> **Exit code 137 is `128 + 9` — the process was `SIGKILL`ed — and the kernel did it, not Kubernetes.** The container exceeded its memory cgroup limit. Nothing in `kubectl logs` will say so, because the process got no chance to say anything. The proof lives in `Last State`, and knowing to look there is the drill.

**Break it** — *pass 1 only.*

A container with `limits.memory: 64Mi` that allocates well past it — a few lines of Python, or `stress-ng --vm 1 --vm-bytes 200M`. Then a second variant with **no limit at all**, so the node's memory is the constraint and the kubelet evicts instead (**TS2**). The two look similar and are not the same event.

**Work it**

- **`kubectl describe pod`, and read `Last State`**, not `State`. A restarted container's current state is `Running`; the *previous* one carries `Reason: OOMKilled` and `Exit Code: 137`. Looking only at the current state is why this fault gets misdiagnosed as a crash loop.
- **`kubectl logs --previous`** for whatever the process managed to emit before it died. Usually nothing — and that emptiness is itself consistent with a `SIGKILL`, which is a diagnostic fact, not a dead end (**TS13** is the other reason logs are empty).
- **Tell it apart from a crash loop.** Both show `CrashLoopBackOff` and climbing restarts. OOMKilled has reason `OOMKilled` and code **137**; an application failure has its own non-zero code and usually a log. One command separates them; reach for it before anything else.
- **Tell it apart from eviction.** OOM-kill is the **kernel** enforcing one container's cgroup limit — pod stays, container restarts. Eviction is the **kubelet** acting on node-level pressure — the pod leaves the node entirely with status `Evicted`. Different actor, different scope, different fix.
- **Find the limit that bound it**: `kubectl get pod -o jsonpath` for the container's `resources`. Then, on the node, read the cgroup's `memory.max` and `memory.peak` for the real numbers. That is the measurement that turns right-sizing from guesswork into arithmetic.
- **Right-size it.** Raise the limit, confirm it stops. Then consider the real question — whether the limit was wrong or the application leaks. Note that raising a *limit* without raising the *request* changes QoS class from `Guaranteed` to `Burstable`, which changes eviction order (**W1**). A fix in one dimension is a change in another.

**Observe**

```sh
kubectl get pods                      # CrashLoopBackOff, RESTARTS climbing
kubectl describe pod hog | sed -n '/Last State/,/Ready/p'
kubectl get pod hog -o jsonpath='{.status.containerStatuses[0].lastState}' | python3 -m json.tool
kubectl logs hog --previous
kubectl get pod hog -o jsonpath='{.spec.containers[0].resources}{"\n"}'
```

**Done when** — you prove OOMKilled from `Last State` and exit code in under a minute, and can say in a sentence how it differs from both a crash loop and an eviction.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Both variants, both diagnoses. | 10 min |
| **2** | A multi-container pod where only one was killed. Name which, and why the others lived. | 8 min |
| **3** | Cold, no notes. Prove it and right-size it. | 5 min |

**Teardown** — delete the namespace. Confirm no node is left under memory pressure.

**See also** — **TS2** is the eviction this is not; **W1** is the requests-and-limits model underneath; **W11** is the restart behaviour.
