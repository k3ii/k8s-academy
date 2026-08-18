<a id="a-namespace-with-no-sidecars"></a>
# Switch the namespace to ambient: `1/1` pods, and sockets inside the pod's netns held by a process in another one

**Claim** — after the switch, `httpbin` and `sleep` are **`1/1` with no `istio-init` and no `istio-proxy`**, and yet their network namespaces contain listening sockets on 15008, 15006 and 15001. The process holding those sockets is `ztunnel`, running on the node in a **different** network namespace — provable by comparing `/proc/<pid>/ns/net` for the two processes and finding the pod's netns inode among `ztunnel`'s open file descriptors. **Nothing is encapsulated and no overlay is involved**: the node agent passed a namespace, not a tunnel.

**Rests on** — [the sidecar cost curve](19-what-a-sidecar-costs.md), which must be finished first because this exercise removes the thing it measured, and [the netfilter reading](06-interception-reduced-to-netfilter.md), whose rules are about to be replaced by a different mechanism in the same place.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — install the ambient data plane with the same `istiod` overrides.** Only the profile changes; keeping everything else identical is what makes [the second curve](21-the-same-curve-flat.md) a comparison rather than two unrelated measurements:

```sh
sed 's/profile: minimal/profile: ambient/' ~/istiod-academy.yaml > ~/istiod-ambient.yaml
diff ~/istiod-academy.yaml ~/istiod-ambient.yaml
istioctl install -f ~/istiod-ambient.yaml -y
kubectl -n istio-system get ds,deploy
kubectl -n istio-system get pods -o wide
```

**Do — move the namespace, and let the old data plane go:**

```sh
kubectl label namespace mesh istio-injection-
kubectl label namespace mesh istio.io/dataplane-mode=ambient
kubectl -n mesh rollout restart deploy httpbin sleep
kubectl -n mesh rollout status deploy httpbin && kubectl -n mesh rollout status deploy sleep
kubectl -n mesh get pods
kubectl -n mesh get pod -l app=httpbin -o json \
  | jq '.items[0] | {containers: [.spec.containers[].name], init: [.spec.initContainers[]?.name],
                     annotations: (.metadata.annotations | keys)}'
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w '%{http_code}\n' http://httpbin:8000/get
```

**Observe — part 1, where the proxy is now.** It is a DaemonSet, and it is not in the pod:

```sh
kubectl -n istio-system get pods -o wide | grep -E 'ztunnel|cni'
WK=$(kubectl get node -l '!node-role.kubernetes.io/control-plane' -o name | cut -d/ -f2)
ZPOD=$(kubectl -n istio-system get pod -l app=ztunnel --field-selector spec.nodeName=$WK -o jsonpath='{.items[0].metadata.name}')
echo $ZPOD
```

**Observe — part 2, the two namespaces and the file descriptor between them.** This is the exercise:

```sh
ZPID=$(ssh zain@10.10.10.131 'sudo crictl inspect $(sudo crictl ps -q --label io.kubernetes.container.name=ztunnel) | jq -r .info.pid')
APID=$(ssh zain@10.10.10.131 'sudo crictl inspect $(sudo crictl ps -q --label io.kubernetes.container.name=httpbin) | jq -r .info.pid')
ssh zain@10.10.10.131 "sudo readlink /proc/$ZPID/ns/net; sudo readlink /proc/$APID/ns/net; sudo readlink /proc/1/ns/net"
ssh zain@10.10.10.131 "sudo nsenter -t $APID -n ss -ltnp"
ssh zain@10.10.10.131 "sudo ls -l /proc/$ZPID/fd | grep -c 'net:'"
ssh zain@10.10.10.131 "sudo ls -l /proc/$ZPID/fd | grep 'net:' | head"
ssh zain@10.10.10.131 "sudo ls -l /var/run/ztunnel/"
```

**Observe — part 3, the rules that replaced `ISTIO_INBOUND`:**

```sh
ssh zain@10.10.10.131 "sudo nsenter -t $APID -n iptables -t mangle -S"
ssh zain@10.10.10.131 "sudo nsenter -t $APID -n iptables -t nat -S"
kubectl -n istio-system logs $ZPOD --tail=20
```

**Expect** — pods at **`1/1`**, no `istio-init`, no `sidecar.istio.io/status` annotation, and traffic still working. Expect two DaemonSets in `istio-system`: `ztunnel` and `istio-cni-node`. Expect the pod spec to hold **no privileged container at all** — the capability that wrote rules into this netns now belongs to a node agent, which is the security argument for ambient stated as an object diff rather than as a slogan.

Expect `ss -ltnp` **inside the pod's netns** to list sockets on **15008, 15006 and 15001**, with a process name and PID attached — and expect that PID to be `ztunnel`'s, whose `/proc/<pid>/ns/net` is a **different inode** from the application's. Read that carefully: `ss` resolves the process through the node's PID namespace while `nsenter -n` scoped it to the pod's network namespace, so you are seeing a process that is not in this namespace holding a listening socket in it.

Expect `/proc/<ztunnel-pid>/fd` to contain **`net:[…]` symlinks**, one per enrolled pod, and expect the application's netns inode to be one of them. That is the mechanism, and it is worth stating exactly because it is so often described wrongly: `istio-cni`'s node agent enters the new pod's network namespace, installs redirection there, then passes the **open namespace file descriptor to `ztunnel` over a Unix domain socket** — the one in `/var/run/ztunnel/`. `ztunnel` calls `setns` on that descriptor to create sockets in the pod's namespace and returns to its own. **There is no Geneve, no VXLAN and no encapsulation of the pod's traffic**; the node-to-node hop is an ordinary TCP connection to port 15008 carrying HTTP/2 `CONNECT` inside mTLS, which is what HBONE names.

Expect the `mangle` table to be where the work happens now — **`TPROXY` with connection marks** rather than `nat` `REDIRECT` — and expect that difference to have a reason worth writing down: `TPROXY` delivers the packet to a local socket **without rewriting the destination address**, so the original destination survives to the proxy without the `nat` bookkeeping a sidecar needs. Expect **no UID 1337 exemption anywhere**, and expect [the loop-breaking exercise](07-the-uid-that-breaks-the-loop.md) to be inapplicable here for a structural reason: the proxy's traffic originates in a different namespace, so it cannot match rules in this one.

**Write down** — in `journal/p9-ambient.md`: the two `ns/net` inodes with the file descriptor that links them, the socket list from inside the pod netns, the `mangle` rules, and a two-column table — sidecar versus ambient — for *where redirection is installed*, *who installs it*, *what capability the pod needs*, and *where the L7 proxy is*. Leave the last row's ambient cell empty; [the waypoint exercise](22-the-waypoint-l7-policy-needs.md) fills it in, and its being empty right now is the honest state of the mesh.

**Footprint note** — `ztunnel` and `istio-cni-node` are per **node**, not per pod: on the order of tens of Mi each, on both nodes. Against [the sidecars they replaced](19-what-a-sidecar-costs.md) that is a trade you can now measure rather than assume, which is [the next exercise](21-the-same-curve-flat.md). `istiod` itself is unchanged — same Deployment, same 512Mi request, same pinning to the control-plane node.

**Teardown** — the sidecars are already gone, removed by the rollout. Confirm nothing from the old data plane survived, and keep the ambient install:

```sh
kubectl -n mesh get pods -o wide
kubectl -n mesh get namespace mesh --show-labels
```

**Ambient stays** — [the flat curve](21-the-same-curve-flat.md), [the waypoint](22-the-waypoint-l7-policy-needs.md) and [its removal](23-the-waypoint-removed-and-the-silence.md) all run on it, and [the capstone](25-one-request-both-halves.md) reinstates sidecar mode deliberately for the comparison. **The topology stays.**
