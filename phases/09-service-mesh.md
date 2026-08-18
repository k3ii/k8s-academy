# Phase 9 — Service mesh & L7

> **2–3 weeks.** The honest note first: this is the **least load-bearing phase for control-plane mastery** and the second-cheapest to cut ([#10](https://github.com/k3ii/k8s-academy/issues/10)). Istio teaches **Envoy and xDS**, not Kubernetes internals — the apiserver, scheduler, kubelet and CNI you spent eight phases inside are all *below* the mesh, untouched by it. Walk it for the one thing it teaches that nothing else does: how an L7 proxy is spliced transparently into a running pod, and what that costs. If time is short, this is where it comes from.
> The range is planning information. **The gate at the bottom decides when the phase is finished.**

| | |
|---|---|
| **Prerequisites** | [P7 Networking](07-networking.md) — the mesh is `iptables`/`netfilter` redirection into a userspace proxy; without P7's `syncProxyRules` and `netns` fluency the interception rules are unreadable. [P4 Controllers](04-controllers.md) — `istiod` is a controller that watches the API and pushes config, and xDS is its reconcile loop over gRPC. |
| **Unlocks** | [P12](12-gitops-platform.md)'s progressive-delivery module — Flagger drives metric-based canaries **through this mesh**; without a mesh it degrades to blunt `maxSurge` rollouts. Cutting P9 partially guts that module ([#10](https://github.com/k3ii/k8s-academy/issues/10)). |
| **Source** | **No k/k area** — like [P0](00-linux-primitives.md), the source is not the Kubernetes tree. Here it is a **live sidecar**: the `iptables-save` output inside a real pod and the Envoy `/config_dump`, read against Envoy's own architecture docs. The "file:line" the capstone demands is a line of a config dump you can re-pull, not a path in `k/k`. |
| **Build track** | **None** ([build mechanics](../strands/build-mechanics.md#artifact-table) lists no P9 artifact). The *Build Your Own Envoy Control Plane* talk is an optional stretch, not a required artifact — this phase reads a config plane, it does not ship one. |
| **Lab** | [`pair`](../strands/lab-topologies.md#pair), **everything else torn down — a big rock.** `istiod`'s chart default is **un-installable as shipped here**; it needs an explicit request override, which is itself the phase's first lesson about what a mesh costs. |
| **Labs** | [`labs/09/`](../labs/09/README.md) — 25 exercises, in order. Three of them need no cluster at all, and the index gives the point the topology arrives and the point it goes. |
| **Strands** | [talks](../strands/talks.md#mesh) · [chaos](../strands/chaos.md#principle) |

---

<a id="objectives"></a>
## 1. Objectives

Every one is falsifiable — an artifact, a timed production, or a claim a hostile reader could check against a live cluster or a config dump. *understand* and *know* appear nowhere.

By the end you can:

1. **Read a live sidecar's `iptables-save`** and name which rules redirect inbound (→ 15006) and outbound (→ 15001) traffic into Envoy, mapping each rule to the `istio-init` container's args.
2. **Walk one request through a config dump** — listener → filter chain → route → cluster → endpoint — pointing at each object in the JSON.
3. **Explain the four xDS resource types** (LDS/RDS/CDS/EDS) and the version/ACK semantics, tracing one Service from its listener to its EDS endpoints in *your own* dump.
4. **Kill `istiod`** and state, from observation, exactly what breaks and what keeps serving — the control-plane/data-plane separation the mesh exists to demonstrate.
5. **Decode the SPIFFE identity** in a sidecar's certificate SAN, flip `PeerAuthentication` to `STRICT`, and observe plaintext rejected at the mesh boundary.
6. **Contrast sidecar and ambient interception** — where redirection happens (per-pod `iptables` vs node `ztunnel`) and where L7 lives (in-pod Envoy vs a waypoint proxy).
7. **State plainly what this phase did not teach** — Envoy and xDS, not Kubernetes internals — and why the mesh is the second-cheapest phase to cut.

---

<a id="modules"></a>
## 2. Modules

There is no reading list from the corpus here — the "source" is a running sidecar and Envoy's own docs. The rule is still archaeology-grade: **every claim resolves to a line of a config dump or an `iptables` rule a hostile reader could re-derive**, never "the mesh handles it."

<a id="m9-1"></a>
### Module 9.1 — Envoy's object model, before any mesh (~3 days)

You cannot read a config dump without the object model, so it comes first, from Envoy's docs and the Klein talk — no Istio yet, and for these three days no cluster either.

**Read** — Envoy's architecture docs (listeners, filter chains, clusters, endpoints, and the threading model) alongside the *Envoy Internals Deep Dive* talk.

> **Question to answer from the source:** trace a single connection through the four objects — **listener → filter chain → cluster → endpoint**. Which object picks the upstream, and which one terminates the downstream connection? Name the doc section.

**Labs** — [The four objects, in a file you typed](../labs/09/01-four-objects-in-a-file-you-typed.md) · [A dump with nothing pushed into it](../labs/09/02-a-dump-with-nothing-pushed-into-it.md) · [Which object owns the failure](../labs/09/03-which-object-owns-the-failure.md)

---

<a id="m9-2"></a>
### Module 9.2 — Sidecar interception: the `iptables` rules (~4 days)

**The entire internals payload.** Istio goes on in **sidecar mode** — the only mode with a pod whose interception you can read directly. The install is where the phase's footprint problem becomes concrete rather than predicted, and the exercises resolve it before they inject anything.

> **Question to answer from the source (the live pod):** which chain redirects **inbound** vs **outbound**, and which ports/UIDs are *excluded* from redirection so that Envoy's own traffic doesn't loop? Cite the rule.

> **Question to answer from the cluster:** the pod has two containers and the Deployment's template has one. Which object rewrote it, and what happens to a pod created while that object's backend is gone? The second half is [module 9.3](#m9-3)'s drill, predicted here.

**Labs** — [The request that does not fit](../labs/09/04-the-request-that-does-not-fit.md) · [A pod the webhook rewrote](../labs/09/05-a-pod-the-webhook-rewrote.md) · [Interception reduced to netfilter](../labs/09/06-interception-reduced-to-netfilter.md) · [The UID that breaks the loop](../labs/09/07-the-uid-that-breaks-the-loop.md) · [9.C1 — a port outside the mesh](../labs/09/08-9c1-a-port-outside-the-mesh.md)

---

<a id="m9-3"></a>
### Module 9.3 — xDS and the config dump (~4 days)

`istiod` is a controller; xDS is how it pushes state to the data plane. Read the result, not the magic. The endpoints at the far end are [P7](07-networking.md)'s `EndpointSlice` data, now consumed by a second reader.

> **Question to answer from the source (the dump):** find the `version_info`/`nonce` on one resource type. What does Envoy send back to `istiod` to **ACK** a push, and what happens to the version on a NACK? Cite the field in the dump.

> **Question to answer by counting:** one Service produces objects of how many resource types, and which of those types moves when you only change the *number* of pods behind it? The answer is what makes EDS a separate stream rather than a field.

**Labs** — [The same dump, now dynamic](../labs/09/09-the-same-dump-now-dynamic.md) · [One Service, four resource types](../labs/09/10-one-service-four-resource-types.md) · [An ACK and a NACK](../labs/09/11-an-ack-and-a-nack.md) · [A scale event is one resource type](../labs/09/12-a-scale-event-is-one-resource-type.md) · [9.C4 — a delay you declared](../labs/09/13-9c4-a-delay-you-declared.md) · [9.C3 — `istiod` killed, and the planes come apart](../labs/09/14-9c3-istiod-killed-and-the-planes-come-apart.md)

---

<a id="m9-4"></a>
### Module 9.4 — mTLS and workload identity (~3 days)

The security payload — the part [P10](10-security.md) builds on.

> **Question to answer from the source (the cert):** what is the exact SPIFFE URI, and which Kubernetes object (not the IP) does each path segment name? Where did the cert come from, and what rotates it?

> **Question to answer from the listener:** `STRICT` is enforced by *removing* something from the inbound listener rather than by adding a check. What is removed, and what does the client see because of it? Then: which addresses is `STRICT` actually a statement about? One of the four probes in [the boundary exercise](../labs/09/17-the-boundary-is-the-netns.md) succeeds in plaintext under `STRICT`, and the reason it does is [P10](10-security.md)'s opening, not this phase's.

**Labs** — [A certificate that names a ServiceAccount](../labs/09/15-a-certificate-that-names-a-serviceaccount.md) · [`STRICT`, and the plaintext refused](../labs/09/16-strict-and-the-plaintext-refused.md) · [The boundary is the netns](../labs/09/17-the-boundary-is-the-netns.md) · [9.C2 — a root that no longer signs](../labs/09/18-9c2-a-root-that-no-longer-signs.md)

---

<a id="m9-5"></a>
### Module 9.5 — Ambient mode, and Linkerd by contrast (~3 days)

Ambient second — the sidecar-free architecture, **and the OOM escape hatch** when per-pod Envoys won't fit. The module opens by measuring the thing ambient is an escape from, on a node small enough that the measurement has an end.

**Watch** — *Life of a Packet: Ambient Edition*, against what you observe on your own node rather than against its slides.

**Read-and-contrast (never install)** — Linkerd's micro-proxy (`linkerd2-proxy`, Rust, not Envoy). It **cannot coexist with Istio on this node** ([#6](https://github.com/k3ii/k8s-academy/issues/6)), so it is read, not run: what does a purpose-built L7 proxy give up versus Envoy's generality, and what does it win (footprint)?

> **Question to answer from observation:** in ambient, where is the packet redirected and by what — contrasted with module 9.2's per-pod rules? What did moving interception to the node *remove* from every pod, and what is now holding the pod's sockets?

> **Question to answer from the policy:** an L7 rule in a namespace with no L7 proxy in the path — does it fail open or closed? Record what your version did rather than what the docs say it should, then remove the proxy again and find the object that reports the loss. Nothing does.

**Labs** — [What a sidecar costs](../labs/09/19-what-a-sidecar-costs.md) · [A namespace with no sidecars](../labs/09/20-a-namespace-with-no-sidecars.md) · [The same curve, flat](../labs/09/21-the-same-curve-flat.md) · [The waypoint an L7 policy needs](../labs/09/22-the-waypoint-l7-policy-needs.md) · [The waypoint removed, and the silence](../labs/09/23-the-waypoint-removed-and-the-silence.md) · [Linkerd read and never installed](../labs/09/24-linkerd-read-and-never-installed.md)

---

<a id="chaos"></a>
## 3. Chaos drills

Anchored in [`chaos.md#principle`](../strands/chaos.md#principle). The twist this phase: **the data plane is itself a fault injector** — Envoy's fault filter means the mesh injects its own L7 faults (delay, abort) declaratively, so drill 9.C4 needs no external tool. The other three attack the mesh's own guarantees.

| # | Drill | What you must produce afterwards |
|---|---|---|
| 9.C1 | [**Bypass interception**](../labs/09/08-9c1-a-port-outside-the-mesh.md) | The app traffic flowing outside the mesh, the missing `REDIRECT` rule that let it, and the header that stopped arriving because of it |
| 9.C2 | [**Break mTLS trust**](../labs/09/18-9c2-a-root-that-no-longer-signs.md) | Two workloads holding certificates from two different roots, and which half of the pair stopped working — recorded as observed, because the direction is version-dependent |
| 9.C3 | [**Kill `istiod`**](../labs/09/14-9c3-istiod-killed-and-the-planes-come-apart.md) | Existing traffic still flowing, a new Service that never reaches the dump, and a pod that cannot be created at all — the two planes, separated, plus the seam that is neither |
| 9.C4 | [**Inject an L7 fault**](../labs/09/13-9c4-a-delay-you-declared.md) | A declarative delay applied by Envoy's fault filter, found in the config dump — and the filter shown to have been in the chain before you declared anything |

All four are by-hand or mesh-native, so **no chaos tooling is installed this phase** — which is also the only reason the mesh fits. 9.C1 and 9.C2 stay by-hand because reading the broken rule *is* the lesson; 9.C4 is mesh-native because the point is that the proxy you're studying is also a chaos engine.

---

<a id="talks"></a>
## 4. Talks

Full entries under [Service mesh internals](../strands/talks.md#mesh).

- **★ Envoy Internals Deep Dive** (Klein, EU 2018) — explicitly advanced, from Envoy's creator: the threading model and the **listener → filter chain → cluster → endpoint** object model. **The prerequisite for reading any config dump** — watch it before module 9.1, not after.
- **★ Life of a Packet: Ambient Edition** (Howard & Mattix, NA 2024) — a packet traced through ambient's `ztunnel` and waypoints with the explicit contrast against sidecar interception. Mechanism the whole way down; the module 9.5 talk.
- **Build Your Own Envoy Control Plane** (Sloka, NA 2020) — xDS from the **server** side (the gRPC discovery streams, LDS/RDS/CDS/EDS, ACK/version semantics). Optional — the cheapest way to stop treating xDS as magic if module 9.3's dump-reading leaves it opaque.
- **Envoy's Using 10GB of Memory and It's All My Fault!** (Sloka, NA 2019, 9:40) — a short, honest memory-blowup postmortem. The concrete face of the header's "`istiod` won't fit as shipped" — a mesh's footprint is a first-class operational fact, not a footnote.

---

<a id="ecosystem"></a>
## 5. Ecosystem

**Istio** is the one big rock — everything else is torn down for it ([#8](https://github.com/k3ii/k8s-academy/issues/8)).

- **Hands-on:** **sidecar first** ([module 9.2](#m9-2)) because it is the only mode whose interception you can read in one pod; **ambient second** ([9.5](#m9-5)), which is also the escape hatch when per-pod Envoys exhaust the host.
- **Internals note (required):** the mesh adds **nothing** to the Kubernetes control plane — `istiod` is an ordinary controller watching the API, and the data plane is Envoy processes reached by `iptables` rules. Every capability (mTLS, retries, canaries, telemetry) is an Envoy **filter** configured over xDS. This is why the phase is cuttable: it is a self-contained L7 layer, not a piece of Kubernetes.
- **Maturity:** Istio is **CNCF graduated** (2023); ambient mode reached GA in 2024. **Linkerd** (also graduated) is read-and-contrast only — a Rust micro-proxy that trades Envoy's generality for footprint, and it **cannot coexist** with Istio on `pair` ([#6](https://github.com/k3ii/k8s-academy/issues/6)), so it is never installed.

---

<a id="capstone"></a>
## 6. Capstone

**Pull a config dump from a live sidecar and walk one request through listener → filter chain → cluster → endpoint, then show the `iptables` rules that got the packet into Envoy in the first place.**

One request, end to end, both halves:

1. **Into Envoy** (module 9.2): the `iptables` `REDIRECT` rule — inbound or outbound — that captured the packet, cited by chain and port, mapped to the `istio-init` arg that installed it.
2. **Through Envoy** (module 9.3): the **listener** that accepted it → the **filter chain**/route that matched → the **cluster** it selected → the **endpoint** IP it reached, each pointed at in the `/config_dump`, with the endpoint confirmed against the `EndpointSlice`.

**Cite "file:line" a hostile reader could check** — but here the "file" is a **re-pullable runtime artifact**, not a source path: the config-dump resource name and JSON path at each hop, and the `iptables-save` rule line. A reader re-pulls the dump and the rules and checks every claim. This is the [P2 archaeology standard](../strands/source-archaeology.md#drills) applied to a live proxy instead of a source tree — the one phase where the corpus offers no `k/k` line to cite, so the running system *is* the citation.

**Lab** — [One request, both halves](../labs/09/25-one-request-both-halves.md), which is also where the topology goes.

---

<a id="checklist"></a>
## 7. Checklist

Concrete, demonstrable, grouped by evidence type. No item says *understand* or *know*.

**Live against a running cluster:**
- [ ] A sidecar's inbound/outbound `REDIRECT` rules read from `iptables-save`, mapped to `istio-init` args (9.2).
- [ ] One Service walked LDS→RDS→CDS→EDS in a real `/config_dump`, endpoints confirmed against the `EndpointSlice` (9.3).
- [ ] `istiod` killed; existing traffic still flowing and a new Service absent from the dump (9.3 / 9.C3).
- [ ] A sidecar cert decoded to its SPIFFE ServiceAccount identity; plaintext rejected under `STRICT` (9.4).
- [ ] Ambient enabled; sidecar-free pods and `ztunnel`/waypoint redirection observed (9.5).

**Written artifacts — each is an exercise's write-down step:**
- [ ] The four-object Envoy path, annotated by thread (9.1).
- [ ] The inbound/outbound `REDIRECT` rules mapped to `istio-init` args (9.2).
- [ ] The LDS→RDS→CDS→EDS chain with concrete resource names + the ACK `version_info` field (9.3).
- [ ] The SPIFFE identity decoded to a ServiceAccount + the observed `STRICT` rejection (9.4).
- [ ] The ambient vs sidecar redirection point + what a waypoint is for (9.5).

**Falsifiable claims — write, then verify:**
- [ ] Why killing `istiod` does not stop existing traffic (control/data-plane separation).
- [ ] Why the mesh adds nothing to the Kubernetes control plane — and is therefore cuttable.
- [ ] What a purpose-built proxy (Linkerd) gives up vs Envoy, and what it wins.

---

<a id="gate"></a>
## 8. Gate

You may advance to [P10](10-security.md) when:

1. **The capstone request is walked end to end** — the `iptables` rule that captured the packet *and* the listener→filter→cluster→endpoint path in your own dump, each cited to a re-pullable line. If you can name the four Envoy objects but cannot find them in your dump, module 9.1 didn't land — **stay here**.
2. **`istiod` was killed and the data plane kept serving** — you can state from observation exactly what stopped (config convergence) and what did not (existing connections). If you cannot separate the two planes, the phase's one irreplaceable lesson is missing.
3. **mTLS is proven at the identity layer** — the SPIFFE SAN decoded to a ServiceAccount and a plaintext connection rejected under `STRICT`, read at the Envoy filter, not as a bare "connection refused."

You can also state, honestly, what this phase did **not** teach: Kubernetes internals. The mesh sat entirely above the control plane you spent eight phases inside. [P10](10-security.md) drops back down — the CVE-driven security incident runs against a component you already installed and disabled, and mTLS identity here becomes the workload-identity groundwork the CKS phase hardens.
