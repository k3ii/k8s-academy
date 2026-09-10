<a id="containerd-container-runtime-options-kubernetes"></a>
# The project this post announces survives in the pinned documentation as a tab id, a PNG filename and an AppArmor profile; the runtime it was written to displace has six migration pages, a glossary entry and a note saying it does not implement CRI at all; and of this curriculum's two hand-edits to `config.toml` one is gone because two defaults agreed, and the other is the answer the kubelet now asks for instead of reading its own setting

**Post** — [Containerd Brings More Container Runtime Options for Kubernetes](https://kubernetes.io/blog/2017/11/containerd-container-runtime-options-kubernetes/),
2017-11-02, Kubernetes v1.8. Lantao Liu (Google) and Mike Brown (IBM). 136 lines, one scope table,
two diagrams hosted on `googleusercontent.com`, and an `_Update:_` banner at lines 11-13 that the
authors did not write.

This is the last of 2017's eight, and it is the only one whose subject the curriculum has already
installed before the reader opens the file. Every other exercise in this year asks you to apply
something. This one asks you to look at what is already on the node.

**As written** — the post has a thesis, an argument in four parts, and a roadmap.

The thesis is in the first paragraph. There are several container runtimes — the post names Docker,
rkt, containerd and lxd — and Docker
is *"by far the most common container runtime used in production Kubernetes environments, but
Docker's smaller offspring, containerd, may prove to be a better option"* (line 15). The whole post
is an argument for that *may*.

The argument's first part is the interface. Line 17: Kubernetes 1.5 introduced CRI, so *"in theory,
Kubernetes could use any container runtime that implements CRI to manage pods, containers and
container images."* That interface is [the 2016 CRI post](../2016/13-container-runtime-interface-cri-in-kubernetes.md)'s
whole subject, and this post is what the interface was for: something other than Docker, arriving.

The second part is the case for containerd itself, and it is made as a table (lines 34-42) with
three columns — the feature, whether it is In or Out of containerd's scope, and what Kubernetes
requires. Six rows, six ✔️. Container lifecycle: In. Image management: In. **Networking: Out** —
*"No concrete network solution. User can setup network namespace and put containers into it"* —
justified because *"Kubernetes networking deals with pods, rather than containers, so container
runtimes should not provide complex networking solutions."* Volumes: Out. **Persistent container
logging: Out** — *"Container STDIO is provided as FIFOs."* **Metrics: In** — *"Containerd provides
container and snapshot metrics as part of the API."* The table's closing line, which has escaped its
own cell and sits in the markdown as a stray row at line 42: *"Overall, from a technical
perspective, containerd is a very good alternative container runtime for Kubernetes."*

The third part is the shim. containerd does not speak CRI, so something must, and that something is
a separate project, `cri-containerd`, hosted in the `kubernetes-incubator` GitHub organisation:
*"feature complete v1.0.0-alpha.0 release on September 25, 2017"* (line 19), written over six
months by engineers from five companies. It is drawn as its own box between the kubelet and containerd
(line 52), it eliminates *"an extra hop in the stack"* compared to dockershim (line 54), and the
Architecture section walks a single-container pod through it in seven numbered steps (lines 65-71).
Step 3 is the one to hold on to: *"cri-containerd configures the pod's network namespace using
CNI."*

The fourth part is Status (lines 76-85). Feature complete. All Kubernetes features supported. All
CRI validation tests passed. All node e2e tests passed.

Then the roadmap. Try it Out (lines 89-97) gives four separate installation routes: an ansible and
kubeadm multi-node installer, Kubernetes the Hard Way on Google Cloud, a release tarball, and
LinuxKit on a local VM. Next Steps (lines 103-119) lists stability work, then three usability items —
*"improve the user experience of crictl"*, integrate with `kube-up.sh`, *"improve our documentation"* —
and a date: *"We plan to release our v1.0.0-beta.0 by the end of 2017."*

Above all of it, lines 11-13, is a banner in the site's own editorial voice: *"Update: Kubernetes
support for Docker via `dockershim` is now deprecated."* It links a 2020 release announcement and a
GitHub issue. It was added to this post by the site, years later, and it warns the reader away from
the thing this post was already written to replace.

**As it runs now** — nothing here is a manifest, so nothing can be applied and nothing can fail to
apply. What can be checked is whether the words still name things. Sort them into four groups.

*Names that are gone from the pinned documentation entirely.* `rkt` and `lxd`, two of the four
runtimes the first sentence offers, occur zero times in the whole of `content/en/docs`.
`kubernetes-incubator`, the GitHub organisation that hosts every link in Try it Out and Contribute
and the crictl link in Next Steps, occurs zero times. `docs/getting-started-guides/` — the directory
that line 116's `kube-up.sh` link points into — does not exist, so that link is dead at the pin.

*Names that survive without prose.* `cri-containerd` occurs three times in `content/en/docs`, and
not once in a sentence. It is a Hugo tab id at `change-runtime-containerd.md:41`
(`{{< tabs name="tab-cri-containerd-installation" >}}`). It is a fragment of a PNG path at
`check-if-dockershim-removal-affects-you.md:67`
(`/images/blog/2018-05-24-kubernetes-containerd-integration-goes-ga/cri-containerd.png`). And it is
a line of sample output at `apparmor.md:107`, where a profile named `cri-containerd.apparmor.d` is
listed as `(enforce)`. A tab, an image filename, and a security profile: that is what is left of the
project, and none of the three is anybody explaining what it was.

*Names that grew.* `dockershim` occurs in thirteen files. Six of them are one directory,
`tasks/administer-cluster/migrating-from-dockershim/`, whose members are `_index.md`,
`change-runtime-containerd.md`, `check-if-dockershim-removal-affects-you.md`,
`find-out-runtime-you-use.md`, `migrating-telemetry-and-security-agents.md` and
`troubleshooting-cni-plugin-related-errors.md`. There is a glossary entry, `dockershim.md`, whose
body reads *"Starting with version 1.24, dockershim has been removed from Kubernetes."* And there is
a reference page, `topics-on-dockershim-and-cri-compatible-runtimes.md`, which is fifty-three lines
of nothing but reading material about the removal: four blog posts, two documentation pages, and a
KEP cited on its line 28 as *"KEP-2221: Removing dockershim from kubelet"*, followed by eight external
items from AWS, CNCF, Docker, Google, Microsoft, Mirantis and Tripwire. The alternative got three
non-sentences. The removal got a bibliography.

*Names that changed meaning.* Two of them, and they are the interesting pair.

The first is *container runtime*. The post's premise is that Docker is one — the most common one.
The pinned glossary entry `container-runtime.md` closes with: *"Kubernetes supports container
runtimes such as containerd, CRI-O, and any other implementation of the Kubernetes CRI."* Docker is
not in that list. It has a glossary entry of its own, `docker.md`, which describes it as
*"a software technology providing operating-system-level virtualization"* and never uses the phrase
*container runtime* at all. And `install-kubeadm.md:139-143`, on the page this curriculum's own
baseline follows, states it outright: *"Docker Engine does not implement the CRI which is a
requirement for a container runtime to work with Kubernetes. For that reason, an additional service
cri-dockerd has to be installed."* The runtime table two lines below lists three options, and Docker
appears in it only as *"Docker Engine (using cri-dockerd)"* — parenthesised, behind an adapter.

The second is *containerd*. The post's scope table put Networking firmly **Out**, on principle, with
a justification. The pinned glossary entry `containerd.md` reads: *"containerd takes care of fetching
and storing container images, executing containers, providing network access, and more."* Providing
network access is the row the post marked Out. It is In now, because cri-containerd — the separate
box in the post's own diagram, the thing whose step 3 called CNI — is no longer separate. It is
containerd's CRI plugin, and its presence on a node is asserted by an absence:
`container-runtimes.md:227-232` tells you that if you installed containerd from a package,
*"you may find that the CRI integration plugin is disabled by default. You need CRI support enabled
to use containerd with Kubernetes. Make sure that `cri` is not included in the `disabled_plugins`
list within `/etc/containerd/config.toml`."* The post's four installation recipes have become one
sentence about three letters not being in an array.

And the installation itself is now shorter than the post's shortest route. `container-runtimes.md:185-187`
is the entire containerd install instruction in the pinned documentation: *"To install containerd on
your system, follow the instructions on getting started with containerd. Return to this step once
you've created a valid `config.toml` configuration file."* One off-site link and a re-entry point.
`change-runtime-containerd.md:44-59` gives the Linux steps concretely, and they are three: install
the `containerd.io` package from Docker's own repositories, run
`containerd config default | sudo tee /etc/containerd/config.toml`, restart the service. This
curriculum's own [node baseline](../../strands/lab-topologies.md#node-baseline-steps) follows
exactly one of the three, and the middle one — allowing for `>/dev/null`. It installs no package at
all. It fetches the containerd tarball, the `containerd.service` unit and a `runc` binary from the
projects' release pages and verifies their checksums, because a package is a version, and the
version trixie ships cannot answer a call `kubeadm` now makes. The baseline's own note records
walking into that, on a node that had already been built. kubeadm still finds the result without
being told: `install-kubeadm.md:129-133` says it scans a fixed list of socket paths and only asks
you which runtime to use if it finds several or none.

Three things about that page deserve to be looked at rather than summarised, and steps 5, 11 and 12
below do the looking.

The first is that the pinned documentation's only occurrence of the string `bin_dir` in the whole of
`content/en/docs` is at `change-runtime-containerd.md:82`, inside a PowerShell comment, in the
Windows tab, on a page whose own first paragraph says it *"is applicable for cluster operators
running Kubernetes 1.23 or earlier."* The comment reads `# - cni bin_dir and conf_dir locations`,
and it is offered as one of two things to review after generating the default config. The Linux tab,
immediately above it, does not mention either. This curriculum's baseline used to set `bin_dir` with
a `sed` and now sets nothing: the edit existed because Debian's package patched the field to
`/usr/lib/cni` while the plugins sat in `/opt/cni/bin` the whole time, put there by `kubernetes-cni`,
which `kubelet` depends on. Upstream containerd defaults to the directory that was always right, and
at config schema `version = 3` the field is a list spelled `bin_dirs`. So the one place the pin names
the field is a Windows comment addressed to operators of a version it no longer serves, and the
spelling it names is the old one: `bin_dirs` appears nowhere in `content/en/docs` at all. The failure
the edit prevented outlives the edit, and the note beneath the baseline keeps it in view — the node
still flips to `Ready` and no pod can ever start.

The second is that `container-runtimes.md` disagrees with itself about how to spell the plugin.
Lines 206-222 give the `SystemdCgroup` setting twice, once per major version, and the difference is
not the value:

- containerd 1.x: `[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]`
- containerd 2.x: `[plugins.'io.containerd.cri.v1.runtime'.containerd.runtimes.runc.options]`

A different plugin id *and* a different quote character. Then lines 257-260, forty lines further
down the same page, show how to override the sandbox image — using `[plugins."io.containerd.grpc.v1.cri"]`,
the 1.x spelling, with no version note at all. The page teaches the rename and then ignores it.

The third is the mechanism that moved this curriculum's baseline, and four places in the pin do not
agree on whether it exists. `container-runtimes.md:145-149` says that at the pinned version, with
`KubeletCgroupDriverFromCRI` enabled and a runtime that supports the `RuntimeConfig` CRI RPC,
*"the kubelet automatically detects the appropriate cgroup driver from the runtime, and ignores the
`cgroupDriver` setting within the kubelet configuration."* A hundred lines further down the same
page, `:248-249` says *"In Kubernetes v1.28, you can enable automatic detection of the cgroup driver
as an alpha feature."* `kubelet-integration.md:83`, a kubeadm page, says flatly that *"the kubelet
cannot automatically detect the cgroup driver used by the container runtime."* And the gate file has
carried a `stable` stage defaulting on since v1.34.

Then the two deadlines, which are not the same deadline. `container-runtimes.md:156-157`: *"In
Kubernetes 1.38, this fallback behavior will be dropped, and older versions of containerd will fail
with newer kubelets."* The gate file's own body: *"The kubelet will stop falling back to this
configuration in Kubernetes 1.36."* The pin is v1.37, so one of those two dates has already gone by
and the fallback is still there — the node baseline's own note records a `kubeadm` run being handed
it on 2026-09-02, on a node carrying Debian's containerd 1.7 package, warning included. Nothing in
the pinned tree picks between the two dates. The node can be asked, though, and steps 11 and 12 ask
it.

**The diff, and why** — four of the template's seven cases land here, and the sixth is the one the
post's own subject ended up in.

*The post is still right.* The technical argument is intact and it won. containerd is the first
runtime named in the glossary's definition of the term, the first row of kubeadm's runtime table,
and the runtime on both of this curriculum's nodes. The scope reasoning that the table was built to
justify — that a runtime should not own networking, volumes or log format because Kubernetes owns
them — is still the pin's reasoning: `container-runtimes.md:171-175` requires v1 of the interface and
nothing more, and *"if a container runtime does not support the v1 API, the kubelet will not register
as a node."* The post asked to be judged on whether containerd was a good alternative. It is not an
alternative any more; it is the default, which is a stronger form of the same verdict.

*The post was retired by being agreed with.* cri-containerd was going to be a project: an incubator
repo, its own release cadence, its own alpha version number, its own installation documentation, its
own beta due by the end of 2017. None of that exists — not because it failed, but because it was
absorbed into containerd and stopped being a thing you install. There is no package, no version, no
name. The forecast came true, and that is exactly why the post's four installation routes cannot be
followed: what they install is not missing, it is everywhere, as a section of a TOML file.

*The post describes a plan the project abandoned.* That plan is `kube-up.sh`. Next Steps promised
integration with it, and the directory that documented it is gone from the pin, so the integration
target outlived neither the shim nor the post. The two disappearances read the same from a distance
and are opposites up close, which is why the template keeps them as separate cases: one forecast was
honoured and the other was reversed.

*The post has been overtaken by stasis.* Two of the six rows in the scope table were bets on future
plumbing, and the ladders below measure where that plumbing got to. Metrics was ticked ✔️ in 2017 on
the strength of containerd exposing them; the gate that makes the kubelet actually read pod and
container stats over CRI went alpha in v1.23 and reached beta in v1.37, still defaulting off — the
tick is fourteen releases old and the wire is not on yet. Persistent container logging was marked
Out on principle; the kubelet feature that took the job graduated to stable in v1.21 and was retired
two releases later. And crictl, the third usability item on the roadmap, has carried
`{{< feature-state for_k8s_version="v1.11" state="stable" >}}` at the top of its documentation page
ever since, moved from `kubernetes-incubator/cri-tools` to `kubernetes-sigs/cri-tools`
(`crictl.md:19`), and is still installed by downloading a tarball from a release page and matching
its version to your Kubernetes version by hand (`crictl.md:27-32`). Nine years of stability and no
package.

The cases that do *not* apply are the interesting absence. Nothing in this post was wrong when
published, and nothing in it broke. There is no manifest to break, and no instruction here fails on
its own terms. The sixth case is the only one that can explain why they cannot be followed anyway.

**The ladder** — the post's subject has no gate and never had one, so the ladders here belong to the
scope table's three most load-bearing rows: the one the post ticked, the one it disclaimed, and the
one the curriculum's own `sed` sits inside. Each is transcribed whole from its gate file's
`stages:` list.

`PodAndContainerStatsFromCRI` is the Metrics row:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.23 – v1.36 |
| beta | `false` | — | v1.37 –  |

Fourteen releases in alpha, beta in the pinned release, and the default has never changed. The
post's ✔️ described containerd's side of the contract, which was ready. The kubelet's side is a
switch you still have to throw.

`CRIContainerLogRotation` is the Persistent Container Logging row, and its file carries
`removed: true`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.10 – v1.10 |
| beta | `true` | — | v1.11 – v1.20 |
| stable | `true` | — | v1.21 – v1.22 |

One release in alpha, ten in beta, two in stable, then gone. The post said container log format was
out of a runtime's scope because Kubernetes had specific requirements. Kubernetes met them itself,
and the gate that says so is retired because it is unconditional now.

`KubeletCgroupDriverFromCRI` is the row the post did not have, and it is the one that reaches the
learner's own `config.toml`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.28 – v1.30 |
| beta | `true` | — | v1.31 –  |
| stable | `true` | — | v1.34 –  |

Stable, defaulting on, since v1.34, and the `beta` stage in the file has no `toVersion` at all, so
two stages claim v1.34 onwards. Three facts in the gate file's body carry more than the table does.
The first names a runtime version: *"containerd: Support was added in v2.0.0"*, which is the whole
reason this curriculum's baseline fetches a tarball instead of installing a package. The second is a
deadline the page above disagrees with, and it is the third thing in *As it runs now*. The third is
an instrument — *"Admins can use the metric `kubelet_cri_losing_support` to see if there are any
nodes in their cluster that will lose support"* — which
`docs/reference/instrumentation/metrics.md:2394-2399` records as an ALPHA gauge whose single label
is `version`.

`container-runtimes.md:151-154` says why the fallback is there at all: *"older versions of container
runtimes (specifically, containerd 1.y and below) do not support the `RuntimeConfig` CRI RPC… and
thus the Kubelet falls back to using the value in its own `--cgroup-driver` flag."*

So the direction of the question has reversed. In 2017 you configured the kubelet and hoped the
runtime agreed. At the pin the runtime is asked and the kubelet's own setting is ignored, unless the
runtime is too old to be asked. Step 4 records which containerd the node has, and steps 11 and 12
are where that number becomes the answer to a question about the baseline rather than about the
post.

**No gate** — there is no `feature-gates/cri-containerd.md`, no `feature-gates/containerd.md` and no
gate for CRI itself. The interface graduated by shortcode: `cri.md:24` carries
`{{< feature-state for_k8s_version="v1.23" state="stable" >}}`, and that is the only dating
instrument the pin offers for the thing this post was built on top of. Twenty-two gate files have `cri`, `container` or `runtime` in their names and not one of them
governs whether CRI is used; the one that names the protocol itself, `CRIListStreaming`, gates a set
of server-side streaming RPCs carried over it, described at `cri.md:45-66`. The nearest thing to a date for the post's own subject is
negative evidence: `container-runtimes.md:173-175` names v1.26 as the release in which only CRI v1
works, so a runtime that speaks only the version cri-containerd shipped would not register a node at
all.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair): a control-plane node at
`10.10.10.130` and one worker at `10.10.10.131`. Almost every command below runs on one node and
reads one node's filesystem, so `solo` would carry the exercise. Two nodes are wanted for step 8.
The runtime holds the control plane's static pods exactly the way it holds an application pod, and
the only way to see that is to run the same command on a node that has them and a node that does
not. The contrast is the point, and it needs two machines.

Provision with the five steps at [`#provision`](../../strands/lab-topologies.md#provision), then the
node baseline at [`#node-baseline-steps`](../../strands/lab-topologies.md#node-baseline-steps) on
both nodes, then `kubeadm init --pod-network-cidr=10.244.0.0/16`, Flannel, and the join command on
the worker. Take the current minor; step 11 asks you to compare it to a number in the pin, and any
recent minor gives the same answer. Then `ssh zain@10.10.10.130`.

Do not skip the baseline's one `sed` in order to watch it fail, and take the tarball rather than the
package: `apt-get install -y containerd` produces a node this pin's `kubeadm` warns about and the
next release refuses. Step 6 shows you the edit without changing anything.

**Do**

1. Ask the pin's own question — what runtime do these nodes use — the pin's own way:

   ```sh
   kubectl get nodes -o wide
   ```

   `find-out-runtime-you-use.md:24-30` gives this exact command as the whole answer, and prints two
   sample outputs at `:37-41` and `:50-55`: `docker://19.3.1` on a v1.16 cluster and
   `containerd://1.4.1` on a v1.19 one. Read your own `CONTAINER-RUNTIME` column and write down the
   version string. The post argued for a runtime. The cluster you built before reading the post
   already runs it, and you were never asked.

2. Find the socket, the way the pin says to:

   ```sh
   tr \\0 ' ' < /proc/"$(pgrep kubelet)"/cmdline; echo
   ```

   That is `find-out-runtime-you-use.md:81` verbatim. The page tells you at `:86-95` to look for two
   flags: `--container-runtime` and `--container-runtime-endpoint`. Note which of the two you have,
   and note `:92` — *"the `--container-runtime` command line argument is not available in Kubernetes
   v1.27 and later."* One of the two flags the page's own instructions ask you to find cannot be
   there.

3. Look for the thing the banner at lines 11-13 is warning you about:

   ```sh
   command -v docker; echo "exit $?"
   dpkg -l | grep -i docker; echo "exit $?"
   ```

   Both find nothing and both exit non-zero. This is where the census row for this post has a broken
   premise, recorded in full in the [note at the end](#loose-row): it predicts that `docker ps`
   returns success and an empty list. On these nodes there is no `docker` to run. The quiet failure
   is quieter than the row expected — the command does not return an empty list, it does not exist.

4. Find out what put containerd on this node, and record the major version:

   ```sh
   containerd --version
   ctr --version
   ls /usr/local/bin /usr/local/sbin
   dpkg -S "$(command -v containerd)"; echo "exit $?"
   ```

   Write the containerd major version down. Steps 11 and 12 are about that number. The last command
   is the interesting one: no package owns this binary, so `dpkg -S` exits non-zero and says so. The
   pin's own concrete instruction, `change-runtime-containerd.md:44`, is to install a package, and
   this node has none — the reason is under *As it runs now*. Then read the two directory listings
   against the post: containerd and `ctr` from one release page, a shim beside them, and `runc` from
   a second project's release page because containerd 2.x needs a newer one than trixie ships. There
   is no `cri-containerd` binary anywhere in either, because there is no cri-containerd.

5. Read the configuration the baseline generated, and find the plugin the post drew as a separate
   box:

   ```sh
   grep -n 'SystemdCgroup\|bin_dir\|conf_dir\|sandbox_image\|disabled_plugins\|^version' /etc/containerd/config.toml
   sudo ctr plugin ls | grep -i cri
   ```

   Four things to check against the pin. `disabled_plugins` should be an empty list, which is what
   `container-runtimes.md:227-232` requires and the whole of what "install cri-containerd" has become.
   `SystemdCgroup` is the baseline's one `sed` edit, and `bin_dir` is the one it used to make: the
   spelling your `grep` finds instead tells you which schema this file is written in, and neither
   spelling is the one the pin names. `sandbox_image` names the pause
   container from the post's Architecture step 2, and `container-runtimes.md:257-260` shows the
   override with a concrete value. And read the plugin id in the section headers your `grep` printed:
   compare it, character for character including the quote marks, to the two spellings at
   `container-runtimes.md:206-222`. Which major version is your `config.toml` written in?

6. See the edit as an edit, without changing anything:

   ```sh
   containerd config default | diff - /etc/containerd/config.toml
   ```

   `containerd config default` writes to stdout, so this touches nothing. The diff is the baseline's
   one `sed` line and nothing else: one word changed in one line. It used to be two lines, and the
   one that went away is the more interesting of the pair — it existed only because a packaged
   containerd looked for CNI plugins in a directory nothing filled, and its absence is the
   difference between a working node and a node that reports `Ready` while no pod can ever start.
   Nothing prevents that failure now except two defaults happening to agree, which is what the note
   beneath the baseline is for.

7. Confirm that the interface the post is built on is the interface in use, from the kubelet's side:

   ```sh
   sudo systemctl status containerd --no-pager | head -5
   ls -l /run/containerd/containerd.sock
   ```

   `container-runtimes.md:198` gives `/run/containerd/containerd.sock` as the default CRI socket on
   Linux. Compare it to the endpoint you read in step 2. The kubelet is a gRPC client, per
   `cri.md:26`, and this socket file is the whole of what the post's diagram drew as three boxes.

8. Look at what the runtime is holding, in both of its namespaces, on the control plane:

   ```sh
   sudo ctr namespaces list
   sudo ctr containers list
   sudo ctr -n k8s.io containers list
   ```

   The first `containers list` runs in the `default` namespace and prints a header and nothing else,
   exit 0. The second prints every sandbox and every application container on the node. Now do the
   same on the worker:

   ```sh
   ssh zain@10.10.10.131 'sudo ctr -n k8s.io containers list'
   ```

   Compare the two lists. The control plane's includes etcd, the API server, the scheduler and the
   controller manager. The worker's does not. To containerd, a static pod is a container like any
   other; nothing in the list says which of them Kubernetes considers infrastructure. Neither list
   mentions pods, because containerd has no pods — that concept lives in the CRI layer above, which
   is the reason the post needed a shim at all.

9. Find the sandbox container the post's Architecture step 2 sends you off-site to read about:

   ```sh
   sudo ctr -n k8s.io images list | grep -i pause
   sudo ctr -n k8s.io containers list | grep -ci pause
   ```

   Compare the image reference to the `sandbox_image` value from step 5, and the count to the number
   of pods on the node. Every pod has one. The post links an external essay to explain what it is;
   the pin gives it a config key and moves on.

10. Look for the tool the roadmap wanted improved:

    ```sh
    command -v crictl; echo "exit $?"
    ls -l /etc/crictl.yaml; echo "exit $?"
    ```

    Whichever way these come out, `crictl.md:27-32` is the pin's install instruction — download a
    tarball from a release page, match its version to your Kubernetes version, move it onto your
    path — and `crictl.md:39-42` lists three ways to point it at a socket, one of which is the file
    you just looked for. If `crictl` is present, run
    `sudo crictl --runtime-endpoint unix:///run/containerd/containerd.sock pods` and compare its
    output to step 8's second list: the same containers, grouped into the concept `ctr` does not
    have.

11. Ask which of two cgroup-driver settings the kubelet is obeying:

    ```sh
    sudo grep -n 'cgroupDriver' /var/lib/kubelet/config.yaml; echo "exit $?"
    ```

    Now put three facts side by side. The ladder above says `KubeletCgroupDriverFromCRI` has been
    stable and on by default since v1.34. `container-runtimes.md:145-149` says that with that gate
    the kubelet asks the runtime which driver it uses and *ignores* the key you just grepped for.
    `container-runtimes.md:151-154` says containerd 1.y cannot answer that query, so on those
    versions the kubelet falls back to *"the value in its own `--cgroup-driver` flag"* — the pin's
    words, and worth holding against the fact that the setting you grepped for lives in a file and
    not in a flag. Your containerd major version is the one you wrote down in step 4.

    Work out from those three which of two settings decides this node's cgroup driver: the
    `cgroupDriver` key in this file, or the `SystemdCgroup = true` that the baseline's one `sed`
    writes into `config.toml` and step 6 showed you. In the post's era neither component asked the
    other: you set both by hand and they had to match. Only one of the two is still set by hand on
    this node, and it is not the kubelet's. If the `grep` finds nothing at all, that is an answer
    too, and a stronger one: a generated file has stopped carrying a key nothing reads. Then read
    `container-runtimes.md:156-157` against the deadline quoted from the gate file's body under *As
    it runs now*, and notice they name different releases for the same removal while the pin you are
    reading is v1.37.

12. Ask the kubelet whether it is on the path being removed:

    ```sh
    for N in $(kubectl get nodes -o name | cut -d/ -f2); do
      echo "== $N"
      kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" | grep 'kubelet_cri_losing_support'
      echo "exit $?"
    done
    ```

    The gate file's body names this metric for exactly this question, and
    `reference/instrumentation/metrics.md:2394-2399` gives its shape: an ALPHA gauge with a single
    `version` label, and help text reading *"the Kubernetes version that the currently running CRI
    implementation will lose support on if not upgraded."* Do not predict the output. If the metric
    is absent, the kubelet has nothing to warn about, and that absence answers step 11 a second way.
    If it is present, its `version` label names the release this node stops working in, and you can
    hold that number against the two deadlines you have just read and see which of them the running
    code agrees with. A pinned tree that contradicts itself can be adjudicated by a cluster, and
    this is the command that does it.

**Expect** — every command exits zero except the four deliberate probes in steps 3, 4 and 10, whose
non-zero exits are the finding. Nothing in this exercise creates, deletes or modifies an object, a
file or a service; step 6 is the only command that could and it writes to a pipe. The list in step 8
differs between the two nodes by exactly the control-plane static pods. The plugin id in step 5
matches one of the two spellings at `container-runtimes.md:206-222` and not the other, and which one
it matches is the same fact as the containerd major version from step 4 and the same fact again as
the setting the kubelet obeys in step 11. Three separate observations, one number — and step 12 is a
fourth reading of it, taken from the running kubelet rather than from a file.

Three outputs cannot be predicted here, and each of the three is a question rather than a check.
Step 10's depends on whether `crictl` came in with the `kubeadm` package on the minor you installed,
and the pin does not say — its own instruction assumes you install the tool by hand. Step 11's
depends on whether the generator still writes a key the kubelet no longer reads. Step 12's depends on
whether the kubelet has anything to warn about. Every outcome of all three is informative and none of
them is a mistake in the lab.

**Read on** — five questions. Four can be answered from the pinned tree; the fifth cannot be
answered from anywhere and is the one worth carrying.

1. `change-runtime-containerd.md` is a task page in v1.37 documentation whose first paragraph scopes
   it to *"cluster operators running Kubernetes 1.23 or earlier"*, and it is the only page in the
   tree that names `bin_dir`. Read it end to end and ask which of its steps a reader on a supported
   version could still use, and why the two review items in its Windows tab at `:80-83` — the
   sandbox image and the CNI directories — appear nowhere in its Linux tab. This curriculum's
   baseline sets neither key, and one of them the pin no longer spells the way it names it, so ask
   whether the omission is a gap in the baseline or a gap in the page.

2. The plugin id changed and one page uses both spellings. Read `container-runtimes.md:206-222`
   against `:252-260` and work out what a reader with containerd 2.x would produce if they followed
   the second section after the first. Then ask the same question of the baseline's one surviving
   `sed`, and notice that it matches the `SystemdCgroup = false` assignment rather than the plugin
   header above it, so it lands whichever spelling generated the file. Ask which lines of a generated
   config are safe to edit by hand on that basis, and what it cost the edit that did not survive.

3. `topics-on-dockershim-and-cri-compatible-runtimes.md` is a fifty-three-line bibliography about a
   removal. `cri-containerd` has three non-prose occurrences. Read the six files in
   `migrating-from-dockershim/` and ask where a reader is supposed to learn what the CRI layer inside
   containerd *is*, as opposed to how to migrate onto it — and whether `cri.md`, which is seventy
   lines about the protocol, is that place.

4. The post's Metrics row was ticked in 2017 and `PodAndContainerStatsFromCRI` reached beta, off by
   default, in the pinned release. Read `reference/instrumentation/cri-pod-container-metrics.md`
   against `node-metrics.md` and work out what is serving pod metrics on your cluster right now if
   that gate is off, and what the tick in the post's table was actually claiming.

5. The one that has no answer at the pin. This post's argument was won so completely that its subject
   ceased to be nameable: there is no package, no version, no repository and no documentation page
   for the thing five organisations spent six months building, because it became a section of a TOML
   file. Every other exercise in this year walks a divergence between a post and a cluster. Here
   there is no divergence to walk — the cluster agrees with the post entirely, and that is why the
   post is unreadable as instructions. Ask what an archive is supposed to do with a document that was
   right, and then ask why the site's editors added a warning banner to it in 2020, addressed to a
   danger the post itself is the escape from.

**Teardown** — [`#teardown`](../../strands/lab-topologies.md#teardown). There is nothing to
restore, because nothing was changed: this is the only exercise in 2017 that reads the cluster
without writing to it. The `pair` cluster is exactly as `kubeadm init` and the join left it, and it
is reusable as it stands.

<a id="loose-row"></a>
**One note on the census.** 2017's row for this post says *"`docker ps` on a modern node returns
success and an empty list, which is the quietest failure in the archive, and the lab's own nodes
already run containerd."* The second clause is right and it is this exercise's foundation. The first
clause has a premise this curriculum's nodes do not meet. `docker ps` returning an empty list
requires a Docker Engine to be installed and running, and the node baseline installs containerd
from an upstream tarball and never installs Docker. On these nodes the command is absent, so step 3
substitutes `command -v docker` and gets a non-zero exit rather than a successful empty list. The
observation the row was reaching for survives in a different place: `sudo ctr containers list` in the
`default` namespace exits zero and prints a header with no rows, on a node running dozens of
containers, because they are all in the `k8s.io` namespace. That is step 8, and it is quieter than
`docker ps` would have been. Census rows are immutable, so the row stands as written and this file
walks the post rather than the row.
