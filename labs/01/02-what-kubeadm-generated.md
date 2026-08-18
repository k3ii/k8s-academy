<a id="what-kubeadm-generated"></a>
# The map of what kubeadm left on disk

**Artifact** — a one-page map of every file `kubeadm init` generated, grouped by what it is for. **This is [a gate condition](../../phases/01-operate-shallow.md#gate) and the input [P3](../../phases/03-api-machinery.md) reads as source** — P3 greps these exact files.

**Rests on** — [module 1.1's `staging.md` question](../../phases/01-operate-shallow.md#m1-1). Answer it before this exercise, not after: you are about to look at a directory of certificates and kubeconfigs, and the answer to why `k8s.io/client-go` exists as a published repo is what makes `/etc/kubernetes/*.conf` look like *client configuration for four different clients* rather than four similar files.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), from [exercise 1](01-provision-and-kubeadm-init.md), still up.

**Do**

1. Inventory the three directories, on the control-plane node:

   ```sh
   sudo ls -la /etc/kubernetes/manifests/   # static pods
   sudo ls -la /etc/kubernetes/pki/         # the CA and every cert it signed
   sudo ls -la /etc/kubernetes/*.conf       # kubeconfigs
   sudo ls -la /var/lib/kubelet/            # config.yaml, pki/, and the kubelet's own kubeconfig
   ```

2. For **each certificate**, print who signed it, who it identifies and what it is allowed to be used for:

   ```sh
   for c in /etc/kubernetes/pki/*.crt /etc/kubernetes/pki/etcd/*.crt; do
     echo "== $c"
     sudo openssl x509 -in "$c" -noout -subject -issuer -ext subjectAltName,extendedKeyUsage
   done
   ```

   Two of them are CAs, not leaves, and one leaf is signed by neither of the obvious CAs. Find all three and say why.

3. For each of the four kubeconfigs, name the client it is for and extract the identity it presents:

   ```sh
   sudo grep -o 'client-certificate-data: .*' /etc/kubernetes/scheduler.conf \
     | cut -d' ' -f2 | base64 -d | openssl x509 -noout -subject
   ```

   The `O=` field is not decoration — it is the group RBAC binds against, and `admin.conf` says something about `system:masters` that is worth reading twice.

4. Run the same inventory **on the worker**. It has `/var/lib/kubelet` and one kubeconfig and nothing else. Say what that asymmetry means about where cluster state lives.

**Observe** — `sudo kubeadm certs check-expiration` prints the whole PKI as a table with expiry dates and the CA each cert descends from. Read it *after* doing step 2 by hand; it is the answer key.

**Expect** — three CAs, not one (`ca`, `etcd/ca`, `front-proxy-ca`), and once you see the third, the `--requestheader-*` flags in [the next exercise](03-static-pod-flags-vs-local-up.md) stop being mysterious. Every leaf expires in one year and the CAs in ten. The kubelet's client certificate is *not* in `/etc/kubernetes/pki` at all — it is under `/var/lib/kubelet/pki`, rotated by a different mechanism, and finding that is the point of step 1's fourth line.

**Write down** — the one-page map: every file, one line each, saying **what writes it, what reads it, and what breaks if it is deleted**. Write it now, while the cluster is up. It is the artifact that outlives the phase — [this cluster does not](24-the-incident-note.md), and P3 consumes the map rather than the guest.

**Teardown** — nothing was created. **The topology stays.**
