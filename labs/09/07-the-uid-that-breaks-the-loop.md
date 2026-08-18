<a id="the-uid-that-breaks-the-loop"></a>
# Delete the `--uid-owner 1337` exemptions and measure the loop: one request, many connections

**Claim** — the rules that exempt UID and GID **1337** from outbound redirection are **the only thing standing between the proxy and itself**. Remove them and Envoy's own upstream connection is redirected straight back into Envoy's outbound listener: one `curl` produces a burst of connections on port 15001 instead of one, which is the loop made visible as a counter rather than argued about.

**Rests on** — [the netfilter reading](06-interception-reduced-to-netfilter.md). You are deleting rules you have already mapped to their `istio-init` arg, in the pod you already found the PID for.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — the client's proxy is the one that loops**, so this is done in `sleep`, not `httpbin`. Confirm the baseline works and take the counters before touching anything:

```sh
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w '%{http_code}\n' http://httpbin:8000/get
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET stats \
  | grep -E '^listener\.0\.0\.0\.0_15001\.downstream_cx_total|^cluster_manager\.cds\.'
SPID=$(ssh zain@10.10.10.131 'sudo crictl inspect $(sudo crictl ps -q --label io.kubernetes.container.name=istio-proxy --label io.kubernetes.pod.namespace=mesh | head -1) | jq -r .info.pid')
```

Check that `$SPID` is the **`sleep`** pod's proxy and not `httpbin`'s before continuing — `sudo crictl ps --label io.kubernetes.container.name=istio-proxy` prints the pod name beside each container, and getting this wrong makes the rest of the exercise measure the wrong thing.

**Do — part 1, find every exemption, not the first one.** There is more than one, and how many there are is the answer to a question the previous exercise left open:

```sh
ssh zain@10.10.10.131 "sudo nsenter -t $SPID -n iptables -t nat -S ISTIO_OUTPUT"
```

**Do — part 2, delete them.** Delete by full rule specification rather than by line number, so a version whose chain is ordered differently does not silently remove something else:

```sh
ssh zain@10.10.10.131 "sudo nsenter -t $SPID -n iptables -t nat -D ISTIO_OUTPUT -m owner --uid-owner 1337 -j RETURN"
ssh zain@10.10.10.131 "sudo nsenter -t $SPID -n iptables -t nat -D ISTIO_OUTPUT -m owner --gid-owner 1337 -j RETURN"
ssh zain@10.10.10.131 "sudo nsenter -t $SPID -n iptables -t nat -S ISTIO_OUTPUT"
```

**Do — part 3, one request. Exactly one, with a timeout**, then read the counters:

```sh
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -m 5 -o /dev/null -w '%{http_code}\n' http://httpbin:8000/get
kubectl -n mesh exec deploy/sleep -c istio-proxy -- pilot-agent request GET stats \
  | grep -E '^listener\.0\.0\.0\.0_15001\.downstream_cx_(total|active)|^listener\.0\.0\.0\.0_15001\.downstream_cx_overflow'
kubectl -n mesh get pod -l app=sleep
```

**Expect** — **two** rules deleted in part 2, one for the UID and one for the GID. Both exist because a process is exempt on either credential, and netfilter's `owner` match takes one at a time; a chain that checked only the UID would loop for any workload whose proxy shares a group but not a user.

Expect part 3's request to **fail** — and treat the exact failure mode as the measurement, not as something to predict from memory. Record which of these you got: a `000` from `curl` hitting its own timeout, a `503` from Envoy, or a hang that ends when the connection budget runs out. What must be true in every case is the counter: **`downstream_cx_total` on the 15001 listener rises by far more than one for a single request**, because each connection Envoy opens to the upstream is redirected back into 15001 and becomes another downstream connection to accept. That ratio is the loop. Write the number down; it is the only observation in this exercise that is not version-dependent.

Expect the proxy to survive, and expect that to be Envoy's doing rather than luck — there are connection limits and an overload manager between this rule set and a dead pod. Do **not** hold the loop open to find out where the limit is: `istio-proxy` has a memory limit on the order of a gigabyte and the worker has [1948Mi of allocatable memory](04-the-request-that-does-not-fit.md) with [nothing to reclaim from](../../strands/lab-topologies.md#ceiling), so a loop left running is a node problem rather than a pod problem.

**Write down** — the two deleted rules verbatim, the before-and-after `downstream_cx_total`, and one sentence on the design question this raises: the exemption works because the proxy runs as a **different user than the application**, so injection must guarantee that. Name where that guarantee was made — the `runAsUser` in [the injection template](05-a-pod-the-webhook-rewrote.md) — and note that [ambient's data plane](20-a-namespace-with-no-sidecars.md) cannot use this trick at all, because there the proxy is not in the pod's user namespace or its netns to begin with. That contrast is the reason this exercise exists in a phase that ends in ambient.

**Teardown — restore, and prove the restoration** rather than assuming it. The rules are pod-scoped state written at pod creation, so the reliable repair is to throw the pod away:

```sh
kubectl -n mesh delete pod -l app=sleep
kubectl -n mesh rollout status deploy sleep
kubectl -n mesh exec deploy/sleep -c sleep -- curl -s -o /dev/null -w '%{http_code}\n' http://httpbin:8000/get
NEW=$(ssh zain@10.10.10.131 'sudo crictl inspect $(sudo crictl ps -q --label io.kubernetes.container.name=istio-proxy --label io.kubernetes.pod.namespace=mesh | head -1) | jq -r .info.pid')
ssh zain@10.10.10.131 "sudo nsenter -t $NEW -n iptables -t nat -S ISTIO_OUTPUT | grep 1337"
```

A `200` and both `1337` rules back is the gate on leaving this exercise. **A half-broken rule set left in place makes the next exercise fail for a reason that has nothing to do with the next exercise** — and unlike a deleted Kubernetes object, nothing reconciles it: no controller watches a pod's `nat` table, which is itself worth one line in the notes.

**The topology stays.**
