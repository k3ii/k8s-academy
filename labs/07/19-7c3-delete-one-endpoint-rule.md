<a id="7c3-delete-one-endpoint-rule"></a>
# 7.C3 — one wrong DNAT, one third of the requests failing, and a repair you did not perform

**Artifact** — drill [7.C3](../../phases/07-networking.md#chaos), by hand: a Service that fails for a **predictable fraction** of requests, the specific map entry or rule that causes it named before the symptom is measured, and the time kube-proxy took to undo your edit. By hand rather than through Chaos Mesh because [the phase says so](../../phases/07-networking.md#chaos) and the reason is exact — **the lesson is reading the broken rule**, and a fault injector that hides the rule from you has removed the exercise.

**Rests on** — [exercise 17](17-the-same-service-as-a-verdict-map.md) for the nftables dump and the chain layout, and [exercise 18](18-the-tracker-between-two-syncs.md) for the resync interval this drill has to outlive.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with the `svc` namespace's three-endpoint Service from [exercise 16](16-a-clusterip-followed-to-its-kube-sep.md).

**Do — part 1, predict, before touching anything.** Three endpoints, one broken. Write down: what fraction of connections fail; what the client-side error is; whether `kubectl get endpointslice` shows anything wrong; whether the pod's own probes go red; and what `kubectl describe svc` says. Four of those five have the same answer and it is the answer that makes this drill worth running.

**Do — part 2, break exactly one endpoint.** Find the endpoint chains, pick one, and repoint its DNAT at a port nothing is listening on:

```sh
ssh zain@10.10.10.131
sudo -i
nft -a list table ip kube-proxy | grep -B4 'dnat to' | head -40
```

Note the **handle** of one `dnat to <pod-ip>:8080` rule and the chain it is in, then replace it:

```sh
CH=<the endpoint chain name>; H=<the handle>; IP=<that pod's IP>
nft delete rule ip kube-proxy $CH handle $H
nft add rule ip kube-proxy $CH meta l4proto tcp dnat to $IP:9999
nft -a list chain ip kube-proxy $CH
```

**Observe — part 3, measure the fraction.** Ninety attempts, so that a third is unmistakable and the arithmetic is not a judgement call:

```sh
kubectl -n svc run c --rm -it --restart=Never --image=registry.k8s.io/e2e-test-images/agnhost:2.47 -- \
  sh -c 'ok=0; bad=0; for i in $(seq 1 90); do
           if curl -s -m2 -o /dev/null http://web.svc/hostname; then ok=$((ok+1)); else bad=$((bad+1)); fi
         done; echo "ok=$ok bad=$bad"'
```

And confirm the control plane is unaffected, which is the fact that makes this diagnosable:

```sh
kubectl -n svc get endpointslice -o json | jq -c '.items[].endpoints[]|{ip:.addresses[0],c:.conditions}'
kubectl -n svc describe svc web | tail -5
kubectl -n svc get pods -o wide
```

**Expect** — roughly 30 failures in 90, `Connection refused` rather than a timeout (the DNAT succeeded; the pod refused the port), and **three `Ready` endpoints, a healthy Service, three healthy pods, and no event anywhere.** Every control-plane view of this cluster says the Service is fine. That gap is the drill: the object graph describes intent and the rule set describes behaviour, and only one of them is what the packet meets.

Expect a timeout instead of a refusal if you point the DNAT at a *different address* rather than a different port, and expect that difference to be worth one line in the write-up — refused means something answered, timed out means nothing did, and on a datapath fault that is the first fork in the diagnosis.

**Do — part 4, the repair you do not perform.** Wait, and watch:

```sh
date +%T; nft -a list chain ip kube-proxy $CH
# wait, checking every 10s
date +%T; nft -a list chain ip kube-proxy $CH
```

**Expect the rule to come back on its own**, within the periodic resync interval [exercise 18](18-the-tracker-between-two-syncs.md) measured — not because kube-proxy noticed your edit (it did not; nothing watches the ruleset) but because it periodically writes what it believes regardless of what is there. Time it, and compare with the interval you measured. Then say what this implies for a *persistent* corruption: something that rewrites the rule every second would win, and kube-proxy would report perfect health throughout.

**Do — part 5, the version that does not self-heal**, for one minute, because it is the shape a real incident takes:

```sh
nft delete map ip kube-proxy service-ips 2>/dev/null || nft -a list table ip kube-proxy | grep -n 'map service-ips'
```

Deleting the map that dispatches *every* ClusterIP breaks all Services on the node at once, including DNS — which is why this is done last, deliberately, and confirmed repaired before moving on. Expect the resync to fix this too, and expect the interval to be the same one; **a total outage and a one-third degradation have the same recovery time**, which is not obvious until you have measured both.

**Write down** — the prediction table with the observed column, the exact rule you replaced, the measured failure fraction, the repair latency, and one sentence naming what would have made this fault permanent. That last sentence is what [7.C4](33-7c4-a-policy-that-reads-correct.md) is, at a different layer.

**Footprint note** — nothing added. Three pods that were already running.

**Teardown** — force the repair rather than waiting for it, and prove the Service is whole again:

```sh
kubectl -n kube-system rollout restart ds kube-proxy && kubectl -n kube-system rollout status ds kube-proxy
kubectl -n svc run c --rm -it --restart=Never --image=registry.k8s.io/e2e-test-images/agnhost:2.47 -- \
  sh -c 'for i in $(seq 1 30); do curl -s http://web.svc/hostname; echo; done' | sort | uniq -c
```

Three names, ten each, zero failures. **The topology stays** — [exercise 20](20-7c1-a-partition-named-by-path.md) needs the same Service and installs Chaos Mesh onto this cluster.
