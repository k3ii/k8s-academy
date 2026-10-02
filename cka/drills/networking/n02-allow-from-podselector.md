<a id="n02"></a>
# N2 — Allow from a label, and prove both the allow and the block

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Servicing and Networking / Network Policies

> **A test that only checks the allow is half a test.** Any policy lets *something* through; the question is what it stops. Every NetworkPolicy exercise here ends with two curls, one that works and one that hangs, and the one that hangs is the one being graded.

**Do**

1. Start from the N1 default-deny. Three pods: `app=client`, `app=other`, and `app=server`.
2. Write an ingress rule on `app=server` allowing `from: podSelector: app=client`. Test both clients. One works, one hangs.
3. **Learn the YAML trap that costs the most marks.** These are different:

   ```yaml
   from: [{podSelector: ..., namespaceSelector: ...}]   # AND -- that pod in that namespace
   from: [{podSelector: ...}, {namespaceSelector: ...}]  # OR -- either
   ```

   One list item with two selectors is an intersection; two list items is a union. Build both and prove the difference rather than memorising the sentence.
4. Add a `ports` restriction and confirm it narrows the allow rather than widening it. An empty `ports` means all ports, not none.
5. Change the client's label while everything is running. Access changes within seconds, with no restart. Policies select live.

**Observe**

```sh
kubectl exec client -- wget -qO- --timeout=3 http://server     # works
kubectl exec other  -- wget -qO- --timeout=3 http://server     # hangs
kubectl label pod other app=client --overwrite                 # now it works
kubectl describe netpol allow-client
```

**Done when** — both results are as predicted *before* running them, and you can explain the AND/OR difference without looking.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Build both forms, prove both. | 10 min |
| **2** | Three existing policies, one of which already allows more than you think. | 8 min |
| **3** | Cold, no notes. Deny plus allow from scratch. | 5 min |

**Teardown** — delete the namespace.

**See also** — **N1** is the deny this sits on; **N4** does the same job across namespaces.
