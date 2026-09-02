<a id="config-as-env-and-volume"></a>
# The same ConfigMap, two ways in — and only one of them updates

**Claim** — a ConfigMap that you mount as a volume changes inside a running container, with no restart. The same ConfigMap consumed as an environment variable never changes. You can demonstrate both behaviours, and you can name where the mounted copy actually comes from.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up.

**Do**

1. Take one ConfigMap and one Secret. Consume them **both** ways, in one pod:

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

2. **Predict two things.** Which of the two paths reflects an edit, and how long does the change take? Then run `kubectl edit cm/settings`, and check both paths. Check them once immediately, and once after two minutes.
3. Find out what the mounted directory actually is:

   ```sh
   kubectl exec <pod> -- ls -la /etc/app
   kubectl exec <pod> -- readlink /etc/app/colour
   ```

   You find two levels of symlink and a dot-directory. Say what that indirection buys you. Be specific: what does a reader of the file see during an update?

4. Confirm the filesystem type of the Secret mount from inside the container. Then connect the type back to [P0](../../phases/00-linux-primitives.md):

   ```sh
   kubectl exec <pod> -- mount | grep /etc/creds
   kubectl exec <pod> -- df -h /etc/creds
   ```

5. Break the configuration in a useful way. Reference a key that does not exist, once through `configMapKeyRef`, and once through a volume `items` entry. The two failures happen at different times and in different places. Only one of them is visible in `kubectl get pods`.
6. Set `optional: true` on the env reference. Observe that the pod now starts, and that the variable is simply absent.

**Expect** — the volume updates within approximately one minute. That delay is the sync period of the kubelet, and the update is not instant. The environment variable is fixed when the process execs. No mechanism exists to change it, and that is why configuration by environment variable implies a rollout. The Secret mount is a **tmpfs**, so the Secret never touches the disk of the node. You handled that mount type directly in [P0](../../phases/00-linux-primitives.md), and here it wears a manifest field. The two missing-key cases also differ. The env case leaves the pod in `CreateContainerConfigError`. The volume case starts the pod, and the file is simply not there — your application discovers that failure, and the kubelet does not.

**Write down** — the update table of two rows. Then write the three mappings from manifest field to P0 primitive that you have so far: `resources.limits.memory` → cgroup, `secret` volume → `tmpfs` mount, and the one from [the capability drop](11-drop-a-capability-in-a-manifest.md). [The checklist](../../phases/01-operate-shallow.md#checklist) asks for at least three.

**Teardown** — delete the pod, the ConfigMap and the Secret. **The topology stays.**
