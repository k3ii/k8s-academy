<a id="dns-from-a-pod"></a>
# Why a one-label name resolves and a two-label name does not

**Claim** — you can predict how many DNS queries a given name produces from inside a pod, and explain the count from `/etc/resolv.conf` alone, including the case where a public name takes five queries to resolve.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up, with the `web` Service.

**Do**

1. From a pod, read the file that decides everything:

   ```sh
   kubectl exec -it probe -- cat /etc/resolv.conf
   ```

   Three lines matter: `nameserver`, `search`, and `options ndots:5`. Write down what you predict each does before testing.

2. **Predict the query count** for each of these, then measure it:
   - `web`
   - `web.default`
   - `web.default.svc.cluster.local`
   - `web.default.svc.cluster.local.` (note the trailing dot)
   - `github.com`

   Measure by watching CoreDNS rather than by trusting the client:

   ```sh
   kubectl -n kube-system logs -l k8s-app=kube-dns -f --prefix
   ```

   Enable the `log` plugin in the CoreDNS ConfigMap first if the queries are not showing.

3. Resolve the headless-Service form and a pod-specific name, and compare the answers to what the ClusterIP form returned. One returns a single address that belongs to no pod; the other returns several that do.
4. Set `dnsConfig.options` on a pod with `ndots: 1` and repeat step 2's measurement for `github.com`. The count changes and the reason is one number.
5. Break it two ways and diagnose each from inside the pod only: scale CoreDNS to zero, and then (restored) point a pod at a `nameserver` that does not answer using `dnsPolicy: None`. The two symptoms are distinguishable and the distinction is the useful part.

**Expect** — `web` costs one query only if you are lucky about ordering; with `ndots:5` every name containing fewer than five dots is tried against each `search` suffix *first*, so `github.com` costs four failures before the fifth query succeeds. That is not a misconfiguration — it is the price of making `web` work — and it is the single most common source of "DNS is slow in Kubernetes" reports. The trailing dot makes a name fully qualified and skips the search list entirely, which is the cheapest fix available and the one nobody uses.

**Write down** — the five-name query-count table with the `ndots` explanation in one sentence, and the two failure signatures from step 5.

**Teardown** — restore CoreDNS to its original replica count and revert the ConfigMap if you enabled logging. Delete the probe pods. **The topology stays.**
