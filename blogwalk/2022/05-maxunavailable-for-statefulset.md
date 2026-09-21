<a id="maxunavailable-for-statefulset"></a>

# The default for this post's gate went on at 1.35.0, off at 1.35.4 and on again at 1.37, so whether the field the post tells you to enable works at all is a question about your patch number, and the generated half of the reference still reports it off, along with thirty-five other gates

**Post** — [Kubernetes 1.24: Maximum Unavailable Replicas for
StatefulSet](https://kubernetes.io/blog/2022/05/27/maxunavailable-for-statefulset/),
2022-05-27.

149 lines, 8,883 bytes, one author from one vendor — Mayank Kumar, Salesforce — against a 2022
median of 8,081 bytes, so an ordinary post by every measure the manifest records. It is the fifth of
the year's thirteen walked posts and the fifth 1.24 announcement in a row: every walked post of 2022
so far has been about a gate or a graduation in the same release.

**As written**

The argument is short and good. A StatefulSet with `podManagementPolicy: OrderedReady` updates one
Pod at a time, and the post gives two cases where that is too slow: a cache-backed application whose
containers need a long time to warm, and a leader-plus-followers application whose followers can all
go down at once. Both want a batch size larger than one, and neither wants to give up per-Pod
identity, which is the only reason they are StatefulSets at all.

Then the instruction, at `:31-33`:

> In order to support such scenarios, Kubernetes 1.24 includes a new alpha feature to help. Before
> you can use the new feature you must enable the `MaxUnavailableStatefulSet` feature flag. Once you
> enable that, you can specify a new field called `maxUnavailable`, part of the `spec` for a
> StatefulSet.

The manifest that follows sets `replicas: 5`, `maxUnavailable: 2`, `partition: 0`, and carries an
inline comment on the pod management policy — `podManagementPolicy: OrderedReady # you must set
OrderedReady` (`:42`). The demonstration changes the image and prints forty lines of `kubectl get
pods --watch`, annotated in the right margin: 4 and 3 terminate together, then 2 and 1 only after
both 4 and 3 are running, then 0 alone. The narration at `:117-127` states the guarantee precisely —
ordering holds *between* batches and not inside one, so replica 3 may become ready before replica 4,
and an application that cannot survive that must not set the field above 1.

The post closes by admitting two things it has not covered (`:137-139`):

> So, now you may have a lot of questions about:-
> - What is the behavior when you set `podManagementPolicy: Parallel`?
> - What is the behavior when `partition` to a value other than `0`?

It has in fact half-answered the first, four lines earlier at `:133-135`: under `Parallel` the
terminations and the creations both happen `maxUnavailable` at a time, *"This is called bursting."*
Then it asks for bug reports, and links the documentation section, the KEP, the implementation pull
request and the tracking issue.

**As it runs now**

The feature exists, the field is beta, and the one sentence in it you cannot check without looking
at your own cluster is *"you must enable the `MaxUnavailableStatefulSet` feature flag"*. Its truth
has changed four times, and one of those changes landed inside a release rather than between two:
alpha and off from 1.24 through 1.34, beta and on from 1.35.0, beta and **off again** from 1.35.4
through 1.36, beta and on once more at 1.37. Two of those four boundaries are patch numbers. This
repo's lab clusters run v1.35, which means the post's instruction is correct on some of them and
wrong on others, decided by a number that most people never read off `kubectl version`.

The documentation the post links still lands. `### Maximum unavailable Pods` sits at
`statefulset.md:357`, so the `#maximum-unavailable-pods` fragment at `:146` resolves, and the
section underneath carries the post's arithmetic almost unchanged — percentage rounded up, the field
cannot be 0, the default is 1. It also carries a hand-written stamp, `{{< feature-state
for_k8s_version="v1.35" state="beta" >}}` (`:359`), and a note (`:372`): *"The `maxUnavailable`
field is in Beta stage and it is enabled by default."* Neither names the releases in which that was
false.

And the reference disagrees with itself. The feature-gate page for this gate is hand-maintained YAML
and says beta, default `true`, from v1.37. The component pages — `kube-apiserver.md`,
`kube-controller-manager.md` and `kube-scheduler.md`, all three carrying `auto_generated: true` and
built from the components' own Go source — print `kube:MaxUnavailableStatefulSet=true|false (BETA -
default=false)`. That is not a typo and it is not specific to this gate: the generated pages at this
pin were built from v1.36 binaries.

**What this exercise does not cover, and where it lives**

The gate's own four-row ladder is printed, with four sibling StatefulSet and DaemonSet gates, in
[The two sentences this post is most emphatic
about](../2017/04-kubernetes-statefulsets-daemonsets.md), which also shows that the `{{<
feature-state >}}` stamp above the section is written by hand rather than driven by the gate name,
and that the `partition` rules contradict each other once `.spec.ordinals.start` is non-zero. This
exercise does not repeat any of that. It takes the other cut: why the default moved, how far the two
halves of the reference have drifted apart, and what the rollback looks like on a running cluster.

The arithmetic of `maxSurge` and `maxUnavailable` on a Deployment — how many Pods exist at each
step, and why a rollout with `maxSurge: 0` stalls — belongs to [Rolling update
predictions](../../labs/01/08-rolling-update-predictions.md) and to [the Deployment objects
post](../2016/04-using-deployment-objects-with.md). StatefulSet identity, ordinals and claim
retention belong to [the StatefulSet
announcement](../2016/14-statefulset-run-scale-stateful-applications-in-kubernetes.md) and to [the
PVC auto-deletion post](../2021/11-statefulset-pvc-auto-deletion.md). Nothing here re-derives them.

**The diff, and why**

**Broke, and then unbroke, and then broke again.** *"Before you can use the new feature you must
enable the `MaxUnavailableStatefulSet` feature flag"* is not stale. It is intermittently correct.
Run it against a cluster and the answer depends on the minor release and, for one minor release, on
the patch: true for 1.24–1.34, false for 1.35.0–1.35.3, true again for 1.35.4–1.36, false at 1.37. A
reader who checks it once and writes the answer down has recorded a fact with an expiry date and no
way to tell when it expired. The usual repair for a stale instruction — read it, note the version it
stopped being true, move on — does not work here, because it never stopped being true; it
alternates.

**Wrong when it was published, by four lines.** The manifest comment at `:42` says
`podManagementPolicy: OrderedReady # you must set OrderedReady`. The post's own body at `:133-135`
describes what happens when you set `Parallel` instead, and gives the behaviour a name. Both cannot
be right, and it is the comment that is wrong: `maxUnavailable` has always applied under both
policies. The documentation now says so in a sentence the post could have written itself
(`statefulset.md:305-307`), and uses the post's word: *"the StatefulSet controller terminates and
creates up to `maxUnavailable` Pods simultaneously (also known as \"bursting\")"*.

**Still right, in the part that took the most work.** Everything the post says about semantics
survives: the batch boundary, the guarantee that batch *n+1* waits for batch *n*, the explicit
warning that replica 3 may become ready before replica 4 and that this is the application's problem,
the percentage rounding up, the default of 1, and the observation that Kubernetes calls them
replicas while the operator does not. Four years on, `statefulset.md:361-373` says the same things
in fewer words. The post is a correct description of a mechanism whose configuration story went
sideways.

**Retired by being agreed with, in one of its two open questions.** *"What is the behavior when you
set `podManagementPolicy: Parallel`?"* is now a documented paragraph under `#### Parallel Pod
Management`, cross-linked to the `maxUnavailable` section, with the post's own coinage in it. The
second question — `partition` set to something other than `0` — has no such paragraph, and where the
documentation does discuss `partition` it contradicts itself. One question was answered by being
absorbed. The other is still open, four years and thirteen releases later, and the post is still
where it is put most plainly.

**The ladder**

The gate's own stages are [laddered next door](../2017/04-kubernetes-statefulsets-daemonsets.md) and
are not reprinted here. What belongs here is the population those stages sit in, because every
number is small enough to check and each one says something different about how rare this post's
gate is.

Of the 487 feature-gate files at the pin, exactly two record a stage boundary at a patch release
rather than a minor: this post's gate, and `DisableNodeKubeProxyVersion`, which went beta at 1.31.0
and deprecated at 1.31.1 — one patch later, which reads as a mistake caught immediately. Ten gates
have a `defaultValue` that goes from `true` back to `false` at some point, and five of those ten do
it without changing stage. Two of the five are already deprecated when it happens, so the flip is
part of switching something off for good. The other three are in beta, where a default going
backwards means the project shipped an on-by-default feature and then took it back:
`MaxUnavailableStatefulSet`, `SchedulerQueueingHints` and `WatchList` — and all three were later
turned back on. And 401 gates have an alpha stage at all; 23 of those spent eleven or more releases
on it, and four spent exactly eleven, this one among them.

The drift between the two halves of the reference is the number worth writing down. The component
pages list 150 gates in their `--feature-gates` help text; 136 of those have a hand-maintained gate
file to compare against. Thirty-six of the 136 disagree with that file about stage or default at
v1.37. Five disagree at v1.36. The generated pages were built one minor release before the gate
files were updated, and nothing on either page says so:

```
gate                          gate file, at v1.37    binaries, as generated
MaxUnavailableStatefulSet     beta    true           BETA    default=false
MemoryQoS                     beta    true           ALPHA   default=false
HPAScaleToZero                beta    true           ALPHA   default=false
SELinuxMount                  stable  true           BETA    default=false
PodCertificateRequest         stable  true           BETA    default=false
DRAExtendedResource           stable  true           BETA    default=true
                              ... 30 more at v1.37, 5 at v1.36
```

For thirty-five of those thirty-six the drift is the ordinary lag of a generated artifact. For this
one it is worse, because the thing the generated page is a release behind on is precisely the flag
flip: `default=false` was the answer for 1.35.4 through 1.36 and is the answer the binaries' help
text still gives. A reader who checks the component reference gets the correct answer for the wrong
release, and has no way to tell from the page which release it is.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`, 4096MB, 4 cores, 25G.
Five Pods on one kubelet, so the only variable in the timing is the controller's batching — a second
node would add image-pull and scheduling skew to a measurement that is entirely about when the
controller decides to delete. The single node is also the control plane, which this exercise needs,
because step 3 may have to turn the gate on the way the post says: by editing two static Pod
manifests. Bring it up with [the strand's provisioning
run](../../strands/lab-topologies.md#provision) if it is not already there.

**Do**

1. Find out which row of the ladder this cluster is standing on, before touching anything. The patch
   number matters here and almost nowhere else, so read it explicitly rather than trusting the
   minor:

   ```sh
   kubectl version -o json | python3 -c 'import json, sys
   v = json.load(sys.stdin)["serverVersion"]
   mi = int(v["minor"].rstrip("+"))
   pa = int(v["gitVersion"].lstrip("v").split(".")[2].split("-")[0])
   if mi <= 34:                     row = "alpha, default false - you must enable it"
   elif mi == 35 and pa <= 3:       row = "beta, default TRUE - already on"
   elif mi == 35 or mi == 36:       row = "beta, default FALSE - you must enable it"
   else:                            row = "beta, default TRUE - already on"
   print("server   ", v["gitVersion"])
   print("ladder   ", row)'
   kubectl get node -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints
   ssh zain@10.10.10.180 "sudo grep -n feature-gates \
     /etc/kubernetes/manifests/kube-apiserver.yaml \
     /etc/kubernetes/manifests/kube-controller-manager.yaml || echo 'no --feature-gates set'"
   ```

2. Ask the API server what it thinks, and ask the schema whether the field is there at all. The
   first tells you what was compiled in; the second tells you nothing about the gate, which is the
   point:

   ```sh
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' \
     | grep -i 'maxunavailable\|watchlist\|queueinghints' || echo "no matching gate reported"
   kubectl explain statefulset.spec.updateStrategy.rollingUpdate.maxUnavailable
   ```

3. Now the only test that settles it: write the field and read it back. An API server with the gate
   off drops the field silently on the way in. If it comes back missing, enable the gate on both
   components the post's instruction implies — the API server that stores the field and the
   controller manager that acts on it — and wait for the static Pods to restart:

   ```sh
   kubectl create ns sts
   kubectl -n sts apply -f - <<'YAML'
   apiVersion: apps/v1
   kind: StatefulSet
   metadata:
     name: web
   spec:
     serviceName: web
     podManagementPolicy: OrderedReady
     replicas: 5
     selector:
       matchLabels: {app: web}
     template:
       metadata:
         labels: {app: web}
       spec:
         terminationGracePeriodSeconds: 1
         containers:
         - name: a
           image: registry.k8s.io/e2e-test-images/agnhost:2.53
           args: ["netexec", "--http-port=8080"]
           readinessProbe:
             tcpSocket: {port: 8080}
             periodSeconds: 1
     updateStrategy:
       type: RollingUpdate
       rollingUpdate:
         maxUnavailable: 2
         partition: 0
   YAML
   kubectl -n sts get sts web -o jsonpath='{.spec.updateStrategy.rollingUpdate}{"\n"}'
   ```

4. If and only if step 3 came back without `maxUnavailable`, do what the post tells you to do. Keep
   the backups; the teardown needs them:

   ```sh
   ssh zain@10.10.10.180 'set -e
   cd /etc/kubernetes/manifests
   sudo cp kube-apiserver.yaml kube-controller-manager.yaml /root/
   sudo sed -i "/- kube-apiserver/a\\    - --feature-gates=MaxUnavailableStatefulSet=true" kube-apiserver.yaml
   sudo sed -i "/- kube-controller-manager/a\\    - --feature-gates=MaxUnavailableStatefulSet=true" kube-controller-manager.yaml'
   sleep 45
   kubectl -n sts patch sts web --type=merge \
     -p '{"spec":{"updateStrategy":{"rollingUpdate":{"maxUnavailable":2}}}}'
   kubectl -n sts get sts web -o jsonpath='{.spec.updateStrategy.rollingUpdate}{"\n"}'
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' | grep -i maxunavailable
   ```

5. Reproduce the post's own demonstration, but measure it instead of reading it. The watch output in
   the post is forty lines of interleaved events; what you actually want is how many Pods are
   terminating at once, sampled once a second and collapsed:

   ```sh
   cat > /tmp/roll.py <<'PY'
   import json, subprocess, sys, time
   ns = sys.argv[1]
   for _ in range(int(sys.argv[2])):
       ps = json.loads(subprocess.check_output(
           ["kubectl", "-n", ns, "get", "pod", "-o", "json"]))["items"]
       term = sorted(p["metadata"]["name"] for p in ps
                     if p["metadata"].get("deletionTimestamp"))
       ready = [p for p in ps
                if any(c.get("ready") for c in p["status"].get("containerStatuses", []))]
       print("pods %2d  terminating %-22s ready %d"
             % (len(ps), ",".join(term) or "-", len(ready)))
       time.sleep(1)
   PY
   kubectl -n sts rollout status sts/web --timeout=180s
   kubectl -n sts set env sts/web ROLL=2
   python3 /tmp/roll.py sts 120 | uniq -c
   ```

6. Answer the post's first open question with the cluster rather than the documentation.
   `podManagementPolicy` cannot be patched on a live StatefulSet, so this needs a second one, in a
   namespace of its own so the sampler sees only it. Watch the creations as well as the deletions —
   that is what makes it bursting:

   ```sh
   kubectl create ns burst
   kubectl -n burst apply -f - <<'YAML'
   apiVersion: apps/v1
   kind: StatefulSet
   metadata:
     name: burst
   spec:
     serviceName: burst
     podManagementPolicy: Parallel
     replicas: 5
     selector:
       matchLabels: {app: burst}
     template:
       metadata:
         labels: {app: burst}
       spec:
         terminationGracePeriodSeconds: 1
         containers:
         - name: a
           image: registry.k8s.io/e2e-test-images/agnhost:2.53
           args: ["netexec", "--http-port=8080"]
           readinessProbe:
             tcpSocket: {port: 8080}
             periodSeconds: 1
     updateStrategy:
       type: RollingUpdate
       rollingUpdate:
         maxUnavailable: 2
         partition: 0
   YAML
   kubectl -n burst rollout status sts/burst --timeout=180s
   kubectl -n burst set env sts/burst ROLL=2
   python3 /tmp/roll.py burst 120 | uniq -c
   ```

7. Now the bug the project turned this gate off for. The v1.37 release note describes it exactly: a
   faulty *initial* revision whose Pod never becomes ready, after which the controller fails to move
   that Pod to the corrected revision. Build that, then correct it, and see whether your cluster has
   the fix:

   ```sh
   kubectl create ns bug
   kubectl -n bug apply -f - <<'YAML'
   apiVersion: apps/v1
   kind: StatefulSet
   metadata:
     name: broke
   spec:
     serviceName: broke
     podManagementPolicy: OrderedReady
     replicas: 3
     selector:
       matchLabels: {app: broke}
     template:
       metadata:
         labels: {app: broke}
       spec:
         terminationGracePeriodSeconds: 1
         containers:
         - name: a
           image: registry.k8s.io/e2e-test-images/agnhost:2.53
           args: ["netexec", "--http-port=8080"]
           readinessProbe:
             tcpSocket: {port: 9999}
             periodSeconds: 1
     updateStrategy:
       type: RollingUpdate
       rollingUpdate:
         maxUnavailable: 2
   YAML
   sleep 60
   kubectl -n bug get pod -o wide
   kubectl -n bug patch sts broke --type=json \
     -p '[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/tcpSocket/port","value":8080}]'
   python3 /tmp/roll.py bug 120 | uniq -c
   kubectl -n bug get pod -o custom-columns=NAME:.metadata.name,REV:.metadata.labels.controller-revision-hash,READY:.status.containerStatuses[0].ready
   kubectl -n bug get controllerrevision -o custom-columns=NAME:.metadata.name,REV:.revision
   ```

8. The second open question, which the documentation still does not answer. Set a partition and a
   batch size at the same time and find out which one wins at the boundary:

   ```sh
   kubectl -n sts patch sts web --type=merge \
     -p '{"spec":{"updateStrategy":{"rollingUpdate":{"partition":3,"maxUnavailable":2}}}}'
   kubectl -n sts set env sts/web ROLL=3
   python3 /tmp/roll.py sts 90 | uniq -c
   kubectl -n sts get pod \
     -o custom-columns=NAME:.metadata.name,REV:.metadata.labels.controller-revision-hash | sort
   ```

9. Offline now, in the pinned checkout. Count how rare each part of this gate's shape is, against
   the whole population of gate files rather than against memory:

   ```sh
   cd /path/to/kubernetes/website/content/en/docs/reference/command-line-tools-reference/feature-gates
   cat MaxUnavailableStatefulSet.md
   grep -lE '(from|to)Version: "[0-9]+\.[0-9]+\.[0-9]+"' *.md
   python3 - <<'PY'
   import os, yaml
   g = {}
   for fn in sorted(os.listdir(".")):
       if fn.endswith(".md") and fn != "index.md":
           g[fn[:-3]] = yaml.safe_load(open(fn).read().split("---")[1])
   print("gate files", len(g))
   back = [(k, a["stage"], b["stage"])
           for k, m in g.items()
           for a, b in zip(m.get("stages", []), m.get("stages", [])[1:])
           if a.get("defaultValue") is True and b.get("defaultValue") is False]
   print("default true -> false:", len(back))
   print("  same stage:", sorted(k for k, s1, s2 in back if s1 == s2))
   mi = lambda v: int(str(v).split(".")[1])
   span = {}
   for k, m in g.items():
       a = [s for s in m.get("stages", []) if s["stage"] == "alpha"]
       if a:
           span[k] = (max(mi(s["toVersion"]) if s.get("toVersion") else 37 for s in a)
                      - min(mi(s["fromVersion"]) for s in a) + 1)
   print("with an alpha stage:", len(span))
   print("eleven or more:", sum(1 for v in span.values() if v >= 11))
   print("exactly eleven:", sorted(k for k, v in span.items() if v == 11))
   PY
   ```

10. And the drift between the two halves of the reference, which is the measurement that explains
    why step 2 and step 9 can both be right and still disagree. Compare every gate the binaries name
    against the gate file of the same name, at v1.37 and then at v1.36:

    ```sh
    cd /path/to/kubernetes/website/content/en
    python3 - <<'PY'
    import os, re, yaml
    D = "docs/reference/command-line-tools-reference"
    g = {}
    for fn in sorted(os.listdir(D + "/feature-gates")):
        if fn.endswith(".md") and fn != "index.md":
            g[fn[:-3]] = yaml.safe_load(
                open(D + "/feature-gates/" + fn).read().split("---")[1])
    gen = {m[0]: (m[1], m[2]) for m in re.findall(
        r'kube:([A-Za-z0-9]+)=true\|false \((ALPHA|BETA|GA|DEPRECATED) - default=(true|false)\)',
        open(D + "/kube-apiserver.md").read())}
    def at(name, minor):
        best = None
        for s in g[name].get("stages", []):
            lo = int(str(s["fromVersion"]).split(".")[1])
            hi = int(str(s["toVersion"]).split(".")[1]) if s.get("toVersion") else 999
            if lo <= minor <= hi:
                best = s
        return best and (best["stage"].upper(), str(best.get("defaultValue")).lower())
    both = [k for k in gen if k in g]
    print("named by the binaries", len(gen), " with a gate file", len(both))
    for minor in (37, 36):
        bad = [k for k in both if at(k, minor) != gen[k]]
        print("v1.%d disagreements: %d" % (minor, len(bad)),
              "MaxUnavailableStatefulSet" in bad)
    PY
    grep -n 'you must set OrderedReady' blog/_posts/2022/maxunavailable-for-statefulset.md
    sed -n '305,307p' docs/concepts/workloads/controllers/statefulset.md
    sed -n '607,616p' blog/_posts/2026/kubernetes-v1-37-release/index.md
    ```

**Expect**

Step 1 prints `v1.35.x` on a cluster provisioned from this repo's strand, and the ladder row it maps
to is the whole exercise in one line. On 1.35 and nowhere else the patch number decides: 3 or lower
and the gate is already on, so the post's instruction is wrong for you; 4 or higher and the gate is
off, so the instruction is right for you, four years after it stopped being right for anyone running
1.35.0. The node should carry no `NoSchedule` taint — `solo` is a single node that has to run
workloads — and neither static Pod manifest should mention `--feature-gates`, because nothing in the
provisioning run sets one.

Step 2 reports `kubernetes_feature_enabled{name="MaxUnavailableStatefulSet",stage="BETA"}` with a
value of 0 or 1 matching step 1's row, alongside `WatchList` and, if your build exposes it,
`SchedulerQueueingHints` — the two other gates in the archive whose default went off and on again
inside a single stage. `kubectl explain` describes the field in full either way. That is worth
pausing on: the schema always has the field, the gate only decides whether a write survives, so the
documentation you get from the cluster cannot tell you whether the feature works.

Step 3 is the test that matters. With the gate on, the read-back prints
`{"maxUnavailable":2,"partition":0}`. With it off, it prints `{"partition":0}` and nothing warns you
— no error, no event, no field on the status. The StatefulSet is accepted, the rollout will be
correct, and it will update one Pod at a time forever. This is the failure mode the post's
instruction exists to prevent, and it is silent.

Step 4 restarts both static Pods, so expect `kubectl` to fail for perhaps twenty seconds in the
middle. Afterwards the read-back has `maxUnavailable` in it and the metric reads 1. If the API
server does not come back, the manifest edit is the first suspect: `sed` inserted the flag after the
`- kube-apiserver` line, and a component that already had a `--feature-gates` flag would now have
two, which it rejects at startup. Step 1 checked for exactly that.

Step 5 is the post's `kubectl get pods --watch` block, compressed. Expect the collapsed output to
show a run with `web-3,web-4` terminating together, then a run with `web-1,web-2` together, then
`web-0` alone: three batches for five Pods, which is the arithmetic the post narrates at `:117-119`.
Watch the ready count as well — it should never fall below 3, because `maxUnavailable: 2` is a floor
on availability and not just a batch size. With `maxUnavailable` absent — which is the state step 3
leaves you in when the gate is off — the same rollout is five batches of one, and that is the
comparison the post never had to make.

Step 6 answers the first of the post's two closing questions the way the post half-answered it.
Under `Parallel` the terminations still come two at a time, but so do the creations: the Pod count
stays at 5 and two Pods are simultaneously terminating and being replaced, rather than the count
dipping while the controller waits. The post named this *bursting* at `:135` and the documentation
now uses the same word at `statefulset.md:307`. Note what the second manifest changes and what it
does not — the name, the namespace, the policy and the label move; `replicas`, `maxUnavailable`,
`partition` and the container are identical to step 3, because they are the variables being held
constant.

Step 7 is the one that may fail, and failing is the result. Under `OrderedReady` only `broke-0` is
ever created, because the controller will not start `broke-1` until its predecessor is ready, so the
three replicas you asked for never appear — that alone is worth seeing. On a cluster with the fix,
`broke-0` is recreated on the corrected revision within a few seconds of the patch and becomes
ready. On a cluster without it, `broke-0` stays on the first `controllerrevision` indefinitely while
a second revision sits in the list unused — the controller has counted a Pod that was never
available against `maxUnavailable`, and so never takes it. Compare the revision hash on the Pod
against the two `controllerrevision` objects. Whichever you get, you have reproduced the reasoning
behind the patch-level rollback: this is the shape of bug that is worth turning a beta default off
for, because the workload it strands is the one that was already broken.

Step 8 should update `web-3` and `web-4` together and leave `web-0` through `web-2` on the old
revision, which is `partition` and `maxUnavailable` agreeing rather than competing: the partition
chooses the set, the batch size chooses the rate. The interesting case is not this one. It is the
one where `.spec.ordinals.start` is non-zero, and that case is argued next door rather than here.

Step 9 prints the gate file with its four stages and two patch-level boundaries, then finds exactly
two files in 487 that use a three-part version — this gate and `DisableNodeKubeProxyVersion`. The
default-regression count should be 10 and the same-stage list should have five names on it, two of
them deprecated gates being switched off for good and three of them beta gates that were taken back:
`MaxUnavailableStatefulSet`, `SchedulerQueueingHints`, `WatchList`. Then 401 gates with an alpha
stage, 23 of them eleven releases or longer, and four at exactly eleven —
`BalanceAttachedNodeVolumes`, `CloudControllerManagerWebhook`, `ServiceNodeExclusion` and this one.
Ten out of 487 is not rare enough to be remarkable on its own; three out of 487 is, and two out of
487 is close to unique.

Step 10 should report 150 gates named by the binaries, 136 with a gate file, 36 disagreements at
v1.37 and 5 at v1.36 — and `MaxUnavailableStatefulSet` in the v1.37 list. That ratio is the finding:
a sevenfold jump between the two releases is not a documentation quality problem, it is a build
date. The generated reference at this pin is a v1.36 artifact sitting inside a v1.37 tree. Then the
three greps: the post contradicting itself four lines apart, the documentation answering the first
of its two questions in the post's own vocabulary, and the release note naming the bug that moved
the default back. Read that note against the gate file once more. The note says the bug was observed
in v1.36; the gate file records the default going false at 1.35.4. The rollback reached the 1.35
patch stream as well, and only the gate file says so.

**Read on**

1. [The two sentences this post is most emphatic
   about](../2017/04-kubernetes-statefulsets-daemonsets.md) — the gate's ladder in full, next to
   four sibling gates, plus the `partition` contradiction this exercise deliberately stops short of.
   Read it after step 8, when you have seen the easy case work.

2. [Rolling update predictions](../../labs/01/08-rolling-update-predictions.md) — the same question
   on a Deployment, where `maxUnavailable` has never been gated, has a percentage default, and comes
   with `maxSurge`. Predicting Pod counts there and then here is the fastest way to feel what
   ordering costs.

3. [Two halves of one Service CIDR](04-service-ip-dynamic-and-static-allocation.md) — the
   neighbouring row, on a gate that took four releases from alpha to deleted. Put its span against
   this one's eleven-release alpha and you have the two ends of the same distribution, measured on
   the same 487 files four days apart.

4. `kube-apiserver.md` in the pinned tree, specifically the `--feature-gates` row — 150 gates in one
   table cell, generated from the binary's help text, and the single best source at the pin for what
   a component actually shipped with. The index page next to it lists stage and default for every
   gate too, but it is built from the gate files rather than from a binary, which is exactly why the
   two can drift and step 10 can measure by how much.

5. Unanswerable from the pin: whether your cluster carries the fix for the bug in step 7. The
   release note names the issue and the release that fixed it, and the gate file records the default
   moving, but no page at the pin lists the patch releases of 1.35 or 1.36 that the fix was
   backported to — if it was. Step 7 measures your own cluster; it cannot tell you what any other
   cluster does.

**Teardown**

```sh
kubectl delete ns sts burst bug
ssh zain@10.10.10.180 'sudo test -f /root/kube-apiserver.yaml \
  && sudo cp /root/kube-apiserver.yaml /root/kube-controller-manager.yaml \
       /etc/kubernetes/manifests/ \
  || echo "step 4 was not needed; nothing to put back"'
sleep 45
kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' | grep -i maxunavailable
rm -f /tmp/roll.py
```

Put the manifests back even if you plan to keep the guest. A hand-set `--feature-gates` on two
static Pods is exactly the kind of state that makes the next exercise on this cluster measure the
wrong thing, and this one is worse than most because the flag it sets is the flag whose default
moves. Confirm the metric has gone back to the value step 2 printed before you walk away.
