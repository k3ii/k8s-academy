<a id="the-same-drawing-corrected"></a>
# The same drawing, now with the file names checked

**Artifact** — [objective 1's](../../phases/04-controllers.md#objectives) deliverable: the reflector → DeltaFIFO → indexer → workqueue diagram redrawn from memory with the implementing file named at every stage and no question marks left, **plus the diff against [the drawing you made before reading anything](01-draw-it-before-you-read-it.md)**. The diff is the artifact that matters; the corrected drawing is the easy half.

**Rests on** — the whole of module 4.2, exercises [6](06-the-same-key-a-hundred-times.md) through [12](12-4c4-act-before-the-cache-is-synced.md). Every box below is one you have now driven by hand.

**Topology** — none. Do not open the source while drawing; open it afterwards to check.

**Do**

1. Redraw it from memory. Then fill the same table, and add a third column:

   | Stage | File | The thing it does that nothing else does |
   |---|---|---|
   | LIST then WATCH, forever | | |
   | holds what changed | | |
   | holds what is | | |
   | holds what to work on | | |
   | calls your handlers | | |

   The third column is the one that catches a shallow answer. "Holds objects" is true of two of these boxes and distinguishes neither.

2. Check every file name against the tree, and every claim in column three against a function you can point at.

3. Put the two drawings side by side and write the diff — not "I was wrong about X", but *what I believed the shape was, and which exercise changed it*.

**Expect** — the correction is rarely in the file names. It is usually in the arrows: the store being written by the consumer rather than by the reflector, the workqueue holding strings rather than objects, and the handler chain hanging off the informer rather than off the queue. Those three are the ones the pre-reading picture almost always gets wrong, and each has an exercise behind it now.

One box deserves a sentence of its own in the write-up, because it is the one the factory hides: **nothing keeps the indexer up to date except the code that pops the queue.** You wired that by hand in [exercise 8](08-deltas-are-per-key.md) and it was four lines. In a shared informer those four lines are `HandleDeltas`, and finding them is what makes the shared informer legible rather than magic.

**Write down** — both drawings and the diff, in `journal/04-controllers.md`. This is [the checklist's](../../phases/04-controllers.md#checklist) 4.1 artifact in its finished form, and [the capstone](../../phases/04-controllers.md#capstone) assumes it exists.

**Footprint note** — nothing running. This is the last exercise before the build modules, and a good moment to check `df -h` on [`forge`](../../strands/lab-topologies.md#build-guest): the k/k clone, the module cache and everything from here on share 25G.

**Teardown** — nothing to delete. **The topology stays**, idle, for [the operator](14-generate-the-clientset.md).
