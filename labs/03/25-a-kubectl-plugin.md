<a id="a-kubectl-plugin"></a>
# A client binary, and why it never gets a stage 2

**Artifact** — the phase's fourth build-track artifact: `kubectl-whoadmits`, a plugin in `build/03-kubectl-whoadmits/` that answers *"which admission webhooks and policies would match a write to this resource, in this namespace, by this user?"* — computed from the cluster's own registration objects, without making the write.

**This artifact has no stage 2, and that is correct rather than an omission.** [The artifact table says so](../../strands/build-mechanics.md#artifact-table) and [the phase file says so](../../phases/03-api-machinery.md#m3-3) rather than letting you notice. It is a client binary: it runs where `kubectl` runs, it is distributed by being on a `PATH`, and there is no deployment mechanic for it to practise. Every other build artifact in the curriculum ships into a cluster; this one is the control that shows what that step actually was.

**Rests on** — [the match conditions](24-matchconditions-stop-the-call.md), which established that matching has three independent layers. Reproducing all three is what makes this plugin non-trivial.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued from [the match conditions](24-matchconditions-stop-the-call.md). The plugin runs on `forge` against `pair`'s API.

**Build**

```
build/03-kubectl-whoadmits/
  go.mod
  main.go          flags, kubeconfig loading via genericclioptions
  match.go         the three matching layers
  match_test.go    table test: (config, request) → matched / not, with the reason
```

What it must implement:

1. **Discovery of the binary as a plugin.** The file must be named `kubectl-whoadmits`, be executable, and be on `PATH`; then `kubectl whoadmits` invokes it. Confirm with `kubectl plugin list` and note what that command does and does not check.
2. **Kubeconfig handling through `genericclioptions.ConfigFlags`**, not by parsing `--kubeconfig` yourself. This is the one place the plugin is expected to behave exactly like `kubectl`, including `--context` and `--namespace`.
3. **The three matching layers, reproduced faithfully**:
   - `rules` — group/version/resource/operation/scope, including the wildcard forms and the `*/*` case;
   - `namespaceSelector` and `objectSelector` — label selectors, evaluated against the live Namespace object;
   - `matchConditions` — CEL, evaluated against a synthesised `request` object.
   Reproduce the first two. For the third, **report that conditions exist and print them** rather than evaluating them, and say in the output that they are unevaluated — a plugin that silently skips a layer is worse than one that admits to it.
4. **Output**: one line per matching configuration, naming the object, the webhook name within it, its `failurePolicy`, and which layer matched. Plus a summary line: how many of the matches are `Fail` — because that count is the blast radius.

```sh
kubectl whoadmits pods -n tenant --verb=create --as=system:serviceaccount:tenant:default
```

**Gate** — [tier 2, a falsifiable written claim](../../strands/build-mechanics.md#gates). The claim: **"my `rules` matcher agrees with the apiserver's, cited to ⟨`file:function`⟩ under `staging/src/k8s.io/apiserver/pkg/admission/plugin/webhook/rules/`, including the ⟨named⟩ edge case."** Find at least one genuine edge case in that matcher — the wildcard handling and the subresource handling are both good hunting — and either reproduce it or state in your output that you do not.

**Verify from outside** — the plugin's answer must agree with what the cluster actually does. You have the ground truth already: both webhooks log every call.

```sh
kubectl whoadmits pods -n tenant --verb=create
kubectl -n academy-build logs deploy/academy-webhook --tail=0 -f &
kubectl -n academy-build logs deploy/academy-mutator --tail=0 -f &
kubectl -n tenant run agree --image=busybox --restart=Never
```

Then a case the plugin should get *right by saying no*:

```sh
kubectl whoadmits pods -n kube-system --verb=create
kubectl whoadmits configmaps -n tenant --verb=create
```

**Expect** — the plugin's list and the webhooks that actually logged a call are the same set. The two negative cases are the interesting ones: `kube-system` is excluded by `namespaceSelector`, `configmaps` by `rules`, and your output should name *which* layer said no, not merely that nothing matched. A tool that reports "no match" without the reason is not useful during the outage it exists for.

Expect to be wrong about at least one wildcard. `resources: ["*"]` and `resources: ["*/*"]` are not the same thing, `pods` and `pods/status` are different resources to the matcher, and `apiGroups: ["*"]` with `apiVersions: ["v1"]` is legal and matches more than you would guess.

**Write down** — the citation and the edge case, and one sentence, [which the checklist wants](../../phases/03-api-machinery.md#checklist): why this artifact has no stage 2. Write it in terms of what stage 2 *is* rather than what this binary lacks — the useful form is a definition, not an exemption.

**Footprint note** — none. The plugin is a client binary built and run on `forge`; it adds nothing to the cluster and nothing to the ceiling.

**Teardown** — delete the `agree` pod. **Keep the plugin on `PATH`** — [the chaos drill](26-3c1-corrupt-a-cabundle.md) is where it earns itself, because it answers *"what is currently able to block this write"* without attempting the write. **The topology stays.**
