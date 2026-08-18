<a id="the-webhook-behind-a-service"></a>
# Stage 2: what `clientConfig.service` actually costs

**Artifact** — the same webhook, unchanged in its logic, now running as a Deployment in `academy-build`, reached through a Service, with a certificate whose SANs are Kubernetes DNS names, registered with `clientConfig.service` instead of `clientConfig.url`. Everything added here is the cost of the swap, and the point is to have paid it deliberately once.

**Rests on** — [stage 1](18-the-webhook-the-apiserver-dials.md), and the edit-run cycle time you recorded there. You are about to destroy that number.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [the comparison](20-the-same-rejection-twice.md).

**Build**

Nothing in `admit.go` changes. What is added:

1. **A second certificate**, because the name changed. The apiserver will dial `academy-webhook.academy-build.svc`, so that is what the SAN must say — and the short forms are not optional if anything else ever dials it:

   ```sh
   cd ~/webhook-pki
   cat > svc-san.cnf <<'CNF'
   [req]
   distinguished_name = dn
   [dn]
   [v3]
   subjectAltName = @alt
   basicConstraints = CA:FALSE
   keyUsage = digitalSignature, keyEncipherment
   extendedKeyUsage = serverAuth
   [alt]
   DNS.1 = academy-webhook.academy-build.svc
   DNS.2 = academy-webhook.academy-build.svc.cluster.local
   DNS.3 = academy-webhook.academy-build
   CNF
   openssl genrsa -out svc-tls.key 2048
   openssl req -new -key svc-tls.key -subj "/CN=academy-webhook.academy-build.svc" -out svc-tls.csr
   openssl x509 -req -in svc-tls.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
     -days 90 -sha256 -extfile svc-san.cnf -extensions v3 -out svc-tls.crt
   ```

   The CA is the same, so **`caBundle` does not change.** That is worth noticing: the thing that felt like the hard part in stage 1 is the part that survives the swap untouched.

2. **A container image.** [`scratch`, per the strand](../../strands/build-mechanics.md#base-image):

   ```dockerfile
   FROM scratch
   COPY validating-webhook /validating-webhook
   ENTRYPOINT ["/validating-webhook"]
   ```

   ```sh
   CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o validating-webhook .
   docker buildx build --platform linux/amd64 -t forge.lab:5000/validating-webhook:v1 --push .
   ```

3. **An identity.** [Namespace `academy-build`, one ServiceAccount, one hand-written ClusterRole](../../strands/build-mechanics.md#identity). Write the ClusterRole before you write the Deployment, and write it from first principles: list every API call the binary makes. *(Read `admit.go` again if you need to. The answer is more interesting than it looks.)*

4. **A Deployment**, one replica, mounting the cert and key from a Secret, with [a memory request and a written-down limit decision](../../strands/build-mechanics.md#sizing) taken from `kubectl top pod` during stage 1 — not guessed.

5. **A Service** on port 443 targeting 8443.

6. **The registration change**, and only this:

   ```yaml
   clientConfig:
     service:
       name: academy-webhook
       namespace: academy-build
       path: /validate-pods
       port: 443
     caBundle: <unchanged>
   ```

**Verify from outside** — the webhook must reject and admit exactly as it did in stage 1, with the `go run` process on `forge` **stopped**, so there is no possibility of the old path still serving:

```sh
pkill -f 'go run .'
kubectl -n tenant run nolimit --image=busybox --restart=Never
kubectl -n tenant run withlimit --image=busybox --restart=Never \
  --overrides='{"spec":{"containers":[{"name":"withlimit","image":"busybox","resources":{"limits":{"memory":"32Mi"}}}]}}'
kubectl -n academy-build logs deploy/academy-webhook | tail
kubectl auth can-i --list --as=system:serviceaccount:academy-build:academy-webhook
```

**Expect** — identical admission behaviour and a completely different operational shape. Specifically:

- **The ClusterRole is empty, and that is the right answer.** The webhook makes no API calls: the apiserver calls *it*, carrying the object in the request body. `auth can-i --list` should show only the discovery and self-review rules every authenticated identity has. A webhook that needs a ClusterRole is a webhook that decided to go and look something up, and that is a design choice with an availability cost, not a default.
- **`kubectl exec` into the pod fails** with `exec: "sh": not found`, because the image is `scratch`. The way in is `kubectl debug -it <pod> --image=busybox --target=academy-webhook`, and doing it once here is worth more than reading about ephemeral containers later.
- **The edit-run cycle is now build → push → rollout → wait.** Time it and put it next to stage 1's number.

The failure you should expect at least once: `no endpoints available for service "academy-webhook"`. The apiserver resolved the Service, found no ready endpoint, and reported it clearly — a *fifth* distinct failure string for [the running list](04-mis-sign-a-client-cert.md), and the one that will not appear in any `url`-mode deployment.

The second-most-likely failure is the port. `service.port` is the Service's port, not the container's; getting them crossed produces a connection refused that looks like the pod is broken when the pod is fine.

**Scope discipline** — no leader election, no HA, no PodDisruptionBudget. One replica is correct here and its consequences are [the chaos drill's](26-3c1-corrupt-a-cabundle.md) subject.

**Write down** — the two cycle times, the empty-ClusterRole finding with the sentence explaining it, the memory limit decision and its reason, and **the list of objects that had to exist for `clientConfig.service` to work**. That list is the answer to *what the swap costs*, and it is the thing [the strand's two-stage argument](../../strands/build-mechanics.md#two-stages) says you should be able to produce from having done it.

**Footprint note** — the Deployment is one small Go process; the image is ~12MB and the pod's working set is the [564 MiB shape's](../../strands/build-mechanics.md#measurements) runtime, not its build peak. It does not move the arithmetic: `pair` 5.0GB + `forge` 2560MB = 7.5GB, unchanged. The registry container on `forge` is already counted in `forge`'s allocation.

**Teardown** — delete the pods. **Keep everything else** — the Deployment, Service, Secret, image and webhook configuration are the platform [the mutating webhook](22-the-mutating-webhook-cert-manager-signs.md), [the reinvocation demonstration](23-reinvocation-observed.md), [the match conditions](24-matchconditions-stop-the-call.md) and [the chaos drill](26-3c1-corrupt-a-cabundle.md) all build on. **The topology stays.**
