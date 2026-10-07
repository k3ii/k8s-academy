<a id="kubeconfig"></a>
# Pass 0 — kubeconfig and contexts: which cluster are you talking to?

**Pass 0** · **untimed** · [`pair`](../../strands/lab-topologies.md#pair) · **No single domain** — mechanics under every drill

> **Worked live on 4–5 Oct.** The exam spans several clusters and every task begins by telling you to switch to one. A correct answer applied to the wrong cluster scores zero, with no error at any point.
>
> **Done when** you can say what a context actually is, and name two ways `kubectl` shows you an empty result that does not mean "empty".

---

<a id="three-lists"></a>
## 1. Three lists and a pointer

```yaml
clusters:         # WHERE -- an API server URL and its CA certificate
users:            # WHO   -- credentials: cert, token, or an exec plugin
contexts:         # PAIRINGS -- this user, against this cluster, in this namespace
current-context:  # which pairing is active
```

**A context is a named triple and nothing more.** It holds no connection and no state. Switching context does not connect to anything — it changes which three values `kubectl` reads on its next call. That is why [`k config set-context --current --namespace=…`](../workspace.md#shell) is instant: it edits a local file and contacts nobody.

```sh
k config view          # credentials come back REDACTED -- safe to read and share
k config view --raw    # prints the actual client cert and key -- DO NOT paste anywhere
```

Measured on `pair-cp`:

```yaml
clusters:  name: kubernetes                   server: https://10.10.10.130:6443
users:     name: kubernetes-admin             client-certificate-data, client-key-data
contexts:  name: kubernetes-admin@kubernetes  cluster + user + namespace
```

<a id="four-notes"></a>
### Four things that output tells you

- **It is a Kubernetes-shaped document that is not in Kubernetes.** `apiVersion: v1`, `kind: Config` — the same format as any manifest, but it lives at `~/.kube/config` and is **never submitted to any API**. Nothing in the cluster knows it exists.
- **Authentication is a client certificate, not a password.** Mutual TLS. There is no password anywhere in kubeadm's default admin setup: the API server trusts you because your certificate is signed by a CA it recognises, and your identity is a field inside that certificate. (**TS7** is what happens when that goes wrong.)
- **`https://10.10.10.130:6443`** is `pair-cp`'s LAN address and the API server's port. Every `k` command is an HTTPS request to that URL.
- **`<user>@<cluster>`** is kubeadm's naming convention for contexts, not a rule.

---

<a id="empty"></a>
## 2. What failure looks like — results that mean nothing

The context still named a namespace that had been deleted. Checked rather than guessed:

```sh
k get pods
# No resources found in scope namespace.

k get ns scope
# Error from server (NotFound): namespaces "scope" not found
```

**`k get pods` did not error.** A namespace that does not exist and a namespace that is empty produce **identical** output. Only `k get ns <name>` tells them apart.

Stacked against [the API surface](the-api-surface.md#get-all), there are now two independent ways to get a clean, confident, empty answer that means nothing:

| | |
|---|---|
| `k get all` | omits ConfigMaps, Secrets, PVCs, ServiceAccounts, Ingresses, NetworkPolicies, RBAC and every CRD |
| a wrong or mistyped namespace | returns an empty **list**, not an error |

> **"I looked and there was nothing there" is not evidence.** Confirm the namespace exists, and name your kinds explicitly.

---

<a id="commands"></a>
## 3. The commands

```sh
kubectl config get-contexts         # what exists, and which is live (the *)
kubectl config use-context <name>   # switch -- edits the local file, contacts nothing
kubectl config current-context      # confirm, one line
```

**The per-command override**, safer when unsure, because there is no state to forget to restore:

```sh
kubectl --context=<name> get nodes
```

**`KUBECONFIG`** selects a different file, or several joined by `:`, which are merged with first-wins on conflicts — how to work with a cluster without touching your default config:

```sh
export KUBECONFIG=~/.kube/config:~/lab.yaml
```

---

<a id="habit"></a>
## 4. The habit

Every exam task opens with the switch command it gives you. **Make the second keystroke your own:**

```sh
kubectl config current-context
```

One second, one line. Nothing in a `kubectl` response identifies which cluster answered, so there is no later opportunity to notice.

**The failure is silent and total.** On the wrong cluster the Deployment is created, the Service works, your own verification passes, and the grader reads a different machine. No error is produced at any stage.

> A live example, measured on this laptop: four contexts, with `*` on `rancher-desktop`. Every drill command run locally rather than over ssh would have gone to Rancher Desktop and succeeded — teaching nothing about the lab, and reporting no problem.
