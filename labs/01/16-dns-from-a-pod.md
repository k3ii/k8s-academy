<a id="dns-from-a-pod"></a>
# Why a one-label name resolves and a two-label name does not

**Claim** — you can predict how many DNS queries a given name produces from inside a pod. You can explain the count from `/etc/resolv.conf` alone. This includes the case where a public name takes five queries to resolve.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), still up, with the `web` Service.

**Do**

1. From a pod, read the file that decides everything:

   ```sh
   kubectl exec -it probe -- cat /etc/resolv.conf
   ```

   Three lines matter: `nameserver`, `search`, and `options ndots:5`. Write down what you predict each line does, before you test anything.

2. **Predict the query count** for each of the names below. Then measure it.
   - `web`
   - `web.default`
   - `web.default.svc.cluster.local`
   - `web.default.svc.cluster.local.` — note the trailing dot
   - `github.com`

   Measure by watching CoreDNS. Do not trust the client:

   ```sh
   kubectl -n kube-system logs -l k8s-app=kube-dns -f --prefix
   ```

   If the queries do not show, enable the `log` plugin in the CoreDNS ConfigMap first.

3. Resolve the headless-Service form and a pod-specific name. Compare the two answers against what the ClusterIP form returned. One form returns a single address that belongs to no pod. The other returns several addresses that do belong to pods.
4. Set `dnsConfig.options` on a pod, with `ndots: 1`. Repeat the measurement from step 2 for `github.com`. The count changes, and one number is the reason.
5. Break DNS in two ways, and diagnose each one from inside the pod only. First, scale CoreDNS to zero. Then restore it, and point a pod at a `nameserver` that does not answer, using `dnsPolicy: None`. The two symptoms are distinguishable, and that distinction is the useful part.

**Expect** — `web` costs one query only if you are lucky about the ordering. With `ndots:5`, every name that contains fewer than five dots is tried against each `search` suffix *first*. `github.com` therefore costs four failures before the fifth query succeeds. That is not a misconfiguration. It is the price of making `web` work, and it is the single most common source of "DNS is slow in Kubernetes" reports. The trailing dot makes a name fully qualified, and it skips the search list completely. That is the cheapest fix available, and it is the one that nobody uses.

**Write down** — the query-count table for the five names, with a one-sentence explanation of `ndots`. Add the two failure signatures from step 5.

**Teardown** — restore CoreDNS to its original replica count. Revert the ConfigMap if you enabled logging. Delete the probe pods. **The topology stays.**
