<a id="partition-one-member"></a>
# 2.C5 — cut one member off the peer port

**Claim** — a member isolated from its peers is unavailable for writes *and* for linearizable reads while the remaining majority carries on serving both, and the isolated member reports this as a leaderless cluster rather than as a network error. This is Figure 2's safety rule made operational, and it is the drill [module 2.2](../../phases/02-etcd.md#m2-2) points at.

**Rests on** — [exercise 12](12-kill-the-leader-read-the-term.md). The difference is that nothing has died: the isolated member is healthy, its disk is fine, its client port answers. It is simply outvoted, and it is the *only* one that thinks anything is wrong.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only), three healthy members. Ensure the leader is **not** `.162` before you start — `etcdctl move-leader` it away if it is, so that the first run isolates a follower and the variables stay separated.

**Setup**

Watch from the majority side, on `.160`:

```sh
while true; do etcdctl --endpoints=http://10.10.10.160:2379,http://10.10.10.161:2379 \
  endpoint status -w table; sleep 1; done
```

**Do**

1. On `.162`, drop peer traffic in both directions and leave the client port alone:

   ```sh
   ssh zain@10.10.10.162
   sudo iptables -A INPUT  -p tcp --dport 2380 -j DROP
   sudo iptables -A OUTPUT -p tcp --dport 2380 -j DROP
   ```

   `DROP`, not `REJECT`: a rejection is a fast, explicit failure and it produces a different and much less interesting set of log lines than silence does. [P0 made this distinction](../00/12-cut-a-link-then-slow-it.md); this is where it earns its keep.

2. From `.162`, still over the untouched client port, try each of the three:

   ```sh
   etcdctl --endpoints=http://127.0.0.1:2379 put /part/k v
   etcdctl --endpoints=http://127.0.0.1:2379 get /part/k
   etcdctl --endpoints=http://127.0.0.1:2379 get /part/k --consistency=s
   ```

3. From `.160`, confirm the majority is entirely unbothered:

   ```sh
   etcdctl --endpoints=http://10.10.10.160:2379 put /part/majority v
   etcdctl --endpoints=http://10.10.10.160:2379 get /part/majority
   ```

4. Read what the isolated member says about itself:

   ```sh
   ssh zain@10.10.10.162 'journalctl -u etcd -n 40 --no-pager'
   ssh zain@10.10.10.162 'curl -s http://127.0.0.1:2379/metrics | grep -E "^etcd_server_(has_leader|leader_changes_seen_total) "'
   ```

5. **Check the term on both sides.** Note the isolated member's term now, and the majority's. Then answer: did the isolated member's term climb while it was cut off? If it did, say what happens to the cluster when it rejoins carrying a higher term. If it did **not**, find the mechanism that stopped it — search the raft clone for `PreVote` and read what it does — and say which problem that mechanism exists to solve.

6. Heal it, and time the recovery:

   ```sh
   ssh zain@10.10.10.162 'sudo iptables -D INPUT -p tcp --dport 2380 -j DROP; sudo iptables -D OUTPUT -p tcp --dport 2380 -j DROP'
   etcdctl endpoint status --cluster -w table
   ```

7. Now run it again with one variable changed: isolate the member that **is** the leader. Predict first whether the majority elects a new one, how long it takes, and what the old leader does with the writes it accepted in the meantime.

**Observe** — step 2's `put` and linearizable `get` both fail after a timeout; the serializable `get` succeeds and returns data that gets staler every second. Step 3 succeeds instantly.

**Expect** — `etcdserver: request timed out` or a `no leader` error from the isolated member. The important detail is what it is **not**: no connection refused, no DNS failure, no TLS error. The client's socket to `.162` is fine; the member is answering; it is answering *"I cannot safely serve this"*. Anyone debugging from client errors alone will look at the network between the client and etcd, which is the one segment that is working.

Step 2's third command is the sharpest part of the drill: **a serializable read from a partitioned member returns confidently wrong data**, with no error, indefinitely. That is the operational cost of the mode [exercise 10](10-linearizable-versus-serializable.md) had you measure, and it is why the apiserver's default is the expensive one.

Step 7 should elect within roughly the election timeout, and the deposed leader — which has no way to find out it has been deposed until it can talk to someone — should serve stale serializable reads until healed and then step down on seeing the higher term.

**Footprint note** — no cost. Two `iptables` rules and a `-D` for each. It is the cheapest drill in the phase and it is doing more work than most of them.

**Write down** — the three outcomes from step 2 in one line each, and the answer to step 5. The sentence *why a minority member cannot serve writes* is on [the checklist](../../phases/02-etcd.md#checklist), and it must be written as a claim about safety rather than about connectivity — "it cannot reach a quorum" is a description, not a reason.

**Teardown** — `sudo iptables -S | grep 2380` on `.162` and confirm it is empty. `etcdctl del --prefix /part/`. **The topology stays.**
