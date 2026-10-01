# The `pair` baseline — captured 1 Oct 2026

> **What makes the running cluster work**, read off `pair-cp` and `pair-w1` while they were up, 28 days into their life.
> This is [the sprint plan](plan.md)'s Thu 1 Oct session, and it exists for one reason: **on Sat 10 Oct this cluster is destroyed twice.** If the evening rebuild does not come back, [the abort rule](plan.md#topology) rebuilds from this file rather than from memory.

| | |
|---|---|
| **Captured** | Thu 1 Oct 2026, ~20:45 SAST, over SSH from the control node |
| **Subject** | `pair-cp` `10.10.10.130` · `pair-w1` `10.10.10.131` — both `Ready`, uptime 18d, cluster age 28d |
| **Method** | Read-only inspection of a running cluster. **The capture changed nothing** — the one thing that was then installed is [§5 edge 1](#sharp-edges), recorded as a fix rather than folded in silently. |
| **Expires** | Sat 10 Oct, when the pin to v1.35 makes the version numbers below wrong on purpose |

---

<a id="versions"></a>

## 1. What it is running

| | |
|---|---|
| **OS** | Debian GNU/Linux 13 (trixie), kernel `6.12.107+deb13-cloud-amd64` |
| **Kubernetes** | **v1.37.0** — `kubeadm`, `kubelet`, `kubectl` all `1.37.0-1.1` |
| **Runtime** | containerd **v2.2.1**, runc **1.5.1**, `kubernetes-cni` `1.9.1-1.1` |
| **etcd** | `registry.k8s.io/etcd:3.7.0-0`, stacked, `/var/lib/etcd` |
| **CoreDNS** | `registry.k8s.io/coredns/coredns:v1.14.6`, 2 replicas |
| **CNI** | `ghcr.io/flannel-io/flannel:v0.28.9`, vxlan |
| **Policy** | `registry.k8s.io/networking/kube-network-policies:v1.1.2` |
| **Storage** | `docker.io/rancher/local-path-provisioner:v0.0.37` — **installed 1 Oct**, see [§5](#sharp-edges) |

**v1.37.0 is the thing being left behind.** The rebuild on Sat 10 pins **v1.35**, so every version above is a record of what *was*, not a target — except containerd, runc and the kernel, which are the node baseline and do not move.

---

<a id="node"></a>

## 2. The node baseline — identical on both nodes

This is the part `factory` does **not** manage, and therefore the part that `kubeadm init` preflight rests on.

**Kernel modules**, `/etc/modules-load.d/`:

```
overlay
br_netfilter
```

Loaded and confirmed on both nodes, along with `nf_conntrack`, `nf_conntrack_netlink`, `vxlan` (Flannel's backend) and `nfnetlink_queue` — the last is `kube-network-policies`' datapath and is **why the policy controller works at all**.

**Sysctls**, `/etc/sysctl.d/`, all three live at `1`:

```
net.ipv4.ip_forward=1
net.bridge.bridge-nf-call-iptables=1
net.bridge.bridge-nf-call-ip6tables=1
```

**Swap:** off, and not in `fstab`.

**iptables:** `v1.8.11 (nf_tables)`, with the alternative pointed at `/usr/sbin/iptables-nft`. Both kube-proxy and Flannel are nonetheless in **legacy iptables mode** — see [§5](#sharp-edges).

**containerd**, `/etc/containerd/config.toml`, config `version = 3`:

| Key | Value |
|---|---|
| `SystemdCgroup` | `true` |
| `snapshotter` | `overlayfs` |
| pinned `sandbox` | `registry.k8s.io/pause:3.10.1` |

`SystemdCgroup = true` against the kubelet's `cgroupDriver: systemd` is the pair that has to match. A mismatch here is the classic kubelet-won't-start, and it is one of the things a rebuild gets wrong.

**Package pin.** All three are **held**, which is what makes the version stable across 28 days of unattended upgrades:

```
$ apt-mark showhold
kubeadm
kubectl
kubelet
```

Repo: `deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.37/deb/ /`

**On Sat 10 that URL changes to `v1.35`.** The minor version is in the repo path, so pinning back is an edit to this line, an `apt-mark unhold`, an install of the pinned `1.35.x-1.1` versions, and a re-hold. It is not an `apt upgrade`.

`kubelet` and `containerd` are both `enabled`.

---

<a id="cluster"></a>

## 3. The cluster shape

From `kubeadm-config`, `kubeadm.k8s.io/v1beta4`:

| | |
|---|---|
| **podSubnet** | `10.244.0.0/16` — and Flannel's `Network` matches it |
| **serviceSubnet** | `10.96.0.0/12` |
| **dnsDomain** | `cluster.local` |
| **advertise-address** | `10.10.10.130` |
| **imageRepository** | `registry.k8s.io` |
| **kube-proxy mode** | `iptables` |
| **cgroupDriver** | `systemd` |
| **resolvConf** | `/run/systemd/resolve/resolv.conf` |

**`podSubnet` must be passed to `kubeadm init`** and must equal Flannel's `Network`, or pods come up and nothing routes. It is the single most common rebuild failure and it is silent — nodes go `Ready`, and only pod-to-pod traffic is broken.

`/etc/cni/net.d/10-flannel.conflist`, written by Flannel:

```json
{
  "name": "cbr0",
  "cniVersion": "0.3.1",
  "plugins": [
    { "type": "flannel", "delegate": { "hairpinMode": true, "isDefaultGateway": true } },
    { "type": "portmap", "capabilities": { "portMappings": true } }
  ]
}
```

`kube-flannel-cfg`:

```json
{ "Network": "10.244.0.0/16", "EnableNFTables": false, "Backend": { "Type": "vxlan" } }
```

**Certificates** are not a constraint: leaf certs run to **Sep 2027**, the CAs to **2036**. Nothing in this sprint will see an expiry, so the cert-rotation drill has to induce one rather than wait for it.

---

<a id="rebuild"></a>

## 4. The rebuild order

What Sat 10 evening actually does, and what the abort rule repeats. Steps 1–4 are [the plan](plan.md#topology)'s four manual stages; **5 onward is B1**.

1. `just tofu labs apply -var 'topology=pair'`
2. `just gate pair-cp` and `just gate pair-w1` — `apply` returns on clone, not on reachable
3. `just play` — the Ansible baseline
4. **By hand, both nodes:** modules, sysctls, swap off, containerd with `SystemdCgroup = true`, the **v1.35** apt repo, install, `apt-mark hold`
5. `kubeadm init --pod-network-cidr=10.244.0.0/16` on the CP
6. Flannel, then **`kube-network-policies` v1.1.2 with the image `sed`** (the manifest at that tag still names the v1.1.1 image), then **`local-path-provisioner` v0.0.37 with its own image `sed`, annotated default** ([§7](#storage-fix))
7. `kubeadm join` the worker
8. **Prove it**, in this order: both nodes `Ready` · CoreDNS 2/2 · a pod on `w1` reaches a Service on `cp` · a `NetworkPolicy` actually denies · **a PVC actually binds**

**Step 8 is the part worth insisting on.** Steps 1–7 can all appear to succeed on a cluster whose pod network is broken, and the F09 fault class exists precisely because a cluster with no policy enforcement looks identical to one with a correct allow-all.

---

<a id="sharp-edges"></a>

## 5. Four sharp edges found while capturing

None of these were known before tonight, and three of them are drill material rather than defects.

**1. There was no StorageClass at all — and it broke a fault, not just the drills.** `kubectl get sc,pv,pvc -A` returned `No resources found`. Storage is [a scored domain](../strands/certs.md#cka), so every storage drill had nothing to bind to; a rebuild would not have fixed it, because there was never anything to rebuild.

> **Fixed the same night.** This one could not wait, because **Fri 2 Oct plants the diagnostic's faults** and the injector's `F12 — no default StorageClass` aborts the whole run when it finds none to un-default. Worse, the obvious workaround is wrong: the injector picks faults by **seeded shuffle over the whole catalogue**, so dropping F12 would have changed which faults *every* seed selects, and with it the "same seed, same faults, three weeks later" property the three-pass rule depends on. Standing a StorageClass up keeps the catalogue and the seeds intact. See [§7](#storage-fix).

**2. `KUBELET_KUBEADM_ARGS` is empty.** `/var/lib/kubelet/kubeadm-flags.env` holds `KUBELET_KUBEADM_ARGS=""` — no `--container-runtime-endpoint`, no pod-infra image. It works, because containerd's socket is at the default path the kubelet already probes. Worth knowing: a rebuild that puts the socket anywhere else will fail with nothing in this file to explain why.

**3. `/etc/crictl.yaml` does not exist.** So `crictl` has no configured runtime endpoint and warns on every invocation. **This is good for the exam and should be left alone** — it forces `crictl -r unix:///run/containerd/containerd.sock`, which is the form the exam environment rewards knowing.

**4. The nft/legacy split.** The host's `iptables` alternative is `iptables-nft`, but kube-proxy runs `mode: iptables` and Flannel has `EnableNFTables: false`. Rules therefore land in the nft tables via the compat shim, and **`iptables-legacy -L` shows nothing while `iptables -L` shows everything.** A troubleshooting drill that greps the wrong one concludes the rules are missing. Leave the split in place — it is a faithful reproduction of what a real node looks like.

---

<a id="leftovers"></a>

## 6. Leftovers, left alone

`storefront/till` — an `agnhost:2.47` Deployment, 2/2, with a ClusterIP Service, **27 hours old**. It is the 30 Sep policy-controller smoke test, and it is deliberately not cleaned up: the **3 Oct diagnostic** wants a namespace someone else left behind, and this is a real one rather than a staged one.

It dies with the cluster on Sat 10 and does not need to come back.


---

<a id="storage-fix"></a>

## 7. The StorageClass, installed 1 Oct

[Rancher local-path-provisioner](https://github.com/rancher/local-path-provisioner) **v0.0.37**, pinned, marked default. Chosen over a `no-provisioner` StorageClass with hand-made PVs because that would satisfy F12's guard while leaving dynamic provisioning — the thing the storage domain is actually about — still untestable.

```sh
curl -sSL -o lpp.yaml \
  https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.37/deploy/local-path-storage.yaml
sed -i 's|image: docker.io/library/busybox$|image: docker.io/library/busybox:1.37.0|' lpp.yaml
kubectl apply -f lpp.yaml
kubectl annotate sc local-path storageclass.kubernetes.io/is-default-class=true
```

**The `sed` is not cosmetic, and it is the same shape as the `kube-network-policies` one.** The upstream manifest's helper pod is `docker.io/library/busybox` with **no tag** — an implicit `:latest`. A lab whose storage path silently re-pulls a different busybox on every rebuild is not a baseline, and the whole point of this file is that Sat 10 reproduces what was here. The provisioner's own image was already pinned; the helper was not.

`local-path` is **not** default as shipped, and the annotation is a separate step. F12 un-defaults it, so without that annotation the fault has nothing to act on even with the provisioner running.

### Verified, not assumed

- Provisioner rolled out **1/1**.
- A 64Mi PVC went **`Bound`**, its PV landing with node affinity on `pair-w1` — so `WaitForFirstConsumer` is doing what it should.
- Data written through the mount and read back.
- Deleting the namespace reclaimed the PV, leaving `No resources found` — the `Delete` policy works, so drills will not silently accumulate volumes.
- **F12's guard query, run verbatim, now returns `local-path`**, and its inject/revert annotation pair round-trips cleanly.

**What was not verified:** `cka-inject.sh --only F12` end to end. The script sources `scripts/env.sh`, which needs the state-encryption passphrase from `gpg`, and `gpg` needs a tty — its own error text says to run it from an interactive shell rather than over `ssh <host> <command>`. The guard and the mechanism were checked by hand instead. **Running the real thing once, interactively, belongs at the start of Fri 2 Oct**, before the night's faults go in.

### What this costs the rebuild

One more step at [§4](#rebuild) step 6, alongside Flannel and the policy controller — and one more thing that is **plumbing, not a drill**, for the same reason the CNI is: the curriculum tests using storage, not installing a provisioner.
