<a id="userns-alpha"></a>

# The rename this gate underwent is recorded once, forward only, and in prose, where the year's other rename is recorded twice and machine-readably; the feature is four gates at the pin, the one the post names is the dead one, and the containerd forecast missed a major version

**Post** — [Kubernetes 1.25: alpha support for running Pods with user namespaces](https://kubernetes.io/blog/2022/10/03/userns-alpha/),
2022-10-03.

2,864 bytes, 81 lines, two authors: Rodrigo Campos of Microsoft and Giuseppe Scrivano of Red Hat.
Tenth of 2022's thirteen `walk` verdicts, and the shortest of them by a wide margin — the next
shortest is 4,540 bytes and the longest 14,295. Four years on, the feature it announces in those
2,864 bytes has a 323-line concept page, a 111-line task page, four feature-gate files and two
kubelet metrics of its own.

**As written**

One sentence of announcement, `:11`: Kubernetes v1.25 introduces the support for user namespaces.
Then the security case, `:13-16` — each pod will have access only to a limited subset of the
available UIDs and GIDs on the system — and a number, `:19-20`: a process running on Linux can use
up to 4294967296 different UIDs and GIDs. `:22-26` explains what a user namespace is, and `:28-43`
explains why it matters, in two bullets at `:31-34` — restricting the IDs a pod can use, and running
workloads as root in a safer manner — and a paragraph at `:36-39` on root inside the pod being a
non-zero ID from the host's point of view.

The instructions are three sentences and one manifest. `:46-47`: you must enable it for a pod
setting `hostUsers` to `false` under the pod spec stanza. `:48-56`: the manifest. `:58-60`: make
sure to enable the `UserNamespacesStatelessPodsSupport` gate. `:62-69`: the runtime must also
support user namespaces, with containerd support planned for the 1.7 release, CRI-O having it in
v1.25, and `cri-dockerd` not planning it. `:74-81` is the usual invitation to the SIG.

What is not in it is as short a list. The body never uses the word *alpha*; the word appears only in
the title and the slug. *Beta* and *stable* do not appear at all. *Stateless* appears exactly once,
at `:59`, inside the gate name — the single most consequential word in the post, and it is there as
a substring rather than as a claim. The post announces a feature whose scope limit is encoded in its
own gate name and never mentions the limit.

**What this exercise does not cover, and where it lives**

The obvious demonstration — `id` inside the container against the same process seen from the node,
and a file written in the container appearing on the host owned by a high unprivileged UID — is
booked by a later year's census row, which walks the post that announced the field on by default.
This exercise reads `/proc/self/uid_map` and the user-namespace inode instead, which is the narrower
and more falsifiable half of the same fact.

`UserNamespacesPodSecurityStandards`, the relaxation of the Pod Security Standards for
user-namespaced pods, and the node-side `/etc/subuid` configuration are owned by [the runc
CVE-2019-5736 exercise](../2019/02-runc-cve-2019-5736.md), which quotes the gate file's retirement
paragraph and runs a `hostUsers: false` pod under a restricted namespace. The ladder below names
that gate and points there rather than transcribing it.

The lifting of the stateless limit — running stateful pods, with volumes, in a user namespace — is a
post of its own in a later year and that year's row owns it. So does the graduation to stable. [The
PodHasNetwork exercise](08-pod-has-network-condition.md) owns the `former_titles:` field and the
other rename this year announced, and [the CRD validation rules
exercise](09-crd-validation-rules-beta.md) owns the count of live gates that no generated help text
names. Both are cited here; neither is recounted.

**The diff, and why**

**Retired by rename, not by graduating.** `UserNamespacesStatelessPodsSupport` ran alpha from 1.25
to 1.27 and its file declares `removed: true`. The feature did not stop: `UserNamespacesSupport`
begins again at alpha 1.28 and is stable and locked at 1.36. The interesting part is what records
the join. Of the 487 feature-gate files at the pin, exactly one carries a machine-readable
`former_titles:` field, and it belongs to the other rename this year announced. Exactly five name a
successor in prose. This is one of the five, and the sentence is in the *dead* gate's file: *This
feature gate was superseded by the `UserNamespacesSupport` feature gate in the Kubernetes v1.28
release.* `UserNamespacesSupport.md` says nothing about where it came from. The receipt runs one
way. The 2023 post that lifted the stateless limit states the rename too, at its `:66-70`, but a
blog post is an archive entry nobody goes back and edits; in the tree that is actually maintained,
the dead gate's own file is the only place the join is written down. Delete the file for the gate
nobody can set any more and the rename becomes untraceable from the tree. The project does keep such
files — 230 of the 487 are for gates that declare `removed: true` — so the record survives by
convention, not by design.

**Overtaken by its own growth.** One gate became four. `UserNamespacesSupport` is the feature;
`UserNamespacesStatelessPodsSupport` is the dead name; `UserNamespacesPodSecurityStandards` ran
alpha 1.29 to 1.34 and is removed; and `UserNamespacesHostNetworkSupport` arrived at alpha in 1.35
and is still alpha at the pin. That last one exists to unpick a limitation the feature shipped with
and the post never mentions: `hostUsers: false` forbids `hostNetwork: true`, and four years later
there is a gate whose whole purpose is to allow both at once. The field grew outward too. At the pin
`procMount: Unmasked` *requires* `spec.hostUsers` to be `false`
(`docs/tasks/configure-pod-container/security-context.md:820-824`, which notes that v1.12 to v1.29
did not enforce it), and `user.*` sysctls are skipped for any pod that shares the host user
namespace (`docs/tasks/administer-cluster/sysctl-cluster.md:265-266`). A field introduced as an
opt-in security boundary is now a precondition for other people's features.

**Wrong when it was published, and right in the same paragraph.** `:64-65` forecasts containerd
support in the 1.7 release. The pin says containerd version 2.0 and later
(`docs/concepts/workloads/pods/user-namespaces.md:59`) — a major version out. `:67` says CRI-O v1.25
has support; the pin says CRI-O version 1.25 and later (`:60`), exactly right and still exactly
right four years on. Two predictions, one paragraph, one of each. The miss is not academic for this
repo: Debian Trixie ships containerd 1.7.24, precisely the release the post named, which is why [the
lab node baseline](../../strands/lab-topologies.md) installs containerd 2.2.1 and runc 1.5.1 from
upstream tarballs. It does that for an unrelated reason — the CRI `RuntimeConfig` RPC — and the side
effect is that the lab clears this feature's runtime floor by accident.

**Never absorbed.** The manifest at `:49-55` has `apiVersion`, `kind` and `spec` and no `metadata`,
so it cannot be applied as it stands; its fence at `:48` carries no language tag; and its image is
`docker.io/nginx` with no tag. The pin's equivalent, `examples/pods/user-namespaces-stateless.yaml`,
is a complete object with a name and a command, and is what the task page hands a reader today. The
post's three-sentence instruction — set the field, enable the gate, check your runtime — survived
into the documentation as a 323-line concept page with a prerequisites section, five constraints on
the subuid range, a filesystem-support section and a metrics section. Nothing in the post was wrong
about the mechanism. It was simply the shortest possible statement of a feature that turned out to
need the longest possible one.

**The ladder**

Three tables, and a fourth gate that lives in another exercise.

`UserNamespacesStatelessPodsSupport`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.25 – v1.27 |

The file declares `removed: true`. One stage, three releases, then gone — and gone by rename, which
the stage table cannot express. A reader who has only this table sees a feature that was tried and
dropped.

`UserNamespacesSupport`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.28 – v1.29 |
| beta | `false` | — | v1.30 – v1.32 |
| beta | `true` | — | v1.33 – v1.35 |
| stable | `true` | `true` | v1.36 – |

Four rows for three stages, because beta happened twice: three releases off by default, then three
on. The last row carries `locked: true`, one of 49 gate files at the pin that lock a stage, so from
1.36 the gate exists and cannot be set to anything but `true`. Read the two tables end to end and
the feature took eleven releases from the post to stable — 1.25 to 1.36 — of which the first three
are filed under a name that no longer exists.

`UserNamespacesHostNetworkSupport`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.35 – |

Live at the pin and still alpha in its first release. It is named in all five generated
`--feature-gates` help texts. `UserNamespacesSupport`, stable and locked, is named in none of them —
one instance of the count [the CRD validation rules exercise](09-crd-validation-rules-beta.md)
measured at 119 live gates out of 257. The generated reference lists what the binaries still accept
on the command line, so a gate that can no longer be set falls off it; the practical effect is that
the newest and least finished of the four gates is the one most visible in the reference, and the
finished one is invisible.

`UserNamespacesPodSecurityStandards` is the fourth. Its ladder and its retirement paragraph belong
to [the runc CVE-2019-5736 exercise](../2019/02-runc-cve-2019-5736.md).

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 cores, at `10.10.10.180`,
running v1.35. That release matters: `UserNamespacesSupport` is beta and defaulting to `true` from
1.33 to 1.35 and stable-and-locked from 1.36, so v1.35 is the last release in which the feature is
both on and still settable, and a reader on 1.36 or later cannot turn it off to compare. Steps 2, 3,
4, 6 and 7 are `kubectl` against the apiserver, in a namespace called `uns`. Steps 1 and 5 need a
root shell on the node — `ssh zain@10.10.10.180` — for the runtime version and the host's own user
namespace. Steps 8 to 10 need no cluster; they read the pinned checkout.

**Do**

1. Establish the ground. The concept page states three prerequisites at `:34-60` — the kernel and
   its filesystems, an OCI runtime, a CRI runtime — and names the gate exactly once, in a
   `feature-state` shortcode at `:10`, because at the pin there is nothing left to enable. All four
   are readable without creating anything.

   ```sh
   N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl get node "$N" -o jsonpath='{.status.nodeInfo.kubeletVersion}{"\n"}{.status.nodeInfo.kernelVersion}{"\n"}{.status.nodeInfo.containerRuntimeVersion}{"\n"}'
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" \
     | grep 'kubernetes_feature_enabled.*UserNamespaces'
   ssh zain@10.10.10.180 'sudo runc --version | head -1'
   kubectl create ns uns
   ```

2. The baseline. A pod with no `hostUsers` field at all, which is what every pod in the cluster
   already is.

   ```sh
   kubectl -n uns run plain --image=registry.k8s.io/e2e-test-images/agnhost:2.53 \
     --restart=Never --command -- sleep 3600
   kubectl -n uns wait --for=condition=Ready pod/plain --timeout=120s
   kubectl -n uns exec plain -- cat /proc/self/uid_map
   kubectl -n uns exec plain -- readlink /proc/self/ns/user
   kubectl -n uns get pod plain -o jsonpath='{.spec.hostUsers}{"\n"}'
   ```

3. The post's manifest, twice: once exactly as `:49-55` prints it, and once with the one addition
   that makes it an object. Nothing else is changed — not the image, not the container name.

   ```sh
   kubectl -n uns apply -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   spec:
     hostUsers: false
     containers:
     - name: nginx
       image: docker.io/nginx
   YAML

   kubectl -n uns apply -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata:
     name: nginx
   spec:
     hostUsers: false
     containers:
     - name: nginx
       image: docker.io/nginx
   YAML
   kubectl -n uns wait --for=condition=Ready pod/nginx --timeout=180s
   kubectl -n uns exec nginx -- cat /proc/self/uid_map
   ```

4. The claim no page demonstrates. The concept page says at `:153-156` that the kubelet assigns pods
   UIDs above 0-65535 so that host and pod ranges do not overlap, and at `:133-134` that users on
   each pod are mapped to different non-overlapping users on the host. Two pods is the smallest test
   of *each*.

   ```sh
   for i in 1 2; do
     kubectl -n uns apply -f - <<YAML
   apiVersion: v1
   kind: Pod
   metadata:
     name: u$i
   spec:
     hostUsers: false
     containers:
     - name: shell
       image: registry.k8s.io/e2e-test-images/agnhost:2.53
       command: ["sleep", "3600"]
   YAML
   done
   kubectl -n uns wait --for=condition=Ready pod/u1 pod/u2 --timeout=180s
   for i in 1 2; do
     printf 'u%s uid_map: ' "$i"; kubectl -n uns exec u$i -- cat /proc/self/uid_map
     printf 'u%s ns:      ' "$i"; kubectl -n uns exec u$i -- readlink /proc/self/ns/user
   done
   ```

5. The host side, and a check on the page that tells you to do it. The task page prints
   `user:[4026531837]` at `:82` as the output a reader should see *inside* the container, and then
   says at `:98-99` that the namespace should be different on the host.

   ```sh
   ssh zain@10.10.10.180 'sudo readlink /proc/1/ns/user; sudo cat /proc/1/uid_map'
   kubectl -n uns exec u1 -- readlink /proc/self/ns/user
   kubectl -n uns exec plain -- readlink /proc/self/ns/user
   ```

6. The limitations. The concept page at `:288-294` says that with `hostUsers: false` you may not set
   `hostNetwork`, `hostIPC` or `hostPID`. It does not say where the refusal comes from, so apply all
   three for real and see how far each one gets.

   ```sh
   for hostns in hostNetwork hostIPC hostPID; do
     echo "== $hostns"
     kubectl -n uns apply -f - <<YAML
   apiVersion: v1
   kind: Pod
   metadata:
     name: bad-$hostns
   spec:
     hostUsers: false
     $hostns: true
     containers:
     - name: shell
       image: registry.k8s.io/e2e-test-images/agnhost:2.53
       command: ["sleep", "3600"]
   YAML
   done
   kubectl -n uns get pods -o wide
   N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" \
     | grep 'kubernetes_feature_enabled.*UserNamespacesHostNetwork'
   ```

7. The two metrics. The concept page at `:317-319` names them; nothing in the post has a
   counterpart, because in 1.25 they did not exist. Read them, make one more user-namespaced pod,
   read them again.

   ```sh
   N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" | grep '^started_user_namespaced_pods'
   kubectl -n uns apply -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata:
     name: u3
   spec:
     hostUsers: false
     containers:
     - name: shell
       image: registry.k8s.io/e2e-test-images/agnhost:2.53
       command: ["sleep", "3600"]
   YAML
   kubectl -n uns wait --for=condition=Ready pod/u3 --timeout=180s
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" | grep '^started_user_namespaced_pods'
   ```

8. Offline. The four gate files, and the census that places this rename among the 487.

   ```sh
   cd /path/to/kubernetes/website/content/en
   python3 - <<'PY'
   import glob, os, re, yaml
   G = "docs/reference/command-line-tools-reference/feature-gates"
   R = "docs/reference/command-line-tools-reference"
   def front(p): return yaml.safe_load(open(p, encoding="utf-8").read().split("---")[1])
   for p in sorted(glob.glob(G + "/UserNamespaces*.md")):
       fm = front(p)
       print(os.path.basename(p)[:-3])
       for s in fm["stages"]:
           print(("  %-7s default=%-5s locked=%-5s %s - %s" % (
               s["stage"].strip(), s["defaultValue"], s.get("locked", "-"),
               s["fromVersion"], s.get("toVersion", ""))).rstrip())
       print("  removed: %s  former_titles: %s" % (fm.get("removed"), fm.get("former_titles")))
   sup = former = locked = 0
   for p in sorted(glob.glob(G + "/*.md")):
       if os.path.basename(p) == "index.md":
           continue
       fm = front(p)
       body = open(p, encoding="utf-8").read().split("---")[2]
       sup += bool(re.search(r"supersed|renamed", body, re.I))
       former += bool(fm.get("former_titles"))
       locked += any(s.get("locked") for s in fm["stages"])
   print("of 487: %d name a successor in prose, %d carry former_titles, %d lock a stage"
         % (sup, former, locked))
   ref = "".join(open(R + "/" + f, encoding="utf-8").read() for f in
                 ("kube-apiserver.md", "kube-controller-manager.md", "kube-proxy.md",
                  "kube-scheduler.md", "kubelet.md"))
   for n in ("UserNamespacesSupport", "UserNamespacesHostNetworkSupport"):
       print("%s named in the five help texts: %s" % (n, bool(re.search(r"\b" + n + r"\b", ref))))
   PY
   ```

9. Offline. The post's vocabulary, and its manifest against the one the documentation hands out now.

   ```sh
   cd /path/to/kubernetes/website/content/en
   P=blog/_posts/2022/add-userns-alpha/index.md
   for w in alpha beta stable stateless stateful; do
     printf '%-10s %s\n' "$w" "$(sed -n '8,$p' $P | grep -oi "$w" | wc -l | tr -d ' ')"
   done
   grep -n -i stateless $P
   awk 'NR==48 {print "fence tag at :48 = [" substr($0, 4) "]"}' $P
   echo '--- the post, :49-55 ---'
   sed -n '49,55p' $P
   echo '--- the pin, examples/pods/user-namespaces-stateless.yaml ---'
   cat examples/pods/user-namespaces-stateless.yaml
   ```

10. Offline. The runtime forecast against the record, and which files still know which name.

    ```sh
    cd /path/to/kubernetes/website/content/en
    echo '--- what the post forecast, :62-69 ---'
    sed -n '62,69p' blog/_posts/2022/add-userns-alpha/index.md
    echo '--- what the pin records, user-namespaces.md:52-60 ---'
    sed -n '52,60p' docs/concepts/workloads/pods/user-namespaces.md
    for g in UserNamespacesStatelessPodsSupport UserNamespacesSupport UserNamespacesHostNetworkSupport; do
      echo "--- files naming $g ---"
      grep -rl --include='*.md' "$g" . | sed 's|^\./||' | sort
    done
    ```

**Expect**

Step 1 should clear all four prerequisites without any work. The kubelet is v1.35, the kernel is
Debian Trixie's, which is well past the 6.3 the concept page asks for at `:41-42`, the runtime is
`containerd://2.2.1` and runc reports 1.5.1 — both past the floors at `:53` and `:59`. The
`kubernetes_feature_enabled` lines should show `UserNamespacesSupport` at 1: at v1.35 it is beta and
defaults to `true`, so nothing had to be turned on. Note that the reason the runtime clears the
floor has nothing to do with this feature; the lab installs containerd 2.2.1 for the CRI
`RuntimeConfig` RPC, and Debian's own package is 1.7.24.

Step 2 gives the shape of an unmapped container. `/proc/self/uid_map` should read three
whitespace-padded columns, `0`, `0` and `4294967295`: the whole range, identity-mapped, which is the
same thing as no user namespace at all. That last number is one short of the 4294967296 the post
quotes at `:19-20`, and the gap is worth a moment — the post's number is the size of the ID space
and the map's is the size of the mapping, and the ID that is in the first and not the second is the
all-ones value, which no process may own. `readlink` prints the node's own user-namespace inode. The
last command is worth reading slowly: `pod-v1.md:120-121` describes `hostUsers` as optional with a
default of true, and what you get back is either `true` or nothing. Record which. An optional field
with a documented default and an unset value read back are three different statements about the same
field.

Step 3's first apply fails and its second succeeds, and the only difference between them is
`metadata`. Record the exact wording of the failure and where it came from, because the manifest is
the post's own, printed as a complete example under an instruction that says to set the field —
which it does set, correctly. The second pod's `uid_map` should read `0 <base> 65536`: a base
somewhere above 65536 and a range of exactly 65536, which is the hard-coded per-pod count before
v1.33 and the default `idsPerPod` since. If the image pull is slow, that is the other half of the
manifest: `docker.io/nginx` with no tag resolves to whatever `latest` is on the day you run it.

Step 4 is the centrepiece. Both pods should be mapped, and the two bases should be *different* and
both multiples of 65536 — the task page's own example, 833617920 at `:93`, is 65536 times 12720.
That is the non-overlap claim at `:133-134` in one command — not just that pods are separated from
the host, which is what the post argues, but that they are separated from each other, which the post
does not mention and no page demonstrates. The two namespace inodes should differ from each other as
well. If the two bases are equal, the kubelet is not doing what `:153-156` says it does, and that is
a more interesting result than the expected one.

Step 5 closes the loop and catches a defect. The node's `/proc/1/ns/user` is the initial user
namespace and its `uid_map` is the identity map from step 2. Compare that inode with what the task
page prints at `:82` as the *container's* output. If they match, the page's worked example shows the
host's namespace where the container's should be, two lines above a sentence saying the two must
differ — and the pod from step 4, which is genuinely in its own namespace, prints something the page
never shows. The `plain` pod's inode should equal the node's, which is the control.

Step 6 should refuse all three. What to record is *how*: whether each refusal arrives from `kubectl
apply` as a validation error naming both fields, or whether the object is admitted and the pod then
sits in the listing failing on the node. The concept page at `:288-294` says only that it is
disallowed, and those are very different failures for anyone writing a controller that generates pod
specs. The last command should show `UserNamespacesHostNetworkSupport` at 0 — alpha, and off. Of the
three refusals, that is the one the project has already begun to unpick; the other two have no gate
at all.

Step 7's counters should both exist and `started_user_namespaced_pods_total` should be higher after
`u3` than before, by at least one. The errors counter should be unchanged. These are kubelet metrics
with no apiserver counterpart, so a cluster operator can tell how many pods on a node use the
feature without reading a single pod spec — an observability surface that arrived years after the
post and that the post's three sentences of instruction give no hint of.

Step 8 prints the four ladders and four counts:

```
UserNamespacesHostNetworkSupport
  alpha   default=False locked=-     1.35 -
  removed: None  former_titles: None
UserNamespacesPodSecurityStandards
  alpha   default=False locked=-     1.29 - 1.34
  removed: True  former_titles: None
UserNamespacesStatelessPodsSupport
  alpha   default=False locked=-     1.25 - 1.27
  removed: True  former_titles: None
UserNamespacesSupport
  alpha   default=False locked=-     1.28 - 1.29
  beta    default=False locked=-     1.30 - 1.32
  beta    default=True  locked=-     1.33 - 1.35
  stable  default=True  locked=True  1.36 -
  removed: None  former_titles: None
of 487: 5 name a successor in prose, 1 carry former_titles, 49 lock a stage
UserNamespacesSupport named in the five help texts: False
UserNamespacesHostNetworkSupport named in the five help texts: True
```

Five prose successors out of 487, and one machine-readable one, which belongs to the other post this
year. The glob orders them alphabetically, which is the wrong order for reading them and the right
order for seeing the shape: three of the four names begin with the same word and only one of them is
the feature.

Step 9 prints five counts, one grep hit, one bracket and two manifests:

```
alpha      0
beta       0
stable     0
stateless  1
stateful   0
59:the `UserNamespacesStatelessPodsSupport` gate before you can use
fence tag at :48 = []
--- the post, :49-55 ---
apiVersion: v1
kind: Pod
spec:
  hostUsers: false
  containers:
  - name: nginx
    image: docker.io/nginx
--- the pin, examples/pods/user-namespaces-stateless.yaml ---
apiVersion: v1
kind: Pod
metadata:
  name: userns
spec:
  hostUsers: false
  containers:
  - name: shell
    command: ["sleep", "infinity"]
    image: debian
```

The counts run from line 8 so that the title and the front matter are excluded; the body of a post
announcing an alpha feature does not contain the word. The one hit for *stateless* is the gate name
at `:59`. The empty bracket is the fence's language tag. And the two manifests differ by a
`metadata` block, a container name, a command and an image — the smallest of which, `metadata`, is
the one that decides whether the thing can be applied at all.

Step 10 prints the two forecasts, the two records, and three file lists:

```
--- what the post forecast, :62-69 ---
The runtime must also support user namespaces:

* containerd: support is planned for the 1.7 release.  See containerd
  issue [#7063][containerd-userns-issue] for more details.

* CRI-O: v1.25 has support for user namespaces.

Support for this in `cri-dockerd` is [not planned][CRI-dockerd-issue] yet.
--- what the pin records, user-namespaces.md:52-60 ---
* [crun](https://github.com/containers/crun) version 1.9 or greater (it's recommend version 1.13+).
* [runc](https://github.com/opencontainers/runc) version 1.2 or greater

To use user namespaces with Kubernetes, you also need to use a CRI
{{< glossary_tooltip text="container runtime" term_id="container-runtime" >}}
to use this feature with Kubernetes pods:

* containerd: version 2.0 (and later) supports user namespaces for containers.
* CRI-O: version 1.25 (and later) supports user namespaces for containers.
--- files naming UserNamespacesStatelessPodsSupport ---
blog/_posts/2022/add-userns-alpha/index.md
blog/_posts/2023/userns-stateful-pods/index.md
docs/reference/command-line-tools-reference/feature-gates/UserNamespacesStatelessPodsSupport.md
--- files naming UserNamespacesSupport ---
blog/_posts/2023/userns-stateful-pods/index.md
blog/_posts/2026/rootless-beta.md
docs/concepts/storage/ephemeral-storage.md
docs/concepts/workloads/pods/user-namespaces.md
docs/reference/command-line-tools-reference/feature-gates/LocalStorageCapacityIsolationFSQuotaMonitoring.md
docs/reference/command-line-tools-reference/feature-gates/UserNamespacesPodSecurityStandards.md
docs/reference/command-line-tools-reference/feature-gates/UserNamespacesStatelessPodsSupport.md
docs/reference/command-line-tools-reference/feature-gates/UserNamespacesSupport.md
docs/tasks/configure-pod-container/user-namespaces.md
```

Three files still carry the dead name: this post, the 2023 post that lifted its limit, and its own
gate file. Two of the three are archive — a blog post is never edited — so the only *maintained*
file that knows the old name is the one whose whole subject is a gate nobody can set. The
documentation tree proper has no trace of it. Meanwhile the live gate turns up in nine files, two of
which are about storage rather than security, which is the clearest single sign of how far the
feature travelled from the three sentences that announced it.

**Read on**

1. `docs/concepts/workloads/pods/user-namespaces.md`, the whole 323 lines, against the post's 81.
   Read `:151-212` for the custom-range setup — a `kubelet` user that cannot be called anything
   else, `getsubids` on the path, and five constraints on the range — and `:233-251` for
   `idsPerPod`, which has been settable in `KubeletConfiguration` only since v1.33 and must be a
   multiple of 65536. Then ask which of those the post would have had to say, and which are
   consequences of decisions made after it.

2. The two places `hostUsers` now constrains something else. `security-context.md:818-825` says
   `procMount: Unmasked` requires `spec.hostUsers` to be `false`, and that v1.12 to v1.29 did not
   enforce it; `sysctl-cluster.md:263-268` says `user.*` sysctls are skipped for a pod that shares
   the host user namespace. A field introduced as one pod's opt-in is now a precondition in two
   unrelated subsystems. Work out from the first of those which release turned a documented
   requirement into an enforced one.

3. `UserNamespacesStatelessPodsSupport.md` in full — seventeen lines, of which two are prose, and
   one of those two is the only record of the rename in the maintained tree. Then read the 2023 post
   that step 10 turns up, which is the post that lifted the limit the gate name carries. Reading
   them in that order makes the case for why a `former_titles:` field is worth the trouble: the tree
   has a machine-readable way to say this, used once.

4. `ephemeral-storage.md:280-290` and `LocalStorageCapacityIsolationFSQuotaMonitoring.md:21-22`. A
   storage feature that uses project quotas rather than a filesystem walk requires
   `UserNamespacesSupport` to be on. This is the interaction furthest from anything the post
   discusses, and it is the reason the live gate appears in nine files: a security boundary became a
   precondition for a performance optimisation.

5. *Unanswerable from the pin:* whether the containerd forecast at `:64` was wrong when it was made
   or overtaken later — the pin holds one revision of one tree and no issue history. Also
   unanswerable: whether anybody ever enabled `UserNamespacesStatelessPodsSupport` in the three
   releases it existed. The gate was alpha and off by default, the runtime that most clusters ran
   did not support the feature until a major version after the one the post named, and the pin
   records neither adoption nor complaint.

**Teardown**

```sh
kubectl delete ns uns
```

Nothing else is created. The three `bad-` pods from step 6 are in that namespace whether they were
admitted or not, and so is the unpinned `nginx` from step 3, which is the one image in this exercise
that is not from `registry.k8s.io` — deliberately, because it is the post's.
