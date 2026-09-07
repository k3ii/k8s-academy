<a id="kubeadm-ha-v115"></a>

# The commands staged under `kubeadm alpha` moved up so completely that the staging area is now an empty page that five other pages link to, the config format this post releases cannot be read by the migration command it recommends, and the CA rotation it forecasts never landed

**Post** — [Automated High Availability in kubeadm v1.15: Batteries Included But
Swappable](https://kubernetes.io/blog/2019/06/24/kubeadm-ha-v115/), 24 June 2019, by Lucas Käldström
(Weaveworks) and Fabrizio Pandini (independent). 214 lines, 15,271 bytes. No `slug:`, so the URL is
the filename; no `k8s` field either, and the version is in the title. `:10-12` carries an editor's
note recording that Käldström was writing as SIG Cluster Lifecycle co-chair and both authors as
`kubeadm` subproject owners.

This is a release note with a roadmap bolted on, and the roadmap is what has aged. Three things are
announced — HA to beta, certificate management, a new config format — and each one is followed by a
sentence about what comes next. Seven years later two of those sentences came true so thoroughly
that the thing they described is gone, one was quietly dropped, and one is still exactly where the
post left it.

**As written** — scope, then three announcements, then a plan, then a logo.

`:14-24` is the frame: kubeadm bootstraps "minimum viable clusters that are fully compliant with
Certified Kubernetes guidelines", has been under SIG Cluster Lifecycle since 2016, went GA at the
end of 2018, and the team is "now focused on the stability of the core feature set". `:26-48`
defines the scope by exclusion: kubeadm's reach is "limited to the local machine's filesystem and
the Kubernetes API"; `kubeadm init` makes control plane nodes and `kubeadm join` joins workers;
infrastructure provisioning, third-party networking, non-critical add-ons and cloud provider
integrations are all out of scope and belong to other projects, Cluster API among them.

`:54-97` is the headline. `:56` announces that "automated support for High Availability clusters is
graduating to Beta in kubeadm v1.15", and the workflow is the familiar one "with the only difference
that you have to pass the `--control-plane` flag to `kubeadm join`" (`:60`). `:62-64` links a
three-minute asciinema screencast. `:69-85` is the recipe in three steps: set up an external load
balancer, which "is out of scope of kubeadm" though "The community will provide a set of reference
implementations for this task" (`:69-71`); run `kubeadm init` "with small modifications" — create a
config file, set `controlPlaneEndpoint` in it, and run `sudo kubeadm init
--config=kubeadm-config.yaml --upload-certs` (`:72-75`); then run `kubeadm join --control-plane`
whenever you like (`:76-85`). `:87-95` names the four mechanisms that make it work: automated
certificate transfer via `--upload-certs`, "an explicit opt-in feature"; a dynamically-growing
stacked etcd cluster; concurrent joining in any order; and an upgrade flow where `kubeadm upgrade
apply` on the first node is followed by `kubeadm upgrade node` on the rest. `:97` adds that a new
test suite exists to keep it stable.

`:100-128` is certificate management. `kubeadm upgrade` now rotates all certificates automatically
(`:104`); `--certificate-renewal=false` opts out, after which you renew by hand with `kubeadm alpha
certs renew` (`:106`); and a new `kubeadm alpha certs check-expiration` reports expiry, with ten
rows of sample output at `:116-125` under a four-column header at `:115`: `CERTIFICATE`, `EXPIRES`,
`RESIDUAL TIME`, `EXTERNALLY MANAGED`. `:128` is the forecast, and it is two forecasts in one
sentence: "more work around certificate management in kubeadm in the next releases, with the
introduction of ECDSA keys and with improved support for CA key rotation", followed by "the commands
staged under `kubeadm alpha` are expected to move top-level soon".

`:131-151` is the config format, and it is the section with an argument rather than a changelog.
Flags do not scale: hard to maintain past thirty of them, hard to upgrade, limited to key-value, and
imperative where the rest of Kubernetes is declarative (`:136-139`), and the problem is general —
"some components have 150+ flags" (`:141`) — so kubeadm is "pioneering the ComponentConfig effort"
with a declarative versioned file. `:149` releases **v1beta2**, promises that v1beta1 "will still
continue to work for several releases", and names `kubeadm config migrate` as the way across. `:151`
looks forward to graduating the schema "to General Availability `v1`" during the course of the year.

`:153-166` is the 2019 plan: GA for the config format, HA to stable, better automatic certificate
rotation, and then four improvement areas — Windows nodes joining a kubeadm cluster with end-to-end
tests, better upstream CI signal for HA and upgrades, consolidated artifact building, and "Utilize
Kustomize to allow for advanced, layered and declarative configuration". `:166` is careful: "We make
no guarantees that these deliverables will ship this year though, as this is a community effort."
`:169-176` announces that kubeadm has a logo, chosen from nineteen options by a public poll with 386
answers. `:178-214` is contributing links and thanks.

**As it runs now** — the mechanism the post announces is intact. Almost every sentence it writes
about the *future* has either landed so hard that the thing it describes is now an empty room, or
never landed at all. This is a post to score rather than to correct.

**The forecast that came true too completely.** `:128` says "the commands staged under `kubeadm
alpha` are expected to move top-level soon". They moved. `kubeadm alpha certs` has **zero hits in
the whole pinned documentation tree**; `kubeadm certs renew` has twenty, across seventeen files.
What is left behind is stranger than a redirect: `kubeadm-alpha.md` still exists, nineteen lines
long, still carrying a caution that "`kubeadm alpha` provides a preview of a set of features made
available for gathering feedback from the community. Please try it out and give us feedback!"
(`kubeadm-alpha.md:7-9`) — and then, at `:12`, the whole body of the page: "Currently there are no
experimental commands under `kubeadm alpha`." Five other pages still link to it as the place "to try
experimental functionality" (`kubeadm-init-phase.md:178`, `kubeadm-join-phase.md:80`,
`kubeadm-reset-phase.md:49`, `kubeadm-upgrade-phase.md:43`) or "to preview a set of features"
(`reference/setup-tools/kubeadm/_index.md:33`). The staging area outlived everything that was ever
staged in it.

**The post's own sample output has a successor, and it is older than the post's.** `:114-126` pastes
ten rows of `kubeadm alpha certs check-expiration` under four columns, every row expiring `May 15,
2020` with `364d` residual. The pin's equivalent is `kubeadm-certs.md:150-167`: same command without
the `alpha`, the same ten certificate names in the same order, a fifth column `CERTIFICATE
AUTHORITY` inserted before `EXTERNALLY MANAGED`, a second table beneath listing `ca`, `etcd-ca` and
`front-proxy-ca` expiring `Dec 28, 2029` with `9y` residual — and `EXTERNALLY MANAGED` rendered `no`
rather than the post's `false`. Its rows expire `Dec 30, 2020`, also at `364d`, so by their own
residual times the blog's paste was taken around May 2019 and the documentation's around December
2019 — seven months newer, and six and a half years old at this pin. Both of them are also
incomplete in the same way: `reference/setup-tools/kubeadm/kubeadm-certs.md:19-38` lists twelve
renewal tabs — an `all` and eleven named certificates — and the eleventh certificate is
`super-admin.conf` (`:37`), which appears in neither sample output.

**The config format this post releases cannot be read by the command this post recommends.** `:149`
announces v1beta2 and names `kubeadm config migrate` as the migration path. Both halves are now
false together. `kubeadm.k8s.io/v1beta2` has **zero hits** in the pinned tree;
`reference/config-api/` holds only `kubeadm-config.v1beta3.md` and `kubeadm-config.v1beta4.md`. And
the migration chain is written down, twice: `kubeadm-config.v1beta4.md:67-70` records that v1.15
migrates v1beta1 to v1beta2, v1.22 dropped v1beta1 and migrates v1beta2 to v1beta3, "kubeadm v1.27.x
and newer no longer support v1beta2 and older APIs", and v1.31 migrates v1beta3 to v1beta4. Against
that, `implementation-details.md:90-92`: "The kubeadm tool only supports migrating from deprecated
configuration formats to the current format." v1beta2 is not deprecated at this pin, it is
unsupported, so a v1beta2 file written on the day this post was published now has no automated route
forward at all. The window in which the post's advice worked ran from v1.22 to v1.26 — five releases
— and it shut at v1.27, ten releases before this pin.

**And the page describing that command disagrees with itself about how many formats it can read.**
`generated/kubeadm_config/kubeadm_config_migrate.md:19-21` states the supported set as a one-item
list: "In this version of kubeadm, the following API versions are supported:" followed by "-
kubeadm.k8s.io/v1beta4". Two lines later, `:23`: "Further, kubeadm can only write out config of
version "kubeadm.k8s.io/v1beta4", but read both types." Both of what? One list, one item. Either the
list is short by a row and v1beta3 is still readable, or the sentence is a leftover from when it was
true and v1beta3 is not. Nothing else on the page settles it, and neither does
`kubeadm-config.v1beta4.md:70`, which says only that v1.31 and newer "can be used to migrate from
v1beta3 to v1beta4" without saying whether v1.37 still is. A command settles it, so one is in *Do*.

**The GA the post expects "During the course of the year" has not arrived in twenty-two of them.**
`:151` looks forward "to graduate the schema to General Availability `v1`", and `:157` repeats it as
the first 2019 deliverable, `kubeadm.k8s.io/v1`. Searching the pin for that exact string returns
eleven files and fifty-eight hits — which is exactly the sum of the twelve `v1beta3` hits and the
forty-six `v1beta4` hits, because every one of them is a prefix match. There is no
`kubeadm.k8s.io/v1`. The newest format is `v1beta4`, still being extended:
`kubeadm-config.v1beta4.md` records `httpEndpoints` added in v1.35 (`:11-21`), `ECDSA-P384` added to
`encryptionAlgorithm` in v1.34 (`:22-25`), and `UpgradeConfiguration.plan.EtcdUpgrade` in v1.33
(`:26-30`). That growth has outrun the reference page that documents its commands:
`generated/kubeadm_config/` holds `kubeadm_config_print_reset-defaults.md` and
`kubeadm_config_print_upgrade-defaults.md`, and `kubeadm-config.md:40-66` includes neither, so two
generated pages sit in the tree with nothing rendering them. Both sentences that promise GA also
have a stray trailing backtick in the published post (`:151`, `:157`), which is a small thing but a
durable one: the post is served with the typo.

**The graduation to stable was never announced, because the page that would announce it has no
maturity label.** `:56` graduates HA to Beta and `:157` plans "graduating this super-easy High
Availability flow to stable". The pin's HA page,
`setup/production-environment/tools/kubeadm/high-availability.md`, is 448 lines and says neither.
Grep it for maturity words and you get three hits, none of them about HA: `apiVersion:
kubeadm.k8s.io/v1beta4` at `:302`, `kubernetesVersion: stable` at `:304`, and a link to the
config-api reference at `:180`. There is no sentence anywhere on that page saying HA is beta, or
stable, or anything. This is the diff case where nothing broke and nothing was fixed: the feature
simply stopped being described in maturity terms at all, and no reader arriving today could tell
that its status was ever a question.

**The three-step recipe is now a two-step recipe.** `:72-75` requires a config file, because
`controlPlaneEndpoint` was a field before it was a flag: create `kubeadm-config.yaml`, set the
field, then `sudo kubeadm init --config=kubeadm-config.yaml --upload-certs`. The pin at
`high-availability.md:166` does it in one line with no file at all: `sudo kubeadm init
--control-plane-endpoint "LOAD_BALANCER_DNS:LOAD_BALANCER_PORT" --upload-certs`. The post's path
still works, but taking it now costs something the post could not have warned about —
`high-availability.md:179-183` notes that "The `kubeadm init` flags `--config` and
`--certificate-key` cannot be mixed", so a config-file user has to set `certificateKey` inside the
file under both `InitConfiguration` and `JoinConfiguration: controlPlane`. The post's own `--config`
invocation is on the far side of that prohibition.

**Two places spell the field as if it were a type.** The field is `controlPlaneEndpoint`, lower
camel, and the post gets it right at `:73`. The pin has it right in four files and nineteen places —
and capitalised in exactly two places, one of them backticked as if it were code:
`high-availability.md:140` ("the address of kubeadm's `ControlPlaneEndpoint`") and the heading at
`create-cluster-kubeadm.md:182`, "Considerations about apiserver-advertise-address and
ControlPlaneEndpoint". Both are reachable by someone following this post's recipe, and neither
string is a thing you can put in a YAML file.

**The reference implementations were provided, and not here.** `:70` promises that "The community
will provide a set of reference implementations for this task though", naming HAproxy and Envoy at
`:71` as candidates. Grep the pinned documentation tree for `haproxy`, `keepalived` or "reference
implementation" and nothing about kubeadm HA comes back. What `high-availability.md:118-143` gives
instead is one generic worked shape — a TCP forwarding load balancer, health-checked on `:6443`, no
software named, prefaced by a note that "There are many configurations for load balancers. The
following example is only one option" (`:120-123`) — and, at `:142`, a link out of the documentation
entirely to `git.k8s.io/kubeadm/docs/ha-considerations.md#options-for-software-load-balancing`.
There is a document with that name in the kubeadm repository, but it is outside the pin, so from
inside the pinned tree the promise cannot be checked at all — only observed to have moved somewhere
the reader has to leave to find.

**Of the four things `:128` and `:153-164` promise, two landed and two did not.** ECDSA keys landed
twice over: first as the kubeadm feature gate `PublicKeysECDSA`, alpha in v1.19 and removed in v1.37
(`kubeadm-init.md:164-177`), then as the `encryptionAlgorithm` field, whose values are "`RSA-2048`
(default), `RSA-3072`, `RSA-4096` or `ECDSA-P256`" (`kubeadm-certs.md:53-62`) — and the gate's own
description now ends "This feature gate is deprecated in favor of the `encryptionAlgorithm`
functionality available in kubeadm v1beta4" (`kubeadm-init.md:204-210`), so the promised feature
outlived the mechanism that delivered it. Windows nodes landed: `adding-windows-nodes.md` and
`upgrading-windows-nodes.md` sit beside their Linux equivalents. "Improved support for CA key
rotation" did not: `kubeadm-certs.md:311` is one flat sentence, "Kubeadm does not support rotation
or replacement of CA certificates out of the box", pointing at a manual procedure elsewhere. And
Kustomize did not: `:164` plans to "Utilize Kustomize to allow for advanced, layered and declarative
configuration", and `kustomize` has **zero hits, case-insensitive, in both
`reference/setup-tools/kubeadm/` and `setup/production-environment/tools/kubeadm/`**. What arrived
in its place is `--patches` (`kubeadm-init.md:198`) and a `patches.directory` config field.

**The post's first link is dead.** `:14` sends the reader to
`https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/`. There is no
`setup/independent/` in the pinned tree — `setup/` holds `_index.md`, `best-practices/`,
`learning-environment/` and `production-environment/`, and the page is now
`setup/production-environment/tools/kubeadm/create-cluster-kubeadm.md`. The post's other deep link,
the `#config-file` anchor at `:73`, still resolves: `kubeadm-init.md:112` is `### Using kubeadm init
with a configuration file {#config-file}`.

**What is still exactly right.** Every mechanical claim. `--upload-certs` still uploads a shared
certificate set as an opt-in (`high-availability.md:173-177`), the `--certificate-key` it prints is
still required by `kubeadm join --control-plane` (`:197`, `:259`), and the join phase that consumes
it is still called `control-plane-prepare/download-certs`
(`generated/kubeadm_join/_index.md:66-76`). The upgrade order at `:95` — `kubeadm upgrade apply`
first, then `kubeadm upgrade node` — is unchanged and appears in nineteen files. The scope statement
at `:26-48` has aged better than anything else in the post: kubeadm is still bounded by "the local
machine's filesystem and the Kubernetes API", the load balancer is still not its problem, and
Cluster API is still where the layer above lives. The post also documents something it presents as a
footnote and the pin now presents as a security boundary: `:89`'s automated certificate transfer is
time-limited, and `high-availability.md:199-200` and `:351` both say so — "uploaded-certs will be
deleted in two hours", "the decryption key from `--certificate-key` expires after two hours, by
default".

**What this exercise does not cover, and where it lives.** The upgrade verbs (`kubeadm upgrade
plan`, `apply`, `node`), the `kubeadm init|join|reset|upgrade phase` subcommands, the
`kubeadm-config` ConfigMap and the unconditional flags kubeadm writes belong to [the kubeadm GA
exercise](../2017/05-kubeadm-v18-released.md), which is also the one exercise in this tree that
deliberately installs an older minor. Both of kubeadm's feature-gate tables, including the
`PublicKeysECDSA` row cited above, are transcribed in full by [the kubeadm-arrival
exercise](../2016/09-how-we-made-kubernetes-easy-to-install.md); this exercise cites two rows and
leaves the tables there. Kustomize itself — what it is, how it composes — belongs to [the kustomize
exercise](../2018/03-announcing-kustomize.md); the only Kustomize question here is whether kubeadm
ever adopted it.

**The diff, and why** — five of the six cases at once, and the interesting thing is that they are
all statements about the same three paragraphs. A release note ages by being superseded. A roadmap
ages by being scored.

**Retired by being agreed with.** `:128`'s closing clause — the `kubeadm alpha` commands "are
expected to move top-level soon" — is the most completely fulfilled sentence in the post, and
fulfilling it is what made the sentence unusable. `kubeadm alpha certs renew` and `kubeadm alpha
certs check-expiration`, the two commands the post teaches, are both gone as written; their
replacements differ from them by exactly one word. A reader who takes the post literally types a
command that does not exist, and the reason it does not exist is that the post's own prediction came
true. What remains is a nineteen-line page whose body is a sentence saying there is nothing here,
with five other pages pointing at it — a mitigation that outlived the thing it mitigated.

**The post broke.** Not the mechanism, the artifacts. The v1beta2 format the post *releases* is
unreadable by the pinned tool, and the escape hatch the post names in the same breath — `kubeadm
config migrate` — is documented twice over as working only from *deprecated* formats
(`implementation-details.md:90-92`, `kubeadm-config.md:31-32`), which v1beta2 stopped being at
v1.27. The window in which the post's advice worked was v1.22 to v1.26. It has been shut for ten
releases. A config file written on 24 June 2019 by following this post is now a file with no
supported path forward, and nothing in the pin says so in those words; you have to read three pages
and subtract.

**A plan the project abandoned.** Three of the five forward-looking items this exercise checks never
landed, and each failed differently. GA `kubeadm.k8s.io/v1` was expected "During the course of the
year" and is still at the fourth beta revision, with `v1beta4` gaining fields as recently as v1.35 —
this is not a stalled API, it is an API that stopped wanting to be v1. CA key rotation was expected
"in the next releases" and is now a one-line refusal (`kubeadm-certs.md:311`). Kustomize was to be
"utilized" and was instead replaced, before adoption, by `--patches` — a narrower answer to the same
question. Against those, two items did land: ECDSA keys, and Windows nodes with their own
adding-and-upgrading pages. Scoring a roadmap is the only honest way to read this section, and the
score is two out of five, with `kubeadm alpha` graduating so hard it counts as neither.

**Overtaken by stasis.** `:56` says Beta and `:157` plans stable. The pinned HA page says nothing:
448 lines with no maturity statement of any kind. Nobody wrote "this is now stable", and nobody
wrote "this is still beta" either. The status question was not answered, it was dropped, and the
result is that this post is the most recent document in the pinned corpus that says what maturity
kubeadm HA has — while being seven years out of date and wrong to trust.

**Still right.** The whole of `:26-48`. The scope statement — local filesystem plus the Kubernetes
API, workers via `kubeadm join`, provisioning and networking and cloud integration out of scope,
Cluster API above — is unchanged in substance and almost unchanged in wording. The mechanics of
`:87-95` are also intact down to the flag names. The post is at its most durable exactly where it
describes a boundary rather than a version.

**No gate** — none of the 488 gate files in the pinned tree names a kubeadm feature, because
kubeadm's gates are not Kubernetes' gates: they are declared in the kubeadm configuration and
documented in their own tables on `kubeadm-init.md`, not in
`content/en/docs/reference/command-line-tools-reference/feature-gates/`. Two of those rows bear on
this post — `PublicKeysECDSA`, alpha in v1.19 and removed in v1.37, and `EtcdLearnerMode`, which
made the post's `:91` growing-etcd claim safer than it was by creating each new member "as a
learner" and promoting it "to a voting member only after the etcd data are fully aligned"
(`kubeadm-init.md:186-188`), beta in v1.29 and removed in v1.33 — and both tables are transcribed in
full by [the kubeadm-arrival exercise](../2016/09-how-we-made-kubernetes-easy-to-install.md). So
there is no ladder here to climb. What this exercise reads instead is the tool's own help text and
exit status: `kubeadm alpha`, `kubeadm certs renew --help`, `kubeadm config print init-defaults`,
and `kubeadm config migrate` fed files it should and should not accept. Where a gate would have
supplied a release number, the binary supplies a behaviour, and the behaviour is measured.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair): a control-plane node at
`10.10.10.130` and a worker at `10.10.10.131`, brought up with [the five provision
steps](../../strands/lab-topologies.md#provision). The second machine is the point. This post is
about joining a *second control plane node*, and the only honest way to look at that flow without
building a real HA cluster is to stand on a machine that is not already a control plane and try. The
`pair` cluster is also, by construction, the wrong cluster for the attempt: it was initialised
without `controlPlaneEndpoint`, which is precisely the condition the post's second step exists to
avoid. So the attempt fails, and the failure is the reading.

What the topology cannot show is the thing the post announces. There is no load balancer, so there
is no stable endpoint to put in the field; there is one etcd member, so nothing grows; and there is
no quorum to lose. Every claim in `:87-95` about *three* control planes behaving well together is
out of reach here, and this exercise does not pretend otherwise — it reads the boundary around that
flow, not the flow. Everything except step 9 runs on the control-plane host; step 9 runs on the
worker, reached over `ssh zain@10.10.10.131`.

Nine steps on the `pair` cluster. Steps 1 to 7 read the tool and touch nothing. Step 8 creates one
Secret in `kube-system`, which *Teardown* removes. Step 9 runs `kubeadm join` with `--dry-run`,
documented as "Don't apply any changes; just output what would be done"
(`generated/kubeadm_join/_index.md:164-167`), which is what makes it safe to point a control-plane
join at a node that is already a member of the cluster.

**Do**

1. Ask the binary for the staging area the post says its commands are leaving. Both of the post's
   certificate commands are spelled with `alpha`:

   ```sh
   kubeadm version -o short
   kubeadm alpha; echo "exit=$?"
   kubeadm alpha --help 2>&1 | head -20; echo "exit=$?"
   sudo kubeadm alpha certs check-expiration; echo "exit=$?"
   ```

2. Now the command as the pin spells it, and the one row both sample outputs leave out:

   ```sh
   sudo kubeadm certs check-expiration
   sudo kubeadm certs check-expiration | head -1
   sudo kubeadm certs check-expiration | grep super-admin.conf; echo "exit=$?"
   sudo kubeadm certs check-expiration | grep -c ' no$\|false$'; true
   ```

   Compare the header line against the post's four columns at `:115` and against the pin's five at
   `kubeadm-certs.md:151`, and compare the row count against the post's ten.

3. Count the renewable targets against the eleven listed at
   `reference/setup-tools/kubeadm/kubeadm-certs.md:19-38`, and the subcommands against the four
   subcommand sections on that page:

   ```sh
   sudo kubeadm certs --help 2>&1 | sed -n '/Available Commands/,/^$/p'
   sudo kubeadm certs renew --help 2>&1 | sed -n '/Available Commands/,/^$/p'
   sudo kubeadm certs renew --help 2>&1 | sed -n '/Available Commands/,/^$/p' | grep -c '^  [a-z]'; true
   ```

4. Ask which config version the tool writes by default, and whether the two generated reference
   pages that nothing includes correspond to commands that exist:

   ```sh
   kubeadm config print init-defaults | grep apiVersion
   kubeadm config print --help 2>&1 | sed -n '/Available Commands/,/^$/p'
   kubeadm config print upgrade-defaults >/dev/null 2>&1; echo "upgrade-defaults exit=$?"
   kubeadm config print reset-defaults  >/dev/null 2>&1; echo "reset-defaults exit=$?"
   ```

5. Write the post's own step 2 — a config file carrying `controlPlaneEndpoint` — in the format this
   post releases, and hand it to the command this post recommends. No version field is set, so
   nothing that happens can be blamed on an old `kubernetesVersion`:

   ```sh
   cat > /tmp/v1beta2.yaml <<'YAML'
   apiVersion: kubeadm.k8s.io/v1beta2
   kind: ClusterConfiguration
   controlPlaneEndpoint: "lb.blogwalk.example:6443"
   YAML
   kubeadm config migrate --old-config /tmp/v1beta2.yaml; echo "exit=$?"
   kubeadm config validate --config /tmp/v1beta2.yaml; echo "exit=$?"
   ```

6. Change one digit and ask again. This settles the contradiction on
   `generated/kubeadm_config/kubeadm_config_migrate.md` between the one-item supported list at
   `:19-21` and "read both types" at `:23`:

   ```sh
   sed 's|v1beta2|v1beta3|' /tmp/v1beta2.yaml > /tmp/v1beta3.yaml
   kubeadm config migrate --old-config /tmp/v1beta3.yaml; echo "exit=$?"
   kubeadm config migrate --old-config /tmp/v1beta3.yaml 2>/dev/null | grep -i 'apiVersion\|controlPlaneEndpoint'
   ```

7. Ask whether the capitalisation at `high-availability.md:140` and `create-cluster-kubeadm.md:182`
   is a typo that costs nothing or a typo that costs a cluster. The file is valid v1beta4 in every
   other respect:

   ```sh
   cat > /tmp/capital.yaml <<'YAML'
   apiVersion: kubeadm.k8s.io/v1beta4
   kind: ClusterConfiguration
   ControlPlaneEndpoint: "lb.blogwalk.example:6443"
   YAML
   kubeadm config validate --config /tmp/capital.yaml; echo "exit=$?"
   kubeadm config migrate --old-config /tmp/capital.yaml 2>/dev/null | grep -i controlplaneendpoint; echo "exit=$?"
   ```

8. Make the post's `:89` "automated certificate transfer" visible as an object, and find out where
   the two hours at `high-availability.md:199-200` and `:351` are actually written down. The flags
   are `--certificate-key` and `--upload-certs`
   (`generated/kubeadm_init/kubeadm_init_phase_upload-certs.md:34`, `:76`):

   ```sh
   KEY=$(sudo kubeadm certs certificate-key); echo "$KEY" | wc -c
   sudo kubeadm init phase upload-certs --upload-certs --certificate-key "$KEY"
   kubectl -n kube-system get secret kubeadm-certs -o json | python3 -c '
   import json,sys
   s=json.load(sys.stdin)
   print("keys:", sorted(s["data"]))
   print("owners:", [(o["kind"], o["name"]) for o in s["metadata"].get("ownerReferences", [])])'
   kubectl -n kube-system get secrets --field-selector type=bootstrap.kubernetes.io/token -o json | python3 -c '
   import base64, json, sys
   for i in json.load(sys.stdin)["items"]:
       d = i["data"]
       exp = base64.b64decode(d.get("expiration", "")).decode() or "-"
       print(i["metadata"]["name"], exp)'
   ```

9. Attempt the post's third step. On the control-plane node, mint a join command; then take it to
   the worker, add the two flags the post says are the only difference, and add `--dry-run` so that
   nothing is written:

   ```sh
   # on 10.10.10.130
   kubeadm token create --print-join-command
   kubectl -n kube-system get cm kubeadm-config -o json \
     | python3 -c 'import json,sys; print(json.load(sys.stdin)["data"]["ClusterConfiguration"])' \
     | grep -i controlplaneendpoint; echo "exit=$?"
   ```

   ```sh
   # on 10.10.10.131, with TOKEN, HASH and KEY pasted from above
   sudo kubeadm join 10.10.10.130:6443 --token TOKEN \
     --discovery-token-ca-cert-hash sha256:HASH \
     --control-plane --certificate-key KEY \
     --dry-run --ignore-preflight-errors=all 2>&1 | tail -30; echo "exit=$?"
   ```

**Expect**

1. `kubeadm version -o short` reports the newest minor, v1.37. The open part is `kubeadm alpha`
   itself: the pin ships a reference page for it, so the question is whether the *binary* still
   ships the subcommand. Record which of the two you get — a help screen listing no available
   commands, or `unknown command "alpha"`. Either way the fourth line fails, and that is the point:
   both certificate commands the post teaches are spelled with a word that no longer selects
   anything.

2. Real output this time. Compare three things against `:115-125`. The header: the post has four
   columns, the pin's paste at `kubeadm-certs.md:151` has five, and yours will match one of them.
   `EXTERNALLY MANAGED` renders `no` in the pin and `false` in the post — record which your binary
   prints, because the post's spelling of that value is the sort of thing that gets copied into a
   parser. And the row count: the post lists ten certificates, the reference page at
   `reference/setup-tools/kubeadm/kubeadm-certs.md:19-38` names eleven renewable certificates, and
   the eleventh is `super-admin.conf`. Record whether it appears in your output. If it does, both
   sample outputs in the pinned corpus are missing a row that the live tool prints.

3. `kubeadm certs` should offer four subcommands, matching the four subcommand sections on the
   reference page: `renew` (`:19`), `certificate-key` (`:40`), `check-expiration` (`:51`),
   `generate-csr` (`:61`). The count from `renew --help` is the number to write down — the reference
   page offers twelve tabs, an `all` plus eleven named certificates. If your count differs, the
   reference page and the binary disagree, and the binary wins.

4. `apiVersion: kubeadm.k8s.io/v1beta4`, twenty-two releases after the post expected `v1`. The two
   exit codes are the interesting part. If both are zero, then `kubeadm config print
   upgrade-defaults` and `reset-defaults` are real commands and `kubeadm-config.md:40-66` simply
   forgot to include the two generated pages that document them. If they are non-zero, the generated
   pages describe commands the tool no longer has. Record which; the pin is defective either way,
   but not in the same way.

5. This is the step the whole exercise exists for, and it should fail twice. The post's own
   configuration file, in the format the post announces, fed to the migration command the post
   recommends. Record the exact message, and specifically whether it names `v1beta2` or only says
   the kind is unregistered — a message that names the version tells the reader what happened, and a
   message about an unregistered kind does not. `kubeadm config validate` should refuse the same
   file for the same reason.

6. One character apart, and this is the open one. If migrate succeeds and prints `apiVersion:
   kubeadm.k8s.io/v1beta4` with the endpoint carried across, then "read both types"
   (`kubeadm_config_migrate.md:23`) is the true half and the one-item supported list at `:19-21` is
   short by a row. If it fails the same way step 5 did, the list is right and the sentence is a
   leftover. Record which half of that page is stale — and note that the reader has just been asked
   to settle a documentation contradiction with a two-line shell command, which is the whole
   argument for running these at all.

7. Three outcomes are possible and they are not equally cheap. `kubeadm config validate` may reject
   `ControlPlaneEndpoint` as an unknown field, in which case the two capitalised occurrences in the
   pin are harmless typos. It may accept the file and silently drop the field, in which case a
   reader who copied the casing from `high-availability.md:140` gets a cluster with no stable
   endpoint and no warning — and finds out at the first control-plane join, which is step 9. Or it
   may treat it as an alias, which would be a surprise. Record which, and record whether `migrate`
   echoes the field back.

8. `wc -c` should print 65: sixty-four hex characters and a newline, matching "an AES key of size 32
   bytes" at `high-availability.md:225`. The upload prints the key back unless
   `--skip-certificate-key-print` is passed. The Secret's data keys are the encrypted certificate
   filenames; the `ownerReferences` list is where the two hours live, and it should name a Secret of
   the form `bootstrap-token-<id>`. The last command prints every bootstrap token with its
   `expiration`, so subtract: the owning token should expire about two hours out, which is the
   mechanism behind "uploaded-certs will be deleted in two hours" (`high-availability.md:199-200`).
   Record the actual delta. The post says at `:89` only that the transfer is automated and opt-in;
   it never mentions that what it opts you into is a two-hour window.

9. The join must fail; the question is on which check. The cluster has no `controlPlaneEndpoint` —
   the `grep` on the ConfigMap should exit non-zero, proving it — and adding a control plane to a
   cluster without a stable endpoint is the thing the post's second step exists to prevent. Because
   `--ignore-preflight-errors=all` clears the file-availability complaints about a node that is
   already joined, what remains should be that check. Record the sentence verbatim, and record
   whether it names `controlPlaneEndpoint`, `--control-plane-endpoint`, or neither. If some other
   check fires first, record that instead and say so: the order in which kubeadm's preflight checks
   run is not written down anywhere this exercise could find in the pin, so whatever fires first is
   a measurement and not a contradiction.

**Read on** — four questions the pin can answer and one it cannot.

1. Score the rest of the roadmap yourself. `:159-164` names four improvement areas, and this
   exercise checks two of them: Windows nodes (`:161`) landed, Kustomize (`:164`) did not. The other
   two are "Improve the upstream CI signal, mainly for HA and upgrades" (`:162`) and "Consolidate
   how Kubernetes artifacts are built and installed" (`:163`). For each, find the pinned page that
   delivers it or establish that no such page exists; `tasks/administer-cluster/kubeadm/` and
   `setup/production-environment/tools/kubeadm/` are the places to start, and the absence of a page
   is as much of an answer as its presence.

2. `kubeadm-init.md:164-177` lists eight removed kubeadm feature gates. Read the descriptions at
   `:179-240` and sort them: which concern `kubeadm init`, and which concern `kubeadm join`? The
   answer says something about where the work went after this post — the HA join flow kept getting
   gates for years after it was declared beta.

3. `kubeadm-certs.md:311` refuses CA rotation and points at
   `tasks/tls/manual-rotation-of-ca-certificates/`. Read that page and count what kubeadm would have
   had to automate to keep the promise at `:128`. Then read `kubeadm-certs.md:294-307`, on renewal
   with an external CA, and note `:301`: "A CA, however, cannot be produced as a CSR." That sentence
   is most of the reason the promise was not kept.

4. Both config-api pages are marked `auto_generated: true`, and both carry the same migration list.
   `kubeadm-config.v1beta3.md:33` ends it with a comma — "kubeadm v1.27.x and newer no longer
   support v1beta2 and older APIs," — and `kubeadm-config.v1beta4.md:69` ends the same sentence with
   a full stop. Work out which page is generated from the current source and which is the fossil,
   then decide whether a generated page can be said to have a typo at all.

What the pin cannot answer is why the HA page has no maturity sentence. Either kubeadm HA was
declared stable and nobody wrote it into
`setup/production-environment/tools/kubeadm/high-availability.md`, or it was never declared and the
beta label from `:56` simply stopped being repeated until it was forgotten. The pinned tree contains
no statement either way, which means this blog post — seven years old, and wrong about almost
everything it predicts — is the most recent document in the corpus that says what maturity this
feature has. That is the failure mode worth carrying away: a feature can lose its status not by
being demoted but by nobody mentioning it again.

**Teardown** — one Secret, one token and three files. Run on the control-plane node:

```sh
kubectl -n kube-system delete secret kubeadm-certs
kubeadm token list
sudo kubeadm token delete TOKEN
rm -f /tmp/v1beta2.yaml /tmp/v1beta3.yaml /tmp/capital.yaml
```

Nothing on the worker needs undoing: step 9 ran with `--dry-run`, so `ls /etc/kubernetes/` there
should show the same two kubeconfig files and the same empty `manifests` directory as before.
Nothing about the cluster's own configuration was changed either — no `controlPlaneEndpoint` was
added, no certificate was renewed, and the `kubeadm-config` ConfigMap was only read. The cluster is
a two-node cluster with one control plane at the end of this exercise exactly as it was at the
start, which is the honest end state for a post about a flow this topology cannot host.
