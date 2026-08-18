<a id="botch-a-rollout-and-roll-back"></a>
# Chaos drill 1.C3 — wedge a rollout, then recover it

**Claim** — a rollout with a broken new image stops rather than fails, leaves the service up, and can be diagnosed from `kubectl` output alone and reversed in under three minutes. You can say which field capped the damage and which object made the reversal possible.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up. [By hand](../../strands/chaos.md#principle) — and **run it twice**: once exploring, once against a clock, because [the checklist times this at three minutes](../../phases/01-operate-shallow.md#checklist).

**Setup** — a Deployment at 5 replicas with `maxSurge: 1, maxUnavailable: 0` and a readiness probe. Keep traffic on it throughout — a `while true; do wget -qO- ...; sleep 0.2; done` loop from a pod, so "did anyone notice" is a question with an answer rather than a guess.

**Do**

1. Break it in the way that wedges rather than crashes: roll an image whose readiness probe never passes. (The other two shapes — an image that does not exist, and a missing ConfigMap key — behave differently and you should do all three, one at a time.)
2. **Do not run `rollout undo` yet.** First observe, in this order, and write down what each told you:

   ```sh
   kubectl rollout status deploy/web --timeout=60s    # what does it say, and does it return?
   kubectl get rs                                     # the counts
   kubectl get pods                                   # which ones are not ready
   kubectl describe pod <the new one>                 # the reason, in the Events block
   ```

3. Answer three questions from that output alone: how many replicas are serving; how many the *old* ReplicaSet still has; and what stopped the controller from continuing.
4. Check the traffic loop. Did a single request fail?
5. Now `kubectl rollout undo deploy/web`, and watch which ReplicaSet scales. Confirm the wedged one goes to zero and is *kept*.
6. Repeat the whole thing with `maxUnavailable: 2` and compare the traffic loop's error count. This is the experiment that makes the field mean something.
7. Do all three break-shapes once each and note where the diagnosis differs: `ImagePullBackOff` names the problem in `get pods`; the missing ConfigMap key gives `CreateContainerConfigError`; the failing probe gives a `Running` pod that is `0/1` and says nothing until you `describe` it. **Rank them by how long they take you to spot.**

**Expect** — the rollout stops with the old ReplicaSet still at full strength and the new one holding one unready pod; `rollout status` never returns and its timeout is the only reason you get your prompt back. With `maxUnavailable: 0` the traffic loop sees zero errors — the outage is entirely in the *deployment*, not in the service — and that is what makes this failure mode dangerous: it is invisible to users and to dashboards, and it will sit wedged until someone looks. With `maxUnavailable: 2` the same break costs real requests.

**Write down** — the four observations from step 2, the three answers from step 3, the traffic-loop error counts for both `maxUnavailable` values, and your ranking from step 7. **This transcript is the raw material for [the incident note](24-the-incident-note.md)** — you cannot write that note from memory, and this is the run you will be writing about.

**Teardown** — `kubectl rollout undo` back to a healthy image, delete the traffic-loop pod, and confirm `deploy/web` is fully ready before you leave. **The topology stays.**
