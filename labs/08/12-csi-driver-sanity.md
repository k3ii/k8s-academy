<a id="csi-driver-sanity"></a>
# A CSI driver that passes `csi-sanity`, with no Kubernetes anywhere

**Artifact** — a Go binary serving the three CSI gRPC services over a UNIX socket, passing `csi-sanity` clean. **This is [stage 1](../../strands/build-mechanics.md#two-stages), and it is the only fully objective gate in this curriculum outside the three exams.**

**Rests on** — [Module 8.1's reading question](../../phases/08-storage.md#m8-1) on which calls the spec requires to be idempotent, and where it says so. `csi-sanity` will find every idempotency bug you left; the reading is how you avoid writing them.

**Topology** — **none.** This runs entirely on [`forge`](../../strands/lab-topologies.md#build-guest); no cluster is involved and none needs to be up. If `pair` is still running from the module labs, leave it — this exercise does not touch it and the two [fit inside the ceiling together](../../strands/lab-topologies.md#ceiling).

**Build**

```
build/08-csi-driver/
  cmd/toy-csi/main.go        flags: --endpoint, --node-id; signal handling; grpc.Serve
  internal/identity/         GetPluginInfo, GetPluginCapabilities, Probe
  internal/controller/       CreateVolume, DeleteVolume, ControllerGetCapabilities
  internal/node/             NodeStageVolume, NodeUnstageVolume, NodePublishVolume,
                             NodeUnpublishVolume, NodeGetCapabilities, NodeGetInfo
  internal/store/            the backing store, and nothing clever
```

Each `internal/` package satisfies exactly one generated interface from
`container-storage-interface/spec/lib/go/csi` — `IdentityServer`, `ControllerServer`,
`NodeServer` — and `main.go` registers all three on one server. Splitting them into
separate binaries is a later problem and not this one.

Constraints that are the actual lesson:

- **The backing store is directories on the host.** Deliberately trivial; the subject is the contract and the lifecycle, not a filesystem.
- **Every call named above is idempotent**, and `csi-sanity` calls each one twice.
- **Volume identity is yours to invent** and must survive a restart, because `csi-sanity` restarts nothing but Kubernetes will.
- **Return the right gRPC codes.** `AlreadyExists` versus `OK` on a repeated `CreateVolume` with different parameters is a specific requirement in the spec, not a judgement call.

**Gate**

```sh
ssh hopper
ssh forge
go run ./cmd/toy-csi --endpoint=unix:///tmp/csi.sock --node-id=forge &
csi-sanity --csi.endpoint=/tmp/csi.sock
```

**Expect** — it passes or it does not. Commit the output. Read `kubernetes-csi/csi-driver-host-path` and `external-provisioner`'s `doc/design.md` for shape, not for code to copy.

**Scope discipline** — no snapshots, no expansion, no topology in your driver. Those were read about in [expansion](09-expansion-two-phase.md) and [snapshots](10-snapshot-and-restore.md), not implemented. A driver that grows features is a month you did not budget.

**Teardown** — stop the `go run` process. `forge` [is never torn down](../../strands/lab-topologies.md#build-guest) and its module cache is the reason.
