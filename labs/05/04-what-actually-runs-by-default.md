<a id="what-actually-runs-by-default"></a>
# The default plugin set, mapped onto the points it fills

**Artifact** — your [extension-point table](02-eleven-points-and-what-an-error-does.md) with a second column: which plugins the default profile registers at each point, taken from `pkg/scheduler/framework/plugins/registry.go` and the default profile, not from documentation.

**Rests on** — [the table](02-eleven-points-and-what-an-error-does.md) and [the two cycles](03-two-cycles-not-one.md). This is what turns an interface into a running system: the framework calls whatever is registered, and this is the list of what is.

**Topology** — none. Reading on [`forge`](../../strands/lab-topologies.md#build-guest).

**Do**

1. Read `pkg/scheduler/framework/plugins/registry.go` — 4.8 KB and, as [the area notes](../../strands/source-reading.md#area-3-scheduler), a map from name to constructor and nothing more. It answers "what exists", not "what runs".

2. "What runs" is the default profile. Find it:

   ```sh
   grep -rn 'func getDefaultPlugins\|PluginSet{' pkg/scheduler/apis/config/v1/default_plugins.go | head -20
   sed -n '/func getDefaultPlugins/,/^}/p' pkg/scheduler/apis/config/v1/default_plugins.go
   ```

3. Fill the column. One plugin may appear at several points; write it in every row where it appears, because that repetition is the exercise's finding.

4. Count. How many *distinct* plugins are in the default profile, and how many *registrations* is that across all points? Those two numbers are not close.

5. Look specifically at the plugins that appear at four or more points. There are only a couple. For each, write down the four points and a one-clause guess at why a single concern needs to touch the cycle that many times. **`VolumeBinding` is one of them** — note where it appears and move on. What it does with those four registrations is [P8's subject](../../phases/08-storage.md), and P8 names this phase as its prerequisite precisely so that the *shape* is familiar before the storage semantics arrive.

**Expect** — around twenty plugins and half again as many registrations. The high-multiplicity plugins are the ones that must reserve something during the scheduling cycle and finish or release it during the binding cycle, which is the same structural pattern in every case, whatever the resource is.

Expect also a plugin registered at a point where it does nothing but return `Skip`. Finding one is worth a note: a plugin that declines cheaply at an early point is how the framework avoids paying for machinery a given pod does not need.

**Write down** — the completed table, the two counts, and the plugins with four or more registrations, one line each.

**Footprint note** — reading only.

**Teardown** — nothing created. **No topology to release.**
