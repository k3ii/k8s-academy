<a id="kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community"></a>
# The option this post buries in bullet two is still the default eleven years later, and its replacement is locked on

**Post** — [Kubernetes 1.1 Performance upgrades, improved tooling and a growing
community](https://kubernetes.io/blog/2015/11/kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community/),
2015-11-09, Kubernetes 1.1 — the project's second release, announced on the first day of the first
KubeCon.

**As written** — a release announcement, eight bullets and three vendor quotes. The bullets:

1. **"Substantial performance improvements"** — "later this week, we will be sharing examples of
   running thousand node clusters, and running over a million QPS against a single cluster."
2. **"Significant improvement in network throughput"** — "we have included **an option** to use
   native IP tables offering an 80% reduction in tail latency, an almost complete elimination of
   CPU overhead and improvements in reliability and system architecture ensuring Kubernetes can
   handle high-scale throughput well into the future."
3. **Horizontal pod autoscaling (Beta)** — pods scale "based on CPU usage", linked to
   `kubernetes.io/v1.1/docs/user-guide/horizontal-pod-autoscaler.html`.
4. **HTTP load balancer (Beta)** — "route HTTP traffic based on the packets introspection", so
   `http://foo.com/bar` and `http://foo.com/meep` reach different services. Linked to the Ingress
   object under the same versioned docs tree.
5. **Job objects (Beta)** — "runs a workload, restarts it if it fails, and keeps trying until it's
   successfully completed", linked twice: once to `kubernetes/kubernetes/blob/master/docs/user-guide/jobs.md`
   and once to the versioned docs.
6. **"New features to shorten the test cycle"** — "the ability to run containers interactively, and
   improved schema validation to let you know if there are any issues with your configuration files
   before you deploy them."
7. **"Rolling update improvements"** — "rolling updates now ensure that updated pods are healthy
   before continuing the update."
8. **"And many more"**, pointing at the GitHub release notes.

Then KubeCon — "some 400 community members along with dozens of vendors" — and three CEOs. CoreOS
is "betting our major product, Tectonic … on Kubernetes because we believe it is the future of the
data center." Univa has "selected Kubernetes as a foundational element of our new Navops suite."
Redapt is "a trusted advisor."

**As it runs now** — take the bullets in order, because the announcement's own ranking turns out to
be almost exactly backwards.

1. **The scale numbers are historical.** The pin states the supported envelope as four
   simultaneous limits: no more than 110 pods per node, 5,000 nodes, 150,000 total pods, 300,000
   total containers. The post's thousand-node cluster was a fifth of today's ceiling and was
   announced as a forthcoming demonstration; the ceiling is now a documented support statement with
   a per-node cap the post never mentions.
2. **The option became the default and never left.** `--proxy-mode` on Linux accepts `iptables`
   (the default), `ipvs` and `nftables`. `userspace` — the mode iptables was an *option* against —
   is not a valid value at all; it was moved out of tree. Eleven years, four proxy
   implementations attempted, and bullet two's "option" is still what your cluster is running.
3. **HPA is stable and no longer only about CPU.** The versioned docs URL is gone with the whole
   `/v1.1/` tree. The API's own history — `autoscaling/v1` still being served and converted on read
   — is [exercise 01's ending](01-introducing-kubernetes-v1beta3.md); do not re-derive it here.
4. **The HTTP load balancer is stable, frozen, and no longer recommended.** Ingress went GA in
   v1.19, and the pin now opens the Ingress page with: "The Kubernetes project recommends using
   Gateway instead of Ingress. The Ingress API has been frozen. … The Ingress API is no longer
   being developed, and will have no further changes or updates made to it." A beta feature
   announced in 2015 reached GA, stopped moving, and was superseded by an API that lives outside
   the cluster as CRDs — see [exercise 08's step 8](08-using-kubernetes-namespaces-to-manage.md)
   for what that means for a namespace.
5. **Job is stable, and the sentence describing it was always wrong.** "Keeps trying until it's
   successfully completed" is not what a Job does: `.spec.backoffLimit` "is set by default to 6",
   after which the Job is marked failed and stops. The post describes unbounded retry; the API has
   shipped bounded retry since it was beta.
6. **Both halves landed, and both are elsewhere.** Interactive `kubectl run` is
   [exercise 09's section 1](09-some-things-you-didnt-know-about-kubectl.md), including the `-t`
   promise the post's own release kept. Schema validation became *server-side* field validation —
   the client stopped guessing and started asking — and the gate that carried it is stable and then
   deleted, which is what the ladder below shows.
7. **The command it improved no longer exists.** `kubectl rolling-update` is not in the pin's
   command reference; `kubectl rollout` is. Rolling updates moved from a client-side loop into the
   Deployment controller, where `maxSurge`, `maxUnavailable` and `minReadySeconds` are fields rather
   than a running kubectl process you must not interrupt.
8. **The dead links are the same class as the SSL post's.** `kubernetes/kubernetes/blob/master/docs/user-guide/jobs.md`
   is the in-repo docs tree that was moved to the website;
   [exercise 07](07-strong-simple-ssl-for-kubernetes.md) has the explanation.

And the vendors. Searching the pin's entire documentation set: **Tectonic — zero mentions. Navops —
zero. Univa — zero. Redapt — zero.** CoreOS appears eight times, none of them about Tectonic. Three
CEOs staked their product lines on this release, and the project's own documentation eleven years
later contains no trace of any of the three products. That is not a criticism of the bets; two of
the three companies were right about Kubernetes and wrong about what they would sell on top of it.

**The diff, and why** — this is the sweep's cleanest instance of ***the announcement is not the
event***, and the mechanism is visible in the bullet order.

The post ranks its eight items the way a launch ranks them: scale first, then throughput, then the
three beta APIs with their own headings and links, then tooling, then rolling updates. If you
predicted durability from that ranking you would be wrong in both directions at once. The two items
that mattered most eleven years later are bullet two — a parenthetical *option*, offered as one way
to configure a component, which became the permanent default of every Kubernetes network — and
bullet six's second half, one clause in a sentence about developer workflow, which became the
API-server contract for every manifest anyone applies. The three items given headings, links and
the word *Beta* all reached GA and then stopped being where the interesting work was: HPA moved to
metrics the post did not imagine, Ingress was frozen in favour of an out-of-tree API, and Job's
one-sentence description was inaccurate on the day it shipped.

Why the option won is worth being precise about, because "iptables was faster" is the remembered
version and it is not the reason it lasted. The userspace proxy put a userspace process in the path
of every packet, and iptables moved that into the kernel — that is the 80% and the CPU elimination,
and it is a one-time win the post correctly claims. What made iptables the *default for a decade*
is different: it required nothing of the operator and nothing of the kernel beyond what was already
there. IPVS was faster still on large services and arrived as a gate in v1.8; it is now deprecated,
and the pin states its end date — "disabled by default from Kubernetes v1.40", "fully removed in
Kubernetes v1.43" — along with the reason it lost, which is that it needed a kernel subsystem the
node might not have. nftables is better-shaped than both — it replaces linear chain traversal with
maps — and it took four releases from alpha to a *locked* stable. The default did not move because
being slightly slower everywhere beats being faster only where an extra kernel module is loaded,
and the pressure here is the same one behind
[CRI](03-docker-and-kubernetes-and-appc.md) and
[logging](04-cluster-level-logging-with-kubernetes.md), seen once more: the project keeps whatever
works without asking permission of a component it does not own.

There is a second lesson in the ladder, and it is the reason a release announcement is a good place
to learn to read one. Four of the six gates below are stable-and-then-deleted or deprecated. A gate
whose last row says `stable` and whose file says `removed: true` did not regress — it graduated and
the switch was thrown away, which is success. A gate whose only row says `deprecated` is a feature
being wound down. And a gate whose stable row carries `locked: true` cannot be turned off at all.
Three different endings, none of them announced in a blog post, all of them legible in four columns.

Release facts and the pressure behind each are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

**The ladder** — six gates carry bullets two and six between them. Transcribed per gate, which is
the only way the two IPVS entries make sense.

`NFTablesProxyMode`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.29 – v1.30 |
| beta | `true` | — | v1.31 – v1.32 |
| stable | `true` | `true` | v1.33 – |

`MinimizeIPTablesRestore`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.26 – v1.26 |
| beta | `true` | — | v1.27 – v1.27 |
| stable | `true` | — | v1.28 – v1.29 |

`IPTablesOwnershipCleanup`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.25 – v1.26 |
| beta | `true` | — | v1.27 – v1.27 |
| stable | `true` | — | v1.28 – v1.29 |

`SupportIPVSProxyMode`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.8 – v1.8 |
| beta | `false` | — | v1.9 – v1.9 |
| beta | `true` | — | v1.10 – v1.10 |
| stable | `true` | — | v1.11 – v1.20 |

`KubeProxyIPVS`

| stage | default | locked | releases |
|---|---|---|---|
| deprecated | `true` | — | v1.37 – |

`ServerSideFieldValidation`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.23 – v1.24 |
| beta | `true` | — | v1.25 – v1.26 |
| stable | `true` | — | v1.27 – v1.31 |

Four of these files declare `removed: true`: `MinimizeIPTablesRestore`, `IPTablesOwnershipCleanup`,
`SupportIPVSProxyMode` and `ServerSideFieldValidation`. None declares `former_titles`.

Read the IPVS pair together and separately, because between them they are the best argument for
transcribing gates rather than features. `SupportIPVSProxyMode` has **two beta rows** — beta
arrived defaulted off in v1.9 and flipped on in v1.10, the same stage twice with different
defaults — and it was removed after v1.20, having done its job of introducing the mode.
`KubeProxyIPVS` is a *different gate* for the same proxy mode, with one `deprecated` row, and it
faces the opposite direction: the pin explains that when `ipvs` is disabled by default at v1.40,
this gate is how you **re-enable** it, until the mode is removed at v1.43. One gate switched a mode
on while it was new; the other will switch it back on while it is dying. A per-feature table would
have had to average those into one misleading row.

Note also a disagreement of the kind [exercise 07](07-strong-simple-ssl-for-kubernetes.md) meets
from a different angle. The `KubeProxyIPVS` gate file dates its `deprecated` stage from **v1.37**;
the prose page for the mode is marked deprecated for **v1.35**. Two releases apart, at the same
commit. Cite both and say they disagree — the gate file governs what your binary accepts, and the
prose page is what a reader will find first.

**No gate** — nothing gates the four scale limits, the `--proxy-mode` flag's list of accepted
values, Ingress's freeze, or Job's `backoffLimit` default. For those the instruments are the
kube-proxy binary's own flag help (steps 3 and 4), `kubectl api-resources` and
`kubectl explain` (steps 6 and 7), and — for the scale limits — nothing you can run on this lab at
all, which step 8 says out loud rather than faking.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo) — the guest from
[the kubectl exercise](09-some-things-you-didnt-know-about-kubectl.md) is still up; keep it. If you
are starting here, bring it up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, then `ssh zain@10.10.10.180`.

**Do**

1. Find out which of bullet two's descendants your cluster actually chose, and where it wrote it
   down:

   ```sh
   kubectl -n kube-system get cm kube-proxy -o jsonpath='{.data.config\.conf}' \
     | grep -E '^mode|^ipvs:|^nftables:' 
   sudo iptables-save | grep -c '^-A KUBE-'
   sudo nft list tables 2>/dev/null | grep -c kube
   ```

2. Measure the shape of the thing the post claims 80% on. Rules are per service, so make some and
   count again:

   ```sh
   sudo iptables-save | grep -c 'KUBE-SVC'
   for i in $(seq 1 40); do kubectl create deployment svc$i --image=nginx:alpine >/dev/null
     kubectl expose deployment svc$i --port=80 >/dev/null; done
   sleep 20
   sudo iptables-save | grep -c 'KUBE-SVC'
   time sudo iptables-save > /dev/null
   ```

3. Ask kube-proxy which modes it will accept, including the one the post's era was escaping:

   ```sh
   P=$(kubectl -n kube-system get pod -l k8s-app=kube-proxy -o name | head -1)
   kubectl -n kube-system exec $P -- kube-proxy --help 2>&1 | grep -A4 -- '--proxy-mode'
   kubectl -n kube-system exec $P -- kube-proxy --help 2>&1 | grep -i -c userspace
   ```

4. Then test the one word in the ladder that changes what you are allowed to do — `locked`:

   ```sh
   kubectl -n kube-system exec $P -- \
     kube-proxy --feature-gates=NFTablesProxyMode=false --proxy-mode=iptables 2>&1 | head -3
   kubectl -n kube-system exec $P -- \
     kube-proxy --feature-gates=KubeProxyIPVS=false --proxy-mode=iptables 2>&1 | head -3
   ```

5. Bullet five's sentence, checked against the API:

   ```sh
   kubectl create job flaky --image=busybox -- sh -c 'exit 1'
   kubectl explain job.spec.backoffLimit | tail -4
   sleep 90; kubectl get job flaky -o jsonpath='{.status}{"\n"}' | tr ',' '\n' | head -8
   ```

6. Bullet six's second half — find out where the validation the post promised actually happens:

   ```sh
   cat <<'YAML' > typo.yaml
   apiVersion: v1
   kind: Pod
   metadata: {name: typo}
   spec:
     contaners:
       - {name: c, image: busybox}
   YAML
   kubectl apply -f typo.yaml --validate=strict; echo "strict exit=$?"
   kubectl apply -f typo.yaml --validate=false --dry-run=server; echo "server exit=$?"
   ```

7. Bullets four and seven, which are each one command's worth of finding out:

   ```sh
   kubectl api-resources | grep -i -E 'ingress|gateway'
   kubectl rolling-update --help 2>&1 | head -2
   kubectl rollout --help | sed -n '/Available Commands/,/^$/p'
   ```

8. Bullet one, honestly. Read the ceiling, then read your lab:

   ```sh
   kubectl get nodes -o custom-columns=\
   NAME:.metadata.name,PODCAP:.status.capacity.pods,CPU:.status.capacity.cpu
   kubectl get pods -A --no-headers | wc -l
   ```

**Expect** — step 1 prints `mode: ""` or `mode: iptables` from the ConfigMap; empty means "use the
default", and the default is iptables, so both readings mean the same thing. The `-A KUBE-` count is
in the low hundreds on an idle single-node cluster. `nft list tables | grep -c kube` prints `0`,
because nothing selected nftables mode even though it has been stable and locked since v1.33 — a
locked gate guarantees the code path is *present*, not that it is *chosen*.

Step 2: the `KUBE-SVC` count rises roughly in proportion to services — each service gets its own
chain, and each chain is reached from a linear scan of `KUBE-SERVICES`. Note the `time`. On forty
services it is unremarkable; extrapolate to five thousand and you have the reason nftables exists,
and also the reason it took until v1.29 to start: the linear scan is fine until it isn't, and
"fine until it isn't" is very hard to schedule.

Step 3: `--proxy-mode` lists `iptables`, `ipvs` and `nftables` for Linux. The `grep -c userspace`
prints `0`. The mode this post's bullet two was an alternative *to* is not merely deprecated — it is
not a value the flag accepts, so there is nothing left to compare the 80% against on any current
cluster.

Step 4 is the ladder made executable. `NFTablesProxyMode=false` is refused, and the error says the
gate is locked to its default — that is what `locked: true` in the stable row means, and it is the
only one of the six gates that would do this. `KubeProxyIPVS=false` behaves differently: it is
`deprecated`, not locked, so setting it produces a warning rather than a refusal. Two gates
covering the same subsystem, two different answers to the same syntax.

Step 5: `backoffLimit` explains itself as defaulting to 6. After a minute and a half the Job's
status shows `failed: 6` and a `Failed` condition — it stopped. "Keeps trying until it's
successfully completed" is a description of a Job with `backoffLimit` unset to infinity, which is
not the default and was not the default in 1.1 either.

Step 6: `--validate=strict` rejects `contaners` and names the unknown field. Then the second command
is the interesting one — with client validation off and a *server-side* dry run, the API server
rejects it anyway, and that is the difference the removed `ServerSideFieldValidation` gate bought:
the check now lives where the schema does. The post's "let you know if there are any issues with
your configuration files before you deploy them" was a client-side promise, and the client was
guessing from a schema it had downloaded.

Step 7: `ingresses` and `ingressclasses` in `networking.k8s.io/v1`, no Gateway resources — the API
the project now recommends is not installed, because it is not part of Kubernetes.
`kubectl rolling-update` reports an unknown command. `kubectl rollout` lists `history`, `pause`,
`restart`, `resume`, `status` and `undo`: six verbs where the post had one improved flag, all of
them possible only because the loop moved into a controller.

Step 8 is the honest end of this exercise. Your node reports a pod capacity — 110 by default, the
first of the pin's four limits — and your whole cluster is running a few dozen pods. Bullet one's
thousand-node cluster and million QPS cannot be reproduced here, cannot be reproduced on any lab
you will build for this course, and could not be verified by most readers in 2015 either. That is
worth naming rather than skipping: it is the one bullet in this post whose truth you have to take
on trust, and it is also the one the announcement put first.

**Read on** — the [feature gate reference](https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/),
which is generated from the same frontmatter the six ladders above transcribe. Pick any gate whose
last row is `stable` and whose file says `removed`, then answer this: if the switch is gone, what
is the sentence you would write to tell someone on v1.28 and someone on v1.37 the same true thing
about that feature? The four-column ladder is one answer. Find out what it costs you.

**Teardown** — `kubectl delete deployment,svc -l app --all-namespaces=false` will not catch these,
so remove them by name and clean up the rest:

```sh
for i in $(seq 1 40); do kubectl delete deployment svc$i --ignore-not-found >/dev/null
  kubectl delete svc svc$i --ignore-not-found >/dev/null; done
kubectl delete job flaky --ignore-not-found; rm -f typo.yaml
```

This is the last exercise in 2015. When you are done with the guest, tear the lab down properly —
[the teardown steps](../../strands/lab-topologies.md#teardown) — rather than leaving a cluster
running for a year that has no more posts in it.
