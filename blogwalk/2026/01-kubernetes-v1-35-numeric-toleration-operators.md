<a id="kubernetes-v1-35-numeric-toleration-operators"></a>

# The paragraph that explains `Lt` says the opposite of the definition two lines above it and of all four examples below it, four sentences claim that a toleration decides where a Pod may go, and the component that has to honour the eviction promise is missing from the pair the post names

**Post** — [Kubernetes v1.35: Extended Toleration Operators to Support Numeric Comparisons (Alpha)](https://kubernetes.io/blog/2026/01/05/kubernetes-v1-35-numeric-toleration-operators/),
2026-01-05.

306 lines, 12,513 bytes, the second post of 2026 and the year's first `walk`. One author, Heba
Elayoty of Microsoft, writing for SIG Scheduling. It belongs to the run of v1.35 announcements that
carries over into January, and it is the longest of the five: two thirds of the file is worked
examples, and most of the rest argues that the feature belongs on tolerations rather than on node
affinity.

**As written**

The post opens on a cost problem. Clusters mix on-demand and spot capacity; platform teams want a
safe default that keeps most workloads off the risky nodes while letting specific workloads opt in
against an explicit threshold — *"I can tolerate nodes with failure probability up to 5%"*. Taints
and tolerations cannot express that, because a toleration can only test a taint's value for equality
or for existence. The workarounds are discrete taint categories, an external admission controller,
or worse placement.

`TaintTolerationComparisonOperators`, alpha at v1.35, adds `Gt` and `Lt` to
`spec.tolerations[].operator`. The post defines them in a two-item list at `:47-48`: `Gt` matches
when the taint's numeric value is greater than the toleration's value, `Lt` when it is less. A note
at `:55` constrains the values to positive 64-bit integers with no leading zeros and rules out `0`
explicitly, and `:57` says the operators work with `NoSchedule`, `NoExecute` and `PreferNoSchedule`.

A section at `:33-41` answers the obvious objection — node affinity already has numeric operators —
with three arguments. Policy orientation: affinity is per-Pod and opt-out, taints are per-node and
opt-in, so taints give the safer default. Eviction semantics: affinity cannot evict, `NoExecute`
with `tolerationSeconds` can. Operational ergonomics: node-side policy matches the built-in pressure
taints.

Four worked examples follow. Spot protection taints two nodes `failure-probability=15` and `=2` and
gives a payment processor `Lt "5"` with `tolerationSeconds: 30`, and a batch job `Lt "20"`. GPU
tiering taints an A100 node `gpu-compute-score=1000` and a T4 node `=500`, and gives a training Pod
`Gt "800"` and an inference Pod `Gt "400"`. Cost tiering and disk IOPS are two more, written as YAML
fragments rather than whole objects. Three numbered instructions at `:253-275` tell you to enable
the gate on *"both your API server and scheduler"*, taint your nodes with `kubectl taint`, and write
the operator into a Pod spec. The roadmap at `:283-287` promises CEL expressions, autoscaler
integration, and beta then GA.

**As it runs now**

**The gate has one rung and it has not moved.** `TaintTolerationComparisonOperators.md` declares a
single stage: `alpha`, `defaultValue: false`, `fromVersion: "1.35"`, no end version. Two releases
after the post, at a pin whose newest Kubernetes is v1.37, the feature is exactly where the post
left it. The file's body is two lines and links one page, the tolerations concept page; it names no
components.

**The paragraph that explains `Lt` says the opposite of the definition two lines above it.** Post
`:48` is unambiguous: *"`Lt` (Less Than): The toleration matches if the taint's numeric value is
less than the toleration's value"*. Post `:50` then glosses it: *"Since tolerations allow
scheduling, the pod can run on nodes where the taint value is greater than the toleration value.
Think of it as: 'I tolerate nodes that are above my minimum requirements'."* That is the `Gt` rule,
written under the `Lt` heading, and the mnemonic offered for it is the `Gt` mnemonic. The pin sides
with the definition: `taint-and-toleration.md:186-187` says `Gt` matches when the taint value is
greater than the toleration value and `Lt` when it is less.

**All four of the post's `Lt` uses read it the other way from its own gloss.** The payment processor
with `Lt "5"` is described at `:115` as landing on the node tainted `2` and not the one tainted
`15`; the batch job with `Lt "20"` at `:135` tolerates *"failure probability up to 20%"*; the
cost-tiering fragment with `Lt "100"` at `:233` schedules *"on nodes costing less than $100/hour"*;
and the third numbered instruction at `:271-274` writes `Lt "1"`. Every one of them is the
definition list's rule. Only the gloss disagrees, and it is the sentence a reader stops at because
it is the one offering to explain.

**Four sentences claim that a toleration decides where a Pod may go.** `:115` says the payment Pod
will *only* schedule on nodes with `failure-probability` less than 5; `:186` says the training Pod
only schedules on nodes with compute scores greater than 800; `:233` says the batch job will
schedule on cheap nodes *"but avoid more expensive nodes"*; `:247` says the disk-IOPS Pod only
schedules where the value exceeds 3000. A toleration does none of that. The pin states the direction
plainly at `:247-248` — taints and tolerations *"are a flexible way to steer pods away from nodes"*
— and the dedicated-nodes bullet at `:250-259` spells out the consequence: if you want Pods to use
the tainted nodes *and* only those nodes, you must additionally label the nodes and add a node
affinity. On any cluster with one untainted node, all four sentences are false.

**And the post already knows this, one section earlier.** The rationale at `:37` is the correct
statement: *"Taints invert control — nodes declare their risk level, and only pods with matching
tolerations may land there"*. Matching tolerations *may* land there; nothing says they must, and
nothing stops them landing elsewhere. The argument for tolerations over node affinity and the four
examples of tolerations doing node affinity's job are in the same document, four paragraphs apart.

**The pinned page's matching rule names two operators, a hundred lines above the section that adds
two more.** `taint-and-toleration.md:80-83` still reads: *"A toleration 'matches' a taint if the
keys are the same and the effects are the same, and: the `operator` is `Exists` ... or the
`operator` is `Equal` and the values should be equal."* The numeric section that contradicts it
starts at `:178` on the same page. Nothing at `:80-83` signals that the list is incomplete, and
nothing at `:178` says it is amending a rule stated earlier. This is the pinned documentation
disagreeing with itself inside one file.

**"Positive" against "signed".** Post `:55` says the values *"must be positive 64-bit integers
without leading zeros"* and rules out `"0"` by name. The pin's note at `:226-227` says *"both the
toleration and taint values must be valid signed 64-bit integers (zero leading numbers (e.g.,
"0550") are not allowed)"*. The two agree about leading zeros and disagree about sign, and neither
repeats the other's claim: the pin never says `0` is forbidden, the post never says negatives are
allowed. One of them describes the validation that shipped in v1.35.

**"Signed" is unreachable on the taint side, and only one of the two API reference pages says why.**
A negative taint value has to survive node validation before any toleration can compare against it,
and a taint value is a label value, which may not begin with `-`. The pin records that constraint
for device taints and not for node taints: `resource-slice-v1.md:406` says the device taint key
*"Must be a label name"* and `:414` says the value *"Must be a label value"*, while `node-v1.md:562`
and `:570` carry the same two sentences with both clauses removed — *"Required. The taint key to be
applied to a node."* and *"The taint value corresponding to the taint key."* Same struct, same
fields, same generator, one page constrained and the other not. The label-value rule itself is
quoted in full by [the 2017 advanced scheduling
row](../2017/02-advanced-scheduling-in-kubernetes.md) and is not re-derived here.

**Only one side of the comparison is validated at all.** The note at `:192-198` is explicit: the API
server validates that a *toleration's* values are valid integers, taint values on nodes are not
validated at registration time, and a node carrying a non-numeric taint value simply fails to match
— the example given is `servicelevel.organization.example/agreed-service-level=high:NoSchedule`. So
a typo on the node side produces no error anywhere; it produces a Pod that will not schedule and a
taint that looks correct. The post has no counterpart to this note, and its own instructions put the
human on the node side.

**The other taint system in the same pin did not get the operators.** Devices carry taints too, and
tolerations for them are declared on a ResourceClaim. `resource-claim-v1.md:475` describes that
field: *"Operator represents a key's relationship to the value. Valid operators are Exists and
Equal. Defaults to Equal."* No `Gt`, no `Lt`, no enum values for them. The two systems sit on the
same concept page — `taint-and-toleration.md:399-405` is the device-taints section, 221 lines below
the numeric-operators section — and neither says that the new operators stop at the node boundary.
Device taints and tolerations belong to [the 2025 DRA
row](../2025/08-kubernetes-v1-34-dra-updates.md); what is noted here is only which of the two taint
vocabularies grew.

**`PreferNoSchedule` acquires a behaviour the post does not state.** Post `:57` says the operators
*"work with all taint effects"* and stops. The pin's note goes further at `:230-232`: for
`PreferNoSchedule` with numeric operators, a Pod whose toleration does not satisfy the comparison
gets the node a lower priority *"but may still schedule there if no better options exist"*. That is
the soft effect behaving as a soft effect, but it is the one combination where a failed numeric
comparison does not keep a Pod off a node, and it is the combination a reader of the post would
assume behaves like the other two.

**The pin's warning is about switching the gate off, and the post has no counterpart to it.**
`:235-243` is a four-item warning: before disabling `TaintTolerationComparisonOperators`, identify
every workload using `Gt` or `Lt` *"to avoid controller hot-loops"*, rewrite those templates to
`Equal` or `Exists`, delete pending Pods that use the operators, and watch `apiserver_request_total`
for spikes in validation errors. An alpha gate is off by default, so every cluster that has the
feature turned it on by hand and can turn it off by hand; the post's three numbered instructions
cover only the on direction.

**The component that has to honour the eviction promise is missing from the pair the post names.**
The first numbered instruction at `:253-257` says to enable the gate on *"both your API server and
scheduler"*. The API server validates the toleration and the scheduler matches it at placement time,
so that pair is enough to place a Pod. It is not enough to evict one. The pin records at `:360-363`
that taint-based eviction moved out of the node controller after 1.29 into a separate component,
`taint-eviction-controller`, which runs inside kube-controller-manager and can be switched off with
`--controllers=-taint-eviction-controller`. Example 1's entire payoff — *"if a node's SLA degrades
... the pod gets 30 seconds to gracefully terminate before forced eviction"* at `:115` — is that
component's work, and the component is not on the list.

**The pin's worked example is a `Gt` and the post's flagship is an `Lt`.** The concept page's
example at `:202-221` taints `node1` with
`servicelevel.organization.example/agreed-service-level=950` and tolerates it with `Gt "900"`; the
one shipped manifest, `examples/pods/pod-with-numeric-toleration.yaml`, is that same `Gt "900"`
toleration on an `nginx` Pod. The `Lt` case gets four lines of YAML and no narrative. The post
inverts the weighting: `Lt` carries the spot-instance story that opens the piece, and `Gt` is the
GPU example in the middle.

**Not one of the post's taint keys reaches the documentation.** `failure-probability`,
`gpu-compute-score`, `cost-per-hour` and `disk-iops` have zero occurrences under `docs`. The key the
pin uses instead, `servicelevel.organization.example/agreed-service-level`, has three, all in
`taint-and-toleration.md` — it is prefixed with a reserved-looking example domain and is the kind of
key the documentation's own label conventions steer you towards. The post's four are bare keys with
no prefix at all.

**Every complete Pod manifest the post prints names an image that does not exist, and half its
examples are not manifests at all.** `payment-app:v1`, `batch-worker:v1`, `ml-trainer:v1` and
`ml-inference:v1` are placeholders; two of them also request `nvidia.com/gpu: 1`. Example 3 at
`:215-221` and `:225-231`, Example 4 at `:239-245`, and the third numbered instruction at `:268-275`
are fragments — a bare `spec:` with taints, a bare `tolerations:` list — with no `apiVersion` and no
`kind`. So of the eleven YAML blocks the post prints, four apply and then sit in `ImagePullBackOff`,
four cannot be applied at all, and the remaining three are Node objects carrying nothing but
`spec.taints`, which is its own problem.

**Three hard line breaks in the pinned section were typed as trailing whitespace.**
`taint-and-toleration.md:210`, `:211` and `:212` each end with two spaces, inside the three-line
explanation of why `950 > 900` matches. They are the only trailing-whitespace lines in the file, and
they are consecutive: one paragraph, written by someone who wanted line breaks and reached for the
older of markdown's two ways to get them.

**The operators reach three files and stop.** The string `Gt` occurs four times in
`assign-pod-node.md`, seven times in `taint-and-toleration.md` and once in the gate file; `Lt`
occurs four, six and once. No other file under `docs` mentions either. Two of those three files are
in the same directory, `docs/concepts/scheduling-eviction/`, and one of them says the operators
belong to node affinity alone — the sentence at `assign-pod-node.md:718`, which [the 2017 advanced
scheduling row](../2017/02-advanced-scheduling-in-kubernetes.md) reads against this gate's ladder.
What that row could not yet read it against is the sibling page in its own directory, which by the
pin documents the operators for tolerations in a section with its own heading anchor.

**Both of the post's two documentation links resolve.** `:304` points at
`/docs/concepts/scheduling-eviction/taint-and-toleration/` and `:305` at that page's
`#numeric-comparison-operators` fragment, which exists because the heading at `:178` was written
with an explicit id — `## Numeric comparison operators {#numeric-comparison-operators}` — rather
than left to Hugo. For a walk that has spent twelve years finding dead fragments, a post that hands
you two live ones is worth the sentence.

**What this exercise does not cover, and where it lives**

Node affinity's own `Gt` and `Lt` — the operator tables at `assign-pod-node.md:715-730`, the
sentence that restricts them to `nodeAffinity`, and the note that they are unavailable for
`podAffinity` — belong to [the 2017 advanced scheduling
row](../2017/02-advanced-scheduling-in-kubernetes.md). That row also prints this gate's ladder for
its own purpose, quotes the label-value syntax rule in full, and settles what `PreferNoSchedule`
means. This exercise cites all four and re-derives none of them.

Inter-pod affinity, `matchLabelKeys`, and what the same concept page forbids you to write belong to
[the 2024 matchLabelKeys row](../2024/08-matchlabelkeys-podaffinity.md), which reads
`assign-pod-node.md:260-495` closely. Pod topology spread — the other way to express placement
against a continuous property — is [the 2020 PodTopologySpread
row](../2020/04-introducing-podtopologyspread.md)'s.

Device taints and device tolerations, the ResourceSlice and DeviceTaintRule objects behind them, and
the DRA gates that carry them are [the 2025 DRA row](../2025/08-kubernetes-v1-34-dra-updates.md)'s.
This exercise reads exactly two lines of that API — the operator field at `resource-claim-v1.md:475`
and the value constraint at `resource-slice-v1.md:414` — to establish which taint vocabulary the new
operators reached, and nothing else.

Taint-based eviction as a subject — the built-in condition taints, the `out-of-service` taint a
human applies to a dead node, and the force-deletion path that follows — is [the 2022 non-graceful
node shutdown row](../2022/03-kubernetes-1-24-non-graceful-node-shutdown-alpha.md)'s. Step 6 here
uses eviction only as an instrument, to find out whether a numeric toleration is honoured by a
component the post never mentions.

**The diff, and why**

**Wrong when it was published.** The gloss on `Lt` at `:50` was wrong on the day it went up, and so
were the four sentences that give a toleration the power to exclude. Neither is a break: the pinned
concept section documenting the same feature was written for the same release, and it says the
opposite of the gloss in one line and the opposite of the exclusion claims in a bullet that has been
on the page for years. Nothing changed underneath the post. The post and the reference disagreed
from the start, about the two things a reader most needs to get right.

**Still right.** The definition list at `:47-48` matches `taint-and-toleration.md:186-187` word for
word in substance. The gate name is right, the field is right, the three effects are right, the
leading-zero rule is right, and the two documentation links at the foot of the post both resolve,
fragment included. The feature exists, does what the list says, and is reachable exactly the way the
post says it is.

**Overtaken by stasis.** Two releases on, `TaintTolerationComparisonOperators` is still alpha and
still `defaultValue: false`, with no end version on its only rung. The roadmap at `:283-287`
promised beta and then GA; what shipped in the interval was v1.36 and v1.37, neither of which
touched the gate. Everything the post tells you to do, you still have to do — by hand, on two
components, on a cluster you are willing to restart. The instruction did not become unnecessary the
way an absorbed feature's does; it just stopped being temporary.

**Never absorbed.** The post's real contribution is the argument at `:33-41` for why a threshold
belongs on the node rather than in every Pod, and none of it reached the documentation. The pin's
section is 66 lines: two bullets of semantics, an integer rule, two notes, one worked example with
an abstract SLA key, and a warning about switching the gate off. There is no spot capacity, no GPU
tier, no cost per hour, no comparison with node affinity, and no statement of what problem the
operators are for. A reader who arrives at `:178` from the feature-gate index learns what the
operators do and never learns why anyone wanted them.

**The ladder**

One gate, one rung, and the shortest ladder this walk has printed.

`TaintTolerationComparisonOperators`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.35 – |

The file declares no `removed`, no `former_titles` and no second stage. Its body is two lines and
points at one page. Read this row beside [the 2017 advanced scheduling
row](../2017/02-advanced-scheduling-in-kubernetes.md), which prints the same single rung as the last
entry in a set of six and uses it to date a restriction on the node-affinity page that is scheduled
to stop being true. What that row could not know from its own post is that the restriction has
already stopped being written as though it held: the tolerations page documents the operators, with
their own heading, their own anchor and their own worked example, while the affinity page still says
they belong to node affinity alone. The gate being alpha is what lets both pages be in the tree at
once without either being a lie.

The lab matters here in a way it usually does not. The clusters run v1.35, which is the release the
post announces and the first release in which the gate exists. Every earlier exercise that turned on
an alpha gate was reaching back from a pin two releases newer; this one is standing exactly where
the post stood. Whatever the v1.35 binaries do with a negative value or a zero is the behaviour the
post was describing, not a later revision of it.

**Topology** — [`workhorse`](../../strands/lab-topologies.md#workhorse), fresh: a control plane at
`10.10.10.140` and two workers at `10.10.10.141`–`.142`, one core each. Two workers is the minimum
that makes the central finding visible. A toleration that cannot exclude only proves it cannot
exclude when there is somewhere else for the Pod to go, and a numeric comparison that picks one node
over another needs two nodes carrying different values of the same taint key. The control plane is
where both edited manifests live, so it has to be a real kubeadm node and not a single-binary
distribution. Bring the three guests up with [the provisioning
recipe](../../strands/lab-topologies.md#provision) and take each through [the node
baseline](../../strands/lab-topologies.md#node-baseline-steps). Derive the worker names from
`kubectl get nodes` rather than typing them.

**Do**

1. Establish where the cluster stands before opening the post. The gate is alpha and off, so the
   interesting question is what a v1.35 API server says about operators it will not accept:

   ```sh
   mkdir -p /tmp/bw-tolerations
   kubectl version -o json | grep -i gitversion
   kubectl get nodes -o wide
   kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.taints}{"\n"}{end}'
   kubectl explain pod.spec.tolerations.operator
   ssh zain@10.10.10.140 "sudo grep -n feature-gates \
     /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/manifests/kube-scheduler.yaml" \
     || echo "neither manifest carries a feature-gates flag"
   ```

   Read `kubectl explain` against `docs/reference/kubernetes-api/definitions/toleration-v1.md:48`,
   which is generated from v1.37 and says *"Valid operators are Exists, Equal, Lt, and Gt. Defaults
   to Equal ... Lt and Gt perform numeric comparisons (requires feature gate
   TaintTolerationComparisonOperators)"*. Record whether the v1.35 server's own schema says the same
   thing, and whether it mentions the gate.

2. Submit the post's flagship Pod with the gate off, and the pin's sample beside it. The image is a
   placeholder in the post, so substitute the house image and say so; nothing else changes:

   ```sh
   cd /tmp/bw-tolerations
   cat > payment.yaml <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: payment-processor
   spec:
     tolerations:
     - key: "failure-probability"
       operator: "Lt"
       value: "5"
       effect: "NoExecute"
       tolerationSeconds: 30
     containers:
     - name: app
       image: registry.k8s.io/e2e-test-images/agnhost:2.53
       args: ["pause"]
   EOF
   cat > sla.yaml <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: nginx-numeric-toleration
     labels:
       env: test
   spec:
     containers:
       - name: nginx
         image: registry.k8s.io/e2e-test-images/agnhost:2.53
         args: ["pause"]
     tolerations:
       - key: "servicelevel.organization.example/agreed-service-level"
         operator: "Gt"
         value: "900"
         effect: "NoSchedule"
   EOF
   kubectl apply -f payment.yaml; kubectl apply -f sla.yaml
   ```

   Both are the same shape as `examples/pods/pod-with-numeric-toleration.yaml`. Record the exact
   message. An alpha field that is off is normally dropped rather than rejected; an alpha *enum
   value* usually cannot be, because there is nothing to drop it to. Which of the two happened here
   decides how a cluster operator finds out the gate is off.

3. Apply the post's Node blocks exactly as it prints them, then do the same thing the way the pin
   does it, and compare what each leaves behind:

   ```sh
   cd /tmp/bw-tolerations
   WK=$(kubectl get nodes -l '!node-role.kubernetes.io/control-plane' -o name | cut -d/ -f2)
   W1=$(echo "$WK" | sed -n 1p); W2=$(echo "$WK" | sed -n 2p); echo "$W1 $W2"
   kubectl get node "$W1" -o yaml > w1-before.yaml
   cat > node-spot.yaml <<EOF
   apiVersion: v1
   kind: Node
   metadata:
     name: $W1
   spec:
     taints:
     - key: "failure-probability"
       value: "15"
       effect: "NoExecute"
   EOF
   kubectl apply -f node-spot.yaml
   kubectl get node "$W1" -o yaml > w1-after.yaml
   diff w1-before.yaml w1-after.yaml | head -40
   kubectl taint nodes "$W2" failure-probability=2:NoExecute
   kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.taints}{"\n"}{end}'
   ```

   `kubectl apply` on an object the kubelet also owns is not the same operation as `kubectl taint`.
   Say which fields the diff shows moving, whether the taint survived, and whether anything else in
   `spec` did. The post prints the Node block as if it were the instruction; the pin's example at
   `taint-and-toleration.md:202-204` prints a `kubectl taint` line instead.

4. Enable the gate on the two components the post names, and only those two. Back both manifests up
   first; the control plane restarts twice:

   ```sh
   ssh zain@10.10.10.140 "sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/bw-apiserver.yaml.bak \
     && sudo cp /etc/kubernetes/manifests/kube-scheduler.yaml /tmp/bw-scheduler.yaml.bak \
     && sudo sed -i '/- kube-apiserver/a\\    - --feature-gates=TaintTolerationComparisonOperators=true' \
          /etc/kubernetes/manifests/kube-apiserver.yaml \
     && sudo sed -i '/- kube-scheduler/a\\    - --feature-gates=TaintTolerationComparisonOperators=true' \
          /etc/kubernetes/manifests/kube-scheduler.yaml"
   until kubectl version >/dev/null 2>&1; do sleep 5; done
   kubectl -n kube-system get pods -l tier=control-plane
   kubectl explain pod.spec.tolerations.operator
   ```

   Deliberately leave kube-controller-manager alone: the post's list has two components on it and
   step 6 is about what the third one does. Confirm both edited Pods came back before continuing,
   and say whether `kubectl explain` changed.

5. Remove every taint, then submit the payment Pod again. This is the sentence at `:115` under test
   — *"This pod will only schedule on nodes with `failure-probability` less than 5"* — on a cluster
   where no node has that taint at all:

   ```sh
   cd /tmp/bw-tolerations
   kubectl taint nodes --all failure-probability- 2>/dev/null || true
   kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.taints}{"\n"}{end}'
   kubectl delete pod payment-processor --ignore-not-found
   kubectl apply -f payment.yaml
   kubectl get pod payment-processor -o wide
   kubectl get events --field-selector involvedObject.name=payment-processor \
     --sort-by=.lastTimestamp | tail -5
   ```

   Write down the node it landed on and what that node's `failure-probability` is. Then decide which
   of the post's four *only* sentences survive contact with an untainted cluster, and check your
   answer against `taint-and-toleration.md:247-248` and the dedicated-nodes bullet at `:250-259`.

6. Now give the two workers different values of the same key, place the Pod against them, and then
   move the ground under it. This is Example 1 run end to end:

   ```sh
   cd /tmp/bw-tolerations
   WK=$(kubectl get nodes -l '!node-role.kubernetes.io/control-plane' -o name | cut -d/ -f2)
   W1=$(echo "$WK" | sed -n 1p); W2=$(echo "$WK" | sed -n 2p); echo "$W1 $W2"
   kubectl taint nodes "$W1" failure-probability=15:NoExecute
   kubectl taint nodes "$W2" failure-probability=2:NoExecute
   kubectl delete pod payment-processor --ignore-not-found
   kubectl apply -f payment.yaml
   sleep 15; kubectl get pod payment-processor -o wide
   kubectl taint nodes "$W2" failure-probability=2:NoExecute-
   kubectl taint nodes "$W2" failure-probability=15:NoExecute
   for i in $(seq 1 12); do
     printf '%s ' "$(date +%T)"
     kubectl get pod payment-processor -o wide --no-headers 2>&1 | head -1
     sleep 5
   done
   kubectl -n kube-system logs -l component=kube-controller-manager --tail=20
   ```

   Two questions, and they are separate. Did the Pod land on the node tainted `2` rather than the
   one tainted `15`, which is the scheduler honouring `Lt` with the gate on? And when the value
   flipped to `15`, was the Pod evicted — and if so, after thirty seconds or at once? The gate is
   not set on kube-controller-manager, where `taint-and-toleration.md:360-363` puts the
   `taint-eviction-controller`. Also settle what `tolerationSeconds: 30` covers: a toleration that
   matches and is being waited out, or a toleration that has stopped matching.

7. Settle the direction of the comparison by measurement rather than by reading. One taint value,
   two Pods, one on each side of it:

   ```sh
   cd /tmp/bw-tolerations
   for OP in Gt Lt; do
     cat > cmp-$OP.yaml <<EOF
   apiVersion: v1
   kind: Pod
   metadata:
     name: cmp-$(echo $OP | tr 'A-Z' 'a-z')
   spec:
     tolerations:
     - key: "failure-probability"
       operator: "$OP"
       value: "10"
       effect: "NoExecute"
     containers:
     - name: c
       image: registry.k8s.io/e2e-test-images/agnhost:2.53
       args: ["pause"]
   EOF
   done
   kubectl apply -f cmp-Gt.yaml -f cmp-Lt.yaml
   sleep 15; kubectl get pods -o wide | grep '^cmp-'
   ```

   Both workers are tainted `15` from step 6. A toleration of `10` with `Gt` matches if the taint
   value is greater than the toleration value; with `Lt` it matches if it is less. Say which Pod
   scheduled, then hold the result against post `:48`, post `:50` and
   `taint-and-toleration.md:186-187`, and state which of the three the binary agrees with.

8. Take the toleration side of the validation apart. The post and the pin disagree about sign and
   agree about leading zeros, so test both, plus the edges of a 64-bit integer:

   ```sh
   cd /tmp/bw-tolerations
   for V in 5 0 0100 -5 +5 9223372036854775807 9223372036854775808 abc ""; do
     cat > t.yaml <<EOF
   apiVersion: v1
   kind: Pod
   metadata:
     name: v-test
   spec:
     tolerations:
     - key: "failure-probability"
       operator: "Lt"
       value: "$V"
       effect: "NoSchedule"
     containers:
     - name: c
       image: registry.k8s.io/e2e-test-images/agnhost:2.53
       args: ["pause"]
   EOF
     printf '%-22s ' "[$V]"
     kubectl apply --dry-run=server -f t.yaml 2>&1 | tail -1
   done
   ```

   Nine values, nine verdicts. Post `:55` says positive, no leading zeros, and `"0"` not permitted;
   `taint-and-toleration.md:226-227` says signed, no leading zeros, and says nothing about zero.
   Build the table and mark which line each verdict supports. `--dry-run=server` is used so the same
   Pod name can be reused; nothing is created.

9. Now the taint side, which is validated by a different rule and, per the pin, barely validated at
   all. Then the one effect whose behaviour the post does not describe:

   ```sh
   W2=$(kubectl get nodes -l '!node-role.kubernetes.io/control-plane' -o name | sed -n 2p | cut -d/ -f2)
   kubectl taint nodes "$W2" fp-neg=-5:NoSchedule
   kubectl taint nodes "$W2" fp-text=high:NoSchedule
   kubectl taint nodes "$W2" fp-zero=0100:NoSchedule
   kubectl get node "$W2" -o jsonpath='{.spec.taints}' | tr ',' '\n'
   kubectl taint nodes --all fp-neg- fp-text- fp-zero- 2>/dev/null || true
   kubectl taint nodes --all failure-probability- 2>/dev/null || true
   kubectl taint nodes --all failure-probability=15:PreferNoSchedule
   kubectl delete pod cmp-gt cmp-lt --ignore-not-found
   kubectl apply -f /tmp/bw-tolerations/cmp-Lt.yaml
   sleep 15; kubectl get pod cmp-lt -o wide
   ```

   Which of the three taint values did the API server accept, and what did it say about the one it
   did not? Read the answer against `node-v1.md:562` and `:570`, which state no constraint on a node
   taint's key or value, and against `resource-slice-v1.md:406` and `:414`, which state both for a
   device taint. Then the `PreferNoSchedule` case: `cmp-lt` tolerates values below 10 and every node
   is tainted `15`, so the comparison fails everywhere. `taint-and-toleration.md:230-232` says the
   node gets a lower priority *"but may still schedule there if no better options exist"*. Say
   whether it did.

10. Offline, against the tree itself. Run these from `cd /path/to/kubernetes/website/content/en` and
    record the counts, not the impressions:

    ```sh
    grep -rc '`Gt`' docs | grep -v ':0'
    grep -rc '`Lt`' docs | grep -v ':0'
    sed -n '80,83p;178,187p' docs/concepts/scheduling-eviction/taint-and-toleration.md
    grep -rn 'failure-probability\|gpu-compute-score\|cost-per-hour\|disk-iops' docs | wc -l
    grep -rc 'servicelevel.organization.example' docs | grep -v ':0'
    grep -n ' $' docs/concepts/scheduling-eviction/taint-and-toleration.md
    sed -n '562p;570p' docs/reference/kubernetes-api/core/node-v1.md
    sed -n '406p;414p' docs/reference/kubernetes-api/resource/resource-slice-v1.md
    sed -n '475p' docs/reference/kubernetes-api/resource/resource-claim-v1.md | cut -c1-200
    cat docs/reference/command-line-tools-reference/feature-gates/TaintTolerationComparisonOperators.md
    ```

    Ten commands, and the first two are the whole reach of the feature in the documentation. The
    `sed` of `:80-83` beside `:178-187` is the self-disagreement: read them in that order and decide
    whether a reader arriving at the top of the page could know the matching rule was incomplete.
    The two API reference lines against the two DRA ones are the constraint that is written down
    once and not twice. Finish by counting how many of the post's own keys appear anywhere in the
    tree.

**Expect**

Step 1 should show three nodes at v1.35.x, the control plane carrying
`node-role.kubernetes.io/control-plane:NoSchedule` and the two workers carrying nothing, and neither
static Pod manifest carrying a `--feature-gates` flag. `kubectl explain
pod.spec.tolerations.operator` prints whatever description the v1.35 OpenAPI carries. The pinned
v1.37 text at `toleration-v1.md:48` names four operators and the gate; if the v1.35 text names two,
you have dated the sentence, and if it already names four you have learned that the schema
description was written when the field was added rather than when it was enabled.

Step 2 is the one place where a rejection is the useful answer. With the gate off, a `Lt` toleration
has no legal value for `operator`, and the expected outcome is a validation error from the API
server naming the unsupported value rather than a silently dropped field. Both Pods should fail the
same way, which matters because one is the post's and one is the documentation's: if the pin's own
example manifest cannot be applied to a default cluster, that is a property of the feature and not
of the post. Keep the exact message; step 4 is judged against it.

Step 3 should show `kubectl apply` succeeding on the Node object and the diff being larger than one
taint. A Node's `spec` also carries `podCIDR`, `podCIDRs` and `providerID`, and applying a manifest
that omits them invites the apply machinery to reconcile their absence; watch for the kubelet
writing some of them straight back. The taint itself should land. The point is not that the post's
block fails — it may well work — but that it is a whole-object write standing in for a field-level
one, and the pin's example uses `kubectl taint` for exactly that reason.

Step 4 should bring both control-plane Pods back within a minute or two, and `kubectl explain`
should be unchanged, because the schema description is compiled in and does not consult the gate. If
the API server does not come back, the `sed` landed in the wrong list — restore from
`/tmp/bw-apiserver.yaml.bak` on `10.10.10.140` and look at where the flag was inserted. The
scheduler is the component nothing will complain about if you forget it: the Pod will be admitted
and then sit `Pending` with no matching node, which is the symptom of a half-enabled gate.

Step 5 is the central measurement and it should be anticlimactic. With no `failure-probability`
taint on any node, the payment Pod is admitted and scheduled onto a worker whose
`failure-probability` is not less than 5 for the excellent reason that it has no such value at all.
Nothing was violated: the toleration was never consulted, because no taint asked to be tolerated.
That is the whole of the finding, and it is why `:115`, `:186`, `:233` and `:247` are wrong in the
same way. A toleration is a permission to ignore an objection, and a node that raises no objection
needs no permission.

Step 6 splits in two. The placement half should work: with `.141` at `15` and `.142` at `2`, the `Lt
"5"` toleration matches only `.142`'s taint, the `NoExecute` on `.141` repels the Pod, and the Pod
lands on `.142`. That is the feature doing the thing the post was written to announce, and it is
worth seeing. The eviction half is open. When `.142`'s value flips to `15` the toleration stops
matching, and two things could follow: eviction at once, because `tolerationSeconds` governs how
long a *matching* toleration holds and there is no longer a matching toleration; or eviction after
thirty seconds, if the controller reads the field off the Pod without re-testing the match. A third
outcome is possible and is the one this step is really hunting: no eviction at all, because
`taint-eviction-controller` runs in kube-controller-manager, which step 4 deliberately did not
touch. If the Pod is still running after a minute, enable the gate on the third component and repeat
— and note that the post's numbered instruction told you to enable two.

Step 7 should schedule exactly one of the two Pods. Both workers carry `failure-probability=15` and
both test Pods offer `10`. `Gt` matches when the taint value exceeds the toleration value, so
`cmp-gt` tolerates a `15` node and should be `Running`; `Lt` matches when the taint value is below
it, so `cmp-lt` should be `Pending` with an unschedulable event naming the untolerated taint. If
that is what you see, the binary agrees with post `:48` and with `taint-and-toleration.md:186-187`,
and the gloss at post `:50` is simply an error. The reverse result would be the more interesting
outcome and would mean the pin's two bullets are the ones to distrust; either way one sentence in
the tree is now dated by measurement.

Step 8 should produce a clean split. `5` is accepted. `abc` and the empty value are rejected as
non-integers. `0100` is rejected by both documents' rule. The three that decide the disagreement are
`0`, `-5` and `+5`: the post forbids `0` and implies `-5` is illegal, the pin allows both by saying
*signed*. The two 64-bit edges should separate as well, with `9223372036854775807` accepted and
`9223372036854775808` rejected, which is the cheapest possible confirmation that the parse is a
signed 64-bit one rather than an arbitrary-precision one. Whatever the table says, it describes
v1.35 — the release the post announces — so a disagreement here is a disagreement about what
shipped, not about what changed later.

Step 9 should reject `fp-neg=-5` and accept `fp-text=high` and `fp-zero=0100`. A taint value is a
label value, and a label value may not begin with `-`; `high` and `0100` are perfectly good label
values and perfectly useless numeric ones, which is the pin's point at `:192-198` — the node side is
not checked for numbers, so the failure surfaces as a Pod that will not schedule rather than as an
error. That makes the pin's *signed* unreachable from the node end even if the API server accepts it
from the Pod end. The `PreferNoSchedule` half should show `cmp-lt` scheduled despite failing the
comparison on every node, which is `:230-232` behaving exactly as written and the one case the
post's *"work with all taint effects"* leaves a reader unprepared for.

Step 10 should give: three files for `Gt` and three for `Lt`, at 4/7/1 and 4/6/1; a matching rule at
`:80-83` listing two operators and a section at `:178-187` adding two more, with nothing between
them acknowledging the other; zero occurrences of all four of the post's taint keys and three of the
pin's one; three trailing-whitespace lines, consecutive, at `:210-212`; a node taint key and value
documented with no constraints and a device taint key and value documented with both; a
DeviceToleration that accepts `Exists` and `Equal` and nothing else; and a gate file of two lines
with one rung. If the `Gt` count comes back as anything other than three files, the feature grew
between this reading and yours, and the ladder above is the first thing to re-check.

**Read on**

11. [The 2017 advanced scheduling row](../2017/02-advanced-scheduling-in-kubernetes.md), which is
    the other half of this exercise. It reads the node-affinity operator tables at
    `assign-pod-node.md:715-730`, including the sentence that says `Gt` and `Lt` *"can only be used
    with `nodeAffinity`"*, and it prints this gate's single rung as the last of six to date that
    sentence. It also quotes the label-value syntax rule in full and settles `PreferNoSchedule`.
    Read it first if you want the affinity side of the comparison the post spends `:33-41` arguing
    against.

12. [The 2022 non-graceful node shutdown
    row](../2022/03-kubernetes-1-24-non-graceful-node-shutdown-alpha.md), for taint-based eviction
    as a subject rather than as an instrument: the built-in condition taints, the one taint a human
    applies by hand, and what force-deletion after a taint actually does. It runs on the same
    topology and is the right place to go after step 6 leaves you wondering which component evicted
    what.

13. [The 2024 matchLabelKeys row](../2024/08-matchlabelkeys-podaffinity.md), for the other concept
    page in the same directory and the same failure mode at a larger scale: a post whose worked
    examples cannot be submitted to the API they describe, and a documentation page that fixed one
    violation while inheriting another. The parallel is exact enough to be worth the comparison —
    scheduling posts are written from the feature's point of view and validated, if at all, against
    a cluster where the feature is on.

14. [The 2025 DRA row](../2025/08-kubernetes-v1-34-dra-updates.md), for the second taint and
    toleration vocabulary in the same pin. Devices get taints, ResourceClaims get tolerations, and
    the operators stop at `Exists` and `Equal`. Read it for what the newer of the two systems chose
    not to copy, and for the ResourceSlice fields whose two constraint sentences this exercise
    borrows to show what the node taint's fields do not say.

15. *Unanswerable from the pin.* Whether v1.35 shipped the validation the post describes or the
    validation the reference describes. The post says positive, no zero; the reference says signed,
    and is generated from a tree two releases newer. A one-commit sparse checkout cannot distinguish
    a rule that was tightened between 1.35 and 1.37 from a rule that was mis-stated in the
    announcement, and the gate file records no second stage that would mark a behaviour change. Step
    8 tells you what one v1.35 binary accepts, which settles the lab and not the history.

**Teardown**

```sh
kubectl delete pod payment-processor nginx-numeric-toleration cmp-gt cmp-lt --ignore-not-found
kubectl taint nodes --all failure-probability- fp-neg- fp-text- fp-zero- 2>/dev/null || true
ssh zain@10.10.10.140 "sudo cp /tmp/bw-apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml \
  && sudo cp /tmp/bw-scheduler.yaml.bak /etc/kubernetes/manifests/kube-scheduler.yaml \
  && sudo rm -f /tmp/bw-apiserver.yaml.bak /tmp/bw-scheduler.yaml.bak"
until kubectl version >/dev/null 2>&1; do sleep 5; done
kubectl -n kube-system get pods -l tier=control-plane
rm -rf /tmp/bw-tolerations
```
