<a id="botch-a-rollout-and-roll-back"></a>
# Chaos drill 1.C3 — wedge a rollout, then recover it

**Claim** — a rollout with a broken new image stops, and it does not fail. It leaves the service up. You can diagnose it from `kubectl` output alone, and reverse it in less than three minutes. You can also say which field capped the damage, and which object made the reversal possible.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up. Do this drill [by hand](../../strands/chaos.md#principle). **Run it twice**: once to explore, and once against a clock. [The checklist times this drill at three minutes](../../phases/01-operate-shallow.md#checklist).

**Setup** — use a Deployment at 5 replicas, with `maxSurge: 1, maxUnavailable: 0` and a readiness probe. Keep traffic on it throughout. Run a loop from a pod, such as `while true; do wget -qO- ...; sleep 0.2; done`. The loop turns "did anyone notice?" into a question with an answer, instead of a guess.

**Do**

1. Break the rollout in the way that wedges it, rather than crashes it. Roll an image whose readiness probe never passes. There are two other break-shapes: an image that does not exist, and a missing ConfigMap key. They behave differently, and you should do all three, one at a time.
2. **Do not run `rollout undo` yet.** Observe first, in this order, and write down what each command told you:

   ```sh
   kubectl rollout status deploy/web --timeout=60s    # what does it say, and does it return?
   kubectl get rs                                     # the counts
   kubectl get pods                                   # which ones are not ready
   kubectl describe pod <the new one>                 # the reason, in the Events block
   ```

3. Answer three questions from that output alone. How many replicas are serving? How many replicas does the *old* ReplicaSet still have? What stopped the controller from continuing?
4. Check the traffic loop. Did a single request fail?
5. Now run `kubectl rollout undo deploy/web`, and watch which ReplicaSet scales. Confirm that the wedged ReplicaSet goes to zero, and that it is *kept*.
6. Repeat the whole drill with `maxUnavailable: 2`, and compare the error count of the traffic loop. This experiment is what makes the field mean something.
7. Do all three break-shapes once each, and note where the diagnosis differs. `ImagePullBackOff` names the problem in `get pods`. The missing ConfigMap key gives `CreateContainerConfigError`. The failing probe gives a `Running` pod that is `0/1`, and it says nothing until you `describe` it. **Rank the three by how long each one takes you to spot.**

**Expect** — the rollout stops. The old ReplicaSet stays at full strength, and the new one holds one unready pod. `rollout status` never returns, and its timeout is the only reason that you get your prompt back. With `maxUnavailable: 0`, the traffic loop sees zero errors. The outage is entirely in the *deployment*, and not in the service. That is what makes this failure mode dangerous: it is invisible to users and to dashboards, and it stays wedged until somebody looks. With `maxUnavailable: 2`, the same break costs real requests.

**Write down** — four things. The four observations from step 2. The three answers from step 3. The error counts of the traffic loop for both `maxUnavailable` values. Your ranking from step 7. **This transcript is the raw material for [the incident note](24-the-incident-note.md).** You cannot write that note from memory, and this is the run that you will be writing about.

**Teardown** — run `kubectl rollout undo` back to a healthy image. Delete the traffic-loop pod. Confirm that `deploy/web` is fully ready before you leave. **The topology stays.**
