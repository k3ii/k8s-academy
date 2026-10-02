<a id="b03"></a>
# B3 — Three stacked control planes, then lose one and keep quorum

**Build** · **Pinned** · **4 h** · [`ha`](../../../strands/lab-topologies.md#ha) · Cluster Architecture, Installation and Configuration / HA control plane

> **The only four-hour object in the plan, and the only one that needs its own Saturday.** It is also the only one that requires destroying `pair` and rebuilding it afterwards — two applies in one day — so it is costed outside the weeknight budget entirely. [The plan](../../plan.md#topology) puts it on Sat 10 Oct with an abort rule attached.

> **Quorum is arithmetic, and the arithmetic is the lesson.** Three members tolerate one loss. Two members tolerate **none** — a two-member cluster is strictly worse than a single one, because either failure is fatal and there are two things to fail. Being able to say that cold is worth more than any command here.

**Do**

1. Stand up the first control plane with `--upload-certs`, and understand what that flag does: it puts the shared CA material into a Secret with a short-lived key so the other two can fetch it instead of you copying files by hand.
2. Join the second and third with the control-plane join command. Watch the etcd member list grow from one to three. The certificate key expires in two hours — if the join fails on that, `kubeadm init phase upload-certs --upload-certs` regenerates it, and knowing that saves a rebuild.
3. **Stop one member.** Read what the remaining two do: the cluster stays writable, `kubectl` works through any surviving endpoint, and the etcd member list shows one unreachable. Nothing dramatic happens, which is the point.
4. **Stop a second.** Now read what the survivor does: it refuses writes, `kubectl get` may still answer from cache or may not answer at all, and the API server logs say so plainly. Note the difference between "the API server is down" and "the API server is up and cannot reach quorum", because they need different responses.
5. Bring both back and watch the cluster recover on its own.

**Observe**

```sh
sudo kubeadm init --control-plane-endpoint=<vip-or-name> --upload-certs --pod-network-cidr=<cidr>
kubectl get nodes
sudo ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key member list -w table
kubectl -n kube-system logs -l component=kube-apiserver --tail=50
```

**Done when** — three members listed, one stopped and the cluster still serving writes, two stopped and you can state precisely what the survivor will and will not do.

**The abort rule.** If this is not working by early afternoon, stop. Switch back to `pair` and rebuild from [the baseline](../../baseline.md#rebuild). A lost Saturday costs one build; a `pair` cluster that is still broken on Monday costs the rest of the week.

**Teardown** — the evening apply back to `pair`, which destroys `ha` entirely. **Everything B4 installed is gone with it** and must be reinstalled; budget that as part of the switch rather than discovering it on Monday.

**See also** — **TS9** rides this same Saturday and buys no topology switch of its own: it is quorum behaviour read as a *component* symptom. Nothing in either object restores an etcd snapshot.
