<a id="how-we-made-kubernetes-easy-to-install"></a>
# The three stages in this post are still exactly right, all five of its own links are dead, and the hole its join command left open was renamed rather than closed

**Post** — [How we made Kubernetes insanely easy to install](https://kubernetes.io/blog/2016/09/how-we-made-kubernetes-easy-to-install/),
2016-09-28, Kubernetes v1.4 — Luke Marsden of Weaveworks, writing for SIG-cluster-lifecycle, on
the arrival of `kubeadm`. The post says twice that the tool is not finished: *"It's still in
**alpha**, but it works like this"*.

**As written** — the post's argument is a division of labour. Setting up a cluster has three
stages, and `kubeadm` deliberately takes only the last two:

> 1. **Provisioning**: getting some machines
> 2. **Bootstrapping**: installing Kubernetes on them and configuring certificates
> 3. **Add-ons**: installing necessary cluster add-ons like DNS and monitoring services, a pod
>    network, etc

The reason for the omission is stated plainly, and it is the most durable sentence in the post:

> They use lots of different cloud providers, private clouds, bare metal, or even Raspberry Pi's,
> and almost always have their own preferred tools for automating provisioning machines: Terraform
> or CloudFormation, Chef, Puppet or Ansible, or even PXE booting bare metal. So we made an
> important decision: **kubeadm would not provision machines**.

The second stated constraint is about where the work belongs:

> Another important constraint was we didn't want to just build another tool that "configures
> Kubernetes from the outside, by poking all the bits into place". [...] We chose to actually
> improve the Kubernetes core itself to make it easier to install.

Then the procedure, five bullets, and no code block anywhere in the post:

> - You install Docker and the official Kubernetes packages for you distribution.
> - Select a master host, run kubeadm init.
> - This sets up the control plane and outputs a kubeadm join [...] command which includes a secure
>   token.
> - On each host selected to be a worker node, run the kubeadm join [...] command from above.
> - Install a pod network. Weave Net is a great place to start here. Install it using just kubectl
>   apply -f https://git.io/weave-kube

Note what the third and fourth bullets say and do not say. The join command is described entirely
by one thing it carries — *"a secure token"* — and the post never prints it. The security model of
the whole procedure is compressed into the adjective.

**As it runs now** — the division of labour survived intact and the commands did not.

The three stages are still the shape of a bring-up, and the pin's own `kubeadm init` page ends its
workflow on the dependency the post's stage 3 implies. Its last step reads:

> Installs a DNS server (CoreDNS) and the kube-proxy addon components via the API server.
> Please note that although the DNS server is deployed, it will not be scheduled until CNI is
> installed.
>
> — `docs/reference/setup-tools/kubeadm/kubeadm-init.md`

That is the post's stage 3 written as a control-plane property: `kubeadm` still hands you a cluster
that is not finished, and still declines to finish it.

Four things in the five bullets have moved.

**The first bullet's runtime is now the wrong runtime.** The pin's install page carries a note
against the post's opening instruction:

> Docker Engine does not implement the [CRI](/docs/concepts/architecture/cri/) which is a
> requirement for a container runtime to work with Kubernetes. For that reason, an additional
> service [cri-dockerd](https://mirantis.github.io/cri-dockerd/) has to be installed.
>
> — `docs/setup/production-environment/tools/kubeadm/install-kubeadm.md:139-143`

Installing Docker is now a step that produces a node the kubelet cannot use without a shim. That
change has its own exercise later in this year and is left there.

**The third and fourth bullets' join command grew a second secret.** The pin names three discovery
modes with three different trust models, and the post's procedure is the middle one:

> #### Token-based discovery with CA pinning
>
> This is the default mode in kubeadm. In this mode, kubeadm downloads the cluster configuration
> (including root CA) and validates it using the token as well as validating that the root CA
> public key matches the provided hash and that the API server certificate is valid under the root
> CA.
>
> — `docs/reference/setup-tools/kubeadm/kubeadm-join.md`

and the mode the post actually describes is the one below it:

> #### Token-based discovery without CA pinning
>
> This mode relies only on the symmetric token to sign (HMAC-SHA256) the discovery information that
> establishes the root of trust for the control-plane. To use the mode the joining nodes must skip
> the hash validation of the CA public key, using `--discovery-token-unsafe-skip-ca-verification`.
> You should consider using one of the other modes if possible.

The pin states the exposure the post's *"secure token"* left open, in the same section:

> If an attacker is able to steal a bootstrap token via some vulnerability, they can use that token
> (along with network-level access) to impersonate the control-plane node to other bootstrapping
> nodes.

**The fifth bullet's pod network survives in the docs as a description that was never updated
attached to a URL that was.** The pin's add-ons page still carries Weave Net's 2016 sentence —

> [Weave Net](https://github.com/rajch/weave#using-weave-on-kubernetes) provides networking and
> network policy, will carry on working on both sides of a network partition, and does not require
> an external database.
>
> — `docs/concepts/cluster-administration/addons.md:94-96`

— and the link under it points at a personal account, not at `weaveworks/weave-kube`, which is
what the post's one-liner installed. The one-liner's host, `git.io`, appears nowhere at the pin.

**And all five of the post's own links are the same dead path.** `/docs/getting-started-guides/kubeadm/`
appears four times, plus once with a `#prerequisites` anchor. At the pin, `getting-started-guides`
survives only inside other blog posts; nothing under `docs/` uses that tree. Its successor is
`docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm.md`, which is one page
among ten in that directory.

**The diff, and why** — this is the post that is still right, and the one place it is not right is
the place it was vaguest.

Everything the post argues for is now load-bearing. Provisioning was never absorbed: the pin's
install page still opens on machine requirements — *"2 GB or more of RAM per machine"*, *"2 CPUs or
more for control plane machines"*, unique hostname, MAC address and `product_uuid` — and expects
you to have arrived with them. The three stages are still three. The choice to *"actually improve
the Kubernetes core itself"* rather than poke bits into place is why `kubeadm init` can be
described, at the pin, as nine steps of ordinary API and filesystem work rather than as a template
engine.

The tool's own alpha label resolved in a way worth noticing. `kubeadm alpha` is still a page at the
pin, and it exists to say it is empty: *"Currently there are no experimental commands under
`kubeadm alpha`."* The word survived the tool it once qualified, as a namespace with nothing in it.

The join command is the exception, and it is a specific kind of exception: **the post did not
describe an insecure command, it described a command without saying which of its properties were
doing the security work.** *"A kubeadm join [...] command which includes a secure token"* is true.
The token is secure — it is a bearer credential over TLS. What the sentence omits is that a bearer
credential alone cannot tell the joining node *whose* TLS it is talking to. A node holding only a
token will trust the first API server that answers with a plausible cluster configuration, which is
trust on first use, and the pin spells out what that costs.

The fix was not to make the hash mandatory. It was to make the omission unspeakable. At the pin you
can still join with a token alone — you simply cannot do it without typing
`--discovery-token-unsafe-skip-ca-verification`, a flag that names the tradeoff in the middle of
itself. The hole is exactly as open as it was in 2016 and is now impossible to fall into. That is a
different repair from the ones the rest of this year records: nothing was removed, renamed, or
regrouped. A default was inverted and a name was made to carry an argument.

Which makes this post's census row the loose one in the year. It says the hash *"is now mandatory
and the post's `kubeadm join` line fails without it"*. The second half is exact. The first half is
not: two of the pin's three discovery modes need no hash at all, and the mode the post describes is
still documented, still supported, and still reachable by asking for it. Rows are immutable, so the
row stands and the correction lives here.

**The ladder** — this post's feature has no gate file, and the reason is instructive.

`kubeadm` is not a component the API server gates. It carries **its own** feature gates, applied
only at `kubeadm init`, and the pin says so:

> kubeadm supports a set of feature gates that are unique to kubeadm and can only be applied during
> cluster creation with `kubeadm init`. [...] Passing feature gates for core Kubernetes components
> directly to kubeadm is not supported.
>
> — `docs/reference/setup-tools/kubeadm/kubeadm-init.md:135-142`

So the transcription source is not `stages:` frontmatter but two prose tables, and they are the
ladder **transposed** — one row per feature, with the stages as columns, and no default-value or
locked column at all. Transcribed losslessly, as they stand at the pin:

```
kubeadm feature gates
| Feature                | Default | Alpha | Beta | GA | Deprecated |
|------------------------|---------|-------|------|----|------------|
| `RootlessControlPlane` | `false` | 1.22  | -    | -  | 1.31       |

kubeadm removed feature gates
| Feature                           | Alpha | Beta | GA   | Removed |
|-----------------------------------|-------|------|------|---------|
| `ControlPlaneKubeletLocalMode`    | 1.31  | 1.33 | 1.35 | 1.36    |
| `EtcdLearnerMode`                 | 1.27  | 1.29 | 1.32 | 1.33    |
| `IPv6DualStack`                   | 1.16  | 1.21 | 1.23 | 1.24    |
| `NodeLocalCRISocket`              | 1.32  | 1.34 | 1.36 | 1.37    |
| `PublicKeysECDSA`                 | 1.19  | -    | -    | 1.37    |
| `UnversionedKubeletConfigMap`     | 1.22  | 1.23 | 1.25 | 1.26    |
| `UpgradeAddonsBeforeControlPlane` | 1.28  | -    | -    | 1.31    |
| `WaitForAllControlPlaneComponents`| 1.30  | 1.33 | 1.34 | 1.35    |
```

Eight of those nine names have no file under
`docs/reference/setup-tools/kubeadm/../command-line-tools-reference/feature-gates/`, which holds
488 of them. One does — and the two sources disagree.

`IPv6DualStack.md`'s `stages:` list, parsed as YAML, gives:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.15 – v1.20 |
| beta | `true` | — | v1.21 – v1.22 |
| stable | `true` | — | v1.23 – v1.24 |

with `removed: true` declared at file level. kubeadm's table above puts the same name at alpha in
**1.16**, and it fits `1.21` and `1.23` against the gate file's `beta` and `stable`. The gate file
says alpha ran through 1.20; kubeadm's row implies beta began the release after alpha. Both
documents are at the pin, both spell the gate identically, and their alpha releases are one apart.
Neither is annotated as being about a different gate. Cite both when this comes up; do not pick.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), fresh, and fresh is not optional:
the exercise joins a node twice under two different trust models and resets it in between, so the
worker has to be disposable. Bring the topology up with
[the five provision steps](../../strands/lab-topologies.md#provision) using `topology=pair`,
install the packages on **both** nodes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps) — and stop
there, initialising nothing — then `ssh zain@10.10.10.130`.

The standard bring-up, walked slowly with commentary, is already the curriculum's first kubeadm
lab. This exercise does not repeat it. Step 1 below is one command and no discussion; the subject
starts at step 2.

**Do**

1. On `.130`, take stage 2 in a single line, and keep its output:

   ```sh
   sudo kubeadm init --pod-network-cidr=10.244.0.0/16 \
     --apiserver-advertise-address=10.10.10.130 | tee ~/init.log
   ```

   Then the `mkdir -p $HOME/.kube` incantation it prints, so `kubectl` answers.

2. Extract the join line the post promised and count its secrets:

   ```sh
   grep -A2 'kubeadm join' ~/init.log
   ```

   The post says this command *"includes a secure token"*. Count how many `--` arguments carry a
   secret. Write down what the second one is for before you use it.

3. Take stage 3, so that the rest of the exercise is not competing with a `Pending` CoreDNS:
   install Flannel, one manifest, and watch `kubectl get pods -n kube-system` settle. Note that
   `kubeadm` did deploy CoreDNS and did not schedule it — the pin's `kubeadm init` workflow says it
   would not, and this is that sentence happening.

4. **Now run the post's procedure literally.** On `.131`, join with the token alone — the token
   from step 2, no second argument:

   ```sh
   sudo kubeadm join --token <token> 10.10.10.130:6443
   ```

   Read the refusal in full. It names what it wants and it offers you two ways out. Which of the
   pin's three discovery modes is each way out?

5. Take the way out that reproduces 2016, and read what you have to type to get it:

   ```sh
   sudo kubeadm join --token <token> \
     --discovery-token-unsafe-skip-ca-verification 10.10.10.130:6443
   ```

   The node joins. Confirm from `.130` with `kubectl get nodes`. The post's procedure works
   unchanged; the only change is the eleven syllables in the middle of it.

6. Undo it and do it properly. On `.131`:

   ```sh
   sudo kubeadm reset -f
   sudo kubeadm join --token <token> \
     --discovery-token-ca-cert-hash sha256:<hash> 10.10.10.130:6443
   ```

   `kubeadm reset -f` prints a short list of things it did not clean up. Read it; one of the items
   is why step 5 and step 6 can both succeed on the same host.

7. Derive the hash yourself rather than copying it, with the pipeline the pin gives:

   ```sh
   openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt \
     | openssl rsa -pubin -outform der 2>/dev/null \
     | openssl dgst -sha256 -hex | sed 's/^.* //'
   ```

   Compare it to the value `kubeadm init` printed in step 2. It hashes the CA's **public key**, not
   the certificate — the pin cites [RFC7469](https://tools.ietf.org/html/rfc7469#section-2.4) for
   the format. Say what that buys: which cluster changes would leave this value the same?

8. The token in step 2 expires. Get the whole command back in its modern form:

   ```sh
   sudo kubeadm token create --print-join-command
   ```

   Diff it against the post's third bullet. Every difference is something the post's sentence was
   silent about rather than something the post got wrong.

9. Test the post's first bullet against the node you are on:

   ```sh
   sudo crictl --runtime-endpoint unix:///run/containerd/containerd.sock version
   which docker || echo 'no docker on this node'
   ```

   The cluster you just built has no Docker anywhere in it. Reconcile that with the post's opening
   instruction.

10. Look for the tool's alpha label:

    ```sh
    kubeadm alpha --help
    ```

    Then chase the post's own reading list — its five links all point at
    `/docs/getting-started-guides/kubeadm/`. Nothing under the pin's `docs/` tree uses that path.
    Name the page you would send a 2026 reader to instead, and say how many pages the successor
    directory holds.

**Expect**

```sh
kubectl get nodes -o wide
kubectl get pods -n kube-system -o wide
kubectl get configmap -n kube-public cluster-info -o yaml
kubectl get secrets -n kube-system | grep bootstrap-token
```

Two nodes `Ready`, the worker having been joined twice by two different routes. `cluster-info` in
`kube-public` is the object the joining node reads *before* it trusts anything; open it and find the
CA certificate sitting in a ConfigMap that is readable without credentials. That is the whole reason
step 4 refuses: the data is public, so the token can prove nothing about who served it, and only the
hash can. The bootstrap-token Secret is where the token in step 2 lives, and it carries an
expiry — the post's *"secure token"* is secure partly because it is short-lived, which the post also
does not say.

By the end you should be able to state which of the post's five bullets you would still hand to
someone today, and for the two you would not, whether the reason is that Kubernetes changed or that
the sentence was underspecified when it was written.

**Read on** — the pin's
[`kubeadm join` discovery section](https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-join/#discovering-what-cluster-ca-to-trust)
lists the third mode this exercise does not use, `--discovery-file`, and gives its advantages in the
same shape as the other two. Read it against step 5 and answer: if the file is fetched over HTTPS
from a URL, what has replaced the CA hash as the thing establishing trust, and where did that trust
have to be configured?

**Teardown** — [the teardown step](../../strands/lab-topologies.md#teardown). The worker in this
exercise has been `kubeadm reset` once and joined twice; do not carry it into another exercise.
