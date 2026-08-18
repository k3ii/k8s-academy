<a id="10c4-a-digest-that-no-longer-matches"></a>
# 10.C4 — the signature is real, the image is real, and verification fails anyway because they are not the same image

**Claim** — with [the verifyImages policy from exercise 20](20-verifyimages-rejects-the-unsigned.md) still enforcing, two failures that look different but are the same failure: (a) an *unsigned* image is rejected, and (b) a *signed* image whose bytes were changed after signing — a different digest under the same tag — is *also* rejected, because a cosign signature is bound to a content digest, not to a tag or a name. The drill's whole payload is that last clause: you cannot sign `myimage:latest` and then swap what `latest` points to, because the signature was never about the name.

**Rests on** — [exercise 20](20-verifyimages-rejects-the-unsigned.md)'s policy and [exercise 19](19-a-signature-with-no-private-key.md)'s signature. This is their adversarial test.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Kyverno and the `verify-signed` policy from [exercise 20](20-verifyimages-rejects-the-unsigned.md) are still in place.

**Read** — re-read [what cosign signs](https://docs.sigstore.dev/cosign/signing/overview/): the signature payload includes the image's `sha256` digest. The question to answer: *if you rebuild an image with one byte changed and push it to the same tag, what happens to the digest, and therefore to the signature that named the old digest?*

**Do — the unsigned rejection first (the easy half):**

```sh
REG=ghcr.io/YOURNAME/signdemo
kubectl create ns c4
kubectl -n c4 run u --image=$REG:unsigned 2>&1 | grep -i 'failed\|not.*signed\|verif'
```

**Do — the tampered-digest rejection (the point):** rebuild the image so its content differs, push it to the *same signed tag*, and try to run it. cosign's signature was made against the old digest; the new bytes have a new digest the signature does not cover:

```sh
ssh zain@hopper
REG=ghcr.io/$(whoami)/signdemo
# same tag, different content -> different digest, old signature no longer applies
docker build -t $REG:v1 - <<'DOCK'
FROM gcr.io/distroless/static-debian12
ENV TAMPERED=yes
DOCK
docker push $REG:v1        # v1 now resolves to a NEW digest, unsigned
exit
# back on the workstation:
kubectl -n c4 run tampered --image=ghcr.io/YOURNAME/signdemo:v1 2>&1 | tee c4-reject.txt
```

**Observe** — both `u` (never signed) and `tampered` (signed tag, changed bytes) are refused by the same policy with the same class of message: *image verification failed, no matching signature for the digest*. `kubectl -n c4 get pods` shows neither was created. The two rejections are identical because to Kyverno they *are* identical: it resolved each tag to a digest and found no valid signature covering *that digest*. The tampered image's old signature still exists in Rekor — it just names a digest this image no longer has. **That is the drill's one sentence: a signature is a statement about bytes, so changing the bytes silently un-signs the image, and no attacker can re-point a tag to smuggle content past a verifier that checks digests.**

**Expect** — two rejections, one cause. If the tampered image is *admitted*, the rebuild produced an identical digest (nothing actually changed — make sure the `ENV`/content edit took) or the policy is in `Audit` mode.

**Write down** — the two rejection messages, the old vs. new digest of the tampered tag, and the sentence: signature binds to content, not to name.

**Teardown** — namespace goes; restore the signed `v1` on `hopper` if you want [exercise 20](20-verifyimages-rejects-the-unsigned.md) repeatable (re-sign the new digest); **the topology stays**:

```sh
kubectl delete ns c4
```
