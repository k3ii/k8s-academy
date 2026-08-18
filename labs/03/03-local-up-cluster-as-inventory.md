<a id="local-up-cluster-as-inventory"></a>
# The honest inventory: what a control plane minimally is

**Claim** — `hack/local-up-cluster.sh` and your hand-wired cluster disagree about roughly a dozen flags, and every difference is either *a development shortcut* or *a thing you configured because nothing else would*. No leftovers.

**Rests on** — [the hop table](01-hand-wire-the-control-plane.md), and [P1's two-column version of this table](../../phases/01-operate-shallow.md#m1-1) — which had `local-up-cluster.sh` against kubeadm and no third column. You are now the third column.

**Topology** — **none.** [`forge`](../../strands/lab-topologies.md#build-guest) and the clone from [the flag hunt](02-every-flag-located-in-source.md). The script is **read, not run**.

**Do**

1. Pull the apiserver invocation out of the script rather than reading the whole thing:

   ```sh
   cd ~/src/kubernetes
   sed -n '/start_apiserver()/,/^}/p' hack/local-up-cluster.sh
   sed -n '/start_controller_manager()/,/^}/p' hack/local-up-cluster.sh
   sed -n '/start_kubelet()/,/^}/p' hack/local-up-cluster.sh
   ```

2. Build the three-column table — **flag · `local-up-cluster.sh` · yours** — and mark every row `both`, `dev-only`, or `yours-only`.

3. For each `dev-only` row, write what it turned *off*. For each `yours-only` row, write what would break if you removed it, and be specific: "TLS" is not an answer, "the controller-manager could no longer prove who it is, so every write it makes is anonymous" is.

4. Find the rows that are `both` but have **different values**. `--authorization-mode` is the one worth the most attention: the script's value is not a smaller version of yours, it is the absence of the mechanism.

5. One row is not a flag: locate where the script generates or skips certificates, and say in one sentence what it substitutes for the PKI you built by hand.

**Observe**

```sh
grep -n 'ALLOW_PRIVILEGED\|AUTHORIZATION_MODE\|ENABLE_ADMISSION_PLUGINS\|SERVICE_ACCOUNT' hack/local-up-cluster.sh | head -40
```

Every one of these is a shell variable with a default, which means the script's *real* flag list is a function of the environment it runs in. Note which defaults you are reading.

**Expect** — the scheduler's diff is nearly empty, which is the honest signal that the scheduler is the same program in both cases and its configuration is not where the difficulty lives. The apiserver's diff is almost entirely security and aggregation. The kubelet's diff is the one that will surprise you: it is mostly about *cgroups and the runtime*, not about the API, and it is [P6](../../phases/06-kubelet-node.md)'s subject arriving early.

**Write down** — the three tables, and one sentence: **the smallest set of flags you could delete from your cluster and still have it serve `kubectl get nodes`**. That set is what a control plane minimally is, and the distance between it and what you actually configured is the answer to why installers exist.

**Teardown** — nothing created. **No topology is up.**
