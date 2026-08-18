<a id="10c3-encryption-that-lies"></a>
# 10.C3 — encryption is "on", the flag is set, and the Secret is plaintext on disk

**Claim** — with the *exact* `EncryptionConfiguration` from [exercise 12](12-a-secret-that-is-no-longer-plaintext-on-disk.md) but the provider array reordered so `identity` is **first**, the apiserver reports encryption configured, accepts every Secret, and writes them to etcd in plaintext — because the first provider in the list is the one used to *write*, and `identity` is the no-op provider whose "encryption" is the bytes unchanged. This is the config that lies: nothing errors, no flag is missing, and the at-rest guarantee is silently void. It is the single most dangerous misconfiguration in this phase because it *passes every check that does not read the disk*.

**Rests on** — [exercise 12](12-a-secret-that-is-no-longer-plaintext-on-disk.md), whose working config and etcd-read skill this drill inverts. Do that one first; this only makes sense as its negation.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. The encryption config from exercise 12 is still in place.

**Read** — re-read [the provider-ordering rule](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/): *the first provider is used to encrypt new writes; the rest are tried, in order, on read.* `identity` in a *later* slot is correct and necessary — it lets the apiserver read pre-encryption Secrets. `identity` in the *first* slot means every write is a no-op. The whole drill turns on that one positional fact.

**Do** — reorder the providers so `identity` leads, restart, write a fresh Secret, read its bytes:

```sh
ssh zain@10.10.10.130
# put identity first, aescbc second (invert exercise 12's order)
sudo tee /etc/kubernetes/enc.yaml >/dev/null <<'YAML'
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources: ["secrets"]
  providers:
  - identity: {}
  - aescbc:
      keys:
      - {name: k1, secret: REPLACE}
YAML
sudo sed -i "s#secret: REPLACE#secret: $(head -c 32 /dev/urandom | base64)#" /etc/kubernetes/enc.yaml
# the apiserver static pod reloads the file on write for newer versions; if not, bounce it:
sudo crictl ps --name kube-apiserver -q | xargs -r sudo crictl stop
```

After the apiserver is healthy again, write a Secret and read the raw key:

```sh
kubectl create secret generic liar --from-literal=pw=topsecret -n default
sudo ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get /registry/secrets/default/liar | hexdump -C | grep -A1 topsecret
```

**Observe** — the ASCII `topsecret` is right there in the dump, exactly as it was *before* encryption was ever configured in exercise 12 — and yet `kubectl get --raw /healthz` is `ok`, the `--encryption-provider-config` flag is set, and nothing logged an error. The `k8s:enc:aescbc:v1:` prefix from exercise 12 is gone; the value is bare. **The cluster's answer to "is encryption at rest enabled?" is yes, and it is telling the truth about the config and lying about the outcome.** This is why the phase's Write-down for encryption is *the on-disk bytes*, not the flag: only the disk can refute this.

**Expect** — plaintext on disk despite encryption "on". The one-line lesson: a security control that is verified by reading its configuration rather than its effect can be defeated by a configuration that is valid and wrong.

**Write down** — the plaintext dump, and one sentence naming the positional rule (`identity` first = no-op writes) that caused it.

**Teardown — this is a repair, not a delete.** Restore the correct order from exercise 12 (`aescbc` first, `identity` last), restart the apiserver, and re-verify one Secret encrypts before you leave — leaving the cluster in the lying state would poison every later exercise's Secrets:

```sh
# restore aescbc-first, restart, then rewrite Secrets and confirm k8s:enc: on disk again
kubectl delete secret liar -n default
```
