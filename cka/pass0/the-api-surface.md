<a id="api-surface"></a>
# Pass 0 — The API surface: `api-resources`, scope, and finding things fast

**Pass 0** · **untimed** · [`pair`](../../strands/lab-topologies.md#pair) · **No single domain** — mechanics under every drill

> **Worked live on 4 Oct**, following [manifests](manifests-spec-status-and-explain.md). Where `apiVersion` strings come from, what namespaced actually means, and the reads that turn "where is it?" into one command.
>
> **Done when** you can say why `pods` is `v1` but `deployments` is `apps/v1` without looking, and name three kinds that `kubectl get all` does not show.

---

<a id="catalogue"></a>
## 1. The cluster hands you the catalogue

```sh
k api-resources
k api-resources | grep -i ingress
```

Five columns, four of which you need to write any YAML at all: `NAME`, `SHORTNAMES`, `APIVERSION`, `NAMESPACED`, `KIND`.

<a id="groups"></a>
### `apiVersion` is `<group>/<version>` — except when it isn't

```
deployments     apps/v1                      group "apps"
networkpolicies networking.k8s.io/v1         group "networking.k8s.io"
storageclasses  storage.k8s.io/v1            group "storage.k8s.io"

pods            v1                           no group at all
services        v1
configmaps      v1
secrets         v1
```

The bare `v1` entries are the **core group**, written without a slash. Not for any principled reason — they existed *before* API groups were invented. Pods, Services, ConfigMaps, Secrets, Nodes, PVs and PVCs are core; Deployments, ReplicaSets, DaemonSets and StatefulSets came later and live in `apps`.

**There is nothing to memorise here, and trying is a waste.** The move is `k api-resources | grep -i <thing>` and read the column.

<a id="scope"></a>
### `NAMESPACED` is a boolean that carries a lot

A **namespaced** object lives in a namespace and needs `-n` to find. A **cluster-scoped** object belongs to no namespace — `k get nodes -n whatever` silently ignores the flag, because there is nothing for it to mean.

```
persistentvolumes        false      ← shared infrastructure
persistentvolumeclaims   true       ← a team's claim on it

rolebindings             rbac.authorization.k8s.io/v1   true
clusterrolebindings      rbac.authorization.k8s.io/v1   false
```

That second pair is the whole Role/ClusterRole distinction: **same group, same version, one boolean apart.** Not a different mechanism — a different scope. The PV/PVC split is half of **S1**'s subject.

> `secrets` has **no short name**. There is no `k get sec`. People guess it, it fails, and it costs fifteen seconds at exactly the wrong moment.

---

<a id="get-all"></a>
## 2. What failure looks like — `all` does not mean all

```sh
k create ns scope && k config set-context --current --namespace=scope
k create deployment web --image=nginx
k create configmap settings --from-literal=mode=test
k create secret generic creds --from-literal=password=hunter2
k get all
```

The ConfigMap and the Secret are **not there**. Nor would be:

> ConfigMaps · Secrets · PVCs · ServiceAccounts · Ingresses · NetworkPolicies · Roles and RoleBindings · every CRD

`all` is a hardcoded category — roughly pods, services and the workload controllers. The failure is specific and expensive: run `k get all -n foo`, see nothing, conclude the namespace is empty. It was not empty.

```sh
k get deploy,svc,cm,secret,sa,pvc          # name the kinds; -o wide and --show-labels stack across all of them
```

The exhaustive version, worth seeing once and never using under a clock:

```sh
kubectl api-resources --verbs=list --namespaced -o name | paste -sd, | xargs -I{} kubectl get {} -n scope
```

<a id="alias"></a>
### Why that command needs `kubectl` written out

```
xargs: k: No such file or directory
```

**`k` is a shell alias.** Aliases exist only in the interactive shell — `xargs`, `watch`, `find -exec` and every script spawn separate processes that have never heard of it. Write `kubectl` in full inside any of them.

---

<a id="finding"></a>
## 3. The reads worth having in your fingers

```sh
k get pods -A                                        # every namespace
k get pods -A -o wide                                # + IP and NODE
k get pods -A --sort-by=.metadata.creationTimestamp
k get events -n <ns> --sort-by=.lastTimestamp        # events are unordered by default
```

<a id="two-networks"></a>
### `-o wide` shows you two different address spaces

```
kube-apiserver-pair-cp      10.10.10.130    ← the node's own IP
kube-proxy-cnjw6            10.10.10.130    ← the node's own IP
coredns-559f6c778d-b5zq9    10.244.0.11     ← a pod IP
web-5fc9f4bf66-44v8b        10.244.1.28     ← a pod IP
```

`10.10.10.x` is the real LAN; `10.244.x.x` is the cluster's pod network. **A pod showing its node's IP is running `hostNetwork: true`** — sharing the node's network stack rather than getting its own. The control plane and `kube-proxy` have no choice: they must work *before* pod networking exists. A chicken-and-egg constraint, readable off a column. (**N10** is this in detail.)

The shape is readable too: one each of `etcd`, `kube-apiserver`, `kube-controller-manager`, `kube-scheduler`, all on the control-plane node — those four **are** the control plane, running as ordinary-looking pods. `kube-proxy` and `kube-flannel` appear once per node, because they are DaemonSets.

<a id="events"></a>
### Events are the system explaining what it did

```
Scheduled           pod/web-...      assigned to pair-w1
SuccessfulCreate    replicaset/...   Created pod: web-...
ScalingReplicaSet   deployment/web   Scaled up replica set web-5fc9f4bf66 from 0 to 1
Pulling → Pulled → Created → Started
```

[The object chain](w05-w06-the-object-chain.md#chain), narrated by the cluster: the Deployment scaled a ReplicaSet, the ReplicaSet created a Pod, the scheduler assigned it a node, the kubelet pulled and started it. **Four different controllers, each reporting its own step.** Sorting by `.lastTimestamp` is what makes it legible.

---

<a id="teardown"></a>
## 4. Teardown

```sh
k delete ns scope
```
