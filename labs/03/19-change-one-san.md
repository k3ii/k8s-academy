<a id="change-one-san"></a>
# One SAN wrong, recognised from the apiserver's log in two minutes

**Claim** — changing a single Subject Alternative Name on the webhook's serving certificate, while leaving the CA, the `caBundle`, the network path and the process untouched, produces `x509: certificate is valid for ⟨…⟩, not forge.lab` — a *different* string from the one a wrong CA produces — and you can tell the two apart from the log alone, without checking anything else.

**Rests on** — [the working webhook](18-the-webhook-the-apiserver-dials.md) and [the SAN block](17-a-ca-and-a-serving-cert-by-hand.md). This is [the checklist's two-minute item](../../phases/03-api-machinery.md#checklist) and it is only meaningful as a *timed* exercise, so start a clock.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [stage 1](18-the-webhook-the-apiserver-dials.md), with the `go run` webhook still up on `forge`.

**Setup**

Have a colleague-shaped process do the breaking: write both broken certificates *now*, name them opaquely, and have a script pick one at random so the failure you are diagnosing is not one you picked.

```sh
cd ~/webhook-pki
sed 's/forge\.lab/forge.wrong/' san.cnf > san-badname.cnf
openssl x509 -req -in tls.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -days 90 -sha256 -extfile san-badname.cnf -extensions v3 -out tls-A.crt

openssl genrsa -out other-ca.key 2048
openssl req -x509 -new -nodes -key other-ca.key -sha256 -days 90 \
  -subj "/CN=not-the-academy-ca" -out other-ca.crt
openssl x509 -req -in tls.csr -CA other-ca.crt -CAkey other-ca.key -CAcreateserial \
  -days 90 -sha256 -extfile san.cnf -extensions v3 -out tls-B.crt
```

Note that `tls-A.crt` keeps the right issuer and loses the right name; `tls-B.crt` keeps the right name and loses the right issuer. The private key is the same in both, so nothing else changes.

**Do**

1. Pick one without looking, restart the webhook with it, and start the clock:

   ```sh
   C=$(ls tls-[AB].crt | shuf -n1)     # do not echo $C
   pkill -f 'go run .' ; cd ~/k8s-academy/build/03-validating-webhook
   go run . --tls-cert ~/webhook-pki/$C --tls-key ~/webhook-pki/tls.key --addr :8443 &
   ```

2. From the cluster, attempt an admitted write:

   ```sh
   kubectl -n tenant run probe --image=busybox --restart=Never \
     --overrides='{"spec":{"containers":[{"name":"probe","image":"busybox","resources":{"limits":{"memory":"32Mi"}}}]}}'
   ```

3. Diagnose from the apiserver's log **only**. Name which certificate is loaded before you look at it. Stop the clock.

**Observe**

```sh
ssh zain@10.10.10.130 'sudo crictl logs $(sudo crictl ps -q --name kube-apiserver) 2>&1 | tail -30'
kubectl -n tenant run probe2 --image=busybox --restart=Never 2>&1 | tail -3
openssl x509 -in ~/webhook-pki/$C -noout -issuer -ext subjectAltName    # the reveal, after you have answered
```

**Expect** — both failures reach the client as `failed calling webhook "memlimit.academy.local"` wrapped around an `x509` string, and the wrapper is identical. The inner string is not:

- **Wrong SAN** — `x509: certificate is valid for forge.wrong, forge, 10.10.10.125, not forge.lab`. The certificate verified fine; the *name* did not match. The fix is a new certificate.
- **Wrong CA** — `x509: certificate signed by unknown authority`. The chain did not verify at all and the name was never reached. The fix is a new `caBundle`, or a certificate from the CA the bundle names.

Two minutes is generous once the discriminator is fixed in mind as the word `valid for` versus the words `unknown authority`, and that is exactly what the drill is training. What makes it *hard* is that `failurePolicy: Fail` means the cluster is now refusing writes in that namespace, so the pressure to guess is real — which is the honest version of this failure and the reason [the chaos drill](26-3c1-corrupt-a-cabundle.md) exists.

The third string you may hit instead of either: `tls: failed to verify certificate` with no detail, if the apiserver version wraps the error differently. Note it if you see it and record what *did* discriminate.

**Write down** — the two `x509` strings verbatim, the discriminating words, your time, and which certificate you guessed. Add both rows to [the running list of failures that look identical from the client](04-mis-sign-a-client-cert.md) — it now has four entries, at three different layers.

**Teardown** — restore the good certificate and confirm admission works again:

```sh
pkill -f 'go run .' ; rm -f ~/webhook-pki/tls-A.crt ~/webhook-pki/tls-B.crt ~/webhook-pki/other-ca.* ~/webhook-pki/san-badname.cnf
cd ~/k8s-academy/build/03-validating-webhook
go run . --tls-cert ~/webhook-pki/tls.crt --tls-key ~/webhook-pki/tls.key --addr :8443 &
kubectl -n tenant delete pod --all
```

**The topology stays.**
