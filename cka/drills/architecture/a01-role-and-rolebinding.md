<a id="a01"></a>
# A1 — A Role and a RoleBinding for a ServiceAccount, proved rather than assumed

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Cluster Architecture, Installation and Configuration / RBAC

> **Writing RBAC is easy; proving it is the drill.** `kubectl auth can-i --as` turns a guess into a fact in two seconds, and it is the only way to check your work without logging in as someone else. Every RBAC task in the exam should end with it.

**Do**

1. A ServiceAccount in a namespace. A Role granting a narrow verb set on one resource. A RoleBinding tying them together.
2. **Prove it in the positive and the negative.** `can-i get pods --as=system:serviceaccount:<ns>:<sa>` should say yes; the same for `delete` should say no. A test that only checks the allow is half a test.
3. Get the subject string exactly right: `system:serviceaccount:<namespace>:<name>`. A typo here produces a confident `no` that looks like a broken Role, and this is the single most common way to lose the task.
4. Learn the three fields that actually matter in a rule: `apiGroups` — **`""`** for core resources, which is easy to forget and silently grants nothing — `resources`, and `verbs`. Add a subresource (`pods/log`) and see that it is granted separately from its parent.
5. `--as-group` for the group case, and `auth can-i --list --as=...` for the whole picture at once.

**Observe**

```sh
kubectl auth can-i get pods --as=system:serviceaccount:<ns>:<sa> -n <ns>
kubectl auth can-i delete pods --as=system:serviceaccount:<ns>:<sa> -n <ns>
kubectl auth can-i --list --as=system:serviceaccount:<ns>:<sa> -n <ns>
kubectl describe rolebinding <name> -n <ns>
```

**Done when** — the allow and the deny both come back as expected, and you wrote the subject string from memory.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Build all three objects with the docs open. | 10 min |
| **2** | Messy. The namespace already has two Roles; add a third without disturbing them. | 8 min |
| **3** | Cold, no notes. Include `pods/log` as a subresource. | 5 min |

**Teardown** — delete the namespace.

**See also** — **A2** is the cluster-scoped version, **A3** the hybrid, and **A6** is this drill run backwards from a 403.
