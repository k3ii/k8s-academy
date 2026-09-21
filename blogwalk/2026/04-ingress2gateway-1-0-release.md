<a id="ingress2gateway-1-0-release"></a>

# A release announced as 1.0 stamps `ingress2gateway-dev` on every manifest it prints, turns two one-second timeouts into a ten-second one the post then edits to three, and ten of the names and values it writes appear nowhere in a tree whose Gateway vocabulary is one page wide

**Post** — [Announcing Ingress2Gateway 1.0: Your Path to Gateway API](https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release/),
2026-03-20.

377 lines, 15,761 bytes, the twentieth of 2026's fifty-nine published rows and the fourth `walk`
among them. Two authors, Beka Modebadze of Google and Steven Jin of Microsoft, writing for SIG
Network. A single file rather than a page bundle, with no images and no `math`. The census gives it
no Kubernetes version, and it is right not to: nothing in the post ships in a Kubernetes release. It
is also the landing place of the only forward reference [the 2023 census](../2023/README.md) found
that reaches into 2026 — the 2023 tool announcement now opens with an update pointing here.

**As written**

The frame is a deadline. `:11` opens with the Ingress-NGINX retirement *scheduled for March 2026*,
links the 2025 announcement, and says the networking landscape is at a turning point; `:12` narrows
the question from whether to migrate to how to do it safely. `:14-18` gives the reason the migration
is hard: Gateway API is modular and extensible with Kubernetes-native RBAC, the Ingress API is
simple, and implementations such as Ingress-NGINX extend it *through esoteric annotations,
ConfigMaps, and CRDs*, so moving off one means capturing all the nuances of a controller and mapping
them onto a different API. `:20-21` introduces Ingress2Gateway as an assistant that translates
Ingress resources and implementation-specific annotations while warning about what will not
translate. `:23-24` announces 1.0.

Three things changed at 1.0, one per subsection. `:30-32`: annotation coverage went from three
Ingress-NGINX annotations to *over 30 common annotations (CORS, backend TLS, regex matching, path
rewrite, etc.)*. `:36-37`: each supported annotation is backed by controller-level integration tests
that spin up a real Ingress-NGINX controller and real Gateway API controllers, apply both, and
compare runtime behaviour rather than YAML structure — the five bullets are at `:41-45`, and `:47`
sends the reader to the sibling post on surprising Ingress-NGINX defaults. `:52-54`: the
notification formatting was cleaned up, because *surfacing subtleties and untranslatable behavior is
as important as translating supported configuration*.

`:56-64` states the posture the rest of the post is built on. Ingress2Gateway is *a migration
assistant, not a one-shot replacement* (`:58`), with three goals at `:61-63`: migrate what is
supported, identify what is not and suggest alternatives, and reevaluate or discard configuration
you should not have been carrying. Then a worked example in four numbered sections.

The input is at `:67-98`: one Ingress, `my-ns/my-ingress`, `ingressClassName: nginx`, six
`nginx.ingress.kubernetes.io/*` annotations — `proxy-body-size: "1G"`, `use-regex: "true"`,
`proxy-send-timeout: "1"`, `proxy-read-timeout: "1"`, `enable-cors: "true"` and a
`configuration-snippet` that sets a `Request-Id` header — one rule for `my-host.example.com`, one
path `/users/(\d+)` with `pathType: ImplementationSpecific` pointing at `website-service:80`, and a
TLS block naming `my-secret`.

Section 1 (`:100-114`) offers three install paths in order: `go install
github.com/kubernetes-sigs/ingress2gateway@v1.0.0` if you have a Go environment, otherwise `brew
install ingress2gateway`, otherwise the GitHub release binary or a build from source. Section 2
(`:116-131`) shows three ways to run it — `--input-file`, `--namespace`, `--all-namespaces`, each
with `--providers=ingress-nginx` and each redirecting to `gwapi.yaml` — and a note at `:130` that
`--emitter <agentgateway|envoy-gateway|kgateway>` produces implementation-specific extensions.

Section 3 (`:133-288`) is the one the post calls *the most critical step*. `:138-231` prints the
generated manifests: a Gateway named `nginx` with `gatewayClassName: nginx` and two listeners on the
same hostname, port 80 HTTP and port 443 HTTPS with `certificateRefs` to `my-secret`; an HTTPRoute
carrying a CORS filter, a `RegularExpression` match on `(?i)/users/(\d+).*`, and `timeouts.request:
10s`; and a second HTTPRoute with a `RequestRedirect` filter to HTTPS at status 308. Every one of
the three objects carries the annotation `gateway.networking.k8s.io/generator: ingress2gateway-dev`.

`:238-263` prints five notification blocks — four `WARN` and one `INFO` — and `:265-285` walks them.
The `configuration-snippet` annotation is unsupported and you must check your implementation's
documentation. The regex match is case-insensitive because that is what Ingress-NGINX does, which is
where the `(?i)` and the trailing `.*` come from, and `:269` tells you most organizations will want
to strip both. The proxy timeout annotations became a request timeout, and `:272` says that if
requests *should be much shorter, say 3 seconds*, you can edit the manifest. `proxy-body-size` has
no Gateway API equivalent and was dropped, though an emitter might carry it as an extension
(`:276-277`). URL normalization is not configurable through standard Gateway API and varies by
implementation. And the port-80 listener plus the redirect route exist to match Ingress-NGINX's
default. `:286-288` cautions you to review the output and the logs thoroughly.

`:292-351` prints the manifests after those hand edits: the port-80 listener and the redirect route
gone, the path down to `/users/(\d+)`, the timeout down to `3s`. Section 4 (`:353-362`) says to test
in a development cluster, deploy alongside the existing Ingress, shift traffic gradually with
weighted DNS or the platform's traffic splitting, and only then delete the Ingress resources and
uninstall the controller. `:364-367` closes by inviting help *as we approach the March 2026
Ingress-NGINX retirement*, and `:369-377` lists four resources: listener sets, `gwctl`, and two
Slack channels.

**As it runs now**

**Every object in the post is stamped with a name that is not the tool's.** The annotation
`gateway.networking.k8s.io/generator` appears five times in the post — `:143`, `:167` and `:216` in
the generated output, `:298` and `:318` in the hand-edited output — and every one of them carries
the value `ingress2gateway-dev`. A `-dev` suffix is what a Go build stamps when it does not know its
own version, and this is a release announcement whose whole subject is that the version is now 1.0.
The survival of the suffix through the hand-edit section is the part that reads worst: `:292-351` is
the output the post has just told you to review thoroughly, and the stamp is still there. The pinned
annotation registry gives the example value as `ingress2gateway`, without the suffix, at
`labels-annotations-taints/_index.md:1547`, and repeats it in prose at `:1553-1554`.

**The tool is named in exactly two lines of the documentation, and both of them say it does not
matter.** [The 2023 census](../2023/README.md) counted the occurrences; what the two lines actually
say is that the annotation *is informational only and does not affect the behavior of any Gateway
API implementation* (`labels-annotations-taints/_index.md:1554-1555`). So the only place in
`content/en/docs` where a reader meets the word `ingress2gateway` is a reference page for annotation
values, in an entry whose point is that the value has no effect. [The Gateway API
walk](../2021/02-evolving-kubernetes-networking-with-the-gateway-api.md) already has the
registration itself and why an add-on API has a reserved annotation in the core reference.

**The page that tells you the conversion is necessary does not tell you what does it.**
`gateway.md:259-266` is headed *Migrating from Ingress*; [the Ingress API
walk](../2020/02-improvements-to-the-ingress-api-in-kubernetes-1-18.md) has the sentence that says a
one-time conversion is necessary. What follows it is `:265-266`, one more sentence, sending the
reader to an off-site migration guide. The tool is not named there. The two lines that do name it
are on a different page, in the reference section, inside an entry for an annotation, and nothing
links the two pages to each other. A reader who starts at the page the site sends them to for
migration, and who never reads the annotation registry front to back, will not learn the tool exists
from the documentation at all.

**Ten of the names and values the tool writes occur zero times in the whole documentation tree.**
Counting occurrences of each literal under `content/en/docs`: `certificateRefs` 0, `filters:` 0,
`type: CORS` 0, `allowCredentials` 0, `allowOrigins` 0, `maxAge` 0, `RegularExpression` 0,
`timeouts:` 0, `requestRedirect` 0, `statusCode` 0. This is the output of the tool the project
registered an annotation for, and the majority of what it emits has no documented existence on the
site that recommends the migration.

**The five that do occur are all on one page, inside that page's own examples.** `gatewayClassName`
occurs once, at `gateway.md:107`. `listeners:` occurs once, at `:108`. `parentRefs` occurs three
times and `backendRefs` three times, at `:147`, `:187`, `:208` and `:156`, `:192`, `:217` — the
HTTPRoute example [the kind walk](02-experimenting-gateway-api-with-kind.md) uses, plus the two
GRPCRoute examples. `hostnames:` occurs seventeen times, three of them on this page and the other
fourteen in `debug-service.md` and `basic-stateful-set.md`, where the word means something else
entirely. The Gateway API vocabulary in `content/en/docs` is five YAML fences on one 283-line page,
and the generated output of a 1.0 migration tool exceeds it.

**The one occurrence of `CORS` in the documentation is a flag on the apiserver.** The `type: CORS`
filter the tool writes at `:203` comes from `enable-cors`, and CORS is the first item in the post's
own list of newly supported annotations at `:32`. Searching the documentation for it returns
`--cors-allowed-origins`: `kube-apiserver.md:451` documents the flag and `:454` explains that an
allowed origin can be a regular expression and how to anchor it. That is the entire appearance of
the string in the tree, and it has nothing to do with the filter.

**The timeouts do not divide.** The input Ingress asks for one second, twice:
`nginx.ingress.kubernetes.io/proxy-send-timeout: "1"` and `proxy-read-timeout: "1"` at `:74-75`. The
generated HTTPRoute carries `timeouts.request: 10s` at `:209-210`. The prose at `:271` says the tool
made a best-effort translation *from the `nginx.ingress.kubernetes.io/proxy-{send,read}-timeout`
annotations to a 10 second request timeout*, and `:272` then offers to edit it down if requests
*should be much shorter, say 3 seconds* — three times what the Ingress asked for in the first place.
The hand-edited manifest at `:349-350` settles on `3s`, and `:356` tells you to verify that a
three-second timeout is enough. Nowhere in the chain does one second appear again. Either the tool
ignores the annotation values and always writes ten seconds, or the printed output was produced from
a different input than the one printed above it; step 9 is built to find out which, by changing the
annotation and reading what comes out.

**The tool supplies the definition of `ImplementationSpecific` that the API declines to give.** [The
Ingress API walk](../2020/02-improvements-to-the-ingress-api-in-kubernetes-1-18.md) has the
path-type section and what it says about the three types. The relevant part here is that
`ImplementationSpecific` is defined as *matching is up to the IngressClass* and nothing more, so the
translation of `path: /users/(\d+)` with that path type is not a lookup; it is a decision. The tool
decides it means an Ingress-NGINX case-insensitive prefix-anchored regex, and writes
`(?i)/users/(\d+).*` (`:207`). It then immediately tells you, in an `INFO` block at `:244-248` and
in prose at `:268-269`, that you will probably want to undo both halves of the decision it just
made.

**And the decision it makes runs against both path types the API does define.** Of the three path
types, the two with definitions are case-sensitive in as many words. `ImplementationSpecific` is the
one with no definition, and the tool's default rendering of it is the only case-insensitive match in
the picture. That is faithful to Ingress-NGINX and unfaithful to the API: a reader who knew Ingress
path matching from the documentation alone would be surprised by the `(?i)`, which is exactly why
the tool prints a notification about it.

**The Gateway is named after the IngressClass, and no GatewayClass comes with it.**
`ingressClassName: nginx` at `:82` becomes a Gateway named `nginx` at `:144` and a
`gatewayClassName: nginx` at `:147` — one input string, two output meanings. The output never
contains a GatewayClass, so the class the Gateway references does not exist anywhere in the
manifests you are told to apply, and the pinned tree's one example of the field uses the name
`example-class` (`gateway.md:107`). Whether that reference resolves depends entirely on what the
implementation you install happens to call its class, and neither the post nor the output says so.
The grouping rule that produces this is what step 7 measures, by adding a second Ingress and
counting what comes out.

**The redirect route has no matches, so it matches everything.** The second HTTPRoute at `:212-230`
has `parentRefs` to port 80, one rule, one `RequestRedirect` filter, and no `matches` block at all.
The Ingress it came from served exactly one path on that host. The route that replaces it redirects
every path on that host, including paths nothing served before. The post's justification at `:283`
is that this matches Ingress-NGINX's default behaviour, which is true and is also the widest single
behavioural change in the output — and the only change of that size that the notification blocks
pass over in silence.

**Five notifications, two sources, and one of them has no object.** The fence at `:238-263` holds
five blocks: four `WARN` and one `INFO`. Three name `source: INGRESS-NGINX` and two name `source:
STANDARD_EMITTER`. Four carry an `object:` line naming the Ingress or the HTTPRoute the notification
is about; the fifth, the URL normalization warning at `:259-262`, has a source and no object,
because it is about the API rather than about anything in your input. Four of the six input
annotations are named in a block; `use-regex` and `enable-cors` are not, because they translated.
The `INFO` block is the only one that describes a translation that succeeded, and it is there to
warn you about the shape of the success rather than to report it.

**`nginx` is everywhere in the documentation and is never the controller.** The string occurs 1,333
times across 101 files under `content/en/docs`, seventy-five of those as the literal `image: nginx`
in a Pod spec. The string `ingress-nginx` occurs zero times, which [the 2025
census](../2025/README.md) established and which this post's opening sentence depends on being
false. The project's most-used example image and the controller the project is retiring share a
name, and at the pin the tree has kept the first and lost the second entirely.

**The pin disagrees with itself about whether Gateway is an alternative to Ingress.** `ingress.md`
opens, at `:25-26`, by recommending Gateway instead of Ingress — [the Gateway API
walk](../2021/02-evolving-kubernetes-networking-with-the-gateway-api.md) has that note and the
freeze it announces. Six hundred lines later the same page has a section headed *Alternatives*
(`:638-643`), which begins *You can expose a Service in multiple ways that don't directly involve
the Ingress resource* and then lists two: `Service.Type=LoadBalancer` and `Service.Type=NodePort`.
Gateway is not on the list. Neither is it in the page's what's-next at `:645-648`, which offers the
Ingress API reference and the Ingress controllers page. A reader who scrolls to the section named
after the question they are asking gets an answer that omits the successor the same page opened by
recommending.

**Three install paths, and the node baseline can take one of them after an apt install.** `go
install github.com/kubernetes-sigs/ingress2gateway@v1.0.0` (`:105`) needs a Go toolchain, which the
node baseline does not provide; Debian trixie ships one as `golang-go`, which [the validating
admission policy walk](../2024/04-validating-admission-policy-ga.md) already installs for the same
reason. `brew install ingress2gateway` (`:111`) is not a path on a Debian node. The GitHub release
binary at `:114` is, but the post links the release page rather than an asset, so it is the one path
that cannot be written as a command. Step 2 takes the first path, because it is the only one that
pins a version from the command line — and because the version string the resulting binary prints is
the direct test of the `-dev` stamp.

**The `--emitter` flag names three implementations, and the tree names none of them.**
`agentgateway`, `envoy-gateway` and `kgateway` are offered at `:130` and again at `:277`, and Istio
joins them in prose at `:280`. Under `content/en/docs` those four strings occur 0, 0, 0 and 8 times,
and of the eight `Istio` occurrences two are an entry in the third-party controller list at
`ingress-controllers.md:62-63` and the rest are the glossary entry and passing mentions of service
mesh; none is about Gateway API. `gateway.md:272` handles the whole question with a link to an
off-site implementations list. So the post's advice for the annotations that do not translate is to
pick from a set of products the documentation cannot help you choose between.

**The deadline in the first sentence had arrived before the post was published, and the pin is five
months past it.** `:11` says the retirement is *scheduled for March 2026*; the post is dated
2026-03-20. `:367` repeats *as we approach the March 2026 Ingress-NGINX retirement* from inside it.
The pinned tree is from 2026-08-26, and contains no `ingress-nginx` anywhere under `content/en/docs`
— so from the pin's point of view the migration this post is preparing readers for is not upcoming,
it is over, and the tool that assists it is still documented only as an example annotation value.

**What this exercise does not cover, and where it lives.** Nothing here installs an Ingress
controller or a Gateway API implementation, so no request is ever served and no behaviour is ever
compared; this exercise measures what the tool *prints*, not what the printed thing would do.
Getting Gateway API kinds onto a cluster at all, and watching a Gateway acquire an address, is [the
kind walk](02-experimenting-gateway-api-with-kind.md), which runs on `nested` for exactly that
reason. Why the apiserver refuses these kinds at the pin, and what the add-on's relationship to the
core tree is, is [the Gateway API
walk](../2021/02-evolving-kubernetes-networking-with-the-gateway-api.md). The Ingress path types,
the `IngressClass` resource and the annotation sprawl the post is migrating away from are [the
Ingress API walk](../2020/02-improvements-to-the-ingress-api-in-kubernetes-1-18.md) and, for the
original shape of the resource, [the 1.2 Ingress
walk](../2016/03-kubernetes-1-2-and-simplifying-advanced-networking-with-ingress.md). The five
surprising Ingress-NGINX behaviours the post links at `:47` are a `read` row in this year's census
and stay one. And the correctness of the translation — whether the generated Gateway API really
behaves like the Ingress it came from — is the thing the post's integration tests at `:36-37` exist
to establish and the thing a cluster with no controller on it cannot check.

**The diff, and why**

**Wrong when it was published.** Two things, and both are in the output rather than the argument.
The generator annotation reads `ingress2gateway-dev` in all five printed manifests, in a post whose
headline is the 1.0 release and whose own project registered the un-suffixed value in the Kubernetes
annotation reference. And the timeout chain does not connect: one second goes in at `:74-75`, ten
seconds comes out at `:210`, the prose at `:271` attributes the ten to the one, and the correction
at `:272` lands on three. Neither is a fact that time overtook. Both were checkable against the page
they appear on, on the day it was published, by reading twenty lines up.

**Still right.** The posture is the post's best feature and it has not aged at all. *A migration
assistant, not a one-shot replacement* (`:58`) is the correct description of what the output is, the
three goals at `:61-63` include discarding configuration you should not have been carrying, and the
whole of section 3 is built to make you read rather than apply. The notification design earns that:
five blocks, each naming a source and usually an object, each saying what did not translate and why.
The advice at `:358-362` — deploy alongside, shift traffic gradually, delete the Ingress last — is
the advice a reader needs, and nothing at the pin contradicts any of it. Where the post is weak, it
is weak in its own printed output, not in its reasoning.

**Never absorbed.** The pin gained nothing from this release. The tool is named in two lines, both
in the annotation registry, both describing a value with no effect, and both older than this post —
[the 2023 census](../2023/README.md) found the same two. No page gained a migration walkthrough, no
reference page gained a row, the `gateway.md` migration section still ends with an off-site link,
and the output vocabulary the tool now emits at 1.0 is ten literals the tree has never written.
There is a reason: the tool is a SIG Network subproject and not part of a Kubernetes release, so
there is no release note to hang documentation on. It is still a gap, because the documentation is
where the post's readers were sent by the retirement announcement, and the documentation does not
know the tool reached 1.0.

**Overtaken by stasis.** `ingress.md` is the page the whole migration passes through and it has not
been re-read end to end since Gateway was recommended at the top of it. The note at `:25-26` was
added; the *Alternatives* section at `:638-643` was not touched, and still offers
`Service.Type=LoadBalancer` and `Service.Type=NodePort` as the ways to expose a Service without
Ingress; the what's-next at `:645-648` still points at the Ingress API reference and the Ingress
controller list. Nothing on that page became false. The page simply grew a new first paragraph and
kept an old last one, and a reader who reaches the bottom is told less than a reader who stops at
the top.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180`, 4096MB, 4
CPUs, 25G, [provisioned](../../strands/lab-topologies.md#provision) and
[baselined](../../strands/lab-topologies.md#node-baseline-steps) as usual, running Kubernetes v1.35.
One node is enough and a second would add nothing: the only cluster interaction in the whole
exercise is creating and reading objects through the apiserver, and the tool that does the work runs
on the node as an ordinary binary. No Ingress controller is installed and no Gateway API
implementation is installed, which is deliberate rather than a shortcut — the objects the tool reads
need no controller to exist, and the objects it writes have no kind to be written into. Everything
the exercise creates lives in a namespace called `bw-i2g`, except the Go toolchain installed in step
1 and the `ingress2gateway` binary installed in step 2, which *Teardown* removes. Steps 1 to 9 run
on the node over `ssh zain@10.10.10.180`; step 10 runs offline against a checkout of
`kubernetes/website` at the pin, with `W` set to its `content/en` directory.

**Do**

1. Establish what the cluster has, what it has not, and a Go toolchain. Open one session with `ssh
   zain@10.10.10.180` and stay in it; every fence up to step 10 is written as though you are already
   there. The two `api-resources` calls are the frame for the whole exercise: one API is present and
   the other is not.

   ```sh
   kubectl version -o json | grep gitVersion
   kubectl api-resources --api-group=networking.k8s.io
   kubectl api-resources --api-group=gateway.networking.k8s.io; echo "gateway group exit $?"
   kubectl get ingressclass -A
   kubectl create namespace bw-i2g
   sudo apt-get update -qq && sudo apt-get install -y golang-go openssl
   go version
   ```

2. Install the tool by the post's first path, at the post's exact version, and ask the binary what
   it thinks it is. The version question is the whole point of the step: the post prints
   `ingress2gateway-dev` into five manifests, and this is the binary those manifests were supposed
   to come from. If `version` is not a subcommand the command prints usage instead, which is also an
   answer; keep whatever it prints.

   ```sh
   go install github.com/kubernetes-sigs/ingress2gateway@v1.0.0
   export PATH="$PATH:$(go env GOPATH)/bin"
   command -v ingress2gateway
   ingress2gateway version 2>&1 | head -5
   ingress2gateway print --help 2>&1 | sed -n '1,40p'
   ingress2gateway print --help 2>&1 | grep -- '--emitter\|--providers' || echo "neither flag listed"
   ```

3. Put the post's Ingress into the cluster, with the two objects it references. The Service and the
   Secret exist so that the cluster-read path in step 5 sees a complete picture; nothing serves
   traffic and nothing needs to. The last line is a measurement in its own right — read what the
   apiserver stored against what you sent, and note that `ingressClassName: nginx` was accepted with
   no IngressClass of that name anywhere in the cluster.

   ```sh
   kubectl -n bw-i2g create service clusterip website-service --tcp=80:8080
   openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj /CN=my-host.example.com \
     -keyout /tmp/tls.key -out /tmp/tls.crt 2>/dev/null
   kubectl -n bw-i2g create secret tls my-secret --cert=/tmp/tls.crt --key=/tmp/tls.key
   cat > /tmp/my-ingress.yaml <<'EOF'
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     annotations:
       nginx.ingress.kubernetes.io/proxy-body-size: "1G"
       nginx.ingress.kubernetes.io/use-regex: "true"
       nginx.ingress.kubernetes.io/proxy-send-timeout: "1"
       nginx.ingress.kubernetes.io/proxy-read-timeout: "1"
       nginx.ingress.kubernetes.io/enable-cors: "true"
       nginx.ingress.kubernetes.io/configuration-snippet: |
         more_set_headers "Request-Id: $req_id";
     name: my-ingress
     namespace: bw-i2g
   spec:
     ingressClassName: nginx
     rules:
       - host: my-host.example.com
         http:
           paths:
             - backend:
                 service:
                   name: website-service
                   port:
                     number: 80
               path: /users/(\d+)
               pathType: ImplementationSpecific
     tls:
       - hosts:
           - my-host.example.com
         secretName: my-secret
   EOF
   kubectl apply -f /tmp/my-ingress.yaml
   kubectl -n bw-i2g get ingress my-ingress -o yaml | grep -v last-applied-configuration
   ```

4. Translate the file, and read the three values the post gets wrong or leaves unexplained. Send the
   two streams to separate files first, because which stream the notifications arrive on is itself
   worth knowing: if `warn-file.txt` is empty the blocks are on standard output, mixed into the
   manifest the post tells you to redirect straight into `gwapi.yaml`.

   ```sh
   ingress2gateway print --input-file /tmp/my-ingress.yaml --providers=ingress-nginx \
     > /tmp/gwapi-file.yaml 2> /tmp/warn-file.txt
   wc -l /tmp/gwapi-file.yaml /tmp/warn-file.txt
   head -3 /tmp/gwapi-file.yaml
   grep -n 'generator:' /tmp/gwapi-file.yaml
   grep -n '^kind:' /tmp/gwapi-file.yaml
   grep -n -A1 'timeouts:' /tmp/gwapi-file.yaml
   grep -n -A2 '      path:' /tmp/gwapi-file.yaml
   ```

5. Translate the same Ingress again, this time out of the cluster, and diff the two results. The
   post gives three ways to run the tool and says nothing about whether they agree. The object the
   apiserver returns is not byte-identical to the file you sent — step 3 showed you the difference —
   so this asks whether that difference survives the translation.

   ```sh
   ingress2gateway print --namespace bw-i2g --providers=ingress-nginx \
     > /tmp/gwapi-ns.yaml 2> /tmp/warn-ns.txt
   diff /tmp/gwapi-file.yaml /tmp/gwapi-ns.yaml; echo "manifest diff exit $?"
   diff /tmp/warn-file.txt /tmp/warn-ns.txt; echo "notification diff exit $?"
   ingress2gateway print --all-namespaces --providers=ingress-nginx 2>/dev/null \
     | grep -c '^kind:'
   ```

6. Count the notifications and classify them. The post prints five blocks, four `WARN` and one
   `INFO`, from two sources, with four of the five naming an object. The last loop asks a different
   question: which of the six input annotations is named anywhere in the output at all.

   ```sh
   cat /tmp/warn-ns.txt
   grep -c 'WARN' /tmp/warn-ns.txt
   grep -c 'INFO' /tmp/warn-ns.txt
   grep -o 'source: [A-Z_-]*' /tmp/warn-ns.txt | sort | uniq -c
   grep -c 'object:' /tmp/warn-ns.txt
   for a in proxy-body-size use-regex proxy-send-timeout proxy-read-timeout \
            enable-cors configuration-snippet; do
     printf '%-22s %s\n' "$a" "$(grep -c "$a" /tmp/warn-ns.txt)"
   done
   ```

7. Find the grouping rule, by giving the tool a second Ingress. The first one produced a Gateway
   named after its IngressClass; the question is whether the Gateway count tracks Ingresses, hosts
   or classes. The second Ingress uses `pathType: Prefix` rather than `ImplementationSpecific`, so
   the last command also shows you what the tool does with a path type the API actually defines.

   ```sh
   cat > /tmp/other-ingress.yaml <<'EOF'
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: my-other-ingress
     namespace: bw-i2g
   spec:
     ingressClassName: nginx
     rules:
       - host: other.example.com
         http:
           paths:
             - backend:
                 service:
                   name: website-service
                   port:
                     number: 80
               path: /health
               pathType: Prefix
   EOF
   kubectl apply -f /tmp/other-ingress.yaml
   ingress2gateway print --namespace bw-i2g --providers=ingress-nginx \
     > /tmp/gwapi-two.yaml 2> /tmp/warn-two.txt
   grep -c '^kind: Gateway$' /tmp/gwapi-two.yaml
   grep -c '^kind: HTTPRoute$' /tmp/gwapi-two.yaml
   grep -c 'kind: GatewayClass' /tmp/gwapi-two.yaml
   grep -n '^  name:\|hostname' /tmp/gwapi-two.yaml
   grep -n -B1 -A2 '        type: ' /tmp/gwapi-two.yaml
   ```

8. Run the three emitters the post names and measure what each one adds. The post says an emitter
   *might* carry `proxy-body-size` as an implementation-specific extension; this counts the added
   lines and looks for the annotation by name. The `apiVersion` tally is the part that matters for
   step 10 — every API group that appears here is a group the tool expects you to have installed. If
   the flag is not recognised the loop prints a failure line per emitter, and that is the
   measurement.

   ```sh
   for e in agentgateway envoy-gateway kgateway; do
     ingress2gateway print --input-file /tmp/my-ingress.yaml --providers=ingress-nginx \
       --emitter "$e" > /tmp/gwapi-$e.yaml 2> /tmp/warn-$e.txt || echo "$e failed, exit $?"
   done
   for e in agentgateway envoy-gateway kgateway; do
     printf '%-14s added=%-4s removed=%s\n' "$e" \
       "$(diff /tmp/gwapi-file.yaml /tmp/gwapi-$e.yaml | grep -c '^>')" \
       "$(diff /tmp/gwapi-file.yaml /tmp/gwapi-$e.yaml | grep -c '^<')"
   done
   grep -h '^apiVersion:' /tmp/gwapi-file.yaml /tmp/gwapi-agentgateway.yaml \
     /tmp/gwapi-envoy-gateway.yaml /tmp/gwapi-kgateway.yaml | sort | uniq -c
   grep -hi 'body' /tmp/gwapi-agentgateway.yaml /tmp/gwapi-envoy-gateway.yaml \
     /tmp/gwapi-kgateway.yaml || echo "no emitter carried the body size"
   ```

9. Settle the timeout. One second went in and ten came out; either the tool ignores the annotation
   values or the post's printed output did not come from the input printed above it. Sweep five
   values through the same annotation pair and read what each produces, then split the pair so the
   two annotations disagree and see which one the single `timeouts.request` field follows.

   ```sh
   grep -E 'proxy-(send|read)-timeout' /tmp/my-ingress.yaml
   for t in 1 3 10 30 90; do
     sed "s/-timeout: \"1\"/-timeout: \"$t\"/g" /tmp/my-ingress.yaml > /tmp/mi-$t.yaml
     printf 'both annotations %-3s -> %s\n' "$t" \
       "$(ingress2gateway print --input-file /tmp/mi-$t.yaml --providers=ingress-nginx 2>/dev/null \
          | grep -A1 'timeouts:' | grep 'request:' | tr -d ' ')"
   done
   sed 's/proxy-read-timeout: "1"/proxy-read-timeout: "30"/' /tmp/my-ingress.yaml > /tmp/mi-split.yaml
   ingress2gateway print --input-file /tmp/mi-split.yaml --providers=ingress-nginx 2>/dev/null \
     | grep -A1 'timeouts:'
   ```

10. Leave the node. On a machine with a checkout of `kubernetes/website` at the pin, count what the
    documentation knows about any of this. The first block is the tool; the second is the ten
    literals the generated output uses that the tree does not; the third is the five it does, and
    where they live; the fourth is the section of `ingress.md` that never learned about its own
    first paragraph.

    ```sh
    cd /path/to/kubernetes/website/content/en
    W="$(pwd)"
    grep -rn --include='*.md' -F 'ingress2gateway' "$W/docs"
    for t in certificateRefs 'filters:' 'type: CORS' allowCredentials allowOrigins maxAge \
             RegularExpression 'timeouts:' requestRedirect statusCode; do
      printf '%-20s %s\n' "$t" "$(grep -rF --include='*.md' -o "$t" "$W/docs" | wc -l)"
    done
    for t in gatewayClassName 'listeners:' parentRefs backendRefs; do
      echo "== $t"
      grep -rn --include='*.md' -F "$t" "$W/docs" | sed "s|$W/docs/||"
    done
    sed -n '25,26p;638,648p' "$W/docs/concepts/services-networking/ingress.md"
    sed -n '259,266p' "$W/docs/concepts/services-networking/gateway.md"
    grep -rc --include='*.md' -F 'ingress-nginx' "$W/docs" | grep -cv ':0$'
    grep -rl --include='*.md' -F 'nginx' "$W/docs" | wc -l
    ```

**Expect**

Step 1 draws the line the exercise sits on. `kubectl version` reports v1.35. The `networking.k8s.io`
group lists `ingressclasses` and `ingresses` at `v1`, alongside `networkpolicies` — the input API is
core, stable and installed. The `gateway.networking.k8s.io` query prints a header with nothing under
it and exits 0, so the output API is not merely uninstalled, it is indistinguishable from an empty
one as far as that command is concerned. `kubectl get ingressclass -A` reports no resources, which
matters later: the Ingress you are about to create names a class that does not exist and the
apiserver will not mind. The apt install pulls `golang-go` and `go version` reports whatever Debian
trixie ships, the same toolchain and the same non-answer as the [validating admission policy
walk](../2024/04-validating-admission-policy-ga.md).

Step 2 takes a minute or two, because `go install` at a tag fetches and compiles the module rather
than downloading a binary. `command -v` puts it at `~/go/bin/ingress2gateway`. Then the number: a Go
program that reads its own version from the module's build information will print `v1.0.0`, because
that is the tag you asked for; a Go program that carries a version string injected at link time will
print whatever the default of that variable is, and `dev` is the conventional default. The post's
five manifests say `ingress2gateway-dev`, which is the shape of the second case with the link-time
flag unset. So one of two things is true when you read this line, and both are worth having: the
binary agrees with the post, and the stamp is what the tool writes for everyone who installs it this
way; or the binary says `v1.0.0`, and the output printed in the post was made by a build that was
not the release. The `--help` output should list `--providers`; whether it lists `--emitter` decides
how step 8 reads.

Step 3 is uneventful on purpose, and the uneventfulness is the result. The Service and the Secret
are created, and the Ingress is accepted with no warning and no complaint about `ingressClassName:
nginx`, about a path of `/users/(\d+)`, or about six annotations for a controller that is not
installed. The round-trip adds what the apiserver always adds — `uid`, `resourceVersion`,
`generation`, `creationTimestamp`, `managedFields` and an empty `status.loadBalancer` — and changes
nothing you wrote. The annotations come back byte for byte, including the block scalar with the
`nginx` directive inside it. An Ingress at the pin is a document the apiserver stores and does not
interpret, which is why a translator can be a standalone program in the first place.

Step 4 gives you the three objects: one Gateway and two HTTPRoutes, `^kind:` matching three times,
`generator:` matching three times. Check which file the notification blocks landed in before
anything else. If `warn-file.txt` has the five blocks in it then the post's `> gwapi.yaml`
redirection at `:122` is safe and the blocks reach your terminal; if `warn-file.txt` is empty and
`head -3` shows a box-drawing character, then following the post literally puts the notifications
inside the manifest file. The path value should read `(?i)/users/(\d+).*`, matching `:207`. The
timeout is the number to write down and not yet interpret: the annotations said one second, and
whatever `request:` says here is the first half of step 9.

Step 5 should print two `exit 0` lines, and the exercise expects it to. The apiserver added five
fields to the Ingress in step 3 and none of them is input to the translation, so reading the object
out of the cluster and reading it out of the file give the same Gateway API and the same
notifications. That is worth confirming rather than assuming, because the three invocations at
`:120-126` are offered as interchangeable and the post never says they are. The `--all-namespaces`
count matches the namespace count at three, since `bw-i2g` holds the only Ingress on the cluster.

Step 6 reproduces the post's block structure: `WARN` four times, `INFO` once, `object:` four times,
and the source tally three `INGRESS-NGINX` to two `STANDARD_EMITTER`. The annotation loop is the
part that does not reproduce cleanly, and that is the finding. `configuration-snippet` and
`proxy-body-size` are named in full and match. `proxy-send-timeout` and `proxy-read-timeout` match
zero times each, because the message that concerns them writes the pair as
`proxy-{send,read}-timeout`, a brace expansion that is not the name of either annotation — so a
reader grepping the notifications for the annotation they are worried about finds nothing.
`use-regex` and `enable-cors` also match zero, but for the opposite reason: they translated, and
nothing reports a success.

Step 7 gives the grouping rule. One Gateway, still named `nginx`, now with three listeners: the two
for `my-host.example.com` on 80 and 443, and one for `other.example.com` on 80 with no TLS and
therefore no redirect partner. Three HTTPRoutes, because the first Ingress contributes its route and
its redirect and the second contributes one. Zero GatewayClass objects, as before. So the Gateway
count follows the IngressClass, the listener count follows host-and-protocol, and the HTTPRoute
count follows neither — two Ingresses became four objects that reference a class the output never
defines. The second Ingress's `Prefix` path comes out as `type: PathPrefix`, which is the one match
type the pinned documentation writes down, exactly once.

Step 8 has two possible shapes. If `--emitter` is accepted, each run should add lines rather than
remove them, the `apiVersion` tally grows a group that is not `gateway.networking.k8s.io`, and the
`body` grep tells you whether the annotation the post said an emitter *might* carry is actually
carried by any of the three. Take the new API groups to step 10 and count them there; the post
offers these emitters as the answer to untranslatable configuration, and the answer is a CRD from a
project the documentation does not name. If `--emitter` is rejected, you get three failure lines and
the three output files are empty, which says the flag documented in the note at `:130` is not in the
binary that `go install` at `v1.0.0` produces — a sharper version of the same finding.

Step 9 decides the timeout. If the five sweep lines read `request:1s`, `request:3s`, `request:10s`,
`request:30s` and `request:90s`, then the tool tracks the annotation faithfully and the ten seconds
at `:210` did not come from the one second at `:74-75` — the post printed output from an input it
did not print. If all five read `request:10s`, then the tool writes a constant and the post's prose
at `:271`, which attributes the ten to the annotations, is describing something the tool does not
do. The split run answers the smaller question underneath: two ingress-nginx timeouts map to one
Gateway API field, so the tool must pick, and whether it takes the larger, the read value, or the
send value is a behaviour no notification mentions and the post does not raise.

Step 10 is the pin's side of it. The first grep returns exactly two lines, both from
`labels-annotations-taints/_index.md`, one an example value and one a sentence saying the value has
no effect. The ten-literal loop prints `0` ten times. The five-literal loop prints
`gatewayClassName` once and `listeners:` once, both from `gateway.md`, and `parentRefs` and
`backendRefs` three times each, all from `gateway.md` — so every Gateway API field name the
documentation contains is on one page. The two `sed` extracts put the contradiction side by side:
`ingress.md` recommending Gateway at the top, `ingress.md` listing `LoadBalancer` and `NodePort` as
the alternatives at the bottom, and `gateway.md` saying the conversion is necessary and then linking
somewhere else to say how. The last two lines print `0` and `101`: no file under `content/en/docs`
mentions `ingress-nginx`, and 101 of them mention `nginx`.

**Read on**

11. [The Gateway API walk](../2021/02-evolving-kubernetes-networking-with-the-gateway-api.md), for
    why the apiserver has no kind to put this output into, and for the annotation registration this
    exercise reads the value of.

12. [The Ingress API walk](../2020/02-improvements-to-the-ingress-api-in-kubernetes-1-18.md), for
    the three path types, the `IngressClass` resource the Gateway takes its name from, and the
    annotation sprawl the whole migration exists to undo.

13. [The kind walk](02-experimenting-gateway-api-with-kind.md), for a cluster that does have the
    kinds, an implementation to apply them to, and a Gateway that gets an address — everything this
    exercise deliberately does without.

14. [The 1.2 Ingress
    walk](../2016/03-kubernetes-1-2-and-simplifying-advanced-networking-with-ingress.md), for what
    the resource looked like when it was new, which is the far end of the ten-year arc this post is
    trying to close.

15. Unanswerable from the pin: where the ten seconds came from. Step 9 can tell you whether the tool
    produces ten seconds from an input of one, and that settles whether the number is the tool's or
    the author's. What it cannot tell you is which — the post links no repository revision, the
    generated output is pasted rather than generated by the site, and the pinned tree has no copy of
    the tool at any version. The node can reproduce the translation. It cannot reproduce the paste.

**Teardown**

The namespace takes the Ingresses, the Service and the Secret. The Go toolchain and the built binary
are outside it, and so are the dozen files in `/tmp`; remove all three, because a stray
`ingress2gateway` on the node would quietly answer a later exercise's version question with this
one's build.

```sh
ssh zain@10.10.10.180 "kubectl delete namespace bw-i2g --wait; \
  rm -rf ~/go /tmp/gwapi-*.yaml /tmp/warn-*.txt /tmp/mi-*.yaml; \
  rm -f /tmp/my-ingress.yaml /tmp/other-ingress.yaml /tmp/tls.key /tmp/tls.crt; \
  sudo apt-get remove -y golang-go && sudo apt-get autoremove -y"
```
