<a id="native-sidecar-containers"></a>

# The one sentence this post writes about its new field is wrong in both halves at the pin, three pinned pages give three different answers about whether a sidecar may carry a probe at all, and the post's only link into the API documentation has had no target since the material moved

**Post** — [Kubernetes v1.28: Introducing native sidecar containers](https://kubernetes.io/blog/2023/08/25/native-sidecar-containers/),
2023-08-25.

Todd Neal (AWS), Matthias Bertschy (ARMO), Sergey Kanzhelev (Google), Gunju Kim (NAVER) and Shannon
Kularathna (Google). 117 lines, 8,857 bytes, of which thirteen lines are acknowledgements. The
pattern it gives a name to was described eight years earlier in the post walked as [two of three
patterns that are still patterns](../2015/05-the-distributed-system-toolkit-patterns.md), which is
where the pattern-to-field argument lives; this exercise reads the field.

**As written**

The frame is that Kubernetes has had sidecars "since nearly the very beginning" without ever having
a word for one: "Until now, sidecars were a concept that Kubernetes users applied without native
support. The lack of native support has caused some usage friction, which this enhancement aims to
resolve" (`:16`). The post links the 2015 composite-containers post for the original description.

*What are sidecar containers in 1.28?* is the specification. "Kubernetes 1.28 adds a new
`restartPolicy` field to init containers that is available when the `SidecarContainers` feature gate
is enabled" (`:20`), and a six-line YAML fragment shows it: two `initContainers`, the second
carrying `restartPolicy: Always` (`:22-34`). Then one sentence that does all the constraining work:
"The field is optional and, if set, the only valid value is Always" (`:36`). Setting it changes
init-container behaviour three ways — the container restarts if it exits; any subsequent init
container starts immediately after the `startupProbe` has completed instead of waiting for this one
to exit; and "the resource usage calculation changes for the pod as restartable init container
resources are now added to the sum of the resource requests by the main containers" (`:38-40`). Pod
termination "continues to only depend on the main containers" (`:42`), and three properties make
restartable init containers ideal for the pattern: defined startup order, no extension of the Pod's
lifetime, and restart on exit (`:44-48`).

*When to use sidecar containers* lists four workloads — batch and AI/ML Pods that run to completion,
network proxies, log collection, and Jobs, where "sidecars for any purpose" no longer block
completion and "no additional configuration is required to ensure this behavior" (`:52-57`). *How
did users get sidecar behavior before 1.28?* names the two workarounds and what each cost: an init
container gives ordering but must exit, and a second main container runs for the Pod's lifetime but
gives no ordering and can block termination (`:61-64`).

*Transitioning existing sidecars to the new model* recommends the gate only in "short lived testing
clusters" at alpha, and says an existing sidecar configured as a main container "can be moved to the
`initContainers` section of the pod spec and given a `restartPolicy` of `Always`" (`:73`). *Known
issues* lists two, both promised as resolved before beta: the CPU, memory, device and topology
managers "are unaware of the sidecar container lifetime and additional resource usage", and "the
output of `kubectl describe node` is incorrect when sidecars are in use" (`:77-80`). *We need your
feedback!* asks about three things by name: the shutdown sequence with multiple sidecars, the
backoff timeout for crashing sidecars, and "the behavior of Pod readiness and liveness probes when
sidecars are running" (`:84-87`). *What's next?* forecasts one thing: "we're working on adding
termination ordering for sidecar and main containers. This will ensure that sidecar containers only
terminate after the Pod's main containers have exited" (`:93`). *More Information* is two bullets,
in this order: "[API for sidecar
containers](/docs/concepts/workloads/pods/init-containers/#api-for-sidecar-containers) in the
Kubernetes documentation", and the KEP (`:117-118`).

**As it runs now**

The sentence at `:36` is wrong in both of its halves, and neither half was wrong when it was
written. The field is no longer reached only through `initContainers`: `ContainerRestartRules` is
beta and on by default from v1.35, and `pod-lifecycle.md:397-400` says you can set `restartPolicy`
and `restartPolicyRules` "on _individual containers_ to override the Pod restart policy", applying
to app containers and to regular init containers alike. And `Always` is no longer the only valid
value: `:408-410` lists three — `Always`, `OnFailure`, `Never` — with `restartPolicyRules` layered
on top, each rule an `exitCodes` condition and a `Restart` action, evaluated in order (`:412-419`).
The API reference states the general form outright at `pod-v1.md:762-763`: "RestartPolicy defines
the restart behavior of individual containers in a pod. This overrides the pod-level restart
policy." What the post introduced as a special case of init containers became a general container
field, and the sidecar is now defined in terms of it rather than the other way round —
`pod-lifecycle.md:402-403`: "A Kubernetes-native sidecar container has its container-level
`restartPolicy` set to `Always`."

The documentation disagrees with itself about whether a sidecar may carry a probe, on one page and
then across two. `pod-v1.md:137` describes `initContainers` and says flatly that "Init containers
may not have Lifecycle actions, Readiness probes, Liveness probes, or Startup probes", with no
exception for the restartable kind — and a sidecar is an init container, which is the post's whole
design. `init-containers.md:54-58` says regular init containers do not support those fields and that
sidecar containers "_do_ support some probes". Twenty lines later the same page says sidecar
containers "support all these probes to control their lifecycle" (`:74-75`), and
`sidecar-containers.md:120` agrees with *all*. *None*, *some* and *all*, in three places, about the
same four fields. Step 6 settles it by asking the API server, which is the only one of the four that
has to be consistent.

The post's one link into the API documentation has no target.
`/docs/concepts/workloads/pods/init-containers/#api-for-sidecar-containers` occurs nowhere under
`content/en/docs` at the pin: there is no *API for sidecar containers* section on
`init-containers.md` or anywhere else, because the material moved to a page of its own,
`sidecar-containers.md`, 171 lines long, which did not exist when the post was written. That page's
further-reading list points back at this post (`:168`), so the two are linked in one direction only,
and it is the direction that works.

Both known issues were answered, one of them off the ceiling of this lab. `kubectl describe node`
reports allocated requests from the scheduler's effective Pod request, and the effective-request
rule at `sidecar-containers.md:140-158` now names sidecars explicitly: the Pod's effective request
is the higher of the effective init request and "the sum of all non-init containers(app and sidecar
containers) request/limit", with quota, limits and the Pod's cgroups all derived from the same
number (`:157-163`). Step 9 measures that. The resource managers are the other half, and the only
page in the pinned tree that says they understand sidecars is `pod-level-resource-managers.md`,
whose `:52-56` reads "Both standard init containers and restartable init containers (sidecars) are
fully supported" — on a page carrying `min-kubernetes-server-version: v1.36` and gated behind
`PodLevelResources` plus `PodLevelResourceManagers`, the second of which is beta and off by default
at the pin. Eight releases after the post, and still not something a v1.35 cluster can be asked.

The forecast landed. `pod-lifecycle.md:1006-1008` is the *What's next* paragraph turned into
behaviour: "the kubelet will delay sending the TERM signal to these sidecar containers until the
last main container has fully terminated. The sidecar containers will be terminated in the reverse
order they are defined in the Pod spec." The reverse-order half is more than the post promised. So
is `:1017-1018`, which tells you to go back and delete work you did before 1.28: "if you have used
`preStop` hooks to control the termination order without sidecar containers, you can now remove them
and allow the kubelet to manage sidecar termination automatically."

Two of the three things the post asked for feedback about are documented answers now, and one is
documented twice with different force. Pod readiness: "If a `readinessProbe` is specified for this
init container, its result will be used to determine the `ready` state of the Pod"
(`sidecar-containers.md:62-63`), which step 8 drives from a file. The shutdown sequence with
multiple sidecars: reverse order, above. The third, backoff for crashing sidecars, is folded into
the general container backoff at `pod-lifecycle.md:405` and never treated as a sidecar question.
Against that, `sidecar-containers.md:106-110` says something the termination paragraph does not
prepare you for — that a sidecar's graceful termination "is less important", that when other
containers use all the grace period sidecars "will receive the `SIGTERM` signal, followed by the
`SIGKILL` signal, before they have time to terminate gracefully", and that non-zero sidecar exit
codes on Pod termination "are normal" and "should be generally ignored by the external tooling".

The tutorial that the concept page sends adopters to has not moved since beta.
`pod-sidecar-containers.md:91-92` tells you to "make sure that both API server and Nodes are at
Kubernetes version v1.29 or later", `:103-104` to ensure the feature gate is enabled "for the API
server(s) within the control plane **and** for all nodes", and `:120-124` prints the output you are
looking for as `kubernetes_feature_enabled{name="SidecarContainers",stage="BETA"} 1`. The gate has
been stable and locked since v1.33. A reader following that page on a current cluster is checking a
switch that cannot be off, against a stage string that will not match.

**What this exercise does not cover, and where it lives**

The pattern-to-field argument, the two pre-1.28 workarounds run side by side, and the Job that never
completes because a helper is still alive all belong to [the composite-containers
exercise](../2015/05-the-distributed-system-toolkit-patterns.md), together with the release
provenance of the gate beyond its stages and the KEP-753 reading. That exercise proves the field
solves the lifecycle problem; this one starts from a cluster where the field is stable and asks what
has happened to it since. Where a sidecar's resources are written into the Pod's cgroups is [the
cgroup v2 version](../2022/06-cgroupv2-ga-1-25.md).

**The diff, and why**

The post ***broke*** in exactly one sentence and one link. The sentence is the post's `:36`, and it
broke twice over — once in v1.34 when `ContainerRestartRules` arrived at alpha and made
`restartPolicy` a field on every container, and once in v1.35 when that gate turned on by default,
which is the version this lab runs. The link is the *More Information* bullet, and it broke by
success: the API material the post pointed at got large enough to need its own page. A reader who
follows the post's manifest is fine; a reader who follows its constraint will not try things that
work.

Everything else is ***still right***, including the parts the post could not know it was right
about. The three behaviour changes at the post's `:38-40` are the pin's behaviour. The Job claim at
`:57` holds with no configuration. The *What's next* forecast landed, and landed larger —
reverse-order shutdown was not promised. Both *Known issues* were fixed, the second of them in a
place a v1.35 cluster cannot look. The pressure in all of this is the same one: a field introduced
to describe one pattern turned out to describe a general question about container lifetime, and the
project generalised the field rather than adding more special cases.

The gate is stable and locked, so there is nothing to enable; the exercise that owns this gate's
provenance is linked above and is not repeated here.

`SidecarContainers`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.28 – v1.28 |
| beta | `true` | — | v1.29 – v1.32 |
| stable | `true` | `true` | v1.33 – |

`ContainerRestartRules`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.34 – v1.34 |
| beta | `true` | — | v1.35 – |

Neither file carries `removed: true` at the pin, and neither carries `former_titles:`. The
`SidecarContainers` body is one sentence that defines the feature as setting "the `restartPolicy` of
an init container to `Always`" and sends the reader to `sidecar-containers.md`; the
`ContainerRestartRules` body sends them to `pod-lifecycle.md`. The two gates read as one feature
split across two files.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 vCPU, 25G, at `10.10.10.180`.
Every question here is a kubelet question answered inside one Pod, and the node's
allocated-resources table in step 9 is easier to read when nothing else is competing for it.
Provision with the [standard steps](../../strands/lab-topologies.md#provision) and the [node
baseline](../../strands/lab-topologies.md#node-baseline-steps). The lab runs Kubernetes v1.35, which
is the first release where `ContainerRestartRules` is on without being asked; steps 4 and 5 will
fail on v1.34 and earlier, and that failure is itself the post's sentence being true.

**Do**

1. Ask the cluster about both gates, and run the adoption tutorial's own check against a cluster
   eight releases past the one it was written for.

   ```sh
   kubectl version | head -2
   kubectl create ns sidecar
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' \
     | grep -E 'SidecarContainers|ContainerRestartRules' || echo "neither gate in the series"
   NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/metrics" | grep kubernetes_feature_enabled \
     | grep SidecarContainers || echo "not reported by the node either"
   ```

2. Build the post's manifest, shape unchanged from its `:22-34`, with images that exist.

   ```sh
   cat > /tmp/post-shape.yaml <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: post-shape, namespace: sidecar }
   spec:
     volumes:
       - name: shared
         emptyDir: {}
     initContainers:
       - name: secret-fetch
         image: busybox:1.36
         command: ["sh", "-c", "echo fetched > /shared/secret"]
         volumeMounts: [{ name: shared, mountPath: /shared }]
       - name: network-proxy
         image: busybox:1.36
         restartPolicy: Always
         command: ["sh", "-c", "while true; do sleep 5; done"]
     containers:
       - name: app
         image: busybox:1.36
         command: ["sh", "-c", "cat /shared/secret; sleep 3600"]
         volumeMounts: [{ name: shared, mountPath: /shared }]
   EOF
   kubectl apply -f /tmp/post-shape.yaml
   kubectl -n sidecar wait --for=condition=Ready pod/post-shape --timeout=90s
   kubectl -n sidecar get pod post-shape -o jsonpath='{range .status.initContainerStatuses[*]}{.name}: started={.started} ready={.ready}{"\n"}{end}'
   kubectl -n sidecar logs post-shape -c app
   ```

3. Ask the API where the field lives now. The post adds it to init containers; the
   composite-containers exercise already reads it there, so read the other side.

   ```sh
   kubectl explain pod.spec.containers.restartPolicy
   kubectl explain pod.spec.containers.restartPolicyRules
   kubectl explain pod.spec.containers.restartPolicyRules.exitCodes
   ```

4. Test the post's constraint directly, with the pin's own example from `pod-lifecycle.md:424-439` —
   two app containers in one Pod, one of which may never restart — shortening the second container's
   sleep from 1800 seconds so the restarts are visible while you watch.

   ```sh
   cat > /tmp/restart-values.yaml <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: on-failure-pod, namespace: sidecar }
   spec:
     restartPolicy: OnFailure
     containers:
       - name: try-once-container
         image: busybox:1.36
         command: ["sh", "-c", "echo 'Only running once' && sleep 10 && exit 1"]
         restartPolicy: Never
       - name: on-failure-container
         image: busybox:1.36
         command: ["sh", "-c", "echo 'Keep restarting' && sleep 20 && exit 1"]
   EOF
   kubectl apply -f /tmp/restart-values.yaml
   kubectl -n sidecar get pod on-failure-pod -w --output-watch-events=false &
   sleep 90; kill %1
   kubectl -n sidecar get pod on-failure-pod \
     -o jsonpath='{range .status.containerStatuses[*]}{.name}: restarts={.restartCount} state={.state}{"\n"}{end}'
   ```

5. Now the part of the field that has no counterpart anywhere in the post: a rule that decides on
   the exit code. This is the pin's sample at `:466-483`, whose container exits `0` and therefore
   never triggers the rule it carries; this one exits `42`.

   ```sh
   cat > /tmp/restart-rules.yaml <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: restart-on-exit-codes, namespace: sidecar }
   spec:
     restartPolicy: Never
     containers:
       - name: restart-on-exit-codes
         image: busybox:1.36
         command: ["sh", "-c", "echo attempt; sleep 10; exit 42"]
         restartPolicy: Never
         restartPolicyRules:
           - action: Restart
             exitCodes:
               operator: In
               values: [42]
   EOF
   kubectl apply -f /tmp/restart-rules.yaml
   sleep 60
   kubectl -n sidecar get pod restart-on-exit-codes \
     -o jsonpath='phase={.status.phase} restarts={.status.containerStatuses[0].restartCount}{"\n"}'
   kubectl -n sidecar logs restart-on-exit-codes | head -5
   ```

6. Settle the probe question by submitting it. One sidecar carrying all four of the disputed fields,
   and one regular init container carrying one of them.

   ```sh
   cat > /tmp/probes.yaml <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: probed, namespace: sidecar }
   spec:
     initContainers:
       - name: sidecar
         image: busybox:1.36
         restartPolicy: Always
         command: ["sh", "-c", "touch /tmp/up; while true; do sleep 5; done"]
         startupProbe: { exec: { command: ["test", "-f", "/tmp/up"] }, periodSeconds: 2 }
         readinessProbe: { exec: { command: ["test", "-f", "/tmp/up"] }, periodSeconds: 2 }
         livenessProbe: { exec: { command: ["true"] }, periodSeconds: 5 }
         lifecycle: { preStop: { exec: { command: ["sh", "-c", "echo stopping"] } } }
     containers:
       - name: app
         image: busybox:1.36
         command: ["sh", "-c", "sleep 3600"]
   EOF
   kubectl apply -f /tmp/probes.yaml
   kubectl -n sidecar run regular-init --image=busybox:1.36 --dry-run=client -o yaml \
     --command -- sh -c 'sleep 5' > /tmp/regular.yaml
   kubectl apply --dry-run=server -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: regular-init-probe, namespace: sidecar }
   spec:
     initContainers:
       - name: setup
         image: busybox:1.36
         command: ["sh", "-c", "sleep 5"]
         readinessProbe: { exec: { command: ["true"] }, periodSeconds: 2 }
     containers:
       - name: app
         image: busybox:1.36
         command: ["sh", "-c", "sleep 3600"]
   EOF
   ```

7. Measure the post's forecast at its `:93`. Two sidecars and one main container, each announcing
   its own `SIGTERM` with a timestamp, then delete the Pod and read the order off the logs.

   ```sh
   cat > /tmp/term-order.yaml <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: term-order, namespace: sidecar }
   spec:
     terminationGracePeriodSeconds: 60
     initContainers:
       - name: sidecar-one
         image: busybox:1.36
         restartPolicy: Always
         command: ["sh", "-c", "trap 'echo TERM $(date +%s.%N) sidecar-one; sleep 2; exit 0' TERM; while true; do sleep 1; done"]
       - name: sidecar-two
         image: busybox:1.36
         restartPolicy: Always
         command: ["sh", "-c", "trap 'echo TERM $(date +%s.%N) sidecar-two; sleep 2; exit 0' TERM; while true; do sleep 1; done"]
     containers:
       - name: app
         image: busybox:1.36
         command: ["sh", "-c", "trap 'echo TERM $(date +%s.%N) app; sleep 5; exit 0' TERM; while true; do sleep 1; done"]
   EOF
   kubectl apply -f /tmp/term-order.yaml
   kubectl -n sidecar wait --for=condition=Ready pod/term-order --timeout=90s
   kubectl -n sidecar delete pod term-order --wait=false
   sleep 25
   for c in app sidecar-two sidecar-one; do
     kubectl -n sidecar logs term-order -c $c 2>/dev/null | grep TERM || echo "$c: no TERM seen"
   done
   ```

8. Drive Pod readiness from the sidecar, which is the first of the three things the post asked for
   feedback about.

   ```sh
   kubectl -n sidecar get pod probed \
     -o jsonpath='ready={.status.conditions[?(@.type=="Ready")].status}{"\n"}'
   kubectl -n sidecar exec probed -c sidecar -- rm /tmp/up
   sleep 15
   kubectl -n sidecar get pod probed \
     -o jsonpath='ready={.status.conditions[?(@.type=="Ready")].status}{"\n"}'
   kubectl -n sidecar get pod probed -o jsonpath='{range .status.initContainerStatuses[*]}{.name}: ready={.ready}{"\n"}{end}'
   kubectl -n sidecar exec probed -c sidecar -- touch /tmp/up
   sleep 15
   kubectl -n sidecar get pod probed \
     -o jsonpath='ready={.status.conditions[?(@.type=="Ready")].status}{"\n"}'
   ```

9. Answer the second known issue with arithmetic the node has to agree with.

   ```sh
   kubectl describe node "$NODE" | sed -n '/Allocated resources/,/^Events/p'
   cat > /tmp/accounting.yaml <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: accounting, namespace: sidecar }
   spec:
     initContainers:
       - name: heavy-init
         image: registry.k8s.io/pause:3.10
         resources: { requests: { memory: 300Mi } }
       - name: side
         image: registry.k8s.io/pause:3.10
         restartPolicy: Always
         resources: { requests: { memory: 200Mi } }
     containers:
       - name: app
         image: registry.k8s.io/pause:3.10
         resources: { requests: { memory: 200Mi } }
   EOF
   kubectl apply -f /tmp/accounting.yaml
   kubectl -n sidecar wait --for=condition=Ready pod/accounting --timeout=90s
   kubectl describe node "$NODE" | sed -n '/Non-terminated Pods/,/Allocated resources/p' | grep -E 'accounting|NAMESPACE'
   kubectl describe node "$NODE" | sed -n '/Allocated resources/,/^Events/p'
   ```

10. Offline, in a checkout of `kubernetes/website` at the pin, read the three voices on probes and
    the link with no target.

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -rn 'api-for-sidecar-containers' --include='*.md' docs | wc -l
    grep -n 'may not have Lifecycle actions' docs/reference/kubernetes-api/core/pod-v1.md
    sed -n '54,58p;74,75p' docs/concepts/workloads/pods/init-containers.md
    sed -n '118,121p' docs/concepts/workloads/pods/sidecar-containers.md
    sed -n '120,124p' docs/tutorials/configuration/pod-sidecar-containers.md
    cat docs/reference/command-line-tools-reference/feature-gates/ContainerRestartRules.md
    ```

**Expect**

Step 1 prints `SidecarContainers` at stage `STABLE` and `ContainerRestartRules` at stage `BETA`,
both with value 1 — or drops the locked one from the series entirely, depending on the build. The
node endpoint agrees with the API server, which is the check the adoption tutorial asks you to make
and the only part of that page still worth running. Note the stage string:
`pod-sidecar-containers.md:120-124` tells you to look for `stage="BETA"` and would have you conclude
the feature is off.

Step 2 is the post working exactly as written, three years on. Both init container statuses report
`started=true`; `secret-fetch` also reports `ready=true` after it exits, `network-proxy` reports
`ready=true` while still running, and `app` logs `fetched` — the ordering guarantee the post's first
bullet promises, with no gate set anywhere. This is the baseline against which the rest of the
exercise is a surprise.

Step 3 is where the post's sentence comes apart. `kubectl explain pod.spec.containers.restartPolicy`
returns a field description, not `error: field "restartPolicy" does not exist`, and it describes the
general form from `pod-v1.md:762-763` rather than the sidecar special case. `restartPolicyRules` is
there too, with an `action` and an `exitCodes` condition underneath it. The post says the field is
added to init containers and that its only valid value is `Always`; two `explain` calls disagree
with both halves, and neither of them is about sidecars at all.

Step 4 runs that disagreement. `try-once-container` exits 1 after ten seconds and stays down —
`restarts=0`, `state` terminated — while `on-failure-container` exits 1 after twenty seconds and
comes straight back, its restart count climbing every twenty seconds or so as the backoff grows. Two
containers, one Pod, one Pod-level `restartPolicy` of `OnFailure`, and two different outcomes
decided per container. Nothing in this Pod is a sidecar; the field the post introduced for sidecars
is doing all of it.

Step 5 restarts on an exit code. `restarts` climbs above 0 and the Pod stays out of `Failed` even
though its Pod-level policy is `Never` and its container-level policy is `Never` as well, because
the rule matched first. Change the `42` in the command to any other number and re-apply: the rule
stops matching, the container-level `Never` takes over and the Pod goes to `Failed`. Worth noticing
that the pinned sample this is copied from exits `0` (`pod-lifecycle.md:476`), so as published it
never triggers the rule it exists to demonstrate.

Step 6 is the answer to the three-way disagreement, and it comes in two parts. The `probed` Pod is
accepted and reaches `Ready`, so a sidecar carries `startupProbe`, `readinessProbe`, `livenessProbe`
and `lifecycle` — all four, which is `init-containers.md:74-75` and `sidecar-containers.md:120`
against `:54-58`'s *some*. The server-side dry run of `regular-init-probe` is rejected with a
validation error naming `spec.initContainers[0].readinessProbe` as a field that may not be set,
which is `pod-v1.md:137` being right about regular init containers and silent about the exception.
The API server holds all three positions at once without contradiction; only the prose contradicts.

Step 7 prints three timestamped lines, and the order is the finding: `app` first, then
`sidecar-two`, then `sidecar-one`. The gap between `app`'s line and `sidecar-two`'s is at least the
five seconds `app` sleeps before exiting, which is the delay `pod-lifecycle.md:1006-1008` promises.
The two sidecar lines arrive in reverse declaration order, which the post never forecast. If a
container's line is missing, it was killed before it could log — read that as the grace period
expiring rather than as an ordering failure, and raise `terminationGracePeriodSeconds`.

Step 8 makes the Pod unready without touching the app. Removing `/tmp/up` fails the sidecar's
readiness probe, and within about two probe periods the Pod's `Ready` condition flips to `False`
while `app` keeps running and its own status stays ready; the init container status for `sidecar`
reports `ready=false`. Restoring the file flips it back. A Service in front of this Pod would have
removed it from its endpoints on the strength of a container that is not the application — which is
the answer to the second thing the post asked for feedback about, and it is a sharper answer than
the post anticipated.

Step 9 is the arithmetic from `sidecar-containers.md:140-158`. The `accounting` Pod requests 300Mi
on a regular init container, 200Mi on a sidecar and 200Mi on the app container; the node's
*Allocated resources* table should rise by 400Mi, not by 300Mi and not by 700Mi — the sum of the
non-init containers, which now includes the sidecar, beats the effective init request of 300Mi. If
it rises by 200Mi you have found the post's second known issue still alive, and it is worth saying
so precisely. The per-Pod line in *Non-terminated Pods* should carry the same 400Mi.

Step 10 is the paperwork. The anchor count is `0`: the post's only link into the API documentation
has had no target since the material moved to a page of its own. The three probe sentences print one
after another and can be read as a set — *may not have*, *some*, *all these* — and the tutorial's
`stage="BETA"` prints beside a gate file whose last stage is `stable` with `locked: true`.

**Read on**

1. `sidecar-containers.md:106-110`, on sidecar exit codes being normal and ignorable. Read it
   against step 7's timestamps and work out which of the two descriptions your grace period
   produced.

2. `pod-lifecycle.md:485-488`, the paragraph warning that restart rules inherit every inconsistency
   of the restart policy — kubelet restarts, runtime garbage collection and control-plane
   connectivity can all re-run a container you asked never to be re-run.

3. `pod-level-resource-managers.md:40-56`, for what sidecar-aware resource management looks like
   when it finally arrives, and which two gates you would have to turn on to see it.

4. `pod-sidecar-containers.md:128-196`, the adoption tutorial's sections on third-party tooling and
   on automatic sidecar injection. The post says an existing sidecar "can be moved" to
   `initContainers`; this is the page that says what else has to move with it.

5. *Unanswerable from the pin.* Whether the classic per-container CPU, memory, device and topology
   managers became sidecar-aware, and in which release. The only statement in the tree is about the
   pod-level managers, on a page that needs v1.36 and two feature gates; nothing under `content/en`
   says what the per-container managers do with a restartable init container today.

**Teardown**

```sh
kubectl delete ns sidecar --ignore-not-found
rm -f /tmp/post-shape.yaml /tmp/restart-values.yaml /tmp/restart-rules.yaml       /tmp/probes.yaml /tmp/regular.yaml /tmp/term-order.yaml /tmp/accounting.yaml
kubectl describe node "$NODE" | sed -n '/Allocated resources/,/^Events/p'
```

The last line is worth reading before you leave: allocated requests should be back where step 9
found them. Then return the guest with the [standard
teardown](../../strands/lab-topologies.md#teardown), or leave it up for the next row.

Back to the [2023 census](README.md).
