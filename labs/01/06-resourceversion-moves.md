<a id="resourceversion-moves"></a>
# What a changed resourceVersion does and does not promise

**Claim** — you can state, and then demonstrate, exactly two things a client may do with `resourceVersion` and at least three it may not — including one that looks obviously safe and is not.

**Rests on** — [module 1.2's reading question](../../phases/01-operate-shallow.md#m1-2), the *Resource Version* section. **Write your answer before running anything.** The demonstrations below are designed to catch a wrong answer, not to supply the right one.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), with the `objectmodel` namespace from [the previous exercise](05-spec-status-ownership.md).

**Do**

1. Watch one move. In one terminal:

   ```sh
   kubectl -n objectmodel get cm/settings -o yaml -w \
     | grep -E 'resourceVersion|^  [a-z]+:'
   ```

   In another, `kubectl -n objectmodel annotate cm/settings poke=1 --overwrite`, then `poke=2`, then `poke=2` again. The third one does not move it. Say why in terms of what a write is.

2. **Test whether it is comparable.** Record the `resourceVersion` of your ConfigMap and of your Deployment at the same moment. Is one larger? Now annotate *only the ConfigMap* three times and compare again. Then answer: does a larger number mean *newer*? Does it mean newer **for a different object**? The conventions answer both, and only one of your answers is allowed to be "yes".
3. **Use it the way it is meant to be used** — as an optimistic-concurrency token:

   ```sh
   RV=$(kubectl -n objectmodel get cm/settings -o jsonpath='{.metadata.resourceVersion}')
   kubectl -n objectmodel annotate cm/settings other=1 --overwrite     # someone else writes
   kubectl -n objectmodel replace -f <(kubectl -n objectmodel get cm/settings -o json \
     | jq --arg rv "$RV" '.metadata.resourceVersion=$rv | .data.k="v"')
   ```

   Read the rejection. That error is the entire reason the field is in every object.

4. **Use it the other way it is meant to be used** — as a watch cursor. Take a version, make three changes, then start a watch *from* that version and count the events you receive:

   ```sh
   kubectl get --raw "/api/v1/namespaces/objectmodel/configmaps?watch=1&resourceVersion=$RV" | head -3
   ```

5. Now do the forbidden thing on purpose: try `resourceVersion=1`, and try a very large number.

**Expect** — step 3 fails with a `Conflict` naming the object, and that is the mechanism every controller in [P4](../../phases/04-controllers.md) relies on to avoid lost updates. Step 4 replays the changes you made after `$RV` — the value is a *position in a stream*, which is the strongest hint yet at what it will turn out to be in [P2](../../phases/02-etcd.md). Step 5's first case either replays from the beginning or returns `410 Gone` depending on how much history exists, and the second is rejected outright: the number is opaque to you and meaningful to the server, and *you may not do arithmetic on it* is the rule the whole section exists to state.

**Write down** — the two permitted uses and three forbidden ones, in one sentence each, with the error message you actually got for the ones you tested. [The checklist](../../phases/01-operate-shallow.md#checklist) asks for the rule; the errors are what make it yours.

**Teardown** — `kubectl -n objectmodel annotate cm/settings poke- other-`. **The topology stays.**
