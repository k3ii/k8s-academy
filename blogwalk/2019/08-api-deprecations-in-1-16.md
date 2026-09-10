<a id="api-deprecations-in-1-16"></a>

# This post was absorbed into a reference page so completely that its opening two sentences are that page's overview and its only heading is that page's only heading, and of the three migration targets it names, one was deleted and one was unserved by the release it forecasts

**Post** — [Deprecated APIs Removed In 1.16: Here’s What You Need To
Know](https://kubernetes.io/blog/2019/07/18/api-deprecations-in-1-16/), 18 July 2019, by Vallery
Lancey (Lyft). 109 lines. An advisory: six API versions stop being served in v1.16, here is where to
move, here is one more coming in v1.22, and here are three things to do about it.

Most posts in this archive were overtaken by a version. This one was overtaken by a *page*. The
thing to hold onto while working through it is that almost every sentence in it is still true, and
the reason you would no longer read it is that somebody moved it.

**As written** — the post has one structural idea and executes it cleanly. An intro of two sentences
(`:10-11`). A list of six kinds whose old group-versions v1.16 stops serving, each with a
destination and an "available since" release and, where relevant, the field changes that come with
the move (`:15-47`). One forecast: v1.22 will stop serving `extensions/v1beta1` Ingress, so move to
`networking.k8s.io/v1beta1`, available since v1.14 (`:49-53`). Then a heading, `# What To Do`
(`:55`), under which sit three imperatives (`:60-63`) — change your YAML, update your custom
integrations and controllers, update your third-party tools — followed by the tool that does the
first one for you, `kubectl convert -f <file> --output-version <group>/<version>` (`:69`), the
rehearsal technique that tells you whether you are done, an apiserver started with the doomed
group-versions switched off (`:77-81`), and a closing block of release notes and a mailing-list
quotation from Jordan Liggitt (`:83-109`).

The deadline is in the text: *"Kubernetes 1.16 is due to be released in September 2019, so be sure
to audit your configuration and integrations now!"* (`:57-58`). It shipped on schedule.

**As it runs now** — the pin is `kubernetes/website` at `7c76070faf9b19e6a417c446043dbafd10a7aa1d`,
and the post is not so much stale as rehoused.

**The post's first two sentences are the opening of the page that replaced it.** Compare the post's
`:10-11` with `reference/using-api/deprecation-guide.md:13-14`: *"As the Kubernetes API evolves,
APIs are periodically reorganized or upgraded. When APIs evolve, the old API is deprecated and
eventually removed."* Word for word, punctuation for punctuation. The page then adds one sentence
the post does not have — *"This page contains information you need to know when migrating from
deprecated API versions to newer and more stable API versions"* (`:15-16`) — which is the post's
subtitle rewritten as a permanent brief.

**Its one section heading is the page's one section heading.** The post's `# What To Do` (`:55`) is
the page's `## What to do` (`:377`), and underneath it the page has three subsections in the post's
order: `### Test with deprecated APIs disabled` (`:379`), which is the post's `--runtime-config`
rehearsal; `### Locate use of deprecated APIs` (`:390`), which the post does not have; and `###
Migrate to non-deprecated APIs` (`:395`), which is the post's three imperatives plus `kubectl
convert`. Two of the three subsections are this post's paragraphs with a heading put over them.

**The six kinds are all there, in a section named after the release the post is about.** `### v1.16`
at `:308`, opening *"The v1.16 release stopped serving the following deprecated API versions:"*
against the post's *"The v1.16 release will stop serving the following deprecated API versions in
favor of newer and more stable API versions"* (`:13`) — same sentence, tense corrected. Then the
same six kinds: NetworkPolicy (`:312`), DaemonSet (`:319`), Deployment (`:332`), StatefulSet
(`:349`), ReplicaSet (`:361`), PodSecurityPolicy (`:370`). The post's order put PodSecurityPolicy
second; the page puts it last. Every "available since" release matches, and every one of the post's
notable-change bullets is reproduced, down to the parenthetical old defaults.

**One of the six destinations has since been deleted, and the page says so 224 lines before it
recommends it.** At `:374` the page tells you to *"Migrate manifests and API client to use the
policy/v1beta1 API version, available since v1.10"* — the post's advice at `:19`. At `:150`, in the
`### v1.25` section, the same page says *"PodSecurityPolicy in the policy/v1beta1 API version is no
longer served as of v1.25, and the PodSecurityPolicy admission controller will be removed."* There
is no successor API version and no successor kind: `:153-154` sends you to Pod Security Admission or
a third-party admission webhook instead. So of the post's six migrations, five point at an API that
is still served at the pin and one points at an API that was itself removed nine releases after the
removal this post is about.

**The page still says that removal is in the future.** `:375`, the second bullet of the v1.16
PodSecurityPolicy entry: *"Note that the policy/v1beta1 API version of PodSecurityPolicy will be
removed in v1.25."* Twelve releases after v1.25, in the same file that records the removal as having
happened. The tense survives because the sentence was correct when written and nothing in the page's
structure forces a second look at an entry once its release section is closed.

**The Ingress forecast was right about the release and wrong about the destination.** The post
(`:49-53`) says v1.22 will stop serving Ingress in `extensions/v1beta1`, and to move to
`networking.k8s.io/v1beta1`. The page's `:259` says *"The extensions/v1beta1 and
networking.k8s.io/v1beta1 API versions of Ingress is no longer served as of v1.22"* — both of them,
in the release the post named, and the destination is `networking.k8s.io/v1`, *"available since
v1.19"* (`:260`). v1.19 shipped a year after this post, so in July 2019 the destination the post
should have named did not exist yet. The advice was the best available and had a shelf life of one
release either way.

**And the promise attached to it does not describe the migration that was actually needed.** The
post: *"Migrating to the new Ingress API will only require changing the API path - the API fields
remain the same"* (`:65`). True of the move to `networking.k8s.io/v1beta1`. Not true of the move to
`networking.k8s.io/v1`, which the page lists five notable changes for (`:264-270`): `spec.backend`
renamed to `spec.defaultBackend`, `serviceName` to `service.name`, numeric `servicePort` to
`service.port.number`, string `servicePort` to `service.port.name`, and `pathType` *"now required
for each specified path"*.

**The rehearsal flag names a granularity the flag's own documentation does not offer.** The post's
recipe (`:81`) is
`--runtime-config=apps/v1beta1=false,apps/v1beta2=false,extensions/v1beta1/daemonsets=false,...` and
so on for five `extensions/v1beta1/<resource>` entries. The flag's reference entry at
`reference/command-line-tools-reference/kube-apiserver.md:997-1000` lists what it supports:
`v1=true|false` for the core group, `<group>/<version>=true|false` *"for a specific API group and
version (e.g. apps/v1=true)"*, and four `api/<track>` wildcards. A three-segment
group/version/resource key is not among them. Whether the apiserver still accepts one is the
question the exercise puts to a running cluster.

**The page's own example of that flag would not parse.** `:388`:
`--runtime-config=admissionregistration.k8s.io/v1beta1=false,apiextensions.k8s.io/v1beta1,...` — the
second element has no `=false` and the third is a literal ellipsis. The post's flag, whatever else
is wrong with it, is a complete argument you can paste. Its descendant is not.

**The gap the post left was closed in the very next release, by the apiserver.** The post tells you
to *"audit your configuration and integrations now"* (`:58`) and gives you no way to do it: no
command, no metric, nothing but read your YAML. `reference/using-api/deprecation-policy.md:288-303`
records what arrived in v1.19 — a request to a deprecated endpoint returns a `Warning` header, adds
a `"k8s.io/deprecated":"true"` annotation to the audit event, and sets an
`apiserver_requested_deprecated_apis` gauge with `group`, `version`, `resource`, `subresource` and
`removed_release` labels, joinable to `apiserver_request_total`. The metric is listed at
`reference/instrumentation/metrics.md:70`. v1.16 was the last removal a cluster could not tell you
about itself, which makes this post the last of its genre that had to exist.

**The page that inherited that gap fills it with a link to another blog post.** `### Locate use of
deprecated APIs` is two lines long (`:392-393`), and its whole content is a pointer to a September
2020 post about warnings. The retrospective half of this post's job was institutionalised into a
reference page; the how-do-I-find-them half is still a blog link.

**Nothing in the pin does the forecasting half at all.** `## Removed APIs by release` (`:21`) has
seven release sections — v1.32, v1.29, v1.27, v1.26, v1.25, v1.22, v1.16 — and thirty entries under
them. There is no section for a release that has not happened. The word "upcoming" appears once in
the file, inside the rehearsal instruction (`:382`), and the newest section is five releases behind
the pin's newest Kubernetes. The page records removals; it does not announce them. Whatever tells a
v1.37 operator what v1.38 will stop serving, it is not this page, and it is not a successor to this
post.

**The rehearsal technique does have a successor, with a floor this post's APIs are below.**
`concepts/cluster-administration/compatibility-version.md` — 25 lines, the whole subsystem — says
that *"Since release v1.32, we introduced configurable version compatibility and emulation options"*
(`:12`) and that with `--emulated-version` set, *"Any capabilities removed after the emulation
version will be available"* (`:22`). That is the post's rehearsal turned into a supported mechanism,
one whole release at a time instead of a hand-typed list. The flag's reference entry
(`kube-apiserver.md:514-517`) gives the accepted range as `kube=1.33..1.36`. Everything this post is
about was removed at v1.16 or v1.22, so the mechanism cannot reach it and never will.

**A resource table in the kubectl reference disagrees with itself about the post's destination.**
`reference/kubectl/_index.md:186` introduces the table with a parenthesis: *"(This output can be
retrieved from `kubectl api-resources`, and was accurate as of Kubernetes 1.25.0)"*. Fifty-six rows
follow. One of them, `:235`, is `podsecuritypolicies` / `psp` / `policy/v1beta1` / `false` /
`PodSecurityPolicy` — a resource that v1.25.0 removed, in a table stamped accurate as of v1.25.0.
Two more, `:228-229`, put FlowSchema and PriorityLevelConfiguration at
`flowcontrol.apiserver.k8s.io/v1beta2`, which the deprecation guide records as unserved since v1.29
(`:42`). The page's prose was maintained; the pasted output was not. This is a claim a single
command settles, so settling it is a step in *Do*.

**What is still exactly right.** All six kinds and their old group-versions. Five of the six
destinations. Every "available since" release. Every notable change, including all four Deployment
default changes and both `updateStrategy.type` flips. The promise that *"Existing persisted data can
be retrieved/updated via the new version"*, which the page repeats as a bullet under five of the six
v1.16 entries — every one but PodSecurityPolicy's, the entry whose destination was later deleted.
The three imperatives at `:60-63`, which are still the whole job. The release date. And the link at
`:90` to the deprecation policy, whose anchor `#deprecating-parts-of-the-api` still resolves to
`deprecation-policy.md:21`, as does the API-reference link at `:75` to `reference/_index.md:18`. For
a seven-year-old advisory about a completed migration, the error rate is one destination and one
promise.

**What this exercise does not cover, and where it lives.** Five of the post's six bullets are
already walked elsewhere, and this exercise cedes them rather than repeat them. NetworkPolicy's move
out of `extensions` belongs to [the network-policy API
exercise](../2016/06-kubernetes-network-policy-apis.md). DaemonSet's notable changes, including
`templateGeneration` and the `OnDelete` default, belong to [the StatefulSet and DaemonSet updates
exercise](../2017/04-kubernetes-statefulsets-daemonsets.md). Deployment's four default changes,
`spec.rollbackTo`, and the shape of the refusal you get from a dead group-version belong to [the
Deployment objects exercise](../2016/04-using-deployment-objects-with.md). StatefulSet's belong to
[the StatefulSet GA
exercise](../2016/14-statefulset-run-scale-stateful-applications-in-kubernetes.md). The Ingress
group-version hard-error belongs to [the Ingress
exercise](../2016/03-kubernetes-1-2-and-simplifying-advanced-networking-with-ingress.md), and
`kubectl convert` no longer shipping inside `kubectl` belongs to [the v1beta3
exercise](../2015/01-introducing-kubernetes-v1beta3.md). What is left, and what this exercise is
about, is the post as a *document*: where it went, what the thing that replaced it does and does not
do, and the two of its instructions that a v1.37 cluster will not carry out.

**The diff, and why** — five of the seven cases at once, which is what an advisory gets when the thing
it advises about completes.

**Retired by being agreed with.** The post argued that six removals needed a single place that
explained where to go. That place exists, it is `reference/using-api/deprecation-guide.md`, and its
overview is this post's first paragraph unedited and its one heading is this post's one heading. The
post did not become wrong. It became a page, and the page has a `weight` and a `content_type` and a
list of reviewers, which is what winning looks like for a piece of writing like this.

**The post broke.** Two of its instructions will not run. `kubectl convert` is not in `kubectl` —
the guide's own note (`:411-422`) concedes it *"is not installed by default, although in fact it
once was part of `kubectl` itself"* and sends you to three per-operating-system plugin install
pages, of which `tasks/tools/install-kubectl-linux.md:316` is the Linux one. And the
`--runtime-config` rehearsal names seven group-versions of which none is served at the pin, in a
per-resource form the flag's documentation does not list.

**A plan the project abandoned.** Not by the post, but of it: the half of this post's job that
looked forward. The guide records seven completed releases of removals and forecasts nothing. The
post's own forecast — one line about v1.22 Ingress — turned out to be the more valuable half, and it
is the half that has no home in the pin.

**Overtaken by stasis.** Three sentences in the pin were true when written and have not been read
since. `deprecation-guide.md:375` still says `policy/v1beta1` PodSecurityPolicy *"will be removed in
v1.25"*. `deprecation-policy.md:301` still offers a PromQL example for *"requests made to deprecated
APIs which will be removed in v1.22"*. `reference/kubectl/_index.md:186` still certifies a table as
accurate as of v1.25.0 while a row in it names an API v1.25.0 deleted. All three sit in maintained
pages, and all three are the parts of a maintained page nobody re-reads.

**Still right.** The body of the post — six kinds, five destinations, every field change, every
availability release, and the three things to do — is reproduced in the pin nearly verbatim, which
is a stronger form of correct than surviving unchallenged.

**No gate** — there is no feature gate anywhere near this post, and the pin has no file for one. API
removals are governed by the deprecation policy, not by a gate: the tracks table at
`deprecation-policy.md:23-34` and the rules under `## Deprecating parts of the API` (`:21`) are what
decide when a group-version stops being served, and none of that is switchable at runtime. The two
runtime switches this exercise does touch — `--runtime-config` and `--emulated-version` — are
apiserver flags, not gates, and neither has a stage or a graduation. Where a ladder would go, read
`kube-apiserver.md:997-1000` for what `--runtime-config` claims to accept and `:514-517` for
`--emulated-version`'s accepted range, and treat those two as the maturity statement for this
exercise's subject matter.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180`, guest
account `zain`, provisioned by the [standard steps](../../strands/lab-topologies.md#provision).
Every question here is answered by the apiserver about itself, so a second node would add nothing:
there is no scheduling, no networking and no cross-node behaviour in play. What the topology cannot
show is the thing the post is actually about — a migration under load. A single-node cluster with no
workloads has nothing stored under a doomed group-version, so when you switch a group-version off
you will see the apiserver's reaction to the flag and not the reaction of a fleet of controllers to
a missing API. That second reaction is the one the post's readers were afraid of, and it is not
reproducible here at any node count, because the APIs are gone from the binary.

Four steps edit `/etc/kubernetes/manifests/kube-apiserver.yaml` and restart the control plane. Copy
the file first, in step 5, before touching anything: if the apiserver refuses to start, `kubectl`
stops answering and the backup is the only way back. The kubelet re-reads the manifest directory
within seconds of a write, so restoring the copy is enough — no `systemctl`, no reboot.

**Do**

1. Take the census the post asks you to take, seven years late.

   ```
   kubectl api-versions | sort > /tmp/served.txt
   wc -l < /tmp/served.txt
   grep '^extensions' /tmp/served.txt || echo "no extensions group is served"
   grep -E '^apps/|^policy/|^networking' /tmp/served.txt
   ```

2. Ask the apiserver about each group-version the post names, and each destination it names.

   ```
   for gv in extensions/v1beta1 apps/v1beta1 apps/v1beta2 policy/v1beta1 \
             networking.k8s.io/v1beta1 apps/v1 policy/v1 networking.k8s.io/v1; do
     printf '%-28s ' "$gv"
     kubectl get --raw "/apis/$gv" >/dev/null 2>&1 && echo served || echo "not served"
   done
   ```

3. Follow the post's PodSecurityPolicy bullet (`:18-20`) to its destination and record what is
   there.

   ```
   kubectl api-resources 2>/dev/null | grep -i podsecuritypolic || echo "no such resource"
   kubectl get psp 2>&1 | head -3
   kubectl explain psp 2>&1 | head -3
   kubectl get --raw /apis/policy/v1beta1 2>&1 | head -2
   kubectl api-resources --api-group=policy
   ```

4. Settle the kubectl reference's resource table (`reference/kubectl/_index.md:186-245`) against the
   cluster it claims to describe.

   ```
   kubectl api-resources | tail -n +2 | wc -l
   kubectl api-resources -o wide | grep -E 'flowschemas|prioritylevel'
   kubectl api-resources -o wide | grep -E '^ingresses|^networkpolicies'
   ```

5. Copy the apiserver manifest, then paste the post's rehearsal flag (`:81`) into it verbatim and
   watch what the apiserver makes of a three-segment key.

   ```
   sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/kube-apiserver.yaml.bak
   sudo sed -i '/- kube-apiserver$/a\    - --runtime-config=apps/v1beta1=false,apps/v1beta2=false,extensions/v1beta1/daemonsets=false,extensions/v1beta1/deployments=false,extensions/v1beta1/replicasets=false,extensions/v1beta1/networkpolicies=false,extensions/v1beta1/podsecuritypolicies=false' /etc/kubernetes/manifests/kube-apiserver.yaml
   grep -c runtime-config /etc/kubernetes/manifests/kube-apiserver.yaml
   sleep 30
   kubectl get --raw /readyz 2>&1 | head -2
   sudo crictl logs --tail 15 $(sudo crictl ps -a --name kube-apiserver -q | head -1) 2>&1 | tail -15
   ```

   Then put it back, and wait for the API to answer before going on.

   ```
   sudo cp /root/kube-apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml
   sleep 30; kubectl get --raw /readyz
   ```

6. Repeat with the documented two-segment form for a group-version the binary no longer has. This
   separates "the flag rejects the key shape" from "the flag rejects the dead group".

   ```
   sudo sed -i '/- kube-apiserver$/a\    - --runtime-config=apps/v1beta1=false' /etc/kubernetes/manifests/kube-apiserver.yaml
   sleep 30
   kubectl get --raw /readyz 2>&1 | head -2
   sudo crictl logs --tail 15 $(sudo crictl ps -a --name kube-apiserver -q | head -1) 2>&1 | tail -15
   sudo cp /root/kube-apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml
   sleep 30; kubectl get --raw /readyz
   ```

7. Repeat with the deprecation guide's own example of the flag (`:388`), ellipsis and missing
   `=false` included.

   ```
   sudo sed -i '/- kube-apiserver$/a\    - --runtime-config=admissionregistration.k8s.io/v1beta1=false,apiextensions.k8s.io/v1beta1,...' /etc/kubernetes/manifests/kube-apiserver.yaml
   sleep 30
   kubectl get --raw /readyz 2>&1 | head -2
   sudo crictl logs --tail 15 $(sudo crictl ps -a --name kube-apiserver -q | head -1) 2>&1 | tail -15
   sudo cp /root/kube-apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml
   sleep 30; kubectl get --raw /readyz
   ```

8. Ask the successor mechanism to rehearse the release this post is about, and read the range it
   gives you back.

   ```
   sudo sed -i '/- kube-apiserver$/a\    - --emulated-version=kube=1.16' /etc/kubernetes/manifests/kube-apiserver.yaml
   sleep 30
   kubectl get --raw /readyz 2>&1 | head -2
   sudo crictl logs --tail 15 $(sudo crictl ps -a --name kube-apiserver -q | head -1) 2>&1 | tail -15
   sudo cp /root/kube-apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml
   sleep 30; kubectl get --raw /readyz
   ```

9. Look for the audit mechanism the post could not offer, on a cluster with nothing to report.

   ```
   kubectl get --raw /metrics | grep apiserver_requested_deprecated_apis | head -5
   kubectl get --raw /metrics | grep -c '^apiserver_requested_deprecated_apis{' || \
     echo "the gauge has no series"
   kubectl get --raw /metrics | grep -c '^apiserver_request_total{'
   ```

**Expect**

1. `extensions` is not served at all — not the group-version, the group. The post's five
   `extensions/v1beta1` resources have no group to belong to. `apps/` should show `apps/v1` alone,
   `policy/` should show `policy/v1` alone, and `networking.k8s.io/` should show `v1` alone. Record
   the total count of served group-versions: it is a number the post's readers would not recognise.

2. Five "not served" and three "served", in that order — the post's five doomed group-versions gone,
   its three surviving destinations present. `policy/v1beta1` is in the doomed list even though the
   post puts it in the destination column, which is the whole finding in one line of output.

3. `kubectl api-resources` has no `podsecuritypolicies` row, and `kubectl get psp` and `kubectl
   explain psp` both fail. The exact wording of both failures is open — record it, because the two
   commands fail for different reasons: one cannot resolve a resource name against the discovery
   document, the other cannot find a schema. `kubectl get --raw /apis/policy/v1beta1` should return
   a 404. `kubectl api-resources --api-group=policy` should list `poddisruptionbudgets` at
   `policy/v1` and nothing else, against the reference table's two `policy` rows.

4. Fifty-six rows in the documentation, some other number on the cluster — record both. The
   `flowcontrol.apiserver.k8s.io` group-version the cluster reports should not be the `v1beta2` the
   table gives at `:228-229`. Between the missing `podsecuritypolicies` and the wrong `flowcontrol`
   version, three of fifty-six rows in a table stamped *"accurate as of Kubernetes 1.25.0"* are
   wrong, and one of them was wrong on the day it was stamped.

5. Genuinely open, and the centre of the exercise. The apiserver either ignores unknown
   group-versions in `--runtime-config`, warns about them, or refuses to start. Record which, and
   record the exact message. If it refuses, the post's rehearsal instruction is not merely useless
   at the pin — pasting it into a running cluster takes the control plane down, which is a strong
   argument for the copy in step 5's first line. `grep -c runtime-config` should print `1` before
   the wait; if it prints `0` the `sed` address did not match, and the manifest's command line is
   worth reading before retrying.

6. Open, and the point is the comparison with step 5. Same outcome in both means the flag objects to
   the dead group. Different outcomes mean it objects to the three-segment key shape, and the post's
   flag was already using an undocumented granularity in 2019.

7. Open. Whatever the apiserver does with a bare `apiextensions.k8s.io/v1beta1` and a literal `...`,
   the deprecation guide's example is not something a reader can paste, and this is the step that
   proves it rather than asserting it.

8. Open, and the useful part is the message rather than the outcome. `1.16` is far below the
   documented floor, so expect a refusal; the thing to write down is the range the binary itself
   names, and whether it matches the `kube=1.33..1.36` at `kube-apiserver.md:517`. If it does not,
   the generated reference page was built from a different binary than the one you are running,
   which is worth knowing before trusting any other range on that page.

9. Expect the metric name to appear only in its `# HELP` and `# TYPE` lines, with no labelled series
   — a fresh cluster running current APIs has nothing deprecated to count. That is the correct
   answer and it is also the unsatisfying one: the mechanism that closed this post's audit gap
   reports zero on a cluster that has nothing to migrate, which is exactly when nobody looks at it.
   `apiserver_request_total` should have many series, so the join in `deprecation-policy.md:301`
   would work if there were anything to join.

**Read on** — four of these are answerable from the pin and one is not.

1. The guide's `### v1.22` section (`:166-307`) has twelve entries. The post forecast one of them.
   Read the other eleven and sort them by their "available since" line into those whose destination
   already existed in July 2019 and those whose did not. The post could have warned about the first
   group and could not have warned about the second; the ratio is a measurement of how much of an
   advisory's value is available to its author.

2. `deprecation-policy.md` — the tracks table at `:23-34` and the rules under `## Deprecating parts
   of the API` (`:21`), with `### REST resources (aka API objects)` at `:277`. Find the clause that
   let `extensions/v1beta1` PodSecurityPolicy go at v1.16 while `policy/v1beta1` PodSecurityPolicy
   survived to v1.25, and then find the clause that covers a beta API with no successor version at
   all. Write down whether the second case is provided for or merely permitted.

3. `tasks/configure-pod-container/migrate-from-psp.md`, 345 lines. This is the migration the post's
   PodSecurityPolicy bullet eventually required. Count how many of its steps have any counterpart in
   the post's three imperatives at `:60-63`, and note what kind of change it asks for that "change
   your YAML" does not describe.

4. `concepts/cluster-administration/compatibility-version.md` is 25 lines for a subsystem introduced
   in v1.32. Read it against `kube-apiserver.md:514-517` and `:818`, and write down which of the two
   flags in that reference the concept page never mentions, and what a reader who only read the
   concept page would therefore get wrong.

5. Not answerable from the pin: whether the guide's newest section being v1.32 means nothing has
   been removed since, or means the page stopped being updated. The page has no way to say "nothing
   was removed in this release", so silence and absence look identical from inside the tree. Decide
   what you would have to read outside the pin to tell them apart, and write that down instead.

**Teardown**

```
sudo cp /root/kube-apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml
sleep 30
kubectl get --raw /readyz
kubectl get nodes
grep -c 'runtime-config\|emulated-version' /etc/kubernetes/manifests/kube-apiserver.yaml
sudo rm -f /root/kube-apiserver.yaml.bak
rm -f /tmp/served.txt
```

The last `grep -c` should print `0`: no flag from steps 5 through 8 survives in the restored
manifest. No API objects were created anywhere in this exercise, so there is nothing else to delete
— which is itself worth noticing, since the post's subject is what happens to objects you have
already stored.