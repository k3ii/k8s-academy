<a id="mis-sign-a-client-cert"></a>
# A wrong client cert fails at a nameable place

**Claim** — a client certificate signed by the wrong CA is rejected at *authentication* with a distinct message, and a client certificate signed by the right CA but carrying the wrong `O` is accepted at authentication and rejected at *authorization* with a different one. Two failures that look the same to the user, at two different stages.

**Rests on** — [the hop table](01-hand-wire-the-control-plane.md) — specifically the CN/O column, and the `--client-ca-file` flag you [located in source](02-every-flag-located-in-source.md).

**Topology** — **none.** This runs inside the same browser-hosted playground as [the hand-wiring](01-hand-wire-the-control-plane.md), on the cluster you built there — which is the only cluster in this phase where breaking a component credential costs nothing to repair, because you have the CA and the openssl commands in your scrollback already.

**Do**

1. Take the controller-manager's kubeconfig and make **two** broken copies.

2. **Copy A — wrong CA.** Generate a fresh CA and sign a new client cert for `system:kube-controller-manager` with it. Same CN, same O, different issuer. Point a kubeconfig at it.

3. **Copy B — wrong identity.** Sign a client cert with the *cluster's real CA*, but give it `CN=nobody` and no `O`.

4. Use each in turn, and watch the apiserver, not the client:

   ```sh
   kubectl --kubeconfig=/tmp/broken-a.conf get nodes
   kubectl --kubeconfig=/tmp/broken-b.conf get nodes
   ```

**Observe** — the apiserver's own log at `--v=4` or higher, and the response body in each case:

```sh
kubectl --kubeconfig=/tmp/broken-a.conf get nodes -v=8 2>&1 | tail -20
kubectl --kubeconfig=/tmp/broken-b.conf get nodes -v=8 2>&1 | tail -20
```

**Expect** — copy A never reaches an HTTP status you would recognise: the TLS handshake itself fails, and the message names a certificate, not a permission. Copy B gets a clean `403` naming `User "nobody"` and the resource it was refused — the apiserver has decided *who you are* successfully and is telling you that person may do nothing.

That difference is the whole of [module 3.1](../../phases/03-api-machinery.md#m3-1)'s rejection-point lesson, met here on a cluster where you own the CA. When [the same distinction returns on a real cluster](07-rejected-at-authorization-not-admission.md) it will be a token rather than a cert, and the stage will be the same.

The likely surprise: copy B may not get `403` at all but a `401`, if you also managed to break the `O` in a way that makes the certificate fail *verification* rather than merely carry a useless identity. If so, you have accidentally reproduced copy A — check the issuer before concluding anything.

**Write down** — the two error strings verbatim, with which stage produced each, and the flag on the apiserver that decides stage one. This is the first entry in the running list of *failures that look identical from the client and are not*, which [the SAN break](19-change-one-san.md) and [the expired credential](41-3c5-an-expired-component-certificate.md) both add to.

**Teardown** — delete both broken kubeconfigs and their keys; restore the controller-manager's real kubeconfig and confirm it reconciles again (`kubectl -n kube-system get events` should stop accumulating failures). The playground goes when the session does. **No topology is up in the homelab, and none has been all module.**
