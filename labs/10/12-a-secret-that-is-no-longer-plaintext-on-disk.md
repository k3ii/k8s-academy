<a id="a-secret-that-is-no-longer-plaintext-on-disk"></a>
# The same Secret, read straight out of etcd, before and after encryption at rest

**Artifact** — two hex dumps of the *same* etcd key: one where the Secret's value is legible ASCII, and one — after an `EncryptionConfiguration` is in force and the Secret is rewritten — where the value is a `k8s:enc:aescbc:v1:` prefix followed by ciphertext. Encryption at rest is a claim the cluster makes; this exercise is the claim's audit, read from the bytes the disk actually holds, not from a flag that says it is on.

**Rests on** — [reading a raw etcd key straight off disk](../../phases/02-etcd.md#m2-1) from P2 — the same `etcdctl get` skill, now pointed at a Secret instead of a hand-written key. That P2 skill is the prerequisite tool; this exercise is what it is for.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — [the encryption-at-rest task](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/): the apiserver reads an `EncryptionConfiguration` file named by `--encryption-provider-config`; each resource lists an ordered array of providers, and *the first provider is used to write*. Hold the question that [exercise 15](15-10c3-encryption-that-lies.md) will exploit: *if `identity` (the no-op provider) is first in the list, what does the apiserver write* — and does the flag being present tell you anything about that?

**Do — read it plaintext first.** On the control-plane node:

```sh
ssh zain@10.10.10.130
kubectl create secret generic before --from-literal=pw=hunter2 -n default
# read the raw value straight from etcd (adjust cert paths to your P2 setup)
sudo ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get /registry/secrets/default/before | hexdump -C | grep -A1 hunter2
```

**Do — turn encryption on.** Write the config, point the apiserver at it, let the static pod restart:

```sh
sudo tee /etc/kubernetes/enc.yaml >/dev/null <<'YAML'
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources: ["secrets"]
  providers:
  - aescbc:
      keys:
      - name: k1
        secret: $(head -c 32 /dev/urandom | base64)
  - identity: {}
YAML
# fill the key in (the heredoc did not expand it):
sudo sed -i "s#secret: .*#secret: $(head -c 32 /dev/urandom | base64)#" /etc/kubernetes/enc.yaml
sudo sed -i '/- kube-apiserver/a\    - --encryption-provider-config=/etc/kubernetes/enc.yaml' /etc/kubernetes/manifests/kube-apiserver.yaml
# mount the file into the static pod (add a hostPath volume + volumeMount) — see the task page for the exact stanza
```

Existing Secrets are *not* rewritten by turning encryption on — only new writes are. So force a rewrite of every Secret, then read the same key again:

```sh
kubectl get secrets --all-namespaces -o json | kubectl replace -f -
sudo ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get /registry/secrets/default/before | hexdump -C | head
```

**Observe** — the first dump contains the ASCII `hunter2`; the second begins `k8s:enc:aescbc:v1:k1` and then bytes with no legible run. The Secret the API returns is identical in both cases (`kubectl get secret before -o jsonpath='{.data.pw}' | base64 -d` is still `hunter2`) — the apiserver decrypts on read. **On disk it changed; through the API it did not.** That gap is the entire point of encryption at rest: it defends the etcd file, not the API.

**Expect** — `k8s:enc:aescbc:v1:` on disk, `hunter2` through the API. If the second dump is still plaintext, the rewrite did not happen (or `identity` ended up first — which is [exercise 15](15-10c3-encryption-that-lies.md), do not fix it there by accident here).

**Write down** — the two hex dumps' first lines side by side, and the one sentence that names what encryption-at-rest does and does not protect.

**Teardown** — the encryption config is a keeper; delete only the test Secret; **the topology stays**:

```sh
kubectl delete secret before -n default
```
