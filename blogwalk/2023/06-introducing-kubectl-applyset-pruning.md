<a id="introducing-kubectl-applyset-pruning"></a>

# The alpha this post announces is switched on by an environment variable rather than a feature gate, the flag it documents appears nowhere in the generated reference for the command that takes it, and the mode it was built to replace has now been alpha for thirty-two releases

**Post** — [Kubernetes 1.27: Safer, More Performant Pruning in kubectl apply](https://kubernetes.io/blog/2023/05/09/introducing-kubectl-applyset-pruning/),
2023-05-09.

Katrina Verey (independent) and Justin Santa Barbara (Google). 72 lines, 4,224 bytes — the second
shortest of the year's thirteen `walk` posts, and one of the few that announces a replacement rather
than a feature.

**As written**

The post opens on the problem `kubectl apply` has always had. Declarative configuration is "the gold
standard approach to creating or modifying Kubernetes resources", but deleting what is no longer
wanted is the part it does badly, and the `--prune` flag introduced "in Kubernetes version 1.5" was
the answer to that (the post's `:11-15`).

Then it says that answer was built wrong. The existing `--prune` "has design flaws that diminish its
performance and can result in unexpected behaviors", and the post names the root cause precisely:
"the lack of explicit encoding of the previously applied set by the preceding `apply` operation,
necessitating error-prone dynamic discovery". Four consequences follow in one sentence — object
leakage, inadvertent over-selection of resources, limited compatibility with custom resources, and a
coupling to client-side apply that "hinders user upgrades to the superior server-side apply
mechanism" (`:17-23`).

The announcement itself is two sentences. Version 1.27 of `kubectl` introduces "an alpha version of
a revamped pruning implementation", based on a concept called *ApplySet*, which "promises better
performance and safety" (`:25-27`). An ApplySet is then defined: "a group of resources associated
with a *parent* object on the cluster, as identified and configured through standardized labels and
annotations", with additional standardized metadata allowing "accurate identification of ApplySet
*member* objects within the cluster" (`:29-32`).

The invocation is one fence. Set `KUBECTL_APPLYSET=true` in the environment and add `--prune` and
`--applyset` to the command (`:34-39`). By default the parent object is a Secret; a ConfigMap can be
used instead with `--applyset=configmaps/<name>`; if the object does not exist `kubectl` "will
create it for you"; and custom resources "can be enabled for use as ApplySet parent objects"
(`:41-44`).

The last two paragraphs are addressed past the reader. The implementation rests on "a new low-level
specification that can support higher-level ecosystem tools by improving their interoperability",
and the specification is deliberately lightweight so those tools can keep their own grouping systems
while opting in to ApplySet's metadata conventions "to prevent inadvertent changes by other tools
(such as `kubectl`)" (`:46-49`). Then the pitch: try it, send feedback, "ApplySet is under active
development" (`:51-54`). Two further resources close the post — the declarative-configuration task
page, and KEP 3659, whose title the post spells out in full: *ApplySet: `kubectl apply --prune`
redesign and graduation strategy* (`:57-63`).

**As it runs now**

Everything the post says about the mechanism is still true, and the command still works. What has
not happened is the graduation. `declarative-config.md:375-382` at the pin describes not one pruning
mode but two, and calls both of them alpha: allowlist-based pruning "has existed since kubectl v1.5
but is still in alpha due to usability, correctness and performance issues with its design", and
ApplySet-based pruning "was introduced in alpha in kubectl v1.27 as a replacement for
allowlist-based pruning". The page says of the first that "the ApplySet-based mode is designed to
replace it" and then documents both, in two tabs, side by side.

The invocation survives intact. `declarative-config.md:443` gives it as `KUBECTL_APPLYSET=true
kubectl apply -f <directory> --prune --applyset=<name>`, which is the post's `:38` minus the
trailing slash the post puts inside its placeholder. The four sentences about parent objects survive
too, expanded: Secret by default and ConfigMap via `--applyset=configmaps/<name>` at `:446-448`, and
at `:450-455` the full recipe for a custom-resource parent, including the
`applyset.kubernetes.io/is-parent-type: true` label on the CRD and the
`--applyset=<resource>.<group>/<name>` form. What the post does not mention and the page does are
three caveats at `:465-472`: an object may belong to at most one set, `--namespace` is required for
any namespaced parent — "This means that ApplySets spanning multiple namespaces must use a
cluster-scoped custom resource as the parent object" — and a directory needs its own ApplySet name
if pruning it is to be safe.

The "new low-level specification" the post gestures at did get written down, in one place: the label
and annotation reference. Seven entries carry the `applyset.kubernetes.io/` prefix there —
`additional-namespaces` at `labels-annotations-taints/_index.md:137`, `contains-group-kinds` at
`:158`, `contains-group-resources` at `:179`, `id` at `:204`, `is-parent-type` at `:226`, `part-of`
at `:242` and `tooling` at `:257`. That is the whole of it. The string `applyset` occurs in exactly
four files in the whole of `content/en`: this post, one interview, and the two pages named above.

Those two pages disagree with themselves, and with each other, in three separate places, and it is
worth being exact about each because two of the three are settleable at the keyboard.

*First.* `_index.md:179` heads `applyset.kubernetes.io/contains-group-resources` "(deprecated)", and
the note at `:199-202` says it "is currently deprecated and replaced by
`applyset.kubernetes.io/contains-group-kinds`, support for this will be removed in applyset beta or
GA". The body of that same deprecated entry, at `:195-196`, says "in Kubernetes version v1.37, it is
required by kubectl" — and the body of the replacement entry, at `:175-176`, says "as of Kubernetes
version v1.37, it is required by kubectl". The two entries are otherwise the same paragraph twice,
down to the example value. Two annotations, both described as required by the same client in the
same release, one of them deprecated in favour of the other. The page does not say which one kubectl
writes; the object kubectl creates does, and reading it is step 6.

*Second.* `_index.md:221-223` fixes the value of the `applyset.kubernetes.io/id` label and uses

**must** to do it: the ID "must be the base64 encoding (using the URL safe encoding of RFC4648) of
the hash of the group-kind-name-namespace of the object it is on, in the form:
`<base64(sha256(<name>.<namespace>.<kind>.<group>))>`". The prose names four ingredients in one
order and the form names the same four in the reverse order, in the same sentence. Then, thirteen
lines earlier, `:208` gives the example value
`applyset-0eFHV8ySqp7XoShsGvyWFQD3s96yqwHmzc4e0HR1dsY-v1`, which carries a literal prefix and a
literal suffix that no base64 encoding of a hash can produce; `:246` repeats the same value as the
example for `part-of`. So the one written specification of this label disagrees with itself about
the order of its inputs and with its own example about the shape of its output. A cluster settles
both, and computing them is step 7.

*Third.* `declarative-config.md:439` documents `--applyset` as a flag of `kubectl apply`. The pinned
reference for that command, which is generated from the binary, does not. `kubectl_apply/_index.md`
lists `--prune` at `:168-171` and `--prune-allowlist` at `:175-178`, gives two worked `--prune`
examples at `:52-57`, and still carries at `:31` the line "Alpha Disclaimer: the --prune
functionality is not yet complete. Do not use unless you are aware of what the current state is. See
https://issues.k8s.io/34274." It contains the string `applyset` zero times, as does every other page
under `docs/reference/kubectl`. One of those two pages is describing a flag the other's source of
truth does not have, and which of them is right depends on something neither page mentions. Step 1
finds out what.

One more thing is true of this post at the pin and is not about pruning at all. Three lines in
`content/en` link to it, all three from `sig-cli-spotlight.md` — `:104` cites it correctly as the
1.27 alpha of "a new pruning mode in kubectl apply", and then `:108` and `:110` give the same URL as
the reference for KEP 3895, an interactive mode for `kubectl delete`, and for KEP 3104, the `kuberc`
user preferences file. Neither KEP is mentioned in this post. Two of the three citations this post
has in the pinned tree are pointing at the wrong thing.

**What this exercise does not cover, and where it lives**

`declarative-config.md` is a thousand-line page and most of it is about applying rather than
pruning. Its server-side-apply half, and the history of the
`kubectl.kubernetes.io/last-applied-configuration` annotation that allowlist pruning depends on,
belong to the exercise on [the limitation conceded in the last note and contradicted two hundred
lines earlier](../2020/01-kubernetes-1-18-feature-server-side-apply-beta-2.md). That `kubectl diff`
carries `--prune` and `--prune-allowlist` in its own flag list is already read and counted in the
exercise on [the three commands that have to be
retyped](../2019/01-apiserver-dry-run-and-kubectl-diff.md). And the general argument that a
client-side feature has no gate because gates govern servers is made twice already, in the exercises
on [nine features and six fates](../2015/09-some-things-you-didnt-know-about-kubectl.md) and on [the
template-free tool that now ships five flags for running Helm](../2018/03-announcing-kustomize.md);
this one takes it as settled and asks the next question instead.

**The diff, and why**

The post is ***still right***. Every sentence it writes about the mechanism holds at the pin, the
invocation is still the documented invocation, the parent-object rules are still the parent-object
rules, and the specification it promised for ecosystem tools exists and is readable. A reader who
follows the post in 2026 gets a working command.

What has changed is nothing, and that is the finding: the post has been ***overtaken by stasis***.
It announces the 1.27 alpha of a redesign whose KEP the post itself titles *redesign and graduation
strategy*. Ten releases later, at v1.37, ApplySet-based pruning is still alpha, still behind an
environment variable, and still documented in a tab beside the mode it was built to replace — which
is also still alpha, and has been since v1.5. That is thirty-two releases in alpha for the older
mode, and it is a long time by every measure available in the pinned tree. Of the 453
`feature-state` banners under `docs`, 190 name no feature gate, and twelve of those 190 say alpha;
only one of the twelve claims a release older than the allowlist banner does
(`kubelet-files.md:195`, at v1.2). Of the 487 gate files, the longest unbroken alpha any of them
records is 26 releases — `QOSReserved`, alpha from v1.11 with no closing version, so still open at
the pin. The thing this post was written to retire has now been alpha six releases longer than the
longest-running alpha the gate directory knows about, and the replacement has spent its own decade
not graduating.

That case usually has no failure to show at the lab ceiling, and this one is no exception: both
modes work, and neither errors. So *Do* does not try to break anything. It runs the two modes over
the same three manifests and records what each one deletes and what each one leaves — which is the
difference the post was written about, and the only place the argument for the replacement becomes
visible rather than asserted. What it cannot show is why the replacement has not happened; nothing
in the pinned tree records a reason or a target release.

Neither pruning mode has a feature gate, and the reason is worth naming rather than assuming,
because the switch is not the absence of one.

**No gate** — pruning is a client-side operation and gates govern servers, so of the 487 gate files
in the pinned tree none names pruning, ApplySet, or `kubectl`'s own behaviour at all; the nearest
thing is `ServerSideApply.md`, whose stages run alpha at v1.14 through stable ending at v1.31 and
which carries `removed: true`, and which governed the API server rather than the client. What stands
in for a gate here is an environment variable: `KUBECTL_APPLYSET` occurs on exactly two lines under
`docs`, `declarative-config.md:435` and `:443`, and nowhere else. The instruments this exercise
reads instead of a ladder are that variable, the two hand-written banners on the page it appears on
— `:387` and `:428`, both of the `for_k8s_version`/`state` form rather than the `feature_gate_name`
form that 263 of the docs tree's 453 banners use — the generated reference for `kubectl apply`, and
on your own cluster `kubectl apply --help` run twice, once with the variable and once without. Where
a gate would have given a release number, this exercise can only give a behaviour, so step 1
measures it.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 vCPU, 25G, at `10.10.10.180`.
Everything here is a ConfigMap, a Role and a Secret; nothing is scheduled, nothing needs storage,
and the whole exercise is two directories and one namespace. Provision it with the [standard
steps](../../strands/lab-topologies.md#provision) and the [node
baseline](../../strands/lab-topologies.md#node-baseline-steps) if it is not already up, then work
from the node: `ssh zain@10.10.10.180`.

The cluster's own version does not matter much here and the client's version matters entirely. Both
pruning modes are implemented in `kubectl`; the API server only ever sees ordinary applies, patches
and deletes. If your `kubectl` is not the lab's v1.35, step 1 will tell you so before anything else
runs.

**Do**

1. Establish what the switch is. Ask the server for a gate, then ask the client for the flag, twice.

   ```sh
   kubectl version
   kubectl get --raw /metrics | grep -i applyset || echo "no server-side gate by that name"
   kubectl apply --help | grep -- '--applyset' || echo "no --applyset flag"
   kubectl apply --help | grep -- '--prune'
   KUBECTL_APPLYSET=true kubectl apply --help | grep -- '--applyset' || echo "still no --applyset flag"
   ```

2. Write the three manifests once, into a directory you will copy rather than edit. None of them
   names a namespace: every command below passes `-n prune`, which is the same restriction the
   ApplySet caveat at `declarative-config.md:468-470` imposes, arrived at from the other direction.

   ```sh
   mkdir -p /tmp/pruneset-src
   cat > /tmp/pruneset-src/keep.yaml <<'EOF'
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: keep
     labels: { set: pruneset }
   data: { a: "1" }
   EOF
   cat > /tmp/pruneset-src/drop-cm.yaml <<'EOF'
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: drop-cm
     labels: { set: pruneset }
   data: { a: "2" }
   EOF
   cat > /tmp/pruneset-src/drop-role.yaml <<'EOF'
   apiVersion: rbac.authorization.k8s.io/v1
   kind: Role
   metadata:
     name: drop-role
     labels: { set: pruneset }
   rules:
     - apiGroups: [""]
       resources: ["configmaps"]
       verbs: ["get"]
   EOF
   ls /tmp/pruneset-src
   ```

3. Apply the whole directory the old way, and confirm all three objects exist and carry the
   annotation allowlist pruning depends on.

   ```sh
   kubectl create ns prune
   rm -rf /tmp/pruneset && cp -r /tmp/pruneset-src /tmp/pruneset
   kubectl -n prune apply -f /tmp/pruneset
   kubectl -n prune get cm,role -l set=pruneset
   kubectl -n prune get cm keep \
     -o jsonpath='{.metadata.annotations.kubectl\.kubernetes\.io/last-applied-configuration}{"\n"}'
   ```

4. Delete two manifests from the copy and prune with the allowlist mode. Read the output before you
   read the cluster.

   ```sh
   rm /tmp/pruneset/drop-cm.yaml /tmp/pruneset/drop-role.yaml
   kubectl -n prune apply -f /tmp/pruneset --prune -l set=pruneset
   kubectl -n prune get cm,role -l set=pruneset
   ```

5. Now give the allowlist the type it was missing, and run exactly the same command again. Note that
   `kubectl_apply/_index.md:178` describes this flag as "Overwrite the default allowlist", not
   extend it.

   ```sh
   kubectl -n prune apply -f /tmp/pruneset --prune -l set=pruneset \
     --prune-allowlist=rbac.authorization.k8s.io/v1/Role
   kubectl -n prune get cm,role -l set=pruneset
   ```

6. Reset, and apply the same three manifests the new way. Then print every piece of ApplySet
   metadata kubectl put on the parent object it created.

   ```sh
   kubectl delete ns prune --wait
   kubectl create ns prune
   rm -rf /tmp/pruneset && cp -r /tmp/pruneset-src /tmp/pruneset
   KUBECTL_APPLYSET=true kubectl -n prune apply -f /tmp/pruneset --prune --applyset=demo
   kubectl -n prune get secret demo -o jsonpath='{.metadata.labels}{"\n"}'
   kubectl -n prune get secret demo -o jsonpath='{.metadata.annotations}{"\n"}'
   ```

   Which of `applyset.kubernetes.io/contains-group-kinds` and
   `applyset.kubernetes.io/contains-group-resources` appears in that second line is the measurement.
   The reference says both are required by kubectl in this release and that one of them is
   deprecated in favour of the other; the object settles which one this client actually writes.

7. Compute the ID the reference says the parent's label must carry, and compare it with the label
   the parent has. The reference gives the ingredients twice and in two different orders, so hash
   the string both ways. The parent is a Secret named `demo` in namespace `prune`, and its group is
   the core group, which is the empty string — which is why one of the two strings begins with a dot
   and the other ends with one.

   ```sh
   kubectl -n prune get secret demo \
     -o jsonpath='{.metadata.labels.applyset\.kubernetes\.io/id}{"\n"}'
   printf 'demo.prune.Secret.' | openssl dgst -sha256 -binary | base64 | tr '+/' '-_' | tr -d '='
   printf '.Secret.demo.prune' | openssl dgst -sha256 -binary | base64 | tr '+/' '-_' | tr -d '='
   kubectl -n prune get cm keep -o jsonpath='{.metadata.labels}{"\n"}'
   ```

8. Delete the same two manifests from the copy and prune with the ApplySet mode. No allowlist flag,
   no selector.

   ```sh
   rm /tmp/pruneset/drop-cm.yaml /tmp/pruneset/drop-role.yaml
   KUBECTL_APPLYSET=true kubectl -n prune apply -f /tmp/pruneset --prune --applyset=demo
   kubectl -n prune get cm,role -l set=pruneset
   kubectl -n prune get secret demo -o jsonpath='{.metadata.annotations}{"\n"}'
   ```

9. Test the two caveats the page states as restrictions rather than as errors. Run the first without
   a namespace, and the second against a second parent name over objects that already belong to
   `demo`.

   ```sh
   KUBECTL_APPLYSET=true kubectl apply -f /tmp/pruneset --prune --applyset=demo
   KUBECTL_APPLYSET=true kubectl -n prune apply -f /tmp/pruneset --prune --applyset=other
   kubectl -n prune get secret
   ```

10. Offline, in a checkout of `kubernetes/website` at the pin, read the eight places this exercise
    took its claims from and check each one against what your cluster did.

    ```sh
    cd /path/to/kubernetes/website/content/en
    sed -n '375,382p;387p;428p;465,472p' docs/tasks/manage-kubernetes-objects/declarative-config.md
    sed -n '158,177p' docs/reference/labels-annotations-taints/_index.md
    sed -n '179,202p' docs/reference/labels-annotations-taints/_index.md
    sed -n '208p;221,223p;246p' docs/reference/labels-annotations-taints/_index.md
    sed -n '31p;52,57p;168,178p' docs/reference/kubectl/generated/kubectl_apply/_index.md
    grep -c applyset docs/reference/kubectl/generated/kubectl_apply/_index.md
    grep -rli applyset . --include='*.md'
    sed -n '104,110p' blog/_posts/2023/sig-cli-spotlight.md
    ```

**Expect**

Step 1 is the answer to the third disagreement. The server knows nothing: `/metrics` has no
`kubernetes_feature_enabled` series for anything called applyset, because there is no gate and the
feature is not in the server. `kubectl apply --help` prints `--prune` and `--prune-allowlist`, in
the flag list and in two of its own examples, and no `--applyset` anywhere. Set
`KUBECTL_APPLYSET=true` in front of the same `--help` and the flag appears. The generated reference
is built from a binary running without that variable, which is why `applyset` occurs zero times in
it: the page is not out of date, it is accurate about a client that has not been switched on. The
flag does not exist until the variable does.

Steps 3 and 4 are the post's "inadvertent over-selection" and "object leakage" the right way round.
After step 3 all three objects exist and `keep` carries
`kubectl.kubernetes.io/last-applied-configuration`, which is the annotation `--prune` uses to decide
that an object was once applied. After step 4 the apply prints `configmap/drop-cm pruned` and says
nothing whatever about the Role — which is still there. Nothing warned you. The default allowlist is
"a partial list of both namespaced and cluster-scoped types" (`declarative-config.md:401-402`), the
Role's type is not in it, and an object outside the allowlist is not pruned, not reported, and not
distinguishable from an object you meant to keep.

Step 5 deletes the Role, with the same directory, the same selector and the same apply. The only
difference is a flag naming `rbac.authorization.k8s.io/v1/Role`, which you had to know to write.
Both halves of that are the finding: the mode works exactly as documented, and what it prunes is a
function of a flag rather than of what you applied.

Step 6 creates a Secret named `demo` that you never wrote a manifest for, carrying the
`applyset.kubernetes.io/id` label and the `applyset.kubernetes.io/tooling` annotation with a value
naming kubectl and its version. Record which `contains-` annotation is present. Whichever it is, the
reference describes the other one in the same words in the adjacent entry, and one of the two
entries is headed "(deprecated)" — so the page cannot be read as a specification here, and the
object is the only thing that can be.

Step 7 settles the second disagreement and the one folded inside it. At most one of the two hashes
you computed can appear inside the label, and the one that does is the answer to which half of
`_index.md:221-223` is the specification and which half is a slip of the pen. Neither of them is the
label, though: the label begins `applyset-` and ends `-v1`, exactly as the example at `:208` does,
and the formula written with **must** produces neither affix. If neither hash appears in the label
at all, then the formula is wrong about more than its ordering, and what you have measured is that
the only written specification of this label does not describe the only implementation of it. The
third command shows `keep` carrying `applyset.kubernetes.io/part-of` with the parent's full ID,
prefix and suffix included, as `:254` requires it to match.

Step 8 deletes both objects, the ConfigMap and the Role, with no allowlist and no selector. This is
the whole of the post's argument in one command: membership was recorded when the objects were
applied, so pruning does not have to guess what types to look for. Look at the parent's annotations
again and the `contains-` list has shrunk to the types still in the set. The set is explicit, which
is the thing the old mode's "lack of explicit encoding" meant.

Step 9's first command fails before it applies anything, because a namespaced parent needs
`--namespace`; the caveat at `declarative-config.md:468-470` is enforced. Its second command is the
at-most-one-set rule at `:467`, and what you are recording is whether that rule is enforced by the
client or merely stated by the page — run it and read the message rather than trusting either
answer. `kubectl -n prune get secret` afterwards says whether a second parent was created.

**Read on**

1. `declarative-config.md:465-472`, the three caveats, beside `:457-463`, which explains why the
   second one exists: the parent's annotations record which namespaces the set spans, and a
   namespaced parent cannot span more than its own.

2. `labels-annotations-taints/_index.md:137-156`, `applyset.kubernetes.io/additional-namespaces` —
   the one piece of the specification this exercise never touches, because reaching it requires a
   cluster-scoped custom resource as the parent.

3. `kubectl_apply/_index.md:31`. The disclaimer points at `issues.k8s.io/34274`, an issue number
   that predates both pruning modes, and it is attached to `--prune` generally rather than to either
   mode.

4. `declarative-config.md:360-368`, which is what the page recommends *instead* of everything in
   this exercise: `kubectl delete -f <directory>`, on the grounds that it is the only approach that
   is not alpha.

5. *Unanswerable from the pin.* The KEP this post names is titled *redesign and graduation
   strategy*, and nothing in the pinned tree records what the strategy was, what stalled it, or what
   release either mode is aimed at now. The banners give a start version and no end.

**Teardown**

```sh
kubectl delete ns prune --ignore-not-found
rm -rf /tmp/pruneset /tmp/pruneset-src
```

Nothing was written outside that namespace and nothing was changed on the node, so there is no
manifest to restore and no component to restart. Return the guest with the [standard
teardown](../../strands/lab-topologies.md#teardown), or leave it up — this exercise leaves the
cluster exactly as it found it.

Back to the [2023 census](README.md).
