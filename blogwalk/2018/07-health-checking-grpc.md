<a id="health-checking-grpc"></a>
# The project agreed with this post and turned the tool into a field, and the field is not a superset of the tool it replaced: `grpc` is the only one of the four probe mechanisms that can be given neither a port name nor a host, and it runs from the node rather than from inside the container over `localhost`

**Post** — [Health checking gRPC servers on Kubernetes](https://kubernetes.io/blog/2018/10/01/health-checking-grpc/),
2018-10-01, by Ahmet Alp Balkan (Google). 101 lines and 5,064 bytes, the second-smallest `walk` in
this year after [the dynamic kubelet configuration exercise](05-dynamic-kubelet-configuration.md).
`manifest.tsv` dates the v1.12 release announcement 2018-09-27, so the current Kubernetes was four
days old when this went up.

Like that post, the first line of the pinned copy is not the author's. Unlike that post's, it is not
a retraction: "**Update (December 2021):** _Kubernetes now has built-in gRPC health probes starting
in v1.23. To learn more, see [Configure Liveness, Readiness and Startup Probes](...). This article
was originally written about an external tool to achieve the same task._" (`:9-11`). A note added
more than three years after publication, pointing at the thing the post spent its last paragraph
asking for.

**As written** — a diagnosis, a standard, and a tool to carry the standard.

The diagnosis is the durable part. "Kubernetes [does not support] gRPC health checks natively"
(`:26-28`), where the link is to a Kubernetes issue rather than to documentation, because in 2018
the absence was the subject. That absence leaves three options, each with an objection:

- "**httpGet probe:** Cannot be natively used with gRPC. You need to refactor your app to serve both
  gRPC and HTTP/1.1 protocols (on different port numbers)." (`:34-36`)
- "**tcpSocket probe:** Opening a socket to gRPC server is not meaningful, since it cannot read the
  response body." (`:37-38`)
- "**exec probe:** This invokes a program in a container's ecosystem periodically. In the case of
  gRPC, this means you implement a health RPC yourself, then write and ship a client tool with your
  container." (`:39-41`)

"Can we do better? Absolutely." (`:43`)

The post's answer is to make the third option bearable by standardising both of its halves: "a
**standard** health check "protocol" that can be implemented in any gRPC server easily" and "a
**standard** health check "tool" that can query the health protocol easily" (`:49-51`). The protocol
already existed, and the post links it at tag `v1.15.0` (`:53-54`). The tool is
`grpc-health-probe`, and the post's three instructions are to find the health module for your
language, "Ship the [grpc_health_probe] binary in your container", and configure a Kubernetes exec
probe to invoke it (`:75-82`).

Then the sentence this exercise turns on: "In this case, executing "grpc_health_probe" will call
your gRPC server over `localhost`, since they are in the same pod." (`:84-85`)

The close is a request rather than a claim. The project "is still in its early days and it needs
your feedback", and "It supports a variety of features like communicating with TLS servers and
configurable connection/RPC timeouts" (`:89-91`).

**As it runs now** — the request was granted. The tool the post asks you to ship is a field on the
Pod, and the exercise is the difference between those two things.

*The list of three is a list of four.* `probes.md:149-152` opens the mechanisms section with
"There are four different ways to check a container using a probe. Each probe must define exactly
one of these four mechanisms", and the fourth is `grpc`: "Performs a remote procedure call using
gRPC. The target should implement gRPC health checks. The diagnostic is considered successful if the
`status` of the response is `SERVING`" (`:158-162`). The post's two objections to the other
mechanisms are not merely still true, they are restated by the documentation as properties.
`httpGet` "Performs an HTTP `GET` request against the Pod's IP address on a specified port and path"
(`:164-168`) — still HTTP/1.1 unless you opt in, of which more below. And `tcpSocket` "Performs a
TCP check against the Pod's IP address on a specified port. The diagnostic is considered successful
if the port is open. If the remote system (the container) closes the connection immediately after it
opens, this counts as healthy" (`:170-176`), which is the post's "cannot read the response body"
written as a guarantee. The one mechanism the page argues against is the one the post recommends:
`:177-184` is a `caution` block saying that "Unlike the other mechanisms, `exec` probe's
implementation involves the creation/forking of multiple processes each time when executed", that
this "might introduce an overhead on the cpu usage of the node", and that "In such scenarios,
consider using the alternative probe mechanisms to avoid the overhead."

*The field is not a superset of the tool.* Each mechanism is a distinct type in the generated Pod
API reference, and the types are not the same size. Measured from
`reference/kubernetes-api/core/pod-v1.md`, where `Probe` itself is at `:2341` and lists ten fields —
the four mechanisms and six knobs:

| mechanism | type | at | fields | port by name | host |
|---|---|---|---|---|---|
| `exec` | `ExecAction` | `:1361` | `command` | not applicable | runs inside the container |
| `grpc` | `GRPCAction` | `:1440` | `port`, `service` | no | no |
| `httpGet` | `HTTPGetAction` | `:1513` | `host`, `httpHeaders`, `path`, `port`, `scheme` | yes | yes |
| `tcpSocket` | `TCPSocketAction` | `:2943` | `host`, `port` | yes | yes |

`GRPCAction` is the only one of the four that cannot be told where to connect. The reference says
its `port` must be an integer — "Port number of the gRPC service. Number must be in the range 1 to
65535" (`:1450-1451`) — while `httpGet` and `tcpSocket` both take the port "Name or number"
(`:1535-1536`, `:2957-2958`). The task page states the consequence twice: "gRPC probes do not
support named ports" (`:287`) and, in a note, "Unlike HTTP or TCP probes, you cannot specify the
health check port by name, and you cannot configure a custom hostname" (`probes.md:465-468`).

*Where the check runs from is the whole of it.* `ExecAction`'s one-line description in the reference
is `ExecAction describes a "run in container" action` (`:1363`), and its `command` field is
documented as "the command line to execute inside the container" (`:1370-1371`). That is the post's
`localhost` sentence, restated by the API. Every other mechanism is the opposite: the task page's
first technical detail about the gRPC probe is "The probes run against the pod IP address or its
hostname. Be sure to configure your gRPC endpoint to listen on the Pod's IP address" (`:256-257`),
and `probes.md:439-441` says of the TCP mechanism that "the kubelet makes the probe connection at
the node, not in the Pod, which means that you can not use a service name in the `host` parameter
since the kubelet is unable to resolve it." The pin's own gRPC example carries the same fact as a
flag: `pods/probe/grpc-liveness.yaml:9` starts etcd with `--listen-client-urls http://0.0.0.0:2379`
and advertises `http://127.0.0.1:2379`. A server that binds only the loopback address satisfies the
post's tool and fails the field that replaced it, and nothing in the post could have told you that,
because when it was written the check ran in the same network namespace as the server.

*TLS was a feature of the tool in 2018 and is an alpha field at this pin.* The post's closing
paragraph lists "communicating with TLS servers" among the things `grpc-health-probe` already did.
The field's version of it is `GRPCContainerProbeTLS`, alpha and off from v1.37 — ten releases after
the gRPC probe went stable at v1.27 — and it is narrower than the tool's: "the `kubelet` connects
over TLS with `InsecureSkipVerify` and does not verify the server certificate. This matches the
behavior of HTTPS probes. Certificate verification is not supported" (`:277-279`). Turned off, which
is the default, the API does not reject the field; "the `kube-apiserver` removes the `mode` field
from new or updated Pods" (`:281-282`).

*The prose describes two probe fields the pin's own reference does not list.* `GRPCAction` at
`:1440` has exactly two rows, `port` and `service`; there is no `mode`. `HTTPGetAction` at `:1513`
has exactly five, and there is no `protocol` — the field `H2CContainerProbe` adds, described at
`probes.md:330-333` as "`protocol`: Protocol to use for the probe request. Defaults to `HTTP1`. Set
to `HTTP2` to probe over HTTP/2 cleartext (h2c)". Cite both and say they disagree: at this pin two
pages of prose document two fields that the generated reference does not carry, and both are alpha
and off. The post's first objection — that using `httpGet` means serving "both gRPC and HTTP/1.1
protocols" — is being answered from the other end twenty-five releases later, by teaching
the HTTP probe to speak HTTP/2 instead.

*The tool survives in exactly one place, and it is a footnote about a gate.* Across the whole of
`content/en/docs`, `grpc-health-probe` is named once, at
`configure-liveness-readiness-startup-probes.md:261-262`: "If `ExecProbeTimeout` feature gate is set
to `false`, grpc-health-probe does **not** respect the `timeoutSeconds` setting (which defaults to
1s), while built-in probe would fail on timeout." In the 767-post corpus it survives in two files:
this post and the 2022 beta announcement. So the last documented trace of the post's
recommendation is a warning that the tool and the field disagree about a Pod field, and the
disagreement only appears if you switch a gate off.

*That gate was born stable.* `ExecProbeTimeout`'s body is three sentences: "Ensure kubelet respects
exec probe timeouts. This feature gate exists in case any of your existing workloads depend on a
now-corrected fault where Kubernetes ignored exec probe timeouts." A gate that is stable in its
first row is not a feature being rolled out; it is an opt-out from a fix. Parse the `stages:` list of
all 488 gate files in the pinned tree and exactly **four** of them start at `stable`:
`ExecProbeTimeout` (v1.20), `ConsistentHTTPGetHandlers` (v1.25), `ExternalPolicyForExternalIP`
(v1.18) and `VolumeSubpath` (v1.10). All four have a single stage. Three of the four declare
`removed: true`, and two of those three say in their own bodies what they were for: "Fix a bug where
ExternalTrafficPolicy is not applied to Service ExternalIPs" and "Normalize HTTP get URL and Header
passing for lifecycle handlers with probers." So two of the four born-stable gates in the tree are
about probes, and `ExecProbeTimeout` is the only one of the four still live. It also reached
`stable` earlier than any other live gate, by a distance: of the 96 gate files that end at `stable`
with no `toVersion` and no `removed:` key, this one arrived at v1.20 and the next is
`PodSchedulingReadiness` at v1.30, ten releases later. It is also the only single-stage gate among
the 96; the other 95 have two, three or four. Seventeen releases after the timeout fix, the switch
that undoes it is still shipped, still settable, and still the only documentation the post's tool
has.

*The addresses did not survive as well as the advice.* The post links Kubernetes documentation twice,
at `:21` and `:100`, and both name
`/docs/tasks/configure-pod-container/configure-liveness-readiness-probes/`. The pinned file is
`configure-liveness-readiness-startup-probes.md`, whose front matter carries no `aliases:` entry,
and the old address is claimed by no page under `content/en/docs`. It does still appear in exactly
one file there, and the choice of file is unkind: `contribute/style/write-new-topic.md:27`, the guide
that teaches contributors how to write a task page, offers it as the example of "a longer task
page". The note added to the top of the post in 2021 links the current address and its fragment
(`#define-a-grpc-liveness-probe`) resolves to the heading at `:228` — so the sentence that was added
was written against a live address while the two sentences beneath it were left pointing at a dead
one. The gate file has the same trouble one level down: `ExecProbeTimeout.md` ends by sending you to
the task page at `#configure-probes`, and that fragment is defined at `probes.md:209`, on the
concept page, not on the page the link names. This is the same failure as the one
[the eleven ways exercise](06-11-ways-not-to-get-hacked.md) is built on, and the pinned tree does it
to itself as well: `:286` of this very task page links the Pod API reference at
`/docs/reference/kubernetes-api/workload-resources/pod-v1/`, there is no `workload-resources`
directory in the pinned tree at all — the file is at `reference/kubernetes-api/core/pod-v1.md`, with
no `aliases:` — and 23 files under `content/en/docs` still link that path.

*The eight-year-old post is the more reproducible document.* Five of its links name an immutable
ref: the protocol and the `health.proto` at tag `v1.15.0`, twice each (`:54`, `:60`, and both again
on `:99`), and the configuration example at commit `1329d682b4232c102600b5e7886df8ffdcaf9e26`
(`:80`). The pinned
documentation links that same protocol file three times — `probes.md:448`,
`configure-liveness-readiness-startup-probes.md:233`, and inside the description of `GRPCAction` at
`pod-v1.md:1455` — and all three name `master`. The post pinned what it cited; the current
documentation does not. One smaller mark of age: the post's four image references sit under
`/images/blog/2019-09-30-health-checking-grpc/`, a directory named for a date a year after
publication, and no other post in the corpus references it.

**What this exercise does not cover, and where it lives.** A pending row in the 2022 census carries
the beta announcement for this field, and with it the ladder for `GRPCContainerProbe` and the
before-and-after of one binary leaving one image. That is the graduation story and it is not
repeated here. This exercise starts where that one ends: from the field as it stands at the pin, and
what it will not do.

**The diff, and why** — none of the five cases fits, and the sixth one does. The post did not break
by being wrong: its diagnosis of the three mechanisms is intact, line by line, in the pin's own
descriptions of them. It is not *still right* in the way a hardening checklist is still right,
because its three instructions are obsolete — nobody should ship that binary now. It was not a plan
the project abandoned, and it has not been overtaken by stasis. It was **retired by being agreed
with**: the post argued that health checking a gRPC server should be standard rather than
per-application, and the project agreed so thoroughly that the tool became a field, the field went
stable, and the gate that carried it was removed. The other instance of this shape in the same year
is [the CSI beta exercise](02-container-storage-interface-beta.md), where the plan the post
announced was carried out.

What this post adds to that shape is that agreement is not absorption. Four things the post's tool
did that the field does not do, or does not yet do without a gate:

- the check ran **inside** the container, over `localhost`; the field runs from the node against the
  Pod IP, and a loopback-only server that passed then fails now;
- the tool was invoked with a command line, so the port could be whatever the author wrote; the
  field cannot take a port **name**;
- the tool could be pointed at a **host**; `GRPCAction` has no `host` field, and the note at
  `probes.md:465-468` says so explicitly;
- the tool spoke **TLS** in 2018; the field got a `mode: TLS` alpha at v1.37 that skips certificate
  verification, ten releases after the field itself went stable.

Against that, one thing came across and it is the thing the post was actually arguing for: nothing
has to be added to the image, and nobody has to write a health client. The trade is real in both
directions, which is why the exec route was never removed — it still works at this pin, and the only
thing the project did to it was add a `caution` recommending against the mechanism on CPU grounds.

**The ladder** — the gate that governs the field is not transcribed here, for the reason given
above. The two that this exercise turns on are the gate in the tool's last surviving mention, and
the gate for the capability that came back last.

`ExecProbeTimeout`

| stage | default | locked | releases |
|---|---|---|---|
| stable | `true` | — | v1.20 – |

One row is the whole history. There is no `alpha` row and no `beta` row, no `toVersion`, and no
`removed:` key, so at v1.37 the gate is still there and still settable. A gate with this shape does
not record a feature arriving; it records a fault being fixed and the fix being made optional for
the workloads that had come to rely on it.

`GRPCContainerProbeTLS`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.37 – |

Also one row, and no older than the pin itself. Its body names the exact shape of the addition:
"Enables TLS support for gRPC container probes. When enabled, you can add the `mode` field to the
`grpc` field in gRPC probes." Neither file declares `locked`, so both gates are settable in either
direction. `H2CContainerProbe` is the third gate in this neighbourhood and has the same shape — alpha,
`false`, from v1.37, no `toVersion` — and it is the one that answers the post's first objection from
the HTTP side rather than the gRPC side.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair). Steps 1 to 6 need no cluster, only the
pinned checkout. Steps 7 to 12 need one worker: the control plane carries the usual `NoSchedule`
taint, so every Pod here lands on `k8s-worker`, which matters for step 12 because that is the
kubelet whose configuration gets edited.

**Do**

1. Count the mechanisms, and measure how much each one can express. The first command is the
   sentence; the loop is the evidence:

   ```sh
   D=/path/to/pinned/website/content/en/docs
   sed -n '149,152p' "$D/concepts/workloads/pods/probes.md"
   for t in ExecAction GRPCAction HTTPGetAction TCPSocketAction; do
     printf '%-16s ' "$t"
     awk "/^## $t /,/<\/table>/" "$D/reference/kubernetes-api/core/pod-v1.md" \
       | grep -o '<td><code>[a-zA-Z]*</code>' | sed 's/.*<code>//;s|</code>||' | tr '\n' ' '
     echo
   done
   ```

2. Read what the pin says about the mechanism the post recommends, and about the one that replaced
   it. Both are opinions, stated in the documentation, about the same choice the post made:

   ```sh
   D=/path/to/pinned/website/content/en/docs
   sed -n '177,184p' "$D/concepts/workloads/pods/probes.md"
   sed -n '254,262p' "$D/tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md"
   sed -n '284,287p' "$D/tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md"
   ```

3. Find every surviving mention of the post's tool in the pinned tree, and then read the gate that
   the one mention is about:

   ```sh
   W=/path/to/pinned/website/content/en
   grep -rn 'grpc-health-probe\|grpc_health_probe' "$W/docs" | wc -l
   grep -rln 'grpc-health-probe\|grpc_health_probe' "$W/blog/_posts"
   cat "$W/docs/reference/command-line-tools-reference/feature-gates/ExecProbeTimeout.md"
   ```

4. Ask how unusual that gate's shape is. A gate whose first stage is `stable` was never rolled out;
   scan all 488 for the shape:

   ```sh
   G=/path/to/pinned/website/content/en/docs/reference/command-line-tools-reference/feature-gates
   ls "$G" | wc -l
   for f in "$G"/*.md; do
     s=$(grep -m1 '^  - stage:' "$f" | awk '{print $3}')
     [ "$s" = stable ] && echo "$(basename "$f" .md) stages=$(grep -c '^  - stage:' "$f") removed=$(grep -c '^removed: true' "$f")"
   done
   ```

5. Resolve the post's two documentation addresses, find out where the dead one still lives, and
   then follow the address the gate file in step 3 gave you:

   ```sh
   D=/path/to/pinned/website/content/en/docs
   T="$D/tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md"
   ls "$D/tasks/configure-pod-container/" | grep -i probe
   grep -rln 'configure-liveness-readiness-probes/' "$D"
   grep -c '^aliases' "$T"; true
   grep -c 'configure-probes' "$T"; true
   grep -rn '{#configure-probes}' "$D/concepts/workloads/pods/probes.md"
   ls "$D/reference/kubernetes-api/" | grep workload-resources; true
   grep -rl 'kubernetes-api/workload-resources' "$D" | wc -l
   ```

6. Compare how the post cites the gRPC health protocol with how the pinned documentation cites it:

   ```sh
   W=/path/to/pinned/website/content/en
   grep -o 'blob/v1.15.0' "$W/blog/_posts/2018/health-checking-grpc.md" | wc -l
   grep -rn 'doc/health-checking.md' "$W/docs" | grep -c 'blob/master'
   ```

7. Now the cluster. Apply the pin's own gRPC probe example, unedited, and look at what the Pod spec
   ended up holding:

   ```sh
   kubectl create ns probes
   kubectl -n probes apply -f /path/to/pinned/website/content/en/examples/pods/probe/grpc-liveness.yaml
   kubectl -n probes get pod etcd-with-grpc -o wide
   kubectl -n probes get pod etcd-with-grpc -o json \
     | python3 -c 'import sys,json; print(json.load(sys.stdin)["spec"]["containers"][0]["livenessProbe"])'
   kubectl -n probes get pod etcd-with-grpc -o jsonpath='{.spec.containers[0].image}{"\n"}'
   ```

8. Ask the running cluster the two questions the pin's own reference and prose disagree about: does
   the served schema carry `mode`, and can the port be named?

   ```sh
   kubectl explain pod.spec.containers.livenessProbe.grpc
   kubectl explain pod.spec.containers.livenessProbe.httpGet.port
   kubectl -n probes apply --dry-run=server -f - <<'EOF' 2>&1 | tail -3
   apiVersion: v1
   kind: Pod
   metadata:
     name: grpc-named-port
   spec:
     containers:
     - name: etcd
       image: registry.k8s.io/etcd:3.5.1-0
       ports:
       - name: client
         containerPort: 2379
       livenessProbe:
         grpc:
           port: client
   EOF
   ```

9. Try to give the probe TLS without the gate, and watch what the API server does with the field.
   Apply, then read back what was stored:

   ```sh
   kubectl -n probes apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: grpc-tls-attempt
   spec:
     containers:
     - name: etcd
       image: registry.k8s.io/etcd:3.5.1-0
       command: [ "/usr/local/bin/etcd", "--data-dir", "/var/lib/etcd",
                  "--listen-client-urls", "http://0.0.0.0:2379",
                  "--advertise-client-urls", "http://127.0.0.1:2379" ]
       livenessProbe:
         grpc:
           port: 2379
           mode: TLS
         initialDelaySeconds: 10
   EOF
   kubectl -n probes get pod grpc-tls-attempt -o json \
     | python3 -c 'import sys,json; print(json.load(sys.stdin)["spec"]["containers"][0]["livenessProbe"]["grpc"])'
   kubectl -n probes get pod grpc-tls-attempt -o yaml | grep -A4 'grpc:'
   ```

10. Move the server off the Pod IP and onto the loopback address, changing nothing else. This is the
    post's `localhost` made into an experiment. The watch does not end on its own; interrupt it once
    the restart count has moved twice:

    ```sh
    sed -e 's/name: etcd-with-grpc/name: etcd-loopback/' \
        -e 's|http://0.0.0.0:2379|http://127.0.0.1:2379|' \
        /path/to/pinned/website/content/en/examples/pods/probe/grpc-liveness.yaml \
      | kubectl -n probes apply -f -
    kubectl -n probes get pod etcd-loopback -w
    kubectl -n probes describe pod etcd-loopback | grep -A2 -i 'liveness\|restart' | head -20
    kubectl -n probes get pod etcd-loopback -o jsonpath='{.status.containerStatuses[0].restartCount}{"\n"}'
    ```

11. Now the gate in the footnote, on an exec probe of the kind the post asks you to configure. First
    with the gate at its default, which is on:

    ```sh
    kubectl -n probes run slow-exec --image=busybox --restart=Never -- sh -c 'sleep 3600'
    kubectl -n probes patch pod slow-exec --type merge -p '{"spec":{"containers":[{"name":"slow-exec","livenessProbe":{"exec":{"command":["sh","-c","sleep 5"]},"timeoutSeconds":1,"periodSeconds":5,"failureThreshold":1}}]}}' 2>&1 | tail -2
    ```

    A probe cannot be patched onto a running Pod, so create it with the probe in place instead:

    ```sh
    kubectl -n probes delete pod slow-exec --ignore-not-found
    kubectl -n probes apply -f - <<'EOF'
    apiVersion: v1
    kind: Pod
    metadata:
      name: slow-exec
    spec:
      containers:
      - name: app
        image: busybox
        command: ["sh", "-c", "sleep 3600"]
        livenessProbe:
          exec:
            command: ["sh", "-c", "sleep 5"]
          timeoutSeconds: 1
          periodSeconds: 5
          failureThreshold: 1
    EOF
    kubectl -n probes get pod slow-exec -w   # interrupt once the restart count moves
    kubectl -n probes get pod slow-exec -o jsonpath='{.status.containerStatuses[0].restartCount}{"\n"}'
    ```

12. Then switch the gate off on the worker's kubelet and create the same Pod again. The kubelet
    reads its configuration from a file on the host, which is the subject of
    [the dynamic kubelet configuration exercise](05-dynamic-kubelet-configuration.md); this is the
    plainest edit of it. The first command decides how to make the second one: if the file already
    has a `featureGates:` key, add the entry under it by hand instead of appending a second one,
    because two mappings with the same key is not a YAML document the kubelet will load. If your
    node sets `--config-dir`, put the entry in a drop-in file there instead.

    ```sh
    ssh zain@10.10.10.131 'grep -n featureGates /var/lib/kubelet/config.yaml'
    ssh zain@10.10.10.131 'sudo cp /var/lib/kubelet/config.yaml /var/lib/kubelet/config.yaml.bak
      printf "featureGates:\n  ExecProbeTimeout: false\n" | sudo tee -a /var/lib/kubelet/config.yaml >/dev/null
      sudo systemctl restart kubelet'
    kubectl get --raw "/api/v1/nodes/k8s-worker/proxy/configz" \
      | python3 -c 'import sys,json; print(json.load(sys.stdin)["kubeletconfig"].get("featureGates"))'
    kubectl -n probes delete pod slow-exec --ignore-not-found
    kubectl -n probes apply -f - <<'EOF'
    apiVersion: v1
    kind: Pod
    metadata:
      name: slow-exec
    spec:
      containers:
      - name: app
        image: busybox
        command: ["sh", "-c", "sleep 3600"]
        livenessProbe:
          exec:
            command: ["sh", "-c", "sleep 5"]
          timeoutSeconds: 1
          periodSeconds: 5
          failureThreshold: 1
    EOF
    sleep 60
    kubectl -n probes get pod slow-exec -o jsonpath='{.status.containerStatuses[0].restartCount}{"\n"}'
    ```

**Expect** — step 1: `probes.md` says four, and the loop prints `command` for `ExecAction`, `port
service` for `GRPCAction`, `host httpHeaders path port scheme` for `HTTPGetAction`, and `host port`
for `TCPSocketAction`. One, two, five, two. The mechanism the project chose as the answer to this
post is the second-poorest of the four in what it can be told, and the poorest is the one that
cannot be told anything because it runs the command you wrote.

Step 2: three opinions. The `caution` recommends against `exec` on the grounds that it forks
processes; the gRPC technical details begin by telling you to bind the Pod IP and end with the
`grpc-health-probe` footnote; and the named-port section says in one sentence that "gRPC probes do
not support named ports."

Step 3: `1` from the first command — one mention in the whole of `content/en/docs`. The second
prints two blog files, this post and the 2022 announcement. The gate file is sixteen lines, and its
body is an apology for a bug rather than a description of a feature.

Step 4: `488`, then four names — `ConsistentHTTPGetHandlers`, `ExecProbeTimeout`,
`ExternalPolicyForExternalIP`, `VolumeSubpath` — each with `stages=1`, and `removed=1` on all but
`ExecProbeTimeout`. Four in 488, three of them already gone, and the survivor is the one that
belongs to this post.

Step 5: the directory holds `configure-liveness-readiness-startup-probes.md` and nothing else that
matches; the dead address appears in exactly one file, `contribute/style/write-new-topic.md`; the
`aliases` count is `0`; the `configure-probes` count on the task page is also `0` while
`probes.md:209` defines it; `ls` prints nothing for `workload-resources`; and 23 files link into
that path anyway. Three separate addresses, three separate ways of being wrong: a page that moved
and left no forwarding entry, a fragment that lives on a different page from the one linked, and a
whole directory the pinned tree does not have. The style guide's is the one worth stopping on,
because a guide to writing task pages is the last place a rotted task-page link should survive.

Step 6: `4` and `3`. The post's citations name a tag and a commit; the documentation's name a branch.
Everything in the corpus this exercise belongs to — the pin, the manifest, the census — exists
because of the difference between those two numbers.

Step 7: the Pod goes `Running` and then stays `Running`, on `k8s-worker`. The stored probe prints as
`{'grpc': {'port': 2379}, 'initialDelaySeconds': 10}` — note what is not in it: no `command`, no
`service`, no `mode`, and no binary anywhere in the image, which is `registry.k8s.io/etcd:3.5.1-0`.
Whatever else has changed, this part of the post's argument was won.

Step 8: `kubectl explain` on the `grpc` field lists `port` and `service`; whether it also lists
`mode` depends on the gate, and this is the moment to record which answer your cluster gives,
because the pinned reference does not list it and the pinned prose does. The `httpGet.port` field
explains itself as accepting either a name or a number; record the type your `kubectl` prints for
it, because the same field is the one `grpc` does not have. The server-side dry run fails: the port
is declared as a named
port on the container, the `httpGet` and `tcpSocket` mechanisms would both accept that name, and
`grpc` rejects it before the Pod is ever scheduled. Read the message and note which field it names.

Step 9: the Pod is created and the field is gone. Reading back the `grpc` object gives
`{'port': 2379}` with no `mode`, and the YAML around `grpc:` shows the same, exactly as `:281-282`
says. No error, no warning, no event. A probe you asked to speak TLS is now a probe that speaks
plaintext, and the only way to find out is to look. Compare this with the rule shape that is
accepted and never matches in
[the admission webhook exercise](01-extensible-admission-is-beta.md): the same failure mode, one
release apart in publication and eight years apart in mechanism.

Step 10: the Pod starts, passes nothing, and restarts. `describe` shows `Liveness probe failed`, the
`restartCount` climbs, and the container is otherwise perfectly healthy — etcd is up and serving,
on an address the kubelet cannot reach, because the kubelet is not in the Pod. One flag value is the
difference between a server the post's tool would have called successfully over `localhost` and a
server the field it became declares dead.

Step 11: the patch is rejected — probes are not mutable on a running Pod — which is worth seeing
once, because it means the choice of mechanism is made at creation and never revised. The Pod
created with the probe in place restarts on a cycle: the exec command sleeps five seconds,
`timeoutSeconds` is one, `failureThreshold` is one, so every probe fails and `restartCount` climbs
by roughly one per period. This is the corrected behaviour, and it has been the default since v1.20.

Step 12: `configz` reports `ExecProbeTimeout` as `False` among the kubelet's feature gates, and the
same Pod now stays `Running` with `restartCount` at `0`. The kubelet no longer cuts the exec off at
one second; it waits for the
command to exit, the command exits `0` after five seconds, and the probe passes. Nothing about the
Pod changed. The fault the post's tool carried its own timeout flags to work around is one line in a
file on one node, and it is still shipped, seventeen releases after it was corrected.

**Read on**

- [The CSI beta exercise](02-container-storage-interface-beta.md) — the other post in this year that
  was retired by being agreed with, and the one to read next if the sixth diff case is the thing you
  came for.
- [The dynamic kubelet configuration exercise](05-dynamic-kubelet-configuration.md) — for the
  kubelet configuration file, the drop-in directory, and `configz`, all of which step 12 uses and
  none of which it explains.
- [The eleven ways exercise](06-11-ways-not-to-get-hacked.md) — for the same address rot at the scale
  of a whole checklist rather than two links.

**Teardown**

```sh
ssh zain@10.10.10.131 'sudo mv /var/lib/kubelet/config.yaml.bak /var/lib/kubelet/config.yaml
  sudo systemctl restart kubelet'
kubectl get --raw "/api/v1/nodes/k8s-worker/proxy/configz" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["kubeletconfig"].get("featureGates"))'
kubectl delete ns probes
```

Restore the kubelet first and check `configz` before deleting anything: a node left with
`ExecProbeTimeout: false` will quietly not time out an exec probe for every later exercise on this
cluster, and that is exactly the class of fault this one is about.
