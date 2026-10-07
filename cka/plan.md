# The CKA sprint — 28 Sep to 30 Oct 2026

> **Five weeks, dated.** Unlike a [phase](../phases/), this file expires: it is a schedule for one sitting of one exam, and on 31 Oct it is history.
> **The calendar is the deliverable.** A phase passes when its gate passes, whenever that falls. This passes or fails on **Fri 30 Oct**, so here the dates are not planning information — they are the plan.

> ### Revised 7 Oct — read this before the calendar
>
> **The plan was written for a reader who already knew Kubernetes and needed to get fast. That reader did not turn up.** The diagnostic was attempted on 5 Oct, abandoned after 4 of 13 tasks, and the one domain it scored returned **1 of 3 — cold**. Three separate nights then went on untimed explanation rather than drills, because the drills were unusable without it.
>
> Three things change, and nothing else:
>
> 1. **The diagnostic is cancelled, not postponed.** [§4](#diagnostic) now measures on **Simulator 1, Sat 17 Oct**. Until then, allocation is by raw exam weight — the correct prior when you have no information, and close to what the gap rule outputs when every domain scores cold anyway.
> 2. **[Pass 0](learning-pass.md) leads a domain instead of following it.** A new domain opens with an untimed explainer, and the drills come after. See [§1](#how-to-read).
> 3. **The `ha` day is cut** — B3 and TS9 with it. [§3](#topology) says why.
>
> **The date is not changed and is not in doubt until Thu 29 Oct.** If the two simulators say otherwise, the sitting moves and the retake window runs to 26 Nov or later. See [§5](#simulators).

| | |
|---|---|
| **Exam** | **Fri 30 Oct 2026**, booked 30 Sep off the Linux Foundation portal. Standard two-attempt entitlement — the retake gets **its own window** and does not inherit the sit-by date, which is **26 Nov 2026 or later**. |
| **Curriculum** | v1.35. Domains, weights, competencies, exam mechanics and the allowed-docs policy all live in [certs](../strands/certs.md#cka) and are **not restated here**. |
| **Topologies** | [`pair`](../strands/lab-topologies.md#pair) (56 of 66 objects) · [`workhorse`](../strands/lab-topologies.md#workhorse) (8) · ~~[`ha`](../strands/lab-topologies.md#ha)~~ (2, **cut 7 Oct** — see [§3](#topology)) |
| **Committed time** | Week 1, three Saturdays, and the exam-week tail. Real hours, deliberately **outside** the headline figure. |
| **Headline figure** | **~15.25 h** of weeknights from 7 Oct — 14 nights × 70 min. Was 24 h across weeks 2–5; five nights went to the diagnostic and its repair. Every allocation below refers to this number rather than restating one. |
| **Provenance** | Charted as a wayfinder map in `k3ii/factory` at `thoughts/shared/wayfinder/cka-sprint/`. Thirteen tickets; this file is their output. |

---

<a id="how-to-read"></a>

## 1. How to read this

Two words do the work, and they are **different axes** — the plan is unreadable if they are conflated.

**Tier is size.** A **Reflex** is a 10-minute object worked **three times**: pass 1 in a clean namespace, pass 2 from a namespace someone left messy, pass 3 cold with no notes and the clock visible. All three are **reflex** passes: they measure recall under pressure and presume the material is known. A **Build** is 60 minutes of construction, not speed.

**[Pass 0](learning-pass.md) comes before all of them, and it is untimed.** It is done when you can explain the thing with the terminal closed — not when the commands run. Commands run by copying. This was the 5 Oct lesson and it is now the default rather than a patch: **a domain you have not studied opens at pass 0, not at pass 1.**

So a weeknight from 7 Oct has a fixed shape, and the calendar below writes it as a **read-then-drill night**:

| | | |
|---|---|---|
| **~15 min** | read one pass-0 document | no typing |
| **~50 min** | the drills it was written for, at pass 1 | clock running, help open |

Once a domain's pass-0 documents are read, its nights are ordinary drill nights and the 15 minutes goes back into the pool.

**Band is priority.** **Pinned** runs whatever [the measurement](#measurement) says. **Core** is what the gap rule allocates against. **Optional** is overshoot — a reservoir for the retake week, not dead weight, and **not scheduled in the first place**.

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
| ~~Sat 3 Oct~~ | **Did not run.** The diagnostic slipped to Sun 5 Oct. | `pair` |

Thursday is **capture, not rehearsal**. Reading a machine that has been up 27 days contaminates nothing. Rehearsing B1 would contaminate B1 *and* destroy the cluster Saturday needs.

**What happened instead, 2–6 Oct.** Recorded because the calendar below is a response to it, not a revision of it.

| | |
|---|---|
| 2 Oct | [TS12](drills/troubleshooting/ts12-the-whole-logs-flag-surface.md) pass 1 was run as a warm-up. The eight commands ran; nothing was understood; the drill body turned out to be wrong twice. **This is where [pass 0](learning-pass.md) came from.** |
| 2–5 Oct | Five pass-0 documents written and worked through live: the object chain, manifests, the API surface, kubeconfig, and the workspace. |
| 5 Oct | **The diagnostic, abandoned after four tasks.** Two Architecture tasks were found dead beforehand and repaired. **T1 ✓, T2 ✗, T3 ✗**; T4 and the remaining nine were never reached. |
| 5 Oct | Three more pass-0 documents written out of the three tasks: [reading a crash](pass0/reading-a-crash.md), [static pods](pass0/static-pods-and-the-control-plane.md), [node health](pass0/node-health-and-who-decides-ready.md). |

**The run produced one finding worth more than the score.** T1 (`kubelet` stopped) and T3 (a control-plane static pod broken) were planted together, and T3's fault **suppressed T1's symptom**: the node's `Ready` condition is written by the node lifecycle controller inside `kube-controller-manager`, so with that component down the node reported a 32-day-old `Ready` while its kubelet was dead. Six minutes went on a task that could not present. **Faults mask faults**, and a `status` field is a cached verdict rather than a probe.

### Week 2 — Mon 5 to Sat 10 Oct · `pair`

**Mon 5 and Tue 6 went to the diagnostic and its write-ups. B4 and B5 did not run.** The week restarts on Wednesday.

| Date | Session |
|---|---|
| ~~Mon 5 Oct~~ | B4 did not run — the night went to the diagnostic |
| ~~Tue 6 Oct~~ | did not run |
| **Wed 7 Oct** | **read-then-drill** · [node health](pass0/node-health-and-who-decides-ready.md) → **TS1** pass 1 |
| **Thu 8 Oct** | **read-then-drill** · [reading a crash](pass0/reading-a-crash.md) → **TS11**, **TS12** pass 1 |
| **Fri 9 Oct** | **read-then-drill** · [static pods](pass0/static-pods-and-the-control-plane.md) → **TS5**, **TS6** pass 1 |
| **Sat 10 Oct** | **B1 — rebuild `pair` from nothing, pinned to v1.35.** ~3 h, long slot. See [§3](#topology). |
| Sun 11 Oct | **Release valve.** Costs nothing — Sunday is neither a night nor a long slot. |

**Week 2's three nights are Troubleshooting and only Troubleshooting.** It is 30% of the exam, it is where the score is, and its three pass-0 documents are already written — so these nights need nothing authored first. **B4 moves to Mon 12 Oct**, which is the last date that still buys W10 and N13 two passes each.

### Week 3 — Mon 12 to Sat 17 Oct

| Date | Session | Topology |
|---|---|---|
| **Mon 12 Oct** | **B4** — metrics-server, a Gateway controller, MetalLB via Helm, then one Kustomize overlay. **Unlocks W10, N7 and N13**, and must not slip again. | `pair` |
| **Tue 13 Oct** | **read-then-drill** · Workloads pass 0 → **W5**, **W6** pass 1 | `pair` |
| **Wed 14 Oct** | **read-then-drill** · Storage pass 0 → **S1**, **S2** pass 1. **Last night a new Reflex may be introduced.** | `pair` |
| **Thu 15 Oct** | switch in (~25 min), then passes 1 & 2: **W1, W2, W3, TS2, TS3** | **`workhorse`** |
| **Fri 16 Oct** | passes 1 & 2 continue; **TS4 last** | **`workhorse`** |
| **Sat 17 Oct** | **Simulator 1 — CKA-A. This is now the plan's only real measurement.** Activate ~09:00. | lab idle |
| Sun 18 Oct | slack from the 36-hour window. Nothing is planned into it. | — |

**The `workhorse` block is the next thing to cut if week 3 slips.** It costs ~50 minutes of switching across Thu 15 and Mon 19 to buy five drills, one of them Pinned (TS3). If Mon–Wed overrun, drop the switch, run TS3 on `pair` with its PDB clause weakened, and give Thu and Fri back as ordinary nights.

### Week 4 — Mon 19 to Sat 24 Oct

**Mon 19 Oct is week 4**, not week 3 — t06's night count and its fortnight definition both only balance that way.

| Date | Session | Topology |
|---|---|---|
| **Mon 19 Oct** | pass 3 of the `workhorse` block (~30 min), **TS4 last** — it destroys usable cluster state — then the ~25 min switch back. The night is owned by the switch. | `workhorse` → `pair` |
| **Tue 20 Oct** | drill night — **the first night sim 1's re-weight can act on** | `pair` |
| **Wed 21 Oct** | **TB2** — the broken-cluster hour. Five faults at once; read all five before touching anything, bank the cheap ones, flag and skip the expensive one, report what you deliberately did not fix. | `pair` |
| Thu 22 Oct | drill night | `pair` |
| Fri 23 Oct | drill night | `pair` |
| **Sat 24 Oct** | **Simulator 2 — CKA-B.** Different question set from CKA-A. | lab idle |

**B2 — `kubeadm upgrade` — has no slot left and is cut.** It was Mon 12 Oct; B4 took that night when it slipped out of week 2. At a v1.35 base after Sat 10 it would be rehearsable, but Architecture already carries B1, C1-shaped RBAC work and the bootstrap-token material, and three hours is not available. **Reinstate it only if sim 1 scores Architecture well enough to free the night.**

### Week 5 — Mon 26 to Fri 30 Oct

| Date | Session |
|---|---|
| **Mon 26 – Wed 28 Oct** | **Taper.** Pass 3 only, no new drills. Order set by sim 2. |
| **Thu 29 Oct** | **Off — and the last date to doubt.** Reservation changes lock 24 h out, and a no-show voids **both** attempts. Any doubt about sitting must be resolved today. |
| **Fri 30 Oct** | **The exam.** |

### The fourteen Pinned objects, and where they sit

The calendar above names Build nights but writes most weeknights as "drill
night", and that is deliberate: **which Core drills run on a given night is
decided on 17 Oct, not today**, by the gap rule in [§4](#measurement). What *is*
fixed is Pinned — it runs whatever the measurement says — so all fourteen are
placed here.

**Seven Builds, of which four run.** Each is 60 minutes of construction, not speed.

| | Drill | When | Topology |
|---|---|---|---|
| **B1** | Prepare the infrastructure, `kubeadm init`, join a worker — from nothing | **Sat 10 Oct**, ~3 h | `pair` |
| **B4** | metrics-server, a Gateway controller and MetalLB via Helm, then one Kustomize overlay | **Mon 12 Oct** | `pair` |
| **TB1** | The fault catalogue and the injector | **week 1 — built** | `pair` |
| **TB2** | The broken-cluster hour: five faults at once | **Wed 21 Oct** | `pair` |
| ~~**B2**~~ | `kubeadm upgrade` | **cut** — B4 took its night | — |
| ~~**B3**~~ | Three stacked control planes; lose one, keep quorum | **cut** with the `ha` day | — |
| ~~**B5**~~ | A CRD and its operator | **cut** — no slot survived | — |

**Three Builds cut is the largest single change in this revision**, and it is stated here rather than discovered in week 4. B2 and B5 are reinstatable if sim 1 frees a night; **B3 is not**, because the topology it needs is gone.

**TB1 is already done.** It was the week-1 work: the injector exists, both of its
policy checks were fixed, and it was smoke-tested on 30 Sep. Fri 2 Oct's
fault-injection night is its last exercise before the diagnostic consumes it.

**Seven Pinned Reflex objects**, each worked three times like any other Reflex. **Pinned outranks everything, including a bad sim-1 score** — that is what the band means:

| | Drill | Topology | First pass no earlier than |
|---|---|---|---|
| **A7** | Name the CNI, CSI and CRI in play; find each config on disk and its socket | `pair` | week 2 |
| **N13** | A minimal Gateway plus HTTPRoute | `pair` | **after B4** (Mon 12 Oct) |
| **W10** | HPA on CPU against metrics-server, under real load | `pair` | **after B4** (Mon 12 Oct) |
| **TS3** | Cordon, drain, uncordon against a PDB and a DaemonSet — make `drain` refuse, say why, then get it through | **`workhorse`** | Thu 15 Oct |
| **TS12** | The whole `logs` flag surface in one pass | `pair` | **Thu 8 Oct** — pass 1 done 2 Oct, re-run after [reading a crash](pass0/reading-a-crash.md) |
| **TS15** | A Service with no endpoints: selector, pod labels, readiness, `targetPort` — and say which of the four it was | `pair` | week 2 |
| **TS16** | One pod resolves a name, another does not: `resolv.conf`, `ndots`, the search list, `dnsPolicy` | `pair` | week 2 |

**N13 and W10 are why B4 cannot slip again.** Neither is provable without
metrics-server and a Gateway controller. At Mon 12 Oct they get **two** passes
rather than three; one more week of slippage and they get one, at which point
they stop being Reflex objects in any meaningful sense. **TS3 is the only Pinned
Reflex that is not on `pair`**, which is why the `workhorse` window must carry it.

Everything else on a drill night is Core, allocated by exam weight until 17 Oct
and by the gap rule after it, one pass per drill per week, and **no new Reflex
may be introduced after Wed 14 Oct**.

---

<a id="topology"></a>

## 3. The topology schedule

**One cluster at a time**, and it is enforced by the code rather than by discipline: `topology` is a single string over a single state file, so a switch is **one apply**, and the destroy falls out of the plan.

| Date | Command | Destroys |
|---|---|---|
| Sat 10 Oct | `just tofu labs apply -var 'topology=pair'` | `pair` (the v1.37 build) |
| Thu 15 Oct | `just tofu labs apply -var 'topology=workhorse'` | `pair` |
| Mon 19 Oct | `just tofu labs apply -var 'topology=pair'` | `workhorse` |

Three applies, down from four. **Zero in week 1** — the cluster is already up — and **zero on either simulator Saturday**, because killer.sh is hosted and does not compete for the lab.

**The `ha` day is cut, and with it B3 and TS9.** Three reasons, in order of weight:

1. **It is the wrong material at the wrong time.** Stacked etcd quorum is four hours spent on the rarest thing in the curriculum, by someone who learnt what a ReplicaSet was on 2 Oct. The same four hours buys eight Reflex passes in domains worth 30% and 25%.
2. **It is this plan's single point of failure**, by [the old §3](#topology)'s own admission, and it is now also the week the lab cannot afford to lose. Every night from 7 Oct needs a working `pair`.
3. **It costs one apply and one teardown**, both inside the slot that would otherwise be B1.

**B3 and TS9 go to the Optional reservoir** — the retake material, not deleted. Reinstating them needs a free Saturday, and there is exactly one: Sun 18 Oct, which [§5](#simulators) protects as slack and this revision does not touch.

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
| morning | apply `pair` — the VMs clone from nothing (~1 h, including `just gate` per node and `just play`) |
| | **B1** — prepare the infrastructure, `kubeadm init`, join the worker, **pinned to v1.35**. ~2 h. |
| | re-apply the policy controller; prove a NetworkPolicy still drops |
| afternoon | stop. The day has one job. |

**This is still the plan's single point of failure**, but it is now a smaller one: one topology instead of two, and a whole afternoon of slack behind it. `factory` manages no sysctls, so `kubeadm init` preflight rests entirely on B1's first clause — and Sat 10 is the first time that clause is ever exercised.

**B1 is also the v1.35 pin**, which is the second reason the day survives the cut: three behaviours in [§3](#topology) below differ between the lab's v1.37 and the exam's v1.35, one of them inside the 30% domain.

**Contingency.** Sun 11 is the valve. **If `pair` is not serving by Sunday evening, stop debugging and rebuild from [the captured baseline](baseline.md#rebuild)** — week 3's Mon–Wed become rebuild nights, and the drills they lose come off the top of [the drop order](#what-does-not-run). B4 is the first casualty, and with it W10 and N13.

---

<a id="diagnostic"></a>
<a id="measurement"></a>

## 4. The measurement, and the one re-weight

> **The home-made diagnostic is cancelled.** It was attempted on 5 Oct and abandoned after four tasks. Its post-mortem is in [week 1](#calendar); what follows replaces it.

**It was the wrong instrument, and the reason generalises.** A pass/fail test across thirteen tasks only tells you something when the domains *separate*. A reader who scores cold in all five learns nothing from it except that they scored cold — which one night of honest work already shows — while paying 110 minutes and a good deal of discouragement for the privilege. **Measure when measurement can discriminate.** Before that, allocate on the prior.

### Until 17 Oct — allocate by exam weight

The prior *is* the exam's own weighting, and nothing better is available:

| Domain | Share | Reading |
|---|---|---|
| Troubleshooting | **30%** | three pass-0 documents written; week 2 is entirely this |
| Cluster Architecture | **25%** | B1 and B4 carry most of it |
| Servicing and Networking | **20%** | needs a pass 0 written; see [§7](#handoff) |
| Workloads and Scheduling | **15%** | pass 0 partly written — the object chain |
| Storage | **10%** | needs a pass 0 written |

This is also, near enough, what `share = exam_weight × (1 − score)` returns when every score is the same — the gap rule degenerates to the weights, which is the correct behaviour and a small point in its favour.

**One real datum survives the abandoned run:** Troubleshooting, 1 of 3 — *cold*. It changes nothing, because Troubleshooting is already the largest share and already has the floor.

### From 17 Oct — the gap rule, fired once

**Simulator 1 (Sat 17 Oct) is now the plan's only real measurement.** It is a proper CKA practice exam, externally scored, 17 questions over 120 minutes — strictly better evidence than thirteen tasks written by the person sitting them. [§5](#simulators) covers how a per-domain shape is manufactured from a tool that publishes none.

It feeds `share(domain) = exam_weight × (1 − score)`, allocating against **fortnight 2's drill-night minutes** — Mon 19 Oct to Fri 23 Oct, plus the taper:

- **Floors first.** Troubleshooting 70 min; every other domain below `solid` 35 min.
- **The gap rule distributes the rest**, dropping Core from the lightest domain first.

There is **no sub-competency floor inside Troubleshooting**. The six Pinned objects there are one already, and a named drill is a better floor than a time quota.

**The rule now fires once rather than twice**, which makes the single firing load-bearing. Fortnight 2's pool is smaller than the raw night count suggests, because **Mon 19 is not a full drill night** — it carries ~30 min of pass 3 and then the switch back. Call it ~245 movable minutes: about four hours, in one shot.

A domain tested by **fewer than two questions is no-signal**: its allocation carries forward unchanged at the exam weight. An untested domain is **not** scored 1.0 — that would zero its share at exactly the moment there is least reason to.

**Sim 2 (Sat 24 Oct) does not re-weight.** It decides the taper's contents and whether to sit, and nothing else — see [§5](#simulators).

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

**Of 66 objects, about 30 run and about 36 do not.** That is down from 43 in the pre-revision plan, and it is the price of the five nights lost to the diagnostic and its repair. It is stated here rather than discovered in week 4.

The inventory is a **menu, not a schedule** — deliberately larger than the hours can absorb. The hours are now these:

| | Nights | Minutes |
|---|---|---|
| Wed 7 – Fri 9 Oct | 3 | 210 |
| Tue 13 – Fri 16 Oct | 4, one eaten ~25 min by the `workhorse` switch | 255 |
| Mon 19 – Fri 23 Oct | 4, one of them ~40% after the switch back | 240 |
| Mon 26 – Wed 28 Oct | 3, **taper — pass 3 only, no new material** | 210 |
| **Total** | **14** | **915** |

Take off **~120 min of pass-0 reading** across the eight nights that open new domains, and the drillable pool is **~795 minutes**. A Reflex costs ~30 minutes for its three passes, so the pool buys about **26 Reflex objects of 59**, plus the four surviving Builds.

**The taper's 210 minutes cannot introduce anything**, so new material has to fit in ~585 minutes — roughly **19 Reflex objects reaching pass 1 before Fri 23 Oct**. Seven of those are Pinned and spoken for. **Twelve Core slots is the real budget**, and the gap rule on 17 Oct is choosing among them.

**The 10 Optional objects are never scheduled.** They are the retake reservoir, and **B3, TS9, B2 and B5 join them** under this revision — written, cut, and available if there is a second sitting.

**Three Core drills are cut now, at zero coverage cost**, because each is the same object as a Troubleshooting drill seen from the other side:

| Cut | Covered by | Why it costs nothing |
|---|---|---|
| **N5** — ClusterIP and endpoints; break the selector | **TS15** (Pinned) | The unlabelled counterpart. TS15 runs regardless of the measurement. |
| **N3** — egress policy with the DNS carve-out | **TS17** | Same object, fault side. |
| **N9** — edit the Corefile, make CoreDNS reload | **TS8** | *"The same object seen as fault and as feature."* |

**The rest are named on 17 Oct, not today** — they depend on `weight × (1 − score)`, and the scores do not exist yet. Naming them now would merely restate the exam weights, which [§4](#measurement) already does openly as the interim allocation.

What ships instead is **the drop order**, so that Saturday night's arithmetic is mechanical rather than a fresh judgement under time pressure: **drop Core from the lightest domain first, down to each domain's floor, and never below it.** Pinned is immune by definition.

---

<a id="handoff"></a>

## 7. Handoff

This file is a schedule. It is **not** the drills, and four things remain:

- **The drill files themselves.** 66 objects are specified by id, title, tier, band, domain and topology in the map's inventory tickets. They now have a home — [the drill menu](drills/) — and **56 of 66 bodies are written: every Pinned and every Core object**. Nothing in §2's calendar is blocked on unwritten work at any point. The **10 that remain are all Optional**, and the gap rule decides whether any of them is ever needed; writing them before sim 1 would be writing for a reader who may never arrive. The menu lists all 66 either way, so what is missing is visible rather than merely absent.
- **~~`cka/check-drills.py`~~ — written.** [The script](check-drills.py) enforces the four checks t05 specified, and the tree is green from its first file as intended. It found four real violations on its first run, including two in these very drills. Run it by hand: `python3 cka/check-drills.py`.
- **One dependency the calendar does not satisfy: there is no Ingress controller.** *(B4 moved from Mon 5 to Mon 12 Oct in this revision; the call below is unchanged and now more urgent, since B4 has one fewer week of slack behind it.)* Measured on the `pair` cluster while authoring the drills — `kubectl get ingressclass` returns nothing, no ingress controller Deployment exists, and there are **0 Gateway API CRDs**. [B4](drills/architecture/b04-helm-and-kustomize.md) installs metrics-server, a **Gateway** controller and MetalLB, which covers [N13](drills/networking/n13-gateway-and-httproute.md) and [N7](drills/networking/n07-loadbalancer-metallb.md) — but nothing in this plan installs an **Ingress** controller, and [N12](drills/networking/n12-ingress-host-and-path.md) needs one. N12 is written with that gap stated and treats the install as a one-time fixture outside its ten minutes. **The call is whether B4 absorbs it** — one more `helm install` in a build that is already full — **or whether N12 keeps carrying it.** Either way it must happen before N12 runs.
- **~~Nothing in the tree teaches a concept cold~~ — [pass 0](learning-pass.md) exists and now leads.** Found on 2 Oct by running [TS12](drills/troubleshooting/ts12-the-whole-logs-flag-surface.md) pass 1 against `pair`: the eight commands ran, nothing was understood, and the drill body turned out to be wrong twice besides. **Seven documents are written** — the object chain, manifests, the API surface, kubeconfig, the workspace, and the three from the abandoned diagnostic. As of this revision pass 0 is no longer a patch applied to a weak domain; it is [the first 15 minutes of any night that opens a new one](#how-to-read).
- **Two pass-0 documents are not written and have dates.** Networking's is needed for **Tue 13 Oct** and Storage's for **Wed 14 Oct**, which are the only two nights in the calendar whose material does not yet exist. Nothing else in [§2](#calendar) is blocked on unwritten work. Write them one at a time, in [the four-part shape](learning-pass.md#shape), and not before the week they are needed — the three that came out of the diagnostic are better than the four that were guessed, because they were written against something that actually happened.
- **~~Three drills are authored once and presented twice~~ — done.** N5/TS15, N3/TS17 and N9/TS8 are the same objects from opposite sides, written together, with [§6](#what-does-not-run) running only one side of each.

### What this revision decided, and what it left open

**Decided, 7 Oct:** the diagnostic is cancelled and sim 1 is the measurement; pass 0 leads a domain rather than patching it; the `ha` day, B3 and TS9 are cut; B2 and B5 are cut; B4 moves to Mon 12 Oct; B1 moves to Sat 10 Oct and carries the v1.35 pin.

**Left open, deliberately:**

| | Decide by |
|---|---|
| Whether B4 absorbs the Ingress controller install, or N12 keeps carrying it | Mon 12 Oct |
| Whether the `workhorse` switch is worth ~50 min for five drills | Wed 14 Oct |
| Whether to reinstate B2 or B5 if sim 1 frees a night | Sat 17 Oct |
| **Whether to sit on 30 Oct** | **Thu 29 Oct** — see [§5](#simulators) |

**The last row is the one that matters and it is not decided here.** The exam is 23 days out as this is written, the reader is three weeks newer to Kubernetes than the plan assumed, and a no-show voids both attempts while a reschedule does not. **Sit unless Thursday 29 Oct says otherwise**, and let the two simulators — not a bad week — be what says it.

**`cka/` stays unpublished until the exam is passed.** It is outside `check-anchors.py` by construction — the script globs only `strands/`, `phases/` and `labs/` — so nothing here can turn the repo's gate red. Publishing is one commit afterwards: a `docs/cka` symlink, a line in `docs/.pages`, and the pointer from [P8](../phases/08-storage.md)'s CKA drill block that is deliberately not added yet, because it would render dead on the site while `cka/` is unpublished.

**CI wiring is out of scope.** `check-anchors.py` is not in CI either — the repo's only workflow builds the site — so `check-drills.py` is run by hand, as `check-anchors.py` is. Standing up the repo's first real CI during a five-week exam sprint is the wrong week for it.
