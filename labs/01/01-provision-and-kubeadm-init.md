<a id="provision-and-kubeadm-init"></a>
# A two-node cluster, stood up by hand

**Artifact** — a `pair` cluster you built with `kubeadm init`, `kubeadm join` and one CNI manifest, both nodes `Ready`, plus the full terminal transcript of all three steps kept for [the map](02-what-kubeadm-generated.md).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), provisioned per [the five steps](../../strands/lab-topologies.md#provision). This is P1's first exercise and the first thing in the phase that costs RAM; [`bare`](../../strands/lab-topologies.md#bare) from P0 is gone by [its last exercise](../00/22-find-your-container-in-config-json.md).

**Setup** — the provisioning commands are [in the strand](../../strands/lab-topologies.md#provision) and are not repeated here. Two things about them bite on the first run: `ssh hopper` is mandatory and `just gate <node>` is not optional. Note also that [Kubernetes is not on the node when the five steps finish](../../strands/lab-topologies.md#node-baseline) — putting it there is step 1 below, and it is yours to do rather than `factory`'s. That note applies to every exercise in this directory and is stated there once.

**Do**

1. **Put Kubernetes on both nodes yourself.** The five provisioning steps end at a configured Debian guest with no container runtime and no `kubeadm`; [the strand carries the commands](../../strands/lab-topologies.md#node-baseline-steps), and [why they are yours to run](../../strands/lab-topologies.md#node-baseline). Do `.130` and `.131` both, before anything below.

   Two of those lines are for reading rather than pasting, and both are edits to `/etc/containerd/config.toml`. `SystemdCgroup = true` fails loudly — the kubelet reports the node `NotReady` and names the cgroup driver. `bin_dir = "/opt/cni/bin"` fails silently, and not until step 5: the node reaches `Ready` and no pod ever starts. Note which of the two you would have caught.

2. On `.130`, initialise the control plane:

   ```sh
   sudo kubeadm init \
     --pod-network-cidr=10.244.0.0/16 \
     --apiserver-advertise-address=10.10.10.130 \
     | tee ~/kubeadm-init.log
   ```

   `--pod-network-cidr` is not decoration — Flannel reads it from the Node object's `podCIDR`, which the controller-manager only allocates because you passed it here. Getting it wrong produces a cluster where every pod is `ContainerCreating` forever, and the error names neither flag.

3. **Read the last twenty lines of that output before doing what they say.** `kubeadm` prints three things: the `mkdir -p $HOME/.kube` incantation, a CNI reminder, and a `kubeadm join` line carrying a token and a CA cert hash. Copy the join line somewhere; the token expires in 24 hours and `kubeadm token create --print-join-command` is how you get another.
4. `kubectl get nodes` before installing any CNI. The node is `NotReady`, and `kubectl describe node` says why in one condition. Write the exact message down — it is the most common "broken cluster" in the CKAD/CKA world and it is not broken.
5. Install **Flannel**, one manifest, and watch the node flip to `Ready`.
6. On `.131`, run the join line under `sudo`. Then, back on `.130`, watch the second node register and go `Ready`.
7. Deliberately break a join and read the error: run `kubeadm join` again on `.131` with one character of the `--discovery-token-ca-cert-hash` changed. It refuses, and the refusal is the whole reason that hash is in the line.

**Observe**

```sh
kubectl get nodes -o wide
kubectl get pods -A
kubectl get node <worker> -o jsonpath='{.spec.podCIDR}{"\n"}'
```

**Expect** — five namespaces' worth of pods in `kube-system` and nothing else; two `podCIDR` allocations that do not overlap; a worker that has no `/etc/kubernetes/manifests` content of its own. The step-7 join fails at *discovery*, before any TLS bootstrap, with a message about the CA hash not matching — the cluster refused to be joined by a node that could not prove which cluster it was talking to.

**Write down** — the `NotReady` condition message from step 4 verbatim, and one sentence on why the CNI, not the kubelet, satisfies it.

**Footprint note** — **Flannel, not Cilium.** The [module](../../phases/01-operate-shallow.md#m1-1) offers either and calls the choice thin. On [`pair`](../../strands/lab-topologies.md#pair) it is not thin: a Cilium agent per node costs more RAM than MetalLB and ingress-nginx together, both of which arrive at [exercise 14](14-four-ways-to-expose.md), and the eBPF datapath it buys is a [P7](../../phases/07-networking.md) subject that P1 is explicitly forbidden to descend into. Flannel is the smallest thing that satisfies the CNI dependency. This is the smallest change to the plan, not a softening of it — nothing in P1 reads the CNI.

**Teardown** — nothing to delete; this exercise only created the cluster. **The topology stays.** Exercises 2 through 23 all run on it, and [a provision costs minutes](../../strands/lab-topologies.md#teardown) each time.
