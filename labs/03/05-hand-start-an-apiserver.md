<a id="hand-start-an-apiserver"></a>
# An apiserver you built, started from flags, with nothing around it

**Artifact** — a single-member etcd and a `kube-apiserver` **you compiled**, both running on [`forge`](../../strands/lab-topologies.md#build-guest), with `kubectl` talking to them. No scheduler, no controller-manager, no kubelet, no nodes. This is the instrument for [module 3.1](../../phases/03-api-machinery.md#m3-1) and [module 3.2](../../phases/03-api-machinery.md#m3-2): every exercise up to [the CA and serving cert](17-a-ca-and-a-serving-cert-by-hand.md) runs against it.

**Rests on** — [the flags you located in source](02-every-flag-located-in-source.md). You are about to pass those exact flags to a binary whose source you have open, which is the arrangement [module 3.0's argument](../../phases/03-api-machinery.md#m3-0) exists to produce.

**Topology** — **none.** `forge` only. Nothing is provisioned during modules 3.0, 3.1 or 3.2, and the phase's first cluster is [the one that dials your webhook](18-the-webhook-the-apiserver-dials.md).

**Setup**

etcd first, single member, on the loopback — it is a store to be written to here, not a subject:

```sh
V=$(curl -Ls https://api.github.com/repos/etcd-io/etcd/releases/latest | grep -m1 tag_name | cut -d'"' -f4)
cd ~ && curl -LO https://github.com/etcd-io/etcd/releases/download/$V/etcd-$V-linux-amd64.tar.gz
tar xzf etcd-$V-linux-amd64.tar.gz
sudo install -m0755 etcd-$V-linux-amd64/etcd etcd-$V-linux-amd64/etcdctl /usr/local/bin/
etcd --data-dir /tmp/apiserver-etcd --listen-client-urls http://127.0.0.1:2379 \
     --advertise-client-urls http://127.0.0.1:2379 >/tmp/etcd.log 2>&1 &
```

And a `kubectl` that is not the one you are about to build, so a broken build cannot also break your client:

```sh
curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -m0755 kubectl /usr/local/bin/
```

**Do**

1. Build the apiserver from [your clone](02-every-flag-located-in-source.md), with the optimiser and inlining off so a debugger can follow it later:

   ```sh
   cd ~/src/kubernetes
   GOGC=50 go build -gcflags=all="-N -l" -o ~/kube-apiserver ./cmd/kube-apiserver
   ```

   Read the footprint note below **before** you run this. It is the largest single memory event in the phase.

2. Make the two credentials the apiserver needs to exist at all — a keypair for signing ServiceAccount tokens, and a static token file that stands in for the whole authentication story:

   ```sh
   mkdir -p ~/apiserver && cd ~/apiserver
   openssl genrsa -out sa.key 2048
   openssl rsa -in sa.key -pubout -out sa.pub
   cat > tokens.csv <<'CSV'
   s3cr3t-admin,admin,1001,"system:masters"
   s3cr3t-nobody,nobody,1002
   CSV
   ```

   **`--token-auth-file` is a development authenticator and no real cluster uses it** — it is here because it gives you two identities with one line each, one of which is deliberately bound to nothing. [The next-but-one exercise](07-rejected-at-authorization-not-admission.md) is what the second row is for.

3. Start it, with the smallest flag set that serves:

   ```sh
   ~/kube-apiserver \
     --etcd-servers=http://127.0.0.1:2379 \
     --service-account-key-file=$HOME/apiserver/sa.pub \
     --service-account-signing-key-file=$HOME/apiserver/sa.key \
     --service-account-issuer=https://kubernetes.default.svc.cluster.local \
     --token-auth-file=$HOME/apiserver/tokens.csv \
     --authorization-mode=RBAC \
     --cert-dir=$HOME/apiserver/certs \
     --bind-address=127.0.0.1 \
     --secure-port=6443 \
     --v=4 >/tmp/apiserver.log 2>&1 &
   ```

   No `--tls-cert-file`: the apiserver generates a self-signed serving cert into `--cert-dir` when you do not give it one. Note that it did, and where.

4. Point `kubectl` at it twice — once as each identity:

   ```sh
   kubectl config set-cluster forge --server=https://127.0.0.1:6443 --insecure-skip-tls-verify=true
   kubectl config set-credentials admin  --token=s3cr3t-admin
   kubectl config set-credentials nobody --token=s3cr3t-nobody
   kubectl config set-context admin  --cluster=forge --user=admin
   kubectl config set-context nobody --cluster=forge --user=nobody
   kubectl config use-context admin
   ```

**Observe**

```sh
kubectl get --raw='/healthz?verbose'
kubectl api-resources | head -20
kubectl get namespaces
kubectl create namespace probe
kubectl get nodes
etcdctl --endpoints=http://127.0.0.1:2379 get --prefix --keys-only /registry | head
```

**Expect** — `kubectl get nodes` returns `No resources found`, not an error: the resource exists, the registry serving it exists, and nothing has ever registered. That is the correct mental separation — **an apiserver is a store with a schema and a policy engine in front of it, and it does not need a cluster to be one of those things.**

`kubectl get namespaces` shows `default` and `kube-system` and possibly `kube-public`/`kube-node-lease` — created by the apiserver's own bootstrap, not by any controller. `kubectl create namespace probe` succeeds and *stays* `Active` forever, because nothing is reconciling it. Watch what happens to `kubectl delete namespace probe`: it hangs in `Terminating`, and the reason is a finaliser with no controller behind it. Do not fix this; it is [P4](../../phases/04-controllers.md)'s subject and the cleanest possible preview of it.

The likely first failure is the ServiceAccount issuer: omit `--service-account-signing-key-file` and the binary refuses to start with a validation error rather than starting and failing later — which is the good kind of flag, and worth noting beside the one you [could not locate a consumer for](02-every-flag-located-in-source.md).

**Write down** — the flag set that was actually sufficient, next to your [three-column inventory](03-local-up-cluster-as-inventory.md)'s "smallest set" answer. If they differ, one of them is wrong and the running binary is the arbiter.

**Footprint note — this build does not fit `forge` at its default size, and that is a stated deviation.** [The build strand measured](../../strands/build-mechanics.md#measurements) a `cmd/kube-scheduler` link at **1535 MiB with DWARF kept**, on a guest sized 1536MB; `cmd/kube-apiserver` is the larger binary and `-gcflags=all="-N -l"` makes it larger still. The smallest change is the one [the strand already sanctions for P5](../../strands/build-mechanics.md#forge) — a `qm set` and a reboot — applied here as well:

```sh
ssh hopper
qm set 125 --memory 2560 && qm reboot 125
```

**Leave it at 2560MB for the whole of P3.** Resizing back before [`pair`](../../strands/lab-topologies.md#pair) arrives buys nothing: `pair` at 5.0GB plus `forge` at 2560MB is 7.5GB against [the 9.5GB ceiling](../../strands/lab-topologies.md#ceiling), a 2.0GB margin — wider than [`ha`](../../strands/lab-topologies.md#ha) ever gets. During this module and the next, nothing else is running at all.

Disk is the second half of the note: a blobless `k/k` clone plus a cold `GOCACHE` for it is several GB on a 25G guest that also holds the Go module cache, the registry and P2's clones. Check `du -sh ~/src/* $(go env GOCACHE)` after the first build and record the number; if the guest gets tight, `docker system prune` before `go clean -cache`, because the module cache is the expensive thing to lose.

**Teardown** — **nothing here is torn down yet.** etcd and the apiserver stay running for the next eleven exercises; if you stop them, restart with the same `--data-dir` and the same flags and everything is where you left it. [The CA exercise](17-a-ca-and-a-serving-cert-by-hand.md) is where both processes are killed and `/tmp/apiserver-etcd` is deleted. **No topology is up.**
