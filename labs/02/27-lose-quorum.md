<a id="lose-quorum"></a>
# 2.C2 — stop two of three and meet a cluster that cannot decide anything

**Claim** — with two of three members stopped, the survivor serves stale serializable reads and **nothing else**: no writes, no linearizable reads, no member changes, no leader. Recovery is not a restart; it is a decision to abandon the old cluster's membership, and `--force-new-cluster` is the flag that makes it.

**Rests on** — [exercise 15](15-partition-one-member.md), which took one member away. This takes two, and the difference is not one of degree: at one loss the cluster is fine and one member is stranded, at two losses there is no cluster. This is [drill 2.C2](../../phases/02-etcd.md#chaos) and [manual drill 3](../../strands/chaos.md#manual-drills), and it is [capstone artifact 1](../../phases/02-etcd.md#capstone).

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only), all three healthy and hashes agreeing after [exercise 26](26-corrupt-a-member.md).

**Setup**

**Take a snapshot first.** You are about to do something with a real chance of ending with a cluster you cannot recover, and [the next exercise](28-restore-from-snapshot.md) is the other half of this one:

```sh
etcdctl put /quorum/before yes
etcdctl snapshot save /tmp/before-quorum-loss.db
scp /tmp/before-quorum-loss.db zain@10.10.10.160:~   # keep a copy off the member you will keep
etcdctl member list -w table                          # you will need these IDs when member list stops working
```

**Do**

1. Stop two members. **Stop the guests, not the process** — [the strand says why](../../strands/chaos.md#cannot-express): a killed process is a lesson about supervision, and this drill is about a machine being gone. On the Proxmox host:

   ```sh
   qm stop <vmid-of-.161>
   qm stop <vmid-of-.162>
   ```

2. From `.160`, try everything, and predict each result first:

   ```sh
   etcdctl --endpoints=http://127.0.0.1:2379 put /quorum/after no
   etcdctl --endpoints=http://127.0.0.1:2379 get /quorum/before
   etcdctl --endpoints=http://127.0.0.1:2379 get /quorum/before --consistency=s
   etcdctl --endpoints=http://127.0.0.1:2379 member list
   etcdctl --endpoints=http://127.0.0.1:2379 member remove <id-of-.161>
   etcdctl --endpoints=http://127.0.0.1:2379 endpoint status -w table
   ```

3. `member remove` is the one to think about. It is the operation that would *fix* the problem — reducing the cluster to one member makes one member a quorum. Say why it is refused, and why a system that permitted it would be unsafe.

4. Read what the survivor says about itself:

   ```sh
   ssh zain@10.10.10.160 'journalctl -u etcd -n 40 --no-pager'
   ```

5. **The recovery.** Stop the survivor, and restart it declaring itself the whole cluster:

   ```sh
   ssh zain@10.10.10.160 'sudo systemctl stop etcd'
   ssh zain@10.10.10.160 'sudo etcdutl snapshot restore --help; sudo etcd --help 2>&1 | grep -i force-new-cluster'
   ```

   Add `--force-new-cluster` to `.160`'s unit, start it, and read what it did:

   ```sh
   ssh zain@10.10.10.160 'sudo systemctl daemon-reload && sudo systemctl start etcd'
   etcdctl --endpoints=http://10.10.10.160:2379 member list -w table
   etcdctl --endpoints=http://10.10.10.160:2379 put /quorum/after yes
   ```

6. **Take the flag back out immediately** and restart. A member that keeps `--force-new-cluster` in its unit will discard the cluster's membership every time it restarts, which is a foot-gun that lies dormant until a reboot months later.

7. Rebuild to three. Start the two stopped guests, and notice that they come back believing in the *old* cluster — they have the old membership on disk and it no longer exists:

   ```sh
   qm start <vmid-of-.161>
   ssh zain@10.10.10.161 'journalctl -u etcd -n 30 --no-pager'
   ```

   Fix them the way [exercise 24](24-the-on-disk-trio.md) established: `member add` on the survivor, wipe the data dir, `--initial-cluster-state existing`, start. Do one at a time and check health between.

**Observe** — step 2's write, linearizable read, `member list` and `member remove` all fail with a timeout or a no-leader error; the serializable read succeeds and returns the value from before the loss.

**Expect** — `--force-new-cluster` rewrites the surviving member's membership so that it alone is the cluster, at the cost of **discarding any entry the survivor had not yet received**. That is the trade and it must be stated out loud: this is not a repair, it is an assertion that whatever the two dead members knew and this one did not is now acceptably lost. On a Kubernetes cluster that is objects created in the last few seconds.

Step 3's answer is the same safety rule as [exercise 15](15-partition-one-member.md), one level up. A membership change is a Raft log entry like any other, so changing membership requires a quorum of the membership you are changing — a cluster cannot vote itself smaller when it cannot vote at all. `--force-new-cluster` is not an exception to that rule; it is an operator stepping outside the protocol and taking responsibility for the consequence.

**Footprint note** — `qm stop` frees 2.0GB for the duration, which is unhelpfully the wrong direction: the phase's whole [3.0GB](../../strands/lab-topologies.md#etcd-only) was never the constraint. What it does buy is honesty — [no chaos tool can express this](../../strands/chaos.md#cannot-express), so the fault is a machine that is off.

**Write down** — the six outcomes from step 2, the answer to step 3, and what `--force-new-cluster` costs. Then the ordered recovery, written so someone else could follow it. That procedure plus [the restore](28-restore-from-snapshot.md) is [capstone artifact 1](../../phases/02-etcd.md#capstone).

**Teardown** — confirm `--force-new-cluster` is out of `.160`'s unit, confirm three healthy members with agreeing `hashkv`, `etcdctl del --prefix /quorum/`. **Keep `/tmp/before-quorum-loss.db`** — [the restore drill](28-restore-from-snapshot.md) wants a snapshot that is deliberately stale. **The topology stays.**
