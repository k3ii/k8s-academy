<a id="a-signature-with-no-private-key"></a>
# An image signed with a key that never existed, and the public transparency-log entry that proves it

**Artifact** — a container image you built and pushed, a `cosign sign` that used *no long-lived private key* (identity came from an OIDC token, Fulcio issued a short-lived certificate), a `cosign verify` that names your identity and the OIDC issuer, and the Rekor transparency-log entry UUID that recorded the signing event publicly. Keyless signing is the supply-chain primitive the phase's admission rule will enforce; this exercise produces the signature that [exercise 20](20-verifyimages-rejects-the-unsigned.md) will demand.

**Rests on** — [the SBOM and scan exercises](17-a-scan-that-names-a-cve.md): signing attests *this image, unmodified* — it is the integrity layer on top of the vulnerability layer. You sign an image you have already decided is clean.

**Topology** — **none.** `cosign` runs on [`hopper`](../../strands/lab-topologies.md#build-guest); the registry is whatever you push to; Fulcio and Rekor are public Sigstore services. No cluster. Footprint zero, per [the index](README.md).

**Read** — [how keyless cosign works](https://docs.sigstore.dev/cosign/signing/overview/): `cosign sign` opens an OIDC flow, gets a token proving *who you are*, sends it to Fulcio which returns a certificate binding that identity to an ephemeral key valid for minutes, signs, and logs the signature to Rekor — then throws the key away. The question to answer: *if there is no private key stored anywhere, what exactly is `cosign verify` checking against* — where does the trust root live if not in a key you hold?

**Build** — on `hopper`, push an image, sign it keyless, verify it, and read the Rekor entry:

```sh
ssh zain@hopper
# push a trivial image you own to a registry you control (GHCR shown)
REG=ghcr.io/$(whoami)/signdemo
docker build -t $REG:v1 - <<'DOCK'
FROM gcr.io/distroless/static-debian12
DOCK
docker push $REG:v1
DIGEST=$(cosign triangulate --type digest $REG:v1 2>/dev/null || docker inspect --format='{{index .RepoDigests 0}}' $REG:v1)

# keyless sign — this opens an OIDC flow; on a headless box use a device-code or CI token
COSIGN_EXPERIMENTAL=1 cosign sign --yes $REG:v1
```

**Verify from outside** — verify by identity (not by a key), and pull the transparency-log record:

```sh
COSIGN_EXPERIMENTAL=1 cosign verify \
  --certificate-identity-regexp '.*' \
  --certificate-oidc-issuer-regexp '.*' \
  $REG:v1 | jq '.[0].optional.Subject, .[0].optional.Issuer, .[0].optional.Bundle.Payload.logIndex'
```

**Expect** — `cosign verify` prints your OIDC subject (your email or CI identity), the issuer (e.g. GitHub or Google), and a Rekor `logIndex`/UUID. That triple is the answer to the reading question: there is no key to trust, so verification checks that *a signature exists, was made by the named identity, was certified by Fulcio's CA, and was recorded in Rekor's append-only log* — the trust root is the transparency log plus Fulcio's root, not a secret in your possession. Look the entry up publicly: `rekor-cli get --log-index <N>` returns the same signing event, which means anyone can audit that this image was signed, by whom, and when — the property key-based signing cannot give you because a stolen key signs silently.

**Write down** — the verified subject + issuer, the Rekor log index, and one sentence on where the trust root lives when there is no private key.

**Teardown** — the signature and Rekor entry are *permanent by design* (a transparency log is append-only — you cannot and should not try to delete the entry); remove only local images:

```sh
ssh zain@hopper 'docker rmi ghcr.io/$(whoami)/signdemo:v1 2>/dev/null || true'
```
