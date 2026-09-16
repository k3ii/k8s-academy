<a id="contextual-logging-in-kubernetes-1-29"></a>

# The gate file declares one live alpha and one live beta at the same time, the binary answers with a single word, both of the post's sample log lines carry markdown bold markers no logger ever printed, and the page documenting the feature is one of 187 that never asks the file anything

**Post** — [Contextual logging in Kubernetes 1.29: Better troubleshooting and enhanced
logging](https://kubernetes.io/blog/2023/12/20/contextual-logging-in-kubernetes-1-29/),
2023-12-20.

148 lines, 9,286 bytes, by Mengjiao Liu (DaoCloud) and Patrick Ohly (Intel). Thirteenth and last of
this year's thirteen walks in publication order, sixth-largest of them by bytes. Its `:6` carries a
`canonicalUrl` pointing at `www.kubernetes.dev`, where the post was published first; 51 of the
archive's posts carry that field and twelve of this year's 78. Its last eighteen lines, `:131-148`,
are an alphabetical list of eighteen contributors, and both authors are in it — `:140` and `:143`.

**As written.** Contextual logging, the post says at `:14-16`, was introduced in v1.24 and has now
been migrated to two components: kube-scheduler and kube-controller-manager. `:22-28` gives the
mechanism: the feature is built on the go-logr API, in which libraries are passed a logger by their
caller instead of reaching for a global one, so that the binary, not the libraries, decides the
logging implementation. `:32-34` names the two calls that make it useful: `WithName`, which adds a
`logger` key whose value is the names so far joined by dots, and `WithValues`, which adds key/value
pairs. And `:36-38` states the payoff: pass the extended logger into a function and every entry that
function writes carries the extra information, with no edit to the code that writes it. `:47-51`
adds the design decision that a logger may be attached to a `context.Context`, because it is part of
the context and not merely a user of it.

**The instructions are the part that has aged.** `:55-58` says the feature is `alpha starting from
Kubernetes v1.24`, that it therefore requires the gate to be enabled, and that a reader who wants to
test it `while it is alpha` must switch it on for both the controller manager and the scheduler.
`:60-68` qualifies that for the scheduler: instrumentation also depends on verbosity, so that at
`-v3` or lower `only WithValues("pod") is used once per scheduling cycle`, and at `-v4` or higher
`richer log entries get produced`, with `WithValues` applied to the node as well and `WithName` to
the current operation and plugin. Two sentences in that stretch are written against a future: `:66`
says `Once contextual logging is GA, "pod" key/value pairs can be removed from all log calls`, and
`:76-77` says `Once it is GA, log calls can be simplified to avoid repeating those values`.

**Two sample log lines carry the argument.** `:71` shows a scheduler line and `:82` a
controller-manager one, both as blockquotes. `:88-97` puts numbers on the cost — no measurable
slowdown at `-v3` or lower, and at debug levels `:96` calls `a 28% slowdown for some test cases`
reasonable. `:100-102` closes the argument by disclaiming it: log output, it says, is not part of
the Kubernetes API and changes in every release. The post then asks for contributors at `:112-126`
and thanks eighteen of them.

**As it runs now.** The gate is beta and on by default, and has been since v1.30. The file at
`docs/reference/command-line-tools-reference/feature-gates/ContextualLogging.md:12-14` gives it a
`beta` stage with `defaultValue: true` and `fromVersion: "1.30"`. Two generated flag tables agree:
`kube-controller-manager.md:528` and `kube-scheduler.md:178` each enumerate 149 gates in the
`--feature-gates` help text, and in both the entry reads `kube:ContextualLogging=true|false (BETA -
default=true)`. So the post's `:55-58` instruction to enable the gate on those two components is now
an instruction to set a switch to the position it is already in.

**The alpha stage the post describes never ended.** `ContextualLogging.md:9-11` is `stage: alpha`,
`defaultValue: false`, `fromVersion: "1.24"` — and no `toVersion`. Under the reading rule this
archive has used since 2016, a stage with no `toVersion` is current at the pin, so the file asserts
that the gate is alpha-from-v1.24-onward *and* beta-from-v1.30-onward. Of the 487 gate files, four
have a non-terminal stage that never closes: this one, `DRAWorkloadResourceClaims` (alpha from
1.36), `KubeletCgroupDriverFromCRI` (beta from 1.31) and `DisableNodeKubeProxyVersion` (deprecated
from 1.31.1). This is the oldest of the four by seven releases, and the only one on which a censused
post depends. From v1.24 to the pin's v1.37 is fourteen releases in flight.

**Nothing in the tree asks the file which stage it means.** The `feature-state` shortcode has two
forms: name a gate and let the file supply the answer, or hardcode a version and a state. Across
`docs/`, 263 uses take the first form and 187 the second. The page that documents this feature,
`docs/concepts/cluster-administration/system-logs.md`, stamps its Contextual Logging section at
`:125` with `{{< feature-state for_k8s_version="v1.30" state="beta" >}}` — the hardcoded form. The
string `feature_gate_name="ContextualLogging"` does not occur anywhere in `content/en`. The one
malformed gate file that a reader might have been walked into is the one no page reads.

**Where the pinned documentation disagrees with itself.** One table is built from this file.
`feature-gates/index.md:68` is a `feature-gate-table` shortcode with `include="alpha,beta"`, and
`:49-52` states the contract its columns keep: `Since` carries `the Kubernetes release when a
feature is introduced`, and `Until`, when not empty, carries `the last Kubernetes release in which
you can still use a feature gate`. The same page defines the stages it is sorting by. `:80-82` says
an Alpha feature is `Disabled by default`; `:89-91` says a Beta feature is `Usually enabled by
default`. `ContextualLogging.md` hands that one table an alpha row with `defaultValue: false` and no
`Until`, and a beta row with `defaultValue: true` and no `Until`. Read the columns as the page
defines them and the gate is, right now, a disabled-by-default alpha and an enabled-by-default beta.
Both halves are cited; neither is wrong about the file. A command settles which stage the running
binary is in — that is step 1 — and no command changes what the table says.

**The post's two sample log lines are not log lines.** `:71` and `:82` are blockquotes, and inside
both, the key names are wrapped in Markdown emphasis markers. The source holds them like this:

```text
> I1113 08:43:37.029524 87144 default_binder.go:53] "Attempting to bind pod to node" **logger="Bind.DefaultBinder"** **pod**="kube-system/coredns-69cbfb9798-ms4pq" **node**="127.0.0.1"

> I1113 08:43:29.284360 87141 graph_builder.go:285] "garbage controller monitor not synced: no monitors" **logger="garbage-collector-controller"**
```

On the rendered page the asterisks become bold; in the source they are the sample. On the first line
the emphasis wraps the whole `logger` pair but only the bare keys `pod` and `node`, so the three
pairs are not even marked the same way. klog writes neither. And the sentence that explains the
second line, `:84`, quotes it back with typographic quotation marks, where the blockquote one line
above uses straight ones. Step 10 puts a real line beside all three.

**What this exercise does not cover, and where it lives.** Structured logging itself — `InfoS`,
`ErrorS`, `KObj`, the JSON log format, the klog flags that were removed at v1.26, and the two
sibling logging gates `LoggingAlphaOptions` and `LoggingBetaOptions` that arrived alongside this one
at v1.24 — is [the 2020 structured-logs
post](../2020/08-kubernetes-1-19-introducing-structured-logs.md), which also reads the rest of
`system-logs.md` and the five generated flag tables. Reading a node's journal through the API
server, and the rest of `system-logs.md` below its logging sections, is [the node log query
exercise](03-node-log-query-alpha.md) earlier in this year. Nothing below reads an audit log, a
metrics endpoint or a container log; this exercise reads control-plane component stdout and two
files in the pinned tree.

**The diff, and why**

**Four of the seven cases.** This post ***broke***, it was ***wrong when it was published***, it
has been ***overtaken by stasis***, and one of its defects was ***never absorbed***. The premise of
its how-to — that the feature is alpha and the gate must be switched on — stopped being true at
v1.30. Its two sample log lines carry emphasis markers, and one of them is quoted back a line later
with curly quotation marks. Both of its `Once it is GA` sentences are still waiting, seven releases
on. And when the beta row was added to the gate file, the alpha row above it was never closed.

**The interesting one is the last.** The other three are ordinary ageing: a release moved, a draft
went out with markdown in a code sample, a promise was not kept. The unclosed alpha row is
different, because it is not a claim anybody made in prose. It is one absent line in a data file,
and the data file is the tree's own machine-readable answer to the question *what stage is this
feature in*. The post's whole how-to section rests on that answer. The tree can tell you, from two
generated flag tables and from the running binary, that the answer is beta. The file that is
supposed to be the source for both still says alpha as well, and the one page that documents the
feature never consults it, so there is no rendered page anywhere that shows the contradiction. You
have to open the file.

**The ladder**

`ContextualLogging`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.24 – |
| beta | `true` | — | v1.30 – |

Both rows are unbounded, and that is the whole finding: the transcription above is lossless, and a
lossless transcription of this file has two open stages. The file declares no `removed` field and no
`locked` field on either stage, and its body, `ContextualLogging.md:16-17`, is the single sentence
the 2020 structured-logs exercise transcribes alongside its two siblings. A ladder reads down a
column of closed intervals with at most one left open at the bottom. This one has two.

**Topology**

One node, the [`solo` topology](../../strands/lab-topologies.md#solo), fresh. Bring the guest up
with [the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, install Kubernetes with [the node baseline
procedure](../../strands/lab-topologies.md#node-baseline-steps), bring the cluster up as usual, and
untaint the control plane so that the probe Pods below have somewhere to land. Everything here edits
the two static Pod manifests on that one node and reads what the two components print. Steps 2 and
10 are read against a checkout of the pinned tree on your workstation, not on the guest.

**Do**

1. Provision, back up both manifests, untaint the node, and ask the binary what stage it thinks the
   gate is in. The last command is the one that settles what *The ladder* cannot.

   ```sh
   ssh zain@10.10.10.180
   kubectl version
   CP=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl taint node $CP node-role.kubernetes.io/control-plane- || true
   sudo cp /etc/kubernetes/manifests/kube-scheduler.yaml /tmp/bw-sched.yaml
   sudo cp /etc/kubernetes/manifests/kube-controller-manager.yaml /tmp/bw-kcm.yaml
   kubectl -n kube-system exec kube-controller-manager-$CP -- \
     kube-controller-manager --help 2>&1 | grep -o 'ContextualLogging=[^ ]* ([A-Z]* - default=[a-z]*)'
   kubectl -n kube-system exec kube-scheduler-$CP -- \
     kube-scheduler --help 2>&1 | grep -o 'ContextualLogging=[^ ]* ([A-Z]* - default=[a-z]*)'
   ```

2. Read the gate file whole, then read the contract the table that consumes it keeps, then ask
   whether any page in the tree names the gate. This is on your workstation, against the pinned
   checkout.

   ```sh
   cd /path/to/kubernetes/website/content/en
   cat docs/reference/command-line-tools-reference/feature-gates/ContextualLogging.md
   sed -n '49,52p;79,92p' docs/reference/command-line-tools-reference/feature-gates/index.md
   grep -rn 'feature_gate_name="ContextualLogging"' . --include='*.md' || echo "no page names this gate"
   sed -n '123,126p' docs/concepts/cluster-administration/system-logs.md
   ```

3. Back on the guest. Put the scheduler at `-v=3` — the verbosity the post calls production — with
   the gate left at its default, schedule one Pod, and keep the lines that mention it.

   ```sh
   sudo sed -i '/- kube-scheduler$/a\    - --v=3' /etc/kubernetes/manifests/kube-scheduler.yaml
   sleep 40
   kubectl -n kube-system get pod kube-scheduler-$CP -o jsonpath='{.spec.containers[0].command}'; echo
   kubectl create namespace bw-ctxlog
   kubectl -n bw-ctxlog run p3on --image=registry.k8s.io/pause:3.10 --restart=Never
   kubectl -n bw-ctxlog wait --for=condition=Ready pod/p3on --timeout=120s
   kubectl -n kube-system logs -l component=kube-scheduler --tail=3000 | grep p3on | tee /tmp/bw-v3-on.txt
   wc -l /tmp/bw-v3-on.txt
   grep -c 'logger=' /tmp/bw-v3-on.txt || true
   ```

4. Raise it to `-v=4`, the verbosity at which the post promises `WithName` for the operation and
   plugin, and repeat with a second Pod.

   ```sh
   sudo sed -i 's|- --v=3|- --v=4|' /etc/kubernetes/manifests/kube-scheduler.yaml
   sleep 40
   kubectl -n bw-ctxlog run p4on --image=registry.k8s.io/pause:3.10 --restart=Never
   kubectl -n bw-ctxlog wait --for=condition=Ready pod/p4on --timeout=120s
   kubectl -n kube-system logs -l component=kube-scheduler --tail=3000 | grep p4on | tee /tmp/bw-v4-on.txt
   wc -l /tmp/bw-v4-on.txt
   grep -o 'logger="[^"]*"' /tmp/bw-v4-on.txt | sort | uniq -c
   ```

5. Now turn the gate off at the same `-v=4` and schedule a third Pod. This is the comparison the
   census row asks for, and the interesting output is not the line count but the set of keys.

   ```sh
   sudo sed -i '/- --v=4/a\    - --feature-gates=ContextualLogging=false' \
     /etc/kubernetes/manifests/kube-scheduler.yaml
   sleep 40
   kubectl -n kube-system get pod kube-scheduler-$CP -o jsonpath='{.spec.containers[0].command}'; echo
   kubectl -n bw-ctxlog run p4off --image=registry.k8s.io/pause:3.10 --restart=Never
   kubectl -n bw-ctxlog wait --for=condition=Ready pod/p4off --timeout=120s
   kubectl -n kube-system logs -l component=kube-scheduler --tail=3000 | grep p4off | tee /tmp/bw-v4-off.txt
   wc -l /tmp/bw-v4-off.txt
   grep -o '[a-zA-Z]*=' /tmp/bw-v4-on.txt  | sort -u > /tmp/bw-keys-on.txt
   grep -o '[a-zA-Z]*=' /tmp/bw-v4-off.txt | sort -u > /tmp/bw-keys-off.txt
   diff /tmp/bw-keys-on.txt /tmp/bw-keys-off.txt || true
   ```

6. Complete the square: `-v=3` with the gate off. Four captures now exist, and the post's claim at
   `:60-68` is a claim about all four of them at once.

   ```sh
   sudo sed -i 's|- --v=4|- --v=3|' /etc/kubernetes/manifests/kube-scheduler.yaml
   sleep 40
   kubectl -n bw-ctxlog run p3off --image=registry.k8s.io/pause:3.10 --restart=Never
   kubectl -n bw-ctxlog wait --for=condition=Ready pod/p3off --timeout=120s
   kubectl -n kube-system logs -l component=kube-scheduler --tail=3000 | grep p3off | tee /tmp/bw-v3-off.txt
   for f in /tmp/bw-v3-on.txt /tmp/bw-v4-on.txt /tmp/bw-v3-off.txt /tmp/bw-v4-off.txt; do
     printf '%-20s lines=%s logger=%s\n' "$f" "$(wc -l < $f)" "$(grep -c 'logger=' $f || true)"
   done
   ```

7. Restore the scheduler and move to the other component the post names. `kube-controller-manager`
   at `-v=4` with the gate at its default is where the post's second sample line comes from.

   ```sh
   sudo cp /tmp/bw-sched.yaml /etc/kubernetes/manifests/kube-scheduler.yaml
   sudo sed -i '/- kube-controller-manager$/a\    - --v=4' \
     /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 60
   kubectl -n kube-system get pods -l component=kube-controller-manager
   kubectl -n kube-system logs -l component=kube-controller-manager --tail=4000 > /tmp/bw-kcm-on.txt
   grep -o 'logger="[^"]*"' /tmp/bw-kcm-on.txt | sort | uniq -c | sort -rn | head -20
   grep -c 'garbage-collector-controller' /tmp/bw-kcm-on.txt || true
   ```

8. Turn the gate off on the controller manager at the same verbosity and count the same things.

   ```sh
   sudo sed -i '/- --v=4/a\    - --feature-gates=ContextualLogging=false' \
     /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 60
   kubectl -n kube-system logs -l component=kube-controller-manager --tail=4000 > /tmp/bw-kcm-off.txt
   grep -c 'logger=' /tmp/bw-kcm-off.txt || true
   grep -o '[a-zA-Z]*=' /tmp/bw-kcm-on.txt  | sort -u > /tmp/bw-kcm-keys-on.txt
   grep -o '[a-zA-Z]*=' /tmp/bw-kcm-off.txt | sort -u > /tmp/bw-kcm-keys-off.txt
   diff /tmp/bw-kcm-keys-on.txt /tmp/bw-kcm-keys-off.txt || true
   ```

9. Do what the post tells you to do. Set the gate to `true` explicitly on both components, which is
   the entire instruction at its `:55-58`, and look for anything in either component's output that
   comments on the setting.

   ```sh
   sudo sed -i 's|--feature-gates=ContextualLogging=false|--feature-gates=ContextualLogging=true|' \
     /etc/kubernetes/manifests/kube-controller-manager.yaml
   sudo sed -i '/- kube-scheduler$/a\    - --v=4\n    - --feature-gates=ContextualLogging=true' \
     /etc/kubernetes/manifests/kube-scheduler.yaml
   sleep 60
   kubectl -n kube-system get pods -l tier=control-plane
   kubectl -n bw-ctxlog run p9 --image=registry.k8s.io/pause:3.10 --restart=Never
   kubectl -n bw-ctxlog wait --for=condition=Ready pod/p9 --timeout=120s
   kubectl -n kube-system logs -l component=kube-scheduler --tail=3000 | grep p9 | tee /tmp/bw-v4-again.txt
   grep -c 'logger=' /tmp/bw-v4-again.txt || true
   kubectl -n kube-system logs -l component=kube-controller-manager --tail=4000 \
     | grep -i 'feature gate\|deprecat\|contextuallogging' | head -20
   kubectl -n kube-system logs -l component=kube-scheduler --tail=3000 \
     | grep -i 'feature gate\|deprecat\|contextuallogging' | head -20
   ```

10. Last, put one real line beside the three renderings the post prints. Copy a captured scheduler
    line off the guest, then read the post's source on your workstation.

    ```sh
    grep -m1 'Attempting to bind\|logger=' /tmp/bw-v4-on.txt
    cd /path/to/kubernetes/website/content/en
    sed -n '71p;82p;84p' blog/_posts/2023/contextual-logging-in-kubernetes-1-29.md
    grep -o '\*\*' blog/_posts/2023/contextual-logging-in-kubernetes-1-29.md | wc -l
    grep -n '[“”]' blog/_posts/2023/contextual-logging-in-kubernetes-1-29.md
    ```

**Expect**

Step 1 should report a v1.35 server, and both `--help` greps should print exactly one line each,
reading `ContextualLogging=true|false (BETA - default=true)`. One word, one stage, one default.
Write it down, because it is the answer the gate file does not give. If a grep prints nothing, the
binary does not carry the gate on that component and the post's instruction was never applicable
there; if it prints two lines, stop and read them, because that is a finding this exercise did not
predict.

Step 2 gives you seventeen lines of gate file with two `stage:` keys and no `toVersion:` anywhere.
The absence that matters is the one on the *first* stage; a last stage with no `toVersion` is
ordinary and is how the tree spells `current at this release`. `index.md:49-52` tells you what an
empty `Until` means and `:79-92` tells you what each stage promises about defaults. The `grep -rn`
should print the `no page names this gate` fallback: nothing in `content/en` names this gate in a
`feature-state` shortcode. `system-logs.md:125` hardcodes `v1.30` and `beta` instead, which is the
right answer arrived at by not asking.

Step 3 is the baseline. At `-v=3` with the gate on, the scheduler should print a small number of
lines about `p3on` — single digits — and most or all of them should carry `logger=`, because the
post says at `:64` that a single `WithValues("pod")` is applied once per cycle at this verbosity.
Record both counts; they are two of the eight numbers step 6 tabulates.

Step 4 should print more lines for `p4on` than step 3 did for `p3on`, and the `uniq -c` should show
several distinct `logger=` values rather than one. The post's `:67-68` predicts exactly that:
`WithName` for the current operation and plugin, so values like `Bind.DefaultBinder` in the shape of
the sample at `:71`. If every line carries the same `logger=` value, the `WithName` half of the post
is not reaching this build's scheduler and that is the finding.

Step 5 is the measurement the census row commissions. With the gate off at the same `-v=4`, the
`diff` of the key sets is the answer: expect `logger=` to be present on the left and absent on the
right, and expect the rest of the keys to survive, because the individual log calls in the scheduler
still pass `pod` and `node` themselves — the post says so at `:74`. What the gate removes is the
accumulated context, not the structured pairs. A diff showing no change at all means the gate is not
wired into this code path; a diff removing most keys means it does more than the post claims.

Step 6 completes a two-by-two: verbosity on one axis, the gate on the other. The interesting cell is
`-v=3` with the gate off, because the post's performance argument at `:94-96` rests on production
verbosity costing nothing. Compare `bw-v3-on` against `bw-v3-off`: if the `logger=` count differs
there as sharply as it does at `-v=4`, then the gate is doing work at production verbosity too, and
the post's no-measurable-slowdown claim was about the scheduler's own restraint in what it attaches,
not about the gate.

Step 7 should show one `logger=` value per controller, which is the point of the post's `:79-86`:
`WithName` is applied by the controller manager core when it instantiates each controller, so the
name is on every line that controller writes. Expect `garbage-collector-controller` among them,
spelled exactly as `:82` spells it — with straight quotation marks, not the curly ones `:84` uses
one line later. Note how many distinct controller names appear; that number is how much of the
component has been converted.

Step 8 should collapse the `logger=` count towards zero and the key-set `diff` should be the
scheduler's result again, at a different scale. If a few `logger=` lines survive with the gate off,
read them: those are call sites passing a `logger` key by hand rather than through `WithName`, and
they are the difference between a structured log call and a contextual one.

Step 9 should change nothing. Both components should restart cleanly, both greps should return no
line that mentions the gate, and the scheduler's output for a new Pod should look exactly like step
4's: `/tmp/bw-v4-again.txt` should carry about as many lines, and about as many `logger=` pairs, as
`/tmp/bw-v4-on.txt` did. That null result *is* the diff: the instruction at `:55-58` is still
accepted, still harmless, and no longer does anything, and nothing in either component's output
tells a reader following the post that they have set a switch to the position it was already in.

Step 10 puts three renderings beside one another: a real klog line from your own cluster, the post's
`:71` and `:82` blockquotes, and the `:84` sentence about `:82`. The real line has no asterisks and
no curly quotation marks anywhere. The `grep -o` counts every emphasis marker in the source, and the
last grep should find typographic quotation marks on `:84` and nowhere else that matters. Neither is
a behaviour that changed; both were wrong the day the post was published, and the rendered page has
carried them ever since.

**Read on**

1. `ContextualLogging.md` in full, and then the three other files that share its defect:
   `DRAWorkloadResourceClaims.md`, `KubeletCgroupDriverFromCRI.md` and
   `DisableNodeKubeProxyVersion.md`. The other three record their unclosed stage at v1.31 or later,
   so each could plausibly be a typing error not yet noticed. This one has been open since v1.24,
   and someone opened the file again at v1.30 to add the beta row underneath it.

2. `docs/concepts/cluster-administration/system-logs.md:123-171`, the only place in the tree that
   documents this feature, read for what it stamps at `:125` and what it demonstrates at `:144-156`.
   The demonstration is a Go program run from a source checkout, and `:151` shows its `--help`
   printing the same `(BETA - default=true)` string your step 1 got from a real binary. The rest of
   that file, and the logging work this feature was built on top of, belong to [the 2020
   structured-logs post](../2020/08-kubernetes-1-19-introducing-structured-logs.md).

3. [The scheduler at `-v=10`, line by line](../../labs/05/12-one-pod-through-schedule-one.md), which
   walks a single Pod through the scheduling cycle against the code that logs it. Read it after step
   4 here: the `logger=` values you counted are the names of the stages that lab walks through, and
   the two exercises are reading the same output at different resolutions.

4. [Two control planes, one flag list](../../labs/01/03-static-pod-flags-vs-local-up.md), for what a
   static Pod manifest is and why editing one is how a flag gets set on this topology. Every step
   above from 3 onward is an edit to a file the kubelet is watching, and that lab is where the
   watching is explained.

5. Unanswerable from the pin: whether the unclosed alpha row is a mistake or a statement. A gate can
   be held at two stages in the sense that different components ship different amounts of the
   feature — the post's own `:14-16` says two components were migrated and `:86` says shared
   packages like client-go still have not been — and a reader could argue the file is recording
   that. Nothing in `content/en` says whether the schema permits it, because the schema is not in
   `content/en`. The KEP the post links at `:110`, KEP-3077, is outside the pin as well. What the
   pin does settle is that no page renders both rows in a way a reader would notice, and that every
   generated artifact downstream of the file reports one stage.

**Teardown**

Put both manifests back from the backups taken in step 1, confirm each restore against its backup,
delete the probe namespace, and re-taint the control plane if you intend to keep the guest for
another exercise. Leave it untainted if the next thing you do is destroy it, which is [the standard
teardown](../../strands/lab-topologies.md#teardown).

```sh
sudo cp /tmp/bw-sched.yaml /etc/kubernetes/manifests/kube-scheduler.yaml
sudo cp /tmp/bw-kcm.yaml /etc/kubernetes/manifests/kube-controller-manager.yaml
sleep 60
diff /tmp/bw-sched.yaml /etc/kubernetes/manifests/kube-scheduler.yaml && echo "scheduler restored"
diff /tmp/bw-kcm.yaml /etc/kubernetes/manifests/kube-controller-manager.yaml && echo "kcm restored"
kubectl -n kube-system get pods -l tier=control-plane
kubectl delete namespace bw-ctxlog --ignore-not-found
rm -f /tmp/bw-sched.yaml /tmp/bw-kcm.yaml
rm -f /tmp/bw-v3-on.txt /tmp/bw-v4-on.txt /tmp/bw-v3-off.txt /tmp/bw-v4-off.txt /tmp/bw-v4-again.txt
rm -f /tmp/bw-keys-on.txt /tmp/bw-keys-off.txt /tmp/bw-kcm-keys-on.txt /tmp/bw-kcm-keys-off.txt
rm -f /tmp/bw-kcm-on.txt /tmp/bw-kcm-off.txt
CP=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
kubectl taint node $CP node-role.kubernetes.io/control-plane=:NoSchedule || true
```
