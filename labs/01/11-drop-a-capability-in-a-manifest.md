<a id="drop-a-capability-in-a-manifest"></a>
# The P0 capability drop, as a manifest field

**Claim** — `securityContext.capabilities` produces exactly the bounding set and effective set that you predict. You can prove this from inside the container with `capsh --decode`, and you do not have to trust the field.

**Rests on** — [P0's capability work](../00/17-drop-a-capability.md). There you dropped one capability by hand, and you lost one syscall. This exercise adds no mechanism. It only changes who makes the call.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up.

**Do**

1. Take a baseline first. Run a plain pod, and read the actual sets instead of the documentation:

   ```sh
   kubectl exec <pod> -- grep ^Cap /proc/1/status
   kubectl exec <pod> -- sh -c 'capsh --decode=$(grep CapEff /proc/1/status | cut -f2)'
   ```

   Write the default set down. It is not empty. It is also not the full set of root. The container runtime already dropped approximately two thirds of the capabilities before Kubernetes said anything.

2. **Predict, then apply, four variants.** Run the same two commands after each variant:

   ```yaml
   securityContext:
     capabilities: {drop: [ALL], add: [NET_BIND_SERVICE]}
     runAsNonRoot: true
     runAsUser: 1000
     allowPrivilegeEscalation: false
   ```

   - `drop: [ALL]` alone.
   - `drop: [ALL]` plus `add: [NET_BIND_SERVICE]`.
   - `runAsNonRoot: true` with `runAsUser: 1000`, and capabilities left alone.
   - All of the above together.

3. Make the capability *do* something. Add `NET_BIND_SERVICE`, then bind port 80 as UID 1000. Then remove the `add`, and try the same bind. The failure is `EACCES` from `bind(2)`. It happens at the syscall, and not at admission.
4. Test `allowPrivilegeEscalation: false` properly. Run a setuid binary inside the container, and watch it fail to gain anything. Then check `NoNewPrivs` in `/proc/1/status`. The field set one bit.
5. Try `runAsNonRoot: true` on an image whose `USER` is root, and whose manifest gives no `runAsUser`. The pod does not start, and the message names the check.
6. Add `readOnlyRootFilesystem: true`, and find what breaks. Fix the break with an `emptyDir` on the one path that must be writable.

**Expect** — with `drop: [ALL]`, `CapEff` is `0000000000000000`, and `capsh --decode` prints nothing after the `=`. With the `add`, exactly one bit is set. The **bounding** set is the ceiling. A capability that is not in the bounding set cannot be regained by any means inside the container. You proved that same statement by hand in P0, and it is why `add` cannot escalate past what the runtime allowed. Note where `runAsNonRoot` is enforced: the *kubelet* checks it against the resolved UID of the image, at container start. Its failure is therefore a pod that never runs, and not a rejected manifest. That distinction matters when you diagnose from `kubectl get pods` alone.

**Write down** — the table of four variants, with the decoded sets. Include the `capsh` output for the added capability. [The checklist](../../phases/01-operate-shallow.md#checklist) times you at three minutes on this pod, from memory. This exercise is where you make it correct, and not where you make it fast.

**Teardown** — delete the pods. **The topology stays.**
