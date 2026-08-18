<a id="static-pod-flags-vs-local-up"></a>
# Two control planes, one flag list

**Claim** — you can put `local-up-cluster.sh`'s flags and `kubeadm`'s static-pod flags side by side and account for every difference as either *a development shortcut* or *a production requirement*, with no leftovers.

**Rests on** — [module 1.1's `local-up-cluster.sh` question](../../phases/01-operate-shallow.md#m1-1): the flag list per binary. That list is the left-hand column of the table you are about to build, so produce it from [the source](../../strands/source-reading.md#area-0-foundational) first. A third of these flags come back in [P3](../../phases/03-api-machinery.md).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up. `local-up-cluster.sh` is **read, not run** — it wants a built tree and it would not fit alongside the cluster anyway.

**Do**

1. Print the three static-pod manifests and pull out just the arguments:

   ```sh
   sudo grep -A40 'command:' /etc/kubernetes/manifests/kube-apiserver.yaml
   sudo awk '/- --/{print $2}' /etc/kubernetes/manifests/kube-controller-manager.yaml
   sudo awk '/- --/{print $2}' /etc/kubernetes/manifests/kube-scheduler.yaml
   ```

2. Build a three-column table per binary: **flag · `local-up-cluster.sh` · `kubeadm`**. Mark each row `both`, `dev-only`, or `kubeadm-only`.
3. For every `kubeadm-only` row, write the one-word reason. Nearly all of them fall into four buckets — TLS, authentication, authorisation, and the aggregation layer — and the fourth bucket is why [the map](02-what-kubeadm-generated.md) found a third CA.
4. For every `dev-only` row, say what it turned *off*. `--authorization-mode=AlwaysAllow` is the one to sit with: a control plane with no authoriser is still a working control plane, which tells you exactly how much of Kubernetes RBAC is.
5. Find the flags that appear in *neither* list but govern things you already care about — start with the apiserver's `--etcd-servers` and the controller-manager's `--allocate-node-cidrs`, and connect the second one back to [exercise 1](01-provision-and-kubeadm-init.md)'s `--pod-network-cidr`.

**Observe** — the manifests also carry `hostNetwork: true`, `priorityClassName: system-node-critical`, and volume mounts of `/etc/kubernetes/pki` straight off the host. Note what each one implies about how early in the boot these pods must be able to start.

**Expect** — the apiserver diff is the big one and it is almost entirely security; the scheduler diff is nearly empty, which is the honest signal that the scheduler is the same program in both. The controller-manager's extra flags are mostly about *which controllers run* and *what signs what* — `--controllers`, `--cluster-signing-cert-file`, `--use-service-account-credentials`.

**Write down** — the three tables, and one sentence naming the single flag whose absence would most quickly turn this cluster into `local-up-cluster.sh`'s.

**Teardown** — nothing was created. **The topology stays.**
