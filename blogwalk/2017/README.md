# 2017 — the census

53 posts, 2017-01-09 to 2017-12-21. Seven percent of the corpus and **41% fewer posts than
2016**, which is the sharpest year-on-year drop in the archive; the blog stopped printing
weekly meeting minutes and the volume went with them. Kubernetes 1.6 through 1.9 shipped inside
the year, with the earliest posts still targeting 1.5. This is **the year the security defaults
moved** — RBAC goes beta in 1.6 and GA in 1.8, NetworkPolicy goes stable in 1.7, and
containerd arrives as a real alternative to Docker under CRI — see [the method](../README.md).

**Yield: 8 `walk`**, on the floor of the [8–15 band](../README.md#the-budget). 25 `read`, **0
`dated`**, 20 `skip`.

**The floor is now tested, and it held without being leaned on.** Two prior years reached the
ceiling and neither was cut by it; this is the first year to arrive at the other end, and it
got there with nothing pushed out and nothing promoted to fill space. The eight are not a thin
year's consolation either — they are the year's spine: dynamic provisioning, affinity, cluster
DNS, the workload-controller update strategies, `kubeadm upgrade`, RBAC, NetworkPolicy and
containerd. Every one of the eight is a subsystem a 2026 cluster still runs, and in every one
of the eight the mechanism the post describes has since been replaced underneath the name,
which is what makes the diffs worth walking. The floor did not bind, so **8–15 has now been
approached from both ends without either end cutting a post** — evidence the band was set about
right, and the first evidence of that kind the sweep has produced.

**No post earned `dated`, the first year with an empty verdict.** That is not a claim the year
had no oversized walkthroughs; it is a consequence of rule order. `dated` requires that the
post be a walkthrough, and the year's genuinely oversized walkthroughs — distributed
deep-learning training on Baidu's framework, twice — are vendor posts, which the vendor rule
sends to `skip` before the `dated` tests are ever reached. The lab-infeasibility is real and
goes unrecorded. This is a rule interaction rather than a defect in either rule, and it is
reported in the pass's findings rather than settled here.

The 20 rejects are four release announcements, two release-series index posts, two conference
talk trailers that are a paragraph around a video, a UX survey, a community points scheme, a
governance election result, a release-lead retrospective, a conformance round-up, and seven
vendor or ecosystem posts that record no decision. At **38% the reject rate falls for the third
straight year** — 48% in 2015, 42% in 2016, 38% here, against 19% in 2024 — and the fall is
entirely the disappearance of the weekly-hangout genre, which alone accounted for seven rejects
in 2016 and eleven in 2015 and produced none here.

What replaced that volume is vendor writing. **`ecosystem` is 15 rows, 28% of the year and the
highest share of any year censused** — against 21% in 2016 and 9% in 2015. At 15 rows against
`meta`'s 14 it is **the largest tag in the year, the first time `meta` has not led one**. Eight
of the fifteen clear the vendor rule's bar and are `read`: they are case studies that name what
they moved off and what it cost them, a different genre from the product announcements that
make up the other seven. The service mesh arrives inside this tag, twice.

`etcd` earned no rows again: three of the four years censused have none, and the tag's only row
in the archive so far is in 2024. `api` earned one. Neither is evidence against its tag — the
workload API was moving all year — but the blog covered it through the controllers on top
rather than through the objects underneath.

## Census

Verdicts and topics are defined in [`../README.md`](../README.md#the-census). Every post has a
row, and a row's title always links the post — never the exercise file, so the row never
changes once written. The **Exercises** table below is the progress record.

| post | date | k8s | verdict | topic | why |
|---|---|---|---|---|---|
| [Kubernetes UX Survey Infographic](https://kubernetes.io/blog/2017/01/kubernetes-ux-survey-infographic/) | 01-09 | — | `skip` | `meta` | Survey results for the Dashboard UI, presented as an infographic. |
| [A Stronger Foundation for Creating and Managing Kubernetes Clusters](https://kubernetes.io/blog/2017/01/stronger-foundation-for-creating-and-managing-kubernetes-clusters/) | 01-12 | 1.6 | `read` | `tooling` | SIG-Cluster-Lifecycle setting kubeadm's scope against kops — the division of labour that held; kubeadm reached GA in 1.13. |
| [Scaling Kubernetes deployments with Policy-Based Networking](https://kubernetes.io/blog/2017/01/scaling-kubernetes-deployments-with-policy-base-networking/) | 01-19 | — | `skip` | `ecosystem` | Vendor networking product. The first screen argues for policy-based networking generally and names no alternative it rejected. |
| [How we run Kubernetes in Kubernetes aka Kubeception](https://kubernetes.io/blog/2017/01/how-we-run-kubernetes-in-kubernetes-kubeception/) | 01-20 | — | `read` | `ecosystem` | Running tenant control planes as workloads on a host cluster, and why the fleet layer underneath was kept — the pattern Cluster API later made standard. |
| [Fission: Serverless Functions as a Service for Kubernetes](https://kubernetes.io/blog/2017/01/fission-serverless-functions-as-service-for-kubernetes/) | 01-30 | — | `skip` | `ecosystem` | Vendor FaaS framework. The rationale section begins inside the first screen but its argument falls outside it. |
| [Running MongoDB on Kubernetes with StatefulSets](https://kubernetes.io/blog/2017/01/running-mongodb-on-kubernetes-with-statefulsets/) | 01-30 | 1.5 | `read` | `storage` | StatefulSet walkthrough the site itself now stamps with a staleness warning; the mechanics are carried in richer form by the 09-27 update post. |
| [Highly Available Kubernetes Clusters](https://kubernetes.io/blog/2017/02/highly-available-kubernetes-clusters/) | 02-02 | 1.5 | `read` | `tooling` | HA masters across three zones via `kube-up`, which no longer exists; the modern path is `kubeadm init --control-plane-endpoint`. |
| [Run Deep Learning with PaddlePaddle on Kubernetes](https://kubernetes.io/blog/2017/02/run-deep-learning-with-paddlepaddle-on-kubernetes/) | 02-08 | — | `skip` | `ecosystem` | Vendor deep-learning framework on Kubernetes. |
| [Inside JD.com's Shift to Kubernetes from OpenStack](https://kubernetes.io/blog/2017/02/inside-jd-com-shift-to-kubernetes-from-openstack/) | 02-10 | — | `read` | `ecosystem` | Migration decision record: physical machines to OpenStack to Kubernetes, with what each step cost them in allocation time and density. |
| [Containers as a Service, the foundation for next generation PaaS](https://kubernetes.io/blog/2017/02/caas-the-foundation-for-next-gen-paas/) | 02-21 | — | `read` | `ecosystem` | The argument that container orchestrators became the layer PaaS is built on rather than a competitor to it. |
| [Deploying PostgreSQL Clusters using StatefulSets](https://kubernetes.io/blog/2017/02/postgresql-clusters-kubernetes-statefulsets/) | 02-24 | 1.5 | `read` | `storage` | Vendor StatefulSet walkthrough on kubeadm; same ground as the 09-27 update post, which carries the version diff too. |
| [The K8sPort: Engaging Kubernetes Community One Activity at a Time](https://kubernetes.io/blog/2017/03/k8sport-engaging-the-kubernetes-community/) | 03-24 | — | `skip` | `meta` | Community engagement hub and points scheme. |
| [Kubernetes 1.6: Multi-user, Multi-workloads at Scale](https://kubernetes.io/blog/2017/03/kubernetes-1-6-multi-user-multi-workloads-at-scale/) | 03-28 | 1.6 | `skip` | `meta` | Release announcement. |
| [Dynamic Provisioning and Storage Classes in Kubernetes](https://kubernetes.io/blog/2017/03/dynamic-provisioning-and-storage-classes-kubernetes/) | 03-29 | 1.6 | `walk` | `storage` | Dynamic provisioning went stable here, and the annotations around it diverge: `volume.alpha.kubernetes.io/storage-class` has been silently ignored since 1.6 while its beta sibling is still honoured with a warning. Add the default-class admission plugin and `WaitForFirstConsumer`, and a PVC that sits `Pending` is now working correctly. |
| [Five Days of Kubernetes 1.6](https://kubernetes.io/blog/2017/03/five-days-of-kubernetes-1-6/) | 03-29 | 1.6 | `skip` | `meta` | Index post linking the 1.6 series. |
| [Scalability updates in Kubernetes 1.6: 5,000 node and 150,000 pod clusters](https://kubernetes.io/blog/2017/03/scalability-updates-in-kubernetes-1-6/) | 03-30 | 1.6 | `read` | `sched` | The scalability SLOs and what was measured to claim 5,000 nodes; a report on someone else's cluster rather than a walkthrough. |
| [Advanced Scheduling in Kubernetes](https://kubernetes.io/blog/2017/03/advanced-scheduling-in-kubernetes/) | 03-31 | 1.6 | `walk` | `sched` | Node and pod affinity, taints and custom schedulers all at beta here, and all GA long since. The discontinuity is in the post's own YAML: every affinity example keys on `failure-domain.beta.kubernetes.io/zone`, which has been deprecated in favour of `topology.kubernetes.io/zone` since v1.17 and never removed — so the manifest still applies, still schedules, and matches nothing unless you set the old label by hand. Observable in the lab on a single labelled node. |
| [Configuring Private DNS Zones and Upstream Nameservers in Kubernetes](https://kubernetes.io/blog/2017/04/configuring-private-dns-zones-upstream-nameservers-kubernetes/) | 04-04 | 1.6 | `walk` | `net` | Stub domains and upstream nameservers configured through the kube-dns ConfigMap. At the pin `stubDomains` and `upstreamNameservers` appear nowhere in the DNS-customisation task — CoreDNS `forward` blocks in a Corefile replaced them — yet the Service is still *named* `kube-dns`, so the post's first instruction still finds something. |
| [RBAC Support in Kubernetes](https://kubernetes.io/blog/2017/04/rbac-support-in-kubernetes/) | 04-06 | 1.6 | `read` | `security` | The ABAC-versus-RBAC argument at beta; the 10-28 GA post covers the same ground with the ladder finished. |
| [How Bitmovin is Doing Multi-Stage Canary Deployments with Kubernetes in the Cloud and On-Prem](https://kubernetes.io/blog/2017/04/multi-stage-canary-deployments-with-kubernetes-in-the-cloud-onprem/) | 04-21 | — | `read` | `ecosystem` | Multi-stage canary deployments across cloud and on-prem, and why the cloud-neutral abstraction was worth the migration. |
| [Dancing at the Lip of a Volcano: The Kubernetes Security Process - Explained](https://kubernetes.io/blog/2017/05/kubernetes-security-process-explained/) | 05-18 | — | `read` | `security` | How Kubernetes triages, patches and discloses a vulnerability — a process that outlived every command in the year. |
| [Kubernetes: a monitoring guide](https://kubernetes.io/blog/2017/05/kubernetes-monitoring-guide/) | 05-19 | — | `read` | `obs` | What to measure in a cluster and why, organised by layer; a technical guide from a vendor with no product in the first screen. |
| [Kubespray Ansible Playbooks foster Collaborative Kubernetes Ops](https://kubernetes.io/blog/2017/05/kubespray-ansible-collaborative-kubernetes-ops/) | 05-19 | — | `read` | `tooling` | Ansible playbooks as the operator-familiar path to a cluster, and the argument that familiar tools grow the community. |
| [Draft: Kubernetes container development made easy](https://kubernetes.io/blog/2017/05/draft-kubernetes-container-development/) | 05-31 | — | `skip` | `ecosystem` | Vendor developer tool for scaffolding containerised apps. |
| [Managing microservices with the Istio service mesh](https://kubernetes.io/blog/2017/05/managing-microservices-with-istio-service-mesh/) | 05-31 | — | `read` | `ecosystem` | The first serious service-mesh post on this blog: the problems microservices create at number, and what a mesh moves out of the application. |
| [Kubernetes 1.7: Security Hardening, Stateful Application Updates and Extensibility](https://kubernetes.io/blog/2017/06/kubernetes-1-7-security-hardening-stateful-application-extensibility-updates/) | 06-30 | 1.7 | `skip` | `meta` | Release announcement. |
| [How Watson Health Cloud Deploys Applications with Kubernetes](https://kubernetes.io/blog/2017/07/how-watson-health-cloud-deploys/) | 07-14 | — | `read` | `ecosystem` | Sidecars and a shared namespace to meet healthcare compliance, and the density argument against the virtual machines it replaced. |
| [Happy Second Birthday: A Kubernetes Retrospective](https://kubernetes.io/blog/2017/07/happy-second-birthday-kubernetes/) | 07-28 | — | `read` | `history` | Two-year retrospective with contribution figures — the project's own account of how fast it grew. |
| [Kompose Helps Developers Move Docker Compose Files to Kubernetes](https://kubernetes.io/blog/2017/08/kompose-helps-developers-move-docker/) | 08-10 | — | `read` | `tooling` | Compose files converted to Kubernetes objects, on the tool graduating from the incubator into the project proper. |
| [High Performance Networking with EC2 Virtual Private Clouds](https://kubernetes.io/blog/2017/08/high-performance-networking-with-ec2/) | 08-11 | — | `skip` | `ecosystem` | Vendor networking product preview addressing EC2 VPC routing limits. |
| [Kubernetes Meets High-Performance Computing](https://kubernetes.io/blog/2017/08/kubernetes-meets-high-performance/) | 08-22 | — | `read` | `sched` | Why HPC schedulers and Kubernetes disagree about what a unit of work is, and the approaches taken to run both on one cluster. |
| [Windows Networking at Parity with Linux for Kubernetes](https://kubernetes.io/blog/2017/09/windows-networking-at-parity-with-linux/) | 09-08 | 1.8 | `read` | `net` | Windows containers reaching networking parity; the lab has no Windows nodes to see it on. |
| [Introducing the Resource Management Working Group](https://kubernetes.io/blog/2017/09/introducing-resource-management-working/) | 09-21 | 1.8 | `read` | `nodes` | The working group that produced CPU manager, device plugins and topology manager — the seed for every hardware-aware scheduling feature that followed. |
| [Kubernetes StatefulSets & DaemonSets Updates](https://kubernetes.io/blog/2017/09/kubernetes-statefulsets-daemonsets/) | 09-27 | 1.7 | `walk` | `api` | DaemonSet and StatefulSet update strategies, worked through ZooKeeper, Kafka and a node exporter. Three defaults moved underneath it: `apps/v1beta1` and `v1beta2` are gone, `spec.selector` became required and immutable, and 1.9 flipped cascading delete from orphan to background. The post's manifests apply against nothing at the pin. |
| [Kubernetes 1.8: Security, Workloads and Feature Depth](https://kubernetes.io/blog/2017/09/kubernetes-18-security-workloads-and/) | 09-29 | 1.8 | `skip` | `meta` | Release announcement. |
| [Kubernetes Community Steering Committee Election Results](https://kubernetes.io/blog/2017/10/kubernetes-community-steering-committee-election-results/) | 10-05 | — | `skip` | `meta` | Governance election results. |
| [Request Routing and Policy Management with the Istio Service Mesh](https://kubernetes.io/blog/2017/10/request-routing-and-policy-management/) | 10-10 | — | `read` | `ecosystem` | Request routing and policy rules over the same Bookinfo app; mesh configuration has been rewritten twice since. |
| [Introducing Software Certification for Kubernetes](https://kubernetes.io/blog/2017/10/software-conformance-certification/) | 10-19 | — | `read` | `meta` | Why a conformance mark was worth defining when sixty distributions claimed the name — an argument that still governs what may be called Kubernetes. |
| [Five Days of Kubernetes 1.8](https://kubernetes.io/blog/2017/10/five-days-of-kubernetes-18/) | 10-24 | 1.8 | `skip` | `meta` | Index post linking the 1.8 series. |
| [kubeadm v1.8 Released: Introducing Easy Upgrades for Kubernetes Clusters](https://kubernetes.io/blog/2017/10/kubeadm-v18-released/) | 10-25 | 1.8 | `walk` | `tooling` | `kubeadm upgrade` introduced here, against a control plane the post expects to become self-hosted — a word that appears nowhere in the pinned documentation. `kubeadm alpha phase` is now `kubeadm init phase`, and the config API these flags feed has reached `v1beta4`. An upgrade is the one cluster-lifecycle operation the lab can run end to end. |
| [It Takes a Village to Raise a Kubernetes](https://kubernetes.io/blog/2017/10/it-takes-village-to-raise-kubernetes/) | 10-26 | 1.8 | `skip` | `meta` | Release-lead retrospective on running the release. |
| [Using RBAC, Generally Available in Kubernetes v1.8](https://kubernetes.io/blog/2017/10/using-rbac-generally-available-18/) | 10-28 | 1.8 | `walk` | `security` | RBAC at GA, with the ladder's discontinuities intact: `v1alpha1` was disabled by default in 1.8 and now fails as `no matches for kind` rather than as deprecated, and `--authorization-rbac-super-user` is gone in favour of `system:masters`. The trap worth walking is that `--authorization-mode` still defaults to `AlwaysAllow`, so a hand-rolled apiserver ignores every Role in this post. |
| [Enforcing Network Policies in Kubernetes](https://kubernetes.io/blog/2017/10/enforcing-network-policies-in-kubernetes/) | 10-30 | 1.7 | `walk` | `net` | NetworkPolicy went stable here, and the `net.beta.kubernetes.io/network-policy` namespace annotation that used to switch isolation on is gone — the 1.7 notes warned that policies inert under the annotation model start enforcing. Observable in the lab on any CNI that implements it. |
| [Kubernetes the Easy Way](https://kubernetes.io/blog/2017/11/kubernetes-easy-way/) | 11-01 | — | `skip` | `ecosystem` | Vendor tutorial pairing a hosted cluster with a hosted CI product. |
| [Containerd Brings More Container Runtime Options for Kubernetes](https://kubernetes.io/blog/2017/11/containerd-container-runtime-options-kubernetes/) | 11-02 | 1.8 | `walk` | `nodes` | containerd as an alternative to Docker under CRI, written while Docker was still the default; the post now carries the site's own dockershim deprecation banner. `docker ps` on a modern node returns success and an empty list, which is the quietest failure in the archive, and the lab's own nodes already run containerd. |
| [Securing Software Supply Chain with Grafeas](https://kubernetes.io/blog/2017/11/securing-software-supply-chain-grafeas/) | 11-03 | — | `read` | `security` | Supply-chain metadata as a first-class API, three years before the attestation formats that answer the same question today. |
| [Kubernetes is Still Hard (for Developers)](https://kubernetes.io/blog/2017/11/kubernetes-is-still-hard-for-developers/) | 11-15 | — | `skip` | `meta` | Conference talk trailer with a video embed. |
| [Certified Kubernetes Conformance Program: Launch Celebration Round Up](https://kubernetes.io/blog/2017/11/certified-kubernetes-conformance/) | 11-16 | — | `skip` | `meta` | Round-up of the first certified distributions. |
| [Autoscaling in Kubernetes](https://kubernetes.io/blog/2017/11/autoscaling-in-kubernetes/) | 11-17 | — | `skip` | `meta` | Conference talk trailer with a video embed. |
| [PaddlePaddle Fluid: Elastic Deep Learning on Kubernetes](https://kubernetes.io/blog/2017/12/paddle-paddle-fluid-elastic-learning/) | 12-06 | — | `skip` | `ecosystem` | Vendor deep-learning release with an elastic scheduling controller. |
| [Using eBPF in Kubernetes](https://kubernetes.io/blog/2017/12/using-ebpf-in-kubernetes/) | 12-07 | — | `read` | `net` | What eBPF is and why the networking and tracing layers were moving into it — the direction that produced the nftables and eBPF dataplanes that followed. |
| [Kubernetes 1.9: Apps Workloads GA and Expanded Ecosystem](https://kubernetes.io/blog/2017/12/kubernetes-19-workloads-expanded-ecosystem/) | 12-15 | 1.9 | `skip` | `meta` | Release announcement. |
| [Introducing Kubeflow - A Composable, Portable, Scalable ML Stack Built for Kubernetes](https://kubernetes.io/blog/2017/12/introducing-kubeflow-composable/) | 12-21 | — | `read` | `ecosystem` | A composable ML stack assembled from Kubernetes primitives, and the hand-rolled deployments it was arguing against. |

## Exercises

Eight `walk` verdicts, numbered in publication order. All eight are written. The rubric they
are authored against was ratified in [#57](https://github.com/k3ii/k8s-academy/issues/57); the
section order and the ladder they use were amended in
[#78](https://github.com/k3ii/k8s-academy/issues/78).

| # | exercise | state |
|---|---|---|
| 01 | [The four cases in this post are now five, the fifth is described by two reference pages that contradict each other about whether it can happen, and the whole table of cloud defaults died on one schedule](01-dynamic-provisioning-and-storage-classes-kubernetes.md) | written |
| 02 | [Two of this post's four affinity examples cannot be applied, the word "slightly" hides the whole difference between a filter and a score, and the page that replaced it still tells you to switch off a field through a gate that is locked on](02-advanced-scheduling-in-kubernetes.md) | written |
| 03 | [Every JSON value in this post carries typographic quotation marks, so none of the four configurations could ever have been parsed, the last code fence is never closed so the post ends inside it, and the only name that survived the rewrite is the one that stopped describing what answers](03-configuring-private-dns-zones-upstream-nameservers-kubernetes.md) | written |
| 04 | [The two sentences this post is most emphatic about are still printed almost word for word on the task pages that replaced it, both were made false by the concept pages next door, and the symmetry it claims between the two controllers is now an asymmetry documented in two places that never mention each other](04-kubernetes-statefulsets-daemonsets.md) | written |
| 05 | [Every forecast in this post has been answered and none of them in its own terms: the feature it wanted to make the default is gone so completely that its name now belongs to the mechanism it was built to replace, the command it promised for v1.9 arrived four times under four other verbs, and the one-command upgrade is one command inside sixteen spread across two pages](05-kubeadm-v18-released.md) | written |
| 06 | [The rule at the centre of this post names an API group that now serves nothing and the API server accepts it without a warning, two of the post's other manifests never worked and `kubectl` rather than the API server is what catches them, and the one property the post praises — that RBAC rules are purely additive — is why one flag on your own control plane makes every Role here decoration](06-using-rbac-generally-available-18.md) | written |
| 07 | [The first of this post's two manifests is still exactly right, the second stopped being right in the release the post was written to announce, and on the cluster this curriculum builds neither of them does anything at all — the object is stored, the command reports success, and the API has no field anywhere in which to say that nothing is enforcing it](07-enforcing-network-policies-in-kubernetes.md) | written |
| 08 | [The project this post announces survives in the pinned documentation as a tab id, a PNG filename and an AppArmor profile; the runtime it was written to displace has six migration pages, a glossary entry and a note saying it does not implement CRI at all; and whether this curriculum's two hand-edits to `config.toml` match anything is a test of a containerd major version the pin says will stop working in v1.38](08-containerd-container-runtime-options-kubernetes.md) | written |
