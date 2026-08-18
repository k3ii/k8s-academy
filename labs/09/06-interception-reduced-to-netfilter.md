<a id="interception-reduced-to-netfilter"></a>
# Interception reduced to netfilter: four chains inside one pod, and every port in them is an `istio-init` arg

**Claim** — the whole of "the mesh captured the traffic" is **four chains in the `nat` table of one pod's network namespace**, and every number in them was passed to `istio-init` on its command line. Inbound arrives on a redirect to **15006**, outbound on a redirect to **15001**, and a handful of ports are exempted so that the proxy's own management traffic is not captured by the proxy. This is [module 9.2's reading question](../../phases/09-service-mesh.md#m9-2) and the first half of [the capstone](25-one-request-both-halves.md).

**Rests on** — [the injected pod](05-a-pod-the-webhook-rewrote.md), whose `istio-init` container is the thing that wrote these rules and then exited.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — the args first, so the rules are read against a prediction:**

```sh
kubectl -n mesh get pod -l app=httpbin -o jsonpath='{.items[0].spec.initContainers[0].args}'; echo
kubectl -n mesh get pod -l app=httpbin -o wide
```

**Do — part 1, try the obvious thing and watch it fail.** The rules are in the pod, so `exec` into the pod ought to show them:

```sh
kubectl -n mesh exec deploy/httpbin -c istio-proxy -- iptables-save
```

**Do — part 2, read them from the node instead.** The netns belongs to the pod; the capability to read its tables does not. Both workloads are on the worker — the control plane is tainted and only [`istiod` tolerates it](04-the-request-that-does-not-fit.md) — so `.131` is where you go, once you have confirmed it:

```sh
kubectl -n mesh get pod -l app=httpbin -o jsonpath='{.items[0].spec.nodeName}'; echo   # expect the worker
ssh zain@10.10.10.131 'sudo crictl ps -q --label io.kubernetes.container.name=istio-proxy'
PID=$(ssh zain@10.10.10.131 'sudo crictl inspect $(sudo crictl ps -q --label io.kubernetes.container.name=istio-proxy) | jq -r .info.pid')
ssh zain@10.10.10.131 "sudo nsenter -t $PID -n iptables-save -t nat"
ssh zain@10.10.10.131 "sudo nsenter -t $PID -n ss -ltnp"
```

**Observe — map each rule to the arg that produced it.** Fill this from your own output; the table is the module's written deliverable and the answers are not to be copied from anywhere:

| `istio-init` arg | The rule it produced | Chain it lives in |
|---|---|---|
| `-p 15001` | | |
| `-z 15006` | | |
| `-u 1337` | | |
| `-m REDIRECT` | | |
| `-b '*'` | | |
| `-d 15090,15021` | | |
| `-i '*'` / `-x ''` | | |

**Expect** — part 1 to **fail**, with a permission error rather than an empty ruleset. `istio-proxy` runs as UID 1337 with no `NET_ADMIN`: the rules are in its namespace and it cannot list them, which is exactly the property that makes them hard for a compromised sidecar to rewrite. `istio-init` had the capability, used it once, and exited — check that with `kubectl -n mesh get pod -l app=httpbin -o jsonpath='{.items[0].status.initContainerStatuses[0].state}'`.

Expect four chains and two jump targets in part 2: **`ISTIO_INBOUND`** hooked from `PREROUTING`, **`ISTIO_IN_REDIRECT`** doing the `REDIRECT --to-ports 15006`, **`ISTIO_OUTPUT`** hooked from `OUTPUT`, and **`ISTIO_REDIRECT`** doing the `REDIRECT --to-ports 15001`. Inbound is captured before routing because the packet is arriving for someone else; outbound is captured in `OUTPUT` because the packet was generated locally, and that difference in hook is the reason there are two chains rather than one.

Expect `ISTIO_INBOUND` to `RETURN` — not redirect — for **15008, 15090, 15021 and 15020** before its catch-all jump. Those are the proxy's own ports: tunnel, Prometheus telemetry, health status and the agent. A rule set that captured them would send the kubelet's health probe into the proxy that the probe exists to check. Expect `ISTIO_OUTPUT` to be the longer chain, with `RETURN`s for loopback traffic, for a source of **`127.0.0.6`**, and for anything owned by **UID/GID 1337** — the last of which is [the loop-breaker you will remove in the next exercise](07-the-uid-that-breaks-the-loop.md).

**Expect `iptables-save` to possibly show nothing, and for that not to mean the rules are absent.** If the chains are missing, you are reading the wrong backend: the rules were written through whichever of `nft` or `legacy` `istio-init` detected, and the node's `iptables-save` may default to the other. Try `iptables-nft-save` and `iptables-legacy-save` in the same `nsenter` before concluding anything. This is the same split that decides how a kube-proxy ruleset is read in [P7](../../phases/07-networking.md), reached from the other direction.

Expect `ss -ltnp` inside the netns to show Envoy listening on **15001, 15006, 15020, 15021 and 15090** — the redirect targets exist, which is the difference between a `REDIRECT` rule and a black hole.

**Write down** — the completed arg-to-rule table with your own rule lines pasted in, and the four chain names with their hooks, in `journal/p9-interception.md`. Add one sentence naming what would happen to the pod's traffic if `istio-init` had run and Envoy had **not** started: the rules do not depend on the process being alive, and that asymmetry is worth stating before [the exercise that removes a rule](08-9c1-a-port-outside-the-mesh.md) and [the one that kills the control plane](14-9c3-istiod-killed-and-the-planes-come-apart.md).

**Teardown** — nothing created; every command above is a read. Leave the `nsenter` session, and keep the PID you looked up only as a note — it is invalid the moment the pod restarts, and several later exercises restart it.

**The topology stays.**
