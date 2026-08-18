<a id="find-the-leader-and-move-it"></a>
# One leader, three logs, and a handover you asked for

**Claim** — you can name the leader from `endpoint status`, hand leadership to a chosen member without any member restarting, and show a follower's log index tracking the leader's rather than lagging arbitrarily.

**Rests on** — [module 2.2's](../../phases/02-etcd.md#m2-2) Figure 2 reading: the three sub-problems, and which single rule makes a committed entry safe forever. Answer that before touching the cluster — the rest of the module is the rule made operational.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only), all three members healthy. If [exercise 10](10-linearizable-versus-serializable.md)'s `netem` is still on `.162`, take it off first; a 300ms peer delay changes every number below.

**Do**

1. Find the leader and read what else that table tells you:

   ```sh
   etcdctl endpoint status --cluster -w table
   ```

   Five columns matter: the member ID, `IS LEADER`, `RAFT TERM`, `RAFT INDEX` and `RAFT APPLIED INDEX`. Say what the difference between the last two is *before* looking it up — one of them is about the log and one is about the state machine, and which is which is the library-versus-server distinction the whole module is about.

2. Watch the indices move together. In one terminal:

   ```sh
   while true; do etcdctl endpoint status --cluster -w table | grep -E 'IS LEADER|http'; echo; sleep 1; done
   ```

   In another, `while true; do etcdctl put /raft/k "$(date +%s%N)" >/dev/null; done`.

3. Hand leadership over deliberately. Take the *member ID* of a follower — hex, from [exercise 5](05-three-members-by-hand.md)'s notes:

   ```sh
   etcdctl move-leader <follower-hex-id>
   ```

   Watch the term and the `IS LEADER` column in the other terminal as it happens.

4. Try the two things that fail, because their errors are informative:

   ```sh
   etcdctl move-leader <the-current-leader's-own-id>
   etcdctl --endpoints=http://10.10.10.161:2379 move-leader <some-id>    # against a follower
   ```

5. Read the write path from the client side. With the write loop running, ask each member how far behind it is:

   ```sh
   for n in 160 161 162; do
     curl -s http://10.10.10.$n:2379/metrics | grep -E '^etcd_server_(has_leader|leader_changes_seen_total|is_leader) '
   done
   ```

**Observe** — during step 2, all three `RAFT INDEX` values stay within a couple of each other under load, and `RAFT APPLIED INDEX` trails `RAFT INDEX` by a small amount on every member including the leader.

**Expect** — `move-leader` completes in well under a second with no restart and no write errors: it is a `MsgTimeoutNow` to the target, not a failure. Step 4's second command is rejected because a transfer must be requested *of* the current leader, which is a fact about where the authority to give something away lives.

The applied-index lag in step 2 is the module's central observation and it is easy to skim past: **an entry is committed before it is applied**, and the gap between those two indices is the window in which etcd has durably promised something it has not yet done. Everything in [module 2.3](../../phases/02-etcd.md#m2-3) about watchers and everything in [module 2.5](../../phases/02-etcd.md#m2-5) about corruption detection lives in that gap.

**Write down** — the three member IDs against their names, and one sentence distinguishing `RAFT INDEX` from `RAFT APPLIED INDEX`. Keep the IDs handy; [the quorum-loss drill](27-lose-quorum.md) needs them when two members are gone and `member list` no longer answers.

**Teardown** — `etcdctl del --prefix /raft/`. **The topology stays.**
