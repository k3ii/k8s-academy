<a id="7c2-it-was-dns"></a>
# 7.C2 — a resolver that lies, and a five-check method that clears it four times out of five

**Artifact** — drill [7.C2](../../phases/07-networking.md#chaos): the same application broken twice through DNS — once so that resolution **fails**, once so that resolution **succeeds and is wrong** — with [exercise 25's](25-a-name-resolved-in-five-hops.md) diagnostic checklist run in order against both and each check scored *clean* or *hit*. The deliverable is the scored checklist, not the outage.

**Rests on** — [exercise 25](25-a-name-resolved-in-five-hops.md) for the five hops, the checklist and the `dns` namespace; [exercise 20](20-7c1-a-partition-named-by-path.md) for Chaos Mesh, already resident. `dnsServer.create=true` in [the strand's install block](../../strands/chaos.md#install) exists for this drill and no other — this is where the flag is spent.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued, with Chaos Mesh and the `dns` namespace both up.

**Setup** — a baseline you can diff against, and a pod address you can reach without a name. Both matter: the whole signature of this fault class is *name fails, address works*, and you cannot show that without having the address written down first.

```sh
kubectl -n dns run app --image=registry.k8s.io/e2e-test-images/agnhost:2.47 --command -- sleep 3600
kubectl -n dns get pods -o wide          # note one web pod IP and the ClusterIP of web
kubectl -n dns exec app -- cat /etc/resolv.conf | tee /tmp/resolv.baseline
kubectl -n dns exec app -- getent hosts web
kubectl -n dns exec app -- curl -sS -m3 http://web/hostname; echo
kubectl -n dns exec app -- curl -sS -m3 http://<web-pod-ip>:8080/hostname; echo
kubectl -n chaos-mesh get pods -l app.kubernetes.io/component=chaos-dns-server
```

**Do — part 1, the honest failure.** `action: error` returns `SERVFAIL` for matching names:

```sh
kubectl apply -f - <<'YAML'
apiVersion: chaos-mesh.org/v1alpha1
kind: DNSChaos
metadata: {name: dns-servfail, namespace: dns}
spec:
  action: error
  mode: all
  patterns: ["web.dns.svc.cluster.local"]
  selector:
    namespaces: [dns]
    labelSelectors: {run: app}
YAML
kubectl -n dns exec app -- getent hosts web; echo "exit=$?"
kubectl -n dns exec app -- curl -sS -m3 http://web/hostname; echo "exit=$?"
kubectl -n dns exec app -- curl -sS -m3 http://<web-pod-ip>:8080/hostname; echo "exit=$?"
```

**Do — part 2, run the checklist and score it.** Five checks, in [exercise 25's](25-a-name-resolved-in-five-hops.md) order, against a fault that is live right now:

```sh
kubectl -n dns exec app -- cat /etc/resolv.conf | diff /tmp/resolv.baseline -    # hop 1
kubectl -n kube-system get svc kube-dns -o wide                                  # hop 3
kubectl -n kube-system get pods -l k8s-app=kube-dns -o wide                      # hop 4
kubectl -n kube-system get endpointslices -l k8s-app=kube-dns                    # hop 4
kubectl -n kube-system logs -l k8s-app=kube-dns --tail=20                        # hop 4
kubectl -n dns exec app -- getent hosts kube-dns.kube-system                     # a second name
kubectl -n dns exec app -- nslookup -type=SRV _http._tcp.web.dns.svc.cluster.local
```

| Check | Hop it tests | Clean or hit | What it actually proved |
|---|---|---|---|
| `resolv.conf` unchanged? | 1 | | |
| `kube-dns` Service and ClusterIP present? | 3 | | |
| CoreDNS pods `Ready`, EndpointSlice populated? | 4 | | |
| CoreDNS logs show the query? | 4 | | |
| A *different* name resolves? | 2–5 | | |

**Do — part 3, name the primitive from evidence.** [The mechanism table](../../strands/chaos.md#mechanisms) claims one Linux primitive per fault. Find this one rather than reciting it — there are only two places a redirect can live, and the two commands distinguish them:

```sh
kubectl -n dns exec app -- nslookup web.dns.svc.cluster.local | grep -i '^Server'
ssh zain@10.10.10.131 'sudo nsenter -t $(sudo crictl inspect --output go-template --template "{{.info.pid}}" $(sudo crictl ps -q --name app)) -n iptables-save -t nat | grep -i 53'
```

Either the pod's view of its resolver changed, or the pod's packets are being sent somewhere else with its view intact. Write down **which**, with the output that decided it — and note that the answer determines whether check 1 could ever have caught this.

**Do — part 4, the lie that looks like an answer.** Delete the first fault, apply the second:

```sh
kubectl -n dns delete dnschaos dns-servfail
kubectl apply -f - <<'YAML'
apiVersion: chaos-mesh.org/v1alpha1
kind: DNSChaos
metadata: {name: dns-random, namespace: dns}
spec:
  action: random
  mode: all
  patterns: ["web.dns.svc.cluster.local"]
  selector:
    namespaces: [dns]
    labelSelectors: {run: app}
YAML
kubectl -n dns exec app -- getent hosts web; echo "exit=$?"
kubectl -n dns exec app -- getent hosts web; echo "exit=$?"
kubectl -n dns exec app -- curl -sS -m3 http://web/hostname; echo "exit=$?"
kubectl -n dns exec app -- curl -sS -m3 -v http://web/hostname 2>&1 | head -5
```

**Gate** — the drill counts when you can state, in one sentence and without looking, **which check in the table above is the only one that fires** for each of the two faults, and why the other four are structurally unable to. A checklist you have only ever run against a healthy cluster is a list of commands; one you have run against a fault it misses is a method.

**Expect** — under `action: error`: the name fails, the address works, and **four of the five checks come back clean** — `resolv.conf` may be untouched, the `kube-dns` Service is healthy, CoreDNS is `Ready` with a full EndpointSlice, and the real CoreDNS's logs are silent *because it never received the query*. That silence is the strongest single piece of evidence in the drill and it is an absence, which is why it is the check people skip.

Under `action: random`: `getent` **succeeds** with a different address each call, and `curl` fails with a timeout rather than a refusal — the shape that generates the sentence this drill is named for. The application's error message will say *connection timed out*, will name an IP nobody recognises, and will not contain the word DNS anywhere.

Expect the SRV lookup in part 2 to be answered **correctly while the A record is being lied about**, because [the fault's own limits](../../strands/chaos.md#catalogue) are A/AAAA-only with suffix-only wildcards. A fault that covers one record type is a sharper instrument than one that covers all of them, and it means a partial DNS failure is a real thing rather than an artefact of this tool.

**Write down** — the scored five-row table for each of the two actions; the primitive from part 3 with its evidence; and the checklist rewritten as **six** checks, with the new one being whichever question would have found this in under a minute. That rewritten checklist is [the phase checklist's](../../phases/07-networking.md#checklist) DNS item and it is now yours rather than the talk's.

**Footprint note** — nothing new. `chaos-dns-server` is already resident and is the difference between [the strand's 512Mi and 582Mi figures](../../strands/chaos.md#install) — about 70Mi, spent once at [exercise 20](20-7c1-a-partition-named-by-path.md), used only here. Chaos Mesh stays for now and comes out before [exercise 31](31-kube-proxy-replaced-by-map-lookups.md) for the reason [the index](README.md) sets out.

**Teardown**

```sh
kubectl -n dns delete dnschaos --all
kubectl -n dns exec app -- cat /etc/resolv.conf | diff /tmp/resolv.baseline - && echo restored
kubectl -n dns exec app -- getent hosts web
kubectl delete ns dns
```

Check resolution *after* deleting the fault and before deleting the namespace — a chaos object whose finalizer did not run leaves the fault in place, and finding that out here is cheaper than finding it out in [exercise 31](31-kube-proxy-replaced-by-map-lookups.md). **The topology stays** — [exercise 27](27-adminnetworkpolicy-read-and-banked.md) reads only, and module 7.5 needs this cluster.
