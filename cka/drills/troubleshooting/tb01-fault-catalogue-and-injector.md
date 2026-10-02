<a id="tb01"></a>
# TB1 — Build the fault catalogue and the injector

**Build** · **Pinned** · **60 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Troubleshooting / Harness for TS1–TS19

> **This is the harness, not a drill.** Every TS object's third pass is "the injector plants one and does not say which", and none of them is runnable until this exists. It is also the only object in the plan that was **already built** before the plan was written — `scripts/cka-inject.sh` and `scripts/cka-faults.md` live in `k3ii/factory` — so what remains is understanding why it is shaped the way it is.

> **Hand first, script second.** Each fault was induced by hand and its signature recorded in `describe`, events and logs *before* anything was automated. A fault you have never seen by hand is a fault whose script you cannot debug, and the signatures are the actual deliverable: the script only plants them.

**Do**

1. **Induce each fault class once, by hand, and write down what it looks like** — the exact event, the exact condition, the exact log line. That document is worth more than the injector. `cka-faults.md` is that document, and it has been wrong twice.
2. **Then automate.** Twelve faults, `F01`–`F12`, each with a plant and a revert. `setup`, `inject`, `status`, `revert`, `reveal`, `list`.
3. **Make it reproducible.** Selection is a **seeded shuffle**, so the same seed plants the same faults three weeks later. That property is the whole reason the three-pass rule works across weeks. It is also why **an id is never removed from the catalogue**: deleting one renumbers the shuffle and silently changes what every past seed means. A dead fault gets fixed or neutered in place, never dropped.
4. **Constrain the combinations.** Some faults are not independent. Faults in the `nodeloss` family can appear at most once together, as can `dns`; `silent` allows at most two. Without caps a random draw can plant a cluster that is unrecoverable rather than merely broken.
5. **Make a half-applied injection impossible.** A fault that cannot plant must abort *before* anything else is planted, not halfway through. The script's own header calls a half-applied cluster "worse than no injector at all", and that is correct: it teaches you to distrust the harness, which ends the drill.

**Observe**

```sh
./scripts/cka-inject.sh list
./scripts/cka-inject.sh inject -n 3            # note the seed it prints, and do not look further
./scripts/cka-inject.sh status
./scripts/cka-inject.sh reveal                 # only after the clock stops
./scripts/cka-inject.sh revert
```

Run it over an **interactive** session. It sources the repo's environment, which reaches gpg, and gpg needs a tty; over a non-interactive connection it fails in a way that looks like a cluster problem.

**Done when** — `inject` then `revert` round-trips to a clean cluster, `status` is honest about what is live, and the same seed twice gives the same faults.

**Done in one sitting.** Already done. What is not done is **re-verifying the catalogue after every topology switch**, which is a five-minute job and is the thing that catches dead faults.

**Teardown** — `revert`, then confirm `status` reports clean. Confirm it from the cluster too; the state file and the cluster can disagree.

**Two faults in twelve were dead on arrival, and neither was visible in the script.** One needed a resource the cluster had never had — the lab had no StorageClass at all, so the fault's guard aborted the run every time it was drawn. Both were found by looking at the cluster rather than by reading the script, which is the lesson rather than the anecdote: **the catalogue is a claim about the cluster, and claims about the cluster are checked against the cluster.**

**See also** — **TB2** is the hour this harness exists to make possible.
