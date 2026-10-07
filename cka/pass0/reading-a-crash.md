<a id="reading-a-crash"></a>
# Pass 0 — reading a crash: `CrashLoopBackOff`, exit codes, and why `exec` fails

**Pass 0** · **untimed** · [`pair`](../../strands/lab-topologies.md#pair) · Troubleshooting · prerequisite for **TS11**, **TS12**, **TS13**

> **Worked live on 5 Oct**, from the [diagnostic](../plan.md#diagnostic)'s task T2, which was failed inside its box. Written in the shape [pass 0](../learning-pass.md#shape) specifies. Everything below came out of that run rather than out of recollection.
>
> **Done when** you can say what `CrashLoopBackOff` actually names, which three questions `describe` answers that `logs` cannot, and why installing the missing program is never the fix.

---

<a id="fixture"></a>
## 1. The fixture

A **Deployment** named `ledger` in namespace `storefront`, **1 replica**. One container, named `ledger`, running the image `python:3.12-alpine`. Its command is:

```sh
exec /usr/local/bin/ledger --config /etc/ledger/ledger.conf
```

`python:3.12-alpine` is a Python runtime. **There is no `ledger` binary inside it and there never was.** So the shell starts, tries to replace itself with a program that does not exist, fails, and the container is over in a few milliseconds.

That is the entire fault. It produced 680 restarts over five days and three separate dead ends before it produced an answer, which is why it is worth a write-up.

---

<a id="backoff"></a>
## 2. What `CrashLoopBackOff` is

**It is not a state the container is in. It is a timer the kubelet is sitting in.**

The loop runs like this:

1. The kubelet starts the container.
2. The container exits.
3. The kubelet waits, then starts it again.
4. Each failure doubles the wait — roughly 10s, 20s, 40s, up to a **5-minute ceiling**.

`CrashLoopBackOff` is the name for **step 3**: the gap. At the moment you look at the pod, most of the time there is **no container running at all** — it is between attempts. Three consequences follow directly, and all three bit during T2:

- **`kubectl exec` cannot work.** `exec` attaches to a live process. There isn't one.
- **`kubectl logs` without `--previous` usually reads nothing,** because the current container either doesn't exist yet or has just been born.
- **The restart count is the clock.** `RESTARTS 680` is not severity — it is *age*. A pod crashing every 5 minutes for two days looks far worse than one crashing every second for ten minutes, and is not.

**The opposite error is equally common.** A container that exits **successfully** also gets restarted, because the default `restartPolicy` is `Always`. A pod running `echo hello` crash-loops forever with exit code 0 and no error anywhere. That is not a bug; it is a Deployment being asked to hold a job.

---

<a id="three-questions"></a>
## 3. The three questions, and which command answers each

`kubectl logs` answers exactly one of them. This is why reaching for `logs` first — which is the instinct — leaves two thirds of the picture missing.

| The question | Where the answer is |
|---|---|
| **Did it ever start?** | `k describe pod` → `State` and `Last State`. A container that never started has no logs to read, and no flag will produce any. |
| **What did it say on the way out?** | `k logs <pod> --previous` → the dead instance's output. See [TS12](../drills/troubleshooting/ts12-the-whole-logs-flag-surface.md). |
| **How did it die?** | `k describe pod` → `Last State: Terminated`, with a `Reason` and an **`Exit Code`**. |

So the order is **`describe` first, `logs` second** — the reverse of what feels natural. `describe` tells you *whether there is anything to read* and *what kind of death it was*, and the kind of death narrows the cause before you have read a single log line.

```sh
k describe pod -n storefront ledger-5f5dbc88-rm78w
```

The block to find:

```
    State:          Waiting
      Reason:       CrashLoopBackOff
    Last State:     Terminated
      Reason:       Error
      Exit Code:    127
      Started:      ...
      Finished:     ...
    Restart Count:  680
```

---

<a id="centre"></a>
## 4. The one that matters — the exit code

**The exit code sorts the cause into one of four families before you look at anything else.** Learn these four and most crashes are half-solved from `describe` alone.

| Exit code | `Reason` | What it means | Where to look next |
|---|---|---|---|
| **0** | `Completed` | The process finished its work and exited cleanly — and was restarted anyway, because `restartPolicy: Always`. | The **workload kind** is wrong. This is a Job, not a Deployment. |
| **1** (or any small number) | `Error` | **The program ran and rejected something.** Bad config, missing file, unreachable dependency, flag it doesn't accept. | **`logs --previous`.** The program spoke on its way out; this is the one family where the logs carry the answer. |
| **137** | `OOMKilled` | Killed by the kernel: `128 + 9` (SIGKILL). It exceeded its memory **limit**. | `describe` → `Limits:`. Not the logs — the process was shot, it did not get to say anything. See [TS11](../drills/troubleshooting/ts11-oomkilled.md). |
| **126 / 127** | `Error` | **The program never ran.** `127` is "command not found"; `126` is "found but not executable". | The **image**. The thing you asked for is not in it, or the path is wrong. |

T2 was a **127**, and that family has a property the others don't: **the logs tell you the truth in one line and it still misleads you.**

```
/bin/sh: exec: line 0: /usr/local/bin/ledger: not found
```

The natural reading is *"I need to install `ledger`."* That is the wrong instinct and unlearning it is the point of this document.

---

<a id="immutable"></a>
## 5. Why you can never install the missing thing

**A container image is a complete, immutable filesystem.** The container is not a small machine you log into and maintain — it is a fresh instance built from the image, every single time, and it is thrown away when it exits.

So even supposing you could get a shell into a crashing container, anything you installed would be destroyed by the next restart, seconds later. There is no persistent place to put it.

Which leaves exactly **two** possible causes, and therefore exactly two possible fixes, both of them edits to the **Pod spec**:

1. **The image is wrong.** You asked for `python:3.12-alpine` when the thing you need lives in a different image, or a different tag of the same one. Fix the `image:` field.
2. **The command is wrong.** The image is right and you are calling a path that is not in it — a typo, a binary that moved between versions, a command copied from a different image. Fix the `command:` / `args:` field.

Telling the two apart is one command:

```sh
k run probe --rm -it --image=python:3.12-alpine --restart=Never -- sh
# then, inside:  ls /usr/local/bin/
```

Start the same image **by hand with a shell instead of the broken command**, and look. If `ledger` is absent, the image is wrong. If it is present under another name or path, the command is wrong. Either way you have measured it rather than guessed, and the pod you are debugging is untouched.

> **This is the general move.** When a container will not start, run its image interactively with `sh` as the command. You get the exact filesystem the container sees, with none of the crash.

---

<a id="failure"></a>
## 6. What failure looks like

The errors from the T2 run, each of which means something specific:

| What you see | What it means |
|---|---|
| `error: unable to upgrade connection: container not found ("ledger")` | **`exec` on a crash-looping pod.** There is no running container to attach to. This error means your diagnosis is already half-made: the pod is genuinely down, not merely unhealthy. |
| `container python:3.12-alpine is not valid for pod … out of: ledger` | **`-c` takes a container *name*, not an image.** Names come from the Pod spec, and `kubectl` printed the valid list for you — `out of: ledger`. Read those lists; they are free. |
| `Error from server (BadRequest): previous terminated container … not found` | Nothing has restarted yet. `RESTARTS 0` in `k get pods` would have told you first. |
| `Back-off restarting failed container` in the events | The kubelet narrating step 3. Informational — it names the symptom, never the cause. |
| Pod stuck in `Init:CrashLoopBackOff` | The failure is in an **init container**, which runs to completion before the main ones start. `k logs <pod> -c <init-name>` — the main container has not been created and has nothing to say. |
| `ImagePullBackOff` / `ErrImagePull` | **Not this problem at all.** The container never got as far as starting; the image could not be fetched. Wrong name, wrong tag, or missing registry credentials. No exit code, because no process ran. |

---

<a id="say"></a>
## 7. Done when

With the terminal closed, you can say:

- what `CrashLoopBackOff` names, and why `RESTARTS` is a measure of age rather than severity;
- why `describe` comes before `logs`, and the three things `describe` tells you that `logs` cannot;
- what exit codes **0**, **1**, **127** and **137** each point at;
- why "install the missing program" is never available, and what the two real fixes are;
- how to inspect an image's filesystem without the crash.

**See also** — [TS12](../drills/troubleshooting/ts12-the-whole-logs-flag-surface.md) for the full `logs` surface, [TS11](../drills/troubleshooting/ts11-oomkilled.md) for the `137` family in depth, and [TS13](../drills/troubleshooting/ts13-logs-empty-app-writes-a-file.md) for the case where the container is healthy and the logs are empty anyway.
