# 2026 — the census

70 posts, 2026-01-02 to 2026-08-26. The year is two-thirds long: the pin is 2026-08-26, the same
day v1.37 shipped, so the archive stops mid-year. Kubernetes 1.35, 1.36 and 1.37 are in scope, and
eleven of the 70 are unpublished drafts — see [the method](../README.md).

**Yield: 14 `walk`**, inside the [band](../README.md#the-budget) and the second-largest count the census
has produced, behind 2016's 15 and out of a year barely three-quarters the size. 42 `read`,
1 `dated`, 13 `skip`.

**The census closes, and the budget never bound.** Twelve years, 767 rows: 135 `walk`, 394 `read`,
17 `dated`, 221 `skip`. The 8–15 band was reached at both ends — 2017's and 2019's floor of 8,
2016's ceiling of 15 — and in twelve years it never once cut a post that the rubric would otherwise
have kept. Every year that came in low did so because the posts were release notes, and every year
that came in high did so because the posts were walkthroughs. The band described the corpus; it
never disciplined it. That is the answer to the open question the map has carried since 2016.

**Eleven drafts, not ten, and the eleventh has a permalink that 404s.** Every earlier statement of
the method says the unpublished drafts resolve to nothing and carry an empty `url`. Ten do. The
eleventh, *Kubernetes Changed Block Tracking API - Beta Differences*, carries `draft: true` **and**
a frontmatter date, so `hugo.toml`'s permalink template resolves cleanly for it and the manifest
records a URL. The site does not serve that URL: a request for it returns 404 while a control URL
taken from the same manifest returns 200. So the rule keys off `draft: true`, not off whether a URL
resolved, and this pass changes the gate to say so — `by_url` now holds published posts only,
`by_title` holds drafts, and a `Title (draft)` cell containing a link no longer parses as an
unlinked one. Ratified here, and the method's two "ten drafts" sentences are corrected with it.

**Twenty-one releases on the first rung.** `HPAScaleToZero` was alpha from 1.16 to 1.36 and reaches
beta at 1.37 — the longest alpha span in all 488 feature-gate files at the pin, ahead of `WinDSR`
and `ProcMountType` at 19. No earlier year found it because no earlier post pointed at it. And it
was not alone: 1.37 ends the alpha of 15 gates whose alpha closed at 1.36, among them the four
longest unfinished ones — `HPAScaleToZero` at 21, `MemoryQoS` and `KubeletInUserNamespace` at 15,
`PodAndContainerStatsFromCRI` at 14. Three of this year's rows are those gates. Against that, the
ordinary case: of 346 closed alpha spans in the directory, **151 — 44% — lasted exactly one
release**, and the tail is one gate each at 21, 16, 14, 13 and 12.

**The instrument cannot see the longest beta in the corpus.** The Metrics API sat at beta from 1.8
to 1.36 and reaches v1 at 1.37: twenty-nine releases, longer than any beta the feature-gate
directory records — `AppArmor` at 27, `ExperimentalHostUserNamespaceDefaulting` at 23,
`APIListChunking` at 20. The directory has no file for it, because an aggregated API has no gate.
Nine years of censuses have read promotion history off those 488 files; this is the first row that
had to be read off the API reference instead, and the reference has not caught up either — the pin
still ships only `metrics.v1beta1`, and the HorizontalPodAutoscaler page still says `v1beta1` is
what it supports.

**The release announcement and the gate directory contradict each other.** The published v1.37
announcement says the Storage Version Migration API graduates to Stable and becomes enabled by
default. `StorageVersionMigrator.md` at the same pin stops at `beta`, `defaultValue: false`, from
1.35, with no `toVersion` and no 1.37 stage at all. Of the 28 gate names the announcement mentions,
it is the only claimed 1.37 graduation with nothing in the directory to match. A second, weaker case
sits beside it: the announcement lists `SELinuxChangePolicy` among v1.37's stable graduations, and
the gate file has it stable from 1.36.

**Two pages of one site disagree about a field you can still set.** The Service concept page marks
`spec.externalIPs` deprecated at 1.36 and tells all users to begin migrating away. The generated
API reference for the same object, from the same commit, describes the field with no deprecation
notice. Both are current; the archive has found stale links, moved pages and redirects before, but
this is the first time two live pages give opposite advice about the same field.

**A discontinuity that ships outside Kubernetes.** The new cgroup v1 → v2 CPU conversion changes
what weight a `cpu: 250m` request produces, and it has no feature gate and no Kubernetes version:
the post says adoption depends solely on the OCI runtime, runc 1.3.2 or crun 1.23. Every walk in
the eleven years before this one anchored to a release or a gate. This one anchors to a runtime
the cluster does not version.

**A ratified rule that only one year has obeyed.** The spotlight rule reads `read` when the
interviewee owns code and `skip` otherwise — a technical SIG on one side, a working group on the
other. 2024 applied it, giving `read` to six SIG spotlights. 2020, 2021, 2022, 2023 and 2025
skipped every spotlight they met, including SIG Node, SIG Storage and SIG API Machinery. 2026 has
all three cases in one year — SIG Architecture, SIG Storage, and WG Device Management — and follows
the written rule: two `read`, one `skip`. Rows are immutable once written, so the divergence is
reported here rather than repaired backwards. It is the only rule in the rubric the archive has
applied inconsistently, and it was found only because the last year happened to contain the full
set.

**The blog gets better at correcting itself.** 2019 added a `{{< note >}}` to a post after
publication; 2020 struck a sentence with an inline `<del>`. This year *How the controller-runtime
Cache Actually Works* opens with a `{{% pageinfo %}}` saying the article was revised to correct
several significant technical inaccuracies in the original text, and a second post carries a line
saying it was originally published with the wrong date and later republished. The archive has
watched this convention grow from a footnote to a banner.

**Half the year is the archive answering itself, and it is a smaller half than last year's.** Ten
rows point back at an exercise or a row an earlier year already owns — in-place resize twice, user
namespaces, `kuberc`, `MemoryQoS`, DRA twice, workload-aware scheduling twice, per-container
restart policy — 14%, against 2025's 26%. The reject rate is 19%, against 48%, 42%, 38%, 40%, 37%,
41%, 21%, 17%, 15%, 19% and 18% for the years before it, and the corpus has settled: `meta` leads
at 11 rows and 16%, `ecosystem` follows at 10, and 37 of 70 titles name a Kubernetes version — 53%,
down from 2025's record 63%. The digest that triaged this year cost 9% of the source bytes, the
cheapest of any year censused.

## Census

Verdicts and topics are defined in [`../README.md`](../README.md#the-census). Every post has a
row, and a row's title always links the post — never the exercise file, so the row never
changes once written. The eleven unpublished drafts are unlinked and marked `(draft)`; they are
the v1.37 queue at the pin, and they sort last because a draft carries no publication date.
The **Exercises** table below is the progress record.

| post | date | k8s | verdict | topic | why |
|---|---|---|---|---|---|
| [Kubernetes v1.35: New level of efficiency with in-place Pod restart](https://kubernetes.io/blog/2026/01/02/kubernetes-v1-35-restart-all-containers/) | 01-02 | 1.35 | `read` | `nodes` | In-place Pod restart keeps the Pod object and its node while every container starts again. 2025's exercise 07 already carries the per-container `restartPolicy` this sits on top of, and the new part is one more value in the same field. |
| [Kubernetes v1.35: Extended Toleration Operators to Support Numeric Comparisons (Alpha)](https://kubernetes.io/blog/2026/01/05/kubernetes-v1-35-numeric-toleration-operators/) | 01-05 | 1.35 | `walk` | `sched` | `Gt` and `Lt` join `Equal` and `Exists`, so a toleration can compare a taint's value numerically instead of matching it. Alpha at 1.35 and still alpha with `defaultValue: false` two releases later at the pin — a gate to turn on by hand, and a taint to set by hand. |
| [Kubernetes v1.35: A Better Way to Pass Service Account Tokens to CSI Drivers](https://kubernetes.io/blog/2026/01/07/kubernetes-v1-35-csi-sa-tokens-secrets-field-beta/) | 01-07 | 1.35 | `read` | `storage` | Service account tokens stop reaching CSI drivers through `NodePublishSecretRef` and get a field of their own. Seeing the difference means a driver that reads the token and reports what it received, which is driver work rather than cluster work. |
| [Kubernetes v1.35: Mutable PersistentVolume Node Affinity (alpha)](https://kubernetes.io/blog/2026/01/08/kubernetes-v1-35-mutable-pv-nodeaffinity/) | 01-08 | 1.35 | `read` | `storage` | A bound PersistentVolume's `nodeAffinity` becomes editable so a volume whose data moved can follow it. Alpha, and the payoff only appears on a cluster whose storage actually migrated between nodes. |
| [Kubernetes v1.35: Restricting executables invoked by kubeconfigs via exec plugin allowList added to kuberc](https://kubernetes.io/blog/2026/01/09/kubernetes-v1-35-kuberc-credential-plugin-allowlist/) | 01-09 | 1.35 | `read` | `tooling` | The `allowList` that restricts which executables a kubeconfig `exec` credential plugin may invoke. 2025's exercise 06 is `kuberc`, and its census row already names this policy as the thing the 1.34 post did not mention. |
| [Uniform API server access using clientcmd](https://kubernetes.io/blog/2026/01/19/clientcmd-apiserver-access/) | 01-19 | — | `read` | `tooling` | A Go walkthrough of the loading rules `kubectl` itself uses to find and merge a kubeconfig. It is a client-library tutorial: the cluster never notices what the program did. |
| [Announcing the Checkpoint/Restore Working Group](https://kubernetes.io/blog/2026/01/21/introducing-checkpoint-restore-wg/) | 01-21 | — | `skip` | `meta` | A working group announcement. The seed is container checkpoint and restore, which no census row owns yet. |
| [Headlamp in 2025: Project Highlights](https://kubernetes.io/blog/2026/01/22/headlamp-in-2025-project-highlights/) | 01-22 | — | `skip` | `ecosystem` | A project year in review for an ecosystem UI. |
| [Cluster API v1.12: Introducing In-place Updates and Chained Upgrades](https://kubernetes.io/blog/2026/01/27/cluster-api-v1-12-release/) | 01-27 | — | `read` | `ecosystem` | In-place updates and chained upgrades in Cluster API, and the post names the alternative it rejected — replacing machines rather than mutating them — so it reads rather than skips. |
| [Experimenting with Gateway API using kind](https://kubernetes.io/blog/2026/01/28/experimenting-gateway-api-with-kind/) | 01-28 | — | `walk` | `net` | The only post in 767 that builds a Gateway API lab on `kind` and nothing else: install the CRDs, install a controller, watch a Gateway take an address. Every other Gateway post in the archive starts from a cluster that already has one. |
| [Ingress NGINX: Statement from the Kubernetes Steering and Security Response Committees](https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/) | 01-29 | — | `read` | `net` | The Steering and Security Response Committees on why Ingress NGINX is being retired rather than re-staffed. An argument, and the decision it records is why the two migration posts later in the year exist. |
| [New Conversion from cgroup v1 CPU Shares to v2 CPU Weight](https://kubernetes.io/blog/2026/01/30/new-cgroup-v1-to-v2-cpu-conversion-formula/) | 01-30 | — | `walk` | `nodes` | The mapping from cgroup v1 `cpu.shares` to v2 `cpu.weight` changes, so the same `cpu: 250m` request yields a different weight. No feature gate and no Kubernetes version gates it — adoption depends solely on the OCI runtime, runc 1.3.2 or crun 1.23 — which makes it the first walk in the census whose discontinuity ships entirely outside Kubernetes. |
| [Introducing Node Readiness Controller](https://kubernetes.io/blog/2026/02/03/introducing-node-readiness-controller/) | 02-03 | — | `read` | `nodes` | An out-of-tree controller that holds a node `NotReady` until the components it depends on report in. The mechanism underneath is a startup taint removed by a controller: something to install, not something to exercise. |
| [Spotlight on SIG Architecture: API Governance](https://kubernetes.io/blog/2026/02/12/sig-architecture-api-spotlight/) | 02-12 | — | `read` | `meta` | A spotlight whose interviewees own the API review process and the code that enforces it, which is the side of the spotlight rule that reads. |
| [Before You Migrate: Five Surprising Ingress-NGINX Behaviors You Need to Know](https://kubernetes.io/blog/2026/02/27/ingress-nginx-before-you-migrate/) | 02-27 | — | `read` | `net` | Five Ingress NGINX behaviours that Gateway API does not reproduce. It is the argument the migration needs, and every detail in it is specific to a controller being retired. |
| [Announcing the AI Gateway Working Group](https://kubernetes.io/blog/2026/03/09/announcing-ai-gateway-wg/) | 03-09 | — | `skip` | `meta` | A working group announcement. |
| [The Invisible Rewrite: Modernizing the Kubernetes Image Promoter](https://kubernetes.io/blog/2026/03/17/image-promoter-rewrite/) | 03-17 | — | `read` | `meta` | How the project's image promotion pipeline was rewritten without users noticing. Project infrastructure, and the decision it records — invisibility as the success criterion — is the readable part. |
| [Securing Production Debugging in Kubernetes](https://kubernetes.io/blog/2026/03/18/securing-production-debugging-in-kubernetes/) | 03-18 | — | `read` | `security` | Ephemeral containers, `kubectl debug` profiles and the RBAC around them. The payload is which subresource to withhold from whom, argued rather than demonstrated. |
| [Running Agents on Kubernetes with Agent Sandbox](https://kubernetes.io/blog/2026/03/20/running-agents-on-kubernetes-with-agent-sandbox/) | 03-20 | — | `read` | `ecosystem` | Per-session sandboxes for AI agents on Kubernetes. An out-of-tree project that names the alternative it rejects — plain Pods — so it reads. |
| [Announcing Ingress2Gateway 1.0: Your Path to Gateway API](https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release/) | 03-20 | — | `walk` | `net` | A converter that reads a cluster's live Ingress objects and emits Gateway API ones, at 1.0. It is the only tool in the archive that turns one API's objects into another's, and the diff it prints is the lesson. |
| [Kubernetes v1.36 Sneak Peek](https://kubernetes.io/blog/2026/03/30/kubernetes-v1-36-sneak-peek/) | 03-30 | 1.36 | `skip` | `meta` | A pre-release preview. |
| [Gateway API v1.5: Moving features to Stable](https://kubernetes.io/blog/2026/04/21/gateway-api-v1-5/) | 04-21 | — | `read` | `net` | Features moving to the Standard channel in an out-of-tree API. The promotion is real, but the exercise it would produce is the one this year's `kind` and ingress2gateway walks already carry. |
| [Kubernetes v1.36: ハル (Haru)](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/) | 04-22 | 1.36 | `skip` | `meta` | A release announcement, and no line in it is load-bearing for an exercise elsewhere. |
| [SELinux Volume Label Changes goes GA (and likely implications in v1.37)](https://kubernetes.io/blog/2026/04/22/breaking-changes-in-selinux-volume-labeling/) | 04-22 | 1.36 | `dated` | `storage` | `SELinuxMount` was alpha from 1.30 and is stable and on by default at 1.37, and the post is a walkthrough of what that breaks. Reproducing it needs node hardware running SELinux in enforcing mode, which the lab does not have. |
| [Kubernetes v1.36: User Namespaces in Kubernetes are finally GA](https://kubernetes.io/blog/2026/04/23/kubernetes-v1-36-userns-ga/) | 04-23 | 1.36 | `read` | `security` | `UserNamespacesSupport` reaches GA. 2022's exercise 10 already carries user namespaces from their alpha, and GA moves the default rather than the mechanism. |
| [Kubernetes v1.36: Fine-Grained Kubelet API Authorization Graduates to GA](https://kubernetes.io/blog/2026/04/24/kubernetes-v1-36-fine-grained-kubelet-authorization-ga/) | 04-24 | 1.36 | `walk` | `security` | `KubeletFineGrainedAuthz` splits the kubelet's single `nodes/proxy` permission into per-endpoint subresources, so a client granted metrics can no longer also exec. Alpha 1.32, beta 1.33, stable at 1.36 — a permission that moved, and one RBAC rule is enough to watch the old grant stop covering everything. |
| [Kubernetes v1.36: Mutable Pod Resources for Suspended Jobs (beta)](https://kubernetes.io/blog/2026/04/27/kubernetes-v1-36-mutable-pod-resources-for-suspended-jobs/) | 04-27 | 1.36 | `read` | `sched` | A suspended Job's Pod template resources become editable. Beta, and it is one field on an object that is not running — 2023's exercise 07 already carries resizing one that is. |
| [Kubernetes v1.36: Staleness Mitigation and Observability for Controllers](https://kubernetes.io/blog/2026/04/28/kubernetes-v1-36-staleness-mitigation-for-controllers/) | 04-28 | 1.36 | `read` | `api` | Controllers get a way to notice their informer cache is behind the API server. The mechanism is a client-library concern; what the cluster shows for it is a metric. |
| [Kubernetes v1.36: Tiered Memory Protection with Memory QoS](https://kubernetes.io/blog/2026/04/29/kubernetes-v1-36-memory-qos-tiered-protection/) | 04-29 | 1.36 | `read` | `nodes` | `MemoryQoS` is the subject of 2021's exercise 08, *Fifteen releases on the first rung*, and this is the release that ends the run: alpha 1.22 to 1.36, beta and on by default at 1.37. |
| [Kubernetes v1.36: In-Place Vertical Scaling for Pod-Level Resources Graduates to Beta](https://kubernetes.io/blog/2026/04/30/kubernetes-v1-36-inplace-pod-level-resources-beta/) | 04-30 | 1.36 | `read` | `nodes` | Pod-level resources become resizable in place. The redundancy filter: in-place resize is 2023's exercise 07 and two 2025 rows already track it to stable, and this moves it from the container to the Pod. |
| [Kubernetes v1.36: Pod-Level Resource Managers (Alpha)](https://kubernetes.io/blog/2026/05/01/kubernetes-v1-36-feature-pod-level-resource-managers-alpha/) | 05-01 | 1.36 | `read` | `nodes` | The CPU and memory managers learn about Pod-level resources. Alpha, and the effect shows only where node topology actually constrains placement. |
| [Kubernetes v1.36: Admission Policies That Can't Be Deleted](https://kubernetes.io/blog/2026/05/04/kubernetes-v1-36-manifest-based-admission-control/) | 05-04 | 1.36 | `read` | `security` | Admission policies that ship with the control plane manifest and that an API client cannot delete. The demonstration is a `kubectl delete` that fails, which is one command — the shape of a `read`. |
| [Kubernetes v1.36: Declarative Validation Graduates to GA](https://kubernetes.io/blog/2026/05/05/kubernetes-v1-36-declarative-validation-ga/) | 05-05 | 1.36 | `read` | `api` | Validation moves from hand-written Go to declarative tags. It is an internal rewrite whose success criterion is that nothing observable changes. |
| [Kubernetes v1.36: Server-Side Sharded List and Watch](https://kubernetes.io/blog/2026/05/06/kubernetes-v1-36-server-side-sharded-list-and-watch/) | 05-06 | 1.36 | `read` | `api` | The API server can hand each of several watchers a shard of one list. It is a scale mechanism, and a lab cluster has nothing worth sharding. |
| [Kubernetes v1.36: More Drivers, New Features, and the Next Era of DRA](https://kubernetes.io/blog/2026/05/07/kubernetes-v1-36-dra-136-updates/) | 05-07 | 1.36 | `read` | `sched` | More drivers and more DRA features. 2025's exercise 08 already carries `resource.k8s.io` at v1 with a driver that has no devices. |
| [Kubernetes v1.36: Moving Volume Group Snapshots to GA](https://kubernetes.io/blog/2026/05/08/kubernetes-v1-36-volume-group-snapshot-ga/) | 05-08 | 1.36 | `read` | `storage` | Volume group snapshots reach GA. The API alone shows nothing without a CSI driver that implements the group capability. |
| [Kubernetes v1.36: PSI Metrics for Kubernetes Graduates to GA](https://kubernetes.io/blog/2026/05/12/kubernetes-v1-36-psi-metrics-ga/) | 05-12 | 1.36 | `walk` | `obs` | `KubeletPSI` runs alpha 1.33, beta 1.34, stable 1.36 — three releases end to end, against the twenty-one that the same pin records for the longest. The kubelet then exposes Linux pressure-stall figures for CPU, memory and IO that one busy container is enough to move. |
| [Kubernetes v1.36: Advancing Workload-Aware Scheduling](https://kubernetes.io/blog/2026/05/13/kubernetes-v1-36-advancing-workload-aware-scheduling/) | 05-13 | 1.36 | `read` | `sched` | The `Workload` API one release on from 2025's exercise 11, which already records that it reached `v1alpha2` and lost a gate to a merge. |
| [Kubernetes v1.36: Deprecation and removal of Service ExternalIPs](https://kubernetes.io/blog/2026/05/14/kubernetes-v1-36-deprecation-and-removal-of-service-externalips/) | 05-14 | 1.36 | `walk` | `net` | `spec.externalIPs` is deprecated at 1.36 and the concept page says all users should begin migrating away. The generated API reference at the same pin describes the field with no deprecation notice at all — two pages of one site disagreeing about a field a cluster still accepts. |
| [Kubernetes v1.36: Mixed Version Proxy Graduates to Beta](https://kubernetes.io/blog/2026/05/15/kubernetes-1-36-feature-mixed-version-proxy-beta/) | 05-15 | 1.36 | `read` | `api` | One API server proxies a request to the peer that serves the resource it does not. Announcement, not walkthrough, and it needs a control plane running two versions at once. |
| [Kubernetes v1.36: New Metric for Route Sync in the Cloud Controller Manager](https://kubernetes.io/blog/2026/05/15/ccm-new-metric-route-sync-total/) | 05-15 | 1.36 | `read` | `obs` | One new metric in the cloud controller manager. The lab has no cloud controller manager to emit it. |
| [Announcing etcd 3.7.0-beta.0](https://kubernetes.io/blog/2026/05/20/etcd-370-beta/) | 05-20 | — | `skip` | `etcd` | A pre-release announcement for a component the archive does not build. |
| [Reconciling the Past: Correcting Records for Unfixed Kubernetes CVEs](https://kubernetes.io/blog/2026/05/26/reconciling-unfixed-kubernetes-cves/) | 05-26 | — | `read` | `security` | The project corrects its own records for CVEs that were never fixed. An argument about disclosure hygiene that names the alternative — quietly closing them — it rejects. |
| [From Kubernetes Dashboard to Headlamp: Understanding the Transition](https://kubernetes.io/blog/2026/06/01/dashboard-to-headlamp/) | 06-01 | — | `read` | `ecosystem` | Why the Dashboard is being retired in favour of Headlamp. It names the alternative it rejects, staffing two dashboards, so it reads rather than skips. |
| [Spotlight on SIG Storage](https://kubernetes.io/blog/2026/06/15/sig-storage-spotlight-2026/) | 06-15 | — | `read` | `meta` | The interviewees own the CSI and volume code, which is the side of the spotlight rule that reads. |
| [Spotlight on WG Device Management](https://kubernetes.io/blog/2026/06/24/wg-device-management-spotlight-2026/) | 06-24 | — | `skip` | `meta` | A working group, not a SIG. The ratified spotlight rule puts a working group on the skip side, and this year is the first to have all three cases at once. |
| [See your serverless: introducing the Headlamp plugin for Knative](https://kubernetes.io/blog/2026/06/25/headlamp-knative-plugin/) | 06-25 | — | `skip` | `ecosystem` | A plugin announcement for an ecosystem UI. |
| [Inspect Volcano workloads faster with Headlamp](https://kubernetes.io/blog/2026/06/25/visual-context-volcano-headlamp-plugin/) | 06-25 | — | `skip` | `ecosystem` | A plugin announcement for an ecosystem UI. |
| [Introducing the Cluster API plugin for Headlamp](https://kubernetes.io/blog/2026/06/25/headlamp-cluster-api-plugin/) | 06-25 | — | `skip` | `ecosystem` | A plugin announcement for an ecosystem UI. |
| [Open source maintainership in the age of AI](https://kubernetes.io/blog/2026/06/26/open-source-maintainership-in-the-age-of-ai/) | 06-26 | — | `read` | `meta` | An argument about review load and contributor trust. No commands, and the position it takes is the whole payload. |
| Kubernetes Changed Block Tracking API - Beta Differences (draft) | 07-07 | 1.33 | `read` | `storage` | The SnapshotMetadataService CRD goes from `v1alpha1` to `v1beta1`, and `v1alpha1` is removed rather than served alongside it. Out-of-tree, no feature gate, and it needs a CSI driver shipping the sidecar. This is the eleventh draft and the only one carrying a date, so the manifest resolves a permalink for it that the site does not serve. |
| [Announcing etcd v3.7.0](https://kubernetes.io/blog/2026/07/08/announcing-etcd-3.7/) | 07-08 | — | `skip` | `etcd` | A component release announcement. |
| [Kubernetes Dashboard to Headlamp: A Step-by-Step Guide](https://kubernetes.io/blog/2026/07/13/kubernetes-dashboard-to-headlamp/) | 07-13 | — | `read` | `ecosystem` | A step-by-step migration between two ecosystem dashboards. The steps are real, and nothing in Kubernetes changes when they finish. |
| [Operating AI/ML Workloads on Kubernetes: A Headlamp Plugin for Kubeflow](https://kubernetes.io/blog/2026/07/13/introducing-headlamp-plugin-for-kubeflow/) | 07-13 | — | `skip` | `ecosystem` | A plugin announcement for an ecosystem UI. |
| [Building a Custom Metrics Exporter for Kubernetes](https://kubernetes.io/blog/2026/07/14/custom-metrics-exporter-kubernetes/) | 07-14 | — | `walk` | `obs` | Write a Prometheus exporter in Go, ship it in a container, and wire it so that Prometheus and then a HorizontalPodAutoscaler consume what it reports. It is the only post in the archive that builds the producer side; every other observability post starts from metrics that already exist. |
| [How the controller-runtime Cache Actually Works, and Why Your Controller Does Not Crash the API Server](https://kubernetes.io/blog/2026/07/29/controller-runtime-cache-explained/) | 07-29 | — | `read` | `ecosystem` | How controller-runtime's cache keeps a controller from hammering the API server. It also carries the archive's strongest self-annotation: a `pageinfo` box saying the article was revised to correct several significant technical inaccuracies in the original text. |
| [Kubernetes v1.37 Sneak Peek](https://kubernetes.io/blog/2026/07/31/kubernetes-v1-37-sneak-peek/) | 07-31 | 1.37 | `skip` | `meta` | A pre-release preview. |
| [Gateway API v1.6: TCPRoute and UDPRoute Graduate to Standard](https://kubernetes.io/blog/2026/08/03/gateway-api-v1-6-release/) | 08-03 | — | `read` | `net` | TCPRoute and UDPRoute reach the Standard channel. Out-of-tree promotion, and this year's two Gateway walks already carry the API itself. |
| [How to Pretty-Print Your Kubernetes YAML as KYAML and Why You'd Want To](https://kubernetes.io/blog/2026/08/11/how-to-pretty-print-kubernetes-yaml-as-kyaml/) | 08-11 | 1.34 | `walk` | `tooling` | `kubectl -o kyaml` prints YAML with every string quoted and every block braced, so no value is ever guessed at. Alpha and opt-in behind `KUBECTL_KYAML=true` at 1.34, beta and on by default from 1.35, and the `kubectl alpha kuberc` prefix the post tells you to type is one 1.36 no longer accepts. |
| [Kubernetes v1.37: Garhwal](https://kubernetes.io/blog/2026/08/26/kubernetes-v1-37-release/) | 08-26 | 1.37 | `read` | `meta` | A release announcement, which the rule skips unless a line in it is load-bearing elsewhere. This one says the Storage Version Migration API graduates to Stable and becomes enabled by default; the pin's own gate file for it stops at beta, `defaultValue: false`, from 1.35. |
| Kubernetes v1.37: Scale Workloads to Zero with HorizontalPodAutoscaler (draft) |  | 1.37 | `walk` | `sched` | `HPAScaleToZero` was alpha from 1.16 to 1.36 and reaches beta, on by default, at 1.37 — twenty-one releases, the longest alpha span in all 488 gate files at the pin. A Deployment that drops to zero replicas and comes back is one HPA and one metric. |
| Kubernetes v1.37: Advancing Workload-Aware Scheduling (draft) |  | 1.37 | `read` | `sched` | Workload-aware scheduling two releases on from 2025's exercise 11, which already carries this API and the gate it lost. |
| Kubernetes v1.37: DRA Updates (draft) |  | 1.37 | `read` | `sched` | More DRA features on an API 2025's exercise 08 already carries at v1. |
| Kubernetes v1.37: etcd RangeStream Cuts Memory Use on Large List Reads (draft) |  | 1.37 | `read` | `etcd` | etcd streams large range reads instead of buffering them, so the API server holds less memory during a big list. The saving only appears on a list large enough to matter. |
| Kubernetes v1.37: Metrics API graduates to stable (draft) |  | 1.37 | `walk` | `obs` | `metrics.k8s.io` reaches v1 after sitting at beta from 1.8 to 1.36 — twenty-nine releases, longer than any beta the feature-gate directory records, and invisible to that instrument because an aggregated API has no gate. The pin's reference section still ships only `metrics.v1beta1`, and the HorizontalPodAutoscaler page still says it supports `metrics.k8s.io/v1beta1`. |
| Kubernetes v1.37: Storage Version Migration Enabled by Default (draft) |  | 1.37 | `walk` | `api` | Migrate every stored object to the current storage version without touching any of them. The post says the API is on by default; the pin's gate file says beta and off from 1.35 — the only claimed 1.37 graduation among the twenty-eight gates the release announcement names that has no 1.37 stage at all. |
| Kubernetes v1.37: Introducing Node Lifecycle Conditions (draft) |  | 1.37 | `walk` | `nodes` | A node reports where it is in its own lifecycle, so a workload can tell draining from broken. `NodeLifecycleConditions` is alpha at 1.37 with a single stage and no end version, and the pin adds a reference page for it that no earlier tree had. |
| Kubernetes 1.37: Pod Certificates and Cluster Trust Bundles (draft) |  | 1.37 | `walk` | `security` | A Pod receives an X.509 certificate through a projected volume, signed on request, with the trust anchors in a cluster-scoped bundle. `PodCertificateRequest` runs alpha 1.34 to stable 1.37 and `ClusterTrustBundle` alpha 1.27 to stable 1.37 — ten releases — and the result is a file to read inside the container. |
| Kubernetes v1.37: KubeletInUserNamespace (aka Rootless mode) Graduates to Beta (draft) |  | 1.37 | `read` | `nodes` | `KubeletInUserNamespace` after fifteen releases of alpha, beta and on by default at 1.37. It needs a kubelet that is not running as root, which is a node build rather than a manifest. |
| Kubernetes v1.37: Scheduler Preemption for In-Place Pod Resize (Alpha) (draft) |  | 1.37 | `read` | `sched` | A resize that does not fit can now preempt to make room. Alpha, and it needs a node contended enough for preemption to fire. |

## Exercises

Fourteen `walk` verdicts, numbered in the order the census lists them — publication order, with the
five unpublished drafts last. Two are written; the other twelve are *pending* — an authoring
ticket's to claim. The rubric they are authored against was ratified in
[#57](https://github.com/k3ii/k8s-academy/issues/57).

| # | exercise | state |
|---|---|---|
| 01 | [Two new operators, a gloss that reverses one of them, and an eviction nobody enabled the gate for](01-kubernetes-v1-35-numeric-toleration-operators.md) | written |
| 02 | [The only step-by-step lab the project promised to maintain, resting on nothing the pin ships](02-experimenting-gateway-api-with-kind.md) | written |
| 03 | The weight that changed without a release | pending |
| 04 | One API's objects, printed as another's | pending |
| 05 | The permission that stopped covering everything | pending |
| 06 | Three releases, and a number that moves under load | pending |
| 07 | The field two pages disagree about | pending |
| 08 | The metric nobody was producing yet | pending |
| 09 | Output nothing has to guess at | pending |
| 10 | Twenty-one releases, and then zero replicas | pending |
| 11 | Twenty-nine releases and no gate to show for it | pending |
| 12 | The graduation the gate file never records | pending |
| 13 | Draining is not broken | pending |
| 14 | A certificate that arrives as a file | pending |
