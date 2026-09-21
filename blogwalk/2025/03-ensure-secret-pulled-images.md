<a id="ensure-secret-pulled-images"></a>

# The page that defines the image pull policy still gives the answer this post replaced, and keeps every line it has about credential verification in one band four hundred lines below, while the policy that makes that verification configurable is spelled two ways in two references

**Post** — [Kubernetes v1.33: Image Pull Policy the way you always thought it worked!](https://kubernetes.io/blog/2025/05/12/kubernetes-v1-33-ensure-secret-pulled-images-alpha/),
2025-05-12.

8,391 bytes across 136 lines, of which 31 are blank; 1,290 words. Two authors, Ben Petersen and
Stanislav Láznička, both at Microsoft. Nine second-level headings, one `{{< note >}}` defining the
term *pod credentials*, one `{{< figure >}}` whose SVG is 32,224 bytes — nearly four times the prose
it illustrates — and not one code fence. Nine external links, eight of them distinct: two to the
same KEP-2535, one to KEP-4412, one to a ten-year-old GitHub issue, two to author profiles, two to
Slack, and one to the SIG Auth meeting schedule. Exactly one link points into the documentation, at
`:115`, and unlike the single documentation link in the Endpoints deprecation post it lands where it
says it will.

**As written**

The post opens on a hole. `imagePullPolicy: IfNotPresent` has always done what it says and nothing
more: if the image is on the node, use it. The post's worked scenario at `:28-34` runs *Pod A* in
*Namespace X*, which references *Secret 1* and pulls *image Foo* from a private registry, and then
*Pod B* in *Namespace Y*, scheduled to the same node, which references no secret at all and gets
*image Foo* anyway. The post dates the problem by its issue number rather than by a release: `:16`
links kubernetes issue 18787, open "for over 10 years".

The fix, in the post's account, is one behaviour change with one shape. `:52-53` states it flatly:
"If the image is present, then the behavior of the Kubelet changes. The Kubelet will now verify the
pod's credentials before allowing the pod to use the image." Three headings then apply that single
rule to the three policies. `IfNotPresent` verifies before reuse (`:47-58`). `Never` does not fetch,
but still demands credentials for an image already on the node (`:60-68`). `Always` is unchanged,
because it always went to the registry (`:70-79`) — and the post is candid that forcing `Always`
through pod admission had been "the only way" to close the hole, at the cost of putting the registry
in the critical path of every rollout and restart (`:76-79`).

`:81-107` is the mechanism, and it is file-based. The kubelet writes a record of intent before a
pull, writes a record of success after one — including a hash of the credentials used and the Secret
they came from — and then deletes the intent. A later pod on the same node is admitted to the image
if its credential hash or its source Secret matches a recorded successful pull, and otherwise is
made to pull again, which triggers the registry's own authorization. `:109-116` asks you to turn on
the `KubeletEnsureSecretPulledImages` feature gate on your 1.33 kubelets, and `:118-127` lists four
things still to come: interoperation with KEP-4412, a benchmarking suite, an in-memory caching
layer, and credential expiry.

**As it runs now**

**The gate is two rungs further up, and the cluster this exercise runs on already has it on.**
`docs/reference/command-line-tools-reference/feature-gates/KubeletEnsureSecretPulledImages.md:8-15`
gives two stages and no more: alpha from 1.33 to 1.34 with `defaultValue: false`, then beta from
1.35 with `defaultValue: true` and no `toVersion`. At the pin, v1.37, that is three releases in beta
with no stable rung. The instruction at `:112` to enable the gate is therefore unnecessary on any
cluster from 1.35 on, which includes every cluster this tree builds. The gate file also carries
`_build: list: never` and `render: false` at `:4-6`, so the two sentences of description at `:17-19`
never render as a page of their own — they exist only to feed the `{{< feature-state >}}` shortcode
wherever it is called.

**The post describes one behaviour; the pin ships four, and the default is the weakest of the three
that verify anything.** `docs/concepts/containers/images.md:435-442` lists the values of
`imagePullCredentialsVerificationPolicy`: `NeverVerify` mimics the gate being off,
`NeverVerifyPreloadedImages` exempts anything the kubelet did not pull itself,
`NeverVerifyAllowListedImages` narrows that exemption to a configured list, and `AlwaysVerify`
verifies everything. `:438` says the second of those "is the default behavior". The post's flat
sentence at `:52-53` describes `AlwaysVerify`, which is not what you get.

**The first place the pinned tree disagrees with itself: the policy value is spelled two ways, and a
command settles it.** The concept page writes `NeverVerifyAllowListedImages`, with a capital L, at
`images.md:439`. The generated configuration reference writes `NeverVerifyAllowlistedImages`,
lowercase, at `docs/reference/config-api/kubelet-config.v1beta1.md:717`, and again at `:736` inside
the description of `preloadedImagesVerificationAllowlist`, the field that value exists to activate.
One of the two is a string the kubelet will refuse. Step 9 puts each into a kubelet configuration
and reads the answer out of the restart.

**The second such disagreement is a sentence long, and a command settles that one too.**
`docs/reference/node/kubelet-files.md:171-172` reads: "These records are cached as files in the
`image_registry` directory within the kubelet base directory. On a typical Linux node, this means
`/var/lib/kubelet/image_manager`." The directory is named twice in consecutive sentences and the two
names differ. `:174-176` then describes the two subdirectories, `pulling` and `pulled`, which is the
post's mechanism written down. Step 2 asks the node which of the two parent names exists.

**The canonical definition of `imagePullPolicy` was never touched.**
`docs/concepts/containers/images.md:89-90` still defines `IfNotPresent` as "the image is pulled only
if it is not already present locally" and stops there. The file is 589 lines; every one of the
fourteen lines in it containing the string *verif* falls between `:413` and `:449`, a band 37 lines
deep sitting 330 lines past that definition. Exactly one link reaches into the band from outside it,
at `:413`, and it sits inside a `{{< note >}}` under **Pre-pulled images**, a heading a reader
looking up a pull policy has no reason to open. `Never`, at `:104-107`, at least points at
`#pre-pulled-images`; `IfNotPresent` at `:89-90` points nowhere at all.

**The same file sells the old model three more times after that.** `images.md:280-282` lists
pre-pulled images among the ways to reach a private registry and states the consequence without
qualification: "All Pods can use any images cached on a node." The **Use cases** section repeats the
point twice more, at `:557-558` and at `:561-562`, each time as advice: keep the `AlwaysPullImages`
admission controller active, because "Otherwise, all Pods potentially have access to all images" and
"Otherwise, all Pods of all tenants potentially have access to all images." Both sentences are the
hole the post closed, offered at the pin as a live risk.

**Outside that file the hole is still described as open, in the present tense, on the page the
post's own workaround lives on.**
`docs/reference/access-authn-authz/admission-controllers.md:158-162` explains why you want
`AlwaysPullImages`: "Without this admission controller, once an image has been pulled to a node, any
pod from any user can use it by knowing the image's name (assuming the Pod is scheduled onto the
right node), without any authorization check against the image." No feature gate is mentioned.
`docs/concepts/security/security-checklist.md:386-388` files the same controller under plugins "not
enabled by default but could be considered", and `docs/concepts/storage/volumes.md:560-561` extends
it to the `image` volume source. Five pages under `docs/` name the new model — `images.md`,
`kubelet-files.md`, the two generated kubelet configuration references, and the metrics reference —
and three of the pages that recommend `AlwaysPullImages` still teach the old one.

**The record format is documented twice over, and a third of its fields are not documented at all.**
`kubelet-config.v1beta1.md:411-458` gives `ImagePulledRecord`, and
`docs/reference/config-api/kubelet-config.v1alpha1.md:75-122` gives the same type again under
`kubelet.config.k8s.io/v1alpha1`, field for field, example for example. Which `apiVersion` the
kubelet actually writes into the file is not stated on either page; step 6 reads it off disk. Inside
the v1beta1 page, `ImagePullSecret` at `:2059-2099` has four fields, all four marked `[Required]`,
and three of the four — `uid`, `namespace`, `name` — carry the text "No description provided.";
`ImagePullServiceAccount` at `:2105-2138` has three fields, all `[Required]`, all three undescribed.
Both pages also mistype the record's own name: the heading is `ImagePulledRecord`, and the first
sentence under it at `:415` in v1beta1 and `:79` in v1alpha1 calls it `ImagePullRecord`.

**The two kinds of record hash different things into their filenames.** `ImagePullIntent`, at
`kubelet-config.v1beta1.md:399-405`, says the filename is a SHA-256 of `image`, "the image spec from
a Container's image field". `ImagePulledRecord`, at `:436-443`, says the filename is a SHA-256 of
`imageRef`, "a reference to the image represented by this file as received from the CRI". Those are
two different strings for the same image: one is what you typed, the other is what the runtime
resolved. Steps 5 hashes both and finds out which directory each belongs to. The `credentialMapping`
key is a third form again — per `:452-453`, the container's image field "that's got its tag/digest
removed".

**Two of the four things filed under "what's next" have already shipped, and one of them is visible
only as a metric.** `:121` wanted the feature to work with KEP-4412; that graduated to beta in 1.34,
and `blog/_posts/2025/kubernetes-1-34-sa-tokens-image-pulls-beta.md:59-67` describes the result —
ServiceAccount namespace, name and UID recorded per pulled image, revocable by deleting and
recreating the ServiceAccount so the UID changes. Its landing place in the record is
`kubernetesServiceAccounts`, at `kubelet-config.v1beta1.md:2024-2029`. `:124-125` wanted an
in-memory caching layer; `docs/reference/instrumentation/metrics.md:2520-2532` already exposes
`kubelet_imagemanager_inmemory_pulledrecords_usage_percent` and
`kubelet_imagemanager_inmemory_pullintents_usage_percent`. Neither the concept page nor the kubelet
file reference mentions an in-memory cache at all.

**Seven metrics name this subsystem, no concept page cites any of them, and they are spelled two
ways.** `metrics.md:2499-2545` carries `kubelet_image_manager_ensure_image_requests_total`, with
labels `present_locally`, `pull_policy` and `pull_required`, and then six more prefixed
`kubelet_imagemanager_` without the second underscore: `image_mustpull_checks_total` labelled by
`result`, the two in-memory gauges, and `ondisk_pulledrecords` and `ondisk_pullintents`. All seven
are stability level ALPHA. `kubelet_imagemanager` appears on exactly one page in the English tree,
this one. Step 3 scrapes them, and step 2's file count has `ondisk_pulledrecords` to check itself
against.

**The release notes cannot agree on who did the work, and one of them calls a configuration field a
flag.** The post says at `:49` that "we - SIG Auth and SIG Node" did it.
`blog/_posts/2025/kubernetes-v1-33-release/index.md:527-529` credits KEP-2535 to SIG Auth alone;
`blog/_posts/2025/kubernetes-v1-35-release/index.md:199` credits it to SIG Node alone. `:197` of
that same 1.35 post calls `imagePullCredentialsVerificationPolicy` a flag. It is not:
`docs/reference/command-line-tools-reference/kubelet.md` lists eight flags with `image` in the name
and none of them is this, and the string `VerificationPolicy` does not occur in that file. It is a
kubelet configuration field and nothing else.

**What this exercise does not cover, and where it lives.** The `image` volume source belongs to [the
2024 image-volume post](../2024/07-image-volume-source.md), and this exercise hands it one open
question rather than answering it: whether credential verification reaches an image mounted as a
volume at all, given that `images.md:444-445` scopes the verification to pre-pulled images,
node-wide secrets and Pod-level secrets and says nothing about volumes. Toggling `AlwaysPullImages`
on a running API server is [the admission-plugin lab](../../labs/03/13-toggle-a-built-in-plugin.md);
this exercise only cites the plugin as the workaround the post retires, and never enables it.
Counting the CRI calls one pod's pull costs is [the CRI call-counting
lab](../../labs/06/02-one-pod-is-how-many-cri-calls.md). Where images live on disk, and what happens
when that filesystem is split off from the node's root, is [the 2024 image-filesystem
post](../2024/01-kubernetes-separate-image-filesystem.md), which also owns the garbage collection
that can delete an image out from under a record read here. Nothing below reads a Secret's bytes off
the disk they are stored on; that is [the encryption-at-rest
lab](../../labs/10/12-a-secret-that-is-no-longer-plaintext-on-disk.md).

**The diff, and why**

**Still right.** The mechanism survives the read intact. Intent record, then pull, then success
record carrying a credential hash and the Secret's coordinates, then the intent deleted — that is
`:87-97` of the post and `kubelet-files.md:168-176` plus `kubelet-config.v1beta1.md:411-458` of the
pin, in the same order and with the same parts. The promise at `:56-58` that pods sharing a
credential, or sharing a Secret across a rotation, do not re-authenticate is repeated at
`images.md:447-451` in almost the same words. Two of the four items the post files under "what's
next" have since shipped, which is a stronger form of still right: the post's forecast was accurate,
and only the documentation that would have told you so is missing.

**Broke.** Two instructions no longer apply. `:112` tells you to enable
`KubeletEnsureSecretPulledImages` on your 1.33 kubelets; from 1.35 the gate defaults to on, so on
this tree's clusters the thing to practise is turning it *off*, not on. And `:52-53` describes the
new behaviour as a single rule, which it was at 1.33 alpha and is not at the pin: there are four
policies, the default exempts every image the kubelet did not pull itself, and on a node that had
images before the gate was first enabled that exemption covers all of them — `images.md:453-467`
says so plainly, and adds that deleting the records directory reproduces the same blanket exemption
on the next restart. A reader who takes `:52-53` literally will believe a node is closed that is
not.

**Never absorbed.** The correction reached one section of one concept page and stopped. The
definition of `IfNotPresent` at `images.md:89-90` is unchanged and unlinked; the pre-pulled bullet
at `:281` still says every pod can use any cached image; the **Use cases** advice at `:557-558` and
`:561-562` still presents `AlwaysPullImages` as what stands between a tenant and someone else's
image; and `admission-controllers.md:158-162` still describes the hole in the present tense, on the
page a reader arrives at from all three. This is the diff that costs something. Every one of those
four passages is the first thing a reader looking up pull policy, pre-pulled images, or multi-tenant
image isolation will find, and all four were true when the post was written.

**Overtaken by stasis.** The other two items on the post's list have not moved. A benchmarking suite
(`:122-123`) and credential expiry (`:126-127`) leave no trace in the pinned tree three releases
later: nothing in `images.md`, nothing in `kubelet-files.md`, no field in either kubelet
configuration reference, no metric. Credential expiry is the one that matters, because without it a
credential that successfully pulled an image once keeps working on that node for as long as the
record survives, which `images.md:465-467` implies is until somebody deletes the directory.

**The ladder**

One gate, two rungs, and the second one is where you already are. `KubeletEnsureSecretPulledImages`
was alpha and off in 1.33 and 1.34, and is beta and on from 1.35 with no end version recorded, so at
the pin it has been beta for 1.35, 1.36 and 1.37 without a stable rung. The lab cluster runs v1.35,
which is the first release on which none of the post's setup is needed and the feature is simply
present. The second column of the ladder is the policy, and it has no ladder of its own:
`imagePullCredentialsVerificationPolicy` carries no feature gate and no version history anywhere in
the pinned tree, defaults to `NeverVerifyPreloadedImages` according to `images.md:438` and to
nothing at all according to the generated reference, and is the knob that decides how much of the
promise you actually get. Steps 1 and 9 read and then move that column.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node at `10.10.10.180`, built by
[provision](../../strands/lab-topologies.md#provision) and brought to the [node
baseline](../../strands/lab-topologies.md#node-baseline-steps). One node is not a limitation here,
it is the point: the hole the post closes is a hole between two pods on the *same* node, and every
record this exercise reads is a file in that node's kubelet directory. The cluster is at Kubernetes
v1.35, two releases behind the pin and two ahead of the release the post announces, which is exactly
the release where the gate turned on by default. Every command below that touches `/var/lib/kubelet`
runs over `ssh zain@10.10.10.180` with `sudo`; the rest run from wherever your `kubectl` is.

**Do**

1. Establish what the node is running and whether the gate is on, and look for the policy field in
   the kubelet's live configuration. The concept page says the default is
   `NeverVerifyPreloadedImages`; the generated reference gives the field no `Default:` line, unlike
   `registryPullQPS`, `eventRecordQPS` and `eventBurst` around it. Find out whether the kubelet
   reports the value it is using.

   ```sh
   kubectl version
   N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   echo "node: $N"
   kubectl get --raw "/api/v1/nodes/$N/proxy/configz" > /tmp/bw-configz.json
   python3 -m json.tool /tmp/bw-configz.json | grep -i 'imagePull\|serializeImagePulls'
   python3 -m json.tool /tmp/bw-configz.json | grep -i -A 40 'featureGates' | head -50
   ```

2. Ask the node which of the two directory names in `kubelet-files.md:171-172` is real, and count
   what is in it. `pulled` holds one file per image the kubelet pulled itself; `crictl images` holds
   every image the runtime has, however it arrived.

   ```sh
   ssh zain@10.10.10.180
   sudo ls -d /var/lib/kubelet/image_registry /var/lib/kubelet/image_manager 2>&1
   sudo ls -l /var/lib/kubelet/image_manager
   sudo ls /var/lib/kubelet/image_manager/pulled | wc -l
   sudo ls /var/lib/kubelet/image_manager/pulling | wc -l
   sudo crictl images -q | sort -u | wc -l
   ```

3. Scrape the seven metrics no concept page cites, and use one of them to check the count you just
   made by hand. Note the two spellings while you are there.

   ```sh
   kubectl get --raw "/api/v1/nodes/$N/proxy/metrics" > /tmp/bw-metrics.txt
   grep -E '^kubelet_image_?manager' /tmp/bw-metrics.txt
   grep -c '^kubelet_imagemanager' /tmp/bw-metrics.txt
   grep '^kubelet_imagemanager_ondisk_pulledrecords' /tmp/bw-metrics.txt
   grep '^kubelet_image_manager_ensure_image_requests_total' /tmp/bw-metrics.txt
   ```

4. Make a record appear. Remove the house image from the node, then run a pod that needs it, then
   look at the newest file in `pulled`. If the image is in use by another pod, `crictl rmi` will
   refuse; pick a tag nothing on the node is running, or stop the pod that holds it first.

   ```sh
   kubectl create namespace bw-epv
   ssh zain@10.10.10.180 'sudo crictl rmi registry.k8s.io/e2e-test-images/agnhost:2.53; \
     sudo ls /var/lib/kubelet/image_manager/pulled | wc -l'
   kubectl -n bw-epv run puller --image=registry.k8s.io/e2e-test-images/agnhost:2.53 \
     --restart=Never -- /agnhost netexec --http-port=8080
   kubectl -n bw-epv wait --for=condition=Ready pod/puller --timeout=180s
   ssh zain@10.10.10.180 'sudo ls -lt /var/lib/kubelet/image_manager/pulled | head -4; \
     sudo ls /var/lib/kubelet/image_manager/pulled | wc -l'
   ```

5. Check the two filename claims. An intent record survives only while the pull is unfinished, so
   give the kubelet an image it cannot get and the file stays. Then hash both candidate strings for
   the successful pull — the spec you typed and the reference the CRI returned — and see which one
   names the file in `pulled`.

   ```sh
   kubectl -n bw-epv run noimage --image=registry.k8s.io/e2e-test-images/agnhost:0.0.0-bw \
     --restart=Never --command -- sleep 3600
   kubectl -n bw-epv get pod noimage -w   # ctrl-c once it reaches ImagePullBackOff
   ssh zain@10.10.10.180 'sudo ls /var/lib/kubelet/image_manager/pulling'
   printf '%s' 'registry.k8s.io/e2e-test-images/agnhost:0.0.0-bw' | sha256sum
   kubectl -n bw-epv get pod puller -o jsonpath='{.status.containerStatuses[0].imageID}{"\n"}'
   printf '%s' 'registry.k8s.io/e2e-test-images/agnhost:2.53' | sha256sum
   printf '%s' '<the imageID printed above>' | sha256sum
   ```

6. Read a success record. Three things are worth naming before you open it: which `apiVersion` the
   kubelet writes, given that the same type is documented under both `v1alpha1` and `v1beta1`; what
   the `credentialMapping` key looks like against the reference's claim that it is the image field
   with the tag or digest removed; and what `nodePodsAccessible` says for an image pulled with no
   credentials at all.

   ```sh
   ssh zain@10.10.10.180
   R=$(sudo ls -t /var/lib/kubelet/image_manager/pulled | head -1)
   sudo cat "/var/lib/kubelet/image_manager/pulled/$R" | python3 -m json.tool
   sudo cat "/var/lib/kubelet/image_manager/pulled/$R" \
     | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["apiVersion"], d["kind"]); \
       print(list(d["credentialMapping"].keys()))'
   ```

7. Ask whether a tag and a digest for the same image collapse to one key. Run a second pod against
   the digest the CRI reported, then read the same record again and count the keys under
   `credentialMapping`.

   ```sh
   D=$(kubectl -n bw-epv get pod puller -o jsonpath='{.status.containerStatuses[0].imageID}')
   echo "$D"
   kubectl -n bw-epv run bydigest --image="$D" --restart=Never -- /agnhost netexec --http-port=8080
   kubectl -n bw-epv wait --for=condition=Ready pod/bydigest --timeout=180s
   ssh zain@10.10.10.180 'R=$(sudo ls -t /var/lib/kubelet/image_manager/pulled | head -1); \
     sudo cat "/var/lib/kubelet/image_manager/pulled/$R" | python3 -m json.tool'
   ```

8. Put a Secret in the path and see what the record records. `registry.k8s.io` does not require
   credentials, so this is a question the documentation does not answer: when a pod offers a pull
   secret for a registry that does not need one, does the kubelet write the Secret's coordinates
   into the record, fall back to anonymous, or fail the pull? The reference says at
   `kubelet-config.v1beta1.md:2036-2038` that `nodePodsAccessible` being true is mutually exclusive
   with `kubernetesSecrets`, so whichever way it goes, the file has to pick a side.

   ```sh
   kubectl -n bw-epv create secret docker-registry bw-reg \
     --docker-server=registry.k8s.io --docker-username=bw --docker-password=not-a-real-password
   kubectl -n bw-epv get secret bw-reg -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d; echo
   ssh zain@10.10.10.180 'sudo crictl rmi registry.k8s.io/e2e-test-images/agnhost:2.53 || true'
   kubectl -n bw-epv apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: withsecret
   spec:
     imagePullSecrets:
       - name: bw-reg
     containers:
       - name: a
         image: registry.k8s.io/e2e-test-images/agnhost:2.53
         imagePullPolicy: Always
         args: ["netexec", "--http-port=8080"]
         command: ["/agnhost"]
   EOF
   kubectl -n bw-epv describe pod withsecret | tail -20
   ssh zain@10.10.10.180 'R=$(sudo ls -t /var/lib/kubelet/image_manager/pulled | head -1); \
     sudo cat "/var/lib/kubelet/image_manager/pulled/$R" | python3 -m json.tool'
   ```

9. Settle the spelling. Put the concept page's value into the kubelet configuration, restart, and
   read the result; then the configuration reference's value; then a value both pages agree on. Keep
   the backup, and put it back before you leave.

   ```sh
   ssh zain@10.10.10.180
   sudo cp /var/lib/kubelet/config.yaml /var/lib/kubelet/config.yaml.bw
   for V in NeverVerifyAllowListedImages NeverVerifyAllowlistedImages AlwaysVerify; do
     sudo cp /var/lib/kubelet/config.yaml.bw /var/lib/kubelet/config.yaml
     echo "imagePullCredentialsVerificationPolicy: $V" | sudo tee -a /var/lib/kubelet/config.yaml
     sudo systemctl restart kubelet
     sleep 15
     echo "--- $V: $(systemctl is-active kubelet)"
     sudo journalctl -u kubelet --since '1 min ago' --no-pager | grep -i 'verif\|invalid\|error' | tail -5
   done
   sudo cp /var/lib/kubelet/config.yaml.bw /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet && sleep 15 && systemctl is-active kubelet
   ```

10. Count the claims offline, in the pinned checkout, so the numbers in **As it runs now** are yours
    and not mine. Six counts: the width of the verification band inside the concept page, the pages
    under `docs/` that name the gate or the policy, the two spellings of the enum, the two names of
    the records directory, the metric prefixes, and the flags the kubelet reference does not have.

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -c -i verif docs/concepts/containers/images.md
    grep -n -i verif docs/concepts/containers/images.md | sed -n '1p;$p'
    wc -l docs/concepts/containers/images.md
    grep -rln --include='*.md' 'KubeletEnsureSecretPulledImages\|imagePullCredentialsVerificationPolicy' docs/ \
      | grep -v command-line-tools-reference/kube
    grep -n 'NeverVerifyAllow' docs/concepts/containers/images.md \
      docs/reference/config-api/kubelet-config.v1beta1.md
    grep -n 'image_registry\|image_manager' docs/reference/node/kubelet-files.md
    grep -c '^kubelet_imagemanager\|kubelet_image_manager' docs/reference/instrumentation/metrics.md
    grep -c -i 'VerificationPolicy' docs/reference/command-line-tools-reference/kubelet.md
    ```

**Expect**

Step 1 should report a v1.35 server. `configz` renders the kubelet's live configuration, so the
interesting question is not whether the gate is listed — on 1.35 it is on by default and a
default-valued gate may not appear under `featureGates` at all — but whether
`imagePullCredentialsVerificationPolicy` appears with a value. If it does, write the value down and
check it against `images.md:438`. If it does not appear, you have found the practical cost of the
missing `Default:` line in the generated reference: the concept page is the only place in the pinned
tree that will tell you what policy your node is enforcing, and it tells you in prose.

Step 2 should find `/var/lib/kubelet/image_manager` and no `/var/lib/kubelet/image_registry`, which
makes `kubelet-files.md:171` the wrong half of its own sentence. Expect `pulling` to be empty or
nearly so — intents are short-lived — and `pulled` to hold fewer files than `crictl images -q`
returns, because the node's images were on it before the gate was ever enabled and, per
`images.md:455-460`, the kubelet has no record of those. Record both numbers; their difference is
the set that `NeverVerifyPreloadedImages` exempts on this node. If `image_registry` is the one that
exists, the disagreement resolves the other way and the rest of this exercise needs its paths
rewritten — say so in your notes rather than quietly adjusting.

Step 3 should print seven metric families and confirm that six of them use `kubelet_imagemanager_`
and one uses `kubelet_image_manager_`. Expect `kubelet_imagemanager_ondisk_pulledrecords` to equal
the file count from step 2; if it does not, the likeliest reason is that the gauge is sampled rather
than live, so re-read it after step 4 and see whether it catches up.
`kubelet_image_manager_ensure_image_requests_total` carries the labels `present_locally`,
`pull_policy` and `pull_required`, which is the whole decision this feature makes, exposed as three
label values — note the current counts before step 4 so you can watch the `pull_required="true"`
series move.

Step 4 should show one more file in `pulled` after the pod is ready than before it. If `crictl rmi`
refuses because the image is in use, that is the cluster telling you the house image is running
somewhere; either name a pod to delete first or accept that the record already exists and skip to
reading it. If the count does not change but the pod starts, the image was never actually removed —
check `crictl images` between the two commands rather than trusting `rmi` to have done anything.

Step 5 should give you a clean split. The `pulling` filename should equal the SHA-256 of the literal
string `registry.k8s.io/e2e-test-images/agnhost:0.0.0-bw`, because
`kubelet-config.v1beta1.md:403-405` says the intent hashes the container's image field. The `pulled`
filename should equal the SHA-256 of the `imageID` the pod status reports, not of the tag you typed,
because `:440-443` says the success record hashes the CRI's reference. Expect the `imageID` to be a
digest-bearing string; if your runtime reports it with a `docker-pullable://` prefix, hash both with
and without the prefix before concluding anything. If the intent file is gone by the time you look,
the pull failed fast and the kubelet cleaned up — recreate the pod and look sooner.

Step 6 should return valid JSON with `kind: ImagePulledRecord`. The `apiVersion` is the answer to a
question neither reference page asks: both `v1alpha1` and `v1beta1` document this type identically,
and only the file says which one is written. Expect exactly one key under `credentialMapping`, and
expect it to be `registry.k8s.io/e2e-test-images/agnhost` with no tag, matching `:452-453`. Expect
`nodePodsAccessible: true`, because the pull needed no credentials and `:2036-2037` says that flag
covers both the node-wide case and the no-credentials case — which means the record cannot tell you
which of the two it was.

Step 7 should leave one key, not two. The digest pod and the tag pod name the same image by two
strings that both reduce to `registry.k8s.io/e2e-test-images/agnhost` once the tag and digest are
stripped, so if a second key appears the stripping is less thorough than `:452-453` claims and that
is worth writing down with both key strings copied out. Expect no second file in `pulled` either:
same `imageRef` from the CRI, same filename hash. If `kubectl run` rejects the digest form, fall
back to a manifest rather than fighting the flag.

Step 8 is the step with no documented answer, so record whatever happens rather than predicting it.
The three outcomes worth distinguishing: the record grows a `kubernetesSecrets` entry with `uid`,
`namespace`, `name` and `credentialHash` and `nodePodsAccessible` flips to false; or the record
keeps `nodePodsAccessible: true` and the Secret leaves no trace, meaning the kubelet fell back to
anonymous and the credential you supplied was never what authorised anything; or the pull fails
outright with a 401 and the pod sits in `ImagePullBackOff`, meaning `registry.k8s.io` rejects bad
basic auth rather than ignoring it. `images.md:368-369` and `:384-386` say the kubelet tries every
credential it finds and falls through on failure, which argues for the second, but that text is
about `config.json` paths and not about this. Whichever you get, the `credentialHash` — if one
appears — is a SHA-256 of the Secret's content per `:2094-2099`, so you can check it against the
base64 you decoded.

Step 9 settles the spelling and should produce three distinguishable results. Expect exactly one of
`NeverVerifyAllowListedImages` and `NeverVerifyAllowlistedImages` to leave `systemctl is-active
kubelet` reporting `active`, and the other to fail the kubelet's configuration validation with a
message naming the field. `AlwaysVerify` is the control: both pages spell it the same way, so if it
also fails you have a syntax problem in how the line was appended, not a documentation defect. Note
that a kubelet that refuses its configuration does not roll back — the node goes `NotReady` and
stays there until you restore the file, which is why the backup is taken before the loop and
restored after it. If all three are accepted, check whether the kubelet is reading
`/var/lib/kubelet/config.yaml` at all on this node before concluding the enum is permissive.

Step 10 should reproduce the counts in **As it runs now** exactly: fourteen lines matching *verif*
in a 589-line `images.md`, the first at `:413` and the last at `:449`; four pages under `docs/` once
the generated component references are filtered out; the two spellings on the two lines named; both
directory names inside `kubelet-files.md`; seven metric lines; and zero occurrences of
`VerificationPolicy` in the kubelet flag reference. Any count that differs means the pin moved under
you — check the commit before assuming the prose is wrong.

**Read on**

11. [Mounting an OCI artifact as a read-only volume](../2024/07-image-volume-source.md) — the
    `image` volume source, and the open question this exercise hands it: whether credential
    verification applies to an image mounted that way, which `images.md:444-445` does not say.

12. [Turning an admission plugin on and off under a running API
    server](../../labs/03/13-toggle-a-built-in-plugin.md) — `AlwaysPullImages` is the workaround
    this post says was the only way, and the lab makes you watch it rewrite a field you set.

13. [Where PullImage falls in the sequence that starts one
    pod](../../labs/06/02-one-pod-is-how-many-cri-calls.md) — `PullImage` is the call this whole
    feature wraps, and the lab makes you predict the sequence before you count it.

14. [Where the images actually live, when that is not the node's root
    filesystem](../2024/01-kubernetes-separate-image-filesystem.md) — the image filesystem, its
    split, and the garbage collection that can remove an image out from under a record this exercise
    just read.

15. [Reading a Secret's bytes off the disk they are stored
    on](../../labs/10/12-a-secret-that-is-no-longer-plaintext-on-disk.md) — the `credentialHash` in
    a pull record is a hash of one of these, and encryption at rest changes what is on disk without
    changing what the kubelet is handed.

**Teardown**

```sh
kubectl delete namespace bw-epv --ignore-not-found
rm -f /tmp/bw-configz.json /tmp/bw-metrics.txt
ssh zain@10.10.10.180 'sudo diff /var/lib/kubelet/config.yaml.bw /var/lib/kubelet/config.yaml \
  && sudo rm -f /var/lib/kubelet/config.yaml.bw; systemctl is-active kubelet'
kubectl get nodes
```

The pull records are deliberately left in place: they are the node's, not this exercise's, and
deleting the directory resets every image on the node to pre-pulled, which `images.md:465-467` warns
about and which is not a state to leave a shared cluster in. If you want the node back exactly as it
was, remove only the records for the images you pulled, by the filenames step 5 taught you to
compute.
