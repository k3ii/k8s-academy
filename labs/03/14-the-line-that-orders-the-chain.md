<a id="the-line-that-orders-the-chain"></a>
# The two-method guarantee, cited and then watched

**Artifact** — a `file:line` citation in `admission/chain.go` that a hostile reader could check and find wrong, backed by a log the same apiserver produced showing every plugin's name in the order it ran. [Objective 2](../../phases/03-api-machinery.md#objectives) and [gate condition 2](../../phases/03-api-machinery.md#gate) both want this and want it without notes.

**Rests on** — [the plugin metrics](13-toggle-a-built-in-plugin.md), which showed the `admit`/`validate` label split without explaining it, and [the instrumented tree](08-the-order-of-calls-in-create-go.md).

**Topology** — **none.** `forge`, [the running apiserver](05-hand-start-an-apiserver.md).

**Do**

1. Read `staging/src/k8s.io/apiserver/pkg/admission/chain.go`. It is small enough to read completely. Answer, from the code and not from prose about it:
   - What concrete type is `chainAdmissionHandler`, and what does its `Admit` method iterate over?
   - What does its `Validate` method iterate over?
   - **Where in this file is it stated that all `Admit` calls finish before any `Validate` call begins?** Read carefully: it may not be stated *in this file at all*, and if it is not, the citation you want is in the caller.

2. Follow the answer to wherever it actually lives. `staging/src/k8s.io/apiserver/pkg/admission/interfaces.go` names the three interfaces; the caller that invokes both methods is in the handler path you already mapped in [the call-order note](08-the-order-of-calls-in-create-go.md). Produce **one** `file:line` that is the guarantee, and say in a sentence why the other candidates are not it.

3. Verify it the way [P2's archaeology standard](../../strands/source-archaeology.md#drills) requires — the line as it stands today, at your recorded sha:

   ```sh
   cd ~/src/kubernetes
   sed -n '<line>p' staging/src/k8s.io/apiserver/pkg/admission/chain.go
   git log -1 --format='%h %cd %s' --date=short -L <line>,<line>:staging/src/k8s.io/apiserver/pkg/admission/chain.go
   ```

4. Now make it observable. Add one log line inside each of the two methods, printing the handler's name:

   ```go
   klog.Infof("ACADEMY chain-admit %T", handler)
   klog.Infof("ACADEMY chain-validate %T", handler)
   ```

   Rebuild, restart, and create one Pod.

**Observe**

```sh
grep 'ACADEMY chain-' /tmp/apiserver.log | sed 's/.*ACADEMY //'
```

**Expect** — every `chain-admit` line appears before the first `chain-validate` line, for a single request. Not interleaved, not per-plugin paired. That is the rule, and this log is the only form of it that is not somebody's assertion.

Expect also to find that `chain.go` alone does **not** prove the rule. It provides two independent loops; nothing in the file forces one to complete before the other starts. The guarantee is that the caller invokes `Admit` and `Validate` as two separate phases — so the honest citation is the call site, and the honest sentence is *"`chain.go` gives you two phases; `<caller>:<line>` is what orders them."* Getting this right is the difference between a citation that survives checking and one that sounds right.

A second thing the log shows that no reading predicts: some plugin names appear in the `admit` list and again in the `validate` list. Cross-check against [the metrics](13-toggle-a-built-in-plugin.md) — same set, same explanation.

**Write down** — the citation, the sentence about why the other candidates are not it, and the plugin order from the log. [Gate condition 2](../../phases/03-api-machinery.md#gate) asks for this without notes, so write it in a form you would say out loud.

**Teardown** — delete the pod; keep the two chain log lines in the tree, they are cheap and [the reinvocation exercise](23-reinvocation-observed.md) reads them again. **The apiserver and etcd stay up. No topology is up.**
