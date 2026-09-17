<a id="userns-beta"></a>

# The post's only evidence is a video the pinned documentation never names, the two container runtimes it says cannot do this are exactly the two this lab already runs, and one process writes two files in the same second that the node reports as belonging to two different users

**Post** — [Kubernetes 1.30: Beta Support For Pods With User Namespaces](https://kubernetes.io/blog/2024/04/22/userns-beta/),
2024-04-22.

7,777 bytes, 158 lines, three authors: Rodrigo Campos Catelin of Microsoft, Giuseppe Scrivano of Red
Hat and Sascha Grunert of Red Hat. Thirty-fourth of 2024's 54 posts by size, 2,991 bytes under the
year's mean of 10,768, and the only post in the year that embeds a video. Its directory holds one
other file, `userns-ids.xcf`, a 96,554-byte GIMP document — twelve times the post's own prose, and
the only editable-source artifact among the 53 non-markdown files the year's post directories carry.
The figure a reader actually sees is pulled from the site's image tree at `:67`, not from here.

**As written**

The argument is four paragraphs long and it is the best short statement of the feature anywhere.
`:12-19`: a typical pod already runs in a network namespace and a PID namespace, and the user
namespace is the one that was left behind. `:21-24`: we are root inside the container and can do
everything root can inside the pod, but our interactions with the host are limited to what a
non-privileged user can do. `:26-31` defines a container breakout — a process inside a container
breaks out onto the host using some unpatched vulnerability in the container runtime or the kernel —
and says that with user namespaces both the privileges over the rest of the host and the files
outside the container it can access are reduced.

`:37-41` heads off the obvious collision: Linux user namespaces are a different concept from
Kubernetes namespaces. `:43-48` states the mapping rule twice over — the host UID/GIDs used for
different containers never overlap, and the identifiers can be mapped to unprivileged,
non-overlapping UIDs and GIDs on the host — and then names two benefits at `:50-65`. The first,
*prevention of lateral movement*, is careful: container A can do to container B's files only what
the file allows to others. The second, *increased host isolation*, is less careful: if a container
escapes the container boundaries, even if it runs as root inside the container, it has no privileges
on the host. `:69-72` repeats it as a contrast with the no-namespace case, with the parenthesis
*modulo bugs, of course*.

The release news is one section and three bullets, `:74-87`. A way for the kubelet to use custom
ranges for the UIDs/GIDs mapping; a way for Kubernetes to enforce that the runtime supports all the
features needed, so that a pod requesting user namespaces gets a clear error rather than, as before
1.30, being created without one; and more tests, including tests in cri-tools. `:89-91` sends the
reader to the documentation section on configuring custom ranges and says nothing further about how.

Then the *Demo*, `:93-109`, which is the post's only evidence and the only evidence in the year
delivered this way. CVE-2024-21626 is named, scored — *this vulnerability score is 8.6 (HIGH)* — and
described as allowing an attacker to escape a container and read or write any path on the node and
other pods on the same node. A video is embedded at `:103`. `:105-107` is the honest qualifier and
the most useful sentence in the post: with user namespaces, an attacker can do on the host file
system what the permission bits for *others* allow, so the CVE is not completely prevented but the
impact is greatly reduced. Finally `:111-147`, the node requirements: Linux 6.3 or greater, because
idmap mounts on tmpfs landed there; CRI-O with crun 1.9 or greater; and twice, in two consecutive
paragraphs, *if you are using CRI-O with runc, this is still not supported* and *if you are using
containerd with runc, this is still not supported*. Containerd support is targeted for containerd
2.0.

**As it runs now**

**The two sentences that say runc is not supported are both false here, and the node this exercise
runs on is the counter-example.** At the pin the prerequisites list two OCI runtimes:
`docs/concepts/workloads/pods/user-namespaces.md:52-53` gives crun 1.9 or greater, recommending
1.13+, and runc version 1.2 or greater. runc is on the list. The CRI side at `:59-60` gives
containerd 2.0 and later, and CRI-O 1.25 and later. The lab's node baseline installs containerd
2.2.1 and runc 1.5.1 from upstream tarballs and installs crun not at all, so every pod in this
exercise runs on the pairing the post names twice as unsupported. The containerd half of that — a
forecast that missed by a major version — belongs to [the alpha-announcement
exercise](../2022/10-userns-alpha.md) and is not recounted here; what is new is that the *OCI*
runtime the post rules out is now the one in the supported list, and the lab reaches the feature
through it.

**The per-pod ID count stopped being a constant.** The post is written in the release where every
user-namespaced pod got exactly 65536 IDs, and it never mentions the number. At the pin
`user-namespaces.md:233-251` documents a `KubeletConfiguration` field, `userNamespaces.idsPerPod`,
settable since Kubernetes v1.33, which must be a multiple of 65536, defaults to 65536, applies only
to containers created after the kubelet restarts, and which the page closes by saying that prior to
v1.33 the count was hard-coded. The generated API reference carries the same field at
`docs/reference/config-api/kubelet-config.v1beta1.md:2481-2490` and gives its type as `int64` with
the constraint *must be less than 1<<32*, where the concept page at `:244` calls it a `uint32`.

**The custom range the post points at in one sentence is now three requirements, five constraints
and a warning.** `user-namespaces.md:164-172` wants a user literally named `kubelet` — *you cannot
use any other username here* — the `getsubids` binary from shadow-utils on the kubelet's `PATH`, and
a subordinate ID configuration for that user. `:177-198` then imposes five rules: the first ID must
be a multiple of 65536 and at least 65536, the count must be a multiple of 65536, the count must be
at least `65536 x <maxPods>`, UID and GID ranges must match, ranges must not overlap anything else,
and the configuration must be exactly one line. `:214-228` adds the operational half the post has no
counterpart for: change this only with no user-namespaced pods running, drain the node first, and be
warned that *the kubelet will fail to start if it can't honor the new configuration for existing
pods on the node*.

**The documentation disagrees with itself about how many IDs a pod gets.** The task page states it
as a rule: `docs/tasks/configure-pod-container/user-namespaces.md:101-102` — *the last number of the
`uid_map` file inside the container must be 65536, on the host it must be a bigger number*. The
concept page states the opposite, that the number is a knob with a default. The same disagreement
runs through the constraint arithmetic: `user-namespaces.md:188-189` requires the subordinate count
to be at least `65536 x <maxPods>`, an expression written in a constant that the field two sections
later made configurable, and the page never restates it in terms of `idsPerPod`. Both halves are in
the tree that ships together, and step 8 settles which one a running kubelet obeys.

**What this exercise does not cover, and where it lives**

The ladder is not here. `UserNamespacesSupport` and its two dead siblings are transcribed in full by
[the alpha-announcement exercise](../2022/10-userns-alpha.md), which also owns the rename, the count
of gates that name a successor in prose, the reading of `/proc/self/uid_map` and the user-namespace
inode, the demonstration that two pods get non-overlapping ranges, the two kubelet metrics, and the
refusal of `hostNetwork`, `hostIPC` and `hostPID` alongside `hostUsers: false`. That exercise booked
this one: it says the obvious demonstration — `id` inside the container against the same process
seen from the node, and a file written in the container landing on the host under an unprivileged
UID — belongs to a later year's row. This is that row, and it does only that half.

The relaxation of the Pod Security Standards for user-namespaced pods, the
`UserNamespacesPodSecurityStandards` gate and its retirement paragraph, and reading `/etc/subuid` on
a node that has never been configured, all belong to [the runc CVE-2019-5736
exercise](../2019/02-runc-cve-2019-5736.md). That exercise deliberately reads the file and leaves it
alone. This one writes it, which is the other half and the reason the teardown here is longer.

Two limitations at `user-namespaces.md:296-313` are out of reach on this topology and are named
rather than run: no container in a user-namespaced pod may use `volumeDevices`, which needs a raw
block volume to test, and NFS volumes cannot be mounted because the Linux NFS client does not
support idmap mounts, which needs a second filesystem this lab does not provision. The CVE the post
demonstrates is also out of reach, and for a better reason: the node runs runc 1.5.1, which is not
vulnerable to it.

**The diff, and why**

***Broke.*** The node requirements section is the only part of the post that a reader can act on
wrongly today, and both of its runtime sentences have failed. runc gained support and is now on the
pin's list at `user-namespaces.md:52-53`; containerd 2.0 shipped and is on it at `:59`. A reader
following the post's `:120-126` in 2026 would conclude that the pairing this exercise runs on cannot
run the feature, and would go looking for crun. The paragraphs are not merely stale — they were the
practical gate on adopting the feature, which is why they are the longest section in a post whose
argument took four paragraphs.

***Never absorbed.*** The post's proof is a video and a CVE number. Neither entered the
documentation. `CVE-2024-21626` appears nowhere in the pinned tree — not in the docs, not in the
other 766 posts, not in the examples. The concept page makes the same argument with a *different*
vulnerability, `CVE-2021-25741` at `user-namespaces.md:158-162`, which is a Kubernetes CVE and
therefore appears in the project's own feed at
`docs/reference/issues-security/official-cve-feed.md:43`; the post's is a runc advisory and the
project's feed has no reason to carry it. So the strongest evidence the feature ever had is held in
a medium the documentation cannot cite and about a defect the documentation does not own. Step 9
counts it.

***Still right.*** The post's `:105-107` — with user namespaces an attacker can do on the host file
system what the permission bits for *others* allow, so the CVE is not completely prevented but the
impact is greatly reduced — is exactly right, exactly as qualified, and two years later the concept
page has still not said it that plainly. It is also the sentence a reader is most likely to skip,
because it sits under a video and reads as a disclaimer. Steps 4 and 5 are built to make it the
thing the reader cannot skip: the same in-container root writes two files, the node reports two
different owners, and a volume the pod mounts turns the *others* qualifier off entirely.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 cores, at `10.10.10.180`,
running Kubernetes v1.35 on containerd 2.2.1 and runc 1.5.1. Bring the guest up with [the five
provision steps](../../strands/lab-topologies.md#provision) and install Kubernetes with [the node
baseline procedure](../../strands/lab-topologies.md#node-baseline-steps). The node must be one you
are willing to reconfigure: steps 7, 8 and 10 create a system user, write `/etc/subuid` and
`/etc/subgid`, edit `/var/lib/kubelet/config.yaml` and restart the kubelet four times between them,
draining the node each time the page tells you to. Steps 2, 4, 5 and 9's `kubectl` half run from the
workstation; every `ssh zain@10.10.10.180` line needs `sudo` on the far end. Step 6 and most of step
9 need no cluster at all. The working namespace is `bw-userns` and the node-side scratch directory
is `/var/tmp/bw-userns`.

**Do**

1. Establish the floor the post says this node cannot clear. Every prerequisite at
   `user-namespaces.md:34-60` is readable before anything is created: the kernel version, the
   filesystem under the kubelet's pod directory, the CRI runtime, the OCI runtime, and whether crun
   is present at all. Take the node's before-state for the two files step 7 will write, and make the
   scratch directory the pods will share.

   ```sh
   NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl taint node $NODE node-role.kubernetes.io/control-plane- || true
   kubectl create ns bw-userns
   ssh zain@10.10.10.180 'uname -r; stat -f -c "%T %n" /var/lib/kubelet'
   ssh zain@10.10.10.180 'sudo ctr --version; sudo runc --version | head -1; command -v crun || echo "crun: absent"'
   ssh zain@10.10.10.180 'id kubelet 2>&1 | head -1; command -v getsubids || echo "getsubids: absent"'
   ssh zain@10.10.10.180 'sudo cat /etc/subuid /etc/subgid; echo "exit $?"'
   ssh zain@10.10.10.180 'sudo mkdir -p /var/tmp/bw-userns && sudo chmod 755 /var/tmp/bw-userns'
   ```

2. The whole of the census row, in two pods and two commands. Both pods are identical but for one
   field, both mount the same host directory, and both are asked the same question from the inside
   and from the outside. `user-namespaces.md:121-127` predicts the answer in prose and tells you to
   check it with `ps aux` from the host; it does not tell you what to expect for the pod that has no
   user namespace, which is why there are two.

   ```sh
   kubectl -n bw-userns apply -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata:
     name: uns
   spec:
     hostUsers: false
     containers:
     - name: shell
       image: registry.k8s.io/e2e-test-images/agnhost:2.53
       command: ["sleep", "3600"]
       volumeMounts:
       - name: out
         mountPath: /host-out
     volumes:
     - name: out
       hostPath:
         path: /var/tmp/bw-userns
         type: Directory
   ---
   apiVersion: v1
   kind: Pod
   metadata:
     name: plain
   spec:
     containers:
     - name: shell
       image: registry.k8s.io/e2e-test-images/agnhost:2.53
       command: ["sleep", "3600"]
       volumeMounts:
       - name: out
         mountPath: /host-out
     volumes:
     - name: out
       hostPath:
         path: /var/tmp/bw-userns
         type: Directory
   YAML
   kubectl -n bw-userns wait --for=condition=Ready pod/uns pod/plain --timeout=180s
   kubectl -n bw-userns exec uns   -- id
   kubectl -n bw-userns exec plain -- id
   ssh zain@10.10.10.180 'ps -eo user,uid,pid,comm,args | grep "[s]leep 3600"'
   ```

3. Name the runtime that just did it. The post says twice that this pairing is not supported, so the
   interesting artifact is not the pod but the runtime handle containerd recorded for it. Read the
   runtime name off the container object and the version off the binary, and confirm nothing else
   was quietly substituted.

   ```sh
   ssh zain@10.10.10.180 'sudo crictl ps --name shell -o table'
   ssh zain@10.10.10.180 'for c in $(sudo crictl ps --name shell -q); do sudo ctr -n k8s.io containers info "$c" | jq -r "[.ID[0:12], .Runtime.Name] | @tsv"; done'
   ssh zain@10.10.10.180 'sudo crictl version'
   ssh zain@10.10.10.180 'sudo runc --version'
   ```

4. One process, two writes, two answers. The pod that is root inside writes its own UID into a file
   on its root filesystem and into a file in the mounted host directory, in the same command, as the
   same user. Then read both from the node. `user-namespaces.md:79-91` says which of the two the
   mapping applies to; the post's *increased host isolation* paragraph at `:59-65` does not
   distinguish them.

   ```sh
   kubectl -n bw-userns exec uns   -- sh -c 'id -u > /root/marker; id -u > /host-out/uns-marker'
   kubectl -n bw-userns exec plain -- sh -c 'id -u > /root/marker; id -u > /host-out/plain-marker'
   ssh zain@10.10.10.180 'sudo ls -ln /var/tmp/bw-userns/'
   ssh zain@10.10.10.180 'sudo cat /var/tmp/bw-userns/uns-marker /var/tmp/bw-userns/plain-marker'
   ssh zain@10.10.10.180 'for p in $(pgrep -f "sleep 3600"); do sudo stat -c "%u %g %n" /proc/$p/root/root/marker; done'
   ```

5. Test the qualifier. The post's `:105-107` says an attacker with a user namespace can do on the
   host file system what the permission bits for *others* allow. Put three root-owned files on the
   node at three modes and ask the user-namespaced pod to read and to append to each. The files are
   reached through the volume the pod already mounts, which is the only path it has.

   ```sh
   ssh zain@10.10.10.180 'sudo sh -c "cd /var/tmp/bw-userns && echo secret > p600 && echo world > p644 && echo open > p666 && chown root:root p600 p644 p666 && chmod 600 p600 && chmod 644 p644 && chmod 666 p666"'
   for f in p600 p644 p666; do
     echo "== $f"
     kubectl -n bw-userns exec uns -- sh -c "cat /host-out/$f 2>&1 | head -1"
     kubectl -n bw-userns exec uns -- sh -c "echo appended >> /host-out/$f 2>&1 && echo 'write ok' || echo 'write refused'"
   done
   ssh zain@10.10.10.180 'sudo ls -ln /var/tmp/bw-userns/; sudo cat /var/tmp/bw-userns/p600'
   ```

6. Offline, before the node changes. Read the four blocks that steps 7 and 8 will act on, in this
   order: the prerequisites, the volume-ownership paragraph, the five constraints on the subordinate
   range, and the `idsPerPod` section. Then read the task page's rule and put the two `idsPerPod`
   citations side by side.

   ```sh
   cd /path/to/kubernetes/website/content/en
   sed -n '34,60p;79,102p' docs/concepts/workloads/pods/user-namespaces.md
   sed -n '164,199p;214,228p;233,251p' docs/concepts/workloads/pods/user-namespaces.md
   sed -n '96,111p' docs/tasks/configure-pod-container/user-namespaces.md
   grep -n 'idsPerPod' docs/concepts/workloads/pods/user-namespaces.md
   grep -n 'idsPerPod\|less than 1' docs/reference/config-api/kubelet-config.v1beta1.md
   ```

7. Configure the custom range, following `user-namespaces.md:164-212` exactly and `:214-228` first.
   Drain before touching anything, create the user with the name the page says you cannot vary,
   write the page's own example line into both files, find the binary the page requires, and
   restart. The append is checked afterwards because `useradd` on some distributions allocates a
   subordinate range of its own, and `:197-198` allows only one line.

   ```sh
   NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl drain "$NODE" --ignore-daemonsets --delete-emptydir-data --force --timeout=180s
   ssh zain@10.10.10.180 'sudo useradd --system --no-create-home --shell /usr/sbin/nologin kubelet'
   ssh zain@10.10.10.180 'echo "kubelet:65536:7208960" | sudo tee -a /etc/subuid /etc/subgid'
   ssh zain@10.10.10.180 'sudo grep -n "^kubelet:" /etc/subuid /etc/subgid'
   ssh zain@10.10.10.180 'command -v getsubids || sudo apt-get install -y uidmap; command -v getsubids || echo "getsubids: still absent"'
   ssh zain@10.10.10.180 'getsubids kubelet; getsubids -g kubelet'
   ssh zain@10.10.10.180 'sudo systemctl restart kubelet'
   kubectl uncordon "$NODE"
   ```

8. Settle the disagreement. Ask for four times the documented default, restart, and read the third
   column of a fresh pod's `uid_map`. The subordinate range written in step 7 is the page's own
   example, sized for 110 pods at 65536 IDs each, so this also asks whether the kubelet checks the
   `65536 x <maxPods>` arithmetic at `:188-189` against the configured `idsPerPod` or against the
   constant the sentence is written in.

   ```sh
   NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   ssh zain@10.10.10.180 'sudo cp -n /var/lib/kubelet/config.yaml /tmp/bw-kubelet-config.yaml'
   ssh zain@10.10.10.180 'printf "userNamespaces:\n  idsPerPod: 262144\n" | sudo tee -a /var/lib/kubelet/config.yaml'
   kubectl drain "$NODE" --ignore-daemonsets --delete-emptydir-data --force --timeout=180s
   ssh zain@10.10.10.180 'sudo systemctl restart kubelet'
   ssh zain@10.10.10.180 'systemctl is-active kubelet; sudo journalctl -u kubelet --since "-2 min" --no-pager | tail -20'
   kubectl uncordon "$NODE"
   kubectl -n bw-userns run wide --image=registry.k8s.io/e2e-test-images/agnhost:2.53 --restart=Never --overrides='{"spec":{"hostUsers":false}}' --command -- sleep 3600
   kubectl -n bw-userns wait --for=condition=Ready pod/wide --timeout=180s
   kubectl -n bw-userns exec wide -- cat /proc/self/uid_map
   ```

9. Count the evidence. The post's case rests on one CVE number and one video; the tree the post
   lives in carries neither. Search the whole pinned checkout for the CVE it names, then for the one
   the concept page names instead, then count how many of the year's 54 posts embed a video and what
   else this post's directory is carrying.

   ```sh
   cd /path/to/kubernetes/website/content/en
   grep -rn 'CVE-2024-21626' docs blog examples || echo "CVE-2024-21626: no matches in the pinned tree"
   grep -rn 'CVE-2021-25741' --include='*.md' docs | cut -c1-110
   grep -rl '{{< youtube' blog/_posts/2024/ ; echo "posts in 2024 with a video: above"
   find blog/_posts/2024 -type f ! -name '*.md' | wc -l
   ls -l blog/_posts/2024/userns-beta/
   grep -n 'image.svg' blog/_posts/2024/userns-beta/index.md
   ```

10. The warning at `user-namespaces.md:226-228`, tested rather than believed. With a user-namespaced
    pod still running and the node not drained, move the subordinate range to a different base and
    restart the kubelet. The page says the kubelet will fail to start if it cannot honour the new
    configuration for existing pods. Watch what it actually does, then put the range back before the
    teardown.

    ```sh
    kubectl -n bw-userns get pods -o wide
    ssh zain@10.10.10.180 'sudo sed -i "s/^kubelet:65536:7208960$/kubelet:131072:7208960/" /etc/subuid /etc/subgid'
    ssh zain@10.10.10.180 'sudo grep -n "^kubelet:" /etc/subuid /etc/subgid'
    ssh zain@10.10.10.180 'sudo systemctl restart kubelet'
    ssh zain@10.10.10.180 'systemctl is-active kubelet; sudo journalctl -u kubelet --since "-2 min" --no-pager | grep -i "subuid\|user namespace\|userns\|getsubids" | tail -20'
    kubectl -n bw-userns get pods -o wide
    kubectl get nodes
    ssh zain@10.10.10.180 'sudo sed -i "s/^kubelet:131072:7208960$/kubelet:65536:7208960/" /etc/subuid /etc/subgid'
    ```

**Expect**

Step 1: the kernel is 6.12 or later on Debian Trixie, comfortably past the 6.3 floor, and `stat -f`
reports `ext2/ext3` for `/var/lib/kubelet`, which is what a Trixie `ext4` root prints and which
`docs/concepts/workloads/pods/user-namespaces.md:46-47` lists as an idmap-capable filesystem. `ctr`
reports 2.2.1 and `runc` reports 1.5.1; `crun` is absent, because the node baseline never installs
it. `id kubelet` fails — there is no such user yet — and `getsubids` is absent. Both `/etc/subuid`
and `/etc/subgid` exist and are empty or missing entirely; the exit code is the honest answer and
either is fine. This is a node that meets every published requirement for the feature while meeting
none of the requirements for the *custom range* the post announced.

Step 2: both pods reach `Ready`, which is already the post's first claim falsified — a pod with
`hostUsers: false` started on containerd with runc. `id` prints `uid=0(root) gid=0(root)` inside
*both* pods; the user namespace changes nothing a process can see about itself. The host `ps` is
where they separate: the `plain` pod's `sleep` runs as `root` with `UID` 0, and the `uns` pod's
`sleep` runs under a UID at or above 65536 — on a default kubelet, a multiple of 65536 — with no
name in `/etc/passwd`, so `ps` prints the number rather than a user. Two processes, identical
inside, different to the node. That is the whole of the census row for this post.

Step 3: `crictl ps` lists both containers, and `ctr` reports the runtime name for each as
`io.containerd.runc.v2`. There is no crun in the picture and no second runtime handler configured.
`crictl version` reports the containerd 2.2.1 server, and `runc --version` reports 1.5.1 above an
OCI specification line. Written out together, this is the configuration the post's `:120-126`
describes twice as unsupported, running the feature the post is announcing.

Step 4: the two markers in `/var/tmp/bw-userns` are both owned by UID 0 and GID 0 on the node, and
both contain `0`. The pod with the user namespace and the pod without it produced identical results,
which is exactly what `user-namespaces.md:79-91` promises and exactly what the post's *increased
host isolation* paragraph would not lead you to expect. The `/proc/$p/root/root/marker` pair is
where they diverge: the `plain` pod's marker is `0 0`, the `uns` pod's is the same high UID and GID
that `ps` printed in step 2. One process, one `id -u` of `0`, two files written a microsecond apart,
and the node reports two different owners. The difference is not the process; it is whether the path
went through a volume.

Step 5: all three reads succeed and all three appends succeed, including `p600`, which is mode
`0600` and owned by `root`. The pod is root inside its namespace, the volume is idmapped so that
in-container UID 0 is the file's owner, and *owner* permissions apply. The post's qualifier — what
the permission bits for *others* allow — is a statement about a breakout, where the process arrives
on the host filesystem under its host UID and no idmap is in play. It is not a statement about
anything the pod mounts, and this step is the cheapest way to learn that before mounting something
that matters. If any of the three had been refused, the volume would not have been idmapped and the
feature would not be working.

Step 6: four blocks and one rule. The prerequisites list runc 1.2 or greater beside crun 1.9, and
containerd 2.0 beside CRI-O 1.25. The volume paragraph says in so many words that the inodes created
or read in volumes mounted by the pod will be the same as if the pod were not using user namespaces,
and names `hostPath` explicitly — step 4's result, stated three sections above the section that
would let you configure it away. The constraint list has six bullets, not five, once you count the
one-line rule separately. And `docs/tasks/configure-pod-container/user-namespaces.md:101-102` says
the last number of `uid_map` *must* be 65536, while the concept page's `idsPerPod` section says it
is a configurable multiple of 65536 with a default. The two `grep` outputs put the `uint32` of the
concept page beside the `int64` of the generated reference.

Step 7: the drain evicts `uns` and `plain` — they are bare pods, which is why `--force` is needed,
and they do not come back. `useradd` succeeds silently. The `grep` afterwards is the step's real
result: if it prints one line per file, the append is the whole configuration and the page's
one-line rule holds; if it prints two, `useradd` allocated a range of its own and you must delete
the line you did not write before the kubelet will accept the file. `getsubids` may already be
present, or arrive with `uidmap`, or not arrive at all — on a Debian node it ships in the `uidmap`
package alongside `newuidmap`. When it runs, `getsubids kubelet` prints `0: kubelet 65536 7208960`
and `getsubids -g kubelet` prints the same, which is the page's requirement that both ranges match.
The kubelet restarts and the node returns to `Ready`.

Step 8: the kubelet accepts the file and starts. `journalctl` shows a normal startup with no
complaint about the ratio between 262144 and the 7,208,960 subordinate IDs, which answers the
arithmetic question: the `65536 x <maxPods>` rule at
`docs/concepts/workloads/pods/user-namespaces.md:188-189` is a documentation constraint, not a
kubelet validation, and it is written in a constant the kubelet no longer uses. The `wide` pod
becomes `Ready` and `cat /proc/self/uid_map` prints three numbers whose third is `262144`, not
`65536`. The task page's *must* is false on this node, and it was made false by following the
concept page. Nothing in the tree flags the contradiction; the reader has to hold both pages open.

Step 9: `grep` finds no occurrence of `CVE-2024-21626` anywhere in the pinned checkout — not in the
767 posts, not in the documentation, not in the examples. `CVE-2021-25741` returns three lines:
twice in the concept page, where it is the worked motivation for keeping the host and pod ID ranges
apart, and once in `docs/reference/issues-security/official-cve-feed.md`, because it is a Kubernetes
vulnerability and the post's is a runc advisory. The `youtube` search returns exactly one path,
`blog/_posts/2024/userns-beta/index.md`. The `find` counts 53 non-markdown files across the year's
post directories, and the listing shows this one holds `userns-ids.xcf` at 96,554 bytes while the
figure the reader sees is fetched from `/images/blog/2024-04-22-userns-beta/image.svg`, a path
outside the post.

Step 10: the honest answer is whichever one you get, and the page's warning names only one of two
outcomes. If the kubelet refuses to start, `systemctl is-active` prints `activating` or `failed` and
the journal carries a line naming the subordinate range or the existing pod's mapping — the
documented behaviour, and the reason `user-namespaces.md:214-228` tells you to drain. If it starts
anyway, the node is now running a pod whose mapping falls outside the range the kubelet is
configured to hand out, and the warning describes a check that this version does not perform. Either
way the running pod keeps running, because a restart of the kubelet does not restart containers. Put
the range back before teardown so the file you delete is the file you wrote.

**Read on**

1. `docs/concepts/workloads/pods/user-namespaces.md:151-251` — the setup section this exercise
   executed, end to end: the three requirements, the six constraints, the reconfiguration warning
   and the `idsPerPod` field. Read `:79-102` immediately afterwards; the two sections are about the
   same numbers and they are 60 lines apart.

2. `docs/reference/config-api/kubelet-config.v1beta1.md:2465-2490` — the generated `UserNamespaces`
   type. One field, and the only place in the tree that states the upper bound as *less than 1<<32*.

3. [The alpha-announcement exercise](../2022/10-userns-alpha.md) — the ladder for all four
   user-namespace gates, the rename that the dead gate's own file is the only record of, and the
   `uid_map` and namespace-inode reading this exercise deliberately skipped.

4. [The runc CVE-2019-5736 exercise](../2019/02-runc-cve-2019-5736.md) — the Pod Security Standards
   relaxation for user-namespaced pods, and the same `/etc/subuid` file read on a node that has
   never been configured.

5. Unanswerable from the pin: what CVE-2024-21626 actually did. The post scores it, describes its
   effect in one sentence and links a video; the pinned tree never mentions it; and the runc
   advisory it points at is outside the checkout. The exercise can show that the mitigation the
   video demonstrates is real without ever naming the defect, which is both the honest position and
   a fair description of how much the documentation retained.

**Teardown**

Everything this exercise created is either in the `bw-userns` namespace, in `/var/tmp/bw-userns`, or
in three node files that are restored from the copies taken in steps 7 and 8. Run the whole block
even if a step failed: a half-written `/etc/subuid` will stop the kubelet from starting on the next
reboot, which is a worse outcome than any result above.

```sh
NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
kubectl delete ns bw-userns --wait=true
ssh zain@10.10.10.180 'sudo cp /tmp/bw-kubelet-config.yaml /var/lib/kubelet/config.yaml'
ssh zain@10.10.10.180 'sudo sed -i "/^kubelet:/d" /etc/subuid /etc/subgid'
ssh zain@10.10.10.180 'sudo userdel kubelet'
ssh zain@10.10.10.180 'sudo rm -rf /var/tmp/bw-userns'
ssh zain@10.10.10.180 'sudo systemctl restart kubelet'
ssh zain@10.10.10.180 'systemctl is-active kubelet; sudo grep -c . /etc/subuid /etc/subgid'
kubectl uncordon "$NODE"
kubectl get nodes
```

Re-taint the control plane if you intend to keep the guest for something else, and leave it
untainted if the next thing you do here is another blogwalk exercise on `solo`.

```sh
NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
kubectl taint node $NODE node-role.kubernetes.io/control-plane=:NoSchedule || true
```
