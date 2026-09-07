<a id="Improvements-to-the-Ingress-API-in-Kubernetes-1.18"></a>

# All three of the post's additions survive at v1, and the one it published as optional with a default is now required with none — the pin never calls that default a default, and the only one left is what `kubectl create ingress` reads off an asterisk it puts at both ends of a path

**Post** — [Improvements to the Ingress API in Kubernetes
1.18](https://kubernetes.io/blog/2020/04/02/Improvements-to-the-Ingress-API-in-Kubernetes-1.18/), 2
April 2020, by Rob Scott (Google) and Christopher M Luciano (IBM). 88 lines and 5,571 bytes. Three
additions, announced in a bulleted list at the top and then taken one at a time: a `pathType` field,
an `IngressClass` resource, and wildcards in hostnames. Two manifests, one match table, and a
closing section on where the API is going.

All three additions are still there. That is the unusual thing about this post: nothing it announces
was reverted, renamed or gated away. What happened instead is that one of the three was described in
a way the pin will not repeat, and the API it was added to stopped being developed at all. Work the
`pathType` thread first — it is the one where the post and the pin make incompatible statements
about the same field — and the manifests second.

**As written**

The lead-in (`:11`) names three *"significant additions"* to the Ingress API in Kubernetes 1.18: *"a
new `pathType` field that can specify how Ingress paths should be matched"*, *"a new `IngressClass`
resource that can specify how Ingresses should be implemented by controllers"*, and *"support for
wildcards in hostnames"*.

Path types come first (`:17-22`), as three bullets. The first carries a parenthesis in its label,
set in bold in the post's own markup — `ImplementationSpecific (default)` — and then *"with this
path type, matching is up to the controller implementing the `IngressClass`. Implementations can
treat this as a separate `pathType` or treat it identically to the `Prefix` or `Exact` path types."*
Then *"**Exact:** Matches the URL path exactly and with case sensitivity"* and *"**Prefix:** Matches
based on a URL path prefix split by `/`. Matching is case sensitive and done on a path element by
element basis."* Three sentences for three types, and one parenthesis naming a default.

Ingress classes come second (`:24-50`), with a reason. The Ingress resource *"was designed with
simplicity in mind, providing a simple set of fields that would be applicable in all use cases. Over
time, as use cases evolved, implementations began to rely on a long list of custom annotations for
further configuration. The new `IngressClass` resource provides a way to replace some of those
annotations."* An `IngressClass` names the controller that should implement its Ingresses and may
point at a custom resource for extra parameters; the post prints one (`:28-39`). A new
`ingressClassName` field on the Ingress spec references it (`:42`). The
`kubernetes.io/ingress.class` annotation that did the same job before *"never formally defined"* but
*"widely supported by Ingress controllers"*, and *"should now be considered formally deprecated"*
(`:45`). And an `IngressClass` annotated `ingressclass.kubernetes.io/is-default-class: true` becomes
the class assigned to *"new Ingresses without an `ingressClassName` specified"* (`:48-50`).

Wildcards come third (`:52-59`). *"Many Ingress providers have supported wildcard hostname matching
like `*.foo.com` matching `app1.foo.com`, but until now the spec assumed an exact FQDN match of the
host."* Precise matches require the host header to match the host setting; wildcard matches require
the host header to equal the suffix of the wildcard rule. A three-row table follows: `bar.foo.com`
matches `*.foo.com`, `baz.bar.foo.com` does not, `foo.com` does not, both because *"wildcard only
covers a single DNS label"*.

*Putting it All Together* (`:61-80`) prints one Ingress using all three: `ingressClassName:
"external-lb"`, `host: "*.example.com"`, `path: "/example"`, `pathType: "Prefix"`, and a backend of
`serviceName: "example-service"` and `servicePort: 80`. Both of the post's manifests declare
`apiVersion: "networking.k8s.io/v1beta1"`. Controller support is a caveat rather than a step
(`:83`): the features are new, *"each Ingress controller implementation will need some time to
develop support"*, check your controller's documentation.

*The Future of Ingress* (`:85-88`) makes two forecasts. The API *"is on pace to graduate from beta
to a stable API in Kubernetes 1.19"*, and it *"will continue to provide a simple way to manage
inbound network traffic"*. Separately, *"work is currently underway on a new highly configurable set
of APIs that will provide an alternative to Ingress in the future. These APIs are being referred to
as the new “Service APIs”. They are not intended to replace any existing APIs, but instead provide a
more configurable alternative for complex use cases."* The post's only link is to that work's
repository, `http://github.com/kubernetes-sigs/service-apis`.

**As it runs now** — the pin is `kubernetes/website` at `7c76070faf9b19e6a417c446043dbafd10a7aa1d`,
newest release v1.37. The Ingress concept page is 649 lines; `pathType` appears on eight pages in
the tree and `ImplementationSpecific` on three.

**All three additions are at `networking.k8s.io/v1`, and the API they were added to is frozen.**
`ingress.md:21` stamps the page `stable` at v1.19, which is the release the post forecast. Above the
body, `:24-34` and `ingress-controllers.md:12-22` carry the same note twice: the project recommends
Gateway instead of Ingress, the API *"has been frozen"*, and *"is no longer being developed"*. What
that state is, and why an API can be generally available and finished at the same time, is [already
read against a 2016
post](../2016/03-kubernetes-1-2-and-simplifying-advanced-networking-with-ingress.md); this exercise
takes the three additions themselves.

**The field the post publishes as optional with a default is required, and has no default.**
`ingress-v1.md:155` lists `pathType` in the `HTTPIngressPath` table with the required marker beside
it, and the description at `:156` runs to nine lines without the word *default* in it.
`ingress.md:185-186` puts it as a rule: *"Each path in an Ingress is required to have a
corresponding path type. Paths that do not include an explicit `pathType` will fail validation."* A
field can be optional-with-a-default or required-with-none; the post announces the first and the pin
serves the second.

**And the pin does not agree that there was ever a default.** `ImplementationSpecific` occurs three
times in the whole tree: `ingress.md:189-191`, the generated description at `ingress-v1.md:156`, and
one bullet in the migration guide. That bullet, `deprecation-guide.md:268-269`, is the only one that
looks back: *"`pathType` is now required for each specified path. Options are `Prefix`, `Exact`, and
`ImplementationSpecific`. To match the undefined `v1beta1` behavior, use `ImplementationSpecific`."*
The post says `ImplementationSpecific` was the default. The guide says the behaviour was *undefined*
and that `ImplementationSpecific` is what you write to reproduce it. Those are two different claims
about the same six months of the same API, and the pin holds no record of the version that would
settle it.

**The default came back, in `kubectl create ingress`, and the flag help puts the asterisk at the
other end from every one of its own examples.** `kubectl_create_ingress.md:141` documents `--rule`:
*"Rule in format host/path=service:port[,tls=secretname]. Paths containing the leading character '*'
are considered pathType=Prefix."* Leading. The page's own examples put it last — `:52-55` is headed
*"Create an ingress with multiple hosts and the pathType as Prefix"* and its rules are
`foo.com/path*` and `bar.com/admin*`; `:64` and `:69` use `foo.com/*`; `:60` uses
`foo.com/path/subpath*`. Eleven rules appear across the examples, five carry an asterisk, and all
five put it last. Whatever the tool actually does, a path type is being chosen for you off a
character, on the one field the API refuses to choose for you.

**The concept page's expansion of `Prefix` does not parse, and the same broken sentence is on two
pages.** `ingress.md:195-199` reads: *"`Prefix`: Matches based on a URL path prefix split by `/`.
Matching is case sensitive and done on a path element by element basis. A path element refers to the
list of labels in the path split by the `/` separator. A request is a match for path p if every p is
an element-wise prefix of p of the request path."* The last sentence names `p` three times for what
must be two different things. It is in `ingress-v1.md:156` in the same words, which places it in the
Go field comment both pages are drawn from rather than in either page's prose. The post's one-line
version of the same rule — *"matching is case sensitive and done on a path element by element
basis"* — is the half that survived intact, and it is the half that is readable. The section drifted
in one other way: the post says `ImplementationSpecific` matching is *"up to the controller
implementing the `IngressClass`"* (`:20`), and `ingress.md:189-190` says it is *"up to the
IngressClass"* — a resource that holds a controller's name and some parameters, and does no matching
itself.

**One sentence about path types is only in the generated reference.** `ingress-v1.md:156` ends its
`ImplementationSpecific` clause with *"Implementations are required to support all path types."*
That requirement is on controllers, it is the strongest sentence about path types anywhere at the
pin, and `ingress.md`'s *Path types* section (`:183-205`) does not contain it. The post does not
contain it either; the post's version is a caveat pointing outward — *"each Ingress controller
implementation will need some time to develop support for these new features"* (`:83`).

**The post's match table survived word for word; the paragraph above it lost its first clause.**
`ingress.md:244-248` is the post's three-row wildcard table with not one byte changed, typographic
quotes and column padding included. The paragraph at `:239-242` is the post's sentence at `:53` with
the announcement removed: *"Many Ingress providers have supported wildcard hostname matching like
`*.foo.com` matching `app1.foo.com`, but until now the spec assumed an exact FQDN match of the
host"* is gone, and *"http host header"* and *"the Host setting"* have become *"HTTP `host` header"*
and *"the `host` field"*. Six years of edits took the news out of the paragraph and left the table
alone.

**The pin carries the post's `IngressClass` manifest with exactly two edits, and does not carry the
other one at all.** `examples/service/networking/external-lb.yaml`, the file `ingress.md:259`
renders under *Ingress class*, is the post's manifest from `:28-39` name for name and field for
field: an `IngressClass` called `external-lb`, controller `example.com/ingress-controller`,
parameters of kind `IngressParameters` named `external-lb`. Two things differ. `apiVersion` reads
`networking.k8s.io/v1`, and `apiGroup` reads `k8s.example.com` where the post writes
`k8s.example.com/v1alpha`. The post's other manifest, the one at `:64-80` that uses all three
additions, has no counterpart in the examples tree; the pin's equivalents are `minimal-ingress.yaml`
and `ingress-wildcard-host.yaml`, and neither of them sets `ingressClassName` and a wildcard host
and a `pathType` in the same file.

**The second of those two edits corrects a field the post filled in with the wrong kind of value.**
`ingress-class-v1.md:118-119` defines it: *"`apiGroup` is the group for the resource being
referenced. If APIGroup is not specified, the specified Kind must be in the core API group."* A
group, not a group and a version. `k8s.example.com/v1alpha` is a group with a version stapled to it,
in a field whose sibling `kind` (`:122-123`) carries no version either. This was not a change in the
API; `apiGroup` has meant the group since the field existed, so the post's example was describing
something that does not exist on the day it was published. Whether the API server refuses it is a
separate question from whether it means anything, and step 1 asks the first one.

**The default-class annotation acquired an admission controller, and the two pages that describe its
refusal do not describe the same refusal.** `DefaultIngressClass` is in the default-enabled plugin
list at `admission-controllers.md:130`, and its own entry at `:194-210` says it is *Mutating*, that
it *"observes creation of `Ingress` objects that do not request any specific ingress class and
automatically adds a default ingress class to them"*, that it *"does not do anything when no default
ingress class is configured"*, and that it *"ignores any `Ingress` updates; it acts only on
creation"*. On the two-default case it says: *"when more than one ingress class is marked as
default, it rejects any creation of `Ingress` with an error"*. Any creation. `ingress.md:377-382`
says something narrower: *"the admission controller prevents creating new Ingress objects that don't
have an `ingressClassName` specified"*. One of those pages says an Ingress that names its class
explicitly is refused along with everything else, and the other says it is not. Step 6 asks the
cluster.

**The annotation the post formally deprecates has three different statuses at the pin.**
`ingress.md:357-368` is headed *Deprecated annotation* and its body never says the annotation is
deprecated: it says it *"was never formally defined, but was widely supported by Ingress
controllers"* and that `ingressClassName` *"is a replacement for that annotation, but is not a
direct equivalent"*. `labels-annotations-taints/_index.md:1568-1576` says it flatly — *"starting in
v1.18, this annotation is deprecated in favor of `spec.ingressClassName`"*. And `ingress-v1.md:77`,
describing `ingressClassName`, says both halves at once: *"even though the annotation is officially
deprecated, for backwards compatibility reasons, ingress controllers should still honor that
annotation if present."* So the deprecation names a replacement that the page defining the
replacement says is not equivalent, and the reference tells implementations to keep honouring the
deprecated thing. The annotation string itself appears exactly three times in the tree, once in each
of those places.

**The successor the post names does not exist under that name, and the pin calls it the successor.**
*Service APIs* appears nowhere in the documentation tree, and neither does `service-apis`; the
repository the post links has a different name now. What does exist is `gateway.md`, 283 lines, a
concept page for Gateway API — *"an add-on containing API kinds"* (`:13`), defined as custom
resources (`:32`), with four stable kinds (`:42`). Its last section is headed *Migrating from
Ingress*, and reads: *"Gateway API is the successor to the Ingress API. However, it does not include
the Ingress kind. As a result, a one-time conversion from your existing Ingress resources to Gateway
API resources is necessary."* (`:259-263`) The tree even registers an annotation for the tooling
that does it — `gateway.networking.k8s.io/generator`, example value `ingress2gateway`
(`labels-annotations-taints/_index.md:1543-1554`). Against that, the post: *"They are not intended
to replace any existing APIs, but instead provide a more configurable alternative for complex use
cases."*

**And one of the post's own reasons was answered by the successor rather than by the addition.** The
post gives `IngressClass` a motive: implementations *"began to rely on a long list of custom
annotations for further configuration"*, and the new resource *"provides a way to replace some of
those annotations"* (`:25`). Some. `gateway.md:34-36` names what the rest were for: Gateway API
*"support[s] functionality for common traffic routing use cases such as header-based matching,
traffic weighting, and others that were only possible in Ingress by using custom annotations."* The
class annotations were replaced by a field in 1.18. The routing annotations were replaced by a
different API, and the post's hedge on the word *some* turns out to be the whole of the story.

**What this exercise does not cover, and where it lives.** The `networking.k8s.io/v1beta1`
group-version that both of the post's manifests declare, the four field renames between `v1beta1`
and `v1`, the refusal you get for a path with no `pathType`, and the `IngressClass` gate ladder are
all [walked on the 2016 Ingress
post](../2016/03-kubernetes-1-2-and-simplifying-advanced-networking-with-ingress.md). `kubectl
convert`, which would do the version half of the porting and does not ship inside `kubectl` any
more, belongs to [the 1.16 deprecations exercise](../2019/08-api-deprecations-in-1-16.md). Nothing
here runs an Ingress controller, so no step in *Do* observes a path being matched or a host header
being compared; every claim the post makes about matching is a claim about controller behaviour, and
this exercise stops at what the API server will accept and what it writes back.

**The diff, and why** — six years is long enough for a three-item announcement to end up in five
different states.

**Still right, and one of them word for word.** The wildcard table came through unedited, and the
forecast in the last section — *"the Ingress API is on pace to graduate from beta to a stable API in
Kubernetes 1.19"* — is stamped on the concept page as `v1.19` `stable`. A post that predicts the
next release correctly and then has its own table copied into the reference documentation unchanged
for six years has done the job. The pressure that usually rewrites a table is a disagreement about
behaviour; hostname wildcards had none, because there was one rule and it was short.

**The post broke, on one word in a parenthesis.** `ImplementationSpecific (default)` was true of
`networking.k8s.io/v1beta1` and is not true of anything served now. The mechanism was graduation:
the field went from optional to required across a group-version boundary, which is a thing the
deprecation policy permits and a thing no amount of care in the post could have anticipated, because
at the time of writing the field had shipped in exactly one version and that version was beta. What
makes this the interesting kind of breakage is that the pin does not simply say *the default was
removed*; it declines to record that there was one, and calls the old behaviour *undefined* instead.
The reader who arrives with the post in hand is not looking at a changed fact. They are looking at a
fact the documentation now denies.

**Retired by being agreed with.** `IngressClass` and `ingressClassName` are not just still there;
they picked up an admission controller that is on by default, a `spec.parameters` extension, a
namespaced-scope field with a gate ladder of its own, and an entry in the annotations reference that
names the field as the annotation's replacement. Everything the post asks for happened. The post's
own paragraph on the subject is now the shortest description of it in existence, which is the usual
fate of a good announcement: it gets replaced by reference documentation that is longer and harder
to read.

**Wrong when it was published.** `apiGroup: "k8s.example.com/v1alpha"` is a group with a version
attached, in a field defined to hold a group. Nothing changed underneath it; the field's meaning is
the same today as it was on the day the post went up. This is the case where the diff is not a diff
at all — the pin's copy of the same manifest has the version stripped, and the reason the example
survived in the documentation is that somebody fixed it there and not here.

**A plan the project abandoned, and it is the plan about the plan.** The post's forecast for the
Ingress API was right. Its forecast for the *thing next to* the Ingress API was not: the *Service
APIs* were renamed, the alternative became the successor, and *"not intended to replace any existing
APIs"* is now contradicted by a page that says a conversion away from Ingress is necessary. The
pressure is visible in the post's own text — the motive it gives `IngressClass` is that
implementations *"began to rely on a long list of custom annotations"*, and it can only claim to
replace *some* of them. The rest needed a different API, and once a different API exists that can
express what the annotations expressed, the API that could not is finished whether anyone intended
that or not.

**Overtaken by stasis, in the negative.** The three additions of 1.18 are the last three additions.
One field graduated in v1.19, one gate ran from v1.21 to v1.24, and after that the Ingress page
acquired a note saying the API is frozen. So the post is not a snapshot of an API in motion; without
knowing it, it is the last release note the Ingress API ever got. Every subsequent piece of Ingress
documentation is either a rewording, a migration instruction, or a pointer somewhere else.

**The ladder** — the Ingress family has exactly one feature gate at the pin,
`IngressClassNamespacedParams`, and its four-row ladder is [transcribed on the 2016 Ingress
post](../2016/03-kubernetes-1-2-and-simplifying-advanced-networking-with-ingress.md) at lines 88–99,
where it belongs, because it is the last thing that happened to the family rather than anything this
post announces. What the table cannot say is the thing that matters here: **none of the three
additions was ever behind a gate.** All three shipped as schema on a beta group-version, and the
group-version *was* the gate — you opted in by writing `networking.k8s.io/v1beta1` at the top of the
file, and you opted out by not having upgraded. A gate ladder records a decision the cluster
operator could make; the 1.18 Ingress additions arrived without one, so on the day of the post there
was nothing to enable and nothing to turn off, and the only lever was which apiVersion you typed.
That lever is also what took the default away.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo). One node, no Ingress controller, and
none installed by any step below. That bounds the exercise hard, and the bound is worth stating
before you start: **nothing here observes a path being matched or a host header being compared.**
Path types and hostname wildcards are two thirds of what the post announces, and both are, in the
end, instructions to a controller. What a controller-less cluster can answer is the other question —
what the API server accepts, what it refuses, and what it writes into an object you did not write
yourself — and every one of the disagreements found above turns out to live on that side of the
line. If you provision from scratch, the [node baseline and
install](../../strands/lab-topologies.md#provision) is the same one every exercise uses.

**Do**

1. The `apiGroup` value, three ways. Start with the post's `IngressClass` from `:28-39`, changed in
   one place only — `apiVersion` to `networking.k8s.io/v1`, because `networking.k8s.io/v1beta1` is
   [not served](../2016/03-kubernetes-1-2-and-simplifying-advanced-networking-with-ingress.md) and
   that refusal is not this exercise's subject. Everything else, quoting included, is the post's.

   ```bash
   kubectl create namespace ing18

   cat > post-class.yaml <<'EOF'
   apiVersion: "networking.k8s.io/v1"
   kind: "IngressClass"
   metadata:
     name: "external-lb"
   spec:
     controller: "example.com/ingress-controller"
     parameters:
       apiGroup: "k8s.example.com/v1alpha"
       kind: "IngressParameters"
       name: "external-lb"
   EOF

   kubectl apply -f post-class.yaml
   PARAMS='import json,sys; print(json.dumps(json.load(sys.stdin)["spec"]["parameters"], indent=2))'
   kubectl get ingressclass external-lb -o json | python3 -c "$PARAMS"
   ```

2. Now the pin's copy of the same manifest, renamed so both can exist at once, and then a value that
   is definitely not a DNS subdomain. Three data points on one field.

   ```bash
   cat > pin-class.yaml <<'EOF'
   apiVersion: networking.k8s.io/v1
   kind: IngressClass
   metadata:
     name: pin-lb
   spec:
     controller: example.com/ingress-controller
     parameters:
       apiGroup: k8s.example.com
       kind: IngressParameters
       name: external-lb
   EOF

   kubectl apply -f pin-class.yaml
   kubectl get ingressclass pin-lb -o json | python3 -c "$PARAMS"

   kubectl apply --dry-run=server -f - <<'EOF'
   apiVersion: networking.k8s.io/v1
   kind: IngressClass
   metadata:
     name: bad-group
   spec:
     controller: example.com/ingress-controller
     parameters:
       apiGroup: "not a group name"
       kind: IngressParameters
       name: external-lb
   EOF
   ```

3. The post's final manifest, the one at `:64-80` that uses all three additions at once, ported to
   `networking.k8s.io/v1`. The four field renames the port needs are [walked
   elsewhere](../2016/03-kubernetes-1-2-and-simplifying-advanced-networking-with-ingress.md); what
   matters here is that the object goes in and comes back out.

   ```bash
   kubectl apply -n ing18 -f - <<'EOF'
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: example-ingress
   spec:
     ingressClassName: external-lb
     rules:
     - host: "*.example.com"
       http:
         paths:
         - path: /example
           pathType: Prefix
           backend:
             service:
               name: example-service
               port:
                 number: 80
   EOF

   kubectl get ingress -n ing18
   SPEC='import json,sys; d=json.load(sys.stdin); print(json.dumps(d["spec"], indent=2))'
   kubectl get ingress example-ingress -n ing18 -o json | python3 -c "$SPEC"
   ```

4. What `pathType` says about itself, and what an empty one does. `explain` reads the same schema
   the API server validates against, so it is the closest thing to an authority on whether the field
   is optional. Then two ways of not choosing a path type that are not the same as omitting the
   field.

   ```bash
   kubectl explain ingress.spec.rules.http.paths.pathType
   kubectl explain ingress.spec.rules.http.paths --recursive | grep -A1 pathType

   for PT in '""' '"ImplementationSpecific"' '"Nonsense"'; do
     echo "--- pathType: $PT"
     kubectl apply --dry-run=server -n ing18 -f - <<EOF
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: pt-probe
   spec:
     ingressClassName: external-lb
     rules:
     - host: probe.example.com
       http:
         paths:
         - path: /p
           pathType: $PT
           backend:
             service:
               name: example-service
               port:
                 number: 80
   EOF
   done
   ```

5. The default that came back. `kubectl create ingress` infers a path type from an asterisk; the
   flag help says the asterisk is the *leading* character and all five of the page's own
   asterisk-bearing examples put it last. Ask the client, which needs no cluster to answer, and
   while you are there ask what a path with no asterisk at all becomes — the case the page does not
   document.

   ```bash
   PT='import json,sys; d=json.load(sys.stdin)
   for r in d["spec"]["rules"]:
       for p in r["http"]["paths"]:
           print(repr(p["path"]), "->", p["pathType"])'

   RULES='foo.com/path=svc:8080
   foo.com/path*=svc:8080
   foo.com/*path=svc:8080
   foo.com/*=svc:8080
   foo.com/=svc:8080'

   echo "$RULES" | while read RULE; do
     echo "--- $RULE"
     kubectl create ingress probe --class=external-lb --rule="$RULE" \
       --dry-run=client -o json | python3 -c "$PT"
   done
   ```

6. Hostname wildcards, on the only side of them a cluster with no controller can see. The pin's
   table (`ingress.md:244-248`) is about matching, which needs a controller; validation is about
   what shape of host string the API server will store, which does not. Six hosts, one of them the
   post's own.

   ```bash
   for H in '*.example.com' '*.*.example.com' 'foo.*.com' '*' 'a.*' '*.example.com.'; do
     printf '%-20s ' "$H"
     kubectl apply --dry-run=server -n ing18 -f - >/dev/null 2>host.err <<EOF
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: host-probe
   spec:
     ingressClassName: external-lb
     rules:
     - host: "$H"
       http:
         paths:
         - path: /p
           pathType: Prefix
           backend:
             service:
               name: example-service
               port:
                 number: 80
   EOF
     if [ $? -eq 0 ]; then echo accepted; else echo "refused: $(tr '\n' ' ' < host.err)"; fi
   done
   ```

7. One default class. Mark the post's class default with the annotation the post introduces, create
   an `Ingress` that names no class, and read back a field you did not write. This is the
   `DefaultIngressClass` admission plugin, which the post does not mention because it did not exist
   when the post was written.

   ```bash
   kubectl annotate ingressclass external-lb ingressclass.kubernetes.io/is-default-class=true

   NOCLASS='apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: NAME
   spec:
     rules:
     - host: noclass.example.com
       http:
         paths:
         - path: /p
           pathType: Prefix
           backend:
             service:
               name: example-service
               port:
                 number: 80'

   echo "$NOCLASS" | sed 's/name: NAME/name: noclass-one/' | kubectl apply -n ing18 -f -

   CN='import json,sys; d=json.load(sys.stdin)
   print("field:", repr(d["spec"].get("ingressClassName")))'
   kubectl get ingress noclass-one -n ing18 -o json | python3 -c "$CN"
   ```

8. Two default classes, which is the case two pages of the pin describe differently. One says the
   plugin *"rejects any creation of `Ingress` with an error"*; the other says it prevents creating
   Ingresses *"that don't have an `ingressClassName` specified"*. So try both: one Ingress with no
   class, one with a class named explicitly. Then, because the plugin's own entry says it *"ignores
   any `Ingress` updates"*, edit the object that already exists.

   ```bash
   kubectl annotate ingressclass pin-lb ingressclass.kubernetes.io/is-default-class=true
   kubectl get ingressclass -o custom-columns=NAME:.metadata.name,\
   DEFAULT:'.metadata.annotations.ingressclass\.kubernetes\.io/is-default-class'

   echo "$NOCLASS" | sed 's/name: NAME/name: noclass-two/' | kubectl apply -n ing18 -f -

   echo "$NOCLASS" | sed 's/name: NAME/name: withclass/' \
     | sed 's/^spec:/spec:\n  ingressClassName: external-lb/' | kubectl apply -n ing18 -f -

   kubectl patch ingress example-ingress -n ing18 --type=json \
     -p='[{"op":"replace","path":"/spec/rules/0/http/paths/0/path","value":"/example2"}]'
   ```

9. Back to one default class, and then the deprecated annotation against the plugin that fills in
   the field. An `Ingress` that carries `kubernetes.io/ingress.class` and no `ingressClassName` is
   exactly the object the post's deprecation is about, and the pin does not say anywhere what the
   mutating plugin does with it. Two more probes for the neighbouring cases: an `Ingress` that names
   a class which does not exist, and one created while no class is marked default at all.

   ```bash
   kubectl annotate ingressclass pin-lb ingressclass.kubernetes.io/is-default-class-

   kubectl apply -n ing18 -f - <<'EOF'
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: annotated
     annotations:
       kubernetes.io/ingress.class: nginx
   spec:
     rules:
     - host: annotated.example.com
       http:
         paths:
         - path: /p
           pathType: Prefix
           backend:
             service:
               name: example-service
               port:
                 number: 80
   EOF

   ANN='import json,sys; d=json.load(sys.stdin)
   print("field:", repr(d["spec"].get("ingressClassName")))
   print("annotations:", d["metadata"].get("annotations"))'
   kubectl get ingress annotated -n ing18 -o json | python3 -c "$ANN"

   echo "$NOCLASS" | sed 's/name: NAME/name: ghostclass/' \
     | sed 's/^spec:/spec:\n  ingressClassName: no-such-class/' | kubectl apply -n ing18 -f -

   kubectl annotate ingressclass external-lb ingressclass.kubernetes.io/is-default-class-
   echo "$NOCLASS" | sed 's/name: NAME/name: nodefault/' | kubectl apply -n ing18 -f -
   kubectl get ingress nodefault -n ing18 -o json | python3 -c "$CN"
   ```

10. The successor, counted. The post names one future API; the pin recommends a different one by
    name and calls it the successor. Ask the cluster the pin's own install procedure builds how much
    of it is there.

    ```bash
    kubectl api-resources | grep -i 'ingress\|gateway'
    kubectl get crd 2>&1 | grep -ci gateway
    kubectl api-versions | grep -i 'networking\|gateway'
    ```

**Expect**

Step 1 applies. What to look at is the read-back: the `apiGroup` field is a string, and the question
is whether the API server stores `k8s.example.com/v1alpha` as written or objects to it. Record
which. The field is a reference to a resource that does not exist in the cluster either — no
`IngressParameters` kind is registered — so if the object is accepted, note that nothing about
`spec.parameters` has been checked against reality at all.

Step 2 gives the comparison. The pin's version, with the group alone, should behave exactly as the
post's did or not; a difference between the two is the finding, and no difference is also the
finding. Then `"not a group name"` — a string with spaces in it, which no group has ever been. If
that is accepted too, `apiGroup` carries no validation, the post's value was never going to be
caught, and the fix in `external-lb.yaml` was a documentation fix rather than a bug report.

Step 3 should apply cleanly and give you the post's example running at `v1`. In the wide listing,
the `CLASS` column carries `external-lb` and `HOSTS` carries `*.example.com`; the `ADDRESS` column
stays empty forever, because that is a controller's job and there is no controller. The spec
read-back is worth reading in full — it is the post's manifest with four field names changed and
nothing else, which is a fair summary of what the `v1beta1`-to-`v1` port costs.

Step 4 is where the post's parenthesis is settled. Read the `explain` output for two things: whether
it marks the field required, and whether the word *default* appears anywhere in it. Then the three
probes. `"ImplementationSpecific"` is accepted; that much the post and the pin agree on. For `""`
and `"Nonsense"`, record the message each produces, and compare them with each other — an empty
string is not a missing field, and whether the API server treats them as the same mistake is not
documented anywhere at the pin.

Step 5 needs no cluster and takes a second. Five rules go in and five path types come out. Write
them down as a table before reading any further, because the interesting result is not any one row:
it is whether the row with a *leading* asterisk and the row with a *trailing* asterisk get different
answers, since the flag description at `kubectl_create_ingress.md:141` and the five examples above
it cannot both be right. The row with no asterisk at all is the one the page never mentions, and
whatever it produces is the default that the API removed, reinstated by the client.

Step 6 prints one line per host. `*.example.com` is accepted — the post's own manifest already
proved that in step 3. The other five are the edges: two wildcard labels, a wildcard in the middle,
a bare asterisk, a wildcard as the last label, and a trailing dot. Record each verdict. None of them
tells you what a controller would *match*; all of them tell you what the API server considers a
legal `host`, and the gap between those two sets is a thing the pin never puts on one page.

Step 7 is the first mutation. The manifest names no class; the object that comes back should, and
reading `.spec.ingressClassName` tells you whether the plugin ran. If the value is `None`, check
that the annotation actually landed on the class before concluding anything — the plugin *"does not
do anything when no default ingress class is configured"*, and a mistyped annotation key is
indistinguishable from a plugin that did not fire.

Step 8 is the disagreement. Two classes are now marked default. `noclass-two` names no class, and
both pages of the pin agree it is refused. `withclass` names `external-lb` explicitly, and the two
pages do not agree: `admission-controllers.md:203-204` says any creation is rejected,
`ingress.md:378-380` says only the ones without a class name. Record which happened, and quote the
error if there is one — that error message is the only authority on the point that exists. The
`patch` on `example-ingress` should then succeed, because the plugin acts only on creation; an
object created before the second default class existed keeps working, which means a cluster can sit
in this state indefinitely and only notice when somebody creates something.

Step 9 has three probes and one of them is unanswerable from the documentation. With one default
class again, `annotated` carries `kubernetes.io/ingress.class: nginx` and no `ingressClassName` —
the exact object the post deprecates. Record whether the plugin overwrites the absent field anyway,
giving you an Ingress that claims one class in an annotation and a different one in a field, or
whether it stands off. Nothing at the pin says which. Then `ghostclass` names a class that does not
exist, and `nodefault` is created with no default class configured; expect the field to survive as
written in the first case and to stay absent in the second, and note that an `Ingress` with a class
name pointing at nothing is as inert as one with no class name at all, for the same reason — nobody
is listening.

Step 10 is a count and an absence. The Ingress resources are all there: `ingresses` and
`ingressclasses` in `networking.k8s.io/v1`, exactly as the post left them. The `grep -ci gateway`
prints `0`; there are no Gateway API custom resource definitions, because Gateway API is an add-on
and nothing in the install procedure this cluster was built with installs add-ons. So the API the
post said would not replace anything is absent from the cluster, and the API the pin calls its
successor is absent too — the recommendation on the front of the Ingress page cannot be followed
here without installing something first, which is worth holding onto when you read the word
*frozen*.

**Read on** — four of these are answerable from the pin, and the fifth is the one the post is about.

1. `ingress.md:183-205` and `ingress-v1.md:155-156` are the same three path types described twice.
   The reference carries one sentence the concept page does not: *"implementations are required to
   support all path types."* Decide which page you would put it on, given that the concept page is
   the one a person reads and the reference is the one generated from the code.

2. `admission-controllers.md:194-210` in full, against `ingress.md:370-382`. Your step 8 result
   settles which is right about the two-default case. Work out what the wrong one would have to say
   instead, and whether the fix is a sentence or a paragraph.

3. `gateway.md:259-266`, *Migrating from Ingress*, and then `gateway.md:34-36`. Read the second one
   as the answer to the post's `:25` — the paragraph that gives `IngressClass` its motive and
   concedes it replaces only *some* of the annotations.

4. `kubectl_create_ingress.md`, the examples at `:37-69` against the `--rule` description at `:141`.
   Step 5 tells you what the tool does. Decide which of the two is the defect, and note that a path
   type is being inferred here for a field the API server refuses to infer.

5. Unanswerable from the pin: whether `pathType` genuinely defaulted to `ImplementationSpecific` in
   `networking.k8s.io/v1beta1`. The post says it did, in a bold label. The migration guide at
   `deprecation-guide.md:268-269` calls the `v1beta1` behaviour *undefined* and gives
   `ImplementationSpecific` as the value you write to reproduce it, which is a different claim. The
   `v1beta1` group-version has been unserved since v1.22 and its reference page is not in the pinned
   tree, so the schema that would settle it — whether the field was optional-with-a-default or
   optional-with-no-default-and-undefined-behaviour — is not here. This is the one case in the file
   where the post is the better witness, and there is nothing at the pin to check it against.

**Teardown** — one namespace, two cluster-scoped classes and three files.

```bash
kubectl delete namespace ing18
kubectl delete ingressclass external-lb pin-lb
rm -f post-class.yaml pin-class.yaml host.err
```

`IngressClass` is cluster-scoped, so deleting the namespace does not take the classes with it; that
is worth noticing on its way out, because it is the shape of the whole addition — a per-cluster
object that per-namespace Ingresses point at. Nothing on the node was reconfigured and no controller
was installed, so the cluster is back where it started.
