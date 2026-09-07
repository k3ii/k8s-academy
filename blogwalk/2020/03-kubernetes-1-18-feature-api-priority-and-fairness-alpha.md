<a id="kubernetes-1-18-feature-api-priority-and-fairness-alpha"></a>

# The post announces as new to 1.18 a feature already three releases into alpha under a name the pin keeps only to record the rename, both flags it tells you to set are gone in opposite directions, and its flattest sentence — never anywhere else — was made false in 1.26

**Post** — [API Priority and Fairness
Alpha](https://kubernetes.io/blog/2020/04/06/kubernetes-1-18-feature-api-priority-and-fairness-alpha/),
6 April 2020, by Min Kim (Ant Financial), Mike Spreitzer (IBM) and Daniel Smith (Google). 70 lines
and 7,826 bytes. A design walkthrough rather than a tutorial: four numbered ideas, three
prerequisites for turning the thing on, two `kubectl get` commands, and a closing list of what the
authors knew was still missing.

This is the most churned API surface in the archive, and the churn is the exercise. Everything in
the post's four-idea design is still standing; almost nothing in its vocabulary or its plumbing is.
Read the design section for what to keep, then treat every identifier the post names — the gate, the
group-version, the field, the metric label — as a thing to look up rather than a thing to type.

**As written**

The post opens on a problem it states in one sentence. Before this feature, the apiserver had only
`max-in-flight limits for mutating and for readonly requests`, and that made it, in the post's
words, `far too easy for Kubernetes workloads to accidentally DoS the apiservers`. A single badly
behaved controller could crowd out everything else, because the only defence counted requests
without caring who sent them or what they were for.

The fix is presented as four numbered ideas stacked on each other. Requests are matched by a Flow
Schema, which states the Priority Level for the requests that match it and assigns each one a flow
identifier; each Priority Level `gets its own isolated concurrency pool` and may queue requests it
cannot serve immediately; a level may be given multiple queues, into which requests are dealt by
shuffle sharding, so that no one user or namespace monopolises the level; and when there is
capacity, a fair queuing algorithm picks the next request, the queues competing `with even
fairness`.

Then the prerequisites. The post asks for three things: a cluster at 1.18 or later, the apiserver
started with `--runtime-config="flowcontrol.apiserver.k8s.io/v1alpha1=true"`, and the apiserver
started with `--feature-gates=APIPriorityAndFairness=true`. With those in place you `will see a few
default FlowSchema and PriorityLevelConfiguration resources`, listed with `kubectl get flowschemas`
and `kubectl get prioritylevelconfigurations`.

The design section that follows is where the post is at its most confident, and it is worth reading
closely because it is where the language has moved most. A FlowSchema matches a request on `the
identity making the request, the verb, and the target object`. Priority Levels come in two kinds. An
`exempt` level is for `apiserver self requests, and any reentrant traffic (e.g., admission webhooks
which themselves make API requests)`, and for such a level `no queueing or limiting of any sort is
done`, which the post explains is `to prevent priority inversions`. Every other level is `configured
with a number of "concurrency shares" and gets an isolated pool of concurrency to use`, and then the
sentence to hold on to: `Requests of that Priority Level run in that pool when it is not full, never
anywhere else.` The whole apiserver has `a total concurrency limit (taken to be the sum of the old
limits on mutating and readonly requests)`, divided among the levels in proportion to their shares.

Between the two kinds sits the post's one piece of imagery, and it is the reason shuffle sharding
gets a paragraph of its own: the elephants and the mice. A high-intensity flow is an elephant, a
low-intensity one a mouse, and the point of dealing requests into randomly chosen queues is to make
it unlikely that any particular mouse shares every one of its queues with an elephant.

The post closes on a section headed `What’s missing? When will there be a beta?`. Three enhancements
are listed — traffic management for `WATCH` and `EXEC` requests, adjusting and improving the default
set of FlowSchema and PriorityLevelConfiguration objects, and enhancing observability on how the
feature works — followed by an invitation to join the discussion. Then, set apart from the list as
its own closing line, a fourth: `Possibly treat LIST requests differently depending on an estimate
of how big their result will be.` That last line is the one that has aged into a whole vocabulary,
and it is worth marking before you read on.

**As it runs now**

Both gate names the post depends on are dead, and the switch has moved out of the gate system
altogether. `reference/command-line-tools-reference/feature-gates/APIPriorityAndFairness.md` carries
`removed: true`, and so does the gate file for the name it took over from. What replaced them is an
ordinary apiserver flag: `kube-apiserver.md:563` lists `--enable-priority-and-fairness` with
`Default: true`. The feature is not something you enable any more; it is something you would have to
go out of your way to switch off. The two-gate history is the ladder, below.

**The group-version the post tells you to serve has no occurrences at the pin at all.** Search the
whole pinned documentation tree for `flowcontrol.apiserver.k8s.io/v1alpha1` and nothing comes back —
not a reference page, not the deprecation guide, not a migration note. That absence is not an
oversight: alpha versions sit outside the API support window, so they are removed without ever
entering the guide that records removals. What the pin does say is
`reference/kubernetes-api/group-versions.md:26`, one line, one served version: `v1`.

**The pin's instruction for disabling the API group names a version the pin says elsewhere is not
served.** `concepts/cluster-administration/flow-control.md:48-59` describes the group as having `(a)
a stable v1 version, introduced in 1.29` and `(b) a v1beta3 version, enabled by default, and
deprecated in v1.29`, and then `:61-65` gives you a command to turn that beta off:
`--runtime-config=flowcontrol.apiserver.k8s.io/v1beta3=false`. But
`reference/using-api/deprecation-guide.md:27-34` says `flowcontrol.apiserver.k8s.io/v1beta3` is `no
longer served as of v1.32`. Two pages of the same tree, one describing a version as enabled by
default and offering you a flag to disable it, the other recording that it stopped being served five
releases before the pin. The cluster settles it.

**A second page disagrees with the same fact in a different direction.**
`reference/kubectl/_index.md:228-229` lists both `flowschemas` and `prioritylevelconfigurations`
under `flowcontrol.apiserver.k8s.io/v1beta2` — a group-version the deprecation guide says stopped
being served at v1.29, two betas before the one the concept page still offers to disable. Three
pages, three different answers about which version of this group a cluster serves. `kubectl
api-resources` gives the fourth, and it is the only one that counts.

**The two commands the post ends its setup section with are the part that needed no maintenance.**
`kubectl get flowschemas` and `kubectl get prioritylevelconfigurations` work exactly as printed,
with no flags, no runtime-config and no gate. The resources are there on a default cluster because
nobody has to turn them on.

**The two old flags the post frames as the inadequate predecessor are both still present, and still
summed.** `kube-apiserver.md:808` gives `--max-requests-inflight` a `Default: 400` and `:801` gives
`--max-mutating-requests-inflight` a `Default: 200`, and both descriptions (`:804`, `:811`) say the
same thing: this and the other flag `are summed to determine the server's total concurrency limit
(which must be positive) if --enable-priority-and-fairness is true`. The post described the total
concurrency limit as `taken to be the sum of the old limits`, which is precisely what the flag
reference still says six years later. The flags the post came to replace are the flags that now
configure it.

**The sentence the post states most flatly is the one that broke, and the pin names the release it
broke in.** `Requests of that Priority Level run in that pool when it is not full, never anywhere
else.` Against `flow-control.md:128-133`: `The concurrency limits of the priority levels are
periodically adjusted, allowing under-utilized priority levels to temporarily lend concurrency to
heavily-utilized levels.` A level's requests now do run somewhere else — in concurrency borrowed
from a quiet neighbour. And `:234-240` dates it: `in Kubernetes release 1.25 and earlier there were
no periodic adjustments: the nominal/assured limits were always applied without adjustment`. So the
post's sentence was exactly true through 1.25 and has been false from 1.26 on.

**The field that expresses a level's share was renamed, and the renaming is why this group has so
many names.** `assuredConcurrencyShares` became `nominalConcurrencyShares`, recorded at
`deprecation-guide.md:47` as a notable change accompanying the removal of `v1beta2`. The old name
survives at the pin only in those deprecation-guide lines; every reference page and the concept page
use the new one, and `flow-control.md:234-240` puts the old name in words rather than as an
identifier — `assured concurrency shares` — because there is no field left to spell.
[`research/blog-era-translation.md`](../../research/blog-era-translation.md) already records the
chronology in one row: `v1beta1` gone at v1.26, `v1beta2` at v1.29, `v1beta3` at v1.32, `v1` served
since v1.29. Three betas in six releases, because each incompatible reshape of how borrowing and
lending are expressed needed a new beta rather than an in-place edit.

**The exempt level acquired fields, which puts it inside the accounting the post says it stands
outside of.** The post's `exempt` does `no queueing or limiting of any sort`. At the pin,
`reference/kubernetes-api/flowcontrol/priority-level-configuration-v1.md:133-153` gives
`ExemptPriorityLevelConfiguration` a `lendablePercent` and a `nominalConcurrencyShares`, and the
description of the latter is worth reading twice: it `DOES NOT limit the dispatching from this
priority level but affects the other priority levels through the borrowing mechanism`, and `Bigger
numbers mean a larger nominal concurrency limit, at the expense of every other priority level.`
Meanwhile the same page's `type` field says an `Exempt` level's requests `do not detract from the
capacity made available to other priority levels`. Both statements are true only at the field's
default of zero. The exempt level is still exempt from being limited; it is no longer exempt from
the accounting.

**`A few default FlowSchema and PriorityLevelConfiguration resources` is now a specified set with
two halves.** `flow-control.md:354-381` names four mandatory objects — an `exempt` priority level
and an `exempt` FlowSchema, a `catch-all` priority level and a `catch-all` FlowSchema — which
`reflect fixed built-in guardrail behavior` the server has whether the objects exist or not.
`:383-419` names six suggested priority levels: `node-high`, `system`, `leader-election`,
`workload-high`, `workload-low`, `global-default`. The suggested FlowSchemas that steer requests
into them are the one part the pin declines to list: they `serve to steer requests into the above
priority levels, and are not enumerated here`. So the number of FlowSchemas on a default cluster is
a fact you can only get from the cluster.

**Those defaults are not installed once, they are maintained on a one-minute loop, and the two
halves are maintained differently.** `flow-control.md:421-477` is the section the post has no
counterpart for. Each apiserver makes `an initial maintenance pass` and then `periodic maintenance
(once per minute)`. For a mandatory object, maintenance means ensuring it exists with the right
spec, and `The server refuses to allow a creation or update with a spec that is inconsistent with
the server's guardrail behavior` — you cannot edit it at all. For a suggested object the design is
the opposite: the spec is `designed to allow their specs to be overridden`, but `Deletion, on the
other hand, is not respected: maintenance will restore the object.` Delete a suggested object and it
comes back within a minute; edit a mandatory one and you are refused.

**One annotation decides who owns a suggested object, and putting it on an object of your own gets
the object deleted.** Ownership is settled by `apf.kubernetes.io/autoupdate-spec`: `true` means the
apiservers control the spec and will overwrite your edits, `false` means you do. If the annotation
is absent the server falls back to `metadata.generation`, treating 1 as apiserver-owned — a rule
`introduced in release 1.22` for the sake of migrating from the earlier behaviour. That fallback is
close to unreachable in practice, because maintenance `also includes ensuring that it has an
apf.kubernetes.io/autoupdate-spec annotation that accurately reflects whether the kube-apiservers
control the object`. And the last line of the section is a trap worth setting off on purpose:
`Maintenance also includes deleting objects that are neither mandatory nor suggested but are
annotated apf.kubernetes.io/autoupdate-spec=true.`
`reference/labels-annotations-taints/_index.md:25-37` states the consequence without hedging — if
the API server does not recognise an APF object and you annotate it for automatic update, `the API
server deletes the entire object`.

**Of the three enhancements the post lists as missing, one shipped, one shipped and grew, and half
of the first will never ship.** The post asks for `Traffic management for WATCH and EXEC requests`.
Watch arrived: `flow-control.md:39-41` states it in bold — `API Priority and Fairness does apply to
watch requests` — and `:152-170` gives watch its own section on execution-time estimation. Exec did
not, and the same caution explains why it cannot. Requests classified as long-running, `such as
remote command execution or log tailing`, are `not subject to the API Priority and Fairness filter`,
and that is a property of what the filter is rather than a gap in it: a filter that limits
concurrency cannot meaningfully limit a request that stays open for an hour. `Adjusting and
improving the default set` shipped as the four-plus-six configuration described above. `Enhancing
observability` shipped hardest of the three: `:501-706` documents thirty `apiserver_flowcontrol_*`
metrics — seven at maturity level BETA and twenty-three still at ALPHA, long after the feature
itself went stable in 1.29.

**The line the post sets apart at the end, the one it hedges with `Possibly`, became a noun that
runs through the whole page.** `Possibly treat LIST requests differently depending on an estimate of
how big their result will be` shipped as the **seat**. `flow-control.md:135-150` gives it a section
of its own: a request occupies some number of seats for some duration, and a list request estimated
to return many objects takes proportionally many. The metric
`apiserver_flowcontrol_work_estimated_seats` (`:692-695`) records `the number of estimated seats
(maximum of initial and final stage of execution) associated with requests`. The post's own
vocabulary has no word for this. It talks about requests and about concurrency shares, and one
request is one unit of concurrency. The estimate the post floats as a possibility is now the unit
the whole mechanism counts in.

**The one piece of the post's language that the pin adopted whole is the metaphor.**
`flow-control.md:297-317` carries a table of shuffle-sharding probabilities, and its caption is
about `the probability that a given mouse (low-intensity flow) is squished by the elephants
(high-intensity flows)`. Six years, five group-versions, two gate names and a renamed field later,
the elephants and the mice are still there, in the reference documentation, in the post's own words.

**What this exercise does not cover, and where it lives.** Two questions about this feature belong
to the cluster under load rather than to the API surface, and both are walked elsewhere in this
repository's third strand: which FlowSchema actually caught a particular request, read off the
response headers the apiserver attaches, and what happens when two flows are pushed hard enough at
one priority level that requests start being refused with `429 Too Many Requests`. That second one
is where the distinction between the distinguisher and the concurrency shares gets settled by
measurement. Neither is repeated here. This exercise generates no load at all: it reads the
configuration surface, checks every identifier the post names against what the cluster serves, and
then spends its second half on the maintenance loop — the one part of the mechanism that the
third-strand material deliberately leaves alone, on the grounds that discovering how mandatory and
suggested objects are restored differently deserves its own sitting. This is that sitting.

**The diff, and why**

**Still right.** The four-idea design is intact. Requests are still classified by a FlowSchema into
a Priority Level, levels still have their own concurrency budgets, those budgets are still served by
queues chosen by shuffle sharding, and the queues are still served fairly. The two `kubectl get`
commands still work verbatim. The total concurrency limit is still the sum of
`--max-requests-inflight` and `--max-mutating-requests-inflight`, and both flags still carry the
defaults they had. And the elephants and the mice made it into the reference documentation. When a
post's architecture survives six years of its own API being reshaped five times, that is worth
noticing: what churned was every name, not the design.

**The post broke.** `Requests of that Priority Level run in that pool when it is not full, never
anywhere else.` This is a statement about isolation, and isolation was traded away deliberately.
Borrowing was added because strict isolation wastes concurrency: a quiet level's budget sat unused
while a busy level queued. The pin now describes limits that are `periodically adjusted`, with
`lendablePercent` and `borrowingLimitPercent` fields to bound the trade per level. The post's
sentence held through 1.25 and stopped holding at 1.26. Nothing about it was wrong when written; the
design changed its mind about the guarantee.

**Wrong when it was published.** `This blog describes “API Priority And Fairness”, a new alpha
feature in Kubernetes 1.18.` The feature was not new to 1.18 and was not new to alpha. The gate file
for `RequestManagement` shows the same capability alpha in 1.15 and 1.16, and deprecated in 1.17 in
favour of the gate the post names. What was new in 1.18 was the second gate name and the first
version of the API group. The post is a rename presented as an arrival — an easy thing to do when
the rename lands in the release you are writing about, and something worth suspecting whenever a
post announces an alpha with a confident version number.

**A plan the project abandoned.** `Traffic management for WATCH and EXEC requests` — the EXEC half.
Watch shipped, and got its own execution-time estimation. Exec did not, and the pin's caution makes
clear it is not pending: long-running requests such as remote command execution sit outside the
filter by construction. This is the cleanest kind of abandoned plan in the archive, because nothing
was tried and reverted. The mechanism simply turned out not to be the right shape for the problem,
and the documentation now states the exclusion as a property rather than as a limitation.

**Overtaken by stasis.** The two flags the post introduces as the inadequate old defence.
`--max-requests-inflight` at 400 and `--max-mutating-requests-inflight` at 200 are still there,
still defaulted to the same numbers, and now serve as the input to the thing that replaced them. The
post frames them as what APF improves on; the pin frames them as how you configure APF's total. Also
in this case: twenty-three of the thirty metrics are still labelled ALPHA at v1.37, which is what
observability looks like when it is added continuously and graduated rarely.

**Retired by being agreed with.** Two of the three enhancement items on the post's closing list, and
the hedged line beneath it. The default configuration set was adjusted and improved into four
mandatory objects, six suggested levels and a maintenance loop. Observability was enhanced into
thirty metrics. And `Possibly treat LIST requests differently depending on an estimate of how big
their result will be` was agreed with so thoroughly that the estimate became the seat, and the seat
became the unit the entire page counts in. The reason to read a post's closing wishlist is that it
dates the vocabulary: every word in the pin that the post lacks a word for came from somewhere, and
here the post tells you where.

**A fourth thing, and this post's is a three-way disagreement inside the pin.** The concept page
describes `v1beta3` as enabled by default and hands you a flag to disable it; the deprecation guide
says `v1beta3` has not been served since v1.32; the kubectl reference page lists both resources at
`v1beta2`, which has not been served since v1.29. None of these is the post's fault and all three
are readable at the pin. A group-version that changes five times in six years leaves sediment in the
documentation, and the pages that mention it in passing are the ones that do not get swept. `kubectl
api-resources` is the arbiter, and asking it is a two-second habit worth having whenever a page
names a group-version rather than a group.

**The ladder**

Two gate files, because the capability was gated twice under two names, and the second file says so.
`feature-gates/RequestManagement.md` is headed `# Removed from Kubernetes` and carries `removed:
true`. Its stages are alpha with `defaultValue: false` from 1.15 to 1.16, then deprecated from 1.17
to 1.17 with no default value recorded. Its description reads `Enables managing request concurrency
with prioritization and fairness at each API server. Deprecated by APIPriorityAndFairness since
1.17.` So the rungs the post's feature climbed before the post existed are: alpha in 1.15, alpha in
1.16, deprecated in 1.17.

`feature-gates/APIPriorityAndFairness.md` also carries `removed: true`. Its stages are alpha with
`defaultValue: false` from 1.18 to 1.19, beta with `defaultValue: true` from 1.20 to 1.28, and
stable with `defaultValue: true` from 1.29 to 1.30. Its description reads `Enable managing request
concurrency with prioritization and fairness at each server. (Renamed from RequestManagement)`. The
stable band ending at 1.30 is the ladder's last rung: a gate that is stable and defaulted true
changes nothing, so it went away after 1.30, and the file survives only to tell you that the name is
no longer a name. The post's own closing question — `When will there be a beta?` — is answered by
the next release on the list.

There is a third state, and it is not on either ladder. The thing that turns this feature on and off
today is `--enable-priority-and-fairness`, a plain apiserver flag with `Default: true`
(`kube-apiserver.md:563`). A feature gate is a temporary object by design: it exists to let a
capability be off, then to let it be on, then to be removed. A flag is permanent, and it means
something different — not `this is not finished yet` but `you may not want this`. Reading the two
gate files together with the flag gives the whole shape: gated for three releases under one name,
gated for another thirteen under a second, then handed a permanent switch.

**Topology**

One node, the [`solo` topology](../../strands/lab-topologies.md#solo). Everything below is either a
read against the apiserver's own API surface or a small write to a cluster-scoped object, and none
of it needs a second machine or any workload at all. If the node is not up, the [provisioning
steps](../../strands/lab-topologies.md#provision) bring it up; a control plane at the pin's version
is the only requirement.

Say plainly what a single apiserver cannot show. The pin's `Recursive server scenarios` section
(`flow-control.md:70-99`) is about what happens when one apiserver's requests are served by another
— an aggregated API server, or a webhook that calls back — and one node cannot produce the
configuration where that matters. More directly relevant to the second half of the Do block:
maintenance is described as something each apiserver does `independently`, with the consequence that
`in a situation with a mixture of servers of different versions there may be thrashing as long as
different servers have different opinions of the proper content of these objects`. On one apiserver
there is exactly one opinion, so the restoration you will watch is clean and repeatable. That is
convenient for learning it and it hides the failure mode, so it is worth holding in mind that on a
three-server control plane mid-upgrade the same loop is a fight.

**Do**

1. Start where the post starts: with the three things it says the apiserver must be told. Look for
   all of them at once in the static Pod manifest, and then check whether the feature is running
   anyway.

   ```bash
   sudo grep -E 'runtime-config|feature-gates|priority-and-fairness' \
     /etc/kubernetes/manifests/kube-apiserver.yaml || echo "none of the three appear"
   kubectl get flowschemas --no-headers | wc -l
   ```

2. Ask the cluster which versions of the group it serves, then compare the answer with the three
   documentation pages that disagree about it. Probe each of the five names the group has had.

   ```bash
   kubectl api-versions | grep flowcontrol
   for V in v1alpha1 v1beta1 v1beta2 v1beta3 v1; do
     printf '%-9s ' "$V"
     kubectl get --raw "/apis/flowcontrol.apiserver.k8s.io/$V" >/dev/null 2>&1 \
       && echo served || echo "not served"
   done
   kubectl api-resources --api-group=flowcontrol.apiserver.k8s.io
   ```

3. Count what the post calls `a few default` resources, and read off each one who controls its spec.
   The annotation column and the generation column are the two inputs to the ownership rule.

   ```bash
   OWN='
   import json, sys
   for o in json.load(sys.stdin)["items"]:
       m = o["metadata"]
       a = m.get("annotations", {}).get("apf.kubernetes.io/autoupdate-spec", "-")
       print("%-26s autoupdate=%-6s generation=%s" % (m["name"], a, m["generation"]))
   '
   kubectl get prioritylevelconfigurations -o json | python3 -c "$OWN"
   kubectl get flowschemas -o json | python3 -c "$OWN"
   ```

4. Look for the field the post names, and for the struct the post says has no fields. One of these
   three commands is meant to fail; keep its message.

   ```bash
   kubectl explain prioritylevelconfiguration.spec.limited.nominalConcurrencyShares
   kubectl explain prioritylevelconfiguration.spec.limited.assuredConcurrencyShares
   kubectl explain prioritylevelconfiguration.spec.exempt
   ```

5. Do the arithmetic the post describes, then check it against what the apiserver says its levels
   are actually allowed. The post's total is the sum of the two old flags; the levels' shares divide
   it.

   ```bash
   SHARES='
   import json, sys
   total = 0
   for o in json.load(sys.stdin)["items"]:
       s = o["spec"]
       b = s.get("limited") or s.get("exempt") or {}
       ncs = b.get("nominalConcurrencyShares")
       print("%-26s %-8s ncs=%-5s lendable=%-5s borrowing=%s" % (
             o["metadata"]["name"], s["type"], ncs,
             b.get("lendablePercent"), b.get("borrowingLimitPercent")))
       if s["type"] == "Limited":
           total += ncs or 0
   print("sum of Limited shares:", total)
   '
   kubectl get prioritylevelconfigurations -o json | python3 -c "$SHARES"
   kubectl get --raw /metrics | grep '^apiserver_flowcontrol_nominal_limit_seats'
   ```

6. Take the census the post's third enhancement item asks for. Pull every metric name the apiserver
   exposes for this feature, count them, and then look for the two request kinds the post wanted
   managed.

   ```bash
   kubectl get --raw /metrics \
     | sed -n 's/^# HELP \(apiserver_flowcontrol_[a-z_]*\) .*/\1/p' \
     | sort -u > /tmp/apf-metrics.txt
   wc -l < /tmp/apf-metrics.txt
   grep -E 'watch|exec' /tmp/apf-metrics.txt || echo "(neither appears)"
   grep seats /tmp/apf-metrics.txt
   ```

7. Now the maintenance loop. Delete a suggested priority level, keeping a copy first, and time how
   long it stays deleted. The pin says maintenance runs once a minute, so give it seventy seconds.

   ```bash
   kubectl get prioritylevelconfiguration global-default -o yaml > /tmp/gd-before.yaml
   kubectl delete prioritylevelconfiguration global-default
   for I in $(seq 1 14); do
     kubectl get prioritylevelconfiguration global-default --no-headers 2>/dev/null \
       && { echo "restored after about $((I * 5)) seconds"; break; }
     sleep 5
   done
   kubectl get prioritylevelconfiguration global-default -o yaml > /tmp/gd-after.yaml
   diff /tmp/gd-before.yaml /tmp/gd-after.yaml || true
   ```

8. Deletion is not respected; overriding is. Change the level's share and watch what the loop does
   about it, then take ownership with the annotation and change it again.

   ```bash
   kubectl patch prioritylevelconfiguration global-default --type=merge \
     -p '{"spec":{"limited":{"nominalConcurrencyShares":11}}}'
   sleep 70
   kubectl get prioritylevelconfiguration global-default \
     -o jsonpath='{.spec.limited.nominalConcurrencyShares}{"\n"}'
   kubectl annotate prioritylevelconfiguration global-default \
     apf.kubernetes.io/autoupdate-spec=false --overwrite
   kubectl patch prioritylevelconfiguration global-default --type=merge \
     -p '{"spec":{"limited":{"nominalConcurrencyShares":11}}}'
   sleep 70
   kubectl get prioritylevelconfiguration global-default \
     -o jsonpath='{.spec.limited.nominalConcurrencyShares}{"\n"}'
   ```

9. The other half of the loop behaves the opposite way. Try to change a mandatory object's spec, and
   keep whatever the apiserver says. Then delete one and see whether deletion is treated any
   differently than it was for the suggested level.

   ```bash
   kubectl patch flowschema exempt --type=merge -p '{"spec":{"matchingPrecedence":5}}'
   kubectl patch prioritylevelconfiguration catch-all --type=merge \
     -p '{"spec":{"limited":{"nominalConcurrencyShares":9}}}'
   kubectl delete flowschema exempt
   for I in $(seq 1 14); do
     kubectl get flowschema exempt --no-headers 2>/dev/null \
       && { echo "restored after about $((I * 5)) seconds"; break; }
     sleep 5
   done
   ```

10. Last, set off the trap the maintenance section ends on. Create a FlowSchema that is neither
    mandatory nor suggested, annotate it as apiserver-controlled, and then wait a minute and look
    for it.

    ```bash
    kubectl apply -f - <<'EOF'
    apiVersion: flowcontrol.apiserver.k8s.io/v1
    kind: FlowSchema
    metadata:
      name: blogwalk-2020-03
      annotations:
        apf.kubernetes.io/autoupdate-spec: "true"
    spec:
      priorityLevelConfiguration:
        name: global-default
      matchingPrecedence: 9000
      rules:
      - subjects:
        - kind: User
          user:
            name: nobody-at-all
        resourceRules:
        - verbs: ["get"]
          apiGroups: [""]
          resources: ["configmaps"]
          namespaces: ["default"]
    EOF
    kubectl get flowschema blogwalk-2020-03
    sleep 70
    kubectl get flowschema blogwalk-2020-03 || echo "gone"
    ```

**Expect**

Step 1 is the whole point of the post's setup section evaporating. Expect the grep to come back
empty, or to find at most an unrelated `--runtime-config` or `--feature-gates` line that has nothing
to do with flow control; record whatever it does find. Then expect a non-zero FlowSchema count from
a cluster that was told none of the three things the post says are prerequisites. Neither of the
post's two flags is set, and the feature is running.

Step 2 should give `flowcontrol.apiserver.k8s.io/v1` from `api-versions`, one served version out of
the five names the group has carried, and the same string in the `APIVERSION` column of
`api-resources`. The four probes that fail are failing with a 404 from the apiserver, which is the
plainest possible answer to a documentation page that offers you a flag for disabling one of them.
Note which of the three pages named in *As it runs now* the cluster agrees with: none of them
entirely.

Step 3 gives you the two halves of the default set. Expect at least eight priority levels — the two
mandatory ones plus the six suggested — and record the FlowSchema count, because the pin does not
state it: the suggested FlowSchemas `are not enumerated here`. Expect `autoupdate=true` on every
built-in and `generation=1` on most of them. If nothing lacks the annotation, you have found why the
`metadata.generation` fallback almost never fires: the same maintenance loop that consults it also
guarantees the annotation it would be a fallback for.

Step 4: the first command describes `nominalConcurrencyShares` and should include the default-of-30
language. The second is the one meant to fail — record the message, because the field the post's
generation of documentation called `assuredConcurrencyShares` is not merely deprecated here, it is
absent from the schema. The third prints the `exempt` struct, and it has fields: at minimum
`lendablePercent` and `nominalConcurrencyShares`, on a level the post describes as doing no limiting
of any sort.

Step 5 is arithmetic against the post's own formula. Record the sum of the Limited levels' shares;
it is a property of your cluster's suggested configuration, not something the pin fixes. If both
inflight flags are at their documented defaults the total concurrency limit is 600, and each level's
`apiserver_flowcontrol_nominal_limit_seats` should be near that total times the level's share over
the sum of shares. The interesting columns are the other two: a non-zero `lendablePercent` on a
level means that level's concurrency can be spent by a different level, which is exactly the thing
the post says never happens. Record whether the exempt level appears in the seat metric at all.

Step 6: the pin documents thirty metric names for this feature, seven at BETA and twenty-three at
ALPHA. Record how many your apiserver actually exposes and whether the number matches — a metric is
only present once something has caused it to be emitted, so a quiet cluster may show fewer. In the
grep for the two request kinds, expect `apiserver_flowcontrol_watch_count_samples` and expect
nothing containing `exec`. That asymmetry is the post's first enhancement item, half-delivered on
purpose. The `seats` grep is the post's last line, delivered in full.

Step 7 should print `restored after about` some number of seconds no greater than about seventy, and
then a diff confined to `metadata` — a new `uid`, a new `resourceVersion`, a new
`creationTimestamp`, and no change to the spec. Deleting a suggested object does not remove it; it
replaces it with an identical object the apiserver made. If the diff shows a spec change, you have
found something better than the exercise expected, and the thing to record is which field moved.

Step 8 is the two ownership states, back to back. The first read-back should show the level's
original share and not 11: the annotation says the apiservers control the spec, so the loop
overwrote your edit. After the annotation is set to `false` the second read-back should show 11 and
keep showing it. Nothing about the object changed except one string in its metadata, and that string
decides whether your `kubectl patch` is a change or a suggestion.

Step 9 is where the two sorts of object part company, and the parting is narrower than it sounds.
Record what the apiserver says to each patch attempt — the pin's claim is that a spec inconsistent
with the server's guardrail behaviour is refused outright, so expect a rejection rather than a
silent revert. But then watch the delete: the mandatory FlowSchema comes back on the same loop and
in the same way the suggested level did. So the difference between mandatory and suggested is about
*updates*, not deletions. Deletion is not respected for either.

Step 10 should print the FlowSchema once, and then `gone`. Nobody deleted it. The object was neither
mandatory nor suggested, and it claimed to be apiserver-controlled, so maintenance concluded that an
apiserver it did not recognise must have created it and cleaned up. This is the one thing on this
page that can cost you an object you cared about, and the annotation that does it is three words
long.

**Read on** — four of these are answerable from the pin, and the fifth is about the version
the post tells you to enable.

1. What do the two old inflight flags do on an apiserver with the feature switched off? Both flag
   descriptions (`kube-apiserver.md:804`, `:811`) make the summing conditional on
   `--enable-priority-and-fairness` being true, and the caution at `flow-control.md:34-42` says that
   without the feature, `--max-requests-inflight` does not cover watch requests either. Read the two
   together and you get the pre-1.15 behaviour the post was describing.

2. Why does the pin devote a section to exempting health checks (`flow-control.md:478-499`), and
   what does the FlowSchema in `examples/priority-and-fairness/health-for-strangers.yaml` actually
   match? It is a worked example of the thing the post says you may do — direct other requests into
   the exempt level — for a case the post does not mention.

3. What does a watch request cost? `flow-control.md:152-170` covers execution-time tweaks for
   watches, and `apiserver_flowcontrol_watch_count_samples` records `the number of active WATCH
   requests relevant to a given write`. Following that back gives the mechanism by which the number
   of watchers changes the seat cost of somebody else's write.

4. What are the two things the pin recommends you actually change? `flow-control.md:759-820` gives
   more seats to high-priority requests and isolates non-essential requests from starving other
   flows, the second with an example in
   `examples/priority-and-fairness/list-events-default-service-account.yaml`. Both are advice the
   post had no basis to give yet.

5. Unanswerable from the pin: what `flowcontrol.apiserver.k8s.io/v1alpha1` contained. The version
   the post's `--runtime-config` line enables has zero occurrences in the pinned tree, and alpha
   versions never enter the deprecation guide because they are outside the support window the guide
   is about. So the shape of the objects the post's own commands would have listed — which fields
   existed, what the level type was called — is not recoverable from the pin. Only the post's prose
   survives it.

**Teardown** — nothing of yours to remove, one object to hand back, and three files.

```bash
kubectl get flowschema blogwalk-2020-03 || echo "already deleted by the apiserver"
kubectl annotate prioritylevelconfiguration global-default \
  apf.kubernetes.io/autoupdate-spec=true --overwrite
sleep 70
kubectl get prioritylevelconfiguration global-default \
  -o jsonpath='{.spec.limited.nominalConcurrencyShares}{"\n"}'
rm -f /tmp/apf-metrics.txt /tmp/gd-before.yaml /tmp/gd-after.yaml
```

The FlowSchema from step 10 should need no deleting; confirm that rather than assume it. Giving
`global-default` its annotation back is the whole of the cleanup, because handing ownership to the
apiservers means the next maintenance pass restores the spec you overrode — the mechanism you have
just spent nine steps on is also the undo. The mandatory objects need nothing either: whatever step
9's two patches did, the loop's opinion of a mandatory spec is the one that stands, and the
FlowSchema you deleted was put back before you got to this line. Leave the cluster's own
configuration alone from here; it is a default set worth having.
