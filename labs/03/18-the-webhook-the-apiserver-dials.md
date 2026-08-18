<a id="the-webhook-the-apiserver-dials"></a>
# Stage 1: the apiserver calls a process you are still editing

**Artifact** — the phase's first build-track artifact: a validating admission webhook in `build/03-validating-webhook/`, running as `go run` on [`forge`](../../strands/lab-topologies.md#build-guest), registered with `clientConfig.url` so a real cluster's apiserver dials it over the lab bridge. Admission is live while the code is still being edited. [The strand's argument for why](../../strands/build-mechanics.md#two-stages) is not repeated here; this is the how.

**Rests on** — [the CA and serving cert](17-a-ca-and-a-serving-cert-by-hand.md), whose SANs were chosen for exactly this, and [the policy](16-a-policy-with-no-webhook.md), whose rule this webhook deliberately duplicates so [the two can be compared](20-the-same-rejection-twice.md).

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), **freshly provisioned — this is the phase's first cluster.** The provisioning commands are [in the strand](../../strands/lab-topologies.md#provision) and are not repeated here; `ssh hopper` is mandatory and `just gate` is not optional. Note also [what does not exist yet](../../strands/lab-topologies.md#contract) — that note applies to every exercise in this directory from here on and is stated there once.

`pair` runs every exercise up to and including [the expired credential](41-3c5-an-expired-component-certificate.md).

**Setup**

The cluster must be able to resolve and reach `forge.lab`. Check both, from the control-plane node, before writing any Go:

```sh
ssh zain@10.10.10.130
getent hosts forge.lab || echo '10.10.10.125 forge.lab forge' | sudo tee -a /etc/hosts
nc -vz 10.10.10.125 8443     # expected to fail: nothing is listening yet
```

**Build**

```
build/03-validating-webhook/
  go.mod
  main.go          flag parsing, TLS server, one route
  admit.go         the review decode/encode, and the decision
  admit_test.go    table test over AdmissionReview fixtures
```

What it must implement, as an interface rather than an implementation:

1. **An HTTPS server** on `:8443`, serving `~/webhook-pki/tls.crt` and `tls.key`, with **one** route — `/validate-pods`. Later exercises add routes to this same binary; leave room for them.
2. **A handler** that decodes an `admissionregistration`-shaped request body into an `admission/v1.AdmissionReview`, and responds with an `AdmissionReview` whose `response.uid` **echoes the request's `request.uid`**. Getting that echo wrong is the single most common webhook bug and it produces a timeout rather than an error.
3. **The decision, deliberately identical to [the policy's](16-a-policy-with-no-webhook.md)**: allow only if every container has `resources.limits.memory`. Deny with a message naming the offending container. The rule is a duplicate on purpose — the artifact being built here is the plumbing, and holding the semantics fixed is what makes [the comparison](20-the-same-rejection-twice.md) mean anything.
4. **A request counter**, logged per call: path, namespace, object name, and the decision. [Two](24-matchconditions-stop-the-call.md) [later](23-reinvocation-observed.md) exercises read nothing but this log.
5. **A `--fail-open` flag** defaulting to false, which if set returns `allowed: true` on any internal error. You will not use it here; [the chaos drill](26-3c1-corrupt-a-cabundle.md) is where its absence is felt.

Run it on `forge`, in the foreground, and keep the terminal:

```sh
cd ~/k8s-academy/build/03-validating-webhook
go run . --tls-cert ~/webhook-pki/tls.crt --tls-key ~/webhook-pki/tls.key --addr :8443
```

Register it from the cluster, with `url` and no Service anywhere:

```sh
kubectl apply -f - <<YAML
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata: {name: academy-memlimit}
webhooks:
  - name: memlimit.academy.local
    admissionReviewVersions: ["v1"]
    sideEffects: None
    failurePolicy: Fail
    clientConfig:
      url: https://forge.lab:8443/validate-pods
      caBundle: $(cat ~/webhook-pki/ca.b64)
    rules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["pods"]
        scope: "Namespaced"
    namespaceSelector:
      matchLabels: {academy: "yes"}
YAML
kubectl create namespace tenant
kubectl label namespace tenant academy=yes
```

**Gate** — [tier 2, a falsifiable written claim](../../strands/build-mechanics.md#gates); there is no harness for a webhook and inventing one is not the standard. The claim to write: **"an `AdmissionReview` response is matched to its request by `response.uid`, and a mismatched uid is treated as ⟨X⟩ rather than an error"** — completed and cited to a `file:function` under `staging/src/k8s.io/apiserver/pkg/admission/plugin/webhook/`. Test the claim by deliberately returning a wrong uid once and watching what the apiserver does with it.

Plus the objective half, which is not the gate but is the reason to keep going:

```sh
kubectl -n tenant run nolimit --image=busybox --restart=Never
kubectl -n tenant run withlimit --image=busybox --restart=Never \
  --overrides='{"spec":{"containers":[{"name":"withlimit","image":"busybox","resources":{"limits":{"memory":"32Mi"}}}]}}'
kubectl -n default run elsewhere --image=busybox --restart=Never
```

**Expect** — `nolimit` is refused with your message, prefixed by `admission webhook "memlimit.academy.local" denied the request`. `withlimit` is created. `elsewhere` is created **without your webhook being called at all** — the `namespaceSelector` kept it out, and your log proves it. That third case is the one worth deliberately checking: a webhook that is not called and a webhook that allows are indistinguishable from the client and completely different in an outage.

**The apiserver is not lying about the network.** If the log on `forge` is silent while `kubectl` reports a webhook error, read the error text: `context deadline exceeded` means it dialled and got nothing, `no such host` means DNS on the control-plane node, and `x509` means the `caBundle` and the serving cert disagree — three failures with three fixes and no overlap between them.

The uid-echo bug from the build spec presents as `context deadline exceeded` even though your process replied instantly, which is why it is worth causing on purpose once.

**Scope discipline** — do not add a Service, a Deployment or an image to this exercise. Stage 1 exists to be edited; every one of those is [stage 2's cost](21-the-webhook-behind-a-service.md) and paying it now removes the thing being taught.

**Write down** — the three results, the uid claim with its citation, and **the edit-run cycle time** — how long from saving `admit.go` to a changed decision landing on the cluster. That number is the whole argument for stage 1, and it is the number [stage 2 destroys](21-the-webhook-behind-a-service.md).

**Footprint note** — [`pair`](../../strands/lab-topologies.md#pair) at 5.0GB plus `forge` at 2560MB is 7.5GB against [the 9.5GB ceiling](../../strands/lab-topologies.md#ceiling), a 2.0GB margin. `go run` re-links on every save, and this artifact is [the 564 MiB shape](../../strands/build-mechanics.md#measurements), not the apiserver — the margin is comfortable and stays comfortable until [`cert-manager` arrives](22-the-mutating-webhook-cert-manager-signs.md).

**Teardown** — leave the webhook configuration, the namespace and the `go run` process up: [the SAN break](19-change-one-san.md) needs all three, working, before it breaks one of them. Delete the three pods. **The topology stays** — `pair` is now the phase's cluster.
