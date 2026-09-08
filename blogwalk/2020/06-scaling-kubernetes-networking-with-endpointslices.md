<a id="scaling-kubernetes-networking-with-endpointslices"></a>

# The pin's own deprecation policy makes one of this post's two closing promises unbreakable and the other one broken, the third promise has no gate file and no page six years later, and the number the whole scalability argument rests on appears nowhere at all in the pinned tree

**Post** — [Scaling Kubernetes Networking With
EndpointSlices](https://kubernetes.io/blog/2020/09/02/scaling-kubernetes-networking-with-endpointslices/),
2 September 2020, by Rob Scott (Google). 46 lines and 6,026 bytes, and not one fenced block: one of
three walks in this year with none. It announces that in Kubernetes 1.19 kube-proxy reads
EndpointSlices instead of Endpoints, explains why the old object could not scale, and then spends
its last section forecasting what happens next.

Every other walk in this year is measured against a manifest or a command. This one has neither.
What it has is four statements about the future — two about the Endpoints API, two about features
EndpointSlices would enable — and a scalability argument built on one number. Six years later, the
pin can be asked about all five. Three of them landed, one is nowhere, and one of the two Endpoints
promises turns out to be guaranteed by written policy while the other one is exactly what the policy
permits to break.

**As written**

The problem statement is one object per Service. `With the Endpoints API, there was only one
Endpoints resource for a Service`, holding every IP and port for every Pod behind it, and
`kube-proxy was running on every node and watching for any updates to Endpoints resources`. The
consequence the post draws is the one that matters: `If even a single network endpoint changed in an
Endpoints resource, the whole object would have to be sent to each of those instances of
kube-proxy.`

Then comes the arithmetic. `The default size limit for an object stored in etcd is 1.5MB. In some
cases that can limit an Endpoints resource to 5,000 Pod IPs.` A Service with 5,000 Pods `might end
up with a 1.5MB Endpoints resource`; in a 3,000-node cluster one endpoint change means `sending
4.5GB of data (1.5MB Endpoints * 3,000 Nodes) across the cluster`, and a rolling update replacing
all 5,000 Pods is `more than 22TB (or 5,000 DVDs) worth of data transferred`. Four figures, all
derived from the first one.

The mechanism is sharding. `Instead of tracking all Pod IPs for a Service with a single Endpoints
resource, we split them into multiple smaller EndpointSlices.` The worked example is a diagram
rather than a fence: fifteen Pods, five endpoints per slice, three slices. `By default,
EndpointSlices store as many as 100 endpoints each, though this can be configured with the
--max-endpoints-per-slice flag on kube-controller-manager.` The claimed result is that `Services can
now scale to at least 10 times beyond any previous limitations`, and that `EndpointSlices have
already been used to scale Services beyond 100,000 network endpoints`.

The last two sections are the forecasts. Three features are named as what the new API was built to
enable: dual-stack Services, which `rely on the addressType field on EndpointSlices to track these
addresses by IP family`; topology aware routing, which `makes use of the topology fields stored for
each endpoint in an EndpointSlice`; and endpoint subsetting, which `would allow kube-proxy to only
watch a subset of EndpointSlices`, described as something `we're exploring the potential of`.

Then the section the title of this exercise comes from. `Although the EndpointSlice API is providing
a newer and more scalable alternative to the Endpoints API, the Endpoints API will continue to be
considered generally available and stable.` `The most significant change planned for the Endpoints
API will involve beginning to truncate Endpoints that would otherwise run into scalability issues.`
And, opening the final paragraph: `The Endpoints API is not going away, but many new features will
rely on the EndpointSlice API.`

**As it runs now**

**The mechanism is intact, down to the default.**
`concepts/services-networking/endpoint-slices.md:62-66` says the control plane creates and manages
EndpointSlices `to have no more than 100 endpoints each` and names the same flag on the same
component, with one addition the post does not have: `up to a maximum of 1000`. The flag itself is
still in the reference at
`reference/command-line-tools-reference/kube-controller-manager.md:721-724`, defaulting to 100, and
its help text mentions no ceiling. The page has the maximum, the flag reference does not.

**The distribution rule is written down now, and it is not the diagram.** `:159-174` gives the
controller's three steps and then says the third one `prioritizes limiting EndpointSlice updates
over a perfectly full distribution of EndpointSlices`, with a worked case: ten new endpoints and two
slices with room for five each produce a new slice rather than two updates. `:176-180` gives the
reason, which is the post's own reason turned around — every slice change is transmitted to every
node, so the controller would rather create than update. The post's picture of fifteen Pods packing
into three slices of five is the best case. `:159` says the control plane `tries to fill
EndpointSlices as full as possible, but does not actively rebalance them`, and `:182-187` argues the
untidy shape should be rare — so the diagram is what the controller aims at and not what it
guarantees, and the difference is a thing a client can see.

**And there is a consequence the post does not mention at all.** `:189-203` says endpoints `may be
represented in more than one EndpointSlice at the same time`, and puts the burden on every client:
iterate all of a Service's slices and deduplicate. The single-object API the post is retiring could
not have this problem. Sharding bought the scalability and sold a correctness obligation to every
consumer, and the note pointing at `kube-proxy`'s own `EndpointSliceCache` as the reference
implementation is the pin admitting the obligation is not trivial.

**The topology fields the post's second forecast rests on are gone as a writable thing.** `:118-127`
lists exactly two per-endpoint topology fields, `nodeName` and `zone`. The map the post means is at
`reference/kubernetes-api/discovery/endpoint-slice-v1.md:113-114`, renamed: `deprecatedTopology
contains topology information part of the v1beta1 API. This field is deprecated, and will be removed
when the v1beta1 API is removed (no sooner than kubernetes v1.24). While this field can hold values,
it is not writable through the v1 API, and any attempts to write to it will be silently ignored.`
`reference/using-api/deprecation-guide.md:99-104` names the two substitutions, and the group-version
that carried the map stopped being served at v1.25.

**The API the post announces reached stable and shed its gate.** `endpoint-slices.md:19` marks the
feature stable for v1.21, and the group-version the post's readers would have used is gone:
`deprecation-guide.md:95-97` records `The discovery.k8s.io/v1beta1 API version of EndpointSlice is
no longer served as of v1.25`, with `v1` available since v1.21. Both halves of the post's own object
therefore moved — the version and one of its fields — while the Endpoints object it was replacing
did not move at all.

**The Endpoints API is deprecated.** `concepts/services-networking/service.md:310-312` opens a
section headed `Endpoints (deprecated)` and marks it deprecated for v1.33, giving three reasons at
`:314-325`. That reading, and the API reference's own deprecation sentence, are already carried by
the exercise that borrowed an Endpoints object for leader election; this exercise takes it as given.

**And the API is not going away, by written rule.** `reference/using-api/deprecation-policy.md:83`
is one line long: `GA API versions may be marked as deprecated, but must not be removed within a
major version of Kubernetes`. Endpoints is `v1` in the core group. The pin marks it deprecated,
recommends at `service.md:324-325` that all clients use EndpointSlice instead, and nowhere names a
release in which Endpoints stops being served, because the policy does not allow one while
Kubernetes is at v1. The post's last promise is not merely still true at the pin; it is the promise
the project had already bound itself to keep.

**The truncation forecast shipped, and became an argument against the thing it was protecting.**
`service.md:327-344` is the section: over 1000 backing endpoints and Kubernetes `truncates the data
in the Endpoints object`, selecting at most 1000, setting `endpoints.kubernetes.io/over-capacity:
truncated`, removing the annotation if the count drops again, and — the sentence that makes it
testable — `The same API limit means that you cannot manually update an Endpoints to have more than
1000 endpoints.` The annotation has its own entry at
`reference/labels-annotations-taints/_index.md:1718-1740`, headed `(deprecated)`, ending in a note
that EndpointSlices `do not require truncation`. Then read `service.md:322`: truncation is listed
there as the third reason not to use the API. The post's `most significant change planned` for the
Endpoints API is now cited by the documentation as a defect of it.

**The number the arithmetic rests on is not in the pinned tree.** `1.5MB`, `1.5 MB` and `1.5MiB`
return nothing across the docs tree, and no page states a per-object size limit for etcd at all.
`100,000` endpoints, the post's demonstrated ceiling, is not there either. What the pin does carry
is `setup/best-practices/cluster-large.md:12-18`: 5,000 nodes, 150,000 total Pods, 110 Pods per
node. The post's example — 5,000 Pods across 3,000 nodes — sits inside that envelope, so the
scenario is still a supported one; only the constant it is multiplied by is unsourced.

**Dual-stack arrived, and the field the post pinned it to is the field that does it.**
`endpoint-slices.md:72-81` says each object represents one address type, `IPv4` or `IPv6`, and that
a dual-stack Service has at least two slices. The `IPv6DualStack` gate reached stable at v1.23 and
is `removed: true`. This forecast is the clean one: named mechanism, named field, delivered.

**Topology aware routing arrived by a different route than the one the post names.** The design the
post describes — routing decided from the topology fields on each endpoint — is not the design that
shipped, and the two gates that record the substitution are transcribed in full by the 2018 IPVS
exercise, which reaches them from the proxy side. This exercise does not re-transcribe them. What it
adds is the field-level consequence: the per-endpoint map the post points at is the one now called
`deprecatedTopology` and silently ignored on write.

**Endpoint subsetting has no page, no field and no gate.** `subsetting` and `endpoint subset` return
nothing in the docs tree. Of the 488 feature-gate files at the pin, the only one whose body contains
the word `subset` is `ShardedListAndWatch`, alpha at v1.36, which lets a client shard list and watch
requests by hash ranges of metadata fields — a general answer to the same watch-volume problem,
arriving seventeen releases later and not specific to endpoints at all. The post's third forecast
was hedged when it was written and it is still hedged; six years produced no artefact for it.

**Endpoints objects are mirrored into slices, and that mirroring is deprecated too.**
`endpoint-slices.md:205-234` describes the compatibility bridge: the control plane mirrors most
user-created Endpoints resources into EndpointSlices, unless the Endpoints carries
`endpointslice.kubernetes.io/skip-mirror: "true"`, or carries a
`control-plane.alpha.kubernetes.io/leader` annotation, or its Service is missing, or its Service has
a selector. The section is marked deprecated for v1.33 along with the rest of the Endpoints API.
That second exclusion is the one the archive has already met: it is there for the leader-election
scheme that wrote its holder into an Endpoints object, which the 2016 leader-election post is the
exercise for.

**The two labels that make mirroring legible are in the reference.**
`labels-annotations-taints/_index.md:1489-1501` documents `endpointslice.kubernetes.io/managed-by`
and gives `endpointslice-controller.k8s.io` as the value meaning a slice built for a Service with a
selector; `:1503-1510` documents `skip-mirror`. `endpoint-slices.md:136-143` says every entity
managing slices should set a unique value. So a cluster's slices can be sorted by who made them,
which is how a reader tells the post's mechanism from the compatibility bridge on the same cluster.

**The one sentence about 1.19 that was not true when it was published.** The post says `In
Kubernetes 1.19 this feature is enabled by default with kube-proxy reading from EndpointSlices
instead of Endpoints`, unqualified. The gate files disagree by platform. `EndpointSliceProxying`
covers `kube-proxy running on Linux` and is beta, default true, from v1.19.
`WindowsEndpointSliceProxying` covers Windows and at v1.19 is alpha, default `false`; it does not
default true until v1.21. On the post's own release the sentence held for Linux nodes and not for
Windows ones, and the gate bodies are where the split is recorded.

**What this exercise does not cover, and where it lives.** The proxy-side ladder — which endpoints a
proxier is allowed to turn into real servers, and the abandoned per-Service topology design that
`TopologyAwareHints` replaced — is transcribed gate by gate in [the 2018 IPVS
post](../2018/04-ipvs-in-cluster-load-balancing.md), together with `trafficDistribution` and the
hints that appear on a slice. The Endpoints object as a container for something other than
endpoints, and the API reference's deprecation sentence, belong to [the 2016 leader-election
post](../2016/01-simple-leader-election-with-kubernetes.md). Zone labels on nodes, and what happened
to the label the post's era would have used, are [the 2016 multi-zone
post](../2016/02-building-highly-available-applications-using-kubernetes-new-multi-zone-clusters-aka-ubernetes-lite.md).
Nothing here revisits kube-proxy's rule tables, which are [the 2019 connection-reset
post](../2019/04-kube-proxy-subtleties-debugging-an-intermittent-connection-resets.md).

**The diff, and why**

**A forecast that split, and the pin's own rulebook is what splits it.** The post's closing section
makes two promises in two sentences, and they are not the same kind of statement. `The Endpoints API
will continue to be considered generally available and stable` is a statement about *status*, and
status is the thing a project can change unilaterally: `deprecation-policy.md:83` permits exactly
this move, marking a GA version deprecated without removing it, and the project made it at v1.33.
`The Endpoints API is not going away` is a statement about *availability*, and the same line of
policy forbids taking that away for as long as Kubernetes is at v1. So the sentence a reader would
call the bolder of the two is the one that held, and it held because it was never the author's
promise to make — the policy had already made it. The weaker-sounding sentence is the one that
broke. This is a case the archive has not produced before: not a post overtaken, not a post wrong
when written, but a post whose two adjacent claims were resolved in opposite directions by the same
paragraph of written rule.

**Wrong when published, and only on the platform the post does not mention.** `In Kubernetes 1.19
this feature is enabled by default with kube-proxy reading from EndpointSlices instead of Endpoints`
was true of Linux nodes and false of Windows nodes on the day it was published, and the gate files
are what say so. This is the cheapest kind of error to make and the hardest to see: the sentence is
not wrong about the release, the default, or the mechanism, only about the scope, and the scope is
the word that is absent.

**A plan abandoned, with no artefact to point at.** Endpoint subsetting was the third forecast and
the only hedged one — `we're exploring the potential of` — and six years later the docs tree has no
page, no field, no gate and no mention. The nearest thing at the pin answers the same underlying
problem from the client side rather than the endpoint side, arrives at v1.36, and is about list and
watch in general. The archive has met abandoned plans before, but they left gate files behind: an
alpha row and a `deprecated` row, or a rename in a body. This one left nothing, and that is worth
recording as its own outcome. A forecast that never became a switch cannot be dated, staged or
found; the only evidence that it was ever project intent is the post.

**Retired by being agreed with, and then used as evidence against itself.** `The most significant
change planned for the Endpoints API will involve beginning to truncate Endpoints that would
otherwise run into scalability issues` is the post's one concrete forecast about the old API, and it
shipped: a hard limit of 1000, an annotation to mark it, and a validation rule that refuses a manual
object above it. Then read where that behaviour is documented. It is not in a section about
protecting Endpoints; it is inside the section headed `Endpoints (deprecated)`, and truncation is
listed at `service.md:322` as one of three reasons to stop using the API. The change the post
described as the API's future is now the documentation's third argument for abandoning it.

**Still right, and more precisely than the post claims.** The sharding mechanism, the 100-endpoint
default and the flag name are unchanged, and the field the dual-stack forecast is pinned to is the
field that does the job. What the pin adds is two operational facts the post's picture leaves out:
the controller deliberately does not pack slices tightly, and endpoints can appear in more than one
slice at once. Both are consequences of the same design decision the post is announcing, and both
are things a reader who believed the diagram would get wrong.

**A soft ceiling became a hard count, which is why the arithmetic cannot be reproduced.** The post's
limit is derived: an etcd object size limit, divided by the size of an endpoint, giving a figure
that varies `in some cases`. The pin has no etcd size limit anywhere and one endpoint limit, 1000,
which is a count rather than a size and is enforced by the apiserver rather than inferred. The
exercise below measures the object it applies to, so a reader can see for themselves how far 1000
endpoints is from 1.5MB and therefore that the number that replaced the post's ceiling is not a
restatement of it. What the exercise settles is narrower than the post's subject and answerable on
two nodes: which group-versions the cluster serves, whether the renamed topology field can be
written, what the sharding flag actually does to slice counts, whether the mirroring bridge behaves
as its four exclusions say, and whether the refusal `service.md:344` promises actually happens.

**The ladder**

Four gates, and one absence. The proxy-side gates are the 2018 IPVS exercise's material and are not
repeated here; these are the gates belonging to the API this post announces and to the one forecast
that shipped as a feature. Transcribed from `reference/command-line-tools-reference/feature-gates/`:

```
EndpointSlice                 alpha  false  1.16 - 1.16
                              beta   false  1.17 - 1.17
                              beta   true   1.18 - 1.20
                              stable true   1.21 - 1.24   removed: true

EndpointSliceNodeName         alpha  false  1.20 - 1.20
                              stable true   1.21 - 1.24   removed: true

WindowsEndpointSliceProxying  alpha  false  1.19 - 1.20
                              beta   true   1.21 - 1.21
                              stable true   1.22 - 1.24   removed: true

IPv6DualStack                 alpha  false  1.15 - 1.20
                              beta   true   1.21 - 1.22
                              stable true   1.23 - 1.24   removed: true

(endpoint subsetting)         no gate file at the pin
```

The first gate is the ordinary shape with one extra rung: a beta that shipped `false` for one
release and then `true`. Read its rows against the post's date. At v1.19 the API had been beta and
default-on for two releases and its gate had two releases left to run before stable. The post is
therefore not announcing the API — it is announcing that a second gate, the proxy-side one, flipped.
That distinction is invisible in the post and obvious in the ladder.

**The second gate skips beta.** `EndpointSliceNodeName` has two rows, `alpha` at v1.20 and `stable`
at v1.21, with nothing between them, for a single field. Of the 488 gate files at the pin, four
carry an explicit `alpha` row followed by a `stable` row and no `beta` row at all, and this is one
of them; the archive has already met another, in the gate for dynamic provisioning, where [the 2016
exercise](../2016/10-dynamic-provisioning-and-storage-in-kubernetes.md) notes the missing beta
without a count to put beside it. Four in 488 is the count. It is rarer than abandoning an alpha and
it means the opposite thing: a change small enough that the project did not think a beta bought it
anything. The field it governs is `nodeName`, which is one of the two survivors of the topology map
— so the field that replaced the post's mechanism climbed faster than the mechanism it replaced.

**The third gate is the one that dates the post's unqualified sentence.**
`WindowsEndpointSliceProxying` is the Windows twin of the Linux gate, and it trails it. At v1.19,
the release the post is about, the Linux gate is beta and default true and the Windows gate is alpha
and default false; the Windows gate does not default true until v1.21, two releases later, and only
from v1.22 do the two read the same. Nothing in the post says `on Linux`, and nothing in the pin's
prose says the split existed; the only record is that these two gate files give different
`fromVersion` values for the same stages. A reader reconstructing 1.19's behaviour from the docs
alone would not find it.

**The fourth gate is the forecast that landed, and it was already climbing when the post was
written.** `IPv6DualStack` went alpha at v1.15, four releases before this post, and reached stable
at v1.23. The post presents dual-stack as something EndpointSlices `will` enable; the gate says the
work had been in flight for a year and was waiting on the field, not the reverse. Forecasting a
feature that is already alpha is the safest kind of forecast in this archive, and it is the one that
came true.

**The absence is the fifth row and it is not a formatting accident.** Endpoint subsetting has no
gate file, so it has no stage, no default, no `fromVersion`, and no `removed: true`. Every other
outcome this archive records for a feature is legible from the gate list: shipped, abandoned,
renamed, stalled in alpha. A plan that never reached a switch is invisible there, and the only way
to establish it went nowhere is to search the tree for its vocabulary and find none. The rule this
yields: when a post forecasts a feature, look for its gate file first; if there is no gate file at
all, the forecast did not fail late, it failed before it was ever built.

**Topology**

[`pair`](../../strands/lab-topologies.md#pair) — a control-plane node at `10.10.10.130` and a worker
at `10.10.10.131`. Two nodes, because the two per-endpoint fields that survived the topology map are
`nodeName` and `zone`, and neither of them says anything on a single node. Bring the pair up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting `topology=pair`,
and confirm both nodes are `Ready` with [the node baseline
steps](../../strands/lab-topologies.md#node-baseline-steps).

Every command below runs on the control-plane node. The workload has to reach both nodes for the
topology fields to differ, and the control plane in this topology carries the default `NoSchedule`
taint, so the Deployment in step 2 declares a toleration for it. That is the only reason the
toleration is there; nothing else in the exercise depends on where a Pod lands.

Two of the steps edit `/etc/kubernetes/manifests/kube-controller-manager.yaml` and wait for the
static Pod to come back. The endpoint slice controller and the mirroring controller both live in
that binary, so it is the component this exercise can break, and the backup taken in step 4 is
restored twice.

**Do**

1. Ask the cluster what the discovery group serves and what became of the post's topology map,
   before building anything. Two questions in four commands: which group-versions exist, and whether
   the renamed field is still described.

   ```bash
   kubectl get --raw /apis/discovery.k8s.io/ | python3 -c 'import json,sys
   for v in json.load(sys.stdin)["versions"]: print(v["groupVersion"])'
   kubectl get --raw /apis/discovery.k8s.io/v1beta1 2>&1 | head -2
   kubectl explain endpointslice.endpoints.deprecatedTopology 2>&1 | head -8
   kubectl explain endpointslice.endpoints --recursive 2>&1 | grep -E 'nodeName|zone|hints|deprecatedTopology|targetRef'
   ```

2. Build the apparatus. A namespace, a zone label on each node so the two nodes are in different
   zones, and six Pods behind one Service, spread across both nodes. `agnhost netexec` answers on
   8080 and is the house workload for anything that needs a real endpoint.

   ```bash
   kubectl create namespace bw-eps
   C=$(kubectl get nodes -o json | python3 -c 'import json,sys
   print([n["metadata"]["name"] for n in json.load(sys.stdin)["items"]
          if "node-role.kubernetes.io/control-plane" in n["metadata"]["labels"]][0])')
   W=$(kubectl get nodes -o json | python3 -c 'import json,sys
   print([n["metadata"]["name"] for n in json.load(sys.stdin)["items"]
          if "node-role.kubernetes.io/control-plane" not in n["metadata"]["labels"]][0])')
   echo "control plane $C, worker $W"
   kubectl label node $C topology.kubernetes.io/zone=bw-zone-a --overwrite
   kubectl label node $W topology.kubernetes.io/zone=bw-zone-b --overwrite
   kubectl apply -f - <<YAML
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: bw-app
     namespace: bw-eps
   spec:
     replicas: 6
     selector:
       matchLabels:
         app: bw-app
     template:
       metadata:
         labels:
           app: bw-app
       spec:
         tolerations:
         - key: node-role.kubernetes.io/control-plane
           operator: Exists
           effect: NoSchedule
         containers:
         - name: agnhost
           image: registry.k8s.io/e2e-test-images/agnhost:2.53
           command: ["/agnhost", "netexec", "--http-port=8080"]
   YAML
   kubectl -n bw-eps expose deployment bw-app --port=80 --target-port=8080
   kubectl -n bw-eps rollout status deployment/bw-app --timeout=180s
   kubectl -n bw-eps get pods -o wide
   ```

3. Read the slice the controller built. `EPS` is the reader used by four of the steps below: per
   slice it prints the name, who manages it, the address type and the endpoint count, and per
   endpoint the address, the two surviving topology fields, the conditions, and whether the renamed
   map is present at all.

   ```bash
   EPS='import json,sys
   for s in json.load(sys.stdin)["items"]:
       m = s["metadata"]
       print(m["name"], m["labels"].get("endpointslice.kubernetes.io/managed-by"),
             s["addressType"], len(s.get("endpoints", [])))
       for e in s.get("endpoints", []):
           print("   ", e["addresses"][0], e.get("nodeName"), e.get("zone"),
                 e.get("conditions"), "deprecatedTopology" in e)'
   kubectl -n bw-eps get endpointslices -l kubernetes.io/service-name=bw-app
   kubectl -n bw-eps get endpointslices -l kubernetes.io/service-name=bw-app -o json | python3 -c "$EPS"
   kubectl -n bw-eps get endpoints bw-app -o json | python3 -c 'import json,sys
   d = json.load(sys.stdin)
   print("subsets", len(d["subsets"]),
         "addresses", sum(len(s["addresses"]) for s in d["subsets"]))'
   ```

4. Now make the post's diagram happen. Six endpoints and a default of 100 give one slice; set the
   flag the post names to 2 and the same six endpoints have to be spread over three, which is the
   fifteen-Pods-over-three-slices picture at lab scale. The backup taken here is the one restored in
   step 5 and again in step 10.

   ```bash
   sudo cp /etc/kubernetes/manifests/kube-controller-manager.yaml /root/kube-controller-manager.yaml.bak
   sudo sed -i '/- kube-controller-manager$/a\    - --max-endpoints-per-slice=2' \
     /etc/kubernetes/manifests/kube-controller-manager.yaml
   grep -c max-endpoints-per-slice /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 30
   kubectl -n kube-system get pods | grep controller-manager
   kubectl -n bw-eps rollout restart deployment/bw-app
   kubectl -n bw-eps rollout status deployment/bw-app --timeout=180s
   sleep 10
   kubectl -n bw-eps get endpointslices -l kubernetes.io/service-name=bw-app -o json | python3 -c "$EPS"
   ```

5. Then find out whether the controller packs slices or avoids updating them. Scale down to three,
   read the counts, scale back to six, read them again, and compare what happened against the
   three-step rule at `endpoint-slices.md:162-174`. Restore the flag afterwards.

   ```bash
   kubectl -n bw-eps scale deployment/bw-app --replicas=3
   sleep 20
   kubectl -n bw-eps get endpointslices -l kubernetes.io/service-name=bw-app -o json | python3 -c "$EPS"
   kubectl -n bw-eps scale deployment/bw-app --replicas=6
   kubectl -n bw-eps rollout status deployment/bw-app --timeout=180s
   sleep 20
   kubectl -n bw-eps get endpointslices -l kubernetes.io/service-name=bw-app -o json | python3 -c "$EPS"
   sudo cp /root/kube-controller-manager.yaml.bak /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 30
   kubectl -n kube-system get pods | grep controller-manager
   ```

6. Test the sentence at `endpoint-slice-v1.md:113-114` directly. Build a slice by hand for a Service
   with no selector, set all three topology expressions on its one endpoint — the two current fields
   and the renamed map — and read back what the apiserver kept.

   ```bash
   kubectl apply -f - <<YAML
   apiVersion: v1
   kind: Service
   metadata:
     name: bw-manual
     namespace: bw-eps
   spec:
     ports:
     - name: http
       port: 80
       protocol: TCP
   YAML
   kubectl apply -f - <<YAML
   apiVersion: discovery.k8s.io/v1
   kind: EndpointSlice
   metadata:
     name: bw-manual-1
     namespace: bw-eps
     labels:
       kubernetes.io/service-name: bw-manual
   addressType: IPv4
   ports:
   - name: http
     protocol: TCP
     port: 80
   endpoints:
   - addresses: ["10.10.10.131"]
     conditions:
       ready: true
     nodeName: $W
     zone: bw-zone-b
     deprecatedTopology:
       kubernetes.io/hostname: $W
       topology.kubernetes.io/zone: bw-zone-b
   YAML
   kubectl -n bw-eps get endpointslice bw-manual-1 -o json | python3 -c 'import json,sys
   e = json.load(sys.stdin)["endpoints"][0]
   for k in sorted(e): print(k, "=", e[k])'
   ```

7. Now the compatibility bridge, and the label that switches it off. Create an Endpoints object for
   a second selectorless Service, watch a slice appear that the endpoint slice controller did not
   build, then set `skip-mirror` and read the result.

   ```bash
   kubectl apply -f - <<YAML
   apiVersion: v1
   kind: Service
   metadata:
     name: bw-mirror
     namespace: bw-eps
   spec:
     ports:
     - name: http
       port: 80
       protocol: TCP
   YAML
   kubectl apply -f - <<YAML
   apiVersion: v1
   kind: Endpoints
   metadata:
     name: bw-mirror
     namespace: bw-eps
   subsets:
   - addresses:
     - ip: 10.244.99.1
     - ip: 10.244.99.2
     ports:
     - name: http
       port: 80
       protocol: TCP
   YAML
   sleep 20
   kubectl -n bw-eps get endpointslices -l kubernetes.io/service-name=bw-mirror -o json | python3 -c "$EPS"
   kubectl -n bw-eps label endpoints bw-mirror endpointslice.kubernetes.io/skip-mirror=true
   sleep 20
   kubectl -n bw-eps get endpointslices -l kubernetes.io/service-name=bw-mirror
   ```

8. Then the post's one concrete forecast, as a refusal. `service.md:344` says an Endpoints object
   cannot be manually updated past 1000 endpoints. Build one with 1001 addresses, apply it, and then
   build the same object with 1000. The two files differ by one line.

   ```bash
   kubectl apply -f - <<YAML
   apiVersion: v1
   kind: Service
   metadata:
     name: bw-big
     namespace: bw-eps
   spec:
     ports:
     - name: http
       port: 80
       protocol: TCP
   YAML
   MKBIG='import sys
   n = int(sys.argv[1])
   head = ["apiVersion: v1", "kind: Endpoints", "metadata:", "  name: bw-big",
           "  namespace: bw-eps", "subsets:", "- addresses:"]
   body = ["  - ip: 10.244.%d.%d" % (i // 250, i % 250 + 1) for i in range(n)]
   tail = ["  ports:", "  - name: http", "    port: 80", "    protocol: TCP"]
   open("/tmp/bw-big-%d.yaml" % n, "w").write("\n".join(head + body + tail) + "\n")'
   python3 -c "$MKBIG" 1001
   python3 -c "$MKBIG" 1000
   grep -c 'ip:' /tmp/bw-big-1001.yaml /tmp/bw-big-1000.yaml
   kubectl apply -f /tmp/bw-big-1001.yaml 2>&1 | tail -3
   kubectl apply -f /tmp/bw-big-1000.yaml 2>&1 | tail -3
   kubectl -n bw-eps get endpoints bw-big -o json | python3 -c 'import json,sys
   d = json.load(sys.stdin)
   print("addresses", sum(len(s["addresses"]) for s in d["subsets"]))
   print("annotations", d["metadata"].get("annotations"))'
   ```

9. Measure the thing the post multiplies. One Endpoints object with 1000 addresses, and the slices
   the mirroring controller made from it, in bytes as the apiserver serves them. This is the post's
   premise — one large object against many small ones — at the boundary the pin actually enforces.

   ```bash
   sleep 30
   kubectl -n bw-eps get endpoints bw-big -o json | wc -c
   kubectl -n bw-eps get endpointslices -l kubernetes.io/service-name=bw-big --no-headers | wc -l
   kubectl -n bw-eps get endpointslices -l kubernetes.io/service-name=bw-big -o json | python3 -c 'import json,sys
   for s in json.load(sys.stdin)["items"]:
       print(s["metadata"]["name"], len(s.get("endpoints", [])),
             len(json.dumps(s)), s["metadata"]["labels"].get("endpointslice.kubernetes.io/managed-by"))'
   ```

10. Last, the switch. The gate that carried this API is `removed: true`, and so is the gate for the
    field that replaced its topology map. Offer both names to the component that owns the endpoint
    slice controller and read what happens; the fence is indented like the others but the recovery
    is the part that matters.

    ```bash
    sudo sed -i '/- kube-controller-manager$/a\    - --feature-gates=EndpointSlice=true,EndpointSliceNodeName=true' \
      /etc/kubernetes/manifests/kube-controller-manager.yaml
    grep -c feature-gates /etc/kubernetes/manifests/kube-controller-manager.yaml
    sleep 30
    kubectl -n kube-system get pods | grep controller-manager
    sudo crictl logs --tail 15 $(sudo crictl ps -a --name kube-controller-manager -q | head -1) 2>&1 | tail -15
    sudo cp /root/kube-controller-manager.yaml.bak /etc/kubernetes/manifests/kube-controller-manager.yaml
    sleep 30
    kubectl -n kube-system get pods | grep controller-manager
    kubectl -n bw-eps get endpointslices -l kubernetes.io/service-name=bw-app --no-headers | wc -l
    ```

**Expect**

Step 1 should show `discovery.k8s.io/v1` and nothing else. The group the post introduced shipped as
`v1beta1` first, and `deprecation-guide.md:95-99` records both that `v1` has been available since
v1.21 and that the beta version stopped being served at v1.25, so the raw request for it should fail
rather than return a resource list. The two `explain` calls are the interesting half:
`deprecatedTopology` is still in the v1 schema at `endpoint-slice-v1.md:113-114`, so record whether
`explain` describes it, and whether the recursive listing shows `nodeName`, `zone`, `hints` and
`targetRef` beside it. If it does, the post's topology map is still a field the API will accept and
describe, which is not the same as a field the API will keep.

Step 2 should place some of the six Pods on each node. The toleration is what makes that possible;
without it all six would land on the worker and the two topology fields would be constant across
every endpoint, which would make step 3 unreadable. Check the `-o wide` output before going on. If
every Pod is on one node, the scheduler had a reason, and the rest of the exercise still runs but
says less.

Step 3 should print one EndpointSlice, managed by `endpointslice-controller.k8s.io`, address type
`IPv4`, with six endpoints. Six is well under the default of 100 from `endpoint-slices.md:62-66`, so
no sharding is needed yet. Per endpoint, expect an address, a `nodeName`, a `zone` matching the
label set in step 2, and a conditions map; `endpoint-slices.md:83-116` names `ready`, `serving` and
`terminating`, so record which of the three the controller actually wrote. Expect the last column to
read `False` on every line: `deprecatedTopology` is in the schema but the controller does not
populate it. The Endpoints object should report the same six addresses, because the endpoints
controller is still running and still writing it.

Step 4 is the post's diagram, reproduced by lowering the ceiling instead of raising the endpoint
count. With `--max-endpoints-per-slice=2` the same six endpoints cannot fit in one slice, so expect
three, each with two endpoints, each with its own name. The rollout restart is there because the
controller reacts to endpoint changes rather than to its own configuration changing, so a slice that
already exists and already fits may not be resplit until the endpoints behind it move. Record
whether three is the total, or whether an emptied slice from the previous shape is still listed. The
`grep -c` before the wait should print 1, and the controller-manager Pod should come back `Running`
within the thirty seconds; if it does not, the manifest edit went in at the wrong indentation and
`/root/kube-controller-manager.yaml.bak` is the way back.

Step 5 is where the post's picture and the pin's description come apart. Scaling to three endpoints
with a ceiling of two could give two slices, or it could leave three slices holding one endpoint
each, because `endpoint-slices.md:169-174` says the third step of the algorithm prioritises limiting
EndpointSlice updates over packing slices full. Scaling back to six could fill the existing slices
before creating new ones, or create new ones and leave the old ones sparse. Record what happened
both times and read it against `:162-174` rather than predicting it here: the point of the step is
that the controller is allowed to be untidy, and the post's evenly-filled diagram is a picture of
the API, not of the controller. The restore at the end should bring the flag count back to zero and
the Pod back to `Running`.

Step 6 should read back an endpoint with `addresses`, `conditions`, `nodeName` and `zone`, and no
`deprecatedTopology` key at all. That is `endpoint-slice-v1.md:113-114` enforced rather than
documented: the write is not rejected, it is silently discarded, so a client that still populates
the old map gets no error and no data. Note the shape of the failure, because it is the shape a
compatibility field has when it has been kept for parsing and abandoned for storage.

Step 7 should produce a slice for `bw-mirror` that the endpoint slice controller did not build,
carrying the two invented addresses with no `nodeName` and no `zone`, because a hand-written
Endpoints object has no Pods behind it to read a node from. Record the
`endpointslice.kubernetes.io/managed-by` value rather than expecting one:
`endpoint-slices.md:141-143` fixes the endpoint slice controller's value and requires other managers
to pick a unique one, and the pin nowhere names the value the mirroring controller uses. This is the
bridge described at `endpoint-slices.md:205-234`, and at the pin the bridge is itself marked
deprecated at `:207`. The `skip-mirror` label is one of the four exclusions at `:222-229`. Record
whether the existing mirror is deleted once the label is set, left in place as a stale slice, or
left in place and no longer updated; the pin states the exclusion but does not state what happens to
a mirror that already exists.

Step 8 is the post's one concrete forecast, arriving as a refusal rather than as truncation. The
1001-address object should be rejected by validation; the 1000-address object should be accepted.
That is `service.md:344` exactly, and it is the second half of what `service.md:322` lists as the
third reason to stop using the API. Do not expect the `endpoints.kubernetes.io/over-capacity`
annotation on `bw-big`: `labels-annotations-taints/_index.md:1726-1730` says the control plane adds
it when the associated Service has more than 1000 backing endpoints, and this object has no
selector, so nothing was truncated to produce it. The annotation marks the case the post predicted;
this step reaches the same limit from the other side, by hand, and finds a wall instead of a trim.

Step 9 turns the post's premise into two numbers. One thousand endpoints in one Endpoints object,
against the slices the mirroring controller cut from it: `endpoint-slices.md:231-234` puts a maximum
of 1000 addresses per subset on the mirror and the default of 100 per slice still applies, so expect
around ten slices. Record all three figures, the whole-object byte count, the slice count and the
per-slice byte counts, and then compare the largest of them against 1.5MB. The post multiplies that
constant by 5,000 IPs and 3,000 nodes to reach 22TB of traffic. The constant appears nowhere in the
pinned tree, and the object the pin does bound is bounded by a count, not by a size. Whatever number
this step prints is the honest version of the post's first paragraph.

Step 10 offers a component two gate names that both read `removed: true` in the ladder above. A
removed gate may or may not be handled the same way as a name the binary has never heard of, and the
pin does not say which, so record what happens: the Pod may never come back, it may come back and
log a rejection, or it may accept the names and warn. Read the `crictl` output before restoring,
since a static Pod that fails to start leaves nothing for `kubectl` to describe. The restore should
bring the controller-manager back and the slice count for `bw-app` back to one, which is also the
check that nothing in the previous nine steps left the controller wedged.

**Read on**

1. The post's arithmetic starts from a per-object limit of 1.5MB. Grep the pinned tree for it. Then
   read `setup/best-practices/cluster-large.md:12-18` and work out whether the 5,000-Pod Service in
   the post's scenario is inside the supported envelope at all, and what `service.md:330` and `:344`
   bound instead.

2. Read `endpoint-slices.md:152-187` in full, then `:189-203`. The first passage is the distribution
   algorithm and the second is duplicate endpoints. Decide from them what a client reading slices
   has to do that a client reading Endpoints did not, and whether the post's diagram tells you about
   it.

3. `endpoint-slices.md:207` marks the mirroring controller deprecated, and `service.md:312` marks
   the Endpoints API itself deprecated. Read `reference/using-api/deprecation-policy.md:83` and work
   out which of those two words can be followed by a removal and which cannot.

4. The post makes three predictions about topology. Read the `hints` field in `endpoint-slice-v1.md`
   and the `topology` passage at `endpoint-slices.md:118-127`, then read the seven-gate ladder in
   [the 2018 exercise on IPVS](../2018/04-ipvs-in-cluster-load-balancing.md) and decide which of the
   three arrived, which arrived under a different name, and which left only two fields behind.

5. Unanswerable from the pin: endpoint subsetting. The post says the community is exploring it, and
   the pinned tree has no page for it, no field for it, and no feature gate file for it. The pin can
   tell you the idea was not built. It cannot tell you whether it was rejected, deferred, or
   absorbed into something the pin describes under another name.

**Teardown**

```bash
kubectl delete namespace bw-eps
kubectl label node --all topology.kubernetes.io/zone-
rm -f /tmp/bw-big-1001.yaml /tmp/bw-big-1000.yaml
sudo cp /root/kube-controller-manager.yaml.bak /etc/kubernetes/manifests/kube-controller-manager.yaml
sudo rm -f /root/kube-controller-manager.yaml.bak
sleep 30
kubectl -n kube-system get pods | grep controller-manager
kubectl get nodes
```

Then take the pair down with [the teardown steps](../../strands/lab-topologies.md#teardown).
