<a id="kubernetes-v1-36-fine-grained-kubelet-authorization-ga"></a>

# The permission the post's worked example gives up was never the one the endpoint it scrapes checks, the gate it says is locked is not marked locked in the file that records the ladder, and none of the seven subresources it tells you to grant instead is written anywhere in the tree

**Post** — [Kubernetes v1.36: Fine-Grained Kubelet API Authorization Graduates to GA](https://kubernetes.io/blog/2026/04/24/kubernetes-v1-36-fine-grained-kubelet-authorization-ga/),
2026-04-24.

299 lines, 11,403 bytes, one author — Vinayak Goyal, Google — nine fenced blocks and two tables, and
no images. The twenty-sixth of 2026's fifty-nine published rows and the fifth `walk` among them.
Every command in it runs against the kubelet's HTTPS port rather than against the API server, which
is the first time in this year's walks that the thing being measured answers on a port of its own.

**As written**

The announcement is three sentences long and the first two of them are the argument. `:10-12`
declares that fine-grained `kubelet` API authorization is generally available in v1.36 on behalf of
SIG Auth and SIG Node. `:14-19` gives the ladder — alpha and opt-in at v1.32, beta and on by default
at v1.33, now *generally available and the feature gate is locked to enabled* — and states the
payoff: the feature *replaces the need to grant the overly broad `nodes/proxy` permission for common
monitoring and observability use cases*.

The motivation section is `:21-45`. `:23-25` describes the kubelet's HTTPS endpoint as serving data
of varying sensitivity, from pod listings to container exec. `:27-32` is the claim the rest of the
post rests on: before the feature, *almost all `kubelet` API paths were mapped to a single
`nodes/proxy` subresource*, so *any workload needing to read metrics or health status from the
`kubelet` required `nodes/proxy` permission*. `:36-41` draws the consequence — monitoring agents,
log collectors and health checkers holding a node-level superuser capability — and `:43-45` links
the issue that carried the complaint and the KEP that answered it.

`:47-72` is the sharper half of the motivation, and it is new material rather than a summary of the
KEP. Security researchers, the post says at `:49-53`, demonstrated in early 2026 that `nodes/proxy
GET` alone can be abused to execute commands in any pod on a reachable node. `:55-63` gives the
mechanism: the WebSocket protocol requires an HTTP `GET` for the handshake, the kubelet maps that
`GET` to the RBAC **get** verb, and it does not make a second check for **create** before the write
half of the connection proceeds. The fence at `:65-72` is a `websocat` invocation against port 10250
with a bearer token, and beneath it the output `uid=0(root) gid=0(root) groups=0(root)`.

`:74-102` is the feature itself. A ten-row table at `:81-92` maps kubelet API paths to a resource
and a subresource: `/stats/*` to `stats`, `/metrics/*` to `metrics`, `/logs/*` to `log`, `/pods` and
`/runningPods/` to `pods, proxy`, `/healthz` to `healthz, proxy`, `/configz` to `configz, proxy`,
`/spec/*` to `spec`, `/checkpoint/*` to `checkpoint`, and everything else to `proxy`. `:94-98`
describes the dual check for the four endpoints that list two subresources: a `SubjectAccessReview`
for the specific one, and on failure a retry against `nodes/proxy`. `:100-102` calls this a smooth
migration path.

The worked example is `:104-138`. A monitoring `DaemonSet` that scrapes `/metrics` previously needed
the *Old approach: overly broad* ClusterRole at `:110-120`, granting **get** on `nodes/proxy`; with
the feature it can use the *New approach: least privilege* at `:125-135`, granting **get** on
`nodes/metrics` and `nodes/stats`. `:137-138` states the win: the agent can read metrics and stats
*without ever being able to execute commands in containers*. `:140-158` then says the built-in
`system:kubelet-api-admin` ClusterRole is automatically updated to cover all the new subresources,
and lists nine of them. `:160-173` promises that upgrades are seamless because of the fallback, that
the API server is unaffected, and that mixed-version clusters are handled.

`:175-258` is a recipe for confirming the feature is on. Step 1 at `:184-199` is one YAML block
holding a ServiceAccount and a ClusterRole granting **get** on `nodes/metrics`; step 2 at `:203-216`
is the ClusterRoleBinding; `:220-224` applies `serviceaccount.yaml`, `clusterrole.yaml` and
`clusterrolebinding.yaml`. Step 3 at `:228-235` runs a pod from `curlimages/curl` with that
ServiceAccount, and `:239-249` reads the projected token and curls `https://$NODE_IP:10250/metrics`,
filtering for the feature gate. `:253-255` prints the expected line,
`kubernetes_feature_enabled{name="KubeletFineGrainedAuthz",stage="GA"} 1`, and `:257-258` is a note
saying to replace `$NODE_IP` with a real address.

The tail is short. `:262-266` is a three-row ladder table for v1.32, v1.33 and v1.36. `:270-286`
expects ecosystem adoption, policy engines that reject `nodes/proxy` grants, and an eventual
deprecation path for `nodes/proxy` in monitoring; `:273-275` says the research it cites shows
unlogged remote code execution and that the risk *is present in the default RBAC configurations of
dozens of widely deployed Helm charts*. `:288-299` names the two SIGs, two Slack channels and
KEP-2862.

**As it runs now**

**The permission the worked example gives up was never the one that endpoint checked.** The
motivating sentence at `:27-32` says any workload needing to read metrics from the kubelet required
`nodes/proxy`, and the *Old approach: overly broad* ClusterRole at `:110-120` is that grant written
out. The pinned mapping that applies when the gate is off is
`reference/access-authn-authz/kubelet-authn-authz.md:68-75`, and its first two rows send `/stats/*`
to `nodes/stats` and `/metrics/*` to `nodes/metrics`. [The 2016 node dashboard
row](../2016/12-visualize-kubelet-performance-with-node-dashboard.md) quotes those rows and builds a
metrics-only ServiceAccount from them, nine years before this feature existed. So the *New approach:
least privilege* at `:125-135` is a rule that was already correct before v1.32, and the old approach
was never the approach.

**Half of the motivating sentence is right, and it is the half the example does not use.** The same
sentence at `:29-31` names *metrics or health status*, and `/healthz` genuinely was in the
catch-all: it has no row in the coarse table, so it fell to `nodes/proxy` like everything else, and
the fine-grained table is where it first gets a subresource of its own. A monitoring agent that
scrapes `/healthz` is the example the post needed. A monitoring agent that scrapes `/metrics` is the
example the post chose.

**One page carries two tables that disagree about `/spec` and `/checkpoint`.** The coarse table at
`kubelet-authn-authz.md:68-75` has six rows, two of which are `/spec/\*` to `spec` and
`/checkpoint/\*` to `checkpoint`. The fine-grained table at `:108-117` has eight rows and neither of
those two is among them, so a literal reading says that when the gate is on, `/spec` and
`/checkpoint` fall into *all others* and are guarded by `proxy` — the feature making authorization
coarser for two paths in the act of making it finer for four. The post's table at `:81-92` has ten
rows: the pin's eight plus the two that went missing. Whoever wrote the post reconciled the two
tables and did not say so; whoever wrote the page did not reconcile them at all. Step 4 asks a v1.35
kubelet which of the two readings the code holds.

**The two lists of attributes the API server must hold disagree in the same place.** Below each
table the page states what the identity in `--kubelet-client-certificate` needs. The coarse list at
`:93-97` names five subresources: `proxy`, `stats`, `log`, `spec`, `metrics`. The gated list at
`:124-130` names seven: `proxy`, `stats`, `log`, `metrics`, `configz`, `healthz`, `pods`. It adds
the three new ones and silently drops `spec`, and `checkpoint` is absent from both. Turning on a
feature that only ever adds authorization paths is documented as removing one.

**The post's nine-item list of what the built-in role gained matches neither.** `:148-158` lists
`nodes/proxy`, `stats`, `metrics`, `log`, `spec`, `checkpoint`, `configz`, `healthz` and `pods` —
the union of the pin's two lists, in the post's own table order. The page that tells you the role is
updated says only that it should cover *all the above mentioned subresources*
(`kubelet-authn-authz.md:132-134`), which is the seven-item list; and `rbac.md:780`, the row for
`system:kubelet-api-admin` in the default-roles table, describes it in one clause — *Allows full
access to the kubelet API* — and enumerates nothing. Step 9 binds a ServiceAccount to the real role
and asks about all nine names one at a time.

**Every occurrence of `nodes/proxy` in the documentation is a warning against granting it.** The
string appears eight times under `content/en/docs`, across four files:
`concepts/security/rbac-good-practices.md:143`, `:148` and `:149`;
`concepts/security/api-server-bypass-risks.md:68` and `:91`;
`concepts/cluster-administration/system-logs.md:259`; and `kubelet-authn-authz.md:79` and `:83`. Not
one of them is a rule you would write; every one is a caution. The mitigation list is the clearest
case: *Avoid granting the `nodes/proxy` catch-all permission, even with just the **get** verb.
Instead, grant granular permissions* (`api-server-bypass-risks.md:91-92`), where *granular
permissions* is a link to the fine-grained section.

**And not one of the granular permissions is written in the form the reader has to type.** Count
occurrences of the `nodes/<subresource>` string under `content/en/docs` for each of the seven the
feature gives you: `nodes/stats` 0, `nodes/metrics` 0, `nodes/log` 0, `nodes/spec` 0,
`nodes/checkpoint` 0, `nodes/configz` 0, `nodes/healthz` 0. `nodes/pods` occurs once, in
`concepts/cluster-administration/dra.md:100`, in the phrase *number of nodes/pods*, where it is not
a subresource at all. The tables write the pair in two columns, because that is the shape of a
`SubjectAccessReview`; an RBAC rule wants the slashed string, and the slashed string that the tree
does write is the one the same tree warns you off eight times.

**Both documented ways to read `/configz` route you through `nodes/proxy`.**
`tasks/administer-cluster/kubelet-config-file.md:167` and
`tasks/administer-cluster/configure-feature-gates.md:193` both stand up `kubectl proxy` and fetch
`/api/v1/nodes/<node-name>/proxy/configz`. That path is the API server's `nodes/proxy` subresource,
not the kubelet's `configz` one — [the 2023 node log query row](../2023/03-node-log-query-alpha.md)
settles the two hops and why the identity changes between them. So the feature gave `/configz` a
subresource of its own, and every recipe in the tree for reading `/configz` still asks for the
permission the feature exists to avoid.

**The gate the post calls locked is not marked locked.**
`reference/command-line-tools-reference/feature-gates/KubeletFineGrainedAuthz.md` records three
stages — alpha from v1.32, beta from v1.33 to v1.35, stable from v1.36 — and no `locked` key on any
of them. Forty-nine gate files in that directory carry `locked: true`, always on the stable stage.
Eighteen gates reach stable at v1.36 and four of those carry it: `ProcMountType`,
`UserNamespacesSupport`, `VolumeAttributesClass` and `KubeletPSI`. This one does not, and neither
does `NodeLogQuery`, which graduates in the same release and belongs to the 2023 row above. The
sentence at `:16-17` is a claim about the code; the pin's record of the same release says nothing.

**The release announcement is the same paragraph with the lock taken out.**
`blog/_posts/2026/kubernetes-v1-36-release/index.md:49-60` is this post's opening, sentence for
sentence, under the heading *Stable: Fine-grained API authorization* — except that where the
standalone post says *the feature is generally available and the feature gate is locked to enabled*,
the release announcement at `:57` says only *Now, the feature is generally available*. The clause
the pin's gate file cannot support is the clause the release announcement does not make.

**The two releases that changed behaviour were never announced.** The gate name occurs in two files
under `blog/_posts`: this post and the v1.36 release announcement. Nothing was published when the
gate arrived in v1.32, and nothing was published in v1.33, which is the release where it flipped to
on by default and every cluster in the world started making a second authorization call it had not
made before. The archive got one post about this feature, at the end, for the release in which
nothing observable changed.

**The discovery the post attributes to researchers is in the pinned documentation three times.**
`kubelet-authn-authz.md:82-84`, `api-server-bypass-risks.md:67-69` and
`rbac-good-practices.md:147-148` all say that some of these endpoints support WebSocket protocols
over HTTP `GET`, that `GET` is authorized with the **get** verb, and that **get** on `nodes/proxy`
is therefore not a read-only permission. The three sentences differ only in their last clause. [The
2016 node dashboard row](../2016/12-visualize-kubelet-performance-with-node-dashboard.md) quotes the
first of them and makes it the pivot of its own step 7. What the cited research adds is a working
client and a measurement of how widespread the grant is; what the post frames as *more severe than
it might appear at first glance* (`:49`) is a thing the site had already written down in three
places.

**The feature does not narrow `nodes/proxy`; it narrows what you have to ask for.** `/exec` has no
row in either table, so it is *all others* in both, and the warning at
`kubelet-authn-authz.md:77-85` sits above the fine-grained section and is not repeated, qualified or
amended inside it. A principal holding **get** on `nodes/proxy` after the graduation reaches exactly
what it reached before. `:277-280` says that moving monitoring tools to `nodes/metrics` *directly
eliminates the WebSocket RCE attack surface for those workloads*, which is true of a workload that
gives the old grant up and true of nothing else. Step 6 puts both identities against the same
`/exec` handshake and reads the two status lines.

**For four of the seven paths, the fallback makes the feature invisible from the client side.** The
dual check at `kubelet-authn-authz.md:103-106` tries the specific subresource and falls back to
`proxy`, so a client that already holds `nodes/proxy` gets the same answer for `/pods`,
`/runningPods`, `/healthz` and `/configz` whether the gate is on or off. The only observation that
separates the two states is a client holding the specific subresource and *not* `proxy`, which is
the identity step 2 builds and step 7 re-measures with the gate turned off. There is a second
observable, and it is on the API server rather than the kubelet: the failed first check is a
`SubjectAccessReview` that would not otherwise be sent. Step 5 counts them.

**The verification recipe applies three files it printed as two.** `:184-199` is a single YAML block
holding both the ServiceAccount and the ClusterRole; `:203-216` is the binding; and `:220-224`
applies `serviceaccount.yaml`, `clusterrole.yaml` and `clusterrolebinding.yaml`. There is no third
file to have saved. `:239-249` then reads `$NODE_IP`, which nothing in the pod ever sets, prints the
output as though the command had run at `:253-255`, and only at `:257-258` adds the note saying to
substitute a real address. The order is the tell: the expected output sits between the command that
cannot produce it and the note that explains why.

**The image the recipe runs is not one the project publishes, and the gate-checking method the
documentation offers cannot read a kubelet gate.** `:230` runs `curlimages/curl`, a Docker Hub
image, where the house standard everywhere else in the tree is `registry.k8s.io`.
`configure-feature-gates.md:201-215` — the metrics method in [the 2025 z-pages
row](../2025/12-kubernetes-v1-35-structured-zpages.md)'s list of four — reads `kubectl get --raw
/metrics`, which is the API server's metrics endpoint and knows nothing about the kubelet's gates.
The remaining method that does reach the kubelet is `configz` through `nodes/proxy`. So the post's
recipe exists because the documented ones do not answer the question, and it is the only place in
reach that reads a kubelet feature gate from the kubelet.

**What this exercise does not cover, and where it lives.** The two-hop shape of every request that
reaches a kubelet through the API server — your identity at the first hop, the API server's at the
second, and why that makes the kubelet-side subresource invisible to `kubectl auth can-i` — is [the
2023 node log query row](../2023/03-node-log-query-alpha.md), which also owns `/logs/*`, the
certificate the API server presents to the kubelet, and the fine-grained section read end to end.
The coarse path-to-subresource table and the `nodes/proxy` warning, met for the first time and
tested through the API server's proxy path, are [the 2016 node dashboard
row](../2016/12-visualize-kubelet-performance-with-node-dashboard.md). RBAC itself — how the default
ClusterRoles are reconciled on restart, what aggregation does, and why rules are purely additive —
is [the 2017 RBAC row](../2017/06-using-rbac-generally-available-18.md), and what the post calls
*automatically updated* at `:142-146` is that reconciliation and not something this feature does.
Nothing here executes a command in a container: step 6 stops at the HTTP status line of the
handshake, which is the authorization decision and not the session. And nothing here can compare
v1.36 behaviour with v1.35 behaviour, because the lab has one release on it.

**The diff, and why**

**Wrong when it was published.** Three things, and the largest is the worked example. The old
ClusterRole at `:110-120` grants a permission that the endpoint in the example never consulted, and
the new one at `:125-135` is a rule that a reader could have written in v1.31 and every release
before it. The lock at `:16-17` is a property the pin's own record of the gate does not carry, and
the release announcement that repeats the paragraph leaves it out. And the verification recipe
applies three files after printing two. None of these needed a later release to become wrong.

**Still right.** The mechanism is described accurately and the caution around it is well judged. The
dual check at `:94-98` matches `kubelet-authn-authz.md:103-106` clause for clause, including which
four endpoints get it. The upgrade section at `:160-173` is correct on all three counts: the
fallback does preserve existing grants, the API server's identity is covered by a built-in role
either way, and a version skew in either direction lands on `nodes/proxy`. The WebSocket risk is
real, the pin states it in three places, and the post is the only document in reach that says out
loud what a monitoring agent should be granted instead. The reasoning is sound; the arithmetic under
it is not.

**Overtaken by stasis.** `kubelet-authn-authz.md` grew a fine-grained section and kept the page
above it untouched, and the seam shows in two places: the new table at `:108-117` lost the `/spec`
and `/checkpoint` rows the old one at `:68-75` has, and the new attribute list at `:124-130` lost
`spec` from the old one at `:93-97`. Neither omission is plausible as a decision — nothing in the
feature touches those paths — and both have survived the graduation. Elsewhere, both pages that
teach a reader to read `/configz` still route through `nodes/proxy`, and the mitigation at
`api-server-bypass-risks.md:91-92` sends the reader to a section that never prints a rule. The pin
recommends the feature and has not rewritten anything around it.

**Never absorbed.** A GA graduation that changed nothing a reader can find. Not one of the seven
subresources it makes grantable is written anywhere under `content/en/docs` in the `nodes/<name>`
form an RBAC rule needs; the only string of that shape in the tree is the one every page warns
against. No page gained the *New approach: least privilege* manifest, or anything like it. The
default-roles table still describes `system:kubelet-api-admin` in a single clause. The one edit the
pin carries for v1.36 is a third stage in a gate file that is never rendered — `_build: render:
false` — and even that stage is missing the `locked` key the post's second paragraph asserts.

**The ladder**

`KubeletFineGrainedAuthz`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.32 |
| beta | `true` | — | v1.33 – v1.35 |
| stable | `true` | — | v1.36 – |

Four releases from introduction to graduation, one of them alpha, three beta. The rung that matters
for this exercise is the last beta one. The clusters run v1.35, which is the final release in which
the gate is settable at all — from v1.36 the stable row is the only row, and the post says it is
locked besides. So the lab is standing on the last cluster in the archive's reach that can turn this
feature off and watch what changes. Every measurement in steps 4 through 7 depends on that, and none
of them will be repeatable on a cluster one release newer.

The empty `locked` column is the finding, not an omission in the table above: forty-nine of the gate
files carry `locked: true` on their stable stage and this is not one of them. Of the eighteen gates
that reach stable at v1.36, four carry it — `ProcMountType`, `UserNamespacesSupport`,
`VolumeAttributesClass` and `KubeletPSI` — and fourteen do not. [The 2022 user namespaces
row](../2022/10-userns-alpha.md) owns the first of those ladders; `NodeLogQuery`, which graduates in
the same release as this gate and is likewise unmarked, belongs to [the 2023 node log query
row](../2023/03-node-log-query-alpha.md). Whether the code locks the gate is a question about the
code. What the pin records is that the file does not say so, and that the file for a feature
announced on an adjacent day of the same release does.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180`, 4096MB, 4
CPUs, 25G, [provisioned](../../strands/lab-topologies.md#provision) and
[baselined](../../strands/lab-topologies.md#node-baseline-steps) as usual, running Kubernetes v1.35.
One node is right and a second would be a distraction: the subject is a single kubelet's
authorization of requests to its own HTTPS port, and on a one-node cluster the control plane and the
kubelet under test are the same machine, so every `curl` in the exercise can use `127.0.0.1` and no
certificate has to be trusted across a network. Everything created lives in a namespace called
`bw-kauthz`, except four ClusterRoles, five ClusterRoleBindings and one appended block in the
kubelet's configuration file, which *Teardown* removes. Step 7 restarts the kubelet twice; on a
single-node cluster that is a short outage of the only node and nothing else. Steps 1 to 9 run on
the node over `ssh zain@10.10.10.180`; step 10 runs offline against a checkout of
`kubernetes/website` at the pin, with `W` set to its `content/en` directory.

**Do**

1. Establish what the kubelet is configured to do with an incoming request, and what the built-in
   role already carries. Open one session with `ssh zain@10.10.10.180` and stay in it; every fence
   up to step 10 is written as though you are already there. The two cache lines in the
   authorization block are the ones to write down — they decide how step 5 has to be read.

   ```sh
   kubectl version -o json | grep gitVersion
   N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}'); echo "node $N"
   sudo grep -n -A14 '^authentication:' /var/lib/kubelet/config.yaml
   sudo grep -n '^featureGates' /var/lib/kubelet/config.yaml || echo "no featureGates block"
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" \
     | grep 'kubernetes_feature_enabled.*KubeletFineGrainedAuthz'
   kubectl get clusterrole system:kubelet-api-admin \
     -o jsonpath='{range .rules[*]}{.resources}{"\n"}{end}'
   kubectl create namespace bw-kauthz
   kubectl -n bw-kauthz run bw-target --image=busybox:1.36 --command -- sleep 3600
   ```

2. Build five identities that differ only in which subresource they hold. Four get exactly one
   `nodes/<subresource>` each and the fifth gets nothing, which is the control. `spec` is in the set
   because it is the path the pin's two tables disagree about; `configz` is in it because it is the
   one the fallback covers.

   ```sh
   for s in none proxy metrics configz spec; do
     kubectl -n bw-kauthz create serviceaccount sa-$s
   done
   for s in proxy metrics configz spec; do
     kubectl create clusterrole bw-$s --resource=nodes --subresource=$s --verb=get
     kubectl create clusterrolebinding bw-$s --clusterrole=bw-$s \
       --serviceaccount=bw-kauthz:sa-$s
   done
   for s in configz spec; do
     echo "sa-$s: nodes/$s $(kubectl auth can-i get nodes/$s \
       --as=system:serviceaccount:bw-kauthz:sa-$s), nodes/proxy $(kubectl auth can-i \
       get nodes/proxy --as=system:serviceaccount:bw-kauthz:sa-$s)"
   done
   ```

3. Reach the kubelet directly, which nothing else in this archive has done. Port 10250 serves a
   certificate the cluster CA did not sign, so `-k` is not optional; the identity comes from a
   bearer token the API server minted, and the kubelet turns it into a user with a `TokenReview`
   before it authorizes anything. Three requests establish the frame: no credential, a credential
   with the wrong subresource, and a credential with the right one.

   ```sh
   K=https://127.0.0.1:10250
   curl -sk -o /dev/null -w 'anonymous      /metrics -> %{http_code}\n' $K/metrics
   TC=$(kubectl -n bw-kauthz create token sa-configz)
   TM=$(kubectl -n bw-kauthz create token sa-metrics)
   curl -sk -o /dev/null -w 'configz-only   /metrics -> %{http_code}\n' \
     -H "Authorization: Bearer $TC" $K/metrics
   curl -sk -o /dev/null -w 'metrics-only   /metrics -> %{http_code}\n' \
     -H "Authorization: Bearer $TM" $K/metrics
   curl -sk -H "Authorization: Bearer $TM" $K/metrics \
     | grep 'kubernetes_feature_enabled.*KubeletFineGrainedAuthz'
   ```

4. The matrix, with the gate in its default state. Five identities against eight paths, reading
   nothing but the status code. This is the table the pin has two versions of; the cells that decide
   between them are the `spec` row and the `/spec/` column.

   ```sh
   P="/metrics /stats/summary /pods /runningPods/ /healthz /configz /logs/ /spec/"
   printf '%-14s' ''; for u in $P; do printf '%-16s' "$u"; done; echo
   for s in none proxy metrics configz spec; do
     T=$(kubectl -n bw-kauthz create token sa-$s)
     printf '%-14s' "$s"
     for u in $P; do
       printf '%-16s' "$(curl -sk -m 10 -o /dev/null -w '%{http_code}' \
         -H "Authorization: Bearer $T" "https://127.0.0.1:10250$u")"
     done
     echo
   done
   ```

5. Count the authorization calls the kubelet makes, and find out why counting is harder than it
   looks. A request the fine-grained check refuses costs two `SubjectAccessReview` calls and a
   request it allows costs one, so the dual check is visible from the API server's own metrics — but
   only until the kubelet's authorization cache swallows the difference. Do one cold request per
   identity, then twenty more, and compare the two deltas against the TTLs from step 1.

   ```sh
   C() { kubectl get --raw /metrics | grep '^apiserver_request_total{' \
         | grep 'resource="subjectaccessreviews"' | awk '{s+=$NF} END {print s+0}'; }
   for s in proxy configz; do
     T=$(kubectl -n bw-kauthz create token sa-$s)
     sleep 35
     B=$(C); curl -sk -o /dev/null -H "Authorization: Bearer $T" \
       https://127.0.0.1:10250/configz; A=$(C)
     echo "$s cold /configz -> $((A-B)) SubjectAccessReviews"
     B=$(C)
     for i in $(seq 20); do
       curl -sk -o /dev/null -H "Authorization: Bearer $T" https://127.0.0.1:10250/configz
     done
     A=$(C); echo "$s next 20      -> $((A-B)) SubjectAccessReviews"
   done
   ```

6. Put the warning to the test, and stop at the status line. A WebSocket handshake is an HTTP `GET`
   with four upgrade headers, so `curl` can perform exactly the authorization step the pinned
   warning describes without ever sending a frame. A `101` means the kubelet authorized an exec
   session and was ready to start it; a `403` means it refused. Nothing runs in the container either
   way — the point of the step is which of the two identities gets the `101`.

   ```sh
   E="https://127.0.0.1:10250/exec/bw-kauthz/bw-target/bw-target?command=id&output=1&error=1"
   for s in proxy metrics configz; do
     T=$(kubectl -n bw-kauthz create token sa-$s)
     curl -sk -m 5 -o /dev/null -w "$s -> %{http_code}\n" --http1.1 \
       -H "Authorization: Bearer $T" \
       -H 'Connection: Upgrade' -H 'Upgrade: websocket' \
       -H 'Sec-WebSocket-Version: 13' -H 'Sec-WebSocket-Key: AAAAAAAAAAAAAAAAAAAAAA==' \
       -H 'Sec-WebSocket-Protocol: v4.channel.k8s.io' "$E"
   done
   ```

7. Turn the feature off and run the matrix again. This is the measurement the post's own release
   cannot make, because from v1.36 the gate has one setting. Guard the append: if the configuration
   file already has a `featureGates` block, a second top-level key of the same name is a parse error
   and the kubelet will not come back.

   ```sh
   sudo cp /var/lib/kubelet/config.yaml /tmp/bw-kubelet.yaml.bak
   sudo grep -q '^featureGates' /var/lib/kubelet/config.yaml \
     && echo "EDIT BY HAND: a featureGates block already exists" \
     || printf 'featureGates:\n  KubeletFineGrainedAuthz: false\n' \
        | sudo tee -a /var/lib/kubelet/config.yaml >/dev/null
   sudo systemctl restart kubelet
   kubectl wait --for=condition=Ready "node/$N" --timeout=120s
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" \
     | grep 'kubernetes_feature_enabled.*KubeletFineGrainedAuthz'
   P="/metrics /stats/summary /pods /runningPods/ /healthz /configz /logs/ /spec/"
   for s in proxy metrics configz spec; do
     T=$(kubectl -n bw-kauthz create token sa-$s)
     printf '%-14s' "$s"
     for u in $P; do
       printf '%-16s' "$(curl -sk -m 10 -o /dev/null -w '%{http_code}' \
         -H "Authorization: Bearer $T" "https://127.0.0.1:10250$u")"
     done
     echo
   done
   sudo cp /tmp/bw-kubelet.yaml.bak /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet
   kubectl wait --for=condition=Ready "node/$N" --timeout=120s
   ```

8. Take the other hop, and watch the new subresource stop mattering. The documented way to read
   `/configz` goes through the API server, which means the first authorization is against
   `nodes/proxy` and yours, and the second is against the kubelet and the API server's. Run it as
   the identity that holds `nodes/configz` and as the identity that holds `nodes/proxy`, and compare
   with what the same two identities got in step 4 talking to the port directly.

   ```sh
   kubectl auth can-i --list --as=system:serviceaccount:bw-kauthz:sa-configz | grep nodes
   kubectl get --raw "/api/v1/nodes/$N/proxy/configz" \
     --as=system:serviceaccount:bw-kauthz:sa-configz | head -c 120; echo
   kubectl get --raw "/api/v1/nodes/$N/proxy/configz" \
     --as=system:serviceaccount:bw-kauthz:sa-proxy | head -c 120; echo
   ```

9. Check the post's nine-item list against the role it describes. Bind the control identity to the
   built-in role and ask about each name in turn, then read the role's own rules. The list in the
   post is the union of the pin's two lists; the pin's gated list is seven long; the role is
   whatever the cluster shipped.

   ```sh
   kubectl create clusterrolebinding bw-admin \
     --clusterrole=system:kubelet-api-admin --serviceaccount=bw-kauthz:sa-none
   for s in proxy stats metrics log spec checkpoint configz healthz pods; do
     printf '%-18s %s\n' "nodes/$s" \
       "$(kubectl auth can-i get "nodes/$s" --as=system:serviceaccount:bw-kauthz:sa-none)"
   done
   kubectl get clusterrole system:kubelet-api-admin -o yaml | grep -v 'creationTimestamp\|uid:'
   ```

10. Leave the node and count what the documentation says. The first two extracts are the page's two
    tables and their two attribute lists, side by side, which is where the `spec` and `checkpoint`
    rows go missing. The loop is the seven names an RBAC rule needs. The rest is the gate file, the
    locked count, and the two blog posts that mention the feature at all.

    ```sh
    cd /path/to/kubernetes/website/content/en
    W="$(pwd)"
    A="$W/docs/reference/access-authn-authz/kubelet-authn-authz.md"
    sed -n '68,75p;93,97p' "$A"
    sed -n '108,117p;124,130p' "$A"
    for s in stats metrics log spec checkpoint configz healthz pods proxy; do
      printf '%-18s %s\n' "nodes/$s" \
        "$(grep -rF --include='*.md' -o "nodes/$s" "$W/docs" | wc -l)"
    done
    grep -rn --include='*.md' -F 'nodes/proxy' "$W/docs" | sed "s|$W/docs/||"
    grep -rn --include='*.md' -F '/proxy/configz' "$W/docs" | sed "s|$W/docs/||"
    G="$W/docs/reference/command-line-tools-reference/feature-gates"
    cat "$G/KubeletFineGrainedAuthz.md"
    grep -l 'locked: true' "$G"/*.md | wc -l
    grep -rl 'KubeletFineGrainedAuthz' "$W/blog/_posts" | sed "s|$W/blog/_posts/||"
    ```

**Expect**

Step 1 fixes the release and the rules. `kubectl version` reports v1.35, which matters more here
than in most of these walks: it is the last release in which this gate can be set at all. The
authentication block says `anonymous: enabled: false`, `webhook: enabled: true` with a `cacheTTL` of
`2m0s`, and an `x509` client CA of `/etc/kubernetes/pki/ca.crt`; the authorization block says `mode:
Webhook` with `cacheAuthorizedTTL: 5m0s` and `cacheUnauthorizedTTL: 30s`. Those two numbers are the
ones to keep. There is no `featureGates` key, so the gate sits at its release default, and the
metric line comes back with `stage="BETA"` and a value of `1`. If that grep prints nothing, your
kubelet build does not register the feature-gate metric; step 7 still measures the feature, it just
measures it by behaviour alone. The role query prints two lines, one of them the bare `["nodes"]`
and the other a list of subresources — do not read it closely yet, step 9 asks it the same question
nine times and gets a better answer.

Step 2 is RBAC arithmetic and should be dull. `kubectl create clusterrole` accepts
`--subresource=configz` and `--subresource=spec` without complaint and writes rules whose resources
are `nodes/configz` and `nodes/spec`, which is worth noticing on its own: the API server has no
registry of legal subresource names, so a rule may grant a string no endpoint will ever check. The
two-line echo prints `sa-configz: nodes/configz yes, nodes/proxy no` and the same shape for
`sa-spec`. Five ServiceAccounts, four of them one permission wide, one of them empty.

Step 3 is the first time anything in this archive speaks to port 10250. The anonymous request
answers `401`, because the configuration you printed in step 1 turns anonymous authentication off;
the kubelet's own default, described at `reference/access-authn-authz/kubelet-authn-authz.md:14-19`,
belongs to a kubelet nobody deploys. The configz-only token answers `403` on `/metrics` and the
metrics-only token answers `200`, which is the whole claim of the feature in two lines. Then the
same gate metric you read through the API server in step 1 comes back from the process that owns it,
identical. Read the two together: the value is the kubelet's, and the path in step 1 was only a way
of asking it.

Step 4 is the exercise. The `none` row should be `403` in all eight columns; if `/healthz` answers
`200` for an identity with no permissions at all, the kubelet is exempting that path from
authorization and its row in the page's table is describing something else. The `metrics` row should
be `200` on `/metrics` and `403` on the other seven, and the `configz` row `200` on `/configz` and
`403` elsewhere, which is the shape the post promises. The row that carries the argument is `proxy`:
expect `200` in all eight columns. Not four, all eight. The gated table at
`kubelet-authn-authz.md:108-117` maps `/metrics/*`, `/stats/*` and `/logs/*` to their own
subresources, but the check is a check and then a fallback, and the fallback is `nodes/proxy`, so
the permission the post exists to retire answers every path in the table. The last column is the one
the pin cannot settle: `/spec/` against the `spec` identity is `200` if the kubelet still maps that
path the way the coarse table at `:68-75` says it does, and `403` if the gated table's silence about
`/spec` is literal. Whichever you get, one of the two tables on that page is wrong about your
cluster.

Step 5 makes the dual check countable. The cold `/configz` request from the proxy-only identity
should cost two `SubjectAccessReview` calls — one for `nodes/configz`, refused, and one for
`nodes/proxy`, allowed — and the cold request from the configz-only identity should cost one,
because the first check is the one that succeeds. Both of the next twenty should cost zero: an
authorized decision is cached for the five minutes step 1 printed, and a refused one for thirty
seconds, which is what the `sleep 35` is clearing before each identity's cold request. A second
delta that is not zero means something else on the cluster is issuing reviews while you count; the
counter is the API server's and it is cluster-wide. Two and one is the number to want. It is the
dual check, observed from the far end of a connection that never mentions it.

Step 6 should print `proxy -> 101`, `metrics -> 403` and `configz -> 403`. `curl` may hold the
upgraded connection open until the five-second timeout expires and then exit non-zero; the status
line is written before that and is the only part that matters. A `101` is the kubelet saying it
authorized an exec session and is ready to stream — no frame is sent, no command runs in
`bw-target`, and the container is unchanged afterwards. That single number is the warning at
`kubelet-authn-authz.md:77-85` reduced to its authorization decision, and it does not move when the
gate does, because `/exec` falls to the catch-all row in both of the page's tables and that row is
`proxy` in each.

Step 7 is the half of the matrix the post's own release can no longer produce. The metric comes back
with the same `stage="BETA"` and a value of `0`. The `metrics` row should be unchanged and the
`configz` row should now answer `403` on `/configz` as well — `nodes/metrics` was in the coarse
table long before the gate existed, and `nodes/configz` was in nothing, so the configz-only identity
now has a permission no code path consults. The `proxy` row is where the four cells move: with the
feature off it answers `403` on `/metrics`, `/stats/summary`, `/logs/` and `/spec/`, and `200` on
the other four. Turning the feature on widened it. That is the measurement, and it is the one
sentence of this exercise worth carrying away: the gate the post describes as narrowing a broad
permission is, on the wire, the thing that makes that permission cover four paths it did not cover
before. If `kubectl wait` times out after the restart, the guard fired or the appended block landed
inside another key; `sudo journalctl -u kubelet -n 20` will say which, and
`/tmp/bw-kubelet.yaml.bak` is the way back.

Step 8 puts the two hops side by side. The `--list` grep prints a `nodes/configz` row with `get`, so
the identity holds exactly what the feature invented. The first raw request then fails with a
`Forbidden` naming `nodes/proxy`, because the API server's own authorization of
`/api/v1/nodes/<name>/proxy/<path>` has one subresource and it is not the one the kubelet would have
checked. The second returns the first 120 bytes of a `kubeletconfig` JSON document. The identity
that holds the new permission cannot reach the endpoint through the documented path; the identity
that holds the permission the feature exists to replace can. The two-hop shape itself, and the
change of identity at the second hop, belong to [the node log query
walk](../2023/03-node-log-query-alpha.md); what is new here is that the first hop is now the one
that decides.

Step 9 should print five `yes` answers and four `no` answers. Expect `proxy`, `stats`, `metrics`,
`log` and `spec` to be allowed and `checkpoint`, `configz`, `healthz` and `pods` to be refused,
which is the built-in role enumerating the coarse world and nothing else. The role YAML on the next
line is the authority and the nine answers have to agree with it; if they do not, you have a second
binding in the cluster that this exercise did not create. Read the printed rules against the nine
names the post lists: the post's list is the union of the page's two lists, and a union is not what
any single object in the cluster holds. The role also comes back if you edit it, for the reason [the
RBAC walk](../2017/06-using-rbac-generally-available-18.md) sets out.

Step 10 leaves the cluster and counts strings. The first extract is the coarse table and its
attribute list, with rows for `/spec` and `/checkpoint`; the second is the gated table and its
attribute list, with neither. That is the same page disagreeing with itself twice. The loop prints
`0` for `stats`, `metrics`, `log`, `spec`, `checkpoint`, `configz` and `healthz`, `1` for `pods` —
and that one is `concepts/cluster-administration/dra.md:100`, a prose phrase counting nodes and
pods, not an RBAC rule — and `8` for `proxy`. The eight are in four files and every one of them is a
warning. The `/proxy/configz` grep prints two task pages, both of which still tell you to hold the
broad permission. The gate file has an alpha row, a beta row and a stable row, and no `locked` key
at all, while `49` files in that directory carry one. And the blog grep prints two paths, this post
and the v1.36 release announcement, which is the whole of what the project has written about the
feature outside the reference.

**Read on**

11. [The node log query walk](../2023/03-node-log-query-alpha.md), for the two-hop path this
    exercise short-circuits, for `/logs/*` mapping to `nodes/log`, and for the built-in role read
    from the other side.

12. [The node dashboard walk](../2016/12-visualize-kubelet-performance-with-node-dashboard.md), for
    the coarse table's `/stats` and `/metrics` rows in the release they were written for, and for a
    metrics-only identity tested through the API server rather than against the port.

13. [The RBAC walk](../2017/06-using-rbac-generally-available-18.md), for auto-reconciliation,
    aggregation, and why the rules step 9 prints are the ones the control plane will keep putting
    back.

14. [The z-pages walk](../2025/12-kubernetes-v1-35-structured-zpages.md), for the four documented
    ways to ask a component which gates it has on, and for `/configz` used as an instrument rather
    than as a target.

15. Unanswerable from the pin: whether `stage="GA"` is a label this metric ever emits. Steps 1, 3
    and 7 can show you `stage="BETA"` with a value of `1` and then `0`, because v1.35 is a release
    in which the gate still has two settings. The pinned tree records the stable row from v1.36 in
    the gate file and says nothing about what the metric prints once a gate is no longer settable,
    and the documented recipe reads the API server's gates rather than the kubelet's. The node can
    show you the feature moving. It cannot show you the label it wears afterwards.

**Teardown**

The namespace takes the five ServiceAccounts and the target pod. Everything else here is
cluster-scoped and will outlive it: four ClusterRoles and five bindings, the last of which grants
full kubelet API access to a ServiceAccount and is the one you least want to forget. Restore the
kubelet configuration from the backup even if step 7 ran to completion, because the restart at the
end of that step is the only thing that puts it back, and an interrupted step leaves the gate off.

```sh
ssh zain@10.10.10.180 "kubectl delete namespace bw-kauthz --wait; \
  kubectl delete clusterrolebinding bw-proxy bw-metrics bw-configz bw-spec bw-admin; \
  kubectl delete clusterrole bw-proxy bw-metrics bw-configz bw-spec; \
  sudo cp /tmp/bw-kubelet.yaml.bak /var/lib/kubelet/config.yaml; \
  sudo systemctl restart kubelet; rm -f /tmp/bw-kubelet.yaml.bak"
```
