<a id="11c3-a-rolling-update-under-conntrack-watch"></a>
# 11.C3 — the conntrack table filling during a rollout: the DNS-talk mechanism, on hardware you own

**Claim** — drive a rolling update while watching `conntrack -L`, and the connection-tracking table grows in the shape [the DNS talk](../../strands/talks.md#debugging) named — not to exhaustion, but far enough to see the mechanism begin. The point is not to reproduce the outage; it is to watch the exact table the talk descended four layers to blame, filling on your own cluster, so the mechanism stops being a slide.

**Rests on** — [the DNS postmortem re-read](08-the-dns-postmortem-re-read.md), whose conntrack row this makes concrete; and [P7's datapath](../../phases/07-networking.md), where conntrack was first read.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from the trace half.

**Read** — [the drill's chaos-table row](../../phases/11-synthesis.md#chaos) and [the manual-drills standard](../../strands/chaos.md#manual-drills). By hand: `conntrack -L` watched during a rollout you trigger, because the skill is recognising the table's growth against traffic you caused.

**Do** — run a small Deployment behind a Service with a trickle of client traffic, then roll it and watch the table on a node while the pods churn:

```sh
kubectl create deployment churn --image=nginx --replicas=4
kubectl expose deployment churn --port=80
# a trickle of clients so there are flows to track:
kubectl run clients --image=busybox --restart=Never -- sh -c \
  'while true; do wget -q -O- churn >/dev/null 2>&1; done'
WK=10.10.10.131
ssh zain@$WK 'sudo conntrack -C; sudo conntrack -L 2>/dev/null | wc -l'   # baseline
kubectl rollout restart deployment/churn
ssh zain@$WK 'for i in 1 2 3 4 5; do sudo conntrack -C; sleep 2; done'    # watch it move
```

**Observe** — the conntrack count climbing as old pods drain and new ones take flows, each replaced endpoint leaving tracked entries behind until they time out. This is the table the talk watched fill; on a two-node cluster it will not exhaust, but its *direction* under churn is the mechanism.

**Expect** — the count rising during the rollout and settling as entries expire — the shape, not the catastrophe. Seeing the direction on hardware you own is the deliverable; the talk supplies the scale you are deliberately not reproducing.

**Write down** — the baseline and peak conntrack counts and one sentence tying the rise to endpoint churn — the observable that makes [the postmortem table's conntrack row](08-the-dns-postmortem-re-read.md) yours rather than the talk's.

**Teardown** — delete the workload and the client loop; **the topology stays** — it is released only when [the upgrade capstone](11-the-upgrade-that-drops-nothing.md) replaces `pair` with `workhorse`:

```sh
kubectl delete deployment churn; kubectl delete service churn; kubectl delete pod clients
```
