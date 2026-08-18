<a id="hand-wire-the-control-plane"></a>
# A control plane with no installer under it

**Artifact** — a serving cluster in which every binary was started by you and every certificate was signed by you, plus **the component-and-flag map**: each binary, the flags that connect it to its neighbours, and the cert that authenticates each hop. [The checklist requires the map](../../phases/03-api-machinery.md#checklist); the cluster is where it comes from.

**Rests on** — [P1's flag table](../../phases/01-operate-shallow.md#m1-1), which put `local-up-cluster.sh`'s flags beside kubeadm's. This module is the third column: the flags nobody wrote down for you. And [P2](../../phases/02-etcd.md) is why the etcd half is now typing rather than learning — you have already brought three members up from `--initial-cluster`.

**Topology** — **none.** The iximiuz *Kubernetes the Very Hard Way* module is browser-hosted: it costs this homelab nothing and it runs while nothing at all is provisioned. That is what makes the first week of this phase free, and it is also the constraint — **the playground does not survive the session.** The artifact is the map, not the cluster; write the map as you go, not afterwards.

**Do**

1. Work the iximiuz module end to end, in its own environment. Do not skip the PKI section to reach the interesting part: the PKI *is* the part [module 3.3](../../phases/03-api-machinery.md#m3-3) charges you for later.

2. Keep a running table with one row per **hop**, not per binary. A hop is a client talking to a server, and there are more of them than there are components:

   | Client | Server | Flag on the client that names the server | Flag on the server that trusts the client | Cert presented |
   |---|---|---|---|---|
   | `kube-apiserver` | etcd | `--etcd-servers` | | |
   | `kube-controller-manager` | `kube-apiserver` | `--kubeconfig` | `--client-ca-file` | |
   | `kube-scheduler` | `kube-apiserver` | | | |
   | `kubelet` | `kube-apiserver` | | | |
   | `kube-apiserver` | `kubelet` | `--kubelet-client-certificate` | `--client-ca-file` (kubelet's) | |
   | `kube-proxy` | `kube-apiserver` | | | |

   The row that surprises people is the fifth: **the apiserver is a client too**, and it needs its own cert to reach a kubelet. Nothing works until that direction is signed as well, and `kubectl logs` is the command that reveals it missing.

3. Every time you generate a key or a CSR, write down *which CA signed it* and *what CN and O you gave it*. `O=system:masters` and `O=system:nodes` are not decoration — they are the entire authorisation story for those two credentials, and [the Node authorizer](11-the-node-authorizer-graph.md) is where the second one comes back.

**Observe** — once the cluster serves:

```sh
kubectl get --raw='/healthz?verbose'
kubectl get --raw='/livez?verbose'
kubectl get nodes
kubectl -n kube-system get pods
kubectl run probe --image=busybox --restart=Never -- sleep 3600
kubectl logs probe          # the fifth hop, exercised
```

**Expect** — `/healthz?verbose` prints one line per registered check, and `etcd ok` is the one that fails first when `--etcd-servers` is wrong. A cluster can pass `kubectl get nodes` and still fail `kubectl logs` with `x509: certificate signed by unknown authority` — that is the apiserver→kubelet hop, and it is the hop most hand-wiring guides get to last.

The usual first failure is not a cert at all: it is `kubectl get nodes` returning an empty list because the kubelet is running and has never successfully registered. Read the kubelet's own log before touching the apiserver.

**Write down** — the completed hop table, and separately: **the one flag whose purpose you could not state in a sentence.** [The next exercise](02-every-flag-located-in-source.md) is where you go and find it in source, and starting from a flag you genuinely could not explain is worth more than starting from one you could.

**Footprint note** — zero. Nothing is provisioned, and [`forge`](../../strands/lab-topologies.md#build-guest) is the only guest involved in this whole module — it holds the clone [the next exercise](02-every-flag-located-in-source.md) makes.

**Teardown** — nothing of yours exists in the homelab to delete. The playground expires on its own; **no topology comes up in this exercise or the three after it**, and the first provision of the phase is [the webhook the apiserver dials](18-the-webhook-the-apiserver-dials.md).
