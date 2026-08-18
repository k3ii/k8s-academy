<a id="helm-does-not-reconcile"></a>
# Delete something Helm created and watch nothing happen

**Claim** — Helm has no controller, and you can prove it in three commands: delete an object from a release, wait as long as you like, then run `helm upgrade` and watch it *still* not come back.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), with the release from [the release-state exercise](20-helm-upgrade-and-release-state.md).

**Do**

1. `kubectl delete svc <the release's service>`. Note the time.
2. Wait five minutes. Check `helm status t` — it says `deployed`. Check `helm list` — one healthy release. Neither has noticed.
3. Now `helm upgrade t build/01-chart` with **no value changes**. Predict first, then look: is the Service back?
4. Repeat with **one value changed**. Predict again. This time it comes back, and the reason is not that Helm noticed the deletion.
5. Explain the difference from [the three-way merge](20-helm-upgrade-and-release-state.md) alone, without inventing a mechanism. The question to answer is: what does Helm PATCH, and what does it do about an object that is in the new manifest and absent from the cluster?
6. Try `helm upgrade --force` and note that it changes the answer by changing the *verb*, not by adding a watch.
7. Finally, ask what a controller would have done differently, and write it as a sentence about *when* rather than *what*. That sentence is the argument [Flux](../../phases/04-controllers.md) makes.

**Expect** — five minutes, an hour, a week: nothing happens, because there is no process anywhere whose job is to look. Step 3's outcome depends on your Helm version's handling of a no-op upgrade and on whether the render is byte-identical; when it does recreate, it is because the upgrade *applied the whole new manifest*, found the object missing, and created it — an accident of apply semantics, not reconciliation. That is the gap: Helm converges **when you run it**, and a controller converges **because time passed**. Level-triggered reconciliation, which you have watched three times in this phase already ([1.C1](13-delete-a-managed-pod.md), [the status stomp](07-stomp-the-status.md), [the endpoint rebuild](17-break-the-endpoints.md)), is precisely what Helm does not have.

**Write down** — the one-sentence difference from step 7, in *when* terms. It is the whole GitOps argument and you now have the experiment behind it.

**Teardown** — `helm upgrade` to restore the release to health. **The topology stays** — [the capstone chart](23-the-multi-service-app.md) builds on this release.
