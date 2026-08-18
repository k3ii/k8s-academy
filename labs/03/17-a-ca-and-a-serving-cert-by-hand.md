<a id="a-ca-and-a-serving-cert-by-hand"></a>
# A CA, a serving cert with the right SANs, and a `caBundle`

**Artifact** — on [`forge`](../../strands/lab-topologies.md#build-guest): a CA key and certificate, a serving certificate signed by it whose SANs cover every name the apiserver might dial `forge` by, and the base64 blob that goes in a webhook's `caBundle`. Every webhook in this phase is served with these, and [breaking one SAN](19-change-one-san.md) is the next exercise.

**Rests on** — [the two broken kubeconfigs](04-mis-sign-a-client-cert.md), which established that *wrong issuer* and *wrong identity* fail differently. This is the same PKI from the server side, and [`openssl` first is the strand's rule](../../strands/build-mechanics.md#webhook-tls), with automation deliberately second.

**Topology** — **none** yet. This runs on `forge` alone; [the next exercise](18-the-webhook-the-apiserver-dials.md) is where the phase's first cluster is provisioned.

**Setup**

**Stop the hand-started control plane first.** Modules 3.1 and 3.2 are finished with it, and leaving an apiserver bound to `:6443` on `forge` will confuse you later:

```sh
pkill -f 'kube-apiserver --etcd-servers'
pkill -f '^etcd --data-dir /tmp/apiserver-etcd'
rm -rf /tmp/apiserver-etcd /tmp/audit.log
kubectl config delete-context admin; kubectl config delete-context nobody
kubectl config delete-context kubeletA; kubectl config delete-cluster forge
```

Keep `~/apiserver/` — the ServiceAccount keypair is disposable, but the directory is where the webhook PKI is about to live too.

**Do**

1. A CA, valid for the length of the phase and not a decade:

   ```sh
   mkdir -p ~/webhook-pki && cd ~/webhook-pki
   openssl genrsa -out ca.key 2048
   openssl req -x509 -new -nodes -key ca.key -sha256 -days 90 \
     -subj "/CN=academy-webhook-ca" -out ca.crt
   ```

2. A serving key and a CSR, with **the SANs in the config, not on the command line** — the extension has to survive signing, and `-addext` on the CSR does not travel unless you tell the signer to copy it:

   ```sh
   openssl genrsa -out tls.key 2048
   cat > san.cnf <<'CNF'
   [req]
   distinguished_name = dn
   [dn]
   [v3]
   subjectAltName = @alt
   basicConstraints = CA:FALSE
   keyUsage = digitalSignature, keyEncipherment
   extendedKeyUsage = serverAuth
   [alt]
   DNS.1 = forge.lab
   DNS.2 = forge
   IP.1  = 10.10.10.125
   CNF
   openssl req -new -key tls.key -subj "/CN=forge.lab" -out tls.csr
   openssl x509 -req -in tls.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
     -days 90 -sha256 -extfile san.cnf -extensions v3 -out tls.crt
   ```

3. Produce the `caBundle` value. It is the **CA** certificate, base64 of the PEM, on one line — not the serving cert, and not a fingerprint:

   ```sh
   base64 -w0 ca.crt > ca.b64
   wc -c ca.b64
   ```

**Observe**

```sh
openssl x509 -in tls.crt -noout -text | grep -A2 'Subject Alternative Name'
openssl x509 -in tls.crt -noout -issuer -subject -dates
openssl verify -CAfile ca.crt tls.crt
openssl s_client -connect forge.lab:8443 -CAfile ca.crt </dev/null 2>&1 | head -5   # nothing is listening yet
```

**Expect** — `openssl verify` prints `tls.crt: OK`, and the SAN block lists all three entries. The most common failure is a certificate with **no** SAN extension at all, which `openssl verify` still calls `OK` — verification checks the chain, not the name. Nothing in this exercise catches a missing SAN; [the next-but-one exercise](19-change-one-san.md) is the thing that catches it, and by then a cluster is depending on it.

Note that `CN=forge.lab` is doing nothing useful. Go's TLS stack has ignored the Common Name for hostname verification for years, so a certificate with a correct CN and no SAN fails against every Go client, including the apiserver. Write that down now rather than rediscovering it under a webhook.

**Write down** — the three SANs and why each is there, the sentence about CN being decorative, and the byte length of `ca.b64`. That length is a cheap tripwire: [when a `caBundle` is corrupted on purpose](26-3c1-corrupt-a-cabundle.md), a length that still matches is what tells you the corruption was a flipped byte rather than a truncation.

**Footprint note** — zero. `forge` stays at 2560MB from [the apiserver build](05-hand-start-an-apiserver.md); the next exercise brings up [`pair`](../../strands/lab-topologies.md#pair) alongside it for a total of 7.5GB against [the 9.5GB ceiling](../../strands/lab-topologies.md#ceiling).

**Teardown** — the hand-started apiserver and its etcd are gone, deleted in Setup above; confirm with `ss -ltnp | grep -E '6443|2379'` returning nothing. **The PKI stays** — `~/webhook-pki/` is used by four later exercises. **No topology is up yet.**
