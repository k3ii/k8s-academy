<a id="eleven-points-and-what-an-error-does"></a>
# The extension points, and what an error at each one costs

**Artifact** — one table with a row per extension point in `pkg/scheduler/framework/interface.go`, and per row: the interface's method signature, what it is allowed to return, and **what the scheduler does when a plugin returns each status code there**. This is the phase's first write-down and every later exercise indexes into it.

**Rests on** — [the call path](01-the-sig-tour-in-call-order.md). The tour tells you where the framework is invoked from; this tells you what the framework can be told.

**Topology** — none. Reading on [`forge`](../../strands/lab-topologies.md#build-guest).

**Do**

1. Open `pkg/scheduler/framework/interface.go` — [the area's ⭐ entry point](../../strands/source-reading.md#area-3-scheduler), and at 17.6 KB the smallest file in this phase that repays a line-by-line read.

2. Find the `Code` constants before you look at any plugin interface. There are a handful; write out what each one *means to the caller*, not what it is named. Two of them are refusals and the difference between them is the whole reason a pod can sit in one queue rather than another:

   ```sh
   sed -n '/^const (/,/^)/p' pkg/scheduler/framework/interface.go | head -60
   grep -n 'func (c Code) String\|UnschedulableAndUnresolvable\|case Skip' pkg/scheduler/framework/interface.go
   ```

3. Now list the plugin interfaces. Each is a Go interface with one or two methods:

   ```sh
   grep -n '^type .*Plugin interface' pkg/scheduler/framework/interface.go
   ```

   Take that list as the row set of your table. It is the authoritative one — a diagram in a blog post is not.

4. For each row, answer the question the phase asks: **what does an error here do?** The answer is not in `interface.go` for most of them; it is at the call site, in `schedule_one.go` and in `framework/runtime/framework.go`. Follow one point at a time:

   ```sh
   grep -n 'RunPreFilterPlugins\|RunFilterPlugins\|RunReservePlugins\|RunPermitPlugins\|RunPreBindPlugins' pkg/scheduler/framework/runtime/framework.go
   ```

   For each `Run*Plugins`, read what it does with a non-`Success` status: does it stop the cycle, mark the pod unschedulable, run the matching *undo*, or abort the bind and leave the pod bound?

5. Three rows deserve a sentence rather than a phrase, because they are the ones that surprise people:
   - the point where a rejection means *"try again when the cluster changes"* versus the point where it means *"never, for this pod, on any node"*;
   - the point after which an undo hook must run on **every** plugin that already succeeded, not just the one that failed;
   - the point at which the node has already been committed to the scheduler's own cache, so a failure has to be actively reversed rather than simply abandoned.

**Expect** — a table with roughly a dozen rows in which the same status code means materially different things in different rows. That asymmetry is the finding: the framework is not a pipeline of equivalent hooks, it is a sequence in which the cost of failing rises monotonically. [Exercise 29](29-a-hard-error-at-reserve.md) is where you pay one of those costs on purpose.

Expect also to find at least one interface whose method returns something other than a `*Status` — those are the scoring points, and they are the subject of [module 5.6](34-placement-that-differs-measurably.md).

**Write down** — the table, and the `file:line` of the `Run*Plugins` function that produced each "what an error does" answer. [The checklist](../../phases/05-scheduler.md#checklist) asks for this sequence from memory later; the citations are what make the recall checkable rather than confident.

**Footprint note** — reading only. No cluster, no build.

**Teardown** — nothing created. **No topology to release.**
