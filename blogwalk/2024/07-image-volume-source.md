<a id="image-volume-source"></a>
# A gate is not a schedule

**Post** — [Kubernetes 1.31: Read Only Volumes Based On OCI Artifacts (alpha)](https://kubernetes.io/blog/2024/08/16/kubernetes-1-31-image-volume-source/),
2024-08-16, Kubernetes v1.31.

**As written** — a new alpha volume source, [KEP-4639](https://kep.k8s.io/4639). Put an image
reference where a volume goes and mount it:

```yaml
kind: Pod
spec:
  containers:
    - volumeMounts:
        - name: my-volume
          mountPath: /path/to/directory
  volumes:
    - name: my-volume
      image:
        reference: my-image:tag
```

The framing is explicit about *why*: Kubernetes was designed for microservices and is now being
asked to serve AI/ML, where you want to ship a model or a dataset as an OCI artifact rather than
bake it into the application image. Alpha in v1.31, so you enable the `ImageVolume` feature gate
and try it.

**As it runs now** — it works with no gate to enable. The field is unconditional, and two things
about the shape have changed since the post: `subPath` and `subPathExpr` mounts on an image
volume are supported (from v1.33), and there is a *new* alpha gate, `ImageVolumeWithDigest`,
adding the resolved image digest to the Pod's status.

So nothing broke, nothing was withdrawn, and a reader following the post today would succeed —
and would still have learned the wrong lesson, because the interesting part of this post is the
sentence it does not contain.

**The diff, and why** — here is the ladder `ImageVolume` actually climbed, from the feature-gate
reference at the pin:

| stage | default | releases |
|---|---|---|
| alpha | `false` | v1.31 – v1.32 |
| beta | **`false`** | v1.33 – v1.34 |
| beta | `true` | v1.35 |
| stable | `true` | v1.36 – |

Five releases, four stage changes, and the step that matters is the second one: **beta with the
gate still off by default, for two releases.** "Graduates to beta" is read as "on unless you
turn it off" — that is what beta has meant for most features for most of Kubernetes' life — and
for `ImageVolume` in v1.33 and v1.34 it was false. A cluster on v1.34 that had read a
"now in beta" post would have had a Pod with an `image` volume start, mount nothing where the
volume should be, and never say why.

Compare a feature from the *same year*, announced four months earlier: `RecursiveReadOnlyMounts`
went alpha in v1.30, beta-and-on in v1.31, and stable-and-locked in v1.33 — three releases, no
off-by-default beta, done in eighteen months.

Two features, one year, both shipped by SIG Node, and their graduations share no shape at all.
That is the lesson: **a feature gate records a decision that was made, not a schedule that will
be kept.** The stage tells you what the project currently promises about an API's stability. It
tells you nothing about the default, nothing about the date, and nothing about whether the next
step is up. `ImageVolume` needed CRI work in both containerd and CRI-O before the default could
flip, and that is why it sat in beta-off — a fact you can only get from the ladder, never from
the announcement.

This is the shape of a 2024 diff. In [2015](../2015/README.md) the diff is that the commands are
gone; here the commands are fine and the diff is in the *trajectory* — which is why the census
records a version for every row and why a `walk` verdict on a still-working post is not a
contradiction.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo). Bring it up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, then `ssh zain@10.10.10.180`.

**Do**

1. Do not look up whether the gate is still there — ask the cluster, and record whatever you get,
   including nothing:

   ```sh
   kubectl get --raw /metrics | grep -i 'feature_enabled.*[Ii]mageVolume'
   ```

2. Run the post's example unmodified, with no gate set anywhere. Use an image whose contents you
   can recognise:

   ```sh
   cat <<'YAML' | kubectl apply -f -
   apiVersion: v1
   kind: Pod
   metadata:
     name: img
   spec:
     containers:
     - name: c
       image: busybox
       command: ["sh", "-c", "sleep 3600"]
       volumeMounts:
       - name: vol
         mountPath: /mnt/artifact
     volumes:
     - name: vol
       image:
         reference: busybox:1.36
         pullPolicy: IfNotPresent
   YAML
   kubectl exec img -- ls /mnt/artifact
   ```

3. Establish that it is a volume and not a second container: write to it.
   `kubectl exec img -- touch /mnt/artifact/x`.

4. Test the failure mode the docs describe, which is the one that will bite in production. Delete
   the pod, then re-apply it with `reference: registry.example.invalid/nope:v1` and
   `pullPolicy: Never`. `kubectl get pod img` and `kubectl describe pod img`.

5. Now the archaeology, which is the point. Reconstruct the ladder yourself from the pinned
   website tree — `content/en/docs/reference/command-line-tools-reference/feature-gates/` —
   reading `ImageVolume.md` beside `RecursiveReadOnlyMounts.md`. Two questions to answer in
   writing: which of the two is `locked: true` at stable and what that changes for a cluster
   operator, and what a "beta" badge is worth as a prediction given these two ladders.

6. `ImageVolumeWithDigest` is alpha at the pin — a new gate on a feature that already went
   stable. Read its file and work out why the digest could not simply have been added to the
   status when the feature graduated.

**Expect** — step 2 succeeds. No gate, no `--feature-gates`, no kubelet config: the volume mounts
and `ls` lists the busybox root filesystem. Step 3 fails read-only — the mount is not writable
and no field makes it writable.

Step 4 is the failure you should be able to recognise later: the Pod does not schedule-then-crash
and it does not report a missing volume. It goes to `Failed`, and the reason is on the Pod, not
on the container — volume resolution happens at Pod startup, so the container never runs at all.
That is a *better* failure than the silent empty mount a v1.34 cluster would have given you, and
noticing the difference is the exercise.

Step 5 is where the year's real lesson lands. Write down the sentence you would now add to the
original post, in 2024, that would have made it honest about what "alpha" was promising.

**Read on** — [KEP-4639](https://github.com/kubernetes/enhancements/tree/master/keps/sig-node/4639-oci-volume-source):
find the `kep.yaml` milestones and compare them to the ladder in step 5. Where the two disagree,
which one happened?

**Teardown** — `kubectl delete pod img --ignore-not-found`. Leave the guest up;
[the WebSockets exercise](10-websocket-transition.md) runs on it.
