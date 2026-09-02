<a id="security-best-practices-kubernetes-deployment"></a>
# The project marked this post partly obsolete without saying which part, its one still-exact snippet is the one nobody should use, and its example manifest contradicts its own table

**Post** — [Security Best Practices for Kubernetes Deployment](https://kubernetes.io/blog/2016/08/security-best-practices-kubernetes-deployment/),
2016-08-31, Kubernetes v1.3. A vendor guest post from Aqua Security, and the only post in this
census whose source file at the pin opens with a warning from the project:

> _Note: some of the recommendations in this post are no longer current. Current cluster hardening
> options are described in this [documentation](/docs/tasks/administer-cluster/securing-a-cluster/)._

That note is the exercise. It says **some**, it does not say which, and it names one successor page
when the pin ships two. Sorting the post's eight recommendations into *still current*, *no longer
current* and *wrong when written* is work the note leaves undone, and it is work you can only
finish against a running cluster.

Note also that the post cannot agree with itself about who wrote it: the frontmatter's `author:`
field names Michael Cherny alone, and the editor's note in the body names *"Amir Jerbi and Michael
Cherny"*. Two attributions, one file; cite both.

**As written** — eight headings, aligned to *"the container lifecycle: build, ship and run"*:

1. **Ensure That Images Are Free of Vulnerabilities** — continuous CVE scanning; redeploy rather
   than `apt-update` a running container, *"as this can break the image-container relationship."*
2. **Ensure That Only Authorized Images are Used in Your Environment** — private registries, a CI
   gate, and a forecast: *"There is work in progress being done in Kubernetes for image
   authorization plugins (expected in Kubernetes 1.4), which will allow preventing the shipping of
   unauthorized images."*
3. **Limit Direct Access to Kubernetes Nodes** — and the sentence to hold onto:

   > You should limit SSH access to Kubernetes nodes, reducing the risk for unauthorized access to
   > host resource. Instead you should ask users to use "kubectl exec", which will provide direct
   > access to the container environment without the ability to access the host.

4. **Create Administrative Boundaries between Resources** — namespaces plus *"Kubernetes
   Authorization plugins"*, demonstrated with an ABAC policy: *"the following policy will allow
   'alice' to read pods from namespace 'fronto'."*

   ```json
   {
     "apiVersion": "abac.authorization.kubernetes.io/v1beta1",
     "kind": "Policy",
     "spec": {
       "user": "alice",
       "namespace": "fronto",
       "resource": "pods",
       "readonly": true
     }
   }
   ```

5. **Define Resource Quota** — *"By default, all resources in Kubernetes cluster are created with
   unbounded CPU and memory requests/limits"*, then a manifest described as *"an example for
   namespace resource quota definition that will limit number of pods in the namespace to 4,
   limiting their CPU requests between 1 and 2 and memory requests between 1GB to 2GB."*

   ```yaml
   apiVersion: v1
   kind: ResourceQuota
   metadata:
     name: compute-resources
   spec:
     hard:
       pods: "4"
       requests.cpu: "1"
       requests.memory: 1Gi
       limits.cpu: "2"
       limits.memory: 2Gi
   ```

   ```
   kubectl create -f ./compute-resources.yaml --namespace=myspace
   ```

6. **Implement Network Segmentation** — GCP firewall rules, and *"There is work being done in this
   area by the Kubernetes Network SIG […] A new network policy API should address the need to create
   firewall rules around pods"*, illustrated by reprinting the same `net.alpha.kubernetes.io` POST
   body that [06](06-kubernetes-network-policy-apis.md) walks, and linking to it.
7. **Apply Security Context to Your Pods and Containers** — a four-row table naming
   `SecurityContext->runAsNonRoot`, `SecurityContext->Capabilities`,
   `SecurityContext->readOnlyRootFilesystem` and `PodSecurityContext->runAsNonRoot`, then an example:

   ```yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: hello-world
   spec:
     containers:
     # specification of the pod's containers
     # ...
     securityContext:
       readOnlyRootFilesystem: true
       runAsNonRoot: true
   ```

   and a second recommendation: *"In case you are running containers with elevated privileges
   (--privileged) you should consider using the "DenyEscalatingExec" admission control."*
8. **Log Everything** — *"the standard output and standard error output of each container can be
   ingested using a Fluentd agent running on each node into either Google Stackdriver Logging or
   into Elasticsearch and viewed with Kibana."*

**As it runs now** — the eight sort into four groups, and the boundaries are not where the project's
note implies.

**Still exactly right, and the advice is now wrong.** The ABAC policy in recommendation 4 is the one
block of code in this post you can run unchanged. `abac.authorization.kubernetes.io/v1beta1` is
still the only valid `apiVersion` for an ABAC policy object, `--authorization-mode=ABAC` with
`--authorization-policy-file=` is still how you switch it on, and the pin's own
*Controlling Access* concept page prints the post's policy with two words changed:

> For example, if Bob has the policy below, then he can read pods only in the namespace
> `projectCaribou`

with `"user": "bob"`, `"namespace": "projectCaribou"`, `"resource": "pods"`, `"readonly": true` —
the same four keys in the same order as alice and fronto. The ABAC reference page carries no
deprecation notice and no caution. And yet the successor page the project's own note points you at
says something else entirely:

> It is recommended that you use the [Node](/docs/reference/access-authn-authz/node/) and
> [RBAC](/docs/reference/access-authn-authz/rbac/) authorizers together, in combination with the
> [NodeRestriction](/docs/reference/access-authn-authz/admission-controllers/#noderestriction)
> admission plugin.

So the post's snippet is valid, the mechanism is supported, nothing in the tree marks it obsolete,
and the recommended configuration does not include it. That gap is not a documentation bug you can
report; it is what "no longer current" means when a feature is kept and unrecommended at the same
time. The post says *"Kubernetes Authorization plugins"* three times and never says RBAC, which had
not shipped: it arrived at alpha in v1.6, seven months after this post.

**Wrong when written.** Two of the eight, and both are checkable in under five minutes.

Recommendation 5's prose does not describe its own manifest. A ResourceQuota governs
*"aggregate resource consumption per namespace"* — `requests.cpu: "1"` is one core of requests
across the whole namespace, not a floor or a ceiling per pod. The mechanism that restricts
*"the maximum or minimum size"* per object is LimitRange, which existed in 2016 and which the post
never names. So *"limiting their CPU requests between 1 and 2"* is a description of a LimitRange
attached to a ResourceQuota's manifest, and the practical consequence is the opposite of what a
reader would expect: with this quota in place, four pods requesting 300m each will not fit.

Recommendation 7's example contradicts recommendation 7's table. The table correctly puts
`readOnlyRootFilesystem` under `SecurityContext`, meaning the container's. The example puts it in
the pod's `securityContext`, where the field does not exist — the pin's Pod reference lists it only
as `spec.containers[*].securityContext.readOnlyRootFilesystem`, and it appears in that form in the
`spec.os` restriction list, which enumerates pod-level and container-level security fields
separately. The example also has no container: `containers:` is followed by two comments and
nothing else. Applied as printed it fails twice over, and the correct version is recoverable from
the post's own table two paragraphs above it.

**Overtaken.** Recommendation 3 is the one the project's note is most likely aimed at, and it is
worse than dated. *"kubectl exec […] without the ability to access the host"* was never a property
of `kubectl exec`; it is a property of the pod you exec into. Exec into a container with
`privileged: true`, or `hostPID: true`, or the host filesystem mounted, and you have the node — and
`kubectl exec` requires only the `pods/exec` subresource, whereas SSH requires a key. The post
therefore recommends closing the door that needs a credential and opening the one that needs an RBAC
verb. The `DenyEscalatingExec` admission controller it offers as a mitigation appears **zero** times
in the pinned documentation; it was removed. Meanwhile the pin ships `kubectl debug node/mynode`,
whose entire purpose is to give you a shell with the node's filesystem from nothing but kubectl, and
the successor page names the real exposure the post never mentions:

> Kubelets expose HTTPS endpoints which grant powerful control over the node and containers.
> By default Kubelets allow unauthenticated access to this API.

Recommendation 6 is [06](06-kubernetes-network-policy-apis.md)'s post reprinted, so it fails in
exactly the ways [06](06-kubernetes-network-policy-apis.md) documents; the only new information is
that a security checklist was still circulating this schema four months after it was proposed and
three releases before anything resembling it shipped. Recommendation 8's pipeline —
Fluentd DaemonSet into Stackdriver or Elasticsearch — is no longer something a cluster arrives with;
it is the same story as [07](07-autoscaling-in-kubernetes.md)'s metrics add-on, one component over.

**Still current, unchanged.** Recommendations 1 and 2 have aged best, and for a reason worth naming:
neither is about Kubernetes. Scanning images for CVEs and gating a registry are things Kubernetes
still does not do, so there was nothing for the API to break. The forecast inside recommendation 2
did land — `ImagePolicyWebhook` exists in the pin's admission-controller reference — which makes it
the mirror image of [06](06-kubernetes-network-policy-apis.md): a 2016 post predicting a feature
"expected in Kubernetes 1.4", and this one was right.

**The diff, and why** — the post is the first case, *the post broke*, applied to a checklist rather
than a command: the recommendations did not stop being good ideas, the objects that carry them
moved. And the direction they moved in is one thing, stated in the pin's successor page:

> Authorization in Kubernetes is intentionally high level, focused on coarse actions on resources.
> More powerful controls exist as **policies** to limit by use case how those objects act on the
> cluster, themselves, and other resources.

Every one of the post's runtime recommendations is per-object: set a field on this pod, add this
admission controller to the API server, write this policy line for this user. The current answer is
per-namespace and declarative, and it is what replaced both halves of recommendation 7:

> You can configure [Pod security admission](/docs/concepts/security/pod-security-admission/) to
> enforce use of a particular [Pod Security Standard](/docs/concepts/security/pod-security-standards/)
> in a namespace, or to detect breaches.

> administrators who wish to prevent client applications from escaping their containers should apply
> the **Baseline** or **Restricted** Pod Security Standard.

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.22 – v1.22 |
| beta | `true` | — | v1.23 – v1.24 |
| stable | `true` | — | v1.25 – v1.27 |

`PodSecurity` declares `removed: true`: one release at alpha, straight to beta on by default, stable
at v1.25, gate retired at v1.28 because the admission controller became unconditional. Six years
after the post, the thing that enforces its recommendation 7 stopped being optional — and it
enforces it by labelling a namespace, not by editing a pod.

The other movement is underneath the post's `runAsNonRoot`, and its ladder is the most instructive
in this year's set:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.28 – v1.29 |
| beta | `false` | — | v1.30 – v1.32 |
| beta | `true` | — | v1.33 – v1.35 |
| stable | `true` | `true` | v1.36 – |

`UserNamespacesSupport` has two beta rows because beta arrived off by default and stayed off for
three releases before the default flipped — the repeated stage marks the flip, not a re-promotion.
Read against the post, it reframes the advice: the post's answer to container root was *don't be
root*, enforced by a field the kubelet checks at container creation. The current answer includes
*be root, and have it mean nothing on the host*, enforced by the kernel. Those are different claims,
and only the first is available to someone following this post.

The post's own summary asked for *"a certain degree of familiarity with these options"*. The pin now
ships that as two documents rather than one: the page the project's note names, and a
`security-checklist` page with nine sections — Authentication & Authorization, Network security, Pod
security, Logs and auditing, Pod placement, Secrets, Images, Admission controllers. Between them
they carry categories the post has no line for at all: restricting cloud metadata API access,
preventing containers from loading kernel modules, restricting access to etcd, encrypting secrets at
rest, rotating infrastructure credentials, and reviewing third-party integrations before enabling
them. That is the honest shape of the diff — not that the post was wrong, but that a 2016 security
checklist could be eight items long.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), fresh, and fresh matters more here
than anywhere else in this year: step 6 edits the API server's static pod manifest, and step 7 wants
a node that is not the control plane. Two nodes gives you both, and both nodes are disposable, which
is the only condition under which switching authorization modes by hand is a reasonable thing to do.
Bring the topology up with [the five provision steps](../../strands/lab-topologies.md#provision)
using `topology=pair`, install Kubernetes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), then
`ssh zain@10.10.10.130`.

**Do**

1. Build the mapping before touching the cluster. Open the post, the page its note names, and the
   pin's `security-checklist` page, and write a three-column table: each of the post's eight
   headings, the section of either current page that covers it, and one of *current* /
   *superseded* / *absent*. Then list the sections of the current pages that the post has no
   heading for. Keep this table; steps 2 to 10 either confirm or overturn rows in it.

2. Disprove recommendation 5's prose with its own manifest:

   ```
   kubectl create namespace myspace
   kubectl create -f ./compute-resources.yaml --namespace=myspace
   kubectl describe quota compute-resources -n myspace
   kubectl -n myspace run a --image=registry.k8s.io/pause:3.10 --overrides='{"spec":{"containers":[{"name":"a","image":"registry.k8s.io/pause:3.10","resources":{"requests":{"cpu":"600m","memory":"600Mi"},"limits":{"cpu":"800m","memory":"800Mi"}}}]}}'
   kubectl -n myspace run b --image=registry.k8s.io/pause:3.10 --overrides='{"spec":{"containers":[{"name":"b","image":"registry.k8s.io/pause:3.10","resources":{"requests":{"cpu":"600m","memory":"600Mi"},"limits":{"cpu":"800m","memory":"800Mi"}}}]}}'
   ```

   Two pods, well under the post's stated per-pod range, and the namespace's pod limit is four.
   Record which command fails and quote the reason. Then find the object type that would have made
   the post's sentence true, and create one.

3. Apply recommendation 7's example pod exactly as printed:

   ```
   kubectl apply -f hello-world.yaml
   ```

   Count the errors. Then rewrite it using the post's own table as the specification — the table
   places one of those two fields somewhere the example does not — and apply again with a real
   container.

4. Test what enforces `runAsNonRoot`, and when:

   ```
   kubectl run rootcheck --image=registry.k8s.io/e2e-test-images/agnhost:2.53 \
     --overrides='{"spec":{"securityContext":{"runAsNonRoot":true}}}' --command -- sleep 3600
   kubectl get pod rootcheck
   kubectl describe pod rootcheck | sed -n '/Events/,$p'
   ```

   The pod is admitted. Say which component refused it, at which point in the lifecycle, and what
   that implies about a `securityContext` as a *security* control.

5. Now apply the control that replaced both of recommendation 7's suggestions, and check what
   happened to the one the post names:

   ```
   kubectl label namespace myspace \
     pod-security.kubernetes.io/enforce=restricted \
     pod-security.kubernetes.io/warn=restricted
   kubectl -n myspace apply -f hello-world.yaml
   kubectl -n myspace run priv --image=registry.k8s.io/pause:3.10 --privileged
   ```

   Copy the rejection message in full — it enumerates every standard the pod violates, which is a
   list the post's four-row table does not contain. Then search the pinned documentation for
   `DenyEscalatingExec` and record the number of occurrences.

6. Make recommendation 4 run. This edits the API server; read the whole step before starting.

   ```
   sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml ~/kube-apiserver.yaml.bak
   sudo mkdir -p /etc/kubernetes/abac
   sudo tee /etc/kubernetes/abac/policy.jsonl >/dev/null <<'EOF'
   {"apiVersion": "abac.authorization.kubernetes.io/v1beta1", "kind": "Policy", "spec": {"user": "alice", "namespace": "fronto", "resource": "pods", "readonly": true}}
   EOF
   ```

   Then add `ABAC` to `--authorization-mode` (keeping `Node` and `RBAC`, and appending rather than
   replacing), add `--authorization-policy-file=/etc/kubernetes/abac/policy.jsonl`, and mount the
   directory into the static pod. Wait for the API server to come back, then ask it:

   ```
   kubectl auth can-i get pods --namespace=fronto --as=alice
   kubectl auth can-i create pods --namespace=fronto --as=alice
   kubectl auth can-i get pods --namespace=default --as=alice
   ```

   Three questions, and the post's four-line policy decides all three. Then restore the backup and
   confirm the API server returns. If it does not come back, the manifest is a file on disk and the
   kubelet is watching it — that is the whole recovery procedure, and finding that out on a
   disposable lab is the reason this step is here.

7. Test recommendation 3's central claim three ways, from the control plane:

   ```
   ssh zain@10.10.10.131 'hostname; ls /etc/kubernetes'
   kubectl run hostpeek --image=registry.k8s.io/e2e-test-images/agnhost:2.53 \
     --overrides='{"spec":{"hostPID":true,"containers":[{"name":"hostpeek","image":"registry.k8s.io/e2e-test-images/agnhost:2.53","command":["sleep","3600"],"securityContext":{"privileged":true}}]}}'
   kubectl exec hostpeek -- ps aux
   kubectl exec hostpeek -- chroot /proc/1/root hostname
   kubectl debug node/<worker-node-name> -it --image=busybox:1.28
   ```

   Three routes to the host. Rank them by what a user needs in order to take them — a key, an RBAC
   verb, or an RBAC verb — and then say whether the post's recommendation makes a cluster safer or
   less safe.

8. Check the forecast in recommendation 2:

   ```
   kubectl -n kube-system get pod -l component=kube-apiserver -o yaml | grep -A2 enable-admission-plugins
   ```

   Then find `ImagePolicyWebhook` in the pin's admission-controller reference and answer two
   questions: did the feature the post expected in 1.4 arrive, and is it on by default in the
   cluster in front of you? Those have different answers.

9. Reprint recommendation 6 and confirm it fails identically to
   [06](06-kubernetes-network-policy-apis.md): send the POST body to the path the post gives, then
   answer one question the two posts together raise — the same dead schema appears in an April
   design post and an August security checklist; which of the two had more reason to check it
   against a running cluster first?

10. Look for recommendation 8's pipeline:

    ```
    kubectl -n kube-system get daemonsets
    kubectl logs rootcheck --previous 2>&1 | head -3
    ssh zain@10.10.10.131 'sudo ls /var/log/pods'
    ```

    Then say where a container's stdout goes on this cluster, how long it stays there, and which of
    the pin's checklist sections owns that question.

**Expect** — step 1: the post's eight headings will not distribute evenly. Expect two rows marked
*current* (the two that are not about Kubernetes), at least three *superseded*, and one that is
worse than superseded. Expect the pin's pages to have roughly twice as many sections as the post has
headings, with the surplus concentrated in things a 2016 checklist could omit: etcd, secrets at rest,
credential rotation, cloud metadata.

Step 2: the quota is created and describes `pods 0/4`, `requests.cpu 0/1`. Pod `a` is admitted; pod
`b` is refused by the `ResourceQuota` admission plugin with `exceeded quota`, naming
`requests.cpu`, the limit of `1`, and the used amount. Two pods out of a stated four, each requesting
less than the post's stated minimum of 1. The object that would have made the sentence true is a
`LimitRange` with `min` and `max` under `type: Container`.

Step 3: two failures at once — `unknown field "spec.securityContext.readOnlyRootFilesystem"` from
strict validation, and a required-value complaint about the container list, because
`containers:` is followed only by comments and therefore parses as null. Moving
`readOnlyRootFilesystem` into the container's `securityContext`, as the post's own table says, and
supplying a container, is accepted.

Step 4: the pod is created and never starts. `describe` shows the kubelet failing at container
creation with a message naming `runAsNonRoot` and the image's root user. The API server admitted a
pod it had no basis to reject: `runAsNonRoot` is a request to the runtime, checked when the container
is made, not a rule the cluster applies to what may be submitted. That is the difference between a
field and a policy, and it is why step 5 exists.

Step 5: the `hello-world` pod is now refused before validation gets to the field errors, with a
`violates PodSecurity "restricted:latest"` message listing several unset requirements at once —
`allowPrivilegeEscalation`, capabilities, `runAsNonRoot`, `seccompProfile`. The privileged pod is
refused for `privileged` and more. `DenyEscalatingExec` occurs zero times in the pinned tree.

Step 6: after the API server restarts, `get pods` in `fronto` as alice is `yes`; `create pods` in
`fronto` is `no`; `get pods` in `default` is `no`. A JSON object published in a blog post in August
2016, typed into a v1.37 cluster, authorizing correctly on all three axes it declares. Note what
this does *not* prove: that the mode is a good idea. There is no way to express in that file the
thing RBAC exists for, which is naming a permission once and binding it to many subjects.

Step 7: SSH needs a key and gives you the worker. The privileged `hostPID` pod's `ps aux` shows the
node's processes including `kubelet` and `containerd`, and `chroot /proc/1/root` gives you the node's
root filesystem — from `kubectl exec`, the command the post recommends as the safe alternative.
`kubectl debug node/` gives you the same thing without needing a pod to exist first. Two of the three
routes need only API permissions.

Step 8: `ImagePolicyWebhook` is documented and is not in the default plugin list; it requires a
configuration file and a webhook you run. So the answer to *did it arrive* is yes and the answer to
*is it on* is no, which is the state most of the pin's admission-controller reference is in.

Step 9: the same 404 as [06](06-kubernetes-network-policy-apis.md), from the same nonexistent group.

Step 10: no logging DaemonSet in `kube-system`. Container output is on the node, rotated by the
kubelet, and gone when the pod is deleted — `--previous` reaches exactly one container generation
back and nothing further. The checklist section that owns it is *Logs and auditing*, and the post's
*Log Everything* covers the first word of that pair and not the second: audit logging is absent from
this post entirely.

**Read on** — the pin's
[Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/):
read the *Restricted* profile's field list against the post's four-row table and answer one
question — how many of Restricted's requirements could have been expressed at all in v1.3, and of
those, how many would a reader of this post have set? Then read the
[security checklist](https://kubernetes.io/docs/concepts/security/security-checklist/)'s own opening
caveat about what a checklist is worth, and answer a harder one: this post carries a project note
saying some of its advice is no longer current, and the checklist page carries a caveat of its own —
what would have to be true of a security document for it to still be accurate ten years on, and does
either page claim it?

**Teardown** — `kubectl delete namespace myspace`, then
`kubectl delete pod rootcheck hostpeek --ignore-not-found`. Confirm
`/etc/kubernetes/manifests/kube-apiserver.yaml` matches the backup taken in step 6 and that
`/etc/kubernetes/abac` is removed. Take the topology down with
[teardown](../../strands/lab-topologies.md#teardown) — and if step 6 left the API server
unreachable, teardown is the answer, which is the other reason this exercise asks for a fresh
`pair`.
