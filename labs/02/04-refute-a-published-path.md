<a id="refute-a-published-path"></a>
# Break one published citation, on purpose

**Claim** — you can take a path or symbol cited in a pre-2023 etcd article and show, with a sha or a `file:line`, either where it lives now or that it is gone. Refuting someone else's citation is the drill; the article is disposable.

**Rests on** — techniques 4 and 5 of [the method](../../strands/source-archaeology.md#method) — the pickaxe and blame walked backwards — and both previous exercises, whose answers you may not reuse. Pick a *third* symbol.

**Topology** — none. [`forge`](../../strands/lab-topologies.md#build-guest) only; it is [not part of any topology](../../strands/lab-topologies.md#build-guest) and is up regardless.

**Do**

1. Find a target. Any etcd storage or watch write-up from 2019–2022 will do; conference slides and vendor blogs are the richest seams because they paste paths. Take one paragraph and extract exactly one claim of the form *"X is in `path/to/file.go`"* or *"the function `F` does Y"*. Write the claim down as a sentence before you check it — an unstated claim is unfalsifiable.

2. Check the cheap way first:

   ```sh
   cd ~/src/etcd
   ls path/to/file.go 2>&1
   git grep -n 'func F' -- '*.go' | head
   ```

   If the symbol is there under a different path, you have your answer already and step 3 dates it. If `git grep` finds nothing, the symbol was renamed or deleted, and the pickaxe is the only thing that will find it.

3. Pickaxe for the string, across all of history:

   ```sh
   git log -S'F(' --oneline -- '*.go' | tail -5     # commits that changed the count of it
   git log -G'func F' --oneline -- '*.go' | tail -5 # commits whose diff matched the regex
   ```

   Read the *last* lines: `git log` is newest-first, so the introduction is at the bottom and the removal is at the top.

4. Take the newest sha `R` from step 3 and read the diff that ended it:

   ```sh
   git show --stat <R>
   git show <R> -- '*.go' | grep -E '^[-+].*F\(' | head
   ```

5. State the refutation in the form [the standard](../../strands/source-archaeology.md#drills) demands: *"the article says `F` is in `A`; as of `<sha>` it is in `B` at line `N`"*, or *"as of `<sha>` it no longer exists, replaced by `G`"*.

6. Confirm your refutation is checkable by someone hostile. Have the exact command that produces the evidence in one line, and run it fresh:

   ```sh
   git grep -n 'func G' -- '*.go'
   ```

**Expect** — most 2019–2022 citations into etcd's storage layer are broken by [the `mvcc/` move alone](02-date-the-mvcc-move.md), and most into consensus are broken by [the extraction](03-prove-the-raft-extraction.md). That is why the phase asks for a *third* symbol: the interesting refutations are the ones where the file still exists and the function inside it was renamed, split or inlined, because those are the citations a careless reader will believe.

The failure mode to watch for is refuting the wrong thing. "The path is wrong" is not a refutation if the article's actual claim was about behaviour and the path was incidental — say which of the two you broke.

**Write down** — the refutation sentence, the command that proves it, and its output. That is [the checklist's](../../phases/02-etcd.md#checklist) *one broken pre-2023 citation refuted* item, and it is the first time in the curriculum the answer is required to be a sha rather than a paragraph.

**Teardown** — nothing was created; step 2's `git grep` pulled some blobs into the clone, which is the clone doing its job. Both clones stay for the phase.
