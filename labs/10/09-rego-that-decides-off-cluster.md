<a id="rego-that-decides-off-cluster"></a>
# A Rego policy that returns a deny message with no cluster in the room

**Artifact** — a `.rego` file that, run through `opa eval` against a Pod manifest on [`forge`](../../strands/lab-topologies.md#build-guest), returns an empty `deny` set for a hardened pod and a populated one — carrying a human message — for a pod that runs as root. The point is not to install Gatekeeper; it is to learn the language admission policy is *written* in, on a laptop-sized binary, so that when you later read a `ConstraintTemplate` its embedded Rego is not the first Rego you have ever seen.

**Rests on** — [exercise 7](07-kyverno-on-the-chain-you-already-read.md) put a policy engine (Kyverno) on the admission chain with its own YAML-flavoured DSL; this exercise shows the *other* major dialect — OPA's Rego — evaluated standalone, so the two engines' expressiveness can be compared without paying for a second controller.

**Topology** — **none.** This runs entirely on [`forge`](../../strands/lab-topologies.md#build-guest) with a single ~40MB `opa` binary; `pair` may be up and idle beside it or torn down — it is not consulted. Costed as zero cluster RAM in [the phase footprint](README.md).

**Read** — [the Rego document model](https://www.openpolicyagent.org/docs/latest/policy-language/): a policy is a set of rules that assign to variables; a rule with an unsatisfied body contributes nothing, which is why `deny` is a *set* that is empty when the input is fine. The question to answer from it before you write any: *why is `deny` a set and not a boolean* — what does that let a policy author do that a single true/false could not?

**Build** — on `forge`, fetch the binary and write two inputs and one policy:

```sh
ssh zain@forge
cd ~ && curl -sSL -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64_static && chmod +x opa
cat > pod-ok.json <<'JSON'
{"kind":"Pod","spec":{"securityContext":{"runAsNonRoot":true},"containers":[{"name":"c","securityContext":{"runAsNonRoot":true,"allowPrivilegeEscalation":false}}]}}
JSON
cat > pod-bad.json <<'JSON'
{"kind":"Pod","spec":{"containers":[{"name":"c","securityContext":{"runAsNonRoot":false,"privileged":true}}]}}
JSON
cat > pod.rego <<'REGO'
package k8s.pod
import rego.v1

deny contains msg if {
  some c in input.spec.containers
  not c.securityContext.runAsNonRoot
  msg := sprintf("container %q may run as root", [c.name])
}

deny contains msg if {
  some c in input.spec.containers
  c.securityContext.privileged
  msg := sprintf("container %q is privileged", [c.name])
}
REGO
```

**Verify from outside** — evaluate each input and read the `deny` set that comes back:

```sh
./opa eval -d pod.rego -i pod-ok.json  'data.k8s.pod.deny' --format pretty
./opa eval -d pod.rego -i pod-bad.json 'data.k8s.pod.deny' --format pretty
```

**Expect** — the first prints an empty set (`[]`); the second prints a set with two strings — the root message and the privileged message — because *both* rule bodies were satisfied and each contributed one element. That is the answer to the reading question made concrete: a boolean could say "denied", but a set says denied *and here are the two independent reasons*, which is exactly what an admission webhook returns to a user as a multi-line rejection. Change `pod-bad.json` to set `runAsNonRoot:true` and re-run; watch the set shrink to one message, not flip to false.

**Write down** — the two-element deny set, and one sentence on why a set-valued rule is the natural shape for a policy that can fail several ways at once.

**Teardown** — three files and a binary on `forge`; nothing on any cluster:

```sh
ssh zain@forge 'rm -f ~/opa ~/pod-ok.json ~/pod-bad.json ~/pod.rego'
```
