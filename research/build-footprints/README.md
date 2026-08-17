# Build footprints — how much RAM does compiling an artifact actually need?

Measured for [#12](https://github.com/k3ii/k8s-academy/issues/12), because `forge`'s sizing
depends on it and an estimate would have been wrong in three separate ways.

## Results

`CGO_ENABLED=0 GOOS=linux GOARCH=amd64`, `-p 2` (matching `forge`'s two cores), Go 1.26.5,
darwin/arm64 host cross-compiling.

| Build | Cache | Peak aggregate RSS | Wall |
|---|---|---|---|
| controller-runtime manager + webhook | cold | **564 MiB** | 43s |
| `k8s.io/kubernetes/cmd/kube-scheduler` | cold | 1076 MiB — *undercounted, see below* | 64s |
| `kube-scheduler`, link step only, DWARF kept | warm | **1535 MiB** | 5s |
| `kube-scheduler`, link only, `-ldflags="-s -w"` | warm | 1177 MiB | 3s |

`GOGC` sweep, link step, DWARF kept:

| `GOGC` | Peak |
|---|---|
| 100 (default) | 1510 / 1535 MiB across two runs |
| 50 | **1352 MiB** |
| 25 | 1426 MiB — worse than 50 |

## Three things an estimate would have got wrong

**The link is the peak, not the compile fan-out.** The cold 1076 MiB figure is simply wrong:
sampling at 1Hz across a 64-second build missed a spike lasting a few seconds. Re-sampled at
5Hz against a warm cache, where nothing but the link runs, it is 1535 MiB.

**`/usr/bin/time -l` is the wrong instrument.** It reports the largest single child's RSS. A Go
build forks dozens of `compile` processes and what OOMs a small guest is the *sum*, so the
scripts here sample aggregate RSS across the whole toolchain process tree.

**Neither `-p` nor `GOGC` is a lever.** The link is one process, so build parallelism cannot
reduce it, and the linker's *live* set is the constraint rather than uncollected garbage —
`GOGC=50` buys ~10% and `GOGC=25` gives some of it back. Run-to-run spread at identical
settings is ~25 MiB, so none of this is a number to cut fine.

## Consequences

Only P5's two artifacts link against `k8s.io/kubernetes`; the other nine are the 564 MiB shape
or smaller. So `forge` runs at 1536MB and is resized to 2560MB for P5's build modules only.

## Caveats

Measured cross-compiling from darwin/arm64. A native linux/amd64 link could differ, though not
by the ~400 MiB that would change any conclusion. The P5 plugin builds against
`kubernetes-sigs/scheduler-plugins`, whose output *is* a `kube-scheduler` with extra plugins
over the same staging-repo module graph — so `cmd/kube-scheduler` is the right proxy, and if
anything a slight underestimate.

**Still to measure:** the native link peak on `forge` itself, before P5 begins. If it exceeds
~2.2GB the 2560MB resize is not enough and `-ldflags="-s -w"` becomes mandatory.

## Reproducing

```
./build-rss.sh <label> <dir> <target> [parallelism]   # whole build, aggregate RSS
./link-peak.sh <dir> <target> <ldflags> <label>       # link step only
./gogc-peak.sh <dir> <target> <GOGC> <probe>          # GOGC sweep
```

`ctrlrt-proxy.go.txt` is the controller-runtime shape-proxy: a manager with a reconciler and a
webhook server, i.e. the import graph a `kubebuilder` scaffold produces. Drop it into a module
as `main.go` and `go mod tidy`.

The `-ldflags "-X=main.probe=..."` argument in the link scripts exists to defeat the build
cache, so each run actually links instead of returning a cached binary.
