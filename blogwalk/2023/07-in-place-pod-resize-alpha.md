<a id="in-place-pod-resize-alpha"></a>

# The one-line instruction at the heart of this post is refused by the API server, the status field whose four values it carefully explains is deprecated in favour of two conditions, and the other field it announces sits behind a gate that was alpha for one release and then deprecated

**Post** — [Kubernetes 1.27: In-place Resource Resize for Kubernetes Pods (alpha)](https://kubernetes.io/blog/2023/05/12/in-place-pod-resize-alpha/),
2023-05-12.

Vinay Kulkarni (Kubescaler Labs). 200 lines, 10,556 bytes, and the only post in this year's thirteen
that is a page bundle rather than a single file — it lives at
`blog/_posts/2023/in-place-pod-resize/index.md`. Nineteen of those lines are a credits list.

**As written**

The post opens on an irritation every reader has met. If you have deployed Pods with CPU or memory
resources specified, "you may have noticed that changing the resource values involves restarting the
pod. This has been a disruptive operation for running workloads... until now" (the post's `:10-13`).
Kubernetes v1.27 adds an alpha feature that resizes CPU and memory "without restarting the
containers", and the mechanism is one sentence: the `resources` field in a Pod's containers "now
allow mutation for `cpu` and `memory` resources. They can be changed simply by patching the running
pod spec" (`:15-19`).

The next paragraph is the consequence, and it is the most durable thing in the post. Because the
spec can now be changed without the container being rebuilt, "`resources` field in the pod spec can
no longer be relied upon as an indicator of the pod's actual resources. Monitoring tools and other
such applications must now look at new fields in the pod's status." Kubernetes asks the runtime what
is actually enforced, "via a CRI (Container Runtime Interface) API call to the runtime, such as
containerd", and reflects the answer in status (`:21-27`). A new `restartPolicy` for resize is
announced in two lines, giving users "control over how their containers are handled when resources
are resized" (`:29-30`).

*What's new in v1.27* then names three new fields. `allocatedResources` is added to
`containerStatuses` and "reflects the node resources allocated to the pod's containers"; a
`resources` field is added to the container's status and "reflects the actual resource requests and
limits configured on the running containers as reported by the container runtime"; and a `resize`
field is added to the Pod's status "to show the status of the last requested resize" (`:35-43`). The
post then spends nine lines defining that field's four values: `Proposed` is an acknowledgement that
the request "was validated and recorded", `InProgress` means the node has accepted it and is
applying it, `Deferred` means it cannot be granted now but the node "will keep retrying", and
`Infeasible` is "a signal that the node cannot accommodate the requested resize" at all (`:43-52`).

*When to use this feature* gives three cases, all of them about pods that are the wrong size on a
node that has room (`:55-63`). *How to use this feature* gives one instruction: enable the
`InPlacePodVerticalScaling` feature gate. What follows is thirty-five lines of terminal transcript
from `FEATURE_GATES=InPlacePodVerticalScaling=true ./hack/local-up-cluster.sh`, run as root in a
Kubernetes source tree, ending in the kubeconfig incantations for talking to it (`:66-107`). Then a
demo video, and two worked use cases — a cloud development environment that resizes between editing
and building, "with a little help from eBPF", and Java processes that need more CPU to start than to
run (`:109-139`).

*Known Issues* is four bullets, and the post is careful to head them with the release's stage:
containerd below v1.6.9 lacks the CRI support, so resizes "will appear to be *stuck* in the
`InProgress` state"; a resize may race with other pod updates; the status may take a while to catch
up; and "Static CPU management policy is not supported with this feature" (`:142-154`). Nineteen
named contributors and two managers close it, followed by five references to task pages
(`:157-200`).

**As it runs now**

The feature finished. `InPlacePodVerticalScaling` was alpha from v1.27 through v1.32, beta in v1.33
and v1.34, and stable from v1.35 — which is the version the lab cluster runs, so everything below
happens on a cluster where nothing needs switching on. The gate file also writes `locked: true` on
the stable row, which means the switch the post tells you to throw can no longer be thrown in either
direction.

The instruction at the post's `:19` is the one that broke, and it broke on a rule that was already
there when the post was written. `pods/_index.md:247-249` lists the fields a Pod update may change —
the two image fields, `activeDeadlineSeconds`, `terminationGracePeriodSeconds`, `tolerations` and
`schedulingGates` — and `resources` is not among them. That list is read closely, and argued to be
grammatically closed, in the exercise on [an extension point described twice in one
post](../2022/13-pod-scheduling-readiness-alpha.md). What that exercise had no reason to reach is
the section immediately after it. `pods/_index.md:257-262`, *Pod subresources*, says the update
rules "apply to regular pod updates, but other pod fields can be updated through *subresources*",
and names the first of them: "the `resize` subresource allows container resources
(`spec.containers[*].resources`) to be updated". So the list stayed closed and a second door was cut
beside it. `pod-v1.md:4693`, `:4748` and `:4841` serve GET, PATCH and PUT on
`/api/v1/namespaces/{namespace}/pods/{name}/resize`, and `resize-container-resources.md:230-231`
gives the post's sentence its modern form: `kubectl patch pod ... --subresource resize --patch ...`,
with `:239-240` warning that a client older than v1.32 "will report an `invalid subresource` error".

That leaves the same reference saying two things about the same field. `pod-v1.md:758` describes a
container's `resources` as "Compute Resources required by this container. Cannot be updated." Ninety
lines of prose away, `resize-container-resources.md:23-24` says that field holds "the *desired*
resources for the container, and are mutable for CPU and memory". Both sentences are true of
different verbs against different endpoints, and neither page says so. Steps 3 and 4 run one command
each and settle it.

The `resize` status field the post explains at length is deprecated. `pod-v1.md:322` still documents
it, still says "Any changes to container resources will automatically set this to "Proposed"", and
then says, in the same table cell: "Deprecated: Resize status is moved to two pod conditions
PodResizePending and PodResizeInProgress." The post's four values do not survive as four.
`resize-container-resources.md:67-73` makes `Deferred` and `Infeasible` into `reason:` values on a
`PodResizePending` condition; `:74-77` makes `InProgress` a condition type in its own right, with
actuation errors reported as `reason: Error`. `Proposed` has no successor at all. The word occurs in
three files under `content/en` — this post, the deprecating sentence at `pod-v1.md:322`, and a 2021
release-cadence post using the ordinary English word about a schedule.

`allocatedResources`, the first of the three fields the post announces, got a gate of its own five
releases later and lost it in one. `InPlacePodVerticalScalingAllocatedStatus` is alpha in v1.32 and
`deprecated` from v1.33, default `false` at both stages, and the field is now described at
`resize-container-resources.md:35-38` as "(Advanced)", "primarily used for internal scheduling
logic", with the reader told to "focus on `status.containerStatuses[*].resources`" instead. The
post's second and third fields are exactly right; its first is off by default and its `resize` field
is deprecated.

The known issues aged in three directions. containerd is at 2.2.1 on the lab node, far past the
v1.6.9 floor, so the first issue cannot be reproduced. The fourth — static CPU management — is still
true and now has two open attempts against it: `InPlacePodVerticalScalingExclusiveCPUs`, alpha since
v1.32, and `InPlacePodVerticalScalingExclusiveMemory`, alpha since v1.34, neither with a closing
version. `resize-container-resources.md:189-190` states the limitation flatly. And the limitation
list it sits in has nine entries (`:169-193`), of which the post anticipates exactly one. QoS class
is fixed at creation and a resize may not change it (`:175-182`), init and ephemeral containers
cannot be resized (`:183-185`), requests and limits cannot be removed once set (`:186-187`), Windows
is out (`:188`), and swap constrains memory resizes (`:191-192`) — none of which the post's *Known
Issues* has a word about.

One page disagrees with the gate file rather than with itself, and it is the page a reader arriving
from this post will land on first. `resize-container-resources.md:50-52` says the
`InPlacePodVerticalScaling` feature gate "must be enabled for your control plane and for all nodes
in your cluster" — of a gate that has been stable and locked since v1.35. This repo has met that
shape twice before, at [a page that still tells you to disable a gate that cannot be
disabled](../2020/04-introducing-podtopologyspread.md) and at [the last release where you must do
what the post says](03-node-log-query-alpha.md), so it is recorded here and not argued again; step 9
is the version of it that can be run rather than read.

**What this exercise does not cover, and where it lives**

The mutable-field list itself, and the argument about how closed it is, belong to the
scheduling-gates exercise linked above; this one takes the list as given and reads the section after
it. Pod-level resources — `resize-pod-resources.md`, the `/resize` subresource applied to
`spec.resources` rather than to a container — are the subject of a later post that this walk has not
reached, and the two gates for them are left alone here. cgroup v2, which the memory half of this
depends on, is walked in the exercise on [the version that went GA in
1.25](../2022/06-cgroupv2-ga-1-25.md).

**The diff, and why**

The post ***broke***, in the narrowest possible way and at the most important sentence. "They can be
changed simply by patching the running pod spec" is a command a reader can type, and at the pin the
API server refuses it: the rule at `pods/_index.md:247-249` was never relaxed, and container
resources became mutable through a subresource instead. The pin does not say why the door was cut
beside the list rather than through it, and this exercise does not guess; what it can show is that
both rules are live at once, which is step 3 and step 4.

Two smaller breaks follow from the same four years. The `resize` status field and its four values —
nine lines of the post, and the part a monitoring author would have copied — are deprecated in
favour of two conditions that carry three of the four values as reasons and drop the fourth. And
`allocatedResources`, announced in the post as simply added, is now behind a gate that is off by
default and deprecated.

Everything else is ***still right***, and one paragraph of it is more right than the post could have
known. The post's `:21-27` says the spec can no longer be relied on as an indicator of actual
resources and that monitoring must read the status instead; `resize-container-resources.md:23-38`
now opens with exactly that distinction, under the heading *Key Concepts*, as the first thing a
reader is told. The CRI round trip is still how the number gets there. And the two-line
`restartPolicy` announcement at the post's `:29-30` survives as `resizePolicy`, per resource, with
`NotRequired` as the default and `RestartContainer` as the alternative
(`resize-container-resources.md:115-134`) — the idea unchanged, the name and the shape settled.

Two gates carry this post, and they went in opposite directions.

`InPlacePodVerticalScaling`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.27 – v1.32 |
| beta | `true` | — | v1.33 – v1.34 |
| stable | `true` | `true` | v1.35 – |

No `removed:` key. `locked: true` is written on the stable row only, which makes this one of the 49
gate files in the pinned tree that write `locked: true` at all. The body of the file is one sentence
— "Enables in-place Pod vertical scaling." — against a task page of 332 lines.

`InPlacePodVerticalScalingAllocatedStatus`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.32 – v1.32 |
| deprecated | `false` | — | v1.33 – |

No `removed:` key and no `locked:` key, and the deprecated stage has no closing version, so it is
open at the pin. An alpha of exactly one release followed directly by `deprecated`, with no beta and
no stable, is not unusual on its own — 25 of the 487 gate files go alpha straight to deprecated —
but 23 of those 25 also carry `removed: true`. This gate and `WindowsHostNetwork` are the two that
do not: deprecated, never promoted, never withdrawn, still listed. The gate's own body adds that the
field "requires the `InPlacePodVerticalScaling` gate be enabled as well".

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 vCPU, 25G, at `10.10.10.180`.
The vCPU count is load-bearing: step 7 asks for eight CPUs on a four-CPU node, and the node's answer
is the point. Provision with the [standard steps](../../strands/lab-topologies.md#provision) and the
[node baseline](../../strands/lab-topologies.md#node-baseline-steps), then work from the node: `ssh
zain@10.10.10.180`.

Everything here is one Pod running `registry.k8s.io/pause:3.10`, which uses no measurable CPU or
memory of its own — so every number you read is a number Kubernetes wrote, not a number a workload
earned. Step 9 edits a static Pod manifest on the node and restores it; read it before you run it.

**Do**

1. Establish the three versions that decide whether any of this runs, and ask the server what it
   thinks of both gates.

   ```sh
   kubectl version
   sudo crictl version
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' | grep -i inplacepod
   ```

2. Create a Guaranteed Pod with a resize policy that treats CPU and memory differently — the
   two-line idea from the post's `:29-30`, in the shape the pin gives it.

   ```sh
   kubectl create ns resize
   cat > /tmp/resize-demo.yaml <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: demo
     namespace: resize
   spec:
     containers:
       - name: app
         image: registry.k8s.io/pause:3.10
         resizePolicy:
           - resourceName: cpu
             restartPolicy: NotRequired
           - resourceName: memory
             restartPolicy: RestartContainer
         resources:
           requests: { cpu: 200m, memory: 64Mi }
           limits: { cpu: 200m, memory: 64Mi }
   EOF
   kubectl apply -f /tmp/resize-demo.yaml
   kubectl -n resize wait --for=condition=Ready pod/demo --timeout=60s
   kubectl -n resize get pod demo \
     -o jsonpath='qos={.status.qosClass} restarts={.status.containerStatuses[0].restartCount}{"\n"}'
   kubectl -n resize get pod demo -o jsonpath='{.status.containerStatuses[0].resources}{"\n"}'
   ```

3. Do exactly what the post says: patch the running Pod spec.

   ```sh
   kubectl -n resize patch pod demo --patch \
     '{"spec":{"containers":[{"name":"app","resources":{"requests":{"cpu":"400m","memory":"64Mi"},"limits":{"cpu":"400m","memory":"64Mi"}}}]}}'
   ```

4. Now do it through the door that was cut beside the rule. The only difference is four words.

   ```sh
   kubectl -n resize patch pod demo --subresource resize --patch \
     '{"spec":{"containers":[{"name":"app","resources":{"requests":{"cpu":"400m","memory":"64Mi"},"limits":{"cpu":"400m","memory":"64Mi"}}}]}}'
   sleep 5
   kubectl -n resize get pod demo -o jsonpath='spec={.spec.containers[0].resources.limits.cpu} status={.status.containerStatuses[0].resources.limits.cpu} restarts={.status.containerStatuses[0].restartCount}{"\n"}'
   ```

5. Go looking for the two status surfaces the post announces, and for the two conditions that
   replaced one of them.

   ```sh
   kubectl -n resize get pod demo -o jsonpath='resize=[{.status.resize}]{"\n"}'
   kubectl -n resize get pod demo \
     -o jsonpath='allocated=[{.status.containerStatuses[0].allocatedResources}]{"\n"}'
   kubectl -n resize get pod demo -o jsonpath='{range .status.conditions[*]}{.type}={.status} {end}{"\n"}'
   ```

6. Resize memory, which this Pod's policy says requires a restart. Watch the counter the post never
   mentions.

   ```sh
   kubectl -n resize patch pod demo --subresource resize --patch \
     '{"spec":{"containers":[{"name":"app","resources":{"requests":{"cpu":"400m","memory":"128Mi"},"limits":{"cpu":"400m","memory":"128Mi"}}}]}}'
   sleep 15
   kubectl -n resize get pod demo -o jsonpath='restarts={.status.containerStatuses[0].restartCount} mem={.status.containerStatuses[0].resources.limits.memory}{"\n"}'
   ```

7. Ask for eight CPUs on a four-CPU node. This is the post's `Infeasible` value, and the question is
   where the word appears now.

   ```sh
   kubectl -n resize patch pod demo --subresource resize --patch \
     '{"spec":{"containers":[{"name":"app","resources":{"requests":{"cpu":"8","memory":"128Mi"},"limits":{"cpu":"8","memory":"128Mi"}}}]}}'
   sleep 15
   kubectl -n resize get pod demo \
     -o jsonpath='{range .status.conditions[?(@.type=="PodResizePending")]}{.type} reason={.reason} msg={.message}{"\n"}{end}'
   kubectl -n resize get pod demo -o jsonpath='resize=[{.status.resize}]{"\n"}'
   kubectl -n resize get pod demo -o jsonpath='enforced={.status.containerStatuses[0].resources.limits.cpu} restarts={.status.containerStatuses[0].restartCount}{"\n"}'
   kubectl -n resize patch pod demo --subresource resize --patch \
     '{"spec":{"containers":[{"name":"app","resources":{"requests":{"cpu":"400m","memory":"128Mi"},"limits":{"cpu":"400m","memory":"128Mi"}}}]}}'
   ```

8. Try to move the Pod from Guaranteed to Burstable by dropping the CPU request below the limit — a
   restriction that exists at the pin and is named nowhere in the post.

   ```sh
   kubectl -n resize patch pod demo --subresource resize --patch \
     '{"spec":{"containers":[{"name":"app","resources":{"requests":{"cpu":"200m","memory":"128Mi"},"limits":{"cpu":"400m","memory":"128Mi"}}}]}}'
   ```

9. Throw the switch the post tells you to throw, in the only direction left. Back the manifest up
   first; the restore at the end is not optional.

   ```sh
   sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/kube-apiserver.yaml.bak
   sudo sed -i '/- kube-apiserver$/a\    - --feature-gates=InPlacePodVerticalScaling=false' \
     /etc/kubernetes/manifests/kube-apiserver.yaml
   sleep 30
   kubectl get --raw /readyz 2>&1 | head -2
   sudo crictl logs --tail 8 "$(sudo crictl ps -a -q --name kube-apiserver | head -1)" 2>&1 | tail -8
   sudo cp /root/kube-apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml
   sleep 30
   kubectl get --raw /readyz
   ```

10. Offline, in a checkout of `kubernetes/website` at the pin, read the eight places this exercise
    took its claims from.

    ```sh
    cd /path/to/kubernetes/website/content/en
    sed -n '247,249p;257,262p' docs/concepts/workloads/pods/_index.md
    sed -n '758p;322p' docs/reference/kubernetes-api/core/pod-v1.md
    sed -n '23,38p;50,52p' docs/tasks/configure-pod-container/resize-container-resources.md
    sed -n '67,77p;115,134p' docs/tasks/configure-pod-container/resize-container-resources.md
    sed -n '167,195p' docs/tasks/configure-pod-container/resize-container-resources.md
    cat docs/reference/command-line-tools-reference/feature-gates/InPlacePodVerticalScalingAllocatedStatus.md
    grep -rn 'Proposed' --include='*.md' . | grep -v release-cadence
    grep -c resize docs/reference/using-api/deprecation-guide.md
    ```

**Expect**

Step 1 sets the floor. `kubectl` and the server are both v1.35, which is at or above the v1.32 the
`--subresource resize` flag needs; containerd reports 2.2.1, which is nine minor versions past the
v1.6.9 the post's first known issue is about. The metric lines are the two ladders above, printed by
the server: `InPlacePodVerticalScaling` at stage `STABLE` with value 1, and
`InPlacePodVerticalScalingAllocatedStatus` at stage `DEPRECATED` with value 0. Nothing in this
exercise needs enabling, and one thing in it cannot be disabled.

Step 2 gives a Pod in the `Guaranteed` class with `restartCount` 0, and a
`status.containerStatuses[0].resources` block that matches the manifest. That status block is the
post's second announced field, and it is exactly as announced.

Step 3 fails, and the message is the whole of the diff: `Pod "demo" is invalid: spec: Forbidden: pod
updates may not change fields other than ...`, followed by the list from `pods/_index.md:247-249`.
The post's sentence is not approximately right at the pin. It is refused.

Step 4 succeeds, and prints `spec=400m status=400m restarts=0`. Same verb, same patch body, same
object — one subresource. The container's CPU limit changed while it was running and the process
inside it never saw a signal, which is the thing the post was written to announce and which still
works exactly as promised.

Step 5 is where the post's paragraph on status fields goes quiet. `allocated=[]` is empty: the field
exists in the API at `pod-v1.md:253`, and the gate that populates it is off. `resize=[]` is the
interesting one — `pod-v1.md:322` says in one clause that a resize request sets it to `Proposed` and
in the next that the whole field is deprecated in favour of conditions, so whichever way it prints,
you have found out which of the two clauses your server obeys. The condition list holds the four
ordinary Pod conditions and neither resize condition, because the resize in step 4 finished.

Step 6 is the resize policy doing its job. `restarts=1` and `mem=128Mi`: because this container's
policy sets `RestartContainer` for memory, the same command that left the process alone for CPU
killed and restarted it for memory. Nothing else about the Pod changed — same name, same UID, same
node, same IP. That distinction, between restarting a container and replacing a Pod, is the one the
post's title is about, and it is only visible in `restartCount`.

Step 7 is the post's `Infeasible`, relocated. A `PodResizePending` condition appears with
`reason=Infeasible` and a message naming the node's capacity, and the enforced CPU limit is still
`400m` — the request is recorded and not granted, and the running container is untouched. Read the
`resize=[]` line against step 5's: this is the moment `pod-v1.md:322` promises the field will be
set. The last command puts the Pod back to something the node can satisfy, or the condition stays.

Step 8 fails with a message about the QoS class. `resize-container-resources.md:175-182` fixes the
class at creation: a Guaranteed Pod's requests must go on equalling its limits, so the one resize a
reader is most likely to reach for — give it a floor, let it burst — is the one that cannot be done
at all. The post's three use cases at `:55-63` are all within the rule, but nothing in the post says
the rule exists.

Step 9 is the locked gate. The API server does not start: `/readyz` refuses the connection for the
thirty seconds the container is crash-looping, and the log tail carries the refusal, naming the gate
and saying it cannot be set because it is locked to its default. Restoring the backup brings the
server back and `/readyz` prints `ok`. The prerequisite at `resize-container-resources.md:50-52`
asks you to ensure something that the same release made impossible to un-ensure, and this is what
that looks like from the node.

**Read on**

1. `resize-container-resources.md:169-193`, the nine limitations, read as a list of everything the
   post's four known issues did not know to warn about. Three of the nine are about memory alone,
   and the post names none of the three.

2. `pod-condition.md:181-188`, the two resize conditions in the Pod-conditions reference, and
   `pod-lifecycle.md:617-618`, which lists them among the conditions a Pod can carry — the
   vocabulary the post's `resize` field was replaced by, written down twice.

3. `resize-container-resources.md:79-104`, how deferred resizes are retried, and the priority order
   the kubelet uses between them. The post's `Deferred` value says only that the node "will keep
   retrying"; this says in what order, and names a gate that lets the scheduler preempt to make
   room.

4. `pod-v1.md:4693-4841` beside `:758`. Three HTTP verbs on a subresource of a field the same
   document says cannot be updated, twenty-five hundred lines apart in one generated reference.

5. *Unanswerable from the pin.* When `.status.resize` will actually be removed. `pod-v1.md:322`
   marks it deprecated and names no release, and `deprecation-guide.md` — the document whose job is
   exactly this — does not contain the string `resize` at all.

**Teardown**

```sh
kubectl delete ns resize --ignore-not-found
rm -f /tmp/resize-demo.yaml
grep -c feature-gates /etc/kubernetes/manifests/kube-apiserver.yaml || true
kubectl get --raw /readyz
```

The `grep` is there because step 9 is the only thing in this exercise that changes the node, and a
count of 0 is the only acceptable answer. If it is 1, the restore did not happen: copy
`/root/kube-apiserver.yaml.bak` back over the manifest and wait thirty seconds. Then return the
guest with the [standard teardown](../../strands/lab-topologies.md#teardown), or leave it up.

Back to the [2023 census](README.md).
