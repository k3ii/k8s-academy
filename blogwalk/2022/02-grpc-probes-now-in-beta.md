<a id="grpc-probes-now-in-beta"></a>

# This post carries the only one of the archive's twenty editorial update notes that leaves its emphasis unclosed, it announces a beta whose gate was deleted five releases later on the commonest schedule a gate has, and one uncorrected sentence contradicts the transcript below it

**Post** — [Kubernetes 1.24: gRPC container probes in
beta](https://kubernetes.io/blog/2022/05/13/grpc-probes-now-in-beta/), 2022-05-13, Kubernetes v1.24.
211 lines, 8,344 bytes, one author and one vendor — a little above 2022's median post of 8,081
bytes, and the second of the year's thirteen walked posts.

**As written** — the post begins with a sentence its author did not write. `:10` is an editorial
note added by the project after publication:

> _Update: Since this article was posted, the feature was graduated to GA in v1.27 and doesn't
> require any feature gates to be enabled.

That is the whole line. The opening underscore is never closed and the paragraph ends at `:10`, so
the rendered page shows a literal `_` before the word *Update* — the only one of the archive's
twenty such notes where that happens, which step 8 measures.

Under it, `:12-14` is the claim: gRPC probes are beta and on by default, and you can health-check a
gRPC app *without exposing any HTTP endpoint, nor do you need an executable*. `:16-41` is the
history. Three probe mechanisms existed — exec, HTTP, TCP — and a gRPC app could repurpose the exec
one, which is what [the 2018 post this one supersedes](../2018/07-health-checking-grpc.md)
described. The post dates the tool that made that work to the day (created 2018-08-21, first release
2018-09-19), counts its adoption with two GitHub code searches, and closes the history at the v1.23
alpha.

`:43-64` argues the case and then undercuts it. The benefits are size — *you don't need to download
and carry `10MB` of an additional executable with your image* — and speed, because exec probes
*require instantiating a new process*. Then three limitations, stated plainly: client certificates
are not supported, server certificates are not checked, and the built-in probe can neither
distinguish error types nor chain several checks into one. The post waves them off: *all these
limitations are quite standard for gRPC and there are easy workarounds for those*.

`:66-97` is a setup section addressed to somebody else's cluster. It tells you to enable the
`GRPCContainerProbe` feature gate, notes that many vendors will have it on by default at 1.24, and
then prints a GKE command that creates a `1.23` cluster with `--enable-kubernetes-alpha`.

`:99-199` is the part that still runs. One Pod, the `agnhost` image, a `grpc-health-checking` server
on port 5000 and an HTTP control port on 8080, and a readiness probe with nothing in it but `port:
5000`. Then `curl /make-not-serving`, watch `Ready` go `False`, `curl /make-serving`, watch it come
back. The post prints its own output, including the event:

> ```
>   Warning  Unhealthy  2s (x6 over 42s)  kubelet            Readiness probe failed: service
>   unhealthy (responded with "NOT_SERVING")
> ```

**As it runs now** — the manifest works unchanged, which is not the same as the post being
unchanged.

**The gate the setup section tells you to enable does not exist.** `GRPCContainerProbe` carries
`removed: true`, its last release was v1.28, and the whole setup section at `:66-97` therefore has
no referent: no gate to enable, no vendor difference to work around, and no 1.23 alpha cluster to
create. The field is unconditional now, and the exercise below reaches it without configuring
anything.

**Six releases from first appearance to deletion is the single most common shape in the
population.** Of 487 gate files at the pin, 159 record all three stages and then a removal. Their
lifetimes run from four releases to twenty-five, and the mode is exactly six, with 23 gates there —
28 are shorter and 108 are longer. The three-release beta this post is announcing is shared by 42
gates. There is nothing unusual about this gate's arc; what is unusual is being able to read the
announcement of its beta and the record of its deletion side by side.

**The post carries two edits made by somebody who is not its author, and it is the only post in the
archive carrying both kinds.** One edit is the update note at `:10`. The other is a YAML comment
inside the manifest at `:119` — *image changed since publication (previously used registry
"k8s.gcr.io")* — one of three posts carrying that comment, and the only one that also carries an
update note. Between them the two edits are why step 2 can apply the post's manifest byte for byte
in 2026 and have it come up `Ready`.

**Two of the post's own commands never worked.** `:135` and `:187` say `kubectl describe test-grpc`,
with no resource type. `:165`, between them, says `kubectl describe pod test-grpc`. The first form
asks `kubectl` to describe a resource *kind* named `test-grpc`, and there is no such kind; the post
prints output underneath both of them that the command as written cannot have produced. Step 4 runs
all three.

**And one sentence contradicts the transcript directly below it.** `:162` says that after the
`make-not-serving` call, *in a few seconds the port status will switch to not ready*. The event the
post pastes eighteen lines later reads `2s (x6 over 42s)`: six consecutive probe failures spread
over forty-two seconds. The manifest sets no `periodSeconds` and no `failureThreshold`, so the
defaults apply — `probes.md:251` gives ten seconds, `:260` gives three failures — and a readiness
probe on those defaults needs up to thirty seconds to flip, not a few. The other direction really is
about a second, and for a reason `:251` states: while a container is not `Ready`, *the readiness
probe may be executed at times other than the configured `periodSeconds` interval. This is to make
the Pod ready faster.* One `successThreshold` against three failures, plus an off-schedule retry, is
the whole asymmetry. Steps 3 and 7 measure both directions.

**The three limitations were not workarounds waiting to happen; they are documented properties
now.** *There are no error codes for built-in probes. All errors are considered as probe failures*
is `configure-liveness-readiness-startup-probes.md:260`. A `mode: TLS` field arrived at v1.37 behind
`GRPCContainerProbeTLS`, and `:277-279` says the kubelet connects *with `InsecureSkipVerify` and
does not verify the server certificate*, then adds *Certificate verification is not supported.* The
post's second limitation survived thirteen releases and a new feature gate intact. Client
certificates have no field at the pin at all.

**What this exercise does not cover, and where it lives.** The field as it stands — that it takes
neither a port name nor a host, that it runs from the node rather than over `localhost` inside the
container, what the `service` field is for, what the API server does with `mode: TLS` when the gate
is off, and the `ExecProbeTimeout` gate in the pin's last surviving mention of the post's tool — is
[the exercise for the 2018 post](../2018/07-health-checking-grpc.md), which ceded this graduation
story in exchange. The consequence table for the three probe kinds, and what a failing readiness
probe does to an EndpointSlice, are [the probes lab](../../labs/01/09-probes-three-kinds.md). This
exercise is the announcement: the gate's arc, the post's own edits, and the two claims it makes
about cost that it never measures.

**The diff, and why** — four of the seven cases.

**Retired by being agreed with: the gate.** The post ends by asking for feedback *before the feature
will be promoted to GA*. It got three releases of beta, went stable at v1.27, and the switch was
deleted after v1.28. The 2018 exercise argues this case about the *tool* — a binary the project
turned into a field. Here it is about the switch: a feature announced as needing configuration,
agreed with so completely that the configuration was taken away. The two are the same case at
different scales, and the second one is the more ordinary, which is the finding.

**Broke: the cluster-level setup.** Every instruction in `:66-97` fails now, and each fails for its
own reason. The gate name is not a gate. `--enable-kubernetes-alpha` creates a cluster nobody would
run a probe experiment on. `--cluster-version=1.23` names a release fourteen behind the pin's
newest. The post even anticipated this — *especially if you are reading this blog post long after
the Kubernetes 1.24 release* — and hedged in the wrong direction, expecting vendors to catch up
rather than the gate to vanish.

**Wrong when it was published: two commands and one sentence.** `kubectl describe test-grpc` is not
a typo that time fixed or broke; it was wrong on 2022-05-13 and the output printed below it was
produced by a different command. *In a few seconds* was wrong against the post's own pasted event on
the same day. Both survived the two later edits, which is the part worth noticing: somebody went
into this file twice to keep it correct, and changed the registry and added a GA note while walking
past a command that cannot run.

**Still right: the three limitations.** The post lists them as temporary annoyances with easy
workarounds. Thirteen releases later all three hold, two of them are written into the documentation
as properties rather than gaps, and the one that got a feature gate got TLS transport without
certificate verification — which is the limitation the post named, unchanged, with a new field in
front of it.

Not the seventh case, and not close. Nothing under `content/en` cites this post at all: the only
occurrence of the string `grpc-probes-now-in-beta` in the whole tree is the post's own `slug:` line.
Its 2018 predecessor is cited by name from inside this very post; this one is cited by nothing. The
first test fails before the identifier test is worth running.

**The ladder**

One gate, transcribed from its `stages:` list parsed as YAML. The three gates in the same
neighbourhood — `ExecProbeTimeout`, `GRPCContainerProbeTLS` and `H2CContainerProbe` — are laddered
in the 2018 exercise and are referred to here, not reprinted.

```
GRPCContainerProbe  alpha  false  1.23 - 1.23
                    beta   true   1.24 - 1.26   <- this post
                    stable true   1.27 - 1.28
                                                removed
```

The alpha lasted one release, which is the ordinary length: 151 of the 401 gates with an alpha stage
have a one-release alpha. The beta lasted three, shared with 41 other gates. The stable stage lasted
two before the gate was deleted, shared with 84 others. Every segment of this ladder is the common
case, and the post is written as though the reader is present at something rare. What the
transcription is good for is the arithmetic in the other direction: the post is dated inside the
`1.24` row, and the row below it ends.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`, 4096MB, 4
vCPU, 25G. Reuse the guest from [the volume expansion exercise](01-volume-expansion-ga.md) if it is
still up, or bring one up with [the provisioning
sequence](../../strands/lab-topologies.md#provision). Everything here is one node's kubelet and four
Pods; there is no reason for a second node and a second kubelet would only split the probe metrics
in step 6 across two endpoints.

**Do**

1. Ask both components which of the four gates in this neighbourhood they still know about. The gate
   this post is announcing should be absent from both, and the two that answer the post's
   limitations should be present on exactly one:

   ```sh
   kubectl version -o json | python3 -c 'import json,sys
   print("server:", json.load(sys.stdin)["serverVersion"]["gitVersion"])'
   NODE=$(kubectl get node -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw /metrics > /tmp/apiserver.txt
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/metrics" > /tmp/kubelet.txt
   for G in GRPCContainerProbe GRPCContainerProbeTLS H2CContainerProbe ExecProbeTimeout; do
     printf '%-22s apiserver=%s kubelet=%s\n' "$G" \
       "$(grep -c "kubernetes_feature_enabled.*\"$G\"" /tmp/apiserver.txt || true)" \
       "$(grep -c "kubernetes_feature_enabled.*\"$G\"" /tmp/kubelet.txt || true)"
   done
   grep -c 'kubernetes_feature_enabled' /tmp/apiserver.txt /tmp/kubelet.txt
   ```

2. Apply the post's manifest byte for byte, comment and all, and then read back what the API server
   wrote into the probe that the post never typed:

   ```sh
   kubectl apply -f - <<'YAML'
   ---
   apiVersion: v1
   kind: Pod
   metadata:
     name: test-grpc
   spec:
     containers:
     - name: agnhost
       # image changed since publication (previously used registry "k8s.gcr.io")
       image: registry.k8s.io/e2e-test-images/agnhost:2.35
       command: ["/agnhost", "grpc-health-checking"]
       ports:
       - containerPort: 5000
       - containerPort: 8080
       readinessProbe:
         grpc:
           port: 5000
   YAML
   kubectl wait --for=condition=Ready pod/test-grpc --timeout=180s
   kubectl get pod test-grpc -o jsonpath='{.spec.containers[0].readinessProbe}' \
     | python3 -m json.tool
   ```

3. Run the post's demonstration with a clock on it. Both directions, timestamped, against the
   defaults the post left in place:

   ```sh
   kubectl port-forward test-grpc 8080:8080 >/tmp/pf.log 2>&1 &
   sleep 4
   R() { kubectl get pod test-grpc \
     -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}'; }
   echo "$(date +%T) not-serving -> $(curl -s http://localhost:8080/make-not-serving)"
   for i in $(seq 1 12); do printf '%s %s\n' "$(date +%T)" "$(R)"; sleep 4; done
   echo "$(date +%T) serving -> $(curl -s http://localhost:8080/make-serving)"
   for i in $(seq 1 10); do printf '%s %s\n' "$(date +%T)" "$(R)"; sleep 1; done
   kubectl describe pod test-grpc | sed -n '/Events:/,$p'
   ```

4. Run the post's own three command lines, in the order it prints them. Two of them are the same
   mistake and the one between them is correct:

   ```sh
   kubectl describe test-grpc 2>&1 | head -3
   kubectl describe pod test-grpc 2>&1 | head -3
   kubectl api-resources --no-headers -o name | grep -x 'test-grpc' || \
     echo "no resource type named test-grpc"
   ```

5. Weigh the post's first argument. It asks you not to carry ten megabytes of extra binary; put that
   number against the image the post itself chose:

   ```sh
   sudo crictl images | grep -i agnhost
   sudo crictl inspecti registry.k8s.io/e2e-test-images/agnhost:2.35 \
     | python3 -c 'import json,sys
   d = json.load(sys.stdin)["status"]
   b = int(d["size"])
   print("agnhost:2.35 bytes:", b, "| MB:", round(b/1e6, 1))
   print("10MB as a share of it:", str(round(1000/(b/1e6), 1)) + "%")'
   ```

6. Weigh the second argument, which the post states as a mechanism and never measures. Two Pods
   probed at the same interval — one gRPC call, one exec of the cheapest command a container can run
   — and the kubelet's own histogram for the answer:

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata: { name: bw-grpc }
   spec:
     containers:
     - name: agnhost
       image: registry.k8s.io/e2e-test-images/agnhost:2.35
       command: ["/agnhost", "grpc-health-checking"]
       ports: [{ containerPort: 5000 }, { containerPort: 8080 }]
       readinessProbe:
         grpc: { port: 5000 }
         periodSeconds: 2
         failureThreshold: 1
   ---
   apiVersion: v1
   kind: Pod
   metadata: { name: bw-exec }
   spec:
     containers:
     - name: busybox
       image: busybox:1.36
       command: ["sleep", "3600"]
       readinessProbe:
         exec: { command: ["/bin/true"] }
         periodSeconds: 2
         failureThreshold: 1
   YAML
   kubectl wait --for=condition=Ready pod/bw-grpc pod/bw-exec --timeout=180s
   sleep 120
   NODE=$(kubectl get node -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/metrics/probes" \
     | grep 'prober_probe_duration_seconds_sum\|prober_probe_duration_seconds_count' \
     | grep 'bw-grpc\|bw-exec'
   ```

7. Now take the defaults away and re-run step 3's transition against `bw-grpc`, whose probe fires
   every two seconds and gives up after one failure. The same two curls, the same clock:

   ```sh
   kubectl port-forward bw-grpc 8081:8080 >/tmp/pf2.log 2>&1 &
   sleep 4
   R2() { kubectl get pod bw-grpc \
     -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}'; }
   echo "$(date +%T) not-serving -> $(curl -s http://localhost:8081/make-not-serving)"
   for i in $(seq 1 8); do printf '%s %s\n' "$(date +%T)" "$(R2)"; sleep 1; done
   echo "$(date +%T) serving -> $(curl -s http://localhost:8081/make-serving)"
   for i in $(seq 1 8); do printf '%s %s\n' "$(date +%T)" "$(R2)"; sleep 1; done
   kubectl get --raw "/api/v1/nodes/$(kubectl get node \
     -o jsonpath='{.items[0].metadata.name}')/proxy/metrics/probes" \
     | grep 'prober_probe_total' | grep 'bw-grpc'
   ```

8. Offline now, in the pinned checkout. Count the editorial notes the project has added to other
   people's posts, and find the one that was added without being finished:

   ```sh
   cd /path/to/kubernetes/website
   python3 - <<'PY'
   import os, re
   B = "content/en/blog/_posts"
   total, odd = 0, []
   for root, _, fs in os.walk(B):
       for fn in sorted(fs):
           if not fn.endswith(".md"): continue
           path = os.path.join(root, fn)
           lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
           for i, line in enumerate(lines):
               if not re.match(r'^[_*]{0,3}Update', line): continue
               j, block = i, []
               while j < len(lines) and lines[j].strip() != "":
                   block.append(lines[j]); j += 1
               total += 1
               if "\n".join(block).count("_") % 2 == 1:
                   odd.append((path.split("_posts/")[1], i + 1))
   print("update blocks:", total)
   print("with unbalanced emphasis:", odd)
   PY
   grep -rl 'image changed since publication' content/en/blog/_posts --include='*.md'
   ```

9. Census the vocabulary, and find out how much of this post the documentation kept. Three of these
   four strings should be absent from `content/en/docs` entirely:

   ```sh
   cd /path/to/kubernetes/website
   for S in grpc_health_probe grpc-health-probe agnhost:2.35 grpc-probes-now-in-beta; do
     printf '%-26s docs=%s blog=%s\n' "$S" \
       "$(grep -rl "$S" content/en/docs --include='*.md' | wc -l | tr -d ' ')" \
       "$(grep -rl "$S" content/en/blog --include='*.md' | wc -l | tr -d ' ')"
   done
   grep -rn 'grpc-probes-now-in-beta' content/en --include='*.md'
   grep -rn 'GRPCContainerProbe' content/en/docs --include='*.md' | grep -vc 'GRPCContainerProbeTLS'
   grep -rn 'no error codes' \
     content/en/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md
   grep -rn 'Certificate verification is not supported' content/en/docs --include='*.md'
   ```

10. Finally, measure the shape of the ladder against the whole population — how long a gate that
    went all the way and then vanished usually lasts, and where six releases sits in that
    distribution:

    ```sh
    cd /path/to/kubernetes/website
    python3 - <<'PY'
    import os, yaml, collections
    G = "content/en/docs/reference/command-line-tools-reference/feature-gates"
    gates = {}
    for fn in sorted(os.listdir(G)):
        if not fn.endswith(".md") or fn == "index.md": continue
        gates[fn[:-3]] = yaml.safe_load(open(os.path.join(G, fn)).read().split("---")[1])
    print("gate files:", len(gates))
    def minor(v): return int(str(v).split(".")[1])
    def stage(v, want):
        for s in v.get("stages") or []:
            if str(s.get("stage")).strip() == want: return s
    lives = {}
    for k, v in gates.items():
        if not v.get("removed"): continue
        a, b, s = stage(v, "alpha"), stage(v, "beta"), stage(v, "stable")
        if a and b and s:
            lives[k] = minor(s["toVersion"]) - minor(a["fromVersion"]) + 1
    counts = collections.Counter(lives.values())
    print("removed gates with all three stages:", len(lives))
    print("lifetime distribution:", sorted(counts.items()))
    mine = lives["GRPCContainerProbe"]
    print("GRPCContainerProbe lifetime:", mine, "| mode:", counts.most_common(1))
    print("shorter:", sum(n for k, n in counts.items() if k < mine),
          "| same:", counts[mine],
          "| longer:", sum(n for k, n in counts.items() if k > mine))
    PY
    ```

**Expect**

Step 1 finds `GRPCContainerProbe` on neither component, `ExecProbeTimeout` on the kubelet, and
`GRPCContainerProbeTLS` and `H2CContainerProbe` on both — the two that arrived at the pin's own
release, answering two of the post's three limitations four years late. The total gate count differs
between the two files, which is the useful part: a gate is only known to the binaries that read it,
so *the* list of feature gates is not a thing a cluster has.

Step 2 comes up `Ready`. The image tag the post names is four years and dozens of releases old and
still pulls, which is the whole of what the project's second edit bought. The read-back shows the
fields the post never wrote: `periodSeconds` 10, `failureThreshold` 3, `successThreshold` 1,
`timeoutSeconds` 1. Those four numbers are the subject of steps 3 and 7.

Step 3 is the post's demonstration with the post's own claim falsified by the clock. `Ready` should
stay `True` for roughly twenty to thirty seconds after the `make-not-serving` call and then go
`False`; the event should read `(x3 over` something in the twenties, because the probe has to fail
three times ten seconds apart. The return trip should take a second or two. Record both numbers. *A
few seconds* describes the second one and the post attaches it to the first.

Step 4 gives two errors and one description. `kubectl describe test-grpc` should report that the
server has no resource type by that name — the argument is read as a kind, not a name — and the
third command confirms there is no such kind. This is what the post printed output under, twice.

Step 5 should put `agnhost:2.35` somewhere in the tens of megabytes. Whatever the number, do the
division: the ten megabytes the post asks you not to carry are a large fraction of a small image and
a rounding error on a large one, and the post makes the argument without naming an image size. The
argument is not wrong; it is unquantified, and the post had the number in front of it.

Step 6 is the one the post asserts and never tests. Divide `_sum` by `_count` for each `probe_type`
and compare. `/bin/true` in a `busybox` container is the cheapest exec probe that can exist — no
interpreter, no work — so if the gRPC round trip is faster than that, the post's mechanism claim
holds at its hardest setting. If it is not faster, the post's claim is true about *typical* exec
probes and false about the floor, and either result is worth writing down. Expect the exec histogram
to be dominated by container-runtime overhead rather than by the command.

Step 7 should flip `Ready` to `False` within about two seconds and back within about two, because
`failureThreshold` is 1 in both directions now. Set that against step 3: same image, same probe,
same protocol, and a transition time that differs by an order of magnitude because of two fields the
post's manifest omits. `prober_probe_total` should show both `failure` and `success` results
accumulating at the two-second cadence.

Step 8 should report twenty update blocks across the archive and exactly one with unbalanced
emphasis, at `2022/grpc-probes-in-beta.md:10`. Three posts carry the registry comment; this is the
only one in both lists. The project has an editorial voice that edits old posts, it has used it
twenty times, and the one time it left a mark on the page is on the post that announces a feature
gate that no longer exists.

Step 9 separates two spellings. `grpc_health_probe`, the binary's own name and the one this post
uses four times, is docs=0 blog=2 — both of them blog posts, this one and its predecessor. The
hyphenated `grpc-health-probe` is docs=1, and that one file is the pin's last mention of the tool.
`agnhost:2.35` is docs=0 blog=1: this post is the only place in the tree that names that tag.
`grpc-probes-now-in-beta` occurs once in `content/en`, in the post's own front matter, so nothing
cites it. And the exact string `GRPCContainerProbe`, discounting the `TLS` gate that contains it,
occurs once in the whole documentation tree — as the `title:` of its own removed, unrendered gate
file.

Step 10 should report 487 gate files, 159 that ran alpha to beta to stable and were then removed,
and a lifetime distribution whose mode is six releases with 23 gates — 28 shorter, 108 longer.
`GRPCContainerProbe` is one of the 23. The announcement in the post is the announcement of the
median case.

**Read on**

1. [The binary that became a field](../2018/07-health-checking-grpc.md) — the post this one
   supersedes, and the exercise that owns the field's limits. Read it after this one: this is the
   graduation, that is the audit of what graduated.

2. [Three probes, three different consequences](../../labs/01/09-probes-three-kinds.md) — the
   consequence table steps 3 and 7 assume, built on HTTP probes, with the readiness failure that
   leaves a Pod `Running` and serving nothing.

3. [The containerd post with the banner it did not
   write](../2017/08-containerd-container-runtime-options-kubernetes.md) — the other exercise that
   turns on an editorial note added years after publication. That banner closes its emphasis and
   spans three lines; this one does neither, and the contrast is what makes step 8 worth running.

4. `configure-liveness-readiness-startup-probes.md:254-282` in the pinned tree — the technical
   details list and the TLS section, which is where the post's three limitations ended up once they
   stopped being limitations and became documentation.

5. Unanswerable from the pin: the post's two adoption figures, *3,626 Dockerfiles* and *6,621 yaml*
   files naming `grpc_health_probe` on GitHub in May 2022. They are the post's entire argument for
   why the feature was needed, they are measurements of the world rather than of Kubernetes, and
   both links are GitHub code searches whose results are not archived. The checkout can tell you
   that the tool survives in exactly one documentation page; it cannot tell you whether those
   numbers went up or down after the field arrived.

**Teardown**

```sh
kill %1 %2 2>/dev/null || true
kubectl delete pod test-grpc bw-grpc bw-exec --ignore-not-found
rm -f /tmp/apiserver.txt /tmp/kubelet.txt /tmp/pf.log /tmp/pf2.log
kubectl get pods
```

Kill the port-forwards before deleting the Pods or the two background jobs will sit there
reconnecting. Nothing here touched a manifest, a kubelet configuration or a feature gate, so the
guest is exactly as step 1 found it; leave it up if you are going straight on, or [destroy
it](../../strands/lab-topologies.md#teardown).
