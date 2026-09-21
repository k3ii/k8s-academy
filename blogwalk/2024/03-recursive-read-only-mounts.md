<a id="recursive-read-only-mounts"></a>

# The same page that tells you to require read-only mounts says eight hundred lines later that a read-only mount is not recursive, the gate it still tells you to enable has been locked for five releases, and the fix this post announces is still not the default and never will be

**Post** — [Kubernetes 1.30: Read-only volume mounts can be finally literally read-only](https://kubernetes.io/blog/2024/04/23/recursive-read-only-mounts/),
2024-04-23.

3,497 bytes, 108 lines, one author: Akihiro Suda of NTT. Fifty-first of 2024's 54 posts by size,
7,271 bytes under the year's mean of 10,768, and the shortest walk in this directory. It is a plain
markdown file with no directory and no images. Six `##` sections, two YAML blocks, one external
link, and one HTML comment at `:100` pointing at the website pull request that carried the
documentation change alongside it. The post is short because the bug is small to state and the fix
is one field.

**As written**

The opening at `:10-13` makes the claim the whole post rests on: read-only volume mounts have
existed since the beginning of Kubernetes, and "surprisingly, read-only mounts are not completely
read-only under certain conditions on Linux." The certain condition is named at `:36-38`. Given a
Pod that mounts the host's `/mnt` as a `hostPath` volume with `readOnly: true`, writes to `/mnt/*`
are rejected, but if something else is mounted read-write at `/mnt/my-nfs-server` on the host, then
`/mnt/my-nfs-server/*` inside the container is still writeable. The manifest at `:20-34` is the one
a reader would have written and believed.

`:40-63` introduces the fix. Kubernetes v1.30 added a `recursiveReadOnly` mount option, shown in a
second manifest that differs from the first by four lines: three comment lines and
`recursiveReadOnly: Enabled`. The comments at `:60-61` carry two of the three facts a reader needs —
the possible values are `Enabled`, `IfPossible` and `Disabled`, and the field "needs to be specified
in conjunction with `readOnly: true`". The prose at `:69-71` repeats the second point and gives the
reason: the field is not a replacement for `readOnly` but is used in conjunction with it, for
backwards compatibility, and to get a properly recursive read-only mount you must set both.

`:65-67` is the mechanism, in one sentence: the attribute `MOUNT_ATTR_RDONLY` applied with the
`AT_RECURSIVE` flag using `mount_setattr(2)`, added in Linux kernel v5.12. This is the only sentence
in the post that says how, and it is the only external link — to the man page, not to Kubernetes.

`:73-88` is a compatibility list under the heading *Feature availability*. Four components are named
with version floors: Kubernetes v1.30 or later with the `RecursiveReadOnlyMounts` feature gate
enabled, which `:79` states is alpha as of v1.30; containerd v2.0 or later as the CRI runtime; runc
v1.1 or later or crun v1.8.6 or later as the OCI runtime; Linux kernel v5.12 or later. This is a
snapshot of what worked on the day of publication, written as a bulleted list a reader was expected
to check by hand against their own cluster.

`:90-96` is *What's next*, and it makes two forecasts of different kinds. The first is a hope: SIG
Node "hope - and expect - that the feature will be promoted to beta and eventually general
availability (GA) in future releases of Kubernetes, so that users no longer need to enable the
feature gate manually." The second is a commitment: `:96` says the default value of
`recursiveReadOnly` will still remain `Disabled`, for backwards compatibility. The post closes at
`:98-102` by pointing at `/docs/concepts/storage/volumes/#read-only-mounts` for the details, and at
`:104-108` with the SIG Node invitation every feature post of the period carries.

**As it runs now**

Four things have moved, and the fourth is not a behaviour.

**The compatibility list became a field you can query.** The post's *Feature availability* section
is a table of version floors a reader had to check by hand. At the pin, a node publishes what its
runtimes actually support: `docs/reference/kubernetes-api/core/node-v1.md:452-463` defines
`NodeRuntimeHandlerFeatures` with a boolean `recursiveReadOnlyMounts`, "set to true if the runtime
handler supports RecursiveReadOnlyMounts", hanging off the `features` field of each entry in
`.status.runtimeHandlers` (`:431-447`). The same structure carries a `userNamespaces` boolean at
`:466-467`. Meanwhile the prose the post sends its reader to has gone the other way: the five
`Enabled` requirements at `docs/concepts/storage/volumes.md:1226-1234` name a kernel version and say
only that the CRI-level and OCI-level runtimes must "support recursive read-only mounts", naming no
containerd, runc or crun version at all. The version list did not get updated; it got replaced by a
query. Step 2 runs it.

**The outcome became a status field.** Nothing in the post tells a reader how to find out whether
the mount they asked for is the mount they got. At the pin,
`docs/concepts/storage/volumes.md:1242-1244` says that when kubelet and kube-apiserver recognise the
property, `.status.containerStatuses[*].volumeMounts[*].recursiveReadOnly` is set to either
`Enabled` or `Disabled`. That matters most for the value the post names but never explains:
`IfPossible` at `:1236-1237` attempts `Enabled` and falls back to `Disabled` if the kernel or the
runtime class does not support it, silently. The status field is the only thing that tells you which
of the two happened. Steps 5 and 7 read it.

**The mechanism sentence was absorbed word for word.** The post's `:65-67` now appears at
`docs/reference/node/kernel-version-requirements.md:79-81`, on a page that did not exist when the
post was published, with the same words in the same order — `MOUNT_ATTR_RDONLY`, `AT_RECURSIVE`,
`mount_setattr`(2), Linux kernel v5.12 — differing only in that the man-page link is gone and a code
pointer sits in an HTML comment above it at `:76`. The same page is worth reading for a second
reason: `:82-83` gives a 6.5+ kernel floor for Pod user namespaces, while
`docs/concepts/workloads/pods/user-namespaces.md:41-44` gives 6.3. Two pages of the same pinned
tree, two floors for the same feature; the exercise beside this one walks that feature and did not
catch it. Step 8 reads both.

**The page disagrees with itself about its own security advice.** The `hostPath` warning at
`docs/concepts/storage/volumes.md:345-350` tells the reader that if they restrict access to
directories on the node using admission-time validation, "that restriction is only effective when
you additionally require that any mounts of that `hostPath` volume are **read only**", because a
read-write host mount lets containers subvert it. Eight hundred and fifty-six lines further down,
the same file at `:1206-1210` says that on Linux read-only mounts are not recursively read-only by
default, and gives as its example a Pod mounting the host's `/mnt` as a `hostPath` volume with a
writeable submount underneath. Cite both halves: the page's advice is to require `readOnly`, and the
page's own later text says `readOnly` does not cover what is mounted beneath. Neither passage
mentions the other, and the earlier one has no pointer to `recursiveReadOnly`. Step 4 settles this
one, because it writes through a mount that satisfies `:345-350` exactly.

A fifth thing, smaller, sits inside the third: `docs/concepts/storage/volumes.md:1216-1219` still
instructs the reader to enable the `RecursiveReadOnlyMounts` feature gate for kubelet and
kube-apiserver. The gate is `locked: true` from v1.33, it is named in none of the five generated
command-line help pages under `docs/reference/command-line-tools-reference/`, and the
`feature-state` shortcode two lines above it at `:1214` renders *stable*. Step 10 settles that half
by trying to set it.

**What this exercise does not cover, and where it lives**

Mount propagation is not this exercise's subject even though `mountPropagation: None` is one of the
five requirements. The three propagation modes, the `shared:N` and `master:N` tags in
`/proc/self/mountinfo`, and what happens when a propagated mount crosses the boundary belong to [the
mount propagation lab](../../labs/00/15-mount-propagation.md). Unmounting a filesystem out from
under a running Pod, and why CSI drivers ask for `Bidirectional`, belong to [the lab that pulls the
mount away](../../labs/08/08-umount-under-a-running-pod.md). Step 7 names `mountPropagation` once,
only to trigger an API rejection, and reads nothing about propagation itself.

The user-namespace half of `NodeRuntimeHandlerFeatures` is read in step 2 because it sits in the
same object, but the feature it describes belongs to [the user namespaces beta
exercise](02-userns-beta.md) beside this one, which owns the runtime support argument in full. The
`supplementalGroupsPolicy` entry in `NodeFeatures` at `node-v1.md:414-426` is a different structure
on the same status and is not touched here; a later row in this directory walks it. Nothing here
needs NFS or a second machine: the post's example is an NFS submount, and a tmpfs submount
reproduces the bug identically and fits the single-node topology.

**The diff, and why**

***Retired by being agreed with.*** The whole of *Feature availability* and the first half of
*What's next* got what they asked for, faster than the post dared say. The post's `:92-94` hopes for
beta and eventually GA "so that users no longer need to enable the feature gate manually"; the gate
went beta-and-on in v1.31 and stable-and-locked in v1.33, and by the pin a user cannot enable it
manually, because a locked gate refuses to be set. The mechanism paragraph at the post's `:65-67`
did not just survive, it became the documentation: `kernel-version-requirements.md:79-81` is the
same sentence. The post's version list at `:81-88` was retired differently — not contradicted, but
made unnecessary by `.status.runtimeHandlers[*].features.recursiveReadOnlyMounts`. A post is retired
by agreement when the project does the thing and then makes the post's own text redundant, and this
one was retired three ways at once.

***Still right.*** The post's `:36-38` describes the bug in three sentences and every word of it
still holds at the pin, on a cluster five minor versions past the one the post was written for, with
the feature stable and locked. Step 4 reproduces it exactly: a mount that sets `readOnly: true` and
nothing else still lets a container write into a submount. The post did not describe a defect that
was then fixed; it described a default that was then kept.

***Overtaken by stasis.*** The post's `:96` commits that the default value of `recursiveReadOnly`
will remain `Disabled`, and `volumes.md:1223` confirms it: `Disabled` (default): no effect. So the
fix went alpha, beta and stable in three releases, has been locked for five more, and the behaviour
a reader gets by writing `readOnly: true` in 2026 is exactly the behaviour that has surprised people
since Kubernetes had volumes at all. The feature is finished; the bug is still the default.
Everything moved except the thing the post was about. That is the shape worth carrying out of this
exercise: a gate reaching stable tells you the API will not change, not that the behaviour did.

**The ladder**

`RecursiveReadOnlyMounts`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.30 – v1.30 |
| beta | `true` | — | v1.31 – v1.32 |
| stable | `true` | `true` | v1.33 – |

Three stages, no repeats, no gaps: each `toVersion` closes exactly where the next `fromVersion`
opens, and the stable stage is unbounded, so it runs from v1.33 to the pin's v1.37 — five releases
locked. The alpha lasted a single release, which is unremarkable: 151 of the pin's 487 gate files do
the same. What is worth noticing is the beta default. `true` at v1.31 means the field became usable
on an upgraded cluster without anyone opting in, one release after it appeared.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180` running Kubernetes v1.35.
Everything here needs node root: a tmpfs submount on the host, a `hostPath` volume over it, and one
edit to the kubelet's configuration file. Provision with [the standard
steps](../../strands/lab-topologies.md#provision) and [the node
baseline](../../strands/lab-topologies.md#node-baseline-steps) if the node is not already up. All
work happens in a namespace called `bw-rro`, and all host state under `/mnt/bw-rro`.

**Do**

1. Ground the node and build the bug. The post's example needs a directory with a separate
   filesystem mounted underneath it; it used NFS, a tmpfs does the same job on one machine. Record
   the kernel and runtime versions first, because they are three of the four rows in the post's
   compatibility list.

   ```sh
   ssh zain@10.10.10.180
   uname -r
   kubectl version -o json | jq -r '.serverVersion.gitVersion'
   ctr --version
   runc --version | head -1
   sudo mkdir -p /mnt/bw-rro/sub
   sudo mount -t tmpfs -o size=16m tmpfs /mnt/bw-rro/sub
   findmnt -no TARGET,FSTYPE,OPTIONS /mnt/bw-rro/sub
   sudo sh -c 'echo host > /mnt/bw-rro/base-file; echo host > /mnt/bw-rro/sub/sub-file'
   sudo chmod -R 0777 /mnt/bw-rro
   kubectl taint node --all node-role.kubernetes.io/control-plane- 2>/dev/null || true
   kubectl create namespace bw-rro
   ```

2. Read the compatibility list as a field. The post asked its reader to check four version floors by
   hand; the node publishes two of the answers. Read every runtime handler the node knows about, not
   just the default one — the field hangs off each handler separately, which is the whole reason it
   exists.

   ```sh
   kubectl get node -o json | jq -r '.items[].status.runtimeHandlers'
   kubectl get node -o jsonpath='{range .items[*].status.runtimeHandlers[*]}{.name}{"\t"}{.features.recursiveReadOnlyMounts}{"\t"}{.features.userNamespaces}{"\n"}{end}'
   kubectl get runtimeclass 2>/dev/null || true
   ```

3. Apply the pin's own example, redirected at the directory you just built. This is
   `examples/storage/rro.yaml` from the pinned tree with `/mnt` changed to `/mnt/bw-rro`, a
   namespace added, and nothing else touched: one volume, three mounts of it, three different
   settings.

   ```sh
   cat <<'EOF' | kubectl apply -f -
   apiVersion: v1
   kind: Pod
   metadata:
     name: rro
     namespace: bw-rro
   spec:
     volumes:
       - name: mnt
         hostPath:
           path: /mnt/bw-rro
     containers:
       - name: busybox
         image: busybox:1.36
         args: ["sleep", "infinity"]
         volumeMounts:
           - name: mnt
             mountPath: /mnt-rro
             readOnly: true
             mountPropagation: None
             recursiveReadOnly: Enabled
           - name: mnt
             mountPath: /mnt-ro
             readOnly: true
           - name: mnt
             mountPath: /mnt-rw
   EOF
   kubectl -n bw-rro wait --for=condition=Ready pod/rro --timeout=90s
   ```

4. Six writes. Two per mount: one at the root of the mount, one in the submount beneath it. This is
   the whole post in one command, and it is also the command that settles the page's argument with
   itself, because `/mnt-ro` is a mount that satisfies `volumes.md:345-350` exactly — a `hostPath`
   required to be read only — and one of its two writes lands.

   ```sh
   kubectl -n bw-rro exec rro -- sh -c '
   for m in /mnt-rro /mnt-ro /mnt-rw; do
     for p in "$m/pod-file" "$m/sub/pod-file"; do
       if echo pod > "$p" 2>/dev/null; then echo "WROTE  $p"; else echo "denied $p"; fi
     done
   done'
   sudo ls -l /mnt/bw-rro /mnt/bw-rro/sub
   ```

5. Read the outcome the post never mentions. The status field says what the kubelet actually did
   with each of the three mounts, mount by mount, and it is reported alongside `readOnly` so the
   pair can be compared.

   ```sh
   kubectl -n bw-rro get pod rro -o jsonpath='{range .status.containerStatuses[*].volumeMounts[*]}{.mountPath}{"\t"}{.readOnly}{"\t"}{.recursiveReadOnly}{"\n"}{end}'
   kubectl -n bw-rro get pod rro -o json | jq -r '.status.containerStatuses[0].volumeMounts'
   ```

6. Look at the mount table from inside. Three mounts of one volume produce six entries in the
   container's mount table, because each submount is mounted again under each mount point. The `ro`
   and `rw` flags on those six lines are the post's `:65-67` seen from the other side.

   ```sh
   kubectl -n bw-rro exec rro -- awk '$2 ~ /^\/mnt-/ {print $2, $3, $4}' /proc/self/mounts
   kubectl -n bw-rro exec rro -- cat /proc/self/mounts | grep -c '^tmpfs /mnt-'
   ```

7. The two rejections and the third value. `pod-v1.md:3194` states two rules the post's two comment
   lines only half carry: if `readOnly` is false the field has no meaning and must be unspecified,
   and `Enabled` or `IfPossible` require `mountPropagation` to be `None` or unset. Try both, then
   apply `IfPossible` on a node that supports the feature and read what the status says.

   ```sh
   cat <<'EOF' | kubectl apply -f - ; echo "exit=$?"
   apiVersion: v1
   kind: Pod
   metadata: {name: bad-noro, namespace: bw-rro}
   spec:
     volumes: [{name: mnt, hostPath: {path: /mnt/bw-rro}}]
     containers:
       - name: busybox
         image: busybox:1.36
         args: ["sleep", "infinity"]
         volumeMounts:
           - {name: mnt, mountPath: /mnt-x, recursiveReadOnly: Enabled}
   EOF
   cat <<'EOF' | kubectl apply -f - ; echo "exit=$?"
   apiVersion: v1
   kind: Pod
   metadata: {name: bad-prop, namespace: bw-rro}
   spec:
     volumes: [{name: mnt, hostPath: {path: /mnt/bw-rro}}]
     containers:
       - name: busybox
         image: busybox:1.36
         args: ["sleep", "infinity"]
         volumeMounts:
           - {name: mnt, mountPath: /mnt-x, readOnly: true, mountPropagation: HostToContainer, recursiveReadOnly: Enabled}
   EOF
   cat <<'EOF' | kubectl apply -f -
   apiVersion: v1
   kind: Pod
   metadata: {name: maybe, namespace: bw-rro}
   spec:
     volumes: [{name: mnt, hostPath: {path: /mnt/bw-rro}}]
     containers:
       - name: busybox
         image: busybox:1.36
         args: ["sleep", "infinity"]
         volumeMounts:
           - {name: mnt, mountPath: /mnt-x, readOnly: true, recursiveReadOnly: IfPossible}
   EOF
   kubectl -n bw-rro wait --for=condition=Ready pod/maybe --timeout=90s
   kubectl -n bw-rro get pod maybe -o jsonpath='{.status.containerStatuses[0].volumeMounts[0].recursiveReadOnly}{"\n"}'
   kubectl -n bw-rro exec maybe -- sh -c 'echo pod > /mnt-x/sub/pod-file 2>/dev/null && echo WROTE || echo denied'
   ```

8. Read the pin. Both halves of the page's disagreement, the example you just ran, the absorbed
   sentence, and the two kernel floors that do not match. Run this on the machine holding the
   checkout, not on the node.

   ```sh
   cd /path/to/kubernetes/website/content/en
   sed -n '334,350p' docs/concepts/storage/volumes.md
   sed -n '1198,1244p' docs/concepts/storage/volumes.md
   cat examples/storage/rro.yaml
   sed -n '74,86p' docs/reference/node/kernel-version-requirements.md
   sed -n '65,67p' blog/_posts/2024/recursive-read-only-mounts.md
   sed -n '41,44p' docs/concepts/workloads/pods/user-namespaces.md
   sed -n '452,468p' docs/reference/kubernetes-api/core/node-v1.md
   awk 'NR==3194' docs/reference/kubernetes-api/core/pod-v1.md | fold -s -w 96
   cat docs/reference/command-line-tools-reference/feature-gates/RecursiveReadOnlyMounts.md
   ```

9. Count what is there and what is not. Three measurements: how many of the generated command-line
   help pages name the gate the concept page tells you to set; how many lines in the whole
   documentation tree mention the field at all; and how many runtime versions survived from the
   post's compatibility list into the prose that replaced it.

   ```sh
   ls docs/reference/command-line-tools-reference/*.md | grep -v _index | wc -l
   grep -l 'RecursiveReadOnlyMounts' $(ls docs/reference/command-line-tools-reference/*.md | grep -v _index) | wc -l
   grep -rn --include='*.md' 'recursiveReadOnly' docs | wc -l
   grep -rln --include='*.md' 'recursiveReadOnly' docs
   sed -n '81,88p' blog/_posts/2024/recursive-read-only-mounts.md | grep -c 'v[0-9]'
   sed -n '1226,1234p' docs/concepts/storage/volumes.md | grep -c 'v[0-9]'
   ```

10. Take the concept page's instruction literally. `volumes.md:1216-1219` says to enable the
    `RecursiveReadOnlyMounts` feature gate for kubelet and kube-apiserver. Do exactly that, in the
    direction that would change something — set it to `false` — and watch the kubelet answer. Check
    first whether `featureGates:` already exists in the file; if it does, add the entry under the
    existing key by hand instead of appending a second one, because a duplicate key fails for the
    wrong reason and teaches nothing.

    ```sh
    sudo cp /var/lib/kubelet/config.yaml /tmp/bw-kubelet-config.yaml
    grep -n '^featureGates:' /var/lib/kubelet/config.yaml || true
    printf 'featureGates:\n  RecursiveReadOnlyMounts: false\n' | sudo tee -a /var/lib/kubelet/config.yaml
    sudo systemctl restart kubelet
    systemctl is-active kubelet || true
    sudo journalctl -u kubelet -n 30 --no-pager | tail -20
    sudo cp /tmp/bw-kubelet-config.yaml /var/lib/kubelet/config.yaml
    sudo systemctl restart kubelet
    kubectl get node
    ```

**Expect**

Step 1. `uname -r` reports a 6.12 kernel, well past the v5.12 floor the post names at `:67`.
`kubectl version` reports v1.35, five minor releases past the v1.30 the post was written for and two
past the release that locked the gate. `ctr --version` reports 2.2.1 and `runc --version` reports
1.5.1, so all four rows of the post's *Feature availability* list at `:75-88` are satisfied, and
satisfied by a wide margin: the post asked for containerd v2.0 and runc v1.1. The tmpfs mounts and
`findmnt` shows it as a separate filesystem at `/mnt/bw-rro/sub` — that separation is the entire
precondition for the bug, and if it is missing nothing in this exercise will reproduce.

Step 2. The node reports at least one runtime handler. The default handler has an empty name and a
`features` object carrying `recursiveReadOnlyMounts: true` and `userNamespaces: true`. Those two
booleans are the replacement for the version list you just checked by hand in step 1: the same
question, asked of the machine instead of of a blog post. Note what the field does not tell you — no
version, no runtime name, no kernel. It answers only the question the scheduler and the kubelet
actually need answered. If `kubectl get runtimeclass` returns nothing, that is expected on this lab;
the handler list is populated by the kubelet from the CRI regardless.

Step 3. The Pod goes Ready. Three `volumeMounts` entries naming one volume is legal and ordinary —
the same host directory appears three times in the container's filesystem, under three paths, with
three different read-only settings. The Pod is admitted even though one of its mounts asks for
`recursiveReadOnly: Enabled`, which means every one of the five requirements at
`volumes.md:1226-1232` is met on this node. Had any been missing, `:1234` says it would have failed;
`pod-v1.md:3194` says where — the Pod would not have started and an error would have said why.

Step 4. Six lines, and the fourth is the post. `/mnt-rro/pod-file` denied, `/mnt-rro/sub/pod-file`
denied, `/mnt-ro/pod-file` denied, **`/mnt-ro/sub/pod-file` written**, `/mnt-rw/pod-file` written,
`/mnt-rw/sub/pod-file` written. The `ls -l` on the host confirms it: `pod-file` exists in
`/mnt/bw-rro/sub` and its contents came from inside a container, through a mount the Pod declared
read-only. Read `volumes.md:345-350` again with that file on screen. The page's advice is that
requiring read-only mounts makes an admission-time directory restriction effective; the file you
just wrote went through a mount that satisfies the requirement. The page's own text at `:1206-1210`
explains why, eight hundred and fifty-six lines later, and points at no remedy. The remedy is the
line `/mnt-rro` proves: the same write is denied when `recursiveReadOnly: Enabled` is set beside
`readOnly`.

Step 5. Three rows. `/mnt-rro` reports `readOnly: true` and `recursiveReadOnly: Enabled`; `/mnt-ro`
reports `readOnly: true` and an empty `recursiveReadOnly`; `/mnt-rw` reports neither. The empty
value on the middle row is the interesting one — `volumes.md:1242-1244` says the field is set to
`Enabled` or `Disabled` when the property is recognised, and `pod-v1.md:3194` says an unspecified
request is treated as equivalent to `Disabled`. A reader who wants to audit a cluster for this bug
is reading `.status`, not `.spec`, and needs to treat unset and `Disabled` alike.

Step 6. Six lines beginning `/mnt-`, in pairs. Each mount point appears once for the host directory
and once for the tmpfs under it, so `/mnt-rro`, `/mnt-rro/sub`, `/mnt-ro`, `/mnt-ro/sub`, `/mnt-rw`
and `/mnt-rw/sub` are all separate entries. Read the option field: `/mnt-rro` and `/mnt-rro/sub`
both carry `ro`, `/mnt-ro` carries `ro` while `/mnt-ro/sub` carries `rw`, and both `/mnt-rw` entries
carry `rw`. That one `rw` on `/mnt-ro/sub` is what the mechanism at the post's `:65-67` exists to
prevent, stated by the kernel rather than inferred from a failed write. The `grep -c` counts the
tmpfs lines; three is the answer, one per mount point.

Step 7. Two rejections and one success. `bad-noro` is refused by the API server, which says the
field may only be specified when `readOnly` is true — the rule `pod-v1.md:3194` states and the
post's comment at `:61` gestures at without saying who enforces it. `bad-prop` is refused for
`mountPropagation`, which must be `None` or unset. Both are rejected at admission, before any node
is involved, so the error arrives immediately and no Pod object is created. `maybe` is admitted and
goes Ready, and its status reports `recursiveReadOnly: Enabled` — on this node `IfPossible` and
`Enabled` do the same thing, and the write into `/mnt-x/sub` is denied. The lesson of `IfPossible`
is not visible here and cannot be made visible on this lab: on a node whose runtime did not support
the feature, the Pod would still go Ready, the status would read `Disabled`, and the write would
land. `IfPossible` is the value that fails open, and `.status` is the only place it says so.

Step 8. `volumes.md:334-350` gives the `hostPath` warning; `:1198-1244` gives the read-only section,
and the two are separated by eight hundred and fifty-six lines of unrelated material. `rro.yaml` is
the file you edited in step 3, and it mounts a `hostPath` — the same volume type the warning at
`volumes.md:341-343` tells you to avoid if you can, used in the example for a feature whose main
purpose is to make `hostPath` mounts safer. Then compare `kernel-version-requirements.md:79-81`
against `blog/_posts/2024/recursive-read-only-mounts.md:65-67`: the same sentence, the same order,
the link markup stripped. Finally the two kernel floors — `kernel-version-requirements.md:82-83`
says Pod user namespaces need 6.5 or later, `user-namespaces.md:41-44` says 6.3. Both are in this
checkout, neither mentions the other, and the node in step 1 is past both, which is exactly why the
disagreement survives unnoticed.

Step 9. Five generated help pages, and zero of them name `RecursiveReadOnlyMounts`. Four lines in
the whole `docs` tree mention `recursiveReadOnly` at all, across three files — the concept page
twice, the Node API reference once for the node-side boolean, the Pod API reference once for the
field itself. Four version tokens in the post's compatibility list at `:81-88`; one in the prose
that replaced it, and it is the kernel. The runtime versions were not updated and were not deleted;
they were replaced by the sentence "the CRI-level container runtime supports recursive read-only
mounts", which is true on any date and useless without step 2.

Step 10. The kubelet does not start. `systemctl is-active` reports `activating` or `failed`, and the
journal carries a line saying the feature gate cannot be set because it is locked to its default.
The instruction at `volumes.md:1216-1219` is not merely stale — it is unfollowable, and has been
since v1.33. Restoring the backup and restarting brings the node back; `kubectl get node` reports
Ready within a minute or so. Do not skip the restore: a kubelet that will not start takes the whole
single-node cluster with it, and the teardown below assumes a working one.

**Read on**

1. `docs/concepts/storage/volumes.md:1198-1244` — the section the post points at, read as a whole.
   The ordering repays attention: the bug is stated before the fix is named, and the fix is gated
   behind an instruction that no longer works.

2. `docs/concepts/storage/volumes.md:334-378` — the `hostPath` warning in full. The five bullets
   after the horizontal rule at `:352` are a separate argument from the read-only one and worth
   reading against any manifest that mounts a host path.

3. `docs/reference/kubernetes-api/core/pod-v1.md:3193-3194` — the complete semantics of the field in
   one table cell: the `readOnly` precondition, the `mountPropagation` precondition, the difference
   between `Enabled` and `IfPossible`, and the treatment of an unset value.

4. `docs/reference/node/kernel-version-requirements.md` — the whole page, ninety-odd lines, listing
   the kernel floors Kubernetes features carry. It is the tidiest example in the pinned tree of a
   blog sentence becoming reference documentation.

5. Unanswerable from the pin: why the default stayed `Disabled`. The post's `:96` says "for
   backwards compatibility" and `volumes.md:1223` repeats the default without a reason. What breaks
   if a recursive read-only mount is applied to a workload that expected the old behaviour is not
   written down anywhere in this checkout.

**Teardown**

```sh
kubectl delete namespace bw-rro --wait=true
sudo umount /mnt/bw-rro/sub
sudo rm -rf /mnt/bw-rro
sudo cmp /tmp/bw-kubelet-config.yaml /var/lib/kubelet/config.yaml && sudo rm -f /tmp/bw-kubelet-config.yaml
systemctl is-active kubelet
kubectl get node
```

If the node was untainted in step 1 and the taint is wanted back:

```sh
kubectl taint node --all node-role.kubernetes.io/control-plane=:NoSchedule
```
