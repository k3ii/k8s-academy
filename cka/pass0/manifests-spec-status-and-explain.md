<a id="manifests"></a>
# Pass 0 — Manifests: `spec` against `status`, `explain`, and never typing YAML

**Pass 0** · **untimed** · [`pair`](../../strands/lab-topologies.md#pair) · **No single domain** — prerequisite for every drill that writes YAML

> **Worked live on 2 Oct**, following [the object chain](w05-w06-the-object-chain.md). Not a domain object: this is the mechanical skill under all of them, so it distorts no single score on [the diagnostic](../plan.md#diagnostic).
>
> **Done when** you can say what `--dry-run=client -o yaml` leaves out and why that matters, and why a selector mismatch is a hard error at creation but silent afterwards.

---

<a id="four-parts"></a>
## 1. Every object is a document with four parts

```yaml
apiVersion: apps/v1     # which API group and version owns this kind
kind: Deployment        # what sort of thing it is
metadata:               # name, namespace, labels, annotations
spec:                   # WHAT YOU WANT
status:                 # WHAT IS -- written by the cluster, never by you
```

The split between the last two is the entire design. **You only ever write `spec`.** Controllers read it, look at reality, and write `status` to report what they found. [The object chain](w05-w06-the-object-chain.md#rescue) restated exactly: `spec.replicas: 2` is the instruction, and the ReplicaSet kept acting until `status` agreed. A deleted pod never returning is simply that nothing in `spec` named it.

---

<a id="reading"></a>
## 2. Reading a live object

```sh
k create deployment web --image=nginx --replicas=2
k get deploy web -o yaml
```

<a id="twice"></a>
### The selector appears twice and must agree

```yaml
spec:
  selector:
    matchLabels: {app: web}       # "which pods are mine?"
  template:
    metadata:
      labels: {app: web}          # stamped on every pod this creates
```

Disagreement means a Deployment that creates pods and instantly disowns them. §5 is what the API does about that.

**The Deployment's selector is only `app=web`.** The ReplicaSet's was `app=web,pod-template-hash=5fc9f4bf66`, and that second label appears in no manifest — **the Deployment controller adds it** per ReplicaSet. That is precisely how two generations of ReplicaSet coexist during a rolling update without competing for pods.

<a id="nesting"></a>
### `template` is a Pod nested inside

```yaml
spec:              # the Deployment's spec
  template:
    spec:          # a POD spec
      containers:
```

`spec.template` is a complete Pod definition minus its name. Probes, volumes, resources, affinity, tolerations — all of it belongs **there**, not at the top level. Getting the nesting depth wrong is the commonest YAML failure under time pressure.

<a id="defaults"></a>
### Almost nothing in that output was typed

One command produced `progressDeadlineSeconds: 600`, `revisionHistoryLimit: 10`, `imagePullPolicy: Always`, `dnsPolicy`, `schedulerName`, `terminationMessagePath`, and:

```yaml
    strategy:
      rollingUpdate: {maxSurge: 25%, maxUnavailable: 25%}
```

Every object is defaulted like this on admission. **Therefore `k get -o yaml` output is a bad starting manifest** — it carries server-set identity and defaults that are noise in a file you intend to edit. §4 is the clean route.

(Those two `25%` values are **W7**'s whole subject. `resources: {}` — no requests or limits at all — is **W1**'s.)

<a id="status-is-the-table"></a>
### `k get` is a rendering of `status`

```yaml
status:
  replicas: 2
  readyReplicas: 2
  availableReplicas: 2
  updatedReplicas: 2
```

Those **are** the `READY / UP-TO-DATE / AVAILABLE` columns. `k get` fetches nothing different; it renders this document as a table, and the document always holds more. That is the reason to reach for `-o yaml` when a table looks wrong.

**Conditions answer two independent questions:**

```yaml
  conditions:
  - type: Available   status: "True"   reason: MinimumReplicasAvailable
  - type: Progressing status: "True"   reason: NewReplicaSetAvailable
```

*Is it serving?* and *is it making progress?* A stuck rollout reads `Progressing: False` / `ProgressDeadlineExceeded` while `Available` stays `True` — the old version still serves, the new one cannot start. One false and one true is a far sharper signal than any column.

> **Observed by accident:** the namespace had been deleted and rebuilt, yet the new Deployment's ReplicaSet hash was again `web-5fc9f4bf66`. The hash is a pure function of the pod template, not of the object's identity — new `uid`, same hash.

---

<a id="explain"></a>
## 3. Where field names come from

Not a browser. `kubectl explain` is always the version you are running and is permitted in the exam.

```sh
k explain deployment.spec.strategy
k explain deployment.spec.template.spec.containers.livenessProbe
k explain deployment.spec.template.spec.containers --recursive | head -40
```

- **It is a tree walked one dot at a time.** `FIELDS:` lists the children; append one and descend. No path has to be known in advance.
- **Capitalised types are doors.** `<string>` and `<integer>` are leaves; `<Probe>`, `<HTTPGetAction>`, `<DeploymentStrategy>` can be descended into.
- **It states defaults** — `failureThreshold` 3, `periodSeconds` 10, `timeoutSeconds` 1 — which is otherwise guesswork.
- **It states legal values** — `enum: Recreate, RollingUpdate` — so spelling and capitalisation never have to be recalled.
- It also answers questions not yet asked: a probe has exactly four mutually exclusive actions, `exec`, `httpGet`, `tcpSocket`, `grpc`. That is **W11**, for free.

---

<a id="generate"></a>
## 4. The one that matters — generate, never type

```sh
k create deployment api --image=nginx --replicas=3 $do > api.yaml
vi api.yaml
k apply -f api.yaml
```

`$do` is `--dry-run=client -o yaml`, from [the workspace](../workspace.md#shell). **`--dry-run=client` means: do not send this, show me what you would send.**

What comes back is **only what was asked for, plus the structural minimum** — no `uid`, no `resourceVersion`, no defaults, no populated `status`. An editable file rather than a dump.

Three details:

- **`strategy: {}`, `resources: {}`, `status: {}`** are empty placeholders. Delete them or leave them; the API fills them on apply.
- **There is no `namespace:` field.** It lands in whatever the current namespace is — generate in one, apply in another, and it goes somewhere unintended, quietly.
- **`selector.matchLabels` and `template.metadata.labels` come out matched**, which is exactly the thing hand-written YAML gets wrong.

---

<a id="failure"></a>
## 5. What failure looks like

<a id="admission"></a>
### Mismatched selector, at creation

```
The Deployment "api" is invalid: spec.template.metadata.labels:
Invalid value: {"app":"api"}: `selector` does not match template `labels`
```

Nothing was created; the API server refused at admission. Note it blames `spec.template.metadata.labels` — **not** the selector that was actually edited. API errors name a field, not an intent.

<a id="two-treatments"></a>
### The same inconsistency, two treatments

| | What happens |
|---|---|
| **At creation** | **Hard rejection.** Nothing created, the error names the field. |
| **By drift afterwards** ([relabelling a pod](w05-w06-the-object-chain.md#released)) | **Silence.** The pod is orphaned, the Deployment reports healthy, nothing reports a fault. |

Kubernetes validates the **document** on submission. It does not keep validating the **world** afterwards. A controller whose count is satisfied holds no opinion about a pod it no longer owns. That gap — strict at admission, silent at drift — is where a large share of real production strangeness lives.

<a id="immutable"></a>
### The selector cannot be changed later

Checked rather than recalled:

```
The Deployment "api" is invalid: spec.selector:
Invalid value: {"matchLabels":{"app":"api2"}}: field is immutable
```

A Deployment's **identity is fixed at birth**. Image, replicas, probes and resources are all mutable; *which pods it claims* is not. Changing a selector means delete and recreate, which means an outage — so it is a decision made once.

---

<a id="teardown"></a>
## 6. Teardown

```sh
k delete ns basics && rm -f d.yaml api.yaml
```
