<a id="resource-usage-monitoring-kubernetes"></a>
# The pipeline in this post is gone; the sentence describing the kubelet's role is still exact

**Post** — [Resource Usage Monitoring in Kubernetes](https://kubernetes.io/blog/2015/05/resource-usage-monitoring-kubernetes/),
2015-05-12, Kubernetes v0.16 — two months before 1.0.

**As written** — install [Heapster](https://github.com/kubernetes/heapster). It "runs as a pod in
the cluster, similar to how any Kubernetes application would run", discovers every node, and
queries usage from each node's kubelet. The kubelet in turn "fetches the data from cAdvisor".
Heapster groups what it collects by pod, attaches the pod's labels, and pushes the result to a
configurable backend — InfluxDB with Grafana, or Google Cloud Monitoring, "and many others".

Two claims about cAdvisor carry the post's only concrete instruction:

- cAdvisor "is integrated into the Kubelet binary", auto-discovers every container on the
  machine, and collects CPU, memory, filesystem and network statistics.
- "On most Kubernetes clusters, cAdvisor exposes a simple UI for on-machine containers on port
  4194" — with a screenshot of it.

And one about the kubelet: it "translates each pod into its constituent containers and fetches
individual container usage statistics from cAdvisor. It then exposes the aggregated pod resource
usage statistics via a REST API."

The post ends with *"Heapster runs by default on most Kubernetes clusters, so you may already
have it!"*

**As it runs now** — four fates, and the exercise is telling them apart:

1. **The UI hard-errors, and it errors in the way that wastes the most time.**
   `curl http://<node>:4194/` gets connection refused. There is nothing to unblock: the
   `--cadvisor-port` flag was deprecated in v1.10, defaulted to `0` in v1.11, and the flag and
   the web server were **removed outright in v1.12**. Connection-refused reads as a firewall
   problem, so the reader debugs `iptables` instead of the docs.
2. **`kubectl top` errors, and not at the kubelet.** `kubectl top nodes` on a cluster with
   nothing extra installed says `error: Metrics API not available`. The failure is API
   discovery: `metrics.k8s.io` is not a registered group. `kubectl top` gained Metrics API
   support in v1.10 with a Heapster fallback, and the fallback was **dropped in v1.19**.
3. **Heapster does not fail — it is simply not a thing you can install.** The repository is
   archived, and no supported cluster ships it. The post's closing reassurance is the most
   misleading line in it: nothing runs by default, and the thing that replaced it also does not.
4. **The sentence about the kubelet is still literally correct**, at a different path. The
   kubelet still compiles cAdvisor in as a library, still aggregates per-pod, and still serves it
   over a REST API — `/stats/summary` for the JSON the post is describing, and
   `/metrics/cadvisor`, `/metrics/resource` and `/metrics/probes` for the Prometheus rendering.
   The architecture diagram is right; two of its three boxes have different names.

**The diff, and why** — the post describes a **collection** design and the project replaced it
with an **API** design, which is why nothing in the middle survived.

Heapster was a pod that scraped every kubelet and wrote to a backend of your choosing. That
places a cluster-wide, credentialed, stateful scraper inside the thing it monitors, with a
different storage schema per backend, and it makes the Horizontal Pod Autoscaler's dependency a
*deployment choice*. Kubernetes cannot ship an autoscaler that only works if you picked
InfluxDB. So the shape inverted: the cluster defines the **Metrics API** — a fixed, aggregated,
read-only API group serving current CPU and memory for nodes and pods — and anything at all may
implement it. `metrics-server` is only the reference implementation. The autoscaler now depends
on an API rather than on a program.

The port-4194 removal is a different pressure and worth separating. An unauthenticated HTTP
server exposing every container's resource usage and filesystem layout on a fixed port of every
node is attack surface for data the kubelet's own authenticated API already served. The second
server was pure exposure, so it went.

Release facts and the pressure behind each are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

**No gate** — the Metrics API has never had a feature gate, because an aggregated API is not a
feature of any binary that reads the gate list; it is a registered API group or it is not.
Instrument used: `kubectl api-versions`, plus the API reference at the pin. It sat at **beta from
v1.8 to v1.36** — 29 releases, longer than any beta in the gate directory — and `metrics.k8s.io/v1`
arrived in **v1.37**. The reference at the pin disagrees with itself about which of those you
will meet: the only generated reference page is `metrics.v1beta1`, while the prose under
`content/en/docs` writes `metrics.k8s.io/v1` nine times, `v1beta1` nine times and `v1beta2` four
times. Step 6 is where you find out which one *your* cluster serves, and the answer depends on
the metrics-server release rather than on the Kubernetes one.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo). If you still have the guest from
[the v1beta3 exercise](01-introducing-kubernetes-v1beta3.md), reuse it; otherwise bring
it up with [the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, then `ssh zain@10.10.10.180`.

**Do**

1. Try the post's one clickable instruction, from the node itself so no firewall can be blamed:

   ```sh
   curl -sS --max-time 5 http://127.0.0.1:4194/ ; echo "exit=$?"
   sudo ss -lntp | grep 4194 || echo 'nothing listening on 4194'
   ```

2. Find where the data went. Set `N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')`,
   then:

   ```sh
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics/cadvisor" | wc -l
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics/cadvisor" | grep -c '^container_'
   ```

   The metric names still say `container_`. Note who is serving them.

3. Now the post's own sentence about the kubelet, tested as written — per-pod aggregation over a
   REST API:

   ```sh
   kubectl get --raw "/api/v1/nodes/$N/proxy/stats/summary" \
     | python3 -c 'import json,sys; d=json.load(sys.stdin); p=d["pods"][0]; print(p["podRef"], [c["name"] for c in p["containers"]], p["cpu"]["usageNanoCores"])'
   ```

4. Ask for the thing the post never mentions, because in 2015 it did not exist:

   ```sh
   kubectl top nodes; echo "exit=$?"
   kubectl api-versions | grep metrics || echo 'no metrics group'
   ```

   Record the error verbatim before installing anything.

5. Install the reference implementation and watch it fail on certificates first:

   ```sh
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   kubectl -n kube-system rollout status deploy/metrics-server --timeout=90s; echo "exit=$?"
   kubectl -n kube-system logs deploy/metrics-server | tail -20
   ```

   Then fix it the way every lab cluster has to, and say why that is not a metrics problem:

   ```sh
   kubectl -n kube-system patch deploy metrics-server --type=json \
     -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
   kubectl -n kube-system rollout status deploy/metrics-server --timeout=90s
   ```

6. Re-run step 4, then ask which version of the API group you were given:

   ```sh
   kubectl top nodes
   kubectl api-versions | grep metrics
   kubectl get --raw "/apis/$(kubectl api-versions | grep metrics | head -1)/nodes" | head -c 300
   ```

7. Last, the design point. Compare the *same* node's CPU through both paths — step 3's
   `usageNanoCores` and step 6's `kubectl top nodes` — and write down why the two numbers differ
   even though one is computed from the other.

**Expect** — step 1: connection refused, and nothing listening. The screenshot in the post is of
a server that has not existed since v1.12.

Step 2 returns thousands of lines whose names all begin `container_`, served by the **kubelet**
over the API server's node proxy. cAdvisor did not go away; its HTTP server did.

Step 3 prints one pod's name, its container names and a CPU figure — the post's sentence,
verbatim, on v1.37. This is the only part of the post you can still execute.

Step 4 fails with `error: Metrics API not available`, and `kubectl api-versions` has no
`metrics.k8s.io` line. The two failures are the same failure, and neither one is about the
kubelet, which was answering fine in steps 2 and 3.

Step 5's first rollout does *not* come up. The logs name a TLS failure reaching the kubelet: the
serving certificate is self-signed and metrics-server will not trust it. That is not a
monitoring defect — it is the kubelet's own serving certificate, self-signed by default and
trusted by nothing, which has sat that way for twenty-five releases and arrives here as somebody
else's outage.

Step 6 succeeds and `kubectl top nodes` prints a table. The group version you get is whatever
your metrics-server build registers, which is why the *No gate* section above could not tell you
in advance.

Step 7: `usageNanoCores` is an instantaneous rate the kubelet computed over its own window;
`kubectl top` shows a figure the Metrics API deliberately smooths for autoscaler stability. The
pin says so outright — the values "may not match those from standard OS tools like `top`". A
number optimised for a controller's decisions is not a number optimised for your eyes, and the
post's pipeline made no such distinction because it had no controller to serve.

**Read on** — [KEP-5207, *`metrics.k8s.io` API
definition*](https://github.com/kubernetes/enhancements/tree/master/keps/sig-instrumentation/5207-metrics-k8s-io-api-definition):
find what had to be *written down* before an API group that had served traffic since v1.8 could
go stable, and write down why the missing thing was a specification rather than code.

**Teardown** — `kubectl -n kube-system delete deploy metrics-server` if you want the node's
memory back; leaving it installed costs about 100Mi and no later exercise depends on it either
way. Leave the guest up; the next exercise in this year reuses it.
