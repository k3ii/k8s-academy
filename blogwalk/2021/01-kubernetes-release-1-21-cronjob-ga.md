<a id="kubernetes-release-1.21-cronjob-ga"></a>

# The census row promises a manifest this post does not contain, the one API claim in it is the only thing here that did not move, and the command it closes with is wrong twice over: a flag name the pin has never spelled that way, and a gate that was deleted for winning

**Post** — [Kubernetes 1.21: CronJob Reaches
GA](https://kubernetes.io/blog/2021/04/09/kubernetes-release-1.21-cronjob-ga/), 2021-04-09, by Alay
Patel (Red Hat) and Maciej Szulik (Red Hat). Ninety-six lines of body, two `##` headings, two SVG
images, no YAML fence and no manifest.

**As written**

The post announces two things at once and treats them as one. The CronJob resource reached general
availability in v1.21 at group version `batch/v1`, and the controller behind it was replaced — a
`v2` controller shipped as alpha in v1.20 and became the default in v1.21.

The reason given for the API promotion is a policy rather than a feature. The post names Kubernetes'
choice to `ensure APIs move beyond beta`, linking the August 2020 post that wrote that policy down,
and says the aim is to stop APIs being `stuck in a "permanent beta" state`. Supporting the beta API
as GA would have meant substantial rework of the existing controller code, so SIG Apps decided
instead to write a new controller and retire the old one gradually. The old one's problems are
described as `several widely recognized issues` and pointed at a single tracking issue,
`kubernetes/kubernetes#82659`.

The middle of the post is a short lesson on how core controllers are supposed to be built, and it
exists to make the rewrite legible. Controllers are control loops that watch resources and move the
cluster toward the desired state. The v1 CronJob controller did not work that way: it performed `a
periodic poll and sweep of all the CronJob objects in your cluster`, as `a single worker
implementation that gets all CronJobs every 10 seconds, iterates over each one of them, and syncs
them to their desired state`. The post dates that design to `almost 5 years ago` and passes
judgement on it — `in hindsight, we can certainly say that such an approach can overload the API
server at scale`.

What replaced it is the standard shape. The post cites the project's own *Writing Controllers*
guidelines, which prescribe shared informers to `receive notifications of adds, updates, and deletes
for a particular resource`; events put keys in a queue, and workers pull them one at a time. The
CronJob v2 controller uses a queue implementing the `DelayingInterface`, so a key can be processed
after a chosen interval: the handler pops a CronJob's key, processes it, and pushes the key back for
the next scheduled time. The post draws two consequences. The first is that the controller `no
longer requires a linear scan of all the CronJobs`. The second is a forecast about operations rather
than architecture — `this controller can be scaled by increasing the number of workers processing
the CronJobs in parallel`. A flowchart SVG carries the information flow from API server through
informer and queue to the reconciliation loop.

The performance section is a measurement, not an argument. A single-node cluster on a VM with 128
GiB of RAM and 64 vCPUs was loaded with 20 CronJobs scheduled every minute plus 2100 scheduled every
20 hours, and then a thousand more at a time until the cluster held 5120 of them. For every thousand
added, the old controller needed `around 90 to 120 seconds more wall-clock time to schedule 20 Jobs
every cycle`; at 5120 CronJobs it took about nine minutes to create twenty Jobs, so `during each
cycle, about 8 schedules were missed`. The new controller `created 20 Jobs without any delay` even
at 6120. A second SVG plots it.

The post closes with two copy-pasteable strings. The new controller exposes `a histogram metric
cronjob_controller_cronjob_job_creation_skew_duration_seconds which helps monitor the time
difference between when a CronJob is meant to run and when the actual Job is created`. And for a
reader still on v1.20 who wants to try the new controller early, there is one command: enable the
`CronJobControllerV2` feature gate for the kube-controller-manager with
`--feature-gate="CronJobControllerV2=true"`.

**As it runs now**

**The API claim is the only thing in this post that did not move.** `batch/v1` is what the pin
serves and what the pin teaches. `concepts/workloads/controllers/cron-jobs.md:19` opens with a
`feature-state` banner reading stable at `v1.21` — the page's own provenance stamp is this post's
headline — and its worked example at `:47` pulls in `examples/application/job/cronjob.yaml`, whose
first line is `apiVersion: batch/v1`. Nothing on the page carries a group-version caveat. The beta
version survives in exactly one place in the whole documentation tree:
`reference/using-api/deprecation-guide.md:89`, under the heading `#### CronJob {#cronjob-v125}`,
where it reads `The batch/v1beta1 API version of CronJob is no longer served as of v1.25` followed
by the migration instruction to `batch/v1`, `available since v1.21`, and the terse verdict `No
notable changes`. Four releases after the post, the version the post replaced stopped being served —
and the guide's assessment of the change is that there was nothing to say about it.

**The census row this exercise is joined to promises a manifest the post does not contain.** The row
ends *Copy the post's manifest as written and the apiserver refuses it; change one line and it
runs.* There is no manifest. The post has no YAML fence at all, and the only `apiVersion` string
anywhere in it is `batch/v1`, which is the one the pin still serves. The row's forecast is not
merely unsupported by the post, it is the reverse of what the post says. Census rows do not change
once written ([#57](https://github.com/k3ii/k8s-academy/issues/57)), so this one stays as it is and
the exercise says what it found. The demonstration the row describes is worth doing and *Do* does
it, using the manifest the pin itself ships rather than one the post never wrote — and the line that
changes is the reader's, not the author's.

**The gate is not gone from the feature-gate list. It moved to the list of the gates that are
gone.** The row also says *at the pin that gate is gone from the feature-gate list entirely*, and
the file is still there:
`reference/command-line-tools-reference/feature-gates/CronJobControllerV2.md`, with three `stages:`
rows and `removed: true`. Its front matter carries `_build: {list: never, render: false}`, which is
what makes it tempting to read the gate as deleted, and those two keys cannot mean that: all 487
gate files in that directory carry both, so if they hid a gate they would hide every gate and both
tables would be empty. What sorts the gates is `removed`. The page at
`feature-gates-removed/index.md` builds its table at `:30` from
`layouts/shortcodes/feature-gate-table.html`, which ranges over the gate directory's page resources
and skips exactly those gates whose `removed` is falsy; the two tables on the main feature-gates
page skip the complement. So `CronJobControllerV2` renders at the pin, on the removed page, with all
three of its stages and both of its version columns intact. What it has lost is not its entry but
its effect — and the same page says so at `:10-11`: `a removed feature gate is different from a
GA'ed or deprecated one in that a removed one is no longer recognized as a valid feature gate`. That
sentence is the difference between a flag that is ignored and a flag that stops a component from
starting, and it is what step 4 measures.

**The flag in the post's closing command is not a flag the pin has ever spelled that way.** Every
component that accepts gates documents `--feature-gates`, plural:
`reference/command-line-tools-reference/kube-controller-manager.md:525` gives it as `--feature-gates
colonSeparatedMultimapStringString`, and the page the post links three words earlier spells it the
same way in both of its own examples, at `feature-gates/index.md:34-35`. A singular `--feature-gate`
appears nowhere in `content/en/docs`. The value syntax has moved as well: the controller manager's
help text at `:528` now describes `comma-separated list of component:key=value pairs`, with the
component defaulting to `kube` and the flag repeatable, so even the corrected spelling takes a shape
the post could not have printed. The post's one command therefore fails at the pin for two
independent reasons, and they fail at different layers — one in flag parsing, before any gate is
looked up, and one in gate validation afterwards.

**The metric was absorbed under a name one token shorter than the one the post prints.**
`reference/instrumentation/metrics.md:119-120` carries
`cronjob_controller_job_creation_skew_duration_seconds`, described as `Time between when a cronjob
is scheduled to be run, and when the corresponding job is created` — a paraphrase of the post's own
closing sentence — and lists it as a stable histogram exported by kube-controller-manager on
`/metrics`. The string the post prints,
`cronjob_controller_cronjob_job_creation_skew_duration_seconds`, occurs nowhere at the pin. The
doubled `cronjob_` reads like a slip, but the pin cannot say whether the post misprinted the name or
the metric was renamed somewhere between v1.21 and v1.37, and a reader cannot tell from either
string which it was. What a reader *can* settle is which name their own controller manager answers
to, which is step 6.

**The forecast in the post's last architectural sentence landed as a flag the post never names.**
`kube-controller-manager.md:266-270` documents `--concurrent-cron-job-syncs int32` with `Default: 5`
and the help text `the number of cron job objects that are allowed to sync concurrently. Larger
number = more responsive jobs, but more CPU (and network) load`. That is precisely the `increasing
the number of workers` the post promises, delivered as an operator-facing knob with a default. The
reference documents the knob and says nothing about why it exists; the post explains why it exists
and does not know it is coming. Neither document mentions the other.

**The pin still explains a user-visible rule by the loop this post retired.** `cron-jobs.md:225` is
a `caution` block: `if startingDeadlineSeconds is set to a value less than 10 seconds, the CronJob
may not be scheduled. This is because the CronJob controller checks things every 10 seconds.` The
ten-second period is the defining property of the controller this post describes being replaced —
the post's own words are `gets all CronJobs every 10 seconds` — and the sentence is the only place
in `concepts/` that states any period for the CronJob controller. Either the constraint outlived the
poll that caused it, or the sentence outlived the constraint. Nothing at the pin distinguishes
those, because nothing at the pin mentions the rewrite at all: the whole page describes deadlines,
missed schedules and the hundred-missed-starts refusal at `:229-233` in terms of a controller that
checks periodically. Step 8 asks one cluster which it is, for one field.

**Two more CronJob gates ran the same ladder after this post, and neither is named in prose
anywhere.** `CronJobTimeZone` went alpha in v1.24 and is `removed: true`;
`CronJobsScheduledAnnotation` went beta in v1.28 and is stable from v1.32 with no closing version
and no `removed` key at all. Both are transcribed in *The ladder*, and neither string occurs
anywhere in `content/en/docs` outside its own gate file. What they gated is documented without them:
`.spec.timeZone` at `cron-jobs.md:176-188` under a `feature-state` banner reading stable at `v1.27`,
with the matching refusal of `TZ` and `CRON_TZ` inside a schedule at `:192-198`, and the annotation
`batch.kubernetes.io/cronjob-scheduled-timestamp` at `:216-218`, dated `starting with Kubernetes
v1.32`. That annotation records `the originally scheduled creation time for the Job` — which is one
half of the subtraction the post's histogram metric performs. The metric measures the skew; the
annotation lets you compute it per Job, four years later, without a metrics endpoint.

**What this exercise does not cover, and where it lives.** The v1.25 removal that finally stopped
serving `batch/v1beta1` is one row of one release's removal list, and the shape of a whole-release
removal event — a dozen API versions going at once, read off the deprecation guide and walked one
manifest at a time — is booked to this year's row on *Kubernetes API and Feature Removals In 1.22*,
four rows further down [the year's census](README.md), for the release where that shape first
arrives. The Job side of `batch` is not here either: `ttlSecondsAfterFinished`, the
`job_controller_*` metrics and the Pod-failure policy belong to their own posts. And the policy this
post leans on for its justification is a 2020 `read` row, [*Moving Forward From
Beta*](../2020/README.md), which is where the argument about permanent betas is recorded rather than
applied.

**The diff, and why**

**Nothing in this post's account of the mechanism broke.** The API is at the group version the post
gives it, under the name the post gives it, promoted in the release the post says. The architecture
the post describes is the architecture the pin's controller manager still runs: a shared informer, a
delaying queue, workers pulling keys. The measurement is unreproducible on lab hardware and is not
contradicted anywhere. A reader who wants to know why CronJob works the way it does will not find a
better account at the pin, because the pin does not contain an account at all — the word `informer`
appears in no CronJob page, and `CronJobControllerV2` appears in no page except its own gate file.

**The post was retired by being agreed with, and that is why its one command fails.** The gate did
not lose an argument. It ran the full ladder — alpha in v1.20, beta and default in v1.21, stable in
v1.22, and then deleted in v1.24 once nothing could be selected any more — and the switch was
removed because there was no longer a second implementation for it to select. The instruction the
post ends with is correct advice about a world in which two controllers existed; what the reader
should do instead is nothing, because the thing the post offers to let them try early is the only
thing their cluster has. The trace the rewrite left in the reference is not the gate but
`--concurrent-cron-job-syncs`, a knob whose existence only makes sense if the controller is
queue-driven, documented without a word about why. This is the template's sixth case and it must not
be read as the fourth: no plan was abandoned here, a forecast was honoured so completely that the
mechanism for opting into it was garbage-collected.

**And the post was wrong when it was published, in one line, twice.** The closing sentence and the
closing command each contain a string that does not exist and never resolved to anything: a metric
name with `cronjob_` twice, and a flag name in the singular. Neither is a translation problem — no
release renamed `--feature-gates` *into* `--feature-gate`, and the page the post itself links to
spells it plural — so a reader who copies either string is not encountering a stale instruction but
an error that shipped. That is the template's third case, with one honest limit: the pin can show
that both strings are wrong *now* and that no documented rename produced them, and it cannot show
what the 2021 site said, so whether the metric name was a typo or a later rename stays in *Read on*
as unanswerable. The command is the sharper of the two, because it fails twice for unrelated reasons
and the first failure hides the second: fix the flag name and the gate rejection appears, which is a
reader's whole afternoon if they assume the first error message was the problem.

**The census row forecast the wrong diff, and the wrongness is the useful part.** The row predicted
an API break — a manifest refused, one line changed — and the API is the one thing in this post that
a reader can still copy without thinking. The break is entirely on the operational side: the flag,
the gate, the metric name. A post that says *this API is now GA* and *here is how to turn the new
implementation on* ages in two different ways at two different speeds, and the row read the title
and priced only the first.

**The ladder**

Three gates, transcribed from their `stages:` lists parsed as YAML. The first is the post's; the
other two are the CronJob gates that came afterwards, and they are here because the post's subject
kept growing gates after the post stopped watching.

```
CronJobControllerV2          alpha  false  1.20 - 1.20
                             beta   true   1.21 - 1.21
                             stable true   1.22 - 1.23
CronJobTimeZone              alpha  false  1.24 - 1.24
                             beta   true   1.25 - 1.26
                             stable true   1.27 - 1.28
CronJobsScheduledAnnotation  beta   true   1.28 - 1.31
                             stable true   1.32 -
```

The first gate's three rows are the shortest complete life in this year's shelf so far: alpha, beta
and stable in three consecutive releases, then removal in v1.24, four releases from first appearance
to deletion. The post is written from the middle row and says so — `Kubernetes 1.21 uses the newer
controller by default` is the `beta true 1.21` line in prose. That exact three-row signature is
carried by no other gate in the pin's 487, which is unusual enough to be worth stating once and no
more than once: 48 distinct `(beta row, stable row)` pairs in the directory are shared by two or
more gates, so matching rows are the rule rather than a finding. Two gates do share this one's beta
and stable rows without sharing its alpha — `BoundServiceAccountTokenVolume` and
`NamespaceDefaultLabelName`, both v1.21 defaults, both since removed.

The third gate has no closing version and no `removed` key, which is what a gate looks like while it
is still on the books: stable, on by default, and awaiting the release that deletes it. It is the
only one of the three a v1.37 kube-controller-manager will still accept on its command line, which
is what makes the three of them a usable experiment rather than a table — step 5 offers all three to
the same binary and gets two different answers.

**Topology**

One node, the [`solo` topology](../../strands/lab-topologies.md#solo) — 4096MB, 4 vCPU, at
`10.10.10.180` — with the control-plane taint removed in step 1, because every Job this exercise
creates has to actually run a Pod. Bring the guest up with [the five provision
steps](../../strands/lab-topologies.md#provision), substituting `topology=solo`, install Kubernetes
with [the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), bring the
cluster up as usual, and confirm one `Ready` node before starting.

One node is not a compromise here, it is the subject. The control plane runs as static Pods, so the
kube-controller-manager's command line is a file on this machine —
`/etc/kubernetes/manifests/kube-controller-manager.yaml` — and steps 3 to 5 edit it, break it on
purpose, read the failure, and put it back. Keep a copy before the first edit. While the controller
manager is down, the API server keeps answering, so `kubectl` works throughout; what stops is
anything that needs a controller, which includes every CronJob firing. Nothing in *Do* schedules
more than about two dozen Jobs, so the post's numbers are not reproducible on this guest and are not
meant to be: what is reproducible is every string the post prints.

**Do**

1. Untaint the single node, confirm the server version, and establish the starting point from the
   API server rather than from the reference: which `batch` versions it serves, and which CronJob
   gates it admits to knowing.

   ```bash
   CP=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl taint node $CP node-role.kubernetes.io/control-plane- || true
   kubectl version -o json | python3 -c 'import json,sys; print(json.load(sys.stdin)["serverVersion"]["gitVersion"])'
   kubectl api-versions | grep '^batch/'
   kubectl api-resources --api-group=batch
   kubectl get --raw /metrics | grep -o 'kubernetes_feature_enabled{name="CronJob[A-Za-z0-9]*"' | sort -u || echo "the apiserver reports no CronJob gate"
   sudo cp /etc/kubernetes/manifests/kube-controller-manager.yaml /root/kcm.yaml.orig
   ```

2. Do what the census row says, with the manifest the pin ships instead of the one the post does not
   have. Take `examples/application/job/cronjob.yaml` — the sample `cron-jobs.md:47` includes and
   the task page walks — put it at the version this post replaced, and apply it. Then change the one
   line.

   ```bash
   kubectl create namespace bw-cron

   cat > /tmp/bw-hello.yaml <<'EOF'
   apiVersion: batch/v1beta1
   kind: CronJob
   metadata:
     name: hello
     namespace: bw-cron
   spec:
     schedule: "* * * * *"
     jobTemplate:
       spec:
         template:
           spec:
             containers:
             - name: hello
               image: busybox:1.28
               imagePullPolicy: IfNotPresent
               command: ["/bin/sh", "-c", "date; echo Hello from the Kubernetes cluster"]
             restartPolicy: OnFailure
   EOF

   kubectl apply -f /tmp/bw-hello.yaml || echo "refused"
   sed -i 's|^apiVersion: batch/v1beta1$|apiVersion: batch/v1|' /tmp/bw-hello.yaml
   kubectl apply -f /tmp/bw-hello.yaml
   kubectl -n bw-cron get cronjob hello -o jsonpath='{.apiVersion}{"\n"}'
   ```

3. Put the post's closing command into the control plane verbatim. Add
   `--feature-gate="CronJobControllerV2=true"` as a new argument to the kube-controller-manager
   static Pod, wait for the kubelet to notice the file changed, and read why the container never
   comes up. The mirror Pod may vanish from `kubectl` entirely while the container is crash-looping,
   so read the kubelet's own log directory on the node.

   ```bash
   KCM=/etc/kubernetes/manifests/kube-controller-manager.yaml
   sudo sed -i 's|^    - --bind-address=|    - --feature-gate="CronJobControllerV2=true"\n    - --bind-address=|' $KCM
   grep -n 'feature-gate' $KCM
   sleep 30
   kubectl -n kube-system get pods -l component=kube-controller-manager || true
   sudo tail -n 5 /var/log/pods/kube-system_kube-controller-manager-*/kube-controller-manager/*.log
   ```

4. Correct only the flag name, leaving the gate alone, and read the second refusal. This is the same
   command with one character added, and it fails for an entirely different reason at an entirely
   different layer.

   ```bash
   sudo sed -i 's|--feature-gate="CronJobControllerV2=true"|--feature-gates=CronJobControllerV2=true|' /etc/kubernetes/manifests/kube-controller-manager.yaml
   grep -n 'feature-gates' /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 30
   sudo tail -n 5 /var/log/pods/kube-system_kube-controller-manager-*/kube-controller-manager/*.log
   ```

5. Offer the same binary the other two gates from *The ladder*, one at a time, then put the file
   back and confirm the controller manager returns. Three gates, the same syntax, and not the same
   answer.

   ```bash
   for g in CronJobTimeZone CronJobsScheduledAnnotation; do
     sudo sed -i "s|--feature-gates=[A-Za-z0-9]*=true|--feature-gates=$g=true|" /etc/kubernetes/manifests/kube-controller-manager.yaml
     sleep 30
     echo "=== $g"
     sudo tail -n 3 /var/log/pods/kube-system_kube-controller-manager-*/kube-controller-manager/*.log
   done

   sudo cp /root/kcm.yaml.orig /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 30
   kubectl -n kube-system get pods -l component=kube-controller-manager
   ```

6. Ask the controller manager which metric name it actually exports. Its `/metrics` endpoint is on
   `127.0.0.1:10257` and wants a bearer token, so grant one to a service account and grep for both
   spellings: the one the post prints and the one the pin documents.

   ```bash
   kubectl create serviceaccount bw-metrics -n bw-cron
   kubectl create clusterrole bw-metrics --non-resource-url=/metrics --verb=get
   kubectl create clusterrolebinding bw-metrics --clusterrole=bw-metrics --serviceaccount=bw-cron:bw-metrics
   TOKEN=$(kubectl create token bw-metrics -n bw-cron)

   curl -sk https://127.0.0.1:10257/metrics -H "Authorization: Bearer $TOKEN" \
     | grep -c 'cronjob_controller_cronjob_job_creation_skew_duration_seconds' || echo "the post's name: 0 lines"
   curl -sk https://127.0.0.1:10257/metrics -H "Authorization: Bearer $TOKEN" \
     | grep '^cronjob_controller_job_creation_skew_duration_seconds' | head -5
   curl -sk https://127.0.0.1:10257/metrics -H "Authorization: Bearer $TOKEN" \
     | grep -o 'kubernetes_feature_enabled{name="CronJob[A-Za-z0-9]*"[^}]*}' | sort -u
   ```

7. Give the controller the post's workload at a scale one guest can hold: twenty CronJobs, every
   minute. Wait for two cycles, then read the histogram the post's closing sentence is about.

   ```bash
   for i in $(seq 1 20); do
     sed "s/^  name: hello$/  name: hello-$i/" /tmp/bw-hello.yaml | kubectl apply -f -
   done
   kubectl -n bw-cron get cronjob --no-headers | wc -l
   sleep 150
   kubectl -n bw-cron get jobs --no-headers | wc -l

   TOKEN=$(kubectl create token bw-metrics -n bw-cron)
   curl -sk https://127.0.0.1:10257/metrics -H "Authorization: Bearer $TOKEN" \
     | grep '^cronjob_controller_job_creation_skew_duration_seconds_bucket' | head -8
   curl -sk https://127.0.0.1:10257/metrics -H "Authorization: Bearer $TOKEN" \
     | grep '^cronjob_controller_job_creation_skew_duration_seconds_sum\|^cronjob_controller_job_creation_skew_duration_seconds_count'
   ```

8. Test the caution at `cron-jobs.md:225` against this cluster. One CronJob with
   `startingDeadlineSeconds` below the ten seconds the page names as the controller's period, and
   one identical CronJob without the field, for three minutes.

   ```bash
   kubectl apply -f - <<'EOF'
   apiVersion: batch/v1
   kind: CronJob
   metadata:
     name: deadline-5
     namespace: bw-cron
   spec:
     schedule: "* * * * *"
     startingDeadlineSeconds: 5
     jobTemplate:
       spec:
         template:
           spec:
             containers:
             - name: hello
               image: busybox:1.28
               imagePullPolicy: IfNotPresent
               command: ["/bin/sh", "-c", "date"]
             restartPolicy: OnFailure
   EOF

   sleep 200
   kubectl -n bw-cron get cronjob deadline-5 -o jsonpath='{.status.lastScheduleTime}{"\n"}'
   kubectl -n bw-cron get jobs -l batch.kubernetes.io/cronjob-name=deadline-5 --no-headers | wc -l
   kubectl -n bw-cron describe cronjob deadline-5 | sed -n '/Events/,$p'
   ```

9. Read the annotation the post's metric became a field for. Every Job the controller created in
   step 7 should carry the originally scheduled time, and the skew the histogram aggregates is the
   subtraction a reader can now do by hand.

   ```bash
   kubectl -n bw-cron get jobs -o json \
     | python3 -c 'import json,sys
   for j in json.load(sys.stdin)["items"][:5]:
       a = j["metadata"].get("annotations", {})
       print(j["metadata"]["name"], a.get("batch.kubernetes.io/cronjob-scheduled-timestamp"), j["metadata"]["creationTimestamp"])'
   kubectl -n bw-cron get jobs -o json | grep -c 'cronjob-scheduled-timestamp'
   ```

10. Finish with the two things the post's subject grew afterwards and the knob its last
    architectural sentence predicted: a time zone, the refusal of the older way of asking for one,
    and `--concurrent-cron-job-syncs` moved off its default of 5.

    ```bash
    kubectl explain cronjob.spec.timeZone
    kubectl -n bw-cron patch cronjob hello --type merge -p '{"spec":{"timeZone":"Etc/UTC"}}'
    kubectl -n bw-cron patch cronjob hello --type merge -p '{"spec":{"schedule":"CRON_TZ=Etc/UTC * * * * *"}}' || echo "refused"

    sudo sed -i 's|^    - --bind-address=|    - --concurrent-cron-job-syncs=20\n    - --bind-address=|' /etc/kubernetes/manifests/kube-controller-manager.yaml
    sleep 30
    kubectl -n kube-system get pods -l component=kube-controller-manager
    TOKEN=$(kubectl create token bw-metrics -n bw-cron)
    curl -sk https://127.0.0.1:10257/metrics -H "Authorization: Bearer $TOKEN" \
      | grep '^cronjob_controller_job_creation_skew_duration_seconds_count'
    ```

**Expect**

Step 1 should report a v1.37 server, and `kubectl api-versions | grep '^batch/'` should print
exactly one line, `batch/v1`. `kubectl api-resources --api-group=batch` should list `cronjobs` and
`jobs` and nothing else. The gate grep should print the fallback message: `CronJobControllerV2` and
`CronJobTimeZone` are both `removed: true` and so are not in any component's feature set, and
`CronJobsScheduledAnnotation` is a kube-controller-manager gate, not an API server one, so the API
server's own `/metrics` has nothing to say about any of the three. That is the expected silence, and
it is why step 6 goes to a different endpoint.

Step 2 is the census row's demonstration, earned honestly. The first `apply` should fail before
anything is admitted, with a message naming the version rather than the object — the API server has
no `batch/v1beta1` to route to, so the error is about an unrecognised group version, not about a bad
CronJob. After the `sed`, the same file applies, and the `jsonpath` should print `batch/v1`. Keep in
mind what has just been shown and what has not: one line changed and it ran, exactly as the row
says, using a manifest that came from `content/en/examples`. The post's contribution to this step is
the sentence saying `batch/v1` is now the version, which is the part that was right.

Step 3 should leave the control plane with one component down and the cluster still answering. The
log tail should show the process exiting immediately on an argument error naming the flag — `unknown
flag: --feature-gate` or the equivalent for the version in the image — with no mention of CronJob,
of the gate, or of features at all. That is the point: flag parsing happens before any gate name is
looked at, so the post's command never gets far enough to discover its second problem. `kubectl -n
kube-system get pods -l component=kube-controller-manager` may show a crash-looping Pod,
`CreateContainerError`, or nothing at all depending on how fast the kubelet gives up; none of those
is informative and the log is.

Step 4 should fail differently. With the flag name corrected the parser accepts the argument and the
feature machinery rejects its value, so the message should name `CronJobControllerV2` and say that
it is not recognised or not a known feature gate. This is the sentence at
`feature-gates-removed/index.md:10-11` executing: a removed gate is not a gate that is ignored, it
is a gate that stops the component. Two edits, two failures, and the first one tells you nothing
about the second.

Step 5 should split the ladder in two. `CronJobTimeZone` is also `removed: true` and should fail
exactly as `CronJobControllerV2` did, with its own name in the message.
`CronJobsScheduledAnnotation` has no `removed` key and a `stable` row still open, so the controller
manager should accept it and come up healthy — setting a stable gate to its default value is a
no-op, which is the entire point of leaving it on the books. After the restore, the component should
be `Running` with a fresh restart count, and everything from step 6 onward depends on that.

Step 6 is the metric question settled for one cluster. The grep for the post's string should report
zero lines; the grep for the documented one should print a `_bucket`, `_sum` and `_count` family, or
the `# HELP` and `# TYPE` headers with no samples yet if no CronJob has fired. Either way, the name
the running binary answers to is the shorter one, which is also the one `metrics.md:119` documents,
and the post's string exists in no version of this cluster. What this does not tell you is whether
it ever existed anywhere. The `kubernetes_feature_enabled` grep should report
`CronJobsScheduledAnnotation` at `true`, and neither removed gate at all.

Step 7 should show twenty-one CronJobs — the one from step 2 and the twenty just made — and, after
two and a half minutes, somewhere between twenty-one and sixty-three Jobs, depending on how many
minute boundaries the wait crossed. The histogram should have samples now, and the `_sum` divided by
the `_count` is this cluster's mean skew in seconds: expect under a second, most samples in the
lowest bucket. That number is the post's claim at 1/256th of the post's scale, so it confirms
nothing about 5120 CronJobs and everything about the shape of the measurement — a reader who wants
the post's graph needs the post's VM, and the histogram is nevertheless the right instrument at
either size. If the Jobs count is zero, the controller manager did not come back in step 5.

Step 8 has two possible outcomes and both are findings. If `status.lastScheduleTime` is empty and no
Job was ever created, the caution at `cron-jobs.md:225` is still describing live behaviour, and the
`Events` on the CronJob should say so — the controller declining to start a Job because it is past
the deadline, repeatedly. If instead the CronJob schedules normally with a five-second deadline, the
constraint has outlived its stated reason: the page's `because` clause is about a ten-second poll
this post retired, and the sentence has stayed put while the mechanism moved. Record which happened
and for which server version, because that is a fact about v1.37 and not about the rule.

Step 9 should print five Jobs, each with a `cronjob-scheduled-timestamp` annotation on a whole
minute boundary and a `creationTimestamp` a fraction of a second later, and the final count should
equal the number of Jobs on the cluster. The difference between the two timestamps on any one Job is
one sample of the histogram in step 7, computed by hand. If the annotation is absent, check that the
server is v1.32 or later and that step 5's restore did not leave a gate argument behind.

Step 10 should show `kubectl explain` describing `timeZone` as the name of a valid time zone, the
merge patch setting `Etc/UTC` cleanly, and the `CRON_TZ` patch rejected by validation with a message
about the schedule — `cron-jobs.md:192-198` promises exactly that refusal. The
`--concurrent-cron-job-syncs=20` edit should bring the controller manager up healthy and change
nothing observable: twenty workers for twenty CronJobs on one node has no work to parallelise, and
the `_count` should keep climbing at the same rate. That is the honest result for the post's
forecast on this hardware. The flag is real, the default is 5, and a single-node guest cannot tell
you what raising it buys.

**Read on**

1. `concepts/workloads/controllers/cron-jobs.md`, whole, and then again looking only for the
   controller. The page is 265 lines and describes scheduling, deadlines, concurrency, suspension,
   history limits, time zones and the hundred-missed-starts refusal without once naming an informer,
   a queue or a rewrite. Read `:19` for the `feature-state` banner that is this post's headline,
   `:38-42` for the 52-character name limit and the eleven characters the controller appends, `:225`
   for the caution step 8 tests, and `:229-247` for the missed-schedules arithmetic — three worked
   examples turning on when the controller was last awake. Then decide whether a reader who has only
   this page knows what kind of program is creating their Jobs.

2. `reference/command-line-tools-reference/kube-controller-manager.md`, for the two flags this
   exercise turns on and what they are surrounded by. `:266-270` is `--concurrent-cron-job-syncs`;
   `:525-528` is `--feature-gates`, whose help text at the pin enumerates every gate the binary
   knows with its stage and default, which makes that one table cell the closest thing the pin has
   to a live inventory. Search it for `CronJob` and count what you find, then compare that count
   against the three gates in *The ladder*. The generated page is also where
   `--concurrent-cron-job-syncs` sits among a dozen other `--concurrent-*-syncs` flags, one per
   controller, which is worth reading as a list: it is the shape of the design this post is arguing
   for, replicated across every controller in the binary.

3. `reference/using-api/deprecation-guide.md`, and specifically how little it says. The CronJob
   entry at `:87-93` is five lines for the removal of the API version this post replaced, and it
   ends `No notable changes`. Read the `### v1.25` section it sits in, count the other resources
   removed in the same release, then read `### v1.22` further up. The contrast is the subject of
   this year's v1.22 removals row rather than of this exercise; the point of reading it here is that
   the guide's format flattens a four-release migration into a bullet and the post that motivated it
   is not linked from anywhere in the guide.

4. The three gate files transcribed in *The ladder*, and then the release that deleted the first
   one. Nine gates in the pin have a last `stages:` row ending at `1.23` and carry `removed: true`,
   which makes them the v1.24 removal cohort: `BoundServiceAccountTokenVolume`,
   `CronJobControllerV2`, `EnableEquivalenceClassCache`, `NamespaceDefaultLabelName`, `NodeLease`,
   `ServiceAccountIssuerDiscovery`, `StartupProbe`, `SupportNodePidsLimit` and
   `SupportPodPidsLimit`. Two of them are already on the shelf — both PID gates are transcribed in
   [the pid-limiting exercise](../2019/05-pid-limiting.md) — and this is the third. Read the six
   that are named nowhere in the walk and decide, for each, whether the archive has no post about it
   or whether the walk has not reached the post yet.

5. Unanswerable from the pin: the history of the two strings this post got wrong. The pin holds one
   CronJob skew metric under one name, and it cannot say whether
   `cronjob_controller_cronjob_job_creation_skew_duration_seconds` was ever exported, was renamed in
   some release between v1.21 and v1.37, or was only ever a typo in this post — step 6 settles which
   name a v1.37 binary answers to and nothing settles which name a v1.21 binary answered to. The
   same gap covers the flag: the pin documents `--feature-gates` everywhere and documents no
   singular form, and it cannot show what the feature-gates page said in April 2021, so `wrong when
   it was published` rests on the absence of any rename rather than on a 2021 reading. It also
   cannot say what the `several widely recognized issues` behind the rewrite were, because the
   post's only pointer to them is a GitHub issue number and the pin does not contain GitHub. And it
   cannot tell you what `--concurrent-cron-job-syncs` is worth: the help text trades responsiveness
   against CPU and network load and names no threshold, the post's own measurement predates the
   flag, and step 10 can only show that raising it costs nothing on one node.

**Teardown**

Remove the namespace and the two cluster-scoped RBAC objects, put the static Pod manifest back to
the copy taken in step 1, and re-taint the control plane if the guest is going to be used for
something else. Deleting the namespace removes all twenty-two CronJobs and every Job and Pod they
made, which takes a minute or so.

```bash
kubectl delete namespace bw-cron --ignore-not-found
kubectl delete clusterrolebinding bw-metrics --ignore-not-found
kubectl delete clusterrole bw-metrics --ignore-not-found
rm -f /tmp/bw-hello.yaml
sudo cp /root/kcm.yaml.orig /etc/kubernetes/manifests/kube-controller-manager.yaml
sudo rm -f /root/kcm.yaml.orig
sleep 30
kubectl -n kube-system get pods -l component=kube-controller-manager
CP=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
kubectl taint node $CP node-role.kubernetes.io/control-plane=:NoSchedule || true
```

Then follow [the teardown procedure](../../strands/lab-topologies.md#teardown) to destroy the guest.
