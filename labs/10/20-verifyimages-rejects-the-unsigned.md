<a id="verifyimages-rejects-the-unsigned"></a>
# An admission rule that lets your signed image in and turns an unsigned one away

**Claim** — a Kyverno `verifyImages` policy, given the OIDC identity and issuer from [exercise 19](19-a-signature-with-no-private-key.md), admits the image you signed keyless and rejects an unsigned image *at the door* — the pod is never created, the rejection names the failed verification. This is where the whole supply-chain module lands on the cluster: the signature you made off-cluster becomes an admission-time gate, so an image's right to run is a property of who signed it, not where it came from.

**Rests on** — [the keyless signature from exercise 19](19-a-signature-with-no-private-key.md) (the identity this policy trusts) and [the Kyverno engine installed in exercise 7](07-kyverno-on-the-chain-you-already-read.md) (still running). Both are prerequisites; this exercise is what they were for.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair) — **back on the cluster** after four hopper-side exercises. Kyverno is still installed from [exercise 7](07-kyverno-on-the-chain-you-already-read.md).

**Read** — [Kyverno `verifyImages`](https://kyverno.io/docs/writing-policies/verify-images/): the rule matches image references by glob, lists trusted `attestors` (for keyless: a `subject` regexp and an `issuer`), and on a match *mutates the image reference to its digest* if verification passes or *denies* if it fails. The question to answer: *why does a passing verification rewrite the tag to a digest* — what attack does pinning the digest at admission close that verifying the tag alone would leave open?

**Do** — apply a policy trusting your identity, then try both images:

```sh
REG=ghcr.io/YOURNAME/signdemo   # the repo you signed in exercise 19
kubectl apply -f - <<YAML
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: {name: verify-signed}
spec:
  validationFailureAction: Enforce
  webhookTimeoutSeconds: 30
  rules:
  - name: check-signature
    match:
      any:
      - resources: {kinds: [Pod]}
    verifyImages:
    - imageReferences: ["$REG*"]
      attestors:
      - entries:
        - keyless:
            subject: "YOUR_OIDC_SUBJECT"
            issuer: "YOUR_OIDC_ISSUER"
YAML
kubectl create ns supply
# signed image — should be admitted, and its tag rewritten to a digest
kubectl -n supply run signed --image=$REG:v1
# unsigned image in the same repo scope — should be rejected
kubectl -n supply run unsigned --image=$REG:unsigned 2>&1 | tee reject.txt
```

**Observe** — `signed` is created; inspect it with `kubectl -n supply get pod signed -o jsonpath='{.spec.containers[0].image}'` and see the tag has become `$REG@sha256:...` — Kyverno pinned it. `unsigned` is refused with a message naming the failed image verification, and `kubectl -n supply get pod unsigned` returns `NotFound` — it never existed. The digest rewrite is the answer to the reading question: verifying a *tag* proves the tag pointed at a signed image *at admission time*, but a tag is mutable — the registry could repoint it afterward. Pinning to the digest at admission binds the running pod to the exact bytes that were verified, closing the tag-mutation window. Signature verifies *content*; digest pinning *keeps* that content.

**Expect** — signed pod running on a digest, unsigned pod never created. If both are admitted, the `imageReferences` glob is not matching your repo, or `validationFailureAction` is `Audit` not `Enforce`; if both are rejected, the `subject`/`issuer` do not match what [exercise 19](19-a-signature-with-no-private-key.md)'s verify printed.

**Write down** — the rewritten digest on the admitted pod, the rejection message on the unsigned one, and one sentence on why passing verification pins the digest.

**Teardown** — namespace and policy go; Kyverno stays (the CVE capstone may reference it); **the topology stays**:

```sh
kubectl delete ns supply
kubectl delete clusterpolicy verify-signed
```
