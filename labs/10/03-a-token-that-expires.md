<a id="a-token-that-expires"></a>
# Two tokens for the same ServiceAccount: one names an audience and an expiry, one is good forever

**Claim** — a projected ServiceAccount token mounted into a running pod carries `aud`, `exp` and a `kubernetes.io` claim binding it to *that pod*, and it is refused once its `exp` passes; a token minted the legacy way (`kubectl create token --duration=...` notwithstanding, the old auto-created Secret) carries no `exp` and no bound audience, so a copy of it is a credential with no clock. Decode both from their base64 middle segment and the difference is four claims, which is the whole of [KEP-1205](../../phases/10-security.md#m10-1).

**Rests on** — [exercise 1](01-one-verb-one-resource.md)'s ServiceAccount pattern. The blast-radius argument here is the one [the capstone postmortem](26-the-cve-incident.md) needs for "what a leaked token is worth" — a bound token that has expired is worth nothing, a forever-token is worth whatever it could ever do.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — [KEP-1205](https://github.com/kubernetes/enhancements/tree/master/keps/sig-auth/1205-bound-service-account-tokens). [The reading question](../../phases/10-security.md#m10-1) is why a bound token is a smaller blast radius; answer it in terms of the two claims a stolen copy cannot satisfy after the fact — `exp` (it stops working) and the bound object reference (it names a pod that may no longer exist).

**Setup** — a decoder that needs no tools beyond `base64` and `jq`, because a real incident reads a token off a compromised disk without a JWT library:

```sh
jwtclaims() { cut -d. -f2 | tr '_-' '/+' | { cat; echo '==='; } | base64 -d 2>/dev/null | jq .; }
kubectl create namespace tok
kubectl -n tok create serviceaccount app
kubectl -n tok run app --image=registry.k8s.io/pause:3.9 --overrides='{"spec":{"serviceAccountName":"app"}}'
kubectl -n tok wait --for=condition=Ready pod/app
```

**Do — the bound token**, read from the pod's projected volume where a compromised process would find it:

```sh
kubectl -n tok exec app -- cat /var/run/secrets/kubernetes.io/serviceaccount/token | jwtclaims
```

**Do — a token with a short life, to watch it die:**

```sh
kubectl -n tok create token app --duration=600s | jwtclaims        # note exp
SHORT=$(kubectl -n tok create token app --duration=60s)
kubectl --token="$SHORT" -n tok get pods                            # works now
# wait past 60s, then:
kubectl --token="$SHORT" -n tok get pods                            # 401: token expired
```

**Observe** — the projected token's claims: `aud` (defaults to the apiserver, not `*`), `exp` roughly an hour out and auto-rotated by the kubelet before it lands, and a `kubernetes.io.pod` reference with a UID. Contrast with what a legacy auto-mounted Secret token would show — the same `sub`, but no `exp`, no bound `aud`, no pod reference. On a current cluster the legacy forever-Secret is not created automatically; that this took an explicit change is itself the KEP.

**Expect** — the 60-second token to return `401 Unauthorized` with an "token is expired" message after its `exp`, from the *same* apiserver that accepted it a minute earlier. Nothing was revoked; the token expired itself. **This is the blast-radius sentence made concrete:** a token exfiltrated from a pod during [the capstone incident](26-the-cve-incident.md) is a credential with a fuse, and the length of that fuse is the `exp` you just read.

**Write down** — the four claims that separate the bound token from a forever-Secret, and the observed `401` with its message. The postmortem's "what the attacker could have done with the token they found" is bounded by these.

**Teardown** — the namespace goes; **the topology stays**:

```sh
kubectl delete namespace tok
```
