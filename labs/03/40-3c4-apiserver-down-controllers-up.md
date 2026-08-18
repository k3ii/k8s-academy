<a id="3c4-apiserver-down-controllers-up"></a>
# 3.C4 — the apiserver stops; the controllers do not

**Claim** — with `kube-apiserver` stopped, `kube-controller-manager` and `kube-scheduler` keep running as processes and stop acting entirely; on recovery they resync from scratch rather than replaying what they missed, and you can prove they missed something by changing the world while the apiserver was down.

**Rests on** — [the watch and cache work](33-overflow-the-ring.md) of module 3.5. This is the drill the phase points forward from: what a controller does when its watch drops is [P4](../../phases/04-controllers.md)'s subject, and this produces the evidence P4 reasons about.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Everything happens on the control-plane node `.130` and the worker `.131`.

**Setup** — the escape hatch is the manifest directory itself: `kube-apiserver` is a static pod, so the kubelet restarts it as soon as its manifest is back. Move the file, do not delete it:

```sh
ssh zain@10.10.10.130 'sudo mkdir -p /root/parked'
```

Have a `Deployment` running with `replicas=2` in a namespace you can watch, and a `sleep` pod on `.131` you can kill by hand.

**Do**

1. Record the state you expect to be restored to: `kubectl get pods -o wide -n drill > /tmp/before.txt`.

2. Stop the apiserver, and only the apiserver:

   ```sh
   ssh zain@10.10.10.130 'sudo mv /etc/kubernetes/manifests/kube-apiserver.yaml /root/parked/'
   ssh zain@10.10.10.130 'sudo crictl ps | grep -E "apiserver|controller-manager|scheduler|etcd"'
   ```

   Confirm from that second command what is still running. This is the whole premise of the drill and it is worth two seconds of looking.

3. Read what the survivors say. Do not `kubectl logs` — there is no apiserver:

   ```sh
   ssh zain@10.10.10.130 'sudo crictl logs -f $(sudo crictl ps -q --name kube-controller-manager) 2>&1 | tail -40'
   ssh zain@10.10.10.130 'sudo crictl logs $(sudo crictl ps -q --name kube-scheduler) 2>&1 | tail -20'
   ```

   Look for two things: the connection errors, and what happens to their **leader election**. Find the lease duration and work out how long they will keep believing they are leader.

4. Change the world while nobody is watching. On `.131`:

   ```sh
   ssh zain@10.10.10.131 'sudo crictl ps | grep sleep'
   ssh zain@10.10.10.131 'sudo crictl stop <the sleep container id>'
   ```

   Predict: does the kubelet restart it? Does anything reschedule it? Are those the same question?

5. Restore, and time it:

   ```sh
   ssh zain@10.10.10.130 'sudo mv /root/parked/kube-apiserver.yaml /etc/kubernetes/manifests/'
   time kubectl get --raw /readyz
   ```

6. Watch the recovery rather than checking it after the fact:

   ```sh
   kubectl get events -A --sort-by=.lastTimestamp | tail -30
   kubectl get pods -o wide -n drill
   ```

**Observe** — the controller-manager's log across the whole outage and the first 60 seconds after, and:

```sh
kubectl get leases -n kube-system -o custom-columns=NAME:.metadata.name,HOLDER:.spec.holderIdentity,RENEW:.spec.renewTime
kubectl get --raw /metrics | grep -E 'workqueue_depth|reflector' | head
```

**Expect** — the controller processes stay up and log connection refusals in a retry loop. They do **not** exit, and this is a deliberate design choice you should be able to defend: a controller that exited on apiserver unavailability would turn a brief control-plane blip into a full restart storm.

The kubelet restarts your killed container from its own static state without asking anyone, because the kubelet is level-triggered against its own pod manifests and does not need the apiserver to keep a pod running. Nothing *reschedules* it, because rescheduling requires the apiserver. Those being two different questions with two different answers is the finding of step 4.

On restore, the controllers reconnect and **re-list**. There is no replay: they observe the current state and reconcile toward the desired state, so an event they missed costs them nothing as long as the *state* is still visible. That sentence is the level-triggered payoff the phase promises, and it should be written down from the evidence, not from the concept.

The lease detail is the sharpest part: the leases went unrenewed for the whole outage, so on reconnect the holders must reacquire, and there is a window where nothing holds them. Check whether the same instance reacquired and how long it took.

**Write down** — the survivors list from step 2, the two answers from step 4, the recovery time, the lease behaviour, and one sentence for [P4](../../phases/04-controllers.md) stating what "level-triggered" bought here in terms of what did *not* have to be recorded.

**Teardown** — confirm `/root/parked` is empty and the manifest is back. Delete the drill namespace. Confirm all control-plane pods are `Running` and `kubectl get --raw /readyz` returns `ok`. **The topology stays** — [the certificate drill](41-3c5-an-expired-component-certificate.md) is the last exercise on this cluster.
