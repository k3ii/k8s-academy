<a id="evolving-kubernetes-networking-with-the-gateway-api"></a>

# Every kind in this post has to be re-grouped before the apiserver will look at it, and then it refuses all of them anyway, because the pin ships none of this: the API is an add-on whose version the tree never names, and the one relationship that reversed kept the word the post gave it

**Post** — [Evolving Kubernetes networking with the Gateway
API](https://kubernetes.io/blog/2021/04/22/evolving-kubernetes-networking-with-the-gateway-api/),
2021-04-22, by Mark Church (Google), Harry Bagdi (Kong), Daneyon Hanson (Red Hat), Nick Young
(VMware) and Manuel Zapf (Traefik Labs) — five authors from five vendors, which is the point the
post is making before it makes any argument. 200 lines, 10,642 bytes. No `k8s` version in the
frontmatter and none in the body, and the census row leaves the version column empty: this post
announces an API that ships on its own release train, and that fact is most of the exercise.

**As written**

The post opens by calling Ingress a success and then explaining how the success became the problem.
Ingress `created a diverse ecosystem of Ingress controllers which were used across hundreds of
thousands of clusters in a standardized and consistent way`, and that standardization `helped users
adopt Kubernetes`. But five years on there are `signs of fragmentation into different but strikingly
similar CRDs` and `overloaded annotations`. The sentence the whole post hangs on is `:14`: `The same
portability that made Ingress pervasive also limited its future.`

It then dates its own origin precisely. A group of contributors gathered at KubeCon 2019 San Diego,
`the discussion overflowed to the hotel lobby across the street`, and what came out of it became the
Gateway API. Three assumptions are listed at `:18-20`: that route matching, traffic management and
service exposure are `commoditized and provide little value to their implementers and users as
custom APIs`; that L4/L7 routing can be represented `through common core API resources`; and that
extensibility for complex capabilities is possible `in a way that does not sacrifice the user
experience of the core API`.

Four design principles follow at `:27-30`. Expressiveness, which buys header manipulation, traffic
weighting and mirroring and TCP/UDP routing — things `only possible in Ingress through custom
annotations`. Role-oriented design, in which the resource model `reflects the separation of
responsibilities that is common in routing and Kubernetes service networking`. Extensibility,
meaning `arbitrary configuration attachment at various layers within the API`. And flexible
conformance, three named levels: `core (mandatory support)`, `extended (portable if supported)`, and
`custom (no portability guarantee)`.

The resource types are introduced at `:36-38`. GatewayClasses are cluster-scoped templates, `similar
in concept to StorageClasses, but for networking data-planes`. Gateways are `the deployed instances
of GatewayClasses`, the logical representation of the data plane. And Routes are `not a single
resource, but represent many different protocol-specific Route resources` — HTTPRoute, and then
`TCPRoutes`, `UDPRoutes` and `TLSRoutes`, each of which `also have protocol-specific semantics`.
Four route kinds, presented as peers.

The post is honest about maturity in one sentence, `:44`: `although Gateway is in Alpha, there are
already several Gateway controller implementations that you can run`. It links a releases page for
the word Alpha and an implementations page for the controllers, and claims portability across them:
because it is a standardized spec, `the following example could be run on any of them and should
function the exact same way`.

The worked example is a three-team scenario at `:50-52`: team foo controls the routing logic for the
pages of its app, team bar wants blue-green rollouts to reduce risk, and a platform team `is
responsible for managing the load balancer and network security of all the apps`. Four YAML fences
follow, all at `apiVersion: networking.x-k8s.io/v1alpha1`. `:58-89` is `foo-route`, an HTTPRoute in
namespace `foo` with three rules, each matching `path.type: Prefix` and forwarding through
`forwardTo` to a `serviceName` on port 8080. `:107-131` is `bar-route` in namespace `bar`, one rule
splitting `weight: 90` and `weight: 10` across two Services and a second matching the HTTP header
`env: canary` — written as `headers.values`, a map. `:151-169` is the Gateway `prod-web`, an HTTPS
listener on port 443 with `tls.certificateRef` naming an `admin-controlled-cert`. `:177-187` is a
fragment: the same `foo-route` with nothing but metadata, two comments, and a YAML end-of-document
marker where the spec should be.

Both route manifests carry a label, `gateway: external-https-prod`, and the Gateway selects on it.
The Gateway's listener holds a `routes` block with `kind: HTTPRoute`, a `selector.matchLabels`
naming that label, and `namespaces.from: All`. The post explains this at `:140` as *Route binding*,
which `describes how Routes and Gateways create a bidirectional relationship between each other`,
and the fourth fence exists purely to show `how the Route can ensure it matches the Gateway's
selector` via its kind and its labels. The direction of that sentence matters later: the Gateway
does the selecting, and the Route's job is to be selectable.

The last section, `:190-192`, is the argument the post wants remembered: a single load balancing
infrastructure `that can be safely shared by multiple teams`, an API that is `not only a more
expressive API for advanced routing, but is also a role-oriented API, designed for multi-tenant
infrastructure`.

**As it runs now** — the argument won and the manifests lost. The role-oriented framing the post
argues for is the tree's own language now: `gateway.md:57` says Gateway API is organized into kinds
with interdependent relationships `to support the role-oriented nature of organizations`, and the
API the post was arguing against has been formally frozen. Meanwhile not one of the post's four
fences will be accepted by the pin's apiserver — and neither will the pin's own examples, for a
reason the post could not have written down in 2021.

**The API group is gone without a trace.** `networking.x-k8s.io` has zero occurrences in
`content/en/docs` at the pin. The API shipped as `gateway.networking.k8s.io`, and the version on
every example is `v1`, not `v1alpha1`. That string appears in exactly four files:
`concepts/services-networking/gateway.md`, which is the whole of the pin's Gateway API
documentation; `concepts/storage/volume-populators-and-data-sources.md`;
`reference/labels-annotations-taints/_index.md`; and
`reference/kubernetes-api/core/persistent-volume-claim-v1.md`. Two of the three that are not the
Gateway page itself are storage pages and the third is the annotation registry. More on that below.

**Re-grouping is not enough, because the pin does not ship the API at all.** This is the finding the
census row understates. `gateway.md:270-272` is explicit: `Instead of Gateway API resources being
natively implemented by Kubernetes, the specifications are defined as Custom Resources supported by
a wide range of implementations`, and `:13` introduces Gateway API as an add-on. A cluster built
from the pin therefore refuses `gateway.networking.k8s.io/v1` exactly as it refuses
`networking.x-k8s.io/v1alpha1` — same error, same reason, and the reason has nothing to do with the
rename. The post's `Gateway is in Alpha` was a statement about a version; five years later the
correct statement is about a location, and the API is still not in the tree.

**The pin names no Gateway API version anywhere.** `gateway.md` carries 14 links to
`gateway-api.sigs.k8s.io` and not one release number; the install step at `:273` is a link, the
conformance section at `:250-257` defers `release channels, support levels, and running conformance
tests` off-site in a single sentence, and `:282` sends the reader to an API specification whose URL
path is `main`. So the census row's instruction to install the CRDs at the pin's version cannot be
carried out from the pin: there is no such version recorded. This exercise therefore does not
install the real API, and the substitution it makes instead is the most interesting thing in the
lab.

**The same worked example, five years apart, with every key renamed.** The pin's HTTPRoute at
`:141-159` routes `www.example.com` with `path` `/login` to a Service on port 8080. The post's
`foo-route` at `:69-75` routes `foo.example.com` with `path` `/login` to a Service on port 8080. The
structure is identical down to the indentation of `matches`; three keys differ. `type: Prefix`
became `type: PathPrefix`. `forwardTo` became `backendRefs`. `serviceName` became `name`. A learner
who reads only these two fences learns the whole rename in under a minute, and learns nothing about
why the apiserver rejects both.

**The one relationship that reversed direction kept the word the post gave it.** In the post the
Gateway selects: `spec.listeners[].routes.selector.matchLabels` names a label, and routes wear that
label to be chosen. At the pin the Route declares: `spec.parentRefs` is a top-level key on the pin's
HTTPRoute at `:147-148` and on both GRPCRoutes, naming the Gateway by name, and the Gateway's only
say is a veto — `allowedRoutes`, described at `:60-61` as the Gateway filtering `the routes that may
be attached to its listeners, forming a bidirectional trust model with routes`. That sentence is the
post's word, five years on, over an inverted mechanism. The post's `bidirectional relationship`
meant a label match that either side could break; the pin's `bidirectional trust model` means the
Route points and the Gateway consents. No label selector survives anywhere on the page.

**The pin's only demonstration of route filtering sets the field to its own default.**
`allowedRoutes` occurs exactly twice in `gateway.md`: once in the Gateway example at `:113-115`, as
`namespaces.from: Same`, and once in a note at `:127-128` which states that `By default, a Gateway
only accepts Routes from the same namespace` and that `Cross-namespace Routes require configuring
allowedRoutes`. The example's use of the field changes nothing. So the page documents that
cross-namespace routing needs configuration and then never shows the configuration — which is
precisely the case the post's `namespaces.from: All` demonstrates, for a Gateway in one namespace
and routes in two others.

**The post's administrative delegation example has no counterpart at the pin.** `prod-web` is an
HTTPS listener on 443 whose certificate is `admin-controlled-cert`, and the whole role-oriented
argument rests on that: the platform team owns the certificate, the app teams own the routes. The
pin's Gateway example is an HTTP listener on port 80 with no `tls` block, and the page's entire
treatment of TLS is one sentence at `:124-125` pointing at an off-site guide. The pin also renders
`certificateRef` nowhere, so the post's singular field name cannot even be diffed against its
successor without leaving the pin.

**Three of the four route kinds the post names have no presence at the pin, and a fourth it never
mentions is stable.** `TCPRoute`, `UDPRoute` and `TLSRoute` have zero occurrences in
`content/en/docs`. `gateway.md:42` says `Gateway API has four stable API kinds` and lists
GatewayClass, Gateway, HTTPRoute and GRPCRoute — and GRPCRoute is not in the post. The pin documents
stable kinds only, so their absence is evidence about what reached stability, not proof that the
protocol-specific Routes were abandoned; the post presented four route kinds as peers, and five
years later exactly one of them is on this page and it is joined by a stranger.

**The figure shows three of the four.** `:63` introduces the diagram as illustrating `the
relationships of the three stable Gateway API kinds`, and its alt text repeats the number. Read at
the pin, `content/en/docs/images/gateway-kind-relationships.svg` contains four text nodes:
`cluster`, `GatewayClass`, `Gateway` and `HTTPRoute`. So the page is not contradicting itself — the
figure really does show three — but the kind it leaves out is the one it had just finished adding to
the list, and GRPCRoute appears in no diagram on the page.

**The post's real victory is on a page it never mentions.** `ingress.md:25-33` opens with a note:
`The Kubernetes project recommends using Gateway instead of Ingress. The Ingress API has been
frozen.` It then spells out what frozen means — Ingress stays generally available, `The Kubernetes
project has no plans to remove Ingress from Kubernetes`, and `The Ingress API is no longer being
developed, and will have no further changes or updates made to it`. The identical note opens
`ingress-controllers.md:12-22`. `gateway.md:261-263` completes it: `Gateway API is the successor to
the Ingress API. However, it does not include the Ingress kind`, so a one-time conversion is
necessary. The post's thesis, that Ingress's portability limited its future, is now the tree's
official position on Ingress.

**And the tension that follows is the thing to sit with.** The pin recommends an API it does not
ship, over an API it does. Run `kubectl api-resources` on a cluster built from the pin and the only
HTTP routing kinds present are `Ingress` and `IngressClass` in `networking.k8s.io/v1` — the frozen
ones. Following the pin's own recommendation requires leaving the pin, and the pin does not say
where to.

**Gateway API's reach at the pin is mostly outside networking.** `ReferenceGrant`, a Gateway API
kind that the Gateway page never names, is a hard prerequisite for a core storage feature:
`volume-populators-and-data-sources.md:122-129` says Kubernetes `checks for a ReferenceGrant in the
other namespace before accepting the reference`, that `ReferenceGrant is part of the
gateway.networking.k8s.io extension APIs`, and that `you must extend your Kubernetes cluster with at
least ReferenceGrant from the Gateway API before you can use this mechanism`; the example at `:142`
is `apiVersion: gateway.networking.k8s.io/v1beta1`, the only `v1beta1` Gateway API version written
anywhere in the tree. `persistent-volume-claim-v1.md:266` repeats the requirement in the API
reference. And `labels-annotations-taints/_index.md:1543-1552` registers the annotation
`gateway.networking.k8s.io/generator`, `added by tools that automatically generate Gateway API
resources`, with the example value `ingress2gateway`. An add-on API has become a dependency of a
core alpha feature and has a reserved annotation in the core reference, while its own kinds remain
uninstallable from the tree.

**What this exercise does not cover, and where it lives.** The release history of Gateway API — when
it left alpha, when each kind went stable, what a release channel is — is not on the pin's
documentation at any point, and the archive carries it as posts of its own in later years; the
census rows for those years own it. Ingress itself, its controllers and its annotation sprawl are a
2016 subject with a walk of their own. This exercise is the rename, the relocation, and the one
reversal, and it stops where the off-site links start.

**The diff, and why** — three of the seven cases, and the dominant one is the plain one. The post
broke, comprehensively and mechanically, because an alpha API changed its group and renamed its
fields on the way to v1; that is the first case and it accounts for every line of YAML in the post.
The interesting part is what the other two cases are attached to.

**The post broke** in its group first and its fields second. `networking.x-k8s.io/v1alpha1` became
`gateway.networking.k8s.io/v1`, which is a change of both the group name and the API version, and it
is the only part of the diff an apiserver will ever tell you about. Underneath it, `forwardTo`
became `backendRefs`, `serviceName` became `name`, `type: Prefix` became `type: PathPrefix`, a
header match written as the map `headers.values` became a list, and `tls.certificateRef` became
plural. None of those produce an error at the pin, because nothing at the pin has a schema for this
API to check them against — which is the pressure worth naming. An API that lives outside the tree
can rename a field between releases without any of the tree's deprecation machinery being involved,
and the only thing that made this post's manifests fail loudly was the one rename that happened to
touch the group.

**Retired by being agreed with** is the case attached to the argument, and it has to be kept away
from the manifests. What the post asked for was that the Kubernetes project stop extending Ingress
through annotations and adopt a role-oriented replacement. It landed: the pin recommends Gateway
over Ingress in a note repeated verbatim on two pages, states that the Ingress API `has been frozen`
and `is no longer being developed`, and calls Gateway API `the successor to the Ingress API`. The
post's closing call to `help design and influence the future of Kubernetes service networking` is
retired by having happened. Note carefully what did *not* happen: the thing the post tells you to
install did not stop being a separate thing, which is the usual signature of this case. It is still
a separate thing, with its own release train, and that is why the sixth case and the first one land
on different halves of the same post — the argument was adopted, the API was not absorbed.

**Overtaken by stasis** is the case attached to the route kinds. The post lists HTTPRoute,
TCPRoutes, UDPRoutes and TLSRoutes as peers, each with `protocol-specific semantics`, and treats
incremental protocol support as the model's proof of extensibility. Five years and sixteen releases
later the pin's list of stable kinds contains one of those four. The other three appear nowhere in
`content/en/docs`, and the second route kind that is stable is GRPCRoute, which the post never
mentions. There is no failure to observe here and no error message to collect — the finding is the
absence, and *Do* can only show it as an absence.

**What is still right** is the diagnosis, and it is right in a way that reads better now than it did
in 2021. `:14` — `The same portability that made Ingress pervasive also limited its future` — is the
sentence the tree eventually agreed with, and `ingress.md:30-33` is what agreement looks like when
it is written as policy: an API that is permanently available, permanently supported, and
permanently finished.

**The ladder**

The post's subject has no gate, and could not have one. Searched across all 487 feature-gate files
at the pin, **none** mentions Gateway API; the only file whose name contains `Routes` is
`CloudControllerManagerWatchBasedRoutesReconciliation`, which is about node route reconciliation in
the cloud-controller-manager library and has nothing to do with this post. This is what an add-on
looks like from inside the tree: there is no switch to turn on, because there is nothing in the
binary to switch. Every gate in this exercise's ladder is therefore borrowed, and there is exactly
one — the gate that depends on a Gateway API kind rather than providing one.

```
CrossNamespaceVolumeDataSource  alpha  false  1.26
```

One stage, no `toVersion`, no `removed`, no `lockToDefault`: the alpha is current, not a
way-station. Body: `Enable the usage of cross namespace volume data source to allow you to specify a
source namespace in the dataSourceRef field of a PersistentVolumeClaim.` It arrived in v1.26 and at
v1.37 it has not moved — twelve releases on the first rung, which is the stasis case again, in a
gate this time instead of an API kind. What makes it worth transcribing here is the dependency
direction. Turning this gate on gives you a PersistentVolumeClaim field whose use requires a
`ReferenceGrant`, and `ReferenceGrant` is not in the binary the gate belongs to: it is a kind from
an add-on API whose own documentation page does not name it. A core feature, however alpha, cannot
reach stability without something the tree does not ship — and the gate file, which carries `_build:
{list: never, render: false}` like all 487 of them, says none of that.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`, 4096MB, 4
CPUs, 25G. Nothing in this exercise sends a packet. Every observation is a decision made by
kube-apiserver about whether a group, a version and a kind are known to it, which means a single
node with no workloads is the whole rig — and it means the lab can be honest about its ceiling in
one sentence: no Gateway controller is installed, nothing reconciles anything, and every object
created here is inert. The control-plane taint can stay where it is: this exercise creates
namespaces, CustomResourceDefinitions and custom objects, and not one Pod.

**Do**

1. Start where a reader in 2026 starts: by pasting the post into a cluster. Three of the post's four
   fences are complete manifests and are reproduced here character for character; the fourth,
   `:177-187`, is a fragment with no spec and is left out. All four parse as YAML — the post's code
   is not broken — so whatever happens next is the cluster's opinion and not the parser's:

   ```sh
   cat > /tmp/post-fences.yaml <<'EOF'
   kind: HTTPRoute
   apiVersion: networking.x-k8s.io/v1alpha1
   metadata:
     name: foo-route
     namespace: foo
     labels:
       gateway: external-https-prod
   spec:
     hostnames:
     - "foo.example.com"
     rules:
     - matches:
       - path:
           type: Prefix
           value: /login
       forwardTo:
       - serviceName: foo-auth
         port: 8080
     - matches:
       - path:
           type: Prefix
           value: /home
       forwardTo:
       - serviceName: foo-home
         port: 8080
     - matches:
       - path:
           type: Prefix
           value: /
       forwardTo:
       - serviceName: foo-404
         port: 8080
   ---
   kind: HTTPRoute
   apiVersion: networking.x-k8s.io/v1alpha1
   metadata:
     name: bar-route
     namespace: bar
     labels:
       gateway: external-https-prod
   spec:
     hostnames:
     - "bar.example.com"
     rules:
     - forwardTo:
       - serviceName: bar-v1
         port: 8080
         weight: 90
       - serviceName: bar-v2
         port: 8080
         weight: 10
     - matches:
       - headers:
           values:
             env: canary
       forwardTo:
       - serviceName: bar-v2
         port: 8080
   ---
   kind: Gateway
   apiVersion: networking.x-k8s.io/v1alpha1
   metadata:
     name: prod-web
   spec:
     gatewayClassName: acme-lb
     listeners:
     - protocol: HTTPS
       port: 443
       routes:
         kind: HTTPRoute
         selector:
           matchLabels:
             gateway: external-https-prod
         namespaces:
           from: All
       tls:
         certificateRef:
           name: admin-controlled-cert
   EOF
   kubectl apply -f /tmp/post-fences.yaml 2>&1 | sort -u
   ```

2. Now ask whether the rename is the problem. Copy the pin's three examples — `gateway.md:75-82`,
   `:100-116` and `:141-159` — without changing a character, and send them to the same apiserver. If
   the group name were the whole story, these would be accepted:

   ```sh
   cat > /tmp/pin-examples.yaml <<'EOF'
   apiVersion: gateway.networking.k8s.io/v1
   kind: GatewayClass
   metadata:
     name: example-class
   spec:
     controllerName: example.com/gateway-controller
   ---
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: example-gateway
     namespace: example-namespace
   spec:
     gatewayClassName: example-class
     listeners:
     - name: http
       protocol: HTTP
       port: 80
       hostname: "www.example.com"
       allowedRoutes:
         namespaces:
           from: Same
   ---
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: example-httproute
   spec:
     parentRefs:
     - name: example-gateway
     hostnames:
     - "www.example.com"
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /login
       backendRefs:
       - name: example-svc
         port: 8080
   EOF
   kubectl apply -f /tmp/pin-examples.yaml 2>&1 | sort -u
   kubectl api-versions | grep -i gateway || echo "no gateway group served"
   kubectl api-resources --api-group=gateway.networking.k8s.io
   ```

3. Ask the cluster what it *does* serve for HTTP routing, and read the answer against the note at
   `ingress.md:25-33`. The pin recommends Gateway over Ingress and says the Ingress API `has been
   frozen`; this is the list of what a cluster built from the pin actually offers a reader who wants
   to route HTTP:

   ```sh
   kubectl api-resources --api-group=networking.k8s.io
   kubectl explain ingress.spec.rules.http.paths.pathType 2>&1 | head -20
   ```

4. Install a schema that is deliberately not the Gateway API. Three CustomResourceDefinitions in the
   pin's group, at the pin's version, with the pin's kinds and scopes — and with
   `x-kubernetes-preserve-unknown-fields: true` at the root, the extension whose rules are [the
   structural-schema exercise](../2019/06-crd-structural-schema.md)'s subject, so that nothing
   inside `spec` is validated or pruned. This is scaffolding and it must be said plainly: it makes
   the apiserver recognise the kinds without giving it a single opinion about their contents. No
   Gateway API implementation behaves this way:

   ```sh
   for K in GatewayClass:gatewayclasses:Cluster Gateway:gateways:Namespaced HTTPRoute:httproutes:Namespaced; do
     KIND=${K%%:*}; REST=${K#*:}; PLURAL=${REST%%:*}; SCOPE=${REST#*:}
     cat <<EOF | kubectl apply -f -
   apiVersion: apiextensions.k8s.io/v1
   kind: CustomResourceDefinition
   metadata:
     name: ${PLURAL}.gateway.networking.k8s.io
   spec:
     group: gateway.networking.k8s.io
     scope: ${SCOPE}
     names:
       plural: ${PLURAL}
       singular: $(echo "$KIND" | tr 'A-Z' 'a-z')
       kind: ${KIND}
     versions:
     - name: v1
       served: true
       storage: true
       schema:
         openAPIV3Schema:
           type: object
           x-kubernetes-preserve-unknown-fields: true
   EOF
   done
   kubectl api-resources --api-group=gateway.networking.k8s.io
   ```

5. Send the pin's three examples again, unchanged, into that scaffolding. The Gateway example names
   a namespace this cluster does not have, so create it first — otherwise the error you collect is a
   missing namespace, which has nothing to do with anything this exercise is about:

   ```sh
   kubectl create namespace example-namespace
   kubectl apply -f /tmp/pin-examples.yaml
   kubectl get gatewayclasses,gateways,httproutes -A
   ```

6. Send the post's fences again, also unchanged. Nothing about them has been made valid, but the
   reason they fail is now narrower than it was in step 1, and it is the only reason left:

   ```sh
   kubectl apply -f /tmp/post-fences.yaml 2>&1 | sort -u
   ```

7. Change one string per document — the `apiVersion`, and nothing else — and send the post's
   manifests a third time. Every field name in them is five years out of date; none of them is being
   corrected here:

   ```sh
   kubectl create namespace foo
   kubectl create namespace bar
   sed 's|^apiVersion: networking.x-k8s.io/v1alpha1$|apiVersion: gateway.networking.k8s.io/v1|' \
     /tmp/post-fences.yaml > /tmp/post-regrouped.yaml
   kubectl apply -f /tmp/post-regrouped.yaml
   kubectl get httproute foo-route -n foo -o yaml | sed -n '/^spec:/,$p'
   ```

8. Ask both HTTPRoutes the same question, which is the question the five-year diff turns on: which
   Gateway does this Route attach to? Then ask both Gateways the mirror of it: which Routes does
   this Gateway accept? One field answers in each direction, and they are not the same field:

   ```sh
   echo "post's route, parentRefs:  $(kubectl get httproute foo-route -n foo -o jsonpath='{.spec.parentRefs}')"
   echo "pin's route,  parentRefs:  $(kubectl get httproute example-httproute -o jsonpath='{.spec.parentRefs}')"
   echo "post's route, labels:      $(kubectl get httproute foo-route -n foo -o jsonpath='{.metadata.labels}')"
   echo "pin's route,  labels:      $(kubectl get httproute example-httproute -o jsonpath='{.metadata.labels}')"
   echo "post's gw, listener.routes: $(kubectl get gateway prod-web -o jsonpath='{.spec.listeners[*].routes}')"
   echo "pin's gw, allowedRoutes:    $(kubectl get gateway example-gateway -n example-namespace -o jsonpath='{.spec.listeners[*].allowedRoutes}')"
   ```

9. Read back the two shapes the pin's page cannot show you at all: the canary header match, and the
   platform team's certificate. `bar-route`'s second rule matches a header written as a map under
   `headers.values`, and `prod-web`'s listener terminates TLS with a singular `certificateRef`. Both
   are stored exactly as written, because the scaffolding has no opinion — and neither field name,
   nor any HTTPS listener, nor any header match, appears in `gateway.md`:

   ```sh
   kubectl get httproute bar-route -n bar -o jsonpath='{.spec.rules[1].matches[0].headers}{"\n"}'
   kubectl get httproute bar-route -n bar -o jsonpath='{.spec.rules[0].forwardTo[*].weight}{"\n"}'
   kubectl get gateway prod-web -o jsonpath='{.spec.listeners[0].tls}{"\n"}'
   echo "pin's gateway, tls: [$(kubectl get gateway example-gateway -n example-namespace \
     -o jsonpath='{.spec.listeners[0].tls}')]"
   ```

10. Last, give the apiserver one opinion and watch the diff become visible. Patch the HTTPRoute
    schema so that `spec` requires `parentRefs` — one requirement, the single field the five-year
    inversion turns on — then send the post's re-grouped route again, and look at what happened to
    the copy that is already stored:

    ```sh
    kubectl patch crd httproutes.gateway.networking.k8s.io --type=json -p '[{"op":"add",
      "path":"/spec/versions/0/schema/openAPIV3Schema/properties",
      "value":{"spec":{"type":"object","required":["parentRefs"],
                "x-kubernetes-preserve-unknown-fields":true}}}]'
    kubectl apply -f /tmp/post-regrouped.yaml 2>&1 | sort -u
    kubectl apply -f /tmp/pin-examples.yaml 2>&1 | sort -u
    kubectl get httproute foo-route -n foo -o jsonpath='{.spec.rules[0].forwardTo[0].serviceName}{"\n"}'
    ```

**Expect**

Step 1 collapses to two distinct lines: `no matches for kind "HTTPRoute" in version
"networking.x-k8s.io/v1alpha1"`, and the same sentence with `Gateway` in place of `HTTPRoute` — the
same refusal shape this archive collects from every removed API group. It is worth noticing what it
does *not* say. It does not mention `forwardTo`, `serviceName` or `Prefix`, and it will not mention
them at any point in this exercise unless you make it. The apiserver stopped reading at the group.

Step 2 is the step that changes the shape of the exercise. Three more lines of the same refusal,
this time naming `gateway.networking.k8s.io/v1` — the pin's own documented examples, rejected by a
cluster built from the pin. `kubectl api-versions` prints no gateway group, and `api-resources
--api-group=gateway.networking.k8s.io` returns no rows. The census row's instruction to re-group
every kind is necessary and not sufficient: at the pin, the API is an add-on (`gateway.md:270-272`),
nothing in the tree installs it, and no version of it is named anywhere in the tree to install.

Step 3 gives you the frozen API. The `networking.k8s.io` group serves `ingresses` and
`ingressclasses` alongside `networkpolicies` and whatever else your release puts in that group, and
`kubectl explain` on `pathType` names the same three values `ingress.md:183-199` documents:
`ImplementationSpecific`, `Exact` and `Prefix`. Read that third one against the post. The post wrote
`type: Prefix` because Ingress spelled it `Prefix`; the successor spells it `PathPrefix`. The API
the project recommends renamed the value, and the API the project froze still carries the old name —
so the only cluster-checkable spelling of `Prefix` on this pin belongs to the resource the post was
arguing against.

Step 4 creates three CustomResourceDefinitions, and `api-resources` now lists `gatewayclasses`,
`gateways` and `httproutes` at `gateway.networking.k8s.io/v1`, cluster-scoped for the first and
namespaced for the other two. The cluster has learned the names and nothing else. There is no
GRPCRoute here, no ReferenceGrant, no validation, no controller, and no status will ever be written
on any of these objects.

Step 5 accepts all three of the pin's examples. Create the namespace first: the Gateway example at
`:100-116` names `example-namespace`, and without it you get a namespace-not-found error that looks
nothing like the errors this exercise is about. The HTTPRoute has no namespace in its metadata and
lands in `default`, which means the pin's own three examples are split across two namespaces while
the Gateway's `allowedRoutes.namespaces.from: Same` says it accepts routes from its own — a
combination that a real implementation would reject and this scaffolding cannot see.

Step 6 fails again, with exactly the two lines from step 1. This is the finding worth stopping on:
the kinds now exist, the version now exists, and the post's manifests are still refused. What the
apiserver checks is the group and version string, character for character, and the post's is wrong
in both halves.

Step 7 succeeds. One `sed` on one line per document, and three objects the post wrote in 2021 are
accepted by a 2026 apiserver with every field name five years stale. The stored spec still reads
`forwardTo`, `serviceName` and `type: Prefix`. If you only ever test Gateway API manifests with
`kubectl`, this is the whole of the feedback you get, and it is worthless: the scaffolding accepts
the post's spelling and the pin's spelling with equal enthusiasm, and so would any CRD whose schema
preserves unknown fields.

Step 8 is the inversion, in six lines. The post's route has no `parentRefs` — the field prints
empty, because the concept did not exist — and carries `gateway: external-https-prod` in its labels.
The pin's route has `[{"name":"example-gateway"}]` and no labels at all. Then the Gateways: the
post's listener holds
`{"kind":"HTTPRoute","selector":{"matchLabels":{"gateway":"external-https-prod"}},
"namespaces":{"from":"All"}}`, and the pin's holds `{"namespaces":{"from":"Same"}}`. In the post the
Gateway names the routes it will take; at the pin the route names the Gateway it wants, and the
Gateway's only remaining say is which namespaces it will hear from. The post's word for its version
of this was `bidirectional`; the pin's word, at `gateway.md:60-61`, is still `bidirectional`. The
word survived the reversal it describes.

Step 9 prints three things the pin's page cannot show you and one absence. The header match comes
back as `{"values":{"env":"canary"}}`, a map; the weights come back as `90 10` on `forwardTo`
entries that the current API does not have; the post's TLS block comes back as
`{"certificateRef":{"name":"admin-controlled-cert"}}`, singular. And the pin's Gateway prints `[]`,
because its example listener is plain HTTP on port 80 and `gateway.md` handles TLS by linking a
guide at `:124-125`. The post's entire administrative-delegation argument — the platform team owning
the certificate while app teams own the routes — has no worked counterpart at the pin at all.

Step 10 is where the diff finally becomes an error. The patch adds one requirement to one field, and
the post's re-grouped route stops being acceptable: the apply fails naming `spec.parentRefs` as a
required field, and which layer reports it depends on whether `kubectl`'s strict validation reaches
the schema before the apiserver does. The pin's three examples still apply cleanly. Then the last
line: `foo-auth` — the copy stored in step 7 is still there, still holding `serviceName`, because a
schema change does not revalidate what is already in etcd. That is the shape of every real Gateway
API upgrade this exercise cannot run: the new rule binds the next write, and the old objects sit
there until something touches them.

**Read on**

1. [The structural-schema exercise](../2019/06-crd-structural-schema.md) is where the tool used in
   step 4 comes from, and it is the right place to go if the scaffolding felt like a cheat. It is
   also the exercise that explains why `x-kubernetes-preserve-unknown-fields: true` is the only
   honest way to stand in for an API you do not have: any schema you wrote by hand would be your
   guess at the Gateway API, and guesses are what this whole archive is trying not to produce.

2. `gateway.md:268-283` is the pin's whole answer to *how do I get this*, and it is five links and a
   caution. Read it beside `concepts/extend-kubernetes/api-extension/custom-resources.md`, which is
   what the sentence `the specifications are defined as Custom Resources` is pointing at, and note
   that the pin treats an API it recommends in two other pages' opening notes as a third-party
   extension in its own whatsnext.

3. `ingress.md:25-33` and `ingress-controllers.md:12-22` carry the same note twice, and
   `gateway.md:259-266` is its other half. Between them they are the clearest statement in the tree
   of what it means for the project to agree with a blog post: one API generally available forever
   and never changed again, one API recommended in its place, and a one-time conversion in between
   whose only trace in the tree is an example value in an annotation registry.

4. The sideways reach is worth an hour on its own.
   `concepts/storage/volume-populators-and-data-sources.md:122-129` makes `ReferenceGrant` a hard
   prerequisite for a PersistentVolumeClaim field,
   `reference/kubernetes-api/core/persistent-volume-claim-v1.md:266` repeats it in the API
   reference, and `reference/labels-annotations-taints/_index.md:1543-1552` reserves
   `gateway.networking.k8s.io/generator` in the core annotation registry with the example value
   `ingress2gateway`. Three core pages depending on an add-on, and the add-on's own page naming none
   of them.

5. Unanswerable from the pin: which version of Gateway API the examples in `gateway.md` were written
   against, and therefore what `install the CRDs at the pin's version` could even mean — the tree
   records no version, no release channel and no CRD manifest. Also unanswerable: whether
   `TCPRoute`, `UDPRoute` and `TLSRoute` were abandoned or are merely still pre-stable. The pin
   documents stable kinds and their absence is all it will tell you; the archive answers both
   questions in later years, and the census rows there own them.

**Teardown**

Deleting the three CustomResourceDefinitions removes every object created here with them, which is
the one piece of real Gateway API behaviour this lab does reproduce: uninstalling the API uninstalls
the configuration. Then remove the three namespaces. Nothing else on the node was touched.

```bash
kubectl delete crd httproutes.gateway.networking.k8s.io \
  gateways.gateway.networking.k8s.io \
  gatewayclasses.gateway.networking.k8s.io
kubectl delete namespace foo bar example-namespace
kubectl get crd,namespaces
rm -f /tmp/post-fences.yaml /tmp/post-regrouped.yaml /tmp/pin-examples.yaml
```

The cluster itself is disposable; if you would rather start the next exercise from a clean node,
[the teardown step](../../strands/lab-topologies.md#teardown) is faster than reasoning about what
this one left behind.
