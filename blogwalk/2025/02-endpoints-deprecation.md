<a id="endpoints-deprecation"></a>

# The one link this post offers for further reading points at a directory the tree no longer has and survives only through a redirect file no census row had opened before, and the label the whole migration turns on is defined one way in the API reference and another in the label reference

**Post** — [Kubernetes v1.33: Continuing the transition from Endpoints to EndpointSlices](https://kubernetes.io/blog/2025/04/24/endpoints-deprecation/),
2025-04-24.

8,161 bytes, 227 lines, one author: Dan Winship (Red Hat), who also wrote the nftables post walked
as [exercise 01](01-nftables-kube-proxy.md) — two of this year's twelve `walk` verdicts by the same
hand. Three headings, six fences in three languages (two `console`, two `go`, two `yaml`), seven
reference-style link definitions at `:35-41`, two of them to KEP documents. The body is a migration
guide: the same lookup written twice in `kubectl`, twice in Go, and one object translated into
another in YAML, followed by five numbered points to note.

**As written**

The post opens with a history and a verdict. EndpointSlices arrived as alpha in v1.15 and reached GA
in v1.21, and since then `:10-18` says the Endpoints API has been *"gathering dust"*: dual-stack
networking and traffic distribution are supported only through EndpointSlice, so every service
proxy, Gateway API implementation and similar controller has already been ported, and Endpoints
survives *"only there to avoid breaking end user workloads and scripts that still make use of it."*
Then the announcement, at `:20-22`: as of Kubernetes 1.33 the Endpoints API is officially
deprecated, and the API server returns warnings to anyone who reads or writes an Endpoints resource.

Two paragraphs set the horizon. `:24-28` names a plan — KEP-4974 — to change the Kubernetes
Conformance criteria so that a conformant cluster need no longer run the Endpoints controller, *"to
avoid doing work that is unneeded in most modern-day clusters."* `:30-33` names the limit on that
plan: because of the deprecation policy, *"the Endpoints type itself will probably never completely
go away"*, so the instruction to readers is to migrate, not to wait for a removal.

The rest is the guide. `:45-97` shows the consumer side: one Endpoints object per Service against
any number of EndpointSlices, a `console` transcript carrying the warning header verbatim, and the
replacement lookup — list by the `kubernetes.io/service-name` label rather than fetch by name.
`:99-134` writes the same change in Go. `:136-197` gives the producer side as a translation pair: an
Endpoints object with three ready addresses and one not-ready one, and the EndpointSlice it *"would
become something like"*. `:199-221` adds five points to note — `generateName`, the explicit
`addressType`, subsets becoming multiple slices, the `endpoints` and `addresses` array convention,
and conditions replacing the ready/not-ready split — and `:223-227` closes by pointing at the
EndpointSlice API reference for the features that only slices have.

**As it runs now**

**The one link the post offers for further reading names a directory the tree does not have.**
`:226` writes `/docs/reference/kubernetes-api/service-resources/endpoint-slice-v1`. At the pin
`content/en/docs/reference/kubernetes-api/` holds twenty-two directories — `admissionregistration`
through `storagemigration` — and `service-resources` is not among them. The page is at
`reference/kubernetes-api/discovery/endpoint-slice-v1.md`, and its front matter carries no
`aliases:` field, so nothing in the page itself answers to the old path. The link works anyway, for
one reason only.

**The reason is a file this archive had never opened.** `static/_redirects.base` sits outside
`content/`, is read by `layouts/index.redirects`, and holds 586 lines: 18 comments, 50 blanks and
518 rules. The rules carry six status tokens — 449 plain `301`, 23 forced `301!`, 29 `302`, 9 forced
`302!`, one `308` and six `404` — and eight of them use a splat. The block that matters opens at
`:496` with the comment *"Applied when kubernetes-api content was switched to the markdown
backend."* `:557` is the post's exact path, redirected to `discovery/endpoint-slice-v1/` with a
`301`. Four siblings at `:558-561` move `endpoints-v1`, `ingress-class-v1`, `ingress-v1` and
`service-v1` out of the same vanished directory.

**Seven pinned pages still write the directory that is not there.** Seventeen occurrences:
`endpoint-slices.md:239` and `:240`; `service.md:315`, `:1111`, `:1112` and `:1113`;
`ingress-controllers.md:84`; `ingress.md:106` and `:647`;
`reference/labels-annotations-taints/_index.md:1484`, `:1486`, `:1735`, `:1737`, `:1754` and
`:1756`; `reference/networking/virtual-ips.md:813`; and `reference/using-api/api-concepts.md:847`.
Six of the seventeen are one boilerplate note in the labels reference — the Endpoints API *"is
deprecated in favor of"* EndpointSlice — pasted under three separate label entries, each of the
three copies writing both stale paths.

**Where the pin disagrees with itself: the label the whole migration turns on is defined two ways.**
`reference/kubernetes-api/discovery/endpoint-slice-v1.md:31` — and identically in the front matter
at `:7` — says you find a Service's slices by *"listing EndpointSlices in the service's namespace
whose `kubernetes.io/service-name` label contains the service's name."*
`reference/labels-annotations-taints/_index.md:1413-1415` says the label *"records the name of the
Service that the EndpointSlice is backing"* and that *"All EndpointSlices should have this label set
to the name of their associated Service."* Containment and equality are different selectors and
`kubectl` cannot express the first one. Cite both and say they disagree; step 4 settles it.

**The post's own text takes the label reference's side, three times.** The post writes the selector
at `:58` and again at `:96` as `kubectl get endpointslice -l kubernetes.io/service-name=myservice`,
and at `:123` as `discoveryv1.LabelServiceName + "=" + name`. Every worked example in the pinned
tree does the same: `dns-debugging-resolution.md:190`, `debug-pods.md:156`, `debug-service.md:451`,
`connect-applications-service.md:147`, `pods-and-endpoint-termination-flow.md:66` and
`topology-aware-routing.md:95` all use `=`. The generated API description is the only text in the
tree that says otherwise.

**The post's central artifact is not a translation of itself.** The Endpoints object at `:146-166`
lists three ready addresses: `10.180.3.17` on `node-4`, `10.180.5.22` on `node-9` and `10.180.18.2`
on `node-7`. The EndpointSlice at `:170-197` that *"would become something like"* it lists
`10.180.3.17`, `10.180.5.22` and — on the same `node-7` — `10.180.18.12`. A reader who copies the
pair gets two objects that send traffic to two different backends. The not-ready address survives
the crossing unchanged, so the defect is one digit in one of four entries.

**The warning the post prints exists in exactly one file in the whole tree, and that file is the
post.** `Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice`
returns one hit across `content/en`: the post's own `console` block, at `:54`. The sentence the
warning is built from survives elsewhere, but only as prose in the generated reference:
`reference/kubernetes-api/core/endpoints-v1.md` carries *"Deprecated: This API is deprecated in
v1.33+"* five times, at `:47`, `:76`, `:105`, `:134` and `:175`, plus once more inside the escaped
`description:` on `:7`. No page in the tree tells a reader what the API server will actually put on
the wire.

**The plan the post points at has left no mark on the documentation.** `4974` returns zero hits
across `content/en`. `reference/command-line-tools-reference/kube-controller-manager.md:437` still
lists `endpoints-controller` among the on-by-default controllers, and names exactly three
disabled-by-default ones — `bootstrap-signer-controller`, `selinux-warning-controller` and
`token-cleaner-controller` — so four releases on, a conformant cluster still runs the controller the
KEP proposes to stop requiring. The Conformance link at `:41` leaves the site entirely, for
`cncf.io`; the tree's only conformance page is `setup/best-practices/node-conformance.md`, which is
about nodes.

**The deprecated API's reference page is as large as its replacement's and documents the same write
surface.** `core/endpoints-v1.md` is 1,268 lines and 82,477 bytes against
`discovery/endpoint-slice-v1.md` at 1,319 and 86,336 — 95% the size. Both document eleven
operations, and the deprecated one's eleven include `post`, `patch`, `put`, `delete` and `delete
collection`, none of them carrying a caveat. Its front matter is `title: "Endpoints"`, with no
marker at all, while `service.md:310` heads the same subject *"Endpoints (deprecated)"* and the
labels reference heads all three of its `endpoints.kubernetes.io/` entries `(deprecated)`, at
`:1472`, `:1718` and `:1741`.

**Point 4 has hardened from a convention into a rule with a number.** The post says at `:213-217`
that `endpoints` and `addresses` are both arrays but *"by convention, each `addresses` array only
contains a single element."* `endpoint-slice-v1.md:106` now states it as three separate facts: the
array *"must contain at least one address but no more than 100"*; slices generated by the controller
*"will always have exactly 1 address"*; and *"No semantics are defined for additional addresses
beyond the first, and kube-proxy does not look at them."* The advice did not change; the reason
behind it became enforceable.

**Point 2 is missing a value and two constraints.** The post's second point, at `:206`, says you
have to indicate `addressType: IPv4` or `IPv6`. `endpoint-slice-v1.md:39-40` marks the field
required and adds that it is *"immutable after creation"*, that all addresses in a slice must share
it, and that there is a third supported value, `FQDN`, itself carrying *"(Deprecated)"* and the note
that the controller never generates it, kube-proxy never processes it, and *"No semantics are
defined for the 'FQDN' type."* A field with three legal values, one of which nothing implements.

**What this exercise does not cover, and where it lives.** The EndpointSlice mechanism itself — the
sharding default, the distribution rule, dual-stack, the mirroring bridge and its two labels, and
the per-object size arithmetic the scalability case rests on — is [the 2020 EndpointSlice
post](../2020/06-scaling-kubernetes-networking-with-endpointslices.md), which is also the post this
one is a sequel to and the file that carries the five EndpointSlice feature-gate ladders. Nothing
here transcribes a ladder, because an API deprecation is not carried by a gate. The `Warning` header
as a mechanism — how a server raises one, how a client deduplicates it, and the metrics recipe — is
[the 2020 warnings post](../2020/07-warnings.md); this exercise only asks which verbs trigger one.
Topology hints and `trafficDistribution`, the two features the post's closing paragraph dangles, are
[the 2018 IPVS post](../2018/04-ipvs-in-cluster-load-balancing.md). Deprecation that ends in
removal, as against this one which does not, is [the 2019 API deprecations
post](../2019/08-api-deprecations-in-1-16.md). Predicting `Ready`, `Serving` and `Terminating` from
the field comments is [the endpoint-conditions
lab](../../labs/07/04-eleven-kilobytes-of-endpointslice.md), and writing both objects by hand
against KEP-4974 is [the lab on the API that is being
deleted](../../labs/07/06-the-api-that-is-being-deleted.md).

**The diff, and why** — four cases, and the one that decides the exercise is a broken link caught by
a file outside `content/`.

**Still right.** Everything the post asserts about the state of the world held. The two pinned pages
that prove it — the deprecated feature-state on the Service concept page, and the deprecation-policy
rule that keeps the type alive however long it gathers dust — are both [the 2020 EndpointSlice
post's](../2020/06-scaling-kubernetes-networking-with-endpointslices.md) findings rather than this
one's. What is new is that the tree has taken the post's advice: the string `kubectl get endpoints`
does not appear once under `docs/`, and its only two occurrences in the English tree are both in the
blog — this post, and the 2016 leader-election post — so the documentation no longer teaches the
verb that raises the warning. The advice in point 4 is not merely still right; the reference has
since put a number and a consequence behind it.

**Broke.** The post's single link to further reading, `:226`, names a directory that does not exist
at the pin. That the path once worked is not an assumption: `static/_redirects.base:557` exists
precisely to catch it, and four sibling rules move the rest of the same directory. The file is not
part of the documentation a reader greps, though: it is a deploy artifact, read by a Hugo template
into a Netlify redirect table. Seven pinned pages write the same stale path seventeen times, which
is why the redirect is still load-bearing and not a courtesy. This is the first census row that had
to open that file to answer a question, and the general lesson is larger than this post: a link that
no source grep can resolve is not thereby dead.

**Overtaken by stasis.** The forward half of the post has not moved. `4974` returns nothing in the
pinned tree, and `kube-controller-manager.md:437` still lists `endpoints-controller` among the
controllers enabled by default, four releases after the post said the plan was to stop requiring it.
The Conformance criteria the post proposes to change are not in the tree at all — the link goes to
`cncf.io`. The plan is neither abandoned nor delivered; it is simply not visible from here.

**Never absorbed.** Two things the post supplies exist nowhere else. The first is the warning text
itself: one hit in `content/en`, in this post, at `:54`. A reader who wants to know what the API
server says has to read a blog entry from 2025 to find out. The second is the guide's framing — one
Endpoints object against any number of slices, and therefore a label lookup rather than a name
lookup. The tree states the rule twice and states it differently the two times, which is the
disagreement step 4 resolves, and neither statement is written as migration advice.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo). One node at `10.10.10.180`. Every question here is
answered by the API server — which verbs warn, what the apiserver keeps when you hand it a slice,
and how a label selector behaves — so a second node would add a `nodeName` value and nothing else.
Bring the guest up with [the five provision steps](../../strands/lab-topologies.md#provision),
install Kubernetes with [the node baseline
procedure](../../strands/lab-topologies.md#node-baseline-steps), then `ssh zain@10.10.10.180`. The
cluster runs Kubernetes v1.35, two releases behind the pin and two ahead of the release the post
announces, so the warning the post prints should be there to read. Steps 1 through 9 run on the
node; step 10 reads the pinned checkout on the workstation.

**Do**

1. Establish what this cluster calls the two APIs, and whether the warning fires at all. Keep the
   transcript: steps 2, 3 and 9 are read against it.

   ```sh
   kubectl version
   kubectl api-resources | grep -i '^endpoint'
   kubectl -n default get endpoints kubernetes 2>&1 | head -5
   kubectl -n default get endpointslice kubernetes 2>&1 | head -5
   ```

2. Build the apparatus. One namespace, one Deployment of two replicas, one Service with a selector —
   the ordinary case the post's first section is about.

   ```sh
   kubectl create namespace bw-epd
   kubectl -n bw-epd create deployment app \
     --image=registry.k8s.io/e2e-test-images/agnhost:2.53 --replicas=2 \
     -- /agnhost netexec --http-port=8080
   kubectl -n bw-epd expose deployment app --port=80 --target-port=8080
   kubectl -n bw-epd rollout status deployment/app --timeout=120s
   kubectl -n bw-epd get endpoints app 2>&1
   kubectl -n bw-epd get endpointslice -l kubernetes.io/service-name=app 2>&1
   ```

3. Find out which verbs the warning attaches to. The post shows it on a read. Try a read, a
   describe, a read through the Service rather than the object, and a write, and separate the header
   from the body each time.

   ```sh
   for c in "get endpoints app" "describe endpoints app" "get ep app" "get svc app" "describe svc app"; do
     echo "--- kubectl $c"
     kubectl -n bw-epd $c 2>&1 | grep -i '^Warning' || echo "(no warning)"
   done
   kubectl -n bw-epd get endpoints app -o yaml > /tmp/ep-app.yaml 2>/tmp/ep-app.err
   cat /tmp/ep-app.err
   kubectl -n bw-epd apply -f /tmp/ep-app.yaml 2>&1 | head -3
   kubectl -n bw-epd get --raw /api/v1/namespaces/bw-epd/endpoints/app -v=6 2>&1 | grep -i 'warning' || echo "(no warning on --raw)"
   ```

4. Settle the disagreement. The API reference says the label *contains* the Service name; the label
   reference says it is *set to* the Service name. Only one of those is a selector `kubectl` can
   express, so ask for the exact match, then for a prefix, then for mere presence, and count.

   ```sh
   kubectl -n bw-epd get endpointslice -l kubernetes.io/service-name=app --no-headers | wc -l
   kubectl -n bw-epd get endpointslice -l kubernetes.io/service-name=ap --no-headers 2>&1 | wc -l
   kubectl -n bw-epd get endpointslice -l kubernetes.io/service-name --no-headers | wc -l
   kubectl -n bw-epd get endpointslice -l 'kubernetes.io/service-name in (app,nothing)' --no-headers | wc -l
   kubectl -n bw-epd get endpointslice -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.labels.kubernetes\.io/service-name}{"\n"}{end}'
   ```

5. Now the post's translation pair, run as written and against two separate selectorless Services so
   that the compatibility bridge cannot muddle the comparison. Read only the addresses.

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: v1
   kind: Service
   metadata: {name: bw-old, namespace: bw-epd}
   spec:
     ports: [{name: https, port: 443, protocol: TCP}]
   ---
   apiVersion: v1
   kind: Service
   metadata: {name: bw-new, namespace: bw-epd}
   spec:
     ports: [{name: https, port: 443, protocol: TCP}]
   ---
   apiVersion: v1
   kind: Endpoints
   metadata: {name: bw-old, namespace: bw-epd}
   subsets:
     - addresses:
         - {ip: 10.180.3.17, nodeName: node-4}
         - {ip: 10.180.5.22, nodeName: node-9}
         - {ip: 10.180.18.2, nodeName: node-7}
       notReadyAddresses:
         - {ip: 10.180.6.6, nodeName: node-8}
       ports: [{name: https, protocol: TCP, port: 443}]
   ---
   apiVersion: discovery.k8s.io/v1
   kind: EndpointSlice
   metadata:
     name: bw-new
     namespace: bw-epd
     labels: {kubernetes.io/service-name: bw-new}
   addressType: IPv4
   endpoints:
     - addresses: [10.180.3.17]
       nodeName: node-4
     - addresses: [10.180.5.22]
       nodeName: node-9
     - addresses: [10.180.18.12]
       nodeName: node-7
     - addresses: [10.180.6.6]
       nodeName: node-8
       conditions: {ready: false}
   ports: [{name: https, protocol: TCP, port: 443}]
   YAML
   kubectl -n bw-epd get endpoints bw-old -o jsonpath='{.subsets[*].addresses[*].ip}{"\n"}' 2>/dev/null
   kubectl -n bw-epd get endpointslice bw-new -o jsonpath='{.endpoints[*].addresses[*]}{"\n"}'
   ```

6. Test point 2 three ways: leave `addressType` out, give it the third legal value, and try to
   change it after the object exists.

   ```sh
   kubectl apply -f - <<'YAML' 2>&1 | tail -3
   apiVersion: discovery.k8s.io/v1
   kind: EndpointSlice
   metadata:
     name: bw-notype
     namespace: bw-epd
     labels: {kubernetes.io/service-name: bw-new}
   endpoints:
     - addresses: [10.180.9.9]
   ports: [{name: https, protocol: TCP, port: 443}]
   YAML
   kubectl apply -f - <<'YAML' 2>&1 | tail -3
   apiVersion: discovery.k8s.io/v1
   kind: EndpointSlice
   metadata:
     name: bw-fqdn
     namespace: bw-epd
     labels: {kubernetes.io/service-name: bw-new}
   addressType: FQDN
   endpoints:
     - addresses: [example.com]
   ports: [{name: https, protocol: TCP, port: 443}]
   YAML
   kubectl -n bw-epd patch endpointslice bw-new --type=merge -p '{"addressType":"IPv6"}' 2>&1 | tail -3
   ```

7. Test point 4 against the number the reference now carries. Two addresses in one entry, then one
   hundred and one.

   ```sh
   kubectl apply -f - <<'YAML' 2>&1 | tail -3
   apiVersion: discovery.k8s.io/v1
   kind: EndpointSlice
   metadata:
     name: bw-two
     namespace: bw-epd
     labels: {kubernetes.io/service-name: bw-new}
   addressType: IPv4
   endpoints:
     - addresses: [10.180.7.1, 10.180.7.2]
   ports: [{name: https, protocol: TCP, port: 443}]
   YAML
   kubectl -n bw-epd get endpointslice bw-two -o jsonpath='{.endpoints[*].addresses[*]}{"\n"}' 2>/dev/null
   { cat <<'YAML'
   apiVersion: discovery.k8s.io/v1
   kind: EndpointSlice
   metadata:
     name: bw-101
     namespace: bw-epd
     labels: {kubernetes.io/service-name: bw-new}
   addressType: IPv4
   endpoints:
     - addresses:
   YAML
     for i in $(seq 1 101); do echo "      - 10.181.0.$i"; done
     echo 'ports: [{name: https, protocol: TCP, port: 443}]'
   } > /tmp/bw-101.yaml
   kubectl apply -f /tmp/bw-101.yaml 2>&1 | tail -3
   ```

8. Test point 5. Store an endpoint with `ready: false`, one with no `conditions` block at all, and
   read back what the API server actually persisted for each.

   ```sh
   kubectl -n bw-epd get endpointslice bw-new \
     -o jsonpath='{range .endpoints[*]}{.addresses[0]}{"\t"}{.conditions}{"\n"}{end}'
   kubectl -n bw-epd get endpointslice bw-new -o yaml | sed -n '/^endpoints:/,/^ports:/p'
   ```

9. Ask the ordinary Service from step 2 the question the post's first section is really about: how
   many objects answer for one Service, and what each one is named. Then delete the Endpoints object
   and watch what comes back.

   ```sh
   kubectl -n bw-epd get endpoints app -o jsonpath='{.metadata.name}{"\n"}' 2>/dev/null
   kubectl -n bw-epd get endpointslice -l kubernetes.io/service-name=app \
     -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.addressType}{"\n"}{end}'
   kubectl -n bw-epd delete endpoints app 2>&1 | tail -2
   sleep 5
   kubectl -n bw-epd get endpoints app 2>&1 | tail -3
   ```

10. Offline, in the pinned checkout on the workstation, count what this exercise rests on: the
    redirect, the status tokens, the stale paths, the warning string, the KEP number and the two
    page sizes. Nothing here needs a cluster.

    ```sh
    cd /path/to/kubernetes/website
    grep -n 'service-resources/endpoint-slice-v1' static/_redirects.base
    awk 'NF>=3 && $1 ~ /^\// {print $NF}' static/_redirects.base | sort | uniq -c
    cd content/en
    grep -rn 'service-resources' docs | wc -l
    grep -rln 'service-resources' docs | wc -l
    grep -rn 'use discovery.k8s.io/v1 EndpointSlice' . | wc -l
    grep -rn '4974' docs | wc -l
    wc -l -c docs/reference/kubernetes-api/core/endpoints-v1.md \
            docs/reference/kubernetes-api/discovery/endpoint-slice-v1.md
    ```

**Expect**

Step 1 should report a server at v1.35 and list both resources: `endpoints` in the core group with
the short name `ep`, and `endpointslices` in `discovery.k8s.io/v1`. The read of the `kubernetes`
Endpoints object in `default` is the cheapest possible test of the post's claim, since that object
exists on every cluster. If a `Warning:` line appears above the table, the behaviour the post
announces for 1.33 is present at 1.35; if none appears, record that and treat every later `(no
warning)` in step 3 as uninformative rather than as a finding. The EndpointSlice read should be
quiet either way.

Step 2 should leave one Endpoints object named `app` and one EndpointSlice named `app-` plus a
five-character suffix, both carrying the two pod IPs. The Endpoints read is the second place a
warning can appear and the first one on an object this exercise created. Note whether the warning is
printed once per command or once per object; the mechanism that decides this is [the 2020 warnings
post's](../2020/07-warnings.md) subject, not this file's.

Step 3 is the shape of the answer, not a single answer. The likely result is that reads and writes
of `endpoints` warn — including through the `ep` alias, which resolves to the same resource — and
that reads of the Service do not, because a Service is a different type. `describe endpoints` is
worth its own line: it is a read of the deprecated type, so it should warn, whereas `describe svc`
prints an `Endpoints:` field that `kubectl` now assembles from slices, and should not. The three
sample `describe svc` outputs in the pinned tree — `validate-dual-stack.md:246`,
`create-external-load-balancer.md:102` and `connect-applications-service.md:142` — all show that
field with no warning above it, which is a prediction this step can check. The `--raw` line may well
print nothing: a warning is an HTTP response header, and whether `kubectl` surfaces it on a raw
request is exactly what is being asked.

Step 4 is the one that settles the disagreement. The exact match should return one line per address
family — one here, since the cluster is single-stack. The prefix `ap` should return zero, and that
zero is the finding: `kubernetes.io/service-name=ap` is an equality selector that happens to be
spelled like a prefix, and the label selector grammar has no containment operator at all. The
presence selector and the set selector should both return the slice. Read the result against
`endpoint-slice-v1.md:31`, which says the label *"contains"* the Service name, and against
`labels-annotations-taints/_index.md:1413-1415`, which says it is *"set to"* it. Write down which
one a reader could act on.

Step 5 should print `10.180.3.17 10.180.5.22 10.180.18.2` from the Endpoints object and `10.180.3.17
10.180.5.22 10.180.18.12 10.180.6.6` from the slice. The third address differs by one digit. Both
objects are accepted, because both are valid — nothing in the API can know that one was meant to be
a transcription of the other, and neither type checks a `nodeName` against the nodes that exist, so
`node-4` through `node-9` are stored on a cluster that has one node. If a `nodeName` is refused,
drop the field from both objects and re-run: the addresses are the whole point of the step. The
control plane will also mirror the `bw-old` Endpoints into a slice of its own; ignore it here, and
take [the 2020 EndpointSlice post](../2020/06-scaling-kubernetes-networking-with-endpointslices.md)
for what the bridge does and when it declines to.

Step 6 should give three different refusals or, more interestingly, fewer than three. Omitting
`addressType` should fail validation, since `endpoint-slice-v1.md:39` marks the field required.
`FQDN` should be accepted, because the reference lists it as a supported value even while saying
nothing implements it — an object the API stores and no component reads. The patch should be refused
as an immutable-field update. If `FQDN` is instead rejected, the reference's enum and the server
disagree, and that is a larger finding than the one this step went looking for.

Step 7 should accept the two-address entry, keep both addresses, and route to neither beyond the
first. The reference is explicit that the controller writes exactly one and that kube-proxy does not
look past it, so the correct reading of a successful apply is *stored but meaningless*, which is a
different thing from *supported*. The 101-address object should be refused by validation against the
documented maximum of 100; if it is accepted, the number in `endpoint-slice-v1.md:106` is
aspirational and that is worth recording against the post's *"by convention"*.

Step 8 should show the first three endpoints of `bw-new` with no `conditions` key at all and the
fourth with `ready: false`. That absence is the point: `endpoint-slice-v1.md:151` says a nil `ready`
*"should be interpreted as 'true'"*, so three of the four endpoints are ready by omission rather
than by assertion, which is not how the Endpoints object the post started from expressed the same
thing — there, membership of `addresses` rather than `notReadyAddresses` said it explicitly. The
post's point 5 is right that conditions replace the split; it does not mention that the replacement
encodes the common case as silence.

Step 9 should show exactly one Endpoints object, named for the Service, against one or more slices
whose names the caller cannot predict — the asymmetry the post's first section is built on. After
the delete, the Endpoints object should reappear within a sync period, because
`kube-controller-manager.md:437` still runs `endpoints-controller` by default. That reappearance is
the state KEP-4974 proposes to make optional, and watching it come back is the closest this cluster
can get to the plan the post describes.

Step 10 should print: one redirect line, `:557`, mapping the post's path to `discovery/`; a
status-token tally of 449 `301`, 23 `301!`, 29 `302`, 9 `302!`, one `308` and six `404`; 17
occurrences of `service-resources` across 7 files under `docs/`; exactly 1 occurrence of the warning
string in `content/en`, in the post; 0 occurrences of `4974`; and 1,268 lines against 1,319 for the
two reference pages. If the redirect grep returns nothing, the link really is dead and every claim
in this exercise about it inverts — check the path before concluding anything else.

**Read on**

11. [The exercise on the post this one
    answers](../2020/06-scaling-kubernetes-networking-with-endpointslices.md) — walks the API's
    arrival, its sharding default, and the five gates that carried it. Its step 6 builds a slice by
    hand for a selectorless Service, which is the same apparatus step 5 here uses for a different
    purpose. Take its finding that the post's scalability arithmetic rests on a number absent from
    the tree, and say whether the deprecation announcement five years later supplies it.

12. [The exercise on warnings](../2020/07-warnings.md) — owns the `Warning` header end to end: how a
    server raises one, how a client deduplicates it, and the metrics that count them. Step 3 here
    produces a table of which verbs warn; take that table there and say which of the header's
    documented behaviours it demonstrates, and which it cannot show from `kubectl` alone.

13. [The lab on the API that is being deleted](../../labs/07/06-the-api-that-is-being-deleted.md) —
    produces the same result through `v1.Endpoints` and `discovery/v1.EndpointSlice` and reads
    KEP-4974 directly. This exercise found that `4974` appears nowhere in the pinned documentation
    and that `endpoints-controller` is still on by default; carry both facts into that lab's
    two-line statement of what the KEP removes.

14. [The exercise on the 1.16 deprecations](../2019/08-api-deprecations-in-1-16.md) — the other
    deprecation post in the archive, and the opposite case: there the versions named were actually
    removed. Read its account of what the deprecation policy permits against
    `deprecation-policy.md:83`, and say in one line why the Endpoints announcement could promise a
    warning but not a removal date.

15. [The lab that predicts endpoint
    conditions](../../labs/07/04-eleven-kilobytes-of-endpointslice.md) — asks for `Ready`, `Serving`
    and `Terminating` across five pod states from the field comments alone. Step 8 here shows that
    three of four endpoints carry no `conditions` key at all; take that back to the lab and say
    which of its five predictions are made from an absent field rather than a present one.

**Teardown**

```sh
kubectl delete namespace bw-epd --ignore-not-found
rm -f /tmp/ep-app.yaml /tmp/ep-app.err /tmp/bw-101.yaml
kubectl get endpointslice -A 2>/dev/null | grep bw- || echo 'clean'
```

One namespace holds everything, including the two selectorless Services and every hand-written
slice, so the delete is the whole teardown. Nothing in this exercise changes a component's
configuration, restarts a control-plane pod, or touches a feature gate, so the cluster is left
exactly as step 1 found it — which is worth confirming, because the answer step 1 recorded about
whether this cluster warns at all is the baseline steps 2 and 3 are judged against.
