<a id="introducing-podtopologyspread"></a>

# The four fields the post prints are still exactly right and are now four of eight, its closing config sample names a group-version the pin never mentions and a plugin that never existed under that name, and the pin still recommends the post as further reading on a field it has outgrown

**Post** — [Introducing
PodTopologySpread](https://kubernetes.io/blog/2020/05/Introducing-PodTopologySpread/), 5 May 2020,
by Wei Huang (IBM) and Aldo Culquicondor (Google). 193 lines and 8,567 bytes. A field walkthrough
with three diagrams: the API, two advanced-usage patterns worked through node by node, and a closing
section on cluster-level defaults.

This is the cleanest survival in the year and one of the messiest peripheries. The four-field
constraint the post prints is byte-for-byte what a v1.37 cluster accepts, and the arithmetic the
post walks through by hand still comes out the same. Everything around it — the gate, the scheduler
configuration, the plugin names, the definition of the number the arithmetic is against — moved.
Work the field first, then the config sample, and treat the config sample as the part to be
suspicious of.

**As written**

The post opens by placing the feature between two things that already existed. Pod affinity and
anti-affinity, it says, `only resolve part of Pods distribution use cases: either place unlimited
Pods to a single topology, or disallow two Pods to co-locate in the same topology`, and between
those extremes is `a common need to distribute the Pods evenly across the topologies`. The plugin
that fills the gap was `originally proposed as EvenPodsSpread`, and the post's occasion is its
promotion: `We promoted it to beta in 1.18.`

The API section prints the field, and this is the block to hold on to, because it is the thing that
did not change:

```yaml
spec:
  topologySpreadConstraints:
  - maxSkew: <integer>
    topologyKey: <string>
    whenUnsatisfiable: <string>
    labelSelector: <object>
```

Four keys, and the post notes that because the field is embedded in the Pod spec, it works `in all
the high-level workload APIs, such as Deployment, DaemonSet, StatefulSet, etc.` Each key then gets a
bullet. `labelSelector` finds matching Pods and is counted per topology. `topologyKey` is `the key
that defines a topology in the Nodes' labels`. `maxSkew` `describes the maximum degree to which Pods
can be unevenly distributed`, and the post works the example through arithmetically: placing the
incoming Pod in zone1 makes the skew 3 against a global minimum of 0 and violates `maxSkew: 1`,
while placing it in zone2 makes the skew 0. Then a sentence that is worth marking: `Note that the
skew is calculated per each qualified Node, instead of a global skew.` `whenUnsatisfiable` is either
`DoNotSchedule (default)`, `a hard constraint`, or `ScheduleAnyway`, `a soft constraint`.

The advanced-usage section has two patterns. The first begins with an admission: `You may have found
that we didn't have a "topologyValues" field to limit which topologies the Pods are going to be
scheduled to.` The workaround is node affinity — restrict the search scope with
`spec.affinity.nodeAffinity`, and `Under the hood, the PodTopologySpread feature will honor that and
calculate the spread constraints among the nodes that satisfy the selectors`. That verb is the one
to watch. The second pattern is multiple constraints, `calculated independently`, with the result
sets merged: three Pods in zone1 against two in zone2 narrows the choice to `nodeX and nodeY`, the
per-node constraint narrows it to `nodeA and nodeY`, and the intersection leaves `nodeY`. A note
closes the section: two constraints sharing a `{topologyKey, whenUnsatisfiable}` tuple mean `the Pod
creation will be blocked returning a validation error`.

The last section is about defaults, and it is where the post ages. Because the field is Pod-level,
`workload authors need to be aware of the underlying topology of the cluster`, so the post offers
cluster-level defaults set as plugin arguments in the scheduling profile configuration, and prints a
sample `KubeSchedulerConfiguration` at `apiVersion: kubescheduler.config.k8s.io/v1alpha2` with a
single `defaultConstraints` entry keyed on `example.com/rack`. Label selectors `must be left empty`
and are deduced from the Pod's membership of `Services, ReplicationControllers, ReplicaSets or
StatefulSets`. A closing note advises that `When using default PodTopologySpread constraints, it is
recommended to disable the old DefaultTopologySpread plugin.`

**As it runs now**

The field is intact. Paste the post's four keys into a v1.37 Pod spec and the apiserver takes them,
with the same meanings and the same default. What has happened is that four more keys grew around
them. `concepts/scheduling-eviction/topology-spread-constraints.md:53-71` prints the field with
eight keys: the post's four, plus `minDomains`, `matchLabelKeys`, `nodeAffinityPolicy` and
`nodeTaintsPolicy`, each marked optional and two of them annotated `beta since v1.26` — an
annotation the same page contradicts further down its own field list, where both are `graduated to
GA in 1.33` (`:191`, `:205`). Nothing was renamed and nothing was removed. Read the rest of this
section as the story of what those four additions did to the meanings of the original four.

**The post's verb became an enum value.** `Under the hood, the PodTopologySpread feature will honor
that`, says the post, about node affinity narrowing the set of nodes the spread is calculated over.
At the pin that behaviour is a field with two values, and one of them is spelled `Honor`:
`nodeAffinityPolicy: [Honor|Ignore]`, where `Honor` means `only nodes matching
nodeAffinity/nodeSelector are included in the calculations` and `Ignore` means they are not. `If
this value is null, the behavior is equivalent to the Honor policy`, so the post's sentence is now
the documented default rather than the only behaviour. The workaround the post offers for a missing
field became a field, and the word the post used to describe it became the name of the value.

**Its sibling has the opposite default, and one gate covers both.** `nodeTaintsPolicy` takes the
same two values, but `If this value is null, the behavior is equivalent to the Ignore policy`. So on
a default cluster node affinity narrows the calculation and node taints do not, and both behaviours
arrive through a single feature gate that names them together. Worth knowing before you predict a
placement on a cluster with a tainted node in it.

**And the page still tells you to disable a gate that cannot be disabled.** Both node-policy notes
end the same way: the fields are `enabled by default in beta, you can disable it by disabling the
NodeInclusionPolicyInPodTopologySpread feature gate` (`:192-193`, `:206-207`). That gate's record
says `stage: stable`, `defaultValue: true`, `locked: true` from 1.33, with no closing version — the
entry that means the switch is welded on. A note written for the beta releases has outlived them by
five, and it is the one sentence on the page a cluster can flatly contradict.

**The field the post says is missing is still missing.** `topologyValues` has zero occurrences in
the pinned documentation tree. The post's admission — that there is no way to name the topologies
you want, only a way to filter the nodes — is as true at v1.37 as it was at 1.18, six years and four
added fields later. This is the rarest thing to find in a walk: a gap a post identified, that nobody
closed, that nobody wrote down as a decision either.

**`minDomains` changed what the arithmetic is against.** The post's sentence, `Note that the skew is
calculated per each qualified Node, instead of a global skew`, was a clarification about where the
count happens. The pin now defines the number the count is compared to, and the definition has a
field in it: the global minimum is `the minimum number of matching pods in an eligible domain or
zero if the number of eligible domains is less than MinDomains` (`:92-93`). Set `minDomains: 3` on a
cluster with two zones and the global minimum becomes 0 by definition, which changes every skew in
the calculation. You may only specify `minDomains` `in conjunction with whenUnsatisfiable:
DoNotSchedule`, and if you do not specify it `the constraint behaves as if minDomains is 1`
(`:112-119`). Setting it changes nothing else about the field, and changes the meaning of every
number in the post's arithmetic.

**And the page defines the new unit of counting twice, differently.** `minDomains` counts *eligible
domains*, so the term has to be defined. It is, twice. Under the page's `minDomains` entry: `An
eligible domain is a domain whose nodes match the node selector.` (`:100-101`). Under its
`topologyKey` entry: `we define an eligible domain as a domain whose nodes meet the requirements of
nodeAffinityPolicy and nodeTaintsPolicy.` (`:125-126`). Those agree on a default cluster and part
company exactly where the new fields bite: set `nodeAffinityPolicy: Ignore` and a domain whose nodes
fail the node selector is ineligible by the first definition and eligible by the second. The page
does not say which one `minDomains` uses.

**The gate record and the prose disagree by one release about when the field became default.** The
note at `:105-107` says the `minDomains` field needed its feature gate before v1.30 and that the
gate was `default since v1.28`. The gate file says otherwise:
`feature-gates/MinDomainsInPodTopologySpread.md:17-20` records `stage: beta` with `defaultValue:
true` from 1.27. One of the two is wrong about 1.27, and the gate file is the machine-readable one.
Nothing depends on the answer today — both releases are long out of support — which is exactly why
it was never noticed.

**`matchLabelKeys` has been beta for ten releases and needed a second gate to change its own
behaviour.** The field lets you name Pod label keys whose values are looked up on the incoming Pod
and merged into the `labelSelector`, which is how a Deployment spreads each revision separately
using `pod-template-hash`. It went beta in 1.27 and is still beta at the pin. Then in 1.34 the merge
stopped being implicit: `Before v1.34, matchLabelKeys was handled implicitly. Since v1.34, key-value
labels corresponding to matchLabelKeys are explicitly merged into labelSelector.` That change has a
gate of its own, `MatchLabelKeysInPodTopologySpreadSelectorMerge`, which exists only to let you go
back. A gate for a behaviour change inside a field that is itself still gated.

**The config sample's group-version has no occurrences at the pin.**
`kubescheduler.config.k8s.io/v1alpha2` appears nowhere in the pinned tree. What does appear is `v1`
(27 mentions), and, in migration notes only, `v1alpha1` once, `v1beta2` twice and `v1beta3` twice.
There is no trace of the version the post uses, and there was never going to be:
[`research/blog-era-translation.md`](../../research/blog-era-translation.md) records the policy that
governs this — alpha versions `may vanish any release, no notice`, and nothing in the deprecation
machinery is obliged to remember them. The equivalent example at
`topology-spread-constraints.md:519-549` is the post's sample with the version replaced, the
`topologyKey` changed to `topology.kubernetes.io/zone`, and one extra argument the post has no
counterpart for: `defaultingType: List`.

**The config sample is also the wrong shape, and was when it was published.** The post writes
`profiles:` and then `pluginConfig:` at the next indent level, which makes `profiles` a mapping. In
the configuration API it is a list: `reference/config-api/kube-scheduler-config.v1.md:438-439` gives
`profiles` as `[]KubeSchedulerProfile` and marks it `[Required]`. The pin's own example shows the
missing piece — a `- schedulerName: default-scheduler` list item, with `pluginConfig` nested under
it. The post's snippet is one hyphen and one indent short of loading, and the API it was written
against had the same list-shaped field.

**The plugin the post's closing note tells you to disable has never existed under that name.**
`DefaultTopologySpread` has zero occurrences in the pinned tree. The plugin that does the job the
note is about is `SelectorSpread`, and here the pin cannot agree with itself about it.
`topology-spread-constraints.md:567-568` says `the legacy SelectorSpread plugin, which provides an
equivalent behavior, is disabled by default`. `reference/scheduling/config.md:483-485`, in the
`v1beta3 → v1` migration tab, says `The scheduler plugin SelectorSpread is removed, instead, use the
PodTopologySpread plugin (enabled by default)`. A plugin cannot be both removed and
disabled-by-default, and the plugin list on the same config page (`:123-207`) does not include it.
The post's advice was taken further than the post asked: it was not disabled, it was deleted.

**The post's link into the reference no longer resolves.** It points at
`/docs/reference/scheduling/profiles/`. The pinned `reference/scheduling/` directory holds
`_index.md`, `config.md` and `policies.md`, and no `profiles` page; the profiles material is a
section of `config.md`, which the concept page links as `config/#profiles`. A page became an anchor,
which is the most common way a documentation link dies.

**Cluster-level defaults were not just made possible, they were shipped.** The post's last section
is about how an operator *can* set defaults. At the pin, an operator who sets nothing gets them:
`topology-spread-constraints.md:550-568` is marked stable at v1.24 and states that kube-scheduler
`acts as if you specified` a `maxSkew: 3` constraint on `kubernetes.io/hostname` and a `maxSkew: 5`
constraint on `topology.kubernetes.io/zone`, both `ScheduleAnyway`. There is a way to turn that off,
and it is the argument the post's sample lacks: set `defaultingType: List` with an empty
`defaultConstraints`. So the field's reach grew in the one direction the post did not anticipate —
into clusters where nobody wrote a constraint at all.

**A failure mode acquired a name.** `topology-spread-constraints.md:642-649` lists *ghost pods*:
`Pods that don't match their own labelSelector create "ghost pods"`, which `won't count itself in
spread calculations`, so `Multiple such pods can just accumulate on the same topology`. The post has
no equivalent warning; the pin has both this limitation and a longer treatment under *Implicit
conventions* (`:511-518`). The advice is one line — `Typically, a pod should match its own topology
spread constraint selector` — and it is the kind of line that only gets written after people have
filed the bug.

**And the pin still recommends the post.** The concept page's *What's next* section (`:651-654`)
links to this blog article, saying it `explains maxSkew in some detail, as well as covering some
advanced usage examples`. That recommendation is correct about the arithmetic and sends the reader
to a config sample with a dead group-version, a malformed `profiles` block and the name of a plugin
that was never called that. It is the clearest case in the archive of a post outliving its own
accuracy by being cited.

**What this exercise does not cover, and where it lives.** Node affinity, node selectors, inter-Pod
affinity and anti-affinity, and taints and tolerations are all inputs to the calculation below, and
none of them is explained here. They are walked as features in their own right in [the 2017
advanced-scheduling exercise](../2017/02-advanced-scheduling-in-kubernetes.md), which takes
`nodeSelector`, node affinity, inter-Pod affinity and taints in turn and follows each to the pin.
Read that one for what `nodeAffinity` does; read this one for what a spread constraint does *with*
it. The scheduling profile configuration API is also not walked here beyond the two claims above
about its shape and its version — configuring and restarting kube-scheduler is a different day's
work, and the *Read on* list says where to start.

**The diff, and why**

**Still right.** The four fields, their order, their types and the default on `whenUnsatisfiable`
are unchanged from the post to v1.37, which is six years and four minor fields. The post's
arithmetic is unchanged too, including the sentence about the skew being per-node rather than
global. This is what a Pod-level API graduating to stable is supposed to look like, and it is the
reason the pin can still send readers here for the `maxSkew` explanation.

**The post broke.** Its closing configuration sample is unusable and its link into the reference is
dead. `kubescheduler.config.k8s.io/v1alpha2` was replaced by `v1beta1` in 1.19, and onward through
`v1beta2`, `v1beta3` and `v1`; the pinned tree does not mention `v1alpha2` at all, because a
scheduler-config alpha version is not something the deprecation guide tracks. And
`/docs/reference/scheduling/profiles/` is now a section anchor of a different page. Both breaks are
in the operator-facing half of the post; the developer-facing half is intact. A post that spans two
audiences usually rots at different rates in each.

**Wrong when it was published.** The same sample writes `profiles:` followed directly by
`pluginConfig:`, which is a mapping. In every version of `KubeSchedulerConfiguration` that has ever
existed, `profiles` is a list — `reference/config-api/kube-scheduler-config.v1.md:438-439` gives it
as `[]KubeSchedulerProfile` and marks it `[Required]`. A reader who pasted the sample in 2020 got a
scheduler that refused to start, for a reason the post could not have helped them find. Correcting
the group-version is not enough; the shape has to be corrected too, and the pin's own example at
`:519-549` shows both corrections at once.

**A plan the project abandoned.** The post's last note advises disabling `the old
DefaultTopologySpread plugin` alongside the new defaults, which describes a plan: two spreading
plugins coexisting, with the operator choosing. That plan did not happen. There has never been a
plugin called `DefaultTopologySpread`; the plugin in question is `SelectorSpread`, and by the `v1`
configuration API it is not a switch you turn off, it is gone —
`reference/scheduling/config.md:483-485` says it `is removed`. The advice was overtaken by a
decision more thorough than the advice.

**Overtaken by stasis.** Two things the post opens the door to are still ajar. `topologyValues` —
the field the post explicitly says it does not have — has no occurrences at the pin, no successor
field, and no recorded decision not to build it. And `matchLabelKeys`, the one addition that changes
what a spread constraint *counts*, went beta in 1.27 and is still beta at 1.37: ten releases, long
enough for a second gate to be added on top of it in 1.34 to gate a change in how it works. A field
can sit in beta long enough to have beta-era history of its own.

**Retired by being agreed with.** The post's sentence `the PodTopologySpread feature will honor
that` is now the name of an enum value, and the post's `it is also possible to specify cluster-level
defaults` is now what you get when you specify nothing at all. In both cases the project did not
just accept the post's position, it promoted it — from prose to API, and from possible to default.
The exercise's *Do* block is largely a walk through this case, because it is the only one of the six
whose evidence is a placement rather than a document.

**A fourth thing: the pin does not agree with itself about this one field.** Four times, in fact.
Whether `SelectorSpread` is removed or disabled by default; what an *eligible domain* is; whether
`MinDomainsInPodTopologySpread` became default in 1.27 or 1.28; and whether the node-policy gate can
be turned off. Only the last is settleable on this cluster, and the last *Do* step settles it. The
`SelectorSpread` one needs kube-scheduler restarted with a configuration file that names the plugin,
which is past where this exercise goes. The *eligible domain* one cannot be settled from a cluster
at all, because the two definitions diverge only in a case the page never works through. And the
1.27-or-1.28 one has no cluster left to ask: both releases are out of support. Four disagreements,
four different distances from an answer.

**The ladder**

Six feature gates name this one field, which is more than any other field walked in this year.
Transcribed from `reference/command-line-tools-reference/feature-gates/`, the field itself came up
the ladder twice under two names, and its four later fields came up four more times behind it.

`EvenPodsSpread` is the post's own gate, under the post's own name for it — `originally proposed as
EvenPodsSpread`, as the post puts it. Alpha, default false, 1.16 to 1.17. Beta, default true, 1.18
to 1.18: a one-release beta, which is the release the post was written in. Stable, default true,
1.19 to 1.21. `removed: true`, and the file carries the `# Removed from Kubernetes` banner. A
three-year gate for a feature that was beta for a single release.

`DefaultPodTopologySpread` is the gate for the post's last section — the cluster-level defaults —
and it appeared after the post. Alpha, default false, 1.19. Beta, default true, 1.20 to 1.23.
Stable, default true, 1.24 to 1.25. `removed: true`. Its body points at
`#internal-default-constraints`, the anchor that now holds `maxSkew: 3` on hostname and `maxSkew: 5`
on zone. So the section of the post that broke worst is also the section whose feature completed
most thoroughly.

`MinDomainsInPodTopologySpread` is the only one of the six with a bent rung. Alpha, default false,
1.24. Beta, default false, 1.25 to 1.26. Then beta again, this time default true, 1.27 to 1.29.
Stable, default true, 1.30 to 1.31. `removed: true`. Two beta stages with a flip between them is how
a gate records that beta arrived before the confidence did, and it is the shape the concept page's
note gets wrong by one release.

`NodeInclusionPolicyInPodTopologySpread` gates both `nodeAffinityPolicy` and `nodeTaintsPolicy` —
one gate, two fields, opposite defaults. Alpha, default false, 1.25. Beta, default true, 1.26 to
1.32. Stable, default true, `locked: true`, from 1.33 with no closing version. It is not removed,
which is the point: the file is still in the live gate directory, and reading it is the only way to
learn that the switch the concept page offers you no longer moves.

`MatchLabelKeysInPodTopologySpread` gates `matchLabelKeys`. Alpha, default false, 1.25 to 1.26.
Beta, default true, from 1.27, no closing version. Not removed. Ten releases in beta at the pin, and
the field is documented without a beta warning anywhere except the note and the YAML comment.

`MatchLabelKeysInPodTopologySpreadSelectorMerge` is the odd one. Beta, default true, from 1.34.
There is no alpha stage in the file at all. Its body says it gates `merging of selectors built from
matchLabelKeys into labelSelector`, and that it `can be enabled when matchLabelKeys feature is
enabled` — a gate whose precondition is another gate. It exists because 1.34 changed the behaviour
of a beta field, and someone needed a way back to the old behaviour. A gate with no alpha stage is a
gate that was never a feature; it is an undo button.

The state of the ladder at v1.37, then: three gates removed, one stable and locked but still
present, and two still beta. Every rung the post could have climbed is gone, and two of the rungs
above it are still being climbed.

**Topology**

Three nodes, the [`workhorse` topology](../../strands/lab-topologies.md#workhorse), fresh: a control
plane and two workers, because a spread constraint needs at least three domains before its
arithmetic says anything. Bring all three guests up with [the five provision
steps](../../strands/lab-topologies.md#provision), substituting `topology=workhorse`, install
Kubernetes on each with [the node baseline
procedure](../../strands/lab-topologies.md#node-baseline-steps), bring the cluster up as usual, and
confirm three nodes before starting.

This exercise needs three *schedulable* nodes, so the first *Do* step removes the control plane's
`NoSchedule` taint. That is deliberate and it is also the only way to get an odd number of domains
out of this topology: two zones holding two nodes and one node, which is the asymmetry the post's
arithmetic is interesting on. A `pair` cannot show it — with one node per zone, every skew is 0 or 1
and `maxSkew: 1` never refuses anything.

What three nodes cannot show: real zones. `topology.kubernetes.io/zone` will be a label this
exercise writes by hand, so nothing here exercises the cloud-provider labelling path, and the
built-in default constraint on `topology.kubernetes.io/zone` will only mean what the labels say it
means. Nor can three nodes show the autoscaling limitation the pin lists — a topology domain scaled
to zero nodes disappearing from the scheduler's view — because there is no node pool to scale. Both
are read, not run.

**Do**

1. Make the topology the post's arithmetic needs. Two zones over three nodes is deliberately
   lopsided — two nodes in one, one in the other — because that is where `maxSkew` has something to
   say. With `CP` set to your control-plane node name and `W1` and `W2` set to your two worker
   names:

   ```bash
   kubectl taint node $CP node-role.kubernetes.io/control-plane:NoSchedule-
   kubectl label node $CP $W1 topology.kubernetes.io/zone=zone-a
   kubectl label node $W2 topology.kubernetes.io/zone=zone-b
   TAINTS='
   import json,sys
   for n in json.load(sys.stdin)["items"]:
       m=n["metadata"]
       t=[x["key"]+":"+x.get("effect","") for x in (n["spec"].get("taints") or [])]
       print(m["name"], m["labels"].get("topology.kubernetes.io/zone","-"), t or "none")
   '
   kubectl get nodes -o json | python3 -c "$TAINTS"
   ```

2. Paste the post's field in, unaltered, and then ask the apiserver what it stored. The four keys
   are the four keys the post prints; nothing else is added.

   ```bash
   kubectl apply -f - <<'EOF'
   apiVersion: apps/v1
   kind: Deployment
   metadata: { name: spread, labels: { app: spread } }
   spec:
     replicas: 5
     selector: { matchLabels: { app: spread } }
     template:
       metadata: { labels: { app: spread } }
       spec:
         topologySpreadConstraints:
           - maxSkew: 1
             topologyKey: topology.kubernetes.io/zone
             whenUnsatisfiable: DoNotSchedule
             labelSelector:
               matchLabels: { app: spread }
         containers:
           - name: c
             image: registry.k8s.io/pause:3.10
   EOF
   kubectl get deploy spread \
     -o jsonpath='{.spec.template.spec.topologySpreadConstraints}' | python3 -m json.tool
   kubectl explain Pod.spec.topologySpreadConstraints \
     | sed -n '/^FIELDS:/,$p' | grep -oE '^  [a-zA-Z]+' | sort
   ```

3. Read the placement, then break it the way the pin's *ghost pods* limitation describes. The
   counting helper is defined here and reused by later steps, so keep the shell session.

   ```bash
   kubectl get nodes -o json > /tmp/bw-nodes.json
   ZONES='
   import json,sys,collections
   z={n["metadata"]["name"]: n["metadata"]["labels"].get("topology.kubernetes.io/zone","-")
      for n in json.load(open("/tmp/bw-nodes.json"))["items"]}
   c=collections.Counter(); h=collections.Counter()
   for p in json.load(sys.stdin)["items"]:
       n=p["spec"].get("nodeName")
       c[z.get(n,"pending") if n else "pending"]+=1
       h[n or "pending"]+=1
   print("by zone:", dict(sorted(c.items())))
   print("by node:", dict(sorted(h.items())))
   '
   kubectl rollout status deploy spread --timeout=90s
   kubectl get pods -l app=spread -o json | python3 -c "$ZONES"
   kubectl patch deploy spread --type=json -p='[{"op":"replace",
     "path":"/spec/template/spec/topologySpreadConstraints/0/labelSelector/matchLabels",
     "value":{"app":"nobody"}}]'
   kubectl rollout status deploy spread --timeout=90s
   kubectl get pods -l app=spread -o json | python3 -c "$ZONES"
   kubectl patch deploy spread --type=json -p='[{"op":"replace",
     "path":"/spec/template/spec/topologySpreadConstraints/0/labelSelector/matchLabels",
     "value":{"app":"spread"}}]'
   kubectl rollout status deploy spread --timeout=90s
   ```

4. Test the rule the post states as a validation error. Two constraints on the same `{topologyKey,
   whenUnsatisfiable}` tuple, then the same pair with one value changed. Record the exact wording of
   the refusal; the post names the error class and the pin's note does not.

   ```bash
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: dup, labels: { app: spread } }
   spec:
     topologySpreadConstraints:
       - { maxSkew: 1, topologyKey: topology.kubernetes.io/zone,
           whenUnsatisfiable: DoNotSchedule,
           labelSelector: { matchLabels: { app: spread } } }
       - { maxSkew: 2, topologyKey: topology.kubernetes.io/zone,
           whenUnsatisfiable: DoNotSchedule,
           labelSelector: { matchLabels: { app: spread } } }
     containers: [{ name: c, image: registry.k8s.io/pause:3.10 }]
   EOF
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: dup, labels: { app: spread } }
   spec:
     topologySpreadConstraints:
       - { maxSkew: 1, topologyKey: topology.kubernetes.io/zone,
           whenUnsatisfiable: DoNotSchedule,
           labelSelector: { matchLabels: { app: spread } } }
       - { maxSkew: 2, topologyKey: topology.kubernetes.io/zone,
           whenUnsatisfiable: ScheduleAnyway,
           labelSelector: { matchLabels: { app: spread } } }
     containers: [{ name: c, image: registry.k8s.io/pause:3.10 }]
   EOF
   kubectl delete pod dup --ignore-not-found
   ```

5. Add the field that rewrote the definition of the number the post's arithmetic is against. There
   are two eligible domains and `minDomains` asks for three, so the global minimum becomes 0 and
   every zone's skew becomes its own Pod count. Then try it with the value the pin says it may not
   be combined with.

   ```bash
   kubectl patch deploy spread --type=json -p='[{"op":"add",
     "path":"/spec/template/spec/topologySpreadConstraints/0/minDomains","value":3}]'
   sleep 15
   kubectl get pods -l app=spread -o json | python3 -c "$ZONES"
   kubectl get pods -l app=spread \
     -o jsonpath='{range .items[?(@.status.phase=="Pending")]}{.metadata.name}{"\n"}{end}'
   kubectl patch deploy spread --type=json -p='[{"op":"replace",
     "path":"/spec/template/spec/topologySpreadConstraints/0/whenUnsatisfiable",
     "value":"ScheduleAnyway"}]'
   kubectl patch deploy spread --type=json -p='[{"op":"remove",
     "path":"/spec/template/spec/topologySpreadConstraints/0/minDomains"}]'
   kubectl rollout status deploy spread --timeout=90s
   ```

6. Reproduce the post's sentence about node affinity as a field. The Deployment below is confined to
   `zone-a` by a `nodeSelector`, which is the post's advanced-usage-1 in miniature. Run it first
   with the field absent — the post's behaviour, and the default — and then with the field set to
   the value that switches the post's behaviour off.

   ```bash
   kubectl apply -f - <<'EOF'
   apiVersion: apps/v1
   kind: Deployment
   metadata: { name: narrow, labels: { app: narrow } }
   spec:
     replicas: 4
     selector: { matchLabels: { app: narrow } }
     template:
       metadata: { labels: { app: narrow } }
       spec:
         nodeSelector: { topology.kubernetes.io/zone: zone-a }
         topologySpreadConstraints:
           - maxSkew: 1
             topologyKey: topology.kubernetes.io/zone
             whenUnsatisfiable: DoNotSchedule
             labelSelector: { matchLabels: { app: narrow } }
         containers: [{ name: c, image: registry.k8s.io/pause:3.10 }]
   EOF
   sleep 20
   kubectl get pods -l app=narrow -o json | python3 -c "$ZONES"
   kubectl patch deploy narrow --type=json -p='[{"op":"add",
     "path":"/spec/template/spec/topologySpreadConstraints/0/nodeAffinityPolicy",
     "value":"Ignore"}]'
   sleep 25
   kubectl get pods -l app=narrow -o json | python3 -c "$ZONES"
   kubectl get events --field-selector reason=FailedScheduling \
     -o custom-columns=OBJ:.involvedObject.name,MSG:.message | tail -3
   ```

7. Now the sibling field, whose default is the other one. Taint the single-node zone so no Pod here
   tolerates it, and run the same experiment in reverse: absent first, which is `Ignore`, then set
   to `Honor`.

   ```bash
   kubectl taint node $W2 blogwalk=spread:NoSchedule
   kubectl apply -f - <<'EOF'
   apiVersion: apps/v1
   kind: Deployment
   metadata: { name: tainted, labels: { app: tainted } }
   spec:
     replicas: 4
     selector: { matchLabels: { app: tainted } }
     template:
       metadata: { labels: { app: tainted } }
       spec:
         topologySpreadConstraints:
           - maxSkew: 1
             topologyKey: topology.kubernetes.io/zone
             whenUnsatisfiable: DoNotSchedule
             labelSelector: { matchLabels: { app: tainted } }
         containers: [{ name: c, image: registry.k8s.io/pause:3.10 }]
   EOF
   sleep 20
   kubectl get pods -l app=tainted -o json | python3 -c "$ZONES"
   kubectl patch deploy tainted --type=json -p='[{"op":"add",
     "path":"/spec/template/spec/topologySpreadConstraints/0/nodeTaintsPolicy",
     "value":"Honor"}]'
   sleep 25
   kubectl get pods -l app=tainted -o json | python3 -c "$ZONES"
   kubectl taint node $W2 blogwalk=spread:NoSchedule-
   ```

8. Watch the field that is still beta, and check the behaviour change that got its own gate in 1.34.
   This Deployment surges its full replica count so both revisions exist at once, which is the
   situation `matchLabelKeys` was added for. What to look at is the `labelSelector` stored on each
   Pod.

   ```bash
   kubectl apply -f - <<'EOF'
   apiVersion: apps/v1
   kind: Deployment
   metadata: { name: rev, labels: { app: rev } }
   spec:
     replicas: 3
     selector: { matchLabels: { app: rev } }
     strategy:
       rollingUpdate: { maxUnavailable: 0, maxSurge: 3 }
     template:
       metadata: { labels: { app: rev } }
       spec:
         topologySpreadConstraints:
           - maxSkew: 1
             topologyKey: kubernetes.io/hostname
             whenUnsatisfiable: DoNotSchedule
             labelSelector: { matchLabels: { app: rev } }
             matchLabelKeys: [pod-template-hash]
         containers: [{ name: c, image: registry.k8s.io/pause:3.10 }]
   EOF
   SEL='
   import json, sys
   for p in json.load(sys.stdin)["items"]:
       c = p["spec"]["topologySpreadConstraints"][0]
       print("%-14s rev=%-11s sel=%-46s keys=%s" % (
           p["spec"].get("nodeName"), p["metadata"]["labels"].get("pod-template-hash"),
           json.dumps(c.get("labelSelector")), c.get("matchLabelKeys")))
   '
   kubectl rollout status deploy rev --timeout=120s
   kubectl get pods -l app=rev -o json | python3 -c "$SEL"
   kubectl set env deploy rev BLOGWALK=2
   kubectl rollout status deploy rev --timeout=120s
   kubectl get pods -l app=rev -o json | python3 -c "$SEL"
   ```

9. Ask what happens with no constraint written at all, which is the state the post says an operator
   can configure and the pin says is already configured.

   ```bash
   kubectl create deployment nodefault --image=registry.k8s.io/pause:3.10 --replicas=6
   kubectl rollout status deploy nodefault --timeout=90s
   kubectl get deploy nodefault \
     -o jsonpath='{.spec.template.spec.topologySpreadConstraints}'; echo "<- deployment"
   kubectl get pods -l app=nodefault \
     -o jsonpath='{.items[0].spec.topologySpreadConstraints}'; echo "<- pod"
   kubectl get pods -l app=nodefault -o json | python3 -c "$ZONES"
   ```

10. The guardrail step, and the one that settles a sentence. Both node-policy notes tell you that
    you can disable the gate. The gate record says it is locked. Ask the apiserver first, then ask
    kube-scheduler by giving it the flag the note describes — and keep the copy, because the
    scheduler will need it back.

    ```bash
    kubectl get --raw /metrics | grep NodeInclusionPolicyInPodTopologySpread \
      || echo "not reported here"
    sudo cp /etc/kubernetes/manifests/kube-scheduler.yaml /tmp/bw-scheduler.yaml
    sudo python3 - <<'PY'
    p = "/etc/kubernetes/manifests/kube-scheduler.yaml"
    ls = open(p).read().split("\n")
    i = [n for n, l in enumerate(ls) if l.strip() == "- kube-scheduler"][0]
    pad = " " * (len(ls[i]) - len(ls[i].lstrip()))
    ls.insert(i + 1, pad + "- --feature-gates=NodeInclusionPolicyInPodTopologySpread=false")
    open(p, "w").write("\n".join(ls))
    PY
    sleep 40
    kubectl -n kube-system get pod -l component=kube-scheduler
    kubectl -n kube-system logs -l component=kube-scheduler --tail=4 2>&1 | tail -4
    sudo cp /tmp/bw-scheduler.yaml /etc/kubernetes/manifests/kube-scheduler.yaml
    sleep 40
    kubectl -n kube-system get pod -l component=kube-scheduler
    ```

**Expect**

Step 1 should print three node names, two of them labelled `zone-a` and one `zone-b`, and no taints
anywhere. A schedulable control plane is not how you would run a cluster; it is how you get three
domains out of three machines, and it is the only reason this exercise fits the topology. Note which
of your two workers ended up alone in `zone-b`, because every later step's asymmetry is that node.

Step 2 is the exercise in one screen. The `jsonpath` should print exactly four keys — the four the
post prints, in the post's order, with nothing defaulted in beside them. The `explain` output should
list eight field names. Four of eight, and the four that are missing from the stored object are
missing because absence is how they express their defaults. That is why a 2020 manifest still
round-trips through a v1.37 apiserver unchanged.

Step 3, first read: five replicas over two zones with `maxSkew: 1`, so expect 3 and 2, with the 3 in
`zone-a` because that is the zone with two nodes to put them on. Work the post's arithmetic against
the numbers you get and they should agree. After the patch, expect the constraint to stop
constraining: a `labelSelector` matching nothing means every domain holds zero matching Pods, the
skew is zero everywhere, and `DoNotSchedule` refuses nothing. Record where the Pods land — the point
is not the distribution, it is that a hard constraint became inert without erroring, which is
exactly what the pin's *ghost pods* entry warns about.

Step 4's first apply should be refused and the second accepted. Keep the refusal's exact wording:
the post says the Pod creation `will be blocked returning a validation error` and the pin's note
(`:74`) states the same rule without naming an error at all, so the cluster is the only one of the
three that tells you what the failure actually is. The second apply differs from the first in one
word, and that word is the second half of the tuple the rule is about.

Step 5 is the arithmetic changing under the post's feet. Two eligible domains and `minDomains: 3`
means the global minimum is 0 by definition, so a zone may hold at most `maxSkew` Pods: expect two
Running — one per zone — and three Pending. Then expect the `ScheduleAnyway` patch to be refused,
because the pin says `you can only specify minDomains in conjunction with whenUnsatisfiable:
DoNotSchedule` and this is where you find out that is enforced rather than advised. The final patch
puts the Deployment back to the post's four fields.

Step 6 should give four Pods in `zone-a` on the first read and one Pod in `zone-a` plus three
Pending on the second. Nothing about the Pods changed between the two reads except a field the post
did not have. With the field absent the calculation covers only the nodes the `nodeSelector` allows,
which is the post's sentence; with `Ignore` it covers `zone-b` too, `zone-b` holds no matching Pods,
the global minimum drops to 0, and `maxSkew: 1` caps `zone-a` at one. The `FailedScheduling` events
should name the constraint; that message is the clearest thing the scheduler ever says about this
field.

Step 7 is step 6 in a mirror. Expect one Running and three Pending first — because the absent field
means `Ignore`, and the tainted zone counts as a domain the Pods cannot reach — and four Running in
`zone-a` after the patch to `Honor`. Two fields, one gate, opposite defaults, opposite outcomes from
the same starting cluster. If you can hold only one fact from this exercise about the four added
fields, hold this one.

Step 8 has two things to read. First, whether `pod-template-hash` appears inside each Pod's stored
`labelSelector`: the pin says that since v1.34 the keys named in `matchLabelKeys` are `explicitly
merged into labelSelector`, so it should, and the merged value should differ between the two
revisions. Second, the placement: six Pods over three nodes, two per node, one from each revision,
which `maxSkew: 1` on `kubernetes.io/hostname` would have made awkward if both revisions counted as
one group. This is the only field in the set whose effect you can see in the object rather than only
in the outcome.

Step 9 should print an empty result for the Deployment, an empty result for the Pod, and a spread
placement anyway — roughly two per node. There is no field anywhere in the cluster recording why.
The reason is `maxSkew: 3` on `kubernetes.io/hostname` and `maxSkew: 5` on
`topology.kubernetes.io/zone`, compiled into kube-scheduler as its default plugin arguments, and the
only way to see them from here is to read them at
`concepts/scheduling-eviction/topology-spread-constraints.md:558-564`. Six Pods is not enough to
strain a `maxSkew` of 3, so what you are watching is the scoring, not the constraint.

Step 10 has no predicted output, only a question. The metric grep may print a
`kubernetes_feature_enabled` line for the gate or nothing at all, depending on whether the apiserver
registers a scheduler gate; record which. Then record what kube-scheduler does with the flag its own
documentation page tells you to use: whether the static Pod comes back, and what the last lines of
its log say. Whatever that message is, hold it against the two notes at `:192-193` and `:206-207`,
which say `you can disable it by disabling the NodeInclusionPolicyInPodTopologySpread feature gate`,
and against the gate record's `locked: true`. Then put the manifest back and confirm the scheduler
returns before you go anywhere near the teardown, because nothing after this line schedules without
it.

**Read on** — four are answerable from the pin, and the fifth is the field the post says it does

not have.

1. Is `SelectorSpread` removed or disabled by default? Settling it means starting kube-scheduler
   with a `KubeSchedulerConfiguration` that names the plugin in its `enabled` list and seeing
   whether the name is accepted. `reference/scheduling/config.md:40-122` has the shape — and the
   `#profiles` anchor there is where the post's dead `/docs/reference/scheduling/profiles/` link now
   leads. The plugin list at `:123-207` is the other half of the answer: check whether
   `SelectorSpread` is in it.

2. The three worked examples the pin ships:
   `examples/pods/topology-spread-constraints/one-constraint.yaml`, `two-constraints.yaml` and
   `one-constraint-with-nodeaffinity.yaml`. The third is the post's advanced-usage-1 as a file you
   can apply, and the second is its advanced-usage-2. Read them against the post's diagrams; the
   diagrams are still the better explanation and the files are the runnable one.

3. `topology-spread-constraints.md:598-621` sets the field against `podAffinity` and
   `podAntiAffinity`, which is the comparison the post opens with. Six years later the pin makes the
   same argument the post made, in fewer words, and ends by pointing at the *Motivation* section of
   KEP 895 — linked from `:620-621` — for the case the post was making informally.

4. The two definitions of *eligible domain*, at `:100-101` and `:125-126`. Read them side by side
   and work out what `minDomains: 3` counts on a cluster where `nodeAffinityPolicy: Ignore` and a
   `nodeSelector` disagree about which nodes belong. The page does not answer it, and neither does a
   cluster unless you already know which answer to look for.

5. Unanswerable from the pin: why `topologyValues` was never built. The post names the gap, the pin
   has no occurrence of the name, no successor field, and no note saying the idea was rejected. Four
   fields were added to this constraint between 1.24 and 1.34 and none of them is this one, which is
   evidence of a decision but not a record of one. The exercises cannot get further than that.

**Teardown** — five workloads of yours, two labels, one taint, and two files.

```bash
kubectl delete deploy spread narrow tainted rev nodefault --ignore-not-found
kubectl delete pod dup --ignore-not-found
kubectl label node $CP $W1 $W2 topology.kubernetes.io/zone-
kubectl taint node $W2 blogwalk=spread:NoSchedule- 2>/dev/null || true
kubectl taint node $CP node-role.kubernetes.io/control-plane=:NoSchedule
diff /tmp/bw-scheduler.yaml /etc/kubernetes/manifests/kube-scheduler.yaml && echo "manifest restored"
rm -f /tmp/bw-nodes.json /tmp/bw-scheduler.yaml
```

The `diff` is the line that matters; run it before you delete the backup. Re-tainting the control
plane is not required if you are about to destroy the guests, and this topology is `fresh` for every
exercise that asks for it, so destroying them is the ordinary path — but re-taint it if you are
keeping the cluster, because a schedulable control plane is a habit that outlives the reason you
made it one. The two zone labels go the same way. What does not need undoing is anything to do with
the field itself: every change this exercise made to a spread constraint was made inside a
Deployment it also deleted, and the cluster's own default constraints were never touched, because
there is no object to touch.
