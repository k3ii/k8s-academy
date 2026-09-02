# Lab topologies

This document describes nine named guest layouts. For each layout it gives three
things. It gives the size of each node. It gives the address of each node. It gives the
commands that build the layout and remove it. The document also explains how you reach
a cluster that runs inside the bastion.

**How to use this document.** An exercise names **one topology**. The exercise links to
the row for that topology in this document. An exercise never repeats a footprint.

**Where these facts come from.** This document derives from
[`../research/lab-topologies.md`](../research/lab-topologies.md). The research date is
2026-08-18. The research is verified against `k3ii/factory@6f4692f`. That tree holds the
full audit of what `factory` contains. Seven of the sizing decisions come from
[#8](https://github.com/k3ii/k8s-academy/issues/8). The eighth comes from
[#14](https://github.com/k3ii/k8s-academy/issues/14). Some facts have no real tree and
no real measurement behind them. This document marks each of those facts
**[UNVERIFIED]** where the fact occurs. It also lists them together in
[What is not confirmed](#unverified).

<a id="contract"></a>
## The commands were a contract before they were a description

**The `tofu/labs` module landed in [`k3ii/factory`](https://github.com/k3ii/factory) on
2026-08-30, in commit `266dac0`. The module declares all nine topologies.**

Read the history in the correct order. Every provision command and every teardown
command in this document was written before the module existed. Each command was a
specification. The specification told `factory` what to build. It did not describe
something that was already built. `factory` has since implemented the specification.
The commands in this document now match what the module exposes.

This order was deliberate ([#49](https://github.com/k3ii/k8s-academy/issues/49)). The
curriculum leads, and the homelab follows. The alternative was worse. Approximately 100
exercises would cite an interface that was built for a different purpose.

**The exercises no longer point here for that reason.** Five lab files held a pointer to
this section. The pointer was named *"what does not exist yet"*.
[#75](https://github.com/k3ii/k8s-academy/issues/75) removed the pointer. The reason is
simple. A provision block that fails today is a bug, and you report it. It is no longer
a gap in `factory`. The exercises now point to [the contents of a node](#node-baseline)
instead. That is a decision, and not a gap. This section keeps the record of why the
interface came first.

`phases/08-storage.md` shipped one such block before this document existed. That block
was not fiction. It was this same specification. The author wrote it as though the
module already existed.

<a id="ceiling"></a>
## The ceiling — you can spend about 9.5GB

The node is an i5-8400T. It has 6 cores. Some machines must stay up at all times. After
you subtract them, you can spend **about 9.5GB of RAM and 95G of disk** on a topology.

| What holds RAM | Amount | Status |
|---|---|---|
| The Proxmox host | ~1.6GB | Measured. |
| `hopper` | 2048MB | **Must stay up.** It is the only machine that runs `tofu` and Ansible. |
| `carthage` | 1024MB | **Must stay up.** It holds the OpenTofu state bucket. |
| `jeremie` | 1024MB | **Reclaimed** ([#8](https://github.com/k3ii/k8s-academy/issues/8)). Destroyed on 2026-08-18, for the duration of the academy. |
| [`forge`](#build-guest) | 1536MB · 2560MB during P3 and P5 | Never torn down. It is **not part of any topology**. |
| Host page cache | ~1.0GB | Held back deliberately. |
| **A topology, plus `forge`** | **~9.5GB** | |

**Budget against 9.5GB. Do not budget against the 9.9GB that the host reports as
available.** Both figures are the same budget at two points in one subtraction. The
9.9GB figure comes before the page-cache holdback. The 9.5GB figure comes after it. A
footprint that fits in 9.9GB but not in 9.5GB does not fit. `jeremie` is destroyed, and
`forge` is declared, so the assumptions behind the figure hold. The figure is still
[a subtraction and not an observation](#unverified).

**Run one topology at a time. This rule applies to RAM and also to disk.** For example,
`workhorse` needs 65G and `nested` needs 40G. The two need 105G together, and only 95G
exists. Their RAM would fit together, but their disks do not. A topology can therefore
fail to provision because of disk while the memory arithmetic says that it fits.

**Every guest runs with `balloon 0`. No guest gives a page back.** No guest carries a
`virtio-balloon` device. Nothing can therefore reclaim a page after the guest touches
it. The configured size is a ceiling. Each guest walks toward that ceiling and never
retreats from it. This behaviour is what makes the arithmetic safe to budget against.

**The guest does not take all of its RAM at boot.** The guests also run without
`prealloc=on`. KVM therefore backs guest RAM lazily. The host pays only for the pages
that the guest touches. Measurements on `factory` after 27 hours of uptime show this
effect:

- `hopper` used 937MB of its 2048MB.
- `forge` used 915MB of its 1536MB.
- `carthage` used 879MB of its 1024MB.

**Read every row in the table below as an upper bound.** A topology that is up costs
less than its figure until you work it.

**KSM is off, so the multi-node rows get no discount.** The file
`/sys/kernel/mm/ksm/run` contains `0`. The host does not share identical pages between
guests. The sum of the nodes is therefore the correct shape for a multi-node figure.

**Do not treat swap as a safety valve.** The host has 6.1GB of swap. A swapped etcd
gives you fsync stalls. The stalls cause missed Raft heartbeats. The cluster then looks
broken for reasons that have nothing to do with the lesson. Staying under budget is the
whole mechanism.

<a id="topologies"></a>
## The nine topologies

**Read the sizing as an allocation decision, and not as a measurement.** This applies to
eight of the nine rows. Only `pair` [has been weighed](#measured). For the other rows,
see [what is not confirmed](#unverified).

**Link to a row, and not to the table.** Each row carries its own anchor.

| Topology | Nodes | Per node | RAM | Disk | For |
|---|---|---|---|---|---|
| <a id="solo"></a>**`solo`** | 1 | 4096MB / 4c / 25G · `.180` | 4.0GB | 25G | CKAD drilling, Helm authoring, build-track deploy target |
| <a id="pair"></a>**`pair`** | 2 | CP 3072MB / 2c / 25G · `.130`<br>worker 2048MB / 2c / 20G · `.131` | 5.0GB<br>[**5.1GB measured**](#measured) | 45G | The daily driver, and **every DaemonSet-heavy module** |
| <a id="workhorse"></a>**`workhorse`** | 3 | CP 3072MB / 2c / 25G · `.140`<br>2 × worker 2048MB / **1c** / 20G · `.141`–`.142` | 7.0GB | 65G | Scheduling at scale, drain/cordon, chaos |
| <a id="ha"></a>**`ha`** | 3 | 3 × stacked CP 2560MB / 2c / 20G, untainted · `.150`–`.152` | 7.5GB | 60G | Quorum loss, etcd member failure, upgrades |
| <a id="etcd-only"></a>**`etcd-only`** | 3 | 3 × 1024MB / 1c / 10G, **no Kubernetes** · `.160`–`.162` | 3.0GB | 30G | Raft, watch, MVCC, compaction, defrag, backup |
| <a id="bare"></a>**`bare`** | 1 | 2048MB / 2c / 20G, **no Kubernetes, no container runtime** · `.192` | 2.0GB | 20G | [P0](../phases/00-linux-primitives.md) — namespaces, cgroups, veth and `pivot_root` by hand |
| <a id="k0s-light"></a>**`k0s-light`** | 1 | 2048MB / 2c / 20G, single binary · `.170` | 2.0GB | 20G | Distro contrast |
| <a id="nested"></a>**`nested`** | 1 | 6144MB / 4c / 40G, kind/k3d inside · `.190` | 6.0GB | 40G | Multi-cluster escape hatch |
| <a id="platform"></a>**`platform`** | 1 | 6144MB / 4c / 40G, real kubeadm, untainted · `.191` | 6.0GB | 40G | P12 ([#14](https://github.com/k3ii/k8s-academy/issues/14)) |

**`bare` is the only topology that is not a cluster.** It has no kubeadm, no k0s and no
containerd. It carries [the Ansible baseline](#provision) and nothing more. The reason
is the subject of P0. P0 teaches what a container is *before* a runtime exists to make
one. `bare` is also the cheapest item in the curriculum. It uses 2.0GB of a 9.5GB
budget. P0 can therefore fork-bomb it, fill it and OOM it, and you do not need to do
any arithmetic first.

**`nested` and `platform` have the same shape, but they are not the same topology.**
`nested` runs kind inside a VM. `platform` is a real single-node kubeadm cluster.
`nested` is a place to run several throwaway clusters. `platform` is the machine that
you build a platform on.

**The topologies come from three issues.** Seven come from
[#8](https://github.com/k3ii/k8s-academy/issues/8). `platform` comes from
[#14](https://github.com/k3ii/k8s-academy/issues/14). `bare` comes from
[#34](https://github.com/k3ii/k8s-academy/issues/34). Note one detail of the history:
#14 proposed `platform` as an addition, and nobody edited the resolution of #8. The repo
therefore mis-cited the count in two places until this document corrected it.

**`bare` was added for a specific reason.** The author generated the P0 exercises and
found that the exercises had no topology to name. `solo` and `k0s-light` both install a
cluster, and P0 exists to work without a cluster. [`forge`](#build-guest) was also not
an option. P0 would fork-bomb it, fill its disk and `pivot_root` it, and eleven other
phases depend on that one guest.

**Each `workhorse` worker gets 1 core, and not 2.** This is deliberate. The third node
exists so that the scheduler has somewhere to choose *between*. Six vCPU on a six-core
host is already oversubscribed.

<a id="measured"></a>
## One row is measured: `pair` costs 5.1GB, and the row says 5.0GB

**The author provisioned `pair` on `factory` and weighed it on 2026-08-31**
([#50](https://github.com/k3ii/k8s-academy/issues/50)). The other eight rows are still
arithmetic.

**Read the figures below as host-side figures.** Each figure is the `VmRSS` value from
`/proc/<pid>/status` for the `kvm` process of one guest. It is what the host pays for
the guest. It is not what the guest reports about itself.

| Stage | `pair-cp` | `pair-w1` | Host total | Against the 5.0GB row |
|---|---|---|---|---|
| Fresh boot, cloud-init done | 966MB | 954MB | 1920MB | 38% |
| After [the Ansible baseline](#provision) | 1237MB | 1251MB | 2488MB | 49% |
| containerd and the v1.35 packages, **no cluster** | 1912MB | 1881MB | 3793MB | 74% |
| **At rest** — both nodes `Ready`, 10 pods, idle | 2966MB | 2041MB | **5007MB** | **98%** |
| **Under load** — 18 pods, 3 PVCs bound | 3106MB | 2079MB | **5185MB** | **101%** |

**The 5.0GB figure is correct to within 1.3%. It is correct for a reason that the
arithmetic never states.** The figure is not a forecast of demand that happened to be
right. Both guests fill their configured allocation and then stay there. `pair-cp` holds
3106MB of its 3072MB. `pair-w1` holds 2079MB of its 2048MB. The row predicts
*allocation*. There is [no balloon to hand a page back](#ceiling). Allocation is
therefore what a worked guest eventually costs. Most of what the guests hold is page
cache. At the end of the test, 2.0GB of the 3.0GB in `pair-cp` was page cache, and only
118MB of MemFree was left.

**The error goes upward, by approximately 32MB per guest.** A saturated guest costs its
configured size *plus* the process overhead of QEMU. That overhead was 34MB for
`pair-cp` and 31MB for `pair-w1`. Every row in the table above omits this term. Every
row is therefore low. The error is 0.6% for `pair`. In absolute terms, it is three times
as large for the three-node topologies. The ceiling of approximately 9.5GB absorbs the
error. A footprint that you compute to the last 100MB does not.

**Installing the cluster costs as much as running it.** containerd and the v1.35
packages alone took the topology to 74% of its row, and nothing was scheduled yet. Host
RSS grew by 675MB on `pair-cp` and by 630MB on `pair-w1`. That memory never comes back,
because the page cache of apt holds touched pages like any other cache. Learn from this:
an exercise that budgets from "cluster idle" has already spent three quarters of the row
before it starts.

**Neither guest swapped, and neither guest was OOM-killed.** The workload had the shape
of P8. It ran a local-path provisioner, the external snapshotter,
`csi-driver-host-path`, and three writer pods on 1Gi PVCs. The headroom that the row
claims does therefore exist. That headroom is approximately 1% of the row. The kernel
holds it in page cache, and the kernel drops that cache before it kills anything.

**The measurement runs in one direction only.** RSS never retreats. You cannot read *at
rest* again after you read *under load* on the same guest. The order of the rows above
is the only order in which you can take them. To measure again, you must destroy the
topology and start over. Two of the ten at-rest pods were `coredns` replicas that were
still pending because of [#76](https://github.com/k3ii/k8s-academy/issues/76). That is
why this document does not re-take that row.

<a id="addresses"></a>
## Addresses

The subnet is `10.10.10.0/24`, and the gateway is `.1`. The convention in `factory` is
simple: **the `vm_id` is the last octet**.

| Range | Use |
|---|---|
| `.110`–`.129` | Persistent infrastructure — `hopper` `110`, `carthage` `120`, [`forge`](#build-guest) `125`; `111` freed when `jeremie` went |
| `.130`–`.199` | Lab topologies, one block of ten each — see the table above. **`.190`–`.199` is the single-node block**, and holds `nested`, `platform` and `bare` rather than one topology's ten |
| `.200`–`.250` | MetalLB, [reserved by prose only](#unverified) |

**Blocks of ten cost nothing and keep the nodes of each topology contiguous.** That
property matters because a hundred exercises cite these nodes by address.

**Three addresses are refused at plan time.** `9000` is the template, and a validation
in `tofu/vms` refuses `110` and `120`. The same guard should also exist in `tofu/labs`.

<a id="provision"></a>
## Provisioning

Provisioning has five steps. **You run none of them on the Mac.**

```sh
ssh hopper                                    # 1. required. See below.
cd factory && git pull
just tofu labs apply -var 'topology=pair'     # 2. bring the topology up
just gate <node>                              # 3. wait for boot and cloud-init
just play                                     # 4. Ansible baseline
ssh zain@10.10.10.130                         # 5. from the Mac. Do not use -J.
```

**Step 1 — `ssh hopper` is not a convenience.** Every `factory` recipe that touches
Proxmox, OpenTofu or Ansible calls `factory_require_hopper`. That function refuses to
run on macOS *in code*. It prints this message: *"Those run on hopper. This machine
writes code and pushes git."* An exercise that omits this line does not run. It exits
with a non-zero status before it provisions anything.

**Step 2 — the `topology` variable is the contract.** `tofu/labs` takes a topology name.
It expands the name to a preset node map. You do not hand-edit a fleet definition. The
state key of the module is **`labs/terraform.tfstate`**, and that key is separate from
`vms/`. This separation is the load-bearing part of the design. It is what makes
[teardown](#teardown) structurally unable to touch a persistent guest. Note also that
`just tofu <dir> <cmd>` was already generic in `factory`. `just tofu labs …` therefore
cost nothing when the module landed.

**Step 3 — the boot wait is real, and P8 never mentioned it.** `tofu apply` returns when
the *clone* completes, after approximately 9 seconds. The guest must still boot. An
immediate SSH attempt returns `No route to host`. `just gate <vm>` polls SSH for up to
240s. It then waits on `cloud-init status`.

**Step 4 — the Ansible baseline is also real.** `just play` runs `site.yml` and applies
the `common` role. A node that skipped this step is not the node that the exercises
assume. A node that had this step is [still not a node with Kubernetes on
it](#node-baseline), and that is by design.

**[UNVERIFIED]** — `ansible/inventory/hosts.yml` is static today, and somebody maintains
it by hand. Ephemeral lab nodes break exactly that pattern. The contract is different:
**lab nodes must reach Ansible through a dynamic inventory that is generated from the
`tofu` output**. You must not hand-edit a file for each topology.

**Step 5 — the guest account is `zain`, and you need no jump flag.** cloud-init creates
that one account. There is no `debian` user. `factory` commits `Host 10.10.10.*` →
`ProxyJump factory` in its `ssh/config`. `-J factory` is therefore redundant from the
Mac. It is also wrong from `hopper`, because `hopper` is already in the subnet.
`factory` deleted those flags from its own outputs deliberately.

<a id="node-baseline"></a>
## The Kubernetes install belongs to the learner, and not to `factory`

**[#77](https://github.com/k3ii/k8s-academy/issues/77) settled this question.
`factory` delivers a configured Debian guest. The exercises put Kubernetes on it.**

The Ansible roles in `factory` are `common`, `control`, `carthage` and `zeko_*`. None of
them installs a container runtime, and none installs `kubeadm`. A check on a freshly
baselined `pair-cp` on 2026-08-31 found that `kubeadm`, `kubelet`, `kubectl`,
`containerd` and `crictl` were all absent. That is the intended shape. It is not a gap.

**The alternative was rejected, for two reasons.** The alternative was a `kubernetes`
role in `factory`, keyed on the `role` field that [the labs state already
publishes](#provision). The first reason is the title of
[`labs/01/01`](../labs/01/01-provision-and-kubeadm-init.md). That exercise is called *"A
two-node cluster, stood up by hand"*. A runtime that somebody else installs takes a
piece of that exercise away. The second reason is
[P0](../phases/00-linux-primitives.md). P0 spends three weeks arriving at what a
container is, before a runtime exists to make one. If a learner then arrives in P1 on a
node that already has containerd, those three weeks are wasted.

**This document does not pin the Kubernetes version.**
[`certs.md`](certs.md#tooling) holds the version once. The exams track the newest
Kubernetes minor version, which is v1.35 today. The lab clusters follow the same rule,
and not a frozen version. Read the minor version from `certs.md`, call it `$V`, and use
it in the two lines below that name it.

<a id="node-baseline-steps"></a>
### The procedure, stated once

Three exercises stand up a cluster from nothing:

- [`labs/01/01`](../labs/01/01-provision-and-kubeadm-init.md)
- [`labs/03/18`](../labs/03/18-the-webhook-the-apiserver-dials.md)
- [`labs/04/03`](../labs/04/03-sample-controller-against-a-real-cluster.md)

The first exercise walks through these commands and comments on them, because that is
its subject. The other two exercises run the commands and move on.

**Run all of these commands on every node of the topology.** This includes the control
plane and the workers. Step 5 is the one exception, and it belongs to the control plane
alone.

```sh
V=<the current Kubernetes minor, per certs.md#tooling>   # 0. deliberately not pasteable

sudo swapoff -a                                  # 1. the kubelet refuses to start with swap on
sudo sed -i '/\sswap\s/s/^/#/' /etc/fstab        #    and again after the next reboot

printf 'overlay\nbr_netfilter\n' | sudo tee /etc/modules-load.d/k8s.conf
sudo modprobe overlay && sudo modprobe br_netfilter
printf 'net.bridge.bridge-nf-call-iptables=1\nnet.bridge.bridge-nf-call-ip6tables=1\nnet.ipv4.ip_forward=1\n' \
  | sudo tee /etc/sysctl.d/99-k8s.conf
sudo sysctl --system                             # 2. bridged traffic must reach iptables

CD=2.2.1; RUNC=1.5.1                             # 3. upstream, and not apt. See below.

curl -fsSLO "https://github.com/containerd/containerd/releases/download/v$CD/containerd-$CD-linux-amd64.tar.gz"
curl -fsSLO "https://github.com/containerd/containerd/releases/download/v$CD/containerd-$CD-linux-amd64.tar.gz.sha256sum"
sha256sum -c "containerd-$CD-linux-amd64.tar.gz.sha256sum"
sudo tar Cxzf /usr/local "containerd-$CD-linux-amd64.tar.gz"
sudo curl -fsSL -o /etc/systemd/system/containerd.service \
  "https://raw.githubusercontent.com/containerd/containerd/v$CD/containerd.service"

curl -fsSLo runc.amd64 "https://github.com/opencontainers/runc/releases/download/v$RUNC/runc.amd64"
curl -fsSL "https://github.com/opencontainers/runc/releases/download/v$RUNC/runc.sha256sum" \
  | grep ' runc.amd64$' | sha256sum -c -
sudo install -m 755 runc.amd64 /usr/local/sbin/runc

sudo mkdir -p /etc/containerd
/usr/local/bin/containerd config default | sudo tee /etc/containerd/config.toml >/dev/null
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo systemctl daemon-reload
sudo systemctl enable --now containerd           # see the one edit below

sudo mkdir -p /etc/apt/keyrings
curl -fsSL "https://pkgs.k8s.io/core:/stable:/$V/deb/Release.key" \
  | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/$V/deb/ /" \
  | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update && sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl       # 4. apt must not move a cluster's minor

sudo kubeadm config images pull                  # 5. control plane only. Silence, spent up front.
```

**Debian's `containerd` package cannot run Kubernetes 1.37, which is why step 3 takes
the upstream tarball.** Trixie ships containerd `1.7.24`. Since
[KEP-4033](https://git.k8s.io/enhancements/keps/sig-node/4033-group-driver-detection-over-cri)
went GA, `kubeadm` asks the runtime for its cgroup driver over the CRI `RuntimeConfig`
RPC, and containerd 1.7 does not answer:

```
E0902 21:43:34.028287 ... "RuntimeConfig from runtime service failed" err="rpc error: code = Unimplemented desc = method RuntimeConfig not implemented"
        [WARNING ContainerRuntimeVersion]: You must update your container runtime to a version that supports the CRI method RuntimeConfig.
```

**That warning is not survivable for long, and the wait does not help.** `kubeadm` falls
back to reading `cgroupDriver` from the kubelet config, and the fallback is removed in
1.38. containerd 1.7 will never gain the RPC either. The backport,
[containerd#11346](https://github.com/containerd/containerd/pull/11346), was closed
unmerged in April 2025, and its author's parting note reads: "When the feature is GA'd
containerd v1.7 becomes incompatible with kubernetes. The kubelet refuses to start." So
`apt-get install -y containerd` is a dead end. The author walked into it on 2026-09-02,
on an already-baselined `pair-cp`.

**containerd 2.x drags `runc` along with it.** [containerd 2.0 requires runc
1.2.0](https://github.com/containerd/containerd/blob/main/docs/containerd-2.0.md) or
later, and trixie ships `1.1.15`. Step 3 therefore installs a runc binary to
`/usr/local/sbin`, which the default systemd `PATH` reaches before `/usr/sbin`.

**Step 3 pins two versions, and `$V` stays unpinned.** The reason is the checksum. A
tarball fetched by hand is worth verifying, and a sum cannot be verified against a
version that floats. Bump both deliberately, and re-read the sums when you do.

**One `sed` line against `config.toml` is load-bearing, and it is the cgroup driver.**
`SystemdCgroup = true` matches the driver that the kubelet uses on a systemd host. If
you leave the value as `false`, the two components disagree about who owns the cgroup
tree. The kubelet then reports the node as `NotReady`, and it says why in its own log.
That is the recoverable kind of failure.

**The `bin_dir` edit is gone, and nothing replaces it**
([#76](https://github.com/k3ii/k8s-academy/issues/76)). That edit existed because two
defaults disagreed, and not because anything was missing. Debian's `containerd` patched
`bin_dir` to `/usr/lib/cni`. The plugins were in `/opt/cni/bin` the whole time, put
there by `kubernetes-cni`, which `kubelet` depends on and which step 4 therefore
installs without being asked. containerd was looking in the wrong one of two
directories. Upstream containerd defaults to the directory `kubernetes-cni` uses, and at
config schema `version = 3` the field is a list reading `bin_dirs = ['/opt/cni/bin']`.
The two halves agree on their own, so there is nothing left to `sed`.

**The failure mode outlives the edit, and it is worth keeping in view.** containerd looks
in a directory. The conflist names a plugin type that is not in it. Sandbox creation
fails, pods sit in `ContainerCreating`, `SandboxChanged` repeats, and nothing names the
directory. The node reaches `Ready` before any of this, so its own success signal fires
and then no pod ever starts. The author met this the hard way while [weighing
`pair`](#measured), and it cost ten minutes of a cluster that had already told him it
was fine. Any future disagreement about that path — a plugin installed by hand, a
`bin_dirs` someone tidied — arrives dressed in exactly these clothes.

**Flannel is not what fills `/opt/cni/bin`, and the strand used to imply otherwise.**
Flannel's DaemonSet drops `/opt/cni/bin/flannel` and a conflist. That conflist delegates
to `bridge` and chains `portmap`, and those two pull in `host-local` and `loopback`.
Flannel ships none of the four. `kubernetes-cni` does, and a check on `pair-wk` on
2026-09-02 found version `1.9.1-1.1` of it owning `/opt/cni/bin/bridge`. This is also
why step 3 does not install the CNI plugins itself: step 4 already has.

**The curriculum assumes `/opt/cni/bin` throughout, and `kubernetes-cni` fills it.**
[`labs/07`](../labs/07/) installs a hand-written plugin in that directory.
[`labs/11/06`](../labs/11/06-11c4-kill-one-trace-component-mid-flight.md) breaks the
datapath by moving `/opt/cni/bin/bridge` aside. That break needs `bridge` to be there
first.

**Step 5 pulls the images, and it is not an optimisation.** It runs on the control plane
only, because a worker needs `kube-proxy` and `pause` and `kubeadm join` fetches those
two by itself. `kubeadm init` prints nothing between "This might take a minute or two"
and the `[certs]` phase, for however long the pull runs. On `pair` on 2026-09-02 that
was `kube-apiserver` in 28 seconds and `kube-controller-manager` in twelve minutes, on
the same link, because the CDN edge had collapsed to 40 KB/s in between. containerd logs
a pull only when it completes, so nothing anywhere moves for minutes at a stretch. Piped
into `tee`, that is indistinguishable from a hang, and the temptation is to `Ctrl-C` a
tool that is working. `kubeadm config images pull` spends the same minutes and names each
image as it lands.

**`etcd-only`, `k0s-light` and `bare` want none of this procedure.** Each one installs
what it needs, or needs nothing on purpose:

- `etcd-only` takes three etcd binaries, copied out from [`forge`](#build-guest).
- `k0s-light` runs `get.k0s.sh`, for a distribution that ships its own runtime.
- [`bare`](#bare) installs nothing. The whole point is that no runtime exists.

<a id="teardown"></a>
## Teardown

```sh
ssh hopper
just tofu labs destroy       # never `just destroy-vms` — that one is hardcoded to tofu/vms
```

**`just destroy-vms` is the wrong verb, and it always will be.** It is hardcoded to
`tofu/vms`, which is the persistent fleet. Keeping the labs in [their own state
key](#provision) is what makes the two commands impossible to confuse.

**Somebody has tested the separate state key. It is not only asserted.** The author ran
`just tofu labs destroy` against a live `pair` on 2026-08-31
([#50](https://github.com/k3ii/k8s-academy/issues/50)). It reported `2 destroyed`.
`hopper`, `carthage` and [`forge`](#build-guest) came through the teardown as the same
processes as before. They kept the same PIDs, and their uptimes ran on unbroken. `forge`
is the guest that matters most here, because eleven phases depend on it.

**Teardown has two layers, and different issues rule them at different scopes**
([#8](https://github.com/k3ii/k8s-academy/issues/8),
[#35](https://github.com/k3ii/k8s-academy/issues/35)).

**The first layer is the *guest* layer. #8 settled it, and it is coarse:**

> Every phase starts from a clean provision — no long-lived clusters accreting across
> phases. Because both RAM and disk are one-topology-at-a-time, teardown is not hygiene
> but a hard precondition for the next phase booting at all.

Three guest-layer scopes are settled. All three are coarser than one exercise:

- Per **phase**.
- Per **lab group** within a phase. P12 runs two groups, with a teardown between them.
- *Everything else down* for a **big rock**, such as a service mesh.

**Consecutive exercises may share a live cluster. That is the intended pattern, and not
a shortcut.** A provision, a gate and a baseline cost minutes of wall-clock time before
any teaching happens. The line about the guest in an exercise is therefore usually a
**continuity marker**, such as *"leave it up, 8.3 continues on it"*. A real `just tofu
labs destroy` appears where the exercise ends a phase, ends a group, or installs a big
rock.

**The second layer is finer, and it always runs: each exercise deletes what it
created.** This includes its namespace, its CRs, its `iptables` rules and its loop
devices. The exercise deletes them before the next exercise starts.

Learn from the mistake here. Somebody read #8 as *no teardown at all between exercises*
while the storage phase was being drafted. That reading survived until objects left
behind by one exercise started to answer the next exercise's question for it. A cluster
that eleven exercises have used is not the cluster that the twelfth was written against.
The teardown step of an exercise therefore does two things. It runs the fine layer
unconditionally. It then names the coarse layer: the topology **stays**, or it **goes**.

**Disk needs eviction too, and that is a build-track fact.** `go clean -modcache` and
`docker system prune` belong in the same runbook. See
[`build-mechanics#p5-split`](build-mechanics.md#p5-split), where `workhorse` plus
`forge` is 90G of 95G.

<a id="access"></a>
## How to reach a cluster from the Mac

The subnet is NAT'd. You can reach it only through the `factory` bastion. Egress uses
MASQUERADE. Nothing reaches the guests unsolicited.

**Services get a real address. MetalLB runs in L2 mode on `.200`–`.250`.** The choice
was pedagogical. `kubectl port-forward` bypasses the Service and LoadBalancer datapath
completely. It hides the mechanics that this curriculum exists to teach. L2 mode instead
makes one question concrete through ARP: *"how does a LoadBalancer get an IP?"* The
bridge `vmbr0` is `10.10.10.1/24` with `bridge-ports none`. It therefore has no physical
port, no competing DHCP and no other L2 speakers. Those conditions are close to ideal
for L2 mode.

**`kubectl port-forward` stays sanctioned where access is incidental rather than the
lesson.** That describes most exercises. Use it without ceremony. The rule above governs
what an exercise *teaches*. It does not govern every time that you need a dashboard.

To open a VIP in a browser on the Mac, run this command:

```sh
ssh -L 8080:10.10.10.200:80 factory     # then http://localhost:8080
```

**[UNVERIFIED]** — one `-L` forward per VIP is the convention of this document. It is
not an inherited decision. #8 settled MetalLB and the SSH proxy, but #8 never wrote the
literal command. This document prefers `-L` over a `-D` SOCKS proxy for two reasons. It
needs no browser configuration. It also leaves no proxy setting for you to forget
afterwards.

<a id="build-guest"></a>
## `forge` is not part of any topology

The build guest is always up. It is sized independently. **You subtract it from the
ceiling before you choose a topology.** It is co-resident with whatever runs. It is never
a node in a topology. It holds the Go module cache and the registry for one precise
reason: a teardown must not cost them.

That is the whole relationship of `forge` to this document. The rest of its detail
lives in [`build-mechanics#forge`](build-mechanics.md#forge). That document holds four
subjects:

- Why `forge` gets 1536MB, and not 2048MB.
- The 2560MB resize that P3 and P5 each take and then give back.
- The kernel lockstep with the lab nodes.
- The registry.

<a id="unverified"></a>
## What is not confirmed

The provenance rule for the strands is that the status of a fact travels with the fact.
The facts below have no verified source. Do not write an exercise as though these facts
were settled.

1. **One row of the table is measured. The other eight rows are not.** The author stood
   `pair` up and weighed it on 2026-08-31 — [one row is measured](#measured). Every other
   RAM figure is an allocation decision. It is the number that a guest will be *given*.
   It is not a number observed in use. The disk column is unmeasured for all nine rows,
   and that includes `pair`.
2. **This document allocates most per-node addresses. It does not observe them.** Only
   the `.130` and `.131` addresses of `pair` pre-date this document. Only `.110`, `.120`,
   `.125` and `.192` have ever been occupied. `.111` belonged to `jeremie`, and it is now
   free.
3. **How ephemeral nodes enter the Ansible inventory** is specified as dynamic-from-tofu,
   and implemented as neither.
4. **The range `.200`–`.250` is reserved in prose only.** `factory` has no IPAddressPool,
   no MetalLB config, and no comment that claims the range.
5. **The browser-to-VIP command** is chosen in [Reaching a cluster](#access). It is not
   inherited.
6. **The ceiling of approximately 9.5GB is a subtraction, and not an observation.**
   `jeremie` is destroyed, since 2026-08-18, and `forge` is declared. The assumptions
   behind the figure therefore hold now. The host reports 15.49 GiB in total. That leaves
   9.4 GiB after you charge every guest that must stay up at its configured ceiling. But
   note one weakness. One row calls the approximately 1.6GB of the Proxmox host
   *"Measured"*. That row holds the only measured term in a column of allocations. The two
   kinds of number are not the same.
