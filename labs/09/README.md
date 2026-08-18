# Labs — Phase 9, service mesh & L7

Twenty-five exercises in the order they are meant to run, for **the phase most likely to
breach the lab's ceiling**. A mesh's control plane, its sidecars, a workload and an
observability stack do not co-reside on [a 5.0GB
topology](../../strands/lab-topologies.md#pair) — so the sequence was costed before it was
written, and [exercise 4](04-the-request-that-does-not-fit.md) carries the whole arithmetic,
including four things a normal mesh install brings that this one declines and why each is
not needed. Nothing about the mesh itself was softened: a real `istiod`, real sidecars, a
real ambient data plane with `ztunnel` and a waypoint, and a capstone that walks one request
from a netfilter rule to an endpoint IP.

Each file states one claim to test or one artifact to produce, links its
[topology](../../strands/lab-topologies.md) rather than restating a footprint, and ends with
a teardown that does two things: **deletes what that exercise created**, then says whether
the topology stays or goes. This phase's teardowns are unusually specific, because its risk
is accretion — a half-broken `nat` table, a five-second fault filter or eight sidecars left
running makes the *next* exercise fail for a reason that has nothing to do with it.

The framing — why each module exists, what to read and the question to answer from it —
stays in [`phases/09-service-mesh.md`](../../phases/09-service-mesh.md). These files hold
only what you type and what you should see.

| # | Exercise | Why it exists |
|---|---|---|
| 1 | [Four objects in a file you typed](01-four-objects-in-a-file-you-typed.md) | The object model is cheaper to learn from twenty lines you wrote than from a 10,000-line dump. |
| 2 | [A dump with nothing pushed into it](02-a-dump-with-nothing-pushed-into-it.md) | Establishes the control: zero `version_info` fields, so the dynamic case has something to differ from. |
| 3 | [Which object owns the failure](03-which-object-owns-the-failure.md) | Kills an upstream and finds the fix belongs to the cluster, not the listener — the object model as a prediction. |
| 4 | [The request that does not fit](04-the-request-that-does-not-fit.md) | The chart default is un-installable here, and the scheduler says so in two clauses. The phase's whole footprint argument lives in this file. |
| 5 | [A pod the webhook rewrote](05-a-pod-the-webhook-rewrote.md) | The Deployment still has one container. Mutation is a property of pod admission, and that is checkable. |
| 6 | [Interception reduced to netfilter](06-interception-reduced-to-netfilter.md) | Four chains, and every port in them is an `istio-init` arg. The module's entire internals payload. |
| 7 | [The UID that breaks the loop](07-the-uid-that-breaks-the-loop.md) | Deletes the exemptions and measures the loop as a counter ratio rather than describing it. |
| 8 | [9.C1 — a port outside the mesh](08-9c1-a-port-outside-the-mesh.md) | The request still returns 200; the identity header is gone. What a bypass looks like when nothing alerts. |
| 9 | [The same dump, now dynamic](09-the-same-dump-now-dynamic.md) | Same object types, one push away. The three counts that separate a config file from a control plane. |
| 10 | [One Service, four resource types](10-one-service-four-resource-types.md) | LDS→RDS→CDS→EDS, ending on a port the Service does not advertise — which proves the last hop is `EndpointSlice` data. |
| 11 | [An ACK and a NACK](11-an-ack-and-a-nack.md) | One `EnvoyFilter` applied, one rejected, and a version that does not move. `istiod` accepts both; the proxy decides. |
| 12 | [A scale event is one resource type](12-a-scale-event-is-one-resource-type.md) | Why xDS is four types and not one, measured from `istiod`'s push counters with no telemetry stack installed. |
| 13 | [9.C4 — a delay you declared](13-9c4-a-delay-you-declared.md) | The fault filter was already in every listener. The chaos engine ships inside the thing being studied. |
| 14 | [9.C3 — `istiod` killed and the planes come apart](14-9c3-istiod-killed-and-the-planes-come-apart.md) | Traffic flows, a new Service is never heard of, and no pod can be created — the third result is the honest limit of "separate planes". |
| 15 | [A certificate that names a ServiceAccount](15-a-certificate-that-names-a-serviceaccount.md) | No DNS name, no IP, one URI — and the projected token it was traded for. |
| 16 | [`STRICT` and the plaintext refused](16-strict-and-the-plaintext-refused.md) | The policy *removes filter chains*. The refusal happens before any HTTP exists to refuse. |
| 17 | [The boundary is the netns](17-the-boundary-is-the-netns.md) | Pod IP refused, `127.0.0.1` not. Where mTLS stops being a property of the Service. |
| 18 | [9.C2 — a root that no longer signs](18-9c2-a-root-that-no-longer-signs.md) | Two workloads, two issuers, one trust bundle — and a recovery that is part of the artifact. |
| 19 | [What a sidecar costs](19-what-a-sidecar-costs.md) | The phase's one deliberate walk toward the node's limit, measured from the kubelet's summary API. |
| 20 | [A namespace with no sidecars](20-a-namespace-with-no-sidecars.md) | Sockets in the pod's netns held by a process in another one, proved by a file descriptor. Not an overlay, not Geneve. |
| 21 | [The same curve, flat](21-the-same-curve-flat.md) | The comparison the ambient claim rests on — and three caveats that keep it honest. |
| 22 | [The waypoint L7 policy needs](22-the-waypoint-l7-policy-needs.md) | An HTTP-shaped rule with no HTTP-aware proxy in the path, then the one Envoy per namespace that fixes it. |
| 23 | [The waypoint removed, and the silence](23-the-waypoint-removed-and-the-silence.md) | The policy stays `Applied` and stops applying. No event, no status, no warning. |
| 24 | [Linkerd, read and never installed](24-linkerd-read-and-never-installed.md) | Four questions answered from a source tree on `forge`, with citations — and a footprint number explicitly not claimed. |
| 25 | [The capstone: one request, both halves](25-one-request-both-halves.md) | Two netfilter rules and four `jq` paths for one `GET`. Ends the phase and releases the topology. |

## Order, topology and what arrives when

**Exercises 1, 2, 3 and 24 need no cluster.** The first three run entirely on
[`forge`](../../strands/lab-topologies.md#build-guest) with a container image and two
`python3 -m http.server` upstreams, which is why the phase's first RAM is spent at
**exercise 4** and not at exercise 1. Exercise 24 is a source clone, and `pair` may be up
and idle beside it.

**One cluster runs exercises 4 through 23 and 25.**
[`pair`](../../strands/lab-topologies.md#pair) comes up at exercise 4 and is destroyed by
[the capstone](25-one-request-both-halves.md). Two workloads — `httpbin` and `sleep` — are
created once at [exercise 5](05-a-pod-the-webhook-rewrote.md) and are the only application
in the phase.

**The data plane changes shape twice.** Sidecar mode from exercise 4, ambient from
[exercise 20](20-a-namespace-with-no-sidecars.md), and back to sidecar at
[the capstone](25-one-request-both-halves.md) — which is a deliberate reinstall, because a
capstone that walks per-pod interception rules needs a data plane that has some. The Gateway
API CRDs arrive at [exercise 22](22-the-waypoint-l7-policy-needs.md) and are the only
cluster-scoped objects the phase adds.

## Exceptions

- **Nothing observability-shaped is installed.** Every objective's evidence is an `iptables` rule, a config dump, an Envoy counter read through `pilot-agent request GET stats`, or `istiod`'s own `:15014/metrics` reached from a pod with `curl`. [Exercise 4](04-the-request-that-does-not-fit.md) costs the addons that were declined and says which exercise would have used each.
- **No Chaos Mesh, for the first time since [P6](../../phases/06-kubelet-node.md).** [The phase's drill table](../../phases/09-service-mesh.md#chaos) makes 9.C4 mesh-native and the other three by-hand, so the tool would cost [582Mi](../../strands/chaos.md#install) to inject faults the mesh injects itself — and using it for 9.C4 would hide the filter being taught.
- **The workload is `httpbin` and `sleep`, not `bookinfo`.** Three Java `reviews` pods demonstrate traffic splitting, which no objective in this phase asks for; `httpbin` echoes its request headers, which is what turns [9.C1](08-9c1-a-port-outside-the-mesh.md) and [the identity exercise](15-a-certificate-that-names-a-serviceaccount.md) into one-line observations.
- **`istiod` is pinned to the control-plane node.** Not for capacity — [it is the only node with room](04-the-request-that-does-not-fit.md) — but so that the worker stays a clean instrument for [the two cost curves](19-what-a-sidecar-costs.md).
- **Exercises 7, 8, 16, 17, 18 and 23 leave the cluster in a deliberately broken state mid-file.** Each ends by proving the repair, not by asserting it: a `200`, a restored fingerprint, a rule back in the chain. Do not skip those last blocks.
- **Two version numbers are recorded rather than quoted.** [Exercise 1](01-four-objects-in-a-file-you-typed.md) records `istioctl version --remote=false` and derives every image tag from it; [exercise 22](22-the-waypoint-l7-policy-needs.md) records the Gateway API release its Istio version expects. Ambient GA — Istio 1.24 or later — is the only hard requirement.
- **Three exercises ask you to record an outcome rather than confirm one**: [the loop's failure mode](07-the-uid-that-breaks-the-loop.md), [the root-replacement direction](18-9c2-a-root-that-no-longer-signs.md), and [an unenforceable L7 policy failing open or closed](22-the-waypoint-l7-policy-needs.md). All three are version-dependent, all three have a version-independent observable beside them, and writing down the outcome you expected instead of the one you got defeats the exercise.
