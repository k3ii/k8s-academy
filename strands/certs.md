# Certification

CKAD, CKA and CKS: verified domain weights, exam mechanics, what changed recently,
which practice resources are current, and which speed tactics are worth drilling.

Derived from [`../research/cert-exams.md`](../research/cert-exams.md), research date
2026-08-17. Every domain weight was read out of the current curriculum PDF in
[`cncf/curriculum`](https://github.com/cncf/curriculum) — none from memory or from
blog posts. Facts that could not be confirmed from a primary source are marked
**[UNVERIFIED]** inline, and the unresolved ones are collected under
[Open items](#open-items).

## Which phase sits which exam

| Phase | Exam | Anchor |
|---|---|---|
| P1 — operate shallow + Helm | **CKAD** | [CKAD](#ckad) |
| P8 — storage | **CKA** | [CKA](#cka) |
| P10 — security | **CKS** | [CKS](#cks) |

**CKS last is optimal, not merely convenient.** CKA is a hard prerequisite for CKS
but need not be *active*, and under the CARE programme passing CKS reinstates an
expired CKA — so the ordering that falls out of the spine is also the ordering that
buys the most validity. See [Cert ordering](#ordering).

## Three standing rules for this strand

1. **Cert results are never a gate.** A phase does not wait on an exam booking. The
   exam is external validation of work already done, and a failed sitting extends
   nothing.
2. **Exam drilling and internals depth are different activities.** Drilling optimises
   speed and correctness under time pressure; everything else optimises for
   understanding. A cert block in a phase file carries no source reading, and it says
   what *not* to drill as well as what to.
3. **Do not bill etcd depth as CKA prep.** CKA v1.32 **removed `etcd backup and
   restore` from the curriculum** — see [Recent changes (CKA)](#cka-changes). P2 spends a
   month on etcd because that is where control-plane mastery lives, not because the
   exam asks. Saying otherwise would be a lie the learner discovers at the worst
   moment.

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

**Note the CKS skew:** CNCF has published CKAD and CKA at v1.35 but the newest CKS
curriculum in the repo is still **v1.34**, while the CKS *exam environment* already runs
k8s v1.35. So the CKS curriculum document lags the exam environment by one minor release
as of today. LF states the environment tracks the newest k8s minor
"within approximately 4 to 8 weeks of the K8s release date", and CNCF says
"Quarterly exam updates are planned to match Kubernetes releases" — so expect a CKS v1.35
document to land shortly. Design the CKS phase against v1.34 topics and re-check before the
learner sits it.

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

Sums to 100%. Verified by reading the PDF text directly.

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

CKAD has been **substantively stable**. Diffing the PDFs:

- **v1.29 → v1.31:** weights unchanged (20/20/15/25/20).
- **v1.32** (Feb 2025): a layout rewrite plus typo corrections — "Development, DaemonSet"
  → "**Deployment**, DaemonSet"; "Understand Application" → "Understand Application
  **Security**". No topic added or removed, no weight moved.
- **v1.33** (Jun 2025): fixed the typo "Kuztomize" → "**Kustomize**". Nothing else.
- **v1.34 → v1.35:** extracted text is **byte-for-byte identical**. Version bump only.

**Implication for the curriculum:** CKAD is the low-risk checkpoint. No retired topics to
avoid. Note Ingress (not Gateway API) is still the CKAD exposure primitive — Gateway API is
a **CKA** topic, not CKAD.

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

Sums to 100%. Weights are **unchanged** from v1.31 through v1.35 — the 2025 revision moved
*topics*, not percentages. This is the number most often misquoted; it is verified here from
the PDF.

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

The revision landed in **CKA v1.32, committed 2025-02-17**. Content is then
**byte-for-byte identical** across v1.32, v1.33, v1.34 and v1.35 — the later bumps are
version-label changes only. So "the new CKA" means the v1.32 revision, now ~18 months old.

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
- **"Implement etcd backup and restore"** — gone from the curriculum entirely. This is the
  single biggest trap: it is the most-drilled classic CKA task in every older course and
  question bank, and it is no longer a listed CKA competency.
  *Caveat:* etcd depth is still enormously valuable for this curriculum's internals goals
  (and `etcd.io/docs` remains a CKS allowed-docs domain) — so keep etcd internals in the
  internals track, just don't bill it as CKA exam prep.
- **"Choose an appropriate container network interface plugin"** — generalised into
  "Understand extension interfaces (CNI, CSI, CRI, etc.)".
- **"Understand host networking configuration on the cluster nodes"** — dropped.
- **"Awareness of manifest management and common templating tools"** — replaced by the
  explicit Helm + Kustomize requirement.
- **"Perform a version upgrade on a Kubernetes cluster using Kubeadm"** — subsumed into the
  broader "Manage the lifecycle of Kubernetes clusters" (upgrades are still in scope, the
  wording just widened).
- Section renamed "Services & Networking" → "**Servicing** and Networking".

**Corroborating signals** (two, independent of the PDF diff):
1. `https://gateway-api.sigs.k8s.io/` is on the allowed-documentation list for CKA **and only
   CKA** — confirmation that Gateway API is genuinely examinable, not aspirational curriculum
   text. Likewise `helm.sh/docs/` is allowed for CKA and CKAD.
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

Sums to 100%.

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
  (multi-tenancy, sandboxed containers, etc.)"** — gVisor and Kata are no longer named.
- "Implement pod to pod encryption by use of mTLS" → **"Implement Pod-to-Pod encryption
  using Cilium"** (Cilium named explicitly).
- "Properly set up Ingress objects with security control" → **"...with TLS"**.
- "Update Kubernetes frequently" → "Upgrade Kubernetes to avoid vulnerabilities".
- "Minimize IAM roles" → "Using least-privilege identity and access management".
- Supply-chain wording modernised to **SBOM / artifact signing** language.
- **REMOVED:** "Minimize use of, and access to, GUI elements" — the old
  Kubernetes-Dashboard-hardening task is gone. Do not drill it.
- **REMOVED:** "Scan images for known vulnerabilities" as a standalone line (folded into
  the static-analysis bullet).

**Then in v1.33, committed 2025-07-03 — the only content change since:**
- "Implement Pod-to-Pod encryption using Cilium" → **"Implement Pod-to-Pod encryption
  (Cilium, Istio)"**. **Istio added** alongside Cilium.

**v1.34 (2025-10-30) is byte-for-byte identical to v1.33** — version label only.

**Corroborating signal:** both `https://docs.cilium.io/en/stable` and
`https://istio.io/latest/docs/` are on the CKS allowed-documentation list, matching the
v1.33 change exactly. `https://falco.org/docs/` being allowed confirms Falco is the
expected behavioural-analytics tool despite not being named in the curriculum text.

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
- **Delivery:** online proctored, via the **PSI Bridge** proctoring platform. The exam is a
  remote desktop launched in the PSI Secure Browser containing a Linux terminal emulator,
  **VSCodium** (graphical editor with integrated terminal), and a Firefox browser locked to
  the allowed-docs domains. Installing VSCodium extensions is prohibited.
  ([Candidate Handbook](https://docs.linuxfoundation.org/tc-docs/certification/lf-handbook2),
  [ExamUI: Performance Based Exams](https://docs.linuxfoundation.org/tc-docs/certification/lf-handbook2/exam-user-interface/examui-performance-based-exams))
- **Validity was cut from 36 months to 24** effective **2024-04-01 00:00 UTC**: "36-month
  certification period will change to a 24-month certification period starting for exams
  taken April 1, 2024, 00:00 UTC." Certs earned before then keep 36 months
  ("will remain active for 36 months from the achieved date"). **CKS was explicitly
  unaffected** — it was always 24 months.
  ([Certification Policy Change 2024](https://training.linuxfoundation.org/certification-policy-change-2024/))
- **Recertification:** retake and pass the same exam before expiry, which extends validity
  2 years from the new pass date.
- **Retake:** one free retake per purchase, which must be used within 12 months of the
  original purchase. No explicit mandatory cooldown between attempts was found on any
  primary page — **[UNVERIFIED]** whether a waiting period exists at all.

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

**Search rule:** using the search function on the allowed sites is permitted, "but you must
not open external search results". Same restriction applies to Istio's search. English pages
are recommended over localised ones as they are the most current.

<a id="tab-policy"></a>
### Tab policy — what's documented vs. what's folklore

What is **verified**: documentation is browsed in a **Firefox browser inside the proctored
remote desktop**, restricted to the allowed domains — "Firefox browser to access 'Resources
Allowed'". The remote desktop presents **"2 tabs presented as default"**: the **ReadMe** tab
("important instructions regarding the exam environment") and the **Remote Desktop** tab
("the workstation configured with the necessary applications and tools").
([ExamUI: Performance-Based Exams](https://docs.linuxfoundation.org/tc-docs/certification/lf-handbook2/exam-user-interface/examui-performance-based-exams))

What is **not** verified: the widely repeated "you may have one additional browser tab open"
rule. **[UNVERIFIED]** — no current primary page states it, and no current primary page
states a numeric limit on open applications or browser windows either. The rule appears to
date from the pre-PSI-Bridge era, when the exam ran in the candidate's own browser rather
than in a proctored remote desktop; the delivery model has clearly changed. But **treat "the
one-tab rule has been abolished" as an inference, not a documented fact** — the operative
constraint today is the *domain whitelist* plus the no-external-search-results rule, which is
documented. Any course still teaching "one extra tab" is at minimum describing an obsolete
platform.

---

<a id="tooling"></a>
## 5. Tooling reality

All from the official instructions pages
([CKA/CKAD](https://docs.linuxfoundation.org/tc-docs/certification/tips-cka-and-ckad),
[CKS](https://docs.linuxfoundation.org/tc-docs/certification/important-instructions-cks)).

- **kubectl / Kubernetes version: v1.35** for all three exams as of today. LF policy: "The
  CKA, CKS and CKAD exam environment will be aligned with the most recent K8s minor version
  within approximately 4 to 8 weeks of the K8s release date." Lab clusters should therefore
  track the newest minor, not a pinned old one.
- **Aliases and autocompletion are PRE-CONFIGURED, not something to set up.** Verbatim:
  "All SSH hosts have the following additional command-line tools pre-installed and
  pre-configured: **kubectl with `k` alias and Bash autocompletion**, **`yq`** for YAML
  processing, **`curl`** and **`wget`** for testing web services, **`man`** and man pages."
  - **Curriculum consequence:** do *not* spend drill time on building an alias/`vimrc`
    bootstrap ritual. `k` and completion are already there. Drill *using* them, and drill
    `yq` — it is provided and is the fastest way to mutate YAML non-interactively.
  - **Trap worth drilling:** "The base system (with hostname `base`) does **not** have any
    of the above tools pre-installed as all tasks on this exam must be completed on a
    designated SSH host." Every task begins by SSH-ing to the right host.
- **Host discipline (CKS wording, and the general pattern):** "Each task on this exam must
  be completed on a designated host", "You must **return to the base node** (with hostname
  `base`) after completing each task. **Nested ssh is not supported.**" This is the modern
  equivalent of the old context-switching discipline and is a genuine failure mode — work
  done on the wrong host scores zero.
- **Multiple clusters / `kubectl config use-context`:** **[UNVERIFIED]** from primary
  sources. The official pages describe per-task **designated SSH hosts** reached from
  `base`, and say nothing about multiple kubeconfig contexts. The "each question tells you
  which context to switch to" claim appears only in community write-ups. **Drill the
  ssh-to-designated-host discipline as the primary habit**, and treat `use-context` as a
  cheap secondary habit rather than a documented requirement.
- **Editors:** **VSCodium** is explicitly documented. **vim** is strongly implied — the
  instructions give the classic vim workaround: "For security reasons, the **INSERT key is
  prohibited** within the Remote Desktop. Candidates can **Type `i`** to switch into insert
  mode... press **`Esc`** to get out of insert mode." **nano** is **[UNVERIFIED]** — not
  mentioned on any primary page. Plan for vim, know VSCodium exists.
  - **Drill the INSERT-key restriction explicitly.** Muscle memory that reaches for the
    Insert key will silently fail under exam conditions.
- **Copy/paste:** in the Linux terminal `Ctrl+Shift+C` / `Ctrl+Shift+V`; in other remote
  desktop apps `Ctrl+C` / `Ctrl+V`. Worth rehearsing — the split convention costs time.
- **Use `Ctrl+Alt+W`, never `Ctrl+W`** — in the browser-hosted exam, `Ctrl+W` closes the tab.
  Another documented habit-breaker worth drilling alongside the INSERT key.
- **Handy prep trick:** appending **`.md`** to any `docs.linuxfoundation.org` documentation URL
  returns a clean Markdown version of the page — useful while studying the official
  instructions (not needed in-exam).
- **VSCodium is available** from the Applications menu / desktop icon, but **"installing
  extensions in VSCodium is disabled and strictly prohibited during the exam"** — so no
  YAML-linting extension crutch. Plain vim or bare VSCodium only.
- Whether *additional* personal aliases or a custom `.vimrc` may be configured beyond what
  ships pre-provisioned is **[UNVERIFIED]** — not addressed on any primary page.

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

Both are official. The CNCF wording is the more specific and answers the question directly:
**passing the CKA at any point in the past satisfies the prerequisite; expiry is irrelevant.**

### And it now runs the other way too — the CARE program

Effective **2026-06-18**, passing *or* recertifying CKS **automatically reinstates or
extends** the CKA:

> "Passing the Certified Kubernetes Security Specialist (CKS) exam or recertifying your CKS
> will automatically reinstate or extend your Certified Kubernetes Administrator (CKA)
> certification. This applies whether your CKA is still active or has already expired."

The CKA expiration date is realigned to the newly earned/renewed CKS. No conditions or
limits were stated.
Sources: [LF blog](https://training.linuxfoundation.org/blog/expanding-care-passing-cks-can-now-extend-your-cka-certification/),
[CNCF blog, 2026-06-17](https://www.cncf.io/blog/2026/06/17/expanding-care-passing-cks-can-now-extend-your-cka-certification/),
[CARE Program](https://training.linuxfoundation.org/care-program/),
[FAQ](https://docs.linuxfoundation.org/tc-docs/certification/faq-cka-ckad-cks).

### Consequence for the curriculum

The staged ordering **CKAD → CKA → CKS** is confirmed valid and is the *only* legal ordering
for CKS. Critically, **there is no deadline pressure between CKA and CKS**:

- The 2-year CKA clock does **not** constrain when CKS may be attempted.
- A slow, depth-first march through the security phases cannot invalidate the CKS
  eligibility earned by passing CKA.
- Better still, CKS-last is now the *optimal* order financially and administratively: passing
  CKS refreshes the CKA for another 2 years, so the learner does not need to sit a CKA
  retake to stay current. **This is a strong argument for keeping CKS as the final
  checkpoint rather than resequencing.**
- The 12-month *voucher* eligibility window is the only real clock, and it starts at
  purchase — so the curriculum should say "buy the voucher when the relevant phases are
  nearly done", not "buy all three up front".

---

<a id="vouchers"></a>
## 7. What ships with an exam voucher

Per the CKA, CKAD and CKS product pages and the FAQ:

- **Exam simulator by killer.sh — still bundled, unchanged.** "Once enrolled you will
  receive access to an exam simulator, provided by **Killer.sh**... You will have **two
  simulation attempts (36 hours of access for each attempt from the start of activation)**."
  The FAQ confirms: "Candidates will have two attempts (per exam registration). Each attempt
  grants 36 hours of access starting from the time of activation," and names Killer.sh as the
  provider for CKA, CKAD **and** CKS.
- Each simulator session has **17 questions**, with "a different set of questions (17 total)
  in each attempt". (17 is the *simulator's* count — the real exam is 15–20.)
- **One retake**, **12-month eligibility window**, PDF certificate and digital badge.
- **Carve-out worth knowing:** the FAQ states "Exam Simulator access is **not** included in
  CKA-SINGLE, CKAD-SINGLE, CKS-SINGLE Exam Registrations." **[UNVERIFIED]** what exactly the
  `-SINGLE` SKUs are — most plausibly a reduced/retake-only registration rather than the
  standard purchase, but the definition was not found on a primary page. If the learner buys
  a non-standard or discounted SKU, confirm simulator inclusion before relying on it.
- No training course is bundled with a base exam voucher — the product pages list exam
  delivery, the simulator, the retake and the certificate/badge, nothing instructional. LF
  does sell separate exam+training and multi-exam bundle SKUs, but **[UNVERIFIED]** — the
  specific bundle products and their contents were not confirmed against a primary page in
  this pass. Check the LF catalogue at purchase time.
- **[UNVERIFIED]** scheduling mechanics: minimum lead time before an exam can be sat, and the
  forward scheduling window. Not addressed on the FAQ or the pages fetched. The only
  documented clock is the **12-month eligibility window** from purchase.

Sources: [CKA](https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/),
[CKAD](https://training.linuxfoundation.org/certification/certified-kubernetes-application-developer-ckad/),
[CKS](https://training.linuxfoundation.org/certification/certified-kubernetes-security-specialist/),
[FAQ](https://docs.linuxfoundation.org/tc-docs/certification/faq-cka-ckad-cks).

---

<a id="practice"></a>
## 8. Practice resources, with honest quality notes

Ordered by usefulness to this curriculum. **Quality notes are deliberately blunt** —
several widely recommended resources are stale, and one has been discontinued outright.

<a id="currency-test"></a>
### The currency litmus test

Use this to triage *any* resource, including ones not listed here:

> **If it predates ~February 2025 and never mentions Gateway API, Helm/Kustomize as a CKA
> install competency, or CRDs/operators — it is describing the pre-v1.32 CKA and is stale.
> If its lab environment is pinned to Kubernetes ≤ v1.30, discount it further.**

The exam environment is on **v1.35** today, and LF realigns within 4–8 weeks of each minor
release, so a resource two minor versions behind is normal and tolerable; five behind is not.

### Tier 1 — use these

**killer.sh** — <https://killer.sh> · **the single strongest resource, and you already own it.**
- Bundled with every standard voucher: 2 sessions × 36 h, 17 questions each (§7).
- **Currency: good.** killer.sh's own FAQ states its CKA/CKAD/CKS/CNPE environments are at
  **Kubernetes 1.35** — matching the live exam version. ([killer.sh/faq](https://killer.sh/faq),
  vendor-stated)
- **On the "it's harder than the real exam" claim:** this is **community consensus, not an
  official claim.** killer.sh's FAQ explicitly *declines* to quantify difficulty or map
  simulator scores to real scores, saying only that questions are "of the same type" as the
  real exam. **[UNVERIFIED]** as a sourced fact. Treat the harder-than-real reputation as
  useful framing ("train harder than the test") but **do not let a mediocre simulator score
  be read as a fail signal** — that inference is unsupported.
- **Curriculum consequence:** because sessions are only 36 h once activated, **do not
  activate until the phase work is done.** Schedule activation deliberately: session 1 as a
  diagnostic ~2 weeks out, session 2 as a dress rehearsal a few days out.

**`kubernetes.io/docs/tasks/`** — <https://kubernetes.io/docs/tasks/> · **not optional.**
This is the only general-purpose docs site permitted in-exam (§4), so navigation fluency is a
direct speed multiplier, not background reading. Highest-yield sections:
- `/docs/tasks/debug/` — **most important single section**; Troubleshooting is 30% of CKA.
- `/docs/tasks/configure-pod-container/` — limits, securityContexts, probes, volumes (CKAD/CKS)
- `/docs/tasks/run-application/` — Deployments, rolling updates, StatefulSets, HPA (CKAD)
- `/docs/tasks/access-application-cluster/` — Services, port-forward, Ingress
- `/docs/tasks/administer-cluster/` — certs, quotas, node/cluster lifecycle (CKA/CKS)
- `/docs/tasks/configmap-secret/`, `/docs/tasks/inject-data-application/` — CKAD staples
- `/docs/tasks/extend-kubernetes/` — CRDs, admission webhooks; newly relevant given the
  v1.32 CKA CRD/operator additions
- **`kubectl` Cheat Sheet** — <https://kubernetes.io/docs/reference/kubectl/cheatsheet/> — the
  canonical, in-exam-reachable source for nearly every speed tactic in §9.

**`dgkanatsios/CKAD-exercises`** — <https://github.com/dgkanatsios/CKAD-exercises>
- **Actively maintained and current.** 10.1k stars; last commit **2026-08-03** (verified via
  GitHub API — two weeks before this research). The best free CKAD question bank, full stop.

**`bmuschko/ckad-crash-course` / `cka-crash-course` / `cks-crash-course`**
- All three actively maintained (GitHub API: CKAD **2026-05-19**, CKA **2026-04-01**,
  CKS **2025-11-18**). Ben Muschko is a reliable maintainer. CKS is the least fresh of the
  three but still well within tolerance.

### Tier 2 — good, with caveats

**KodeKloud** (Mumshad Mannambeth) — **best structured beginner path, but FLAG the currency.**
- Genuinely strong pedagogy: browser labs (no local cluster needed), practice tests woven
  through lessons, Lightning Labs, and mock exams (CKA 3, CKAD 2, CKS 3).
- **Currency flag:** all three course pages state **"Last Updated: May 26, 2025"** with labs
  being moved to **Kubernetes v1.33** — i.e. ~15 months old and two minor versions behind the
  live exam as of today. Helm/Kustomize sections were added around Jan 2025, so post-v1.32
  competency coverage is *plausibly* intact, but **verify at enrolment rather than trusting
  this note.** It's possible content was updated without the headline date moving.
- Subscription model; free tier exists but full lab access is paid.
- **Curriculum consequence:** valuable for the learner's *first* exposure, but this
  curriculum already builds foundations properly from a homelab — so KodeKloud is optional
  reinforcement, not the spine. Its main unique value is browser labs, which matters less
  here given `factory` exists.

**Killercoda** — <https://killercoda.com/cka> · <https://killercoda.com/ckad> ·
<https://killercoda.com/cks>
- **IMPORTANT — the resource named in the ticket has been discontinued.** The original free
  `killercoda.com/killer-shell-cka` / `killer-shell-ckad` scenario sets by Kim Wüstkamp now
  show *"The Killer Shell CKA scenarios have been replaced with the CKA Scenario Course"*.
  **Any roundup still recommending `killer-shell-*` as the free go-to is pointing at a
  dead end.**
- Replaced by a paid-looking **"Scenario Course"** (`killercoda.com/course/cka`, `/course/ckad`)
  — "complex and supported scenarios with additional videos". **[UNVERIFIED]** pricing.
- Free scenarios still exist at the generic `/cka`, `/ckad` landing pages, but are now a
  **multi-author patchwork** (Chad M. Crowell's "AcingTheCKA", Sachin H R, Alexis Carbillet,
  Omkar Shelke's `cka-mock-practice`) with **no visible version or last-updated metadata**.
  Quality and currency are now inconsistent — **spot-check each scenario, don't trust the set.**
- **[UNVERIFIED]** current CKS free-scenario coverage — `killercoda.com/cks` did not render
  usable scenario content when fetched. Needs a manual check before the CKS phase cites it.

**`walidshaari/Kubernetes-Certified-Administrator`** — <https://github.com/walidshaari/Kubernetes-Certified-Administrator>
- **FLAG — stale.** 4.4k stars but last commit **2025-01-05** (verified via GitHub API):
  ~19 months idle, and it **predates the v1.32 CKA revision entirely.** Its content
  references v1.31 as the standard. Still usable as a topic index / link farm; **not a source
  of truth on current CKA scope.** This is one of the most-recommended repos in older blog
  roundups, so flag it explicitly.
- Companion `walidshaari/Certified-Kubernetes-Security-Specialist` is healthier
  (last commit **2026-03-14**).

**Other exercise repos checked** (GitHub API, for completeness):
- `chadmcrowell/CKA-Exercises` — last commit 2025-10-08; reasonably fresh.
- `David-VTUK/CKA-StudyGuide` — last commit 2025-03-15; borderline, post-dates v1.32 narrowly.
- `stretchcloud/cka-lab-practice` — **last commit 2020-06-10. Six years dead. Avoid.**

**LF's own free training: LFS158 "Introduction to Kubernetes"** —
<https://training.linuxfoundation.org/training/introduction-to-kubernetes/>
- Confirmed **free ($0)**, 17 chapters, 15–20 h, hands-on labs, 90-day access, digital badge.
- Genuinely useful as a zero-cost orientation, though this curriculum's Phase 1 will go
  deeper. **[UNVERIFIED]** which k8s version it targets.
- LF's paid companions are **LFS258** (CKA-aligned), **LFS259** (CKAD), **LFS260** (CKS).

### Tier 3 — avoid

- **Exam dumps / braindump sites** (ExamTopics-style aggregators and similar). **Two
  independent reasons to refuse them:**
  1. **They violate the LF Candidate/Confidentiality Agreement**, which explicitly prohibits
     "using recollections of others or materials from previous administration of any Exam,
     a.k.a. braindump material", with penalties up to **score cancellation, permanent ban,
     and revocation of existing certifications**.
     ([LF Certification & Confidentiality Agreement](https://docs.linuxfoundation.org/tc-docs/certification/lf-cert-agreement))
  2. **They don't even work.** These are hands-on performance exams; static Q&A pairs are a
     category error and are frequently wrong about how tasks actually behave.
- **Any pre-Feb-2025 Udehmy/YouTube "CKA crash course"** — apply the litmus test above.
  **[UNVERIFIED]** — specific course titles were not confirmable in this pass (search budget
  exhausted; review-aggregator pages blocked automated fetch), so no individual course is
  named here. Judge by the test, not by rating: a highly-rated 2023 course still teaches
  etcd backup/restore as a core CKA task and the obsolete one-tab rule.
- **Anything teaching the "one additional browser tab" rule or an alias-bootstrap ritual** —
  both describe an obsolete platform (§4, §5).

### Notable gap

There is **no official LF-built simulator.** The FAQ is explicit that the simulator is
"provided by Killer.sh" — a bundled third-party partner product, not an LF tool. So the
bundled killer.sh sessions are effectively irreplaceable, which reinforces the advice above
about not burning them early.

---

<a id="speed-tactics"></a>
## 9. Speed tactics to drill

Kept deliberately **separate from internals depth** per the standing preference in issue #1.
This is a *timed correctness* skill, drilled as such: 15–20 tasks in 120 minutes is roughly
**6 minutes per task**, and the pass marks (66/66/67%) mean roughly a third of the paper can
be sacrificed — so triage is itself a skill.

### Tier 1 — the load-bearing habits

1. **Never write YAML from scratch.** Generate, then edit:
   - `kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml`
   - `kubectl create deployment web --image=nginx --replicas=3 --dry-run=client -o yaml`
   - `kubectl create job`, `cronjob`, `configmap`, `secret`, `serviceaccount`, `role`,
     `rolebinding`, `clusterrole`, `clusterrolebinding`, `quota`, `ingress`, `service`
   - `kubectl expose` for Services off an existing workload
2. **`export do='--dry-run=client -o yaml'`** so every generator is `k run x --image=y $do`;
   likewise `export now='--force --grace-period=0'`.
   (`k` and completion are already provisioned — see §5 — so this is the one shell nicety
   actually worth adding.) **Sourcing note:** this specific idiom is *community convention*,
   popularised by killer.sh's study tips, **not** documented by LF. Officially documented on
   the [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/) are the
   analogous `kx` (context) and `kn` (namespace) aliases and `-A` as shorthand for
   `--all-namespaces`.
3. **`--dry-run=client` vs `--dry-run=server`** — know the difference; server-side validates
   against admission, which matters for Pod Security Admission tasks on CKS.
4. **Fast deletion:** `kubectl delete pod x --force --grace-period=0` — terminating pods
   burn exam clock.
5. **`kubectl explain <res>.<path> --recursive`** — the fastest in-terminal field lookup, and
   it beats navigating kubernetes.io for a field name. Drill it until it replaces the reflex
   to open the docs browser.
6. **`kubectl -h` / `kubectl <verb> <res> -h`** — the examples block at the bottom of the
   help output is faster than the website for flag syntax.

### Tier 2 — extraction and inspection

7. **`-o jsonpath`** for exact-format answers a task demands written to a file:
   `kubectl get pods -o jsonpath='{.items[*].metadata.name}'`,
   `{range .items[*]}{.metadata.name}{"\t"}{.status.podIP}{"\n"}{end}`
8. **`-o custom-columns=`** and **`--sort-by=`** — e.g.
   `--sort-by=.metadata.creationTimestamp`, `--sort-by=.spec.nodeName`
9. **`yq`** — provided in the exam environment. Fastest way to patch a field in an existing
   manifest without an editor round-trip.
10. `kubectl get <res> -A --show-labels`, `-l key=value`, `-o wide`, `--field-selector`
11. **Debug reflexes:** `kubectl describe` (Events section first), `kubectl logs --previous`,
    `kubectl get events --sort-by=.metadata.creationTimestamp`,
    `kubectl exec -it`, `kubectl debug` (ephemeral containers),
    `kubectl auth can-i --as=system:serviceaccount:ns:sa` for every RBAC task,
    `kubectl top nodes/pods` for the CKA "monitor resource usage" competency.
12. `kubectl cp`, `kubectl port-forward` for connectivity verification.

### Tier 3 — editing and environment discipline

13. **vim under exam conditions:** `:set expandtab shiftwidth=2 tabstop=2` (YAML indentation
    is the #1 self-inflicted failure), `:set paste` before pasting, `:set number`,
    visual-block indent (`Ctrl+V`, `>`), `dd`/`p`, `:wq`.
    **Sourcing note:** community convention, not LF-documented. Whether a persistent
    `.vimrc` may be created in-exam is **[UNVERIFIED]** — assume you type these per-file.
14. **The INSERT key is prohibited** — type `i`. Drill this; it is documented and it breaks
    ingrained habits (§5).
15. **Copy/paste split convention:** `Ctrl+Shift+C/V` in the terminal, `Ctrl+C/V` elsewhere.
16. **Host discipline:** SSH to the designated host for every task, **return to `base`
    afterwards**, no nested SSH. Verify you are where you think you are before mutating
    anything (`hostname`, `kubectl config current-context`).
17. **Namespace discipline:** always pass `-n`, or
    `kubectl config set-context --current --namespace=x`. Silent wrong-namespace work is a
    top scoring loss.
18. **Doc navigation:** rehearse finding things by *searching within* `kubernetes.io/docs`
    only — external search results are forbidden (§4). Know the high-yield task pages cold
    so the docs are a fallback, not the primary path.
19. **Triage:** read every task first, bank the cheap ones, flag and skip the expensive ones.
    A third of the paper is expendable. Never let one hard task eat 20 minutes.

---

<a id="open-items"></a>
## 10. Open items / not verified from a primary source

- Whether the exam uses **multiple kubeconfig contexts** requiring `use-context`. Official
  pages describe designated SSH hosts only. Community sources claim contexts.
- **nano** availability in the exam terminal.
- Whether **custom aliases / a personal `.vimrc`** may be configured beyond the
  pre-provisioned `k` alias and completion.
- Whether any **cooldown period** applies between an exam attempt and its retake (only the
  12-month outer window is documented).
- The exact definition of the **`CKA-SINGLE` / `CKAD-SINGLE` / `CKS-SINGLE`** SKUs that
  exclude simulator access.
- Exact **forward scheduling window** (60 vs 90 days).
- Whether a **CKS v1.35** curriculum document is imminent (the exam environment is already on
  k8s v1.35 while the curriculum PDF is v1.34).
- The "**killer.sh is harder than the real exam**" claim — community consensus only; killer.sh
  itself declines to quantify difficulty.
- **Killercoda CKS** free-scenario coverage, and the pricing of the Killercoda
  "Scenario Course" that replaced the `killer-shell-*` sets.
- Whether **KodeKloud** content has moved past the stated v1.33 / May-2025 headline.
- Which Kubernetes version **LFS158** targets.
- Specific stale Udemy/YouTube courses — not confirmable this pass; the litmus test in §8
  substitutes for a named list.

### Research method note

Domain weights, competency lists and version history were established by **downloading the
curriculum PDFs from `cncf/curriculum` and diffing the extracted text** across versions —
not from prose descriptions of them. Percentages were read off the PDFs and each domain set
was checked to sum to 100%. Mechanics came from `training.linuxfoundation.org` product pages
and `docs.linuxfoundation.org` FAQ/instructions/handbook pages. Repo maintenance status came
from the **GitHub API** (`pushed_at` / latest commit), not from README claims.

One caveat on method: the session's web-search budget was exhausted partway through, so the
practice-resources sweep relied on direct URL fetches rather than discovery search. That
biases §8 toward resources already known by name — **there may be newer good resources not
surfaced here.** Everything actually asserted in §8 was fetched or API-checked; the risk is
omission, not error.
