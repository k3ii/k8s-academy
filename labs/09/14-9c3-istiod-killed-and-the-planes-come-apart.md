<a id="9c3-istiod-killed-and-the-planes-come-apart"></a>
# 9.C3 — scale `istiod` to zero: traffic that exists keeps flowing, a Service that arrives is never heard of, and no pod can be created

**Artifact** — drill [9.C3](../../phases/09-service-mesh.md#chaos): a control plane taken to zero replicas, with **three results recorded side by side** — requests still returning 200, a new Service that never reaches the dump, and a pod creation that is refused outright by the injection webhook. The third is not in the drill's description and is the one worth arguing about, because it is the case where the two planes are *not* separate.

**Rests on** — [the injection webhook](05-a-pod-the-webhook-rewrote.md), whose `failurePolicy: Fail` you predicted this from, and [the NACK exercise](11-an-ack-and-a-nack.md), where Envoy already demonstrated it keeps the last state it accepted.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — a baseline of all three things you are about to test:**

```sh
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w '%{http_code}\n' http://httpbin:8000/get
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET stats | grep -E 'control_plane\.connected_state'
istioctl -n mesh proxy-status
```

**Do — take the control plane away.** Scale rather than delete: a deleted pod is recreated in seconds and the window closes before you have measured anything:

```sh
kubectl -n istio-system scale deploy istiod --replicas=0
kubectl -n istio-system get pods
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET stats | grep -E 'control_plane\.connected_state'
```

**Observe — result 1, the data plane.** Run this for long enough to be convincing, not once:

```sh
kubectl -n mesh exec deploy/sleep -c sleep -- \
  sh -c 'for i in $(seq 30); do curl -s -o /dev/null -w "%{http_code} " http://httpbin:8000/get; sleep 1; done; echo'
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET config_dump > ~/dump-nocp.json
diff <(jq -S '[.configs[] | select(."@type"|test("Clusters")) | .dynamic_active_clusters[].cluster.name]|sort' ~/dump-dynamic.json) \
     <(jq -S '[.configs[] | select(."@type"|test("Clusters")) | .dynamic_active_clusters[].cluster.name]|sort' ~/dump-nocp.json)
```

**Observe — result 2, a Service that arrives with nobody listening:**

```sh
kubectl -n mesh create service clusterip academy-orphan --tcp=9998:9998
kubectl -n mesh get svc academy-orphan
sleep 20
istioctl -n mesh proxy-config cluster deploy/sleep --fqdn academy-orphan.mesh.svc.cluster.local
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -m 3 -o /dev/null -w '%{http_code}\n' http://academy-orphan:9998/
```

**Observe — result 3, the one the drill's description does not mention:**

```sh
kubectl -n mesh run canary --image=curlimages/curl --restart=Never -- sleep 60
kubectl -n mesh get pods
```

**Expect** — `control_plane.connected_state` to fall to **0** within seconds and the 30 requests to be **thirty 200s**. Expect the cluster-name `diff` to be **empty**: not one resource was lost, because Envoy holds its configuration in memory and the ADS stream's absence is not a signal to forget anything. That is the phase's [objective 4](../../phases/09-service-mesh.md#objectives), observed rather than asserted.

Expect the new Service to exist in the API, get a ClusterIP, and be **entirely absent** from the proxy — `proxy-config cluster` finds nothing, and the request to it fails. Expect the *failure mode* to be worth a line in the notes: with no cluster for that address, the connection falls through to the passthrough or blackhole path rather than being refused, so what you see is a timeout or a 502 rather than "no such host". DNS resolved fine; the proxy simply had no configuration for the destination.

Expect result 3 to be a **hard refusal**: `Error from server (InternalError): ... failed calling webhook "namespace.sidecar-injector.istio.io" ... connect: connection refused`, and **no pod object created at all**. This is the honest boundary on "the planes are separate". They are separate for *traffic*; they are joined at *admission*, because [the webhook is `failurePolicy: Fail`](05-a-pod-the-webhook-rewrote.md) and every pod creation in a labelled namespace now depends on a Deployment that is scaled to zero. A node reboot during an `istiod` outage does not bring the workloads back.

Expect `istioctl proxy-status` to fail with a connection error rather than report anything about the proxies — the tool talks to `istiod`, not to the sidecars, so **your observability of the mesh dies with the control plane while the mesh itself does not**. Two different sentences, and conflating them is the mistake this drill exists to prevent.

**Write down** — in `journal/p9-9c3.md`: the three results with their evidence, and a fourth line for what you did *not* test and why — **certificate expiry**. The sidecar's certificate is short-lived and rotated by `istiod`; an outage longer than the certificate lifetime ends with mTLS failing everywhere, which means "existing traffic keeps flowing" has a clock on it. Name the lifetime from [the certificate exercise](15-a-certificate-that-names-a-serviceaccount.md) once you have measured it, and state the outage budget that follows from it.

**Teardown — restore, and prove all three results reverse:**

```sh
kubectl -n istio-system scale deploy istiod --replicas=1
kubectl -n istio-system rollout status deploy istiod
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET stats | grep -E 'control_plane\.connected_state'
istioctl -n mesh proxy-status
istioctl -n mesh proxy-config cluster deploy/sleep --fqdn academy-orphan.mesh.svc.cluster.local
kubectl -n mesh run canary --image=curlimages/curl --restart=Never -- sleep 60
kubectl -n mesh get pod canary -o jsonpath='{.spec.containers[*].name}'; echo
kubectl -n mesh delete pod canary --ignore-not-found
kubectl -n mesh delete svc academy-orphan
rm -f ~/dump-nocp.json
```

`connected_state` back to **1**, `academy-orphan` now present as a cluster, and `canary` created **with a sidecar** — the same command that was refused a minute ago. Delete both; they were instruments, not workloads. **The topology stays.**
