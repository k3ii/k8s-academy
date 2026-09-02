# Labs — Phase 1, Operate a cluster (deliberately shallow)

Twenty-six exercises, in the order that they are meant to run. Each exercise states one
claim to test, or one artifact to produce. Each exercise links its
[topology](../../strands/lab-topologies.md) instead of restating a footprint. Each exercise
ends with a teardown, and that teardown does two things: it **deletes what the exercise
created**, and then it says whether the topology stays or goes. It usually stays, because
[a provision costs minutes](../../strands/lab-topologies.md#teardown) before any teaching
happens.

The framing stays in [`phases/01-operate-shallow.md`](../../phases/01-operate-shallow.md).
That is where you find why each module exists, what to read, and the question to answer
from the reading. These files hold two things only: what you type, and what you should see.

**The phase is held short on purpose, and so are these files.** Every exercise here has a
deeper version somewhere in P2 through P10, and each exercise says where. Resist the
descent. That is what the next nine phases are for.

| # | Exercise | Why it exists |
|---|---|---|
| 1 | [A two-node cluster, stood up by hand](01-provision-and-kubeadm-init.md) | You build the parts, and not the one-command distro. It also shows a `NotReady` node that is not broken. |
| 2 | [The map of what kubeadm left on disk](02-what-kubeadm-generated.md) | **A gate condition, and the file that P3 reads as source.** There are three CAs, and not one. |
| 3 | [Two control planes, one flag list](03-static-pod-flags-vs-local-up.md) | The diff between a dev control plane and a real one is almost entirely security. |
| 4 | [1.C4 — move the apiserver's manifest out of the directory](04-static-pod-blip.md) | This is the single most clarifying fact about how Kubernetes runs itself: a kubelet watches a directory. |
| 5 | [Who writes each half of an object](05-spec-status-ownership.md) | The split is about reconciliation. The two objects that break the pattern say why. |
| 6 | [What resourceVersion does and does not promise](06-resourceversion-moves.md) | Two permitted uses, three forbidden ones, and a `Conflict` that you caused on purpose. |
| 7 | [Write a lie into status and time the correction](07-stomp-the-status.md) | It uses the static-pod trick as an on/off switch for a controller. The loop is then visible by its absence. |
| 8 | [Predict the ReplicaSet counts at every step](08-rolling-update-predictions.md) | You predict the counts, and you do not watch them. The retained empty ReplicaSet is what the incident note must explain. |
| 9 | [Three probes, three different consequences](09-probes-three-kinds.md) | Two of the three produce a pod that looks fine in `kubectl get pods`. |
| 10 | [The same ConfigMap, two ways in](10-config-as-env-and-volume.md) | One way updates in place, and one way cannot. The Secret mount is a P0 `tmpfs` that wears a manifest field. |
| 11 | [The P0 capability drop, as a manifest field](11-drop-a-capability-in-a-manifest.md) | Same mechanism as P0, different author. You prove it with `capsh`, and not with the field. |
| 12 | [Five workload kinds, chosen by the forcing property](12-choose-the-workload-shape.md) | It is enough to choose the right shape, and not to read its controller. It also shows the DaemonSet's injected tolerations. |
| 13 | [1.C1 — delete a pod that something is watching](13-delete-a-managed-pod.md) | **The gate names this one.** Which controller, and what two values it compared. |
| 14 | [One Deployment, four exposures](14-four-ways-to-expose.md) | It installs MetalLB and writes the first `IPAddressPool` in the curriculum. Each component is removed in turn. |
| 15 | [A readiness probe, followed to an endpoint list](15-endpointslice-drains.md) | Five hops and one race. It is the race that makes `preStop` hooks necessary. |
| 16 | [Why a one-label name resolves and a two-label name does not](16-dns-from-a-pod.md) | `ndots:5` costs four failed queries per external name, and that is not a misconfiguration. |
| 17 | [1.C2 — an empty endpoint list, from `describe` alone](17-break-the-endpoints.md) | Four causes, a triage order that you own, and the one cause that your triage order misses. |
| 18 | [Two overlays over one base](18-kustomize-base-and-overlays.md) | The generator hash is what Helm must fake with a checksum annotation. |
| 19 | [A chart with a subchart, a helper and a real conditional](19-author-a-helm-chart.md) | The capstone's input, gated by `--dry-run=server` rather than by `helm lint`. |
| 20 | [Find the release on the cluster and read it](20-helm-upgrade-and-release-state.md) | A gzipped Secret, decoded by hand, and the third merge input that is not in it. |
| 21 | [Delete something Helm created and watch nothing happen](21-helm-does-not-reconcile.md) | It converges *when you run it*, and not *because time passed*. That is the whole GitOps argument, as an experiment. |
| 22 | [1.C3 — wedge a rollout, then recover it](22-botch-a-rollout-and-roll-back.md) | Three break-shapes, ranked by how long they take to spot, with a traffic loop that counts the damage. |
| 23 | [Three services, one `helm install`, in a browser](23-the-multi-service-app.md) | **The capstone's first half.** `--wait` is the honest test, and startup ordering is what fails it. |
| 24 | [The one-page incident note](24-the-incident-note.md) | **The capstone's second half**, and the format that P6, P8 and P11 escalate. It ends the phase's cluster. |
| 25 | [One program that exercises every primer construct](25-the-go-primer-program.md) | It removes the language as a variable before P2. The race detector finds something on the first honest attempt. |
| 26 | [The CKAD drill block, as a timed harness](26-ckad-drill-block.md) | A different activity, with a different success condition: a clock, and not a mechanism. |

**One cluster runs exercises 1 through 23.**
[`pair`](../../strands/lab-topologies.md#pair) comes up at exercise 1. Exercise 24 destroys
it. Exercise 24 ends it on purpose, so that the phase's last two exercises cannot lean on
it. Exercise 25 needs **no topology at all**, because it builds on
[`forge`](../../strands/lab-topologies.md#build-guest). Exercise 26 wants a **fresh** `pair`
that it did not build.

Two things arrive mid-chain, and they stay up for the rest of the phase: **MetalLB** and
**ingress-nginx**, at exercise 14. They cost roughly 250Mi across the two nodes, and they
are the first standing cost that the worker carries. Exercise 23 is the phase's peak. Its
footprint note says what to scale down if the arithmetic gets tight.

**The CNI is Flannel, and not Cilium.**
[Exercise 1 gives the reasoning](01-provision-and-kubeadm-init.md). It is a footprint
decision, and not a preference.
