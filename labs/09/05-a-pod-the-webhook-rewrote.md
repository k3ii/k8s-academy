<a id="a-pod-the-webhook-rewrote"></a>
# The same Deployment, two containers: find the object that rewrote the pod and the template it rewrote it from

**Claim** — the Deployment you applied has **one container in its template and still has one** after injection, while every pod it creates has **two containers and an init container**. The rewriting object is a `MutatingWebhookConfiguration` calling `istiod` at pod-admission time, and the sidecar it inserts is rendered from a template stored in a ConfigMap you can read.

**Rests on** — [the installed control plane](04-the-request-that-does-not-fit.md). This exercise creates the two workloads the rest of the phase uses.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Setup** — bring the two sample workloads over from `forge`, where [exercise 1](01-four-objects-in-a-file-you-typed.md) unpacked the release, and create the namespace **without** injection first, so that the before-state is a real observation rather than a memory:

```sh
scp zain@10.10.10.125:~/istio-*/samples/httpbin/httpbin.yaml \
    zain@10.10.10.125:~/istio-*/samples/sleep/sleep.yaml zain@10.10.10.130:~/
kubectl create namespace mesh
kubectl -n mesh apply -f httpbin.yaml -f sleep.yaml
kubectl -n mesh get pods
```

**Do — part 1, the before and after.** One label, one restart, and nothing else changes:

```sh
kubectl -n mesh get pod -l app=httpbin -o jsonpath='{.items[0].spec.containers[*].name}'; echo
kubectl label namespace mesh istio-injection=enabled
kubectl -n mesh rollout restart deploy httpbin sleep
kubectl -n mesh rollout status deploy httpbin
kubectl -n mesh get pods
kubectl -n mesh get pod -l app=httpbin \
  -o jsonpath='{.items[0].spec.initContainers[*].name}{"\n"}{.items[0].spec.containers[*].name}'; echo
```

**Do — part 2, prove the Deployment is innocent.** The thing that changed is not the thing you applied:

```sh
kubectl -n mesh get deploy httpbin -o jsonpath='{.spec.template.spec.containers[*].name}'; echo
diff <(kubectl -n mesh get deploy httpbin -o json | jq -S '.spec.template.spec') \
     <(kubectl -n mesh get pod -l app=httpbin -o json | jq -S '.items[0].spec') | head -40
```

**Observe — the object that did it, and what selects you into its reach:**

```sh
kubectl get mutatingwebhookconfiguration | grep istio
kubectl get mutatingwebhookconfiguration istio-sidecar-injector -o json \
  | jq '.webhooks[] | {name, failurePolicy, sideEffects, namespaceSelector, objectSelector,
                       rules: .rules, path: .clientConfig.service.path, svc: .clientConfig.service}'
kubectl -n mesh get pod -l app=httpbin -o json \
  | jq -r '.items[0].metadata.annotations["sidecar.istio.io/status"]' | jq .
```

**Read** — the template the webhook renders, which is configuration rather than code:

```sh
kubectl -n istio-system get cm istio-sidecar-injector -o jsonpath='{.data.config}' | head -60
```

| Read | Answer from it |
|---|---|
| The `config` key of `cm/istio-sidecar-injector` | Which Go template block emits `istio-init`, and which emits `istio-proxy`. |
| The `istio-init` block's `securityContext` | Which two capabilities it adds, and why a container that only writes `iptables` rules needs both. |
| The `istio-proxy` block's `securityContext` | The numeric `runAsUser`, and the one place that number appears again — [the rule that keeps Envoy's own traffic out of its own listener](07-the-uid-that-breaks-the-loop.md). |
| `.webhooks[].rules` on the webhook object | Which resource and which verb the webhook intercepts. Not `deployments`, and that is the whole of part 2's result. |

**Expect** — one container before, and after the restart an `istio-init` init container plus `istio-proxy` beside `httpbin`, with **`2/2` in `kubectl get pods`**. Expect the Deployment's template to still list exactly one container, and the `diff` to show the injected containers, an `istio-proxy` volume set (`istio-envoy`, `istio-data`, `istio-podinfo`, `istio-token`, `istiod-ca-cert`) and a `securityContext` present in the pod and absent from the template. **Mutation happens on `CREATE pods`, not on the Deployment**, which is why `kubectl get deploy -o yaml` will never show you a sidecar and why deleting a pod is enough to re-run the injector.

Expect `istio-init` to carry **`NET_ADMIN` and `NET_RAW`** and `istio-proxy` to run as **UID 1337**. Expect the `sidecar.istio.io/status` annotation to be a machine-readable inventory of exactly what was added — the honest audit trail for a mutation you did not write, and the first thing to read when an injected pod looks wrong.

Expect the webhook's **`failurePolicy: Fail`** to be a prediction about a later exercise: if the endpoint behind `clientConfig.service` is unreachable, pod creation in this namespace does not silently skip injection, it **fails**. Do not test that here — [the exercise that kills `istiod`](14-9c3-istiod-killed-and-the-planes-come-apart.md) tests it deliberately, and predicting it now is what makes that result mean something.

**Write down** — the webhook's name, its `namespaceSelector`, the resource/verb from `.rules`, and the two container names it added, in `journal/p9-injection.md`. One sentence on why the Deployment being unchanged is the *correct* design and not a leak: the mesh is a property of pods, and a template that carried a sidecar would carry a version of it that ages.

**Footprint note** — two workloads, two sidecars. A sidecar Envoy idles around **60Mi**, so this is roughly **200Mi on the worker's 1948Mi**, and it is the whole of the phase's workload — no third application arrives. [Why `httpbin` and `sleep` rather than the sample everyone uses](04-the-request-that-does-not-fit.md) is costed in the previous exercise.

**Teardown** — nothing to remove. Delete any scratch pod you created while comparing, and confirm the pair you meant to keep is what is running:

```sh
kubectl -n mesh get pods
```

**The `mesh` namespace and both workloads stay** — every exercise from [the netfilter reading](06-interception-reduced-to-netfilter.md) to [the ambient switch](20-a-namespace-with-no-sidecars.md) uses them. **The topology stays.**
