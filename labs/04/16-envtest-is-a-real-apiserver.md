<a id="envtest-is-a-real-apiserver"></a>
# The gate: four assertions a fake client would pass and a real API server fails you on

**Artifact** — `build/04-operator-clientgo/` passing [its gate](../../strands/build-mechanics.md#gates): an `envtest` suite that starts a genuine `kube-apiserver` and `etcd` out of cluster, installs the CRD, runs the reconciler against it, and asserts four things **chosen because a fake client agrees with whatever you wrote**.

**Rests on** — [the hand-wired loop](15-the-hand-wired-loop.md). The suite tests that artifact and nothing else, and [exercise 31](31-scaffold-the-same-operator.md) runs this same file against the `kubebuilder` version — which is the whole reason [the diff](33-the-diff.md) is a comparison rather than a story.

**Topology** — **none.** `envtest` is a real control plane in two processes on [`forge`](../../strands/lab-topologies.md#build-guest); [`pair`](../../strands/lab-topologies.md#pair) is up but must be idle while this runs, for the reason in the footprint note.

**Setup**

```sh
go install sigs.k8s.io/controller-runtime/tools/setup-envtest@latest
export KUBEBUILDER_ASSETS=$(setup-envtest use -p path)
ls $KUBEBUILDER_ASSETS      # kube-apiserver, etcd, kubectl — real binaries, not stubs
```

Those three files are the argument for this gate in one `ls`.

**Build** — `pkg/controller/suite_test.go`: start the environment with `CRDDirectoryPaths` pointing at `config/`, build a client, start your controller against the test environment's config, and stop it in the teardown.

**The four assertions**, each with the fake-client answer beside it, because the contrast is what makes them worth writing:

| Assertion | What a fake client does |
|---|---|
| Update an `Ensemble` from a stale copy → `409 Conflict`, and the reconcile retries rather than clobbers | accepts it silently; last writer wins, forever |
| Create with `spec.voices: 99` → rejected by the CRD's schema | accepts it; your reconcile then creates 99 ConfigMaps |
| Write `status` → `metadata.generation` **unchanged**; write `spec` → generation **increments** | has no subresource; generation never moves, so `observedGeneration` logic is untestable |
| Delete an `Ensemble` carrying the finalizer → object still readable, `deletionTimestamp` set | deletes it immediately; the finalizer path never executes |

Assertion three is the one that finds real bugs: a controller that writes status through the main resource passes every unit test ever written and then, in a cluster, bumps `generation` on every status write, which makes `observedGeneration` meaningless and turns a quiet operator into one that reconciles itself in a circle.

**Do**

```sh
cd ~/src/k8s-academy/build/04-operator-clientgo
go test ./pkg/controller/... -count=1 -p 1 -v
```

**Gate** — this is it. [The strand](../../strands/build-mechanics.md#gates) names `envtest` as an objective harness for both operators precisely because a suite you wrote is good practice and bad evidence: what makes this one count is that the *API semantics* under test are upstream's, not yours. Your four assertions choose the surface; the API server decides the answers.

**Verify from outside** — while the suite runs, from a second session:

```sh
ps -o rss=,args= -C kube-apiserver -C etcd
```

**Expect** — the four assertions pass, and `ps` shows two processes you did not start by name, one of which is the same `kube-apiserver` binary family you hand-started in [P3](../../phases/03-api-machinery.md#m3-1). Make at least one assertion fail on purpose — delete the `maximum: 8` from the CRD schema and re-run — so that the suite is demonstrably capable of failing. **A gate nobody has watched fail is not evidence.**

**Write down** — the four assertions with the failure output of the one you broke, and the `setup-envtest` version string. The `kubebuilder` artifact must run this same file unmodified.

**Footprint note — this is the phase's one place where the guest is tight, and it is worth the two flags.** [`forge` is 1536MB](../../strands/build-mechanics.md#forge). A test run links the suite — the shape [the strand measured at 564 MiB](../../strands/build-mechanics.md#measurements) — and then runs `kube-apiserver` and `etcd`, which together sit in the high hundreds of MiB. Sequentially that fits with room to spare; **concurrently it does not**, and Go will happily compile one package while another package's test binary is running an API server.

The smallest change that removes the risk, rather than raising the guest: **`-p 1` on every `go test` in this phase**, and do not leave [the stage-1 operator](15-the-hand-wired-loop.md) running while the suite runs — that is a third copy of the same code holding informers open. If a run is still killed, `go build ./... && go test -p 1 -count=1` splits the link peak away from the API server entirely. [P5 raises `forge` to 2560MB](../../strands/build-mechanics.md#p5-split) because a scheduler *link* needs it; nothing in P4 does, and raising it here would hide a scheduling problem behind memory.

**Teardown** — the suite stops both binaries itself; confirm with `pgrep -a kube-apiserver` that nothing survived a failed run, which is the one way this exercise can quietly cost you 400 MiB for the rest of the day. **No topology to release** — `pair` is still up and [the drill](17-4c1-kill-it-mid-reconcile.md) needs it.
