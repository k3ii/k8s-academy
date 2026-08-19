<a id="12c5-the-leak-in-the-golden-path"></a>
# 12.C5 — one leak left in the golden path on purpose, and the time until a fresh consumer hits it

**Claim** — hand a consumer (a teammate, or your own past self) the golden path with exactly one abstraction leak left in — a value the abstraction *should* hide but doesn't, or a Kubernetes primitive that shows through — and time how long until they hit it. The leak is the lesson: a platform's abstractions fail at the worst moment, and the number you measure is the evidence for [the capstone critique](18-the-platform-and-its-critique.md). This drill produces data about your own platform, not a pass/fail.

**Rests on** — [the golden path](07-a-golden-path-with-no-portal.md), which must exist and mostly work for a single leak to stand out; and [the scaffolder contrast](08-backstage-read-never-installed.md), which named the failure classes a platform hides versus exposes.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), continued.

**Read** — [the drill's chaos-table row](../../phases/12-gitops-platform.md#chaos) and [the manual-drills standard](../../strands/chaos.md#manual-drills). By hand: the fault is a deliberately imperfect abstraction, and the observable is a human's time-to-collision with it.

**Do** — leave one leak in, then run a fresh consumer through the path:

```sh
# choose one leak: e.g. the CRD requires the developer to name the storageClass,
# or a failed provision surfaces a raw Crossplane composition error, or the port must
# match an undocumented Service the template hides.
# Then: hand the template repo to a fresh consumer and start a timer.
# Measure: minutes from "clone" to "they ask a question the abstraction should have answered."
```

**Observe** — the consumer moving smoothly until the leak, then stalling on a detail the platform promised to hide — a `storageClass` they should never have needed to name, a raw controller error with no translation, a Kubernetes object surfacing in what was meant to be a Kubernetes-free interface. The time-to-leak is the measurement; the *nature* of the leak is the catalogue entry.

**Expect** — a concrete failure with a stopwatch on it, not an opinion that platforms leak. If the consumer never hit the leak, either the leak was too obscure to matter (a finding) or your abstraction is tighter than you thought (also a finding) — record which.

**Write down** — the time-to-leak for a fresh consumer, the exact detail that leaked, and which class it was (a value that should have been hidden, a primitive that showed through, an error that wasn't translated). This is the failure-mode evidence [the critique](18-the-platform-and-its-critique.md) is built from.

**Teardown** — patch the leak or leave it documented for the capstone; delete the fresh consumer's app instance. **The topology stays.**
