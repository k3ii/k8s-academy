<a id="helm-charts-making-it-simple-to-package-and-deploy-apps-on-kubernetes"></a>
# The canonical location this post promoted is unreachable from every page of the current documentation, and what outlived it is a label set the same documentation says nothing reads

**Post** — [Helm Charts: making it simple to package and deploy common applications on Kubernetes](https://kubernetes.io/blog/2016/10/helm-charts-making-it-simple-to-package-and-deploy-apps-on-kubernetes/),
2016-10-10, Kubernetes v1.4 — Vic Iglesias of Google, writing for SIG Apps, announcing the
Kubernetes Charts repository. It is the only post in this year whose subject is a *place* rather
than a mechanism, which is what makes it worth walking.

**As written** — the post opens on a problem of duplication, and names four places a reader might
already be looking:

> For best practices on how these applications should be configured, users could look at the many
> resources available such as: the examples folder in the Kubernetes repository, the Kubernetes
> contrib repository, the Helm Charts repository, and the Bitnami Charts repository. While these
> different locations provided guidance, it was not always formalized or consistent such that users
> could leverage similar installation procedures across different applications.

Then it embeds [xkcd 927](https://xkcd.com/927/) — the *Standards* comic, in which an attempt to
unify fourteen competing standards produces fifteen — and immediately disclaims it:

> In this case, we're not creating Yet Another Place for Applications, rather promoting an existing
> one as the canonical location.

The canonical location is named:

> The home for these Charts is the Kubernetes Charts repository which provides continuous
> integration for pull requests, as well as automated releases of Charts in the master branch.

with two folders, `stable` and `incubator`, and the promotion rule between them. The analogy that
carried the idea is one sentence:

> **Helm is the package manager** (analogous to yum and apt) and **Charts are packages** (analogous
> to debs and rpms).

Then a table of what was available: six charts in `stable` — Drupal, Jenkins, MariaDB, MySQL,
Redmine, WordPress — and nine in `incubator`. Then two workflows. The developer's is seven steps,
ending in a pull request to the charts repository. The user's is five:

> 1. Install Helm
> 2. Initialize Helm
> 3. Search for a chart
> 4. Install the chart
> 5. After the install

with two commands, printed as the reader would type them:

```
$ helm search
NAME VERSION DESCRIPTION stable/drupal 0.3.1 One of the most versatile open source content m...
```

```
$ helm install stable/jenkins
```

and a `NOTES.txt` transcript whose release is called `brawny-frog-jenkins`.

**As it runs now** — take the four locations in the opening paragraph first, because the post's
whole argument is that they should have collapsed into one.

At the pin, **none of the four is reachable from anywhere under `docs/`**. Zero files contain
`kubernetes/kubernetes/tree/master/examples`, zero contain `kubernetes/contrib`, zero contain
`helm/charts`, and zero contain `kubernetes/charts` — which is the canonical location itself. The
post's `stable` and `incubator` folders, its promotion rule, its repository-structure README and its
issue tracker are, from the current documentation's point of view, nowhere.

The component the user workflow depended on left a single trace. Searching the pin for `tiller`
returns exactly one line, and it is not a deprecation note:

> ```
> helm-tiller: disabled
> ```
>
> — `docs/tutorials/hello-minikube.md:260`, in a sample of `minikube addons list` output

That is the whole of it: a server-side component whose entire remaining presence in the Kubernetes
documentation is another tool's list of add-ons reporting that it is off.

Note that the post never names it. Step 2 of the user workflow is the words *"Initialize Helm"*
wrapped around a link, and the link's own fragment is `#install-an-example-chart`. Whoever
retargeted the post's hrefs onto Helm's current documentation left the 2016 anchor text in place, so
the post now instructs you to initialize Helm and points at a page about installing a chart.
Initialization is not a step any more; the post's step 4 link and its step 3 link were retargeted
the same way, while step 4 of the *developer* workflow still points at a branch called `dev-v2`. The
post's link set now spans both major versions of the tool.

What survived is narrower than the repository and much more durable than it.

The **analogy** survived, minus the analogy. The pin says:

> [Helm](https://helm.sh/) is a tool for managing packages of pre-configured Kubernetes resources.
>
> — `docs/reference/tools/_index.md:43`, and again verbatim at
> `docs/concepts/workloads/management.md:75`

One further sentence follows it on both pages, naming those packages *Helm charts*. Both
occurrences sit behind a `thirdparty-content` marker. The apt-and-rpm comparison is gone; what is
left is the noun *package* doing the work the comparison used to do, in two sentences duplicated
across two pages.

The **charts** survived, as an example. The pin's page on recommended labels is built around a
worked case it introduces this way:

> Consider a slightly more complicated application: a web application (WordPress) using a database
> (MySQL), installed using Helm.
>
> — `docs/concepts/overview/working-with-objects/common-labels.md:105-107`

WordPress and MySQL are two of the six charts in the post's `stable` column. Ten years on, the two
of them are the illustration the Kubernetes documentation reaches for when it needs an application
that was installed by a package manager, and `app.kubernetes.io/managed-by: Helm` appears in five
manifest snippets on that page.

And the **convention** survived — with a disclaimer directly above it:

> These are recommended labels. They make it easier to manage applications but aren't required for
> any core tooling.
>
> — `docs/concepts/overview/working-with-objects/common-labels.md:22-25`

Six keys, one of which exists to record the tool: *"`app.kubernetes.io/managed-by` — The tool being
used to manage the operation of an application"*, example value `Helm`. Meanwhile `helm.sh/chart` —
the label the tool actually stamps on what it installs — has **zero** occurrences at the pin. The
documented convention names Helm as a *value* in a field nothing reads, and does not mention the
label Helm writes itself.

One live link to Helm's source remains, and it uses the address Helm moved out of:

> If you want to generate a Chart to be used with [Helm](https://github.com/kubernetes/helm) run:
>
> — `docs/tasks/configure-pod-container/translate-compose-kubernetes.md:346`

**The diff, and why** — this post was right about the problem, right about the solution, and the
xkcd comic it disclaimed is the thing that actually happened to it.

Read the disclaimer again — *"we're not creating Yet Another Place for Applications, rather
promoting an existing one as the canonical location"*. The claim is not that consolidation is
valuable; everybody agreed on that. The claim is a claim about **authority**: that this repository,
because it had CI and a promotion rule and lived in the Kubernetes org, would be the place. The
mechanism was social, not technical. Nothing in Kubernetes pointed at it, enforced it, or depended
on it — the pointing was done by prose, and prose is deletable.

So the repository lost its authority the ordinary way: the tool it served changed shape, the
project's docs stopped linking it, and the org moved. `kubernetes/charts` became `helm/charts`
became archived, and the post's table of fifteen charts is now fifteen dead ends in nine rows —
four of which, in the *Incubating* column, already pointed at `stable` folders under a different org
when the post's links were last touched. A reader auditing the table finds Grafana, MongoDB,
Prometheus and Spark listed as incubating and linked as stable. That defect is in the corpus and is
worth naming, because it is the same failure at small scale: a hand-maintained index of a
hand-maintained index.

What survived is the part that was not an index. `app.kubernetes.io/*` is a **convention with no
central list** — it is six key names, and any manifest anywhere can carry them. There is no folder
to archive and no org to move. That is why it outlived the repository whose charts popularised it,
and it outlived it *without being enforced*: the pin says plainly that the labels *"aren't required
for any core tooling"*. Nothing validates them, nothing defaults them, no controller reads them.
They are useful exactly to the degree that people agree, which is the same mechanism the charts
repository ran on — and the difference is that a convention costs nothing to keep agreeing with,
while a repository costs somebody's afternoon every week.

The comic, then, landed twice. The post promised not to add a standard and was correct: it added a
*location*, and the location is gone. The standard that replaced it is a label prefix, which is a
fifteenth standard by any reading, and it won because it had nothing to maintain.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), fresh. Nothing here needs a second
node: the whole exercise is objects, labels and selectors, plus one optional client binary. Bring
the guest up with [the five provision steps](../../strands/lab-topologies.md#provision),
substituting `topology=solo`, install Kubernetes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), then
`ssh zain@10.10.10.180`.

The charts themselves are out of bounds — this curriculum does not run software somebody else
packages, and the post's fifteen are archived regardless. Steps 8 to 10 use the client against a
chart you write.

**Do**

1. Establish, before anything else, what the API records about any of this:

   ```sh
   kubectl api-resources | grep -i -e chart -e release -e helm
   kubectl get crd 2>/dev/null | wc -l
   ```

   Nothing. The post's package manager has no API surface in a cluster it has not been pointed at,
   which is the difference between it and everything else this year's posts announce.

2. Build the pin's own worked example by hand — the WordPress and MySQL pair, carrying all six
   recommended labels exactly as `common-labels.md` prints them:

   ```sh
   kubectl create namespace shop
   kubectl apply -n shop -f - <<'EOF'
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: wordpress
     labels:
       app.kubernetes.io/name: wordpress
       app.kubernetes.io/instance: wordpress-abcxyz
       app.kubernetes.io/version: "4.9.4"
       app.kubernetes.io/managed-by: Helm
       app.kubernetes.io/component: server
       app.kubernetes.io/part-of: wordpress
   spec:
     replicas: 1
     selector:
       matchLabels:
         run: wordpress
     template:
       metadata:
         labels:
           run: wordpress
       spec:
         containers:
           - name: c
             image: registry.k8s.io/pause:3.10
   EOF
   ```

   Two label sets are in that manifest and they do different jobs. Say which one the Deployment
   would fail to create without, and which one you could delete with no effect on anything.

3. Prove the second half of that answer:

   ```sh
   kubectl label -n shop deployment wordpress app.kubernetes.io/managed-by=Kustomize --overwrite
   kubectl rollout status -n shop deployment/wordpress
   kubectl get -n shop deployment wordpress -o jsonpath='{.metadata.labels}{"\n"}'
   ```

   You have just told the cluster a different tool manages this application. Nothing happened.
   Reconcile that with the pin's note that these labels *"aren't required for any core tooling"* and
   say what the field is actually for.

4. Now do the same to the label that is load-bearing, and watch the difference:

   ```sh
   kubectl label -n shop deployment wordpress run=changed --overwrite
   kubectl patch -n shop deployment wordpress --type=merge \
     -p '{"spec":{"selector":{"matchLabels":{"run":"changed"}}}}'
   ```

   The patch is refused, and the refusal names the field. This is the same immutability
   [04](04-using-deployment-objects-with.md) found in `spec.selector`; the point here is the
   contrast with step 3, not the rule itself.

5. Add the second object of the pin's example, so `part-of` has something to gather:

   ```sh
   kubectl apply -n shop -f - <<'EOF'
   apiVersion: v1
   kind: Service
   metadata:
     name: mysql
     labels:
       app.kubernetes.io/name: mysql
       app.kubernetes.io/instance: mysql-abcxyz
       app.kubernetes.io/version: "5.7.21"
       app.kubernetes.io/managed-by: Helm
       app.kubernetes.io/component: database
       app.kubernetes.io/part-of: wordpress
   spec:
     clusterIP: None
     selector:
       run: mysql
     ports:
       - port: 3306
   EOF
   kubectl get all -n shop -l app.kubernetes.io/part-of=wordpress
   ```

   One query, two objects of different kinds, no controller involved. This is the entire practical
   payoff of the convention, and it is worth measuring against how much agreement it took to get.

6. Test whether the cluster distinguishes a recommended label from an invented one:

   ```sh
   kubectl label -n shop service mysql app.kubernetes.io/nonsense=yes
   kubectl label -n shop service mysql my.own.prefix/managed-by=Helm
   kubectl get -n shop service mysql --show-labels
   ```

   Both accepted. The pin explains the prefix as a namespacing courtesy — *"Labels without a prefix
   are private to users"* — not as a validated set. Say what that implies about typos in a
   convention with no schema.

7. Go looking for the post's world in the pinned corpus, since its absence is the finding:

   ```sh
   grep -rn "tiller" /path/to/pinned/website/content/en/docs | wc -l
   grep -rln "kubernetes/charts\|helm/charts\|kubernetes/contrib" \
     /path/to/pinned/website/content/en/docs | wc -l
   ```

   One and zero. Then read the single `tiller` line in context and note what kind of document it is.

8. Install the Helm 3 client on the guest by whatever route your host offers — the client only, no
   repositories added. Then run the post's step 3 exactly as printed:

   ```sh
   helm search
   helm repo list
   ```

   Two different refusals. One is about the command's shape and one is about the cluster's state.
   Which of the two is the post's *"canonical location"* argument failing, and which is merely a CLI
   that grew a subcommand?

9. Run the post's step 4 exactly as printed:

   ```sh
   helm install stable/jenkins
   ```

   It fails for at least two independent reasons before it can fail for the interesting one. Name
   them in order. Then confirm that the release-naming behaviour the post's transcript relies on —
   `brawny-frog-jenkins` — is now something you have to ask for:

   ```sh
   helm install --generate-name --help | head -20
   ```

10. Take the post's *developer* workflow, which is the half that still runs, using a chart you own:

    ```sh
    helm create mychart
    ls mychart mychart/templates
    helm template mychart | head -40
    helm install mine ./mychart --dry-run 2>&1 | head -20
    ```

    Compare the scaffold against the post's seven developer steps. Its `values.yaml` is there, its
    `NOTES.txt` is there, its README is not. Then find the labels the scaffold puts on every object
    and check them against step 2's list — including whether `helm.sh/chart` is among them, and
    whether that label appears anywhere in the pinned documentation.

**Expect**

```sh
kubectl get all -n shop --show-labels
kubectl get all -n shop -l app.kubernetes.io/managed-by=Helm
kubectl get all -n shop -l app.kubernetes.io/part-of=wordpress
helm list -A
```

Two objects, both labelled as though a package manager put them there, and `helm list -A` empty —
because it looks for release Secrets and there are none. That gap is the exercise's centre: the
convention and the tool are fully decoupled, so a manifest can claim to be Helm-managed and no
component in the cluster, including Helm, will contradict it.

By the end you should be able to say which of the post's two workflows still runs (the developer's,
minus the pull request), which does not (the user's, at every step), and where the post's
contribution actually landed — not in a repository, and not in an API, but in six key names that
survived because nobody had to maintain a list of them.

**Read on** — the pin's
[recommended labels page](https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/)
distinguishes `app.kubernetes.io/name` from `app.kubernetes.io/instance` and spends a section on why
both are needed. Read it against step 5 and answer: if a package manager installs the same chart
twice into one namespace, which of the six labels is the only one that can tell the two installations
apart, and what breaks in step 5's query if it is omitted?

**Teardown** — [the teardown step](../../strands/lab-topologies.md#teardown). If you installed the
Helm client in step 8 it lives on the guest and goes with it; nothing in this exercise wrote outside
the `shop` namespace.
