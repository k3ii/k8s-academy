<a id="the-capstone-trace"></a>
# The capstone: a pod dies, and a Service stops sending it traffic — half cited, half owed

**Artifact** — [corpus trace #2](../../strands/source-reading.md#trace-pod-dies) written up end to end: from the container exiting on the worker to the nftables rule disappearing on the other node, with **Area 7 hops carrying `file:line` a hostile reader could check**, and the far half carrying live evidence plus an explicit statement of which citations are owed to [P7](../../phases/07-networking.md).

**Rests on** — [relist](03-relist-and-the-threshold-it-checks.md) for the first hop and [`syncLoopIteration`](24-one-hundred-lines-of-select.md) for the machinery around it. [The phase's capstone section](../../phases/06-kubelet-node.md#capstone) sets the split and the standard; this file is how you produce the evidence.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued and for the last time. **This exercise destroys it.**

**Setup** — a Service with two endpoints on two nodes, so that losing one is visible as a change rather than as an outage:

```sh
kubectl create ns trace
kubectl -n trace create deployment web --image=registry.k8s.io/e2e-test-images/agnhost:2.47 --replicas=2 -- /agnhost netexec --http-port=8080
kubectl -n trace expose deployment web --port=8080
kubectl -n trace get pods -o wide
kubectl -n trace get endpointslice -o wide
```

Capture the "before" on **the node that is not running the victim** — the rules you are about to watch change are programmed there:

```sh
ssh zain@10.10.10.130 'sudo nft list ruleset > /tmp/before.nft; grep -c . /tmp/before.nft; grep -n "<victim pod IP>" /tmp/before.nft'
```

**Do** — kill one container in a way that produces a clean single event, and timestamp everything:

```sh
ssh zain@10.10.10.131 'date +%T.%N; sudo crictl stop --timeout 0 <the victim container id>'
```

Then collect, in this order, with timestamps:

```sh
ssh zain@10.10.10.131 'sudo journalctl -u kubelet -o short-precise --since "-2 min" | grep -i -e pleg -e "container died" -e status'
kubectl -n trace get pod <victim> -o jsonpath='{.status.containerStatuses[0].state}{"\n"}'
kubectl -n trace get endpointslice -o json | jq '.items[].endpoints[] | {addresses, conditions}'
ssh zain@10.10.10.130 'sudo nft list ruleset > /tmp/after.nft; diff /tmp/before.nft /tmp/after.nft'
```

**The six hops, and what each one owes you:**

| Hop | Evidence required |
|---|---|
| The container exits; the runtime records it | `crictl` state, and the timestamp |
| `relist` notices and emits `ContainerDied` | **`file:line` in `pleg/generic.go`** for the emission, plus the kubelet log line |
| The status manager writes the new pod status to the API server | **`file:line` in `status_manager.go`** for the version bookkeeping — the check that stops it writing a status older than one already sent |
| The EndpointSlice reconciler removes the endpoint | `kubectl get endpointslice` before and after. **Citation owed to P7.** |
| `kube-proxy`'s change tracker picks up the watch event | the proxy's log or metrics on `.130`. **Citation owed to P7.** |
| `syncProxyRules` reprograms nftables | the `diff` between your two rule dumps. **Citation owed to P7.** |

**Expect** — the whole path to complete in a second or two, and the `diff` to be small and specific: the victim's address gone from one map or verdict chain, everything else unchanged. That small diff is the entire argument that a Service is a set of rules and not a process.

Expect the status manager's version check to be the hop that is genuinely worth the reading: it is what stops a slow status write from resurrecting a stale endpoint after a fast one has already removed it, and it is invisible from outside until it fails.

Expect to be unable to cite the last three hops honestly, **and expect that to be the correct outcome.** Write them as observed facts with the citation marked as owed, name `kubelet-cri-networking.md` as the seam, and say in one line what P7 has to produce for each. A trace that admits its boundary is worth more than one that guesses across it — and P7 opens by paying exactly these three debts.

**Write down** — the six-hop trace with timestamps, two source citations, three pieces of live evidence, three named debts. [The phase's gate](../../phases/06-kubelet-node.md#gate) is whether this survives a hostile reader, so every claim in it should be one you could re-produce on demand.

Commit the write-up:

```sh
ssh zain@10.10.10.125 'cd ~/src/k8s-academy && git add -A && git commit -m "P6 capstone: trace #2" && git push'
```

**Footprint note** — two small pods and two rule dumps. Nothing about the capstone is tight; the phase's pressure was all in [module 6.6](25-the-stack-that-must-not-be-evicted.md) and it is behind you.

**Teardown** — [the standard way](../../strands/lab-topologies.md#teardown), `just tofu labs destroy`. **The topology goes**, and with it Chaos Mesh and the monitoring stack — both are re-installed from their charts when a later phase wants them, which is why neither was ever uninstalled by hand.

Confirm the phase left nothing behind:

```sh
ssh hopper 'qm list'                       # forge at 1536MB, nothing else running
ssh zain@10.10.10.125 'free -m; df -h /'
```

`forge` is untouched by this phase — no resize was needed, because [there is no build artifact here](../../phases/06-kubelet-node.md) and nothing was linked. It goes into [P7](../../phases/07-networking.md) exactly as it arrived.
