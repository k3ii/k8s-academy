# The CKA sprint — 28 Sep to 30 Oct 2026

> **Five weeks, dated.** Unlike a [phase](../phases/), this file expires: it is a schedule for one sitting of one exam, and on 31 Oct it is history.
> **The calendar is the deliverable.** A phase passes when its gate passes, whenever that falls. This passes or fails on **Fri 30 Oct**, so here the dates are not planning information — they are the plan.

| | |
|---|---|
| **Exam** | **Fri 30 Oct 2026**, booked 30 Sep off the Linux Foundation portal. Standard two-attempt entitlement — the retake gets **its own window** and does not inherit the sit-by date, which is **26 Nov 2026 or later**. |
| **Curriculum** | v1.35. Domains, weights, competencies, exam mechanics and the allowed-docs policy all live in [certs](../strands/certs.md#cka) and are **not restated here**. |
| **Topologies** | [`pair`](../strands/lab-topologies.md#pair) (56 of 66 objects) · [`workhorse`](../strands/lab-topologies.md#workhorse) (8) · [`ha`](../strands/lab-topologies.md#ha) (2) |
| **Committed time** | Week 1, four Saturdays, and the exam-week tail. Real hours, deliberately **outside** the 24 h headline figure. |
| **Headline figure** | **24 h** of weeknights across weeks 2–5. Every allocation below refers to this number rather than restating one. |
| **Provenance** | Charted as a wayfinder map in `k3ii/factory` at `thoughts/shared/wayfinder/cka-sprint/`. Thirteen tickets; this file is their output. |

---

<a id="how-to-read"></a>

## 1. How to read this

Two words do the work, and they are **different axes** — the plan is unreadable if they are conflated.

**Tier is size.** A **Reflex** is a 10-minute object worked **three times**: pass 1 in a clean namespace, pass 2 from a namespace someone left messy, pass 3 cold with no notes and the clock visible. All three are **reflex** passes: they measure recall under pressure and presume the material is known. When it is not, an untimed [**pass 0**](learning-pass.md) comes first — see §7. A **Build** is 60 minutes of construction, not speed.

**Band is priority.** **Pinned** runs whatever the diagnostic says. **Core** is what the gap rule allocates against. **Optional** is overshoot — a reservoir for the retake week, not dead weight, and **not scheduled in the first place**.

So "Core" is a band, never a tier. The drop rule acts on band; the calendar acts on tier.

A **night** is a weeknight slot of ~70 min. A **long slot** is a Saturday. A **fortnight** is the allocation period — F1 is weeks 2–3, F2 is weeks 4–5.

**One pass per drill per week, maximum**, so three passes span three weeks. **Week 3 is the last week that can introduce a new Reflex.** A lost night is **dropped, never rescheduled** — it costs that night's pass 1 only, because rescheduling compounds.

---

<a id="calendar"></a>

## 2. The calendar

### Week 1 — Mon 28 Sep to Sat 3 Oct · committed time

`pair` has been up since roughly 3 Sep. **B1 was scheduled for Tue 29 Sep and never ran, because it had nothing to do** — so week 1's build nights are found time, in the week the plan has least of it.

| Date | Session | Topology |
|---|---|---|
| Mon 28 Sep | the map; nothing to run | `pair` |
| Tue 29 Sep | — free (B1 not needed) | `pair` |
| Wed 30 Sep | fault-injector smoke test · policy controller installed and proved | `pair` |
| **Thu 1 Oct** | **Capture the baseline** — done: [`baseline.md`](baseline.md). Sysctls, modules, containerd, the apt pin, the CNI and policy manifests, the rebuild order, and four sharp edges nobody knew about. | `pair` |
| Fri 2 Oct | **Fault-injection night**, light. Plant the diagnostic's faults and sleep on them. | `pair` |
| **Sat 3 Oct** | **The diagnostic** — 13 tasks / 65 min, then 45 min review. One sitting, 110 min. | `pair` |

Thursday is **capture, not rehearsal**. Reading a machine that has been up 27 days contaminates nothing. Rehearsing B1 would contaminate B1 *and* destroy the cluster Saturday needs.

### Week 2 — Mon 5 to Sat 10 Oct · `pair`

| Date | Session |
|---|---|
| **Mon 5 Oct** | **B4** — metrics-server, a Gateway controller, MetalLB via Helm, then one Kustomize overlay. First, because it **unlocks W10, N7 and N13**. |
| Tue 6 Oct | drill night |
| **Wed 7 Oct** | **B5** — install a CRD and its operator, create a CR, watch it reconcile |
| Thu 8 Oct | drill night |
| Fri 9 Oct | drill night |
| **Sat 10 Oct** | **The `ha` day, ~6.6 h.** See [§3](#topology). |
| Sun 11 Oct | **Release valve.** Costs nothing — Sunday is neither a night nor a long slot. |

### Week 3 — Mon 12 to Sat 17 Oct

| Date | Session | Topology |
|---|---|---|
| **Mon 12 Oct** | **B2** — `kubeadm upgrade`, control plane then node, drain and uncordon around it | `pair` |
| Tue 13 Oct | drill night | `pair` |
| Wed 14 Oct | drill night — **last night a new Reflex may be introduced** | `pair` |
| **Thu 15 Oct** | switch in (~25 min), then passes 1 & 2: **W1, W2, W3, TS2, TS3** | **`workhorse`** |
| **Fri 16 Oct** | passes 1 & 2 continue; **TS4 last** | **`workhorse`** |
| **Sat 17 Oct** | **Simulator 1 — CKA-A.** Activate ~09:00. | lab idle |
| Sun 18 Oct | slack from the 36-hour window. Nothing is planned into it. | — |

### Week 4 — Mon 19 to Sat 24 Oct

**Mon 19 Oct is week 4**, not week 3 — t06's night count and its fortnight definition both only balance that way.

| Date | Session | Topology |
|---|---|---|
| **Mon 19 Oct** | pass 3 of the `workhorse` block (~30 min), **TS4 last** — it destroys usable cluster state — then the ~25 min switch back. The night is owned by the switch. | `workhorse` → `pair` |
| **Tue 20 Oct** | drill night — **the first night the re-weight can act on** | `pair` |
| **Wed 21 Oct** | **TB2** — the broken-cluster hour. Five faults at once; read all five before touching anything, bank the cheap ones, flag and skip the expensive one, report what you deliberately did not fix. | `pair` |
| Thu 22 Oct | drill night | `pair` |
| Fri 23 Oct | drill night | `pair` |
| **Sat 24 Oct** | **Simulator 2 — CKA-B.** Different question set from CKA-A. | lab idle |

### Week 5 — Mon 26 to Fri 30 Oct

| Date | Session |
|---|---|
| **Mon 26 – Wed 28 Oct** | **Taper.** Pass 3 only, no new drills. Order set by sim 2. |
| **Thu 29 Oct** | **Off — and the last date to doubt.** Reservation changes lock 24 h out, and a no-show voids **both** attempts. Any doubt about sitting must be resolved today. |
| **Fri 30 Oct** | **The exam.** |

### The fourteen Pinned objects, and where they sit

The calendar above names Build nights but writes most weeknights as "drill
night", and that is deliberate: **which Core drills run on a given night is
decided on 3 Oct, not today**, by the gap rule in [§4](#diagnostic). What *is*
fixed is Pinned — it runs whatever the diagnostic says — so all fourteen are
placed here.

**Seven Builds.** Each is 60 minutes of construction, not speed; B3 is four hours.

| | Drill | When | Topology |
|---|---|---|---|
| **B1** | Prepare the infrastructure, `kubeadm init`, join a worker — from nothing | Sat 10 Oct, evening | `pair` |
| **B2** | `kubeadm upgrade`, control plane then node, drain and uncordon around it | Mon 12 Oct | `pair` |
| **B3** | Three stacked control planes; lose one, keep quorum | Sat 10 Oct (4 h) | `ha` |
| **B4** | metrics-server, a Gateway controller and MetalLB via Helm, then one Kustomize overlay | Mon 5 Oct | `pair` |
| **B5** | A CRD and its operator; create a CR, watch it reconcile | Wed 7 Oct | `pair` |
| **TB1** | The fault catalogue and the injector | **week 1 — built** | `pair` |
| **TB2** | The broken-cluster hour: five faults at once | Wed 21 Oct | `pair` |

**TB1 is already done.** It was the week-1 work: the injector exists, both of its
policy checks were fixed, and it was smoke-tested on 30 Sep. Fri 2 Oct's
fault-injection night is its last exercise before the diagnostic consumes it.

**Seven Pinned Reflex objects**, each worked three times like any other Reflex:

| | Drill | Topology | First pass no earlier than |
|---|---|---|---|
| **A7** | Name the CNI, CSI and CRI in play; find each config on disk and its socket | `pair` | week 2 |
| **N13** | A minimal Gateway plus HTTPRoute | `pair` | **after B4** (Mon 5 Oct) |
| **W10** | HPA on CPU against metrics-server, under real load | `pair` | **after B4** |
| **TS3** | Cordon, drain, uncordon against a PDB and a DaemonSet — make `drain` refuse, say why, then get it through | **`workhorse`** | Thu 15 Oct |
| **TS12** | The whole `logs` flag surface in one pass | `pair` | week 2 |
| **TS15** | A Service with no endpoints: selector, pod labels, readiness, `targetPort` — and say which of the four it was | `pair` | week 2 |
| **TS16** | One pod resolves a name, another does not: `resolv.conf`, `ndots`, the search list, `dnsPolicy` | `pair` | week 2 |

**N13 and W10 are why B4 goes first.** Neither is provable without
metrics-server and a Gateway controller, so a Monday-5-Oct B4 buys two Pinned
drills their full three weeks of passes. **TS3 is the only Pinned Reflex that is
not on `pair`**, which is why the `workhorse` window must carry it.

Everything else on a drill night is Core, allocated by the gap rule, one pass
per drill per week, and **no new Reflex may be introduced after Wed 14 Oct**.

---

<a id="topology"></a>

## 3. The topology schedule

**One cluster at a time**, and it is enforced by the code rather than by discipline: `topology` is a single string over a single state file, so a switch is **one apply**, and the destroy falls out of the plan.

| Date | Command | Destroys |
|---|---|---|
| Sat 10 Oct, morning | `just tofu labs apply -var 'topology=ha'` | `pair` (2 nodes) |
| Sat 10 Oct, evening | `just tofu labs apply -var 'topology=pair'` | `ha` (3 nodes) |
| Thu 15 Oct | `just tofu labs apply -var 'topology=workhorse'` | `pair` |
| Mon 19 Oct | `just tofu labs apply -var 'topology=pair'` | `workhorse` |

Four applies. **Zero in week 1** — the cluster is already up — and **zero on either simulator Saturday**, because killer.sh is hosted and does not compete for the lab.

**A switch is always paid for inside its own window's slot, never the next one's.** Otherwise a Saturday's teardown silently eats a Monday night from inside the 24 h figure.

There is **no composite bring-up recipe**. Each apply above is followed by hand:

1. `just tofu labs apply -var 'topology=<name>'` — clones the VMs
2. `just gate <vm>` per node — `apply` returns when the *clone* completes, not when the guest is reachable
3. `just play` — the Ansible baseline
4. `kubeadm` by hand — **this part is the drill**, not plumbing

**The lab pins Kubernetes v1.35 from Sat 10 onward.** `pair` runs v1.37.0, held by `apt-mark` against the `pkgs.k8s.io/core:/stable:/v1.37` repo ([baseline §2](baseline.md#node)), and three things make that the wrong base: `kubectl debug`'s default profile silently changed `legacy` → `general` and `legacy` was removed (30% domain, in no changelog); `RelaxedServiceNameValidation` makes the lab *accept* Service names the exam *rejects* (20% domain, and permissive-lab/strict-exam is the bad direction); and **B2 is patch-only at a 1.37 base**, because v1.38 does not exist. kubeadm 1.37 refuses to go below 1.36, so the pin costs a rebuild — which every topology pays anyway.

**Each build applies the policy controller.** `kube-network-policies` v1.1.2, pinned by hand because the manifest published at that tag still references the v1.1.1 image — the build whose random nfqueue packet loss v1.1.2 exists to fix. Without it Flannel enforces no NetworkPolicy, and **N1–N4 and TS17 stop being provable**. It is plumbing, not a drill: v1.32 removed *"choose an appropriate CNI plugin"* from the curriculum.

### Sat 10 Oct, hour by hour

| | |
|---|---|
| morning | apply `ha` (most of an hour — three nodes from nothing) |
| | **B3** — three stacked control planes, lose one, keep quorum. **4 h, not shortened.** |
| | **TS9** rides B3's cluster (~15 min). It buys no topology switch of its own. |
| evening | apply `pair` — **and this is B1**, a from-nothing stand-up that has to happen regardless |

**This is the plan's single point of failure.** `factory` manages no sysctls, so `kubeadm init` preflight rests entirely on B1's first clause — and Sat 10 is the first time that clause is ever exercised. Week 1 had four nights of slack behind a failure; Sat 10 has Sunday and a rebuild obligation.

**Contingency.** Sun 11 is the valve. **If `pair` is not serving by Sunday evening, stop debugging and rebuild from [the captured baseline](baseline.md#rebuild)** — week 3's Mon–Wed become rebuild nights, and the drills they lose come off the top of [the drop order](#what-does-not-run).

---

<a id="diagnostic"></a>

## 4. The diagnostic, and the two re-weights

**Sat 3 Oct.** 13 tasks, 65 minutes, then 45 minutes of review. Scored pass/fail per task — blunt, and the only scoring you can do honestly on yourself.

It feeds `share(domain) = exam_weight × (1 − score)`, which allocates against **drill-night minutes, per fortnight**:

- **Floors first.** Troubleshooting 70 min; every other domain below `solid` 35 min. That is 210 min of a fortnight's ~490 — about 43%.
- **The gap rule distributes the rest**, dropping Core from the lightest domain first.

There is **no sub-competency floor inside Troubleshooting**. The six Pinned objects there are one already, and a named drill is a better floor than a time quota.

**The rule fires twice**: once on the diagnostic, and once more at the week-3 boundary on simulator 1. The second firing divides **fortnight 2's drill-night minutes** — floors take 210, leaving roughly 245 to move. The lever is more modest than it sounds: about four hours, in one shot. Fortnight 2's pool is slightly smaller than the raw night count suggests, because **Mon 19 is not a full drill night** — it carries ~30 min of pass 3 and then the switch back.

A domain tested by **fewer than two questions is no-signal**: its allocation carries forward unchanged. An untested domain is **not** scored 1.0 — that would zero its share at exactly the moment there is least reason to.

---

<a id="simulators"></a>

## 5. The simulators

Two killer.sh sessions, **Sat 17 Oct (CKA-A)** and **Sat 24 Oct (CKA-B)** — different question sets, not a re-test.

**The day's shape.** Activate ~09:00. One strict 120-minute run, countdown honoured, no notes. Stop, reveal, ~2 h review. Then, if the day still has room, restart and re-run only the failed questions. **Sunday is slack, not budget.**

**The 36-hour window is wall-clock from activation and runs overnight. Restarts are unlimited and work persists. The 120-minute countdown is advisory** — at zero it *unlocks* solutions and the score rather than ending anything. That window is this plan's release valve; **neither simulator moves.**

**killer.sh returns no per-domain breakdown.** Scoring is per-sub-task and the vendor deliberately suppresses percentages, so the domain shape the re-weight needs is **manufactured by hand during the review**: assign each of the 17 questions **one primary domain — the one the fix lives in** — never split a question across two, and give ties to Troubleshooting. Budget ~15 min inside the review slot.

**The simulator is deliberately harder than the exam and publishes no score mapping.** Circulating pass targets are folklore. So:

- **Sim 1's tripwire asks whether the plan's shape is wrong.** If no domain separates from the others, the diagnosis is breadth without depth — not a misallocation between domains, because the gap rule cannot act on a flat profile. The response is to **move the cut line deeper**: cut more Core and give the survivors their three passes.
- **Sim 2's tripwire asks whether to sit, and the answer is yes.** It is deliberately low — under 50% of sub-tasks inside 120 minutes — and even then the answer is to sit on 30 Oct and treat attempt 1 as the real diagnostic. The retake has its own window and does not inherit the sit-by date. **A no-show voids both attempts**, so this is never resolved by not turning up.
- **What sim 2 decides is what the taper contains.** It may **reorder the pass-3 queue freely**, and may swap **at most two** pass-3 slots for a re-run covering a sim-2 failure. It may not add drills, extend into the Thursday, or introduce material never drilled. Two is the cap because the taper is three nights of ~70 min; beyond that it stops being a taper.

**Not used, deliberately:** appending `/content` to the activation URL reveals the questions and solutions without activating a session. Recorded so that *not* using it is a decision rather than an oversight.

---

<a id="what-does-not-run"></a>

## 6. What does not run

**Of 66 objects, about 43 run and about 22 do not.** This is the plan's least comfortable number and it is stated here rather than discovered in week 4.

The inventory is a **menu, not a schedule** — deliberately ~30% larger than the hours can absorb. The hours are real: 18 nights × 70 min = **21.0 h** of deliverable pool, of which four are Build nights, leaving ~912 drill-night minutes against **1225 minutes of demand**. The overshoot is ~313 min ≈ **12 Core drills**.

**The 10 Optional objects are never scheduled.** They are the retake reservoir.

**Three Core drills are cut now, at zero coverage cost**, because each is the same object as a Troubleshooting drill seen from the other side:

| Cut | Covered by | Why it costs nothing |
|---|---|---|
| **N5** — ClusterIP and endpoints; break the selector | **TS15** (Pinned) | The unlabelled counterpart. TS15 runs regardless of the diagnostic. |
| **N3** — egress policy with the DNS carve-out | **TS17** | Same object, fault side. |
| **N9** — edit the Corefile, make CoreDNS reload | **TS8** | *"The same object seen as fault and as feature."* |

**The remaining ~9 are named on 3 Oct, not today** — they depend on `weight × (1 − score)`, and the scores do not exist yet. Naming them now would either ignore the diagnostic or merely restate the exam weights.

What ships instead is **the drop order**, so that Saturday night's arithmetic is mechanical rather than a fresh judgement under time pressure: **drop Core from the lightest domain first, down to each domain's floor, and never below it.** Pinned is immune by definition.

---

<a id="handoff"></a>

## 7. Handoff

This file is a schedule. It is **not** the drills, and five things remain:

- **The drill files themselves.** 66 objects are specified by id, title, tier, band, domain and topology in the map's inventory tickets. They now have a home — [the drill menu](drills/) — and **56 of 66 bodies are written: every Pinned and every Core object**. Nothing in §2's calendar is blocked on unwritten work at any point. The **10 that remain are all Optional**, and the gap rule decides whether any of them is ever needed; writing them before the diagnostic would be writing for a reader who may never arrive. The menu lists all 66 either way, so what is missing is visible rather than merely absent.
- **~~`cka/check-drills.py`~~ — written.** [The script](check-drills.py) enforces the four checks t05 specified, and the tree is green from its first file as intended. It found four real violations on its first run, including two in these very drills. Run it by hand: `python3 cka/check-drills.py`.
- **One dependency the calendar does not satisfy: there is no Ingress controller.** Measured on the `pair` cluster while authoring the drills — `kubectl get ingressclass` returns nothing, no ingress controller Deployment exists, and there are **0 Gateway API CRDs**. [B4](drills/architecture/b04-helm-and-kustomize.md) installs metrics-server, a **Gateway** controller and MetalLB, which covers [N13](drills/networking/n13-gateway-and-httproute.md) and [N7](drills/networking/n07-loadbalancer-metallb.md) — but nothing in this plan installs an **Ingress** controller, and [N12](drills/networking/n12-ingress-host-and-path.md) needs one. N12 is written with that gap stated and treats the install as a one-time fixture outside its ten minutes. **The call is whether B4 absorbs it** — one more `helm install` in a build that is already full — **or whether N12 keeps carrying it.** Either way it must happen before N12 runs.
- **Nothing in the tree teaches a concept cold, and that is a hole.** All 66 objects are reflex exercises; the slowest pass still carries a clock. Found on 2 Oct by running [TS12](drills/troubleshooting/ts12-the-whole-logs-flag-surface.md) pass 1 against `pair` — the eight commands ran, nothing was understood, and the drill body turned out to be wrong twice besides. [**Pass 0**](learning-pass.md) is the patch: untimed, done when you can explain it rather than when it runs, and written for **one drill at a time** only once the diagnostic shows its domain scored low. It adds no calendar slots — it is taken off the front of a weak domain's allocation. TS12's write-up is there as the worked example and the template.
- **Three drills are authored once and presented twice.** N5/TS15, N3/TS17 and N9/TS8 are the same objects from opposite sides. Whoever writes them should write them together even though [§6](#what-does-not-run) runs only one side of each. **All three pairs are done** — N5/TS15, N3/TS17 and N9/TS8.

**`cka/` stays unpublished until the exam is passed.** It is outside `check-anchors.py` by construction — the script globs only `strands/`, `phases/` and `labs/` — so nothing here can turn the repo's gate red. Publishing is one commit afterwards: a `docs/cka` symlink, a line in `docs/.pages`, and the pointer from [P8](../phases/08-storage.md)'s CKA drill block that is deliberately not added yet, because it would render dead on the site while `cka/` is unpublished.

**CI wiring is out of scope.** `check-anchors.py` is not in CI either — the repo's only workflow builds the site — so `check-drills.py` is run by hand, as `check-anchors.py` is. Standing up the repo's first real CI during a five-week exam sprint is the wrong week for it.
