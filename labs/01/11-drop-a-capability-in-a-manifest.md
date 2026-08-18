<a id="drop-a-capability-in-a-manifest"></a>
# The P0 capability drop, as a manifest field

**Claim** — `securityContext.capabilities` produces exactly the bounding and effective sets you predict, and you can prove it from inside the container with `capsh --decode` rather than by trusting the field.

**Rests on** — [P0's capability work](../00/17-drop-a-capability.md), where you dropped one capability by hand and lost one syscall. This exercise adds no mechanism; it only changes who makes the call.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up.

**Do**

1. Baseline first. Run a plain pod, and read the actual sets rather than the docs:

   ```sh
   kubectl exec <pod> -- grep ^Cap /proc/1/status
   kubectl exec <pod> -- sh -c 'capsh --decode=$(grep CapEff /proc/1/status | cut -f2)'
   ```

   Write down the default set. It is not empty, and it is not root's full set either — the container runtime already dropped about two-thirds before Kubernetes said anything.

2. **Predict, then apply, four variants**, running the same two commands after each:

   ```yaml
   securityContext:
     capabilities: {drop: [ALL], add: [NET_BIND_SERVICE]}
     runAsNonRoot: true
     runAsUser: 1000
     allowPrivilegeEscalation: false
   ```

   - `drop: [ALL]` alone.
   - `drop: [ALL]` plus `add: [NET_BIND_SERVICE]`.
   - `runAsNonRoot: true` with `runAsUser: 1000`, capabilities left alone.
   - all of the above together.

3. Make the capability *do* something. With `NET_BIND_SERVICE` added, bind port 80 as UID 1000; then remove the `add` and try the same bind. The failure is `EACCES` from `bind(2)`, and it happens at the syscall, not at admission.
4. Test `allowPrivilegeEscalation: false` properly: run a setuid binary inside the container and watch it fail to gain anything. Then check `NoNewPrivs` in `/proc/1/status` — the field set one bit.
5. Try `runAsNonRoot: true` on an image whose `USER` is root and whose manifest gives no `runAsUser`. The pod does not start, and the message names the check.
6. Add `readOnlyRootFilesystem: true` and find what breaks. Fix it with an `emptyDir` on the one path that needs to be writable.

**Expect** — with `drop: [ALL]`, `CapEff` is `0000000000000000` and `capsh --decode` prints nothing after the `=`; with the `add`, exactly one bit is set. The **bounding** set is the ceiling — a capability not in it cannot be regained by any means inside the container, which is the same statement you proved by hand in P0 and is why `add` cannot be used to escalate past what the runtime allowed. `runAsNonRoot` is checked by the *kubelet* against the image's resolved UID at container start, so its failure is a pod that never runs rather than a rejected manifest — a distinction that matters when you are diagnosing from `kubectl get pods` alone.

**Write down** — the four-variant table with the decoded sets, and the `capsh` output for the added capability. [The checklist](../../phases/01-operate-shallow.md#checklist) times you at three minutes on this pod, from memory; this exercise is where you make it correct, not fast.

**Teardown** — delete the pods. **The topology stays.**
