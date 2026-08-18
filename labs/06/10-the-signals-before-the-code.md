<a id="the-signals-before-the-code"></a>
# Four signals, eight predictions, written before you open the kubelet

**Artifact** — a prediction table covering every eviction signal the kubelet observes: what it measures, where the number comes from, whether it has a grace period, and what the kubelet does when it crosses. Written from the design document alone, filed unread-against-code, and scored at [exercise 12](12-an-eviction-you-configured.md).

**Rests on** — nothing. This is deliberately the first thing in module 6.3: the code is far easier to read once you have committed to an answer that the code can contradict.

**Topology** — **none.** Reading and writing only; `pair` may stay up.

**Read** — `~/src/design-proposals-archive/node/kubelet-eviction.md` (item 10), end to end. It is the document the implementation was written from and it is still the clearest statement of the model.

**Do** — fill this table in from the document, one row per signal, and add the four columns yourself:

| Signal | What it measures | Hard threshold behaviour | Soft threshold behaviour | Grace period? |
|---|---|---|---|---|
| `memory.available` | | | | |
| `nodefs.available` | | | | |
| `nodefs.inodesFree` | | | | |
| `imagefs.available` | | | | |
| `pid.available` | | | | |

Then answer these four, in writing, from the same document:

1. Which signal has **no** grace period even when configured as a soft threshold, and what is the argument for that asymmetry? [Module 6.3](../../phases/06-kubelet-node.md#m6-3) asks it as the module's question and the answer is a property of the resource, not a default someone chose.
2. What does `evictionMinimumReclaim` change about *when the kubelet stops evicting*, as opposed to when it starts?
3. Two pods are over their requests by the same absolute amount and are in the same QoS class. What decides which one goes?
4. Reclaiming disk has a step that reclaiming memory does not. What is it, and why does it change which pods get evicted for `imagefs.available`?

Finally, **predict the defaults**: guess the shipped hard threshold for `memory.available` and for `nodefs.available` before reading any code. Write the guesses down. [Exercise 11](11-synchronize-and-the-ranking.md) locates the real ones.

**Expect** — the design document to be explicit about ranking and vague about exact numbers, which is the correct division: the numbers are per-platform and live in code, and going looking for them in a design doc is the mistake this exercise is arranged to make cheaply.

Expect at least one of your four answers to be wrong in a way you can name after exercise 12. That is what the table is for.

**Write down** — the table, the four answers, and the two guessed defaults. Keep the file; three later exercises score against it.

**Footprint note** — none; nothing runs.

**Teardown** — nothing to delete. **The topology stays** if you left it up.
