<a id="kubernetes-v1-33-updates-to-container-lifecycle"></a>

# The half of this post that finished its ladder is documented nowhere in the pinned tree, not one page and not one example, the half still alpha five releases on has a section and a marker and an example, and the page that carries both counts its hooks to two and then lists three

**Post** — [Kubernetes v1.33: Updates to Container Lifecycle](https://kubernetes.io/blog/2025/05/14/kubernetes-v1-33-updates-to-container-lifecycle/),
2025-05-14.

6,268 bytes across 77 lines, 21 of them blank; 918 words of body; one author, Sreeram Venkitesh of
DigitalOcean. Three `##` headings, three `###` headings, one code fence, and not one Hugo shortcode,
so the alpha status of its headline feature is stated only in prose. Five external links: one into
`kubernetes/kubernetes` at a pinned commit, for a line range of `types.go` that holds the list of
valid signals, and four to SIG Node contact points. The SIG Node link spells the organisation
`Kubernetes` with a capital letter.

**As written**

The post carries two unrelated features under one title. The first, at `:15-25`, is the zero value
for the `Sleep` action in container lifecycle hooks. The `Sleep` action arrived in v1.29 so that a
hook could pause without the container image needing a `sleep` binary, which the post notes is
awkward with third-party images; it did not at first accept a duration of zero, even though the
`time.Sleep` underneath it does. That was fixed in v1.32 behind `PodLifecycleSleepActionAllowZero`,
and the post announces that gate reaching beta and default-on in v1.33.

The second, at `:27-64`, is `ContainerStopSignals`, new and alpha in v1.33. Until then the only way
to change the signal a container is stopped with was to rebuild the image with a different
`STOPSIGNAL` instruction. The gate adds `lifecycle.stopSignal` to the container spec. The post
describes it at `:35` as a new lifecycle added "along with the existing PreStop and PostStart
lifecycle handlers", requires `spec.os.name` to be set so that the signal can be cross-validated
against the operating system, and says that Windows Pods may use only `SIGTERM` and `SIGKILL`. The
fallback chain at `:39` is lifecycle, then image, then runtime default, which it names as `SIGTERM`
for both containerd and CRI-O.

Two of its own sentences are worth carrying forward. At `:43`, under **Version skew**, it says the
container runtime must also support the feature and that "the container runtime implementations for
containerd and CRI-O are still a work in progress and will be rolled out soon". At `:47` it says the
gate must be turned on in both the kube-apiserver and the kubelet. The YAML at `:49-62` sets
`spec.os.name: linux` and `lifecycle.stopSignal: SIGUSR1` on an `nginx:latest` container.

**As it runs now**

**The two halves ended in opposite places, and the census row for this post is about that.**
`PodLifecycleSleepActionAllowZero` was alpha in 1.32, beta in 1.33, and stable and locked from 1.34
(`PodLifecycleSleepActionAllowZero.md:9-20`); the older `PodLifecycleSleepAction` took the same last
step in the same release (`PodLifecycleSleepAction.md:9-20`). `ContainerStopSignals.md:8-11` has one
stage, `alpha`, `defaultValue: false`, `fromVersion: "1.33"`, and no `toVersion`. Counted at the pin
that is five releases alpha, 1.33 through 1.37, and four releases since the post.

**Twenty gates entered alpha in 1.33 and two of them are still alpha.** Reading every `stages:`
block under `feature-gates/` at the pin gives 487 gates with a ladder, of which 52 end in an open
alpha stage. Twenty of the 487 begin alpha at 1.33. Eighteen have moved since. The two that have not
are `ContainerStopSignals` and `ReduceDefaultCrashLoopBackOffDecay`. One of the eighteen is
`KubeletEnsureSecretPulledImages`, alpha 1.33 to 1.34 and beta from 1.35, which is the subject of
[the exercise on image pull credential verification](03-ensure-secret-pulled-images.md); it and the
stop signal gate shipped in the same release and are three releases apart now.

**The half that finished is documented nowhere.** `PodLifecycleSleepActionAllowZero` appears on
exactly one line under `docs/` at the pin, and that line is the `title:` of its own gate definition,
which carries `_build: list: never` and `render: false` and is therefore never rendered as a page.
Three files in the whole English tree name it: that gate definition, this post, and the v1.32
release announcement. Neither the concept page nor the task page nor the API reference says anywhere
that a sleep duration of zero is allowed; `pod-v1.md:2882-2883` marks `SleepAction.seconds` required
and describes it as "Seconds is the number of seconds to sleep", with no range and no note. A reader
who starts from the documentation has no way to learn that the thing the post announced exists.

**There is not one YAML example of the `sleep` handler in the whole tree.** `grep -rn 'sleep:'`
across `docs/` and `examples/` returns nothing. Four files under `examples/` set `lifecycle:`, and
all four use `exec`. One of them, `examples/service/pod-with-graceful-termination.yaml:23-32`, is a
`preStop` hook whose command is `["/bin/sh", "-c", "sleep 180"]`: precisely the pattern this post
says at `:17` the `Sleep` action was added to replace, still shipped as documentation one release
after that action went stable and locked. `examples/pods/lifecycle-events.yaml:15` does the same
thing in a loop.

**The half that did not move has a section, a marker and an example.** `pod-lifecycle.md:867-897`
carries two headings for it, `### Stop Signals` at `:867` with the anchor
`#pod-termination-stop-signals` and `### Defining custom stop signals` at `:873`, a `feature-state`
shortcode naming `ContainerStopSignals` at `:875`, the `spec.os.name` requirement at `:878-879`, the
Windows restriction at `:881`, and a YAML example at `:885-894` that is the post's example with the
object header dropped and the image and container name changed. The alpha feature is better
documented than the stable one.

**One page counts its hooks to two and then lists three.** `container-lifecycle-hooks.md:26` says
"There are two hooks that are exposed to Containers:", and then lists `PostStart` at `:28`,
`PreStop` at `:42` and `StopSignal` at `:55`. The API agrees with the sentence and not with the
list: `pod-v1.md:1725-1747` gives `Lifecycle` three fields, of which `postStart` and `preStop` are
of type `LifecycleHandler` and `stopSignal` is a plain `string`. The type description at `:1727`
still speaks only of "the PostStart and PreStop lifecycle handlers".

**The same page marks nothing alpha.** `container-lifecycle-hooks.md` contains no `feature-state`
shortcode at all, so `StopSignal` is presented at `:55-61` with no gate, no version and no caveat,
four lines after two hooks that need none. `pod-lifecycle.md:875` marks the same field alpha. Two
concept pages, one field, one of them silent about the gate; step 3 settles which page a reader
should believe.

**And it describes the `Sleep` handler as something the container does.**
`container-lifecycle-hooks.md:71` reads "Sleep - Pauses the container for a specified duration.",
with a trailing space. Seven lines later, `:77-78` says `httpGet`, `tcpSocket` and `sleep` "are
executed by the kubelet process, and `exec` is executed in the container". The container is not
paused by anything; the kubelet waits. Step 9 measures which of the two sentences the cluster
behaves like.

**The task page and the concept page disagree about what a `postStart` hook blocks.**
`attach-handler-lifecycle-event.md:71-72` states flatly that "The Container's status is not set to
RUNNING until the postStart handler completes". `container-lifecycle-hooks.md:31-32` says the hook
"runs **concurrently** with the container's `ENTRYPOINT`", and the note at `:36-40` softens the
consequence to "it can delay container status updates; the container may not transition to `Running`
until the hook completes". The stable `sleep` handler makes this measurable to the second, which is
step 9.

**The only task page on lifecycle hooks knows about neither feature.**
`attach-handler-lifecycle-event.md:8-11` says "Kubernetes supports the postStart and preStop events"
and "A Container may specify one handler per event". It names no `sleep` action and no stop signal,
and the file it renders, `examples/pods/lifecycle-events.yaml`, is the `exec` example above. Outside
the generated component flag tables and the gate definition itself, three files under `docs/`
mention the stop signal at all: `pod-lifecycle.md`, `container-lifecycle-hooks.md` and the generated
`pod-v1.md`.

**The generated reference carries the signal list the post linked to source for.** `pod-v1.md:1744`
describes `stopSignal` and then enumerates 65 possible values, all distinct as strings. They include
`SIGKILL` and `SIGSTOP`, which a process cannot catch or handle, and three pairs that are aliases on
Linux: `SIGCLD` with `SIGCHLD`, `SIGIOT` with `SIGABRT`, and `SIGPOLL` with `SIGIO`. The same line
records the constraint as "StopSignal can only be set for Pods with a non-empty .spec.os.name".
Steps 6 and 7 push on both halves of that list.

**`spec.os.name` is advisory everywhere except here.** `pods/_index.md:125-144` marks Pod OS stable
since v1.25 and says at `:129` that you "should" set it, then spends the rest of the section
explaining that it does not affect scheduling. `windows/user-guide.md:165-184` says the same thing
twice more, and its note at `:171-173` tells readers older than 1.24 to enable `IdentifyPodOS` "to
be able to set a value for `.spec.pod.os`", which is not the path of that field. `pod-v1.md:148`
makes `os` optional on the Pod spec while `:2160-2170` makes `name` required inside `PodOS`. Step 6
is the one place a missing `spec.os` should stop a Pod from being created at all.

**One of the two lifecycle pages hard-codes a release into its API link, and it has rotted.**
`container-lifecycle-hooks.md:77` links `tcpSocket` to
`/docs/reference/generated/kubernetes-api/v1.35/#lifecyclehandler-v1-core`. Counting every
`generated/kubernetes-api/v1.NN` reference in the English tree gives 56 of them across eight
versions, and that `v1.35` is the only one at 1.35; 31 sit at 1.36 and the rest at 1.13, 1.16, 1.18,
1.19, 1.25 and 1.28. `attach-handler-lifecycle-event.md:97-99` writes the same kind of link three
times as `{{< param "version" >}}`, which does not rot.

**The release notes narrowed the sleep feature to `preStop` and then widened it back.** The v1.32
announcement heads its entry "Allow zero value for sleep action of PreStop hook"
(`kubernetes-v1-32-release/index.md:243-248`). The v1.33 announcement heads its entry "Zero-second
sleeps for container PreStop hooks" and describes the action twice as belonging to the `preStop`
hook (`kubernetes-v1-33-release/index.md:419-433`), citing KEP-3960 and KEP-4818, both of whose
titles say "PreStop Hook". This post says at `:17` that the action is for "PreStop and PostStart"
hooks. The v1.34 announcement agrees with the post (`kubernetes-v1-34-release/index.md:188-194`). A
`postStart` hook in step 9 settles it.

**Nothing published since says whether the runtimes caught up.** The v1.33 announcement describes
the stop signal feature at `:469-481` and cites KEP-4960. `ContainerStopSignals`, `stopSignal` and
`StopSignal` appear in no release announcement after it; the v1.34, v1.35, v1.36 and v1.37 posts are
all present at the pin and all silent. The post's own sentence at `:43` about containerd and CRI-O
being "a work in progress" is the last thing the pinned tree says on the subject, and no
documentation page repeats it. Step 5 is the only way to find out.

**What this exercise does not cover, and where it lives**

What a long `preStop` does to the endpoint list belongs to [the fifteen-cell EndpointSlice
conditions table](../../labs/07/04-eleven-kilobytes-of-endpointslice.md) and to [the readiness probe
followed to an endpoint list](../../labs/01/15-endpointslice-drains.md); this exercise never puts
the test Pod behind a Service. Termination ordering between a sidecar and the container it serves is
[the native sidecar containers exercise](../2023/09-native-sidecar-containers.md). What the cluster
looks like while the apiserver's static pod restarts is [the manifest-directory chaos
drill](../../labs/01/04-static-pod-blip.md); step 4 here waits for the apiserver and moves on.
Getting a feature gate from a kubelet configuration file into a running kubelet is worked in detail
by [the image pull credential verification exercise](03-ensure-secret-pulled-images.md); step 5
reuses its backup-and-restore shape without re-explaining it.

**The diff, and why**

***Never absorbed*** is the whole of the first half. The zero-second sleep shipped, graduated twice,
and locked, and none of it reached the documentation: no page names the gate, no page says zero is
allowed, no example uses the handler, and the one example that most needs it still shells out to
`sleep 180`. This is the rarer shape of never-absorbed, because the feature is not obscure and not
contested; it simply finished its ladder in a release whose notes were the last thing written about
it.

***Overtaken by stasis*** is the second half. Everything the post says about `ContainerStopSignals`
is still true, including the sentence at `:43` warning that the runtimes had not caught up. Five
releases later the gate has the same stage, the same default and no end version, and no page or
announcement has updated the runtime-support question either way. The post has not aged; it has been
left where it was put.

***Still right*** covers the mechanics. The fallback chain at `:39`, the `spec.os.name` requirement,
the Windows restriction to `SIGTERM` and `SIGKILL`, and the instruction at `:47` to enable the gate
in both the kube-apiserver and the kubelet all survive into `pod-lifecycle.md:867-897` and
`pod-v1.md:1744` unchanged. The post's YAML and the documentation's differ in an image name, a
container name and a four-line object header.

***Wrong when it was published*** applies to one sentence. At `:35` the post says stop signals were
"added to the API as a new lifecycle along with the existing PreStop and PostStart lifecycle
handlers". `stopSignal` is a string field on `Lifecycle`, not a handler and not a hook; it has no
`LifecycleHandler`, no action and no execution. `container-lifecycle-hooks.md` repeated the framing,
which is why that page now counts to two and lists three.

**The ladder**

Two gates, opposite directions, one post. `PodLifecycleSleepActionAllowZero` has three rungs and a
lock: alpha off at 1.32, beta on at 1.33, stable and locked at 1.34. Its parent
`PodLifecycleSleepAction` has the same three rungs and the same lock, three releases earlier at the
first two and the same release at the last: alpha at 1.29, beta at 1.30, stable and locked at 1.34.
Locked is what makes the first half of the post have nothing left to turn on, on any cluster at 1.34
or later.

`ContainerStopSignals` has one rung and an open right-hand column: alpha, off, from 1.33, no
`toVersion`. That is not an omission in the gate file; it is the file saying the feature has not
moved. The lab cluster at v1.35 is two releases past the post and two behind the pin: the two sleep
gates are locked stable there and need nothing, and the stop signal gate is alpha and off, so
everything the post describes about stop signals has to be switched on by hand in two places before
any of it can be observed. The runtime is a third column the ladder does not have, and step 5 is
where it either appears or does not.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180`, running Kubernetes
v1.35. Provision it with [the Ansible baseline](../../strands/lab-topologies.md#provision) and [the
node baseline steps](../../strands/lab-topologies.md#node-baseline-steps) if it is not already up.
The exercise edits the kube-apiserver static pod manifest and the kubelet configuration file on that
node, so a single-node cluster you can break and restore is the right shape; it needs no worker and
no second control plane.

**Do**

1. Establish what the cluster serves and what it has switched on. `kubectl explain` reads the
   OpenAPI the apiserver publishes, not the feature gates it honours, so the two answers are allowed
   to differ and the point of this step is to see by how much.

   ```sh
   kubectl version
   kubectl explain pod.spec.containers.lifecycle
   kubectl explain pod.spec.containers.lifecycle.stopSignal | head -20
   kubectl explain pod.spec.containers.lifecycle.sleep
   ssh zain@10.10.10.180 "sudo grep -n 'feature-gates' /etc/kubernetes/manifests/kube-apiserver.yaml || echo 'no --feature-gates on the apiserver'"
   ssh zain@10.10.10.180 "sudo grep -n -A6 '^featureGates' /var/lib/kubelet/config.yaml || echo 'no featureGates block in the kubelet config'"
   ```

   Write down whether the kubelet configuration already has a `featureGates` block. Step 5 appends
   one; if there is already a block, add the single line under it instead of appending a second
   mapping key, which would make the file invalid YAML and the kubelet would not start.

2. Find out what a container is stopped with today. The image sets no `STOPSIGNAL`, so this is the
   runtime default, which `pod-lifecycle.md:870-871` and the post's `:39` both name as `SIGTERM`.

   ```sh
   kubectl create namespace bw-css
   cat <<'EOF' | kubectl apply -f -
   apiVersion: v1
   kind: Pod
   metadata:
     name: sig-base
     namespace: bw-css
   spec:
     terminationGracePeriodSeconds: 30
     containers:
     - name: c
       image: busybox:1.36
       command: ["sh", "-c", "trap 'echo CAUGHT-TERM; exit 0' TERM; trap 'echo CAUGHT-USR1; exit 0' USR1; echo ready; while true; do sleep 1; done"]
   EOF
   kubectl -n bw-css wait --for=condition=Ready pod/sig-base --timeout=90s
   kubectl -n bw-css delete pod sig-base --grace-period=30 --wait=false
   sleep 4
   kubectl -n bw-css logs sig-base
   kubectl -n bw-css delete pod sig-base --ignore-not-found --wait=true
   ```

3. With both gates still off, ask for a custom stop signal. The question is not whether it works; it
   is whether the apiserver refuses the field or accepts the object and silently drops it, which is
   the difference between a reader finding out immediately and finding out never.

   ```sh
   cat <<'EOF' | kubectl apply -f -
   apiVersion: v1
   kind: Pod
   metadata:
     name: sig-usr1
     namespace: bw-css
   spec:
     terminationGracePeriodSeconds: 30
     os:
       name: linux
     containers:
     - name: c
       image: busybox:1.36
       command: ["sh", "-c", "trap 'echo CAUGHT-TERM; exit 0' TERM; trap 'echo CAUGHT-USR1; exit 0' USR1; echo ready; while true; do sleep 1; done"]
       lifecycle:
         stopSignal: SIGUSR1
   EOF
   kubectl -n bw-css get pod sig-usr1 -o jsonpath='os={.spec.os}{"\n"}lifecycle={.spec.containers[0].lifecycle}{"\n"}'
   kubectl -n bw-css delete pod sig-usr1 --ignore-not-found --wait=true
   ```

4. Turn the gate on in the kube-apiserver only, and repeat. The post at `:47` says both components
   need it; this step measures what the first one alone buys you.

   ```sh
   ssh zain@10.10.10.180 "sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/bw-apiserver.yaml.bak && sudo sed -i '/- kube-apiserver$/a\    - --feature-gates=ContainerStopSignals=true' /etc/kubernetes/manifests/kube-apiserver.yaml"
   until kubectl get --raw /readyz >/dev/null 2>&1; do sleep 3; done
   kubectl get --raw /readyz; echo
   cat <<'EOF' | kubectl apply -f -
   apiVersion: v1
   kind: Pod
   metadata:
     name: sig-usr1
     namespace: bw-css
   spec:
     terminationGracePeriodSeconds: 30
     os:
       name: linux
     containers:
     - name: c
       image: busybox:1.36
       command: ["sh", "-c", "trap 'echo CAUGHT-TERM; exit 0' TERM; trap 'echo CAUGHT-USR1; exit 0' USR1; echo ready; while true; do sleep 1; done"]
       lifecycle:
         stopSignal: SIGUSR1
   EOF
   kubectl -n bw-css get pod sig-usr1 -o jsonpath='lifecycle={.spec.containers[0].lifecycle}{"\n"}'
   kubectl -n bw-css wait --for=condition=Ready pod/sig-usr1 --timeout=90s
   kubectl -n bw-css delete pod sig-usr1 --grace-period=30 --wait=false
   sleep 4
   kubectl -n bw-css logs sig-usr1
   kubectl -n bw-css delete pod sig-usr1 --ignore-not-found --wait=true
   ```

5. Turn the gate on in the kubelet as well, and repeat once more. This is the headline measurement
   of the exercise, and its answer is not in the pinned tree: the API half can be complete and the
   container still receive `SIGTERM`, because the runtime is a third participant the post says at
   `:43` was not ready.

   ```sh
   ssh zain@10.10.10.180 "sudo cp /var/lib/kubelet/config.yaml /tmp/bw-kubelet.yaml.bak && printf 'featureGates:\n  ContainerStopSignals: true\n' | sudo tee -a /var/lib/kubelet/config.yaml >/dev/null && sudo systemctl restart kubelet"
   until kubectl get nodes 2>/dev/null | grep -q ' Ready '; do sleep 3; done
   ssh zain@10.10.10.180 "sudo systemctl is-active kubelet; sudo tail -5 /var/lib/kubelet/config.yaml"
   cat <<'EOF' | kubectl apply -f -
   apiVersion: v1
   kind: Pod
   metadata:
     name: sig-usr1
     namespace: bw-css
   spec:
     terminationGracePeriodSeconds: 30
     os:
       name: linux
     containers:
     - name: c
       image: busybox:1.36
       command: ["sh", "-c", "trap 'echo CAUGHT-TERM; exit 0' TERM; trap 'echo CAUGHT-USR1; exit 0' USR1; echo ready; while true; do sleep 1; done"]
       lifecycle:
         stopSignal: SIGUSR1
   EOF
   kubectl -n bw-css wait --for=condition=Ready pod/sig-usr1 --timeout=90s
   kubectl -n bw-css delete pod sig-usr1 --grace-period=30 --wait=false
   sleep 4
   kubectl -n bw-css logs sig-usr1
   ```

6. Push on validation. Three Pods that should not be created: a stop signal with no `spec.os` at
   all, a signal name that is not in the enum, and a Linux-only signal on a Pod declared as Windows.
   Each `apply` is expected to fail; keep the message.

   ```sh
   for case in nos bogus windows; do
     case $case in
       nos)     OSBLOCK=""                                    ; SIG=SIGUSR1 ;;
       bogus)   OSBLOCK=$'  os:\n    name: linux'             ; SIG=SIGFOO  ;;
       windows) OSBLOCK=$'  os:\n    name: windows'           ; SIG=SIGUSR1 ;;
     esac
     echo "--- case $case"
     printf 'apiVersion: v1\nkind: Pod\nmetadata:\n  name: bad-%s\n  namespace: bw-css\nspec:\n%s\n  containers:\n  - name: c\n    image: busybox:1.36\n    lifecycle:\n      stopSignal: %s\n' "$case" "$OSBLOCK" "$SIG" | kubectl apply -f - 2>&1 | head -5
   done
   ```

7. Now the signals the enum lists but a process cannot act on. `pod-v1.md:1744` accepts `SIGKILL`
   and `SIGSTOP` as values, and it also accepts `SIGCLD`, which is the same signal number as
   `SIGCHLD`. Find out which of the three the apiserver stores and what the container sees.

   ```sh
   for s in SIGKILL SIGSTOP SIGCLD; do
     echo "--- $s"
     cat <<EOF | kubectl apply -f - 2>&1 | head -3
   apiVersion: v1
   kind: Pod
   metadata:
     name: sig-$(echo $s | tr 'A-Z' 'a-z')
     namespace: bw-css
   spec:
     terminationGracePeriodSeconds: 20
     os:
       name: linux
     containers:
     - name: c
       image: busybox:1.36
       command: ["sh", "-c", "trap 'echo CAUGHT-TERM; exit 0' TERM; trap 'echo CAUGHT-CHLD' CHLD; echo ready; while true; do sleep 1; done"]
       lifecycle:
         stopSignal: $s
   EOF
   done
   kubectl -n bw-css get pods -o custom-columns=NAME:.metadata.name,SIGNAL:.spec.containers[0].lifecycle.stopSignal
   for s in sigkill sigstop sigcld; do
     kubectl -n bw-css get pod sig-$s >/dev/null 2>&1 || continue
     kubectl -n bw-css wait --for=condition=Ready pod/sig-$s --timeout=90s
     START=$(date +%s)
     kubectl -n bw-css delete pod sig-$s --grace-period=20 --wait=true
     echo "$s took $(( $(date +%s) - START ))s"
   done
   ```

8. Ask the node what it thinks the stop signal is. The kubelet passes the field to the runtime over
   CRI; whether the runtime records it anywhere a human can read is a separate question, and no page
   in the pinned tree answers it.

   ```sh
   kubectl -n bw-css apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: sig-usr1
     namespace: bw-css
   spec:
     terminationGracePeriodSeconds: 30
     os:
       name: linux
     containers:
     - name: c
       image: busybox:1.36
       command: ["sh", "-c", "trap 'echo CAUGHT-TERM; exit 0' TERM; trap 'echo CAUGHT-USR1; exit 0' USR1; echo ready; while true; do sleep 1; done"]
       lifecycle:
         stopSignal: SIGUSR1
   EOF
   kubectl -n bw-css wait --for=condition=Ready pod/sig-usr1 --timeout=90s
   ssh zain@10.10.10.180 "sudo crictl version"
   ssh zain@10.10.10.180 "ID=\$(sudo crictl ps -q --name c | head -1); echo id=\$ID; sudo crictl inspect \$ID | grep -i -n 'signal' || echo 'no signal string in the container inspect output'"
   kubectl -n bw-css delete pod sig-usr1 --grace-period=30 --wait=false
   sleep 6
   ssh zain@10.10.10.180 "sudo journalctl -u kubelet --since '-2 min' --no-pager | grep -i -E 'signal|stopping|killing' | tail -20"
   kubectl -n bw-css delete pod sig-usr1 --ignore-not-found --wait=true
   ```

9. The other half of the post. No gate is involved: the `sleep` handler and its zero value have been
   stable and locked since 1.34. Settle three sentences with it. Whether the action works on
   `postStart` as well as `preStop`, which the v1.32 and v1.33 release notes imply it does not;
   whether a `postStart` hook holds the container out of `Running`, which the task page asserts and
   the concept page hedges; and whether zero and negative durations are accepted.

   ```sh
   cat <<'EOF' | kubectl apply -f -
   apiVersion: v1
   kind: Pod
   metadata:
     name: sleep-ps
     namespace: bw-css
   spec:
     containers:
     - name: c
       image: busybox:1.36
       command: ["sh", "-c", "echo entrypoint-started; while true; do sleep 1; done"]
       lifecycle:
         postStart:
           sleep:
             seconds: 30
   EOF
   START=$(date +%s)
   until [ -n "$(kubectl -n bw-css get pod sleep-ps -o jsonpath='{.status.containerStatuses[0].state.running.startedAt}' 2>/dev/null)" ]; do sleep 1; done
   echo "container reported running after $(( $(date +%s) - START ))s"
   kubectl -n bw-css logs sleep-ps
   kubectl -n bw-css get pod sleep-ps -o jsonpath='phase={.status.phase} ready={.status.containerStatuses[0].ready}{"\n"}'
   for secs in 0 -1; do
     echo "--- seconds: $secs"
     printf 'apiVersion: v1\nkind: Pod\nmetadata:\n  name: sleep-z%s\n  namespace: bw-css\nspec:\n  containers:\n  - name: c\n    image: busybox:1.36\n    lifecycle:\n      preStop:\n        sleep:\n          seconds: %s\n      postStart:\n        sleep:\n          seconds: %s\n' "$(echo $secs | tr -d -- -)" "$secs" "$secs" | kubectl apply -f - 2>&1 | head -4
   done
   ```

10. Count the documentation offline, in the pinned checkout, so the claims above are numbers and not
    impressions.

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -rn 'PodLifecycleSleepActionAllowZero' docs/ | wc -l
    grep -rln 'PodLifecycleSleepActionAllowZero' .
    grep -rn 'sleep:' docs/ examples/ | wc -l
    grep -rl 'lifecycle:' examples/
    grep -rl -i 'stopsignal' docs/ --include='*.md' | grep -v command-line-tools-reference
    grep -c 'feature-state' docs/concepts/containers/container-lifecycle-hooks.md
    sed -n '1744p' docs/reference/kubernetes-api/core/pod-v1.md | grep -o '`"SIG[^"]*"`' | sort -u | wc -l
    grep -rno --include='*.md' 'generated/kubernetes-api/v1\.[0-9]*' . | sed 's/.*\(v1\.[0-9]*\)/\1/' | sort | uniq -c
    ```

**Expect**

Step 1 should report a v1.35 server and a `lifecycle` explain block that lists three fields:
`postStart`, `preStop` and `stopSignal`. That is the first thing worth noticing, because the gate is
off and the field is described anyway; `kubectl explain` renders the published schema, and an alpha
field is in the schema whether or not the apiserver will honour it. Expect neither grep against the
node to find `ContainerStopSignals`. If the kubelet configuration already carries a `featureGates`
block, record its contents now and adjust step 5 accordingly.

Step 2 should print `CAUGHT-TERM`. If it prints nothing, the pod finished terminating before the
`logs` call; raise the sleep after `delete` or watch with `kubectl logs -f` in a second shell while
deleting in the first. If it prints `CAUGHT-USR1` with no stop signal configured, something other
than this feature is sending `SIGUSR1` and the rest of the exercise will not be readable — stop and
find out what.

Step 3 is the interesting negative. The likeliest outcome is that the Pod is created and the
jsonpath prints `os=map[name:linux]` with `lifecycle=` empty, because the apiserver prunes a field
whose gate is off rather than rejecting the object. If that is what happens, note that nothing in
the output told you the field was discarded: no warning, no event, no status. The alternative is a
validation error naming the feature gate, which would be the better behaviour and is worth recording
precisely if you see it.

Step 4 should show the apiserver coming back within a minute or two and `lifecycle` now surviving
the round trip as `map[stopSignal:SIGUSR1]`. The container should still report `CAUGHT-TERM` when it
is deleted, because the kubelet has not been told about the gate. If it reports `CAUGHT-USR1` at
this point, then the kubelet does not gate the field at all and the post's instruction at `:47` to
enable it in both components is stricter than the code — say so, and note that no documentation page
repeats that instruction either way.

Step 5 has three outcomes and all three are worth writing down. `CAUGHT-USR1` means the whole chain
works at v1.35 and the post's warning at `:43` about containerd has been overtaken by a release
nobody announced. `CAUGHT-TERM` means the chain stops somewhere, and step 8 is where you find out
whether the kubelet passed the signal on. A container that never logs a catch line and is killed at
the end of the grace period means the signal arrived but was one the shell could not trap, which
should not happen with `SIGUSR1` and would point at the trap rather than at Kubernetes. Record the
containerd version from step 8 alongside whichever answer you get, because the answer is a property
of that version and not of Kubernetes alone.

Step 6 should fail three times. The `nos` case should be rejected by validation for a missing
`spec.os.name`, which is the one place in the tree where that field stops being advisory. The
`bogus` case should be rejected as not a valid value, and the message is worth keeping: it is the
closest thing the cluster will give you to the 65-value enum that `pod-v1.md:1744` prints. The
`windows` case should be rejected for the operating system, not for the signal name. If any of the
three is accepted instead, the cross-validation the post describes at `:35` is not doing what it
says, and which one succeeded is the finding.

Step 7 should accept all three signals at the API and behave differently at the node. `SIGKILL` and
`SIGSTOP` are in the enum, so validation has no grounds to refuse them; whether a container asked to
stop with `SIGSTOP` is stopped at all, or hangs until the grace period expires and is killed, is the
measurement, and the elapsed seconds printed by the loop is how you read it. Expect `SIGCLD` to be
stored verbatim rather than normalised to `SIGCHLD`. A container whose only handler for it is a
non-exiting trap should also run out its grace period, which tells you the kubelet does not check
that the signal you chose can end the process.

Step 8 should print a containerd version — record it, it is the third column of the ladder — and
then either a `stopSignal` or `StopSignal` string somewhere in the container inspect output, or
nothing at all. Nothing at all is a legitimate result and the likelier one: the field may be passed
on the stop call rather than stored in the container's configuration, in which case the kubelet
journal is the only place it appears. Expect the journal lines to name the container and the grace
period; if any of them names a signal, quote it, because no page in the pinned tree shows what that
line looks like.

Step 9 should settle three things at once. The container should report `running` after roughly
thirty seconds, not immediately, which makes `attach-handler-lifecycle-event.md:71-72` the accurate
sentence and the concept page's "may not transition" the hedged one — but check `logs` as well,
because `entrypoint-started` should be printed at the beginning of those thirty seconds, which is
what `container-lifecycle-hooks.md:31-32` means by concurrent and what `:71` gets wrong by saying
the container is paused. The `postStart` hook being accepted at all settles the PreStop-only framing
of the v1.32 and v1.33 release notes. Expect a zero duration to be accepted on both hooks and a
negative one to be rejected by validation; if negative is accepted, the post's sentence at `:19`
that a negative value returns immediately is the only description of that behaviour anywhere, and
that is worth its own note.

Step 10 should print, in order: one occurrence of `PodLifecycleSleepActionAllowZero` under `docs/`,
which is the `title:` line of the unrendered gate definition; three files in the whole tree that
name it, that gate definition and two blog posts; zero occurrences of `sleep:` under `docs/` and
`examples/`; four example files that set `lifecycle:`; three documentation pages that mention a stop
signal; zero `feature-state` shortcodes in the container lifecycle hooks page; 65 distinct signal
names in the enum; and a version tally in which `v1.35` appears exactly once against 31 at `v1.36`.
Any number that comes back different means the pin moved under you; re-read the count before
trusting anything above it.

**Read on**

11. [The gate that entered alpha in the same release and did not
    stall](03-ensure-secret-pulled-images.md) — the other 1.33 alpha this exercise counts, three
    releases further along, and the exercise that works the kubelet configuration file in detail.

12. [Termination order between a sidecar and the container it
    serves](../2023/09-native-sidecar-containers.md) — what happens after the signal this exercise
    chooses has been delivered, when there is more than one container to deliver it to.

13. [Fifteen cells of EndpointSlice conditions for five pod
    states](../../labs/07/04-eleven-kilobytes-of-endpointslice.md) — a `preStop` hook used to hold a
    pod in `Terminating` long enough to read what the endpoint list says about it.

14. [A readiness probe followed all the way to an endpoint
    list](../../labs/01/15-endpointslice-drains.md) — the race between an address leaving a slice
    and a container receiving its signal.

15. [Moving the apiserver's manifest out of the directory](../../labs/01/04-static-pod-blip.md) —
    what the kubelet does with the file step 4 edits, and what the cluster looks like in between.

**Teardown**

```sh
kubectl delete namespace bw-css --ignore-not-found
ssh zain@10.10.10.180 "sudo diff /tmp/bw-apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml; sudo cp /tmp/bw-apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml"
until kubectl get --raw /readyz >/dev/null 2>&1; do sleep 3; done
ssh zain@10.10.10.180 "sudo diff /tmp/bw-kubelet.yaml.bak /var/lib/kubelet/config.yaml; sudo cp /tmp/bw-kubelet.yaml.bak /var/lib/kubelet/config.yaml && sudo systemctl restart kubelet"
until kubectl get nodes 2>/dev/null | grep -q ' Ready '; do sleep 3; done
ssh zain@10.10.10.180 "sudo rm -f /tmp/bw-apiserver.yaml.bak /tmp/bw-kubelet.yaml.bak"
kubectl get nodes
kubectl explain pod.spec.containers.lifecycle.stopSignal | head -3
```

Run the two `diff` lines before the two `cp` lines and read them: each should show exactly the one
line the exercise added, and nothing else. The last command is there to make the point the exercise
opened with — with both gates off again, the apiserver still describes the field as if you could use
it.
