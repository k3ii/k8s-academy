<a id="using-deployment-objects-with"></a>
# Every command in this post still runs, the one that made a Deployment now makes a Pod, and the field behind its rollback is gone

**Post** — [Using Deployment objects with Kubernetes 1.2](https://kubernetes.io/blog/2016/04/using-deployment-objects-with/),
2016-04-01, Kubernetes v1.2 — the seventh instalment of the *Five days of Kubernetes 1.2* series,
written while Deployment was still beta. The post says so itself, in a note under the conclusion:
*"In Kubernetes 1.2, Deployment (beta release) is now feature-complete and enabled by default."*

**As written** — the post opens by asking why Deployments are needed at all, and answers with a
comparison:

> Compared with kubectl rolling-update, Deployment API is much faster, is declarative, is
> implemented server-side and has more features (for example, you can rollback to any previous
> revision even after the rolling update is done).

Then five commands, in order, and no manifest anywhere. First, serve the demo's static site out of
a checkout of the website repository:

```
$ kubectl proxy --www=docs/user-guide/update-demo/local/ &
```

with the reader told to visit `http://localhost:8001/static/`. Then create the app:

```
$ kubectl run update-demo
--image=gcr.io/google\_containers/update-demo:nautilus --port=80 -l name=update-demo

deployment “update-demo” created
```

Then scale it, edit it, and break it:

```
$ kubectl scale deployment/update-demo --replicas=4
deployment "update-demo" scaled

$ kubectl edit deployment/update-demo
```

— changing `.spec.template.spec.containers[0].image` from `nautilus` to `kitty`, a tag that does not
exist. The post's account of what happens next is one sentence:

> If you look closer, you'll find that the pods with the new "kitty" tagged image stays pending. The
> Deployment automatically stops the rollout if it's failing.

and the fix is one command:

```
$ kubectl rollout undo deployment/update-demo
deployment "update-demo" rolled back
```

A footnote explains how `kubectl run` decides what to create:

> The "--generator" flag can be used with "kubectl run" to generate other types of resources, for
> example, set it to "run/v1" to create a Replication Controller, which was the default in 1.1 and
> 1.0, and to "run-pod/v1" to create a Pod, such as for --restart=Never pods.

**As it runs now** — four different fates, and the second is the one that will cost you an
afternoon if you do not separate it from the first.

1. **Still exact.** `kubectl proxy --www=DIR` is intact at the pin, down to the two defaults the
   post relies on without naming them: `-p, --port int` is `Default: 8001` and `-P, --www-prefix
   string` is `Default: "/static/"`, so `http://localhost:8001/static/` is still the right URL. The
   reference even keeps an example of the pairing, `kubectl proxy --www=/my/files
   --www-prefix=/static/`. `kubectl scale`, `kubectl edit`, `kubectl describe` and `kubectl rollout
   undo` — including `--to-revision` — are all still there, spelled as printed.
2. **Succeeds, and creates something else.** `kubectl run` no longer creates a Deployment. Its
   synopsis at the pin is *"Create and run a particular image in a pod"*, and every example it
   carries produces a Pod. The post's flags all survive — `--image`, `--port`, and `-l` as the
   shorthand for `--labels` — so the command exits zero and prints a creation message. It is the
   *kind* that changed, silently, and the next command in the post is the one that notices.
3. **Errors outright.** `kubectl scale deployment/update-demo` and `kubectl edit
   deployment/update-demo` both fail, because there is no Deployment to scale or edit. `--generator`
   is gone from `kubectl run` entirely, so the footnote's escape hatch is not a deprecated flag but
   an unknown one. And the API version any 2016 Deployment manifest carries is not served:
   *"The **extensions/v1beta1**, **apps/v1beta1**, and **apps/v1beta2** API versions of Deployment
   are no longer served as of v1.16."*
4. **Not recoverable, and worth saying so.** The post's step 3 asks you to fetch
   `github.com/kubernetes/kubernetes.github.io/tree/master/docs/user-guide/update-demo`. That
   repository was renamed, and there is no `user-guide/update-demo` in the pinned tree; across all
   of `content/en/docs` the string `kubernetes.github.io` survives in exactly one file. Five of the
   post's six internal doc links — `/docs/getting-started-guides/`, `/docs/user-guide/prereqs/`,
   `/docs/user-guide/update-demo`, `/docs/user-guide/deployments/`, `/docs/user-guide/replicasets/`
   — resolve to nothing at the pin. So the little website of pod cards cannot be brought back, and
   *Do* does not pretend otherwise: it serves a directory of your own through the same flag, which
   is the part of the demo that still works.

The image path is its own small archaeology. `gcr.io/google_containers` survives in the whole pinned
docs tree in exactly one file, a ConfigMap task page, where it appears twice. `k8s.gcr.io`, the registry that
replaced it, appears **zero** times, having been scrubbed in favour of `registry.k8s.io` across 47
files. Whether the old path still answers is not something this repository can tell you, so *Do*
runs the post's image reference and has you report what the kubelet says rather than being told in
advance.

**The diff, and why** — the post broke, but not where it looks like it broke. Every individual
command still parses; what came apart is the sentence that justifies them. Take the four claims in
it one at a time.

*"Compared with kubectl rolling-update"* — there is nothing to compare against. `kubectl
rolling-update` is not deprecated in the pinned reference; it is absent. The generated command
directory holds `kubectl_rollout` and nothing matching `rolling`. The post's framing question —
*why would we need Deployments?* — is one no reader can now ask, because the alternative it was
arguing against left no trace in the documentation. This is the ordinary fate of a post written to
persuade rather than to instruct: the argument decays faster than the commands.

*"is implemented server-side"* — this is the claim that actually broke, and the mechanism is
precise. In `extensions/v1beta1` a rollback was a write to the object: you set `spec.rollbackTo` and
the controller performed the revert. The deprecation guide's notable-changes list for the move to
`apps/v1` opens with `spec.rollbackTo` **is removed**, and across the entire pinned docs tree the
string `rollbackTo` survives in exactly one file — that list. It is not in the `apps/v1` Deployment
API reference, because there is no such field to document. Meanwhile `kubectl rollout undo` still
works and the concept page still shows it printing `deployment.apps/nginx-deployment rolled back`.
So the operation the post singles out as *server-side* is the one operation that stopped being a
field, while keeping its command intact — the most misleading possible combination. The pinned
documentation never says who computes the revert now, which is why *Do* settles it with
`--dry-run=client` instead of asserting it.

*"you can rollback to any previous revision"* — literally true when written, and literally false
now, by a default. The same notable-changes list records that `spec.revisionHistoryLimit` *"now
defaults to `10` (the default in `apps/v1beta1` was `2`, the default in `extensions/v1beta1` was to
retain all)"*. Retain all is what makes *any previous revision* a true sentence. Ten is what makes
it a true sentence about the last ten. The concept page adds the sharp end of it: *"Explicitly
setting this field to 0, will result in cleaning up all the history of your Deployment thus that
Deployment will not be able to roll back."* The feature the post sells hardest is the one that
quietly acquired a ceiling.

*"The Deployment automatically stops the rollout if it's failing"* — here the pin contradicts
itself, and the disagreement is the most useful thing in the exercise. `deployment.md` carries a
note beside a stuck `ImagePullBackOff` rollout saying *"The Deployment controller stops the bad
rollout automatically, and stops scaling up the new ReplicaSet. This depends on the rollingUpdate
parameters (`maxUnavailable` specifically) that you have specified."* Almost nine hundred lines further down, the same page says *"Kubernetes takes no action on a stalled Deployment other than to report a status
condition with `reason: ProgressDeadlineExceeded`. Higher level orchestrators can take advantage of
it and act accordingly, for example, rollback the Deployment to its previous version."* Both
sentences are in the pinned tree at one commit and they do not describe the same system. Read
together, what they mean is that nothing *stops*: the new ReplicaSet simply cannot grow past
`maxSurge` while the old one cannot shrink past `maxUnavailable`, so a failing rollout stalls
against arithmetic. That is not a decision, and in 2016 it was not even reported — the deadline
that produces the condition did not exist, since `spec.progressDeadlineSeconds` *"now defaults to
`600` seconds (the default in `extensions/v1beta1` was no deadline)"*. So the post described an
emergent stall as though it were a safety mechanism; ten years later a report arrived, and the
mechanism still has not.

The arithmetic itself moved, which matters for the post's other promise — *"without a service
outage"*. `maxSurge` and `maxUnavailable` *"now default to `25%` (the default in `extensions/v1beta1`
was `1`)"*, with `maxUnavailable` computed *"by rounding down"* and `maxSurge` *"by rounding up"*. At
the post's four replicas the two eras agree: one and one either way. At the single replica the post
starts with, they do not. Twenty-five percent of one rounds down to zero unavailable and up to one
surge, so the replacement must be Ready before the original goes; an absolute `1` permitted the
original to go first. The post's outage-free claim is truer now than when it was made, at exactly
the replica count where it was making it.

One more redefinition sits under the screenshots. `.status.replicas` in the `apps/v1` reference is
*"Total number of non-terminating pods targeted by this deployment"*, and terminating pods are
counted separately in a field that did not exist for the post's first nine years:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.33 – v1.34 |
| beta | `true` | — | v1.35 – |

`DeploymentReplicaSetTerminatingReplicas` is beta and **on** at the pin — the API reference says so
in the field's own description, *"This is a beta field and requires enabling
DeploymentReplicaSetTerminatingReplicas feature (enabled by default)"* — so `.status.terminatingReplicas`
is readable on a v1.37 cluster with no flags touched. The gate file declares no `removed:` and no
`former_titles:`. What it buys a reader of this post is the missing half of *"the update seems
stuck"*: the concept page notes that terminating pods *"may take a long time to terminate"* so *"the
total number of all pods can temporarily exceed `.spec.replicas`"*. The 2016 reader watching four
cards on a web page had no field that distinguished a pod on its way up from one on its way out.
`kubectl get pods` did not tell them, and neither did the Deployment's status.

Finally, the post's own output betrays its era in a way the pinned documentation has not finished
cleaning up. The post describes a pod as `update-demo-1326485872-a4key`; the middle segment is the
`pod-template-hash`, and it is a decimal number. At the pin the same page that documents the label
shows it as `pod-template-hash=75675f5897` on pods named `nginx-deployment-75675f5897-7ci7o` — and
then, four hundred lines further down, still prints `pod-template-hash=1159050644` and
`nginx-deployment-1564180365-70iae` inside two sample outputs it never regenerated, one of them
alongside a `QoS Tier:` block that `kubectl describe` has not emitted in years. The current
Deployment page carries both eras of hash, which is a fair warning about how much of any
documentation tree is a screenshot of an older cluster.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), fresh. One node is enough: the whole
exercise is four tiny pods and a great deal of reading of `.status`, and nothing here depends on
scheduling across nodes. Bring the guest up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, install Kubernetes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), then
`ssh zain@10.10.10.180`.

**Do**

1. Prove the survivor, then prove what it cannot serve. Make a directory with one file in it —
   `mkdir -p ~/www && echo 'still here' > ~/www/index.html` — and run `kubectl proxy --www=$HOME/www
   &`, with no other flags. `curl -s localhost:8001/static/`. Then look for what the post actually
   pointed the flag at: is there a `docs/user-guide/update-demo/local/` anywhere you can obtain?
   Write down where you looked. Kill the proxy when you are done reading step 2's output.

2. Run the post's create command verbatim, era image and all, and then ask what appeared:

   ```
   kubectl run update-demo --image=gcr.io/google_containers/update-demo:nautilus --port=80 -l name=update-demo
   kubectl get all -l name=update-demo
   kubectl get pod update-demo -o jsonpath='{.status.containerStatuses[0].state}{"\n"}'
   ```

   Record two things separately: what kind of object the first command reports creating, and what
   the container's state is. These are different failures and only one of them is about the image.

3. Continue the post as written, both commands, and then try its footnote:

   ```
   kubectl scale deployment/update-demo --replicas=4
   kubectl edit deployment/update-demo
   kubectl run gen-test --image=registry.k8s.io/e2e-test-images/agnhost:2.53 --generator=run/v1
   ```

   Note which of the three complains about the object and which complains about the command line.

4. Clear the ground — `kubectl delete pod update-demo` — and write what the post meant, in the
   version it would have written it in. Apply this first:

   ```yaml
   apiVersion: extensions/v1beta1
   kind: Deployment
   metadata:
     name: update-demo
   spec:
     replicas: 1
     template:
       metadata:
         labels:
           name: update-demo
       spec:
         containers:
         - name: update-demo
           image: registry.k8s.io/e2e-test-images/agnhost:2.53
           args: ["netexec", "--http-port=8080"]
           ports:
           - containerPort: 8080
   ```

5. Now change only `apiVersion` to `apps/v1` and apply it again. Read the error, add the one field
   it names — `spec.selector.matchLabels.name: update-demo` — and apply a third time. Three
   attempts, three different outcomes; keep all three error strings.

6. `kubectl scale deployment/update-demo --replicas=4`, then `kubectl rollout history
   deployment/update-demo`. How many revisions? Compare against the concept page's rule that a
   rollout fires *"if and only if"* `.spec.template` changed.

7. Break it the post's way and read the status the post could not:

   ```
   kubectl set image deployment/update-demo update-demo=registry.k8s.io/e2e-test-images/agnhost:kitty
   kubectl get rs -l name=update-demo
   kubectl get pods -l name=update-demo
   kubectl get deploy update-demo -o jsonpath='{range .status.conditions[*]}{.type}={.status} {.reason}{"\n"}{end}'
   kubectl get deploy update-demo -o jsonpath='replicas={.status.replicas} updated={.status.updatedReplicas} unavailable={.status.unavailableReplicas} terminating={.status.terminatingReplicas}{"\n"}'
   ```

   Count how many new pods the controller created before it stopped. Then work out from
   `maxSurge` and `maxUnavailable` at four replicas whether it could have created any more.

8. Test whether anything stops the rollout. `kubectl patch deployment update-demo -p '{"spec":
   {"progressDeadlineSeconds":30}}'`, re-run the bad `set image` if the rollout has settled, wait a
   minute, and re-read `.status.conditions`. Then re-read `kubectl get rs -l name=update-demo`. Did
   the deadline change the ReplicaSets, or only the conditions?

9. Roll back, but find out who does the work first:

   ```
   kubectl rollout undo deployment/update-demo --dry-run=client
   kubectl rollout undo deployment/update-demo
   kubectl rollout history deployment/update-demo --revision=2
   ```

   The first command prints only what would be sent to the server. Whatever it prints answers the
   question the pinned documentation does not. Then compare the third command's output against the
   sample the concept page prints for the same command, field by field.

10. Put a ceiling on the history and try to reach past it. `kubectl patch deployment update-demo -p
    '{"spec":{"revisionHistoryLimit":1}}'`, then change `.spec.template` three times in a
    row — `kubectl set env deployment/update-demo ROUND=1`, then `ROUND=2`, then `ROUND=3` —
    waiting for each rollout to finish.
    `kubectl get rs -l name=update-demo` and `kubectl rollout history deployment/update-demo`, then
    `kubectl rollout undo deployment/update-demo --to-revision=1`.

**Expect** — step 1: `still here`, served from a path the API server never sees, which is
the point — `--www` is a kubectl feature, not an API one. The post's directory is not obtainable
from the pinned tree.

Step 2: `pod/update-demo created`, not `deployment "update-demo" created`. Then a container state
of `waiting` with a reason of `ErrImagePull` or `ImagePullBackOff` — report which, and the message
alongside it, since that message is the only evidence in this exercise about the old registry.

Step 3: the first two commands return `Error from server (NotFound)` naming
`deployments.apps "update-demo"` — the object, not the verb, is what is missing. The third returns
`unknown flag: --generator` before it ever reaches the API server. Two commands failed on state and
one failed on syntax.

Step 4: `no matches for kind "Deployment" in version "extensions/v1beta1"`, the same shape of
refusal that `extensions/v1beta1` Ingress gives in
[03](03-kubernetes-1-2-and-simplifying-advanced-networking-with-ingress.md). The group-version is
not served, so nothing in the body is even read.

Step 5: a `Required value` error naming `spec.selector`, then success. The manifest that used to be
complete is now short one field — and note what the missing field would have defaulted to in the
version that accepted it, since that default is what let the post get away with never writing a
manifest at all.

Step 6: one revision, not two. Scaling changed `.spec.replicas`, not `.spec.template`.

Step 7: the new ReplicaSet reaches one pod, stuck in `ImagePullBackOff`, and stays there while the
old ReplicaSet keeps three of its four. `Available=True`, `Progressing=True` with a reason of
`ReplicaSetUpdated` at first. `terminating=0` — nothing is on its way out, because nothing was
allowed to leave. The arithmetic: `maxSurge` 25% of 4 rounds up to 1, `maxUnavailable` 25% of 4
rounds down to 1, so five pods total and three old ones minimum is the whole envelope, and the
controller is already at the edge of it.

Step 8: `Progressing=False` with `reason: ProgressDeadlineExceeded`, and the ReplicaSets exactly as
they were. The deadline wrote a sentence into `.status` and touched nothing else. That is the
disagreement in the pinned docs resolved by observation: the note that says the controller *"stops
the bad rollout"* is describing the arithmetic of step 7, and the note that says Kubernetes *"takes
no action"* is describing step 8.

Step 9: `--dry-run=client` prints a whole object. Which one, and what is different about its
`.spec.template` — that is the answer to *is the rollback server-side*. Then the real command
prints `deployment.apps/update-demo rolled back`. The `--revision=2` output will not match the
concept page's sample: the page's `pod-template-hash` is a decimal number and yours will not be,
and the page's `QoS Tier:` block will not appear at all.

Step 10: two ReplicaSets survive rather than four, `rollout history` lists two revisions rather
than four, and `--to-revision=1` fails because the ReplicaSet holding revision 1 was garbage
collected. Name the error. This is *"any previous revision"* meeting its default.

**Read on** — the pin's [Deployment `apps/v1` API reference](https://kubernetes.io/docs/reference/kubernetes-api/apps/deployment-v1/):
search the whole page for `rollbackTo` and confirm it is not there, then read the `.status`
descriptions for `replicas`, `updatedReplicas`, `unavailableReplicas` and `terminatingReplicas`
together and answer one question — with `rollbackTo` gone and nothing in the spec naming a
revision, which of the fields on this page would a *server-side* rollback have had to write to, and
what does its absence say about where `kubectl rollout undo` does its arithmetic? Then read the
[deprecation guide's Deployment entry](https://kubernetes.io/docs/reference/using-api/deprecation-guide/#deployment-v116)
and pick out which of its five notable changes a 2016 reader would have noticed immediately and
which four they would only have noticed months later.

**Teardown** — `kubectl delete deploy update-demo; kubectl delete pod gen-test --ignore-not-found`.
Kill the backgrounded `kubectl proxy` and remove `~/www`. Take the guest down with
[teardown](../../strands/lab-topologies.md#teardown); the next exercise wants a clean cluster and
nothing here is worth carrying forward.
