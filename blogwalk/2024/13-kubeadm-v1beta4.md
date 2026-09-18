<a id="kubernetes-1-31-kubeadm-v1beta4"></a>

# The fully populated example on the page this post sends you to does not parse, the same block on the deprecated page it replaces does, five of the ten changes announced here are named at the pin by nothing but that same generated page, and twice the post spells a field it misspells

**Post** — [Kubernetes v1.31: kubeadm v1beta4](https://kubernetes.io/blog/2024/08/23/kubernetes-1-31-kubeadm-v1beta4/),
2024-08-23.

6,231 bytes over 104 lines, sole author Paco Xu (DaoCloud). Sixth-smallest of the thirteen `walk`
posts of 2024 and fifteenth-smallest of the year's fifty-four. It carries no fenced code block at
all — one of three walks that carry none, and the only one of the three whose subject is a file
format. Its four headings run `###`, `###`, `####`, `##`, so the one heading at the top level is the
acknowledgements. The change list is given twice, once as six bullets at `:31-37` and again as nine
at `:41-69`, and the same reference page is linked three times, at `:11`, `:22` and `:39`. Its one
command is inline prose at `:84`, and neither of the two files that command names is ever shown.

**As written** — kubeadm has a new configuration file format, `kubeadm.k8s.io/v1beta4`, as of
Kubernetes v1.31. The previous format, `v1beta3`, is "now formally deprecated, which means it's
supported but you should migrate to v1beta4 and stop using the deprecated format" (`:12-14`).
"Support for v1beta3 configuration will be removed after a minimum of 3 Kubernetes minor releases"
(`:15`). Ten things are new: two configuration kinds, `ResetConfiguration` and
`UpgradeConfiguration`; `dryRun` and `nodeRegistration.imagePullSerial` on `InitConfiguration` and
`JoinConfiguration`; `certificateValidityPeriod`, `caCertificateValidityPeriod`,
`encryptionAlgorithm`, `dns.disabled` and `proxy.disabled` on `ClusterConfiguration`; `extraEnvs` on
every control plane component; a `timeouts` structure on all four kinds; and `extraArgs` changed
"from a map to structured extra arguments for duplicates" (`:36`). To move, run `kubeadm config
migrate --old-config old-v1beta3.yaml --new-config new-v1beta4.yaml` (`:84`).

**As it runs now** — the migration advice landed and the syntax change is complete. Every kubeadm
document at the pin that shows an `extraArgs` block shows the v1beta4 list form: the four examples
on `control-plane-flags.md` (`:66-76`, `:84-94`, `:102-116`, `:124-132`), plus
`troubleshooting-kubeadm.md:425-427`, `setup-ha-etcd-with-kubeadm.md:137-141` and
`kubeadm-certs.md:282-286`. Not one v1beta3 map survives in an example. Six releases on, that half
of the post reads as a finished job.

**Five of the ten changes have no home outside the generated reference.** Collect the kubeadm
documentation — everything under `docs/reference/setup-tools/kubeadm/`,
`docs/setup/production-environment/tools/kubeadm/` and `docs/tasks/administer-cluster/kubeadm/`, 171
files — and ask which of the post's ten new things each names. `ResetConfiguration` is in two,
`UpgradeConfiguration` in three, `encryptionAlgorithm` in two, `certificateValidityPeriod` in one.
`extraEnvs`, `imagePullSerial`, `dns.disabled`, `proxy.disabled` and the whole `timeouts` structure
are in **none**. Five of the ten exist at the pin in exactly one place outside the Go source: the
generated reference page the post links three times.

**The page that teaches the structured `extraArgs` still says the new form cannot do the thing it
was built for.** `control-plane-flags.md` is the documentation's home for customising control plane
components, and it was updated: `:37` now reads "These structures contain a common `extraArgs`
field, that consists of `name` / `value` pairs", which is v1beta4's shape. Three lines below,
unchanged, sits a note: "Duplicate flags (keys), or passing the same flag `--foo` multiple times, is
currently not supported. To workaround that you must use patches" (`:55-58`). Duplicates are the
reason the field was restructured — the post says so at `:36`, and `kubeadm-config.v1beta4.md:39-42`
says "structured extra arguments that support duplicates". The note is v1beta3-era text sitting
directly above four v1beta4 examples, telling you the new form cannot do the thing it was built to
do.

**The two new kinds have reference pages that nothing on the site includes.**
`kubeadm-config.v1beta4.md:99` says "To print the defaults for `init` and `join` actions use the
following commands", and then lists four in the block at `:100-103`: `kubeadm config print
init-defaults`, `join-defaults`, `reset-defaults` and `upgrade-defaults`. All four have generated
reference files on disk under `docs/reference/setup-tools/kubeadm/generated/kubeadm_config/`. The
hand-written `kubeadm config` page includes three of the five — `kubeadm_config_print.md`,
`..._print_init-defaults.md` and `..._print_join-defaults.md`, at `kubeadm-config.md:42`, `:46` and
`:50`. The other two are included by nothing. Grep all of `content/en` for `reset-defaults` and
outside the generated file that documents it there is one hit, `:102` in that block; `:103` does the
same for `upgrade-defaults`.

**The page's fully populated example is not valid YAML, and the deprecated page's copy of it is.**
At `kubeadm-config.v1beta4.md:181-182` the page offers "a fully populated example of a single YAML
file containing multiple configuration types to be used during a kubeadm init run", and the block
runs `:183-310`. It does not parse. The second bootstrap token's `usages:` and `groups:` keys are at
four-space indentation while their list items sit at two (`:191-195`), so a parser fails at `:194`
with *mapping values are not allowed here* before it reaches a single kubeadm field. The same block
on the page this one deprecates, `kubeadm-config.v1beta3.md:138-238`, indents those list items
correctly and parses into four documents.

**Fix that and it still does not validate.** Re-indent those five lines and the next refusal comes
from the `timeouts` block two hundred lines further down, which spells `kubenetesAPICall` (`:220`).
The field is `kubernetesAPICall`; the page's own `Timeouts` table gives it at `:1847`. One typo in
the example hides behind another.

**Twice, the post spells a field correctly that the page it links spells wrong.** The overview names
the two fields v1beta4 replaced and gets both wrong. `:58-59` says
`ClusterConfiguration.timeoutForControlPlane` is replaced by
`Timeouts.controlPlaneComponentHealthCheck` and `JoinConfiguration.discovery.timeout` by
`timeouts.Discovery`. Neither path is real: the key is `timeouts` and the member is `discovery`,
both lower-case, as the table at `:1807-1890` has them. The post spells both correctly at `:63-64`.
Twice, on the two fields the post's own bullet is about, the two-year-old blog entry is the accurate
text and the generated page it sends you to is not.

**Three more disagreements, all inside the one page that was kept current.** `:24` records that
v1.34 added `ECDSA-P384` to `encryptionAlgorithm`, and the field table at `:601-603` lists five
values — but the v1.31 bullet at `:43-45` still lists four, and so does the hand-written task page
at `kubeadm-certs.md:62`. `:611` gives the non-CA certificate default as a backtick-wrapped duration
inside an HTML block, where backticks are not markup and render as themselves, while the CA default
one row below at `:619` is a proper HTML code element. And the page carries 29 `[Required]` markers
against v1beta3's 18, among them `dryRun` (`:652`), `dns.disabled` (`:1177`) and
`timeouts.upgradeManifests` (`:1883`) — three of the fields the post announces as new *options*, the
last of which is marked required and given `Default: 5m` in the same cell.

**And the disagreement a command can settle, which is therefore in *Do*.**
`kubeadm_config_validate.md:25-26` says "In this version of kubeadm, the following API versions are
supported: - kubeadm.k8s.io/v1beta4", and `:21-22` says "Unknown API versions and fields with
invalid values will also trigger errors". The migrate page prints the same one-item list and then
says kubeadm reads both types. So `kubeadm config validate` against a v1beta3 document either
refuses it, and the format that is "supported but deprecated" has no validator, or accepts it, and
`validate`'s own supported-versions list is short by one. Step 3 asks the binary.

**What this exercise does not cover, and where it lives** — the post's removal promise at `:15` and
the notice on the deprecated page belong to [the swap exercise](../2023/08-swap-linux-beta.md),
which measures `kubeadm-config.v1beta3.md:257-258` against the release it names. What `kubeadm
config migrate` reads and what it writes, at the `apiVersion` level, belongs to [the registry
exercise](../2022/11-registry-k8s-io-faster-cheaper-ga.md). Step 3 below runs migrate too, but it
watches the fields inside the document rather than the line at the top of it.
`ClusterConfiguration.featureGates` belongs to [the etcd learner-mode
exercise](../2023/10-kubeadm-use-etcd-learner-mode.md). Nothing here reconfigures a running cluster
or re-runs `kubeadm init`: every command in steps 1 to 7 and 9 reads or writes a file in `/tmp` and
touches no cluster state.

**The diff, and why** — three of the seven cases at once, and none of them is *broke*. The migration
instruction is **still right**: `kubeadm config migrate` is still the command, v1beta3 is still
readable, and every `extraArgs` example in the kubeadm documentation now uses the structured form
the post announced. The feature list is **never absorbed**: five of the ten changes have no home in
the 171 kubeadm documentation files two years and six releases later, and the one page that teaches
the structured `extraArgs` still carries the note that contradicts it. And the deprecation is

**overtaken by stasis**: the post promised removal after a minimum of three minor releases, the pin
is six past v1.31, and v1beta3 is still generated, still linked from the reference index, and still
read by the binary. The reason all three land together is that v1beta4 was shipped as a Go API
change with a generated reference, and the generated reference is the only artifact that tracked it.
The hand-written pages around it are edited when somebody edits them, and nobody did.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 vCPU, 25G, at `10.10.10.180`,
running v1.35. Provision with the [standard steps](../../strands/lab-topologies.md#provision) and
the [node baseline](../../strands/lab-topologies.md#node-baseline-steps), stand the cluster up as
[`labs/01/01`](../../labs/01/01-provision-and-kubeadm-init.md) does, then `ssh zain@10.10.10.180`.
There is no namespace in this exercise and no manifest is ever applied, because nothing here is
submitted to an API server: `kubeadm config` validates, migrates and prints files locally in the CLI
tool. A second node would give you a second copy of the same binary. Steps 1 to 7 and 9 need only
the binary; step 8 reads `/etc/kubernetes/pki` through `sudo kubeadm certs check-expiration`, which
is why the node has to be one that ran `kubeadm init`. Step 10 is offline, against the pinned
checkout on your workstation.

**Do**

1. Ground the binary, and read what it says about itself. Both `validate` and `migrate` print a
   supported-versions list; write down what each one claims before you test either.

   ```sh
   ssh zain@10.10.10.180
   mkdir -p /tmp/bw-v1beta4 && cd /tmp/bw-v1beta4
   kubeadm version -o short
   kubeadm config validate --help 2>&1 | sed -n '1,14p'
   kubeadm config migrate --help 2>&1 | sed -n '1,14p'
   kubeadm config print --help 2>&1 | sed -n '1,30p'
   ```

2. The four print subcommands the reference page names. Run each one, record the `apiVersion` and
   `kind` it emits, then feed its own output straight back to the validator.

   ```sh
   for s in init-defaults join-defaults reset-defaults upgrade-defaults; do
     printf '=== %s ===\n' "$s"
     if kubeadm config print "$s" > "print-$s.yaml" 2>"print-$s.err"; then
       grep -h '^apiVersion:\|^kind:' "print-$s.yaml"
     else
       sed -n '1,3p' "print-$s.err"
     fi
   done
   for s in init-defaults join-defaults reset-defaults upgrade-defaults; do
     printf '%-18s validate exit ' "$s"
     kubeadm config validate --config "print-$s.yaml" >/dev/null 2>&1; echo "$?"
   done
   ```

3. The disagreement from step 1, settled. A v1beta3 `ClusterConfiguration` carrying the two things
   v1beta4 changed — a map-shaped `extraArgs` and `timeoutForControlPlane` — put through the
   validator first and the post's own command second.

   ```sh
   cat > old-v1beta3.yaml <<'EOF'
   apiVersion: kubeadm.k8s.io/v1beta3
   kind: ClusterConfiguration
   kubernetesVersion: v1.35.0
   timeoutForControlPlane: 5m0s
   apiServer:
     extraArgs:
       v: "5"
       audit-log-path: /var/log/audit.log
   EOF
   kubeadm config validate --config old-v1beta3.yaml; echo "validate exit $?"
   kubeadm config migrate --old-config old-v1beta3.yaml --new-config new-v1beta4.yaml
   echo "migrate exit $?"
   grep -n 'apiVersion\|extraArgs\|  - name\|    value\|timeout' new-v1beta4.yaml
   ```

4. Duplicates, which are the reason the field was restructured and which
   `control-plane-flags.md:55-58` says are not supported. Two entries with the same `name`, then the
   v1beta3 map shape inside a v1beta4 document.

   ```sh
   cat > dup.yaml <<'EOF'
   apiVersion: kubeadm.k8s.io/v1beta4
   kind: ClusterConfiguration
   kubernetesVersion: v1.35.0
   apiServer:
     extraArgs:
     - name: runtime-config
       value: api/all=true
     - name: runtime-config
       value: admissionregistration.k8s.io/v1alpha1=true
   EOF
   kubeadm config validate --config dup.yaml; echo "duplicates exit $?"
   cat > mapform.yaml <<'EOF'
   apiVersion: kubeadm.k8s.io/v1beta4
   kind: ClusterConfiguration
   kubernetesVersion: v1.35.0
   apiServer:
     extraArgs:
       runtime-config: api/all=true
   EOF
   kubeadm config validate --config mapform.yaml; echo "map form exit $?"
   ```

5. The reference page's own fully populated example, transcribed from
   `kubeadm-config.v1beta4.md:183-220` exactly as it renders, and handed to the validator.

   ```sh
   cat > ref-init.yaml <<'EOF'
   apiVersion: kubeadm.k8s.io/v1beta4
   kind: InitConfiguration
   bootstrapTokens:
     - token: "9a08jv.c0izixklcxtmnze7"
       description: "kubeadm bootstrap token"
       ttl: "24h"
     - token: "783bde.3f89s0fje9f38fhf"
       description: "another bootstrap token"
       usages:
     - authentication
     - signing
       groups:
     - system:bootstrappers:kubeadm:default-node-token

   nodeRegistration:
     name: "ec2-10-100-0-1"
     criSocket: "unix:///var/run/containerd/containerd.sock"
     taints:
       - key: "kubeadmNode"
         value: "someValue"
         effect: "NoSchedule"
     kubeletExtraArgs:
       - name: v
         value: "5"
     ignorePreflightErrors:
       - IsPrivilegedUser
     imagePullPolicy: "IfNotPresent"
     imagePullSerial: true

   localAPIEndpoint:
     advertiseAddress: "10.100.0.1"
     bindPort: 6443
   certificateKey: "e6a2eb8581237ab72a4f494f30285ec12a9694d750b9785706a83bfcbbbd2204"
   skipPhases:
     - preflight
   timeouts:
     controlPlaneComponentHealthCheck: "60s"
     kubenetesAPICall: "40s"
   EOF
   kubeadm config validate --config ref-init.yaml; echo "reference example exit $?"
   ```

6. The same block from the page this one deprecates, and then the v1beta4 block with its five list
   items put back where the v1beta3 page has them.

   ```sh
   cat > v1beta3-tokens.yaml <<'EOF'
   apiVersion: kubeadm.k8s.io/v1beta3
   kind: InitConfiguration
   bootstrapTokens:
     - token: "9a08jv.c0izixklcxtmnze7"
       description: "kubeadm bootstrap token"
       ttl: "24h"
     - token: "783bde.3f89s0fje9f38fhf"
       description: "another bootstrap token"
       usages:
         - authentication
         - signing
       groups:
         - system:bootstrappers:kubeadm:default-node-token
   localAPIEndpoint:
     advertiseAddress: "10.100.0.1"
     bindPort: 6443
   EOF
   kubeadm config validate --config v1beta3-tokens.yaml; echo "v1beta3 block exit $?"
   sed -e 's|^  - authentication|      - authentication|' \
       -e 's|^  - signing|      - signing|' \
       -e 's|^  - system:bootstrappers|      - system:bootstrappers|' \
       ref-init.yaml > ref-init-reindented.yaml
   kubeadm config validate --config ref-init-reindented.yaml; echo "re-indented exit $?"
   ```

7. The four spellings of the two replaced fields: the two the reference overview gives at `:58-59`,
   and the two the post gives at `:63-64`.

   ```sh
   mk() { printf 'apiVersion: kubeadm.k8s.io/v1beta4\nkind: InitConfiguration\n%s\n' "$2" > "$1"; }
   mk t1.yaml 'timeouts:
     controlPlaneComponentHealthCheck: "60s"'
   mk t2.yaml 'Timeouts:
     controlPlaneComponentHealthCheck: "60s"'
   mk t3.yaml 'timeouts:
     discovery: "5m0s"'
   mk t4.yaml 'timeouts:
     Discovery: "5m0s"'
   for f in t1 t2 t3 t4; do
     printf '%-4s ' "$f"
     kubeadm config validate --config "$f.yaml" >/dev/null 2>&1 && echo accepted || echo refused
   done
   ```

8. The five fields no kubeadm documentation file names, all in one document, plus the two
   certificate validity defaults the reference gives at `:610-619`.

   ```sh
   cat > five.yaml <<'EOF'
   apiVersion: kubeadm.k8s.io/v1beta4
   kind: InitConfiguration
   nodeRegistration:
     imagePullSerial: false
   timeouts:
     kubernetesAPICall: "40s"
   ---
   apiVersion: kubeadm.k8s.io/v1beta4
   kind: ClusterConfiguration
   kubernetesVersion: v1.35.0
   apiServer:
     extraEnvs:
     - name: GODEBUG
       value: x509negativeserial=1
   dns:
     disabled: false
   proxy:
     disabled: false
   EOF
   kubeadm config validate --config five.yaml; echo "five undocumented fields exit $?"
   sudo kubeadm certs check-expiration | sed -n '1,6p'
   sudo kubeadm certs check-expiration | grep -i 'ca ' | head -4
   ```

9. The `[Required]` markers, tested, and the algorithm list the post and the task page both stop one
   short of.

   ```sh
   printf 'apiVersion: kubeadm.k8s.io/v1beta4\nkind: ClusterConfiguration\nkubernetesVersion: v1.35.0\n' > bare.yaml
   kubeadm config validate --config bare.yaml; echo "no proxy, no dns, no timeouts: exit $?"
   cat > tmo.yaml <<'EOF'
   apiVersion: kubeadm.k8s.io/v1beta4
   kind: InitConfiguration
   timeouts:
     discovery: "5m0s"
   EOF
   kubeadm config validate --config tmo.yaml; echo "timeouts without upgradeManifests exit $?"
   for a in RSA-2048 RSA-3072 RSA-4096 ECDSA-P256 ECDSA-P384 ECDSA-P521; do
     printf 'apiVersion: kubeadm.k8s.io/v1beta4\nkind: ClusterConfiguration\nkubernetesVersion: v1.35.0\nencryptionAlgorithm: %s\n' "$a" > alg.yaml
     printf '%-12s ' "$a"
     kubeadm config validate --config alg.yaml >/dev/null 2>&1 && echo accepted || echo refused
   done
   ```

10. Offline, against the pinned checkout. The coverage census, the note that contradicts the
    restructure, the two orphaned reference pages, the two misspelled paths, and the two algorithm
    lists.

    ```sh
    cd /path/to/kubernetes/website/content/en
    find docs/reference/setup-tools/kubeadm docs/setup/production-environment/tools/kubeadm \
         docs/tasks/administer-cluster/kubeadm -name '*.md' > /tmp/kdocs.txt
    wc -l < /tmp/kdocs.txt
    for t in extraEnvs imagePullSerial dns.disabled proxy.disabled controlPlaneComponentHealthCheck \
             ResetConfiguration UpgradeConfiguration certificateValidityPeriod encryptionAlgorithm extraArgs; do
      printf '%-34s %s\n' "$t" "$(grep -l -F -- "$t" $(cat /tmp/kdocs.txt) 2>/dev/null | wc -l | tr -d ' ')"
    done
    sed -n '37p;55,58p' docs/setup/production-environment/tools/kubeadm/control-plane-flags.md
    ls docs/reference/setup-tools/kubeadm/generated/kubeadm_config/ | grep print
    grep -n 'include "generated/kubeadm_config' docs/reference/setup-tools/kubeadm/kubeadm-config.md
    grep -rn 'reset-defaults' --include='*.md' docs | grep -v 'generated/kubeadm_config'
    sed -n '58,59p;601,603p;611p;619p' docs/reference/config-api/kubeadm-config.v1beta4.md | sed -e 's/<[^>]*>//g'
    sed -n '1847p;1883p' docs/reference/config-api/kubeadm-config.v1beta4.md | sed -e 's/<[^>]*>//g'
    grep -c '\[Required\]' docs/reference/config-api/kubeadm-config.v1beta3.md
    grep -c '\[Required\]' docs/reference/config-api/kubeadm-config.v1beta4.md
    sed -n '62p' docs/tasks/administer-cluster/kubeadm/kubeadm-certs.md
    ```

**Expect**

Step 1 prints a v1.35 binary, four releases past the one this post announces and one behind the
pin's newest. Read the two help texts against each other. `kubeadm config migrate --help` is the
generated text at `kubeadm_config_migrate.md:19-27`: it lists exactly one supported API version,
`kubeadm.k8s.io/v1beta4`, and then says the tool can read both types while writing only the one.
`kubeadm config validate --help` is `kubeadm_config_validate.md:19-26`: the same one-item list, and
above it the sentence that unknown API versions trigger errors. Those two pages cannot both be a
complete account of what the binary accepts, and step 3 makes the binary answer.

Step 2 is the first place the reference page and the site part company. The page names four print
subcommands at `kubeadm-config.v1beta4.md:100-103`, and
`docs/reference/setup-tools/kubeadm/kubeadm-config.md` includes generated text for only two of them,
at `:46` and `:50`. The two it skips, `reset-defaults` and `upgrade-defaults`, have generated files
sitting in the same directory as the two it includes. Expect the binary to run all four, and expect
each one to emit a `kubeadm.k8s.io/v1beta4` document whose own output validates cleanly. Nothing is
broken here. Two working subcommands are simply unreachable from any page a reader would navigate
to, which is why step 10 counts the include calls.

Step 3 settles it. The v1beta3 file is refused or accepted by the validator, and then the post's
migrate command is handed the same file. If migrate succeeds where validate refused, the generated
`validate` page's claim that unknown API versions trigger errors is scoped to what the validator
enforces, not to what the binary can parse, and the migrate page's "read both types" is the accurate
half. Read the output file rather than the exit code: `timeoutForControlPlane`, which lived at the
top of `ClusterConfiguration` in v1beta3, should come back as a `timeouts` entry, and the two map
keys under `apiServer.extraArgs` should come back as two `name`/`value` pairs. That transformation
is the whole of what this post asked readers to do, and it is the half of the post that the
documentation absorbed completely.

Step 4 is the contradiction. `control-plane-flags.md:55-58` says duplicate flags are not supported
and tells you to reach for patches instead; it says this three lines below the sentence at `:37`
that introduces the `name`/`value` pairs, and above four worked v1beta4 examples. Handing the
validator two `apiServer.extraArgs` entries that share a `name` tests whether the note describes the
API or an older one. Then the second file tests the other direction: a v1beta3-shaped map under a
v1beta4 `apiVersion`. Whatever each one returns, record it — the point of the step is that the page
teaching this field states a limitation the field exists to remove, and the binary is the only thing
on the node that can say which is current.

Step 5 fails before kubeadm reads a single field. The block transcribed here is the page's own
"fully populated example", introduced at `kubeadm-config.v1beta4.md:181-182` and running to `:310`;
the transcription above stops at the end of the `InitConfiguration` document. Five lines inside it —
`usages:`, its two items, `groups:` and its one item — are indented so that the two keys sit deeper
than the list items beneath them, which closes the mapping those keys belong to before the items
arrive. Expect a YAML scanner error naming a line, not a kubeadm validation error naming a field. A
parser refusing a document is a different kind of failure from a validator refusing a value, and
only the second kind means the example is wrong about the API.

Step 6 separates the two. The same bootstrap-token block appears on the page this one deprecates, at
`kubeadm-config.v1beta3.md:138-238`, correctly indented; it parses, and the validator gets far
enough to judge it. Then the `sed` puts the v1beta4 copy's five lines back where its predecessor has
them and re-runs. Expect the scanner error to move rather than disappear: the `timeouts` block at
`kubeadm-config.v1beta4.md:220` spells its second key `kubenetesAPICall`, and the struct documented
at `:1847` on the same page spells it `kubernetesAPICall`. One indentation defect and one
transposition, both in the block the page offers as the canonical complete configuration, both
surviving on the one page that the release notes at `:11-63` show was edited in v1.31, v1.33, v1.34
and v1.35.

Step 7 inverts the usual direction. Two of these four spellings come from the post, written in
August 2024 and never edited; two come from the overview of the page the post links, at
`kubeadm-config.v1beta4.md:58-59`, which writes the replaced timeout fields as
`Timeouts.controlPlaneComponentHealthCheck` and `timeouts.Discovery`. Go names are capitalised and
YAML keys are not, and that overview mixes the two conventions in a single pair of bullet points.
The post at `:63-64` gives both paths in the form you would actually type. Expect the binary to
accept the post's two and refuse the reference page's two, which is the clearest single reading in
this exercise: the two-year-old announcement is more accurate than the page it sends you to.

Step 8 puts the five orphans in front of the only reader that knows them. `imagePullSerial`,
`timeouts.kubernetesAPICall`, `extraEnvs`, `dns.disabled` and `proxy.disabled` are all announced in
this post, all present in the generated reference, and all absent from every hand-written kubeadm
page — step 10 counts that. Expect the validator to take them without comment. Then read the
certificate table: the reference gives one year for leaf certificates and ten for the CA, at
`kubeadm-config.v1beta4.md:611` and `:619`, and `certificateValidityPeriod` is the field this post
added for changing the first of those. `check-expiration` is reading the certificates `kubeadm init`
already wrote, so it shows you the defaults the field would override, not the field.

Step 9 tests what `[Required]` means on these pages. The v1beta4 reference carries twenty-nine of
those markers against the v1beta3 page's eighteen, and three of them sit on fields a reader would
call optional: `dryRun` at `:652`, `dns.disabled` at `:1177`, and `timeouts.upgradeManifests` at
`:1883`, which is marked required and given `Default: 5m` in the same entry. A
`ClusterConfiguration` with none of them, and a `timeouts` block without `upgradeManifests`, should
both pass. The marker is generated from the Go struct's serialization tags, not from what the binary
insists on, and a reader taking it at face value would write far more configuration than kubeadm
wants. The algorithm loop is the smaller check: expect all six accepted, including the `ECDSA-P384`
that `kubeadm-certs.md:62` leaves out of the list it offers as the choices.

Step 10 is the census, and it is the reason this exercise exists. Across the hundred and seventy-one
files under the three kubeadm documentation trees, expect `extraArgs` in five and
`ResetConfiguration`, `UpgradeConfiguration`, `encryptionAlgorithm` and `certificateValidityPeriod`
in a handful each — and expect `extraEnvs`, `imagePullSerial`, `dns.disabled`, `proxy.disabled` and
`controlPlaneComponentHealthCheck` in none of them. The `reset-defaults` grep should find exactly
one line outside the generated directory, and it is inside the reference page's own command block.
The post announced ten things; the documentation absorbed the ones that changed how you write a file
you already had, and left the ones that added something you did not have to the one page nobody
edits by hand.

**Read on**

11. [The exercise on the Linux swap beta](../2023/08-swap-linux-beta.md) — owns the v1beta3 removal
    promise and the deprecation notice this post's `:15` gestures at, measured against the release
    the deprecated page actually names.

12. [The exercise on registry.k8s.io going GA](../2022/11-registry-k8s-io-faster-cheaper-ga.md) —
    owns what `kubeadm config migrate` does at the `apiVersion` level, which step 3 above uses
    without re-deriving it.

13. [The exercise on etcd learner mode](../2023/10-kubeadm-use-etcd-learner-mode.md) — owns
    `ClusterConfiguration.featureGates`, the other kubeadm configuration field whose documentation
    outlived what it configured.

14. [The exercise on the other v1beta3](../2015/01-introducing-kubernetes-v1beta3.md) — the same
    three letters on the core API nine years earlier, announced the same way, and removed on
    schedule.

15. [The lab that stands a cluster up by hand](../../labs/01/01-provision-and-kubeadm-init.md) —
    where the `kubeadm` binary every step here calls comes from, and the `kubeadm init` run that
    step 8 reads certificates from.

**Teardown**

Nothing was submitted to an API server, so nothing has to be deleted from one. Remove the working
directory on the node, and the file list step 10 wrote on your workstation.

```sh
ssh zain@10.10.10.180 'rm -rf /tmp/bw-v1beta4'
rm -f /tmp/kdocs.txt
```

The cluster is left as the provisioning exercise left it. If you want the node gone as well, follow
[Teardown](../../strands/lab-topologies.md#teardown).
