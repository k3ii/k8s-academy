<a id="falco-reads-the-syscall"></a>
# A shell opened inside a container, and the alert Falco writes from the syscall — no agent in the pod

**Artifact** — a running Falco (modern-eBPF driver) and the alert line it emits when you `kubectl exec` a shell into an unrelated pod, showing that Falco saw the `execve` from *outside* the container, at the kernel, with no sidecar and nothing installed in the workload. This establishes the instrument the rest of the module tunes: before you can write a rule that beats a variant, you need Falco reading syscalls and proving it by firing on a default rule.

**Rests on** — [the P7 eBPF work](../../phases/07-networking.md): Falco's modern driver is the same eBPF machinery, now attached to syscall tracepoints instead of the network path. This is that mechanism in a security tool.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued — **but Falco costs real memory** ([512Mi request / 1Gi limit per node](../../research/ecosystem-picks.md#falco)), so this phase installs the DaemonSet **pinned to the worker only** via a `nodeSelector`, halving the footprint to one node, and every workload from here to the capstone is scheduled to that worker so Falco can see it. The index carries the arithmetic; the one-node pin is the change that keeps the phase under [the ceiling](../../strands/lab-topologies.md#pair).

**Read** — [the Falco architecture](https://falco.org/docs/): a per-node driver copies syscall events into userspace, `libsinsp` reconstructs process/container/k8s state, and rules match against that enriched event. The question to answer before you install: *what does the `container.id` on an event come from* — how does a syscall, which the kernel tags with no Kubernetes identity at all, end up labelled with a container and a pod?

**Do** — install Falco on the worker only, then trigger a default rule:

```sh
WORKER=$(kubectl get node -l '!node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].metadata.name}')
helm repo add falcosecurity https://falcosecurity.github.io/charts && helm repo update
helm install falco falcosecurity/falco -n falco --create-namespace \
  --set driver.kind=modern_ebpf \
  --set nodeSelector."kubernetes\.io/hostname"=$WORKER \
  --set 'falco.rules_file={/etc/falco/falco_rules.yaml,/etc/falco/rules.d}' \
  --set resources.requests.memory=512Mi --set resources.limits.memory=1Gi
kubectl -n falco rollout status ds/falco

# a workload on the worker, then a shell into it
kubectl run victim --image=nginx --overrides="{\"spec\":{\"nodeName\":\"$WORKER\"}}" --restart=Never
kubectl wait --for=condition=Ready pod/victim
kubectl exec victim -- bash -c 'echo in'
# read what Falco emitted
kubectl -n falco logs ds/falco | grep -i 'shell\|exec\|Terminal' | tail -5
```

**Observe** — a Falco alert line for the exec, of the form `Notice A shell was spawned ... container=<id> ... k8s.pod=victim` (the default *Terminal shell in container* rule). Falco is a DaemonSet pod on the worker — not a sidecar in `victim`, not a process in the pod's namespaces — yet it named the pod. That naming is the answer to the reading question: the driver reports the raw `execve` with a cgroup id; `libsinsp` maps that cgroup to a container via the container runtime and then to a pod via the kubelet, enriching a kernel event with Kubernetes identity after the fact. **The detection is at the kernel; the labels are reconstructed.**

**Expect** — one alert naming the exec and the pod. If the log is empty, the driver failed to load (check `kubectl -n falco logs ds/falco | grep -i driver`) — modern eBPF needs a recent-enough kernel, and the fallback is `driver.kind=ebpf` (legacy) before the kernel module.

**Write down** — the alert line for the exec, and one sentence on how a syscall acquires a pod name.

**Teardown** — **Falco stays** for [the string-rule drill](23-10c5-a-string-rule-a-variant-evades.md) and [the behavioral rule](24-a-falco-rule-that-names-the-container.md); delete only the victim pod; **the topology stays**:

```sh
kubectl delete pod victim
```
