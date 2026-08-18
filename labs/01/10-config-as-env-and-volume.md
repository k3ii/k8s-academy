<a id="config-as-env-and-volume"></a>
# The same ConfigMap, two ways in — and only one of them updates

**Claim** — a ConfigMap mounted as a volume changes inside a running container without a restart; the same ConfigMap consumed as an environment variable does not, ever. You can demonstrate both and name where the mounted copy actually comes from.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up.

**Do**

1. One ConfigMap and one Secret, consumed **both** ways by one pod:

   ```yaml
   env:
     - name: FROM_ENV
       valueFrom: {configMapKeyRef: {name: settings, key: colour}}
   volumeMounts:
     - {name: cfg, mountPath: /etc/app}
     - {name: sec, mountPath: /etc/creds, readOnly: true}
   volumes:
     - {name: cfg, configMap: {name: settings}}
     - {name: sec, secret: {secretName: apikey}}
   ```

2. **Predict** which of the two reflects an edit, and how long it takes. Then `kubectl edit cm/settings` and check both, once immediately and once after two minutes.
3. Find out what the mounted directory actually is:

   ```sh
   kubectl exec <pod> -- ls -la /etc/app
   kubectl exec <pod> -- readlink /etc/app/colour
   ```

   Two levels of symlink and a dot-directory. Say what that indirection buys — specifically, what a reader of the file sees during an update.

4. Confirm the Secret mount's filesystem type from inside, and connect it to [P0](../../phases/00-linux-primitives.md):

   ```sh
   kubectl exec <pod> -- mount | grep /etc/creds
   kubectl exec <pod> -- df -h /etc/creds
   ```

5. Break it usefully: reference a key that does not exist, once via `configMapKeyRef` and once via a volume `items` entry. The two failures happen at different times and in different places, and only one of them is visible in `kubectl get pods`.
6. Set `optional: true` on the env reference and observe that the pod now starts with the variable simply absent.

**Expect** — the volume updates within about a minute (the kubelet's sync period, not instantly); the environment variable is fixed at process exec and no mechanism exists to change it, which is why config-by-env implies a rollout. The mount is a **tmpfs**, so the Secret never touches the node's disk — a mount type you handled directly in [P0](../../phases/00-linux-primitives.md), now wearing a manifest field. The missing-key env case leaves the pod in `CreateContainerConfigError`; the missing-key volume case starts the pod and the file is simply not there — a failure your application discovers, not the kubelet.

**Write down** — the two-row update table, and three manifest-field-to-P0-primitive mappings so far: `resources.limits.memory` → cgroup, `secret` volume → `tmpfs` mount, and the one from [the capability drop](11-drop-a-capability-in-a-manifest.md). [The checklist](../../phases/01-operate-shallow.md#checklist) asks for at least three.

**Teardown** — delete the pod, ConfigMap and Secret. **The topology stays.**
