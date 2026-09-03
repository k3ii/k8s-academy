# 2018 — the census

70 posts, 2018-01-08 to 2018-12-12. Nine percent of the corpus and **32% more posts than
2017**, reversing the drop that year recorded. Kubernetes 1.9 through 1.13 shipped inside it.
This is **the year the storage stack was rebuilt in public** — CSI runs alpha, beta and GA
across twelve months — and the year the blog's centre of gravity moved from *what a company
built on Kubernetes* to *what shipped in the release* — see [the method](../README.md).

**Yield: 9 `walk`**, inside the [8–15 band](../README.md#the-budget). 32 `read`, **1 `dated`**, 28
`skip`.

**The band's real test still has not arrived.** 2017 landed on the floor, 2016 and 2024 on or
near the ceiling, and in none of those did the band cut a post; 2018 lands at 9 and does not
either. What kept the number down here was not space but **redundancy against years already
censused**: containerd's GA, `apps/v1`'s GA, CoreDNS's GA and kubeadm's GA are four of the
year's biggest events and all four are `read`, because the 2017 census already walks the diff
each one announces. That is the first time the sweep's own back-catalogue, rather than a genre
rule, has been the thing deciding a verdict — and it will only get commoner as the archive
fills in.

**The single best find in the year is a GA that is being deleted.** IPVS became kube-proxy's
third backend and reached general availability in 1.11, with a deep-dive post arguing it out
against iptables. At the pin it is **deprecated as of v1.35, off by default from v1.40 and
removed in v1.43**, and the pinned docs are unusually blunt about why: the kernel IPVS API "turned
out to be a bad match for the Kubernetes Services API", and the backend "was never able to
implement all of the edge cases of Kubernetes Service functionality correctly". Every
beta-graduation rule in [the method](../README.md) is built on the assumption that the ladder
runs one way. This year contains two counter-examples — IPVS, and Dynamic Kubelet Configuration,
which was beta and **on by default** in 1.11 and had its gate removed from the kubelet in v1.24.
Neither is a case of a feature that never landed. Both landed, and were then taken out.

**`dated` returns, once.** [Building a Network Bootable Server Farm with LTSP](https://kubernetes.io/blog/2018/10/02/network-bootable-farm-with-ltsp/)
is the year's only post that passes both of the verdict's tests: a genuine end-to-end
walkthrough, and one that needs bare-metal machines that can boot over the network. After
2017's empty column, the verdict is at 9 rows in 311.

The 28 rejects are five release and pre-release announcements, one index post, twelve
community-and-contributor posts, two conference-speaking guides, one website-infrastructure
post, and seven vendor or ecosystem posts that record no decision. At **40% the reject rate
rises** for the first time in the sweep — 48% in 2015, 42% in 2016, 38% in 2017, 40% here — and
the rise is not the return of an old genre but the arrival of a new one: 2018 is the year the
project started writing about *itself as an organisation*. Steering elections, contributor
summits, office hours, a forum launch, a non-code contributor guide, localisation, a KubeCon
speaking guide in two parts. Twelve rows, none of them about Kubernetes.

That is also why **`meta` leads again at 24 rows and 34%**, its highest share since 2015, and
why 2017's `ecosystem` lead turns out to have been a single year: vendor writing halves from 28%
to 14%. **`storage` reaches 7 rows** — as many as 2016 and 2017 put together — which is CSI arriving.
`sched` earned none. `etcd` earned one, its second in five years censused and the first outside
2024, which retires the streak the 2017 pass flagged.

## Census

Verdicts and topics are defined in [`../README.md`](../README.md#the-census). Every post has a
row, and a row's title always links the post — never the exercise file, so the row never
changes once written. The **Exercises** table below is the progress record.

| post | date | k8s | verdict | topic | why |
|---|---|---|---|---|---|
| [Five Days of Kubernetes 1.9](https://kubernetes.io/blog/2018/01/five-days-of-kubernetes-19/) | 01-08 | 1.9 | `skip` | `meta` | Index post linking the 1.9 feature series. |
| [Kubernetes v1.9 releases beta support for Windows Server Containers](https://kubernetes.io/blog/2018/01/kubernetes-v19-beta-windows-support/) | 01-09 | 1.9 | `read` | `nodes` | Windows Server containers to beta: what SIG-Windows had working and what it still did not. Windows nodes are outside the lab, and the post is a status report rather than a walkthrough. |
| [Introducing Container Storage Interface (CSI) Alpha for Kubernetes](https://kubernetes.io/blog/2018/01/introducing-container-storage-interface/) | 01-10 | 1.9 | `read` | `storage` | CSI's alpha, superseded by its own sequel three months later; the beta post carries the deployment model and the API objects that survived. |
| [Extensible Admission is Beta](https://kubernetes.io/blog/2018/01/extensible-admission-is-beta/) | 01-11 | 1.9 | `walk` | `api` | Admission webhooks reached beta here as `admissionregistration.k8s.io/v1beta1`. At the pin the group is `v1` and it will not accept the post's registration: `admissionReviewVersions` is a required field when creating a webhook configuration, and the pin's own example carries a `sideEffects` declaration the post has no reason to include. The failure lands at registration, before the webhook is ever called. |
| [Introducing client-go version 6](https://kubernetes.io/blog/2018/01/introducing-client-go-version-6/) | 01-12 | 1.9 | `read` | `tooling` | The client-go release that tracked Kubernetes 1.9, and the compatibility matrix between the two — a table the post has to print because the two version numbers did not line up. |
| [Core Workloads API GA](https://kubernetes.io/blog/2018/01/core-workloads-api-ga/) | 01-15 | 1.9 | `read` | `api` | `apps/v1` at GA for Deployment, ReplicaSet, DaemonSet and StatefulSet, told as the road from ReplicationController. The defaults that moved in the same release are carried by the 2017 census's `apps/v1` exercise. |
| [Reporting Errors from Control Plane to Applications Using Kubernetes Events](https://kubernetes.io/blog/2018/01/reporting-errors-using-kubernetes-events/) | 01-25 | — | `read` | `obs` | Emitting Kubernetes Events from a control-plane service so that application owners can see why their request failed — Events used as an interface between operators, not as a debugging aid. |
| [Kubernetes: First Beta Version of Kubernetes 1.10 is Here](https://kubernetes.io/blog/2018/03/first-beta-version-of-kubernetes-1-10/) | 03-02 | 1.10 | `skip` | `meta` | Pre-release announcement for the 1.10 beta. |
| [Apache Spark 2.3 with Native Kubernetes Support](https://kubernetes.io/blog/2018/03/apache-spark-23-with-native-kubernetes/) | 03-06 | — | `read` | `ecosystem` | Spark's native Kubernetes scheduler backend, and the decision it records: one control plane for batch and services instead of a dedicated YARN stack beside it. |
| [How to Integrate RollingUpdate Strategy for TPR in Kubernetes](https://kubernetes.io/blog/2018/03/how-to-integrate-rollingupdate-strategy/) | 03-13 | — | `read` | `api` | A rolling-update controller for ThirdPartyResources, written when TPR was already gone — the post says "TPR (currently CRD)" once and then uses the dead name throughout. `ThirdPartyResource` appears nowhere in the pinned docs. |
| [Expanding User Support with Office Hours](https://kubernetes.io/blog/2018/03/expanding-user-support-with-office-hours/) | 03-14 | — | `skip` | `meta` | Kubernetes office hours: a support-format announcement. |
| [Principles of Container-based Application Design](https://kubernetes.io/blog/2018/03/principles-of-container-app-design/) | 03-15 | — | `read` | `api` | Seven contracts a container has to satisfy to be managed by a platform — health, lifecycle, disposability. The contracts outlived every tool named around them. |
| [Kubernetes 1.10: Stabilizing Storage, Security, and Networking](https://kubernetes.io/blog/2018/03/26/kubernetes-1.10-stabilizing-storage-security-networking/) | 03-26 | 1.10 | `skip` | `meta` | Release announcement. |
| [Fixing the Subpath Volume Vulnerability in Kubernetes](https://kubernetes.io/blog/2018/04/04/fixing-subpath-volume-vulnerability/) | 04-04 | — | `read` | `security` | CVE-2017-1002101: how a `subPath` mount could reach outside its volume, and why the fix had to be a kernel-level open rather than a path check. An explanation of a race, not something to reproduce. |
| [Container Storage Interface (CSI) for Kubernetes Goes Beta](https://kubernetes.io/blog/2018/04/10/container-storage-interface-beta/) | 04-10 | 1.10 | `walk` | `storage` | CSI at beta, with the deployment walkthrough. At the pin the objects have moved on — `VolumeAttachment` went from the `storage/v1beta1` group this post announces to `storage.k8s.io/v1` — and the sidecar it names, `driver-registrar`, is gone along with the limitation the post itself records against it: it needed write access to every Node object, which is the reason `CSINode` exists. |
| [Migrating the Kubernetes Blog](https://kubernetes.io/blog/2018/04/11/migrating-the-kubernetes-blog/) | 04-11 | — | `read` | `meta` | Blogger to GitHub, and the redirect scheme that kept eleven years of permalinks alive. This is why the archive copies each post's URL from the manifest rather than assembling it from the date and the slug: 205 posts override the site-wide permalink. |
| [Local Persistent Volumes for Kubernetes Goes Beta](https://kubernetes.io/blog/2018/04/13/local-persistent-volumes-beta/) | 04-13 | 1.10 | `read` | `storage` | Local PVs to beta: pre-created PersistentVolumes pinned to a node by `nodeAffinity`. Still how local volumes work at the pin, and the annotation this release replaced — `volume.alpha.kubernetes.io/node-affinity` — was deprecated in the same 1.10, so a reader of this post was never on the old path. |
| [Kubernetes Application Survey 2018 Results](https://kubernetes.io/blog/2018/04/24/kubernetes-application-survey-results-2018/) | 04-24 | — | `skip` | `meta` | Survey results from the Application Definition Working Group. |
| [Kubernetes Community - Top of the Open Source Charts in 2017](https://kubernetes.io/blog/2018/04/25/open-source-charts-2017/) | 04-25 | — | `skip` | `meta` | GitHub Octoverse statistics for the project. |
| [Zero-downtime Deployment in Kubernetes with Jenkins](https://kubernetes.io/blog/2018/04/30/zero-downtime-deployment-kubernetes-jenkins/) | 04-30 | — | `read` | `api` | Why `RollingUpdate` is not zero-downtime on its own without a readiness probe and a `preStop` grace, and where blue/green is the better trade. The Jenkins and cloud plugins around the argument are incidental to it. |
| [Developing on Kubernetes](https://kubernetes.io/blog/2018/05/01/developing-on-kubernetes/) | 05-01 | — | `read` | `tooling` | A survey of Kubernetes development workflows and the tools built for them. Most of the tools are gone; the taxonomy of the problem — build loop, remote debug, put-your-laptop-in-the-cluster — is what survived. |
| [Current State of Policy in Kubernetes](https://kubernetes.io/blog/2018/05/02/policy-in-kubernetes/) | 05-02 | — | `read` | `security` | The state of policy across Kubernetes before there was a policy story: identity, networking, storage and RBAC each expressing intent in their own language. The consolidation the post argues for arrived through the admission layer. |
| [Announcing Kubeflow 0.1](https://kubernetes.io/blog/2018/05/04/announcing-kubeflow-0.1/) | 05-04 | — | `skip` | `ecosystem` | Progress report on a project's 0.1 release. |
| [Docs are Migrating from Jekyll to Hugo](https://kubernetes.io/blog/2018/05/05/hugo-migration/) | 05-05 | — | `skip` | `meta` | Website build system migration, Jekyll to Hugo. |
| [Gardener - The Kubernetes Botanist](https://kubernetes.io/blog/2018/05/17/gardener/) | 05-17 | — | `read` | `ecosystem` | Managing Kubernetes clusters as objects on a host cluster — the seed/shoot model, and the single-cluster provisioning tools the post names as what it is rejecting. |
| [Getting to Know Kubevirt](https://kubernetes.io/blog/2018/05/22/getting-to-know-kubevirt/) | 05-22 | — | `skip` | `ecosystem` | Introductory tour of an add-on project; no decision recorded. |
| [Kubernetes Containerd Integration Goes GA](https://kubernetes.io/blog/2018/05/24/kubernetes-containerd-integration-goes-ga/) | 05-24 | 1.10 | `read` | `nodes` | containerd's CRI integration at GA. The 2017 census's containerd exercise carries the diff this post announces. |
| [Introducing kustomize; Template-free Configuration Customization for Kubernetes](https://kubernetes.io/blog/2018/05/29/announcing-kustomize/) | 05-29 | — | `walk` | `tooling` | kustomize as a standalone binary you piped into `kubectl apply -f -`. At the pin it is a kubectl verb — `kubectl apply -k`, `kubectl kustomize`, `kubectl diff -k` — which means the kustomize doing the work is the one compiled into your kubectl rather than the one you installed. The post's own workflow still runs, and runs a different version of the tool. |
| [Say Hello to Discuss Kubernetes](https://kubernetes.io/blog/2018/05/30/say-hello-to-discuss-kubernetes/) | 05-30 | — | `skip` | `meta` | Announcement of a Discourse forum. |
| [4 Years of K8s](https://kubernetes.io/blog/2018/06/06/4-years-of-k8s/) | 06-06 | — | `read` | `history` | The first commit, and the Borg and Omega work it came out of, told by the person who pushed it. |
| [Dynamic Ingress in Kubernetes](https://kubernetes.io/blog/2018/06/07/dynamic-ingress-kubernetes/) | 06-07 | — | `skip` | `ecosystem` | Vendor API gateway configured through Service annotations; no alternative examined. |
| [Kubernetes 1.11: In-Cluster Load Balancing and CoreDNS Plugin Graduate to General Availability](https://kubernetes.io/blog/2018/06/27/kubernetes-1.11-release-announcement/) | 06-27 | 1.11 | `skip` | `meta` | Release announcement. |
| [Airflow on Kubernetes (Part 1): A Different Kind of Operator](https://kubernetes.io/blog/2018/06/28/airflow-kubernetes-operator/) | 06-28 | — | `skip` | `ecosystem` | Workflow orchestrator's Kubernetes executor; the first screen introduces the tool and names no rejected alternative. |
| [IPVS-Based In-Cluster Load Balancing Deep Dive](https://kubernetes.io/blog/2018/07/09/ipvs-in-cluster-load-balancing/) | 07-09 | 1.11 | `walk` | `net` | IPVS reached GA here as kube-proxy's third backend. At the pin it is **deprecated as of v1.35**, off by default from v1.40 and removed in v1.43 — and the pinned docs give the reason plainly: the kernel IPVS API turned out to be a bad match for the Service API, and the backend never implemented all of the Service edge cases correctly. `nftables` is the replacement. The baseline the post argues against is gone too: `userspace` is not among the pin's four modes. A feature can reach GA and still be deleted. |
| [CoreDNS GA for Kubernetes Cluster DNS](https://kubernetes.io/blog/2018/07/10/coredns-ga/) | 07-10 | 1.11 | `read` | `net` | CoreDNS at GA, and the Corefile that replaced the kube-dns ConfigMap. The 2017 census's DNS exercise walks that same translation, and this post's remaining surprise — the Service is still named `kube-dns` at the pin, deliberately — is that exercise's payload. |
| [Meet Our Contributors - Monthly Streaming YouTube Mentoring Series](https://kubernetes.io/blog/2018/07/10/meet-our-contributors-youtube-mentoring-series/) | 07-10 | — | `skip` | `meta` | Monthly contributor mentoring stream. |
| [Dynamic Kubelet Configuration](https://kubernetes.io/blog/2018/07/11/dynamic-kubelet-configuration/) | 07-11 | 1.11 | `walk` | `nodes` | Dynamic Kubelet Configuration, beta and on by default in this release. It is the year's one ladder that ran backwards: deprecated at v1.22, and the gate **removed from the kubelet in v1.24**. What survives is the trap — `node.spec.configSource` is still a field on the Node API at the pin, documented only as belonging to a feature that "is removed". The post's central step still applies cleanly and does nothing at all. |
| [Resizing Persistent Volumes using Kubernetes](https://kubernetes.io/blog/2018/07/12/resizing-persistent-volumes-using-kubernetes/) | 07-12 | 1.11 | `read` | `storage` | PVC expansion to beta: edit the claim, get a bigger volume. The step the post spends its length on — recreate the pod so the filesystem resize can finish — is the part that stopped being necessary; at the pin an in-use claim expands online and becomes available to its Pod without a restart. |
| [How the sausage is made: the Kubernetes 1.11 release interview, from the Kubernetes Podcast](https://kubernetes.io/blog/2018/07/16/kubernetes-1-11-release-interview/) | 07-16 | 1.11 | `read` | `meta` | The release managers for 1.11 and 1.12 on how a release is actually run. The maintainer-interview rule asks whether the interviewee owns code; these two own the process, which is the thing being explained. |
| [11 Ways (Not) to Get Hacked](https://kubernetes.io/blog/2018/07/18/11-ways-not-to-get-hacked/) | 07-18 | — | `walk` | `security` | A hardening checklist, and the half of it that expired. PodSecurityPolicy — the post's answer for restricting what a workload may do — was deprecated at v1.21 and **removed at v1.25**, and Pod Security Admission replaced it with a different enforcement model rather than a renamed object. The control-plane half, TLS everywhere and RBAC over ABAC, is still the advice. |
| [Kubernetes Wins the 2018 OSCON Most Impact Award](https://kubernetes.io/blog/2018/07/19/kubernetes-wins-2018-oscon-most-impact-award/) | 07-19 | — | `skip` | `meta` | Award announcement. |
| [The History of Kubernetes & the Community Behind It](https://kubernetes.io/blog/2018/07/20/history-kubernetes-community/) | 07-20 | — | `read` | `history` | The keynote version of the project's history, 1.0 through CNCF, from the stage where the award was given. |
| [Feature Highlight: CPU Manager](https://kubernetes.io/blog/2018/07/24/cpu-manager/) | 07-24 | — | `read` | `nodes` | The CPU Manager's static policy and the exclusive-CPU allocation it buys. The post names no Kubernetes version; what it describes climbed the ladder without a surprise in it, and the contention it fixes needs more load than a 4-vCPU lab can generate. |
| [KubeVirt: Extending Kubernetes with CRDs for Virtualized Workloads](https://kubernetes.io/blog/2018/07/27/kubevirt-crds-for-virtualization/) | 07-27 | — | `read` | `ecosystem` | CRDs versus an aggregated API server for a virtualization API, and why the project chose CRDs in 2017 despite what they could not yet do — the decision and the rejected alternative, both on the record. |
| [Dynamically Expand Volume with CSI and Kubernetes](https://kubernetes.io/blog/2018/08/02/dynamically-expand-volume-csi/) | 08-02 | — | `read` | `storage` | Extending CSI 0.2 to add volume expansion, written from the driver's side. A specification walkthrough rather than a cluster one. |
| [Out of the Clouds onto the Ground: How to Make Kubernetes Production Grade Anywhere](https://kubernetes.io/blog/2018/08/03/make-kubernetes-production-grade-anywhere/) | 08-03 | — | `read` | `tooling` | What "production grade" means off a cloud: the failure modes of an on-premise control plane, and what has to exist before you call one finished. |
| [Introducing Kubebuilder: an SDK for building Kubernetes APIs using CRDs](https://kubernetes.io/blog/2018/08/10/introducing-kubebuilder/) | 08-10 | — | `read` | `tooling` | The SDK announcement for building CRD-backed APIs. Writing a controller is beyond a blog walk; the argument for why a CRD plus a controller-runtime became the default shape is the part to read. |
| [The Machines Can Do the Work, a Story of Kubernetes Testing, CI, and Automating the Contributor Experience](https://kubernetes.io/blog/2018/08/29/kubernetes-testing-ci-automating-contributor-experience/) | 08-29 | — | `read` | `meta` | How the project automated its own contributor workflow, and why it treated heroism as a bug rather than a virtue. |
| [2018 Steering Committee Election Cycle Kicks Off](https://kubernetes.io/blog/2018/09/06/2018-steering-committee-election-cycle-kicks-off/) | 09-06 | — | `skip` | `meta` | Election process announcement. |
| [Hands On With Linkerd 2.0](https://kubernetes.io/blog/2018/09/18/2018-linkerd-2-0/) | 09-18 | — | `skip` | `ecosystem` | Vendor service-mesh tutorial. |
| [Kubernetes 1.12: Kubelet TLS Bootstrap and Azure Virtual Machine Scale Sets (VMSS) Move to General Availability](https://kubernetes.io/blog/2018/09/27/kubernetes-1-12-release-announcement/) | 09-27 | 1.12 | `skip` | `meta` | Release announcement. |
| [Health checking gRPC servers on Kubernetes](https://kubernetes.io/blog/2018/10/01/health-checking-grpc/) | 10-01 | — | `walk` | `api` | Health-checking a gRPC server in 2018 meant adding a binary to your image. The post now carries the site's own note pointing at the built-in probe, **stable since v1.27**: the tool became a `grpc:` field. The pin still names `grpc-health-probe` in exactly one place, because it and the built-in probe disagree about `timeoutSeconds` when the `ExecProbeTimeout` gate is off — the external tool did not simply disappear, it left a behavioural difference behind. |
| [Building a Network Bootable Server Farm for Kubernetes with LTSP](https://kubernetes.io/blog/2018/10/02/network-bootable-farm-with-ltsp/) | 10-02 | — | `dated` | `nodes` | A network-boot pipeline: PXE, DHCP and a node OS image built by CI, so a rack of new machines joins the cluster with no installer run on any of them. Genuinely a walkthrough and still a sound one, but it needs bare-metal nodes that can boot over the network and a second machine to serve them — beyond the lab's single-host 9.5GB ceiling, which has nothing to PXE-boot. |
| [KubeDirector: The easy way to run complex stateful applications on Kubernetes](https://kubernetes.io/blog/2018/10/03/kubedirector/) | 10-03 | — | `skip` | `ecosystem` | Vendor operator for stateful applications; a capabilities list, no decision. |
| [Introducing the Non-Code Contributor’s Guide](https://kubernetes.io/blog/2018/10/04/non-code-contributors-guide/) | 10-04 | — | `skip` | `meta` | Contributor guide for non-code roles. |
| [Support for Azure VMSS, Cluster-Autoscaler and User Assigned Identity](https://kubernetes.io/blog/2018/10/08/support-for-azure-vmss/) | 10-08 | 1.12 | `skip` | `ecosystem` | Cloud-provider-specific configuration guide. |
| [Introducing Volume Snapshot Alpha for Kubernetes](https://kubernetes.io/blog/2018/10/09/volume-snapshot-alpha/) | 10-09 | 1.12 | `walk` | `storage` | Volume snapshots at alpha, `snapshot.storage.k8s.io/v1alpha1`, with the types shipped in the cluster. At the pin the API is `v1` and it is **not part of the core Kubernetes API at all**: the pinned docs say the snapshot types are CRDs, that a snapshot controller has to be deployed into the control plane, and that installing both is the distribution's responsibility. So a cluster can have a CSI driver that supports snapshots and still have no `VolumeSnapshot` kind to create. |
| [Kubernetes v1.12: Introducing RuntimeClass](https://kubernetes.io/blog/2018/10/10/runtimeclass/) | 10-10 | 1.12 | `walk` | `nodes` | RuntimeClass at alpha. The post describes "a RuntimeClassSpec [that] holds a single field, the RuntimeHandler". At the pin RuntimeClass is `node.k8s.io/v1`, stable since v1.20, and the pinned docs say it "currently only has 2 significant fields: the RuntimeClass name (`metadata.name`) and the handler (`handler`)" — no spec at all. The shape the post describes cannot be written down any more, and the field that replaced it is a sibling of `metadata` rather than a child of `spec`. |
| [Topology-Aware Volume Provisioning in Kubernetes](https://kubernetes.io/blog/2018/10/11/topology-aware-volume-provisioning/) | 10-11 | 1.12 | `read` | `storage` | Topology-aware provisioning: `WaitForFirstConsumer`, so the volume is created where the pod can actually run. The 2017 census's dynamic-provisioning exercise carries the binding mode. |
| [2018 Steering Committee Election Results](https://kubernetes.io/blog/2018/10/15/steering-election-results/) | 10-15 | — | `skip` | `meta` | Election results. |
| [Kubernetes 2018 North American Contributor Summit](https://kubernetes.io/blog/2018/10/16/kubernetes-2018-north-american-contributor-summit/) | 10-16 | — | `skip` | `meta` | Contributor summit logistics. |
| [Tips for Your First Kubecon Presentation - Part 1](https://kubernetes.io/blog/2018/10/18/tips-for-first-kubecon-presentation-part-1/) | 10-18 | — | `skip` | `meta` | Conference speaking advice. |
| [Tips for Your First Kubecon Presentation - Part 2](https://kubernetes.io/blog/2018/10/26/tips-for-first-kubecon-presentation-part-2/) | 10-26 | — | `skip` | `meta` | Conference speaking advice, part two. |
| [gRPC Load Balancing on Kubernetes without Tears](https://kubernetes.io/blog/2018/11/07/grpc-load-balancing-with-linkerd/) | 11-07 | — | `read` | `net` | Why L4 load balancing does not balance gRPC, and the three answers available: client-side balancing, a headless Service, or a proxy that speaks HTTP/2. The vendor's mesh is the third; the diagnosis is general. |
| [Kubernetes Docs Updates, International Edition](https://kubernetes.io/blog/2018/11/08/kubernetes-docs-update-i18n/) | 11-08 | — | `skip` | `meta` | Localization workflow for the documentation. |
| [Kubernetes 1.13: Simplified Cluster Management with Kubeadm, Container Storage Interface (CSI), and CoreDNS as Default DNS are Now Generally Available](https://kubernetes.io/blog/2018/12/03/kubernetes-1-13-release-announcement/) | 12-03 | 1.13 | `skip` | `meta` | Release announcement. |
| [Production-Ready Kubernetes Cluster Creation with kubeadm](https://kubernetes.io/blog/2018/12/04/kubeadm-ga-release/) | 12-04 | 1.13 | `read` | `tooling` | kubeadm at GA, headlining a `v1beta1` configuration schema you could finally tune declaratively. The pin ships kubeadm config docs for `v1beta3` and `v1beta4` only, so the schema the GA post advertises is two removals behind. The 2017 census's kubeadm exercise carries the phase and self-hosting diff. |
| [New Contributor Workshop Shanghai](https://kubernetes.io/blog/2018/12/05/new-contributor-shanghai/) | 12-05 | — | `skip` | `meta` | Contributor workshop report. |
| [etcd: Current status and future roadmap](https://kubernetes.io/blog/2018/12/11/current-status-and-future-roadmap/) | 12-11 | — | `read` | `etcd` | etcd from its own maintainers: what the 3.x line fixed, the storage and Raft work behind it, and where the project was headed. The archive's second `etcd` row in four years censused, and the first outside 2024. |
| [Kubernetes Federation Evolution](https://kubernetes.io/blog/2018/12/12/kubernetes-federation-evolution/) | 12-12 | — | `read` | `api` | KubeFed's model for propagating objects across clusters, and the federation v1 design it was built to replace. The pinned docs carry no KubeFed page at all, so both ends of that succession are now history. |

## Exercises

Nine `walk` verdicts, numbered in publication order. Five of the nine are written; four are still
*pending*. The rubric they are authored against was ratified in
[#57](https://github.com/k3ii/k8s-academy/issues/57).

| # | exercise | state |
|---|---|---|
| 01 | [The webhook that fails before it runs](01-extensible-admission-is-beta.md) | written |
| 02 | [One sidecar that could write to every Node](02-container-storage-interface-beta.md) | written |
| 03 | [Two kustomizes, one of them inside kubectl](03-announcing-kustomize.md) | written |
| 04 | [GA is not the end of the ladder](04-ipvs-in-cluster-load-balancing.md) | written |
| 05 | [A field that still applies and does nothing](05-dynamic-kubelet-configuration.md) | written |
| 06 | Eleven ways, and the one that was deleted | pending |
| 07 | The binary that became a field | pending |
| 08 | The kind that is not in the cluster | pending |
| 09 | A spec with nothing in it | pending |
