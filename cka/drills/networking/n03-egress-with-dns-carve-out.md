<a id="n03"></a>
# N3 — An egress policy, including the DNS carve-out it will not work without

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Servicing and Networking / Network Policies

> **Write the egress policy first and watch everything break.** The first egress rule you apply to a namespace is also the first thing that stops DNS, because resolving a name *is* egress — to `kube-system`, on port 53 — and nothing about the symptom says so. The carve-out is the drill; the policy is the setup.

> **Enforcement is not free on this cluster.** The CNI is Flannel, which does not implement NetworkPolicy at all, so a policy applied to a bare Flannel cluster is accepted by the API server and enforced by nobody. Enforcement here comes from the `kube-network-policies` DaemonSet in `kube-system`. **Confirm it is running before you conclude a policy works** — a policy that appears to allow everything may simply be unenforced.

**Do**

1. Two pods in a namespace: a client and a server. Confirm the client can reach the server by name, and can reach something outside the cluster.
2. Apply an egress policy allowing only the server's `podSelector`. Re-test. The in-namespace call by **IP** still works; the call by **name** does not, and neither does anything external.
3. Read the failure correctly before fixing it. It is a DNS timeout, not a connection refusal, and the distinction is the whole diagnosis.
4. Add the carve-out: egress to the `kube-system` namespace on port 53, **both `UDP` and `TCP`**. Most people allow UDP only; it works until a response exceeds 512 bytes and the resolver retries over TCP, and then it fails intermittently, which is far worse than failing outright.
5. Re-test all three paths. Then check the policy's shape: `policyTypes: [Egress]` with an empty `egress: []` is deny-all egress, and is a different object from one with no `policyTypes` at all.

**Observe**

```sh
kubectl -n kube-system get ds kube-network-policies
kubectl get netpol -o yaml
kubectl exec client -- nslookup server
kubectl exec client -- wget -qO- --timeout=3 http://<server-cluster-ip>
kubectl exec client -- wget -qO- --timeout=3 http://server
```

**Done when** — the client resolves names and reaches the server, reaches nothing else, and you can write the carve-out from memory including both protocols.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean namespace. Build both pods, break DNS, fix it. | 10 min |
| **2** | A namespace with an ingress policy already in it. Egress and ingress are independent and you must not fix one by editing the other. | 8 min |
| **3** | Cold, no notes, clock visible. Whole thing from scratch. | 5 min |

**Teardown** — delete the namespace. Leave `kube-network-policies` alone; it is a fixture.

**See also** — [TS17](../troubleshooting/ts17-a-policy-you-did-not-write.md) is this same object from the other side: the policy is already in place, you did not write it, and the task is proving the drop is the policy and not the app.
