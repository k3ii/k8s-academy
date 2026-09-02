<a id="visualize-kubelet-performance-with-node-dashboard"></a>
# The dashboard this post built is gone, every latency segment it had to parse out of kubelet logs is now a histogram the kubelet emits directly, and all four of them are still alpha

**Post** — [Visualize Kubelet Performance with Node Dashboard](https://kubernetes.io/blog/2016/11/visualize-kubelet-performance-with-node-dashboard/),
2016-11-17, Kubernetes v1.4 — Zhou Fang of Google, for SIG Node. This is the only post in the year
that the project has explicitly marked dead in the post's own body, which makes the interesting
question not *what replaced the tool* but *what of it survived into the binary*.

**As written** — the post carries an editor's note above its first paragraph:

> _Since this article was published, the Node Performance Dashboard was retired and is no longer
> available._
>
> _This retirement happened in early 2019, as part of the_ `kubernetes/contrib`
> _repository deprecation._

Read past it, because the post underneath is doing something more durable than hosting a web page.
It starts from a measurement problem. Kubernetes had two published benchmarks:

> **\* API responsiveness** : 99% of all API calls return in less than 1s.
> **\* Pod startup time** : 99% of pods and their containers (with pre-pulled images) start within 5s.

and only cluster-level tests to check them against:

> Prior to 1.4 release, we've only measured and defined these at the cluster level, opening up the
> risk that other factors could influence the results.

So the post adds node-isolated tests, collects resource usage from *"a standalone cAdvisor pod for
flexible monitoring interval (comparing with Kubelet integrated cAdvisor)"*, and — the part that
matters — decomposes pod startup into eight timestamps, six of which it obtains by **parsing the
kubelet's log**:

> - "create" (in test): the test creates pods through API client;
> - "running" (in test): the test watches that pods are running from API server;
> - "pod\_config\_change": pod config change detected by Kubelet SyncLoop;
> - "runtime\_manager": runtime manager starts to create containers;
> - "infra\_container\_start": the infra container of a pod starts;
> - "container\_start': the container of a pod starts;
> - "pod\_running": a pod is running;
> - "pod\_status\_running": status manager updates status for a running pod;

That decomposition immediately earns its keep. Comparing two builds of identical code, the post
finds a 40-second spread in 99th-percentile startup latency, drills into the time series, and lands
on a specific cause:

> We figure out this latency is introduced due to the query per second (QPS) limits of Kubelet to
> the API server (default is 5). After being aware of this, we find in additional tests that by
> increasing QPS limits, curve "running" gradually converges with "pod\_running', and results in
> much lower latency. Therefore the previous e2e test pod startup results reflect the combined
> latency of both Kubelet and time of uploading status, the performance of Kubelet is thus
> under-estimated.

And it forecasts its own replacement:

> In future we plan to use events in Kubernetes which has a fixed log format to collect tracing
> data more conveniently. Instead of extracting existing log entries, then you can insert your own
> tracing probes inside Kubelet and obtain the break-down latency of each segment.

**As it runs now** — the tool is gone as advertised. `node-perf-dash` has **zero** occurrences
anywhere under `docs/` at the pin, and so does `node-perf`. The post's link to the kubelet's
documentation, `/docs/admin/kubelet/`, also has zero occurrences; the page now lives at
`docs/reference/command-line-tools-reference/kubelet.md`.

The two benchmarks are gone from the documentation too. Search the pin for `99% of` and you get
**nothing** — neither the one-second API figure nor the five-second startup figure appears anywhere
under `docs/`. The numbers the post organised itself around are not published targets any more.

What replaced them is a different shape of claim. The kubelet emits the post's decomposition as
first-class histograms, and the pin's metrics reference prints them four in a row:

> `kubelet_pod_start_duration_seconds` — Duration in seconds from kubelet seeing a pod for the
> first time to the pod starting to run
>
> `kubelet_pod_start_sli_duration_seconds` — Duration in seconds to start a pod, excluding time to
> pull images and run init containers, measured from pod creation timestamp to when all its
> containers are reported as started and observed via watch
>
> `kubelet_pod_start_total_duration_seconds` — Duration in seconds to start a pod since creation,
> including time to pull images and run init containers, measured from pod creation timestamp to
> when all its containers are reported as started and observed via watch
>
> `kubelet_pod_status_sync_duration_seconds` — Duration in seconds to sync a pod status update.
> Measures time from detection of a change to pod status until the API is successfully updated for
> that pod, even if multiple intevening changes to pod status occur.
>
> — `docs/reference/instrumentation/metrics.md:2786-2812`, help text as printed

Line them up against the post's probe list and the mapping is one to one. `pod_config_change` →
`pod_running` is `kubelet_pod_start_duration_seconds`. `create` → `running` is
`kubelet_pod_start_total_duration_seconds`. The status-manager segment the post diagnosed as the
bottleneck is `kubelet_pod_status_sync_duration_seconds`, its own histogram. And the third one is
the post's segment with image pulls removed — the measurement the post's *"with pre-pulled images"*
parenthetical was trying to approximate by hand.

Every one of the four is marked `Stability Level: ALPHA`, and every one is served on plain
`/metrics`.

The bottleneck itself was fixed. The post found a default of 5; the pin's kubelet configuration
reference says:

> `kubeAPIQPS` is the QPS to use while talking with kubernetes apiserver. Default: 50
>
> — `docs/reference/config-api/kubelet-config.v1beta1.md:1198-1199`

Tenfold, with `kubeAPIBurst` at 100 alongside it.

Two further things changed under the post's feet. The first is what alpha means for a metric. The
pin publishes a lifecycle the post had no equivalent of:

> Alpha metric → Beta metric → Stable metric → Deprecated metric → Hidden metric → Deleted metric
>
> Alpha metrics have no stability guarantees. These metrics can be modified or deleted at any time.
>
> — `docs/concepts/cluster-administration/system-metrics.md:60-64`

with a rule that decides how long a rename gives you warning, graded by stability — *"**ALPHA**
metrics can be hidden or removed in the same release in which they are deprecated"* (`:96`). So the
four histograms carrying the post's decomposition sit in the one tier that is allowed to vanish
without notice, ten years after the decomposition was published.

The second is that the post's *"standalone cAdvisor pod ... comparing with Kubelet integrated
cAdvisor"* choice has been overtaken from the other side. The integrated one is now the deprecated
one:

> As of Kubernetes v1.37, cAdvisor-based pod and container metrics collection in the kubelet is
> deprecated. CRI runtimes that do not support the required metrics will lose pod and container
> level metrics collection when this feature reaches general availability (GA).
>
> — `docs/reference/instrumentation/cri-pod-container-metrics.md:39-43`

and the endpoint named after cAdvisor is explicitly no longer promised to be cAdvisor:

> The kubelet queries the CRI runtime for pod and container metrics via the `ListPodSandboxMetrics`
> RPC and serves them on the `/metrics/cadvisor` endpoint. This replaces the cAdvisor-based
> collection at the pod and container level while preserving the same endpoint path and metric
> names.
>
> — `docs/reference/instrumentation/cri-pod-container-metrics.md:60-64`

which is why a metric exists whose only job is to say which of the two you are actually reading:
*"The kubelet exposes a `kubelet_metrics_provider` metric with a `provider` label set to either
`cri` or `cadvisor`"* (`:69-71`).

**The diff, and why** — this is the case where **the post was right, the fix shipped, and the
artifact still died** — and the reason the artifact died is the same reason the fix survived.

Separate the two things the post produced. One is a web application: a Go service, a set of charts,
a hostname, a build index, and a scraper that parsed kubelet log lines to recover timestamps. The
other is a *claim about what pod startup is made of* — that the number everyone was quoting
conflated the kubelet's work with the time taken to upload a status, and that the kubelet was being
blamed for the second.

Only one of those can move into the binary. The dashboard lived in `kubernetes/contrib`, outside
the release, parsing a log format nothing promised to keep stable; the post says as much when it
plans to stop *"extracting existing log entries"*. A consumer that depends on an unversioned
by-product of somebody else's logging is not a component, it is a guess that keeps working, and it
stopped working the way such guesses always do — the repository holding it was deprecated, and
nothing in the release noticed. The claim, by contrast, could be answered by instrumenting the
thing itself, which is exactly what the post asked for in its *Future Work*: probes inside the
kubelet rather than a parser outside it. That request was granted, and the granting is why there is
no dashboard: once the kubelet emits the segments, the visualiser is somebody else's Prometheus.

So the retirement note at the top of the post is accurate and misleading at once. Accurate: the URL
is dead. Misleading: it reads like a failure, and the post got what it wanted.

What it did not get is a promise. The decomposition arrived as four alpha metrics and has stayed
alpha across every release since, which by the pin's own lifecycle means it can be renamed or
deleted in a single release with no deprecation period. A reader building on it today is in a
recognisably similar position to the post's author: depending on an interface the project has
declined to guarantee. The difference — and it is the whole difference — is that this one is
*inside* the binary, versioned with it, and documented as unstable rather than undocumented and
assumed stable. That is a smaller promise, honestly labelled, and it has now outlived the tool that
asked for it by seven years.

One artifact of the drift is worth naming, because it is the kind of thing that makes a reader
doubt the whole page. The scheduler's requested-resources metrics are documented like this:

> The metrics are exposed at the HTTP endpoint `/metrics/resources`. [...]
>
> On Kubernetes 1.21 you must use the `--show-hidden-metrics-for-version=1.20` flag to expose these
> alpha stability metrics.
>
> — `docs/concepts/cluster-administration/system-metrics.md:171-176`

Two traps in six lines. The instruction is addressed to a release sixteen behind the pin and is
carried unqualified in current documentation. And the endpoint is `/metrics/resources`, **plural**,
on the **kube-scheduler** — one letter and one component away from the kubelet's
`/metrics/resource`, singular, which is a different endpoint serving different data. The plural
spelling appears in exactly three lines at the pin, all three of them these.

Resource usage — cAdvisor, the summary API, `metrics-server` and the four endpoints that carry
them — is
[the 2015 monitoring post's subject](../2015/02-resource-usage-monitoring-kubernetes.md) and is
settled there. This exercise stays on the latency side: what the kubelet says about its own
operations, and how much that saying is worth.

**The ladder** — the two gates a reader chasing this post's replacement will meet. Neither belongs
to the post, which announced a tool and not a feature; both decide what the reader's own kubelet
will answer.

The gate that decides whether `/metrics/cadvisor` is cAdvisor:

## PodAndContainerStatsFromCRI
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.23 – v1.36 |
| beta | `false` | — | v1.37 –  |

Fourteen releases at alpha, and the promotion to beta lands on the pinned release itself — with the
default still `false`. This is the rarer kind of beta: available and off. The prose page calls it
*"a beta feature"* in its second sentence and the reader who takes that as "enabled" will read
cAdvisor's numbers all afternoon while looking for CRI's.

The gate that decides whether `/metrics/slis` exists:

## ComponentSLIs
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.26 – v1.26 |
| beta | `true` | — | v1.27 – v1.31 |
| stable | `true` | `true` | v1.32 – v1.34 |

`removed: true` is declared at file level, and the last release the file names is v1.34 — three
before the pin. The gate is gone; you cannot set it either way. Yet the page describing the endpoint
still says *"The `ComponentSLIs` feature gate defaults to enabled for each Kubernetes component as
of v1.27"* (`docs/reference/instrumentation/slis.md:19-21`) and still renders a feature-state
banner keyed to it. The endpoint is unconditional now, which is the outcome the sentence was
describing; the sentence just hasn't been told it won.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), fresh. One node, one kubelet, and
every question here is about what that kubelet says about itself. Bring the guest up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, install Kubernetes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), then
`ssh zain@10.10.10.180`.

Nothing is installed on top. The post's dashboard is unreachable and its charts are screenshots;
what the exercise measures is the metric surface the pinned kubelet ships with.

**Do**

1. Find the post's decomposition. Set `N` once and reuse it:

   ```sh
   N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" | grep '^# HELP kubelet_pod_start'
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" | grep '^# HELP kubelet_pod_status_sync'
   ```

   Four `# HELP` lines. Each carries a bracketed stability marker; read what it says and hold onto
   it for step 9.

2. Produce a startup event and watch which histograms move. Capture the counts first:

   ```sh
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" \
     | grep -E '^kubelet_pod_start_(duration|total_duration|sli_duration)_seconds_count' > /tmp/before
   kubectl run p1 --image=registry.k8s.io/pause:3.10
   kubectl wait --for=condition=Ready pod/p1 --timeout=120s
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" \
     | grep -E '^kubelet_pod_start_(duration|total_duration|sli_duration)_seconds_count' > /tmp/after
   diff /tmp/before /tmp/after
   ```

   Not all three necessarily advance by one. Before reading the diff, predict which do, from the
   help text in step 1 — in particular, which of them requires the kubelet to have *observed the
   pod via watch* rather than merely started it.

3. Recover the post's central finding — that a single startup number conflates two different
   waits — by reading the sums rather than the counts:

   ```sh
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" \
     | grep -E '^kubelet_pod_start_(duration|total_duration)_seconds_sum'
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" \
     | grep '^kubelet_pod_status_sync_duration_seconds_sum'
   ```

   The post had to plot two curves and observe that one lagged the other. Say which subtraction of
   these three numbers is the post's *"combined latency of both Kubelet and time of uploading
   status"* minus the kubelet's own part, and why that subtraction is only approximately the thing
   the post plotted.

4. Make the difference visible by making the image pull expensive, which is the segment
   `sli_duration` exists to exclude:

   ```sh
   kubectl run p2 --image=docker.io/library/debian:bookworm --command -- sleep 3600
   kubectl wait --for=condition=Ready pod/p2 --timeout=300s
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" \
     | grep -E '^kubelet_pod_start_(sli_duration|total_duration)_seconds_bucket' | tail -30
   ```

   Two histograms over the same event, differing by the pull. Identify the bucket each landed in
   and state which of the post's two published benchmarks — the one-second or the five-second
   figure — would have been reported as met or missed depending purely on which metric you chose.

5. Check the post's diagnosed bottleneck against your own kubelet's setting, rather than against
   the documented default:

   ```sh
   kubectl get --raw "/api/v1/nodes/$N/proxy/configz" | tr ',' '\n' | grep -i -e kubeAPIQPS -e kubeAPIBurst
   ```

   Compare with the post's *"default is 5"* and with the pin's documented default of 50. If your
   value is neither, find what set it — the kubelet config file on the node is where kubeadm writes
   its answer.

6. Establish that these endpoints are not one permission but two. Read the pin's own mapping first:

   > | Kubelet API | resource | subresource |
   > | `/stats/*` | nodes | stats |
   > | `/metrics/*` | nodes | metrics |
   > | *all others* | nodes | proxy |
   >
   > — `docs/reference/access-authn-authz/kubelet-authn-authz.md:66-72`

   then test whether the split is reachable through the path you have been using:

   ```sh
   kubectl create serviceaccount reader
   kubectl create clusterrole metrics-only --resource=nodes --subresource=metrics --verb=get
   kubectl create clusterrolebinding reader-metrics \
     --clusterrole=metrics-only --serviceaccount=default:reader
   kubectl auth can-i get nodes/metrics --as=system:serviceaccount:default:reader
   kubectl auth can-i get nodes/proxy   --as=system:serviceaccount:default:reader
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" --as=system:serviceaccount:default:reader
   ```

   The last command fails despite the second-to-last succeeding on `nodes/metrics`. Explain the
   failure in terms of which authorizer is refusing: the API server deciding whether you may use
   the node proxy at all, or the kubelet deciding which of its paths you may read.

7. Read the warning that makes step 6 more than bookkeeping:

   > **get** permission on `nodes/proxy` is not a read-only permission, and authorizes executing
   > commands in any container running on the node.
   >
   > — `docs/reference/access-authn-authz/kubelet-authn-authz.md:81-84`

   Every `kubectl get --raw .../proxy/...` in this exercise is exercising that permission. Say what
   a monitoring agent should be granted instead, given the subresource table in step 6, and what it
   would then have to do differently to reach the kubelet.

8. Settle which of two nearly-identical endpoint names belongs to which component:

   ```sh
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics/resource" | head -5
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics/resources" ; echo "exit=$?"
   kubectl get --raw "/metrics/resources" | head -5 ; echo "exit=$?"
   ```

   One serves, one 404s on the kubelet, and the third asks the API server for the scheduler's
   plural-spelled endpoint and will not find it there either. Work out from the results which
   component you would have to reach, and on which port, to see `kube_pod_resource_request`.

9. Test the lifecycle rule from `system-metrics.md` against a metric that has actually been through
   it:

   ```sh
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" | grep -c 'Deprecated since'
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" | grep 'Deprecated since' | head -5
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" | grep -c '\[ALPHA\]'
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" | grep -c '\[STABLE\]'
   ```

   Count how many of the kubelet's metrics carry each marker. Then answer the question that decides
   whether the post's decomposition is safe to build on: for a metric marked `[ALPHA]`, how much
   notice does the documented lifecycle oblige the project to give you before the name disappears?

10. Determine which source is behind the endpoint named after cAdvisor on *your* node:

    ```sh
    kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" | grep kubelet_metrics_provider
    kubectl get --raw "/api/v1/nodes/$N/proxy/configz" | tr ',' '\n' | grep -i featureGates -A5
    ```

    If the provider metric is absent or reports `cadvisor`, reconcile that with the ladder above —
    which stage the gate reached at this release, and what its default is. Do not enable the gate;
    the point is that a beta feature named in prose as beta is off, and that the endpoint's name
    tells you nothing either way.

**Expect**

```sh
kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" | grep -c '^kubelet_'
kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" | grep '^kubelet_pod_start.*_count'
kubectl get --raw "/api/v1/nodes/$N/proxy/metrics/slis" | grep -c '^kubernetes_healthcheck'
kubectl auth can-i get nodes/proxy --as=system:serviceaccount:default:reader
```

Several hundred kubelet metrics, the pod-start counters showing your two pods, a populated
`/metrics/slis` on an endpoint whose feature gate no longer exists, and a `no` from the last
command.

By the end you should be able to state the post's finding without the post: that pod startup time,
quoted as one number, is at least three measurements, and that choosing among them changes whether
a cluster passes. You should also be able to say why the dashboard's death is not evidence against
the post — and to point at the exact tier of the metric lifecycle that the post's surviving
contribution has never left.

**Read on** — the pin's
[metrics reference](https://kubernetes.io/docs/reference/instrumentation/metrics/) lists every
metric with its stability level and the endpoint that serves it. Filter it to the kubelet and
answer: of the metrics the kubelet serves, how many are `STABLE`, and does the set of stable ones
include anything at all about how long the kubelet takes to do its work? Then say what that implies
about writing an alert on kubelet latency.

**Teardown** — `kubectl delete pod p1 p2 --ignore-not-found` and
`kubectl delete clusterrolebinding reader-metrics; kubectl delete clusterrole metrics-only;
kubectl delete serviceaccount reader` if you are keeping the node, otherwise
[the teardown step](../../strands/lab-topologies.md#teardown).
