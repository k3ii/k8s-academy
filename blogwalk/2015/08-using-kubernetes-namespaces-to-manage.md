<a id="using-kubernetes-namespaces-to-manage"></a>
# The commands in this post all still work; the sentence in the middle of it is the reason people lose clusters

**Post** — [Using Kubernetes Namespaces to Manage
Environments](https://kubernetes.io/blog/2015/08/using-kubernetes-namespaces-to-manage/),
2015-08-28, Kubernetes 1.0.

**As written** — namespaces let you "manage different environments within the same cluster", so
test, staging and production can share machines instead of each needing a cluster. Four sections.

*The Default Namespace*: `kubectl get namespaces` prints two rows, `default` and `kube-system`,
under the headers `NAME LABELS STATUS`. The post then drops a hook it never comes back to — "The
status of the namespace is used later when turning down and deleting the namespace" — and moves
on.

*Creating a New Namespace*: a five-line manifest, `kind: Namespace`, `apiVersion: v1`, a name and
a `name:` label, then `kubectl create -f my-namespace.yaml`.

*Service Names*, which is the load-bearing section and worth quoting in full:

> This works because each of the resources in the cluster will by default only "see" the other
> resources in the same namespace. This means that you can avoid naming collisions by creating
> pods, services, and replication controllers with the same names provided they are in separate
> namespaces.

Then DNS: short names resolve within the namespace, and to reach across you use "the full DNS name
which takes the form of `SERVICE-NAME.NAMESPACE-NAME`. So for example, `elasticsearch.prod` or
`elasticsearch.canary`".

*An Example*: four namespaces — `default`, `mytunes-prod`, `mytunes-staging`, `my-other-app` — and
`kubectl get services --namespace=mytunes-staging` twice, showing `mytunes` and `mysql` with
identical names and different IPs in each. One detail in that pasted output: the staging external
IP is printed as `104.185.824.125`. There is no such address; `824` is not an octet. The output was
hand-edited, and the edit did not survive.

*Caveats*: if you share a cluster between staging and production you "will need to be careful to
set up resource limits so that your staging environment doesn't starve production", and doing that
properly "takes a lot of time and effort", so unless you can measurably save money, "you may not
really want to do that." Closing line: "namespaces will also serve as a level where you can apply
resource limits so look for more resource management features at the namespace level in the
future."

**As it runs now** — the census called this "almost the only 2015 post whose commands still run",
and that holds. The manifest applies unchanged. `--namespace=` works. Same-named services in
different namespaces get different cluster IPs. Short-name DNS resolves in-namespace. What changed:

1. **The listing is longer and the columns are different.** A cluster starts with **four**
   namespaces, not two: `default`, `kube-system`, `kube-public` — "readable by *all* clients
   (including those not authenticated)" — and `kube-node-lease`, which holds the Lease objects the
   kubelet heartbeats into. The `LABELS` column is gone from default output; you ask for it with
   `--show-labels`.
2. **`kubectl get services` prints a different table.** The post's `NAME LABELS SELECTOR IP(S)
   PORT(S)`, with the external IP wrapped onto a second line under `IP(S)`, became `NAME TYPE
   CLUSTER-IP EXTERNAL-IP PORT(S) AGE`. Nothing about the resource changed; the human-readable
   printer did.
3. **The post's own recommendation is now advised against.** The pin: "For a production cluster,
   consider *not* using the `default` namespace. Instead, make other namespaces and use those."
   The post opens by teaching you `default`.
4. **The cross-namespace name in the post is shorter than the one the docs now require.** The pin
   says the DNS entry is `<service-name>.<namespace-name>.svc.cluster.local` and that "if you want
   to reach across namespaces, you need to use the fully qualified domain name (FQDN)". The post's
   `elasticsearch.prod` is not an FQDN, and it resolves anyway — because of the `search` list and
   `ndots` in the pod's `/etc/resolv.conf`, not because of anything the API promises. Step 5 is
   where that distinction stops being pedantic.
5. **The prediction came true.** ResourceQuota and LimitRange are namespace-scoped and the
   concepts page now states flatly that "namespaces are a way to divide cluster resources between
   multiple users (via resource quota)". Pod Security Admission is configured entirely by
   *labels on the namespace* — `pod-security.kubernetes.io/<MODE>: <LEVEL>`. Namespaces became the
   place policy attaches, which is exactly what the last line asked for.
6. **The sentence in *Service Names* is the one thing here that is dangerous.** Names are scoped.
   Nothing else is. By default "if no policies exist in a namespace, then all ingress and egress
   traffic is allowed to and from pods in that namespace" — a pod in staging can open a connection
   to a pod in production, by IP or by qualified name, with no policy in its way. The pin's
   multi-tenancy page says the quiet part: "The namespace isolation model requires configuration of
   several other Kubernetes resources, networking plugins, and adherence to security best practices
   to properly isolate tenant workloads."

**The diff, and why** — this post is three cases at once, and sorting them is the exercise.

Most of it is **still right**, and that is unusual enough in 2015 to be worth noticing on its own:
namespaces were designed once, correctly, at v1.0, and have not needed to change. Compare
[the SSL post](07-strong-simple-ssl-for-kubernetes.md), whose mechanics also survived — the
difference is that nothing absorbed namespaces, because there was nothing above them to absorb
them into.

A small piece is **wrong as published**: `104.185.824.125` never existed. It is harmless, and it
is the fourth wrong-at-publication finding in this corpus and the first of its shape — not a
mangled manifest, but fabricated sample output. Worth cataloguing because it tells you what to
distrust in a blog post: the prose was reviewed, the pasted terminal output was not.

The interesting case is the third, and it is neither a break nor a stasis. The sentence "each of
the resources in the cluster will by default only 'see' the other resources in the same namespace"
was **true of the only thing that could see anything in August 2015**. Service discovery was
environment variables, injected per namespace, and DNS short names, resolved per namespace. If
that is how your pod learns about other pods, then namespace scoping really is the whole boundary,
and the sentence is a fair description of the system. There was no `NetworkPolicy` at v1.0 to
contradict it. "See" meant "can find the name of".

Then the ways a pod could see things multiplied, and the sentence did not move. Every mechanism
added since — direct pod IPs, service IPs from another namespace, cross-namespace qualified DNS,
the API server itself once a ServiceAccount can list — punches straight through, and the sentence
still reads as a guarantee to anyone who does not already know it is not one. That is why the
census marks the *advice* as expired while the commands run: the post did not become wrong by
being contradicted. It became wrong by staying still while the meaning of one of its verbs widened
underneath it.

There was one release era in which the post's sentence nearly came true, and it is worth knowing
about because it is the closest Kubernetes ever came to making a namespace a boundary. When
`NetworkPolicy` first appeared it lived in `extensions/v1beta1`, and isolation was switched on by
**annotating the namespace** — `net.beta.kubernetes.io/network-policy`. For those releases,
"resources in a namespace only see each other" was a thing you could literally turn on, per
namespace, with one annotation. By `networking.k8s.io/v1` (served since v1.8) the annotation was
gone and isolation had moved to the Pod: a pod is isolated if and only if some policy's
`spec.podSelector` selects it, and a pod selected by nothing accepts everything. The switch was
taken off the namespace and handed to a selector — which is why step 1's automatic
`kubernetes.io/metadata.name` label exists at all.

The pressure behind this is the one the whole sweep keeps meeting from different sides. Kubernetes
will not ship a boundary it cannot specify completely — see
[CRI](03-docker-and-kubernetes-and-appc.md) and
[logging](04-cluster-level-logging-with-kubernetes.md) for the same refusal in different clothes.
Network isolation depends on a CNI plugin the project does not own, so `NetworkPolicy` is an API
that a plugin may or may not enforce, and a namespace stayed what it always was: a scope for
names, plus a place to hang policies you must opt into.

Release facts and the pressure behind each are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

**No gate** — nothing in this exercise is gated. Namespaces, ResourceQuota, LimitRange, the DNS
scheme and PSA's namespace labels are all unconditional at the pin, and there is no gate to read
for any claim above. The instruments are the API server's own resource list
(`kubectl api-resources --namespaced=false`, step 8 — the definitive statement of what a namespace
can never contain), the namespace object's `.status.phase` and `.spec.finalizers` (step 7), and
the pod's `/etc/resolv.conf` (step 5), which is the only place the post's `elasticsearch.prod`
shorthand is actually explained.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo) — the guest from
[the SSL exercise](07-strong-simple-ssl-for-kubernetes.md) is still up; keep it. If you are
starting here, bring it up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, then `ssh zain@10.10.10.180`.

**Do**

1. Run the post's first command and count:

   ```sh
   kubectl get namespaces
   kubectl get namespaces --show-labels
   ```

2. Build the post's example with the post's own manifest, unedited except for the name:

   ```sh
   for n in mytunes-prod mytunes-staging my-other-app; do
   cat <<YAML | kubectl create -f -
   kind: Namespace
   apiVersion: v1
   metadata:
    name: $n
    labels:
      name: $n
   YAML
   done
   ```

3. Put identically-named services in two of them and compare the table to the post's:

   ```sh
   for n in mytunes-prod mytunes-staging; do
     kubectl -n $n create deployment mysql --image=nginx:alpine
     kubectl -n $n expose deployment mysql --name=mysql --port=3306 --target-port=80
   done
   kubectl get svc -A --field-selector metadata.name=mysql
   ```

4. Now test the *Service Names* sentence. From a pod in staging, try to reach production three
   ways — the short name, the post's two-label name, and the raw cluster IP:

   ```sh
   PIP=$(kubectl -n mytunes-prod get svc mysql -o jsonpath='{.spec.clusterIP}')
   kubectl -n mytunes-staging run probe --image=busybox --restart=Never -it --rm -- sh -c "
     nslookup mysql | tail -3
     nslookup mysql.mytunes-prod | tail -3
     wget -qS -O /dev/null http://$PIP:3306 2>&1 | head -3
     echo '--- resolv.conf ---'; cat /etc/resolv.conf"
   ```

5. Then the trap the pin warns about, which the post's naming style walks straight into. `prod` is
   not a public top-level domain. `dev` is:

   ```sh
   kubectl create namespace dev
   kubectl -n dev create deployment www --image=nginx:alpine
   kubectl -n dev expose deployment www --name=www --port=80
   kubectl run probe --image=busybox --restart=Never -it --rm -- sh -c \
     'nslookup www.dev; nslookup www.dev. | tail -4'
   ```

   Note which of the two lookups went to the cluster and which went to the internet, and what the
   difference between them was.

6. Test the post's *Caveats* section — the one place it hedges — by finding out what a namespace
   does *not* separate:

   ```sh
   kubectl get pods -A -o wide --field-selector status.phase=Running \
     -o custom-columns=NS:.metadata.namespace,NAME:.metadata.name,NODE:.spec.nodeName
   kubectl -n mytunes-staging create quota starve --hard=cpu=100m,memory=128Mi
   kubectl -n mytunes-staging scale deployment mysql --replicas=3
   kubectl -n mytunes-staging get events --field-selector reason=FailedCreate | tail -2
   ```

7. Close the hook the post opened and abandoned. Look at what `STATUS` is actually made of, then
   watch it change:

   ```sh
   kubectl get ns my-other-app -o jsonpath='{.spec.finalizers}{"  phase="}{.status.phase}{"\n"}'
   kubectl delete ns my-other-app --wait=false
   kubectl get ns my-other-app -o jsonpath='{.status.phase}{"\n"}'
   ```

8. Finally, ask the API server for the boundary's real shape — the list of things no namespace can
   ever contain:

   ```sh
   kubectl api-resources --namespaced=false -o name | tr '\n' ' ' | fold -w 88
   kubectl api-resources --namespaced=false -o name | wc -l
   ```

**Expect** — step 1 prints four namespaces where the post printed two, under `NAME STATUS AGE`
rather than `NAME LABELS STATUS`. `--show-labels` reveals `kubernetes.io/metadata.name` on every
one, set by the control plane so that a `namespaceSelector` in a NetworkPolicy can match a
namespace by name — a label that exists only because the isolation the post assumed had to be
built later, out of selectors.

Step 2: the eleven-year-old manifest applies with no complaint and no deprecation warning.

Step 3: two services, both named `mysql`, different `CLUSTER-IP`s, `EXTERNAL-IP` `<none>` for
both. This is the post's central demonstration and it reproduces exactly. The columns do not match
the post's, and neither IP has an octet above 255.

Step 4 is the whole exercise. `nslookup mysql` resolves to staging's IP — names are scoped, as
promised. `nslookup mysql.mytunes-prod` resolves to production's, so the post's shorthand works.
And the `wget` **connects** to production's cluster IP from a staging pod. It will fail at the HTTP
layer, because you pointed port 3306 at nginx; read the failure carefully — a refusal from the
server is a completed TCP connection. Nothing stopped the packet. Then `/etc/resolv.conf` explains
the second lookup: `search mytunes-staging.svc.cluster.local svc.cluster.local cluster.local` and
`options ndots:5`. `mysql.mytunes-prod` has one dot, fewer than five, so the resolver appends each
search suffix in turn and the second one hits. The post's "full DNS name" is not full; it is a
two-label name that a specific resolver configuration completes for you.

Step 5: `www.dev` — one dot, under `ndots:5` — is searched first and resolves to **your cluster's**
service. `www.dev.` with the trailing dot skips the search list and leaves the cluster. That is the
pin's warning made concrete: "Workloads from any namespace performing a DNS lookup without a
trailing dot will be redirected to those services, taking precedence over public DNS." A namespace
name is a DNS label, so choosing namespace names is choosing which public domains your cluster
quietly shadows — and the post's suggested names (`prod`, `canary`, `staging`) were chosen for
readability by someone for whom this could not yet go wrong.

Step 6: every pod, in every namespace, is on the same node — `solo` guarantees it, but on any
cluster nothing about a namespace influences scheduling. The quota is where the post's caveat was
right: the third replica is refused with a quota error, and the mechanism it asked for in its last
sentence is the mechanism doing the refusing. Note also what the quota did *not* do: it did not
stop staging's existing pods competing for the node's CPU with production's.

Step 7: the finalizer is `["kubernetes"]` and the phase is `Active`. After a non-blocking delete
the phase reads `Terminating`, and it stays there until the namespace controller has deleted every
namespaced object inside and removed the finalizer. That is the "status … used later when turning
down and deleting the namespace" the post promised and never explained, and it is the single most
common way a namespace gets stuck: a finalizer waiting on something that is never coming.

Step 8 prints on the order of fifty kinds — Node, PersistentVolume, StorageClass,
ClusterRole, ValidatingAdmissionPolicy, the ClusterTrustBundle from
[the SSL exercise](07-strong-simple-ssl-for-kubernetes.md). Read that list as the negative image
of the post's claim. Everything on it is shared by every environment in the cluster, so "test and
staging in the same cluster" means test and staging share your cluster roles, your storage classes,
your admission policies and your nodes. The post's cost argument was about VMs. The list is the
part of the bill it did not price.

**Teardown** — `kubectl delete ns mytunes-prod mytunes-staging dev` and
`kubectl get ns my-other-app` to confirm the delete from step 7 finished. If any namespace is still
`Terminating` after a minute, look for the finalizer before you look for a bigger hammer. Leave the
guest up; [the kubectl exercise](09-some-things-you-didnt-know-about-kubectl.md) runs on it.
