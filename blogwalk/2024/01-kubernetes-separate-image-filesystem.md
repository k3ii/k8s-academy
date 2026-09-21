<a id="kubernetes-separate-image-filesystem"></a>

# The post files under future work a split whose alpha had already shipped in the release it was written against, the image filesystem it says is ignored was being measured all along, and the signals for the thing it promised exist on a node whose runtime cannot produce them

**Post** — [Image Filesystem: Configuring Kubernetes to store containers on a separate
filesystem](https://kubernetes.io/blog/2024/01/23/kubernetes-separate-image-filesystem/),
2024-01-23.

213 lines, 10,732 bytes, Kevin Hannon (Red Hat), with four reviewers thanked by name at `:210-213`.
It is the first of 2024's thirteen walks and the earliest post in the year to earn one, 22nd of 54
by size and 35 bytes under the year's mean of 10,767. The frontmatter at `:1-8` carries no
`canonicalUrl`, so the address above is the one the site serves.

**As written**

The stated purpose is narrow and operational: bring attention to the ways you can configure a
container runtime to store its content separately from the default partition (`:16-17`), because
running out of disk is a common way to lose a node (`:10`). Before the recipes, the post spends a
section on a question it says needs more explaining — where Kubernetes writes to disk (`:19`). The
answer is three categories, ephemeral storage, logs, and the container runtime (`:27-29`), and one
sentence that is the whole reason the post exists: this is different from most POSIX systems,
because the root or node filesystem is not `/` but the disk that `/var/lib/kubelet` is on (`:31`).
The runtime then gets its own two-part account — a read-only layer of image content and a writeable
layer for whatever a container writes (`:49-58`) — and the post names the pair: the container
runtime filesystem contains both, and that is what Kubernetes documentation calls `imagefs`
(`:60-61`).

The recipes are short. CRI-O reads `/etc/containers/storage.conf`, where `graphroot` is the
persistent store and `runroot` the temporary one, with a `semanage`/`restorecon` pair for
relabelling if SELinux is enforcing (`:67-95`). containerd reads `/etc/containerd/config.toml`,
where `root` defaults to `/var/lib/containerd` and `state` to `/run/containerd` (`:99-110`). Neither
recipe is more than a handful of lines, which is the post's point: the split is cheap to make and
the consequences are all downstream of it.

Those consequences are the second half. Kubernetes detects the split automatically and is then
responsible for watching both filesystems (`:114-115`); the two are called nodefs and imagefs
(`:116`); either one crossing a threshold puts the whole node under disk pressure (`:117`); and the
kubelet reclaims by deleting unused containers and images before it resorts to evicting pods
(`:118`). Which reclaim happens where depends on the split — images are collected on imagefs and
dead pods removed from nodefs when both exist, and everything happens on the one filesystem when it
does not (`:119-122`). Then the signals: four of them, `nodefs.available`, `nodefs.inodesFree`,
`imagefs.available` and `imagefs.inodesFree` (`:127`), followed by the sentence this exercise
measures — if there is not a dedicated disk for the container runtime then imagefs is ignored
(`:128`). Four defaults are listed (`:130-135`), `EvictionHard` and `EvictionSoft` are defined
(`:139-143`), and the reader is warned that specifying `EvictionHard` replaces the defaults, so it
is important to set all signals (`:145-146`). A sample `KubeletConfiguration` closes the section
(`:150-175`).

The post ends honestly. Under *Problems* (`:177-191`) it names its own trap — mounting a new
filesystem at `/var/lib/containers/storage` or `/var/lib/containerd` is a common misconfiguration
precisely because Kubernetes will detect it, so the imagefs thresholds you never set are suddenly
live — and then a second one: ephemeral storage reporting does not change when you define an image
filesystem, because the kubelet always reports ephemeral capacity from nodefs even when the writes
are landing on imagefs. Under *Future work* (`:193-197`) it says SIG Node are working on a KEP that
will let Kubernetes detect whether the writeable layer is separated from the read-only layer, which
would put all ephemeral storage on one disk and images on another.

**As it runs now**

The future work shipped, and it had already started shipping when the post was published. The gate
file `KubeletSeparateDiskGC.md` records an alpha at v1.29 closed at v1.30 and a beta from v1.31 that
is still open at the pin, and its body describes exactly the post's closing paragraph: the split
image filesystem feature enables the kubelet to garbage-collect images and containers deployed on
separate filesystems. The kubelet's own flag reference carries it as `KubeletSeparateDiskGC=true|
false (BETA - default=true)`, once, in the `--feature-gates` help. The post is dated 2024-01-23,
under v1.29 — the release in which that alpha appeared. The eviction page now recognises three
filesystem identifiers rather than two, adding `containerfs` for the writeable layers
(`node-pressure-eviction.md:130-133`) and the signals `containerfs.available` and
`containerfs.inodesFree` (`:78-79`), and it names the three layouts the post could only gesture at
(`:149-167`).

It shipped somewhere this lab cannot reach. The same page states that only CRI-O at v1.29 or higher
offers `containerfs` filesystem support (`:145-146`), and the house runtime is containerd. So the
gate is beta and on, the signals are documented, the thresholds are described as automatically
derived — and on the guest you are about to split, nothing will produce a `containerfs` number. The
split the post actually teaches, runtime storage on its own disk, is the middle layout of the three
(`:156-160`) and works exactly as written.

The post's four defaults are five on the pinned page, which lists `imagefs.inodesFree<5%` as well
and adds a Windows memory figure (`:232-241`). The replace-the-defaults trap the post warns about is
still the default behaviour, and it now has a switch: `mergeDefaultEvictionSettings`, which makes
unspecified signals inherit their defaults instead of being set to zero
(`node-pressure-eviction.md:245-250`, `kubelet-config-file.md:69-75`). Whether the eviction page's
list of defaults or the kubelet config reference's is the one the binary uses is a disagreement
another exercise in this walk already settles, and it is settled with the same `configz` read used
below.

And the pinned tree disagrees with itself about whether `containerfs` exists on a containerd node.
`node-pressure-eviction.md:145-146` says only CRI-O offers the support at this release. `:119-120`
introduces the three identifiers as ones the kubelet recognises, with no runtime qualifier.
`:252-261` says the `containerfs.available` and `containerfs.inodesFree` defaults will be set as
follows — the same as `nodefs` or the same as `imagefs`, depending on which one `containerfs`
coincides with — and that custom overrides are unsupported and will be warned about and ignored.
`:410-414` repeats that the metric is set automatically to reflect `nodefs` or `imagefs`. Read
together, the page says the feature is unavailable on this node and describes the thresholds it has
there anyway. Neither half is a claim about what the kubelet reports, and step 6 is the command that
settles it.

**What this exercise does not cover, and where it lives**

The eviction cascade on an *unsplit* node — the four things the kubelet tries before it evicts
anyone, on a guest where nodefs and imagefs are one device — is [the phase-six disk-pressure
drill](../../labs/06/28-6c4-disk-pressure-cascade.md), which observes the collapsed case and
deliberately declines to add a second device to chase the distinction. This exercise is the other
side of that decision: it adds the device. Reading a configured threshold back out of the running
kubelet belongs to [the exercise that sets one and crosses
it](../../labs/06/12-an-eviction-you-configured.md). And the disagreement between the eviction
page's list of hard defaults and the kubelet configuration reference's shorter one is owned by [the
2019 post that became a documentation page](../2019/05-pid-limiting.md), which settles it from
`configz`; this exercise reads `configz` too, but for a different question.

**The diff, and why**

**Three of the seven cases.** This post was ***wrong when it was published***, part of it has
been ***retired by being agreed with***, and the rest of it is ***still right***. Take them in that
order. The *Future work* section says SIG Node are working on a way to detect a writeable layer
separated from the read-only layer. At the moment those words were published the gate for that work
was already in the tree, alpha in v1.29, the release the post was written against. Nothing about the
claim was dishonest — a KEP under an alpha gate is genuinely still being worked on — but a reader
who took *future* at face value would not have gone looking for a gate they could switch on that
afternoon.

Then it was agreed with, thoroughly. The split landed at beta and on by default in v1.31, the
eviction page grew a third filesystem identifier, and the three layouts the post had to describe in
prose are now an enumerated list with names. A post whose closing section asks for something and
gets it is ordinarily the happiest of the seven cases. This one comes with a qualifier the post
could not have anticipated: two years and six releases after the beta, exactly one container runtime
implements it, and it is not the one this lab runs. The feature is on, and on containerd it is
furniture.

What remains is still right, and more of it than the reader might expect. The paths are unchanged,
the two configuration knobs per runtime are unchanged, the reclaim order is unchanged, and the trap
the post names under *Problems* — that mounting a filesystem where the runtime stores things
silently arms a threshold you never configured — is the same trap, on the same default, with the
same consequence. The one sentence worth arguing with is `:128`, that imagefs is ignored without a
dedicated disk. The pinned page's first layout says the opposite in a different vocabulary: with
everything on one filesystem, `nodefs`, `imagefs` and `containerfs` all refer to it (`:151-153`),
which is not the same as ignoring the imagefs signals. Steps 2 and 5 ask the kubelet which of those
two descriptions it is living in, before and after the split.

**The ladder**

`KubeletSeparateDiskGC`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.29 – v1.30 |
| beta | `true` | — | v1.31 – |

The gate has never had a `lockToDefault`, and the alpha's `toVersion` is the clean kind — it closes
where the beta opens. Seven releases in beta at the pin, v1.31 through v1.37.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo), fresh. One node, and it has to be a node you are
willing to repartition: the exercise stops the kubelet and the container runtime, moves containerd's
entire store onto a second filesystem, and then fills that filesystem until the node reports
pressure. Bring the guest up with [the five provision
steps](../../strands/lab-topologies.md#provision), install Kubernetes with [the node baseline
procedure](../../strands/lab-topologies.md#node-baseline-steps), then `ssh zain@10.10.10.180`. The
second filesystem is a 3GiB file on the root disk, preallocated, so the ceiling on everything you
fill in steps 7 and 8 is that file's size and the root filesystem never moves. Steps 1, 2 and 4 to 9
need the cluster; steps 3 and 10 need only the pinned tree.

**Do**

1. Take the baseline before anything moves. Back up the kubelet configuration file, untaint the
   single node so Pods can land on it, and write down three numbers you will need later: the server
   version, the eviction thresholds the kubelet is actually running, and the image
   garbage-collection threshold that sits alongside them.

   ```sh
   NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl taint node $NODE node-role.kubernetes.io/control-plane- || true
   sudo cp /var/lib/kubelet/config.yaml /tmp/bw-kubelet-config.yaml
   kubectl version -o json | python3 -c 'import sys,json; print("server:", json.load(sys.stdin)["serverVersion"]["gitVersion"])'
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" \
     | python3 -c 'import sys,json; c=json.load(sys.stdin)["kubeletconfig"]; print("evictionHard:", c.get("evictionHard")); print("mergeDefaultEvictionSettings:", c.get("mergeDefaultEvictionSettings")); print("imageGCHighThresholdPercent:", c.get("imageGCHighThresholdPercent"))'
   sudo grep -n 'evictionHard\|mergeDefault' /var/lib/kubelet/config.yaml || echo "neither key is in the file"
   ```

2. Now put the post's `:128` to the node. There is no dedicated disk for the container runtime here,
   so if imagefs is ignored, the kubelet should have nothing to say about it. Ask for the Summary
   API and print both filesystems side by side, then ask what the node advertises as ephemeral
   storage.

   ```sh
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/stats/summary" \
     | python3 -c 'import sys,json; d=json.load(sys.stdin)["node"]; fs=d["fs"]; im=d["runtime"]["imageFs"]; print("nodefs  cap=%s avail=%s inodesFree=%s" % (fs["capacityBytes"], fs["availableBytes"], fs.get("inodesFree"))); print("imagefs cap=%s avail=%s inodesFree=%s" % (im["capacityBytes"], im["availableBytes"], im.get("inodesFree"))); print("runtime keys:", sorted(d["runtime"].keys()))'
   kubectl describe node $NODE | sed -n '/^Capacity:/,/^System Info:/p' | grep -i 'ephemeral\|Capacity\|Allocatable'
   df -h / /var/lib/containerd /var/lib/kubelet
   ```

3. Read the pinned tree before you change the machine, so that the later measurements land against
   text you have already seen. Four regions of one page, one gate file, and two counts.

   ```sh
   cd /path/to/kubernetes/website/content/en
   sed -n '119,147p' docs/concepts/scheduling-eviction/node-pressure-eviction.md
   sed -n '149,167p;232,261p;410,414p' docs/concepts/scheduling-eviction/node-pressure-eviction.md
   cat docs/reference/command-line-tools-reference/feature-gates/KubeletSeparateDiskGC.md
   grep -c 'KubeletSeparateDiskGC' docs/reference/command-line-tools-reference/kubelet.md
   grep -rln 'feature_gate_name="KubeletSeparateDiskGC"' --include='*.md' docs/
   ```

4. Split the disk. Stop the kubelet first and the runtime second, build a 3GiB ext4 filesystem in a
   preallocated file, copy containerd's store into it, and mount it where containerd expects its
   root to be. The old directory is kept, renamed, so that nothing is destroyed by this step.

   ```sh
   sudo systemctl stop kubelet
   sudo systemctl stop containerd
   sudo fallocate -l 3G /var/bw-imagefs.img
   sudo mkfs.ext4 -q /var/bw-imagefs.img
   sudo mkdir -p /mnt/bw-imagefs
   sudo mount -o loop /var/bw-imagefs.img /mnt/bw-imagefs
   sudo cp -a /var/lib/containerd/. /mnt/bw-imagefs/
   sudo umount /mnt/bw-imagefs
   sudo mv /var/lib/containerd /var/lib/containerd.orig
   sudo mkdir /var/lib/containerd
   sudo mount -o loop /var/bw-imagefs.img /var/lib/containerd
   df -h / /var/lib/containerd
   sudo systemctl start containerd
   sudo systemctl start kubelet
   ```

5. Ask the same two questions you asked in step 2. Nothing in the kubelet's configuration changed —
   the only thing that changed is a mount — so whatever moves here moved because the kubelet asked
   the runtime and got a different answer.

   ```sh
   sleep 60
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/stats/summary" \
     | python3 -c 'import sys,json; d=json.load(sys.stdin)["node"]; fs=d["fs"]; im=d["runtime"]["imageFs"]; print("nodefs  cap=%s avail=%s" % (fs["capacityBytes"], fs["availableBytes"])); print("imagefs cap=%s avail=%s" % (im["capacityBytes"], im["availableBytes"])); print("same device:", fs["capacityBytes"] == im["capacityBytes"])'
   kubectl describe node $NODE | sed -n '/^Capacity:/,/^System Info:/p' | grep -i 'ephemeral'
   kubectl get node $NODE -o jsonpath='{range .status.conditions[*]}{.type}={.status} {end}'; echo
   ```

6. Hunt for `containerfs`. The gate is on by default at this version, the eviction page documents
   two signals for it and says the thresholds are derived automatically, and the same page says the
   support exists only on CRI-O. Four places can answer: the Summary API, the kubelet's own metrics,
   the effective configuration, and the CRI itself.

   ```sh
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/stats/summary" \
     | python3 -c 'import sys,json; r=json.load(sys.stdin)["node"]["runtime"]; print("runtime keys:", sorted(r.keys()))'
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/metrics" | grep -c containerfs || echo "0 metric lines mention containerfs"
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" \
     | python3 -c 'import sys,json; c=json.load(sys.stdin)["kubeletconfig"]; print("evictionHard:", c.get("evictionHard")); print("featureGates:", c.get("featureGates", {}))'
   sudo crictl imagefsinfo
   sudo journalctl -u kubelet --since '5 min ago' | grep -i containerfs || echo "the kubelet has not used the word"
   ```

7. Stage the fillers before the filesystem is tight, because once the node reports pressure it is
   tainted and nothing new will schedule. Two Pods, one of which writes most of a gigabyte into its
   own writeable layer — which now lives on the new filesystem — and two images nothing is using, so
   that the kubelet has something to garbage-collect that is not a running container.

   ```sh
   kubectl create namespace bw-imagefs
   kubectl -n bw-imagefs run quiet --image=registry.k8s.io/pause:3.10 --restart=Never
   kubectl -n bw-imagefs run hog --image=docker.io/library/debian:trixie-slim --restart=Never \
     --command -- sh -c 'dd if=/dev/zero of=/hog.bin bs=1M count=700 && sleep 3600'
   kubectl -n bw-imagefs wait --for=condition=Ready pod/quiet pod/hog --timeout=300s
   sudo crictl pull docker.io/library/alpine:latest
   sudo crictl pull docker.io/library/busybox:latest
   sudo crictl images | wc -l
   df -h /var/lib/containerd
   ```

8. Cross the threshold. Leave 300MiB free on a 3GiB filesystem, which is 10% and comfortably under
   the 15% default you read in step 1, then watch for three minutes without touching anything. The
   order of what happens is the whole measurement.

   ```sh
   AVAIL=$(df -BM --output=avail /var/lib/containerd | tail -1 | tr -dc '0-9')
   sudo dd if=/dev/zero of=/var/lib/containerd/ballast bs=1M count=$((AVAIL - 300)) status=none
   for i in $(seq 1 12); do
     printf '%2s DiskPressure=%s avail=%s images=%s pods=%s\n' "$i" \
       "$(kubectl get node $NODE -o jsonpath='{.status.conditions[?(@.type=="DiskPressure")].status}')" \
       "$(df -h --output=avail /var/lib/containerd | tail -1 | tr -d ' ')" \
       "$(sudo crictl images -q | wc -l | tr -d ' ')" \
       "$(kubectl -n bw-imagefs get pods --no-headers | awk '{print $3}' | paste -sd, -)"
     sleep 15
   done
   kubectl -n bw-imagefs get events --sort-by=.lastTimestamp | tail -15
   kubectl -n bw-imagefs get pod hog -o jsonpath='{.status.message}'; echo
   ```

9. Two restarts, to settle what the pinned tree says about `mergeDefaultEvictionSettings`. First set
   one hard threshold and nothing else, and read back what happened to the other four. Then add the
   merge switch and a partial `evictionSoft`, and read back both maps. The API reference says the
   switch names four fields and that only one of them has defaults to merge; this is that sentence,
   executed.

   ```sh
   sudo rm -f /var/lib/containerd/ballast
   sudo cp /tmp/bw-kubelet-config.yaml /var/lib/kubelet/config.yaml
   printf 'evictionHard:\n  nodefs.available: "12%%"\n' | sudo tee -a /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet && sleep 45
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" \
     | python3 -c 'import sys,json; c=json.load(sys.stdin)["kubeletconfig"]; print("evictionHard:", c.get("evictionHard"))'
   printf 'mergeDefaultEvictionSettings: true\nevictionSoft:\n  nodefs.available: "20%%"\nevictionSoftGracePeriod:\n  nodefs.available: "2m"\n' | sudo tee -a /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet && sleep 45
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" \
     | python3 -c 'import sys,json; c=json.load(sys.stdin)["kubeletconfig"]; print("evictionHard:", c.get("evictionHard")); print("evictionSoft:", c.get("evictionSoft")); print("evictionMinimumReclaim:", c.get("evictionMinimumReclaim"))'
   ```

10. Offline, with no cluster. Put the post's two lists beside the pinned page's, and find out what
    the tree says about the KEP the post points at.

    ```sh
    cd /path/to/kubernetes/website/content/en
    sed -n '127p;130,135p;145,146p;195p' blog/_posts/2024/image-filesystem.md
    sed -n '236,241p' docs/concepts/scheduling-eviction/node-pressure-eviction.md
    grep -o 'kep.k8s.io/[0-9]*' blog/_posts/2024/image-filesystem.md
    grep -rn 'kep.k8s.io/4191' --include='*.md' docs/ | wc -l
    grep -rln 'KubeletSeparateDiskGC' --include='*.md' docs/
    ```

**Expect**

Step 1 prints a v1.35 server and an `evictionHard` map the kubeadm file never wrote. The map is the
shipped defaults, and there are five entries in it rather than the post's four: `memory.available`
at `100Mi`, `nodefs.available` at `10%`, `nodefs.inodesFree` at `5%`, `imagefs.available` at `15%`,
and `imagefs.inodesFree` at `5%`. `mergeDefaultEvictionSettings` is absent or false,
`imageGCHighThresholdPercent` is 85 — which is the same line as `imagefs.available` at 15%, drawn
from the other side — and the grep finds neither eviction key in `/var/lib/kubelet/config.yaml`,
which is why the backup you just took is enough to undo step 9.

Step 2 is where the post's `:128` fails. There is no dedicated disk, so by that sentence imagefs
should be out of the picture; instead the Summary API reports an `imageFs` block with real numbers,
and its capacity is identical to `fs`'s, because both are the root filesystem. Nothing is ignored:
two thresholds are armed against one device, and since 15% is stricter than 10%, the imagefs signal
is the one that will fire first on a node like this. The `runtime` keys should be `['imageFs']`
alone. The node's ephemeral-storage capacity matches the root filesystem, and `df` shows `/`,
`/var/lib/containerd` and `/var/lib/kubelet` on one line's worth of device.

Step 3 should produce a gate file with two stages and no `lockToDefault`, a body describing garbage
collection of images and containers on separate filesystems, exactly one `KubeletSeparateDiskGC`
line in the kubelet's flag reference, and exactly one page in the whole tree carrying the
`feature_gate_name` shortcode for it — `node-pressure-eviction.md`. Read `:139-147` carefully
against `:252-261`: the first says the support is CRI-O only, the second describes thresholds that
are set automatically on a node with any layout. Both are on the page you are reading; neither
mentions the other.

Step 4 should be quiet. `df` afterwards shows `/var/lib/containerd` on a loop device with a capacity
near 3.0G and the root filesystem unchanged, minus the 3GiB the image file occupies. If containerd
fails to start, the copy is the suspect — `cp -a` preserves the overlayfs metadata containerd
depends on and a plain `cp` does not. `/var/lib/containerd.orig` still holds the original store,
which is what makes this step reversible.

Step 5 is the split arriving, without a single configuration change. `imagefs` capacity is now about
3.0G against nodefs's twenty-odd, and `same device: False`. The kubelet was not told; it asked the
runtime, and the runtime answered differently. The second print is the post's other claim holding:
ephemeral-storage capacity on the node is unchanged, still measured from nodefs, even though a
container writing to its own root filesystem now writes somewhere else entirely. That is `:184-191`,
still exactly true two years later. Conditions should all read the healthy way, with
`DiskPressure=False`.

Step 6 is the one that settles the page against itself. Expect `runtime` keys to be `['imageFs']`
still, zero metric lines mentioning `containerfs`, no `containerfs` entry anywhere in the effective
`evictionHard`, and a kubelet log that has never used the word. `crictl imagefsinfo` should return
an `imageFilesystems` array with one entry pointing at the new mount; whether a
`containerFilesystems` key appears beside it at all is the thing to write down, because that key is
the CRI-level answer to the question. On this node, `node-pressure-eviction.md:145-146` is the half
that describes reality and `:252-261` and `:410-414` describe thresholds with no observable surface.
The gate is on. There is nothing behind it here.

Step 7 should give two Ready Pods and a visibly fuller filesystem. `hog` writes 700MiB into its own
writeable layer, which is on the new filesystem now, so `df /var/lib/containerd` jumps by about that
much while `df /` does not move. The image count goes up by two, and those two are the only images
on the node that nothing references — which is what makes them the kubelet's first move in the next
step.

Step 8 is the measurement the census row asks for, and the order is the answer. Within a
housekeeping interval or two of the ballast landing, `DiskPressure` flips to `True`. The image count
drops first: the kubelet garbage-collects unused images, which on this node means `alpine`,
`busybox` and anything else nothing is running. That is the `imagefs` branch of `:315-324` — with a
dedicated image filesystem the kubelet deletes images rather than sweeping dead pods off nodefs.
Then, because the ballast is a plain file the kubelet has no authority over and cannot reclaim,
pressure does not clear, and the second stage runs: a Pod is evicted, and it should be `hog` rather
than `quiet`, because with a separate imagefs the kubelet ranks candidates by the writeable-layer
usage of their containers (`:392-398`). The status message on `hog` should name the signal. Note
what this drill does *not* do: it never touches the root filesystem, and the worst case is a full
3GiB loop file.

Step 9's first read should show an `evictionHard` with one entry in it. The four defaults you
printed in step 1 are gone — the page's wording is that they are set to zero — and a node whose
operator set one threshold has quietly stopped watching memory. The second read should restore them:
`nodefs.available` stays at your 12%, and the other four reappear at their shipped values. Then look
at `evictionSoft`, which you also set partially, with the merge switch on. Expect exactly the one
entry you wrote, and no defaults merged into it, because `kubelet-config.v1beta1.md:1299-1305` says
the switch names four fields and that only `evictionHard` has default values to merge. Both prose
pages describe the switch without that qualifier.

Step 10 is arithmetic. The post's `:127` names four signals and `:130-135` lists four defaults;
`node-pressure-eviction.md:236-241` lists six lines, adding `imagefs.inodesFree` and a Windows
memory figure. The `grep -o` prints `kep.k8s.io/4191` once, and the search for that number across
the documentation tree returns nothing: the pinned tree never names a KEP for this gate, so whether
4191 is the right number is not a question this walk can answer. The last grep should find the gate
named in seven files — the gate file, the eviction page, and five component command-line references,
`kubelet`, `kube-apiserver`, `kube-controller-manager`, `kube-proxy` and `kube-scheduler`, each of
which offers a kubelet-only gate in its own `--feature-gates` help.

**Read on**

1. `docs/reference/command-line-tools-reference/feature-gates/KubeletSeparateDiskGC.md` and
   `docs/concepts/scheduling-eviction/node-pressure-eviction.md:139-167` together, as a pair. The
   gate file describes a capability; the page describes where it is available. The gap between them
   is this exercise.

2. `docs/concepts/storage/ephemeral-storage.md:44-92` — the same three layouts as the eviction page,
   written for a reader who cares about limits rather than evictions, and the place to look if step
   5's unchanged ephemeral-storage number surprised you.

3. [The phase-six disk-pressure cascade](../../labs/06/28-6c4-disk-pressure-cascade.md), which runs
   the same fill on a node with one filesystem and watches the kubelet try three things before it
   evicts anyone. Run it after this one and the difference is the point.

4. [The 2019 post that became a documentation page](../2019/05-pid-limiting.md), for the other
   disagreement about this same list of defaults — the eviction page's six entries against the
   kubelet configuration reference's four — settled the same way, from `configz`.

5. Unanswerable from the pin: what `containerfs` does on a node that can produce it. Every
   measurement in step 6 is an absence, and an absence on containerd says nothing about CRI-O. The
   pinned tree has no CRI-O node in it and neither does this lab.

**Teardown**

Put the kubelet configuration back from the backup taken in step 1, unmount the image filesystem,
restore containerd's original store, and delete the file. Then delete the probe namespace and
re-taint the control plane if you intend to keep the guest; leave it untainted if the next thing you
do is destroy it, which is [the standard teardown](../../strands/lab-topologies.md#teardown).

```sh
sudo cp /tmp/bw-kubelet-config.yaml /var/lib/kubelet/config.yaml
kubectl delete namespace bw-imagefs --ignore-not-found
sudo systemctl stop kubelet
sudo systemctl stop containerd
sudo umount /var/lib/containerd
sudo rmdir /var/lib/containerd
sudo mv /var/lib/containerd.orig /var/lib/containerd
sudo rm -f /var/bw-imagefs.img
sudo rmdir /mnt/bw-imagefs
sudo systemctl start containerd
sudo systemctl start kubelet
sleep 45
df -h / /var/lib/containerd
kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["kubeletconfig"].get("evictionHard"))'
rm -f /tmp/bw-kubelet-config.yaml
kubectl taint node $NODE node-role.kubernetes.io/control-plane=:NoSchedule || true
```
