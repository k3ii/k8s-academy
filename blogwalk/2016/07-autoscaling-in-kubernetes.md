<a id="autoscaling-in-kubernetes"></a>
# The closing promise of this post is now a documented pattern, every command in it fails, and the error it prints survives in the current documentation in three incompatible forms

**Post** — [Autoscaling in Kubernetes](https://kubernetes.io/blog/2016/07/autoscaling-in-kubernetes/),
2016-07-12, Kubernetes v1.3, part of *Five days of Kubernetes 1.3*. Two authors from Google, and the
subject is two autoscalers used together: the new Cluster Autoscaler adding nodes, and the
Horizontal Pod Autoscaler adding pods.

**As written** — the pitch is cost, stated twice, and both statements are the reason this post is
worth walking:

> Kubernetes will automatically scale up your cluster as soon as you need it, and scale it back down
> to save you money when you don't.

> Ideally, we would want the number of nodes in the cluster and the number of pods in deployment to
> dynamically adjust to the load to meet end user demand. The new Cluster Autoscaling feature
> together with Horizontal Pod Autoscaler can handle this for you automatically.

The cluster half is GCE-specific and built by the in-tree script:

```
export NUM\_NODES=2
export KUBE\_AUTOSCALER\_MIN\_NODES=2
export KUBE\_AUTOSCALER\_MAX\_NODES=5
export KUBE\_ENABLE\_CLUSTER\_AUTOSCALER=true
```

```
./cluster/kube-up.sh
```

> The kube-up.sh script creates a cluster together with Cluster Autoscaler add-on. The autoscaler
> will try to add new nodes to the cluster if there are pending pods which could schedule on a new
> node.

The pod half is a workload created imperatively, in one command that also creates its Service:

```
$ kubectl run php-apache \
  --image=gcr.io/google\_containers/hpa-example \
  --requests=cpu=500m,memory=500M --expose --port=80
service "php-apache" createddeployment "php-apache" created
```

then an autoscaler over it:

```
$ kubectl autoscale deployment php-apache --cpu-percent=50 --min=1 --max=10
```

> This defines a Horizontal Ppod Autoscaler that maintains between 1 and 10 replicas of the Pods
> controlled by the php-apache deployment […] the horizontal autoscaler will increase and decrease
> the number of replicas (via the deployment) so as to maintain an average CPU utilization across all
> Pods of 50% (since each pod requests 500 milli-cores by kubectl run, this means average CPU usage
> of 250 milli-cores)

```
$ kubectl get hpa
NAME         REFERENCE                     TARGET    CURRENT   MINPODS   MAXPODS   AGE
php-apache   Deployment/php-apache/scale   50%       0%        1         20        14s
```

Load is generated from a shell in a `busybox` pod, the HPA reaches 310% and seven replicas, three of
the seven go `Pending`, and the post reads the reason off the pod:

```
  1m {default-scheduler } Warning FailedScheduling pod (php-apache-2046965998-3ewo6) failed to fit in any node
fit failure on node (kubernetes-minion-group-yhdx): Insufficient CPU
fit failure on node (kubernetes-minion-group-de5q): Insufficient CPU

  1m {cluster-autoscaler } Normal TriggeredScaleUp pod triggered scale-up, mig: kubernetes-minion-group, sizes (current/new): 2/3
```

A node appears, the seven pods run, the load stops, the HPA returns to one replica, and after
*"approximately 10-12 minutes"* the node is removed. The post ends on the cost argument again:
*"Having machines that do nothing is a waste of money."*

**As it runs now** — nothing the post types survives, and the first thing to establish is why the
post never mentions installing anything to measure CPU. In 2016 `kube-up.sh` installed the metrics
add-on along with the cluster, so *"we need to wait a moment (about one minute) for stats to
propagate"* is the only trace of a whole component. At the pin the metrics pipeline is a
prerequisite you satisfy yourself, and the successor page says so before its first command:

> To follow this walkthrough, you also need to use a cluster that has a
> [Metrics Server](https://github.com/kubernetes-sigs/metrics-server#readme) deployed and configured.

A cluster with no metrics-server still accepts a HorizontalPodAutoscaler and reports its own failure
in a status condition — which is the one place this post's subject *gained* a feedback path where
[06](06-kubernetes-network-policy-apis.md)'s lost one.

The component the post is silently relying on is Heapster, which it never names, and which the
pinned tree has not finished forgetting: `system:heapster` is still listed as a default ClusterRole
in the RBAC reference, annotated *"Role for the Heapster component (deprecated)"* and linking a
repository, and three other pages still print sample output showing a `heapster` pod or service
running. A retired component's authorization role outliving the component is the same kind of
residue as the `--storage-driver-db` flag, which the pin's `kubectl run` and `kubectl autoscale`
both still accept, defaulting to `"cadvisor"` — cAdvisor storage-driver plumbing from this post's era
hanging off the two commands this post runs.

The command-line breakage, in order:

1. **`kubectl run --requests=` is gone.** The pin's `kubectl run` has fifty-nine flags and
   `--requests` is not among them; neither is `--limits`. `--expose` and `--port` both survive, and
   `--expose` now reads *"If true, create a ClusterIP service associated with the pod. Requires
   --port"* — *with the pod*, because as [04](04-using-deployment-objects-with.md) established,
   `kubectl run` makes a Pod and no longer makes a Deployment. So the post's single command has to
   fail: it names a flag that does not exist, and if it did exist the object it created would be the
   wrong kind for the `kubectl autoscale deployment` on the next line.
2. **`--cpu-percent` was renamed.** `kubectl autoscale` at the pin takes `--cpu`, `--memory`,
   `--min`, `--max` and `--name`. `--cpu-percent` is absent, and its replacement is not a rename but
   a widening: `--cpu` accepts *both* forms — *"When specified as a percentage (e.g."70%" for 70% of
   requested CPU) it will target average utilization. When specified as quantity (e.g."500m" for 500
   milliCPU) it will target average value."* The post could only express a ratio. And `--memory` is
   new: the post's autoscaler had one signal.
3. **The output columns changed shape.** The post prints `TARGET` and `CURRENT` as separate
   columns; the pin prints one `TARGET` column holding `0% / 50%`, and adds `REPLICAS`.
4. **Two of the post's three `kubectl get hpa` samples contradict its own command.** It runs
   `--max=10` and then prints `MAXPODS 20`, twice, before printing `10` in the final sample. That was
   wrong on the day it published and no rung of Kubernetes has anything to do with it.
5. **The markdown is damaged in the same way [05](05-configuration-management-with-containers.md)
   is.** `NUM\_NODES`, `KUBE\_AUTOSCALER\_MIN\_NODES`, `google\_containers` — every underscore inside
   a fenced block is escaped, so the environment variables and the image path are both unusable as
   printed. The post also renders *"version [v1.3.0](http://v1.3.0/)"*, a version string turned into
   a hyperlink to a hostname that never existed, and *"Horizontal Ppod Autoscaler"*.
6. **The image path moved registries.** `gcr.io/google_containers/hpa-example` is
   `registry.k8s.io/hpa-example` in the pin's manifest — and that manifest carries **no tag**, which
   is the same omission the pin fixed in the load generator beside it, where the post's bare
   `busybox` became `busybox:1.28`.
7. **`kube-up.sh` and the in-tree Cluster Autoscaler are not where the post left them.** The pinned
   documentation still links `kubernetes/kubernetes/blob/master/cluster/kube-up.sh` from a kubectl
   verification page and still describes log rotation *"In Kubernetes clusters created by the
   `kube-up.sh` script"* — two references, no instructions, and nothing that would tell you whether
   the four `KUBE_AUTOSCALER_*` variables are read by anything. Cluster Autoscaler itself now lives
   at `github.com/kubernetes/autoscaler`, outside the tree this pin covers.

**The diff, and why** — the post is the fifth case: **overtaken by stasis** in its documentation
while its subject moved underneath. Three things are worth separating.

**The thesis survived exactly and got a name.** The pin has a section called *Horizontal workload
autoscaling* on its node-autoscaling page whose closing sentence is the post's opening one:

> If configured correctly, this pattern ensures that your application always has the Node capacity to
> handle load spikes if needed, but you don't have to pay for the capacity when it's not needed.

That is the rarest outcome in this whole census: the argument is unchanged, promoted from a release
announcement to a documented pattern, while every keystroke that demonstrated it broke. The
vocabulary did shift, and the pin records the shift as a note rather than leaving it implicit —
*"Provisioning was formerly known as scale-up in Cluster Autoscaler."* The post's `TriggeredScaleUp`
event names a concept that has since been renamed by the project that emitted it.

**The error message is frozen in three eras, in four places, and the one you will see is in none of
them.** This is the finding to spend time on. Search the pinned documentation for the scheduler's
refusal and you get two distinct historical forms:

- `pod (php-apache-...) failed to fit in any node` / `fit failure on node (X): Insufficient CPU` —
  the post's own 2016 form, still printed verbatim in an extended-resource task page and a
  debug-running-pod page.
- `No nodes are available that match all of the following predicates:: Insufficient cpu (3).` — a
  later form, with a doubled colon, still printed in the assign-cpu-resource and
  assign-memory-resource task pages.

The current message is a third shape again: it aggregates by *reason* with counts rather than naming
each node, so a two-node cluster where one node is tainted reports one line, not two. Four task
pages, two dead formats, zero occurrences of the live one. The reader who follows this post will
produce an event that matches neither sample the documentation shows them, and the only way to find
that out is to run it. The pin's own HPA walkthrough carries the same kind of fossil: its
`kubectl describe hpa` sample is timestamped `Fri, 16 Jun 2017`, describes a `ReplicationController`,
and sits under a page whose reviewer list still includes this post's author.

**The autoscaler gained the two things the post could not express, and one of them took twenty-one
releases.** The post's autoscaler has three knobs — a target ratio, a minimum and a maximum — and
its cost argument logically ends at zero replicas, which it cannot request, because `minReplicas: 0`
was not accepted. It still is not accepted for a CPU-metric HPA:

> Scaling to zero is only supported for object and external metrics. It is not available for
> resource metrics (such as CPU or memory utilization), because those can only be measured on
> running Pods. Setting `minReplicas: 0` requires at least one object or external metric to be
> configured; the API server rejects the HorizontalPodAutoscaler otherwise.

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.16 – v1.36 |
| beta | `true` | — | v1.37 – |

`HPAScaleToZero` sat at alpha, off by default, for **twenty-one consecutive releases**, and reached
beta at the pin's own version. It is the longest alpha in this year's set by a wide margin. Read
against the post that is the sharpest possible commentary on the cost pitch: the promise was
*scale it back down to save you money*, and the floor of one replica moved for the first time nine
years later, for metrics the post never mentions.

The second knob is the flapping the post walks past. It observes that node removal is slow —
*"Cluster Autoscaler makes sure that the node is really not needed so that short periods of
inactivity (due to pod upgrade etc) won't trigger node deletion"* — and does not say that the pod
autoscaler has the same problem with the same shape of answer. It does, and the answer is now two
fields:

> For scaling down the stabilization window is _300_ seconds […] For scaling up there is no
> stabilization window.

and a tolerance that was cluster-wide and is now per-object:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.33 – v1.34 |
| beta | `false` | — | v1.35 – v1.36 |
| stable | `true` | `true` | v1.37 – |

`HPAConfigurableTolerance` is the year's cleanest example of a shape worth naming: **its beta rung
defaults to `false`.** Beta is not the same as on. Two releases at beta with the gate off, then
stable and locked at v1.37 — and the default it makes configurable, *"the default cluster-wide
tolerance of 10%"*, is the number that decided every scaling decision in the post without appearing
in it. The pin adds one more constraint worth reading twice: *"(You can't use the Kubernetes API to
configure this default value.)"*

One more ladder, for the granularity the post's whole-pod average could not express:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.20 – v1.26 |
| beta | `true` | — | v1.27 – v1.29 |
| stable | `true` | — | v1.30 – v1.31 |

`HPAContainerMetrics` declares `removed: true` — retired because per-container targets became
unconditional, the same reason [06](06-kubernetes-network-policy-apis.md)'s `NetworkPolicyEndPort`
gate was retired, and the opposite reason from why `NetworkPolicyStatus` was.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), fresh. Two nodes is the post's own
shape and the reason is arithmetic: the worker has two cores, the pin's manifest requests 200m per
replica, and the post's `--max=10` therefore cannot fit — so the `Pending` pods the post gets from a
five-node cloud cluster arrive on a two-node lab for free, and the wall is real rather than
contrived. What cannot arrive is the node that resolves them. Node autoscalers *"need to interact
with cloud provider APIs to provision and consolidate Nodes […] they need to be explicitly
integrated with each supported cloud provider"*, and this lab has no cloud provider, so the second
half of the post's demonstration is unreachable here and unreachable anywhere in this curriculum.
That is the same line [06](06-kubernetes-network-policy-apis.md) draws at the policy plugin, drawn
one layer lower. Bring the topology up with
[the five provision steps](../../strands/lab-topologies.md#provision) using `topology=pair`, install
Kubernetes with [the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps),
then `ssh zain@10.10.10.130`.

**Do**

1. Before installing anything, ask the cluster for the measurement the post assumes it has:

   ```
   kubectl get nodes
   kubectl top nodes
   kubectl get apiservices | grep metrics
   ```

   Record what `top` says. This is the state the post's cluster was never in.

2. Run the post's workload command exactly as the published page renders it, escapes included, into
   a shell on the control plane. Then remove the four backslashes from the underscores and run it
   again. Then remove `--requests=cpu=500m,memory=500M` and run it a third time, and inspect what
   you got:

   ```
   kubectl get all -l run=php-apache
   ```

   Three attempts, three different outcomes. Name the kind that the third one created and say what
   the post's next command expects instead.

3. Delete that and use the pin's manifest, reading it before you apply it:

   ```
   kubectl delete pod php-apache --ignore-not-found
   kubectl delete service php-apache --ignore-not-found
   kubectl apply -f https://k8s.io/examples/application/php-apache.yaml
   kubectl get deployment php-apache -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
   ```

   Write down the image reference the pin ships and how it differs from the load-generator image on
   the same page.

4. Create the autoscaler the post's way, then the pin's way, and then look at what was stored:

   ```
   kubectl autoscale deployment php-apache --cpu-percent=50 --min=1 --max=10
   kubectl autoscale deployment php-apache --cpu=50% --min=1 --max=10
   kubectl get hpa php-apache -o yaml | head -20
   ```

   The third command answers a question the first two do not raise: which API version the server
   returned, given that the pin's synopsis says the command *"will attempt to use the autoscaling/v2
   API first, in case of an error, it will fall back to autoscaling/v1 API."*

5. Read the autoscaler's own account of itself with no metrics available:

   ```
   kubectl get hpa
   kubectl describe hpa php-apache
   ```

   Compare your `kubectl get hpa` header against the post's and against the one the pin prints. Then
   find the condition that is `False` and copy its reason and message verbatim.

6. Install the metrics pipeline. It is out of tree and this exercise does not pin it: follow the
   link the pin itself gives, choose a release, and record which one you chose.

   ```
   kubectl -n kube-system get deployment metrics-server
   kubectl -n kube-system rollout status deployment/metrics-server --timeout=180s
   ```

   If it does not become available, read its logs and record what it says — a kubeadm lab's kubelet
   serving certificates are the usual obstacle here, and the metrics-server README is the authority on
   it, not this repository.

7. Re-ask both questions from steps 1 and 5, then start the load with both spellings:

   ```
   kubectl top pods
   kubectl describe hpa php-apache | sed -n '/Conditions/,$p'
   kubectl run -i --tty service-test --image=busybox /bin/sh
   kubectl run -i --tty load-generator --rm --image=busybox:1.28 --restart=Never -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://php-apache; done"
   ```

   The first `run` is the post's form and the second is the pin's. Record what the post's form does
   before you use the pin's.

8. In another shell, watch it climb into the wall:

   ```
   kubectl get hpa php-apache --watch
   kubectl get pods -l run=php-apache
   kubectl describe pod -l run=php-apache | sed -n '/Events/,$p'
   ```

   Copy the `FailedScheduling` message character for character. Then compare it with the post's
   `fit failure on node` output and with the two other forms the pinned documentation prints, and
   say which of the three it resembles most.

9. Stop the load and time the descent, then take the brake off:

   ```
   kubectl get hpa php-apache --watch
   kubectl patch hpa php-apache --type merge -p '{"spec":{"behavior":{"scaleDown":{"stabilizationWindowSeconds":0}}}}'
   ```

   Measure how long the first scale-down took against the documented 300 seconds, then raise the
   load, drop it, and measure again with the window at zero.

10. Ask for the two things the post could not ask for, and record which the API accepts:

    ```
    kubectl patch hpa php-apache --type merge -p '{"spec":{"minReplicas":0}}'
    kubectl patch hpa php-apache --type merge -p '{"spec":{"behavior":{"scaleUp":{"tolerance":"0.05"}}}}'
    kubectl explain hpa.spec.behavior.scaleUp.tolerance
    ```

    One of these is refused and the refusal is the point. Read the message and connect it to the
    reason the pin gives for the restriction.

**Expect** — step 1: two nodes `Ready`. `kubectl top nodes` fails, reporting that the metrics API is
not available; no `metrics.k8s.io` APIService is registered. The post has no equivalent moment
because its cluster arrived with the add-on.

Step 2: the escaped form fails before the API server — the shell sees `google\_containers` and
`cpu=500m` inside a flag the parser will reject anyway. Unescaped, the refusal is
`unknown flag: --requests`. Without that flag it succeeds and prints two lines, `pod/php-apache
created` and `service/php-apache created`. The kind is `Pod`, and `kubectl autoscale deployment
php-apache` will not find a Deployment.

Step 3: `deployment.apps/php-apache created` and `service/php-apache created`. The image is
`registry.k8s.io/hpa-example` with no tag; the load-generator image on the same page is
`busybox:1.28`.

Step 4: `unknown flag: --cpu-percent`. The pin's form returns
`horizontalpodautoscaler.autoscaling/php-apache autoscaled`. The stored object's `apiVersion` is
`autoscaling/v2`; note that the post's era's `autoscaling/v1` is still served, and that the pin says
v2-only fields *"are preserved as annotations when working with autoscaling/v1"*.

Step 5: the `TARGET` column reads `<unknown>/50%`. `ScalingActive` is `False` with a
`FailedGetResourceMetric` reason, and `AbleToScale` is `True` — the autoscaler can act and cannot
decide. Both the post's `TARGET`/`CURRENT` pair and the pin's single `0% / 50%` cell differ from what
your kubectl prints; write down all three.

Step 6: whichever release you chose, the version is yours and not this repository's, which is the
honest position for a component the pinned tree does not contain.

Step 7: `kubectl top pods` returns per-pod CPU; `ScalingActive` flips to `True` with
`ValidMetricFound`. The post's `kubectl run … /bin/sh` form is refused — the trailing command is not
separated by `--` — and the pin's form gives you a shell that loops. Four differences separate those
two lines: the `--`, the `--rm`, the `--restart=Never`, and the pinned tag.

Step 8: the target climbs well past 50% and replicas rise toward 10. Some pods stay `Pending`. The
event aggregates its reasons with counts across both nodes and mentions the control plane's taint
alongside insufficient CPU; it names neither node individually. It does not resemble either sample
in the documentation. No `TriggeredScaleUp` event ever arrives, because nothing is watching for one:
the pods will stay `Pending` until you remove the load or the deployment.

Step 9: the first scale-down does not begin promptly; expect roughly five minutes of the highest
recommendation in the window being held, which is the documented default. With the window at zero
the descent starts on the next sync interval, which the pin gives as fifteen seconds.

Step 10: `minReplicas: 0` is rejected by the API server, because this HPA's only metric is a
resource metric. The `tolerance` patch is accepted, and `kubectl explain` finds the field, because
the gate that carries it is stable and locked at this version.

**Read on** — the pin's
[Horizontal Pod Autoscaling concept page](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/),
the *Algorithm details* section. Read the paragraphs on missing metrics and not-yet-ready pods, and
answer one question with your step 8 output in hand: the controller *"conservatively assumes that
the not-yet-ready pods are consuming 0% of the desired metric"*, and your `Pending` pods will never
become ready — so what does that do to the ratio, and does it push the replica count up or hold it?
Then read
[Node Autoscaling](https://kubernetes.io/docs/concepts/cluster-administration/node-autoscaling/)
and answer a harder one: the page presents Cluster Autoscaler and Karpenter as interchangeable from
a cluster user's view, one working on pre-configured Node groups and the other auto-provisioning
individual machines — which of the post's four `KUBE_AUTOSCALER_*` variables has an equivalent in
each, and which has an equivalent in neither?

**Teardown** — `kubectl delete hpa php-apache`, then
`kubectl delete -f https://k8s.io/examples/application/php-apache.yaml`, then remove metrics-server
with whatever manifest you installed it from. Take the topology down with
[teardown](../../strands/lab-topologies.md#teardown).
