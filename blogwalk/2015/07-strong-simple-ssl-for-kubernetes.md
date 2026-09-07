<a id="strong-simple-ssl-for-kubernetes"></a>
# Every line of this post still runs, and the sentence it quotes to justify itself is gone

**Post** — [Strong, Simple SSL for Kubernetes Services](https://kubernetes.io/blog/2015/07/strong-simple-ssl-for-kubernetes/),
2015-07-14, Kubernetes pre-1.0 — eight days before 1.0.

**As written** — a Google Cloud solutions architect has Jenkins running in a pod behind a
`type: LoadBalancer` service, on the public internet, with no authentication and no encryption,
and observes that "since there's no encryption, configuring authentication is kind of a symbolic
gesture." Rather than learn how Jenkins does TLS, he puts nginx in front of it — "Kubernetes is
all about building functionality by orchestrating and composing containers" — and gets
HTTP→HTTPS redirection and basic auth for free.

The proxy is a **separate pod behind its own service**, not a container inside the Jenkins pod. It
finds its backend through the service environment variables:

```
        env:
          -
            name: "SERVICE_HOST_ENV_NAME"
            value: "JENKINS_SERVICE_HOST"
          -
            name: "SERVICE_PORT_ENV_NAME"
            value: "JENKINS_SERVICE_PORT_UI"
```

— the indirection being that the image is generic, and you tell it *which* env vars to read. Its
own service is `type: LoadBalancer` on 80 and 443 with named `targetPort`s, and Jenkins's service
stops being public.

Then the key material, under the heading "Keep it secret, keep it safe". The post links
`GoogleCloudPlatform/kubernetes/blob/master/docs/secrets.md` and quotes it: secrets "are intended
to hold sensitive information, such as passwords, OAuth tokens, and ssh keys. Putting this
information in a secret is safer and more flexible than putting it verbatim in a pod definition or
in a docker image." Three steps: `cat ssl.key | base64`, paste the output into a `Secret` with
`data.proxycert` / `data.proxykey` / `data.htpasswd`, `kubectl create -f secrets.json`. Then a
`secret` volume mounted at `/etc/secrets`, `readOnly: true`, and the three files appear
base64-decoded for nginx to read.

Idea to working: "about 2 hours."

**As it runs now** — this is the rarest kind of post in 2015. Run down the mechanics:

- `apiVersion: "v1"`, `kind: "Secret"`, `data:` with base64 values — current.
- `ReplicationController` — still a core/v1 resource with a live reference page and a concept page
  that recommends using one "even if your application requires only a single pod". Nobody writes
  them; nothing removed them.
- Named `containerPort`s referenced by name from `targetPort` — current.
- `volumes: [{secret: {secretName: ...}}]` mounted at a path, files appearing decoded — current.
- The service environment variables. `JENKINS_SERVICE_HOST` and `JENKINS_SERVICE_PORT_UI` are
  still injected into every container in the namespace, from a service named `jenkins` with a port
  named `ui`. Injection is on unless you set `enableServiceLinks: false` on the pod.

So the post's stack is not broken. Four things around it changed instead:

1. **The link is dead and the quote is gone.** `GoogleCloudPlatform/kubernetes` is the pre-rename
   org, and per-repo `docs/` was moved to the website years ago. More interesting: the sentence
   the post quotes to justify putting a private key in a Secret — "safer and more flexible than
   putting it verbatim in a pod definition or in a docker image" — does not appear anywhere in the
   docs at the pin. What sits at the top of the Secret page instead is a caution: Secrets "are, by
   default, stored unencrypted in the API server's underlying data store (etcd). Anyone with API
   access can retrieve or modify a Secret, and so can anyone with access to etcd. Additionally,
   anyone who is authorized to create a Pod in a namespace can use that access to read any Secret
   in that namespace; this includes indirect access such as the ability to create a Deployment."
   The post's central security move is the thing the current page hedges hardest.
2. **The Secret grew a type, and stopped requiring you to base64 things by hand.**
   `kubernetes.io/tls` requires the keys `tls.crt` and `tls.key`, and the API server verifies they
   are set — "although the API server doesn't actually validate the values". `kubectl create
   secret tls` builds it from PEM files. `stringData` takes plaintext and encodes for you. None of
   those existed when the post was written, which is why step 1 is a `base64` pipeline.
3. **The front door has a name now, and the post's front door does not work in a lab.**
   `type: LoadBalancer` provisions anything only "on cloud providers which support external load
   balancers". The generic-HTTP-reverse-proxy-in-front-of-a-service pattern this post hand-rolls
   became Ingress, whose canonical TLS configuration is precisely a `kubernetes.io/tls` Secret.
4. **At the pin's own newest release, the private key stopped needing to be a Secret at all.** A
   `podCertificate` projected volume source hands a pod a private key and an X.509 chain that the
   *kubelet* requests and rotates — "Kubelet will then handle refreshing the private key and
   certificate chain when they get close to expiration." You pick a `signerName`, a `keyType`, and
   a `maxExpirationSeconds`; the credential bundle is written into the pod as PEM. Nothing is
   stored in etcd for anyone with API access to read.

**The diff, and why** — the post is **still right**, and the sweep's usual question — what broke —
gets no purchase on it. The interesting question is the other one: why does a post whose every
command still works read as bad advice?

Because the post is proud of the wrong thing. Its thesis is composition: don't learn Jenkins's
TLS, compose a proxy container instead, two hours, done. Kubernetes agreed with that thesis so
thoroughly that it absorbed it. Terminating TLS in front of a service is not a thing you assemble
from a `ReplicationController`, an env-var indirection convention and a `:latest` tag in someone
else's registry; it is a resource type. The composition happened once, upstream, and the reader
gets to write eight lines instead of four files.

The other half of the diff is about the key, and it is a genuine reversal rather than an
absorption. In 2015, "put it in a Secret" *was* the security advice, and the post is quoting the
official documentation saying so. The advice was not wrong; it was under-qualified, and the
qualifications took eleven years to arrive in the form of encryption at rest, RBAC on Secrets,
external store providers, and finally credentials the API server never holds. The post cannot be
faulted for the sentence it quoted. The sentence is what expired.

Watch the direction of that pressure, because it is the same one behind
[CRI](03-docker-and-kubernetes-and-appc.md) and [logging](04-cluster-level-logging-with-kubernetes.md)
from the other side: those two moved responsibility *out* of Kubernetes, toward a contract with an
implementation the project does not own. This one moves it *in* — the kubelet now generates the
private key. The consistent rule is not "less code" or "more code"; it is that the project keeps
whatever it can specify completely and delegates whatever it cannot.

Release facts and the pressure behind each are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

**The ladder** — three gates carry the v1.37 answer to this post, and the transcription is per
gate:

`PodCertificateRequest`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.34 – v1.34 |
| beta | `false` | — | v1.35 – v1.36 |
| stable | `true` | — | v1.37 – |

`ClusterTrustBundle`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.27 – v1.32 |
| beta | `false` | — | v1.33 – v1.36 |
| stable | `true` | — | v1.37 – |

`ClusterTrustBundleProjection`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.29 – v1.32 |
| beta | `false` | — | v1.33 – v1.36 |
| stable | `true` | — | v1.37 – |

None of the three declares `removed` or `former_titles`. Note that all three are `stable` /
`true` only in the pin's newest release, and that beta was `false` throughout — a beta you had to
ask for. And note a disagreement you will meet in step 8: at this same commit, the generated
`--feature-gates` help text in the kubelet reference lists all three as `BETA - default=false`,
and the API reference pages are `pod-certificate-request-v1beta1` and `cluster-trust-bundle-v1beta1`.
Two of the three sources say beta. The gate files say stable. Believe your cluster over all of
them, which is what step 8 is for.

**No gate** — the Secret half of this exercise is not gated at all, in either direction: there is
no gate for `kubernetes.io/tls`, for `stringData`, or for secret volumes, and none was removed to
make room for the certificate work. The instrument for those claims is the API server itself —
`kubectl explain secret.stringData` and a server-side dry run, used in steps 3 and 4 — not a
feature-gate table.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo) — the guest from
[the checkpoint exercise](06-how-did-quake-demo-from-dockercon-work.md) is still up; keep it. If
you are starting here, bring it up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, then `ssh zain@10.10.10.180`.

**Do**

1. Build the post's backend and its service, with the exact names its env-var indirection depends
   on:

   ```sh
   kubectl create deployment jenkins --image=nginx:alpine
   kubectl expose deployment jenkins --name=jenkins --port=8080 --target-port=80
   kubectl patch svc jenkins --type=json \
     -p='[{"op":"replace","path":"/spec/ports/0/name","value":"ui"}]'
   ```

2. Prove the indirection the post is built on still holds, from inside a container the post never
   wrote:

   ```sh
   kubectl run probe --image=busybox --restart=Never --rm -it -- env | grep JENKINS
   ```

3. Now make key material and follow the post's step 1 literally. Do not skip the `wc`:

   ```sh
   openssl req -x509 -newkey rsa:2048 -nodes -days 1 \
     -keyout tls.key -out tls.crt -subj '/CN=jenkins.default.svc'
   cat tls.key | base64 | wc -l
   cat tls.key | base64 | head -2
   ```

   Write down what pasting that output into a JSON string, as the post instructs, would produce.
   Then find the field that made the pipeline unnecessary:

   ```sh
   kubectl explain secret.stringData
   ```

4. Create it both ways and compare what the API server made of each:

   ```sh
   kubectl create secret generic ssl-proxy-secret \
     --from-file=proxycert=tls.crt --from-file=proxykey=tls.key
   kubectl create secret tls ssl-proxy-tls --cert=tls.crt --key=tls.key
   kubectl get secret ssl-proxy-secret ssl-proxy-tls \
     -o custom-columns=NAME:.metadata.name,TYPE:.type,KEYS:.data
   kubectl create secret tls broken --cert=tls.crt --key=tls.crt --dry-run=server -o name
   ```

5. Mount it the post's way and read the decoded files:

   ```sh
   kubectl run proxy --image=nginx:alpine --restart=Never --overrides='
   {"spec":{"containers":[{"name":"proxy","image":"nginx:alpine",
     "volumeMounts":[{"name":"secrets","mountPath":"/etc/secrets","readOnly":true}]}],
    "volumes":[{"name":"secrets","secret":{"secretName":"ssl-proxy-secret"}}]}}'
   kubectl wait --for=condition=Ready pod/proxy --timeout=60s
   kubectl exec proxy -- head -1 /etc/secrets/proxykey
   kubectl exec proxy -- sh -c 'touch /etc/secrets/x' ; echo "exit=$?"
   ```

6. Test the caution's sharpest clause — "anyone who is authorized to create a Pod in a namespace
   can use that access to read any Secret in that namespace" — and then the other one, that the
   store is unencrypted:

   ```sh
   kubectl auth can-i get secrets
   kubectl auth can-i create pods
   E=$(kubectl -n kube-system get pod -l component=etcd -o name | head -1)
   kubectl -n kube-system exec $E -- sh -c \
     'ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
        --cacert=/etc/kubernetes/pki/etcd/ca.crt \
        --cert=/etc/kubernetes/pki/etcd/server.crt \
        --key=/etc/kubernetes/pki/etcd/server.key \
        get /registry/secrets/default/ssl-proxy-secret' | strings | grep -c 'PRIVATE KEY'
   ```

7. Try the post's front door:

   ```sh
   kubectl expose pod proxy --name=nginx-ssl-proxy --port=443 --type=LoadBalancer
   kubectl get svc nginx-ssl-proxy
   ```

   Wait as long as you like. Then find the resource that replaced it:
   `kubectl api-resources | grep -i -E 'ingress|gateway'`.

8. Ask your cluster which of the three sources in *The ladder* is telling the truth:

   ```sh
   kubectl api-resources | grep -i -E 'podcertificate|clustertrustbundle'
   kubectl explain pod.spec.volumes.projected.sources.podCertificate 2>&1 | head -14
   kubectl get --raw /metrics | grep -o 'kubernetes_feature_enabled{name="PodCertificateRequest"[^}]*}' \
     | head -1
   ```

   Record which API groups your server actually serves and at which version, and compare that
   against the gate table, the kubelet's `--feature-gates` help, and the API reference page names.

**Expect** — step 2 prints `JENKINS_SERVICE_HOST`, `JENKINS_SERVICE_PORT`, `JENKINS_PORT_8080_TCP_*`
and — because you renamed the port — `JENKINS_SERVICE_PORT_UI`. The post's whole configuration
mechanism, unchanged, in a cluster eleven years newer.

Step 3: `base64` from GNU coreutils wraps at 76 columns, so `wc -l` reports around 23. The post
says `cat ssl.key | base64` and then "add the base64-encoded values" to a JSON document, and does
not mention `-w 0`. Twenty-three lines is not a JSON string. `kubectl explain secret.stringData`
describes the field that removed the whole problem — "Write-only convenience", merged into `data`
on write.

Step 4: the generic Secret is type `Opaque` with keys `proxycert` and `proxykey`; the TLS one is
`kubernetes.io/tls` with `tls.crt` and `tls.key`. The `broken` dry run is rejected server-side —
the cert and key do not match — which is the API server enforcing something about your key
material that no gate governs and that the post's `Opaque` Secret cannot express.

Step 5: `head -1` prints `-----BEGIN PRIVATE KEY-----`, decoded, exactly as the post promises. The
`touch` fails read-only; secret volumes are mounted read-only whether or not you say so, which
makes the post's `readOnly: true` a comment.

Step 6: both `can-i` checks return `yes` for a cluster-admin kubeconfig, and the point is that the
second one alone would have been enough — step 5 read the key through a pod, not through
`get secrets`. The `grep -c` prints a non-zero count: your private key is sitting in etcd in the
clear, and the only thing between it and a reader is filesystem access to a node you just used
`exec` to reach. That is the sentence the Secret page leads with and the post's quoted sentence
did not contain.

Step 7: `EXTERNAL-IP` reads `<pending>`, permanently. There is no cloud controller manager on this
guest, so nothing is listening for the request. `api-resources` shows `ingresses` and
`ingressclasses` in `networking.k8s.io/v1` — and no Gateway API, which is out-of-tree CRDs you
would have to install. The post's front door needs a bill from a cloud provider; its replacement
needs a controller you choose.

Step 8 is the only instrument that outranks all four written sources, because it asks the running
server. On a v1.37 cluster you should find `podcertificaterequests` and `clustertrustbundles`
served, and `explain` should describe `signerName`, `keyType` and `credentialBundlePath`. The
`/metrics` line either prints a `kubernetes_feature_enabled` sample naming the gate and its stage
or prints nothing — the metric exists only where a component still tracks the gate, so silence
here is itself the answer a stable, unconditionally-enabled feature gives. If `explain` returns
nothing, your server is older than the pin or your distribution disabled the gates, and you have
reproduced from the other direction the same disagreement the reference pages carry.

**Read on** — the [all-in-one volume design
proposal](https://git.k8s.io/design-proposals-archive/node/all-in-one-volume.md), which the pin's
projected-volumes page still cites as the origin of the mechanism. Read what it set out to
combine, then ask what it assumed about where a projected file's *contents* come from — and why a
source the kubelet fills by requesting a fresh, expiring credential from the API server fits that
design without changing it.

**Teardown** — `kubectl delete pod proxy; kubectl delete deployment jenkins;
kubectl delete svc jenkins nginx-ssl-proxy; kubectl delete secret ssl-proxy-secret ssl-proxy-tls broken`,
then `rm -f tls.key tls.crt` — you generated a real private key on the guest and wrote it into
etcd; do not leave either copy behind. Leave the guest up; the next exercise in this year
reuses it.
