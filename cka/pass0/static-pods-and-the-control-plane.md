<a id="static-pods"></a>
# Pass 0 — static pods and the control plane: what runs where, and who starts it

**Pass 0** · **untimed** · [`pair`](../../strands/lab-topologies.md#pair) · Cluster Architecture · prerequisite for **TS05**, **TS06**

> **Worked live on 5 Oct**, from the [diagnostic](../plan.md#diagnostic)'s task T3, which was failed inside its box. Written in the shape [pass 0](../learning-pass.md#shape) specifies; every listing below was read off `pair-cp` rather than recalled.
>
> **Done when** you can say why static pods exist at all, what `kubectl delete` does to one, and why a broken *flag* and broken *YAML* leave you in two completely different places.

---

<a id="fixture"></a>
## 1. The fixture

`pair-cp`, a kubeadm control plane. One line was inserted into the `command:` list in `/etc/kubernetes/manifests/kube-controller-manager.yaml`:

```yaml
    - --vertical-pod-autoscaling=maybe
```

The binary does not accept that flag. It parses its arguments, rejects the unknown one, prints an error and exits non-zero — so the pod is created, attempted, and fails, over and over.

**Nothing else was touched.** No API object was edited, because there is no API object to edit, which is the whole subject of this document.

---

<a id="what-runs-where"></a>
## 2. What actually runs on a control-plane node

Three different mechanisms, and knowing which is which decides where you go when one breaks.

| Component | How it runs | Where it is defined |
|---|---|---|
| **`kubelet`** | a **systemd unit** on the host | `/etc/systemd/system/kubelet.service.d/` + `/var/lib/kubelet/config.yaml` |
| **`etcd`**, **`kube-apiserver`**, **`kube-controller-manager`**, **`kube-scheduler`** | **static pods** | `/etc/kubernetes/manifests/*.yaml` |
| **`kube-proxy`**, the CNI (`kube-flannel`), CoreDNS, everything else | ordinary **DaemonSets** and **Deployments** | the API, like any workload you create |

Read live from `pair-cp`:

```sh
$ ls /etc/kubernetes/manifests/
etcd.yaml  kube-apiserver.yaml  kube-controller-manager.yaml  kube-scheduler.yaml
```

```sh
$ k get ds -A
NAMESPACE      NAME                    DESIRED   CURRENT   READY
kube-flannel   kube-flannel-ds         2         2         2
kube-system    kube-network-policies   2         2         2
kube-system    kube-proxy              2         2         2
```

**So the control plane is four files and one systemd unit.** Everything else on the cluster, including the networking, is an ordinary workload that the four files make possible.

---

<a id="why"></a>
## 3. Why static pods exist — the bootstrap problem

A normal pod is created by asking `kube-apiserver` for it. So: **who asks `kube-apiserver` to start `kube-apiserver`?**

Nobody can. There is no API to ask yet. That circularity is the problem static pods solve:

> **The kubelet watches a directory on local disk and runs whatever pods it finds there, without consulting any API server.**

The directory is named in the kubelet's own config, which it reads from disk at startup:

```sh
$ grep staticPodPath /var/lib/kubelet/config.yaml
staticPodPath: /etc/kubernetes/manifests
```

So the boot order is: systemd starts the kubelet → the kubelet reads that directory → the kubelet starts `etcd` and `kube-apiserver` → the cluster exists. No chicken, no egg.

**This also means the control plane keeps running when the API is down.** A static pod does not need the API to stay alive; the kubelet is managing it locally. That is deliberate, and it is why a cluster can recover from its own API server crashing.

---

<a id="mirror"></a>
## 4. The mirror pod — visible, but not yours

You *can* see static pods in `kubectl`:

```sh
$ k get pods -n kube-system -o wide
NAME                              READY   STATUS    RESTARTS   AGE    IP             NODE
etcd-pair-cp                      1/1     Running   4          33d    10.10.10.130   pair-cp
kube-apiserver-pair-cp            1/1     Running   4          33d    10.10.10.130   pair-cp
kube-controller-manager-pair-cp   1/1     Running   0          30m    10.10.10.130   pair-cp
kube-scheduler-pair-cp            1/1     Running   4          33d    10.10.10.130   pair-cp
```

What you are reading is a **mirror pod**: a read-only copy the kubelet creates in the API *so that you can see it*. It exists for your benefit. The real pod is on the node, and the mirror is a reflection of it.

Three tells, all visible above:

- **The name is `<component>-<nodename>`.** `kube-controller-manager-pair-cp`. No random suffix, because there is no ReplicaSet generating one — compare an ordinary pod like `coredns-559f6c778d-b5zq9`. If a kube-system pod's name ends in a node name, it is a static pod.
- **The IP is the node's LAN address**, `10.10.10.130`, not a pod-network address like `10.244.0.11`. Control-plane components run with `hostNetwork: true`; they have to, since they are what the pod network depends on.
- **`k get deploy,rs -n kube-system` does not list them.** There is no controller behind them. Nothing owns them but the kubelet.

**Therefore `kubectl delete pod` does nothing useful.** The mirror disappears for a few seconds and the kubelet immediately recreates it from the file on disk, because the file is the source of truth and you did not change it. Delete it ten times and it comes back ten times.

> The same logic reads forwards: **to change a control-plane component, edit the file.** The kubelet notices within about twenty seconds and rebuilds the pod. There is nothing to apply and nothing to restart — and no `kubectl` command in the repair at all.

---

<a id="centre"></a>
## 5. The one that matters — a bad flag and bad YAML are different failures

This is the distinction the whole drill turns on, and it decides **whether you have a pod to debug**.

| | **Invalid flag** (valid YAML) | **Invalid YAML** |
|---|---|---|
| The kubelet | parses the file fine, creates the pod | **rejects the file** |
| `k get pods -n kube-system` | shows the pod, `CrashLoopBackOff` | **shows nothing at all** |
| `k describe` / `k logs` | work normally | nothing to describe |
| Where the answer is | the container's **logs** | the **kubelet's** journal on the node |

The second column is the nastier one by a distance, because `k get pods -n kube-system` returns a clean, confident list with one component simply **absent** — and an absence is far harder to notice than a failure. This is the third member of a family worth naming:

> **`k get all` omits half the kinds. A wrong namespace returns an empty list rather than an error. A rejected static pod manifest leaves no pod at all.** Three separate ways to get a clean empty answer that means nothing. *"I looked and there was nothing there"* is not evidence.

When the pod is missing, you leave `kubectl` and go to the node:

```sh
sudo journalctl -u kubelet -n 50 --no-pager      # the kubelet says why it rejected the file
sudo crictl ps -a | head                          # containers the kubelet ran, including dead ones
sudo crictl logs <container-id>                   # logs without going through the API at all
```

`crictl` talks to the container runtime directly. It is the tool for when `kubectl` cannot help you — which, on a control-plane fault, is exactly when you need it.

---

<a id="failure"></a>
## 6. What failure looks like

| What you see | What it means |
|---|---|
| `Back-off restarting failed container kube-controller-manager in pod kube-controller-manager-pair-cp_kube-system(…)` | The pod exists and is crash-looping. **You have a pod to work with** — `logs --previous`, and remember `-n kube-system`. |
| `k logs kube-controller-manager-pair-cp` → `pods "…" not found` | **You forgot `-n kube-system`.** This reads like "the pod is gone" and means "you looked in the wrong namespace". It is the single most expensive typo in control-plane troubleshooting. |
| The component is simply **missing** from `k get pods -n kube-system` | The kubelet rejected the manifest. Go to `journalctl -u kubelet` on the node. |
| `The connection to the server … was refused` | **`kube-apiserver` itself is down.** `kubectl` cannot tell you anything about anything. Everything from here is `crictl` and `journalctl` on the node. |
| Scheduler down: new pods sit **`Pending`** forever, existing pods untouched | Nothing is choosing nodes. See [TS06](../drills/troubleshooting/ts06-scheduler-or-controller-manager.md). |
| Controller-manager down: Deployments don't scale, nodes never go `NotReady`, nothing reconciles | Nothing is *reconciling*. The cluster looks frozen in its last good state rather than broken — see [node health](node-health-and-who-decides-ready.md). |

**That last row is the one to remember.** A dead controller-manager does not produce errors. It produces **stillness**, which looks like health.

---

<a id="say"></a>
## 7. Done when

With the terminal closed, you can say:

- which four components are static pods, and which three mechanisms run things on a control-plane node;
- why static pods have to exist, in terms of the bootstrap problem;
- what a mirror pod is, and the three ways to recognise one in `k get pods`;
- what `kubectl delete pod` does to a static pod, and why;
- why a bad flag leaves you a pod and bad YAML leaves you nothing, and where you go in the second case.

**See also** — [TS05](../drills/troubleshooting/ts05-broken-static-pod.md), the reflex drill for this; [TS06](../drills/troubleshooting/ts06-scheduler-or-controller-manager.md) for telling the two silent components apart; and [reading a crash](reading-a-crash.md) for the `describe`-then-`logs` ladder once you do have a pod.
