<a id="kubernetes-1-24-non-graceful-node-shutdown-alpha"></a>

# The taint this post introduces still does what it says, the gate that guarded it is gone, both documentation links it hands you point at a section that moved pages and eight other files follow the same dead fragment, and the automation it promises was promised again word for word at GA

**Post** — [Kubernetes 1.24: Introducing Non-Graceful Node Shutdown Alpha](https://kubernetes.io/blog/2022/05/20/kubernetes-1-24-non-graceful-node-shutdown-alpha/), 2022-05-20.

97 lines, 7,935 bytes, two authors from one vendor — a little under 2022's median post of 8,081
bytes, and the third of the year's thirteen walked posts. It is the first of three posts on the same
feature: the beta seven months later and the GA fifteen months after that are both `read` rows, and
the whole arc is booked here.

**As written**

The post opens on a distinction. Graceful node shutdown, which went beta the year before, works
because the kubelet can see the shutdown coming: systemd takes an inhibitor lock, the kubelet
notices, and the Pods are terminated properly before the machine goes. Non-graceful is everything
else — a shutdown the kubelet never detects, a power cut, a broken OS, or a kubelet whose
`ShutdownGracePeriod` was misconfigured (`:18-22`).

Then it names the consequence, and the naming is the best part of the post. For a stateless workload
a lost node is barely an event: a ReplicaSet notices a missing Pod and makes another one. For a
StatefulSet it is a deadlock, because the replacement must take the dead Pod's name and the dead Pod
still exists. `:30-32` puts it in one sentence — *the StatefulSet cannot create a replacement pod
because the pod still exists in the cluster* — and `:36-37` closes the trap: if the node never comes
back, those Pods stay `Terminating` forever. A pasted `kubectl get pod -o wide` at `:39-44` shows
it: `web-0` Running, `web-1` Terminating.

The fix is one taint applied by a human. Enable `NodeOutOfServiceVolumeDetach` on the
`kube-controller-manager` (`:48-50`), satisfy yourself the node is genuinely off, and taint it
`node.kubernetes.io/out-of-service`. Pods that do not tolerate the taint are force-deleted, their
volumes are detached immediately, and the StatefulSet's replacement starts elsewhere. A second
pasted block at `:63-70` shows `web-1` Running again on a different node, ten minutes old. A bolded
Note at `:72` says you **must** verify the node is off first, and `:74-76` says to remove the taint
afterwards or delete the node outright.

The post closes on two forward-looking sentences. The first is a schedule: beta in 1.25 or 1.26,
*depending on feedback and adoption* (`:80`). The second is a plan: *In the future, we plan to find
ways to automatically detect and fence nodes that are shutdown/failed and automatically failover
workloads to another node* (`:82`). There is also a hedge earlier, at `:24-25`, that the kubelet
does not watch for shutdowns on Windows and that *this may change in a future Kubernetes release*.

**As it runs now**

The schedule was kept. `NodeOutOfServiceVolumeDetach` went beta in 1.26 — the later of the two
releases the post offered — stable in 1.28, and its stable stage ends at `1.31` with `removed:
true`. Six releases end to end, which [the previous exercise](02-grpc-probes-now-in-beta.md)
measured as the commonest lifetime a removed gate has. Two consecutive exercises, two gates, the
same six releases, different internal shapes: two-two-two here against one-three-two there.

The taint outlived the gate and is documented as a permanent part of the API. It has its own entry
at `labels-annotations-taints/_index.md:1963-1980`, and the behaviour the post describes is restated
almost word for word at `node-shutdown.md:274-279`, down to the two effects and the tolerations
check. `node-shutdown.md:281-284` breaks it into the two phases the post ran together — force-delete
the Pods, then detach the volumes — and `:288-292` carries the post's Note as a documented
requirement, including the instruction to remove the taint by hand afterwards.

**The documentation the post links to is on a different page.** Both of the post's links — `:15` for
graceful and `:86-87` for non-graceful — point at
`/docs/concepts/architecture/nodes/#graceful-node-shutdown` and `#non-graceful-node-shutdown`. At
the pin, `nodes.md` carries neither section: its last word on the subject is a see-also at
`nodes.md:307` pointing at `cluster-administration/node-shutdown.md`, a page that did not exist when
the post was written. The fragments themselves are still correct — `node-shutdown.md:252` is `##
Non-graceful node shutdown handling {#non-graceful-node-shutdown}` — so the anchors survived the
move and the links did not. Eight other files under `content/en` follow one of the same two dead
fragments, and four of them are documentation, including the description text of two feature gates.

**Two places the feature landed that the post does not mention.** The first is the Pod garbage
collector: `pod-lifecycle.md:1032-1037` lists three conditions under which PodGC cleans a Pod up,
and the third is *terminating Pods, bound to a non-ready node tainted with* this taint. The second
is its own replacement. `node-shutdown.md:296-318` documents a forced storage detach after six
minutes of a pod deletion not succeeding on an unhealthy node — automatic, and warned about, because
it can violate the CSI specification and corrupt data. The page says at `:307-308` that the
automatic one is optional and that users might use this post's manual procedure instead, and
`kube-controller-manager.md:448-451` gives the flag that does it: with
`--disable-force-detach-on-timeout` set, *the non-graceful node shutdown feature must be used to
recover from node failure*. The manual taint is the supported path, and the automatic thing that
arrived is the one you are told to turn off.

The instrumentation arrived with the beta and does not carry the names the posts print. The sequel
announces `force_delete_pods_total` and `force_delete_pod_errors_total`; the pin documents them at
`metrics.md:3360` and `:3367` as `pod_gc_collector_force_delete_pod_errors_total` and
`pod_gc_collector_force_delete_pods_total`, both ALPHA counters on the `kube-controller-manager`,
both labelled `namespace` and `reason`. The GA post's third metric fares worse: it calls it
`attachdetach_controller_forced_detaches` and the pin has
`attach_detach_controller_attachdetach_controller_forced_detaches` at `metrics.md:1750`, a name that
says its own subsystem twice — and its neighbour at `:1757` says it once.

The Windows hedge came true. `WindowsGracefulNodeShutdown` exists at the pin, alpha in 1.32, eight
releases after the post guessed it might happen, and beta from 1.34. The confident sentence did not.
There is no automatic fencing at the pin: `node-shutdown.md:288-292` still requires a human to add
the taint and a human to take it off, and it gives the reason — *since the user was the one who
originally added the taint*.

**What this exercise does not cover, and where it lives**

The volume half. This post's mechanism has two effects and only one of them is observable on this
lab. [The storage phase's node-loss drill](../../labs/08/19-chaos-node-loss.md) already measures the
detach timeline, names the flag that dominates it, and reaches the finding that a lost volume is
never reattached elsewhere here, because every backend available is node-local and the replacement
Pod stays `Pending` on volume node affinity. That drill also says, in terms, not to add a topology
to chase reattachment. This exercise takes it at its word: the StatefulSet below has no volume at
all, which removes storage from the experiment and leaves the Pod-identity deadlock on its own,
where it is fully observable.

The timers. [The kubelet stops and the Pods do
not](../../labs/06/22-6c2-the-kubelet-stops-the-pods-do-not.md) and [the node
vanishes](../../labs/06/23-6c1-the-node-vanishes.md) own the pair of drills this one rests on: the
lease arithmetic, the two eviction taints, and the finding that a stopped kubelet and a dead machine
are indistinguishable to the API server for the first forty seconds. Step 3 re-runs their setup only
far enough to reach the point where they stop, and the timers are theirs.

The taint vocabulary. [The advanced scheduling
post](../2017/02-advanced-scheduling-in-kubernetes.md) owns `key=value:Effect`, the three effects,
and the admission controller that gives every Pod a 300-second forgiveness toleration for
`node.kubernetes.io/not-ready` and `node.kubernetes.io/unreachable` — the timer that makes step 3
take five minutes. Graceful node shutdown itself is a `read` row in the 2021 census, where the
observable needs a real machine shutting down and a systemd inhibitor lock.

**The diff, and why**

**Broke: both documentation links, and the anchor census behind them.** The post's *How can I learn
more?* at `:86-87` is a link to a section that is not on that page any more, and `:15` is the same
failure for graceful shutdown. Neither is a 404: `/docs/concepts/architecture/nodes/` still
resolves, so a reader lands at the top of a long page about Nodes with no shutdown section in it and
no indication that anything is missing. This is the failure mode of a moved section rather than a
moved page, and it is quiet. The census in step 10 finds eight other files doing the same thing,
including the two feature-gate files whose entire job is to describe the feature and link its page.

**A plan the project abandoned, and you can date the abandonment inside this archive.** `:82` says
*we plan to find ways to automatically detect and fence nodes*. Seven months later the beta post
moves the work: *The cluster operator can automate this process by automatically applying the
`out-of-service` taint if there is a programmatic way to determine that the node is really shut
down*. The project's plan has become the operator's problem. The same paragraph then re-makes the
promise in new words, and the GA post, fifteen months after this one, prints this post's original
sentence again byte for byte. Three posts, one promise made three times, one handoff — and at the
pin, three years further on, the documentation still tells a human to type the taint and a human to
remove it. What was abandoned is not the feature, which is complete and permanent; it is the
sentence about what would come next, which has been carried forward twice without being worked on.

**Still right: the entire procedure, and the hedge.** Take out the feature-gate instruction at
`:48-50` and everything from `:52` to `:76` still describes the pin exactly — the taint, the two
effects, the tolerations check, the force-deletion, the detach, the replacement on another node, the
requirement to verify the node is off, the requirement to remove the taint afterwards. The prose is
close enough to `node-shutdown.md:274-292` that reading them side by side is a useful exercise in
itself. And the throwaway at `:24-25` about Windows, the one sentence in the post that is explicitly
uncertain, is the one that came true.

**Wrong when it was published: both taint strings in the prose.** `:56` gives
`node.kubernetes.io/out-of-service=nodeshutdown: "NoExecute"` and `:57` gives
`node.kubernetes.io/out-of-service=nodeshutdown:" NoSchedule"`. Neither is a taint `kubectl` will
accept as typed: the first has a space and a quote where the effect should start, the second opens
its quote before the colon's argument and then puts a space inside it. Eight lines later the code
block at `:64` gets it right. The beta post repeats the sentence with both effects and gets the
quoting right, so this is a defect of one post and not of the series. Step 4 types all three forms.

The gate itself is the case [the volume expansion exercise](01-volume-expansion-ga.md) opened this
year on: a switch removed because everyone agreed with the thing it switched. It is not re-argued
here.

Not the seventh case, but the near miss is worth the line. Nothing under `content/en` cites this
post, or the beta post. The documentation's single link into this three-post series is at
`node-shutdown.md:331` and points at the GA post — written `-ga/` against a slug spelled `-GA`. Step
9 measures how unusual that is across every blog link the documentation makes.

**The ladder**

Two gates, transcribed from their `stages:` lists parsed as YAML. `GracefulNodeShutdown`, which the
post contrasts itself against, belongs to the 2021 census to ladder and is named here only as beta
since 1.21 with no end recorded.

```
NodeOutOfServiceVolumeDetach  alpha  false  1.24 - 1.25   <- this post
                              beta   true   1.26 - 1.27
                              stable true   1.28 - 1.31
                                                          removed

WindowsGracefulNodeShutdown   alpha  false  1.32 - 1.33
                              beta   true   1.34 -
```

The first ladder is the whole arc of the feature and every rung of it has a post: `1.24` is this
one, `1.26` is the December sequel, `1.28` is the August 2023 sequel, and nothing was written when
the gate was deleted. The second is the answer to a sentence in this post's third paragraph,
delivered eight releases after the feature it hedged about.

**Topology** — [`workhorse`](../../strands/lab-topologies.md#workhorse): a control plane at
`10.10.10.140` and two workers at `10.10.10.141`–`.142`, one core each. Bring it up with [the
provisioning sequence](../../strands/lab-topologies.md#provision) if it is not standing. Two workers
is not scale here, it is the minimum that makes the finding visible: the deadlock this post is about
is a Pod that cannot be recreated, and *recreated where* has to have an answer or the experiment
proves nothing. Derive both worker names rather than typing them.

**Do**

1. Establish the pin's position before breaking anything. The gate the post tells you to enable
   should be unknown to the component it names, and the taint should be documented and unused:

   ```sh
   kubectl version -o json | python3 -c 'import json,sys
   print("server:", json.load(sys.stdin)["serverVersion"]["gitVersion"])'
   kubectl get nodes -o custom-columns=NAME:.metadata.name,IP:'.status.addresses[0].address'
   kubectl get node -l '!node-role.kubernetes.io/control-plane' \
     -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'
   kubectl get --raw /metrics | grep -c 'NodeOutOfServiceVolumeDetach' || echo 0
   kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.taints}{"\n"}{end}'
   ```

2. Build the ground the post assumes and the control it does not have. One StatefulSet with no
   volume of any kind, one Deployment, both two replicas, one replica pinned to each worker so the
   failure lands on exactly one of each:

   ```sh
   kubectl create ns ngs
   kubectl apply -n ngs -f - <<'YAML'
   apiVersion: apps/v1
   kind: StatefulSet
   metadata: { name: web }
   spec:
     serviceName: web
     replicas: 2
     selector: { matchLabels: { app: web } }
     template:
       metadata: { labels: { app: web } }
       spec:
         affinity:
           podAntiAffinity:
             requiredDuringSchedulingIgnoredDuringExecution:
             - labelSelector: { matchLabels: { app: web } }
               topologyKey: kubernetes.io/hostname
         containers:
         - name: c
           image: registry.k8s.io/pause:3.10
   ---
   apiVersion: apps/v1
   kind: Deployment
   metadata: { name: dep }
   spec:
     replicas: 2
     selector: { matchLabels: { app: dep } }
     template:
       metadata: { labels: { app: dep } }
       spec:
         affinity:
           podAntiAffinity:
             requiredDuringSchedulingIgnoredDuringExecution:
             - labelSelector: { matchLabels: { app: dep } }
               topologyKey: kubernetes.io/hostname
         containers:
         - name: c
           image: registry.k8s.io/pause:3.10
   YAML
   kubectl -n ngs get pods -o wide
   ```

3. Take a worker away and wait out the timer. Stop only the kubelet, which is the drill the node
   phase already owns, and mark the four moments. The last one takes five minutes and the wait is
   the point:

   ```sh
   V=$(kubectl -n ngs get pod web-1 -o jsonpath='{.spec.nodeName}')
   echo "victim: $V"
   ssh zain@$(kubectl get node $V -o jsonpath='{.status.addresses[0].address}') \
     'date +%T; sudo systemctl stop kubelet'
   date +%T
   kubectl get node $V -w -o custom-columns=\
   NAME:.metadata.name,READY:'.status.conditions[?(@.type=="Ready")].status'
   # in a second shell, until the eviction fires:
   kubectl get node $V -o jsonpath='{range .spec.taints[*]}{.key}:{.effect}{"\n"}{end}'
   kubectl -n ngs get pods -o wide -w
   ```

4. While you wait, type the post's three taint forms at a node that is not the victim and find out
   which of them `kubectl` will parse. Two are from the prose, one is from the code block:

   ```sh
   C=$(kubectl get node -l node-role.kubernetes.io/control-plane \
     -o jsonpath='{.items[0].metadata.name}')
   kubectl taint nodes $C 'node.kubernetes.io/out-of-service=nodeshutdown: "NoExecute"' \
     --dry-run=client 2>&1 | tail -1
   kubectl taint nodes $C 'node.kubernetes.io/out-of-service=nodeshutdown:" NoSchedule"' \
     --dry-run=client 2>&1 | tail -1
   kubectl taint nodes $C node.kubernetes.io/out-of-service=nodeshutdown:NoExecute \
     --dry-run=client 2>&1 | tail -1
   ```

5. The eviction has fired by now. Record the deadlock the post exists for, and prove it is the name
   and not the storage — there is no storage:

   ```sh
   kubectl -n ngs get pods -o wide
   kubectl -n ngs get pod web-1 \
     -o jsonpath='{.metadata.deletionTimestamp}{"\t"}{.status.phase}{"\n"}'
   kubectl -n ngs get statefulset web -o jsonpath='{.status.replicas}/{.spec.replicas}{"\n"}'
   kubectl -n ngs describe statefulset web | sed -n '/Events:/,$p'
   kubectl get volumeattachment 2>&1 | head -3
   ```

6. Now the taint, in the spelling the documentation uses rather than the one the post uses, and
   watch the deadlock clear:

   ```sh
   date +%T
   kubectl taint nodes $V node.kubernetes.io/out-of-service:NoExecute
   kubectl -n ngs get pods -o wide -w
   # once it settles:
   date +%T; kubectl -n ngs get pods -o wide
   kubectl get --raw /metrics | grep '^pod_gc_collector_force_delete' | grep -v '^#'
   ```

7. Find out what the taint's *value* is worth. The post, both its sequels and nothing in the
   documentation use `nodeshutdown`; the documented example at `labels-annotations-taints:1967` has
   no value at all. You have just applied the valueless form successfully, so re-run the whole cycle
   with a value that means nothing:

   ```sh
   kubectl taint nodes $V node.kubernetes.io/out-of-service:NoExecute-
   ssh zain@$(kubectl get node $V -o jsonpath='{.status.addresses[0].address}') \
     'sudo systemctl start kubelet'
   kubectl wait --for=condition=Ready node/$V --timeout=300s
   kubectl -n ngs delete pod --all --wait=true
   kubectl -n ngs rollout status statefulset/web --timeout=300s
   # break it again, wait out the five minutes, then:
   kubectl taint nodes $V node.kubernetes.io/out-of-service=banana:NoExecute
   kubectl -n ngs get pods -o wide -w
   ```

8. Do what the post's bolded Note forbids, deliberately, and see what it is protecting you from. The
   victim's kubelet was stopped, not powered off, so its containers never stopped running. Go and
   look at them from the node while the replacement is up:

   ```sh
   kubectl -n ngs get pods -o wide
   ssh zain@$(kubectl get node $V -o jsonpath='{.status.addresses[0].address}') \
     'sudo crictl ps --name c -o table'
   kubectl -n ngs get pod -l app=web -o jsonpath=\
   '{range .items[*]}{.metadata.name}{"\t"}{.spec.nodeName}{"\n"}{end}'
   ```

9. Offline now, in the pinned checkout. Every link the documentation makes into the blog, joined
   against the archive's own slugs — because the one link it makes into this post's series is the
   reason to look:

   ```sh
   cd /path/to/kubernetes/website
   python3 - <<'PY'
   import os, re
   B = "content/en/blog/_posts"
   slugs = set()
   for root, _, fs in os.walk(B):
       for fn in fs:
           if not fn.endswith(".md"): continue
           t = open(os.path.join(root, fn), encoding="utf-8", errors="replace").read()
           m = re.search(r'^slug:\s*(\S+)\s*$', t, re.M)
           if m: slugs.add(m.group(1))
           elif fn == "index.md": slugs.add(os.path.basename(root))
           else: slugs.add(fn[:-3])
   pat = re.compile(r'/blog/\d{4}/\d{2}/\d{2}/([A-Za-z0-9._-]+)/?')
   links = set()
   for root, _, fs in os.walk("content/en/docs"):
       for fn in fs:
           if not fn.endswith(".md"): continue
           pth = os.path.join(root, fn)
           for i, l in enumerate(open(pth, encoding="utf-8", errors="replace"), 1):
               for m in pat.finditer(l):
                   links.add((m.group(1), pth.split("content/en/")[1], i))
   print("slug candidates:", len(slugs), "| docs->blog links:", len(links))
   for s, pth, i in sorted(links):
       if s in slugs: continue
       ci = [x for x in slugs if x.lower() == s.lower()]
       print("  MISS", s, "| case-only match:", ci, "|", pth + ":" + str(i))
   PY
   ```

10. And the dead fragment, counted, plus the promise, pulled out of all three posts in the series
    and normalised so the wrapping does not hide the answer:

    ```sh
    cd /path/to/kubernetes/website
    grep -rn 'architecture/nodes/#[a-z-]*graceful' content/en --include='*.md' \
      | sed 's|content/en/||' | sort
    grep -rl 'architecture/nodes/#[a-z-]*graceful' content/en --include='*.md' | wc -l
    grep -n 'graceful-node-shutdown\|non-graceful-node-shutdown' \
      content/en/docs/concepts/architecture/nodes.md || echo "no such section on that page"
    grep -n '{#non-graceful-node-shutdown}\|{#graceful-node-shutdown}' \
      content/en/docs/concepts/cluster-administration/node-shutdown.md
    for F in 2022/non-graceful-node-shutdown.md \
             2022/non-graceful-node-shutdown-to-beta.md \
             2023/non-graceful-node-shutdown-to-ga.md; do
      printf '%s\n  ' "$F"
      tr '\n' ' ' < "content/en/blog/_posts/$F" \
        | grep -o 'In the future, we plan[^.]*\.\|The cluster operator can automate[^.]*\.' \
        | tr -s ' '
    done
    ```

**Expect**

Step 1 finds no `NodeOutOfServiceVolumeDetach` anywhere in the `kube-apiserver` metrics, which is
correct twice over — it was never an apiserver gate, and it is not a gate anywhere any more. The
instruction at `:48-50` is the one line of the procedure that has no modern equivalent, and there is
nothing to put in its place: the behaviour it guarded is unconditional.

Step 2 gives you four Pods, two per worker. The anti-affinity is doing the work the post's pasted
output implies without saying: `web-0` and `web-1` on different nodes is not a StatefulSet
guarantee, it is a scheduling outcome, and the experiment needs it to be reliable.

Step 3 reproduces the node phase's drill and stops where it stops. `Ready` goes to `Unknown` about
forty seconds after the kubelet dies; `node.kubernetes.io/not-ready` and then
`node.kubernetes.io/unreachable` appear; and roughly five minutes later — the 300 seconds the
admission controller wrote into every Pod — the eviction fires and both Pods on the victim gain a
`deletionTimestamp`. Nothing confirms either deletion, because the only component that could is the
one you stopped.

Step 4 should reject the first two and accept the third. The point is not that `kubectl` validates
taints; it is that a reader who copied either sentence from the prose rather than the code block got
an error message, in 2022, on the day the post published, and that the beta post prints the same
sentence seven months later with the quoting right.

Step 5 is the deadlock, and it should be clean. The Deployment is already back at 2/2 — a
replacement Pod with a new name started on the surviving worker within seconds of the eviction, as
[the node-vanishes drill](../../labs/06/23-6c1-the-node-vanishes.md) predicts. The StatefulSet is at
1/2 and will stay there: `web-1` has a `deletionTimestamp` and is still `Running`, and the
controller will not create a second `web-1`. `kubectl get volumeattachment` returns nothing, which
is the control — there is no storage in this experiment, so the only thing holding the replacement
back is the name.

Step 6 should clear it in seconds. The taint goes on, PodGC force-deletes the Pods that do not
tolerate it, the API object for `web-1` disappears without the kubelet ever being consulted, and the
StatefulSet immediately creates a new `web-1` on the surviving worker. The counters should read
`pod_gc_collector_force_delete_pods_total` with a `reason` label — the label the GA post added and
the alpha post could not have had — and with `namespace="ngs"`. Note what you had to type: the
documentation's spelling, with no value, and it worked.

Step 7 should find that the value is decoration. `banana` is not `nodeshutdown` and is not in any
documentation, and the Pods move anyway; the controller matches on the key. Three blog posts across
sixteen months print `=nodeshutdown` and the pin's own example does not, which is the more
interesting half: the convention survives entirely in announcements of a feature, and never made it
into the reference page for the taint it decorates.

Step 8 is why `:72` is bolded and why `node-shutdown.md:288-289` repeats it. `crictl ps` on the
victim shows the container from `web-1` still running, minutes after the API server stopped
believing in it and after a new `web-1` took its name on another node. Nothing was shut down; a
kubelet was stopped, and you asserted otherwise. On this experiment the container is a `pause` and
the cost is zero. With a database and a shared volume it is two writers, and the CSI note at
`node-shutdown.md:300-305` is describing the same hazard from the storage side. Write down what the
taint actually is: not a command to the node, which is gone, but an operator's sworn statement to
the control plane, believed without verification.

Step 9 should find 39 distinct blog links from the documentation and six whose slug is not an exact
match. Five of those are posts this checkout does not contain. The sixth is `node-shutdown.md:331`,
and it is the only one where a case-insensitive match exists —
`kubernetes-1-28-non-graceful-node-shutdown-ga` written against
`kubernetes-1-28-non-graceful-node-shutdown-GA`. Eighteen slugs in the archive carry an uppercase
letter; exactly one of them is linked from the documentation, and that link does not match it.

Step 10 should list twelve links across nine files, and no section on `nodes.md` for either of them
to land on. Four of the nine are documentation pages, including `GracefulNodeShutdown.md:20` and
`WindowsGracefulNodeShutdown.md:21` — gate descriptions whose one link is broken. The loop should
print four sentences: the promise once per post, and one extra from the beta's block. The alpha's
and the GA's are byte-identical, fifteen months apart, with the feature finished in between. The
beta's, in the middle, is reworded — *shut down or in a non-recoverable state* rather than
*shutdown/failed* — and sits directly under the sentence handing the automation to the cluster
operator. The promise was reworded once and then restored to its original text, which is a stranger
thing to find than a promise quietly dropped.

**Read on**

1. [The node vanishes](../../labs/06/23-6c1-the-node-vanishes.md) — the drill this one starts at the
   end of. It measures the two timers, establishes that a stopped kubelet and a dead machine look
   identical for forty seconds, and finds that the stuck deletions unstick themselves when the node
   returns. This exercise is the case where the node does not return.

2. [Lose a node with a volume attached](../../labs/08/19-chaos-node-loss.md) — the other half of
   this post's mechanism, and the reason the StatefulSet above has no volume. It owns the detach
   timeline, the flag that dominates it, and the finding that node-local storage turns a node
   failure into a data-placement problem.

3. [Advanced scheduling, and the anchor that was broken before the page
   moved](../2017/02-advanced-scheduling-in-kubernetes.md) — the taint vocabulary, the three
   effects, and the 300-second forgiveness toleration that makes step 3 slow. It also carries the
   archive's other moved-page finding, which fails the opposite way round: there the fragment was
   already wrong, here the fragment is right and the page is wrong.

4. `node-shutdown.md:252-318` in the pinned tree — the section the post's link no longer reaches,
   read end to end. The first half is this post in documentation voice; the second half is the
   automatic force-detach that arrived later, the data corruption it can cause, and the flag that
   makes this post's manual procedure mandatory.

5. Unanswerable from the pin: whether automatic node fencing was ever designed. The sentence at
   `:82` is repeated verbatim at GA and the pin holds no trace of work behind it — no gate, no flag,
   no documentation, not a note. The post links KEP-2268 for the feature that shipped; there is no
   KEP named in any of the three posts for the fencing that did not, and the checkout carries no
   KEPs, so the archive can date the promise and cannot date its abandonment.

**Teardown**

```sh
kubectl taint nodes $V node.kubernetes.io/out-of-service=banana:NoExecute- 2>/dev/null || true
ssh zain@$(kubectl get node $V -o jsonpath='{.status.addresses[0].address}') \
  'sudo systemctl start kubelet'
kubectl wait --for=condition=Ready node/$V --timeout=300s
kubectl delete ns ngs
kubectl get nodes
```

Take the taint off before starting the kubelet, not after, or the returning node is force-emptied as
it reports in. The victim's own containers from the first half of the experiment are cleaned up by
the kubelet the moment it comes back and finds Pods it is no longer meant to run. Nothing here
changed a component's configuration, so the cluster is as step 1 found it; leave it up if you are
going straight on, or [destroy it](../../strands/lab-topologies.md#teardown).
