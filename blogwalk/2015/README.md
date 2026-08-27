# 2015 — the census

44 posts, 2015-03-20 to 2015-12-22. Kubernetes 0.13 to 1.1; 1.0 shipped on 2015-07-21, four
months into the blog's life. **Nothing here runs as written.** v1beta3 arrives and is
superseded by v1 inside a month, there is no RBAC, no Deployment, no kubeadm, no CRI, no
Ingress, and `kubectl apply` does not exist yet.

That is why 2015 was censused first — see [the method](../README.md). If the format survives
this year it survives the staleness case entirely.

**Yield: 10 `walk`**, inside the [8–15 band](../README.md#yield). 11 `read`, 2 `dated`,
21 `skip`. The 21 rejects are 11 weekly-hangout notes, a launch party, a training-course ad, a
UX-study recruitment, two video posts, a slide deck, two changelog dumps and three vendor
availability announcements — a little under half the year, which is what a project's first nine
months of blogging looks like.

Only 2 rows are `dated`, and both for the same reason: *One million requests per second* wants a
cloud load balancer and hundreds of nodes, and *Raspberry Pi Part 1* is a bill of materials.
Nothing else in the year fails on the lab ceiling. Two posts that were hands-on but whose
technique is redundant or whose tool is abandoned — Sysdig and the Puppet module — are `read`,
per [the verdict definitions](../README.md#the-census).

Triage cost: 299KB of source, a 93KB first-screen digest, ~530 tokens a post.

## Census

Verdicts and topics are defined in [`../README.md`](../README.md#the-census). Every post has a
row, and a row's title always links the post — never the exercise file, so the row never
changes once written. The **Exercises** table below is the progress record.

| post | date | k8s | verdict | topic | why |
|---|---|---|---|---|---|
| [Welcome to the Kubernetes Blog!](https://kubernetes.io/blog/2015/03/welcome-to-kubernetes-blog/) | 03-20 | — | `skip` | `meta` | A link roundup to nine posts on other sites, six of which 404. |
| [Kubernetes Gathering Videos](https://kubernetes.io/blog/2015/03/kubernetes-gathering-videos/) | 03-23 | — | `skip` | `meta` | A YouTube playlist embed, 301 characters long. |
| [Hangout notes — March 27](https://kubernetes.io/blog/2015/03/Weekly-Kubernetes-Community-Hangout/) | 03-28 | — | `skip` | `meta` | Raw meeting notes. Carries the `kubectl exec` demo — SPDY over HTTP, entered via `nsenter` — but as minutes, not as a lesson. |
| [Participate in a Kubernetes User Experience Study](https://kubernetes.io/blog/2015/03/participate-in-kubernetes-user/) | 03-31 | — | `skip` | `meta` | Recruitment ad; the study ran April 2015. |
| [Hangout notes — April 3](https://kubernetes.io/blog/2015/04/Weekly-Kubernetes-Community-Hangout/) | 04-04 | — | `skip` | `meta` | Minutes. The cluster-federation design discussion that became Ubernetes, then KubeFed, then nothing. |
| [Faster than a speeding Latte](https://kubernetes.io/blog/2015/04/faster-than-speeding-latte/) | 04-06 | — | `skip` | `meta` | 129 characters and a YouTube shortcode. |
| [Hangout notes — April 10](https://kubernetes.io/blog/2015/04/weekly-kubernetes-community-hangout_11/) | 04-11 | — | `skip` | `meta` | Minutes. Contains the argument that produced the Deployment object — "treating rcs as pets vs. cattle" — in note form. |
| [Introducing Kubernetes API Version v1beta3](https://kubernetes.io/blog/2015/04/introducing-kubernetes-v1beta3/) | 04-16 | 0.15 | **`walk`** | `api` | Every version named in it is dead, including the one it calls the release candidate. The whole payload is why the API is versioned at all. |
| [Kubernetes Release: 0.15.0](https://kubernetes.io/blog/2015/04/kubernetes-release-0150/) | 04-16 | 0.15 | `read` | `api` | The changelog half of the row above: v1beta3 becomes the default API *and* the etcd storage version, so stored objects were rewritten on read. |
| [Hangout notes — April 17](https://kubernetes.io/blog/2015/04/weekly-kubernetes-community-hangout_17/) | 04-17 | — | `skip` | `meta` | Minutes. |
| [Kubernetes and the Mesosphere DCOS](https://kubernetes.io/blog/2015/04/kubernetes-and-mesosphere-dcos/) | 04-22 | 0.15 | `read` | `history` | The product is gone, but this is where "cloud native" gets defined in three bullets, three months before the CNCF existed. |
| [Borg: The Predecessor to Kubernetes](https://kubernetes.io/blog/2015/04/borg-predecessor-to-kubernetes/) | 04-23 | 0.15 | `read` | `history` | Four Kubernetes features traced to a Borg feature, by the people who wrote both. Nothing to run; it explains the shape of everything you do run. |
| [Hangout notes — April 24](https://kubernetes.io/blog/2015/04/weekly-kubernetes-community-hangout_29/) | 04-30 | — | `skip` | `meta` | Minutes. |
| [AppC Support for Kubernetes through RKT](https://kubernetes.io/blog/2015/05/appc-support-for-kubernetes-through-rkt/) | 05-04 | 0.15 | `read` | `history` | The rkt bet, stated as a bet. rkt was archived in 2020; read it for what "support two runtimes with in-tree code" cost, which is the pressure CRI answered. |
| [Kubernetes Release: 0.16.0](https://kubernetes.io/blog/2015/05/kubernetes-release-0160/) | 05-11 | 0.16 | `read` | `api` | One line in a changelog — "Cloning v1beta3 as v1 and exposing it in the apiserver" — is the moment `v1` exists. |
| [Hangout notes — May 1](https://kubernetes.io/blog/2015/05/Weekly-Kubernetes-Community-Hangout/) | 05-11 | — | `skip` | `meta` | Minutes. |
| [Resource Usage Monitoring in Kubernetes](https://kubernetes.io/blog/2015/05/resource-usage-monitoring-kubernetes/) | 05-12 | 0.16 | **`walk`** | `obs` | Heapster is archived and unpublished, cAdvisor's port 4194 is gone, and the modern path is a different API with a different owner. |
| [Kubernetes Release: 0.17.0](https://kubernetes.io/blog/2015/05/kubernetes-release-0170/) | 05-15 | 0.17 | `skip` | `meta` | 55KB of PR titles — the largest post of the year and the emptiest. The v1beta3 conversion churn it records is already the payload of two rows above. |
| [Docker and Kubernetes and AppC](https://kubernetes.io/blog/2015/05/docker-and-kubernetes-and-appc/) | 05-18 | 0.17 | **`walk`** | `nodes` | "We intend to continue to support Docker indefinitely." Indefinitely ended in v1.24, and the thing that replaced it is an interface, not a runtime. |
| [Hangout notes — May 15](https://kubernetes.io/blog/2015/05/weekly-kubernetes-community-hangout_18/) | 05-18 | — | `skip` | `meta` | Minutes. |
| [Kubernetes on OpenStack](https://kubernetes.io/blog/2015/05/kubernetes-on-openstack/) | 05-19 | 0.17 | `skip` | `ecosystem` | Availability announcement for a Murano app catalog entry; the catalog and the repo it points at are both gone. |
| [Hangout notes — May 22](https://kubernetes.io/blog/2015/06/Weekly-Kubernetes-Community-Hangout/) | 06-02 | — | `skip` | `meta` | Minutes. |
| [Cluster Level Logging with Kubernetes](https://kubernetes.io/blog/2015/06/cluster-level-logging-with-kubernetes/) | 06-11 | pre-1.0 | **`walk`** | `obs` | A fluentd DaemonSet, Elasticsearch and Kibana shipped *with* the cluster. Kubernetes ships no logging at all now, and that was a decision. |
| [Slides: Cluster Management with Kubernetes](https://kubernetes.io/blog/2015/06/slides-cluster-management-with/) | 06-26 | pre-1.0 | `skip` | `meta` | Two links to a Google Slides deck. |
| [The Distributed System ToolKit: Patterns for Composite Containers](https://kubernetes.io/blog/2015/06/the-distributed-system-toolkit-patterns/) | 06-29 | pre-1.0 | **`walk`** | `api` | Sidecar, ambassador and adapter are still the three names everyone uses. The manifests are cosmetic; what changed is that one of the three became a field. |
| [How did the Quake demo from DockerCon Work?](https://kubernetes.io/blog/2015/07/how-did-quake-demo-from-dockercon-work/) | 07-02 | pre-1.0 | **`walk`** | `nodes` | Checkpoint/restore, done outside Kubernetes with CRIU because nothing supported it. The kubelet has an endpoint for it now — still alpha, eleven years later. |
| [Kubernetes 1.0 Launch Event at OSCON](https://kubernetes.io/blog/2015/07/kubernetes-10-launch-party-at-oscon/) | 07-02 | pre-1.0 | `skip` | `meta` | Party invitation. `kuberneteslaunch.com` no longer resolves. |
| [Announcing the First Kubernetes Enterprise Training Course](https://kubernetes.io/blog/2015/07/announcing-first-kubernetes-enterprise/) | 07-08 | pre-1.0 | `skip` | `meta` | Course ad; the course ran on 2015-07-20. |
| [Hangout notes — July 10](https://kubernetes.io/blog/2015/07/Weekly-Kubernetes-Community-Hangout/) | 07-13 | — | `skip` | `meta` | Minutes. |
| [Strong, Simple SSL for Kubernetes Services](https://kubernetes.io/blog/2015/07/strong-simple-ssl-for-kubernetes/) | 07-14 | pre-1.0 | **`walk`** | `security` | Neither strong nor simple now: an nginx sidecar terminating TLS from a hand-rolled secret, no rotation, no issuer, no expiry. Every layer of that has an owner today. |
| [Hangout notes — July 17](https://kubernetes.io/blog/2015/07/weekly-kubernetes-community-hangout_23/) | 07-23 | — | `skip` | `meta` | Minutes. |
| [The Growing Kubernetes Ecosystem](https://kubernetes.io/blog/2015/07/the-growing-kubernetes-ecosystem/) | 07-24 | 1.0 | `read` | `ecosystem` | A census of the ecosystem in the week 1.0 shipped. Read it as a survivorship list: count how many of the fifteen still exist under the same name. |
| [Hangout notes — July 31](https://kubernetes.io/blog/2015/08/Weekly-Kubernetes-Community-Hangout/) | 08-04 | — | `skip` | `meta` | Minutes. |
| [Using Kubernetes Namespaces to Manage Environments](https://kubernetes.io/blog/2015/08/using-kubernetes-namespaces-to-manage/) | 08-28 | 1.0 | **`walk`** | `api` | Almost the only 2015 post whose commands still run. The advice is what expired: a namespace is not an isolation boundary, and nothing in the post would tell you. |
| [Kubernetes Performance Measurements and Roadmap](https://kubernetes.io/blog/2015/09/kubernetes-performance-measurements-and/) | 09-10 | 1.0 | `read` | `obs` | Two SLOs — 99% of API calls under 1s, 99% of pod startups under 5s — set in 2015 and still the scalability SLOs. The node target moved 100 → 5000; the promises did not. |
| [Some things you didn't know about kubectl](https://kubernetes.io/blog/2015/10/some-things-you-didnt-know-about-kubectl_28/) | 10-28 | 1.0 | **`walk`** | `tooling` | Six features, one per section, and the fate of each is different: still there, renamed, silently ignored for three releases, or removed outright. |
| [Kubernetes as Foundation for Cloud Native PaaS](https://kubernetes.io/blog/2015/11/kubernetes-as-foundation-for-cloud-native-paas/) | 11-03 | 1.0 | `skip` | `ecosystem` | Four vendor quote blocks. Deis, Gondor and OpenShift v3's PaaS framing all went elsewhere; no argument survives the quotes. |
| [Kubernetes 1.1 Performance upgrades, improved tooling and a growing community](https://kubernetes.io/blog/2015/11/kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community/) | 11-09 | 1.1 | **`walk`** | `net` | Announces iptables kube-proxy as an *option* with an 80% tail-latency claim. It is still the default at v1.37, and nftables — GA since 1.33 — still is not. |
| [One million requests per second](https://kubernetes.io/blog/2015/11/one-million-requests-per-second-dependable-and-dynamic-distributed-systems-at-scale/) | 11-11 | 1.1 | `dated` | `net` | Was hands-on, but needs a cloud load balancer and hundreds of nodes. The rolling-update argument inside it is carried better by the 1.1 row above. |
| [Monitoring Kubernetes with Sysdig](https://kubernetes.io/blog/2015/11/monitoring-kubernetes-with-sysdig/) | 11-19 | 1.1 | `read` | `obs` | `csysdig` still runs and the syscall-level view is worth seeing, but the product split into Falco and a SaaS and the cluster-side half of the lesson is the Heapster exercise's. Redundant, not out of reach. |
| [Creating a Raspberry Pi cluster, the shopping list (Part 1)](https://kubernetes.io/blog/2015/11/creating-a-raspberry-pi-cluster-running-kubernetes-the-shopping-list-part-1/) | 11-25 | 1.1 | `dated` | `nodes` | A 2015 bill of materials — Pi 2 model B, 8GB SD cards. The hands-on half is Part 2. |
| [How Weave built a multi-deployment solution for Scope using Kubernetes](https://kubernetes.io/blog/2015/12/how-weave-built-a-multi-deployment-solution-for-scope-using-kubernetes/) | 12-12 | 1.1 | `read` | `ecosystem` | A real production architecture written up honestly, including what they rejected. The "three environments as near identical as possible" requirement is the GitOps argument, four years early. |
| [Managing Kubernetes Pods, Services and Replication Controllers with Puppet](https://kubernetes.io/blog/2015/12/managing-kubernetes-pods-services-and-replication-controllers-with-puppet/) | 12-17 | 1.1 | `read` | `tooling` | The module is abandoned and generated from Swagger that no longer exists. Worth one paragraph, not an exercise: a run-once config manager pointed at a level-triggered controller, which is the argument GitOps settled. |
| [Creating a Raspberry Pi cluster, the installation (Part 2)](https://kubernetes.io/blog/2015/12/creating-raspberry-pi-cluster-running/) | 12-22 | 1.1 | `read` | `nodes` | Pre-kubeadm bring-up in full: `docker run` each control-plane component by hand, on ARM, with `--api-servers` on every kubelet. Read as the problem statement kubeadm was written against. |

## Exercises

Ten `walk` verdicts, numbered in publication order. Two are written; the eight marked *pending*
are an authoring ticket's to claim. The rubric they are authored against was ratified in
[#57](https://github.com/k3ii/k8s-academy/issues/57).

| # | exercise | state |
|---|---|---|
| 01 | [Every version in this post is dead, and every rename in it is still law](01-introducing-kubernetes-v1beta3.md) | written |
| 02 | Resource usage monitoring | pending |
| 03 | Docker, appc, and the interface that replaced both | pending |
| 04 | Cluster-level logging | pending |
| 05 | [Two of the three patterns are still patterns; one became a field](05-the-distributed-system-toolkit-patterns.md) | written |
| 06 | Checkpoint and restore | pending |
| 07 | Strong, simple SSL | pending |
| 08 | Namespaces as environments | pending |
| 09 | kubectl's undocumented corners | pending |
| 10 | iptables, and the default that never moved | pending |
