<a id="cloud-provider-integration-changes"></a>

# The escape hatch this post offers you now stops the component from starting, the guide it sends you to opens with a prerequisite the pin cannot satisfy, and the post that founded the whole effort is cited twice under a URL that resolves nowhere and zero times under the one that works

**Post** — [Kubernetes 1.29: Cloud Provider Integrations Are Now Separate Components](https://kubernetes.io/blog/2023/12/14/cloud-provider-integration-changes/),
2023-12-14.

219 lines, 11,585 bytes, by Michael McCune (Red Hat) and Andrew Sy Kim (Google) — the second name
also appears on the 2019 post this one opens by citing, four years and one employer earlier.
Eleventh of this year's thirteen walks in publication order, and the third-longest of them by byte
count, behind 12,890 and 12,802.

**As written** — the post announces a default flip. At `:11-15` Kubernetes v1.29 components *abort*,
in the post's own bold, if you ask for one of the legacy compiled-in cloud provider integrations,
and *"a future release will remove even that option"*. At `:48-54` the mechanism is two feature
gates, `DisableCloudProviders` and `DisableKubeletCloudCredentialProviders`, moving their default
from `false` to `true`; when they are true, *"the only recognized value for the `--cloud-provider`
command line argument is `external`"*. The post quotes both gate descriptions at `:59-65` from the
feature-gates reference, and at `:67-68` forecasts the next move: *"The next stage beyond beta will
be full removal; for that release onwards, you won't be able to override those feature gates back to
false."*

The history is at `:17-30`. SIG Cloud Provider formed in 2018; KEP-2395, *Removing In-Tree Cloud
Provider Code*, was approved in January 2019; the post blockquotes the KEP's motivation paragraph,
typo and `[sic]` intact. At `:39-44` the five legacy integrations are named — Azure, AWS, GCE,
OpenStack, vSphere — with AWS already removed in v1.27 and OpenStack in v1.26, leaving three that
the flip actually affects.

Then the instructions, and they fork. The recommended path at `:95-106` is to set
`--cloud-provider=external` on `kube-apiserver`, `kube-controller-manager` and `kubelet`, deploy a
cloud controller manager, and follow two named pages for the procedure: *Cloud Controller Manager
Administration* and *Migrate Replicated Control Plane To Use Cloud Controller Manager*. The other
path, at `:110-119`, is to opt back out, with one line to add to all three components:

```
--feature-gates=DisableCloudProviders=false,DisableKubeletCloudCredentialProviders=false
```

A note at `:124-128` puts a fuse on that line — the gates *"will be locked to `true` in an upcoming
release"*, and the in-tree providers are *"planned for removal as early as Kubernetes version
1.31"*. At `:132-136` readers on other clouds are told to confirm they are already external by
inspecting the kubelet's `--cloud-provider` flag. `:178-182` lists the five project-hosted
replacements, one repository per cloud.

**As it runs now** — nothing in the post's mechanism is still switchable. Both gates reached stable
in v1.31, both stable stages close at v1.32, and both files declare `removed: true`, so the line at
`:117-119` is not an escape hatch at the pin: it is a flag value that makes the component refuse to
start. The forecast at `:67-68` is right about the destination and wrong about the route — the stage
after beta was stable, not removal, and removal came two releases after that. The forecast at
`:124-128` has no counterpart in the tree at all: neither gate file ever recorded a lock, which is
what the empty `locked` column below records.

The post's `:53-54` was not true when it was written. The pinned gate file for
`DisableCloudProviders` says *"In Kubernetes v1.31 and later, the only valid values for
`--cloud-provider` are the empty string (no cloud provider integration), or "external" (integration
via a separate cloud-controller-manager)"*, and `kubelet.md:161` says the same in the binary's own
help text: *"Set to empty string for running with no cloud provider. Set to 'external' for running
with an external cloud provider."* Every cluster in this repo runs with the empty string, which the
post's sentence excludes. The distinction matters for step 2, where you check what your own cluster
passes.

The two pages the post hands you at `:101-106` are both still live, and neither has moved.
`running-cloud-controller.md:13` still carries `{{< feature-state state="beta"
for_k8s_version="v1.11" >}}`. So does `developing-cloud-controller-manager.md:12`, and so does
`concepts/architecture/cloud-controller.md:10`. Count the beta stamps in the pinned tree: 31
`feature-state` shortcodes declare `state="beta"`, and the three oldest of them — the only three
older than v1.14 outside the style guide's own example page — are these, all v1.11. Twenty-six
releases after that stamp, the cloud controller manager is the oldest thing in the documentation
still calling itself beta, and the in-tree implementation it was built to replace has been deleted
outright.

`running-cloud-controller.md` still describes that implementation in the present tense. `:20-26`
says providers *"already supported in Kubernetes core are expected to use the in-tree
cloud-controller-manager to transition out of Kubernetes core"*; `:90-93` offers to run it as a
DaemonSet and ships the manifest; `developing-cloud-controller-manager.md:41-43` keeps a section
headed *In tree* whose whole content is a pointer to that offer. The manifest is
`examples/admin/cloud/ccm-example.yaml`, and three of its lines have outlived their subject: `:47`
pins `registry.k8s.io/cloud-controller-manager:v1.8.0`, `:50` passes
`--cloud-provider=[YOUR_CLOUD_PROVIDER]`, and `:72-73` selects nodes by
`node-role.kubernetes.io/master`. Step 10 applies it and counts what schedules.

The migration guide is where the post's recommended path actually stops.
`controller-manager-leader-migration.md` states its own starting state at `:52-54`: *"As of version
N, an in-tree cloud provider must be set with `--cloud-provider` flag and `cloud-controller-manager`
should not yet be deployed."* At the pin there is no version N for which that sentence can be made
true on a supported release. Everything after it — the lease patches at `:85` and `:91`, the four
configuration files, the rolling replacement at `:198-202` — is written for a cluster that cannot be
built.

And the guide disagrees with the rest of the tree about how to write its own configuration file, in
two ways that a command settles. The four YAML blocks at `:104-116`, `:122-135`, `:157-169` and
`:236-251` all declare `apiVersion: controllermanager.config.k8s.io/v1`. The flag that consumes that
file says otherwise: `kube-controller-manager.md:675` describes `--leader-migration-config` as
taking a file *"of type LeaderMigrationConfiguration, group controllermanager.config.k8s.io, version
v1alpha1"*, and the generated API reference at `kube-controller-manager-config.v1alpha1.md:522`
gives the same `v1alpha1`. Four occurrences of `/v1` against two of `/v1alpha1`, and the binary is
the tie-breaker; step 8 asks it.

The second disagreement is the controller names. The guide's configuration files migrate `route`,
`service` and `cloud-node-lifecycle`, and its `:233` disables the IPAM controller with
`--controllers=*,-nodeipam`. The list of names the binary accepts is printed in full at
`kube-controller-manager.md:437`, and none of those four is in it: the names there are
`node-route-controller`, `service-lb-controller`, `cloud-node-lifecycle-controller` and
`node-ipam-controller`. The generated API reference offers a third set —
`kube-controller-manager-config.v1alpha1.md:573` gives *"E.g. service-controller, route-controller,
cloud-node-controller"* as examples of the `name` field, and `cloud-node-controller` is a different
controller from `cloud-node-lifecycle-controller`. Three pages, three vocabularies, one field.

Two of the guide's YAML blocks are not YAML. Its `:130-134` and `:244-250` write `component: *`, and
a bare `*` opens an alias node, so a parser stops at the first one with a scanner error rather than
loading a document with a wildcard in it. The second of the two carries a stray leading dash at
`:250` as well, which would make `component` a sibling list item of `nodeipam` rather than its key
even if the value parsed. The guide tells you at `:137` to save that content to
`/etc/leadermigration.conf` and mount it; step 7 saves it and reads it back.

One more thing about both pages, and it is the smallest of the findings and the easiest to check.
The post's first paragraph links the founding decision at `:17-18`, through the reference
`[oldblog]` defined at `:218` as
`https://kubernetes.io/blog/2019/04/17/the-future-of-cloud-providers-in-kubernetes/`. No post in the
767-row archive has that URL. The post is *The Future of Cloud Providers in Kubernetes*, whose file
is `2019/future-of-cloud-providers.md` and which declares no `slug`, so its path is its filename and
its URL ends `/2019/04/17/future-of-cloud-providers/`. The wrong URL occurs exactly twice under
`content/en` — here, and at `controller-manager-leader-migration.md:17`, where it is the link on the
words *"cloud provider extraction effort"*. The correct URL occurs zero times. Both citations of SIG
Cloud Provider's founding document are broken, and they are broken the same way.

**What this exercise does not cover, and where it lives** — the post tells you at `:97-98` to set
`--cloud-provider=external` on `kube-apiserver`, and `kube-apiserver.md` does not document that
flag. That absence is already established and tested against a running API server in [the exercise
on kubeadm v1.8's forecasts](../2017/05-kubeadm-v18-released.md), which reaches it from the other
direction, and it is not re-argued here. The DaemonSet toleration for
`node-role.kubernetes.io/master` in the tree's shipped examples belongs to [the exercise on
StatefulSets and DaemonSets](../2017/04-kubernetes-statefulsets-daemonsets.md); step 10 uses the
`nodeSelector` on the same key instead, which is a different failure and has a different symptom.
The census row for the founding post is in [2019's census](../2019/README.md), where it is a `read`.

**The diff, and why** — four cases at once, and the combination is the point: ***broke***, ***still
right***, ***wrong when it was published*** and ***overtaken by stasis***.

It broke in the only place it hands you a command. The feature-gate line at `:117-119` now prevents
the three components it is addressed to from starting, and following `:110-115` on all three takes
the cluster apart. It is still right everywhere else: every reader who took the recommended path in
December 2023 is fine, and that path — external cloud controller manager,
`--cloud-provider=external`, one repository per cloud — is exactly what the pin runs. It was wrong
on the day it shipped at `:53-54`, which excludes the empty string; that value was valid then and is
valid now, and it is the value every cluster in this repo uses. And the stasis is not the post's:
the two pages it routes its readers to are frozen at a beta stamp from v1.11, describing a starting
state the project spent six years deleting.

The interesting part is which half of the post decayed. The announcement half — what changed, why,
what to do — aged well; the flip happened, the removal happened, the replacements exist at the five
URLs it lists. The *referral* half aged badly, and it aged badly through no fault of its own: the
post correctly pointed at the two canonical procedure pages, and those pages then did not change. A
post can only be as durable as what it links to, and a link is a claim about someone else's
maintenance.

That is also why this is not the ***never absorbed*** case. The post's substance was absorbed
completely — into the gate files, into the kubelet's help text, into the deletion of the code. What
was not absorbed is the follow-through on the pages that describe the migration, which is a
different failure and lands on a different owner.

`DisableCloudProviders`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.22 – v1.28 |
| beta | `true` | — | v1.29 – v1.30 |
| stable | `true` | — | v1.31 – v1.32 |

`DisableKubeletCloudCredentialProviders`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.23 – v1.28 |
| beta | `true` | — | v1.29 – v1.30 |
| stable | `true` | — | v1.31 – v1.32 |

`ControllerManagerLeaderMigration`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.21 – v1.21 |
| beta | `true` | — | v1.22 – v1.23 |
| stable | `true` | — | v1.24 – v1.26 |

All three files declare `removed: true`. None declares a lock in any stage, which is why the
`locked` column is empty throughout — the post's forecast at `:124-128` that the first two would be
*"locked to `true` in an upcoming release"* is not recorded anywhere in the gate files, and the
stage that followed beta was stable rather than the removal the post named at `:67-68`. The third
gate is not the post's; it is the migration guide's, named at
`controller-manager-leader-migration.md:56-61` as the gate an out-of-tree provider needed before
`k8s.io/cloud-provider` v0.22.0. It has been gone since v1.27.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), one node, and the choice is part of
the finding. `controller-manager-leader-migration.md:26-28` says so itself: *"For a single-node
control plane, or if unavailability of controller managers can be tolerated during the upgrade,
Leader Migration is not needed and this guide can be ignored."* You are not going to perform the
migration — there is no in-tree provider to migrate from on any supported release. You are going to
walk the guide's instructions one at a time against a real `kube-controller-manager` and record
which of them the binary still accepts. Every measurement below is single-node work.

**Do**

1. Provision the topology and stand the cluster up, following
   [provision](../../strands/lab-topologies.md#provision) and the [node
   baseline](../../strands/lab-topologies.md#node-baseline-steps), then `kubeadm init` with
   Flannel's CIDR as in [the provisioning lab](../../labs/01/01-provision-and-kubeadm-init.md). Then
   take a backup you will restore from four times.

   ```sh
   ssh zain@10.10.10.180
   kubectl get nodes -o wide
   sudo cp /etc/kubernetes/manifests/kube-controller-manager.yaml ~/kcm.yaml.bak
   sudo cp /var/lib/kubelet/kubeadm-flags.env ~/kubeadm-flags.env.bak
   ```

2. Establish the starting state the post assumes at its `:132-136` — what value your components
   actually pass for `--cloud-provider`, and whether either gate is visible to the API server.

   ```sh
   sudo grep -c 'cloud-provider' /etc/kubernetes/manifests/kube-controller-manager.yaml || true
   sudo grep -c 'cloud-provider' /etc/kubernetes/manifests/kube-apiserver.yaml || true
   sudo cat /var/lib/kubelet/kubeadm-flags.env
   kubectl get --raw /metrics | grep '^kubernetes_feature_enabled' | grep -i cloud \
     || echo "no cloud gate in the series"
   ```

3. Take the post's escape hatch at its `:117-119` literally on the controller manager. Add the line
   to the static pod, then watch what the kubelet does with the result.

   ```sh
   sudo sed -i '/- kube-controller-manager/a\    - --feature-gates=DisableCloudProviders=false,DisableKubeletCloudCredentialProviders=false' \
     /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 30
   kubectl -n kube-system get pods -l component=kube-controller-manager
   sudo crictl ps -a --name kube-controller-manager | head -5
   sudo crictl logs $(sudo crictl ps -a --name kube-controller-manager -q | head -1) 2>&1 | tail -5
   sudo cp ~/kcm.yaml.bak /etc/kubernetes/manifests/kube-controller-manager.yaml
   ```

4. Same line, the other component the post addresses. The kubelet is not a static pod, so this one
   takes the node down and gives it back; do not skip the restore.

   ```sh
   sudo sed -i 's|KUBELET_KUBEADM_ARGS="|KUBELET_KUBEADM_ARGS="--feature-gates=DisableCloudProviders=false,DisableKubeletCloudCredentialProviders=false |' \
     /var/lib/kubelet/kubeadm-flags.env
   sudo systemctl restart kubelet
   sleep 10
   sudo systemctl is-active kubelet || true
   sudo journalctl -u kubelet -n 15 --no-pager | tail -8
   sudo cp ~/kubeadm-flags.env.bak /var/lib/kubelet/kubeadm-flags.env
   sudo systemctl restart kubelet
   ```

5. Now start the migration guide at its prerequisite, `:52-54`. It requires an in-tree cloud
   provider to be set. Try to set one, using a name from the post's own list at `:39-44`.

   ```sh
   sudo sed -i '/- kube-controller-manager/a\    - --cloud-provider=gce' \
     /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 30
   sudo crictl logs $(sudo crictl ps -a --name kube-controller-manager -q | head -1) 2>&1 | tail -6
   kubectl -n kube-system get pods -l component=kube-controller-manager
   sudo cp ~/kcm.yaml.bak /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 20
   ```

6. The guide's first actual step, *Grant access to Migration Lease* at `:75-92`. It gives you two
   `kubectl patch` commands, `:85` and `:91`. Run both.

   ```sh
   kubectl get role -n kube-system | grep leader-locking || true
   kubectl patch -n kube-system role 'system::leader-locking-kube-controller-manager' \
     -p '{"rules":[{"apiGroups":["coordination.k8s.io"],"resources":["leases"],"resourceNames":["cloud-provider-extraction-migration"],"verbs":["create","list","get","update"]}]}' \
     --type=merge
   kubectl patch -n kube-system role 'system::leader-locking-cloud-controller-manager' \
     -p '{"rules":[{"apiGroups":["coordination.k8s.io"],"resources":["leases"],"resourceNames":["cloud-provider-extraction-migration"],"verbs":["create","list","get","update"]}]}' \
     --type=merge || true
   ```

7. The guide's *Initial Leader Migration configuration* at `:94-135`. It offers two forms and
   recommends the second as *"consistent between both parties"*. Save the recommended one where the
   guide says to save it, at `:137`, and then read it back the way the binary will.

   ```sh
   sudo tee /etc/leadermigration.conf >/dev/null <<'EOF'
   kind: LeaderMigrationConfiguration
   apiVersion: controllermanager.config.k8s.io/v1
   leaderName: cloud-provider-extraction-migration
   resourceLock: leases
   controllerLeaders:
     - name: route
       component: *
     - name: service
       component: *
     - name: cloud-node-lifecycle
       component: *
   EOF
   python3 -c "import yaml,sys; yaml.safe_load(open('/etc/leadermigration.conf'))" \
     || echo "the recommended form does not parse"
   ```

8. Fall back to the guide's first form, at `:104-116`, which is valid YAML. Mount it and turn on the
   two flags the guide names at `:142-143`. This is the step that settles `/v1` against `/v1alpha1`.

   ```sh
   sudo tee /etc/leadermigration.conf >/dev/null <<'EOF'
   kind: LeaderMigrationConfiguration
   apiVersion: controllermanager.config.k8s.io/v1
   leaderName: cloud-provider-extraction-migration
   resourceLock: leases
   controllerLeaders:
     - name: route
       component: kube-controller-manager
     - name: service
       component: kube-controller-manager
     - name: cloud-node-lifecycle
       component: kube-controller-manager
   EOF
   sudo sed -i '/- kube-controller-manager/a\    - --enable-leader-migration\n    - --leader-migration-config=/etc/leadermigration.conf' \
     /etc/kubernetes/manifests/kube-controller-manager.yaml
   sudo sed -i 's|volumes:|volumes:\n  - hostPath:\n      path: /etc/leadermigration.conf\n      type: File\n    name: leadermigration|' \
     /etc/kubernetes/manifests/kube-controller-manager.yaml
   sudo sed -i 's|volumeMounts:|volumeMounts:\n    - mountPath: /etc/leadermigration.conf\n      name: leadermigration\n      readOnly: true|' \
     /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 30
   sudo crictl logs $(sudo crictl ps -a --name kube-controller-manager -q | head -1) 2>&1 | tail -8
   ```

9. Change the mounted file's `apiVersion` to the value the two reference pages give, force the
   controller manager to read it again, and compare. Then restore, and test the fourth controller
   name from the guide's Node IPAM section at `:228-234`.

   ```sh
   sudo sed -i 's|controllermanager.config.k8s.io/v1$|controllermanager.config.k8s.io/v1alpha1|' \
     /etc/leadermigration.conf
   sudo crictl rm -f $(sudo crictl ps -a --name kube-controller-manager -q | head -1)
   sleep 30
   sudo crictl logs $(sudo crictl ps -a --name kube-controller-manager -q | head -1) 2>&1 | tail -8
   sudo cp ~/kcm.yaml.bak /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 20
   sudo sed -i '/- kube-controller-manager/a\    - --controllers=*,-nodeipam' \
     /etc/kubernetes/manifests/kube-controller-manager.yaml
   sleep 30
   sudo crictl logs $(sudo crictl ps -a --name kube-controller-manager -q | head -1) 2>&1 | tail -4
   sudo cp ~/kcm.yaml.bak /etc/kubernetes/manifests/kube-controller-manager.yaml
   ```

10. Last, the other page the post sends you to. `running-cloud-controller.md:90-93` offers the
    in-tree cloud controller manager as a DaemonSet and ships the manifest. Apply it and count.

    ```sh
    cd /path/to/kubernetes/website/content/en
    kubectl apply -f examples/admin/cloud/ccm-example.yaml
    kubectl -n kube-system get daemonset cloud-controller-manager
    kubectl get nodes --show-labels | tr ',' '\n' | grep node-role || true
    sudo crictl pull registry.k8s.io/cloud-controller-manager:v1.8.0 \
      || echo "the image the page ships cannot be pulled"
    ```

**Expect**

Step 1 is the ordinary single-node build and should take a few minutes; the node reaches `Ready`
only after Flannel is applied. The two backups are the whole safety net for steps 3 through 9, each
of which deliberately breaks the controller manager and restores it. If `kubeadm init` refuses
because swap is on, the node baseline was skipped.

Step 2 establishes that the post's world is not yours. Neither static pod manifest should contain
the string `cloud-provider` at all, and `kubeadm-flags.env` should not carry it either — kubeadm
sets no cloud provider, which is the empty string, the value the post's `:53-54` says is not
recognised. The metrics grep should also come back empty: `kubernetes_feature_enabled` carries a
series per *live* gate, and both of this post's gates were deleted in v1.33, so there is nothing to
report. Between them these two facts are the exercise in miniature — the switch is gone and the
setting it guarded is the one the post said could not be set.

Step 3 should leave you without a controller manager. The kubelet restarts the static pod when the
manifest changes, the new process parses `--feature-gates`, finds two names it does not recognise,
and exits; expect a crash loop and an `unrecognized feature gate` error naming both. Read the
message carefully: it does not say *removed*, and it does not distinguish a gate that was deleted
from a gate that never existed. A reader following the post's `:117-119` in good faith gets the same
error as a reader who made a typo. Restoring the backup brings the pod back within a minute.

Step 4 is the same failure on a component that cannot crash-loop quietly. The kubelet refuses the
flag and stops; `systemctl is-active` should report `failed` or `activating`, and the journal should
carry the same unrecognised-gate error. While it is down the node goes `NotReady` and nothing
schedules. This is what the post's second option costs at the pin: following it on all three
components, as `:110-115` instructs, takes the cluster apart. Restore the file and restart before
going on.

Step 5 is the migration guide's prerequisite, and it is the one that has no workaround. What you
should *not* see is a controller manager running with a GCE provider — the code is gone. Expect
either a startup error naming `gce` as an unknown provider, or a startup error on the flag value
itself. Either way the guide's `:52-54` has been answered: there is no way to reach the state it
requires as version N. Note that this is not the same as the flag being removed — `--cloud-provider`
is still listed at `kube-controller-manager.md:171`, and its help text there still says only *"Empty
string for no provider"*, never mentioning `external` at all, which is the value `kubelet.md:161`
and the gate file both name.

Step 6 is two patches and one of them cannot land. `system::leader-locking-kube-controller-manager`
exists on any kubeadm cluster and should patch cleanly, which is worth seeing: you have just granted
a live component access to a lease for a migration that cannot happen.
`system::leader-locking-cloud-controller-manager` should fail with a `NotFound` — kubeadm never
creates it, because it never deploys a cloud controller manager. The guide's `:88` says *"Do the
same"* as though the two were symmetric. They are not, and nothing on the page says the second role
is yours to create.

Step 7 is the parser. `yaml.safe_load` should fail with a scanner error about an alias, at the first
`component: *`. The guide recommends this form at `:118-120` precisely because it is *"consistent
between both parties of the migration"* — and it is, in that neither party can read it. Look at
`:244-250` while you are here: the same block reappears with `nodeipam` added, and its last line
carries a leading `-` that would have made `component` a separate list item even in a world where
the value parsed. Two of the guide's four configuration blocks are unusable as printed.

Step 8 is the version question, and the answer comes from the log rather than from either page. The
controller manager reads the mounted file, finds `kind: LeaderMigrationConfiguration` in group
`controllermanager.config.k8s.io` at version `v1`, and decodes it or refuses it. Expect a refusal
naming the group and version it could not recognise. If instead the pod comes up healthy with leader
migration enabled, then `kube-controller-manager.md:675` and
`kube-controller-manager-config.v1alpha1.md:522` are both stale and the task page is right — record
which way it went, because the three pages cannot all be describing the same binary.

Step 9 answers the same question the other way and then moves on to the names. Whichever
`apiVersion` the binary accepts, only one of the two can be right, and the other is a documented
value that does not work. Then the controller list: `--controllers=*,-nodeipam` should be rejected,
because the name at `kube-controller-manager.md:437` is `node-ipam-controller`. That is the fourth
of the guide's four controller names to miss, after `route`, `service` and `cloud-node-lifecycle` in
the configuration files. A migration configuration is a list of controller names, and the guide gets
none of them right against this binary.

Step 10 should create a DaemonSet with `DESIRED 0`. The `nodeSelector` at `ccm-example.yaml:72-73`
is `node-role.kubernetes.io/master`, and kubeadm stopped setting that key —
`labels-annotations-taints/_index.md:2925-2926` says the label for the control-plane role is
`node-role.kubernetes.io/control-plane`, and the only entry for the `master` form, at `:2947-2958`,
documents it as a deprecated *taint* and says *"kubeadm no longer sets or uses this deprecated
taint."* So the manifest the page ships selects a key no node carries, schedules nothing, and
reports success. The image pull is the second half: `ccm-example.yaml:47` names `v1.8.0`, a tag from
2017, and whether it still resolves is the last measurement. Note what the manifest also does at its
`:20` — binds its ServiceAccount to `cluster-admin`, in a page about administering a cloud
integration.

**Read on**

1. [The census row for the post that founded the effort](../2019/README.md) — the 2019 entry for
   *The Future of Cloud Providers in Kubernetes*, a `read`, and the document both broken links were
   aiming at.

2. [The exercise on kubeadm v1.8's forecasts](../2017/05-kubeadm-v18-released.md) — where the API
   server's missing `--cloud-provider` is established against a running binary, from the
   implementation-details page rather than from this post.

3. [The exercise on StatefulSets and DaemonSets](../2017/04-kubernetes-statefulsets-daemonsets.md) —
   the other place in the tree where a shipped example still names `node-role.kubernetes.io/master`,
   there as a toleration rather than a selector.

4. [The exercise on registry.k8s.io](../2022/11-registry-k8s-io-faster-cheaper-ga.md) — what a
   `registry.k8s.io` tag from an old release does and does not still serve, which is the question
   step 10's pull asks.

5. [The drill where the apiserver stops and the controllers do
   not](../../labs/03/40-3c4-apiserver-down-controllers-up.md) — the controller manager as a static
   pod you can stop, break and restore, which is the mechanic steps 3 through 9 lean on.

**Teardown**

```sh
kubectl delete -f examples/admin/cloud/ccm-example.yaml --ignore-not-found
sudo cp ~/kcm.yaml.bak /etc/kubernetes/manifests/kube-controller-manager.yaml
sudo cp ~/kubeadm-flags.env.bak /var/lib/kubelet/kubeadm-flags.env
sudo systemctl restart kubelet
sudo rm -f /etc/leadermigration.conf ~/kcm.yaml.bak ~/kubeadm-flags.env.bak
just tofu labs destroy
```
