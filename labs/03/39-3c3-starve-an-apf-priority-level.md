<a id="3c3-starve-an-apf-priority-level"></a>
# 3.C3 — one client, one priority level, everyone in it queued

**Claim** — a single client issuing well-formed, authorized, individually reasonable requests can drive one priority level's queues to saturation, causing `429` for **other** clients sharing that level while requests in other levels are unaffected; and you can name the two configuration choices that decide how far the damage spreads.

**Rests on** — [the FlowSchema exercise](38-which-flowschema-caught-the-request.md), which is where you learned to read the headers this drill's diagnosis depends on. The talk in [the phase's list](../../phases/03-api-machinery.md#m3-5) is the same failure in production.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup — the escape hatch, written down before anything is broken.** APF can be turned off entirely by removing the feature gate, but that requires editing the static pod manifest on `.130` and waiting for a restart, and if you have saturated the level your own `kubectl` uses you may not be able to reach the cluster to fix it. So:

1. Open a second SSH session to `.130` **now** and leave it open. Node-level access does not go through APF.
2. Confirm `sudo crictl ps` and `sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml` both work in it.
3. Note that your admin kubeconfig is very likely in `system:masters` and therefore **exempt** — which means the drill will not lock you out, and that is a property of your lab rather than of production. Say so in the write-up.

**Do**

1. Pick the target level from [the previous exercise](38-which-flowschema-caught-the-request.md)'s table — one with queues, a small `nominalConcurrencyShares`, and a FlowSchema you can match on demand. `global-default` or a workload-serviceaccounts level is the usual choice.

2. Create two ServiceAccounts, `noisy` and `quiet`, in the same namespace, with identical RBAC — both can list ConfigMaps. Confirm from the headers that both land in the same FlowSchema.

3. Populate 500 ConfigMaps so a list is expensive enough to hold a seat.

4. Flood as `noisy` — many parallel expensive lists, each one a legitimate request:

   ```sh
   for i in $(seq 1 60); do
     ( while :; do kubectl --token=$NOISY get cm -n load >/dev/null 2>&1; done ) &
   done
   ```

5. With the flood running, measure `quiet`:

   ```sh
   time kubectl --token=$QUIET get cm -n load -v=6 2>&1 | grep -E 'Response Status|X-Kubernetes-PF'
   ```

   And measure a request in a *different* level, as yourself: `time kubectl get nodes`.

6. Now the configuration question. Stop the flood. Change **one** thing — either give the FlowSchema a `distinguisherMethod` of `ByUser`, or raise the target level's `nominalConcurrencyShares` — and repeat steps 4–5. Then change the other. Three measurements, one variable at a time.

7. Kill every background job: `jobs -p | xargs kill`. Verify with `jobs` that nothing survived; a forgotten flood loop poisons every measurement in [the next exercise](40-3c4-apiserver-down-controllers-up.md).

**Observe**

```sh
kubectl get --raw /metrics | grep -E 'apiserver_flowcontrol_(current_inqueue_requests|rejected_requests_total|request_wait_duration_seconds_count)'
kubectl get --raw /metrics | grep apiserver_flowcontrol_current_executing_requests
```

Watch `current_inqueue_requests` by priority level, not in total. The whole diagnosis is which label value is moving.

**Expect** — `quiet` sees latency in seconds and then `429 Too Many Requests` with a `Retry-After`. Your own `kubectl get nodes` is unaffected, which is APF working exactly as designed — the containment boundary is the priority level, and it holds.

The two configuration answers from step 6, which are the drill's actual finding:

- **The distinguisher decides whether `noisy` can hurt `quiet` at all.** With `ByUser`, shuffle sharding gives them different queues, and `quiet`'s latency drops sharply even while `noisy` keeps flooding. Without it, they share one queue and one client's backlog is everyone's backlog.
- **Concurrency shares decide the level's total capacity**, not its fairness. Raising them helps both clients and protects neither from the other.

Getting those two the wrong way round is the mistake the talk describes, so state them separately.

**Write down** — the three measurements from step 6 as numbers, the two configuration answers, the `429` response body and header, and the exemption note from the setup — including one sentence on what would have happened if your admin identity had not been exempt.

**Teardown** — kill the flood (again — check `jobs`), delete the load namespace, the two ServiceAccounts and their RBAC, and revert any FlowSchema or priority-level edit. Confirm `apiserver_flowcontrol_current_inqueue_requests` is back to zero across all levels before moving on. **The topology stays.**
