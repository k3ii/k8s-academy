<a id="docker-and-kubernetes-and-appc"></a>
# Both runtimes this post promises to support are gone, and the promise underneath them was kept

**Post** — [Docker and Kubernetes and AppC](https://kubernetes.io/blog/2015/05/docker-and-kubernetes-and-appc/),
2015-05-18, Kubernetes v0.17 — two months before 1.0.

**As written** — there is nothing to type. This is a positioning post, written a fortnight after
[the rkt announcement](https://kubernetes.io/blog/2015/05/appc-support-for-kubernetes-through-rkt/)
by Kubernetes's co-founder at Google, and its content is a set of commitments:

- The rkt/appc announcement has been "construed as a move from Google to support Appc over
  Docker" and that reading "is simply untrue."
- "Docker is currently the only supported runtime in GKE … and in GAE".
- "We intend to continue to support the Docker project and product, and Docker the company
  **indefinitely**."
- "We believe that Docker will continue to drive great experiences for developers looking to use
  containers and **plan to support this technology and its burgeoning community indefinitely**."
- And the reason for supporting rkt at all: "Our intent … was to establish Kubernetes (our open
  source project) as a **neutral ground in the world of containers**. Customers should be able to
  pick their container runtime and format based solely on its technical merits."

Two runtimes, both to be carried in tree, so that no one has to choose.

**As it runs now** — the two commitments and the goal came apart completely, and the exercise is
noticing that only the commitments failed:

1. **rkt is not a thing you can select.** In-tree rkt support — "rktnetes" — was deprecated in
   v1.10, the code was removed in **v1.11**, and the `--container-runtime` flag that chose
   between runtimes was removed from the kubelet in **v1.27**. `rkt/rkt` on GitHub is archived
   and its README opens *[Project ended]*.
2. **"Indefinitely" ended in v1.24.** `dockershim`, the in-tree adapter that let the kubelet
   drive Docker, was deprecated in v1.20 and removed in **v1.24**. Docker Engine still runs
   containers on plenty of these nodes; what it no longer does is take instructions from a
   kubelet.
3. **The removal is not in the document that lists removals.** The pin's deprecation guide has
   sections for v1.32, v1.29, v1.27, v1.26, v1.25, v1.22 and v1.16 — and **no v1.24 section at
   all.** The largest breaking change in the project's history is invisible there, because that
   guide tracks API versions and dockershim was a component.
4. **The goal was met, by the opposite method.** A cluster today is neutral about runtimes
   because the kubelet supports *none of them directly*. It speaks one gRPC interface, CRI, and
   whatever answers on the socket is the runtime. Neutrality was delivered by deleting both of
   the in-tree implementations this post promised to maintain.

**The diff, and why** — this is a post about a **plan the project abandoned**, and the forecast
that failed is the interesting one because it failed by being achieved.

Supporting two runtimes in tree means the kubelet contains, compiles and ships an adapter per
runtime. Every runtime feature is a Kubernetes release; every runtime bug is a Kubernetes CVE;
every new entrant needs a merged PR in `kubernetes/kubernetes` and a sponsor to review it. That
is the exact opposite of neutral — it makes the project the gatekeeper of the runtime market,
and it makes "based solely on its technical merits" impossible, because the merit that decides
is whether SIG Node has bandwidth. The post's own two examples prove the cost: one adapter was
deleted for lack of users, the other for lack of maintainers.

So the pressure was **maintenance ownership, not preference**. CRI moves the adapter out of the
kubelet and behind a socket: the runtime vendor maintains their side, the kubelet maintains one
client, and adding a runtime needs nobody's permission. The CRI API went **stable in v1.23** —
one release before dockershim was removed, which is the ordering you would expect if the removal
was waiting on the replacement rather than the other way round. From **v1.26** the kubelet
refuses to register a node whose runtime does not serve the `v1` CRI API, so the interface is now
the hard requirement that a specific runtime used to be.

The one trace of the post's promise left in the API is `pod.spec.runtimeClassName` — a string
naming a *class* the cluster administrator defined, not a runtime the manifest author chose.
Neutrality survived; the right to name Docker in a pod spec never existed and now cannot be
added.

Release facts and the pressure behind each are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md); the removal
releases there come from the source tree at the release tag, not from the note that announced the
removal — which for dockershim matters more than usual, since the v1.20 note said the removal was
"currently planned for the 1.22 release" and it landed in 1.24.

**No gate** — CRI has never had a feature gate, and it could not have one: a gate is read by a
binary at startup to switch behaviour, and the kubelet has no alternative behaviour to switch to.
Instruments used, in the order the steps below use them: the CRI concept page's own feature-state
marker (`stable`, `v1.23`), the node object's `status.nodeInfo.containerRuntimeVersion`, and
`crictl version`'s `RuntimeApiVersion`. What they disagree with is the deprecation guide, which —
per point 3 above — does not record v1.24 happening.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo). If you still have the guest from
[the monitoring exercise](02-resource-usage-monitoring-kubernetes.md), reuse it; otherwise bring
it up with [the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, then `ssh zain@10.10.10.180`.

**Do**

1. Ask the cluster which of the post's two runtimes it picked:

   ```sh
   kubectl get nodes -o wide
   kubectl get nodes -o jsonpath='{range .items[*]}{.status.nodeInfo.containerRuntimeVersion}{"\n"}{end}'
   ```

2. Look for both of them on the node, and be precise about what "absent" means for each:

   ```sh
   command -v docker rkt || echo 'neither on PATH'
   systemctl is-active docker 2>/dev/null || echo 'no docker service'
   ```

3. Find the socket the answer in step 1 came from, by asking the process rather than guessing:

   ```sh
   sudo tr '\0' '\n' < /proc/$(pgrep -x kubelet | head -1)/cmdline | grep -i runtime
   ```

4. Talk to the runtime yourself, the way the kubelet does, and confirm which API version it
   serves:

   ```sh
   sudo crictl version
   sudo crictl pods | head
   kubectl get pods -A --no-headers | wc -l
   sudo crictl pods --state Ready --quiet | wc -l
   ```

5. Try to make the choice the post promised you would always have. `--help` parses flags without
   starting anything, so this is safe:

   ```sh
   kubelet --container-runtime=docker --help 2>&1 | head -3
   kubelet --help 2>&1 | grep -c 'container-runtime-endpoint'
   ```

6. Look for v1.24 in the document that is supposed to tell you what a release removed:

   ```sh
   kubectl explain pod.spec.runtimeClassName
   kubectl get runtimeclasses
   ```

   Then search the pin's deprecation guide for `1.24` and write down what you find instead.

7. Finally, settle whether "neutral" is a property of the API or of the docs. Grep the Pod spec
   for any field that names a runtime *implementation*:

   ```sh
   kubectl explain pod.spec | grep -i -E 'runtime|docker|containerd'
   ```

**Expect** — step 1 prints something like `containerd://2.x` or `cri-o://1.3x`. Neither of the
post's two runtimes is the answer on any cluster you can build today.

Step 2 is where the distinction lives. `rkt` is absent because the project ended. `docker` may
well be *present* — plenty of engineers have it installed — and it is still absent from step 1,
because presence on the node stopped implying use by the cluster in v1.24.

Step 3 shows exactly one runtime flag, `--container-runtime-endpoint`, pointing at a socket. Step
5 confirms why: `--container-runtime=docker` fails with an unknown-flag error, and the only
survivor is the *endpoint*. The flag that expressed the post's promise — a choice between named
runtimes — is the flag that was deleted.

Step 4's `crictl version` reports `RuntimeApiVersion: v1`. It has to: since v1.26 a runtime that
serves anything else does not get its node registered. The two pod counts will not match exactly,
and the gap is the point — `crictl` sees sandboxes on this node, `kubectl` sees pods in the
cluster, and neither is wrong.

Step 6: `runtimeClassName` exists, `kubectl get runtimeclasses` is almost certainly empty, and
the deprecation guide has no v1.24 entry. A reader who upgraded a v1.23 cluster by reading that
guide would have lost every node and found no explanation in it.

Step 7 finds `runtimeClassName` and nothing else. There is no field anywhere in a Pod that names
a runtime binary — which is why the post's promise could be broken without breaking a single
manifest.

**Read on** — [KEP-2221, *Remove
dockershim*](https://github.com/kubernetes/enhancements/tree/master/keps/sig-node/2221-remove-dockershim):
find what its authors said would happen to users who could not migrate, and compare that with
this post's word "indefinitely". Write down, in one sentence, what a project can honestly promise
about an interface that it cannot promise about an implementation.

**Teardown** — nothing was created. Leave the guest up;
[the cluster-level logging exercise](04-cluster-level-logging-with-kubernetes.md) needs a second
node, so read its *Topology* before you tear anything down.
