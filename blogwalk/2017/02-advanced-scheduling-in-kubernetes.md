<a id="advanced-scheduling-in-kubernetes"></a>
# Two of this post's four affinity examples cannot be applied, the word "slightly" hides the whole difference between a filter and a score, and the page that replaced it still tells you to switch off a field through a gate that is locked on

**Post** — [Advanced Scheduling in Kubernetes](https://kubernetes.io/blog/2017/03/advanced-scheduling-in-kubernetes/),
2017-03-31, Kubernetes v1.6 — Ian Lewis and David Oppenheimer of Google, part of *Five Days of
Kubernetes 1.6*. Four features, all moving to beta in the same release: node affinity/anti-affinity,
taints and tolerations, pod affinity/anti-affinity, and custom schedulers.

**As written** — the post opens by conceding the default scheduler is usually right, then states the
premise for everything that follows:

> Ultimately, you know much more about how your applications should be scheduled and deployed than
> Kubernetes ever will.

Node affinity is introduced as *"a generalization of the nodeSelector feature which has been in
Kubernetes since version 1.0"*, split into required and preferred. The required example is a pod
that must land in one GCE zone:

```yaml
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
            - key: "failure-domain.beta.kubernetes.io/zone"
              operator: In
              values: ["us-central1-a"]
```

Then the sentence this exercise is built on:

> You can prefer instead of require that pods are deployed to us-central1-a by slightly changing the
> pod spec to use preferredDuringSchedulingIgnoredDuringExecution:

```yaml
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
            - key: "failure-domain.beta.kubernetes.io/zone"
              operator: In
              values: ["us-central1-a"]
```

A third block does anti-affinity by swapping `In` for `NotIn`, and the operator list follows:
*"Valid operators you can use are In, NotIn, Exists, DoesNotExist. Gt, and Lt."* The post also names
a field that does not exist yet: *"There are future plans to offer
requiredDuringSchedulingRequiredDuringExecution which will evict pods from nodes as soon as they
don't satisfy the node affinity rule(s)."*

Taints and tolerations come next, with the example the reader's own cluster already runs — *"you
might want to mark your master node as schedulable only by Kubernetes system components"* — and one
command:

```
kubectl taint nodes node1 key=value:NoSchedule
```

The three effects are given in a parenthesis: *"The other taint effects are PreferNoSchedule, which
is the preferred version of NoSchedule, and NoExecute, which means any pods that are running on the
node when the taint is applied will be evicted unless they tolerate the taint."* Then an alpha
feature:

> In addition to moving taints and tolerations to _beta_ in Kubernetes 1.6, we have introduced an
> _alpha_ feature that uses taints and tolerations to allow you to customize how long a pod stays
> bound to a node when the node experiences a problem like a network partition instead of using the
> default five minutes.

Pod affinity gets a worked scenario — front-ends in service S1 talking to back-ends in S2, wanted in
one zone but not a zone chosen by hand — with the labels stated in prose as *"service=S2"* and
*"service=S1"*:

```yaml
affinity:
    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: service
            operator: In
            values: [“S1”]
        topologyKey: failure-domain.beta.kubernetes.io/zone
```

Anti-affinity is *"just make two changes to the snippet above -- change podAffinity to
podAntiAffinity and change topologyKey to kubernetes.io/hostname."*

Custom schedulers close the post. A pod carrying `schedulerName: my-scheduler` is ignored by the
default scheduler and *"will remain in a Pending state"* until something else claims it, and the
post supplies that something: a scheduler in Bash, which lists unscheduled pods with that
`schedulerName`, picks a node with `$RANDOM`, and POSTs a `Binding`.

```
curl --header "Content-Type:application/json" --request POST --data '{"apiVersion":"v1", "kind": "Binding", "metadata": {"name": "'$PODNAME'"}, "target": {"apiVersion": "v1", "kind": "Node", "name": "'$CHOSEN'"}}' http://$SERVER/api/v1/namespaces/default/pods/$PODNAME/binding/
```

The last paragraph is a warning worth keeping: the release notes have *"details about how to change
your configurations if you are already using the alpha version of one or more of these features
(this is required, as the move from alpha to beta is a breaking change for these features)"*.

**As it runs now** — start with the two YAML blocks the post presents as variants of each other,
because they are not variants. The pin's Pod API reference gives the required side a node selector
and the preferred side something else entirely:

> `preferredDuringSchedulingIgnoredDuringExecution` — *PreferredSchedulingTerm array* — The
> scheduler will prefer to schedule pods to nodes that satisfy the affinity expressions specified by
> this field, but it may choose a node that violates one or more of the expressions. [...] compute a
> sum by iterating through the elements of this field and adding "weight" to the sum if the node
> matches the corresponding matchExpressions; the node(s) with the highest sum are the most
> preferred.
>
> — `docs/reference/kubernetes-api/core/pod-v1.md:1814-1815`

A `PreferredSchedulingTerm` has exactly two fields and **both are required**: `preference`, which is
a `NodeSelectorTerm`, and `weight`, an integer (`pod-v1.md:2330-2334`). So the post's second block is
wrong three times over. It supplies a mapping where an array is required. It has no `preference`
wrapper. And it has no `weight` at all — which is not a cosmetic omission, because `weight` is the
entire output of the preferred form: the required form answers yes or no, and the preferred form
answers with a number that is summed across terms. The two forms do not differ by one field name.
One is a filter and the other is a scoring function, and the post's word for the distance between
them is *slightly*.

The fourth block, the pod affinity one, fails for a different reason. Its selector value is
`[“S1”]` — typographic quotation marks, not the straight ones used in all three node affinity
blocks. YAML has no special meaning for `“`, so the value is the four-character string `“S1”`, and
the pin's label rules leave no room for it:

> * must be 63 characters or less (can be empty),
> * unless empty, must begin and end with an alphanumeric character (`[a-z0-9A-Z]`),
> * could contain dashes (`-`), underscores (`_`), dots (`.`), and alphanumerics between.
>
> — `docs/concepts/overview/working-with-objects/labels.md:79-81`

A value that begins with `“` cannot be a label value, so the selector cannot be a label selector.
The post's prose says the label is `service=S1`; its manifest asks for something no object can
carry. Step 7 finds out which of the two problems the API server reports.

Three of the post's five documentation links are dead paths at the pin:
`/docs/user-guide/node-selection/` (the target of three separate links, each with its own anchor),
`/docs/user-guide/replicasets/`, and `/docs/admin/multiple-schedulers/` all have zero occurrences.
One of the three anchors is misspelled in the source as well —
`#taints-and-toleations-beta-feature` — so it was broken before the page moved. What replaced the
node-selection page is `docs/concepts/scheduling-eviction/assign-pod-node.md`, and it is where the
rest of this exercise goes.

The operator list has been split into two tables. Four operators work everywhere; the two the post
appends after a stray full stop do not:

> The following operators can only be used with `nodeAffinity`.
> [...]
> `Gt` and `Lt` operators will not work with non-integer values. If the given value doesn't parse as
> an integer, the Pod will fail to get scheduled. Also, `Gt` and `Lt` are not available for
> `podAffinity`.
>
> — `docs/concepts/scheduling-eviction/assign-pod-node.md:718-730`

Hold that sentence — *"can only be used with nodeAffinity"* — against the last row of the ladder
below, which is an alpha gate at v1.37 whose whole purpose is to add `Lt` and `Gt` to tolerations.
The page's restriction is true today and is scheduled to stop being true, and nothing on the page
says so.

`requiredDuringSchedulingRequiredDuringExecution`, the post's future plan, has zero occurrences at
the pin: nine years, no field.
[2016's StatefulSet exercise](../2016/14-statefulset-run-scale-stateful-applications-in-kubernetes.md)
found the same string typed into a live manifest and traces what happened to it there; what is new
here is only that the post promised it in the same release the annotation-based form was already on
its way out.

The taints half has aged better than the affinity half. The command is unchanged, the three effects
are unchanged, and the post's own master-node example is what `kubeadm` still does to your control
plane (`node-role.kubernetes.io/control-plane:NoSchedule`, at
`reference/setup-tools/kubeadm/implementation-details.md:438`). One phrase did not survive. The post
calls `PreferNoSchedule` *"the preferred version of NoSchedule"*, which reads as a recommendation;
the pin calls it *"a 'preference' or 'soft' version of `NoSchedule`"* (`taint-and-toleration.md:115`).
Same word, opposite senses, and only the second one is about the scheduler.

The post's alpha feature had the strangest fate of the four. It offered to let you customise the
five-minute eviction delay *"instead of using the default five minutes"* — and what shipped was the
mechanism that produces the default:

> This admission controller sets the default forgiveness toleration for pods to tolerate the taints
> `notready:NoExecute` and `unreachable:NoExecute` based on the k8s-apiserver input parameters
> `default-not-ready-toleration-seconds` and `default-unreachable-toleration-seconds` if the pods
> don't already have toleration for taints `node.kubernetes.io/not-ready:NoExecute` or
> `node.kubernetes.io/unreachable:NoExecute`. The default value [...] is 5 minutes.
>
> — `docs/reference/access-authn-authz/admission-controllers.md:234-241`

Both flags default to 300 (`kube-apiserver.md:465`, `:472`). So the five minutes the post describes
as *the default*, in contrast to the thing you could now configure, is now written into the spec of
every pod you create as two tolerations you did not ask for. Step 6 reads them back.

**The page that replaced the post now contradicts the feature-gate record about its own field.**
Pod affinity grew a `matchLabelKeys` field, and the page announcing it says this:

> The `matchLabelKeys` field is a beta-level field and is enabled by default in Kubernetes
> [current version]. When you want to disable it, you have to disable it explicitly via the
> `MatchLabelKeysInPodAffinity` feature gate.
>
> — `docs/concepts/scheduling-eviction/assign-pod-node.md:387-390`

The version is a shortcode that renders as whatever release the site is built for, so the note reads
as current no matter how old it is. Three things in it are wrong. The field is not beta-level:
`MatchLabelKeysInPodAffinity` went stable at v1.33, five releases before the pin. The instruction
cannot be followed: that stage carries `locked: true`, so the gate cannot be set to false. And the
line immediately above the note, at `:386`, is a source comment reading
`UPDATE THIS WHEN PROMOTING TO STABLE` — a reminder the author left in the published file, still
asking for the update that the gate record shows already happened. Two lines above that, the page's
own `feature-state` shortcode reads the same gate file and prints *stable*. The page states both
things at once, four lines apart, and the note that says *beta* is the one written in prose.

Custom schedulers changed most of all, and the change is in what `schedulerName` means. The post's
model is exclusion: the field's value is a name no built-in component answers to, so the pod stays
`Pending` until an outside process binds it. The pin's model is selection:

> To determine if a scheduler is responsible for scheduling a specific Pod, the `spec.schedulerName`
> field in a PodTemplate or Pod manifest must match the `schedulerName` field of the
> `KubeSchedulerProfile`.
>
> — `docs/tasks/extend-kubernetes/configure-multiple-schedulers.md:83-84`

The replacement page also declines the post's actual subject — *"A detailed description of how to
implement a scheduler is outside the scope of this document"* — and its worked example runs
`kube-scheduler` itself as the second scheduler, built from a `git clone` of `kubernetes/kubernetes`.
So the post ships a scheduler and no configuration story; the page ships a configuration story and
no scheduler.

And the API call the post's scheduler is built on is documented nowhere. `pod-v1.md` lists around
forty operations on Pod, including one other write-only subresource, `Create Eviction`
(`pod-v1.md:3389`), with full request and response schemas. There is no `Binding` entry, and
`kind: Binding` has zero occurrences anywhere under `docs/`. The endpoint still works — step 9 uses
it — but the pin's documentation set contains no description of the resource, no schema for it, and
no mention that it exists.

Two smaller notes on the zone label, whose deprecation
[2016's multi-zone exercise](../2016/02-building-highly-available-applications-using-kubernetes-new-multi-zone-clusters-aka-ubernetes-lite.md)
already covers in full. It survives in three files at the pin, and two of them are permission lists
rather than documentation: `NodeRestriction`'s allowed set for kubelet self-labelling
(`admission-controllers.md:617-618`, both entries carrying the parenthesis `(deprecated)`) and the
kubelet's `--node-labels` allowlist (`kubelet.md:644`). Deprecated since v1.17 and still explicitly
permitted for a node to write about itself.

**The diff, and why** — the post's four features had one thing in common in 2017 and nothing in
common after, and the split runs along whether the feature was a *field* or a *process*.

Node affinity, pod affinity and tolerations are fields. Fields accrete: `matchFields` arrived beside
`matchExpressions`, `namespaceSelector` beside `namespaces`, `matchLabelKeys` and
`mismatchLabelKeys` beside `labelSelector`, `Gt` and `Lt` beside the original four operators. Every
line of the post's required-form YAML still applies, unchanged, in v1.37. That is nine years of
compatibility on a beta API, and it is the strongest thing about this post.

Custom schedulers were a process, and processes get replaced rather than extended. The post's answer
to "the scheduler is not enough" was *write another one*, and it demonstrated that the barrier was
low by writing one in twenty lines of Bash. The project's answer became *configure the one you have*
— scheduling profiles, then the scheduling framework's plugin points — which is a better answer and
a strictly narrower one. You can now change how scheduling scores without writing a scheduler, and
you can no longer find out from the documentation how to write a scheduler. The `Binding` resource
is where that shows: it was never removed, because the framework is built on it, but it stopped being
something a reader was expected to reach for, and the reference dropped it while keeping `eviction`,
its exact structural twin. An undocumented API is not a deprecated API. It is an API whose audience
changed from *users* to *this project's own code*, with no record of the change.

Which brings the `matchLabelKeys` note into focus, because it is the same failure in miniature. Two
sources describe one field: a `stages:` list, which is data, and a prose note, which is not. The
shortcode reads the data and prints *stable*. The note beside it says *beta* and tells you to use a
switch the data marks locked. Nobody was wrong at the time of writing — the note was accurate for
two releases — and nobody is responsible for the moment it stopped being accurate, because the thing
that changed was the file the note does not read. The author saw this coming clearly enough to leave
`UPDATE THIS WHEN PROMOTING TO STABLE` in the source, and the reminder is now the oldest inaccurate
thing on the page.

The two broken manifests are worth separating from all of that, because they are not decay. The
preferred-affinity block was invalid on the day it was published: `PreferredSchedulingTerm` had
`preference` and `weight` in v1.6 exactly as it does now. The pod affinity block was invalid on the
day it was published too, for the entirely different reason that a word processor changed two
characters. What made both survivable was the word *slightly*: it invites the reader to read the
second block as the first block with one word changed, which is how a reader gets a scheduling
concept right while copying a manifest that cannot be applied.
[2016's StatefulSet exercise](../2016/14-statefulset-run-scale-stateful-applications-in-kubernetes.md)
shows a wrong field name surviving nine years because it sat where nothing checked it. Here nothing
checked it because nobody applied it.

**The ladder** — the gates behind the post's four features and their descendants.

## AffinityInAnnotations
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.6 – v1.7 |
| deprecated | — | — | v1.8 – v1.8 |

`removed: true`, plus `_build: {list: never, render: false}`, so the file exists and the site does
not publish it. This is the gate for the annotation form of pod affinity, and it is the breaking
change the post's closing paragraph gestures at without naming. It entered in v1.6 — the release this
post announces — **already off by default**, was deprecated for exactly one release, and never
reached beta. The `deprecated` stage carries no `defaultValue`, which is the template gap recorded
against 2016's authoring ticket rather than a new one.

## TaintBasedEvictions
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.6 – v1.12 |
| beta | `true` | — | v1.13 – v1.17 |
| stable | `true` | — | v1.18 – v1.20 |

`removed: true`. This is the post's alpha feature, and the dates match the post exactly: introduced
in v1.6, described as alpha, and it stayed alpha for seven releases before beta. Twelve releases from
introduction to stable, three more before the gate was deleted.

## TaintNodesByCondition
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.8 – v1.11 |
| beta | `true` | — | v1.12 – v1.16 |
| stable | `true` | — | v1.17 – v1.18 |

`removed: true`. The other half of the same idea, and it arrived two releases *after* the post
without being mentioned in it: node conditions expressed as taints rather than read separately by the
scheduler. Note that it reached stable at v1.17, one release before `TaintBasedEvictions` did, having
started two releases later.

## PodAffinityNamespaceSelector
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.21 – v1.21 |
| beta | `true` | — | v1.22 – v1.23 |
| stable | `true` | — | v1.24 – v1.25 |

`removed: true`. One release alpha, two beta, two stable, then deleted — five releases end to end,
against `TaintBasedEvictions`' fifteen. The post's pod affinity example has no namespace scoping of
any kind; this gate is what added the choice.

## MatchLabelKeysInPodAffinity
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.29 – v1.30 |
| beta | `true` | — | v1.31 – v1.32 |
| stable | `true` | `true` | v1.33 – |

Still present, and the only gate in this set with `locked: true`. This is the record that
`assign-pod-node.md:386-390` contradicts.

## TaintTolerationComparisonOperators
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.35 – |

Enables `Lt` and `Gt` for tolerations. Read it against `assign-pod-node.md:718`, *"The following
operators can only be used with `nodeAffinity`"*, and against the post's own list, which put those
two operators in a sentence about node affinity with a full stop in the middle of it.

Six gates, and the shape of the set is the point: the two that carry the post's own features are
`removed: true` after fifteen and eleven releases, the two that extended pod affinity are
`removed: true` after five and eight, and the two live ones were introduced in v1.29 and v1.35. The
features stopped needing gates. The gates for extending them did not stop being created.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), fresh. Two nodes is the minimum for
this exercise and the maximum it needs: a control plane at `10.10.10.130` and one worker at
`10.10.10.131`. Node affinity needs two nodes with different labels to prefer between, pod
anti-affinity needs two nodes to spread across, and the control plane arrives with the exact taint
the post gives as its motivating example. Bring both guests up with
[the five provision steps](../../strands/lab-topologies.md#provision), install Kubernetes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), join the worker,
and confirm both nodes are Ready before starting.

**Do**

1. Read the taint the installer already set, which is the post's own example running unprompted:

   ```sh
   kubectl get nodes -o custom-columns='NAME:.metadata.name,TAINTS:.spec.taints[*].key'
   kubectl get node -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.taints}{"\n"}{end}'
   kubectl get nodes --show-labels
   kubectl get nodes -o json | grep -c 'failure-domain.beta.kubernetes.io/zone'
   ```

   Match the taint you found against `implementation-details.md:438`. Then say which of the post's
   three sentences about tolerations explains why the control plane still runs `kube-apiserver`
   despite it, and check the last command's count against
   [2016's multi-zone exercise](../2016/02-building-highly-available-applications-using-kubernetes-new-multi-zone-clusters-aka-ubernetes-lite.md).

2. Apply the post's first block exactly as printed, with its deprecated label key:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: aff-required }
   spec:
     containers: [{ name: p, image: registry.k8s.io/pause:3.10 }]
     affinity:
       nodeAffinity:
         requiredDuringSchedulingIgnoredDuringExecution:
           nodeSelectorTerms:
             - matchExpressions:
               - key: "failure-domain.beta.kubernetes.io/zone"
                 operator: In
                 values: ["us-central1-a"]
   EOF
   kubectl get pod aff-required
   kubectl describe pod aff-required | tail -6
   ```

   The manifest is accepted and the pod does not schedule. Quote the scheduler's message. Then label
   the worker with the post's deprecated key and value, and report how long the pod takes to move:

   ```sh
   kubectl label node <worker> failure-domain.beta.kubernetes.io/zone=us-central1-a
   kubectl get pod aff-required -w   # Ctrl-C once it is Running
   ```

   The label is deprecated and the scheduler honoured it. Read `admission-controllers.md:617-618`
   and say what that list permits, and what it does not tell you about whether anything writes the
   label.

3. Apply the post's second block exactly as printed:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: aff-preferred }
   spec:
     containers: [{ name: p, image: registry.k8s.io/pause:3.10 }]
     affinity:
       nodeAffinity:
         preferredDuringSchedulingIgnoredDuringExecution:
           nodeSelectorTerms:
             - matchExpressions:
               - key: "failure-domain.beta.kubernetes.io/zone"
                 operator: In
                 values: ["us-central1-a"]
   EOF
   ```

   Record the error verbatim. Then write the form the API accepts and apply it:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: aff-preferred }
   spec:
     containers: [{ name: p, image: registry.k8s.io/pause:3.10 }]
     affinity:
       nodeAffinity:
         preferredDuringSchedulingIgnoredDuringExecution:
           - weight: 1
             preference:
               matchExpressions:
                 - key: "failure-domain.beta.kubernetes.io/zone"
                   operator: In
                   values: ["us-central1-a"]
   EOF
   kubectl get pod aff-preferred -o wide
   ```

   Now delete the label from the worker and create the same pod again under a second name. It should
   still schedule. State the difference in outcome between step 2 and this step when no node
   matches, and count how many edits it took to get from the post's block to this one.

4. Test the two operators the post appends to its list:

   ```sh
   kubectl label node <worker> blogwalk.example/cores=8
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: aff-gt }
   spec:
     containers: [{ name: p, image: registry.k8s.io/pause:3.10 }]
     affinity:
       nodeAffinity:
         requiredDuringSchedulingIgnoredDuringExecution:
           nodeSelectorTerms:
             - matchExpressions:
               - key: blogwalk.example/cores
                 operator: Gt
                 values: ["4"]
   EOF
   kubectl get pod aff-gt -o wide
   kubectl label node <worker> --overwrite blogwalk.example/cores=eight
   kubectl delete pod aff-gt --now
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: aff-gt2 }
   spec:
     containers: [{ name: p, image: registry.k8s.io/pause:3.10 }]
     affinity:
       nodeAffinity:
         requiredDuringSchedulingIgnoredDuringExecution:
           nodeSelectorTerms:
             - matchExpressions:
               - key: blogwalk.example/cores
                 operator: Gt
                 values: ["4"]
   EOF
   kubectl describe pod aff-gt2 | tail -5
   ```

   Compare the second outcome against `assign-pod-node.md:727-729`. Then say which of the post's six
   operators the ladder's last gate would move, and which sentence on the pin's page stops being true
   when that gate is on.

5. The post's taint command, unchanged, and its toleration:

   ```sh
   kubectl taint nodes <worker> key=value:NoSchedule
   kubectl run t1 --image=registry.k8s.io/pause:3.10 --restart=Never
   kubectl get pod t1 -o wide
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: t2 }
   spec:
     containers: [{ name: p, image: registry.k8s.io/pause:3.10 }]
     tolerations:
     - key: "key"
       operator: "Equal"
       value: "value"
       effect: "NoSchedule"
   EOF
   kubectl get pod t2 -o wide
   kubectl taint nodes <worker> key=value:NoSchedule-
   ```

   Both the taint and the toleration are copied from the post verbatim and both work. Then switch the
   effect and watch what the post promises:

   ```sh
   kubectl get pods -o wide
   kubectl taint nodes <worker> key=value:NoExecute
   kubectl get pods -o wide
   ```

   Say which pods went and which stayed, and use `PreferNoSchedule` to explain why the post's phrase
   *"the preferred version of NoSchedule"* is the one sentence in this half you should not repeat to
   anyone.

6. Read back the tolerations you did not write:

   ```sh
   kubectl taint nodes <worker> key=value:NoExecute-
   kubectl run plain --image=registry.k8s.io/pause:3.10 --restart=Never
   kubectl get pod plain -o jsonpath='{.spec.tolerations}{"\n"}' | tr ',' '\n'
   ```

   Two tolerations with a `tolerationSeconds` you never asked for. Name the admission controller from
   `admission-controllers.md:234-241`, give the two apiserver flags and their defaults, and then
   state the inversion: what the post offered as an alpha feature, in relation to what those
   tolerations now are.

7. Apply the post's pod affinity block exactly as printed, typographic quotes included. Type them, or
   copy them from the post — do not straighten them:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: pa-verbatim
     labels: { service: S2 }
   spec:
     containers: [{ name: p, image: registry.k8s.io/pause:3.10 }]
     affinity:
       podAffinity:
         requiredDuringSchedulingIgnoredDuringExecution:
         - labelSelector:
             matchExpressions:
             - key: service
               operator: In
               values: [“S1”]
           topologyKey: failure-domain.beta.kubernetes.io/zone
   EOF
   ```

   Record the message. Then decide, from `labels.md:79-81`, whether the value was rejected as a label
   value or never reached that check, and say which of the post's four YAML blocks are affected by
   this and which are not.

8. Build the anti-affinity case the post describes in prose, across the pair, and then meet the field
   the pin's page misdescribes:

   ```sh
   kubectl taint nodes <control-plane> node-role.kubernetes.io/control-plane:NoSchedule-
   kubectl apply -f - <<'EOF'
   apiVersion: apps/v1
   kind: Deployment
   metadata: { name: spread }
   spec:
     replicas: 3
     selector: { matchLabels: { service: S1 } }
     template:
       metadata: { labels: { service: S1 } }
       spec:
         containers: [{ name: p, image: registry.k8s.io/pause:3.10 }]
         affinity:
           podAntiAffinity:
             requiredDuringSchedulingIgnoredDuringExecution:
             - labelSelector:
                 matchExpressions:
                 - key: service
                   operator: In
                   values: ["S1"]
               topologyKey: kubernetes.io/hostname
   EOF
   kubectl get pods -l service=S1 -o wide
   ```

   Two nodes, three replicas, a hard rule per host. Say what the third pod is doing and why untainting
   the control plane was necessary for the first two. Then read
   `assign-pod-node.md:381-390` and attempt what it tells you to do:

   ```sh
   grep -o "enable-admission-plugins=[^ ]*" /etc/kubernetes/manifests/kube-apiserver.yaml
   grep -o "feature-gates=[^ ]*" /etc/kubernetes/manifests/kube-scheduler.yaml
   # then, on the control plane, add to kube-scheduler.yaml's command:
   #   --feature-gates=MatchLabelKeysInPodAffinity=false
   sudo crictl ps | grep scheduler
   sudo crictl logs $(sudo crictl ps -a --name kube-scheduler -q | head -1) 2>&1 | tail -5
   ```

   Report what the scheduler said. Then list the three things `assign-pod-node.md:386-390` states
   that the gate file does not support, and undo the edit.

9. The post's custom scheduler, exactly as designed. In one shell:

   ```sh
   kubectl proxy --port=8001
   ```

   In another, create the post's pod and confirm nothing takes it:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: nginx, labels: { app: nginx } }
   spec:
     schedulerName: my-scheduler
     containers: [{ name: nginx, image: nginx:1.10 }]
   EOF
   kubectl get pod nginx
   kubectl describe pod nginx | tail -4
   ```

   Note that `describe` shows no scheduler events at all — not a failure, an absence. Then bind it by
   hand with the post's own call, one pod rather than a loop:

   ```sh
   CHOSEN=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   curl -sS --header "Content-Type:application/json" --request POST \
     --data '{"apiVersion":"v1","kind":"Binding","metadata":{"name":"nginx"},"target":{"apiVersion":"v1","kind":"Node","name":"'$CHOSEN'"}}' \
     http://localhost:8001/api/v1/namespaces/default/pods/nginx/binding/
   kubectl get pod nginx -o wide
   ```

   It works. Now find the resource you just used in the pin's reference: search `pod-v1.md`'s
   Operations section for `Binding`, and search the whole `docs/` tree for `kind: Binding`. Report
   both counts, then find `Create Eviction` in the same list and say what distinguishes the two
   subresources apart from one being documented.

10. Close on what replaced the post's last section, without leaving the reference:
    read `configure-multiple-schedulers.md` and
    [the scheduler config API](https://kubernetes.io/docs/reference/config-api/kube-scheduler-config.v1/).
    Answer three questions. First: in the post's model, what does a pod's `schedulerName` tell you
    about which component will schedule it, and in the pin's model, what does it tell you? Second:
    the pin's page uses `kube-scheduler` itself as the second scheduler and declines to describe
    writing one — say what a reader who needs the post's section would do today. Third: your pod
    `nginx` is bound and running under `schedulerName: my-scheduler` with no such profile
    configured. Say whether that pod is now indistinguishable from a normally-scheduled pod, and how
    you would check.

**Expect**

```sh
kubectl get pods -o wide
kubectl get pod plain -o jsonpath='{range .spec.tolerations[*]}{.key}={.tolerationSeconds}{"\n"}{end}'
kubectl get pod nginx -o jsonpath='{.spec.schedulerName}|{.spec.nodeName}{"\n"}'
kubectl get nodes -o custom-columns='NAME:.metadata.name,TAINTS:.spec.taints[*].key'
```

A pod that scheduled on a deprecated label, a preferred-affinity pod that took three corrections to
apply, at least one `Pending` pod from the anti-affinity Deployment, two tolerations on a pod whose
manifest had none, and one pod bound by `curl` to a scheduler that does not exist.

By the end you should be able to say what `weight` does that the required form has no place for, name
the component that writes a five-minute toleration into every pod, give the two counts that show the
`Binding` resource is undocumented at the pin, and state the three claims
`assign-pod-node.md:386-390` makes that its own gate file refutes.

**Read on** — the pin's
[scheduling framework page](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/)
describes the extension points that replaced the post's approach. Read it and answer: at which of its
points would the post's random-node scheduler have been a plugin, and does the page anywhere tell you
that the mechanism the post used is still supported?

**Teardown** — `kubectl delete deploy spread; kubectl delete pod --all; kubectl label node <worker>
failure-domain.beta.kubernetes.io/zone- blogwalk.example/cores-` — then re-taint the control plane if
you plan to keep the cluster, and note why leaving it untainted is a change to the cluster the
installer built. Then [the teardown step](../../strands/lab-topologies.md#teardown).
