<a id="the-go-primer-program"></a>
# One program that exercises every primer construct

**Artifact** — one small Go program that uses every construct in [module 1.6's list](../../phases/01-operate-shallow.md#m1-6), with a table-driven test that passes. **[The checklist requires it](../../phases/01-operate-shallow.md#checklist).** It is the last item in the teaching order of the phase, and it has one purpose: it removes the language as a variable before [P2](../../phases/02-etcd.md) opens the `k/k` source.

**Topology** — none. This program builds on [`forge`](../../strands/lab-topologies.md#build-guest), which is up whatever topology runs. The cluster is already gone, because [the incident note](24-the-incident-note.md) destroyed it.

**Build**

**This program is not one of [the eleven build-track artifacts](../../strands/build-mechanics.md#artifact-table)**, because [the phase has none](../../phases/01-operate-shallow.md#modules). No module path convention applies. No version stamp applies. No ship step from `build-mechanics` applies. The program is a few hundred lines in `build/01-go-primer/`.

Do not write six toy programs. Write **one** program that does something small and coherent. The constructs only teach you anything when they have to coexist. A worker pool that fetches N things with a deadline is enough, and it forces all six constructs:

```
build/01-go-primer/
  go.mod
  fetch.go        the Fetcher interface and two implementations
  pool.go         the goroutines, the channel, the select, the WaitGroup
  errors.go       a typed error, wrapped and unwrapped
  pool_test.go    the table test
```

The program must do six things. You can prove each one by deleting it and watching something break.

1. **Take a `context.Context` as the first parameter of every function that can block.** The caller sets a deadline, and the deadline cancels the context. Prove it: set the deadline shorter than the work, and confirm that the program returns early instead of finishing.
2. **Run a producer that feeds a channel, a `select` with a `ctx.Done()` case, and a `sync.WaitGroup`** for shutdown. Prove it: run the program under `go test -race`.
3. **Define an interface with two implementations**, one real and one fake. The test uses the fake. Every `Interface` type in `k/k` exists for this pattern. Using it here is what makes the fakes in [P4](../../phases/04-controllers.md) unremarkable.
4. **Use struct embedding once, deliberately**, at the one place where composition genuinely reads better than a field.
5. **Wrap your errors.** Put a typed error at the bottom. Use `fmt.Errorf("...: %w", err)` on the way up. At the top, use `errors.Is` and `errors.As`, *each* for the thing that it is for. Mixing the two up is the most common Go error-handling bug, and it is worth making that mistake once, on purpose.
6. **Write one generic function.** You need only enough to read them, because `client-go` now uses them. A `Map[T, U]` over a slice is plenty.

**Verify**

```sh
cd build/01-go-primer
go vet ./...
go test -race -run Test -v ./...
go test -run TestFetch -count=1 ./...      # the table test, named cases in the output
```

**Gate** — three conditions must hold. `go vet` is clean. `go test -race` passes. The table test names each case in its output, through `t.Run(tc.name, ...)`, instead of printing one pass line for the whole set. The named subtests are the shape, and not a nicety. Every test that you will read in `k/k` looks like this, and so will every test that you write against `envtest` in [P4](../../phases/04-controllers.md).

**Expect** — the race detector finds something on the first honest attempt. It is usually one of two things: a `WaitGroup.Add` inside the goroutine instead of before it, or the loop variable captured by the closure. Both are worth hitting once here, rather than in a controller. The other thing that usually needs a second pass is the distinction between `errors.Is` and `errors.As`. `Is` compares against a sentinel value. `As` extracts a typed error. `%w` is what makes either of them possible, through any number of layers of wrapping.

**Write down** — commit the program, with the output of `go test -race -v`. That transcript is the proof. The checklist asks for a passing table test, and this is how you show that it passed.

**Teardown** — run `go clean -modcache` on `forge` if disk is tight. [`build-mechanics#p5-split`](../../strands/build-mechanics.md#p5-split) is the runbook, and it is the reason. No topology was involved, so there is nothing to destroy.
