<a id="linkerd-read-and-never-installed"></a>
# Read `linkerd2-proxy` on `forge` and answer four questions Envoy answered differently — without installing anything

**Artifact** — `journal/p9-linkerd.md`: a four-row comparison table where **every row cites a file and line you found**, in a source tree you cloned but never ran. [The phase's ecosystem note](../../phases/09-service-mesh.md#ecosystem) says Linkerd is read-and-contrast because it cannot coexist with Istio on this node; this exercise is what "read" means concretely, and its cluster footprint is zero.

**Rests on** — [the worker-thread reading](03-which-object-owns-the-failure.md), [the certificate](15-a-certificate-that-names-a-serviceaccount.md) and [the cost curve](19-what-a-sidecar-costs.md). Each supplies the Envoy half of one row; this exercise supplies the other half.

**Topology** — **none.** [`forge`](../../strands/lab-topologies.md#build-guest) only, and `pair` may stay up untouched — nothing here talks to the cluster.

**Setup**

```sh
ssh zain@10.10.10.125
git clone --depth 1 https://github.com/linkerd/linkerd2-proxy ~/src/linkerd2-proxy
cd ~/src/linkerd2-proxy && du -sh . && ls linkerd/
rg --version || sudo apt-get install -y ripgrep
```

**Read — four questions, each answered by locating code rather than by reading a summary.** The searches below find candidates; the answer is the file and line you settle on, and finding *nothing* is a valid answer that must be reported as one:

| Question | Where to start looking | The Envoy answer it is contrasted with |
|---|---|---|
| How many worker threads does the proxy start, and what decides it? | `rg -n 'worker_threads\|CORES\|core_ids\|available_parallelism'` | [`concurrency` from `/server_info`, fixed at startup](03-which-object-owns-the-failure.md), and what a sidecar picked in [the cost curve](19-what-a-sidecar-costs.md) |
| Does it speak xDS? If not, what protocol does it get its configuration over, and what are that API's service names? | `rg -ni 'xds\|envoy\|discovery' --glob '!*.lock'` then `rg -n 'linkerd2-proxy-api\|Destination\|Identity' Cargo.toml linkerd/` | [four resource types on one ADS stream](10-one-service-four-resource-types.md) |
| What form does a workload identity take in its certificate — a URI SAN or a DNS SAN? | `rg -ni 'spiffe\|dns_name\|subject_alt' linkerd/` | [`spiffe://cluster.local/ns/mesh/sa/sleep`](15-a-certificate-that-names-a-serviceaccount.md) |
| Can an operator add a filter to the data path without recompiling the proxy? | `rg -ni 'wasm\|lua\|plugin\|extension' --glob '!*.lock'` | [an `EnvoyFilter` with inline Lua, pushed at runtime](11-an-ack-and-a-nack.md) |

**Do — one more search, for the thing the comparison usually gets wrong:**

```sh
cd ~/src/linkerd2-proxy
rg -n 'fn main' --glob '*.rs' | head
wc -l $(rg -l --glob '*.rs' '' | head -200) | tail -1
rg -c 'unsafe' --glob '*.rs' | wc -l
```

**Expect** — a proxy whose configuration protocol is **its own gRPC API rather than xDS**, and expect that to be the structural difference the other three rows follow from. A purpose-built control protocol carries exactly the concepts Linkerd has; xDS carries everything Envoy can express, which is why [your dynamic dump was two orders of magnitude larger than the file you typed](09-the-same-dump-now-dynamic.md) and why an Istio proxy holds configuration for services it will never call.

Expect the identity to be a **DNS-form name rather than a URI SAN**, encoding the same three facts — trust domain, namespace, ServiceAccount — in a different syntax. Note it precisely: this is the row where "both do mTLS with workload identity" is true and useless, and the difference decides whether a certificate is portable to a SPIFFE-aware system.

Expect **no runtime extension mechanism** — no WASM, no Lua, nothing an operator loads. That is the trade in one line: Envoy buys you [a fault injector you never installed](13-9c4-a-delay-you-declared.md) and an `EnvoyFilter` that can NACK a listener; Linkerd buys you a smaller surface with fewer ways to break it and no way to extend it in production.

Expect the thread-count question to have a different **shape** of answer, not just a different number — an async runtime over a task scheduler is not the same object as a thread-per-core listener model, and if the search leads you to a runtime builder rather than a worker count, that *is* the finding. Write down what you actually found.

**Do not install it.** [The phase says so](../../phases/09-service-mesh.md#ecosystem) and the reason is mechanical rather than cautious: both meshes install a CNI-adjacent node agent and both want to own a pod's interception, and this lab has [one worker with 1948Mi](04-the-request-that-does-not-fit.md) already running an Istio control plane. The comparison you can make honestly is a source comparison, so make that one well rather than a runtime comparison badly.

**Write down** — `journal/p9-linkerd.md`: the four rows with file and line for each answer, plus one paragraph on what a purpose-built proxy gives up and what it wins. Be specific about the footprint claim: you **measured** Envoy's sidecar cost and you have **not** measured Linkerd's, so cite the design reasons you found in the source and say plainly that the number is not yours. That distinction is the difference between this exercise and a blog post.

**Teardown**

```sh
rm -rf ~/src/linkerd2-proxy
```

**No topology to release** — nothing was provisioned and nothing in the cluster was touched. The clone goes; the notes stay.
