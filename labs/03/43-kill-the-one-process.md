<a id="kill-the-one-process"></a>
# Kill one process, lose four components

**Claim** — `kill`ing the k0s supervisor stops the entire control plane at once, and killing one of its children does not — the supervisor restarts it; on the hand-wired cluster you can stop exactly one component and name precisely what stops with it. Same fault, two architectures, two blast radii.

**Rests on** — [the k0s install](42-k0s-in-one-binary.md), and [the apiserver-down drill](40-3c4-apiserver-down-controllers-up.md), which is the kubeadm half of this comparison and was run on a cluster that no longer exists — so the evidence you need from it is what you wrote down there.

**Topology** — [`k0s-light`](../../strands/lab-topologies.md#k0s-light), continued.

**Do**

1. Establish the baseline: a Deployment with 2 replicas, and a terminal running `sudo k0s kubectl get pods -w`.

2. Kill a **child** first, because the prediction is less obvious than it looks:

   ```sh
   ps -ef --forest | grep -E 'kube-scheduler|kube-controller-manager'
   sudo kill <the kube-scheduler pid>
   ```

   Time how long until a scheduler is running again. Then do the same to `kube-apiserver` and record whether the two behave the same.

3. Now kill the **supervisor**:

   ```sh
   sudo systemctl stop k0scontroller     # the graceful form
   ps -ef | grep -c 'k0s\|kube-'
   sudo k0s kubectl get nodes            # predict first
   ```

   Then restart, and do it again ungracefully — `sudo kill -9` on the supervisor PID — and note whether the children survive their parent. That is a real question about process supervision, not a rhetorical one; check `ps` rather than assuming.

4. Scale the Deployment while the control plane is down, or try to. Then check whether the *workload* survived at all:

   ```sh
   sudo crictl ps | grep nginx
   ```

5. Restart and time full recovery to `sudo k0s status` reporting healthy and `get nodes` returning `Ready`.

6. Write the comparison. Three rows, from three different clusters, two of them from your notes:

   | Cluster | Smallest thing you can stop | What stops with it | What keeps working |
   |---|---|---|---|
   | Hand-wired ([3.0](01-hand-wire-the-control-plane.md), [3.1](05-hand-start-an-apiserver.md)) | | | |
   | kubeadm ([3.C4](40-3c4-apiserver-down-controllers-up.md)) | | | |
   | k0s (here) | | | |

**Observe**

```sh
sudo journalctl -u k0scontroller -f
ps -ef --forest | sed -n '/k0s/,$p'
sudo crictl ps
```

**Expect** — a killed child comes back in seconds, supervised, with no manual step: the supervisor is doing what the kubelet does for static pods on a kubeadm cluster, and noticing that those are the *same role played by different software* is the sentence worth extracting.

Killing the supervisor takes everything. Whether the children are reaped with it depends on how they are supervised, and finding the answer by looking is more instructive than being told — check `ps` after `kill -9` before drawing any conclusion.

The workload keeps running throughout. Containers already started do not need a control plane, on any of the three architectures. That is the same finding as [step 4 of the apiserver drill](40-3c4-apiserver-down-controllers-up.md) arriving from a different direction, and it is the most durable thing in the module: **the control plane is the thing that makes changes, not the thing that keeps things running.**

**Write down** — the comparison table from step 6, the child-restart interval, the `kill -9` result, and the recovery time.

**Teardown** — delete the Deployment, confirm the control plane is healthy. **The topology stays** — [the three-control-planes write-up](44-three-control-planes.md) is the last thing that touches it.
