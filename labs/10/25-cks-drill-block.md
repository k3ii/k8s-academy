<a id="cks-drill-block"></a>
# The CKS drill block, as a timed harness against a node you must edit

**Artifact** — a repeatable timed session, run until every task lands inside its clock twice in a row on a cluster you did not prepare — and, unlike CKA, **half the clock is spent in `ssh` and `vim` on the control-plane node**, not in `kubectl`.

**This is a different activity from every exercise above it.** Everything above optimises for mechanism — read the rule, cite the byte. This optimises for speed and correctness under a clock, and it **runs last, after [the CVE capstone](26-the-cve-incident.md)**, per [the phase's framing](../../phases/10-security.md#cks-block). Do not blend them, and **do not read source during this block.**

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), freshly provisioned, and **not** the cluster you hardened across this phase — a drill against a cluster you built is a drill against your own memory of it. Two nodes because CKS tasks touch kubelet config and node-local files on a worker as well as the control plane.

**The harness**

| | |
|---|---|
| **Clock** | Per task, below. Start it before reading the task, as the exam does. |
| **Docs** | Only [the CKS allowed list](../../strands/certs.md#cks-changes) — Falco, Cilium, Kyverno/OPA, Trivy and the k8s docs. Practising against *those exact pages* is part of the drill. |
| **Environment** | A cluster you did not prepare, context set to the wrong namespace, and a node you must `ssh` into. |
| **Pass mark** | Every task inside its clock, **twice in consecutive sessions.** One clean run is luck. |
| **Scoring** | Binary per task. A task that needed a second look did not pass, even if the object is right. |

**Three rules specific to CKS**, from [the phase block](../../phases/10-security.md#cks-block): CKS is `kubectl` *plus the node* — drill the `ssh`+`vim` edits (apiserver flags, audit policy, `EncryptionConfiguration`, kubelet config), not only the API objects; the allowed docs *are* the map, so navigate them fast; pod-to-pod encryption is both Cilium and Istio. Domains and weights are in [`certs.md#cks`](../../strands/certs.md#cks) and are **not restated here.**

**The task list** — the timed items are [the phase's own live checklist](../../phases/10-security.md#checklist), each already built once in an exercise above; the drill is doing it *under time, from memory, on an unfamiliar cluster*:

1. A least-privilege Role that denies the action just outside it, `default` SA automount off — **4 minutes**, from [exercise 1](01-one-verb-one-resource.md).
2. `restricted` PSA on a namespace + a Kyverno policy that rejects a violating pod — **5 minutes**, from [exercises 6](06-restricted-rejects-a-pod-you-can-name.md) and [7](07-kyverno-on-the-chain-you-already-read.md).
3. Write an `EncryptionConfiguration`, restart the apiserver, prove a new Secret is ciphertext on disk — **6 minutes**, a **node edit**, from [exercise 12](12-a-secret-that-is-no-longer-plaintext-on-disk.md).
4. An audit policy logging exec at `Metadata`, confirmed by one `kubectl exec` in the log — **5 minutes**, a **node edit**, from [exercise 13](13-an-exec-that-writes-a-line-to-the-audit-log.md).
5. A Kyverno `verifyImages` rule that rejects an unsigned image — **4 minutes**, from [exercise 20](20-verifyimages-rejects-the-unsigned.md).
6. A behavioral Falco rule firing on an unexpected exec in a marked container, not on a benign one — **6 minutes**, from [exercise 24](24-a-falco-rule-that-names-the-container.md).

**Expect** — tasks 3 and 4 fail first, and they fail on `vim` and manifest-restart speed rather than on recall — a mis-indented apiserver flag that takes the control plane down costs you the task and the ones after it while you recover. That is the point of the clock: CKS punishes slow, error-prone node edits harder than CKA does. Everything about weights, exam mechanics and vouchers lives in [the certs strand](../../strands/certs.md#cks) and is not repeated here.

**Write down** — per session, which tasks passed and the wall-clock for each. The trend is the signal, not any single run.

**Teardown** — `just tofu labs destroy` when the block ends. Sit the exam after this block, not before — and [the exam result is deliberately not a gate condition](../../phases/10-security.md#gate).
