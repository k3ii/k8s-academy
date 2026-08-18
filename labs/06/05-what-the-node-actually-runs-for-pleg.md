<a id="what-the-node-actually-runs-for-pleg"></a>
# Which PLEG is on this node, and why the polling loop never leaves

**Claim** — the node you just broke runs the generic, polling PLEG; the evented implementation exists in the same package behind a feature gate, and even when that gate is on the relist loop is still there — as a safety net with a longer period, not as a fallback that is removed once events work.

**Rests on** — [the relist loop](03-relist-and-the-threshold-it-checks.md) and [the failure it produced](04-pleg-is-not-healthy.md). The reason this exercise comes after the break is that the break is the argument for keeping relist.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. One read from the live kubelet, the rest on [`forge`](../../strands/lab-topologies.md#build-guest).

**Read** — KEP-3386 (item 6) with `pkg/kubelet/pleg/evented.go` open beside it, and answer [module 6.1's last question](../../phases/06-kubelet-node.md#m6-1) — why relist is kept once events exist — from two specific places rather than from the KEP's summary:

- the CRI RPC that carries the events (find it in the same `api.proto` you read in [exercise 2](02-one-pod-is-how-many-cri-calls.md)) and what happens to that stream if the runtime restarts;
- the relist period `evented.go` sets when the evented path is active, versus the one `generic.go` uses. The ratio between them is the answer to the question.

**Do** — establish which one is actually running, from the node rather than from the KEP's status field:

```sh
kubectl get --raw /api/v1/nodes/pair-worker/proxy/configz | jq '.kubeletconfig.featureGates'
kubectl get --raw /api/v1/nodes/pair-worker/proxy/metrics | grep -E 'evented_pleg|kubelet_pleg_discard_events'
ssh zain@10.10.10.131 'sudo crictl version -o json | jq ".runtimeName, .runtimeVersion"'
```

Then decide, and say why: is the gate absent from that map because it is off, or because it is on by default and therefore not listed? `configz` reports **only what was set**, so the absence of a key is not an answer. Find the default in the source rather than guessing:

```sh
grep -rn 'EventedPLEG' ~/src/kubernetes/pkg/features/kube_features.go
```

**Expect** — a gate that is off on a stock kubeadm node, the metric for evented events either absent or flat at zero, and a `versioned_generic_pleg` shape to the metrics you already used. Expect the source grep to give you a `featuregate.Alpha` or `featuregate.Beta` marker plus a default, and expect that marker to be the honest answer to "which PLEG is this" — far more reliable than reading a KEP's `implementable`/`implemented` field, which describes upstream's intent and not your node.

The finding worth writing down is the one about the safety net: an event stream is a *stateful* connection to a process that can die, and everything you observed in [exercise 4](04-pleg-is-not-healthy.md) — containerd gone, containers still running, the kubelet's picture frozen — is exactly the state an event-driven kubelet would be left in with no way back. Relist is what re-synchronises reality after the stream lied by omission. That is the same argument as [P4's level-triggered reconcile](../../phases/04-controllers.md#m4-1), arrived at from a completely different direction, and it is worth stating in those words.

**Write down** — which PLEG this node runs and the evidence (not the KEP), the two periods with their `file:line`, and one sentence connecting relist to level-triggered reconciliation. [Module 6.5's `syncLoopIteration`](24-one-hundred-lines-of-select.md) is where the same argument reappears at the top of the kubelet instead of the bottom.

**Teardown** — nothing created. **The topology stays** — [the QoS work](06-three-pods-three-classes.md) is next on it.
