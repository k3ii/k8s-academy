<a id="start-sidecar-first"></a>

# The field the whole question turns on is referenced three times in the pinned API reference and defined nowhere in it, the rule that reads it is stated twice and both times about a different container, and the 488-line page documenting the lever the post lands on never says sidecar

**Post** — [Start Sidecar First: How To Avoid Snags](https://kubernetes.io/blog/2025/06/03/start-sidecar-first/),
2025-06-03.

13,166 bytes, 234 lines, 1,657 words of body; one author, Agata Skorupka of The Scale Factory. Seven
`##` headings, no `###`, seven fenced blocks, no Hugo shortcodes, nine markdown links across eight
distinct targets, trailing whitespace on five lines. It is the only one of 2025's twelve `walk`
verdicts whose census row carries no Kubernetes version, and that is not an oversight: the behaviour
it investigates has not changed since the gate went on by default, so there is no release to name.

**As written**

The post opens by pointing at a sibling post from six weeks earlier for the patterns, then narrows
to one question: how do you make the main application container wait until a sidecar is not merely
started but *fully running and ready to serve* (`:36`). Its refresher at `:14-16` dates native
sidecars to the v1.29.0 release and shows a manifest snippet at `:18-27`. Its `:30` gives three
properties in one sentence — init containers always launch before the main application, native
sidecars terminate after it, and with Jobs a sidecar "should still be alive and could potentially
even restart after the owning Job is complete".

The investigation is four experiments in order. A `readinessProbe` that can never pass (`:48-86`),
whose `kubectl describe` transcript at `:90-112` carries two `Started container` events one second
apart in the `Age` column while the sidecar is still unready; the post concludes at `:114` that
"myapp has been started before the sidecar is ready. That was not the result I wanted to achieve". A
`startupProbe`, first as `httpGet` (`:120-159`) and then as an `exec` sleeping fifteen seconds
(`:163-170`), which the post reports at `:173` "helps to delay the main application start until the
sidecar is ready. It's not optimal, but it works". A `postStart` lifecycle hook polling `curl` in a
loop (`:179-200`), which the post says "will also do the job, but I'd have to write my own
mini-shell script, which is even less efficient" (`:177`). And a `livenessProbe` that always fails
(`:207-215`), after which "the sidecar has a restart count above 0. Nevertheless, the main
application is not restarted nor influenced at all" (`:217`).

Three sentences are carried forward into the exercise. `:36` cites the kubelet source at a pinned
commit for the claim that sidecar and main container start "almost in parallel" — the only external
code link the post makes, and the only citation it offers for the rule it is testing. `:37` names
the reason the question is hard: "the problem with sidecars is there's no obvious success signal",
because an init container's exit status 0 is unambiguous and a running sidecar's state is not. And
the summary table at `:224-229` records the four answers as a grid, whose `startupProbe` row is the
only one with **Yes** in both of the first two columns.

**As it runs now**

**The field the whole question turns on has no definition in the pinned API reference.** The thing
that decides when the main application containers start is `started` on the sidecar's entry in
`.status.initContainerStatuses`. `pod-v1.md` carries 103 `##` type sections, among them
`ContainerState`, `ContainerStateRunning`, `ContainerStateTerminated`, `ContainerStateWaiting`,
`ContainerPort`, `ContainerUser`, `ContainerResizePolicy` and `ContainerRestartRule`. It names
`ContainerStatus` three times, at `:261`, `:265` and `:281`, each time as the element type of a
status array, and it defines that type nowhere. Neither does any other page under
`docs/reference/kubernetes-api/`. The cluster will hand you the field on request; the reference will
not tell you what it means.

**The rule that reads the field is stated twice, and both times about a different container.**
`sidecar-containers.md:71-75` is the fuller of the two: "After a sidecar-style init container is
running (the kubelet has set the `started` status for that init container to true), the kubelet then
starts the next init container from the ordered `.spec.initContainers` list. That status either
becomes true because there is a process running in the container and no startup probe defined, or as
a result of its `startupProbe` succeeding." The last sentence of `pod-v1.md:762` says the same thing
in one clause: "the next init container starts immediately after this init container is started, or
after any `startupProbe` has successfully completed." Both are about *the next init container*. The
post's entire question is about the main application containers, and no page in the pinned tree
states the rule for them.

**The page that documents the lever does not contain the word.** `probes.md` is 488 lines, the
tree's canonical account of startup, liveness and readiness probes — mechanisms, results,
configuration fields, HTTP redirect handling, gRPC. It uses the word "sidecar" zero times and the
phrase "init container" zero times. Thirty-seven files under `docs/`, outside the generated
command-line reference, name sidecars; this is not one of them.

**Four links point at a probe anchor that left the page they name.** `sidecar-containers.md:120` and
`:170`, and `init-containers.md:75` and `:372`, all link to
`/docs/concepts/workloads/pods/pod-lifecycle/#types-of-probe`. The heading at `pod-lifecycle.md:783`
is `## Container probes`, and `{#types-of-probe}` is defined at `probes.md:21` — the only place in
the tree it is defined. Six other inbound links naming `pod-lifecycle/#container-probes` resolve
fine. A fifth broken one sits in the gate file: `StartupProbe.md:26` points at
`pod-lifecycle/#when-should-you-use-a-startup-probe`, a heading now at `probes.md:95`. All four of
the first set are on the two pages this post is about.

**The post's own probe links point at a path with no file behind it.** All three — `:44`, `:46` and
`:204` — name `/docs/concepts/configuration/liveness-readiness-startup-probes/`.
`docs/concepts/configuration/` holds six files at the pin and none of them is about probes; the path
survives as a 301 to `/docs/concepts/workloads/pods/probes/`. The post also writes the same target
two ways: `:44` and `:204` use the site-relative form, `:46` the absolute one with the hostname
spelled out.

**One of the post's seven fenced blocks is not valid YAML.** The refresher snippet at `:18-27` fails
to load with a scanner error at `mountPath`: `volumeMounts:` opens a block sequence whose first item
sits at column four and whose second key sits at column eight. The other six blocks parse. The
snippet is `examples/application/deployment-sidecar.yaml:24-32` dedented out of its `spec:`, with
the file's standalone comment moved onto the `restartPolicy` line and the `volumeMounts` list
flattened by one level too many.

**The example it was copied from is still there, unchanged, and no sidecar example anywhere carries
a probe.** `deployment-sidecar.yaml` and `job/job-sidecar.yaml` are the two the sidecar page
renders, at `:54` and `:91` by `code_sample` shortcode, and both files end without a trailing
newline. Seven files under `examples/` define nine containers with `restartPolicy: Always` inside
`initContainers`, and not one of the nine carries a `startupProbe`, a `readinessProbe` or a
`livenessProbe`. The technique this post arrives at has no worked example in the tree.

**The probe summary is written out on three concept pages.** `probes.md` is the canonical one.
`pod-lifecycle.md:783-840` repeats it: twenty-nine lines longer than forty characters are
byte-identical between the two files, and `pod-lifecycle.md:794-797` tells the reader to go to
`probes.md` for mechanisms, fields and usage guidance before restating all three probe descriptions
anyway. `pods/_index.md:479-489` is a third and older copy, naming the mechanisms by their Go type
names.

**The two pages disagree about what a failed startup probe restarts.** `probes.md:39`: "If the
startup probe fails, the kubelet kills the container, and the container is subjected to its restart
policy." `pod-v1.md:774`, for the same field, says "StartupProbe indicates that the Pod has
successfully initialized" and "If this probe fails, the Pod will be restarted, just as if the
`livenessProbe` failed." One says container twice, the other says Pod twice. Step 6 settles it by
failing one.

**The page titled Init containers denies the post's premise outright.** `init-containers.md:60-63`
says the kubelet runs each init container sequentially, each must succeed before the next can run,
and "when all of the init containers have run to completion, kubelet initializes the application
containers for the Pod and runs them as usual". `:71-72` repeats it: "the main container does not
start until all the init containers have successfully completed." A sidecar is an init container
that never completes, which the same page concedes at `:54-58`. Read literally, a Pod with a sidecar
would never start its main container. Step 1 settles it.

**A third and a fourth voice on ordering, each wrong in its own direction.**
`pod-sidecar-containers.md:62-63` lists as a benefit that "you can configure a native sidecar
container to start ahead of init containers", which reads as a category distinction where the
difference is one of position in a single list. `pods/_index.md:475` says sidecars "start up before
the main application Pod", where the word wanted is container.

**The gate file's link names a section its target does not have.** `SidecarContainers.md:24` sends
the reader to "Sidecar containers and restartPolicy" on `sidecar-containers.md`. That page carries
nine headings and none of them is that. Separately, `pod-sidecar-containers.md:74` labels a link
"differences from init containers" and points it at `#differences-from-application-containers`.

**The post and the API reference disagree about sidecars in Jobs, and a third page sides with the
post.** The post's `:30` says a sidecar "should still be alive and could potentially even restart
after the owning Job is complete". `pod-v1.md:762` says "Once all regular containers have completed,
all init containers with `restartPolicy` `Always` will be shut down."
`pod-sidecar-containers.md:71-72` sides with the post: "with Jobs, built-in sidecar containers would
keep being restarted once they are done, even if regular containers would not with Pod's
`restartPolicy: Never`." Nothing in this exercise settles it — Jobs are outside the Pod-shaped
budget of the ten steps below, and the disagreement is recorded here so the next reader knows it is
open.

**The summary table disagrees with itself in one cell and formats two rows differently.** `:226`
answers "sidecar starts before the main app?" for `readinessProbe` with "**Yes**, but it's almost in
parallel (effectively **no**)", bolding both words. `:227` gives `livenessProbe` the same answer
with the leading **Yes** unbolded. `postStart` at `:229` is the only one of the four row labels not
set in backticks.

**The post's `httpGet` probe is shaped exactly like the hazard the probe page names.** Its
`:152-153` set `initialDelaySeconds: 5` with `periodSeconds: 30`. `probes.md:248` says that "in some
older Kubernetes versions, the `initialDelaySeconds` might be ignored if `periodSeconds` was set to
a value higher than `initialDelaySeconds`. However, in current versions, `initialDelaySeconds` is
always honored and the probe will not start until after this initial delay." The post never says
which it was writing against. Step 4 puts a number on what the cluster does now.

**What this exercise does not cover, and where it lives**

Whether a sidecar may carry each probe field at all, and what the API server's validation actually
accepts where three pages give three answers, is settled by submitting it in [the exercise on the
post that introduced the field](../2023/09-native-sidecar-containers.md), which also owns driving
Pod readiness from a sidecar's `readinessProbe`, the node's resource arithmetic for sidecars, and
the termination order at the other end of the Pod's life. The `postStart` hook's own timing —
whether it delays the container reaching `Running`, and what the two lifecycle pages say about that
— belongs to [the container lifecycle
exercise](04-kubernetes-v1-33-updates-to-container-lifecycle.md). The redirect file that keeps the
post's probe links alive is read in [the Endpoints deprecation
exercise](02-endpoints-deprecation.md), which is where that instrument was opened. The four probe
mechanisms, and the list of three that is a list of four, are [the gRPC health checking
exercise's](../2018/07-health-checking-grpc.md); the gate behind the newest of them is [the gRPC
probe beta exercise's](../2022/02-grpc-probes-now-in-beta.md). What each of the three probes does to
an ordinary container, and why a slow-booting application with only a liveness probe restart-loops
forever, is [the lab that fails one probe at a time](../../labs/01/09-probes-three-kinds.md); this
exercise asks only what a sidecar's probe does to the container beside it. The argument from pattern
to API field is [the composite containers
exercise's](../2015/05-the-distributed-system-toolkit-patterns.md).

**The diff, and why**

**Still right.** All four experiments reproduce. The readiness probe does not delay the main
container, the startup probe does, the liveness probe restarts only the sidecar, and the ordering is
unchanged from the release the post was written against. This is the only one of the year's twelve
`walk` verdicts whose census row names no Kubernetes version, because there is no release at which
any of this moved.

**Never absorbed.** The post's finding is that `startupProbe` on the sidecar is the supported lever
for delaying the main application, and the pinned tree does not say so anywhere. `probes.md` does
not know sidecars exist. `sidecar-containers.md:71-75` states the mechanism in terms of the next
init container and stops. Nine sidecars across seven example files carry no probe between them. A
reader who arrives at the documentation with the post's question leaves without the answer.

**Wrong when it was published.** The refresher snippet at `:18-27` has never been loadable — it is
the tree's own example with one list flattened a level too far, and it fails to parse today exactly
as it would have on the day it went up. The same paragraph dates native sidecars to the v1.29.0
release, which is the release the gate went on by default; `SidecarContainers.md` puts its alpha at
1.28, one release earlier.

**Overtaken by stasis.** The behaviour stood still and the documentation moved out from under the
post. The probe material was split into its own page, taking `{#types-of-probe}` with it and leaving
four inbound links on the two pages this post is about pointing at an anchor `pod-lifecycle.md` no
longer has; the concept page the post links three times moved out of `concepts/configuration/`
entirely. Nothing the post claims became false. Every path it offers a reader became indirect.

**The ladder**

`SidecarContainers.md` is a three-rung ladder with the shortest possible alpha: alpha at 1.28 and to
1.28, beta and on by default from 1.29 through 1.32, stable and locked from 1.33. The lab runs
v1.35, so the gate is locked on and cannot be turned off; there is nothing to flip, and this
exercise is the rarer kind that mutates no node. Of the three probe fields it leans on, only
`startupProbe` ever carried a gate of its own: alpha at 1.16, beta at 1.18, stable at 1.20, and
`removed: true` after 1.23. That file outlives the flag it documented, and the one sentence left in
it is the fifth broken probe link in the tree.

The ladder that matters here is the one the documentation did not climb. The gate reached stable in
1.33 and the guidance the post writes has not appeared in any of the four releases since. There is
no right-hand column to wait for, because nothing is pending: the feature is finished and the page
that would explain how to use it is the one that does not mention it.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180`, Kubernetes v1.35,
[provisioned](../../strands/lab-topologies.md#provision) and
[baselined](../../strands/lab-topologies.md#node-baseline-steps) as usual. Nothing is flipped on the
node and nothing is restarted: every step below is a Pod, and the whole exercise lives and dies
inside one namespace. Timing matters in four of the ten steps, so run them on an otherwise idle
cluster and pull the two images once, in step 1, before anything is measured.

**Do**

1. Ask the cluster for the field the reference does not define, then put a number on the post's
   "almost in parallel".

   ```sh
   kubectl version -o yaml | grep gitVersion
   kubectl explain pod.status.initContainerStatuses.started
   kubectl explain pod.spec.initContainers.restartPolicy | tail -6
   kubectl create namespace bw-ssf
   kubectl -n bw-ssf apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: bare }
   spec:
     initContainers:
       - name: side
         image: busybox:1.36
         restartPolicy: Always
         command: ["sh", "-c", "while true; do sleep 5; done"]
     containers:
       - name: app
         image: busybox:1.36
         command: ["sh", "-c", "sleep 3600"]
   EOF
   kubectl -n bw-ssf wait --for=condition=Ready pod/bare --timeout=180s
   kubectl -n bw-ssf get pod bare -o jsonpath='side started={.status.initContainerStatuses[0].started} at={.status.initContainerStatuses[0].state.running.startedAt}{"\n"}app                at={.status.containerStatuses[0].state.running.startedAt}{"\n"}'
   ```

2. Submit the post's refresher snippet exactly as the post indents it, then move one line two
   columns left.

   ```sh
   kubectl -n bw-ssf apply --dry-run=client -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: snippet }
   spec:
     initContainers:
       - name: logshipper
         image: busybox:1.36
         restartPolicy: Always # this is what makes it a sidecar container
         command: ['sh', '-c', 'tail -F /opt/logs.txt']
         volumeMounts:
         - name: data
             mountPath: /opt
     containers:
       - name: app
         image: busybox:1.36
         command: ["sh", "-c", "sleep 3600"]
     volumes:
       - name: data
         emptyDir: {}
   EOF
   kubectl -n bw-ssf apply --dry-run=client -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: snippet }
   spec:
     initContainers:
       - name: logshipper
         image: busybox:1.36
         restartPolicy: Always # this is what makes it a sidecar container
         command: ['sh', '-c', 'tail -F /opt/logs.txt']
         volumeMounts:
         - name: data
           mountPath: /opt
     containers:
       - name: app
         image: busybox:1.36
         command: ["sh", "-c", "sleep 3600"]
     volumes:
       - name: data
         emptyDir: {}
   EOF
   ```

3. Reproduce the post's first experiment, and read the two fields it treats as one.

   ```sh
   kubectl -n bw-ssf apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: never-ready }
   spec:
     initContainers:
       - name: side
         image: busybox:1.36
         restartPolicy: Always
         command: ["sh", "-c", "while true; do sleep 5; done"]
         readinessProbe:
           exec: { command: ["false"] }
           periodSeconds: 5
     containers:
       - name: app
         image: busybox:1.36
         command: ["sh", "-c", "sleep 3600"]
   EOF
   sleep 30
   kubectl -n bw-ssf get pod never-ready
   kubectl -n bw-ssf get pod never-ready -o jsonpath='side started={.status.initContainerStatuses[0].started} ready={.status.initContainerStatuses[0].ready}{"\n"}app  at={.status.containerStatuses[0].state.running.startedAt}{"\n"}'
   kubectl -n bw-ssf get pod never-ready -o jsonpath='{range .status.conditions[*]}{.type}={.status}{"\n"}{end}'
   ```

4. The post's second experiment, timed, in the exact probe shape the probe page names as the old
   hazard.

   ```sh
   kubectl -n bw-ssf apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: slow-start }
   spec:
     initContainers:
       - name: side
         image: busybox:1.36
         restartPolicy: Always
         command: ["sh", "-c", "while true; do sleep 5; done"]
         startupProbe:
           exec: { command: ["sh", "-c", "sleep 15"] }
           initialDelaySeconds: 10
           periodSeconds: 30
           failureThreshold: 3
           timeoutSeconds: 20
     containers:
       - name: app
         image: busybox:1.36
         command: ["sh", "-c", "sleep 3600"]
   EOF
   kubectl -n bw-ssf wait --for=condition=Ready pod/slow-start --timeout=180s
   kubectl -n bw-ssf get pod slow-start -o jsonpath='side at={.status.initContainerStatuses[0].state.running.startedAt}{"\n"}app  at={.status.containerStatuses[0].state.running.startedAt}{"\n"}'
   ```

5. The form the post actually recommends, on an image that serves a real endpoint.

   ```sh
   kubectl -n bw-ssf apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: http-start }
   spec:
     initContainers:
       - name: side
         image: registry.k8s.io/e2e-test-images/agnhost:2.53
         restartPolicy: Always
         args: ["netexec", "--http-port=8080"]
         ports:
           - containerPort: 8080
             protocol: TCP
         startupProbe:
           httpGet: { path: /readyz, port: 8080 }
           initialDelaySeconds: 5
           periodSeconds: 30
           failureThreshold: 10
           timeoutSeconds: 20
     containers:
       - name: app
         image: busybox:1.36
         command: ["sh", "-c", "sleep 3600"]
   EOF
   kubectl -n bw-ssf wait --for=condition=Ready pod/http-start --timeout=180s
   kubectl -n bw-ssf get pod http-start -o jsonpath='side at={.status.initContainerStatuses[0].state.running.startedAt}{"\n"}app  at={.status.containerStatuses[0].state.running.startedAt}{"\n"}'
   kubectl -n bw-ssf describe pod http-start | sed -n '/^Events/,$p'
   ```

6. Settle the disagreement between the probe page and the API reference: fail a startup probe and
   see what restarts.

   ```sh
   kubectl -n bw-ssf apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: never-starts }
   spec:
     initContainers:
       - name: side
         image: busybox:1.36
         restartPolicy: Always
         command: ["sh", "-c", "while true; do sleep 5; done"]
         startupProbe:
           exec: { command: ["false"] }
           periodSeconds: 3
           failureThreshold: 2
     containers:
       - name: app
         image: busybox:1.36
         command: ["sh", "-c", "sleep 3600"]
   EOF
   kubectl -n bw-ssf get pod never-starts -o jsonpath='uid={.metadata.uid}{"\n"}'
   sleep 60
   kubectl -n bw-ssf get pod never-starts
   kubectl -n bw-ssf get pod never-starts -o jsonpath='uid={.metadata.uid}{"\n"}side restarts={.status.initContainerStatuses[0].restartCount} started={.status.initContainerStatuses[0].started}{"\n"}app phase={.status.phase} waiting={.status.containerStatuses[0].state.waiting.reason}{"\n"}'
   ```

7. The post's fourth experiment: a sidecar that keeps dying, beside a main container that does not
   notice.

   ```sh
   kubectl -n bw-ssf apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: flapping }
   spec:
     initContainers:
       - name: side
         image: busybox:1.36
         restartPolicy: Always
         command: ["sh", "-c", "while true; do sleep 5; done"]
         livenessProbe:
           exec: { command: ["false"] }
           periodSeconds: 5
           failureThreshold: 1
     containers:
       - name: app
         image: busybox:1.36
         command: ["sh", "-c", "sleep 3600"]
   EOF
   kubectl -n bw-ssf wait --for=condition=Ready pod/flapping --timeout=180s
   kubectl -n bw-ssf get pod flapping -o jsonpath='app at={.status.containerStatuses[0].state.running.startedAt}{"\n"}'
   sleep 90
   kubectl -n bw-ssf get pod flapping
   kubectl -n bw-ssf get pod flapping -o jsonpath='side restarts={.status.initContainerStatuses[0].restartCount}{"\n"}app  restarts={.status.containerStatuses[0].restartCount} at={.status.containerStatuses[0].state.running.startedAt}{"\n"}'
   ```

8. Now the rule as the documentation actually states it: does the *next* container in the list wait?

   ```sh
   kubectl -n bw-ssf apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: two-sides }
   spec:
     initContainers:
       - name: first
         image: busybox:1.36
         restartPolicy: Always
         command: ["sh", "-c", "while true; do sleep 5; done"]
         startupProbe:
           exec: { command: ["sh", "-c", "sleep 15"] }
           periodSeconds: 30
           failureThreshold: 3
           timeoutSeconds: 20
       - name: second
         image: busybox:1.36
         restartPolicy: Always
         command: ["sh", "-c", "while true; do sleep 5; done"]
       - name: plain
         image: busybox:1.36
         command: ["sh", "-c", "sleep 2"]
     containers:
       - name: app
         image: busybox:1.36
         command: ["sh", "-c", "sleep 3600"]
   EOF
   kubectl -n bw-ssf wait --for=condition=Ready pod/two-sides --timeout=180s
   kubectl -n bw-ssf get pod two-sides -o jsonpath='{range .status.initContainerStatuses[*]}{.name} started={.started} running={.state.running.startedAt} done={.state.terminated.finishedAt}{"\n"}{end}'
   kubectl -n bw-ssf get pod two-sides -o jsonpath='app running={.status.containerStatuses[0].state.running.startedAt}{"\n"}'
   ```

9. One Pod that separates the two fields the post treats as one: a sidecar that starts at once and
   is never ready.

   ```sh
   kubectl -n bw-ssf apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: thesis }
   spec:
     initContainers:
       - name: side
         image: busybox:1.36
         restartPolicy: Always
         command: ["sh", "-c", "while true; do sleep 5; done"]
         startupProbe:
           exec: { command: ["true"] }
           periodSeconds: 2
         readinessProbe:
           exec: { command: ["false"] }
           periodSeconds: 5
     containers:
       - name: app
         image: busybox:1.36
         command: ["sh", "-c", "sleep 3600"]
   EOF
   sleep 30
   kubectl -n bw-ssf get pods
   kubectl -n bw-ssf get pod thesis -o jsonpath='side started={.status.initContainerStatuses[0].started} ready={.status.initContainerStatuses[0].ready}{"\n"}app  at={.status.containerStatuses[0].state.running.startedAt}{"\n"}'
   kubectl -n bw-ssf get pod thesis -o jsonpath='{range .status.conditions[*]}{.type}={.status}{"\n"}{end}'
   ```

10. Offline, in a checkout of `kubernetes/website` at the pin, count what the cluster just showed
    you against what the tree says about it.

    ```sh
    cd /path/to/kubernetes/website/content/en
    wc -l docs/concepts/workloads/pods/probes.md
    grep -ci sidecar docs/concepts/workloads/pods/probes.md
    grep -rn 'pod-lifecycle/#types-of-probe' --include='*.md' docs
    grep -rn '{#types-of-probe}' --include='*.md' docs
    grep -n '^## Container probes' docs/concepts/workloads/pods/pod-lifecycle.md
    sed -n '69,75p' docs/concepts/workloads/pods/sidecar-containers.md
    sed -n '60,63p;71,72p;307,309p' docs/concepts/workloads/pods/init-containers.md
    grep -c '^## ' docs/reference/kubernetes-api/core/pod-v1.md
    grep -c 'ContainerStatus' docs/reference/kubernetes-api/core/pod-v1.md
    grep -rln 'restartPolicy: Always' examples | sort
    grep -rl 'startupProbe' examples | wc -l
    grep -rn 'liveness-readiness-startup-probes' ../../static/_redirects.base
    ```

**Expect**

Step 1: `gitVersion` reads v1.35.x, two releases below the pin, and nothing in this exercise is
gated. `kubectl explain pod.status.initContainerStatuses.started` prints a definition: the field
turns true once the container has finished its `postStart` hook and passed its startup probe, and is
always true when no startup probe is defined and the container is running. The cluster's own OpenAPI
carries the definition that the rendered API reference does not — the field is documented exactly
where a reader of kubernetes.io will never look for it. The `restartPolicy` description ends on the
rule `sidecar-containers.md:71-75` states: the *next* init container starts once this one is
started, or once its startup probe has succeeded. Read both sentences for what they do not say.
Neither names `.spec.containers`. The `bare` Pod goes Ready in a few seconds and the two `startedAt`
stamps are one second apart or identical: with no startup probe the sidecar is `started` the moment
it runs, so the post's "almost in parallel" is a measurement, not a figure of speech.

Step 2: the first apply fails before the API server is reached. `kubectl` stops at `error converting
YAML to JSON: yaml: line 12: mapping values are not allowed in this context`, naming the line
`mountPath` sits on. The snippet at the post's `:18-27` is not valid YAML: the block sequence under
`volumeMounts` opens its entry at the same column as the key, and `mountPath` then sits two columns
right of `name`, where the parser is expecting either the end of the entry or a sibling key. The
second apply, with `mountPath` moved two columns left, prints `pod/snippet created (dry run)`. Four
manifests in this post are meant to be run and all four parse. The one that does not is the
refresher — the snippet a reader who has never seen a sidecar copies first.

Step 3: `get pod` shows `never-ready` as `0/1` and `Running`, and it will stay that way. The
jsonpath prints `side started=true ready=false` and an `app at=` stamp a second or two later: the
main container started, and it started while the sidecar's readiness probe was already failing. The
conditions list carries `Initialized=True`, `Ready=False`, `ContainersReady=False`. This is the
post's first experiment reproduced, and it separates two consequences that a reader who knows
ordinary containers will run together. A sidecar's readiness governs the Pod's `Ready` condition,
and through it the Service endpoints. It governs nothing at all about whether the containers beside
it are allowed to start.

Step 4: the wait returns, and the two stamps are about twenty-five seconds apart. That number is
`initialDelaySeconds` plus the fifteen seconds the probe body itself takes, and it is emphatically
not the thirty-second `periodSeconds`: the first probe fires at ten seconds, exactly as
`probes.md:248` promises for current releases, and succeeds on that first attempt. Had the older
behaviour the same paragraph describes applied — the delay ignored when the period exceeds it — the
main container would have waited about forty-five seconds instead. So the field the page hedges
about is honoured here, and the cost of the hedge is paid in full by a container that has nothing to
do with the probe.

Step 5: the gap collapses to about five seconds. The agnhost sidecar serves `/readyz` from the
moment it binds, so the probe succeeds on its first attempt and the whole delay is the
`initialDelaySeconds` you chose. This is the shape the post recommends, and the measurement is the
argument for it: a startup probe against a real endpoint costs the main container only the delay you
configure, where the exec probe of step 4 costs the delay plus however long the probe body runs. The
event list shows `Started container side` and `Started container app`, in that order, with no
`Unhealthy` event between them.

Step 6: the Pod never becomes Ready. After sixty seconds the jsonpath prints `side started=false`, a
`restarts` count of three or four, and — the line to read twice — `app phase=Pending
waiting=PodInitializing`. The main container has not started at all. The Pod's UID is byte-identical
to the one printed before the sleep, which settles the disagreement between the two pages:
`probes.md:39` says a failed startup probe makes the kubelet kill the *container*, while
`pod-v1.md:774` writes *Pod* twice — the Pod has initialized, the Pod will be restarted — in the
description of a field that can only be set on a container. The container is restarted; the Pod
object is untouched. And note what the post's summary table has no row for. Every cell in it
describes a sidecar probe's effect on a running main container. Here the main container is not
running, and the sidecar's startup probe is why.

Step 7: `side restarts=` has climbed to four or five while `app restarts=0`, and the `app at=` stamp
is the same one you printed ninety seconds earlier. The main container has not been restarted, has
not been stopped, and has been serving throughout. `get pod` may show the Pod as Ready or not
depending on where in the kill-and-restart cycle you catch it, since the sidecar carries no
readiness probe and its `ready` follows its running state. This is the post's fourth experiment, and
it is the one whose answer is least surprising once the other three have landed: liveness on a
sidecar restarts the sidecar. The blast radius is one container.

Step 8: the three-row output is the documented rule, timed. `first` shows a `running=` stamp near
zero and no `done=` stamp, because a sidecar never terminates on its own. `second` shows a
`running=` stamp about fifteen seconds later — it waited for `first` to be `started`, not for it to
finish, which it never will. `plain` carries a `done=` stamp about two seconds after that, so the
ordinary init container ran to completion in the sequence as it always has. And `app running=` lands
after all three. Every hop in that chain is stated on a pinned page. The hop from the last init
container to `app` is the one no page states, and it is the hop the post is about.

Step 9: `side started=true ready=false`, an `app at=` stamp from thirty seconds ago, and
`Ready=False` in the conditions. The two fields the post treats as one thing have come apart on
purpose. `started` released the main container and will never be revoked; `ready` never turned true
and never will. If you keep one sentence from this exercise, keep this one: the gate that starts
your application is `started`, and the field your instinct reaches for — readiness, the one every
tutorial teaches first — controls whether traffic arrives, not whether anything runs.

Step 10: `probes.md` is 488 lines long and the word sidecar appears in it zero times. Four links
point at `pod-lifecycle/#types-of-probe`; that anchor is defined at `probes.md:21` and nowhere else,
and `pod-lifecycle.md:783` now reads `## Container probes`, so all four land on a page that no
longer has the id they name — and all four sit on `sidecar-containers.md` and `init-containers.md`,
the two pages this post sends its reader to. `sidecar-containers.md:69-75` prints the `started`
rule, stated once more for the next init container. `init-containers.md:60-63` and `:71-72` deny the
post's premise outright with no sidecar carve-out, though `:54-58` two paragraphs above concedes
that sidecars never complete; `:307-309` asserts that validation prohibits `readinessProbe` on init
containers, which step 3 quietly submitted and the API server accepted. The 2023 exercise on native
sidecar containers owns that last contradiction and settles it. `pod-v1.md` carries 103 type
sections and names `ContainerStatus` three times without defining it once. Of the nine example files
matching `restartPolicy: Always`, seven define sidecars and two set the field on the Pod; and `grep
-rl 'startupProbe' examples` prints 0. The lever this post lands on appears in no example in the
tree. Finally, the redirect at `_redirects.base:88` is the reason the post's three probe links still
resolve five years after the page they name was moved.

**Read on**

11. [What a sidecar costs in CPU and memory, in what order it is shut down, and whether a Pod may be
    Ready while one is not](../2023/09-native-sidecar-containers.md) — the three questions this
    exercise handed off, all of them settled against the post that announced the feature.

12. [The composite-container patterns this field was eventually named
    after](../2015/05-the-distributed-system-toolkit-patterns.md), argued eight years before there
    was a field to argue about.

13. [The lifecycle hook that has to finish before `started` can turn
    true](04-kubernetes-v1-33-updates-to-container-lifecycle.md), and what happens to it when it
    does not.

14. [A probe mechanism this exercise never used](../2022/02-grpc-probes-now-in-beta.md) — the same
    three probe types checked over a different wire, announced under a gate that was deleted five
    releases later.

15. *Unanswerable from the pin.* No page in the pinned tree states which containers the `started`
    status releases. Whether that is an omission nobody noticed or a deliberate refusal to commit
    the ordering in writing is not something the tree records, and the SIG Node discussion that
    would settle it is not in this checkout.

**Teardown**

One namespace holds every object this exercise created, and no step changed anything on the node.

```sh
kubectl delete namespace bw-ssf
```

The checkout of `kubernetes/website` was only ever read, so nothing there needs undoing either. If
you want the timings again on a quiet cluster, step 4 and step 8 are the two that are worth
repeating — both measure a delay, and both are sensitive to how busy the kubelet is when the probe
fires.
