<a id="experimenting-gateway-api-with-kind"></a>

# The project promised to maintain this one forever and it is the only step-by-step lab among the forty-four carrying that promise, yet the pin ships nothing the post installs, describes kind on three pages that disagree about what it is for, and gives a Gateway its address in one clause

**Post** — [Experimenting with Gateway API using kind](https://kubernetes.io/blog/2026/01/28/experimenting-gateway-api-with-kind/),
2026-01-28.

No Kubernetes version. The post names none, and the only `v1.` string in its 358 lines is a Gateway
API release inside an image tag at `:194`; the census marks its Kubernetes column `—` for that
reason. 10,823 bytes, by Ricardo Katz (Red Hat), the fourth post of 2026 and the year's second walk.
Sixteen fences: twelve shell and four YAML. Its frontmatter carries `evergreen: true` at `:6`, and
that line is the reason this file is longer than the tutorial it reads.

**As written**

The post is a lab, and it says so in its first sentence: *"This document will guide you through
setting up a local experimental environment with Gateway API on kind"* (`:11`). A caution at
`:13-17` fences it off from production before the reader has done anything. Four prerequisites at
`:32-35` — Docker, kubectl, kind, curl — and then five moves.

`kind create cluster` (`:43`). Then cloud-provider-kind, which the post introduces at `:49-52` as
providing three things at once: *"A LoadBalancer controller that assigns addresses to
LoadBalancer-type Services"*, *"A Gateway API controller that implements the Gateway API
specification"*, and — the sentence that matters most — *"It also automatically installs the Gateway
API Custom Resource Definitions (CRDs) in your cluster."* It is run as a container on the host, not
in the cluster:

```sh
VERSION="$(basename $(curl -s -L -o /dev/null -w '%{url_effective}' https://github.com/kubernetes-sigs/cloud-provider-kind/releases/latest))"
docker run -d --name cloud-provider-kind --rm --network host -v /var/run/docker.sock:/var/run/docker.sock registry.k8s.io/cloud-provider-kind/cloud-controller-manager:${VERSION}
```

A note follows at `:62`: *"On some systems, you may need elevated privileges to access the Docker
socket."* Then `:81` tells the reader that a GatewayClass named `cloud-provider-kind` has appeared
without their asking, and `:83` explains the naming: *"while kind is not a cloud provider, the
project is named as `cloud-provider-kind` as it provides features that simulate a cloud-enabled
environment."*

The third move is a Namespace and a Gateway in one manifest (`:96-118`) — namespace `gateway-infra`,
one listener on port 80, `hostname: "*.exampledomain.example"`, and `allowedRoutes.namespaces.from:
All`. The bullet introducing that last field carries its own warning at `:91-92`: *"In real
clusters, prefer Same or Selector values on the `allowedRoutes` namespace selector field to limit
attachments."* The post then shows what success looks like (`:126-129`):

```
NAME      CLASS                 ADDRESS      PROGRAMMED   AGE
gateway   cloud-provider-kind   172.18.0.3   True         5m6s
```

Fourth, an echo application in a namespace called `demo` (`:143-196`) — a Service on port 3000 and a
Deployment running `registry.k8s.io/gateway-api/echo-basic:v20251204-v1.4.1` — and an HTTPRoute
(`:208-227`) that lives in `demo`, names `parentRefs: [{name: gateway, namespace: gateway-infra}]`,
and matches the hostname `some.exampledomain.example`. Fifth, the test (`:234-236`):

```sh
GW_ADDR=$(kubectl get gateway -n gateway-infra gateway -o jsonpath='{.status.addresses[0].value}')
curl --resolve some.exampledomain.example:80:${GW_ADDR} http://some.exampledomain.example
```

A troubleshooting section at `:263-315` closes the technical content, and a cleanup at `:317-346`
deletes two namespaces, stops the container and deletes the cluster. The last words of the post
(`:356-358`) repeat the first caution: *"This kind setup is for development and learning only."*

**As it runs now** — it runs. That is the unusual part, and everything interesting about this file
follows from it.

Every command in the post still works at the pin. No API group moved, no field was renamed, no kind
was deprecated. Run the five moves in order on a machine with Docker and you get a Gateway with an
address and a `curl` that returns JSON. This exercise therefore cannot be about breakage. It is
about what a document promises, what the pinned tree can back that promise with, and what the pin
says about the one piece of the lab it does own.

**The project promised to maintain this one indefinitely.** `:6` reads `evergreen: true`, and
`docs/contribute/blog/_index.md:53-58` is where that key is defined: *"You can mark an article as
evergreen by setting `evergreen: true` in the front matter. We only mark blog articles as maintained
(`evergreen: true` in front matter) if the Kubernetes project can commit to maintaining them
indefinitely."* The default it opts out of is stated eighteen lines above, at `:38-41`: *"any
published article more than one year old will normally not be eligible for issues or pull requests
that ask for changes. To avoid establishing precedent, even technically correct pull requests are
likely to be rejected."* The mark is the difference between a document that can be fixed and one
that is frozen where it was written.

**Forty-four posts in 767 carry the mark, and forty of them have nothing left to maintain.** Count
them in the archive and the list is release announcements — 0.16, 0.17, 1.1, 1.2, 1.3, 1.8, 1.9,
every release from 1.10 to 1.23, and 1.33 through 1.37 — plus contributor summit write-ups, an
obituary, the updated dockershim FAQ, a historical-context essay on PodSecurityPolicy, a third-party
audit, and a notice that a tutorial platform shut down. Those are finished documents: records of a
moment, and a record cannot go out of date because the moment does not move. Forty of the forty-four
contain zero shell fences.

**This post carries twelve, which is more than any other evergreen post in the archive.** Twelve
shell fences and four YAML, against ten and two for the next highest, and zero for everything
outside the top three. It is the only one of the forty-four that is a step-by-step lab, and a
step-by-step lab is precisely the document that rots: not because its prose ages but because the
things it tells you to download change underneath it.

**And almost nothing the post installs belongs to the project that promised to maintain it.** kind,
Docker, cloud-provider-kind, the Gateway API CRDs and the echo image are all outside the tree.
`cloud-provider-kind` has zero occurrences in `content/en/docs`; so does `echo-basic`. That the
Gateway API itself is an add-on the tree does not ship is [the central finding of the 2021 Gateway
API walk](../2021/02-evolving-kubernetes-networking-with-the-gateway-api.md), which also establishes
that the pin names no Gateway API version anywhere; this exercise takes it as settled. What is new
here is the direction: the 2021 post could not be run because its API never existed in the form it
described, and this one runs perfectly while the documentation can vouch for none of it.

**Three pages at the pin describe kind, and they disagree about what it is for.**
`docs/reference/tools/_index.md:56-58` says kind *"is primarily designed for testing Kubernetes
itself, but may also be used for local development or CI"* — learning is not in that list.
`docs/setup/learning-environment/_index.md:25` says it *"is lightweight and designed specifically
for testing Kubernetes itself, but works great for learning too"* — same premise, opposite
conclusion, and a stronger word for the premise. `docs/tasks/tools/_index.md:36-38` carries no
caveat at all: kind *"lets you run Kubernetes on your local computer"*, full stop. Three
descriptions of one tool, in three sections of the same site, and the reader cannot tell from them
whether the tool the post builds on is meant for the use the post puts it to.

**The two pages that carry a caveat and the page that does not point at each other.**
`docs/tasks/tools/_index.md:14-16` opens with a note sending the reader to the learning-environment
page to set up a practice environment, and `docs/setup/learning-environment/_index.md:17` sends them
back to `/docs/tasks/tools/#kubectl` for the tool. Each page covers kind in its own words on the way
past. The post links the one with no caveat: its prerequisite list at `:32` points at
`kubernetes.io/docs/tasks/tools/`.

**The pin's whole account of where a Gateway's address comes from is one subordinate clause.**
`gateway.md:119-121`: *"Since the `addresses` field is unspecified, an address or hostname is
assigned to the Gateway by the implementation's controller. This address is used as a network
endpoint for processing traffic."* That is the entire mechanism, on a 283-line page, and the
twenty-eight lines of install at `:48-75` of the post exist to supply the one actor in it. A reader
who has only the pin knows that an address arrives and knows nothing about what has to be true for
it to arrive.

**The pin never says what waiting for that address looks like.** `<pending>` occurs six times in
`content/en/docs`, every one of them a Service or an Ingress, and `ingress.md:415-418` is the note
that explains it: *"Ingress controllers and load balancers may take a minute or two to allocate an
IP address. Until that time, you often see the address listed as `<pending>`."* The Gateway page has
no equivalent sentence and no sample output at all. Whether a Gateway with no address yet prints
`<pending>`, an empty column or something else is not recorded anywhere in the tree, and step 5
settles it by looking.

**No Gateway status condition is named anywhere in the pinned documentation.** `Programmed`,
`Accepted`, `ResolvedRefs` and `BackendNotFound` have zero occurrences in `content/en/docs`. The
post's expected output at `:126-129` has a `PROGRAMMED` column and its troubleshooting section at
`:263-315` walks a `BackendNotFound` status with a real `lastTransitionTime`, so the only place on
kubernetes.io where a reader can learn the vocabulary they will need to debug a Gateway is a blog
post — and blog posts, per the policy quoted above, are not maintained unless somebody marks them.
Somebody marked this one. That is not a coincidence; it is the policy working.

**The one object the pin insists on is the one the post never creates.** `gateway.md:69-71`: *"A
Gateway must reference a GatewayClass that contains the name of the controller that implements the
class"*, followed at `:74-81` by a minimal GatewayClass with `controllerName:
example.com/gateway-controller`. The post skips the object entirely, because `:81` says the
controller provisions a GatewayClass called `cloud-provider-kind` on its own. So the reader never
sees a `controllerName` — and the post's troubleshooting sample at `:305` shows the class's real one
is `kind.sigs.k8s.io/gateway-controller`. Two names for one binary, one of them in the manifest the
reader writes and the other visible only in an error, with the object that connects them never
printed.

**A load balancer installs an API as a side effect, and that is how the version gets chosen.** `:52`
is the sentence: the controller installs the CRDs. Nowhere does the post decide which Gateway API
release it wants, because the decision has been delegated to whatever version of cloud-provider-kind
the redirect at `:59` resolved to on the day the reader ran it. The 2021 walk found that the pin
names no Gateway API version; this post reaches the same silence by a different road, and the road
is worse, because the pin at least admits it is pointing off-site.

**One dependency floats and one is frozen, in the same tutorial.** `:59` resolves the controller
version by following `https://github.com/kubernetes-sigs/cloud-provider-kind/releases/latest` and
taking the basename of wherever it lands — a value that is different tomorrow. `:194` pins
`registry.k8s.io/gateway-api/echo-basic:v20251204-v1.4.1` — a value that is never different. In a
document nobody is expected to edit, the floating half will drift out from under the frozen half
without a single commit, and the maintenance promise does not protect against that because there is
nothing to fix until it breaks.

**The controller runs in a place the pin does not describe.** `cloud-controller.md:27-30` says the
cloud controller manager *"runs in the control plane as a replicated set of processes (usually,
these are containers in Pods)"*, and the note at `:33-37` offers a second placement: *"You can also
run the cloud controller manager as a Kubernetes addon rather than as part of the control plane."*
The post uses a third: a Docker container on the host, with `--network host`, outside the cluster
entirely. [The 2023 walk on cloud provider integration
changes](../2023/11-cloud-provider-integration-changes.md) holds the history of that component and
the manifest the tree still ships for running it as a DaemonSet; what this post adds is a deployment
shape the tree has no word for.

**And the way it reaches the cluster is the thing the pin's only other mention of that socket tells
you to hunt down.** `/var/run/docker.sock` appears five times in `content/en/docs`. Four of them are
in `migrating-telemetry-and-security-agents.md:52-68`, which calls it *"the Docker daemon's
privileged socket"* and supplies a script whose purpose is to *"find Pods that have a mount directly
mapping the Docker socket"* so that they can be migrated away from it. The post mounts exactly that
path into a container it asks the reader to run, notes at `:62` that elevated privileges may be
needed, and does not say what the privilege buys. It buys control of every container on the host,
which for a kind cluster means every node.

**The post advises against the setting it uses, one paragraph above using it.** `:91-92` tells the
reader to prefer `Same` or `Selector`; `:117` writes `from: All`. The pin agrees with the advice and
not the manifest: the Gateway example at `gateway.md:114-116` ends with `from: Same`, and the note
at `:127-129` states the rule — *"By default, a Gateway only accepts Routes from the same namespace.
Cross-namespace Routes require configuring `allowedRoutes`."* The post needs `All` because its
HTTPRoute is in `demo` and its Gateway is in `gateway-infra`, so the warning is not wrong and the
manifest is not wrong; the tutorial is simply built on the shape it tells you to avoid, and never
shows the safer one.

**The pin's worked example has no namespaces in it at all.** The HTTPRoute at `gateway.md:140-158`
names no namespace on itself, none on its `parentRefs` entry and none on its `backendRefs` entry;
every reference is implicitly local. Read the page end to end and cross-namespace attachment is one
sentence of prose with no manifest behind it. The post's arrangement — route in one namespace,
Gateway in another — is the common one in a real cluster and the one the documentation never draws.

**The example hostname occurs nowhere else in the repository.** `exampledomain.example` has seven
occurrences in the pinned tree, all seven in this post. The tree's own habits are visible a page
away: `gateway.md:113` and `:148` use `www.example.com`, `ingress.md:409-412` uses the RFC 5737
address `203.0.113.123`, and `service.md:616` uses `192.0.2.127`. Nothing is broken by the choice —
`.example` is reserved for exactly this — but it is the one string in the post that a reader
searching the documentation for a second opinion will find nothing about.

**The error sample is a real capture, and it is dated.** `:298` carries `lastTransitionTime:
"2026-01-19T17:13:35Z"`, nine days before the post's own date of 2026-01-28, alongside a pod name
`echo-dc48d7cf8-vs2df` and a `curl/8.15.0` user agent at `:240-259`. Somebody ran this and pasted
what came out, which is the best thing that can be said about a tutorial's sample output and the
reason the troubleshooting section is worth more than the happy path. Two lines carry trailing
whitespace, `:15` and `:91`, both of them prose.

**The cleanup does four things where two would do.** `:325-326` deletes the `gateway-infra` and
`demo` namespaces; `:336` stops the container; `:345` runs `kind delete cluster`, which removes the
namespaces, the Gateway, the HTTPRoute, the Deployment and the CRDs the controller installed, all at
once. The first two commands are inside the third. Only the container is genuinely outside the
cluster, and `--rm` at `:60` means stopping it is all that is needed. Step 9 measures what each
command actually removes, because the arithmetic of teardown is the part of a lab that a reader
skips and then pays for.

**What this exercise does not cover, and where it lives.** The Gateway API as an argument — why
role-oriented routing replaced Ingress, what each kind is for, which kinds reached stability and
which never appear in the tree — belongs to [the 2021 Gateway API
walk](../2021/02-evolving-kubernetes-networking-with-the-gateway-api.md), and the frozen state of
the API it replaced belongs to [the 2020 Ingress
walk](../2020/02-improvements-to-the-ingress-api-in-kubernetes-1-18.md). The cloud controller
manager's own history — the in-tree providers, the migration guide, the beta stamp it has carried
since v1.11 — belongs to [the 2023 cloud provider integration
walk](../2023/11-cloud-provider-integration-changes.md). The complementary case of the frontmatter
key, a post whose author set `evergreen: false` with a comment naming the reason, is read in [the
2019 runc walk](../2019/02-runc-cve-2019-5736.md). Converting existing Ingress objects into Gateway
objects is a 2026 subject with a walk of its own later in this year. This exercise is the lab and
the promise: what the tutorial needs, where the pin can and cannot vouch for it, and what the
project signed up for when it marked the file maintained.

**The diff, and why** — three of the seven cases, and the one that usually dominates is absent.

Nothing here broke. There is no renamed field, no removed group, no flag that stopped being
accepted. Run the post today on a machine with Docker and it does what it says, which puts this file
in a small minority of the archive and makes the other three cases carry the whole weight.

**What is still right** is the post, in full, and the interesting question is why. It is right
because it depends on almost nothing that the Kubernetes release cycle can move. kind, Docker and
cloud-provider-kind version independently of Kubernetes; the four Gateway API kinds it touches were
stable before it was written; and the one Kubernetes-versioned thing in the lab, the cluster kind
creates, is whatever kind's default happens to be, which the post never pins and therefore never
gets wrong. A tutorial that names no version cannot be dated by one. That is a real property and not
a trick, and it is worth naming because most of this archive's survivors survive by accident.

**Never absorbed** is the case attached to everything the lab actually teaches. How a Gateway gets
an address, what it looks like while it is waiting, which status conditions to read and what
`BackendNotFound` means, how a route in one namespace attaches to a Gateway in another, what a
GatewayClass's `controllerName` is for when nobody typed it: none of this is in `content/en/docs`.
The pin has one clause on the address, one note on namespaces, one minimal GatewayClass and no
status vocabulary at all. The knowledge exists on kubernetes.io only because this post is on
kubernetes.io, and it stays there only because somebody marked it evergreen. The 2021 walk found the
pin recommending an API it does not ship; five years later the pin still does not explain how to
watch one work, and a blog post is doing the job.

**Overtaken by stasis** is the case attached to the three pages about kind. They did not break and
they were not wrong when written; they simply never got reconciled with each other, and the drift
shows up as a reader who cannot find out whether the tool this whole post rests on is meant for
learning. Two of the three say kind is primarily for testing Kubernetes itself and then disagree
about how much of an exception learning is; the third makes no claim. The post links the third.

There is a fourth thing the cases do not have a name for, and it is the reason this file exists. The
post is a promise. `evergreen: true` says the project will keep it true, and the project can keep
true only the parts it controls, which here are the four Gateway API kinds and nothing else. Every
other moving part — a redirect that resolves to a new version each release, a Docker socket whose
privileges are not explained, a controller with three jobs and two names — sits outside the promise
and inside the tutorial. That is not a diff between the post and the pin. It is a diff between what
a mark in the frontmatter means and what it can reach.

**Topology** — [`nested`](../../strands/lab-topologies.md#nested), fresh: one node at
`10.10.10.190`, 6144MB, 4 cores, 40G. This is the only exercise in the walk so far that wants this
topology, and it wants it for the reason the topology exists: the cluster under test is a cluster
inside a container inside a VM, and the host it runs on has to be disposable. Bring the guest up
with [the provisioning recipe](../../strands/lab-topologies.md#provision). Do not take it through
the kubeadm baseline — there is no kubeadm here, and [the Kubernetes install belongs to the
learner](../../strands/lab-topologies.md#node-baseline) in this case too: step 1 puts a container
runtime, kind and kubectl on the guest and kind supplies the cluster. Every command after step 1
runs on that guest, so open one session with `ssh zain@10.10.10.190` at the end of step 1 and stay
in it; the fences below are written as though you are already there. Nothing in this exercise should
ever be run on the Mac or on hopper.

**Do**

1. Put a runtime, kind and kubectl on the guest, then make a cluster and record what it has before
   anything Gateway-shaped exists. All three downloads follow a redirect to whatever is newest,
   which is the post's own idiom at `:59` and is why step 10 writes down what the redirects resolved
   to today.

   ```sh
   ssh zain@10.10.10.190 "curl -fsSL https://get.docker.com | sudo sh \
     && sudo usermod -aG docker zain \
     && sudo curl -fsSLo /usr/local/bin/kind \
          https://github.com/kubernetes-sigs/kind/releases/latest/download/kind-linux-amd64 \
     && sudo curl -fsSLo /usr/local/bin/kubectl \
          https://dl.k8s.io/release/\$(curl -fsSL https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl \
     && sudo chmod +x /usr/local/bin/kind /usr/local/bin/kubectl"
   ssh zain@10.10.10.190
   ```

   From here on you are on the guest.

   ```sh
   mkdir -p /tmp/bw-gateway && cd /tmp/bw-gateway
   kind create cluster
   kubectl version
   kubectl get crd --no-headers | wc -l
   kubectl api-resources --api-group=gateway.networking.k8s.io
   kubectl get nodes -o wide
   ```

2. Submit the post's Gateway before its controller exists. The post says at `:52` that the CRDs
   arrive with cloud-provider-kind; this is the command that makes that claim falsifiable, and it is
   also the only moment in the lab where the cluster is a plain Kubernetes cluster.

   ```sh
   cat > /tmp/bw-gateway/gateway.yaml <<'EOF'
   ---
   apiVersion: v1
   kind: Namespace
   metadata:
     name: gateway-infra
   ---
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: gateway
     namespace: gateway-infra
   spec:
     gatewayClassName: cloud-provider-kind
     listeners:
     - name: default
       hostname: "*.exampledomain.example"
       port: 80
       protocol: HTTP
       allowedRoutes:
         namespaces:
           from: All
   EOF
   kubectl apply -f /tmp/bw-gateway/gateway.yaml
   kubectl get namespace gateway-infra
   ```

3. Install cloud-provider-kind exactly as the post writes it, then look at what you just ran. Record
   the version the redirect produced, what the container was given, and how many CRDs appeared.

   ```sh
   VERSION="$(basename $(curl -s -L -o /dev/null -w '%{url_effective}' \
     https://github.com/kubernetes-sigs/cloud-provider-kind/releases/latest))"
   echo "resolved: $VERSION"
   docker run -d --name cloud-provider-kind --rm --network host \
     -v /var/run/docker.sock:/var/run/docker.sock \
     registry.k8s.io/cloud-provider-kind/cloud-controller-manager:${VERSION}
   docker inspect cloud-provider-kind \
     --format 'net={{.HostConfig.NetworkMode}} binds={{.HostConfig.Binds}} privileged={{.HostConfig.Privileged}}'
   sleep 20
   kubectl get crd --no-headers | wc -l
   kubectl get crd --no-headers | grep gateway.networking.k8s.io
   kubectl api-resources --api-group=gateway.networking.k8s.io
   ```

4. Read the object nobody created. The post names the GatewayClass at `:81` and never shows it; the
   pin insists at `gateway.md:69-71` that the class is what names the controller, and prints a
   minimal one at `:74-81`. Print the real one and compare the `controllerName` with the value that
   appears in the post's troubleshooting sample at `:305`.

   ```sh
   kubectl get gatewayclass
   kubectl get gatewayclass cloud-provider-kind -o jsonpath='{.spec.controllerName}{"\n"}'
   kubectl get gatewayclass cloud-provider-kind \
     -o jsonpath='{range .status.conditions[*]}{.type}={.status}({.reason}) {end}{"\n"}'
   kubectl get crd gateways.gateway.networking.k8s.io \
     -o jsonpath='{range .spec.versions[*]}{.name}={.served} {end}{"\n"}'
   kubectl get crd gateways.gateway.networking.k8s.io \
     -o jsonpath='{.metadata.annotations}{"\n"}'
   ```

5. Re-submit the Gateway and watch the address arrive. The first `get` is the one the pin has no
   sentence for: `ingress.md:415-418` promises `<pending>` for an Ingress, and nothing in the tree
   says what a Gateway prints while it waits. Capture it before the poll overwrites the answer.

   ```sh
   kubectl apply -f /tmp/bw-gateway/gateway.yaml
   kubectl get gateway -n gateway-infra gateway
   kubectl get gateway -n gateway-infra gateway -o jsonpath='{.status.addresses}{"\n"}'
   for i in $(seq 1 20); do
     A=$(kubectl get gateway -n gateway-infra gateway -o jsonpath='{.status.addresses[0].value}')
     if [ -n "$A" ]; then echo "address $A after $((i*3))s"; break; fi
     sleep 3
   done
   kubectl get gateway -n gateway-infra gateway \
     -o jsonpath='{range .status.conditions[*]}{.type}={.status}({.reason}) {end}{"\n"}'
   kubectl get gateway -n gateway-infra gateway
   ```

6. Find out where that address came from. The pin's one clause says the implementation's controller
   assigns it and stops; `service.md:622-625` describes how the same controller does the job for a
   Service. Check whether a Service was involved at all, and whether the address is on the bridge
   the nodes are on.

   ```sh
   kubectl get svc -A
   docker ps --format '{{.Names}}  {{.Image}}'
   docker network inspect kind --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}'
   docker inspect kind-control-plane \
     --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
   docker logs cloud-provider-kind --tail 30
   ```

7. Run the post's happy path, then push on the listener. The first `curl` is the post's; the second
   asks for a hostname that matches the listener's wildcard but no route; the third asks for the
   bare address with no hostname at all. Three answers, one listener.

   ```sh
   cat > /tmp/bw-gateway/echo.yaml <<'EOF'
   ---
   apiVersion: v1
   kind: Namespace
   metadata:
     name: demo
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: echo
     namespace: demo
     labels:
       app.kubernetes.io/name: echo
   spec:
     selector:
       app.kubernetes.io/name: echo
     ports:
     - name: http
       port: 3000
       protocol: TCP
       targetPort: 3000
   ---
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: echo
     namespace: demo
   spec:
     replicas: 1
     selector:
       matchLabels:
         app.kubernetes.io/name: echo
     template:
       metadata:
         labels:
           app.kubernetes.io/name: echo
       spec:
         containers:
         - name: echo
           image: registry.k8s.io/gateway-api/echo-basic:v20251204-v1.4.1
           ports:
           - containerPort: 3000
   ---
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: echo
     namespace: demo
   spec:
     parentRefs:
     - name: gateway
       namespace: gateway-infra
     hostnames: ["some.exampledomain.example"]
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /
       backendRefs:
       - name: echo
         port: 3000
   EOF
   kubectl apply -f /tmp/bw-gateway/echo.yaml
   kubectl -n demo rollout status deploy/echo --timeout=180s
   kubectl -n demo get httproute echo -o jsonpath='{range .status.parents[*]}{.controllerName}{" "}{range .conditions[*]}{.type}={.status}({.reason}) {end}{end}{"\n"}'
   GW=$(kubectl get gateway -n gateway-infra gateway -o jsonpath='{.status.addresses[0].value}')
   curl -s --resolve some.exampledomain.example:80:$GW http://some.exampledomain.example | head -12
   curl -s -o /dev/null -w 'other: %{http_code}\n' --resolve other.exampledomain.example:80:$GW http://other.exampledomain.example
   curl -s -o /dev/null -w 'bare:  %{http_code}\n' http://$GW/
   ```

8. Take the advice the post gives at `:91-92` and see what it costs. Flip the listener from `All` to
   `Same` — the value the pin's own example uses at `gateway.md:116` — and read the route's status,
   then flip it back. Then move the backend across a namespace boundary, which is the case the pin
   never draws, and read the status again.

   ```sh
   kubectl -n gateway-infra patch gateway gateway --type=json \
     -p='[{"op":"replace","path":"/spec/listeners/0/allowedRoutes/namespaces/from","value":"Same"}]'
   sleep 15
   kubectl -n demo get httproute echo -o jsonpath='{range .status.parents[*]}{range .conditions[*]}{.type}={.status}({.reason}) {end}{end}{"\n"}'
   curl -s -o /dev/null -w 'same: %{http_code}\n' --resolve some.exampledomain.example:80:$GW http://some.exampledomain.example
   kubectl -n gateway-infra patch gateway gateway --type=json \
     -p='[{"op":"replace","path":"/spec/listeners/0/allowedRoutes/namespaces/from","value":"All"}]'
   sleep 15
   kubectl create namespace backends
   kubectl -n backends create service clusterip echo --tcp=3000:3000
   kubectl -n demo patch httproute echo --type=json \
     -p='[{"op":"add","path":"/spec/rules/0/backendRefs/0/namespace","value":"backends"}]'
   sleep 15
   kubectl -n demo get httproute echo -o jsonpath='{range .status.parents[*]}{range .conditions[*]}{.type}={.status}({.reason}) {end}{end}{"\n"}'
   curl -s -o /dev/null -w 'xns:  %{http_code}\n' --resolve some.exampledomain.example:80:$GW http://some.exampledomain.example
   ```

9. Do the post's cleanup in its own order and count what each command removes. The first two are
   inside the fourth; the third is the only one that touches anything outside the cluster.

   ```sh
   kubectl delete namespace gateway-infra demo
   kubectl get crd --no-headers | grep -c gateway.networking.k8s.io
   kubectl get gatewayclass
   kubectl get namespace backends
   docker stop cloud-provider-kind
   docker ps -a --format '{{.Names}}' | sort
   kind delete cluster
   docker ps -a --format '{{.Names}}' | sort
   docker network ls --format '{{.Name}}' | sort
   docker images --format '{{.Repository}}:{{.Tag}}' | sort
   ```

10. Offline, against the pinned tree, on the Mac. This is the census the prose above rests on, and
    running it is the only way to own the numbers rather than believe them.

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -rl '^evergreen: true' blog/_posts | wc -l
    for f in $(grep -rl '^evergreen: true' blog/_posts); do
      printf '%s\t%s\n' "$(grep -c '^[`][`][`]\(bash\|shell\|sh\|console\|shell-session\)' "$f")" "${f#blog/_posts/}"
    done | sort -rn | head -5
    grep -rn 'cloud-provider-kind\|echo-basic\|exampledomain' docs --include='*.md' | wc -l
    grep -rn 'Programmed\|ResolvedRefs\|BackendNotFound' docs --include='*.md' | wc -l
    grep -rn '<pending>' docs --include='*.md'
    grep -rn 'docker\.sock' docs --include='*.md'
    sed -n '56,58p' docs/reference/tools/_index.md
    sed -n '25p'    docs/setup/learning-environment/_index.md
    sed -n '36,38p' docs/tasks/tools/_index.md
    sed -n '14,16p' docs/tasks/tools/_index.md
    sed -n '17p'    docs/setup/learning-environment/_index.md
    sed -n '38,41p;53,58p' docs/contribute/blog/_index.md
    sed -n '69,81p;114,121p;127,129p;140,158p' docs/concepts/services-networking/gateway.md
    sed -n '415,418p' docs/concepts/services-networking/ingress.md
    sed -n '27,37p' docs/concepts/architecture/cloud-controller.md
    ```

**Expect**

Step 1 gives you a one-node cluster whose Kubernetes version you did not choose and the post never
named. Write it down: it is whatever kind's newest release defaults to, and it is the only
Kubernetes version anywhere in this lab. The CRD count is small and fixed — a plain kind cluster
ships a handful and none of them is `gateway.networking.k8s.io`. The `api-resources` call against
that group prints nothing and exits non-zero, which is the baseline the next step is measured
against. Note also that three separate redirects decided three versions for you before you typed a
single Kubernetes command.

Step 2 splits. The Namespace is created; the Gateway is refused with `no matches for kind "Gateway"
in version "gateway.networking.k8s.io/v1"`, and because `kubectl apply` processes a multi-document
manifest item by item, you are left with half the file applied. That is the honest kind of failure —
the command errors and says why — and it confirms `:52`: the API is not in the cluster and nothing
in Kubernetes put it there. Keep the half-applied namespace; step 5 re-runs the same file.

Step 3 is where the lab's assumptions become visible. The `echo` prints a version string that will
be different for the next reader, and the `docker inspect` line prints `net=host`, a bind of
`/var/run/docker.sock:/var/run/docker.sock`, and `privileged=false`. Read that trio together: the
container is not privileged in Docker's sense and does not need to be, because the socket gives it
the ability to create containers of its own choosing on this host. The CRD count jumps, and the
names that appear are the Gateway API set — `gatewayclasses`, `gateways`, `httproutes`,
`grpcroutes`, `referencegrants` and more, depending on the channel the controller vendored. Count
them. Nothing in the pinned documentation told you which set to expect, because nothing in the
pinned documentation knows this controller exists.

Step 4 answers the question the post leaves hanging. The class is there, named
`cloud-provider-kind`, created by something that is not you, and its `controllerName` is
`kind.sigs.k8s.io/gateway-controller` — a different string from the class name, and the string the
post only ever shows inside an error at `:305`. Its `Accepted` condition should be `True`. The CRD
version list tells you which Gateway API release the controller shipped, which is the closest this
lab ever comes to a version decision, and it was made for you in step 3.

Step 5 settles the `<pending>` question. The first `get`, run within a second of the apply, prints
the row with an empty `ADDRESS` column and `PROGRAMMED` reading `Unknown` or `False` — not
`<pending>`, which is a `kubectl` convention for Services and Ingresses and not for Gateways. The
jsonpath on `.status.addresses` prints nothing at all, because the field is absent rather than
empty. Then the poll: the address arrives, typically within the first few iterations, and it is a
`172.18.x.x` address. The conditions line ends with `Accepted=True` and `Programmed=True`. Whatever
number of seconds you recorded, notice that the pin gave you no way to know whether to keep waiting
or start debugging.

Step 6 tells you what the one clause at `gateway.md:119-121` was standing in for. No Service of type
LoadBalancer exists for the Gateway — the implementation did not route through the Service API at
all — and yet the address is on the `kind` bridge subnet that `docker network inspect` prints, the
same subnet the control-plane container is on. `docker ps` shows a second container that you did not
start, created by cloud-provider-kind through the socket, which is what the socket was for. The logs
name the Gateway and the address they gave it. The pin's account of a cloud controller acting
through `service.md:622-625` describes a different mechanism from the one you are looking at, and
neither the Gateway page nor the Service page describes this one.

Step 7 gives three different answers to three requests down one listener. The post's `curl` returns
the echo server's JSON, with `"host": "some.exampledomain.example"` in it. The request for
`other.exampledomain.example` matches the listener's wildcard hostname but no HTTPRoute, so the
Gateway answers `404` itself — the listener is doing the matching, not the route. The bare-address
request sends no matching `Host` header, so it too is refused; the `curl --resolve` dance in the
post is not decoration, it is the only way to reach this Gateway. The route's status prints
`Accepted=True` and `ResolvedRefs=True` next to the controller name from step 4.

Step 8 is the price of the advice. With the listener set to `Same`, the route's `Accepted` condition
flips to `False` with a reason naming the namespace policy, and the `curl` returns `404` — the
post's lab stops working the moment you follow the post's own recommendation, because the tutorial's
layout puts the route and the Gateway in different namespaces. That is the finding to sit with:
`:91-92` and `:117` are not reconcilable in this arrangement, and the pin's example at
`gateway.md:114-116` avoids the problem by putting everything in one namespace and never mentioning
the other case. After the flip back, the cross-namespace backend gives you the second half:
`ResolvedRefs` goes `False` with a reason about the reference not being permitted, and the `curl`
returns `500`. A ReferenceGrant in `backends` is what would allow it; the Gateway page never names
that kind.

Step 9 is arithmetic. Deleting the two namespaces removes the Gateway, the HTTPRoute, the Service
and the Deployment, and leaves the CRD count unchanged, the GatewayClass present, and the `backends`
namespace present — the post's cleanup does not know about anything you added. `docker stop` removes
the controller container, and `--rm` means it is gone from `docker ps -a` without a second command.
`kind delete cluster` then removes the node container and everything that was ever in the cluster,
including the CRDs the first two commands could not touch. What survives is the `kind` Docker
network and every image that was pulled, which is several gigabytes and which no command in the post
removes. The teardown below does.

Step 10 is the census. Forty-four posts carry `evergreen: true`; this one tops the shell-fence
ranking at twelve with the next at ten and the rest at two or zero. `cloud-provider-kind`,
`echo-basic` and `exampledomain` together have zero occurrences under `docs`. The three Gateway
condition names have zero. `<pending>` has six, every one a Service or an Ingress. `docker.sock` has
five, four of them in a migration page teaching you to find and remove such mounts. Then read the
three descriptions of kind one after another and decide for yourself what the pinned documentation
thinks the tool is for; that question has no answer in the tree, which is the point.

**Read on**

11. [Evolving Kubernetes networking with the Gateway
    API](../2021/02-evolving-kubernetes-networking-with-the-gateway-api.md) — the argument this lab
    is downstream of, and the exercise that establishes the pin ships no Gateway API and names no
    version of it.

12. [Improvements to the Ingress API in Kubernetes
    1.18](../2020/02-improvements-to-the-ingress-api-in-kubernetes-1-18.md) — the API the Gateway
    replaced, now frozen in the tree, and the last one whose address allocation the pin documents.

13. [Cloud provider integration changes](../2023/11-cloud-provider-integration-changes.md) — where a
    cloud controller manager is supposed to run, what the tree still ships for running one, and why
    it has called itself beta since v1.11.

14. [Runc and CVE-2019-5736](../2019/02-runc-cve-2019-5736.md) — the same frontmatter key with the
    opposite value, set by an author who wrote down in the file which of their own claims had
    stopped being true.

15. *Unanswerable from the pin.* Who is on the hook for an evergreen tutorial whose every dependency
    is out of tree, and what happens to the promise when the redirect at `:59` resolves to a release
    that changes the CRD channel? The policy at `docs/contribute/blog/_index.md:53-58` says the
    project commits to maintaining the article; it does not say who notices, how, or how often.
    Nothing in the pinned tree records a review cadence, an owner, or a test that runs this
    tutorial. The archive's answer, as far as it goes, is this walk.

**Teardown**

```sh
ssh zain@10.10.10.190 "docker stop cloud-provider-kind 2>/dev/null || true; \
  kind delete cluster 2>/dev/null || true; \
  docker network rm kind 2>/dev/null || true; \
  docker system prune -af --volumes; \
  rm -rf /tmp/bw-gateway"
```

Then destroy the guest with [the teardown recipe](../../strands/lab-topologies.md#teardown). The
`docker system prune` is the line the post has no equivalent for, and on a 40G disk after two runs
of this lab it is the difference between a guest that boots and one that does not.
