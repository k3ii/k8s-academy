<a id="ts05"></a>
# TS5 — A static pod is broken, so `kubectl` is dead: diagnose without it

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Troubleshooting / Troubleshoot cluster components

> **When the API server will not start, every tool you habitually reach for is gone at once.** No `kubectl get`, no events, no logs through the API. What remains is `/etc/kubernetes/manifests`, `crictl`, and `journalctl -u kubelet` — and the kubelet is still running, still watching that directory, still trying. Working comfortably in that reduced environment is a CKA competency and it cannot be faked.

**Break it** — *pass 1 only.* This is **F05**.

Introduce a malformed line into `/etc/kubernetes/manifests/kube-apiserver.yaml` — a bad indent, or an argument the binary will reject such as a nonexistent `--etcd-servers`. **Copy the file somewhere outside `/etc/kubernetes/manifests` first.** A backup left *inside* that directory is itself read as a static pod and will run a second API server, which is a worse fault than the one you planted.

**Work it**

- **Confirm the shape of the problem**: `kubectl` fails with a connection refused to `:6443`. Refused, not timed out — something is at that address and nothing is listening, which points at the local process rather than the network.
- **On the node.** `crictl ps -a` shows every container, including exited ones; this is the no-API-server equivalent of `kubectl get pods`. Find the apiserver container, note it is absent or repeatedly exiting.
- **`crictl logs <id>`** on the exited container. If the process started and rejected its flags, the reason is in there verbatim. This is the equivalent of `kubectl logs --previous` and it is the command people forget exists.
- **If no container was ever created**, the kubelet could not parse the manifest and never got that far — so the error is in `journalctl -u kubelet`, not in `crictl logs`. **Which of the two logs holds the answer tells you which kind of mistake you made**: YAML errors go to the kubelet, flag and runtime errors to the container. That fork is the real content of this drill.
- **Fix, then wait.** The kubelet rescans on a short interval; do not restart anything. Watch `crictl ps` until the container is up and stays up, then `kubectl get nodes`.
- Note while you are there that all four control-plane components live in this directory, that a static pod's name is the filename plus the node name, and that you cannot delete one with `kubectl` — it comes straight back, because the kubelet owns it, not the API server. Try that once.

**Observe**

```sh
kubectl get nodes                       # connection refused
sudo ls -l /etc/kubernetes/manifests/
sudo crictl ps -a | grep apiserver
sudo crictl logs <container-id> 2>&1 | tail -30
sudo journalctl -u kubelet -n 50 --no-pager
```

**Done when** — you fix it with the API server down throughout, and you go to the right log first based on whether a container was created.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Break it both ways — bad YAML, and a bad flag. | 10 min |
| **2** | Break `etcd` instead and work it the same way. | 8 min |
| **3** | **Injected.** **F05**, component unknown, `kubectl` dead on arrival. | **5 min** |

**Teardown** — `cka-inject.sh revert`, then **remove any backup file you left in `/etc/kubernetes/manifests`** and confirm exactly four manifests are present and all four components are `Running`.

**See also** — **TS6** is a component down that leaves `kubectl` working, which is a completely different experience; **B1** is where these manifests came from.
