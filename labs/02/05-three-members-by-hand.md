<a id="three-members-by-hand"></a>
# Three members, wired together by hand

**Artifact** — a healthy three-member etcd cluster on [`etcd-only`](../../strands/lab-topologies.md#etcd-only), started from unit files you wrote, with `etcdctl endpoint status` showing one leader and two followers. This cluster runs every remaining exercise in the phase.

**Rests on** — nothing read yet. Wiring the cluster *before* [module 2.1](../../phases/02-etcd.md#m2-1)'s reading is deliberate: `--initial-cluster`, `--initial-cluster-token` and `--initial-cluster-state` are the three flags [the restore drill](28-restore-from-snapshot.md) turns on, and meeting them first as "the flags that made it start" is what makes the restore procedure's ordering legible three weeks from now.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only), **no Kubernetes anywhere in this phase**. The provisioning commands are [in the strand](../../strands/lab-topologies.md#provision) and are not repeated here; `ssh hopper` is mandatory and `just gate` is not optional. Note also [what does not exist yet](../../strands/lab-topologies.md#contract) — that note applies to every exercise in this directory and is stated there once.

What `just play` gives you is a configured Debian guest and nothing else: **there is no etcd on it.** Installing and wiring three of them is this exercise.

**Setup**

1. On [`forge`](../../strands/lab-topologies.md#build-guest), pick the release you are reading. In the clone from [exercise 1](01-two-blobless-clones.md):

   ```sh
   cd ~/src/etcd && git tag --sort=-v:refname | grep -E '^v3\.[0-9]+\.[0-9]+$' | head -1
   ```

   Call it `$V`. Fetch that release once, on `forge`, rather than three times:

   ```sh
   cd ~ && curl -LO https://github.com/etcd-io/etcd/releases/download/$V/etcd-$V-linux-amd64.tar.gz
   tar xzf etcd-$V-linux-amd64.tar.gz
   for n in 160 161 162; do
     scp etcd-$V-linux-amd64/etcd etcd-$V-linux-amd64/etcdctl etcd-$V-linux-amd64/etcdutl zain@10.10.10.$n:
   done
   ```

2. Build `etcd-dump-db` from the clone, because it ships in the source tree and not in the release tarball. [Exercise 7](07-decode-a-bbolt-key.md) needs it:

   ```sh
   cd ~/src/etcd/tools/etcd-dump-db && go build -o ~/etcd-dump-db .
   scp ~/etcd-dump-db zain@10.10.10.160:
   ```

**Do**

1. On each member, install the binaries and make a data dir:

   ```sh
   sudo install -m 0755 etcd etcdctl etcdutl /usr/local/bin/
   sudo mkdir -p /var/lib/etcd && sudo chown "$USER" /var/lib/etcd
   ```

2. On `.160`, write `/etc/systemd/system/etcd.service`. The name and the two `.160`s are the only per-member differences:

   ```ini
   [Unit]
   Description=etcd
   [Service]
   ExecStart=/usr/local/bin/etcd \
     --name m1 \
     --data-dir /var/lib/etcd \
     --listen-peer-urls http://10.10.10.160:2380 \
     --listen-client-urls http://10.10.10.160:2379,http://127.0.0.1:2379 \
     --initial-advertise-peer-urls http://10.10.10.160:2380 \
     --advertise-client-urls http://10.10.10.160:2379 \
     --initial-cluster m1=http://10.10.10.160:2380,m2=http://10.10.10.161:2380,m3=http://10.10.10.162:2380 \
     --initial-cluster-token academy-1 \
     --initial-cluster-state new \
     --logger zap
   Restart=on-failure
   [Install]
   WantedBy=multi-user.target
   ```

   Repeat on `.161` (`m2`) and `.162` (`m3`), changing `--name` and the three URLs that carry an address. `--initial-cluster` is **identical on all three** — that is the list every member bootstraps from, and disagreement between copies of it is the single most common way a hand-built cluster fails to form.

3. Start all three within a few seconds of each other:

   ```sh
   sudo systemctl daemon-reload && sudo systemctl enable --now etcd
   journalctl -u etcd -f      # watch on one of them while the others come up
   ```

4. Put an endpoint list in your shell on `.160`, since every later exercise uses it:

   ```sh
   export ETCDCTL_ENDPOINTS=http://10.10.10.160:2379,http://10.10.10.161:2379,http://10.10.10.162:2379
   echo 'export ETCDCTL_ENDPOINTS=...' >> ~/.bashrc     # with the real list
   ```

**Observe**

```sh
etcdctl member list -w table
etcdctl endpoint status --cluster -w table
etcdctl endpoint health --cluster
etcdctl put /hello world && etcdctl get /hello
```

**Expect** — `member list` shows three started members with peer and client URLs matching what you wrote. `endpoint status` shows exactly one row with `IS LEADER` true; the `RAFT TERM` is the same on all three and the `RAFT INDEX` is the same or within one. A member that started before its peers logs `health check for peer ... could not connect` for as long as it takes the others to arrive, then elects — those errors during bootstrap are the cluster working, not failing.

If a member refuses to start with `error validating peerURLs ... member count is unequal`, two copies of `--initial-cluster` disagree. If it starts but never joins, check that each member's `--initial-advertise-peer-urls` matches its own entry in that list character for character — etcd matches on the string, not on the address.

**Write down** — the member IDs from `member list`. They are hex, they are stable for the life of the member, and [the quorum-loss drill](27-lose-quorum.md) and [the restore](28-restore-from-snapshot.md) both reason about them rather than about hostnames.

**Footprint note — this cluster runs without TLS, and that is a stated deviation.** A real Kubernetes etcd is client- and peer-authenticated, and every `etcdctl` in production carries `--cacert --cert --key`. Adding that here would put certificate plumbing in front of every command in the phase for no gain against any of [the objectives](../../phases/02-etcd.md#objectives) — none of which are about transport security, which is [P10](../../phases/10-security.md)'s subject. The one place it costs something is realism of the command lines, so note it once: **everything in `labs/02/` is one `--cacert/--cert/--key` triple short of the command you would run against a kubeadm cluster's etcd**, and [P1's static-pod manifest](../01/03-static-pod-flags-vs-local-up.md) is where you already saw those flags in place.

3.0GB of the [9.5GB ceiling](../../strands/lab-topologies.md#ceiling), and nothing else is running: no Kubernetes, no CNI, no MetalLB. This is the cheapest month in the curriculum and the deepest, which is why it gets four to five weeks.

**Teardown** — `etcdctl del /hello`. **The topology stays** — it stays for the whole phase, through to [the capstone](29-the-capstone-writeup.md). Every exercise from here deletes its own keys and leaves the cluster up.
