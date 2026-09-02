# Certification

This document covers CKAD, CKA and CKS. It gives you five things: the verified domain
weights, the exam mechanics, what changed recently, which practice resources are current,
and which speed tactics are worth drilling.

It derives from [`../research/cert-exams.md`](../research/cert-exams.md), research date
2026-08-17. Every domain weight here was read out of the current curriculum PDF in
[`cncf/curriculum`](https://github.com/cncf/curriculum). No weight came from memory, and no
weight came from a blog post. Facts that could not be confirmed from a primary source are
marked **[UNVERIFIED]** inline. The unresolved ones are collected under
[Open items](#open-items).

## Which phase sits which exam

| Phase | Exam | Anchor |
|---|---|---|
| P1 — operate shallow + Helm | **CKAD** | [CKAD](#ckad) |
| P8 — storage | **CKA** | [CKA](#cka) |
| P10 — security | **CKS** | [CKS](#cks) |

**CKS last is optimal, and not merely convenient.** CKA is a hard prerequisite for CKS,
but the CKA need not be *active*. And under the CARE programme, passing CKS reinstates an
expired CKA. So the ordering that falls out of the spine is also the ordering that buys the
most validity. See [Cert ordering](#ordering).

<a id="rules"></a>
## Three standing rules for this strand

1. **Cert results are never a gate.** A phase does not wait on an exam booking. The exam
   is external validation of work that is already done, and a failed sitting extends
   nothing.
2. **Exam drilling and internals depth are different activities.** Drilling optimises speed
   and correctness under time pressure. Everything else optimises for understanding. So a
   cert block in a phase file carries no source reading. It also says what *not* to drill,
   as well as what to drill.
3. **Do not bill etcd depth as CKA prep.** CKA v1.32 **removed `etcd backup and restore`
   from the curriculum**. See [Recent changes (CKA)](#cka-changes). P2 spends a month on
   etcd because that is where control-plane mastery lives. It does not spend a month on etcd
   because the exam asks. Saying otherwise would be a lie, and the learner discovers that
   lie at the worst moment.

---

<a id="versions"></a>
## 0. Version state at a glance

| Cert | Current curriculum version | Published | Exam environment k8s version | Duration | Pass mark | Validity |
|---|---|---|---|---|---|---|
| CKAD | **v1.35** | 2026-02-25 | v1.35 | 2 h | **66%** | 2 years |
| CKA | **v1.35** | 2026-03-03 | v1.35 | 2 h | **66%** | 2 years |
| CKS | **v1.34** | 2025-10-30 | v1.35 | 2 h | **67%** | 2 years |

Sources: [`cncf/curriculum`](https://github.com/cncf/curriculum) (file listing + git log),
[FAQ: CKA, CKAD & CKS](https://docs.linuxfoundation.org/tc-docs/certification/faq-cka-ckad-cks),
[Important Instructions: CKA and CKAD](https://docs.linuxfoundation.org/tc-docs/certification/tips-cka-and-ckad),
[Important Instructions: CKS](https://docs.linuxfoundation.org/tc-docs/certification/important-instructions-cks).

**Note the CKS skew.** CNCF has published CKAD and CKA at v1.35. But the newest CKS
curriculum in the repo is still **v1.34**, and the CKS *exam environment* already runs k8s
v1.35. So as of today, the CKS curriculum document lags the exam environment by one minor
release. LF states that the environment tracks the newest k8s minor "within approximately 4
to 8 weeks of the K8s release date". CNCF says that "Quarterly exam updates are planned to
match Kubernetes releases". So expect a CKS v1.35 document to land shortly. Design the CKS
phase against the v1.34 topics, and re-check before the learner sits the exam.

---

<a id="ckad"></a>
## 1. CKAD — Certified Kubernetes Application Developer

**Curriculum v1.35**, primary source:
[CKAD_Curriculum_v1.35.pdf](https://github.com/cncf/curriculum/blob/master/CKAD_Curriculum_v1.35.pdf)

### Domains and weights

| Weight | Domain |
|---|---|
| 25% | Application Environment, Configuration and Security |
| 20% | Application Design and Build |
| 20% | Application Deployment |
| 20% | Services and Networking |
| 15% | Application Observability and Maintenance |

These weights sum to 100%. That was verified by reading the PDF text directly.

### Competencies per domain (verbatim from the PDF)

**Application Design and Build (20%)**
- Define, build and modify container images
- Choose and use the right workload resource (Deployment, DaemonSet, CronJob, etc.)
- Understand multi-container Pod design patterns (e.g. sidecar, init and others)
- Utilize persistent and ephemeral volumes

**Application Deployment (20%)**
- Use Kubernetes primitives to implement common deployment strategies (e.g. blue/green or canary)
- Understand Deployments and how to perform rolling updates
- Use the Helm package manager to deploy existing packages
- Kustomize

**Application Observability and Maintenance (15%)**
- Understand API depreciations *(sic — CNCF's own typo for "deprecations")*
- Implement probes and health checks
- Use built-in CLI tools to monitor Kubernetes applications
- Utilize container logs
- Debugging in Kubernetes

**Application Environment, Configuration and Security (25%)**
- Discover and use resources that extend Kubernetes (CRD, Operators)
- Understand authentication, authorization and admission control
- Understand requests, limits, quotas
- Define resource requirements
- Understand ConfigMaps
- Create & consume Secrets
- Understand ServiceAccounts
- Understand Application Security (SecurityContexts, Capabilities, etc.)

**Services and Networking (20%)**
- Demonstrate basic understanding of NetworkPolicies
- Provide and troubleshoot access to applications via services
- Use Ingress rules to expose applications

<a id="ckad-changes"></a>
### Recent changes (CKAD)

CKAD has been **substantively stable**. Here is what a diff of the PDFs shows.

- **v1.29 → v1.31:** weights unchanged (20/20/15/25/20).
- **v1.32** (Feb 2025): a layout rewrite plus typo corrections — "Development, DaemonSet"
  → "**Deployment**, DaemonSet"; "Understand Application" → "Understand Application
  **Security**". No topic added or removed, no weight moved.
- **v1.33** (Jun 2025): fixed the typo "Kuztomize" → "**Kustomize**". Nothing else.
- **v1.34 → v1.35:** extracted text is **byte-for-byte identical**. Version bump only.

**Implication for the curriculum:** CKAD is the low-risk checkpoint. There are no retired
topics to avoid. Note one thing. Ingress is still the CKAD exposure primitive, and Gateway
API is not. Gateway API is a **CKA** topic.

---

<a id="cka"></a>
## 2. CKA — Certified Kubernetes Administrator

**Curriculum v1.35**, primary source:
[CKA_Curriculum_v1.35.pdf](https://github.com/cncf/curriculum/blob/master/CKA_Curriculum_v1.35.pdf)

### Domains and weights

| Weight | Domain |
|---|---|
| 30% | Troubleshooting |
| 25% | Cluster Architecture, Installation and Configuration |
| 20% | Servicing and Networking |
| 15% | Workloads and Scheduling |
| 10% | Storage |

These weights sum to 100%. They are **unchanged** from v1.31 through v1.35, because the
2025 revision moved *topics* and not percentages. This is the number that is most often
misquoted, and it is verified here from the PDF.

### Competencies per domain (verbatim from the PDF)

**Cluster Architecture, Installation and Configuration (25%)**
- Manage role based access control (RBAC)
- Prepare underlying infrastructure for installing a Kubernetes cluster
- Create and manage Kubernetes clusters using kubeadm
- Manage the lifecycle of Kubernetes clusters
- Implement and configure a highly-available control plane
- **Use Helm and Kustomize to install cluster components**
- **Understand extension interfaces (CNI, CSI, CRI, etc.)**
- **Understand CRDs, install and configure operators**

**Workloads and Scheduling (15%)**
- Understand application deployments and how to perform rolling update and rollbacks
- Use ConfigMaps and Secrets to configure applications
- **Configure workload autoscaling**
- Understand the primitives used to create robust, self-healing, application deployments
- **Configure Pod admission and scheduling (limits, node affinity, etc.)**

**Servicing and Networking (20%)**
- Understand connectivity between Pods
- **Define and enforce Network Policies**
- Use ClusterIP, NodePort, LoadBalancer service types and endpoints
- **Use the Gateway API to manage Ingress traffic**
- Know how to use Ingress controllers and Ingress resources
- Understand and use CoreDNS

**Storage (10%)**
- **Implement storage classes and dynamic volume provisioning**
- Configure volume types, access modes and reclaim policies
- Manage persistent volumes and persistent volume claims

**Troubleshooting (30%)**
- Troubleshoot clusters and nodes
- Troubleshoot cluster components
- Monitor cluster and application resource usage
- Manage and evaluate container output streams
- Troubleshoot services and networking

<a id="cka-changes"></a>
### Recent changes (CKA) — this is the important one

The revision landed in **CKA v1.32, committed 2025-02-17**. The content is then
**byte-for-byte identical** across v1.32, v1.33, v1.34 and v1.35, because the later bumps
are version-label changes only. So "the new CKA" means the v1.32 revision, and that revision
is now about 18 months old.

**ADDED in v1.32:**
- **Use the Gateway API to manage Ingress traffic** (Gateway API enters the CKA)
- **Use Helm and Kustomize to install cluster components** (replaces the vague
  "Awareness of manifest management and common templating tools")
- **Understand CRDs, install and configure operators**
- **Understand extension interfaces (CNI, CSI, CRI, etc.)**
- **Define and enforce Network Policies** (previously CKS/CKAD territory on the CKA sheet)
- **Configure workload autoscaling** (replaces "Know how to scale applications")
- **Configure Pod admission and scheduling (limits, node affinity, etc.)** (replaces
  "Understand how resource limits can affect Pod scheduling")
- **Implement storage classes and dynamic volume provisioning** (Storage moves from
  "understand" to "implement" — dynamic provisioning is now explicit)
- **Manage the lifecycle of Kubernetes clusters** and **Implement and configure a
  highly-available control plane**

**REMOVED in v1.32 — do NOT drill these as CKA exam topics:**
- **"Implement etcd backup and restore"** — it is gone from the curriculum entirely. This
  is the single biggest trap. It is the most-drilled classic CKA task in every older course
  and question bank, and it is no longer a listed CKA competency.
  *Caveat:* etcd depth is still enormously valuable for the internals goals of this
  curriculum, and `etcd.io/docs` remains an allowed-docs domain for CKS. So keep etcd
  internals in the internals track. Just do not bill that work as CKA exam prep.
- **"Choose an appropriate container network interface plugin"** — generalised into
  "Understand extension interfaces (CNI, CSI, CRI, etc.)".
- **"Understand host networking configuration on the cluster nodes"** — dropped.
- **"Awareness of manifest management and common templating tools"** — replaced by the
  explicit Helm + Kustomize requirement.
- **"Perform a version upgrade on a Kubernetes cluster using Kubeadm"** — it is subsumed
  into the broader "Manage the lifecycle of Kubernetes clusters". Upgrades are still in
  scope, and the wording just widened.
- Section renamed "Services & Networking" → "**Servicing** and Networking".

**Two corroborating signals, independent of the PDF diff:**
1. `https://gateway-api.sigs.k8s.io/` is on the allowed-documentation list for CKA, **and for
   CKA only**. That confirms that Gateway API is genuinely examinable, and not aspirational
   curriculum text. Likewise, `helm.sh/docs/` is allowed for CKA and for CKAD.
2. LF published a dedicated CKA program-change notice for this revision:
   [CKA Program Changes](https://training.linuxfoundation.org/certified-kubernetes-administrator-cka-program-changes)
   (Feb 2025), calling out the Gateway API and Helm/Kustomize additions.

---

<a id="cks"></a>
## 3. CKS — Certified Kubernetes Security Specialist

**Curriculum v1.34**, primary source:
[CKS_Curriculum v1.34.pdf](https://github.com/cncf/curriculum/blob/master/CKS_Curriculum%20v1.34.pdf)

### Domains and weights

| Weight | Domain |
|---|---|
| 20% | Minimize Microservice Vulnerabilities |
| 20% | Supply Chain Security |
| 20% | Monitoring, Logging and Runtime Security |
| 15% | Cluster Setup |
| 15% | Cluster Hardening |
| 10% | System Hardening |

These weights sum to 100%.

### Competencies per domain (verbatim from the PDF)

**Cluster Setup (15%)**
- Use Network security policies to restrict cluster level access
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
- Properly set up Ingress objects with TLS
- Protect node metadata and endpoints
- Verify platform binaries before deploying

**Cluster Hardening (15%)**
- Use Role Based Access Controls to minimize exposure
- Exercise caution in using service accounts e.g. disable defaults, minimize permissions
  on newly created ones
- Restrict access to Kubernetes API
- Upgrade Kubernetes to avoid vulnerabilities

**System Hardening (10%)**
- Minimize host OS footprint (reduce attack surface)
- Using least-privilege identity and access management
- Minimize external access to the network
- Appropriately use kernel hardening tools such as AppArmor, seccomp

**Minimize Microservice Vulnerabilities (20%)**
- Use appropriate pod security standards
- Manage kubernetes secrets
- Understand and implement isolation techniques (multi-tenancy, sandboxed containers, etc.)
- **Implement Pod-to-Pod encryption (Cilium, Istio)**

**Supply Chain Security (20%)**
- Minimize base image footprint
- Understand your supply chain (e.g. SBOM, CI/CD, artifact repositories)
- Secure your supply chain (permitted registries, sign and validate artifacts, etc.)
- Perform static analysis of user workloads and container images (e.g. Kubesec, KubeLinter)

**Monitoring, Logging and Runtime Security (20%)**
- Perform behavioral analytics to detect malicious activities
- Detect threats within physical infrastructure, apps, networks, data, users and workloads
- Investigate and identify phases of attack and bad actors within the environment
- Ensure immutability of containers at runtime
- Use Kubernetes audit logs to monitor access

<a id="cks-changes"></a>
### Recent changes (CKS)

**The emphasis shift landed in v1.31, committed 2024-10-15:**
- **Cluster Setup 10% → 15%** (weight up)
- **System Hardening 15% → 10%** (weight down)
- "Setup appropriate OS level security domains" → **"Use appropriate pod security
  standards"** — the PSP-era framing is gone; Pod Security Standards / Pod Security
  Admission is the examinable mechanism now.
- "Use container runtime sandboxes in multi-tenant environments (e.g. gvisor, kata
  containers)" → generalised to **"Understand and implement isolation techniques
  (multi-tenancy, sandboxed containers, etc.)"**. gVisor and Kata are no longer named.
- "Implement pod to pod encryption by use of mTLS" → **"Implement Pod-to-Pod encryption
  using Cilium"** (Cilium named explicitly).
- "Properly set up Ingress objects with security control" → **"...with TLS"**.
- "Update Kubernetes frequently" → "Upgrade Kubernetes to avoid vulnerabilities".
- "Minimize IAM roles" → "Using least-privilege identity and access management".
- Supply-chain wording modernised to **SBOM / artifact signing** language.
- **REMOVED:** "Minimize use of, and access to, GUI elements". The old
  Kubernetes-Dashboard-hardening task is gone. Do not drill it.
- **REMOVED:** "Scan images for known vulnerabilities" as a standalone line. It is folded
  into the static-analysis bullet.

**Then in v1.33, committed 2025-07-03 — the only content change since:**
- "Implement Pod-to-Pod encryption using Cilium" → **"Implement Pod-to-Pod encryption
  (Cilium, Istio)"**. **Istio added** alongside Cilium.

**v1.34 (2025-10-30) is byte-for-byte identical to v1.33** — version label only.

**Corroborating signal:** both `https://docs.cilium.io/en/stable` and
`https://istio.io/latest/docs/` are on the CKS allowed-documentation list. That matches the
v1.33 change exactly. `https://falco.org/docs/` is allowed as well, which confirms that
Falco is the expected behavioural-analytics tool. The curriculum text does not name it.

---

<a id="mechanics"></a>
## 4. Exam mechanics (all three)

| Item | CKAD | CKA | CKS |
|---|---|---|---|
| Duration | 2 hours | 2 hours | 2 hours |
| Passing score | 66% | 66% | **67%** |
| Tasks | 15–20 | 15–20 | 15–20 |
| Format | performance-based, remote desktop | same | same |
| Validity | 2 years | 2 years | 2 years |
| Retakes included | 1 | 1 | 1 |
| Eligibility window | 12 months | 12 months | 12 months |
| Prerequisite | none | none | **CKA (see §6)** |

- **Task count:** "The exams consist of 15-20 performance-based tasks."
  ([CKA/CKAD instructions](https://docs.linuxfoundation.org/tc-docs/certification/tips-cka-and-ckad),
  [CKS instructions](https://docs.linuxfoundation.org/tc-docs/certification/important-instructions-cks))
- **Passing scores** are per-exam and differ: CKA 66%, CKAD 66%, CKS **67%**
  ([FAQ](https://docs.linuxfoundation.org/tc-docs/certification/faq-cka-ckad-cks)).
- **Delivery:** the exam is online and proctored, via the **PSI Bridge** proctoring
  platform. It is a remote desktop, launched in the PSI Secure Browser. That desktop holds
  three things: a Linux terminal emulator, **VSCodium** as a graphical editor with an
  integrated terminal, and a Firefox browser that is locked to the allowed-docs domains.
  Installing VSCodium extensions is prohibited.
  ([Candidate Handbook](https://docs.linuxfoundation.org/tc-docs/certification/lf-handbook2),
  [ExamUI: Performance Based Exams](https://docs.linuxfoundation.org/tc-docs/certification/lf-handbook2/exam-user-interface/examui-performance-based-exams))
- **Validity was cut from 36 months to 24 months**, effective **2024-04-01 00:00 UTC**:
  "36-month certification period will change to a 24-month certification period starting for
  exams taken April 1, 2024, 00:00 UTC." Certs that were earned before then keep 36 months,
  because they "will remain active for 36 months from the achieved date". **CKS was
  explicitly unaffected**, because it was always 24 months.
  ([Certification Policy Change 2024](https://training.linuxfoundation.org/certification-policy-change-2024/))
- **Recertification:** retake and pass the same exam before expiry, which extends validity
  2 years from the new pass date.
- **Retake:** you get one free retake per purchase. You must use it within 12 months of
  the original purchase. No primary page states a mandatory cooldown between attempts. So it
  is **[UNVERIFIED]** whether a waiting period exists at all.

<a id="allowed-docs"></a>
### Allowed documentation

Primary source:
[Resources Allowed: All LF Certification Programs](https://docs.linuxfoundation.org/tc-docs/certification/certification-resources-allowed)

**CKA and CKAD:**
- `https://kubernetes.io/docs/`
- `https://kubernetes.io/blog/`
- `https://helm.sh/docs/`
- `https://gateway-api.sigs.k8s.io/` — **CKA only**

**CKS** (a notably wider list):
- `https://kubernetes.io/docs/`
- `https://kubernetes.io/blog/`
- `https://falco.org/docs/`
- `https://kubernetes-sigs.github.io/bom/cli-reference/`
- `https://etcd.io/docs/`
- `https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/`
- `https://docs.cilium.io/en/stable`
- `https://istio.io/latest/docs/`

Plus task-specific documentation surfaced in the exam's Quick Reference box.

**Search rule:** you may use the search function on the allowed sites, "but you must not
open external search results". The same restriction applies to the search on Istio's site.
Prefer the English pages over the localised ones, because the English pages are the most
current.

<a id="tab-policy"></a>
### Tab policy — what's documented vs. what's folklore

Here is what is **verified**. You browse the documentation in a **Firefox browser inside
the proctored remote desktop**, and that browser is restricted to the allowed domains. The
wording is "Firefox browser to access 'Resources Allowed'". The remote desktop presents
**"2 tabs presented as default"**. One is the **ReadMe** tab, which holds "important
instructions regarding the exam environment". The other is the **Remote Desktop** tab, which
is "the workstation configured with the necessary applications and tools".
([ExamUI: Performance-Based Exams](https://docs.linuxfoundation.org/tc-docs/certification/lf-handbook2/exam-user-interface/examui-performance-based-exams))

Here is what is **not** verified: the widely repeated rule that "you may have one
additional browser tab open". That rule is **[UNVERIFIED]**. No current primary page states
it. No current primary page states a numeric limit on open applications or browser windows
either. The rule appears to date from the era before PSI Bridge, when the exam ran in the
candidate's own browser rather than in a proctored remote desktop. The delivery model has
clearly changed. But **treat "the one-tab rule has been abolished" as an inference, and not
as a documented fact.** The operative constraint today is the *domain whitelist*, plus the
no-external-search-results rule, and both of those are documented. Any course that still
teaches "one extra tab" is describing an obsolete platform at minimum.

---

<a id="tooling"></a>
## 5. Tooling reality

Everything in this section comes from the official instructions pages.
([CKA/CKAD](https://docs.linuxfoundation.org/tc-docs/certification/tips-cka-and-ckad),
[CKS](https://docs.linuxfoundation.org/tc-docs/certification/important-instructions-cks)).

- **The kubectl and Kubernetes version is v1.35** for all three exams, as of today. The LF
  policy reads: "The CKA, CKS and CKAD exam environment will be aligned with the most recent
  K8s minor version within approximately 4 to 8 weeks of the K8s release date." So your lab
  clusters should track the newest minor version, and not a pinned old one.
- **Aliases and autocompletion are PRE-CONFIGURED, not something to set up.** Verbatim:
  "All SSH hosts have the following additional command-line tools pre-installed and
  pre-configured: **kubectl with `k` alias and Bash autocompletion**, **`yq`** for YAML
  processing, **`curl`** and **`wget`** for testing web services, **`man`** and man pages."
  - **Curriculum consequence:** do *not* spend drill time on building an alias or `vimrc`
    bootstrap ritual. `k` and completion are already there. Drill *using* them. Drill `yq`
    as well, because it is provided, and it is the fastest way to mutate YAML
    non-interactively.
  - **A trap worth drilling:** "The base system (with hostname `base`) does **not** have any
    of the above tools pre-installed as all tasks on this exam must be completed on a
    designated SSH host." So every task begins with an SSH to the right host.
- **Host discipline.** This is the CKS wording, and it is the general pattern: "Each task
  on this exam must be completed on a designated host", and "You must **return to the base
  node** (with hostname `base`) after completing each task. **Nested ssh is not
  supported.**" This is the modern equivalent of the old context-switching discipline, and
  it is a genuine failure mode. Work that you do on the wrong host scores zero.
- **Multiple clusters, and `kubectl config use-context`.** This is **[UNVERIFIED]** from
  primary sources. The official pages describe per-task **designated SSH hosts**, reached
  from `base`. They say nothing about multiple kubeconfig contexts. The claim that "each
  question tells you which context to switch to" appears in community write-ups only. So
  **drill the ssh-to-designated-host discipline as the primary habit.** Treat `use-context`
  as a cheap secondary habit, and not as a documented requirement.
- **Editors.** **VSCodium** is explicitly documented. **vim** is strongly implied, because
  the instructions give the classic vim workaround: "For security reasons, the **INSERT key
  is prohibited** within the Remote Desktop. Candidates can **Type `i`** to switch into
  insert mode... press **`Esc`** to get out of insert mode." **nano** is **[UNVERIFIED]**,
  because no primary page mentions it. So plan for vim, and know that VSCodium exists.
  - **Drill the INSERT-key restriction explicitly.** Muscle memory that reaches for the
    Insert key will silently fail under exam conditions.
- **Copy and paste.** In the Linux terminal it is `Ctrl+Shift+C` and `Ctrl+Shift+V`. In
  the other remote desktop applications it is `Ctrl+C` and `Ctrl+V`. Rehearse that, because
  the split convention costs time.
- **Use `Ctrl+Alt+W`, and never `Ctrl+W`.** In the browser-hosted exam, `Ctrl+W` closes the
  tab. That is another documented habit-breaker, and it is worth drilling next to the INSERT
  key.
- **A handy prep trick.** Append **`.md`** to any `docs.linuxfoundation.org` documentation
  URL, and you get a clean Markdown version of the page. That is useful while you study the
  official instructions. You do not need it in the exam.
- **VSCodium is available**, from the Applications menu or the desktop icon. But
  **"installing extensions in VSCodium is disabled and strictly prohibited during the
  exam"**. So there is no YAML-linting extension to lean on. You get plain vim, or bare
  VSCodium.
- It is **[UNVERIFIED]** whether you may configure *additional* personal aliases or a custom
  `.vimrc`, beyond what ships pre-provisioned. No primary page addresses it.

---

<a id="ordering"></a>
## 6. CKA → CKS prerequisite (the constraint on cert ordering)

**CKA is still a required prerequisite for CKS. But it does NOT have to be unexpired.**

CNCF's own CKS page states it explicitly, parenthetical included:

> "CKS candidates must have taken and passed the Certified Kubernetes Administrator (CKA)
> exam prior to attempting the CKS exam **(but CKA doesn't have to be active)**."
> — [cncf.io/training/certification/cks](https://www.cncf.io/training/certification/cks/)

The LF product page carries the requirement without the parenthetical:

> "Certified Kubernetes Security Specialist (CKS) candidates must have taken and passed the
> Certified Kubernetes Administrator (CKA) exam prior to attempting the CKS exam."
> — [training.linuxfoundation.org CKS](https://training.linuxfoundation.org/certification/certified-kubernetes-security-specialist/)

Both statements are official. The CNCF wording is the more specific one, and it answers the
question directly. **Passing the CKA at any point in the past satisfies the prerequisite, and
expiry is irrelevant.**

### And it now runs the other way too — the CARE program

Effective **2026-06-18**, passing *or* recertifying CKS **automatically reinstates or
extends** the CKA:

> "Passing the Certified Kubernetes Security Specialist (CKS) exam or recertifying your CKS
> will automatically reinstate or extend your Certified Kubernetes Administrator (CKA)
> certification. This applies whether your CKA is still active or has already expired."

The CKA expiration date is realigned to the newly earned or renewed CKS. No conditions and
no limits were stated.
Sources: [LF blog](https://training.linuxfoundation.org/blog/expanding-care-passing-cks-can-now-extend-your-cka-certification/),
[CNCF blog, 2026-06-17](https://www.cncf.io/blog/2026/06/17/expanding-care-passing-cks-can-now-extend-your-cka-certification/),
[CARE Program](https://training.linuxfoundation.org/care-program/),
[FAQ](https://docs.linuxfoundation.org/tc-docs/certification/faq-cka-ckad-cks).

### Consequence for the curriculum

The staged ordering **CKAD → CKA → CKS** is confirmed valid, and it is the *only* legal
ordering for CKS. Critically, **there is no deadline pressure between CKA and CKS**:

- The 2-year CKA clock does **not** constrain when CKS may be attempted.
- A slow, depth-first march through the security phases cannot invalidate the CKS
  eligibility earned by passing CKA.
- Better still, CKS-last is now the *optimal* order, both financially and
  administratively. Passing CKS refreshes the CKA for another 2 years, so the learner does
  not need to sit a CKA retake to stay current. **That is a strong argument for keeping CKS
  as the final checkpoint, rather than resequencing.**
- The 12-month *voucher* eligibility window is the only real clock, and it starts at
  purchase. So the curriculum should say "buy the voucher when the relevant phases are
  nearly done". It should not say "buy all three up front".

---

<a id="vouchers"></a>
## 7. What ships with an exam voucher

This section comes from the CKA, CKAD and CKS product pages, and from the FAQ.

- **Exam simulator by killer.sh — still bundled, unchanged.** "Once enrolled you will
  receive access to an exam simulator, provided by **Killer.sh**... You will have **two
  simulation attempts (36 hours of access for each attempt from the start of activation)**."
  The FAQ confirms: "Candidates will have two attempts (per exam registration). Each attempt
  grants 36 hours of access starting from the time of activation," and names Killer.sh as the
  provider for CKA, CKAD **and** CKS.
- Each simulator session has **17 questions**, with "a different set of questions (17
  total) in each attempt". Note that 17 is the count for the *simulator*. The real exam has
  15 to 20 tasks.
- **One retake**, **12-month eligibility window**, PDF certificate and digital badge.
- **A carve-out worth knowing.** The FAQ states: "Exam Simulator access is **not** included
  in CKA-SINGLE, CKAD-SINGLE, CKS-SINGLE Exam Registrations." What exactly the `-SINGLE`
  SKUs are is **[UNVERIFIED]**. The most plausible reading is a reduced or retake-only
  registration, rather than the standard purchase. But the definition was not found on a
  primary page. So if the learner buys a non-standard or discounted SKU, confirm simulator
  inclusion before relying on it.
- No training course is bundled with a base exam voucher. The product pages list four
  things: exam delivery, the simulator, the retake, and the certificate with the badge.
  Nothing on that list is instructional. LF does sell separate exam-plus-training SKUs and
  multi-exam bundle SKUs. But that is **[UNVERIFIED]**, because the specific bundle products
  and their contents were not confirmed against a primary page in this pass. Check the LF
  catalogue at purchase time.
- The scheduling mechanics are **[UNVERIFIED]**. That covers the minimum lead time before
  you can sit an exam, and the forward scheduling window. Neither the FAQ nor the pages
  fetched addresses them. The only documented clock is the **12-month eligibility window**
  from purchase.

Sources: [CKA](https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/),
[CKAD](https://training.linuxfoundation.org/certification/certified-kubernetes-application-developer-ckad/),
[CKS](https://training.linuxfoundation.org/certification/certified-kubernetes-security-specialist/),
[FAQ](https://docs.linuxfoundation.org/tc-docs/certification/faq-cka-ckad-cks).

---

<a id="practice"></a>
## 8. Practice resources, with honest quality notes

The resources are ordered by usefulness to this curriculum. **The quality notes are
deliberately blunt.** Several widely recommended resources are stale, and one has been
discontinued outright.

<a id="currency-test"></a>
### The currency litmus test

Use this test to triage *any* resource, including the ones that are not listed here.

> **If it predates ~February 2025 and never mentions Gateway API, Helm/Kustomize as a CKA
> install competency, or CRDs/operators — it is describing the pre-v1.32 CKA and is stale.
> If its lab environment is pinned to Kubernetes ≤ v1.30, discount it further.**

The exam environment is on **v1.35** today, and LF realigns within 4 to 8 weeks of each
minor release. So a resource that is two minor versions behind is normal and tolerable. A
resource that is five behind is not.

### Tier 1 — use these

**killer.sh** — <https://killer.sh> · **the single strongest resource, and you already own it.**
- Every standard voucher bundles it. You get 2 sessions of 36 hours, with 17 questions
  each. See §7.
- **Currency: good.** The killer.sh FAQ states that its CKA, CKAD, CKS and CNPE environments
  are at **Kubernetes 1.35**. That matches the live exam version.
  ([killer.sh/faq](https://killer.sh/faq), vendor-stated)
- **On the claim that "it's harder than the real exam":** that is **community consensus,
  and not an official claim.** The killer.sh FAQ explicitly *declines* to quantify difficulty,
  and it declines to map simulator scores onto real scores. It says only that the questions
  are "of the same type" as the real exam. So the claim is **[UNVERIFIED]** as a sourced
  fact. Treat the harder-than-real reputation as useful framing, in the sense of "train
  harder than the test". But **do not read a mediocre simulator score as a fail signal**,
  because that inference is unsupported.
- **Curriculum consequence:** a session lasts 36 hours once you activate it. So **do not
  activate until the phase work is done.** Schedule the activations deliberately. Use session
  1 as a diagnostic, about 2 weeks out. Use session 2 as a dress rehearsal, a few days out.

**`kubernetes.io/docs/tasks/`** — <https://kubernetes.io/docs/tasks/> · **not optional.**
This is the only general-purpose docs site that is permitted in the exam (§4). So navigation
fluency is a direct speed multiplier, and not background reading. These are the
highest-yield sections:
- `/docs/tasks/debug/` is the **most important single section**, because Troubleshooting is
  30% of CKA.
- `/docs/tasks/configure-pod-container/` covers limits, securityContexts, probes and volumes.
  It serves CKAD and CKS.
- `/docs/tasks/run-application/` covers Deployments, rolling updates, StatefulSets and the
  HPA. It serves CKAD.
- `/docs/tasks/access-application-cluster/` covers Services, port-forward and Ingress.
- `/docs/tasks/administer-cluster/` covers certificates, quotas, and node and cluster
  lifecycle. It serves CKA and CKS.
- `/docs/tasks/configmap-secret/` and `/docs/tasks/inject-data-application/` are CKAD
  staples.
- `/docs/tasks/extend-kubernetes/` covers CRDs and admission webhooks. It is newly relevant,
  because v1.32 added CRDs and operators to CKA.
- The **`kubectl` Cheat Sheet**, at <https://kubernetes.io/docs/reference/kubectl/cheatsheet/>,
  is the canonical source for nearly every speed tactic in §9. You can reach it in the exam.

**`dgkanatsios/CKAD-exercises`** — <https://github.com/dgkanatsios/CKAD-exercises>
- **Actively maintained and current.** It has 10.1k stars, and its last commit was
  **2026-08-03**, verified via the GitHub API, two weeks before this research. It is the best
  free CKAD question bank, full stop.

**`bmuschko/ckad-crash-course` / `cka-crash-course` / `cks-crash-course`**
- All three are actively maintained. The GitHub API gives CKAD **2026-05-19**, CKA
  **2026-04-01** and CKS **2025-11-18**. Ben Muschko is a reliable maintainer. CKS is the
  least fresh of the three, and it is still well within tolerance.

### Tier 2 — good, with caveats

**KodeKloud** (Mumshad Mannambeth) — **best structured beginner path, but FLAG the currency.**
- The pedagogy is genuinely strong. You get browser labs, so you need no local cluster.
  You also get practice tests woven through the lessons, Lightning Labs, and mock exams:
  3 for CKA, 2 for CKAD and 3 for CKS.
- **Currency flag.** All three course pages state **"Last Updated: May 26, 2025"**, and the
  labs are being moved to **Kubernetes v1.33**. That is about 15 months old, and two minor
  versions behind the live exam as of today. The Helm and Kustomize sections were added
  around January 2025, so the post-v1.32 competency coverage is *plausibly* intact. But
  **verify that at enrolment, rather than trusting this note.** The content may have been
  updated without the headline date moving.
- It is a subscription model. A free tier exists, and full lab access is paid.
- **Curriculum consequence:** it is valuable for the learner's *first* exposure. But this
  curriculum already builds the foundations properly, from a homelab. So KodeKloud is
  optional reinforcement, and not the spine. Its main unique value is the browser labs, and
  that matters less here, because `factory` exists.

**Killercoda** — <https://killercoda.com/cka> · <https://killercoda.com/ckad> ·
<https://killercoda.com/cks>
- **IMPORTANT: the resource that the ticket named has been discontinued.** The original
  free scenario sets by Kim Wüstkamp, at `killercoda.com/killer-shell-cka` and
  `killer-shell-ckad`, now show *"The Killer Shell CKA scenarios have been replaced with the
  CKA Scenario Course"*. **Any roundup that still recommends `killer-shell-*` as the free
  go-to is pointing at a dead end.**
- A **"Scenario Course"** replaced them, at `killercoda.com/course/cka` and `/course/ckad`.
  It looks paid, and it offers "complex and supported scenarios with additional videos". The
  pricing is **[UNVERIFIED]**.
- Free scenarios still exist, on the generic `/cka` and `/ckad` landing pages. But they are
  now a **multi-author patchwork**: "AcingTheCKA" by Chad M. Crowell, plus scenarios by
  Sachin H R and Alexis Carbillet, plus `cka-mock-practice` by Omkar Shelke. They carry **no
  visible version metadata and no last-updated metadata**. Quality and currency are therefore
  inconsistent, so **spot-check each scenario, and do not trust the set.**
- The current CKS free-scenario coverage is **[UNVERIFIED]**. `killercoda.com/cks` did not
  render usable scenario content when it was fetched. It needs a manual check before the CKS
  phase cites it.

**`walidshaari/Kubernetes-Certified-Administrator`** — <https://github.com/walidshaari/Kubernetes-Certified-Administrator>
- **FLAG: stale.** It has 4.4k stars, but its last commit was **2025-01-05**, verified via
  the GitHub API. That is about 19 months idle, and it **predates the v1.32 CKA revision
  entirely.** Its content references v1.31 as the standard. It is still usable as a topic
  index or a link farm. It is **not a source of truth on the current CKA scope.** Older blog
  roundups recommend it heavily, so flag it explicitly.
- The companion repo, `walidshaari/Certified-Kubernetes-Security-Specialist`, is healthier.
  Its last commit was **2026-03-14**.

**Other exercise repos checked**, through the GitHub API, for completeness:
- `chadmcrowell/CKA-Exercises` — last commit 2025-10-08. It is reasonably fresh.
- `David-VTUK/CKA-StudyGuide` — last commit 2025-03-15. It is borderline, because it
  post-dates v1.32 only narrowly.
- `stretchcloud/cka-lab-practice` — **last commit 2020-06-10. Six years dead. Avoid it.**

**LF's own free training: LFS158 "Introduction to Kubernetes"** —
<https://training.linuxfoundation.org/training/introduction-to-kubernetes/>
- It is confirmed **free**, at $0. You get 17 chapters, 15 to 20 hours of work, hands-on
  labs, 90-day access, and a digital badge.
- It is genuinely useful as a zero-cost orientation, although Phase 1 of this curriculum
  goes deeper. Which k8s version it targets is **[UNVERIFIED]**.
- LF sells three paid companions: **LFS258** aligns to CKA, **LFS259** to CKAD, and
  **LFS260** to CKS.

### Tier 3 — avoid

- **Exam dumps and braindump sites**, meaning the ExamTopics-style aggregators and
  similar. **There are two independent reasons to refuse them:**
  1. **They violate the LF Candidate/Confidentiality Agreement**, which explicitly prohibits
     "using recollections of others or materials from previous administration of any Exam,
     a.k.a. braindump material", with penalties up to **score cancellation, permanent ban,
     and revocation of existing certifications**.
     ([LF Certification & Confidentiality Agreement](https://docs.linuxfoundation.org/tc-docs/certification/lf-cert-agreement))
  2. **They do not even work.** These are hands-on performance exams. Static question-and-
     answer pairs are a category error, and they are frequently wrong about how the tasks
     actually behave.
- **Any "CKA crash course" on Udemy or YouTube that predates February 2025.** Apply the
  litmus test above. This entry is **[UNVERIFIED]** at the level of specific course titles.
  They were not confirmable in this pass, because the search budget was exhausted and the
  review-aggregator pages blocked automated fetching. So no individual course is named here.
  Judge by the test, and not by the rating. A highly-rated 2023 course still teaches etcd
  backup and restore as a core CKA task, and it still teaches the obsolete one-tab rule.
- **Anything that teaches the "one additional browser tab" rule, or an alias-bootstrap
  ritual.** Both describe an obsolete platform. See §4 and §5.

### Notable gap

There is **no official LF-built simulator.** The FAQ is explicit that the simulator is
"provided by Killer.sh". That is a bundled third-party partner product, and not an LF tool.
So the bundled killer.sh sessions are effectively irreplaceable. That reinforces the advice
above about not burning them early.

---

<a id="speed-tactics"></a>
## 9. Speed tactics to drill

This section is kept deliberately **separate from internals depth**, per the standing
preference in issue #1. This is a *timed correctness* skill, and it is drilled as one. Do the
arithmetic: 15 to 20 tasks in 120 minutes is roughly **6 minutes per task**. And the pass
marks of 66%, 66% and 67% mean that you can sacrifice roughly a third of the paper. So triage
is itself a skill.

### Tier 1 — the load-bearing habits

1. **Never write YAML from scratch.** Generate a manifest first, and then edit it:
   - `kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml`
   - `kubectl create deployment web --image=nginx --replicas=3 --dry-run=client -o yaml`
   - `kubectl create job`, `cronjob`, `configmap`, `secret`, `serviceaccount`, `role`,
     `rolebinding`, `clusterrole`, `clusterrolebinding`, `quota`, `ingress`, `service`
   - `kubectl expose` for Services off an existing workload
2. **Export two variables.** Set `export do='--dry-run=client -o yaml'`, so that every
   generator becomes `k run x --image=y $do`. Set `export now='--force --grace-period=0'` as
   well. The `k` alias and completion are already provisioned, as §5 explains. So these two
   variables are the one shell nicety that is worth adding yourself. **Sourcing note:** this
   idiom is *community convention*. The killer.sh study tips popularised it, and LF does
   **not** document it. The
   [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/) documents
   the analogous aliases officially: `kx` for context, `kn` for namespace, and `-A` as
   shorthand for `--all-namespaces`.
3. **Know `--dry-run=client` against `--dry-run=server`.** The server-side form validates
   against admission. That matters for the Pod Security Admission tasks on CKS.
4. **Delete fast.** Use `kubectl delete pod x --force --grace-period=0`, because terminating
   pods burn exam clock.
5. **Use `kubectl explain <res>.<path> --recursive`.** It is the fastest field lookup in the
   terminal, and it beats navigating kubernetes.io for a field name. Drill it until it
   replaces the reflex to open the docs browser.
6. **Use `kubectl -h` and `kubectl <verb> <res> -h`.** The examples block at the bottom of
   the help output is faster than the website for flag syntax.

### Tier 2 — extraction and inspection

7. **Use `-o jsonpath`** when a task demands an exact output format written to a file. For
   example, `kubectl get pods -o jsonpath='{.items[*].metadata.name}'`, or
   `{range .items[*]}{.metadata.name}{"\t"}{.status.podIP}{"\n"}{end}`.
8. **Use `-o custom-columns=` and `--sort-by=`.** For example,
   `--sort-by=.metadata.creationTimestamp`, or `--sort-by=.spec.nodeName`.
9. **Use `yq`.** The exam environment provides it. It is the fastest way to patch a field in
   an existing manifest, because it needs no editor round-trip.
10. `kubectl get <res> -A --show-labels`, `-l key=value`, `-o wide`, `--field-selector`
11. **Build these debug reflexes.** Run `kubectl describe`, and read the Events section
    first. Then `kubectl logs --previous`,
    `kubectl get events --sort-by=.metadata.creationTimestamp`, `kubectl exec -it`, and
    `kubectl debug` for ephemeral containers. Run
    `kubectl auth can-i --as=system:serviceaccount:ns:sa` on every RBAC task. Run
    `kubectl top nodes/pods` for the CKA "monitor resource usage" competency.
12. **Verify connectivity** with `kubectl cp` and `kubectl port-forward`.

### Tier 3 — editing and environment discipline

13. **Drive vim under exam conditions.** Type `:set expandtab shiftwidth=2 tabstop=2`
    first, because YAML indentation is the number one self-inflicted failure. Type
    `:set paste` before you paste. Then `:set number`, visual-block indent with `Ctrl+V` and
    `>`, `dd` and `p`, and `:wq`. **Sourcing note:** this is community convention, and LF
    does not document it. Whether you may create a persistent `.vimrc` in the exam is
    **[UNVERIFIED]**, so assume that you type these settings once per file.
14. **The INSERT key is prohibited.** Type `i` instead. Drill this, because the rule is
    documented and it breaks an ingrained habit. See §5.
15. **Learn the split copy-and-paste convention.** Use `Ctrl+Shift+C` and `Ctrl+Shift+V` in
    the terminal, and `Ctrl+C` and `Ctrl+V` everywhere else.
16. **Keep host discipline.** SSH to the designated host for every task, and **return to
    `base` afterwards.** Never nest an SSH session. Verify where you are before you mutate
    anything, with `hostname` and `kubectl config current-context`.
17. **Keep namespace discipline.** Always pass `-n`, or run
    `kubectl config set-context --current --namespace=x`. Silent wrong-namespace work is a
    top scoring loss.
18. **Rehearse doc navigation.** Find things by *searching within* `kubernetes.io/docs` only,
    because external search results are forbidden. See §4. Know the high-yield task pages
    cold, so that the docs stay a fallback and never become the primary path.
19. **Triage the paper.** Read every task first. Bank the cheap ones, and flag and skip the
    expensive ones. A third of the paper is expendable. Never let one hard task eat 20
    minutes.

---

<a id="open-items"></a>
## 10. Open items / not verified from a primary source

- Whether the exam uses **multiple kubeconfig contexts**, which would require
  `use-context`. The official pages describe designated SSH hosts only. Community sources
  claim contexts.
- Whether **nano** is available in the exam terminal.
- Whether you may configure **custom aliases or a personal `.vimrc`**, beyond the
  pre-provisioned `k` alias and completion.
- Whether any **cooldown period** applies between an exam attempt and its retake. Only the
  12-month outer window is documented.
- The exact definition of the **`CKA-SINGLE`, `CKAD-SINGLE` and `CKS-SINGLE`** SKUs, which
  exclude simulator access.
- The exact **forward scheduling window**, which is either 60 or 90 days.
- Whether a **CKS v1.35** curriculum document is imminent. The exam environment is already on
  k8s v1.35, and the curriculum PDF is still v1.34.
- The claim that **killer.sh is harder than the real exam**. It is community consensus only,
  and killer.sh itself declines to quantify difficulty.
- The free-scenario coverage of **Killercoda CKS**, and the pricing of the Killercoda
  "Scenario Course" that replaced the `killer-shell-*` sets.
- Whether the **KodeKloud** content has moved past the stated v1.33 and May-2025 headline.
- Which Kubernetes version **LFS158** targets.
- The specific stale Udemy and YouTube courses. They were not confirmable in this pass, so
  the litmus test in §8 substitutes for a named list.

### Research method note

The domain weights, the competency lists and the version history were established one way:
by **downloading the curriculum PDFs from `cncf/curriculum`, and diffing the extracted text**
across versions. They do not come from prose descriptions of those PDFs. The percentages were
read off the PDFs, and each domain set was checked to sum to 100%. The mechanics came from the
`training.linuxfoundation.org` product pages, and from the FAQ, instructions and handbook
pages on `docs.linuxfoundation.org`. The repo maintenance status came from the **GitHub API**,
by way of `pushed_at` and the latest commit, and not from README claims.

There is one caveat on method. The session's web-search budget was exhausted partway through.
So the practice-resources sweep relied on direct URL fetches, rather than on discovery search.
That biases §8 toward the resources that were already known by name. **There may be newer good
resources that this pass did not surface.** Everything that §8 actually asserts was fetched or
API-checked. So the risk here is omission, and not error.
