<a id="a-two-version-crd"></a>
# Two served versions, one stored, no webhook yet

**Artifact** — a `widgets.academy.k3ii.dev` CRD serving `v1` and `v2`, with `v1` as the storage version, structural schemas on both, and one CEL validation rule — installed and working *before* any conversion exists, so that what the conversion webhook adds is visible as a delta rather than assumed.

**Rests on** — [the policy exercise](16-a-policy-with-no-webhook.md)'s CEL, which is the same expression language `x-kubernetes-validations` uses. [Module 3.4's reading](../../phases/03-api-machinery.md#m3-4) is the KEP trio behind it.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [the chaos drill](26-3c1-corrupt-a-cabundle.md).

**Do**

1. Define the two versions so that conversion between them is **interesting rather than mechanical** — the same information, differently shaped:

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: apiextensions.k8s.io/v1
   kind: CustomResourceDefinition
   metadata: {name: widgets.academy.k3ii.dev}
   spec:
     group: academy.k3ii.dev
     names: {plural: widgets, singular: widget, kind: Widget, shortNames: [wg]}
     scope: Namespaced
     versions:
       - name: v1
         served: true
         storage: true
         schema:
           openAPIV3Schema:
             type: object
             properties:
               spec:
                 type: object
                 required: [size]
                 properties:
                   size:
                     type: string
                     enum: [small, medium, large]
                 x-kubernetes-validations:
                   - rule: "self.size != 'medium' || has(self.__comment__) == false"
                     message: "placeholder — replace with a rule of your own"
       - name: v2
         served: true
         storage: false
         schema:
           openAPIV3Schema:
             type: object
             properties:
               spec:
                 type: object
                 required: [dimensions]
                 properties:
                   dimensions:
                     type: object
                     required: [width, height]
                     properties:
                       width:  {type: integer, minimum: 1}
                       height: {type: integer, minimum: 1}
   YAML
   ```

   Replace the placeholder rule with one that means something — *"width and height must not both be 1"* expressed on v2, or a constraint on `size`. The point is to have written a CEL rule into a schema, not to have copied this one.

2. Create a `v1` Widget and read it back as `v1`.

3. Read the same object as `v2`. Predict what happens first.

4. Create a `v2` Widget.

5. Ask the CRD what it thinks its own state is:

   ```sh
   kubectl get crd widgets.academy.k3ii.dev -o jsonpath='{.status.storedVersions}{"\n"}'
   kubectl get crd widgets.academy.k3ii.dev -o jsonpath='{.status.conditions}' | jq -r '.[].type'
   ```

**Observe**

```sh
kubectl -n tenant get widgets.v1.academy.k3ii.dev -o yaml
kubectl -n tenant get widgets.v2.academy.k3ii.dev -o yaml
kubectl api-resources --api-group=academy.k3ii.dev
kubectl explain widget.spec --api-version=academy.k3ii.dev/v2
etcdctl_on_cp() { ssh zain@10.10.10.130 "sudo ETCDCTL_API=3 etcdctl \
  --cacert /etc/kubernetes/pki/etcd/ca.crt --cert /etc/kubernetes/pki/etcd/server.crt \
  --key /etc/kubernetes/pki/etcd/server.key $*"; }
etcdctl_on_cp get --prefix --keys-only /registry/academy.k3ii.dev
```

**Expect** — reading a `v1` object as `v2` returns it **unchanged**, with `apiVersion: academy.k3ii.dev/v2` stamped on it and `spec.size` still present. With no conversion strategy, `apiextensions` uses `None`, which rewrites the apiVersion field and nothing else. The object now fails its own `v2` schema — it has no `dimensions` — and the apiserver serves it anyway, because **validation happens on write, not on read.**

That is the failure conversion webhooks exist to prevent, and meeting it before building one is the point of doing this exercise first.

`status.storedVersions` contains `["v1"]` only. Note that it is a *list* and that entries are never removed automatically; a version cannot be dropped from `spec.versions` while it is still in `storedVersions`, and clearing it is a deliberate migration step. That constraint is the reason `storage: true` is a decision rather than a formality.

The etcd listing shows one key per object under `/registry/academy.k3ii.dev/widgets/`, regardless of which version you created it through — the v2 Widget is stored as v1, converted on the way in by `None`, which for these two schemas means its `dimensions` were **pruned**. Check it, and expect to lose data on step 4.

**Write down** — what `conversion: None` actually does, the pruning you observed on the v2 object, and one sentence on why `storedVersions` cannot be edited casually. This is the *problem statement* for [the conversion webhook](28-the-conversion-webhook.md); write it as one.

**Teardown** — delete the Widgets but **keep the CRD** — [the conversion webhook](28-the-conversion-webhook.md) attaches to it. **The topology stays.**
