<a id="learning-pass"></a>
# Pass 0, the learning pass — and a worked example

> **Found by running a drill, 2 Oct.** The tree's 66 objects are all **reflex** exercises: they assume the material is already known and measure how fast it comes back. [The plan](plan.md#how-to-read) defines three passes and the slowest of them still runs with a clock and a target. **Nothing in the tree teaches a concept cold.** That is a hole, not a design choice, and this file is the patch.

---

<a id="pass-0"></a>
## 1. What pass 0 is

**Pass 0 is untimed.** That is the whole of it. Every other pass measures recall under some amount of pressure; pass 0 removes the pressure so that there is something to recall later. A clock on a learning pass teaches you to type fast and understand nothing, which is what happened on TS12's first run.

| | Pass 0 | Pass 1 | Pass 2 | Pass 3 |
|---|---|---|---|---|
| **Clock** | none | target, help open | target, messy namespace | visible, cold |
| **Help** | encouraged | allowed | allowed | none |
| **Done when** | you can **explain** it | it runs | it runs at 80% | it runs at 50% |

**Done when you can explain it to someone else** — not when the commands succeed. Commands succeed by copying. The test is whether you can say *why the flag exists* and *what you would see if the thing were broken*, with the terminal closed.

<a id="which-drills"></a>
### Which drills get one

**Not all 66.** Writing 66 explainers on spec would be the same mistake in the other direction — most of them would teach you things you already know. The selection rule is the one already in the plan:

> Run pass 0 on a drill when its **domain scored low** on [the diagnostic](plan.md#diagnostic) or on a simulator. A low score means the material is not there, and drilling material that is not there is just typing.

So the diagnostic does double duty. It already decides *how many minutes* a domain gets; it now also decides *whether those minutes start at pass 0 or at pass 1*. No new machinery, and nothing is written before it is known to be needed.

<a id="shape"></a>
### The shape of a pass-0 write-up

Four parts, in this order. §2 below is the worked example and the template at once.

1. **The fixture, in plain words.** What exists, how many of it, and which part was rigged to misbehave. A learner cannot reason about output from a system they cannot picture.
2. **The problem the commands solve.** One sentence, then a table mapping each command to *the question a person would actually ask* — never to its flag name.
3. **The one that matters.** Every drill has a centre of gravity: one or two items that carry real weight while the rest are convenience. Name it, and say what it would cost you not to know it.
4. **What a failure looks like.** The output you would see if the thing were genuinely broken, so the clean case has something to contrast against.

---

<a id="ts12"></a>
## 2. Worked example — TS12, container output streams

The write-up for [TS12](drills/troubleshooting/ts12-the-whole-logs-flag-surface.md), produced after running its pass 1 and finding the pass unhelpful.

<a id="ts12-fixture"></a>
### The fixture

A **Deployment** named `web` with **2 replicas** — two identical pods, so there is more than one place to read from.

Each pod runs **three containers**, which is what makes reading logs awkward in the first place:

- **`seed`** — an **init container**. Init containers run to completion *before* the normal containers start, then exit. They exist for setup work. A pod stuck in `Init:` is stuck here, and this is the only place it explains itself.
- **`app`** — the main container, rigged to **fail on its first start**, printing `app: config checksum mismatch, refusing to start` and exiting non-zero. Kubernetes restarts it; the second instance succeeds and prints a line every second.
- **`car`** — a quiet sidecar printing `car: flush ok` every seven seconds.

So: two pods, three containers each, one of which has already died once. Artificial, deliberately — it is the smallest shape in which all eight reads are *necessary* rather than decorative.

<a id="ts12-problem"></a>
### The problem

`kubectl logs` prints what a container wrote to standard output. That is all it does. Every flag on the list exists to answer one question: **which output, from which container, from when?**

| What you type | The question a person is actually asking |
|---|---|
| `k logs <pod>` | "Just show me." With three containers that is ambiguous, so `kubectl` picks the first and says so: `Defaulted container "app" out of: app, car, seed (init)`. **Read that line.** |
| `k logs <pod> -c seed` | "Show me the **init** container." Where a pod that never started explains itself. |
| `k logs <pod> -c app --previous` | **"Show me the instance that died."** |
| `--since=10m` / `--since-time=<RFC3339>` | "Only recently." Relative, then absolute. |
| `--tail=50` | "Only the last 50 lines." The default is *everything*. |
| `--timestamps` | "When did each line happen?" Off by default. |
| `-l app=web --all-containers --prefix` | "Every container in **every** pod carrying this label." |
| `k logs deploy/web` | "Just show me the Deployment" — which quietly reads **one** pod of however many exist, naming it in a line above the output. |

<a id="ts12-centre"></a>
### The one that matters

Everything above is convenience except **`--previous`**.

When a container crashes, Kubernetes does not repair it — it starts a **fresh** one in its place. The new container's output is empty, because it has only just begun. The dead container's output is still retained, but **only the most recent dead one**, and only until the pod itself is deleted.

This is why a crash-looping pod seems to say nothing. Plain `k logs` reads the newborn. `--previous` reads the corpse, and the corpse is the one that knows what went wrong:

```sh
k logs <pod> -c app --previous
# app: config checksum mismatch, refusing to start
```

That line appears in **no other command** — not in `kubectl describe`, not in `k logs` without the flag. It is retained exactly once and it is lost when the pod is recreated, which is why `kubectl delete pod` on something that is crash-looping is usually the worst available move: it destroys the evidence and the symptom returns unchanged.

<a id="ts12-broken"></a>
### What failure looks like

Four outputs worth recognising, because each one means something different:

| What you see | What it means |
|---|---|
| `Error from server (BadRequest): previous terminated container … not found` | The container has **not** restarted. Nothing died, so there is no corpse. `--previous` is the wrong tool here, and `RESTARTS 0` would have told you first. |
| Output is **empty**, exit code 0 | The process is writing to a **file** rather than to stdout. No flag will fix this; see **TS13**. |
| `Defaulted container …`, then content you did not expect | You read the wrong container. The warning told you which one; it went to stderr and scrolled past. |
| `Found 2 pods, using pod/web-…` | You asked a fleet-wide question and got a **single-pod** answer. `-l` is the fleet-wide read; `deploy/x` is not. |

<a id="ts12-say"></a>
### Done when

With the terminal closed, you can say: why a crash-looping pod appears to have no logs; what `--previous` reads and when it has nothing to read; and why deleting the pod makes the problem harder rather than easier.

---

<a id="next"></a>
## 3. What this changes

**One line in the plan, and nothing else.** Pass 0 is not a new tier and does not consume calendar slots of its own — it is time taken off the front of a domain's allocation when the diagnostic says the material is not there. A domain that scores badly spends its first night understanding and its remaining nights drilling, rather than three nights drilling something it does not know.

**Write-ups live in [`pass0/`](pass0/).** TS12's stays here, in §2, because it is the template as much as a write-up. Written so far:

| Pass 0 | Prerequisite for | Written |
|---|---|---|
| [Deployment, ReplicaSet, Pod: what is actually connected to what](pass0/w05-w06-the-object-chain.md) | **W5**, **W6** | 2 Oct |
| [Manifests: `spec` against `status`, `explain`, and never typing YAML](pass0/manifests-spec-status-and-explain.md) | **every drill that writes YAML** | 2 Oct |
| [The API surface: `api-resources`, scope, and finding things fast](pass0/the-api-surface.md) | **mechanics under every drill** | 4 Oct |
| [kubeconfig and contexts: which cluster are you talking to?](pass0/kubeconfig-and-contexts.md) | **mechanics under every drill** | 5 Oct |
| [Reading a crash: `CrashLoopBackOff`, exit codes, and why `exec` fails](pass0/reading-a-crash.md) | **TS11**, **TS12**, **TS13** | 5 Oct |
| [Static pods and the control plane: what runs where, and who starts it](pass0/static-pods-and-the-control-plane.md) | **TS05**, **TS06** | 5 Oct |
| [Node health: who decides a node is `Ready`](pass0/node-health-and-who-decides-ready.md) | **TS01**, **TS02**, **TS04** | 5 Oct |

> **The last three were chosen by the rule rather than by guesswork.** The first four were picked on a hunch about what a beginner would need. The [diagnostic](plan.md#diagnostic) of 5 Oct was abandoned after four tasks, but it tested Troubleshooting three times and returned **1 of 3** — *cold*, under 50%. All three write-ups come straight out of the tasks that were failed, which is exactly what [§1](#which-drills) says is supposed to happen: a low score sends the domain to pass 0 before it drills.

**The drill bodies are not rewritten.** Fifty-six of them are correct as reflex objects and stay that way. A pass-0 write-up is a **separate** document, written for one drill, at the point the diagnostic shows it is needed — and never before.
