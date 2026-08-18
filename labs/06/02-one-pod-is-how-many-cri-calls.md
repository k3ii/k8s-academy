<a id="one-pod-is-how-many-cri-calls"></a>
# Predict the CRI calls that start one pod, then count them

**Claim** — starting one single-container pod takes a fixed, small sequence of CRI calls that you can write down from the protobuf before you ever see it happen, and `crictl` on a live node accounts for every one of them — including one container you did not ask for.

**Rests on** — [the inventory](01-the-sub-managers-named.md), specifically its `RuntimeService`/`ImageService` split and your one-line answer about the sandbox.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), **provisioned here** and kept up until the phase's last exercise. Two nodes rather than three because [the phase is DaemonSet-heavy](../../phases/06-kubelet-node.md) — Chaos Mesh's daemon, node-exporter and kube-proxy all cost once per node — and two is the smallest number that still has a worker to pressure while the control plane stays alive to watch it.

**Setup** — provision per [the five steps](../../strands/lab-topologies.md#provision), then confirm the runtime and the cgroup version, both of which every later exercise in this phase assumes:

```sh
ssh zain@10.10.10.131 'sudo crictl version; stat -fc %T /sys/fs/cgroup; sudo cat /etc/containerd/config.toml | grep -i SystemdCgroup'
```

`cgroup2fs` is the answer you want from `stat`; if it says `tmpfs` you are on a v1 hierarchy and [module 6.4](../../phases/06-kubelet-node.md#m6-4) does not apply to this node.

**Do**

1. **Before touching the node**, read the proto (item 3) and write the sequence:

   ```sh
   sed -n '/service RuntimeService/,/^}/p' ~/src/kubernetes/staging/src/k8s.io/cri-api/pkg/apis/runtime/v1/api.proto | grep '  rpc'
   ```

   From those RPC names alone, write the ordered list of calls the kubelet must make to go from "a pod is bound to me" to "the container is running". Include the image path. Six to eight calls is the right order of magnitude; commit to a number.

2. Watch it happen. On the worker, in one session:

   ```sh
   ssh zain@10.10.10.131 'sudo journalctl -u kubelet -f -o cat' 
   ```

   and from the Mac:

   ```sh
   kubectl create ns node-lab
   kubectl -n node-lab run probe --image=registry.k8s.io/pause:3.10 --restart=Never
   ```

3. Account for the sandbox from the node's own view:

   ```sh
   ssh zain@10.10.10.131 'sudo crictl pods --name probe -o json | jq ".items[].id"'
   ssh zain@10.10.10.131 'sudo crictl ps -a --pod <pod-id>'
   ssh zain@10.10.10.131 'sudo crictl inspectp <pod-id> | jq ".info.pid, .status.linux.namespaces"'
   ```

4. Find the shared namespaces. `crictl inspect` the application container and compare its `pid` and its namespace paths with the sandbox's. Which namespaces are shared with the sandbox, and which are the container's own?

**Observe** — `crictl images` before and after (was `PullImage` called at all, and what decided that), and the sandbox's own process:

```sh
ssh zain@10.10.10.131 'sudo ps -o pid=,comm=,args= -p $(sudo crictl inspectp <pod-id> | jq -r .info.pid)'
```

**Expect** — your list to be short and mostly right, with one systematic error: people forget that the sandbox is created *and started* before any application container exists, so `RunPodSandbox` precedes `CreateContainer` and there is nothing to attach a network namespace to until it has run. The `pause` process itself does nothing but hold namespaces open — `ps` shows it sleeping forever, and killing it takes the pod's whole network identity with it.

Expect `PullImage` to depend on `imagePullPolicy` and on whether the image is already in `crictl images`, which is why a pod that starts in 400 ms on the second node takes eight seconds on the first.

**Write down** — your predicted sequence beside the observed one, the diff between them, and the corrected one-line answer to "what is the sandbox for". That line is now evidence rather than a paraphrase, and [the capstone](29-the-capstone-trace.md) starts from the other end of the same lifecycle.

**Footprint note** — `pair` is 5.0GB and [`forge`](../../strands/lab-topologies.md#build-guest) stays at its normal 1536MB all phase (nothing is compiled here — [the phase has no build artifact](../../phases/06-kubelet-node.md)), so the steady state is **6.5GB against the [9.5GB ceiling](../../strands/lab-topologies.md#ceiling), 3.0GB of margin**. The margin is not spare: it is what [the two installs](08-chaos-mesh-at-582mi.md) and [the stack](25-the-stack-that-must-not-be-evicted.md) spend, and they spend it *inside* the guests, where a 2048MB worker has far less than 3.0GB free.

**Teardown** — `kubectl delete ns node-lab`. **The topology stays** — every remaining exercise in this phase runs on it.
