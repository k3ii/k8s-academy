<a id="b01"></a>
# B1 — Prepare the host, `kubeadm init`, join a worker. From nothing.

**Build** · **Pinned** · **60 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Cluster Architecture, Installation and Configuration / Prepare infrastructure · Create clusters with kubeadm

> **This is the only build that destroys what every other object needs.** It cannot be rehearsed on a running cluster, which is why [the plan](../../plan.md#calendar) scheduled it for Tue 29 Sep and then found it had nothing to do: `pair` had already been up for four weeks. It runs for real **after a topology switch**, when the cluster is being rebuilt anyway, and at no other time.

**Do**

The exam does not ask you to install a cluster from bare metal, but it does ask you to fix a node that was installed wrong, and you cannot recognise wrong without having done right once.

1. **Host preparation, and know why each step exists.** Swap off, and permanently. The `overlay` and `br_netfilter` modules. The three sysctls — `net.ipv4.ip_forward` and the two `bridge-nf-call-*` — which exist so that a bridged packet is seen by iptables, which is how Services work at all. Skipping any one of these produces a cluster that comes up and then fails to route, which is the hardest class of fault to attribute afterwards.
2. **The runtime.** containerd with `SystemdCgroup = true`, matching the kubelet's `cgroupDriver: systemd`. A mismatch here is the classic install fault: pods start and are then killed in ways that look like resource pressure.
3. **The packages.** The `pkgs.k8s.io` repo is pinned to one **minor** version by its URL, and the three packages are then `apt-mark hold`ed. Understand both halves: the pin decides what you *can* install, the hold decides what an unattended upgrade cannot do to you at three in the morning.
4. **`kubeadm init`.** Pick the pod CIDR to match the CNI you intend to install, not the other way round. Read the output properly — it prints the join command, the admin kubeconfig path, and the CNI step it is deliberately not doing for you.
5. **The CNI, then the worker.** Nodes stay `NotReady` until a CNI is installed, and a `NotReady` control plane immediately after `init` is expected rather than broken. Join the worker and watch it go `Ready`.

**Observe**

```sh
sudo swapon --show                      # expect no output
lsmod | grep -E 'overlay|br_netfilter'
sysctl net.ipv4.ip_forward net.bridge.bridge-nf-call-iptables
sudo kubeadm init --pod-network-cidr=<cidr> --apiserver-advertise-address=<ip>
kubectl get nodes                       # NotReady is correct, until the CNI
kubectl -n kube-system get pods -o wide
sudo kubeadm token create --print-join-command
```

**Done when** — two `Ready` nodes, every `kube-system` pod running, and a pod on the worker can reach a Service backed by a pod on the control plane.

**Done in one sitting.** If it overruns, the cluster must still end the night usable; an abandoned half-init is a worse starting state than the one you began with.

**Teardown** — none; this *is* the cluster. [The baseline](../../baseline.md#rebuild) is the mark scheme — it records what a correct result looks like on this hardware, down to the module list and the sysctl values, so diff against it rather than trusting the absence of errors.

**See also** — **B2** upgrades what this builds, and **TS1** is the ladder you climb when one of these steps was skipped by someone else.
