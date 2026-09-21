<a id="crd-validation-rules-beta"></a>

# The post writes the disjoint-sets rule correctly in one table and negated in the next, forty-three lines apart and still uncorrected, links to the cost limits through a stray letter that is one of two such typos in 765 posts, and names two of the six fields a validation rule now has

**Post** — [Kubernetes 1.25: CustomResourceDefinition Validation Rules Graduate to Beta](https://kubernetes.io/blog/2022/09/23/crd-validation-rules-beta/),
2022-09-23.

11,522 bytes, 147 lines, three authors, all at Google: Joe Betz, Cici Huang and Kermit Alexander.
Ninth of 2022's thirteen `walk` verdicts. It is a reference post rather than a narrative one — four
tables of CEL expressions and two sections on cost — and that shape is why it is worth walking: a
table of rules is a set of claims each of which either holds or does not, and one of them does not.

**As written**

The announcement is one line, `:12`: validation rules for CustomResourceDefinitions have graduated
to beta in 1.25. Then an example schema at `:16-32` — a `spec` carrying `self.minReplicas <=
self.replicas && self.replicas <= self.maxReplicas` under `x-kubernetes-validations`, with a message
— and a table of five capabilities at `:37-43`.

Two arguments follow. *Why CEL*, `:48-53`: expressions inline into the schema, so the CRD is
self-contained, and they are compiled and type checked when the CRD is created rather than when a
custom resource is validated, so a bad expression is caught once and early. *Why not use validation
webhooks*, `:55-61`: three bullets, of which the third is the one with teeth — a webhook is a remote
call in the apiserver's request path, and every webhook installed lowers the control plane's
expected availability.

*Getting started*, `:63-84`, is advice rather than mechanism: scope rules close to the fields they
validate, use OpenAPI value validations where they exist, and declare size limits. It closes with a
four-row table of good practice, `:79-84`. Then transition rules, `:86-97`, built on `oldSelf`. Two
sentences from the paragraph at `:88` carry the whole of the post's model of when they run:

> A transition rule is a validation rule that references 'oldSelf'. The API server only evaluates
> transition rules when both an old value and new value exist.

Then the function libraries, `:100-117`, and *Resource use and limits*, `:119-137`, which is the
most careful part of the post. CEL is non-Turing-complete by design, so the apiserver can compute a
worst-case cost for an expression statically and refuse to accept a CRD whose cost is too high;
separately it tracks actual cost during evaluation and halts. The fix for both is the same, and
`:129` states it under a heading that reads *Good practice*: set `maxItems`, `maxProperties` and
`maxLength` on every array, map and string in a CRD schema.

*Future work*, `:139-143`, is two sentences. The first hopes for general availability in an upcoming
release. The second says a growing community is thinking about how to write extensible admission
controllers using CEL as a substitute for admission webhooks, and points at a Slack channel.

**What this exercise does not cover, and where it lives**

CEL in an admission policy rather than in a schema is [A rejection with no network hop in
it](../../labs/03/16-a-policy-with-no-webhook.md), and the four-way measurement of a policy against
a webhook doing the identical job is [Identical semantics, two failure
surfaces](../../labs/03/20-the-same-rejection-twice.md). `matchConditions` — CEL deciding whether
the apiserver dials at all — is [Narrowing that happens before the network call, not after
it](../../labs/03/24-matchconditions-stop-the-call.md). A CRD serving two versions, with one CEL
rule on it, already exists as [Two served versions, one stored, no webhook
yet](../../labs/03/27-a-two-version-crd.md); this row uses single-version CRDs so that nothing here
depends on conversion. Where a CRD's REST storage comes from is [Where a CRD's REST storage comes
from at runtime](../../labs/03/30-how-a-crd-gets-its-storage.md).

The transition-rule ground below is not a borrowing from elsewhere in the year. A second CEL post
arrives six days after this one, *Enforce CRD Immutability with CEL Transition Rules*, and the
census marks it `read` with its exercise booked back here — so `oldSelf` is this row's to carry, one
layer deeper than the tutorial that follows it.

The `ValidatingAdmissionPolicy` API that the closing paragraph predicts is a `read` verdict in this
year's census and a `walk` in the year that covers it at general availability; it is named here only
as the outcome of a forecast. The other broken link this exercise counts belongs to [the Pod
Security Admission exercise](../2021/09-pod-security-admission-beta.md), which found it first; this
row contributes the population it sits in, not the finding.

**The diff, and why**

**Retired by being agreed with.** `CustomResourceValidationExpressions` went stable at 1.29 and was
removed as a gate after 1.30. There is nothing to enable. Writing `x-kubernetes-validations` into a
CRD schema is now simply how CRDs are written, and the gate name appears in none of the five
generated `--feature-gates` help texts because there is no gate left to name. The post's *Future
work* wish — general availability in an upcoming release — was granted four releases later.

**Wrong when it was published.** The post's good-practice table tells you to require two sets to be
disjoint with `!self.set1.all(e, !(e in self.set2))`. That is the negation of the rule the same post
gives at `:41`, and it asserts the opposite: it passes when the sets share an element and fails when
they do not. Forty-three lines separate the correct form from the broken one. The documentation page
the post links to has it right, at `custom-resource-definitions.md:904`, so this was never the
project's mistake — it is the post's, and it is still there. Step 3 runs both rules against the same
two resources.

The same table row, `:84`, is also the only row in the post with no closing pipe, so it is the one
row a markdown table renderer has to guess at. `:73` is a bullet that stops mid-sentence — *Do not
use validation rules for validations already* — and was published that way. `:75` says *were
appropriate*. `:114` closes a quoted hostname it never opened. And `:125` links to the cost
documentation through `o/docs/tasks/...`, a target that is neither absolute nor external and
resolves to nothing. Five defects in one post, none of them corrected in four years.

**Overtaken by its own growth.** A validation rule had two fields the post could name, `rule` and
`message`. At the pin it has six: `messageExpression`, `reason`, `fieldPath` and `optionalOldSelf`
arrived afterwards, and each has its own subsection in the documentation. One of them contradicts
the post outright. `:88` says the apiserver only evaluates transition rules when both an old and a
new value exist; `optionalOldSelf: true` opts a transition rule into evaluation on creation, when
there is no old value at all. Step 4 creates a resource that a transition rule rejects.

**Never absorbed — the other direction.** Validation ratcheting has no counterpart anywhere in the
post's model of how validation works. `CRDValidationRatcheting` went alpha at 1.28, beta at 1.30 and
stable at 1.33, and it means the apiserver will accept an update to a resource that does not satisfy
the schema, provided the parts that fail were already failing and did not change. The post describes
validation as a predicate over a resource. Ratcheting makes it a predicate over a *diff*. Step 7 is
a resource that is invalid, accepted.

**The ladder**

Two gates, and neither is the feature's whole story on its own.

`CustomResourceValidationExpressions`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.23 – v1.24 |
| beta | `true` | — | v1.25 – v1.28 |
| stable | `true` | — | v1.29 – v1.30 |

The file declares `removed: true`. Three stages across eight releases, then gone: from 1.31 there is
no switch, and a cluster either has a version of the apiserver that evaluates CEL in CRD schemas or
a version that predates the feature entirely. The post announces the beta row, which ran for four
releases rather than the one its *Future work* section imagined.

`CRDValidationRatcheting`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.28 – v1.29 |
| beta | `true` | — | v1.30 – v1.32 |
| stable | `true` | — | v1.33 – |

This one is still live at the pin: stable, defaulting to `true`, with no `locked` field and no
closing version, so it remains settable. It is also named in none of the five generated help texts,
one of 119 live gates that are not. [The certificate
exercise](../2015/07-strong-simple-ssl-for-kubernetes.md) found three gates the kubelet's help text
calls beta while their files say stable, and [the exercise for the PodHasNetwork
post](08-pod-has-network-condition.md) counted thirty-four such disagreements among the apiserver's
149 named gates. This is the complementary population: not gates the help text gets wrong, gates it
does not mention at all.

The lab at v1.35 sits past the end of the first table and inside the last row of the second. Every
step below except the offline ones therefore runs against an apiserver where CEL validation cannot
be switched off and ratcheting cannot be switched off either, which is the state the post was
arguing towards without saying so.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 cores, at `10.10.10.180`. No
root shell is needed anywhere: steps 1 to 7 are `kubectl` against the apiserver, and the only
cluster-scoped objects are the CRDs, which the teardown removes by name. Custom resources are
created in a namespace called `crv`. Steps 8 to 10 need no cluster; they read the pinned checkout.
Every CRD below is in the group `bw-cel.example.com`, which nothing else in this repo uses.

**Do**

1. Establish the ground. The cluster's own OpenAPI is the authority on what a validation rule is,
   and it is a shorter list to read than the documentation.

   ```sh
   kubectl version -o json | jq -r '.serverVersion.gitVersion'
   kubectl get validatingwebhookconfigurations,mutatingwebhookconfigurations
   kubectl get --raw '/openapi/v3/apis/apiextensions.k8s.io/v1' \
     | jq -r '.components.schemas
              | to_entries[] | select(.key | endswith(".ValidationRule"))
              | .value.properties | keys[]'
   kubectl create ns crv
   ```

2. Install the post's own example and make it reject something. The rule and the message are
   `:26-27` verbatim; the three fields are required so that the expression never evaluates against
   an absent field.

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: apiextensions.k8s.io/v1
   kind: CustomResourceDefinition
   metadata:
     name: budgets.bw-cel.example.com
   spec:
     group: bw-cel.example.com
     scope: Namespaced
     names: {plural: budgets, singular: budget, kind: Budget}
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
               required: [minReplicas, replicas, maxReplicas]
               x-kubernetes-validations:
               - rule: "self.minReplicas <= self.replicas && self.replicas <= self.maxReplicas"
                 message: "replicas should be in the range minReplicas..maxReplicas."
               properties:
                 minReplicas: {type: integer}
                 replicas: {type: integer}
                 maxReplicas: {type: integer}
   YAML
   kubectl -n crv apply -f - <<'YAML'
   apiVersion: bw-cel.example.com/v1
   kind: Budget
   metadata: {name: ok}
   spec: {minReplicas: 1, replicas: 3, maxReplicas: 5}
   YAML
   kubectl -n crv apply -f - <<'YAML'
   apiVersion: bw-cel.example.com/v1
   kind: Budget
   metadata: {name: bad}
   spec: {minReplicas: 4, replicas: 3, maxReplicas: 5}
   YAML
   ```

3. The centrepiece. Install the post's capability rule from `:41` and its good-practice rule from
   `:84` as two CRDs whose rules differ in one character, then put the same two resources through
   each. Predict in writing which resource each rule accepts before you run it.

   ```sh
   for PAIR in "goodsets:GoodSet:self.set1.all(e, !(e in self.set2))" \
               "badsets:BadSet:!self.set1.all(e, !(e in self.set2))"; do
     PL=${PAIR%%:*}; REST=${PAIR#*:}; K=${REST%%:*}; RULE=${REST#*:}
     kubectl apply -f - <<YAML
   apiVersion: apiextensions.k8s.io/v1
   kind: CustomResourceDefinition
   metadata:
     name: ${PL}.bw-cel.example.com
   spec:
     group: bw-cel.example.com
     scope: Namespaced
     names: {plural: ${PL}, singular: ${PL%s}, kind: ${K}}
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
               required: [set1, set2]
               x-kubernetes-validations:
               - rule: "${RULE}"
                 message: "set1 and set2 must be disjoint"
               properties:
                 set1:
                   type: array
                   maxItems: 10
                   x-kubernetes-list-type: set
                   items: {type: string}
                 set2:
                   type: array
                   maxItems: 10
                   x-kubernetes-list-type: set
                   items: {type: string}
   YAML
   done
   sleep 3
   for K in GoodSet BadSet; do
     for CASE in "disjoint:[\"a\",\"b\"]:[\"c\",\"d\"]" "overlap:[\"a\",\"b\"]:[\"b\",\"c\"]"; do
       CN=${CASE%%:*}; S1=$(echo $CASE | cut -d: -f2); S2=$(echo $CASE | cut -d: -f3)
       echo "== $K / $CN"
       kubectl -n crv apply -f - <<YAML 2>&1 | tail -1
   apiVersion: bw-cel.example.com/v1
   kind: ${K}
   metadata: {name: ${CN}}
   spec: {set1: ${S1}, set2: ${S2}}
   YAML
     done
   done
   ```

4. Transition rules, and the sentence at `:88`. The first CRD is the post's `self == oldSelf`; the
   second sets `optionalOldSelf: true` and asks for an old value that cannot exist yet.

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: apiextensions.k8s.io/v1
   kind: CustomResourceDefinition
   metadata:
     name: pins.bw-cel.example.com
   spec:
     group: bw-cel.example.com
     scope: Namespaced
     names: {plural: pins, singular: pin, kind: Pin}
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
               required: [id]
               properties:
                 id:
                   type: string
                   x-kubernetes-validations:
                   - rule: "self == oldSelf"
                     message: "id is immutable"
   YAML
   kubectl -n crv apply -f - <<'YAML'
   apiVersion: bw-cel.example.com/v1
   kind: Pin
   metadata: {name: p1}
   spec: {id: "first"}
   YAML
   kubectl -n crv patch pin p1 --type=merge -p '{"spec":{"id":"second"}}' 2>&1 | tail -1
   kubectl apply -f - <<'YAML'
   apiVersion: apiextensions.k8s.io/v1
   kind: CustomResourceDefinition
   metadata:
     name: oldpins.bw-cel.example.com
   spec:
     group: bw-cel.example.com
     scope: Namespaced
     names: {plural: oldpins, singular: oldpin, kind: Oldpin}
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
               required: [id]
               properties:
                 id:
                   type: string
                   x-kubernetes-validations:
                   - rule: "oldSelf.hasValue() && self == oldSelf.value()"
                     message: "there was no old value"
                     optionalOldSelf: true
   YAML
   sleep 3
   kubectl -n crv apply -f - <<'YAML' 2>&1 | tail -1
   apiVersion: bw-cel.example.com/v1
   kind: Oldpin
   metadata: {name: o1}
   spec: {id: "first"}
   YAML
   ```

5. The claim at `:53`, that expressions are type checked when the CRD is created. Ask for a
   comparison that cannot hold and watch what the apiserver refuses: not the custom resource, the
   CustomResourceDefinition.

   ```sh
   kubectl apply -f - <<'YAML' 2>&1 | tail -3
   apiVersion: apiextensions.k8s.io/v1
   kind: CustomResourceDefinition
   metadata:
     name: typos.bw-cel.example.com
   spec:
     group: bw-cel.example.com
     scope: Namespaced
     names: {plural: typos, singular: typo, kind: Typo}
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
               required: [replicas]
               x-kubernetes-validations:
               - rule: "self.replicas == 'three'"
                 message: "never evaluated"
               properties:
                 replicas: {type: integer}
   YAML
   kubectl get crd typos.bw-cel.example.com 2>&1 | tail -1
   ```

6. The estimated cost limit, `:123-129`. One rule, applied twice: once over an array with no
   declared maximum and once over the same array with `maxItems`. The rule does not change. The
   static cost estimate does, and it is the estimate the apiserver refuses on.

   ```sh
   apply_costly() {
     kubectl apply -f - <<YAML 2>&1 | tail -2
   apiVersion: apiextensions.k8s.io/v1
   kind: CustomResourceDefinition
   metadata:
     name: costs.bw-cel.example.com
   spec:
     group: bw-cel.example.com
     scope: Namespaced
     names: {plural: costs, singular: cost, kind: Cost}
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
               required: [names]
               x-kubernetes-validations:
               - rule: "self.names.all(a, self.names.all(b, a == b || a != b))"
                 message: "pairwise"
               properties:
                 names:
                   type: array
                   $1
                   items:
                     type: string
                     maxLength: 32
   YAML
   }
   echo "== no maxItems"
   apply_costly ""
   echo "== with maxItems"
   apply_costly "maxItems: 10"
   ```

7. Ratcheting, which the post has no account of. Create a resource, then tighten the schema under it
   so that the stored resource no longer satisfies the rule, then change a field the rule does not
   look at.

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: apiextensions.k8s.io/v1
   kind: CustomResourceDefinition
   metadata:
     name: ratchets.bw-cel.example.com
   spec:
     group: bw-cel.example.com
     scope: Namespaced
     names: {plural: ratchets, singular: ratchet, kind: Ratchet}
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
               required: [size, label]
               properties:
                 size: {type: integer}
                 label: {type: string}
   YAML
   kubectl -n crv apply -f - <<'YAML'
   apiVersion: bw-cel.example.com/v1
   kind: Ratchet
   metadata: {name: r1}
   spec: {size: 3, label: "before"}
   YAML
   kubectl patch crd ratchets.bw-cel.example.com --type=json -p='[{"op":"add",
     "path":"/spec/versions/0/schema/openAPIV3Schema/properties/spec/properties/size/x-kubernetes-validations",
     "value":[{"rule":"self >= 10","message":"size must be at least 10"}]}]'
   sleep 3
   kubectl -n crv patch ratchet r1 --type=merge -p '{"spec":{"label":"after"}}' 2>&1 | tail -1
   kubectl -n crv patch ratchet r1 --type=merge -p '{"spec":{"size":4}}' 2>&1 | tail -1
   ```

8. Offline, against the pinned checkout. Both ladders, the gate's absence from the generated
   reference, and the fields a validation rule has.

   ```sh
   cd /path/to/kubernetes/website/content/en
   python3 - <<'PY'
   import yaml, glob, os, re
   G = "docs/reference/command-line-tools-reference/feature-gates"
   R = "docs/reference/command-line-tools-reference"
   def front(p):
       return yaml.safe_load(open(p).read().split("---")[1])
   for name in ("CustomResourceValidationExpressions", "CRDValidationRatcheting"):
       f = front(G + "/" + name + ".md")
       print(name)
       for s in f["stages"]:
           print(("  %-7s default=%-5s %s - %s" % (
               s["stage"].strip(), s["defaultValue"],
               s["fromVersion"], s.get("toVersion", ""))).rstrip())
       print("  removed:", f.get("removed"))
   ref = ""
   for fn in ("kube-apiserver.md", "kube-controller-manager.md", "kube-proxy.md",
              "kube-scheduler.md", "kubelet.md"):
       ref += open(R + "/" + fn, encoding="utf-8", errors="replace").read()
   live = []
   for p in sorted(glob.glob(G + "/*.md")):
       n = os.path.basename(p)[:-3]
       if n == "index":
           continue
       fm = front(p)
       if fm.get("removed") or fm["stages"][-1].get("toVersion"):
           continue
       live.append(n)
   gone = [n for n in live if not re.search(r"\b" + n + r"\b", ref)]
   print("live gates: %d, named in no help text: %d" % (len(live), len(gone)))
   print("CRDValidationRatcheting among them:", "CRDValidationRatcheting" in gone)
   A = "docs/reference/kubernetes-api/apiextensions/custom-resource-definition-v1.md"
   t = open(A, encoding="utf-8", errors="replace").read()
   blk = t.split("## ValidationRule")[1].split("\n## ")[0]
   print("ValidationRule fields:", sorted(set(re.findall(r"<td><code>([a-zA-Z]+)</code>", blk))))
   PY
   ```

9. Offline. The post's five defects, and the same rule in the page it links to.

   ```sh
   cd /path/to/kubernetes/website/content/en
   P=blog/_posts/2022/crd-validation-rules-graduate-to-beta.md
   D=docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions.md
   echo "-- the disjoint rule, both times the post writes it"
   grep -no '[!]*self\.set1\.all(e, !(e in self\.set2))' $P
   echo "-- and once in the page the post links to"
   grep -no '[!]*self\.set1\.all(e, !(e in self\.set2))' $D
   echo "-- rows with no closing pipe, and lines ending in a space"
   grep -c '^|.*[^|]$' $P
   grep -c ' $' $P
   echo "-- link targets that are neither absolute nor external"
   grep -o '](o[^)]*)' $P
   ```

10. Offline. Put the broken link in its population: every blog post at the pin, every absolute link
    into the documentation, and every target that is neither absolute nor external.

    ```sh
    cd /path/to/kubernetes/website/content/en
    python3 - <<'PY'
    import os, re
    root = "blog/_posts"
    md, odd_name = [], []
    for d, _, fs in os.walk(root):
        for fn in fs:
            if fn.endswith(".md"):
                md.append(os.path.join(d, fn))
            elif not re.fullmatch(r"\.[a-z0-9]{1,7}", os.path.splitext(fn)[1]):
                odd_name.append(os.path.join(d, fn))
    print("post files matched by --include='*.md': %d" % len(md))
    print("files under %s with no usable extension: %d" % (root, len(odd_name)))
    for p in sorted(odd_name):
        print("   " + p)
    docs_links, dead, odd = 0, 0, []
    for p in sorted(md):
        t = open(p, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"\]\(([^)\s]+)\)", t):
            u = m.group(1)
            if not u.startswith(("http://", "https://", "/", "#", "mailto:", "<")):
                odd.append((p, u))
            if u.startswith("/docs/"):
                docs_links += 1
                rel = u.split("#")[0].strip("/")
                if not any(os.path.exists(c) for c in
                           (rel + ".md", rel + "/index.md", rel + "/_index.md")):
                    dead += 1
    print("absolute /docs/ links: %d, of which unresolved: %d" % (docs_links, dead))
    print("link targets neither absolute nor external: %d" % len(odd))
    for p, u in sorted(odd):
        if re.match(r"^[a-z]/docs/", u):
            print("   %s\n     %s" % (os.path.basename(p), u))
    PY
    ```

**Expect**

Step 1 prints a v1.35 server and no webhook configurations at all — which is the post's third bullet
made into a precondition rather than an argument: everything below is rejected by the apiserver
itself, with nothing else installed. The field list is the one to keep. It should print six names:
`fieldPath`, `message`, `messageExpression`, `optionalOldSelf`, `reason` and `rule`. The post names
two of them.

Step 2 creates `ok` and rejects `bad`, and the rejection should quote the post's own message string
back at you — `replicas should be in the range minReplicas..maxReplicas.` — prefixed by the path the
rule is scoped to, `spec`. Note that the message is the author's, not the apiserver's: a CEL failure
with no `message` prints the expression instead. That is why the post puts a message on its very
first example.

Step 3 is the point of the exercise, and the two CRDs should behave in opposite directions. Against
`goodsets`, the disjoint resource is created and the overlapping one is rejected. Against `badsets`
— which is the rule the post's good-practice table tells you to use — the overlapping resource is
created and the disjoint one is rejected with the message `set1 and set2 must be disjoint`. A rule
whose message names the constraint it enforces, enforcing its negation, is the worst shape a broken
validation can take: it fails closed on the correct input and open on the wrong one, and it tells
you it is doing the right thing while it does it.

Step 4 should reject the patch to `p1` with `id is immutable`, which is the post's claim holding
exactly as written. Then `o1` should fail to create, with `there was no old value`. Read that second
failure against `:88`. A transition rule was evaluated on a creation, where there is no old value —
which is precisely what the post says the apiserver does not do. The sentence was true when it was
written and `optionalOldSelf` made it false; the field is gated on ratcheting, so the version that
made it false is 1.28 at the earliest and 1.30 by default.

Step 5 should fail at `kubectl apply`, not later, and the `kubectl get crd` that follows should
report `NotFound`. The error names the expression and the mismatch between an integer and a string.
This is the whole of the argument at `:53` in one command: the compile happens when the CRD is
written, so a typo in a rule costs the CRD author a failed apply rather than costing every future
user of that resource a confusing runtime error. Record the exact wording; it is more specific than
the post suggests.

Step 6 should refuse the first apply and accept the second. The message names the estimated cost and
the limit it exceeded, and the only difference between the two attempts is `maxItems: 10` on an
array the rule traverses twice. Note what this means for the good practice at `:129`: it is not
advice about efficiency, it is the difference between a CRD that installs and one that does not. If
the first apply succeeds on your cluster, the rule is not expensive enough — raise the nesting or
drop `maxLength` from the items and try again, and say which change was needed.

Step 7 is the behaviour with no counterpart in the post. The CRD accepts the new rule even though
`r1` already violates it. The patch that changes only `label` should be accepted, because the field
the rule reads did not change. The patch that changes `size` to 4 should be rejected, because it did
change and 4 is still not 10. Confirm the stored object afterwards: `kubectl -n crv get ratchet r1
-o jsonpath='{.spec.size}'` should still print 3. A resource that the schema says is invalid,
sitting in etcd, being updated.

Step 8 prints the two ladders and three facts:

```
CustomResourceValidationExpressions
  alpha   default=False 1.23 - 1.24
  beta    default=True  1.25 - 1.28
  stable  default=True  1.29 - 1.30
  removed: True
CRDValidationRatcheting
  alpha   default=False 1.28 - 1.29
  beta    default=True  1.30 - 1.32
  stable  default=True  1.33 -
  removed: None
live gates: 257, named in no help text: 119
CRDValidationRatcheting among them: True
ValidationRule fields: ['fieldPath', 'message', 'messageExpression', 'optionalOldSelf', 'reason', 'rule']
```

Forty-six per cent of the live gates are named in none of the five help texts. That is a larger
number than it first looks, and it bounds what the generated reference can be used for: it is a list
of the gates those five binaries accept on the command line, not a list of the gates that exist.
`CRDValidationRatcheting` is in it, which is why step 7's behaviour cannot be discovered by reading
the reference at all.

Step 9 prints the post's defects as line numbers:

```
-- the disjoint rule, both times the post writes it
41:self.set1.all(e, !(e in self.set2))
84:!self.set1.all(e, !(e in self.set2))
-- and once in the page the post links to
904:self.set1.all(e, !(e in self.set2))
-- rows with no closing pipe, and lines ending in a space
1
2
-- link targets that are neither absolute nor external
](o/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#resource-use-by-validation-functions)
```

One character, one line apart in the output and forty-three in the file. The one row with no closing
pipe is `:84`, the same row: a table cell that is malformed and wrong at once. The two lines ending
in a space are `:61` and `:73`, and `:73` is the bullet that stops mid-sentence, which suggests the
trailing space is where the rest of it was going to go.

Step 10 gives the link its population:

```
post files matched by --include='*.md': 765
files under blog/_posts with no usable extension: 2
   blog/_posts/2022/kubernetes-1.23-release-interview
   blog/_posts/2022/kubernetes-1.24-release-interview
absolute /docs/ links: 1506, of which unresolved: 365
link targets neither absolute nor external: 97
   pod-security-admission-beta.md
     h/docs/concepts/security/pod-security-standards/#profile-details
   crd-validation-rules-graduate-to-beta.md
     o/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#resource-use-by-validation-functions
```

Three numbers and a caveat. Twenty-four per cent of the archive's absolute links into the
documentation no longer resolve, so a dead `/docs/` link is the archive's normal condition and not
worth a finding on its own. Ninety-seven targets are neither absolute nor external, and most of
those are GitHub handles written as though they were links. But exactly two of the ninety-seven are
a single stray letter in front of `/docs/`, and one of them is this post's. The other is the Pod
Security Admission post, where [the exercise for it](../2021/09-pod-security-admission-beta.md) at
`:151-156` recorded it as still unfixed. Two posts, four years apart, the same typo, neither
corrected.

The caveat is the first two lines. The census for this year counts 69 posts and the manifest counts
767 across the archive, but a glob for `*.md` finds 765 files — because two of 2022's posts are
stored with no file extension. `--include='*.md'` is the standing idiom in this repo and in four of
this year's other exercises, and it silently skips those two. They are release interviews, both
`read` verdicts, so nothing here turns on them. The instrument reading two is the finding: a
measurement over the archive is a measurement over what the glob reaches.

**Read on**

1. `custom-resource-definitions.md`, the page the post links to, at `:783-1388`. It is the post's
   subject grown to six hundred lines. Read `:1096-1211` for the field-by-field reference, four of
   whose five sections describe fields that did not exist when the post was written, and `:720-782`
   for ratcheting. The page has a defect of its own worth noticing at `:1198-1199`, where a sentence
   about `optionalOldSelf` has been swallowed by a link: *a more control tool [than provided by the
   default equality based behavior of](#validation-ratcheting)*. Documentation about a correction
   mechanism, needing one.

2. `docs/reference/using-api/cel.md`, one of the six files at the pin that mention
   `x-kubernetes-validations` — the other five being this post, the post a week after it, the
   concept page, the API reference and the gate file itself. It is the cross-cutting account of
   where CEL is used in Kubernetes, which did not exist in a form worth linking when this post was
   written. Read it for how many places the answer now is, and note which of them the post's closing
   paragraph predicted.

3. The good-practice table at `:79-84` against what the documentation kept. Three of its four rows
   became ordinary advice on the concept page; the fourth is the broken one. Work out from the
   surrounding text whether the negation was a transcription slip or a misreading of `all`, and then
   ask which of the two a reviewer would have been more likely to catch.

4. The 119 live gates that none of the five generated help texts name, against the 149 that the
   apiserver's help text alone does. Step 8 counts the first number and [the exercise for the
   PodHasNetwork post](08-pod-has-network-condition.md) counts the second; the interesting question
   is what the 119 have in common. Start by splitting them on whether the gate is read by a
   component that has no `--feature-gates` page of its own.

5. *Unanswerable from the pin:* which release made the post's link broken, and whether it was ever
   correct. The pinned tree holds one revision of one file, so the stray `o` is all there is; the
   history that would say whether it shipped that way is in a repository this archive does not read.
   Also unanswerable: whether anybody has ever pasted the `:84` rule into a production CRD. The rule
   fails safe in the sense that it rejects valid input loudly — which is the only reason to think
   somebody would have noticed.

**Teardown**

```sh
kubectl delete ns crv
kubectl delete crd budgets.bw-cel.example.com goodsets.bw-cel.example.com \
  badsets.bw-cel.example.com pins.bw-cel.example.com oldpins.bw-cel.example.com \
  costs.bw-cel.example.com ratchets.bw-cel.example.com --ignore-not-found
```

`typos.bw-cel.example.com` is not in that list because step 5 succeeds by failing to create it. If
the delete reports it missing, step 5 did what it should.
