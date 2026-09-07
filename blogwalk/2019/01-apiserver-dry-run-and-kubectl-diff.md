<a id="apiserver-dry-run-and-kubectl-diff"></a>

# Three of this post's four commands have to be retyped, the gate it tells you to switch on is absent from the server because the feature can no longer be switched off, and the one thing it offers as optional advice is now a required field with two of its four values withdrawn

**Post** — [APIServer dry-run and kubectl
diff](https://kubernetes.io/blog/2019/01/14/apiserver-dry-run-and-kubectl-diff/), 14 January 2019,
by Antoine Pelisse (Google Cloud). 105 lines, 5,090 bytes. Kubernetes v1.13.

It is the first walk of 2019 and the shortest route in the archive from a post to a diff: four
commands, three of which have to be retyped and one of which is byte-for-byte still correct. The
post also carries something no earlier walk does — an editor's note added later by the project
itself (`:99-105`), warning that the flag in the post's own body was deprecated in v1.18. The
exercise starts where that note stops, because the note repairs one command and leaves three.

**As written** — the post is an announcement from the Apply working group: Kubernetes 1.13 promoted
server-side dry-run and `kubectl diff` to beta, and *"these two features are big improvements for
the Kubernetes declarative model"* (`:14-15`).

The Challenges section (`:17-35`) states two problems, and both are worth reading as claims rather
than as background, because the exercise below tests them. The first (`:22-28`):

> While compilers and linters do a good job to detect errors in pull-requests for code, a good
> validation is missing for Kubernetes configuration files. The existing solution is to run
> `kubectl apply --dry-run`, but this runs a *local* dry-run that doesn't talk to the server: it
> doesn't have server validation and doesn't go through validating admission controllers. As an
> example, Custom resource names are only validated on the server so a local dry-run won't help.

The second (`:29-35`) is about not being able to predict the stored object: defaulting sets fields
to *"potentially unexpected values"*, mutating webhooks *"might set fields or clobber/change some
values"*, and merges have surprising effects — *"it can be hard to know how lists are going to be
ordered once merged."*

APIServer dry-run (`:39-52`) is the answer to both, and the post links it at
`/docs/reference/using-api/api-concepts/#dry-run`. Three properties (`:43-48`): individual requests
can be marked dry-run, the API server *"guarantees that dry-run requests won't be persisted to
storage"*, and the request is otherwise processed as a normal one — defaulted, validated, through
the validating chain and the mutating chain, and returned to the user unpersisted. Then the
constraint at `:50-52`: *"dry-run requests are only processed if all admission controllers
explicitly announce that they don't have any dry-run side-effects."*

How to enable it (`:54-63`) is two instructions. One for the cluster:

> Server-side dry-run is enabled through a feature-gate. Now that the feature is Beta in 1.13, it
> should be enabled by default, but still can be enabled/disabled using
> `kube-apiserver --feature-gates DryRun=true`.

And one for anybody running webhooks: remove side effects when the dry-run parameter is set, and

> Specify in the `sideEffects` field of the `admissionregistration.k8s.io/v1beta1.Webhook` object to
> indicate that the object doesn't have side-effects on dry-run (or at all).

In the post that field name is a link, and it points at the v1.13 archive of the generated API
reference rather than at the docs — the only citation in the file that its author already expected
to go stale.

How to use it (`:65-70`) is one command: `kubectl apply --server-dry-run`, *"which will decorate the
request with the dryRun flag and return the object as it would have been applied, or an error if it
would have failed."*

`kubectl diff` (`:72-87`) is presented as the ergonomic layer on top. Dry-run shows you the object;
diff shows you *"the differences between the current "live" object and the new "dry-run" object"*.
It is *"meant to be as similar as possible to `kubectl apply`"*, so `kubectl diff -f
some-resources.yaml` is the whole interface, and one fence (`:85-87`):

```
KUBECTL_EXTERNAL_DIFF=meld kubectl diff -f some-resources.yaml
```

What's next (`:89-97`) is three predictions, and they have had three different fates:

> - Server-side apply is trying to improve the apply scenario, by adding owner
> semantics to fields! It's also going to improve support for CRDs and unions!
> - Some kubectl apply features are missing from diff and could be useful, like the ability
> to filter by label, or to display pruned resources.
> - Eventually, kubectl diff will use server-side apply!

**As it runs now** — the mechanism is on, unconditional, and documented on the page the post links
to. `api-concepts.md:1288-1297` is the same section at the same anchor, and its guarantee is the
post's guarantee in different words: dry run *"helps to evaluate a request through the typical
request stages (admission chain, validation, merge conflicts) up until persisting objects to
storage"*, and *"Kubernetes guarantees that dry-run requests will not be persisted in storage or
have any other side effects."* `:1313-1318` spells out what `?dryRun=All` runs — admission
controllers, validating admission post-mutation, `PATCH` merge, defaulting and schema validation —
and `:1320-1322` states the constraint the post gave: a request that would trigger a side-effecting
admission controller *"will be failed rather than risk an unwanted side effect"*, and *"All built in
admission control plugins support dry-run."*

The three commands fail in three different ways, and telling them apart is the exercise.

`kubectl apply --server-dry-run` **errors before a connection is opened**. The string
`server-dry-run` has zero occurrences anywhere in `content/en/docs` at the pin; `dry-run=server`
occurs in 27 files. This is the one the editor's note covers, and it is the honest failure: the flag
is not there, `kubectl` says so, and nothing has happened.

`kube-apiserver --feature-gates DryRun=true` **stops the control plane**, and it is not the flag
that is missing but the gate. `DryRun.md` still exists under `feature-gates/` and declares
`removed: true`; the gate name does not appear in the generated `--feature-gates` help in
`kube-apiserver.md`; and there is no `DryRun.md` under `feature-gates-removed/`, which holds only
its own `index.md`. A gate an API server does not recognise is a start-up failure, not a warning,
so the post's *"still can be enabled/disabled"* is now the one instruction in the file that can cost
you a cluster rather than a command.

`kubectl apply --dry-run` **is accepted as a flag and rejected as a value**, and this is the failure
mode the post's own first bullet is about, arriving one layer up. The generated help for the flag
reads, on 45 pages at the pin:

```
--dry-run string[="unchanged"]     Default: "none"
```

The `[="unchanged"]` is what a bare `--dry-run` resolves to, and the description on the very same
line — present on all 45 of those pages — says the value *"Must be "none", "server", or "client""*.
The word `"unchanged"` occurs in `content/en/docs` only inside that one help line, 45 times, and
never once as a documented value of anything. So the pin advertises a value it forbids, in a single
line, forty-five times over; step 1 below reads it and step 2 asks the server to adjudicate.

The same hazard is in the API, one layer further down, and there the pin is unambiguous.
`api-concepts.md:1301-1311` says the `dryRun` query parameter is *"a string, working as an enum, and
the only accepted values are"* — then lists two, and the first is `[no value set]`, whose meaning is
*"Allow side effects. You request this with a query string such as `?dryRun` or
`?dryRun&pretty=true`."* A valueless `dryRun` is a real write. A valueless `--dry-run` is a rejected
value. Seven years apart, in two different components, the same absence means two different things
and neither of them means *dry run*.

The fourth command has not moved. `kubectl_diff/_index.md:39-41` still gives the synopsis as
`kubectl diff -f FILENAME`, `:31` still documents `KUBECTL_EXTERNAL_DIFF` — with a different
example, `colordiff -N -u` rather than the post's `meld` — `:33` names the default differ as `diff`
with `-u` and `-N`, and `:35` publishes the exit status contract the post never mentions: *"0 No
differences were found. 1 Differences were found. >1 Kubectl or diff failed with an error."*

And the optional advice has become law. `deprecation-guide.md:172-184` records the removal of
`admissionregistration.k8s.io/v1beta1` — the exact group-version the post's `sideEffects` sentence
names — as *"no longer served as of v1.22"*, with the migration target `admissionregistration.k8s.io/v1`
*"available since v1.16"*, and among the notable changes at `:181-182`:

> `webhooks[*].sideEffects` default value is removed, and the field made required,
> and only `None` and `NoneOnDryRun` are permitted for v1

So the post says *specify the field to indicate you have no side effects*, and the field is now
required whether or not you have any, with the two values that meant *I might, or I have not
checked* deleted from the enum.

**And here the pin contradicts itself about that enum.**
`extensible-admission-controllers.md:1042-1048` lists exactly two acceptable values, `None` and
`NoneOnDryRun`, and describes each. The generated reference for the **v1** kinds lists four:
`validating-webhook-configuration-v1.md:134` and `mutating-webhook-configuration-v1.md:138` both
carry *"Acceptable values are: None, NoneOnDryRun (webhooks created via v1beta1 may also specify
Some or Unknown)"*, followed by a `Possible enum values` list of four, among them *"`"Some"` means that
calling the webhook will possibly have side effects"* and *"`"Unknown"` means that no information is
known about the side effects"*. The v1 reference page is documenting the semantics of objects created
through an API version the same tree says has not been served for fifteen releases. Neither page is
lying and they cannot both be a description of what the server will accept today; step 8 sends the
server one of each and lets it say which.

A second, smaller self-disagreement sits on the field manager, and it matters for step 11.
`kubectl_apply/_index.md:98` gives `--field-manager` a single documented default,
`"kubectl-client-side-apply"`, printed whether or not `--server-side` is also passed;
`server-side-apply.md:543` says *"The default field manager for kubectl server-side apply is
`kubectl`."* One flag, two published defaults, and a read-back of `managedFields` settles it.

**What this exercise does not cover, and where it lives.** How a webhook is written, served and
registered — the object whose `sideEffects` field this post is talking about — is [already
walked](../2018/01-extensible-admission-is-beta.md); step 8 only sends configurations to admission
and reads the answers, and never stands up an endpoint. Field ownership, conflicts and the
`managedFields` semantics that make server-side apply more than a flag have a `walk` of their own in
2020's census, on the post that announces the second beta; step 11 reads the manager names and
stops.

**The diff, and why** — three cases land, and the third is the one that explains the other two.

The post **broke**, twice, and the two breakages are not the same kind of event. The flag rename is
a deprecation carried out on schedule and announced in the post's own body by a later editor: the
project changed `--server-dry-run` to `--dry-run=server` in v1.18 because a boolean flag per
dry-run mode does not scale to three modes, and `--dry-run=client` needed a name that was not
"nothing". The bare `--dry-run` in the first bullet broke as collateral damage of that same change,
and it broke silently at the time — the flag survived, its arity did not — which is why the
editor's note does not mention it and why the pin still offers `[="unchanged"]` on 45 pages.

The post is **still right** about the mechanism and about all three of its predictions, which is
rarer than it sounds. Server-side apply arrived one release later and went stable in v1.22. `diff`
did get the two `apply` features the second bullet asked for, and can be checked flag by flag:
`kubectl_diff/_index.md` lists `-l, --selector` and both `--prune` and `--prune-allowlist` among its
options at the pin. And the third bullet, *"Eventually, kubectl diff will use server-side apply!"*,
landed as `--server-side` — an opt-in flag, with `--force-conflicts` beside it *"If true,
server-side apply will force the changes against conflicts"*, and a `--field-manager` whose printed
default is still the string `kubectl-client-side-apply`. The forecast came true as a choice rather
than as a default, which is the smallest possible version of coming true.

And all three of the switches this post's argument produced were **retired by being agreed with** —
which is why none of them is in the server. `DryRun` went stable in v1.19 and its file says
`removed: true`. `ServerSideApply` went stable in v1.22 and its file says `removed: true`.
`ServerSideFieldValidation` — which is the *first* Challenges bullet answered by a gate, the *"good
validation ... missing for Kubernetes configuration files"* — went stable in v1.27 and its file says
`removed: true`. Three problems, three gates, three graduations, three deletions.

That is not the same shape as a feature being withdrawn, and reading a terminal `toVersion` as
withdrawal is the misreading the four-column ladder invites. What happened is the opposite: each
answer became unconditional, and an unconditional answer needs no switch. The consequence for a
reader is precise and unpleasant. The post's *"How to enable it"* section is now the most dangerous
paragraph in the file — not because the advice is wrong, but because it succeeded. There is no error
message anywhere that will tell you *this feature is on and the knob for it has been compiled out*;
the API server simply refuses to start, and the flag you were told was optional is the reason.

**The ladder** — three gates, one per Challenges bullet, all three `removed: true`.

`DryRun`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.12 |
| beta | `true` | — | v1.13 – v1.18 |
| stable | `true` | — | v1.19 – v1.27 |

Body: "Enable server-side dry run requests so that validation, merging, and mutation can be tested
without committing." The beta row is the release this post announces, and note the `default` on it:
`true`, which is what the post's *"it should be enabled by default"* is describing. Nine releases
between stable and deletion — long enough that the page documenting the feature outlived the file
that dates it.

`ServerSideApply`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.14 – v1.15 |
| beta | `true` | — | v1.16 – v1.21 |
| stable | `true` | — | v1.22 – v1.31 |

Body: "Enables the Sever Side Apply (SSA) feature on the API Server." Alpha in v1.14 — the release
after this post, which is what *"is trying to improve"* in the first What's-next bullet meant at the
time. Ten releases from stable to deletion.

`ServerSideFieldValidation`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.23 – v1.24 |
| beta | `true` | — | v1.25 – v1.26 |
| stable | `true` | — | v1.27 – v1.31 |

Body: "Enables server-side field validation. This means the validation of resource schema is
performed at the API server side rather than the client side (for example, the `kubectl create` or
`kubectl apply` command line)." This is the Challenges section's first sentence answered eight
releases later, and the answer is exactly the relocation the post asked for: validation moved from
the client to the server. It is also why step 6's client-side run may behave differently from what
the post predicts for it — the post's *"local dry-run ... doesn't talk to the server"* was a
statement about 2019's `kubectl`, and what today's `kubectl` does with `--validate` when the object
is never sent is the thing the step is there to record.

None of the three has a `locked` value and none has a repeated stage, so all three ladders climb
once and stop. What they do not show — and what the sentence under each table has to carry — is that
stopping meant deletion rather than regression.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`. Every
step below is either a read of the pinned checkout or an API-server decision — flag parsing,
defaulting, admission, schema validation, `managedFields` — and none of it needs a second node or a
scheduled Pod. Bring it up with [the five provision
steps](../../strands/lab-topologies.md#provision), substituting `topology=solo`, then
`ssh zain@10.10.10.180`. Steps 1, 7, 10 and 12 read the checkout and need no cluster.

**Do**

1. Read the flag the post's first bullet names, in the pin's own words, and find the value it offers
   and forbids in one line:

   ```sh
   W=/path/to/pinned/website/content/en/docs
   grep -rl 'dry-run string\[="unchanged"\]' $W | wc -l
   grep -rn '"unchanged"' $W | grep -v 'dry-run string' | wc -l
   sed -n '91,94p' $W/reference/kubectl/generated/kubectl_apply/_index.md
   ```

   Forty-five pages carry the line. The second count is how many times the word appears anywhere
   else. Read the fourth line of the `sed` output against the first and write down what you expect a
   bare `--dry-run` to do.

2. Ask the server. Make a namespace and a file first, then run the post's two commands exactly as
   written:

   ```sh
   kubectl create ns dryrun
   cat > /tmp/cm.yaml <<'YAML'
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: house
     namespace: dryrun
   data:
     a: b
   YAML
   kubectl apply --dry-run -f /tmp/cm.yaml; echo "exit $?"
   kubectl apply --server-dry-run -f /tmp/cm.yaml; echo "exit $?"
   ```

   Two failures, and they are not the same failure. One message is about a value and one is about a
   flag. Record both, and say which of the two tells you what to type instead.

3. The flag that replaced the second one, and the guarantee at `api-concepts.md:1296-1297`:

   ```sh
   kubectl apply --dry-run=server -f /tmp/cm.yaml
   kubectl -n dryrun get configmap; echo "exit $?"
   ```

   The first command reports the object as created. The second is the guarantee: nothing was
   persisted, so there is nothing to list.

4. Watch what `kubectl` actually puts on the wire, and compare it with the enum at
   `api-concepts.md:1301-1311`:

   ```sh
   kubectl apply --dry-run=server -f /tmp/cm.yaml --v=8 2>&1 | grep -o 'dryRun=[A-Za-z]*' | sort -u
   kubectl apply --dry-run=client -f /tmp/cm.yaml --v=8 2>&1 | grep -c 'dryRun'; true
   ```

   The pin says the parameter accepts one value, `All`, and that setting it with *no* value means
   allow side effects. Check which one `kubectl` sends for `--dry-run=server`, then check whether
   `--dry-run=client` sends anything at all.

5. The post's second bullet, measured. Defaulting is the part a local run cannot show you:

   ```sh
   cat > /tmp/dep.yaml <<'YAML'
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: house
     namespace: dryrun
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: house
     template:
       metadata:
         labels:
           app: house
       spec:
         containers:
           - name: c
             image: busybox
             command: ["sleep", "3600"]
   YAML
   kubectl apply --dry-run=client -o yaml -f /tmp/dep.yaml > /tmp/client.yaml
   kubectl apply --dry-run=server -o yaml -f /tmp/dep.yaml > /tmp/server.yaml
   wc -l /tmp/client.yaml /tmp/server.yaml
   diff /tmp/client.yaml /tmp/server.yaml
   ```

   Every line the `diff` adds is a field you did not write and would have got. Pick three of them
   and say which of the post's three sources at `:31-35` each one came from — defaulting, a mutating
   webhook, or a merge.

6. The post's own example of why a local run is not enough: *"Custom resource names are only
   validated on the server."* Test the claim with a built-in kind and an illegal name:

   ```sh
   cat > /tmp/badname.yaml <<'YAML'
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: Not_A_DNS_Name
     namespace: dryrun
   data:
     a: b
   YAML
   kubectl apply --dry-run=client -f /tmp/badname.yaml; echo "exit $?"
   kubectl apply --dry-run=server -f /tmp/badname.yaml; echo "exit $?"
   ```

   Record both exit codes and both messages. The server's answer is the post's claim holding. The
   client's answer is the interesting one, because `ServerSideFieldValidation` moved schema checking
   to the server in v1.27 and `--validate` defaults to it — so whether a *client* dry run still
   reaches the server for validation is a question this pair of commands answers and the post could
   not have.

7. The gate. One file, one absence, one metric:

   ```sh
   G=$W/reference/command-line-tools-reference/feature-gates
   sed -n '1,26p' $G/DryRun.md
   ls $W/reference/command-line-tools-reference/feature-gates-removed/
   grep -o 'DryRun=true|false' $W/reference/command-line-tools-reference/kube-apiserver.md; echo "exit $?"
   ```

   The file declares `removed: true` and its last stage ends at v1.27. The removed-gates directory
   holds one file and it is `index.md`, so the gate is not there either. Then the generated
   `--feature-gates` help for the API server: use `grep -o`, never a bare match, because that help
   is one enormous line. It finds nothing, and `echo "exit $?"` is how you see that it found nothing.

8. Now ask the running server, which is the only instrument that reports what the binary was
   actually built with:

   ```sh
   kubectl get --raw /metrics | grep -c '^kubernetes_feature_enabled'
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' \
     | grep -c 'DryRun\|ServerSideApply\|ServerSideFieldValidation'; true
   kubectl get --raw /metrics | grep -m3 '^kubernetes_feature_enabled'
   ```

   `metrics.md:546-551` describes `kubernetes_feature_enabled` as a BETA gauge with two labels,
   `name` and `stage`, exported by kube-apiserver among others. The first count proves the metric is
   there and populated. The second is the three gates this post's argument produced. The third shows
   you the label shape so you can see that a gate the binary does not have cannot report a stage.

9. The `sideEffects` advice, now law, in three dry-run requests. The requests are the instrument and
   nothing is created:

   ```sh
   kubectl apply --dry-run=server -f - <<'YAML'; echo "exit $?"
   apiVersion: admissionregistration.k8s.io/v1beta1
   kind: ValidatingWebhookConfiguration
   metadata:
     name: house-beta
   webhooks:
     - name: house.example.com
       clientConfig:
         url: https://10.10.10.180:8443/validate
   YAML
   kubectl apply --dry-run=server -f - <<'YAML'; echo "exit $?"
   apiVersion: admissionregistration.k8s.io/v1
   kind: ValidatingWebhookConfiguration
   metadata:
     name: house-bare
   webhooks:
     - name: house.example.com
       clientConfig:
         url: https://10.10.10.180:8443/validate
       rules:
         - apiGroups: [""]
           apiVersions: ["v1"]
           operations: ["CREATE"]
           resources: ["configmaps"]
   YAML
   kubectl apply --dry-run=server -f - <<'YAML'; echo "exit $?"
   apiVersion: admissionregistration.k8s.io/v1
   kind: ValidatingWebhookConfiguration
   metadata:
     name: house-unknown
   webhooks:
     - name: house.example.com
       clientConfig:
         url: https://10.10.10.180:8443/validate
       rules:
         - apiGroups: [""]
           apiVersions: ["v1"]
           operations: ["CREATE"]
           resources: ["configmaps"]
       admissionReviewVersions: ["v1"]
       sideEffects: Unknown
   YAML
   ```

   Three refusals for three reasons. The first is the group-version at `deprecation-guide.md:173`,
   and the message names the missing kind rather than the missing version, which is worth reading
   twice. The second omits `sideEffects` and `admissionReviewVersions`, both of which
   `deprecation-guide.md:181-184` says were made required at v1 — count how many required fields the
   one message names. The third supplies a value that the generated v1 reference at
   `validating-webhook-configuration-v1.md:134` lists as a possible enum value.

10. Read the two pages that disagree about that enum, and decide what step 9 settled:

    ```sh
    sed -n '1042,1048p' $W/reference/access-authn-authz/extensible-admission-controllers.md
    sed -n '134p' $W/reference/kubernetes-api/admissionregistration/validating-webhook-configuration-v1.md \
      | tr '.' '\n' | grep -i 'acceptable\|v1beta1\|Some\|Unknown' | head
    sed -n '181,182p' $W/reference/using-api/deprecation-guide.md
    ```

    Two values on the concept page, four on the reference page for the same kind, and one sentence in
    the deprecation guide saying which pair the server will take. The reference page is generated from
    the API's own type comments, so it is not wrong about the type — write down what it *is* wrong
    about, and what a reader who trusts it will build.

11. The one flag with two published defaults. Apply the ConfigMap for real, twice, and read the
    manager names back:

    ```sh
    kubectl apply -f /tmp/cm.yaml
    kubectl -n dryrun get configmap house --show-managed-fields -o json \
      | python3 -c 'import sys,json; [print(e["manager"], e["operation"], e["apiVersion"]) for e in json.load(sys.stdin)["metadata"]["managedFields"]]'
    kubectl apply --server-side --force-conflicts -f /tmp/cm.yaml
    kubectl -n dryrun get configmap house --show-managed-fields -o json \
      | python3 -c 'import sys,json; [print(e["manager"], e["operation"], e["apiVersion"]) for e in json.load(sys.stdin)["metadata"]["managedFields"]]'
    ```

    Read the two names against the two documented defaults — `kubectl_apply/_index.md:98` and
    `server-side-apply.md:543` — and say which document describes the flag and which describes the
    subcommand. Use `-o json` piped to `python3` and not `-o jsonpath`: `managedFields` entries carry
    a nested `fieldsV1` map, and `jsonpath` renders a map as Go's `map[...]`, which is not a shape you
    can feed to anything.

12. The command that did not change, and the three predictions. First the survivor, including the
    exit-status contract at `kubectl_diff/_index.md:35`:

    ```sh
    kubectl apply -f /tmp/dep.yaml
    kubectl diff -f /tmp/dep.yaml; echo "exit $?"
    sed -i 's/replicas: 1/replicas: 3/' /tmp/dep.yaml
    kubectl diff -f /tmp/dep.yaml; echo "exit $?"
    KUBECTL_EXTERNAL_DIFF='diff -q' kubectl diff -f /tmp/dep.yaml; echo "exit $?"
    ```

    Then the flags, against the post's `:95-97`:

    ```sh
    D=$W/reference/kubectl/generated/kubectl_diff/_index.md
    grep -n 'heading "options"\|heading "parentoptions"' $D
    sed -n '53,157p' $D | grep 'colspan="2">-' \
      | sed 's/.*colspan="2">//; s/&nbsp;.*//; s|</td>||'
    ```

    The `grep -n` is there so the range in the `sed` is one you have checked rather than one you have
    been given: the second heading is where the command's own flags stop and its parents' begin, and
    everything below it belongs to every `kubectl` subcommand. Take the second What's-next bullet —
    filter by label, display pruned resources — and find both in the list above that line. Take the
    third and find `--server-side`. Then find the one flag in that list that a different post in this
    walk is entirely about, and name it.

**Expect**

Step 1: `45` and `0`. The `sed` prints the flag line with `[="unchanged"]` and, three lines later,
the sentence that permits only `none`, `server` and `client`. Whatever you wrote down in step 1 is
tested in step 2.

Step 2 fails twice and the two messages are in different registers. `--server-dry-run` is not a flag
`kubectl` has, so the complaint is about the command line and no request is made. `--dry-run` *is* a
flag, so the complaint is about the value — the one the pin's own help line offered you. Neither
message mentions the other command, and only one of them names the replacement.

Step 3 prints the ConfigMap as `created` and then `No resources found in dryrun namespace.` with a
zero exit. Nothing was written; the report of a creation is the response body
`api-concepts.md:1317-1318` describes.

Step 4 prints `dryRun=All` and nothing else — one value, matching the enum's only accepted one. The
client run's count is the answer to whether a local dry run talks to the server in v1.37; record the
number rather than predicting it, and read it together with step 6.

Step 5: the server's YAML is substantially longer than the client's. The client output is your file
plus a `creationTimestamp: null` and little else; the server output carries a `strategy`, a
`revisionHistoryLimit`, a `progressDeadlineSeconds`, a `dnsPolicy`, a `restartPolicy`, a
`terminationGracePeriodSeconds`, a `securityContext`, a `schedulerName`, a resource version and a
`status` block. None of it is in the file you wrote and all of it is what you would have stored.

Step 6: the server run is refused and the message names `metadata.name` and the DNS rule it broke.
The client run's exit code is the finding — do not assume it matches 2019.

Step 7: `removed: true` in the frontmatter, a `stages` list whose last entry ends at `1.27`, one file
called `index.md` in the removed-gates directory, and `exit 1` from the `grep -o`. Three independent
readings, one conclusion: there is no `DryRun` gate to set.

Step 8: a non-zero count of `kubernetes_feature_enabled` series, then `0` for the three gate names,
then three sample series showing `name=` and `stage=` labels. The metric works; the gates are not in
it.

Step 9 refuses all three requests. The first refusal is about the *kind*, not the version — the API
server has no `ValidatingWebhookConfiguration` in `admissionregistration.k8s.io/v1beta1`, so the
message is that no kind matched, which is what the removal of a group-version looks like from a
client. The second names required fields, and the count is the point: the post treated one of them as
optional advice. The third is refused for a value that the generated v1 reference documents.

Step 10: two values on the concept page, four on the reference page, and one sentence saying two are
permitted at v1. The disagreement is real and step 9 already resolved it in the only way that counts.

Step 11 prints `kubectl-client-side-apply Update v1` for the first apply and a second entry for
`kubectl Apply v1` after `--server-side`. Two managers on one object, named by the two documents that
each claim to give the default.

Step 12: the first `kubectl diff` exits `0` and prints nothing, because the object was just applied
from the same file. After the `sed`, it prints a unified diff of the `replicas` field and exits `1`.
The external differ prints a one-line *files differ* message instead of the diff — proof that the
variable is read — and its exit status is `diff -q`'s, not `kubectl`'s. The two headings are at
`:53` and `:158`, so the command's own flags are the thirteen between them, and they contain
`-l, --selector`, `--prune`, `--prune-allowlist` and `--server-side` — the second and third
What's-next bullets, delivered. The flag belonging to another post is `-k, --kustomize`.

**Read on**

- [The extensible admission exercise](../2018/01-extensible-admission-is-beta.md) — for the object
  whose field step 9 keeps sending. Given that `sideEffects` is now required and only `None` and
  `NoneOnDryRun` are permitted, which of the two is a claim the API server can check, and what does
  it do when the claim is false?
- [The RuntimeClass exercise](../2018/09-runtimeclass.md) — four of its steps use
  `--dry-run=server` as an ordinary working tool, on an object it never intends to create. Read
  them and say what those steps would have to do instead if the v1.18 change had removed the
  capability rather than renamed the flag.
- [The kustomize exercise](../2018/03-announcing-kustomize.md) — for `-k`, the fourth `apply`
  feature `diff` acquired and the only one on its flag list that this post does not ask for. Read
  what `kubectl kustomize` does before any request is sent, and say whether a `-k` diff can be a
  server-side one.

**Teardown**

```sh
kubectl delete ns dryrun
rm -f /tmp/cm.yaml /tmp/dep.yaml /tmp/badname.yaml /tmp/client.yaml /tmp/server.yaml
kubectl get validatingwebhookconfigurations -o name | grep house; true
```

Leave the guest up; the next exercise in this year reuses it. The namespace takes the ConfigMap and
the Deployment with it. The last line is a check rather than a cleanup: every webhook configuration
in step 9 was sent with `--dry-run=server`, so none of them should exist, and if one does then a
command in that step was run without the flag.
