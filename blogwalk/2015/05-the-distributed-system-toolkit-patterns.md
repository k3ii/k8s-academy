<a id="distributed-system-toolkit-patterns"></a>
# Two of the three patterns are still patterns; one became a field

**Post** — [The Distributed System ToolKit: Patterns for Composite Containers](https://kubernetes.io/blog/2015/06/the-distributed-system-toolkit-patterns/),
2015-06-29, Kubernetes pre-1.0 — three weeks before the 1.0 release.

**As written** — the argument first: a container image should be "analogous to a class in an
object-oriented language", so a pod of several containers is composition, and the reason to put
them in one pod is that they need to share a filesystem and a network namespace. Then three
examples, each one prose and a diagram — the post ships no manifests at all:

- **Sidecar** — an `nginx` container serving files out of a volume, plus a *git synchronizer*
  container that pulls a repository into that same volume. Push to git, the site updates. Two
  images, separately built and separately reusable, sharing one filesystem.
- **Ambassador** — an application that talks to a redis on `localhost`, and a proxy container in
  the same pod that splits reads from writes across a real redis cluster. The application's
  configuration is `localhost`, forever, in every environment.
- **Adapter** — several different applications each emitting monitoring data in its own format,
  each with a small container beside it that normalises the output to one interface, so the
  monitoring system sees a uniform fleet.

**As it runs now** — every word of it still runs. Same pod, same shared network namespace, same
shared volume, same `localhost`. Eleven years and the three examples need no translation; this
is the far end of the range from
[the v1beta3 exercise](01-introducing-kubernetes-v1beta3.md), where nothing ran at all.

What changed is not the patterns. It is that **the first one stopped being a pattern and became
an API field**, because a plain second container has two failure modes this post could not see
in June 2015 — there was no Job object worth speaking of and no service mesh to be a sidecar of.

- **No defined startup order.** Containers in `containers` start concurrently. A proxy that
  comes up after the application misses the application's first outbound calls.
- **No defined shutdown order, and no notion of "not the point of the pod".** A container that
  never exits keeps its pod `Running` forever. Under a Deployment nobody notices. Under a Job it
  means the Job never completes.

**The diff, and why** — a native sidecar at the pin is an entry in `initContainers` carrying
`restartPolicy: Always`. That placement is the whole design: it inherits `initContainers`'
ordering guarantee — it is started, and becomes ready, before the containers after it — while
`restartPolicy: Always` tells the kubelet it is long-running rather than a step that finishes,
and that it should be terminated once the main containers are done and excluded from deciding
whether the pod succeeded.

Alpha in **v1.28** behind the `SidecarContainers` gate, beta and on by default in **v1.29**, GA
in **v1.33**; `LegacySidecarContainers` removed in **v1.34**, and the `SidecarContainers` gate
itself deleted from the codebase in **v1.37**. At the pin there is no gate to enable. KEP-753's
`kep.yaml` reads `status: implemented`, `stage: stable`.

The decision behind it: the pattern had been load-bearing for eight years — meshes, log
shippers, secret agents — while the API had no word for it, so every user of it rebuilt the same
two workarounds. The field did not invent anything. It named something that already existed and
handed the lifecycle problem to the kubelet, which is the only component positioned to solve it.

Full release provenance in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md) — the removal
releases there were confirmed by reading the source tree at each release tag, because
Kubernetes' own deprecation notices get their own removals wrong in both directions.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo). If you still have the guest from
[the v1beta3 exercise](01-introducing-kubernetes-v1beta3.md), reuse it; otherwise bring it up
with [the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, then `ssh zain@10.10.10.180`.

**Do**

1. First, confirm what did *not* change — the ambassador's premise. One pod, two containers, one
   network namespace:

   ```sh
   kubectl run amb --image=nginx --restart=Never --dry-run=client -o yaml \
     | kubectl patch --local -f - --type=json -o yaml \
       -p '[{"op":"add","path":"/spec/containers/-","value":{"name":"app","image":"busybox","command":["sh","-c","sleep 3600"]}}]' \
     | kubectl apply -f -
   kubectl exec amb -c app -- wget -qO- http://localhost/ | head -3
   ```

2. Now build the post's sidecar the only way the post could have built it — a second entry in
   `containers` — and put it under a Job, so the lifecycle problem shows:

   ```yaml
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: legacy
   spec:
     template:
       spec:
         restartPolicy: Never
         volumes:
         - name: shared
           emptyDir: {}
         containers:
         - name: worker
           image: busybox
           command: ["sh", "-c", "cat /shared/ready 2>/dev/null || echo 'NO CONFIG'; sleep 5; echo work done"]
           volumeMounts: [{name: shared, mountPath: /shared}]
         - name: shipper
           image: busybox
           command: ["sh", "-c", "echo ready > /shared/ready; while true; do sleep 5; done"]
           volumeMounts: [{name: shared, mountPath: /shared}]
   ```

   `kubectl apply -f legacy.yaml`, then watch for a full minute:
   `kubectl get job legacy -w`. In another shell:
   `kubectl logs job/legacy -c worker`.

3. Delete it (`kubectl delete job legacy`) and re-apply the same two containers with one
   change — the shipper moves into `initContainers` and gains a restart policy:

   ```yaml
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: native
   spec:
     template:
       spec:
         restartPolicy: Never
         volumes:
         - name: shared
           emptyDir: {}
         initContainers:
         - name: shipper
           image: busybox
           restartPolicy: Always
           command: ["sh", "-c", "echo ready > /shared/ready; while true; do sleep 5; done"]
           volumeMounts: [{name: shared, mountPath: /shared}]
         containers:
         - name: worker
           image: busybox
           command: ["sh", "-c", "cat /shared/ready 2>/dev/null || echo 'NO CONFIG'; sleep 5; echo work done"]
           volumeMounts: [{name: shared, mountPath: /shared}]
   ```

   `kubectl apply -f native.yaml`, then `kubectl get job native -w` and
   `kubectl logs job/native -c worker`.

4. Ask the API where the field lives, and note that it is a `Container` field, not a new kind:
   `kubectl explain job.spec.template.spec.initContainers.restartPolicy`.

5. Repeat step 2 several times if the worker printed `ready`. Startup order is *undefined*, not
   *reversed* — you are looking for the race, and on a quiet single node it will often go the
   convenient way.

**Expect** — step 1 succeeds: `app` fetches nginx on `localhost` with no service, no DNS, no
port published. The ambassador pattern needs nothing that 2015 did not have.

Step 2 fails in two ways at once, and only one of them is honest with you. The `worker` may
print `NO CONFIG` — it started concurrently with the shipper and read the file before it
existed. And whatever the worker prints, `kubectl get job legacy -w` never reaches
`COMPLETIONS 1/1`: the pod stays `Running` because `shipper` is still alive, and the Job has no
signal that `shipper` was never the point. Nothing errors. Nothing warns. It just sits
there.

Step 3, with the same two images and the same volume, prints `ready` every time — the sidecar
is started and ready before `worker` begins — and the Job reaches `1/1` a few seconds after
`worker` exits, because the kubelet terminates the sidecar once the main containers are done.

One field. That is the entire difference, and it is the difference between a pattern you
implement carefully and a guarantee you can rely on.

**Read on** — [KEP-753](https://github.com/kubernetes/enhancements/tree/master/keps/sig-node/753-sidecar-containers):
find the alternatives that were rejected before `initContainers` + `restartPolicy` was chosen,
and work out what a new top-level `sidecarContainers` list would have cost every existing
consumer of the Pod API.

**Teardown** — `kubectl delete pod amb; kubectl delete job native --ignore-not-found`. When
you are done with the guest,
[tear the lab down properly](../../strands/lab-topologies.md#teardown).
