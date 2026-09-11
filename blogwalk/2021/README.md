# 2021 — the census

53 posts, 2021-03-09 to 2021-12-22. Kubernetes 1.21, 1.22 and 1.23 are in scope, and three is the
whole year: the release cadence changed from four a year to three in July. This is **the year the
blog stopped being about the project and became about the software** — see
[the method](../README.md).

**Yield: 11 `walk`**, mid-[band](../README.md#the-budget) and the highest of any year since 2016. 31
`read`, **0 `dated`**, 11 `skip`.

**The reject rate halves, and the shape of the year explains why.** 21%, against 48%, 42%, 38%,
40%, 37%, 41% for the six years before it — the lowest of the chronological sweep and beaten only
by 2024's 19%. `meta` falls to 11 rows and 21%, its lowest share in the census, 2024's 30%
included. The mechanism is visible in the dates. In 2018, 2019 and 2020 the three busiest months
carried 46%, 44% and 43% of the year's posts; in 2021 they carry **62%**, and they are April,
August and December — the three release months, exactly. The pinned tree holds no 2021 post before
9 March and only four between then and the end of June. The blog stopped filling the quiet months
with community writing and started clustering feature posts around the release train, which is
also the shape 2024 has (65%). There are no hangout notes this year, no KubeCon recaps, no case
studies and no memorials: 42 of the 53 posts are about how the software behaves.

**The largest removal event in the archive, and it is not close.** The pin's deprecation guide
gives v1.22 twelve subsections — Webhook resources, CustomResourceDefinition, APIService,
TokenReview, SubjectAccessReview, CertificateSigningRequest, Lease, Ingress, IngressClass, RBAC
resources, PriorityClass and Storage resources. v1.16, the removal 2019's walk is built on, has
six. Every removal release *after* v1.22 put together — v1.25's seven, v1.26's two, and one each
at v1.27, v1.29 and v1.32 — comes to twelve as well. One release removed as much as the following
ten years, and it has its own post here.

**The ladder shows its whole range inside one year.** `PodSecurity` went alpha in 1.22 and stable
in 1.25: three releases, announcement to done. In the same two releases the project shipped
`MemoryQoS`, alpha from 1.22 through 1.36 and beta only at 1.37 — **fifteen releases on the first
rung**, graduating on the newest release the pin carries; `CSIVolumeHealth`, alpha from 1.21 with
no end version and no later stage recorded at all; and `GracefulNodeShutdown`, beta from 1.21 with
no stable stage, sixteen releases on. `MemoryManager` took ten releases to cross beta. 2020
produced one stationary rung and read as an anomaly. 2021 produces three, alongside the fast
graduations that make them legible, and the anomaly turns out to be the distribution.

**Self-annotation stops being an event and becomes a habit.** 2019 gave the archive its first
later-added editorial note; 2020 gave the first strikethrough. 2021 carries four, and three of
them retire something other than a version.
[PodSecurityPolicy Deprecation: Past, Present, and Future](https://kubernetes.io/blog/2021/04/06/podsecuritypolicy-deprecation-past-present-and-future/)
opens with a `{{% pageinfo %}}` **Update** saying its subject was removed in v1.25.
[Spotlight on SIG Usability](https://kubernetes.io/blog/2021/07/15/sig-usability-spotlight-2021/)
opens with a `{{< note >}}` saying the SIG has been inactive since August 2023 — an interview
annotated with the end of the group it interviews.
[A Closer Look at NSA/CISA Kubernetes Hardening Guidance](https://kubernetes.io/blog/2021/10/05/nsa-cisa-kubernetes-hardening-guidance/)
carries an Update from November 2023 pointing at version 1.2 of a guide the post reviews at 1.0:
the annotation moves the *source* on, not the post.
[Dockershim removal is coming. Are you ready?](https://kubernetes.io/blog/2021/11/12/are-you-ready-for-dockershim-removal/)
opens with a **Poll closed** alert and has both links to its survey wrapped in `<del>`.

**Several subjects left no trace.** `networking.x-k8s.io` — the API group
[Evolving Kubernetes networking with the Gateway API](https://kubernetes.io/blog/2021/04/22/evolving-kubernetes-networking-with-the-gateway-api/)
is written in — has zero occurrences at the pin; the API shipped as `gateway.networking.k8s.io/v1`,
and that rename is a walk. The other three are absences that stayed absent. `kpng`, a SIG Network
subproject with a post explaining how to write proxier backends against it, has zero occurrences;
kube-proxy still ships as kube-proxy and the backend that did arrive, nftables, arrived in tree.
`a8r.io`, a proposed annotation convention for Services, has zero. `ClusterClass` has zero, in a
tree that references Cluster API in six files. Three ideas the blog put its weight behind in one
year, none of which reached the documentation.

**`dated` is empty for the second time, and for the same reason as 2017.**
[Kubernetes-in-Kubernetes and the WEDOS PXE bootable server farm](https://kubernetes.io/blog/2021/12/22/kubernetes-in-kubernetes-and-pxe-bootable-server-farm/)
is the only candidate and it passes both tests on its face: a complete procedure, and two data
centres of bare metal underneath it. The vendor rule reaches it first and makes it a `read`. That
ordering was raised when 2017 came out empty and was left as it stood; this is the second year it
has cost the verdict its only row. `dated` remains at 11 rows in 472.

Three things in the topic tallies are worth the taxonomy's attention. **`storage` takes 9 rows and
3 `walk`s, both records for the sweep** — a year of 1.22 and 1.23 storage alphas, three of which
have since gone stable and are still observable in a single-node cluster. **`tooling` drops from 7
rows to 3 and takes zero `walk`s for the second year running**: the year's two substantial tooling
posts are about writing software, not about running a cluster, and the walk machinery has nothing
to grip. And **`ecosystem` falls again, to 2 rows and 4%** — 9%, 21%, 28%, 14%, 12%, 5%, 4% — a new
low on top of last year's low. `sched` and `etcd` are both empty.

## Census

Verdicts and topics are defined in [`../README.md`](../README.md#the-census). Every post has a
row, and a row's title always links the post — never the exercise file, so the row never
changes once written. The **Exercises** table below is the progress record.

| post | date | k8s | verdict | topic | why |
|---|---|---|---|---|---|
| [The Evolution of Kubernetes Dashboard](https://kubernetes.io/blog/2021/03/09/the-evolution-of-kubernetes-dashboard/) | 03-09 | — | `read` | `history` | The Dashboard's own six-year retrospective, written from inside the project: three rewrites, a change of framework, and the reasoning behind each. At the pin the Dashboard has one task page in the whole documentation tree. Read for the account of a component the core stopped owning; there is no cluster operation in it. |
| [PodSecurityPolicy Deprecation: Past, Present, and Future](https://kubernetes.io/blog/2021/04/06/podsecuritypolicy-deprecation-past-present-and-future/) | 04-06 | 1.21 | `read` | `security` | The deprecation announcement, and the post now carries a `{{% pageinfo %}}` **Update** on top of itself saying PodSecurityPolicy was removed in v1.25 — a post annotated with the death of its own subject. The pin's deprecation guide lists PodSecurityPolicy under the v1.25 removals, four releases after this was written. The migration it promises is the one 47 actually teaches, so the discontinuity is booked there and this reads for the reasoning. |
| [Kubernetes 1.21: Power to the Community](https://kubernetes.io/blog/2021/04/08/kubernetes-1-21-release-announcement/) | 04-08 | 1.21 | `skip` | `meta` | Release announcement. Everything in 1.21 that matters to this census — CronJob at GA, PodSecurityPolicy deprecated, graceful node shutdown to beta — has its own post below. |
| [Kubernetes 1.21: CronJob Reaches GA](https://kubernetes.io/blog/2021/04/09/kubernetes-release-1.21-cronjob-ga/) | 04-09 | 1.21 | `walk` | `api` | CronJob reaches GA on `batch/v1`, with a rewritten controller behind the `CronJobControllerV2` gate. At the pin that gate is gone from the feature-gate list entirely and the deprecation guide lists CronJob under the v1.25 removals: `batch/v1beta1` stopped being served four releases after this post. Copy the post's manifest as written and the apiserver refuses it; change one line and it runs. |
| [Introducing Suspended Jobs](https://kubernetes.io/blog/2021/04/12/introducing-suspended-jobs/) | 04-12 | 1.21 | `read` | `api` | Suspended Jobs, alpha behind `SuspendJob`. At the pin the gate is stable-then-removed and `spec.suspend` is ordinary API named in fourteen files, so the only expired part of the post is its `--feature-gates` preamble. One field and one patch is thin material for an exercise when 04 already opens the batch group. |
| [kube-state-metrics goes v2.0](https://kubernetes.io/blog/2021/04/13/kube-state-metrics-v-2-0/) | 04-13 | — | `read` | `obs` | kube-state-metrics v2.0, an out-of-tree add-on's major release, with a breaking-change list: renamed flags, dropped metrics, a new `--metric-labels-allowlist`. The pin names kube-state-metrics in four files and documents none of those flags. Read for what a metric rename costs whoever built a dashboard on it. |
| [Local Storage: Storage Capacity Tracking, Distributed Provisioning and Generic Ephemeral Volumes hit Beta](https://kubernetes.io/blog/2021/04/14/local-storage-features-go-beta/) | 04-14 | 1.21 | `read` | `storage` | Three storage features to beta in one release: capacity tracking (`CSIStorageCapacity`), distributed provisioning, and generic ephemeral volumes (`GenericEphemeralVolume`). Both gates are stable-then-removed at the pin, so every beta caveat in the post is spent. Generic ephemeral volumes already carry a 2020 exercise; what is left is a graduation announcement. |
| [Three Tenancy Models For Kubernetes](https://kubernetes.io/blog/2021/04/15/three-tenancy-models-for-kubernetes/) | 04-15 | — | `read` | `security` | Three tenancy models — namespaces, virtual control planes, a cluster per tenant — argued as a design space rather than a procedure. Nothing in it is a version, so nothing in it expired. The value is the vocabulary for the trade-off. |
| [Volume Health Monitoring Alpha Update](https://kubernetes.io/blog/2021/04/16/volume-health-monitoring-alpha-update/) | 04-16 | 1.21 | `read` | `storage` | Volume health monitoring, alpha behind `CSIVolumeHealth`. The gate's entry at the pin has `fromVersion: "1.21"`, no `toVersion`, and no later stage: five years on the first rung with no movement recorded at all. That is a finding about the ladder rather than a lab exercise — observing it needs a CSI driver that implements the health RPCs. |
| [Introducing Indexed Jobs](https://kubernetes.io/blog/2021/04/19/introducing-indexed-jobs/) | 04-19 | 1.21 | `read` | `api` | Indexed Jobs, alpha behind `IndexedJob`. At the pin the gate is removed, `completionMode: Indexed` is ordinary API in three files, and `JOB_COMPLETION_INDEX` works exactly as the post writes it. A post that aged so well it left nothing to discover. |
| [Annotating Kubernetes Services for Humans](https://kubernetes.io/blog/2021/04/20/annotating-k8s-for-humans/) | 04-20 | — | `skip` | `ecosystem` | A proposal to standardise `a8r.io/*` annotations on Services. The string `a8r.io` has zero occurrences anywhere in the pin's documentation tree: the convention was never adopted. Vendor advocacy for something that did not happen. |
| [Defining Network Policy Conformance for Container Network Interface (CNI) providers](https://kubernetes.io/blog/2021/04/20/defining-networkpolicy-conformance-cni-providers/) | 04-20 | — | `read` | `net` | Defining NetworkPolicy conformance for CNI providers, with the `cyclonus` fuzzer and a matrix of which plugin fails which case. `cyclonus` has zero occurrences at the pin. The finding survives the tool: identical NetworkPolicy YAML behaved differently on different CNIs, which is why conformance had to be defined at all. |
| [Graceful Node Shutdown Goes Beta](https://kubernetes.io/blog/2021/04/21/graceful-node-shutdown-beta/) | 04-21 | 1.21 | `read` | `nodes` | Graceful node shutdown to beta, configured with `shutdownGracePeriod` in the kubelet. At the pin the gate still reads `fromVersion: "1.21"` with no `toVersion`, no stable stage and no removal — sixteen releases on the middle rung. Second only to 09 as a stationary rung, but the observable needs a systemd inhibitor lock and a real node shutting down, which is past the lab ceiling. |
| [Evolving Kubernetes networking with the Gateway API](https://kubernetes.io/blog/2021/04/22/evolving-kubernetes-networking-with-the-gateway-api/) | 04-22 | — | `walk` | `net` | The Gateway API introduced as the successor to Ingress, in API group `networking.x-k8s.io`. That group has zero occurrences at the pin: the API shipped as `gateway.networking.k8s.io/v1`, so every kind in the post has to be re-grouped before it applies. Install the CRDs at the pin's version and diff GatewayClass, Gateway and HTTPRoute against what the post prints. |
| [Kubernetes 1.21: Metrics Stability hits GA](https://kubernetes.io/blog/2021/04/23/kubernetes-release-1.21-metrics-stability-ga/) | 04-23 | 1.21 | `read` | `obs` | The metrics stability framework at GA: `ALPHA` and `STABLE` labels on metrics, and a deprecation policy that governs them. The policy is the payload and it still holds at the pin. Reading it explains why a metric name is allowed to move; running it explains nothing. |
| [Using Finalizers to Control Deletion](https://kubernetes.io/blog/2021/05/14/using-finalizers-to-control-deletion/) | 05-14 | — | `walk` | `api` | The one 2021 post that is a tutorial first: create an object, add a finalizer, delete it, watch the deletion hang, remove the finalizer, watch it complete. The pin still documents the same semantics at `concepts/overview/working-with-objects/finalizers.md`, so the commands run verbatim five years on. This year's proof that some of the archive did not move. |
| [Writing a Controller for Pod Labels](https://kubernetes.io/blog/2021/06/21/writing-a-controller-for-pod-labels/) | 06-21 | — | `read` | `tooling` | Writing a controller for Pod labels: a full controller-runtime walkthrough with a mutating webhook and certificate wiring. Substantial and still conceptually correct, but the Go module versions are five years stale and the exercise it implies is *write a controller*, not *run a cluster*. Read for the shape of a reconcile loop. |
| [Announcing Kubernetes Community Group Annual Reports](https://kubernetes.io/blog/2021/06/28/Announcing-Kubernetes-Community-Group-Annual-Reports/) | 06-28 | — | `skip` | `meta` | Announcement that community groups now file annual reports. Governance process. |
| [Kubernetes API and Feature Removals In 1.22: Here’s What You Need To Know](https://kubernetes.io/blog/2021/07/14/upcoming-changes-in-kubernetes-1-22/) | 07-14 | 1.22 | `walk` | `api` | The removal notice for the largest removal event in the archive. The pin's deprecation guide gives v1.22 twelve subsections — Webhook resources, CustomResourceDefinition, APIService, TokenReview, SubjectAccessReview, CertificateSigningRequest, Lease, Ingress, IngressClass, RBAC resources, PriorityClass and Storage resources — exactly as many as every removal release after it put together, and twice the six of v1.16. None of them overlaps the `extensions/v1beta1` workloads that 2019's removal walk covers. Take each row of the post's table, apply the old apiVersion at the pin, and record the refusal. |
| [Spotlight on SIG Usability](https://kubernetes.io/blog/2021/07/15/sig-usability-spotlight-2021/) | 07-15 | — | `skip` | `meta` | SIG Usability spotlight. The post now carries a `{{< note >}}` saying the SIG was deprecated and has been inactive since August 2023 — an interview whose subject is the thing that ended. Kept in the census as evidence of self-annotation; skipped as a process interview, the same call as 2020's SIG-Windows spotlight. |
| [Kubernetes Release Cadence Change: Here’s What You Need To Know](https://kubernetes.io/blog/2021/07/20/new-kubernetes-release-cadence/) | 07-20 | — | `skip` | `meta` | The move from four releases a year to three. Process change, and the reason this year's census carries three release announcements where 2020's carried four. |
| [Updating NGINX-Ingress to use the stable Ingress API](https://kubernetes.io/blog/2021/07/26/update-with-ingress-nginx/) | 07-26 | — | `read` | `net` | Porting ingress-nginx off `extensions/v1beta1` and onto the stable Ingress API ahead of the v1.22 removal. A useful migration note, but the discontinuity it prepares for belongs to 19, and the controller's own versions have moved five years on. |
| [Roorkee robots, releases and racing: the Kubernetes 1.21 release interview](https://kubernetes.io/blog/2021/07/29/kubernetes-1-21-release-interview/) | 07-29 | 1.21 | `read` | `meta` | The 1.21 release lead on the release, on the record. `read` on the maintainer-interview rule, as with every release interview from 2018 onward. |
| [Kubernetes 1.22: Reaching New Peaks](https://kubernetes.io/blog/2021/08/04/kubernetes-1-22-release-announcement/) | 08-04 | 1.22 | `skip` | `meta` | Release announcement for the release that owns this year's removal event and four of its walks. |
| [Kubernetes 1.22: Server Side Apply moves to GA](https://kubernetes.io/blog/2021/08/06/server-side-apply-ga/) | 08-06 | 1.22 | `read` | `api` | Server Side Apply at GA. At the pin the gate is stable from 1.22 and then removed, so this is simply how `kubectl apply --server-side` works now. Field management and conflict forcing already carry a 2020 exercise; this is the graduation notice for it. |
| [New in Kubernetes v1.22: alpha support for using swap memory](https://kubernetes.io/blog/2021/08/09/run-nodes-with-swap-alpha/) | 08-09 | 1.22 | `walk` | `nodes` | Alpha swap support, configured with `swapBehavior: UnlimitedSwap` in the kubelet. At the pin `UnlimitedSwap` has zero occurrences: the accepted values are `LimitedSwap` and `NoSwap`, and `NodeSwap` went beta off-by-default at 1.28, beta on at 1.30 and stable at 1.34. The post's central configuration line is the one thing in it that no longer parses — set it at the pin and read the kubelet's refusal. |
| [Kubernetes 1.22: CSI Windows Support (with CSI Proxy) reaches GA](https://kubernetes.io/blog/2021/08/09/csi-windows-support-with-csi-proxy-reaches-ga/) | 08-09 | 1.22 | `read` | `storage` | CSI support on Windows nodes at GA, by way of csi-proxy. The pin mentions `csi-proxy` in a single file. Windows nodes are past the lab ceiling and the post is an announcement rather than a procedure. |
| [Kubernetes Memory Manager moves to beta](https://kubernetes.io/blog/2021/08/11/kubernetes-1-22-feature-memory-manager-moves-to-beta/) | 08-11 | 1.22 | `read` | `nodes` | Memory Manager to beta: NUMA-aware memory pinning alongside the CPU manager. At the pin the gate is beta from 1.22 and stable only at 1.32 — ten releases on the middle rung, and still listed rather than removed. Observing it needs a node with more than one NUMA domain. |
| [Alpha in v1.22: Windows HostProcess Containers](https://kubernetes.io/blog/2021/08/16/windows-hostprocess-containers/) | 08-16 | 1.22 | `read` | `nodes` | Windows HostProcess containers, alpha in 1.22. At the pin the gate is stable from 1.26 and removed. Windows nodes are past the lab ceiling. |
| [Enable seccomp for all workloads with a new v1.22 alpha feature](https://kubernetes.io/blog/2021/08/25/seccomp-default/) | 08-25 | 1.22 | `walk` | `security` | `SeccompDefault`: one kubelet flag that moves every workload on the node from `Unconfined` to `RuntimeDefault`. The gate went stable at 1.27 and left the list, but `--seccomp-default` is a live kubelet flag at the pin, named in three files. Turn it on in a single-node cluster's kubelet configuration and diff a Pod's effective seccomp profile before and after; the entire change is observable in one cluster. |
| [Minimum Ready Seconds for StatefulSets](https://kubernetes.io/blog/2021/08/27/minreadyseconds-statefulsets/) | 08-27 | 1.22 | `read` | `api` | `minReadySeconds` for StatefulSets, alpha in 1.22. At the pin the gate is stable from 1.25 and removed, and the field is ordinary API in thirteen files. One field, one behaviour, and the behaviour never changed. |
| [Kubernetes 1.22: A New Design for Volume Populators](https://kubernetes.io/blog/2021/08/30/volume-populators-redesigned/) | 08-30 | 1.22 | `read` | `storage` | Volume populators redesigned around `AnyVolumeDataSource` and a registry of `VolumeDataSource` kinds — the second design for the same problem. The gate reached stable at 1.33, so the redesign landed, but exercising it needs a populator controller and a CSI driver. Read for why the first design had to be withdrawn. |
| [Alpha in Kubernetes v1.22: API Server Tracing](https://kubernetes.io/blog/2021/09/03/api-server-tracing/) | 09-03 | 1.22 | `read` | `obs` | API server tracing, alpha in 1.22, exported to an OpenTelemetry collector. The gate is beta from 1.27 and stable at 1.34, so the feature arrived intact. Running it means standing a collector next to the apiserver; the post's value is the argument for tracing a control plane at all. |
| [Introducing Single Pod Access Mode for PersistentVolumes](https://kubernetes.io/blog/2021/09/13/read-write-once-pod-access-mode-alpha/) | 09-13 | 1.22 | `walk` | `storage` | `ReadWriteOncePod`: the access mode that finally means one Pod, after `ReadWriteOnce` had meant one node since 2015. Alpha here, stable at 1.29, gate removed, and the mode is named in thirteen files at the pin. Two Pods and one claim is the whole experiment, and the second Pod's refusal is the payload. |
| [Spotlight on SIG Node](https://kubernetes.io/blog/2021/09/27/sig-node-spotlight-2021/) | 09-27 | — | `skip` | `meta` | SIG Node spotlight: how the SIG is organised, what its subprojects are, how to join. Process rather than engineering, and skipped on the same reading as 2020's SIG-Windows spotlight. |
| [How to Handle Data Duplication in Data-Heavy Kubernetes Environments](https://kubernetes.io/blog/2021/09/29/how-to-handle-data-duplication-in-data-heavy-kubernetes-environments/) | 09-29 | — | `read` | `storage` | A vendor argument for hardware-offloaded snapshots instead of copying volumes through compute. It names the alternative it rejects — download to compute, push back to the provider — so it reads under the vendor rule rather than skipping. It never becomes a walk. |
| [A Closer Look at NSA/CISA Kubernetes Hardening Guidance](https://kubernetes.io/blog/2021/10/05/nsa-cisa-kubernetes-hardening-guidance/) | 10-05 | — | `read` | `security` | SIG Security going through the NSA/CISA hardening guidance section by section, adding what the guidance left out. The post now carries a `{{% pageinfo %}}` Update from November 2023 pointing at version 1.2 of a guide this post reviews at 1.0 — the annotation moves the *source* on, not the post. Argument, not procedure. |
| [Introducing ClusterClass and Managed Topologies in Cluster API](https://kubernetes.io/blog/2021/10/08/capi-clusterclass-and-managed-topologies/) | 10-08 | — | `read` | `tooling` | ClusterClass and managed topologies in Cluster API: a cluster becomes a templated object with a class behind it. `ClusterClass` has zero occurrences in the pin's documentation and Cluster API appears in six files as a reference to an out-of-tree project. Read for the idea; it is not a k8s-academy lab. |
| [Use KPNG to Write Specialized kube-proxiers](https://kubernetes.io/blog/2021/10/18/use-kpng-to-write-specialized-kube-proxiers/) | 10-18 | — | `read` | `net` | KPNG: kube-proxy refactored into a library so you can write your own proxier backend. `kpng` has zero occurrences at the pin — five years on, kube-proxy still ships as kube-proxy, and the new backend that did land, nftables, landed in tree. Read as a design that lost. |
| [Announcing the 2021 Steering Committee Election Results](https://kubernetes.io/blog/2021/11/08/steering-committee-results-2021/) | 11-08 | — | `skip` | `meta` | Steering Committee election results. |
| [Non-root Containers And Devices](https://kubernetes.io/blog/2021/11/09/non-root-containers-and-devices/) | 11-09 | — | `read` | `nodes` | Why a device node's ownership defeats `runAsNonRoot`, and the device-plugin path around it. The problem is real at the pin and the explanation is good, but reproducing it needs a device to plug in. |
| [Dockershim removal is coming. Are you ready?](https://kubernetes.io/blog/2021/11/12/are-you-ready-for-dockershim-removal/) | 11-12 | — | `skip` | `meta` | The dockershim readiness survey. Both links to the form are wrapped in `<del>`, and the post opens with a `{{% alert %}}` titled **Poll closed**. A call to action whose action is over. |
| [Quality-of-Service for Memory Resources](https://kubernetes.io/blog/2021/11/26/qos-memory-resources/) | 11-26 | 1.22 | `walk` | `nodes` | Memory QoS: requests and limits mapped onto cgroup v2's `memory.min` and `memory.high` instead of being scheduling hints only. At the pin `MemoryQoS` is alpha from 1.22 through 1.36 and beta only at 1.37 — fifteen releases on the first rung, graduating on the newest release the pin carries. Enable the gate on a cgroup v2 node and read the values the kubelet writes into the Pod's cgroup; the slowest climb in the archive is observable in one `cat`. |
| [Contribution, containers and cricket: the Kubernetes 1.22 release interview](https://kubernetes.io/blog/2021/12/01/kubernetes-1.22-release-interview/) | 12-01 | 1.22 | `read` | `meta` | The 1.22 release lead on the release that removed twelve API groups. `read` on the maintainer-interview rule. |
| [Kubernetes 1.23: The Next Frontier](https://kubernetes.io/blog/2021/12/07/kubernetes-1-23-release-announcement/) | 12-07 | 1.23 | `skip` | `meta` | Release announcement. It deprecates FlexVolume, which the pin still names in fourteen files, and deprecates the klog-specific flags. |
| [Kubernetes 1.23: Dual-stack IPv4/IPv6 Networking Reaches GA](https://kubernetes.io/blog/2021/12/08/dual-stack-networking-ga/) | 12-08 | 1.23 | `read` | `net` | Dual-stack IPv4/IPv6 at GA, seven releases after the alpha. The gate is stable from 1.23 and removed at the pin. Exercising dual-stack needs a CNI and a host network configured for both families; the post is the announcement of a migration that had already finished. |
| [Kubernetes 1.23: Pod Security Graduates to Beta](https://kubernetes.io/blog/2021/12/09/pod-security-admission-beta/) | 12-09 | 1.23 | `walk` | `security` | Pod Security admission to beta — the replacement whose arrival 02 promises. At the pin the gate is stable from 1.25 and removed, the configuration API is `pod-security.admission.config.k8s.io/v1`, and the three namespace labels are ordinary API. Label a namespace `restricted`, apply a Pod that violates the standard, and read the rejection: the whole PodSecurityPolicy migration collapses into one exercise. |
| [Kubernetes 1.23: Kubernetes In-Tree to CSI Volume Migration Status Update](https://kubernetes.io/blog/2021/12/10/storage-in-tree-to-csi-migration-status-update/) | 12-10 | 1.23 | `read` | `storage` | A status table for in-tree to CSI migration, driver by driver, taken mid-flight. Every row of it has since resolved. Read for what a five-year migration costs, not for anything to run. |
| [Kubernetes 1.23: Prevent PersistentVolume leaks when deleting out of order](https://kubernetes.io/blog/2021/12/15/kubernetes-1-23-prevent-persistentvolume-leaks-when-deleting-out-of-order/) | 12-15 | 1.23 | `walk` | `storage` | Deleting a PersistentVolume before its claim used to leak the backing volume. `HonorPVReclaimPolicy` fixes it with a finalizer; at the pin the gate is stable from 1.33 and removed, and `external-provisioner.volume.kubernetes.io/finalizer` appears in four files. Delete in both orders on a cluster that has the fix and the difference is a finalizer you can watch appear. |
| [Kubernetes 1.23: StatefulSet PVC Auto-Deletion (alpha)](https://kubernetes.io/blog/2021/12/16/kubernetes-1-23-statefulset-pvc-auto-deletion/) | 12-16 | 1.23 | `walk` | `storage` | `persistentVolumeClaimRetentionPolicy` on StatefulSets, with `whenDeleted` and `whenScaled`. Alpha here, stable at 1.32, and the field is documented in five files at the pin. Scale a StatefulSet down under each policy and count the claims left behind; the default is still the 2021 behaviour, which is the part worth finding out by hand. |
| [What's new in Security Profiles Operator v0.4.0](https://kubernetes.io/blog/2021/12/17/security-profiles-operator/) | 12-17 | — | `skip` | `ecosystem` | Release notes for an out-of-tree operator. |
| [Using Admission Controllers to Detect Container Drift at Runtime](https://kubernetes.io/blog/2021/12/21/admission-controllers-for-container-drift/) | 12-21 | — | `read` | `security` | A vendor engineering post on catching `kubectl exec` drift with a validating webhook. It states the decision and the alternatives it rejected — audit logs, runtime agents — so it reads under the vendor rule. Its own tooling, `kube-applier`, has zero occurrences at the pin. |
| [Kubernetes-in-Kubernetes and the WEDOS PXE bootable server farm](https://kubernetes.io/blog/2021/12/22/kubernetes-in-kubernetes-and-pxe-bootable-server-farm/) | 12-22 | — | `read` | `tooling` | Kubernetes running inside Kubernetes, with compute nodes PXE-booted from the cluster that manages them. The most complete procedure published all year and the only 2021 post that walks a reader end to end — but it wants two data centres, and the vendor rule reaches it before the `dated` tests do. The second year that rule order has cost `dated` its only candidate. |

## Exercises

Eleven `walk` verdicts, numbered in publication order. Three are written and eight are *pending* — an
authoring ticket's to claim. The rubric they are authored against was ratified in
[#57](https://github.com/k3ii/k8s-academy/issues/57).

| # | exercise | state |
|---|---|---|
| 01 | [The gate that was removed for winning](01-kubernetes-release-1-21-cronjob-ga.md) | written |
| 02 | [Re-grouped, and refused anyway](02-evolving-kubernetes-networking-with-the-gateway-api.md) | written |
| 03 | [The delete that hangs, exactly as promised](03-using-finalizers-to-control-deletion.md) | written |
| 04 | Twelve removals in one release, one manifest at a time | pending |
| 05 | The setting the kubelet no longer has a word for | pending |
| 06 | One flag, and every Pod's profile changes | pending |
| 07 | Once per node, and then once per Pod | pending |
| 08 | Fifteen releases on the first rung | pending |
| 09 | Three labels where a whole API used to be | pending |
| 10 | Delete them in the wrong order and the disk stays | pending |
| 11 | The claims that used to outlive the set | pending |
