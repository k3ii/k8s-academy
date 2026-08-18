# Phase 9 — Service mesh & L7

> **2–3 weeks.** The honest note first: this is the **least load-bearing phase for control-plane mastery** and the second-cheapest to cut ([#10](https://github.com/k3ii/k8s-academy/issues/10)). Istio teaches **Envoy and xDS**, not Kubernetes internals — the apiserver, scheduler, kubelet and CNI you spent eight phases inside are all *below* the mesh, untouched by it. Walk it for the one thing it teaches that nothing else does: how an L7 proxy is spliced transparently into a running pod, and what that costs. If time is short, this is where it comes from.
> The range is planning information. **The gate at the bottom decides when the phase is finished.**

| | |
|---|---|
| **Prerequisites** | [P7 Networking](07-networking.md) — the mesh is `iptables`/`netfilter` redirection into a userspace proxy; without P7's `syncProxyRules` and `netns` fluency the interception rules are unreadable. [P4 Controllers](04-controllers.md) — `istiod` is a controller that watches the API and pushes config, and xDS is its reconcile loop over gRPC. |
| **Unlocks** | [P12](12-gitops-platform.md)'s progressive-delivery module — Flagger drives metric-based canaries **through this mesh**; without a mesh it degrades to blunt `maxSurge` rollouts. Cutting P9 partially guts that module ([#10](https://github.com/k3ii/k8s-academy/issues/10)). |
| **Source** | **No k/k area** — like [P0](00-linux-primitives.md), the source is not the Kubernetes tree. Here it is a **live sidecar**: the `iptables-save` output inside a real pod and the Envoy `/config_dump`, read against Envoy's own architecture docs. The "file:line" the capstone demands is a line of a config dump you can re-pull, not a path in `k/k`. |
| **Build track** | **None** ([build mechanics](../strands/build-mechanics.md#artifact-table) lists no P9 artifact). The *Build Your Own Envoy Control Plane* talk is an optional stretch, not a required artifact — this phase reads a config plane, it does not ship one. |
| **Lab** | [`pair`](https://github.com/k3ii/k8s-academy/issues/8), **everything else torn down — a big rock.** `istiod`'s chart default (500m / 2Gi) is **un-installable as shipped here**; it needs an explicit request override, which is itself the phase's first lesson about what a mesh costs. |
| **Strands** | [talks](../strands/talks.md#mesh) · [chaos](../strands/chaos.md#principle) |

---

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

## 2. Modules

There is no reading list from the corpus here — the "source" is a running sidecar and Envoy's own docs. The rule is still archaeology-grade: **every claim resolves to a line of a config dump or an `iptables` rule a hostile reader could re-derive**, never "the mesh handles it."

### Module 9.1 — Envoy's object model, before any mesh (~3 days)

You cannot read a config dump without the object model, so it comes first, from Envoy's docs and the Klein talk — no Istio yet.

**Read** — Envoy's architecture docs (listeners, filter chains, clusters, endpoints, and the threading model) alongside the *Envoy Internals Deep Dive* talk.

> **Question to answer from the source:** trace a single connection through the four objects — **listener → filter chain → cluster → endpoint**. Which object picks the upstream, and which one terminates the downstream connection? Name the doc section.

**Write down** — the four-object path as a diagram, annotated with which thread handles each (the threading model is why a mesh scales *and* why it costs a core per busy sidecar).

### Module 9.2 — Sidecar interception: the `iptables` rules (~4 days)

**The entire internals payload.** Install Istio in **sidecar mode** — the only mode with a pod whose interception you can read directly.

**Do** — inject a sidecar, then `nsenter` into the pod's netns (or `kubectl exec` the sidecar) and run `iptables-save`. Find the `REDIRECT`/`TPROXY` rules in the `ISTIO_*` chains that send inbound traffic to 15006 and outbound to 15001. Map each rule to an arg the `istio-init` container was invoked with.

> **Question to answer from the source (the live pod):** which chain redirects **inbound** vs **outbound**, and which ports/UIDs are *excluded* from redirection so that Envoy's own traffic doesn't loop? Cite the rule.

**Break it** — chaos drill [9.C1](#4-chaos-drills): exclude an app port from redirection (or add it to the exclude list) and watch that traffic bypass the mesh entirely — no mTLS, no telemetry, no policy. The rule that was missing is the proof the mesh is *only* those rules.

**Write down** — the inbound and outbound `REDIRECT` rules with their port numbers, mapped one-to-one to `istio-init`'s args — the interception, reduced to netfilter.

### Module 9.3 — xDS and the config dump (~4 days)

`istiod` is a controller; xDS is how it pushes state to the data plane. Read the result, not the magic.

**Do** — pull the Envoy config with `istioctl proxy-config {listeners,routes,clusters,endpoints}` and the raw admin `/config_dump`. Walk one Service: the **LDS** listener → its **RDS** route config → the **CDS** cluster → the **EDS** endpoints, confirming the final endpoint IPs against `kubectl get endpointslice` (the [P7](07-networking.md) data structure, now consumed by a second reader).

> **Question to answer from the source (the dump):** find the `version_info`/`nonce` on one resource type. What does Envoy send back to `istiod` to **ACK** a push, and what happens to the version on a NACK? Cite the field in the dump.

**Break it** — chaos drill [9.C3](#4-chaos-drills): kill `istiod` and re-pull the dump. The config is *unchanged* and traffic keeps flowing — Envoy serves its last-ACKed state. Then create a new Service and watch it **never appear** in the dump. That gap is control-plane/data-plane separation, observed.

**Write down** — the LDS→RDS→CDS→EDS chain for one Service with the concrete resource names at each hop, and the `version_info` field that carries the ACK.

### Module 9.4 — mTLS and workload identity (~3 days)

The security payload — the part [P10](10-security.md) builds on.

**Do** — pull the sidecar's certificate (`istioctl proxy-config secret`) and decode it. Find the **SPIFFE URI SAN** (`spiffe://…/ns/…/sa/…`) — the pod's identity is its ServiceAccount, not its IP. Then set `PeerAuthentication` to `STRICT` and attempt a plaintext connection.

> **Question to answer from the source (the cert):** what is the exact SPIFFE URI, and which Kubernetes object (not the IP) does each path segment name? Where did the cert come from, and what rotates it?

**Break it** — chaos drill [9.C2](#4-chaos-drills): break mTLS trust (wrong root, or a plaintext client against `STRICT`) and read the rejection at the Envoy layer, not just "connection refused" — the filter that dropped it and why.

**Write down** — the SPIFFE identity decoded to its ServiceAccount, and the observed plaintext-rejection under `STRICT`.

### Module 9.5 — Ambient mode, and Linkerd by contrast (~3 days)

Ambient second — the sidecar-free architecture, **and the OOM escape hatch** when per-pod Envoys won't fit.

**Do** — switch a namespace to ambient and confirm the pods have **no sidecar**. Find `ztunnel` as a per-node DaemonSet and identify where redirection now happens (node-level, not per-pod `iptables`), and where L7 processing goes (a **waypoint** proxy, only when an L7 policy needs one). Watch the *Life of a Packet: Ambient Edition* talk against what you observe.

**Read-and-contrast (never install)** — Linkerd's micro-proxy (`linkerd2-proxy`, Rust, not Envoy). It **cannot coexist with Istio on this node** ([#6](https://github.com/k3ii/k8s-academy/issues/6)), so it is read, not run: what does a purpose-built L7 proxy give up versus Envoy's generality, and what does it win (footprint)?

> **Question to answer from observation:** in ambient, where is the packet redirected and by what — contrasted with module 9.2's per-pod rules? What did moving interception to the node *remove* from every pod?

**Break it** — remove the waypoint from an L7-policied namespace and watch L7 policy silently stop applying while L4 mTLS keeps working — the two planes ambient splits that the sidecar fused.

**Write down** — the ambient redirection point vs the sidecar's, and the one-line statement of what a waypoint is *for*.

---

## 3. Chaos drills

Anchored in [`chaos.md#principle`](../strands/chaos.md#principle). The twist this phase: **the data plane is itself a fault injector** — Envoy's fault filter means the mesh injects its own L7 faults (delay, abort) declaratively, so drill 9.C4 needs no external tool. The other three attack the mesh's own guarantees.

| # | Drill | Mechanism | What you must produce afterwards |
|---|---|---|---|
| 9.C1 | **Bypass interception** | by hand (edit the exclude list) | The app traffic flowing outside the mesh, and the missing `REDIRECT` rule that let it |
| 9.C2 | **Break mTLS trust** | by hand (`STRICT` + plaintext) | The rejection read at the Envoy filter layer, not "connection refused" |
| 9.C3 | **Kill `istiod`** | by hand (`kubectl delete`) | Existing traffic still flowing + a new Service that never reaches the dump — the two planes, separated |
| 9.C4 | **Inject an L7 fault** | mesh-native (`VirtualService` `HTTPFaultInjection`) | A declarative delay/abort applied by Envoy's fault filter, found in the config dump |

9.C1 and 9.C2 stay by-hand because reading the broken rule *is* the lesson; 9.C4 is mesh-native because the point is that the proxy you're studying is also a chaos engine.

---

## 4. Talks

Full entries under [Service mesh internals](../strands/talks.md#mesh).

- **★ Envoy Internals Deep Dive** (Klein, EU 2018) — explicitly advanced, from Envoy's creator: the threading model and the **listener → filter chain → cluster → endpoint** object model. **The prerequisite for reading any config dump** — watch it before module 9.1, not after.
- **★ Life of a Packet: Ambient Edition** (Howard & Mattix, NA 2024) — a packet traced through ambient's `ztunnel` and waypoints with the explicit contrast against sidecar interception. Mechanism the whole way down; the module 9.5 talk.
- **Build Your Own Envoy Control Plane** (Sloka, NA 2020) — xDS from the **server** side (the gRPC discovery streams, LDS/RDS/CDS/EDS, ACK/version semantics). Optional — the cheapest way to stop treating xDS as magic if module 9.3's dump-reading leaves it opaque.
- **Envoy's Using 10GB of Memory and It's All My Fault!** (Sloka, NA 2019, 9:40) — a short, honest memory-blowup postmortem. The concrete face of the header's "`istiod` won't fit as shipped" — a mesh's footprint is a first-class operational fact, not a footnote.

---

## 5. Ecosystem

**Istio** is the one big rock — everything else is torn down for it ([#8](https://github.com/k3ii/k8s-academy/issues/8)).

- **Hands-on:** **sidecar first** ([module 9.2](#module-92--sidecar-interception-the-iptables-rules-4-days)) because it is the only mode whose interception you can read in one pod; **ambient second** ([9.5](#module-95--ambient-mode-and-linkerd-by-contrast-3-days)), which is also the escape hatch when per-pod Envoys exhaust the host.
- **Internals note (required):** the mesh adds **nothing** to the Kubernetes control plane — `istiod` is an ordinary controller watching the API, and the data plane is Envoy processes reached by `iptables` rules. Every capability (mTLS, retries, canaries, telemetry) is an Envoy **filter** configured over xDS. This is why the phase is cuttable: it is a self-contained L7 layer, not a piece of Kubernetes.
- **Maturity:** Istio is **CNCF graduated** (2023); ambient mode reached GA in 2024. **Linkerd** (also graduated) is read-and-contrast only — a Rust micro-proxy that trades Envoy's generality for footprint, and it **cannot coexist** with Istio on `pair` ([#6](https://github.com/k3ii/k8s-academy/issues/6)), so it is never installed.

---

## 6. Capstone

**Pull a config dump from a live sidecar and walk one request through listener → filter chain → cluster → endpoint, then show the `iptables` rules that got the packet into Envoy in the first place.**

One request, end to end, both halves:

1. **Into Envoy** (module 9.2): the `iptables` `REDIRECT` rule — inbound or outbound — that captured the packet, cited by chain and port, mapped to the `istio-init` arg that installed it.
2. **Through Envoy** (module 9.3): the **listener** that accepted it → the **filter chain**/route that matched → the **cluster** it selected → the **endpoint** IP it reached, each pointed at in the `/config_dump`, with the endpoint confirmed against the `EndpointSlice`.

**Cite "file:line" a hostile reader could check** — but here the "file" is a **re-pullable runtime artifact**, not a source path: the config-dump resource name and JSON path at each hop, and the `iptables-save` rule line. A reader re-pulls the dump and the rules and checks every claim. This is the [P2 archaeology standard](../strands/source-archaeology.md#drills) applied to a live proxy instead of a source tree — the one phase where the corpus offers no `k/k` line to cite, so the running system *is* the citation.

---

## 7. Checklist

Concrete, demonstrable, grouped by evidence type. No item says *understand* or *know*.

**Live against a running cluster:**
- [ ] A sidecar's inbound/outbound `REDIRECT` rules read from `iptables-save`, mapped to `istio-init` args (9.2).
- [ ] One Service walked LDS→RDS→CDS→EDS in a real `/config_dump`, endpoints confirmed against the `EndpointSlice` (9.3).
- [ ] `istiod` killed; existing traffic still flowing and a new Service absent from the dump (9.3 / 9.C3).
- [ ] A sidecar cert decoded to its SPIFFE ServiceAccount identity; plaintext rejected under `STRICT` (9.4).
- [ ] Ambient enabled; sidecar-free pods and `ztunnel`/waypoint redirection observed (9.5).

**Written artifacts (each is a module's Write-down):**
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

## 8. Gate

You may advance to [P10](10-security.md) when:

1. **The capstone request is walked end to end** — the `iptables` rule that captured the packet *and* the listener→filter→cluster→endpoint path in your own dump, each cited to a re-pullable line. If you can name the four Envoy objects but cannot find them in your dump, module 9.1 didn't land — **stay here**.
2. **`istiod` was killed and the data plane kept serving** — you can state from observation exactly what stopped (config convergence) and what did not (existing connections). If you cannot separate the two planes, the phase's one irreplaceable lesson is missing.
3. **mTLS is proven at the identity layer** — the SPIFFE SAN decoded to a ServiceAccount and a plaintext connection rejected under `STRICT`, read at the Envoy filter, not as a bare "connection refused."

You can also state, honestly, what this phase did **not** teach: Kubernetes internals. The mesh sat entirely above the control plane you spent eight phases inside. [P10](10-security.md) drops back down — the CVE-driven security incident runs against a component you already installed and disabled, and mTLS identity here becomes the workload-identity groundwork the CKS phase hardens.
