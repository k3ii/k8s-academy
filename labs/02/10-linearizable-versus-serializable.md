<a id="linearizable-versus-serializable"></a>
# A stale read you caused on purpose

**Claim** — a serializable read is served from one member's local state with **no quorum round trip**, so it can return an older revision than a linearizable read taken at the same moment; and from `api_guarantees` you can name exactly what a client is forbidden from inferring from a revision number. This closes the question [P1 deferred](../01/06-resourceversion-moves.md).

**Rests on** — [module 2.1's](../../phases/02-etcd.md#m2-1) `data_model` and `api_guarantees` reading questions, and [objective 3](../../phases/02-etcd.md#objectives). `resourceVersion` upstream *is* an etcd revision; this exercise is where that sentence acquires its second half.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only). You will add a `netem` delay to `.162` and take it off again; [P0 taught the tool](../00/12-cut-a-link-then-slow-it.md).

**Do**

1. First, with the cluster healthy, show that the two consistency modes normally agree:

   ```sh
   etcdctl put /rv/key v1
   etcdctl --endpoints=http://10.10.10.162:2379 get /rv/key -w json | grep -o '"revision":[0-9]*'
   etcdctl --endpoints=http://10.10.10.162:2379 get /rv/key --consistency=s -w json | grep -o '"revision":[0-9]*'
   ```

2. Now widen the window. On `.162`, delay everything leaving the interface by 300ms — replication included:

   ```sh
   ssh zain@10.10.10.162 'sudo tc qdisc add dev ens18 root netem delay 300ms'
   ```

   Check the interface name first with `ip -br link`; the guest may not call it `ens18`.

3. Drive writes from `.160` in one terminal:

   ```sh
   while true; do etcdctl put /rv/key "$(date +%s%N)" > /dev/null; done
   ```

4. In another, read `.162` **locally**, so your own client traffic is not the thing being delayed:

   ```sh
   ssh zain@10.10.10.162
   while true; do
     L=$(etcdctl --endpoints=http://127.0.0.1:2379 get /rv/key -w json | grep -o '"revision":[0-9]*')
     S=$(etcdctl --endpoints=http://127.0.0.1:2379 get /rv/key --consistency=s -w json | grep -o '"revision":[0-9]*')
     echo "$L  $S"
   done
   ```

5. Stop the write loop, remove the delay, and check the two converge:

   ```sh
   ssh zain@10.10.10.162 'sudo tc qdisc del dev ens18 root'
   ```

6. Read what the guarantees document actually promises, and write the three sentences it forbids:

   - is a revision number comparable **across two different keys**?
   - does the *difference* between two revision numbers mean anything?
   - having read revision `N`, may a client assume a later read returns `≥ N`? Under which consistency mode, and against which member?

**Observe** — the two columns in step 4. Under load and delay they diverge, with the serializable read behind; the linearizable read is slower to return and never behind.

**Expect** — the serializable read costs a fraction of the linearizable one in latency and pays for it with a revision that may lag. The gap is small on an idle LAN cluster, which is exactly why it needs the `netem` to be visible at all and exactly why it is dangerous: **a stale read is not an error, it is a correct answer to a weaker question**, and nothing in the response distinguishes the two.

Answering step 6 well is the point of the exercise. The revision counter is a position in one log, so it orders *writes*, not *keys*; the difference between two of them counts everything the cluster did, including internal writes and the failed transaction from [exercise 8](08-what-sub-is-for.md); and monotonicity is a promise about a linearizable read against the cluster, not about whichever member your client reconnected to. Every one of those has an exact counterpart in [P1's `resourceVersion` rules](../01/06-resourceversion-moves.md) — go back and match them up one to one, because that mapping is the whole reason [P1](../../phases/01-operate-shallow.md) deferred the question rather than answering it badly.

**Write down** — the `resourceVersion = etcd revision` sentence with the guarantee it does **not** carry, in one sentence, and the three forbidden inferences with the `api_guarantees` wording behind each. [The checklist](../../phases/02-etcd.md#checklist) asks for this, and [P3](../../phases/03-api-machinery.md) assumes it.

**Teardown** — `etcdctl del /rv/key`, and **check the qdisc is gone**: `ssh zain@10.10.10.162 'tc qdisc show dev ens18'`. A forgotten `netem` will quietly poison the leader election timings in [module 2.2](../../phases/02-etcd.md#m2-2) and cost you a day. **The topology stays.**
