<a id="dynamic-kubelet-configuration"></a>
# The Node API still carries the field this post is about, still documents its four status subfields in the present tense, and the kubelet stopped reading any of it three years ago

**Post** — [Dynamic Kubelet Configuration](https://kubernetes.io/blog/2018/07/11/dynamic-kubelet-configuration/),
2018-07-11, by Michael Taufen (Google). Kubernetes 1.11, part of the 1.11 in-depth series. Fifty
lines and 4,447 bytes, the smallest `walk` in this year.

This is also the only post in the 2018 census whose first line is a retraction. The pinned copy
opens with an editor's note that was added later: "**The feature has been removed in the version
1.24 after deprecation in 1.22.**" So unlike every other exercise here, the reader is told the
answer before the argument. What the note does not tell them is that the API is still there.

**As written** — a problem, a mechanism, four features and a pointer.

The problem is stated in one paragraph and it is a real one. "Most Kubernetes installations,
however, run the Kubelet as a native process on each host, outside the scope of standard Kubernetes
APIs." So administrators "could not rely on Kubernetes APIs to reconfigure Kubelets in a live
cluster," and were left with three bad options: "either ssh into machines to perform manual
reconfigurations, use third-party configuration management automation tools, or create new VMs with
the desired configuration already installed, then migrate work to the new machines. These
approaches are environment-specific and can be expensive."

The mechanism builds on something that had just shipped. "Kubernetes v1.10 made it possible to
configure the Kubelet via a beta [config file] API. Kubernetes already provides the ConfigMap
abstraction for storing arbitrary file data in the API server." So: put the config file in a
ConfigMap, and "extend the Node object so that a Node can refer to a ConfigMap that contains the
same type of config file."

Four core features are listed:

- the kubelet uses the dynamically assigned configuration;
- it "checkpoints" that configuration to local disk, "enabling restarts without API server
  access";
- it "reports assigned, active, and last-known-good configuration sources in the Node status";
- and on invalid configuration it "automatically falls back to a last-known-good configuration and
  reports errors in the Node status."

Then the workflow, which is the post's central instruction and the thing the exercise turns on:
post a ConfigMap, "then set each Node.Spec.ConfigSource.ConfigMap reference to refer to the new
ConfigMap. Operators can update these references at their preferred rate, giving them the ability
to perform controlled rollouts of new configurations."

The rest is the state machine. Each kubelet watches its own Node object. On a change to
`Node.Spec.ConfigSource.ConfigMap` it writes the ConfigMap's files to local disk, "will then exit,
and the OS-level process manager will restart it." On restart it validates; on success it updates
`Node.Status.Config`; on failure it "will fall back to its last-known-good configuration and report
an error in Node.Status.Config." And if the reference is not set at all, "the Kubelet uses the set
of flags and config files local to the machine it is running on."

One precedence rule is stated explicitly, and it is worth holding onto: "Command-line flags that
overlap with the config file always take precedence over both the local configuration file and
dynamic configurations, for backwards-compatibility."

The post closes with a diagram and a single pointer: "Please see the official tutorial at
/docs/tasks/administer-cluster/reconfigure-kubelet/, which contains more in-depth details on user
workflow, how a configuration becomes 'last-known-good,' how the Kubelet 'checkpoints' config, and
possible failure modes."

**As it runs now** — the feature is gone, the API is not, and the API's documentation has not
caught up in either direction.

**`node.spec.configSource` is still a field in the core `v1` API.** It is at
`node-v1.md:72-73`, typed `NodeConfigSource`, in the Node spec table, and its description is a single
sentence: "Deprecated: Previously used to specify the source of the node's configuration for the
DynamicKubeletConfig feature. This feature is removed." Past tense, no ambiguity, and still
present in the schema of the pin's newest release. That is the whole exercise in one line: the
post's central instruction — set this field — still applies cleanly and does nothing.

**The status half of the same feature was never marked deprecated at all.** Fifty-seven lines down
the same file, `node-v1.md:129-130` documents `node.status.config`, typed `NodeConfigStatus`, and its
description reads: "Status of the config assigned to the node via the dynamic Kubelet config
feature." Present tense. No "Deprecated:" prefix. No note. One page, two halves of one feature,
and only the half you write to says the feature is gone.

**Three different deprecation phrasings appear on that page for one feature.** `:73` says "This
feature is removed." `ConfigMapNodeConfigSource` at `:224` says "This API is deprecated since 1.22"
and links the KEP. `NodeConfigSource` at `:353` says "This API is deprecated since 1.22" with no
link. And `:130` says nothing. Removed, deprecated-since, deprecated-since, and silent — for four
parts of the same thing, in one generated reference.

**The state machine is still documented in full working detail.** `NodeConfigStatus` at
`node-v1.md:368-391` is not a stub. It carries all four subfields the post's third bullet promises
— `active`, `assigned`, `lastKnownGood`, `error` — each with a paragraph in the present tense
describing behaviour that no longer occurs. `assigned` explains that "When Node.Spec.ConfigSource
is updated, the node checkpoints the associated config payload to local disk, along with a record
indicating intended config." `error` explains which failures roll back and which do not: "Earlier
errors (e.g. download or checkpointing errors) will not result in a rollback to LastKnownGood, and
may resolve across Kubelet retries. Later errors (e.g. loading or validating a checkpointed config)
will result in a rollback to LastKnownGood." And `lastKnownGood` supplies a number the post did not
give: "This is currently implemented as a 10-minute soak period starting when the local record of
Assigned config is updated. If the Assigned config is Active at the end of this period, it becomes
the LastKnownGood."

That last paragraph then gives advice about the future: "You should not make assumptions about the
node's method of determining config stability and correctness, as this may change or become
configurable in the future." It is warning the reader against depending on an implementation
detail of a feature that has no implementation. This is a better and more complete description of
how dynamic kubelet configuration worked than the post itself contains, and it is sitting in the
current API reference of a release that cannot do it.

**The post's one pointer is dead, and it never worked as a link.** The path
`/docs/tasks/administer-cluster/reconfigure-kubelet/` does not exist in the pinned tree. That is
expected for a removed feature. What is not expected: grep the whole pinned checkout — docs and
every blog post from 2015 to 2026 — for the string `reconfigure-kubelet` and you get **exactly one
hit, this post's own line 50**. The tutorial the post calls "official" has left no trace anywhere,
including in the redirect and reference machinery that usually catches this. And look at how the
post wrote it: as bare text in a sentence, not as a markdown link. It was never clickable, so it
never showed up as a broken link to any checker. A pointer that was already only a sentence became
a sentence about nothing.

**What replaced it is a flag and a directory on the node.** `kubelet.md:186-189` documents
`--config-dir`: "Path to a directory containing drop-in configuration files that override settings
from defaults and the --config file… Drop-in files must have a '.conf' suffix (e.g.,
'99-kubelet-address.conf') and are processed in lexical order." The task page for it is
`kubelet-config-file.md:103-144`, with the example `--config-dir=/etc/kubernetes/kubelet.conf.d`
(`:107`) and a transition note that dates it: "For Kubernetes v1.28 to v1.29, you can only specify
`--config-dir` if you also set the environment variable `KUBELET_CONFIG_DROPIN_DIR_ALPHA` for the
kubelet process (the value of that variable does not matter)" (`:109-111`).

Set that against the post's opening. The problem it names is that operators had to "ssh into
machines to perform manual reconfigurations" or "use third-party configuration management
automation tools." The pin's answer to the same problem is a directory of `.conf` files on each
machine, populated by whatever put them there. The project accepted the problem and rejected the
API-shaped solution: reconfiguring a kubelet at the pin means changing files on the host, exactly
as it did before v1.11, with the improvement being that the files now compose.

**The pin contradicts itself, twice bolded, about how those files compose.**
`kubelet-config-file.md:117-118` says: "The kubelet processes files in its config drop-in directory
by sorting the **entire file name** alphanumerically." Twenty-five lines later, `:142-143`, inside a
note comparing the mechanism to kubeadm's: "The kubelet determines the order of merges based on
sorting the **suffixes** alphanumerically, and replaces every field present in a higher priority
file." Entire file name, or suffixes. Both emphasised in the source. Both on the same page.

The tree cannot settle it. `kubelet.md:189` — the flag's own help text — says only "processed in
lexical order" and declines to say lexical in what, while adding a fact the task page never
mentions: "All .conf files in the directory and its subdirectories are processed in lexical order."
And both statements on the task page point the reader at
`/docs/reference/node/kubelet-config-directory-merging/` for "more information"; that page exists,
runs 155 lines, and covers only how data *types* merge — structure fields, lists, maps. It contains
no occurrence of "sort", "order", "suffix" or "file name". The two contradictory sentences send you
to a page that does not discuss ordering.

**The post's precedence rule is still right, with one carve-out it could not have predicted.** Post:
command-line flags "always take precedence over both the local configuration file and dynamic
configurations." `kubelet-config-file.md:133-136` gives the pin's merge order, lowest first:

- "Feature gates specified over the command line (lowest precedence)."
- "The kubelet configuration."
- "Drop-in configuration files, according to sort order."
- "Command line arguments excluding feature gates (highest precedence)."

So command-line arguments are still highest — the post's "always" holds — except for
`--feature-gates`, which is now the *lowest* precedence input, below the config file it used to
override. The word doing the work in that list is "excluding". One flag was carved out of a rule
the post states without exception, and the carve-out is only visible from the parenthetical.

**One artifact of the feature is still in the kubelet's own config API.**
`kubelet-config.v1beta1.md:1820-1838` documents `SerializedNodeConfigSource`, whose stated purpose
is "SerializedNodeConfigSource allows us to serialize v1.NodeConfigSource" — the type that exists
to write the removed field to disk during the checkpointing step. Its `source` field links out to
`kubernetes.io/docs/reference/generated/kubernetes-api/v1.36/#nodeconfigsource-v1-core`. That
version in the path is not a comment on this type: all four of the page's cross-references into the
core API name `v1.36`, in a pin whose newest release is v1.37, so the generated page trails the
tree it ships in by one release across the board.

**And the thing the post was built on won outright.** The post's second section credits "a beta
config file API" shipped in v1.10. At the pin, that config file is how the kubelet is configured:
`kubelet.md` marks 105 flags `DEPRECATED`, and 100 of those 105 carry the same appended sentence —
"(DEPRECATED: This parameter should be set via the config file specified by the Kubelet's --config
flag. See https://kubernetes.io/docs/tasks/administer-cluster/kubelet-config-file/ for more
information.)" — and `--config` itself (`:179-182`) is the flag everything else defers to. The ladder below has what
happened to its gate, which is not what happened to the file.

**The diff, and why** — this is a **plan the project abandoned**, and it is the cleanest example of
that case in the year, because the abandonment is so precisely partial. The problem was accepted.
The mechanism was rejected. The API surface was left behind.

Take the three pieces separately, because they came apart.

The **problem** — kubelets are configured outside the API, so fleet reconfiguration is
environment-specific and expensive — was never disputed and is still real. The pin's answer to it
exists and is documented: `--config-dir`, a drop-in directory, a defined merge order. That answer
is not API-centric. It requires something to place files on each host, which is the third-party
configuration management the post lists as one of the bad options. So the project agreed the
problem was worth solving and disagreed that the API server should be the mechanism.

The **mechanism** — a Node field pointing at a ConfigMap, checkpointed to disk, with a
`lastKnownGood` fallback and a 10-minute soak — was built, shipped as beta, defaulted **on** for
eleven releases, deprecated, and removed from the kubelet. The ladder below shows that the whole
arc took twenty-two releases. This is not a feature that failed to land.

The **API surface** is still here, and this is where the post becomes a trap rather than a
historical note. `node.spec.configSource` exists in the current `v1` Node schema. It is writable.
`kubectl patch node` will accept it, the API server will store it, `kubectl get node -o yaml` will
show it back to you, and no kubelet anywhere will read it. The post's central instruction — "set
each Node.Spec.ConfigSource.ConfigMap reference to refer to the new ConfigMap" — succeeds, returns
no error, produces no warning, and has no effect. A field that still applies and does nothing is
worse than a field that was deleted, because a deleted field tells you.

So the mechanism by which this post misleads is not that the docs are out of date. It is that the
docs are out of date *in one direction only*. The spec field says the feature is removed; the
status field describes it in the present tense; the status subfields describe it in more detail
than the post does, including a number the post omits, plus advice about how it might change in
future. If you read the pin from the status side — which is what you do when you are debugging a
node and run `kubectl get node -o yaml` — everything you find says this works.

Release facts and the pressure behind each are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

**The ladder** — two gates. Unlike the IPVS exercise next door, this post's own gate is not
transcribed anywhere else in the archive, so it gets it here, along with the gate for the config
file it was built on.

`DynamicKubeletConfig`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.4 – v1.10 |
| beta | `true` | — | v1.11 – v1.21 |
| deprecated | `false` | — | v1.22 – v1.25 |

`KubeletConfigFile`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.8 – v1.9 |
| deprecated | — | — | v1.10 – v1.10 |

Both files declare `removed: true`. Neither declares `former_titles`. `KubeletConfigFile`'s single
`deprecated` row has **no `defaultValue` at all**, which is why the `default` column is empty
rather than `false`; the transcription prints the absence rather than guessing at it.

Four readings.

**The default flipped inside the deprecation, and that is the whole shape of a retreat.**
`DynamicKubeletConfig` is `beta` with `defaultValue: true` for eleven releases, v1.11 through
v1.21, and this post is written in the first of them. Then one row later it is `deprecated` with
`defaultValue: false`. A repeated stage in a gate file marks a default change; here the change and
the stage change land together, so the same table records both "we turned this on for everyone" and
"we turned it off for everyone" in adjacent rows. Eleven releases is a long time to be on by
default. This was not an experiment that never caught on; it was a shipped default that was
withdrawn.

**The gate file's body disagrees with the gate file's own stages.** The body reads: "Enable the
dynamic configuration of kubelet. The feature is no longer supported outside of supported skew
policy. **The feature gate was removed from kubelet in 1.24.**" The `stages:` list carries the
`deprecated` row to `toVersion: "1.25"`. Cite both and say they disagree: by the body the kubelet
stopped accepting the gate at v1.24, by the stages the gate is documented as existing through
v1.25. The census row for this post takes the body's number, and the table above takes the stages'.
Both are in the same file, eleven lines apart.

**The alpha ran for seven releases before the beta this post announces.** v1.4 to v1.10 is longer
than the whole life of most gates in the tree. Read that against the post's confidence: the four
core features are stated as accomplished facts, and by v1.11 they had been in the tree, off by
default, for seven releases. The post is not announcing new code. It is announcing that a default
changed.

**`KubeletConfigFile` shows the opposite outcome in two rows.** The gate for the config file went
`alpha` at v1.8, and at v1.10 its next and last row is `deprecated` with no default value. The post
says "Kubernetes v1.10 made it possible to configure the Kubelet via a beta config file API" — and
what actually happened at v1.10 is that the gate was retired, because the config file stopped
being optional. A gate deprecated at v1.10 and a mechanism that is now the only supported way to
configure a kubelet are the same event seen from two sides. `DynamicKubeletConfig`'s gate went to
`deprecated` because the feature was being taken away; `KubeletConfigFile`'s went to `deprecated`
because the feature had won. **The stage name does not tell you which.** That is the reading worth
carrying out of this exercise: `deprecated` in a gate file is a statement about the *switch*, not
about the *feature*, and the two gates in this one table point in opposite directions.

The KEP for the removal is linked from the pinned tree itself, at `node-v1.md:224`:
`git.k8s.io/enhancements/keps/sig-node/281-dynamic-kubelet-configuration`. That number is quoted
from the tree, not from memory, and it is the only KEP link on the Node reference page.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair): a control-plane node at
`10.10.10.130` and a worker at `10.10.10.131`. Two nodes are the point. The post's selling
proposition is not "configure a kubelet"; it is "update these references at their preferred rate,
giving them the ability to perform controlled rollouts." A controlled rollout needs somewhere to
roll to. With two nodes you can set the dead field on one and not the other and watch both kubelets
behave identically, and then do the replacement properly with `--config-dir` and see exactly how
much per-host work the API was meant to remove — twice, by hand, over SSH.

Bring it up with [the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=pair`, then [the node baseline](../../strands/lab-topologies.md#node-baseline-steps) on
both, then `ssh zain@10.10.10.130`.

What this cannot show: whether the feature ever worked. Nothing in the lab can exercise the
checkpoint, the soak period or the `lastKnownGood` rollback, because no kubelet in any release you
can install from `pkgs.k8s.io` still contains that code. Every step below that touches
`configSource` is testing the *API server's* willingness to store the field, which is a different
and much smaller claim than the post's. Say so in your notes; the exercise is about the gap between
a schema and an implementation, not about the implementation.

**Do**

1. Confirm the field is still in the schema your cluster is serving. Three ways of asking, because
   they can disagree:

   ```
   kubectl explain node.spec.configSource
   kubectl explain node.status.config
   kubectl get --raw /openapi/v2 | python3 -c 'import sys,json; d=json.load(sys.stdin)["definitions"]; print(json.dumps(d["io.k8s.api.core.v1.NodeConfigSource"], indent=2))'
   ```

2. Read what your cluster says about each half, and compare the wording to the pin:

   ```
   kubectl explain node.spec.configSource | sed -n '1,12p'
   kubectl explain node.status.config | sed -n '1,12p'
   kubectl explain node.status.config.lastKnownGood
   kubectl explain node.status.config.error
   ```

3. Ask the kubelet whether it still has the gate. Do this on both nodes:

   ```
   sudo journalctl -u kubelet --no-pager | grep -ci 'DynamicKubeletConfig' || true
   ps -o args= -C kubelet | tr ' ' '\n' | grep -- '--config\|--feature-gates'
   sudo kubelet --feature-gates=DynamicKubeletConfig=true --help 2>&1 | head -3
   ```

4. Build the post's ConfigMap exactly as instructed — a kubelet config file stored in the API. This
   part still works, because it is only a ConfigMap:

   ```
   sudo cat /var/lib/kubelet/config.yaml | head -20
   kubectl -n kube-system create cm kubelet-config-attempt \
     --from-literal=kubelet="$(printf 'apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nmaxPods: 42\n')"
   kubectl -n kube-system get cm kubelet-config-attempt -o jsonpath='{.data.kubelet}{"\n"}'
   kubectl -n kube-system get cm kubelet-config-attempt -o jsonpath='{.metadata.uid}{"\n"}'
   ```

5. Now the post's central step, on the worker only. Record what the API server does with it:

   ```
   UID=$(kubectl -n kube-system get cm kubelet-config-attempt -o jsonpath='{.metadata.uid}')
   kubectl patch node k8s-worker --type merge -p "$(printf '{"spec":{"configSource":{"configMap":{"name":"kubelet-config-attempt","namespace":"kube-system","uid":"%s","kubeletConfigKey":"kubelet"}}}}' "$UID")"
   echo "exit=$?"
   kubectl get node k8s-worker -o jsonpath='{.spec.configSource}{"\n"}'
   ```

6. Look for every signal the API is supposed to give you when you write to something dead:

   ```
   kubectl patch node k8s-worker --type merge -p '{"spec":{"configSource":null}}' >/dev/null
   kubectl patch node k8s-worker --type merge -p "$(printf '{"spec":{"configSource":{"configMap":{"name":"kubelet-config-attempt","namespace":"kube-system","uid":"%s","kubeletConfigKey":"kubelet"}}}}' "$(kubectl -n kube-system get cm kubelet-config-attempt -o jsonpath='{.metadata.uid}')")" 2>&1 | tee /tmp/patch-out
   grep -ci 'warn\|deprecat' /tmp/patch-out || echo 'no warning of any kind'
   kubectl get --raw '/api/v1/nodes/k8s-worker' -v=6 2>&1 | grep -i 'warning' || echo 'no Warning header'
   ```

7. Wait out the post's state machine and see whether any of it happens:

   ```
   kubectl get node k8s-worker -o jsonpath='{.status.config}{"\n"}'
   kubectl get node k8s-worker -o jsonpath='{.status.config.assigned}{"\n"}'
   kubectl get node k8s-worker -o jsonpath='{.status.config.error}{"\n"}'
   kubectl get node k8s-worker -o jsonpath='{.status.nodeInfo.kubeletVersion}{"\n"}'
   kubectl get node k8s-worker -o jsonpath='{.status.capacity.pods}{"\n"}'
   ```

8. Confirm the field survives a kubelet restart untouched — the post says a change triggers a
   checkpoint and an exit, so a restart is the moment the mechanism would fire:

   ```
   sudo ls -la /var/lib/kubelet/ | grep -i 'checkpoint\|config' || echo 'no checkpoint dir'
   ```

   Then on the worker:

   ```
   ssh zain@10.10.10.131 'sudo systemctl restart kubelet; sleep 15; sudo journalctl -u kubelet --since "-1min" --no-pager | grep -ci "configSource\|checkpoint\|lastKnownGood" || echo 0'
   kubectl get node k8s-worker -o jsonpath='{.spec.configSource.configMap.name}{"\n"}'
   kubectl get node k8s-worker -o jsonpath='{.status.capacity.pods}{"\n"}'
   ```

9. Prove the ConfigMap is inert by breaking it. If anything were reading it, this is where the
   `lastKnownGood` fallback and `status.config.error` would appear:

   ```
   kubectl -n kube-system patch cm kubelet-config-attempt --type merge \
     -p '{"data":{"kubelet":"this is not yaml at all: [["}}'
   ssh zain@10.10.10.131 'sudo systemctl restart kubelet; sleep 15; systemctl is-active kubelet'
   kubectl get node k8s-worker -o jsonpath='{.status.config.error}{"\n"}'
   kubectl get node k8s-worker -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}{"\n"}'
   ```

10. Now do it the way the pin says to. Set `maxPods` on the worker through the replacement
    mechanism, and count the steps it takes:

    ```
    ssh zain@10.10.10.131 'sudo mkdir -p /etc/kubernetes/kubelet.conf.d && \
      printf "apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nmaxPods: 42\n" \
      | sudo tee /etc/kubernetes/kubelet.conf.d/99-maxpods.conf'
    ssh zain@10.10.10.131 'sudo grep -n "config-dir" /var/lib/kubelet/kubeadm-flags.env /etc/systemd/system/kubelet.service.d/*.conf 2>/dev/null || echo "--config-dir is not set anywhere"'
    ```

11. Set the flag, since nothing set it for you. This is the per-host manual step the post's opening
    paragraph exists to eliminate:

    ```
    ssh zain@10.10.10.131 'sudo sed -i "s|KUBELET_KUBEADM_ARGS=\"|KUBELET_KUBEADM_ARGS=\"--config-dir=/etc/kubernetes/kubelet.conf.d |" /var/lib/kubelet/kubeadm-flags.env && cat /var/lib/kubelet/kubeadm-flags.env'
    ssh zain@10.10.10.131 'sudo systemctl restart kubelet; sleep 20; systemctl is-active kubelet'
    kubectl get node k8s-worker -o jsonpath='{.status.capacity.pods}{"\n"}'
    kubectl get node k8s-cp -o jsonpath='{.status.capacity.pods}{"\n"}'
    ```

12. Settle the ordering contradiction on your own node, since the tree will not. Two files that
    differ in the prefix and two that differ in the suffix, and see which pair changes the outcome:

    ```
    ssh zain@10.10.10.131 'cd /etc/kubernetes/kubelet.conf.d && \
      printf "apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nmaxPods: 11\n" | sudo tee 10-aaa.conf >/dev/null && \
      printf "apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nmaxPods: 22\n" | sudo tee 20-aaa.conf >/dev/null && \
      sudo rm -f 99-maxpods.conf && ls'
    ssh zain@10.10.10.131 'sudo systemctl restart kubelet; sleep 20'
    kubectl get node k8s-worker -o jsonpath='{.status.capacity.pods}{"\n"}'
    ```

    Then invert it, so the prefixes sort one way and the suffixes the other:

    ```
    ssh zain@10.10.10.131 'cd /etc/kubernetes/kubelet.conf.d && \
      sudo rm -f 10-aaa.conf 20-aaa.conf && \
      printf "apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nmaxPods: 33\n" | sudo tee 10-zzz.conf >/dev/null && \
      printf "apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nmaxPods: 44\n" | sudo tee 20-aaa.conf >/dev/null && \
      sudo systemctl restart kubelet; sleep 20'
    kubectl get node k8s-worker -o jsonpath='{.status.capacity.pods}{"\n"}'
    ```

13. Test the other undocumented half of the flag's help text — subdirectories, which the task page
    never mentions:

    ```
    ssh zain@10.10.10.131 'cd /etc/kubernetes/kubelet.conf.d && sudo rm -f *.conf && sudo mkdir -p sub && \
      printf "apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nmaxPods: 55\n" | sudo tee sub/50-nested.conf >/dev/null && \
      sudo systemctl restart kubelet; sleep 20'
    kubectl get node k8s-worker -o jsonpath='{.status.capacity.pods}{"\n"}'
    ```

14. Test the precedence carve-out. A flag beats the config file, and `--feature-gates` does not:

    ```
    ssh zain@10.10.10.131 'sudo grep -o "\-\-[a-z-]*" /var/lib/kubelet/kubeadm-flags.env | sort -u'
    ssh zain@10.10.10.131 'cd /etc/kubernetes/kubelet.conf.d && \
      printf "apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nfeatureGates:\n  CustomCPUCFSQuotaPeriod: true\n" | sudo tee 60-gates.conf >/dev/null && \
      sudo sed -i "s|KUBELET_KUBEADM_ARGS=\"|KUBELET_KUBEADM_ARGS=\"--feature-gates=CustomCPUCFSQuotaPeriod=false |" /var/lib/kubelet/kubeadm-flags.env && \
      sudo systemctl restart kubelet; sleep 20; systemctl is-active kubelet'
    kubectl get --raw "/api/v1/nodes/k8s-worker/proxy/configz" | python3 -m json.tool | grep -A4 featureGates
    ```

15. Read the config the kubelet actually ended up with, which is the one answer none of the twelve
    steps above could give you directly:

    ```
    kubectl get --raw "/api/v1/nodes/k8s-worker/proxy/configz" | python3 -c 'import sys,json; c=json.load(sys.stdin)["kubeletconfig"]; print("maxPods:", c.get("maxPods")); print("featureGates:", c.get("featureGates"))'
    kubectl get --raw "/api/v1/nodes/k8s-cp/proxy/configz" | python3 -c 'import sys,json; c=json.load(sys.stdin)["kubeletconfig"]; print("maxPods:", c.get("maxPods"))'
    kubectl get node k8s-worker -o jsonpath='{.spec.configSource}{"\n"}'
    ```

**Expect**

Step 1 is the exercise in three lines. `kubectl explain node.spec.configSource` returns the field
and its "This feature is removed." description; `kubectl explain node.status.config` returns the
field and describes it as live. The OpenAPI definition for `NodeConfigSource` is present with its
`configMap` subfield, because it has to be — the field is part of the served `v1` schema, and
removing it would be a breaking API change. That is why it is still here, and it is the honest
reason: the feature was removable, the field was not.

Step 2 should show you the asymmetry in your own cluster's output rather than in the pin's markdown.
`lastKnownGood` will hand you the 10-minute soak paragraph. Read it and note that it is a claim
about running code, delivered by a v1.37 API server, about behaviour last present in a v1.23
kubelet.

Step 3 should find zero mentions of the gate in the journal and a kubelet whose `--help` either
rejects `DynamicKubeletConfig` as an unrecognised gate or ignores it. Either outcome makes the same
point; record which one you got, because "unrecognised" and "silently ignored" are different
failure modes and the gate file's own body claims the former from v1.24.

Step 4 all works. Nothing in it touches the removed feature: it is a ConfigMap with some YAML in it,
and ConfigMaps are fine. Keep the UID — step 5 needs it, because `ConfigMapNodeConfigSource`
requires `uid` and `kubeletConfigKey`, which is itself worth noticing: the API still validates the
shape of a reference nothing will follow.

Step 5 is the moment. `kubectl patch` prints `node/k8s-worker patched`, exits 0, and
`{.spec.configSource}` reads the value back to you in full. If your node is named differently,
substitute; `kubectl get nodes` has the names. **This is the post's central instruction and it has
just succeeded.**

Step 6 is the search for a warning, and it comes up empty. No `Warning:` line in the patch output,
no `Warning` header in the raw request, no deprecation notice, no admission rejection. Compare this
to what the API server does when you use a genuinely deprecated *API version* — it emits a
`Warning` header the client prints — and note that a deprecated *field* gets none of that
machinery. That asymmetry is the whole reason this post is a trap rather than a curiosity.

Step 7: `status.config` is empty. Not "reporting an error", not "assigned", empty — the kubelet
never writes it, because the code that wrote it is gone. `capacity.pods` is whatever your kubelet's
real config says, which for a kubeadm node is 110, not the 42 in the ConfigMap.

Step 8 finds no checkpoint directory under `/var/lib/kubelet` and no journal lines about
checkpointing, and `configSource` is still set on the Node afterwards, unchanged. The post says a
change to this reference makes the kubelet write files to disk and exit. The kubelet restarts
cleanly and does neither. `capacity.pods` is unchanged.

Step 9 is the negative control and the most useful step for a sceptical reader. You have now put
syntactically invalid YAML in the ConfigMap that the Node's `configSource` points at. If any part
of the mechanism were live, the kubelet would fail validation, roll back to `lastKnownGood`, and
write `status.config.error`. Instead: kubelet `active`, `status.config.error` empty, Node `Ready`.
Nothing read the file.

Step 10 shows that `--config-dir` is not set on a kubeadm node — kubeadm does not configure a
drop-in directory — so the file you just placed does nothing either, for a completely different
reason. Two inert config sources on the same node, one because the feature was removed and one
because the flag was never set.

Step 11 is where the real work happens, and where you should count. You edited
`kubeadm-flags.env`, restarted a service, and did it over SSH, on one host. `capacity.pods` on the
worker becomes 42; on the control-plane node it stays at its default. That difference is the
"controlled rollout" the post promised through the API, achieved by doing exactly the thing the
post's first paragraph describes as expensive. The feature was removed; the need was not.

Step 12 is the experiment the documentation cannot answer for you. With `10-aaa.conf` and
`20-aaa.conf` both rules agree and you get 22. With `10-zzz.conf` and `20-aaa.conf` they disagree:
sorting by **entire file name** processes `10-zzz` then `20-aaa` and yields **44**; sorting by
**suffix** processes `aaa` then `zzz` and yields **33**. Whichever number you get, you have just
settled which of `kubelet-config-file.md:117-118` and `:142-143` is correct at your version, and
the other one is a documentation bug. Write down the number and the version, because that is a
finding, not an exercise answer.

Step 13 should give you 55, matching `kubelet.md:189`'s "directory and its subdirectories" — and if
it does, note that the task page's entire drop-in section describes a flat directory and never
mentions subdirectories at all. The flag's generated help text is more accurate than the
hand-written task page.

Step 14 tests the parenthetical. `CustomCPUCFSQuotaPeriod` is set `true` in a drop-in file and
`false` on the command line. By the post's rule the flag wins and `configz` reports `false`; by
`kubelet-config-file.md:133-136` the command line is the *lowest* precedence input for feature
gates, so the file's `true` should win. Read the answer out of `configz`.

That gate is chosen for three reasons, and they are the reasons to check before substituting
another one. Its `defaultValue` is `false` and it is still alpha at the pin, with a `stages:` list
of one row — `alpha`, `false`, from v1.12, no `toVersion` — so `true` is the non-default value and
a `true` in `configz` can only have come from the drop-in file. It is kubelet-scoped, so the
kubelet will accept it and the API server never sees it. And it is inert: it only *permits* setting
`cpuCFSQuotaPeriod` away from the kernel default, which nothing here does, so enabling it changes
no behaviour on the node. If the file's `true` survives, the post's "always take precedence" now
has an exception, and that is the finding.

Step 15 is the reconciliation. `configz` is the only interface that tells you what the kubelet is
*actually* running, and it exists on the Node proxy — reachable through the API server, which is
mildly ironic given the post's thesis. Compare its `maxPods` against the four places you tried to
set it: the ConfigMap in `configSource` (ignored), the drop-in files (honoured, once the flag was
set), the flags file, and the control-plane node's untouched default. And read `.spec.configSource`
one last time: still set, still stored, still doing nothing.

**Read on** — three questions the pinned tree can answer, and one it cannot.

1. `node-v1.md:72` says "This feature is removed" and `:129` says nothing at all, for two halves of
   one feature in one generated reference. Both descriptions come from Go doc comments on the
   `core/v1` types, so the difference is in the source, not in the site build. Read the two
   descriptions against `ConfigMapNodeConfigSource` at `:224` and `NodeConfigSource` at `:353`, both
   of which say "This API is deprecated since 1.22" — and ask which of the four phrasings a
   client-side deprecation checker could act on.
2. `kubelet-config-file.md:117-118` and `:142-143` contradict each other about drop-in ordering, and
   the reference page they both cite covers only data-type merging. Read
   `/docs/reference/node/kubelet-config-directory-merging/` in full — it is 155 lines, three
   sections, all about structure fields, lists and maps — and ask what the page would need to say
   for either of the two contradictory sentences to be checkable against it.
3. `DynamicKubeletConfig`'s gate body says the gate "was removed from kubelet in 1.24" while its
   `stages:` list runs the `deprecated` row through v1.25. Compare that against
   `KubeletConfigFile`, whose two-row ladder ends at `deprecated` for the opposite reason, and ask
   what `deprecated` in a gate file's stage list is a statement *about* — the switch, the feature,
   or the support commitment.
4. The unanswerable one. The pinned tree does not say why `node.spec.configSource` is still in the
   schema. The API-compatibility rule is the obvious explanation and it is a good one: `v1` is
   stable, so a field cannot be removed, only emptied of meaning. But that explanation predicts a
   *symmetric* treatment — both halves of the feature marked the same way, with the same words, at
   the same time — and that is not what happened. There is no page in the tree recording a decision
   about how to document a field that must remain but must not be used, no convention stated for
   the wording, and no index of such fields. So what cannot be settled here is whether the
   asymmetry between `:72` and `:129` is a deliberate distinction (you write to spec, so spec is
   where the warning belongs) or simply the half that nobody edited. `SerializedNodeConfigSource`
   at `kubelet-config.v1beta1.md:1820-1838`, still documented and still pointing at a v1.36 URL, is
   weak evidence for the second reading, and this exercise cannot get past weak.

Sibling exercises worth reading first, both backward. The kubelet config file that this post builds
on, and where kubeadm actually writes it on a node, is Do-step material in the node-dashboard
exercise
([`../2016/12-visualize-kubelet-performance-with-node-dashboard.md`](../2016/12-visualize-kubelet-performance-with-node-dashboard.md)),
which is the fastest way to get oriented on the file before step 4 here. And the pattern of a
`deprecated` gate row that means two opposite things is the same reading problem as the two IPVS
gates facing opposite directions, worked out in the exercise next door
([`04-ipvs-in-cluster-load-balancing.md`](04-ipvs-in-cluster-load-balancing.md)) — read the two
ladders together and the stage names stop being self-explanatory.

**Teardown** — undo the node edits before the objects, because a kubelet with a bad drop-in file and
no drop-in directory is harder to reason about than one that never had either:

```
ssh zain@10.10.10.131 'sudo rm -rf /etc/kubernetes/kubelet.conf.d && \
  sudo sed -i "s|--config-dir=/etc/kubernetes/kubelet.conf.d ||; s|--feature-gates=CustomCPUCFSQuotaPeriod=false ||" /var/lib/kubelet/kubeadm-flags.env && \
  cat /var/lib/kubelet/kubeadm-flags.env && sudo systemctl restart kubelet'
kubectl patch node k8s-worker --type merge -p '{"spec":{"configSource":null}}'
kubectl -n kube-system delete cm kubelet-config-attempt --ignore-not-found
kubectl get node k8s-worker -o jsonpath='{.status.capacity.pods}{"\n"}'
rm -f /tmp/patch-out
```

Check `capacity.pods` is back to the kubeadm default and both nodes agree before you finish; if the
worker is still reporting 42 or 55, the `sed` did not match and `kubeadm-flags.env` still has
`--config-dir` in it. Then
[tear the topology down](../../strands/lab-topologies.md#teardown).
