# 2020 — the census

56 posts, 2020-01-08 to 2020-12-21. Seven percent of the corpus and **8% more posts than 2019**,
only the second expansion the sweep has measured. Kubernetes 1.15 through 1.20 are in scope,
three of them shipped inside the year. This is **the year the archive stopped only aging and
started arguing with itself**: a post that promises something the project later reversed, and a
post edited to strike a sentence out rather than correct it — see [the method](../README.md).

**Yield: 9 `walk`**, one above the floor of the [8–15 band](../README.md#the-budget). 23 `read`, **1
`dated`**, 23 `skip`.

**The best find in the year is a promise the project broke.**
[Scaling Kubernetes Networking With EndpointSlices](https://kubernetes.io/blog/2020/09/02/scaling-kubernetes-networking-with-endpointslices/)
says it twice and in as many words: the Endpoints API "will continue to be considered generally
available and stable", and "The Endpoints API is not going away." At the pin the API reference
for that object opens "Deprecated: This API is deprecated in v1.33+. Use discoveryv1.EndpointSlice."
Every staleness the census has recorded so far is a post overtaken by a decision taken after it
was written. This is different in kind: the post makes a forecast, on the project's own
blog, about the project's own plans, and the project went the other way. The rubric has a verdict
for a post that has aged and one for a post that was wrong when it was published; it has no name
for a post that was right at publication and was made wrong by the people who published it.

**The second is the archive editing itself in public.** 2019 gave the first later-added editorial
note attached to a post. 2020 goes further twice over.
[Don't Panic: Kubernetes and Docker](https://kubernetes.io/blog/2020/12/02/dont-panic-kubernetes-and-docker/)
— the most-read thing the project has ever published — contains a sentence with a clause struck
through inside the body: removal is "currently planned for the 1.22 release in late 2021", the
whole clause wrapped in `<del>`. It went in v1.24. Its companion
[Dockershim Deprecation FAQ](https://kubernetes.io/blog/2020/12/02/dockershim-faq/) carries an
inline "*Update*: removal of dockershim is scheduled for Kubernetes v1.24" over an original that
named no release at all. A note beside a post says *this has aged*. A strikethrough inside a post
says *we said this and we were wrong*, and leaves the wrong thing legible underneath.

**Third: the ladder, broken in both directions, in the year the project wrote the ladder down.**
[Moving Forward From Beta](https://kubernetes.io/blog/2020/08/21/moving-forward-from-beta/)
explains the alpha → beta → stable progression and states flatly that "beta features are enabled
by default"; the pin has softened that to "Usually enabled by default, well-tested", because new
beta APIs stopped being on by default in v1.24. Six weeks earlier
[Warning: Helpful Warnings Ahead](https://kubernetes.io/blog/2020/09/03/warnings/) shipped a
feature gate that **has no alpha stage at all** — `WarningHeaders` starts at beta, default-true,
in 1.19. Two weeks after that,
[Introducing Structured Logs](https://kubernetes.io/blog/2020/09/04/kubernetes-1-19-Introducing-Structured-Logs/)
announced JSON log output as alpha in 1.19, and it is *still* marked alpha for v1.19 in the
pinned docs — six years stationary, while the klog flags the post writes against were deprecated
in v1.23 and removed in v1.26 underneath it. One feature skipped a rung, one never climbed one,
and both are in the same quarter as the post explaining what the rungs mean.

**And the year's headline event earns no walk.** Dockershim deprecation is the biggest Kubernetes
story of 2020 and both of its posts are `read`. Nothing in either breaks a manifest: the diff is
a date, a strikethrough, and a migration path that survives intact — `migrating-from-dockershim`
is six pages at the pin and `cri-dockerd` is documented as the supported way to keep the daemon.
The walk machinery detects manifests that stop applying and commands that stop existing, and the
defining change of the year is neither. It shows in the tallies: `nodes` takes 4 rows and **zero
`walk`s, the first year in the sweep where it earns none**.

**`dated` earns one row.** [Deploying External OpenStack Cloud Provider with Kubeadm](https://kubernetes.io/blog/2020/02/07/Deploying-External-OpenStack-Cloud-Provider-with-Kubeadm/)
passes both tests: fifty code fences of genuine bring-up — project, network, router, floating
IPs, security groups, kubeadm on CentOS, then the out-of-tree provider and Cinder CSI — that
needs an OpenStack cloud underneath before the first command runs. That is not a RAM problem the
9.5GB ceiling can be argued around, it is a second infrastructure layer. The verdict is now at 11
rows in 419.

The 23 rejects are three release announcements, two memorials, twelve community-and-contributor
posts, and six vendor or ecosystem posts recording no decision. At **41% the reject rate turns up**
for the first time since 2018: 48%, 42%, 38%, 40%, 37%, 41%. `meta` takes 21 rows and 38%, its
highest share since 2015, and the blog's centre of gravity in a pandemic year is visibly the
project talking about itself.

Three things in the topic tallies are worth the taxonomy's attention. **`ecosystem` collapses to
3 rows and 5%, its lowest share of any year censused** — 21%, 28%, 14%, 12%, now 5% — which is
the vendor genre draining out of the blog rather than the vendor rule working harder. **`obs`
returns from the empty column 2019 left**, with 3 rows and the first observability `walk` since
2016. And **`history` is empty for the first time**, alongside `etcd`: in a year with three
releases and a runtime deprecation, nobody wrote about where any of it came from.

## Census

Verdicts and topics are defined in [`../README.md`](../README.md#the-census). Every post has a
row, and a row's title always links the post — never the exercise file, so the row never
changes once written. The **Exercises** table below is the progress record.

| post | date | k8s | verdict | topic | why |
|---|---|---|---|---|---|
| [Testing of CSI drivers](https://kubernetes.io/blog/2020/01/08/csi-driver-testing/) | 01-08 | — | `read` | `tooling` | Reusing the in-tree storage test suites and `csi-sanity` against a third-party driver, and the sequel to 2019's *E2E Testing for Everyone*. Go development against a driver you already have, not cluster work. |
| [Remembering Brad Childs](https://kubernetes.io/blog/2020/01/10/Remembering-Brad-Childs/) | 01-10 | — | `skip` | `meta` | A memorial for a SIG Storage chair. |
| [Announcing the Kubernetes bug bounty program](https://kubernetes.io/blog/2020/01/14/kubernetes-bug-bounty-announcement/) | 01-14 | — | `read` | `security` | The bug bounty launch, and the only place in the archive where the project writes down what it considers its own attack surface — the in-scope and out-of-scope lists are a trust boundary stated out loud. No technique in it. |
| [Kubernetes on MIPS](https://kubernetes.io/blog/2020/01/15/Kubernetes-on-MIPS/) | 01-15 | — | `read` | `nodes` | A MIPS port carried by cross-compilation under QEMU, with a component table pinning `hyperkube` v1.14.3 from a vendor registry. `hyperkube` was itself discontinued after v1.18 and survives at the pin only as three incidental mentions, so the artefact the port is built around outlived neither the architecture nor the release. |
| [CSI Ephemeral Inline Volumes](https://kubernetes.io/blog/2020/01/21/csi-ephemeral-inline-volumes/) | 01-21 | 1.16 | `read` | `storage` | Inline volumes served straight by a CSI driver, with `volumeLifecycleModes` on CSIDriver. Superseded inside its own year by the generic-ephemeral post seven months later, which does the same job with any storage class; the `CSIInlineVolume` gate went stable in 1.25 and is `removed: true` at the pin. |
| [Reviewing 2019 in Docs](https://kubernetes.io/blog/2020/01/21/reviewing-2019-in-docs/) | 01-21 | — | `skip` | `meta` | SIG Docs year in review. |
| [KubeInvaders - Gamified Chaos Engineering Tool for Kubernetes](https://kubernetes.io/blog/2020/01/22/kubeinvaders-gamified-chaos-engineering-tool-for-kubernetes/) | 01-22 | — | `skip` | `ecosystem` | A chaos tool that renders Pods as Space Invaders. Fun, no decision. |
| [Deploying External OpenStack Cloud Provider with Kubeadm](https://kubernetes.io/blog/2020/02/07/Deploying-External-OpenStack-Cloud-Provider-with-Kubeadm/) | 02-07 | 1.15 | `dated` | `tooling` | Both `dated` tests hold. It is a full bring-up — OpenStack project, network, router, floating IPs, security groups, kubeadm on CentOS, then the out-of-tree cloud provider and Cinder CSI — 50 code fences of it, and it needs an OpenStack cloud underneath before the first command runs. That is not a RAM problem the 9.5GB ceiling can be argued around; it is a second infrastructure layer. |
| [Contributor Summit Amsterdam Schedule Announced](https://kubernetes.io/blog/2020/02/18/Contributor-Summit-Amsterdam-Schedule-Announced/) | 02-18 | — | `skip` | `meta` | Summit schedule. |
| [Bring your ideas to the world with kubectl plugins](https://kubernetes.io/blog/2020/02/28/bring-your-ideas-to-world-with-kubectl-plugins/) | 02-28 | — | `read` | `tooling` | Writing a `kubectl` plugin instead of patching `kubectl`, with the KEP-and-review cost of the alternative spelled out as the reason. The plugin mechanism and Krew both survive at the pin unchanged, so there is no diff to walk. |
| [Contributor Summit Amsterdam Postponed](https://kubernetes.io/blog/2020/03/04/Contributor-Summit-Delayed/) | 03-04 | — | `skip` | `meta` | Summit postponed. |
| [Kong Ingress Controller and Service Mesh: Setting up Ingress to Istio on Kubernetes](https://kubernetes.io/blog/2020/03/18/kong-ingress-controller-and-istio-service-mesh/) | 03-18 | — | `skip` | `ecosystem` | A vendor ingress controller in front of a service mesh. Product capabilities, no decision. |
| [Join SIG Scalability and Learn Kubernetes the Hard Way](https://kubernetes.io/blog/2020/03/19/join-sig-scalability/) | 03-19 | — | `skip` | `meta` | A recruiting post for SIG Scalability. |
| [Kubernetes 1.18: Fit & Finish](https://kubernetes.io/blog/2020/03/25/kubernetes-1-18-release-announcement/) | 03-25 | 1.18 | `skip` | `meta` | Release announcement. |
| [Kubernetes 1.18 Feature Server-side Apply Beta 2](https://kubernetes.io/blog/2020/04/01/Kubernetes-1.18-Feature-Server-side-Apply-Beta-2/) | 04-01 | 1.18 | `walk` | `api` | A beta that shipped twice. The post's own explanation — Server-side Apply "has been Beta since 1.16, but it didn't track the owner for fields associated with objects that had not been applied" — describes a beta reissued because the first one did not do the thing it was for. The `ServerSideApply` gate reads beta 1.16–1.21, stable 1.22, `removed: true` at the pin. `kubectl apply --server-side` and `--force-conflicts` survive; what does not is the post's premise that you can go and look at `managedFields`, which `kubectl get -o yaml` has hidden behind `--show-managed-fields` ever since it grew too noisy to print. |
| [Kubernetes Topology Manager Moves to Beta - Align Up!](https://kubernetes.io/blog/2020/04/01/kubernetes-1-18-feature-topology-manager-beta/) | 04-01 | 1.18 | `read` | `nodes` | The best hardware-topology explanation in the archive — NUMA, TopologyHints, HintProviders, `Policy.Merge` — and it fails `dated`'s first test: it is a design document with thirty-two fenced blocks of Go and policy tables, not a walkthrough. `dated` is for a walkthrough the lab cannot run; a post that needs a two-socket machine but never asks you to run anything is a `read`. The gate went stable in 1.27 and is `removed: true`. |
| [Improvements to the Ingress API in Kubernetes 1.18](https://kubernetes.io/blog/2020/04/02/Improvements-to-the-Ingress-API-in-Kubernetes-1.18/) | 04-02 | 1.18 | `walk` | `net` | `pathType` arrives here as an optional field defaulting to `ImplementationSpecific`. At the pin: "Paths that do not include an explicit `pathType` will fail validation" — an optional field with a default became mandatory with none. Both of the post's manifests are `networking.k8s.io/v1beta1`, unserved since v1.22, and the `kubernetes.io/ingress.class` annotation the IngressClass resource replaces is "officially deprecated" while controllers are still told to honour it. Three separate ways for the same file to fail. |
| [Introducing Windows CSI support alpha for Kubernetes](https://kubernetes.io/blog/2020/04/03/kubernetes-1-18-feature-windows-csi-support-alpha/) | 04-03 | 1.18 | `read` | `storage` | CSI drivers on Windows nodes via a privileged proxy. Alpha, announcement-shaped, and the lab is Linux. |
| [API Priority and Fairness Alpha](https://kubernetes.io/blog/2020/04/06/kubernetes-1-18-feature-api-priority-and-fairness-alpha/) | 04-06 | 1.18 | `walk` | `api` | The most churned API in the archive. The post has you set `--runtime-config="flowcontrol.apiserver.k8s.io/v1alpha1=true"` and `--feature-gates=APIPriorityAndFairness=true`; at the pin the gate went stable in 1.29 and is `removed: true`, and that group has since been served and unserved four times over — `v1beta1` stopped at v1.26, `v1beta2` at v1.29, `v1beta3` at v1.32, with `v1` since v1.29 and `assuredConcurrencyShares` renamed to `nominalConcurrencyShares` on the way. Meanwhile `kubectl get flowschemas` needs no flags at all now. |
| [Cluster API v1alpha3 Delivers New Features and an Improved User Experience](https://kubernetes.io/blog/2020/04/21/cluster-api-v1alpha3-delivers-new-features-and-an-improved-user-experience/) | 04-21 | — | `read` | `tooling` | Cluster API at `v1alpha3`, with the machine-health-checking and control-plane provider design that survived. The project is now at `v1beta1`, so every manifest in the post is unserved, and running it needs a management cluster plus an infrastructure provider. |
| [How Kubernetes contributors are building a better communication process](https://kubernetes.io/blog/2020/04/21/contributor-communication/) | 04-21 | — | `skip` | `meta` | How the contributor community organises its own communication. |
| [Two-phased Canary Rollout with Open Source Gloo](https://kubernetes.io/blog/2020/04/Two-phased-Canary-Rollout-With-Gloo/) | 04-22 | — | `skip` | `ecosystem` | A vendor gateway's canary workflow. |
| [Introducing PodTopologySpread](https://kubernetes.io/blog/2020/05/Introducing-PodTopologySpread/) | 05-05 | 1.18 | `walk` | `sched` | `topologySpreadConstraints` is still exactly as the post prints it, and everything around it moved. The scheduler config the post configures defaults with is `kubescheduler.config.k8s.io/v1alpha2`, a version the pinned docs no longer mention at all — `v1` accounts for 27 of the 31 occurrences left. Both gates are gone: `EvenPodsSpread` stable at 1.19, `DefaultPodTopologySpread` stable at 1.24, both `removed: true`. Three nodes and two labels reproduce the whole thing. |
| [How Docs Handle Third Party and Dual Sourced Content](https://kubernetes.io/blog/2020/05/third-party-dual-sourced-content/) | 05-06 | — | `skip` | `meta` | The docs policy on third-party content. |
| [WSL+Docker: Kubernetes on the Windows Desktop](https://kubernetes.io/blog/2020/05/21/wsl-docker-kubernetes-on-the-windows-desktop/) | 05-21 | — | `read` | `tooling` | KinD and Minikube under WSL2 on a Windows desktop, and Docker Desktop's licence has changed underneath it since. The lab builds real multi-node clusters, so the local-cluster ground is covered twice over already. |
| [An Introduction to the K8s-Infrastructure Working Group](https://kubernetes.io/blog/2020/05/27/an-introduction-to-the-k8s-infrastructure-working-group/) | 05-27 | — | `skip` | `meta` | An introduction to the infrastructure working group. |
| [My exciting journey into Kubernetes’ history](https://kubernetes.io/blog/2020/05/my-exciting-journey-into-kubernetes-history/) | 05-28 | — | `read` | `meta` | Ninety thousand issues and pull requests put through Kubeflow and TensorFlow to predict PR labels. A genuine end-to-end build, but what it teaches is data science; Kubernetes is the substrate, not the subject. |
| [K8s KPIs with Kuberhealthy](https://kubernetes.io/blog/2020/05/29/k8s-kpis-with-kuberhealthy/) | 05-29 | — | `skip` | `obs` | A synthetic-monitoring operator's release update. Names no alternative it rejected. |
| [Supporting the Evolving Ingress Specification in Kubernetes 1.18](https://kubernetes.io/blog/2020/06/05/Supporting-the-Evolving-Ingress-Specification-in-Kubernetes-1.18/) | 06-05 | 1.18 | `read` | `net` | A vendor's migration guide for the same 1.18 Ingress changes the API post above walks, written from the controller side. Read for what a spec change costs the implementers; the diff itself is carried first-party. |
| [A Better Docs UX With Docsy](https://kubernetes.io/blog/2020/06/better-docs-ux-with-docsy/) | 06-15 | — | `skip` | `meta` | The website changes theme. |
| [Working with Terraform and Kubernetes](https://kubernetes.io/blog/2020/06/working-with-terraform-and-kubernetes/) | 06-29 | — | `read` | `tooling` | Terraform for the cluster, Kustomize for what runs on it, with the Terraform Kubernetes provider named as the thing rejected and why. A decision with its alternative on the record, so it clears the vendor bar as a read. |
| [SIG-Windows Spotlight](https://kubernetes.io/blog/2020/06/30/sig-windows-spotlight-2020/) | 06-30 | — | `skip` | `meta` | A SIG spotlight interview about how the group works. |
| [Music and math: the Kubernetes 1.17 release interview](https://kubernetes.io/blog/2020/07/27/kubernetes-1-17-release-interview/) | 07-27 | 1.17 | `read` | `meta` | The 1.17 release lead on the release. `read` on the maintainer-interview rule, as with 2019's two. |
| [Physics, politics and Pull Requests: the Kubernetes 1.18 release interview](https://kubernetes.io/blog/2020/08/03/kubernetes-1-18-release-interview/) | 08-03 | 1.18 | `read` | `meta` | The 1.18 release lead, on a release that a bug in `k8s.io/utils` delayed by a day. |
| [Introducing Hierarchical Namespaces](https://kubernetes.io/blog/2020/08/14/introducing-hierarchical-namespaces/) | 08-14 | — | `read` | `security` | Hierarchical namespaces, proposed as the answer to multi-tenancy that RBAC and NetworkPolicy leave half-solved. At the pin the phrase "hierarchical namespace" and the `hnc.x-k8s.io` API group both return **zero hits** in the docs: it stayed a `kubernetes-sigs` project and never entered the thing it was designed to extend. Read for the tenancy argument, which is still the live one. |
| [Moving Forward From Beta](https://kubernetes.io/blog/2020/08/21/moving-forward-from-beta/) | 08-21 | 1.20 | `read` | `api` | The project writing down its own ladder, and the post the census's beta-graduation rule is arguing with. It states flatly that "beta features are enabled by default"; the pin has softened that to "Usually enabled by default, well-tested" and new beta APIs have been off by default since v1.24. No commands in it, so the diff is a sentence rather than a manifest. |
| [Kubernetes 1.19: Accentuate the Paw-sitive](https://kubernetes.io/blog/2020/08/26/kubernetes-release-1.19-accentuate-the-paw-sitive/) | 08-26 | 1.19 | `skip` | `meta` | Release announcement. |
| [Increasing the Kubernetes Support Window to One Year](https://kubernetes.io/blog/2020/08/31/kubernetes-1-19-feature-one-year-support/) | 08-31 | 1.19 | `skip` | `meta` | The support window goes from nine months to one year, on survey evidence. A schedule change with no surface a cluster can show you. |
| [Ephemeral volumes with storage capacity tracking: EmptyDir on steroids](https://kubernetes.io/blog/2020/09/01/ephemeral-volumes-with-storage-capacity-tracking/) | 09-01 | 1.19 | `walk` | `storage` | `ephemeral.volumeClaimTemplate` gives a Pod a full PVC that dies with it — one manifest, any storage class, and the lab's provisioner is enough. The `GenericEphemeralVolume` gate went stable at 1.23 and is `removed: true`, and the capacity-tracking half moved group-version: `storage.k8s.io/v1beta1` CSIStorageCapacity stopped being served at v1.27. The post's own demonstration clones `intel/pmem-csi` and needs persistent memory, so the walk is the feature, not the tour. |
| [Scaling Kubernetes Networking With EndpointSlices](https://kubernetes.io/blog/2020/09/02/scaling-kubernetes-networking-with-endpointslices/) | 09-02 | 1.19 | `walk` | `net` | The post makes a promise and the project broke it. "The Endpoints API will continue to be considered generally available and stable", it says, and "The Endpoints API is not going away"; at the pin the API reference reads "Deprecated: This API is deprecated in v1.33+. Use discoveryv1.EndpointSlice." Its own API moved too — `discovery.k8s.io/v1beta1` unserved since v1.25, and the per-endpoint `topology` map it describes is now `deprecatedTopology` and not writable, replaced by `zone` and `nodeName`. One Service with a handful of Pods shows both objects side by side. |
| [Warning: Helpful Warnings Ahead](https://kubernetes.io/blog/2020/09/03/warnings/) | 09-03 | 1.19 | `walk` | `api` | A feature that has no alpha stage: the `WarningHeaders` gate starts at beta and default-true in 1.19, stable 1.22, `removed: true` — the only ladder in the year that skips a rung. The post's worked example is a `kubectl apply` printing "networking.k8s.io/v1beta1 Ingress is deprecated in v1.19+, unavailable in v1.22+", which at the pin is not a warning any more but a hard failure, so the demonstration has been overtaken by the thing it demonstrates. `--warnings-as-errors` and CRD `deprecationWarning` both survive. |
| [Introducing Structured Logs](https://kubernetes.io/blog/2020/09/04/kubernetes-1-19-Introducing-Structured-Logs/) | 09-04 | 1.19 | `walk` | `obs` | Six years and it never left alpha. The pinned docs still mark JSON log format `{{< feature-state for_k8s_version="v1.19" state="alpha" >}}` — the release this post announces — while `--logging-format` sits on all five components defaulting to `text`. Underneath it the klog surface the post writes against was cut: eleven flags including `--log-file`, `--logtostderr` and `--alsologtostderr` deprecated at v1.23 and removed at v1.26, with `kube-log-runner` handed the job instead. The year's only `obs` walk, and the tag's first since the taxonomy was frozen. |
| [GSoC 2020 - Building operators for cluster addons](https://kubernetes.io/blog/2020/09/16/gsoc20-building-operators-for-cluster-addons/) | 09-16 | — | `read` | `tooling` | A Google Summer of Code report, and the declarative addon-operator pattern inside it is the payload rather than the programme framing. Read for how an addon becomes a controller. |
| [Contributing to the Development Guide](https://kubernetes.io/blog/2020/10/01/contributing-to-the-development-guide/) | 10-01 | — | `skip` | `meta` | A technical writer's account of updating the development guide. |
| [Announcing the 2020 Steering Committee Election Results](https://kubernetes.io/blog/2020/10/12/steering-committee-results-2020/) | 10-12 | — | `skip` | `meta` | Election results. |
| [Remembering Dan Kohn](https://kubernetes.io/blog/2020/11/02/remembering-dan-kohn/) | 11-02 | — | `skip` | `meta` | A memorial for the CNCF's first executive director. |
| [Cloud native security for your clusters](https://kubernetes.io/blog/2020/11/18/cloud-native-security-for-your-clusters/) | 11-18 | — | `skip` | `security` | An announcement that a CNCF whitepaper exists. |
| [Dockershim Deprecation FAQ](https://kubernetes.io/blog/2020/12/02/dockershim-faq/) | 12-02 | 1.20 | `read` | `nodes` | The FAQ half of the dockershim deprecation, and it has been edited in place — "_Update_: removal of dockershim is scheduled for Kubernetes v1.24" sits inside the body, over an original that named no release. Its migration path survived: `migrating-from-dockershim` is six pages at the pin and `cri-dockerd` is documented as the way to keep the daemon. |
| [Don't Panic: Kubernetes and Docker](https://kubernetes.io/blog/2020/12/02/dont-panic-kubernetes-and-docker/) | 12-02 | 1.20 | `read` | `nodes` | The most-read post the project ever published, and the one place in the archive where a sentence has been **struck through rather than corrected**: "removed in a future release (`<del>`currently planned for the 1.22 release in late 2021`</del>`)". It went in v1.24. Nothing here breaks a manifest — the diff is a date and a strikethrough — so the year's biggest story is a read, not a walk. |
| [GSoD 2020: Improving the API Reference Experience](https://kubernetes.io/blog/2020/12/04/gsod-2020-improving-api-reference-experience/) | 12-04 | — | `skip` | `meta` | A Season of Docs report on the API reference generator. |
| [Kubernetes 1.20: The Raddest Release](https://kubernetes.io/blog/2020/12/08/kubernetes-1-20-release-announcement/) | 12-08 | 1.20 | `skip` | `meta` | Release announcement. |
| [Kubernetes 1.20: Kubernetes Volume Snapshot Moves to GA](https://kubernetes.io/blog/2020/12/10/kubernetes-1.20-volume-snapshot-moves-to-ga/) | 12-10 | 1.20 | `read` | `storage` | Snapshots reach GA, four years and two alphas after the 2018 post the census already walks. The ladder ran alpha 1.12, second alpha with breaking changes 1.13, beta 1.17, GA 1.20, and the interesting rung is the one 2019 already recorded. |
| [Kubernetes 1.20: Granular Control of Volume Permission Changes](https://kubernetes.io/blog/2020/12/14/kubernetes-release-1.20-fsGroupChangePolicy-fsGroupPolicy/) | 12-14 | 1.20 | `walk` | `storage` | The cheapest observable failure in the year: mount a volume with many files, set `fsGroup`, and watch the Pod sit in `ContainerCreating` while the kubelet recursively `chown`s every one of them. `fsGroupChangePolicy: "OnRootMismatch"` makes it instant. Both gates are stable-and-`removed: true` and both fields survive verbatim, so this is a walk on the second clause alone — plus one thing the post predates: the pin now warns that the policy has no effect once a CSI driver has been delegated the job. |
| [Third Party Device Metrics Reaches GA](https://kubernetes.io/blog/2020/12/16/third-party-device-metrics-reaches-ga/) | 12-16 | 1.20 | `read` | `obs` | The Pod Resources API at GA and kubelet's own accelerator metrics turned off in favour of it. The plugin architecture is the point and the devices are the prerequisite. |
| [Kubernetes 1.20: Pod Impersonation and Short-lived Volumes in CSI Drivers](https://kubernetes.io/blog/2020/12/18/kubernetes-1.20-pod-impersonation-short-lived-volumes-in-csi/) | 12-18 | 1.20 | `read` | `storage` | Service-account tokens handed to CSI drivers so a driver stops needing the TokenRequest permission or the host filesystem. A least-privilege argument worth reading; acting on it means writing a driver. |
| [A Custom Kubernetes Scheduler to Orchestrate Highly Available Applications](https://kubernetes.io/blog/2020/12/21/writing-crl-scheduler/) | 12-21 | — | `read` | `sched` | A vendor writes a second scheduler to keep a distributed database's replicas apart, having found anti-affinity and StatefulSet ordering insufficient — the alternatives are named, which is what the vendor rule asks for. The scheduler framework has since made most of this an out-of-tree plugin rather than a second binary. |

## Exercises

Nine `walk` verdicts, numbered in publication order. All nine are *pending* — an authoring
ticket's to claim. The rubric they are authored against was ratified in
[#57](https://github.com/k3ii/k8s-academy/issues/57).

| # | exercise | state |
|---|---|---|
| 01 | The ledger you have to ask to see | pending |
| 02 | The field that stopped being optional | pending |
| 03 | Four names for the same queue | pending |
| 04 | The constraint survived, the config did not | pending |
| 05 | A claim that dies with the Pod | pending |
| 06 | The API that was not going away | pending |
| 07 | A warning that became a refusal | pending |
| 08 | Six years alpha, and the flags went first | pending |
| 09 | The Pod that waits for a million chowns | pending |
