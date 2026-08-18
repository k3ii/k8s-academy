<a id="why-a-mutating-webhook-reruns"></a>
# Reinvocation, written as a claim before it is seen

**Claim** — a mutating webhook may be invoked more than once for a single request, exactly once more at most per pass, only if it asked to be, and only if a *later* webhook changed the object after it ran. You can state the rule, cite the bookkeeping that enforces the "at most" part, and predict which of three webhook configurations would re-run.

**Rests on** — [the chain citation](14-the-line-that-orders-the-chain.md). Reinvocation is the one place the two-phase rule needs a qualification, and it is worth having the unqualified rule solid first.

**Topology** — **none.** `forge` and [the clone](02-every-flag-located-in-source.md). No cluster is involved; **this is a reading exercise with a written deliverable**, and [the live demonstration is deferred](23-reinvocation-observed.md) until there are two webhooks to demonstrate it with.

**Do**

1. Read **KEP-492**'s webhook semantics section — the normative statement. Answer: what are the permitted values of `reinvocationPolicy`, what is the default, and what does the KEP promise about how many times a webhook may be called?

2. Read `staging/src/k8s.io/apiserver/pkg/admission/plugin/webhook/mutating/reinvocationcontext.go`. It is short. Answer three questions from the code:
   - What state does the reinvocation context hold *per webhook*, and what is the key?
   - Which method decides whether a second pass happens at all, and what is it looking at?
   - What stops a third pass? Name the mechanism, not the intent.

3. Read `plugin.go` and `dispatcher.go` in the same directory far enough to answer: **is the decision to re-run made per webhook or for the whole set?** The answer changes what a webhook author must assume.

4. Now predict. Three configurations, one request that all three webhooks want to mutate:

   | | `reinvocationPolicy` | Position in the list | Does it re-run? |
   |---|---|---|---|
   | A | `Never` (default) | first | |
   | B | `IfNeeded` | first | |
   | C | `IfNeeded` | last | |

   Fill in the third column, and for each write the *one condition* that decides it.

5. Write the falsifiable claim [the checklist wants](../../phases/03-api-machinery.md#checklist): one paragraph, ending in a `file:line`, stating why a mutating webhook may be invoked more than once. Make it a sentence someone could check and find wrong — *"because ordering is not guaranteed"* is not checkable and is also not the reason.

**Observe** — the only observation available here is the source itself. Confirm the citation resolves at your sha, the same way you did for [the chain](14-the-line-that-orders-the-chain.md):

```sh
cd ~/src/kubernetes
git log -1 --format='%h %cd %s' --date=short \
  -- staging/src/k8s.io/apiserver/pkg/admission/plugin/webhook/mutating/reinvocationcontext.go
```

**Expect** — B re-runs and C does not, for the same reason expressed twice: a webhook re-runs when the object changed *after* it saw it, and the last webhook in the list has nothing after it. A is the free one — `Never` is the default, so **most webhooks in the world are never reinvoked**, which is why the failure mode this rule prevents is rare and vicious rather than common.

The subtlety worth catching in step 3: the second pass is not "re-run the webhooks that asked" in isolation — the pass is over the set, and the per-webhook policy filters it. A webhook author must therefore assume their handler may see an object *they themselves already mutated*, which makes idempotency a requirement rather than good manners. That is the sentence your written claim should be built around.

**Write down** — the three-row prediction table with reasons, and the falsifiable claim with its `file:line`. [The live demonstration](23-reinvocation-observed.md) will either confirm the table or find your reading wrong, and being wrong here in writing first is the point of writing it first.

**Teardown** — nothing created. **The apiserver and etcd stay up. No topology is up.**
