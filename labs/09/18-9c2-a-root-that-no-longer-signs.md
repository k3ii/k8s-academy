<a id="9c2-a-root-that-no-longer-signs"></a>
# 9.C2 — replace the root CA under a running mesh: two workloads, two issuers, one trust bundle

**Artifact** — drill [9.C2](../../phases/09-service-mesh.md#chaos): the root CA deleted and regenerated under a live mesh, with **the two workloads' issuers printed side by side** and the resulting TLS failure read from Envoy's counters and logs rather than from `curl`'s exit code. Recovery is part of the artifact: the original root is backed up before anything is deleted, restored afterwards, and the restoration is proved.

**Rests on** — [the certificate exercise](15-a-certificate-that-names-a-serviceaccount.md) for the root fingerprint you recorded, and [`STRICT`](16-strict-and-the-plaintext-refused.md), which must still be in force — without it a broken trust chain could fall back to plaintext and the drill would prove nothing. Mechanism is **by hand**, per [the drill table](../../phases/09-service-mesh.md#chaos).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — back up the root first.** This is the one drill in the phase that can leave the mesh unable to issue any certificate at all, and the backup is the difference between a five-minute recovery and a reinstall:

```sh
kubectl -n istio-system get secret istio-ca-secret -o json \
  | jq 'del(.metadata.resourceVersion,.metadata.uid,.metadata.creationTimestamp,.metadata.managedFields)' \
  > ~/istio-ca-secret.backup.json
test -s ~/istio-ca-secret.backup.json && echo "backup written"
for w in sleep httpbin; do
  printf '%-8s ' $w
  istioctl -n mesh proxy-config secret deploy/$w -o json \
    | jq -r '.dynamicActiveSecrets[] | select(.name=="ROOTCA") | .secret.validationContext.trustedCa.inlineBytes' \
    | base64 -d | openssl x509 -noout -fingerprint
done
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w '%{http_code}\n' http://httpbin:8000/get
```

**Do — remove the root and let `istiod` generate a new one:**

```sh
kubectl -n istio-system delete secret istio-ca-secret
kubectl -n istio-system rollout restart deploy istiod
kubectl -n istio-system rollout status deploy istiod
kubectl -n istio-system get secret istio-ca-secret -o jsonpath='{.metadata.creationTimestamp}'; echo
```

**Do — restart one workload only.** The asymmetry is the drill: `sleep` gets a leaf signed by the new root, `httpbin` keeps a leaf signed by the old one until its own rotation comes due:

```sh
kubectl -n mesh delete pod -l app=sleep
kubectl -n mesh rollout status deploy sleep
for w in sleep httpbin; do
  printf '=== %s\n' $w
  istioctl -n mesh proxy-config secret deploy/$w -o json \
    | jq -r '.dynamicActiveSecrets[] | select(.name=="default") | .secret.tlsCertificate.certificateChain.inlineBytes' \
    | base64 -d | openssl x509 -noout -issuer -dates
  istioctl -n mesh proxy-config secret deploy/$w -o json \
    | jq -r '.dynamicActiveSecrets[] | select(.name=="ROOTCA") | .secret.validationContext.trustedCa.inlineBytes' \
    | base64 -d | openssl x509 -noout -fingerprint
done
```

**Observe — try both directions, and read the failure where it happened:**

```sh
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -m 5 -o /dev/null -w 'sleep -> httpbin: %{http_code}\n' http://httpbin:8000/get
kubectl -n mesh exec deploy/httpbin -c istio-proxy -- pilot-agent request GET stats | grep -E 'ssl\.(connection_error|fail_verify)' | head
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET stats | grep -E 'ssl\.(connection_error|fail_verify)' | head
kubectl -n mesh logs deploy/sleep -c istio-proxy --tail=30 | grep -iE 'verify|handshake|tls'
kubectl -n mesh logs deploy/httpbin -c istio-proxy --tail=30 | grep -iE 'verify|handshake|tls'
```

**Expect** — a **new `istio-ca-secret` with a fresh creation timestamp** and a root fingerprint that differs from the one in your notes. Expect the two workloads to end up with **different issuers on their leaf certificates**, which is the state this drill manufactures and the reason it is worth doing: a mesh mid-rotation is not a mesh with one CA.

Expect at least one direction of traffic to fail with a **certificate verification error in the Envoy logs** — `certificate verify failed` or an `ssl.connection_error` counter climbing — and expect the client's `curl` to report only a reset, as it did under [`STRICT`](16-strict-and-the-plaintext-refused.md).

**Predict which direction fails before you run it, then record what actually happened.** The trust bundle (`ROOTCA`) is pushed to every proxy over SDS as soon as `istiod` has it, while leaf certificates are only reissued on restart or rotation — so a proxy can be validating peers against a root that did not sign its own certificate. Whether that produces a failure in one direction, in both, or in neither depends on whether your Istio version pushes a **combined** bundle containing both roots during the transition. All three outcomes are informative and only one of them is a surprise; what is not acceptable is writing down the outcome you expected instead of the one you got.

Expect the blast radius to **grow with time rather than shrink**, and say so in the notes. Every workload that restarts or rotates crosses to the new root; every one that does not, drifts further from it. A root replacement is not an event, it is a window — bounded by the certificate lifetime you measured in [the identity exercise](15-a-certificate-that-names-a-serviceaccount.md).

**Write down** — in `journal/p9-9c2.md`: the two root fingerprints, the two leaf issuers, the direction that failed, the Envoy-layer evidence, and the outage window in hours implied by the certificate lifetime. One sentence on why a production mesh uses an **external** root whose private key `istiod` never holds — the drill you just ran is exactly the failure that design removes.

**Teardown — restore the original root and prove the mesh converged again:**

```sh
kubectl -n istio-system delete secret istio-ca-secret
kubectl apply -f ~/istio-ca-secret.backup.json
kubectl -n istio-system rollout restart deploy istiod
kubectl -n istio-system rollout status deploy istiod
kubectl -n mesh delete pod -l app=sleep
kubectl -n mesh delete pod -l app=httpbin
kubectl -n mesh rollout status deploy sleep && kubectl -n mesh rollout status deploy httpbin
for w in sleep httpbin; do
  printf '%-8s ' $w
  istioctl -n mesh proxy-config secret deploy/$w -o json \
    | jq -r '.dynamicActiveSecrets[] | select(.name=="ROOTCA") | .secret.validationContext.trustedCa.inlineBytes' \
    | base64 -d | openssl x509 -noout -fingerprint
done
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w '%{http_code}\n' http://httpbin:8000/get
```

**Both fingerprints back to the one in your notes, and a 200 between the workloads, is the gate on leaving this exercise.** If the backup cannot be restored, the recovery is `istioctl uninstall --purge` followed by a reinstall from [the values file](04-the-request-that-does-not-fit.md) and a rollout of both Deployments — about ten minutes, and the reason that file was written once and kept.

**Keep `~/istio-ca-secret.backup.json` until the phase ends.** [The ambient switch](20-a-namespace-with-no-sidecars.md) changes the data plane while leaving this CA in place, and a half-restored trust chain would be indistinguishable from an ambient bug. **The topology stays.**
