<a id="fill-the-quota"></a>
# 2.C4 — drive it into `NOSPACE` and get it back

**Claim** — crossing `--quota-backend-bytes` puts the **whole cluster** into a read-only alarm state that survives deleting data, and the recovery has exactly one correct ordering: compact, defrag, disarm. Doing them in any other order either fails or appears to work and leaves the cluster armed.

**Rests on** — [exercise 20](20-compaction-frees-no-disk.md) and [exercise 21](21-defrag-frees-disk-and-blocks.md). The ordering is not arbitrary and you should be able to derive it from those two before running this: the alarm is about `dbSize`, compaction does not move `dbSize`, and defrag needs the free pages compaction produces.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only). All three units get a small quota and are restarted one at a time.

**Setup**

The default quota is 2GB. Filling that on this hardware would take a long time and produce nothing extra, so set it low deliberately — add to all three unit files:

```
  --quota-backend-bytes 67108864 \
```

Restart one member at a time, `etcdctl endpoint health --cluster` between each. Confirm no alarm is set to begin with:

```sh
etcdctl alarm list
etcdctl endpoint status --cluster -w json | python3 -m json.tool | grep -E 'dbSize'
```

**Do**

1. Churn until it stops. Values large enough to get there in minutes rather than hours:

   ```sh
   V=$(head -c 8000 /dev/urandom | base64 -w0)
   i=0
   while true; do
     i=$((i+1))
     etcdctl put /quota/k "$V" > /dev/null 2>&1 || { echo "stopped at $i"; break; }
     [ $((i % 200)) -eq 0 ] && etcdctl endpoint status -w json | python3 -c 'import sys,json; print(json.load(sys.stdin)[0]["Status"]["dbSize"])'
   done
   ```

2. Read the failure, then read the alarm:

   ```sh
   etcdctl put /quota/again x
   etcdctl alarm list
   etcdctl endpoint status --cluster -w table
   ```

3. Establish exactly how read-only it is. Test all four, and predict each before running it:

   ```sh
   etcdctl get /quota/k --keys-only        # a read
   etcdctl del /quota/k                    # a delete — is a delete a write?
   etcdctl compact <some-rev>              # maintenance
   etcdctl put /quota/x y                  # a write
   ```

   The delete is the one worth thinking about hardest. It removes data; it is also a write; the alarm exists because writes are what filled the disk. Which wins?

4. **Do the recovery in the wrong order first**, because the failure teaches the ordering:

   ```sh
   etcdctl alarm disarm
   etcdctl put /quota/x y
   ```

   Say what happened and why.

5. Now the right order:

   ```sh
   REV=$(etcdctl endpoint status -w json | python3 -c 'import sys,json; print(json.load(sys.stdin)[0]["Status"]["header"]["revision"])')
   etcdctl compact $REV
   etcdctl endpoint status --cluster -w json | python3 -m json.tool | grep -E 'dbSize'   # still large
   for n in 160 161 162; do etcdctl --endpoints=http://10.10.10.$n:2379 defrag; done
   etcdctl endpoint status --cluster -w json | python3 -m json.tool | grep -E 'dbSize'   # now small
   etcdctl alarm disarm
   etcdctl alarm list
   etcdctl put /quota/x y
   ```

6. Answer why the alarm needs an explicit disarm at all, rather than clearing itself when `dbSize` drops. State it as a design argument, not as a description.

**Observe** — the write loop stops with `etcdserver: mvcc: database space exceeded`. `alarm list` shows `NOSPACE` against a member ID. Reads keep working throughout.

**Expect** — the cluster is read-only on **every** member, not just the one that filled up, because the alarm is raised cluster-wide. Step 3's delete fails: a delete is a write, it consumes a revision and more disk, and permitting it would be the exact wrong response to being out of space — which is the single most counter-intuitive thing in this drill and the reason people escalate.

Step 4 fails again immediately: disarming without fixing anything re-triggers the alarm on the next write, because nothing about the disk changed. Step 5 works because compaction produced free pages inside the file and defrag returned them, in that order — reverse them and the defrag has nothing to reclaim.

Step 6's answer: an alarm that cleared itself would flap, and a cluster oscillating between writable and read-only is worse for every client than one that stays down until a human has looked at it. The explicit disarm is an assertion that someone has.

**Footprint note — the 64MB quota is a deliberate change from the 2GB default**, made so this drill fits inside a 10G guest and a working session rather than an afternoon. It changes nothing about the mechanism: the alarm, the read-only state and the recovery ordering are identical at any quota. **Say so in the write-up** — a measurement taken at a non-default setting is fine, and a measurement whose setting is undisclosed is not.

**Write down** — the recovery as three ordered steps with one sentence of *why this step is here* each, and the answer to step 3's delete question. [The checklist](../../phases/02-etcd.md#checklist) asks you to do this from memory, timed; the write-up is what you rehearse from.

**Teardown** — `etcdctl del --prefix /quota/`, then compact and defrag once more so the phase's remaining exercises start from a small `db`. **Remove the `--quota-backend-bytes` line from all three units** and restart one at a time, or [the corruption drill](26-corrupt-a-member.md) will hit a quota you have forgotten about. **The topology stays.**
