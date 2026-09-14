<a id="volume-expansion-ga"></a>

# One feature announced as one thing was three gates with three different beta lengths, all deleted two releases after the GA this post celebrates, and on a cluster with no CSI driver what is left is a controller that runs, a field that validates, and a claim whose capacity never moves

**Post** — [Kubernetes 1.24: Volume Expansion Now A Stable
Feature](https://kubernetes.io/blog/2022/05/05/volume-expansion-ga/), 2022-05-05, Kubernetes v1.24.
103 lines, 5,097 bytes, one author and one vendor — well under 2022's median post of 7,935 bytes,
and the first of the year's thirteen walked posts.

**As written** — the post opens with a version history and a promise, and the history is one
sentence long:

> Volume expansion was introduced as a alpha feature in Kubernetes 1.8 and it went beta in 1.11
> and with Kubernetes 1.24 we are excited to announce general availability(GA) of volume
> expansion.

Then the instruction, at `:19-37`: edit the `spec` of a PersistentVolumeClaim, ask for more storage,
and watch. The post is specific about where to watch:

> Once you've changed the requested size, watch the `status.conditions` field of the PVC to see if
> the resize has completed. [...] When Kubernetes starts expanding the volume - it will add
> `Resizing` condition to the PVC, which will be removed once expansion completes.

`:46-70` is the qualifier. Not everything is expandable: in-tree `hostPath` volumes are *not
expandable at all*, a CSI driver must carry the `EXPAND_VOLUME` capability, and the StorageClass
must opt in. The post prints one StorageClass to show what opting in looks like:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp2-default
provisioner: kubernetes.io/aws-ebs
parameters:
  secretNamespace: ""
  secretName: ""
allowVolumeExpansion: true
```

`:72-90` separates online from offline expansion and closes the year's best typo — *His behaviour
has been changed* — and `:92-103` is a two-item forecast: recovery from a failed expansion,
introduced in v1.23, and a proposal to expand every claim under a StatefulSet by editing the
StatefulSet.

**As it runs now** — the instruction still works, and on this lab it does nothing at all, for a
reason the post states itself and does not connect to its own example.

**One feature, three gates.** The post says *alpha in 1.8, beta in 1.11, GA in 1.24*, and that is
the history of `ExpandPersistentVolumes` — one of three gates whose graduation the post is
announcing. The online-expansion section is `ExpandInUsePersistentVolumes`, alpha at 1.11 and beta
at 1.15; the storage-driver section is `ExpandCSIVolumes`, alpha at 1.14 and beta at 1.16. Three
features that started six releases apart were switched on together at 1.24 and described as one, and
the post names none of the three. The ladder below is what the sentence flattens.

**All three are gone, and the population says that is rare in this exact way.** Each of the three
gate files carries `removed: true` and a `stable` row ending at `1.26`, so all three stopped
existing at v1.27. Of the 487 gate files at the pin, 230 are removed, and **182 of those reached
stable first** — removal after GA is the normal end of a gate's life, not an unusual one. What is
unusual is the cohort: exactly **five** gates carry a stable range of `1.24` through `1.26`, and
three of the five are these. The other two are `CSIMigrationAzureDisk` and
`ControllerManagerLeaderMigration`.

**The controller outlived its switches.** `kube-controller-manager.md:437` lists
`persistentvolume-expander-controller` among the controllers enabled by default, with no gate
anywhere that could turn it off. It is running on this cluster right now with nothing to do, which
is the sharpest available statement of what GA meant here.

**The list of expandable volume types has emptied of everything you can build by hand.**
`persistent-volumes.md:381-387` says expansion works for `csi`, `flexVolume` (deprecated) and
`portworxVolume` (deprecated) — three entries, two of them marked deprecated in the same list. The
supported-plugin list 120 lines later at `:501-509` offers six in-tree types you can still create —
`csi`, `fc`, `hostPath`, `iscsi`, `local`, `nfs` — and **not one of the five non-CSI entries appears
in the expandable list**. The post's own sentence, that in-tree `hostPath` is not expandable at all,
is still exactly right, and it is now the general case rather than the exception it was written as.

**The StorageClass example names a provisioner the documentation no longer contains.**
`kubernetes.io/aws-ebs` occurs **zero** times under `content/en/docs` at the pin and six times in
the blog archive. The volume *type* survives — `awsElasticBlockStore` is still in the deprecated
plugin list at `:515-516`, marked *migration on by default starting v1.23* — but the in-tree
provisioner string the post's example turns on is not written down anywhere a reader could check it.
The parameters are stranger still: the pin's equivalent example at `:391-403` carries `resturl`,
`restuser`, `secretNamespace` and `secretName` under a deliberately fictional
`vendor-name.example/magicstorage`, and the post's version keeps two of those four keys under a real
provisioner name. Those keys belong to GlusterFS, which the pin records as **not available starting
v1.26**.

**`EXPAND_VOLUME` is not a word the documentation knows.** The capability the post tells you to look
for in your driver occurs zero times under `content/en/docs` and twice in the whole archive — here,
and in the 2021 post that [the access-mode
exercise](../2021/07-read-write-once-pod-access-mode-alpha.md) walks, which found the same silence
for `SINGLE_NODE_MULTI_WRITER`. The CSI specification's vocabulary reaches Kubernetes users through
blog posts or not at all; two posts a year apart are the second and third data points for that.

**And the pin disagrees with itself about where to watch.** This is a statement about the
documentation rather than about the post, so it belongs here and not in the next section.
`persistent-volumes.md` never mentions a `Resizing` condition; its recovery section at `:488` tells
you to watch `.status.allocatedResourceStatuses`. The generated API reference still carries the
post's advice: `persistent-volume-claim-v1.md:138` says *"If underlying persistent volume is being
resized then the Condition will be set to 'Resizing'"*, and `:229` repeats it for the condition's
`reason`. Both are true; one is five years older than the other, and the hand-written page has moved
on without the generated one following. The controller has the same problem in the other direction:
`rbac.md:828` calls it `system:controller:expand-controller` while `kube-controller-manager.md:437`
calls it `persistentvolume-expander-controller`, two files in the same reference directory naming
one component twice.

**What this exercise does not cover, and where it lives.** The two-phase mechanics — which phase
sets `FileSystemResizePending`, which clears it, what must be true of the Pod before the node phase
runs, and the recovery drill that reduces a failed request — are [an existing storage
lab](../../labs/08/09-expansion-two-phase.md), run on a `pair` topology with a working CSI driver
behind it. That lab is the happy path and its interesting failure. This exercise is deliberately the
opposite: one node, no driver, and every step below is about what the API does when the thing that
would carry out the resize is not there. The two do not overlap, and the lab is the one to run if
you want to see a volume actually get bigger.

**The diff, and why** — four of the seven cases.

**Retired by being agreed with: the gates.** The post asks you to celebrate that expansion is on by
default and no longer needs a switch. The project agreed so completely that two releases later it
deleted all three switches, and a reader who goes looking for `ExpandPersistentVolumes` today finds
a file whose frontmatter says `removed: true` and whose `_build` block says `render: false` — a page
that exists only so the ladder is not lost. The forecast was honoured, and the way you can tell is
that there is nothing left to point at.

**Broke: the StorageClass example.** A reader who copies `:60-70` gets an object the API server will
accept and no provisioner will ever answer, under a name the documentation has erased. This is the
smallest kind of break and the most common in the storage posts: the mechanism is fine, the example
is addressed to a world that has been migrated out from under it. Step 3 builds the class the post
should have printed for a cluster with no cloud behind it.

**Still right: the instruction, and the one negative claim that makes this lab silent.** Edit the
claim, ask for more, the control plane resizes the volume underneath and never creates a new one —
all of that is `persistent-volumes.md:405-407` word for word. And the post's aside that in-tree
`hostPath` is not expandable at all is still true, which is why the interesting half of this
exercise is what happens when the instruction is followed on a cluster that cannot carry it out. The
post never connects its own caveat to its own example; the reader who notices is the one who learns
what GA bought.

**A plan the project abandoned: expansion through StatefulSets.** `:100-103` says the contributor
community *is also discussing the potential for StatefulSet-driven storage expansion*, and links an
enhancement proposal. Four years and thirteen releases later, `statefulset.md` contains **zero**
occurrences of the string `expan` — not the feature, not a forecast, not a note that it was dropped.
The link in `:103` is the only occurrence of that enhancement's URL in the entire content tree. The
claim template is still the only way to size a StatefulSet's storage, and resizing one still means
editing every claim by hand.

Not the seventh case, and the near miss is worth recording. The pin does cite this post —
`csi-nodeexpandsecret.md:41` says *"Please read"* and links it — but that citation is in another
blog post, and the seventh case requires a page under `content/en/docs`. `EXPAND_VOLUME` passes the
identifier test and the post fails the first one, so this is a post the archive leans on, not a post
the documentation leans on.

**The ladder**

Three gates, transcribed from their `stages:` lists parsed as YAML. Reading them side by side is the
point: the post's one-sentence history is the first row of the first table.

```
ExpandPersistentVolumes       alpha  false  1.8  - 1.10
                              beta   true   1.11 - 1.23
                              stable true   1.24 - 1.26   removed

ExpandInUsePersistentVolumes  alpha  false  1.11 - 1.14
                              beta   true   1.15 - 1.23
                              stable true   1.24 - 1.26   removed

ExpandCSIVolumes              alpha  false  1.14 - 1.15
                              beta   true   1.16 - 1.23
                              stable true   1.24 - 1.26   removed
```

Thirteen releases of beta on the first gate is long and not remarkable: of 376 gates with a beta
stage, six sat in beta for exactly thirteen releases and fourteen sat there longer, the record being
`AppArmor` at twenty-seven. What the three tables show that no prose summary can is that the three
lines *converge* — three different alphas, three different betas, one shared stable range, one
shared deletion — which is the shape of a feature assembled from parts and shipped as a whole.

A fourth gate belongs to the post's forecast rather than its subject.
`RecoverVolumeExpansionFailure`, the v1.23 alpha `:96-98` points at, is **stable and `locked: true`
since 1.34** and is not laddered here; it is the one thing in *Next steps* that arrived. Step 6
tests the behaviour it locked in, because that behaviour is pure API validation and needs no driver.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`, 4096MB, 4
vCPU, 25G, brought up with [the provisioning sequence](../../strands/lab-topologies.md#provision).
Two static directories on the node, two StorageClasses that provision nothing, and one edit to a
control-plane manifest. A second node would add nothing and would take something away: `hostPath` is
single-node by definition, `persistent-volumes.md:503-505` says so in the plugin list itself, and
the whole argument here depends on the volume being one the cluster cannot resize.

**Do**

1. Ask the cluster about all three gates before reading anything about them. The metric is the only
   machine-readable answer, and here the informative result is the empty one:

   ```sh
   kubectl version -o json | python3 -c 'import json,sys
   print("server:", json.load(sys.stdin)["serverVersion"]["gitVersion"])'
   for G in ExpandPersistentVolumes ExpandInUsePersistentVolumes ExpandCSIVolumes \
            RecoverVolumeExpansionFailure; do
     printf '%-32s apiserver=%s\n' "$G" \
       "$(kubectl get --raw /metrics | grep -c "kubernetes_feature_enabled.*\"$G\"" || true)"
   done
   kubectl get --raw /metrics | grep -c 'kubernetes_feature_enabled'
   ```

2. Try to turn one of them back on, in the component that would do the resizing. The API server is
   left alone on purpose, so the cluster stays reachable whatever happens; the static pod restarts
   the moment the file is written:

   ```sh
   sudo cp /etc/kubernetes/manifests/kube-controller-manager.yaml /root/kcm.yaml.bak
   sudo sed -i '/- kube-controller-manager/a\    - --feature-gates=ExpandPersistentVolumes=true' \
     /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 25
   kubectl -n kube-system get pods -l component=kube-controller-manager
   sudo crictl logs "$(sudo crictl ps -a -q --name kube-controller-manager | head -1)" 2>&1 | tail -6
   sudo cp /root/kcm.yaml.bak /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 25
   kubectl -n kube-system get pods -l component=kube-controller-manager
   ```

3. Build the ground the post should have printed. Two StorageClasses that provision nothing,
   differing in one field; two 1Gi `hostPath` volumes; two claims and two Pods, so that the same
   edit can be made against a class that opts in and a class that does not:

   ```sh
   for i in 0 1; do sudo mkdir -p /srv/bw-exp/$i; done
   kubectl apply -f - <<'YAML'
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata: { name: bw-noexp }
   provisioner: kubernetes.io/no-provisioner
   ---
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata: { name: bw-exp }
   provisioner: kubernetes.io/no-provisioner
   allowVolumeExpansion: true
   YAML
   for i in 0 1; do
     SC=$([ $i = 0 ] && echo bw-noexp || echo bw-exp)
     kubectl apply -f - <<YAML
   apiVersion: v1
   kind: PersistentVolume
   metadata: { name: bw-exp-$i }
   spec:
     capacity: { storage: 1Gi }
     accessModes: ["ReadWriteOnce"]
     persistentVolumeReclaimPolicy: Retain
     storageClassName: $SC
     hostPath: { path: /srv/bw-exp/$i }
   ---
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata: { name: bw-exp-$i }
   spec:
     accessModes: ["ReadWriteOnce"]
     storageClassName: $SC
     volumeName: bw-exp-$i
     resources: { requests: { storage: 1Gi } }
   ---
   apiVersion: v1
   kind: Pod
   metadata: { name: bw-exp-$i }
   spec:
     containers:
       - name: c
         image: registry.k8s.io/e2e-test-images/agnhost:2.53
         args: ["netexec", "--http-port=8080"]
         volumeMounts: [{ name: d, mountPath: /data }]
     volumes:
       - name: d
         persistentVolumeClaim: { claimName: bw-exp-$i }
   YAML
   done
   kubectl wait --for=condition=Ready pod/bw-exp-0 pod/bw-exp-1 --timeout=180s
   kubectl get sc bw-noexp bw-exp -o custom-columns=NAME:.metadata.name,EXPAND:.allowVolumeExpansion
   kubectl get pvc
   ```

4. Follow the post's instruction against the class that never opted in. This is the one failure mode
   the post mentions in passing and never shows:

   ```sh
   kubectl patch pvc bw-exp-0 --type=merge \
     -p '{"spec":{"resources":{"requests":{"storage":"2Gi"}}}}' 2>&1 | tail -3
   kubectl get pvc bw-exp-0 -o jsonpath='{.spec.resources.requests.storage}{"\t"}{.status.capacity.storage}'; echo
   ```

5. Now follow it against the class that did opt in, and then wait. The polling loop is the step: the
   request is accepted, and the interesting measurement is how long nothing happens for:

   ```sh
   kubectl patch pvc bw-exp-1 --type=merge \
     -p '{"spec":{"resources":{"requests":{"storage":"2Gi"}}}}'
   for i in $(seq 1 10); do
     kubectl get pvc bw-exp-1 -o jsonpath='{.spec.resources.requests.storage}{"\t"}{.status.capacity.storage}{"\t"}{.status.conditions[*].type}{"\t"}{.status.allocatedResourceStatuses}{"\n"}'
     sleep 6
   done
   kubectl describe pvc bw-exp-1 | tail -12
   kubectl get events --field-selector involvedObject.name=bw-exp-1 -o wide | tail -5
   kubectl -n kube-system logs -l component=kube-controller-manager --tail=200 2>/dev/null \
     | grep -i 'resiz\|expand' | tail -5 || echo "no resize lines"
   ```

6. Walk the validation boundary, which is the only part of this feature that works without a driver.
   Two edits that should be refused and one that the gate stable since v1.34 was written to allow —
   and the third is the one to record, because it is the behaviour the post's *Next steps* forecast:

   ```sh
   kubectl patch pvc bw-exp-1 --type=merge \
     -p '{"spec":{"resources":{"requests":{"storage":"500Mi"}}}}' 2>&1 | tail -3
   kubectl patch pvc bw-exp-1 --type=merge \
     -p '{"spec":{"resources":{"requests":{"storage":"1Gi"}}}}' 2>&1 | tail -3
   kubectl patch pvc bw-exp-1 --type=merge \
     -p '{"spec":{"resources":{"requests":{"storage":"1500Mi"}}}}' 2>&1 | tail -3
   kubectl get pvc bw-exp-1 -o jsonpath='{.spec.resources.requests.storage}{"\t"}{.status.capacity.storage}'; echo
   ```

7. Reproduce the warning the concept page prints and the post does not. Grow the PersistentVolume
   first, then make the claim match it, and watch the control plane conclude that its work is
   already done:

   ```sh
   kubectl patch pv bw-exp-1 --type=merge -p '{"spec":{"capacity":{"storage":"2Gi"}}}'
   kubectl get pv bw-exp-1 -o jsonpath='{.spec.capacity.storage}'; echo
   kubectl patch pvc bw-exp-1 --type=merge \
     -p '{"spec":{"resources":{"requests":{"storage":"2Gi"}}}}'
   sleep 20
   kubectl get pvc bw-exp-1 -o jsonpath='{.spec.resources.requests.storage}{"\t"}{.status.capacity.storage}{"\t"}{.status.conditions[*].type}'; echo
   sudo df -h /srv/bw-exp/1 | tail -1
   kubectl exec bw-exp-1 -- df -h /data | tail -1
   ```

8. Find the controller that has been idle through all of this, and find both of its names. One is in
   the binary's own flag documentation and one is in the RBAC that ships with the cluster:

   ```sh
   kubectl -n kube-system get pod -l component=kube-controller-manager \
     -o jsonpath='{.items[0].spec.containers[0].command}' | tr ',' '\n' | grep -i 'controller\|feature'
   kubectl get clusterrole system:controller:expand-controller \
     -o jsonpath='{range .rules[*]}{.apiGroups}{" "}{.resources}{" "}{.verbs}{"\n"}{end}'
   kubectl get clusterrolebinding system:controller:expand-controller \
     -o jsonpath='{.subjects}'; echo
   kubectl get clusterrole -o name | grep -c 'expander' || echo "0 roles named expander"
   ```

9. Census the vocabulary in the pinned tree. Four names the post uses, one of which the
   documentation has never used, one it has erased, and one that survives only in generated output:

   ```sh
   cd /path/to/kubernetes/website
   for S in EXPAND_VOLUME kubernetes.io/aws-ebs allowVolumeExpansion allocatedResourceStatuses; do
     printf '%-28s docs=%s blog=%s\n' "$S" \
       "$(grep -rl "$S" content/en/docs --include='*.md' | wc -l | tr -d ' ')" \
       "$(grep -rl "$S" content/en/blog --include='*.md' | wc -l | tr -d ' ')"
   done
   grep -rn "'Resizing'" content/en/docs/reference/kubernetes-api/core/persistent-volume-claim-v1.md
   grep -c 'Resizing' content/en/docs/concepts/storage/persistent-volumes.md || echo 0
   grep -c -i 'expan' content/en/docs/concepts/workloads/controllers/statefulset.md || echo 0
   sed -n '381,387p;501,509p' content/en/docs/concepts/storage/persistent-volumes.md
   ```

10. Offline, in the pinned checkout, measure the two things the ladder turns on: how many removed
    gates reached stable before they went, and how crowded the 1.24-to-1.26 stable range is:

    ```sh
    cd /path/to/kubernetes/website
    python3 - <<'PY'
    import os, yaml
    G = "content/en/docs/reference/command-line-tools-reference/feature-gates"
    gates = {}
    for fn in sorted(os.listdir(G)):
        if not fn.endswith(".md") or fn == "index.md": continue
        gates[fn[:-3]] = yaml.safe_load(open(os.path.join(G, fn)).read().split("---")[1])
    print("gate files:", len(gates))
    rm = {k: v for k, v in gates.items() if v.get("removed")}
    print("removed:", len(rm))
    def row(v, want):
        for s in v.get("stages") or []:
            if str(s.get("stage")).strip() == want: return s
        return None
    reached = {k: row(v, "stable") for k, v in rm.items()}
    reached = {k: s for k, s in reached.items() if s}
    print("removed after reaching stable:", len(reached))
    print("removed without ever reaching stable:", len(rm) - len(reached))
    cohort = [k for k, s in reached.items()
              if str(s.get("fromVersion")) == "1.24" and str(s.get("toVersion")) == "1.26"]
    print("stable 1.24-1.26 exactly:", sorted(cohort))
    spans = []
    for k, v in gates.items():
        s = row(v, "beta")
        if not s: continue
        a = int(str(s["fromVersion"]).split(".")[1])
        b = int(str(s["toVersion"]).split(".")[1]) if s.get("toVersion") else 37
        spans.append((b - a + 1, k))
    spans.sort(reverse=True)
    print("gates with a beta stage:", len(spans))
    print("beta longer than 13:", len([x for x in spans if x[0] > 13]),
          "| exactly 13:", len([x for x in spans if x[0] == 13]))
    print("longest:", spans[0])
    PY
    ```

**Expect**

Step 1 finds nothing for the three expansion gates and a number in the hundreds for the metric as a
whole. That is the answer: `kubernetes_feature_enabled` reports the gates the binary knows about,
and a binary compiled after v1.26 does not know these three exist. `RecoverVolumeExpansionFailure`
is the control — it should be present, at value 1, with a `stage` label of `STABLE`, which is what a
gate that is still a gate looks like.

Step 2 should stop the controller manager from starting. A removed gate is not an unset gate: the
flag parser rejects a name it has no entry for, and the container crash-loops with a line naming the
unrecognized gate. Read it before restoring, because it is the difference between *off* and *gone*
and the cluster only says it out loud here. The restore is a file copy and the component is back
inside half a minute; do not leave the flag in place.

Step 3 gives you two bound claims, two running Pods and two classes differing in one boolean. Both
PVCs report `1Gi` for both the request and `status.capacity`, because a statically created volume
binds at the size it was declared with.

Step 4 is refused, and the message is the point: the API server names the class and the field, so
the reader learns that `allowVolumeExpansion` is enforced at admission and not by the controller.
The claim's request is unchanged afterwards — nothing was half-applied.

Step 5 is accepted and then silent. `spec` reads `2Gi`, `status.capacity` stays `1Gi`, and
`status.conditions` and `status.allocatedResourceStatuses` stay empty for the whole minute the loop
runs. There is no error, no event and no controller log line, because there is no plugin that claims
this volume: `hostPath` is not in the expandable list at `persistent-volumes.md:381-387` and there
is no CSI driver installed. This is what the post's GA looks like on a cluster the post was not
written for — a request that is valid, accepted, recorded, and never acted on. A reader who trusted
`status.conditions` would wait forever for a condition that is never set.

Step 6 is three edits and the third is the finding. `500Mi` is below `status.capacity` and is
refused outright — Kubernetes does not shrink volumes, which `persistent-volumes.md:490-493` states
flatly. `1Gi` is exactly `status.capacity`; record which way that one goes, because the boundary is
inclusive or it is not and the pin does not say. `1500Mi` is below the previous request and above
the current capacity, which is precisely the window `RecoverVolumeExpansionFailure` opened, and the
pin describes it at `:479-493` for a PVC whose expansion *failed* rather than one whose expansion
was never attempted. Whether the validation cares about the difference is the thing this step
measures, and the pin will not tell you.

Step 7 reproduces the warning at `:409-417` exactly. The PV goes to `2Gi`, the claim goes to `2Gi`,
and nothing resizes — but for the second reason, not the first. On a cluster with a real driver this
is a trap, because the control plane compares desired to desired and concludes the work is done.
Here the work was never going to be done anyway, so what you are checking is that the two states are
indistinguishable from outside: `df` inside the Pod and `df` on the node both report the size of the
node's filesystem, because a `hostPath` volume has no size of its own and never did. The number in
`capacity` was always a label.

Step 8 finds the controller under both of its names. The command line carries no `--controllers`
flag at all, which means the default set, which means `persistentvolume-expander-controller` is
running; and `system:controller:expand-controller` exists as a ClusterRole with permissions on
`persistentvolumeclaims` and `persistentvolumeclaims/status`. Two names, one component, both
shipped. The last command should find no ClusterRole spelled *expander* — the RBAC objects use the
older spelling and the flag documentation uses the newer one.

Step 9 should report `EXPAND_VOLUME` at docs=0 blog=2, `kubernetes.io/aws-ebs` at docs=0 blog=6,
`allowVolumeExpansion` present in both, `Resizing` absent from the concept page and present twice in
the generated reference, and `expan` absent from `statefulset.md` entirely. The two `sed` ranges
printed side by side are the sentence this exercise turns on: three expandable types, six creatable
types, and an intersection of one that you cannot build without a driver.

Step 10 should report 487 gate files, 230 removed, 182 of them removed after reaching stable and 48
removed before ever getting there, the five-gate cohort with a `1.24`-to-`1.26` stable range, 376
gates carrying a beta stage, fourteen with a beta longer than thirteen releases and six at exactly
thirteen, and `AppArmor` at twenty-seven as the record.

**Read on**

Five, and the last one is the question this exercise cannot close.

1. [Expansion is two phases, and you can get stuck](../../labs/08/09-expansion-two-phase.md) — the
   same feature with a driver underneath it, on a two-node topology. Everything this exercise
   measures by its absence, that lab measures by watching it happen.

2. [The access mode whose gate was deleted](../2021/07-read-write-once-pod-access-mode-alpha.md) —
   the other half of the CSI-vocabulary finding. That exercise measured `SINGLE_NODE_MULTI_WRITER`
   at zero occurrences in the documentation; this one measures `EXPAND_VOLUME` at zero. Same
   specification, same silence, a year apart.

3. [The post that became the
   documentation](../2016/10-dynamic-provisioning-and-storage-in-kubernetes.md) — where
   `allowVolumeExpansion`'s neighbours on the StorageClass came from, and the earliest exercise in
   the corpus built on `kubernetes.io/no-provisioner`, which is the trick that makes this one
   runnable at all.

4. `persistent-volumes.md:453-495` in the pinned tree — the recovery section, written as two tabs
   for two different people. It is the only part of this feature's documentation that assumes the
   expansion will fail, and it is what the post's *Next steps* was pointing at.

5. Unanswerable from the pin: whether `kubernetes.io/aws-ebs` ever accepted `secretNamespace` and
   `secretName`. The in-tree plugin's parameter reference is gone from the tree along with the
   provisioner name, so the pin can show that the post's four-key example matches a GlusterFS
   example and cannot show whether the two keys it kept were ever valid for the provisioner it moved
   them to. The example may have been wrong the day it was published; nothing in this checkout can
   settle it.

**Teardown**

Objects first, then the node, then the control-plane manifest — and check the manifest even if you
think you restored it in step 2:

```sh
kubectl delete pod bw-exp-0 bw-exp-1 --ignore-not-found
kubectl delete pvc bw-exp-0 bw-exp-1 --ignore-not-found
kubectl delete pv bw-exp-0 bw-exp-1 --ignore-not-found
kubectl delete storageclass bw-noexp bw-exp --ignore-not-found
sudo rm -rf /srv/bw-exp
ls -l /etc/kubernetes/manifests/kube-controller-manager.yaml
sudo grep -c 'feature-gates' /etc/kubernetes/manifests/kube-controller-manager.yaml || true
sudo rm -f /root/kcm.yaml.bak
kubectl -n kube-system get pods -l component=kube-controller-manager
```

Leave the guest up if you are going straight on; nothing here has changed the node beyond one
directory tree and one manifest edit that step 2 undid. Otherwise [destroy
it](../../strands/lab-topologies.md#teardown).
