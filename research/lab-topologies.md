# Lab topologies, provisioning and teardown — what is specified, and what is not

Resolves [#31](https://github.com/k3ii/k8s-academy/issues/31). Research date: **2026-08-18**.
Input to [#32](https://github.com/k3ii/k8s-academy/issues/32), which writes
`strands/lab-topologies.md` — this file is the evidence, not the strand doc.

**What was read, and how.**

| Source | Revision | Method |
|---|---|---|
| `k3ii/k8s-academy` | `main` @ `c466b38` | working tree, `grep` across `phases/`, `strands/`, `README.md` |
| `k3ii/factory` | `main` @ `6f4692f28e5a3866d621b8ac75dfcf5b20bda36c` (2026-08-17 11:28 +0400, *"tofu: drop the Mac-only flags from ssh_commands"*) | `gh repo clone k3ii/factory -- --depth=1`, whole tree enumerated, every `tofu/`, `ansible/` and `justfile` file read |
| [#8](https://github.com/k3ii/k8s-academy/issues/8) resolution | single comment, author `k3ii`, unedited | `gh issue view 8 --comments` |
| [#14](https://github.com/k3ii/k8s-academy/issues/14) resolution | single comment | `gh issue view 14 --comments` |

`k3ii/factory` is private and was reachable. `git ls-remote` shows **one branch (`main`) and no
tags**, so there is no unmerged lab work hiding on a side branch.

---

## Headline

Three of the four things the strand doc needs are settled and citable. The fourth — the
provisioning and teardown invocations — **is not written anywhere, in either repo**.

`tofu/labs` does not exist in `k3ii/factory`. No variable named `topology` exists anywhere in
that tree. The command in [`phases/08-storage.md:67`](../phases/08-storage.md) is the only
occurrence in either repository, and it is a **plausible sketch of an unwritten module**, not a
verified invocation. Two of its four lines are also wrong against conventions `factory` already
enforces.

That is the finding, and it is not a blocker: [#29](https://github.com/k3ii/k8s-academy/issues/29)
already places *writing* `tofu/labs` out of scope. What it changes is the register the strand doc
must use — **specified** for sizing, **proposed** for invocations.

---

## 1. The topologies, at per-node resolution

Seven come from #8's resolution. The eighth, `platform`, comes from
**[#14](https://github.com/k3ii/k8s-academy/issues/14)**, not #8 — see the provenance note below.

| Topology | Nodes | Per node | Total RAM | Total disk | Purpose (as stated) |
|---|---|---|---|---|---|
| **solo** | 1 | 4096MB / 4c / 25G | 4.0GB | 25G | CKAD drilling, Helm authoring, build-track deploy target |
| **pair** | 2 | CP 3072MB / 2c / 25G · worker 2048MB / 2c / 20G | 5.0GB | 45G | Daily driver; **and all DaemonSet-heavy modules** |
| **workhorse** | 3 | CP 3072MB / 2c / 25G · 2 × worker 2048MB / 1c / 20G | 7.0GB | 65G | Scheduling, DaemonSets, drain/cordon, chaos drills |
| **ha** | 3 | 3 × stacked CP 2560MB / 2c / 20G, **untainted** | 7.5GB | 60G | Quorum loss, etcd member failure, upgrade drills |
| **etcd-only** | 3 | 3 × 1024MB / 1c / 10G, **no Kubernetes at all** | 3.0GB | 30G | Raft, watch, MVCC, compaction, defrag, backup/restore |
| **k0s-light** | 1 | 2048MB / 2c / 20G, single binary | 2.0GB | 20G | Distro contrast — feel the weight difference |
| **nested** | 1 | 6144MB / 4c / 40G, runs kind/k3d inside | 6.0GB | 40G | Multi-cluster escape hatch |
| **platform** | 1 | 6144MB / 4c / 40G, real kubeadm, CP **untainted** | 6.0GB | 40G | P12 — GitOps, platform APIs, multi-tenancy, progressive delivery |

Every RAM and disk figure above is quoted, not derived. The `workhorse` worker asymmetry (1 core,
not 2) is as written in #8 and is easy to lose in a retype.

**`nested` and `platform` are the same shape and are not the same topology.** #14 says so
explicitly: one runs kind nodes as containers inside the VM, the other is a real single-node
kubeadm cluster. A strand doc that folds them into one row loses a distinction #14 paid for.

**Provenance of `platform`, which the repo currently mis-cites.** #8's table has seven rows and
`platform` is not one of them; #14 proposed it as an *addition* to that table
(*"Add a topology to #8's table"*), and #8's resolution comment was never edited. Both
[`phases/12-gitops-platform.md:14`](../phases/12-gitops-platform.md) and
[`strands/build-mechanics.md:86`](../strands/build-mechanics.md) attribute it to #8. The strand
doc should cite **#14** for `platform` and #8 for the other seven, and that correction is worth
making explicitly rather than silently.

### One at a time — a disk constraint as well as a RAM one

#8: *"One topology at a time — this is a RAM **and** disk constraint."* Concretely, `workhorse`
(65G) and `nested` (40G) cannot coexist inside 95G. Two topologies whose RAM would fit can still
fail to provision.

### What runs alongside, on the same node

| Guest | RAM | Status |
|---|---|---|
| Proxmox host itself | ~1.6GB | measured (`free` showed 5.6GB used with 4GB of guests up) |
| `hopper` | 2048MB | **mandatory, must stay up** — it is the only machine that runs `tofu` and Ansible |
| `carthage` | 1024MB | **mandatory, must stay up** — holds the OpenTofu state bucket |
| `jeremie` | 1024MB | **reclaimed** by #8 decision 1 — destroyed for the duration of the academy |
| `forge` | 1536MB, 2560MB during P5's build modules | never torn down ([`build-mechanics#forge`](../strands/build-mechanics.md#forge)) |
| held back for host page cache | ~1.0GB | |
| **spendable on lab VMs** | **~9.5GB** | |

Disk: `/dev/sda1` is 111G with **95G available**; VM images live on that same root filesystem and
existing guests consume ~26G of it.

**`balloon 0` is set on all guests, so there is no memory reclaim** — every allocated MB is
committed. 6.1GB of swap exists and #8 rules it out as a safety net: swapped etcd means fsync
stalls, missed Raft heartbeats, and a cluster that looks broken for reasons unrelated to the
lesson.

### 9.9GB or 9.5GB — the strand doc has to pick, and it should pick 9.5

`README.md` and #8's *question* both say **~9.9GB**; #8's *resolution*, after subtracting the
~1.0GB held back for page cache, says **~9.5GB spendable**, and `build-mechanics#forge` does all
of its margin arithmetic against 9.5. These are the same budget at two points in the subtraction,
not a contradiction, but a per-exercise footprint line that says "fits in 9.9GB" is measuring
against the wrong number. **9.5GB is the spendable figure.**

Note also that 9.5GB **already assumes `jeremie` is gone** — see §6.

---

## 2. Provisioning: the P8 invocation against what `factory` actually contains

[`phases/08-storage.md:66–69`](../phases/08-storage.md) states, in full:

```
cd tofu/labs && tofu apply -var 'topology=pair'
ssh -J factory debian@10.10.10.130
```

Line by line, against `k3ii/factory` @ `6f4692f`:

| Claim | Verdict | What the tree actually has |
|---|---|---|
| a `tofu/labs` root module exists | **False** | The only root module is `tofu/vms/`; the only other `tofu/` directory is `tofu/modules/vm/` (a reusable single-guest module). No branch, no tag, no stub. |
| `-var 'topology=…'` | **False** | `tofu/vms/variables.tf` declares `node_name`, `datastore_id`, `template_vm_id`, `bootstrap_vm_ids`, `gateway`, `dns_servers`, `dns_domain`, `admin_username`, `ssh_public_key_paths`, `vms`. Nothing named `topology` exists in the repo. |
| `cd tofu/labs && tofu apply` | **Against the repo's own idiom** | Two ways. See below. |
| `ssh -J factory debian@…` | **Wrong user, redundant flag** | See below. |
| an Ansible step follows `apply` | **Omitted, and there is one** | See below. |

**`cd` is not how this repo runs OpenTofu.** The `justfile` has a generic recipe

```just
tofu dir cmd *args:
    tofu -chdir=tofu/{{ dir }} {{ cmd }} "$@"
```

so the idiomatic form is `just tofu vms apply`, from the repository root, never a `cd`.

**And it cannot be run from the Mac at all.** Every recipe touching Proxmox, OpenTofu or Ansible
calls `factory_require_hopper` (`scripts/env.sh`), which refuses on macOS with:

```
refusing: 'just tofu vms apply' reaches Proxmox, OpenTofu or Ansible.
          Those run on hopper. This machine writes code and pushes git.
```

`factory`'s README states the same as a design decision: *"Mac … does not run `tofu` or
`ansible`."* A lab-provisioning step therefore begins `ssh hopper`, and the strand doc must say
so — it is the single most load-bearing correction in this file, because ~100 exercises would
otherwise open with a command that exits non-zero on the machine the learner is sitting at.
(`FACTORY_ALLOW_MAC=1` overrides it; the guard's own comment calls that recovery-only.)

**The SSH line is wrong twice.** `tofu/vms/variables.tf` sets `admin_username` default **`zain`**,
and cloud-init creates exactly that one account with no password — there is no `debian` user.
And `-J factory` is redundant from the Mac, because the committed `ssh/config` already carries

```
Host 10.10.10.*
  User zain
  ProxyJump factory
```

and it is *wrong* from `hopper`, which is already inside `10.10.10.0/24`. `tofu/vms/outputs.tf`
emits the deliberately flagless `ssh zain@10.10.10.x` and explains why at length; the HEAD commit
of the whole repo is *"tofu: drop the Mac-only flags from `ssh_commands`"*. **P8's line is the
exact form `factory` removed the day before this research ran.**

**There is a step between `apply` and `ssh`, and it is not optional.** From `just gate`'s own
comment: *"`tofu apply` returns when the CLONE is complete, which is ~9s — the guest still has to
boot after that, so a single immediate SSH gets 'No route to host'."* `factory` ships `just gate
<vm>` for this: poll SSH to a 240s deadline, then `cloud-init status --wait` (bounded at 180s),
then assert hostname, address, route, sudo, DNS and `authorized_keys`.

**Yes, there is an Ansible step.** `ansible/site.yml` applies the `common` baseline (packages,
timezone, SSH hardening, unattended-upgrades, guest agent, tools) to `factory_guests`, driven by
`just play`. Two consequences for lab nodes:

- `ansible/inventory/hosts.yml` is **static and hand-maintained** — its own comment says keeping
  it in step with the `vms` map is *"a two-line change, one here and one there"*, and *"dynamic
  inventory from OpenTofu state is deferred, not rejected."* Lab nodes that come and go per phase
  are precisely the case that convention does not cover.
- `ansible-galaxy` collections are installed by `just ansible-deps`; `just idempotent` asserts a
  second run reports `changed=0`.

### The invocation, if `tofu/labs` is written to this repo's existing conventions

**Extrapolation, not verification. Nothing below was run and no file below exists.** It is
recorded so #32 has something concrete to mark as unconfirmed rather than a blank.

```
ssh hopper
cd factory && git pull
just tofu labs apply -var 'topology=pair'    # interface unspecified — see caveat
just play                                     # baseline onto the new guests
just gate <node>                              # SSH + cloud-init settled
```

The `just tofu <dir> <cmd>` recipe is already generic, so `just tofu labs …` costs nothing the
moment the module exists. **The caveat is the interface.** `tofu/vms` models a fleet as a
`map(object({vm_id, ipv4_address, cpu_cores, memory_mb, disk_gb, tags}))` keyed by hostname — a
data edit, not a switch. Whether `tofu/labs` exposes a `topology` *string* selecting a preset, or
a `vms`-shaped map per topology, is an unmade design decision in a repo this map has declared out
of scope. **#32 cannot state the flag name.**

### What `factory` does confirm about lab node identity

Not the invocation, but the constraints any lab module must satisfy:

- **VMID = last octet of the IPv4 address** — the stated convention, enforced nowhere but followed
  everywhere.
- `modules/vm/variables.tf` validates `vm_id >= 100 && vm_id < 9000` (9xxx reserved for templates).
- `bootstrap_vm_ids = [9000, 110, 120]` — template, `hopper`, `carthage` — and `tofu/vms` refuses
  at **plan** time to create a VM at any of them. So `10.10.10.130`+ is clear, exactly as #8
  suggested.
- `disk_gb` is validated `>= 4` (the Debian 13 genericcloud image is 3.0G virtual); every topology
  above clears it comfortably.
- Defaults are `cpu_cores = 2`, `memory_mb = 1024`, `disk_gb = 5` — no topology should rely on
  them.
- Currently occupied: `.110` `hopper`, `.111` `jeremie`, `.120` `carthage`. Nothing else.

### Per-node IPs are not specified anywhere authoritative

#8 gives a **range**, not addresses: *"suggest labs occupy `10.10.10.130`+ leaving `.200`+ for
MetalLB."* The only concrete per-node assignment in either repo is
`phases/08-storage.md:63` — `pair` CP at `.130`, worker at `.131` — which appears exactly once and
is not corroborated. **The other seven topologies have no addresses at all.** #32 either invents a
consistent scheme (and flags it as invented) or states the range and leaves node addresses to the
unwritten module. The second is more honest; the first is more useful to ~100 exercises. That
choice is #32's, and it should be recorded as a choice.

---

## 3. Teardown, as `factory` implements it

There is **exactly one** teardown recipe in the whole repo:

```just
[confirm("Destroy all VMs in tofu/vms? The template (9000), hopper (110) and carthage (120)
are in no state file and are NOT affected. [y/N]")]
destroy-vms:
    tofu -chdir=tofu/vms destroy -auto-approve
```

Facts that follow:

- It is **hardcoded to `tofu/vms`**. There is no labs equivalent and no parameterised destroy.
- It is interactively confirmed, and `just check` **deliberately excludes it** — the justfile says
  so: *"nothing that can destroy a VM or reboot the node is reachable from the routine check."*
  An unattended per-exercise teardown would need `--yes` or the generic recipe.
- The generic `just tofu labs destroy` **would** work the moment `tofu/labs` exists, and is the
  more likely lab form. Unverified.
- As of `6f4692f`, `just destroy-vms` destroys `jeremie` and nothing else, because `jeremie` is
  the entire content of the `vms` map.

`strands/build-mechanics.md:127–130` adds two commands to the same teardown, on disk grounds
(`workhorse` 65G + `forge` 25G is 90G of 95G): **`go clean -modcache` and `docker system prune`
belong in the teardown runbook alongside `tofu destroy`.** That is a build-track fact and stays in
`build-mechanics`; the strand doc links to it rather than restating it.

---

## 4. The bastion pattern

**Settled, and stated in one sentence in #8:** *"MetalLB in L2 mode on a reserved slice of
`10.10.10.0/24` (suggest `.200`–`.250`) is the standard way labs expose a UI, reached from the Mac
over an SSH proxy through `factory`."*

Chosen deliberately over `kubectl port-forward`, and the reasoning is pedagogical rather than
practical: port-forward bypasses the Service/LoadBalancer datapath entirely and hides the exact
mechanics the curriculum exists to teach, whereas MetalLB L2 makes *"how does a LoadBalancer
actually get an IP"* concrete via ARP announcement. **`port-forward` stays available as the quick
path when access is incidental rather than the lesson** — that clause matters for ~100 exercises,
most of which are not teaching L2.

Cross-checked against `factory`, and consistent:

- `vmbr0` is `10.10.10.1/24` with **`bridge-ports none`** — no physical port, no DHCP. #8 calls
  this *"close to ideal for L2 mode"*, and it is: no competing DHCP server, no other L2 speakers.
- The bastion is real and committed: `ssh/config` carries `Host factory` (192.168.100.20,
  `ForwardAgent yes`) and `Host 10.10.10.*` (`ProxyJump factory`). It is wired in with a single
  `Include` at the top of `~/.ssh/config`, and *"at the very top"* is load-bearing — ssh takes the
  first value it sees per keyword.
- Egress is MASQUERADE out `nic0`; guests reach the internet, nothing reaches guests.

**Two gaps.** Nothing in `factory` reserves `.200`–`.250` — there is no MetalLB config, no
IPAddressPool, and no comment claiming the range; the reservation exists only in #8's prose, which
is sufficient today because only `.110`/`.111`/`.120` are allocated. And #8 does **not** give the
concrete command for reaching a MetalLB VIP from a browser on the Mac — whether that is
`ssh -L 8080:10.10.10.200:80 factory`, a `-D` SOCKS proxy, or something else, is unsettled.
A dozen exercises need that literal line and it does not exist yet.

---

## 5. Teardown discipline — #8 ruled **per phase**, and never per exercise

This is the question #31 asked to be answered plainly, so plainly:

> **Every phase starts from a clean provision — no long-lived clusters accreting across phases.
> Because both RAM and disk are one-topology-at-a-time, teardown is not hygiene but a hard
> precondition for the next phase booting at all.** — #8, *Teardown discipline*, in full.

That is the entire ruling. **#8 contains no statement about per-exercise teardown, in either
direction.** Three finer scopes exist, all settled elsewhere and all coarser than an exercise:

| Scope | Ruled by | Form |
|---|---|---|
| Per phase | #8 | *"Every phase starts from a clean provision."* |
| Per lab **group** within a phase | #14, applied in `phases/12-gitops-platform.md#teardown` | Tear down Group A before Group B — the `platform` node holds either group but not both |
| "Everything else torn down" for a **big rock** | #8's one-big-rock rule, applied in `phases/09-service-mesh.md:12` | Istio is the rock; nothing co-resident |

And the worked prototype demonstrates the **opposite** of per-exercise teardown:
`phases/08-storage.md:63` opens Lab 8.2 with *"Everything from Phase 7 torn down first — this is a
hard precondition, not hygiene"* (a per-phase line), and `phases/08-storage.md:107` opens Lab 8.3
with **"`pair`, continued from 8.2"**. Consecutive exercises deliberately share a live cluster.
Under one-topology-at-a-time that is not laxness, it is the only way a phase of 6–12 exercises
completes: a `pair` provision plus baseline plus `gate` is minutes of wall-clock before any
teaching happens.

**So #32 must not invent a per-exercise teardown rule.** What it can state without inventing
anything: the three scopes above, and that an exercise's own teardown line is therefore usually a
*continuity marker* — `pair`, continued from `08-02` — with a real teardown only where an exercise
ends a phase, ends a lab group, or installs a big rock. Whether that is the final form is a
**format** decision belonging to [#33](https://github.com/k3ii/k8s-academy/issues/33) (the
`labs/08/` prototype) and [#35](https://github.com/k3ii/k8s-academy/issues/35) (the template
ratification), not a capacity decision #32 may take alone.

---

## 6. Drift found in `factory` while checking

Not what #31 asked, but it bears on whether the numbers hold.

**`jeremie` is still declared.** #8 decision 1 destroys it *"for the duration of the academy"* —
and that reclaimed 1GB is *"the difference between the `ha` topology fitting and not."* At
`6f4692f` (2026-08-17) `jeremie` is still the sole entry in `tofu/vms/variables.tf`'s `vms` map,
still in `ansible/inventory/hosts.yml`, and `just gate` and `just verify-agent` still default to
`vm="jeremie"` — the exact *"consequence to handle"* #8 flagged, unhandled. The ~9.5GB spendable
figure is therefore **a budget conditional on an action not yet taken**. Fixing it is a `factory`
commit, out of scope here; the strand doc should not silently present 9.5GB as the live state.

**`forge` does not exist yet either.** `build-mechanics#forge` specifies it at 1536MB / 2c / 25G on
`10.10.10.0/24`, *"never torn down"*. It is in no `vms` map, no inventory, and no state. Same
class of gap: specified in the curriculum, unbuilt in the lab.

---

## 7. Overlap with `build-mechanics#forge` — what #32 must not duplicate

The `#forge` table is genuinely a **forge-sizing argument**, not a topology spec. Its columns are
*topology total · + `forge` 1536MB · margin in 9.5GB*, and its conclusion is *"1536MB keeps 'always
up' literally true for every topology in the table."* The topology totals are that argument's
input.

Under the one-fact-one-place convention, the totals column is the only genuine collision. The
strand doc becomes the home for per-node sizing and totals; `build-mechanics` keeps — and #32 must
not restate — `forge`'s own footprint (1536MB, 2560MB for P5), the
[P5 split](../strands/build-mechanics.md#p5-split), kernel lockstep, the registry, and cache
eviction as part of teardown. The cleanest repair is `build-mechanics`'s table linking its
topology names into the new strand doc; whether that edit happens now or when #32 lands is #32's
call, but leaving two totals tables is the outcome the convention forbids.

---

## What could **not** be verified

Flat list, for #32 to mark unconfirmed rather than assert:

1. **`tofu/labs` exists.** It does not, at `k3ii/factory@6f4692f`. Any invocation naming it is
   aspirational.
2. **The variable name `topology`, and its values.** No such variable exists. `-var 'topology=pair'`
   cannot be confirmed and the interface it implies (string preset vs. `vms`-style map) is an
   unmade design decision.
3. **A teardown target for labs.** Only `just destroy-vms` exists, hardcoded to `tofu/vms`. Whether
   labs get `just tofu labs destroy`, a dedicated confirmed recipe, or something else is unwritten.
4. **Per-node IP addresses for seven of the eight topologies.** Only `pair` has addresses
   (`.130`/`.131`), from one uncorroborated line in `phases/08-storage.md`. #8 gives a starting
   octet and a MetalLB reservation, nothing more.
5. **The exact Ansible step for lab nodes.** `just play` / `site.yml` / `just gate` exist and apply
   to `factory_guests`, but the inventory is hand-maintained and has no lab entries; how ephemeral
   nodes join it is not decided.
6. **The concrete browser-to-MetalLB-VIP command.** The pattern is settled; the literal
   `ssh -L …` / SOCKS form is not stated anywhere.
7. **Anything measured.** No topology in the table has been provisioned. Every RAM figure is an
   allocation decision, not an observation — `ha`'s 7.5GB in particular is #8's arithmetic, and
   `build-mechanics` itself flags the `ha` + `forge` margin as *"thin"* at 0.5GB.
8. **That ~9.5GB is currently spendable.** It assumes `jeremie` destroyed; `jeremie` still exists.

## What *is* safe to state without qualification

- All eight topologies' node counts, per-node RAM/cores/disk, and totals (§1) — quoted from #8 and
  #14, with `platform` attributed to #14.
- One topology at a time, on RAM **and** disk; `balloon 0`, no reclaim, swap is not a valve.
- `hopper` + `carthage` mandatory; `jeremie` reclaimed; `forge` always up; ~9.5GB spendable, 95G
  disk.
- Labs occupy `10.10.10.130`+, VMID = last octet, `.200`–`.250` reserved for MetalLB.
- MetalLB L2 is the exposure pattern, over an SSH proxy through `factory`; `port-forward` is the
  sanctioned quick path when access is incidental.
- **Everything reaching Proxmox, OpenTofu or Ansible runs on `hopper`, never the Mac** — enforced
  in code by `factory_require_hopper`.
- The guest account is **`zain`**, key-only, and `ssh zain@10.10.10.x` needs **no** `-J` flag from
  either machine.
- `tofu apply` returns ~9s before the guest is reachable; a boot/cloud-init wait is required, and
  `just gate <vm>` is the existing implementation.
- Teardown is ruled **per phase** (#8), with per-group (#14) and big-rock (#8) refinements. **Not
  per exercise.**

---

### Sources

`k3ii/factory` @ `6f4692f` — `justfile` (recipes `tofu`, `destroy-vms`, `play`, `ping`,
`ansible-deps`, `gate`, `idempotent`, `check`); `scripts/env.sh` (`factory_require_hopper`,
platform dispatch, `FACTORY_JUMP_HOST`); `tofu/vms/{variables,main,outputs,backend}.tf`;
`tofu/modules/vm/{main,variables}.tf`; `ansible/inventory/hosts.yml`; `ansible/site.yml`;
`ssh/config`; `README.md`.

`k3ii/k8s-academy` @ `c466b38` — [#8](https://github.com/k3ii/k8s-academy/issues/8) resolution
comment; [#14](https://github.com/k3ii/k8s-academy/issues/14) resolution comment;
`phases/08-storage.md` (lines 63, 66–69, 107); `phases/09-service-mesh.md:12`;
`phases/12-gitops-platform.md` (lines 12, 14, 76–78); `strands/build-mechanics.md` (lines 60–130);
`README.md` (lab environment, conventions).

**Re-verify before relying on this.** `k3ii/factory` is under active development — its HEAD moved
the day before this research ran, and every "does not exist" above is a statement about one commit
on one day. The unwritten pieces (`tofu/labs`, `forge`, `jeremie`'s removal) are exactly the ones
most likely to have changed.
