<a id="introducing-kubernetes-v1beta3"></a>
# Every version in this post is dead, and every rename in it is still law

**Post** — [Introducing Kubernetes API Version v1beta3](https://kubernetes.io/blog/2015/04/introducing-kubernetes-v1beta3/),
2015-04-16, Kubernetes v0.15 — three months before 1.0.

**As written** — move to `v1beta3` now. It is "the release candidate for the v1 API"; `v1beta1`
and `v1beta2` are deprecated and "will be removed by the end of June". As of v0.15.0 it is the
primary and default API for the server, for `kubectl` and for the client, and it is also the
**etcd storage version** — so "objects persisted in etcd will be converted from v1beta1 to
v1beta3 as they are rewritten."

Then a migration list. Thirteen renames, of which these are the ones you will meet:

- `id` is now called `name`, and `name`, `labels` and `annotations` are nested in a map called
  `metadata`
- `desiredState` is now `spec`, `currentState` is now `status`
- `/minions` has moved to `/nodes`, and the resource has kind `Node`
- the namespace is required and has moved from a URL parameter into the path:
  `/api/v1beta3/namespaces/{namespace}/{resource_collection}/{resource_name}`
- collection names are lower-cased — `replicationcontrollers`, not `replicationControllers`
- the container's `entrypoint` is now `command`, and `command` is now `args`
- resources are nested maps with scaling suffixes (`resources{cpu:1}`), not fields in fixed
  scales
- restart policy is a string (`"Always"`), not a nested map (`always{}`)
- a volume's `source` is inlined into the volume, and `hostDir` becomes `hostPath`
- to watch, open an HTTP or WebSocket connection to the collection URL with `?watch=true` and a
  `resourceVersion`

It closes with two pieces of tooling advice: use the conversion tool, and because the default
version changed under `kubectl`, "always explicitly specify the API version rather than relying
upon the default" when using `-o template`.

**As it runs now** — three different fates, and telling them apart is the exercise:

1. **It hard-errors.** `v1beta1`, `v1beta2` and `v1beta3` are all gone from the API server.
   `v1beta3` did not survive its own release-candidate status by four weeks: v0.16.0, three and
   a half weeks after this post, carries the changelog line *"Cloning v1beta3 as v1 and exposing
   it in the apiserver"*.
2. **The tooling is gone.** `kubectl convert`, the conversion tool this post points at, was
   deprecated in v1.13 and removed in **v1.20**.
3. **Every rename in the list is still exactly the API you wrote a manifest against this
   morning.** `metadata`, `spec`, `status`, `nodes`, `command`/`args`, `hostPath`, restart policy
   as a string, resources as a nested map with suffixes, the namespace in the path. Not one of
   the thirteen was revisited in eleven years.

**The diff, and why** — v1beta3 did not lose. It won so completely that it changed its name.

That is the whole lesson about API versioning, and it is the opposite of what the post's
framing leads you to expect. A beta version is not a worse edition of a product; it is **a
shape still under negotiation**. The negotiation ended in April 2015, `v1` is the settled
shape, and the version string is a *compatibility promise* rather than a design — which is why
the promise could be renamed while every field it described stayed put.

The conversion machinery the post describes in one sentence is also unchanged. One object,
many representations, converted on read, stored in whichever version the server calls its
storage version. Only the version names in that sentence are different, and step 6 below is
that sentence running on v1.37.

Release facts and the pressure behind each one are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md); the removal
releases there come from the source tree at the release tag, not from the note that announced
the removal.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), fresh. Bring it up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, then `ssh zain@10.10.10.180`.

**Do**

1. Write the post's era into a file exactly as it would have been written, `v1beta3.yaml`:

   ```yaml
   apiVersion: v1beta3
   kind: Pod
   metadata:
     name: hello
   spec:
     containers:
     - name: hello
       image: busybox
       command: ["sh", "-c", "echo hi && sleep 3600"]
   ```

   `kubectl apply -f v1beta3.yaml`. Record the error verbatim.

2. Ask the server what it does serve: `kubectl api-versions | sort`. Count the lines. Find the
   groups that serve **more than one** version of the same thing — there are only a few, and
   one of them is step 6's.

3. Check three of the thirteen renames against the live API rather than taking the post's word
   for it:

   ```sh
   kubectl explain pod.spec.containers.command      # entrypoint -> command
   kubectl explain pod.spec.volumes.hostPath        # hostDir -> hostPath
   kubectl api-resources | grep -iE '^nodes|minion' # /minions -> /nodes
   ```

4. Confirm the namespace really is in the path, not a parameter:
   `kubectl get --raw /api/v1/namespaces/kube-system/pods | head -c 200`.

5. Test the post's closing advice. `kubectl get pods -o template --api-version=v1` — whatever
   the outcome, write down why the advice is now unnecessary rather than merely unavailable.
   Step 2 answered it.

6. **Conversion on read, in 2026.** `autoscaling` is one of the groups from step 2.

   ```sh
   kubectl create deployment web --image=nginx
   cat <<'YAML' | kubectl apply -f -
   apiVersion: autoscaling/v1
   kind: HorizontalPodAutoscaler
   metadata:
     name: web
   spec:
     scaleTargetRef: {apiVersion: apps/v1, kind: Deployment, name: web}
     minReplicas: 1
     maxReplicas: 3
     targetCPUUtilizationPercentage: 50
   YAML
   kubectl get hpa.v1.autoscaling web -o yaml | grep -A3 'spec:'
   kubectl get hpa.v2.autoscaling web -o yaml | grep -A8 'metrics:'
   ```

   Then write a field that only the newer version has, and read the object back through the
   older one — the whole object this time, not a grep:

   ```sh
   kubectl patch hpa.v2.autoscaling web --type=merge \
     -p '{"spec":{"behavior":{"scaleDown":{"stabilizationWindowSeconds":600}}}}'
   kubectl get hpa.v2.autoscaling web -o yaml | grep -A4 'behavior:'
   kubectl get hpa.v1.autoscaling web -o yaml
   ```

7. Before concluding anything from step 6, read `pkg/apis/autoscaling/v1/conversion.go` in
   `kubernetes/kubernetes`: what does the conversion do with the fields `v1` has no schema for,
   and why can it not simply drop them?

**Expect** — step 1 fails with `no matches for kind "Pod" in version "v1beta3"`, and it fails in
the *client*: `kubectl` asked the server for its versions and v1beta3 was not among them.

Step 3 finds all three renames intact. Step 4 shows the namespace as a path segment, as the post
said it would.

Step 6 is the point. Both reads in the first block describe the same object — one as
`targetCPUUtilizationPercentage: 50`, the other as a `metrics` list with
`resource.target.averageUtilization: 50`. Neither is a copy and neither is a conversion you
asked for; there is one stored object and two representations of it, exactly as the post
describes for `v1beta1` and `v1beta3`, with the version names swapped.

Then the second block. Through `v2`, `spec.behavior.scaleDown.stabilizationWindowSeconds: 600`.
Through `v1`, **`spec` has no `behavior` field at all** — `autoscaling/v1`'s schema has no word
for it. Do not stop there: read the rest of the `v1` object before deciding the value was lost.
A version that silently dropped what it could not express would make every read-modify-write
through it destructive, and Kubernetes cannot afford that, so the value has to be somewhere.
Find where, name it, and write down what would happen to it if you edited the object through
`v1` in a tool that did not preserve that place. Step 7 is where the answer is written down in
Go.

**Read on** — the [API deprecation policy](https://kubernetes.io/docs/reference/using-api/deprecation-policy/):
find the rule that made it legal to delete `v1beta3` weeks after telling everyone to adopt it,
and the rule that would forbid doing the same to `v1`. Write down the difference between them in
one sentence.

**Teardown** — `kubectl delete deploy web && kubectl delete hpa web`. Leave the guest up;
[the sidecar exercise](05-the-distributed-system-toolkit-patterns.md) runs on it.
