<a id="container-runtime-interface-cri-in-kubernetes"></a>
# Both switches this post asks you to set have been removed — one because what it enabled became mandatory, the other because what it enabled was abandoned

**Post** — [Introducing Container Runtime Interface (CRI) in Kubernetes](https://kubernetes.io/blog/2016/12/container-runtime-interface-cri-in-kubernetes/),
2016-12-19, Kubernetes v1.5 — Yu-Ju Hong of Google, for SIG Node, part of the *Five Days of
Kubernetes 1.5* series. Of everything announced in this year, this is the piece that most
completely won, which is why it is the hardest to see: there is no CRI setting to inspect any more.

**As written** — CRI is a gRPC plugin interface so the kubelet can drive any runtime *"without the
need to recompile"*. It ships as **Alpha** in v1.5. The post is candid about why it exists:

> However, both Docker and rkt were integrated directly and deeply into the kubelet source code
> through an internal and volatile interface. [...] These factors form high barriers to entry for
> nascent container runtimes.

Two services, `ImageService` and `RuntimeService`, over one or two Unix sockets:

> The sockets can be set in Kubelet by --container-runtime-endpoint and --image-service-endpoint
> flags.

The post prints the RPC list, and the list is worth keeping in view because it comes back at the
end of this exercise:

```
    // Sandbox operations.
    rpc RunPodSandbox(...)   rpc StopPodSandbox(...)   rpc RemovePodSandbox(...)
    rpc PodSandboxStatus(...)   rpc ListPodSandbox(...)
    // Container operations.
    rpc CreateContainer(...)   rpc StartContainer(...)   rpc StopContainer(...)
    rpc RemoveContainer(...)   rpc ListContainers(...)   rpc ContainerStatus(...)
```

It names the abstraction it is introducing and deliberately underspecifies it:

> A Pod is composed of a group of application containers in an isolated environment with resource
> constraints. In CRI, this environment is called PodSandbox. We intentionally leave some room for
> the container runtimes to interpret the PodSandbox differently based on how they operate
> internally. For hypervisor-based runtimes, PodSandbox might represent a virtual machine.

It explains why the interface is imperative and container-centric rather than declarative and
Pod-shaped — *"the Pod specification was (and is) still evolving rapidly"* — and it makes one
further design claim, about streaming:

> Another potential issue with the kubelet implementation today is that kubelet handles the
> connection of all streaming requests, so it can become a bottleneck for the network traffic on
> the node. When designing CRI, we incorporated this feedback to allow runtimes to eliminate the
> middleman. The container runtime can start a separate streaming server upon request (and can
> potentially account the resource usage to the pod!), and return the location of the server to
> kubelet. Kubelet then returns this information to the Kubernetes API server, which opens a
> streaming connection directly to the runtime-provided server and connects it to the client.

Then four projects — `cri-o`, `rktlet`, `frakti`, and the built-in `dockershim` — and a forecast:

> Kubelet does not yet use CRI by default, but we are actively working on making this happen.

with the instruction that follows from it, which is where the exercise starts:

> you simply have to start the Kubernetes API server with
> `--feature-gates=StreamingProxyRedirects=true` to enable the new streaming redirect feature, and
> then start the kubelet with `--experimental-cri=true`.

**As it runs now** — take the two switches in that sentence one at a time, because they are the two
halves of the post's fate.

`--experimental-cri` has **zero** occurrences under `docs/` at the pin. So does `EnableCRI`, the
minikube spelling the post's recipe uses. There is no flag, no gate, no configuration field that
turns CRI on or off. What there is instead is a precondition:

> For Kubernetes v1.26 and later, the kubelet requires that the container runtime supports the `v1`
> CRI API. If a container runtime does not support the `v1` API, the kubelet will not register the
> node.
>
> — `docs/concepts/containers/cri.md:33-35`, on a page that declares the API
> `{{< feature-state for_k8s_version="v1.23" state="stable" >}}`

Not a default: a requirement. A runtime that does not speak CRI does not produce a Node object.

`StreamingProxyRedirects` is gone in the other direction, and its gate file records the shape of
the retreat — see [the ladder](#the-ladder) below. The design the post described, in which the API
server connects *"directly to the runtime-provided server"*, was switched off before the switch was
deleted.

The post's two socket flags both survive, but only one is still the recommended way to set
anything:

> `--image-service-endpoint string` — The endpoint of container image service. If not specified, it
> will be the same with --container-runtime-endpoint by default. [...] (DEPRECATED: This parameter
> should be set via the config file specified by the Kubelet's `--config` flag.)
>
> — `docs/reference/command-line-tools-reference/kubelet.md:459-462`

`--container-runtime-endpoint` appears across five pages and is the flag the migration
documentation still tells you to look for. Its sibling `--container-runtime` did not survive at
all: *"The `--container-runtime` command line argument is not available in Kubernetes v1.27 and
later"* (`docs/tasks/administer-cluster/migrating-from-dockershim/find-out-runtime-you-use.md:92-93`).

Of the post's four integrations, one is left. `cri-o` appears across fourteen files. `rktlet`,
`frakti` and `rktnetes` have **zero** occurrences each. `dockershim` appears across thirteen files
and every one of them is about its absence:

> The dockershim is a component of Kubernetes version 1.23 and earlier. [...] Starting with version
> 1.24, dockershim has been removed from Kubernetes.
>
> — `docs/reference/glossary/dockershim.md`

which is the note [09](09-how-we-made-kubernetes-easy-to-install.md) left for this exercise to
pick up: the reason the pin tells a kubeadm reader that *"Docker Engine does not implement the CRI
which is a requirement for a container runtime to work with Kubernetes"* and points at
`cri-dockerd`, *"a project based on the legacy built-in Docker Engine support that was removed from
the kubelet in version 1.24"* (`install-kubeadm.md:139-144`). The shim the post shipped inside the
kubelet now lives outside it, maintained by a vendor, and the post's fourth bullet is the only one
of the four whose code still runs.

The post's `--network-plugin=kubenet` has also gone quiet, in a way worth one line. Grep the pin for
`kubenet` and you get exactly one hit, and it is not kubenet: `kubenetesAPICall`, a misspelling of
`kubernetesAPICall` inside a copy-pasteable sample configuration in kubeadm's v1beta4 reference
(`docs/reference/config-api/kubeadm-config.v1beta4.md:220`, against the correctly-spelled field
definition at `:1847`). The network plugin the post recommended is undocumented; the only thing
left carrying its letters is a typo.

And there is a hole where the page defining all this should be reachable from. The concept page is
`docs/concepts/containers/cri.md`, and exactly one file in the corpus links to it
(`concepts/services-networking/_index.md`). Six link to `/docs/concepts/architecture/cri/`:
`install-kubeadm.md:139`, `find-out-runtime-you-use.md:64`,
`migrating-telemetry-and-security-agents.md:37`, `volumes.md:1231`, `cgroups.md:147`, and — the one
that matters most — the `full_link` of the glossary term itself:

> ```
> title: Container Runtime Interface (CRI)
> id: cri
> full_link: /docs/concepts/architecture/cri
> ```
>
> — `docs/reference/glossary/cri.md:2-4`

There is no `concepts/architecture/cri.md` in the pinned tree, no `aliases:` entry in `cri.md`
claiming that path, no CRI rule in `hugo.toml`, and no `[[redirects]]` block anywhere in
`netlify.toml`. Meanwhile `cri.md` opens by pulling its own definition out of that glossary entry
with `{{< glossary_definition term_id="cri" >}}`. The page and the glossary cite each other, and
one of the two citations has no target.

**The diff, and why** — this is two of the seven cases at once, and the pair is the point.

The first switch is **the post was right, and being right removed the switch**. `--experimental-cri`
did not become the default; it stopped existing. That is a stronger outcome than defaulting, and a
different one. A defaulted flag leaves a seam: something you could still turn off, a code path that
must keep working for whoever turns it off, a compatibility promise. Removing the flag says the
alternative is not supported, and the pin says exactly that in the harshest available terms — no CRI
`v1`, no Node object. The interface stopped being a feature and became the definition of what a
node *is*. You cannot run an exercise that observes CRI being switched on for the same reason you
cannot run one that observes TCP being switched on.

The second switch is **the post describes a plan the project abandoned**. Re-read the streaming
paragraph and notice that it is not describing CRI; it is describing a consequence the authors
expected CRI to unlock. Runtimes would stand up their own streaming servers, the API server would
dial them directly, and the kubelet would stop carrying `exec` traffic — with a parenthetical
hoping the bytes could then be billed to the pod. Every part of that needed the API server to
follow a redirect it received from the kubelet, which is precisely what `StreamingProxyRedirects`
controlled. That gate spent twelve releases on by default, four releases deprecated-but-on, three
releases deprecated-and-off, and was then deleted. The middleman is still the middleman.

The two outcomes have the same visible signature — a flag that no longer exists — and opposite
meanings, and nothing in the corpus distinguishes them. This is the practical lesson the exercise
is built to teach: **absence of a switch is not evidence about the feature.** A reader who greps
today's documentation for either name finds nothing and can conclude nothing. The gate files are
where the difference is written down, and they are the only place it is written down, which is why
the ladder below is not decoration here but the whole argument.

Notice also which half of the post aged best, because it is not the half that shipped hardware. The
`PodSandbox` paragraph — *"we intentionally leave some room for the container runtimes to interpret
the PodSandbox differently"* — is still exactly right, and it is right in a way that had to be
designed for rather than discovered. The reasoning for an imperative interface is likewise intact:
the Pod spec did keep evolving rapidly, and the runtimes did not have to be changed for most of it.
The post's durable content is its *refusals* — what it declined to specify, and what it declined to
push down into the runtime. Its perishable content is its optimism about what a good interface would
let somebody else build.

One last thing, and it closes the loop on the RPC list printed above. The three `List` calls in that
block have outgrown themselves:

> The standard CRI list RPCs (`ListContainers`, `ListPodSandbox`, `ListImages`) return all results
> in a single unary response. On nodes with a large number of containers (for example, more than
> roughly 10,000 including both running and stopped), these responses can exceed gRPC's default
> 16 MiB message size limit, causing the kubelet to fail when reconciling state with the container
> runtime.
>
> — `docs/concepts/containers/cri.md:48-53`

Two of those three RPC names are in the code block the post printed. Ten years in, the interface's
first breaking scale limit is not in the design the post argued about for six paragraphs; it is in
the two most boring calls on the list.

<a id="the-ladder"></a>
**The ladder** — the gate the post tells you to enable, the gate that was added to guard it, and
the gate now amending the RPC list the post printed. The first two are the evidence for the
abandonment claim above.

## StreamingProxyRedirects
| stage | default | locked | releases |
|---|---|---|---|
| beta | `false` | — | v1.5 – v1.5 |
| beta | `true` | — | v1.6 – v1.17 |
| deprecated | `true` | — | v1.18 – v1.21 |
| deprecated | `false` | — | v1.22 – v1.24 |

`removed: true` at file level. Three things to read off this. It has **no alpha stage at all** — it
enters the ladder at beta, in the post's own release, defaulting `false`, which is why the post has
to tell you to set it. Its `deprecated` stages **do** carry a `defaultValue`, and the value
*changes* between them: deprecated-and-on for four releases, then deprecated-and-off for three. A
`deprecated` stage is therefore not the absence of a default — compare
[10](10-dynamic-provisioning-and-storage-in-kubernetes.md), where two `deprecated` stages carry no
`defaultValue` and the cell transcribes as an em-dash. Both shapes are legal, and only reading the
file tells you which one you have. Third, the flip from `true` to `false` at v1.22 is the actual
moment the design was given up; the removal at v1.25 is bookkeeping.

## ValidateProxyRedirects
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.12 – v1.13 |
| beta | `true` | — | v1.14 – v1.21 |
| deprecated | `true` | — | v1.22 – v1.24 |

Also `removed: true`. Its description is *"This flag controls whether the API server should
validate that redirects are only followed to the same host. Only used if the
`StreamingProxyRedirects` flag is enabled."* It arrived six releases after the feature to constrain
where the API server would follow a kubelet's redirect to, and its final stage is
deprecated-with-default-`true` — a guard left switched on over a feature that by then defaulted off.
The file describing it still names the other gate in the present tense, and that other gate no
longer exists.

## CRIListStreaming
| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.36 –  |

No `removed`, no closing release, alpha at the pin and one release old. This is the amendment to the
post's RPC list: `StreamContainers`, `StreamPodSandboxes`, `StreamImages`, added because the unary
`List` calls hit gRPC's 16 MiB ceiling. The pin notes the compatibility arrangement — *"If the
container runtime does not support streaming RPCs, the kubelet automatically falls back to the
standard unary RPCs"* — which is the same shape of promise the post made about runtimes providing
one socket or two.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), fresh. Two nodes, because the
central experiment breaks a node's runtime endpoint on purpose and you want a control plane that is
still answering while you do it. Bring both guests up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=pair`, install Kubernetes on both with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), then bring up
the cluster as usual and confirm two `Ready` nodes before starting.

Do not install a second runtime. The exercise is about the interface between the kubelet and the one
you already have.

**Do**

1. Find the socket the post's two flags name, without assuming which mechanism set it. On the
   control-plane node:

   ```sh
   tr '\0' ' ' < /proc/"$(pgrep -f 'kubelet --')"/cmdline; echo
   sudo grep -n -e containerRuntimeEndpoint -e imageServiceEndpoint /var/lib/kubelet/config.yaml
   ```

   The migration page tells you to *"look for the `--container-runtime` flag and the
   `--container-runtime-endpoint` flag"*. Report which of the post's two flags appear on the command
   line, which appear in the config file, and which appear in neither — then say what the kubelet is
   using for the image service given that neither file mentions it.

2. Establish that there is no switch to find:

   ```sh
   kubelet --help 2>&1 | grep -i -e experimental-cri -e enable-cri ; echo "exit=$?"
   kubectl get --raw "/api/v1/nodes/$(kubectl get node -o jsonpath='{.items[0].metadata.name}')/proxy/configz" \
     | tr ',' '\n' | grep -i -e cri -e runtime
   ```

   Nothing named after CRI is configurable. Contrast that with what step 6 will show about a gate
   that *is* configurable, and keep the distinction: a missing flag and a disabled flag look
   identical here.

3. Ask the runtime the post's own RPCs, using the tool the pin documents for it. Install `crictl`
   from your distribution or the Kubernetes release tooling, point it at the socket from step 1, and
   run the read-only half of the post's list:

   ```sh
   sudo crictl --runtime-endpoint unix:///run/containerd/containerd.sock version
   sudo crictl pods
   sudo crictl ps
   sudo crictl images
   ```

   `crictl version` prints the CRI API version the runtime negotiated. Check it against
   `cri.md`'s requirement that the kubelet needs `v1`, and note which of the post's two services
   each of the last three commands is exercising.

4. Look at the abstraction the post said it was leaving underspecified, and see what containerd
   chose:

   ```sh
   kubectl run sandbox-probe --image=registry.k8s.io/pause:3.10
   kubectl wait --for=condition=Ready pod/sandbox-probe --timeout=120s
   POD=$(sudo crictl pods --name sandbox-probe -q)
   sudo crictl inspectp "$POD" | head -60
   ```

   One `PodSandbox`, and containers inside it. Find in that output what this runtime decided a
   PodSandbox *is* — the post offered "a virtual machine" and "Linux namespaces" as two legal
   readings. Name which one you are looking at and the field that told you.

5. Confirm the sandbox is the pod's resource boundary, which is the one thing the post said a
   PodSandbox *must* do:

   ```sh
   sudo crictl inspectp "$POD" | grep -i -e cgroup -e cgroupParent
   sudo crictl ps --pod "$POD" -q | while read -r c; do sudo crictl inspect "$c" | grep -i cgroupsPath; done
   ```

   The post says this is *"achieved by launching all the processes within the pod-level cgroup that
   kubelet creates and passes to the runtime"*. Say which side created the path you are looking at,
   and what would go wrong if the runtime chose its own.

6. Test the post's other switch, which is the one that was abandoned:

   ```sh
   sudo grep -n feature-gates /etc/kubernetes/manifests/kube-apiserver.yaml ; echo "exit=$?"
   kubectl get --raw /metrics | grep -c 'kubernetes_feature_enabled.*StreamingProxyRedirects'
   ```

   Zero and zero. Then check the post's instruction directly, without editing the static manifest —
   read what the API server accepts:

   ```sh
   kubectl -n kube-system logs -l component=kube-apiserver --tail=5 >/dev/null 2>&1
   kube-apiserver --help 2>&1 | grep -A20 'feature-gates' | grep -i -e Streaming -e Redirect ; echo "exit=$?"
   ```

   If `kube-apiserver` is not on your PATH, the same answer is available from the ladder above. Say
   what would happen if you added the post's `--feature-gates=StreamingProxyRedirects=true` to the
   static manifest, and which of the two failure modes it would be: refused as unrecognised, or
   accepted and ignored.

7. Now show that streaming still goes through the kubelet, which is the abandoned design's
   observable consequence. From the control-plane node, watch the worker's kubelet while exec'ing
   into a pod on it:

   ```sh
   kubectl run shell --image=registry.k8s.io/e2e-test-images/agnhost:2.53 --overrides='{"spec":{"nodeName":"'"$(kubectl get node -o jsonpath='{.items[1].metadata.name}')"'"}}' -- sleep 3600
   kubectl wait --for=condition=Ready pod/shell --timeout=180s
   ```

   then on the **worker**, in one terminal:

   ```sh
   sudo ss -tnp | grep -c kubelet
   ```

   and from the control plane, in another, run `kubectl exec shell -- sleep 30` while re-running the
   `ss` count on the worker. Report whether the connection count on the kubelet moves. Then explain
   what the post predicted would happen to that count and why it did not.

8. Break the interface rather than the runtime, and watch what the post's forecast actually bought.
   On the **worker only**:

   ```sh
   sudo cp /var/lib/kubelet/config.yaml /var/lib/kubelet/config.yaml.bak
   sudo sed -i 's#^containerRuntimeEndpoint:.*#containerRuntimeEndpoint: unix:///run/nothing/here.sock#' /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet
   sudo journalctl -u kubelet -n 40 --no-pager
   ```

   From the control plane, `kubectl get nodes -w`. The worker does not merely go `NotReady` in the
   ordinary way — read the kubelet's own log lines and say at which step it stops. Match that
   against `cri.md`'s sentence about node registration and state precisely what "the flag was
   removed rather than defaulted" costs you operationally.

9. Restore it, and verify the restoration the way the pin's troubleshooting page would:

   ```sh
   sudo mv /var/lib/kubelet/config.yaml.bak /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet
   sudo crictl --runtime-endpoint unix:///run/containerd/containerd.sock info | head -20
   ```

   Then, from the control plane, confirm both nodes are `Ready` again before continuing.

10. Close on the RPC list. Check whether your runtime offers the streaming variants, and whether
    your kubelet would use them:

    ```sh
    kubectl get --raw "/api/v1/nodes/$(kubectl get node -o jsonpath='{.items[0].metadata.name}')/proxy/configz" \
      | tr ',' '\n' | grep -i -e CRIListStreaming -e featureGates -A3
    sudo crictl ps -a | wc -l
    ```

    Given the ladder above, say whether `CRIListStreaming` is on, and what the pin promises happens
    if you enable it against a runtime that has not implemented `StreamContainers`. Then estimate,
    from the container count on your node, how far you are from the roughly-ten-thousand figure the
    pin names — and say what that tells you about who the gate is for.

**Expect**

```sh
kubectl get nodes
sudo crictl version
sudo crictl pods
sudo crictl ps | wc -l
kubelet --help 2>&1 | grep -c -i -e experimental-cri -e enable-cri
```

Two `Ready` nodes, a runtime reporting CRI `v1`, one sandbox per pod on the node, and a zero from
the last command. That zero is the exercise: the interface this post introduced as alpha behind a
flag is now the thing whose absence stops a node from existing, and there is nothing left to toggle.

By the end you should be able to give two different accounts of a missing flag — one where the
feature won and one where it lost — and say which piece of the corpus is the only place that
distinguishes them. You should also be able to name what a `PodSandbox` is on *your* node, from the
runtime's own answer rather than from the post's two examples.

**Read on** — the pin's
[CRI concept page](https://kubernetes.io/docs/concepts/containers/cri/) is short, and it is the page
the glossary term for CRI fails to reach. Read its *Upgrading* section against step 8, then answer:
if you upgrade a node's Kubernetes version and its container runtime on the same afternoon, in which
order must the two restarts happen, and what does the page say you might have to do a second time?

**Teardown** — `kubectl delete pod sandbox-probe shell --ignore-not-found`, and confirm
`/var/lib/kubelet/config.yaml` on the worker no longer has a `.bak` beside it, otherwise
[the teardown step](../../strands/lab-topologies.md#teardown).
