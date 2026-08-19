<a id="the-paper-trace-before-the-cluster"></a>
# The map drawn from notes, before a single command — so the live trace confirms a prediction instead of discovering a path

**Artifact** — a hand-drawn pod-create map, assembled from your P2–P10 notes *alone*, that marks at each of the five area boundaries the single file you expect the request to be in — then reconciled against [trace #1's spec](../../strands/source-reading.md#trace-pod-create) and corrected **in red** where the two disagree. Where your map is wrong is where a phase did not land, and that red mark is the real output of this exercise: it names, before you spend any RAM, which seam you are about to fail to cite.

**Rests on** — the whole descent. This is [the one phase prerequisite on all of P2–P10](../../phases/11-synthesis.md); an area you did not enter is a seam you cannot draw, and drawing it wrong here is cheaper than discovering it wrong live.

**Topology** — none. This is paper and source only; [`pair`](../../strands/lab-topologies.md#pair) is not up yet and there is nothing to cost.

**Read** — [the module framing](../../phases/11-synthesis.md#m11-1) and [trace #1's spec](../../strands/source-reading.md#trace-pod-create), but *only after* you have drawn the map from memory. Reading the spec first defeats the exercise: the point is the delta between what eight phases left in your notes and what the source actually does.

> **Question to answer from the source:** the trace crosses five areas. At each of the four *internal* seams, which single function hands the object to the next area — the last frame in area N, the first frame in area N+1? Name both, from your notes, before you open the spec.

**Build** — from your P2–P10 notes alone, draw the full path of `kubectl run nginx` and mark, at each area boundary, the file you expect the request to be in. Then open [the spec](../../strands/source-reading.md#trace-pod-create) and reconcile. Correct every wrong guess in red. Live-verify nothing yet — the live modules below do that, seam by seam; this map is the prediction they test.

**Verify from outside** — the map is honest when every arrow carries a *predicted* file name (right or wrong), not a subsystem label. "The apiserver handles it" is not a prediction; `handlers/create.go` is. A reader should be able to hold your map beside the spec and count the red corrections.

**Expect** — corrections concentrated at the seams whose phase you rushed. A clean map is either mastery or a lie you are about to pay for at the seam it hides; expect at least one red mark, and treat a wholly clean map as the thing to distrust.

**Write down** — the predicted map with a file per seam, kept beside you and corrected in red as [Seam A](02-seam-a-client-apiserver-etcd.md), [Seam B](04-seam-b-watch-cache-scheduler-binding.md) and [Seam C](05-seam-c-kubelet-cri-cni-the-syscalls.md) prove or disprove each guess. It is one of the phase's committed written artifacts.

**Footprint note** — none. No cluster, no build guest; the only cost is your own paper. [The ceiling](../../strands/lab-topologies.md#ceiling) is untouched until [Seam A](02-seam-a-client-apiserver-etcd.md) brings `pair` up.

**Teardown** — nothing was created but your notes, which you keep. No topology to release.
