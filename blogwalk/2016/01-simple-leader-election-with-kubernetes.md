<a id="simple-leader-election-with-kubernetes"></a>
# The trick in this post is now an API kind, and the object it borrowed is deprecated

**Post** — [Simple leader election with Kubernetes and Docker](https://kubernetes.io/blog/2016/01/simple-leader-election-with-kubernetes/),
2016-01-11, Kubernetes v1.1 — six months after 1.0.

**As written** — you do not need ZooKeeper, etcd or Consul to elect a leader among your
replicas, because two properties of *every* Kubernetes API object are already enough:

> * ResourceVersions - Every API object has a unique ResourceVersion, and you can use these
>   versions to perform compare-and-swap on Kubernetes objects
> * Annotations - Every API object can be annotated with arbitrary key/value pairs to be used by
>   clients.

The candidate set is an **Endpoints** object, chosen deliberately over a ReplicationController
because "they are tied to a specific binary, and generally you want to have a single leader even
if you are in the process of performing a rolling update". Run three racers:

```
$ kubectl run leader-elector --image=gcr.io/google_containers/leader-elector:0.4 --replicas=3 -- --election=example
```

Read the winner from a pod's logs, or from the object directly — "'example' is the name of the
candidate set from the above kubectl run … command":

```
$ kubectl get endpoints example -o yaml
```

Kill the leader with `kubectl delete pods (leader-pod-name)`; the replication controller replaces
it, the survivors re-race, and failover takes "30-40 seconds" because of the pod grace period.
Then the second half: rerun with `--http=0.0.0.0:4040` so each member serves the leader's name as
JSON, and reach it through the API server —

```
http://localhost:8001/api/v1/proxy/namespaces/default/pods/(leader-pod-name):4040/
```

— which returns `{"name":"(name-of-leader-here)"}`. Any container in the pod can now ask
`http://localhost:4040` who the leader is, "since all containers in a Pod share the same network
namespace, there's no service discovery required!"

**As it runs now** — four fates, and the first two are the honest kind:

1. **The command hard-errors, in the client.** `kubectl run` has no `--replicas` flag; the pin's
   reference gives its whole synopsis as
   `kubectl run NAME --image=image [--env="key=value"] [--port=port] …` and describes it as
   "Create and run a particular image in a pod" — singular. It creates a Pod and nothing else, so
   the post's `kubectl delete rc leader-elector` has nothing to delete either.
2. **The image does not pull.** `gcr.io/google_containers` is two registry migrations behind:
   that host, then `k8s.gcr.io`, then `registry.k8s.io`. Do not take the failure on trust — step 3
   makes the kubelet say it.
3. **The URL is accepted and 404s.** `kubectl proxy` still works and the pod proxy subresource
   still exists, but the `proxy` segment moved from *before* the namespace to *after* the resource
   name: the pin writes `/api/v1/namespaces/default/pods/$POD_NAME:8080/proxy/`. The post's shape
   is not an old spelling of a live route; it is a path the API server does not serve at all.
4. **The two primitives are both still there, and only one of them is still the answer.**
   Compare-and-swap on `resourceVersion` is exactly how leader election is implemented today —
   step 7 makes the server prove it. Annotations as the place the winner is recorded is what got
   replaced, because a typed object arrived that means it.

**The diff, and why** — the post is not wrong about the mechanism. It is wrong about there being
nothing to install, in the same way that a hand-rolled linked list is not wrong about pointers.

Leader election is now `Lease` in `coordination.k8s.io/v1`, and what a `Lease` adds over an
annotation is a *schema for the thing everyone was already writing*: `holderIdentity`,
`acquireTime`, `renewTime`, `leaseDurationSeconds` — the post's "heartbeat to renew their
position" as four fields instead of a blob a client has to agree with itself about — plus
`leaseTransitions`, a counter of how many times the lease has changed hands, which no annotation
scheme ever bothered to keep. The control plane runs on it: `kube-controller-manager` and
`kube-scheduler` elect through Leases in `kube-system`, and every kubelet heartbeat is an update
to a Lease in `kube-node-lease`. The pin's own advice for your workload is the post's advice with
the object swapped — "you might run a custom controller where a primary or leader member performs
operations that its peers do not. You define a Lease so that the controller replicas can select
or elect a leader."

The borrowed object, meanwhile, lost. `Endpoints` is deprecated as of v1.33, and its reference at
the pin opens on it: *"Deprecated: This API is deprecated in v1.33+. Use
discoveryv1.EndpointSlice."* The reasons are nothing to do with leader election — no dual-stack,
no `trafficDistribution`, and it "will truncate the list of endpoints if it is too long to fit in
a single object" — which is the price of having repurposed a Service-shaped object as a lock:
when the thing it was actually for outgrew it, the lock went down with it. That is the pressure
the post's cleverness could not see, and the reason a lock now has a kind of its own.

The part still being negotiated is *who gets to decide the winner*. Ordinary Lease election is
first-past-the-post: whoever wins the compare-and-swap holds it. Coordinated leader election adds
a `strategy` field and a `preferredHolder`, so the control plane can ask a holder to *give the
lease up* to a better candidate — during a skewed upgrade, the oldest-version instance. Its gate:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.31 – v1.32 |
| beta | `false` | — | v1.33 – |

Two rows, and the second one is the finding: **beta since v1.33 and still off by default at the
pin** — five releases of beta that nobody's cluster has switched on. The two sources disagree
about even that. `CoordinatedLeaderElection.md`'s frontmatter says `stage: beta`; the `Lease`
reference, at the same commit, documents `spec.strategy` as "(Alpha) Using this field requires the
CoordinatedLeaderElection feature gate to be enabled." Cite both, and note which one a reader
would have found first.

Release facts and the pressure behind each one are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

**Topology** — [`ha`](../../strands/lab-topologies.md#ha), fresh: three stacked control planes are
the only way to watch a control-plane lease change hands rather than be told that it does. Bring
it up with [the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=ha`, install Kubernetes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), then
`ssh zain@10.10.10.150`.

**Do**

1. Run the post's command exactly as written. Record the error verbatim, and note which process
   produced it — nothing reached the API server.

   ```sh
   kubectl run leader-elector --image=gcr.io/google_containers/leader-elector:0.4 --replicas=3 -- --election=example
   ```

2. Ask what `kubectl run` does create, then look for what the post assumed it created:

   ```sh
   kubectl run leader-elector --image=gcr.io/google_containers/leader-elector:0.4 -- --election=example
   kubectl get rc
   kubectl get pod leader-elector -o jsonpath='{.metadata.ownerReferences}'; echo
   ```

3. Now find out whether the image is the second failure or only the first one restated:

   ```sh
   kubectl get pod leader-elector
   kubectl describe pod leader-elector | tail -15
   ```

   Write down the message. Then delete the pod: `kubectl delete pod leader-elector`.

4. Look for the object the post parks the leader in, and then for the object itself:

   ```sh
   kubectl get endpoints example
   kubectl api-resources | grep -iE 'endpoint'
   kubectl explain endpoints | head -8
   ```

5. Read the live election. Three control planes, one holder each for two components:

   ```sh
   kubectl -n kube-system get leases
   kubectl -n kube-system get lease kube-scheduler -o yaml
   kubectl get leases -A -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,HOLDER:.spec.holderIdentity,TRANSITIONS:.spec.leaseTransitions
   ```

   The holder identity begins with a node name. Which node holds the scheduler, and is it the same
   one holding the controller manager?

6. Take the leader away and watch, rather than waiting to be told. In one terminal:

   ```sh
   kubectl -n kube-system get lease kube-scheduler -o jsonpath='{.spec.holderIdentity}{"  t="}{.spec.leaseTransitions}{"\n"}' --watch
   ```

   In another, delete the scheduler on the node from step 5 —
   `kubectl -n kube-system delete pod kube-scheduler-<that-node>` — and time the handover against
   the post's "30-40 seconds". Compare `leaseDurationSeconds` on the object with what you measured.

7. **The compare-and-swap, on a modern object.** This is the post's first primitive, unchanged:

   ```sh
   kubectl create -f - <<'YAML'
   apiVersion: coordination.k8s.io/v1
   kind: Lease
   metadata:
     name: my-app
   spec:
     holderIdentity: candidate-a
     leaseDurationSeconds: 15
   YAML
   kubectl get lease my-app -o yaml > candidate-b.yaml
   kubectl patch lease my-app --type=merge -p '{"spec":{"holderIdentity":"candidate-a-renewed"}}'
   sed -i 's/candidate-a/candidate-b/' candidate-b.yaml
   kubectl replace -f candidate-b.yaml
   ```

   Candidate B read the object, candidate A renewed first, and B is now writing back what it read.
   Record the exact status and message the server returns, and find the field in `candidate-b.yaml`
   that made it possible for the server to notice.

8. Ask whether the coordination half is even on:

   ```sh
   kubectl get --raw /metrics | grep -c 'kubernetes_feature_enabled.*CoordinatedLeaderElection'
   kubectl get --raw /metrics | grep 'kubernetes_feature_enabled.*CoordinatedLeaderElection'
   kubectl api-resources | grep -i leasecandidate
   ```

   Then read `spec.strategy` in `kubectl explain lease.spec` and set it against the ladder above.

**Expect** — step 1 fails with `unknown flag: --replicas` before any request is made; `kubectl`
rejected it locally, so no `leader-elector` anything exists. Step 2 gets `No resources found in
default namespace.` from `kubectl get rc` and an empty `ownerReferences`: a bare Pod, owned by
nothing, which is why the post's `kubectl delete rc` line was already dead before the flag was.

Step 3 is the second failure and a real one: `ErrImagePull` or `ImagePullBackOff`, and the
`describe` events name the host that does not answer. Two independent breakages in one line of
2016 shell.

Step 4 finds `endpoints` still served in `v1` alongside `endpointslices` in `discovery.k8s.io/v1`,
and `kubectl explain` reads out the sentence the reference opens with:
`Deprecated: This API is deprecated in v1.33+. Use discoveryv1.EndpointSlice.` The `example`
object is `NotFound` — nothing created it, and nothing would.

Step 5 lists at least `kube-controller-manager` and `kube-scheduler` in `kube-system`, one Lease
per node in `kube-node-lease`, and `apiserver-<hash>` Leases if API server identity is on. The two
control-plane components need not agree on a holder; there is no cluster-wide leader, only a
leader per component.

Step 6 is the exercise. `leaseTransitions` increments by exactly one and `holderIdentity` changes
to another node's — and the handover is *faster* than the post's 30–40 seconds, because it is
bounded by `leaseDurationSeconds` on the object rather than by a pod's grace period. Read
`leaseDurationSeconds` and say which of the two numbers you should have predicted from.

Step 7 fails with `409 Conflict` and the phrase `the object has been modified; please apply your
changes to the latest version and try again`. That is the post's compare-and-swap, eleven years
later, on a kind that did not exist when it was written; the field the server compared is
`metadata.resourceVersion`, and every leader election in the cluster is that 409 happening to the
loser.

Step 8: `kubernetes_feature_enabled` reports `CoordinatedLeaderElection` present with value `0`,
`leasecandidates` may not appear in `api-resources` at all, and `explain` calls `strategy` alpha
while the gate file calls it beta. Write down which of the three you would trust and why.

**Read on** — `client-go`'s `tools/leaderelection/leaderelection.go` in `kubernetes/client-go`:
find what it does when its update returns the conflict from step 7, and say why that single branch
is the whole election. Then find where it decides it has *lost* the lease rather than merely
failed to renew it — a distinction the post does not make, and the one that decides whether your
two replicas are briefly both leaders.

**Teardown** — `kubectl delete lease my-app`, and let the scheduler you deleted come back
(`kubectl -n kube-system get pods | grep scheduler` — three of three Running). Leave the three
guests up; a multi-node topology is expensive to rebuild and the next exercise in this year uses
one.
