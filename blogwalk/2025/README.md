# 2025 — the census

78 posts, 2025-01-21 to 2025-12-31. Kubernetes 1.33, 1.34 and 1.35 are in scope, with one 1.32
feature post arriving in March. It ties 2023 as the second-largest year censused, behind 2016's
90 — see [the method](../README.md).

**Yield: 12 `walk`**, upper-[band](../README.md#the-budget). 50 `read`, 2 `dated`, 14 `skip`.

**The first year the blog is mostly not about itself.** `meta` takes 12 rows and 15%, a new floor
under 2023's 17%, and this is the first year the census has reached whose largest topic is about
how the software behaves: `nodes` takes 19 rows and 24%. `meta` led every censused year but 2017,
where `ecosystem` did. The reject rate is 18%, against 48%, 42%, 38%, 40%, 37%, 41%, 21%, 17%, 15%
and 19% for the years already censused. What replaced the community writing is release writing: 49
of the 78 titles name a Kubernetes version, 63% — the highest share of any year in the corpus,
against 5% in 2015 and 32% in 2021. The three busiest months carry 50%, September alone carrying
17 posts.

**The blog spends the year answering the archive.** Twenty rows — better than one in four — point
back at an exercise or a row an earlier year already owns: in-place Pod resize twice, user
namespaces, image volumes, the reclaim policy, VolumeAttributesClass, fine-grained supplemental
groups twice, swap, backoff limit per index, and the Gateway API group-version behind both of this
year's Gateway posts. This is the redundancy filter doing most of the triage, and it is what a year
this close to the pin looks like: the features are the same features, three or four rungs further
up.

**Half the feature-gate directory documents gates that are gone.** Every census since 2016 has
read a gate's fate off its stage table: a last stage with a `toVersion` means retired, one without
means still current. The pin carries the answer directly. 230 of the 488 files declare
`removed: true` in their frontmatter, against 257 that do not, and the two readings agree on 486
of the 487 files with stage tables. The single exception, `DynamicProvisioningScheduling`, is
marked removed while its last stage — `deprecated`, from 1.12 — never closes, so the inference
alone would call a gate retired in 2018 still live. The archive has been right by nine years of
luck and one convention.

**An API two releases old and already two versions on.**
[Kubernetes v1.35: Introducing Workload Aware Scheduling](https://kubernetes.io/blog/2025/12/29/kubernetes-v1-35-introducing-workload-aware-scheduling/)
is the last feature post of the year and the fastest-moving subject in the archive. It is written
against `scheduling.k8s.io/v1alpha1`; the pin serves `Workload` at `v1alpha2` and adds a runtime
sibling, `CompositePodGroup`, at `v1alpha3`. Of the three gates the post names, `GangScheduling`
carries `removed: true` and the note "removed in 1.37 and merged together with the
`GenericWorkload` feature gate"; `GenericWorkload` itself reaches beta at 1.37 with
`defaultValue: false`, so it is beta and still off. Five gates the post never mentions —
`CompositePodGroup`, `PodGroupPreemptionPolicy`, `TopologyAwareWorkloadScheduling`,
`WorkloadWithJob` and `DRAWorkloadResourceClaims` — did not exist when it was published. Two
releases is enough for a gate to be born, promoted and deleted.

**A third instrument: the tree keeps a redirect table.** `static/_redirects.base` holds 449
permanent redirects, one per documentation path the project has moved. The Endpoints deprecation
post is the first census row to need it: the API reference has left
`kubernetes-api/service-resources/` for `core/`, `discovery/` and `networking/`, five redirects
cover the move, and seven English docs pages still write the old path. Every earlier year that
found a link pointing somewhere the tree no longer has could have checked here first.

**A backend that cannot be switched off, and is still not the default.** `NFTablesProxyMode` is
stable and `locked: true` from 1.33, so at the pin the gate will not turn it off. `--proxy-mode`
still documents `iptables` as the Linux default, four releases later, exactly as
[NFTables mode for kube-proxy](https://kubernetes.io/blog/2025/02/28/nftables-kube-proxy/)
predicted it would. `DynamicResourceAllocation` takes the same pair of rungs a release apart:
stable with `locked: false` at 1.34, stable and locked at 1.35.

**Ingress NGINX leaves the documentation, not just the ecosystem.**
[Ingress NGINX Retirement: What You Need to Know](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/)
promises that existing deployments keep working and installation artifacts stay available. At the
pin the string `ingress-nginx` appears in zero files under `content/en/docs`, and the ingress
controller list the post sends readers to lists F5's commercial NGINX product and no
community one. 2022 spent an exercise on a registry that stopped answering; this is the same
shape, applied to a controller most clusters were running.

**Topics.** `nodes` 19, `meta` 12, `storage` 9, `security` 8, `api` 6, `sched` 6, `net` 5,
`ecosystem` 4, `tooling` 4, `obs` 3, `etcd` 2. `history` takes no row, as in 2020 — the year has
no retrospective in it at all. Walks: `nodes` 3, `net` 2, `sched` 2, `api` 1, `obs` 1,
`security` 1, `storage` 1, `tooling` 1.

## Census

Verdicts and topics are defined in [`../README.md`](../README.md#the-census). Every post has a
row, and a row's title always links the post — never the exercise file, so the row never
changes once written. The **Exercises** table below is the progress record.

| post | date | k8s | verdict | topic | why |
|---|---|---|---|---|---|
| [Spotlight on SIG Architecture: Enhancements](https://kubernetes.io/blog/2025/01/21/sig-architecture-enhancements/) | 01-21 | — | `skip` | `meta` | SIG Architecture's enhancements subproject describes its own process. Class-wide `skip` for SIG spotlights. |
| [The Cloud Controller Manager Chicken and Egg Problem](https://kubernetes.io/blog/2025/02/14/cloud-controller-manager-chicken-egg-problem/) | 02-14 | — | `read` | `nodes` | A cloud controller manager needs a Node to run on, and the Node needs the CCM to be initialised. The post names the `node.cloudprovider.kubernetes.io/uninitialized` taint and the tolerations that break the cycle. The in-tree-to-external migration itself is 2023's exercise 11. |
| [NFTables mode for kube-proxy](https://kubernetes.io/blog/2025/02/28/nftables-kube-proxy/) | 02-28 | 1.33 | `walk` | `net` | The nftables backend goes stable in 1.33 and its gate is locked from that release, so it can no longer be switched off. `--proxy-mode` still defaults to `iptables` at the pin, four releases later, and `kind` can start a cluster in either mode. |
| [Spotlight on SIG etcd](https://kubernetes.io/blog/2025/03/04/sig-etcd-spotlight/) | 03-04 | — | `skip` | `meta` | SIG etcd formed in 2024 and describes its charter. Class-wide `skip` for SIG spotlights. |
| [Spotlight on SIG Apps](https://kubernetes.io/blog/2025/03/12/sig-apps-spotlight-2025/) | 03-12 | — | `skip` | `meta` | SIG Apps describes its scope and meetings. Class-wide `skip` for SIG spotlights. |
| [Introducing JobSet](https://kubernetes.io/blog/2025/03/23/introducing-jobset/) | 03-23 | — | `read` | `ecosystem` | JobSet is a `sigs.k8s.io` API for multi-template batch workloads. It argues why plain Job could not carry the leader-follower shape, which earns a `read` under the ecosystem rule. |
| [Ingress-nginx CVE-2025-1974: What You Need to Know](https://kubernetes.io/blog/2025/03/24/ingress-nginx-CVE-2025-1974/) | 03-24 | — | `read` | `security` | A CVE announcement with a mitigation list. It documents the decision to disable the admission controller and what that costs. |
| [Fresh Swap Features for Linux Users in Kubernetes 1.32](https://kubernetes.io/blog/2025/03/25/swap-linux-improvements/) | 03-25 | 1.32 | `read` | `nodes` | Swap gained `LimitedSwap` accounting and per-QoS behaviour in 1.32. 2023's exercise 08 already carries the swap ladder and the gate that had to be asked for. |
| [Kubernetes v1.33 sneak peek](https://kubernetes.io/blog/2025/03/26/kubernetes-v1-33-upcoming-changes/) | 03-26 | 1.33 | `skip` | `meta` | A pre-release preview of 1.33. Class-wide `skip` for sneak peeks. |
| [Introducing kube-scheduler-simulator](https://kubernetes.io/blog/2025/04/07/introducing-kube-scheduler-simulator/) | 04-07 | — | `read` | `tooling` | `kube-scheduler-simulator` replays scheduling decisions without a cluster. Useful, but nothing in it is a discontinuity between the post and the pin. |
| [Kubernetes Multicontainer Pods: An Overview](https://kubernetes.io/blog/2025/04/22/multi-container-pods-overview/) | 04-22 | — | `read` | `nodes` | An overview of sidecar, ambassador and adapter patterns. 2015's exercise 05 already carries the pattern-to-API-field arc. |
| [Kubernetes v1.33: Octarine](https://kubernetes.io/blog/2025/04/23/kubernetes-v1-33-release/) | 04-23 | 1.33 | `skip` | `meta` | Release announcement. Class-wide `skip`. |
| [Kubernetes v1.33: Continuing the transition from Endpoints to EndpointSlices](https://kubernetes.io/blog/2025/04/24/endpoints-deprecation/) | 04-24 | 1.33 | `walk` | `net` | The Endpoints API is deprecated in 1.33 and the API server returns a warning header naming its replacement. At the pin the Go doc comment still reads `Deprecated: This API is deprecated in v1.33+`, and the reference page has moved out of `service-resources/` — a move that survives only as a 301 in the tree's redirect table. |
| [Kubernetes v1.33: User Namespaces enabled by default!](https://kubernetes.io/blog/2025/04/25/userns-enabled-by-default/) | 04-25 | 1.33 | `read` | `security` | `UserNamespacesSupport` is beta and on by default from 1.33, stable and locked from 1.36. 2022's exercise 10 and 2024's exercise 02 both carry it. |
| [Kubernetes v1.33: HorizontalPodAutoscaler Configurable Tolerance](https://kubernetes.io/blog/2025/04/28/kubernetes-v1-33-hpa-configurable-tolerance/) | 04-28 | 1.33 | `read` | `sched` | `HPAConfigurableTolerance` lets a HorizontalPodAutoscaler set its own tolerance instead of the cluster-wide 10%. Alpha here, stable and locked at 1.37. |
| [Kubernetes v1.33: Image Volumes graduate to beta!](https://kubernetes.io/blog/2025/04/29/kubernetes-v1-33-image-volume-beta/) | 04-29 | 1.33 | `read` | `nodes` | `ImageVolume` reaches beta but stays off by default until 1.35. That gap is exactly 2024's exercise 07. |
| [Kubernetes v1.33: Storage Capacity Scoring of Nodes for Dynamic Provisioning (alpha)](https://kubernetes.io/blog/2025/04/30/kubernetes-v1-33-storage-capacity-scoring-feature/) | 04-30 | 1.33 | `read` | `storage` | `StorageCapacityScoring` scores nodes by remaining capacity instead of only filtering. Alpha here; beta at 1.37, four releases later. |
| [Kubernetes v1.33: New features in DRA](https://kubernetes.io/blog/2025/05/01/kubernetes-v1-33-dra-updates/) | 05-01 | 1.33 | `read` | `sched` | Driver-owned taints, prioritised lists and admin access in DRA. Superseded by the GA post at row 45. |
| [Kubernetes v1.33: Mutable CSI Node Allocatable Count](https://kubernetes.io/blog/2025/05/02/kubernetes-1-33-mutable-csi-node-allocatable-count/) | 05-02 | 1.33 | `read` | `storage` | CSI drivers can update a node's attachable volume count while it runs. Alpha here; row 53 is the beta post. |
| [Kubernetes v1.33: Prevent PersistentVolume Leaks When Deleting out of Order graduates to GA](https://kubernetes.io/blog/2025/05/05/kubernetes-v1-33-prevent-persistentvolume-leaks-when-deleting-out-of-order-graduate-to-ga/) | 05-05 | 1.33 | `read` | `storage` | `HonorPVReclaimPolicy` goes GA. 2021's exercise 10 and 2024's exercise 06 both carry the out-of-order deletion. |
| [Kubernetes v1.33: Fine-grained SupplementalGroups Control Graduates to Beta](https://kubernetes.io/blog/2025/05/06/kubernetes-v1-33-fine-grained-supplementalgroups-control-beta/) | 05-06 | 1.33 | `read` | `security` | `supplementalGroupsPolicy: Strict` stops the container runtime silently merging the image's `/etc/group` entries. 2024's exercise 12 carries it; row 75 is the GA post. |
| [Kubernetes v1.33: From Secrets to Service Accounts: Kubernetes Image Pulls Evolved](https://kubernetes.io/blog/2025/05/07/kubernetes-v1-33-wi-for-image-pulls/) | 05-07 | 1.33 | `read` | `security` | Kubelet credential providers can exchange a workload's service account token for registry credentials. Row 47 is the beta post with the breaking change. |
| [Kubernetes 1.33: Volume Populators Graduate to GA](https://kubernetes.io/blog/2025/05/08/kubernetes-v1-33-volume-populators-ga/) | 05-08 | 1.33 | `read` | `storage` | `AnyVolumeDataSource` goes stable, so any custom resource can be a PVC's `dataSourceRef`. 2023's row on cross-namespace data sources is the alpha end of the same arc. |
| [Kubernetes v1.33: Streaming List responses](https://kubernetes.io/blog/2025/05/09/kubernetes-v1-33-streaming-list-responses/) | 05-09 | 1.33 | `read` | `api` | List responses are encoded item by item instead of buffered whole. `StreamingCollectionEncodingToJSON` is stable and locked from 1.34 — nothing left to switch. |
| [Kubernetes v1.33: Image Pull Policy the way you always thought it worked!](https://kubernetes.io/blog/2025/05/12/kubernetes-v1-33-ensure-secret-pulled-images-alpha/) | 05-12 | 1.33 | `walk` | `security` | Before 1.33 a Pod with `imagePullPolicy: IfNotPresent` could run any image already cached on the node, whether or not its own secret would have authorised the pull. The gate that closes a ten-year-old hole is alpha here and on by default from 1.35. |
| [Kubernetes v1.33: Job's Backoff Limit Per Index Goes GA](https://kubernetes.io/blog/2025/05/13/kubernetes-v1-33-jobs-backoff-limit-per-index-goes-ga/) | 05-13 | 1.33 | `read` | `api` | `JobBackoffLimitPerIndex` goes GA and the gate is locked from 1.33. 2023's row on the alpha is the other end. |
| [Kubernetes v1.33: Updates to Container Lifecycle](https://kubernetes.io/blog/2025/05/14/kubernetes-v1-33-updates-to-container-lifecycle/) | 05-14 | 1.33 | `walk` | `nodes` | `ContainerStopSignals` lets a Pod override SIGTERM per container. It is the year's clearest example of a subject still alpha at the pin: alpha from 1.33 with no end version, five releases on. |
| [Kubernetes 1.33: Job's SuccessPolicy Goes GA](https://kubernetes.io/blog/2025/05/15/kubernetes-1-33-jobs-success-policy-goes-ga/) | 05-15 | 1.33 | `read` | `api` | `.spec.successPolicy` lets an indexed Job succeed without every index succeeding. Gate stable and locked from 1.33. |
| [Announcing etcd v3.6.0](https://kubernetes.io/blog/2025/05/15/announcing-etcd-3.6/) | 05-15 | — | `read` | `etcd` | The first etcd minor release since 3.5.0 in June 2021, mirrored from the etcd blog. Row 73 is the upgrade hazard that followed. |
| [Kubernetes v1.33: In-Place Pod Resize Graduated to Beta](https://kubernetes.io/blog/2025/05/16/kubernetes-v1-33-in-place-pod-resize-beta/) | 05-16 | 1.33 | `read` | `nodes` | In-place Pod resize reaches beta. 2023's exercise 07 carries the resize; row 72 is the GA post. |
| [Gateway API v1.3.0: Advancements in Request Mirroring, CORS, Gateway Merging, and Retry Budgets](https://kubernetes.io/blog/2025/06/02/gateway-api-v1-3/) | 06-02 | — | `read` | `net` | Percentage-based request mirroring to Standard, plus CORS, gateway merging and retry budgets as experimental. 2021's Gateway API exercise carries the API itself. |
| [Start Sidecar First: How To Avoid Snags](https://kubernetes.io/blog/2025/06/03/start-sidecar-first/) | 06-03 | — | `walk` | `nodes` | A native sidecar that has started is not a sidecar that is ready, and the main container does not wait for it. The post is a walkthrough of the ordering traps left after 2023's exercise 09 made sidecars an init container with `restartPolicy: Always`. |
| [Introducing Gateway API Inference Extension](https://kubernetes.io/blog/2025/06/05/introducing-gateway-api-inference-extension/) | 06-05 | — | `read` | `net` | An Inference Extension for Gateway API that routes by model identity and request criticality. Needs model servers to be more than a manifest read. |
| [Enhancing Kubernetes Event Management with Custom Aggregation](https://kubernetes.io/blog/2025/06/10/enhancing-kubernetes-event-management-custom-aggregation/) | 06-10 | — | `read` | `obs` | Events are dropped after an hour and correlated by nothing. The post builds an aggregator in Python; the discontinuity is in the retention default, not the code. |
| [Changes to Kubernetes Slack](https://kubernetes.io/blog/2025/06/16/changes-to-kubernetes-slack/) | 06-16 | — | `skip` | `meta` | Slack workspace administration. No Kubernetes content. |
| [Image Compatibility In Cloud Native Environments](https://kubernetes.io/blog/2025/06/25/image-compatibility-in-cloud-native-environments/) | 06-25 | — | `read` | `nodes` | Node Feature Discovery gains an image compatibility spec, so an image can declare the kernel and driver features it needs. The spec validates anywhere; only its subject needs the hardware. |
| [Navigating Failures in Pods With Devices](https://kubernetes.io/blog/2025/07/03/navigating-failures-in-pods-with-devices/) | 07-03 | — | `read` | `nodes` | A conference talk written up: how Pods with GPUs fail, and which of those failures Kubernetes can see. A survey, not a walkthrough. |
| [Post-Quantum Cryptography in Kubernetes](https://kubernetes.io/blog/2025/07/18/pqc-in-k8s/) | 07-18 | — | `read` | `security` | Kubernetes inherits hybrid post-quantum key exchange from its Go toolchain rather than choosing it. The post's own finding is that no Kubernetes decision was involved. |
| [Kubernetes v1.34 Sneak Peek](https://kubernetes.io/blog/2025/07/28/kubernetes-v1-34-sneak-peek/) | 07-28 | 1.34 | `skip` | `meta` | A pre-release preview of 1.34. Class-wide `skip` for sneak peeks. |
| [Introducing Headlamp AI Assistant](https://kubernetes.io/blog/2025/08/07/introducing-headlamp-ai-assistant/) | 08-07 | — | `skip` | `ecosystem` | A plugin announcement for a UI project. No decision documented and no alternative weighed. |
| [Tuning Linux Swap for Kubernetes: A Deep Dive](https://kubernetes.io/blog/2025/08/19/tuning-linux-swap-for-kubernetes-a-deep-dive/) | 08-19 | 1.34 | `dated` | `nodes` | A walkthrough of `swappiness`, `min_free_kbytes` and `watermark_scale_factor` against kubelet eviction. A `kind` node shares the host kernel and cannot be given its own swap device, so the tuning cannot be observed at lab scale. |
| [Kubernetes v1.34: Of Wind & Will (O' WaW)](https://kubernetes.io/blog/2025/08/27/kubernetes-v1-34-release/) | 08-27 | 1.34 | `skip` | `meta` | Release announcement. Class-wide `skip`. |
| [Kubernetes v1.34: User preferences (kuberc) are available for testing in kubectl 1.34](https://kubernetes.io/blog/2025/08/28/kubernetes-v1-34-kubectl-kuberc-beta/) | 08-28 | 1.34 | `walk` | `tooling` | `kuberc` is the first kubectl configuration file that is not kubeconfig: aliases, per-command defaults, and at the pin a credential plugin policy the post does not mention. It runs entirely client-side. |
| [Kubernetes v1.34: Finer-Grained Control Over Container Restarts](https://kubernetes.io/blog/2025/08/29/kubernetes-v1-34-per-container-restart-policy/) | 08-29 | 1.34 | `walk` | `nodes` | `restartPolicy` becomes a per-container field, with rules that restart on some exit codes and not others. Alpha here, on by default from 1.35 — the post's enable-this-gate step is already stale. |
| [Kubernetes v1.34: DRA has graduated to GA](https://kubernetes.io/blog/2025/09/01/kubernetes-v1-34-dra-updates/) | 09-01 | 1.34 | `walk` | `sched` | `resource.k8s.io` reaches v1 and the gate goes stable but unlocked at 1.34, then locked at 1.35. 2022's exercise 12 ends with an alpha API that was replaced; this is what replaced it, and a fake driver is enough to see it. |
| [Kubernetes v1.34: Introducing CPU Manager Static Policy Option for Uncore Cache Alignment](https://kubernetes.io/blog/2025/09/02/kubernetes-v1-34-prefer-align-by-uncore-cache-cpumanager-static-policy-optimization/) | 09-02 | 1.34 | `dated` | `nodes` | A walkthrough of `prefer-align-cpus-by-uncorecache`, which only changes placement on processors whose last-level cache is split across core complexes. No lab node has one. |
| [Kubernetes v1.34: Service Account Token Integration for Image Pulls Graduates to Beta](https://kubernetes.io/blog/2025/09/03/kubernetes-v1-34-sa-tokens-image-pulls-beta/) | 09-03 | 1.34 | `read` | `security` | The beta makes `cacheType` a required field, breaking alpha configurations. Row 22 is the alpha post; both need a registry that accepts federated tokens. |
| [Kubernetes v1.34: PSI Metrics for Kubernetes Graduates to Beta](https://kubernetes.io/blog/2025/09/04/kubernetes-v1-34-introducing-psi-metrics-beta/) | 09-04 | 1.34 | `read` | `obs` | Pressure Stall Information reaches beta and is stable and locked from 1.36. Kernel-level metrics surfaced through the kubelet, with nothing to configure at the pin. |
| [Kubernetes v1.34: Pod Replacement Policy for Jobs Goes GA](https://kubernetes.io/blog/2025/09/05/kubernetes-v1-34-pod-replacement-policy-for-jobs-goes-ga/) | 09-05 | 1.34 | `read` | `api` | `podReplacementPolicy` stops a Job counting terminating Pods as running. Gate stable and locked from 1.34. |
| [Kubernetes v1.34: VolumeAttributesClass for Volume Modification GA](https://kubernetes.io/blog/2025/09/08/kubernetes-v1-34-volume-attributes-class/) | 09-08 | 1.34 | `read` | `storage` | VolumeAttributesClass goes GA. 2023's exercise 12 carries it, including the locked stable stage it reaches at 1.36. |
| [Kubernetes v1.34: Snapshottable API server cache](https://kubernetes.io/blog/2025/09/09/kubernetes-v1-34-snapshottable-api-server-cache/) | 09-09 | 1.34 | `read` | `api` | The API server can serve a consistent list from a snapshot of its own cache. The last step of a multi-release effort with no user-facing surface to drive. |
| [Kubernetes v1.34: Use An Init Container To Define App Environment Variables](https://kubernetes.io/blog/2025/09/10/kubernetes-v1-34-env-files/) | 09-10 | 1.34 | `read` | `nodes` | `EnvFiles` lets an init container write a file that the kubelet turns into a container's environment. Alpha here, on by default from 1.35 — the same shape as row 44, which carries it. |
| [Kubernetes v1.34: Mutable CSI Node Allocatable Graduates to Beta](https://kubernetes.io/blog/2025/09/11/kubernetes-v1-34-mutable-csi-node-allocatable-count/) | 09-11 | 1.34 | `read` | `storage` | Beta, and off by default until 1.35 — the pattern 2023 named, where a beta in the title is not a promise the gate was on. |
| [Kubernetes v1.34: Autoconfiguration for Node Cgroup Driver Goes GA](https://kubernetes.io/blog/2025/09/12/kubernetes-v1-34-cri-cgroup-driver-lookup-now-GA/) | 09-12 | 1.34 | `read` | `nodes` | The kubelet asks the CRI implementation which cgroup driver to use instead of being told twice. Its gate is one of the few whose beta stage never ends in the file. |
| [Kubernetes v1.34: Decoupled Taint Manager Is Now Stable](https://kubernetes.io/blog/2025/09/15/kubernetes-v1-34-decoupled-taint-manager-is-now-stable/) | 09-15 | 1.34 | `read` | `sched` | Taint-based eviction moves out of the node lifecycle controller into its own controller. 2023's row on the beta is the other end. |
| [Kubernetes v1.34: Moving Volume Group Snapshots to v1beta2](https://kubernetes.io/blog/2025/09/16/kubernetes-v1-34-volume-group-snapshot-beta-2/) | 09-16 | 1.34 | `read` | `storage` | A second beta for volume group snapshots, in external CRDs rather than the core API. 2023's alpha post is the other end. |
| [Kubernetes v1.34: Pods Report DRA Resource Health](https://kubernetes.io/blog/2025/09/17/kubernetes-v1-34-pods-report-dra-resource-health/) | 09-17 | 1.34 | `read` | `nodes` | Device health reaches DRA through `ResourceHealthStatus`, alpha from 1.31 and beta at 1.36. Needs a driver that reports unhealthy devices. |
| [Kubernetes v1.34: DRA Consumable Capacity](https://kubernetes.io/blog/2025/09/18/kubernetes-v1-34-dra-consumable-capacity/) | 09-18 | 1.34 | `read` | `sched` | DRA devices can be shared by capacity rather than by claim. Alpha here, beta at 1.36. |
| [Kubernetes v1.34: Recovery From Volume Expansion Failure (GA)](https://kubernetes.io/blog/2025/09/19/kubernetes-v1-34-recover-expansion-failure/) | 09-19 | 1.34 | `walk` | `storage` | Ask for 20TiB by mistake and, before this, only a cluster admin could get you back. Eleven releases alpha, then beta at 1.32 and stable and locked at 1.34 — and the recovery is a PVC edit a CSI driver in a lab can show. |
| [Kubernetes v1.34: Pod Level Resources Graduated to Beta](https://kubernetes.io/blog/2025/09/22/kubernetes-v1-34-pod-level-resources/) | 09-22 | 1.34 | `read` | `nodes` | Resources can be set for the Pod as a whole, not only per container. Beta and on by default from 1.34. |
| [Announcing Changed Block Tracking API support (alpha)](https://kubernetes.io/blog/2025/09/25/csi-changed-block-tracking/) | 09-25 | 1.34 | `read` | `storage` | A CSI API for listing the blocks that changed between two snapshots. No driver in reach implements it. |
| [Introducing Headlamp Plugin for Karpenter - Scaling and Visibility](https://kubernetes.io/blog/2025/10/06/introducing-headlamp-plugin-for-karpenter/) | 10-06 | — | `skip` | `ecosystem` | A plugin announcement for a UI project. No decision documented and no alternative weighed. |
| [Spotlight on Policy Working Group](https://kubernetes.io/blog/2025/10/18/wg-policy-spotlight-2025/) | 10-18 | — | `skip` | `meta` | A working group describes its work, and its completion. Class-wide `skip` for spotlights. |
| [7 Common Kubernetes Pitfalls (and How I Learned to Avoid Them)](https://kubernetes.io/blog/2025/10/20/seven-kubernetes-pitfalls-and-how-to-avoid/) | 10-20 | — | `read` | `tooling` | Seven configuration mistakes and their fixes. Sound advice, none of it a change between the post and the pin. |
| [Gateway API 1.4: New Features](https://kubernetes.io/blog/2025/11/06/gateway-api-v1-4/) | 11-06 | — | `read` | `net` | BackendTLSPolicy, `supportedFeatures` and named route rules to Standard. 2021's Gateway API exercise carries the API itself. |
| [Announcing the 2025 Steering Committee Election Results](https://kubernetes.io/blog/2025/11/09/steering-committee-results-2025/) | 11-09 | — | `skip` | `meta` | Election results. Class-wide `skip`. |
| [Ingress NGINX Retirement: What You Need to Know](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/) | 11-11 | — | `read` | `ecosystem` | SIG Network retires Ingress NGINX and points at Gateway API. At the pin the project no longer appears anywhere in the documentation, including the controller list the post sends readers to. |
| [Kubernetes Configuration Good Practices](https://kubernetes.io/blog/2025/11/25/configuration-good-practices/) | 11-25 | — | `read` | `tooling` | A refresh of the configuration good-practices page. No discontinuity of its own. |
| [Kubernetes v1.35 Sneak Peek](https://kubernetes.io/blog/2025/11/26/kubernetes-v1-35-sneak-peek/) | 11-26 | 1.35 | `skip` | `meta` | A pre-release preview of 1.35. Class-wide `skip` for sneak peeks. |
| [Kubernetes v1.35: Timbernetes (The World Tree Release)](https://kubernetes.io/blog/2025/12/17/kubernetes-v1-35-release/) | 12-17 | 1.35 | `skip` | `meta` | Release announcement. Class-wide `skip`. |
| [Kubernetes v1.35: Job Managed By Goes GA](https://kubernetes.io/blog/2025/12/18/kubernetes-v1-35-job-managedby-for-jobs-goes-ga/) | 12-18 | 1.35 | `walk` | `api` | `.spec.managedBy` tells the built-in Job controller to do nothing, so a Job with no external controller listening simply never runs. Alpha at 1.30, stable at 1.35, and one field is enough to watch a Job sit still. |
| [Kubernetes 1.35: In-Place Pod Resize Graduates to Stable](https://kubernetes.io/blog/2025/12/19/kubernetes-v1-35-in-place-pod-resize-ga/) | 12-19 | 1.35 | `read` | `nodes` | In-place Pod resize goes stable and its gate is locked. 2023's exercise 07 carries it. |
| [Avoiding Zombie Cluster Members When Upgrading to etcd v3.6](https://kubernetes.io/blog/2025/12/21/preventing-etcd-zombies/) | 12-21 | — | `read` | `etcd` | Upgrading 3.5 to 3.6 can resurrect members removed from the v2 store. Mirrored from the etcd blog; row 29 is the release it follows. |
| [Kubernetes v1.35: Kubelet Configuration Drop-in Directory Graduates to GA](https://kubernetes.io/blog/2025/12/22/kubernetes-v1-35-kubelet-config-drop-in-directory-ga/) | 12-22 | 1.35 | `read` | `nodes` | `--config-dir` merges kubelet configuration fragments. GA here with no feature gate of its own at the pin. |
| [Kubernetes v1.35: Fine-grained Supplemental Groups Control Graduates to GA](https://kubernetes.io/blog/2025/12/23/kubernetes-v1-35-fine-grained-supplementalgroups-control-ga/) | 12-23 | 1.35 | `read` | `security` | Fine-grained supplemental groups goes GA. 2024's exercise 12 carries it; row 21 is the beta post with the behavioural break. |
| [Kubernetes v1.35: Introducing Workload Aware Scheduling](https://kubernetes.io/blog/2025/12/29/kubernetes-v1-35-introducing-workload-aware-scheduling/) | 12-29 | 1.35 | `walk` | `sched` | The post's `scheduling.k8s.io/v1alpha1` Workload is `v1alpha2` at the pin, one of its three gates was removed in 1.37 for being merged into another, and five sibling gates it never mentions now exist. Two releases old and already a different API. |
| [Kubernetes v1.35: Watch Based Route Reconciliation in the Cloud Controller Manager](https://kubernetes.io/blog/2025/12/30/kubernetes-v1-35-watch-based-route-reconciliation-in-ccm/) | 12-30 | 1.35 | `read` | `nodes` | The cloud provider route controller can watch instead of polling on a fixed interval. Alpha from 1.35 and still alpha at the pin. |
| [Kubernetes 1.35: Enhanced Debugging with Versioned z-pages APIs](https://kubernetes.io/blog/2025/12/31/kubernetes-v1-35-structured-zpages/) | 12-31 | 1.35 | `walk` | `obs` | `/statusz` and `/flagz` return structured, versioned responses instead of text. Alpha at 1.32, beta and on by default at 1.36 — so at the pin the endpoints the post asks you to enable are already answering. |

## Exercises

Twelve `walk` verdicts, numbered in publication order. One is written; the other eleven are
*pending* — an authoring ticket's to claim. The rubric they are authored against was ratified in
[#57](https://github.com/k3ii/k8s-academy/issues/57).

| # | exercise | state |
|---|---|---|
| 01 | [The one incompatibility the post names, and the alpha gate that puts it back](01-nftables-kube-proxy.md) | written |
| 02 | A warning header, and a reference page that moved | pending |
| 03 | An image already on the node, and no proof you may use it | pending |
| 04 | Five releases alpha, and no end version | pending |
| 05 | Started is not ready | pending |
| 06 | A second file kubectl reads before your flags | pending |
| 07 | One container's restart policy, and the exit code that decides | pending |
| 08 | Devices, from a driver with no devices | pending |
| 09 | The typo you can take back | pending |
| 10 | The Job nothing is listening for | pending |
| 11 | A gate removed for being merged | pending |
| 12 | The debug endpoints you no longer have to enable | pending |
