<a id="announcing-kustomize"></a>
# Both kustomization files in this post still parse and only one of them still builds, because the overlay's `patches` field kept its name and changed its type; the field list that would tell you so omits two fields the same page's own examples use, names four that the page's own prose has stopped using, and the tool announced here as template-free now ships five flags for running Helm

**Post** — [Introducing kustomize; Template-free Configuration Customization for Kubernetes](https://kubernetes.io/blog/2018/05/29/announcing-kustomize/),
2018-05-29, by Jeff Regan and Phil Wittrock, both then at Google. It names no Kubernetes release,
because the thing it announces does not ship in one: kustomize is a client-side program, and at the
time of writing it was not part of kubectl.

**As written** — an argument in three moves and four code fences, announcing a tool by first
describing the problem it refuses to solve with templates.

The scenario is concrete: *"Somewhere on the internet you find someone's Kubernetes configuration
for a content management system … Then, in some corner of your own company you find a configuration
for a database to back that CMS."* You want both, with your own labels, your own CPU and memory
values, your own replica count, and *"multiple variants of the entire configuration: a small
variant (in terms of computing resources used) devoted to testing and experimentation, and a much
larger variant devoted to serving outside users in production."*

Then the framing that gives the post its title. Copying is one answer and a bad one: *"As with code,
severing the connection to the source material makes it difficult to benefit from ongoing
improvements to the source material."* Templating is the other, and the post's objection to it is
worth having in full, because it is the claim the pinned tree can be read against:

> Another approach to reuse is to express the source material as a parameterized template. A tool
> processes the template—executing any embedded scripting and replacing parameters with desired
> values—to generate the configuration. Reuse comes from using different sets of values with the
> same template. The challenge here is that the templates and value files are not specifications of
> Kubernetes API resources. They are, necessarily, a new thing, a new language, that wraps the
> Kubernetes API.

And the cost of that new language: *"almost every specification that you can include in a YAML file
becomes a parameter that needs a value. As a result, the value sets get large … This defeats one of
the goals of reuse—keeping the differences between the variants small in size and easy to understand
in the absence of a full resource declaration."*

The alternative is a file. *"Compare that to **kustomize**, where the tool's behavior is determined
by declarative specifications expressed in a file called `kustomization.yaml`. The **kustomize**
program reads the file and the Kubernetes API resource files it references, then emits complete
resources to standard output. This text output can be further processed by other tools, or streamed
directly to **kubectl** for application to a cluster."*

The first fence is the smallest possible kustomization file:

```
   commonLabels:
     app: hello
   resources:
   - deployment.yaml
   - configMap.yaml
   - service.yaml
```

Run `kustomize build` beside it and *"emits a YAML stream that includes the three given resources,
and adds a common label `app: hello` to each resource."* The post adds that *"you can use a
*commonAnnotations* field to add an annotation to all resources, and a *namePrefix* field to add a
common prefix to all resource names"*, and calls this *"trivial yet common customization … just the
beginning."*

The second move is bases and overlays: *"The base declares things that the variants share in common
(both resources and a common customization of those resources), and the overlays declare the
differences."* The layout is drawn as a tree:

```
   someapp/
   ├── base/
   │   ├── kustomization.yaml
   │   ├── deployment.yaml
   │   ├── configMap.yaml
   │   └── service.yaml
   └── overlays/
      ├── production/
      │   └── kustomization.yaml
      │   ├── replica_count.yaml
      └── staging/
          ├── kustomization.yaml
          └── cpu_count.yaml
```

with the production overlay's kustomization file given as:

```
   commonLabels:
    env: production
   bases:
   - ../../base
   patches:
   - replica_count.yaml
```

and the patch itself as a partial Deployment carrying nothing but `replicas: 100`. The post's
defence of that shape is the sentence its whole argument rests on: *"The patch, being a partial
deployment spec, has a clear context and purpose and can be validated even if it's read in isolation
from the remaining configuration. It's not just a context free *{parameter name, value}* tuple."*

It closes on the same claim, widened: *"With **kustomize**, you can manage an arbitrary number of
distinctly customized Kubernetes configurations using only Kubernetes API resource files. Every
artifact that **kustomize** uses is plain YAML and can be validated and processed as such."* Then
three invitations: try the hello world example, join the mailing list, open an issue.

**As it runs now** — the tool is inside kubectl, and the shape of both its input and its output has
moved under the post's feet.

*There are two kustomizes, and the pinned tree says so twice.*
`kustomization.md:9-13` opens with *"[Kustomize](…) is a standalone tool to customize Kubernetes
objects through a kustomization file. Since 1.14, kubectl also supports the management of Kubernetes
objects using a kustomization file."* And `management.md:79-82` files it as an external tool:
*"Kustomize traverses a Kubernetes manifest to add, remove or update configuration options. It is
available both as a standalone binary and as a native feature of kubectl."* So the post's `kustomize
build` and the pin's `kubectl kustomize` are two programs with two release cadences, and nothing in
the pinned tree states which version of the first is compiled into the second. `kubectl version`
does not report one; the only handle a learner has on the vendored build's identity is its own flag
list.

*The post's smallest kustomization file is still the shape the docs use, including what it leaves
out.* No pinned example of a kustomization file carries an `apiVersion` or a `kind`:
`kustomize.config.k8s.io` has zero occurrences in the whole pinned tree. Every example is a bare
mapping of fields, exactly as the post prints it.

*The post's first field is documented in one place and used in none.* `commonLabels` appears exactly
once in the pinned tree outside this post: as a row in the Kustomize Feature List at
`kustomization.md:1026`, typed `map[string]string`, described as *"labels to add to all resources and
selectors"*. It appears in no example. What the examples use instead is a different field with a
different shape — `kustomization.md:433-436`:

```
labels:
  - pairs:
      app: bingo
    includeSelectors: true
```

That is a list of objects. The same page's feature list types `labels` as `map[string]string`
(`:1032`) and describes it as *"Add labels without automatically injecting corresponding
selectors"* — which is the opposite of what `includeSelectors: true` asks for. One page, one field,
two incompatible descriptions and a worked example that matches neither. Cite both and say they
disagree; the exercise settles it by building the file.

*The post's second field survives in prose and has been dropped from every example.* `bases:`
occurs exactly once in the whole pinned English tree, and that occurrence is this post. The
documentation still describes the concept in the post's words — an overlay is *"a directory with a
`kustomization.yaml` that refers to other kustomization directories as its `bases`"*, and *"may
refer to multiple `bases`"* (`kustomization.md:867-870`) — while every code example in that same
section writes `resources: - ../base` instead (`:929-939`). The field name is in the prose, in the
feature list at `:1024`, and in none of the code. Whether the vendored build still accepts it is a
question for the cluster, not the page.

*And the post's third field is the one that broke, in the least visible way available.* `patches` is
still a field and still means patches. At the pin it is *"a list of patches applied in the order
they are specified"*, and each entry is an object: *"The patch target selects resources by `group`,
`version`, `kind`, `name`, `namespace`, `labelSelector` and `annotationSelector`"*
(`kustomization.md:535-540`). The worked form is `:597-601`:

```
patches:
  - path: increase_replicas.yaml
  - path: set_memory.yaml
```

The post writes `patches:` with a list of bare filenames. Same field, same meaning, and a type that
went from string to object under one name. That is a harder failure to spot than a removed field: a
removed field gives you an unknown-field error naming the thing you should look up, whereas this
one reports a type mismatch on a field that is still perfectly current.

*The feature list that would settle any of this is missing the two fields the page itself uses.* The
Kustomize Feature List at `kustomization.md:1022-1040` has seventeen rows: `bases`,
`commonAnnotations`, `commonLabels`, `configMapGenerator`, `configurations`, `crds`,
`generatorOptions`, `images`, `labels`, `namePrefix`, `nameSuffix`, `patchesJson6902`,
`patchesStrategicMerge`, `replacements`, `resources`, `secretGenerator`, `vars`. Neither `patches`
nor `namespace` is among them, and the page uses both — `namespace: my-namespace` at `:430`,
`patches` at `:599`. It lists `patchesStrategicMerge` (`:1036`) and `patchesJson6902` (`:1035`), the
two fields whose
work the page's own Customizing section says is now done through `patches`. It lists `vars` (`:1040`) and
`replacements` (`:1037`) side by side with no note that the second exists to replace the first. The one table
in the pinned tree that inventories this file's vocabulary describes a vocabulary the same page has
stopped writing in.

*The post's own starting example is still what kubectl offers, at its 2018 tag.* The post's last
paragraph says *"To get started, try the [hello world] example"*, linking
`kubernetes-sigs/kustomize/blob/master/examples/helloWorld`. The pinned, auto-generated help for
`kubectl kustomize` offers the same example, at a version (`kubectl_kustomize/_index.md:43`):

```
  # Build from github
  kubectl kustomize https://github.com/kubernetes-sigs/kustomize.git/examples/helloWorld?ref=v1.0.6
```

`ref=v1.0.6` is a tag contemporaneous with this post. It is embedded in the binary's help text, so
it is printable from the lab node, and it has outlived every field name the post used.

*The template-free tool has thirteen flags of its own and five of them are for Helm.*
`kubectl_kustomize/_index.md:56-147` lists `--as-current-user`, `--enable-alpha-plugins`,
`--enable-helm`, `-e/--env`, `--helm-api-versions`, `--helm-command` (default `"helm"`),
`--helm-debug`, `--helm-kube-version`, `--load-restrictor` (default
`"LoadRestrictionsRootOnly"`), `--mount`, `--network`, `--network-name`, and `-o/--output`. The
post's argument against templating is untouched as an argument — it is about what a template *is*,
and nothing in the pinned tree contradicts it. What the flag list records is a concession about
where configuration comes from: the tool defined against a template engine will now shell out to
that engine, by name, as a documented option. And `management.md:71-82` puts the two of them
adjacent, Helm first, under one heading for external tools.

*The closing claim — that everything is plain YAML for the API — now has four documented
exceptions.* `kubectl kustomize`'s synopsis calls its output *"a set of KRM resources"*
(`kubectl_kustomize/_index.md:27`), not Kubernetes API objects, and the pinned labels-and-annotations
reference carries four annotations whose specification is the Kubernetes Resource Model Functions
Specification and whose named consumer is this tool: `config.kubernetes.io/local-config` (`:321`),
the reserved prefix `internal.config.kubernetes.io/*` (`:462`), `internal.config.kubernetes.io/path`
(`:479`) and `internal.config.kubernetes.io/index` (`:497`). The first exists to say that an object
is not for the cluster: *"This annotation is used in manifests to mark an object as local
configuration that should not be submitted to the Kubernetes API … For example, Kustomize removes
objects with this annotation from its final build output"* (`:329-340`). The other three are
bookkeeping the orchestrator writes on the way in and strips on the way out — a file path and a
document index, *"not persisted to the manifests on the filesystem"* (`:470-473`). The post says
every artefact is plain YAML that can be validated and processed as such. Two of these annotations
are documented as internal to a process, one marks YAML that must never reach the API server, and
all four are in the Kubernetes reference rather than the tool's.

**The diff, and why** — no feature gate governs any of this, so the diff has to be read from the
tool and the prose rather than from a ladder.

*The post was wrong when published, in its picture rather than its code.* The directory tree at
lines 163-177 is drawn with two defects. The production overlay's children are given as
`│   └── kustomization.yaml` followed by `│   ├── replica_count.yaml` — the last-child marker
before the not-last-child marker, so the drawing closes the directory and then adds a file to it.
And `overlays/` children are indented six columns where `base/` children are indented seven. The
files are the right files in the right directories; the picture of them cannot be produced by any
tree-drawing program. Unlike the unpasteable fences elsewhere in this year, this one costs you
nothing if you read it and everything if you trust it, because the one thing a beginner needs from
that fence is which file sits where.

*The post is still right about YAML tolerating its own formatting.* All four of the post's YAML and tree
fences indent every top-level line by three columns. That is a valid block mapping in YAML, so the fences can
be copied with their leading whitespace intact and still parse — the opposite of the 2018 admission
post, whose fence carried a line-number gutter. Where a fence in this year's archive is unusable, it
is worth checking which kind of unusable it is before retyping it.

*The post broke where a field kept its name.* `patches:` taking a list of strings is the failure,
and the post's overlay is the only artefact here that cannot be built. Everything else in the post
either still works or fails loudly. This one fails on a field that is current, documented and
correctly spelled.

*The post's field names were retired and its concepts were not.* `bases` and `commonLabels` both
survive in the pinned feature list, both have replacements the same page prefers, and neither
replacement is announced anywhere in the pinned tree as a replacement. There is no deprecation
guide for this file — `reference/using-api/deprecation-guide.md` covers API versions, and a
kustomization file is not an API object, so nothing in the tree is obliged to record when its
vocabulary changes. This is the shape a client-side tool's history takes: no gate, no served-until
release, no removal note. The pinned page is the only record, and it disagrees with itself.

*And the argument was won, then quietly qualified.* Nothing in the pin contradicts the post's case
against templates. What the pin adds is `--enable-helm`, `--helm-command`, and a place in the docs
next to Helm rather than opposite it. The tool's premise held; its boundary did not.

**No gate** — kustomize is client-side, so no feature gate has ever governed it: of the 488 gate
files in the pinned tree, none names kustomize or the Kubernetes Resource Model, and exactly one so
much as mentions kubectl. The instruments this exercise reads instead are the vendored build's own
help text (`kubectl kustomize --help`, whose pinned form is
`reference/kubectl/generated/kubectl_kustomize/_index.md`), the Kustomize Feature List at
`tasks/manage-kubernetes-objects/kustomization.md:1022-1040`, and the exit status and stderr of
`kubectl kustomize` itself. Where a gate would have given a release number, this exercise can only
give a behaviour, so it measures it.

That one gate is worth having, because it is about the post's closing promise rather than about the
tool. `ServerSideFieldValidation`:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.23 – v1.24 |
| beta | `true` | — | v1.25 – v1.26 |
| stable | `true` | — | v1.27 – v1.31 |

The file declares `removed: true`, and its body is the only place in 488 gate files where kubectl
appears: *"Enables server-side field validation. This means the validation of resource schema is
performed at the API server side rather than the client side (for example, the `kubectl create` or
`kubectl apply` command line)."* The post says every artefact kustomize uses *"can be validated and
processed as such"*. Between v1.23 and v1.27 the place that validation happens moved off the machine
holding the files and onto the API server — so the claim survived and the thing doing the checking
changed hands. That is checkable from the lab node, and step 13 checks it.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`. Almost
everything here happens before a request is sent: `kubectl kustomize` reads files and writes YAML to
stdout, and needs no cluster at all. The single node exists for the four steps that apply the output
and read it back. Bring it up with
[the five provision steps](../../strands/lab-topologies.md#provision), then
[the node baseline](../../strands/lab-topologies.md#node-baseline-steps), then
`ssh zain@10.10.10.180`.

Say plainly what this cannot show. The standalone `kustomize` binary is not part of a Kubernetes
install, so unless you fetch it yourself only one of the two kustomizes is on this node — and the
exercise is honest about which findings are therefore about kubectl's copy rather than about
kustomize.

**Do**

1. Read the vendored build's own account of itself.

   ```
   kubectl kustomize --help
   kubectl kustomize --help | grep -ci helm
   kubectl version --client
   ```

   Count the flags that are not inherited from kubectl's global set. Find the example that builds
   from GitHub and read the `ref=` on the end of it. Note whether `kubectl version` tells you which
   kustomize this is.

2. Build the post's first example, verbatim, three-space indentation and all.

   ```
   mkdir -p ~/kz/hello && cd ~/kz/hello
   cat > kustomization.yaml <<'YAML'
   commonLabels:
     app: hello
   resources:
   - deployment.yaml
   - configMap.yaml
   - service.yaml
   YAML
   ```

   Write the three resources it names — any valid Deployment, ConfigMap and Service, all called
   `hello` — then:

   ```
   kubectl kustomize . ; echo "exit=$?"
   kubectl kustomize . 2>/dev/null | grep -c 'app: hello'
   ```

   Note whether `commonLabels` is accepted, whether anything is printed on stderr, and how many
   places the label lands — in particular whether it reaches the Deployment's `spec.selector` and
   the Service's `spec.selector`.

3. Now write the same intent in the field the pinned page's example uses.

   ```
   cd ~/kz && cp -r hello labels && cd labels
   cat > kustomization.yaml <<'YAML'
   labels:
     - pairs:
         app: hello
       includeSelectors: true
   resources:
   - deployment.yaml
   - configMap.yaml
   - service.yaml
   YAML
   kubectl kustomize . > /tmp/new.yaml; echo "exit=$?"
   kubectl kustomize ../hello > /tmp/old.yaml
   diff /tmp/old.yaml /tmp/new.yaml && echo IDENTICAL
   ```

   Then set `includeSelectors: false` and diff again. One of these two runs tells you what
   `commonLabels` means in terms the feature list at `kustomization.md:1032` gets wrong.

4. Build the post's tree, exactly as the post draws it — which requires deciding what the drawing
   means.

   ```
   cd ~/kz
   mkdir -p someapp/base someapp/overlays/production someapp/overlays/staging
   ```

   Put the three resources and a `kustomization.yaml` in `base/`, then write the production overlay
   the post gives:

   ```
   cat > someapp/overlays/production/kustomization.yaml <<'YAML'
   commonLabels:
    env: production
   bases:
   - ../../base
   patches:
   - replica_count.yaml
   YAML
   cat > someapp/overlays/production/replica_count.yaml <<'YAML'
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: the-deployment
   spec:
     replicas: 100
   YAML
   ```

   Give the base Deployment the name `the-deployment`, so the patch has something to match.

5. Run the post's own command and read the failure.

   ```
   kubectl kustomize someapp/overlays/production; echo "exit=$?"
   ```

   Write down which field the error names and which one it does not. Before changing anything, say
   which of the overlay's three fields you expect to be the problem.

6. Fix one field at a time, so you learn which changes were actually required.

   ```
   cd ~/kz/someapp/overlays/production
   sed -i 's/^   - replica_count.yaml/   - path: replica_count.yaml/' kustomization.yaml
   kubectl kustomize .; echo "exit=$?"
   sed -i 's/^   bases:/   resources:/' kustomization.yaml
   kubectl kustomize .; echo "exit=$?"
   ```

   Two edits, two builds. Report which single edit was sufficient, and whether the second changed
   the output at all.

7. Check the load restriction the post could not have met or broken.

   ```
   kubectl kustomize . --load-restrictor LoadRestrictionsNone; echo "exit=$?"
   kubectl kustomize . --load-restrictor LoadRestrictionsRootOnly; echo "exit=$?"
   ```

   The overlay reaches out of its own directory with `../../base`. Find out whether the default
   restriction minds, and if it does, what the message says.

8. Now use the cluster. Apply the fixed overlay through the four subcommands that take `-k`.

   ```
   kubectl apply -k .
   kubectl get -k . -o custom-columns=KIND:.kind,NAME:.metadata.name,REPLICAS:.spec.replicas
   kubectl diff -k . ; echo "diff exit=$?"
   ```

   Then edit `replica_count.yaml` to `replicas: 3`, run `kubectl diff -k .` again, and read what it
   prints before applying. This is the post's *"streamed directly to kubectl"* sentence, ten years
   on and with four verbs instead of a pipe.

9. Mark one of the base resources as not-for-the-cluster and rebuild.

   ```
   cd ~/kz/someapp/base
   kubectl annotate --local -f configMap.yaml --dry-run=client \
     config.kubernetes.io/local-config=true -o yaml > configMap.yaml.new
   mv configMap.yaml.new configMap.yaml
   cd ../overlays/production
   kubectl kustomize . | grep -c 'kind: ConfigMap'
   kubectl kustomize . | grep -c 'local-config'
   ```

   `labels-annotations-taints/_index.md:339-340` says Kustomize *"removes objects with this
   annotation from its final build output"*. Confirm it, then say what that does to the post's claim
   that every artefact is plain YAML for the API.

10. Look for the internal annotations the same reference reserves.

    ```
    kubectl kustomize . | grep -c 'internal.config.kubernetes.io'
    kubectl kustomize . --output /tmp/out && grep -rc 'internal.config' /tmp/out
    ```

    `:470-473` says these are set on the way in and removed on the way out. A count of zero is the
    documented behaviour, not an absence of the feature.

11. Try the post's own starting point, at the tag kubectl still recommends. This one needs outbound
    network from the node; skip it if the lab has none.

    ```
    kubectl kustomize 'https://github.com/kubernetes-sigs/kustomize.git/examples/helloWorld?ref=v1.0.6'; echo "exit=$?"
    ```

    Whatever happens, it is a fact about the pinned help text at
    `kubectl_kustomize/_index.md:43` as much as about the example.

12. If — and only if — you fetch the standalone binary yourself, run the second kustomize on the
    same directory and compare.

    ```
    kustomize version
    kustomize build ~/kz/someapp/overlays/production > /tmp/standalone.yaml
    kubectl kustomize ~/kz/someapp/overlays/production > /tmp/vendored.yaml
    diff /tmp/standalone.yaml /tmp/vendored.yaml && echo IDENTICAL
    ```

    Also run both against the *unfixed* overlay from step 4 and compare the two error messages. Two
    programs, one file format, and the difference between them is the whole of this exercise's
    title.

13. Find out where the validation the post promises is now performed.

    ```
    cd ~/kz/someapp/overlays/production
    kubectl kustomize . | kubectl apply --dry-run=client -f - --validate=strict; echo "client exit=$?"
    kubectl kustomize . | kubectl apply --dry-run=server -f - ; echo "server exit=$?"
    ```

    Then break the patch on purpose — add `replicasss: 3` beside `replicas:` in
    `replica_count.yaml` — rebuild, and send it through both dry runs again. One of the two tells you
    about the typo, and which one is the subject of the `ServerSideFieldValidation` ladder above.
    Undo the typo before moving on.

**Expect**

Step 1 — thirteen flags before the inherited block, of which `--enable-helm`, `--helm-api-versions`,
`--helm-command`, `--helm-debug` and `--helm-kube-version` are five; `grep -ci helm` should return
at least five. The GitHub example ends `?ref=v1.0.6`. `kubectl version --client` prints a client
version and no kustomize version, so the vendored build stays anonymous.

Step 2 — the build succeeds. `commonLabels` is still accepted by the vendored kustomize, and the
label lands on more places than the objects' `metadata.labels`: expect it in the Deployment's
`spec.selector.matchLabels` and `spec.template.metadata.labels` and in the Service's
`spec.selector` too, because the feature list's own description of the field is *"labels to add to
all resources and selectors"*. Whether anything is printed on stderr is the part worth recording
rather than predicting; a deprecated field may warn, and the pinned tree gives no indication either
way.

Step 3 — `includeSelectors: true` should reproduce `commonLabels` exactly, so the first `diff`
prints nothing and you see `IDENTICAL`. With `includeSelectors: false` the selectors keep the
original label and only `metadata.labels` changes — which is the behaviour the feature list at
`:1032` ascribes to `labels` unconditionally. So the table is right about the field's default and
wrong about its type, and the page's example is right about both.

Step 4 — nothing to expect but a decision: the post's tree draws `replica_count.yaml` inside
`production/` after closing the directory, and the only reading that produces a buildable tree is
the one where it is a sibling of the overlay's `kustomization.yaml`.

Step 5 — a failure, exit non-zero, and the message is about `patches`, not about `bases` or
`commonLabels`. Expect a type or unmarshalling error along the lines of a string being found where
an object was wanted. Note that `bases` is not mentioned: it is the field with no examples in the
whole pinned tree, and it is not the field that stops the build.

Step 6 — the first edit alone is sufficient; the build succeeds after `- path:` and before `bases:`
becomes `resources:`. The second edit changes the output not at all — same objects, same labels,
same replica count — which is why the post's overlay reads as though it should still work. One of
its three fields is a synonym that still resolves, one is current, and one changed type.

Step 7 — record both. The overlay's `../../base` is above the directory named on the command line,
so `LoadRestrictionsRootOnly` is the interesting one; if it refuses, the message names the flag and
the path, and `LoadRestrictionsNone` accepts what the post wrote. Either answer is a fact about a
restriction that did not exist when the post was published, applied by default to the example the
post prints.

Step 8 — `apply -k` creates the objects, `get -k` lists them with `replicas: 100`, and the first
`kubectl diff -k` prints nothing and exits 0 because the cluster already matches. After the edit to
`replicas: 3`, `diff -k` prints a unified diff of the Deployment showing `-  replicas: 100` and
`+  replicas: 3`, and exits 1 — a non-zero exit meaning *there is a difference*, not *there was an
error*.

Step 9 — the ConfigMap count drops to zero and the `local-config` count is zero as well. The object
is not in the output at all, so it is not in what `apply -k` would send. This is a documented,
Kubernetes-reference-blessed way for a file in a kustomization to be YAML that is deliberately not
for the API server.

Step 10 — zero in both. The annotations exist during the build and are stripped before output, which
is precisely why the post's *"every artifact … is plain YAML"* claim is both still true of the files
on disk and no longer true of the process that reads them.

Step 11 — whatever it returns, the interesting half is the tag. A network-isolated lab gives a
resolution or timeout error; a connected one either builds a 2018 example or fails on a repository
that has moved. The pinned help text recommends it either way.

Step 12 — for the fixed overlay, expect the two outputs to be identical or to differ only in field
ordering, since both are building a file that uses only current fields. For the unfixed overlay the
two error messages are the measurement: a standalone build several major versions ahead of kubectl's
copy is where the post's `bases` and `commonLabels` are most likely to be refused rather than
accepted, and that difference — same file, two programs, two answers — is the reason this exercise
does not state which kustomize the post's fields work in.

Step 13 — the clean build passes both. With `replicasss` added, expect `--dry-run=server` to reject
it, naming the unknown field, because the schema lives on the API server; `kubectl kustomize` itself
builds it happily, since it is not schema-aware about a field it was told to patch in. Whether
`--dry-run=client --validate=strict` also catches it is the measurement: `ServerSideFieldValidation`
went stable at v1.27 and its file is marked removed, so on a v1.37 cluster the client is no longer
the component the post's *"can be validated"* sentence describes.

**Read on** — three questions the pinned tree can answer, and one it cannot.

1. The Kustomize Feature List at `kustomization.md:1022-1040` omits `patches` and `namespace` while
   listing `patchesStrategicMerge`, `patchesJson6902` and `vars`. Compare it against the fields the
   same page's own examples use — `:430`, `:433`, `:599`, `:675`, `:936` — and ask what a reader who
   trusts only the table would write.
2. `kubectl kustomize`'s synopsis at `kubectl_kustomize/_index.md:27` calls its output *"a set of
   KRM resources"* and its flags include `--enable-alpha-plugins`, `--mount`, `--network` and
   `--as-current-user` (`:56-140`). Read those four against
   `labels-annotations-taints/_index.md:462-478` and ask what a program that runs containers to
   transform manifests is, in the post's own terms — a tool, or a new language.
3. `management.md:71-82` puts Helm and Kustomize in adjacent subsections under one heading. Read the
   post's objection to templating against both entries and ask which of its two claims — that
   templates are a new language, and that value sets grow without bound — the pinned tree gives you
   any way to test.
4. The unanswerable one. This post's `bases` and `commonLabels` were superseded, and the pinned tree
   contains no record of when or why: there is no deprecation guide for a kustomization file, no
   feature gate to carry a stage, and no removed-in release to cite, because none of it is an API
   object. The prose at `:867-870` still teaches the post's vocabulary while the examples beneath it
   have quietly changed. What cannot be recovered from the archive is whether a reader was ever told
   — whether the field was announced as replaced, or simply stopped appearing. Every other exercise
   in this year can date its diff to a release. This one can date nothing, and that is the finding:
   the parts of Kubernetes that live outside the API have no ladder, so their history is only as
   good as the page someone remembered to edit.

Sibling exercises worth reading first, all backward. The case this post argues against has its own
post from two years earlier
([`../2016/11-helm-charts-making-it-simple-to-package-and-deploy-apps-on-kubernetes.md`](../2016/11-helm-charts-making-it-simple-to-package-and-deploy-apps-on-kubernetes.md)),
and reading the two together is the only way to see that the pinned docs now list them as
neighbours. The problem both are answering was stated plainly in 2016
([`../2016/05-configuration-management-with-containers.md`](../2016/05-configuration-management-with-containers.md)).
And the program that ended up carrying this tool inside it was already the subject of a post in 2015
([`../2015/09-some-things-you-didnt-know-about-kubectl.md`](../2015/09-some-things-you-didnt-know-about-kubectl.md)),
written when `kubectl kustomize` was six years away.

**Teardown** — the cluster holds only what `apply -k` put there, and the rest is files:

```
kubectl delete -k ~/kz/someapp/overlays/production --ignore-not-found
kubectl get all -l env=production
rm -rf ~/kz /tmp/old.yaml /tmp/new.yaml /tmp/out /tmp/standalone.yaml /tmp/vendored.yaml
```

The `get all` is worth running after the delete rather than before: the overlay's `commonLabels`
gave every object `env: production`, so one label selector confirms the whole build is gone. Then
[tear the topology down](../../strands/lab-topologies.md#teardown).
