<a id="resume-a-watch-from-a-revision"></a>
# A watch that starts in the past

**Claim** — a watch opened with `--rev=N` replays every event from `N` onward before it delivers anything live, and the revision a client passes to resume is the same number `resourceVersion` carried in [P1](../01/06-resourceversion-moves.md). This is the mechanism the entire Kubernetes control plane is a client of.

**Rests on** — [module 2.3's](../../phases/02-etcd.md#m2-3) `api` doc question: how does a client *resume* a watch, and what does it pass? Answer it before running this.

**Topology** — [`etcd-only`](../../strands/lab-topologies.md#etcd-only).

**Do**

1. Establish a starting point and make history after it:

   ```sh
   R=$(etcdctl put /w/start x -w json | python3 -c 'import sys,json; print(json.load(sys.stdin)["header"]["revision"])')
   for i in $(seq 1 5); do etcdctl put /w/k$i "$i"; done
   etcdctl del /w/k3
   ```

2. Open a watch from `R` and count what arrives before anything live does:

   ```sh
   etcdctl watch --prefix /w/ --rev=$R
   ```

   Leave it running. In a second terminal, `etcdctl put /w/k9 live`.

3. Read the event stream carefully. For each event note its type and its revision, and answer three questions:

   - is the delete replayed as an event, or as an absence?
   - is `/w/k1`'s *value* in the event, or only its key?
   - does the replay include the write at revision `R` itself, or start after it?

   The third one has cost people a great deal of time. Test it rather than assuming.

4. Now the resume pattern as a client would implement it. Kill the watch, note the revision of the last event you received, and restart from **that** revision:

   ```sh
   etcdctl watch --prefix /w/ --rev=<last-seen>
   ```

   Do you receive the last event twice, or not at all? One of those is a duplicate and one is a lost update, and which you get determines whether a client resuming a watch must add one or not. Get this wrong in a controller and it silently drops an event per reconnect.

5. Ask for the future:

   ```sh
   etcdctl watch --prefix /w/ --rev=999999999
   ```

   Then write a key. Say what the server did with a revision that does not exist yet.

6. Find the surface in the API doc and match your observations to it:

   ```sh
   (cd ~/src/etcd && git grep -n 'start_revision' -- Documentation/ api/ | head)
   ```

**Expect** — the replay arrives as a burst of ordinary events, indistinguishable in shape from live ones, followed by the live one from step 2. Nothing marks the boundary between history and now. A client that needs to act only on live events has to compute that boundary itself from the revision it started at — which is exactly what an informer's initial-list-then-watch does, and why it lists first rather than watching from `0`.

Step 5 is the asymmetric case: a future revision is accepted and simply waits, while [a past one that has been compacted is refused](18-compact-under-a-live-watcher.md). One end of the range is open and the other is a cliff, and the whole of [module 2.3](../../phases/02-etcd.md#m2-3) is about the cliff.

**Write down** — the answer to step 4 as a rule of the form *"resume from X, because Y"*, and the boundary question from the Expect paragraph. [P4](../../phases/04-controllers.md) builds an informer on top of exactly this and will assume you have the rule.

**Teardown** — `etcdctl del --prefix /w/`. **The topology stays.**
