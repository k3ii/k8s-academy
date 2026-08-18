<a id="the-plugin-the-kubelet-calls"></a>
# Stage 2: real pods on the worker, addressed by your allocator

**Artifact** — the worker node `.131` running **your** plugin: `/opt/cni/bin/academy` installed, a conflist that wins the kubelet's discovery order, and `kubectl get pods -o wide` showing pods on that node with addresses out of your subnet while the control plane's pods keep the addresses the stock CNI gave them. Two nodes, two networks, on purpose.

**Rests on** — [exercise 8](08-add-and-del-that-cnitool-accepts.md) and [exercise 9](09-an-ipam-that-does-not-leak.md), both gated. **The three things [exercise 7](07-what-replaces-stage-1.md) said the harness could not test are what this exercise is for**, so do not arrive here with an ungated plugin: a bug that `cnitool` would have caught costs ten seconds there and a node's worth of `ContainerCreating` pods here.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. **The control plane's networking is not touched.** That is the safety property that makes the rest of the phase possible: whatever happens to `.131`, there is always a node whose pod network is known-good, which is what makes [exercise 11](11-two-nodes-two-pod-cidrs-no-route.md) a comparison rather than an outage.

**Setup** — read the two facts the install depends on, rather than assuming either:

```sh
kubectl get nodes -o custom-columns='NAME:.metadata.name,CIDR:.spec.podCIDR,IP:.status.addresses[0].address'
ssh zain@10.10.10.131 'ls -1 /etc/cni/net.d/'
```

The first tells you whether the cluster allocates a per-node pod CIDR (and what the worker's is); the second tells you the filename you have to sort before. If the node has a `podCIDR`, **use it** — your plugin becomes the thing that implements the allocation the control plane already published, which is what a real CNI does. If it does not, pick `10.98.0.0/24` and write down that you have taken over an address space nothing else knows about, because that is a difference [exercise 11](11-two-nodes-two-pod-cidrs-no-route.md) will make you pay for.

**Do**

```sh
cd ~/src/k8s-academy/build/07-cni-academy
GOOS=linux GOARCH=amd64 go build -o /tmp/academy ./cmd/academy
scp /tmp/academy zain@10.10.10.131:/tmp/academy
ssh zain@10.10.10.131 'sudo install -m0755 /tmp/academy /opt/cni/bin/academy'
```

The conflist, named to win:

```sh
ssh zain@10.10.10.131 'sudo tee /etc/cni/net.d/05-academy.conflist >/dev/null' <<'JSON'
{
  "cniVersion": "1.0.0",
  "name": "academy",
  "plugins": [
    { "type": "academy", "bridge": "br-academy",
      "subnet": "10.98.0.0/24", "gateway": "10.98.0.1" },
    { "type": "loopback" }
  ]
}
JSON
ssh zain@10.10.10.131 'sudo cp /opt/cni/lab-bin/loopback /opt/cni/bin/ 2>/dev/null; ls -1 /etc/cni/net.d/'
```

Then make the kubelet use it, by giving it pods to create:

```sh
kubectl create ns mynet
kubectl -n mynet create deployment web --image=registry.k8s.io/e2e-test-images/agnhost:2.47 --replicas=3 -- /agnhost netexec --http-port=8080
kubectl -n mynet get pods -o wide -w
```

**Observe**

```sh
kubectl get pods -A -o wide | awk '{print $1, $2, $7, $8}' | sort -k4
ssh zain@10.10.10.131 'ip -br addr show br-academy; ls -1 /var/lib/cni/academy/academy/; sudo ip netns list | head'
```

**Expect** — the three `agnhost` pods `Running` with addresses in your subnet, one file per pod in your store, and a `br-academy` bridge that did not exist before the first `ADD`. Expect **pod-to-pod on the same node** to work immediately:

```sh
kubectl -n mynet exec deploy/web -- curl -s -m3 -o /dev/null -w '%{http_code}\n' http://<another pod IP>:8080/
```

**Expect exactly one thing to be broken, and expect it not to be broken in your plugin**: nothing can reach these pods from the control-plane node, and they can reach nothing there. That is [exercise 11](11-two-nodes-two-pod-cidrs-no-route.md) and it is a routing fact, not a bug.

**Expect the failure modes here to be the three the harness could not reach**, and it is worth producing at least one deliberately before moving on:

| Provoke it | What the kubelet shows |
|---|---|
| rename the conflist to `99-academy.conflist` and delete a pod | pods get addresses from the *other* CNI again — your plugin is installed, correct, and never called |
| omit `ips` from the result (the [exercise 8](08-add-and-del-that-cnitool-accepts.md) variant) | `Running` pods with an empty `.status.podIP`, and a Service with no endpoints |
| leave the binary at mode `0644` | `ContainerCreating`, and a kubelet event naming the exec failure |

**Verify from outside** — from the *control plane*, which has no route to your subnet, the pods must be reachable by the one path that does not need one:

```sh
kubectl -n mynet port-forward deploy/web 18080:8080 &
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:18080/
kill %1
```

`port-forward` goes through the API server and the kubelet on the node, so it works while `ping` does not — which is a useful thing to have seen once, because it is why "I can reach it with `port-forward`" is never evidence that pod networking is healthy.

**Write down** — the discovery-order fact as a sentence you could hand to somebody debugging a plugin that "does nothing", and the three failure modes above with the symptom each one produces at the API. [The checklist's](../../phases/07-networking.md#checklist) *real pods get a `ping`-able network from your CNI plugin* is satisfied at the end of [exercise 11](11-two-nodes-two-pod-cidrs-no-route.md), not here — here it is `ping`-able within one node.

**Footprint note** — three `agnhost` pods, ~45 MiB, on the worker. The plugin binary is a few MiB on disk. The phase is still at 6.5GB.

**Teardown** — **nothing is torn down.** The plugin stays installed, the namespace stays, and the three pods stay: [exercise 11](11-two-nodes-two-pod-cidrs-no-route.md) needs exactly this state, and [exercise 12](12-a-malformed-result-at-the-cri-seam.md) breaks it deliberately afterwards. **The topology stays.**

Record how to undo it, though, because [exercise 31](31-kube-proxy-replaced-by-map-lookups.md) will need to and by then it will not be fresh:

```sh
# not run now — the undo, written down while it is obvious
# ssh zain@10.10.10.131 'sudo rm /etc/cni/net.d/05-academy.conflist; sudo rm -rf /var/lib/cni/academy'
```
