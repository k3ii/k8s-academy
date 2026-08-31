<a id="sample-controller-against-a-real-cluster"></a>
# The Rosetta Stone, running against a cluster you can break

**Artifact** — `sample-controller` compiled on [`forge`](../../strands/lab-topologies.md#build-guest) and running against a live cluster, with its `Foo` CRD installed, one `Foo` created, and the `Deployment` it produced running on the worker node. This process stays up for the next two exercises.

**Rests on** — [the two cited lines](02-the-line-that-enqueues-a-key.md). You have read this controller; now it runs, and every log line it prints maps to a line you can point at.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), **freshly provisioned — this is the phase's first cluster.** The provisioning commands are [in the strand](../../strands/lab-topologies.md#provision) and are not repeated here; `ssh hopper` is mandatory and `just gate` is not optional. [Kubernetes is yours to install on the guest](../../strands/lab-topologies.md#node-baseline-steps), as it was in [`labs/01/01`](../01/01-provision-and-kubeadm-init.md). That applies to every exercise in this directory and is stated there once.

`pair` runs every exercise from here to [the capstone](34-the-capstone-writeup.md), with three exercises in between that use no cluster at all and say so.

**Setup**

1. Give `forge` a kubeconfig for the new cluster:

   ```sh
   ssh zain@10.10.10.125
   mkdir -p ~/.kube && ssh zain@10.10.10.130 'sudo cat /etc/kubernetes/admin.conf' > ~/.kube/config
   kubectl get nodes
   ```

2. Build the controller from the tree you cited in [exercise 2](02-the-line-that-enqueues-a-key.md), so the running binary and the line numbers are the same code:

   ```sh
   cd ~/src/kubernetes/staging/src/k8s.io/sample-controller
   go build -o ~/sample-controller .
   ```

   The staging modules carry `replace` directives to their siblings, which is why this builds in place. If the module graph refuses, clone `kubernetes/sample-controller` at the tag matching your sha and build that — same code, different packaging.

**Do**

1. Install the CRD and confirm the API server serves it:

   ```sh
   kubectl apply -f artifacts/examples/crd.yaml
   kubectl api-resources --api-group=samplecontroller.k8s.io
   ```

2. Start the controller in the foreground and keep the terminal:

   ```sh
   ~/sample-controller -kubeconfig=$HOME/.kube/config -v=2
   ```

3. In a second session on `forge`, create a `Foo` asking for one replica:

   ```sh
   kubectl apply -f artifacts/examples/example-foo.yaml
   kubectl get foo example-foo -o yaml
   kubectl get deploy,pods -o wide
   ```

4. Now do the thing that separates a controller from a script. Delete the `Deployment` it made, and do not touch the `Foo`:

   ```sh
   kubectl delete deploy example-foo && sleep 5 && kubectl get deploy
   ```

**Observe** — the controller's log at each of the four moments: startup, `Foo` created, `Deployment` created, `Deployment` deleted by you.

**Expect** — the `Deployment` comes back. Nothing you did asked for it: there was no create request, no retry loop of yours, and the `Foo` never changed. The delete produced a watch event on a *Deployment*, the controller's second event handler mapped that object to its owner's key, and the same `syncHandler` ran again and found actual ≠ desired.

Two details worth catching now, because they are load-bearing later:

- the pod count reported in `foo.status.availableReplicas` lags the `Deployment` by a moment and then settles — that is a **status subresource** being written by a second, later reconcile, not by the same one;
- the log at startup shows a burst of activity *before* you created anything. That burst is the initial LIST arriving as events, and it is [exercise 11's](11-what-hassynced-actually-promises.md) subject.

This resurrection is the same behaviour [P1](../../phases/01-operate-shallow.md) showed you from the outside when a Deployment's pods came back, and the same one the Helm comparison in [the ecosystem note](../../phases/04-controllers.md#ecosystem) turns on. The difference is that you can now open the file that does it.

**Write down** — nothing yet. [Exercise 4](04-five-log-lines-five-stages.md) is where this run produces its artifact.

**Footprint note** — [`pair`](../../strands/lab-topologies.md#pair) at 5.0GB plus [`forge`](../../strands/lab-topologies.md#build-guest) at 1536MB is 6.5GB of [the 9.5GB ceiling](../../strands/lab-topologies.md#ceiling), and that is the phase's steady state: no exercise in `labs/04/` adds a node, and the only thing that grows is the number of small Go processes on `forge`. The one place that gets tight is [`envtest`](16-envtest-is-a-real-apiserver.md), which has its own note.

**Teardown** — leave the controller running and leave the `Foo` in place; [the next exercise](04-five-log-lines-five-stages.md) instruments this same binary. **The topology stays.**
