<a id="static-pod-blip"></a>
# Chaos drill 1.C4 — move the apiserver's manifest out of the directory

**Claim** — a kubelet that watches a directory reconciles the control plane. You can prove this claim: you make the apiserver disappear and come back, and you never run a command against the apiserver.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up. Do this drill [by hand, with no tool](../../strands/chaos.md#principle). The drill has no tool form. The reason is what you manipulate: it is a file, and the API server has no record of it.

**Setup** — open two terminals on `.130`. In the first terminal, run this command in a loop: `sudo crictl ps --name kube-apiserver -o json | jq -r '.containers[].createdAt'`. Use the second terminal to move the file. Also start `kubectl get pods -n kube-system -w` from the Mac, and watch what that command does when the thing that serves it dies.

**Do**

1. **Predict three things in writing, before you touch anything.** How long until the container stops? What does `kubectl` say while the apiserver is gone? What happens to the *other* two static pods?
2. Move the manifest aside, and start a clock:

   ```sh
   sudo mv /etc/kubernetes/manifests/kube-apiserver.yaml /root/
   ```

3. Watch `crictl ps`, and not `kubectl`. `kubectl` is about to become useless. Note the wall-clock time between the `mv` and the disappearance of the container.
4. Now run `kubectl get nodes`. Read the error carefully. It is a *connection* error. It is not an authentication error, and it is not an authorisation error. That difference is diagnostic.
5. Check whether the controller-manager and the scheduler still run. They do, and they log failures. Run `sudo crictl logs <id> --tail 20`. The log shows what a component does when its only dependency is gone.
6. Move the manifest back, and clock the return:

   ```sh
   sudo mv /root/kube-apiserver.yaml /etc/kubernetes/manifests/
   ```

7. Afterwards, find the pod object: `kubectl get pod -n kube-system kube-apiserver-<node> -o yaml | grep -A5 ownerReferences`. Its owner is a `Node`, and not a ReplicaSet. It has no controller that could have recreated it.

**Observe**

```sh
sudo journalctl -u kubelet -f | grep -i 'static\|manifest\|kube-apiserver'
```

**Expect** — the container stops within a few seconds, and it returns within a few seconds. The file watch of the kubelet is not a poll of minutes. `kubectl` fails for the whole window, with a refused connection to `:6443`. The other two components stay *running*, and they keep failing to reach the apiserver. Learn that shape, because every control-plane outage that you diagnose later has it: the components are up, and the thing that they all talk to is not. Note one more fact. The mirror pod in the API is a *reflection* of the file. Delete the mirror pod with `kubectl`, and the container does not die, because [nothing reconciles it](13-delete-a-managed-pod.md). Here the direction of authority runs from disk to API, which is the opposite of everything else in this phase.

**Write down** — your three predictions, with the actual timings. Then write one sentence on what the `ownerReferences` from step 7 prove about who is in charge of the control plane.

**Teardown** — put the manifest back. Confirm that `kubectl get nodes` answers before you leave. Nothing else was created. **The topology stays.**
