<a id="kubernetes-1-31-custom-profiling-kubectl-debug"></a>

# Two of the three fields the post's second worked example changes are forbidden on the kind of container its first example creates, the default profile the task page names is not the one the reference page names, and the switch that made this beta has no record anywhere in the tree

**Post** — [Kubernetes 1.31: Custom Profiling in Kubectl Debug Graduates to Beta](https://kubernetes.io/blog/2024/08/22/kubernetes-1-31-custom-profiling-kubectl-debug/),
2024-08-22.

3,549 bytes over 103 lines: the fifth-smallest of the fifty-four 2024 posts and the second-smallest
of the thirteen the year marks `walk`. One author, Arda Güçlü of Red Hat, and three people thanked
at `:99-103`. Five fenced blocks in a post of ten prose paragraphs — two shell, two YAML, one JSON —
which is an unusually high ratio of example to argument, and the reason this exercise is the
cheapest in the year to run: one node, one namespace, a `busybox` image and no reboots. Three lines
carry trailing whitespace (`:11`, `:20`, `:43`), one of the ten paragraphs is the two words *and
execute:*, and the file has no final newline — small evidence, but it is the only evidence, that
this one was typed rather than generated.

**As written**

`:10-16` opens on the thing that already worked. `kubectl debug` ships a set of *static profiles*,
one per role, and the example given is a network administrator taking a node: `kubectl debug
node/mynode -it --image=busybox --profile=netadmin`. `:18-20` names the cost of that design —
*static profiles also bring about inherent rigidity* — and `:22-36` gives the case it breaks on: a
Pod whose container will not start healthy without an environment variable, shown as a twelve-line
manifest with `image: customapp:latest` and `REQUIRED_ENV_VAR=value1`.

`:38-39` states the problem in one sentence and one rhetorical question: copying the Pod is *the
sole mechanism that supports debugging this pod*, and if you need the variable set to something else
for the debugging run, *there is no mechanism to achieve this*.

`:41-57` is the answer. A new flag, `--custom`, taking a partial `Container` spec in YAML or JSON.
The first example is four lines of YAML setting one environment variable, applied with `kubectl
debug example-pod -it --image=customapp --custom=partial_container.yaml`, and `:44` says what shape
of debugging it is doing: *by creating an ephemeral container*.

`:59-85` is the second example, and it is the one this exercise is mostly about. Twenty-five lines
of JSON introduced as *another example that modifies multiple fields at once*, with the three fields
named in the prose: *change port number, add resource limits, modify environment variable*. The JSON
sets `ports`, `resources` with both limits and requests, and `env`.

`:87-90` is a section called `Constraints`, and it lists what you may not customise: *command,
image, lifecycle, volume devices and container name*. It closes by predicting the list will grow —
*in the future, more fields can be added to the disallowed list if required*.

`:92-95` is a section called `Limitations`, and it is a claim about shape rather than about a field.
`kubectl debug` has three aspects — ephemeral containers, pod copying, node debugging — and *the
largest intersection set of these aspects is the container spec within a Pod*, so custom profiling
supports container fields and not Pod fields. The sentence that says so is missing its full stop.

**As it runs now**

**The post's second example cannot be applied to the container its first example creates.**
`pod-v1.md:1225` is the `EphemeralContainer` type, and it is a `Container` with holes cut in it.
`:1274` against `ports` reads *Ports are not allowed for ephemeral containers.* `:1286` against
`resources` reads *Resources are not allowed for ephemeral containers. Ephemeral containers use
spare resources already allocated to the pod.* Those are two of the three things the post says its
JSON changes. The third, `env`, is fine. So the example is two-thirds inadmissible in the aspect the
post had just demonstrated, and entirely admissible in the other two, where the container being
built is an ordinary one. The post does not say which aspect the JSON is for, and nothing in it
suggests the answer changes with the aspect. Steps 4 to 7 submit it three times and collect three
different outcomes.

**The list of forbidden fields the documentation gives is not the list the API enforces.**
`debug-running-pod.md:767-772` carries a note with five names — `name`, `image`, `command`,
`lifecycle`, `volumeDevices` — and adds that the Pod spec is out of reach. Those five are kubectl's
list, refused client-side. The `EphemeralContainer` table refuses six more, and one of them
overlaps: `lifecycle` at `:1262`, `ports` at `:1274`, `resources` at `:1286`, probes at `:1266`,
`:1278` and `:1302`, and subpath mounts at `:1334`. `lifecycle` appears on both lists; `ports`,
`resources` and the three probes appear only on the second, where the rejection arrives from the API
server after kubectl has already accepted the file. The post's `Constraints` section at `:89`
reproduces kubectl's five and nothing else.

**The post predicted the forbidden list would grow, and it has not.** `:90` says *in the future,
more fields can be added to the disallowed list if required*. The note at `debug-running-pod.md:769`
at the pin names the same five, in a different order, with `volumeDevices` spelled as one word
rather than two. Step 8 submits all five and then submits four that ought still to be allowed.

**The default profile the task page names is not the default the reference page gives.**
`debug-running-pod.md:702` says *if you don't specify `--profile`, the `legacy` profile is used by
default, but it is planned to be deprecated in the near future*, and the table at `:691-698` lists
`legacy` as the first of six profiles. The generated flag reference at
`kubectl_debug/_index.md:195-198` says `Default: "general"` and enumerates five options — *general*,
*baseline*, *restricted*, *netadmin*, *sysadmin*. `legacy` is not among them. Two pages in one
checkout, one flag, two different defaults and two different option sets. One command settles it,
and it is step 1.

**`legacy` survives in exactly two places, both on the same page.** Across all of `content/en` the
word appears as a debug profile only at `debug-running-pod.md:693`, in the table row whose
description is *A set of properties backwards compatibility with 1.22 behavior*, and at `:702`, in
the note that calls it the default. The generated reference dropped it; nothing else mentions it. A
profile named for compatibility with a release eleven behind the one this post announces is the only
entry in the table the reference does not know about.

**There is no record of how this was ever a beta.** The post's title says *Graduates to Beta*. There
is no file for it under the feature-gates directory, because it was never an API server feature; it
is client-side, and kubectl's switches are not gates in that sense. But the string `KUBECTL_DEBUG`
occurs zero times in the whole pinned checkout. This is not a general gap in the documentation of
kubectl switches: `kubectl_debug/_index.md:366` prints, on the `--kuberc` flag, *this can be
disabled by exporting KUBECTL_KUBERC=false feature gate or turning off the feature KUBERC=off*, and
the same sentence is repeated on dozens of other generated pages. kubectl gating is documented at
the pin. It is documented for `kuberc` and not for this. Step 9 goes looking and comes back empty,
which is the finding.

**The stable banner on this feature is hand-written.** `debug-running-pod.md:762` is `{{<
feature-state for_k8s_version="v1.32" state="stable" >}}` — the two-argument form that states a
version and a stage directly, rather than the `feature_gate_name` form that reads a gate record.
There is no record to read. Taken with the post, the shape is beta at v1.31 and stable at v1.32: one
release. That is worth holding beside the [exercise on the pod failure policy GA
post](09-pod-failure-policy-for-jobs-goes-ga.md) from three days earlier in the same month, where
three banners on the same shortcode are keyed to gate records that have been deleted. The same
shortcode is doing two different jobs in the same tree, and only one of them can go stale on its
own.

**The post's own worked example has never been runnable.** `:32` gives the target Pod `image:
customapp:latest` and `:56` debugs it with `--image=customapp`, an image that exists in no registry.
The documentation's version of the same walkthrough at `debug-running-pod.md:774-819` replaced both
with `busybox:1.28`, replaced the partial container with a different one — two environment variables
and `NET_ADMIN` plus `SYS_TIME` capabilities at `:784-793` — and added `--profile=general` to a
command line the post left bare at `:56`. Step 2 runs the documentation's version, which works; step
3 runs the post's shape with a real image, which also works.

**The `Limitations` claim is the wrong way round.** `:94-95` says the container spec is *the largest
intersection set* of the three aspects of `kubectl debug`. It is the intersection only if all three
take the same container spec, and they do not: two take a `Container` and one takes an
`EphemeralContainer`, which `pod-v1.md:1225-1341` defines as a `Container` with `ports`,
`resources`, three probes, `lifecycle`, `restartPolicy` and subpath mounts removed. The intersection
is the smaller type, not the larger one, and the post's second example is written against the larger
one.

**The flag itself is exactly what the post says it is.** `--custom` takes a path to a JSON or YAML
file containing a partial container spec, composes with `--profile`, and is described at
`kubectl_debug/_index.md:111-114` in one sentence that matches `:43` of the post almost word for
word. Nothing about the mechanism drifted. Everything in this exercise is about the two examples
around it and the pages that describe it.

**And the thing the documentation cannot settle with itself.** `pod-v1.md:1227` introduces ephemeral
containers with two sentences that sit awkwardly together: *Ephemeral containers have no resource or
scheduling guarantees*, and *the kubelet may evict a Pod if an ephemeral container causes the Pod to
exceed its resource allocation.* The whole premise of `kubectl debug` on a running Pod — the premise
`debug-running-pod.md` is built on, and the reason the post wants to reach into production Pods — is
that attaching a debugger is the safe move. The same paragraph says attaching one may get the Pod
killed. That is also why `resources` is refused at `:1286`: you cannot reserve headroom for the
debugger, so the post's *add resource limits* is asking for the one thing the design forbids.
Neither page gives a threshold, neither says how much room a debug container may take before the
eviction it warns about happens, and a one-node lab with no memory pressure cannot produce it on
demand. Both halves are quoted here and neither is picked.

**What this exercise does not cover, and where it lives**

What an ephemeral container is, and the first demonstration of putting one into a running Pod,
belong to [the exercise on nine kubectl features and six
fates](../2015/09-some-things-you-didnt-know-about-kubectl.md), which runs `kubectl debug pod/redis
-it --image=busybox --target=redis` and reads the target's filesystem through `/proc/1/root`. Node
debugging — `kubectl debug node/`, and what the debug Pod gets that an ordinary Pod does not —
belongs to [the exercise on the security post the project marked partly
obsolete](../2016/08-security-best-practices-kubernetes-deployment.md). Step 7 below uses `node/`
only as the third place to submit one JSON file. Why a container's resources cannot be changed after
it starts, and which container kinds are excluded from the mechanism that changes them, is [the
exercise on the in-place resize alpha](../2023/07-in-place-pod-resize-alpha.md), which already
records that init and ephemeral containers cannot be resized. Pod Security Standards, which two of
the six static profiles are named after, are not touched here at all.

**The diff, and why**

**Still right.** The flag exists, takes what the post says it takes, composes with `--profile`, and
refuses the five fields the post's `Constraints` section names. Steps 2, 3 and 8 confirm all of it.
For a post this short that is most of the surface area, and it should be said before the rest.

**Wrong when it was published.** The JSON at `:61-85` sets `ports` and `resources` on what `:44` has
just established is an ephemeral container. `pod-v1.md` forbade both then and forbids both now; this
is not drift. The post did not test its second example against the aspect its first example
introduced, and the aspect it *would* be valid for — pod copying, node debugging — is mentioned only
two sections later, in `Limitations`, in a sentence that gets the containment backwards. Step 4 is
one command and it has been failing since the day the post went up.

**Overtaken by stasis.** The `legacy` profile is the clearest case. It is still tabled and still
called the default on the task page; the generated reference, which is regenerated from kubectl's
own flag help, has dropped it from both the default and the option list. The task page was not
edited when kubectl changed, and nothing links the two. The prose warning that `legacy` *is planned
to be deprecated in the near future* has outlived the deprecation it predicted.

**Retired by being agreed with.** Custom profiling went beta in v1.31 and stable in v1.32, and the
only evidence of its beta period left in the tree is this post's title. The switch is gone, the env
var is unmentioned, and the banner that marks the feature stable was typed by hand rather than read
off a record. There is nothing left to turn off, which is why this exercise has no ladder.

**Never absorbed.** The post's prediction at `:90` that more fields would join the disallowed list
did not happen, and neither did the natural fix for what this exercise finds: kubectl still does not
refuse `ports` or `resources` on an ephemeral-container debug, so the error still comes from the API
server, in the API server's words, about a field the user wrote into a file the client had already
accepted.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 cores, at `10.10.10.180`,
running Kubernetes v1.35. Bring it up with [the provision
steps](../../strands/lab-topologies.md#provision) and install Kubernetes with [the node baseline
procedure](../../strands/lab-topologies.md#node-baseline-steps). This is the cheapest exercise in
the year: everything below is `busybox:1.28`, one namespace called `bw-dbg`, and no step touches the
node's configuration or restarts anything. One node is enough because step 7 debugs *a* node and
there is only one to debug. Note that an ephemeral container cannot be removed from a Pod once added
— `pod-v1.md:1229` says so — so each step that adds one uses a fresh Pod rather than reusing the
last. The offline reads are against the pinned checkout at `/path/to/kubernetes/website/content/en`;
`W` below is that path.

**Do**

1. Settle the default. Read what kubectl says about `--profile`, then ask for the profile the task
   page calls the default. Compare all three answers: `debug-running-pod.md:702`,
   `kubectl_debug/_index.md:195-198`, and the binary.

   ```sh
   kubectl version -o json | grep -E '"gitVersion"'
   kubectl debug --help | grep -A3 -- '--profile'
   kubectl create namespace bw-dbg
   kubectl -n bw-dbg run app1 --image=busybox:1.28 --restart=Never -- sleep 1d
   kubectl -n bw-dbg wait --for=condition=Ready pod/app1 --timeout=180s
   kubectl -n bw-dbg debug app1 --image=busybox:1.28 --target=app1 --profile=legacy -- true
   kubectl -n bw-dbg get pod app1 -o jsonpath='{range .spec.ephemeralContainers[*]}{.name}{"\n"}{end}'
   ```

2. Run the documentation's own custom-profile walkthrough, verbatim from
   `debug-running-pod.md:774-819`. The file it asks for is at `:784-793`; this writes it out rather
   than retyping it, so any drift between what you read and what you run is impossible.

   ```sh
   W=/path/to/kubernetes/website/content/en
   sed -n '784,793p' $W/docs/tasks/debug/debug-application/debug-running-pod.md > /tmp/custom-profile.yaml
   cat /tmp/custom-profile.yaml
   kubectl -n bw-dbg run app2 --image=busybox:1.28 --restart=Never -- sleep 1d
   kubectl -n bw-dbg wait --for=condition=Ready pod/app2 --timeout=180s
   kubectl -n bw-dbg debug app2 --image=busybox:1.28 --target=app2 \
     --profile=general --custom=/tmp/custom-profile.yaml -- true
   kubectl -n bw-dbg get pod app2 -o jsonpath='{.spec.ephemeralContainers[0].env}{"\n"}'
   kubectl -n bw-dbg get pod app2 -o jsonpath='{.spec.ephemeralContainers[0].securityContext}{"\n"}'
   ```

3. Now the post's shape: one environment variable, no `--profile` on the command line, against a Pod
   that actually carries the variable the post's example Pod carries. The image is the only thing
   changed, because `customapp:latest` does not exist.

   ```sh
   kubectl -n bw-dbg run app3 --image=busybox:1.28 --restart=Never \
     --env=REQUIRED_ENV_VAR=value1 -- sleep 1d
   kubectl -n bw-dbg wait --for=condition=Ready pod/app3 --timeout=180s
   cat > /tmp/partial_container.yaml <<'YAML'
   env:
     - name: REQUIRED_ENV_VAR
       value: value2
   YAML
   kubectl -n bw-dbg debug app3 --image=busybox:1.28 --target=app3 \
     --custom=/tmp/partial_container.yaml -- true
   kubectl -n bw-dbg get pod app3 -o jsonpath='{.spec.containers[0].env}{"\n"}'
   kubectl -n bw-dbg get pod app3 -o jsonpath='{.spec.ephemeralContainers[0].env}{"\n"}'
   ```

4. The post's second example, verbatim, against an ephemeral container — the aspect `:44`
   introduced. This is the whole finding in one command.

   ```sh
   cat > /tmp/post-json-profile.json <<'JSON'
   {
     "ports": [
       {
         "containerPort": 80
       }
     ],
     "resources": {
       "limits": {
         "cpu": "0.5",
         "memory": "512Mi"
       },
       "requests": {
         "cpu": "0.2",
         "memory": "256Mi"
       }
     },
     "env": [
       {
         "name": "REQUIRED_ENV_VAR",
         "value": "value2"
       }
     ]
   }
   JSON
   kubectl -n bw-dbg run app4 --image=busybox:1.28 --restart=Never -- sleep 1d
   kubectl -n bw-dbg wait --for=condition=Ready pod/app4 --timeout=180s
   kubectl -n bw-dbg debug app4 --image=busybox:1.28 --target=app4 \
     --custom=/tmp/post-json-profile.json -- true
   ```

5. Bisect it. Three files, one field each, three fresh Pods, so you learn which of the three the
   post names is the one that is fine and which two are not — and, from the wording of each error,
   whether kubectl refused it or the API server did.

   ```sh
   printf '{"ports":[{"containerPort":80}]}\n'                  > /tmp/only-ports.json
   printf '{"resources":{"limits":{"memory":"512Mi"}}}\n'       > /tmp/only-resources.json
   printf '{"env":[{"name":"X","value":"y"}]}\n'                > /tmp/only-env.json
   for n in 5a 5b 5c; do
     kubectl -n bw-dbg run app$n --image=busybox:1.28 --restart=Never -- sleep 1d
   done
   kubectl -n bw-dbg wait --for=condition=Ready pod/app5a pod/app5b pod/app5c --timeout=180s
   for pair in "app5a only-ports" "app5b only-resources" "app5c only-env"; do
     set -- $pair
     echo "--- $2 ---"
     kubectl -n bw-dbg debug "$1" --image=busybox:1.28 --target="$1" --custom=/tmp/$2.json -- true
   done
   ```

6. The same JSON against the second aspect: pod copying. Here the thing being built is an ordinary
   container in a new Pod, so the `EphemeralContainer` restrictions do not apply.

   ```sh
   kubectl -n bw-dbg run app6 --image=busybox:1.28 --restart=Never -- sleep 1d
   kubectl -n bw-dbg wait --for=condition=Ready pod/app6 --timeout=180s
   kubectl -n bw-dbg debug app6 --image=busybox:1.28 --copy-to=app6-copy \
     --custom=/tmp/post-json-profile.json -- sleep 1d
   kubectl -n bw-dbg get pod app6-copy \
     -o jsonpath='{range .spec.containers[*]}{.name}{"\t"}{.ports}{"\t"}{.resources}{"\n"}{end}'
   ```

7. And the third aspect: node debugging. Same file, a third kind of target. The debug Pod runs in
   `bw-dbg` so teardown catches it.

   ```sh
   NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl -n bw-dbg debug node/"$NODE" --image=busybox:1.28 \
     --profile=general --custom=/tmp/post-json-profile.json -- sleep 1d
   kubectl -n bw-dbg get pods -o name | grep node-debugger
   kubectl -n bw-dbg get pods -o json | grep -o '"containerPort":[0-9]*' | sort -u
   ```

8. The five fields the post's `Constraints` section names, one at a time, and then four it does not,
   to test the prediction at `:90` that the list would have grown. Every one of these is refused or
   accepted by kubectl before the API server sees it, so a single Pod is enough — nothing that fails
   adds a container.

   ```sh
   kubectl -n bw-dbg run app8 --image=busybox:1.28 --restart=Never -- sleep 1d
   kubectl -n bw-dbg wait --for=condition=Ready pod/app8 --timeout=180s
   for j in '{"name":"nope"}' \
            '{"image":"busybox:1.36"}' \
            '{"command":["sh"]}' \
            '{"lifecycle":{"preStop":{"exec":{"command":["true"]}}}}' \
            '{"volumeDevices":[{"name":"d","devicePath":"/dev/x"}]}' \
            '{"workingDir":"/tmp"}' \
            '{"tty":true}' \
            '{"imagePullPolicy":"Never"}' \
            '{"securityContext":{"runAsUser":1000}}'; do
     echo "--- $j"
     printf '%s\n' "$j" > /tmp/one-field.json
     kubectl -n bw-dbg debug app8 --image=busybox:1.28 --target=app8 \
       --custom=/tmp/one-field.json -- true 2>&1 | head -2
   done
   kubectl -n bw-dbg get pod app8 -o jsonpath='{range .spec.ephemeralContainers[*]}{.name}{"\n"}{end}'
   ```

9. Go looking for the switch the post's title implies. Ask kubectl for anything gate-shaped on this
   command, ask it for the one client-side gate the tree does document, and ask the checkout for the
   string that would name this one.

   ```sh
   W=/path/to/kubernetes/website/content/en
   kubectl debug --help | grep -inE 'gate|alpha|beta|experiment|KUBECTL_' || echo 'nothing gate-shaped on kubectl debug'
   kubectl options | grep -i kuberc
   grep -rc 'KUBECTL_DEBUG' $W || echo 'KUBECTL_DEBUG: zero occurrences in the checkout'
   grep -rln 'KUBECTL_KUBERC' $W/docs/reference/kubectl/generated | wc -l
   ls $W/docs/reference/command-line-tools-reference/feature-gates/ | grep -icE 'debug|profile|kubectl' || true
   ```

10. Offline, against the pinned checkout. Four reads: the two profile lists side by side, the
    hand-written stable banner, the note that says which fields kubectl refuses, and the
    `EphemeralContainer` rows that say which fields the API refuses.

    ```sh
    cd /path/to/kubernetes/website/content/en
    sed -n '686,704p' docs/tasks/debug/debug-application/debug-running-pod.md
    sed -n '195,199p' docs/reference/kubectl/generated/kubectl_debug/_index.md | sed -e 's/<[^>]*>//g'
    grep -rn '`legacy`\|^| legacy' --include='*.md' docs | grep -i 'profile\|1.22'
    sed -n '760,772p' docs/tasks/debug/debug-application/debug-running-pod.md
    sed -n '1225,1229p' docs/reference/kubernetes-api/core/pod-v1.md | sed -e 's/<[^>]*>//g'
    grep -n 'not allowed for ephemeral containers' docs/reference/kubernetes-api/core/pod-v1.md
    sed -n '111,115p;363,367p' docs/reference/kubectl/generated/kubectl_debug/_index.md | sed -e 's/<[^>]*>//g'
    ```

**Expect**

Step 1 prints `v1.35`. The help text for `--profile` gives `general` as the default and lists five
names with `legacy` absent — the generated reference at `kubectl_debug/_index.md:195-198` is right
and `debug-running-pod.md:702` is wrong. Asking for `--profile=legacy` therefore fails, and fails
client-side with a message about an unsupported profile rather than anything from the API server;
the ephemeral-container list on `app1` stays empty. If instead the profile is accepted and a
container appears, note it and carry that forward, because every later step's default changes with
it.

Step 2 works cleanly, which is the point of running it first. The file extracted from the page is
ten lines: two environment variables and a `securityContext` adding `NET_ADMIN` and `SYS_TIME`. The
debug container is created, and the two read-backs print
`[{"name":"ENV_VAR_1","value":"value_1"},{"name":"ENV_VAR_2","value":"value_2"}]` and
`{"capabilities":{"add":["NET_ADMIN","SYS_TIME"]}}`, matching `debug-running-pod.md:806-818`
exactly. That is the documentation's walkthrough reproducing itself at v1.35 with nothing changed.

Step 3 is the post's own case with a real image. The target Pod's own container carries
`REQUIRED_ENV_VAR=value1`; the ephemeral container carries `value2`. Two containers in one Pod,
sharing the same target namespaces, disagreeing about one variable — which is precisely the thing
`:38-39` said there was no mechanism to achieve. It also runs without `--profile`, so whatever step
1 found the default to be is what this container was built from.

Step 4 fails. The post's JSON is accepted by kubectl — the client checks only its own five names —
and refused by the API server, which is where the error text comes from. Expect it to name
`spec.ephemeralContainers[0].ports` and `spec.ephemeralContainers[0].resources` and to say they are
not allowed, the sentences at `pod-v1.md:1274` and `:1286` in their enforced form. No ephemeral
container is added to `app4`. This is the exercise's centre: a worked example from a GA-track
announcement that the API has never accepted for the aspect the post was demonstrating.

Step 5 separates the three. `only-env.json` succeeds. `only-ports.json` and `only-resources.json`
both fail, and both errors come from the API server rather than from kubectl — read the prefix of
each message and note which component is speaking. Two fields out of three, and the one the post's
prose puts last is the only one that works. If a message instead mentions kubectl's own validation,
the client-side list has grown since the pin and the post's prediction at `:90` came true late;
record which field.

Step 6 succeeds where step 4 failed, with the same file. `app6-copy` is a new Pod holding an
ordinary container, so `containerPort: 80` and the CPU and memory limits and requests are all
present in the read-back. Nothing about the JSON changed; only what kubectl was asked to build from
it. Hold this beside step 4 and the `Limitations` paragraph at `:94-95` reads backwards: the
container spec is not the largest intersection of the three aspects, it is two supersets and one
subset.

Step 7 succeeds as well, and the `node-debugger` Pod carries the port. That is the third of three:
rejected once, accepted twice, from one file. The `grep` for `containerPort` is a coarse instrument
on purpose — it will match the debug Pod and nothing else in the namespace at this point.

Step 8 prints nine results. The first five — `name`, `image`, `command`, `lifecycle`,
`volumeDevices` — are refused by kubectl with a message naming the field, which is the `Constraints`
section at `:89` and the note at `debug-running-pod.md:769` both holding. The last four —
`workingDir`, `tty`, `imagePullPolicy`, `securityContext` — are accepted, and `app8` ends with four
ephemeral containers on it, one per success. Four accepted fields is the answer to the post's *more
fields can be added to the disallowed list*: two years on, none were.

Step 9 comes back empty, and the emptiness is the finding. `kubectl debug --help` says nothing about
gates, alpha, beta or any `KUBECTL_` variable. `kubectl options` does print the `--kuberc` line with
its *KUBECTL_KUBERC=false feature gate* sentence, so the mechanism exists and is documented — for a
different feature. The recursive grep for `KUBECTL_DEBUG` across the whole checkout returns nothing,
and the feature-gates directory has no file matching `debug`, `profile` or `kubectl`. A post whose
title is *Graduates to Beta* has left no trace of the switch that beta was behind.

Step 10 is all reading. The static-profile section prints six rows and a note calling `legacy` the
default; the reference stanza three lines later prints `Default: "general"` and five options. The
`legacy` census returns two hits, both on the task page. The custom-profile section shows `{{<
feature-state for_k8s_version="v1.32" state="stable" >}}` with no gate name in it, and the note
beneath it with its five field names. The `EphemeralContainer` header paragraph gives the two
sentences that cannot both be comfortable — no resource guarantees, and the kubelet may evict the
Pod — and the grep beneath it returns seven rows of *not allowed for ephemeral containers*, of which
only `lifecycle` also appears in kubectl's list. Finally the `--custom` flag's own description, one
sentence, still correct.

**Read on**

11. [The exercise on nine kubectl features and six
    fates](../2015/09-some-things-you-didnt-know-about-kubectl.md) — where `kubectl debug` first
    appears in this archive, as the thing that arrived to fill a gap a 2015 post could not have
    named.

12. [The exercise on the security post the project marked partly
    obsolete](../2016/08-security-best-practices-kubernetes-deployment.md) — it owns `kubectl debug
    node/`, which step 7 above borrows for one submission and gives back.

13. [The exercise on the in-place pod resize alpha](../2023/07-in-place-pod-resize-alpha.md) — for
    why container resources are not an ordinary mutable field, and for the limitation list that
    already records ephemeral containers as excluded.

14. [The exercise on the pod failure policy GA post](09-pod-failure-policy-for-jobs-goes-ga.md) —
    three days earlier in the same month, and the other half of the `feature-state` story: banners
    keyed to gate records that no longer exist, against this one's banner with no record behind it
    at all.

15. [Stage 2 of the webhook lab](../../labs/03/21-the-webhook-behind-a-service.md) — the one place
    in the repo where `kubectl debug --target` is not an exercise about `kubectl debug` but the only
    way into a `scratch` image that has no shell.

**Teardown**

```sh
kubectl delete namespace bw-dbg --wait=true
rm -f /tmp/custom-profile.yaml /tmp/partial_container.yaml /tmp/post-json-profile.json \
      /tmp/only-ports.json /tmp/only-resources.json /tmp/only-env.json /tmp/one-field.json
kubectl get nodes -o wide
```
