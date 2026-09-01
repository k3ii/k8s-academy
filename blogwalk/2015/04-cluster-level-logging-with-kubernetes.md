<a id="cluster-level-logging-with-kubernetes"></a>
# The manifest in this post never parsed, and the stack it describes is no longer shipped at all

**Post** — [Cluster Level Logging with Kubernetes](https://kubernetes.io/blog/2015/06/cluster-level-logging-with-kubernetes/),
2015-06-11, Kubernetes pre-1.0 — six weeks before the 1.0 release.

**As written** — the post assumes a cluster "created with cluster level logging support", which
was "an option when creating a GKE cluster, and is **enabled by default** for the open source GCE
Kubernetes distribution". So `kubectl get pods` opens with a per-node agent already running:

```
fluentd-cloud-logging-kubernetes-minion-0f64   1/1       Running   0          32m
fluentd-cloud-logging-kubernetes-minion-27gf   1/1       Running   0          32m
kube-dns-v3-pk22                               3/3       Running   0          32m
monitoring-heapster-v1-20ej                    0/1       Running   9          32m
```

Then a synthetic log generator, `counter-pod.yaml`, quoted here exactly as the post fences it:

```
  apiVersion : v1  
  kind : Pod  
  metadata :  
    name : counter  
  spec :  
    containers :  
   - name : count  
      image : ubuntu:14.04  
      args : [bash, -c,   
            'for ((i = 0; ; i++)); do echo "$i: $(date)"; sleep 1; done']  
```

`kubectl create -f counter-pod.yaml`, then `kubectl logs counter` — "this command fetches the log
text from the **Docker log file** for the image that is running in this container." Then
`kubectl exec -i counter bash` to watch the script from inside.

Then the demonstration the post is built around. Restart the container and lose its history:

```
$ kubectl stop pod counter
$ kubectl create -f counter-pod.yaml
$ kubectl logs counter
0: Tue Jun  2 21:51:40 UTC 2015
```

*"Oh no! We've lost the log lines from the first invocation of the container in this pod!"* — and
the fix is the agent, whose spec the post gives in full: a `kind: Pod` named
`fluentd-cloud-logging`, mounting `hostPath: /var/lib/docker/containers`, of which "one instance
of this pod runs on each node of the cluster." The rest of the article queries the result in
Google Cloud Logging, exports it to BigQuery, and greps it out of a GCS bucket with `jq`.

**As it runs now** — four fates, and the first one has to be fixed before any of the others can
be observed:

1. **The manifest never worked, in 2015 or now.** It is not a translation problem: run that block
   through any YAML parser and it fails outright. `containers :` sits at indent 4 and the
   sequence item `- name : count` sits at indent **3** — dedented below the key it belongs to —
   so the parser reports a block-sequence start where it expected the mapping to end. The spaces
   before the colons are legal and harmless; the indentation is not. `kubectl create -f` on that
   file has never produced a pod. The post links a working copy in the source repo, so the fence
   is a transcription defect that nobody caught — and a reader who assumes it once worked will go
   looking for an old `kubectl` that accepted it.
2. **`kubectl stop` hard-errors.** It was deprecated in code at v1.1.1 and **removed in v1.8**.
   `kubectl delete pod counter` is the replacement, and the two are not the same command — `stop`
   scaled a controller to zero first.
3. **The agent is not missing from your cluster; it is missing from Kubernetes.** No supported
   distribution ships a logging agent, and the pin says so twice: "Kubernetes does not provide a
   native storage solution for log data", and "while Kubernetes does not provide a native
   solution for cluster-level logging, there are …". The post's opening `kubectl get pods` cannot
   be reproduced on any cluster you can build.
4. **The mechanism underneath is not only intact, it is specified.** Containers still write to
   stdout and stderr; the kubelet still directs the runtime to write them to files; the path is
   documented and configurable (`/var/log/pods` by default, `podLogsDir` to move it); the kubelet
   rotates them (`containerLogMaxSize`, default 10Mi; `containerLogMaxFiles`, default 5) and log
   rotation itself has been **stable since v1.21**. The post's `/var/lib/docker/containers` is
   the only part of the agent's spec that is wrong, and it is wrong because it named an
   implementation's directory instead of an interface.

And the post's central complaint is now **half** fixed, which is the most interesting number in
the exercise. "By default, if a container restarts, the kubelet keeps **one** terminated container
with its logs." So `kubectl logs counter --previous` answers the post's question — once. Restart
twice and the post's "Oh no!" is exactly as true as it was in 2015.

**The diff, and why** — the post describes a Kubernetes that shipped a logging *product*, and the
project stopped shipping products.

Cluster-level logging is not one decision. It is a store, a retention period, an index, a query
language, a cost owner, and a compliance boundary — and there is no answer to any of them that
is right for both a Raspberry Pi and a bank. The 2015 answer was to pick one per distribution:
Cloud Logging on GCE, Elasticsearch and Kibana elsewhere, wired in by the cluster turn-up
scripts. That makes the vendor's choice the cluster's default, puts a credentialed shipper into
every node's base image, and — the pressure that actually settled it — makes the logging stack
something SIG Node has to keep working, forever, for backends it does not own. It is the same
maintenance-ownership argument that removed the in-tree container runtimes in
[the CRI exercise](03-docker-and-kubernetes-and-appc.md), reaching a different subsystem.

So the project retreated to the layer it can actually promise: a **contract about files**. Write
to stdout; the kubelet puts it at a known path in a known layout, rotates it to a known bound,
and serves the current plus one previous instance through the API. Everything above that — the
DaemonSet, the parsing, the store, the dashboards — is explicitly yours, and the post's fluentd
Pod is a thing you now write rather than a thing you find running.

The retreat has a visible cost, and it is not hidden in the docs. The kubelet's bound is
10Mi × 5 per container by default, which at the counter's one line a second is generous but
finite, and nothing warns you when it wraps. The API-level ability to ask for *just* stderr —
the first thing anyone parsing logs wants — is `PodLogsQuerySplitStreams`, and it has been alpha
and off since v1.32 with no later stage. Eleven years after this post, the thing Kubernetes has
added to the reader's side of container logging is one alpha query parameter.

Release facts and the pressure behind each are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.32 – |

`PodLogsQuerySplitStreams`, whole. One row is the finding: there is no promotion to report, and
the gate file declares neither `removed` nor a `toVersion`, so the alpha is current rather than
abandoned. Step 8 is where you meet it.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), fresh. The post's entire picture is
one agent per node and you cannot see that on one node. Bring it up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=pair`, then `ssh zain@10.10.10.130`.

**Do**

1. Type the post's manifest into `counter-pod.yaml` **exactly as fenced above**, whitespace and
   all, and apply it:

   ```sh
   kubectl apply -f counter-pod.yaml; echo "exit=$?"
   ```

   Record the error. Then find the single character position that is wrong, fix only that, and
   apply again. Do not retype the block from memory — the defect is invisible if you do.

   If `ubuntu:14.04` will not pull on your guest's architecture, substitute `busybox` and change
   `bash` to `sh`. Note that you had to: the post's image predates the architecture your lab runs
   on, and that is a fifth kind of staleness this file is not about.

2. The post's read path, unchanged:

   ```sh
   kubectl logs counter | head -3
   kubectl exec -i counter bash 2>&1 | head -2
   kubectl exec -it counter -- bash -c 'ps aux | head -5'
   ```

   The pin's synopsis is `kubectl exec (POD | TYPE/NAME) [-c CONTAINER] [flags] -- COMMAND`, and
   every example in the reference uses `--`. Record what the post's form actually does before you
   use the modern one.

3. The post's teardown command:

   ```sh
   kubectl stop pod counter; echo "exit=$?"
   ```

4. Now reproduce the post's demonstration without deleting the pod — restart just the container,
   which is what the post was really testing:

   ```sh
   kubectl exec counter -- kill 1
   sleep 20
   kubectl get pod counter -o jsonpath='{.status.containerStatuses[0].restartCount}{"\n"}'
   kubectl logs counter | head -2
   kubectl logs counter --previous | tail -2
   ```

5. Then do it once more and ask for the instance before last:

   ```sh
   kubectl exec counter -- kill 1
   sleep 20
   kubectl logs counter --previous | tail -2
   ```

   Write down how many invocations the cluster can hand you, and compare that number with the
   post's complaint.

6. Find the files, on whichever node the pod landed on:

   ```sh
   kubectl get pod counter -o jsonpath='{.spec.nodeName}{"\n"}'
   sudo ls -l /var/log/pods/default_counter_*/count/
   sudo head -2 /var/log/pods/default_counter_*/count/0.log
   ```

   The post mounted `/var/lib/docker/containers`. Note what is in each log line besides your text,
   and who put it there.

7. Read the bound the kubelet is enforcing, from the kubelet's own live configuration rather than
   from a config file you might not have:

   ```sh
   N=$(kubectl get pod counter -o jsonpath='{.spec.nodeName}')
   kubectl get --raw "/api/v1/nodes/$N/proxy/configz" | tr ',' '\n' | grep -i containerLog
   ```

   The counter writes roughly one line a second. Work out how long this pod's history survives.

8. Ask the API for only the error stream — the one thing a log consumer always wants:

   ```sh
   kubectl get --raw "/api/v1/namespaces/default/pods/counter/log?stream=Stderr" | head -3
   ```

9. Finally, build what the post's cluster had built for it. One DaemonSet, one node-local view:

   ```yaml
   apiVersion: apps/v1
   kind: DaemonSet
   metadata:
     name: logtail
   spec:
     selector:
       matchLabels: {app: logtail}
     template:
       metadata:
         labels: {app: logtail}
       spec:
         containers:
         - name: tail
           image: busybox
           command: ["sh", "-c", "find /var/log/pods -name '*.log' | sort; sleep 3600"]
           volumeMounts: [{name: podlogs, mountPath: /var/log/pods, readOnly: true}]
         volumes:
         - name: podlogs
           hostPath: {path: /var/log/pods}
   ```

   `kubectl apply -f logtail.yaml`, then `kubectl logs -l app=logtail --prefix`. Count how many
   agents you got and compare with the post's `kubectl get pods` listing.

**Expect** — step 1 fails before the API server is even consulted, with a YAML parse error naming
line 7 or the block that starts there. This is the only 2015 exercise whose first step is a
*correction*: nothing in the post can be tested until the manifest is repaired, and no version of
Kubernetes ever accepted it.

Step 2's first form prints a deprecation warning or an argument error rather than a shell; the
`--` form works. Step 3 fails with an unknown-command error — `stop` has not existed since v1.8.

Step 4 is the payload. `restartCount` becomes 1, `kubectl logs` restarts from `0:`, exactly as
the post laments — **and** `--previous` returns the tail of the first invocation, which the post
had no way to ask for. Step 5 then returns the *second* invocation, not the first: the kubelet
keeps one terminated container, so the post's "Oh no!" is now merely delayed by one restart. The
cluster-level agent is still the only thing that fixes it.

Step 6 shows `/var/log/pods/default_counter_<uid>/count/0.log`, and each line carries an RFC3339
timestamp, the stream name (`stdout`), a partial/full flag, and then your text. That framing is
the CRI log format — the kubelet asked the runtime to write it, which is why the modern agent
mounts a Kubernetes path rather than a runtime's.

Step 7 reports `containerLogMaxSize: 10Mi` and `containerLogMaxFiles: 5` unless your distribution
changed them. Step 8 does **not** give you stderr: the gate is alpha and off, so the query
parameter is ignored and you get the merged stream. That is the ladder above, observed.

Step 9 gives you exactly two pods, one per node, printing that node's log files and no other
node's. That is the post's architecture diagram, reproduced from a manifest you wrote — and the
distance between step 9 and the post is the whole diff: eleven years ago it was in the cluster's
turn-up script, and now it is in your repository.

**Read on** — the [CRI protocol
definition](https://github.com/kubernetes/cri-api/blob/v0.33.1/pkg/apis/runtime/v1/api.proto),
which the pin's own CRI page links: find where a container's log path is set, and then look for
an RPC that *serves* log content. There isn't one. Write down who reads the file for
`kubectl logs`, and what that means for step 8's stream parameter — which component would have to
change to honour it.

**Teardown** — `kubectl delete pod counter; kubectl delete ds logtail`. The `pair` guests are the
only two-node topology 2015 needs;
[tear the lab down properly](../../strands/lab-topologies.md#teardown) and bring up `solo` again
for [the checkpoint exercise](06-how-did-quake-demo-from-dockercon-work.md).
