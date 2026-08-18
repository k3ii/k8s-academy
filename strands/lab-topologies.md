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
## The invocations below are a contract, not a description

**`tofu/labs` does not exist in [`k3ii/factory`](https://github.com/k3ii/factory)
today, and neither do seven of the eight topologies.** Every provision and teardown
command in this document — and therefore in every exercise that links here — is a
specification `factory` is expected to implement, written ahead of the module rather
than after it. Run one today and it fails at the `-chdir`.

This is deliberate ([#49](https://github.com/k3ii/k8s-academy/issues/49)). The
curriculum leads and the homelab follows; the alternative was ~100 exercises citing an
interface built for a different purpose. The consequence is stated **once, here**, and
never repeated per exercise: an exercise's provision block being unrunnable is a known
gap in `factory`, not a mistake in the exercise or in what you typed.

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
| `jeremie` | 1024MB | **Reclaimed** ([#8](https://github.com/k3ii/k8s-academy/issues/8)) — destroyed for the duration of the academy. |
| [`forge`](#build-guest) | 1536MB · 2560MB during P5 | Never torn down, and **not part of any topology**. |
| Host page cache | ~1.0GB | Held back deliberately. |
| **A topology, plus `forge`** | **~9.5GB** | |

**~9.5GB, not the ~9.9GB the host reports as available.** Same budget at two points in
the subtraction: 9.9 is before the page-cache holdback, 9.5 after. A footprint line that
fits in 9.9 and not in 9.5 does not fit. **[UNVERIFIED]** — 9.5GB also assumes
`jeremie` is already destroyed, and at `factory@6f4692f` it is still declared.

**One topology at a time, on RAM *and* disk.** `workhorse` at 65G and `nested` at 40G
will not coexist in 95G even though their RAM would fit — a topology can fail to
provision for disk while the memory arithmetic says yes.

**`balloon 0` on every guest: there is no reclaim.** Every allocated MB is committed.
6.1GB of swap exists and is not a valve — swapped etcd means fsync stalls, missed Raft
heartbeats, and a cluster that looks broken for reasons unrelated to the lesson.
Staying under budget is the whole mechanism.

<a id="topologies"></a>
## The eight topologies

Sizing is an **allocation decision, not a measurement** — see
[what is not confirmed](#unverified). Link to a row, not to the table.

| Topology | Nodes | Per node | RAM | Disk | For |
|---|---|---|---|---|---|
| <a id="solo"></a>**`solo`** | 1 | 4096MB / 4c / 25G · `.180` | 4.0GB | 25G | CKAD drilling, Helm authoring, build-track deploy target |
| <a id="pair"></a>**`pair`** | 2 | CP 3072MB / 2c / 25G · `.130`<br>worker 2048MB / 2c / 20G · `.131` | 5.0GB | 45G | The daily driver, and **every DaemonSet-heavy module** |
| <a id="workhorse"></a>**`workhorse`** | 3 | CP 3072MB / 2c / 25G · `.140`<br>2 × worker 2048MB / **1c** / 20G · `.141`–`.142` | 7.0GB | 65G | Scheduling at scale, drain/cordon, chaos |
| <a id="ha"></a>**`ha`** | 3 | 3 × stacked CP 2560MB / 2c / 20G, untainted · `.150`–`.152` | 7.5GB | 60G | Quorum loss, etcd member failure, upgrades |
| <a id="etcd-only"></a>**`etcd-only`** | 3 | 3 × 1024MB / 1c / 10G, **no Kubernetes** · `.160`–`.162` | 3.0GB | 30G | Raft, watch, MVCC, compaction, defrag, backup |
| <a id="k0s-light"></a>**`k0s-light`** | 1 | 2048MB / 2c / 20G, single binary · `.170` | 2.0GB | 20G | Distro contrast |
| <a id="nested"></a>**`nested`** | 1 | 6144MB / 4c / 40G, kind/k3d inside · `.190` | 6.0GB | 40G | Multi-cluster escape hatch |
| <a id="platform"></a>**`platform`** | 1 | 6144MB / 4c / 40G, real kubeadm, untainted · `.191` | 6.0GB | 40G | P12 ([#14](https://github.com/k3ii/k8s-academy/issues/14)) |

**`nested` and `platform` are the same shape and are not the same topology.**
kind-in-a-VM versus a real single-node kubeadm cluster: the first is a place to run
several throwaway clusters, the second is the thing a platform gets built on.

**The seven come from [#8](https://github.com/k3ii/k8s-academy/issues/8); `platform`
comes from [#14](https://github.com/k3ii/k8s-academy/issues/14).** #14 proposed it as
an addition and #8's resolution was never edited, so the repo mis-cited it in two
places until this document.

**`workhorse`'s workers get 1 core each, not 2.** Deliberate: the third node exists so
the scheduler has somewhere to choose *between*, and six vCPU on a six-core host is
already oversubscribed.

<a id="addresses"></a>
## Addresses

`10.10.10.0/24`, gateway `.1`, and `factory`'s own convention is **`vm_id` = the last
octet**.

| Range | Use |
|---|---|
| `.110`–`.129` | Persistent infrastructure — `hopper` `110`, `jeremie` `111`, `carthage` `120`, [`forge`](#build-guest) `125` |
| `.130`–`.199` | Lab topologies, one block of ten each — see the table above |
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
already generic in `factory`, so `just tofu labs …` costs nothing once the module lands.

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

**Teardown is ruled per *phase*, not per exercise**
([#8](https://github.com/k3ii/k8s-academy/issues/8)):

> Every phase starts from a clean provision — no long-lived clusters accreting across
> phases. Because both RAM and disk are one-topology-at-a-time, teardown is not hygiene
> but a hard precondition for the next phase booting at all.

Three scopes are settled, all coarser than an exercise: per **phase**, per **lab group**
within a phase (P12 runs two, with a teardown between), and *everything else down* for a
**big rock** like a service mesh. Consecutive exercises sharing a live cluster is the
intended pattern, not a shortcut — a provision, gate and baseline is minutes of
wall-clock before any teaching happens. An exercise's teardown line is therefore usually
a **continuity marker** (*"leave it up, 8.3 continues on it"*), with a real teardown
where the exercise ends a phase, ends a group, or installs a big rock.

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
not 2048MB, the 2560MB resize for P5, the kernel lockstep with the lab nodes, and the
registry all live in [`build-mechanics#forge`](build-mechanics.md#forge).

<a id="unverified"></a>
## What is not confirmed

The provenance rule for the strands is that a fact's status travels with it. These are
the ones without a verified source, and an exercise should not be written as though they
were settled:

1. **Nothing here has ever been measured.** No topology has been provisioned on the node.
   Every RAM and disk figure is an allocation decision — the number that will be *given*
   to a guest, not one observed in use. [#50](https://github.com/k3ii/k8s-academy/issues/50)
   brings exactly one topology, `pair`, into scope to be stood up and weighed; until it
   closes, every row of the table is arithmetic.
2. **`tofu/labs`, the `topology` variable, the labs state key and `just tofu labs destroy`
   do not exist** — see [the contract note](#contract).
3. **Per-node addresses are allocated here, not observed.** Only `pair`'s `.130`/`.131`
   pre-dates this document. `.110`, `.111` and `.120` are the only octets actually in use.
4. **How ephemeral nodes enter the Ansible inventory** is specified as dynamic-from-tofu
   and implemented as neither.
5. **`.200`–`.250` is reserved in prose only.** There is no IPAddressPool, no MetalLB
   config and no comment in `factory` claiming the range.
6. **The browser-to-VIP command** is chosen in [Reaching a cluster](#access), not inherited.
7. **~9.5GB assumes `jeremie` is destroyed**, and it is still declared in `factory`'s
   `vms` map — along with `forge`, which is specified everywhere and declared nowhere.
