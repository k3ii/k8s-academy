<a id="w09"></a>
# W9 — A Secret from a literal and from a file, consumed as a volume

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Workloads and Scheduling / ConfigMaps and Secrets

> **A Secret is a ConfigMap with base64 in the API and `tmpfs` on the node, and that is nearly the whole difference.** It is encoded, not encrypted — `get -o yaml` plus `base64 -d` reads any Secret you can get. Being precise about what a Secret does and does not protect is the point of this drill, because the exam asks for Secrets in places where the protection is nominal.

**Do**

1. `kubectl create secret generic` three ways: `--from-literal`, `--from-file`, and `--from-file=key=path`. Read each back and decode it. Confirm for yourself that the API stores base64, not ciphertext.
2. **Write one as YAML by hand**, which is where the two fields matter: `data` expects base64 and `stringData` takes plaintext and encodes it for you. `stringData` is the one to use under time pressure, and it does not survive a read-back — it reappears as `data`. Prove that.
3. Mount it as a volume. Check the permissions: `0644` by default, and `defaultMode`/`mode` set it. Check the filesystem type on the node — it is `tmpfs`, so it never touches disk.
4. Consume one key as an env var with `secretKeyRef`, and note that the same freeze applies as in **W8**: env is read once, the mounted file updates.
5. **The typed Secrets you will actually be asked for.** `kubernetes.io/dockerconfigjson` via `create secret docker-registry`, referenced by `imagePullSecrets` — go and look at the pod field, because the Secret alone does nothing. And `kubernetes.io/tls` via `create secret tls`, which an Ingress references. Both have dedicated subcommands worth knowing.
6. A ServiceAccount's token is a Secret-shaped thing that is no longer auto-created — see **A4** rather than looking for one here.

**Observe**

```sh
kubectl create secret generic db --from-literal=pass=s3cr3t
kubectl get secret db -o jsonpath='{.data.pass}' | base64 -d; echo
kubectl exec web -- ls -l /etc/sec/
kubectl exec web -- mount | grep /etc/sec        # tmpfs
kubectl create secret tls web-tls --cert=tls.crt --key=tls.key
kubectl get secret -o custom-columns=NAME:.metadata.name,TYPE:.type
```

**Done when** — all three `create secret` subcommands run from memory, you can decode any Secret in one line, and you can say in a sentence what a Secret protects against and what it does not.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Three creates, both consumers, both typed Secrets. | 10 min |
| **2** | An existing Secret in use. Rotate its value with no downtime. | 8 min |
| **3** | Cold, no notes. TLS Secret from a cert and key, mounted. | 5 min |

**Teardown** — delete the namespace, and any cert files you generated on disk.

**See also** — **W8** is the ConfigMap half and the env-against-volume rule; **A4** is the ServiceAccount token.
