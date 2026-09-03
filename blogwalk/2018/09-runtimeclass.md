<a id="runtimeclass"></a>

# The one field this post describes lost the `spec` that held it, and the page that documents the resource now states three different maturities and counts two fields while documenting four — a disagreement one `kubectl explain` settles and eight years of edits did not

**Post** — [Kubernetes v1.12: Introducing
RuntimeClass](https://kubernetes.io/blog/2018/10/10/runtimeclass/), 10 October 2018, by Tim Allclair
(Google). 47 lines, 5,399 bytes.

It is the shortest walk in this year and it has a property no other walk in the archive has: it
introduces an API resource and never shows it. There are no code fences in the file at all, and the
strings `apiVersion` and `kind:` do not appear once. Everything the post says about the shape of the
object is said in prose, in a single sentence, and that sentence is what this exercise is about.

**As written** — the post opens with history (`:9`): Docker first, then rkt in 1.3, then the
Container Runtime Interface that followed from it, then Kata Containers and gVisor for stronger
workload isolation and the Windows support progressing alongside them. From that it derives
four problems (`:13-16`): how users find out which runtimes exist and pick one, how pods reach nodes
that support the chosen runtime, which runtimes support which features and how incompatibilities
surface, and how the differing resource overheads get accounted for. *"**RuntimeClass** aims to
solve these issues"* (`:18`).

Then the sentence, at `:24`:

> The RuntimeClass resource represents a container runtime supported in a Kubernetes cluster. The
> cluster provisioner sets up, configures, and defines the concrete runtimes backing the
> RuntimeClass. In its current form, a RuntimeClassSpec holds a single field, the
> **RuntimeHandler**. The RuntimeHandler is interpreted by the CRI implementation running on a node,
> and mapped to the actual runtime configuration. Meanwhile the PodSpec has been expanded with a new
> field, **RuntimeClassName**, which names the RuntimeClass that should be used to run the pod.

Two names, in Go casing, and a container for one of them. `:26` then answers why the choice is
per-pod rather than per-container: the resource model expects some resources to be shareable between
containers in a pod, and *"it is extremely difficult to support a loopback (localhost) interface
across a VM boundary"*.

The rest of the post is forward-looking, and it is worth separating into two lists because they have
had two different fates. `:30` names two things the project *might* do — add
`NodeAffinity` terms to the RuntimeClass definition so the scheduler can handle heterogeneous nodes,
and pursue the Pod Overhead proposal for the varying resource requirements. Then `:32` says many
other extensions have been proposed and *"will be revisited as the feature continues to develop and
mature"*, and `:34-38` lists five:

> - Surfacing optional features supported by runtimes, and better visibility into errors caused by
>   incompatible features.
> - Automatic runtime or feature discovery, to support scheduling decisions without manual
>   configuration.
> - Standardized or conformant RuntimeClass names that define a set of properties that should be
>   supported across clusters with RuntimeClasses of the same name.
> - Dynamic registration of additional runtimes, so users can install new runtimes on existing
>   clusters with no downtime.
> - "Fitting" a RuntimeClass to a pod's requirements. For instance, specifying runtime properties
>   and letting the system match an appropriate RuntimeClass, rather than explicitly assigning a
>   RuntimeClass by name.

`:40` closes: RuntimeClass *"will be under active development at least through 2019"*, and names
the v1.12 alpha as the start of it.

Finally, four links under Learn More (`:44-47`). The first is the one a reader acts on — *"Take it
for a spin!"* — and it points at `/docs/concepts/containers/runtime-class/#runtime-class`. The
second points at `keps/sig-node/runtime-class.md` in the enhancements repository. Both are checked
below.

**As it runs now** — the resource is `node.k8s.io/v1`, cluster-scoped, and the only kind in its
group. `group-versions.md:29` lists `node.k8s.io` with `v1` and nothing else, which is the trace of
the v1beta1 removal that `deprecation-guide.md:158-162` records for v1.25. The version the post
announced is not in that guide, because an alpha version leaves no removal to document.

The generated reference has one page for the whole group, `node/runtime-class-v1.md`. Its field
table has six rows (`:39-60`): `apiVersion`, `handler`, `kind`, `metadata`, `overhead`,
`scheduling`. Four of those are not boilerplate. There is no `spec` and there is no `status`, so of
the two Go type names the post gave you, `RuntimeClassSpec` names nothing and `RuntimeClassName`
survives verbatim as `spec.runtimeClassName` on the Pod (`runtime-class.md:94`). The field that was
inside the spec is now `handler`, a sibling of `metadata`, and it is the only required field on the
object (`:43`). Its description adds two constraints the post does not mention: *"The Handler must
be lowercase, conform to the DNS Label (RFC 1123) requirements, and is immutable"* (`:44`).

The concept page states the object's size at `:59-60`:

> The RuntimeClass resource currently only has 2 significant fields: the RuntimeClass name
> (`metadata.name`) and the handler (`handler`).

That sentence is contradicted by its own page twice. `:140-141` documents `scheduling` — *"By
specifying the `scheduling` field for a RuntimeClass, you can set constraints to ensure that Pods
running with this RuntimeClass are scheduled to nodes that support it"* — and `:165` documents
`overhead`: *"Pod overhead is defined in RuntimeClass through the `overhead` field."* Both are
fields of this resource, both have their own generated sub-tables (`Overhead` at reference `:95`,
`Scheduling` at `:112`), and both are eighty and a hundred lines below the sentence that says there
are two.

The page also cannot settle when the resource grew up. It carries three `feature-state` shortcodes:

| line | subject | shortcode |
|---|---|---|
| `:13` | the page, and so the resource | stable, v1.20 |
| `:138` | the `scheduling` field | **beta, v1.16** |
| `:160` | the `overhead` field | stable, v1.24 |

The middle one is the problem, and the ladder below is what settles it: `scheduling` never had a
gate of its own. It rode the `RuntimeClass` gate, which went stable at v1.20 and was deleted after
v1.24. There is no switch at v1.37 that can make `scheduling` beta, and there has not been one for
thirteen releases.

One more sentence dates the same way. `:104-105` reads: *"If no `runtimeClassName` is specified, the
default RuntimeHandler will be used, which is equivalent to the behavior when the RuntimeClass
feature is disabled."* The behaviour is right and the comparison is to a state no v1.37 cluster can
be put into.

What *is* still switched on is the admission plugin, and it is the reason two of the steps below
work with no configuration at all. `admission-controllers.md:130` lists nineteen plugins enabled by
default and `RuntimeClass` is one of them; `:841-854` gives it as *"Mutating and Validating"*, says
it *"rejects any Pod create requests that have the overhead already set"* (`:847-848`), and says it
*"sets `.spec.overhead` in the Pod based on the value defined in the corresponding RuntimeClass"*
(`:849-851`). The feature gate was removed. The controller it gated was not.

Against the post's two lists, the outcome divides cleanly. Both items at `:30` landed, and neither
in the form the post floated. The scheduler support arrived as `scheduling.nodeSelector` plus
`scheduling.tolerations` (reference `:122`, `:126`), which is not `NodeAffinity` — a `nodeSelector`
is an equality map, and the merge semantics are stated per field: the selector is intersected and a
conflict rejects the pod, the tolerations are unioned. Pod Overhead landed as `overhead.podFixed`
(reference `:105`) with its own concept page and its own gate.

None of the five at `:34-38` landed, and for three of them the pinned documentation now states the
opposite as a standing assumption rather than an open problem:

- **Automatic runtime or feature discovery.** `runtime-class.md:46-48`: *"RuntimeClass assumes a
  homogeneous node configuration across the cluster by default."* Reference `:44`: *"It is assumed
  that all handlers are available on every node, and handlers of the same name are equivalent on
  every node."*
- **Standardized or conformant RuntimeClass names.** Reference `:44` again: *"The possible values
  are specific to the node & CRI configuration."* There is no conformant handler name anywhere in
  the pinned tree.
- **Surfacing optional features, and better visibility into errors.** `runtime-class.md:98-102`:
  the pod enters the `Failed` terminal phase and *"Look for a corresponding event for an error
  message."* That is the same visibility the post was writing to improve.

The other two are absent rather than contradicted. Installing a new runtime still means editing a
file on the node and restarting the runtime (`:113-118`), which is not dynamic registration; and a
pod still names its RuntimeClass, which is not fitting.

The Learn More links have both rotted, in two different ways. `:44` sends you to
`/docs/concepts/containers/runtime-class/#runtime-class`; the page is there, and the fragment is
not — the page's headings are Motivation, Setup, Usage, CRI Configuration, Scheduling and Pod
Overhead, and nothing defines `runtime-class`. `:45` sends you to `keps/sig-node/runtime-class.md`;
the pinned page's own version of the same link (`:171`) is
`keps/sig-node/585-runtime-class/README.md`, so the KEP acquired a number and a directory. Note
where that number comes from: the pinned tree, at `:171` and again at `:175` for pod overhead. It is
not written from memory here and should not be.

**What this exercise does not cover, and where it lives.** The `pod-overhead.md` page verifies its
own worked example by reading `/sys/fs/cgroup/memory/kubepods/…/memory.limit_in_bytes` (`:186`),
which is a cgroup v1 path; cgroups have three census rows of their own in later years and the
version question belongs to them, so step 9 stops at the API object. Migrating `node.k8s.io/v1beta1`
manifests is owned by a later year's removal exercise. The 2019 post that builds an end-to-end
system on RuntimeClass is `dated` in its own census and not walkable in this lab. And the
containerd major-version question raised by `:113-118` is [already
measured](../2017/08-containerd-container-runtime-options-kubernetes.md); step 6 uses its result
rather than re-deriving it.

**The diff, and why** — the post is right about everything it asserts and the object it describes
cannot be written down.

That is not the post breaking. `RuntimeClassSpec` existed, held exactly one field, and was described
accurately. What happened is that the resource was promoted, and promotion in this case meant
deletion: the alpha's `spec` wrapper went away and its one field moved up beside `metadata`. The
name `RuntimeClassName` came through untouched. So a reader following `:24` at the pin gets one
sentence half right, and the half that fails is the half about structure rather than about
behaviour.

The interesting part is what happened next, because the resource is one of very few in Kubernetes
that got *simpler* on its way to stable and then grew back by exactly two fields — both of them
from the post's own paragraph of maybes, and neither in the shape the paragraph proposed. `:30`
guessed `NodeAffinity` and got a `nodeSelector` with published merge semantics. It guessed a
proposal document and got `overhead.podFixed` with an admission controller that will reject a pod
for setting the field itself. Meanwhile the five extensions listed as under active consideration
produced nothing in eight years, and the documentation quietly converted three of them from open
problems into stated assumptions. *"under active development at least through 2019"* (`:40`) turned out to be a ceiling rather than
a floor: the gate went stable in v1.20 and was
deleted in v1.24, and the only new gate in this neighbourhood since is
`RuntimeClassInImageCriApi`, which is about pulling images and not about any of the four problems at
`:13-16`.

So the reading to carry is about the documentation rather than the API. The API is small, stable and
easy to measure — one kind, one required field, two optional structs, nine operations. The page that
describes it has a field count from an earlier version of the object, a maturity marker from an
earlier version of the gate, and a comparison to a switch that no longer exists, all three of which
are settled by a command the page never suggests running. A resource that stops changing stops
getting read, and a page that stops getting read keeps its arithmetic.

**The ladder** — two removed gates and one live one.

`RuntimeClass`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.12 – v1.13 |
| beta | `true` | — | v1.14 – v1.19 |
| stable | `true` | — | v1.20 – v1.24 |

`removed: true`, with a `# Removed from Kubernetes` comment above the title. Body: "Enable the
RuntimeClass feature for selecting container runtime configurations." Alpha in the release this post
announces, and gone four releases after going stable. This is the gate that `runtime-class.md:104-105`
still compares against and that `:138` still describes as beta.

`PodOverhead`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.16 – v1.17 |
| beta | `true` | — | v1.18 – v1.23 |
| stable | `true` | — | v1.24 – v1.25 |

Also `removed: true`. Body: "Enable the PodOverhead feature to account for pod overheads." Its
stable row starts at v1.24, which is exactly the version in the `feature-state` shortcode at
`runtime-class.md:160` — so of the page's three maturity markers, this is the one that matches a
gate file. Note also that the second thing `:30` hedged on took four releases to appear as a gate
and eight to reach stable.

`RuntimeClassInImageCriApi`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.29 – |

One row, no `toVersion`, no `removed`, so it is live and off by default at the pin. Body: "Enables
images to be pulled based on the runtime class of the pods that reference them." Seven years after
the post, the only new switch in this neighbourhood is about which image gets pulled for a handler —
adjacent to the post's third problem about feature compatibility, and not an answer to it.

There is no gate for `scheduling`. That absence is the finding, and the reason `:138` cannot be
right.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair): a control-plane node at
`10.10.10.130` and a worker at `10.10.10.131`. Two nodes are load-bearing here for one reason: the
`scheduling` field is about placing pods on the subset of nodes that support a handler, and a subset
needs something to be a subset of. Steps 10 and 11 label and taint the worker and watch admission
merge those constraints into a pod. Bring it up with [the five provision
steps](../../strands/lab-topologies.md#provision), substituting `topology=pair`, then
`ssh zain@10.10.10.130`. Steps 3, 4, 12 and 13 read the pinned checkout and need no cluster.

**Do**

1. Establish the group, the kind and the scope:

   ```sh
   kubectl create ns rtc
   kubectl api-resources --api-group=node.k8s.io
   kubectl api-versions | grep node.k8s.io
   kubectl get runtimeclass
   ```

   One kind, one version, cluster-scoped, and no objects. Compare the version list against
   `group-versions.md:29` and note that `v1beta1` is not offered — `deprecation-guide.md:158-162`
   is the entry that records why, and there is no corresponding entry for the `v1alpha1` the post
   announced.

2. Ask the server for the shape, and then for the thing the post named:

   ```sh
   kubectl explain runtimeclass
   kubectl explain runtimeclass.spec
   kubectl explain runtimeclass.handler
   kubectl explain pod.spec.runtimeClassName
   ```

   The second command is the exercise. Record its exact response. Then read `:24` of the post again
   and mark which of its two Go names still resolves to something.

3. Count the fields three ways and find the disagreement. No cluster needed for the last two:

   ```sh
   kubectl explain runtimeclass --recursive
   W=/path/to/pinned/website/content/en/docs
   grep -c '<td><code>' $W/reference/kubernetes-api/node/runtime-class-v1.md
   sed -n '29,60p' $W/reference/kubernetes-api/node/runtime-class-v1.md | grep -o '<code>[a-zA-Z]*</code>'
   sed -n '59,60p' $W/concepts/containers/runtime-class.md
   sed -n '140,141p;165p' $W/concepts/containers/runtime-class.md
   ```

   The first `grep -c` counts every field cell on the page including the list, the sub-structs and
   the operation parameters, so use the `sed` after it for the object's own six. Then the sentence
   that says two, then the two fields the same page documents later. Write down the number you would
   put in that sentence.

4. Find the three maturities, and decide which can be true:

   ```sh
   grep -n 'feature-state' $W/concepts/containers/runtime-class.md
   grep -n 'feature-state' $W/concepts/scheduling-eviction/pod-overhead.md
   G=/path/to/pinned/website/content/en/docs/reference/command-line-tools-reference/feature-gates
   ls $G | grep -i 'runtime\|overhead'
   grep -il runtimeclass $G/*.md
   ```

   Three shortcodes on one page. Then the three gate files that exist in this neighbourhood, and the
   two gate files whose subject is RuntimeClass itself — neither of them about the `scheduling`
   field. Match each shortcode to a gate file and say which one has no gate to justify it.

5. The gate is gone and the controller is not. Ask the API server what it has enabled:

   ```sh
   kubectl -n kube-system get pod -l component=kube-apiserver \
     -o jsonpath='{.items[0].spec.containers[0].command}' | tr ',' '\n' | grep -i 'admission\|feature'; true
   sed -n '130p' $W/reference/access-authn-authz/admission-controllers.md | tr ',' '\n' | grep -n RuntimeClass
   sed -n '841,854p' $W/reference/access-authn-authz/admission-controllers.md
   ```

   A kubeadm API server usually names no plugins at all, which means it runs the defaults. Find
   `RuntimeClass` in the default list and its position, then read what the plugin does. Both halves
   — the mutation and the rejection — get tested in steps 9 and 10. If you want the distinction
   between a compiled-in plugin and a webhook, [the extensible admission
   exercise](01-extensible-admission-is-beta.md) is where it lives.

6. Create a RuntimeClass for a handler the node actually has, and one for a handler it does not.
   Find the real handler name on the node first, in the runtime's own configuration:

   ```sh
   ssh zain@10.10.10.131 'sudo grep -n containerd.runtimes /etc/containerd/config.toml | head'
   kubectl apply -f - <<'YAML'
   apiVersion: node.k8s.io/v1
   kind: RuntimeClass
   metadata:
     name: house-runc
   handler: runc
   ---
   apiVersion: node.k8s.io/v1
   kind: RuntimeClass
   metadata:
     name: house-absent
   handler: notinstalled
   YAML
   kubectl get runtimeclass
   ```

   Both objects are accepted. The API server does not check handlers against nodes, and reference
   `:44` says why: it assumes every handler is on every node. Whether the table name in your
   `config.toml` matches `runtime-class.md:117` is a containerd major-version question with [its own
   exercise](../2017/08-containerd-container-runtime-options-kubernetes.md); here you only need the
   handler name, which is the last component of the table key.

7. Run a pod under each, and read the difference:

   ```sh
   for rc in house-runc house-absent; do
     kubectl -n rtc run $rc --image=busybox --restart=Never \
       --overrides="{\"spec\":{\"runtimeClassName\":\"$rc\"}}" -- sleep 300
   done
   sleep 20
   kubectl -n rtc get pod -o wide
   kubectl -n rtc get pod house-absent -o jsonpath='{.status.phase}{"\n"}'
   kubectl -n rtc describe pod house-absent | sed -n '/Events/,$p'
   ```

   `runtime-class.md:98-102` predicts the failing case exactly: the pod enters the `Failed` terminal
   phase and the reason is in an event, not in the object. Read the event text and then re-read the
   post's third problem at `:15` — *"how can we surface incompatibilities to the user?"* — and say
   whether an event on a `Failed` pod is a surface.

8. The object has two different naming rules, one for the name and one for the handler. Reference
   `:44` says the handler must be a DNS *label* and immutable; `runtime-class.md:74-75` says the
   name must be a DNS *subdomain*. Test both, and the immutability:

   ```sh
   kubectl apply --dry-run=server -f - <<'YAML'
   apiVersion: node.k8s.io/v1
   kind: RuntimeClass
   metadata:
     name: house.dotted.name
   handler: runc
   YAML
   kubectl apply --dry-run=server -f - <<'YAML'
   apiVersion: node.k8s.io/v1
   kind: RuntimeClass
   metadata:
     name: house-dotted-handler
   handler: house.dotted.handler
   YAML
   kubectl patch runtimeclass house-runc --type=merge -p '{"handler":"somethingelse"}'
   ```

   One dot is legal in the name and illegal in the handler, on the same object, in the same request.
   Then the patch: the field the post called the whole of the spec cannot be changed once set. Record
   the error, and note that immutability is stated only in the generated reference — `grep -c
   immutable` the concept page and see.

9. `overhead`, the second of the post's two maybes. Create a class that declares some, run a pod
   that declares none, and read back what admission did:

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: node.k8s.io/v1
   kind: RuntimeClass
   metadata:
     name: house-overhead
   handler: runc
   overhead:
     podFixed:
       memory: "120Mi"
       cpu: "250m"
   YAML
   kubectl -n rtc run overhead-pod --image=busybox --restart=Never \
     --overrides='{"spec":{"runtimeClassName":"house-overhead"}}' -- sleep 300
   kubectl -n rtc get pod overhead-pod -o json \
     | python3 -c 'import sys,json; s=json.load(sys.stdin)["spec"]; print("overhead:", s.get("overhead")); print("runtimeClassName:", s.get("runtimeClassName"))'
   ```

   The pod's manifest never mentioned `overhead` and the object has it. That is
   `admission-controllers.md:849-851` happening. Read the value with `-o json` and not with
   `jsonpath`: `pod-overhead.md:98` uses jsonpath and `:104` prints the result as
   `map[cpu:250m memory:120Mi]`, which is Go's rendering of a map and not JSON, and is a shape you
   cannot feed to anything.

10. The validating half of the same plugin. Set the field by hand and keep the RuntimeClass:

    ```sh
    kubectl -n rtc apply --dry-run=server -f - <<'YAML'
    apiVersion: v1
    kind: Pod
    metadata:
      name: overhead-by-hand
    spec:
      runtimeClassName: house-overhead
      overhead:
        podFixed:
          memory: "1Gi"
      containers:
        - name: c
          image: busybox
          command: ["sleep", "300"]
    YAML
    ```

    `admission-controllers.md:847-848` says this is refused: the plugin *"rejects any Pod create
    requests that have the overhead already set."* Record the message. Then consider what it implies
    about who owns the field, and compare that with `pod-overhead.md:33`, which tells you the
    prerequisite is a RuntimeClass that defines `overhead` and does not mention that you are
    forbidden from setting it yourself.

11. `scheduling.nodeSelector`, merged by intersection, conflict rejected. Label the worker, then
    send a pod whose own selector disagrees:

    ```sh
    kubectl label node k8s-worker house.io/sandbox=yes
    kubectl apply -f - <<'YAML'
    apiVersion: node.k8s.io/v1
    kind: RuntimeClass
    metadata:
      name: house-sandboxed
    handler: runc
    scheduling:
      nodeSelector:
        house.io/sandbox: "yes"
    YAML
    kubectl -n rtc run sel-ok --image=busybox --restart=Never \
      --overrides='{"spec":{"runtimeClassName":"house-sandboxed"}}' -- sleep 300
    kubectl -n rtc get pod sel-ok -o json \
      | python3 -c 'import sys,json; print(json.load(sys.stdin)["spec"].get("nodeSelector"))'
    kubectl -n rtc apply --dry-run=server -f - <<'YAML'
    apiVersion: v1
    kind: Pod
    metadata:
      name: sel-conflict
    spec:
      runtimeClassName: house-sandboxed
      nodeSelector:
        house.io/sandbox: "no"
      containers:
        - name: c
          image: busybox
          command: ["sleep", "300"]
    YAML
    ```

    The first pod sent no `nodeSelector` and has one. The second sent a contradicting value for the
    same key. Reference `:122-123` states both outcomes — merged with the pod's, *"Any conflicts
    will cause the pod to be rejected in admission"* — and `runtime-class.md:146-148` says the same
    in prose. This is what `:30`'s `NodeAffinity` became; write down one behavioural difference
    between an equality selector merged at admission and a node affinity term evaluated by the
    scheduler.

12. `scheduling.tolerations`, unioned rather than intersected. Taint the worker so that nothing
    ordinary lands there, then let the class carry the toleration:

    ```sh
    kubectl taint node k8s-worker house.io/sandbox=yes:NoSchedule
    kubectl apply -f - <<'YAML'
    apiVersion: node.k8s.io/v1
    kind: RuntimeClass
    metadata:
      name: house-tolerant
    handler: runc
    scheduling:
      nodeSelector:
        house.io/sandbox: "yes"
      tolerations:
        - key: house.io/sandbox
          operator: Equal
          value: "yes"
          effect: NoSchedule
    YAML
    kubectl -n rtc run tol-pod --image=busybox --restart=Never \
      --overrides='{"spec":{"runtimeClassName":"house-tolerant"}}' -- sleep 300
    kubectl -n rtc get pod tol-pod -o wide
    kubectl -n rtc get pod tol-pod -o json \
      | python3 -c 'import sys,json; [print(t) for t in json.load(sys.stdin)["spec"]["tolerations"]]'
    ```

    The pod declared no tolerations and runs on a tainted node. Print the full list and count how
    many of the tolerations on the object you actually asked for — reference `:126-127` says the
    class's are *"appended (excluding duplicates)"*, and the rest are the defaults every pod gets.

13. Resolve the post's two lists against the pin. This is reading, and it is the point of the
    exercise:

    ```sh
    E=/path/to/pinned/website/content/en
    sed -n '30p;34,38p' $E/blog/_posts/2018/runtimeclass.md
    sed -n '46,48p;98,102p;113,118p' $E/docs/concepts/containers/runtime-class.md
    sed -n '44p' $E/docs/reference/kubernetes-api/node/runtime-class-v1.md | tr '.' '\n' | grep -i 'assum\|specific'
    ```

    Take the five extensions one at a time and mark each as absent or contradicted. Three of the
    five have a sentence at the pin that assumes the opposite of the thing the post wanted to build;
    find all three. Then the two at `:30` that did land, and for each one name the difference between
    what was floated and what shipped.

14. The two Learn More links. Check the fragment first, then the KEP path:

    ```sh
    grep -n '^##\|{#' $E/docs/concepts/containers/runtime-class.md
    sed -n '171,175p' $E/docs/concepts/containers/runtime-class.md
    sed -n '44,45p' $E/blog/_posts/2018/runtimeclass.md
    ```

    The post's `:44` names a fragment; list the page's anchors and say whether it exists. The post's
    `:45` names a flat KEP file; `:171` names a numbered directory. Take the number from `:171` and
    from `:175`, and do not take either from memory.

**Expect**

Step 1 shows one row for `node.k8s.io`, `runtimeclasses`, `false` under NAMESPACED, and one served
version. No objects yet.

Step 2 is the whole exercise in one command. `kubectl explain runtimeclass.spec` cannot describe a
field that does not exist, and whatever `kubectl` says about that is your answer to `:24`. The other
three explains all resolve: `handler` on the RuntimeClass, `runtimeClassName` on the Pod.

Step 3: six field rows for the object itself, four of them not boilerplate, no `spec` and no
`status`. The concept page's sentence says two. Step 4: three `feature-state` shortcodes on
`runtime-class.md` and one on `pod-overhead.md`; three gate files matching runtime or overhead; and
no gate file anywhere whose subject is RuntimeClass scheduling.

Step 5: no `--enable-admission-plugins` on a kubeadm API server, `RuntimeClass` present in the
nineteen defaults, and a plugin section describing one mutation and one rejection.

Step 6 accepts both classes, including the one naming a handler that exists nowhere. Step 7 gives
you a running pod and a `Failed` one; the failure is visible in an event and nowhere in the pod's
own fields.

Step 8: the dotted name is accepted and the dotted handler is not, and the patch is refused for
immutability. Expect `grep -c immutable` on the concept page to be zero.

Step 9 prints an `overhead` the pod never declared. Step 10 is rejected for declaring it. Step 11
prints a `nodeSelector` the first pod never declared and rejects the second for disagreeing with it.
Step 12 places a pod on a tainted node and prints more tolerations than you wrote — the class's one,
plus the two `node.kubernetes.io` defaults every pod is given.

Steps 13 and 14 produce notes rather than output: five extensions, three of them contradicted by an
explicit assumption; two predictions, both landed in a different shape; one dead fragment; one KEP
that acquired a number.

**Read on**

- [The CRI exercise](../2016/13-container-runtime-interface-cri-in-kubernetes.md) — for the interface
  that interprets `handler`, and for what became of the two switches that first turned it on.
- [The containerd exercise](../2017/08-containerd-container-runtime-options-kubernetes.md) — for
  `/etc/containerd/config.toml`, the major-version question step 6 leans on, and where a handler
  name comes from.
- [The extensible admission exercise](01-extensible-admission-is-beta.md) — for the difference
  between the compiled-in plugin that does the work in steps 9 to 12 and a webhook that could do the
  same work from outside.
- [The dynamic kubelet configuration exercise](05-dynamic-kubelet-configuration.md) — for the other
  2018 node feature whose fields the API still carries after the machinery behind them was removed.
  There the surviving field does nothing; here the surviving controller does all the work.

**Teardown**

```sh
kubectl delete ns rtc
kubectl delete runtimeclass house-runc house-absent house-overhead house-sandboxed house-tolerant
kubectl taint node k8s-worker house.io/sandbox=yes:NoSchedule-
kubectl label node k8s-worker house.io/sandbox-
kubectl get runtimeclass; kubectl describe node k8s-worker | grep -i 'taints\|house.io'; true
```

Remove the taint before the label, and check both with the last line. A worker left tainted
`NoSchedule` will silently refuse to run anything for every later exercise on this cluster, and
RuntimeClasses are cluster-scoped, so deleting the namespace does not remove any of the five
objects.
