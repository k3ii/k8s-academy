<a id="a-precondition-becomes-a-txn"></a>
# `resourceVersion` is etcd's `mod_revision`, wearing a different name

**Claim** — an object's `metadata.resourceVersion` **is** the etcd `mod_revision` of its key, and a write carrying a stale one fails because the apiserver turns it into an etcd transaction that compares that revision. You can read both numbers and find them equal.

**Rests on** — [P2's revision model](../../phases/02-etcd.md#m2-1) — `main`/`sub`, and what a `Txn` compares. This exercise is that machinery seen from the layer above, and the phase file's claim that P2 is *"the store the apiserver encodes onto"* becomes a number you can check.

**Topology** — **none.** `forge`, [the running apiserver](05-hand-start-an-apiserver.md) and its single-member etcd.

**Do**

1. Create an object and read its `resourceVersion`:

   ```sh
   kubectl --context=admin create configmap rv --from-literal=a=1
   kubectl --context=admin get configmap rv -o jsonpath='{.metadata.resourceVersion}{"\n"}'
   ```

2. Read the same key straight out of etcd and print the revision fields:

   ```sh
   etcdctl --endpoints=http://127.0.0.1:2379 \
     get /registry/configmaps/default/rv -w json \
     | jq '.kvs[0] | {create_revision, mod_revision, version}'
   ```

3. Update it three times and watch both numbers move together:

   ```sh
   for i in 2 3 4; do
     kubectl --context=admin create configmap rv --from-literal=a=$i --dry-run=client -o yaml \
       | kubectl --context=admin replace -f - >/dev/null
     printf 'k8s=%s  etcd=%s\n' \
       "$(kubectl --context=admin get cm rv -o jsonpath='{.metadata.resourceVersion}')" \
       "$(etcdctl --endpoints=http://127.0.0.1:2379 get /registry/configmaps/default/rv -w json | jq -r '.kvs[0].mod_revision')"
   done
   ```

4. Now force the conflict. Save an old copy, change the object, then replace with the stale one:

   ```sh
   kubectl --context=admin get cm rv -o yaml > /tmp/stale.yaml
   kubectl --context=admin patch cm rv --type=merge -p '{"data":{"a":"99"}}'
   kubectl --context=admin replace -f /tmp/stale.yaml
   ```

5. Read the code that made that a `Txn`. In `staging/src/k8s.io/apiserver/pkg/storage/etcd3/store.go`, find `GuaranteedUpdate`, and answer: **which `clientv3.Compare` does it build, on which field, and what is the `Then` branch versus the `Else` branch?** The `Else` branch is the interesting one — it does not just report failure.

**Observe**

```sh
etcdctl --endpoints=http://127.0.0.1:2379 watch --prefix /registry/configmaps/default/ -w json &
kubectl --context=admin patch cm rv --type=merge -p '{"data":{"a":"100"}}'
sleep 1; kill %1
grep -c 'ACADEMY 5-storage-write' /tmp/apiserver.log
```

**Expect** — the two numbers in step 3 are equal at every iteration, not merely close. They are the same number: the apiserver does not maintain a counter, it reports etcd's.

Step 4 fails with `409 Conflict` and the message *"the object has been modified; please apply your changes to the latest version and try again"*. That sentence is the user-facing form of a failed `Compare` on `mod_revision`.

The `Else` branch is where the surprise is: on a failed compare, etcd's transaction *returns the current value*, so the apiserver already holds the fresh object without a second round trip — which is why a conflicting `patch` retries transparently while a conflicting `replace` does not. That difference is not in etcd; it is in whether the caller supplied a precondition it insisted on.

Note also that `create_revision` and `mod_revision` are equal only for an object never updated, and that the k8s-side `resourceVersion` of a *list* is not any object's revision — it is the store's current revision, which is [what the watch cache is indexed by](33-overflow-the-ring.md).

**Write down** — the paired numbers from step 3, the exact `409` sentence, and the `file:function` of the `Compare`. Then one sentence connecting it to P2: *"a `resourceVersion` precondition is a `Txn` whose compare is …"*, completed with the field name from the source.

**Teardown** — `kubectl --context=admin delete configmap rv` and `rm /tmp/stale.yaml`. **The apiserver and etcd stay up. No topology is up.**
