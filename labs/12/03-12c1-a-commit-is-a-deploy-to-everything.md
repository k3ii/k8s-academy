<a id="12c1-a-commit-is-a-deploy-to-everything"></a>
# 12.C1 — a bad commit reconciles everywhere at once: the GitOps blast radius, and a rotated secret every consumer already cached

**Claim** — push one bad manifest to the git repo and every `Kustomization` watching it applies the breakage on its next reconcile, with no second gate between commit and cluster — the flip side of "git is the source of truth" is that **a mistake you commit is a mistake you deploy to everything.** Then rotate a SOPS-encrypted secret and watch consumers that cached the old value keep using it until they restart: the source of truth changed and the running system did not. This drill's first half is the phase's signature failure mode; recognising your own commit's consequence from the system's behaviour is the skill.

**Rests on** — [the Flux install and delivery path](01-gitops-the-reconcile-loop-you-already-wrote.md); [the drift beat](02-drift-detection-off-by-default.md), whose `mode: enabled` is this drill's setup (drift-on is what makes the revert observable); and [the secrets exercise](04-three-ways-to-not-commit-a-secret.md) for the SOPS half.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), continued.

**Read** — [the drill's chaos-table row](../../phases/12-gitops-platform.md#chaos) and [the manual-drills standard](../../strands/chaos.md#manual-drills). By hand, because the fault is a *commit* — the whole point is that the failure travels the same path a good change does, with nothing distinguishing them until the cluster reacts.

**Do** — commit a manifest that cannot work (a bad image tag, an invalid field), and watch it spread; then rotate a secret without restarting its consumers:

```sh
# the blast radius: one commit, every reconciler applies it
git -C <repo> commit -am 'break the image tag' && git -C <repo> push
flux reconcile kustomization demo --with-source
kubectl get pods -w        # the breakage appears wherever the app runs — no staging gate caught it
# recover the GitOps way: revert the commit, let reconciliation heal
git -C <repo> revert --no-edit HEAD && git -C <repo> push
flux reconcile kustomization demo --with-source
# the stale-cache half: rotate the SOPS secret, leave consumers running
kubectl get pods -l app=<consumer>      # still Running on the old value until a restart re-reads it
```

**Observe** — the bad commit reaching the workload with no human approval between push and apply, and the revert healing it the same way; then the rotated secret leaving already-running pods on the previous value, because a `Secret` change is not a rollout — nothing told the pods to re-read it. Two distinct GitOps truths: the repo is a blast radius, and "the source of truth changed" is not "the system changed."

**Expect** — recovery that is itself a GitOps test: the cluster returns from a reverted commit, proving reconciliation heals as readily as it breaks. If you fixed it with `kubectl edit` instead of a revert, you proved git was *not* the source of truth — do it again through the repo.

**Write down** — one sentence on why a committed mistake is a deployed mistake, and one on what a secret rotation does *not* do to a running pod — the two failure modes that make git-as-truth a double-edged guarantee.

**Teardown** — the reverted commit already restored the app; confirm the consumers are healthy and the secret consumers restarted onto the new value. **The topology stays.**
