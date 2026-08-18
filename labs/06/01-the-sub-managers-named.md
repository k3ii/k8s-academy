<a id="the-sub-managers-named"></a>
# The kubelet has no main loop, so start with the list of things it is instead

**Artifact** — a one-page inventory of the kubelet's sub-managers: for each one, the package that owns it, the one sentence of what it is responsible for, and **whether this phase reads it, watches it, or never touches it**. Written before any `pkg/kubelet/` file is opened.

**Rests on** — nothing in this phase. It rests on [Area 7's rule](../../strands/source-reading.md#area-7-kubelet), which is the strongest in the corpus and is the reason this exercise exists at all: there is no file to enter through, so the map comes from the SIG's prose first.

**Topology** — **none.** Two clones and a text editor. Do this on [`forge`](../../strands/lab-topologies.md#build-guest) beside the `~/src/kubernetes` clone [P5 made](../../phases/05-scheduler.md#m5-1), or on the Mac; nothing here needs a cluster and the next exercise is expensive enough to want the ceiling free.

**Setup** — the two narrative sources for this phase live in two repositories that are not `kubernetes/kubernetes`, and both are needed for the whole phase:

```sh
ls ~/src/community || git clone --filter=blob:none https://github.com/kubernetes/community ~/src/community
ls ~/src/design-proposals-archive || git clone --filter=blob:none https://github.com/kubernetes/design-proposals-archive ~/src/design-proposals-archive
```

The archive is not maintained and that is the point: for PLEG, eviction and the cgroup hierarchy it holds the **only** narrative descriptions that exist, which is why [Area 7](../../strands/source-reading.md#area-7-kubelet) leads with it rather than with code.

**Do**

1. Read `~/src/community/contributors/devel/sig-node/kubelet.md` (item 1) end to end. It is 9.6 KB and it is the map.

2. Build the inventory as a table. One row per manager the doc names — pod workers, PLEG, the status manager, the probe manager, the volume manager, the container manager (cgroups), the eviction manager, the image manager, the pod-source config layer. For each, fill three columns: **package**, **one sentence**, and **this phase**.

3. Fill the third column from [the phase's module list](../../phases/06-kubelet-node.md#modules), not from a guess. Exactly one function is assigned from `kubelet.go` in this whole phase; find which one and mark every other row of that file's contents as out of scope. Two managers on your list are read in [P8](../../phases/08-storage.md) instead — mark them as owed rather than as gaps.

4. Read `~/src/community/contributors/devel/sig-node/container-runtime-interface.md` (item 2) and add a second small table: `RuntimeService` versus `ImageService`, and which of your managers talks to which.

5. Answer [module 6.1's first reading question](../../phases/06-kubelet-node.md#m6-1) — what the sandbox (pause) container is *for* — in one line, in your own words, from the doc. You will check that line against a running node in [the next exercise](02-one-pod-is-how-many-cri-calls.md).

**Expect** — a map with roughly nine rows in which most rows are marked *not read this phase*. That proportion is the finding, not a disappointment: the kubelet is a supervisor tree, this phase reads five of its branches, and the reason [`kubelet.go` is 156 KB](../../strands/source-reading.md#area-7-kubelet) is that it wires all of them together. A reader who starts at line 1 of that file is reading the wiring, which explains nothing about any branch.

**Write down** — the inventory, and the sandbox answer as a single sentence you are willing to be wrong about in public. Keep it; [exercise 2](02-one-pod-is-how-many-cri-calls.md) either confirms it or gives you a better one.

**Teardown** — nothing to delete. Keep both clones for the whole phase; the design-proposals archive is cited by four of the six modules. **No topology to release** — none was taken.
