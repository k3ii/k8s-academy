<a id="restore-from-snapshot"></a>
# 2.C3 — put the cluster back, and count what you lost

**Claim** — restoring a snapshot rebuilds a cluster in a fixed order that cannot be varied, and it returns the store to **exactly** the revision the snapshot was taken at — so everything written since is gone, silently, with no error anywhere. The procedure is the skill; the arithmetic of what disappeared is the lesson.

**Rests on** — [exercise 27](27-lose-quorum.md), whose deliberately stale `/tmp/before-quorum-loss.db` you kept, and [exercise 24's](24-the-on-disk-trio.md) `new` versus `existing` sentence. This is [drill 2.C3](../../phases/02-etcd.md#chaos), [manual drill 1](../../strands/chaos.md#manual-drills), and [capstone artifact 1](../../phases/02-etcd.md#capstone)'s second half.

**This is not CKA preparation, and [the phase file's claim that it is](../../phases/02-etcd.md#m2-5) is wrong.** *Implement etcd backup and restore* was [removed from the CKA curriculum entirely in v1.32](../../strands/certs.md#cka-changes) — the strand calls it the single biggest trap in the revision, because it is the most-drilled task in every older question bank and is no longer a listed competency. The drill stays here at full length because it is real operational skill and because [the capstone](../../phases/02-etcd.md#capstone) is built on it; it is billed as internals, not as exam prep.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only), three healthy members.

**Setup — make something to lose**

```sh
etcdctl snapshot save /tmp/snap-A.db
etcdctl endpoint status -w json | python3 -c 'import sys,json; print("revision at snapshot:", json.load(sys.stdin)[0]["Status"]["header"]["revision"])'

for i in $(seq 1 300); do etcdctl put /after/k$i "written-after-the-snapshot" > /dev/null; done
etcdctl get --prefix /after/ --keys-only | grep -c after
```

Three hundred keys exist that the snapshot has never heard of. Write that number down; you are going to check it again in twenty minutes.

**Do**

1. Inspect the snapshot before trusting it. A snapshot file is a bbolt database and it can be read without restoring anything:

   ```sh
   etcdutl snapshot status /tmp/snap-A.db -w table
   ~/etcd-dump-db list-bucket /tmp/snap-A.db
   ```

   Note the revision and the hash. **Checking a backup is not the same as having one**, and this command is the difference.

2. Find out which binary owns the restore in your release, rather than assuming:

   ```sh
   etcdutl snapshot restore --help | head -20
   etcdctl snapshot restore --help 2>&1 | head -5
   ```

   The offline operations moved out of `etcdctl` into `etcdutl`; which of the two your release accepts is a fact about the version from [exercise 5](05-three-members-by-hand.md), and [checking it rather than citing it](../../strands/source-archaeology.md#drills) is the phase's standing habit.

3. Stop all three members. All of them, before restoring any of them:

   ```sh
   for n in 160 161 162; do ssh zain@10.10.10.$n 'sudo systemctl stop etcd'; done
   ```

4. Restore **once per member**, each with its own identity, all from the same file, all with the **same new token**:

   ```sh
   scp /tmp/snap-A.db zain@10.10.10.161:~ ; scp /tmp/snap-A.db zain@10.10.10.162:~

   # on .160
   sudo rm -rf /var/lib/etcd/*
   sudo etcdutl snapshot restore ~/snap-A.db \
     --name m1 \
     --initial-cluster m1=http://10.10.10.160:2380,m2=http://10.10.10.161:2380,m3=http://10.10.10.162:2380 \
     --initial-cluster-token academy-restored-1 \
     --initial-advertise-peer-urls http://10.10.10.160:2380 \
     --data-dir /var/lib/etcd
   ```

   Repeat on `.161` and `.162`, changing `--name` and `--initial-advertise-peer-urls` only.

5. Fix the unit files. `--initial-cluster-token` must match what you restored with, on all three:

   ```
     --initial-cluster-token academy-restored-1 \
   ```

   On a kubeadm cluster this step is editing `/etc/kubernetes/manifests/etcd.yaml` instead, which is [the static pod you moved in P1](../01/04-static-pod-blip.md) — same step, different file.

6. Start all three and verify:

   ```sh
   for n in 160 161 162; do ssh zain@10.10.10.$n 'sudo systemctl daemon-reload && sudo systemctl start etcd'; done
   etcdctl member list -w table
   etcdctl endpoint status --cluster -w table
   etcdctl endpoint hashkv --cluster -w table
   ```

7. **Now count.** The moment the drill exists for:

   ```sh
   etcdctl get --prefix /after/ --keys-only | grep -c after
   etcdctl endpoint status -w json | python3 -c 'import sys,json; print("revision now:", json.load(sys.stdin)[0]["Status"]["header"]["revision"])'
   ```

8. Do it once more, wrong on purpose, and note what each mistake produces: restore with the **old** token; restore only one member and start all three; skip step 3 and restore under a running member. Each fails differently and each failure is one somebody has shipped.

**Observe** — three members come back healthy with agreeing hashes, and the revision is the snapshot's, not the one you had before you started.

**Expect** — zero keys under `/after/`. Three hundred writes that returned success to a client are gone, and there is no error, no alarm, no log line naming them. **A restore is a rollback of the entire keyspace to a point in time**, and on a Kubernetes cluster that means every object created since the snapshot — pods, secrets, RBAC bindings — is gone while the workloads created from them may still be running on nodes that have not heard about it.

That gap between the store and the world is what makes etcd restores harder than database restores, and it is the reason step 7 is a counting exercise and not a `kubectl get`.

The `--initial-cluster-token` is the guard that keeps the restored cluster from being confused with the old one: identical member names and URLs would otherwise let a stale member from the previous incarnation rejoin and contribute a log it has no right to. Step 8's first case is that failure, made deliberately.

**Footprint note** — the restore writes a fresh data dir per member from a snapshot the same size as the store. On a small store this is instant; **the time this takes is proportional to the store, and stating it is part of a recovery plan.** Time yours and note the store size next to it.

**Write down** — the ordered procedure as five steps, each with one clause of *why here*, plus the count from step 7 and the three failures from step 8. That procedure is [the checklist's](../../phases/02-etcd.md#checklist) restore item and it must be written so another person could follow it without this file.

**Teardown** — `rm /tmp/snap-A.db /tmp/before-quorum-loss.db` and the copies on the members. Confirm three healthy members with agreeing hashes and a `--initial-cluster-state new` unit on each. **The topology stays** — [the capstone](29-the-capstone-writeup.md) runs the whole sequence once more, in one sitting, and is the last thing the cluster does.
