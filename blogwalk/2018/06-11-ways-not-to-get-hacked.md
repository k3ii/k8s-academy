<a id="11-ways-not-to-get-hacked"></a>

# The advice in this post is still the project's advice and the post can no longer be followed: four of its nine links into `kubernetes.io` are broken, nothing in the pinned tree redirects any of them, two of the dead paths survive nowhere in the whole checkout except inside this post, and the pin's own removal reference still says in the future tense that the object at the centre of it will be removed

**Post** — [11 Ways (Not) to Get Hacked](https://kubernetes.io/blog/2018/07/18/11-ways-not-to-get-hacked/),
2018-07-18, Andrew Martin (ControlPlane). 24,938 bytes, 310 lines: the longest `walk` in this year
and the only one written as a checklist. The census row for it is in
[this year's table](README.md) and commits the exercise to *the one that was deleted*.

**As written** — eleven numbered recommendations under three parts, with a table of contents the
post builds by hand at `:11-25`:

- **Part One: The Control Plane** (`:27`) — 1 TLS Everywhere, 2 Enable RBAC with Least Privilege /
  Disable ABAC / Monitor Logs, 3 Use Third Party Auth for API Server, 4 Separate and Firewall your
  etcd Cluster, 5 Rotate Encryption Keys.
- **Part Two: Workloads** (`:102`) — 6 Use Linux Security Features and PodSecurityPolicies,
  7 Statically Analyse YAML, 8 Run Containers as a Non-Root User, 9 Use Network Policies,
  10 Scan Images and Run IDS.
- **Part Three: The Future** (`:278`) — 11 Run a Service Mesh.

Each recommendation opens with a single bolded claim and then argues it. There are four YAML blocks
and one Python one, and exactly one Kubernetes object among them that the API server of the day
would have stored on the operator's behalf: a `PodSecurityPolicy` fragment at `:172-178`.

Nine links point at `kubernetes.io`. Eight are into `/docs/`:

| post line | target | topic |
|---|---|---|
| `:37` | `/docs/tasks/administer-cluster/securing-a-cluster/#use-transport-level-security-tls-for-all-api-traffic` | item 1 |
| `:65` | `/docs/admin/authorization/rbac/#role-binding-examples` | item 2 |
| `:69` | `/docs/tasks/debug/debug-cluster/audit/` | item 2 |
| `:97` | `/docs/tasks/tls/certificate-rotation/` | item 5 |
| `:99` | `/docs/tasks/administer-cluster/encrypt-data/` | item 5 |
| `:112` | `/docs/concepts/policy/pod-security-policy/` | item 6 |
| `:200` | `/docs/concepts/services-networking/network-policies/` | item 9 |
| `:266` | `/docs/admin/admission-controllers/` | item 10 |

The ninth, at `:53`, is a cross-reference to a sibling blog post:
`http://kubernetes.io/blog/2017/04/rbac-support-in-kubernetes.html`.

**As it runs now** — the recommendations have aged unusually well and the pointers under them have
not. Resolving all nine against the pinned tree gives three dead `/docs/` paths and one dead blog
URL:

- `/docs/admin/authorization/rbac/` — no file, no directory.
- `/docs/concepts/policy/pod-security-policy/` — no file. The page that answers to this subject now
  lives at `docs/concepts/security/pod-security-policy.md`: `concepts/security/`, not
  `concepts/policy/`.
- `/docs/admin/admission-controllers/` — no file, no directory.
- The blog link at `:53` is right about the path and wrong about the shape.
  `manifest.tsv` gives that post's URL as `https://kubernetes.io/blog/2017/04/rbac-support-in-kubernetes/`:
  no `.html`, and `https`. The post's link carries both.

**Nothing redirects any of them.** Hugo would catch a moved page through an `aliases:` entry in the
new page's front matter, and there is not a single `aliases:` line containing `/docs/admin/`
anywhere in the docs tree. The two `/docs/admin/` paths are not stale links to relocated pages;
they are links to a URL prefix the site has stopped acknowledging.

**Two of the three dead paths survive in the checkout only inside this post.** Searching the whole
pinned tree for `admin/authorization/rbac` returns one file, and for `admin/admission-controllers`
one file, and in both cases the file is `blog/_posts/2018/11-ways-not-to-get-hacked.md`. The third,
`concepts/policy/pod-security-policy`, returns five files — and all five are blog posts, none of
them a documentation page. The archive is the last place these addresses are written down.

The tooling fared the same way. Item 6 at `:110` recommends two profile generators.
`docker-slim` appears in zero files under `docs/`. `bane` appears in exactly one,
`docs/tutorials/security/apparmor.md:255`, where it is described as "an AppArmor profile generator
for Docker that uses a simplified profile language" and linked as
`https://github.com/jfrazelle/bane`. The post links `https://github.com/genuinetools/bane`. The
tool outlived the post and the docs and the post disagree about where it lives.

**The object is gone, and it is the only object the post asks you to create.** The name
`PodSecurityPolicy` occurs 53 times across `docs/`, in ten files. Four of those files exist because
the object does not — a tombstone concept page, a glossary entry, a 22-occurrence migration task,
and a field-by-field mapping reference — and the other six are passing mentions, in the Pod Security
Admission concept, the security checklist, the labels-and-annotations reference, the `kubectl`
reference, the admission-controllers reference and the deprecation guide. The tombstone page opens
with a warning box (`pod-security-policy.md:9-12`):

> PodSecurityPolicy was [deprecated](/blog/2021/04/08/kubernetes-1-21-release-announcement/#podsecuritypolicy-deprecation)
> in Kubernetes v1.21, and removed from Kubernetes in v1.25.

Both of that page's citations are blog posts. So are the deprecation guide's. Neither points at a
KEP, a release note, or another documentation page for the reasoning — the authority for why the
project deleted the object this post recommends is the blog this post was published on.

**The pin's removal reference still speaks about it in the future tense.**
`deprecation-guide.md:148-151` reads:

> #### PodSecurityPolicy {#psp-v125}
>
> PodSecurityPolicy in the **policy/v1beta1** API version is no longer served as of v1.25,
> and the PodSecurityPolicy admission controller will be removed.

The same file carries a second PodSecurityPolicy entry, `:370-375`, for an earlier removal of the
same kind — the `extensions/v1beta1` version, gone at v1.16 — and it closes:

> * Note that the **policy/v1beta1** API version of PodSecurityPolicy will be removed in v1.25.

Two sentences in the tense of a plan, in a v1.37 pin, about work finished twelve releases ago.
The object was removed twice, nine releases apart, and the page that records both removals has not
been re-read since the first one was written.

**The successor declines to cover half of what the post's object did.**
`psp-to-pod-security-standards.md` maps `PodSecurityPolicySpec` field by field onto the Pod Security
Standards. Its first table has 25 field rows, and **13 of the 25** answer with some form of
*No opinion*; the second table, for the four annotations PodSecurityPolicy honoured, adds two more.
`migrate-from-psp.md:127-130` says why in its own words:

> There are several fields in PodSecurityPolicy that are not covered by the Pod Security Standards.
> If you must enforce these options, you will need to supplement Pod Security Admission with an
> admission webhook, which is outside the scope of this guide.

And `:102-105` names the harder half:

> If a PodSecurityPolicy is mutating pods, then you could end up with pods that don't meet the Pod
> Security level requirements when you finally turn PodSecurityPolicy off. […] Unfortunately PSP
> does not cleanly separate mutating & validating fields, so this is not a straightforward
> migration.

**What this exercise does not cover, and where it lives.** A checklist collides with the rest of the
corpus in a way a single-subject post does not, and three of these eleven items are already carried
elsewhere in full. Item 2 belongs to
[the RBAC exercise](../2017/06-using-rbac-generally-available-18.md) — RBAC against ABAC, the
`--authorization-mode` flag, and the additive-rules property are its whole subject. Item 9 belongs
to [the NetworkPolicy exercise](../2017/07-enforcing-network-policies-in-kubernetes.md), including
the `default-deny` object of exactly the shape this post prints and the reason nothing on this
curriculum's cluster enforces it. The move from a cluster-scoped policy object to a labelled
namespace, and the `PodSecurity` gate that made it unconditional, belong to
[the 2016 security checklist](../2016/08-security-best-practices-kubernetes-deployment.md). Pointers,
not prerequisites: this exercise takes the pointers and the object, and leaves the mechanisms where
they are already exercised.

Two smaller readings, stated here and not built:

- **The post's one prediction came true.** Item 8 at `:196` says *"Having to run workloads as a
  non-root user is not going to change until user namespaces are usable"*. At the pin it has
  changed; the ladder for that is transcribed in
  [the 2016 security checklist](../2016/08-security-best-practices-kubernetes-deployment.md), which
  reaches the same field from the other direction.
- **One sentence in the post was wrong the day it was published.** Item 9's second policy sets
  `policyTypes: [Egress]` and the prose at `:219` claims it "also prevents inbound connections to
  your application". A policy that lists only `Egress` selects no ingress rules at all and cannot
  affect inbound traffic; `network-policies.md:109-113` is the paragraph that says so. The
  mechanism is the NetworkPolicy exercise's; the error is this post's.

**The diff, and why** — the second case, *the post is still right*, and this is the clearest
instance of it in the archive so far, because being right turns out not to be the same as being
followable. Seven of the eleven recommendations need no correction at all: TLS everywhere (1), RBAC
over ABAC (2), third-party auth (3), firewalling etcd (4), static analysis (7), network policies (9)
and image scanning (10). Four moved. Item 5 asks you to rotate encryption keys and states that the
symmetric keys "are not automatically rotated", which is now true of only part of the key hierarchy.
Item 6 names an object that no longer exists. Item 8's advice stands and its worked example does
not: the workaround is unnecessary and the blocker it names is gone. Item 11 was filed under *The
Future* and predicted a third-party mesh, while the mechanism it depends on — a proxy that starts
before the application containers and is stopped only once they are done — was absorbed into the Pod
API instead.

That is a good record for an eight-year-old security checklist, and it is not what makes this post
hard to use. What makes it hard to use is that four of its nine references into the project's own
site are broken, three of them by a reorganisation that left no aliases, and the fourth by a change
to the site's URL scheme. Every earlier exercise in this year has measured a feature against the
pin. This one measures the *addresses*, and they have decayed faster than the advice they point at.

It is worth naming why that asymmetry exists, because it is a property of the archive and not of
this post. A recommendation is prose, and prose does not break; a URL is a claim about someone
else's filesystem, and it breaks the moment they tidy up. The project has a mechanism for keeping
that claim true — `aliases:` — and used it nowhere in this post's blast radius. Meanwhile the one
thing the post asks you to *create* got six replacement pages, a field-by-field migration table
that declines half the fields, and two reference sentences still written in the future tense.
The care went into documenting the deletion and none of it went into the pointers.

Compare with [the 2016 security checklist](../2016/08-security-best-practices-kubernetes-deployment.md),
which is the same genre two years earlier. That post carries an editor's note from the project
saying its recommendations are no longer current, without saying which ones, and its exercise is a
classification: sort the eight items into what broke, what was wrong when written, and what is
untouched. This post carries no such note, and it does not need one, because almost nothing in it
is wrong. The failure is one level down, in the apparatus, and no editor's note would have caught
it.

**The ladder** — the workaround in item 8 is retired by a Pod field, and the gate that put that
field in the API is `Sysctls`:

| stage | default | locked | releases |
|---|---|---|---|
| beta | `true` | — | v1.11 – v1.20 |
| stable | `true` | — | v1.21 – v1.22 |

`Sysctls.md` declares `removed: true`, and its body is one sentence: "Enable support for namespaced
kernel parameters (sysctls) that can be set for each pod." There is no `alpha` row in the file. The
gate was already beta and on by default at **v1.11**, and `manifest.tsv` dates the v1.11 release
announcement 2018-06-27 and the v1.12 one 2018-09-27 — so v1.11 was the current release on the day
this post went up, and `spec.securityContext.sysctls` was available to the author. What was not
available was the *particular* parameter that matters here: `sysctl-cluster.md:78` dates
`net.ipv4.ip_unprivileged_port_start` into the safe set at **1.22**, eleven releases after the gate
reached beta, and the manifest dates the v1.22 announcement 2021-08-04 — three years after the post.
The mechanism preceded the post; the entry that makes the mechanism answer the post's problem did
not.

The same setting is moving again, and the second gate is one release old at this pin:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.37 – |

`DefaultPodSysctls` has no `toVersion` and no `removed`. Its body: "Enables the `defaultPodSysctls`
field in KubeletConfiguration, allowing Node administrators to specify a default set of namespaced
kernel parameters (sysctls) that the `kubelet` applies to all Pods on the Node." The arc runs from
*not settable at all*, through *settable per Pod by whoever writes the Pod* from v1.11, to
*settable per Node by whoever runs the kubelet* — and the third step is alpha and off in the release
this tree is pinned at.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair). Steps 1 to 6 need no cluster at all,
only the pinned checkout; steps 7 to 12 need one worker, because the bind test has to land on a
node and the sysctl has to be applied by a kubelet. A single-node cluster would do, but the
`restricted` label test in step 10 is clearer when the namespace is not the one the control plane
lives in.

**Do**

1. Resolve the post's eight `/docs/` links against the pinned checkout. For each path, look for
   both `content/en/<path>.md` and `content/en/<path>/_index.md`, and record which of the eight
   resolve to a file:

   ```sh
   cd /path/to/pinned/website/content/en
   for p in \
     docs/tasks/administer-cluster/securing-a-cluster \
     docs/admin/authorization/rbac \
     docs/tasks/debug/debug-cluster/audit \
     docs/tasks/tls/certificate-rotation \
     docs/tasks/administer-cluster/encrypt-data \
     docs/concepts/policy/pod-security-policy \
     docs/concepts/services-networking/network-policies \
     docs/admin/admission-controllers
   do
     if [ -f "$p.md" ] || [ -f "$p/_index.md" ]; then echo "OK   $p"; else echo "DEAD $p"; fi
   done
   ```

2. Look for the redirects. A moved Hugo page keeps its old address as an `aliases:` entry in the
   new page's front matter, so if the two `/docs/admin/` pages moved rather than vanished, some
   page claims those paths:

   ```sh
   grep -rn '/docs/admin/' /path/to/pinned/website/content/en/docs --include='*.md'
   ```

3. Find out where the three dead paths still exist in the tree, and what kind of file each one is:

   ```sh
   for s in admin/authorization/rbac admin/admission-controllers concepts/policy/pod-security-policy; do
     printf '\n== %s\n' "$s"; grep -rl "$s" /path/to/pinned/website/content/en
   done
   ```

4. Resolve the ninth link, the blog cross-reference at `:53`. Take the canonical URL for that post
   out of the census manifest and compare it character by character with what the post wrote:

   ```sh
   grep 'rbac-support-in-kubernetes' blogwalk/manifest.tsv | cut -f7
   ```

5. Ask the cluster for the object the post asks you to create, three ways — the resource list, the
   API groups, and the explain endpoint:

   ```sh
   kubectl api-resources | grep -i podsecurity
   kubectl api-versions | grep -i policy
   kubectl explain podsecuritypolicy
   ```

6. Measure how much of that object the replacement declines to answer for. Count the field rows in
   the mapping reference's first table and the ones that answer with *No opinion*:

   ```sh
   D=/path/to/pinned/website/content/en/docs
   F="$D/reference/access-authn-authz/psp-to-pod-security-standards.md"
   sed -n '28,232p' "$F" | grep -c '<td><code>'
   sed -n '28,232p' "$F" | grep -ci 'no opinion'
   ```

7. Now the workaround. Create a namespace and apply the post's Service from `:182-194` exactly as it
   is printed, with the selector and both ports unchanged:

   ```sh
   kubectl create namespace hardening
   kubectl -n hardening apply -f - <<'EOF'
   kind: Service
   apiVersion: v1
   metadata:
     name: my-service
   spec:
     selector:
       app: MyApp
     ports:
     - protocol: TCP
       port: 443
       targetPort: 8443
   EOF
   kubectl -n hardening get service my-service -o yaml
   ```

8. Build the Pod the post's item 8 asks for — non-root, no escalation, no capabilities — and have
   it try to bind the port the post says it cannot:

   ```sh
   kubectl -n hardening apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: lowport
   spec:
     securityContext:
       runAsNonRoot: true
       runAsUser: 1000
       seccompProfile: {type: RuntimeDefault}
     containers:
     - name: bind
       image: busybox
       command: ["sh", "-c", "nc -l -p 443 || sleep 3600"]
       securityContext:
         allowPrivilegeEscalation: false
         capabilities: {drop: [ALL]}
   EOF
   kubectl -n hardening logs lowport
   kubectl -n hardening exec lowport -- sh -c 'nc -l -p 443'
   ```

9. Delete that Pod and re-apply it with one field added — the Pod-level sysctl the safe set gained
   at 1.22 — then run the same bind:

   ```sh
   kubectl -n hardening delete pod lowport
   kubectl -n hardening apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: lowport
   spec:
     securityContext:
       runAsNonRoot: true
       runAsUser: 1000
       seccompProfile: {type: RuntimeDefault}
       sysctls:
       - name: net.ipv4.ip_unprivileged_port_start
         value: "443"
     containers:
     - name: bind
       image: busybox
       command: ["sh", "-c", "sleep 3600"]
       securityContext:
         allowPrivilegeEscalation: false
         capabilities: {drop: [ALL]}
   EOF
   kubectl -n hardening exec lowport -- sh -c 'nc -l -p 443 & sleep 1; netstat -ltn | grep 443'
   kubectl -n hardening exec lowport -- cat /proc/sys/net/ipv4/ip_unprivileged_port_start
   ```

10. Turn on the strictest enforcement the project ships and re-apply the same Pod, to find out
    whether the workaround's replacement is itself allowed:

    ```sh
    kubectl label namespace hardening \
      pod-security.kubernetes.io/enforce=restricted \
      pod-security.kubernetes.io/warn=restricted
    kubectl -n hardening delete pod lowport
    kubectl -n hardening apply -f - <<'EOF'
    apiVersion: v1
    kind: Pod
    metadata:
      name: lowport
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        seccompProfile: {type: RuntimeDefault}
        sysctls:
        - name: net.ipv4.ip_unprivileged_port_start
          value: "443"
      containers:
      - name: bind
        image: busybox
        command: ["sh", "-c", "sleep 3600"]
        securityContext:
          allowPrivilegeEscalation: false
          capabilities: {drop: [ALL]}
    EOF
    ```

11. Change one character of that Pod — the sysctl name — to another entry from the same safe set,
    and apply it into the same labelled namespace:

    ```sh
    kubectl -n hardening apply -f - <<'EOF'
    apiVersion: v1
    kind: Pod
    metadata:
      name: rmem
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        seccompProfile: {type: RuntimeDefault}
        sysctls:
        - name: net.ipv4.tcp_rmem
          value: "4096 87380 6291456"
      containers:
      - name: bind
        image: busybox
        command: ["sh", "-c", "sleep 3600"]
        securityContext:
          allowPrivilegeEscalation: false
          capabilities: {drop: [ALL]}
    EOF
    ```

12. Measure the two lists that step 11 has just set against each other. The node-level safe set is
    the bulleted list at `sysctl-cluster.md:74-87`; the admission-level allow list is inside the
    `restricted` table at `pod-security-standards.md:317-326`:

    ```sh
    D=/path/to/pinned/website/content/en/docs
    sed -n '74,87p' "$D/tasks/administer-cluster/sysctl-cluster.md" | grep -c '^- `'
    sed -n '317,326p' "$D/concepts/security/pod-security-standards.md" | grep -c '<li><code>'
    ```

**Expect** — step 1: five of the eight resolve and three do not. The three failures are
`docs/admin/authorization/rbac`, `docs/concepts/policy/pod-security-policy` and
`docs/admin/admission-controllers`, which is one link from item 2, one from item 6 and one from
item 10 — one in Part One and two in Part Two, with Part Three, the projection into the future,
the only part that still resolves in full. Note what the five survivors are: `securing-a-cluster`,
`audit`, `certificate-rotation`, `encrypt-data`, `network-policies`. Four of the five are task
pages under `docs/tasks/`, and the
paths that broke were both under a top-level `/docs/admin/` prefix that no longer exists. The link
rot is not random; it is one reorganisation.

Step 2 prints nothing. That is the finding, and it is worth pausing on: an `aliases:` entry is
cheap, it is the mechanism this site uses for exactly this case, and it was not used here. Anyone
following the post from a search result gets a 404 rather than the current page, and there is
nothing in the tree that would ever have changed that.

Step 3 returns one file for each of the first two searches, and that file is the post itself. For
the third, five files, all of them under `blog/_posts/`. Read this back against step 1: the address
`/docs/concepts/policy/pod-security-policy/` is written in five places in the pinned tree and
documented in none of them. The blog archive is the only surviving record of where the project used
to keep this page, which makes the archive a source of dead links about itself.

Step 4: the manifest's URL is `https://kubernetes.io/blog/2017/04/rbac-support-in-kubernetes/`. The
post wrote `http://kubernetes.io/blog/2017/04/rbac-support-in-kubernetes.html`. The path segment is
identical; the scheme and the trailing `.html` are not. This is a fourth broken pointer and it is
a different failure from the other three — the target still exists, at an address the site's own URL
scheme stopped producing. Nine links, four broken, and no two broken for the same reason.

Step 5: `api-resources` prints nothing matching, `api-versions` prints `policy/v1` and no
`policy/v1beta1`, and `kubectl explain` fails outright rather than reporting a deprecated type.
Compare this with the shape of a *deprecated* object: there is no warning header, no annotation on
the field, no note in the response. The API server does not tell you the object used to exist. The
only thing in the pin that says so is documentation, and the page carrying that news is at a path
the post does not link to.

Step 6: 25 and 13. Read the 13 rows: the mapping is a careful document that says, for over half the
fields the post's object could set, that the replacement takes no position. Add the four annotation
rows and their two, and 15 of 29 mappings decline. This is the shape of the census row's claim that
Pod Security Admission "replaced it with a different enforcement model rather than a renamed
object", made measurable: a rename would have mapped every field.

Step 7: the Service is accepted unchanged, and `get -o yaml` shows `port: 443` and
`targetPort: 8443` exactly as printed. Three of the post's four Kubernetes manifests still apply
without an edit — this Service and both NetworkPolicies — and only the `PodSecurityPolicy` fragment
has nowhere to go. But this one is the only one whose *reason for existing* expired: the post prints
it because non-root containers cannot bind low ports and "services can be used to disguise this
fact". The snippet survived; its justification did not.

Step 8: the Pod is admitted and `nc -l -p 443` fails. The `exec` prints
`nc: bind: Permission denied` and exits non-zero. Two things are being demonstrated at once, and
they should be separated. The post attributes the failure to `CAP_NET_BIND_SERVICE`, and that
attribution was already incomplete when it was written — the capability is one of two gates on a low
bind, and this Pod fails both, because it drops all capabilities *and* runs above the unprivileged
port floor. A container that keeps `NET_BIND_SERVICE` binds 443 as UID 1000 without any sysctl at
all — but the Pod the post's own item 8 asks for drops every capability, so that route is closed by
following the post. What is left is the other gate, and that is the one this exercise moves.

Step 9: the same image, the same user, the same dropped capabilities, and the bind succeeds.
`netstat` shows a listener on `:443`, and `/proc/sys/net/ipv4/ip_unprivileged_port_start` reads
`443` inside the Pod while the node's own value is unchanged. This is the whole retirement of item
8's workaround in one field: the Service indirection existed to hide the port floor, and the floor
is now a Pod-level setting. Note also that nothing was granted to the container to make this work —
no capability was added back, the seccomp profile is still `RuntimeDefault`, and the process is
still UID 1000. The post's advice was *be non-root*; the pin's answer is *be non-root, and move the
boundary instead of the port*.

Step 10: the Pod is admitted with the `restricted` label in force. Expect no warning and no
rejection. `net.ipv4.ip_unprivileged_port_start` is one of the ten entries in the `restricted`
standard's allow list at `pod-security-standards.md:317-326`, so the strictest profile the project
publishes permits the field that retires the post's workaround. The Pod in step 9 was written to
pass `restricted` on purpose — `runAsNonRoot`, `allowPrivilegeEscalation: false`,
`capabilities: {drop: [ALL]}`, `seccompProfile: RuntimeDefault` — which is the post's item 8
checklist restated as an admission rule. The post's advice is not merely still current; it is the
enforced default profile.

Step 11 is rejected. The message names the namespace's `restricted:latest` policy and the
`forbidden sysctl` by name. `net.ipv4.tcp_rmem` is in the node-level safe set — the kubelet will
apply it without `--allowed-unsafe-sysctls` — and it is not in the admission-level allow list.
Two lists, both called safe, disagreeing about the same parameter.

Step 12: **14** and **10**. The safe set has fourteen entries; the `restricted` allow list has ten.
The four the safe set has and admission does not are the four most recently added:
`net.ipv4.tcp_rmem` and `net.ipv4.tcp_wmem` (1.32), and `net.ipv4.tcp_slow_start_after_idle` and
`net.ipv4.tcp_notsent_lowat` (1.37, this pin's own release). The disagreement is not a
disagreement about safety; it is latency. One list is maintained in the task page and the other in
the standards page, and the standards page's newest dated entry is 1.29 while the safe set carries
entries from 1.32 and from 1.37. The safe-set list itself, and
what "safe" means to a kubelet, belongs to
[the IPVS exercise](04-ipvs-in-cluster-load-balancing.md), which measures it for a different reason.

**Read on** — four questions, three of them answerable in the pinned tree:

1. `deprecation-guide.md` says twice, in the future tense, that PodSecurityPolicy will be removed.
   Find the other removals on that page whose target release is at or below v1.36 and check their
   tense. Is the PodSecurityPolicy entry the exception, or is the whole page written as a plan and
   never revised? Answerable — the page is one file.
2. Item 5 says the symmetric encryption keys "are not automatically rotated". Read
   `encrypt-data.md` on the providers it tabulates and work out which half of that claim the pin has
   answered: which key in the hierarchy now rotates without an operator, which still does not, and
   which provider draws the line. Answerable.
3. The safe sysctl set and the `restricted` allow list differ by the four newest entries. Look for
   any statement in the tree that the two lists are meant to agree — a note, a cross-reference, a
   shared source file. If there is none, the two lists are independently maintained by design.
   Answerable, and the answer decides whether step 11's rejection is a bug or a policy.
4. The three broken `/docs/` paths got no `aliases:`. Was that a decision or an omission? Nothing in
   the pinned tree can say: the tree holds the outcome and not the reasoning. Answering it means
   leaving the pin, which is what the pin is for — noticing where a question stops being a
   documentation question.

**Teardown** — `kubectl delete namespace hardening`, which takes the Service and both Pods with it.
The namespace labels go with the namespace. Nothing was changed on any node: the sysctl in step 9
was set inside the Pod's network namespace by the kubelet and does not outlive it, so
`cat /proc/sys/net/ipv4/ip_unprivileged_port_start` on the worker reads whatever it read before.
Confirm that before you stop, because it is the difference between a Pod-level sysctl and the
node-level one `DefaultPodSysctls` is being built to set.
