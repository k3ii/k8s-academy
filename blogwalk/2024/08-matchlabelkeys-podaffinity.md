<a id="matchlabelkeys-podaffinity"></a>

# Neither term of this post's second worked example can be submitted to the API it describes, both of its translated blocks depict objects that the same validation forbids you to write, and the page that replaced the example fixed one of the two violations and inherited the other

**Post** — [Kubernetes 1.31: MatchLabelKeys in PodAffinity graduates to beta](https://kubernetes.io/blog/2024/08/16/matchlabelkeys-podaffinity/),
2024-08-16.

5,792 bytes, 156 lines, by Kensei Nakada of Tetrate. Fourteenth-smallest of the fifty-four posts
2024 published, against a mean of 10,767 bytes, and the fifth-smallest of the thirteen this year
sends you to walk. The shape matters more than the size: thirty-two lines of prose and eighty-five
lines of YAML across four fences, which makes this post a specification by example. Three of those
four fences are examples you are meant to copy, and the fourth exists only to show you what the
first three become. That is where the trouble is.

**As written**

Two fields, `matchLabelKeys` and `mismatchLabelKeys`, arrived in `podAffinity` and `podAntiAffinity`
at 1.29. At 1.31 they reach beta and the gate `MatchLabelKeysInPodAffinity` turns on by default.
That is the whole announcement, in two sentences at `:10` and `:12`. Everything after is the two use
cases.

The first use case is the rolling update. During a rollout a cluster holds Pods from two revisions
at once, and the scheduler, which sees only the `labelSelector` you wrote, cannot tell them apart
(`:16-17`). The post names two ways that goes wrong at `:20-21`: new Pods get co-located with old
Pods that are about to be deleted, or old Pods have already taken every topology domain and
`podAntiAffinity` leaves the new Pods nowhere to go. `matchLabelKeys` is a set of label keys; the
scheduler reads their values off the incoming Pod and combines them with the `labelSelector`
(`:23-25`). Put `pod-template-hash` in it and only Pods of the same revision are ever considered
(`:27-28`).

Then the first fence, `:30-48`: a Deployment whose `podAffinity` term selects `app in (database)` on
`topology.kubernetes.io/zone`, with `matchLabelKeys: [pod-template-hash]` added beneath the
`topologyKey`. Then a line that is the hinge of the whole post, `:50` — "The above `matchLabelKeys`
will be translated in Pods like:" — and the second fence, `:52-75`, a Pod whose
`labelSelector.matchExpressions` now carries a second expression the author never wrote, `key:
pod-template-hash`, `operator: In`, `values: [xyz]`, with an inline comment saying it was added from
`matchLabelKeys`.

The second use case is tenant isolation. Suppose every Pod gets a `tenant` label from a controller
or from Helm, and the value is not known when the manifest is composed (`:83-86`). The cluster admin
wants one tenant per domain, exclusively. The post's answer at `:88-91` is to apply one affinity
block globally, with a mutating webhook: a `podAffinity` term that pulls the tenant's own Pods
together, and a `podAntiAffinity` term that keeps every other tenant's Pods away.

The third fence, `:93-109`, is that block. Its `podAffinity` term has `matchLabelKeys: [tenant]` and
`topologyKey: node-pool` and nothing else. Its `podAntiAffinity` term has `mismatchLabelKeys:
[tenant]`, a `labelSelector` matching `tenant Exists`, and the same `topologyKey`. The fourth fence,
`:113-145`, translates both: a `labelSelector` appears inside the affinity term where the source had
none, and the anti-affinity term's selector grows a second `tenant` expression beside the one that
was already there.

Two closing links at `:155-156`: the pod-affinity section of the concepts page, and KEP-3633,
anchored at `#story-2`. No caveats, no validation rules, no note that either example needs anything
the post has not shown you.

**As it runs now**

**The API reference states two rules the post never mentions, once for each field.**
`docs/reference/kubernetes-api/core/pod-v1.md:1949` describes `matchLabelKeys` under
`PodAffinityTerm` and ends with two sentences: "The same key is forbidden to exist in both
matchLabelKeys and labelSelector. Also, matchLabelKeys cannot be set when labelSelector isn't set."
`:1953` says the identical pair for `mismatchLabelKeys`. Both are stated as prohibitions on the
object you submit, not as advice.

**Both terms of the post's tenant block break one of those rules.** The `podAffinity` term at the
post's `:97-99` sets `matchLabelKeys` with no `labelSelector` at all, which is the second rule. The
`podAntiAffinity` term at the post's `:102-108` puts `tenant` in `mismatchLabelKeys` and then puts
`tenant` in the `labelSelector` immediately below it, which is the first. The post presents this
block as something a cluster admin applies to every Pod in the cluster through a mutating webhook.

**Both of the post's translated fences depict objects that break the first rule too.** The
translated Pod at the post's `:62-74` has `pod-template-hash` in the `labelSelector` and
`pod-template-hash` in `matchLabelKeys`. The translated tenant Pod at the post's `:134-143` has
`tenant` in `mismatchLabelKeys` and twice in the `labelSelector`. These are not manifests the post
is asking you to write — they are its picture of what the cluster stores. Which is the interesting
part: if the rules hold, the merge produces an object you are forbidden to submit, and the
prohibition therefore applies to authorship and not to the stored shape. Step 5 submits one of them
and finds out.

**The merge is attributed to the apiserver, not the scheduler.**
`docs/concepts/scheduling-eviction/assign-pod-node.md:401-405` carries a caution against using
`matchLabelKeys` with labels that might be edited directly on Pods, and gives the reason:
"kube-apiserver doesn't reflect the label update onto the merged `labelSelector`." A warning phrased
that way is only coherent if the merged `labelSelector` is a persisted thing the apiserver wrote
once. That is what makes the post's "will be translated in Pods like" a claim you can check with
`kubectl get` rather than one you have to take on faith.

**The gate is stable and locked, so nothing here is conditional.** The ladder for
`MatchLabelKeysInPodAffinity`, and the note on the concepts page that still calls the field
beta-level, are [worked through beside the 2017 post on advanced
scheduling](../2017/02-advanced-scheduling-in-kubernetes.md); that exercise owns them and this one
does not repeat them. What matters here is only the consequence: at the pin these fields are
unconditional, so every rejection you see in `Do` is validation and never a disabled gate.

**The post's first example survived intact into the page the post points at.** The Deployment at
`assign-pod-node.md:412-436` is the post's first fence with three differences: the `spec:` and
`template:` levels the post elided behind `...` are spelled out, three comment lines were added
above `matchLabelKeys`, and nothing else changed. Same `app in (database)`, same zone topology key,
same field. At v1.37 the documentation still teaches the rolling-update case in the post's own
arrangement and the post's own words.

**The tenant example survived too, with one of its two violations repaired.** The Pod at
`assign-pod-node.md:463-495` is the post's third fence rewritten as a standalone Pod. Its
`podAffinity` term gained `labelSelector: {}` at `:478`, which is exactly the second rule being
satisfied. Its `podAntiAffinity` term at `:483-493` still has `tenant` in `mismatchLabelKeys` and
`tenant` in the `labelSelector` — and now carries a three-line comment explaining that the selector
has to be there, "otherwise this Pod would have anti-affinity against Pods from daemonsets as well".
The page has reasoned its way to keeping the thing the API reference forbids.

**The topology key both examples use is not a label Kubernetes knows.** `node-pool` appears in
exactly two places across the pinned `content/en` tree outside this post, and both are the tenant
example on the concepts page. It is not in the well-known labels reference. That is legal — a
`topologyKey` may be any label key — but `assign-pod-node.md:361-364` then says that for required
anti-affinity "the admission controller `LimitPodHardAntiAffinityTopology` limits `topologyKey` to
`kubernetes.io/hostname`", and `docs/reference/access-authn-authz/admission-controllers.md:502` says
that controller "is disabled by default". The page states a restriction and then relies, in its own
example, on the restriction not being enforced. Step 8 reads the apiserver's flags and settles which
half describes this cluster.

**The deadlock the post is fixing has a documented counterpart that cannot happen.**
`assign-pod-node.md:308-315` guarantees that a group of Pods with affinity to themselves will never
deadlock: the first one is allowed through if no other Pod matches its selector. There is no
equivalent paragraph for anti-affinity anywhere on the page, and there cannot be, because the
predecessor Pod that blocks the surge Pod is real and running. The asymmetry is the post's second
bullet at `:21` restated from the other side, and steps 2 and 3 make you watch it.

**The feature's own announcements are lopsided.** `matchLabelKeys` appears in five posts across the
whole archive. Alpha got one sentence inside the v1.29 release announcement, under "New alpha
features" at that post's `:95-97`. Stable got one section of the v1.33 release announcement, at that
post's `:218-226`, which names KEP-3633 and calls the fields "newly stable options". Beta got this
post — the only piece the feature ever had to itself. Six files in the archive name its author; five
of those are author credits, and the affiliation on them changes from Mercari in the 2023 posts to
Tetrate in this one and in everything after it.

**And the fourth thing, which is the pinned documentation disagreeing with itself in a way no
command settles.** `assign-pod-node.md:260-263` is a note near the top of the inter-pod affinity
section: these rules "require substantial amounts of processing which can slow down scheduling in
large clusters significantly. We do not recommend using them in clusters larger than several hundred
nodes." Two hundred lines later the same page presents the tenant pattern, and the post it took it
from says at `:88-91` to apply that pattern to every Pod in the cluster with a mutating webhook.
Multi-tenant clusters partitioned into node pools are not small clusters; the pattern's natural
habitat is the population the note warns off. Both halves are the same file. Cite them both. A
single node cannot tell you which one to believe, because the cost the note describes is a function
of node count and this cluster has one.

**What this exercise does not cover, and where it lives**

The gate ladder for `MatchLabelKeysInPodAffinity`, and the note on the concepts page that calls the
field beta-level when the gate record says stable and locked, belong to [the walk beside the 2017
post on advanced scheduling](../2017/02-advanced-scheduling-in-kubernetes.md). The same field name
exists under `topologySpreadConstraints`, with its own gate, its own ten-release stay at beta and a
second gate added at 1.34 to make its merge explicit; all of that, including reading the stored
`labelSelector` off a spread-constrained Pod, belongs to [the walk beside the post introducing
PodTopologySpread](../2020/04-introducing-podtopologyspread.md). Diagnosing a spread constraint that
no node can satisfy is [drill 5.C3 in the
labs](../../labs/05/36-5c3-a-spread-nobody-can-satisfy.md). This exercise is about one thing: what
the apiserver accepts, what it writes, and whether those are the same object.

**The diff, and why**

**Still right.** The rolling-update case is correct in every particular and the fix works. The
scheduler really cannot distinguish revisions from a `labelSelector` alone; required anti-affinity
against your own Pods really does stall a rollout; `pod-template-hash` in `matchLabelKeys` really
does unstall it. Steps 2 and 3 reproduce the failure and the repair on one node running v1.35, with
the post's own field and nothing else.

**Retired by being agreed with.** The post's first fence is now the concepts page's example,
transcribed with the nesting filled in and three comments added. `assign-pod-node.md:412-436` says
what the post says, in the post's arrangement, on a page the post itself sends you to at `:155`.
When the documentation has absorbed your example verbatim, the announcement has finished its job —
which is why the only reason to read this post at the pin is the half the documentation did not
absorb cleanly.

**Wrong when it was published.** The tenant block was not a manifest anyone could apply, and was not
one in August 2024 either. Both of its rules — a key may not appear in both the keys field and the
selector, and the keys field may not be set without a selector — are properties of the validation
that shipped with the fields at 1.29, not rules added later. The post did not print a manifest that
has since gone stale; it printed a manifest that the API server it was announcing would have
rejected on the day the post went up. Step 6 applies it verbatim and reads the errors.

**Never absorbed.** What the concepts page took from the second use case is the YAML. What it left
is the delivery mechanism: the post's `:88-91` says to apply the affinity block globally through a
mutating webhook, because the tenant value is not knowable when the manifest is written — which is
the entire reason `mismatchLabelKeys` exists rather than a hand-written selector. The page at
`assign-pod-node.md:460-461` reduces it to a hand-written Pod with `tenant: tenant-a` typed in the
labels, which is the case that needed neither field. The operational idea survives only in
KEP-3633's second story, which the post links at `:156` and nothing in the pinned tree does.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180` running Kubernetes v1.35,
provisioned with [the standard steps](../../strands/lab-topologies.md#provision) and [the node
baseline](../../strands/lab-topologies.md#node-baseline-steps). One node is not a limitation here,
it is the instrument. A required `podAntiAffinity` on `kubernetes.io/hostname` divides this cluster
into exactly one domain, so a rolling update that needs a second domain has nowhere to go and the
failure the post describes arrives in seconds instead of needing a fleet. Everything else in this
exercise is admission: whether the API server accepts an object, and what it writes when it does.
Admission does not care how many nodes are watching. Namespace `bw-mlk`, deleted at the end.

**Do**

1. Ground the cluster and read the two fields back from the server's own schema, not from the post.
   The server is v1.35 and the pinned documentation is v1.37; note the gap and carry it into every
   reading below.

   ```sh
   ssh zain@10.10.10.180
   kubectl version -o json | jq -r '.serverVersion.gitVersion'
   kubectl create namespace bw-mlk
   R=requiredDuringSchedulingIgnoredDuringExecution
   kubectl explain pod.spec.affinity.podAffinity.$R.matchLabelKeys
   kubectl explain pod.spec.affinity.podAntiAffinity.$R.mismatchLabelKeys
   kubectl get nodes -o jsonpath='{.items[*].metadata.name}{"\n"}'
   ```

2. Build the failure the post's second bullet describes. One replica, required anti-affinity against
   its own label, the hostname topology key, and a rollout strategy that must surge before it may
   remove anything. Then change the pod template and ask for the rollout to finish.

   ```sh
   kubectl -n bw-mlk apply -f - <<'YAML'
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: web
   spec:
     replicas: 1
     strategy:
       type: RollingUpdate
       rollingUpdate:
         maxUnavailable: 0
         maxSurge: 1
     selector:
       matchLabels:
         app: web
     template:
       metadata:
         labels:
           app: web
       spec:
         affinity:
           podAntiAffinity:
             requiredDuringSchedulingIgnoredDuringExecution:
             - labelSelector:
                 matchExpressions:
                 - key: app
                   operator: In
                   values:
                   - web
               topologyKey: kubernetes.io/hostname
         containers:
         - name: pause
           image: registry.k8s.io/pause:3.10
   YAML
   kubectl -n bw-mlk rollout status deploy/web --timeout=90s
   kubectl -n bw-mlk set env deploy/web REV=2
   kubectl -n bw-mlk rollout status deploy/web --timeout=60s ; echo "exit=$?"
   kubectl -n bw-mlk get pods -o wide
   kubectl -n bw-mlk describe pod -l app=web | grep -A6 '^Events:'
   ```

3. Start again from a clean Deployment that differs from the one above by two lines —
   `matchLabelKeys` holding the one label the Deployment controller writes for you — and run the
   same rollout. Deleting first keeps the comparison honest: the stalled surge Pod from step 2 is
   not left lying around to confuse the scale-down arithmetic.

   ```sh
   kubectl -n bw-mlk delete deploy/web --wait=true
   kubectl -n bw-mlk apply -f - <<'YAML'
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: web
   spec:
     replicas: 1
     strategy:
       type: RollingUpdate
       rollingUpdate:
         maxUnavailable: 0
         maxSurge: 1
     selector:
       matchLabels:
         app: web
     template:
       metadata:
         labels:
           app: web
       spec:
         affinity:
           podAntiAffinity:
             requiredDuringSchedulingIgnoredDuringExecution:
             - labelSelector:
                 matchExpressions:
                 - key: app
                   operator: In
                   values:
                   - web
               topologyKey: kubernetes.io/hostname
               matchLabelKeys:
               - pod-template-hash
         containers:
         - name: pause
           image: registry.k8s.io/pause:3.10
   YAML
   kubectl -n bw-mlk rollout status deploy/web --timeout=90s
   kubectl -n bw-mlk set env deploy/web REV=2
   kubectl -n bw-mlk rollout status deploy/web --timeout=90s ; echo "exit=$?"
   kubectl -n bw-mlk get rs -o custom-columns=NAME:.metadata.name,DESIRED:.spec.replicas,READY:.status.readyReplicas
   ```

4. Ask the cluster whether the post's `:50` is literally true. Read the anti-affinity term off a
   running Pod and compare it with the term the Deployment holds. The question is whether the
   `labelSelector` gained an expression nobody wrote.

   ```sh
   kubectl -n bw-mlk get deploy/web -o json \
     | jq '.spec.template.spec.affinity.podAntiAffinity.requiredDuringSchedulingIgnoredDuringExecution[0]'
   kubectl -n bw-mlk get pod -l app=web -o json \
     | jq -r '.items[] | "\(.metadata.name) hash=\(.metadata.labels["pod-template-hash"])"'
   kubectl -n bw-mlk get pod -l app=web -o json \
     | jq '.items[0].spec.affinity.podAntiAffinity.requiredDuringSchedulingIgnoredDuringExecution[0]'
   ```

5. Take whatever the previous step printed and submit it as a Pod of your own. This asks the only
   question that matters about the two rules: are they properties of the object, or properties of
   authorship?

   ```sh
   kubectl -n bw-mlk get pod -l app=web -o json | jq '{
     apiVersion:"v1", kind:"Pod",
     metadata:{name:"echo-back", labels:{app:"web"}},
     spec:{affinity:.items[0].spec.affinity,
           containers:[{name:"pause", image:"registry.k8s.io/pause:3.10"}]}}' > /tmp/bw-mlk-echo.json
   jq '.spec.affinity.podAntiAffinity.requiredDuringSchedulingIgnoredDuringExecution[0]' /tmp/bw-mlk-echo.json
   kubectl -n bw-mlk apply -f /tmp/bw-mlk-echo.json ; echo "exit=$?"
   ```

6. Apply the post's tenant block exactly as it is printed at its `:93-109`, wrapped in the smallest
   Pod that will carry it. Nothing has been altered: `matchLabelKeys` with no `labelSelector` in the
   affinity term, `tenant` in both places in the anti-affinity term.

   ```sh
   kubectl -n bw-mlk apply -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata:
     name: post-tenant
     labels:
       tenant: service-a
   spec:
     affinity:
       podAffinity:      # ensures the pods of this tenant land on the same node pool
         requiredDuringSchedulingIgnoredDuringExecution:
         - matchLabelKeys:
             - tenant
           topologyKey: node-pool
       podAntiAffinity:  # ensures only Pods from this tenant lands on the same node pool
         requiredDuringSchedulingIgnoredDuringExecution:
         - mismatchLabelKeys:
             - tenant
           labelSelector:
             matchExpressions:
             - key: tenant
               operator: Exists
           topologyKey: node-pool
     containers:
     - name: pause
       image: registry.k8s.io/pause:3.10
   YAML
   echo "exit=$?"
   ```

7. Now the version the concepts page printed instead, from `assign-pod-node.md:463-495`. One term
   gained `labelSelector: {}`; the other is unchanged from the post. Submit it and see whether one
   repair was enough.

   ```sh
   kubectl -n bw-mlk apply -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata:
     name: docs-tenant
     labels:
       tenant: tenant-a
   spec:
     affinity:
       podAffinity:
         requiredDuringSchedulingIgnoredDuringExecution:
         - matchLabelKeys:
             - tenant
           labelSelector: {}
           topologyKey: node-pool
       podAntiAffinity:
         requiredDuringSchedulingIgnoredDuringExecution:
         - mismatchLabelKeys:
           - tenant
           labelSelector:
             matchExpressions:
             - key: tenant
               operator: Exists
           topologyKey: node-pool
     containers:
     - name: pause
       image: registry.k8s.io/pause:3.10
   YAML
   echo "exit=$?"
   ```

8. Settle the `topologyKey` restriction. Clear away anything steps 6 and 7 may have left carrying a
   `tenant` label, give the node the label both examples assume exists, read the API server's
   admission plugin flags, and then submit a required anti-affinity term keyed on something other
   than `kubernetes.io/hostname`.

   ```sh
   kubectl -n bw-mlk delete pod post-tenant docs-tenant --ignore-not-found
   NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl label node "$NODE" node-pool=alpha --overwrite
   grep -o -- '--\(enable\|disable\)-admission-plugins=[^ ]*' /etc/kubernetes/manifests/kube-apiserver.yaml \
     || echo "neither admission-plugins flag is set; the defaults are in force"
   kubectl -n bw-mlk apply -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata:
     name: pool-keyed
     labels:
       tenant: service-b
   spec:
     affinity:
       podAntiAffinity:
         requiredDuringSchedulingIgnoredDuringExecution:
         - labelSelector:
             matchExpressions:
             - key: tenant
               operator: Exists
           topologyKey: node-pool
     containers:
     - name: pause
       image: registry.k8s.io/pause:3.10
   YAML
   kubectl -n bw-mlk get pod pool-keyed -o wide
   ```

9. Offline, on the pinned checkout, count what the archive and the tree actually say about these two
   fields. Do not guess at any of these numbers; read them.

   ```sh
   cd /path/to/kubernetes/website/content/en
   grep -rl 'matchLabelKeys' blog/_posts | sort
   grep -rl 'mismatchLabelKeys' . | sort
   grep -rn 'topologyKey: node-pool' docs
   grep -rn 'Kensei Nakada' blog/_posts | sort
   ```

10. Still offline, put the three field descriptions that govern this exercise beside each other —
    the same pair of rules stated three times — and then the two halves of the disagreement no
    command on this cluster can settle.

    ```sh
    cd /path/to/kubernetes/website/content/en
    sed -n '1949p;1953p' docs/reference/kubernetes-api/core/pod-v1.md | fold -s -w 100
    sed -n '2979p' docs/reference/kubernetes-api/core/pod-v1.md | fold -s -w 100
    sed -n '260,264p' docs/concepts/scheduling-eviction/assign-pod-node.md
    sed -n '308,315p' docs/concepts/scheduling-eviction/assign-pod-node.md
    sed -n '460,461p' docs/concepts/scheduling-eviction/assign-pod-node.md
    ```

**Expect**

Step 1 prints a v1.35 server against a v1.37 pin, so hold every line number lightly and trust the
cluster over the file when they differ. The two `kubectl explain` calls are the important part: the
field descriptions the server serves come from the same Go doc comments that generate `pod-v1.md`,
so you should read both prohibitions back off your own API server — the same key forbidden in both
places, and the keys field not settable without a selector. If the server's text omits either
sentence, write down which, because it means the rule you are about to test was documented after
this server was built.

Step 2 gives you the failure whole. The first `rollout status` returns cleanly with one Pod Running.
After `set env` the second one does not return: it sits until the 60-second timeout and exits
non-zero. `get pods` shows two Pods, one Running and one Pending, with different `pod-template-hash`
values, and the Pending one never moves. The events on it name the reason in the scheduler's own
words — look for `didn't match pod anti-affinity rules` against 0 of 1 available nodes. The
Deployment cannot remove the old Pod because `maxUnavailable` is 0, and cannot place the new one
because the old one holds the only domain. That is the post's `:21` bullet, running.

Step 3 is the same cluster, the same strategy, the same selector, and two more lines of YAML. Both
`rollout status` calls return zero, the second within a few seconds. `get rs` shows two ReplicaSets,
the older at 0 desired and the newer at 1 desired and 1 ready. Nothing about the cluster changed
between step 2 and step 3 — the fix is entirely in what the scheduler was asked to compare, and the
label it compares on is one the Deployment controller had already been writing on every Pod all
along.

Step 4 is the measurement the rest of the exercise stands on. The Deployment's term prints back
exactly as you wrote it. The Pod's term is the question. If the post's `:50` is literal, the Pod's
`labelSelector.matchExpressions` carries a second entry that no manifest in this exercise contains —
`key: pod-template-hash`, `operator: In`, one value, and that value is the hash printed beside the
Pod's name on the line above. The `matchLabelKeys` list is still there beside it; the merge adds, it
does not consume. If instead the Pod's term is identical to the Deployment's, then the merge happens
inside the scheduler and is never written down, and the post's word "translated" is describing a
computation rather than a stored object. Write down which you saw. Step 5 means different things in
each case.

Step 5 submits the object the cluster wrote. If step 4 showed the merge persisted, the JSON you just
built contains `pod-template-hash` in `matchLabelKeys` and `pod-template-hash` in the
`labelSelector` — which is precisely the shape `pod-v1.md:1949` calls forbidden. A rejection here is
the interesting outcome: it means the prohibition governs authorship and not the stored shape, and
that the API server routinely writes into etcd an object it would refuse from you. An acceptance is
also interesting, and means the sentence in the reference describes an intention that this version
does not enforce on this path. If step 4 showed no merge at all, the submission is a round trip and
tells you only that the term you wrote is valid, which you already knew.

Step 6 should fail, and the error is the point. Two rules are broken in one object: the
`podAffinity` term sets `matchLabelKeys` with no `labelSelector`, and the `podAntiAffinity` term has
`tenant` in `mismatchLabelKeys` and `tenant` in its `labelSelector`. Validation may report both or
may stop at the first; either way the message should name a field path under `spec.affinity`. This
manifest is the post's `:93-109` character for character, so a rejection here says the post shipped
a worked example that its own release could not apply. If the Pod is accepted, both sentences in
`pod-v1.md` are unenforced at 1.35 and this exercise has found a documentation defect instead of a
post defect — record it that way and carry it into step 7.

Step 7 separates the two rules. The concepts page added `labelSelector: {}` to the affinity term,
which satisfies the second rule exactly; the anti-affinity term it inherited from the post is
untouched. So if the first rule is enforced, this Pod is still rejected, and rejected on the
anti-affinity term alone. That is the finding: the page repaired one violation, kept the other, and
wrote a three-line comment at `assign-pod-node.md:488-490` explaining that the selector has to stay
because otherwise the Pod would be anti-affine to DaemonSet Pods too. Which leaves the use case in
an awkward place — the selector must name `tenant` to exclude Pods that lack it, and may not name
`tenant` because `mismatchLabelKeys` already does. If both step 6 and step 7 are accepted, none of
that holds and the two sentences in the reference are the thing to doubt.

Step 8 settles the `topologyKey` question with three readings. The delete is housekeeping: if steps
6 and 7 were rejected it removes nothing, and if they were accepted it clears two Pods carrying a
`tenant` label that would otherwise be counted by the anti-affinity term you are about to submit.
The node then takes the `node-pool` label without complaint, because a topology key is an ordinary
node label and Kubernetes has no opinion about which ones exist. The grep prints the API server's
admission flags — on a kubeadm-built cluster expect `--enable-admission-plugins=NodeRestriction` and
nothing else — and `LimitPodHardAntiAffinityTopology` is not in it, nor is it in the default-enabled
list that `kube-apiserver.md:531` prints in parentheses. So the restriction at
`assign-pod-node.md:361-364` is not in force here, the Pod is accepted, and it goes Running. The
page's own tenant example depends on exactly this: it keys required anti-affinity on `node-pool`,
which the same page says is limited to `kubernetes.io/hostname`.

Step 9 gives four counts, and none of them should be taken from this file without checking.
`matchLabelKeys` appears in five posts across the whole archive: two release announcements, the 2023
topology-spread post, this one, and the v1.33 announcement. `mismatchLabelKeys` appears in five
files under `content/en` and only five: this post, the v1.33 announcement, the concepts page, the
gate file, and the API reference — so outside the blog the field has exactly three homes.
`topologyKey: node-pool` appears on exactly two lines, both of them the concepts page's tenant
example. And six files name Kensei Nakada, five of them as an author credit, with the affiliation
changing from Mercari in the 2023 posts to Tetrate in this one and everything after it.

Step 10 is the reading, and it is best done with the five outputs on screen together. The two
`PodAffinityTerm` entries state the two rules twice, once per field, in the same words. The
`topologySpreadConstraints` entry states the same two rules a third time — capitalised
`MatchLabelKeys` and `LabelSelector`, "ANDed with labelSelector" where the affinity entries say
"merged with `labelSelector` as `key in (value)`", and with its feature gate named inline where the
affinity entries name none. Then the three passages from the concepts page. The self-affinity
paragraph guarantees a group of mutually affine Pods cannot deadlock; there is no such paragraph for
anti-affinity, and steps 2 and 3 are why there cannot be. And the two that disagree: a note near the
top of the section that says not to use inter-pod affinity above several hundred nodes, and, two
hundred lines below it, a pattern for partitioning a multi-tenant cluster by node pool which the
post it came from says to inject into every Pod with a mutating webhook. Both are the same file. One
node cannot arbitrate between them, because the cost the note describes is paid per node and this
cluster has one.

**Read on**

1. `docs/concepts/scheduling-eviction/assign-pod-node.md:381-495` — the two field sections whole,
   both worked examples included. This is the page the post sends you to at its `:155`, and it is
   the page that absorbed one of the post's two examples cleanly and the other one with a repair
   that does not go far enough. Read the comments as carefully as the YAML; three of them carry the
   reasoning the post never wrote down.

2. `docs/reference/kubernetes-api/core/pod-v1.md:1943-1966` — the whole `PodAffinityTerm` field
   table, six rows. Two of them state the rules this exercise tests; the `labelSelector` row at
   `:1945` states a third thing worth holding beside them, that a null selector matches no Pods at
   all, which is why the second rule exists.

3. `docs/reference/access-authn-authz/admission-controllers.md:495-502` and
   `docs/reference/command-line-tools-reference/kube-apiserver.md:531` — the admission controller
   that would make half of both tenant examples illegal, and the list of what is actually on by
   default. The second is a long single line; the names in parentheses are the defaults and the
   names after "Comma-delimited list of" are merely available.

4. [The walk beside the 2017 post on advanced
   scheduling](../2017/02-advanced-scheduling-in-kubernetes.md) — where this gate's ladder lives,
   along with the note on the concepts page that still calls the field beta-level while the gate
   record has it stable and locked. That exercise reads the same section of the same page for a
   different reason, and the two readings do not overlap.

5. [The walk beside the post that introduced
   PodTopologySpread](../2020/04-introducing-podtopologyspread.md) — the same field name under a
   different parent, with its own gate, a stay at beta long enough to need a second gate at 1.34 to
   make the merge explicit, and a step that reads the stored `labelSelector` off a
   spread-constrained Pod. Read it after this one and the contrast between the two code paths is the
   whole lesson.

**Teardown**

```sh
kubectl delete namespace bw-mlk --wait=true
NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
kubectl label node "$NODE" node-pool-
rm -f /tmp/bw-mlk-echo.json
kubectl get nodes -o jsonpath='{.items[0].metadata.labels}' | tr ',' '\n' | grep node-pool \
  || echo "node-pool label gone"
```

The node label is the part the namespace deletion cannot reach. `node-pool` is not a well-known
label and nothing in this repo's topologies sets it, so leaving it behind would make a later
exercise's node look like it belongs to a pool that does not exist. The last command is the check:
it should print the fallback line and nothing else.
