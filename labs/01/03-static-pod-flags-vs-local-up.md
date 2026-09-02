<a id="static-pod-flags-vs-local-up"></a>
# Two control planes, one flag list

**Claim** — you can put the flags of `local-up-cluster.sh` and the static-pod flags of `kubeadm` side by side. You can then account for every difference in one of two ways. A difference is either *a development shortcut* or *a production requirement*. Nothing is left over.

**Rests on** — [module 1.1's `local-up-cluster.sh` question](../../phases/01-operate-shallow.md#m1-1). That question asks for the flag list of each binary. This list is the left-hand column of the table that you are about to build, so produce it from [the source](../../strands/source-reading.md#area-0-foundational) first. A third of these flags come back in [P3](../../phases/03-api-machinery.md).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up. You **read** `local-up-cluster.sh`, and you do not run it. It wants a built tree, and it would not fit alongside the cluster anyway.

**Do**

1. Print the three static-pod manifests, and pull out only the arguments:

   ```sh
   sudo grep -A40 'command:' /etc/kubernetes/manifests/kube-apiserver.yaml
   sudo awk '/- --/{print $2}' /etc/kubernetes/manifests/kube-controller-manager.yaml
   sudo awk '/- --/{print $2}' /etc/kubernetes/manifests/kube-scheduler.yaml
   ```

2. Build a table of three columns for each binary: **flag · `local-up-cluster.sh` · `kubeadm`**. Mark each row `both`, `dev-only` or `kubeadm-only`.
3. For every `kubeadm-only` row, write the reason in one word. Nearly all of the rows fall into four buckets: TLS, authentication, authorisation, and the aggregation layer. The fourth bucket is why [the map](02-what-kubeadm-generated.md) found a third CA.
4. For every `dev-only` row, say what the flag turned *off*. Sit with `--authorization-mode=AlwaysAllow`. A control plane with no authoriser is still a working control plane. That fact tells you how large a part of Kubernetes RBAC really is.
5. Find the flags that appear in *neither* list but govern things that you already care about. Start with `--etcd-servers` on the apiserver and `--allocate-node-cidrs` on the controller-manager. Then connect the second flag back to the `--pod-network-cidr` flag from [exercise 1](01-provision-and-kubeadm-init.md).

**Observe** — the manifests also carry three items: `hostNetwork: true`, `priorityClassName: system-node-critical`, and volume mounts of `/etc/kubernetes/pki` straight off the host. Note what each item implies. Each one tells you how early in the boot these pods must be able to start.

**Expect** — the apiserver diff is the big one, and it is almost entirely about security. The scheduler diff is nearly empty. Read that as an honest signal: the scheduler is the same program in both control planes. The extra flags of the controller-manager mostly answer two questions. Which controllers run, and what signs what? Those flags are `--controllers`, `--cluster-signing-cert-file` and `--use-service-account-credentials`.

**Write down** — the three tables, and one more sentence. That sentence names the single flag whose absence would most quickly turn this cluster into the cluster of `local-up-cluster.sh`.

**Teardown** — nothing was created. **The topology stays.**
