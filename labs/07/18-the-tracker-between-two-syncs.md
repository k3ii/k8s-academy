<a id="the-tracker-between-two-syncs"></a>
# Make the pending-changes counter sit above zero, and cite the code that drains it

**Claim** — `kubeproxy_sync_proxy_rules_endpoint_changes_pending` can be driven above zero and held there, and the number of *changes* kube-proxy accounts for is larger than the number of *syncs* it performs. Both facts are the reason `endpointschangetracker.go` exists at all, and both are countable from the metrics endpoint. **This repays the last of [P6's three owed citations](../../phases/06-kubelet-node.md#capstone)** by confirming the file [exercise 14](14-the-model-files-before-the-machine.md) read against a proxy that is running.

**Rests on** — [exercise 14](14-the-model-files-before-the-machine.md) for the reading, [exercise 17](17-the-same-service-as-a-verdict-map.md) for the backend now in use, and the `svc` namespace those exercises left running.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup** — kube-proxy's metrics are on `10249` and bound to localhost by default, so read them from the node rather than through a Service:

```sh
ssh zain@10.10.10.131 'curl -s http://127.0.0.1:10249/metrics | grep -E "^kubeproxy_sync_proxy_rules_(endpoint|service)_changes|^kubeproxy_sync_proxy_rules_last_timestamp|^kubeproxy_sync_proxy_rules_duration_seconds_count"'
```

Then slow the proxy down deliberately, so that the accumulation window is wide enough to see with a one-second `watch` instead of needing a scrape pipeline:

```sh
kubectl -n kube-system get cm kube-proxy -o jsonpath='{.data.config\.conf}' > /tmp/kp.conf
grep -n 'minSyncPeriod\|syncPeriod' /tmp/kp.conf
sed -i 's/^\( *minSyncPeriod:\).*/\1 15s/' /tmp/kp.conf
# re-apply the ConfigMap as in exercise 17, then:
kubectl -n kube-system rollout restart ds kube-proxy && kubectl -n kube-system rollout status ds kube-proxy
```

**Do** — one terminal watching, one terminal churning:

```sh
ssh zain@10.10.10.131 'watch -n1 "curl -s http://127.0.0.1:10249/metrics | grep -E \"changes_pending|changes_total|duration_seconds_count\""'
```

```sh
kubectl -n svc scale deployment web --replicas=12; sleep 2
kubectl -n svc scale deployment web --replicas=3
kubectl -n svc delete pod -l app=web --wait=false
```

**Observe** — take the three numbers before and after and put them in a table: `endpoint_changes_total`, `duration_seconds_count` (which is the number of syncs), and the peak `endpoint_changes_pending` you saw.

**Expect** — `pending` to climb into double figures and then drop to `0` in one step, not to decay gradually. That single step **is** the checkout: the tracker hands the backend everything it has accumulated, in one call, and starts again from empty. Expect `changes_total` to exceed the number of syncs by a wide margin — that ratio is the compression the tracker buys, and with `minSyncPeriod: 15s` you can make it as large as you like.

Expect the sync duration to be **almost unaffected by how many changes were in the batch**, on this cluster, and expect that to be a fact about nftables rather than about the tracker: [exercise 17's](17-the-same-service-as-a-verdict-map.md) second structural reason says the update is a delta, so a batch of twelve endpoint changes is twelve map-element operations rather than a full rewrite. Say so explicitly, because on the iptables backend the same experiment gives a different shape and the difference is the point of having read both.

**Expect one number that does not move**: `service_changes_total`. Twelve pods came and went and the Service was never touched. Two trackers, two independent streams, one sync — and [exercise 14's](14-the-model-files-before-the-machine.md) service-port key is what joins them.

**Do — the negative control**, because a counter that only ever goes up proves less than one you have seen stay still:

```sh
sleep 30
ssh zain@10.10.10.131 'curl -s http://127.0.0.1:10249/metrics | grep -E "changes_total|duration_seconds_count"'
```

Nothing has changed in the cluster, and `duration_seconds_count` has still moved — that is the periodic full resync (`syncPeriod`, not `minSyncPeriod`), which exists so that a rule somebody deleted by hand comes back. **[Exercise 19](19-7c3-delete-one-endpoint-rule.md) is that sentence turned into a drill**, and the interval you just measured is the one it has to beat.

**Write down** — the before/after table, the changes-to-syncs ratio, the `file:line` of the checkout method in `endpointschangetracker.go` with the commit, and one sentence for P6: *kube-proxy's change tracker picks up the watch event* — now with a line number, a counter, and a measured batch size.

**Footprint note** — twelve short-lived `agnhost` pods for a couple of seconds, back down to three. Peak around 180 MiB on the worker, well inside its 2048MB, and gone before the next exercise.

**Teardown** — put `minSyncPeriod` back, or [exercise 19](19-7c3-delete-one-endpoint-rule.md) will be measuring your edit rather than the default:

```sh
sed -i 's/^\( *minSyncPeriod:\).*/\1 1s/' /tmp/kp.conf     # or delete the line if it was absent
# re-apply the ConfigMap, then rollout restart, then confirm from the logs
kubectl -n kube-system logs -l k8s-app=kube-proxy --tail=5 | grep -i sync
```

Leave the `svc` namespace and its three pods. **The topology stays.**
