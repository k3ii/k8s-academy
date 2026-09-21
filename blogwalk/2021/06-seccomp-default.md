<a id="seccomp-default"></a>

# The gate reached stable and left the tree in seven releases, the default it was built to change is still `Unconfined` at the pin, and the post's two-step recipe now works only if you skip step one — because step one enables a gate that no longer exists, and the kubelet refuses to start

**Post** — [Enable seccomp for all workloads with a new v1.22 alpha
feature](https://kubernetes.io/blog/2021/08/25/seccomp-default/), 2021-08-25, by Sascha Grunert (Red
Hat) — 267 lines, 11,409 bytes. Two kubelet settings that move every workload on a node from
`Unconfined` to the container runtime's default seccomp profile, plus an upgrade strategy for doing
it without breaking the applications. One of the two settings has been deleted, the other works
exactly as written, and the thing the post says `should be fixed in the long term` is still not
fixed.

**As written**

The post opens on the state of seccomp in Kubernetes after its graduation to GA in v1.19. The
`securityContext` gained dedicated seccomp fields (`:19-23`), and a Pod or container can name one of
three profile types (`:29-33`): `Unconfined` — `seccomp will not be enabled`; `RuntimeDefault` —
`the container runtimes default profile will be used`; and `Localhost` — `a node local profile will
be applied, which is being referenced by a relative path to the seccomp profile root
(<kubelet-root-dir>/seccomp) of the kubelet`. Then the sentence the rest of the post exists to
answer, at `:35-39`: `With the graduation of seccomp, nothing has changed from an overall security
perspective, because Unconfined is still the default. This is totally fine if you consider this from
the upgrade path and backwards compatibility perspective of Kubernetes releases. But it also means
that it is more likely that a workload runs without seccomp at all, which should be fixed in the
long term.`

`## SeccompDefault to the rescue` (`:41-60`) introduces the v1.22 kubelet feature gate, `added in
alpha state as every other new feature`, disabled by default and `enabled manually for every single
Kubernetes node`. What it does is one sentence at `:50-51`: `it just changes the default seccomp
profile from Unconfined to RuntimeDefault`. `:53-57` warns that the runtime default differs between
CRI-O and containerd and between hardware architectures, while `generally speaking, those default
profiles allow a common amount of syscalls while blocking the more dangerous ones`.

`### Enabling the feature` (`:62-74`) is the operational core, and it is a numbered list of exactly
two items. **One**: `Enable the feature gate by setting the SeccompDefault=true via the command line
(--feature-gates) or the kubelet configuration file.` **Two**: `Turn on the feature by enabling the
feature by adding the --seccomp-default command line flag or via the kubelet configuration file
(seccompDefault: true).` Then the sentence that makes the pair a pair, at `:74`: `The kubelet will
error on startup if only one of the above steps have been done.`

`### Trying it out` (`:76-176`) is four manifests and four readings. A one-container Pod with no
`securityContext` at all (`:81-90`), then the verification recipe (`:99-102`): `CONTAINER_ID=$(sudo
crictl ps -q --name=test-container)` followed by `sudo crictl inspect $CONTAINER_ID | jq
.info.runtimeSpec.linux.seccomp`, whose output (`:104-116`) shows `defaultAction: SCMP_ACT_ERRNO`,
three x86 architectures, and a `syscalls` array with an `SCMP_ACT_ALLOW` entry. `:118-121` reads
that back as CRI-O and runc having applied the default profile, which `denies all syscalls per
default, while allowing commonly used ones`. `:128-131` adds the limitation: `the feature will not
influence any Kubernetes API for now. Therefore, it is not possible to retrieve the used seccomp
profile via kubectl get or describe if the SeccompProfile field is unset within the
SecurityContext.` Then a two-container Pod (`:138-152`) where `test-container-nginx` sets `type:
Unconfined` and `test-container-redis` sets nothing, and three `jq` assertions (`:156-176`) proving
the first is unprofiled, the second is not, and the sandbox itself runs with the default.

`### Upgrade strategy` (`:178-252`) is the half of the post that is advice rather than mechanism, in
four stages. Turning on the gate changes nothing observable — `Enabling the feature gate at the
kubelet level will not turn on the feature, but will make it possible` (`:185-188`). Testing the
application offers five bullets, two `_Recommended_` and three `_Optional_`: analyse the code or run
it under `strace` (`:197-203`); set the profile manually and roll it out (`:205-207`); run an
end-to-end suite with `RuntimeDefault` (`:209-211`); build a custom profile whose `defaultAction` is
`SCMP_ACT_LOG` rather than `SCMP_ACT_ERRNO` so blocked syscalls are logged instead of denied, then
read them out of `/var/log/audit/audit.log` or `/var/log/syslog` by `type=SECCOMP` or `type=1326`
(`:213-224`); or use the Security Profiles Operator, which `makes the above mentioned manual log
investigation obsolete` (`:226-229`). Deploying follows from the test result (`:237-242`), and the
last stage enables the kubelet setting `on a per-node basis to reduce the overall risk of missing a
syscall` (`:244-252`).

**As it runs now** — the mechanism is stable, one of the two switches has been deleted, and the
default has not moved.

**The gate is gone, and the post's first instruction is the one that breaks the kubelet.** The
`SeccompDefault` gate file is still on disk at the pin, but it declares `removed: true` and `_build:
{list: never, render: false}`, so it is one of the 230 gate files that exist without being published
as pages. Its stages end at v1.28. A kubelet at v1.37 does not know the name, and a `featureGates`
entry naming it is a startup error rather than a no-op — which inverts `:74` exactly. The post says
the kubelet errors if you do only one of the two steps; at the pin the kubelet errors if you do
*both*, and starts cleanly if you do only the second.

**The second switch works verbatim.** `seccompDefault` is a live `bool` in the kubelet configuration
(`reference/config-api/kubelet-config.v1beta1.md:1706-1711`), described in the post's own words —
`SeccompDefault enables the use of RuntimeDefault as the default seccomp profile for all workloads`
— and `--seccomp-default` is a live flag
(`reference/command-line-tools-reference/kubelet.md:823-826`), notable for *not* carrying the
`(DEPRECATED: This parameter should be set via the config file…)` marker that 100 of that page's 126
flag rows carry. The post's second instruction can be pasted into a v1.37 node unchanged.

**The default is still `Unconfined`.** `kubelet-config.v1beta1.md:1711` reads `Default: false`, and
`tasks/administer-cluster/kubelet-config-file.md:285` shows `"seccompDefault": false` in a kubelet's
own dumped configuration. The project's security checklist puts it in the imperative at
`concepts/security/security-checklist.md:165-167`: `Since Kubernetes 1.27, you can enable the use of
RuntimeDefault as the default seccomp profile for all workloads` — *can enable*, with the
corresponding checklist item at `:106` still unticked by default. The gate went alpha, beta, stable
and out of the tree; the behaviour it gated is still opt-in per node. That is the whole finding:
what graduated was the *ability to change the default*, not the default.

**The post's API limitation is now documentation, and it names the same tool.**
`tutorials/security/seccomp.md:440-447`: `Enabling the feature will neither change the Kubernetes
securityContext.seccompProfile API field nor add the deprecated annotations of the workload. This
provides users the possibility to rollback anytime without actually changing the workload
configuration. Tools like crictl inspect can be used to verify which seccomp profile is being used
by a container.` The post's warning at `:128-131` and its verification recipe at `:99-102` were both
absorbed, the second one by name. Four years on there is still no way to ask the API what profile a
container actually got.

**That invisibility has a consequence the post could not have seen.** Pod Security admission reads
the spec, not the node, and the Restricted standard at
`concepts/security/pod-security-standards.md:435-443` requires that the `Seccomp profile must be
explicitly set to one of the allowed values. Both the Unconfined profile and the absence of a
profile are prohibited.` So a node with `seccompDefault: true` running a Pod with no seccomp field
gives that Pod the `RuntimeDefault` profile *and* fails Restricted — the node default cannot satisfy
an admission rule that is written against the manifest. The refusal itself is walked by [the runc
CVE exercise](../2019/02-runc-cve-2019-5736.md); what belongs here is the asymmetry: this feature
makes a cluster more secure without making a single Pod compliant.

**Three of the post's five testing bullets have become documentation; two have not.** The
`Unconfined` override and the custom profile survive as `tutorials/security/seccomp.md:453-456`, the
per-node rollout as `:458-460`, and the `SCMP_ACT_LOG` idea is now an entire tutorial step rather
than an optional bullet — `:201-306` builds a Pod around an `audit.json` profile for exactly that
purpose. What did not survive is the tooling. `strace` appears zero times under `content/en/docs` at
the pin. The Security Profiles Operator is named in three documentation files —
`concepts/security/linux-kernel-security-constraints.md:229`,
`concepts/security/security-checklist.md:168-169` and `tutorials/security/apparmor.md:239` — none of
which is the seccomp tutorial or the seccomp reference. The operator the post recommends for
profiling is still recommended, from pages about other things.

**And the advice underneath those bullets was reversed.**
`concepts/security/linux-kernel-security-constraints.md:100-114` is a section titled `Considerations
for seccomp` which opens `seccomp is a low-level security configuration that you should only
configure yourself if you require fine-grained control over Linux syscalls`, lists three risks of
doing it at scale — `Configurations might break during application updates`, `Attackers can still
use allowed syscalls to exploit vulnerabilities`, `Profile management for individual applications
becomes challenging at scale` — and then states a **Recommendation**: `Use the default seccomp
profile that's bundled with your container runtime. If you need a more isolated environment,
consider using a sandbox, such as gVisor.` The post's answer to a workload that `RuntimeDefault`
breaks is a hand-built profile, twice. The pin's answer is: do not hand-build profiles, and if the
runtime default is not enough, change the sandbox instead of the filter.

**The documentation the post points at grew a page that did not exist, and kept talking about the
gate.** Seccomp now has a reference page of its own, `reference/node/seccomp.md`, which lists

**four** places a profile can be specified (`:19-25`) against the post's two — adding init
containers and ephemeral containers — and states two things the post never mentions: that
container-level fields beat the Pod-level value while unset containers inherit it (`:36-38`), and
that `It is not possible to apply a seccomp profile to a Pod or container running with privileged:
true set in the container's securityContext. Privileged containers always run as Unconfined.`
(`:40-44`). Meanwhile the tutorial the docs send readers to still speaks of the removed gate in four
places: `the SeccompDefault feature` at `:454` and `:476`, and `this feature gate` at `:459` and
`:475`, the last inside a `kind` example pinned to `kindest/node:v1.28.0` — the last release in
which the gate existed.

**The lab's runtime is not the post's.** The output at `:104-116` is CRI-O and runc, as `:118-119`
says. This lab runs containerd, and both the post at `:53-54` and `reference/node/seccomp.md:55-59`
warn that the defaults differ between runtimes and between their releases. The profile you read in
step 5 will not match the post's byte for byte, and that is the post being right rather than wrong.
The runtime itself, the socket and `crictl` are [the CRI
exercise](../2016/13-container-runtime-interface-cri-in-kubernetes.md)'s subject; the kubelet
drop-in directory used here to make a one-node change is [the PID-limiting
exercise](../2019/05-pid-limiting.md)'s. Setting the seccomp field explicitly, as part of a
Restricted-compliant Pod, is [the eleven-ways exercise](../2018/06-11-ways-not-to-get-hacked.md)'s.
Release dates and the pressure behind each are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

**The diff, and why** — four cases, and the interesting one is the stasis.

**Broke: step one of a two-step recipe.** The gate was removed after v1.28 and the kubelet no longer
recognises the name, so a configuration that follows the post exactly does not start. This is the
ordinary fate of an alpha-era instruction and the post could not have written it differently. What
makes it worth a measurement is the shape of the failure: the post's own safety sentence at `:74`
promised an error for the half-configured case, and the pin delivers an error for the
fully-configured one. A reader following the post and reading its warning would conclude they had
done *too little*, when they had done one thing too many.

**Overtaken by stasis: the default.** The post's premise is that `Unconfined` is the default and
`should be fixed in the long term`. Sixteen versions later the gate that was created to fix it has
completed its whole life cycle — alpha at v1.22, beta and on at v1.25, stable at v1.27, deleted
after v1.28 — and `seccompDefault` still defaults to `false`. Nothing regressed and nothing was
abandoned: the graduation was real, the feature works, and the project simply never took the step of
changing what happens to a node where nobody has configured anything. Set beside the other stasis
case in this year — the scheduler that still `currently does not` account for swap, walked by [the
swap exercise](05-run-nodes-with-swap-alpha.md) — the pattern is that Kubernetes graduates
*capabilities* readily and changes *defaults* almost never, because a default is the one thing an
upgrade cannot opt out of.

**Retired by being agreed with.** The verification recipe, the API-invisibility warning, the
per-node rollout, the `Unconfined` escape hatch and the `SCMP_ACT_LOG` trick are all in the
documentation now, in some places nearly word for word, and `crictl inspect` is still the only way
to answer the question the post asks. An alpha announcement whose *mechanics* were absorbed this
completely is unusual in this archive; compare it with the same year's swap post, where the caveats
were absorbed and the configuration was replaced.

**Never absorbed: the tooling, and the strategy underneath it.** `strace` is nowhere in the
documentation, the Security Profiles Operator is named only from pages about other subjects, and the
pin's own recommendation section argues against the custom-profile path that two of the post's five
bullets recommend. This is not the documentation disagreeing with a fact; it is the documentation
having changed its mind about what an operator should do when `RuntimeDefault` breaks an
application. The post says profile it and fix the profile. The pin says use the runtime's profile,
and if that is not enough, use a stronger sandbox.

**The ladder**

One gate, transcribed from its `stages:` list parsed as YAML, plus the file-level flag that ends it.

```
SeccompDefault  alpha  false  1.22 - 1.24
                beta   true   1.25 - 1.26
                stable true   1.27 - 1.28
                removed: true
```

Seven releases end to end, and the second row is the one to read carefully. From v1.25 the gate
defaulted to `true`, and nothing observable changed on any node — because, as the post itself says
at `:185-188`, `Enabling the feature gate at the kubelet level will not turn on the feature, but
will make it possible`. A gate defaulting to `true` while the behaviour stayed off is the clearest
example in this year of why a gate's `defaultValue` is not the feature's default: the gate governed
*availability*, and `seccompDefault` governed *behaviour*. When the gate went stable at v1.27 and
was deleted after v1.28, availability became unconditional and the behaviour did not move at all.
The gate's body text says what it always said: `Enables the use of RuntimeDefault as the default
seccomp profile for all workloads.` `locked` never appears in this file — it never needed to,
because the whole ladder is about whether the option exists, and the option is now simply a field.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair): a control-plane node at
`10.10.10.130` and a worker at `10.10.10.131`, brought up with [the five provision
steps](../../strands/lab-topologies.md#provision). Two nodes are the subject, not a convenience. The
post's whole upgrade strategy is per-node — `:244-252` says to enable the kubelet setting `on a
per-node basis`, and `tutorials/security/seccomp.md:458-460` still recommends `a subset of your
nodes` — and a claim about a subset of nodes cannot be shown on one node. Here the setting goes on
the worker only, so the same manifest with no `securityContext` at all gets `RuntimeDefault` on one
node and `Unconfined` on the other, and the difference is invisible to the API on both. Everything
is driven from the control-plane host; the worker is reached over `ssh zain@10.10.10.131` for the
kubelet's own files, and `crictl` is needed on both nodes.

**Do**

1. Establish that neither node has this feature on, from the kubelet's own view rather than from a
   file. Do it for both nodes, because the rest of the exercise is a comparison:

   ```sh
   for N in $(kubectl get nodes -o jsonpath='{.items[*].metadata.name}'); do
     echo "== $N"
     kubectl get --raw "/api/v1/nodes/$N/proxy/configz" \
       | python3 -c 'import sys,json; c=json.load(sys.stdin)["kubeletconfig"]; print(" seccompDefault:", c.get("seccompDefault")); print(" featureGates:", c.get("featureGates", {}))'
   done
   sudo grep -o -- '--seccomp-default[^ ]*' /var/lib/kubelet/kubeadm-flags.env || echo "flag not set on the control plane"
   ssh zain@10.10.10.131 "sudo grep -o -- '--seccomp-default[^ ]*' /var/lib/kubelet/kubeadm-flags.env || echo 'flag not set on the worker'"
   ```

2. Apply the post's first manifest exactly as `:81-90` gives it, then read the effective profile
   with the post's own recipe from `:99-102`, on whichever node the scheduler chose:

   ```sh
   kubectl apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: test-pod
   spec:
     containers:
       - name: test-container
         image: nginx:1.21
   EOF
   kubectl wait --for=condition=Ready pod/test-pod --timeout=120s
   kubectl get pod test-pod -o jsonpath='{.spec.nodeName}{"\n"}'
   sudo crictl --runtime-endpoint unix:///run/containerd/containerd.sock inspect \
     "$(sudo crictl ps -q --name=test-container)" | jq .info.runtimeSpec.linux.seccomp
   ```

3. Now do the post's step 1 on the worker, and only step 1. A drop-in file keeps the change to one
   node and one line, the way [the PID-limiting exercise](../2019/05-pid-limiting.md) does it:

   ```sh
   ssh zain@10.10.10.131 'sudo mkdir -p /etc/kubernetes/kubelet.conf.d && \
     printf "apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nfeatureGates:\n  SeccompDefault: true\n" \
     | sudo tee /etc/kubernetes/kubelet.conf.d/20-seccomp-gate.conf'
   ssh zain@10.10.10.131 'sudo systemctl restart kubelet; sleep 20; systemctl is-active kubelet'
   ssh zain@10.10.10.131 'sudo journalctl -u kubelet --since "-2min" --no-pager | grep -i -m5 "feature\|seccomp\|unrecognized"'
   ```

4. Take the gate away and do the post's step 2 on its own. One file replaces the other, and this is
   the configuration the post says is incomplete:

   ```sh
   ssh zain@10.10.10.131 'sudo rm -f /etc/kubernetes/kubelet.conf.d/20-seccomp-gate.conf && \
     printf "apiVersion: kubelet.config.k8s.io/v1beta1\nkind: KubeletConfiguration\nseccompDefault: true\n" \
     | sudo tee /etc/kubernetes/kubelet.conf.d/21-seccomp-default.conf'
   ssh zain@10.10.10.131 'sudo systemctl restart kubelet; sleep 20; systemctl is-active kubelet'
   kubectl get --raw "/api/v1/nodes/$(kubectl get nodes -o jsonpath='{.items[?(@.spec.taints)]}' >/dev/null; echo node2)/proxy/configz" 2>/dev/null | head -c 0
   WORKER=$(kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{" "}{end}' | tr ' ' '\n' | grep -v "$(kubectl get nodes -l node-role.kubernetes.io/control-plane -o jsonpath='{.items[0].metadata.name}')" | head -1)
   kubectl get --raw "/api/v1/nodes/$WORKER/proxy/configz" \
     | python3 -c 'import sys,json; print("seccompDefault:", json.load(sys.stdin)["kubeletconfig"].get("seccompDefault"))'
   ```

5. Run the post's manifest again, pinned to the worker this time, and read what the runtime actually
   applied. The post printed CRI-O's profile; this is containerd's:

   ```sh
   kubectl delete pod test-pod --wait
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Pod
   metadata:
     name: test-pod
   spec:
     nodeName: $WORKER
     containers:
       - name: test-container
         image: nginx:1.21
   EOF
   kubectl wait --for=condition=Ready pod/test-pod --timeout=120s
   ssh zain@10.10.10.131 'sudo crictl inspect "$(sudo crictl ps -q --name=test-container)" \
     | jq "{defaultAction: .info.runtimeSpec.linux.seccomp.defaultAction, architectures: .info.runtimeSpec.linux.seccomp.architectures, rules: (.info.runtimeSpec.linux.seccomp.syscalls | length), allowed: (.info.runtimeSpec.linux.seccomp.syscalls[0].names | length)}"'
   ```

6. The same manifest on the control-plane node, and the same question asked of the API on both. This
   is the per-node claim and the invisibility claim in one step:

   ```sh
   CP=$(kubectl get nodes -l node-role.kubernetes.io/control-plane -o jsonpath='{.items[0].metadata.name}')
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Pod
   metadata:
     name: test-pod-cp
   spec:
     nodeName: $CP
     tolerations: [{operator: "Exists"}]
     containers:
       - name: test-container-cp
         image: nginx:1.21
   EOF
   kubectl wait --for=condition=Ready pod/test-pod-cp --timeout=120s
   sudo crictl inspect "$(sudo crictl ps -q --name=test-container-cp)" | jq '.info.runtimeSpec.linux.seccomp == null'
   kubectl get pod test-pod test-pod-cp -o jsonpath='{range .items[*]}{.metadata.name}{": "}{.spec.securityContext}{" / "}{.spec.containers[0].securityContext}{"\n"}{end}'
   kubectl describe pod test-pod | grep -i seccomp || echo "describe says nothing about seccomp"
   ```

7. The post's two-container manifest from `:138-152`, pinned to the worker, with its three `jq`
   assertions from `:156-176`. One container opts out, one inherits the node default, and the
   sandbox has a profile of its own:

   ```sh
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Pod
   metadata:
     name: test-pod-multi
   spec:
     nodeName: $WORKER
     containers:
       - name: test-container-nginx
         image: nginx:1.21
         securityContext:
           seccompProfile:
             type: Unconfined
       - name: test-container-redis
         image: redis:6.2
   EOF
   kubectl wait --for=condition=Ready pod/test-pod-multi --timeout=180s
   ssh zain@10.10.10.131 'sudo crictl inspect $(sudo crictl ps -q --name=test-container-nginx) | jq ".info.runtimeSpec.linux.seccomp == null"
   sudo crictl inspect $(sudo crictl ps -q --name=test-container-redis) | jq ".info.runtimeSpec.linux.seccomp != null"
   sudo crictl inspectp $(sudo crictl pods -q --name test-pod-multi) | jq ".info.runtimeSpec.linux.seccomp != null"'
   ```

8. The exception the post does not mention, which `reference/node/seccomp.md:40-44` states flatly.
   One field defeats the node default silently, with nothing in the Pod's seccomp configuration to
   show for it:

   ```sh
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Pod
   metadata:
     name: test-pod-priv
   spec:
     nodeName: $WORKER
     containers:
       - name: test-container-priv
         image: nginx:1.21
         securityContext:
           privileged: true
   EOF
   kubectl wait --for=condition=Ready pod/test-pod-priv --timeout=120s
   ssh zain@10.10.10.131 'sudo crictl inspect $(sudo crictl ps -q --name=test-container-priv) \
     | jq "{seccomp: .info.runtimeSpec.linux.seccomp, privileged: .info.config.linux.security_context.privileged}"'
   ```

9. Inheritance, on the field surface the pin lists as four and the post lists as two. A Pod-level
   `Unconfined` with an init container that overrides it — the shape of the pin's own `fields.yaml`
   example, minus the `ephemeralContainers` block that example admits cannot be set at create time:

   ```sh
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Pod
   metadata:
     name: test-pod-inherit
   spec:
     nodeName: $WORKER
     securityContext:
       seccompProfile:
         type: Unconfined
     initContainers:
       - name: init-container
         image: nginx:1.21
         command: ["sleep", "300"]
         restartPolicy: Always
         securityContext:
           seccompProfile:
             type: RuntimeDefault
     containers:
       - name: main-container
         image: nginx:1.21
   EOF
   kubectl wait --for=condition=Ready pod/test-pod-inherit --timeout=120s
   ssh zain@10.10.10.131 'for c in init-container main-container; do printf "%s: " "$c"; sudo crictl inspect $(sudo crictl ps -q --name=$c) | jq -c ".info.runtimeSpec.linux.seccomp.defaultAction // \"none\""; done'
   kubectl explain pod.spec.securityContext.seccompProfile | head -8
   ```

10. Offline, read the paper trail this feature left. Two spellings of one switch, a gate file that
    exists without being a page, and a recommendation that points away from the post's advice:

    ```sh
    cd /path/to/kubernetes/website
    grep -rln --include='*.md' -- '--seccomp-default' content/en/docs
    grep -rln --include='*.md' 'seccompDefault' content/en/docs
    grep -c 'removed: true' content/en/docs/reference/command-line-tools-reference/feature-gates/SeccompDefault.md
    grep -rl 'removed: true' content/en/docs/reference/command-line-tools-reference/feature-gates/*.md | wc -l
    grep -n 'SeccompDefault\|feature gate\|kindest/node' content/en/docs/tutorials/security/seccomp.md
    grep -rn --include='*.md' 'strace' content/en/docs | wc -l
    sed -n '100,114p' content/en/docs/concepts/security/linux-kernel-security-constraints.md
    ```

**Expect**

Step 1 prints `seccompDefault: False` and an empty `featureGates` map for both nodes, and no
`--seccomp-default` in either `kubeadm-flags.env`. A cluster installed by `kubeadm` at v1.37 gives
every workload `Unconfined`, which is the state the post set out to change and the state the project
has left in place. Note that `configz` answers this question directly: the effective kubelet
configuration is readable through the API even though the resulting *profile* is not.

Step 2 prints a node name and then `null`. The post's manifest, unmodified, on a current cluster,
produces a container with no seccomp filter at all — the same result it would have produced in 2021
before enabling anything. Keep the node name: if the scheduler put this Pod on the worker, steps 5
and 6 will still be a clean comparison because the setting is not on yet.

Step 3 is the measurement. `systemctl is-active kubelet` should print something other than `active`,
and the journal should name `SeccompDefault` as an unrecognised or unsupported feature gate — the
exact wording varies by release, so copy it down. If your build instead logs a warning and starts,
record that instead; either way what you have is a configuration that follows the post's numbered
list precisely and leaves the node worse than not following it at all. The worker will go `NotReady`
a minute or two later, which is the visible cost of the post's step 1 at the pin.

Step 4 starts cleanly and prints `seccompDefault: True`. The post's `:74` — `The kubelet will error
on startup if only one of the above steps have been done` — is now false in the most direct way
available: doing only one of the two steps is the only configuration that works. The `WORKER` shell
variable is worth keeping for the rest of the exercise; the first `kubectl get --raw` line in that
step exists only to fail harmlessly if your node names differ from the derivation that follows.

Step 5 prints a `defaultAction` of `SCMP_ACT_ERRNO`, a list of architectures, a `rules` count and an
`allowed` count. The architecture list and both counts will differ from the post's output, which
came from CRI-O and runc; containerd's default profile is its own file with its own history. What
matches is the structure and the meaning: deny by default, allow a named set. This is the whole
feature, and it took one line in one file on one node.

Step 6 prints `true` for the control-plane container's profile being `null`, and then the comparison
that makes the point: the same image, the same empty `securityContext`, two nodes, two different
seccomp postures. The `jsonpath` line prints nothing for either Pod's `securityContext`, and
`describe` says nothing about seccomp for either. Everything the API can tell you about these two
Pods is identical, and the thing that differs is not in the API. That is `:128-131` holding four
years later, and it is also why Pod Security admission cannot credit this node for the profile it is
applying.

Step 7 prints `true`, `true`, `true` — the post's three assertions, unchanged, on a containerd
cluster with the gate it names deleted. The container that asked for `Unconfined` got `Unconfined`,
the container that asked for nothing got the node default, and the sandbox got the node default too.
The precedence rule behind the middle result is `reference/node/seccomp.md:36-38`: container fields
beat the Pod-level value, and unset containers inherit.

Step 8 prints a `seccomp` of `null` next to `privileged: true`. A privileged container on a node
with `seccompDefault: true` is unfiltered, and nothing in the Pod's seccomp configuration says so —
there is no field to inspect, no event, and no warning. The post's `it just changes the default
seccomp profile from Unconfined to RuntimeDefault` has one exception it does not name, and this is
the cheapest possible demonstration that a node-level default is not a guarantee.

Step 9 prints `SCMP_ACT_ERRNO` for the init container and `none` for the main one, then `kubectl
explain` describing `seccompProfile`. The Pod-level `Unconfined` propagated to the main container,
the init container's own field won, and the node default never entered into it — an explicit
Pod-level setting beats `seccompDefault` everywhere it appears. The init container has to carry
`restartPolicy: Always` to still be running when you inspect it; that is the sidecar form, and it is
one of the two field locations the pin lists that the post's era did not have.

Step 10 is a count of the feature's footprint. The hyphenated flag appears in two files, the
camel-case field in three, and only `tutorials/security/seccomp.md` contains both; the gate file
declares `removed: true` and is one of 230 that do; the last release in which that gate existed was
v1.28; the tutorial names the removed gate at `:454` and `:476` and calls it a feature gate twice
more at `:459` and `:475`, with its `kind` example pinned to `kindest/node:v1.28.0` at `:484` and
`:492` (the `v1.18.2` image at `:145` is an unrelated `docker ps` printout); `strace` returns a
count of `0`; and the `sed` prints a recommendation to use the runtime's bundled profile or a
sandbox rather than a profile of your own. Read that last block against the post's `_Optional_`
bullets and you are reading a change of strategy, not a change of fact.

**Read on**

1. `tutorials/security/seccomp.md:201-306` is the post's fourth testing bullet promoted to a
   tutorial step: an `audit.json` profile whose `defaultAction` is `SCMP_ACT_LOG`, applied to a Pod,
   with the resulting syscall log read off the node. It is the only place in the tree that does what
   the post suggests, and it needs `Localhost` profiles on disk — which is a different mechanism
   from everything this exercise touched.

2. `reference/node/seccomp.md:69-146` is the profile format itself: the OCI JSON scheme,
   `defaultErrnoRet`, and the eight action entries from `SCMP_ACT_ERRNO` to `SCMP_ACT_LOG`, with the
   note at `:128-135` that several of them may not work depending on the runtime, the OCI runtime or
   the kernel version. Read it next to the pin's own `fields.yaml` example, whose comment at `:9-10`
   admits that the `ephemeralContainers` block it contains cannot be used when creating a Pod.

3. `concepts/security/linux-kernel-security-constraints.md` is the page that did not exist when this
   post was written and now frames the whole subject: seccomp beside capabilities, AppArmor and
   SELinux, with a table at `:175-213` setting out what each mechanism is for. Its seccomp
   considerations at `:100-114` are the strategic reversal named above; read `:221-230` after them,
   where the Security Profiles Operator is recommended for managing custom configurations of all
   three mechanisms at scale — the post's own recommendation, arrived at from the opposite
   direction.

4. Three pieces of this exercise's machinery belong to other rows. [The CRI
   exercise](../2016/13-container-runtime-interface-cri-in-kubernetes.md) installs `crictl` and
   explains the socket and the RPCs behind every reading in this file. [The PID-limiting
   exercise](../2019/05-pid-limiting.md) is the kubelet drop-in directory and the per-node
   configuration change as a subject in itself. [The eleven-ways
   exercise](../2018/06-11-ways-not-to-get-hacked.md) sets `seccompProfile: RuntimeDefault`
   explicitly in every manifest, which is the other half of this story: the field, rather than the
   node default.

5. Unanswerable from the pin: why the default never moved. The gate completed its ladder, the
   documentation has recommended the behaviour since v1.27, and nothing in the tree argues against
   flipping `seccompDefault` to `true` — but nothing in the tree explains why it was not flipped
   either, and a gate file records stages, not reasons. Two smaller questions go the same way:
   whether the `privileged` exception at `reference/node/seccomp.md:40-44` held in v1.22, which the
   pin states without dating; and why the Security Profiles Operator, the post's own recommendation,
   is absent from both seccomp pages while being linked from three other security pages.

**Teardown**

This exercise left five Pods and one kubelet drop-in file. The drop-in is the only durable change,
and it is on the worker:

```bash
kubectl delete pod test-pod test-pod-cp test-pod-multi test-pod-priv test-pod-inherit --ignore-not-found
ssh zain@10.10.10.131 'sudo rm -f /etc/kubernetes/kubelet.conf.d/20-seccomp-gate.conf /etc/kubernetes/kubelet.conf.d/21-seccomp-default.conf'
ssh zain@10.10.10.131 'sudo systemctl restart kubelet; sleep 20; systemctl is-active kubelet'
for N in $(kubectl get nodes -o jsonpath='{.items[*].metadata.name}'); do
  kubectl get --raw "/api/v1/nodes/$N/proxy/configz"     | python3 -c 'import sys,json; print("seccompDefault:", json.load(sys.stdin)["kubeletconfig"].get("seccompDefault"))'
done
kubectl get nodes
```

Both nodes should report `seccompDefault: False` again and both should be `Ready`. Nothing was
installed and no API object outlived the Pods, so this returns the cluster to the state step 1
measured — a cluster where every workload runs `Unconfined` unless its author says otherwise. Leave
the two guests up if the next exercise in this year wants them; otherwise [destroy
them](../../strands/lab-topologies.md#teardown).
