<a id="cache-or-etcd"></a>
# Which of your reads reached etcd

**Claim** — for any `GET` or `LIST` you can name in advance whether it is served from the watch cache or from etcd, from the request's parameters alone; and a *quorum-consistent* read can be served from cache without violating consistency, by a mechanism you can name and observe.

**Rests on** — [the ring](33-overflow-the-ring.md) and [the two-layer comparison](34-the-same-failure-two-layers.md), which established that both sources exist. [KEP-2340](../../phases/03-api-machinery.md#m3-5) is the reading; this is the experiment that makes it non-obvious.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup** — build the prediction table **before** touching the cluster. Read `staging/src/k8s.io/apiserver/pkg/storage/cacher/delegator.go` and fill in your own answers:

| Request | Cache or etcd? | Which line decides |
|---|---|---|
| `GET /api/v1/namespaces/x/configmaps/c` | | |
| `LIST ...?resourceVersion=0` | | |
| `LIST ...` with no `resourceVersion` | | |
| `LIST ...?resourceVersion=0&limit=5` | | |
| `LIST ...?resourceVersion=<recent>&resourceVersionMatch=NotOlderThan` | | |
| `LIST ...?resourceVersion=<exact>&resourceVersionMatch=Exact` | | |
| `LIST ...?labelSelector=a=b` | | |

Two of these have answers most people get wrong, and `limit` is one of them. Commit to the table in writing first — a table filled in after the metrics are read teaches nothing.

**Do**

1. Create 200 ConfigMaps in one namespace so a list is measurable.

2. Take a metrics snapshot, run one request from the table, take another snapshot, and diff. Automate it, because you are doing this seven times:

   ```sh
   snap() { kubectl get --raw /metrics | grep -E '^etcd_request_duration_seconds_count|^apiserver_cache_list_total|^apiserver_watch_cache_read_wait' | sort; }
   snap > /tmp/a; kubectl get --raw "$URL" >/dev/null; snap > /tmp/b; diff /tmp/a /tmp/b
   ```

   The metric names differ between releases. Find the ones your apiserver actually exports — `kubectl get --raw /metrics | grep -i cache` — and say in your notes which you used.

3. Score your table.

4. Now the KEP's mechanism. Find in `delegator.go` how a consistent read is served from cache at all — what the cacher waits for, and what etcd feature makes that wait bounded. Then check whether it is on in your cluster:

   ```sh
   kubectl get --raw /metrics | grep -i consistent_read
   ssh zain@10.10.10.130 'sudo grep -n "feature-gates\|watch-progress" /etc/kubernetes/manifests/kube-apiserver.yaml'
   ```

5. Observe the wait. With a heavy write loop running against the resource, issue consistent reads in a tight loop and watch the wait metric move. If it does not move, find out whether the mechanism is disabled in your version and say so — a negative result you can explain is the answer.

**Expect** — `resourceVersion=0` is the cheap one everybody quotes. The result that repays the exercise is that a plain list with **no** `resourceVersion` is the *most* expensive request in the table on an old apiserver and may be free on a new one, and that is entirely down to whether the KEP's mechanism is enabled. `limit` and `labelSelector` each interact with the cache in a way that is not symmetrical with the other.

The mechanism itself is the sentence to be able to say without notes: the cacher asks etcd where "now" is, waits for its own cache to reach that revision, and then serves locally — so the read is as consistent as a quorum read while costing etcd one cheap call instead of a full list. `etcd_request_duration_seconds_count` still moves; it moves by one small request rather than by one large one, and seeing that difference in the diff is the confirmation.

**Write down** — the table with predicted and actual, the two you got wrong, the mechanism in one sentence with its `file:line`, and whether it was enabled in your cluster. Then one line for [P4](../../phases/04-controllers.md): which of these seven a controller's informer issues on startup, and why the answer is `resourceVersion=0` and then a watch.

**Teardown** — delete the ConfigMap namespace. **The topology stays** — [server-side apply](37-managedfields-and-a-conflict.md) is next.
