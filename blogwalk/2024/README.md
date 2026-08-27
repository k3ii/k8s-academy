# 2024 — the census

54 posts, 2024-01-15 to 2024-12-18. Kubernetes v1.30 *Uwubernetes*, v1.31 *Elli* and v1.32
*Penelope*. **Almost everything here still runs**, which is the opposite problem from
[2015](../2015/README.md) and the reason this year was censused second — see
[the method](../README.md).

**Yield: 13 `walk`**, at the top of the [8–15 band](../README.md#yield) and inside it. 28 `read`,
3 `dated`, 10 `skip`.

The three `dated` rows are the *DIY: Create Your Own Cloud* series, and they are the cleanest
example of what that verdict now means: genuinely hands-on, genuinely current, and needing
KubeVirt, LINSTOR, Kube-OVN and nested tenant clusters — nowhere near the
[9.5GB ceiling](../../strands/lab-topologies.md#ceiling). Nothing else in the year fails on the
lab; the year's rejects fail on having nothing to do.

Triage cost: 568KB of source, an 82KB first-screen digest, ~390 tokens a post — **14% of reading
the year end-to-end**, against 2015's 31%. 2024's posts are twice as long and their first screen
is a far better predictor of the rest, because the genre is fixed: *what it was, what it is now,
which gate, how to try it*.

## What the rubric could not decide

Three findings, all reported rather than quietly resolved. Each was ruled on in
[#56](https://github.com/k3ii/k8s-academy/issues/56); the rulings are **proposed** amendments
and are frozen in the ratification ticket, not applied here. No ruling moved a row in this
census — two `walk` rows had their `why` rewritten to argue against the new rule instead of
around it.

**The SIG spotlight interview is a genre with no rule.** Nine of 54 posts are interviews — six
with a technical SIG (Release, Cloud Provider, Architecture/Code Organization, Node, API
Machinery, Scheduling) and three with a community group (Book Club, CNCF DHHWG, Upstream
Training Japan). They are not vendor posts, not release notes, and not hangout minutes. The
technical six carry real design rationale straight from maintainers; the community three carry
none. Provisionally `read` and `skip` respectively, which is a judgement the rubric does not
license.

**The `dated`/`read` line does not survive a modern year.** [`dated`](../README.md) is defined
as "hardware or scale beyond the [9.5GB ceiling](../../strands/lab-topologies.md#ceiling)" and
called the one verdict decided by a fact. Eleven of this year's 28 `read` rows fail on the lab
just as squarely, but on a *missing component* rather than on RAM: a CSI driver implementing
`ModifyVolume`, or snapshots, or group snapshots; a real OIDC issuer; CRI-O instead of
containerd; Windows nodes; NUMA or SMT topology; load a 4-vCPU guest cannot generate. The line
I drew, and the rubric does not state, is that `dated` needs the post to be a *walkthrough* the
reader could follow on bigger hardware, while an announcement with a snippet that needs a driver
nobody has is `read`. That is a judgement about the post's genre wearing a fact's clothes.

**`obs` earns zero rows in 2024.** The topic added on 2015's evidence matches nothing here. It
is not wrong — it is unexercised, and one year of evidence for a twelve-slot vocabulary is thin.

## Census

Verdicts and topics are defined in [`../README.md`](../README.md#the-census). Every post has a
row, and a row's title always links the post — never the exercise file, so the row never
changes once written. The **Exercises** table below is the progress record.

| post | date | k8s | verdict | topic | why |
|---|---|---|---|---|---|
| [Spotlight on SIG Release](https://kubernetes.io/blog/2024/01/15/sig-release-spotlight-2023/) | 01-15 | 1.29 | `read` | `meta` | Interview. How the 4-month cycle, code freeze and release artefacts actually get made — the process every "Kubernetes 1.X: Y graduates" post is downstream of. |
| [Image Filesystem: storing containers on a separate filesystem](https://kubernetes.io/blog/2024/01/23/kubernetes-separate-image-filesystem/) | 01-23 | 1.29 | **`walk`** | `nodes` | Split the container store off the root filesystem, then fill it and watch which eviction signal fires. The one 2024 post whose subject is a node you can break. |
| [A look into the Kubernetes Book Club](https://kubernetes.io/blog/2024/02/22/k8s-book-club/) | 02-22 | 1.29 | `skip` | `meta` | Interview about a reading group. No technical content. |
| [Spotlight on SIG Cloud Provider](https://kubernetes.io/blog/2024/03/01/sig-cloud-provider-spotlight-2024/) | 03-01 | 1.29 | `read` | `meta` | Interview. Read it beside the migration post below: this is the SIG that had to make "vendor-neutral" mean something in code. |
| [CRI-O: Applying seccomp profiles from OCI registries](https://kubernetes.io/blog/2024/03/07/cri-o-seccomp-oci-artifacts/) | 03-07 | 1.29 | `read` | `security` | A real idea — ship seccomp profiles as OCI artifacts instead of files on every node — but it is CRI-O-only and the lab runs containerd. The argument transfers; the commands do not. |
| [A Peek at Kubernetes v1.30](https://kubernetes.io/blog/2024/03/12/kubernetes-1-30-upcoming-changes/) | 03-12 | 1.30 | `skip` | `meta` | Mid-cycle preview. Every item in it is covered by its own post six weeks later. |
| [Introducing the Windows Operational Readiness Specification](https://kubernetes.io/blog/2024/04/03/intro-windows-ops-readiness/) | 04-03 | 1.29 | `read` | `nodes` | The lab has no Windows nodes, so nothing here is runnable, but the framing is worth one read: conformance has to be certifiable without buying a licence. |
| [DIY: Create Your Own Cloud with Kubernetes (Part 1)](https://kubernetes.io/blog/2024/04/05/diy-create-your-own-cloud-with-kubernetes-part-1/) | 04-05 | 1.29 | `dated` | `ecosystem` | Talos plus Flux on bare metal. Hands-on and current; needs bare metal. |
| [DIY: Create Your Own Cloud with Kubernetes (Part 2)](https://kubernetes.io/blog/2024/04/05/diy-create-your-own-cloud-with-kubernetes-part-2/) | 04-05 | 1.29 | `dated` | `ecosystem` | KubeVirt, LINSTOR and Kube-OVN. Replicated block storage and VMs inside the cluster, far past the ceiling. |
| [DIY: Create Your Own Cloud with Kubernetes (Part 3)](https://kubernetes.io/blog/2024/04/05/diy-create-your-own-cloud-with-kubernetes-part-3/) | 04-05 | 1.29 | `dated` | `ecosystem` | Kamaji and Cluster API running tenant clusters inside a cluster. The `nested` topology gestures at this; three control planes do not fit in it. |
| [Spotlight on SIG Architecture: Code Organization](https://kubernetes.io/blog/2024/04/11/sig-architecture-code-spotlight-2024/) | 04-11 | 1.29 | `read` | `meta` | Interview. Why staging repos and `k8s.io/*` published modules exist, and what "stay on supported Go versions" costs a project this size. |
| [Kubernetes v1.30: Uwubernetes](https://kubernetes.io/blog/2024/04/17/kubernetes-v1-30-release/) | 04-17 | 1.30 | `skip` | `meta` | Release announcement, 45 enhancements. Every load-bearing item has its own post. |
| [Beta Support For Pods With User Namespaces](https://kubernetes.io/blog/2024/04/22/userns-beta/) | 04-22 | 1.30 | **`walk`** | `security` | `hostUsers: false`. The post says beta-and-off; at the pin it is stable and locked on. Root in the container, nobody on the host — provable in one `id` and one file write. |
| [Read-only volume mounts can be finally literally read-only](https://kubernetes.io/blog/2024/04/23/recursive-read-only-mounts/) | 04-23 | 1.30 | **`walk`** | `storage` | `readOnly: true` was never recursive, and for nine years nothing told you. Alpha here, locked-stable at the pin. The bug is the lesson. |
| [Validating Admission Policy Is Generally Available](https://kubernetes.io/blog/2024/04/24/validating-admission-policy-ga/) | 04-24 | 1.30 | **`walk`** | `security` | No ladder discontinuity — GA here, GA at the pin — so this one earns `walk` on the observable half: a CEL expression rejecting a Deployment with a message you wrote, against the served TLS endpoint and Go binary the same rule needed a release earlier. What the post could not say is that the mutating half arrived too, so the genre stopped being "webhooks or nothing". |
| [Structured Authentication Configuration Moves to Beta](https://kubernetes.io/blog/2024/04/25/structured-authentication-moves-to-beta/) | 04-25 | 1.30 | `read` | `security` | Multiple JWT authenticators, reloadable without an API server restart. Needs a real OIDC issuer to exercise; read it for the reason the flag-based design ran out of room. |
| [Multi-Webhook and Modular Authorization Made Much Easier](https://kubernetes.io/blog/2024/04/26/multi-webhook-and-modular-authorization-made-much-easier/) | 04-26 | 1.30 | `read` | `security` | The authorization chain becomes a file instead of a flag. Pairs with the `AlwaysAllow` trap in the [translation record](../../research/blog-era-translation.md). |
| [Preventing unauthorized volume mode conversion moves to GA](https://kubernetes.io/blog/2024/04/30/prevent-unauthorized-volume-mode-conversion-ga/) | 04-30 | 1.30 | `read` | `storage` | Needs a CSI driver with snapshot support. The security gap it closes — snapshot a filesystem volume, restore it as raw block — is worth the two minutes. |
| [Container Runtime Interface streaming explained](https://kubernetes.io/blog/2024/05/01/cri-streaming-explained/) | 05-01 | 1.30 | `read` | `nodes` | Exec, Attach and PortForward are unlike every other CRI call. Read this before the WebSockets exercise; it is the half the exercise assumes. |
| [Gateway API v1.1: Service mesh, GRPCRoute, and more](https://kubernetes.io/blog/2024/05/09/gateway-api-v1-1/) | 05-09 | 1.30 | `read` | `net` | Mesh and GRPCRoute reach Standard. The hands-on half is [`labs/09`](../../labs/09/)'s, so this is a `read` under the redundancy clause, not for lack of substance. |
| [Completing the largest migration in Kubernetes history](https://kubernetes.io/blog/2024/05/20/completing-cloud-provider-migration/) | 05-20 | 1.30 | `read` | `history` | 1.5M lines of Go removed, core binaries 40% smaller, four new subsystems built to do it. The best single account of what "vendor-neutral" cost. |
| [10 Years of Kubernetes](https://kubernetes.io/blog/2024/06/06/10-years-of-kubernetes/) | 06-06 | 1.30 | `skip` | `meta` | Anniversary post: contributor counts and testimonials. |
| [Spotlight on SIG Node](https://kubernetes.io/blog/2024/06/20/sig-node-spotlight-2024/) | 06-20 | 1.30 | `read` | `meta` | Interview. The SIG that owns the kubelet on why node features take so many releases — useful context for every graduation ladder in this year. |
| [Removals and Major Changes In v1.31](https://kubernetes.io/blog/2024/07/19/kubernetes-1-31-upcoming-changes/) | 07-19 | 1.31 | `read` | `api` | Load-bearing for the whole archive, and not in the way it intends: this is the genre [#54](https://github.com/k3ii/k8s-academy/issues/54) proved gets its own removals wrong in both directions. Read it as a claim to check, never as a record. |
| [Spotlight on SIG API Machinery](https://kubernetes.io/blog/2024/08/07/sig-api-machinery-spotlight-2024/) | 08-07 | 1.30 | `read` | `meta` | Interview with the people who own the API server. Includes the origin of `kubeconfig` and of the `*Review` APIs, both ported from OpenShift. |
| [Introducing Feature Gates to Client-Go](https://kubernetes.io/blog/2024/08/12/feature-gates-in-client-go/) | 08-12 | 1.31 | `read` | `tooling` | Gates move client-side. Matters if you write controllers; nothing to run. |
| [Kubernetes v1.31: Elli](https://kubernetes.io/blog/2024/08/13/kubernetes-v1-31-release/) | 08-13 | 1.31 | `skip` | `meta` | Release announcement, 45 enhancements. |
| [Moving cgroup v1 Support into Maintenance Mode](https://kubernetes.io/blog/2024/08/14/kubernetes-1-31-moving-cgroup-v1-support-maintenance-mode/) | 08-14 | 1.31 | **`walk`** | `nodes` | "Maintenance mode" is not a state the deprecation policy defines, which is exactly why it is worth walking: find out what the phrase turned into by the pin, on a node you can inspect. |
| [PersistentVolume Last Phase Transition Time Moves to GA](https://kubernetes.io/blog/2024/08/14/last-phase-transition-time-ga/) | 08-14 | 1.31 | `read` | `storage` | One status field, 2KB of post. Real, trivial, no exercise in it. |
| [Accelerating Cluster Performance with Consistent Reads from Cache](https://kubernetes.io/blog/2024/08/15/consistent-read-from-cache-beta/) | 08-15 | 1.31 | `read` | `etcd` | Watch-cache reads with an etcd progress-notify fence instead of a quorum read. Visible only under load the lab cannot generate. |
| [VolumeAttributesClass for Volume Modification Beta](https://kubernetes.io/blog/2024/08/15/kubernetes-1-31-volume-attributes-class/) | 08-15 | 1.31 | `read` | `storage` | Needs a CSI driver implementing `ModifyVolume`. The gap it fills — IOPS is neither the storage class nor the capacity — is the interesting part. |
| [Prevent PersistentVolume Leaks When Deleting out of Order](https://kubernetes.io/blog/2024/08/16/kubernetes-1-31-prevent-persistentvolume-leaks-when-deleting-out-of-order/) | 08-16 | 1.31 | **`walk`** | `storage` | Delete the PV before the PVC and the backing volume leaks silently. Reproducible with the local-path provisioner, and the failure leaves no event. |
| [Read Only Volumes Based On OCI Artifacts (alpha)](https://kubernetes.io/blog/2024/08/16/kubernetes-1-31-image-volume-source/) | 08-16 | 1.31 | **`walk`** | `storage` | Mount an image as a volume. Alpha behind a gate here; at the pin, stable — via a beta that stayed *off by default for two releases*, which no graduation post mentions. |
| [MatchLabelKeys in PodAffinity graduates to beta](https://kubernetes.io/blog/2024/08/16/matchlabelkeys-podaffinity/) | 08-16 | 1.31 | **`walk`** | `sched` | During a rolling update the scheduler cannot tell old pods from new ones, so anti-affinity fights the rollout. `pod-template-hash` in `matchLabelKeys` fixes it, and you can watch it deadlock first. |
| [Pod Failure Policy for Jobs Goes GA](https://kubernetes.io/blog/2024/08/19/kubernetes-1-31-pod-failure-policy-for-jobs-goes-ga/) | 08-19 | 1.31 | **`walk`** | `api` | `backoffLimit` alone cannot tell a retriable failure from a hopeless one, so it burns money either way. Fail fast on exit code, ignore a preemption — both observable in one Job. |
| [Streaming Transitions from SPDY to WebSockets](https://kubernetes.io/blog/2024/08/20/websockets-transition/) | 08-20 | 1.31 | **`walk`** | `api` | The post is still true and that is the trap: swapping POST for GET quietly moved the RBAC surface of `pods/exec`, and it took until v1.35 to notice. Also where [2015's `nsenter` hangout note](../2015/README.md) finally lands. |
| [Autoconfiguration For Node Cgroup Driver (beta)](https://kubernetes.io/blog/2024/08/21/cri-cgroup-driver-lookup-now-beta/) | 08-21 | 1.31 | `read` | `nodes` | The kubelet asks the runtime instead of being told twice. 1.6KB, and the cgroup exercise carries the observable half. |
| [New CPUManager Static Policy: Distribute CPUs Across Cores](https://kubernetes.io/blog/2024/08/22/cpumanager-static-policy-distributed-cpu-across-cores/) | 08-22 | 1.31 | `read` | `nodes` | Alpha and hidden, and it needs real SMT topology to mean anything. A 4-vCPU guest cannot show the contention it fixes. |
| [Custom Profiling in Kubectl Debug Graduates to Beta](https://kubernetes.io/blog/2024/08/22/kubernetes-1-31-custom-profiling-kubectl-debug/) | 08-22 | 1.31 | **`walk`** | `tooling` | Also `walk` on the observable half rather than a discontinuity: the default debug container gets no env, no resource limits and no volume mounts, so debugging a pod that needed any of them was not possible at all. One command pair shows the before and the after, and it is the cheapest exercise in the year. |
| [Fine-grained SupplementalGroups control](https://kubernetes.io/blog/2024/08/22/fine-grained-supplementalgroups-control/) | 08-22 | 1.31 | **`walk`** | `security` | Your pod has a group you never granted, because the kubelet merges `/etc/group` from the image. One `id` proves it; `supplementalGroupsPolicy: Strict` stops it. |
| [kubeadm v1beta4](https://kubernetes.io/blog/2024/08/23/kubernetes-1-31-kubeadm-v1beta4/) | 08-23 | 1.31 | **`walk`** | `tooling` | The lab is a kubeadm lab, so this one is not hypothetical: v1beta3 is deprecated here, and the exercise is to find out what happened to it by the pin before an upgrade finds out for you. |
| [Spotlight on SIG Scheduling](https://kubernetes.io/blog/2024/09/24/sig-scheduling-spotlight-2024/) | 09-24 | 1.31 | `read` | `meta` | Interview. The scheduler simulator and the WASM extension subproject both exist and both are worth a look. |
| [Spotlight on CNCF Deaf and Hard-of-hearing Working Group](https://kubernetes.io/blog/2024/09/30/cncf-deaf-and-hard-of-hearing-working-group-spotlight/) | 09-30 | 1.31 | `skip` | `meta` | Community interview. No technical content. |
| [Announcing the 2024 Steering Committee Election Results](https://kubernetes.io/blog/2024/10/02/steering-committee-results-2024/) | 10-02 | 1.31 | `skip` | `meta` | Election results. |
| [Spotlight on Kubernetes Upstream Training in Japan](https://kubernetes.io/blog/2024/10/28/k8s-upstream-training-japan-spotlight/) | 10-28 | 1.31 | `skip` | `meta` | Community interview about a contributor onboarding programme. |
| [Kubernetes v1.32 sneak peek](https://kubernetes.io/blog/2024/11/08/kubernetes-1-32-upcoming-changes/) | 11-08 | 1.32 | `skip` | `meta` | Deprecation preview. Superseded by the release it previews. |
| [How we built a dynamic API Server for the Aggregation Layer in Cozystack](https://kubernetes.io/blog/2024/11/21/dynamic-kubernetes-api-server-for-cozystack/) | 11-21 | 1.31 | `read` | `api` | A vendor post that earns its row: it states why CRDs plus a controller were rejected and what the aggregation layer bought instead. Under [the vendor rule](../README.md#three-genres-with-a-rule-because-they-are-most-of-the-corpus) that makes it `read`, and the same rule keeps it off `walk`. |
| [Gateway API v1.2: WebSockets, Timeouts, Retries, and More](https://kubernetes.io/blog/2024/11/21/gateway-api-v1-2/) | 11-21 | 1.32 | `read` | `net` | Notable for the breaking change: `v1alpha2` GRPCRoute and ReferenceGrant removed, and a controller still speaking `v1alpha2` breaks even if your YAML says `v1`. |
| [Kubernetes v1.32: Penelope](https://kubernetes.io/blog/2024/12/11/kubernetes-v1-32-release/) | 12-11 | 1.32 | `skip` | `meta` | Release announcement, 44 enhancements. |
| [QueueingHint Brings a New Possibility to Optimize Pod Scheduling](https://kubernetes.io/blog/2024/12/12/scheduler-queueinghint/) | 12-12 | 1.32 | `read` | `sched` | ActiveQ, BackoffQ and the unschedulable pool, and why a pod used to wait 5 minutes for an event that had already happened. Best explanation of the scheduling queue anywhere. |
| [Memory Manager Goes GA](https://kubernetes.io/blog/2024/12/13/memory-manager-goes-ga/) | 12-13 | 1.32 | `read` | `nodes` | GA after ten releases in beta. Needs NUMA topology the guests do not have. |
| [A New CPU Manager Static Policy Option For Strict CPU Reservation](https://kubernetes.io/blog/2024/12/16/cpumanager-strict-cpu-reservation/) | 12-16 | 1.32 | `read` | `nodes` | Alpha and hidden. `reservedSystemCPUs` was never actually exclusive for burstable and best-effort pods — worth reading, not worth a 4-vCPU guest. |
| [Enhancing API Server Efficiency with API Streaming](https://kubernetes.io/blog/2024/12/17/kube-apiserver-api-streaming/) | 12-17 | 1.32 | `read` | `api` | The API server used to assemble every **list** response in memory before sending a byte, so a few concurrent lists could OOM it. Watch-list streaming fixes it; you need a big cluster to see it. |
| [Moving Volume Group Snapshots to Beta](https://kubernetes.io/blog/2024/12/18/kubernetes-1-32-volume-group-snapshot-beta/) | 12-18 | 1.32 | `read` | `storage` | Crash-consistent snapshots across a set of PVCs. Needs a CSI driver that implements group snapshots. |

## Exercises

Thirteen `walk` verdicts, numbered in publication order. Two are written; the eleven marked
*pending* are an authoring ticket's to claim. The rubric they are authored against was ratified
in [#57](https://github.com/k3ii/k8s-academy/issues/57).

| # | exercise | state |
|---|---|---|
| 01 | Image filesystem on its own disk | pending |
| 02 | User namespaces | pending |
| 03 | Recursive read-only mounts | pending |
| 04 | ValidatingAdmissionPolicy | pending |
| 05 | cgroup v1 in maintenance mode | pending |
| 06 | Honouring the reclaim policy | pending |
| 07 | [A gate is not a schedule](07-image-volume-source.md) | written |
| 08 | matchLabelKeys in PodAffinity | pending |
| 09 | Pod failure policy for Jobs | pending |
| 10 | [The protocol changed, and so did who is allowed to use it](10-websocket-transition.md) | written |
| 11 | Custom profiling in kubectl debug | pending |
| 12 | Fine-grained SupplementalGroups | pending |
| 13 | kubeadm v1beta4 | pending |
