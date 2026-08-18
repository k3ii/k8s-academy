<a id="3c5-an-expired-component-certificate"></a>
# 3.C5 — x509 from the inside, and the order recovery has to happen in

**Claim** — an expired client certificate on a control-plane component produces an `x509` error indistinguishable in wording from the two you already produced by other means, and recovery has a **required order**: the certificate, then the kubeconfig that embeds it, then the process — with `kubeadm certs renew` doing the first and not the last.

**Rests on** — [the mis-signed client cert](04-mis-sign-a-client-cert.md) and [the changed SAN](19-change-one-san.md), which produced the other two members of the `x509` family. This closes [the running list](04-mis-sign-a-client-cert.md).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), the last exercise on it.

**Setup — do not move the clock.** [The chaos strand](../../strands/chaos.md#manual-drills) rules this out and gives the reason: on this topology etcd shares the node, and skewing its clock corrupts more than it demonstrates. **Fake the expiry properly**: issue a replacement certificate that is already expired, signed by the real CA, and install it in place of a live one.

Take a full backup of the PKI first, because you are about to overwrite a working credential:

```sh
ssh zain@10.10.10.130 'sudo tar czf /root/pki-backup.tgz /etc/kubernetes/pki /etc/kubernetes/*.conf && ls -l /root/pki-backup.tgz'
```

Read the current expiry set before touching it — this command is the CKA-banked half of the drill and you should be able to type it from memory by the end:

```sh
ssh zain@10.10.10.130 'sudo kubeadm certs check-expiration'
```

**Do**

1. Pick the target. `controller-manager.conf`'s embedded client certificate is the right one: it is a component, not your admin access, and its failure is loud without being terminal. Say why you did **not** pick `apiserver.crt` — the answer involves what would still be reachable afterwards.

2. Mint an already-expired replacement from the real cluster CA, on `.130`:

   ```sh
   sudo openssl req -new -newkey rsa:2048 -nodes -keyout /tmp/cm.key \
     -subj "/CN=system:kube-controller-manager" -out /tmp/cm.csr
   sudo openssl x509 -req -in /tmp/cm.csr \
     -CA /etc/kubernetes/pki/ca.crt -CAkey /etc/kubernetes/pki/ca.key -CAcreateserial \
     -not_before 20240101000000Z -not_after 20240102000000Z -out /tmp/cm.crt
   sudo openssl x509 -in /tmp/cm.crt -noout -dates -subject
   ```

   `-not_before`/`-not_after` need a recent OpenSSL; if yours rejects them, use `faketime` on the signing command only — the signing process, not the node. Either way the certificate must be **validly signed** and **expired**, or you have reproduced [exercise 4](04-mis-sign-a-client-cert.md) instead of this.

3. Install it into `controller-manager.conf` — base64 the cert and key into `client-certificate-data` and `client-key-data` — and restart the component by touching its manifest.

4. Diagnose it as though you had walked in cold. From the apiserver's side first, then the client's:

   ```sh
   ssh zain@10.10.10.130 'sudo crictl logs $(sudo crictl ps -aq --name kube-controller-manager) 2>&1 | tail -30'
   ssh zain@10.10.10.130 'sudo crictl logs $(sudo crictl ps -q --name kube-apiserver) 2>&1 | grep -i x509 | tail'
   kubectl get leases -n kube-system kube-controller-manager -o yaml | grep -E 'holder|renew'
   ```

5. Observe the *cluster* symptom, not just the log. Create a Deployment and see what does and does not happen. Then create a PVC, or delete a namespace, and note which of those stall.

6. Recover in the correct order, and record where each step stops being enough:

   ```sh
   sudo kubeadm certs renew controller-manager.conf
   sudo kubeadm certs check-expiration | grep controller-manager
   ```

   Then check whether the component recovered on its own. It did not. Work out what the remaining step is and do it. Then verify the lease is being renewed again.

**Observe** — the exact `x509` wording on both sides. It matters that the apiserver's message and the component's message describe the same event from two directions.

**Expect** — `x509: certificate has expired or is not yet valid`, with a `current time ... is after ...` clause naming both timestamps. Set that beside the other two:

| Fault | Message | Where it fails |
|---|---|---|
| Wrong CA ([4](04-mis-sign-a-client-cert.md), [26](26-3c1-corrupt-a-cabundle.md)) | `certificate signed by unknown authority` | TLS handshake |
| Wrong SAN ([19](19-change-one-san.md)) | `certificate is valid for X, not Y` | TLS handshake |
| Expired (here) | `certificate has expired or is not yet valid` | TLS handshake |

Three faults, three messages, one layer — and none of them reaches authorization, which is why [exercise 7](07-rejected-at-authorization-not-admission.md)'s `403` is a *different kind of thing* despite looking similar from a client. That table is the phase's answer to "it says x509" and is worth memorising for the exam as much as for the job.

Step 5's cluster symptom is the useful surprise: the apiserver is healthy, `kubectl` works perfectly, and the Deployment creates a `Deployment` object and no `ReplicaSet`. **A dead controller-manager looks like a cluster that accepts your writes and ignores them**, which is far harder to spot than an outage.

Step 6's ordering: `kubeadm certs renew` rewrites the certificate **inside the kubeconfig** and does not restart the process. The component holds its old credential until it restarts. Find out whether the kubelet restarts a static pod when its manifest is unchanged, and what the actual restart lever is.

**Write down** — the three-row table above, the step-5 symptom in one sentence, and the recovery sequence as an ordered list you could execute under exam time pressure.

**Teardown** — verify `kubeadm certs check-expiration` is clean, the controller-manager lease is renewing, and a test Deployment produces a ReplicaSet and Pods. Delete the test objects and `/root/pki-backup.tgz` once you are satisfied.

**The topology goes.** This is the end of module 3.5 and the last exercise on `pair`:

```sh
just tofu labs destroy
```

[Module 3.6](42-k0s-in-one-binary.md) provisions [`k0s-light`](../../strands/lab-topologies.md#k0s-light) fresh, and the contrast it exists to make is weaker if a kubeadm cluster is still running beside it.
