# Lab topologies

Eight named guest layouts, their per-node sizing and addresses, how one is provisioned
and torn down, and how you reach a cluster running inside the bastion. An exercise
names **one topology** and links here; it never restates a footprint.

Derived from [`../research/lab-topologies.md`](../research/lab-topologies.md), research
date 2026-08-18, verified against `k3ii/factory@6f4692f` — which carries the full
audit of what `factory` actually contains, and the seven sizing decisions quoted from
[#8](https://github.com/k3ii/k8s-academy/issues/8) and the eighth from
[#14](https://github.com/k3ii/k8s-academy/issues/14). Facts that could not be confirmed
against a real tree or a real measurement are marked **[UNVERIFIED]** inline and
collected under [What is not confirmed](#unverified).

<a id="contract"></a>
## The invocations below were a contract before they were a description

**`tofu/labs` landed in [`k3ii/factory`](https://github.com/k3ii/factory) on 2026-08-30
(`266dac0`), with all nine topologies declared.** Every provision and teardown command in
this document was written before the module existed — a specification `factory` was
expected to implement, not a description of something already built. `factory` has since
implemented it, and the commands here match what the module exposes.

This was deliberate ([#49](https://github.com/k3ii/k8s-academy/issues/49)). The
curriculum leads and the homelab follows; the alternative was ~100 exercises citing an
interface built for a different purpose.

**The exercises no longer point here for that.** Five lab files carried a *"what does
not exist yet"* pointer to this section; [#75](https://github.com/k3ii/k8s-academy/issues/75)
retired it, because a provision block that fails today is a bug worth reporting rather
than the gap in `factory` it used to be. What is still missing is
[on the node itself](#provision), not in `factory`. This section keeps the history of why
the interface was written first.

`phases/08-storage.md` shipped one such block before this document existed. It was not
fiction — it was this same specification, written as though it were built.

<a id="ceiling"></a>
## The ceiling — ~9.5GB spendable

The node is an i5-8400T: 6 cores, and after everything that must stay up, **~9.5GB of
RAM and 95G of disk** to spend on a topology.

| Holds RAM | Amount | Status |
|---|---|---|
| The Proxmox host | ~1.6GB | Measured. |
| `hopper` | 2048MB | **Must stay up** — the only machine that runs `tofu` and Ansible. |
| `carthage` | 1024MB | **Must stay up** — holds the OpenTofu state bucket. |
| `jeremie` | 1024MB | **Reclaimed** ([#8](https://github.com/k3ii/k8s-academy/issues/8)) — destroyed 2026-08-18, for the duration of the academy. |
| [`forge`](#build-guest) | 1536MB · 2560MB during P3 and P5 | Never torn down, and **not part of any topology**. |
| Host page cache | ~1.0GB | Held back deliberately. |
| **A topology, plus `forge`** | **~9.5GB** | |

**~9.5GB, not the ~9.9GB the host reports as available.** Same budget at two points in
the subtraction: 9.9 is before the page-cache holdback, 9.5 after. A footprint line that
fits in 9.9 and not in 9.5 does not fit. `jeremie` is destroyed and `forge` is declared,
so the assumptions hold — but the figure is still
[subtraction rather than observation](#unverified).

**One topology at a time, on RAM *and* disk.** `workhorse` at 65G and `nested` at 40G
will not coexist in 95G even though their RAM would fit — a topology can fail to
provision for disk while the memory arithmetic says yes.

**`balloon 0` on every guest: there is no reclaim.** No guest carries a `virtio-balloon`
device, so nothing hands a page back once the guest has touched it — the configured size
is a ceiling each guest walks toward and never retreats from, and that is what makes the
arithmetic safe to budget against. It is *not* a commitment taken at boot: the guests
also run without `prealloc=on`, so KVM backs their RAM lazily and the host pays only for
pages actually touched. Measured on `factory` at 27 hours' uptime, `hopper` cost 937MB of
its 2048MB, `forge` 915MB of 1536MB and `carthage` 879MB of 1024MB. Every row below is
therefore an **upper bound**: a topology that is up is cheaper than its figure until it
has been worked. KSM is off (`/sys/kernel/mm/ksm/run` is `0`), so the multi-node rows get
no page-sharing discount either — sum-of-nodes is the right shape.
6.1GB of swap exists and is not a valve — swapped etcd means fsync stalls, missed Raft
heartbeats, and a cluster that looks broken for reasons unrelated to the lesson.
Staying under budget is the whole mechanism.

<a id="topologies"></a>
## The nine topologies

Sizing is an **allocation decision, not a measurement** for eight of the nine rows.
`pair` [has been weighed](#measured); for the rest, see
[what is not confirmed](#unverified). Link to a row, not to the table.

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

**`bare` is the only topology that is not a cluster.** No kubeadm, no k0s, not even
containerd — [the Ansible baseline](#provision) and nothing else, because P0's entire
subject is what a container is *before* a runtime exists to make one. It is also the
cheapest thing in the curriculum: 2.0GB of a 9.5GB budget, which is why P0 can afford to
fork-bomb it, fill it and OOM it without arithmetic.

**`nested` and `platform` are the same shape and are not the same topology.**
kind-in-a-VM versus a real single-node kubeadm cluster: the first is a place to run
several throwaway clusters, the second is the thing a platform gets built on.

**The seven come from [#8](https://github.com/k3ii/k8s-academy/issues/8), `platform`
from [#14](https://github.com/k3ii/k8s-academy/issues/14), and `bare` from
[#34](https://github.com/k3ii/k8s-academy/issues/34).** #14 proposed `platform` as an
addition and #8's resolution was never edited, so the repo mis-cited it in two places
until this document. `bare` was added when generating P0's exercises found that they had
no topology they could name: `solo` and `k0s-light` both install a cluster P0 exists to
do without, and running P0 on [`forge`](#build-guest) would fork-bomb, disk-fill and
`pivot_root` the one guest eleven other phases depend on.

**`workhorse`'s workers get 1 core each, not 2.** Deliberate: the third node exists so
the scheduler has somewhere to choose *between*, and six vCPU on a six-core host is
already oversubscribed.

<a id="measured"></a>
## One row is measured: `pair` costs 5.1GB, and the row said 5.0

**`pair` was provisioned on `factory` and weighed on 2026-08-31
([#50](https://github.com/k3ii/k8s-academy/issues/50)). The other eight rows are still
arithmetic.** The host-side figures below are per-guest `VmRSS` from `/proc/<pid>/status`
for each `kvm` process — what the host actually pays for a guest, not what the guest
reports about itself.

| Stage | `pair-cp` | `pair-w1` | Host total | Against the 5.0GB row |
|---|---|---|---|---|
| Fresh boot, cloud-init done | 966MB | 954MB | 1920MB | 38% |
| After [the Ansible baseline](#provision) | 1237MB | 1251MB | 2488MB | 49% |
| containerd and the v1.35 packages, **no cluster** | 1912MB | 1881MB | 3793MB | 74% |
| **At rest** — both nodes `Ready`, 10 pods, idle | 2966MB | 2041MB | **5007MB** | **98%** |
| **Under load** — 18 pods, 3 PVCs bound | 3106MB | 2079MB | **5185MB** | **101%** |

**The 5.0GB figure is right to within 1.3%, and it is right for a reason the arithmetic
never states.** It is not a forecast of demand that happened to land: both guests saturate
their configured allocation and stay there, `pair-cp` at 3106MB of 3072 and `pair-w1` at
2079MB of 2048. The row predicts *allocation* — and with [no balloon to hand a page
back](#ceiling), allocation is what a worked guest eventually costs. Most of what the
guests hold is page cache: 2.0GB of `pair-cp`'s 3.0GB at the end, with 118MB of MemFree
left.

**The direction of the error is up, by about 32MB per guest.** A saturated guest costs its
configured size *plus* QEMU's own process overhead — `pair-cp` +34MB, `pair-w1` +31MB.
Every row omits that term, so every row is low: by 0.6% for `pair`, and by three times as
much in absolute terms for the three-node topologies. The ~9.5GB ceiling absorbs it. A
footprint line computed to the last 100MB does not.

**Installing the cluster costs as much as running it.** containerd and the v1.35 packages
alone took the topology to 74% of its row with nothing scheduled: +675MB on `pair-cp` and
+630MB on `pair-w1` of host RSS that never comes back, because apt's page cache is a
touched page like any other. An exercise budgeting from "cluster idle" has already spent
three quarters of the row before it starts.

**Neither guest swapped and neither OOM-killed** under a P8-shaped workload — a local-path
provisioner, the external snapshotter, `csi-driver-host-path` and three writer pods on 1Gi
PVCs. So the headroom the row claims does exist; it is about 1% of the row, held in page
cache the kernel drops before it kills anything.

**The measurement is one-way.** RSS never retreats, so *at rest* cannot be re-read after
*under load* on the same guest: the order of the rows above is the only order they can be
taken in. Re-measuring means destroying the topology and starting over. Two of the ten
at-rest pods were `coredns` replicas still pending on
[#76](https://github.com/k3ii/k8s-academy/issues/76), which is why that row is not
re-taken here.

<a id="addresses"></a>
## Addresses

`10.10.10.0/24`, gateway `.1`, and `factory`'s own convention is **`vm_id` = the last
octet**.

| Range | Use |
|---|---|
| `.110`–`.129` | Persistent infrastructure — `hopper` `110`, `carthage` `120`, [`forge`](#build-guest) `125`; `111` freed when `jeremie` went |
| `.130`–`.199` | Lab topologies, one block of ten each — see the table above. **`.190`–`.199` is the single-node block**, and holds `nested`, `platform` and `bare` rather than one topology's ten |
| `.200`–`.250` | MetalLB, [reserved by prose only](#unverified) |

Blocks of ten waste nothing and keep each topology's nodes contiguous, which matters
when a hundred exercises cite them by address. `9000` is the template and `110`/`120`
are refused at plan time by a validation in `tofu/vms` — the same guard should exist in
`tofu/labs`.

<a id="provision"></a>
## Provisioning

Five steps, and **none of them run on the Mac.**

```sh
ssh hopper                                    # 1. mandatory — see below
cd factory && git pull
just tofu labs apply -var 'topology=pair'     # 2. bring the topology up
just gate <node>                              # 3. wait for boot + cloud-init
just play                                     # 4. Ansible baseline
ssh zain@10.10.10.130                         # 5. from the Mac, no -J
```

**1 — `ssh hopper` is not a convenience.** Every `factory` recipe touching Proxmox,
OpenTofu or Ansible calls `factory_require_hopper`, which refuses to run on macOS *in
code*: *"Those run on hopper. This machine writes code and pushes git."* An exercise
that omits this line does not run; it exits non-zero before anything is provisioned.

**2 — the `topology` variable is the contract.** `tofu/labs` takes a topology name and
expands it to a preset node map, rather than making you hand-edit a fleet definition.
Its state key is **`labs/terraform.tfstate`, separate from `vms/`** — this is the
load-bearing part of the design, because it is what makes [teardown](#teardown)
structurally incapable of touching persistent guests. `just tofu <dir> <cmd>` is
already generic in `factory`, so `just tofu labs …` cost nothing when the module landed.

**3 — the boot wait is real and P8 never mentioned it.** `tofu apply` returns when the
*clone* completes, about 9 seconds in, and the guest still has to boot; an immediate
SSH gets `No route to host`. `just gate <vm>` polls SSH to 240s, then waits on
`cloud-init status`.

**4 — so is the Ansible baseline.** `just play` runs `site.yml`, applying the `common`
role. A node that skipped it is not the node the exercises assume.
**[UNVERIFIED]** — `ansible/inventory/hosts.yml` is static and hand-maintained today,
which is exactly what ephemeral lab nodes break. The contract is that **lab nodes reach
Ansible through a dynamic inventory generated from the `tofu` output**, not by hand-editing
a file per topology.

**5 — the guest account is `zain`, and needs no jump flag.** cloud-init creates that one
account; there is no `debian` user. `factory` commits `Host 10.10.10.*` → `ProxyJump
factory` in its `ssh/config`, so `-J factory` is redundant from the Mac and wrong from
`hopper`, which is already in the subnet. `factory` deleted those flags from its own
outputs deliberately.

<a id="teardown"></a>
## Teardown

```sh
ssh hopper
just tofu labs destroy       # never `just destroy-vms` — that one is hardcoded to tofu/vms
```

**`just destroy-vms` is the wrong verb and always will be.** It is hardcoded to
`tofu/vms`, the persistent fleet. Keeping labs in [their own state
key](#provision) is what makes the two impossible to confuse.

**The separate state key has been tested once, not just asserted.** `just tofu labs
destroy` was run against a live `pair` on 2026-08-31
([#50](https://github.com/k3ii/k8s-academy/issues/50)): it reported `2 destroyed`, and
`hopper`, `carthage` and [`forge`](#build-guest) came through it as the same processes
they were before — same PIDs, uptimes running on unbroken. `forge` is the one that
matters, because eleven phases depend on it.

**Teardown has two layers, ruled at different scopes**
([#8](https://github.com/k3ii/k8s-academy/issues/8),
[#35](https://github.com/k3ii/k8s-academy/issues/35)). The *guest* layer is the one #8
settled, and it is coarse:

> Every phase starts from a clean provision — no long-lived clusters accreting across
> phases. Because both RAM and disk are one-topology-at-a-time, teardown is not hygiene
> but a hard precondition for the next phase booting at all.

Three guest-layer scopes are settled, all coarser than an exercise: per **phase**, per
**lab group** within a phase (P12 runs two, with a teardown between), and *everything
else down* for a **big rock** like a service mesh. Consecutive exercises sharing a live
cluster is the intended pattern, not a shortcut — a provision, gate and baseline is
minutes of wall-clock before any teaching happens. An exercise's line about the guest is
therefore usually a **continuity marker** (*"leave it up, 8.3 continues on it"*), with a
real `just tofu labs destroy` where the exercise ends a phase, ends a group, or installs
a big rock.

The second layer is finer and always runs: **each exercise deletes what it created** —
its namespace, its CRs, its `iptables` rules, its loop devices — before the next one
starts. #8 was read as *no teardown at all between exercises* while the storage phase was
being drafted, and the reading survived until objects left behind by one exercise started
answering the next one's question for it. A cluster that has been used for eleven
exercises is not the cluster the twelfth was written against. So an exercise's teardown
step does the fine layer unconditionally, then names the coarse one: **stays**, or
**goes**.

**Disk needs evicting too, and that is a build-track fact**: `go clean -modcache` and
`docker system prune` belong in the same runbook — see
[`build-mechanics#p5-split`](build-mechanics.md#p5-split), where `workhorse` plus
`forge` is 90G of 95G.

<a id="access"></a>
## Reaching a cluster from the Mac

The subnet is NAT'd and reachable only through the `factory` bastion. Egress is
MASQUERADE; nothing reaches the guests unsolicited.

**Services get a real address: MetalLB in L2 mode on `.200`–`.250`.** Chosen over
`kubectl port-forward` on pedagogical grounds — port-forward bypasses the
Service/LoadBalancer datapath entirely and hides the mechanics this curriculum exists to
teach, while L2 makes *"how does a LoadBalancer get an IP"* concrete via ARP. `vmbr0` is
`10.10.10.1/24` with `bridge-ports none` — no physical port, no competing DHCP, no other
L2 speakers — which is close to ideal for L2 mode.

**`kubectl port-forward` stays sanctioned wherever access is incidental rather than the
lesson**, which is most exercises. Reach for it without ceremony; the rule above is about
what an exercise *teaches*, not about every time you need a dashboard.

To open a VIP in a browser on the Mac:

```sh
ssh -L 8080:10.10.10.200:80 factory     # then http://localhost:8080
```

**[UNVERIFIED]** — a per-VIP `-L` forward is this document's convention, not an inherited
decision; #8 settled MetalLB and the SSH proxy but never wrote the literal command. It is
preferred over a `-D` SOCKS proxy because it needs no browser configuration and leaves no
proxy setting to forget afterwards.

<a id="build-guest"></a>
## `forge` is not part of any topology

The build guest is always up, sized independently, and **subtracted from the ceiling
before a topology is chosen** — it is co-resident with whatever is running, never a node
in it. It holds the Go module cache and the registry precisely so that a teardown does
not cost them.

That is the whole of `forge`'s relationship to this document. Its sizing, why 1536MB and
not 2048MB, the 2560MB resize that P3 and P5 each take and give back, the kernel
lockstep with the lab nodes, and the registry all live in
[`build-mechanics#forge`](build-mechanics.md#forge).

<a id="unverified"></a>
## What is not confirmed

The provenance rule for the strands is that a fact's status travels with it. These are
the ones without a verified source, and an exercise should not be written as though they
were settled:

1. **One row of the table is measured; the other eight are not.** `pair` was stood up and
   weighed on 2026-08-31 — [one row is measured](#measured). Every other RAM figure is an
   allocation decision: the number that will be *given* to a guest, not one observed in
   use. The disk column is unmeasured for all nine, `pair` included.
2. **Per-node addresses are mostly allocated here, not observed.** Only `pair`'s
   `.130`/`.131` pre-dates this document, and only `.110`, `.120`, `.125` and `.192` have
   ever been occupied. `.111` was `jeremie` and is now free.
3. **How ephemeral nodes enter the Ansible inventory** is specified as dynamic-from-tofu
   and implemented as neither.
4. **`.200`–`.250` is reserved in prose only.** There is no IPAddressPool, no MetalLB
   config and no comment in `factory` claiming the range.
5. **The browser-to-VIP command** is chosen in [Reaching a cluster](#access), not inherited.
6. **The ~9.5GB ceiling is subtraction, not observation.** `jeremie` is destroyed
   (2026-08-18) and `forge` is declared, so the assumptions the figure rests on now hold;
   the host reports 15.49 GiB total, which leaves 9.4 GiB once every guest that must stay
   up is charged at its configured ceiling. But the row calling the Proxmox host's ~1.6GB
   *"Measured"* is the only measured term in a column of allocations, and the two are not
   the same kind of number.
