<a id="the-smallest-plugin-that-exists"></a>
# A `Filter` plugin is two methods and a string

**Claim** — the smallest working scheduler plugin in the tree is under fifty lines including the licence header, and the thing that makes it a plugin is not a base class, a registration annotation or a lifecycle: it is that it satisfies an interface and appears in a map.

**Rests on** — [the default set](04-what-actually-runs-by-default.md). You have the list of what runs; this is the shape of one of them, and it is the shape [build artifact 2](28-the-out-of-tree-plugin.md) must reproduce from outside the tree.

**Topology** — none.

**Do**

1. Read all three of the tiny filters end to end. They are [item 7 of the area](../../strands/source-reading.md#area-3-scheduler) and the whole point of assigning three is that the third one is boring:

   ```sh
   wc -l pkg/scheduler/framework/plugins/nodename/*.go \
         pkg/scheduler/framework/plugins/nodeunschedulable/*.go \
         pkg/scheduler/framework/plugins/tainttoleration/*.go | grep -v _test
   cat pkg/scheduler/framework/plugins/nodeunschedulable/node_unschedulable.go
   ```

2. For each, write down four things: the `Name()` string, the interfaces it satisfies, the exact condition under which it returns a refusal, and **which refusal code** it uses. Two of the three refuse in a way that means "this will never work for this pod as written"; note which and why that is the correct choice there.

3. Find the rejection *message* each one produces — the human-readable string, not the code. Grep for it as a literal:

   ```sh
   grep -rn 'ErrReason' pkg/scheduler/framework/plugins/nodeunschedulable/ pkg/scheduler/framework/plugins/tainttoleration/
   ```

   Those strings are what a pod's event will say. Write them down verbatim; [the next exercise](06-three-rejections-three-plugins.md) produces them on a live cluster and the comparison is the check.

4. Answer the phase's question: what would you have to add to one of these files to make it also score nodes? Do not write it — name the interface and the method signature.

**Expect** — three files where the largest is dominated by the taint-matching helper and the smallest is almost entirely the struct, the `Name()` and one `if`. Expect the refusal codes to differ between the three, and expect that difference to line up exactly with the queue behaviour you will meet in [module 5.4](18-find-the-queue-yourself.md): a pod refused as unresolvable does not get retried on the same trigger as one refused as merely unschedulable.

**Write down** — the four-item description of each plugin, the three verbatim rejection strings, and the one-line answer to the scoring question.

**Footprint note** — reading only. This is the last exercise before the phase's first cluster.

**Teardown** — nothing created. **No topology to release** — [the next exercise provisions one](06-three-rejections-three-plugins.md).
