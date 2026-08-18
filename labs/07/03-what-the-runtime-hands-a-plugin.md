<a id="what-the-runtime-hands-a-plugin"></a>
# Capture the exact env vars and stdin JSON the runtime gives a plugin, from a real pod creation

**Artifact** — one captured `ADD` invocation: the six `CNI_*` environment variables and the network configuration JSON, taken **off a live pod creation on `.131`** rather than read out of `SPEC.md`. It is the input contract for [the plugin you write](08-add-and-del-that-cnitool-accepts.md), and having it on disk is what makes that plugin's first run a test rather than a guess.

**Rests on** — [exercise 2](02-the-kernel-both-sides-must-share.md) for the cluster. The spec question it answers — *what does the runtime hand a plugin on stdin?* — is [module 7.1's](../../phases/07-networking.md#m7-1) and the answer is meant to come from the wire, with `SPEC.md` open beside it as the thing being confirmed.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. Everything here happens on the **worker `.131`**; the control plane is left alone so that there is always one node whose pod networking is known-good.

**Setup** — first find out what is actually installed, rather than assuming. [The topologies strand is explicit](../../strands/lab-topologies.md#unverified) that nothing in it has been measured, and the CNI that `just play` leaves behind is exactly the kind of fact that has to be read off the node:

```sh
ssh zain@10.10.10.131 'ls -l /etc/cni/net.d/ /opt/cni/bin/ ; sudo cat /etc/cni/net.d/*'
```

Record the conflist's filename, its `cniVersion`, and the `type` of the **first** plugin in its `plugins` array. That first `type` is the binary you are about to wrap.

**Do** — put a shim in front of it. Replace the binary with a script that records its inputs and then execs the real thing, so the pod still gets a network and you get a transcript:

```sh
ssh zain@10.10.10.131
sudo -i
P=/opt/cni/bin/<the first plugin type>
mv $P $P.real
cat > $P <<'SHIM'
#!/bin/sh
L=/var/log/cni-shim.log
{ echo "=== $(date -Ins) ==="; env | grep ^CNI_ | sort; echo "--- stdin ---"; } >> $L
tee -a $L | $0.real
SHIM
chmod +x $P
```

Now create one pod on that node and let the runtime call it:

```sh
kubectl create ns cnispec
kubectl -n cnispec run probe --image=registry.k8s.io/pause:3.10 --overrides='{"spec":{"nodeName":"<worker node name>"}}'
kubectl -n cnispec get pod probe -o wide
```

**Observe**

```sh
ssh zain@10.10.10.131 'sudo cat /var/log/cni-shim.log'
```

**Expect** — one `ADD` block containing `CNI_COMMAND=ADD`, a `CNI_CONTAINERID` that is the **sandbox** id and not the container id, a `CNI_NETNS` that is a path under `/var/run/netns` or `/proc/<pid>/ns/net`, `CNI_IFNAME=eth0`, `CNI_ARGS` carrying `K8S_POD_NAMESPACE`/`K8S_POD_NAME`/`K8S_POD_INFRA_CONTAINER_ID`, and `CNI_PATH` listing the plugin directory. On stdin: the conflist's first plugin object, **not the whole conflist** — the runtime splits it and calls each plugin with its own config.

**Expect `CNI_ARGS` to be the surprise.** Nothing in `SPEC.md` requires those keys; they are a convention Kubernetes layers on top, which is the difference [`CONVENTIONS.md`](../../strands/source-reading.md#area-5-networking) exists to describe. A plugin that parses them is a Kubernetes plugin; a plugin that ignores them is a CNI plugin. [Yours](08-add-and-del-that-cnitool-accepts.md) will be the second kind, and [exercise 10](10-the-plugin-the-kubelet-calls.md) is where that choice becomes visible.

Then confirm the delete half, which is the one people forget exists:

```sh
kubectl -n cnispec delete pod probe --wait=true
ssh zain@10.10.10.131 'sudo grep -c "CNI_COMMAND=DEL" /var/log/cni-shim.log'
```

**Write down** — the captured `ADD` block verbatim, and beside it the three fields of the returned result the runtime cares about (`cniVersion`, `interfaces`, `ips`), which you can read from `SPEC.md`'s result section and will produce yourself in [exercise 8](08-add-and-del-that-cnitool-accepts.md). Answer in one line: **which of `CNI_CONTAINERID` and `CNI_NETNS` is the key your IPAM must be keyed on**, and why the other one is wrong.

**Footprint note** — one `pause` pod and a log file. No change to the 6.5GB the phase opened at.

**Teardown** — put the real binary back **before doing anything else**; a shim left in place will make [exercise 10](10-the-plugin-the-kubelet-calls.md)'s failures unreadable:

```sh
ssh zain@10.10.10.131 'sudo mv /opt/cni/bin/<type>.real /opt/cni/bin/<type>; sudo rm -f /var/log/cni-shim.log'
kubectl delete ns cnispec
kubectl -n cnispec get pods 2>&1 | tail -1     # the namespace should be gone
```

**The topology stays** — [exercise 4](04-eleven-kilobytes-of-endpointslice.md) is the next user of this cluster.
