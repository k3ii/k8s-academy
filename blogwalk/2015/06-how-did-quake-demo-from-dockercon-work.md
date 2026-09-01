<a id="how-did-quake-demo-from-dockercon-work"></a>
# Kubernetes shipped the half of this post that produces a file, and not the half that resumes a process

**Post** — [How did the Quake demo from DockerCon Work?](https://kubernetes.io/blog/2015/07/how-did-quake-demo-from-dockercon-work/),
2015-07-02, Kubernetes pre-1.0 — three weeks before the 1.0 release.

**As written** — nothing in this post touches Kubernetes. It is an engineering report on making
[CRIU](https://criu.org) — Checkpoint/Restore In Userspace — work on a Docker container, and its
premise is a gap: Docker has `start`, `stop`, `restart`, `kill`, `pause`, `unpause`, and "what is
still missing is the ability to Checkpoint and Restore (C/R) a container natively via Docker
itself."

It lists five reasons to want it:

- restart the Docker daemon without killing running containers
- reboot the machine without restarting containers from scratch
- speed up slow-start applications
- "*Forensic debugging*" of container processes by examining their checkpoint images
- "*Migrate containers by restoring them on a different machine*"

Phase 1 is external C/R — drive CRIU by hand, from outside Docker — and the three problems it had
to solve are the whole flavour of the era: Docker's external bind mounts for
`/etc/{hostname,hosts,resolv.conf}` (fixed by adding `--ext-mount-map` to CRIU), AUFS exposing
physical branch paths in `/proc/<pid>/map_files` (fixed by generalising `--root`), and the Docker
daemon deleting the container's cgroup directories on "exit" (fixed by adding
`--manage-cgroups`). The command it lands on:

```
$ sudo criu dump -o dump.log -v4 -t 17810 \
        -D /tmp/img/<container_id> \
        --root /var/lib/docker/aufs/mnt/<container_id> \
        --ext-mount-map /etc/resolv.conf:/etc/resolv.conf \
        --ext-mount-map /etc/hosts:/etc/hosts \
        --ext-mount-map /etc/hostname:/etc/hostname \
        --ext-mount-map /.dockerinit:/.dockerinit \
        --manage-cgroups \
        --evasive-devices
```

Restoring needs the AUFS branch stack re-mounted by hand first — six `br=` layers listed by
digest — and afterwards `docker ps -a` still says `Exited`, because Docker has no idea the
process is back. Phase 2 adds `checkpoint()`/`restore()` to libcontainer and
`docker checkpoint`/`docker restore` to Docker, and the hard part is re-parenting the container's
stdio pipes when CRIU, not the daemon, is the parent — solved by adding `--inherit-fd` to CRIU.

Then the forecasts. "We hope that checkpoint and restore commands will be introduced in **Docker
1.8**." "Work is underway to merge C/R functionality into Docker." Meanwhile, use one of two
personal GitHub forks — `SaiedKazemi/docker` at Docker 1.5 ("relatively stable") or
`boucher/docker` at 1.7 ("newer, less stable"). And the Quake demo itself: a container running
Quake, checkpointed on one machine and restored on another, at DockerCon15 — "effectively
implementing container migration."

**As it runs now** — nothing in the *As written* section can be run on a Kubernetes node, and the
reasons are worth separating carefully:

1. **The path this post travels no longer reaches a Kubernetes container.** Every command is aimed
   at the Docker daemon and its storage driver. Since v1.24 the kubelet does not talk to Docker at
   all, so `/var/lib/docker/aufs/mnt/<id>` is not where your container's root filesystem is, and
   `/.dockerinit` is not in it. See [the CRI exercise](03-docker-and-kubernetes-and-appc.md) for
   why.
2. **The two forks are the wrong kind of dead.** They are personal branches of a five-releases-old
   Docker, offered as the way to get the feature. Nothing errors when you visit them; they simply
   are not a supported path to anything, and the post's "work is underway to merge" is the last
   word it has on the subject.
3. **The capability arrived — in Kubernetes, not in the post's vehicle.** The kubelet has a
   checkpoint API: `POST /checkpoint/{namespace}/{pod}/{container}`, gated on
   `ContainerCheckpoint`, which has been **beta and on by default since v1.30**. It asks the CRI
   implementation for a checkpoint and writes
   `checkpoint-<podFullName>-<containerName>-<timestamp>.tar` into `/var/lib/kubelet/checkpoints`.
4. **The restore half does not exist as a Kubernetes operation, and that is not an oversight.**
   The API has exactly one operation. The reference page's own framing is passive — "if you move
   the checkpointed container data to a computer **that's able to restore it**" — and the page
   still carries an editorial TODO saying return codes cannot be documented properly until CRI
   implementations have checkpoint *and* restore, a note written before the **v1.25** release and
   still there at v1.37, two stages later.
5. **Four of the five reasons were answered by refusing the question.** Restart the daemon without
   killing containers, reboot without restarting from scratch, migrate a running container: a
   Kubernetes cluster's answer to all three is that pods are disposable and a controller makes
   another one. Slow start is answered by probes, sidecars and pre-pulled images. The one
   remaining item on the post's list — "forensic debugging … by examining their checkpoint
   images" — is, word for word, the use case the pin's checkpoint page leads with.

**The diff, and why** — the post is a **plan the project abandoned** wrapped around a **stasis**
finding, and separating the two is the exercise.

The abandoned plan is the vehicle. C/R was going to arrive as `docker checkpoint`, in the daemon,
because in 2015 the daemon was the thing that owned containers on a Kubernetes node. That premise
was deleted in v1.24, and with it any route from this post's commands to a running pod.

The stasis is the destination, and it is a *deliberate* asymmetry rather than a stalled promotion.
Checkpointing produces an artefact: a tar file on a node, which some other tool may or may not be
able to open. That fits Kubernetes's model, because producing a file is a node-local operation
with no bearing on what the cluster believes is running. Restoring does not fit, and no amount of
release cycles will make it fit, because a Pod is a *declaration* — "run this image with these
resources" — and a restored process tree is the opposite: a specific set of memory pages, open
file descriptors, cgroup paths and kernel version, none of which the Pod API has a field for and
all of which the scheduler would have to honour exactly. The post's own Phase 1 is the proof: it
took three new CRIU command-line options to restore into the *same* daemon on the *same* machine.
There is no schema for that.

So the ladder below reads as a success and the missing operation reads as a failure, and both
readings are wrong. What went to beta is a debugging endpoint. What did not arrive is a feature
Kubernetes decided not to have.

The security paragraph on the pin's page is the other half of the reason, and it is unusually
blunt for a reference: a checkpoint "contains all memory pages of all processes in the
checkpointed container", so "everything that used to be in memory is now available on the local
disk. This includes all private data and possibly keys used for encryption." An operation that
serialises your secrets to a tar file is not one you promote quickly, and it explains five
releases at alpha better than any missing code would.

Release facts and the pressure behind each are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.25 – v1.29 |
| beta | `true` | — | v1.30 – |

`ContainerCheckpoint`, whole; the gate file declares neither `removed` nor a closing
`toVersion`, so beta-on-by-default is the current state and not a way-station. Note what the
table cannot tell you: whether *your* node's runtime implements the CRI call the endpoint
forwards to. The gate governs the kubelet, not the runtime, and step 4 is where that distinction
stops being academic.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), fresh — the checkpoint lands on the
node's disk and you want it to be the only interesting thing there. Bring it up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, then `ssh zain@10.10.10.180`.

**Do**

1. Give yourself a container with state worth freezing — the point of the post's Quake demo,
   reduced to a counter you can read:

   ```sh
   kubectl run ticker --image=busybox --restart=Never -- \
     sh -c 'i=0; while true; do i=$((i+1)); echo $i > /tmp/n; sleep 1; done'
   kubectl wait --for=condition=Ready pod/ticker --timeout=60s
   sleep 30
   kubectl exec ticker -- cat /tmp/n
   ```

2. Confirm the gate the endpoint depends on is actually on, from the kubelet rather than from a
   table:

   ```sh
   N=$(kubectl get pod ticker -o jsonpath='{.spec.nodeName}')
   kubectl get --raw "/api/v1/nodes/$N/proxy/configz" | tr ',' '\n' | grep -i ContainerCheckpoint \
     || echo 'not set explicitly — the default applies'
   ```

3. Look for the post's world on the node, so that step 4's failure cannot be blamed on it:

   ```sh
   sudo ls /var/lib/docker 2>&1 | head -2
   sudo ls -d /var/lib/kubelet/checkpoints 2>&1
   ```

4. Now ask the kubelet to do what the post spent eighteen months teaching CRIU to do. It is a
   `POST`, so `--raw` needs `create`:

   ```sh
   kubectl create --raw "/api/v1/nodes/$N/proxy/checkpoint/default/ticker/ticker" -f /dev/null
   echo "exit=$?"
   ```

   Record the status code and the message. All three documented outcomes are informative and only
   one of them is about your cluster being misconfigured.

5. If step 4 returned 200, read the artefact — and note that reading it is all Kubernetes offers:

   ```sh
   sudo ls -lh /var/lib/kubelet/checkpoints/
   sudo tar tf /var/lib/kubelet/checkpoints/checkpoint-ticker_default-ticker-*.tar | head -20
   ```

   Find the counter's value inside the archive. The post's five benefits all assumed you would
   never need to.

6. Search for the operation the post's whole Phase 2 was about:

   ```sh
   kubectl api-resources | grep -i -E 'checkpoint|restore'
   kubectl get --raw "/api/v1/nodes/$N/proxy/checkpoint/default/ticker/ticker" 2>&1 | head -2
   ```

7. Then test the answer Kubernetes gave instead of restore. Kill the node's container out from
   under the pod and time how long the cluster takes to have a running `ticker` again:

   ```sh
   sudo crictl ps --name ticker -q | xargs -r sudo crictl stop
   kubectl get pod ticker -w
   ```

   Write down what happened to `/tmp/n`, and which of the post's five benefits that outcome
   satisfies and which it discards.

**Expect** — step 1 prints a number in the twenties or thirties: the state the post's demo exists
to preserve.

Step 2 usually prints nothing, because a beta gate that is on by default does not need to appear
in the kubelet's configuration. That absence is the ladder's second row.

Step 3 finds no `/var/lib/docker` on a modern node, and `/var/lib/kubelet/checkpoints` may not
exist yet — the kubelet creates it on first use.

Step 4 gives you one of three things, all of them documented on the pin's checkpoint page:

- **200** — the runtime implemented `CheckpointContainer` and you have a tar file.
- **500**, with a message about the CRI implementation not implementing the checkpoint CRI API —
  the kubelet is willing and the runtime is not. This is the most likely result, and it is the
  point of the exercise rather than a defect in your lab: eleven years after this post, whether
  you can checkpoint a container still depends on which runtime somebody installed, exactly as it
  depended on which storage driver Docker was using.
- **404** — the gate is off, which contradicts step 2 and means your distribution disabled it.

Step 5's archive is a tar whose contents "depend on the underlying CRI implementation" — the pin
declines to specify them, which tells you how load-bearing this interface is not.

Step 6 finds nothing. There is no `checkpoints` resource, no restore verb, and a `GET` on the same
path is not an API. The post's Phase 2 has no counterpart here at all.

Step 7 is the answer Kubernetes actually shipped: the container is recreated within seconds, the
pod name and IP survive, and `/tmp/n` restarts from 1. Availability was preserved; state was
not. Four of the post's five benefits are satisfied by that and the fifth — forensics — is what
step 4 is for. A cluster that treats containers as disposable does not need to migrate them, and
that is why the missing half of this post has never been missed.

**Read on** — the [CRI protocol
definition](https://github.com/kubernetes/cri-api/blob/v0.33.1/pkg/apis/runtime/v1/api.proto):
find `CheckpointContainer` in the `RuntimeService`, then look for its inverse. Write down what an
RPC that restored a container would have to promise the kubelet about the node it is restoring
onto, and why that promise cannot be made through an interface whose implementations the project
does not control.

**Teardown** — `kubectl delete pod ticker` and
`sudo rm -rf /var/lib/kubelet/checkpoints/checkpoint-ticker_default-*` — a checkpoint archive is
a plaintext copy of everything that container had in memory, so do not leave it lying on the
guest. Leave the guest up; [the TLS exercise](07-strong-simple-ssl-for-kubernetes.md) runs on it.
