<a id="managedfields-and-a-conflict"></a>
# Two owners, one field, one conflict

**Claim** — `managedFields` records ownership per field per manager, and a second manager writing a field the first owns is refused with a `409` naming both the field and the owner; you can make the same edit succeed three ways, each of which changes ownership differently.

**Rests on** — nothing built. [KEP-555](../../phases/03-api-machinery.md#m3-5) is the reading, and this is the only exercise in the phase where the interesting object is the metadata rather than the spec.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. Apply a Deployment as one manager and look at what the apiserver wrote about you:

   ```sh
   kubectl apply --server-side --field-manager=alice -f deploy.yaml
   kubectl get deploy web -o json | jq '.metadata.managedFields'
   ```

   Read the `fieldsV1` structure until you can say what `f:`, `k:` and `v:` prefixes mean. Do not skip this — the rest of the exercise is unreadable without it.

2. Have a second manager write a field the first owns:

   ```sh
   kubectl apply --server-side --field-manager=bob -f deploy-changed-replicas.yaml
   ```

3. Resolve it three ways, resetting between each, and record the `managedFields` after each:

   | Way | Command | What it does to ownership |
   |---|---|---|
   | Force | `--force-conflicts` | |
   | Yield | remove the field from alice's manifest and re-apply as alice, then apply as bob | |
   | Sidestep | `kubectl scale` | |

   The third is the one worth predicting first: `kubectl scale` is not an apply, so what manager name appears, and does the conflict machinery engage at all?

4. Do the same with a **list** field — add a container port as alice, a second as bob — and watch the `k:` keyed-list entries appear. Find where the key for a list is declared: it is not in the manifest, it is a marker on the Go type. Locate it in `staging/src/k8s.io/api/core/v1/types.go` and quote the line.

5. Then the trap. Apply as alice with a field **removed** from the manifest and observe what happens to it on the object. Predict first.

**Observe**

```sh
kubectl get deploy web -o json | jq '.metadata.managedFields[] | {manager, operation, fields: .fieldsV1}'
kubectl get deploy web --show-managed-fields -o yaml
```

**Expect** — the `409` names the field path and the owning manager in a message you can act on without reading any documentation, which is the single biggest practical difference from strategic-merge patch: the old model silently took the field.

Step 5 is the one that surprises people: with server-side apply, **removing a field from your manifest deletes it from the object**, because apply means "this is the complete set of fields I own". That is a correct implementation of the model and a common production incident, and meeting it here for two minutes is cheaper than meeting it later.

Step 3's third row: `kubectl scale` writes as a different manager with `operation: Update`, not `Apply`, and it does not conflict — an update takes ownership of what it changes. Two operation types, two ownership rules, one object.

**Write down** — the `fieldsV1` prefix meanings in your own words, the three ownership outcomes from step 3, the list-key marker line from step 4, and the step-5 result stated as a rule you would tell a colleague.

**Teardown** — `kubectl delete deploy web`. **The topology stays** — [APF](38-which-flowschema-caught-the-request.md) is next and needs a cluster under load.
