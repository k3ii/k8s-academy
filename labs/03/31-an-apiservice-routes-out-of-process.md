<a id="an-apiservice-routes-out-of-process"></a>
# A URL path served by a process that is not the apiserver

**Artifact** — an `APIService` registering a group your own Pod serves, with `kubectl get` against it succeeding — and a written comparison of the three ways `academy.k3ii.dev` and your aggregated group differ, none of which is visible to the client.

**Rests on** — [the CRD's runtime storage](30-how-a-crd-gets-its-storage.md), which is the alternative this is being compared against, and [the serving certificate](17-a-ca-and-a-serving-cert-by-hand.md) — the aggregator's trust of an extension apiserver is the same problem with a different `caBundle` field.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. Do **not** build a new binary for this. Reuse the conversion webhook's Deployment shape and serve a minimal API surface from a fourth route on it — the aggregation contract is small enough to satisfy by hand:
   - `GET /apis/toy.k3ii.dev/v1` returning an `APIResourceList` naming one resource, `pings`;
   - `GET /apis/toy.k3ii.dev/v1/pings` returning a `PingList` with two hard-coded items;
   - `GET /apis/toy.k3ii.dev/v1/pings/{name}` returning one.

   Hard-coded is the right answer here: the subject is routing, not storage, and a fake backend makes it unambiguous which process answered.

2. Register it:

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: apiregistration.k8s.io/v1
   kind: APIService
   metadata: {name: v1.toy.k3ii.dev}
   spec:
     group: toy.k3ii.dev
     version: v1
     groupPriorityMinimum: 1000
     versionPriority: 15
     service: {name: academy-converter, namespace: academy-build, port: 443}
     caBundle: PLACEHOLDER
   YAML
   ```

   Take the `caBundle` from the same `cert-manager` Secret the conversion webhook uses, or use the injection annotation. If you use the annotation, check afterwards that it was actually injected rather than assuming it — this is a different resource kind from the one you annotated in [the mutating webhook exercise](22-the-mutating-webhook-cert-manager-signs.md).

3. Watch it be accepted, then watch it be *believed*:

   ```sh
   kubectl get apiservice v1.toy.k3ii.dev -o jsonpath='{.status.conditions}' | jq
   kubectl api-resources --api-group=toy.k3ii.dev
   kubectl get pings
   kubectl get --raw /apis/toy.k3ii.dev/v1/pings | jq
   ```

4. Break the availability probe without touching your code: scale the Deployment to zero. Then run `kubectl api-resources` with no group filter and read the whole output, not just the part about your group.

5. Scale back up and find how long recovery takes.

**Observe**

```sh
kubectl get apiservice                                   # the full set, yours among them
kubectl -n academy-build logs deploy/academy-converter | grep toy.k3ii.dev
kubectl get --raw /apis | jq -r '.groups[].name'
```

**Expect** — `kubectl get pings` works and your Pod's log shows the request, arriving from the apiserver rather than from your workstation. The client cannot tell it left the process.

Step 4 is the exercise. A single unavailable `APIService` makes `kubectl api-resources` emit an error line for the whole call and exit non-zero, and anything that enumerates resources — `kubectl get all`, a controller building a RESTMapper, `helm` — degrades with it. **One broken extension API is a cluster-wide discovery fault**, and meeting that here is why the exercise exists. Note also which `APIService` the aggregator reports as unavailable versus which requests actually fail.

Recovery in step 5 is not instant; find the interval rather than guessing it, and note that `status.conditions` lags the actual recovery.

The three differences to write up: **who stores the objects**, **who is on the path of the request** (and therefore whose outage it is), and **what a client's discovery does when it is broken**. A CRD cannot produce step 4's failure mode; that is the trade.

**Write down** — the three differences, the exact `kubectl api-resources` failure output from step 4, and the recovery interval you measured.

**Footprint note** — no new Pod: four routes on an existing Deployment. This is deliberate — a real extension apiserver is a substantial process, and [the phase's ceiling](../../strands/lab-topologies.md#ceiling) does not have room for one alongside three webhooks and `cert-manager`. **What is skipped by faking it**: `k8s.io/apiserver`'s own delegated authentication and authorization wiring, which is where a real extension apiserver spends its complexity. Note that as skipped rather than covered — it is the honest cost of this substitution.

**Teardown** — delete the `APIService` **first**, then anything else. Deleting the Deployment while the `APIService` still points at it leaves discovery broken for as long as it takes you to notice. **Keep the CRD and the webhooks.** **The topology stays** — [the drill](32-3c2-garbage-from-the-conversion-webhook.md) is next.
