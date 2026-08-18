<a id="a-scan-that-names-a-cve"></a>
# A known-vulnerable image, the CVE a scanner names, and the fixed version that clears it

**Artifact** — a `trivy` (and `grype`) scan of a deliberately old image that reports at least one `CRITICAL` CVE by ID, and a second scan of a patched tag of the same image where that CVE is gone. A scanner's value is not the wall of findings; it is the ability to answer "does *this* image have *that* CVE, and does bumping the version fix it?" — which is the exact question the phase capstone's remediation step asks about a real one.

**Rests on** — [the SBOM exercise](16-an-sbom-that-shrinks.md): a scanner is an SBOM matched against a vulnerability feed, so this is what the previous exercise's package inventory is *for*.

**Topology** — **none.** `trivy` and `grype` run on [`hopper`](../../strands/lab-topologies.md#build-guest) against a pulled image; no cluster. Footprint zero, per [the index](README.md).

**Read** — [how trivy decides](https://trivy.dev/latest/docs/): it builds a package list (its own SBOM), then joins it against advisory databases keyed by package + version + ecosystem. The question to answer: *why can two scanners disagree on the same image* — what about the "join against a database" step is not deterministic across tools?

**Do** — scan an old image, note a CRITICAL by ID, scan a fixed tag, confirm it clears:

```sh
ssh zain@hopper
# a deliberately old, known-vulnerable image
trivy image --severity CRITICAL,HIGH python:3.4-slim | tee old.scan
grep -Eo 'CVE-[0-9]{4}-[0-9]+' old.scan | sort -u | head
# the same ecosystem, current
trivy image --severity CRITICAL,HIGH python:3.12-slim | tee new.scan
```

Cross-check with a second scanner on the same old image:

```sh
grype python:3.4-slim | tee old.grype
# does grype name the same CVE trivy called CRITICAL?
comm -12 \
  <(grep -Eo 'CVE-[0-9]{4}-[0-9]+' old.scan  | sort -u) \
  <(grep -Eo 'CVE-[0-9]{4}-[0-9]+' old.grype | sort -u) | head
```

**Observe** — the old image reports a long CRITICAL/HIGH list; the current image reports far fewer (often zero CRITICAL). The two scanners' CVE sets overlap heavily but not perfectly — that overlap-not-identity is the answer to the reading question: each tool ships its *own* advisory database and its own matching heuristics (how it maps a distro package to an upstream CVE, whether it trusts a distro's "will-not-fix" status), so a CVE present in one feed and absent from another shows up as a disagreement about the identical bytes. The lesson for the capstone: a clean scan from one tool is not proof; agreement between two is stronger, and a named CVE with a fixed-in version is an *actionable* finding while a raw count is not.

**Expect** — a shared CVE ID both tools flag on the old image and neither flags on the new. If the new image also shows CRITICALs, that is realistic — pick a CVE that *is* in old and *not* in new for the write-down; the point is the delta, not a zero.

**Write down** — one CVE ID both scanners named on the old image, its fixed-in version, and one sentence on why two scanners can disagree.

**Teardown** — pulled images and scan files on `hopper`:

```sh
ssh zain@hopper 'docker rmi python:3.4-slim python:3.12-slim 2>/dev/null; rm -f ~/old.scan ~/new.scan ~/old.grype'
```
