<a id="using-rbac-generally-available-18"></a>
# The rule at the centre of this post names an API group that now serves nothing and the API server accepts it without a warning, two of the post's other manifests never worked and `kubectl` rather than the API server is what catches them, and the one property the post praises — that RBAC rules are purely additive — is why one flag on your own control plane makes every Role here decoration

**Post** — [Using RBAC, Generally Available in Kubernetes v1.8](https://kubernetes.io/blog/2017/10/using-rbac-generally-available-18/),
2017-10-28, Kubernetes v1.8. Written by Eric Chiang (CoreOS), co-lead of SIG Auth, three days after
[the kubeadm release post](05-kubeadm-v18-released.md). An editor's note at the top places it in a
*Five Days of Kubernetes 1.8* series.

**As written** — the post is a tutorial in three movements, and each movement ends in a manifest or
a terminal transcript you are meant to copy.

It opens on the default ClusterRoles. *"All Kubernetes clusters install a default set of
ClusterRoles, representing common buckets users can be placed in"* — `admin`, `cluster-admin`,
`edit`, `view` — and it prints `kubectl get clusterroles` with those four and a `# ...` where the
rest would be. Before any of that it states the premise the whole post rests on:

> Users start with no permissions and must explicitly be granted access by an administrator.

Then the bindings, demonstrated rather than described:

```
$ kubectl create clusterrolebinding jane --clusterrole=edit --user=jane

$ kubectl get namespaces --as=jane

NAME          STATUS    AGE
default       Active    43m
kube-public   Active    43m
kube-system   Active    43m

$ kubectl auth can-i create deployments --namespace=dev --as=jane
yes
```

And the namespaced case, with the denial spelled out in full:

```
$ kubectl get deployments --as=dave --as-group=infra --namespace prod
Error from server (Forbidden): deployments.extensions is forbidden: User "dave" cannot list deployments.extensions in the namespace "prod".
```

The second movement is custom roles. *"Each ClusterRole holds a list of permissions specifying
'rules.' Rules are purely additive and allow specific HTTP verb to be performed on a set of
resource."* A `deployer` ClusterRole follows, at `rbac.authorization.k8s.io/v1`, granting seven verbs
on `apps` `deployments`, seven on core `configmaps` and `secrets`, and three on core `pods`.

Then the sentence the exercise turns on. *"Verbs correspond to the HTTP verb of the request, while
the resource and API groups refer to the resource being referenced. Consider the following Ingress
resource:"*

```
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: test-ingress
spec:
  backend:
    serviceName: testsvc
    servicePort: 80
```

*"To POST the resource, the user would need the following permissions:"*

```
rules:
- apiGroups: ["extensions"] # "apiVersion" without version
  resources: ["ingresses"]  # Plural of "kind"
  verbs: ["create"]         # "POST" maps to "create"
```

Three inline comments, one per line, teaching the reader how to derive a rule from a manifest. This
is the post's method, stated as a rule of thumb and shown once.

The third movement is roles for applications. *"When deploying containers that require access to the
Kubernetes API, it's good practice to ship an RBAC Role with your application manifests."* A Role for
a Prometheus instance in the `dev` namespace:

```
kind: Role

metadata:
  name: prometheus-role
  namespace: dev

rules:
- apiGroups: [""] # "" refers to the core API group
  Resources: ["services", "endpoints", "pods"]
  verbs: ["get", "list", "watch"]
```

Then service accounts. *"To run a pod with a custom service account, create a ServiceAccount
resource in the same namespace and specify the `serviceAccountName` field of the manifest."*

```
apiVersion: apps/v1beta2 # Abbreviated, not a full manifest
kind: Deployment
metadata:
  name: prometheus-deployment
  namespace: dev
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:v1.8.0
        command: ["prometheus", "-config.file=/etc/prom/config.yml"]
    # Run this pod using the "prometheus-sa" service account.
    serviceAccountName: prometheus-sa
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus-sa
  namespace: dev
```

Five manifests, two transcripts, and one premise. Take them in that order.

**As it runs now** — the three outcomes the rest of this tree keeps insisting are different are all
present in this one post, one per manifest, and the post gives you no way to tell them apart.

*The manifests that error.* The Prometheus Role fails twice. It carries no `apiVersion` at all, so
there is no group-version for `kubectl` to map `kind: Role` onto and nothing is sent to the cluster;
and once you add `rbac.authorization.k8s.io/v1` it fails again on `Resources:` with a capital R,
because `kubectl --validate` defaults to `strict`
(`docs/reference/kubectl/generated/kubectl_create/kubectl_create_namespace.md:105` and every other
generated `kubectl` page carry `--validate string[="strict"]  Default: "strict"`) and
`docs/concepts/overview/working-with-objects/_index.md:142` defines strict as *"Strict field
validation, errors on validation failure"*. The Deployment errors too, on `apps/v1beta2`, which
`docs/reference/using-api/deprecation-guide.md:334` records as *no longer served as of v1.16*.

*The manifest that succeeds and does nothing.* The Ingress rule — the one with the three teaching
comments — applies cleanly. No error, no warning, no event. At the pin it grants nothing at all,
because there is nothing left in the `extensions` group to grant. Every resource that group ever
served has been withdrawn: Ingress as of v1.22 (`deprecation-guide.md:259`), and NetworkPolicy,
DaemonSet, Deployment, ReplicaSet and PodSecurityPolicy all as of v1.16 (`:314`, `:321`, `:334`,
`:363`, `:372`). `extensions` is a name with an empty body, and a Role naming it is accepted at
`--validate=strict` by an API server that will never match it against a request. Ingress now lives
in `networking.k8s.io`; the post's rule and the post's Ingress manifest were consistent with each
other in 2017 and are both wrong now, in the same direction, for the same reason — and only one of
them tells you.

*The manifest that is accepted and then quietly does the wrong thing.* The Deployment's
`serviceAccountName` is indented one level too shallow. Load it with a YAML parser and the field
lands at `spec.template.serviceAccountName`, a sibling of `spec.template.spec` rather than a key
inside it: `spec.template` comes back with the keys `['spec', 'serviceAccountName']` and
`spec.template.spec` comes back with `['containers']` alone. `PodTemplateSpec` has no
`serviceAccountName`, so at strict validation this is an unknown field and errors; drop to
`--validate=warn` — or POST it from anything that is not `kubectl` — and the field is pruned, the
Deployment is created, the Pod runs, and it runs as the service account the post wrote three
manifests to avoid. `docs/reference/access-authn-authz/rbac.md:1103` states the consequence in one
sentence: *"If an application does not specify a `serviceAccountName`, it uses the 'default' service
account."* The comment immediately above the misplaced line reads *"Run this pod using the
'prometheus-sa' service account."* The `# Abbreviated, not a full manifest` disclaimer on the first
line covers the missing `selector` and `labels`. It does not cover indentation.

*The transcripts.* Both still run and both print something different from what the post printed.
`kubectl get namespaces --as=jane` returns **four** namespaces, not three: `kube-node-lease` joined
the initial set and `docs/concepts/overview/working-with-objects/namespaces.md:44` now opens
*"Kubernetes starts with four initial namespaces"*, listing it as the holder of the Lease objects the
kubelet heartbeats through. And the Forbidden message names a resource that no longer exists —
`deployments.extensions` — because in 2017 `kubectl` resolved `deployments` through the `extensions`
group. Today the same command produces the same denial about `deployments.apps`. The post's error
text is evidence for the era, not a string to match against.

*The premise.* *"Users start with no permissions"* is not true of an authenticated user on a fresh
cluster, and was not true in 2017 either. `rbac.md`'s discovery-roles table binds
**`system:basic-user`** and **`system:discovery`** to the `system:authenticated` group, and
**`system:public-info-viewer`** to both `system:authenticated` and `system:unauthenticated`, all by
default, all before any administrator does anything. The table dates the third to v1.14 and notes
that the first two were bound to `system:unauthenticated` as well prior to v1.14 — so the direction
of travel since the post has been to grant *less* by default, and the floor is still not zero.
`rbac.md:581` calls this *"read-only access to API information that is deemed safe to be publicly
accessible"*, and the way to switch it off is `--anonymous-auth=false`, which is an authentication
flag rather than an authorization one.

**The diff, and why** — two of the template's cases land in this post at once, and the interesting
thing is that they land on different manifests of the same tutorial. Three manifests were **wrong
when they were published**: the Role with no `apiVersion`, the Role with `Resources:`, and the
Deployment with `serviceAccountName` at the wrong depth. None of the three has ever worked, on any
release. A reader who assumes they did will spend the first ten minutes of this exercise blaming
their cluster, which is why those corrections come first below and the translation comes after. The
Ingress example is the other case: it **broke**, in v1.22, and the release that broke it is recorded
in a page about API removals that does not mention RBAC.

Take the corrections first, because they are the ones that say something about the tooling rather
than about 2017.

`kubectl` catches two of the three. It catches `Resources:` and it catches the misindented
`serviceAccountName`, and in both cases it catches them because they are **unknown fields in a typed
schema**. It does not catch them because they are wrong; it catches them because they are not in the
Go struct. The distinction is not academic, because `kubectl`'s strictness is `kubectl`'s, not the
cluster's. `docs/reference/kubernetes-api/rbac/cluster-role-binding-v1.md:128` documents the
`fieldValidation` request parameter and states the server-side default plainly: `Warn` *"is the
default in v1.23+"*, and `Warn` *"will send a warning via the standard warning response header for
each unknown field that is dropped from the object … The request will still succeed if there are no
other errors."* So the API server's own posture toward the post's two never-worked manifests is to
accept them, drop the fields it does not recognise, and mention it in a header. The thing standing
between this post and a silently pruned Role is a client-side default in one command-line tool.

Now the third manifest, the one nothing catches, and the reason is the whole point of the exercise.
A rule's `apiGroups`, `resources` and `verbs` are lists of **strings**. There is no group-version to
map, no struct field to be absent from, and no discovery lookup at admission time — an RBAC rule
naming a group that does not exist is a syntactically perfect object, and the API server stores it
without complaint. `rbac.md:239` prints one on purpose, in the *Referring to resources* section: a
`example.com-superuser` ClusterRole over `apiGroups: ["example.com"]`, captioned
`# DO NOT USE THIS ROLE, IT IS JUST AN EXAMPLE`. The pin therefore demonstrates, in passing and
without saying so, that a rule for an API group no cluster serves is a legal object. It never states
the rule that makes the demonstration safe.

That asymmetry runs one way through the whole of `rbac.md` and through
`docs/concepts/security/rbac-good-practices.md`. Both warn at length about rules that grant **too
much**: avoid wildcards, because *"providing wildcard access gives rights not just to all object
types that currently exist in the cluster, but also to all object types which are created in the
future"* (`rbac-good-practices.md:34`); avoid `cluster-admin`; avoid `system:masters`, whose
membership *"cannot be revoked by removing RoleBindings or ClusterRoleBindings"* (`:41-43`). And
*Periodic review* tells you to review *"for redundant entries and possible privilege escalations"*
(`:79`). Nothing anywhere tells you to review for rules that grant **nothing**, and nothing in the
API will ever tell you either. A Role whose rules are all misspelled and a Role whose rules are all
correct are the same object to every instrument the cluster offers. The post's method — read the
`apiVersion`, strip the version, pluralise the `kind` — is a good method, and it produces an
undetectably dead rule the moment a resource changes groups.

Which brings the second half, and the census row's trap. The post says *"Rules are purely
additive"*; `rbac.md:58` still says it, in almost the same words: *"Permissions are purely additive
(there are no 'deny' rules)."* The post presents this as simplicity. The pin presents the same fact
as a warning, in the box beside `AlwaysAllow` at `docs/reference/access-authn-authz/authorization.md:151`:

> Activating the `AlwaysAllow` means that if all other authorizers return "no opinion", the request
> is allowed. For example, `--authorization-mode=AlwaysAllow,RBAC` has the same effect as
> `--authorization-mode=AlwaysAllow` because Kubernetes RBAC does not provide negative (deny) access
> rules.

One property, two readings, nine years apart. Because RBAC can only ever say *allow* or *no
opinion*, it cannot overrule anything, and an authorizer chain is only as restrictive as its most
permissive member. Every Role in this post — the correct ones included — becomes decoration the
moment `AlwaysAllow` appears anywhere in the chain. And the flag still defaults to it:
`docs/reference/command-line-tools-reference/kube-apiserver.md:363` reads *"Ordered list of
plug-ins to do authorization on secure port. Defaults to AlwaysAllow if --authorization-config is not
used."* Note where that default lives. The flag's header cell carries no `Default:` annotation the
way `--anonymous-auth   Default: true` does; the default is stated only inside the description, and
only conditionally.

The pressure that moved it is the second flag in that sentence. `--authorization-config` replaced the
comma-separated list with a file, and the two are mutually exclusive:
`authorization.md:358-360` says *"You cannot combine the `--authorization-mode` command line argument
with the `--authorization-config` command line argument"*, and `:179` says what happens if you
try — *"the API server reports an error message during startup, then exits immediately."* That
sentence at `:358` also contains the page's one broken self-reference: it links
`#using-configuration-file-for-authorization-mode`, while the heading it means declares
`{#using-configuration-file-for-authorization}` and is linked correctly from `:173`. The same page
links its own section twice, once right and once wrong, and the wrong one is in the paragraph a
reader reaches after their control plane has exited at startup.

Two other things the post could not have said, both consequences of releases after it. Its claim at
*"as new resources are added to Kubernetes, the default ClusterRoles are updated to automatically
grant the correct permissions to RoleBinding subjects within their namespace"* is now served by two
distinct mechanisms rather than one: **auto-reconciliation**, which `rbac.md:567` describes as the
API server updating default cluster roles *"at each start-up … with any missing permissions"*, and
**ClusterRole aggregation** (`rbac.md:256`), a control-plane controller that watches for an
`aggregationRule` label selector and fills in `rules` from the ClusterRoles it matches. The first
covers what Kubernetes ships; the second is what makes the post's sentence true for a *custom*
resource, and it is how `admin`, `edit` and `view` acquire rules today —
`rbac.md:633` says those three *"use ClusterRole aggregation to allow admins to include rules for
custom resources"*. Aggregation also inverts the post's mental model of a Role as a thing you write:
`rbac.md:266` cautions that *"the control plane overwrites any values that you manually specify in
the `rules` field of an aggregate ClusterRole"*.

And the four default roles are still four, still named what the post names them, with one of the
post's one-line descriptions now carrying a caveat the post had no reason to print. The post says
*"'view' lets a user observe non-sensitive resources"*; the pin's table spells out which resource it
means and why — `view` *"does not allow viewing Secrets, since reading the contents of Secrets
enables access to ServiceAccount credentials in the namespace, which would allow API access as any
ServiceAccount in the namespace (a form of privilege escalation)"*. The post says *"the 'edit' role
lets users perform basic actions like deploying pods"*; the pin's row for `edit` says that role
*"allows accessing Secrets and running Pods as any ServiceAccount in the namespace, so it can be used
to gain the API access levels of any ServiceAccount in the namespace"*. Both rows also carve out
write access to EndpointSlices *"in clusters created using Kubernetes v1.22+"*. The buckets did not
change; what changed is that the documentation now says out loud what being in one of them buys you.

**No gate** — RBAC has none, and this is a `"now Generally Available"` post, so the absence is worth
naming rather than skipping. There is no `feature-gates/RBAC.md`; a built-in authorizer selected by a
flag was never gated, and the five files under `feature-gates/` whose names match *rbac* or
*author* — `AuthorizeNodeWithSelectors`, `AuthorizePodWebsocketUpgradeCreatePermission`,
`AuthorizeWithSelectors`, `DRAResourceClaimGranularStatusAuthorization`,
`StructuredAuthorizationConfiguration` — are all later and none is RBAC itself.

**The instrument, then, is `deprecation-guide.md`**, and what it can tell you is thin. Its entry
*RBAC resources* (`:279-286`) records that `rbac.authorization.k8s.io/v1beta1` is *no longer served as
of v1.22* and, in the migration bullet beneath, that `rbac.authorization.k8s.io/v1` has been
*"available since v1.8"*. That clause is the only place in the pinned documentation tree that dates
this post's subject, and it is a parenthesis inside a removal notice for the version RBAC's GA
replaced. A graduation that got a five-day blog series leaves, nine years on, one date in a footnote
about something else. It is also the only version claim in the post that is still exactly right: the
`deployer` ClusterRole is written at `rbac.authorization.k8s.io/v1`, and of the post's five manifests
it is the one whose `apiVersion` needs no translation at all. Search the tree for
`rbac.authorization.k8s.io/v1alpha1` and you get two hits, both in
`docs/concepts/overview/kubernetes-api.md` (`:141`, `:295`), both as illustrations of what a discovery
URL looks like rather than as a served version.

Two gates *are* load-bearing below, and each gets its ladder. Neither is RBAC's.

`StructuredAuthorizationConfiguration` is why the `AlwaysAllow` default is stated conditionally:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.29 – v1.29 |
| beta | `true` | — | v1.30 – v1.31 |
| stable | `true` | — | v1.32 – |

`ComponentFlagz` is the instrument step 7 uses to read the running authorizer chain without opening a
file:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.32 – v1.35 |
| beta | `true` | — | v1.36 – |

Neither file declares `removed` or `former_titles`. The second ladder matters to this exercise in one
specific way: beta and on by default from v1.36 means the endpoint is there on a cluster you install
today without enabling anything, and `docs/tasks/administer-cluster/configure-feature-gates.md:222-234`
tells you it exists — *"you can inspect the command-line flags that were used to start the
component by visiting the `/flagz` endpoint"* — without ever printing a command for doing so.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair): a control-plane node at `10.10.10.130`
and one worker at `10.10.10.131`. RBAC is entirely an API-server concern and one node would carry
every authorization check below, but the post's third movement ends in a Deployment, and the only way
to see what the misindented `serviceAccountName` cost is to read the service account off a Pod that
is actually running. The worker is there so that Pod schedules without the control-plane taint
entering the exercise.

Provision with the five steps at [`#provision`](../../strands/lab-topologies.md#provision), then the
node baseline at [`#node-baseline-steps`](../../strands/lab-topologies.md#node-baseline-steps) on both
nodes, then `ssh zain@10.10.10.130`. Take the current minor here — the deviation
[the previous exercise](05-kubeadm-v18-released.md) makes for its own subject does not carry forward,
and nothing below depends on the version except the two ladders above.

Create the namespace the post assumes before step 1: `kubectl create namespace dev`. Every manifest in
the post's third movement names `namespace: dev` and the post never creates it.

**Do**

1. Save the post's Prometheus Role exactly as printed and run
   `kubectl apply -f prometheus-role.yaml`. Record the error verbatim. Then add
   `apiVersion: rbac.authorization.k8s.io/v1` as the first line — change nothing else — and apply
   again. Record the second error verbatim. Two defects, two messages, and they come from different
   places: name which of the two errors could have been produced without a cluster to talk to, and
   how you can tell from the text alone.

2. Fix `Resources:` to `resources:` and apply. It is accepted. Now go back to the version from the end
   of step 1 — `apiVersion` present, capital `R` still there — and apply it with
   `kubectl apply --validate=warn -f prometheus-role.yaml`. Read what comes back, then run
   `kubectl get role prometheus-role -n dev -o yaml` and count the entries under `rules`. Compare
   against the three resources the post's Role names.

3. Write out the post's Ingress rule as a real Role in `dev` — `apiGroups: ["extensions"]`,
   `resources: ["ingresses"]`, `verbs: ["create"]`, named `ingress-creator` — and apply it with the
   default validation. Then create a ServiceAccount `ingress-maker` in `dev` and a RoleBinding tying
   it to that Role. Everything applies. Nothing warns. Note that before moving on.

4. Ask the cluster whether the binding did anything:

   ```sh
   kubectl auth can-i create ingresses -n dev --as=system:serviceaccount:dev:ingress-maker
   kubectl api-resources --api-group=extensions
   kubectl api-resources -o name | grep ingresses
   ```

   The three outputs together are the exercise. Say which one of them the API server would have used
   to reject the Role in step 3, if it checked rules against served resources at all.

5. Now do the same thing correctly — a second Role over `apiGroups: ["networking.k8s.io"]`, same
   resource, same verb, bound to the same ServiceAccount — and re-run the first `can-i` from step 4.
   Then run `kubectl auth can-i --list -n dev --as=system:serviceaccount:dev:ingress-maker` and find
   both Roles' contributions in the output. The dead rule appears in that listing too. What does that
   tell you about using `--list` to audit a namespace?

6. Test the post's premise. Before creating any binding for `jane`, run
   `kubectl auth can-i --list --as=jane` and count the lines. Then follow the post:
   `kubectl create clusterrolebinding jane --clusterrole=edit --user=jane`, then
   `kubectl get namespaces --as=jane`, then
   `kubectl auth can-i create deployments --namespace=dev --as=jane`. Compare the namespace list
   against the post's three rows. Then reproduce the post's denial —
   `kubectl create namespace prod`, `kubectl create rolebinding infra --clusterrole=edit --group=infra --namespace=dev`,
   and `kubectl get deployments --as=dave --as-group=infra --namespace prod` — and compare the
   resource name inside the `Forbidden` message against the one the post printed.

7. Save the post's Deployment and ServiceAccount pair. Apply it: `apps/v1beta2` fails. Change the
   `apiVersion` to `apps/v1`, add the `metadata.labels` and `spec.selector` the post's own
   `# Abbreviated, not a full manifest` note excuses, and leave the indentation of
   `serviceAccountName` untouched. Apply. Record the error and the exact field path it names. Then
   apply the same file with `--validate=warn`, wait for the Pod, and run

   ```sh
   kubectl get pod -n dev -l app=prometheus -o jsonpath='{.items[0].spec.serviceAccountName}'
   ```

   Then fix the indentation, re-apply at default validation, and run the same `jsonpath` against the
   new Pod. Three outcomes from one file: name them in the vocabulary this section header uses.

8. Read the authorizer chain your own cluster is running, two ways, and notice that only one of them
   is documented:

   ```sh
   kubectl get --raw /flagz | grep -i authorization
   sudo grep -n authorization /etc/kubernetes/manifests/kube-apiserver.yaml
   ```

   One of the two flags in `authorization.md`'s mutually-exclusive pair is in that manifest and the
   other is not. Say which, and then search `docs/reference/setup-tools/kubeadm/` for the string
   `authorization-mode`: the page that claims to list the API server flags kubeadm *"set[s]
   unconditionally"* does not mention it. Where in the pinned tree does `Node,RBAC` appear as
   kubeadm's value at all?

9. Make the census row's trap real, using the mechanism from
   [the previous exercise](05-kubeadm-v18-released.md): edit
   `/etc/kubernetes/manifests/kube-apiserver.yaml` and change the authorization mode to
   `AlwaysAllow,Node,RBAC`. Do not restart anything — the kubelet is watching that directory. Wait
   for the API server to come back (`crictl ps` on the node while `kubectl` is down), then confirm the
   change through `kubectl get --raw /flagz` and re-run every `can-i` from steps 4, 5 and 6,
   including the `--as=jane` one *before* you delete her binding. Then delete
   `clusterrolebinding jane` and ask again.

10. Put the flag back, wait for the API server again, and confirm the denials return. That restart
    also exercises auto-reconciliation, so use it: before restoring the flag, run
    `kubectl patch clusterrole view --type=json -p '[{"op":"remove","path":"/rules/0"}]'` and count
    the rules; after the API server is back, count them again. `rbac.md:567` says when this happens
    and `rbac.md:572` says how to stop it — which annotation, on which object?

**Expect**

Step 1's first error is produced without any request reaching the cluster: with no `apiVersion`
there is no group-version to map `kind: Role` onto, and the mapping happens client-side. The second
error does reach the cluster, and names the unknown field. Record both strings rather than matching
them against ones written here; the point of the step is that the two messages have different
origins, and that is legible from the text.

Step 2: at `--validate=warn` the Role is created with **zero** rules. `Resources:` is pruned as an
unknown field, and what is left of the rule is `apiGroups` and `verbs` with nothing to apply them to.
A Role that grants nothing, created successfully, with a warning in a header you had to ask for.

Step 3: three objects created, exit 0, no warnings.

Step 4: `can-i create ingresses` answers **no**. `kubectl api-resources --api-group=extensions`
returns an empty list — the group is served by nothing. `kubectl api-resources -o name | grep
ingresses` returns `ingresses.networking.k8s.io`. The Role from step 3 is a valid, stored,
permanently inert object, and the third command is the only one of the three that would have caught
it. Nothing in the admission path runs it.

Step 5: `can-i create ingresses` now answers **yes**. `can-i --list` shows both Roles' rules,
including `ingresses` under `extensions`, because `--list` reports what the RBAC objects say and not
what the API server can serve. It is a rule inventory, not an audit.

Step 6: `can-i --list --as=jane` before any binding is **not empty** — `jane` authenticates into
`system:authenticated`, which the discovery bindings already cover, so she arrives with read access
to `/api`, `/apis`, `/version`, `/healthz` and the rest of the non-resource discovery set. That is
the post's premise failing on a fresh cluster. `kubectl get namespaces --as=jane` prints **four**
rows: `default`, `kube-node-lease`, `kube-public`, `kube-system`. `can-i create deployments` prints
`yes`, as the post says. The `Forbidden` message names `deployments.apps`, not
`deployments.extensions`.

Step 7: `apps/v1beta2` errors on the version. With `apps/v1` and default validation, the error names
the unknown field at `spec.template.serviceAccountName` — the path itself is the finding, because it
is a sibling of `spec.template.spec`, not a child. At `--validate=warn` the Deployment is created and
the `jsonpath` returns **`default`**. With the indentation fixed it returns **`prometheus-sa`**. The
post's comment was right about the intent and the manifest under it was wrong about the depth, and
the only cluster-side symptom of the difference is which service account's token is mounted into the
container.

Step 8: `/flagz` prints `authorization-mode=[Node,RBAC]`, bracketed, because it is a list flag.
`--authorization-config` is absent from the manifest. `implementation-details.md` never mentions the
authorization mode in any of its unconditional-flag lists; the only places in the pinned tree that
show `Node,RBAC` as kubeadm's value are the two generated config-API pages
(`kubeadm-config.v1beta3.md:199` and `kubeadm-config.v1beta4.md:258`), and both show it as an example
of *overriding* an extra argument rather than as a statement of the default. The value your cluster
runs on is documented nowhere in prose; it is only in the manifest and in `/flagz`.

Step 9: every `can-i` answers **yes**, including for `jane` after her ClusterRoleBinding is deleted
and including `create ingresses` for a service account bound only to the dead `extensions` Role.
`/flagz` shows `authorization-mode=[AlwaysAllow,Node,RBAC]`. The Roles are all still there; they
have simply stopped meaning anything, which is the difference between an authorization *decision* and
an authorization *object* and the reason `AlwaysAllow` is the one mode with a warning box beside it.

Step 10: the denials come back. `view` has its removed rule back after the API server restarts,
because reconciliation runs at start-up and adds missing permissions to default cluster roles.

**Read on** — three questions, all answerable from the pin, and one that is not.

`docs/reference/using-api/deprecation-guide.md:279-286` is the only dated record of this post's
subject in the whole tree. Read the entry and answer two things: which release stopped serving
`rbac.authorization.k8s.io/v1beta1`, and where in that entry the date of RBAC's graduation appears.
Then ask why the graduation has no page of its own, when the removal of the version it replaced does.

`docs/reference/access-authn-authz/authorization.md:170-183` and `:340-363` describe the two ways to
configure the authorizer chain. Read both, then settle which of the page's two links to its own
configuration-file section resolves and which does not — they are at `:173` and `:360` — and what the
broken one costs a reader whose API server has just *"report[ed] an error message during startup, then exit[ed] immediately"*. The
answer is three characters long.

`docs/reference/kubernetes-api/rbac/cluster-role-binding-v1.md:128` documents `fieldValidation` and
gives the server-side default. Read it against
`docs/concepts/overview/working-with-objects/_index.md:130-152`, which gives `kubectl`'s. The two
defaults differ. Which of this post's three never-worked manifests would be created rather than
rejected by a client that took the server's default, and what would each one do afterwards?

And the one that is not in the pin: `StructuredAuthorizationConfiguration` reached stable in v1.32
and the pinned tree carries **no KEP link for it** — not in `authorization.md`, not in the gate file,
not in the 2024 blog post that announced its beta. The number is not written here, because a KEP
number written from memory is not evidence. Find it from
`docs/reference/command-line-tools-reference/feature-gates/StructuredAuthorizationConfiguration.md`
and the enhancements repository, then answer from the KEP itself what problem the ordered
comma-separated list could not express — the answer is why the flag that still defaults to
`AlwaysAllow` now has a rival that cannot.

**Teardown** — [`#teardown`](../../strands/lab-topologies.md#teardown). Take it down. Step 9 put
`AlwaysAllow` in front of the authorizer chain of a cluster on a routable lab address, and step 10
restores the flag but not the certainty: the API server was restarted twice by hand, `view` was
patched, and four Roles, two RoleBindings, a ClusterRoleBinding and two namespaces are left behind.
None of that is worth carrying into the next exercise.
