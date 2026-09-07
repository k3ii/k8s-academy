<a id="kubeadm-v18-released"></a>
# Every forecast in this post has been answered and none of them in its own terms: the feature it wanted to make the default is gone so completely that its name now belongs to the mechanism it was built to replace, the command it promised for v1.9 arrived four times under four other verbs, and the one-command upgrade is one command inside sixteen spread across two pages

**Post** — [kubeadm v1.8 Released: Introducing Easy Upgrades for Kubernetes Clusters](https://kubernetes.io/blog/2017/10/kubeadm-v18-released/),
2017-10-25, Kubernetes v1.8. Written by Lucas Käldström (Weaveworks), thirteen months after
[the post that announced the tool](../2016/09-how-we-made-kubernetes-easy-to-install.md).

**As written** — the post is a release note with a roadmap attached, and the roadmap is the longer
half. It announces four things and predicts three.

The headline is *"**one-command upgrades** of the control plane"*. You check first:

```
$ kubeadm upgrade plan
```

*"This gives you information about which versions you can upgrade to, as well as the health of your
cluster."* Then, if you want to see what an upgrade would do before it does it:

> You can examine the effects an upgrade will have on your system by specifying the --dry-run flag.
> In previous versions of kubeadm, upgrades were essentially blind in that you could only make
> assumptions about how an upgrade would impact your cluster. With the new dry run feature, there is
> no more mystery. You can see exactly what applying an upgrade would do before applying it.

And then you upgrade:

```
$ kubeadm upgrade apply v1.8.0
```

The second announcement is a feature gate, and it comes with a definition:

> Self-hosting in this context refers to a specific way of setting up the control plane. The
> self-hosting concept was initially developed by CoreOS in their bootkube project. […]
> Self-hosting means that the control plane components, the API Server, Controller Manager and
> Scheduler are workloads themselves in the cluster they run. This means the control plane
> components can be managed using Kubernetes primitives, which has numerous advantages. […] Rolling
> upgrades in Kubernetes can be used for upgrades of the control plane components, and next to no
> extra code has to be written for that to work; it's one of Kubernetes' built-in primitives!

```
$ kubeadm init --feature-gates=SelfHosting=true
```

*"Self-hosting won't be the default until v1.9.0, but users can easily test the feature in
experimental clusters."*

The third is modularity — *"The inclusion of the kubeadm alpha phase command supports our aim to
make kubeadm more modular, letting you invoke atomic sub-steps of the bootstrap process"* — with a
name attached to a date: *"We hope that we can graduate the command to beta as kubeadm phase in
v1.9.0."*

The fourth is the least advertised and takes one sentence: *"beginning with v1.8.0, kubeadm uploads
your configuration to a ConfigMap inside of the cluster, and later reads that configuration when
upgrading for a seamless user experience."* Alongside it, a graduation with a release number on it:
*"The first certificate rotation feature has graduated to beta in v1.8, which is great to see. […]
the Kubernetes node component kubelet can now rotate its client certificate automatically. We expect
this area to improve continuously."*

Between the announcements and the forecasts the post stops to draw a boundary, in a section called
*The scope of kubeadm*:

> kubeadm performs the actions necessary to get a minimum viable cluster up and running. It only
> cares about bootstrapping, not about provisioning machines, by design. Likewise, installing
> various nice-to-have addons by default like the Kubernetes Dashboard, some monitoring solution,
> cloud provider-specific addons, etc. is not in scope.

Then the forecasts, all three for v1.9: high availability as an alpha feature, `kubeadm phase` at
beta, and *"we want to make self-hosting the default way to deploy your control plane: Kubernetes
becomes much easier to manage if we can rely on Kubernetes' own tools to manage the cluster
components."*

Two of the post's own defects are worth noting before you start, because both are in the published
HTML and neither is yours. A section heading has collapsed into the paragraph above it, so the
sentence *"We wanted to add a lot of new features and improvements in this cycle, and we
succeeded.Upgrades along with better introspectability."* runs a full stop straight into a fragment
that was a title. And in the closing paragraph the word *meetings* has its individual letters
hyperlinked — `mee`**`t`**`i`**`n`**`g`**`s`** carries three separate links to the same Slack
channel, as does the lone `o` in *"or check out"* — which is what an editor's find-and-replace does
to a word when the pattern it matched was a single character.

**As it runs now** — `kubeadm upgrade plan` and `kubeadm upgrade apply` both work, do what the post
says they do, and are the commands the pinned documentation tells you to run. Everything else in
the post has moved, and the four kinds of movement are worth telling apart, because only the first
announces itself.

`kubeadm init --feature-gates=SelfHosting=true` **fails**, and fails at the gate name rather than
at anything about your cluster. `SelfHosting` is not a gate kubeadm has. It is not in the live table
on `docs/reference/setup-tools/kubeadm/kubeadm-init.md`, which holds exactly one row at the pin, and
it is not in the removed table beneath it, which holds eight —
[2016/09](../2016/09-how-we-made-kubernetes-easy-to-install.md) transcribes both in full, and
reading them for what is absent is the only use this exercise makes of them. So kubeadm's own
record of every gate it has ever offered does not remember offering this one.

`kubeadm phase` **is not a command**, and never was. What exists instead is `kubeadm init phase`,
`kubeadm join phase`, `kubeadm reset phase` and `kubeadm upgrade phase` — four reference pages under
`docs/reference/setup-tools/kubeadm/`, one per verb. `kubeadm init phase` appears 127 times across
the pinned documentation and `kubeadm join phase` 33; the string `kubeadm phase` appears twice, both
times as prose on `docs/tasks/administer-cluster/kubeadm/kubeadm-certs.md:108,110` rather than as a
command anybody is told to run. The forecast graduated four times over and never got its name.

`--dry-run` **survives and is undocumented where you would look for it.** The flag still exists:
`docs/reference/setup-tools/kubeadm/implementation-details.md:660-661` mentions it, in a subsection
about a different command — *"A more verbose way to do the same thing is running `kubeadm upgrade
apply --dry-run` or `kubeadm upgrade node --dry-run`"*, where *the same thing* is `kubeadm upgrade
diff`, a subcommand the post did not have. The string `--dry-run` occurs **zero** times on
`docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade.md`, the page you would actually follow to
perform an upgrade. The post gave the feature a five-sentence paragraph; the procedure gives it
nothing.

And the ConfigMap **is load-bearing**, which is the one prediction that came entirely true. The name
`kubeadm-config` appears in 59 files at the pin. `implementation-details.md:665-673` lists what
`kubeadm upgrade apply` does, and two of its five steps are reading and rewriting that ConfigMap and
its sibling `kubelet-config`.

The fourth kind of movement leaves no error at all, and it is the one this exercise spends most of
its steps on. `implementation-details.md` is the page whose stated job is to say what `kubeadm init`
does. At `:309` it opens a list — *"Other API server flags that are set unconditionally are:"* — and
the first entry is:

> - `--insecure-port=0` to avoid insecure connections to the api server
>
> — `docs/reference/setup-tools/kubeadm/implementation-details.md:311`

`--insecure-port` has **zero** occurrences in
`docs/reference/command-line-tools-reference/kube-apiserver.md`, a 75KB generated page that
enumerates every flag the API server accepts. It has zero occurrences anywhere else in the pinned
documentation: `implementation-details.md:311` is the string's only appearance in the tree. A Go
binary handed a flag its parser does not carry prints an error and exits, so an API server started
with that line does not start — which is checkable on your own cluster in about forty seconds, and
step 3 below checks it. Two flags above it are in the same condition: `--cloud-provider` and
`--cloud-config`, at `:305-307`, are likewise absent from `kube-apiserver.md`, and the page hedges
them itself — *"this is experimental, alpha and will be removed in a future version"* — a
parenthesis that has now outlasted the thing it was hedging.

The same list also carries a link that no longer lands. Of the eight admission plugins at
`:317-334`, seven link to headings that exist on
`docs/reference/access-authn-authz/admission-controllers.md`. The eighth,
`PersistentVolumeLabel` at `:325`, links to `#persistentvolumelabel`, and the plugin has no section
on that page — the string appears nowhere in the 42KB file. It is also the only one of the eight
whose entry predicts its own removal: *"This admission controller is deprecated and will be removed
in a future version."* The prediction was correct, the section went, and the link stayed.

**The diff, and why** — this post describes a plan the project abandoned, and reading it that way
requires care, because on the surface it looks like a post that came true. The command it advertises
still runs. The ConfigMap it mentions in passing is now the mechanism the upgrade path depends on.
High availability, the first of its three forecasts, shipped and is documented at
`docs/setup/production-environment/tools/kubeadm/high-availability.md`, reached via
`kubeadm init --control-plane-endpoint` and `kubeadm join --control-plane`. Nothing in the post
reads as embarrassing. What happened instead is that every forecast was answered by the same
pressure, and the pressure is stated in the post itself, two paragraphs after the forecast it
contradicts.

Self-hosting was a proposal about **where the control plane lives**, and the argument for it was
that living inside the cluster makes upgrades free: *"Rolling upgrades in Kubernetes can be used for
upgrades of the control plane components, and next to no extra code has to be written for that to
work."* That is a real and good argument. It also makes kubeadm's output a set of Deployments and
DaemonSets rather than five files in a directory, which means kubeadm's blast radius becomes the
cluster's own control loops, and a failed control-plane rollout becomes a failed rollout of the
thing that reconciles rollouts. The project went the other way. `kubeadm upgrade apply` at the pin
*"upgrades the control plane manifest files on disk in `/etc/kubernetes/manifests` and waits for the
kubelet to restart the components if the files have changed"* — five files and a directory watch.
The extra code the post hoped not to write was written; `kubeadm-upgrade.md` is 16KB of it seen from
the outside.

`kubeadm phase` as a top-level verb would have made phases composable — a phase is a thing you run,
and you assemble a bootstrap out of them. Phases as sub-nouns of `init`, `join`, `reset` and
`upgrade` are the opposite arrangement: you cannot run a phase, you can only run a phase *of* a verb
that already existed. The four `*-phase.md` pages are a deliberate narrowing, not an incomplete
graduation, and they all end the same way — each of the four carries a *See also* line pointing at
`kubeadm alpha`, the page whose body says there is nothing in it. Four signposts to an empty room,
which [2016/09](../2016/09-how-we-made-kubernetes-easy-to-install.md) found from the other
direction.

`--dry-run` was the post's answer to a real complaint, and it survived as a flag while losing its
place in the sentence. Its demotion is the most legible of the four, because you can see the
replacement: `kubeadm upgrade diff` does the same job under a name that says what it produces, and
`--dry-run` became the more verbose way to spell it. A feature that gets a better name loses its old
one slowly, in the pages nobody rewrote.

So: the two predictions that failed are the two that would have widened what kubeadm owns, and the
one that succeeded completely — the config ConfigMap — added nothing to kubeadm's remit at all. It
made kubeadm remember a decision you had already given it. The section that decided all three sits
between the announcements and the forecasts, and it was written by the same author in the same post:
*"kubeadm performs the actions necessary to get a minimum viable cluster up and running. It only
cares about bootstrapping."* A tool that publishes a scope will resolve its own roadmap against
that scope, and the roadmap and the scope were two screens apart.

The vocabulary is the part that did not resolve. *Self-hosted* survived the feature's cancellation
and was reassigned, and the pinned documentation now carries the word four times in three senses.
`docs/concepts/architecture/_index.md:161-175` lists four ways a control plane can be deployed and
makes two of them distinct entries:

> Static Pods
> : Control plane components are deployed as static Pods, managed by the kubelet on specific nodes.
>   This is a common approach used by tools like kubeadm.
>
> Self-hosted
> : The control plane runs as Pods within the Kubernetes cluster itself, managed by Deployments
>   and StatefulSets or other Kubernetes primitives.
>
> — `docs/concepts/architecture/_index.md:167-172`

That second entry is the post's definition, almost to the word, and it puts kubeadm on the other
side of the line. Two other concept pages put kubeadm on this side of it, in a sentence they share
verbatim:

> The main use for static Pods is to run a self-hosted control plane: in other words, using the
> kubelet to supervise the individual control plane components. For example, kubeadm uses static
> Pods to run `kube-apiserver`, `kube-controller-manager`, `kube-scheduler`, and `etcd` on control
> plane nodes.
>
> — `docs/concepts/workloads/pods/static-pods.md:16-20`, and again at
> `docs/concepts/workloads/pods/_index.md:423-427`

Three concept pages, two mutually exclusive definitions of one term, kubeadm named as the example on
both sides, and the definition that lost is the one printed twice. The fourth occurrence,
`docs/reference/access-authn-authz/admission-controllers.md:108`, uses the word about webhooks and is
a third sense again. Meanwhile the strings `SelfHosting`, `self-hosting` and `bootkube` occur
**zero** times in the whole tree. The feature is gone without a trace and its name is in three
places, because a cancelled feature stops compiling and a word does not.

The ladder belongs to the post's smallest verifiable claim — *"The first certificate rotation feature
has graduated to beta in v1.8"* — and it takes two tables, because *this area* turned out to be two
gates that went opposite ways.

`RotateKubeletClientCertificate`:

| stage | default | locked | releases |
|---|---|---|---|
| beta | `true` | — | v1.8 – v1.18 |
| stable | `true` | — | v1.19 – v1.21 |

with `removed: true` declared at file level.

`RotateKubeletServerCertificate`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.7 – v1.11 |
| beta | `true` | — | v1.12 – |

The first table confirms the post exactly: beta at v1.8, the release the post is announcing, which
is the only claim in the piece that carries a version number and can be checked against the gate
tree. It then went stable at v1.19 and was removed at v1.21, and the removal was clean — the string
`RotateKubeletClientCertificate` occurs nowhere in the pinned documentation outside its own gate
file. Client certificate rotation is now simply what the kubelet does, configured by the
`rotateCertificates` field.

The second table has no end. `RotateKubeletServerCertificate` has been beta since v1.12 and is beta
at v1.37 — twenty-six minor releases in one stage, and *"enabled by default"* for all of them, which
is what makes the stasis invisible rather than merely long. The reason it never moved is written down
in the same place as the feature:

> The CSR approving controllers implemented in core Kubernetes do not approve node *serving*
> certificates for security reasons. To use `RotateKubeletServerCertificate` operators need to run a
> custom approving controller, or manually approve the serving certificate requests.
>
> — `docs/reference/access-authn-authz/kubelet-tls-bootstrapping.md:450-456`

The gate is on by default and enables a request that core Kubernetes has decided, on purpose, not to
answer. That is not a stalled promotion; it is a feature whose last mile was ruled out of scope by a
different SIG, and the gate has sat at beta for twenty-six releases because there is nothing left to
promote it *to*. The post's *"We expect this area to improve continuously"* met a design refusal,
not a backlog — and the same page still dates the whole business by the post's own release, in a
sentence whose floor has never been raised:

> Kubernetes v1.8 and higher kubelet implements features for enabling rotation of its client and/or
> serving certificates. Note, rotation of serving certificate is a __beta__ feature and requires the
> `RotateKubeletServerCertificate` feature flag on the kubelet (enabled by default).
>
> — `docs/reference/access-authn-authz/kubelet-tls-bootstrapping.md:427-430`

Twenty-nine minors after v1.8, *v1.8 and higher* is still the version the page names, and the word
*beta* beside it is still accurate.

One page-level fact bears on the gates without being a ladder. `kubeadm-init.md:137` states the rule
its own tables run on — *"Feature gates are removed after a feature graduates to GA."* Two rows of
the removed table beneath it were removed without graduating at all: `PublicKeysECDSA` (alpha 1.19,
no beta, no GA, removed 1.37) and `UpgradeAddonsBeforeControlPlane` (alpha 1.28, no beta, no GA,
removed 1.31). The table is transcribed in
[2016/09](../2016/09-how-we-made-kubernetes-easy-to-install.md); the rule above it is the new
observation, and it is the rule under which `SelfHosting` would have had to appear somewhere. It
appears nowhere, which means the gate was withdrawn before the page that tracks withdrawals existed
to track it.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair): a control-plane node at
`10.10.10.130` and one worker at `10.10.10.131`. Two nodes is the smallest cluster on which the
post's headline claim can be counted rather than believed, because the control-plane procedure and
the worker procedure are two different pages at the pin and a single-node cluster only ever sends you
to the first one.

Provision with the five steps at [`#provision`](../../strands/lab-topologies.md#provision), then run
[the node baseline](../../strands/lab-topologies.md#node-baseline-steps) on **both** nodes — and
stop before `kubeadm init`, because step 1 below runs against a machine that has kubeadm and no
cluster. Then `ssh zain@10.10.10.130`.

**This is the one exercise in the tree that does not install the newest minor**, and the deviation is
the subject rather than a shortcut: an upgrade needs somewhere to come from. Read the current minor
where the baseline's step 0 sends you, subtract one, and use *that* in the two lines of the baseline
that name `$V` — the package repository URL and the `apt-get install` — on both nodes. Everything
else in the baseline is unchanged. You will spend the second half of this exercise walking the
cluster forward one minor by hand, which is the only way to hold the post's sentence and the
procedure in view at the same time.

**Do**

1. Before any cluster exists, run the post's gate command as printed, with `--dry-run` so it cannot
   half-build anything:

   ```
   sudo kubeadm init --feature-gates=SelfHosting=true --dry-run
   ```

   Record the error text verbatim and say which part of the command line it objects to. Then open
   `kubeadm-init.md`'s two tables at the pin and answer a narrower question than "is the gate there":
   given the rule printed at `:137`, which of the two tables would `SelfHosting` have to be in, and
   what does its absence from both mean about when it was withdrawn?
   [2016/09](../2016/09-how-we-made-kubernetes-easy-to-install.md) holds both tables; do not
   re-transcribe them.

2. Build the cluster at one minor behind: `kubeadm init` on `10.10.10.130` with
   `--pod-network-cidr=10.244.0.0/16`, Flannel, then join the worker. Now read what `kubeadm init`
   wrote:

   ```
   sudo cat /etc/kubernetes/manifests/kube-apiserver.yaml
   ```

   Take the six flags listed at `implementation-details.md:311-316` under *"Other API server flags
   that are set unconditionally are:"* and mark each one present or absent in the file, copying the
   value where it is present. Do not stop at the first absence. Then do the same for
   `--cloud-provider` and `--cloud-config` at `:305-307`.

3. Now take the page at its word. Add the line it says is set unconditionally to the manifest's
   command list:

   ```
   sudo cp /etc/kubernetes/manifests/kube-apiserver.yaml ~/apiserver.yaml.bak
   sudo sed -i '/- kube-apiserver/a\    - --insecure-port=0' /etc/kubernetes/manifests/kube-apiserver.yaml
   ```

   Then watch, from the same node, in this order: `kubectl get nodes`, then
   `sudo crictl ps -a --name kube-apiserver`, then the exited container's log via
   `sudo crictl logs <id>`. Record the exact error string and say which process printed it. Note what
   the kubelet is doing between your edit and your reading, and how you can tell. Then put the file
   back — `sudo cp ~/apiserver.yaml.bak /etc/kubernetes/manifests/kube-apiserver.yaml` — and time how
   long `kubectl get nodes` takes to answer again. Nothing here needs `kubectl` to be working, which
   is the point of doing it in that order.

4. Follow the eight admission-plugin links at `implementation-details.md:317-334` to
   `admission-controllers.md`, one at a time, and find the one that lands on no heading. Then read
   what that entry says about itself that no other entry says, and answer: which happened first, the
   removal it predicted or the link that was supposed to describe it?

5. Run the name the post forecast, then the names that exist:

   ```
   kubeadm phase --help
   kubeadm init phase --help
   kubeadm join phase --help
   kubeadm reset phase --help
   kubeadm upgrade phase --help
   ```

   Count the verbs that carry `phase` and say what a top-level `kubeadm phase` would have let you do
   that these four do not. Then open any one of the four reference pages under
   `docs/reference/setup-tools/kubeadm/` and read its *See also* list to the end;
   [2016/09](../2016/09-how-we-made-kubernetes-easy-to-install.md) already ran the command that
   settles where it points.

6. Change the package repository on the control-plane node to the current minor and install the new
   `kubeadm` only — not the kubelet, not kubectl. Then run the post's first command and the two the
   post did not have:

   ```
   sudo kubeadm upgrade plan
   sudo kubeadm upgrade diff
   sudo kubeadm upgrade apply v<current>.<patch> --dry-run
   ```

   Compare the last two outputs and say what `--dry-run` adds. Then search
   `kubeadm-upgrade.md` — the page the pin sends you to for this procedure — for the flag the post
   devoted a paragraph to, and record the number of hits.

7. Count the procedure before you run it. On `kubeadm-upgrade.md`, count the fenced command blocks
   for the Debian path on a single control-plane node, from *Determine which version to upgrade to*
   through *Verify the status of the cluster*. Do not count the CentOS/RHEL/Fedora tabs, the block
   that shows expected output, or the two blocks under *For the other control plane nodes*. Then
   count the same way on `docs/tasks/administer-cluster/kubeadm/upgrading-linux-nodes.md`, which is
   where the page sends you for the worker. Add them. Then find the one block that is the post's
   one-command upgrade, and name the step in between the two counts that has no command at all.

8. Now actually do it: the full control-plane procedure to the current minor, then the full worker
   procedure. Then check what the upgrade wrote rather than what it printed:

   ```
   kubectl get nodes -o wide
   kubectl get cm -n kube-system kubeadm-config -o yaml
   sudo grep image: /etc/kubernetes/manifests/kube-apiserver.yaml
   ```

   Say which of those three the post predicted in one sentence, and which one is the post's
   self-hosting argument answered by other means.

9. Read `docs/concepts/architecture/_index.md:161-175`, then
   `docs/concepts/workloads/pods/static-pods.md:16-20`. Decide which of the first page's four
   deployment models the cluster you just upgraded matches. Then answer whether the control plane
   you upgraded in step 8 is self-hosted, once from each page, and say which of the two answers the
   post would have given.

10. On the control-plane node, check where certificate rotation actually stands on the cluster in
    front of you:

    ```
    sudo grep -E 'rotateCertificates|serverTLSBootstrap' /var/lib/kubelet/config.yaml
    sudo ls /var/lib/kubelet/pki/
    kubectl get csr
    ```

    Then read `kubelet-tls-bootstrapping.md:427-430` and the note at `:450-456`, and answer: which
    of the two rotations is switched on here, and which of the two gates in the ladder above is the
    one you cannot finish enabling no matter what you set?

**Expect**

Step 1: `kubeadm` rejects the gate name itself, before any preflight check about ports or
directories — the objection is to `SelfHosting`, not to the machine. Record the wording; the
question the step asks is answerable from `kubeadm-init.md` alone. The rule at `:137` says gates are
removed *after* GA, so a gate that was withdrawn should appear in the removed table with blanks in
its Beta and GA columns, exactly as `PublicKeysECDSA` and `UpgradeAddonsBeforeControlPlane` do.
`SelfHosting` is in neither table, so it left before that table began recording departures.

Step 2: **`--insecure-port` is not in the manifest.** That one is certain, and it is certain by
deduction rather than by prediction: the flag is absent from the API server's own exhaustive flag
reference, so a running API server was not given it. The other seven are yours to record. This
exercise deliberately does not tell you what they are, because the pin does not settle them — a
generated flag reference says what the binary accepts, not what kubeadm passes — and an expectation
that guesses is the failure this whole tree exists to catch. Write down what you find; it is the
input to step 3 and to nothing else.

Step 3: the API server exits, the kubelet notices the manifest changed and creates the container
again, it exits again, and the loop continues for as long as the line is in the file. `kubectl get
nodes` fails with a connection error against `10.10.10.130:6443` rather than an authorization error
— the difference matters, because it tells you the process is gone rather than refusing you.
`crictl ps -a` shows the container in `Exited` with a recent finish time and an incrementing attempt
count; its log holds a single line naming the flag it could not parse. So the sentence at
`implementation-details.md:311` is not merely stale: followed literally, on the page whose subject is
what `kubeadm init` does, it prevents the cluster from existing. Recovery takes a few seconds after
you restore the file, and needs no `systemctl` and no `kubeadm` — the kubelet's directory watch is
the whole mechanism, which is also the mechanism `kubeadm upgrade apply` uses in step 8.

Step 4: seven of the eight land on a heading. `PersistentVolumeLabel` does not; the string is absent
from `admission-controllers.md` entirely. It is also the only one of the eight whose entry carries
*"This admission controller is deprecated and will be removed in a future version"*, so the list
predicted the removal, the section was deleted, and the link outlived both. The removal happened
first, which is the ordinary case: a page is edited by whoever owns it, and nothing walks the tree
afterwards asking who was pointing at the heading that went.

Step 5: `kubeadm phase` is not a command and the error says so. Four verbs carry `phase` as a
sub-noun, and each of the four pages ends with a *See also* line pointing at `kubeadm alpha`. The
thing a top-level `kubeadm phase` would have allowed is composition — a bootstrap assembled out of
phases in an order you chose, including orders no verb implements. What shipped is a phase you can
only run *inside* one of four verbs, which is a narrower feature wearing the same word, and it
shipped four times.

Step 6: `kubeadm upgrade plan` prints the current version, the version you can go to, a component
table and a component-config table. `kubeadm upgrade diff` prints a unified diff of the static Pod
manifests. `--dry-run` prints that diff plus everything else the apply would do, which is what
`implementation-details.md:660-661` means by *"a more verbose way to do the same thing."* And the
count on `kubeadm-upgrade.md` is **zero**. The flag the post said removed the mystery from upgrades
is on no page that tells you how to upgrade.

Step 7: **ten** blocks on the control-plane page under that counting rule, **six** on the worker
page, **sixteen** for a two-node cluster — and the two pages are reached by a link, so the second six
are invisible from the first page until you get to the bottom of it. The post's one-command upgrade
is block five of the ten, `sudo kubeadm upgrade apply`. The step with no command at all is *"Manually
upgrade your CNI provider plugin"*, which sends you to the addons page to find out whether your CNI
needs anything. The post's sentence is true about the command and was never a claim about the
procedure; what it could not have foreseen is that the control plane would turn out to be the cheap
part, and that the package manager, the drain, the kubelet, the CNI and the per-node repetition —
none of them inside the command — would be the rest.

Step 8: the upgrade succeeds and `kubectl get nodes -o wide` shows the new version on both nodes,
the control plane first. `kubeadm-config` records the new version, which is the post's single-sentence
prediction working exactly as described — it is the reason `kubeadm upgrade apply` needed no flags
carrying your original choices. The `image:` line in the manifest has a new tag, and nothing you ran
restarted the API server: the file changed and the kubelet did the rest, the same mechanism you drove
by hand in step 3. That is the post's self-hosting argument — *"next to no extra code has to be
written"* — answered by writing the code. `kubeadm upgrade` is that code, and it is a file rewrite
plus a directory watch rather than a rolling update.

Step 9: your cluster is the second entry, *Static Pods*. `architecture/_index.md` therefore says it
is **not** self-hosted, and `static-pods.md` says running a control plane this way is the main use of
static Pods and calls it self-hosted, naming kubeadm in both places. The post would have said no:
its definition is the one at `:170-172`, word for word, and by that definition the control plane you
upgraded is not self-hosted and never was. The two pages are not ambiguous about the same thing, they
are precise about different things, and the term now has to be read off whichever page you arrived
from.

Step 10: `rotateCertificates: true` is present, `serverTLSBootstrap` is absent, `/var/lib/kubelet/pki/`
holds `kubelet-client-current.pem` and a self-signed serving pair, and `kubectl get csr` shows the
bootstrap CSRs for both nodes in `Approved,Issued`. Client rotation is on and has no gate to turn
on — its gate went stable and was removed, which is what a finished feature looks like. Server
rotation is the one you cannot finish: setting `serverTLSBootstrap: true` makes the kubelet request a
serving certificate, and no controller in core Kubernetes will approve it, by the deliberate decision
recorded at `:450-456`. So the gate that is beta and on by default is the gate whose feature cannot
complete, and the gate that is gone is the one that worked. That self-signed serving pair is also
what [the 2015 monitoring exercise](../2015/02-resource-usage-monitoring-kubernetes.md) has to
patch `--kubelet-insecure-tls` around before `metrics-server` will start: a design refusal in one
year's post is another year's failed rollout.

**Read on** — two questions the corpus answers and this exercise did not ask. `kubeadm-init.md`'s
description of `RootlessControlPlane` — the single live gate in kubeadm's namespace, alpha since 1.22
and deprecated since 1.31 — configures *"the kubeadm deployed control plane component static Pod
containers"* to run as non-root. Read it and say what the only surviving kubeadm gate takes for
granted about where the control plane lives, and whether a self-hosted control plane could have had
that gate at all. Then read `docs/setup/best-practices/node-conformance.md:29-31`, which tells you to
*"use `http://localhost:8080` as the URL of the API server"* — the port this post's recap paragraph
says was closed in v1.6 — and settle from the surrounding sentence whether that instruction is a
leftover or a correct statement about a different API server than the one you have been upgrading.
The answer is in the clause immediately before it, and getting it right is the difference between a
finding and a false alarm.

**Teardown** — [`#teardown`](../../strands/lab-topologies.md#teardown). The cluster is one minor
behind nothing by the end of step 8, so it is an ordinary current-minor `pair` and could be kept —
but it has been upgraded in place rather than installed, and every later exercise assumes a cluster
that was installed, so take it down.
