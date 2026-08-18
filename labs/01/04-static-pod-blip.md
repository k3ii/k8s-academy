<a id="static-pod-blip"></a>
# Chaos drill 1.C4 — move the apiserver's manifest out of the directory

**Claim** — the control plane is reconciled by a kubelet watching a directory, and you can prove it by making the apiserver disappear and come back without ever running a command against the apiserver.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up. [By hand, no tool](../../strands/chaos.md#principle) — and this drill has no tool form, because the thing being manipulated is a file the API server has no record of.

**Setup** — open two terminals on `.130`. One runs `sudo crictl ps --name kube-apiserver -o json | jq -r '.containers[].createdAt'` on a loop; the other does the moving. Also start `kubectl get pods -n kube-system -w` from the Mac and watch what it does when the thing serving it dies.

**Do**

1. **Predict, in writing, three things** before touching anything: how long until the container stops; what `kubectl` says while it is gone; and what happens to the *other* two static pods.
2. Move it aside, and start a clock:

   ```sh
   sudo mv /etc/kubernetes/manifests/kube-apiserver.yaml /root/
   ```

3. Watch `crictl ps` — not `kubectl`, which is about to become useless. Note the wall-clock between the `mv` and the container going away.
4. Now run `kubectl get nodes`. Read the error carefully: it is a *connection* error, not an authentication or authorisation error, and the difference is diagnostic.
5. Check whether the controller-manager and scheduler are still running. They are, and they are logging failures. `sudo crictl logs <id> --tail 20` shows what a component does when its only dependency is gone.
6. Move it back and clock the return:

   ```sh
   sudo mv /root/kube-apiserver.yaml /etc/kubernetes/manifests/
   ```

7. Afterwards, find the pod object: `kubectl get pod -n kube-system kube-apiserver-<node> -o yaml | grep -A5 ownerReferences`. Its owner is a `Node`, not a ReplicaSet, and it has no controller that could have recreated it.

**Observe**

```sh
sudo journalctl -u kubelet -f | grep -i 'static\|manifest\|kube-apiserver'
```

**Expect** — the container stops within a couple of seconds and returns within a couple of seconds; the kubelet's file watch is not a poll of minutes. `kubectl` fails with a refused connection to `:6443` for the whole window. The other two components stay *running* and keep failing to reach the apiserver — which is the shape of every control-plane outage you will diagnose later: the components are up, the thing they all talk to is not. And the mirror pod in the API is a *reflection* of the file: delete the mirror pod with `kubectl` and the container does not die, because [nothing reconciles it](13-delete-a-managed-pod.md) — the direction of authority runs from disk to API here, the opposite of everything else in this phase.

**Write down** — your three predictions with the actual timings, and one sentence on what step 7's `ownerReferences` proves about who is in charge of the control plane.

**Teardown** — put the manifest back and confirm `kubectl get nodes` answers before you leave. Nothing else was created. **The topology stays.**
