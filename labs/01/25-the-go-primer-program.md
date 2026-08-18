<a id="the-go-primer-program"></a>
# One program that exercises every primer construct

**Artifact** — a single small Go program using every construct in [module 1.6's list](../../phases/01-operate-shallow.md#m1-6), with a table-driven test that passes. **[The checklist requires it](../../phases/01-operate-shallow.md#checklist)**, and it is the last thing in the phase's teaching order because it exists to remove the language as a variable before [P2](../../phases/02-etcd.md) opens `k/k` source.

**Topology** — none. This builds on [`forge`](../../strands/lab-topologies.md#build-guest), which is up regardless of any topology, and the cluster is already gone by [the incident note](24-the-incident-note.md).

**Build**

**This is not one of [the eleven build-track artifacts](../../strands/build-mechanics.md#artifact-table)** — [the phase has none](../../phases/01-operate-shallow.md#modules) — so no module path convention, no version stamp, no ship step from `build-mechanics` applies. It is a few hundred lines in `build/01-go-primer/`.

Rather than six toy programs, write **one** that does something small and coherent, because the constructs only teach anything when they have to coexist. A worker pool that fetches N things with a deadline is enough, and it forces all six:

```
build/01-go-primer/
  go.mod
  fetch.go        the Fetcher interface and two implementations
  pool.go         the goroutines, the channel, the select, the WaitGroup
  errors.go       a typed error, wrapped and unwrapped
  pool_test.go    the table test
```

Six things the program must do, each provable by deleting it and watching something break:

1. **A `context.Context` as the first parameter of every function that can block**, cancelled by a deadline the caller sets. Prove it: set the deadline shorter than the work and confirm the program returns early rather than finishing.
2. **A producer feeding a channel, a `select` with a `ctx.Done()` case, and a `sync.WaitGroup`** for shutdown. Prove it: run under `go test -race`.
3. **An interface with two implementations**, one real and one fake, and the test uses the fake. This is the pattern every `k/k` `Interface` type exists for, and using it here is what makes the fakes in [P4](../../phases/04-controllers.md) unremarkable.
4. **Struct embedding** used once, deliberately, where composition genuinely reads better than a field.
5. **Wrapped errors** — a typed error at the bottom, `fmt.Errorf("...: %w", err)` on the way up, and `errors.Is` and `errors.As` at the top *both* used for the thing each is for. Getting the two mixed up is the most common Go error-handling bug and it is worth making it once, on purpose.
6. **One generic function** — enough to read them, since `client-go` now uses them. A `Map[T, U]` over a slice is plenty.

**Verify**

```sh
cd build/01-go-primer
go vet ./...
go test -race -run Test -v ./...
go test -run TestFetch -count=1 ./...      # the table test, named cases in the output
```

**Gate** — `go vet` clean, `go test -race` passing, and the table test's output naming each case (`t.Run(tc.name, ...)`) rather than printing one pass line for the lot. The named subtests are the shape, not a nicety: every test you will read in `k/k` looks like this, and every test you write against `envtest` in [P4](../../phases/04-controllers.md) will too.

**Expect** — the race detector finds something on the first honest attempt, usually a `WaitGroup.Add` inside the goroutine instead of before it, or the loop variable captured by the closure. Both are worth hitting once here rather than in a controller. The `errors.Is` versus `errors.As` distinction is the other thing that usually needs a second pass: `Is` compares against a sentinel value, `As` extracts a typed error — and `%w` is what makes either possible through however many layers of wrapping.

**Write down** — commit the program with the `go test -race -v` output. That transcript is the proof; the checklist asks for a passing table test and this is how you show it passed.

**Teardown** — `go clean -modcache` on `forge` if disk is tight; [`build-mechanics#p5-split`](../../strands/build-mechanics.md#p5-split) is the runbook and the reason. No topology was involved, so there is nothing to destroy.
