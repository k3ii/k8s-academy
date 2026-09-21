<a id="kubernetes-v1-36-deprecation-and-removal-of-service-externalips"></a>

# The reference that omits the field's deprecation marks the field beside it deprecated, the warning the post promises never fires on a v1.35 node, the guard it tells you to enable is off by default and its own reference reads as saying to disable it, and one CVE resolves four ways

**Post** — [Kubernetes v1.36: Deprecation and removal of Service
ExternalIPs](https://kubernetes.io/blog/2026/05/14/kubernetes-v1-36-deprecation-and-removal-of-service-externalips/),
2026-05-14.

230 lines, 8,638 bytes, two authors — Adrian Moisey (independent) and Dan Winship (Red Hat) — five
fenced blocks, no tables and no figures. The thirty-ninth of 2026's fifty-nine published rows and
the seventh `walk` among them. It is a deprecation announcement, so it makes no claim a running
cluster can be pointed at to confirm; what it claims instead is that a field is now dangerous, that
two pages agree it should go, and that three named things replace it. The census took the row
because two pages of the same pinned site give opposite advice about a field the lab's own cluster
still accepts in silence.

**As written**

The opening at `:11-33` is the case for the deprecation. `.spec.externalIPs` was *an early attempt
to provide cloud-load-balancer-like functionality for non-cloud clusters*, but the API *assumes that
every user in the cluster is fully trusted*, and where that does not hold it *enables various
security exploits*, linked at `:16` to CVE-2020-8554. `:18-22` records that since Kubernetes 1.21
the project has recommended disabling the field and shipped an admission controller,
`DenyServiceExternalIPs`, to do it, but judged blocking it by default too large a break at the time.
`:29-33` makes the deprecation formal in 1.36 and says a future minor release will drop the
behaviour from `kube-proxy` and change the conformance criteria to require that conforming
implementations *do not* support it.

`:35-54` is a note on terminology. The phrase *external IP* is overloaded: the Service field
`.spec.externalIPs` at `:39-40`, the Node status type `ExternalIP` at `:42-43`, and the
`EXTERNAL-IP` column `kubectl` prints for a LoadBalancer Service at `:45-47`. Only the first is
being deprecated, and `:49-51` tells a reader who sets the field nowhere that it does not apply to
them. `:53-54` adds that as a precaution you *may still want to enable* the `DenyServiceExternalIPs`
admission controller to block future use.

`:56-77` opens the Alternatives with the Service the rest of the section replaces — a `type:
ClusterIP` Service carrying `externalIPs: ["192.0.2.4"]`.

`:79-116` is the first alternative, *manually-managed LoadBalancer Services*, which `:81` calls *the
easiest (but also worst) option*. It is `externalIPs` with one difference stated at `:84-86`: the IP
lives in the Service's `.status`, not its `.spec`, and *in a cluster with RBAC enabled, it can't be
edited by ordinary users by default*. The recipe at `:93-116` is two steps because `.status` cannot
be set at creation: apply a `type: LoadBalancer` Service with a `loadBalancerClass:
non-existent-class` to keep real controllers off it, then `kubectl patch service …
--subresource=status` to write the ingress IP.

`:118-169` is the second alternative, a non-cloud load balancer controller, with MetalLB as the
example: an `IPAddressPool` at `:132-143` names the ranges the controller may assign, and `:145-149`
notes MetalLB honours the deprecated `loadBalancerIP` field so a user can still request a specific
address. `:171-221` is the third, the Gateway API: a `Gateway` takes an IP through its
`.spec.addresses` field at `:176-177`, RBAC can restrict who manages Gateways, and the three-object
example at `:182-217` wires a `Gateway`, an `HTTPRoute` and a `Service` together. `:219` calls
Gateway API *the next generation of Kubernetes Ingress, Load Balancing, and Service Mesh APIs*.

`:223-230` is the timeline. With 1.36 the field is deprecated and `:228` says Kubernetes *now emits
warnings when a user uses this field*; about a year later, v1.40 at the earliest, support is
*disabled in kube-proxy, but users will have a way to opt back in*; about another year later, v1.43
at the earliest, support is removed *completely* with no way to opt back in.

**As it runs now**

**The cluster's own schema carries the omission the release announcement is about — and marks the
field printed next to it deprecated.** `kubectl explain service.spec.externalIPs` prints the field's
description with no deprecation line, because the description is generated from the same Go source
comment the API reference renders, and that comment was never annotated. Run the same command
against `service.spec.loadBalancerIP` and the OpenAPI does carry *Deprecated: This field was
under-specified…*, exactly as `docs/reference/kubernetes-api/core/service-v1.md:117` prints it. So
the generator and the schema both know how to say a Service field is deprecated; for `externalIPs`,
the release the post announces did not add the words anywhere the machine can read them.

**Two pages of the pinned site, from the same commit, give opposite readings of the field.**
`docs/concepts/services-networking/service.md:1051` opens the External IPs section with `{{<
feature-state for_k8s_version="v1.36" state="deprecated" >}}` and `:1053` tells *all users* to
*begin migrating away*. The generated reference at `service-v1.md:84-85` describes `externalIPs` in
four neutral sentences with no deprecation notice at all. Both are current, both are served, and
this is the disagreement the census row is named for. It is not the archive's usual stale-link or
moved-page finding: neither page is wrong about anything, they simply say different things about
whether you should still use the field.

**The guard the post tells you to enable is off by default, and its own reference reads as telling
you to turn it off.** `DenyServiceExternalIPs` is not in the default-enabled list that
`admission-controllers.md:119-130` prints — [the 2021 Pod Security Admission
row](../2021/09-pod-security-admission-beta.md) owns that list — so a stock cluster does not block
the field. Worse, the controller's own section at `admission-controllers.md:247-256` says *This
feature is very powerful (allows network traffic interception)* and *Most users do not need this
feature at all, and cluster admins should consider disabling it*. The subject of *this feature* and
*disabling it* is meant to be `externalIPs`, but the two sentences sit inside the
`DenyServiceExternalIPs` heading with no other noun between them, so read in place they advise
disabling the very mitigation the deprecation blog and the terminology note both tell you to enable.

**One CVE, four addresses across the pinned tree, and one of them is malformed.** The post links
CVE-2020-8554 to `cvedetails.com`; the v1.36 release announcement at
`blog/_posts/2026/kubernetes-v1-36-release/index.md:572` and `security-checklist.md:96` and `:374`
link the GitHub issue `kubernetes/kubernetes/issues/97076`; the *reconciling unfixed CVEs* post of
the same year links `cve.org`; and the v1.36 sneak-peek at `kubernetes-v1-36-sneak-peak.md:53` links
`issues/970760` — the issue number one digit longer than the one the other three GitHub references
use. A reader cannot tell from the pin whether that link 404s, but the string is checkable against
its three siblings, and it does not match.

**The field is still fully live, and no feature gate governs it.** The feature-gate directory holds
no file that turns `externalIPs` on or off — the only externalIP-shaped name in it,
`ExternalPolicyForExternalIP.md`, was a bug fix, stable from 1.18 and removed at 1.22. The
deprecation is a warning emitted by the API server and a note in the docs, not a gate a cluster
operator can flip, which is why there is no ladder in this exercise. On the lab's v1.35 node the
field is accepted with no warning of any kind, because the warning was added at 1.36 and the labs
track the newest published exam version, which is v1.35.

**A `type: ClusterIP` Service becomes reachable from off the cluster, which is the whole point and
the whole danger.** The post's example Service at `:62-77` is `type: ClusterIP`, yet listing
`externalIPs` makes every node accept traffic for that IP and port and route it to the Service's
endpoints; `service.md:1057-1061` states the mechanism and `:1086` states the catch — *Kubernetes
does not manage allocation of `externalIPs`*, so nothing stops two Services, in two namespaces owned
by two users, from claiming the same address. That is CVE-2020-8554 in one sentence, and step 4
builds it.

**The replacement the post calls easiest keeps the IP out of `.spec` on purpose, and the pin's RBAC
backs that up.** The manual-LoadBalancer recipe writes the address to `.status` through the `status`
subresource, and a Role that grants `patch` on `services` does not grant `patch` on
`services/status` — they are distinct resources to RBAC. So the security difference the post asserts
at `:84-86` is real and checkable: an ordinary user who can edit a Service still cannot set its
external address, where `externalIPs` let them write any address into a field they already control.

**The `loadBalancerClass` the recipe leans on to keep controllers away is itself a settled feature,
not a trick.** `loadBalancerClass: non-existent-class` is doing real work — `service.md:693-710`
records the field stable since v1.24, and a default load balancer implementation is required to
ignore a Service whose class it does not recognise. So the recipe's *prevent any real load balancer
controllers from managing this service* comment is not a hack around the API; it is the API behaving
as specified, and on the bare lab node, where there is no load balancer controller at all, the
Service would sit `<pending>` even without the class.

**The Gateway alternative needs an implementation the pin does not ship and the lab does not
install.** [The 2026 Gateway-API-with-kind row](02-experimenting-gateway-api-with-kind.md) already
found that the pinned tree installs none of the Gateway API, that a Gateway takes its address in the
one clause `.spec.addresses`, and that nothing in the pin renders a running Gateway. The
three-object block at `:182-217` will apply — the CRDs, once installed, accept it — but with no
controller watching, the `Gateway` never gets a programmed address or an `Accepted` condition, so
the alternative the post presents as equivalent is the one that does the least on a cluster stood up
from nothing.

**The removal has a named re-enable lever for its twin and none for itself.** `:229` promises that
when kube-proxy drops the behaviour at v1.40 *users will have a way to opt back in*, without naming
it. The identical timeline sits one deprecation over: `virtual-ips.md:208-215` deprecates the `ipvs`
proxy mode at v1.35, disables it by default at v1.40 *with the `KubeProxyIPVS` feature gate*, and
removes it at v1.43. Same three releases, same shape — but the IPVS notice names the gate that
brings it back and the externalIPs notice names nothing, and no gate file in the directory reserves
one.

**The precise thing being removed is narrower than the post's title.** *Deprecation and removal of
Service ExternalIPs* names the whole idea, but `:29-33` and the timeline remove only kube-proxy's
*implementation* of the field, and the terminology note at `:35-54` is careful that the Node
`ExternalIP` address type and the `EXTERNAL-IP` column are untouched. The API field itself is not
scheduled for removal from the Service schema in anything the pin states; what goes away is the
routing kube-proxy does for it. A cluster at v1.43 will, on the pin's own account, still let you set
`.spec.externalIPs` — it just will not do anything.

**What this exercise does not cover, and where it lives.** How kube-proxy turns a Service IP into
rules that answer on a node — the proxy modes and the backends that program them — is [the 2025
nftables kube-proxy row](../2025/01-nftables-kube-proxy.md), and this exercise reads the routing as
given rather than tracing it. The admission controller mechanism and the default-enabled plugin list
belong to [the 2021 Pod Security Admission row](../2021/09-pod-security-admission-beta.md); step 5
enables one plugin and does not re-derive how admission works. The `Warning` header the timeline
points at — how a server raises one and a client shows it — is [the 2020 warnings
row](../2020/07-warnings.md). LoadBalancer, NodePort and MetalLB as ways to expose a Deployment are
[the four-ways-to-expose lab](../../labs/01/14-four-ways-to-expose.md), which installs the only
MetalLB in the curriculum; this exercise points at that alternative and does not stand it up. And
the Gateway API's own shape is [the 2026 Gateway-API-with-kind
row](02-experimenting-gateway-api-with-kind.md).

**The diff, and why** — four cases, and the one that decides the exercise is a disagreement neither
page knows it is having.

**Still right.** Everything the post asserts about the danger and the alternatives holds at the pin.
The field really does let any Service claim any IP with no allocation control; the
`DenyServiceExternalIPs` controller really does block net-new use while leaving existing Services
alone, exactly as `admission-controllers.md:247-252` describes; the manual-LoadBalancer recipe works
step for step and the address really does land in `.status`; and the `loadBalancerClass` and Gateway
`.spec.addresses` fields are where the post says they are. The security argument is sound and the
migrations are real.

**Wrong when it was published — or at least undermined by the tree it shipped into.** The post tells
all users the field is deprecated and points at a release that emits warnings, but the generated API
reference the same release ships carries no deprecation on the field, and the cluster's own OpenAPI
— what `kubectl explain` reads — carries none either. The announcement and the machine-readable
schema disagree from the day of publication, and the schema is the one a tool believes.

**Overtaken by stasis.** The deprecation has not propagated. Nine months of releases in the pin's
own history reach v1.37, and the Go source comment for the field still has no deprecation line, the
reference still reads neutral, and the admission controller that would enforce the advice is still
off by default with a section that reads as arguing against itself. The concept page moved; nothing
downstream of it did.

**Never absorbed.** The one thing the post supplies that exists nowhere else is the
manual-LoadBalancer-with-`non-existent-class` recipe: the string `non-existent-class` appears in the
pinned tree only in this post, and no documentation page teaches the two-step `.status` patch as a
replacement for `externalIPs`. The migration the announcement is built around lives, at the pin, in
the announcement alone.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180`, 4096MB, 4
CPUs, 25G, [provisioned](../../strands/lab-topologies.md#provision) and
[baselined](../../strands/lab-topologies.md#node-baseline-steps) as usual, running Kubernetes v1.35.
One node is the honest choice: `externalIPs` routing is a per-node kube-proxy behaviour, and on a
single-node cluster the node's own address is the only external IP that already routes to it, so the
exercise can make the field answer without touching the network beyond the node. Everything created
lives in a namespace called `bw-extip`, plus a second namespace `bw-extip-attacker` that step 4 uses
and *Teardown* deletes, and one edit to the API server's static Pod manifest that step 5 makes and
*Teardown* reverts. Steps 1 to 7 run on the node over `ssh zain@10.10.10.180`; step 8 runs offline
against a checkout of `kubernetes/website` at the pin, with `W` set to its `content/en` directory.

**Do**

1. Fix the release, confirm nothing gates the field, and stand up the post's own Service. Open one
   session with `ssh zain@10.10.10.180` and stay in it. The last command applies the example from
   `:62-77` unchanged except for the address, which is set to a spare IP on the node's subnet so
   later steps can make it answer.

   ```sh
   kubectl version -o json | grep gitVersion
   kubectl get --raw /metrics | grep -i 'externalip' || echo "no externalIP metric or gate"
   kube-apiserver -h 2>/dev/null | grep enable-admission-plugins | grep -o 'DenyServiceExternalIPs' \
     || echo "DenyServiceExternalIPs not in the default plugin list"
   kubectl create namespace bw-extip
   kubectl -n bw-extip create deployment web \
     --image=registry.k8s.io/e2e-test-images/agnhost:2.53 -- /agnhost netexec --http-port=8080
   kubectl -n bw-extip rollout status deployment/web --timeout=120s
   cat <<'EOF' | kubectl -n bw-extip apply -f -
   apiVersion: v1
   kind: Service
   metadata:
     name: my-service
   spec:
     type: ClusterIP
     selector:
       app: web
     ports:
       - name: http
         protocol: TCP
         port: 80
         targetPort: 8080
     externalIPs:
       - 10.10.10.199
   EOF
   kubectl -n bw-extip get service my-service
   ```

2. Ask the cluster's own schema what it thinks of the field, and of the field beside it. `kubectl
   explain` prints from the same OpenAPI the API reference is generated from, so this is the
   two-page disagreement made live.

   ```sh
   kubectl explain service.spec.externalIPs | sed -n '1,12p'
   echo "--- and the neighbour ---"
   kubectl explain service.spec.loadBalancerIP | grep -i deprecat || echo "no deprecation on loadBalancerIP"
   kubectl explain service.spec.externalIPs | grep -i deprecat || echo "no deprecation on externalIPs"
   kubectl get --raw '/openapi/v3/api/v1' \
     | jq -r '.components.schemas["io.k8s.api.core.v1.ServiceSpec"].properties.externalIPs.description' \
     | grep -i deprecat || echo "openapi carries no deprecation for externalIPs"
   echo "(loadBalancerIP, by contrast:)"
   kubectl explain service.spec.loadBalancerIP | grep -i deprecat
   ```

3. Make the field answer. Add the spare address to the node so traffic to it lands here, then reach
   the ClusterIP Service on it from off-cluster — from the Mac, or from the node's external address.
   A ClusterIP Service is now serving on an IP a user wrote into its `.spec`.

   ```sh
   sudo ip addr add 10.10.10.199/24 dev $(ip route show default | awk '{print $5; exit}')
   ip addr show | grep 10.10.10.199
   curl -s --max-time 5 http://10.10.10.199/hostname && echo
   curl -s --max-time 5 http://10.10.10.199/hostname && echo
   kubectl -n bw-extip get endpointslices -l kubernetes.io/service-name=my-service \
     -o jsonpath='{.items[0].endpoints[*].addresses}'; echo
   ```

4. Build CVE-2020-8554 in miniature. A second user, in a second namespace, points the same external
   IP at a backend of their own. Nothing allocates external IPs, so the API accepts the collision,
   and traffic to the address now reaches a Service the address's first owner never authorised.

   ```sh
   kubectl create namespace bw-extip-attacker
   kubectl -n bw-extip-attacker create deployment evil \
     --image=registry.k8s.io/e2e-test-images/agnhost:2.53 -- /agnhost netexec --http-port=8080
   kubectl -n bw-extip-attacker rollout status deployment/evil --timeout=120s
   cat <<'EOF' | kubectl -n bw-extip-attacker apply -f -
   apiVersion: v1
   kind: Service
   metadata:
     name: intercept
   spec:
     type: ClusterIP
     selector:
       app: evil
     ports:
       - protocol: TCP
         port: 80
         targetPort: 8080
     externalIPs:
       - 10.10.10.199
   EOF
   echo "both services claim 10.10.10.199:"
   kubectl get svc -A -o json | jq -r '.items[]|select(.spec.externalIPs[]?=="10.10.10.199")|"\(.metadata.namespace)/\(.metadata.name)"'
   for i in $(seq 1 6); do curl -s --max-time 5 http://10.10.10.199/hostname; echo; done
   ```

5. Turn on the guard the post names. Enabling an admission plugin on a kubeadm node is one edit to
   the API server's static Pod manifest; the kubelet restarts the Pod when the file changes. Then
   test the three behaviours the reference promises: new use rejected, existing Services untouched,
   values removable but not addable.

   ```sh
   sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/kube-apiserver.yaml.bw
   sudo sed -i 's#\(- --enable-admission-plugins=.*\)#\1,DenyServiceExternalIPs#; t; s#\(- kube-apiserver\)#\1\n    - --enable-admission-plugins=DenyServiceExternalIPs#' \
     /etc/kubernetes/manifests/kube-apiserver.yaml
   grep enable-admission-plugins /etc/kubernetes/manifests/kube-apiserver.yaml
   echo "waiting for the API server to come back..."
   until kubectl -n bw-extip get svc my-service >/dev/null 2>&1; do sleep 3; done
   echo "--- net-new use, expect rejection ---"
   kubectl -n bw-extip create service clusterip late --tcp=80:8080 --dry-run=client -o yaml \
     | kubectl set selector --local -f - app=web -o yaml \
     | sed 's/^spec:/spec:\n  externalIPs: [10.10.10.198]/' \
     | kubectl apply -f - 2>&1 | tail -2
   echo "--- existing service still serves ---"
   curl -s --max-time 5 http://10.10.10.199/hostname; echo
   echo "--- removing the value is allowed ---"
   kubectl -n bw-extip patch service my-service --type=json \
     -p '[{"op":"remove","path":"/spec/externalIPs"}]' && echo removed
   echo "--- adding it back is not ---"
   kubectl -n bw-extip patch service my-service --type=json \
     -p '[{"op":"add","path":"/spec/externalIPs","value":["10.10.10.199"]}]' 2>&1 | tail -1
   ```

6. Follow the post's easiest-but-worst alternative to the letter. A `type: LoadBalancer` Service
   with a class no controller claims stays `<pending>`; the address is written afterwards through
   the `status` subresource, and it lands in `.status`, not `.spec`.

   ```sh
   cat <<'EOF' | kubectl -n bw-extip apply -f -
   apiVersion: v1
   kind: Service
   metadata:
     name: manual-lb
   spec:
     loadBalancerClass: non-existent-class
     type: LoadBalancer
     selector:
       app: web
     ports:
       - protocol: TCP
         port: 80
         targetPort: 8080
   EOF
   kubectl -n bw-extip get svc manual-lb
   kubectl -n bw-extip patch service manual-lb --subresource=status --type=merge \
     -p '{"status":{"loadBalancer":{"ingress":[{"ip":"10.10.10.198"}]}}}'
   kubectl -n bw-extip get svc manual-lb -o jsonpath='{.spec.externalIPs}{"\n"}{.status.loadBalancer.ingress}'; echo
   echo "--- a services-writer Role does not reach services/status ---"
   kubectl create clusterrole svc-writer --verb=get,list,patch,update --resource=services --dry-run=client -o yaml \
     | grep -A3 resources
   ```

7. Apply the Gateway alternative and watch it do nothing. If the Gateway API CRDs are not installed
   the `apply` fails on unknown kinds, which is itself the finding; if a previous exercise installed
   them, the objects are accepted but no controller programs an address.

   ```sh
   cat <<'EOF' | kubectl -n bw-extip apply -f - 2>&1 | tail -6
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: example-gateway
   spec:
     gatewayClassName: example-gateway-class
     addresses:
     - type: IPAddress
       value: 10.10.10.197
     listeners:
     - name: http
       protocol: HTTP
       port: 80
   EOF
   kubectl -n bw-extip get gateway example-gateway -o jsonpath='{.status.addresses}{"\n"}{.status.conditions[*].type}' 2>/dev/null \
     || echo "no Gateway API in this cluster"
   kubectl get crd 2>/dev/null | grep -c gateway.networking.k8s.io || echo 0
   ```

8. Leave the cluster and read the two pages the census row turns on, plus the smaller disagreements
   around them. Run this in a checkout of `kubernetes/website` at the pin, with `W` set to
   `content/en`.

   ```sh
   cd /path/to/kubernetes/website/content/en
   W=$(pwd)
   echo "--- concept page: deprecated + migrate away ---"
   sed -n '1051,1053p' $W/docs/concepts/services-networking/service.md
   echo "--- generated reference: no deprecation on externalIPs ---"
   sed -n '84,85p' $W/docs/reference/kubernetes-api/core/service-v1.md | grep -i deprecat \
     || echo "no deprecation notice on externalIPs in the reference"
   echo "--- same file marks loadBalancerIP deprecated ---"
   sed -n '117p' $W/docs/reference/kubernetes-api/core/service-v1.md | grep -o 'Deprecated'
   echo "--- DenyServiceExternalIPs is not a default plugin ---"
   sed -n '130p' $W/docs/reference/access-authn-authz/admission-controllers.md | grep -o 'DenyServiceExternalIPs' \
     || echo "not in the default list"
   echo "--- one CVE, four destinations ---"
   grep -rho 'CVE-2020-8554[^ )]*' $W --include='*.md' | sort -u
   grep -rn 'issues/970760' $W --include='*.md' | sed 's|.*/content/en/||'
   echo "--- no feature gate governs the field ---"
   ls $W/docs/reference/command-line-tools-reference/feature-gates/ | grep -i externalip
   echo "--- the ipvs twin names its re-enable gate ---"
   sed -n '212p' $W/docs/reference/networking/virtual-ips.md | grep -o 'KubeProxyIPVS'
   ```

**Expect**

Step 1 prints `v1.35.x`. There is no externalIP metric or gate to find, and `DenyServiceExternalIPs`
is not in the default plugin list, so both fallbacks print. The Deployment rolls out, and the
Service is created with no warning and no error: `kubectl get service` shows it `type: ClusterIP`
with `10.10.10.199` under `EXTERNAL-IP`. That silence is the point — the deprecation warning the
post promises was added at v1.36, and this node is a release below it.

Step 2 is the disagreement, live. `kubectl explain service.spec.externalIPs` prints the field's
description with no deprecation line; `service.spec.loadBalancerIP` prints one. The OpenAPI query
confirms it from the wire: the schema the cluster serves carries `Deprecated` for the neighbour and
nothing for `externalIPs`. What the docs concept page asserts, the machine the docs describe does
not know.

Step 3 makes the ClusterIP Service answer from outside the cluster. After the address is added to
the node's interface, both `curl`s to `10.10.10.199` return a hostname, and it is the `web`
Deployment's pod name — the same pod the EndpointSlice lists. A Service typed `ClusterIP`, which is
meant to be reachable only from inside, is now serving on an IP a user chose, because that user
wrote it into `.spec.externalIPs`.

Step 4 is the vulnerability. The attacker's Service is accepted with no complaint — the `jq` line
lists both `bw-extip/my-service` and `bw-extip-attacker/intercept` claiming `10.10.10.199` — and the
six `curl`s return a mix of the two backends' hostnames, or all of the attacker's, depending on
which rules kube-proxy wrote last. Nothing in the cluster decided the second claim was illegitimate,
because nothing allocates external IPs. That is CVE-2020-8554: any principal who can create a
Service can intercept traffic to any address.

Step 5 shows the guard working exactly as its reference describes. Once the API server restarts with
the plugin enabled, the attempt to create a new Service carrying `externalIPs` is rejected with an
admission error naming `DenyServiceExternalIPs`; the existing `my-service` keeps serving on
`10.10.10.199`, so the `curl` still answers; removing the `externalIPs` value from the existing
Service succeeds; and adding it back is rejected. New use blocked, old use preserved, values one-way
removable — the three behaviours `admission-controllers.md:247-252` promises.

Step 6 lands the address in the right half of the object. The `manual-lb` Service is `<pending>` for
its external IP until the `status` patch, because the non-existent class keeps every controller off
it, and after the patch the address shows under `.status.loadBalancer.ingress` while
`.spec.externalIPs` is empty. The ClusterRole print shows `services` and not `services/status`,
which is why an ordinary user granted write on Services still cannot set the address — the security
difference the post claims, made concrete.

Step 7 is the alternative that does the least. If the Gateway API CRDs are absent the `apply` fails
on an unknown kind, which is the pin's own state — nothing in the tree installs them. If an earlier
exercise installed them, the `Gateway` is accepted but its `.status` carries no address and no
`Accepted` condition, because no controller is watching. Either way the address the post attaches in
one clause never becomes a working endpoint on a cluster built from nothing.

Step 8 confirms the reading offline. The concept page prints the `deprecated` feature-state and the
migrate-away sentence; the reference lines for `externalIPs` carry no `Deprecated`, while line 117
of the same file does for `loadBalancerIP`; `DenyServiceExternalIPs` is absent from the
default-plugin line; the CVE resolves to `cvedetails.com`, a `97076` GitHub issue and a `cve.org`
record, with the sneak-peek's `970760` standing alone; no feature-gate file matches `externalip`;
and the IPVS deprecation one page over names `KubeProxyIPVS` as its way back, where the field in
hand names none.

**Read on**

11. [One Deployment, four exposures](../../labs/01/14-four-ways-to-expose.md) — stands up ClusterIP,
    NodePort, LoadBalancer and Ingress and is the one exercise in the curriculum that installs
    MetalLB. It owns the `IPAddressPool` the post's second alternative writes; take its account of
    what LoadBalancer needs to work and say which of the post's three alternatives that lab already
    provides a running example of.

12. [The nftables kube-proxy row](../2025/01-nftables-kube-proxy.md) — owns the proxy modes and the
    rules that make a Service IP answer on a node, which this exercise reads as given. It also
    carries the `ipvs` deprecation whose timeline is this field's twin; read its account of the
    `KubeProxyIPVS` re-enable gate and say what the externalIPs notice is missing.

13. [The Pod Security Admission row](../2021/09-pod-security-admission-beta.md) — owns the admission
    controller mechanism and the default-enabled plugin list at `admission-controllers.md:119-130`.
    Step 5 here enables one plugin that is not on that list; take the list there and say why a
    security-relevant controller ships off by default.

14. [Experimenting with Gateway API using kind](02-experimenting-gateway-api-with-kind.md) — found
    that the pin installs none of the Gateway API and that a Gateway takes its address in the one
    clause `.spec.addresses`. Carry step 7's result — the block applies but never programs an
    address — into that row's finding about what the pin ships.

15. Unanswerable from the pin: what the *way to opt back in* at v1.40 will be. The timeline promises
    one for kube-proxy's removal of the field but names nothing, and unlike the `ipvs` mode beside
    it there is no gate file reserving the name. The pin can prove the promise is unnamed; it cannot
    tell you whether the lever will be a feature gate, a kube-proxy flag, or a config field, because
    the release that would define it is past the pin.

**Teardown**

Revert the API server manifest first, because a `DenyServiceExternalIPs` left enabled will reject
externalIPs work in every later exercise, then drop the namespaces and the spare address:

```sh
ssh zain@10.10.10.180 "sudo mv -f /root/kube-apiserver.yaml.bw /etc/kubernetes/manifests/kube-apiserver.yaml; \
  until kubectl get --raw /healthz >/dev/null 2>&1; do sleep 3; done; \
  kubectl delete namespace bw-extip bw-extip-attacker --wait; \
  sudo ip addr del 10.10.10.199/24 dev \$(ip route show default | awk '{print \$5; exit}')"
```

The Gateway from step 7 goes with its namespace; the CRDs, if an earlier exercise installed them,
are that exercise's to remove. The node itself is
[destroyed](../../strands/lab-topologies.md#teardown) in the usual way when you are finished with
it.
