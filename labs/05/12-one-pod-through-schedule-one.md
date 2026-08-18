<a id="one-pod-through-schedule-one"></a>
# One pod, at `-v=10`, mapped line by line onto `schedule_one.go`

**Artifact** — the log of a single pod's scheduling attempt from the real scheduler at maximum verbosity, annotated so that every line is attributed to a function in `pkg/scheduler/schedule_one.go` or to a plugin, with `file:line` beside it.

**Rests on** — [the call path](01-the-sig-tour-in-call-order.md) and [the default plugin set](04-what-actually-runs-by-default.md). At 54.5 KB `schedule_one.go` is not a file to read straight through; [the area is explicit](../../strands/source-reading.md#area-3-scheduler) that the way in is a log line looked up in it, which is exactly what this produces.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. The change is to the control-plane node's static pod manifest.

**Setup** — raise the real scheduler's verbosity, and note that this restarts it:

```sh
ssh zain@10.10.10.130 'sudo cp /etc/kubernetes/manifests/kube-scheduler.yaml /root/kube-scheduler.yaml.bak'
ssh zain@10.10.10.130 "sudo sed -i 's|- --leader-elect=true|- --leader-elect=true\n    - --v=10|' /etc/kubernetes/manifests/kube-scheduler.yaml"
kubectl -n kube-system get pod -l component=kube-scheduler -o wide
```

The backup is not optional: at `-v=10` this scheduler writes tens of megabytes a minute, and the file you restore from is the only thing standing between you and a full root filesystem on `.130`.

**Do**

1. Start the log capture, then quiesce the cluster so that exactly one pod is scheduled:

   ```sh
   kubectl -n kube-system logs -f -l component=kube-scheduler --tail=0 > /tmp/sched-v10.log &
   sleep 3
   kubectl -n sched-lab run one --image=registry.k8s.io/pause:3.9 --restart=Never \
     --overrides='{"spec":{"containers":[{"name":"pause","image":"registry.k8s.io/pause:3.9","resources":{"requests":{"cpu":"100m"}}}]}}'
   sleep 5; kill %1
   wc -l /tmp/sched-v10.log
   ```

2. Cut it down to the one pod:

   ```sh
   grep -n 'sched-lab/one\|"one"' /tmp/sched-v10.log
   ```

3. Annotate. For each distinct message, find where it is emitted:

   ```sh
   grep -rn '"Attempting to schedule pod"\|"Successfully bound pod"' pkg/scheduler/
   ```

   Do that for every line, in order. Where the message comes from a plugin rather than from `schedule_one.go`, say which plugin and which extension point — you have [the mapping](04-what-actually-runs-by-default.md) for that.

4. Answer the module's question from the annotated log, not from the source: **between "attempting" and "successfully bound", how many distinct phases can you name, and where does each end?** Mark on the log where [the cycle boundary you drew](03-two-cycles-not-one.md) actually falls.

5. Note what the log does **not** say. Count how many of the roughly twenty default plugins produce a line here at all.

**Observe** — the timestamps. The gaps between them are the phase's only free latency measurement of a real scheduling cycle, and one gap is much larger than the others.

**Expect** — a surprisingly short sequence for one pod, on the order of a few dozen lines even at `-v=10`, of which a minority are the framework and the majority are the informer machinery underneath it. Expect the largest time gap to be the bind, and expect it to be a large multiple of everything before it — which is the measured justification for the design you read about in [KEP-624](03-two-cycles-not-one.md) rather than the argued one.

Expect most plugins to be silent. A plugin that filters nothing out logs nothing, so **the log shows you the plugins that had an opinion, not the plugins that ran**. That distinction is worth writing down, because it is the single easiest way to misread a scheduler log.

**Write down** — the annotated log with `file:line` per line, the phase boundaries, and the bind gap in milliseconds.

**Footprint note** — `-v=10` on a static pod writes to the node's disk through the container runtime's log rotation. `pair`'s control-plane node has room for a few minutes of this and not for an afternoon; **turn it down in the teardown, not at the end of the module.** No build, no memory change: 7.5GB total.

**Teardown** — restore the manifest and confirm the scheduler came back:

```sh
ssh zain@10.10.10.130 'sudo cp /root/kube-scheduler.yaml.bak /etc/kubernetes/manifests/kube-scheduler.yaml'
kubectl -n kube-system get pod -l component=kube-scheduler
ssh zain@10.10.10.130 'df -h /'
```

`kubectl -n sched-lab delete pod one`. Keep `/tmp/sched-v10.log` — [the next exercise](13-why-the-bind-is-async.md) uses a second capture and compares against it. **The topology stays.**
