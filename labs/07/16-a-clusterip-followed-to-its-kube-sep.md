<a id="a-clusterip-followed-to-its-kube-sep"></a>
# One ClusterIP, followed through four chains to a DNAT, and the chain name that is a hash of the key

**Artifact** — a hop-by-hop path from `KUBE-SERVICES` to a `DNAT --to-destination <pod>:<port>` for one Service on this cluster, every hop quoted from a live `iptables-save`, with the endpoint confirmed against `discovery/v1` and the DNAT site cited as `file:line` in `pkg/proxy/iptables/proxier.go`. **The second of [P6's three owed citations](../../phases/06-kubelet-node.md#capstone)**, for the iptables backend; [exercise 17](17-the-same-service-as-a-verdict-map.md) does the other one.

**Rests on** — [exercise 14](14-the-model-files-before-the-machine.md), whose service-port key turns out to be visible in the rule dump, and [exercise 4](04-eleven-kilobytes-of-endpointslice.md) for the endpoint the DNAT has to match.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Read the rules on the **worker `.131`**, where your CNI plugin put the pods, so that the DNAT targets and the pod addresses are in the same subnet you allocated.

**Setup** — confirm the backend before reading rules for it, and make a Service with enough endpoints that the load-balancing hop has something to choose between:

```sh
kubectl -n kube-system get cm kube-proxy -o jsonpath='{.data.config\.conf}' | grep -E '^ *mode:'
kubectl -n kube-system get ds kube-proxy -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
kubectl create ns svc
kubectl -n svc create deployment web --image=registry.k8s.io/e2e-test-images/agnhost:2.47 --replicas=3 -- /agnhost netexec --http-port=8080
kubectl -n svc expose deployment web --port=80 --target-port=8080
kubectl -n svc get svc web -o jsonpath='{.spec.clusterIP}{"\n"}'
kubectl -n svc get endpointslice -o json | jq -r '.items[].endpoints[].addresses[0]'
```

**Read** — `syncProxyRules` in `pkg/proxy/iptables/proxier.go`, **and nothing else in that file.** It is 61 KB; the function is the phase's assignment and the rest is not. Four things to locate, in this order, because it is the order the function writes them in:

| Find | Because |
|---|---|
| the helper that computes a `KUBE-SVC-*` chain name | it is a hash of [exercise 14's](14-the-model-files-before-the-machine.md) service-port key, which makes the dump readable rather than opaque |
| the helper that computes a `KUBE-SEP-*` chain name | same, for an endpoint |
| where the `DNAT` rule is written | **this is the citation** |
| where `KUBE-MARK-MASQ` is written, and the condition | it is not written for every packet, and the condition is the whole of why a Service works from off-cluster |

**Do — follow it, one `grep` per hop, on the node.** Never read the whole dump; four greps in order:

```sh
ssh zain@10.10.10.131
sudo -i
CIP=<the ClusterIP>
iptables-save -t nat > /tmp/nat.rules; wc -l /tmp/nat.rules
grep -- "-d $CIP/32" /tmp/nat.rules                      # hop 1: KUBE-SERVICES -> KUBE-SVC-xxxx
SVC=$(grep -- "-d $CIP/32" /tmp/nat.rules | grep -o 'KUBE-SVC-[A-Z0-9]*' | head -1)
grep -- "-A $SVC " /tmp/nat.rules                        # hop 2: the choice between endpoints
SEP=$(grep -- "-A $SVC " /tmp/nat.rules | grep -o 'KUBE-SEP-[A-Z0-9]*' | head -1)
grep -- "-A $SEP " /tmp/nat.rules                        # hop 3: mark-masq, then hop 4: DNAT
```

**Observe** — then prove the chain name is the key, rather than being told:

```sh
grep -c '^:KUBE-SVC-' /tmp/nat.rules; grep -c '^:KUBE-SEP-' /tmp/nat.rules
kubectl -n svc get svc web -o jsonpath='{.spec.ports[0].name}{"\n"}'   # empty for a single unnamed port
```

**Expect** — hop 2 to contain three rules for three endpoints, the first two carrying `-m statistic --mode random --probability`, and the **last one carrying no probability at all**. That is not a rounding shortcut; it is the only way to make a chain of independent probabilistic jumps sum to exactly 1, and the probabilities are `1/3`, `1/2`, then unconditional. Work the arithmetic out and check it against the dump — it is the most commonly misread three lines in Kubernetes networking.

Expect hop 4's `--to-destination` to be one of the addresses `jq` printed from the EndpointSlice, and expect it to be in **your** CNI's subnet. Expect `KUBE-MARK-MASQ` in hop 3 to be conditional on the source *not* being a pod address — the condition your reading found — which is why pod-to-Service traffic keeps its source IP and off-cluster traffic does not.

Expect the two counts to be the argument of [KEP-3866](../../strands/source-reading.md#area-5-networking) in two numbers: **one chain per service port plus one chain per endpoint**, on every node, rewritten as a unit. Scale that to a thousand services and you have the scaling account KEP-3866 opens with.

**Verify from outside** — prove the path carries traffic and that the load balancing is real:

```sh
kubectl -n svc run c --rm -it --restart=Never --image=registry.k8s.io/e2e-test-images/agnhost:2.47 -- \
  sh -c 'for i in $(seq 1 30); do curl -s http://web.svc/hostname; echo; done' | sort | uniq -c
```

Three pod names, roughly ten each. A distribution that is 30/0/0 means the statistic rules were read wrong or one endpoint is not `Ready`, and either way the EndpointSlice says which.

**Write down** — the four hops quoted verbatim, the probability arithmetic, the DNAT `file:line` with the commit, and one sentence for P6: *`syncProxyRules` reprograms the rules* — now with a backend named and a line number under it. **Do not delete the dump**; [exercise 17](17-the-same-service-as-a-verdict-map.md) compares against it and [exercise 19](19-7c3-delete-one-endpoint-rule.md) breaks one of these chains by hand.

```sh
cp /tmp/nat.rules /root/nat-iptables-mode.rules
```

**Footprint note** — three `agnhost` pods, ~45 MiB. No change to the phase's 6.5GB.

**Teardown** — keep the namespace and the Service; [exercises 17](17-the-same-service-as-a-verdict-map.md), [18](18-the-tracker-between-two-syncs.md) and [19](19-7c3-delete-one-endpoint-rule.md) all drive it. **The topology stays.**

One last thing worth testing before moving on, because it follows from the chain-name reading and is two commands: delete the Service and re-create it identically, and the `KUBE-SVC-*` chain name comes back **the same** — the hash is over the service-port key, not over the object's UID. Then delete one **pod**: the `KUBE-SVC-*` name is unchanged and one `KUBE-SEP-*` name is new, because that hash includes the endpoint's address. Two hashes, two scopes, and it is the difference between a rule set that churns on every rollout and one that mostly does not.
