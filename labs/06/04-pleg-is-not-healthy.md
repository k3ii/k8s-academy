<a id="pleg-is-not-healthy"></a>
# Produce the error everybody has seen and nobody has caused on purpose

**Claim** — `PLEG is not healthy` is the runtime being unreachable, not the kubelet being slow: stop containerd and the message appears on a deadline you can predict to within a few seconds from the constant you cited, taking the node `NotReady` while every already-running container keeps running.

**Rests on** — [the threshold you cited](03-relist-and-the-threshold-it-checks.md). This exercise is worth nothing without that number written down first, because the whole result is *"it appeared when the constant said it would"*.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. The break happens on the worker `.131`; the control plane keeps working throughout, which is what makes the observation possible from the Mac.

**Setup** — put something on the worker that you can watch survive, and record the wall-clock:

```sh
kubectl create ns pleg-break
kubectl -n pleg-break run survivor --image=registry.k8s.io/pause:3.10 \
  --overrides='{"spec":{"nodeName":"pair-worker"}}' --restart=Never
date -u +%T
```

**Do**

1. Predict, in writing, two times: when the node condition will flip, and what happens to `survivor` when it does.

2. Stop the runtime — not the kubelet:

   ```sh
   ssh zain@10.10.10.131 'sudo systemctl stop containerd'
   ssh zain@10.10.10.131 'sudo systemctl is-active kubelet containerd'
   ```

3. Watch from the Mac and time it:

   ```sh
   kubectl get nodes -w
   ```

4. When the condition flips, take the message verbatim:

   ```sh
   kubectl get node pair-worker -o jsonpath='{.status.conditions[?(@.type=="Ready")].message}{"\n"}'
   ```

5. Ask the node what is still true while it is `NotReady`:

   ```sh
   ssh zain@10.10.10.131 'ps -o pid=,comm= -C pause | head; sudo crictl ps 2>&1 | head -3'
   ```

6. Recover, and time the recovery too:

   ```sh
   ssh zain@10.10.10.131 'sudo systemctl start containerd'
   kubectl get nodes -w
   ```

**Observe** — the kubelet log across the whole window, which is the only place the relist failure itself is visible:

```sh
ssh zain@10.10.10.131 'sudo journalctl -u kubelet --since "-6 min" | grep -iE "pleg|relist|not healthy|runtime" | tail -30'
```

**Expect** — the flip to land within a few seconds of your predicted deadline, and the message to name PLEG and a duration rather than containerd. That gap between cause and message is the operational lesson of this exercise: the error names the *observer*, not the thing that broke, which is why it sends people to read kubelet source when the answer is `systemctl status containerd`.

Expect `ps` to still show the `pause` processes. Nothing killed them: containerd's absence means nobody is *supervising* them, and a container with no supervisor is still a running process with a namespace. Recovery should be fast — one successful relist is enough to restore `Ready`, so the recovery is not symmetrical with the failure and the reason is in the same `Healthy()` you read.

**Write down** — the predicted and observed flip times, the verbatim message, and one sentence for the phase's forensic checklist: given `PLEG is not healthy`, the first command to run on the node. [Objective 4's forensics](../../phases/06-kubelet-node.md#objectives) is built out of exactly this kind of one-line reflex.

**Footprint note** — nothing is added. A stopped containerd *frees* memory on the worker for the duration, which is worth noticing: if you use this drill later as a way to make room, you are hiding a resource problem behind a broken node.

**Teardown** — confirm `systemctl is-active containerd kubelet` is `active active` on `.131` and the node is `Ready`, then `kubectl delete ns pleg-break`. **The topology stays.** A node left `NotReady` here is a phase's worth of confusing results later.
