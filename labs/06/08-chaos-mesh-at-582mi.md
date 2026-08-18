<a id="chaos-mesh-at-582mi"></a>
# Install the injector once, and read every capability it asks for

**Artifact** — Chaos Mesh running on `pair` inside a measured 582Mi budget, plus a table with one row per capability the daemon holds, naming the fault class that needs it and the syscall or subsystem it reaches. **The install itself is not the artifact — the table is.** You will run this install again at the start of P7, P9, P10, P11 and P12; you read it once, here.

**Rests on** — [the oom_score_adj numbers](07-oom-score-adj-from-the-formula.md), because the next exercise's kill is judged against them.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Both nodes: `chaos-daemon` is a DaemonSet and the worker's copy is the one that does the work in this phase.

**Setup**

```sh
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm repo update
```

Then run [the minimised install from the chaos strand](../../strands/chaos.md#install) **verbatim**, with these four limits appended — the strand says to set them and this is the phase that has to choose the numbers:

```sh
  --version 2.8.2 \
  --set controllerManager.resources.limits.memory=256Mi \
  --set controllerManager.resources.requests.memory=192Mi \
  --set chaosDaemon.resources.limits.memory=100Mi \
  --set chaosDaemon.resources.requests.memory=64Mi \
  --set dnsServer.resources.limits.memory=128Mi \
  --set dnsServer.resources.requests.memory=96Mi
```

Record the chart version you installed. It matters later: [P10](../../phases/10-security.md) deliberately installs an *older* one.

**Read** — [the mechanism table](../../strands/chaos.md#mechanisms) and, beside it, the daemon's actual security context on the running cluster:

```sh
kubectl -n chaos-mesh get ds chaos-daemon \
  -o jsonpath='{.spec.template.spec.containers[0].securityContext}' | jq
kubectl -n chaos-mesh get ds chaos-daemon \
  -o jsonpath='{range .spec.template.spec.volumes[*]}{.name}{"\t"}{.hostPath.path}{"\n"}{end}'
kubectl -n chaos-mesh get ds chaos-daemon \
  -o jsonpath='{.spec.template.spec.hostPID}{"\n"}'
```

The table you are building has one row per capability in the strand's non-privileged set. For each: which fault class stops working without it, and what it lets the daemon do that an ordinary container cannot. `SYS_PTRACE` and `SYS_ADMIN` are the two whose answers are worth a sentence each rather than a phrase.

**Do**

1. Confirm the install is complete and the CRDs are served:

   ```sh
   kubectl -n chaos-mesh get pods -o wide
   kubectl api-resources --api-group=chaos-mesh.org
   ```

2. **Measure what it actually costs**, from the kubelet's own cAdvisor endpoint — there is no metrics-server on this cluster yet, and [there will not be one until exercise 25](25-the-stack-that-must-not-be-evicted.md):

   ```sh
   for n in pair-cp pair-worker; do
     echo "== $n"
     kubectl get --raw "/api/v1/nodes/$n/proxy/metrics/cadvisor" \
       | grep '^container_memory_working_set_bytes{' | grep 'namespace="chaos-mesh"' \
       | awk -F'container="' '{split($2,a,"\""); print a[1], $NF}'
   done
   ```

   Sum it. Compare with the strand's 582Mi budget and with the limits you set.

3. Run [the kernel-config check from the strand](../../strands/chaos.md#verify-first) on the worker and write the answer down once. It decides whether `KernelChaos` is available to you for the rest of the curriculum.

**Expect** — one `chaos-controller-manager`, one `chaos-dns-server`, two `chaos-daemon` pods, and no dashboard. Expect the measured working set to come in *under* the budget on an idle cluster and the controller manager to be the largest single consumer — the daemons are thin because their work happens in other processes' namespaces, not in their own.

Expect `hostPID: true` and the host mounts to explain themselves once the table exists: [the daemon needs a host PID to open `/proc/<pid>/ns/*` with](../../strands/chaos.md#mechanisms), and a container that cannot see the target's PID cannot enter its namespaces. This is the phase's clearest example of a privilege that is not laziness.

**Write down** — the capability table, the measured total against 582Mi, the chart version, and the `CONFIG_BPF_KPROBE_OVERRIDE` answer.

**Footprint note** — 582Mi budgeted, split across both nodes, and it comes out of the **worker's 2048MB** where the daemon and half the split land. That matters more here than anywhere else in the curriculum: from [drill 6.C3](09-6c3-who-killed-the-pod.md) onward the worker's remaining memory *is* the instrument, so the number you measure in step 2 is a baseline to subtract, not a footnote. `pair` at 5.0GB plus `forge` at 1536MB is 6.5GB against [the 9.5GB ceiling](../../strands/lab-topologies.md#ceiling); the injector is inside the guests, not beside them.

**Teardown** — **nothing.** Chaos Mesh stays for the rest of the phase, and it is destroyed with the topology at [the capstone](29-the-capstone-trace.md) rather than uninstalled. Every later phase that needs it re-runs the strand's install block as one line of setup — that is why this exercise exists once and never again. **The topology stays.**
