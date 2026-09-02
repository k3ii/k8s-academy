<a id="what-kubeadm-generated"></a>
# The map of what kubeadm left on disk

**Artifact** — a one-page map of every file that `kubeadm init` generated. Group the files by what each one is for. **This map is [a gate condition](../../phases/01-operate-shallow.md#gate). It is also the input that [P3](../../phases/03-api-machinery.md) reads as source** — P3 greps these exact files.

**Rests on** — [module 1.1's `staging.md` question](../../phases/01-operate-shallow.md#m1-1). Answer that question before this exercise, and not after. Here is why. You are about to look at a directory of certificates and kubeconfigs. The answer explains why `k8s.io/client-go` exists as a published repo. With that answer, the files in `/etc/kubernetes/*.conf` look like *client configuration for four different clients*. Without it, they look like four similar files.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), from [exercise 1](01-provision-and-kubeadm-init.md), still up.

**Do**

1. Inventory the three `/etc/kubernetes` directories on the control-plane node. Then add one more directory, `/var/lib/kubelet`:

   ```sh
   sudo ls -la /etc/kubernetes/manifests/   # static pods
   sudo ls -la /etc/kubernetes/pki/         # the CA and every cert it signed
   sudo ls -la /etc/kubernetes/*.conf       # kubeconfigs
   sudo ls -la /var/lib/kubelet/            # config.yaml, pki/, and the kubelet's own kubeconfig
   ```

2. For **each certificate**, print three things: who signed it, who it identifies, and what it is allowed to be used for:

   ```sh
   for c in /etc/kubernetes/pki/*.crt /etc/kubernetes/pki/etcd/*.crt; do
     echo "== $c"
     sudo openssl x509 -in "$c" -noout -subject -issuer -ext subjectAltName,extendedKeyUsage
   done
   ```

   Two of these certificates are CAs, and not leaves. One leaf is signed by neither of the two obvious CAs. Find all three, and say why each one is as it is.

3. For each of the four kubeconfigs, name the client that it is for. Then extract the identity that it presents:

   ```sh
   sudo grep -o 'client-certificate-data: .*' /etc/kubernetes/scheduler.conf \
     | cut -d' ' -f2 | base64 -d | openssl x509 -noout -subject
   ```

   The `O=` field is not decoration. It is the group that RBAC binds against. `admin.conf` says something about `system:masters`, and that line is worth reading twice.

4. Run the same inventory **on the worker**. The worker has `/var/lib/kubelet` and one kubeconfig, and nothing else. Say what that asymmetry means about where cluster state lives.

**Observe** — `sudo kubeadm certs check-expiration` prints the whole PKI as a table. The table gives the expiry date of each certificate and the CA that each certificate descends from. Read it *after* you do step 2 by hand, because it is the answer key.

**Expect** — three CAs, and not one: `ca`, `etcd/ca` and `front-proxy-ca`. After you see the third CA, the `--requestheader-*` flags in [the next exercise](03-static-pod-flags-vs-local-up.md) stop being mysterious. Every leaf expires in one year, and the CAs expire in ten years. Note also where the kubelet's client certificate is not: it is *not* in `/etc/kubernetes/pki` at all. It is under `/var/lib/kubelet/pki`, and a different mechanism rotates it. Finding that certificate is the point of the fourth line in step 1.

**Write down** — the one-page map. Give every file one line. Each line says three things: **what writes the file, what reads it, and what breaks if you delete it**. Write the map now, while the cluster is up. The map is the artifact that outlives the phase. [This cluster does not outlive it](24-the-incident-note.md), and P3 consumes the map rather than the guest.

**Teardown** — nothing was created. **The topology stays.**
