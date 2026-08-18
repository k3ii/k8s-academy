<a id="one-object-read-out-of-etcd"></a>
# What is actually stored is not YAML, and not JSON either

**Claim** — the bytes under `/registry/...` are protobuf with a four-byte magic prefix, not the JSON `kubectl` shows you; the key layout is `/registry/<resource>/<namespace>/<name>` with cluster-scoped resources one segment shorter; and you can make the same object store as JSON by changing one apiserver flag, then see the difference byte for byte.

**Rests on** — [the revision equality](09-a-precondition-becomes-a-txn.md), which established that you are looking at the same object from two sides. This is the *encoding* half of the same seam, and it is [module 3.1's bottom-of-the-stack question](../../phases/03-api-machinery.md#m3-1).

**Topology** — **none.** `forge`, [the running apiserver](05-hand-start-an-apiserver.md) and its etcd.

**Do**

1. List the key space and describe its shape in one sentence before looking at any value:

   ```sh
   etcdctl --endpoints=http://127.0.0.1:2379 get --prefix --keys-only /registry | sort | head -40
   ```

   Find one namespaced resource and one cluster-scoped one, and say how many segments each key has and why they differ.

2. Look at the raw value of a ConfigMap you can predict the contents of:

   ```sh
   kubectl --context=admin create configmap enc --from-literal=hello=world
   etcdctl --endpoints=http://127.0.0.1:2379 get /registry/configmaps/default/enc | head -c 400 | xxd | head -20
   ```

3. Read the first four bytes. Then find what writes them: in `staging/src/k8s.io/apiserver/pkg/storage/value/`, and in `staging/src/k8s.io/apimachinery/pkg/runtime/serializer/protobuf/protobuf.go`, answer — **what is the magic prefix, what is it for, and what would the apiserver do if it read a value that did not start with it?**

4. Now flip the storage media type. Restart the apiserver with one extra flag:

   ```
   --storage-media-type=application/json
   ```

   and create the *same* ConfigMap again under a new name:

   ```sh
   kubectl --context=admin create configmap enc-json --from-literal=hello=world
   etcdctl --endpoints=http://127.0.0.1:2379 get /registry/configmaps/default/enc-json
   ```

5. Read `enc` — created *before* the flag change — with the apiserver still in JSON mode.

**Observe**

```sh
etcdctl --endpoints=http://127.0.0.1:2379 get /registry/configmaps/default/enc     | wc -c
etcdctl --endpoints=http://127.0.0.1:2379 get /registry/configmaps/default/enc-json | wc -c
kubectl --context=admin get configmap enc -o yaml | head -5
kubectl --context=admin get configmap enc-json -o yaml | head -5
```

**Expect** — the protobuf value begins `k8s\x00` and then, in the middle of otherwise unreadable bytes, contains **readable ASCII**: the group, version and kind, and your literal `hello`/`world`. Protobuf does not encrypt anything, and this is the single most useful fact about etcd for [P10](../../phases/10-security.md): a Secret at rest is a base64 payload in a file anyone with the disk can read, which is what encryption-at-rest exists for and why it is a *separate* feature.

The JSON-stored ConfigMap is larger and completely readable. Both are readable by `kubectl` afterwards, and **that is the point of step 5**: the apiserver detects the encoding of what it reads rather than assuming its own configured one — which is what makes changing `--storage-media-type` on an existing cluster survivable at all, and what the magic prefix is for.

The likely trap: `etcdctl get` prints the value to a terminal that will interpret control characters. Always pipe through `xxd`, `strings` or `wc -c`, never straight to the screen — a raw protobuf object will happily reset your terminal.

**Write down** — the key layouts for one namespaced and one cluster-scoped resource, the magic prefix in hex, the two byte counts, and one sentence for the P10 note: *"what is protected at rest by default is …"*.

**Teardown** — `kubectl --context=admin delete configmap enc enc-json`, and **remove `--storage-media-type` from the flag set** before restarting — the rest of the phase assumes the default. Confirm with a fresh object that the prefix is back:

```sh
kubectl --context=admin create configmap check --from-literal=x=1
etcdctl --endpoints=http://127.0.0.1:2379 get /registry/configmaps/default/check | head -c 8 | xxd
kubectl --context=admin delete configmap check
```

**The apiserver and etcd stay up. No topology is up.**
