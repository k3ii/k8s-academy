<a id="kubernetes-statefulsets-daemonsets"></a>
# The two sentences this post is most emphatic about are still printed almost word for word on the task pages that replaced it, both were made false by the concept pages next door, and the symmetry it claims between the two controllers is now an asymmetry documented in two places that never mention each other

**Post** — [Kubernetes StatefulSets & DaemonSets Updates](https://kubernetes.io/blog/2017/09/kubernetes-statefulsets-daemonsets/),
2017-09-27, Kubernetes v1.7 — Janet Kuo (Google) and Kenneth Owens, whose front-matter affiliation
is his own name repeated: `Kenneth Owens (Kenneth Owens)`. The post is the second half of a pair
with the StatefulSet announcement of the previous December ([2016/14](../2016/14-statefulset-run-scale-stateful-applications-in-kubernetes.md)),
and it is the right post in this year to ask a narrow question: when a blog post is *absorbed* into
the documentation rather than left to rot, which of its sentences get carried, and who checks them
afterwards?

**As written** — two halves, one per controller, and the post is careful to claim they behave the
same way. It opens with what shipped:

> In Kubernetes 1.7, we enhanced the DaemonSet controller to track a history of revisions to the
> PodTemplateSpecs of DaemonSets. This allows the DaemonSet controller to roll back an update. We
> also added the [RollingUpdate] strategy to the [StatefulSet] API Object, and implemented revision
> history tracking for the StatefulSet controller. Additionally, we added the [Parallel] pod
> management policy to support stateful applications that require Pods with unique identities but
> not ordered Pod creation and termination.

The first half deploys a three-server ZooKeeper ensemble and a three-broker Kafka cluster from two
manifests hosted on a contributor's GitHub Pages site, then patches the Kafka StatefulSet's CPU
request four times to demonstrate `partition`: staged, canary, phased, complete. The mechanics of
the ZooKeeper manifest and the objects it creates belong to
[2016/14](../2016/14-statefulset-run-scale-stateful-applications-in-kubernetes.md), which walks the
whole rename; what is new here is the update path.

The paragraph that both halves hang on:

> StatefulSet updates are like DaemonSet updates in that they are both configured by setting the
> spec.updateStrategy of the corresponding API object. When the update strategy is set to OnDelete,
> the respective controllers will only create new Pods when a Pod in the StatefulSet or DaemonSet
> has been deleted. When the update strategy is set to RollingUpdate, the controllers will delete
> and recreate Pods when a modification is made to the spec.template field of a DaemonSet or
> StatefulSet. [...] Note that all updates are destructive, always requiring that each Pod in the
> DaemonSet or StatefulSet be destroyed and recreated. StatefulSet rolling updates differ from
> DaemonSet rolling updates in that Pod termination and creation is ordered and sequential.

So: two strategy values, identical semantics, one named difference (ordering). Then the failure
case, in the second half, after deliberately rolling out a broken image:

> Because the new pod never becomes available, the rollout is halted, preventing the invalid
> specification from propagating to more than one node. StatefulSet rolling updates implement the
> same behavior with respect to failed deployments. Unsuccessful updates are blocked until it
> corrected via roll back or by rolling forward with a specification.

And two sentences the post sets off deliberately, one per half. The first is the only thing in the
post marked as a thing you must not forget:

> Note that you need to enable the DaemonSet rolling update feature by explicitly setting DaemonSet
> .spec.updateStrategy.type to RollingUpdate.

The second closes the StatefulSet half, and is the only claim in the post asserted as design:

> By design, the StatefulSet controller does not delete any persistent volume claims (PVCs): the
> PVCs created for the ZooKeeper ensemble and the Kafka cluster must be manually deleted.

Hold those two. They are the sentences that survived.

**As it runs now** — start with the manifest, because it fails four separate times before any of
the above matters, and the four failures land in four different components.

The DaemonSet manifest is printed inside a heredoc:

> ```
> $ cat \>\> node-exporter-v0.13.yaml \<\<EOF
> ```

The backslashes are in the source, at line 642 of the post. Copy that line into a shell and `cat`
receives three arguments where two redirections and a heredoc were intended, and reports on each:

```
cat: >>: No such file or directory
cat: node-exporter-v0.13.yaml: No such file or directory
cat: <<EOF: No such file or directory
```

Nothing is written. Escape the metacharacters by hand, and the file appears — and does not parse.
The manifest's indentation puts the keys after `- image:` one level deeper than the key they are
siblings of:

> ```
>            containers:
>            - image: prom/node-exporter:v0.13.0
>                name: node-exporter
>                ports:
>                - containerPort: 9100
>                    hostPort: 9100
> ```

A YAML loader stops at the first of them with `mapping values are not allowed here`, pointing at
the colon after `name`. This is a *scanner* error, not a schema error: it happens before any
document structure exists, so `kubectl` never gets as far as talking to an API server. The same
fault repeats one level down, at `hostPort` under `- containerPort`.

Fix the indentation and the third failure is the API group. `apiVersion: extensions/v1beta1` — and
`docs/reference/using-api/deprecation-guide.md:321` records the removal: *"The **extensions/v1beta1**
and **apps/v1beta2** API versions of DaemonSet are no longer served as of v1.16."* Rewrite it as
`apps/v1` and the fourth failure arrives, from the same list, three lines down:

> * Notable changes:
>   * `spec.templateGeneration` is removed
>   * `spec.selector` is now required and immutable after creation; use the existing
>     template labels as the selector for seamless upgrades
>   * `spec.updateStrategy.type` now defaults to `RollingUpdate`
>     (the default in `extensions/v1beta1` was `OnDelete`)
>
> — `docs/reference/using-api/deprecation-guide.md:326-329`

The post's manifest has no `spec.selector`. Under `extensions/v1beta1` it did not need one; under
`apps/v1` the field is required, so the object is rejected by validation. `templateGeneration` has
exactly **one** occurrence in the whole corpus — the removal note above — so the field survives only
as its own obituary.

Read the third bullet again, though, because it is the finding this exercise is built on. The
default the post told you to set by hand *is now the default*. The post's one warning became
redundant somewhere between v1.9, when `apps/v1` became available, and v1.16, when the old group
stopped being served.

Now open the page that replaced the post's second half —
`docs/tasks/manage-daemon/update-daemon-set.md`, whose `reviewers:` field names one of this post's
two authors — and read fourteen lines of it in order:

> `RollingUpdate`: This is the default update strategy.
>
> — `:26`

> To enable the rolling update feature of a DaemonSet, you must set its
> `.spec.updateStrategy.type` to `RollingUpdate`.
>
> — `:34-35`

The post's sentence is still there, in the imperative, on the page that supersedes it, directly
beneath the sentence that makes it unnecessary. Neither sentence mentions the other.

And the page builds on it. The section after that instruction is a verification ritual:

> Check the update strategy of your DaemonSet, and make sure it's set to `RollingUpdate`
>
> — `:66-67`

> If the output isn't `RollingUpdate`, go back and modify the DaemonSet object or manifest
> accordingly.
>
> — `:86-87`

The command it gives is a `go-template` read of `.spec.updateStrategy.type` against a live object.
On a live object that field is never empty, because the apiserver defaults it, so the check has one
possible outcome unless you deliberately wrote `OnDelete`. The page also offers a client-side
variant against the manifest — and the manifest it ships,
`examples/controllers/fluentd-daemonset.yaml`, writes `updateStrategy: type: RollingUpdate` out
explicitly, so that variant passes too. The ritual is closed: the instruction, the check, and the
example all agree with each other and none of them agrees with `:26`.

The same page contradicts itself a second time, on a smaller point. Its description of
`RollingUpdate` promises:

> At most one pod of the DaemonSet will be running on each node during the whole update process.
>
> — `:28-30`

Twelve lines later it offers you `.spec.updateStrategy.rollingUpdate.maxSurge`, *"(defaults to 0)"*
(`:42-43`), whose entire purpose is to start the replacement Pod on the node before the old one is
killed. The promise holds only at the default. `maxSurge` reached the page unconditionally because
its gate is gone (see the ladder).

Then the failure case, which is where the post's symmetry claim breaks. The DaemonSet page:

> If the recent DaemonSet template update is broken, for example, the container is crash looping, or
> the container image doesn't exist (often due to a typo), DaemonSet rollout won't progress.
>
> To fix this, update the DaemonSet template again. New rollout won't be blocked by previous
> unhealthy rollouts.
>
> — `docs/tasks/manage-daemon/update-daemon-set.md:171-176`

That is the post's claim, honoured. Now the StatefulSet concept page, on the identical scenario:

> If you update the Pod template to a configuration that never becomes Running and Ready (for
> example, due to a bad binary or application-level configuration error), StatefulSet will stop the
> rollout and wait.
>
> If you update the Pod template to a configuration that never becomes Running and Ready (for
> example, due to a bad binary or application-level configuration error), StatefulSet will stop the
> rollout and wait.
>
> In this state, it's not enough to revert the Pod template to a good configuration.
>
> — `docs/concepts/workloads/controllers/statefulset.md:381-385`

The page attributes that to an open issue it links by number — `kubernetes/kubernetes#67250`, filed
in 2018 — and continues:

> StatefulSet will continue to wait for the broken Pod to become Ready (which never happens) before
> it will attempt to revert it back to the working configuration.
>
> After reverting the template, you must also delete any Pods that StatefulSet had already attempted
> to run with the bad configuration.
>
> — `docs/concepts/workloads/controllers/statefulset.md:386-393`

The post said the two controllers *"implement the same behavior with respect to failed
deployments"* and that unsuccessful updates are *"blocked until it corrected via roll back or by
rolling forward with a specification"*. For DaemonSets, rolling forward corrects it. For
StatefulSets, rolling forward does not, and the documentation says so while linking an issue that
is still open. Neither page references the other, and the section is titled *"Forced rollback"*,
which is the last place a reader following the post's DaemonSet half would look.

The StatefulSet page then contradicts *itself* about the same thing, sixty lines later, under a
heading that reads like the answer:

> ```bash
> # Rollback to a specific revision
> kubectl rollout undo statefulset/webapp --to-revision=3
> ```
>
> This will:
>
> * Apply the Pod template from revision 3
> * Create a new ControllerRevision with an updated revision number
>
> — `docs/concepts/workloads/controllers/statefulset.md:455-470`

Flat, unconditional, no caveat, no link back to `:381-393` — which says that applying a good Pod
template is precisely what is not sufficient. The revision-history machinery those lines describe
(`revisionHistoryLimit`, `--to-revision`, the roll-forward numbering) is walked for Deployments in
[2016/04](../2016/04-using-deployment-objects-with.md); what is new here is that the same page
carrying the procedure carries the reason it will not work.

Three more things moved under the post's feet.

*Two strategy values became three.* `statefulset.md:313` now reads *"There are three possible
values"*: `OnDelete`, `RollingUpdate`, and `Recreate`, which *"deletes all of the StatefulSet's Pods
before creating new Pods"* and *"incurs downtime for the duration of the update"* (`:322-331`,
`:395-415`). It is alpha and new in the release the pin sits on. The post's *"all updates are
destructive"* was an observation; `Recreate` makes destruction the point.

*One Pod at a time became a default.* `.spec.updateStrategy.rollingUpdate.maxUnavailable` for
StatefulSets — *"The default setting is 1"* (`:365`) — turns the post's *"The controller waits for
each updated Pod to be running and ready before updating the subsequent Pod"* into one setting of
several. The section carries `{{< feature-state for_k8s_version="v1.35" state="beta" >}}` written
out by hand rather than driven by the gate name, unlike the three other feature-state shortcodes on
the same page, plus a note: *"The `maxUnavailable` field is in Beta stage and it is enabled by
default"* (`:372`). Check that against the ladder below before believing it.

*Ordinals stopped starting at zero.* `.spec.ordinals.start` (`:178-188`) lets you assign Pods
ordinals from `start` through `start + replicas - 1`. Two other sections on the same page still
assume the old range. The `maxUnavailable` section says it *"applies to all Pods in the range `0` to
`replicas - 1`"* (`:367`). Worse, the partition section states two rules that cannot both hold once
`start` is non-zero:

> all Pods with an ordinal that is greater than or equal to the partition will be updated
>
> — `:348-350`

> If a StatefulSet's `.spec.updateStrategy.rollingUpdate.partition` is greater than its
> `.spec.replicas`, updates to its `.spec.template` will not be propagated to its Pods.
>
> — `:352-354`

Set `replicas: 3`, `ordinals.start: 5`, `partition: 4`. The ordinals are 5, 6 and 7. By the first
rule every Pod is greater than or equal to 4, so all three update. By the second rule 4 is greater
than 3, so none update. This is exactly the post's own staging technique — *"If you set the
partition to a number greater than or equal to the StatefulSet's spec.replicas [...] any subsequent
updates you perform to the StatefulSet's spec.template will be staged for roll out"* — and it is the
one sentence of the post's four-step demonstration that stops being reliable advice, silently, on
any StatefulSet with a non-zero start ordinal.

Now the second surviving sentence. The post's *"By design, the StatefulSet controller does not
delete any persistent volume claims"* was true when written and is a configurable default now:

> The optional `.spec.persistentVolumeClaimRetentionPolicy` field controls if and how PVCs are
> deleted during the lifecycle of a StatefulSet.
>
> — `docs/concepts/workloads/controllers/statefulset.md:511-512`

Two policies, `whenDeleted` and `whenScaled`, each `Delete` or `Retain`, with *"`Retain` (default)
[...] This is the behavior before this new feature."* So the post's design claim is now the name of
one setting. And the same page, in the sentence immediately after the field is introduced, still
says:

> You must enable the `StatefulSetAutoDeletePVC` [feature gate] on the API server and the controller
> manager to use this field.
>
> — `:512-514`

The gate has been on by default since v1.27 and stable since v1.32 (see the ladder). This is the
same shape as the `matchLabelKeys` note in [2017/02](02-advanced-scheduling-in-kubernetes.md) — a
live instruction about a gate that no longer needs touching — with one difference worth naming: that
gate is stable *and locked*, so its instruction is impossible to follow. This one is stable and
**not** locked, so you still can switch it off. The sentence is wrong about necessity, not about
possibility, which is a harder kind of wrong to notice.

Meanwhile the task page a reader would actually reach for still prints the post's rule with no
qualification at all. `docs/tasks/run-application/delete-stateful-set.md`, under `### Persistent
Volumes`:

> Deleting the Pods in a StatefulSet will not delete the associated volumes. This is to ensure that
> you have the chance to copy data off the volume before deleting it.
>
> — `:60-62`

`persistentVolumeClaimRetentionPolicy` has five occurrences in the corpus, in two files: the concept
page and the generated API reference. The page whose entire subject is deleting a StatefulSet is not
one of them. Neither is the ZooKeeper tutorial that inherited this post's example.

Finally, the flag the post used on every `apply`, and on which its whole rollback demonstration
depends — its `CHANGE-CAUSE` column is populated by nothing else. Three pages disagree about whether
`--record` exists:

| page | what it says |
|---|---|
| `docs/concepts/workloads/controllers/deployment.md:525` | *"In older versions of Kubernetes, you could use the `--record` flag [...] This flag is deprecated and will be removed in a future release."* |
| `docs/tasks/manage-daemon/rollback-daemon-set.md:47-49` | *"You may specify `--record=true` in `kubectl` to record the command executed in the change cause annotation."* |
| `docs/reference/labels-annotations-taints/_index.md:894,900` | *"It is populated when adding `--record` to a `kubectl` command"*, with example value `kubectl edit --record deployment foo` |

Past tense and deprecated on the Deployment page, which replaces it with three manual alternatives.
Present-tense instruction on the DaemonSet rollback page — the direct successor to this post's
second half. Present-tense definition in the annotation reference, which uses it in its own example.

Two small leftovers, for the same reason. `docs/tasks/manage-daemon/update-daemon-set.md:180-182`
still says *"clock skew between master and nodes"*, using a word the project retired for the
control plane; and the DaemonSet example the page ships still tolerates
`node-role.kubernetes.io/master` beside `node-role.kubernetes.io/control-plane`, with a comment
telling you to remove both if you don't want the DaemonSet on control-plane nodes. And nothing the
post ran survives by name: `node_exporter` and `node-exporter` have **zero** occurrences in the
corpus, `kow3ns` has zero, and the `gcr.io/google_containers` registry the Kafka commands pull from
survives in exactly two lines, both of them a `busybox` image in an unrelated ConfigMap task. One of
the post's own commands never worked at all: line 256 pulls
`gcr.io/google\_containers/kubnetes-kafka:1.0-10.2.1`, missing the `r` in `kubernetes`.

**The diff, and why** — this post did not go stale. It was **absorbed**, and the interesting
question is which sentences the absorption carried.

Compare the two halves of the corpus that took it in. The *concept* pages moved: `statefulset.md`
grew a third strategy value, a `maxUnavailable` field, a start ordinal, a PVC retention policy and
a forced-rollback warning, each of them a real change to what the controller does. The *task* pages
did not. `update-daemon-set.md` still opens with *"DaemonSet has two update strategy types"* and
still tells you to switch on a feature that is on. `delete-stateful-set.md` still states the 2017
PVC rule as a fact about the controller. `rollback-daemon-set.md` still recommends a flag another
page in the same tree calls deprecated.

That split is not carelessness, and it is not the same failure as
[2017/03](03-configuring-private-dns-zones-upstream-nameservers-kubernetes.md), where four JSON
documents were malformed from the day they were published because nothing in the pipeline could
object. Here everything is well-formed. The failure is structural: a *concept* page describes an
object, so when the object changes there is an obvious place to write the change down. A *task* page
describes a procedure, and a procedure that still completes successfully generates no signal that
anything beneath it moved. Every stale sentence found above is stale in exactly this way — the
instruction still works. Setting `updateStrategy.type: RollingUpdate` by hand is harmless. Deleting
PVCs by hand is harmless. `--record` may still populate the annotation. Following each of them
produces a working cluster and no complaint, which is why they have outlived the facts that made
them necessary by roughly eight years.

The post's own emphasis is what makes this legible. The two sentences it set off — the one warning
and the one *"by design"* — are the two it was most confident about, and they are precisely the two
that survived into the task pages unqualified. Confidence is what gets a sentence copied, and a
copied sentence has no link back to whatever made it true.

Then hold the DaemonSet and StatefulSet failure paragraphs side by side, because the post's
symmetry claim is the one place it was actually wrong, and being wrong is not the interesting part.
The post asserted parity because parity was the *design*: same field, same two values, same
semantics, one documented difference. What it could not have foreseen is which controller would get the
harder guarantee. `OrderedReady` means the StatefulSet controller must not touch Pod *N-1* until
Pod *N* is Ready, and that rule has no exception for "Pod *N* is Ready-impossible and you have since
fixed the template". So the ordering guarantee the post named as the *only* difference is the
mechanism that produced a second, much larger one. The documentation now records both halves of the
asymmetry accurately, on two pages, using different vocabulary (*"broken rollout"* against *"forced
rollback"*), with no cross-reference — so a reader who arrives via the post's promise of parity has
no path from one to the other.

And the two contradictions on the StatefulSet page itself, `:381-393` against `:455-470`, close the
argument. Both were written by someone with the facts. One describes the guarantee; the other
describes the command. Nobody read them together, because nothing makes you.

**The ladder** — five gates, one per table. `maxSurge` for DaemonSets, and every StatefulSet field
above that the post could not have written about:

## StatefulSetAutoDeletePVC
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.23 – v1.26 |
| beta | `true` | — | v1.27 – v1.31 |
| stable | `true` | — | v1.32 –  |

## StatefulSetStartOrdinal
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.26 – v1.26 |
| beta | `true` | — | v1.27 – v1.30 |
| stable | `true` | — | v1.31 –  |

## MaxUnavailableStatefulSet
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.24 – v1.34 |
| beta | `true` | — | v1.35.0 – v1.35.3 |
| beta | `false` | — | v1.35.4 – v1.36 |
| beta | `true` | — | v1.37 –  |

## StatefulSetRecreateStrategy
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.37 –  |

## DaemonSetUpdateSurge
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.21 – v1.21 |
| beta | `true` | — | v1.22 – v1.24 |
| stable | `true` | — | v1.25 – v1.26 |

`DaemonSetUpdateSurge`'s gate file carries `removed: true`, which is why `maxSurge` appears on
`update-daemon-set.md:42-43` with no feature-state stamp and no gate to enable — and why the
*"at most one pod [...] on each node"* promise at `:28-30` now has an unmarked exception.

`MaxUnavailableStatefulSet` is the only ladder in this year with a default that goes on, off, and on
again inside a single stage, and the only one whose stage boundaries fall on patch releases rather
than minors. Read it against the note at `statefulset.md:372` — *"in Beta stage and it is enabled by
default"* — which was false for the whole of v1.35.4 through v1.36 and is true again at the pin. The
page never named a version for that claim, and the hand-written `for_k8s_version="v1.35"` above it
names the release in which the claim was first true, not the release the page describes.

`StatefulSetRecreateStrategy` is alpha in one release, the pin's own. `StatefulSetAutoDeletePVC` and
`StatefulSetStartOrdinal` are both stable and neither is `locked`, which is the distinction the
*"You must enable"* sentence at `:512-514` fails on: not that the gate is unreachable, but that
reaching for it is no longer part of using the field.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair): a control-plane node at `10.10.10.130`
and one worker at `10.10.10.131`. Two nodes is the right size and not a compromise. A DaemonSet gets
exactly two Pods, which is the minimum at which *"preventing the invalid specification from
propagating to more than one node"* is an observable claim rather than a tautology, and
`lab-topologies.md` names this row for every DaemonSet-heavy module. The StatefulSet work needs three
replicas but not three nodes; none of the steps below uses a `volumeClaimTemplate`, so no
provisioner is required and [2017/01](01-dynamic-provisioning-and-storage-classes-kubernetes.md)'s
static-PV apparatus stays out of the way.

Provision with the five steps at [`#provision`](../../strands/lab-topologies.md#provision), then the
node baseline at
[`#node-baseline-steps`](../../strands/lab-topologies.md#node-baseline-steps), then
`ssh zain@10.10.10.130`. The control-plane node is tainted by default in this row, so the DaemonSet
below carries the control-plane toleration; without it you get one Pod, not two, and step 4 has
nothing to show.

**Do**

1. Write the post's DaemonSet manifest to a file the way the post tells you to — copy line 642
   verbatim, backslashes included, and paste the heredoc after it. Read what `cat` prints. Then
   escape by hand, save the body exactly as printed, and run
   `kubectl apply --dry-run=client -f node-exporter-v0.13.yaml`. Name the component that rejected it
   and the component that never saw it.

2. Correct only the indentation — leave `apiVersion: extensions/v1beta1` — and re-run the same
   `--dry-run=client`. Record the exact error text, then drop `--dry-run` and run it against the
   cluster and record that one too. The message has changed from the one in step 1. Which component
   produced the new one, and does `--dry-run=client` reach the cluster to get it? Answer from the
   two error texts before reading on.

3. Change `apiVersion` to `apps/v1` and apply. Read the error. Then add the minimum that makes it
   valid — `spec.selector.matchLabels` matching `spec.template.metadata.labels` — but **do not** add
   `updateStrategy`, and add a toleration for `node-role.kubernetes.io/control-plane` so both nodes
   get a Pod. Apply, then:

   ```
   kubectl get ds node-exporter -o go-template='{{.spec.updateStrategy.type}}{{"\n"}}'
   ```

   Compare the output against the post's warning and against
   `docs/tasks/manage-daemon/update-daemon-set.md:66-67`. What did the check establish?

4. Break the rollout the way the post does:
   `kubectl set image ds/node-exporter node-exporter=prom/node-exporter:bad`, then watch
   `kubectl get po -l app=node-exporter -o wide -w` and `kubectl get ds node-exporter`. How many
   nodes hold a working Pod, and how many hold a failing one? Which of the two numbers is the
   post's *"preventing the invalid specification from propagating to more than one node"*, and would
   you be able to tell if `maxUnavailable` were 2?

5. Roll forward, exactly as `update-daemon-set.md:175` prescribes: `kubectl set image` back to a
   real tag. Do not delete any Pod. Time how long the DaemonSet takes to reach `AVAILABLE` equal to
   `DESIRED`.

6. Now the same experiment on a StatefulSet. Create a three-replica StatefulSet with a headless
   Service, no `volumeClaimTemplates`, default `podManagementPolicy` and no `updateStrategy` — then
   read back `.spec.updateStrategy.type` and `.spec.podManagementPolicy`. Which of the two did the
   apiserver choose for you, and which of the two would have been different under `apps/v1beta1`?
   [2016/14](../2016/14-statefulset-run-scale-stateful-applications-in-kubernetes.md) has the
   sentence that records the change.

7. Break it the same way: set the image to a tag that does not exist. Watch which ordinal is
   affected and confirm the other two are untouched. Then roll *forward* to a good image — the
   step-5 fix that worked for the DaemonSet — and wait. Watch for at least two minutes. Then run
   `kubectl rollout undo statefulset/<name>` and wait again. Read
   `docs/concepts/workloads/controllers/statefulset.md:381-393` and
   `:455-470` in that order, and say which of the two describes what you just observed.

8. Unstick it by deleting the Pod stuck at the bad revision, and confirm the set converges. Then
   write down, in one sentence each, what the post claimed about failed updates and what the two
   controllers actually did.

9. Reproduce the post's staging demonstration and then break it. First the post's version: patch
   `partition` to 3 on a three-replica set, change the image, confirm nothing rolls. Then set
   `.spec.ordinals.start: 5` on a fresh three-replica set, patch `partition` to 4, change the image,
   and see which of `statefulset.md:348-350` and `:352-354` the controller obeyed. Predict before
   you look.

10. Delete a StatefulSet that has a `volumeClaimTemplate` — reuse the static PV apparatus from
    [2017/01](01-dynamic-provisioning-and-storage-classes-kubernetes.md) if you want a real claim, or
    just read the manifest — and check whether `.spec.persistentVolumeClaimRetentionPolicy` is set,
    what it defaults to, and whether the gate needed enabling. Then read
    `docs/tasks/run-application/delete-stateful-set.md:60-62` and
    `docs/concepts/workloads/controllers/statefulset.md:507-545`, and decide which page you would
    have found first if you had started from the post's closing sentence.

**Expect**

Step 1: three `No such file or directory` lines naming `>>`, the filename and `<<EOF`, and no file
created. After escaping, `kubectl` reports a YAML error citing a line and column, not a validation
error — the failing token is the colon after `name`, and the manifest never reaches an apiserver.
`--dry-run=client` was enough to produce it, because decoding the file precedes every other thing
`kubectl` does with it.

Step 2: the YAML error is gone and both commands now fail on the API group instead, naming the kind
and the unrecognised version. Record the wording rather than trusting this paragraph for it. The
thing to notice is that `--dry-run=client` produces that error too: a client dry run still resolves
the kind through the cluster's discovery endpoint, so it is not an offline check. Step 1's failure
was offline — the parse happens before any request — and this one is not. Two rejections, two
different distances from the cluster.

Step 3: rejected for the missing `spec.selector`. After you supply it, the `go-template` prints
`RollingUpdate` although you never wrote the field. The check at `:66-67` therefore establishes
nothing about your manifest — only that the object exists and the apiserver defaults its fields.

Step 4: one node's Pod goes to `ErrImagePull` or `ImagePullBackOff` and stays; the other node keeps
its working Pod indefinitely. `DESIRED` and `CURRENT` read 2, `READY` reads 1, `UP-TO-DATE` reads 1.
On two nodes with `maxUnavailable: 1` the halt is visible. With `maxUnavailable: 2` both nodes would
have gone at once and the post's sentence would have been false on this cluster — the guarantee is a
consequence of the default, not of the controller.

Step 5: the DaemonSet recovers with no manual deletion, within one image pull. `update-daemon-set.md`
is correct.

Step 6: `.spec.updateStrategy.type` reads `RollingUpdate` and `.spec.podManagementPolicy` reads
`OrderedReady`. Only the first would have differed under `apps/v1beta1`; `OrderedReady` was the
default then too, which is why the post's ZooKeeper manifest had to ask for `Parallel` explicitly
and its Kafka rollout is ordered without asking.

Step 7: the highest ordinal is deleted and its replacement never becomes Ready; the two lower
ordinals keep running the old revision. Rolling forward does **not** clear it — the set stays stuck
with the same Pod pending, because the controller is still waiting on that Pod before it will
consider ordinal *N-1*, and it will not replace a Pod it has not finished waiting for.
`kubectl rollout undo` reports success and changes nothing observable: it writes a new template,
which is the action `:385` says is insufficient. So `:381-393` describes what you saw and `:455-470`
describes what the command claimed. Both are on the same page.

Step 8: deleting the stuck Pod releases the rollout and the set converges to the good revision in
descending ordinal order. The one-sentence summaries should read roughly: the post claimed both
controllers recover by rolling forward; the DaemonSet does, and the StatefulSet needs a Pod deleted
by hand — an asymmetry that follows from the ordering guarantee the post named as the two
controllers' *only* difference.

Step 9: with ordinals starting at 0, the post's technique works exactly as printed — `partition: 3`
on three replicas stages the update and nothing rolls. With `ordinals.start: 5` and `partition: 4`,
`:348-350` wins: every ordinal is at or above the partition, so all three Pods update, and the
staging you asked for did not happen. No warning, no event, no rejected field. Write down what a
reader of `:352-354` alone would have predicted.

Step 10: the field is absent and defaults to `Retain` on both policies, matching the post exactly —
and the gate did not need enabling, so `:512-514` cost you nothing to ignore. The task page tells
you the volumes are safe and never mentions that this is a default you can change; the concept page
tells you the default and never mentions the task page. Starting from the post's closing sentence,
the search term is *delete*, which lands on the task page.

**Read on** — two questions the corpus answers and this exercise does not ask. What does the
`Recreate` strategy do to the `OrderedReady` guarantee, given that
`docs/concepts/workloads/controllers/statefulset.md:405-411` says deletion ignores the Pod management
policy but recreation obeys it? And why does
`docs/tasks/administer-cluster/use-cascading-deletion.md:58` carry an unresolved authoring note —
*"TODO: verify release after which the `--cascade` flag is switched to a string"* — in published
source, on the page that governs what happens to this post's ZooKeeper and Kafka Pods when their
StatefulSets are deleted? Compare it with the published `UPDATE THIS WHEN PROMOTING TO STABLE`
comment in [2017/02](02-advanced-scheduling-in-kubernetes.md).

**Teardown** — [`#teardown`](../../strands/lab-topologies.md#teardown).
