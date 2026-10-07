<a id="a02"></a>
# A2 — A ClusterRole and ClusterRoleBinding over something a Role cannot reach

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Cluster Architecture, Installation and Configuration / RBAC

> **Some resources have no namespace, and therefore no Role can ever grant them.** Nodes, PersistentVolumes, Namespaces themselves, StorageClasses, CRDs. Writing a Role for one of these is accepted by the API server and grants precisely nothing — no error, no warning, no event. Recognising that shape instantly is what this drill buys.

**Do**

1. Pick a genuinely cluster-scoped resource. `kubectl api-resources --namespaced=false` lists every one of them, and that command is the real takeaway here.
2. **Make the mistake first, deliberately.** Write a Role granting `get nodes`, bind it with a RoleBinding, and prove with `auth can-i` that it does nothing. Sit with the silence — no object rejected it.
3. Now do it properly: ClusterRole plus ClusterRoleBinding. Re-prove.
4. Check the blast radius. A ClusterRoleBinding grants in **every** namespace, including ones that do not exist yet. Confirm by testing in two namespaces and then creating a third.
5. Look at what is already there. `kubectl get clusterroles` shows the built-ins — `view`, `edit`, `admin`, `cluster-admin` — and binding an existing ClusterRole is usually the right answer in an exam task, and much faster than authoring one.

**Observe**

```sh
kubectl api-resources --namespaced=false
kubectl auth can-i get nodes --as=system:serviceaccount:<ns>:<sa>
kubectl get clusterrole view -o yaml | head -30
kubectl describe clusterrolebinding <name>
```

**Done when** — you can say from the resource name alone whether a Role could ever grant it, and you reached for a built-in ClusterRole before writing one.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Make the Role mistake, then fix it. | 10 min |
| **2** | Grant read on nodes *and* on pods in all namespaces with one ClusterRole. | 8 min |
| **3** | Cold, no notes. Bind a built-in rather than authoring. | 5 min |

**Teardown** — delete the ClusterRoleBinding and ClusterRole by name. **Cluster-scoped objects do not go away with a namespace**, which is the most common piece of RBAC litter on a lab cluster.

**See also** — **A3**, where a ClusterRole is bound by a RoleBinding instead and the scope comes from the binding.
