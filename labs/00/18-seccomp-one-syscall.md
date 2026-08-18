<a id="seccomp-one-syscall"></a>
# A filter that kills on a syscall, not on a permission

**Claim** — seccomp denies by syscall number regardless of privilege, so a process running as root with every capability still dies on a filtered call. Capabilities and seccomp are two independent gates and a program can pass one while failing the other.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root.

**Setup** — a way to install a filter without writing a BPF program by hand. Either `systemd-run --scope -p SystemCallFilter='~mkdir' ...`, or a short C program using `prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, ...)` with `libseccomp` (`apt install libseccomp-dev`). Pick one and say which; both prove the same claim.

**Do**

1. As root, `mkdir /tmp/works`. It succeeds — root, all capabilities, no filter.
2. Install a filter denying exactly `mkdir` with action `SCMP_ACT_KILL`, and run `mkdir /tmp/blocked` under it. Note *how* the process ends.
3. Change the action to `SCMP_ACT_ERRNO(EPERM)` and repeat. Note how the process ends this time.
4. Confirm the process was still fully privileged when it died: `grep Cap /proc/<pid>/status` before the call, or simply run a capability check inside the filtered process first.
5. Read `grep Seccomp /proc/self/status` inside and outside the filtered process.
6. Try to remove the filter from inside the filtered process. Establish that you cannot, and that this is deliberate — a filter is one-way, which is why `no_new_privs` is required to install one unprivileged.

**Observe**

```sh
grep -E '^(Seccomp|Seccomp_filters|NoNewPrivs|CapEff)' /proc/self/status
dmesg | tail                                # the audit line naming the syscall
echo "exit=$?"                              # 159 (128+31, SIGSYS) under KILL
```

**Expect** — under `SCMP_ACT_KILL` the process dies of **`SIGSYS`**, not `EPERM`: there is no error return, no `errno`, and no chance for the program to handle it, which is why a seccomp denial often surfaces as an unexplained crash rather than a permission message. Under `SCMP_ACT_ERRNO` the same call returns `-EPERM` and the program can continue. `CapEff` is unchanged and full throughout — privilege was never the question.

**Write down** — the two actions and their two very different symptoms, plus one line distinguishing the gates: **capabilities ask *may this process do X*; seccomp asks *may this process make call number N*.** A container hardened with one and not the other has closed one of two doors, which is the frame you will attack from in [P10](../../phases/10-security.md).

**Teardown** — the filter dies with the process. `rmdir /tmp/works`. Guest stays up.
