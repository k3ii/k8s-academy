<a id="kubernetes-v1-34-kubectl-kuberc-beta"></a>

# Thirteen of the fifteen fields are marked required by the only page that carries a schema, the two it leaves optional are the two the prose also calls optional, and of the two kubectl root reference pages at the pin only one has heard of the subcommand that manages this file

**Post** — [Kubernetes v1.34: User preferences (kuberc) are available for testing in kubectl 1.34](https://kubernetes.io/blog/2025/08/28/kubernetes-v1-34-kubectl-kuberc-beta/),
2025-08-28.

5,591 bytes, 140 lines, 733 words of body; one author, Maciej Szulik of Defense Unicorns, Inc. Three
`##` headings and two `###`, five fenced blocks, no Hugo shortcodes, no trailing whitespace on any
line, thirteen markdown links across twelve distinct targets — one of the thirteen is the author
link in the front matter, and the only target linked twice is the reference page this exercise
spends most of its time in. It is the second-shortest of 2025's twelve `walk` verdicts. Every
command below is a client-side command; the cluster is here so that `kubectl` has somewhere to send
the request it has finished assembling.

**As written**

The post opens on two wishes at `:10-12` — that `kubectl delete` could be interactive by default,
linking [KEP 3895](https://kep.k8s.io/3895), and that aliases could be defined without generating
hundreds of shell functions by hand, linking a repository of pre-generated ones — and announces at
`:13-16` that SIG-CLI's user preferences work, [KEP 3104](https://kep.k8s.io/3104), reaches beta in
v1.34.

`## How it works` at `:18` sets the ground rules in one paragraph. `:25-28`: by default `kubectl`
looks for a `kuberc` file in your default kubeconfig directory, which the post names as
`$HOME/.kube`, and you can move it with the `--kuberc` option or the `KUBERC` environment variable.
`:33-37` gives the two lines every `kuberc` starts with, `apiVersion: kubectl.config.k8s.io/v1beta1`
and `kind: Preference`, and a comment where the rest would go. Then `### Defaults` at `:39` turns
the first wish on with the five-line `defaults` entry at `:46-52`, setting `interactive` to `"true"`
for `delete`, notes at `:56-59` that an explicit flag on the command line still wins, and adds
SIG-CLI's second recommendation at `:61-70`, `server-side` set to `"true"` for `apply`. `###
Aliases` at `:72` turns the second wish on: `gns`, an alias for `get` with `namespace` in
`prependArgs` and `--output=json`, and then `runx`, an alias for `run` that appends `--` and
`custom-arg` after whatever the user typed.

`## Debugging` at `:123` is three sentences: run `kubectl` at `-v=5` and *you should get all the
possible debugging information from this feature*, with the reference page and the KEP linked at
`:130-131`. `## Get involved` at `:133` asks for feedback and links the SIG-CLI Slack channel, the
kubectl repository and the community meetings. What the post does not contain is as load-bearing as
what it does. There is no mention of a schema, of any subcommand of `kubectl` for managing the file,
of credential plugins, or of any way to switch the feature off once it is on. All four exist at the
pin.

**As it runs now**

**The post never mentions that this file has a schema, and the schema marks thirteen of its fifteen
fields required.** `docs/reference/config-api/kuberc.v1beta1.md` is 318 lines of generated tables
describing `kubectl.config.k8s.io/v1beta1`. Seventeen rows open with a field name; thirteen of them
carry `[Required]`. The four that do not are `apiVersion`, `kind`, `credentialPluginPolicy` at `:85`
and `credentialPluginAllowlist` at `:98`. Drop the two type markers and fifteen fields remain,
thirteen required and two optional — and the two the schema leaves optional are exactly the two
`docs/reference/kubectl/kuberc.md:160` describes in prose as *Both fields are optional*. Generated
schema and hand-written prose agree, which is worth saying out loud because most of what follows is
the two of them disagreeing.

**What `[Required]` means is not that your file must contain the field.** The post's own first
example proves it: `:33-37` is a complete `kuberc` with nothing in it but `apiVersion` and `kind`,
and the schema marks neither of those required. Required is scoped to the struct the field sits in —
an entry in `aliases` must have a `name` and a `command`, an entry in `options` must have a `name`
and a `default`. Step 3 puts that reading to the test by feeding `kubectl` four files through
`--kuberc`: the two-line stub, a file with `aliases` and no `defaults`, a file with `defaults` and
no `aliases`, and an alias entry with no `command` as the control.

**One of the two root reference pages for `kubectl` has never heard of `kubectl kuberc`.** There are
two root pages for `kubectl` at the pin, hand-written `docs/reference/kubectl/kubectl.md` and
generated `docs/reference/kubectl/generated/kubectl.md`. They share no sentences — different link
forms, different one-line summaries — but both end in a list of subcommands, 43 entries on the
hand-written page and 44 on the generated one. Compare the two lists by name and there is exactly
one difference: `* [kubectl kuberc]` at `generated/kubectl.md:320`, *Manage kuberc configuration
files*. The page a reader is most likely to land on when they go looking for what `kubectl` can do
has never heard of the subcommand that manages the file this post is about.

**The hand-written root page describes the environment variable in the voice of an opt-in that
stopped being one at beta.** That page carries the environment-variable table, and at `:379` it
lists `KUBECTL_KUBERC` with the description *When set to true, kuberc file is taken into account to
define user specific preferences*. That is the voice of an opt-in, and at the pin the feature is
beta and on by default, which makes the only useful value of that variable `false`. The sentence the
generated flag help prints about the same variable is not this exercise's to examine — [the exercise
for the post that shipped custom profiling for `kubectl
debug`](../2024/11-custom-profiling-kubectl-debug.md) measured it and counted the pages that repeat
it. What belongs here is narrower: `KUBECTL_KUBERC` occurs once on the hand-written root page, and
the string `KUBERC` occurs on that page only as part of it.

**One variable does two jobs, and the second job eats a value the first would otherwise accept.**
Bare `KUBERC` is rarer than the prefixed form. Outside `docs/reference/kubectl/generated`, the
string appears on nine lines. Six are placeholder tokens such as `[KUBERC_PREPEND_ARGS]` in the two
config-api schema pages, which describe how an alias is assembled rather than naming a variable you
set. The other three are on `kuberc.md`: `:17` says set it to point at a custom file, and `:373` and
`:376` say export it with the value `off` to disable the feature. A file called `off` in your
working directory therefore cannot be selected by relative path. Step 8 confirms that rather than
assuming it, because the alternative reading — that `off` is special only when nothing resolves — is
equally plausible from the page.

**The post gives one platform's path and the page it points at gives two, and neither says what
happens when `KUBECONFIG` moves.** The post at `:25-27` says `kubectl` looks for the file *in your
default kubeconfig directory, which is `$HOME/.kube`*. `kuberc.md:14-15` gives that same POSIX path
and then adds the Windows one, `%USERPROFILE%\.kube\kuberc`, which the post never mentions. The
framing is the part worth testing: a kubeconfig directory is not a fixed thing — `KUBECONFIG` names
a file, or a colon-separated list of them, anywhere on disk — and nothing on either page says
whether the `kuberc` path follows it. Step 2 is two commands long and answers it.

**Where the pin disagrees with itself: a usage line names two sections and the examples printed
below it use a third.** `kubectl kuberc set` has both, generated from the same source.
`generated/kubectl_kuberc/kubectl_kuberc_set.md:35` prints `kubectl kuberc set --section
(defaults|aliases) --command COMMAND`, naming two sections; the last example on that page, six lines
later, is `kubectl kuberc set --section credentialplugin --policy Allowlist`, and
`kuberc.md:298-325` documents that third section as the only one the subcommand manages. Neither
page tells you that `--command` is meaningless for it. And `kuberc.md`, the page that teaches the
file, contains the string `kuberc view` zero times, so the one subcommand that would show you what
`kubectl` actually loaded is documented nowhere a reader of this page will find it.

**The worked example explains an output without ever showing the input, and the fragment it explains
was borrowed from the next example.** At `:91`, the `prependArgs` example explains that the `getn`
alias *will be translated to `kubectl get namespace test-ns --output json`* — but `getn` defines no
namespace name, and the only `test-ns` on the page is a `default` in the *next* example at `:108`,
which `:123` translates the same way. The page shows you an output without showing you the input
that produced it, and the fragment it borrowed came from a different alias. Step 5 reproduces `getn`
exactly and finds out what the missing input was. At `:29` and `:125` the two main section headings
are `## aliases` and `## defaults` in lower case, matching the YAML keys rather than the page's own
`## Credential plugin policy` at `:153`.

**The alpha schema is still published, still linked, and its field names are not the beta names.**
`docs/reference/config-api/kuberc.v1alpha1.md` is still published at the pin, still listed beside
the beta one at `docs/reference/_index.md:78-79`, and 217 lines long against v1beta1's 318. Its
field names are not the beta names: where v1beta1 has `defaults` and `options`, v1alpha1 has
`overrides` and `flags`, and it has no `credentialPluginPolicy` or `credentialPluginAllowlist` at
all. A reader who follows the first of those two links and copies what they find writes a file in a
shape nothing in this post or its reference page uses. Step 9 writes exactly that file and reads
what comes back.

**One page, two feature-state conventions, a note written in the future tense about a release
already two behind the pin, and a skipped heading level.** `:7` is `{{< feature-state state="beta"
for_k8s_version="1.34" >}}` with no `v` on the version; `:155`, on the same page, is `{{<
feature-state for_k8s_version="v1.35" state="beta" >}}` with one. The bare form appears on four
non-generated pages in the whole checkout and the other three are all `state="stable"`, so this page
is both the outlier and its own counter-example. `:267-273` is a note written in the future tense —
*From Kubernetes 1.36 onward, `name` is deprecated in favor of `command`* — at a pin whose newest
release is 1.37. And `:238` is `##### command`, a level-five heading whose nearest ancestor is the
level-three `### credentialPluginAllowlist` at `:190`. Step 10 counts all of this offline.

**Where the pin disagrees with itself about its own anchors: three camel-case links against one
hyphenated heading.** `kuberc.md:334`, `:336` and `:341` link to `#credentialPluginPolicy` and
`#credentialPluginAllowlist` in camel case, while `hugo.toml:55` sets `autoHeadingIDType =
"blackfriday"`, which lower-cases generated heading ids. The same page writes one anchor by hand at
`:275`, `### Example {#credential-plugin-policy-example}`, in the lower-case hyphenated form. That
is the page disagreeing with itself about its own anchors, three lines against one, and it is a
rendering question rather than a behaviour, so no step in this exercise settles it.

**What this exercise does not cover, and where it lives.** Server-side apply is a default this
exercise turns on and then measures through `managedFields`, but what server-side apply *is* — field
ownership, conflicts, the `kubectl-client-side-apply` manager it replaces — belongs to [the exercise
for its second beta](../2020/01-kubernetes-1-18-feature-server-side-apply-beta-2.md). The `--kuberc`
flag's own generated help text, and how many generated pages repeat it, belongs to [the exercise
that went looking for a gate that was never documented and came back
empty](../2024/11-custom-profiling-kubectl-debug.md). That `kuberc` has no feature gate because
feature gates govern API servers and this is a client-side file is settled in [the exercise that
traced nine `kubectl` features to six different
fates](../2015/09-some-things-you-didnt-know-about-kubectl.md) and again in [the exercise for a
client-side program that shipped in no Kubernetes release](../2018/03-announcing-kustomize.md); it
is one clause here, not an argument. The mis-citation of this feature's own KEP number on SIG-CLI's
spotlight page is measured in [the exercise that checked that page against the KEP numbers it
cites](../2023/06-introducing-kubectl-applyset-pruning.md).

**The diff, and why**

**Still right.** Every example in the post reproduces. The two-line stub is a valid `kuberc`; the
`delete` and `apply` defaults take effect and an explicit flag on the command line still beats them,
as `:56-59` promises; `gns` and `runx` both expand the way the post says they do; and the location
it names is the location `kuberc.md:14` names. Nothing the post asserts about how the feature
behaves has been falsified in three releases, with one open question — the `-v=5` promise at `:127`,
which step 4 puts to the test. That is the baseline, and steps 2 through 6 establish it before
anything else is claimed.

**Retired by being agreed with.** `### Defaults` recommends exactly two defaults — interactive
`delete` and server-side `apply` — in the voice of a person suggesting something. At the pin those
same two, in that order, are the body of `kuberc.md:327-368`, a section titled `## Suggested
defaults` that opens *The kubectl maintainers encourage you to adopt kuberc with the following
defaults*. The post's suggestion is now the project's. The documentation added one thing the post
could not have: a third line, `credentialPluginPolicy: DenyAll`, wrapped in a caution about managed
providers.

**Overtaken by stasis.** Three things grew around this feature that the post cannot mention and does
not hint at. There is a generated schema with fifteen fields and a required marker on thirteen of
them. There is a `kubectl kuberc` subcommand with `set` and `view` under it. There is a credential
plugin policy, beta at v1.35, that can refuse to execute the `exec` plugin your kubeconfig names. A
reader who takes the post as the map of the feature will miss all three, and the two reference pages
they are most likely to reach for disagree about whether the second one exists at all.

**Never absorbed.** The post's `## Debugging` section is the only place in the pinned tree that
tells you how to debug this feature. `kuberc.md` is 385 lines and contains the strings `debug`,
`verbosity` and `v=5` zero times each; the two other pages that mention `--v=5` at all are a kubectl
cheat sheet entry and an RBAC troubleshooting note, neither about preferences. If the post
disappeared, the advice to raise verbosity when your aliases do not expand would disappear with it —
which makes step 4's last command the one worth running twice.

**The ladder**

There is no gate file to read. `docs/reference/command-line-tools-reference/feature-gates/` contains
nothing matching `kuberc`, which is correct — feature gates govern servers and this file is read by
a client before a request is built. The only maturity record in the tree is the two `feature-state`
shortcodes on `kuberc.md`: `:7` puts the file itself at beta in 1.34, and `:155` puts the credential
plugin policy at beta in v1.35. Nothing in the pin records the alpha that preceded either. The
right-hand column of this ladder is one sentence in a note at `:267-273`, promising that the
allowlist entry's `name` field is deprecated in favour of `command` *from Kubernetes 1.36 onward*
and will be removed at GA — written in the future tense about a release the pin is already two past.

The lab runs v1.35, two releases below the pin's v1.37. That gap is the whole of step 1. The file
format is beta and on by default at both versions, so everything in steps 2 through 9 should work;
the `kubectl kuberc` subcommand is a different question, because a subcommand can be renamed or
promoted out of a prefix between releases and the pin's generated page records only where it landed,
not where it started. Step 1 asks the client rather than guessing, and the answer changes nothing
else in the exercise, because no step below needs the subcommand.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo), one node at `10.10.10.180`, Kubernetes v1.35,
[provisioned](../../strands/lab-topologies.md#provision) and
[baselined](../../strands/lab-topologies.md#node-baseline-steps) as usual. Nothing is flipped and no
component is restarted; the API server sees one namespace, three ConfigMaps and a handful of reads,
and everything else happens inside the `kubectl` process before a request exists. The lab's v1.35 is
also the release at which `kuberc.md:155` puts the credential plugin policy at beta, so step 9's
third file lands exactly on the version that introduced it. Two things outside the namespace are
written — a file at `$HOME/.kube/kuberc` on the node, and a scratch directory `/tmp/bw-kuberc` — and
Teardown removes both. Step 2 deliberately moves the home file aside when it is done with it, so
that steps 3 through 7 measure only what `--kuberc` points at.

**Do**

1. Ask the client what it is and whether it has the subcommand, then make somewhere to work.

   ```sh
   kubectl version --client -o yaml | grep gitVersion
   kubectl options 2>&1 | grep -A2 -- '--kuberc' || echo 'no --kuberc in kubectl options'
   kubectl --help 2>&1 | grep -i kuberc || echo 'kuberc absent from the root help'
   kubectl kuberc --help 2>&1 | head -4
   kubectl alpha kuberc --help 2>&1 | head -4
   mkdir -p /tmp/bw-kuberc
   kubectl create namespace bw-kuberc
   ```

2. Put a `kuberc` at the documented path, run an alias from it, then move the kubeconfig somewhere
   else and run the same alias again.

   ```sh
   mkdir -p "$HOME/.kube"
   cat > "$HOME/.kube/kuberc" <<'EOF'
   apiVersion: kubectl.config.k8s.io/v1beta1
   kind: Preference
   aliases:
     - name: gns
       command: get
       options:
         - name: output
           default: json
       prependArgs:
         - namespace
   EOF
   kubectl gns default | head -4
   cp "$HOME/.kube/config" /tmp/bw-kuberc/config
   KUBECONFIG=/tmp/bw-kuberc/config kubectl gns default | head -4
   mv "$HOME/.kube/kuberc" /tmp/bw-kuberc/home-kuberc.yaml
   kubectl gns default 2>&1 | head -2
   ```

3. Find out what the thirteen required markers actually require, by handing the client four files
   that each leave something out.

   ```sh
   printf 'apiVersion: kubectl.config.k8s.io/v1beta1\nkind: Preference\n' > /tmp/bw-kuberc/empty.yaml
   cat > /tmp/bw-kuberc/aliases-only.yaml <<'EOF'
   apiVersion: kubectl.config.k8s.io/v1beta1
   kind: Preference
   aliases:
     - name: gsa
       command: get
       prependArgs:
         - namespace
   EOF
   cat > /tmp/bw-kuberc/defaults-only.yaml <<'EOF'
   apiVersion: kubectl.config.k8s.io/v1beta1
   kind: Preference
   defaults:
     - command: get
       options:
         - name: output
           default: wide
   EOF
   cat > /tmp/bw-kuberc/no-command.yaml <<'EOF'
   apiVersion: kubectl.config.k8s.io/v1beta1
   kind: Preference
   aliases:
     - name: broken
       prependArgs:
         - namespace
   EOF
   for f in empty aliases-only defaults-only no-command; do
     echo "== $f"
     kubectl --kuberc /tmp/bw-kuberc/$f.yaml get ns default 2>&1 | head -3
   done
   kubectl --kuberc /tmp/bw-kuberc/aliases-only.yaml gsa default 2>&1 | head -3
   ```

4. Turn on the post's second suggested default and read the server's record of who applied what,
   then ask the client for the debugging information the post promises.

   ```sh
   cat > /tmp/bw-kuberc/ssa.yaml <<'EOF'
   apiVersion: kubectl.config.k8s.io/v1beta1
   kind: Preference
   defaults:
     - command: apply
       options:
         - name: server-side
           default: "true"
   EOF
   printf 'apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: probe\ndata:\n  k: "1"\n' > /tmp/bw-kuberc/cm.yaml
   kubectl -n bw-kuberc --kuberc /tmp/bw-kuberc/ssa.yaml apply -f /tmp/bw-kuberc/cm.yaml
   sed 's/name: probe/name: probe2/' /tmp/bw-kuberc/cm.yaml | kubectl -n bw-kuberc apply -f -
   sed 's/name: probe/name: probe3/' /tmp/bw-kuberc/cm.yaml | kubectl -n bw-kuberc --kuberc /tmp/bw-kuberc/ssa.yaml apply --server-side=false -f -
   for c in probe probe2 probe3; do
     echo "== $c"
     kubectl -n bw-kuberc get cm $c -o jsonpath='{range .metadata.managedFields[*]}{.manager} {.operation}{"\n"}{end}'
   done
   kubectl -n bw-kuberc --kuberc /tmp/bw-kuberc/ssa.yaml -v=5 apply -f /tmp/bw-kuberc/cm.yaml 2>&1 | grep -i 'kuberc\|alias\|server-side' || echo 'nothing about kuberc at -v=5'
   ```

5. Reproduce the `prependArgs` example exactly as the reference page writes it, and find out what
   input produces the output it claims.

   ```sh
   cat > /tmp/bw-kuberc/getn.yaml <<'EOF'
   apiVersion: kubectl.config.k8s.io/v1beta1
   kind: Preference
   aliases:
     - name: getn
       command: get
       options:
         - name: output
           default: json
       prependArgs:
         - namespace
   EOF
   kubectl --kuberc /tmp/bw-kuberc/getn.yaml getn test-ns 2>&1 | tail -3
   kubectl --kuberc /tmp/bw-kuberc/getn.yaml getn default | head -4
   kubectl --kuberc /tmp/bw-kuberc/getn.yaml getn default --output name
   ```

6. Reproduce the `appendArgs` example and read what the client would have sent, without sending it.

   ```sh
   cat > /tmp/bw-kuberc/runx.yaml <<'EOF'
   apiVersion: kubectl.config.k8s.io/v1beta1
   kind: Preference
   aliases:
   - name: runx
     command: run
     options:
       - name: image
         default: busybox
       - name: namespace
         default: test-ns
     appendArgs:
       - --
       - custom-arg
   EOF
   kubectl --kuberc /tmp/bw-kuberc/runx.yaml runx test-pod --dry-run=client -o yaml 2>&1 | grep -A6 'containers:'
   kubectl --kuberc /tmp/bw-kuberc/runx.yaml runx test-pod --dry-run=client -o yaml 2>&1 | grep 'namespace:' || echo 'no namespace in the rendered object'
   ```

7. Break the one rule the reference page states three times, and see which layer enforces it.

   ```sh
   cat > /tmp/bw-kuberc/collide.yaml <<'EOF'
   apiVersion: kubectl.config.k8s.io/v1beta1
   kind: Preference
   aliases:
     - name: get
       command: get
       options:
         - name: output
           default: name
   EOF
   kubectl --kuberc /tmp/bw-kuberc/collide.yaml get ns default 2>&1 | head -5
   ```

8. Give the environment variable both of its jobs at once and find out which one wins.

   ```sh
   cp /tmp/bw-kuberc/home-kuberc.yaml /tmp/bw-kuberc/off
   cp /tmp/bw-kuberc/home-kuberc.yaml "$HOME/.kube/kuberc"
   kubectl gns default --output name
   cd /tmp/bw-kuberc
   KUBERC=off kubectl gns default --output name 2>&1 | head -3
   KUBERC=/tmp/bw-kuberc/off kubectl gns default --output name 2>&1 | head -3
   KUBERC=/tmp/bw-kuberc/nope.yaml kubectl gns default --output name 2>&1 | head -3
   KUBECTL_KUBERC=false kubectl gns default --output name 2>&1 | head -3
   rm -f "$HOME/.kube/kuberc"
   ```

9. Hand the client three shapes it was never told about: the alpha schema's field names, the alpha
   version with beta field names, and the policy the post does not mention.

   ```sh
   cat > /tmp/bw-kuberc/alpha-shape.yaml <<'EOF'
   apiVersion: kubectl.config.k8s.io/v1alpha1
   kind: Preference
   overrides:
     - command: get
       flags:
         - name: output
           default: wide
   EOF
   cat > /tmp/bw-kuberc/alpha-beta-shape.yaml <<'EOF'
   apiVersion: kubectl.config.k8s.io/v1alpha1
   kind: Preference
   defaults:
     - command: get
       options:
         - name: output
           default: wide
   EOF
   cat > /tmp/bw-kuberc/denyall.yaml <<'EOF'
   apiVersion: kubectl.config.k8s.io/v1beta1
   kind: Preference
   credentialPluginPolicy: DenyAll
   EOF
   for f in alpha-shape alpha-beta-shape denyall; do
     echo "== $f"
     kubectl --kuberc /tmp/bw-kuberc/$f.yaml get ns default 2>&1 | head -4
   done
   ```

10. Count the disagreements offline, in the checkout, where nothing has to be running.

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -c 'B>\[Required\]</B' docs/reference/config-api/kuberc.v1beta1.md
    grep -c '^<tr><td><code>' docs/reference/config-api/kuberc.v1beta1.md
    diff <(grep -o '^\* \[kubectl [a-z-]*\]' docs/reference/kubectl/kubectl.md | sort) \
         <(grep -o '^\* \[kubectl [a-z-]*\]' docs/reference/kubectl/generated/kubectl.md | sort)
    grep -c 'KUBERC' docs/reference/kubectl/kubectl.md
    grep -rn 'KUBERC' --include='*.md' docs | grep -v 'generated/' | grep -v 'KUBECTL_KUBERC'
    grep -c 'kuberc view' docs/reference/kubectl/kuberc.md || true
    grep -n 'test-ns' docs/reference/kubectl/kuberc.md
    grep -n 'feature-state' docs/reference/kubectl/kuberc.md
    grep -rn 'for_k8s_version="1\.' --include='*.md' docs | grep -v generated
    grep -n '#credentialPlugin' docs/reference/kubectl/kuberc.md
    grep -n 'autoHeadingIDType' ../../hugo.toml
    grep -n 'section (defaults|aliases)' docs/reference/kubectl/generated/kubectl_kuberc/kubectl_kuberc_set.md
    grep -n 'credentialplugin' docs/reference/kubectl/generated/kubectl_kuberc/kubectl_kuberc_set.md
    ```

**Expect**

Step 1 prints `gitVersion: v1.35.x` and then answers the only version-sensitive question in the
exercise. `kubectl options` lists `--kuberc` with its one-line description, so the flag exists at
v1.35 and everything from step 2 onward will work. The root help is a different matter: if `kubectl
kuberc --help` prints a synopsis, the subcommand is where the pin's generated page says it is; if it
prints an error and `kubectl alpha kuberc --help` prints the synopsis instead, then the subcommand
moved out from under `alpha` between this client and the pin, and the pinned page records only the
destination. Either answer is fine. What matters is that the pinned hand-written root page lists
neither, which step 10 confirms, and that no later step needs the subcommand at all.

Step 2 prints the `default` namespace as JSON twice and then fails once. The first call proves the
alias loaded from `$HOME/.kube/kuberc` with no flag and no variable, so the documented default
location is real. The second call is the interesting one: `KUBECONFIG` now points at a copy in
`/tmp/bw-kuberc`, and the alias should still expand, because the `kuberc` path is
`$HOME/.kube/kuberc` and has no reason to follow the kubeconfig anywhere. If it does still expand,
*your default kubeconfig directory* is a description of where the file happens to sit rather than of
any rule the client follows. After the `mv`, the last call fails with an unknown-command error on
`gns`, which is the proof that steps 3 through 7 are measuring only the file each one names.

Step 3 is four answers to the question the schema raises. The two-line stub is accepted and `kubectl
get ns default` behaves normally, so thirteen `[Required]` markers do not mean thirteen mandatory
keys. The aliases-only and defaults-only files are both accepted too, which settles it: required is
scoped to the struct the field lives in, not to the document. The fourth file is the control — an
alias entry with a `name` and no `command`, the one shape the schema really does forbid — and it
should fail with a validation error naming the missing field rather than being ignored. The last
line then runs `gsa`, confirming the accepted aliases-only file was not merely tolerated but loaded.

Step 4 prints three pairs of manager and operation, and they are the whole case. The ConfigMap
applied through the kuberc shows `kubectl Apply`, the server-side manager identity
`server-side-apply.md:187` describes. The one applied without it shows `kubectl-client-side-apply
Update`, the default field manager that `kubectl_apply/_index.md:98` prints. The third shows the
client-side pair again, because `--server-side=false` on the command line beats the kuberc default,
which is `:56-59` of the post holding up. The `-v=5` line is the post's own promise under test: if
the grep comes back empty, *all the possible debugging information from this feature* amounts to
nothing this client prints at that verbosity, and the one thing the post supplies that no pinned
page repeats turns out not to work.

Step 5 supplies the input the reference page left out. `kubectl getn test-ns` expands to `kubectl
get namespace test-ns --output json` — exactly the string `kuberc.md:91` prints — and then fails,
because no namespace called `test-ns` exists on this cluster. That failure is the finding: the page
explains its example by showing you a command it never asked you to type, using a name it borrowed
from the `appendArgs` example two sections down, where `test-ns` is an actual `default` value. The
second call substitutes a namespace that does exist and prints it as JSON; the third overrides
`--output` on the command line and prints `namespace/default`.

Step 6 renders the `runx` alias without sending anything. The grep around `containers:` shows an
image of `busybox` and an `args` list ending in `custom-arg`, so both halves of the alias took
effect: the `options` default supplied the image the user never typed, and `appendArgs` put `--` and
`custom-arg` after the name. The second grep is the one worth watching. `namespace` is an option
here, not a field of the object, so a client-side dry run may render no `metadata.namespace` at all
even though the request would have gone to `test-ns`. Whichever way it prints, the reference page's
translation at `:123` names a namespace the object itself may never carry.

Step 7 tests `kuberc.md:51`, *Alias name must not collide with the built-in commands*, which the
page repeats for every alias field list it prints. An alias named `get` is the collision. Two
outcomes are defensible and the page does not say which to expect: the client rejects the file with
an error naming the alias, or it loads the file and silently ignores the shadowing entry so that
`kubectl get ns default` behaves exactly as it always did. The rule is stated as a constraint on you
rather than a promise about the client, so either is consistent with the documentation — and that is
the point of running it.

Step 8 gives `KUBERC` both jobs. With the file restored to `$HOME/.kube/kuberc`, the first call
prints `namespace/default` through the alias. From inside `/tmp/bw-kuberc`, where a readable
`kuberc` file is literally named `off`, `KUBERC=off` should disable the feature rather than load
that file: the alias stops resolving and `kubectl` reports an unknown command. The absolute path to
the same file then loads it and the alias works again, which proves the string `off` is special and
not the filename. A path that does not exist should be an error rather than a silent fallback to the
home file. `KUBECTL_KUBERC=false` disables it the other way.

Step 9 rejects two files and accepts one. The `v1alpha1` document with `overrides` and `flags` is
the shape the still-published alpha reference describes, and a v1.35 client should refuse it —
either on the `apiVersion`, if only `v1beta1` is registered, or on the unknown fields. The second
file keeps the alpha `apiVersion` and uses beta field names, which separates those two failure
modes: if it is also rejected, the version itself is gone. The third is accepted and changes nothing
visible, because `DenyAll` only bites when a kubeconfig names an `exec` credential plugin and this
one does not. That is the field the post never mentions, doing nothing, correctly.

Step 10 is all reading and every number is fixed. Thirteen `[Required]` markers across seventeen
field rows. The two root pages differ by exactly one subcommand name, `* [kubectl kuberc]`, present
on the generated page and absent from the hand-written one. `KUBERC` occurs once on the hand-written
root page and only inside `KUBECTL_KUBERC`. Bare `KUBERC` outside the generated tree appears on
`kuberc.md:17`, `:373` and `:376`, plus six placeholder lines in the two config-api pages. `kuberc
view` occurs zero times on the page that teaches the file. `test-ns` at `:91`, `:108` and `:123`;
`feature-state` at `:7` and `:155`; four bare-form versions in the whole tree, three of them
`stable`; three camelCase anchors at `:334`, `:336` and `:341` against `hugo.toml:55`; and a usage
line naming two sections above an example using a third.

**Read on**

11. [The other client-side flag whose server-side half can no longer be switched
    off](../2019/01-apiserver-dry-run-and-kubectl-diff.md) — `--dry-run=client`, used twice in step
    6, against the version of it that talks to the API server.

12. [What the two field managers this exercise reads actually
    own](../2020/01-kubernetes-1-18-feature-server-side-apply-beta-2.md), and why the default that
    `kuberc.md:349-352` now recommends was worth recommending.

13. [An earlier `kubectl` alpha switched on by an environment variable rather than a feature
    gate](../2023/06-introducing-kubectl-applyset-pruning.md) — the same mechanism as
    `KUBECTL_KUBERC`, seven releases earlier, and the page that mis-cites this feature's own KEP
    number.

14. [Nine conveniences `kubectl` already had before any of this
    existed](../2015/09-some-things-you-didnt-know-about-kubectl.md), including the one that made
    shell-alias generators worth writing in the first place.

15. *Unanswerable from the pin.* The tree gives no removal schedule for
    `kubectl.config.k8s.io/v1alpha1`, and no page says whether any released client ever accepted
    `overrides` and `flags` or whether that reference was generated from a type that never shipped.
    Step 9 can show you what this client refuses; it cannot tell you whether the alpha page is still
    published deliberately, for readers on older clients, or by omission. The SIG-CLI discussion
    that would settle it is not in this checkout.

**Teardown**

One namespace holds every object created on the cluster. Two things were written outside it, on the
node's filesystem, and both are removed here; step 8 already deleted the home file, so the `rm`
below is a safety net rather than a step that does work.

```sh
kubectl delete namespace bw-kuberc
rm -f "$HOME/.kube/kuberc"
rm -rf /tmp/bw-kuberc
```

If you keep a real `kuberc` of your own on this node, move it aside before step 2 and put it back
after Teardown — step 2 overwrites `$HOME/.kube/kuberc` without asking, and step 8 deletes it. The
checkout of `kubernetes/website` was only ever read. Step 4 is the one worth repeating if you want
the `-v=5` output at a higher verbosity: `-v=6` and `-v=8` print the request line and the request
body respectively, and neither is what the post was promising.
