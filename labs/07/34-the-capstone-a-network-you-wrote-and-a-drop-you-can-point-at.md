<a id="the-capstone-a-network-you-wrote-and-a-drop-you-can-point-at"></a>
# The capstone: a pod networked by your own plugin, a drop with a map entry behind it, and three citations P6 was owed

**Artifact** — [the phase capstone](../../phases/07-networking.md#capstone) in three parts, produced on one cluster in one sitting: **(1)** two pods on `.131` wired by the CNI plugin you wrote, pinging each other; **(2)** a NetworkPolicy drop on `.130` proven by the eBPF policy map entry and a `cilium monitor` event, not by a failed connection; **(3)** [the three `file:line` citations P6 was owed](../../phases/06-kubelet-node.md#capstone), each re-verified against the commit this cluster is running.

**Rests on** — everything. Specifically: [exercise 8](08-add-and-del-that-cnitool-accepts.md) and [10](10-the-plugin-the-kubelet-calls.md) for part 1, [30](30-a-drop-decided-by-a-map-entry.md) and [32](32-the-prediction-scored-at-the-datapath.md) for part 2, and [15](15-the-reconciler-and-its-packing-heuristic.md), [16](16-a-clusterip-followed-to-its-kube-sep.md), [17](17-the-same-service-as-a-verdict-map.md) and [18](18-the-tracker-between-two-syncs.md) for part 3.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued and final. **It goes at the end of this exercise**, and so does the phase.

**Do — part 1: your plugin, after everything**

```sh
ssh zain@10.10.10.131
sudo cp /root/05-academy.conflist.kept /etc/cni/net.d/01-academy.conflist
sudo chmod 0600 /etc/cni/net.d/01-academy.conflist && ls -l /etc/cni/net.d
sudo journalctl -u kubelet -f &
```

The rename to `01-` is [exercise 10's](10-the-plugin-the-kubelet-calls.md) discovery order, used deliberately for the first time: yours must sort before Cilium's for the next pod on this node, and that is the whole mechanism. Then two pods, pinned to `.131`:

```sh
for i in 1 2; do kubectl -n cap run p$i --image=registry.k8s.io/e2e-test-images/agnhost:2.47 \
  --overrides='{"spec":{"nodeSelector":{"kubernetes.io/hostname":"<worker>"}}}' --command -- sleep 3600; done
kubectl -n cap get pods -o wide
kubectl -n cap exec p1 -- ping -c3 $(kubectl -n cap get pod p2 -o jsonpath='{.status.podIP}')
kubectl -n kube-system exec ds/cilium -- cilium-dbg endpoint list | grep -c cap
ssh zain@10.10.10.131 'sudo ls /var/lib/cni/academy/*/'
```

**Expect** — the ping to work, both addresses to come from [your IPAM's lease directory](09-an-ipam-that-does-not-leak.md), and **`cilium endpoint list` not to know these pods exist**. That last line is the honest part of part 1: a pod your plugin created is a pod Cilium cannot enforce policy on, which is why part 2 runs on the other node and why "the CNI is where enforcement lives" is a structural claim rather than a slogan.

**Do — part 2: the drop, and the thing you can point at**

```sh
kubectl -n cap run srv --image=registry.k8s.io/e2e-test-images/agnhost:2.47 \
  --overrides='{"spec":{"nodeSelector":{"kubernetes.io/hostname":"<control-plane>"},"tolerations":[{"operator":"Exists"}]}}' \
  --labels app=srv --command -- /agnhost netexec --http-port=8080
kubectl -n cap run cli --image=registry.k8s.io/e2e-test-images/agnhost:2.47 \
  --overrides='{"spec":{"nodeSelector":{"kubernetes.io/hostname":"<control-plane>"},"tolerations":[{"operator":"Exists"}]}}' \
  --labels app=cli --command -- sleep 3600
kubectl -n cap exec cli -- curl -sS -m3 -o /dev/null -w 'before=%{http_code}\n' http://<srv-ip>:8080/hostname
kubectl -n cap apply -f - <<'YAML'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: only-app-x}
spec:
  podSelector: {matchLabels: {app: srv}}
  ingress:
  - from: [{podSelector: {matchLabels: {app: x}}}]
YAML
kubectl -n cap exec cli -- curl -sS -m3 -o /dev/null -w 'after=%{http_code}\n' http://<srv-ip>:8080/hostname
```

Then produce the proof — three artefacts, and the failed `curl` is none of them:

```sh
EP=$(kubectl -n kube-system exec ds/cilium -- cilium-dbg endpoint list -o json | jq -r '.[]|select(.status."external-identifiers"."pod-name"|test("srv"))|.id')
kubectl -n kube-system exec ds/cilium -- cilium-dbg bpf policy get $EP
kubectl -n kube-system exec ds/cilium -- cilium-dbg identity list | grep 'app=cli'
kubectl -n kube-system exec ds/cilium -- cilium-dbg monitor --type drop --related-to $EP &
kubectl -n cap exec cli -- curl -sS -m3 -o /dev/null http://<srv-ip>:8080/hostname; kill %1
```

**Gate** — the proof counts when you can say, in one sentence each: **which identity** was refused, **which map** refused it, **at which hook** that map is consulted, and **what the drop event's reason field says**. [The capstone's wording](../../phases/07-networking.md#capstone) is deliberate — *"the connection failed" is not a proof; the packet's fate in the datapath is* — and the test of whether you have it is whether a hostile reader could reproduce the four answers from your notes without the cluster.

**Do — part 3: pay P6's debt, verified live**

```sh
cd ~/src/k8s-academy/src/kubernetes && git log -1 --format='%H %ci' && kubectl version -o json | jq -r '.serverVersion.gitVersion'
```

Three citations, each re-checked with `sed -n '<line>,<line+6>p'` against **this** checkout rather than copied from your earlier notes — [the archaeology standard](../../strands/source-archaeology.md#drills) exists because 60 KB files renumber and [staging paths move](15-the-reconciler-and-its-packing-heuristic.md):

| Claim P6 could observe but not cite | File | Function | `file:line` |
|---|---|---|---|
| The EndpointSlice reconciler removes the endpoint | `.../endpointslice/reconciler.go` | | |
| kube-proxy's change tracker picks up the watch event | `pkg/proxy/endpointschangetracker.go` | | |
| The DNAT is reprogrammed | `pkg/proxy/nftables/proxier.go` | `syncProxyRules` | |

Add the fourth row this phase makes possible and P6 could not have asked for: **on this cluster, the third claim is no longer true** — `syncProxyRules` is not running anywhere, because [exercise 31](31-kube-proxy-replaced-by-map-lookups.md) deleted the DaemonSet that ran it, and the DNAT is now a `cilium bpf lb list` entry. Cite the line anyway, then say in one sentence what a citation to a function nothing is executing is worth. That sentence is the capstone's actual conclusion.

**Write down** — the three parts as three sections of one document: the ping with the lease directory beside it; the four policy-drop answers with the map dump and the monitor event pasted in; the citation table with the commit hash and the server version at the top. Then [the phase gate](../../phases/07-networking.md#gate), answered in writing rather than assumed.

**Footprint note** — nothing new. The phase ends where it ran all along: [`pair`](../../strands/lab-topologies.md#pair) at 5.0GB and [`forge`](../../strands/lab-topologies.md#build-guest) at 1536MB against [the ~9.5GB ceiling](../../strands/lab-topologies.md#ceiling), with roughly 3.0GB of margin never spent. **P7 resized nothing.** The one real pressure was tenancy rather than totals, and it was handled by [ordering three installs](README.md) instead of by growing a guest — which is the phase's footprint lesson and belongs in the write-up next to the technical ones.

**Teardown — the phase's, not just this exercise's**

```sh
cd ~/src/k8s-academy && git add -A && git commit -m "P7: labs, notes, and both build artifacts" && git push
ssh hopper 'cd factory && just tofu labs destroy'
```

Commit before destroying, and check that `build/07-cni-academy/` and `build/07-ebpf-academy/` are both in the commit — the two artifacts live on `forge`, which survives, but the notes that make them legible were written against a cluster that will not.

**The topology goes.** Nothing after this needs it: [P8](../../phases/08-storage.md) provisions its own, and P9 starts from a clean cluster because [the L7 and mesh layer it inherits](../../phases/07-networking.md#ecosystem) sits on top of the datapath you just finished and is deliberately untouched here.
