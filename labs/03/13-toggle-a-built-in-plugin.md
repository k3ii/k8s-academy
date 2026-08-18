<a id="toggle-a-built-in-plugin"></a>
# Defaults that appear and vanish with one flag

**Claim** — several fields you have always seen on a Pod are not defaults in the schema at all; they are written by admission plugins, and turning one plugin off makes them stop existing. The apiserver will also tell you, in its own metrics, exactly which plugins ran for your request.

**Rests on** — [the refusal that never reached admission](07-rejected-at-authorization-not-admission.md), which asserted a plugin had not run. This exercise gives you the counter that proves it, and [module 3.2's opening claim](../../phases/03-api-machinery.md#m3-2) — that admission is just a function — is what it makes concrete.

**Topology** — **none.** `forge`, [the running apiserver](05-hand-start-an-apiserver.md).

**Do**

1. First, find out what is on. There is no flag that prints the enabled set, so read it from the source of truth for defaults — `pkg/kubeapiserver/options/plugins.go` — and answer: **which plugins are in the default-on list, and which of those are mutating?** The file distinguishes *registered* from *enabled by default*, and the distinction matters.

2. Create a plain Pod and note three fields nobody typed:

   ```sh
   kubectl --context=admin create -f - <<'YAML'
   apiVersion: v1
   kind: Pod
   metadata: {name: defaults, namespace: default}
   spec:
     containers: [{name: c, image: busybox}]
   YAML
   kubectl --context=admin get pod defaults -o yaml \
     | grep -E 'serviceAccount|volumeMounts|volumes|projected|tolerations' -A3
   ```

3. Read the admission metrics for that request:

   ```sh
   kubectl --context=admin get --raw /metrics \
     | grep '^apiserver_admission_controller_admission_duration_seconds_count' \
     | grep 'operation="CREATE"'
   ```

4. Restart the apiserver with the ServiceAccount plugin off:

   ```
   --disable-admission-plugins=ServiceAccount
   ```

   and create the identical Pod under a new name.

5. Restart once more with a plugin that is registered but **off** by default turned on — `--enable-admission-plugins=AlwaysPullImages` — and create the Pod a third time.

**Observe**

```sh
kubectl --context=admin get pod defaults  -o jsonpath='{.spec.serviceAccountName}{"\n"}'
kubectl --context=admin get pod nosa      -o jsonpath='{.spec.serviceAccountName}{"\n"}'
kubectl --context=admin get pod pullalways -o jsonpath='{.spec.containers[0].imagePullPolicy}{"\n"}'
kubectl --context=admin get --raw /metrics | grep 'admission_controller_admission_duration_seconds_count' | grep -c 'type="admit"'
```

**Expect** — the first Pod has `serviceAccountName: default`, a projected volume it did not ask for, and a `volumeMount` at `/var/run/secrets/kubernetes.io/serviceaccount`. **All three are written by one admission plugin**, and with it disabled the second Pod has none of them — no error, no warning, and a container that will never have a token.

`AlwaysPullImages` rewrites `imagePullPolicy` to `Always` regardless of what you set, which is the clearest possible demonstration that a mutating plugin can overwrite an explicit user choice, not merely fill a blank. That is worth sitting with before [you write one](22-the-mutating-webhook-cert-manager-signs.md).

The metrics are the payoff: one time series **per plugin per operation**, with a `type` label of `admit` or `validate`. Some plugins appear under both, which is the source of a common misreading — a plugin implementing both interfaces is not two plugins and does not run twice in one pass.

The likely stumble is that `--disable-admission-plugins` and `--enable-admission-plugins` are *both* deltas against the default list, not replacements. Passing `--enable-admission-plugins=AlwaysPullImages` does not turn everything else off; if you expected it to, the metrics will correct you immediately.

**Write down** — the three fields the ServiceAccount plugin writes, the metric name and its `type` label values, and one sentence you can use later: **"a field absent from a stored object may mean the user did not set it, or may mean a plugin is not running."** That ambiguity is the reason the metric exists.

**Teardown** — delete the three pods; restart the apiserver with the plugin flags **removed**, so the default set is back for the rest of the phase. Verify with a fresh pod that `serviceAccountName: default` returned. **The apiserver and etcd stay up. No topology is up.**
