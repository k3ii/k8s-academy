<a id="ipvs-in-cluster-load-balancing"></a>
# The parameters of the mode this post announces outlived the explanation of why they exist, and the interface it teaches survives in the pinned documentation only inside a field description for the setting that works around it

**Post** — [IPVS-Based In-Cluster Load Balancing Deep Dive](https://kubernetes.io/blog/2018/07/09/ipvs-in-cluster-load-balancing/),
2018-07-09, by Jun Du, Haibin Xie and Wei Liang of Huawei. Kubernetes 1.11. Part of the 1.11
release series, and the post that announces IPVS-based in-cluster Service load balancing at
General Availability.

**As written** — a deep dive with a thesis, six parameters, four design sections and one very
large table.

The thesis is scale, argued in four paragraphs. "As Kubernetes grows in usage, the scalability of
its resources becomes more and more important." Kube-proxy "has relied on the battle-hardened
iptables"; iptables "struggles to scale to tens of thousands of Services because it is designed
purely for firewalling purposes and is based on in-kernel rule lists." Then the arithmetic that
carries the whole post:

> Even though Kubernetes already support 5000 nodes in release v1.6, the kube-proxy with iptables
> is actually a bottleneck to scale the cluster to 5000 nodes. One example is that with NodePort
> Service in a 5000-node cluster, if we have 2000 services and each services have 10 pods, this
> will cause at least 20000 iptable records on each worker node, and this can make the kernel
> pretty busy.

Against that, IPVS: "specifically designed for load balancing and uses more efficient data
structures (hash tables) allowing for almost unlimited scale under the hood."

Then **Parameter Changes**, six of them, each with its own bold lead-in:

- `--proxy-mode` — "In addition to existing userspace and iptables modes, IPVS mode is configured
  via `--proxy-mode=ipvs`. It implicitly uses IPVS NAT mode for service port mapping."
- `--ipvs-scheduler` — the load-balancing algorithm, defaulting to round-robin, with six values
  offered: `rr`, `lc`, `dh`, `sh`, `sed`, `nq`. Followed by a forecast: "In the future, we can
  implement Service specific scheduler (potentially via annotation), which has higher priority and
  overwrites the value."
- `--cleanup-ipvs` — "Similar to the `--cleanup-iptables` parameter, if true, cleanup IPVS
  configuration and IPTables rules that are created in IPVS mode."
- `--ipvs-sync-period` — maximum refresh interval, must be greater than 0.
- `--ipvs-min-sync-period` — minimum refresh interval, must be greater than 0.
- `--ipvs-exclude-cidrs` — CIDRs the proxier must not touch when cleaning up, "because IPVS proxier
  can't distinguish kube-proxy created IPVS rules from user original IPVS rules."

Then four **Design Considerations**, and this is the part of the post that is doing teaching rather
than reference.

*IPVS Service Network Topology.* Creating a ClusterIP Service makes the proxier do three things:
"Make sure a dummy interface exists in the node, defaults to kube-ipvs0", bind Service IPs to that
interface, and create one IPVS virtual server per Service IP. The post then prints a worked
example — `kubectl describe svc`, `ip addr`, `ipvsadm -ln` — showing `73: kube-ipvs0:
<BROADCAST,NOARP> mtu 1500 qdisc noop state DOWN`, the ClusterIP `10.102.128.4/32` bound to it, and
two real servers behind `TCP 10.102.128.4:3080 rr`. And it states two cardinalities plainly: Service
to virtual server is `1:N` (an External IP Service has two IPs, so two virtual servers), and
Endpoint — "each IP+Port pair" — to virtual server is `1:1`.

*Port Mapping.* "There are three proxy modes in IPVS: NAT (masq), IPIP and DR. Only NAT mode
supports port mapping." Hence `Masq` in the output, and hence Service port 3080 can front Pod port
8080.

*Session Affinity.* "IPVS supports client IP session affinity (persistent connection). When a
Service specifies session affinity, the IPVS proxier will set a timeout value (180min=10800s by
default) in the IPVS virtual server" — shown as `persistent 10800` in `ipvsadm` output.

*Iptables & Ipset in IPVS Proxier.* The admission that the mode is not IPVS alone: "IPVS is for
load balancing and it can't handle other workarounds in kube-proxy, e.g. packet filtering,
hairpin-masquerade tricks, SNAT, etc." The proxier falls back to iptables in exactly four
scenarios — `--masquerade-all=true`, a cluster CIDR being specified, LoadBalancer Services, and
NodePort Services. "However, we don't want to create too many iptables rules. So we adopt ipset for
the sake of decreasing iptables rules," followed by an eleven-row table of the ipset sets the
proxier maintains: `KUBE-CLUSTER-IP`, `KUBE-LOOP-BACK`, `KUBE-EXTERNAL-IP`, `KUBE-LOAD-BALANCER`,
`KUBE-LOAD-BALANCER-LOCAL`, `KUBE-LOAD-BALANCER-FW`, `KUBE-LOAD-BALANCER-SOURCE-CIDR`,
`KUBE-NODE-PORT-TCP`, `KUBE-NODE-PORT-LOCAL-TCP`, `KUBE-NODE-PORT-UDP`, `KUBE-NODE-PORT-LOCAL-UDP`.
It closes with the claim the table exists to support: "In general, for IPVS proxier, the number of
iptables rules is static, no matter how many Services/Pods we have."

Finally **Run kube-proxy in IPVS Mode**: local-up scripts, GCE scripts and kubeadm support
`KUBE_PROXY_MODE=ipvs` or `--proxy-mode=ipvs`; five kernel modules must be present (`ip_vs`,
`ip_vs_rr`, `ip_vs_wrr`, `ip_vs_sh`, `nf_conntrack_ipv4`); and the gate note — "for Kubernetes
v1.10, feature gate `SupportIPVSProxyMode` is set to `true` by default. For Kubernetes v1.11, the
feature gate is entirely removed."

**As it runs now** — the mode is deprecated with three dated milestones against it, and the
post's own text splits cleanly in two: almost every *parameter* survives, and almost every
*explanation* is gone from the documentation.

Start with what this exercise does **not** cover, because it is covered better one exercise
backward and restating it here would put one fact in two places. The two feature gates that carried
this mode — `SupportIPVSProxyMode`, with its two beta rows, and `KubeProxyIPVS`, with its single
`deprecated` row facing the other way — are transcribed and read against each other in
[the 1.1 release-announcement exercise](../2015/10-kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community.md).
So is the list of values `--proxy-mode` now accepts, the disappearance of `userspace`, the argument
about why the iptables default outlasted a faster mode, and the four supported-scale limits the
post's 5,000-node arithmetic is drawn from. Read that exercise first; this one starts where it
stops, inside the post's own six parameters and four design sections.

**Five of the six parameters are still in `kube-proxy --help`, and the sixth was renamed and
widened.** `--ipvs-scheduler`, `--ipvs-sync-period` (default 30s), `--ipvs-min-sync-period`
(default 1s) and `--ipvs-exclude-cidrs` are at `kube-proxy.md:244`, `:258`, `:237` and `:230`, with
`--proxy-mode` at `:447-450`. `--cleanup-ipvs` occurs **zero times** in the pinned documentation, and so does the
`--cleanup-iptables` the post compares it to; both were replaced by a single `--cleanup`, at
`kube-proxy.md:83-86`, described as "If true cleanup iptables and ipvs rules and exit." Two
mode-specific flags became one flag that does not name a mode.

**The mode gained four flags after being declared complete.** Beyond the four the post lists, the
pin carries `--ipvs-strict-arp`, `--ipvs-tcp-timeout`, `--ipvs-tcpfin-timeout` and
`--ipvs-udp-timeout`. Eight `--ipvs-*` flags exist; the post announcing GA documents four of them.
The config-file equivalents are at `kube-proxy-config.v1alpha1.md:893-976`, eight fields under
`KubeProxyIPVSConfiguration` — `syncPeriod`, `minSyncPeriod`, `scheduler`, `excludeCIDRs`,
`strictARP`, `tcpTimeout`, `tcpFinTimeout`, `udpTimeout` — and every one of the eight is marked
`[Required]`, on a mode with a removal date.

**The scheduler list nearly doubled, and every one of the post's six is still valid.** The pin
lists eleven at `virtual-ips.md:245-287`: `rr`, `wrr`, `lc`, `wlc`, `lblc`, `lblcr`, `sh`, `dh`,
`sed`, `nq`, `mh`. The post's six are a subset. The five additions are the weighted and
locality-based variants plus Maglev hashing, and the `mh` entry carries a caveat the post's
one-line-per-scheduler format could not have held: "In proxy-mode=ipvs `mh` will work as
source-hashing (`sh`), but with ports" (`:287`). Note also that the post's kernel-module list ships
`ip_vs_wrr` while its scheduler list omits `wrr` — the modules were ahead of the flag
documentation on the day of publication, and the pin has since documented the scheduler the module
was already there for.

**Where you set the scheduler moved.** The post presents it as a command-line flag; the pin closes
its scheduler list with "These scheduling algorithms are configured through the `ipvs.scheduler`
field in the kube-proxy configuration" (`:289-291`). The flag reference half-agrees. Eleven of its
sixty-four flag rows end with a sentence the post's era did not need — "This parameter is ignored
if a config file is specified by --config" — and `--proxy-mode` at `kube-proxy.md:450` is one of
them, but **none of the eight `--ipvs-*` rows carries it**. So the mode is documented as a
config-file setting and its own eight parameters are still documented as flags, on the same page.

**The forecast in the `--ipvs-scheduler` section was never built.** No per-Service scheduler
annotation exists anywhere in the pinned documentation, and the closest thing the project actually
shipped — a Service field for topology-based routing — went alpha and then straight to
`deprecated` without ever reaching beta. Its field name, `topologyKeys`, occurs twice in the pinned documentation
and neither occurrence is on a Service: once in topology spread constraints and once on `CSINode`,
where it means something else entirely. The ladder below has this.

**`kube-ipvs0` is named exactly once in the entire pinned documentation set, and not in the IPVS
reference.** The dummy interface that the post's first design section is built around, and that its
worked `ip addr` output exists to show you, survives in the pin only inside the description of the
`strictARP` config field: "strictARP configures arp_ignore and arp_announce to avoid answering ARP
queries from kube-ipvs0 interface" (`kube-proxy-config.v1alpha1.md:947-948`). The three-step
sequence — ensure the interface, bind the Service IPs, create the virtual servers — is documented
nowhere. The interface is now a thing another field exists to work around rather than a thing
explained.

**And it is still load-bearing for a page that does not name it.** The NodeLocal DNSCache setup
task branches on proxy mode, and the IPVS branch says: "The `node-local-dns` interface cannot bind
the CoreDNS cluster IP since the interface used for IPVS loadbalancing already uses this address"
(`nodelocaldns.md:117-118`), so in IPVS mode the cache listens only on the node-local address, a
different `sed` substitution is applied to the manifest, and the kubelet's `--cluster-dns` has to
be changed too (`:110-118`, `:123-127`). That page needs the fact this post teaches, states the
consequence, and never states the fact — it says "the interface used for IPVS loadbalancing" and
leaves the reader to find out which interface that is from a config-field description in a
different reference.

**The ipset table has no counterpart in the pin at all.** None of the eleven `KUBE-*` set names
occurs anywhere in the pinned documentation. The word `ipset` occurs once, on a third-party
network-policy addon page (`kube-router-network-policy.md:20`), not in any kube-proxy reference.
The four iptables-fallback scenarios are not listed. The claim the whole section builds to — that
the iptables rule count is static under IPVS regardless of Service and Pod count — is not stated,
qualified or contradicted; it is simply absent. This is the post's longest and most carefully
constructed artifact, and the only way to check it now is to run `ipset list` on a node, which is
step 10.

**Two of the design sections survived as a debugging page, in almost the post's words.** The
`ipvsadm -ln` output and the cardinality rule are at `debug-service.md:572-594`: "For each port of
each Service, plus any NodePorts, external IPs, and load-balancer IPs, kube-proxy will create a
virtual server. For each Pod endpoint, it will create corresponding real servers." That is the
post's `1:N` and `1:1`, restated as a troubleshooting step. The mode's own reference does not carry
it.

**Session affinity is still exactly right, and no longer an IPVS fact.** The 10800-second default
the post attributes to the IPVS proxier is now a Service API default:
`.spec.sessionAffinityConfig.clientIP.timeoutSeconds`, "the default value is 10800, which works out
to be 3 hours" (`virtual-ips.md:411-415`). The number did not change. What changed is that it
became configurable per Service through a field, which is the shape the post's own scheduler
forecast asked for and did not get.

**The instruction for doing what the post's last section describes is a link to a moving branch.**
`kubeadm-init.md:242-250` has a subsection called *Adding kube-proxy parameters*. It offers two
pointers: the config-API reference, and then "For information about enabling IPVS mode with kubeadm
see: - [IPVS](…/kubernetes/kubernetes/blob/master/pkg/proxy/ipvs/README.md)" — the target is
`pkg/proxy/ipvs/README.md` on `kubernetes/kubernetes`'s `master` branch. That
is a link into the source tree, on `master`, so what it says at any given moment cannot be pinned
and is not verifiable from this archive's frozen checkout at all. The post's own mechanism —
`KUBE_PROXY_MODE=ipvs` — occurs nowhere in the pin. So the documented answer to "how do I run the
thing this post is about" is a URL to a branch that moves.

**The five kernel modules are gone from the documentation, and one node-level sysctl is left
behind in the wrong list.** None of `ip_vs`, `ip_vs_rr`, `ip_vs_wrr`, `ip_vs_sh` or
`nf_conntrack_ipv4` occurs in the pin. What remains is a single line:
`net.ipv4.vs.conn_reuse_mode` "(used in `ipvs` proxy mode, needs kernel 4.1+)", at
`kernel-version-requirements.md:39`. Two things are wrong with where it sits. It is under the
heading `## Pod sysctls` (`:15`), and it is a kube-proxy setting on the node, not a pod sysctl.
And the list it is in is introduced as sysctls that "are supported in the
[safe set](/docs/tasks/administer-cluster/sysctl-cluster/#safe-and-unsafe-sysctls)" (`:23-24`),
while the actual safe set at `sysctl-cluster.md:74-87` has fourteen entries and
`net.ipv4.vs.conn_reuse_mode` is **not one of them**. Ten of the eleven entries in the
kernel-requirements list appear in the safe set; the IPVS one is the exception, and it is also the
only entry in the list whose annotation names a component rather than a version. Cite both
pages and say they disagree: the safe-set page governs what a Pod may set, and the
kernel-requirements page is where a reader chasing IPVS kernel prerequisites will land first.

**The gate the deprecation notice tells you to use is absent from the binary that would consume
it.** `virtual-ips.md:212-214` says support "will be disabled by default from Kubernetes v1.40 (you
can re-enable it with the `KubeProxyIPVS` feature gate); `ipvs` mode will be fully removed in
Kubernetes v1.43." The string `KubeProxyIPVS` occurs **zero times** in `kube-proxy.md`, whose
`--feature-gates` row (`:167-170`) enumerates every gate that component accepts by name and stage.
Outside the gate's own file, the only other occurrences in the docs tree are at `virtual-ips.md:290` and
`kube-proxy-config.v1alpha1.md:614`, `:893` and `:901`, and all four of those are the unrelated
`KubeProxyIPVSConfiguration` struct rather than the gate. So the escape hatch for the deprecation
is named once, in prose, on a page that is not the component's reference — and the component's
reference does not list it. This is the same failure shape as
[the CSI beta exercise's `MutableCSINodeAllocatableCount`](02-container-storage-interface-beta.md):
a gate the prose instructs you to set, missing from the flag list of the process you would set it
on.

**And the reason the post existed was fixed inside the mode it was written against.** The pin's
note on the IPVS mode is unusually direct for documentation (`virtual-ips.md:223-240`): the mode
"was an experiment", it "succeeded in those goals", but "the kernel IPVS API turned out to be a bad
match for the Kubernetes Services API, and the `ipvs` backend was never able to implement all of
the edge cases of Kubernetes Service functionality correctly." Then the recommendation that closes
the loop: if your kernel is too old for `nftables`, "you should also consider trying the `iptables`
mode rather than `ipvs`, since the performance of `iptables` mode has improved greatly since the
`ipvs` mode was first introduced" (`:235-239`). The post's opening premise — iptables cannot be
made to scale — is answered on the same page that deprecates its subject.

**One number in the post's arithmetic has not moved at all.** "Kubernetes already support 5000
nodes in release v1.6," the post says, and calls that the ceiling kube-proxy was blocking.
`cluster-large.md:12-18` still says "supports clusters with up to 5,000 nodes." Twenty-six releases
later, three proxy backends, and the supported node count is the same integer. The bottleneck was
removed and the ceiling did not rise, which means the ceiling was never that bottleneck.

**The diff, and why** — this is a **post that broke** and a **post that was overtaken by stasis**
at the same time, and the interesting thing is which half is which. The parameters are the part
that survived. The reasoning is the part that vanished.

Take the two halves separately, because the post is organised as a reference wrapped around an
explanation and they have had opposite fates.

The **reference** half — six flags, six schedulers, one timeout default, two cardinality rules —
is in very good shape for a 2018 document. Five flags still work; the sixth was renamed to
something more general. All six schedulers are still accepted, and five more joined them. The
10800-second default is still 10800. The `1:N` and `1:1` rules are still true and are now printed
on the debugging page in almost the post's own sentences. A reader who wanted only the parameters
would find this post more accurate than most 2018 posts about anything.

The **explanation** half is gone. The dummy interface, the three-step provisioning sequence, the
NAT-versus-IPIP-versus-DR choice, the four iptables-fallback scenarios, the eleven ipset sets, the
static-rule-count claim, the five kernel modules, the environment variable — none of it is in the
pinned documentation. Not contradicted: absent. And this is the harder failure to notice, because
nothing tells you. A removed field throws an error. A renamed flag prints usage. A design
explanation that stops being documented leaves no artifact at all; the mechanism is still running
on the node, and the only record of why it looks like that is the blog post.

The confirmation is `nodelocaldns.md:117-118`. That page cannot state its own instruction without
the fact this post teaches — an interface is holding the CoreDNS cluster IP, so something else
cannot bind it — and it states the consequence while omitting the fact and the interface's name.
A current, maintained task page is standing on a 2018 blog post's design section and cannot cite
it, because the reference page that should have carried the fact never did. The one line in the pin
that names `kube-ipvs0` is inside a field description for `strictARP`, a setting whose entire
purpose is to stop the interface from answering ARP. The interface is documented only through the
problem it causes.

So the diff is not "IPVS was deprecated". That is the headline and it is the shallow reading, and
[the 1.1 exercise](../2015/10-kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community.md)
already carries why the mode lost. The diff here is that a *deep dive* — a post whose value is the
explanation, not the flag list — was the only place the explanation ever lived, and when the
feature was wound down the flag list was maintained and the explanation was not. Deprecating a
feature deletes its documentation on a schedule. Nobody ever writes the migration guide for an
explanation.

Which gives the mechanism behind this post's title. GA in v1.11 protected the *interface*: the
flags kept working, kept their defaults documented, kept gaining siblings, and are still in the
reference at the pin while the mode has a removal release named against it. GA protected nothing
about the *account*. And the ladder kept moving anyway — not the mode's own ladder, which is the
1.1 exercise's material, but the ladders underneath it, governing which endpoints the post's
virtual servers are allowed to have real servers for. The post describes a proxier watching
Endpoints objects and creating one real server per IP+Port pair. Between v1.17 and v1.35, seven
gates changed what that sentence means: the object being watched, whether terminating endpoints
count, whether the node's own endpoints are preferred, whether topology is expressed per Service
or computed centrally. Every one of those landed while the mode itself sat at `stable`. GA is not
the end of the ladder because a feature's own gate is not the only ladder it is standing on.

Release facts and the pressure behind each are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

**The ladder** — seven gates, transcribed per gate. **None of them governs the IPVS mode.** They
govern the thing the post's `1:1` rule is about: which endpoints become real servers behind a
virtual server. They are here because they are what moved while the mode did not, and because the
first of them is the answer to the post's own forecast.

`ServiceTopology`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.17 – v1.19 |
| deprecated | `false` | — | v1.20 – v1.22 |

`TopologyAwareHints`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.21 – v1.22 |
| beta | `false` | — | v1.23 – v1.23 |
| beta | `true` | — | v1.24 – v1.32 |
| stable | `true` | `true` | v1.33 – |

`EndpointSliceProxying`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.18 – v1.18 |
| beta | `true` | — | v1.19 – v1.21 |
| stable | `true` | — | v1.22 – v1.24 |

`EndpointSliceTerminatingCondition`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.20 – v1.21 |
| beta | `true` | — | v1.22 – v1.25 |
| stable | `true` | — | v1.26 – v1.27 |

`ProxyTerminatingEndpoints`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.22 – v1.25 |
| beta | `true` | — | v1.26 – v1.27 |
| stable | `true` | — | v1.28 – v1.29 |

`KubeProxyDrainingTerminatingNodes`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.28 – v1.30 |
| beta | `true` | — | v1.30 – v1.30 |
| stable | `true` | — | v1.31 – v1.32 |

`ServiceTrafficDistribution`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.30 – v1.30 |
| beta | `true` | — | v1.31 – v1.32 |
| stable | `true` | `true` | v1.33 – |

Five of the seven files declare `removed: true`; `TopologyAwareHints` and `ServiceTrafficDistribution`
do not, and both of their stable rows carry `locked: true`. None declares `former_titles`.

Four readings, in order of what they cost you to miss.

**`ServiceTopology` is the post's forecast, tried and abandoned.** Its gate body reads "Enable
service to route traffic based upon the Node topology of the cluster." That is a per-Service
routing-policy override, expressed as a field on the Service — the same shape as "Service specific
scheduler (potentially via annotation), which has higher priority and overwrites the value." It
went alpha at v1.17, and its second and last row is `deprecated`. **It never reached beta.** Two
rows, `alpha` then `deprecated`, means the idea was rejected after being shipped behind a switch,
and it is not a freak: **25 of the pinned tree's 488 gate files have exactly that shape**, about
one in twenty, so abandoning an alpha without ever promoting it is a routine outcome rather than
an accident. Then read the next gate: what the
project built instead was `TopologyAwareHints`, which is the same goal reached from the opposite
direction — hints computed by the control plane and written into EndpointSlices, rather than a
policy the Service author declares. It climbed all the way to `stable` with `locked: true`, meaning
it can no longer be switched off. Two ladders, one abandoned and one locked on, and between them
they say the project agreed with the post about the problem and disagreed about who gets to state
the answer. This is the clean case of a **plan the project abandoned**, and unusually it is a plan
the post itself proposed rather than one the project announced.

**`EndpointSliceProxying` moved the object under the post's `1:1` rule.** The post says "the
relationship between a Kubernetes Endpoint (each IP+Port pair) and an IPVS virtual server is
`1:1`." From v1.22 the proxier's source of truth is EndpointSlice, not Endpoints, and at the pin
the Endpoints API itself is marked deprecated from v1.33 (`service.md:310-325`), with three reasons
given: no dual-stack, no room for newer fields such as `trafficDistribution`, and truncation of
long endpoint lists. The post's sentence is still true about the shape of the mapping and wrong
about the noun. This is the quiet kind of break: the sentence stays grammatical and the object it
names is on its way out.

**Three gates in a row are about endpoints that are going away, and they are the edge cases.**
`EndpointSliceTerminatingCondition`, `ProxyTerminatingEndpoints` and
`KubeProxyDrainingTerminatingNodes` all concern whether a terminating Pod, or a Pod on a
terminating Node, still gets traffic. Read them against `virtual-ips.md:227-230` — the `ipvs`
backend "was never able to implement all of the edge cases of Kubernetes Service functionality
correctly." These three ladders are three of those edge cases arriving as work, each one taking
three to four releases, on a mode that was already GA. A post announcing GA has no way to see this
coming, and it is the concrete content of the pin's otherwise abstract complaint.

**One file's rows overlap, and the transcription says so rather than tidying it.**
`KubeProxyDrainingTerminatingNodes` has `alpha` with `toVersion: "1.30"` and `beta` with
`fromVersion: "1.30"` — the same release in both rows. The table prints what the file says,
because the columns are a lossless transcription of the `stages:` list and correcting an
overlapping boundary would be inventing a fact the tree does not carry. Treat v1.30 as ambiguous
in this gate and go to the release notes if it matters.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair): a control-plane node at
`10.10.10.130` and a worker at `10.10.10.131`. Two nodes, for two reasons that are both in the
post. Four of the eleven ipset sets exist only to serve `externalTrafficPolicy=Local`, which is
meaningless with one node because every endpoint is local. And `--ipvs-exclude-cidrs` and the
"can't distinguish kube-proxy created IPVS rules from user original IPVS rules" problem are only
visible if you can put a rule on one node and not the other. Bring it up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting `topology=pair`,
then [the node baseline](../../strands/lab-topologies.md#node-baseline-steps) on both, then
`ssh zain@10.10.10.130`.

Say plainly what this topology cannot show. Nothing here tests the post's thesis. Two nodes and a
handful of Services cannot distinguish a hash table from an in-kernel rule list, and the 2,000
Services and 20,000 iptables records the post's arithmetic needs are three orders of magnitude
past a 4-vCPU guest. Step 13 measures the *shape* of the static-rule claim by adding Services and
counting, which is a different and much weaker test than the one the post makes, and it says so.
What this lab is good for is the design sections: the interface, the sets, the cardinalities, the
schedulers, the affinity timeout, and the flags. Those are all checkable at two nodes and one
Service, and they are the half of the post that the documentation no longer carries.

One more thing to say out loud before you start: **this exercise has an expiry date the pin
states.** `ipvs` mode is disabled by default from v1.40 and removed in v1.43
(`virtual-ips.md:212-214`). If the `$V` you installed is v1.40 or later, step 4 will need the
`KubeProxyIPVS` gate that step 2 shows the binary does not advertise; if it is v1.43 or later,
`--proxy-mode=ipvs` will be rejected and steps 4 through 14 have nothing to run against. That is
not a defect in the exercise. It is the exercise's subject arriving on schedule, and step 1 pins
down which case you are in before anything else happens.

**Do**

1. Establish which release you are on and what it means for the rest of this file. Everything
   downstream depends on the answer:

   ```
   kubectl version -o json | grep -E 'gitVersion|minor' | head -4
   kubectl -n kube-system get ds kube-proxy -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
   ```

2. Ask the binary itself about the post's six parameters and about the gate the deprecation notice
   names. Run this against the running DaemonSet's own image so the answer is about your cluster
   and not about the pin:

   ```
   P=$(kubectl -n kube-system get pod -l k8s-app=kube-proxy -o name | head -1)
   kubectl -n kube-system exec $P -- kube-proxy --help 2>&1 | grep -c -- '--ipvs-'
   kubectl -n kube-system exec $P -- kube-proxy --help 2>&1 | grep -o -- '--ipvs-[a-z-]*' | sort -u
   kubectl -n kube-system exec $P -- kube-proxy --help 2>&1 | grep -c -- '--cleanup-ipvs'
   kubectl -n kube-system exec $P -- kube-proxy --help 2>&1 | grep -A2 -- '--cleanup '
   kubectl -n kube-system exec $P -- kube-proxy --help 2>&1 | grep -c 'KubeProxyIPVS'
   ```

3. Prepare the node, and count how many of the post's five kernel modules the kernel still answers
   to. Do this on **both** nodes; kube-proxy runs on both and a mode change applies to both:

   ```
   sudo apt-get update && sudo apt-get install -y ipvsadm ipset
   for m in ip_vs ip_vs_rr ip_vs_wrr ip_vs_sh nf_conntrack_ipv4; do
     printf '%-18s ' "$m"; sudo modprobe $m 2>&1 && echo ok || true
   done
   lsmod | grep -c '^ip_vs'
   sudo sysctl net.ipv4.vs.conn_reuse_mode
   ```

4. Switch the mode. kube-proxy reads a ConfigMap, so this is an edit and a restart rather than a
   flag, which is itself the answer to the post's `KUBE_PROXY_MODE` instruction:

   ```
   kubectl -n kube-system get cm kube-proxy -o jsonpath='{.data.config\.conf}' | grep -E '^mode:|^ipvs:' -A 9
   kubectl -n kube-system get cm kube-proxy -o yaml > /tmp/kp-orig.yaml
   sed -i '/resourceVersion:/d' /tmp/kp-orig.yaml
   cp /tmp/kp-orig.yaml /tmp/kp-ipvs.yaml
   sed -i 's/^\( *\)mode: ""$/\1mode: "ipvs"/; s/^\( *\)mode: iptables$/\1mode: ipvs/' /tmp/kp-ipvs.yaml
   grep -n 'mode:' /tmp/kp-ipvs.yaml
   kubectl -n kube-system replace -f /tmp/kp-ipvs.yaml
   kubectl -n kube-system rollout restart ds kube-proxy
   kubectl -n kube-system rollout status ds kube-proxy --timeout=90s
   kubectl -n kube-system logs -l k8s-app=kube-proxy --tail=20 | grep -i 'ipvs\|proxy mode\|Using'
   ```

5. Look for the interface the post's first design section promises, and read its flags:

   ```
   ip -o addr show kube-ipvs0
   ip -d link show kube-ipvs0
   ```

6. Create the post's Service shape — Service port 3080 in front of a different container port,
   which is the mapping the post's `Masq` claim rests on — and read the virtual
   server it produces. This is the post's own worked example, on your own cluster:

   ```
   kubectl create deploy nginx-svc --image=nginx --replicas=2
   kubectl expose deploy nginx-svc --name=nginx-service --port=3080 --target-port=80
   kubectl get svc nginx-service -o wide
   kubectl get endpointslices -l kubernetes.io/service-name=nginx-service -o wide
   sudo ipvsadm -ln | grep -A3 "$(kubectl get svc nginx-service -o jsonpath='{.spec.clusterIP}')"
   ```

7. Test the two cardinality claims. `1:N` needs a Service with more than one IP, and `1:1` needs a
   replica count you change:

   ```
   sudo ipvsadm -ln | grep -c '^TCP\|^UDP'
   kubectl patch svc nginx-service -p '{"spec":{"externalIPs":["10.10.10.199"]}}'
   sudo ipvsadm -ln | grep -c '^TCP\|^UDP'
   ip -o addr show kube-ipvs0 | wc -l
   kubectl scale deploy nginx-svc --replicas=4
   sudo ipvsadm -ln | grep -c '^  ->'
   ```

8. Port mapping and the `Masq` forwarding method — the post's claim that only NAT mode supports it:

   ```
   sudo ipvsadm -ln | grep -B2 'Masq' | head -8
   sudo ipvsadm -ln --stats | head -6
   ```

9. Session affinity, first as the post shows it and then as the pin lets you change it — a thing
   the post's flag-and-implementation framing had no way to offer:

   ```
   kubectl patch svc nginx-service -p '{"spec":{"sessionAffinity":"ClientIP"}}'
   sudo ipvsadm -ln | grep 'persistent'
   kubectl patch svc nginx-service -p '{"spec":{"sessionAffinityConfig":{"clientIP":{"timeoutSeconds":600}}}}'
   sudo ipvsadm -ln | grep 'persistent'
   kubectl explain service.spec.sessionAffinityConfig.clientIP.timeoutSeconds
   ```

10. The eleven-row table, checked. This is the post's largest artifact and the pin says nothing
    about it, so the node is the only witness:

    ```
    sudo ipset list -n | sort
    sudo ipset list -n | wc -l
    for s in KUBE-CLUSTER-IP KUBE-LOOP-BACK KUBE-EXTERNAL-IP KUBE-LOAD-BALANCER \
             KUBE-LOAD-BALANCER-LOCAL KUBE-LOAD-BALANCER-FW KUBE-LOAD-BALANCER-SOURCE-CIDR \
             KUBE-NODE-PORT-TCP KUBE-NODE-PORT-LOCAL-TCP KUBE-NODE-PORT-UDP \
             KUBE-NODE-PORT-LOCAL-UDP; do
      printf '%-32s %s\n' "$s" "$(sudo ipset list -n | grep -qx "$s" && echo present || echo MISSING)"
    done
    sudo ipset list KUBE-CLUSTER-IP | tail -6
    ```

11. Change the scheduler, using a value the post's list does not have, to confirm the pin's longer
    list is the real one:

    ```
    kubectl -n kube-system get cm kube-proxy -o jsonpath='{.data.config\.conf}' | grep -A3 '^ipvs:'
     sed -i 's/^\( *\)scheduler: ""$/\1scheduler: "lblcr"/' /tmp/kp-ipvs.yaml
    grep -n 'scheduler:' /tmp/kp-ipvs.yaml
    kubectl -n kube-system replace -f /tmp/kp-ipvs.yaml
    kubectl -n kube-system rollout restart ds kube-proxy
    kubectl -n kube-system rollout status ds kube-proxy --timeout=90s
    sudo ipvsadm -ln | grep -E '^TCP|^UDP' | head -4
    ```

12. Look for the post's forecast, and then for what the project shipped instead. Neither the
    annotation nor the field exists; the replacement is not on the Service at all:

    ```
    kubectl annotate svc nginx-service ipvs.kubernetes.io/scheduler=sed
    sudo ipvsadm -ln | grep -E '^TCP|^UDP' | head -4
    kubectl explain service.spec | grep -ci 'topologyKeys\|scheduler'
    kubectl explain service.spec.trafficDistribution
    kubectl get endpointslices -l kubernetes.io/service-name=nginx-service -o yaml | grep -A4 'hints:' || echo 'no hints on this slice'
    ```

13. The static-rule claim, measured as far as two nodes allow. Count first, then add Services, then
    count again — and read the numbers as a shape, not as a scale test:

    ```
    sudo iptables-save | grep -c '^-A KUBE-'
    sudo ipvsadm -ln | grep -c '^TCP\|^UDP'
    for i in $(seq 1 20); do kubectl expose deploy nginx-svc --name=fan-$i --port=$((9000+i)) --target-port=80 >/dev/null; done
    kubectl get svc --no-headers | wc -l
    sudo iptables-save | grep -c '^-A KUBE-'
    sudo ipvsadm -ln | grep -c '^TCP\|^UDP'
    ```

14. The two-node payoff: a NodePort with `externalTrafficPolicy: Local`, which is what four of the
    post's eleven sets exist for. Run the `ipset` half on the **worker** as well as the
    control-plane node:

    ```
    kubectl patch svc nginx-service -p '{"spec":{"type":"NodePort","externalTrafficPolicy":"Local"}}'
    kubectl get svc nginx-service -o jsonpath='{.spec.ports[0].nodePort}{"\n"}'
    sudo ipset list KUBE-NODE-PORT-LOCAL-TCP | tail -4
    sudo ipset list KUBE-NODE-PORT-TCP | tail -4
    kubectl get pod -l app=nginx-svc -o wide
    ```

15. Put the cluster back, and watch what the post's `--cleanup-ipvs` successor does and does not
    remove:

    ```
    kubectl -n kube-system replace -f /tmp/kp-orig.yaml
    kubectl -n kube-system rollout restart ds kube-proxy
    kubectl -n kube-system rollout status ds kube-proxy --timeout=90s
    sudo ipvsadm -ln | head -5
    ip -o addr show kube-ipvs0 || echo 'kube-ipvs0 gone'
    sudo ipset list -n | grep -c '^KUBE-'
    ```

**Expect**

Step 1 is the gate on everything else. Below v1.40 the mode is deprecated and still on by default,
and steps 4 through 14 run as written. At v1.40 or above, step 4's rollout will report the mode
falling back and the logs will say so; add `KubeProxyIPVS=true` to the ConfigMap's
`featureGates:` and note that you found the gate's name in prose and not in step 2's output. At
v1.43 or above, stop after step 3 and read the rest as archaeology — which is the honest outcome
and worth recording, because the census row for this post was written against a pin where the mode
still ran.

Step 2 should print **eight** `--ipvs-*` flags where the post documents four, and the four extras
are `--ipvs-strict-arp`, `--ipvs-tcp-timeout`, `--ipvs-tcpfin-timeout` and `--ipvs-udp-timeout`.
`--cleanup-ipvs` counts **zero**; `--cleanup` is there instead, and its help text names iptables
and ipvs together. The `KubeProxyIPVS` count is the one to sit with: **zero**, in the complete gate
list of the binary the docs tell you to set it on.

Step 3 is where the post's kernel-module list stops matching the kernel. `ip_vs`, `ip_vs_rr`,
`ip_vs_wrr` and `ip_vs_sh` load. `nf_conntrack_ipv4` is the interesting one — modern kernels do not
carry it under that name, so expect `modprobe` to fail on the fifth of five, and expect
`lsmod | grep -c '^ip_vs'` to be non-zero anyway. The post's prerequisite list is 80% correct and
the failing 20% does not stop the mode working, which is why nobody noticed. `conn_reuse_mode`
prints a value, and it is the sysctl that `kernel-version-requirements.md:39` files under pod
sysctls in the safe set while `sysctl-cluster.md:74-87` does not list it.

Step 4's logs are the confirmation that the mode changed; grep for the line naming the proxier. If
the rollout wedges, the usual cause is the `sed` having missed the `mode:` line's indentation, so
check step 4's `grep -n 'mode:'` output before restarting — and `/tmp/kp-orig.yaml`
is your way back, and step 15 uses it.

Step 5 is the post's screenshot, eight years later. `kube-ipvs0` exists, carries `NOARP`, and is
`state DOWN` with no route through it — the post's `<BROADCAST,NOARP> ... state DOWN` is still
exactly what you see, and `ip -o addr show` lists one address per Service IP on the node. This is
the single fact in the post that the pin names only once, inside `strictARP`'s description.

Step 6 gives you the post's `TCP <clusterIP>:3080 rr` with two real servers on port 80. The
`endpointslices` line is the correction to the post's vocabulary: the object behind the `1:1` rule
is an EndpointSlice, and `Endpoints` is deprecated from v1.33.

Step 7 is the `1:N` and `1:1` rules, measured. Adding an external IP takes the virtual-server count
up by one and the `kube-ipvs0` address count up by one, because the post's rule is per Service *IP*
and not per Service. Scaling to four replicas takes the real-server count to four. Both rules hold.

Step 8 prints `Masq` against every real server, which is the post's NAT-mode claim: 3080 in front
of 80 is only possible because the forwarding method rewrites the port.

Step 9 first prints `persistent 10800` — the post's 180 minutes, unchanged — and then `persistent
600`, which the post could not have shown you, because in 2018 the timeout was a property of the
proxier and now it is a field on the Service. Read `kubectl explain`'s default line and note that
10800 is documented at the API rather than in the IPVS reference.

Step 10 is the payoff of the whole exercise. Expect most of the eleven names to be **MISSING** and
expect a longer list of sets that the post does not name — the set naming and partitioning were
reworked, and the pin records none of it, so the diff between the post's table and `ipset list -n`
is a fact that exists only on your node. Write down the two counts. `KUBE-CLUSTER-IP` should be
present and its members should be your Service IP-and-port pairs, which is the one row of the
eleven you can confirm against the post's `usage` column.

Step 11 should show the scheduler change taking effect in the third column of `ipvsadm`'s output,
with `lblcr` — a value the post's six-item list does not contain and the pin's eleven-item list
does. If your build rejects it, that is worth recording too: it would mean the pin's list is ahead
of the binary, which is the reverse of the usual direction.

Step 12 is the post's forecast, answered. The annotation is accepted — annotations always are —
and the scheduler does not change, which is the whole lesson: an annotation that applies cleanly
and does nothing. `kubectl explain service.spec` has no `topologyKeys` and no scheduler field.
`trafficDistribution` is the field that does exist, and the `hints:` grep on the EndpointSlice
shows where the topology decision actually landed: computed by the control plane and written into
the slice, not declared by whoever wrote the Service. That is `ServiceTopology` deprecated at alpha
and `TopologyAwareHints` locked on, seen from the cluster instead of from the ladder.

Step 13 will not settle the post's thesis and should not be read as if it might. What it does show
is the shape: adding twenty ClusterIP Services takes the virtual-server count up by twenty, while
the `KUBE-` iptables rule count moves by a small constant or not at all. That is the post's
"the number of iptables rules is static" — visible in the direction of the claim if not at the
magnitude that made it worth writing.

Step 14 needs both nodes to be interesting. `KUBE-NODE-PORT-LOCAL-TCP` should carry the node port
only where a backing Pod is actually running, and `KUBE-NODE-PORT-TCP` should carry it on both. If
your build has renamed these — likely, given step 10 — find the successor by name in
`ipset list -n` and compare members. The four `-LOCAL-` rows in the post's table are the only part
of it that a single-node cluster cannot test at all.

Step 15 closes the loop on `--cleanup-ipvs`. Reverting the ConfigMap and restarting is enough to
put the cluster back on iptables, but expect `kube-ipvs0` and at least some `KUBE-` ipsets to
**still be there** afterwards: kube-proxy does not tear down the previous mode's artifacts on a
mode switch, which is precisely the problem `--cleanup` exists for and precisely why
`kubeadm reset` warns that it "does not clean any iptables, nftables or IPVS rules applied"
(`kubeadm-reset.md:57`) and `create-cluster-kubeadm.md:487-491` tells you to run `ipvsadm -C` by
hand. The post's flag was renamed; the problem it names was not solved.

**Read on** — three questions the pinned tree can answer, and one it cannot.

1. `virtual-ips.md:223-240` says the `ipvs` backend "was never able to implement all of the edge
   cases of Kubernetes Service functionality correctly" without naming one. The ladder above offers
   three candidates in `EndpointSliceTerminatingCondition`, `ProxyTerminatingEndpoints` and
   `KubeProxyDrainingTerminatingNodes`. Read those three gate bodies against the `nftables`
   migration notes at `:312-367`, which list four behavioural differences by name, and ask why the
   mode being replaced gets an unnamed complaint while the mode replacing it gets an itemised list.
2. `kubeadm-init.md:242-250` answers "how do I enable IPVS with kubeadm" with a link to
   `pkg/proxy/ipvs/README.md` on the `master` branch. Compare that against how the same page
   answers the two questions either side of it (`:244-246`, `:252-256`), both of which point at
   versioned documentation pages, and ask what it means that the one question with a
   source-tree answer is the one about a deprecated mode.
3. The eight fields of `KubeProxyIPVSConfiguration` at `kube-proxy-config.v1alpha1.md:893-976` are
   every one of them marked `[Required]`. Read that against `mode` at `:599-604`, also `[Required]`,
   and against a mode whose removal release is stated at `virtual-ips.md:214`, and ask what
   `[Required]` means in a generated config-API reference — a promise about your input, or an
   artifact of how the page was produced.
4. The unanswerable one. Every design section in this post describes a mechanism that is still
   running on the node in step 5 and step 10 and is described in no current documentation. The
   pinned tree cannot tell you whether that is deliberate. There is no page saying "the ipset
   partitioning is an implementation detail and will not be documented", and no page saying it was
   removed from the docs when the mode was deprecated; the sets are simply not mentioned, in a
   reference that documents eight flags for configuring the mode they belong to. So the question
   that cannot be settled from the archive is whether the explanation was ever *meant* to be
   documentation. If the design sections were always taken — the post's own framing is "a deep
   dive", not a reference — as a one-time account of a decision, then nothing went wrong here and
   the blog is doing the job the docs never claimed. If they were the only account and everyone
   assumed the reference would pick them up, then a maintained task page is standing on a 2018 blog
   post because of an omission nobody noticed for eight years. `nodelocaldns.md:117-118` is
   evidence for the second reading and not proof of it, and this exercise cannot get further than
   that.

Sibling exercises worth reading first, both backward. The gates that carried this mode, the values
`--proxy-mode` accepts, and the argument about why a slower default outlasted a faster option are
all in the 1.1 release-announcement exercise
([`../2015/10-kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community.md`](../2015/10-kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community.md)),
which is the other half of this post and should be read as one piece with it. And the pattern in
which a prose page instructs you to set a feature gate that the component's own reference does not
list turns up first, in the same year, in the CSI beta exercise
([`02-container-storage-interface-beta.md`](02-container-storage-interface-beta.md)) — two
independent instances thirteen weeks apart in 2018 is enough to call it a class rather than a typo.

**Teardown** — the ConfigMap is the thing that must go back; everything else is objects and node
state:

```
kubectl -n kube-system get cm kube-proxy -o jsonpath='{.data.config\.conf}' | grep '^mode:'
kubectl delete svc nginx-service $(kubectl get svc -o name | grep 'fan-') --ignore-not-found
kubectl delete deploy nginx-svc --ignore-not-found
sudo ipvsadm -C
sudo ipset list -n | grep '^KUBE-' | xargs -r -n1 sudo ipset destroy
sudo ip link delete kube-ipvs0 2>/dev/null || true
rm -f /tmp/kp-orig.yaml /tmp/kp-ipvs.yaml
```

Run the `mode:` check **first** and confirm it does not say `ipvs` before you delete anything: if
step 15 did not take, the three node-level commands will be fighting a running proxier that
recreates what you remove, and the loop will look like it failed when it is working. The last three
commands are the manual `--cleanup` the pin tells you to perform by hand, and they need running on
**both** nodes. Then
[tear the topology down](../../strands/lab-topologies.md#teardown).
