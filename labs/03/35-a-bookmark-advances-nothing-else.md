<a id="a-bookmark-advances-nothing-else"></a>
# A watch event that carries no object change

**Claim** — with `allowWatchBookmarks=true`, a watch on a quiet resource receives periodic `BOOKMARK` events whose `resourceVersion` advances while nothing about the object changed; and a client that resumes from a bookmark survives churn that would have 410'd a client resuming from its last real event.

**Rests on** — [the ring overflow](33-overflow-the-ring.md). Bookmarks exist because of the failure you produced there, and this is the mitigation stated as an experiment rather than as a feature description.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. Two watches on the same quiet resource, side by side in two terminals:

   ```sh
   kubectl create ns quiet
   kubectl get --raw "/api/v1/namespaces/quiet/configmaps?watch=true&allowWatchBookmarks=true" | jq -c '{t:.type, rv:.object.metadata.resourceVersion, n:.object.metadata.name}'
   kubectl get --raw "/api/v1/namespaces/quiet/configmaps?watch=true"                          | jq -c '{t:.type, rv:.object.metadata.resourceVersion, n:.object.metadata.name}'
   ```

2. In a third terminal, churn a *different* namespace hard enough to move the global resource version — the loop from [the ring exercise](33-overflow-the-ring.md). Do not touch `quiet`.

3. Watch both streams for several minutes. Record the last `resourceVersion` each one has seen.

4. Kill both watches. Resume each from **its own** last-seen version, then churn hard again and resume once more:

   ```sh
   kubectl get --raw "/api/v1/namespaces/quiet/configmaps?watch=true&resourceVersion=$LAST_BOOKMARKED"
   kubectl get --raw "/api/v1/namespaces/quiet/configmaps?watch=true&resourceVersion=$LAST_PLAIN"
   ```

5. Find the interval in the code rather than timing it into a guess. Search `storage/cacher/` for where bookmarks are produced and what governs their cadence; note whether the interval is fixed or jittered and why jitter is there at all.

**Observe** — the `type` field on each event, and whether the bookmark's object carries anything besides `metadata.resourceVersion`.

**Expect** — the bookmarked stream shows `BOOKMARK` events at intervals with an advancing `resourceVersion` and an otherwise **empty object** — no name, no data, the kind only. The plain stream shows nothing at all for the whole run.

Step 4 is the payoff: the bookmarked client resumes cleanly after churn that leaves the plain client with a `410`. It is the same watch on the same objects; the only difference is that one of them was told where "now" is while it had nothing to do.

The jitter answer in step 5 is worth the search: without it, every watcher in a large cluster receives its bookmark on the same schedule, and the mitigation for a thundering herd is itself a thundering herd.

**Write down** — the bookmark object's exact shape, the interval you found and its citation, and one sentence on what a client must do differently to benefit — the flag is opt-in for a reason, and the reason is what a naive client would do with an event whose object is empty.

**Teardown** — `kubectl delete ns quiet` and any churn namespace. **The topology stays** — [the consistent-read question](36-cache-or-etcd.md) is next.
