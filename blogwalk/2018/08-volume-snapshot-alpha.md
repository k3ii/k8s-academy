<a id="volume-snapshot-alpha"></a>

# The post's one reassurance became the documentation's one warning: the snapshot CRDs do not arrive with the CSI driver but are the distribution's job, so a cluster can run a snapshot-capable driver and still have no `VolumeSnapshot` kind to create

**Post** — [Introducing Volume Snapshot Alpha for
Kubernetes](https://kubernetes.io/blog/2018/10/09/volume-snapshot-alpha/), 9 October 2018, by Jing
Xu (Google), Xing Yang (Huawei) and Saad Ali (Google). 294 lines, 21,181 bytes, announcing the alpha
that shipped in Kubernetes v1.12.

It is a long post and it does four things. It states a goal: that snapshots belong in the Kubernetes
API so that *"applications can be agnostic to the specifics of the cluster they run on and
application deployment requires no “cluster specific” knowledge"* (`:21`). It introduces three new
kinds — `VolumeSnapshot`, `VolumeSnapshotContent`, `VolumeSnapshotClass` (`:50-58`). It adds one
field to an existing kind, `PersistentVolumeClaimSpec.DataSource` (`:64-78`). And it tells you what
you need before any of it works (`:82-86`).

That last list is the part this exercise is about. It has two items, and neither of them is
"install the API".

**As written** — the post's requirements list (`:84-86`) reads:

> * Ensure a CSI driver implementing snapshots is deployed and running on your Kubernetes cluster.
> * Enable the Kubernetes Volume Snapshotting feature via new Kubernetes feature gate (disabled by
>   default for alpha):
>   * Set the following flag on the API server binary: `--feature-gates=VolumeSnapshotDataSource=true`

The post is explicit that installing the types is not on the list, and it is explicit about why. It
first records that the kinds are CRDs and reads that as a direction of travel for the whole project:
*"unlike the core Kubernetes Persistent Volume objects, these Snapshot objects are defined as
CustomResourceDefinitions (CRDs). The Kubernetes project is moving away from having resource types
pre-defined in the API server, and is moving towards a model where the API server is independent of
the API objects"* (`:60`). Then it settles the operational question in one sentence: *"CSI Drivers
that support snapshots will automatically install the required CRDs. Kubernetes end users only need
to verify that a CSI driver that supports snapshots is deployed on their Kubernetes cluster"*
(`:62`).

Read those two together and the reader's model is complete and self-consistent: the API is somebody
else's, it arrives with the driver, and the only check you owe is whether the driver is there.

Four smaller things in the post are worth noting before the diff, because three of them are still
true and one of them has never worked.

The one that has never worked is the first code fence (`:90-109`). It prints two
`VolumeSnapshotClass` objects — `default-snapclass` at `:91-97` and `csi-snapclass` at `:100-108` —
inside a single fence, with two blank lines between them and no `---` document separator. That is
not two YAML documents. It is one document with `apiVersion`, `kind` and `metadata` set twice, and a
parser that reads it has to reject it before it can ever ask what `VolumeSnapshotClass` is. The
second defect is smaller and in the restore manifest: `Namespace: demo-namespace` at `:217`, with a
capital N, inside `metadata`. What a modern API server does with a misspelled key is a subject with
[an exercise of its own in this year](03-announcing-kustomize.md); it is not this one's, and the
manifest is only used here with the key removed.

The three that are still true: snapshots are CSI-only (`:35`), the alpha offered no consistency
guarantees so you had to quiesce the application yourself (`:145`), and — this is the one to hold on
to — *"the external snapshotter will try to find and set a default snapshot class for the
snapshot"* (`:143`). The post names the actor. It is not Kubernetes.

**As it runs now** — the pinned tree has a concept page for this API, and it opens with a list in
the same position as the post's. The post's list is headed *"Before using Kubernetes Volume
Snapshotting, you must:"* (`:82`) and has two items. The pin's, at `volume-snapshots.md:46`, is headed *"Users
need to be aware of the following when using this feature:"* and has six (`:48-66`). Four of the six
exist to say that something has to be installed and whose job it is:

- `:48-50` — *"API Objects `VolumeSnapshot`, `VolumeSnapshotContent`, and `VolumeSnapshotClass` are
  CRDs, not part of the core API."*
- `:52-58` — the Kubernetes team provides *"a snapshot controller to be deployed into the control
  plane, and a sidecar helper container called csi-snapshotter to be deployed together with the CSI
  driver"*.
- `:59-62` — a validating webhook server, which *"should be installed by the Kubernetes distros
  along with the snapshot controller and CRDs, **not CSI drivers**"*.
- `:66` — *"The CRDs and snapshot controller installations are the responsibility of the Kubernetes
  distribution."*

The emphasis on "not CSI drivers" is the pinned page's own. The sentence exists to correct exactly
the sentence the post ends its requirements section with. And `:63-65` closes the last gap in the
post's check: *"CSI drivers may or may not have implemented the volume snapshot functionality."* So
the one verification the post says you owe — is a CSI driver deployed — is neither necessary nor
sufficient for the kinds to exist.

The post's other requirement is gone outright. `VolumeSnapshotDataSource` went alpha, beta, stable
and then removed after v1.22; the flag in `:86` is not accepted by a v1.37 API server. What it gated
was never the three kinds. It gated the one field, and that field is now core, unconditional, and
generalised past snapshots entirely. The ladder below has both.

The three kinds, meanwhile, have left no trace in any generated artifact:

- `reference/kubernetes-api/` has a `storage` directory. It contains six kinds —
  `csi-driver-v1`, `csi-node-v1`, `csi-storage-capacity-v1`, `storage-class-v1`,
  `volume-attachment-v1`, `volume-attributes-class-v1` — and none of them is a snapshot kind. There
  is no generated reference page for `VolumeSnapshot` anywhere in the tree.
- `group-versions.md` is marked `auto_generated: true` and lists every API group the server serves,
  23 rows at `:13-35`. `storage.k8s.io` is there at `:34`. `snapshot.storage.k8s.io` is not in the
  table at all.
- `reference/using-api/deprecation-guide.md` contains the word "snapshot" zero times — not because
  nothing was renamed, but because that guide covers the Kubernetes API and this is not it.

Exactly one generated page in the whole reference tree mentions a snapshot kind, and it does so as a
string: `persistent-volume-claim-v1.md:77` describes `dataSource` as able to specify *"An existing
VolumeSnapshot object (snapshot.storage.k8s.io/VolumeSnapshot)"*. The core API names the kind. It
does not define it, and nothing in the core API requires it to exist.

Every field the post printed for the three kinds was renamed, and the renames are not recorded
anywhere in Kubernetes because the schema is versioned outside it:

| post | pin |
|---|---|
| `snapshotter:` (`:97`, `:104`) | `driver:` (`volume-snapshot-classes.md:49`) |
| `spec.snapshotClassName` (`:133`) | `spec.volumeSnapshotClassName` (`volume-snapshots.md:137`) |
| `spec.source: {name, kind}` (`:134-136`) | `spec.source.persistentVolumeClaimName` (`volume-snapshots.md:138-139`) |
| `spec.snapshotContentName` (`:197`) | `spec.source.volumeSnapshotContentName` (`volume-snapshots.md:160-161`) |
| `spec.csiVolumeSnapshotSource` (`:175`) | `spec.source.snapshotHandle` (`volume-snapshots.md:203-204`) |
| `Ready` under `Status` (`:149`, `:200`) | `readyToUse` |

One thing did survive verbatim, and it is not a field. The annotation key
`snapshot.storage.kubernetes.io/is-default-class: "true"` is at post `:96`, and it is at
`volume-snapshot-classes.md:56` and `:64` unchanged, eight years on. Note what it says: the API
group is `snapshot.storage.k8s.io` and the annotation on objects in that group is
`snapshot.storage.kubernetes.io`. Two spellings of the same domain, in the same object, both correct
because neither is checked by anything in Kubernetes.

The one field the post added is the opposite story in every respect. `dataSource` is still
`TypedLocalObjectReference`, the type the post's Go struct printed at `:74`
(`persistent-volume-claim-v1.md:76`). The restore manifest's `dataSource` block is unchanged: post
`:220-223` and `persistent-volumes.md:1134-1137` are the same four lines, differing only in the
object name they point at. `persistent-volumes.md:1117` marks the feature stable as of v1.20. And
the field has since grown a sibling, `dataSourceRef`, which drops the two-kinds restriction
altogether (`:80-81`).

Three defects in the pinned concept page are worth having seen, because all three are on this
exercise's subject and one of them is a manifest that cannot apply:

- `:233-235` is a fence tagged ```` ```yaml ```` containing a shell command, the command carries a
  `$` prompt so it cannot be pasted, and the CRD it names — `volumesnapshotcontent` — is not a CRD
  name. A CRD's name is `plural.group`.
- `:239` reads `` `snapshot.storage.kubernetes.io/allow-volume-mode-change: "true"`needs `` — no
  space before "needs".
- `:252-253` writes `annotations:` as a YAML list item. `metadata.annotations` is a map of string to
  string, so that manifest has never applied. It is the only `annotations:` key in the file, and the
  neighbouring file writes the same key as a map (`volume-snapshot-classes.md:63-64`).

Two remarks on the prose, both of which run the same direction as the diff. `:227-229` speaks of
*"the `VolumeSnapshots` API installed on your cluster"* and asks whether it *supports* a field —
which is how you talk about a dependency, not about your own API. And `volume-snapshot-classes.md`
manages the reverse of the post's precision: *"Kubernetes automatically selects a default
VolumeSnapshotClass"* (`:75-77`), where the post said the external snapshotter does it (`:143`). The
older document names the actor correctly and the newer one does not.

**What this exercise does not cover, and where it lives.** The `sourceVolumeMode` field and the
`allow-volume-mode-change` annotation are a security mechanism with a history of their own, and the
census rows for two later years own it; this exercise touches `:252-253` only as a YAML shape and
never as a control. The release-by-release story of how snapshots got from this alpha to GA is owned
by a later year's row too, which is why the ladder here transcribes gate files rather than narrating
graduations. `VolumeGroupSnapshot`, mentioned at `:68-69`, belongs to another year. And what a
v1.37 API server does with a misspelled field is [the kustomize
exercise](03-announcing-kustomize.md)'s subject, in this year, with two siblings before it.

**The diff, and why** — the post was right about the direction and wrong about the consequence, and
the consequence is the part a reader had to act on.

The direction was real. `:60` predicted that the project would stop pre-defining resource types in
the API server and move to a model where the server is independent of the objects, and the three
snapshot kinds are the demonstration: eight years later they are still CRDs, still not in the group
table, and the API they belong to has its own release cadence, its own repository and its own
version skew against the cluster it runs in. The post called that a design goal being met, and it
was.

The consequence the post drew from it was that the reader had nothing to do. *"Kubernetes end users
only need to verify that a CSI driver that supports snapshots is deployed"* (`:62`). What actually
happened is that the CRDs, the snapshot controller and a validating webhook all became someone's job
to install, and the pinned documentation had to spend four of its six opening bullets saying whose
job, ending with a flat assignment of responsibility to the distribution (`:66`) and one italicised
exclusion of the party the post named (`:59-62`).

So this is not a case where the post broke, and not one where it was wrong when published — in
v1.12 the external-snapshotter sidecar did ship the CRDs, and the post described its own release
accurately. It is the case where **a fact about who ships something moved without the API changing
shape at all**. Nothing in the manifests at `:127-136` or `:170-181` became invalid because
Kubernetes changed. They became invalid because a project outside Kubernetes renamed its own fields,
and the reason a reader cannot look those renames up in `deprecation-guide.md` is the same reason
the kinds are not in `group-versions.md`.

That is the reading worth carrying: the post's own success is what made its instructions wrong. An
API that the API server does not define is an API that the API server cannot install, cannot
version, and cannot deprecate on your behalf. The field the post added stayed core and got stronger
— stable at v1.20, generalised to any custom resource, locked on at v1.33. The kinds it announced
went out of the building.

**The ladder** — two gates, and a third that has no file.

`VolumeSnapshotDataSource` — the gate the post tells you to set at `:86`.

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.12 – v1.16 |
| beta | `true` | — | v1.17 – v1.19 |
| stable | `true` | — | v1.20 – v1.22 |

The file declares `removed: true` and carries a `# Removed from Kubernetes` comment above its
`title`. Its body is one line: "Enable volume snapshot data source support." Read the three rows
against what the gate actually controlled — the `dataSource` field on a PVC, not the three kinds —
and the shape says the ordinary thing: a field arrived behind a flag in the release the post
announces, defaulted on two releases later, went stable at v1.20 exactly where
`persistent-volumes.md:1117` still marks the feature stable, and the flag was deleted two releases
after that because there was nothing left to switch off.

`AnyVolumeDataSource` — what the field became.

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.18 – v1.23 |
| beta | `true` | — | v1.24 – v1.32 |
| stable | `true` | `true` | v1.33 – |

Body: "Enable use of any custom resource as the `DataSource` of a PVC." No `toVersion` and no
`removed`, so it is live at the pin; `locked: true` on the stable row means the API server accepts
the flag and refuses to accept `false` for it. The generalisation swallowed a third gate on the way:
`VolumePVCDataSource` ran alpha v1.15, beta v1.16 – v1.17, stable v1.18 – v1.21, `removed: true`,
for the single case of naming an existing PVC as the source. A fourth is still open at one row —
`CrossNamespaceVolumeDataSource`, alpha, `false`, from v1.26, no `toVersion` — for a source in
another namespace.

The third gate has no ladder because it has no file. `volume-snapshots.md:272` says *"When the
`VolumeSnapshotTopology` feature is enabled"* and `:283-284` says it is *"an alpha feature of the CSI
sidecars, enabled with the `VolumeSnapshotTopology` feature gate on the csi-snapshotter and
external-provisioner"*. There are 488 feature-gate files in the pinned tree and none of them is
`VolumeSnapshotTopology`, because the flag is on somebody else's binary. The Kubernetes docs
document a feature gate that Kubernetes does not have — which is the whole of this exercise
restated in one missing file.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo). Bring it up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, then `ssh zain@10.10.10.180`.

One node is enough, and a plain kubeadm cluster with no CSI driver and no StorageClass is not a
limitation here — it is the instrument. Every claim in this exercise is about what a cluster does
*not* have, and the fastest way to measure that is on a cluster that has nothing. Steps 4, 5, 11 and
the reading half of 12 need no cluster at all, only the pinned checkout; the rest need the API
server and never need a volume to bind. Nothing below waits on a PVC reaching `Bound`, and nothing
below should be read as expecting it to: [the storage classes
exercise](../2017/01-dynamic-provisioning-and-storage-classes-kubernetes.md) covers why a kubeadm
cluster has no StorageClass and what a claim does without one.

**Do**

1. Establish what the cluster has. Take the negative result first, then the positive control:

   ```sh
   kubectl create ns snapshots
   kubectl api-resources --api-group=snapshot.storage.k8s.io
   kubectl api-versions | grep -i snapshot; true
   kubectl get crd
   kubectl api-resources --api-group=storage.k8s.io
   kubectl get storageclass
   ```

   Count the rows the fifth command prints and hold the number. Then compare it against the pinned
   reference tree, which is step 4.

2. Try the post's first manifest exactly as printed. Copy `:90-109` — both objects, two blank lines
   between them, no separator:

   ```sh
   kubectl -n snapshots apply -f - <<'YAML'
   apiVersion: snapshot.storage.k8s.io/v1alpha1
   kind: VolumeSnapshotClass
   metadata:
     name: default-snapclass
     annotations:
       snapshot.storage.kubernetes.io/is-default-class: "true"
   snapshotter: com.example.csi-driver


   apiVersion: snapshot.storage.k8s.io/v1alpha1
   kind: VolumeSnapshotClass
   metadata:
     name: csi-snapclass
   snapshotter: com.example.csi-driver
   parameters:
     fakeSnapshotOption: foo
     csiSnapshotterSecretName: csi-secret
     csiSnapshotterSecretNamespace: csi-namespace
   YAML
   ```

   Record the error verbatim, and then answer one question about it: does the message name YAML, or
   does it name a kind? Which of the two you get tells you how far the request travelled. Do not
   move on until you can say which side of the wire refused it.

3. Now separate the documents and ask the server the question the post intended. Then ask the same
   question in the pinned tree's own words (`volume-snapshot-classes.md:44-52`):

   ```sh
   kubectl -n snapshots apply -f - <<'YAML'
   apiVersion: snapshot.storage.k8s.io/v1alpha1
   kind: VolumeSnapshotClass
   metadata:
     name: csi-snapclass
   snapshotter: com.example.csi-driver
   ---
   apiVersion: snapshot.storage.k8s.io/v1
   kind: VolumeSnapshotClass
   metadata:
     name: csi-hostpath-snapclass
   driver: hostpath.csi.k8s.io
   deletionPolicy: Delete
   YAML
   ```

   Two objects, two API versions eight years apart, one error each. Write down whether the two
   errors differ. `volume-snapshot-classes.md:39-42` predicts this outcome in a note: *"Installation
   of the CRDs is the responsibility of the Kubernetes distribution. Without the required CRDs
   present, the creation of a VolumeSnapshotClass fails."* The version is not what is missing.

4. Ask where the kinds are documented. Two commands in the pinned checkout, no cluster:

   ```sh
   R=/path/to/pinned/website/content/en/docs/reference
   ls $R/kubernetes-api/storage/
   grep -c '^| `' $R/kubernetes-api/group-versions.md
   grep -n 'storage' $R/kubernetes-api/group-versions.md
   grep -ril volumesnapshot $R/kubernetes-api/
   grep -ci snapshot $R/using-api/deprecation-guide.md; true
   ```

   Six kinds in the storage directory against the row count you took in step 1. The group table's
   row count, and which storage groups are in it. Then the single file in the whole generated
   reference that mentions a snapshot kind — read `persistent-volume-claim-v1.md:76-77` and note
   that the mention is a string inside a field description. Then the deprecation guide's count of
   the word.

5. Read the two lists side by side. This is the centre of the exercise and it is reading, not
   running:

   ```sh
   W=/path/to/pinned/website/content/en
   sed -n '82,86p' $W/blog/_posts/2018/volume-snapshot-alpha.md
   sed -n '60p;62p' $W/blog/_posts/2018/volume-snapshot-alpha.md
   sed -n '46,66p' $W/docs/concepts/storage/volume-snapshots.md
   ```

   The post's list has two items and the pin's has six. Go through the six and mark each one as
   either something the post also says, something the post says the opposite of, or something the
   post does not raise. Then find the sentence in the pinned list that exists to contradict `:62`,
   and the sentence that makes the post's one verification insufficient on its own.

6. Test the post's second requirement. It named a flag; check whether the field it gated still needs
   one:

   ```sh
   kubectl explain persistentvolumeclaim.spec.dataSource
   kubectl -n kube-system get pod -l component=kube-apiserver \
     -o jsonpath='{.items[0].spec.containers[0].command}' | tr ',' '\n' | grep -i feature; true
   ```

   No `--feature-gates` for snapshots anywhere on the API server, and the field explains anyway.
   Compare against the `VolumeSnapshotDataSource` ladder: the flag in `:86` has not been accepted
   since v1.22, and the thing it gated has been on unconditionally since v1.20.

7. Read the field's sibling, and find a disagreement:

   ```sh
   kubectl explain persistentvolumeclaim.spec.dataSourceRef
   G=/path/to/pinned/website/content/en/docs/reference/command-line-tools-reference/feature-gates
   sed -n '8,23p' $G/AnyVolumeDataSource.md
   ```

   The generated description says `(Beta) Using this field requires the AnyVolumeDataSource feature
   gate to be enabled`. The gate file says `stable` from v1.33 with `locked: true`. Both are in the
   pinned tree, they disagree, and the stale one is the generated one — which means the text comes
   from a comment in the Kubernetes source and not from the website repository. Record both.

8. Ask the core API to accept a reference to a kind that does not exist. Use the pin's own restore
   manifest (`persistent-volumes.md:1127-1143`), minus the `storageClassName` this cluster has no
   class for:

   ```sh
   kubectl -n snapshots apply --dry-run=server -f - <<'YAML'
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: restore-pvc
   spec:
     dataSource:
       name: new-snapshot-test
       kind: VolumeSnapshot
       apiGroup: snapshot.storage.k8s.io
     accessModes:
       - ReadWriteOnce
     resources:
       requests:
         storage: 1Gi
   YAML
   ```

   Step 3 could not create a `VolumeSnapshotClass` on this cluster and step 1 showed there is no
   `VolumeSnapshot` kind. This manifest points at one by name and group. Note which of the two
   requests the API server accepts, and that acceptance here is not a bug: `dataSource` is a
   reference, validated against a list of permitted type names, and existence is the provisioner's
   problem.

9. Find the boundary of that permissiveness. `persistent-volume-claim-v1.md:81` states an asymmetry
   — *"While `dataSource` ignores disallowed values (dropping them), `dataSourceRef` preserves all
   values, and generates an error if a disallowed value is specified."* A core kind that is not a
   PVC is a disallowed value in both. Send it to each field in turn:

   ```sh
   for f in dataSource dataSourceRef; do
     echo "--- $f"
     kubectl -n snapshots apply --dry-run=server -o json -f - <<YAML 2>&1 | tail -20
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: disallowed-source
   spec:
     $f:
       name: some-config-map
       kind: ConfigMap
     accessModes:
       - ReadWriteOnce
     resources:
       requests:
         storage: 1Gi
   YAML
   done
   ```

   Two identical values, two different outcomes. For the first, search the returned JSON for the
   field you sent and say whether it came back. For the second, read the error. Then re-read `:81`
   and check that what you got is what it describes.

10. Watch the two fields mirror each other. Send only `dataSourceRef`, with no namespace, and read
    back what the server made of the object:

    ```sh
    kubectl -n snapshots apply --dry-run=server -o json -f - <<'YAML' \
      | python3 -c 'import sys,json; s=json.load(sys.stdin)["spec"]; print("dataSource   ", s.get("dataSource")); print("dataSourceRef", s.get("dataSourceRef"))'
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: mirrored
    spec:
      dataSourceRef:
        apiGroup: snapshot.storage.k8s.io
        kind: VolumeSnapshot
        name: new-snapshot-test
      accessModes:
        - ReadWriteOnce
      resources:
        requests:
          storage: 1Gi
    YAML
    ```

    `persistent-volume-claim-v1.md:77` says that with `AnyVolumeDataSource` enabled, *"dataSourceRef
    contents will be copied to dataSource when dataSourceRef.namespace is not specified"*, and the
    ladder says that gate has been stable and locked on since v1.33. Print both and record what you
    get. If only one of the two is populated, that is the finding: write down which, and which
    document it contradicts.

11. Take the rename census yourself rather than trusting the table above. Every one of these is a
    field the post printed:

    ```sh
    W=/path/to/pinned/website/content/en
    for f in snapshotter snapshotClassName snapshotContentName csiVolumeSnapshotSource; do
      printf '%-24s post=%s pin=%s\n' "$f" \
        "$(grep -c "$f" $W/blog/_posts/2018/volume-snapshot-alpha.md; true)" \
        "$(grep -rc "$f" $W/docs/concepts/storage/volume-snapshots.md; true)"
    done
    grep -rn 'is-default-class' $W/blog/_posts/2018/volume-snapshot-alpha.md \
      $W/docs/concepts/storage/volume-snapshot-classes.md
    ```

    Four field names present in the post and absent from the pinned page. Then the one string that
    is in both, unchanged, and the two spellings of the same domain inside it — the group is
    `snapshot.storage.k8s.io` and the annotation is `snapshot.storage.kubernetes.io`. Say which
    component would have to check the annotation for the mismatch to matter, and whether that
    component is in this cluster.

12. Read the three defects, then prove the one that is provable without any CRD. `metadata.annotations`
    is a map of string to string on every Kubernetes object, so a core object carries the same shape
    as `:252-253`:

    ```sh
    V=/path/to/pinned/website/content/en/docs/concepts/storage/volume-snapshots.md
    sed -n '233,235p;239p;247,253p' $V
    kubectl -n snapshots apply --dry-run=server -f - <<'YAML'
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: annotations-as-a-list
      annotations:
        - snapshot.storage.kubernetes.io/allow-volume-mode-change: "true"
    data: {}
    YAML
    ```

    The fence at `:233-235` is tagged `yaml` and holds a prompt-prefixed shell command whose CRD
    name is not a CRD name — work out what the name should have been from the rule that a CRD is
    named `plural.group`, and check it against the `kubectl get crd` output from step 1. Then the
    missing space at `:239`. Then the list-shaped `annotations` at `:252-253`: the ConfigMap above
    has the same defect in a kind this cluster does have, so the server can tell you what is wrong
    with it. There is no correct version of the key anywhere in this file — it appears once — so for
    the map form, read `volume-snapshot-classes.md:61-64`.

**Expect**

Step 1 finds nothing. `--api-group=snapshot.storage.k8s.io` returns no resources, `kubectl
api-versions` has no snapshot line, `get crd` reports no resources found, and `get storageclass`
likewise. The positive control is the contrast: `--api-group=storage.k8s.io` prints a handful of
rows, and every one of them corresponds to a file you will list in step 4.

Step 2 fails, and the *kind* of failure is the reading. A duplicated top-level key is a parse
problem, and a parse problem is settled before anything is sent. Whatever the exact wording, the
question to answer is whether the message mentions the document or the kind — this is the one
command in the exercise that never reaches the API server. Step 3 then fails twice for the other
reason, once per document, and both errors should be about the kind rather than the version.

Steps 4 and 5 are the load-bearing pair. Expect six `.md` files plus `_index.md` in the storage
reference directory and no snapshot kind among them; 23 rows in the group table with
`storage.k8s.io` present and `snapshot.storage.k8s.io` absent; exactly one file in the whole
generated reference matching `volumesnapshot`, and that one a PVC page; and zero occurrences of
"snapshot" in the deprecation guide. In step 5, `:66` is the sentence that assigns the work and
`:59-62` is the sentence that names the party the post named and excludes it.

Step 6 explains the field with no gate set anywhere, and finds no snapshot-related
`--feature-gates` on the API server. Step 7 produces a documented disagreement rather than an
answer; both halves belong in your notes.

Step 8 is accepted. Step 9 gives two different outcomes for one value — one field returns the object
without the reference you sent, the other returns an error. Step 10 prints two lines; the
interesting case is if the second is populated and the first is not.

Step 11 finds four names in the post and none of the four in the pinned page, and one annotation key
identical across eight years. Step 12's ConfigMap is rejected, and the rejection is about a type,
not a spelling.

**Read on**

- [The CSI beta exercise](02-container-storage-interface-beta.md) — the post this one's `:44` sends
  you to, and the exercise that establishes what a CSI driver is and what a sidecar does before
  anything here asks whose sidecar ships an API.
- [The storage classes exercise](../2017/01-dynamic-provisioning-and-storage-classes-kubernetes.md)
  — for why this cluster has no StorageClass, and for the same annotation pattern
  (`is-default-class`) on the kind that *is* in the core API.
- [The kustomize exercise](03-announcing-kustomize.md) — for what a v1.37 API server does with the
  misspelled `Namespace:` at the post's `:217`, which this exercise deliberately steps around.
- [The extensible admission exercise](01-extensible-admission-is-beta.md) — for the other reading of
  "the API server is independent of the API objects" that `:60` predicts, from the webhook side
  rather than the CRD side.

**Teardown**

```sh
kubectl delete ns snapshots
kubectl get crd
kubectl api-resources --api-group=snapshot.storage.k8s.io
```

Nothing in this exercise installs anything, so there is nothing to uninstall — every object was
either refused or sent with `--dry-run=server`, and the namespace holds only itself. Confirm that
with the last two commands: the cluster should be exactly as poor in snapshot kinds as it was in
step 1, which is the state the pinned documentation says is normal.
