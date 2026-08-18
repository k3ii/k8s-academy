# Phase 3 — API machinery

> **5–6 weeks.** The heaviest phase and the spine's centre of gravity — the apiserver is the one component every other component is a client of, so this is where reading `k/k` pays its highest dividend.
> The range is planning information. **The gate at the bottom decides when the phase is finished.**

| | |
|---|---|
| **Prerequisites** | [P2](02-etcd.md) — the store the apiserver encodes *onto*. You have already run a three-member cluster, watched Raft elect, and restored from a snapshot, so `--etcd-servers` and peer certs are consolidation here, not new. Critically, the `ErrCompacted → "too old resource version"` chain you traced in etcd is the *same phrase* the watch cache emits from the other side ([module 3.5](#m3-5)). |
| **Unlocks** | [P4](04-controllers.md) — the watch cache you read here is the far end of the informer's watch. [P10](10-security.md) — the aggregation-layer CVE and the webhook/authz surface return there as *security*; here they are *mechanism*, learned first. And every operator, admission policy and CRD in the platform arc rests on this phase. |
| **Source area** | [Area 2 — API machinery](../strands/source-reading.md#area-2-api-machinery), entry point `endpoints/handlers/create.go` — the whole write path in one readable function. `sample-apiserver` is **read, not built** ([#9](https://github.com/k3ii/k8s-academy/issues/9)). |
| **Language** | Go — **four build artifacts** ([artifact table](../strands/build-mechanics.md#artifact-table)): validating webhook → mutating webhook → CRD conversion webhook → `kubectl` plugin. The [`file:line` archaeology standard from P2](../strands/source-archaeology.md#drills) is now assumed, not taught. |
| **Strands** | [source reading](../strands/source-reading.md#area-2-api-machinery) · [build](../strands/build-mechanics.md#artifact-table) · [talks](../strands/talks.md#apiserver) · [chaos](../strands/chaos.md#borrowed-drills) |
| **Labs** | [`labs/03/`](../labs/03/README.md) — forty-five exercises, in order |

---

<a id="objectives"></a>
## 1. Objectives

Every one is falsifiable — an artifact, a timed production, or a claim a hostile reader could check against source or a running cluster. *understand* and *know* appear nowhere.

By the end you can:

1. **Trace one `kubectl apply` through the handler chain**, naming each stage *by the file that implements it*: URL → `requestinfo.go` → `authentication.go` → `authorization.go` → mutating admission → schema validation → validating admission → `storage.Create` → an etcd `Txn`. This is the capstone, derived from `create.go`.
2. **State and cite the admission ordering rule** — *all* mutating plugins run, *then* all validating, never interleaved — pointing at `admission/chain.go` where it is enforced, and explain from `reinvocationcontext.go` why one mutating webhook may be invoked more than once.
3. **Hand-start `kube-apiserver` from flags** (the Very Hard Way) and name what `--etcd-servers`, `--client-ca-file`, `--service-account-issuer` and the aggregation flags each wire up — while reading the very handler the binary is serving.
4. **Build a validating webhook hand-certed end to end**, then change one SAN and recognise `x509: certificate signed by unknown authority` from the apiserver log alone.
5. **Locate the origin of `"too old resource version"` in the apiserver**, in `watch_cache.go`'s ring buffer (`startIndex`/`endIndex`), and connect it by name to the etcd `ErrCompacted` from [P2](02-etcd.md) — the same failure, two layers.
6. **Serve a two-version CRD through a conversion webhook**, name the storage version, and show a round-trip that would break if conversion were not lossless (KEP-598).
7. **Wedge the cluster with a `failurePolicy: Fail` webhook that blocks the write that would fix it**, then recover — and name the escape hatch before you need it.
8. **Contrast three control planes you have run** — hand-wired (Very Hard Way), kubeadm-generated ([P1](01-operate-shallow.md)), and k0s single-binary — naming precisely what k0s collapses into one process.

---

<a id="modules"></a>
## 2. Modules

Reading is [Area 2](../strands/source-reading.md#area-2-api-machinery), the highest essential-to-readable ratio in the corpus, where **sequencing matters more than anywhere else**. The area's 40 items are ordered approachable → hard there; the modules below pick the load-bearing ones and attach a question and a lab to each. `runtime/scheme.go` (item 35) is **deliberately last** — the generics trap, mastery-necessary and disastrous as early reading.

<a id="m3-0"></a>
### Module 3.0 — Kubernetes the Very Hard Way, and why it sits here (~1 week)

Hand-wire every control-plane component from nothing — the placement is deliberate and the argument is the point, not the verdict.

**The argument** ([#10](https://github.com/k3ii/k8s-academy/issues/10)): the module's difficulty concentrates in exactly two places — PKI/TLS plumbing between components, and etcd configuration and peer setup.
- *Before any Kubernetes:* both hard parts are pure yak-shaving — certs for components you cannot yet name. Rejected.
- *Straight after kubeadm:* better, but you would wire etcd with no idea what a revision or a quorum is. The etcd half stays opaque.
- **Here, after the etcd month — chosen.** The etcd half is now *consolidation*, and the apiserver half is at maximum leverage: you hand-start `kube-apiserver` with its flags **while reading `endpoints/handlers/create.go`** — the binary you are configuring is the source you are reading, the same week.

The iximiuz "Kubernetes the Very Hard Way" module is **browser-hosted, so it costs zero homelab RAM** — which is what makes it affordable in a phase that also needs a running `pair`. Area 0 item 12, `hack/local-up-cluster.sh`, is read alongside it: the most honest inventory of what a control plane is.

> **Question to answer from the source:** for each flag you pass `kube-apiserver`, find where it is consumed in `cmd/kube-apiserver/app/server.go` (item 32) or the config it builds — a flag whose effect you cannot locate in source you do not yet control.

**Labs** — [A control plane with no installer under it](../labs/03/01-hand-wire-the-control-plane.md) · [Every flag you passed, found being read](../labs/03/02-every-flag-located-in-source.md) · [The honest inventory: what a control plane minimally is](../labs/03/03-local-up-cluster-as-inventory.md) · [A wrong client cert fails at a nameable place](../labs/03/04-mis-sign-a-client-cert.md)

Hand-wired PKI is where certs go wrong on purpose later ([module 3.3](#m3-3)). This module is also banked toward **CKA** — control-plane installation is a CKA competency, produced here as a by-product of doing it for real.

<a id="m3-1"></a>
### Module 3.1 — The handler chain and the write path (~1.5 weeks)

The entry point and the spine. This module reads *down onto* [P2](02-etcd.md)'s store.

**Read** — each item with a question to answer:

| Item | Answer from it |
|---|---|
| `endpoints/handlers/create.go` (item 2, ⭐) | In one function: where exactly does mutating admission run relative to `Validate` and `storage.Create`? Name the calls in order. |
| `endpoints/filters/` — `requestinfo.go`, `authentication.go`, `authorization.go` (item 4) | How does a URL become `{verb, group, version, resource, namespace, name}`, and at which filter is a request first rejected for *who* you are versus *what* you may do? |
| `registry/rest/{create,update}.go` + `pkg/registry/core/pod/strategy.go` (items 13–14) | What does a `RESTCreateStrategy` decide that the generic path cannot — defaulting, status-subresource rules? |
| `registry/generic/registry/store.go` (item 15) | Read `Create`/`Update`/`Delete`: where is optimistic concurrency enforced, and how does a `resourceVersion` precondition become an etcd `Txn`? |
| `storage/etcd3/{store.go, watcher.go}` (item 23) | The bottom of the stack — where Kubernetes finally speaks etcd gRPC. How does a Kubernetes key map to an etcd key, and how is a watch translated? This is [P2](02-etcd.md) from above. |
| authn/authz interfaces + `rbac.go` + node `graph.go` (item 36) | Why may a kubelet read only *its own* node's secrets? Trace it through the Node authorizer graph. |

**Labs** — [An apiserver you built, started from flags](../labs/03/05-hand-start-an-apiserver.md) · [Four URLs, predicted before they are parsed](../labs/03/06-a-url-becomes-a-requestinfo.md) · [The same request, refused at two different stages](../labs/03/07-rejected-at-authorization-not-admission.md) · [Where validating admission is actually called from](../labs/03/08-the-order-of-calls-in-create-go.md) · [`resourceVersion` is etcd's `mod_revision`](../labs/03/09-a-precondition-becomes-a-txn.md) · [What is actually stored is not YAML, and not JSON either](../labs/03/10-one-object-read-out-of-etcd.md) · [A kubelet may read exactly the secrets its own pods use](../labs/03/11-the-node-authorizer-graph.md) · [The fields the generic path could not have known to drop](../labs/03/12-what-a-strategy-decides.md)

> **Scope:** [module 3.0](#m3-0)'s hand-wiring is browser-hosted and therefore not instrumentable. The apiserver you attach a debugger to is [one you compile on `forge`](../labs/03/05-hand-start-an-apiserver.md) with a single-member etcd behind it — the same binary, the same flags, and the only copy in the phase whose log lines you control. It is also the phase's one footprint deviation, argued in that file.

<a id="m3-2"></a>
### Module 3.2 — Admission (~1 week)

The extension point the whole platform arc hangs off, learned as source before it is built as webhooks.

**Read**

| Item | Answer from it |
|---|---|
| `admission/interfaces.go` + `chain.go` (item 5) | `chain.go` is 2 KB and states the whole ordering model. Cite the line that guarantees all mutating run before any validating. |
| `plugin/pkg/admission/` — `limitranger/`, `serviceaccount/` (item 7) | Best proof admission is "just a function". What does each do to an incoming Pod, and where would a webhook sit relative to it? |
| KEP-492 (item 6) + `webhook/mutating/reinvocationcontext.go` (item 8) | The normative webhook semantics — `failurePolicy`, `reinvocationPolicy`, timeouts. Why can a mutating webhook be called *more than once*, and what bookkeeping makes that safe? |
| KEP-3716 match conditions + KEP-3488 CEL admission (items 10–11) | The modern way to narrow webhook blast radius, and the in-process, webhook-free alternative (`ValidatingAdmissionPolicy`). When is a webhook now the *wrong* tool? |

**Labs** — [Defaults that appear and vanish with one flag](../labs/03/13-toggle-a-built-in-plugin.md) · [The two-method guarantee, cited and then watched](../labs/03/14-the-line-that-orders-the-chain.md) · [Reinvocation, written as a claim before it is seen](../labs/03/15-why-a-mutating-webhook-reruns.md) · [A rejection with no network hop in it](../labs/03/16-a-policy-with-no-webhook.md)

The webhook-versus-CEL contrast is objective 2's payoff and is deliberately split across two modules: the policy is written here, the webhook enforcing the *identical* rule is built in [3.3](#m3-3), and [the four-way comparison](../labs/03/20-the-same-rejection-twice.md) is only honest because the semantics were held fixed.

<a id="m3-3"></a>
### Module 3.3 — Build: three webhooks and a plugin (~1.5 weeks)

Four artifacts, developed under the [two-stage rule](../strands/build-mechanics.md#two-stages) — stage 1 outside the cluster, stage 2 re-shipped inside. Stage 1 is real, not a simulation: the apiserver cannot tell the difference.

1. **Validating webhook — hand-certed end to end.** Stage 1 runs the process on [`forge`](../strands/build-mechanics.md#forge), which is only possible because forge sits on the lab bridge; every certificate is [`openssl` first](../strands/build-mechanics.md#webhook-tls). Stage 2 pays the cost of the swap, and the cost is the lesson.
2. **Mutating webhook — `cert-manager` second.** The certificate is handled for you, and is now readable as *automation of a shape you already hand-built*, not magic.
3. **CRD conversion webhook** — takes whichever cert path fits; the interesting part is the round-trip ([module 3.4](#m3-4)).
4. **`kubectl` plugin.** **The odd one out, and this file says so** rather than letting you notice: it is a client binary, so it has [**no stage 2**](../strands/build-mechanics.md#artifact-table) — it never practises deployment mechanics, and that is correct, not an omission.

**Gate** — the three webhooks fall to the [tier-2 falsifiable-claim bar](../strands/build-mechanics.md#gates) (a `file:line` claim a hostile reader could check); so does the plugin. There is no objective harness for these — name the claim, do not invent a suite.

**Labs** — [A CA, a serving cert with the right SANs, and a `caBundle`](../labs/03/17-a-ca-and-a-serving-cert-by-hand.md) · [Stage 1: the apiserver calls a process you are still editing](../labs/03/18-the-webhook-the-apiserver-dials.md) · [One SAN wrong, recognised in two minutes](../labs/03/19-change-one-san.md) · [Identical semantics, two failure surfaces](../labs/03/20-the-same-rejection-twice.md) · [Stage 2: what `clientConfig.service` actually costs](../labs/03/21-the-webhook-behind-a-service.md) · [The second webhook, with the certificate handled for you](../labs/03/22-the-mutating-webhook-cert-manager-signs.md) · [The webhook that has to run twice](../labs/03/23-reinvocation-observed.md) · [Narrowing that happens before the network call](../labs/03/24-matchconditions-stop-the-call.md) · [A client binary, and why it never gets a stage 2](../labs/03/25-a-kubectl-plugin.md) · [3.C1 — a flipped byte that blocks the write that would fix it](../labs/03/26-3c1-corrupt-a-cabundle.md)

Drill [3.C1](#chaos) **originates in this module**: it is the one place in the curriculum where wedging a cluster with `failurePolicy: Fail` costs nothing, because the cluster is disposable and the outage is the lesson.

<a id="m3-4"></a>
### Module 3.4 — CRDs and aggregation (~1 week)

How a CRD can behave like a built-in, and how a second apiserver is bolted on.

**Read**

| Item | Answer from it |
|---|---|
| KEP-95 CRD GA + KEP-598 conversion + KEP-2876 CEL validation (items 27–29) | Structural schemas, the storage version, and `x-kubernetes-validations`. What must be true of a conversion for multi-version storage to be safe? |
| `apiextensions-apiserver/.../customresource_handler.go` (item 30) | Read `ServeHTTP` and `getOrCreateServingInfoFor`: how is per-CRD `RESTStorage` built *dynamically* and torn down when the CRD changes? This answers "how can a CRD behave like a built-in?" |
| `kube-aggregator/.../handler_proxy.go` (item 31) | A small, readable reverse proxy. How does an `APIService` route to an external apiserver — and why is this the exact surface of CVE-2018-1002105 (talk below)? |
| `cmd/kube-apiserver/app/{server.go, aggregator.go}` (item 32) | The payoff: how `kube-apiserver` → `apiextensions-apiserver` → `kube-aggregator` are chained with delegation. `sample-apiserver` is **read, not built** — read it here as the minimal aggregated server. |

**Labs** — [Two served versions, one stored, no webhook yet](../labs/03/27-a-two-version-crd.md) · [The third webhook: a different request shape entirely](../labs/03/28-the-conversion-webhook.md) · [Prove the round trip, then break it on purpose](../labs/03/29-a-round-trip-that-loses-nothing.md) · [Where a CRD's REST storage comes from at runtime](../labs/03/30-how-a-crd-gets-its-storage.md) · [A URL path served by a process that is not the apiserver](../labs/03/31-an-apiservice-routes-out-of-process.md) · [3.C2 — every read of one resource type fails](../labs/03/32-3c2-garbage-from-the-conversion-webhook.md)

> **Scope:** the aggregation half is met as *routing*, not as a second apiserver you write. Building a real extension apiserver means wiring `k8s.io/apiserver`'s delegated authn/authz, which is a phase of its own and is [not affordable here](../labs/03/31-an-apiservice-routes-out-of-process.md); the proxy seam and its blast radius are what this module is for. The CVE returns in [P10](10-security.md) as security.

<a id="m3-5"></a>
### Module 3.5 — Watch cache, consistency, and APF (~1 week)

The read-scaling machinery, and the apiserver end of [P2](02-etcd.md)'s watch.

**Read**

| Item | Answer from it |
|---|---|
| `storage/cacher/watch_cache.go` (item 21) | The ring buffer behind every watch — `startIndex`/`endIndex`, capacity. **This is the exact origin of `"too old resource version"`**: what makes an event fall off the ring? (Note the [cacher split](../strands/source-archaeology.md#stale-paths) — it is a *package* now, not one file; older walkthroughs cite dead line numbers.) |
| KEP-2340 consistent reads + `cacher/delegator.go` (items 20, 22) | The best KEP for the apiserver/etcd consistency contract: how can a *quorum-consistent* read be served from cache using etcd progress notifications? |
| KEP-1040 APF + `util/flowcontrol/apf_filter.go` (items 25–26) | FlowSchemas, PriorityLevelConfigurations, shuffle sharding — the correct mental model for apiserver overload. What does APF protect, and what does it *not*? |
| KEP-555 server-side apply (item 34) | `managedFields` and apply-vs-update conflict detection — the model that replaced strategic-merge-patch. |

**Labs** — [`too old resource version`, produced on demand](../labs/03/33-overflow-the-ring.md) · [Two `too old` errors, one wording, different causes](../labs/03/34-the-same-failure-two-layers.md) · [A watch event that carries no object change](../labs/03/35-a-bookmark-advances-nothing-else.md) · [Which of your reads reached etcd](../labs/03/36-cache-or-etcd.md) · [Two owners, one field, one conflict](../labs/03/37-managedfields-and-a-conflict.md) · [Naming the FlowSchema for a request you sent](../labs/03/38-which-flowschema-caught-the-request.md) · [3.C3 — one client, one priority level, everyone in it queued](../labs/03/39-3c3-starve-an-apf-priority-level.md) · [3.C4 — the apiserver stops; the controllers do not](../labs/03/40-3c4-apiserver-down-controllers-up.md) · [3.C5 — x509 from the inside](../labs/03/41-3c5-an-expired-component-certificate.md)

This is the module that closes the phase's longest thread: `ErrCompacted` in [P2](02-etcd.md), the ring buffer here, and the relist [P4](04-controllers.md)'s informer performs in response — one failure named at three layers, and the last of the three is the reason the first two mattered.

<a id="m3-6"></a>
### Module 3.6 — The single-binary contrast: k0s (~2–3 days)

The last of three progressively-automated answers to one question.

**Labs** — [One binary, four components, no manifests you wrote](../labs/03/42-k0s-in-one-binary.md) · [Kill one process, lose four components](../labs/03/43-kill-the-one-process.md) · [Three control planes, compared from your own notes](../labs/03/44-three-control-planes.md)

k0s is deliberately separated from kubeadm so the contrast lands against experience, giving the phase three control planes *in sequence*: **hand-wire every component** (Very Hard Way) → **read what kubeadm generated for you** ([P1](01-operate-shallow.md)'s cluster, revisited) → **watch a single binary collapse the whole control plane into one process** (k0s). The full-vs-lightweight trade-off is felt hardest here, because only now can you name precisely what k0s is hiding.

---

<a id="chaos"></a>
## 3. Chaos drills

The **self-inflicted-outage** phase — every fault here is something the operator does to themselves, still **hand-driven** (no chaos tool until [P6](06-kubelet-node.md)). Drill 3.C1 **originates in this phase** and is borrowed by [`chaos.md#borrowed-drills`](../strands/chaos.md#borrowed-drills) — the mechanism lives here, the chaos strand links in.

| # | Drill | What you must produce afterwards |
|---|---|---|
| [3.C1](../labs/03/26-3c1-corrupt-a-cabundle.md) | **Corrupt a webhook `caBundle`** | The apiserver log line that names it, and the reason a broken admission webhook can wedge *every* write — including the one that fixes it |
| [3.C2](../labs/03/32-3c2-garbage-from-the-conversion-webhook.md) | **Garbage-returning conversion webhook** | Why every read of that CRD's objects now fails, and how the blast radius is scoped to one resource type |
| [3.C3](../labs/03/39-3c3-starve-an-apf-priority-level.md) | **Starve an APF priority level** | Which requests get queued/rejected and which sail through — APF's protection boundary, made visible |
| [3.C4](../labs/03/40-3c4-apiserver-down-controllers-up.md) | **Apiserver down, controllers up** | What a controller does when its watch drops and its writes fail — the level-triggered payoff, previewing [P4](04-controllers.md) |
| [3.C5](../labs/03/41-3c5-an-expired-component-certificate.md) | **Expired component certificate** | `x509` from the *inside*, and the recovery order — banked toward CKA cert-rotation |

**The escape hatch is part of the drill, not a footnote:** for 3.C1, establish before you start that `failurePolicy: Fail` on a webhook selecting its own namespace is how clusters actually die — and that the fix is namespace/label exclusion or deleting the webhook config out-of-band.

---

<a id="talks"></a>
## 4. Talks

Full entries with runtimes under [API server](../strands/talks.md#apiserver) and [Security](../strands/talks.md#security).

- **The Life (or Death) of a Kubernetes API Request, 2025 Edition** (Kashem & Schimanski) — **watch first.** The single best entry to the whole control plane: one request end to end, authn → authz → APF → admission → storage → etcd → watch fan-out, with the modern APF/CEL stages in place. This is the spine every module above hangs off.
- **The Cluster Killer Bug: Learning API Priority and Fairness the Hard Way** (Zaneski) — APF through a real outage, the mechanism behind drill 3.C3.
- **Webhook Fatigue? …Introducing the CEL Expression Language** (Betz) — why webhook admission costs you (latency in the request path, availability coupling) and why CEL-in-apiserver was the answer — the argument behind module 3.2's webhook-vs-VAP contrast.
- **Crafty Requests: Deep Dive Into Kubernetes CVE-2018-1002105** (Coldwater) — the model CVE walkthrough: the aggregation-layer proxy upgrade bug that skipped authorization. Watched here as **mechanism** (it is the `handler_proxy.go` seam from module 3.4); it **returns in [P10](10-security.md) as security**.

---

<a id="ecosystem"></a>
## 5. Ecosystem

**k0s** — the single-binary distribution, treated for its internals rather than just installed (module 3.6 is the hands-on contrast).

- **Hands-on:** [module 3.6](#m3-6), on `k0s-light`.
- **Internals note:** k0s ships the entire control plane as **one supervised Go binary** — apiserver, controller-manager, scheduler and an **embedded etcd** (or a `kine`-backed SQL store) started and health-managed as child processes by a single supervisor. The component boundaries you hand-wired in [3.0](#m3-0) still exist inside that binary — the seams are hidden, not gone, which is what makes it worth reading how it supervises.
- **Maturity:** a CNCF-landscape distribution (Mirantis), CNCF-conformant. Contrast with kubeadm (an upstream SIG-Cluster-Lifecycle tool, not a distro) — the two answer *different* questions, which is why this phase runs both.

---

<a id="capstone"></a>
## 6. Capstone

**The Very Hard Way completed, three webhooks running, and a written trace of one `kubectl apply` through the entire handler chain — citing file and line numbers a hostile reader could check.**

Three artifacts, one trace:

1. **A hand-wired cluster** (module 3.0) that comes up and serves — every component started by you, every cert signed by you.
2. **Three webhooks running** on it: the hand-certed validating webhook, the `cert-manager` mutating webhook, and the CRD conversion webhook serving a two-version resource. (The `kubectl` plugin is the fourth build artifact but not a webhook — it stands alone.)
3. **The trace** — one `kubectl apply`, followed from the client through the full chain, each stage cited to `file:line` in the live tree. The nine stages it must cover, and the two the phase's spine talk adds that the list omits, are [in the lab](../labs/03/45-the-capstone-trace.md).

Every path must first have been verified live per [P2's archaeology standard](../strands/source-archaeology.md#drills) — a citation you have not confirmed against the tree does not count, and the `cacher` split is the trap waiting for a copied line number. **The trace is graded as much on whether its `file:line` references survive checking as on whether the cluster serves.**

**Lab** — [the capstone, in one sitting](../labs/03/45-the-capstone-trace.md). It re-provisions its own cluster, and its footprint note argues why that repeat is cheaper than the alternative.

---

<a id="checklist"></a>
## 7. Checklist

Concrete, demonstrable, grouped by evidence type. No item says *understand* or *know*.

**Timed / live against a running apiserver:**
- [ ] Reject one `kubectl create` at `authorization.go` (no binding), then admit it (bound) — naming the rejection point each time.
- [ ] Reproduce `"too old resource version"` on a watch by overflowing the cache window.
- [ ] Break a webhook SAN and recognise the `x509` apiserver log line within 2 minutes.

**Build artifacts (tier-2 `file:line` gate):**
- [ ] Validating webhook, hand-certed, stage 1 (`url`) then stage 2 (`service`).
- [ ] Mutating webhook via `cert-manager`.
- [ ] CRD conversion webhook serving a two-version resource with a proven round-trip.
- [ ] `kubectl` plugin (client binary, no stage 2 — say why).

**Written artifacts (each is a module's Write-down):**
- [ ] The component-and-flag map from the Very Hard Way (3.0).
- [ ] The ordered handler chain with the file per stage (3.1).
- [ ] The admission ordering rule with its `chain.go` citation (3.2).
- [ ] The `caBundle`-corruption symptom and log line (3.3).
- [ ] The storage-version round-trip note (3.4).
- [ ] The ring-buffer origin of `"too old resource version"`, tied to P2's `ErrCompacted` (3.5).
- [ ] The three-control-planes comparison (3.6).
- [ ] The capstone trace with surviving `file:line` citations.

**Falsifiable claims — write, then verify against source:**
- [ ] Why a mutating webhook may be invoked more than once (cite `reinvocationcontext.go`).
- [ ] Why a kubelet may read only its own node's secrets (Node authorizer graph).
- [ ] What APF protects and what it does not.

---

<a id="gate"></a>
## 8. Gate

You may advance to [P4](04-controllers.md) when:

1. **The handler-chain trace is complete and its `file:line` citations survive checking.** A cluster that serves but a trace whose paths do not resolve in the live tree is a *fail* — this is the phase where the citation standard is the deliverable, not a garnish.
2. **You can name the admission ordering rule and the reinvocation reason without notes** — mutating-then-validating, and why a mutating webhook re-runs. [P4](04-controllers.md)'s reconcilers and every later admission policy assume this cold.
3. **The `"too old resource version"` chain is reflexive across both layers:** etcd `ErrCompacted` ([P2](02-etcd.md)) *and* the apiserver watch-cache ring buffer, and why a client's answer to either is a relist. If you cannot draw it end to end, **stay here** — [P4](04-controllers.md)'s informer is the client that has to survive it.

This is the heaviest phase because everything below is a client of what it serves. When [P4](04-controllers.md) wires an informer, the watch it consumes, the cache it reads, and the admission it passes through are all machinery you have now started by hand, read in source, and broken on purpose.
