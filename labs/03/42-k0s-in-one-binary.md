<a id="k0s-in-one-binary"></a>
# One binary, four components, no manifests you wrote

**Artifact** — a serving k0s control plane on a fresh guest, plus a process tree and a table mapping each component you hand-started in [module 3.1](05-hand-start-an-apiserver.md) to where it now lives and what supervises it.

**Rests on** — [the hand-started apiserver](05-hand-start-an-apiserver.md) and the whole of [module 3.0](01-hand-wire-the-control-plane.md). The contrast only lands because you did those first, which is [why the phase orders them this way](../../phases/03-api-machinery.md#m3-6).

**Topology** — [`k0s-light`](../../strands/lab-topologies.md#k0s-light), provisioned fresh. The [`pair`](../../strands/lab-topologies.md#pair) cluster was destroyed at [the end of module 3.5](41-3c5-an-expired-component-certificate.md); provision per [the strand](../../strands/lab-topologies.md#provision). A baselined guest has no container runtime on it and step 1 does not need one: k0s ships its own.

**Do**

1. Install and start it. Time yourself from first command to serving cluster, and compare against the time [module 3.0](01-hand-wire-the-control-plane.md) took:

   ```sh
   curl -sSLf https://get.k0s.sh | sudo sh
   sudo k0s install controller --single
   sudo k0s start
   sudo k0s status
   sudo k0s kubectl get nodes
   ```

2. Before reading any k0s documentation, look at the process tree and work out the architecture from it:

   ```sh
   ps -ef --forest | sed -n '/k0s/,$p'
   sudo ls -l /var/lib/k0s/bin/
   sudo ss -ltnp | grep -E '2379|2380|6443|10257|10259'
   ```

   The `bin` directory is the answer to the question the phase's ecosystem note poses: are the components *gone*, or *hidden*?

3. Build the mapping table. For each of `kube-apiserver`, `kube-controller-manager`, `kube-scheduler`, `etcd`:

   | Component | Separate process? | Parent | Config you would have written | Where k0s put that config |
   |---|---|---|---|---|
   
   Find the last column by looking, not by guessing: `sudo find /var/lib/k0s -name '*.yaml' -o -name '*.conf' | head -40`, and `sudo k0s config create` to see the full default with everything it did not make you decide.

4. Ask what happened to the certificates. You signed every one of them by hand in [module 3.0](01-hand-wire-the-control-plane.md) and [exercise 17](17-a-ca-and-a-serving-cert-by-hand.md):

   ```sh
   sudo ls -l /var/lib/k0s/pki/
   sudo openssl x509 -in /var/lib/k0s/pki/apiserver.crt -noout -subject -ext subjectAltName -dates
   ```

   Compare the SAN list against the one you had to reason out by hand. Note what it included that you would have forgotten.

5. Find the supervision. In the k0s source — clone it on the guest or read it on [`forge`](../../strands/lab-topologies.md#build-guest) — locate the supervisor type that starts these as child processes and answer: what does it do when a child exits, and does it have a backoff? Cite `file:line`.

6. Run a workload, to confirm this is a real cluster and not a demo:

   ```sh
   sudo k0s kubectl create deploy web --image=nginx --replicas=2
   sudo k0s kubectl get pods -o wide
   ```

**Observe** — the process tree above all. Then:

```sh
sudo k0s kubectl get pods -n kube-system
sudo journalctl -u k0scontroller -n 50
```

**Expect** — `kube-system` contains coredns, kube-proxy and a CNI, and **no control-plane pods at all**. There is no `/etc/kubernetes/manifests`. The components you have spent a month starting by hand are child processes of one supervisor, visible in `ps` and invisible to the API. A learner who arrived at k0s first would conclude the control plane is a single program; you can say it is four programs with the seams pre-configured, and you can point at `/var/lib/k0s/bin` to prove it.

The SAN comparison in step 4 usually produces one entry you would have missed. Write down which.

**Footprint note** — 2.0GB of [the 9.5GB ceiling](../../strands/lab-topologies.md#ceiling), the cheapest topology in the phase, and it is the only thing running: `pair` is gone and [`forge`](../../strands/lab-topologies.md#build-guest) is idle. If `forge` is still at the 2560MB [module 3.1](05-hand-start-an-apiserver.md) raised it to, that is fine here and nothing needs changing — but note that the phase's peak was module 3.3, not this.

**Teardown** — delete the Deployment. **The topology stays** — [killing the process](43-kill-the-one-process.md) needs exactly this cluster.
