<a id="dynamic-resource-allocation"></a>

# The gate this post names is stable and locked at the pin, and its recorded ladder begins four releases after publication, because the alpha announced here was moved to a second gate that is now removed, and of 487 gate bodies only those two share their opening sentence word for word

**Post** — [Kubernetes 1.26: Alpha API For Dynamic Resource Allocation](https://kubernetes.io/blog/2022/12/15/dynamic-resource-allocation/),
2022-12-15.

14,295 bytes over 334 lines, by Patrick Ohly (Intel) and Kevin Klues (NVIDIA): the longest of the
year's thirteen `walk` posts, and ninth-largest of its sixty-nine. It announces an alpha API,
describes four new kinds, prints two worked manifests, and closes with a call for hardware vendors
to try the feature and write drivers.

**As written**

Dynamic resource allocation is a new API for requesting resources, *a generalization of the
persistent volumes API for generic resources* (`:11-12`). It makes three things possible that the
resource model of the day did not: sharing one resource instance across pods and containers,
attaching arbitrary constraints to a request, and initialising a resource from user-supplied
parameters (`:14-17`). Interpreting those parameters, tracking the hardware and allocating it are
all the third-party driver's job (`:19-20`).

It is alpha, so two switches must be thrown: the `DynamicResourceAllocation` feature gate on
kube-apiserver, kube-scheduler, kube-controller-manager and the kubelet, and the
`resource.k8s.io/v1alpha1` API group through `--runtime-config` (`:22-30`). The scheduler's
`DynamicResources` plugin is enabled by the default configuration if and only if the gate is
(`:32-34`).

The group provides four kinds (`:43-66`). ResourceClass says which driver handles a kind of resource
and carries common parameters; a cluster administrator creates one when installing a driver.
ResourceClaim is a particular instance a workload needs, created by a user or generated for a Pod
from a ResourceClaimTemplate. ResourceClaimTemplate is the generator. PodScheduling is used
internally by the control plane and the drivers to coordinate scheduling while claims are being
allocated. Parameters for the first two live in *separate objects*, typically a CRD the driver
installs (`:68-71`).

Two fields appear on the Pod. `spec.resourceClaims` lists the claims the Pod needs, each entry
naming either a ResourceClaim or a ResourceClaimTemplate (`:73-79`); a container opts in through
`resources.claims` (`:81-85`). The worked example at `:87-149` invents a driver called
`resource-driver.example.com`, a class, a `ClaimParameters` CRD holding `color: black` and `size:
large`, a ResourceClaimTemplate pointing at it through `parametersRef`, and a Pod whose two
containers each claim one cat.

The scheduling section is the design (`:151-195`). The scheduler has no idea what dynamic resources
exist or how they divide — drivers do, and drivers mark claims allocated. A claim can be allocated
the moment it is created (*immediate allocation*) or, by default, deferred until a Pod needs it
(*wait for first consumer*), and the post says outright that this two-mode design is *similar to how
Kubernetes handles storage provisioning with PersistentVolumes and PersistentVolumeClaims*
(`:166-167`). In the deferred mode the scheduler creates a PodScheduling object named after the Pod,
writes the nodes it is considering into it, and the drivers write back the nodes they cannot serve;
the scheduler picks one, records the choice, the drivers allocate, and only then is the Pod bound
(`:169-185`). The section ends on the promise the whole handshake exists to keep: a Pod is not
scheduled until every one of its resources is allocated and reserved, because a Pod that lands
somewhere it cannot run also pins the RAM and CPU set aside for it (`:191-195`).

Two things are flagged as unfinished. *Limitations* (`:197-204`) says setting `nodeName` bypasses
the scheduler and produces Pods the kubelet refuses to start, and links the issue that might remove
that limitation later. And the driver-writing section (`:206-232`) points at two Go packages on the
`release-1.26` branch, at KEP-3063, and at an example driver that SIG Node *plans* to provide. The
last third (`:234-318`) is a runnable walkthrough: build a cluster from the Kubernetes source with
`local-up-cluster.sh`, run the e2e test driver's controller and kubelet plugin by hand, and watch a
ResourceClaim reach `allocated,reserved`.

**As it runs now**

The gate is on and cannot be turned off. `DynamicResourceAllocation` reads stable, `defaultValue:
true`, `locked: true` from v1.35, which is the release the lab runs. The API group is
`resource.k8s.io/v1`, served by default; the beta groups the post's successors used are not, and a
cluster that wants them has to ask through `--runtime-config` (`set-up-dra-cluster.md:47-57`). So
the two switches the post tells you to throw are one switch that no longer moves and one group name
that no longer resolves.

Of the four kinds, one survives unchanged, one survives with its contents replaced, one was renamed
and one was deleted — and a fifth was added, so the count is still four. ResourceClaimTemplate is
the survivor. ResourceClaim keeps its name and loses its body: `resourceClassName` and
`parametersRef` are gone and `spec.devices.requests[]` is there instead, each request referencing a
DeviceClass and narrowing it with selectors (`dra-api.md:73-77`). ResourceClass became DeviceClass,
which is no longer *which driver handles this* but *a category of devices, and the CEL that selects
within it* (`:59-66`). PodScheduling is gone with the handshake it carried. ResourceSlice took the
empty slot, and it points the other way: drivers publish what they have, and the **scheduler**
allocates from it (`how-dra-works.md:40-71`).

The Pod fields survive with one level removed. The post nests the reference under `source:`; at the
pin `resourceClaimName` and `resourceClaimTemplateName` sit directly on the list entry, and
`examples/dra/dra-example-job.yaml` is the post's own example in the pin's spelling — three
containers, one claim generated from a template and one shared by name between the other two.
Nothing in the tree explains that the nesting went away.

And the documentation the post links has moved.
`/docs/concepts/scheduling-eviction/dynamic-resource-allocation/` is now
`/docs/concepts/resource-management/dynamic-resource-allocation/`, six pages rather than one, and
the post's link still works because the new section's front matter carries the old path as an
`aliases:` entry (`_index.md:7-8`). Ninety-three references to the old path survive across 54 files,
36 of them current documentation pages. One line of front matter is holding all of them up.

The fourth thing to say here is not a behaviour. The pinned tree disagrees with itself about what
this feature's history was. The gate file named in the post records a ladder that starts at alpha
v1.30 — four releases after this post announced the alpha — and the 1.26 alpha the post is *about*
is recorded in a different file, under a different name, marked removed. Neither file mentions the
other.

**What this exercise does not cover, and where it lives**

A working allocation. There is no DRA driver on any topology in this repo and no hardware behind
one, so nothing here allocates a device; every claim in *Do* stays unallocated on purpose, and that
is the state the exercise reads. Seeing DRA actually hand a device to a Pod needs a fake driver, and
a later year's row owns that: the 1.34 GA announcement is a `walk` in 2025 and its census entry
names this exercise as the thing it continues.

The gate archaeology of *renaming* belongs to two rows of this year, not to this one. [The one gate
file in 487 that records its former name](08-pod-has-network-condition.md) owns `former_titles:`,
and [a rename recorded once, forward only, in prose](10-userns-alpha.md) owns the case where a
retired gate's body names its successor. This row is the third member of that set and only the
third: a replacement recorded in neither way.

Device plugins, extended resources and the older accelerator model are not compared here. The
scheduler message that reports insufficient CPU is [a lab
exercise](../../labs/05/15-the-line-that-writes-insufficient-cpu.md) and the shape of a
`FailedScheduling` event is taken from there rather than re-derived. Structured parameters as a
design — what CEL selection buys, how autoscaling reads a ResourceSlice — is later years' ground and
is named, not explained.

**The diff, and why**

Five of the seven cases apply at once, which is what a post announcing the first version of a design
that was later thrown away looks like.

**A plan the project abandoned.** Not the feature — the mechanism. Every sentence in the post's
scheduling section describes allocation performed by the driver's control-plane controller, with the
scheduler reduced to proposing nodes through a PodScheduling object and waiting. At the pin the
scheduler allocates, from ResourceSlices that drivers publish, and PodScheduling does not exist. The
two allocation modes went with it: the post's *immediate* and *wait for first consumer* are not
modes at the pin, and `allocationMode` is still a field name but now takes `ExactCount` or `All` and
counts devices in a request (`resource-claim-v1.md:425`). The stated analogy to PersistentVolumes at
`:166-167` is the clearest casualty — the design was abandoned in the direction of *less* like
storage provisioning, not more.

**Broke.** *Running the test driver* (`:234-318`) cannot be followed at all. It wants
`RUNTIME_CONFIG=resource.k8s.io/v1alpha1` for a group version that is not served,
`FEATURE_GATES=DynamicResourceAllocation=true` for a gate that is locked on and rejects the
assignment, a `test/e2e/dra/test-driver` layout from the `release-1.26` branch, and CRI-O v1.23.2
because containerd v1.7.0 had not shipped. Four independent reasons, any one of them fatal. This is
also the part of the post that would have taught the most, and it is the part that decayed fastest.

**Wrong when it was published, and never corrected.** Line 123 of the post is `–--`: an en dash
followed by two hyphens, where a YAML document separator should be. The block it sits in is the only
end-user-facing example the post gives, and it does not parse — the Pod is swallowed into the
ResourceClaimTemplate above it. The first manifest has its own defect, `name:` at the top level of a
`ResourceClass` with no `metadata:` (`:93-98`), which is invalid however the group version is
spelled. Four years of an archive nobody edits, and step 3 is the first time either has been run.

**Still right, and it is the part the post apologised for.** *Limitations* (`:197-204`) flags the
pre-scheduled Pod as a defect that might be fixed later. It was not fixed; it was promoted. At the
pin it is a section of its own, *Pre-scheduled Pods* (`how-dra-works.md:73-105`), which says the
same thing in more words, adds the reason — a Pod assigned to a node blocks RAM and CPU that nothing
else can use while it is stuck — and prescribes the workaround the post did not have, a
`nodeSelector` that pins the Pod without bypassing the scheduler. The promise at `:191-195` survived
the entire rewrite intact, and it is the one claim in the post that a cluster with no driver at all
can still be made to demonstrate.

**Never absorbed.** Three of the post's words have gone to zero in the documentation tree and
survive, in the whole of `content/en`, in exactly one file: this post. `ResourceClass` and
`PodScheduling` occur in no other file at all; `parametersRef` occurs in one unrelated Gateway API
post that happens to use the same field name. The post is the last surviving record of its own
vocabulary and has no way to know it. And the *replacement* is narrated in three places, all of them
blog posts and none of them documentation: the v1.31 release announcement, which introduces the name
`DRAControlPlaneController` and calls the old design *classic DRA* and says it is *still supported*
(`kubernetes-v1-31-release.md:169-174`); and a 2026 working-group spotlight in which this post's own
author says he wrote the first KEP and then *started over with a second KEP*
(`wg-device-management-spotlight.md:25`), while a third co-chair gives the reason nothing else in
the tree gives — the initial implementation made autoscaling very challenging (`:27`). Naming only
*still right* here would miss all of it.

The ladder is per gate, and the subject spans two. The gate the post tells you to enable:

`DynamicResourceAllocation`

| stage | default | locked | releases |
|---|---|---|---|
| alpha  | `false` | —       | v1.30 – v1.31 |
| beta   | `false` | —       | v1.32 – v1.33 |
| stable | `true`  | `false` | v1.34 |
| stable | `true`  | `true`  | v1.35 – |

`DRAControlPlaneController`

| stage | default | locked | releases |
|---|---|---|---|
| alpha  | `false` | —      | v1.26 – v1.31 |

`DRAControlPlaneController.md` declares `removed: true`; `DynamicResourceAllocation.md` does not.
The second gate is the feature this post announces — alpha from v1.26, the release in the post's
title — and it did not exist under that name until v1.31, when the first gate was re-pointed at a
design that had been built beside it. The first gate's table therefore records a ladder for a
feature that is not the one it was created for, and the release this post is about appears in
neither row of it.

Two file-level facts sit under the tables rather than in them. `DynamicResourceAllocation` is one of
exactly **two** gate files in 487 that write `locked: false` — the other, `DRAPrioritizedList`, is
also a DRA gate — and that flag is the only reason its stable stage is two rows: v1.34 shipped it on
but overridable, v1.35 nailed it shut. And of the 230 files that declare `removed: true`,
`DRAControlPlaneController` is one; what it is not is one of the files whose body names the gate
that replaced it. There is no pointer in either direction.

What the two bodies do share is their opening sentence, word for word: *Enables support for
resources with custom parameters and a lifecycle that is independent of a Pod.* Then one says
allocation is handled *by the Kubernetes scheduler based on "structured parameters"* and the other
says *by a resource driver's control plane controller*. That is the entire recorded difference
between the design this post describes and the design that replaced it — one clause, in two files
that do not acknowledge each other. Step 10 counts how unusual that is: across all 487 gate bodies,
exactly two pairs share a first sentence, and the other pair is the opposite case — `SELinuxMount`'s
body names `SELinuxMountReadWriteOncePod` and says it widens it, both are alive, and both are still
climbing. A shared sentence marks a family. Only one of the two families has a pointer in it.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 vCPU, at `10.10.10.180`,
running Kubernetes v1.35. Nothing here needs a second node, and nothing here needs hardware: every
claim in *Do* is expected to stay unallocated, because a cluster with no DRA driver publishes no
ResourceSlices and the scheduler has nothing to allocate from. That is the point rather than a
limitation of the lab. Steps 7 to 10 are offline and read the pinned checkout.

**Do**

1. What this cluster serves, before touching the post at all.

   ```sh
   kubectl api-versions | grep resource.k8s.io
   kubectl api-resources --api-group=resource.k8s.io
   kubectl get deviceclasses
   kubectl get resourceslices
   kubectl create ns dra
   ```

2. The post's ResourceClass, copied from `:93-98` without a character changed.

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: resource.k8s.io/v1alpha1
   kind: ResourceClass
   name: resource.example.com
   driverName: resource-driver.example.com
   YAML
   echo "apply exit $?"
   kubectl explain resourceclass 2>&1 | head -2
   ```

3. The post's second block (`:103-149`), abridged only after line 20 by dropping the Pod's duplicate
   second container and its claim. Write it to a file first, because the first failure is a single
   byte and you will want to look at it. Then repair that byte and nothing else, and apply again.

   ```sh
   cat > /tmp/post-block.yaml <<'YAML'
   ---
   apiVersion: cats.resource.example.com/v1
   kind: ClaimParameters
   name: large-black-cats
   spec:
     color: black
     size: large
   ---
   apiVersion: resource.k8s.io/v1alpha1
   kind: ResourceClaimTemplate
   metadata:
     name: large-black-cats
   spec:
     spec:
       resourceClassName: resource.example.com
       parametersRef:
         apiGroup: cats.resource.example.com
         kind: ClaimParameters
         name: large-black-cats
   –--
   apiVersion: v1
   kind: Pod
   metadata:
     name: pod-with-cats
   spec:
     containers:
     - name: first-example
       image: ubuntu:22.04
       command: ["sleep", "9999"]
       resources:
         claims:
         - name: cat-0
     resourceClaims:
     - name: cat-0
       source:
         resourceClaimTemplateName: large-black-cats
   YAML
   kubectl apply -n dra -f /tmp/post-block.yaml; echo "apply exit $?"
   sed -n '20p' /tmp/post-block.yaml | od -An -tx1 | tr -s ' ' | sed 's/^ //; s/ *$//'
   sed '20s/.*/---/' /tmp/post-block.yaml > /tmp/post-block-fixed.yaml
   kubectl apply -n dra -f /tmp/post-block-fixed.yaml; echo "apply exit $?"
   ```

4. Ask the cluster where the field the post nests under `source:` went.

   ```sh
   kubectl explain pod.spec.resourceClaims | sed -n '1,22p'
   kubectl explain resourceclaim.spec | sed -n '1,14p'
   ```

5. The pin's own manifests for the same idea, from `examples/dra/deviceclass.yaml` and
   `examples/dra/resourceclaim.yaml`, with the CEL attribute selectors dropped because there are no
   device attributes here to select on.

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: resource.k8s.io/v1
   kind: DeviceClass
   metadata:
     name: example-device-class
   spec:
     selectors:
     - cel:
         expression: device.driver == "driver.example.com"
   YAML
   kubectl apply -n dra -f - <<'YAML'
   apiVersion: resource.k8s.io/v1
   kind: ResourceClaim
   metadata:
     name: example-resource-claim
   spec:
     devices:
       requests:
       - name: single-gpu-claim
         exactly:
           deviceClassName: example-device-class
   YAML
   kubectl -n dra get resourceclaim example-resource-claim -o yaml | sed -n '/^status:/,$p'
   ```

6. A Pod that claims it, in the pin's spelling, and then the post's own limitation at `:199-204`: a
   second Pod identical but for `nodeName`, which takes the scheduler out of the path. Give each of
   them time to settle and write down what the cluster says about both.

   ```sh
   kubectl apply -n dra -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata:
     name: pod-with-cats
   spec:
     containers:
     - name: first-example
       image: registry.k8s.io/pause:3.10
       resources:
         claims:
         - name: cat-0
           request: single-gpu-claim
     resourceClaims:
     - name: cat-0
       resourceClaimName: example-resource-claim
   YAML
   NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl apply -n dra -f - <<YAML
   apiVersion: v1
   kind: Pod
   metadata:
     name: pod-with-cats-pinned
   spec:
     nodeName: $NODE
     containers:
     - name: first-example
       image: registry.k8s.io/pause:3.10
       resources:
         claims:
         - name: cat-0
           request: single-gpu-claim
     resourceClaims:
     - name: cat-0
       resourceClaimName: example-resource-claim
   YAML
   kubectl -n dra wait --for=condition=Ready pod/pod-with-cats --timeout=60s; echo "wait exit $?"
   kubectl -n dra get pods -o wide
   for pod in pod-with-cats pod-with-cats-pinned; do
     echo "--- $pod ---"
     kubectl -n dra get events --field-selector involvedObject.name=$pod \
       -o custom-columns=REASON:.reason,MESSAGE:.message | tail -3
   done
   ```

7. Offline from here. The two gate files, side by side, ladders and bodies.

   ```sh
   cd /path/to/kubernetes/website/content/en/docs/reference/command-line-tools-reference/feature-gates
   for g in DynamicResourceAllocation DRAControlPlaneController; do
     echo "--- $g ---"
     sed -n '/^stages:/,/^---$/p' "$g.md" | grep -v '^$'
     awk '/^---$/{n++; next} n>=2 && NF' "$g.md" | sed 's/^/| /'
   done
   ```

8. Where the replacement is written down, and where it is not.

   ```sh
   cd /path/to/kubernetes/website/content/en
   echo '--- files naming the retired gate ---'
   grep -rl 'DRAControlPlaneController' --include='*.md' . | sed 's|^\./||'
   printf 'of which under docs/   %s\n' \
     "$(grep -rl 'DRAControlPlaneController' --include='*.md' docs | wc -l | tr -d ' ')"
   echo '--- what the prose says ---'
   grep -rnoE '.{0,16}classic DRA.{0,56}' --include='*.md' . | sed 's|^\./||'
   ```

9. The post's own vocabulary, counted two ways: files under `docs`, and files anywhere in
   `content/en`. Word-bounded, so a plural does not count and `ResourceClaimTemplate` does not count
   as `ResourceClaim`.

   ```sh
   for t in ResourceClass ResourceClaim ResourceClaimTemplate PodScheduling parametersRef; do
     printf '%-22s docs %-4s content/en %s\n' "$t" \
       "$(grep -rlw "$t" --include='*.md' docs | wc -l | tr -d ' ')" \
       "$(grep -rlw "$t" --include='*.md' . | wc -l | tr -d ' ')"
   done
   echo '--- the files that still carry the two dead kinds ---'
   grep -rlw 'ResourceClass' --include='*.md' . | sed 's|^\./||'
   grep -rlw 'PodScheduling' --include='*.md' . | sed 's|^\./||'
   echo '--- the post group version, two matching rules ---'
   printf 'loose     %s\n' "$(grep -ro 'resource\.k8s\.io/v1alpha1' --include='*.md' docs | wc -l | tr -d ' ')"
   printf 'anchored  %s\n' "$(grep -roE '(^|[^.a-z])resource\.k8s\.io/v1alpha1' --include='*.md' docs | wc -l | tr -d ' ')"
   ```

10. How unusual a shared opening sentence is. Unwrap each gate body onto one line before splitting
    it, because the files are hand-wrapped at whatever width the author used and a first-*line* rule
    answers a different question.

    ```sh
    cd /path/to/kubernetes/website/content/en/docs/reference/command-line-tools-reference/feature-gates
    for f in *.md; do
      grep -q '^content_type: feature_gate' "$f" || continue
      b=$(awk '/^---$/{n++; next} n>=2' "$f" | tr '\n' ' ' | tr -s ' ')
      printf '%s\t%s\n' "${b%%. *}" "${f%.md}"
    done | sort > /tmp/gate-sentences.txt
    printf 'gate files                 %s\n' "$(wc -l < /tmp/gate-sentences.txt | tr -d ' ')"
    printf 'removed among them         %s\n' "$(grep -l 'removed: true' *.md | wc -l | tr -d ' ')"
    cut -f1 /tmp/gate-sentences.txt | uniq -d > /tmp/gate-shared.txt
    printf 'shared first sentences     %s\n' "$(wc -l < /tmp/gate-shared.txt | tr -d ' ')"
    grep -Ff /tmp/gate-shared.txt /tmp/gate-sentences.txt | cut -f2 | sed 's/^/  /'
    ```

**Expect**

Step 1 establishes that the feature the post calls alpha is now the floor. `kubectl api-versions`
prints `resource.k8s.io/v1` and nothing else from that group — the beta versions exist but are not
served by default, which is what `set-up-dra-cluster.md:47-57` means when it tells an administrator
to enable them. `api-resources` lists four kinds: `deviceclasses`, `resourceclaims`,
`resourceclaimtemplates`, `resourceslices`. Both `get` commands print `No resources found`, and the
second one is the whole reason the rest of this exercise reads states rather than outcomes: no
driver is installed, so no ResourceSlice exists, so nothing can be allocated. If `get deviceclasses`
instead answers `error: the server doesn't have a resource type "deviceclasses"`, the API group has
been disabled on this cluster — that exact message and its cause are at
`set-up-dra-cluster.md:76-83`, and the rest of this exercise will not run until it is fixed.

Step 2 fails on the version, not on the shape. The error names `resource.k8s.io/v1alpha1` and the
kind `ResourceClass`, the exit status is non-zero, and `kubectl explain resourceclass` has nothing
to say either. Read that as two separate deaths reported as one: the group version was retired, and
so was the kind. The manifest would not have applied even against a 1.26 cluster — `name:` sits at
the top level with no `metadata:` — but nothing here gets far enough to tell you that.

Step 3 fails twice, differently, and the difference is the point. The first `apply` reports a YAML
parse error that names a **line number** rather than a kind, because the document separator at line
20 is not one. The byte dump shows why:

```
e2 80 93 2d 2d 0a
```

A separator is three `2d` bytes. This line opens with `e2 80 93`, the UTF-8 spelling of U+2013 EN
DASH, and has only two hyphens after it — so `–--` never separated anything and the Pod below it was
read as a continuation of the ResourceClaimTemplate above. The second `apply`, with that one byte
repaired and nothing else touched, gets past the parser and fails on the API instead: no matches for
kind in `resource.k8s.io/v1alpha1`. Two failures, four years apart in origin, stacked in one code
block.

Step 4 shows where the post's nesting went. `kubectl explain pod.spec.resourceClaims` lists `name`,
`resourceClaimName` and `resourceClaimTemplateName` as direct fields; there is no `source`. `kubectl
explain resourceclaim.spec` lists `devices`, and does not list `resourceClassName` or
`parametersRef`. The post's Pod is one level of nesting and two field names away from a valid
manifest, and no page in the tree records either change.

Step 5 succeeds, which is the surprise. Both objects are accepted — a DeviceClass that selects a
driver nobody installed, and a ResourceClaim that requests a device from it. The claim's `status` is
empty or absent: no `allocation`, no `reservedFor`. An unsatisfiable claim is a perfectly valid
object, and the API server has no opinion about whether anything can ever fill it.

Step 6 is the post's design promise, observed on a cluster that could never keep it. `wait` times
out with a non-zero exit. `pod-with-cats` is `Pending` with no node assigned, and its events carry a
`FailedScheduling` whose message says the claim cannot be allocated — record the exact wording,
which differs between releases. That is `:191-195` still true: the scheduler declines to place a Pod
whose resources are not allocated and reserved, and it declines for exactly the reason given there.
`pod-with-cats-pinned` shows the other half. It has a node from the moment it is created, because
you gave it one, and it will sit there not running — the kubelet will not start a container whose
claim is not reserved, and it re-checks rather than failing outright. That is `:199-204`, promoted
since to a documented section with a prescribed workaround (`how-dra-works.md:73-105`). The
limitation the post hoped to remove is the one thing on this page that has not changed.

Step 7 is the exercise in one fence:

```
--- DynamicResourceAllocation ---
stages:
  - stage: alpha
    defaultValue: false
    fromVersion: "1.30"
    toVersion: "1.31"
  - stage: beta
    defaultValue: false
    fromVersion: "1.32"
    toVersion: "1.33"
  - stage: stable
    defaultValue: true
    locked: false
    fromVersion: "1.34"
    toVersion: "1.34"
  - stage: stable
    defaultValue: true
    locked: true
    fromVersion: "1.35"
---
| Enables support for resources with custom parameters and a lifecycle
| that is independent of a Pod. Allocation of resources is handled
| by the Kubernetes scheduler based on "structured parameters".
--- DRAControlPlaneController ---
stages:
  - stage: alpha
    defaultValue: false
    fromVersion: "1.26"
    toVersion: "1.31"
removed: true
---
| Enables support for resources with custom parameters and a lifecycle
| that is independent of a Pod. Allocation of resources is handled
| by a resource driver's control plane controller.
```

Two identical opening lines and one changed clause. The release in this post's title appears in the
second file only, and the second file is the one marked removed.

Step 8 prints where that is explained:

```
--- files naming the retired gate ---
docs/reference/command-line-tools-reference/feature-gates/DRAControlPlaneController.md
blog/_posts/2024/kubernetes-v1-31-release.md
of which under docs/   1
--- what the prose says ---
blog/_posts/2024/kubernetes-v1-31-release.md:171: is now called "classic DRA".
blog/_posts/2024/kubernetes-v1-31-release.md:173:bernetes v1.31, classic DRA has a separate feature gate named `DRAControlPlaneContr
blog/_posts/2026/wg-device-management-spotlight.md:25: (now known as “classic DRA”) and implemented most of it, then started over with a
```

Two files name the gate: its own file, and one blog post. The single `docs/` hit is the gate file
itself, so no documentation page anywhere explains the split. What does explain it is a release
announcement, and the window cuts the front off its own first sentence: line 171 reads in full
*Allocation by a DRA driver controller is still supported through what is now called "classic DRA"*,
which the pin contradicts, because the gate behind that sentence was removed at v1.31. The second
explanation is a working-group interview four years later in which this post's own author says he
wrote the first KEP and then started over. Both are news; neither is documentation.

Step 9 counts the vocabulary:

```
ResourceClass          docs 0    content/en 1
ResourceClaim          docs 30   content/en 46
ResourceClaimTemplate  docs 17   content/en 23
PodScheduling          docs 0    content/en 1
parametersRef          docs 0    content/en 2
--- the files that still carry the two dead kinds ---
blog/_posts/2022/dynamic-resource-allocation-alpha/index.md
blog/_posts/2022/dynamic-resource-allocation-alpha/index.md
--- the post group version, two matching rules ---
loose     2
anchored  0
```

`ResourceClass` and `PodScheduling` each survive in exactly one file in the whole of `content/en`,
and it is the same file both times: this post. `parametersRef`'s second file is a Gateway API post
that uses the same field name for an unrelated feature, which is the sort of thing a name-only count
cannot see. The last pair is the matching-rule lesson. A loose grep for the post's group version
finds two hits in `docs` and would let you write *it is still there*; both are
`metadata.resource.k8s.io/v1alpha1`, a different group whose name happens to end the same way.
Anchored, the answer is zero.

Step 10 puts the shared sentence in proportion:

```
gate files                 487
removed among them         230
shared first sentences     2
  DRAControlPlaneController
  DynamicResourceAllocation
  SELinuxMount
  SELinuxMountReadWriteOncePod
```

Two pairs out of 487. The other pair is what a documented family looks like: both alive, both
climbing, and `SELinuxMount`'s body says in so many words that it widens the improvements behind
`SELinuxMountReadWriteOncePod`. This pair has the shared sentence and none of the rest. If you run
the same count on first *lines* instead of first sentences you get ten collisions, all of them
artefacts of where the authors happened to wrap their paragraphs — the unwrapping in step 10 is not
tidiness, it is the difference between counting sentences and counting line breaks.

**Read on**

1. `blog/_posts/2024/kubernetes-v1-31-release.md:166-177`, the paragraph that splits the feature in
   two. Read it for what it does not say: it introduces `DRAControlPlaneController` as a gate you
   can enable, never mentions that `DynamicResourceAllocation` has just changed meaning underneath
   you, and gives KEP-3063 as the reference for both designs. It is a `skip` row in its year's
   census, so no exercise will ever be built on it.

2. `blog/_posts/2026/wg-device-management-spotlight.md:25` and `:27`. Patrick Ohly, one of this
   post's two authors: he wrote the first KEP, implemented most of it, *then started over with a
   second KEP*. John Belamaric gives the reason nothing in the documentation tree gives — the
   initial implementation made autoscaling very challenging, and that is why there was concern in
   the community about advancing it to beta. Two sentences in an interview are the only account of
   why the API in this post does not exist.

3. `docs/concepts/resource-management/dynamic-resource-allocation/how-dra-works.md:40-105`. The
   replacement design and the surviving limitation, in that order. Compare `:40-71` against the
   post's `:169-185` handshake — the same three parties, the arrows reversed — and `:73-105` against
   the post's `:197-204`, where the wording is close enough that you can see one was written with
   the other open.

4. `examples/dra/dra-example-job.yaml` beside the post's `:124-149`. A Job rather than a bare Pod
   and three containers rather than two, but the same shape: `resources.claims` on each container,
   and a `resourceClaims` list naming one template-generated claim and one shared by name. Three
   names changed and one level of nesting disappeared. Reading them side by side is a faster way to
   learn the current shape than reading the API reference.

5. *Unanswerable from the pin:* whether anything was ever deployed against the v1alpha1 API. The
   post asks hardware vendors to write drivers (`:332-334`), and by 1.31 the design those drivers
   would have targeted was renamed to *classic* and gated separately, and by 1.32 it was gone. The
   pin holds one revision of a documentation tree; it has no issue history, no vendor announcements
   and no download figures. What it can tell you is that the call to action and the removal of the
   thing it called for are two years apart, which is short.

**Teardown**

```sh
kubectl delete ns dra
kubectl delete deviceclass example-device-class
rm -f /tmp/post-block.yaml /tmp/post-block-fixed.yaml \
  /tmp/gate-sentences.txt /tmp/gate-shared.txt
```
