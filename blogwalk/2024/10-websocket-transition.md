<a id="websocket-transition"></a>
# The protocol changed, and so did who is allowed to use it

**Post** — [Kubernetes 1.31: Streaming Transitions from SPDY to WebSockets](https://kubernetes.io/blog/2024/08/20/websocket-transition/),
2024-08-20, Kubernetes v1.31.

**As written** — as of v1.31, `kubectl` uses WebSockets instead of SPDY by default for streaming
connections. The case is short and entirely convincing: `exec`, `attach`, `cp` and `port-forward`
are not request-response, they need a persistent bidirectional connection, and Kubernetes had been
getting that from SPDY/3.1 — a protocol **deprecated for eight years and never standardised**.
Modern proxies, gateways and load balancers no longer speak it, which is why `kubectl exec`
through a corporate gateway would simply stop working. WebSockets is standard, so it works.

There is no migration to do. It is a default flip, announced as one.

**As it runs now** — still true, still the default, and the post needs no correction. The
commands run, the protocol is the one it says, and nothing in it has expired.

**The diff, and why** — the post is right about everything it says and could not have told you
the interesting part, which is what the change *cost*.

RBAC authorises subresources by verb, and the verb comes from the HTTP method. SPDY upgraded over
an HTTP **`POST`**, which maps to the `create` verb — so `create` on `pods/exec` is what an exec
session has always required, and it is what every Role in every cluster was written against. A
WebSocket handshake is an HTTP **`GET`**.

The verb moved. Nobody announced it, because nobody was making a decision about authorisation —
they were changing a transport. The gap was closed in **v1.35** by
`AuthorizePodWebsocketUpgradeCreatePermission`, a beta-and-on gate that applies a *synthetic*
RBAC check so a WebSocket upgrade to `pods/exec`, `pods/attach` or `pods/portforward` still
demands `create`, "matching the existing SPDY security model". Its own documentation notes you
might want to disable it if you have clients that "connect via WebSockets but do *not* currently
hold the **create** RBAC permission" — which is as close as a feature gate ever comes to
admitting that real clients were relying on the gap.

The other half of the diff is that the transition is *still not finished*. Both gates the post
depends on are beta at the pin, with no stable stage:

| gate | alpha | beta, default on | at the pin |
|---|---|---|---|
| `TranslateStreamCloseWebsocketRequests` | v1.29 | v1.30 | still beta |
| `PortForwardWebsockets` | v1.30 | v1.31 | still beta |

Seven releases and six releases respectively, on by default the whole time, never promoted. And
the architecture kept moving underneath: `ExtendWebSocketsToKubelet`, beta in **v1.36**, proxies
these streams **directly to the kubelet** instead of translating or tunnelling them at the API
server — the same handlers, moved closer to the runtime.

So the honest then→now is not "SPDY became WebSockets". It is: a transport swap that read as
pure cleanup silently relocated an authorisation boundary for four releases, and the thing being
swapped is still in motion two years later. **The change that breaks nothing is the one nobody
audits.**

There is a longer arc here, and it is the reason this post earns an exercise rather than a read.
The [2015 hangout minutes](../2015/README.md) record `kubectl exec` being demoed as *SPDY over
HTTP, entered via `nsenter`*. Eleven years, three transports, and the same four verbs.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo). Reuse the guest from
[the image-volume exercise](07-image-volume-source.md) if you still have it; otherwise
[provision](../../strands/lab-topologies.md#provision) with `topology=solo` and
`ssh zain@10.10.10.180`.

**Do**

1. Confirm the protocol before reasoning about it. Run an exec with the client's wire logging on
   and find the upgrade:

   ```sh
   kubectl run probe --image=busybox --restart=Never -- sh -c 'sleep 3600'
   kubectl wait --for=condition=Ready pod/probe
   kubectl exec -v=8 probe -- true 2>&1 | grep -iE 'upgrade|websocket|spdy|channel.k8s.io'
   ```

2. Same for port-forward, which uses a different sub-protocol:

   ```sh
   kubectl port-forward -v=8 pod/probe 18080:80 2>&1 | grep -iE 'portforward.k8s.io|upgrade' &
   sleep 3; kill %1
   ```

3. Now the authorisation surface. Build a principal that can *read* the exec subresource and
   nothing more:

   ```sh
   kubectl create serviceaccount execonly
   kubectl create role exec-get --verb=get --resource=pods,pods/exec
   kubectl create rolebinding exec-get --role=exec-get --serviceaccount=default:execonly
   SA=system:serviceaccount:default:execonly
   kubectl auth can-i get  pods/exec --as=$SA
   kubectl auth can-i create pods/exec --as=$SA
   ```

4. Try to use it. Predict the outcome from step 3 *before* running it:

   ```sh
   kubectl exec --as=$SA probe -- id
   ```

5. Grant only the missing verb and try again:

   ```sh
   kubectl create role exec-create --verb=create --resource=pods/exec
   kubectl create rolebinding exec-create --role=exec-create --serviceaccount=default:execonly
   kubectl exec --as=$SA probe -- id
   ```

6. Read the three gates at the pin, in
   `content/en/docs/reference/command-line-tools-reference/feature-gates/`:
   `AuthorizePodWebsocketUpgradeCreatePermission.md`, `TranslateStreamCloseWebsocketRequests.md`
   and `PortForwardWebsockets.md`. One question in writing: between v1.31 and v1.34, what verb
   did a WebSocket exec actually require, and what would step 4 have done on such a cluster?

7. `ExtendWebSocketsToKubelet` is beta from v1.36. Read its file and name the thing that had to
   graduate first before it could be relied on, and why a stream terminating at the kubelet
   rather than the API server is a different security question from the one in step 3.

**Expect** — steps 1 and 2 show a WebSocket upgrade, and the sub-protocol versions are the
tell: `v5.channel.k8s.io` for exec, `v2.portforward.k8s.io` for port-forward. No SPDY anywhere.

Step 3: `get` is allowed, `create` is not. Step 4 is **denied**, and the denial is the point —
the HTTP method on the wire is `GET`, the verb RBAC enforces is `create`, and the two no longer
match by accident. That mismatch is a synthetic check added in v1.35, not a property of the
protocol. Step 5 succeeds with `create` alone.

Step 6 is the exercise. On a v1.31 through v1.34 cluster, step 4 would have **worked** — a
principal with read-only intent getting an interactive root shell in a container, through a
default that had been announced as a transport improvement. Nothing in the 2024 post is wrong.
The post is simply not where that consequence was recorded, and no post was.

Write down one sentence you would apply to the next default flip you read about.

**Read on** — [KEP-4006](https://github.com/kubernetes/enhancements/tree/master/keps/sig-api-machinery/4006-transition-spdy-to-websockets):
find where authorisation is discussed. If it is thin, that is the finding — a KEP is a design
record, and what a design record omits is where the next four releases of surprises live.

**Teardown** — `kubectl delete pod probe --ignore-not-found; kubectl delete role exec-get exec-create --ignore-not-found; kubectl delete rolebinding exec-get exec-create --ignore-not-found; kubectl delete sa execonly --ignore-not-found`.
Then [tear the lab down](../../strands/lab-topologies.md#teardown).
