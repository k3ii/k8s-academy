<a id="kubernetes-1-2-and-simplifying-advanced-networking-with-ingress"></a>
# Nothing in this post's fences ran as printed, and the manifest they were meant to create is three kinds of dead

**Post** — [Kubernetes 1.2 and simplifying advanced networking with Ingress](https://kubernetes.io/blog/2016/03/kubernetes-1-2-and-simplifying-advanced-networking-with-ingress/),
2016-03-31, Kubernetes v1.2 — the sixth post in that release's five-day series, and it says so
itself: *"Ingress is currently in beta and under active development."*

**As written** — the Ingress object gives your cluster one place to configure inbound traffic, and
"if you're familiar with the go programming language, Ingress is like net/http's 'Server' for your
entire cluster." A controller does the work: "An Ingress Controller is a daemon, deployed as a
Kubernetes Pod, that watches the ApiServer's /ingresses endpoint for updates to the Ingress
resource." You are told plainly what you must supply: "Your Kubernetes cluster must have exactly one
Ingress controller that supports TLS for the following example to work."

Then the walkthrough. A service:

```
$ kubectl run echoheaders   
--image=gcr.io/google\_containers/echoserver:1.3 --port=8080  
$ kubectl expose deployment echoheaders --target-port=8080   
--type=NodePort  
```

A certificate and a Secret — the fence ends `" | kubectl create -f` — and then the Ingress:

```
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: test
spec:
  tls:
  - secretName: tls
  backend:
    serviceName: echoheaders
    servicePort: 8080
```

"You should get a load balanced IP soon", shown as a `kubectl get ing` table with the columns
`NAME RULE BACKEND ADDRESS AGE` and a row reading `test - echoheaders:8080 130.X.X.X 4m`. And then
the payoff: "you should see requests to that IP on :80 getting redirected to :443 and terminated
using the given TLS certificates", with `curl 130.X.X.X` returning `301 Moved Permanently`.

**As it runs now** — the corrections come before the translation, because two of the fences never
worked in the first place.

1. **The fences are broken as published, not as aged.** Line by line, inside a code block:
   `$ kubectl run echoheaders` ends and `--image=gcr.io/google\_containers/echoserver:1.3` begins on
   the next line, so a copy-paste runs `kubectl run` with no image and then a bare `--image=…` as a
   command. The image name itself carries a literal backslash — `google\_containers` — because a
   Markdown escape was written inside a fence, where escapes are not processed. And the Secret's
   fence closes on `" | kubectl create -f` with no `-`, so `kubectl` is handed a `-f` with nothing
   after it. Whatever `extensions/v1beta1` used to do, this walkthrough did not run in 2016 either.
2. **`kubectl run` no longer makes a Deployment,** so even repaired, `kubectl expose deployment
   echoheaders` has nothing to expose. This is the same 2016-era assumption that
   [the leader election exercise](01-simple-leader-election-with-kubernetes.md) meets as
   `--replicas`, in its other form: `kubectl run` created a controller then, and creates a Pod now.
3. **The group-version hard-errors.** `extensions/v1beta1` and `networking.k8s.io/v1beta1` Ingress
   "is no longer served as of v1.22", per the pin's deprecation guide. There is nothing to translate
   at the wire level; the request is refused before validation.
4. **Every field in the four-line spec was renamed,** and the pin lists them as a set:
   `spec.backend` → `spec.defaultBackend`, `serviceName` → `service.name`, numeric `servicePort` →
   `service.port.number`, string `servicePort` → `service.port.name`.
5. **The shape survives validation and is documented as the shape that does not work.** An Ingress
   with a default backend and no rules is still legal — "An Ingress with no rules sends all traffic
   to a single default backend" — but the pin's TLS section says: "Keep in mind that TLS will not
   work on the default rule because the certificates would have to be issued for all the possible
   sub-domains. Therefore, `hosts` in the `tls` section need to explicitly match the `host` in the
   `rules` section." The post's Ingress is a default backend plus a `tls` block with no `hosts` and
   no rules. Ported field-for-field it is accepted by the API server and cannot do the one thing the
   post uses it for. This is the third fate and the dangerous one.

**The diff, and why** — the post is a beta API being demonstrated as though it were finished, and
what makes it worth walking is that the API did finish — and then stopped.

Three things moved. The **backend** became a structured reference rather than a name-and-port pair,
which is what let a backend be something other than a Service. Every **path** became typed:
"Paths that do not include an explicit `pathType` will fail validation," with `Prefix`, `Exact` and
`ImplementationSpecific` — and the last of those exists to name what `v1beta1` did, since the pin
says to "match the undefined `v1beta1` behavior, use `ImplementationSpecific`." A whole path type
exists as a bookmark for the era this post is written in. And the **class** — which the post handles
by saying you must have "exactly one Ingress controller", a constraint on your cluster standing in
for a field — went from the `kubernetes.io/ingress.class` annotation, which the pin notes "was never
formally defined, but was widely supported", to `spec.ingressClassName`, and the pin is careful that
this was not a rename: "the field is a reference to an IngressClass resource that contains
additional Ingress configuration, including the name of the Ingress controller."

That last move is the one with a gate, and it is the last thing that happened to the Ingress family:

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.21 – v1.21 |
| beta | `true` | — | v1.22 – v1.22 |
| stable | `true` | — | v1.23 – v1.24 |

`IngressClassNamespacedParams`, which let an IngressClass point its `parameters` at a namespaced
object — the last increment of configurability the class-as-an-object idea received. The file
declares `removed: true`. One release at alpha, one at beta, two at stable, gone; and nothing
followed it, because of the note the pin now opens the Ingress page with:

> The Kubernetes project recommends using Gateway instead of Ingress. The Ingress API has been
> frozen. … The Ingress API is generally available, and is subject to the stability guarantees for
> generally available APIs. The Kubernetes project has no plans to remove Ingress from Kubernetes.
> … The Ingress API is no longer being developed, and will have no further changes or updates made
> to it.

Set that against the post's closing paragraph, which is an open invitation: "The Ingress is still in
beta, and we would love your input to grow it. You can contribute by writing controllers or evolving
the API. All things related to the meaning of the word 'ingress' are in scope, this includes DNS,
different TLS modes, SNI, load balancing at layer 4, content caching, more algorithms, better health
checks; the list goes on." Almost every item on that list exists today, and none of it is in
Ingress. The pressure was that "evolving the API" and "writing controllers" turned out to be in
tension: an API whose every interesting behaviour is `ImplementationSpecific` cannot be extended
without breaking the controllers that guessed differently, so the project stopped extending it and
started again with a different one. A frozen GA API is not a dead API and not a deprecated one — it
is a third state the deprecation policy has no word for, and the post's own genre, "here is a beta
we would love your input on", is what it is the end of.

One thing the post presents as Ingress behaviour was never Ingress behaviour. The `301 Moved
Permanently` is the nginx controller redirecting `:80` to `:443`; the API says nothing about it, and
the pin says why not — "There is a gap between TLS features supported by various ingress
controllers. You should refer to the documentation for the ingress controller(s) you've chosen to
understand how TLS works in your environment." Read the post's `curl` output again with that in
hand.

Release facts and the pressure behind each one are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), fresh. This exercise runs no Ingress
controller and does not pretend to: a controller is a third-party component that nothing in this
tree pins, so *Do* stops at the API server, which is where all five of the fates above live. Bring
the guest up with [the five provision steps](../../strands/lab-topologies.md#provision),
substituting `topology=solo`, install Kubernetes with
[the node baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), then
`ssh zain@10.10.10.180`.

**Do**

1. Run the post's first fence exactly as printed, both lines, in order. Record what each one says.

   ```sh
   kubectl run echoheaders
   --image=gcr.io/google\_containers/echoserver:1.3 --port=8080
   ```

2. Repair the line break but not the image, and then repair the image but not the registry, so you
   can tell the three failures apart:

   ```sh
   kubectl run echoheaders --image=gcr.io/google\_containers/echoserver:1.3 --port=8080
   kubectl get pod echoheaders -o jsonpath='{.spec.containers[0].image}'; echo
   kubectl delete pod echoheaders --ignore-not-found
   kubectl run echoheaders --image=gcr.io/google_containers/echoserver:1.3 --port=8080
   kubectl get pod echoheaders
   ```

3. Get a working Service the post's way, then the way that works:

   ```sh
   kubectl expose deployment echoheaders --target-port=8080 --type=NodePort
   kubectl delete pod echoheaders --ignore-not-found
   kubectl create deployment echoheaders --image=registry.k8s.io/e2e-test-images/agnhost:2.53 \
     -- /agnhost netexec --http-port=8080
   kubectl expose deployment echoheaders --target-port=8080 --port=8080 --type=NodePort
   curl -s "$(hostname -I | awk '{print $1}'):$(kubectl get svc echoheaders -o jsonpath='{.spec.ports[0].nodePort}')/hostname"; echo
   ```

4. Make the Secret the post makes, and then make the one the pin's example makes, and find out which
   of the two the API server has an opinion about:

   ```sh
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /tmp/tls.key -out /tmp/tls.crt \
     -subj "/CN=echoheaders/O=echoheaders"
   kubectl create secret generic tls --from-file=tls.crt=/tmp/tls.crt --from-file=tls.key=/tmp/tls.key
   kubectl get secret tls -o jsonpath='{.type}'; echo
   kubectl create secret generic tls-typed --type=kubernetes.io/tls --from-file=tls.crt=/tmp/tls.crt
   kubectl create secret tls tls-proper --cert=/tmp/tls.crt --key=/tmp/tls.key
   kubectl get secret tls tls-proper -o custom-columns=NAME:.metadata.name,TYPE:.type
   ```

5. Apply the post's Ingress verbatim, then with the group-version corrected and nothing else:

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: extensions/v1beta1
   kind: Ingress
   metadata:
     name: test
   spec:
     tls:
     - secretName: tls
     backend:
       serviceName: echoheaders
       servicePort: 8080
   YAML
   kubectl apply -f - <<'YAML'
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: test
   spec:
     tls:
     - secretName: tls
     backend:
       serviceName: echoheaders
       servicePort: 8080
   YAML
   ```

   Two different refusals. Say which layer produced each, and which one you would have predicted.

6. Port it field for field and see what you get — including a `pathType` you did not have to write:

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: test
   spec:
     tls:
     - secretName: tls
     defaultBackend:
       service:
         name: echoheaders
         port:
           number: 8080
   YAML
   kubectl get ing
   kubectl get ing test -o yaml | sed -n '/^spec:/,$p'
   ```

   Compare the column headings with the post's `NAME RULE BACKEND ADDRESS AGE`. Then answer why
   `pathType` — "required for each specified path" — never came up.

7. Now write the rule the post did not need, and meet the requirement:

   ```sh
   kubectl apply -f - <<'YAML'
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: ruled
   spec:
     tls:
     - secretName: tls
     rules:
     - host: echoheaders.lab
       http:
         paths:
         - path: /
           backend:
             service:
               name: echoheaders
               port:
                 number: 8080
   YAML
   ```

   Then add `pathType: Prefix` to that path and apply again. Record the error from the first attempt
   verbatim, and note that the second Ingress still has no `hosts` in its `tls` block while the
   pin's TLS note says it must.

8. Find the class, which the post handles with a sentence about your cluster:

   ```sh
   kubectl get ing -o custom-columns=NAME:.metadata.name,CLASS:.spec.ingressClassName,ADDRESS:.status.loadBalancer.ingress
   kubectl get ingressclass
   kubectl api-resources | grep -i ingress
   kubectl explain ingressclass.spec.parameters
   ```

   `parameters.namespace` is the field the ladder above is the ladder of. Read what `explain` says
   about it and decide whether you could tell, from the API alone, that it was the last thing added.

**Expect** — step 1: the first line creates a Pod named `echoheaders` with no image, so `kubectl`
rejects it with `error: --image is required`; the second line is not a command and the shell says
so. Nothing about Kubernetes was involved in either failure.

Step 2: the repaired line is accepted and the image is stored with the backslash intact —
`gcr.io/google\_containers/echoserver:1.3` — because an image reference is a string and no validator
reads it. The Pod then goes to `ErrImagePull` or `InvalidImageName`; note which, because they are
different diagnoses. Removing the backslash changes the error and does not fix it: the registry host
is two migrations gone.

Step 3: `kubectl expose deployment echoheaders` fails with
`deployments.apps "echoheaders" not found` — `kubectl run` made a Pod. With a real Deployment and a
pinned test image, the NodePort answers and returns the Pod's hostname. That is the post's sanity
check, finally passing.

Step 4: the post's Secret is created with type `Opaque`, and nothing checks its contents.
`tls-typed`, missing `tls.key`, is **rejected**: `Secret "tls-typed" is invalid:
data[tls.key]: Required value`. The API server verifies the required keys for that type and cannot
verify anything about an untyped one. Eleven years later, the difference between the post's Secret
and the documentation's Secret is one line of `type:` and a validator.

Step 5: the verbatim manifest fails in the *client* —
`no matches for kind "Ingress" in version "extensions/v1beta1"` — because `kubectl` asked for the
group-version and did not find it. With `networking.k8s.io/v1` substituted, the request reaches the
server and is refused there:
`error: error validating data: ValidationError(Ingress.spec): unknown field "backend"`. Two layers,
two messages, and only the second one is about the fields.

Step 6: accepted. `kubectl get ing` prints `NAME CLASS HOSTS ADDRESS PORTS AGE` — `RULE` and
`BACKEND` are gone from the output entirely — with `CLASS` set to `<none>`, `ADDRESS` empty, and
`PORTS` reading `80, 443`. `pathType` never came up because the post's Ingress has no paths; it has
a default backend, which is the one shape in the API that requires no path type and, per the pin's
TLS note, is the one shape TLS does not work on.

Step 7: the pathless rule is rejected with
`spec.rules[0].http.paths[0].pathType: Required value: pathType must be specified`. With
`pathType: Prefix` it applies. Both Ingresses now sit with an empty `ADDRESS` forever, because there
is no controller — which is the post's own first requirement, stated in its third paragraph, and the
only part of its setup this lab deliberately does not satisfy.

Step 8: `CLASS` is `<none>` on both, `kubectl get ingressclass` returns
`No resources found`, and `api-resources` lists `ingresses` and `ingressclasses` in
`networking.k8s.io/v1` and nothing in `extensions`. The Ingress objects are valid, stored, and
inert: a frozen API describing traffic that nothing is carrying.

**Read on** — the pin's [deprecation policy](https://kubernetes.io/docs/reference/using-api/deprecation-policy/):
find the rule that forced `extensions/v1beta1` Ingress to keep being served for three releases after
`networking.k8s.io/v1` arrived, and then find the clause that covers a *frozen* GA API. Write down
what the policy obliges the project to do about an API it has stopped developing but promises never
to remove — and if the answer is nothing, say what that means for a reader who finds an Ingress
tutorial dated last month.

**Teardown** — `kubectl delete ing test ruled; kubectl delete svc echoheaders; kubectl delete deploy
echoheaders; kubectl delete secret tls tls-proper`. Take the guest down with
[teardown](../../strands/lab-topologies.md#teardown); nothing here is worth keeping.
