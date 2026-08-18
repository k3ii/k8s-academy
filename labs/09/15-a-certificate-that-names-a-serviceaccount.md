<a id="a-certificate-that-names-a-serviceaccount"></a>
# Decode the sidecar's certificate: no hostname, no IP, a URI that names a ServiceAccount — and the token it was traded for

**Claim** — the workload certificate has **no DNS name and no IP in its SAN**; it carries a single URI, `spiffe://cluster.local/ns/mesh/sa/sleep`, whose three path segments name a trust domain, a Namespace and a ServiceAccount. It was issued in exchange for a **projected ServiceAccount token with a non-default audience**, which is the object that ties the certificate to a pod the API server actually admitted.

**Rests on** — [the injected pod](05-a-pod-the-webhook-rewrote.md) for the volumes involved, and [9.C1](08-9c1-a-port-outside-the-mesh.md), where this identity was already visible as a header before you had read the certificate it came from.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do — pull the certificate and decode it:**

```sh
istioctl -n mesh proxy-config secret deploy/sleep
istioctl -n mesh proxy-config secret deploy/sleep -o json \
  | jq -r '.dynamicActiveSecrets[] | select(.name=="default") | .secret.tlsCertificate.certificateChain.inlineBytes' \
  | base64 -d > ~/sleep-leaf.pem
openssl x509 -in ~/sleep-leaf.pem -noout -text | sed -n '/Subject:/p;/Issuer:/p;/Not Before/p;/Not After/p;/Subject Alternative Name/,+2p'
openssl x509 -in ~/sleep-leaf.pem -noout -dates -issuer -subject
```

**Do — find the object each segment names**, so that the identity is checked against the API rather than parsed and admired:

```sh
kubectl -n mesh get pod -l app=sleep -o jsonpath='{.items[0].spec.serviceAccountName}'; echo
kubectl -n mesh get sa
kubectl -n mesh get pod -l app=sleep -o json | jq '.spec.volumes[] | select(.name=="istio-token")'
istioctl -n mesh proxy-config secret deploy/sleep -o json \
  | jq -r '.dynamicActiveSecrets[] | select(.name=="ROOTCA") | .secret.validationContext.trustedCa.inlineBytes' \
  | base64 -d | openssl x509 -noout -subject -issuer -dates -fingerprint
```

**Do — see the same identity arrive at the other end**, as the header [the bypass drill](08-9c1-a-port-outside-the-mesh.md) removed:

```sh
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s http://httpbin:8000/get | jq -r '.headers["X-Forwarded-Client-Cert"]'
```

**Expect** — a certificate whose **Subject is empty** and whose SAN holds exactly one entry, a URI. Expect no CN, no DNS name, no IP: this identity does not travel with the pod's address, which is the whole point — the pod IP changes on every restart, the ServiceAccount does not. Expect the segments to map to `cluster.local` (the trust domain, a mesh-wide setting), `ns/mesh` (a Namespace object you created) and `sa/sleep` (a ServiceAccount you can `kubectl get`), and expect `spec.serviceAccountName` on the pod to be that same name.

Expect a **short validity window** — measure it from `Not Before` and `Not After` rather than quoting a default — and expect the issuer to be the root you dumped as `ROOTCA`. Two facts follow, and both are worth writing down: the agent must renew this certificate long before it expires, so **there is a rotation loop running inside every pod in the mesh**; and [an `istiod` outage](14-9c3-istiod-killed-and-the-planes-come-apart.md) has a deadline set by this number, which is the outage-budget line that exercise owes.

Expect the `istio-token` volume to be a **projected** token with an explicit `audience` that is not the API server's default, and a bounded `expirationSeconds`. That audience is the mechanism: the agent presents this token to `istiod`'s CA, `istiod` validates it with a `TokenReview` against the API server, and only then signs the CSR. **The certificate's trustworthiness is inherited from the API server's opinion of the pod**, not from anything the pod said about itself — which is why a stolen token that is audience-bound and short-lived is a much smaller problem than a stolen certificate.

Expect `X-Forwarded-Client-Cert` to contain the same `URI=spiffe://...` string, plus a hash of the peer certificate. That header is how an application reads its caller's identity without doing any TLS work itself, and it is the input to every authorization policy [P10](../../phases/10-security.md) will write.

**Write down** — in `journal/p9-identity.md`: the decoded SAN, a three-row table mapping each path segment to the Kubernetes object it names, the certificate lifetime in hours, the root's fingerprint, and the projected token's audience and expiry. Keep the root fingerprint especially — [the drill that replaces the root](18-9c2-a-root-that-no-longer-signs.md) is the one place in this phase where that string is the evidence.

**Teardown** — nothing created in the cluster. Keep `~/sleep-leaf.pem`; the [STRICT exercise](16-strict-and-the-plaintext-refused.md) and the root drill both compare against it. **The topology stays.**
