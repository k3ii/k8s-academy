<a id="state-without-globals"></a>
# Why a plugin cannot keep its own state in a package variable

**Claim** — a plugin that computes something expensive at `PreFilter` and stashes it in a struct field or a package variable is not merely bad style: it is wrong, and the two things that make it wrong are that one plugin instance serves every pod, and that a binding cycle for one pod runs while the scheduling cycle for the next is in progress. `CycleState` exists to be the only correct place for that value.

**Rests on** — [the overlap you just measured](13-why-the-bind-is-async.md), which is one of the two reasons, and [the extension-point table](02-eleven-points-and-what-an-error-does.md), which is where the other one becomes obvious.

**Topology** — none. Reading on [`forge`](../../strands/lab-topologies.md#build-guest); `pair` stays up and idle.

**Do**

1. Read `pkg/scheduler/framework/cycle_state.go` in full. It is small.

   ```sh
   wc -l pkg/scheduler/framework/cycle_state.go
   grep -n 'type CycleState\|func NewCycleState\|func (c \*CycleState) Read\|Write\|Clone' pkg/scheduler/framework/cycle_state.go
   ```

2. Establish the lifetime. Find where a `CycleState` is created and confirm from the call site how many pods one of them serves:

   ```sh
   grep -n 'NewCycleState\|cycleState' pkg/scheduler/schedule_one.go | head
   ```

3. Establish the plugin lifetime, which is the other half. Find where plugins are constructed and confirm how many times per pod that happens:

   ```sh
   grep -n 'func NewFramework\|pluginsMap\[' pkg/scheduler/framework/runtime/framework.go | head
   ```

4. Now find a real user of it and read what it stores. `noderesources` is the natural one:

   ```sh
   grep -rn 'CycleState\|preFilterState' pkg/scheduler/framework/plugins/noderesources/fit.go | head -20
   ```

   Write down: what value is computed once at `PreFilter`, how many times it is read during `Filter`, and what that saves.

5. Answer the module's question as a defect report rather than a rule. Describe, in three sentences, the exact sequence of events by which a package variable holding "the current pod's resource request" produces a **wrong scheduling decision** — not a crash, not a race detector warning, but a pod placed on a node that cannot hold it. Name which of the two mechanisms from steps 2 and 3 does the damage.

6. Find the `Clone` method and answer why it exists at all, given that the state is per-pod. The answer is in the extension points that run after the boundary.

**Expect** — one plugin instance for the lifetime of the scheduler, one `CycleState` per scheduling attempt, and a `PreFilter` value read once per node. On a large cluster that is the difference between parsing a pod's resource requests once and parsing them five thousand times, which is why the mechanism exists at all — the correctness argument and the performance argument point the same way here, and it is worth noticing that they usually do not.

Expect `Clone` to matter for the state that has to survive into a concurrent phase. When you write [your own plugin](28-the-out-of-tree-plugin.md), this is the method you will get wrong if you get anything wrong.

**Write down** — the two lifetimes with `file:line`, the three-sentence defect report from step 5, and the answer to step 6.

**Footprint note** — reading only. `pair` is up and idle; no change to the 7.5GB.

**Teardown** — nothing created. **The topology stays.**
