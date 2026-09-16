<a id="registry-k8s-io-faster-cheaper-ga"></a>

# The name this post retired has zero occurrences in the documentation tree and still answers on the wire, serving a v1.35 image by identical digest out of a registry frozen in 2023, while the three escape hatches the post offered for keeping it have each decayed in a different way

**Post** — [registry.k8s.io: faster, cheaper and Generally Available (GA)](https://kubernetes.io/blog/2022/11/28/registry-k8s-io-faster-cheaper-ga/),
2022-11-28.

6,881 bytes, 92 lines, two authors: Adolfo García Veytia of Chainguard and Bob Killen of Google.
Eleventh of 2022's thirteen `walk` verdicts and sixth-shortest of them. Four years on, the name it
introduces occurs 99 times across 47 files under `content/en/docs` and the name it retires occurs
zero times anywhere in that tree, which is the most complete absorption this year records. It is
also one of four posts in an archive of 765 that carry a `<del>`, and the only one of the four whose
strikethrough puts something back in place of what it strikes.

**As written**

One sentence of announcement and one of architecture, `:11`: starting with Kubernetes 1.25 the
container image registry has changed from `k8s.gcr.io` to `registry.k8s.io`, and the new registry
spreads the load across multiple Cloud Providers & Regions, *functioning as a sort of content
delivery network (CDN) for Kubernetes container images*. The TL;DR is three bullets, `:15-17`.
Releases from `1.25` — struck through, and followed by `1.27` — onward are not published to the old
registry. The December patch releases will backport the new default to every branch still in
support, 1.22, 1.23 and 1.24. And if you run in a restricted environment with domain or IP policies
limited to the old name, *the image pulls will not function*; for those users the recommendation is
to mirror the release images to a private registry.

The reasoning is money and ownership, `:23`. The old name is a custom Google Container Registry
domain set up solely for the Kubernetes project; other providers now want to host images too; Google
recommitted three million dollars and Amazon announced a matching donation at KubeCon NA 2022 in
Detroit. `:25-31` answers the question that follows from that — why there is no stable list of
addresses to allow. The new name is a *secure blob redirector* that connects clients to the closest
cloud provider, the set of backends is expected to keep changing, and restrictive control mechanisms
like man-in-the-middle proxies or network policies that restrict access to a specific list of
IPs/domains will break with this change.

`:33-41` is what failure looks like: a container failing to be created with the warning
`FailedCreatePodSandBox`, and a worked example of a proxied deployment failing on an unknown
certificate. The example at `:40` names `us-west1-docker.pkg.dev` and a manifest path ending
`pause/manifests/3.8` — a Google Artifact Registry host, in the post that announces the load being
spread to Amazon. Then `:43-79` is the way back, under a precondition stated once at `:45`: you can
revert to the old domain name for cluster versions less than 1.25. Three mechanisms follow. `kubeadm
init --image-repository=k8s.gcr.io` at `:50-54`; a three-line `ClusterConfiguration` in
`kubeadm.k8s.io/v1beta3` at `:58-62`; and for the kubelet, `:64-79`, either configure the container
runtime — three links, to the containerd, CRI-O and cri-dockerd override sections — or set
`--pod-infra-container-image`, with a dockershim example for clusters before v1.23.

Two things in the file were not written on the day. `:81-84` is a whole section, *Legacy container
registry freeze*, whose heading carries a hand-written anchor and whose entire body is a pointer to
a post published fourteen months later. `:92` is a one-line italic stamp: *This article was updated
on the 28th of February 2023.* What is not there is the connection between them. The stamp says the
article was updated and gives a date; the strikethrough says which two characters changed; nothing
in the file says why, and the reason is in a different post.

**As it runs now**

The subject landed, completely. Step 7 counts it: `k8s.gcr.io` occurs zero times in
`content/en/docs`, and `registry.k8s.io` occurs 99 times across 47 files. Outside `docs` the old
name survives 62 times in 17 files, and every one of those 17 is a blog post — no reference page, no
task, no concept page, no file under `examples` names it. The 17 span 2019 to 2026, and the last of
them uses the name in the past tense, narrating the 2018 origin of the image promoter. There is
nothing left in the maintained tree for a reader to copy the old name out of.

The name still answers. Step 3 asks it directly: `https://k8s.gcr.io/v2/` returns **302** with
`Location: https://registry.k8s.io/v2/`, and a manifest request for `kube-apiserver:v1.35.0` — the
release the lab runs, and an image that did not exist when the legacy registry was frozen on 3 April
2023 — comes back through the old name with a digest identical to the one the new name serves. The
freeze froze a *registry*; the *name* was pointed at a different one, and a blind redirect has no
opinion about which images predate it. The redirect notice said the old name **WILL** be phased out
entirely in the future (`blog/_posts/2023/image-registry-change.md:174`). That sentence is three and
a half years old at the pin and the redirect is still there.

All three ways back have decayed, and no two of them the same way. The flag survives and its default
inverted: `--image-repository` appears in 13 generated help pages under
`reference/setup-tools/kubeadm`, and all 13 print `Default: "registry.k8s.io"`, so the escape hatch
the post offers is the flag whose unset value is the thing the post was announcing. The config file
lost its version: the snippet at `:59-61` is `kubeadm.k8s.io/v1beta3`, and
`kubeadm_config_migrate.md:21-22` lists exactly one supported API version, `kubeadm.k8s.io/v1beta4`.
The kubelet flag lost its binary: `--pod-infra-container-image` occurs once in the whole
documentation tree, at `container-runtimes.md:340`, and that occurrence is under *Docker Engine*,
describing an argument the `cri-dockerd` adapter accepts. It is not documented as a kubelet flag
anywhere at the pin.

The pin disagrees with itself about the second of those. `kubeadm_config_migrate.md:24` says kubeadm
can only write out config of version `kubeadm.k8s.io/v1beta4`, *but read both types* — two lines
after a list that contains one type. The sentence is a leftover from when there were two, and it is
the only thing at the pin that suggests the post's snippet might still be readable; step 6 settles
it against the binary rather than against the page. The index has the same lag:
`reference/_index.md:100-101` offers v1beta3 and v1beta4 side by side under *Config API for
kubeadm*. Two documentation files name v1beta3 at the pin against twenty for v1beta4, and one of the
two is the v1beta3 page itself.

The three links in the kubelet section all still resolve, which is rarer than it sounds and worse
than a 404 here. `container-runtimes.md:252` is `{#override-pause-image-containerd}` and its worked
example at `:259` is `sandbox_image = "registry.k8s.io/pause:3.10"`. `:294` is
`{#override-pause-image-cri-o}` and its example at `:301` is
`pause_image="registry.k8s.io/pause:3.10"`. `:336` is `{#override-pause-image-cri-dockerd-mcr}`, the
one that still names the flag. The mechanism each section documents is the one the post sent you
there for; the value each section hands you is the host the post was showing you how to avoid. A
reader who follows the link and copies the block has done the opposite of what the link was for.

And the precondition on the whole revert section excludes every cluster the pin describes. `:45`
offers the way back *for cluster versions less than 1.25*. The lab runs 1.35 and the newest release
at the pin is 1.37. Read literally, the post's own instructions have not applied to a supported
cluster for years — which is the correct outcome, and is also why the section survives unread rather
than being removed.

**What this exercise does not cover, and where it lives**

The sandbox image itself is already walked. [The containerd
exercise](../2017/08-containerd-container-runtime-options-kubernetes.md) reads `sandbox_image` out
of `/etc/containerd/config.toml` at its step 5 and finds the pause container in the runtime's own
lists at its step 9, and it is the file that owns what the pause container is for. Step 2 here asks
a narrower question of the same node and never opens the config: of the images the runtime is
holding, how many distinct hosts do their names begin with, and is the old one among them.

Mirroring is the post's own recommendation, twice — `:17` for restricted environments and `:29` for
anyone who needs a fixed set of addresses — and it is out of reach here. No topology in
`strands/lab-topologies.md` carries a registry and nothing in `labs/` builds one. A pull-through
cache is a second service with its own storage, its own TLS and its own failure modes, and standing
one up would make it the subject rather than the evidence. What this exercise can show is the thing
mirroring is a response to: that the address a pull ends at is not the address the manifest names.

The package-repository migration that followed this one, and container image signing, are later
years' ground and later years' rows own them. The two 2023 notices that continue this story — the
freeze announcement and the redirect announcement — are marked `read` in their own year's census
with their coverage delegated here, so they appear in this file as evidence and do not get exercises
of their own. Steps 9 and 10 read them; the census rows that point here are the reason it is
reasonable to.

**The diff, and why**

**Still right, and almost alone in being so.** The post's one instruction to everybody — stop naming
the old host — was carried out to the last occurrence, and step 7 is the receipt. Zero in `docs`,
zero under `examples`, and the 17 survivors all in an archive nobody edits. That is the cleanest
absorption in this year's thirteen posts, and it is worth saying plainly because everything else in
the post decayed. A reader told only that the post still holds would go on to read the revert
section and find three instructions, none of which works as written.

**Wrong when it was published, and corrected in place.** `:15` said container images for Kubernetes
releases from 1.25 onward are not published to `k8s.gcr.io`. The freeze notice contradicts it out of
its own bullets: `:32` says that starting in 1.25 the *default* image registry has been set to
`registry.k8s.io`, and `:46` says the last 1.25 release on `k8s.gcr.io` will be 1.25.8 — a sentence
with no meaning unless 1.25 releases were published there. The post had confused the release in
which the default changed with the release after which publication stopped, and three months later
the project struck the number and wrote the right one beside it. Of the four posts in 765 that carry
a `<del>`, three strike a thing that expired — an event registration, a survey link twice — and the
fourth strikes a forecast and puts nothing back. This is the only one that corrects.

**Overtaken by stasis.** The redirect was announced as a stopgap with an explicit end: it will
enable the project to take advantage of the new resources, and the old name will be phased out
entirely in the future. Step 3 measures the future. Three and a half years on the 302 is still
served, still unconditional, and still fronting an image the frozen registry never held. The stopgap
is now the compatibility layer that lets every unmaintained manifest in the 17 surviving posts keep
working, which is exactly the thing that removes the pressure to withdraw it. Nothing about this is
a mistake; it is what happens when a redirect is cheaper to keep than to argue about.

**Never absorbed.** The revert section is three instructions and the pin kept none of them intact.
The flag is the only survivor and it survives with the opposite default. The config snippet names an
API version kubeadm no longer lists as supported, offered from an index page that still links it.
The kubelet flag is not a kubelet flag any more. What makes this more than ordinary rot is that the
post is still the page a search engine returns for *how do I go back to k8s.gcr.io*, and all three
of its answers now fail in different places — one silently does the wrong thing, one is rejected by
a binary, and one names a flag that is not there.

**No gate**

There is no feature gate for an image registry and there could not be one. A gate is compiled into a
binary and read at start-up; the host a manifest names is a string in the manifest, and no component
has a switch for it. The pin offers no dating instrument for this change at all — no `feature-state`
shortcode, no file in the feature-gates directory, no version in any reference page — because the
change never entered the API. The nearest thing to a version is the number the post itself got wrong
at `:15`.

So the instruments here are two, and they disagree. The first is the generated kubeadm help text:
the `Default:` column of those 13 pages is the only place in the documentation tree where the switch
is machine-readable, and what it records is that the new name won. The second is the wire, and step
3 is the only step here that has to leave both the checkout and the cluster to get an answer. The
tree cannot tell you what the old name does, because the old name is not in the tree; the silence
reads as *gone* and the wire says *302*. Where those two disagree, believe the wire, and note which
one a reader auditing manifests against the documentation would have consulted.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 cores, at `10.10.10.180`,
running v1.35. Nothing in this exercise depends on the release; what it depends on is that the node
can reach the internet, because the whole question is which host it reaches. Steps 1, 4 and 5 are
`kubectl` against the apiserver, in a namespace called `reg`. Steps 2, 3 and 6 need a shell on the
node — `ssh zain@10.10.10.180` — for the runtime's image store, for `curl` from the place the pulls
actually happen, and for `kubeadm`. Steps 7 to 10 need no cluster; they read the pinned checkout.

**Do**

1. Take the inventory the post's own follow-ups tell you to take. The one-liner is copied from
   `blog/_posts/2023/image-registry-change.md:96-101`, where it is Option 1 for finding images that
   still name the old host.

   ```sh
   kubectl get pods --all-namespaces -o jsonpath="{.items[*].spec.containers[*].image}" \
     | tr -s '[[:space:]]' '\n' | sort | uniq -c
   ssh zain@10.10.10.180 'kubeadm config images list'
   kubectl create ns reg
   ```

Read the second list against the first. One of them is what the cluster is running and the other is
what `kubeadm` would pull today if you asked it, and the interesting column is the host, not the
tag.

2. Ask the node what it is holding, by host. `-q` prints one reference per line, including bare
   digests for content with no name, so the `grep` keeps only the named ones and the `sed` throws
   away everything after the first slash.

   ```sh
   ssh zain@10.10.10.180 \
     "sudo ctr -n k8s.io images list -q | grep '/' | sed 's|/.*||' | sort | uniq -c"
   ```

Record the number of distinct hosts and whether `k8s.gcr.io` is one of them. This is the baseline;
step 4 changes it.

3. Now ask the old name whether it is still there. Run this from the node, not from your laptop: the
   question is what the machine that pulls images can reach.

   ```sh
   ssh zain@10.10.10.180 bash -s <<'SH'
   A='application/vnd.oci.image.index.v1+json,application/vnd.docker.distribution.manifest.list.v2+json'
   curl -sS -o /dev/null -w 'old /v2/   %{http_code} -> %{redirect_url}\n' --max-time 10 https://k8s.gcr.io/v2/
   curl -sS -o /dev/null -w 'new /v2/   %{http_code}\n' --max-time 10 https://registry.k8s.io/v2/
   for tag in v1.26.3 v1.35.0; do
     for h in k8s.gcr.io registry.k8s.io; do
       printf '%-9s %-16s %s\n' "$tag" "$h" \
         "$(curl -sSL -D - -o /dev/null --max-time 15 -H "Accept: $A" \
             "https://$h/v2/kube-apiserver/manifests/$tag" \
            | tr -d '\r' | awk -F': ' 'tolower($1)=="docker-content-digest"{print $2}')"
     done
   done
   SH
   ```

`v1.26.3` is the last 1.26 image the freeze notice says reached the old registry
(`blog/_posts/2023/k8s-gcr-io-freeze-announcement.md:47`). `v1.35.0` is the release this node runs,
published years after the freeze. Compare the four digests before reading the next step.

4. Pull through the old name for real, and watch the node's inventory change.

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata:
     name: old-name
     namespace: reg
   spec:
     containers:
     - name: pause
       image: k8s.gcr.io/pause:3.10
   YAML
   kubectl -n reg wait --for=condition=Ready pod/old-name --timeout=120s; echo "wait exit $?"
   kubectl -n reg get pod old-name -o wide
   ssh zain@10.10.10.180 "sudo ctr -n k8s.io images list | grep pause"
   ```

The pod is a `pause` binary and nothing else, so *Ready* is the whole test: it means the image
arrived. Note what the last command now shows that step 2 did not.

5. Break it deliberately, and see which host the cluster names when it complains. `0.0.0` is not a
   tag that exists on either registry.

   ```sh
   kubectl -n reg run absent --image=k8s.gcr.io/pause:0.0.0 --restart=Never
   kubectl -n reg wait --for=condition=Ready pod/absent --timeout=60s; echo "wait exit $?"
   kubectl -n reg get pod absent
   kubectl -n reg get events --field-selector involvedObject.name=absent \
     -o custom-columns=REASON:.reason,MESSAGE:.message | tail -4
   kubectl -n reg get pod absent -o jsonpath='{.spec.containers[0].image}{"\n"}'
   kubectl -n reg get pod old-name -o jsonpath='{.status.containerStatuses[0].imageID}{"\n"}'
   ```

Two questions. Whether the failure message names the host you asked for or the host you were sent to
— and whether the `imageID` of the pod that *succeeded* names the host you asked for. Then say which
field an audit should be reading.

6. Hand `kubeadm` the post's own config snippet, unchanged, and hand it the post's own flag.

   ```sh
   ssh zain@10.10.10.180 bash -s <<'SH'
   cat > /tmp/old-config.yaml <<'YAML'
   apiVersion: kubeadm.k8s.io/v1beta3
   kind: ClusterConfiguration
   imageRepository: "k8s.gcr.io"
   YAML
   kubeadm config migrate --old-config /tmp/old-config.yaml; echo "migrate exit $?"
   kubeadm config images list --image-repository=k8s.gcr.io | head -3
   SH
   ```

One of these two is the post being right and the other is the post being stale, and the page at
`kubeadm_config_migrate.md:24` will have told you to expect the opposite of whichever you get.

7. Offline from here. Count the two names across the whole of the pinned tree.

   ```sh
   cd /path/to/kubernetes/website/content/en
   printf 'old in docs          %s\n' \
     "$(grep -ro 'k8s\.gcr\.io' --include='*.md' docs | wc -l | tr -d ' ')"
   printf 'new in docs          %s across %s files\n' \
     "$(grep -ro 'registry\.k8s\.io' --include='*.md' docs | wc -l | tr -d ' ')" \
     "$(grep -rl 'registry\.k8s\.io' --include='*.md' docs | wc -l | tr -d ' ')"
   printf 'old in content/en    %s across %s files\n' \
     "$(grep -ro 'k8s\.gcr\.io' --include='*.md' . | wc -l | tr -d ' ')" \
     "$(grep -rl 'k8s\.gcr\.io' --include='*.md' . | wc -l | tr -d ' ')"
   printf 'old outside blog     %s\n' \
     "$(grep -rl 'k8s\.gcr\.io' --include='*.md' . | grep -v '/blog/' | wc -l | tr -d ' ')"
   printf 'old in examples      %s\n' \
     "$(grep -rl 'k8s\.gcr\.io' examples | wc -l | tr -d ' ')"
   grep -rl 'k8s\.gcr\.io' --include='*.md' . \
     | sed 's|.*/_posts/||; s|/.*||' | sort | uniq -c | sed 's/^ */  /'
   ```

8. Put the strikethrough in proportion. Two counts and five lines.

   ```sh
   printf 'posts          %s\n' "$(find blog/_posts -name '*.md' | wc -l | tr -d ' ')"
   printf 'with <del>     %s\n' \
     "$(grep -rl '<del>' --include='*.md' blog/_posts | wc -l | tr -d ' ')"
   printf 'with a stamp   %s\n' \
     "$(grep -ril 'this article was updated\|this post was updated\|this blog was updated\|this article was revised\|this post was revised' --include='*.md' blog/_posts | wc -l | tr -d ' ')"
   grep -rn '<del>' --include='*.md' blog/_posts | sed 's|blog/_posts/||' | cut -c1-92
   ```

The second count depends entirely on its pattern, so the pattern is written out in full rather than
summarised. A looser one — editor's notes, `Update:` lines and bolded update headings — matches 59
posts and means several different things.

9. Read the correction, and then read what did not receive it.

   ```sh
   cd blog/_posts
   echo '--- the sentence that was corrected, and the stamp ---'
   sed -n '15p;92p' 2022/registry-k8s-io-change.md | cut -c1-104
   echo '--- what the freeze notice says ---'
   sed -n '28p;32p;46p' 2023/k8s-gcr-io-freeze-announcement.md
   echo '--- what the redirect notice still says ---'
   sed -n '158,159p' 2023/image-registry-change.md
   ```

10. The three ways back, in the order the post gives them.

    ```sh
    cd /path/to/kubernetes/website/content/en/docs
    echo '--- 1. kubeadm init --image-repository ---'
    printf 'files      %s\n' \
      "$(grep -rl --include='*.md' -e '--image-repository' . | wc -l | tr -d ' ')"
    grep -rho --include='*.md' -e '--image-repository string[^<]*' . \
      | sed 's/&nbsp;/ /g' | sort -u
    echo '--- 2. kubeadm ClusterConfiguration v1beta3 ---'
    sed -n '21,24p' reference/setup-tools/kubeadm/generated/kubeadm_config/kubeadm_config_migrate.md
    printf 'v1beta3 in %s docs files, v1beta4 in %s\n' \
      "$(grep -rl --include='*.md' -e 'kubeadm.k8s.io/v1beta3' -e 'kubeadm-config.v1beta3' . | wc -l | tr -d ' ')" \
      "$(grep -rl --include='*.md' -e 'kubeadm.k8s.io/v1beta4' -e 'kubeadm-config.v1beta4' . | wc -l | tr -d ' ')"
    echo '--- 3. kubelet --pod-infra-container-image ---'
    grep -rn --include='*.md' -e '--pod-infra-container-image' . | sed 's|^\./||'
    ```

**Expect**

Step 1 should produce two lists that agree on the host and disagree on everything else. Every
reference `kubeadm config images list` prints begins `registry.k8s.io/`, because that has been the
compiled-in default since 1.25 and step 10 finds the help text saying so. The running-pod inventory
adds whatever the CNI brought with it — on `solo` that is flannel, from `docker.io` or `ghcr.io`
depending on how it was installed — and the number this step is really asking for is the count of
references beginning `k8s.gcr.io`, which is zero.

Step 2 prints a short histogram, two or three hosts, and `k8s.gcr.io` is not one of them. That is
the baseline, and it is also the honest state of a cluster built from the pinned documentation:
nothing in the tree could have put the old name there.

Step 3 is the measurement the checkout cannot make. Run on 2026-09-16 it gave:

```
old /v2/   302 -> https://registry.k8s.io/v2/
new /v2/   401
v1.26.3   k8s.gcr.io       sha256:b8dda58b0c680898b6ab7fdbd035a75065d3607a70c3c4986bc1d8cfba5f0ec8
v1.26.3   registry.k8s.io  sha256:b8dda58b0c680898b6ab7fdbd035a75065d3607a70c3c4986bc1d8cfba5f0ec8
v1.35.0   k8s.gcr.io       sha256:32f98b308862e1cf98c900927d84630fb86a836a480f02752a779eb85c1489f3
v1.35.0   registry.k8s.io  sha256:32f98b308862e1cf98c900927d84630fb86a836a480f02752a779eb85c1489f3
```

Four digests and two distinct values, paired by tag and not by host. The `401` is not a failure: an
unauthenticated `GET /v2/` on the new name gets the registry's authentication challenge, which is
what a client is supposed to receive, while the old name never gets that far because it answers 302
first. The line that matters is the last pair. `v1.35.0` is a Kubernetes release from long after 3
April 2023, the date the legacy registry stopped receiving images, and the old name serves it with
the same digest as the new one — because the old name is not a registry any more, it is a redirect,
and a redirect cannot know that the thing behind it used to be frozen. If your run differs, that is
the exercise rather than a broken step: the notice quoted above promised this would stop working,
and the date it stops is the only fact in this file that the pin cannot hold.

Step 4 goes Ready. The pull follows the 302, and `ctr` now lists `k8s.gcr.io/pause:3.10` beside
`registry.k8s.io/pause:3.10` — the sandbox image the runtime was already using, named at
`container-runtimes.md:259` — with the same digest in both rows. Nothing was downloaded twice.
containerd stores content by digest, so what the second row adds is a name, not an image. The node
now holds one blob under two hostnames, which is a small and exact picture of why the redirect is
cheap to keep and why nobody notices they are still using it.

Step 5 goes `ErrImagePull` and then `ImagePullBackOff`, and the message is the part to write down
rather than the part to predict — which host it names depends on the runtime and on where in the
pull the failure happened, and this repository cannot settle it for you. What does not depend on
anything is the pair of jsonpaths. `.spec.containers[0].image` is the string you wrote, `k8s.gcr.io`
and all, and it is the same field the post's follow-ups read in every one of their five options for
finding stragglers. `.status.containerStatuses[0].imageID` on the pod from step 4 names where the
bytes actually came from, and it is the only field in the cluster that does. An audit that greps
runtime logs for the old host is reading the one place the answer is not guaranteed.

Step 6 splits. The second command always succeeds: `--image-repository` takes an arbitrary string,
so `kubeadm config images list --image-repository=k8s.gcr.io` prints a full set of references to a
host that exists only as a redirect, four years after the post that offered the flag as a way back.
The first command is the one worth running twice — whatever `kubeadm config migrate` does with a
`v1beta3` document, `kubeadm_config_migrate.md:24` told you to expect the other thing, because its
*read both types* is a sentence left over from a release when there were two types to read. Report
the exit status and say which of the page and the binary you would cite in a runbook.

Step 7 prints the absorption:

```
old in docs          0
new in docs          99 across 47 files
old in content/en    62 across 17 files
old outside blog     0
old in examples      0
  2 2019
  1 2020
  1 2021
  6 2022
  6 2023
  1 2026
```

Zero and ninety-nine is the whole argument for the *still right* case. The per-year tail is the
argument for the other three: six of the seventeen are from 2022 and six from 2023, the two years
the migration was live, and the 2026 entry uses the name in the past tense about 2018. The old
hostname now exists in the project's own writing only as history and only in the one directory that
is never revised.

Step 8 puts the correction in proportion:

```
posts          765
with <del>     4
with a stamp   3
2022/registry-k8s-io-change.md:15:* Container images for Kubernetes releases from <del>1.25<
2017/autoscaling-in-kubernetes.md:18:<del><a href="https://www.eventbrite.com/e/kubecon-clou
2021/are-you-ready-for-dockershim-removal/index.md:28:<del>Please fill out this survey: http
2021/are-you-ready-for-dockershim-removal/index.md:50:<del>We are collecting opinions throug
2020/dont-panic-kubernetes-and-docker.md:52:When Docker runtime support is removed in a futu
```

Five strikethroughs in four files out of 765. Three of the five withdraw an invitation that expired
— a conference registration and a survey link twice. The fourth, in the dockershim post, strikes a
forecast — *currently planned for the 1.22 release in late 2021* — and puts nothing in its place,
which was the right call, since the removal landed in 1.24 and a replacement number would have been
wrong again. The fifth is this post, and it is the only one in the archive that strikes a value and
writes the correct one beside it. Three posts also carry a dated italic stamp saying they were
edited; this is the only file that is in both counts.

Step 9 shows the correction and the two things that did not receive it:

```
--- the sentence that was corrected, and the stamp ---
* Container images for Kubernetes releases from <del>1.25</del> 1.27 onward are not published to k8s.gcr
_This article was updated on the 28th of February 2023._
--- what the freeze notice says ---
- 1.27 Kubernetes release will not be published to the old registry.
- Starting in 1.25, the default image registry has been set to `registry.k8s.io`.
- The last 1.25 release on `k8s.gcr.io` will be 1.25.8
--- what the redirect notice still says ---
The project switched to [registry.k8s.io last year with the 1.25
release](https://kubernetes.io/blog/2022/11/28/registry-k8s-io-faster-cheaper-ga/); however, most of
```

The freeze notice holds both halves of the distinction the original sentence collapsed: 1.25 is
where the *default* moved, 1.27 is where *publication* stopped, and 1.25.8 is proof that 1.25
releases were published to the old registry after the default changed. The redirect notice, written
ten days after the correction and linking straight to the corrected post, still says the project
switched with the 1.25 release. That sentence is defensible — it is about the default — but it is
the same phrasing that produced the error, reused by a different set of authors in a post that
points at the fix. Editing one file does not edit the sentence pattern.

Step 10 prints the three ways back:

```
--- 1. kubeadm init --image-repository ---
files      13
--image-repository string     Default: "registry.k8s.io"
--- 2. kubeadm ClusterConfiguration v1beta3 ---
In this version of kubeadm, the following API versions are supported:
- kubeadm.k8s.io/v1beta4

Further, kubeadm can only write out config of version "kubeadm.k8s.io/v1beta4", but read both types.
v1beta3 in 2 docs files, v1beta4 in 20
--- 3. kubelet --pod-infra-container-image ---
setup/production-environment/container-runtimes.md:340:The command line argument to use is `--pod-infra-container-image`.
```

Thirteen pages, one distinct default line, and the default is the new host — the flag is healthy and
its purpose has inverted. One supported API version, listed two lines above a sentence promising to
read two, and the deprecated one still offered from the index at `reference/_index.md:100`. And a
single line for the kubelet flag, in a section about the `cri-dockerd` adapter, which is the
component that replaced the thing the post's last example was written for. Three instructions, three
different kinds of decay, and a reader following any of them today would find out in three different
places.

**Read on**

1. The two override sections the post links, `container-runtimes.md:252-260` and `:294-302`, read as
   the post's reader would have read them. Both anchors still resolve; both worked examples hardcode
   `registry.k8s.io/pause:3.10`. Then `:336-340`, the third link, which is the only one of the three
   that still names `--pod-infra-container-image` — and which does it for an adapter, not for the
   kubelet. Work out from these three what a link check would have to test to catch this, and why no
   link checker does.

2. `kubeadm_config_migrate.md:19-24` and `reference/_index.md:98-101` together. The first is
   generated from the binary's help text and lists one supported API version while promising to read
   two; the second is a hand-kept index offering both. Step 6 asked the binary. Decide which of the
   three sources you would trust for a claim about what a tool accepts, and note that the one that
   is generated is also the one with the stale sentence in it.

3. The two 2023 notices in full, in the order they were published:
   `blog/_posts/2023/k8s-gcr-io-freeze-announcement.md`, whose `:44-47` is a table of last images by
   branch, and `blog/_posts/2023/image-registry-change.md`, whose `:91-137` is five ways to find
   manifests that still name the old host. Both are `read` in their year's census and both delegate
   here. The fifth of those five options is a mutating webhook that rewrites the image field,
   offered as a **LAST** possible option at `:132-137`, and it is worth reading beside step 5: it is
   the only one of the five that does not read `.spec.containers[*].image` but writes it.

4. The sample output at `image-registry-change.md:53-57`, which shows a successful connectivity test
   dated `Fri Feb 31 07:07:07 UTC 2023`. February has no 31st. Nobody ran the command; the output
   was typed. It is a small thing in a post whose whole purpose was to get people to test their
   pulls, and it is a useful calibration for how much of a documented *expected output* anywhere is
   a transcription rather than a capture — including, honestly, the fences in this file, all five of
   which were captured rather than typed, and one of which is dated in the paragraph above it for
   exactly that reason.

5. *Unanswerable from the pin:* when, or whether, the 302 goes away. The redirect notice says the
   old name will be phased out entirely in the future and names no date; the pin holds one revision
   of one documentation tree and no issue history, no traffic figures and no deprecation schedule.
   Also unanswerable from the pin: whether anyone took the post up on its revert instructions while
   they still worked. The tree records the change and both corrections to it, and records nothing at
   all about who resisted it.

**Teardown**

```sh
kubectl delete ns reg
ssh zain@10.10.10.180 \
  'sudo ctr -n k8s.io images rm k8s.gcr.io/pause:3.10; rm -f /tmp/old-config.yaml'
```

The second line matters more than it looks. Deleting the namespace removes the pods but leaves the
name step 4 added to the node's image store, and a node holding `k8s.gcr.io/pause:3.10` is exactly
the state this exercise exists to make visible. Removing the name does not remove the blob, which
`registry.k8s.io/pause:3.10` still refers to; that is the same fact step 4 measured, seen from the
other side.
