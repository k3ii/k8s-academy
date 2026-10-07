<a id="a03"></a>
# A3 — A ClusterRole bound by a RoleBinding: cluster role, namespace scope

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Cluster Architecture, Installation and Configuration / RBAC

> **The ClusterRole says what; the binding says where.** This is the combination that confuses people and the one real clusters use most: define the permission set once, grant it in one namespace at a time. It is also the shape an exam task most often wants when it says "give this user read access to namespace X" and a built-in ClusterRole already exists.

**Do**

1. Bind the built-in `view` ClusterRole with a **RoleBinding** in one namespace. Prove the subject can read there and **not** in another. One object, two different answers depending on `-n`.
2. Compare directly against the A2 shape. Same ClusterRole, a ClusterRoleBinding instead, now readable everywhere. The ClusterRole did not change.
3. **The sharp edge.** If that ClusterRole also grants a *cluster-scoped* resource, the RoleBinding does **not** grant it — there is no namespace to scope it to, so that rule is simply dropped. Build this case and prove it: the subject gets the namespaced rules and silently not the others. This is the detail that separates knowing the pattern from knowing the rule.
4. Note `roleRef` is immutable. Changing which role a binding points at means deleting and recreating it, and discovering that under exam pressure is expensive.

**Observe**

```sh
kubectl create rolebinding r --clusterrole=view --serviceaccount=<ns>:<sa> -n <ns>
kubectl auth can-i get pods --as=system:serviceaccount:<ns>:<sa> -n <ns>        # yes
kubectl auth can-i get pods --as=system:serviceaccount:<ns>:<sa> -n other       # no
kubectl auth can-i get nodes --as=system:serviceaccount:<ns>:<sa>               # no, even via a ClusterRole that grants it
```

**Done when** — you can predict all four of those answers before running them, and explain the fourth.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Build it, prove the namespace boundary. | 10 min |
| **2** | Use a custom ClusterRole mixing namespaced and cluster-scoped rules; prove the drop. | 8 min |
| **3** | Cold, no notes, clock visible. Imperative `kubectl create rolebinding`. | 5 min |

**Teardown** — delete the namespaces and any ClusterRole you authored.

**See also** — **A1** and **A2** are the two pure cases this one sits between.
