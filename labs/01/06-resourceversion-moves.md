<a id="resourceversion-moves"></a>
# What a changed resourceVersion does and does not promise

**Claim** — you can state exactly two things that a client may do with `resourceVersion`, and at least three things that it may not do. You can then demonstrate them. One of the forbidden uses looks obviously safe, and it is not.

**Rests on** — [module 1.2's reading question](../../phases/01-operate-shallow.md#m1-2), the *Resource Version* section. **Write your answer before you run anything.** The demonstrations below are designed to catch a wrong answer. They are not designed to supply the right one.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), with the `objectmodel` namespace from [the previous exercise](05-spec-status-ownership.md).

**Do**

1. Watch one move. In the first terminal, run:

   ```sh
   kubectl -n objectmodel get cm/settings -o yaml -w \
     | grep -E 'resourceVersion|^  [a-z]+:'
   ```

   In the second terminal, run `kubectl -n objectmodel annotate cm/settings poke=1 --overwrite`. Then set `poke=2`. Then set `poke=2` again. The third command does not move the version. Say why, in terms of what a write is.

2. **Test whether the value is comparable.** Record the `resourceVersion` of your ConfigMap and of your Deployment at the same moment. Is one of them larger? Now annotate *only the ConfigMap*, three times, and compare again. Then answer two questions. Does a larger number mean *newer*? Does it mean newer **for a different object**? The conventions answer both questions, and only one of your answers may be "yes".
3. **Use the field the first way that it is meant to be used**, as an optimistic-concurrency token:

   ```sh
   RV=$(kubectl -n objectmodel get cm/settings -o jsonpath='{.metadata.resourceVersion}')
   kubectl -n objectmodel annotate cm/settings other=1 --overwrite     # someone else writes
   kubectl -n objectmodel replace -f <(kubectl -n objectmodel get cm/settings -o json \
     | jq --arg rv "$RV" '.metadata.resourceVersion=$rv | .data.k="v"')
   ```

   Read the rejection. That error is the entire reason why the field is in every object.

4. **Use the field the second way that it is meant to be used**, as a watch cursor. Take a version. Make three changes. Then start a watch *from* that version, and count the events that you receive:

   ```sh
   kubectl get --raw "/api/v1/namespaces/objectmodel/configmaps?watch=1&resourceVersion=$RV" | head -3
   ```

5. Now do the forbidden thing on purpose. Try `resourceVersion=1`. Then try a very large number.

**Expect** — step 3 fails with a `Conflict` that names the object. Every controller in [P4](../../phases/04-controllers.md) relies on that mechanism to avoid lost updates. Step 4 replays the changes that you made after `$RV`, so the value is a *position in a stream*. That is the strongest hint so far about what the value turns out to be in [P2](../../phases/02-etcd.md). Step 5 has two cases. The first case either replays from the beginning or returns `410 Gone`, and the result depends on how much history exists. The second case is rejected outright. The number is opaque to you and meaningful to the server, and *you may not do arithmetic on it*. That is the rule which the whole section exists to state.

**Write down** — the two permitted uses and the three forbidden ones, in one sentence each. Include the error message that you actually got for each case that you tested. [The checklist](../../phases/01-operate-shallow.md#checklist) asks for the rule. The errors are what make the rule yours.

**Teardown** — run `kubectl -n objectmodel annotate cm/settings poke- other-`. **The topology stays.**
