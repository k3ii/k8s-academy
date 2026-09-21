<a id="kubernetes-v1-35-structured-zpages"></a>

# Every Accept header this post prints asks for a version string that appears nowhere in the pinned documentation, both of the feature gates it tells you to switch on are already on by default, and the access rule its security section states is not the rule the built-in ClusterRole carries

**Post** — [Kubernetes 1.35: Enhanced Debugging with Versioned z-pages APIs](https://kubernetes.io/blog/2025/12/31/kubernetes-v1-35-structured-zpages/),
2025-12-31.

218 lines, 9,465 bytes, the last post of 2025 and the last of the v1.35 release series. Two authors,
both from SIG Instrumentation. Announces that `/statusz` and `/flagz` — alpha since 1.32 — can now
return versioned JSON instead of plain text, and prints the `Accept` header that asks for it.

**As written**

The post opens by naming the problem: you want the runtime state of a control plane component and
the only machine-readable thing the cluster offers is `/metrics`. `:15` introduces z-pages as
special debugging endpoints, alpha since Kubernetes 1.32, exposed by `kube-apiserver`,
`kube-controller-manager`, `kube-scheduler`, `kubelet` and `kube-proxy`, and explains the name: the
convention of putting debugging under `/*z` paths. `:19-23` is a definition list of the two
endpoints the project ships — `/statusz` for version, start time, uptime and available debug paths,
`/flagz` for the command-line arguments a component was started with, confidential values redacted.
`:25` states the limitation the post exists to remove: until now both returned plain text that was
difficult to parse programmatically.

`:33` sets the compatibility rule. The structured responses are opt-in; without an `Accept` header
the endpoints keep returning the familiar plain text. `:35-50` shows that plain text, fetched with
`curl` and the API server's own client certificate against `https://localhost:6443/statusz`: seven
lines beginning with a warning that the endpoint is not meant to be machine parseable, then
`Started`, `Up`, `Go version`, `Binary version: 1.35.0-alpha.0.1595`, `Emulation version: 1.35` and
a `Paths` line listing six URLs.

`:56-58` is the header that changes the answer — `Accept:
application/json;v=v1alpha1;g=config.k8s.io;as=Statusz` — and `:62-83` is the JSON that comes back,
a `Statusz` object at `config.k8s.io/v1alpha1` carrying `startTime`, `uptimeSeconds`, `goVersion`,
`binaryVersion`, `emulationVersion` and the same six paths as an array. `:87-89` and `:93-108` do
the same for `/flagz`: the same header with `as=Flagz`, and a `Flagz` object whose `flags` map
carries five keys.

`:110-124` argues why it matters, in three numbered points, and closes with a roadmap sentence: the
project expects to introduce `v1beta1` and eventually `v1` versions of the API. `:126-155` is the
how. Prerequisites at `:128-133`: `/statusz` needs the `ComponentStatusz` feature gate, `/flagz`
needs `ComponentFlagz`. The example at `:139-155` is two `curl` invocations, each with the API
server's client certificate, each with the `v1alpha1` header, each piped to `jq .`. A note at
`:157-161` says the examples verify the server certificate and that `--insecure` is for test
environments only.

`:163-194` is the considerations section. `:167-171` warns that this is alpha and the schema may
change. `:177` states the access rule: z-pages are restricted to members of the `system:monitoring`
group, following the same authorization model as `/healthz`, `/livez` and `/readyz`. `:179` says
authentication depends on your cluster unless anonymous authentication is enabled. `:181-186` lists
what the endpoints disclose. `:196-203` invites you to try it: enable the two gates, query both
formats, build a tool, send feedback.

**As it runs now**

**The two gates the post asks you to enable are already enabled.** `ComponentStatusz.md` and
`ComponentFlagz.md` are the same file twice over: alpha with `defaultValue: false` from 1.32 to
1.35, beta with `defaultValue: true` from 1.36, no `toVersion`, no `locked`, and a two-line body
pointing at the same reference page. The Prerequisites section at `:128-133` and the first of the
four Try-it-out steps at `:200` both ask for work the pin has already done.

**The `Accept` header the post prints four times asks for a version string that does not appear
anywhere in the pinned documentation.** The post writes `v=v1alpha1` at `:57`, `:88`, `:145` and
`:153`, and `"apiVersion": "config.k8s.io/v1alpha1"` at `:65` and `:96`. Search `docs` for the group
without a component prefix and you get exactly ten lines, all in
`docs/reference/instrumentation/zpages.md` — `:65`, `:77`, `:97`, `:100`, `:104`, `:169`, `:181`,
`:197`, `:200` and `:204` — and every one of them says `v1beta1`. The un-prefixed group at
`v1alpha1` has zero occurrences. Every other `config.k8s.io` in the tree carries a component prefix
(`apiserver.`, `controllermanager.`, `kubescheduler.`), so those ten lines are the entire documented
surface of the group the post names.

**The pin says getting that header wrong is a refusal, not a fallback.** `zpages.md:68-71` and the
identical note at `:172-175` state that a request for `application/json` that does not specify all
of `g`, `v` and `as` gets `406 Not Acceptable`. The post's compatibility promise at `:33` covers the
case where you send no `Accept` header at all; it says nothing about the case where you send one the
server does not recognise, which is now the case its own examples produce.

**The way out of a 406 is documented on a page z-pages never links.**
`reference/using-api/api-concepts.md:1004` and `:1015` show the idiom: list the structured type and
a plain media type in the same header, comma-separated, and a server that cannot produce the first
falls back to the second instead of refusing. `:1091-1102` spells out what happens when a client
asks for the structured form and nothing else, and shows the `q=0.9` weighting that makes the
preference explicit. This is the same content negotiation mechanism, in the same syntax, on the
reference page for the API — `as=Table;g=meta.k8s.io;v=v1` rather than `as=Statusz;g=config.k8s.io`.
Neither page mentions the other.

**The z-pages reference page has seven markdown links and five of them point at itself.** `:30-34`
is a hand-maintained nested list of the page's own five headings, whose first item links to the
heading it is already sitting under. The two links that leave the page, at `:38` and `:136`, go to
the two feature gates. Nothing links to `api-concepts.md`, to RBAC, or to any of the five components
the post names.

**The reference page stamps the same feature with three different releases.** `:14` carries `{{<
feature-state for_k8s_version="v1.36" state="beta" >}}` and the closing note at `:217-220` agrees:
the structured responses for both endpoints are beta features in v1.36. But `:59-61` says the
structured format starts with Kubernetes v1.35, and the header printed three lines below that
sentence is `v1beta1`. Both cannot be true. Either the structured response existed at v1.35 and did
not carry the `v1beta1` schema the page shows, or the page is dating a schema a release before it
was written. `:19` and `:25` add a third number by rendering `{{< skew currentVersion >}}`, which is
v1.37 at this pin.

**The plain text sample on the reference page is three releases older than the page around it.**
`:43-53` shows `Binary version: 1.32.0-alpha.0.1484&#43;5eeac4f21a491b-dirty` and `Emulation
version: 1.32.0-alpha.0.1484` — a development build of the release the feature was introduced in,
captured before the post was written. The post's own plain text sample at `:47-48` shows
`1.35.0-alpha.0.1595` and `1.35`. The reference page has been edited repeatedly since: it gained a
beta banner, two structured subsections, two Go structs and a note about `/configz`, and nobody
re-ran the one command at the top.

**An HTML entity has leaked into a fenced code block, and it is the only one in the tree.** `&#43;`
at `zpages.md:50` is the escaped form of `+`. Search all of `docs` and there is exactly one
occurrence, that one. Inside a fenced block the entity is not decoded, so the rendered page shows
readers `&#43;` where the binary printed `+` — the sample was pasted through something that escaped
it on the way in.

**The pin's structured sample is the post's sample with one line changed.** `zpages.md:74-95` and
post `:62-83` are byte-identical except for the `apiVersion` line: same `startTime` of
`2025-10-29T00:30:01Z`, same `uptimeSeconds` of `856`, same `go1.23.2`, same `binaryVersion` of
`1.35.0`, same `emulationVersion`, same six paths in the same order. Somebody copied the blog post
into the reference page and edited `v1alpha1` to `v1beta1`. The Go struct immediately below, at
`:99-132`, then declares a field the copied sample cannot contain: `minimumCompatibilityVersion`,
which appears in no sample anywhere and whose only two occurrences in the tree are its own
declaration and its own comment.

**The flagz sample was edited the same way, and the edit shows.** `zpages.md:178-195` carries the
post's five flags plus two more: `anonymous-auth` inserted in alphabetical position, and
`default-watch-cache-size` appended after `profiling`, out of the alphabetical order the other six
keys follow. A map re-captured from a running server would have been sorted or unsorted throughout;
one that is sorted except for its last entry was typed. And the value of the inserted key is
`"anonymous-auth": "true"`, on the page whose companion post says at `:179` that you need a real
identity unless anonymous authentication is enabled.

**The access rule the post states is not the rule the pin carries.** `:177` says access to z-page
endpoints is restricted to members of the `system:monitoring` group, following the same
authorization model as `/healthz`, `/livez` and `/readyz`. `system:monitoring` occurs in exactly two
lines under `docs`, both inside one row of the default-ClusterRoles table at
`reference/access-authn-authz/rbac.md:801-802`, and that row is the whole documented definition of
what the group can reach: the three liveness and readiness endpoints, their `/*` forms, `/metrics`,
and the API server's handling of the traceparent header. Neither `/statusz` nor `/flagz` is in the
list. The post names the model correctly and then claims membership of a set the pin does not put
the endpoints in.

**The reference page has nothing at all to say about access control.** `zpages.md` runs 220 lines
across two endpoints, four subsections, two JSON samples and two Go structs, and mentions no group,
no ClusterRole, no authorization mode and no RBAC. The post's security section is the only
description of who may read these endpoints, and the one page that could confirm it is silent.

**The post's own example cannot test the post's own access rule.** Both `curl` invocations, at
`:39-41` and again at `:141-155`, authenticate with
`/etc/kubernetes/pki/apiserver-kubelet-client.crt`. That certificate's group is `system:masters`, a
fact this walk has already settled from the certificates table and watched cross an authorization
hop; the [2023 node log query row](../2023/03-node-log-query-alpha.md) holds it at `:103-104` and
`:371-374`. A super-user certificate reaches every non-resource URL there is, so the example
succeeds whether or not the `system:monitoring` claim eighteen paragraphs later is true.

**Five components are named and the documentation reaches one.** `:15` lists `kube-apiserver`,
`kube-controller-manager`, `kube-scheduler`, `kubelet` and `kube-proxy`. The strings `statusz` and
`flagz` appear in exactly four files under `docs`: the two gate files, `zpages.md`, and
`tasks/administer-cluster/configure-feature-gates.md`. Every worked example on all four is the API
server on `localhost:6443`. No page gives an address, a port or a proxy path for either endpoint on
a kubelet or a kube-proxy.

**The note that admits the gap names a third z-endpoint the post never mentions.**
`zpages.md:138-140` says `/flagz` reports command-line flags and defaults, that for components which
also load configuration files — naming the kubelet and kube-proxy — the effective running
configuration can differ, and that you should use `/configz` where available. `/configz` is
documented for the kubelet in two places,
`reference/access-authn-authz/kubelet-authn-authz.md:104-128` and
`tasks/administer-cluster/kubelet-config-file.md:167`. For kube-proxy it is documented nowhere. The
escape hatch offered to the two components z-pages does not document is itself documented for one of
them.

**The gate-checking page now offers `/flagz` as its fourth method, and at v1.35 it is the only one
of the four that needs a gate.** `tasks/administer-cluster/configure-feature-gates.md:180-234` lists
four ways to find out which feature gates a component is running: read the static Pod manifest, read
the kubelet's `configz`, read the `kubernetes_feature_enabled` metric, or read `/flagz`. The first
three work on any cluster. The fourth, added at `:222-234`, works only where `ComponentFlagz` is on
— which on a v1.35 cluster means you must already know how to turn a gate on before the endpoint can
tell you which gates are on.

**The roadmap sentence came true in one release, and it is what broke the post.** `:192` expects the
project to introduce `v1beta1` and eventually `v1` versions of the API. `v1beta1` arrived at 1.36,
one release after publication, and took the gates to beta with it. `v1` has not arrived: the
un-prefixed group appears at no other version anywhere in the tree. The half of the prediction that
landed is precisely the half that makes every `Accept` header above it stale.

**Three lines of trailing whitespace across the two documents.** Post `:158` and `:159`, both inside
the `--insecure` note; `zpages.md:219`, inside the closing beta note. Both are notes, both are the
last thing on their page, and both were edited by hand after the surrounding block was written.

**What this exercise does not cover, and where it lives**

The kubelet's fine-grained authorization table — which paths escape the `proxy` catch-all under
`KubeletFineGrainedAuthz`, and why `/logs/*` never needed to — belongs to the [2023 node log query
row](../2023/03-node-log-query-alpha.md), which reads `kubelet-authn-authz.md:99-134` in full. Read
it if you want the reason `/statusz` and `/flagz` have no row of their own in that table. The same
row owns the certificates table and the `system:masters` group of the API server's kubelet client,
which this exercise cites and does not re-derive.

`/flagz` as an instrument for reading a running component's flags is the [2017 RBAC
row](../2017/06-using-rbac-generally-available-18.md)'s, which uses it to read the authorizer chain
off a cluster whose manifest disagrees with the documentation, and which prints the `ComponentFlagz`
ladder for that purpose. That row's step 8 needs this exercise's step 3 to have happened first on a
v1.35 cluster; the ladder it prints says why.

HTTP content negotiation in general — the four wire encodings, the `produces` list, what a default
cluster actually serves — is the [2016 OpenAPI row](../2016/15-kubernetes-supports-openapi.md)'s, at
`api-concepts.md:140`. Field validation and the `fieldValidation` parameter, which live further down
the same reference page, belong to the [2023 field validation
row](../2023/04-openapi-v3-field-validation-ga.md) at `api-concepts.md:1200-1286`. This exercise
uses only `:941-1102`, the `as`/`g`/`v` parameters and the fallback idiom, which neither row
touches.

Reading the kubelet's effective configuration out of `configz` is settled several times over in this
walk and is not re-done here. The 2024 image filesystem row is the fullest treatment; this exercise
mentions `/configz` only because `zpages.md` points at it.

**The diff, and why**

**Broke.** Every `Accept` header the post prints is a string the pin does not serve. The post gives
the header four times, in two fences and two inline spans, and each asks for
`config.k8s.io/v1alpha1`. The pinned reference publishes only `config.k8s.io/v1beta1`, and states
twice that a request naming the wrong parameters is answered with `406 Not Acceptable` rather than
with plain text. This is the rare break that the post itself predicted, three paragraphs before the
end, in a roadmap item it wrote as a hope.

**Retired by being agreed with.** The Prerequisites section, and the first of the four Try-it-out
steps, ask you to enable two feature gates. Both went beta with `defaultValue: true` at 1.36. The
instruction did not become wrong; it became unnecessary, which is a different thing and leaves a
different trace — the post's steps still run, they just change nothing.

**Still right.** The backward-compatibility promise at `:33` holds exactly as written. A request
with no `Accept` header still gets the plain text format, and the pin's own plain text sample at
`:43-53` is the proof, still sitting at the top of the reference page in a shape the post would
recognise. The two endpoints, their names, their contents and the `/*z` convention behind them are
all unchanged.

**Never absorbed.** The security section is the post's largest original contribution and none of it
reached the documentation. The `system:monitoring` claim, the note that authentication depends on
whether anonymous auth is enabled, and the three-item disclosure list have no counterpart on
`zpages.md`, and the one page that describes what `system:monitoring` can reach does not list these
endpoints. A reader who finds the endpoints through the reference page learns nothing about who may
call them.

**The ladder**

Two gates, one ladder, printed twice because the post names them separately and because the identity
is the point.

`ComponentStatusz`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.32 – v1.35 |
| beta | `true` | — | v1.36 – |

`ComponentFlagz`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.32 – v1.35 |
| beta | `true` | — | v1.36 – |

Neither file declares `removed` or `former_titles`, and neither ladder has closed: both are beta
with no stable rung. Four releases of alpha and then a joint promotion — the two endpoints have
never been at different stages, which is why the post can put them behind one Prerequisites heading
and the reference page can stamp one banner across both. It also means the lab, at v1.35, sits on
the last rung of the alpha run: the last release in which the post's instructions were necessary,
and the release the post was written for.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), fresh. One node at `10.10.10.180`,
4096MB, 4 vCPU, 25G. Nothing here is scheduled and nothing is namespaced: every cluster-side step is
a request to one API server, made either through `kubectl` or with `curl` from inside the node,
because the endpoints listen on the API server's own port and the post's example authenticates with
a certificate that only exists on disk there. Step 3 edits the static Pod manifest, so a second node
would buy nothing and a second control plane would cost a restart. Bring the guest up with [the
provisioning recipe](../../strands/lab-topologies.md#provision) and take it through [the node
baseline](../../strands/lab-topologies.md#node-baseline-steps) to a working single-node cluster at
v1.35.

**Do**

1. Find out what the cluster serves before you open the post. The endpoints are gated, the gates are
   alpha at this version, and the answer to every later step depends on knowing which of the paths
   the API server advertises actually exist.

   ```sh
   mkdir -p /tmp/bw-zpages && cd /tmp/bw-zpages
   kubectl version
   kubectl get --raw /statusz > statusz-before.txt 2>&1; echo "statusz rc=$?"
   kubectl get --raw /flagz   > flagz-before.txt   2>&1; echo "flagz rc=$?"
   head -3 statusz-before.txt flagz-before.txt
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled.*Component' || echo "no Component* gate metrics"
   ```

2. Run the post's three commands verbatim, on the cluster the post was written for, before changing
   anything. Print status codes rather than bodies: the difference between the three outcomes this
   exercise is about — plain text, structured JSON, and a refusal — is only visible in the code.

   ```sh
   printf '%s\n' \
     '#!/bin/sh' \
     '# $1 = path, $2 = Accept header (empty for none)' \
     'A="$2"; S="https://localhost:6443$1"; P=/etc/kubernetes/pki' \
     'set -- -s -o /tmp/zp.out -w "%{http_code} %{content_type}\n"' \
     'set -- "$@" --cert $P/apiserver-kubelet-client.crt --key $P/apiserver-kubelet-client.key --cacert $P/ca.crt' \
     '[ -n "$A" ] && set -- "$@" -H "Accept: $A"' \
     'curl "$@" "$S"; head -c 300 /tmp/zp.out; echo' \
     > /tmp/bw-zpages/zp.sh
   scp /tmp/bw-zpages/zp.sh zain@10.10.10.180:/tmp/zp.sh

   ssh zain@10.10.10.180 "chmod +x /tmp/zp.sh
     echo '-- plain, no Accept'; sudo /tmp/zp.sh /statusz ''
     echo '-- structured, the post header'; sudo /tmp/zp.sh /statusz 'application/json;v=v1alpha1;g=config.k8s.io;as=Statusz'
     echo '-- flagz, the post header';      sudo /tmp/zp.sh /flagz   'application/json;v=v1alpha1;g=config.k8s.io;as=Flagz'"
   ```

3. Do what `:128-133` and `:200` tell you to do. This is the only step that can leave the node
   without a control plane, so back the manifest up first.

   ```sh
   ssh zain@10.10.10.180 "sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/bw-apiserver.yaml.bak \
     && ls -l /tmp/bw-apiserver.yaml.bak"

   ssh zain@10.10.10.180 "sudo sed -i '/- kube-apiserver\$/a\\    - --feature-gates=ComponentStatusz=true,ComponentFlagz=true' /etc/kubernetes/manifests/kube-apiserver.yaml \
     && sudo grep -n 'feature-gates' /etc/kubernetes/manifests/kube-apiserver.yaml"

   echo "waiting for the API server"
   until kubectl version >/dev/null 2>&1; do sleep 5; done
   kubectl -n kube-system get pods -l component=kube-apiserver
   ```

4. Repeat step 2 against the enabled server, and put the pin's header beside the post's. Exactly one
   version string in each pair should produce JSON. Which one it is settles whether the post
   documented the header its own release shipped.

   ```sh
   ssh zain@10.10.10.180 "
     echo '-- plain, no Accept'; sudo /tmp/zp.sh /statusz ''
     echo '-- post: v1alpha1'; sudo /tmp/zp.sh /statusz 'application/json;v=v1alpha1;g=config.k8s.io;as=Statusz'
     echo '-- pin:  v1beta1';  sudo /tmp/zp.sh /statusz 'application/json;v=v1beta1;g=config.k8s.io;as=Statusz'
     echo '-- post: v1alpha1 flagz'; sudo /tmp/zp.sh /flagz 'application/json;v=v1alpha1;g=config.k8s.io;as=Flagz'
     echo '-- pin:  v1beta1 flagz';  sudo /tmp/zp.sh /flagz 'application/json;v=v1beta1;g=config.k8s.io;as=Flagz'"
   ```

5. Test the rule at `zpages.md:68-71` one parameter at a time. Drop `g`, drop `v`, drop `as`, then
   ask for bare JSON, then send nothing — five requests, and the note predicts the code for four of
   them.

   ```sh
   W=$(ssh zain@10.10.10.180 "sudo /tmp/zp.sh /statusz 'application/json;v=v1beta1;g=config.k8s.io;as=Statusz'" | head -1)
   echo "all three: $W"
   for H in \
     'application/json;g=config.k8s.io;as=Statusz' \
     'application/json;v=v1beta1;as=Statusz' \
     'application/json;v=v1beta1;g=config.k8s.io' \
     'application/json' \
     '*/*' ; do
     printf '%-52s ' "$H"
     ssh zain@10.10.10.180 "sudo /tmp/zp.sh /statusz '$H'" | head -1
   done
   ```

6. Now rescue the post. `api-concepts.md:1004` and `:1015` show the fallback idiom: name a second
   acceptable media type in the same header. Apply it to the post's stale version string and watch a
   refusal turn back into the plain text the post promised at `:33`.

   ```sh
   ssh zain@10.10.10.180 "
     echo '-- stale header alone';      sudo /tmp/zp.sh /statusz 'application/json;v=v1alpha1;g=config.k8s.io;as=Statusz'
     echo '-- stale header, fallback';  sudo /tmp/zp.sh /statusz 'application/json;v=v1alpha1;g=config.k8s.io;as=Statusz, text/plain'
     echo '-- stale header, weighted';  sudo /tmp/zp.sh /statusz 'application/json;v=v1alpha1;g=config.k8s.io;as=Statusz, text/plain;q=0.9'
     echo '-- current header, fallback'; sudo /tmp/zp.sh /statusz 'application/json;v=v1beta1;g=config.k8s.io;as=Statusz, text/plain'"
   ```

7. Lay the server's JSON beside the two published samples. The pin's sample is the post's sample
   with the `apiVersion` line changed, so anything that differs from both came from the binary and
   not from an editor.

   ```sh
   ssh zain@10.10.10.180 "sudo curl -s \
     --cert /etc/kubernetes/pki/apiserver-kubelet-client.crt \
     --key /etc/kubernetes/pki/apiserver-kubelet-client.key \
     --cacert /etc/kubernetes/pki/ca.crt \
     -H 'Accept: application/json;v=v1beta1;g=config.k8s.io;as=Statusz' \
     https://localhost:6443/statusz" > /tmp/bw-zpages/statusz.json
   python3 -m json.tool /tmp/bw-zpages/statusz.json
   python3 -c "import json;d=json.load(open('/tmp/bw-zpages/statusz.json'));print(sorted(d.keys()))"

   ssh zain@10.10.10.180 "sudo curl -s \
     --cert /etc/kubernetes/pki/apiserver-kubelet-client.crt \
     --key /etc/kubernetes/pki/apiserver-kubelet-client.key \
     --cacert /etc/kubernetes/pki/ca.crt \
     -H 'Accept: application/json;v=v1beta1;g=config.k8s.io;as=Flagz' \
     https://localhost:6443/flagz" > /tmp/bw-zpages/flagz.json
   python3 -c "import json;d=json.load(open('/tmp/bw-zpages/flagz.json'));f=d['flags'];print(len(f),'flags');print([k for k in ('advertise-address','allow-privileged','anonymous-auth','authorization-mode','enable-priority-and-fairness','profiling','default-watch-cache-size') if k in f])"
   ```

8. Test the post's access rule against the pin's ClusterRole. `kubectl auth can-i` answers for
   non-resource URLs, and the group is impersonable, so you can ask the cluster the question `:177`
   answers in prose — and ask the same question of the three endpoints the post says share the
   model.

   ```sh
   for U in /statusz /flagz /healthz /livez /readyz /metrics /version; do
     printf '%-10s system:monitoring=%-4s me=%s\n' "$U" \
       "$(kubectl auth can-i get "$U" --as=probe --as-group=system:monitoring 2>/dev/null)" \
       "$(kubectl auth can-i get "$U" 2>/dev/null)"
   done
   kubectl get clusterrole system:monitoring -o jsonpath='{range .rules[*]}{.nonResourceURLs}{"\n"}{end}'
   kubectl get clusterrolebinding -o json | python3 -c "import sys,json;print([b['metadata']['name'] for b in json.load(sys.stdin)['items'] if b['roleRef']['name']=='system:monitoring'])"
   ```

9. Run the fourth gate-checking method from `configure-feature-gates.md:222-234` against the other
   three on the same cluster, for the two gates you just switched on. One of the four had to be used
   before the fourth became available.

   ```sh
   echo '-- method 1: the manifest'
   ssh zain@10.10.10.180 "sudo grep -n 'feature-gates' /etc/kubernetes/manifests/kube-apiserver.yaml"
   echo '-- method 3: the metric'
   kubectl get --raw /metrics | grep 'kubernetes_feature_enabled.*Component'
   echo '-- method 4: /flagz'
   kubectl get --raw /flagz | grep -i 'feature-gates'
   echo '-- method 4, structured'
   python3 -c "import json;print(json.load(open('/tmp/bw-zpages/flagz.json'))['flags'].get('feature-gates'))"
   ```

10. Offline, in a checkout of the pinned tree. Count the documented surface of the feature, and read
    the four places it is mentioned against each other.

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -rln 'statusz\|flagz' docs
    grep -rn 'config\.k8s\.io' docs | grep -v '[a-z]\.config\.k8s\.io'
    grep -rc '&#43;' docs/reference/instrumentation/zpages.md
    grep -rn '&#43;' docs | wc -l
    grep -on '\[[^]]*\]([^)]*)' docs/reference/instrumentation/zpages.md
    grep -n 'feature-state\|skew currentVersion\|v1\.35\|v1\.36' docs/reference/instrumentation/zpages.md
    sed -n '795,805p' docs/reference/access-authn-authz/rbac.md
    sed -n '134,142p' docs/reference/instrumentation/zpages.md
    grep -rn 'configz' docs
    diff <(sed -n '63,82p' blog/_posts/2025/zpages-for-kubernetes.md) <(sed -n '75,94p' docs/reference/instrumentation/zpages.md)
    grep -n ' $' docs/reference/instrumentation/zpages.md blog/_posts/2025/zpages-for-kubernetes.md
    ```

**Expect**

Step 1 should report a v1.35 server and two failures. `ComponentStatusz` and `ComponentFlagz` are
alpha and off at this version, so neither handler is registered and both `kubectl get --raw` calls
end in `Error from server (NotFound)`. The metric grep is the interesting half: the API server
publishes `kubernetes_feature_enabled` for every gate it knows about, including the two that are
off, so you can see both gates and their `ALPHA` stage on a cluster where the endpoint that would
report them does not exist. That is the third of the four methods at
`configure-feature-gates.md:180-234` answering a question the fourth cannot yet be asked.

Step 2 should return `404` three times, and the three status lines should be identical apart from
the path. The `Accept` header makes no difference because there is nothing to negotiate with:
content negotiation happens inside a handler, and at v1.35 with the gates off there is no handler.
Keep these three lines. They are the control for step 4, and they are the reason a 406 in a later
step means something — a refusal proves the endpoint is there.

Step 3 takes the API server down and brings it back, usually inside a minute. The `until` loop is
the only reliable signal; the static Pod is recreated with a new UID, so watching the old one is
watching the wrong object. If `kubectl version` never comes back, the manifest is malformed: restore
it from `/tmp/bw-apiserver.yaml.bak` over `ssh` and check the indentation of the inserted line,
which must sit at the same depth as the other `- --flag` entries under `command`.

Step 4 is the measurement the whole exercise turns on, and the pin cannot tell you the answer. The
plain text request should now return `200` with `text/plain`, which confirms the endpoint is live
and confirms the compatibility promise at `:33`. Then one of `v1alpha1` and `v1beta1` returns `200
application/json` and the other returns `406`. Predict which before you run it. If `v1alpha1`
answers, the post documented its own release correctly and the break is real and datable to 1.36,
when the schema was renamed; if `v1beta1` answers, then `zpages.md:59-61` is right that the
structured format arrived at v1.35 carrying that schema, and the post was wrong on the day it was
published. Both outcomes are findings and the pinned tree supports both readings.

Step 5 should print `406` four times and `200` once. Dropping `g`, dropping `v` and dropping `as`
each produce the refusal the note at `:68-71` predicts, and so does bare `application/json`. The
fifth request is the one the note does not cover: `*/*` is what `curl` sends when you give it no
`-H` at all, and a server that refuses an under-specified `application/json` still answers `*/*`
with plain text. The rule is not "structured or nothing"; it is "if you name JSON, name all of it".
The post's promise at `:33` and the pin's note at `:68-71` are describing the two halves of that,
and neither says so.

Step 6 should turn the post's broken examples back into working ones. The stale header alone gives
`406`; the same header with `, text/plain` appended gives `200 text/plain`, because the server
cannot satisfy the first media type and can satisfy the second. The weighted form behaves
identically — `q` orders preferences, it does not create them. The fourth request, the current
header with the same fallback, should return `200 application/json`, because when the first type is
satisfiable it wins. Every one of the post's four `Accept` headers is one comma from being useful at
the pin, and the two pages that document these endpoints never mention the idiom; the page that does
is one this one does not link.

Step 7 should show a JSON object whose keys are the eight the Go struct at `:99-132` declares, minus
whichever are `omitempty` and empty. Expect `minimumCompatibilityVersion` to be absent: it is
optional, it appears in no published sample, and a v1.35 binary predates the v1beta1 struct that
declares it. The `flags` map should be very much larger than the six keys in either sample — a
kubeadm API server is started with more than twenty flags — so the interesting question is which of
the pin's two invented keys are in it. `anonymous-auth` should be there. Whether
`default-watch-cache-size` is depends on whether `/flagz` reports defaults as well as flags, which
`zpages.md:139` asserts and which this is the cheapest way to check.

Step 8 should answer `no` for `/statusz` and `/flagz` and `yes` for `/healthz`, `/livez`, `/readyz`
and `/metrics`, which is `rbac.md:801` read back by the authorizer. Your own kubeconfig answers
`yes` to all seven, because it is in `system:masters`, which is the same reason the post's `curl`
works. The `nonResourceURLs` printout is the table row in machine form: compare it line by line with
the prose at `:801`, and note that `/version` is reachable by a different default role entirely. The
binding query tells you whether anyone is in the group on a kubeadm cluster, which the second column
of that table row claims and which is worth confirming rather than assuming.

Step 9 should have methods one, three and four agree that both gates are on, and disagree about what
they are agreeing to. The manifest and `/flagz` both return the literal string you typed —
`ComponentStatusz=true,ComponentFlagz=true` — because `/flagz` reports the command line. The metric
reports resolved state, one series per gate, for every gate the binary knows. That is the difference
the task page does not state: method four sees what you set, method three sees what the component
decided, and for a gate that is on by default and absent from the command line only one of them has
anything to say. At v1.36 and later, where these two gates are on by default, that gap closes over
the very feature being used to inspect it.

Step 10 is the offline census and every count is exact. Four files mention `statusz` or `flagz`. The
un-prefixed `config.k8s.io` group appears in ten lines, all in one file, all at `v1beta1`. `&#43;`
appears once in the whole of `docs`. The link extraction should return seven links of which five are
anchors into the page itself. The version grep should show `v1.36` twice, `v1.35` once and two `skew
currentVersion` shortcodes that render as v1.37. The `diff` of the two JSON samples should be one
line — the `apiVersion` — which is the cleanest possible evidence that the reference page's sample
is the blog post's sample, and that whoever moved it across read one line of it.

**Read on**

11. [The 2017 RBAC row](../2017/06-using-rbac-generally-available-18.md), which uses `/flagz` as an
    instrument rather than a subject: it reads the running authorizer chain off a cluster whose
    manifest and documentation disagree, and prints the `ComponentFlagz` ladder to explain why the
    endpoint is there. On a v1.35 lab its step 8 needs this exercise's step 3 to have run first,
    which is the ladder's alpha rung showing up as a dependency between two exercises nine years
    apart.

12. [The 2023 node log query row](../2023/03-node-log-query-alpha.md), for the kubelet half of
    everything above. It reads `kubelet-authn-authz.md:99-134` in full — the path-to-subresource
    table, the `proxy` catch-all, and which endpoints were lifted out of it — which is where you
    look to find that `/statusz` and `/flagz` were never lifted. It also settles the
    `system:masters` group of the certificate the post's `curl` uses, at `:103-104` and `:371-374`.

13. [The 2016 OpenAPI row](../2016/15-kubernetes-supports-openapi.md), for content negotiation as a
    subject: what `api-concepts.md:140` says the API serves, what a default cluster actually serves,
    and the gap between the two. z-pages borrow that machinery wholesale — same `as`, `g` and `v`
    parameters, same 406 — for an endpoint that is not an API object at all.

14. [The 2020 structured logging row](../2020/08-kubernetes-1-19-introducing-structured-logs.md),
    the other post about making a component's human-readable output machine-parseable without
    breaking the humans. Read the two together for the shape of the problem: an opt-in format, a
    compatibility promise about the old one, and a schema that has to be versioned because somebody
    will parse it.

15. *Unanswerable from the pin.* Whether `config.k8s.io/v1alpha1` was ever served. The post's
    authors wrote `v1alpha1` four times in the release announcement for v1.35; the pinned reference
    says the structured format started at v1.35 and prints `v1beta1` for it, in a sample copied from
    that same post. One of those is a record of what shipped and the other is a page that was edited
    later, and a one-commit sparse checkout cannot say which is which. Step 4 tells you what one
    v1.35 binary answers, which is evidence about that binary and not about the history.

**Teardown**

```sh
ssh zain@10.10.10.180 "sudo cp /tmp/bw-apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml \
  && sudo rm -f /tmp/bw-apiserver.yaml.bak /tmp/zp.sh /tmp/zp.out"
until kubectl version >/dev/null 2>&1; do sleep 5; done
kubectl -n kube-system get pods -l component=kube-apiserver
rm -rf /tmp/bw-zpages
```
