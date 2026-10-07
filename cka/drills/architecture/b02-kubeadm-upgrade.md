<a id="b02"></a>
# B2 — `kubeadm upgrade`: control plane first, then the node, with a drain around it

**Build** · **Pinned** · **60 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Cluster Architecture, Installation and Configuration / Manage cluster lifecycle

> **Upgrade is an ordering exercise.** Every individual command is short; the marks are in doing them in the right order on the right node, and in remembering that the node you are upgrading has to be drained first and uncordoned after. The order is: `kubeadm` the binary, then `kubeadm upgrade plan`, then `apply` on the control plane, then per node — drain, upgrade `kubeadm`, `upgrade node`, upgrade `kubelet` and `kubectl`, restart, uncordon.

> **There is something to upgrade to, and it is a patch.** Measured on 1 Oct: the cluster runs `1.37.0-1.1` and the pinned repo also offers `1.37.1-1.1`. So the full workflow is rehearsable here **without changing the apt repo line** — which is a trap, because the exam's upgrade is a *minor* one and the repo change is a scored step. Do the patch upgrade for the mechanics, then separately rehearse the repo edit and the `apt-mark unhold` / `hold` dance around it, so the muscle memory includes the step this cluster does not force on you.

**Do**

1. `kubeadm upgrade plan`. Read it rather than skimming it: it states what each component goes to, and it is where a version skew problem announces itself.
2. The control plane, first and alone. `apt-mark unhold kubeadm`, install the target version, `kubeadm upgrade apply <version>`, re-hold. Note that `kubeadm upgrade apply` does **not** touch the kubelet — that is a separate step people routinely miss, and the node then reports the old version indefinitely.
3. The kubelet and kubectl on that same node, then `systemctl daemon-reload && systemctl restart kubelet`.
4. **Now the worker, and drain it first.** `kubeadm upgrade node` — not `apply`, which is control-plane-only. Then its kubelet, then restart, then **uncordon**.
5. Confirm. `kubectl get nodes` showing the new version on both is the whole result, and a node left cordoned is a failed task even if the version is right.

**Observe**

```sh
sudo kubeadm upgrade plan
sudo apt-mark unhold kubeadm && sudo apt-get install -y kubeadm=<ver> && sudo apt-mark hold kubeadm
sudo kubeadm upgrade apply v<ver>
kubectl drain <node> --ignore-daemonsets
sudo kubeadm upgrade node
kubectl uncordon <node>
kubectl get nodes -o wide
```

**Done when** — both nodes report the new version, both are `SchedulingDisabled`-free, and every `kube-system` pod is running.

**Done in one sitting.** The dangerous failure is stopping halfway, with a control plane ahead of its kubelet. If time runs out, finish the node you started.

**Teardown** — none. The cluster stays upgraded; [the baseline](../../baseline.md#versions) records the versions from before, so update your own notes rather than the baseline, which is a dated snapshot and not a live document.

**See also** — **TS3** is the drain half of this on its own, against a PDB that refuses. **B1** is what you are upgrading.
