<a id="kubernetes-release-1.20-fsGroupChangePolicy-fsGroupPolicy"></a>

# The one page in the pin that documents `fsGroupPolicy` says to refer to the specific values for details and no page in the pin lists them, this post's five-line fence is now the task page's own sample byte for byte, and a gate that arrived two releases later turns the first half off

**Post** — [Kubernetes 1.20: Granular Control of Volume Permission
Changes](https://kubernetes.io/blog/2020/12/14/kubernetes-release-1.20-fsGroupChangePolicy-fsGroupPolicy/),
2020-12-14, by Hemant Kumar (Red Hat) and Christian Huffman (Red Hat). Sixty lines, four `###`
headings and three `####` ones, a single YAML fence, no images.

**As written**

The post announces two beta features in 1.20, offered as one thing: more control over how volume
permissions are applied when a volume is mounted inside a Pod.

The first half is a performance complaint with a fix attached. Each time a volume is mounted, the
post says, Kubernetes must recursively `chown()` and `chmod()` every file and directory inside it,
and it does so even when the group ownership already matches the value the Pod asks for, which `can
be pretty expensive for larger volumes with lots of small files, which causes pod startup to take a
long time`. The remedy is a new Pod-level field: set `fsGroupChangePolicy` to `OnRootMismatch` and
the walk is skipped when the root of the volume already has the right permissions. The post attaches
the guarantee that makes the shortcut safe — `Kubernetes ensures that permissions of the top-level
directory are changed last the first time it applies permissions`. Its single fence is five lines of
`securityContext` carrying `runAsUser`, `runAsGroup`, `fsGroup` and the new field.

The second half is an API rather than a field. Some volume types never got the recursive treatment
in the first place — the post names NFS and Gluster — and others cannot support `chown()` at all, so
applying the policy to them produces errors for work that could never have succeeded. So `CSIDriver`
gains a `.spec.fsGroupPolicy` field and each driver declares what it wants. The post enumerates the
values: `Three FSGroupPolicy values are available as of Kubernetes 1.20, with more planned for
future releases.` — `ReadWriteOnceWithFSType`, the default, which preserves the previous behaviour;
`File`, which always attempts the change; and `None`, which never does. Adopting it is a non-event:
`There’s no additional deployment required!`

The post closes with a forecast. `Depending on feedback and adoption, the Kubernetes team plans to
push these implementations to GA in either 1.21 or 1.22.`

**As it runs now**

**The post's fence is the documentation's fence, byte for byte.** `security-context.md:359` opens
*Configure volume permission and ownership change policy for Pods* — the section the post's own *How
can I learn more?* paragraph links to — and `:383-389` renders a YAML block that `diff` reports as
identical to the post's `:20-26`, character for character. The section carries a stability stamp at
`:361` reading `{{< feature-state for_k8s_version="v1.23" state="stable" >}}`, and the gate file for
`ConfigurableFSGroupPolicy` points its reader at the same anchor. Post, gate file and task page all
reference one another and none of the three disagrees.

**Both fields survive; both gates are gone.** `pod-v1.md:2273-2274` documents `fsGroupChangePolicy`
under `PodSecurityContext`, and `csi-driver-v1.md:72-73` documents `fsGroupPolicy` under
`CSIDriverSpec`. Neither page mentions a feature gate, because both gates were deleted after v1.25.
What the post announced as beta is now simply the API.

**The reference tells you to consult a list the pin does not contain.** Three files under
`content/en/docs` contain the string `fsGroupPolicy`, and two of them are the feature-gate files
that carry it in their names. The third is the generated `csi-driver-v1.md`, whose row at `:73`
reads in part `Refer to the specific FSGroupPolicy values for additional details`. There is no such
enumeration in the pin. `ReadWriteOnceWithFSType` appears in that one row and in this post, and
nowhere else; `File` and `None` are never written down as values of this field on any page. The
post's *How can I learn more?* paragraph sends the reader to a CSI page on
`kubernetes-csi.github.io` — outside the pin entirely. Inside it, this post is the enumeration.

**The default the post never names is `Always`.** The post describes the recursive walk as what
happens, and then offers one value to switch it off; it never says what the field is called when you
leave it alone. `pod-v1.md:2274` does: two valid values, `OnRootMismatch` and `Always`, and `If not
specified, "Always" is used`. So the behaviour the first half of the post complains about is still
the behaviour a Pod gets by default, nearly six years and one stable graduation later. Nothing
changed the default; the post added a way to opt out of it.

**There are two exception lists and they are not the same list.** The post's exceptions are volume
types the cluster never walked at all: NFS and Gluster, still described that way at
`persistent-volume-v1.md:721` and `:593`. The pin's exceptions are about the field:
`security-context.md:391-396` and `pod-v1.md:2274` both say the policy has no effect on `secret`,
`configMap` and `emptyDir`. The same generated file says ConfigMap volumes at `:672`, empty
directory volumes at `:1123` and Secret volumes at `:2759` *do* support ownership management. Both
statements can be true only if supporting ownership management and responding to the policy are
separate things, and no page in the pin says that they are. The *Do* steps measure which of the two
the cluster believes.

**A gate the post could not have known about turns the first half off.** `security-context.md:398`
opens *Delegating volume permission and ownership change to CSI driver*, stamped stable at v1.26 at
`:400`. Its body at `:402-410` says that when a driver advertises the `VOLUME_MOUNT_GROUP`
`NodeServiceCapability`, the kubelet passes `fsGroup` down through `NodeStageVolume` and
`NodePublishVolume` instead of walking the tree itself, and that in that case the post's field `does
not take effect`. The gate behind it, `DelegateFSGroupToCSIDriver`, went alpha at v1.22 — two
releases after this post — so the first half of the post acquired a condition under which it is
inert, and the pin documents that condition in the very next section of the page that carries the
post's fence.

**The pin does not say whether the volume type this exercise has to use is covered.** `hostPath`
volumes explicitly do not support ownership management (`persistent-volume-v1.md:622`), and the
policy has no effect on `emptyDir`, which leaves a `local` PersistentVolume as the cheapest way to
put a great many files behind an `fsGroup` on a one-node cluster. `LocalVolumeSource` at
`persistent-volume-v1.md:698-716` documents two fields and says nothing at all about ownership
management, where twelve of the twenty-two volume sources in the same generated file state one way
or the other. Whether a `local` volume gets walked is therefore a measurement here, not a citation.

**What this exercise does not cover, and where it lives.** The shape of the `CSIDriver` object — all
twelve of its spec fields, `fsGroupPolicy` among them — belongs to [the exercise on the CSI
beta](../2018/02-container-storage-interface-beta.md); this one keeps only what the field means and
what the API server will accept in it. Storage capacity and generic ephemeral volumes belong to [the
exercise on capacity tracking](05-ephemeral-volumes-with-storage-capacity-tracking.md). The first
code sample on this same task page, and the Pod Security Standards that judge it, belong to [the
exercise on the runc escape](../2019/02-runc-cve-2019-5736.md). Delegation to CSI drivers got an
announcement post of its own two years after this one; that post falls in a later year of the walk
and is not linked from here.

**The diff, and why**

**Nothing in this post broke.** Both fields exist under the names the post gives them, both carry
the semantics the post describes, the sample is still valid, and the section of the documentation
the post points at is the section that now carries its fence. On the census this is a `walk` on the
second clause alone: the reading is cheap and correct, and the value is in what you can measure that
the pin will not tell you. The template's seventh case is what makes that worth an exercise: the
second half of the post was **never absorbed**, so this is not a record of an API but the pin's only
enumeration of part of one.

**The forecast slipped, and landed in a small cohort.** GA was predicted for 1.21 or 1.22 and
arrived at 1.23. Of the 487 feature-gate files in the pin, six have a `stable` row beginning at
1.23: the two here, `GenericEphemeralVolume`, `IPv6DualStack`, `IngressClassNamespacedParams` and
`TTLAfterFinished`. Five of those six are named by exercises in this directory — the two here, and
one each in the exercises on capacity tracking, EndpointSlices and the Ingress API.
`TTLAfterFinished` is the only member of the cohort the walk has not touched anywhere.

**The new case is a post that got more load-bearing, not less.** The archive already holds a post
the pinned documentation cites as its own reference, and a post whose sample became the
documentation's sample. This one is both, and then a third thing: the API it announces has outlived
its own description. The gate retired, the field stayed, and the reference page kept the sentence
that points at a list of values while the list itself never appeared on any page under
`content/en/docs`. That is not the documentation going stale — a generated page cannot go stale — it
is the documentation never having been written, with a blog post from 2020 quietly holding the only
enumeration anywhere in the archive being walked — the 2022 post on the same API does not repeat it.
The exercise is worth doing because the pin cannot answer the two questions a reader of this post
will actually have: does the policy do anything for the volume types you have, and what will the API
server accept in `fsGroupPolicy`.

**The ladder**

Three gates, all three `removed: true`, transcribed from their `stages:` lists parsed as YAML. The
first two are the ones the post announces; the third is the one that came afterwards and conditions
the first.

```
ConfigurableFSGroupPolicy    alpha  false  1.18 - 1.19
                             beta   true   1.20 - 1.22
                             stable true   1.23 - 1.25
CSIVolumeFSGroupPolicy       alpha  false  1.19 - 1.19
                             beta   true   1.20 - 1.22
                             stable true   1.23 - 1.25
DelegateFSGroupToCSIDriver   alpha  false  1.22 - 1.22
                             beta   true   1.23 - 1.25
                             stable true   1.26 - 1.27
```

The post calls both of the first two new beta features, which is true of the beta rows and hides the
difference in the alpha ones: `ConfigurableFSGroupPolicy` had been alpha since 1.18, two releases
before this post, and `CSIVolumeFSGroupPolicy` since 1.19. From 1.20 onward the two are
indistinguishable — same beta row, same stable row, same removal — which is what the post's framing
of them as one announcement predicts. The third gate begins its beta row in the release the first
two end their journey in, and is stable by 1.26; its body names `NodeStageVolume` and
`NodePublishVolume` as the calls that carry `fsGroup` to the driver.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo), with the control-plane taint removed in step 1 so
that workload Pods schedule. Everything else this exercise needs is built on the node: a directory
under `/mnt` holding three hundred thousand empty files, a no-provisioner StorageClass with
`volumeBindingMode: WaitForFirstConsumer`, and a `local` PersistentVolume with `nodeAffinity`
pinning it to the single node, following the shape at `volumes.md:668-705`. Step 2 takes a few
minutes and step 4 may take several; that wait is the measurement, so do not shorten the file count
without expecting the difference to shrink with it.

**Do**

1. Untaint the node, then read the two fields out of the running API server rather than out of the
   reference pages, and ask the cluster which of the three gates it still knows about.

   ```bash
   CP=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl taint node $CP node-role.kubernetes.io/control-plane- || true
   kubectl version -o json | python3 -c 'import json,sys; print(json.load(sys.stdin)["serverVersion"]["gitVersion"])'
   kubectl explain pod.spec.securityContext.fsGroupChangePolicy
   kubectl explain csidriver.spec.fsGroupPolicy
   kubectl get --raw /metrics | grep -o 'kubernetes_feature_enabled{name="[A-Za-z]*FSGroup[A-Za-z]*"' | sort -u || echo "no fsGroup gate is reported"
   ```

2. Build the volume the post is really about: a directory of three hundred thousand empty files,
   owned by root, with a second empty directory beside it for later. This step is slow; time it,
   because the number is the baseline for everything that follows.

   ```bash
   sudo mkdir -p /mnt/bw-fsg/data /mnt/bw-fsg/hostpath
   time sudo sh -c 'cd /mnt/bw-fsg/data && for i in $(seq 1 300); do mkdir -p d$i && (cd d$i && touch $(seq -f "f%g" 1 1000)); done'
   sudo find /mnt/bw-fsg/data | wc -l
   stat -c '%U:%G %a' /mnt/bw-fsg/data /mnt/bw-fsg/data/d1/f1
   ```

3. Put a `local` PersistentVolume in front of it, following `volumes.md:668-705`: a no-provisioner
   StorageClass with delayed binding, node affinity onto the one node, and a claim in a namespace of
   its own.

   ```bash
   kubectl create namespace bw-fsg

   kubectl apply -f - <<EOF
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: bw-fsg-local
   provisioner: kubernetes.io/no-provisioner
   volumeBindingMode: WaitForFirstConsumer
   ---
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: bw-fsg-pv
   spec:
     capacity:
       storage: 2Gi
     volumeMode: Filesystem
     accessModes:
     - ReadWriteOnce
     persistentVolumeReclaimPolicy: Retain
     storageClassName: bw-fsg-local
     local:
       path: /mnt/bw-fsg/data
     nodeAffinity:
       required:
         nodeSelectorTerms:
         - matchExpressions:
           - key: kubernetes.io/hostname
             operator: In
             values:
             - $CP
   ---
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: bw-fsg-pvc
     namespace: bw-fsg
   spec:
     accessModes:
     - ReadWriteOnce
     storageClassName: bw-fsg-local
     resources:
       requests:
         storage: 2Gi
   EOF

   kubectl -n bw-fsg get pvc bw-fsg-pvc
   ```

4. Mount it from a Pod that sets `fsGroup` and nothing else, and time how long the Pod spends
   between `apply` and `Ready`. This is the default the post complains about.

   ```bash
   cat > /tmp/bw-pod.yaml <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: bw-fsg-pod
     namespace: bw-fsg
   spec:
     securityContext:
       runAsUser: 1000
       runAsGroup: 3000
       fsGroup: 2000
     containers:
     - name: c
       image: busybox
       command: ["sleep", "3600"]
       volumeMounts:
       - name: v
         mountPath: /data
     volumes:
     - name: v
       persistentVolumeClaim:
         claimName: bw-fsg-pvc
   EOF

   T0=$(date +%s); kubectl apply -f /tmp/bw-pod.yaml
   kubectl -n bw-fsg wait --for=condition=Ready pod/bw-fsg-pod --timeout=1800s
   echo "default policy, first mount: $(( $(date +%s) - T0 ))s"
   kubectl -n bw-fsg exec bw-fsg-pod -- stat -c '%u:%g %a %n' /data /data/d1/f1
   ```

5. Delete the Pod and apply exactly the same manifest again. The ownership on disk now already
   matches what the Pod asks for, which is the case the post says is not detected.

   ```bash
   kubectl -n bw-fsg delete pod bw-fsg-pod --wait=true
   T0=$(date +%s); kubectl apply -f /tmp/bw-pod.yaml
   kubectl -n bw-fsg wait --for=condition=Ready pod/bw-fsg-pod --timeout=1800s
   echo "default policy, second mount: $(( $(date +%s) - T0 ))s"
   ```

6. Add the post's field to the same Pod and mount a third time. Nothing else changes.

   ```bash
   kubectl -n bw-fsg delete pod bw-fsg-pod --wait=true
   sed 's/    fsGroup: 2000/    fsGroup: 2000\n    fsGroupChangePolicy: "OnRootMismatch"/' /tmp/bw-pod.yaml > /tmp/bw-pod-onroot.yaml
   grep -A1 'fsGroup: 2000' /tmp/bw-pod-onroot.yaml
   T0=$(date +%s); kubectl apply -f /tmp/bw-pod-onroot.yaml
   kubectl -n bw-fsg wait --for=condition=Ready pod/bw-fsg-pod --timeout=1800s
   echo "OnRootMismatch, root already matches: $(( $(date +%s) - T0 ))s"
   ```

7. Now break only the root directory's group and mount again with the same policy. This is the
   mismatch the value is named after, and it is also the check on the post's claim that the
   top-level directory is changed last.

   ```bash
   kubectl -n bw-fsg delete pod bw-fsg-pod --wait=true
   sudo chgrp 0 /mnt/bw-fsg/data
   stat -c '%U:%G %a' /mnt/bw-fsg/data /mnt/bw-fsg/data/d1/f1
   T0=$(date +%s); kubectl apply -f /tmp/bw-pod-onroot.yaml
   kubectl -n bw-fsg wait --for=condition=Ready pod/bw-fsg-pod --timeout=1800s
   echo "OnRootMismatch, root mismatched: $(( $(date +%s) - T0 ))s"
   stat -c '%U:%G %a' /mnt/bw-fsg/data
   kubectl -n bw-fsg delete pod bw-fsg-pod --wait=true
   ```

8. Test two of the three volume types the pin says the policy has no effect on, plus one it says
   does not support ownership management at all, in a single Pod that sets the policy. Two of the
   three are described elsewhere in the same generated file as supporting ownership management,
   which is the disagreement this step resolves.

   ```bash
   kubectl -n bw-fsg create configmap bw-fsg-cm --from-literal=k=v

   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: bw-fsg-eph
     namespace: bw-fsg
   spec:
     securityContext:
       runAsUser: 1000
       runAsGroup: 3000
       fsGroup: 2000
       fsGroupChangePolicy: "OnRootMismatch"
     containers:
     - name: c
       image: busybox
       command: ["sleep", "3600"]
       volumeMounts:
       - name: ed
         mountPath: /ed
       - name: hp
         mountPath: /hp
       - name: cm
         mountPath: /cm
     volumes:
     - name: ed
       emptyDir: {}
     - name: hp
       hostPath:
         path: /mnt/bw-fsg/hostpath
     - name: cm
       configMap:
         name: bw-fsg-cm
   EOF

   kubectl -n bw-fsg wait --for=condition=Ready pod/bw-fsg-eph --timeout=300s
   kubectl -n bw-fsg exec bw-fsg-eph -- stat -c '%u:%g %a %n' /ed /hp /cm /cm/k
   sudo stat -c '%U:%G %a' /mnt/bw-fsg/hostpath
   ```

9. Ask the API server what the second half of the post shipped. The pin documents the field in one
   row of one page and lists none of its values, so the validation error is the enumeration. Then
   find out whether the field is mutable, which `csi-driver-v1.md:73` says changed at 1.29.

   ```bash
   cat > /tmp/bw-drv.yaml <<'EOF'
   apiVersion: storage.k8s.io/v1
   kind: CSIDriver
   metadata:
     name: bw-fsg.example.com
   spec:
     attachRequired: false
     podInfoOnMount: false
     fsGroupPolicy: PLACEHOLDER
   EOF

   for VAL in ReadWriteOnceWithFSType File None Nonesuch; do
     echo "--- $VAL"
     sed "s/PLACEHOLDER/$VAL/" /tmp/bw-drv.yaml | kubectl apply --dry-run=server -f - 2>&1 | tail -2
   done

   sed 's/PLACEHOLDER/File/' /tmp/bw-drv.yaml | kubectl apply -f -
   kubectl patch csidriver bw-fsg.example.com --type=merge -p '{"spec":{"fsGroupPolicy":"None"}}' 2>&1 | tail -2
   kubectl get csidriver bw-fsg.example.com -o jsonpath='{.spec.fsGroupPolicy}'; echo
   ```

10. One last claim, from a page neither half of the post touches: `pod-v1.md:149` lists
    `spec.securityContext.fsGroupChangePolicy` among the fields that must be unset when the Pod
    declares a Windows OS. Send the API server a Pod that does both.

    ```bash
    kubectl apply --dry-run=server -f - <<'EOF' 2>&1 | tail -3
    apiVersion: v1
    kind: Pod
    metadata:
      name: bw-fsg-win
      namespace: bw-fsg
    spec:
      os:
        name: windows
      securityContext:
        fsGroup: 2000
        fsGroupChangePolicy: "OnRootMismatch"
      containers:
      - name: c
        image: busybox
    EOF
    ```

**Expect**

Step 1 should report a v1.37 server. The description `kubectl explain` prints for
`fsGroupChangePolicy` is the same text the generated reference carries at `pod-v1.md:2274`, both
being rendered from the same schema, so it should name two valid values and state that `Always` is
the default. The description for `csidriver.spec.fsGroupPolicy` should end with the instruction to
refer to the specific values for additional details, and should then stop without listing any. The
metric grep should print the fallback line: all three gates are `removed: true` and a removed gate
is not in the feature set, so the cluster has no opinion left to report.

Step 2 should report 300301 entries — three hundred directories, three hundred thousand files and
the root — owned by `root:root`. Note how long the creation itself took; the chown in step 4 walks
the same tree.

Step 3 should show the claim `Pending`, not `Bound`. That is the `WaitForFirstConsumer` binding mode
doing its job: a `local` volume cannot be bound until a Pod exists to say where it wants to run. If
the claim binds immediately, the StorageClass did not apply and the node affinity in the
PersistentVolume is doing nothing.

Step 4 is the measurement the post exists for, and it has two outcomes. If a `local` volume supports
`fsGroup` ownership management, the Pod sits in `ContainerCreating` while the kubelet walks three
hundred thousand inodes, and the elapsed number is tens of seconds or minutes rather than the two or
three a Pod normally takes; the `stat` inside the container then reports group `2000` on both
`/data` and `/data/d1/f1`, and the mode on `/data` carries the setgid bit. If instead the Pod is
ready almost at once and both paths still report group `0`, then `local` is one of the types the
cluster does not walk, the pin never said so, and steps 5 to 7 will all be equally fast — which is
itself the finding, because the post's whole first half assumes otherwise.

Step 5 should take about as long as step 4, not less. Every file already has group `2000`; the
post's complaint is precisely that the default policy does not check. A second mount that is
noticeably faster than the first means the page cache is helping, not that the walk was skipped —
run it a third time before concluding anything.

Step 6 should be fast: the root of the volume already carries group `2000` from step 4, so
`OnRootMismatch` finds a match and skips the tree. Against steps 4 and 5 this is the post's claim
demonstrated in three numbers, and the difference should be at least an order of magnitude.

Step 7 should be slow again, and should end with `/mnt/bw-fsg/data` back in group `2000`. One
`chgrp` on one directory is enough to make the kubelet redo three hundred thousand of them, which is
the cost of the guarantee the post states — the top-level directory is changed last, so an
interrupted walk leaves a mismatched root and the next mount repeats the work rather than trusting
it. The shortcut is safe because the root is the last thing to change, and this step is what that
sentence buys.

Step 8 has three results and they do not all agree with the same page. `/hp` should still be `0:0`:
`persistent-volume-v1.md:622` says `hostPath` does not support ownership management, and the host
directory should be unchanged when you stat it from outside. `/ed` and `/cm` should both come back
with group `2000` even though `pod-v1.md:2274` says the policy has no effect on `emptyDir` and
`configMap`. If they do, both of the pin's statements hold at once and the step is what makes the
reconciliation visible: `fsGroup` is applied to these volumes, so they do support ownership
management as `:1123` and `:672` claim, and the policy has no effect on them because there is
nothing on a freshly created tmpfs mount for a shortcut to skip. If `/ed` instead comes back `0:0`,
the sentence at `:1123` is the one that is wrong. Either way the pin states both halves and never
joins them.

Step 9 should accept `ReadWriteOnceWithFSType`, `File` and `None`, and reject `Nonesuch` with a
message that names the three values it will take. That message is the only enumeration of this API
you can obtain without leaving the cluster, and it is the thing the post supplies and the pin does
not. The patch should then succeed and the final line should print `None`: `csi-driver-v1.md:73`
says the field was immutable before 1.29 and is mutable now, and a v1.37 server is on the far side
of that change.

Step 10 should be refused, and the message should name both `spec.securityContext.fsGroup` and
`spec.securityContext.fsGroupChangePolicy` as fields that may not be set when `spec.os.name` is
`windows`. `pod-v1.md:149` lists both among a long run of twenty-five fields restricted on Windows,
and `concepts/windows/intro.md:100` repeats the restriction in prose. This is the one place in the
exercise where the pin and the API server say the same thing in the same words.

**Read on**

1. `tasks/configure-pod-container/security-context.md`, sections `:359-396` and `:398-410`, read
   back to back and in that order. The first is the post; the second is what happened to the post.
   Then read the `## Discussion` bullet at `:833-836`, which is the only place in the pin that
   offers to say what supporting ownership management means — and says it by linking to a design
   document on `git.k8s.io`, off the site. Then read the page's reviewers, `erictune`, `mikedanese`
   and `thockin`, none of whom wrote the post whose fence the page carries.

2. `reference/kubernetes-api/core/persistent-volume-v1.md`, for the sentence that decides everything
   in *Do*. Twelve of the twenty-two volume sources on that page carry a claim about ownership
   management: `:261`, `:409`, `:446`, `:475`, `:541`, `:564`, `:593`, `:622`, `:643`, `:721`,
   `:792` and `:829`. Read all twelve, then read `LocalVolumeSource` at `:698-716`, which has two
   fields and no such sentence, and work out whether the silence is an omission or a statement.

3. `reference/kubernetes-api/core/pod-v1.md`, for the same generated file arguing with itself.
   `:2274` says the policy has no effect on `secret`, `configMap` and `emptyDir`. Ten other places
   in the file say whether a volume type supports ownership management — `:496`, `:533`, `:672`,
   `:1102`, `:1123`, `:1463`, `:1490`, `:1607`, `:2417` and `:2759` — and three of those name the
   same three types as supporting it. Read the ten, then read `:149`, then decide whether the two
   families of sentence are about one thing or two.

4. The three gate files transcribed in *The ladder*, and then the cohort around them. Six gates in
   the pin have a `stable` row beginning at 1.23 and five are already on this year's shelf: the two
   here, `GenericEphemeralVolume` in the exercise on capacity tracking in this directory,
   `IPv6DualStack` in [the EndpointSlices
   exercise](06-scaling-kubernetes-networking-with-endpointslices.md), and
   `IngressClassNamespacedParams` in [the Ingress API
   exercise](02-improvements-to-the-ingress-api-in-kubernetes-1-18.md). The sixth,
   `TTLAfterFinished`, is named nowhere in the walk. Read its gate file and decide whether 2020 had
   nothing to say about it or whether the walk simply has not reached the post that did.

5. Unanswerable from the pin: what a driver author is supposed to choose. The pin documents
   `fsGroupPolicy` in one row of one generated page and lists none of its values, so it cannot tell
   you what `ReadWriteOnceWithFSType`, `File` and `None` mean, which one a new driver should
   declare, or whether the `more planned for future releases` the post promises ever arrived — step
   9 recovers the spellings from the API server and nothing recovers the meanings. It cannot tell
   you whether a `local` volume supports `fsGroup`, because `LocalVolumeSource` does not say and no
   concept page fills the gap; step 4 answers that for one cluster. And it cannot tell you how a
   cluster operator is meant to discover that a driver has taken delegation, because
   `security-context.md:402-410` describes the consequence and names no command that reports the
   capability.

**Teardown**

Remove the namespace, the cluster-scoped objects, the temporary manifests and the file tree.
Deleting three hundred thousand files takes about as long as creating them did. Re-taint the control
plane if you intend to keep the guest for another exercise; leave it untainted if the next thing you
do is destroy it.

```bash
kubectl delete namespace bw-fsg --ignore-not-found
kubectl delete csidriver bw-fsg.example.com --ignore-not-found
kubectl delete pv bw-fsg-pv --ignore-not-found
kubectl delete storageclass bw-fsg-local --ignore-not-found
rm -f /tmp/bw-pod.yaml /tmp/bw-pod-onroot.yaml /tmp/bw-drv.yaml
time sudo rm -rf /mnt/bw-fsg
CP=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
kubectl taint node $CP node-role.kubernetes.io/control-plane=:NoSchedule || true
```

Then follow [the teardown procedure](../../strands/lab-topologies.md#teardown) to destroy the guest.
