<a id="find-the-queue-yourself"></a>
# The archaeology case: the path in the documentation no longer exists

**Artifact** — the current location of the scheduler's queue implementation, found by search rather than by following a link, with the sha it was found at, the path the documentation gives, and one sentence on how you established which is live and which is stale.

**Rests on** — [the SIG tour](01-the-sig-tour-in-call-order.md), where you already noted paths that did not resolve. This is the one the phase makes a set-piece of, and [the area names it as the canonical archaeology case](../../strands/source-reading.md#area-3-scheduler) — the technique matters more here than the answer, because the answer will move again.

**Topology** — none. Reading on [`forge`](../../strands/lab-topologies.md#build-guest).

**Do**

1. Start from the wrong path on purpose. Search for `pkg/scheduler/internal/queue` in the tree and in the docs:

   ```sh
   ls pkg/scheduler/internal/queue 2>&1
   grep -rn 'internal/queue' --include='*.md' ~/src/kubernetes/ | head
   ```

2. Find where the code went, without being told. Search for the thing rather than the place — a type name is more durable than a directory:

   ```sh
   grep -rn 'SchedulingQueue interface' --include='*.go' pkg/scheduler/
   grep -rln 'activeQ\|backoffQ\|unschedulablePods' --include='*.go' pkg/scheduler/ | sort
   ```

3. Establish that what you found is live rather than a copy. Three checks, all cheap, and doing all three is the technique:

   ```sh
   grep -rn 'NewSchedulingQueue\|SchedulingQueue' pkg/scheduler/scheduler.go | head
   git log --oneline -5 -- pkg/scheduler/backend/queue/
   git log --oneline -3 -- pkg/scheduler/internal/queue/ 2>/dev/null
   ```

   The first proves it is *reached*; the second proves it is *maintained*; the third proves the old path is not.

4. Find the move itself and read its commit message:

   ```sh
   git log --oneline --follow -- pkg/scheduler/backend/queue/scheduling_queue.go | tail -5
   ```

5. Record the file inventory you will be reading for the rest of this module, with sizes, because one of them is enormous and [the area is explicit that it is reference-only](../../strands/source-reading.md#area-3-scheduler):

   ```sh
   ls -lhS pkg/scheduler/backend/queue/*.go | grep -v _test
   ```

**Expect** — the old path to be absent from the tree and present in the prose, and the new one to be reachable from `scheduler.go` in one hop. Expect the largest file in the directory to be around a hundred kilobytes, and expect the useful ones — the backoff queue, the active queue, the unschedulable set — to be a fraction of that. **The size distribution is the reading plan**: three small files carry the model, and the large one is where you look things up.

Expect the commit message on the move to say something about package layering rather than about scheduling, which is the general case: code moves for reasons that have nothing to do with what it does, so a stale path is almost never a sign that the concept changed.

**Write down** — the live path, the stale path, the sha, the three checks with their outputs, and the file inventory with sizes. [The gate](../../phases/05-scheduler.md#gate) asks you to name a stale documentation path and the current location; this is that answer, and it is worth having it written rather than remembered.

**Footprint note** — reading only. `pair` back up (or woken) for [exercise 20](20-watch-a-pod-move.md); nothing here needs it.

**Teardown** — nothing created. **The topology stays.**
