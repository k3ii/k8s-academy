<a id="two-cycles-not-one"></a>
# Two cycles, one thread — drawn from memory, then checked

**Artifact** — the extension-point sequence drawn **from memory**, with each point marked as belonging to the *scheduling cycle* or the *binding cycle*, and a one-line reason for the boundary between them; then the same drawing corrected against KEP-624 and the source, with the corrections circled.

**Rests on** — [the table](02-eleven-points-and-what-an-error-does.md). Draw first, check second — a drawing produced with the file open teaches nothing, because the file is doing the remembering.

**Topology** — none.

**Do**

1. Close the source. Draw the sequence. Mark the cycle boundary where you think it falls.

2. Read [KEP-624](../../strands/source-reading.md#area-3-scheduler) — the scheduling framework KEP. It is the design document, so it states the *reason* for the split, which the code cannot.

3. Find the boundary in code. It is a `go` statement:

   ```sh
   grep -n 'go func' pkg/scheduler/schedule_one.go | head
   ```

   Read the comment above it. Then answer three questions from the code rather than from the KEP:
   - which points run **before** that `go`, one pod at a time, with the next pod waiting;
   - which points run **after** it, concurrently with the *next* pod's scheduling cycle;
   - what the scheduler does to its own cache at the boundary so that the next pod's cycle sees a node that is not actually running the pod yet.

4. Circle every place your drawing was wrong, and write one clause per circle saying what you had assumed.

**Expect** — the boundary to fall somewhere you did not draw it, most commonly a point too early. The design reason is a throughput one: the expensive, slow, network-bound part of placing a pod is the API write and anything a plugin has to wait for, and holding the single scheduling thread for that would make the scheduler's rate a function of API latency.

Expect the cache answer to be the interesting one. Something has to make the *next* pod's fit calculation account for a pod that has been decided but not yet written, or the scheduler would place the whole backlog on one node. [Exercise 11](11-what-assume-buys.md) measures exactly how much that mechanism is worth, using a scheduler that does not have it.

**Write down** — both drawings, the corrections, and the name of the function at the cache boundary. Do not write down what it does yet; that is the point of building a scheduler without it first.

**Footprint note** — reading only.

**Teardown** — nothing created. **No topology to release.**
