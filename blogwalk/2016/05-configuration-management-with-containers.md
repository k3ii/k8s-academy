<a id="configuration-management-with-containers"></a>
# Neither manifest in this post applies as printed, the API now accepts the defect it used to catch, and the behaviour the post leaves out is the only one that changes

**Post** — [Configuration management with Containers](https://kubernetes.io/blog/2016/04/configuration-management-with-containers/),
2016-04-04, Kubernetes v1.2 — ConfigMap's announcement, and the other post the *Five days of
Kubernetes 1.2* series numbered seventh. It is three days younger than
[04](04-using-deployment-objects-with.md) and shares its Deployment idiom, which is useful: the two
exercises break in different places from the same starting point.

**As written** — the post's argument is that configuration should be separated from code, that
Secret already did this for credentials, and that *"no object existed in the past for ordinary,
non-secret configuration"*. ConfigMap fills the gap. It then states the shape of the API:

> The ConfigMap API is simple conceptually. From a data perspective, the ConfigMap type is just a
> set of key-value pairs. […] There are three ways to consume a ConfigMap in a pod:
>
> - Command line arguments
> - Environment variables
> - Files in a volume

and gives the distinction from Secret as a design principle:

> One major difference in these APIs is that Secret values are stored as byte arrays in order to
> support storing binaries like SSH keys. […] Since ConfigMap is intended to hold only configuration
> information and not binaries, values are stored as strings, and thus are readable in the
> serialized form.

Two manifests follow. The ConfigMap, holding both "property-like" and "file-like" keys:

```
apiVersion: v1
kind: ConfigMap
metadata:
  Name: example-configmap
data:
  # property-like keys
  game-properties-file-name: game.properties
  ui-properties-file-name: ui.properties
  # file-like keys
  game.properties: |
    enemies=aliens
    lives=3
    ...
  ui.properties: |
    color.good=purple
    ...
```

a `kubectl create configmap` fence showing the three ways to supply pairs:

```
    $ kubectl create configmap my-config \
    --from-literal=literal-key=literal-value \
    --from-file=ui.properties \
    --from=file=path/to/config/dir
```

and a Deployment consuming the ConfigMap both ways at once — the property-like keys as environment
variables, the file-like keys as a volume:

```
apiVersion: extensions/v1beta1
kind: Deployment
...
        env:
        # consume the property-like keys in environment variables
        - name: GAME\_PROPERTIES\_NAME
          valueFrom:
            configMapKeyRef:
              name: example-configmap
              key: game-properties-file-name
...
      volumes:
      # consume the file-like keys of the configmap via volume plugin
      - name: config-volume
        configMap:
          name: example-configmap
          items:
          - key: ui.properties
            path: cfg/ui.properties
         - key: game.properties
           path: cfg/game.properties
      restartPolicy: Never
```

The post closes by pointing at [the ConfigMap docs](/docs/user-guide/configmap/) for detail, and
says nothing at all about what happens to either consumption path when the ConfigMap changes.

**As it runs now** — the census row for this post calls it *"the rare 2016 post whose manifests
still apply unchanged."* That is true of the API version and false of the manifests. `ConfigMap` has
been `v1` since it arrived and the `data` block above is byte-for-byte valid at the pin. Neither
manifest applies.

1. **The ConfigMap fails on a capital letter, and the error will not tell you which one.**
   `metadata:` carries `Name:`, not `name:`. YAML keys are case-sensitive and the Kubernetes API has
   no `metadata.Name`, so the object submitted has an unknown field *and* no name. kubectl defaults
   to strict server-side validation — *"The default validation setting for kubectl is
   `--validate=true`, which means strict server-side field validation"* — but the pin also documents
   what happens when a request is both unrecognised and invalid for another reason: the API server
   *"responds with a 400 Bad Request error, but will not provide any information on unknown or
   duplicate fields (only which fatal error it encountered first)."* So the reader is told about the
   name they did not set and not about the name they did.
2. **The `kubectl create configmap` fence has a typo the shell reaches before the API does.**
   `--from=file=path/to/config/dir` should be `--from-file=`. All three of the post's modes survive
   at the pin — `--from-literal`, `--from-file`, and a directory argument to `--from-file` — and a
   fourth the post did not have, `--from-env-file`, plus `--append-hash`. So the sentence is right
   and the command is not.
3. **The Deployment fails four times in a row, and only one of the four is about age.** In order:
   the `volumes:` list is misindented — the `game.properties` item sits one space to the left of the
   `ui.properties` item above it — so the document does not parse. `extensions/v1beta1` is not
   served, exactly as in [04](04-using-deployment-objects-with.md). `restartPolicy: Never` is not a
   legal pod-template restart policy for a Deployment. And `image: imaginarygame` was never a real
   image. Note what does *not* fail: the post's Deployment writes `spec.selector.matchLabels`
   explicitly, so the field that
   [04](04-using-deployment-objects-with.md) had to add by hand is already here. Two posts three
   days apart, one of which converts to `apps/v1` cleanly and one of which does not.
4. **The environment variable name is now legal, which is worse than failing.**
   `GAME\_PROPERTIES\_NAME` is a Markdown escaping artifact of the same kind
   [03](03-kubernetes-1-2-and-simplifying-advanced-networking-with-ingress.md) found in an image
   path: the backslashes are inside a code fence, so they are not consumed, and a reader copying
   from the published page gets them. In 2016 the API rejected that name — environment variable
   names had to be C identifiers. At the pin the Pod API reference says the field *"May consist of
   any printable ASCII characters except '='."* A backslash is printable ASCII and is not `=`. So
   the manifest that used to be caught now applies, and the container receives a variable whose name
   no shell can expand.
5. **Still exact.** The `data` block, the `configMapKeyRef` shape, the `configMap` volume source and
   its `items:` `key`/`path` projection are all unchanged. The blank line the blog's editor inserted
   between every line of both fences is harmless — YAML ignores it — and is worth naming precisely
   because it looks like the same class of problem as the four above and is not.

The dead link at the end, `/docs/user-guide/configmap/`, now resolves to nothing; its successor is
`/docs/tasks/configure-pod-container/configure-pod-configmap/`. That page is where the era went to
hide. Two of its Pod manifests still specify `image: gcr.io/google_containers/busybox` — the only
occurrences of that registry path left anywhere in `content/en/docs`, in the current documentation
for this post's own subject.

**The diff, and why** — the post is *still right* about everything it says and wrong by omission
about the only thing that distinguishes its two consumption paths. It describes three ways to
consume a ConfigMap and does not say that they behave differently after the ConfigMap changes. That
is not a small gap. It is the entire operational difference between them, and it is the reason
choosing one over the other is a decision rather than a preference.

At the pin the two behaviours are documented in adjacent paragraphs and they are opposites. For
volumes: *"When a ConfigMap currently consumed in a volume is updated, projected keys are eventually
updated as well. The kubelet checks whether the mounted ConfigMap is fresh on every periodic sync."*
The delay is bounded but not fixed — *"the total delay […] can be as long as the kubelet sync period
+ cache propagation delay"*, where the propagation term depends on `configMapAndSecretChangeDetectionStrategy`
and is *"watch propagation delay, ttl of cache, or zero"* for the three settings. For environment
variables, one sentence: *"ConfigMaps consumed as environment variables are not updated
automatically and require a pod restart."* And a third case the post could not have had, because
`subPath` mounts came later: *"A container using a ConfigMap as a subPath volume mount will not
receive ConfigMap updates."*

So the post's own example Deployment, which reads the property-like keys as environment variables
and the file-like keys as a volume, is a live demonstration of the asymmetry — and never mentions
it. A reader who changes `game-properties-file-name` in the ConfigMap and `game.properties`
alongside it will find one of the two changes has reached the container and the other has not, with
no error anywhere and nothing in the post to explain it. This is the shape of failure the exercise
exists for: not a command that errors, but a field the API accepts that means something different an
hour later.

Three things the post asserts have since been settled against it, each by a gate.

The design principle — *"Since ConfigMap is intended to hold only configuration information and not
binaries, values are stored as strings"* — was reversed. The pin: *"a ConfigMap has `data` and
`binaryData` fields […] The `data` field is designed to contain UTF-8 strings while the `binaryData`
field is designed to contain binary data as base64-encoded strings."* The distinction from Secret
that the post spends a paragraph establishing is now one of intent and access control, not of
encoding. What survived instead is a limit the post does not mention: *"ConfigMap cannot exceed 1
MiB."*

The implicit promise that a ConfigMap is a mutable thing acquired an opt-out:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.18 – v1.18 |
| beta | `true` | — | v1.19 – v1.20 |
| stable | `true` | — | v1.21 – v1.24 |

`ImmutableEphemeralVolumes` declares `removed: true` in its file, which is the ordinary end state
for a gate whose behaviour became unconditional. Note where the prose picks up the story: the
concept page says *"Starting from v1.19, you can add an `immutable` field"*, and v1.19 is the
**beta** row, not the alpha row and not the stable one — a reminder that documentation dates
features from when they became usable by default rather than from when they existed. Once set,
*"it is not possible to revert this change nor to mutate the contents"*; the only route is delete and
recreate, and *"because existing Pods maintain a mount point to the deleted ConfigMap, it is
recommended to recreate these pods."* Immutability is therefore not the opposite of the update
behaviour above — it removes the update path and leaves the mount point dangling.

The name the post wrote by accident became legal:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.30 – v1.31 |
| beta | `true` | — | v1.32 – v1.33 |
| stable | `true` | `true` | v1.34 – |

`RelaxedEnvironmentVariableValidation` is stable **and locked** from v1.34, so the behaviour cannot
be switched off. Its entire description in the pinned tree is one line — *"Allow almost all
printable ASCII characters in environment variables"* — and it appears in no prose page anywhere
under `content/en/docs`; the only other trace of the change is the Pod API reference sentence quoted
above. A validation rule that had held since before 1.0 was relaxed, locked, and never written up.
Whether `GAME\_PROPERTIES\_NAME` is accepted by the cluster in front of you is therefore a question
the documentation cannot answer, and *Do* settles it against the API server instead.

And the fourth consumption path, which the post's list of three did not have and which the pin
counts alongside them:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.34 – v1.34 |
| beta | `true` | — | v1.35 – |

`EnvFiles` is beta and on by default at the pin. It adds `fileKeyRef`: an init container writes an
env-file into an `emptyDir`, and the consumer container names keys out of that file without mounting
the volume at all. Read against this post it is the two paths converging — configuration arriving as
a *file* and being consumed as an *environment variable* — and the convergence keeps the wrong half
of the semantics. The task page says the kubelet retrieves the values *"during container
initialization"*, so a `fileKeyRef` variable is fixed for the life of the container, like every other
environment variable. Nineteen releases of work on this API, and the answer to *"what happens when
the configuration changes"* is still: mount it, or restart.

The pin also lists a way the post did not: *"Write code to run inside the Pod that uses the
Kubernetes API to read a ConfigMap"*, which is the only route that gets updates on the
application's own terms — *"your application can subscribe to get updates whenever the ConfigMap
changes, and react when that happens"* — and the only one that can read a ConfigMap from another
namespace, the other constraint the post does not mention. Three ways became four, then five, and
exactly one of them has ever notified anybody.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), fresh. One node, one kubelet, and the
kubelet's sync period is the thing being timed, so a second node would only add noise. Bring the
guest up with [the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, install Kubernetes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), then
`ssh zain@10.10.10.180`.

**Do**

1. Apply the post's ConfigMap exactly as printed, capital `N` and all, into a file `cm.yaml`:

   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     Name: example-configmap
   data:
     game-properties-file-name: game.properties
     ui-properties-file-name: ui.properties
     game.properties: |
       enemies=aliens
       lives=3
     ui.properties: |
       color.good=purple
   ```

   `kubectl apply -f cm.yaml`. Write down the error verbatim. Then run
   `kubectl apply -f cm.yaml --validate=warn` and write down what is different. One of the two
   runs names the actual defect.

2. Change `Name` to `name`, apply, and confirm what got stored:
   `kubectl get cm example-configmap -o jsonpath='{.data.game\.properties}'`. The `data` half of this
   post is ten years old and unmodified; that is worth seeing directly rather than being told.

3. Run the post's create fence as printed — all four lines, with the continuation backslashes —
   against a file you make first (`echo 'color.good=purple' > ui.properties`). Then fix the one
   broken flag and run it again. Then run a third time with `--from-env-file=ui.properties` and
   compare the resulting `data` blocks with `kubectl get cm -o yaml`.

4. Write the post's Deployment into `deploy.yaml` with the indentation exactly as printed, including
   the two `volumes:` items at different depths, and apply it. Fix one defect at a time, applying
   after each, and keep every error string: the indentation, then `extensions/v1beta1` →
   `apps/v1`, then `restartPolicy: Never`, then `image: imaginarygame` →
   `registry.k8s.io/e2e-test-images/agnhost:2.53` with `command` replaced by
   `["/agnhost","netexec","--http-port=8080"]`. Four applies, four different failures, and then it
   runs. Do **not** fix the environment variable names.

5. Find out what the container's environment variables are actually called:

   ```
   kubectl exec deploy/configmap-example-deployment -- env | grep -i properties
   kubectl exec deploy/configmap-example-deployment -- sh -c 'echo "[$GAME_PROPERTIES_NAME]"'
   ```

   The first command shows what the API stored. The second shows what a shell can reach. If they
   disagree, the backslash is legal.

6. Confirm the volume half landed where the post's `items:` block said it would:
   `kubectl exec deploy/configmap-example-deployment -- ls -R /etc/game` and
   `kubectl exec deploy/configmap-example-deployment -- cat /etc/game/cfg/game.properties`.

7. Now the payload. Change both halves of the ConfigMap in one edit —
   `kubectl patch cm example-configmap --type merge -p '{"data":{"game-properties-file-name":"CHANGED.properties","game.properties":"enemies=robots\nlives=99\n"}}'` —
   and then poll both consumption paths for two minutes, once every ten seconds, recording the
   time of the first change in each:

   ```
   kubectl exec deploy/configmap-example-deployment -- cat /etc/game/cfg/game.properties
   kubectl exec deploy/configmap-example-deployment -- env | grep -i properties
   ```

   Stop when one of them has changed and the other has not moved for a full minute.

8. Add a third path that the post could not have written, and check it against the other two. Patch
   the Deployment to add a second mount of the same key using `subPath`:

   ```
   kubectl patch deploy configmap-example-deployment --type json -p '[{"op":"add","path":"/spec/template/spec/containers/0/volumeMounts/-","value":{"name":"config-volume","mountPath":"/etc/single/game.properties","subPath":"cfg/game.properties"}}]'
   ```

   Wait for the new pod, patch `game.properties` again, and poll `/etc/game/cfg/game.properties`
   and `/etc/single/game.properties` together.

9. Close the update path entirely. `kubectl patch cm example-configmap --type merge -p
   '{"immutable":true}'`, then try to patch `data` again, then try to set `immutable` back to
   `false`. Two errors. Then check whether the already-mounted file is still readable.

10. Apply the pinned documentation's own ConfigMap example, unedited, from
    `content/en/docs/tasks/configure-pod-container/configure-pod-configmap.md` — the
    `dapi-test-pod` manifest with `image: gcr.io/google_containers/busybox` and
    `restartPolicy: Never` — and read the pod's container status. Then say which of the two
    documents in front of you is out of date.

**Expect** — step 1: the default run reports a missing name, phrased as a `Required value` for
`metadata.name` or a client-side refusal that the resource name may not be empty, and says nothing
about `Name`. The `--validate=warn` run surfaces `unknown field "metadata.Name"` as a warning. The
pinned API concepts page predicted exactly this ordering, and the point of running both is that the
default setting is the one that hides the cause.

Step 2: `enemies=aliens\nlives=3` back out of the API, unchanged, from a `v1` object.

Step 3: `unknown flag: --from` — pflag never gets as far as the API server, and the misprint is one
character. The fixed run creates two keys, `literal-key` and `ui.properties`. The
`--from-env-file` run reads the file's *contents* as pairs rather than storing the file as a value,
so the key it creates is `color.good` and the value is `purple` — the pin's rule for that flag is
only *"Each line in an env file has to be in VAR=VAL format"*, and a dot is a legal ConfigMap key.
Same file, two different ConfigMaps; name which of the post's three modes each corresponds to, and
if the dotted key is refused, record the error, because the flag's documented rule does not predict
it.

Step 4, in order: a YAML parse error citing the line of the `game.properties` item — the parser's
complaint is about mapping structure, not about Kubernetes. Then `no matches for kind "Deployment"
in version "extensions/v1beta1"`. Then an `Unsupported value: "Never"` naming
`spec.template.spec.restartPolicy` and listing `"Always"` as the only supported value. Then a
running pod, or an `ErrImagePull` if you changed the image but not the `command`.

Step 5: `env` prints a variable whose name contains literal backslashes, and
`echo "[$GAME_PROPERTIES_NAME]"` prints `[]`. Both facts at once are the finding: the API accepted a
name in v1.37 that it would have rejected in v1.2, and nothing between the manifest and the shell
noticed. If instead the apply in step 4 failed on the variable name, say so and record the error —
that would mean the relaxation does not extend as far as the API reference's sentence suggests, and
the reference is the thing that is wrong.

Step 6: `/etc/game/cfg/game.properties` and `/etc/game/cfg/ui.properties`, and nothing at
`/etc/game/game.properties` — the `items:` `path` is relative to `mountPath`, which is why the
post's `--config-dir=/etc/game/cfg` matches.

Step 7: the file changes; the environment variable does not, and will not, for the life of that
pod. Record the elapsed time before the file changed. It should be under two minutes on a default
kubelet, and the pinned bound is *"the kubelet sync period + cache propagation delay"* — so a
number well under a minute means the default watch-based strategy is in play. The environment
variable will still read `game.properties` after the pod has been running for an hour.

Step 8: `/etc/game/cfg/game.properties` updates and `/etc/single/game.properties` does not. Three
paths, three behaviours, one ConfigMap. The post named the first two and had no way to name the
third.

Step 9: the `data` patch is rejected as an attempt to modify an immutable field; setting
`immutable` back to `false` is rejected for the same reason. The mounted file keeps its current
contents and keeps serving — immutability freezes the source, not the projection.

Step 10: the pod stays in `ErrImagePull` or `ImagePullBackOff`, from a manifest the project
publishes today as the way to configure a Pod with a ConfigMap. Whatever message the kubelet gives
about `gcr.io/google_containers/busybox` is the only evidence in this tree about that registry's
current state, so quote it.

**Read on** — the pin's
[ConfigMap concept page](https://kubernetes.io/docs/concepts/configuration/configmap/), the section
*Mounted ConfigMaps are updated automatically*: find `configMapAndSecretChangeDetectionStrategy`,
read the three values it accepts, and answer which one makes the propagation term of that delay
*zero* — then say what that setting costs the API server on a cluster with ten thousand pods, and
why it is not the default. Then read the
[Pod API reference's `EnvVar` entry](https://kubernetes.io/docs/reference/kubernetes-api/core/pod-v1/#EnvVar)
against the one-line description of
[`RelaxedEnvironmentVariableValidation`](https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/)
and answer a narrower one: the gate is stable and `locked: true`, so no cluster can refuse the new
rule — what does a cluster operator who wanted the old validation back have left to work with?

That reference URL is worth one more minute than the reading takes. The pinned tree files it under
`reference/kubernetes-api/core/`, but 49 links across 23 of its own pages send readers to
`reference/kubernetes-api/workload-resources/`, a directory the tree does not contain, and not one
page links to the path it does. Find which of the two the live site answers on, and then decide
which is the error: the pages, or the layout.

**Teardown** — `kubectl delete deploy configmap-example-deployment; kubectl delete pod dapi-test-pod
--ignore-not-found; kubectl delete cm example-configmap my-config --ignore-not-found`. The immutable
ConfigMap deletes normally; only its contents were frozen. Take the guest down with
[teardown](../../strands/lab-topologies.md#teardown).
