<a id="kubernetes-supports-openapi"></a>
# The endpoint this post tells you to fetch has moved twice, an authorization page still tells you to permit the version before the one this post announced, and the section describing the version that replaced it wears a badge from a switch that no longer exists

**Post** — [Kubernetes supports OpenAPI](https://kubernetes.io/blog/2016/12/kubernetes-supports-openapi/),
2016-12-23, Kubernetes v1.5 — Mehdy Bohlool of Google, the last instalment of *Five Days of
Kubernetes 1.5* and the last `walk` verdict of 2016. It is a good place to end the year, because it
is the only post in the fifteen whose subject is the machine-readable description of everything the
other fourteen talk about.

**As written** — the post announces a completion, not a beginning:

> Kubernetes has supported swagger 1.2 (older version of OpenAPI spec) for a while, but the spec was
> incomplete and invalid, making it hard to generate tools/clients based on it.

v1.4 added alpha support for what the post carefully calls *"the OpenAPI spec (formerly known as
swagger 2.0 before it was donated to the Open API Initiative)"*, and v1.5 finishes the job:

> the support for the OpenAPI spec has been completed by auto-generating the spec directly from
> Kubernetes source, which will keep the spec--and documentation--completely in sync with future
> changes in operations/models.

Two consequences are claimed. One is a client: *"we have even introduced a supported python
client"*, linked to `github.com/kubernetes-incubator/client-python`. The other is a design
statement that turns out to be the most durable sentence in the post:

> The spec is modular, divided by GroupVersion: this is future-proof, since we intend to allow
> separate GroupVersions to be served out of separate API servers.

The body is one worked example, quoted at length: the OpenAPI fragment for reading a Pod. It prints
the path `/api/v1/namespaces/{namespace}/pods/{name}`, the `operationId`
`readCoreV1NamespacedPod`, a `tags` list of `core_v1`, three `produces` media types
(`application/json`, `application/yaml`, `application/vnd.kubernetes.protobuf`), a `$ref` of
`#/definitions/v1.Pod`, and exactly two query parameters:

```
      {
       "uniqueItems": true,
       "type": "boolean",
       "description": "Should the export be exact.  Exact export maintains cluster-specific fields like 'Namespace'.",
       "name": "exact",
       "in": "query"
      },
      {
       "uniqueItems": true,
       "type": "boolean",
       "description": "Should this value be exported.  Export strips fields that a user can not specify.",
       "name": "export",
       "in": "query"
      }
```

Then the same operation as swagger-codegen would render it, and the same operation as the Python
client calls it. And then the sentence this exercise is built on:

> There are two ways to access OpenAPI spec:
>
> - From `kuber-apiserver`/swagger.json. This file will have all enabled GroupVersions routes and
>   models and would be most up-to-date file with an specific `kube-apiserver`.
> - From Kubernetes GitHub repository with all core GroupVersions enabled. You can access it on
>   [master](https://github.com/kubernetes/kubernetes/blob/master/api/openapi-spec/swagger.json) or
>   an specific release (for example
>   [1.5 release](https://github.com/kubernetes/kubernetes/blob/release-1.5/api/openapi-spec/swagger.json)).

The post closes by pointing at `swagger.io` tooling and telling you the generated clients *"will
mostly work out of the box--but you will need some support for authorization and some Kubernetes
specific utilities."*

**As it runs now** — the corpus documents three endpoints across the history the post describes, and
they are the exercise's three rungs.

The first rung is swagger 1.2, which the post is explicitly replacing. Its path appears exactly once
at the pin, and not as history:

> When using ABAC authorization, those special resources have to be explicitly exposed via the
> `nonResourcePath` property in a policy [...]
>
> * `/api`, `/api/*`, `/apis`, and `/apis/*` for API version negotiation.
> * `/version` for retrieving the server version via `kubectl version`.
> * `/swaggerapi/*` for create/update operations.
>
> — `docs/reference/access-authn-authz/abac.md:97-100`

That is a live instruction on a live reference page, telling a reader to permit a path for
create/update operations. Seven lines above it, the same page says where those operations actually
get their schema:

> Kubectl uses the `/api` and `/apis` endpoints of apiserver to discover served resource types, and
> validates objects sent to the API by create/update operations using schema information located at
> `/openapi/v2`.
>
> — `docs/reference/access-authn-authz/abac.md:91-93`

One page, one paragraph apart, naming two different endpoints for the same purpose. The prose is
current and the copy-into-your-policy list is not, which is the wrong way round: the list is the part
a reader executes.

The second rung is the post's own — OpenAPI v2 — and it is no longer at either address the post
gives. `/openapi/v2` is what the pin documents, in three places (`kubernetes-api.md:161`,
`abac.md:93`, and `webhook.md:209`, where it appears in the default list of non-resource paths a
webhook authorizer is not consulted about). The string `swagger.json` occurs three times under
`docs/`, and every one of them is the *file in the kubernetes/kubernetes repository* —
`api/openapi-spec/swagger.json`, the post's **second** access route. The post's **first** access
route, an apiserver serving the spec at `/swagger.json`, is documented nowhere at the pin, at that
path or any other. Note also that the post misspells the binary in the sentence that gives it:
*"From `kuber-apiserver`/swagger.json"*.

The third rung is the one the post could not have named, and the pin prefers it:

> Kubernetes serves both OpenAPI v2.0 and OpenAPI v3.0. OpenAPI v3 is the preferred method of
> accessing the OpenAPI because it offers a more comprehensive (lossless) representation of
> Kubernetes resources. Due to limitations of OpenAPI version 2, certain fields are dropped from
> the published OpenAPI including but not limited to `default`, `nullable`, `oneOf`.
>
> — `docs/concepts/overview/kubernetes-api.md:151-156`

And it is served the way the post said the spec was already structured — *"modular, divided by
GroupVersion"* — except that this time the modularity is in the transport rather than in the tags:

> A discovery endpoint `/openapi/v3` is provided to see a list of all group/versions available. [...]
> The relative URLs are pointing to immutable OpenAPI descriptions, in order to improve client-side
> caching. The proper HTTP caching headers are also set by the API server for that purpose
> (`Expires` to 1 year in the future, and `Cache-Control` to `immutable`). When an obsolete URL is
> used, the API server returns a redirect to the newest URL.
>
> — `docs/concepts/overview/kubernetes-api.md:208-232`

Each group version has its own document at `/openapi/v3/apis/<group>/<version>?hash=<hash>`. The
post's v2 spec used `tags` to *label* which GroupVersion an operation belonged to inside one
document; v3 gives each GroupVersion a document of its own, with a content hash in the URL. The
prediction in the post's most confident sentence came true one rung later than the rung it was
written about.

Three smaller things, each checkable.

The two query parameters the post prints are both gone. `exact` and `export`, as query parameters
on a read, have zero occurrences at the pin — not in `api-concepts.md`, not in the deprecation
guide, not anywhere under `docs/`. The post's single worked example, the one fragment it quotes in
full, describes an operation whose complete parameter list has since been emptied of everything it
showed.

The three `produces` media types have not moved at all — and that is worth noticing precisely
because a fourth arrived somewhere else:

> Over HTTP, Kubernetes supports JSON, YAML, CBOR and Protobuf wire encodings.
>
> — `docs/reference/using-api/api-concepts.md:140`

Meanwhile the apiserver's `--storage-media-type` flag still advertises exactly the post's three:
*"Supported media types: [application/json, application/yaml, application/vnd.kubernetes.protobuf]"*
(`kube-apiserver.md:1133`). The post's list survives verbatim as the *storage* options while the
wire grew a fourth encoding the storage layer does not take.

The Python client moved organisation and repository. `kubernetes-incubator` and `client-python`
both have zero occurrences at the pin; the officially supported client is
`github.com/kubernetes-client/python` (`client-libraries.md:40`), and the same page lists eight
further community-maintained Python clients beneath it. The post's *"a supported python client"* is
now one supported client among nine.

Now the two dead pointers, which sit on the same page and fail in opposite directions.

Line 147 of `kubernetes-api.md`, immediately above `## OpenAPI interface definition`, is a bare
compatibility anchor:

```html
<a id="#api-specification" />
```

The `id` attribute begins with `#`. An HTML fragment is written `#value`, so an `id` of
`#api-specification` is only reachable by the fragment `##api-specification`, which nothing writes.
Grep the corpus for `api-specification` and every other hit is a substring of the
`OAI/OpenAPI-Specification` GitHub URL. So the anchor is malformed *and* has no referrer — it is
guarding a link nobody follows.

Two files away, two links do want an anchor on that page and there isn't one:

- `docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions.md:1527` —
  `[OpenAPI v3](/docs/concepts/overview/kubernetes-api/#openapi-and-swagger-definitions)`
- `docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions.md:1540` —
  `[OpenAPI v2 spec](/docs/concepts/overview/kubernetes-api/#openapi-and-swagger-definitions)`

The headings on the target page are *OpenAPI interface definition*, *OpenAPI V2* and *OpenAPI V3*.
There is no `openapi-and-swagger-definitions` heading and no explicit anchor supplying one — the
two occurrences above are the *only* occurrences of that string in the whole content tree. Both
links land on the page and then stay at the top of it.

Finally, the badge. The *OpenAPI V3* section opens with

```
{{< feature-state feature_gate_name="OpenAPIV3" >}}
```

and `docs/reference/command-line-tools-reference/feature-gates/OpenAPIV3.md` carries `removed: true`
along with `_build: {list: never, render: false}` — a gate file the site is instructed not to render
and not to list, still driving a state badge on a section of a concept page.

**The diff, and why** — the post is a report on a documentation project, so what happened to it is
unusually legible: the thing it built is still there, working, and doing more than it promised, while
every *address* it printed has moved. Splitting those two halves is the whole reading.

The durable half is the generation. *"Auto-generating the spec directly from Kubernetes source"* is
the sentence that made everything after it possible, and it is the reason the pin's reference
documentation exists in the form it does. Once the spec is derived rather than written, it cannot
drift from the server; and once it cannot drift, tools can be generated from it, which is why
`client-libraries.md` lists thirteen supported clients rather than one hand-written Go library. That
mechanism has never been reversed. It is also why the post's design sentence about GroupVersions
came true: a derived spec can be re-partitioned without anyone rewriting it, so moving from
tag-labelled sections in one document to a document per group version was a change of publication
strategy, not of content.

The volatile half is the addressing, and the reason it churned is the same reason the generation
held. A generated spec is *reachable*, and things that are reachable acquire callers, and callers
force compatibility decisions. `/swaggerapi/` served a spec nobody could generate from, so it could
be dropped. `/swagger.json` served the good spec at a name inherited from the tool the format was
donated away from, so the name was corrected. `/openapi/v2` serves a spec that the format itself
cannot fully express — the pin says so explicitly, listing `default`, `nullable` and `oneOf` as
casualties — so a third endpoint was added rather than the second being changed, because changing
it would have broken the callers the second endpoint had already earned. Each move was cheap for the
project and expensive for exactly one class of reader: whoever wrote the path down.

Which brings the two failures on the pin's own pages into focus, because they are the *same* failure
as the post's, arriving later. `abac.md` names `/openapi/v2` in its prose because someone updating
the prose read the current concept page; it still names `/swaggerapi/*` in its list because a
bulleted path in a policy example is not a link and nothing checks it. The two links to
`#openapi-and-swagger-definitions` are dead because a heading was renamed on one page and the
fragment that pointed at it lived on another, and a fragment that misses does not error — the browser
simply lands at the top and the reader assumes they were meant to skim. And `<a id="#api-specification" />`
is what happens when someone anticipates that problem and mistypes the fix. Three variations on one
theme: **the corpus checks its own links and not its own fragments, and it checks neither the paths
inside its examples.** [14](14-statefulset-run-scale-stateful-applications-in-kubernetes.md) found
the prose-only version of this in a tutorial sentence naming a deleted object; here the same gap has
produced a live authorization instruction for an endpoint that answers nothing.

The badge is the one failure of a different kind, and it is worth separating. `OpenAPIV3` being
`removed: true` is *correct*: the gate is gone, because publishing OpenAPI v3 is now
unconditional. The section is also correct: v3 is served and preferred. What is wrong is only that
the section still asks a removed gate to describe its maturity — so the most current rung of the
three is annotated by the one mechanism in this exercise that has genuinely finished its life. Read
the rendered page and decide for yourself whether the badge helps or misleads; the exercise's last
step asks you to.

The post's own closing caveat has aged into a warning worth keeping. *"The clients this generates
will mostly work out of the box--but you will need some support for authorization and some
Kubernetes specific utilities."* The pin says the same thing about the schema itself, in a warning
box directly beneath the v2 table:

> The validation rules published as part of OpenAPI schemas may not be complete, and usually aren't.
> Additional validation occurs within the API server. If you want precise and complete verification,
> a `kubectl apply --dry-run=server` runs all the applicable validation (and also activates
> admission-time checks).
>
> — `docs/concepts/overview/kubernetes-api.md:194-199`

Ten years apart, the same shape of admission: the published description is nearly the server and
never quite the server. [05](05-configuration-management-with-containers.md) hit the consequence
from the other end, where the API accepted a manifest a client-side check would once have rejected.
The spec is the best available account of the server and it is not the server, and the command that
closes that gap is in the warning above.

**The ladder** — four gates, tracing what happened to the endpoint the post announced and to what is
published through it.

The rung the pin prefers, and the gate that used to control it:

## OpenAPIV3
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.23 – v1.23 |
| beta | `true` | — | v1.24 – v1.26 |
| stable | `true` | — | v1.27 – v1.28 |

`removed: true` at file level. A complete ladder, walked in five releases and retired two after
reaching stable — and the gate file, marked removed and set `render: false`, is the one the *OpenAPI
V3* section still names in its `feature-state` shortcode.

What v3 can carry that v2 dropped, in part:

## OpenAPIEnums
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.23 – v1.23 |
| beta | `true` | — | v1.24 –  |

Beta and on since v1.24, and beta *still* — thirteen releases without promotion, alongside a gate
that entered at the same release and finished its whole life. The pin's list of what OpenAPI v2
drops (`default`, `nullable`, `oneOf`) does not mention `enum`; this gate populates it, and its being
on by default for thirteen releases is why a reader can rely on enums appearing without checking
whether anybody enabled anything.

The post's *"auto-generating the spec directly from Kubernetes source"* extended to types the source
does not contain:

## CustomResourcePublishOpenAPI
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.14 – v1.14 |
| beta | `true` | — | v1.15 – v1.15 |
| stable | `true` | — | v1.16 – v1.18 |

`removed: true` at file level. One release per stage — the fastest ladder in this year's fifteen
exercises — and it is the reason the post's claim survives a reader defining their own kinds: a
CustomResourceDefinition's schema is published into the same spec as a Pod's.

And the encoding that arrived after the post's three:

## CBORServingAndStorage
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.32 –  |

Alpha and off, six releases in. This is why `api-concepts.md:140` can name four wire encodings while
the post's three `produces` values are still the complete set on a default cluster — the fourth is
real, documented, and switched off.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), fresh. One node is enough: every step
here talks to one API server and nothing is scheduled. Bring the guest up with
[the five provision steps](../../strands/lab-topologies.md#provision), install Kubernetes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), and confirm the
single node is Ready.

Run `kubectl proxy --port=8001 &` on the node and use `curl` against `127.0.0.1:8001` throughout, so
the steps below are reading exactly what a generated client would read. `jq` is on the node from the
baseline.

**Do**

1. Try all three rungs at their documented and undocumented addresses, and record the status codes
   before reading anything:

   ```sh
   for p in /swaggerapi/ /swaggerapi/api/v1 /swagger.json /swagger-2.0.0.json /openapi/v2 /openapi/v3; do
     printf '%-24s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' 127.0.0.1:8001$p)"
   done
   ```

   Three of those six are the post's and the ABAC page's. Write down which addresses answer and
   which do not, then read `docs/reference/access-authn-authz/abac.md:91-100` and say which of the
   two endpoints that page names would actually need permitting on this cluster.

2. Confirm the post's example operation still exists, by the identifier it printed:

   ```sh
   curl -s 127.0.0.1:8001/openapi/v2 \
     | jq '.paths["/api/v1/namespaces/{namespace}/pods/{name}"].get
           | {operationId, tags, produces, ref: .responses["200"].schema}'
   ```

   Compare every field against the post's fragment. The `operationId` and `tags` should match a
   ten-year-old blog post character for character. Say what that tells you about the naming scheme
   the post described, and whether anything in the corpus promises it.

3. Now the parameters, which is where the example has emptied out:

   ```sh
   curl -s 127.0.0.1:8001/openapi/v2 \
     | jq -r '.paths["/api/v1/namespaces/{namespace}/pods/{name}"].get.parameters[]?
              | "\(.name)\t\(.in)\t\(.type)"'
   curl -s -o /dev/null -w '%{http_code}\n' \
     "127.0.0.1:8001/api/v1/namespaces/default/pods?export=true&exact=true"
   ```

   Neither `exact` nor `export` should be in the list. The second command sends them anyway. Report
   the status code and then get the server to tell you what it did with them:

   ```sh
   kubectl get pods --v=8 2>&1 | grep -i "GET http" | head -1
   ```

   State whether an unrecognised query parameter on a read is rejected or ignored, and which of
   those two answers makes the missing parameters in step 3's list a *documentation* fact rather
   than a *compatibility* fact.

4. Fetch the v3 discovery document and see the post's design sentence realised:

   ```sh
   curl -s 127.0.0.1:8001/openapi/v3 | jq '.paths | keys | length'
   curl -s 127.0.0.1:8001/openapi/v3 | jq -r '.paths["api/v1"].serverRelativeURL'
   ```

   That is one document per GroupVersion, exactly as the post said the spec was *"modular, divided
   by GroupVersion"*. Say what v2 uses to express the same division inside its single document —
   step 2 already printed it — and which of the two a client that wants only `api/v1` would rather
   have.

5. Test the immutability claim from `kubernetes-api.md:224-232`, which is the reason the hash is in
   the URL:

   ```sh
   U=$(curl -s 127.0.0.1:8001/openapi/v3 | jq -r '.paths["api/v1"].serverRelativeURL')
   curl -s -D - -o /dev/null "127.0.0.1:8001$U" | grep -iE "^(expires|cache-control|etag)"
   curl -s -o /dev/null -w 'stale hash -> %{http_code}\n' "127.0.0.1:8001/openapi/v3/api/v1?hash=deadbeef"
   curl -s -L -o /dev/null -w 'following -> %{http_code} %{url_effective}\n' \
     "127.0.0.1:8001/openapi/v3/api/v1?hash=deadbeef"
   ```

   The page promises a one-year `Expires`, `Cache-Control: immutable`, and a redirect on an obsolete
   URL. Check all three against what came back, and say which of them the page's wording would let
   you predict wrongly.

6. Prove the pin's own claim about what v2 loses, using a field the post's format cannot express:

   ```sh
   curl -s 127.0.0.1:8001/openapi/v2 | grep -c '"oneOf"'
   curl -s "127.0.0.1:8001$U" | grep -c '"oneOf"'
   curl -s "127.0.0.1:8001$U" \
     | jq '.components.schemas["io.k8s.api.core.v1.PodSpec"].properties.restartPolicy'
   curl -s 127.0.0.1:8001/openapi/v2 \
     | jq '.definitions["io.k8s.api.core.v1.PodSpec"].properties.restartPolicy'
   ```

   Note that the `$ref` root changed between the two — `definitions` in the post's format,
   `components.schemas` in v3 — which is why step 2's `$ref` value is not portable between rungs.
   Then compare the two `restartPolicy` schemas and say which of `default`, `nullable`, `oneOf` and
   `enum` each rung gives you, and match that against the two gates in the ladder above.

7. Find out which rung `kubectl explain` is reading, since that is the spec most readers consume
   without ever fetching it:

   ```sh
   kubectl explain pod.spec.restartPolicy
   kubectl explain --v=8 pod.spec.restartPolicy 2>&1 | grep -i "GET http" | head -3
   ```

   The second command names the endpoint. Say whether the human-readable output includes anything
   the rung it fetched can carry and the other rung cannot, and check your answer against step 6.

8. Extend the post's generation claim to a type the Kubernetes source does not contain:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: apiextensions.k8s.io/v1
   kind: CustomResourceDefinition
   metadata: { name: walks.blogwalk.example }
   spec:
     group: blogwalk.example
     scope: Namespaced
     names: { plural: walks, singular: walk, kind: Walk }
     versions:
       - name: v1
         served: true
         storage: true
         schema:
           openAPIV3Schema:
             type: object
             properties:
               spec:
                 type: object
                 properties:
                   verdict:
                     type: string
                     enum: ["walk", "read", "dated", "skip"]
                     default: "walk"
                   year:
                     type: integer
                     nullable: true
   EOF
   sleep 5
   curl -s 127.0.0.1:8001/openapi/v3 | jq -r '.paths | keys[] | select(test("blogwalk"))'
   ```

   The group version appears in the discovery document without anyone regenerating anything. That is
   `CustomResourcePublishOpenAPI` from the ladder, and it is the post's *"auto-generating the spec
   directly from Kubernetes source"* applied to a schema you wrote thirty seconds ago.

9. Now ask both rungs to describe your own type, and see the loss the pin warned about happen to
   fields you chose deliberately:

   ```sh
   V=$(curl -s 127.0.0.1:8001/openapi/v3 | jq -r '.paths["apis/blogwalk.example/v1"].serverRelativeURL')
   curl -s "127.0.0.1:8001$V" \
     | jq '.components.schemas | to_entries[] | select(.key|test("Walk$")) | .value.properties.spec.properties'
   curl -s 127.0.0.1:8001/openapi/v2 \
     | jq '.definitions | to_entries[] | select(.key|test("Walk$")) | .value.properties.spec.properties'
   ```

   You put an `enum`, a `default` and a `nullable` into that CRD. Report which of the three each rung
   published, then test whether the ones v2 dropped are still *enforced*:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: blogwalk.example/v1
   kind: Walk
   metadata: { name: bad }
   spec: { verdict: "sprint" }
   EOF
   kubectl create -f - <<'EOF'
   apiVersion: blogwalk.example/v1
   kind: Walk
   metadata: { name: good }
   spec: { year: 2016 }
   EOF
   kubectl get walk good -o jsonpath='{.spec}{"\n"}'
   ```

   One is rejected and one gains a field nobody set. State where each of those two behaviours is
   implemented, and why a client generated from the v2 spec would have predicted neither.

10. Close on the two documentation defects, which need no cluster at all — only the rendered site and
    the pinned source. Open
    [the API concept page](https://kubernetes.io/docs/concepts/overview/kubernetes-api/) and
    [the CRD page's structural-schema section](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/),
    then answer three questions in your notes:

    - Follow the CRD page's two links to `#openapi-and-swagger-definitions`. Where does the browser
      put you, and how would a reader who did not check the address bar describe what happened?
    - The anchor at `kubernetes-api.md:147` is `<a id="#api-specification" />`. Write the fragment
      that would reach it, and say whether the CRD page's links would have worked if the anchor had
      been written without the leading `#`.
    - The *OpenAPI V3* section's badge is driven by `OpenAPIV3`, a gate file marked `removed: true`.
      Read what the badge actually renders on the live page, compare it to the ladder above, and
      decide whether a reader arriving at that section learns something true from it.

    All three are one-line fixes upstream. Say which of the three would mislead a reader into doing
    the wrong thing, and which merely waste their time — the difference is the same one step 1 found
    on the ABAC page.

**Expect**

```sh
curl -s -o /dev/null -w 'v2 %{http_code}\n' 127.0.0.1:8001/openapi/v2
curl -s -o /dev/null -w 'v3 %{http_code}\n' 127.0.0.1:8001/openapi/v3
curl -s -o /dev/null -w 'swaggerapi %{http_code}\n' 127.0.0.1:8001/swaggerapi/
curl -s -o /dev/null -w 'swagger.json %{http_code}\n' 127.0.0.1:8001/swagger.json
curl -s 127.0.0.1:8001/openapi/v3 | jq -r '.paths | keys[] | select(test("blogwalk"))'
kubectl get walk good -o jsonpath='{.spec.verdict}{"\n"}'
```

Two endpoints answering, two not, your own group version in the discovery document, and a `verdict`
of `walk` on an object whose manifest did not set one.

By the end you should be able to name which rung each of the post's two access routes has become,
say what the v2 spec cannot tell a generated client about your own CRD, and point at the one line on
the pin's ABAC page that would send a reader to an endpoint that answers nothing.

**Read on** — the pin's
[api-concepts page on resource encoding](https://kubernetes.io/docs/reference/using-api/api-concepts/#alternate-representations-of-resources)
covers the wire formats this exercise only counted. Read it against the post's three `produces`
values and answer: for which of the four encodings the page names does the OpenAPI spec you fetched
in step 2 *not* list a media type, and does the spec's silence mean the server would refuse it?

**Teardown** — `kubectl delete crd walks.blogwalk.example`, then stop the proxy
(`kill %1`), then [the teardown step](../../strands/lab-topologies.md#teardown).
