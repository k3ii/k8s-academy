<a id="helm-does-not-reconcile"></a>
# Delete something Helm created and watch nothing happen

**Claim** — Helm has no controller. You can prove that in three commands. Delete an object from a release. Wait as long as you like. Then run `helm upgrade`, and watch the object *still* not come back.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), with the release from [the release-state exercise](20-helm-upgrade-and-release-state.md).

**Do**

1. Run `kubectl delete svc <the release's service>`. Note the time.
2. Wait five minutes. Then check two things. `helm status t` says `deployed`. `helm list` shows one healthy release. Neither command has noticed the deletion.
3. Now run `helm upgrade t build/01-chart` with **no value changes**. Predict the result first, then look. Is the Service back?
4. Repeat the upgrade with **one value changed**. Predict again. This time the Service comes back. The reason is not that Helm noticed the deletion.
5. Explain the difference using [the three-way merge](20-helm-upgrade-and-release-state.md) alone. Do not invent a mechanism. Answer two questions. What does Helm PATCH? What does it do about an object that is in the new manifest and absent from the cluster?
6. Try `helm upgrade --force`. Note that it changes the answer by changing the *verb*. It does not add a watch.
7. Finally, ask what a controller would have done differently. Write the answer as a sentence about *when*, and not about *what*. That sentence is the argument that [Flux](../../phases/04-controllers.md) makes.

**Expect** — nothing happens after five minutes, after an hour, or after a week. There is no process anywhere whose job is to look. The outcome of step 3 depends on two things: how your version of Helm handles a no-op upgrade, and whether the render is byte-identical. When Helm does recreate the object, the cause is mechanical. The upgrade *applied the whole new manifest*, found the object missing, and created it. That is an accident of apply semantics, and not reconciliation. Here is the gap in one line. Helm converges **when you run it**. A controller converges **because time passed**. Level-triggered reconciliation is precisely what Helm does not have, and you have already watched it three times in this phase: in [1.C1](13-delete-a-managed-pod.md), in [the status stomp](07-stomp-the-status.md), and in [the endpoint rebuild](17-break-the-endpoints.md).

**Write down** — the one-sentence difference from step 7, in *when* terms. It is the whole GitOps argument, and you now have the experiment behind it.

**Teardown** — run `helm upgrade` to restore the release to health. **The topology stays**, because [the capstone chart](23-the-multi-service-app.md) builds on this release.
