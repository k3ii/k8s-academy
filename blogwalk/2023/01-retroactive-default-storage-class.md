<a id="retroactive-default-storage-class"></a>

# The gate was stable for one release and then deleted, the instruction for turning it on was already stale on publication day, and the distinction the post drew most carefully — between a field that is absent and one that is empty — is the one the pin's page now states backwards

**Post** — [Kubernetes v1.26: Retroactive Default StorageClass](https://kubernetes.io/blog/2023/01/05/retroactive-default-storage-class/),
2023-01-05.

8,780 bytes over 209 lines, by Roman Bednář (Red Hat), forty-second of the year's seventy-eight
posts by size. It has a sequel in the same year and by the same author — *Kubernetes v1.28:
Retroactive Default StorageClass move to GA*, 2023-08-18, 2,326 bytes, the smallest post the year
produced — and the census sends that one here rather than giving it a walk of its own. Both are
covered below.

**As written**

The v1.25 release added an alpha feature; this post announces its graduation to beta in v1.26
(`:10-14`). The problem it solves is stated at `:20-30`. A default StorageClass is attached to a new
claim by an admission controller, which runs on creation and only on creation, so a claim created
while no default exists never gets one. The post calls such a claim *"stuck"*, and gives two ways to
produce one.

The first is changing the default class (`:32-47`). An administrator who marks the new default
before removing the old one has two defaults for a moment, and a claim created in that window gets
the newer. An administrator who removes the old one first has none for a moment, and a claim created
in *that* window, the post says at `:44-47`, *"would be in `Pending` state forever. The user would
have to fix this by deleting the PVC and recreating it once the default StorageClass was
available."* The second is ordering during cluster installation (`:49-54`): an installer that has to
create storage-consuming components before it creates a StorageClass has an ordering problem it
cannot always solve.

What changed is two sentences at `:56-61`. The PersistentVolume controller now assigns a default
class to any unbound claim whose `storageClassName` is null, and the claim's admission validation in
the API server was relaxed *"to allow the change of values from an unset value to an actual
StorageClass name"* — one transition, in one direction.

Then the section this exercise is mostly about, `:63-79`. Before the feature, a `storageClassName`
of null and a `storageClassName` of `""` were the same request. After it they are not. With a
default present, null means *"Give me a default"* and `""` means *"Give me PersistentVolume that
also has `""` StorageClass name."* With no default present, nothing changes. The post then spends
thirty-three lines, `:81-114`, on an HTML table that walks all four combinations of claim value and
volume value, twice: once without a default class and once with one. It is the only place in the
tree that lays all four combinations out at once.

*How to use it* is `:116-124`, a four-step test drive is `:126-180`, and two new counters —
`retroactive_storageclass_total` and `retroactive_storageclass_errors_total`, on the
PersistentVolume controller — close the technical part at `:182-187`.

**As it runs now**

Nearly all of it, and without a gate. `RetroactiveDefaultStorageClass` reached stable in v1.28 and
its file declares `removed: true`, so at the pin's v1.37 there is no gate to enable and nothing to
enable it in. The behaviour is unconditional. A claim created while no default StorageClass exists
keeps an unset `storageClassName`, and the moment a default appears the control plane fills the
field in. The pin says so at `persistent-volumes.md:918-921` and `:923-926`, and the sequel post
says so with no gate instructions at all.

The `:116-124` instruction has expired, and it was already odd. *"If you want to test the feature
whilst it's alpha, you need to enable the relevant feature gate in the kube-controller-manager and
the kube-apiserver"* is `:118-119`, in a post that announced beta five lines earlier, at `:14`. At
beta the gate defaults to on, so the instruction was superfluous on the day it was published; at the
pin there is no gate at all, so it is now unexecutable as well.

Two other things in the post have not aged. The counters survive the gate that introduced them:
`metrics.md:3640` and `:3647` still list `retroactive_storageclass_errors_total` and
`retroactive_storageclass_total`, both ALPHA-stability, both on kube-controller-manager. And the
post's own test drive contains a command that cannot have produced the output printed under it.
`:162` is `kubectl patch sc -p '...'` with no resource name, which `kubectl` refuses; `:167` is the
output *"storageclass.storage.k8s.io/my-storageclass patched"*, which names a resource the command
never mentions. Step 4 runs both.

The fourth thing is not a behaviour. The pin disagrees with itself, inside one subsection, in
consecutive sentences. `persistent-volumes.md:923-926` says that when a default becomes available
the control plane finds existing claims *"that either have an empty value for `storageClassName` or
do not have this key"* and updates them. `:927-928`, the next sentence, says *"If you have an
existing PVC where the `storageClassName` is `""`, and you configure a default StorageClass, then
this PVC will not get updated."* One of those includes the empty string and the other excludes it.
The post's `:63-79` and its table take a side. So does `:891-895`, higher up the same page, which
draws the same contrast the post draws — `""` binds, a missing key gets updated — but draws it
inside a bullet that opens *"If the admission plugin is turned off, there is no notion of a default
StorageClass"* and then, two lines later, speaks of a default becoming available. Step 5 makes the
cluster answer.

**What this exercise does not cover, and where it lives**

The plain demonstration — a claim made while no default exists, a default marked afterwards, the
field changing on an object that already existed — is already written. [2017's dynamic provisioning
exercise](../2017/01-dynamic-provisioning-and-storage-classes-kubernetes.md) owns it, at its step 6,
along with the reading that makes it confusing: `admission-controllers.md:227` says the plugin
*"ignores any `PersistentVolumeClaim` updates; it acts only on creation"*, which a reader can take
as proof the update cannot happen. That exercise also owns two defaults and newest-wins, and the
post-2017 four-case binding matrix. [2016's dynamic provisioning
exercise](../2016/10-dynamic-provisioning-and-storage-in-kubernetes.md) owns this gate's ladder read
from the other end, and the death of the `storageclass.beta.kubernetes.io/is-default-class`
annotation.

Two labs hold the surrounding mechanics. [Predict the bind](../../labs/08/01-predict-the-bind.md)
owns predicting which volume a claim takes and the `""`-versus-omitted distinction *for binding*,
which is the half of the distinction that predates this post. [Four ways a PVC stays
pending](../../labs/08/06-four-ways-a-pvc-stays-pending.md) owns diagnosing a stuck claim.

What is left here is the arrangement none of them use: the two requests standing side by side,
created in the same second against a cluster with no default, while a default arrives. That is the
only arrangement in which null and `""` can be told apart, and telling them apart is the post's
contribution.

**The diff, and why**

The feature was *retired by being agreed with*. Nothing about the behaviour was withdrawn or
reconsidered; it went alpha, beta, stable and then the gate was deleted because there was no longer
anything to switch. That is the ordinary shape of a successful gate, and this one ran it faster than
almost anything else in the tree — step 10 counts how much faster.

Part of the post was *wrong when it was published*. Not the feature description: the instructions.
`:118-119` tells you to turn the gate on *"whilst it's alpha"* in the post that announces beta, and
`:162` prints a `kubectl patch sc` with no resource name above output at `:167` that names one.
Neither survives contact with a shell, and neither needed a single release to go wrong.

The `null`-versus-`""` section is *still right*, and it is also *never absorbed*, which is the
combination worth the walk. The semantics it describes are exactly the semantics the pin's
controller implements. But the distinction is nowhere else. The sequel post drops it. The v1.28
release announcement at `kubernetes-1.28-blog.md:189-193` states only the missing-key case. The
concept page tries to carry it three times and gets it backwards once, at `:923-926`. Seven files in
the pinned tree return for a search on *retroactive*, one of them a false positive, and of the six
that are left this post is the only one that states both values together. The page a reader is most
likely to land on is the one that contradicts itself. Step 9 reads all of them in order.

The gate's own file records the shortest useful life the tree has on offer.

`RetroactiveDefaultStorageClass`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.25 – v1.25 |
| beta | `true` | — | v1.26 – v1.27 |
| stable | `true` | — | v1.28 – v1.28 |

The file declares `removed: true` and writes no `locked` key on any stage. Three releases separate
the alpha from the stable, and the stable stage is bounded at the release it opened in: the gate was
recognised as stable for v1.28 and for nothing after it. Of the 487 gate files at the pin, five
write a stable stage that lasts exactly one release, and of those five exactly two climbed the full
alpha-beta-stable ladder first — this one and `WindowsGMSA`. Both declare `removed: true`. Step 10
produces the list.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), fresh. One node is enough: nothing
here schedules a Pod, and every behaviour under test is the control plane deciding what a claim's
class is. A fresh kubeadm guest has no StorageClass at all, which is the starting state the post
assumes and the hardest one to arrange on a cloud cluster. Bring the guest up with
[the five provision steps](../../strands/lab-topologies.md#provision), install Kubernetes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), then
`ssh zain@10.10.10.180`. Steps 1 to 8 need the cluster; steps 9 and 10 need only the pinned tree.

**Do**

1. Establish that the gate is not there, in either component the post names, and that the admission
   controller the post blames is running without being configured. The empty results are the
   informative ones:

   ```sh
   kubectl version -o json | python3 -c 'import json,sys
   print("server:", json.load(sys.stdin)["serverVersion"]["gitVersion"])'
   kubectl get sc
   kubectl get --raw /metrics | grep 'kubernetes_feature_enabled' | grep -i retroactive \
     || echo "kube-apiserver: no gate by that name"
   CERT="--cert /etc/kubernetes/pki/apiserver-kubelet-client.crt \
     --key /etc/kubernetes/pki/apiserver-kubelet-client.key"
   sudo curl -sk $CERT https://127.0.0.1:10257/metrics \
     | grep 'kubernetes_feature_enabled' | grep -i retroactive \
     || echo "kube-controller-manager: no gate by that name"
   sudo grep -n 'admission-plugins' /etc/kubernetes/manifests/kube-apiserver.yaml
   ```

   Read `admission-controllers.md:127-131` against that last line and say how `DefaultStorageClass`
   comes to be enabled.

2. Make the two claims the rest of this exercise compares, while there is no default class. The
   first is the post's own manifest from `:132-143`, renamed; the second differs from it by one
   line. Read the field back two ways, because only one of the two ways can tell an absent key from
   an empty one:

   ```sh
   kubectl create namespace retro
   kubectl apply -n retro -f - <<'EOF'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata: { name: pvc-null }
   spec:
     accessModes: ["ReadWriteOnce"]
     resources: { requests: { storage: 1Gi } }
   ---
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata: { name: pvc-empty }
   spec:
     accessModes: ["ReadWriteOnce"]
     storageClassName: ""
     resources: { requests: { storage: 1Gi } }
   EOF
   for P in pvc-null pvc-empty; do
     printf '%s class=[%s] phase=%s\n' "$P" \
       "$(kubectl -n retro get pvc $P -o jsonpath='{.spec.storageClassName}')" \
       "$(kubectl -n retro get pvc $P -o jsonpath='{.status.phase}')"
   done
   kubectl -n retro get pvc pvc-null  -o json | grep -c '"storageClassName"' || true
   kubectl -n retro get pvc pvc-empty -o json | grep '"storageClassName"'
   ```

3. Read why each of them is waiting. The two claims are in the same state for the same reason, and
   this is the last step at which that is true:

   ```sh
   kubectl -n retro describe pvc pvc-null | tail -5
   kubectl -n retro describe pvc pvc-empty | tail -5
   ```

4. Create a class and mark it default — first with the post's command exactly as it is printed at
   `:162`, then with one that can work. The class provisions nothing, so no volume appears from
   anywhere and every later result is the control plane's own bookkeeping:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata: { name: retro-standard }
   provisioner: kubernetes.io/no-provisioner
   volumeBindingMode: WaitForFirstConsumer
   EOF
   kubectl patch sc \
     -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}' \
     || echo "the post's command, as printed at :162 - refused"
   kubectl patch sc retro-standard \
     -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
   kubectl get sc
   ```

   Put the refusal beside the output the post prints at `:167` and say what the command that
   produced that output must have been.

5. The measurement the whole exercise is for. Read both claims again and say which sentence of the
   pin the cluster is obeying:

   ```sh
   sleep 5
   for P in pvc-null pvc-empty; do
     printf '%s class=[%s] phase=%s\n' "$P" \
       "$(kubectl -n retro get pvc $P -o jsonpath='{.spec.storageClassName}')" \
       "$(kubectl -n retro get pvc $P -o jsonpath='{.status.phase}')"
   done
   kubectl -n retro get pvc pvc-empty -o json | grep '"storageClassName"'
   kubectl -n retro describe pvc pvc-null | tail -5
   ```

   `persistent-volumes.md:923-926` says claims *"that either have an empty value for
   `storageClassName` or do not have this key"* are updated. `:927-928` says a claim whose
   `storageClassName` is `""` is not. Write down which claim moved, quote the sentence the cluster
   agrees with, and name the sentence that has to be wrong.

6. Read the two counters the post introduced, on the component the pin says exports them. They are
   the only part of the feature that still carries its name:

   ```sh
   CERT="--cert /etc/kubernetes/pki/apiserver-kubelet-client.crt \
     --key /etc/kubernetes/pki/apiserver-kubelet-client.key"
   sudo curl -sk $CERT https://127.0.0.1:10257/metrics | grep '^retroactive_storageclass'
   kubectl get --raw /metrics | grep -c '^retroactive_storageclass' || true
   ```

   Record the value of `retroactive_storageclass_total` and say how many assignments step 5 should
   have produced. A name that is missing altogether is a different finding from a name reading zero;
   note which you got.

7. Try to perform by hand the transition the post says was made legal, and the one it does not
   mention, on the two claims while both are still unbound:

   ```sh
   kubectl -n retro patch pvc pvc-empty \
     -p '{"spec":{"storageClassName":"retro-standard"}}' \
     || echo "empty string -> class name: refused"
   kubectl -n retro patch pvc pvc-null \
     -p '{"spec":{"storageClassName":""}}' \
     || echo "class name -> empty string: refused"
   kubectl -n retro get pvc pvc-empty -o json | grep '"storageClassName"'
   ```

   The post's `:58-60` licenses exactly one change: unset to a name. Step 5 already used it, and
   nothing in this step is it. Copy both messages down and say which of the two would be needed to
   undo step 5.

8. Now the consequence the pin states in one sentence and nobody demonstrates. Offer a volume that
   would have suited either claim ten minutes ago:

   ```sh
   sudo mkdir -p /mnt/retro-pv
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: PersistentVolume
   metadata: { name: pv-classless }
   spec:
     capacity: { storage: 1Gi }
     accessModes: ["ReadWriteOnce"]
     storageClassName: ""
     hostPath: { path: /mnt/retro-pv }
     persistentVolumeReclaimPolicy: Retain
   EOF
   sleep 5
   kubectl -n retro get pvc
   kubectl get pv
   kubectl -n retro describe pvc pvc-null | tail -4
   ```

   `persistent-volumes.md:895` is *"If the PVC gets updated it will no longer bind to PVs that have
   `storageClassName` also set to `""`."* Say which claim that sentence just cost a volume, and
   whether the post's table at `:81-114` predicted it.

9. Offline. Read every passage in the pinned tree that describes this behaviour, in the order a
   reader would meet them, and score each one on whether it handles the empty string:

   ```sh
   cd /path/to/kubernetes/website/content/en
   grep -rli retroactive docs blog --include='*.md'
   sed -n '891,897p'  docs/concepts/storage/persistent-volumes.md
   sed -n '918,932p'  docs/concepts/storage/persistent-volumes.md
   sed -n '56,79p'    blog/_posts/2023/retroactive-default-storage-class.md
   sed -n '22,28p'    blog/_posts/2023/retroactive-default-storage-class-ga.md
   sed -n '187,193p'  blog/_posts/2023/kubernetes-1.28-blog.md
   ```

   One of the files the search returns is a false positive; find it. Of the rest, mark each passage
   *correct on both values*, *correct but silent on the empty string*, or *wrong*. Then answer the
   question your own table raises: how many passages does a reader have to hold at once before the
   behaviour is unambiguous, and is that number ever one.

10. Offline. Put the gate's shape beside every other gate in the tree, and find the company it
    keeps:

    ```sh
    cd /path/to/kubernetes/website/content/en
    cat docs/reference/command-line-tools-reference/feature-gates/RetroactiveDefaultStorageClass.md
    python3 - <<'PY'
    import yaml, glob, os
    G = "docs/reference/command-line-tools-reference/feature-gates"
    def front(path):
        return yaml.safe_load(open(path).read().split("---")[1])
    tot = 0
    short = []
    for path in sorted(glob.glob(G + "/*.md")):
        if os.path.basename(path) == "index.md":
            continue
        tot += 1
        d = front(path)
        stages = d.get("stages") or []
        for s in stages:
            if s["stage"] == "stable" and s.get("toVersion") == s["fromVersion"]:
                names = [x["stage"] for x in stages]
                short.append((os.path.basename(path)[:-3], names, d.get("removed")))
                break
    print("gate files: %d" % tot)
    for name, names, removed in short:
        print("%-34s %-22s removed=%s" % (name, "-".join(names), removed))
    PY
    ```

    State how many of the five went up the full ladder, and what the other three did instead. Then
    say what a one-release stable stage means about when the file stops being maintained, as against
    when the behaviour stops being conditional.

**Expect**

Step 1 prints a v1.35 server and *No resources found* for `kubectl get sc`. Both gate greps come
back empty, so both fallback lines print: the gate is absent from the API server and from the
controller manager, which is what `removed: true` means measured rather than read. The manifest grep
finds one line, `--enable-admission-plugins=NodeRestriction`, and `DefaultStorageClass` is not in it
— it is in the default set at `admission-controllers.md:130`, enabled because nobody disabled it.

Step 2 creates both claims. Both report `class=[]` and `phase=Pending`, which is exactly why the
jsonpath reading is not enough: it renders an absent key and an empty string identically. The two
JSON reads separate them. `pvc-null` returns 0 — `kubectl` omits the field entirely, because an
unset `storageClassName` is a nil pointer and never serialises. `pvc-empty` prints one line,
`"storageClassName": ""`; the quotes in the pattern are what keep the `managedFields` entry out of
the count. Keep both outputs; step 5 is a comparison against them.

Step 3 shows the same event on both, along the lines of *no persistent volumes available for this
claim and no storage class is set*. Nothing distinguishes the two claims yet, to the cluster or to a
reader.

Step 4 creates `retro-standard`. The post's command fails before it reaches the API server, with a
usage error from `kubectl` about a required resource name; the exact wording varies by client
version, and the point is only that it cannot have printed `:167`. The named form succeeds and
`kubectl get sc` shows `retro-standard (default)`.

Step 5 is the answer. After a few seconds `pvc-null` reads `class=[retro-standard]` and `pvc-empty`
still reads `class=[]`, with its JSON still showing `"storageClassName": ""`. The claim with no key
was updated; the claim with an empty string was not. That is `:927-928` and it is not `:923-926`.
`pvc-null`'s events have changed too — it is now waiting for a first consumer, because
`retro-standard` binds late, rather than waiting for a volume that does not exist.

Step 6 returns both counters from port 10257 and nothing from the API server, so the count prints 0.
`retroactive_storageclass_total` should read 1: one claim, one assignment.
`retroactive_storageclass_errors_total` should read 0. Two ALPHA-stability counters, named after a
gate that no longer exists, still exported nine releases after its removal.

Step 7 is refused twice. Both patches report that the field is immutable, because the only
storage-class transition the API server permits on an existing claim is the one the controller
already performed: nil to a name. There is no supported way back. This is the sentence at `:58-60`
read as a boundary rather than a feature — the change was narrow on purpose, and the narrowness is
why step 5's result is permanent.

Step 8 binds `pv-classless` to `pvc-empty` within seconds. `pvc-null` stays Pending and cannot take
that volume, because its class is now `retro-standard` and the volume's is `""`. That is
`persistent-volumes.md:895` happening: the update in step 5 cost `pvc-null` a volume it would have
matched in step 3. The post's table predicts it — the *with default class* half says the null
claim's class updates while the empty-string claim binds — and the concept page says it in one
sentence that nothing on the page connects to the contradiction two paragraphs down.

Step 9 returns seven files for *retroactive*. One,
`blog/_posts/2022/scalable-job-tracking-ga/index.md`, uses the word in an unrelated sense and is the
false positive. Of the six that remain, `:923-926` is the only passage that is wrong. `:891-895` has
the contrast right but keeps it under a bullet about the admission plugin being off. `:927-928` is
the only sentence in the retroactive subsection that names the empty string, and it is the sentence
immediately after the wrong one. This post's `:63-79` is the only passage anywhere that states both
values together and unconditionally. The GA post and the release announcement are correct and silent
on the empty string. A reader needs two sentences from the same page, read in order, to get the
whole rule, and the first of them is the one that is wrong.

Step 10 prints 487 gate files and five with a one-release stable stage: `DynamicResourceAllocation`,
`ProbeTerminationGracePeriod`, `ReadOnlyAPIDataVolumes`, `RetroactiveDefaultStorageClass` and
`WindowsGMSA`. Two of the five show `alpha-beta-stable` — this gate and `WindowsGMSA` — and both are
removed. The other three reached stable by a shorter route. The lesson the list carries is that a
one-release stable stage is not a short feature life; it is a short *file* life. The behaviour is
permanent, and the file stopped describing it the moment there was nothing left to switch.

**Read on**

1. `docs/reference/access-authn-authz/admission-controllers.md:212-230`, the whole
   `DefaultStorageClass` section. Nineteen lines, written entirely about creation, and the sentence
   at `:227` — *"This admission controller ignores any `PersistentVolumeClaim` updates; it acts only
   on creation"* — is still true and still, read alone, makes step 5 look impossible. The page has
   never been given a pointer to the controller that does the updating.

2. `blog/_posts/2023/retroactive-default-storage-class-ga.md`, all 2,326 bytes of it, the smallest
   post of the year's seventy-eight. It is worth reading beside the January post rather than after
   it. It restates *what changed* in one paragraph, and in doing so drops the `null`-versus-`""`
   section, the table, and the counters. What survives a graduation announcement is a fair guide to
   what the project considered the feature to be.

3. `blog/_posts/2023/kubernetes-1.28-blog.md:187-193`, the release-note paragraph, and `:241`, where
   the same release lists the enhancement by number. The paragraph is the shortest correct statement
   of the behaviour anywhere in the tree and it covers only the missing-key case. Read it as the
   third independent chance the project had to carry the distinction forward.

4. `docs/concepts/storage/persistent-volumes.md:882-897`, the bullets above the subsection this
   exercise lives in. They are where the default-class rules are actually stated, including the
   newest default winning and the behaviour when the admission plugin is off. `:894-895` is the
   page's first telling of the retroactive rule, twenty-four lines above the two tellings that
   contradict each other, and it is filed under a condition that excludes the case it describes.
   Reading the bullets first changes which of the two later sentences looks like the typo.

5. *Unanswerable from the pin:* whether `:923-926` is a slip or a position. The sentence reads like
   someone writing quickly who treated *unset* and *empty* as synonyms, which they were until this
   feature made them different. But a documentation tree at one revision cannot distinguish a slip
   from a deliberate simplification that the next sentence was later added to correct, and it cannot
   say how long the two sentences have sat next to each other. What it can say is that the
   correction was written, placed immediately after the error, and never applied to the error
   itself.

**Teardown** — `kubectl delete ns retro; kubectl delete pv pv-classless; kubectl delete sc
retro-standard; sudo rm -rf /mnt/retro-pv` — the namespace first, because `pvc-empty` holds
`pv-classless` and the volume's `Retain` policy will leave it `Released` rather than let it go. Then
[the teardown step](../../strands/lab-topologies.md#teardown).
