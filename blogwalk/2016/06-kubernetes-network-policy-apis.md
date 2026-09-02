<a id="kubernetes-network-policy-apis"></a>
# The annotation in this post still applies cleanly and has never done anything, and the architecture it describes is now on the API's own list of what it cannot do

**Post** — [SIG-Networking: Kubernetes Network Policy APIs Coming in 1.3](https://kubernetes.io/blog/2016/04/kubernetes-network-policy-apis/),
2016-04-18, Kubernetes v1.2 — a forecast rather than a release note. It describes an experimental
API you could run on v1.2 and a beta API arriving in v1.3, and it is the only post in this year's
`walk` set written entirely in the future tense.

**As written** — the problem is stated as a default: *"the open access network policy of Kubernetes
is not suitable for applications that need more precise control over the traffic that accesses a pod
or service."* The design is borrowed from IaaS security groups, and the mechanism is stated in one
sentence: *"The basic idea is that if isolation were enabled on a per namespace basis, then specific
pods would be selected where specific traffic types would be allowed."*

To have it on v1.2, before the API existed, you extend the API server yourself:

> The simplest way to quickly support this experimental API is in the form of a ThirdPartyResource
> extension to the API Server, which is possible today in Kubernetes 1.2.

```
kind: ThirdPartyResource
apiVersion: extensions/v1beta1
metadata:
 &nbsp;name: network-policy.net.alpha.kubernetes.io
description: "Network policy specification"
versions:
- name: v1alpha1
```

```
$kubectl create -f third-party-res-def.yaml
```

which the post says *"will create an API endpoint (one for each namespace)"*:

```
/net.alpha.kubernetes.io/v1alpha1/namespace/default/networkpolicys/
```

Isolation is then switched on per namespace, by annotation:

> Network isolation is off by default so that all pods can communicate as they normally do.
> However, it's important to know that once network isolation is enabled, all traffic to all pods,
> in all namespaces is blocked, which means that enabling isolation is going to change the behavior
> of your pods

```
net.alpha.kubernetes.io/network-isolation: [on | off]
```

and the policy itself is a POST, with a schema of its own:

```
POST /apis/net.alpha.kubernetes.io/v1alpha1/namespaces/tenant-a/networkpolicys/

{
"kind": "NetworkPolicy",
"metadata": { "name": "pol1" },
"spec": {
  "allowIncoming": {
    "from": [ { "pods": { "segment": "frontend" } } ],
    "toPorts": [ { "port": 80, "protocol": "TCP" } ]
  },
  "podSelector": { "segment": "backend" }
}
}
```

The enforcement is somebody else's: *"External policy control software (specifics vary across
implementations) will watch the new API endpoint for pods being created and/or new policies being
applied."* Five vendors are named as having it working or in progress.

**As it runs now** — this post's fates split cleanly into three, and the middle one is the reason
the post earns a `walk` rather than a `dated`.

1. **Gone without a trace.** `ThirdPartyResource` appears **zero** times in the pinned
   documentation tree; so does the group name `net.alpha.kubernetes.io`, so does the string
   `network-isolation`, so does the field name `allowIncoming`, and so does the plural
   `networkpolicys` the post's URLs use. Five strings, five zeroes. Neither of the post's two
   endpoint paths exists, and they do not even agree with each other — the first has no `/apis`
   prefix and writes `namespace` singular, the second has `/apis` and writes `namespaces`. Nothing
   in the post's request layer survives.
2. **Applies cleanly, does nothing, and says nothing.** The annotation is the exception, and it is
   the whole exercise. `net.alpha.kubernetes.io/network-isolation: on` is a namespace annotation,
   and annotations are opaque strings that the API server stores and does not interpret. So the
   post's isolation switch can be set today, on a current cluster, with no error, no warning, and no
   effect — and there has never been a release in which setting it would have produced a diagnostic.
   A reader following this post on a v1.37 cluster gets a namespace that reports isolation is on and
   traffic that flows exactly as before.
3. **Delivered, under another name, with a different shape.** The API the post forecasts did ship:
   `NetworkPolicy` in `networking.k8s.io/v1`. Exactly one identifier survived the redesign —
   `podSelector` — and even that changed meaning, from a bare label map to a `LabelSelector`
   requiring `matchLabels`. `allowIncoming` became `ingress`, `from` kept its name one level deeper,
   `pods` became `podSelector`, `toPorts` became `ports`, and two things the post has no vocabulary
   for were added: `policyTypes`, which decides whether a policy isolates at all, and `egress`,
   which the post's ingress-only model cannot express.

The post's most confident sentence is also its least accurate, and it was wrong when published:
isolation is described as *per namespace* two paragraphs before it is described as blocking *"all
traffic to all pods, in all namespaces."* Those cannot both be true. At the pin the per-namespace
reading is the one that survived, and the all-namespaces reading is explicitly listed as a thing the
API cannot do — see below.

**The diff, and why** — the plan happened, and the architecture did not. That distinction is the
payload, and it is visible in three places in the pinned tree.

**The extension mechanism was replaced.** `ThirdPartyResource` was the 2016 way to add a kind to the
API server, and it left no trace in the documentation; its successor is
`CustomResourceDefinition`, which is a different object with a different validation story. This is
the ordinary fate of an extension point, and it is not the interesting part.

**The delivery model was disowned.** The post's architecture is: Kubernetes holds the policy
objects, and third-party controllers watch and fulfil them. The pin's NetworkPolicy page has a
section titled *What you can't do with network policies (at least, not yet)*, and two of its ten
bullets describe this post:

> - Creation or management of "Policy requests" that are fulfilled by a third party.
> - Default policies which are applied to all namespaces or pods (there are some third party
>   Kubernetes distributions and projects which can do this).

The first is the post's entire mechanism. The second is the post's isolation annotation. Both are
listed, ten years later, as functionality that *"does not exist in the NetworkPolicy API."* The
project did not reject the use cases; it declined to own the plumbing. What it kept is narrower and
more honest: a namespaced object with a fixed schema, plus a rule that *"Creating a NetworkPolicy
resource without a controller that implements it will have no effect."*

**The feedback path was attempted and withdrawn.** This is the part a reader of the post could not
have predicted and cannot find out from the post's successors either. The post assumes an operator
can tell that policy is being enforced, because a controller is visibly watching an endpoint. On the
current API you cannot, and the pin says so in one sentence:

> Every created NetworkPolicy will be handled by a network plugin eventually, but there is no way to
> tell from the Kubernetes API when exactly that happens.

Kubernetes tried to close that gap and stopped:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.24 – v1.27 |

`NetworkPolicyStatus` declares `removed: true` in its gate file and has exactly one stage. It sat
alpha for four releases, off by default the whole time, and was taken away without ever being
promoted — a ladder with one rung and no landing. What it would have added was a `status` on the
NetworkPolicy object, which is the only place a plugin could report back that a policy was
programmed. Its removal is why the sentence above is still true, and why the *Do* section below
cannot answer "is this policy enforced?" from the API and has to measure traffic instead.

Read against the post, that is a reversal of the post's own claim to visibility. The reader is told
that a controller *"will recognize the change and a controller will respond by configuring the
interface and applying the policy"*, with a diagram of the loop. The loop exists. The half of it
that reports back does not, and the field that would have carried the report is in the removed-gate
list. Three more of the *can't do* bullets say the same thing from other angles:
*"Advanced policy querying and reachability tooling"*, *"The ability to log network security
events (for example connections that are blocked or accepted)"*, and *"The ability to explicitly
deny policies."*

One thing did climb the ladder, and it is worth tabling for the contrast:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.21 – v1.21 |
| beta | `true` | — | v1.22 – v1.24 |
| stable | `true` | — | v1.25 – v1.26 |

`NetworkPolicyEndPort` is also `removed: true`, but for the opposite reason: it went alpha to stable
in four releases and the gate was retired because `endPort` became unconditional. The post's
`toPorts: [{ "port": 80, "protocol": "TCP" }]` can now name a range. And even here the enforcement
gap shows: the pin warns that if your plugin *"does not support the `endPort` field and you specify
a NetworkPolicy with that, the policy will be applied only for the single `port` field"* — a
narrower policy than you wrote, applied silently, with no status field to tell you. Two gates, both
removed, one because the feature won and one because it lost, and only the file-level `removed:
true` distinguishes them.

The isolation model itself is the one place the post's instinct was right and its vocabulary was
not. The pin's default-deny recipe is a policy object rather than a switch:

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

An empty `podSelector` selects every pod in the namespace, and naming `Ingress` in `policyTypes` is
what makes those pods isolated. So *"isolation enabled on a per namespace basis"* survives as an
idiom you construct rather than a flag you set, and the construction is more precise than the flag
was: the post's `[on | off]` has no way to say *ingress only*, and no way to say *egress*, which the
pin's four-way recipe list does — and which carries its own trap the post's model could not have,
that *"A default deny-all egress policy also blocks DNS traffic."*

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), fresh. One node is the right size and
the reason matters: this exercise installs no policy-enforcing network plugin, because a plugin that
implements NetworkPolicy is a third-party component nothing in this tree pins — the same line
[03](03-kubernetes-1-2-and-simplifying-advanced-networking-with-ingress.md) draws at the Ingress
controller. So *Do* does not assume the lab enforces anything; it measures whether it does, which is
the only instrument the API leaves you. Bring the guest up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, install Kubernetes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), then
`ssh zain@10.10.10.180`.

**Do**

1. Write the post's ThirdPartyResource into `tpr.yaml` exactly as the published page renders it,
   including the `&nbsp;` before `name`, and apply it. Then delete the entity, leaving one space of
   indentation, and apply again. Two different refusals. Then find what replaced the kind:
   `kubectl api-resources --api-group=apiextensions.k8s.io`.

2. Ask the API server for both of the post's endpoints, exactly as printed:

   ```
   kubectl get --raw '/net.alpha.kubernetes.io/v1alpha1/namespace/default/networkpolicys/'
   kubectl get --raw '/apis/net.alpha.kubernetes.io/v1alpha1/namespaces/tenant-a/networkpolicys/'
   kubectl get --raw '/apis' | tr ',' '\n' | grep -i net
   ```

   The third command lists the groups that do exist. Write down the group name that carries
   NetworkPolicy today and how many path segments differ from the post's.

3. Set the post's isolation switch and then prove what it did.

   ```
   kubectl create namespace tenant-a
   kubectl annotate namespace tenant-a 'net.alpha.kubernetes.io/network-isolation=on'
   kubectl get namespace tenant-a -o jsonpath='{.metadata.annotations}{"\n"}'
   kubectl get events -n tenant-a
   kubectl get networkpolicy -n tenant-a
   ```

   Record the exit status of the annotate command and everything the cluster has to say about it
   afterwards.

4. Put two pods in that namespace and measure the traffic the annotation is supposed to have
   blocked:

   ```
   kubectl -n tenant-a run backend --image=registry.k8s.io/e2e-test-images/agnhost:2.53 \
     --labels=segment=backend --command -- /agnhost netexec --http-port=8080
   kubectl -n tenant-a run frontend --labels=segment=frontend \
     --image=registry.k8s.io/e2e-test-images/agnhost:2.53 --command -- sleep 3600
   kubectl -n tenant-a wait --for=condition=Ready pod/backend pod/frontend --timeout=120s
   BACKEND=$(kubectl -n tenant-a get pod backend -o jsonpath='{.status.podIP}')
   kubectl -n tenant-a exec frontend -- /agnhost connect --timeout=5s "$BACKEND:8080"
   ```

   This is the baseline. Keep the exact output.

5. Send the post's policy body to the current API. Save the JSON exactly as printed, add
   `"apiVersion": "networking.k8s.io/v1"` and `"metadata": {"name": "pol1", "namespace":
   "tenant-a"}`, and `kubectl apply -f pol1.json`. Then run it again with `--validate=warn` and
   compare, as in [05](05-configuration-management-with-containers.md). Count how many of the
   post's field names the server objects to.

6. Now write the policy the post was describing, in the schema that exists, and apply it:

   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: pol1
     namespace: tenant-a
   spec:
     podSelector:
       matchLabels:
         segment: backend
     policyTypes:
     - Ingress
     ingress:
     - from:
       - podSelector:
           matchLabels:
             segment: frontend
       ports:
       - protocol: TCP
         port: 80
   ```

   Note that the post's port was 80 and your backend listens on 8080. Leave it at 80 for now: the
   mismatch is deliberate and step 8 uses it.

7. Add the pin's default-deny for the namespace, which is what the post's annotation was reaching
   for, and re-measure:

   ```
   kubectl apply -n tenant-a -f - <<'EOF'
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: default-deny-ingress
   spec:
     podSelector: {}
     policyTypes:
     - Ingress
   EOF
   kubectl -n tenant-a exec frontend -- /agnhost connect --timeout=5s "$BACKEND:8080"
   ```

   Compare with step 4. Whatever happens, the next step is the same.

8. Ask the API whether the policies are in force, by every route it offers:

   ```
   kubectl get networkpolicy -n tenant-a -o yaml | grep -c status
   kubectl explain networkpolicy.status
   kubectl describe networkpolicy default-deny-ingress -n tenant-a
   kubectl get events -n tenant-a --field-selector involvedObject.kind=NetworkPolicy
   ```

   Then answer the question step 7 raised — enforced or not — and say which of these four commands
   contributed to the answer.

9. Write a policy with the field the post's `toPorts` became, and one the post could not have
   written at all:

   ```
   kubectl patch networkpolicy pol1 -n tenant-a --type json \
     -p '[{"op":"replace","path":"/spec/ingress/0/ports/0","value":{"protocol":"TCP","port":8080,"endPort":8090}}]'
   kubectl patch networkpolicy default-deny-ingress -n tenant-a --type json \
     -p '[{"op":"add","path":"/spec/policyTypes/-","value":"Egress"}]'
   kubectl -n tenant-a exec frontend -- /agnhost dns-suffix
   ```

   The `endPort` patch names a range. The second turns the namespace's default-deny into the pin's
   `default-deny-all`. The third asks the pod to resolve DNS afterwards.

10. Read the pin's section *What you can't do with network policies (at least, not yet)* and mark
    which of its ten bullets the post either assumed or promised. Then say which single bullet, if
    it were removed from that list, would have made this post's architecture correct.

**Expect** — step 1: the first apply fails in the YAML parser, not in Kubernetes — `&nbsp;` is not a
space and the mapping does not form. The second gets as far as the API server and returns
`no matches for kind "ThirdPartyResource" in version "extensions/v1beta1"`, the same refusal shape as
[03](03-kubernetes-1-2-and-simplifying-advanced-networking-with-ingress.md)'s Ingress and
[04](04-using-deployment-objects-with.md)'s Deployment, from a third unrelated kind. `api-resources`
lists `customresourcedefinitions`.

Step 2: both raw gets return a 404 with a `NotFound` status body; note that the error is about the
*path*, not about the group, because the API server has no reason to believe either was ever real.
The group that answers is `networking.k8s.io`, and `/apis/networking.k8s.io/v1` is three segments
where the post wrote five.

Step 3: `namespace/tenant-a annotated`, exit status 0. The annotation is stored verbatim and
readable back. No events, no policies, nothing else. This is the finding: the post's isolation
switch is a string, and a string is what the cluster keeps.

Step 4: `agnhost connect` succeeds and prints nothing on success. Traffic flows between two pods in
a namespace that claims isolation is on.

Step 5: the strict apply is rejected with `unknown field` complaints. Expect `spec.allowIncoming`
to be named, and expect `spec.podSelector` to be rejected too — the post writes it as a bare label
map and the API wants a `LabelSelector`, so the one identifier that survived the redesign still
fails on its value. Four field names went into that request and the count the server objects to is
the measure of how much of the schema is left.

Step 6: accepted. A policy naming port 80, selecting a backend that listens on 8080.

Step 7: on this lab, most likely unchanged — `agnhost connect` still succeeds, because the node
baseline installs a plugin for connectivity and nothing was installed to enforce policy. If instead
the connection now times out, the plugin in front of you does enforce, and you have measured
something the API would not have told you either way. Either outcome is the exercise; only being
told the answer in advance would not be.

Step 8: `grep -c status` returns 0. `kubectl explain networkpolicy.status` reports no such field.
`describe` shows the spec and no conditions. There are no events. All four commands agree, and none
of them answered the question — which is what the removed `NetworkPolicyStatus` gate was for, and
what the pin means by *"there is no way to tell from the Kubernetes API when exactly that happens."*

Step 9: both patches are accepted. `endPort: 8090` is stored whether or not anything honours it, and
the pin's warning is that an unsupporting plugin narrows it to `port: 8080` silently. After the
`Egress` addition, `agnhost dns-suffix` either resolves as before — non-enforcement again — or
hangs, which is the pin's caution about DNS arriving in practice rather than in a note.

Step 10: at minimum two bullets, *"Creation or management of 'Policy requests' that are fulfilled by
a third party"* and *"Default policies which are applied to all namespaces or pods"*, and a case can
be made for two more.

**Read on** — the pin's
[NetworkPolicy concept page](https://kubernetes.io/docs/concepts/services-networking/network-policies/),
the section *Pod lifecycle*: read the two numbered guarantees about when isolation and allow rules
take effect, and answer one question — a pod is created at the same moment as the policy that
selects it, and the pin says it *"may have no network connectivity at all when it is first
started"*; what does that oblige an application author to do, and which of the post's five named
vendors would that obligation have been invisible to? Then compare the pin's
[`endPort` note](https://kubernetes.io/docs/concepts/services-networking/network-policies/#targeting-a-range-of-ports)
with the removed `NetworkPolicyStatus` gate and answer a harder one: a policy you wrote as a range
is applied as a single port by a plugin that does not support ranges, and no field reports it — name
every way you could find out, and then say which of them scales past one cluster.

**Teardown** — `kubectl delete namespace tenant-a` takes the pods, both policies and the annotation
with it. `kubectl delete -f tpr.yaml --ignore-not-found` in case either apply in step 1 partially
succeeded. Take the guest down with [teardown](../../strands/lab-topologies.md#teardown).
