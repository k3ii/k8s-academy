<a id="warnings"></a>

# Four pages of the pinned documentation cite this post as their own reference for what a warning is, three of them reviewed by its author, and the half of it no page absorbed — the client handler, the deduplication, the metrics recipe — survives nowhere in the tree except the post

**Post** — [Warning: Helpful Warnings Ahead](https://kubernetes.io/blog/2020/09/03/warnings/), 3
September 2020, by Jordan Liggitt (Google). 330 lines, eighteen fenced blocks and two screenshots
included as raw `<img>` tags whose alt text spells out what each terminal shows, which is the only
reason the worked example can be quoted here at all. It introduces the `Warning` response header in
Kubernetes 1.19: what sends one, what a client does with one, and how to send your own from a
webhook or a CustomResourceDefinition.

Most walks in this archive measure a post against the pin and find the post has aged. This one ages
differently. The mechanism is entirely intact — every field, flag and header the post describes
still exists at v1.37 — and the post itself has been absorbed into the reference documentation as a
citation, linked by four pages that do not restate what it says. The interesting question is
therefore not what broke. It is which half of the post the documentation took and which half it
left.

**As written**

**The mechanism is one header, and the post is careful about what it does not do.** A `Warning`
header as defined by [RFC7234, Section 5.5](https://tools.ietf.org/html/rfc7234#section-5.5), added
to an API response, `so it does not change the status code or response body in any way`. The post
links its own KEP — `keps/sig-api-machinery/1693-warnings` — and states the client support boundary:
warnings are surfaced by `kubectl` v1.19+ in `stderr` output, and by the `k8s.io/client-go` client
library v0.19.0+ in log output.

**Deprecated APIs get three signals, not one.** The post's first section gives a request to a
deprecated REST endpoint three consequences: a `Warning` header in the response, an audit annotation
`"k8s.io/deprecated":"true"` on the audit event, and an `apiserver_requested_deprecated_apis` gauge
set to `1` in the kube-apiserver, broken out by group, version, resource, subresource and
`removed_release`. It closes the metrics section with a PromQL join that puts the request rate
beside the deprecation, so that an operator can see not just that a deprecated API is in use but how
much.

**The worked example is a screenshot of an Ingress.** The post shows `kubectl apply` printing
`networking.k8s.io/v1beta1 Ingress is deprecated in v1.19+, unavailable in v1.22+; use
networking.k8s.io/v1 Ingress`. That one line is the whole demonstration: the deprecated request
succeeded, and the operator was told.

**Anyone can send a warning, and the post shows two ways.** A CustomResourceDefinition can mark a
version `deprecated: true` and optionally override the message with `deprecationWarning`. An
admission webhook can return a `warnings` list on its admission response — the post's example is
`".spec.memory: requests >1GB do not work on Fridays"` — and the post gives three rules for writing
one: do not include a `Warning:` prefix, because the client adds that on output; describe a problem
the requesting client should correct or be aware of; and `Be brief; limit warnings to 120 characters
if possible`.

**Clients can turn warnings up or off, and the post shows the Go for both.** A caller can install a
handler that writes to stderr with deduplication and colour — `rest.NewWarningWriter(os.Stderr,
rest.WarningWriterOptions{Deduplicate: true, Color: term.AllowsColorOutput(os.Stderr)})` — or
suppress them entirely with `config.WarningHandler = rest.NoWarnings{}`. And `kubectl` grew
`--warnings-as-errors` in v1.19, shown in the post's second screenshot `displaying a warning message
and exiting with a non-zero exit code`: treat a warning as a failure and exit non-zero.

**The post ends with four ideas and calls two of them future possibilities.** Under `Future
Possibilities` it names warning about known problematic values, linking a Kubernetes issue comment,
and warning about deprecated fields or field values, `(like selectors using beta os/arch node
labels, [deprecated in v1.14])`. Two more ideas appear a section earlier, offered to webhook
authors: a `complain` mode that returns warnings instead of rejections, and `lint` or `vet`-style
webhooks that never reject anything at all.

**As it runs now**

**The header is still there and so is every field.** At the pin,
`reference/using-api/deprecation-policy.md:288-303` states the same three consequences in the same
order, with the same RFC link and the same audit annotation string, and gives the same PromQL join
at `:301`. `reference/kubernetes-api/apiextensions/custom-resource-definition-v1.md:303-308`
documents `deprecated` and `deprecationWarning` unchanged.
`reference/access-authn-authz/extensible-admission-controllers.md:555-567` documents the webhook
`warnings` list. Nothing in the post's description of the mechanism has to be corrected.

**Four pages cite the post, and none of them re-explains it.**
`reference/using-api/api-concepts.md:1242` links it by its full title as the definition of what a
warning is. `reference/using-api/deprecation-guide.md:392` links it, uniquely in the tree, at a
fragment anchor — `#deprecation-warnings` — as the how-to for locating deprecated API use.
`reference/access-authn-authz/validating-admission-policy.md:100` and
`tutorials/cluster-management/admission-policies.md:107` both link it for what the word `warning`
means when a policy's action is `Warn`. Those are the only four citations of this post in
`content/en/docs`, and they are load-bearing: remove the post and four pages lose their definition
of their own term.

**Measure that against the tree and it is unusual.** Eight distinct blog URLs, covering seven posts,
appear under `docs/reference/`; two of them are this post, the bare URL and the anchored one. Three
files under `docs/reference/` cite it, and every other post cited from `docs/reference/` is cited by
exactly one file. Across the whole `docs/` tree thirty-two distinct posts are linked, and this post
is linked from four files — tied for the most-cited post in the documentation with the announcement
of the `pkgs.k8s.io` package repositories.

**The author reviews the pages that absorbed the post.** `liggitt` is a listed reviewer of
`api-concepts.md`, `deprecation-guide.md`, `validating-admission-policy.md`,
`custom-resource-definition-versioning.md` and `extensible-admission-controllers.md` — five of the
six pages carrying this material, including all three under `docs/reference/` that cite the post.
The two exceptions are informative: `deprecation-policy.md`, the page that states the mechanism most
completely, lists `bgrant0607`, `lavalamp` and `thockin` and does not cite the post at all; and the
tutorial that does cite it carries no reviewers block.

**The worked example no longer works, because the deprecation it demonstrates completed.**
`reference/using-api/deprecation-guide.md:257-269` records that `networking.k8s.io/v1beta1` Ingress
is no longer served as of v1.22, along with the field renames and the now-required `pathType`. The
screenshot's warning said `unavailable in v1.22+`, and the pin is v1.37. Applying the post's own
example at the pin does not produce the post's own output; it produces a refusal. The demonstration
was overtaken by the thing it was demonstrating.

**The `complain` mode from the throwaway list is now a field in a stable API.**
`validating-admission-policy.md:98-101` gives `validationActions` three values, of which `Warn` is
`Validation failure is reported to the request client as a warning` — with `warning` linking to this
post. The page is `stable` from v1.30 (`:12`), and `:110` records that `Deny` and `Warn` may not be
used together. What the post offered webhook authors as an idea to get started with arrived as a
first-class enum value on a different API, and the page that carries it points back at the post for
its vocabulary.

**The other future possibility did not arrive, and the pin still shows the exact case the post
named.** `reference/labels-annotations-taints/_index.md:819-829` lists `beta.kubernetes.io/arch` and
`beta.kubernetes.io/os` as deprecated, each pointing at its replacement, and it is the page the
post's own forecast links to. Nothing at the pin warns about a selector that uses them. Nothing at
the pin warns about a deprecated field or field value at all: the mechanism is per-resource-version,
and there is no page describing a per-field one. And `tasks/debug/debug-cluster/_index.md:69-70` and
`:150-151` still print both deprecated labels in sample `kubectl describe node` output and in a
sample manifest, which is the pin using a value the pin marks deprecated with no warning available
to say so.

**The post's own sample metrics output has a label the pin's metric does not.** All three metrics
samples in the post carry a `contentType` label on `apiserver_request_total`.
`reference/instrumentation/metrics.md:63-68` lists that metric's labels as `code`, `component`,
`dry_run`, `group`, `resource`, `scope`, `subresource`, `verb` and `version`. The string
`contentType` does not appear anywhere in that file. The label was dropped between the post and the
pin, and no page says so — the post is the only record in the tree that it ever existed.

**The audit annotation gained a sibling the post does not mention.**
`reference/labels-annotations-taints/audit-annotations.md:23-28` documents `k8s.io/deprecated`, and
`:30-35` documents `k8s.io/removed-release`, whose example value is `"1.22"`. The post names one
annotation; the pin documents two, and the second carries exactly the fact the screenshot's warning
put in prose.

**The tips became reference text, with the numbers the post did not have.**
`extensible-admission-controllers.md:560-562` carries all three of the post's rules for writing a
warning. The middle one is word for word identical. The first lost the post's parenthetical
explaining that the client adds the prefix. The third lost `Be brief;`. And `:564-567` adds a
caution the post has no equivalent of: individual warning messages over 256 characters may be
truncated by the API server, and beyond 4096 characters of warnings from all sources, additional
warnings are ignored. The advice survived; the hard limits are new.

**The client-side half of the post exists nowhere else in the tree.** Six identifiers appear in the
post: `WarningHandler`, `NoWarnings`, `NewWarningWriter`, `WarningWriterOptions`, `Deduplicate` and
`prom2json`. Each of the six occurs in exactly one file in the whole of `content/en`, and that file
is the post. Deduplication is a documented behaviour of `kubectl` in no page at all; the tool does
it, and the only description of it in the pinned tree is a Go snippet in a 2020 blog entry.
`--warnings-as-errors`, by contrast, is on every one of the 110 generated subcommand pages under
`reference/kubectl/generated/` — the 111th file there is the index — so the flag half of the client
story is documented exhaustively and the library half is not documented at all.

**And the pin disagrees with itself inside this post's own topic.**
`tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning.md:271-355` teaches
version deprecation twice: once on the `apiextensions.k8s.io/v1` tab, and once on an
`apiextensions.k8s.io/v1beta1` tab. `deprecation-guide.md:187-193` records that
`apiextensions.k8s.io/v1beta1` has not been served since v1.22. The page that teaches you how to
deprecate an API version still teaches it on an API version that was removed fifteen releases ago.

**What this exercise does not cover, and where it lives.** The Ingress migration the post's
screenshot demonstrates — the two removed versions, the renamed fields, the required `pathType` — is
[the other 2020 Ingress exercise](02-improvements-to-the-ingress-api-in-kubernetes-1-18.md).
Warnings raised by server-side field validation, and the `fieldValidation` query parameter and
`--validate` that select them, are walked at length in [the 2017 RBAC
exercise](../2017/06-using-rbac-generally-available-18.md); the `ServerSideFieldValidation` ladder
is transcribed in [the 2015 tooling
exercise](../2015/10-kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community.md).
The ValidatingAdmissionPolicy apparatus — a policy, a binding, and a replica count refused without a
webhook server — is built in [the 2018 admission
exercise](../2018/01-extensible-admission-is-beta.md), so this exercise reads the `Warn` action
rather than running it. Pod Security Admission's `warn` label is [the 2018 hardening
exercise](../2018/06-11-ways-not-to-get-hacked.md). Audit policy — the file, the flags, and reading
the log the annotation lands in — is not walked in this archive at all; it is built twice under the
lab tracks, which nothing here may link to, so the audit annotation is read from the pin and not
observed.

**The diff, and why**

**The post is still right, and that is not the finding.** Six years is long enough for an API
description to rot, and this one has not. The finding is what the documentation did with a post that
stayed right: it cited it. Four pages depend on this blog entry for the definition of a word they
use in normative text, one of them at a fragment anchor. That is a load-bearing dependency on a
dated artifact, and the archive has not seen it before. Every previous *still right* verdict in this
walk meant the post could be discarded because the docs had absorbed it. Here the docs absorbed the
post by pointing at it.

**The demonstration broke while the mechanism held.** The post's screenshot and the post's prose
have opposite fates: the prose is quoted by the reference tree, and the screenshot cannot be
reproduced because `networking.k8s.io/v1beta1` is gone. A worked example that demonstrates a
deprecation has a shelf life equal to the deprecation. This is the mirror image of the case the
archive keeps meeting, where the mechanism is renamed and the example still runs.

**One forecast arrived in a different body.** The post's `complain` mode was offered to webhook
authors, and it arrived as `validationActions: [Warn]` on ValidatingAdmissionPolicy — a mechanism
that did not exist in a stable form until v1.30 and that the post does not mention.
Forecast-tracking in this archive has so far asked whether an idea shipped. This one shipped
somewhere the post was not looking, which means the honest verdict is neither *arrived* nor *did not
arrive*.

**One forecast did not arrive, and the pin demonstrates the gap.** Warning about deprecated field
values was named with an example — beta `os`/`arch` node label selectors — and at the pin those
labels are still marked deprecated, still have no warning attached, and are still printed in the
pin's own sample output. A forecast that fails is usually invisible; this one left a testable case
behind, so *Do* can ask the cluster directly and get silence.

**Sample output rots quietly.** The `contentType` label is gone from `apiserver_request_total` and
the only place in the tree that records it ever existed is a sample paste in a blog post. Nothing
announced its removal, nothing deprecated it, and no reader of the post can tell from the post that
it is stale. Fenced sample output is the least durable thing a post contains and the hardest thing
to date.

**And the pin disagrees with itself inside the post's own subject.** The CRD versioning page teaches
version deprecation on `apiextensions.k8s.io/v1beta1`, unserved for fifteen releases. A page about
managing removal, carrying an example on something removed, is the archive's ninth documented
self-disagreement and the second one where the disagreeing page lists the post's author as a
reviewer.

**The ladder**

One gate, two rows, and a hand-off. This is the smallest ladder in the year. Transcribed from
`reference/command-line-tools-reference/feature-gates/`:

```
WarningHeaders  beta   true  1.19 - 1.21
                stable true  1.22 - 1.24   removed: true
```

Its body is one sentence: `Allow sending warning headers in API responses.` There is no `alpha` row.
The gate appears already beta and already default `true` in v1.19, the release the post is about,
which is why the post can describe the behaviour as simply present rather than as something to
enable.

**Skipping alpha is not rare, and the census row for this post says otherwise.** Of the 487 gate
files at the pin, 86 carry no `alpha` row at all, 73 have `beta` as their first stage, and 29 have
exactly the two rows `beta` then `stable` that this gate has. The rare shape is skipping *beta* —
four files in 487 — and this year's instance of that is `EndpointSliceNodeName`, transcribed in [the
EndpointSlices exercise](06-scaling-kubernetes-networking-with-endpointslices.md). So the row's
claim that this is the only ladder in the year to skip a rung is wrong twice over: skipping alpha is
one gate file in six, and the year's genuine rung-skipper is a different post. What the two rows do
say is that the switch was never optional in a released version: default `true` from its first row
to its last.

**The second gate belongs to a sibling and is not repeated.** Warnings raised by server-side field
validation ride on `ServerSideFieldValidation`, which climbed `alpha` at v1.23, `beta` at v1.25,
`stable` at v1.27 through v1.31, and carries `removed: true`. That ladder is transcribed in table
form in [the 2015 tooling
exercise](../2015/10-kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community.md)
and is read there, not here. It matters to this exercise only for its dates: the largest single
source of warnings a modern `kubectl` user meets did not have a gate until three releases after this
post, so the post cannot be describing it.

**Read the two `removed: true` markers together.** Both gates are gone from the flag list, and 230
of the 487 gate files at the pin carry that marker. A removed gate is the strongest possible
statement that a behaviour is not configurable any more: there is no switch to find, and the file
that records the switch existed is not rendered on the website. The behaviour this post announces is
now unconditional, and the only durable evidence that it was ever conditional is two files in a
directory the site does not publish.

**Topology**

One node, the [`solo` topology](../../strands/lab-topologies.md#solo), fresh. Bring the guest up
with [the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, install Kubernetes with [the node baseline
procedure](../../strands/lab-topologies.md#node-baseline-steps), bring the cluster up as usual, and
confirm one `Ready` node before starting.

One node is enough because everything measured here happens in the apiserver's admission and
response path. Nothing in this exercise needs a Pod to start, so the control plane keeps its default
`NoSchedule` taint and no toleration appears anywhere below. Two objects created in *Do* — a
Deployment and a Pod — exist only to be admitted, and whether they ever schedule is not the
measurement.

Warnings arrive on `stderr`, which means every command below has to be run in a way that keeps
`stderr` and `stdout` apart, and the raw header has to be read with something that shows headers.
Both requirements are met the same way as elsewhere in this year: a `kubectl proxy` on `127.0.0.1`
and `curl -si` through it, so that the exact bytes the apiserver sent can be read rather than
kubectl's rendering of them.

What one node cannot show: the audit annotation. Reading `k8s.io/deprecated` off an audit event
needs an audit policy file, an apiserver flag and a log to read, and that plumbing belongs to the
lab tracks. The annotation is read from `audit-annotations.md` in *Read on* and is not observed
here.

**Do**

1. Ask the pin's cluster what it still admits to about the switch. Both gates from *The ladder* are
   removed, so neither should appear in the live gate metric — confirm that rather than assuming it,
   because an absent gate and a gate reporting `0` mean different things:

   ```bash
   kubectl version -o json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["serverVersion"]["gitVersion"])'
   kubectl get --raw /metrics | grep -c 'kubernetes_feature_enabled.*WarningHeaders'
   kubectl get --raw /metrics | grep -c 'kubernetes_feature_enabled.*ServerSideFieldValidation'
   kubectl explain customresourcedefinition.spec.versions.deprecated
   kubectl explain customresourcedefinition.spec.versions.deprecationWarning
   ```

2. Build the pin's own worked example, and discover that it does not apply. The three-version CRD at
   `custom-resource-definition-versioning.md:283-317` is exactly the apparatus this exercise needs —
   `v1alpha1` deprecated with a custom warning, `v1beta1` deprecated with the default one, `v1`
   served and stored — but each version's schema is written `schema: ...`, a placeholder, so the
   example as printed cannot be applied. Supply the missing schemas and keep everything else the
   page gives you:

   ```bash
   cat > /tmp/bw-crd.yaml <<'EOF'
   apiVersion: apiextensions.k8s.io/v1
   kind: CustomResourceDefinition
   metadata:
     name: crontabs.example.com
   spec:
     group: example.com
     names:
       plural: crontabs
       singular: crontab
       kind: CronTab
     scope: Namespaced
     versions:
     - name: v1alpha1
       served: true
       storage: false
       deprecated: true
       deprecationWarning: "example.com/v1alpha1 CronTab is deprecated; see http://example.com/v1alpha1-v1 for instructions to migrate to example.com/v1 CronTab"
       schema:
         openAPIV3Schema:
           type: object
           properties:
             spec:
               type: object
               properties:
                 cronSpec: {type: string}
     - name: v1beta1
       served: true
       storage: false
       deprecated: true
       schema:
         openAPIV3Schema:
           type: object
           properties:
             spec:
               type: object
               properties:
                 cronSpec: {type: string}
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
                 cronSpec: {type: string}
   EOF
   kubectl apply -f /tmp/bw-crd.yaml
   kubectl create namespace bw-warn
   kubectl -n bw-warn apply -f - <<'EOF'
   apiVersion: example.com/v1
   kind: CronTab
   metadata:
     name: nightly
   spec:
     cronSpec: "0 3 * * *"
   EOF
   kubectl proxy --port=8001 &
   sleep 2
   ```

3. Read the bytes the apiserver actually sends. Three requests for the same stored object through
   three served versions, headers shown, body discarded. Record the status code on each and the full
   `Warning` header line where there is one — including the number immediately after `Warning:` and
   the agent field after it:

   ```bash
   for V in v1alpha1 v1beta1 v1; do
     echo "== $V"
     curl -si "http://127.0.0.1:8001/apis/example.com/$V/namespaces/bw-warn/crontabs/nightly" \
       | sed -n '1p;/^[Ww]arning:/p'
   done
   ```

   The post's claim to check here is that a warning `does not change the status code or response
   body in any way`. Two of these three responses carry a warning. Compare all three status lines,
   then compare the bodies with `curl -s ... | python3 -c 'import
   json,sys;print(len(sys.stdin.read()))'` and decide whether the claim holds on this evidence.

4. Now read kubectl's rendering of the same two warnings, and separate the channels. The post says
   warnings go to `stderr` and that the client adds the `Warning:` prefix — both are checkable in
   one command each:

   ```bash
   kubectl -n bw-warn get crontabs.v1alpha1.example.com nightly -o name 2>/tmp/bw-err.txt
   cat /tmp/bw-err.txt
   kubectl -n bw-warn get crontabs.v1beta1.example.com nightly -o name 2>&1 >/dev/null
   kubectl -n bw-warn get crontabs.v1alpha1.example.com nightly -o name 2>/dev/null
   ```

   The second command discards `stdout` and keeps `stderr`; the third does the opposite. One of them
   prints the object name and nothing else, and one prints the warning and nothing else. Then strip
   `v1alpha1`'s override and read the default message the pin promises at
   `custom-resource-definition-v1.md:308` — that it `indicates this version is deprecated and
   recommends use of the newest served version of equal or greater stability, if one exists`:

   ```bash
   kubectl patch crd crontabs.example.com --type=json \
     -p '[{"op":"remove","path":"/spec/versions/0/deprecationWarning"}]'
   kubectl -n bw-warn get crontabs.v1alpha1.example.com nightly -o name 2>&1 >/dev/null
   ```

   Three versions are served, of which two are deprecated. Read the default message against the
   promise and work out which version the apiserver names as `the newest served version of equal or
   greater stability`, and whether it could have named `v1beta1` instead.

5. Find out whether the 256-character caution applies to this kind of warning at all.
   `extensible-admission-controllers.md:565` says individual warning messages over 256 characters
   may be truncated by the API server before being returned to clients, but it says it on the
   webhook page. A `deprecationWarning` is a warning from a different source. Push one past the
   limit and measure what comes back:

   ```bash
   python3 - <<'EOF' > /tmp/bw-patch.yaml
   msg = "example.com/v1alpha1 CronTab is deprecated. " + ("Migrate to example.com/v1. " * 12)
   print(len(msg), "characters", file=__import__("sys").stderr)
   print('spec:\n  versions:\n  - name: v1alpha1\n    deprecationWarning: "%s"' % msg)
   EOF
   kubectl get crd crontabs.example.com -o json > /tmp/bw-crd-full.json
   kubectl patch crd crontabs.example.com --type=merge --patch-file /tmp/bw-patch.yaml
   curl -si "http://127.0.0.1:8001/apis/example.com/v1alpha1/namespaces/bw-warn/crontabs/nightly" \
     | sed -n '/^[Ww]arning:/p' | awk '{print length($0)}'
   ```

   A merge patch on a list keyed by `name` may be refused, may replace the whole list, or may
   succeed — read what `kubectl` says before reading the header. Whichever happens, the measurement
   is the same: either a warning comes back and you compare its length against 256, or the write is
   rejected and the limit was enforced earlier than the caution describes. Both outcomes answer the
   question; record which one you got.

6. Turn the warning into the refusal. This is the post's worked example, reconstructed with an API
   whose removal you control instead of one that was removed six years ago. Stop serving `v1alpha1`,
   then ask for it exactly as in step 3:

   ```bash
   kubectl apply -f /tmp/bw-crd.yaml
   kubectl patch crd crontabs.example.com --type=json \
     -p '[{"op":"replace","path":"/spec/versions/0/served","value":false}]'
   sleep 3
   curl -si "http://127.0.0.1:8001/apis/example.com/v1alpha1/namespaces/bw-warn/crontabs/nightly" \
     | sed -n '1p;/^[Ww]arning:/p'
   kubectl get --raw /apis/example.com | python3 -c 'import json,sys; print([v["version"] for v in json.load(sys.stdin)["versions"]])'
   kubectl -n bw-warn get crontabs.v1alpha1.example.com nightly; echo "exit=$?"
   ```

   Compare the status line with step 3's and note that the response body is now the whole message:
   there is no header to read, because a refusal has nowhere to put a warning. This is the
   difference the post's screenshot cannot show you and `deprecation-guide.md:257-269` records for
   Ingress. Then bring `v1alpha1` back with `kubectl apply -f /tmp/bw-crd.yaml` before the next
   step.

7. Ask the two instruments the post's first section names. The gauge is documented at
   `metrics.md:70-75` as counting deprecated *APIs* that have been requested, broken out by group,
   version, resource, subresource and `removed_release` — and a deprecated CRD version has no
   `removed_release` at all:

   ```bash
   kubectl -n bw-warn get crontabs.v1beta1.example.com nightly -o name 2>/dev/null
   kubectl get --raw /metrics | grep 'apiserver_requested_deprecated_apis' | head -20
   LABELS='
   import re,sys
   keys=set()
   for line in sys.stdin:
       if line.startswith("apiserver_request_total{"):
           keys.update(re.findall(r"([a-zA-Z_]+)=", line[line.index("{"):]))
   print(sorted(keys))
   '
   kubectl get --raw /metrics | python3 -c "$LABELS"
   ```

   The second command asks whether a CRD's own deprecated version registers in the gauge at all. The
   third prints the live label keys of `apiserver_request_total` — compare that list with the nine
   keys at `metrics.md:63-68` and with the labels in all three of the post's sample outputs. One key
   the post shows is missing from both the pin's page and your cluster.

8. Check the flag half of the client story, which is the half the documentation kept. The same
   request run twice, once ordinary and once with the flag, and the exit codes compared — then the
   same flag against a request that raises no warning at all:

   ```bash
   kubectl -n bw-warn get crontabs.v1beta1.example.com nightly -o name; echo "exit=$?"
   kubectl -n bw-warn get crontabs.v1beta1.example.com nightly -o name --warnings-as-errors; echo "exit=$?"
   kubectl -n bw-warn get crontabs.v1.example.com nightly -o name --warnings-as-errors; echo "exit=$?"
   ```

   Read the second exit code against the flag's own documented description — `Treat warnings
   received from the server as errors and exit with a non-zero exit code` — and note that the object
   was still returned. Then decide from the third command whether the flag changes anything when
   nothing warns.

9. Measure the behaviour that no page in the tree documents. The post's Go snippet sets
   `Deduplicate: true`, and `kubectl` deduplicates by default; nothing at the pin says so. Make one
   command send two requests that would produce the same warning twice:

   ```bash
   cat > /tmp/bw-two.yaml <<'EOF'
   apiVersion: example.com/v1beta1
   kind: CronTab
   metadata:
     name: alpha-one
   spec:
     cronSpec: "0 1 * * *"
   ---
   apiVersion: example.com/v1beta1
   kind: CronTab
   metadata:
     name: alpha-two
   spec:
     cronSpec: "0 2 * * *"
   EOF
   kubectl -n bw-warn apply -f /tmp/bw-two.yaml 2>/tmp/bw-dedup.txt
   grep -c 'Warning:' /tmp/bw-dedup.txt
   cat /tmp/bw-dedup.txt
   ```

   Two objects were created through a deprecated version, so two responses carried the same header.
   Count the `Warning:` lines and decide from the count whether the client collapsed them. Whatever
   the number is, it is not documented anywhere in `content/en` outside a 2020 blog post — grep the
   tree for `Deduplicate` and see what you get.

10. Ask for the forecast that did not arrive. The post proposed warning about deprecated field
    values and named beta `os`/`arch` node label selectors as the case. Both labels are still marked
    deprecated at `labels-annotations-taints/_index.md:819-829`. Find out first whether your node
    even carries them, then use one in a selector and see whether anything objects:

    ```bash
    kubectl get nodes -o json | python3 -c 'import json,sys; [print(sorted(k for k in n["metadata"]["labels"] if k.startswith("beta.kubernetes.io/"))) for n in json.load(sys.stdin)["items"]]'
    curl -si -X POST -H 'Content-Type: application/json' \
      "http://127.0.0.1:8001/api/v1/namespaces/bw-warn/pods" \
      -d '{"apiVersion":"v1","kind":"Pod","metadata":{"name":"bw-legacy-selector"},"spec":{"nodeSelector":{"beta.kubernetes.io/os":"linux"},"containers":[{"name":"c","image":"registry.k8s.io/pause:3.10"}]}}' \
      | sed -n '1p;/^[Ww]arning:/p'
    ```

    The Pod will not schedule, and that is not the measurement — the response to the POST is.
    Compare the header list here with step 3's. Then read
    `tasks/debug/debug-cluster/_index.md:69-70`, where the pin's own sample node output carries both
    deprecated labels, and decide what a mechanism that warns per resource version can and cannot
    tell an operator about a value inside a field.

**Expect**

Step 1 should report a v1.37 server. Both `grep -c` calls should print `0`: neither gate is in the
live gate metric, because both are removed, and a removed gate reports nothing rather than reporting
`0` as its value. Both `kubectl explain` calls should describe the fields — `deprecated` as a
boolean, `deprecationWarning` as a string that may only be set when `deprecated` is true — which is
the field documentation from `custom-resource-definition-v1.md:303-308` arriving over the cluster's
own OpenAPI rather than from the page.

Step 2 should create the CRD and the namespace and one `CronTab`. The point of the step is what
happens if you skip the schemas: the page's example, pasted as printed, is not valid YAML for a CRD,
because `schema: ...` is prose. Note that the object was created at `v1` with no warning, which
establishes the baseline for step 3.

Step 3 should return `HTTP/1.1 200 OK` three times. Two of the three should carry a `Warning` header
— the `v1alpha1` request carrying the custom text from the CRD, the `v1beta1` request carrying a
message the apiserver composed. Record the number that follows `Warning:` and the agent field after
it; `extensible-admission-controllers.md:556` documents the code `299` for webhook warnings, and
this exercise is not asking a webhook. The `v1` request should carry no warning at all. Bodies and
status codes should be indistinguishable across all three, which is the post's claim confirmed byte
by byte.

Step 4 should show the warning on `stderr` and the object name on `stdout`, cleanly separated by the
two redirections, and the printed warning should begin `Warning:` even though the CRD's
`deprecationWarning` value does not — the prefix is the client's, exactly as the post says and
exactly as the first webhook tip instructs authors not to duplicate. After the patch, the `v1alpha1`
request should carry a message naming a replacement version. Which version it names is the
measurement; the promise is `newest served version of equal or greater stability`, and `v1beta1` is
served but is neither newest nor more stable.

Step 5 should end in one of two states, and the exercise accepts either. If the patch takes and a
long warning comes back, compare the header length against 256 and decide whether the webhook page's
caution describes a general apiserver behaviour or only a webhook one. If `kubectl` refuses the
patch, read its message: a merge patch against a list of versions keyed by `name` is a known hazard,
and a rejection here is a statement about patch semantics rather than about warning length. Either
way the CRD is restored at the start of step 6.

Step 6 should return a status line that is not `200`, and a JSON body rather than a header: with
`v1alpha1` unserved, there is no successful response for a warning to ride on. The discovery list
should print two versions instead of three. `kubectl` should exit non-zero with a message about the
resource not being recognised, which is a different failure from a rejected object — the version is
gone, not the request invalid. Set beside step 3, this is the whole distance the post's Ingress
screenshot travelled between v1.19 and v1.22.

Step 7 should print nothing for `apiserver_requested_deprecated_apis`, or print only samples that
have nothing to do with your CRD. A `deprecated: true` custom resource version is not a deprecated
*built-in* API, has no `removed_release`, and the gauge is documented as counting the latter. That
is the boundary of the post's second signal, and it is not stated on any page. The label list should
come back with the nine keys at `metrics.md:63-68` and without `contentType`, so that the post's
three sample pastes are the only place in the tree that label survives.

Step 8 should give `exit=0` for the plain request, non-zero for the same request with the flag, and
`exit=0` for the `v1` request with the flag. The object should still be printed in the second case:
the flag changes the exit code, not the response. This is the one part of the post's client section
the documentation kept, and it kept it 110 times over.

Step 9 should create two objects and print a single-figure count of `Warning:` lines. If the count
is `1` where two requests each carried a header, `kubectl`'s default handler deduplicated, and you
have just measured a behaviour that `Deduplicate` in a 2020 blog post is the only description of in
the pinned tree. If the count is `2`, the default handler does not deduplicate and the post's
snippet is showing you an option rather than a default. Record which, because the pin cannot tell
you.

Step 10 should print an empty list for each node, or a list containing the two deprecated labels —
modern kubelets stopped setting them, but the pin does not say when, so treat whichever you get as
the measurement. The POST should return `201 Created` with no `Warning` header. Nothing warns about
a deprecated label in a selector, six years after the post proposed it, on a cluster whose own
documentation prints those labels in sample output. That silence is the forecast's outcome, and it
is the only outcome in this exercise you can observe by getting nothing back.

**Read on**

1. `reference/using-api/deprecation-policy.md:288-303` states the post's three signals in the post's
   own order and is the only page that carries all three. Read it against the post, then read its
   reviewers list — `bgrant0607`, `lavalamp`, `thockin` — and note it is the one page in this
   territory that neither cites the post nor lists its author. Decide from the two texts which came
   first.

2. `reference/using-api/api-concepts.md:1224-1270` is the largest source of warnings a modern
   `kubectl` user meets, and `:1237-1242` defines the `Warn` level by linking this post's full
   title. Read the `fieldValidation` parameter at `:1250` and the `--validate` default at
   `:1266-1270`, then read [the 2017 RBAC
   exercise](../2017/06-using-rbac-generally-available-18.md), which walks that mechanism, and work
   out how many of the warnings a v1.37 user sees come from the feature this post announces and how
   many from one that did not exist yet.

3. `reference/labels-annotations-taints/audit-annotations.md:23-35` documents two annotations where
   the post names one. Read both, then find what sets `k8s.io/removed-release` and decide whether
   either annotation can be produced by the CRD you built in *Do* — and, if not, what that says
   about the difference between a deprecated built-in API and a deprecated custom one.

4. Three later blog posts cite this one: the 2022 Pod Security post, the 2024
   ValidatingAdmissionPolicy GA post, and the 2026 `externalIPs` deprecation post. Each links the
   word `warning` to it for a different mechanism. Read what each one is actually doing, then read
   `validating-admission-policy.md:98-110` and decide whether the post's `complain` mode arrived
   once, three times, or not at all.

5. Unanswerable from the pin: the client library. `WarningHandler`, `NoWarnings`,
   `NewWarningWriter`, `WarningWriterOptions` and `Deduplicate` each appear in exactly one file in
   `content/en`, and it is this post. The pin can establish that no documentation page describes the
   client-side API. It cannot tell you whether those types still exist in `client-go` at v0.37,
   whether the defaults changed, or whether the deduplication you measured in step 9 is the same
   deduplication the post's snippet asks for.

**Teardown**

```bash
kill %1 2>/dev/null; pkill -f 'kubectl proxy --port=8001'
kubectl delete namespace bw-warn
kubectl delete crd crontabs.example.com
rm -f /tmp/bw-crd.yaml /tmp/bw-crd-full.json /tmp/bw-patch.yaml /tmp/bw-two.yaml /tmp/bw-err.txt /tmp/bw-dedup.txt
kubectl get crd crontabs.example.com 2>&1 | tail -1
```

Then take the guest down with [the teardown steps](../../strands/lab-topologies.md#teardown).
