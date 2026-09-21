<a id="pod-security-admission-beta"></a>

# The gate that switched this on is gone, the configuration file this post builds will not start an API server on the pin, an unlabelled namespace is still `privileged` because the plan quoted here never shipped, and the control the version pin exists for moved again eleven releases later

**Post** — [Kubernetes 1.23: Pod Security Graduates to
Beta](https://kubernetes.io/blog/2021/12/09/pod-security-admission-beta/), 2021-12-09, by Jim Angel
(Google) and Lachlan Evenson (Microsoft) — 783 lines, 33,830 bytes, the longest post this year's
census walks. A beta announcement with a full kind walkthrough bolted on: three namespaces at three
levels, then the cluster-wide configuration file that sets a default for namespaces nobody labelled.

**As written**

`:11` states the release fact: Pod Security is a built-in admission controller, beta in v1.23, that
evaluates pod specifications against the Pod Security Standards and either `admit`s or `deny`s.
`:13` states the succession: it replaces PodSecurityPolicy, `deprecated in the v1.21 release, and
will be removed in Kubernetes v1.25`. `:17` gives the motive — isolate workloads `without adding
extra third-party tooling`.

`:19-23` is the post's account of what was wrong with the thing being replaced, in three headings:
the policy authorization model, the risks around switching policies with no dry-run, and an
`Inconsistent and Unbounded API`. `:25` is the answer: levels that ship in the box rather than a
policy object each cluster writes for itself.

Then the post spends a paragraph on what the replacement deliberately cannot do. `:27` says Pod
Security `doesn't have complete feature parity with the deprecated PodSecurityPolicy` — no mutation,
`it doesn't have the ability to mutate or change Kubernetes resources to auto-remediate a policy
violation on behalf of the user`, and no fine-grained control over individual fields. `:29` turns
that into a principle: denying rather than mutating `requires resources to be updated in source
repositories, and tooling to be updated prior to being deployed to Kubernetes`.

`:33` places the controller: built in `starting with Kubernetes v1.22, but can also be run as a
standalone [webhook]`. The same sentence carries a broken link in the published source — a pointer
to `[specific](h/docs/concepts/security/pod-security-standards/#profile-details)`, with an `h` where
the leading slash should be.

`:39-42` names the three levels — `privileged`, `baseline`, `restricted` — and `:44-48` lists
example fields the strictest one restricts. `:50` names the two ways to apply them: labels on a
Namespace, and an `AdmissionConfiguration` file for `cluster-wide defaults and exemptions`. `:54-57`
names the three modes, `enforce`, `audit`, `warn`. `:59` names the fourth dial: `In addition to
modes you can also pin the policy to a specific version (for example v1.22). Pinning to a specific
version allows the behavior to remain consistent if the policy definition changes in future
Kubernetes releases.` `:143` repeats it, and `:145-152` gives the two recommended uses of `warn`,
ending on a sequencing fact: `if enforce fails, the entire sequence fails before evaluating the
warn`.

The walkthrough starts at `:61-67` with prerequisites — kind, kubectl, a container runtime — and
`:72` creates the cluster with `kind create cluster --image kindest/node:v1.23.0`. `:99` is the
first check, and it is asked of the running API server rather than of any document:

```
kubectl -n kube-system exec kube-apiserver-kind-control-plane -it -- \
  kube-apiserver -h | grep "default enabled ones"
```

`:104-117` prints the answer — eighteen plugin names, `PodSecurity` fifth among them — and `:119`
concludes: `PodSecurity is listed in the group of default enabled admission plugins.` `:123-129`
then proves admission end to end with `--dry-run=server` against a namespace labelled `restricted`,
and `:134` prints the rejection in full, the one that begins `violates PodSecurity
"restricted:latest"`.

`:139-141` gives the two label forms, `:164` gives the workload — a busybox running `sleep 1000000`
— and `:168-475` walks all three levels with it: privileged admits, baseline admits, restricted
rejects at `:373`. The restricted case then goes further than most walkthroughs do. The pod is fixed
to satisfy the standard and *still* fails, at `:411-418`, with `CreateContainerConfigError`; `:427`
prints the kubelet event `container has runAsNonRoot and image will run as root`; `:430` explains
the choice — `set the effective UID (runAsUser) to a non-zero (root) value or use the nobody UID
(65534)` — and `:437-462` is the pod that finally runs, with `runAsUser: 65534`. `:477-488` is an
aside that inspects the container with `crictl`.

`:490-536` is the part of this post nothing else in the archive covers. `:496` is blunt about the
constraint: `There is no runtime configurable API for the AdmissionConfiguration configuration
file`, and `:500` adds that `It's not recommended to alter control plane / clusters after install`.
`:511-533` is the file itself — an `AdmissionConfiguration` whose `PodSecurity` plugin configuration
is `pod-security.admission.config.k8s.io/v1beta1`, with `defaults` of `enforce: baseline`, `audit:
baseline`, `warn: restricted`, and `exemptions` carrying three empty arrays and `namespaces:
[kube-system]`. `:541-565` mounts it into a kind control plane through `kubeadmConfigPatches` and
points `--admission-control-config-file` at it.

`:577-611` is the payoff: `kubectl describe namespace` shows no labels at all — the post writes
`Same.` — and the pods are judged anyway, by a default that lives in a file on the control plane.
`:658` is an honest correction mid-walkthrough, flagged `**UPDATE:**`, that `The baseline policy
permits allowPrivilegeEscalation`, so the violation is retried with `hostNetwork`; `:683` prints the
rejection naming `host namespaces (hostNetwork=true)`, and `:686` celebrates.

`:693-708` reads `pod_security_evaluations_total` straight off `/metrics`, sample lines and all,
including one with `resource="controller"`. `:720-756` covers auditing, and `:730` quotes the
enhancement proposal for where this was going: a future where `baseline` `could be the default for
unlabeled namespaces`. `:758-768` summarises migration off PodSecurityPolicy in four steps and
points at the migration guide; `:768` notes that migration *tooling* was `Listed as "optional future
extensions" and currently out of scope`. `:774` hands the reader on to `dedicated tutorials` for
cluster level and namespace level, and `:776-783` lists the concept page, the two task pages, the
KEP, and the April 2021 deprecation post.

**As it runs now** — the feature is so completely arrived that the switch announced here no longer
exists, and the file the post spends its last third building is rejected by the API server it was
written for.

**The gate was retired three releases after this post.**
`reference/command-line-tools-reference/feature-gates/PodSecurity.md` declares `removed: true`: one
release at alpha, two at beta, three at stable, gone at v1.28. There is no longer anything to
enable. The post's title verb — *graduates* — describes a six-release passage through a switch that
a reader on the pin cannot find, cannot set, and never needed.

**The check at `:99` still works, and its answer is half again as long.** The string `default
enabled ones` is still in the API server's help text, so the command runs unchanged on any cluster.
What comes back is different: `reference/command-line-tools-reference/kube-apiserver.md:531` carries
that help text at the pin, and its parenthesis holds twenty-seven names against the post's eighteen.
Nine were added and none were removed — `ValidatingAdmissionPolicy`, `MutatingAdmissionPolicy`,
`ClusterTrustBundleAttest`, `JobValidation`, `NodeDeclaredFeatureValidator`, `PodGroupProtection`,
`PodGroupWorkloadExists`, `PodResizeValidator`, `PodTopologyLabels`. `PodSecurity` is still there,
and admission has grown half again around it.

**And the page the post calls the best way to confirm now disagrees with the flag.** `:96` links
`admission-controllers.md#which-plugins-are-enabled-by-default`. At the pin that section is
`reference/access-authn-authz/admission-controllers.md:119-130`, and the list it prints on `:130`
holds nineteen names — the post's eighteen plus `ValidatingAdmissionPolicy`. It is eight short of
the flag help on the same commit. The post's instinct was right and its reason was wrong: asking the
binary beats asking the page not because the page is hard to find, but because the page falls
behind.

**The configuration file is two API versions behind, and the docs date it precisely.**
`pod-security.admission.config.k8s.io` went `v1alpha1` in v1.22, `v1beta1` in v1.23 and v1.24, `v1`
from v1.25. `tasks/configure-pod-container/enforce-standards-admission-controller.md:29-33` and
`tutorials/security/cluster-level-pss.md:211-215` carry the same note, and it does not offer
instructions for the older versions — it offers *links to older documentation sites*,
`v1-24.docs.kubernetes.io` and `v1-22.docs.kubernetes.io`. The post's `:517` is correct only on a
web site that is no longer the one you are reading.

**Everything else in that file is now the documentation's file.** Diff the post's `:511-532` against
`enforce-standards-admission-controller.md:36-67` and four things differ: the `apiVersion` line, the
three default levels, the `namespaces` array, and a block of explanatory comments the docs added.
The rest is identical, down to `# Array of authenticated usernames to exempt.` and the ordering of
`usernames`, `runtimeClasses`, `namespaces`. This post's YAML did not get superseded; it got
promoted.

**The defaults inverted, and the pin documents them twice with two different answers.** The post
configures `enforce: baseline`, `audit: baseline`, `warn: restricted` — a cluster that refuses the
obviously dangerous by default. The task page at `:53-58` configures `privileged` for all three,
which is a file that changes nothing. The tutorial at `cluster-level-pss.md:196-203` configures
`enforce: baseline`, `audit: restricted`, `warn: restricted`. Two pages, one pin, one YAML
structure, and the question *what should an unlabelled namespace get* answered in opposite
directions. The task page's own comment settles which is normative: `:46` marks `"privileged"` as
`(default)`, which is what the API server uses when no file is supplied at all.

**The future `:730` quotes never arrived.** The enhancement proposal's rollout of `baseline` as the
default for unlabelled namespaces is not in the pin: `privileged` is still what a namespace with no
label gets, twelve releases and five years later. The escape hatch the post describes — a
cluster-wide file that raises the floor — is still the *only* way to raise it, and it is still the
thing `:496` says you cannot configure at runtime.

**The standalone webhook is a dead link in both directions.** `:33` sends the reader to
`pod-security-admission/#webhook`. `concepts/security/pod-security-admission.md` is 148 lines at the
pin and has no `Webhook` heading; its `:44` still opens `Once the feature is enabled or the webhook
is installed`, pointing at a thing the page stopped describing. The other broken link in that same
sentence — `h/docs/concepts/security/pod-security-standards/#profile-details` — is still in the
published source, unfixed after five years.

**The control the version pin exists for moved again, eleven releases after this post.**
`concepts/security/pod-security-standards.md` lists eleven controls under Baseline at the pin, and
the seventh of them is `Host Probes / Lifecycle Hooks (v1.34+)` at `:171`: the `host` field in
liveness, readiness and startup probes, and in lifecycle hooks, must not be set. A namespace pinned
to `baseline` with `enforce-version: latest` acquired that restriction on upgrade to v1.34. A
namespace pinned to `v1.23` did not. That is precisely the mechanism `:59` promises, demonstrated by
a control that did not exist when the promise was made — and the post's own file pins everything to
`latest`.

**The metrics did not move at all.** The same three counters are at
`concepts/security/pod-security-admission.md:132-137` and `reference/instrumentation/metrics.md`
`:3374`, `:3381` and `:3388`, and all three are still `ALPHA`. The help string the post prints at
`:699` is character for character the string at `metrics.md:3382`. The feature went alpha, beta,
stable, and had its gate deleted; the way you watch it working is at the same stability level it was
on the day this post was published.

**The thing being replaced left two artifacts of very different sizes.**
`concepts/security/pod-security-policy.md` survives as a twenty-five-line tombstone whose alert says
PodSecurityPolicy was `removed from Kubernetes in v1.25`.
`tasks/configure-pod-container/migrate-from-psp.md` survives at 345 lines, with
`min-kubernetes-server-version: v1.22` in its front matter, still describing a migration off an API
that no supported release has carried for twelve releases. And `pod-security-standards.md:565-566`
still tells its reader that `As of July 2021, Pod Security Policies are deprecated` — the tense the
post used, kept past the removal it announced.

**The walkthrough itself became documentation.** `:774` points at `dedicated tutorials`, and at the
pin those are `tutorials/security/cluster-level-pss.md` (333 lines) and `ns-level-pss.md` (161
lines). The first is this post's last third with the API version corrected and the defaults changed:
same `mkdir -p /tmp/pss`, same `AdmissionConfiguration`, same `kubeadmConfigPatches`, same mount. A
blog post that closes by pointing at the docs that will replace it is unusual; this one is pointing
at a page that had not yet been written the way it now reads.

**The diff, and why** — the announcement was about a switch, and the switch is the only part
that did not survive.

**Broke: the configuration file.** Paste `:511-533` onto a v1.37 control plane and the API server
does not start. `pod-security.admission.config.k8s.io/v1beta1` was served for two releases and the
decoder has not recognised it since v1.25. This is the rare case where a blog post's code does not
merely produce a different result — it produces no cluster at all, and the failure mode is a control
plane that will not come back.

**Retired by being agreed with.** The body of that same file is now the documentation's canonical
example, comments included. So is the walkthrough: the cluster-level tutorial is this post's
structure. The post's argument for the feature — predefined levels beating a policy object each
cluster writes for itself — is not argued anywhere at the pin because nothing disputes it.

**Overtaken by stasis, twice.** The metrics are still alpha after fourteen releases. The default for
an unlabelled namespace is still `privileged` after twelve, so the `AdmissionConfiguration` file is
still load-bearing for exactly the reason the post says it is. Both are cases of the archive being
right in a way the author did not intend: the post is a good guide to the pin because the parts it
describes stopped moving.

**The plan the project abandoned.** `:730` cites the proposal's rollout of `baseline` by default for
unlabelled namespaces, and `:768` cites its migration tooling as an optional future extension.
Neither shipped. The second is a plan the post already labels as out of scope; the first is a plan
the post presents as a direction of travel, and the pin has not travelled.

**Still right, and worth saying because it reads like a caveat.** `:27` and `:29` are the two
sentences that have aged best: no mutation, no per-field control, deny-and-fix-in-source. Every one
of those is still true at the pin, and the third is the reason the other two are not defects.
`pod-security-admission.md:86-88` adds the consequence the post shows but never states — enforce
mode is `**not** applied to workload resources, only to the resulting pod objects` — which is why a
bad Deployment is accepted and its Pods are not.

**Never absorbed: the standalone webhook.** Mentioned at `:33`, linked to an anchor that does not
exist, and referred to once more by the concept page's own first sentence. Whatever the webhook is
now, the pinned documentation does not say.

**The ladder**

One gate, transcribed from its `stages:` list parsed as YAML, plus the file-level flag that ends it.

```
PodSecurity  alpha  false  1.22 - 1.22
             beta   true   1.23 - 1.24
             stable true   1.25 - 1.27
             removed: true
```

Six releases end to end, one of them at alpha. `locked` never appears. Measured across the pin's
feature-gate directory, 230 gate files declare `removed: true`, and 147 of those carry the full
alpha-beta-stable ladder; their median life is eight releases, so `PodSecurity` is on the quick side
— 28 of the 147 were shorter and 23 took exactly as long. The single alpha release is not unusual
either: 72 of the 147 spent exactly one release there. What is worth noticing is the company it
kept. Nine of those 147 gates opened their alpha stage at v1.22, and two of them are already in this
year's census: `SeccompDefault` in [the seccomp exercise](06-seccomp-default.md) and
`ReadWriteOncePod` in [the access-mode exercise](07-read-write-once-pod-access-mode-alpha.md). Three
of the eleven posts this year walks announced a v1.22 alpha gate that has since been deleted, which
is a fair description of what v1.22 was for.

The gate's body text is one line — `Enables the PodSecurity admission plugin.` — and it is the whole
story of the diff. The gate governed the *plugin*, never the policy. When it was deleted at v1.28
nothing about levels, labels, modes or versions changed; the plugin simply stopped being optional.
Everything this post teaches is still true and none of it is reachable through the switch the post
is announcing.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`, 4096MB, 4
CPUs, 25G, brought up with [the five provision steps](../../strands/lab-topologies.md#provision).
Admission happens in the API server, so a second node would watch and contribute nothing. One node
is also the safer choice for what this exercise does: steps 4 and 5 stop the API server on purpose,
by feeding it the post's own configuration file, and on `solo` the machine you have to repair is the
machine you are already on. Keep a shell open on the node throughout — `kubectl` is unavailable for
part of this, and `crictl` is how you find out why.

**Do**

1. Ask the running API server the post's question at `:99`, and count the answer. The exec target is
   a static Pod name that depends on your node's hostname, so look it up rather than typing it:

   ```sh
   kubectl version -o json | grep gitVersion
   CP=$(kubectl -n kube-system get pod -l component=kube-apiserver -o name | head -1)
   echo "$CP"
   kubectl -n kube-system exec ${CP#pod/} -- kube-apiserver -h 2>/dev/null \
     | tr -d '\n' | sed 's/.*default enabled ones (//; s/).*//' \
     | tr ',' '\n' | sed 's/^ *//' | tee /tmp/psa-flag.txt | wc -l
   grep -n PodSecurity /tmp/psa-flag.txt
   kubectl get --raw /metrics | grep -c '^pod_security_' || echo 0
   kubectl get --raw /metrics | grep -c 'kubernetes_feature_enabled{name="PodSecurity"' || echo 0
   ```

Four answers to write down: the release, the number of default-enabled plugins, the position of
`PodSecurity` in that list, and the two counts. The last one is the one to be sure about — a gate
that has been deleted is not reported as `false`, it is not reported at all.

2. Ask the pinned documentation the same question twice, and compare all three answers. The blog
   post is in the same checkout as the docs, so the post's own list can be extracted rather than
   retyped:

   ```sh
   W=/path/to/pinned/website/content/en/docs
   B=/path/to/pinned/website/content/en/blog/_posts
   ext() { tr -d '\n' | sed 's/.*default enabled ones (//; s/).*//' | tr ',' '\n' | sed 's/^ *//' | sort; }
   sed -n '104,118p' $B/2021/pod-security-admission-beta.md | ext > /tmp/psa-post.txt
   sed -n '130p'     $W/reference/access-authn-authz/admission-controllers.md \
     | tr ',' '\n' | sed 's/^ *//' | sort > /tmp/psa-page.txt
   sort /tmp/psa-flag.txt > /tmp/psa-flag-sorted.txt
   wc -l /tmp/psa-post.txt /tmp/psa-page.txt /tmp/psa-flag-sorted.txt
   echo "--- in the flag, not on the page"; comm -13 /tmp/psa-page.txt /tmp/psa-flag-sorted.txt
   echo "--- on the page, not in the flag"; comm -23 /tmp/psa-page.txt /tmp/psa-flag-sorted.txt
   echo "--- added since the post";         comm -13 /tmp/psa-post.txt /tmp/psa-flag-sorted.txt
   echo "--- dropped since the post";       comm -23 /tmp/psa-post.txt /tmp/psa-flag-sorted.txt
   ```

Three counts and four lists. The second `comm` should be empty and the fourth should be empty too;
the first and third should not. `:96` calls the page `the best way to confirm the API's default
enabled plugins` and then ignores its own advice by asking the binary. Say in one sentence why the
post was right to, using the size of the first list as the evidence.

3. Establish what an unlabelled namespace gets on a cluster with no cluster-wide configuration,
   which is the state every kubeadm cluster starts in:

   ```sh
   sudo grep -c admission-control-config-file /etc/kubernetes/manifests/kube-apiserver.yaml || echo 0
   kubectl create namespace psa-cluster
   kubectl get namespace psa-cluster -o jsonpath='{.metadata.labels}'; echo
   kubectl -n psa-cluster run hostnet --image=registry.k8s.io/pause:3.10 --restart=Never \
     --overrides='{"spec":{"hostNetwork":true}}'
   kubectl -n psa-cluster get pod hostnet -o wide
   ```

No flag, no labels, and a Pod in the host network namespace admitted without comment. That is
`privileged`, and it is the default the enhancement proposal quoted at `:730` was going to replace
with `baseline`. Record the Pod's IP: it is the node's.

4. Install the post's configuration file exactly as `:511-533` writes it, and watch the control
   plane refuse it. Two things make this safe to do deliberately: the backup you take first, and the
   fact that `/etc/kubernetes/pki` is already mounted into the API server's static Pod at the same
   path, so the file needs no volume stanza and the manifest needs no edit beyond one flag:

   ```sh
   sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/kube-apiserver.yaml.bak
   sudo mkdir -p /etc/kubernetes/pki/psa
   sudo tee /etc/kubernetes/pki/psa/pod-security.yaml >/dev/null <<'YAML'
   apiVersion: apiserver.config.k8s.io/v1
   kind: AdmissionConfiguration
   plugins:
   - name: PodSecurity
     configuration:
       apiVersion: pod-security.admission.config.k8s.io/v1beta1
       kind: PodSecurityConfiguration
       defaults:
         enforce: "baseline"
         enforce-version: "latest"
         audit: "baseline"
         audit-version: "latest"
         warn: "restricted"
         warn-version: "latest"
       exemptions:
         usernames: []
         runtimeClasses: []
         namespaces: [kube-system]
   YAML
   sudo sed -i '/- kube-apiserver$/a\    - --admission-control-config-file=/etc/kubernetes/pki/psa/pod-security.yaml' \
     /etc/kubernetes/manifests/kube-apiserver.yaml
   sleep 20
   kubectl get --raw /readyz; echo
   sudo crictl ps -a --name kube-apiserver
   sudo crictl logs --tail 20 $(sudo crictl ps -a --name kube-apiserver -q | head -1) 2>&1 | tail -20
   ```

Copy the error line in full. It names the version it could not decode. `:496` says there is no
runtime configurable API for this file; what that sentence does not say, and what this step shows,
is the shape of the failure when the file is wrong — not a rejected request, not a degraded cluster,
but an API server that will not come up.

5. Change one line and watch it start. Do not restore from the backup yet — the flag is correct,
   only the file is not:

   ```sh
   sudo sed -i 's#pod-security.admission.config.k8s.io/v1beta1#pod-security.admission.config.k8s.io/v1#' \
     /etc/kubernetes/pki/psa/pod-security.yaml
   sudo crictl rm -f $(sudo crictl ps -a --name kube-apiserver -q | head -1)
   sleep 30
   kubectl get --raw /readyz; echo
   kubectl -n psa-cluster delete pod hostnet --ignore-not-found
   kubectl -n psa-cluster run hostnet --image=registry.k8s.io/pause:3.10 --restart=Never \
     --overrides='{"spec":{"hostNetwork":true}}'
   kubectl get namespace psa-cluster -o jsonpath='{.metadata.labels}'; echo
   ```

The same namespace, still carrying no labels at all, now refuses the same Pod. Copy the rejection
and note which policy version it names. This is the post's `:577-611` reproduced without kind: the
namespace description is unchanged, and the judgement comes from a file on disk.

6. Compare the three sets of defaults the same YAML structure is documented with, by running two of
   them. Start with the task page's:

   ```sh
   sudo sed -i 's/enforce: "baseline"/enforce: "privileged"/; s/audit: "baseline"/audit: "privileged"/; s/warn: "restricted"/warn: "privileged"/' \
     /etc/kubernetes/pki/psa/pod-security.yaml
   sudo crictl rm -f $(sudo crictl ps -a --name kube-apiserver -q | head -1); sleep 30
   kubectl -n psa-cluster run hostnet2 --image=registry.k8s.io/pause:3.10 --restart=Never \
     --overrides='{"spec":{"hostNetwork":true}}'
   sudo sed -i 's/enforce: "privileged"/enforce: "baseline"/; s/audit: "privileged"/audit: "restricted"/; s/warn: "privileged"/warn: "restricted"/' \
     /etc/kubernetes/pki/psa/pod-security.yaml
   sudo crictl rm -f $(sudo crictl ps -a --name kube-apiserver -q | head -1); sleep 30
   kubectl -n psa-cluster run hostnet3 --image=registry.k8s.io/pause:3.10 --restart=Never \
     --overrides='{"spec":{"hostNetwork":true}}'
   sed -n '36,67p' $W/tasks/configure-pod-container/enforce-standards-admission-controller.md
   sed -n '188,210p' $W/tutorials/security/cluster-level-pss.md
   ```

One file, three published sets of defaults, two of them run here. The first admits everything and is
what the task page prints; the second rejects and warns and is what the tutorial prints; the post's
own sits between them. Diff the post's block against the task page's and list what actually differs
— it is fewer lines than you expect.

7. Find the two edges of enforcement the post demonstrates without naming. First the workload
   resource, then the exemption:

   ```sh
   kubectl -n psa-cluster create deployment hostnet-deploy --image=registry.k8s.io/pause:3.10 \
     --dry-run=client -o yaml > /tmp/hd.yaml
   sed -i 's/^      containers:/      hostNetwork: true\n      containers:/' /tmp/hd.yaml
   kubectl -n psa-cluster apply -f /tmp/hd.yaml
   kubectl -n psa-cluster get deploy,rs,pod
   kubectl -n psa-cluster describe rs | sed -n '/Events/,$p'
   kubectl -n kube-system run exempt --image=registry.k8s.io/pause:3.10 --restart=Never \
     --overrides='{"spec":{"hostNetwork":true}}'
   kubectl get --raw /metrics | grep '^pod_security_exemptions_total'
   ```

The Deployment is accepted, its ReplicaSet is not able to create a Pod, and the reason arrives as a
warning and an event rather than an error on your `apply`. `pod-security-admission.md:86-88` is the
rule. The `kube-system` Pod is admitted for a different reason, and the counter is the proof of
which reason.

8. Put the version pin to work on a control that did not exist when the post recommended it.
   `pod-security-standards.md:171` adds Host Probes and Lifecycle Hooks to Baseline at v1.34:

   ```sh
   kubectl create namespace psa-pinned; kubectl create namespace psa-latest
   kubectl label namespace psa-pinned pod-security.kubernetes.io/enforce=baseline \
     pod-security.kubernetes.io/enforce-version=v1.23
   kubectl label namespace psa-latest pod-security.kubernetes.io/enforce=baseline \
     pod-security.kubernetes.io/enforce-version=latest
   kubectl get ns psa-pinned psa-latest -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.labels}{"\n"}{end}'
   cat > /tmp/probe-pod.yaml <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata:
     name: probe
   spec:
     containers:
     - name: c
       image: registry.k8s.io/pause:3.10
       livenessProbe:
         httpGet: {host: 127.0.0.1, port: 8080, path: /}
   YAML
   for NS in psa-pinned psa-latest; do
     echo "--- $NS"
     kubectl -n $NS apply --dry-run=server -f /tmp/probe-pod.yaml
   done
   sed -n '170,190p' $W/concepts/security/pod-security-standards.md | sed 's/<[^>]*>//g' | grep -v '^ *$'
   ```

Record whether the older pin is accepted as a label value at all, and what each namespace does with
the same Pod. `:59` says pinning `allows the behavior to remain consistent if the policy definition
changes in future Kubernetes releases`; this is that sentence eleven releases later, with a specific
control attached to it. Then answer the question the post does not ask: every file it writes pins to
`latest`, so what did the post's own configuration inherit in v1.34?

9. Read the three counters the post reads, and one it does not:

   ```sh
   kubectl get --raw /metrics | grep '^# HELP pod_security'
   kubectl get --raw /metrics | grep '^pod_security_evaluations_total' | sort
   kubectl get --raw /metrics | grep '^pod_security_exemptions_total\|^pod_security_errors_total'
   grep -n 'pod_security_evaluations_total' -A 3 $W/reference/instrumentation/metrics.md | grep -i 'stability\|metric_help'
   ```

Compare your `# HELP` lines with the post's `:699` and with `metrics.md:3382`: one of the three is a
copy of the other two. Then read `policy_level` and `policy_version` across your samples — between
step 6 and step 8 you have produced evaluations at three levels and two versions, and this counter
is the only place the cluster will tell you which policy actually judged a request.

10. Offline, in the pinned checkout, count what the post left behind and what it points at that is
    not there:

    ```sh
    cd /path/to/kubernetes/website
    grep -n 'h/docs/concepts' content/en/blog/_posts/2021/pod-security-admission-beta.md
    grep -c '^#* *Webhook' content/en/docs/concepts/security/pod-security-admission.md || echo 0
    grep -n 'webhook' content/en/docs/concepts/security/pod-security-admission.md
    wc -l content/en/docs/concepts/security/pod-security-policy.md \
          content/en/docs/tasks/configure-pod-container/migrate-from-psp.md \
          content/en/docs/tutorials/security/cluster-level-pss.md \
          content/en/docs/tutorials/security/ns-level-pss.md
    grep -n 'min-kubernetes-server-version' content/en/docs/tasks/configure-pod-container/migrate-from-psp.md
    grep -n 'As of July 2021' content/en/docs/concepts/security/pod-security-standards.md
    grep -rn 'v1-24.docs.kubernetes.io\|v1-22.docs.kubernetes.io' content/en/docs --include='*.md' | wc -l
    grep -rln 'pod-security.admission.config.k8s.io/v1$\|pod-security.admission.config.k8s.io/v1 ' \
      content/en/docs --include='*.md'
    ```

Six counts and three lists. The pair to sit with is the last two line counts against the first: the
page describing the removed API is twenty-five lines, the page describing how to leave it is 345,
and the two tutorials that replaced this post's walkthrough are longer than the tombstone and the
guide put together. Then find the `h` in the first grep, and say how long it has been there.

**Expect**

Step 1 prints a v1.37 server, a plugin count in the mid twenties, `PodSecurity` somewhere in the
middle of the list, three `pod_security_` series, and zero `kubernetes_feature_enabled` series for
`PodSecurity`. That last zero is the whole of the ladder made visible: the post's subject is a gate,
and the cluster has no opinion about it because there is nothing left to have an opinion about.

Step 2 should give you 18 names from the post, 19 from the docs page, and the same count the binary
gave you in step 1. The page's extra name over the post is `ValidatingAdmissionPolicy`, added once
and then left; the flag's extra names over the page are eight, and nothing has ever been taken away.
If your cluster is not on v1.37 the third number will differ and the first two will not — which is
itself the answer to why the post asks the binary.

Steps 4 and 5 are the pair this exercise is built on. Expect step 4 to leave you without an API
server: `kubectl` stops answering, `crictl ps -a` shows the container exiting and being recreated,
and the log names the unrecognised `pod-security.admission.config.k8s.io/v1beta1`. Expect step 5,
one `sed` later, to bring it back and to change the answer for a namespace nobody has labelled. The
Pod that was admitted in step 3 is refused in step 5 with a message naming `host namespaces`, which
is the same violation the post finally provokes at `:683` after the correction at `:658` — the post
reached it by trial and error, and so will you if you try `allowPrivilegeEscalation` first, because
`baseline` permits it.

Step 6 flips the same file twice. The all-`privileged` defaults from the task page admit `hostnet2`;
the tutorial's defaults refuse `hostnet3` and also warn about `restricted`, so expect a warning line
on a request that succeeded. The diff of the post's block against the task page's comes to four
differences, one of which is only comments.

Step 7 is the asymmetry. The Deployment is created — `kubectl apply` reports success and prints a
warning — the ReplicaSet exists, and no Pod does; the ReplicaSet's events carry the violation. The
`kube-system` Pod is admitted with no warning at all, and `pod_security_exemptions_total` increments
by one. If you exempt a namespace you get silence, not an audit line, which is what
`pod-security-admission.md:97-98` means by *ignored*.

Step 8 has two possible outcomes and both are worth having. If `v1.23` is accepted as a pin, the
pinned namespace admits the probe Pod and the `latest` namespace refuses it, and you have
demonstrated a policy divergence that opened at v1.34. If the older value is rejected or silently
normalised, record what the API server did with it and read the label back — `VERSION must be a
valid Kubernetes minor version, or latest` is the only constraint `pod-security-admission.md:74`
states, and how far back *valid* reaches is not stated anywhere at the pin.

Step 9's `# HELP` lines should match `metrics.md:3382` character for character, `[ALPHA]` included.
Step 10's line counts are 25, 345, 333 and 161, the `As of July 2021` grep returns one line, and the
`Webhook` heading count returns zero while the word `webhook` still appears on the page. The
archived-documentation links appear more than once, because the same compatibility note is carried
by two pages.

**Read on**

1. `concepts/security/pod-security-admission.md` is 148 lines and is the whole feature at the pin.
   Read `:42-78` for the labels, `:80-88` for the workload-resource rule, `:90-115` for exemptions
   including the caution about controller service accounts, `:117-126` for the pod fields whose
   updates are exempt from checks, and `:128-137` for the metrics. Then notice what is not there: no
   Webhook section, and no mention that any of this was ever a gate.

2. `tasks/configure-pod-container/enforce-standards-admission-controller.md` is 72 lines, and
   `tutorials/security/cluster-level-pss.md` is 333. The first is this post's file with the defaults
   neutralised; the second is this post's walkthrough with the defaults kept. Read them in that
   order and you can watch a blog post turn into documentation, including the comments.

3. `tasks/configure-pod-container/migrate-from-psp.md` is 345 lines about leaving an API that has
   not existed for twelve releases. `:13-15` is the dry-run, audit and warn approach the post
   summarises in four steps at `:758-768`, and `:31-40` is the numbered path, which begins by
   telling you to decide whether Pod Security Admission is the right fit at all. Read it beside the
   twenty-five-line `concepts/security/pod-security-policy.md`.

4. Three neighbours own the parts this exercise uses without explaining. [The 2016 security
   checklist](../2016/08-security-best-practices-kubernetes-deployment.md) owns the `PodSecurity`
   ladder as a replacement for a per-pod control and the shape of a `restricted` rejection. [The
   runc exercise](../2019/02-runc-cve-2019-5736.md) owns the three levels applied by label and the
   control inventory read as a table. [The eleven-ways
   exercise](../2018/06-11-ways-not-to-get-hacked.md) owns PodSecurityPolicy's removal and the
   field-by-field mapping. Release timing is in
   [`research/blog-era-translation.md`](../../research/blog-era-translation.md).

5. Unanswerable from the pin: why the default for an unlabelled namespace is still `privileged`.
   `:730` links the proposal section that planned to change it, the pin's documentation still prints
   `privileged` as `(default)`, and nothing between the two says the plan was dropped, deferred or
   reconsidered. The KEP is sig-auth 2579-psp-replacement and it is outside the pin. Two smaller
   ones go the same way: what became of the standalone webhook, mentioned twice and described
   nowhere; and how far back a version pin may reach before the API server stops honouring it.

**Teardown**

This exercise changed a control-plane manifest and created a file under `/etc/kubernetes/pki`, so
the teardown is a restore rather than a delete, and it has to be verified:

```sh
sudo cp /root/kube-apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml
sudo rm -rf /etc/kubernetes/pki/psa
sleep 30
kubectl get --raw /readyz; echo
sudo grep -c admission-control-config-file /etc/kubernetes/manifests/kube-apiserver.yaml || echo 0
kubectl delete namespace psa-cluster psa-pinned psa-latest --ignore-not-found
kubectl -n kube-system delete pod exempt --ignore-not-found
kubectl -n psa-cluster run after --image=registry.k8s.io/pause:3.10 --restart=Never \
  --overrides='{"spec":{"hostNetwork":true}}' 2>&1 | tail -1
kubectl get nodes
```

The flag count should be `0`, the namespace deletions should complete, and the last `run` should
fail because the namespace is gone rather than because a policy refused it — if it fails with a
`violates PodSecurity` message instead, the manifest did not restore and the API server is still
reading a file you deleted. No workload survives this and the node stays up for the next exercise in
this year.
