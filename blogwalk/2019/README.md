# 2019 — the census

52 posts, 2019-01-14 to 2019-12-09. Seven percent of the corpus and **26% fewer posts than
2018**, the second contraction the sweep has measured. Kubernetes 1.13 through 1.17 are in scope, four of
them shipped inside the year. This is **the year the archive started going wrong in a new way**:
not versions drifting out from under a post, but posts that were broken on the day they were
published — see [the method](../README.md).

**Yield: 8 `walk`**, on the floor of the [8–15 band](../README.md#the-budget). 24 `read`, **1
`dated`**, 19 `skip`.

**The band lands on its floor for the second time in six years, and again nothing was cut to get
there.** 2017 landed on 8 with 53 posts; 2019 lands on 8 with 52. Both are years where the
release cadence was steady and the blog was mostly reporting it. The 8 here are what survived
two filters that had nothing to do with space: redundancy against the years already censused —
CSI's GA, local persistent volumes' GA, snapshots' beta and priority-and-preemption's GA are
four of 2019's largest events and all four are `read`, because 2018's census already walks the
ground each announces — and the vendor rule, which took the year's best-written walkthrough away
from the `walk` column on its last screen.

**The best find in the year is not a version drift. It is two posts whose YAML has never
applied to any cluster.** [Raw Block Volume support to Beta](https://kubernetes.io/blog/2019/03/07/raw-block-volume-support-to-beta/)
indents `storage: 1Gi` as a sibling of `requests` rather than a child, and prints `“3600”` in
typographic quotes. [Future of CRDs: Structural Schemas](https://kubernetes.io/blog/2019/06/20/crd-structural-schema/)
has twelve code-fence lines carrying curly quotes and writes `properties` with the colon missing.
A grep across all 52 of the year's posts finds smart quotes inside code fences in **exactly these
two files and no others** — and they are the two that earned walks. The rubric has a verdict for
a post that has aged and a verdict for a post that needs hardware; it has no name for a post that
was wrong at publication, and the reader who follows it hits a parse error before reaching
anything Kubernetes has to say. Both stay `walk`: fixing the manifest is the first thing the
exercise teaches.

**The second-best is a removals post whose own removals have been removed.**
[Deprecated APIs Removed In 1.16](https://kubernetes.io/blog/2019/07/18/api-deprecations-in-1-16/)
is the most consequential post of the year and names three migration targets. Two of them are
gone at the pin: `PodSecurityPolicy` in `policy/v1beta1`, removed in v1.25, and `Ingress` in
`networking.k8s.io/v1beta1`, unserved since v1.22. Its remediation tool has moved too — `kubectl
convert` is "not installed by default" at the pin and ships as a separate `kubectl-convert`
plugin. A post about how to survive an API removal is now a post you cannot follow without a
second migration, which is the archive's central lesson delivered by accident.

**And the archive has begun annotating itself.** The pinned copy of
[APIServer dry-run and kubectl diff](https://kubernetes.io/blog/2019/01/14/apiserver-dry-run-and-kubectl-diff/)
carries a note, added long after publication, saying the flag it exists to teach was deprecated
in v1.18. Every earlier year's staleness had to be discovered by reading the source tree; this is
the first time a post says it about itself. It does not close the diff — the `DryRun` gate the
post tells you to enable went stable and is `removed: true`, and the webhook API it depends on
stopped being served in v1.22, neither of which the note mentions — but it is the first crack in
the assumption that the posts are silent about their own age.

**`dated` earns one row.** [Hardware Accelerated SSL/TLS Termination in Ingress Controllers](https://kubernetes.io/blog/2019/04/24/hardware-accelerated-ssltls-termination-in-ingress-controllers-using-kubernetes-device-plugins-and-runtimeclass/)
passes both tests: a genuine end-to-end build — device plugin, `RuntimeClass`, Ingress
controller, OpenSSL engine — that needs an Intel QuickAssist card passed through an IOMMU to a
Kata sandbox. No amount of RAM inside the 9.5GB ceiling produces a crypto accelerator. The
verdict is now at 10 rows in 363.

The 19 rejects are four release announcements, ten community-and-contributor posts — summits,
elections, registrations, schedules, a docs survey — and five vendor or ecosystem posts that
record no decision. At **37% the reject rate steadies** after 2018's rise: 48%, 42%, 38%, 40%,
37%. `meta` still leads at 17 rows and 33%, barely down from 2018's 34%, and the organisational
genre that arrived in 2018 is now permanent furniture rather than news.

Three things in the topic tallies are worth the taxonomy's attention. **`tooling` reaches 8 rows
and 15%, its highest share in any year censused** — kubeadm, minikube, MicroK8s, the E2E
framework as a library, two client libraries and `kubectl diff` — which is what a project looks
like once the API has stopped moving and the arguments move to the edges. **`net` falls to a
single row, its lowest**, and that row is a debugging story rather than a feature. And **`obs`
earns nothing at all, the first empty observability column in six years censused** — 9%, 3%, 2%,
1%, now 0%. The slot was added to the vocabulary during the prototype because 2015 was full of
it; five years later the blog has stopped writing about it entirely. `storage` holds at 7 rows,
its share rising to 13% on a smaller year, and `etcd` earns a row for the second year running.

## Census

Verdicts and topics are defined in [`../README.md`](../README.md#the-census). Every post has a
row, and a row's title always links the post — never the exercise file, so the row never
changes once written. The **Exercises** table below is the progress record.

| post | date | k8s | verdict | topic | why |
|---|---|---|---|---|---|
| [APIServer dry-run and kubectl diff](https://kubernetes.io/blog/2019/01/14/apiserver-dry-run-and-kubectl-diff/) | 01-14 | 1.13 | `walk` | `tooling` | The single command the post exists to teach, `kubectl apply --server-dry-run`, has **zero hits** in the pinned docs — deprecated in v1.18 for `--dry-run=server`, and the post carries a later-added editor's note saying so. Underneath it, two more: the `DryRun` gate it tells you to set went stable in 1.19 and is `removed: true`, and the `sideEffects` field it tells you to add belongs to `admissionregistration.k8s.io/v1beta1`, no longer served since v1.22. |
| [Container Storage Interface (CSI) for Kubernetes GA](https://kubernetes.io/blog/2019/01/15/container-storage-interface-ga/) | 01-15 | 1.13 | `read` | `storage` | CSI reaches GA thirteen months after the beta post 2018 already walks; the driver-side facts are the same ones that exercise carries. Read for the deprecation-policy argument about what GA buys a storage vendor, not for the commands. |
| [Update on Volume Snapshot Alpha for Kubernetes](https://kubernetes.io/blog/2019/01/17/update-volume-snapshot-alpha/) | 01-17 | 1.13 | `read` | `storage` | A breaking change inside an alpha: CSI v1.0 replaced `SnapshotStatus` with a boolean `ReadyToUse`. Worth reading as evidence that alpha means it, but the terrain is the same as 2018's snapshot walk and the beta post below. |
| [Poseidon-Firmament Scheduler – Flow Network Graph Based Scheduler](https://kubernetes.io/blog/2019/02/06/poseidon-firmament-scheduler-announcement/) | 02-06 | — | `read` | `sched` | A flow-network scheduler offered as a drop-in alongside kube-scheduler, argued against queue-based placement with Borg, Quasar and Quincy named as the alternatives. The project is archived; the argument for min-cost-max-flow placement is not. |
| [Runc and CVE-2019-5736](https://kubernetes.io/blog/2019/02/11/runc-cve-2019-5736/) | 02-11 | — | `walk` | `security` | The emergency mitigation the project published cannot be applied at the pin. Its cluster-wide answer to a container escape is a `policy/v1beta1` PodSecurityPolicy with `rule: 'MustRunAsNonRoot'` — deprecated in v1.21 and **removed in v1.25**, with the pinned docs carrying a tombstone page and a migration guide instead. The per-Pod `securityContext.runAsUser: 1000` in the same post still works, so the post half-applies and half-vanishes. |
| [Building a Kubernetes Edge (Ingress) Control Plane for Envoy v2](https://kubernetes.io/blog/2019/02/12/building-a-kubernetes-edge-control-plane-for-envoy-v2/) | 02-12 | — | `read` | `ecosystem` | Ambassador's edge proxy rebuilt on Envoy's v2 xDS: the post names what it moved off, why per-request config regeneration was the wrong shape, and what ADS bought. A decision with its rejected alternative on the record, so it clears the vendor bar. |
| [Automate Operations on your Cluster with OperatorHub.io](https://kubernetes.io/blog/2019/02/28/automate-operations-on-your-cluster-with-operatorhub/) | 02-28 | — | `skip` | `ecosystem` | A registry launch for Operators, jointly announced by four vendors. No decision, no alternatives. |
| [Raw Block Volume support to Beta](https://kubernetes.io/blog/2019/03/07/raw-block-volume-support-to-beta/) | 03-07 | 1.13 | `walk` | `storage` | The post's PVC manifest has never applied to any cluster: `storage: 1Gi` is indented as a sibling of `requests`, not a child, and its Pod prints `“3600”` in typographic quotes. Fix both and the version diff starts — the `BlockVolume` gate it graduates went stable in 1.18 and is `removed: true`, and of the nine in-tree plugins it lists as supporting raw block, only `local` still exists at the pin. |
| [Kubernetes Setup Using Ansible and Vagrant](https://kubernetes.io/blog/2019/03/15/kubernetes-setup-using-ansible-and-vagrant/) | 03-15 | 1.13 | `read` | `tooling` | A real multi-node bring-up, but the technique is kubeadm underneath Ansible and the version pins are 1.13.3. Redundant against 2017's kubeadm exercise and against the lab's own topology work. |
| [KubeEdge, a Kubernetes Native Edge Computing Framework](https://kubernetes.io/blog/2019/03/19/kubeedge-k8s-based-edge-intro/) | 03-19 | — | `skip` | `ecosystem` | An edge-computing platform announcing that both halves are now open source. Contrasts itself with unnamed "light weight kubernetes platforms" and stops there. |
| [A Look Back and What's in Store for Kubernetes Contributor Summits](https://kubernetes.io/blog/2019/03/20/a-look-back-and-whats-in-store-for-kubernetes-contributor-summits/) | 03-20 | — | `skip` | `meta` | Contributor-summit retrospective and calendar. |
| [A Guide to Kubernetes Admission Controllers](https://kubernetes.io/blog/2019/03/21/a-guide-to-kubernetes-admission-controllers/) | 03-21 | 1.13 | `read` | `security` | The best-written admission-controller walkthrough in the archive, and the walk is a vendor's: `./deploy.sh` from `stackrox/admission-controller-webhook-demo`, a company acquired in 2021. Exactly the dependency the vendor rule's `walk` bar exists to refuse. Its `admissionregistration.k8s.io/v1beta1` webhook config is unserved since v1.22 anyway, and 2018 already walks that ground. |
| [Kubernetes End-to-end Testing for Everyone](https://kubernetes.io/blog/2019/03/22/e2e-testing-for-everyone/) | 03-22 | 1.13 | `read` | `tooling` | Using the Kubernetes E2E framework as a library to test a component that lives outside the tree — the argument that made CSI drivers testable. Go development rather than cluster work. |
| [Kubernetes 1.14: Production-level support for Windows Nodes, Kubectl Updates, Persistent Local Volumes GA](https://kubernetes.io/blog/2019/03/25/kubernetes-1-14-release-announcement/) | 03-25 | 1.14 | `skip` | `meta` | Release announcement. |
| [Running Kubernetes locally on Linux with Minikube - now with Kubernetes 1.14 support](https://kubernetes.io/blog/2019/03/28/running-kubernetes-locally-on-linux-with-minikube/) | 03-28 | 1.14 | `read` | `tooling` | Minikube 1.0 as a local cluster. Still maintained, and the lab is kubeadm on Proxmox rather than a VM-per-cluster; the `--vm-driver` flag it uses has since become `--driver`. |
| [kube-proxy Subtleties: Debugging an Intermittent Connection Reset](https://kubernetes.io/blog/2019/03/29/kube-proxy-subtleties-debugging-an-intermittent-connection-resets/) | 03-29 | 1.15 | `walk` | `net` | The clearest packet-level explanation of Service NAT in the archive — SNAT, DNAT, and the conntrack `INVALID` state that lets a rewritten reply reach a client that then RSTs the server. Two things moved: the mitigation DaemonSet it ships is `apiVersion: extensions/v1beta1`, an API unserved since v1.16, and the sysctl it writes by hand inside a privileged container is now a kube-proxy flag, `--conntrack-tcp-be-liberal`, described at the pin as setting `nf_conntrack_tcp_be_liberal` to 1. |
| [Kubernetes v1.14 delivers production-level support for Windows nodes and Windows containers](https://kubernetes.io/blog/2019/04/01/kubernetes-v1-14-delivers-production-level-support-for-nodes-and-windows-containers/) | 04-01 | 1.14 | `read` | `nodes` | Windows worker nodes reach production support. No walkthrough in it, and the lab is Linux — an announcement with a feature list, so `read` rather than `dated`. |
| [Kubernetes 1.14: Local Persistent Volumes GA](https://kubernetes.io/blog/2019/04/04/local-persistent-volumes-ga/) | 04-04 | 1.14 | `read` | `storage` | Local persistent volumes reach GA with `volumeBindingMode: WaitForFirstConsumer` and the external static provisioner. Alpha 1.7, beta 1.10, GA 1.14, and every manifest in it still applies verbatim at the pin — a ladder with no discontinuity in it. |
| [Process ID Limiting for Stability Improvements in Kubernetes 1.14](https://kubernetes.io/blog/2019/04/15/pid-limiting/) | 04-15 | 1.14 | `walk` | `nodes` | No commands and no YAML in the post at all, and it still earns a walk on the second clause: a fork bomb starving a node of PIDs is the most observable failure in the year. The `SupportPodPidsLimit` gate it announces reads alpha 1.10, beta and default-true 1.14, stable 1.20, `removed: true` at the pin, where the control is `podPidsLimit` in the kubelet's config file and PID reservation is `--system-reserved=pid=`. |
| [Pod Priority and Preemption in Kubernetes](https://kubernetes.io/blog/2019/04/16/pod-priority-and-preemption-in-kubernetes/) | 04-16 | 1.14 | `read` | `sched` | Priority and preemption at GA, argued as economics against the cluster autoscaler: preemption is seconds, a new node is minutes, and a negative-priority workload fills the holes for free. The argument is the payload; the post carries no commands and the feature climbed alpha → beta → GA without surprising anyone. |
| [The Future of Cloud Providers in Kubernetes](https://kubernetes.io/blog/2019/04/17/future-of-cloud-providers/) | 04-17 | — | `read` | `history` | SIG Cloud Provider's charter, written while the in-tree providers were still in the tree. The decision it records — integrations become add-ons, not core — is the one that ends with the legacy providers deleted, so this is the reasoning behind a removal read before it happened. |
| [Introducing kube-iptables-tailer: Better Networking Visibility in Kubernetes Clusters](https://kubernetes.io/blog/2019/04/19/introducing-kube-iptables-tailer/) | 04-19 | — | `skip` | `ecosystem` | A tool that tails iptables drop logs and turns them into Pod events. Names the problem, names no alternative. |
| [Hardware Accelerated SSL/TLS Termination in Ingress Controllers using Kubernetes Device Plugins and RuntimeClass](https://kubernetes.io/blog/2019/04/24/hardware-accelerated-ssltls-termination-in-ingress-controllers-using-kubernetes-device-plugins-and-runtimeclass/) | 04-24 | 1.14 | `dated` | `nodes` | Both `dated` tests hold. It is an end-to-end setup — device plugin, `RuntimeClass`, HAproxy Ingress, OpenSSL dynamic engine — and it needs an Intel QuickAssist PCIe card passed through an IOMMU to a Kata Containers sandbox. No amount of RAM inside the 9.5GB ceiling produces a crypto accelerator. |
| [How You Can Help Localize Kubernetes Docs](https://kubernetes.io/blog/2019/04/26/latest-on-localization/) | 04-26 | — | `skip` | `meta` | How to join a docs localisation team. |
| [Join us for the 2019 KubeCon Diversity Lunch & Hack](https://kubernetes.io/blog/2019/05/02/kubecon-diversity-lunch-and-hack/) | 05-02 | — | `skip` | `meta` | Conference lunch registration. |
| [Cat shirts and Groundhog Day: the Kubernetes 1.14 release interview](https://kubernetes.io/blog/2019/05/13/kubernetes-1-14-release-interview/) | 05-13 | 1.14 | `read` | `meta` | The 1.14 release manager on the release process, on record. `read` on the maintainer-interview rule read for its spirit — see 2018, where the same call was made and flagged: a release manager owns a process, not a component. |
| [Expanding our Contributor Workshops](https://kubernetes.io/blog/2019/05/14/expanding-our-contributor-workshops/) | 05-14 | — | `skip` | `meta` | Workshop registration. |
| [Kubernetes, Cloud Native, and the Future of Software](https://kubernetes.io/blog/2019/05/17/kubernetes-cloud-native-and-the-future-of-software/) | 05-17 | — | `read` | `history` | Google's five-year retrospective, from the first commit through DockerCon to the CNCF. First-party account of the project's own origin; the business framing around it is why it is not more than that. |
| [Kyma - extend and build on Kubernetes with ease](https://kubernetes.io/blog/2019/05/23/kyma-extend-and-build-on-kubernetes-with-ease/) | 05-23 | — | `skip` | `ecosystem` | A platform layer on Kubernetes, announced as such. |
| [Join us at the Contributor Summit in Shanghai](https://kubernetes.io/blog/2019/06/12/contributor-summit-shanghai/) | 06-12 | — | `skip` | `meta` | Summit registration. |
| [Kubernetes 1.15: Extensibility and Continuous Improvement](https://kubernetes.io/blog/2019/06/19/kubernetes-1-15-release-announcement/) | 06-19 | 1.15 | `skip` | `meta` | Release announcement. |
| [Future of CRDs: Structural Schemas](https://kubernetes.io/blog/2019/06/20/crd-structural-schema/) | 06-20 | 1.15 | `walk` | `api` | The post that decides what a CRD is allowed to be, and the only one in the year whose worked example is an actual attack: an unspecified `privileged: true` persisted into etcd, harmless until the field is implemented, then executed. Twelve of its code-fence lines carry typographic quotes and its `properties` keys are missing colons, so nothing in it parses. Fix that and the ladder has moved past it: `apiextensions.k8s.io/v1beta1` is unserved since v1.22, and at `v1` a structural schema is not optional as the post says but mandatory. |
| [Introducing Volume Cloning Alpha for Kubernetes](https://kubernetes.io/blog/2019/06/21/volume-cloning-alpha/) | 06-21 | 1.15 | `read` | `storage` | Cloning a PVC by naming it as a `dataSource`. Alpha here, GA later, no surprises on the way, and it needs a CSI driver that implements cloning. |
| [Automated High Availability in kubeadm v1.15: Batteries Included But Swappable](https://kubernetes.io/blog/2019/06/24/kubeadm-ha-v115/) | 06-24 | 1.15 | `walk` | `tooling` | HA control planes and, quietly, the cert commands. `kubeadm alpha certs renew` and `kubeadm alpha certs check-expiration` — the post's own examples — have **zero hits** at the pin, where the same subcommands are `kubeadm certs renew`, 17 files' worth; the post predicted the move itself in a sentence about `kubeadm alpha` graduating. The `v1beta2` config format it introduces is gone too, leaving `v1beta3` and `v1beta4`. None of this needs three control-plane nodes to observe. |
| [Recap of Kubernetes Contributor Summit Barcelona 2019](https://kubernetes.io/blog/2019/06/25/recap-of-contributor-summit-bcn-2019/) | 06-25 | — | `skip` | `meta` | Summit recap. |
| [Deprecated APIs Removed In 1.16: Here’s What You Need To Know](https://kubernetes.io/blog/2019/07/18/api-deprecations-in-1-16/) | 07-18 | 1.16 | `walk` | `api` | The year's most consequential post, and two of the three migrations it tells you to make have themselves been undone. `PodSecurityPolicy` in `policy/v1beta1` — its migration target — was removed in v1.25, and `Ingress` in `networking.k8s.io/v1beta1` — its other one — stopped being served in v1.22. Its remediation tool, `kubectl convert`, is at the pin "not installed by default" and ships as a separate `kubectl-convert` plugin. The `--runtime-config` rehearsal flag it gives you names group-versions the apiserver no longer has. |
| [Get started with Kubernetes (using Python)](https://kubernetes.io/blog/2019/07/23/get-started-with-kubernetes-using-python/) | 07-23 | — | `read` | `tooling` | Containerise a Flask app, push it, run it. A competent beginner's path that the lab's own onboarding already covers, on Docker Desktop rather than a cluster you built. |
| [OPA Gatekeeper: Policy and Governance for Kubernetes](https://kubernetes.io/blog/2019/08/06/OPA-Gatekeeper-Policy-and-Governance-for-Kubernetes/) | 08-06 | — | `read` | `security` | Gatekeeper's move from an OPA sidecar to a webhook with CRD-backed constraints, with the earlier design named and rejected. Clears the vendor bar as a decision record; policy enforcement is a project that must stay maintained for any exercise to survive it. |
| [Announcing etcd 3.4](https://kubernetes.io/blog/2019/08/30/announcing-etcd-3-4/) | 08-30 | — | `read` | `etcd` | etcd 3.4 from its maintainers: pre-vote, learner members, a backend commit that no longer blocks reads. The second `etcd` row in the year after 2018 broke the tag's silence, and the first two consecutive years it has earned one. |
| [Kubernetes 1.16: Custom Resources, Overhauled Metrics, and Volume Extensions](https://kubernetes.io/blog/2019/09/18/kubernetes-1-16-release-announcement/) | 09-18 | 1.16 | `skip` | `meta` | Release announcement — the release whose removals the July post above is entirely about. |
| [Contributor Summit San Diego Registration Open!](https://kubernetes.io/blog/2019/09/24/san-diego-contributor-summit/) | 09-24 | — | `skip` | `meta` | Summit registration. |
| [2019 Steering Committee Election Results](https://kubernetes.io/blog/2019/10/03/2019-steering-committee-election-results/) | 10-03 | — | `skip` | `meta` | Election results. |
| [Contributor Summit San Diego Schedule Announced!](https://kubernetes.io/blog/2019/10/10/contributor-summit-san-diego-schedule/) | 10-10 | — | `skip` | `meta` | Summit schedule. |
| [Kubernetes Documentation Survey](https://kubernetes.io/blog/2019/10/29/kubernetes-documentation-end-user-survey/) | 10-29 | — | `skip` | `meta` | Docs survey results. |
| [Grokkin' the Docs](https://kubernetes.io/blog/2019/11/05/Grokkin-the-Docs/) | 11-05 | — | `skip` | `meta` | A new contributor's field notes on the docs community. |
| [Develop a Kubernetes controller in Java](https://kubernetes.io/blog/2019/11/26/Develop-A-Kubernetes-Controller-in-Java/) | 11-26 | — | `read` | `tooling` | A controller-builder for the Java client, written for people who cannot use `controller-runtime`. Worth reading for what a reconcile loop needs from a client library. |
| [Running Kubernetes locally on Linux with Microk8s](https://kubernetes.io/blog/2019/11/26/kubernetes-with-microk8s/) | 11-26 | 1.14 | `read` | `tooling` | MicroK8s as a snap rather than a VM, argued against Minikube on portability and footprint. The comparison is the content. |
| [Gardener Project Update](https://kubernetes.io/blog/2019/12/02/gardener-project-update/) | 12-02 | — | `read` | `ecosystem` | Kubernetes control planes running as Pods inside other clusters, and the post opens by answering why a handful of large clusters is not the same thing. A decision with its rejected alternative stated in the first screen. |
| [When you're in the release team, you're family: the Kubernetes 1.16 release interview](https://kubernetes.io/blog/2019/12/06/kubernetes-1-16-release-interview/) | 12-06 | 1.16 | `read` | `meta` | The 1.16 release lead on the release the post above describes. Same call as the 1.14 interview. |
| [Kubernetes 1.17 Feature: Kubernetes In-Tree to CSI Volume Migration Moves to Beta](https://kubernetes.io/blog/2019/12/09/kubernetes-1-17-feature-csi-migration-beta/) | 12-09 | 1.17 | `read` | `storage` | In-tree volume plugins start being redirected to CSI drivers behind the user's back, with a translation library keeping old manifests working. The end state is visible at the pin — the in-tree plugins are gone — but nothing here is walkable without a cloud provider's disks. |
| [Kubernetes 1.17 Feature: Kubernetes Volume Snapshot Moves to Beta](https://kubernetes.io/blog/2019/12/09/kubernetes-1-17-feature-cis-volume-snapshot-beta/) | 12-09 | 1.17 | `read` | `storage` | Snapshots reach beta, with the snapshot controller and validating webhook now separate deployments. `snapshot.storage.k8s.io/v1beta1` is history and 2018's snapshot walk already carries the point that these kinds are not in the cluster until someone installs them. |
| [Kubernetes 1.17: Stability](https://kubernetes.io/blog/2019/12/09/kubernetes-1-17-release-announcement/) | 12-09 | 1.17 | `skip` | `meta` | Release announcement. |

## Exercises

Eight `walk` verdicts, numbered in publication order. Three are written; the remaining five are
*pending* — an authoring ticket's to claim. The rubric they are authored against was ratified in
[#57](https://github.com/k3ii/k8s-academy/issues/57).

| # | exercise | state |
|---|---|---|
| 01 | [The flag that is not there any more](01-apiserver-dry-run-and-kubectl-diff.md) | written |
| 02 | [A mitigation that was itself removed](02-runc-cve-2019-5736.md) | written |
| 03 | [Neither manifest ever applied](03-raw-block-volume-support-to-beta.md) | written |
| 04 | A reply the client refuses | pending |
| 05 | The fork bomb and the field that stops it | pending |
| 06 | A schema that lets anything through | pending |
| 07 | The subcommand that lost its alpha | pending |
| 08 | Three doors, and two of them are bricked up | pending |
