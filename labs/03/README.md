# Labs — Phase 3, API machinery

Forty-five exercises in the order they are meant to run — the largest directory in the
curriculum, for the phase with the most modules and the only one that builds four
artifacts. Each states one claim to test or one artifact to produce, links its
[topology](../../strands/lab-topologies.md) rather than restating a footprint, and ends
with a teardown that does two things: **deletes what that exercise created**, then says
whether the topology stays or goes. It mostly stays —
[a provision costs minutes](../../strands/lab-topologies.md#teardown) before any teaching
happens — so most of these end in a *continuity marker* naming what comes next.

The framing — why each module exists, what to read and the question to answer from it —
stays in [`phases/03-api-machinery.md`](../../phases/03-api-machinery.md). These files hold
only what you type and what you should see.

| # | Exercise | Why it exists |
|---|---|---|
| 1 | [A control plane with no installer under it](01-hand-wire-the-control-plane.md) | The hop table is the artifact; the cluster is ephemeral and that is fine. |
| 2 | [Every flag you passed, found being read](02-every-flag-located-in-source.md) | Creates the phase's k/k clone, and makes a flag a line of code rather than a string. |
| 3 | [The honest inventory: what a control plane minimally is](03-local-up-cluster-as-inventory.md) | Read, never run — every difference from your cluster is a shortcut or a requirement. |
| 4 | [A wrong client cert fails at a nameable place](04-mis-sign-a-client-cert.md) | Opens the running list of failures that look identical from the client. |
| 5 | [An apiserver you built, started from flags](05-hand-start-an-apiserver.md) | The instrumentable apiserver the next seven exercises depend on — and the phase's footprint deviation. |
| 6 | [Four URLs, predicted before they are parsed](06-a-url-becomes-a-requestinfo.md) | `RequestInfo` is the input to authorization *and* APF, which is why it comes first. |
| 7 | [The same request, refused at two different stages](07-rejected-at-authorization-not-admission.md) | Proves admission never ran, rather than asserting it. |
| 8 | [Where validating admission is actually called from](08-the-order-of-calls-in-create-go.md) | The five log points that become the capstone trace's backbone. |
| 9 | [`resourceVersion` is etcd's `mod_revision`](09-a-precondition-becomes-a-txn.md) | Where P2's transaction turns out to have been under a familiar field all along. |
| 10 | [What is actually stored is not YAML, and not JSON either](10-one-object-read-out-of-etcd.md) | The A/B against `--storage-media-type`, and the setup for P10's encryption at rest. |
| 11 | [A kubelet may read exactly the secrets its own pods use](11-the-node-authorizer-graph.md) | The one authorizer that is a graph traversal, built by hand with no scheduler present. |
| 12 | [The fields the generic path could not have known to drop](12-what-a-strategy-decides.md) | Kept, silently dropped, explicitly refused — three writes, three behaviours. |
| 13 | [Defaults that appear and vanish with one flag](13-toggle-a-built-in-plugin.md) | Built-in admission stops being invisible the moment you switch one off. |
| 14 | [The two-method guarantee, cited and then watched](14-the-line-that-orders-the-chain.md) | `chain.go` does not prove the ordering; finding the honest citation is the exercise. |
| 15 | [Reinvocation, written as a claim before it is seen](15-why-a-mutating-webhook-reruns.md) | A prediction table written from KEP-1904, scored eight exercises later. |
| 16 | [A rejection with no network hop in it](16-a-policy-with-no-webhook.md) | The CEL half of the comparison, deliberately enforcing the same rule the webhook will. |
| 17 | [A CA, a serving cert with the right SANs, and a `caBundle`](17-a-ca-and-a-serving-cert-by-hand.md) | Every certificate mistake in the phase is made possible by having signed one yourself. |
| 18 | [Stage 1: the apiserver calls a process you are still editing](18-the-webhook-the-apiserver-dials.md) | Build artifact 1, and where `pair` is first provisioned. |
| 19 | [One SAN wrong, recognised in two minutes](19-change-one-san.md) | A timed, blind-picked drill — the checklist item, run as a drill rather than a claim. |
| 20 | [Identical semantics, two failure surfaces](20-the-same-rejection-twice.md) | Same rule, four measurable differences: the webhook-vs-VAP argument settled on evidence. |
| 21 | [Stage 2: what `clientConfig.service` actually costs](21-the-webhook-behind-a-service.md) | The ClusterRole is empty and that is the right answer. |
| 22 | [The second webhook, with the certificate handled for you](22-the-mutating-webhook-cert-manager-signs.md) | Build artifact 2, and the contrast with having done the certificates by hand. |
| 23 | [The webhook that has to run twice](23-reinvocation-observed.md) | Scores exercise 15's prediction with a second webhook that makes reinvocation necessary. |
| 24 | [Narrowing that happens before the network call](24-matchconditions-stop-the-call.md) | Adds the `academy-build` self-exclusion — the escape hatch met before it is needed. |
| 25 | [A client binary, and why it never gets a stage 2](25-a-kubectl-plugin.md) | Build artifact 3; the only one that runs on your side of the API. |
| 26 | [3.C1 — a flipped byte that blocks the write that would fix it](26-3c1-corrupt-a-cabundle.md) | The drill this phase originates: the repair path runs through the break. |
| 27 | [Two served versions, one stored, no webhook yet](27-a-two-version-crd.md) | Meets `conversion: None` pruning data, so the webhook is a fix rather than a feature. |
| 28 | [The third webhook: a different request shape entirely](28-the-conversion-webhook.md) | Build artifact 4; a list, not an object, and no allow/deny anywhere. |
| 29 | [Prove the round trip, then break it on purpose](29-a-round-trip-that-loses-nothing.md) | Data loss with no event, no condition and no error — the negative result is the finding. |
| 30 | [Where a CRD's REST storage comes from at runtime](30-how-a-crd-gets-its-storage.md) | The built-in path was compiled; this one is constructed, cached and keyed by UID. |
| 31 | [A URL path served by a process that is not the apiserver](31-an-apiservice-routes-out-of-process.md) | One broken `APIService` is a cluster-wide discovery fault; a broken CRD is not. |
| 32 | [3.C2 — every read of one resource type fails](32-3c2-garbage-from-the-conversion-webhook.md) | The deliberate contrast to 3.C1: survivable, because the repair path is not broken. |
| 33 | [`too old resource version`, produced on demand](33-overflow-the-ring.md) | Predict the ring capacity from the constants, then overflow it — twice, two ways. |
| 34 | [Two `too old` errors, one wording, different causes](34-the-same-failure-two-layers.md) | The same words at two layers, and why the wire format cannot tell them apart. |
| 35 | [A watch event that carries no object change](35-a-bookmark-advances-nothing-else.md) | Two watches side by side; only one survives the churn. |
| 36 | [Which of your reads reached etcd](36-cache-or-etcd.md) | A seven-row prediction table scored against metrics, and KEP-2340's mechanism observed. |
| 37 | [Two owners, one field, one conflict](37-managedfields-and-a-conflict.md) | Three ways to resolve a `409`, each changing ownership differently. |
| 38 | [Naming the FlowSchema for a request you sent](38-which-flowschema-caught-the-request.md) | APF is predictable from the request alone, and the apiserver returns the answer in a header. |
| 39 | [3.C3 — one client, one priority level, everyone in it queued](39-3c3-starve-an-apf-priority-level.md) | The distinguisher decides fairness; concurrency shares decide capacity. Getting those the wrong way round is the outage. |
| 40 | [3.C4 — the apiserver stops; the controllers do not](40-3c4-apiserver-down-controllers-up.md) | The level-triggered payoff, produced as evidence P4 can reason from. |
| 41 | [3.C5 — x509 from the inside](41-3c5-an-expired-component-certificate.md) | Closes the look-alike list at three rows, and shows a dead controller-manager as a cluster that ignores your writes. |
| 42 | [One binary, four components, no manifests you wrote](42-k0s-in-one-binary.md) | The seams are hidden, not gone — and `/var/lib/k0s/bin` proves it. |
| 43 | [Kill one process, lose four components](43-kill-the-one-process.md) | Same fault, three architectures, three blast radii. |
| 44 | [Three control planes, compared from your own notes](44-three-control-planes.md) | Objective 8's deliverable: what each makes easy, and what each makes invisible. |
| 45 | [The capstone: one `kubectl apply`, cited end to end](45-the-capstone-trace.md) | Graded on whether the citations survive a hostile reader, not on whether the cluster serves. |

## Which cluster is running when

**Exercises 1 to 16 need no topology at all** — the whole of modules 3.0 to 3.2 runs in a
browser playground and on [`forge`](../../strands/lab-topologies.md#build-guest), where
exercise 5 stands up a single-member etcd and an apiserver you compiled. That is deliberate:
it defers the phase's first provision to exercise 18 and leaves the entire ceiling free
during the heaviest build.

[`pair`](../../strands/lab-topologies.md#pair) comes up at **exercise 18** and runs through
**exercise 41** — modules 3.3, 3.4 and 3.5 on one cluster, twenty-four exercises, three
webhooks and a CRD accumulating on it. It is destroyed at the end of exercise 41 so that
[`k0s-light`](../../strands/lab-topologies.md#k0s-light) (exercises 42 to 44) is met against
a clean machine, which is the entire point of module 3.6. The capstone re-provisions `pair`;
[exercise 45's footprint note](45-the-capstone-trace.md) argues that trade and names the
alternative it rejected.

**Peak cost is module 3.3**: `pair` at 5.0GB plus `forge` at 2560MB, against the
[9.5GB ceiling](../../strands/lab-topologies.md#ceiling) — 2.0GB of margin, the tightest in
the phase and comfortably inside it. Modules 3.4 and 3.5 are the same 5.0GB with three small
Go Deployments and `cert-manager` inside the cluster's own memory rather than beside it.
Module 3.6 costs 2.0GB and nothing else.

**One deviation from the standing footprint, flagged rather than softened:**
[`forge`](../../strands/lab-topologies.md#build-guest) is raised from 1536MB to 2560MB at
[exercise 5](05-hand-start-an-apiserver.md) and stays there for the whole phase, because
linking `cmd/kube-apiserver` with `-gcflags=all="-N -l"` does not fit in 1536MB against the
measured `kube-scheduler` figure. [Exercise 45](45-the-capstone-trace.md) puts it back.

## Exceptions

- **Exercises 1, 3 and 4** run in a browser playground with zero RAM cost; the artifact is the map, not the cluster.
- **Exercise 15** is reading only — a prediction written down and scored at exercise 23.
- **Exercise 30** reads on `forge` while `pair` stays up, and touches the cluster only for a one-line check.
- **Exercise 31** fakes an extension apiserver as four routes on an existing Deployment, and its footprint note says exactly what that substitution skips.
- **Exercise 44** creates nothing; the table is the artifact.
