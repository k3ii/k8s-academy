<a id="drill-menu"></a>
# The CKA drill menu — 66 objects

> **A menu, not a schedule.** [The plan](../plan.md) decides which of these run and when; this tree holds what they *are*. Every object below is listed whether or not its body is written yet — an id in plain text is still owed, an id that links is done.
> **Nothing here is a phase.** Drills are deliberately unchained: no `Rests on`, no ordering between files, no prerequisite but the topology each one names.

| | |
|---|---|
| **Tier and band** | Defined once in [the plan](../plan.md#how-to-read) and **not restated here**. Tier is size, band is priority, and they are different axes. |
| **Counts** | 59 Reflex + 7 Builds · **14 Pinned / 42 Core / 10 Optional** |
| **Topologies** | [`pair`](../../strands/lab-topologies.md#pair) 56 · [`workhorse`](../../strands/lab-topologies.md#workhorse) 8 · [`ha`](../../strands/lab-topologies.md#ha) 2 |
| **Written** | **56 of 66** |
| **Provenance** | The `t04` and `t07` inventories of the wayfinder map in `k3ii/factory` at `thoughts/shared/wayfinder/cka-sprint/`. Ids, titles, tiers, bands and topologies come from there unchanged; the bodies are new work. |

---

<a id="how-to-use"></a>

## 1. How to use this

**Pick by domain, then by band.** The gap rule in the plan allocates minutes to a *domain*; you then spend them on that domain's **Pinned** rows first and its **Core** rows next. **Optional** rows are not scheduled — they are the reservoir for a retake week.

**One pass per drill per week.** A Reflex is worked three times and the three passes are three different exercises, so each file carries all three and you run one of them. The file states what pass 2 adds and what pass 3 takes away.

**Three drills are one object seen twice.** **N5** and **TS15** are the same machinery as feature and as fault; so are **N3**/**TS17** and **N9**/**TS8**. Each pair is written in one sitting and the two files link each other; the plan runs only one side of each, and the other stays here as the reservoir copy.

<a id="file-shape"></a>

### The shape of a drill file

Every file opens with an anchor, an `# <ID> — <title>` heading, and then **one metadata line in a fixed order**:

```
**<Tier>** · **<Band>** · **<time target>** · [`<topology>`](<relative path to strands/lab-topologies.md>#<topology>) · <Domain> / <sub-competency>
```

That line is what `cka/check-drills.py` reads: it carries **exactly one** topology link, a time target and a band, which are three of the gate's four checks. The fourth is this index — every file below appears here exactly once, and every link here resolves.

Ids are **path-scoped**, as `labs/` ids are. Forty-odd files reusing `#do` and `#teardown` would collide in a global namespace.

**Drills address each other through this index, not directly.** A drill file links *out* — to the plan, the baseline, a strand — but when it names a sibling drill it writes the bare id in bold, like **TS10**, and leaves the reader to find it here. That is not a style preference: a tree where file A links file B cannot be gated until both exist, and the gate is meant to be green from the first file rather than red for five weeks. **The one exception is the three authored-together pairs**, which are written in the same sitting and so may link each other directly.

---

<a id="architecture"></a>

## 2. Cluster Architecture, Installation and Configuration — 13 objects, 11 written

| # | Drill | Tier | Band | Topology | Serves |
|---|---|---|---|---|---|
| [**B1**](architecture/b01-kubeadm-init-from-nothing.md) | Prepare the underlying infrastructure, then `kubeadm init` and join a worker from nothing | Build | **Pinned** | [`pair`](../../strands/lab-topologies.md#pair) | Prepare infrastructure · Create clusters with kubeadm |
| [**B2**](architecture/b02-kubeadm-upgrade.md) | `kubeadm upgrade` — control plane first, then the node; drain and uncordon around it | Build | **Pinned** | [`pair`](../../strands/lab-topologies.md#pair) | Manage cluster lifecycle |
| [**B3**](architecture/b03-three-stacked-control-planes.md) | Stand up three stacked control planes, then lose one and keep quorum | Build | **Pinned** | [`ha`](../../strands/lab-topologies.md#ha) | HA control plane |
| [**B4**](architecture/b04-helm-and-kustomize.md) | Install metrics-server, a Gateway controller and MetalLB with Helm; then one Kustomize overlay on top | Build | **Pinned** | [`pair`](../../strands/lab-topologies.md#pair) | Helm and Kustomize · unlocks W10, N7, N13 |
| [**B5**](architecture/b05-crd-and-operator.md) | Install a CRD and its operator, create a CR, watch it reconcile | Build | **Pinned** | [`pair`](../../strands/lab-topologies.md#pair) | CRDs and operators |
| [**A1**](architecture/a01-role-and-rolebinding.md) | Role + RoleBinding for a ServiceAccount, proved with `auth can-i --as` | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | RBAC |
| [**A2**](architecture/a02-clusterrole-cluster-scoped.md) | ClusterRole + ClusterRoleBinding over a cluster-scoped resource | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | RBAC |
| [**A3**](architecture/a03-clusterrole-bound-by-rolebinding.md) | A ClusterRole bound by a *RoleBinding* — cluster role, namespace scope | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | RBAC |
| [**A4**](architecture/a04-serviceaccount-token.md) | ServiceAccount token: create, mount, read and use it from inside a pod | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | RBAC |
| A5 | Aggregated ClusterRoles via `aggregationRule` labels | Reflex | Optional | [`pair`](../../strands/lab-topologies.md#pair) | RBAC |
| [**A6**](architecture/a06-a-request-was-denied.md) | A request was denied — say who, what, and which binding is missing | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | RBAC |
| [**A7**](architecture/a07-cni-csi-cri.md) | Name the CNI, CSI and CRI in play; find each config on disk and its socket | Reflex | **Pinned** | [`pair`](../../strands/lab-topologies.md#pair) | Extension interfaces |
| A8 | Change the runtime's cgroup driver; observe what kubelet does about it | Reflex | Optional | [`pair`](../../strands/lab-topologies.md#pair) | Extension interfaces |

---

<a id="networking"></a>

## 3. Servicing and Networking — 13 objects, 12 written

| # | Drill | Tier | Band | Topology | Serves |
|---|---|---|---|---|---|
| [**N1**](networking/n01-default-deny-ingress.md) | Default-deny ingress across a namespace, proved | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Network Policies |
| [**N2**](networking/n02-allow-from-podselector.md) | Allow from a `podSelector` label; prove both the allow and the block | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Network Policies |
| [**N3**](networking/n03-egress-with-dns-carve-out.md) | Egress policy **including the DNS carve-out** | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Network Policies |
| N4 | `namespaceSelector` allow across namespaces | Reflex | Optional | [`pair`](../../strands/lab-topologies.md#pair) | Network Policies |
| [**N5**](networking/n05-clusterip-and-endpoints.md) | ClusterIP and endpoints — break the selector, watch endpoints empty | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Service types · endpoints |
| [**N6**](networking/n06-nodeport-on-and-off-node.md) | NodePort reached from the node, then from off-node | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Service types |
| [**N7**](networking/n07-loadbalancer-metallb.md) | LoadBalancer against MetalLB with an address pool | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Service types |
| [**N8**](networking/n08-three-dns-names.md) | Resolve `svc`, `svc.ns`, `svc.ns.svc.cluster.local` — and say why each works | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | CoreDNS |
| [**N9**](networking/n09-corefile-forward.md) | Edit the Corefile ConfigMap, add a forward, make CoreDNS reload | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | CoreDNS |
| [**N10**](networking/n10-pod-to-pod-across-nodes.md) | Pod to pod across nodes; find the pod CIDR and the node route that carries it | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Pod connectivity |
| [**N11**](networking/n11-debug-a-distroless-pod.md) | Debug a distroless pod with `kubectl debug` and an ephemeral container | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Pod connectivity |
| [**N12**](networking/n12-ingress-host-and-path.md) | Ingress with host and path rules against the installed controller | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Ingress |
| [**N13**](networking/n13-gateway-and-httproute.md) | A minimal Gateway plus HTTPRoute | Reflex | **Pinned** | [`pair`](../../strands/lab-topologies.md#pair) | Gateway API |

---

<a id="workloads"></a>

## 4. Workloads and Scheduling — 11 objects, 9 written

| # | Drill | Tier | Band | Topology | Serves |
|---|---|---|---|---|---|
| [**W1**](workloads/w01-requests-that-do-not-fit.md) | Requests and limits that do — then don't — fit; read the `FailedScheduling` event | Reflex | Core | [`workhorse`](../../strands/lab-topologies.md#workhorse) | Pod admission and scheduling |
| [**W2**](workloads/w02-nodeaffinity-required-vs-preferred.md) | `nodeAffinity`, required against preferred | Reflex | Core | [`workhorse`](../../strands/lab-topologies.md#workhorse) | Pod admission and scheduling |
| [**W3**](workloads/w03-taints-and-tolerations.md) | Taints and tolerations, including a `NoExecute` eviction | Reflex | Core | [`workhorse`](../../strands/lab-topologies.md#workhorse) | Pod admission and scheduling |
| W4 | `topologySpreadConstraints` across three nodes | Reflex | Optional | [`workhorse`](../../strands/lab-topologies.md#workhorse) | Pod admission and scheduling |
| [**W5**](workloads/w05-rolling-update-paused.md) | Rolling update, paused mid-roll, then resumed | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Rolling updates |
| [**W6**](workloads/w06-rollback-to-a-revision.md) | Roll back to a named revision; read the rollout history | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Rollbacks |
| W7 | `maxSurge` and `maxUnavailable` tuned; watch the pod churn change | Reflex | Optional | [`pair`](../../strands/lab-topologies.md#pair) | Rolling updates |
| [**W8**](workloads/w08-configmap-env-vs-volume.md) | ConfigMap as env and as volume — change it, see which one reloads | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | ConfigMaps and Secrets |
| [**W9**](workloads/w09-secret-literal-and-file.md) | Secret from literal and from file, consumed as a volume | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | ConfigMaps and Secrets |
| [**W10**](workloads/w10-hpa-under-real-load.md) | HPA on CPU against metrics-server, driven under real load | Reflex | **Pinned** | [`pair`](../../strands/lab-topologies.md#pair) | Workload autoscaling |
| [**W11**](workloads/w11-three-probes.md) | Liveness, readiness and startup probes; break one, watch the restarts | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Self-healing primitives |

---

<a id="storage"></a>

## 5. Storage — 8 objects, 6 written

| # | Drill | Tier | Band | Topology | Serves |
|---|---|---|---|---|---|
| [**S1**](storage/s01-bind-mount-write-reread.md) | PVC binds, mounts, takes a write; delete the pod and read it back | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Manage PVs and PVCs |
| [**S2**](storage/s02-pvc-stuck-pending.md) | A PVC stuck `Pending` — no class, no capacity, wrong access mode | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Manage PVs and PVCs |
| S3 | Resize a bound PVC | Reflex | Optional | [`pair`](../../strands/lab-topologies.md#pair) | Manage PVs and PVCs |
| [**S4**](storage/s04-define-a-storageclass.md) | Define a StorageClass and provision dynamically | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Storage classes · dynamic provisioning |
| [**S5**](storage/s05-default-class-set-and-unset.md) | Set and unset the default class; watch what a class-less PVC does | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Storage classes |
| S6 | `WaitForFirstConsumer` against `Immediate` binding | Reflex | Optional | [`pair`](../../strands/lab-topologies.md#pair) | Dynamic provisioning |
| [**S7**](storage/s07-rwo-against-rwx.md) | RWO against RWX, attempted from two nodes at once | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Access modes |
| [**S8**](storage/s08-retain-against-delete.md) | `Retain` against `Delete`; then recover a Released PV | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Reclaim policies |

---

<a id="troubleshooting"></a>

## 6. Troubleshooting — 21 objects, 18 written

| # | Drill | Tier | Band | Topology | Serves |
|---|---|---|---|---|---|
| [**TB1**](troubleshooting/tb01-fault-catalogue-and-injector.md) | **Build the fault catalogue and the injector.** Induce each fault class once by hand, record its signature, then wrap the set in a script that plants a random subset and reveals only after the clock stops | Build | **Pinned** | [`pair`](../../strands/lab-topologies.md#pair) | Harness for TS1–TS19 · all five |
| [**TB2**](troubleshooting/tb02-the-broken-cluster-hour.md) | **The broken-cluster hour.** Five faults at once across the five sub-competencies. Read all five before touching anything, bank the cheap ones, flag and skip the expensive one, report what you deliberately did not fix | Build | **Pinned** | [`pair`](../../strands/lab-topologies.md#pair) | Triage across all five |
| [**TS1**](troubleshooting/ts01-node-notready-ladder.md) | A node is `NotReady` — work the ladder: kubelet unit, kubelet config and certs, runtime socket, CNI config on disk. Name the rung before you fix it | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Clusters and nodes |
| [**TS2**](troubleshooting/ts02-disk-and-memory-pressure.md) | Drive a node into `DiskPressure`, then `MemoryPressure`. Read the condition, the eviction order and the taint that appears; then clear it | Reflex | Core | [`workhorse`](../../strands/lab-topologies.md#workhorse) | Clusters and nodes |
| [**TS3**](troubleshooting/ts03-cordon-drain-uncordon.md) | Cordon, drain, uncordon — against a PDB and a DaemonSet. Make `drain` refuse, say exactly why, then get it through legitimately | Reflex | **Pinned** | [`workhorse`](../../strands/lab-topologies.md#workhorse) | Clusters and nodes |
| [**TS4**](troubleshooting/ts04-a-node-is-gone.md) | A node is simply gone. Read the `NotReady` taint, the eviction timers and what became of its pods; bring it back and watch it rejoin | Reflex | Core | [`workhorse`](../../strands/lab-topologies.md#workhorse) | Clusters and nodes |
| [**TS5**](troubleshooting/ts05-broken-static-pod.md) | A static pod is broken and `kubectl` is therefore dead. Diagnose from `crictl ps -a`, `crictl logs` and `journalctl -u kubelet` alone | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Cluster components |
| [**TS6**](troubleshooting/ts06-scheduler-or-controller-manager.md) | `kube-scheduler` or `kube-controller-manager` is down. Name which **from the symptom** before opening a manifest | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Cluster components |
| [**TS7**](troubleshooting/ts07-tls-401-403.md) | The API server is up and refusing you. Separate a TLS failure from a 401 from a 403; then check and rotate the expiring certificate | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Cluster components |
| [**TS8**](troubleshooting/ts08-coredns-down.md) | CoreDNS is down or its Corefile is wrong. Diagnose it from cluster-wide symptoms rather than from the Deployment, repair, confirm | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Cluster components |
| TS9 | Stop one control-plane member and read what the remaining two do; stop a second and read what the survivor does | Reflex | Optional | [`ha`](../../strands/lab-topologies.md#ha) | Cluster components |
| [**TS10**](troubleshooting/ts10-kubectl-top-returns-nothing.md) | `kubectl top` returns nothing, or lies. Separate not-installed from not-ready from failing-TLS-to-the-kubelet, and fix the one in front of you | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Resource usage |
| [**TS11**](troubleshooting/ts11-oomkilled.md) | A pod was OOMKilled. Prove it from exit code 137, `describe`'s Last State, the limit and the cgroup — then right-size it | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Resource usage |
| [**TS12**](troubleshooting/ts12-the-whole-logs-flag-surface.md) | The full flag surface on one pass: a named container, an init container, `--previous`, `--since`, `--tail`, `--timestamps`, and `-l` across a Deployment | Reflex | **Pinned** | [`pair`](../../strands/lab-topologies.md#pair) | Container output streams |
| [**TS13**](troubleshooting/ts13-logs-empty-app-writes-a-file.md) | `kubectl logs` is empty because the process writes to a file. Find the file, get it out of the container, and state the fix | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Container output streams |
| TS14 | Output on disk: `/var/log/pods`, `/var/log/containers`, the symlink chain to the runtime's log, rotation — and `journalctl` when the pod never started | Reflex | Optional | [`pair`](../../strands/lab-topologies.md#pair) | Container output streams |
| [**TS15**](troubleshooting/ts15-service-with-no-endpoints.md) | A Service has no endpoints. Walk selector, pod labels, readiness, and `targetPort` against the container's port name — and say which of the four it was | Reflex | **Pinned** | [`pair`](../../strands/lab-topologies.md#pair) | Services and networking |
| [**TS16**](troubleshooting/ts16-one-pod-resolves-one-does-not.md) | One pod resolves the name and another does not. Work `resolv.conf`, `ndots`, the search list and `dnsPolicy` before you blame CoreDNS | Reflex | **Pinned** | [`pair`](../../strands/lab-topologies.md#pair) | Services and networking |
| [**TS17**](troubleshooting/ts17-a-policy-you-did-not-write.md) | Traffic that should flow is silently dropped by a NetworkPolicy you did not write — usually an egress rule with no DNS carve-out. Prove it is the policy and not the app | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Services and networking |
| [**TS18**](troubleshooting/ts18-unreachable-from-off-node.md) | NodePort or Ingress unreachable from off-node. Chain it: endpoints, then kube-proxy's mode and its rules, then the node firewall, then the controller's own logs | Reflex | Core | [`pair`](../../strands/lab-topologies.md#pair) | Services and networking |
| TS19 | Pod-to-pod across nodes is slow or lossy. Find the planted `tc` qdisc or the `iptables` DROP with `tc -s qdisc show` and `iptables-save`, not by guessing | Reflex | Optional | [`workhorse`](../../strands/lab-topologies.md#workhorse) | Services and networking |
