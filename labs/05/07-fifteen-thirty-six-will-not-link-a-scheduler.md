<a id="fifteen-thirty-six-will-not-link-a-scheduler"></a>
# The OOM you were promised, produced on purpose — then 2560MB

**Claim** — [`forge` at its standing 1536MB](../../strands/build-mechanics.md#forge) cannot link `cmd/kube-scheduler`; the failure is an OOM kill during the **link step**, it is reported by the Go toolchain as `signal: killed` with no other explanation, and raising the guest to 2560MB fixes it. This is [one of only two moments in the curriculum where the lab's own hardware changes](../../strands/build-mechanics.md#p5-split), and it is a step, not a footnote.

**Rests on** — nothing before it in this phase. It comes first in the build half because every remaining module in it compiles something, and an unexplained kill in the middle of a build is a bad first lesson about a scheduler.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued and **idle**. The change is to [`forge`](../../strands/lab-topologies.md#build-guest), which is never part of a topology, so the cluster is untouched by any of this.

**Setup**

```sh
ssh zain@10.10.10.125
free -m                       # record: this is the "before" number
cd ~/src/kubernetes
```

**Do**

1. **Produce the failure.** Build the scheduler cold, and watch memory while it runs. Two sessions:

   ```sh
   # session 1
   cd ~/src/kubernetes && time go build -o /tmp/kube-scheduler ./cmd/kube-scheduler
   ```

   ```sh
   # session 2
   while :; do free -m | awk '/Mem:/{print strftime("%T"), $3, $7}'; sleep 2; done
   ```

2. When it dies, read the two pieces of evidence, because the toolchain's own message is useless on its own:

   ```sh
   dmesg -T | grep -iE 'killed process|out of memory' | tail -5
   journalctl -k --since '-5 min' | grep -i 'oom' | tail
   ```

   Write down which process the kernel killed. It will not be `go`.

3. **Confirm it is the link and not the compile.** Re-run the build; the compiled packages are cached now, so the second attempt goes almost directly to linking:

   ```sh
   go build -o /tmp/kube-scheduler ./cmd/kube-scheduler
   ```

   If this dies faster than step 1 did, that is the confirmation: the peak is one process, at the end.

4. **Check the two levers that do not work**, so you stop reaching for them later. [The strand measured both](../../strands/build-mechanics.md#measurements); reproduce one of them yourself rather than taking it on trust:

   ```sh
   go build -p 1 -o /tmp/kube-scheduler ./cmd/kube-scheduler
   GOGC=50 go build -o /tmp/kube-scheduler ./cmd/kube-scheduler
   ```

5. **Resize the guest.** This runs on the Proxmox host, not on `forge` and not on macOS — [`ssh hopper` is mandatory for the same reason it is mandatory for a provision](../../strands/lab-topologies.md#provision):

   ```sh
   ssh hopper
   qm list | grep -i forge          # note the VMID
   qm shutdown <forge-vmid> && sleep 20 && qm status <forge-vmid>
   qm set <forge-vmid> --memory 2560
   qm start <forge-vmid>
   ```

   A memory change on a stopped guest needs no hotplug configuration and no argument about whether ballooning applied it, which is why this is a shutdown and a start rather than a live edit.

6. **Verify and re-link:**

   ```sh
   ssh zain@10.10.10.125 'free -m; cd ~/src/kubernetes && time go build -o /tmp/kube-scheduler ./cmd/kube-scheduler && ls -lh /tmp/kube-scheduler'
   ```

**Observe** — the peak `used` figure from your `free -m` loop on the successful run, and the size of the resulting binary.

**Expect** — a kill on the first attempt and a clean link on the second, with a peak somewhere near the figure [the strand records for a warm link with DWARF kept](../../strands/build-mechanics.md#measurements). Expect `-p 1` to change nothing at all, because the link is a single process and parallelism was never the variable. Expect `GOGC=50` to shave a little and not enough — and if you try `GOGC=25`, expect it to be *worse*, which is the counter-intuitive measurement worth reproducing once in your life.

Expect the binary to be large — over a hundred megabytes with debug information in it. `-ldflags="-s -w"` would cut both the binary and the link peak substantially, and it is worth measuring, but **do not adopt it for this phase**: [module 5.3](12-one-pod-through-schedule-one.md) wants symbols.

**Write down** — the kernel's OOM line, the peak on the successful link, and one sentence stating what memory a linker actually needs it for. Then write the revert down as a task with a name: `forge` goes back to 1536MB at [exercise 33](33-forge-back-down-and-workhorse-up.md), before `workhorse` comes up, and if it does not, the ceiling arithmetic in that exercise fails by exactly 1024MB.

**Footprint note — this exercise is the phase's hardware change and the reason the phase is split in two.** With `forge` at 2560MB and `pair` at 5.0GB the standing cost is **7.5GB against the [9.5GB ceiling](../../strands/lab-topologies.md#ceiling)** — 2.0GB of margin, and that is the shape of every exercise from here to [32](32-the-lease-changes-hands.md). It is exactly why [the split exists](../../strands/build-mechanics.md#p5-split): `workhorse` at 7.0GB plus a 2560MB `forge` would be 9.5GB with **no** margin, so nothing in this phase compiles while `workhorse` is up.

Disk deserves a note here too, because on this phase it is tighter than RAM. The k/k build cache and module cache grow fast; check with `df -h /` and `du -sh ~/.cache/go-build ~/go/pkg/mod` now, so that the number in [exercise 33](33-forge-back-down-and-workhorse-up.md) has a baseline to be compared against.

**Teardown** — `rm /tmp/kube-scheduler`; keep the build cache, since the next four exercises benefit from it. **The topology stays**, and **`forge` stays at 2560MB** until exercise 33 — that is the state the rest of the build half assumes.
