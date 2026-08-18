# Labs — Phase 1, Operate a cluster (deliberately shallow)

Twenty-six exercises in the order they are meant to run. Each states one claim to test or
one artifact to produce, links its [topology](../../strands/lab-topologies.md) rather than
restating a footprint, and ends with a teardown that does two things: **deletes what that
exercise created**, then says whether the topology stays or goes. It usually stays —
[a provision costs minutes](../../strands/lab-topologies.md#teardown) before any teaching
happens.

The framing — why each module exists, what to read and the question to answer from it —
stays in [`phases/01-operate-shallow.md`](../../phases/01-operate-shallow.md). These files
hold only what you type and what you should see.

**The phase is held short on purpose and so are these.** Every exercise here has a deeper
version somewhere in P2–P10, and each one says where. Resist the descent; that is what the
next nine phases are for.

| # | Exercise | Why it exists |
|---|---|---|
| 1 | [A two-node cluster, stood up by hand](01-provision-and-kubeadm-init.md) | The parts, not the one-command distro — and the `NotReady` node that is not broken. |
| 2 | [The map of what kubeadm left on disk](02-what-kubeadm-generated.md) | **A gate condition, and the file P3 reads as source.** Three CAs, not one. |
| 3 | [Two control planes, one flag list](03-static-pod-flags-vs-local-up.md) | The diff between a dev control plane and a real one is almost entirely security. |
| 4 | [1.C4 — move the apiserver's manifest out of the directory](04-static-pod-blip.md) | The single most clarifying fact about how Kubernetes runs itself: a kubelet watching a directory. |
| 5 | [Who writes each half of an object](05-spec-status-ownership.md) | The split is about reconciliation, and the two objects that break the pattern say why. |
| 6 | [What resourceVersion does and does not promise](06-resourceversion-moves.md) | Two permitted uses, three forbidden ones, and a `Conflict` you caused on purpose. |
| 7 | [Write a lie into status and time the correction](07-stomp-the-status.md) | Uses the static-pod trick as an on/off switch for a controller, so the loop is visible by its absence. |
| 8 | [Predict the ReplicaSet counts at every step](08-rolling-update-predictions.md) | Predicted, not watched. The retained empty ReplicaSet is what the incident note has to explain. |
| 9 | [Three probes, three different consequences](09-probes-three-kinds.md) | Two of the three produce a pod that looks fine in `kubectl get pods`. |
| 10 | [The same ConfigMap, two ways in](10-config-as-env-and-volume.md) | One updates in place, one cannot, and the Secret mount is a P0 `tmpfs` wearing a manifest field. |
| 11 | [The P0 capability drop, as a manifest field](11-drop-a-capability-in-a-manifest.md) | Same mechanism as P0, different author. Proven with `capsh`, not with the field. |
| 12 | [Five workload kinds, chosen by the forcing property](12-choose-the-workload-shape.md) | Enough to choose the right shape, not to read its controller — and the DaemonSet's injected tolerations. |
| 13 | [1.C1 — delete a pod that something is watching](13-delete-a-managed-pod.md) | **The gate names this one.** Which controller, and what two values it compared. |
| 14 | [One Deployment, four exposures](14-four-ways-to-expose.md) | Installs MetalLB and writes the first `IPAddressPool` in the curriculum. Each component removed in turn. |
| 15 | [A readiness probe, followed to an endpoint list](15-endpointslice-drains.md) | Five hops and one race — the one that makes `preStop` hooks necessary. |
| 16 | [Why a one-label name resolves and a two-label name does not](16-dns-from-a-pod.md) | `ndots:5` costs four failed queries per external name, and that is not a misconfiguration. |
| 17 | [1.C2 — an empty endpoint list, from `describe` alone](17-break-the-endpoints.md) | Four causes, a triage order you own, and the one cause your triage order misses. |
| 18 | [Two overlays over one base](18-kustomize-base-and-overlays.md) | The generator hash is what Helm has to fake with a checksum annotation. |
| 19 | [A chart with a subchart, a helper and a real conditional](19-author-a-helm-chart.md) | The capstone's input, gated by `--dry-run=server` rather than by `helm lint`. |
| 20 | [Find the release on the cluster and read it](20-helm-upgrade-and-release-state.md) | A gzipped Secret, decoded by hand, and the third merge input that is not in it. |
| 21 | [Delete something Helm created and watch nothing happen](21-helm-does-not-reconcile.md) | Converges *when you run it* versus *because time passed*. The whole GitOps argument, as an experiment. |
| 22 | [1.C3 — wedge a rollout, then recover it](22-botch-a-rollout-and-roll-back.md) | Three break-shapes, ranked by how long they take to spot, with a traffic loop counting the damage. |
| 23 | [Three services, one `helm install`, in a browser](23-the-multi-service-app.md) | **The capstone's first half.** `--wait` is the honest test, and startup ordering is what fails it. |
| 24 | [The one-page incident note](24-the-incident-note.md) | **The capstone's second half**, and the format P6, P8 and P11 escalate. Ends the phase's cluster. |
| 25 | [One program that exercises every primer construct](25-the-go-primer-program.md) | Removes the language as a variable before P2. The race detector finds something on the first honest attempt. |
| 26 | [The CKAD drill block, as a timed harness](26-ckad-drill-block.md) | A different activity with a different success condition: a clock, not a mechanism. |

**One cluster runs exercises 1 through 23.**
[`pair`](../../strands/lab-topologies.md#pair) comes up at exercise 1 and is destroyed by
exercise 24, which ends it on purpose so that the phase's last two exercises cannot lean on
it. Exercise 25 needs **no topology at all** — it builds on
[`forge`](../../strands/lab-topologies.md#build-guest) — and exercise 26 wants a **fresh**
`pair` it did not build.

Two things arrive mid-chain and stay up for the rest of the phase: **MetalLB** and
**ingress-nginx** at exercise 14, roughly 250Mi across the two nodes and the first standing
cost the worker carries. Exercise 23 is the phase's peak; its footprint note says what to
scale down if the arithmetic gets tight.

**The CNI is Flannel, not Cilium** — [exercise 1 gives the reasoning](01-provision-and-kubeadm-init.md)
and it is a footprint decision, not a preference.
