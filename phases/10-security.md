# Phase 10 — Security & supply chain + CKS

> **4–5 weeks**, plus a **1–2 week CKS drill block** at the end.
> The range is planning information. **The gate at the bottom decides when the phase is finished** — not the calendar. This is the phase where eight phases of *how it works* become *how it breaks and how you stop it*: nearly nothing here is new machinery, it is the machinery you already read, now viewed as attack surface and hardened.

| | |
|---|---|
| **Prerequisites** | [P3 API machinery](03-api-machinery.md) — the admission **chain** was taught there with *no policy engine at all*, so Kyverno arrives as a policy layer on machinery you already read, not a black box. [P7 Networking](07-networking.md) — NetworkPolicy is CKS *Cluster Setup*, and Cilium's pod-to-pod encryption is CKS *Minimize Microservice Vulnerabilities*. [P9 mesh](09-service-mesh.md) — the SPIFFE workload identity is the other half of that CKS line (Cilium **and** Istio), and mTLS from P9 is now a hardening control. [P2 etcd](02-etcd.md) — secrets-encryption-at-rest is checked by reading the on-disk bytes. |
| **Unlocks** | [P11 Synthesis](11-synthesis.md) and [P12](12-gitops-platform.md). This is the last cert, and the last descent into a Kubernetes subsystem — everything after climbs back up. |
| **Source** | RBAC / authn / authz — [Area 2 items 36–38](../strands/source-reading.md#area-2-api-machinery), **re-read as CKS material**. The admission-chain items (4–12) return from P3 as the substrate Kyverno sits on. |
| **Language** | Go for reading ([#9](https://github.com/k3ii/k8s-academy/issues/9)); the artifacts here are **policies, rules and signatures**, not a build-track binary — [build mechanics](../strands/build-mechanics.md#artifact-table) lists no P10 Go artifact. |
| **Lab** | [`pair`](https://github.com/k3ii/k8s-academy/issues/8), on the **isolated `10.10.10.0/24` bridge** — which is not a convenience here but the *containment boundary* for the capstone (see [§7](#capstone)). |
| **Cert** | [**CKS**](../strands/certs.md#cks), sat at the end of the [drill block](#cks-block). CKS-last is optimal — the CARE programme reinstates an expired CKA. |
| **Strands** | [certs (CKS)](../strands/certs.md#cks) · [chaos (CVE loop)](../strands/chaos.md#install) · [talks](../strands/talks.md#security) · [source archaeology](../strands/source-archaeology.md#drills) |

---

<a id="objectives"></a>
## 1. Objectives

Every one is falsifiable — an artifact, a timed production, or a claim a hostile reader could check against source or a running cluster. *understand* and *know* appear nowhere.

By the end you can:

1. **Trace in `node_authorizer`'s `graph.go`** why one node's kubelet cannot read another node's Secret, citing the graph edge — the lateral-movement boundary that decides how far a compromised node reaches.
2. **Read `rbac.go`'s rule-matcher** and write a Role granting exactly one verb on one resource — proving a wildcard is a *choice*, not a default.
3. **Enforce a Pod Security Standard baseline** with Pod Security Admission *and* a Kyverno policy, showing the P3 admission chain reject a violating pod — the mutating-then-validating split named, not hand-waved.
4. **Harden the cluster against the CIS benchmark** (kube-bench): encrypt Secrets at rest and prove the etcd on-disk bytes changed, and enable an audit policy that logs the exec you will later detect.
5. **Generate an SBOM, scan an image, and sign it keyless with `cosign`**, then reject an unsigned image at admission — the whole supply chain CLI-side on `hopper`, **no private key persisted**.
6. **Write a behavioral Falco rule** that fires on exec in the `chaos-daemon` context, and prove it survives an **unseen variant** (technique, not string).
7. **Run the full CVE incident** — exploit `CVE-2025-59359` on the isolated bridge, detect, remediate to the standing config, postmortem — defanged, working payload destroyed with the cluster.
8. **Sit CKS** and pass.

---

<a id="modules"></a>
## 2. Modules

Reading is [Area 2 items 36–38](../strands/source-reading.md#area-2-api-machinery) plus the P3 admission items returning as attack surface. Every cited item carries a question to answer — no bare links.

<a id="m10-1"></a>
### Module 10.1 — Identity and authorization, as attack surface (~1 week)

The two smallest interfaces in the apiserver decide who you are and what you may touch. Re-read them asking *how does an attacker escalate*, not *how does a request flow*.

**Read**

| Item | Answer from it |
|---|---|
| Item 36 — `authentication/authenticator/interfaces.go` + `authorization/authorizer/interfaces.go`, then `plugin/pkg/auth/authorizer/rbac/rbac.go` | The two interfaces are tiny. `rbac.go` is a readable rule-matcher: **how is a request matched against a rule, and what does a `*` verb or resource actually widen?** Cite the match function. |
| Item 36 (cont.) — `plugin/pkg/auth/authorizer/node/{node_authorizer.go, graph.go}` | The Node authorizer's graph. **Trace why a kubelet may read only *its own* node's Secrets** — which graph edge encodes that, and what a node compromise therefore does *not* automatically grant. This is the lateral-movement boundary. |
| Item 38 — KEP-1205 Bound Service Account Tokens | Audience-and-time-bound projected tokens vs the old forever-Secret. **Why is a bound token a smaller blast radius when a pod is compromised?** |
| Item 37 — KEP-3331 / KEP-3221 (structured authn/authz config) | The current file-based config (multiple JWT issuers; ordered authorizer chains with CEL) that supersedes the flag-soup most material still teaches. What can an ordered authorizer chain express that a flag list cannot? |

**Do** — write a least-privilege Role + RoleBinding for a real ServiceAccount, then attempt an action just outside it and read the authz denial. Disable the `default` SA's automount on a namespace (CKS *Cluster Hardening*).

**Break it** — chaos drill [10.C1](#chaos): grant a wildcard `*` in one Role and find the escalation path it opened; then close it and prove the path is gone.

**Write down** — the `graph.go` edge that confines a kubelet to its own node's Secrets, cited `file:line` — the fact the capstone's blast-radius reasoning rests on.

<a id="m10-2"></a>
### Module 10.2 — Pod hardening and policy admission (~1 week)

The P0 capabilities/seccomp module, now enforced cluster-wide by a policy engine sitting on the P3 admission chain.

**Read** — Pod Security Admission (the three standards: privileged/baseline/restricted) as the examinable PSP-successor ([CKS v1.31 change](../strands/certs.md#cks-changes) made this *the* mechanism). Then re-read admission items 4–8 from P3 — **`chain.go`'s all-mutating-then-all-validating ordering** is what a Kyverno policy plugs into.

> **Question to answer from the source:** in `admission/chain.go`, at what point does a Kyverno validating webhook run relative to a mutating one that adds a `securityContext` default? Cite the ordering guarantee.

**Do** — apply `restricted` Pod Security Admission to a namespace; write a Kyverno policy that requires `runAsNonRoot` and drops all capabilities; apply a seccomp `RuntimeDefault` profile and an AppArmor profile to a pod (CKS *System Hardening*). Learn Rego off-cluster with `opa eval` — no Gatekeeper needed (it won't fit; [#6](https://github.com/k3ii/k8s-academy/issues/6)).

**Break it** — chaos drill [10.C2](#chaos): write a Kyverno policy with a gap (matches `Pod` but not the `Deployment` template that creates it) and watch a violating pod slip through the controller that made it — the classic policy-scope mistake.

**Write down** — the Kyverno policy and the admission-ordering point at which it fires, and the seccomp/AppArmor profiles applied.

<a id="m10-3"></a>
### Module 10.3 — Cluster and node hardening (~1 week)

Turn the cluster you built in P1–P3 into one that passes an auditor.

**Do**
- Run **kube-bench** (CIS benchmark) against etcd, kubelet and the apiserver; fix the top findings and re-run (CKS *Cluster Setup*).
- Write an `EncryptionConfiguration` so Secrets are encrypted at rest, restart the apiserver, create a Secret, and **read the raw etcd bytes** (the [P2](02-etcd.md) `etcdctl get` skill) to prove they are no longer plaintext.
- Enable an **audit policy** at `Metadata`+ level for exec/attach, and confirm a `kubectl exec` appears in the audit log — the same event the Falco rule will catch at runtime.
- Protect node metadata: block pod access to the cloud/link-local metadata endpoint with a NetworkPolicy ([P7](07-networking.md)).

**Break it** — chaos drill [10.C3](#chaos): mis-order the `EncryptionConfiguration` providers (`identity` first) and prove new Secrets are written in plaintext despite encryption being "on" — the config that lies.

**Write down** — the before/after etcd on-disk bytes for one Secret, and the audit-log line for one exec.

<a id="m10-4"></a>
### Module 10.4 — Supply chain, zero-cluster-cost (~1 week)

The whole module runs **CLI-side on `hopper`** — it costs the cluster nothing, which is what makes this phase affordable next to Falco ([#8](https://github.com/k3ii/k8s-academy/issues/8)). CKS *Supply Chain Security*, 20% of the exam.

**Do**
- Generate an **SBOM** for an image (`syft`) and diff it against the image's actual layers — minimize the base image and watch the SBOM shrink.
- **Scan** with `trivy`/`grype`; run static analysis with `kubesec`/`kube-linter` on your own manifests.
- **Sign keyless with `cosign`** (Sigstore/Fulcio OIDC) and verify — **`hopper` holds no long-lived private key**; identity comes from the OIDC token, so there is no key to leak. Record the transparency-log (Rekor) entry.
- Enforce it at admission: a Kyverno `verifyImages` rule that **rejects an unsigned or unverifiable image** and permits only your signed one from a permitted registry.

**Break it** — chaos drill [10.C4](#chaos): push an unsigned image and confirm admission rejects it; then tamper with a signed image's digest and confirm verification fails — signature bound to content, not to a name.

**Write down** — the `cosign verify` output with the Rekor entry, and the admission rejection of the unsigned image.

<a id="m10-5"></a>
### Module 10.5 — Runtime detection with Falco (~4 days)

The behavioral half — the detection the capstone's gate demands. Falco reads syscalls (its eBPF driver is [P7](07-networking.md)'s eBPF, now in a security tool) and matches them against rules.

**Read** — Falco's rule model: `condition`, the syscall fields, and why a **behavioral** rule (exec *in this context*) beats a **string** rule (this exact command). The *Container Forensics* talk frames what you are collecting and why ephemeral workloads make it hard.

> **Question to answer from the source (a rule):** in a Falco rule, which field identifies *the process's container/context* rather than its argv? That field is the difference between a rule a variant evades and one it does not.

**Do** — write a Falco rule that fires on an unexpected `exec` inside the `chaos-daemon` context (the capstone's detector). Test it against a benign exec you expect *not* to fire.

**Break it** — chaos drill [10.C5](#chaos): write the rule as a string match on one command, then run the same technique with a different command and watch it miss — the exact failure the capstone's unseen-variant gate exists to prevent.

**Write down** — the behavioral Falco rule with the context field it keys on, and the missed-detection from the string-match version.

---

<a id="chaos"></a>
## 3. Chaos drills

The phase's chaos **is** its capstone — the CVE incident ([§7](#capstone)). The drills below are its rehearsals: each builds one skill the live incident needs, so that when the incident runs, no single mechanism is new. Anchored in the [CVE loop](../strands/chaos.md#install).

| # | Drill | Mechanism | What you must produce afterwards |
|---|---|---|---|
| 10.C1 | **RBAC escalation** | by hand (a `*` verb) | The escalation path a wildcard opened, and proof it's closed after |
| 10.C2 | **Policy scope gap** | by hand (Kyverno matches Pod not Deployment) | The violating pod that slipped through, mapped to the missing match |
| 10.C3 | **Encryption that lies** | by hand (`identity` provider first) | Plaintext Secret bytes in etcd despite "encryption on" |
| 10.C4 | **Unsigned image admitted** | by hand (push unsigned / tamper digest) | The admission rejection, and the digest-tamper verify failure |
| 10.C5 | **Detection a variant evades** | by hand (string rule vs new command) | The missed detection that forces a behavioral rule |

Every drill is by-hand: reading the exact rule, edge, or byte that failed is the lesson, and each one is a component of the incident in [§7](#capstone).

---

<a id="talks"></a>
## 4. Talks

Full entries under [Security](../strands/talks.md#security).

- **★ Crafty Requests: Deep Dive into CVE-2018-1002105** (Coldwater, EU 2019) — **returns from [P3](03-api-machinery.md), now read as an attack.** The aggregation-layer proxy-upgrade bug that skipped authorization, explained protocol-up. In P3 it was apiserver mechanism; here it is the model CVE walkthrough — *a proxy path that bypasses authz* is the evergreen class, and reading it primes the capstone's own "unauthenticated request → privileged execution" shape.
- **Container Forensics: What to Do When Your Cluster is a Cluster** (Kaczorowski & Wallace, EU 2019) — incident response on ephemeral workloads: what evidence to collect before a pod vanishes, which is exactly the problem the capstone's audit log + Falco rule solve. Watch before [module 10.5](#m10-5).
- **The Path Less Traveled: Abusing Kubernetes Defaults** (Cooley & Coldwater) and **Attack and Defense: Inception-Style** (Beale) — paired attack/defence demos; use them to pressure-test your hardening, not just to admire the escapes.

---

<a id="ecosystem"></a>
## 5. Ecosystem

Multiple tools this phase, because security *is* the integration of them — but each earns its footprint.

- **Kyverno** (~320Mi) — the policy engine, chosen because **Gatekeeper's ~2Gi is un-runnable here** ([#6](https://github.com/k3ii/k8s-academy/issues/6)). **Internals note (required):** Kyverno is a pair of admission webhooks on the P3 chain — it adds *no* new apiserver machinery; every policy is a `ValidatingWebhookConfiguration` or `MutatingWebhookConfiguration` you already read the dispatch code for. That is why it slots in without new theory.
- **Falco** — runtime detection, syscall-level, its driver the same eBPF you loaded in [P7](07-networking.md). Maturity: CNCF **graduated**.
- **cert-manager** — issues and rotates the TLS the CIS benchmark and Ingress-with-TLS demand; the P4 webhook-cert work, now automated.
- **Sigstore / `cosign` + `syft`** — supply chain, **zero cluster cost** ([module 10.4](#m10-4)): CLI on `hopper`, keyless signing so nothing secret is stored. Sigstore is CNCF **graduated**; Kyverno graduated 2025.
- One thing this phase does **not** install: **Gatekeeper** (won't fit) — Rego is learned off-cluster with `opa eval` instead, so the concept survives without the 2Gi.

---

<a id="cks-block"></a>
## 6. ⏱ CKS drill block — 1–2 weeks

> **This section is a different activity from everything above.** Everything above optimises for depth — reading the rule, citing the byte. This optimises for **speed and correctness under a clock**. Do not blend them. Do not read source during this block. It runs **last** — after the capstone incident in [§7](#capstone) — and when it ends, it ends.

Domains, weights and the recent-changes list live in [`certs.md#cks`](../strands/certs.md#cks) — not restated here. Three drill-block rules specific to CKS:

1. **CKS is `kubectl`-plus-the-node.** Half the tasks are edits to files on the control-plane node (apiserver flags, audit policy, `EncryptionConfiguration`, kubelet config) — `ssh` + `vim` speed matters as much as `kubectl`. Drill the node edits, not just the API objects.
2. **The allowed docs are the map.** Falco, Cilium, Istio, Kyverno/OPA and the Trivy docs are on the allowed list ([`certs.md#cks-changes`](../strands/certs.md#cks-changes)) — practice navigating *those specific pages* fast, because they are what you get in the exam.
3. **Pod-to-Pod encryption is Cilium *and* Istio** (v1.33 change) — both already installed in [P7](07-networking.md)/[P9](09-service-mesh.md); the drill is doing it under time, not learning it.

Drill on killer.sh (two included sessions) and Killercoda. Sit the exam at the end of this block, not before.

---

<a id="capstone"></a>
## 7. Capstone — the CVE incident

**Enable the pinned-vulnerable `chaos-dashboard` on the isolated cluster → exploit `CVE-2025-59359` with a self-contained PoC, egress dropped → detect with a Falco rule you wrote that must survive an unseen variant → remediate to v2.7.3 / dashboard-off (the standing [`chaos.md#install`](../strands/chaos.md#install) config) → postmortem, defanged, committed alongside the rule; working payload destroyed with the cluster.**

This is the loop [`chaos.md#install`](../strands/chaos.md#install) named four phases ago: the dashboard the [P6](06-kubelet-node.md) reader turned off is the surface you now exploit, and remediation *returns to that same config*. Incident response arrives at the hardening the curriculum prescribed in P6.

### Containment — read before you enable anything

The CVE numbers, the standing config, and the `chaos-daemon`'s `privileged`/`hostPID`/host-mount facts are in [`chaos.md#install`](../strands/chaos.md#install). What follows is the containment story that the strand does not carry — and it is mandatory:

- **Substrate.** The isolated NAT'd `10.10.10.0/24` bridge — no physical port, reachable only through the `factory` bastion, masqueraded egress. **This is the containment boundary**, and it has to be, because of the next point.
- **Blast radius is the whole lab cluster, by design.** The injection runs in the `chaos-daemon`'s context — `privileged: true`, `hostPID: true`, host mounts. There is **no in-cluster boundary** to contain it: not a namespace, not RBAC, not a NetworkPolicy. A 9.8 in a privileged DaemonSet is a full-cluster compromise, and the lab teaches this directly — *once the daemon is the executor, no in-cluster policy narrows it.* Containment is the bridge, full stop.
- **Egress discipline.** Because the bridge masquerades egress, the PoC **must be self-contained — no second-stage fetch from the internet — and egress from the cluster is dropped for the exploit window.** The postmortem records which mechanism enforced it. This is the one containment rule isolation does not give you for free.
- **Teardown is mandatory and immediate** after the postmortem. Restoring the standing config *is* the remediation, so containment and pedagogy coincide.

### What is committed — and what is never committed

- **Committed:** the learner-authored Falco rule, and a postmortem whose exploit description is **defanged** — the technique (unauthenticated request → command injection → privileged daemon context), never a runnable payload.
- **Never committed:** the working exploit payload. It exists only on the isolated cluster and **dies with teardown.** The repo is a curriculum, not an exploit kit — and its privacy is explicitly **not** load-bearing: nothing runnable is committed regardless of whether the repo is private.

### The detection gate — and the sealed variant

The rule must fire not only on the payload you exploited with but on an **unseen variant — same technique, different payload** — which forces a *behavioral* rule (exec in the `chaos-daemon` context, module 10.5's context field) over a string match. **Stock Falco rules are not sufficient on their own.**

> **SEALED — do not read until your Falco rule is written and passing on your own exploit.**
> The variant is specified below at the **technique level only** — a behavioral difference, not a runnable payload (the never-commit rule binds the variant exactly as it binds the primary exploit). When your rule passes on your own attempt, construct the variant from this description at gate time, run it on the isolated cluster, and confirm your rule still fires; the runnable form is destroyed with teardown like everything else.
> **Variant spec:** *the same unauthenticated-injection entry point, but the injected action changes shape — a different child process name, invoked via an indirection (a shell built-in or an interpreter) rather than the original binary directly, writing to a different host path. A rule keyed on the original command string, argv, or process name will miss it; a rule keyed on "an unexpected exec within the `chaos-daemon` container context" will not.*

### `file:line` a hostile reader could check

The incident's claims must cite checkable evidence, per the [P2 archaeology standard](../strands/source-archaeology.md#drills):
1. **Why it is a full-cluster compromise:** the `chaos-daemon` DaemonSet manifest fields (`securityContext.privileged`, `hostPID`, the host mounts) — cite the manifest line.
2. **Why a compromised node does not automatically own its neighbours:** the `graph.go` edge from [module 10.1](#m10-1) — the boundary that *did* hold, cited `file:line`.
3. **The detection:** the line of your Falco rule that keys on context, and the audit-log entry for the exec.

A reader checks the manifest field, the source edge, and the rule line — all re-derivable.

---

<a id="checklist"></a>
## 8. Checklist

Concrete, demonstrable, grouped by evidence type. No item says *understand* or *know*.

**Live against a running cluster:**
- [ ] A least-privilege Role that denies the action just outside it; `default` SA automount disabled (10.1).
- [ ] `restricted` Pod Security Admission + a Kyverno policy rejecting a violating pod (10.2).
- [ ] kube-bench findings fixed and re-run; Secret bytes encrypted at rest in etcd; an exec in the audit log (10.3).
- [ ] An unsigned image rejected at admission; a signed one from a permitted registry admitted (10.4).
- [ ] A behavioral Falco rule firing on `chaos-daemon` exec and not on a benign one (10.5).

**Written / produced artifacts (each is a module's Write-down):**
- [ ] The `graph.go` edge confining a kubelet to its own node's Secrets, cited `file:line` (10.1).
- [ ] The Kyverno policy + the admission-ordering point it fires at; the seccomp/AppArmor profiles (10.2).
- [ ] Before/after etcd bytes for one Secret; the audit line for one exec (10.3).
- [ ] `cosign verify` output with the Rekor entry; the unsigned-image rejection (10.4).
- [ ] The behavioral Falco rule with its context field; the string-rule miss (10.5).
- [ ] The **defanged postmortem** with a timeline, committed alongside the Falco rule (10.C / §7).

**Falsifiable claims — write, then verify:**
- [ ] Why a bound SA token is a smaller blast radius than a forever-Secret (KEP-1205).
- [ ] Why containment for the capstone is the bridge, not any in-cluster policy.
- [ ] Why a behavioral Falco rule survives the variant and a string rule doesn't.

**Certification:**
- [ ] **CKS passed** (after the [drill block](#cks-block), not before).

---

<a id="gate"></a>
## 9. Gate

You may advance to [P11](11-synthesis.md) when:

1. **The CVE incident ran end to end** — exploited on the isolated bridge with egress dropped, detected by *your* rule which **also fired on the unseen variant**, remediated back to the standing config, and postmortemed (defanged, committed; payload destroyed). If your rule caught your own payload but missed the variant, the detection is a string match — **stay here and make it behavioral.**
2. **The blast-radius reasoning is cited, not asserted** — you point at the `chaos-daemon` manifest fields that make it a full-cluster compromise *and* the `graph.go` edge that kept a node from owning its neighbours. "It was contained" without the boundary named does not pass.
3. **The cluster is hardened and the hardening is demonstrated** — Secrets encrypted at rest proven in etcd bytes, an unsigned image rejected at admission, a least-privilege Role that denies. Claims, each checkable.
4. **CKS is passed.**

This is the last descent. [P11](11-synthesis.md) climbs back up: **corpus trace #1** — `kubectl run nginx` all the way to a running container, through every area you have now entered — attempted only now that all of them are behind you, and named in [P0](00-linux-primitives.md) as the target from week one.
