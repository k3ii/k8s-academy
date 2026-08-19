<a id="three-ways-to-not-commit-a-secret"></a>
# You cannot commit a `Secret` — so here are three mechanisms that let you, compared on where the decryption happens and what holds the key

**Artifact** — a three-row table of SOPS, sealed-secrets and External Secrets Operator (ESO), each described by its *mechanism* — where the plaintext is reconstituted, and what component holds the key or the store — not by preference; and one secret actually shipped via **SOPS at zero in-cluster cost**, decrypted inside Flux's `kustomize-controller` with no new pod. The three answer the same problem (a `Secret` cannot live in git as plaintext) three structurally different ways, and naming the difference is the deliverable.

**Rests on** — [the Flux install](01-gitops-the-reconcile-loop-you-already-wrote.md), because SOPS decrypts *inside* `kustomize-controller` and needs it running; and [P10's encryption-at-rest work](../../phases/10-security.md#m10-1), where "a Secret is base64, not encryption" was first made concrete.

**Topology** — [`platform`](../../strands/lab-topologies.md#platform), continued.

**Read** — [the module's secrets framing](../../phases/12-gitops-platform.md#m12-1) and the objective that calls for [the SOPS half at zero in-cluster cost](../../phases/12-gitops-platform.md#objectives). The three mechanisms' internals are the point; the maturity note — [sealed-secrets is absent from the CNCF landscape entirely](../../phases/12-gitops-platform.md#ecosystem) — is part of the comparison, not a footnote.

**Build** — encrypt one secret with SOPS and commit it; watch Flux decrypt it in-controller; then install sealed-secrets and seal the same value to contrast where the key lives:

```sh
# SOPS: encrypted in git, decrypted in-process by kustomize-controller — zero extra pods
sops --encrypt --age <recipient> secret.yaml > secret.enc.yaml   # commit this
kubectl -n flux-system create secret generic sops-age --from-file=age.agekey    # the decrypt key
# reference it from the Kustomization: spec.decryption.provider=sops
kubectl get secret <name> -o jsonpath='{.data}'   # present in-cluster, plaintext never in git
kubectl get pods -n flux-system                    # no new pod appeared for SOPS
# sealed-secrets: a controller holds a private key; the SealedSecret is public-safe
kubeseal --format=yaml < secret.yaml > sealed.yaml    # commit this
kubectl get pods -n kube-system -l name=sealed-secrets-controller   # 32Mi req / 128Mi limit
```

**Verify from outside** — the SOPS half is verifiable by pod count: `kubectl get pods -A` before and after shows **no new pod**, because the decryption is a library call inside a controller you already run. The sealed-secrets half shows exactly one new pod holding the private key. ESO is read, not installed here — its `kubernetes` provider reads a store in the *local* cluster, so it needs no external Vault, but it does add three pods; the table records that without paying for it.

**Expect** — the same plaintext value reaching the cluster three ways, distinguished by: SOPS decrypts *in-process* (the key is Flux's, no controller of its own); sealed-secrets holds a *private key in a controller* (the `SealedSecret` is safe to commit because only that controller can open it); ESO holds *no secret* but reconciles a `Secret` from a store on a `refreshInterval`. Where the decryption happens is the whole distinction.

**Write down** — the three-way table (SOPS / sealed-secrets / ESO), each row naming where plaintext is reconstituted and what holds the key or store; and the pod-count proof that SOPS cost zero.

**Footprint note** — SOPS: [0 pods, 0 MiB](../../research/platform-engineering-footprints.md) (in-process in `kustomize-controller`); sealed-secrets: [1 pod, 32Mi req / 128Mi limit](../../research/platform-engineering-footprints.md). ESO is read here, not installed. [`platform`](../../strands/lab-topologies.md#platform) is unmoved by the SOPS half.

**Teardown** — delete the demo secrets; sealed-secrets may be removed now or left to be swept [at the group boundary](10-the-teardown-that-proves-git.md). The SOPS decrypt-key secret stays with Flux. **The topology stays.**
