<a id="configuring-private-dns-zones-upstream-nameservers-kubernetes"></a>
# Every JSON value in this post carries typographic quotation marks, so none of the four configurations could ever have been parsed, the last code fence is never closed so the post ends inside it, and the only name that survived the rewrite is the one that stopped describing what answers

**Post** — [Configuring Private DNS Zones and Upstream Nameservers in Kubernetes](https://kubernetes.io/blog/2017/04/configuring-private-dns-zones-upstream-nameservers-kubernetes/),
2017-04-04, Kubernetes v1.6 — Bowei Du and Matthew DeLio of Google, part of *Five Days of Kubernetes
1.6*. Two new keys in one ConfigMap, four worked examples, and two diagrams the argument leans on.

**As written** — the problem is stated in one sentence: *"Many users have existing domain name zones
that they would like to integrate into their Kubernetes DNS namespace"* — a hybrid-cloud `.corp`
domain, or a zone populated by something like Consul. The answer is a ConfigMap read by `kube-dns`.

First the existing behaviour:

> Kubernetes currently supports two DNS policies specified on a per-pod basis using the dnsPolicy
> flag: "Default" and "ClusterFirst". If dnsPolicy is not explicitly specified, then "ClusterFirst"
> is used

with `Default` inheriting the node's resolver configuration and `ClusterFirst` sending everything to
`kube-dns`, which answers the cluster suffix itself and forwards the rest *"to the upstream
nameserver inherited from the node"*. Then the reason the feature exists, which is the best paragraph
in the post:

> Before this feature, it was common to introduce stub domains by replacing the upstream DNS with a
> custom resolver. However, this caused the custom resolver itself to become a critical path for DNS
> resolution, where issues with scalability and availability may cause the cluster to lose DNS
> functionality. This feature allows the user to introduce custom resolution without taking over the
> entire resolution path.

The mechanism is two optional keys in a ConfigMap named `kube-dns`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kube-dns
  namespace: kube-system
data:
  stubDomains: |
    {“acme.local”: [“1.2.3.4”]}
  upstreamNameservers: |
    [“8.8.8.8”, “8.8.4.4”]
```

`stubDomains` is *"a JSON map using a DNS suffix key (e.g.; "acme.local") and a value consisting of a
JSON array of DNS IPs"*, and the post notes that *"The target nameserver may itself be a Kubernetes
service. For instance, you can run your own copy of dnsmasq to export custom DNS names into the
ClusterDNS namespace."* `upstreamNameservers` is *"a JSON array of DNS IPs"* which *"replace the
nameservers taken by default from the node's /etc/resolv.conf"*, with one hard limit: *"a maximum of
three upstream nameservers can be specified"*.

A three-row table gives the routing: `kubernetes.default.svc.cluster.local` to `kube-dns`,
`foo.acme.local` to the custom resolver at 1.2.3.4, `widget.com` to one of the two upstreams.

Two more examples follow. Example #1 integrates Consul at 10.150.0.1 with the suffix `.consul.local`,
using `stubDomains` alone. Example #2 forces all non-cluster lookups through 172.16.0.1, using
`upstreamNameservers` alone.

**As it runs now** — the ConfigMap the post is about does not exist, the mechanism that reads it does
not exist, and the object the post's `metadata` block names does exist as something else.

Start with the name, because it is the one thing that came through the rewrite intact:

> The CoreDNS Service is named `kube-dns` in the `metadata.name` field.
> The intent is to ensure greater interoperability with workloads that relied on the legacy
> `kube-dns` Service name to resolve addresses internal to the cluster.
> Using a Service named `kube-dns` abstracts away the implementation detail of which DNS provider is
> running behind that common name.
>
> — `docs/tasks/administer-cluster/dns-custom-nameservers.md:32-36`

The debugging page states the reason more bluntly — *"The Service for CoreDNS is named `kube-dns`,
for backward compatibility with the original kube-dns"* (`dns-debugging-resolution.md:172-173`) — and the
NodeLocal DNSCache page uses the name in a manifest without comment (`nodelocaldns.md:149`). So a
reader who types the post's `metadata.name` today addresses a real object in the real namespace. It
is a Service rather than a ConfigMap, it is served by different software, and the name is deliberate:
the pin calls it an abstraction over *"which DNS provider is running"*. The post's title says
`kube-dns` was the DNS server. At the pin `kube-dns` is a promise that something will answer.

Of the post's two keys, one is gone and one survives in exactly one place. `upstreamNameservers` has
zero occurrences anywhere under `docs/`. `stubDomains` has one, and it is not on the DNS
customisation page:

> The Corefile in the `node-local-dns` ConfigMap can be modified with the stubDomain configuration.
> Some cloud providers might not allow modifying the `node-local-dns` ConfigMap directly; in that
> case, a `kube-dns` ConfigMap in the format traditionally used by `kube-dns` can be used instead:
>
> ```yaml
> data:
>   stubDomains: |
>     {"abc.com" : ["1.2.3.4"], "my.cluster.local" : ["2.3.4.5"]}
> ```
>
> — `docs/tasks/administer-cluster/nodelocaldns.md:139-152`

*"The format traditionally used by `kube-dns`"* is the post's format, kept alive by the node-local
cache as a fallback for operators who cannot edit the cache's own ConfigMap. Note which of the two
IPs in it matches the post's: `1.2.3.4` is the post's own example address, carried across a decade
and two implementations. Note also that the pin's copy of the post's JSON has straight quotation
marks.

**Every JSON string in the post has typographic quotation marks.** Not one block, all four:
`{“acme.local”: [“1.2.3.4”]}`, `[“8.8.8.8”, “8.8.4.4”]`, `{“consul.local”: [“10.150.0.1”]}`,
`[“172.16.0.1”]`. JSON permits exactly one string delimiter, `"`, so none of the four values in this
post has ever been a JSON document. And there is no point at which a reader finds out: the ConfigMap
is valid, because `stubDomains` is a block scalar and a ConfigMap's `data` values are opaque strings
that the API server neither parses nor is able to parse. `kubectl apply` succeeds. The parse happens
later, inside another pod, and it reports to that pod's log.
[2016's StatefulSet exercise](../2016/14-statefulset-run-scale-stateful-applications-in-kubernetes.md)
found a field name surviving inside an annotation for the same structural reason.
[2017's scheduling exercise](02-advanced-scheduling-in-kubernetes.md) found the opposite: the same
class of typographic defect in a place the API server validates, where it is rejected in under a
second. The three cases differ only in how far the wrong character travels before anything notices,
and this is the furthest.

**The post's last code fence is never closed.** The source has five fence markers — an odd number —
at lines 30, 50, 88, 104 and 115. The fence at 115 opens Example #2's ConfigMap and nothing closes
it, so everything after `[“172.16.0.1”]` is inside the code block: the **Get involved** heading, the
invitation to join the community, the SIG-Network meeting time, the link back to the *Five Days*
index, and all five closing links. The post's final third renders as preformatted text with its links
inert. This is not decay either. A code fence is balanced or it is not, and this one has been
unbalanced since 2017-04-04.

Both diagrams are hosted on `bp.blogspot.com`, and the post's argument refers to them directly —
*"The diagram below shows the flow of DNS queries specified in the configuration above"* — while the
three-row table below restates the same routing in text. Neither image is in the website repository;
the post carries two links to a third-party host for each one, thumbnail and full size.

The `dnsPolicy` model has doubled. The post says *"Kubernetes currently supports two DNS policies"*
and the pin lists four (`dns-pod-service.md:251-274`): `Default`, `ClusterFirst`,
`ClusterFirstWithHostNet` and `None`. The third exists because the post's two-policy model has a
trap the post does not mention:

> "`ClusterFirstWithHostNet`": For Pods running with hostNetwork, you should explicitly set its DNS
> policy to "`ClusterFirstWithHostNet`". Otherwise, Pods running with hostNetwork and
> `"ClusterFirst"` will fallback to the behavior of the `"Default"` policy.
>
> — `dns-pod-service.md:261-264`

A pod that asks for `ClusterFirst` and sets `hostNetwork` silently gets `Default` instead, which
means none of the post's stub-domain routing applies to it. The one warning the post does give — that
`Default` is not the default — survives verbatim in the pin at `:276-277`.

The fourth policy is the post's feature moved from the cluster to the pod. `dnsPolicy: None` with
`dnsConfig` lets a single pod set its own `nameservers`, `searches` and `options`
(`dns-pod-service.md:309-330`), and it carries the post's limit exactly: *"There can be at most 3 IP
addresses specified"*. The post's *"maximum of three upstream nameservers"* was never a Kubernetes
decision — it is the resolver's, and it followed the feature from the cluster-wide ConfigMap to the
per-pod field without changing.

Now the strangest survival. The page that replaced the post reproduces the post's own examples, IPs
included:

> If a cluster operator has a [Consul](https://www.consul.io/) domain server located at "10.150.0.1",
> and all Consul names have the suffix ".consul.local". To configure it in CoreDNS, the cluster
> administrator creates the following stanza in the CoreDNS ConfigMap.
>
> ```
> consul.local:53 {
>     errors
>     cache 30
>     forward . 10.150.0.1
> }
> ```
>
> To explicitly force all non-cluster DNS lookups to go through a specific nameserver at 172.16.0.1,
> point the `forward` to the nameserver instead of `/etc/resolv.conf`
>
> — `docs/tasks/administer-cluster/dns-custom-nameservers.md:143-160`

Consul at 10.150.0.1 with the suffix `.consul.local` is Example #1. All non-cluster lookups through
172.16.0.1 is Example #2. Both addresses, both suffixes, and the second example's sentence is a near
paraphrase of the post's *"the cluster administrator wants to explicitly force all non-cluster DNS
lookups to go through their own nameserver at 172.16.0.1"*. The examples outlived the implementation
they were written for, and one of them appears in the pin twice more, at `:181` and `:190`, inside
the assembled Corefile.

Two smaller things on that page. It closes with a note about a step it never describes:

> CoreDNS does not support FQDNs for stub-domains and nameservers (eg: "ns.foo.com"). During
> translation, all FQDN nameservers will be omitted from the CoreDNS config.
>
> — `dns-custom-nameservers.md:194-197`

*"During translation"* is the only mention of translation on the page. Nothing above it describes a
translation, names a tool that performs one, or tells you what is being translated from — the reader
who needs that sentence is the reader holding the post's ConfigMap, and the sentence assumes they
already found the thing the page does not mention.

And the page misspells the value the post gets right. The post writes `dnsPolicy` values as
`"Default"` and `"ClusterFirst"`, capitalised, which is what the API accepts. The pin's page writes:

> If a Pod's `dnsPolicy` is set to `default`, it inherits the name resolution configuration from the
> node that the Pod runs on.
>
> — `dns-custom-nameservers.md:54`

Lowercase. `dns-pod-service.md:251` gives the enum as "`Default`", and step 4 finds out what the API
server does with the page's spelling.

**The diff, and why** — this post documents a mechanism that no longer exists, in a format that never
parsed, in a rendering that breaks a third of the way from the end, and it is still the ancestor of
the current documentation. Those four things are not in tension; they are the same story told from
four sides.

The mechanism died because of the paragraph the post is proudest of. Its argument against the old
approach was that replacing the upstream resolver *"caused the custom resolver itself to become a
critical path for DNS resolution"*, and its solution was to let `kube-dns` route by suffix, keeping
the cluster's own resolver in charge. That is a routing table, and a routing table expressed as two
JSON keys in a ConfigMap is a small special case of a routing table expressed as a config file. The
project replaced `kube-dns` with CoreDNS, whose Corefile is that general form: the post's
`stubDomains` map becomes a `consul.local:53 { ... }` server block and its `upstreamNameservers`
array becomes a `forward .` line, and the same file can also do rewriting, caching per zone, and
loop detection, which two JSON keys cannot express at all. The feature was not withdrawn. It was
absorbed into something whose configuration language is larger, which is why the examples survived
and the schema did not. A schema is a fixed set of questions; a config file is a language. Schemas
get replaced by languages and not the other way round.

The typographic quotes are the more interesting failure, because they show where the *validation
boundary* sits and how much distance a wrong character can cover inside an opaque string. A
ConfigMap's `data` is `map[string]string` by design — that is what makes it a general configuration
carrier — and the price of that generality is that the API server cannot check the contents. So four
malformed JSON documents passed authoring, review, publication, and a decade of readers copying them,
because the only component in a position to object is a DNS pod, and its objection goes into a log
nobody reads unless resolution is already broken. Everything the post shows you would apply cleanly.
The failure surfaces as *"DNS does not work"* one step removed from its cause, with no error at the
point of the mistake. Compare the `preferredDuringSchedulingIgnoredDuringExecution` block in
[the scheduling exercise](02-advanced-scheduling-in-kubernetes.md): identical class of author error,
caught instantly, because that field has a type.

The unclosed fence is the smallest of the four and the one that says most about the corpus. It is a
mechanical defect, detectable by counting, in a post on the project's own site, and nothing counted.
The blog has no gate. What the exercise directory this file sits in has, and what the blog does not,
is a script that fails when the numbers disagree.

And the name is the part to take away. `kube-dns` now denotes a Service whose entire purpose is that
its name does not tell you what is behind it — the pin says so in as many words: it *"abstracts away
the implementation detail of which DNS provider is running behind that common name"*. The post used
the name to mean the software. Preserving a name for compatibility means keeping the string and
discarding what it referred to, so every sentence written while the name still meant the software
becomes ambiguous the moment the swap happens, without being edited. There is no way to tell, from
this post's text alone, that `kube-dns` in `metadata.name` is now a live pointer to something else.

**The ladder** — the gates behind the per-pod form of the post's feature.

## CustomPodDNS
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.9 – v1.9 |
| beta | `true` | — | v1.10 – v1.13 |
| stable | `true` | — | v1.14 – v1.16 |

`removed: true`. Its description: *"Enable customizing the DNS settings for a Pod using its
`dnsConfig` property."* This is the post's feature moved down a level — from one ConfigMap the cluster
administrator owns to a field on every pod spec — and it arrived three releases after the post. One
release alpha, four beta, three stable, then the gate was deleted. `dnsPolicy: None` came with it,
which is why the post's *"two DNS policies"* is now four.

## ExpandedDNSConfig
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.22 – v1.25 |
| beta | `true` | — | v1.26 – v1.27 |
| stable | `true` | — | v1.28 – v1.29 |

`removed: true`. It raised the search-domain limits, and its description carries a condition the other
gates in this file do not: *"This feature requires container runtime support (Containerd: v1.5.6 or
higher, CRI-O: v1.22 or higher)."* A gate whose stage says `stable` and whose text says *only if your
runtime is new enough* — the ladder has no column for that, and the sentence is the only place it is
recorded. It is the reason the pin's search-domain limit is 32 (`dns-pod-service.md:324`) while the
nameserver limit stayed at the post's 3.

## RelaxedDNSSearchValidation
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.32 – v1.32 |
| beta | `true` | — | v1.33 – v1.33 |
| stable | `true` | `true` | v1.34 – |

Still present, `locked: true`, and one release per stage — the fastest promotion in this file.
*"Relax the server side validation for the DNS search string (`.spec.dnsConfig.searches`) for
containers. For example, with this gate enabled, it is okay to include the `_` character in the DNS
name search string."*

Read the three together. The post's feature was cluster-wide configuration with no gate at all, and
every gate that descends from it governs a *field on a pod*. Nine years of gates on this feature, and
none of them is about stub domains: they are about the per-pod escape hatch, its limits, and how
strictly its strings are checked. The character-level validation the post's own JSON needed is the
subject of the last gate, one field away.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), fresh. One node is enough, and the
post's own note explains why nothing else is needed: *"The target nameserver may itself be a
Kubernetes service."* The custom resolver, the stub-domain authority and the client all run as pods
on the single node. Bring the guest up with
[the five provision steps](../../strands/lab-topologies.md#provision), install Kubernetes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), and confirm the
node is Ready and the DNS pods are Running before starting.

Nothing here needs internet DNS. Where the post uses `8.8.8.8`, this exercise uses a resolver you
run, so every answer you get is one you can account for.

**Do**

1. Find the four objects the post's `metadata` block could be naming, and see which one exists:

   ```sh
   kubectl -n kube-system get svc kube-dns -o wide
   kubectl -n kube-system get configmap kube-dns
   kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}'
   kubectl -n kube-system get deploy -l k8s-app=kube-dns
   kubectl -n kube-system get pods -l k8s-app=kube-dns -o custom-columns='NAME:.metadata.name,IMAGE:.spec.containers[*].image'
   ```

   One `kube-dns` object exists and it is not the kind the post writes. Say what kind it is, what
   software the last command shows behind it, and quote the two sentences at
   `dns-custom-nameservers.md:33-36` that explain why the name did not change. Then say which of the
   five commands would have worked in 2017 and which would not.

2. Read the Corefile against the post's model. In the output of the third command above, find the
   line that does what the post calls forwarding to *"the upstream nameserver inherited from the
   node"*, and the block that answers the cluster suffix:

   ```sh
   kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}' | grep -n "forward\|kubernetes\|cache\|loop"
   cat /etc/resolv.conf
   ```

   Name the plugin that implements the post's upstream behaviour and say where it gets its
   nameservers from. Then map each of the post's three table rows onto one line of the Corefile, and
   report which row has no corresponding line.

3. Apply the post's ConfigMap exactly as printed, typographic quotes included, under a name that
   cannot collide:

   ```sh
   kubectl -n kube-system create configmap kube-dns-blogwalk --from-literal='stubDomains={“acme.local”: [“1.2.3.4”]}' --from-literal='upstreamNameservers=[“8.8.8.8”, “8.8.4.4”]'
   kubectl -n kube-system get configmap kube-dns-blogwalk -o jsonpath='{.data.stubDomains}{"\n"}'
   kubectl -n kube-system get configmap kube-dns-blogwalk -o jsonpath='{.data.stubDomains}' | python3 -c 'import json,sys; json.load(sys.stdin)'
   kubectl -n kube-system get configmap kube-dns-blogwalk -o jsonpath='{.data.stubDomains}' | od -c | head -2
   ```

   The object is accepted, stored byte for byte, and is not JSON. Record the parser's message and the
   octal bytes standing where `"` should be. Then answer the question the exercise turns on: name
   every component between your keyboard and a DNS answer that had an opportunity to reject this, and
   say why none of them took it.

4. Test the spelling on the page that replaced the post:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: dns-lower }
   spec:
     dnsPolicy: default
     containers: [{ name: c, image: registry.k8s.io/e2e-test-images/agnhost:2.53, command: ["sleep","3600"] }]
   EOF
   ```

   Record the error. Then apply it with the post's capitalisation and confirm it is accepted:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: dns-default }
   spec:
     dnsPolicy: Default
     containers: [{ name: c, image: registry.k8s.io/e2e-test-images/agnhost:2.53, command: ["sleep","3600"] }]
   EOF
   kubectl exec dns-default -- cat /etc/resolv.conf
   ```

   State which document is right, the 2017 post or `dns-custom-nameservers.md:54`, and compare that
   pod's `/etc/resolv.conf` with the node's from step 2.

5. Build the post's stub domain for real, using the post's own suggestion that the target *"may itself
   be a Kubernetes service"*. Run an authority for `acme.local`:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: ConfigMap
   metadata: { name: acme-corefile }
   data:
     Corefile: |
       acme.local:5300 {
           hosts {
               10.10.10.7 widget.acme.local
               fallthrough
           }
           log
       }
       .:5300 {
           log
           errors
       }
   ---
   apiVersion: apps/v1
   kind: Deployment
   metadata: { name: acme-dns }
   spec:
     replicas: 1
     selector: { matchLabels: { app: acme-dns } }
     template:
       metadata: { labels: { app: acme-dns } }
       spec:
         containers:
         - name: coredns
           image: registry.k8s.io/coredns/coredns:v1.12.0
           args: ["-conf", "/etc/coredns/Corefile"]
           volumeMounts: [{ name: cfg, mountPath: /etc/coredns }]
         volumes: [{ name: cfg, configMap: { name: acme-corefile } }]
   ---
   apiVersion: v1
   kind: Service
   metadata: { name: acme-dns }
   spec:
     selector: { app: acme-dns }
     ports: [{ port: 5300, targetPort: 5300, protocol: UDP }]
   EOF
   kubectl get svc acme-dns -o jsonpath='{.spec.clusterIP}{"\n"}'
   ```

   Record the ClusterIP; it is this exercise's `1.2.3.4`.

6. Route to it the way the pin does, not the way the post does. Edit the cluster's own ConfigMap:

   ```sh
   kubectl -n kube-system edit configmap coredns
   # add, after the closing brace of the .:53 block, using the IP from step 5:
   #   acme.local:53 {
   #       errors
   #       cache 30
   #       forward . <acme-dns ClusterIP>:5300
   #   }
   kubectl -n kube-system rollout restart deploy coredns
   kubectl -n kube-system rollout status deploy coredns
   kubectl run probe --rm -it --image=registry.k8s.io/e2e-test-images/agnhost:2.53 --restart=Never -- \
     nslookup widget.acme.local
   ```

   Put your stanza beside `dns-custom-nameservers.md:148-153` and beside the post's `stubDomains`
   line. State exactly what the post's two JSON keys corresponded to, and name two things your
   Corefile stanza can express that the post's schema has no place for.

7. Watch the failure the post's format produces, from the consumer's side:

   ```sh
   kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}' > /tmp/corefile.bak
   kubectl -n kube-system patch configmap coredns --type merge \
     -p '{"data":{"Corefile":".:53 {\n    errors\n    forward . “8.8.8.8”\n}\n"}}'
   kubectl -n kube-system rollout restart deploy coredns
   kubectl -n kube-system get pods -l k8s-app=kube-dns
   kubectl -n kube-system logs -l k8s-app=kube-dns --tail=20
   kubectl -n kube-system create configmap coredns --from-file=Corefile=/tmp/corefile.bak --dry-run=client -o yaml | kubectl -n kube-system replace -f -
   kubectl -n kube-system rollout restart deploy coredns
   ```

   The patch is accepted; the pods are not healthy. Report where the complaint about the quotation
   marks appeared, how long after the `patch` returned, and what a reader who applied the post's
   ConfigMap and then tested a name would have concluded from the symptom alone.

8. Do the post's feature per-pod, which is where the ladder went:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: dns-none }
   spec:
     dnsPolicy: None
     dnsConfig:
       nameservers: ["10.96.0.10"]
       searches: ["acme.local", "svc.cluster.local"]
       options: [{ name: ndots, value: "2" }]
     containers: [{ name: c, image: registry.k8s.io/e2e-test-images/agnhost:2.53, command: ["sleep","3600"] }]
   EOF
   kubectl exec dns-none -- cat /etc/resolv.conf
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: dns-none-empty }
   spec:
     dnsPolicy: None
     containers: [{ name: c, image: registry.k8s.io/e2e-test-images/agnhost:2.53, command: ["sleep","3600"] }]
   EOF
   ```

   The second one should be refused. Quote the error and match it against
   `dns-pod-service.md:315-317`. Then say which gate in the ladder above made both of these pods
   possible, and what a cluster administrator loses by moving the post's routing from the ConfigMap
   into pod specs.

9. Find the post's limit and the limit it did not have:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: dns-four }
   spec:
     dnsPolicy: None
     dnsConfig:
       nameservers: ["10.96.0.10", "10.96.0.11", "10.96.0.12", "10.96.0.13"]
     containers: [{ name: c, image: registry.k8s.io/e2e-test-images/agnhost:2.53, command: ["sleep","3600"] }]
   EOF
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata: { name: dns-underscore }
   spec:
     dnsPolicy: None
     dnsConfig:
       nameservers: ["10.96.0.10"]
       searches: ["my_zone.acme.local"]
     containers: [{ name: c, image: registry.k8s.io/e2e-test-images/agnhost:2.53, command: ["sleep","3600"] }]
   EOF
   ```

   The first is refused with the post's own number in the message. The second is accepted, and would
   not have been before v1.32. Name the gate responsible, give its stage at the pin, and say what that
   gate has in common with the four JSON blocks in this post.

10. Close on the two defects no cluster can show you. Read the post's rendered page and its source:

    ```sh
    # in a checkout of kubernetes/website at the pin:
    P=content/en/blog/_posts/2017/configuring-private-dns-zones-upstream-nameservers-kubernetes.md
    grep -c '```' "$P"
    grep -n '```' "$P"
    grep -c 'bp.blogspot.com' "$P"
    grep -o '“[^”]*”' "$P" | head
    ```

    The first number is odd. Work out which fence is unmatched, list what falls inside the block as a
    result, and say what the reader loses. Then count the image references and answer two questions:
    the post says *"The diagram below shows the flow of DNS queries"* and follows it with a table
    giving the same routing in text — say which of the two a reader can still act on, and say what a
    gate over this corpus would have to check to catch either defect.

**Expect**

```sh
kubectl -n kube-system get svc kube-dns
kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}' | grep -c acme.local
kubectl get pods
kubectl exec dns-none -- cat /etc/resolv.conf
kubectl -n kube-system get configmap kube-dns-blogwalk -o jsonpath='{.data.upstreamNameservers}{"\n"}'
```

A Service named `kube-dns` running CoreDNS, one stub-domain stanza you added, a resolving
`widget.acme.local`, a pod whose resolver you wrote by hand, and a stored ConfigMap value that no
JSON parser accepts.

By the end you should be able to name the kind of object `kube-dns` is at the pin and why the name was
kept, state which of the post's two ConfigMap keys still appears in the documentation and on which
page, give the number of components that could have rejected the post's JSON and the number that did,
and say which line of the pin's DNS pages misspells a value the post spells correctly.

**Read on** — the pin's
[CoreDNS ConfigMap options section](https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/#coredns-configmap-options)
lists the plugins the default Corefile loads. Read it and answer: which plugin would have to be
configured to reproduce the post's `stubDomains` behaviour for a suffix *inside* the cluster domain,
and does the page say anywhere what happens when a stub domain overlaps the cluster suffix?

**Teardown** — restore the CoreDNS ConfigMap from `/tmp/corefile.bak` if step 7 left it modified,
then `kubectl delete deploy acme-dns; kubectl delete svc acme-dns; kubectl delete cm acme-corefile;
kubectl -n kube-system delete cm kube-dns-blogwalk; kubectl delete pod --all` — and verify cluster
DNS answers before you finish, since two of the steps above edited the resolver every pod depends on.
Then [the teardown step](../../strands/lab-topologies.md#teardown).
