<a id="seam-a-client-apiserver-etcd"></a>
# Seam A: the create from `kubectl` to an etcd `Txn`, cited at every arrow — and the key it landed under, read back out of etcd

**Artifact** — the sub-path `kubectl → endpoints/filters/* → handlers/create.go → admission chain → registry/generic/registry/store.go → storage/etcd3/store.go → etcd Txn`, with a `file:line` at a stated commit sha on **every arrow**, plus the raw etcd key the object landed under, read back out of etcd directly with the P2 skill. This is two areas — [Area 2](../../strands/source-reading.md#area-2-api-machinery) (P3) and [Area 1](../../strands/source-reading.md#area-1-etcd) (P2) — read as one continuous handoff, not two subsystems.

**Rests on** — [the paper map](01-the-paper-trace-before-the-cluster.md), whose Seam-A guesses this either confirms or corrects in red; [P3's handler-chain trace](../../phases/03-api-machinery.md#m3-1), where `create.go`'s call order was first read; and [P2's read-it-back-out-of-etcd skill](../../phases/02-etcd.md#m2-1), which turns "it was persisted" into a key you can point at.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair) comes up here, the first live RAM of the phase. Provision it [the standard way](../../strands/lab-topologies.md#provision); it stays up through [the joined trace](07-the-joined-trace-terminal-to-container.md).

**Read** — [the module framing](../../phases/11-synthesis.md#m11-2). The mechanics are not restated here — [P3 module 3.1](../../phases/03-api-machinery.md#m3-1) has the admission-ordering rule and the `create.go` call sequence; this exercise only asks you to cite them against a live create and then read the object back out of etcd. Live-verify every path before trusting it — [the tree moves](../../strands/source-archaeology.md#stale-paths).

> **Question to answer from the source:** `handlers/create.go` runs admission *before* the object reaches `registry/generic/registry/store.go`. Cite the line where admission is invoked and the line in `storage/etcd3/store.go` where the object becomes an etcd `Txn` — then state what guarantees the object is validated *before* it is durable, not after. That ordering is the claim [exercise 3](03-11c1-wedge-a-create-at-admission.md) breaks to prove.

**Build** — create the pod, then trace the create live: watch it arrive through the filters and `create.go`, confirm admission fired, and read the key back out of etcd directly so "persisted" is a key, not a belief. Record the sha you read at. Cite each arrow.

```sh
kubectl run nginx --image=nginx --restart=Never
# read the object back out of etcd directly — the P2 skill, not `kubectl get`
CP=10.10.10.130
ssh zain@$CP 'sudo ETCDCTL_API=3 etcdctl \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get /registry/pods/default/nginx --keys-only'
```

**Verify from outside** — a hostile reader clones `k/k` at your stated sha, opens each cited line, and finds admission invoked *above* the `store.Create` call and the `Txn` assembled in `etcd3/store.go`. "The apiserver validates it" fails the gate; `create.go:NNN` and `etcd3/store.go:NNN` at `abc123` pass. The etcd key is the artifact's second half: it proves the write landed where the citation says it would.

**Expect** — the object under `/registry/pods/default/nginx`, and a citation chain in which admission strictly precedes durability. If you cannot find the admission-invoke line above the store call, Seam A did not land in P3 — [go back to that phase, not forward](../../phases/11-synthesis.md#gate).

**Write down** — the `kubectl → filters → create.go → admission → store.go → etcd3/store.go → Txn` sub-path with a cited line at each arrow, the sha, and the raw etcd key. This is the first third of [the joined trace](07-the-joined-trace-terminal-to-container.md).

**Footprint note** — [`pair` at 5.0GB](../../strands/lab-topologies.md#pair), well inside [the 9.5GB ceiling](../../strands/lab-topologies.md#ceiling); it carries the whole trace half of the phase.

**Teardown** — delete the pod (`kubectl delete pod nginx`); its etcd key is recorded and [Seam B](04-seam-b-watch-cache-scheduler-binding.md) watches a fresh create so it can see `spec.nodeName` go from empty to set. **The topology stays.**
