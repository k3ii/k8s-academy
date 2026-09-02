<a id="enforcing-network-policies-in-kubernetes"></a>
# The first of this post's two manifests is still exactly right, the second stopped being right in the release the post was written to announce, and on the cluster this curriculum builds neither of them does anything at all — the object is stored, the command reports success, and the API has no field anywhere in which to say that nothing is enforcing it

**Post** — [Enforcing Network Policies in Kubernetes](https://kubernetes.io/blog/2017/10/enforcing-network-policies-in-kubernetes/),
2017-10-30, Kubernetes v1.7 by the post's own sentence and v1.8 by its editor's note. Ahmet Alp
Balkan (Google). 119 lines, two manifests, two diagrams hosted on `googleusercontent.com`, and
another instalment of the same *Five Days of Kubernetes 1.8* series that carried
[the RBAC post](06-using-rbac-generally-available-18.md) two days earlier.

The census row for this post promises the `net.beta.kubernetes.io/network-policy` annotation. That
divergence is [the 2016 network policy exercise](../2016/06-kubernetes-network-policy-apis.md)'s
whole subject and it is finished there; this post never mentions the annotation, which is the
correct behaviour for a post written a release after the annotation model was retired. See the
[loose row](#loose-row) note at the end.

**As written** — the post is short and its shape is four claims and two examples.

The claim about the default: *"In a Kubernetes cluster configured with default settings, all pods can
discover and communicate with each other without any restrictions"* (line 17), and NetworkPolicy is
the object *"lets you allow and block traffic to pods."* Then the analogy the whole post rests on:
*"Networking policy corresponds to the Security Groups concepts in the Virtual Machines world"*
(line 19).

The claim about installation (line 24): *"Networking Policies are implemented by networking plugins.
These plugins typically install an overlay network in your cluster to enforce the Network Policies
configured."* Three plugins are named and linked — Calico, Romana, Weave Net — and then GKE, whose
one-line recipe sits unfenced in the running text at line 28:
`gcloud beta container clusters create --enable-network-policy`. Line 30 is an empty `##`.

The claim about selectors (line 36), two clauses about the peer field: *"If you omit this field, it
matches to no pods; therefore, no pods are allowed. If you specify an empty pod selector, it matches
to all pods; therefore, all pods are allowed."*

Then the two examples. The first *"blocks all in-cluster traffic to a set of web server pods, except
the pods allowed by the policy configuration"* (line 39) and prints a NetworkPolicy named
`access-nginx` at `networking.k8s.io/v1`, selecting `app: nginx`, with one ingress rule admitting
`app: foo`. The second (line 80): *"If you specify the spec.podSelector field as empty, the set of
pods the network policy matches to all pods in the namespace, blocking all traffic between pods by
default."* Its manifest is five lines and ends at a bare `podSelector:` with no value; the fence
closes there.

The post closes with five further capabilities, of which the first is *"Egress network policies:
Introduced in Kubernetes 1.8, you can restrict your workloads from establishing connections to
resources outside specified IP ranges"* (line 108), and four links, two of them to the author's own
material.

**As it runs now** — sort the outcomes, because this post sorts unusually for this tree.

*Nothing errors.* Not one command, not one manifest. `networking.k8s.io/v1` is the group-version a
v1.37 API server still serves, and both manifests apply into it without translation. This is the
first post in 2017's walk whose YAML needs no repair at all, and the reason it is interesting is
that acceptance is the whole problem.

*The first manifest is the pinned documentation's own example.* `nginx-policy.yaml`, applied by
`docs/tasks/administer-cluster/declare-network-policy.md:88`, is the post's manifest with one label
changed: the peer selector reads `access: "true"` where the post writes `app: foo`. The quotation
marks in the pin's version are load-bearing — a label value is a string and unquoted `true` is a
YAML boolean — and the post's `app: foo` sidesteps that by accident. Everything else is identical,
down to the object's name.

*The second manifest is valid, and shorter than it looks.* A reader today sees a truncated fence and
reaches to repair it, and there is nothing to repair.
`docs/reference/kubernetes-api/networking/network-policy-v1.md:77` says of `podSelector`: *"This
field is optional. If it is not specified, it defaults to an empty selector."* And an empty selector
*"matches all pods in the policy's namespace"*, which is what the post's sentence wants. The post's
five lines mean what the post says they mean, up to the comma.

*After the comma, the sentence is wrong, and it went wrong in v1.8.*
`docs/concepts/services-networking/network-policies.md:109-114` sets out the default for the field
the post's manifest does not write: *"If no `policyTypes` are specified on a NetworkPolicy then by
default `Ingress` will always be set and `Egress` will be set if the NetworkPolicy has any egress
rules."* The API reference (`network-policy-v1.md:81`) spells out the consequence for exactly this
manifest: a policy with no egress section *"would otherwise default to just [ "Ingress" ]"*. So the
post's `default-deny` isolates its namespace for ingress and leaves every outbound connection
untouched, while the sentence above it says *"blocking all traffic between pods by default."* In
v1.7, the release the post says made this feature stable, there was no egress to block and the
sentence was accurate. Egress arrived in v1.8 — the post's own line 108 announces it, three
paragraphs below the manifest it invalidated.

*And the rule at line 36 is wrong by a namespace.* The post's second clause — *"If you specify an
empty pod selector, it matches to all pods; therefore, all pods are allowed"* — is describing the
peer field, and `network-policies.md:147` says what a `podSelector` in a `from` section selects:
*"particular Pods in the same namespace as the NetworkPolicy"*. All pods in one namespace, not all
pods. The pin resolves the whole omit-versus-empty question the post's two clauses gesture at by
keeping two files side by side — `network-policy-allow-all-ingress.yaml`, which is `podSelector: {}`
with `ingress: - {}`, against `network-policy-default-deny-ingress.yaml`, which is the same object
with the `ingress` list absent. Neither of them is what line 36 describes, because line 36 is about
the inner selector and both of those are about the outer one.

*Nothing enforces either of them.* `network-policies.md:49`, the third sentence of the concept
page's Prerequisites: *"Creating a NetworkPolicy resource without a controller that implements it
will have no effect."* The note at `:92-95` repeats it for the page's own example: *"POSTing this to
the API server for your cluster will have no effect unless your chosen networking solution supports
network policy."* This curriculum installs Flannel, and
`docs/concepts/cluster-administration/addons.md:55-56` says of it, complete: *"[Flannel] is an
overlay network provider that can be used with Kubernetes."* Read that bullet against its
neighbours in the same list. Calico (`:25`) *"is a networking and network policy provider"*. Cilium
(`:33`) *"can enforce network policies on L3-L7"*. Weave Net (`:94`) *"provides networking and
network policy"*. Romana (`:86`) *"also supports the NetworkPolicy API"*. Canal (`:31-32`) *"unites
Flannel and Calico, providing networking and network policy"*. Flannel's is the bullet in that list
that makes no policy claim, and the omission is the entire behaviour this exercise observes.

That same list refutes both halves of the post's line 24. An overlay is not necessary — Calico's
bullet advertises *"non-overlay and overlay networks, with or without BGP"*. And an overlay is not
sufficient: Flannel is the pin's canonical overlay provider and enforces nothing. The two properties
the post welds together with the word *typically* are independent.

*Three of the post's four documentation links are gone.* All three provider pages —
`docs/tasks/configure-pod-container/calico-network-policy.md`, `…/romana-network-policy.md`,
`…/weave-network-policy.md` — are absent from the pin. The directory `configure-pod-container/`
exists and is large; it holds none of them. They moved to
`docs/tasks/administer-cluster/network-policy-provider/`, which holds exactly four pages: Antrea,
Calico, Cilium and Kube-router. `declare-network-policy.md:20-25` lists those same four as *"a
number of network providers that support NetworkPolicy"*. Neither Romana nor Weave Net is among
them, and neither has a page anywhere else in the tree. Romana survives as one bullet,
`addons.md:86-87`, linking to `github.com/romana`; Weave Net as `addons.md:94-96`, linking to
`github.com/rajch/weave`. Two of the post's three named providers now exist in the pinned
documentation only as entries in a list that `declare-network-policy.md:13` marks
`{{% thirdparty-content %}}`. The post's one surviving link is the one it files last, under
*Learn more*: the hands-on walkthrough.

*And the surviving provider page has almost nothing local in it.*
`network-policy-provider/calico-network-policy.md:15` opens by offering a choice — *"Decide whether
you want to deploy a cloud or local cluster"* — as though both were documented. The GKE half runs
`:19-41`: two shell examples, a verification command, and what to look for in its output. The local
half is `:43-46`, and this is all of it:

> To get a local single-host Calico cluster in fifteen minutes using kubeadm, refer to the
> [Calico Quickstart](https://projectcalico.docs.tigera.io/getting-started/kubernetes/).

Fifteen words and a hyperlink off the site. That is the pinned documentation's complete instruction
for getting policy enforcement onto the cluster you built by hand. This exercise therefore does not
demonstrate enforcement, and says so in its steps rather than sending you off-site mid-exercise to
get it.

**The diff, and why** — four of the template's five cases land in this post, which is one more than
[the previous exercise](06-using-rbac-generally-available-18.md) managed, and they land on different
sentences.

*Still right.* The first manifest, the group-version, and the port rule at line 111 — *"If you omit
this field, the policy matches all ports by default"* — which `network-policy-v1.md` still
describes the same way. A post can be nine years old and need no edit.

*Broke — and broke in the release it was written to announce.* Line 80's second clause. This is not
drift; drift takes years and arrives from outside. The editor's note files this post under *what's
new in Kubernetes 1.8*, and `policyTypes` and `egress` are what was new in Kubernetes 1.8. The
feature the post is celebrating is the feature that made the post's own sentence wrong, and the
post announces it at line 108 without noticing that line 80 is now half a claim. Nothing in the
tree ever corrected it, because a blog post is not corrected; the manifest simply keeps meaning
something narrower than the words above it every year that passes.

*A plan the project abandoned.* The obvious question a reader asks after step 4 below — *is anything
enforcing this?* — is one the API was briefly going to answer. `NetworkPolicyStatus` enabled *"the
`status` subresource for NetworkPolicy objects"*:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.24 – v1.27 |

The gate file declares `removed: true` and no `former_titles`. Alpha for four releases, off by
default in all four, never beta, gone. Search the pinned content tree for the string
`NetworkPolicyStatus` and there is exactly one hit: that gate file, which carries
`_build: {list: never, render: false}` and so is not published as a page at all. The object today
has four fields — `network-policy-v1.md:29-54` lists `apiVersion`, `kind`, `metadata`, `spec` — and
the Operations section that follows offers create, patch, put, delete, get and watch on a named
policy and no `status` subresource among them. So the question has no field to be asked in, and the
attempt to give it one is a stub the site does not render.

The concept page states the consequence in prose at `:386-387`: *"Every created NetworkPolicy will
be handled by a network plugin eventually, but there is no way to tell from the Kubernetes API when
exactly that happens."* And the whole section that sentence sits in opens, at `:364-365`, by scoping
itself: *"The following applies to clusters with a conformant networking plugin and a conformant
implementation of NetworkPolicy."* A concept page in the Kubernetes documentation, describing a
stable Kubernetes API, conditions one of its sections on the conformance of a component Kubernetes
does not ship and cannot inspect.

*Overtaken by stasis.* Two sentences in the generated API reference, at a v1.37 pin, end with the
words *"This field is beta-level in 1.8"*: the description of `egress` (`:69`) and the description of
`policyTypes` (`:81`). Both fields live in `networking.k8s.io/v1`, a stable group-version, and both
have been there since the release this post was written for. Thirty minor releases have shipped
since and the fields' own reference text still dates itself to 2017. The same shape appears one
heading over: `network-policies.md:444` is titled *"What you can't do with network policies (at
least, not yet)"* and its first line is *"As of Kubernetes {{< skew currentVersion >}}"* — a list
that re-dates itself to the current release on every build while its contents stay put, so *not
yet* renders as *not yet in v1.37* without anyone having looked.

The fifth thing is not one of the template's cases and is the reason the post reads oddly today. It
is titled *Enforcing* Network Policies in Kubernetes, and the pinned documentation's position is
that Kubernetes enforces nothing: `:49` again. Of the title's five words, *enforcing* is the one
Kubernetes does not supply.

<a id="stable"></a>
**And then the word *stable* itself.** `NetworkPolicyEndPort` gated the `endPort` field, which lets
one rule cover a port range:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.21 – v1.21 |
| beta | `true` | — | v1.22 – v1.24 |
| stable | `true` | — | v1.25 – v1.26 |

`removed: true`, no `former_titles`. A clean ladder: one release at alpha, three at beta, stable in
v1.25, gate retired after v1.26. `network-policies.md:289` marks the section
`state="stable"` for v1.25, and it is the only `feature-state` shortcode on the entire page —
NetworkPolicy itself carries none. And then the note at `:307-314`:

> Your cluster must be using a CNI plugin that supports the `endPort` field in NetworkPolicy
> specifications. If your network plugin does not support the `endPort` field and you specify a
> NetworkPolicy with that, the policy will be applied only for the single `port` field.

A stable field, its gate removed, which a conforming-enough plugin may silently ignore — not by
rejecting the policy but by narrowing it, so a rule you wrote for 32000–32768 protects one port and
reports nothing. Put that beside the two manifests below and the shape is the same at both scales.
*Stable* in Kubernetes names what the API server serves. It has never named what your cluster does.

**No gate** — NetworkPolicy has none. There is no `feature-gates/NetworkPolicy.md`; the six files
under `feature-gates/` whose names match *network* are `DefaultHostNetworkHostPortsInPodTemplates`,
`NetworkPolicyEndPort`, `NetworkPolicyStatus`, `PodHasNetworkCondition`,
`UserNamespacesHostNetworkSupport` and `WindowsHostNetwork`, and the two that name NetworkPolicy
gate *fields* of it, not the API. Both of those are transcribed above, because both are
load-bearing here: one is the abandoned answer to this exercise's central question, the other is
what *stable* turns out to mean.

**The instrument for dating this post's subject is the API reference's two beta-level clauses**
(`network-policy-v1.md:69` and `:81`), and they are the wrong instrument pointed at the right
release: they date the v1.8 fields, not the v1.7 graduation the post announces. Nothing in the
pinned tree dates NetworkPolicy's graduation at all. The nearest thing is
`declare-network-policy.md:6`, whose frontmatter reads `min-kubernetes-server-version: v1.8` — the
hands-on page for the feature requires a release later than the one the post says made it stable,
and gives no reason.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair): a control-plane node at
`10.10.10.130` and one worker at `10.10.10.131`. One node would carry every command below, and two
are wanted for two reasons. The first is that pod-to-pod traffic across nodes is what the overlay
actually forwards, so the probe that succeeds is succeeding over the thing the post claims does the
enforcing. The second is `network-policy-v1.md:73`, which allows traffic to a pod *"if the traffic
source is the pod's local node"* regardless of policy — an exemption restated as a limitation at
`network-policies.md:467-468` (*"nor do they have the ability to block access from their resident
node"*). Probing from the wrong place would be exempt even on a cluster that enforces, so which
node the target sits on is part of probing at all.

Provision with the five steps at [`#provision`](../../strands/lab-topologies.md#provision), then the
node baseline at [`#node-baseline-steps`](../../strands/lab-topologies.md#node-baseline-steps) on
both nodes, then `ssh zain@10.10.10.130`. Take the current minor; nothing below depends on the
version. The CNI is Flannel, this curriculum's default, and here it is also the subject — the
deviation [the previous exercise but one](05-kubeadm-v18-released.md) makes for its own purposes does
not carry forward.

Everything runs in `default`. The post names no namespace and the pin's walkthrough uses `default`
throughout.

**Do**

1. Stand up the target the pinned walkthrough uses, and find out where it landed:

   ```sh
   kubectl create deployment nginx --image=nginx
   kubectl expose deployment nginx --port=80
   kubectl get pod -l app=nginx -o wide
   ```

   These are `declare-network-policy.md:29-48` verbatim. Write down the `NODE` column. Call the
   other node the far node.

2. Put a probe pod on the far node and confirm the default the post describes at line 17:

   ```sh
   kubectl run probe --image=busybox --restart=Never \
     --overrides='{"spec":{"nodeName":"<the far node>"}}' -- sleep 3600
   kubectl get pod probe -o wide
   kubectl exec -ti probe -- wget --spider --timeout=1 nginx
   ```

   Expect `remote file exists`, matching the output printed at `declare-network-policy.md:79-82`.
   The connection crossed a node boundary over Flannel's overlay, and the probe pod carries no
   label any policy will look for. Keep this pod; every probe below reuses it.

3. Apply the post's first manifest exactly as printed. The post's fence puts a blank line between
   every line of YAML; leave them in, a blank line inside a mapping is legal:

   ```yaml
   kind: NetworkPolicy
   apiVersion: networking.k8s.io/v1
   metadata:
     name: access-nginx
   spec:
     podSelector:
       matchLabels:
         app: nginx
     ingress:
     - from:
       - podSelector:
           matchLabels:
             app: foo
   ```

   Expect `networkpolicy.networking.k8s.io/access-nginx created`.

4. Probe again, changing nothing else:

   ```sh
   kubectl exec -ti probe -- wget --spider --timeout=1 nginx
   ```

   This is the step at which the pinned walkthrough prints `wget: download timed out`
   (`declare-network-policy.md:122-125`). Its policy and yours differ only in which label the peer
   selector names, and `probe` carries neither. Record what you actually get, and record that the
   Kubernetes documentation's own hands-on task, run verbatim against a cluster built from the
   Kubernetes documentation's own kubeadm instructions, produces the opposite of its printed output.

5. Read what the server stored, and how it read it:

   ```sh
   kubectl get networkpolicy access-nginx -o yaml
   kubectl describe networkpolicy access-nginx
   ```

   `network-policies.md:190` recommends the second of these: *"When in doubt, use `kubectl describe`
   to see how Kubernetes has interpreted the policy."* Two things in the output you did not write:
   `policyTypes` came back as a one-element list, and there is no `status:` block. Note also that
   `describe` reports the rule, in full, with no reference to whether anything acts on it.

6. Ask the cluster the question step 4 raises, and find there is nowhere to ask it:

   ```sh
   kubectl explain networkpolicy
   kubectl get --raw /apis/networking.k8s.io/v1 | python3 -m json.tool | grep -A2 networkpolicies
   kubectl get events --field-selector involvedObject.kind=NetworkPolicy
   ```

   From the first, list the top-level fields and compare against the four at
   `network-policy-v1.md:29-54`. From the second, say whether a `networkpolicies/status` resource
   appears beside `networkpolicies`. From the third, expect no rows. Then, in the pinned checkout:

   ```sh
   grep -rn "NetworkPolicyStatus" /path/to/pinned/website/content/en | wc -l
   ```

   One hit. Open it and read its `stages:` list and its `_build:` block against the ladder above.

7. Apply the post's second manifest exactly as printed, ending where the post's fence ends:

   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: default-deny
   spec:
     podSelector:
   ```

   Expect it to be created, then read it back:

   ```sh
   kubectl get networkpolicy default-deny -o yaml
   ```

   The bare `podSelector:` came back as `podSelector: {}` — the null was defaulted, per
   `network-policy-v1.md:77` — and `policyTypes` came back with one element. Write down which one.

8. Put the post's sentence beside the two manifests the pinned documentation keeps for the two
   things that sentence could mean. `network-policy-default-deny-ingress.yaml`, used at
   `network-policies.md:214-222`:

   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: default-deny-ingress
   spec:
     podSelector: {}
     policyTypes:
     - Ingress
   ```

   and `network-policy-default-deny-all.yaml`, used at `:260-268`:

   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: default-deny-all
   spec:
     podSelector: {}
     policyTypes:
     - Ingress
     - Egress
   ```

   The object you created in step 7 is the first of these, field for field. The sentence above it in
   the post describes the second. `:222` says of the first, in one clause, what the post's sentence
   omits: *"This policy does not affect isolation for egress from any pod."* Find the line in the
   post that announces the release which opened that gap, and note how far it is from line 80.

9. Confirm that the gap between the objects and the behaviour is the documented design and not a
   fault in your cluster:

   ```sh
   kubectl get daemonset -A
   kubectl get networkpolicy
   ```

   The first names what is providing your pod network. The second lists two policies. Read
   `network-policies.md:45-49` and `:92-95` against the two of them, then follow the post's three
   provider links into the pinned checkout:

   ```sh
   ls /path/to/pinned/website/content/en/docs/tasks/configure-pod-container/ | grep -i policy
   ls /path/to/pinned/website/content/en/docs/tasks/administer-cluster/network-policy-provider/
   ```

   Expect nothing from the first command and four filenames from the second. Say which two of the
   post's three named providers are missing from that list, then find each of them in
   `addons.md` and say what is left of them there.

10. Delete both policies and probe a fourth time:

    ```sh
    kubectl delete networkpolicy access-nginx default-deny
    kubectl exec -ti probe -- wget --spider --timeout=1 nginx
    ```

    Write the four outputs — step 2, step 4, step 7's cluster with a default-deny in it, and this
    one — in a column. The cluster passed through four configurations: no policy, an allow-list
    policy naming a label nothing carries, a namespace-wide default-deny, and no policy again. Put
    a fifth column beside them for what `kubectl` reported at each transition.

**Expect** — every command in every step exits zero and every manifest is accepted. The probe
returns `remote file exists` at steps 2, 4 and 10, and would at step 7 too; four cluster
configurations, one output, and four success messages from `kubectl` reporting the four changes that
made no difference. `kubectl get networkpolicy` lists two objects that exist, are valid, are stored,
are readable, and are inert. `kubectl describe` prints their rules in detail and says nothing about
whether the rules apply. `kubectl explain networkpolicy` shows four fields and no `status`; the
discovery document lists `networkpolicies` and no `networkpolicies/status`; the event stream for the
kind is empty. The stored form of the post's second manifest differs from what the post's sentence
claims by exactly one absent element of `policyTypes`, which the server supplied on your behalf. The
pinned checkout returns no provider page at the three paths the post links, four pages at the path
they moved to, and one hit for `NetworkPolicyStatus` in a file the site does not render.

Nothing in this exercise shows a packet being dropped, and nothing in the pinned documentation shows
you how to make one drop on this cluster in more than fifteen words.

**Read on** — five questions, four answerable from the pin.

`network-policy-v1.md:73` allows ingress *"if the traffic source is the pod's local node"*, and
`network-policies.md:467-468` restates it from the other side. Of the probes you ran, which would
that exemption have covered on a cluster that enforces, and which would not? Then read
`:402-442` on `hostNetwork` pods — where behaviour is *"undefined, but it should be limited to 2
possibilities"* and the pin names which of the two is *"the most common implementation"* — and say
what `--overrides` you would have had to write in step 2 to make the probe exempt by accident.

The [note above](#stable) has `endPort` stable since v1.25 with its gate retired, and a plugin that
ignores it narrowing the policy rather than rejecting it. Which of the two components does *stable*
describe there? Find one other field in the pinned tree whose reference text carries a caveat of the
same shape, and say whether the caveat is on the field or on the plugin.

`network-policies.md:444-468` lists eleven things the API cannot do. The post's line 19 offers
Security Groups as the analogy for what NetworkPolicy is. Walk the eleven entries against that
analogy and say how many of them the analogy promises — start with `:464`, `:465` and `:463`, which
are logging, explicit deny, and asking whether it works at all.

`network-policies.md:361-400` says a pod may start unprotected, that allow rules may arrive after
isolation rules so that *"in the worst case, a newly created pod may have no network connectivity at
all when it is first started"*, and that there is no way to ask the API when handling completed.
Read it against the `NetworkPolicyStatus` ladder and say precisely which of those three sentences a
`status` subresource would have addressed and which it would not have touched.

The fifth is not answerable from the pin, and the pin's own answer to it is
`calico-network-policy.md:43-46`. If you take that off-site quickstart and get a policy-capable
plugin onto a cluster of your own, the question to carry with you is not whether step 4 changes —
it does — but which of the four outputs in step 10 changes, and whether the post's line 80 becomes
true or only half true.

**Teardown** — [`#teardown`](../../strands/lab-topologies.md#teardown). Step 10 already removed both
policies, and there was never anything to restore: nothing in this exercise altered how a single
packet was handled. What is left is an nginx Deployment, a Service, and the `probe` pod, which will
keep sleeping for an hour. `kubectl delete deployment nginx`, `kubectl delete service nginx` and
`kubectl delete pod probe` return the cluster to where step 1 found it, and the cluster is
reusable as it stands.

<a id="loose-row"></a>
**One note on the census.** 2017's row for this post reads *"the `net.beta.kubernetes.io/network-policy`
namespace annotation that used to switch isolation on is gone"* and offers that as the divergence to
walk. The annotation is the subject of
[the 2016 exercise](../2016/06-kubernetes-network-policy-apis.md), which carries it in full and
finds that it still applies cleanly and has never done anything. This post does not mention the
annotation, because by v1.7 there was nothing left to mention. Census rows are immutable, so the row
stands as written and this file walks the post rather than the row.
