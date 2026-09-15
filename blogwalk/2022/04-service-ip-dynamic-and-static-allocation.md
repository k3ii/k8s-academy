<a id="service-ip-dynamic-and-static-allocation"></a>

# The gate this post asks you to enable went alpha to deleted in four releases, the floor for a full ladder, and eleven other gates share it; the strategy it switched on is unconditional now; and the post itself became a documentation page that nothing in the documentation links to

**Post** — [Kubernetes 1.24: Avoid Collisions Assigning IP Addresses to
Services](https://kubernetes.io/blog/2022/05/23/service-ip-dynamic-and-static-allocation/),
2022-05-23.

136 lines, 4,540 bytes, one author from one vendor — the sixth-shortest of 2022's sixty-nine posts
against a median of 8,081 bytes, and the fourth of the year's thirteen walked posts. It is also the
shortest distance in the archive between a post and a documentation page, for a reason the diff
section measures rather than asserts.

**As written**

A `ClusterIP` is assigned either *dynamically*, by the control plane picking a free address out of
the configured range, or *statically*, by you naming one (`:20-24`). Every `ClusterIP` in a cluster
must be unique, and asking for one that is taken returns an error (`:26-28`). That is the whole of
the setup, and it is also the whole of the problem.

The problem is the second half. You often *want* a well-known address — the post's example is the
DNS Service, which by convention takes the tenth address of the range, so a cluster configured with
`10.96.0.0/16` wants `kube-dns` on `10.96.0.10` (`:35-38`). A twenty-five-line block at `:40-64`
writes that down. And then `:66-68` explains why it is a gamble: the address is not reserved, so any
Service created before or beside it can be handed `10.96.0.10` dynamically, and then the DNS Service
simply fails to create.

The fix is a partition. Turn on the `ServiceIPStaticSubrange` feature gate, new in 1.24, and the
range is cut into two bands by the formula `min(max(16, cidrSize / 16), 256)` — *never less than 16
or more than 256 with a graduated step between them* (`:72-77`). Dynamic assignment prefers the
*upper* band and only falls back to the lower one when the upper is exhausted, which leaves the
lower band as a low-risk place to put hand-picked addresses (`:79-81`).

Three worked examples follow, at `:85-91`, `:100-106` and `:115-121`, each with a pie chart. A `/24`
gives 254 usable addresses and an offset of 16, so the static band is `10.96.0.1` to `10.96.0.16`
and 238 addresses are left for dynamic use. A `/20` gives 4094 and the offset saturates at 256. A
`/16` gives 65534 and the offset saturates at 256 again. Every one of those numbers is right, and
the arithmetic is worth doing by hand once, because it is the only thing in the post that survived
unedited into the pin.

The post closes on SIG Network's project board and meeting invitation (`:130-135`). It names no KEP.

**As it runs now**

`ServiceIPStaticSubrange` does not exist. Its gate file is still in the pinned tree, which is how
the ladder below can be transcribed, but it carries `removed: true` and the file is built with
`list: never` and `render: false`. Passing the gate to a 1.37 `kube-apiserver` is an error, not a
no-op.

The behaviour it guarded is on, unconditionally, and has been since 1.26. `virtual-ips.md:585-597`
carries it as a stable section, and prints the same formula and the same *never less than 16 or more
than 256* gloss the post printed, with *step function* where the post wrote *step*.

Underneath, the thing being partitioned was replaced wholesale. `MultiCIDRServiceAllocator` is
`stable` and `locked: true` from 1.33, one of forty-nine locked gates at the pin, and what it locked
in is the deletion of the etcd allocation bitmap in favour of two API objects: `ServiceCIDR`, which
states a range, and `IPAddress`, which records one allocation and points back at the Service that
holds it. The post's strategy outlived the implementation it was a strategy for. It also outlived
the page that described that implementation: `virtual-ips.md:445-457` still presents the *internal
allocator atomically updates a global allocation map in etcd* as how allocation works, and puts the
API-object version below it behind a `feature-state` shortcode, which at the pin is a locked stable
gate and therefore not optional at all.

And the post's own text is now a documentation page.
`concepts/services-networking/cluster-ip-allocation.md` is this post, moved, with the feature-gate
sentence taken out and almost nothing else touched — the diff section measures exactly how little.

**What this exercise does not cover, and where it lives**

The path a `ClusterIP` takes once it has been allocated belongs to the network phase and is not
re-derived here: [one ClusterIP followed to its
kube-sep](../../labs/07/16-a-clusterip-followed-to-its-kube-sep.md) owns the four iptables chains
and the DNAT, and [the same Service as a verdict
map](../../labs/07/17-the-same-service-as-a-verdict-map.md) owns the eBPF reading of it. What a
ClusterIP *is*, against the other three ways to expose a workload, is [exercise 14 of the first
phase](../../labs/01/14-four-ways-to-expose.md), which is also where MetalLB's `IPAddressPool`
enters the curriculum — a different object with a confusingly similar name and no relationship to
the `IPAddress` objects read here. The long end of a gate's life is measured in [this year's first
walked post](01-volume-expansion-ga.md), which counts beta lengths across the whole gate population;
this exercise measures the short end and uses a different statistic, so the two do not overlap.

**The diff, and why**

Three cases land, and the third is the one that makes this post worth walking.

**The post broke**, in exactly one line. `:72` says *you can enable a new feature gate
`ServiceIPStaticSubrange`*, and that is now the only instruction in the post, and it fails. The gate
was deleted after 1.27. There is no replacement instruction, because there is nothing to enable.

**The post is still right** about everything else, and unusually so for a 2022 post about a feature
gate. The formula is unchanged. The three worked examples are unchanged. The advice — put your
hand-picked Service addresses low in the range — is still the advice, and step 4 shows it is still
only advice, because nothing enforces it.

**The post was retired by being agreed with**, and this is the strongest instance of that case in
the archive so far, because the project did not merely adopt the argument. It adopted the prose.
`cluster-ip-allocation.md` is the post's body with thirteen changed hunks, of which exactly one is
semantic: the sentence naming the feature gate became *The allocation strategy implemented in
Kubernetes to allocate ClusterIPs to Services reduces the risk of collision*. The rest are tense
(*will be divided* to *is divided*), voice (*as I explained before* to *as it was explained
before*), a softened attribution (*Some Kubernetes installers* to *As a soft convention, some
Kubernetes installers*), and three example headings rewritten into numbered ones with anchors. The
twenty-five-line YAML manifest is byte-identical. The twenty-one lines of arithmetic and pie-chart
data are byte-identical, trailing double-spaces and all. So is the ungrammatical heading *How
Service ClusterIPs are allocated?*. So is the mixed-case anchor `{#avoid-ClusterIP-conflict}`, which
is an odd thing for a blog post to carry and a stranger thing for a documentation page to inherit.
So is the typo in the third example, where *Static band end* became *Static band ends* and stayed
that way on both pages.

The sixth case says the thing the post told you to install stops being a separate thing. Here the
*post* stopped being a separate thing, which is the same movement one level up, and it has a
consequence the reader can check: the documentation never cites this post, from anywhere, and does
not need to.

**Not the seventh case, and the test is worth running to see why.** *Never absorbed* asks two
questions in order — does a pinned page cite the post inline and load-bearing, and does the post
name an identifier occurring nowhere else under `content/en`. The first returns nothing: no page in
`content/en` links this post's slug at all. On a post this specific that looks like the shape of an
unabsorbed post, and it is the exact opposite. The content was absorbed so completely that a
citation would be a page linking to itself. The seventh case is about a project that took the
feature and left the explanation with the post; this is a project that took the explanation too.

There is a hole in what was absorbed, and it is in both copies because it was in the post first. The
formula's `max(16, …)` term is a floor, so a Service CIDR of `/28` or smaller has a static band at
least as large as the whole range and no dynamic band at all. The post's three examples are `/24`,
`/20` and `/16`, all comfortably above that, and the documentation page reproduces those same three.
Meanwhile `extend-service-ip-ranges.md:81-101` — a different page, added for a different feature —
uses a `/28` as its worked example and prints twelve dynamically allocated addresses running from
`10.96.0.2` to `10.96.0.14`, straight through the band the formula page would call static. Both
pages are correct. Nothing at the pin links them, and neither mentions the boundary. Step 10 counts
the distance.

**The ladder**

Three gates, transcribed from their `stages:` lists parsed as YAML. The first is the post's, the
second is the same idea applied to NodePorts a year later, and the third is the allocator that
replaced the thing both of them partitioned.

```
ServiceIPStaticSubrange        alpha  false  1.24          <- this post
                               beta   true   1.25
                               stable true   1.26 - 1.27   removed

ServiceNodePortStaticSubrange  alpha  false  1.27
                               beta   true   1.28
                               stable true   1.29 - 1.30   removed

MultiCIDRServiceAllocator      alpha  false  1.27 - 1.30
                               beta   false  1.31 - 1.32
                               stable true   1.33 -        locked
```

Four releases from a gate's first appearance to its deletion is the floor for a gate that runs the
whole ladder. Of the 487 gate files at the pin, 230 are marked `removed: true`; of those, 34 span
four releases or fewer, and only twelve carry all three of `alpha`, `beta` and `stable`. None spans
fewer than four. The post's gate and its NodePort sibling are two of those twelve, which is not a
coincidence — they are the same three-line change made twice by the same working group, and both
were uncontroversial enough to graduate on the first available release each time.

The third table is a different shape and worth reading against the first two. Its beta carries
`defaultValue: false`, so `MultiCIDRServiceAllocator` sat in beta for two releases without being on,
which is the post-1.24 convention for new APIs and the opposite of the first gate's beta. It then
went stable *and* locked, which means the flag exists only to be accepted and ignored. Four releases
of alpha, two of off-by-default beta, and then no way back.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`, 4096MB, 4 cores, 25G.

Nothing here needs a second node. Service IP allocation is an API-server concern and happens before
any packet is forwarded, so the smallest cluster in the strand shows all of it. What the single node
*does* need is a real Kubernetes with a real Service CIDR, which rules out reading this off a
manifest: step 1 derives the range from the cluster rather than assuming the kubeadm default,
because every number after it is computed from that one. Bring it up with [the strand's provisioning
run](../../strands/lab-topologies.md#provision) if it is not already there.

**Do**

1. Derive the range and compute the boundary before creating anything. The formula is the post's,
   applied to whatever this cluster was actually installed with:

   ```sh
   kubectl version -o json | python3 -c 'import json,sys
   print("server:", json.load(sys.stdin)["serverVersion"]["gitVersion"])'
   kubectl get servicecidr
   CIDR=$(kubectl get servicecidr kubernetes -o jsonpath='{.spec.cidrs[0]}')
   echo "service cidr: $CIDR"
   python3 - "$CIDR" <<'PY'
   import ipaddress, sys
   net = ipaddress.ip_network(sys.argv[1])
   size = net.num_addresses
   offset = min(max(16, size // 16), 256)
   print("cidrSize      ", size)
   print("usable        ", size - 2)
   print("band offset   ", offset)
   print("static band   ", net[1], "-", net[offset])
   print("dynamic band  ", net[offset + 1], "-", net[size - 2])
   PY
   kubectl get svc -A -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,IP:.spec.clusterIP
   ```

2. Establish that the gate the post names is gone and that the allocator underneath it is not the
   one the post assumed. `configure-feature-gates.md:207` gives the idiom: the component publishes
   every gate it knows about, so absence here is a fact about the binary and not about your flags:

   ```sh
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' \
     | grep -i 'subrange\|multicidr\|serviceip' || echo "no matching gate"
   kubectl api-resources --api-group=networking.k8s.io
   kubectl get ipaddresses | head
   ```

3. Allocate enough Services to make the preference visible, and test every address against the
   boundary step 1 computed. Twenty-four is enough to be unambiguous and small enough to delete:

   ```sh
   kubectl create ns svcband
   for i in $(seq 1 24); do
     kubectl -n svcband create service clusterip "d$i" --tcp 80 >/dev/null
   done
   kubectl -n svcband get svc -o jsonpath='{range .items[*]}{.spec.clusterIP}{"\n"}{end}' \
     | sort -t. -k1,1n -k2,2n -k3,3n -k4,4n | tee /tmp/dyn.txt
   python3 - "$(kubectl get servicecidr kubernetes -o jsonpath='{.spec.cidrs[0]}')" <<'PY'
   import ipaddress, sys
   net = ipaddress.ip_network(sys.argv[1])
   offset = min(max(16, net.num_addresses // 16), 256)
   edge = int(net[offset])
   addrs = [int(ipaddress.ip_address(l.strip())) for l in open("/tmp/dyn.txt") if l.strip()]
   print("allocated      ", len(addrs))
   print("in static band ", sum(1 for a in addrs if a <= edge))
   print("in dynamic band", sum(1 for a in addrs if a > edge))
   print("lowest         ", ipaddress.ip_address(min(addrs)))
   print("boundary       ", net[offset])
   PY
   ```

4. Find out what the lower band actually is. The post calls it low-risk; the question is whether it
   is anything more than that. Claim an address there, then claim one in the upper band and see
   whether the API objects:

   ```sh
   CIDR=$(kubectl get servicecidr kubernetes -o jsonpath='{.spec.cidrs[0]}')
   LOW=$(python3 -c 'import ipaddress,sys; print(ipaddress.ip_network(sys.argv[1])[50])' "$CIDR")
   HIGH=$(python3 -c 'import ipaddress,sys
   n=ipaddress.ip_network(sys.argv[1]); print(n[min(max(16,n.num_addresses//16),256)+500])' "$CIDR")
   echo "low $LOW  high $HIGH"
   kubectl -n svcband create service clusterip low --tcp 80 --clusterip "$LOW"
   kubectl -n svcband create service clusterip high --tcp 80 --clusterip "$HIGH"
   kubectl -n svcband get svc low high -o custom-columns=NAME:.metadata.name,IP:.spec.clusterIP
   kubectl -n svcband create service clusterip dup --tcp 80 --clusterip "$LOW" 2>&1 | tail -2
   ```

5. Read the substrate the post could not have known about. Every allocated address is now an API
   object with a back-reference, which makes the allocation table something you can join rather than
   something you infer:

   ```sh
   kubectl get ipaddresses -o custom-columns=IP:.metadata.name,PARENT:.spec.parentRef.name \
     | head -20
   echo "ipaddress objects: $(kubectl get ipaddresses --no-headers | wc -l)"
   echo "cluster ips:       $(kubectl get svc -A -o jsonpath='{range .items[*]}{.spec.clusterIP}{"\n"}{end}' \
     | grep -vc '^None$\|^$')"
   kubectl get servicecidr kubernetes -o yaml | sed -n '/^spec:/,$p'
   ```

6. Churn it. Delete half the Services and create half as many again, then ask whether the boundary
   held and whether any address came back. The answer to the second question is not documented
   anywhere at the pin:

   ```sh
   kubectl -n svcband get svc \
     -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.clusterIP}{"\n"}{end}' \
     | awk '$1 ~ /^d([1-9]|1[0-2])$/ {print $2}' \
     | sort -t. -k1,1n -k2,2n -k3,3n -k4,4n > /tmp/freed.txt
   for i in $(seq 1 12); do kubectl -n svcband delete svc "d$i" >/dev/null; done
   for i in $(seq 25 36); do
     kubectl -n svcband create service clusterip "d$i" --tcp 80 >/dev/null
   done
   kubectl -n svcband get svc \
     -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.clusterIP}{"\n"}{end}' \
     | awk '$1 ~ /^d(2[5-9]|3[0-6])$/ {print $2}' \
     | sort -t. -k1,1n -k2,2n -k3,3n -k4,4n > /tmp/fresh.txt
   echo "freed $(wc -l < /tmp/freed.txt)  fresh $(wc -l < /tmp/fresh.txt)"
   echo "freed addresses handed straight back out:"
   comm -12 /tmp/freed.txt /tmp/fresh.txt | wc -l
   echo "lowest of the fresh twelve:"
   head -1 /tmp/fresh.txt
   ```

7. Add a second range and find out whether the band rule is a property of the cluster or of each
   `ServiceCIDR`. This is the question the pin cannot answer, so measure it. The primary range is
   nowhere near full, so watch which range new Services come from as well:

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: networking.k8s.io/v1
   kind: ServiceCIDR
   metadata:
     name: second
   spec:
     cidrs:
     - 10.97.0.0/24
   YAML
   kubectl get servicecidr
   for i in $(seq 1 6); do
     kubectl -n svcband create service clusterip "s$i" --tcp 80 -o jsonpath='{.spec.clusterIP}{"\n"}'
   done
   kubectl get ipaddresses | grep '^10.97' || echo "nothing allocated from the second range"
   ```

8. Offline now, in the pinned checkout. Measure the copy: how much of the post is the documentation
   page, and which of the post's defects travelled across with it:

   ```sh
   cd /path/to/kubernetes/website
   A=content/en/blog/_posts/2022/service-ip-dynamic-and-static-allocation.md
   B=content/en/docs/concepts/services-networking/cluster-ip-allocation.md
   diff <(sed -n '10,128p' $A) <(sed -n '13,142p' $B) | grep -c '^[<>]'
   diff <(grep -E '^(Range|Band|Static|    ")' $A) <(grep -E '^(Range|Band|Static|    ")' $B) \
     && echo "arithmetic identical: $(grep -cE '^(Range|Band|Static|    \")' $A) lines"
   diff <(sed -n '40,64p' $A) <(sed -n '46,70p' $B) && echo "yaml identical: 25 lines"
   grep -n 'Static band end' $A $B
   grep -n 'avoid-ClusterIP-conflict' $A $B
   ```

9. Ask what happened to the page that resulted. A concept page that nothing links to is reachable
   only through the section navigation, which is a real difference in a documentation set this size,
   so count inbound references for every page in the same directory:

   ```sh
   cd /path/to/kubernetes/website/content/en
   for f in docs/concepts/services-networking/*.md; do
     b=$(basename "$f" .md); [ "$b" = "_index" ] && continue
     n=$(grep -rl "services-networking/$b" . --include='*.md' | grep -v "^./$f$" | wc -l | tr -d ' ')
     printf '%4s  %s\n' "$n" "$b"
   done | sort -n
   ```

10. And the formula, counted where it lives, plus the gate file's own link and the `/28` the formula
    page never meets:

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -rn 'min(max(16, cidrSize / 16), 256)' . --include='*.md' | sed 's|^\./||'
    grep -rn 'upper band' . --include='*.md' | sed 's|^\./||'
    grep -n 'avoiding-collisions' \
      docs/reference/command-line-tools-reference/feature-gates/ServiceIPStaticSubrange.md
    grep -n '{#avoiding-collisions}\|### Avoiding collisions\|{#service-ip-static-sub-range}' \
      docs/reference/networking/virtual-ips.md
    grep -n 'avoid-nodeport-collisions' \
      docs/reference/command-line-tools-reference/feature-gates/ServiceNodePortStaticSubrange.md \
      docs/concepts/services-networking/service.md
    sed -n '81,101p' docs/tasks/network/extend-service-ip-ranges.md
    ```

**Expect**

Step 1 prints a range that is almost certainly `10.96.0.0/12`, because that is what kubeadm installs
and it is the range the DNS Service on this cluster already sits inside. That gives a `cidrSize` of
1048576, a band offset that saturates at 256, a static band of `10.96.0.1` to `10.96.1.0`, and a
dynamic band starting at `10.96.1.1`. Note what is already in the static band before you have
created anything: `kubernetes` on `10.96.0.1` and `kube-dns` on `10.96.0.10`, both placed by the
installer, both exactly where the post says hand-picked addresses belong. The post describes a
convention the cluster you are reading was built on.

Step 2 finds no `ServiceIPStaticSubrange` and no `ServiceNodePortStaticSubrange` — neither gate is
known to the binary — and `MultiCIDRServiceAllocator` reported as enabled. `networking.k8s.io` lists
`servicecidrs` and `ipaddresses` as `v1` resources, and there is already one `IPAddress` object per
existing Service. That last line is the post's world replaced: the allocation table is no longer a
bitmap in etcd that only the API server can read.

Step 3 should put all twenty-four addresses above `10.96.1.0` and none below it. The lowest
allocated address is the measurement — if it is `10.96.1.1` or higher, the preference the post
described is in force with no gate to switch it on. Expect the addresses to be scattered rather than
sequential; the pin never says allocation within a band is random, and the only evidence it offers
either way is a sample output on a page about something else.

Step 4 should succeed three times and fail once. The lower-band address is accepted, and that is the
post's advice working. The *upper*-band address is also accepted, and that is the finding: the split
is a preference in the allocator, not a reservation in the API, so nothing stops you putting a
static address exactly where dynamic allocation will go looking. The duplicate fails with a
conflict, which is the error `:26-28` describes and the only part of this mechanism that is
enforced.

Step 5 should show one `IPAddress` object per `ClusterIP`, with `parentRef` naming the owning
Service, and the two counts equal. The `ServiceCIDR` named `kubernetes` carries the cluster's range
and a finalizer; it was created by the API server from `--service-cluster-ip-range` at bootstrap,
which means the flag the post assumed is now the seed for an object rather than the whole story.

Step 6 is a question, not a demonstration. The boundary should hold — every new address above
`10.96.1.0` again — but whether any of the twelve freed addresses is handed back out of a band
holding roughly a million free ones is something the pin does not document and this cluster can only
sample. Report the number you get; one run does not establish a policy.

Step 7 is the open one. A second `ServiceCIDR` is accepted, and `kubectl get servicecidr` shows two
ranges. What is not documented is whether the band split applies per `ServiceCIDR` or only to the
range the cluster booted with, and — because the primary range has about a million free addresses —
whether anything is allocated from the new range at all while the old one has room. Both questions
are answered by the six addresses step 7 prints. Record them; do not generalise from them.

Step 8 should print 39 differing lines across 13 hunks, then report the arithmetic identical at 21
lines and the YAML identical at 25. `Static band ends` appears on both files, at `:120` in the post
and `:134` on the documentation page. The anchor `{#avoid-ClusterIP-conflict}` appears on both, and
on nothing else in the checkout — a blog post and a documentation page sharing a hand-written
mixed-case anchor that neither of them is linked at.

Step 9 should return one page with zero inbound references, and it should be
`cluster-ip-allocation`. Of the twelve concept pages in `services-networking`, it is the only one
nothing links to; the next lowest is `service-traffic-policy` at one and `service` itself is at 66.
This is the price of the absorption, and it is worth naming precisely: the page is not missing and
not wrong, it is merely unreachable except by browsing the section, which is a different kind of
document from the one the post was.

Step 10 should find the formula on exactly two documentation pages plus the post, with
`cluster-ip-allocation.md:81` and `virtual-ips.md:591` wording the gloss differently — *a graduated
step between them* against *a graduated step function between them* — which is what copy drift looks
like when two pages own one fact. Then the anchors. The removed gate's description file links
`virtual-ips/#avoiding-collisions`, and that anchor exists, at `virtual-ips.md:432`; it is a section
about why Kubernetes allocates Service IPs at all, and it says nothing about bands. The section that
does is 153 lines further down under `{#service-ip-static-sub-range}`, an anchor named after the
gate that no longer exists and that nothing links to. Compare the NodePort sibling, which the same
working group shipped three releases later: its gate file links
`service/#avoid-nodeport-collisions`, that anchor exists, and the section under it is the one that
describes the bands. The later, smaller feature got the better landing. Last, the `/28`: twelve
dynamic allocations from `10.96.0.2` to `10.96.0.14`, every one of them inside what the formula
would call the static band, on a range too small to have a dynamic band at all.

**Read on**

1. [One ClusterIP followed to its
   kube-sep](../../labs/07/16-a-clusterip-followed-to-its-kube-sep.md) — what the address does after
   it is allocated. This exercise stops at the moment the API server writes a number into
   `.spec.clusterIP`; that one starts there and follows it through four iptables chains to a DNAT.

2. [Thirteen releases in beta, then no gate at all](01-volume-expansion-ga.md) — the other end of
   the same distribution, measured on the same population. It counts beta lengths and finds a
   twenty-seven-release record; this one counts whole-ladder spans and finds a four-release floor.
   Read together they bound how fast and how slow the project moves a gate.

3. `extend-service-ip-ranges.md` in the pinned tree, end to end — the task page for the allocator
   that replaced this one. It is where the `ServiceCIDR` finalizer, the `OrphanIPAddress` condition
   and the admission policy for restricting ranges are written down, and it is the page whose worked
   example quietly contradicts the shape of the post's three.

4. [The repo's source-reading list](../../strands/source-reading.md) books the multiple Service
   CIDRs proposal as item 24 and pairs it with `pkg/controller/servicecidrs/`. That is the reading
   that answers step 7 properly — whether the band split is per-range or per-cluster is a question
   about one controller's code, and the pin holds documentation rather than code.

5. Unanswerable from the pin: whether allocation inside the dynamic band is random, and whether the
   band rule survives into a second `ServiceCIDR`. Neither is stated anywhere in `content/en`. The
   only evidence in the whole checkout is two blocks of sample output on
   `extend-service-ip-ranges.md:90-101` and `:131-134`, which show scattered addresses in a range
   too small for the question to mean anything. Steps 6 and 7 sample the answer on one cluster; the
   archive cannot confirm it.

**Teardown**

```sh
kubectl delete ns svcband
kubectl delete servicecidr second
kubectl get servicecidr
echo "ipaddress objects: $(kubectl get ipaddresses --no-headers | wc -l)"
echo "cluster ips:       $(kubectl get svc -A -o jsonpath='{range .items[*]}{.spec.clusterIP}{"\n"}{end}' \
  | grep -vc '^None$\|^$')"
```

Delete the namespace before the `ServiceCIDR`, not after. The finalizer on a `ServiceCIDR` will not
clear while any `IPAddress` object still belongs to it, so a `ServiceCIDR` deleted first sits in
`Terminating` with an `OrphanIPAddress` condition until the Services holding its addresses are gone
— which is worth seeing once, deliberately, and is a nuisance every other time. The two counts at
the end should be equal to each other, which is the invariant step 5 checked on a full namespace,
and back to whatever they were before step 3 created anything.
