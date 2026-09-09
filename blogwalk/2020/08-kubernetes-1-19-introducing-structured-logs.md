<a id="kubernetes-1-19-Introducing-Structured-Logs"></a>

# All eleven klog flags the pinned page says were removed at v1.26 are still documented on one component's reference page, all five generated flag tables permit only text, and the page that lists four components as supporting JSON still stamps it alpha at the release the post carries

**Post** — [Introducing Structured
Logs](https://kubernetes.io/blog/2020/09/04/kubernetes-1-19-Introducing-Structured-Logs/), 4
September 2020, by Marek Siarkowicz (Google) and Nathan Beach (Google). 57 lines, three fenced
blocks and no images, which makes it one of the shortest posts in this year's walk set. It announces
structured logging in Kubernetes 1.19: two new methods on the `klog` library, a default text format
that stays byte-compatible with what came before, and a `--logging-format=json` flag the post itself
labels alpha.

The census row for this post says six years and it never left alpha. Half of that is right.
Structured logging as a *feature* graduated to beta and then grew a successor; the JSON *format* did
not move at all, and the pinned page that documents it still carries the release number in this
post's own title. Separating those two halves is most of the work here, because the pin records them
in three different places that do not agree: a concept page written by hand, a set of flag tables
generated from the components' own flag sets, and a pair of generated configuration references.

**As written**

**Two methods, and one worked pair of samples.** The post's mechanism is a library change: `We've
added two new methods to the klog library: InfoS and ErrorS.` The call it shows is `klog.InfoS("Pod
status updated", "pod", klog.KObj(pod), "status", status)`, and the line it says that call produces
is the block to hold on to, because it is the one piece of the post that survives in the pin
untouched:

```
I1025 00:15:15.525108       1 controller_utils.go:116] "Pod status updated" pod="kube-system/kubedns" status="ready"
```

Everything else in the post is downstream of that one call. The message becomes a quoted string, the
arguments become alternating keys and values, and `klog.KObj(pod)` becomes the `namespace/name` pair
that lets a reader find every line about one object.

**The text format is presented as a compatibility promise, and the JSON one is not.** The post is
explicit that nothing about the existing output changes shape: `To maintain backwards compatibility,
structured logs will still be outputted as a string where the string contains representations of
those "key"="value" pairs.` The very next sentence introduces the second half — `Starting in alpha
in 1.19, logs can also be outputted in JSON format` using a new `--logging-format=json` flag. One
paragraph therefore carries a format described as backward-compatible by construction and a format
described as alpha, and nothing in the post suggests their prospects will differ.

**The JSON sample has four keys and no verbosity.** The post's pretty-printed example is short
enough to quote whole:

```json
{
  "ts": 1580306777.04728,
  "msg": "Pod status updated",
  "pod": {
    "name": "coredns",
    "namespace": "kube-system"
  },
  "status": "ready"
}
```

There is no `v` key, no `err` key, and no statement anywhere in the post of which keys are required.
A reader building a parser off this post would build it against four keys, two of which are the
post's own example payload rather than part of any contract.

**The coverage claim is about volume, and the post itself says the work is not done.** The opening
claims `We have also updated many logging calls such that over 99% of logging volume in a typical
deployment are now migrated to the structured format`, which is a statement about how many *lines* a
running cluster emits and not about how much of the code was converted. The closing section says the
rest out loud: `While we have updated over 99% of the log entries by log volume in a typical
deployment, there are still thousands of logs to be updated.` The post is asking for help finishing,
and that request is worth remembering when the pin is read.

**Five benefits are listed and every one of them belongs to a consumer.** The post promises that
downstream tooling can ingest the data `instead of using regular expressions to parse unstructured
strings`, that entries can be filtered down to `only log entries referencing the particular pod`,
that richer features become possible such as `automated pattern recognition within logs or tighter
correlation of log and trace data`, and that storage costs fall because `most storage systems are
more efficiently able to compress structured key=value data than unstructured strings`. Each of
those is a property of something *reading* the output, so each of them depends on the output being
stable enough to write a reader against. The post never says whether it is, and that is the question
the pin answers.

**As it runs now**

**The text sample survives character for character.** The line the post prints as the output of
`klog.InfoS` is at `concepts/cluster-administration/system-logs.md:111`, byte for byte, six years
later — same timestamp, same goroutine column, same `controller_utils.go:116`, same
`pod="kube-system/kubedns" status="ready"`. The page also gives the shape the line follows, at
`:105`, as `<klog header> "<message>" <key1>="<value1>" <key2>="<value2>" ...`, and adds a detail
the post does not have: strings are quoted, everything else is rendered with `%+v`, and `:114-116`
warns that this `may cause log messages to continue on the next line`. So the format is stable
enough that a sample from 2020 is still the documentation's sample, and unstable enough that a value
can break the line the parser is reading.

**The JSON sample did not survive.** `system-logs.md:190-201` prints the same worked example
reformatted and extended. The indentation went from two spaces to three, `"pod": {` lost its space,
the object moved from `coredns` in `kube-system` to `nginx-1` in `default`, and a key appeared that
the post's sample does not have: `"v": 4`. `:205-208` then names four keys with special meaning —
`ts` required and a float, `v` for info messages only and an int, `err` optional, `msg` required.
Two of those four are absent from the post's example, and one of the two is required.

**The two halves of the post sit at different rungs, and the JSON half is stamped with this post's
own release.** The page marks each section with a feature-state shortcode. Structured Logging is
`{{< feature-state for_k8s_version="v1.23" state="beta" >}}` at `:87`. Contextual Logging, which is
built on top of it, is `{{< feature-state for_k8s_version="v1.30" state="beta" >}}` at `:125`. The
JSON log format is `{{< feature-state for_k8s_version="v1.19" state="alpha" >}}` at `:175`. The
release named in that third shortcode is the release this post announces, and the pin's newest
release is v1.37.

**The flag tables generated from the components' own flag sets know only text.** Every one of the
five component reference pages carries exactly four flags whose name starts with `--log`, and they
are the same four on all five: `--log-flush-frequency`, `--log-text-info-buffer-size`,
`--log-text-split-stream` and `--logging-format`. Two of the four are named for the text format and
there is no `--log-json-` anything anywhere in the reference. The description of `--logging-format`
is identical on all five —

```
Sets the log format. Permitted formats: "text".
```

— at `reference/command-line-tools-reference/kube-apiserver.md:790`,
`kube-controller-manager.md:710`, `kube-scheduler.md:297`, `kubelet.md:560` and `kube-proxy.md:373`.
On the kubelet the same line adds that the flag is `DEPRECATED` and should be set through the config
file instead. Nothing in any of the five tables offers `json` as a permitted value, and each table's
default is `text`.

**Those same tables do know about the logging feature gates.** The `--feature-gates` help on each
page enumerates every gate the binary carries, and on `kube-scheduler.md:178` that list includes
`kube:ContextualLogging=true|false (BETA - default=true)`, `kube:LoggingAlphaOptions=true|false
(ALPHA - default=false)` and `kube:LoggingBetaOptions=true|false (BETA - default=true)`. The two
alpha logging flags on the same page, `--log-text-info-buffer-size` at `:280` and
`--log-text-split-stream` at `:287`, both end with `Enable the LoggingAlphaOptions feature gate to
use this.` So the flag set the pages were generated from knows the gates, knows which alpha logging
options they guard, and offers no JSON option at all.

**Where the JSON format is documented as a first-class thing is the configuration API, not the flag
table.** `reference/config-api/kubelet-config.v1beta1.md:37-52` documents `logging.options.text` and
`logging.options.json`, each marked `[Alpha]` and each carrying `Only available when the
LoggingAlphaOptions feature gate is enabled.` The wrapping `logging.options` field at `:143-152`
says the same, and so do `splitStream` and `infoBufferSize` at `:204-222`. The identical block
appears in `kube-proxy-config.v1alpha1.md` at `:33-48`, `:141-150` and `:202-220`. Two files carry
the name `LoggingAlphaOptions` five times each and no concept or task page in the tree carries it
once. Meanwhile the `format` field itself, at `kubelet-config.v1beta1.md:106-112`, says only `Format
Flag specifies the structure of log messages. default value of format is text` and never names a
second permitted value, and `vmodule` at `:135-141` is `Only supported for "text" log format.`

**All eleven flags the page says were removed at v1.26 are still documented, on one component page
out of five.** `system-logs.md:32-47` states that the flags `are deprecated starting with Kubernetes
v1.23 and removed in Kubernetes v1.26` and lists them. Every one of the eleven is still in the
`kube-proxy.md` flag table at the pin, six of them under the underscore spelling that the page's
hyphenated list does not use:

```
--add-dir-header       kube-proxy.md:48   --add_dir_header
--alsologtostderr      kube-proxy.md:55   --alsologtostderr
--log-backtrace-at     kube-proxy.md:342  --log_backtrace_at
--log-dir              kube-proxy.md:349  --log_dir
--log-file             kube-proxy.md:356  --log_file
--log-file-max-size    kube-proxy.md:363  --log_file_max_size
--logtostderr          kube-proxy.md:377  --logtostderr          Default: true
--one-output           kube-proxy.md:412  --one_output
--skip-headers         kube-proxy.md:461  --skip_headers
--skip-log-headers     kube-proxy.md:468  --skip_log_headers
--stderrthreshold      kube-proxy.md:475  --stderrthreshold      Default: 2
```

None of the eleven appears on any of the other four component pages. Two more klog flags ride along
on the same page and are not in the page's list at all: `--alsologtostderrthreshold` at `:62` and
`--legacy_stderr_threshold_behavior` at `:314`, defaulting to `true`. The second of those occurs
exactly twice in the whole of `content/en`, both times on this one page — once as its own flag and
once inside the description of `--stderrthreshold`, which says its threshold has `no effect when
-logtostderr=true or -alsologtostderr=true unless -legacy_stderr_threshold_behavior=false`. That is
a sentence about the interaction of three flags the same tree says were removed two years earlier.

**The list of components that support JSON is one short, and the missing one is the one that kept
the flags.** `system-logs.md:210-215` gives four: kube-controller-manager, kube-apiserver,
kube-scheduler and kubelet. The flag itself is on five pages. kube-proxy is the component with
`--logging-format` on its reference page and no entry in the support list, and it is also the only
component still carrying the eleven removed flags.

**A warning points at a list that is not there.** `system-logs.md:178-179` says `JSON output does
not support many standard klog flags. For list of unsupported klog flags, see the [Command line tool
reference]` and links `/docs/reference/command-line-tools-reference/`. That page is
`reference/command-line-tools-reference/_index.md`, and it is four lines long: the front-matter
fences, `title: Component tools`, and `weight: 120`. There is no body. No list of unsupported klog
flags exists anywhere in `content/en`, under that heading or any other.

**The migration the post asks for help with is still described as under way.**
`system-logs.md:90-91` warns that `Migration to structured log messages is an ongoing process. Not
all log messages are structured in this version. When parsing log files, you must also handle
unstructured log messages.` The JSON section repeats the shape of the problem at `:181-182`: `Not
all logs are guaranteed to be written in JSON format (for example, during process start). If you
intend to parse logs, make sure you can handle log lines that are not JSON as well.` The post's own
closing line said there were still thousands of calls to convert; six years later the page still
tells readers to write a parser that copes with unconverted output.

**The two methods the post teaches appear nowhere in the tree outside the blog archive.** `InfoS`,
`ErrorS` and `KObj` have zero occurrences in `content/en` outside `blog/_posts`. The apparent
matches are all substrings of unrelated words — `InfoSec` on `tasks/debug/_index.md:66`, and
`ErrorStream` and `InfoStream` in the two config-API references. The contribution the post asks for,
and the API a contributor would write it in, exist only in the post.

**Three separate warnings say the output is not an interface.** The page opens, before its first
heading, with `In contrast to the command line flags described here, the *log output* itself does
*not* fall under the Kubernetes API stability guarantees: individual log entries and their
formatting may change from one release to the next!` at `:21-24`. The Structured Logging section
adds `Log formatting and value serialization are subject to change.` at `:93`. The JSON section adds
`Field names and JSON serialization are subject to change.` at `:184`. Every benefit the post lists
is a benefit to a reader of the output, and the page's answer, given three times, is that readers
get no guarantee.

**What actually happened next is a feature the post does not mention.** `system-logs.md:123-171`
documents Contextual Logging, beta at v1.30, `gated behind the ContextualLogging feature gate and is
enabled by default`, with the note at `:136-138` that `The infrastructure for this was added in 1.24
without modifying components.` It is built on the structured calls this post introduces: the same
key-value pairs, with a logger carried through the call graph so that the pairs accumulate. The
section has aged in place — its worked examples are pinned to `v1.24.0-beta.0` source, its console
samples are dated `I0222 15:13:31`, and `:162` still reads `With contextual logging disable`. The
archive covers contextual logging where it was announced, in years after this one.

**What this exercise does not cover, and where it lives.** Container and Pod logs — what `kubectl
logs` reads, the on-disk layout under `/var/log/pods`, and what a container restart does to a stream
— are the subject of [the 2015 cluster-logging
post](../2015/04-cluster-level-logging-with-kubernetes.md), which also records that a Kubernetes
release no longer ships a logging stack at all. The kubelet's own metrics surface, and what replaced
the node dashboard of that era, are [the 2016 node-dashboard
post](../2016/12-visualize-kubelet-performance-with-node-dashboard.md). cAdvisor, Heapster and the
resource-metrics path are [the 2015 resource-monitoring
post](../2015/02-resource-usage-monitoring-kubernetes.md). Nothing below reads an audit log or a
metrics endpoint; this exercise reads component stdout and nothing else.

**The diff, and why**

**One post, two claims, resolved in opposite directions — and the census row only sees one of
them.** The paragraph at the top of the post carries a text format described as backward compatible
and a JSON format described as alpha. The text format is the half that moved: Structured Logging is
beta from v1.23, its worked example is now the documentation's own worked example, and a successor
feature has been built on top of it and taken to beta as well. The JSON format is the half that did
not: still alpha, still marked with v1.19, absent from every component's flag table, and documented
as a permitted value nowhere in the reference. The census row's `six years and it never left alpha`
is exactly right about the format and exactly wrong about the feature, and the reason it is worth
correcting is that the two halves failed differently. One was overtaken by its own successor. The
other was never wired into the surface that documents it.

**Two pages in the same commit disagree about what the flag accepts, and the disagreement has a
direction.** The five flag tables are generated from the components' flag sets; the concept page is
written by hand. The generated side is internally consistent — four `--log` flags, two of them named
`text`, `Permitted formats: "text"`, and two alpha options that both say `In text format` — which is
what a flag set looks like when the JSON format is not registered in it. The hand-written side has a
flag invocation, a worked sample and a list of supporting components. Neither side is malformed.
What they disagree about is whether the thing the post announces is reachable by the flag the post
names, and only a running cluster can settle it, which is why *Do* asks a cluster rather than
reasoning from the pages. This is a different failure from a page going stale: a generated page
cannot go stale, it can only be generated from something that does not contain the feature.

**The benefit the post sells is the one thing the pin refuses to promise.** Every one of the five
benefits belongs to a consumer of the output, and a consumer needs a contract. The page's answer
appears three times, at `:21-24`, `:93` and `:184`, and the first of the three is placed before the
first heading so that it cannot be missed: log output does not fall under the API stability
guarantees. Read together with the post, that is not a contradiction of anything the post says — the
post never claims stability — but it is a refusal of the thing the post's five benefits require. The
honest reading is that structured logging made the output *parseable* without making it *depended
on*, and the two are not the same achievement.

**Removal reached the code and did not reach the reference.** Eleven flags are declared removed at
v1.26. All eleven are still documented on `kube-proxy.md` at v1.37, six of them under a spelling the
declaration does not use, and one of them still describes its interaction with two others and with a
fourth flag that appears nowhere else in the tree. This is not a page that forgot to be updated by
hand: it is generated, so what it says is that something in the generation path still carries flags
the concept page says are gone. And kube-proxy is the same component the JSON support list omits,
which makes it the one component where both halves of the pin's logging story are wrong.

**A warning that points at a list that has never existed.** The JSON section tells the reader that
some klog flags are unsupported and sends them to a page for the list. The page is a four-line stub.
The failure is small and it is instructive, because it is the one place in this subject where the
pin makes a promise about its own contents that can be checked in a second and found false — and
where a reader who followed the pointer would conclude the flags are supported after all.

**The census row's tag claim is wrong, and the correction matters for reading order.** The row calls
this `The year's only obs walk, and the tag's first since the taxonomy was frozen.` The first clause
holds: 2020 has three `obs` rows and the other two are one `skip` and one `read`. The second does
not. Three `obs` rows in earlier years are `walk` verdicts in the same frozen census — [Resource
Usage Monitoring in Kubernetes](../2015/02-resource-usage-monitoring-kubernetes.md) from May 2015,
[Cluster Level Logging with Kubernetes](../2015/04-cluster-level-logging-with-kubernetes.md) from
June 2015, and [Visualize Kubelet Performance with Node
Dashboard](../2016/12-visualize-kubelet-performance-with-node-dashboard.md) from November 2016. This
is the tag's fourth walk, not its first, and the three that precede it are the three the ceding
paragraph above hands territory to.

**The ladder**

**No gate carries this feature's name.** Of the 487 gate files at the pin, not one is named for
structured logging and not one for the JSON log format. The state of both is recorded only in the
three feature-state shortcodes on the concept page. Three gates do govern logging, all three arrived
at v1.24 — five releases after this post — and the post names none of them. Transcribed from
`reference/command-line-tools-reference/feature-gates/`:

```
ContextualLogging    alpha false 1.24
                     beta  true  1.30
LoggingAlphaOptions  alpha false 1.24
LoggingBetaOptions   beta  true  1.24
```

**Their bodies are one sentence each.** `ContextualLogging` reads `Enables extra details in log
output of Kubernetes components that support contextual logging.` `LoggingAlphaOptions` reads `Allow
fine-tuning of experimental, alpha-quality logging options.` `LoggingBetaOptions` reads `Allow
fine-tuning of experimental, beta-quality logging options.` None of the three names a format. Two of
them name a *quality tier* and leave which options belong to it to be discovered from the flag
tables and the configuration references, which is where the `[Alpha]` markers on `splitStream`,
`infoBufferSize` and the two `options` sub-objects come from.

**Two of the three have not moved in thirteen releases, and that is unusual.** Counting across all
487 files: 52 gates have `alpha` as their last stage with no `toVersion` and no `removed` marker,
and 96 have `beta` in that position. Sorted by the release they entered that stage,
`LoggingAlphaOptions` is the sixth-oldest of the 52 and `LoggingBetaOptions` the eighth-oldest of
the 96. Only six of the surviving alpha gates and nine of the surviving beta gates date from v1.24
or earlier. So the pair that guards logging options is near the front of the queue of things that
stopped moving, and the pin's newest release is thirteen ahead of where they stopped.

**The one gate that did move is the one the post does not mention.** `ContextualLogging` is the only
logging gate with two rows, and its second row is `beta true 1.30` with no `toVersion` and no
`removed` marker, so it is live and on by default at the pin. It is also the gate whose subject was
built on the post's own mechanism. The ladder therefore says something the prose sections say more
slowly: the part of this post that grew a feature gate is not the part the post is about.

**Topology**

One node, the [`solo` topology](../../strands/lab-topologies.md#solo), fresh. Bring the guest up
with [the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, install Kubernetes with [the node baseline
procedure](../../strands/lab-topologies.md#node-baseline-steps), bring the cluster up as usual, and
confirm one `Ready` node before starting.

The component under the microscope is kube-scheduler, for three reasons. It is a static Pod, so its
flags are one file on disk and a restart is a file edit. Its log stream is bounded and predictable —
a handful of lines per scheduling decision, and a decision happens whenever you create a Pod. And
when it fails to start, the cluster keeps serving; the apiserver would not. The manifest edited
below is the same file [the PodTopologySpread exercise](04-introducing-podtopologyspread.md) edits,
and the backup path is deliberately the same one, `/tmp/bw-scheduler.yaml`, so that a half-finished
run of either exercise is recoverable the same way.

A Pod has to actually bind for the scheduler to log a binding, so the first *Do* step removes the
control plane's `NoSchedule` taint. Three Pods are created over the course of the exercise and all
three are `registry.k8s.io/pause:3.10`; none of them does any work, because the thing being measured
is what the scheduler says about them. The namespace is `bw-slog`.

Two steps run a component image as a one-shot Pod to read a binary's own `--help` output. That is
the only way to compare the pin's flag tables against a flag set, because the tables in the pin were
generated from a build that is not this cluster's build, and no page in the pin says which build.
The comparison is therefore a measurement and not a check: what the tables say is fixed and quoted
above, and what the cluster's binary says is whatever it says.

What one node cannot show: the kube-proxy side of the story at any scale, and the JSON output of any
component other than the scheduler. Both are reachable — kube-proxy runs here as a DaemonSet with
one Pod — but a single node makes the proxy's logs almost empty, so step 7 reads its configuration
rather than its output.

**Do**

1. Untaint the control plane, then ask the cluster what it admits to about logging. Two of the three
   gates from *The ladder* are default `true` and one is default `false`, so all three should appear
   in the live gate metric with values that match the transcription. Then read the kubelet's
   *effective* logging configuration out of `configz`, which is the one place a running component
   publishes the block that `kubelet-config.v1beta1.md` documents:

   ```bash
   CP=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl taint node $CP node-role.kubernetes.io/control-plane:NoSchedule-
   kubectl version -o json | python3 -c 'import json,sys; print(json.load(sys.stdin)["serverVersion"]["gitVersion"])'
   kubectl get --raw /metrics | grep 'kubernetes_feature_enabled.*Logging'
   kubectl get --raw "/api/v1/nodes/$CP/proxy/configz" | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin)["kubeletconfig"]["logging"], indent=2))'
   ```

2. Ask the scheduler's own binary which formats it permits. Run the image the cluster is already
   running, with `--help` as its only argument, and compare the four `--log` flags and the
   `--logging-format` description against `kube-scheduler.md:273-297`:

   ```bash
   IMG=$(kubectl -n kube-system get pod -l component=kube-scheduler -o jsonpath='{.items[0].spec.containers[0].image}')
   echo $IMG
   kubectl run sched-help --image=$IMG --restart=Never -- --help
   sleep 20
   kubectl get pod sched-help
   kubectl logs sched-help | grep -- '--log'
   kubectl logs sched-help | grep -A1 -- '--logging-format'
   ```

3. Set the flag the post names and find out which page the cluster agrees with. The backup taken
   here is the one restored in steps 6 and 10 and again in *Teardown*:

   ```bash
   sudo cp /etc/kubernetes/manifests/kube-scheduler.yaml /tmp/bw-scheduler.yaml
   sudo sed -i '/- kube-scheduler$/a\    - --logging-format=json' \
     /etc/kubernetes/manifests/kube-scheduler.yaml
   grep -c logging-format /etc/kubernetes/manifests/kube-scheduler.yaml
   sleep 30
   kubectl -n kube-system get pods | grep scheduler
   sudo crictl logs --tail 8 $(sudo crictl ps -a --name kube-scheduler -q | head -1) 2>&1 | tail -8
   ```

4. Whatever the previous step produced, count it. This one-liner is used again in step 9, so set it
   once: it reports how many lines came out, how many of them are not JSON at all, and which keys
   appear across the ones that are:

   ```bash
   KEYS='import json,sys
   tot=bad=0
   keys={}
   for l in sys.stdin:
       l=l.strip()
       if not l: continue
       tot+=1
       try: d=json.loads(l)
       except Exception: bad+=1; continue
       for k in d: keys[k]=keys.get(k,0)+1
   print("lines", tot, "not JSON", bad)
   for k in sorted(keys, key=lambda x:-keys[x]): print(keys[k], k)'
   kubectl -n kube-system logs -l component=kube-scheduler --tail=200 | python3 -c "$KEYS"
   ```

5. Make a scheduling decision happen and read what the post's `klog.KObj` does to an object
   reference. This is the post's central claim — that every reference to a Kubernetes object is
   structured the same way — tested against one object whose namespace and name you chose:

   ```bash
   kubectl create namespace bw-slog
   kubectl -n bw-slog run probe --image=registry.k8s.io/pause:3.10 --restart=Never
   kubectl -n bw-slog wait --for=condition=Ready pod/probe --timeout=120s
   KOBJ='import json,sys
   for l in sys.stdin:
       l=l.strip()
       if not l: continue
       try: d=json.loads(l)
       except Exception: continue
       if "probe" not in json.dumps(d): continue
       print(json.dumps(d, sort_keys=True))'
   kubectl -n kube-system logs -l component=kube-scheduler --tail=800 | python3 -c "$KOBJ" | head -6
   ```

6. Now offer the component a flag the pin says was removed seven releases after this post, and one
   that is still documented on a sibling component's page at the pin. Read the container log before
   restoring, because a static Pod that never starts leaves nothing for `kubectl` to describe:

   ```bash
   sudo sed -i '/- kube-scheduler$/a\    - --logtostderr=true' \
     /etc/kubernetes/manifests/kube-scheduler.yaml
   sleep 30
   kubectl -n kube-system get pods | grep scheduler
   sudo crictl logs --tail 10 $(sudo crictl ps -a --name kube-scheduler -q | head -1) 2>&1 | tail -10
   sudo cp /tmp/bw-scheduler.yaml /etc/kubernetes/manifests/kube-scheduler.yaml
   sudo sed -i '/- kube-scheduler$/a\    - --logging-format=json' \
     /etc/kubernetes/manifests/kube-scheduler.yaml
   sleep 30
   kubectl -n kube-system get pods | grep scheduler
   ```

7. Read the one component that the pin's support list leaves out. What flags kube-proxy is actually
   started with, and whether its own configuration object carries a `logging` block at all, are both
   answerable without restarting anything:

   ```bash
   kubectl -n kube-system get ds kube-proxy -o json | python3 -c 'import json,sys
   c = json.load(sys.stdin)["spec"]["template"]["spec"]["containers"][0]
   print("command", c.get("command"))
   print("args", c.get("args"))'
   kubectl -n kube-system get cm kube-proxy -o jsonpath='{.data.config\.conf}' | grep -n 'logging' -A6
   kubectl -n kube-system logs -l k8s-app=kube-proxy --tail=6
   ```

8. Look for the replacement the pin names. `system-logs.md:49-59` hands output redirection to
   `kube-log-runner`, says a prebuilt binary is included in several Kubernetes base images under the
   traditional name `/go-runner` and as `kube-log-runner` in server and node release archives, and
   gives a four-row table of shell equivalences at `:63-68`. Find out whether either name is
   anywhere you can reach:

   ```bash
   command -v kube-log-runner; echo "exit $?"
   ls /usr/local/bin
   API=$(kubectl -n kube-system get pod -l component=kube-apiserver -o jsonpath='{.items[0].spec.containers[0].image}')
   kubectl run runner-probe --image=$API --restart=Never --command -- /go-runner --help
   sleep 20
   kubectl get pod runner-probe
   kubectl logs runner-probe 2>&1 | tail -12
   ```

9. Raise the verbosity and re-measure. `system-logs.md:206` says `v` appears on info messages and
   not on error messages, and `:181-182` says not all logs are guaranteed to be JSON `(for example,
   during process start)`. Both are countable, and a restart guarantees process-start lines are in
   the window:

   ```bash
   grep -n ' --v=' /etc/kubernetes/manifests/kube-scheduler.yaml; true
   sudo sed -i '/ --v=/d' /etc/kubernetes/manifests/kube-scheduler.yaml
   sudo sed -i '/- kube-scheduler$/a\    - --v=4' \
     /etc/kubernetes/manifests/kube-scheduler.yaml
   sleep 40
   kubectl -n kube-system get pods | grep scheduler
   kubectl -n bw-slog run probe2 --image=registry.k8s.io/pause:3.10 --restart=Never
   kubectl -n bw-slog wait --for=condition=Ready pod/probe2 --timeout=120s
   kubectl -n kube-system logs -l component=kube-scheduler --tail=2000 | python3 -c "$KEYS"
   ```

10. Put the manifest back and read the format the post promised would not change. Compare the line
    the scheduler prints about `probe3` against the shape at `system-logs.md:105` and the sample at
    `:111`, and against the sample in the post itself:

    ```bash
    sudo cp /tmp/bw-scheduler.yaml /etc/kubernetes/manifests/kube-scheduler.yaml
    sleep 30
    kubectl -n kube-system get pods | grep scheduler
    kubectl -n bw-slog delete pod probe probe2 --ignore-not-found
    kubectl -n bw-slog run probe3 --image=registry.k8s.io/pause:3.10 --restart=Never
    kubectl -n bw-slog wait --for=condition=Ready pod/probe3 --timeout=120s
    kubectl -n kube-system logs -l component=kube-scheduler --tail=400 | grep probe3
    ```

**Expect**

Step 1 should report a v1.37 server, and the three logging gates should appear in
`kubernetes_feature_enabled` with the values *The ladder* transcribes: `ContextualLogging` at 1,
`LoggingBetaOptions` at 1, `LoggingAlphaOptions` at 0. The kubelet's live `logging` block is the
more interesting half. `kubelet-config.v1beta1.md:1572-1580` documents its default as `Format:
text`, and `:143-152` documents an `options` field holding `text` and `json` sub-objects. Write down
whether `configz` shows an `options` key at all, and whether it has a `json` member — a defaulted
struct printing a field is not the same as a component supporting it.

Step 2 is where the exercise turns, and it has two outcomes. The scheduler's own `--help` prints a
`--logging-format` description, and that description either says `Permitted formats: "text".`,
matching `kube-scheduler.md:297` exactly, or it names JSON as well and the generated page is
therefore not describing this binary. Record which, verbatim. Whichever it is, count the `--log`
flags: `kube-scheduler.md:273-297` documents four, and if the binary offers a different number then
the page and the build have diverged in a second way as well. If the Pod never produces output at
all, `--help` on that image may write to stderr and exit non-zero, in which case `kubectl logs
sched-help` still has it — the Pod's phase will be `Failed` and the log will not be empty.

Step 3 has three outcomes and all three are findings. The scheduler may come back `Running` and its
log may turn into JSON, which means the binary accepts a format the reference page says is not
permitted. It may crashloop, and `crictl logs` will then carry an invalid-value error that usually
names the formats the binary does permit — the most direct answer the cluster can give. Or it may
come back `Running` and keep logging text, which would mean the flag is accepted and ignored. Write
down which, and keep the exact error text if there is one, because it is the only string in this
exercise that comes from the code rather than from a page.

Step 4 should report a line count in the low hundreds. If step 3 produced JSON, the key tally should
be led by `ts` and `msg`, which `system-logs.md:205-208` marks required, and `v` should appear on
most lines but not on all of them — the same page says `v` is `verbosity (only for info and not for
error messages, int)`. Compare that tally against the post's four-key sample, which has no `v` at
all, and against the pin's sample at `:190-201`, which has one. The `not JSON` count should be
greater than zero, because the restart put process-start lines in the window and `:181` says `Not
all logs are guaranteed to be written in JSON format (for example, during process start).` If step 3
produced text, the `not JSON` count equals the line count, and that is the measurement.

Step 5 should print at least one entry mentioning `probe`, and the shape of the object reference in
it is the post's whole argument. The post's own sample renders it as `pod="kube-system/kubedns"` in
text, and the pin's JSON sample at `:190-201` renders it as a nested object with `name` and
`namespace`. Write down which of those two shapes your line uses. If nothing matches, widen the
`--tail` and look for `Attempting to bind` or a plugin name instead of the Pod name — the scheduler
logs bindings, not Pod status, and the sample at `system-logs.md:111` is a kube-controller-manager
line, not a scheduler one.

Step 6 has two outcomes and the pin predicts one of them. `system-logs.md:32-47` says
`--logtostderr` was deprecated at v1.23 and removed at v1.26, so the scheduler should refuse to
start and `crictl logs` should show an unknown-flag error. Note that a static Pod that never starts
leaves no `kubectl` object to describe, which is why the log is read through `crictl`. If instead
the scheduler starts, the flag survives in a binary the pin says removed it, and the eleven rows on
`kube-proxy.md` stop looking like a generation artefact and start looking like a description.
manifest Either way the is restored in the same fence, so the run continues from a working cluster.

Step 7 should show kube-proxy started from a config file and not from klog flags — kubeadm passes
`--config` and `--hostname-override`, and nothing else. The question is the ConfigMap.
`kube-proxy-config.v1alpha1.md:141-150` documents a `logging` field on `KubeProxyConfiguration`, and
`:33-48` documents its `options.json` sub-object as `[Alpha]` and gated. Whether kubeadm writes that
block into `config.conf`, and whether it writes `options` underneath it, decides whether the JSON
format is reachable on this component at all. Hold the answer against `system-logs.md:210-215`,
which lists four components as supporting JSON and does not list this one.

Step 8 has two outcomes on the host and two more inside the image. `command -v kube-log-runner`
should fail: it is not a host tool, and `system-logs.md:49-59` never claims it is. Inside the
apiserver image, `/go-runner` either exists and prints its options, which confirms the pin's claim
about base images for at least this image, or the Pod fails to start with an exec error, which means
the claim is about an image set this cluster does not use. Record the container's exit reason either
way. The four-row table at `:63-68` is only checkable in the first case.

Step 9 should raise the line count by roughly an order of magnitude, and if the output is JSON the
`v` values should now spread above 2 where before they did not. The `not JSON` count should rise
too, by at least the process-start lines the restart produced. What matters is the ratio: `:181-182`
tells a reader to `make sure you can handle log lines that are not JSON as well`, and this step is
the only place in the exercise that puts a number on how much handling that is.

Step 10 should return the scheduler to text, and the `probe3` line should have the shape
`system-logs.md:105` describes and resemble the sample at `:111` without matching it — that sample
is the post's sample, carried into the documentation unchanged for six years, and it is a
kube-controller-manager line about Pod status where yours is a scheduler line about binding. The
`"key"="value"` pairs should be quoted the way the post promised they would be. That promise is the
half of this post that held.

**Read on**

1. `concepts/cluster-administration/system-logs.md` in full, all 316 lines. It is the only
   hand-written page in the pin that teaches any of this, and it teaches four features under three
   different feature-state stamps in one document: klog and its flags at `:27-68`, carrying no stamp
   at all, Structured Logging at `:85-121` marked beta at v1.23, Contextual Logging at `:123-171`
   marked beta at v1.30, and the JSON format at `:173-215` marked alpha at v1.19. Read the four
   sections in that order and then read its reviewers, `dims` and `44past4`, neither of whom wrote
   the post. Decide which of the four sections a reader arriving from this post is actually looking
   for.

2. `reference/config-api/kubelet-config.v1beta1.md:37-52` and
   `reference/config-api/kube-proxy-config.v1alpha1.md:33-48`, which are the only two files in
   `content/en` where `LoggingAlphaOptions` appears, five times each. Read the `json` and `text`
   option objects, then `:204-222` and `:202-220` for `splitStream` and `infoBufferSize`, then go
   looking for a concept page or a task page that links either file. There is none. Work out what it
   means that the format this post announces is documented as a first-class configuration field in
   two generated references that nothing points at.

3. The `--log` block on all five component pages:
   `reference/command-line-tools-reference/kube-apiserver.md:766-790`,
   `kube-controller-manager.md:686-710`, `kube-scheduler.md:273-297`, `kubelet.md:536-560` and
   `kube-proxy.md:321-373`. Read the four flags on each, note that two of the four say `In text
   format` in their own descriptions, and then read the eleven flags that survive only on
   `kube-proxy.md` — `--add_dir_header`:48, `--alsologtostderr`:55, `--log_backtrace_at`:342,
   `--log_dir`:349, `--log_file`:356, `--log_file_max_size`:363, `--logtostderr`:377,
   `--one_output`:412, `--skip_headers`:461, `--skip_log_headers`:468, `--stderrthreshold`:475 —
   plus `--alsologtostderrthreshold`:62 and `--legacy_stderr_threshold_behavior`:314, which the
   removal notice at `system-logs.md:32-47` never names.

4. The three gate files transcribed in *The ladder*, and then the population around them.
   `ContextualLogging` moved once, at v1.30. The other two have not moved since v1.24. Read
   `system-logs.md:136-138`, which says contextual logging was `added in 1.24 without modifying
   components`, and then read the typo at `:162` — `With contextual logging disable` — and decide
   how much traffic that section gets. Then compare against [the 2019 PID-limiting
   exercise](../2019/05-pid-limiting.md), which reads two gates that climbed the ladder exactly as
   their post hoped and were deleted for it, and decide which of the two outcomes is the healthier
   one.

5. Unanswerable from the pin: why the two halves diverged. `InfoS`, `ErrorS` and `KObj` — the three
   identifiers the post is built on — appear nowhere in `content/en` outside the blog archive, so
   the pin cannot tell you whether the klog API the post announces still has those names. It cannot
   tell you whether `--logging-format=json` was removed from the components, never wired into the
   release build the reference pages were generated from, or is present and merely undocumented;
   step 2 answers that for one binary on one cluster and no page in the pin answers it at all. And
   it cannot tell you where the `list of unsupported klog flags` at `system-logs.md:178-179` went,
   because `reference/command-line-tools-reference/_index.md` is four lines long and has never held
   a list.

**Teardown**

Restore the manifest, confirm the restore against the backup, and remove the two one-shot Pods in
the default namespace along with the `bw-slog` namespace. Re-taint the control plane if you intend
to keep the guest for another exercise; leave it untainted if the next thing you do is destroy it.

```bash
sudo cp /tmp/bw-scheduler.yaml /etc/kubernetes/manifests/kube-scheduler.yaml
sleep 30
diff /tmp/bw-scheduler.yaml /etc/kubernetes/manifests/kube-scheduler.yaml && echo "manifest restored"
kubectl -n kube-system get pods | grep scheduler
kubectl delete pod sched-help runner-probe --ignore-not-found
kubectl delete namespace bw-slog --ignore-not-found
rm -f /tmp/bw-scheduler.yaml
CP=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
kubectl taint node $CP node-role.kubernetes.io/control-plane=:NoSchedule || true
```

Then follow [the teardown procedure](../../strands/lab-topologies.md#teardown) to destroy the guest.
