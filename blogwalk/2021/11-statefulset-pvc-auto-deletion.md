<a id="kubernetes-1-23-statefulset-pvc-auto-deletion"></a>

# Three lines under a shortcode that reads stable since v1.32, the page still tells you to switch this on in two components, the half of the matrix that deletes a claim does it by making the doomed Pod the claim's owner, and the beta announcement seventeen months later is this post again

**Post** — [Kubernetes 1.23: StatefulSet PVC Auto-Deletion
(alpha)](https://kubernetes.io/blog/2021/12/16/kubernetes-1-23-statefulset-pvc-auto-deletion/),
2021-12-16, Kubernetes v1.23 — Matthew Cary of Google. 103 lines, 6,652 bytes, one author and one
vendor: the second shortest of this year's eleven walked posts, and the last of them. It announces
one optional field with two sub-fields, spends more than half its length walking the four
combinations those two sub-fields make, and ends by asking a question about the mechanism
underneath.

**As written**

The problem statement at `:19-32` is a complaint about who was doing the work:

> The behavior before Kubernetes v1.23 was that the control plane never cleaned up the PVCs
> created for StatefulSets - this was left up to the cluster administrator, or to some add-on
> automation that you'd have to find, check suitability, and deploy.

The fix is one field. `:36-39` introduces it as something you switch on — *If you enable the alpha
feature, a StatefulSet spec includes a PersistentVolumeClaim retention policy* — and `:41-47` names
its two halves. `whenDeleted` covers the whole StatefulSet going away; `whenScaled` covers some
replicas going away. Each takes `Retain` or `Delete`, and the deletion is *done with a normal object
deletion, so that, for example, all retention policies for the underlying PV are respected*.

`:49` then says *this policy forms a matrix with four cases*, and the next four bullets are the
matrix: both `Retain` as the default and the pre-existing behaviour; `Delete`/`Retain` for a CI
instance or an ETL pipeline; `Delete`/`Delete` for data that can be rebuilt; and `Retain`/`Delete`
worked through an Elasticsearch cluster you scale to demand but sometimes take down whole. Four
bullets, four scenarios, thirty-two lines — the bulk of the post.

`:84-86` sends the reader to the documentation for the details. `:88-91` is the call to action:

> Enable the feature and try it out! Enable the `StatefulSetAutoDeletePVC` feature gate on a
> cluster, then create a StatefulSet using the new policy. Test it out and tell us what you think!

And `:93-97` is the part that makes this post worth walking rather than reading. Having built the
feature on owner references, the author says out loud that they do not know whether that was a good
idea:

> I'm very curious to see if this owner reference mechanism works well in practice. For example,
> we realized there is no mechanism in Kubernetes for knowing who set a reference, so it's
> possible that the StatefulSet controller may fight with custom controllers that set their own
> references.

That is an open question published in an announcement, which is rare enough on its own. What
happened to it is most of the diff below.

**As it runs now** — the field is unconditional, the page that documents it has not noticed, and the
question has not been answered.

**The gate went stable at v1.32 and is still in the tree.** `StatefulSetAutoDeletePVC.md:9-20` gives
alpha v1.23–v1.26, beta v1.27–v1.31, stable from v1.32 with no `toVersion` and no `removed: true`.
That is six releases GA and still listed, which puts it near the top of a small population: of the
pin's 487 gate files, 230 declare `removed: true` and 257 do not, and 96 of those 257 carry a stable
stage. Thirteen of the 96 have been stable for exactly six releases. Only five have been stable
longer — `ExecProbeTimeout` at eighteen, `PodSchedulingReadiness` at eight, and `ElasticIndexedJob`,
`LogarithmicScaleDown` and `StatefulSetStartOrdinal` at seven.

**The page that documents the feature still tells you to enable it.** `statefulset.md:509` is a
`feature-state` shortcode naming this gate, which is driven by the gate file above. Three lines
later, `statefulset.md:511-514` says:

> The optional `.spec.persistentVolumeClaimRetentionPolicy` field controls if
> and how PVCs are deleted during the lifecycle of a StatefulSet. You must enable the
> `StatefulSetAutoDeletePVC` feature gate
> on the API server and the controller manager to use this field.

The same pinned tree says the opposite two directories away. `feature-gates/index.md:109-112`
defines the stable stage as *The feature is always enabled; you cannot disable it* and *The
corresponding feature gate is no longer needed*. Ninety-eight lines above the stale sentence,
`statefulset.md:414-416` prints the correct version of exactly the same sentence for
`StatefulSetRecreateStrategy`, which really is alpha and really did arrive at v1.37 — and that one
links to the gate's own anchor, while the stale one links only to the index.

**It is not the only one.** Five passages in four files under `content/en/docs`, outside the
feature-gate reference itself, still instruct the reader to enable a gate the same tree lists as
stable and un-removed: `storage-limits.md:75`, `volume-populators-and-data-sources.md:35` and
`:113`, `statefulset.md:512`, and `virtual-ips.md:395`.

**The gate carries no `locked` marker, which is why step 2 is worth running.** The pin marks 49
gates `locked`, and every one of those 49 markers sits on a stable stage; 46 of them belong to gates
that have not been removed. `StatefulSetAutoDeletePVC` is not among them. So the file that says the
feature is always on and the file that says you must switch it on are joined by a third thing that
does not say either: a stable gate with no marker claiming it refuses to be set.

**The four cases are unchanged, down to the defaults.** `statefulset.md:517-543` is the post's
matrix in reference form — `whenDeleted`, `whenScaled`, `Delete`, `Retain (default)` — and
`stateful-set-v1.md:287` and `:291` give the API's own wording for the two fields. Nothing about the
semantics moved between alpha and stable. What `statefulset.md:537-541` adds is the sentence the
post leaves implicit: the policies apply *only* when Pods go because the set was deleted or scaled
down, not when a Pod is replaced.

**The mechanism the post is curious about is now documented at length, and it is asymmetric.**
`statefulset.md:558-565` covers `whenDeleted`: the controller puts an owner reference to the
*StatefulSet* on every PVC. `statefulset.md:567-573` covers `whenScaled`, and the owner is somebody
else entirely — a Pod whose ordinal is above the replica count is *condemned*, and the condemned Pod
is made the owner of its own PVC before it is deleted. Two policies, one object, two owner kinds.
Neither announcement says this.

**There is one paragraph of operational advice that exists nowhere in either announcement.**
`statefulset.md:575-583` is about the controller crashing mid-scale-down: the owner reference may or
may not have been set on a condemned Pod's PVC, it may take several reconcile loops, and the
recommendation is to wait for the controller rather than force-delete. That paragraph is step 8.

**The page that defines owner references has not heard of StatefulSets.**
`owners-dependents.md:24-31` lists the objects Kubernetes sets `metadata.ownerReferences` on
automatically: *ReplicaSets, DaemonSets, Deployments, Jobs and CronJobs, and
ReplicationControllers*. Five years after the StatefulSet controller joined that list in fact, it
has not joined it on the page. The nearest the pin comes to answering the post's question is
`owners-dependents.md:33-40`, which says `blockOwnerDeletion` is set to `true` automatically when a
controller sets the reference — a signal that *a* controller did it, and nothing at all about which
one.

**Both announcements link to a section that does not exist.** `:84-86` points at
`statefulset/#persistentvolumeclaim-policies`. The heading at `statefulset.md:507` is `##
PersistentVolumeClaim retention`, and no heading anywhere in the pinned tree produces the anchor the
post uses; the string occurs in exactly two files, and both of them are blog posts. The gate file's
own link at `StatefulSetAutoDeletePVC.md:25` uses the right anchor.

**Neither announcement names the field.** `persistentVolumeClaimRetentionPolicy` appears in three
files at the pin — `statefulset.md`, `stateful-set-v1.md` and the gate file — and in none of the 767
blog posts. The archive announced this feature twice using only the names of its two sub-fields.

**And the second announcement is the first one again.** The beta post of 2023-05-04 has 981 words;
so does this one; 921 of them match in order. Eleven of this post's seventeen paragraphs reappear in
it unchanged once backticks and line wrapping are normalised, including the whole Elasticsearch
bullet and the open question — where the single edit is *we realized* becoming *I realized*. The
rewrite tidied the missing blank line after this post's first `##` heading at `:16` and introduced
*retrained* for *retained* in its opening sentence.

**The diff, and why** — five of the seven cases. The feature is the rare one where the thing
announced did not change at all, so four of the five are about the writing around it.

**Broke: the enablement instruction, and the page that repeats it.** `:90-91` tells you to enable
the gate. Since v1.32 there is nothing to enable, by the pin's own definition at
`feature-gates/index.md:111-112`. A stale instruction in a five-year-old blog post is expected and
harmless; the same instruction at `statefulset.md:512-514`, on the page the post sends you to for
*all the details*, is neither. Step 1 reads both sentences and asks the cluster which one it is
living by.

**Still right: the matrix, down to the defaults.** All four bullets at `:51-82` describe behaviour
the pin still documents in the same terms, and `Retain`/`Retain` is still what you get when you say
nothing. Step 4 is the post's four-case table reduced to its first cell, which is also the behaviour
every StatefulSet written before v1.23 depends on.

**Retired by being agreed with: the problem statement.** `:19-32` complains that PVC cleanup was
*left up to the cluster administrator, or to some add-on automation that you'd have to find, check
suitability, and deploy*. The add-on is now the StatefulSet controller, on by default and not
optional. The complaint won so completely that the only trace of it left in the docs is a field
whose default is the behaviour it complained about.

**Never absorbed: who set the reference.** `:93-97` asks a specific question — there is no way to
know who set an owner reference, so a custom controller and the StatefulSet controller may fight
over one. The pin does not answer it. `owners-dependents.md` does not name StatefulSets among the
controllers that set references at all, and the only clue it offers about authorship is
`blockOwnerDeletion`. The author reprinted the question verbatim seventeen months later rather than
answering it. Step 7 puts a second owner reference on a live PVC by hand and watches what the
controller does with it, which is the smallest possible version of the experiment the post asks for.

**Overtaken by stasis: the announcement itself.** The clearest evidence that nothing about this
feature moved between v1.23 and v1.27 is that the beta announcement is this post with the version
numbers changed. Nine hundred and twenty-one identical words is not a summary or a follow-up; it is
a republication, and it is the correct response to a feature that graduated without changing.

**The ladder**

One gate, transcribed from its `stages:` list parsed as YAML. It is the only gate this post
mentions.

```
StatefulSetAutoDeletePVC  alpha  false  1.23 - 1.26
                          beta   true   1.27 - 1.31
                          stable true   1.32 -
```

No `toVersion` on the last row, no `removed:` line, no `locked:` on any row. Nine releases from
first appearance to GA, four of them at alpha, five at beta — and then six more as a stable gate
nobody has deleted. The body text at `StatefulSetAutoDeletePVC.md:22-26` is two sentences and a
link, and the link is the one that points at the right anchor.

This ladder is already printed once in this corpus, as a table in [the StatefulSet rename
exercise](../2016/14-statefulset-run-scale-stateful-applications-in-kubernetes.md), where it appears
as one of four gates that qualify a 2016 claim — there it is the reason the 2016 post's closing
demonstration is now conditional. Here it is the subject. That exercise also runs the `whenDeleted`
half of the matrix, so this one starts from `whenScaled`, which nothing in the corpus has touched.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo): one node at `10.10.10.180`, 4096MB, 4
vCPU, 25G, brought up with [the provisioning sequence](../../strands/lab-topologies.md#provision).
Three replicas, three statically created `hostPath` volumes and one directory tree on the node. A
second node would change nothing here: the subject is which object owns a claim, not where the claim
is mounted, and putting all three replicas on one node keeps the owner references in one `kubectl
get` at a time.

**Do**

1. Ask the two components that enforce this field what they think the gate is, then read the two
   sentences in the pinned tree that disagree about whether it exists. The `stage` label on the
   metric is the whole answer to the first question:

   ```sh
   kubectl version -o json | python3 -c 'import json,sys
   print("server:", json.load(sys.stdin)["serverVersion"]["gitVersion"])'
   kubectl get --raw /metrics | grep 'kubernetes_feature_enabled.*StatefulSetAutoDeletePVC' \
     || echo "kube-apiserver: not reported"
   CERT="--cert /etc/kubernetes/pki/apiserver-kubelet-client.crt \
     --key /etc/kubernetes/pki/apiserver-kubelet-client.key"
   sudo curl -sk $CERT https://127.0.0.1:10257/metrics \
     | grep 'kubernetes_feature_enabled.*StatefulSetAutoDeletePVC' \
     || echo "kube-controller-manager: not reported"
   cd /path/to/kubernetes/website
   sed -n '509,515p' content/en/docs/concepts/workloads/controllers/statefulset.md
   sed -n '109,113p' content/en/docs/reference/command-line-tools-reference/feature-gates/index.md
   ```

2. Try to take the switch the other way, in the component that does the deleting. The API server is
   left alone on purpose — whatever happens here, the cluster stays reachable, and the StatefulSet
   controller is what acts on the policy. The static pod restarts the moment the file is written:

   ```sh
   sudo cp /etc/kubernetes/manifests/kube-controller-manager.yaml /root/kcm.yaml.bak
   sudo sed -i '/- kube-controller-manager/a\    - --feature-gates=StatefulSetAutoDeletePVC=false' \
     /etc/kubernetes/manifests/kube-controller-manager.yaml
   sudo grep -n 'feature-gates' /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 25
   kubectl -n kube-system get pods -l component=kube-controller-manager
   sudo crictl logs "$(sudo crictl ps -a -q --name kube-controller-manager | head -1)" 2>&1 | tail -6
   sudo cp /root/kcm.yaml.bak /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 25
   kubectl -n kube-system get pods -l component=kube-controller-manager
   ```

3. Build the ground. One StorageClass that provisions nothing, three volumes backed by three
   directories on the node, a headless Service, and a three-replica StatefulSet whose claim template
   asks for them. Then write the replica's own name into each volume, so that later you can tell
   whether a claim came back or was rebuilt:

   ```sh
   for i in 0 1 2; do sudo mkdir -p /srv/bw-sts/$i; done
   kubectl apply -f - <<'YAML'
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata: { name: bw-sts }
   provisioner: kubernetes.io/no-provisioner
   YAML
   for i in 0 1 2; do
     kubectl apply -f - <<YAML
   apiVersion: v1
   kind: PersistentVolume
   metadata: { name: bw-sts-$i }
   spec:
     capacity: { storage: 1Gi }
     accessModes: ["ReadWriteOnce"]
     persistentVolumeReclaimPolicy: Retain
     storageClassName: bw-sts
     hostPath: { path: /srv/bw-sts/$i }
   YAML
   done
   kubectl apply -f - <<'YAML'
   apiVersion: v1
   kind: Service
   metadata: { name: bw-sts, labels: { app: bw-sts } }
   spec:
     clusterIP: None
     selector: { app: bw-sts }
     ports: [{ port: 8080, name: http }]
   ---
   apiVersion: apps/v1
   kind: StatefulSet
   metadata: { name: bw-sts }
   spec:
     serviceName: bw-sts
     replicas: 3
     selector: { matchLabels: { app: bw-sts } }
     template:
       metadata: { labels: { app: bw-sts } }
       spec:
         containers:
           - name: c
             image: registry.k8s.io/e2e-test-images/agnhost:2.53
             args: ["netexec", "--http-port=8080"]
             volumeMounts: [{ name: data, mountPath: /data }]
     volumeClaimTemplates:
       - metadata: { name: data, labels: { app: bw-sts } }
         spec:
           accessModes: ["ReadWriteOnce"]
           storageClassName: bw-sts
           resources: { requests: { storage: 1Gi } }
   YAML
   kubectl rollout status statefulset/bw-sts --timeout=180s
   for i in 0 1 2; do kubectl exec bw-sts-$i -- sh -c "echo replica-$i > /data/who"; done
   kubectl get pvc -l app=bw-sts
   kubectl get statefulset bw-sts -o jsonpath='{.spec.persistentVolumeClaimRetentionPolicy}'; echo
   kubectl explain statefulset.spec.persistentVolumeClaimRetentionPolicy
   ```

4. Run the post's first bullet — the default, which is also every StatefulSet written before v1.23.
   Scale down by two, count what is left, then scale back up and ask the replica who it is:

   ```sh
   kubectl scale statefulset bw-sts --replicas=1
   kubectl rollout status statefulset/bw-sts --timeout=120s
   kubectl get pods -l app=bw-sts
   kubectl get pvc -l app=bw-sts
   kubectl get pvc data-bw-sts-2 -o jsonpath='{.metadata.ownerReferences}'; echo
   sudo cat /srv/bw-sts/2/who
   kubectl scale statefulset bw-sts --replicas=3
   kubectl rollout status statefulset/bw-sts --timeout=180s
   kubectl exec bw-sts-2 -- cat /data/who
   ```

5. Now set the half of the matrix the corpus has already walked, and watch only the owner
   references. Nothing is deleted in this step — the policy is patched on and then straight back off
   again, which is the part `statefulset.md:558-565` describes and the part it does not:

   ```sh
   kubectl patch statefulset bw-sts --type=merge \
     -p '{"spec":{"persistentVolumeClaimRetentionPolicy":{"whenDeleted":"Delete","whenScaled":"Retain"}}}'
   sleep 5
   kubectl get pvc -l app=bw-sts -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.ownerReferences[*].kind}{"\t"}{.metadata.ownerReferences[*].name}{"\n"}{end}'
   kubectl get pvc data-bw-sts-0 -o jsonpath='{.metadata.ownerReferences[0].blockOwnerDeletion}'; echo
   kubectl patch statefulset bw-sts --type=merge \
     -p '{"spec":{"persistentVolumeClaimRetentionPolicy":{"whenDeleted":"Retain","whenScaled":"Retain"}}}'
   sleep 5
   kubectl get pvc -l app=bw-sts -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.ownerReferences[*].kind}{"\n"}{end}'
   ```

6. Set the other half and scale down again, this time watching the claims rather than the Pods. The
   loop is there because the interesting state lasts seconds: the condemned claim acquires an owner
   before its Pod is deleted, and is collected after:

   ```sh
   kubectl patch statefulset bw-sts --type=merge \
     -p '{"spec":{"persistentVolumeClaimRetentionPolicy":{"whenDeleted":"Retain","whenScaled":"Delete"}}}'
   kubectl scale statefulset bw-sts --replicas=1
   for i in $(seq 1 12); do
     kubectl get pvc -l app=bw-sts \
       -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.ownerReferences[*].kind}{"\t"}{.metadata.ownerReferences[*].name}{"\n"}{end}'
     echo "--- $i"
     sleep 2
   done
   kubectl get pvc -l app=bw-sts
   kubectl get pv
   sudo cat /srv/bw-sts/2/who
   ```

7. Run the experiment the post says it wants. Give the one surviving claim a second owner, chosen by
   hand, then move the retention policy back and forth underneath it and see whether the controller
   removes what it did not write. The two `blockOwnerDeletion` readings are the only thing in the
   API that distinguishes a reference a controller set from one you set:

   ```sh
   kubectl create configmap bw-owner --from-literal=note=hand-set
   UID=$(kubectl get configmap bw-owner -o jsonpath='{.metadata.uid}')
   kubectl patch pvc data-bw-sts-0 --type=merge -p "{\"metadata\":{\"ownerReferences\":[{\"apiVersion\":\"v1\",\"kind\":\"ConfigMap\",\"name\":\"bw-owner\",\"uid\":\"$UID\"}]}}"
   kubectl get pvc data-bw-sts-0 -o jsonpath='{range .metadata.ownerReferences[*]}{.kind}{"\t"}{.name}{"\t"}{.blockOwnerDeletion}{"\n"}{end}'
   kubectl patch statefulset bw-sts --type=merge \
     -p '{"spec":{"persistentVolumeClaimRetentionPolicy":{"whenDeleted":"Delete","whenScaled":"Delete"}}}'
   sleep 10
   kubectl get pvc data-bw-sts-0 -o jsonpath='{range .metadata.ownerReferences[*]}{.kind}{"\t"}{.name}{"\t"}{.blockOwnerDeletion}{"\n"}{end}'
   kubectl patch pvc data-bw-sts-0 --type=json -p='[{"op":"remove","path":"/metadata/ownerReferences"}]'
   kubectl get pvc data-bw-sts-0 -o jsonpath='{.metadata.ownerReferences}'; echo
   ```

8. Reproduce the one paragraph of this feature's documentation that neither announcement contains.
   Put the two volumes back, scale up, then take the controller away and force-delete a condemned
   Pod while it is gone — which is precisely what `statefulset.md:575-583` tells you not to do:

   ```sh
   kubectl patch statefulset bw-sts --type=merge \
     -p '{"spec":{"persistentVolumeClaimRetentionPolicy":{"whenDeleted":"Retain","whenScaled":"Delete"}}}'
   for i in 1 2; do
     kubectl delete pv bw-sts-$i --ignore-not-found
     kubectl apply -f - <<YAML
   apiVersion: v1
   kind: PersistentVolume
   metadata: { name: bw-sts-$i }
   spec:
     capacity: { storage: 1Gi }
     accessModes: ["ReadWriteOnce"]
     persistentVolumeReclaimPolicy: Retain
     storageClassName: bw-sts
     hostPath: { path: /srv/bw-sts/$i }
   YAML
   done
   kubectl scale statefulset bw-sts --replicas=3
   kubectl rollout status statefulset/bw-sts --timeout=180s
   sudo mv /etc/kubernetes/manifests/kube-controller-manager.yaml /root/kcm.yaml.parked
   sleep 25
   kubectl -n kube-system get pods -l component=kube-controller-manager
   kubectl scale statefulset bw-sts --replicas=1
   sleep 10
   kubectl get pods -l app=bw-sts
   kubectl delete pod bw-sts-2 --force --grace-period=0
   kubectl get pvc data-bw-sts-2 -o jsonpath='{.metadata.ownerReferences}'; echo
   sudo mv /root/kcm.yaml.parked /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 40
   kubectl get pvc -l app=bw-sts
   kubectl get pods -l app=bw-sts
   ```

9. Take the census of the vocabulary in the pinned tree. Four names, one of which the archive never
   uses, and one anchor that resolves nowhere:

   ```sh
   cd /path/to/kubernetes/website
   for S in persistentVolumeClaimRetentionPolicy whenScaled whenDeleted StatefulSetAutoDeletePVC \
            persistentvolumeclaim-policies; do
     printf '%-42s docs=%s blog=%s\n' "$S" \
       "$(grep -rl "$S" content/en/docs --include='*.md' | wc -l | tr -d ' ')" \
       "$(grep -rl "$S" content/en/blog --include='*.md' | wc -l | tr -d ' ')"
   done
   grep -n '^## PersistentVolumeClaim' content/en/docs/concepts/workloads/controllers/statefulset.md
   grep -rn 'persistentvolumeclaim-retention' \
     content/en/docs/reference/command-line-tools-reference/feature-gates/StatefulSetAutoDeletePVC.md
   sed -n '24,40p' content/en/docs/concepts/overview/working-with-objects/owners-dependents.md
   sed -n '414,416p' content/en/docs/concepts/workloads/controllers/statefulset.md
   ```

10. Offline, in the pinned checkout, measure the two things the diff turns on: how long this gate
    has been stable relative to every other stable gate, and how much of the 2021 post the 2023 one
    is:

    ```sh
    cd /path/to/kubernetes/website
    python3 - <<'PY'
    import os, re, difflib
    G = "content/en/docs/reference/command-line-tools-reference/feature-gates"
    stable = {}
    for fn in sorted(os.listdir(G)):
        if not fn.endswith(".md") or fn == "index.md": continue
        fm = open(os.path.join(G, fn)).read().split("---")[1]
        if re.search(r"^removed:\s*true", fm, re.M): continue
        stage, since = None, None
        for line in fm.splitlines():
            t = line.strip()
            if t.startswith("- stage:"): stage = t.split(":", 1)[1].strip()
            if t.startswith("fromVersion:") and stage == "stable" and since is None:
                since = int(t.split('"')[1].split(".")[1])
        if since is not None: stable[fn[:-3]] = since
    print("live gates with a stable stage:", len(stable))
    mine = stable["StatefulSetAutoDeletePVC"]
    print("stable since 1.%d, so %d releases including 1.37" % (mine, 37 - mine + 1))
    print("stable for longer:", sorted(k for k, v in stable.items() if v < mine))
    print("as long, this one included:", len([k for k, v in stable.items() if v == mine]))
    B = "content/en/blog/_posts"
    def words(p):
        return re.sub(r"\s+", " ", open(os.path.join(B, p)).read().split("---", 2)[2].replace("`", "")).split()
    a = words("2021/statefulset-pvc-auto-deletion.md")
    b = words("2023/statefulset-autodelete.md")
    sm = difflib.SequenceMatcher(None, a, b)
    print("2021 words %d, 2023 words %d, matching %d, ratio %.3f"
          % (len(a), len(b), sum(x.size for x in sm.get_matching_blocks()), sm.ratio()))
    PY
    ```

**Expect**

Step 1 finds the gate present and on. Both components report a `kubernetes_feature_enabled` series
for `StatefulSetAutoDeletePVC` with value 1; write down the `stage` label, because it is the pin's
own machine-readable statement of the thing `statefulset.md:512` denies. The two `sed` commands then
print the contradiction in full: a `feature-state` shortcode, a sentence telling you to enable the
gate on two components, and — in the other file — *the corresponding feature gate is no longer
needed*.

Step 2 has two possible outcomes and the interesting work is deciding which one you saw before you
look it up. Either the controller manager accepts the flag and restarts, in which case a gate the
documentation calls stable is still a switch; or it refuses to start, in which case the gate is
locked in code and the pin's `locked` marker — absent here, present on 46 other stable gates — is
not a complete record of which gates refuse to move. The restore is a file copy, and the component
is back within half a minute. Do not leave the flag in place; every step after this one assumes a
default control plane.

Step 3 gives you three Pods, three bound claims named `data-bw-sts-0` through `-2`, and three files
on the node. The `jsonpath` for the retention policy is worth reading closely against `kubectl
explain`: the field is optional, and what you get back for a StatefulSet that never mentioned it is
either the two defaults spelled out or nothing at all. Either way `statefulset.md:543` says the
behaviour is `Retain` on both.

Step 4 is the post's first bullet and the whole of the pre-v1.23 world. Two Pods go, three claims
stay, `data-bw-sts-2` has no owner references at all, and `/srv/bw-sts/2/who` still says
`replica-2`. Scaling back up does not create anything: the same claim binds to the same volume and
`bw-sts-2` reads back its own name. This is the behaviour the post is offering to change, and it is
still what you get by saying nothing.

Step 5 is where an owner reference appears without anything being deleted. Setting `whenDeleted:
Delete` puts a reference of kind `StatefulSet`, named `bw-sts`, on all three claims, with
`blockOwnerDeletion` true — `owners-dependents.md:35-38` says that is what a controller does.
Setting the policy back to `Retain` takes them off again. That second half is not written down
anywhere in the pin; `statefulset.md:564-565` describes the reference being placed and never
mentions its removal.

Step 6 is the half of the matrix nothing else in this corpus walks, and the owner is not the
StatefulSet. For a few seconds `data-bw-sts-1` and `data-bw-sts-2` carry a reference of kind `Pod`
naming the Pod that is about to be deleted, which is `statefulset.md:567-573` exactly: the condemned
Pod is made the owner, then the Pod terminates, then the garbage collector takes the claim with it.
Afterwards two claims are gone, two volumes are `Released` rather than `Available` — the reclaim
policy on them is `Retain`, which is the ground [the lab on a released
volume](../../labs/08/02-released-not-available.md) already covers — and `/srv/bw-sts/2/who` still
says `replica-2`. Nothing deleted any data. The feature deletes API objects and lets the PV's own
policy decide the rest, which is what `:45-47` promised.

Step 7 is the post's question, run. The hand-set reference to the ConfigMap has no
`blockOwnerDeletion` at all, while the controller's has it true, so there is exactly one bit of
provenance available and it distinguishes *some controller* from *not a controller*. Then watch what
happens when the policy asks the controller to write its own reference onto a claim that already has
yours: record whether both survive, whether yours is dropped, and whether the order of the list
changed. Whatever you see, the pin does not document it — that is the sense in which the question
the post asked in December 2021 is still open.

Step 8 should stop the scale-down dead. With no controller manager there is nothing to condemn the
Pods, so `kubectl scale` changes the spec and nothing else happens; the force-delete removes
`bw-sts-2` without any of the reconciliation `statefulset.md:567-573` describes, and the claim is
left in whatever state the controller had reached — which for a controller that was never running is
no owner reference at all. The paragraph at `statefulset.md:575-583` is about the harder case where
the controller had *started*; you have produced its limiting case. What the controller does when it
returns and finds the Pod already gone is the part to write down, because the pin does not say.

Steps 9 and 10 are arithmetic. The census should give `persistentVolumeClaimRetentionPolicy` docs=3
blog=0, `whenScaled` and `whenDeleted` docs=2 blog=2, `StatefulSetAutoDeletePVC` docs=2 blog=2, and
`persistentvolumeclaim-policies` docs=0 blog=2 — an anchor used only by the two posts that announce
the feature and defined nowhere. Step 10 should report 96 live gates with a stable stage, this one
stable for six releases, five stable for longer, thirteen at exactly six including this one, and 921
of 981 words shared between the two announcements.

**Read on**

Five, and the last one is the question this exercise cannot close.

1. [The StatefulSet rename](../2016/14-statefulset-run-scale-stateful-applications-in-kubernetes.md)
   — where this gate is first laddered, as one of four that qualify a 2016 claim, and where the
   `whenDeleted` half of the matrix is run against the post whose closing demonstration it reverses.

2. [The finalizer exercise](03-using-finalizers-to-control-deletion.md) — the other half of how an
   object refuses to disappear. Owner references schedule a deletion; finalizers postpone one. The
   same claims carry both.

3. [The PersistentVolume leak exercise](10-prevent-persistentvolume-leaks.md) — the layer below this
   one. This exercise deletes claims and never touches storage; that one is about what the volume
   does afterwards, and why the `Retain` policy here leaves three directories on the node.

4. `statefulset.md:575-583` in the pinned tree — the crash-recovery paragraph, and the only piece of
   this feature's documentation that reads like it was written by someone who had operated it.

5. Unanswerable from the pin: when the anchor `#persistentvolumeclaim-policies` stopped resolving,
   and whether it ever did. The pinned tree is one commit; it can show that the anchor is used by
   two posts and defined by none, and it cannot show whether the heading was renamed after 2021 or
   the link was wrong the day it was published.

**Teardown**

Objects first, then the node, then the control-plane manifest — and check the manifest even if you
think you restored it in step 2, because step 8 moves the same file:

```sh
kubectl delete statefulset bw-sts --ignore-not-found
kubectl delete service bw-sts --ignore-not-found
kubectl delete configmap bw-owner --ignore-not-found
kubectl delete pvc -l app=bw-sts --ignore-not-found
kubectl delete pv bw-sts-0 bw-sts-1 bw-sts-2 --ignore-not-found
kubectl delete storageclass bw-sts --ignore-not-found
sudo rm -rf /srv/bw-sts
ls -l /etc/kubernetes/manifests/kube-controller-manager.yaml
sudo grep -c 'feature-gates' /etc/kubernetes/manifests/kube-controller-manager.yaml || true
sudo rm -f /root/kcm.yaml.bak /root/kcm.yaml.parked
kubectl -n kube-system get pods -l component=kube-controller-manager
```

If the guest is not needed for the next exercise, [destroy
it](../../strands/lab-topologies.md#teardown) rather than reasoning about what step 8 left behind.
