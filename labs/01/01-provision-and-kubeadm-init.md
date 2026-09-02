<a id="provision-and-kubeadm-init"></a>
# A two-node cluster, stood up by hand

**Artifact** — a `pair` cluster that you build by hand. You build it with `kubeadm init`, `kubeadm join` and one CNI manifest. Both nodes reach `Ready`. Keep the full terminal transcript of all three steps, because [the map](02-what-kubeadm-generated.md) needs it.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair). Provision it with [the five steps](../../strands/lab-topologies.md#provision). This is the first exercise of P1. It is also the first item in the phase that costs RAM. [`bare`](../../strands/lab-topologies.md#bare) from P0 is already gone, because P0 destroys it in [its last exercise](../00/22-find-your-container-in-config-json.md).

**Setup** — the provisioning commands are [in the strand](../../strands/lab-topologies.md#provision), and this exercise does not repeat them. Two of those commands bite you on the first run. First, `ssh hopper` is mandatory. Second, `just gate <node>` is not optional. Note one more fact: [Kubernetes is not on the node when the five steps finish](../../strands/lab-topologies.md#node-baseline). You put it there in step 1 below. That work is yours to do, and not `factory`'s. The same note applies to every exercise in this directory, and the directory states it once, here.

**Do**

1. **Put Kubernetes on both nodes yourself.** The five provisioning steps end at a configured Debian guest. That guest has no container runtime and no `kubeadm`. [The strand carries the commands](../../strands/lab-topologies.md#node-baseline-steps). It also explains [why they are yours to run](../../strands/lab-topologies.md#node-baseline). Do this on `.130` and on `.131`, and do it before anything below.

   Three things in that procedure are worth reading rather than pasting. Two of them can still bite you. The third used to, and the way it was fixed is the interesting part:

   - **The containerd tarball fails loudly, and it fails first.** Reach for `apt-get install -y containerd` instead, and step 2 below prints a `RuntimeConfig` warning at you. Do the same thing one minor version later and step 2 refuses to run at all. [The strand carries the whole story](../../strands/lab-topologies.md#node-baseline-steps), and the short version is that Debian's containerd is a dead end and was never going to stop being one.
   - **`SystemdCgroup = true` fails loudly, and it fails late.** The kubelet reports the node as `NotReady`, and it names the cgroup driver.
   - **The CNI plugin directory used to fail silently, and now it does not.** The old baseline pointed containerd at `/usr/lib/cni` while the plugins sat in `/opt/cni/bin`, and the node reached `Ready` before a single pod could start. Upstream containerd and `kubernetes-cni` agree on that directory without being told, so this one is a failure you have inherited the fix for rather than one you can still cause. Read [why it cost ten minutes anyway](../../strands/lab-topologies.md#node-baseline-steps), and keep the shape: a node whose own success signal fires before the thing that matters works.

   Note which of the three you would have caught.

2. On `.130`, initialise the control plane. Pull the images first, in their own command:

   ```sh
   sudo kubeadm config images pull

   sudo kubeadm init \
     --pod-network-cidr=10.244.0.0/16 \
     --apiserver-advertise-address=10.10.10.130 \
     | tee ~/kubeadm-init.log
   ```

   The first command is not an optimisation, and skipping it teaches you nothing. `kubeadm init` prints nothing at all between `This might take a minute or two` and the `[certs]` phase, for as long as the pull runs. Through a `tee`, those minutes are indistinguishable from a hang, and you will reach for `Ctrl-C` at the exact moment the tool is working correctly. `kubeadm` names this command itself, in the line printed just before the silence starts. Take it at its word.

   `--pod-network-cidr` is not decoration. Flannel reads the value from the `podCIDR` field of the Node object. The controller-manager allocates that field only because you passed the flag here. A wrong value gives you a cluster in which every pod stays in `ContainerCreating` forever. The error message names neither flag.

3. **Read the last twenty lines of that output before you do what they say.** `kubeadm` prints three things:

   - the `mkdir -p $HOME/.kube` incantation;
   - a reminder to install a CNI;
   - a `kubeadm join` line that carries a token and a CA cert hash.

   Copy the join line somewhere safe. The token expires after 24 hours. To get another one, run `kubeadm token create --print-join-command`.

4. Run `kubectl get nodes` before you install any CNI. The node is `NotReady`. `kubectl describe node` says why, in one condition. Write the exact message down. This is the most common "broken cluster" in the CKAD and CKA world, and the cluster is not broken.
5. Install **Flannel**. It is one manifest. Watch the node flip to `Ready`.
6. On `.131`, run the join line under `sudo`. Then go back to `.130`. Watch the second node register and reach `Ready`.
7. Break a join deliberately, and read the error. Run `kubeadm join` again on `.131`, but change one character of the `--discovery-token-ca-cert-hash` value. The join refuses. That refusal is the whole reason why the hash is in the line.

**Observe**

```sh
kubectl get nodes -o wide
kubectl get pods -A
kubectl get node <worker> -o jsonpath='{.spec.podCIDR}{"\n"}'
```

**Expect** — five namespaces exist, and all of the pods sit in `kube-system`. You also see two `podCIDR` allocations, and they do not overlap. The worker has no `/etc/kubernetes/manifests` content of its own. The join in step 7 fails at *discovery*, before any TLS bootstrap, and the message says that the CA hash does not match. Read that failure as follows: the cluster refused a node that could not prove which cluster it was talking to.

**Write down** — the `NotReady` condition message from step 4, word for word. Then write one sentence. The sentence explains why the CNI satisfies that condition, and not the kubelet.

**Footprint note** — **use Flannel, and not Cilium.** The [module](../../phases/01-operate-shallow.md#m1-1) offers either one and calls the choice thin. On [`pair`](../../strands/lab-topologies.md#pair) the choice is not thin, for two reasons. First, one Cilium agent per node costs more RAM than MetalLB and ingress-nginx together, and both of those arrive at [exercise 14](14-four-ways-to-expose.md). Second, Cilium buys you the eBPF datapath, and that datapath is a [P7](../../phases/07-networking.md) subject that P1 must not descend into. Flannel is the smallest thing that satisfies the CNI dependency. This is the smallest change to the plan, and it is not a softening of the plan: nothing in P1 reads the CNI.

**Teardown** — there is nothing to delete, because this exercise only created the cluster. **The topology stays.** Exercises 2 through 23 all run on it, and [a provision costs minutes](../../strands/lab-topologies.md#teardown) each time.
