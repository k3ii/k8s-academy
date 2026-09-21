<a id="node-log-query-alpha"></a>

# Every command in this post still runs word for word, the release you are on is the last one where you must do what it says to make them run, and the `nodes/proxy` it tells you to grant is the right subresource for the API server and the wrong one for the kubelet standing behind it

**Post** — [Kubernetes 1.27: Query Node Logs Using The Kubelet API](https://kubernetes.io/blog/2023/04/21/node-log-query-alpha/),
2023-04-21.

3,881 bytes over 85 lines, by Aravindh Puthiyaparambil (Red Hat), seventy-second of the year's
seventy-eight posts by size and so the seventh smallest of them. It is a SIG Windows feature
announcement written for an alpha. It is also the only post in the archive that dates its own
amendment: grepping `blog/_posts` for the phrase *added to the article* returns exactly one line,
`:49`, recording that the warning above it arrived in early 2026 — three years after publication,
and one release before the feature went stable.

**As written**

The problem is stated in eight lines at `:13-21`. A cluster administrator debugging a service on a
node has to get onto the node, by SSH on Linux or RDP on Windows, to read that service's logs. The
post names Windows as the case that hurts most: a node reaches `Ready` and containers still do not
start, because of a CNI misconfiguration that nothing in the Pod status will tell you about.

The mechanism is four sentences at `:25-34`. The kubelet already serves a `/var/log/` viewer through
the node proxy endpoint, and *Node log query* supplements that endpoint with a shim: on Linux it
shells out to `journalctl`, on Windows to the `Get-WinEvent` cmdlet, and it reuses the filters those
two commands already have. It then describes a heuristic for callers who do not know whether a
service logs to the system logger or to a file — check the native logger first, and if that is not
available try `/var/log/<servicename>`, then `/var/log/<servicename>.log`, then
`/var/log/<servicename>/<servicename>.log`.

The assumptions and the permission are `:36-40`: journald and an installed `journalctl` on Linux,
the application log provider on Windows, and *fetching node logs is only available if you are
authorized to do so (in RBAC, that's **get** and **create** access to `nodes/proxy`)*. A warning
block follows at `:42-47` saying that granting `nodes/proxy` — even just **get** — also authorizes
executing commands in any container on the node, and linking the kubelet authentication and
authorization reference at its `#get-nodes-proxy-warning` anchor. Then `:49`, in italics and
parentheses: *this warning message was added to the article in early 2026*.

The recipe is `:53-58`. Enable the `NodeLogQuery` feature gate for that node, and set both kubelet
configuration options `enableSystemLogHandler` and `enableSystemLogQuery` to true. Three commands
follow. `:61` fetches a named service's logs, `:67` adds `&pattern=error` to filter them, and `:72`
fetches a file from `/var/log/` by putting a leading slash on the query value. All three are
`kubectl get --raw` against `/api/v1/nodes/<node>/proxy/logs/`. The post lists no other query
options; `:75-77` points at the documentation for those. `:79-85` asks for feedback on the
`#sig-windows` Slack channel and the SIG Windows mailing list.

**As it runs now**

Everything the post tells you to type still works, unchanged. That is the first thing, and it is
rarer in this archive than it sounds: the three commands at `:61`, `:67` and `:72` are byte-for-byte
the three commands the pinned concept page prints at `system-logs.md:276`, `:306` and `:283`, node
name and all. The post and the documentation for the feature have not diverged in three years and
five months, because the documentation was written from the post.

The second thing is that the opt-in the post describes is still required on the cluster this
exercise runs on, and will not be one release later. `NodeLogQuery` is beta and off by default
through v1.35, and stable and on from v1.36. The lab runs v1.35. That makes this the last release in
which a reader has to do what `:53-58` says in order for `:61` to work — which is a strange and
useful place to stand, because the same reader can watch the instruction be necessary and read the
page that says it has stopped being necessary, in the same session.

The third thing is the six query options. The post names one, `pattern`, and defers the rest to the
documentation. `system-logs.md:293-300` is that documentation: a six-row table giving `boot`,
`pattern`, `query`, `sinceTime`, `untilTime` and `tailLines`, one line of description each. `query`
is marked *(required)* there and nowhere in the post. The table is the complete reference for every
one of them — there is no expanded prose anywhere under `content/en` — so, for instance, nothing in
the pinned tree says whether `pattern` matches case sensitively. The only way to find out is to run
it.

The fourth thing is not a behaviour. Three times over, the pinned tree disagrees with itself about
this feature, and two of the three can be settled with a command.

The first disagreement is the default of `enableSystemLogHandler`.
`docs/concepts/cluster-administration/system-logs.md:255-256` says it *defaults to false and is
recommended to be left disabled unless actively debugging*. The generated API reference,
`docs/reference/config-api/kubelet-config.v1beta1.md:1587-1588`, says `Default: true`. They cannot
both be right, and the sample kubelet configuration at
`docs/tasks/administer-cluster/kubelet-config-file.md:279-280` writes the key explicitly as `true`
without settling which value it would have had if omitted. A node's own running configuration
settles it, and that is step 1.

The second disagreement is what the recipe becomes at v1.36. `system-logs.md:246-248` says the two
kubelet options must *both* be set to true. Two lines later, `:250-253` says the gate is now locked
to true, *leaving `enableSystemLogHandler` as the only option required to enable or disable the Log
Query feature* — which reads as `enableSystemLogQuery` no longer being needed. The v1.36 release
announcement, `blog/_posts/2026/kubernetes-v1-36-release/index.md:227`, says the opposite: *In
addition, the `enableSystemLogQuery` kubelet configuration option must also be enabled.* Three
statements, two of them four lines apart on one page. A v1.35 cluster cannot settle this one, and
this exercise does not pretend to; what it can do is show that at v1.35 the gate alone is not
enough, which is the only half of the question the lab ceiling reaches.

The third disagreement is about which subresource guards the log endpoint, and it is the one the
post is entangled in. `kubelet-authn-authz.md:66-75` maps kubelet API paths to resources and
subresources, and the row at `:72` reads `/logs/\*` → `nodes` → `log`. The fine-grained table added
under the `KubeletFineGrainedAuthz` gate repeats it at `:112`, and unlike `/pods`, `/healthz` and
`/configz` — which list `pods, proxy`, `healthz, proxy` and `configz, proxy` and so fall back — the
`/logs/\*` row names `log` alone. The post says `nodes/proxy`, and links that very page. Both are
true, of different hops: your request goes to the API server as `/api/v1/nodes/<node>/proxy/logs/`,
where the subresource is `proxy`, and the API server then makes a second request to the kubelet as
`/logs/?query=...`, where the subresource is `log` and the identity is not yours. The post collapses
two authorizations into one sentence. Steps 8 and 9 take them apart.

One more, and it is the reason the second hop is invisible on a kubeadm cluster.
`docs/setup/best-practices/certificates.md:119` puts `kube-apiserver-kubelet-client` in the group
`system:masters`. The note immediately below it, `:122-125`, says a less privileged group can be
used instead and that *kubeadm uses the `kubeadm:cluster-admins` group for that purpose* — present
tense, about the same certificate the table above just described differently. A command settles this
one too: read the certificate on the node.

**The diff, and why**

**Nothing broke, and saying only that would waste the post.** The three commands run. The recipe
works. The heuristic described at `:29-34` is in the concept page at `system-logs.md:286-289`, close
enough to the post's wording that the lineage is obvious. On the axis this archive usually measures
— does the reader's cluster still answer to what the post typed — this is as clean a *still right*
as 2023 has.

**The gate half of the recipe was retired by being agreed with, one release after this cluster's.**
`:53-58` tells you to enable a feature gate. From v1.36 there is no gate to enable:
`system-logs.md:250-253` records that it is locked to true, which is the same sentence pattern the
project uses for every graduation, and the instruction stops being something you do and becomes
something that already happened. The reader's problem in that world is not an error message —
correct instructions that became unnecessary produce no error at all. They produce a reader who
edits a kubelet config file, restarts a kubelet, and cannot tell whether the edit did anything. This
exercise is the last chance to watch the edit matter.

**The Windows half of the mechanism was never absorbed.** `Get-WinEvent` occurs in exactly one file
under `content/en`, and that file is this post. The asymmetry within the post's own sentence is the
evidence. Its Linux half names `journalctl`, and `journalctl` occurs in six files under `docs`, one
of which — `logging.md:183-184` — tells you outright to read the systemd journal with `journalctl -u
kubelet`. Its Windows half names `Get-WinEvent`, and `Get-WinEvent` occurs in no file under `docs`
at all. The nearest the concept page comes is *the application log provider* at
`system-logs.md:267-268`, which is the category and not the command. So for the question *what does
the kubelet actually invoke on a Windows node*, the pinned tree's only answer is a blog post from
2023 that no page under `content/en` links to. Grepping the whole checkout for
`node-log-query-alpha` returns the post and nothing else. Naming *still right* alone here would tell
a reader the post holds; it would not tell them that for one of the two operating systems the post
is the only thing that holds.

The gate itself is short and its stages are unremarkable, which is the point of transcribing it: the
release the beta stage closes on is what makes v1.35 the interesting seat.

`NodeLogQuery`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.27 – v1.29 |
| beta | `false` | — | v1.30 – v1.35 |
| stable | `true` | — | v1.36 – |

The file writes no `locked` key on any stage, and no `removed` key at all — it is one of the 257 of
487 gate files at the pin that are still listed. That absence is worth holding next to
`system-logs.md:251`, which says in prose that the gate *is now locked to true*: the gate file,
which is where this repository reads locking from, does not say so. Nine releases separate the alpha
from the stable, the beta stage runs six of them, and the stable stage is unbounded — open at v1.36
and still open at v1.37, the newest release the pin knows.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo), fresh. One node is enough and one
node is required: every step edits that node's kubelet configuration and restarts its kubelet, and
the thing under test is what a single kubelet will and will not serve. Bring the guest up with [the
five provision steps](../../strands/lab-topologies.md#provision), install Kubernetes with [the node
baseline procedure](../../strands/lab-topologies.md#node-baseline-steps), then `ssh
zain@10.10.10.180`. Steps 1 to 9 need the cluster; step 10 needs only the pinned tree.

**Do**

1. Read the node's running configuration before changing anything. The two options at the post's
   `:53-58` are the subject; the third print is the gate. Note which of the two disagreeing pages
   the first value agrees with.

   ```sh
   NODE=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl version -o json | python3 -c 'import sys,json; print("server:", json.load(sys.stdin)["serverVersion"]["gitVersion"])'
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" \
     | python3 -c 'import sys,json; c=json.load(sys.stdin)["kubeletconfig"]; print("enableSystemLogHandler:", c.get("enableSystemLogHandler")); print("enableSystemLogQuery:", c.get("enableSystemLogQuery")); print("featureGates:", c.get("featureGates", {}))'
   sudo grep -n 'enableSystemLog\|featureGates' /var/lib/kubelet/config.yaml || echo "neither key is in the file"
   ```

2. Run the post's first command unchanged, and then the endpoint the post says this feature
   *supplements*. One of the two works on a cluster that has done nothing.

   ```sh
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=kubelet" | head -5 || echo "refused"
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/" | head -20
   ```

   Record the exact refusal text from the first command. It is the message a reader who skipped
   `:53-58` will see, and it is not printed anywhere in the post or in the concept page.

3. Enable the gate and nothing else. This is the half of the recipe that `system-logs.md:250-253`
   says is the only half that matters from v1.36.

   ```sh
   sudo cp /var/lib/kubelet/config.yaml /var/lib/kubelet/config.yaml.bak
   printf 'featureGates:\n  NodeLogQuery: true\n' | sudo tee -a /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet; sleep 10
   systemctl is-active kubelet
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/configz" \
     | python3 -c 'import sys,json; print(json.load(sys.stdin)["kubeletconfig"].get("featureGates", {}))'
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=kubelet" | head -3 || echo "still refused"
   ```

4. Add the second option. The recipe from the post's `:53-58` is now complete, and this is the line
   where the post starts working.

   ```sh
   printf 'enableSystemLogQuery: true\n' | sudo tee -a /var/lib/kubelet/config.yaml
   sudo systemctl restart kubelet; sleep 10
   systemctl is-active kubelet
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=kubelet" | head -5
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=kubelet" | wc -l
   ```

5. Filter on the node, then run the same filter yourself, and find out what the one-line description
   of `pattern` at `system-logs.md:296` does not say.

   ```sh
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=kubelet" > /tmp/kubelet-all.log
   wc -l /tmp/kubelet-all.log
   grep -c 'error' /tmp/kubelet-all.log || true
   grep -c -i 'error' /tmp/kubelet-all.log || true
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=kubelet&pattern=error" | wc -l
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=kubelet&pattern=Error" | wc -l
   ```

6. Use the four options the post never mentions. They are the rest of the table at
   `system-logs.md:293-300`, and the post's `:75-77` is the sentence that sends you there.

   ```sh
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=kubelet&tailLines=5"
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=kubelet&boot=0" | wc -l
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=kubelet&boot=-1" | head -3 || echo "no previous boot"
   SINCE=$(date -u -d '-10 min' +%Y-%m-%dT%H:%M:%SZ)
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=kubelet&sinceTime=$SINCE" | wc -l
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=kubelet" | wc -l
   ```

7. Walk the heuristic at `:29-34` with a service that is not a service. Nothing on this node logs to
   a file under a directory named after itself, so make one, and then ask for it both ways — by
   name, which is the heuristic, and by path, which is `:72`.

   ```sh
   sudo mkdir -p /var/log/madeup
   printf 'line one\nline two error\nline three\n' | sudo tee /var/log/madeup/madeup.log > /dev/null
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=madeup"
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=/madeup/madeup.log"
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=containerd" | head -3
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=nosuchservice" || echo "nothing by that name"
   ```

8. Ask which subresource the API server checks for this path. The post names one at `:39-40`; the
   page it links names another. Grant each in turn to an identity that has nothing else. The
   exercise on [the dashboard the project marked
   dead](../2016/12-visualize-kubelet-performance-with-node-dashboard.md) already establishes that
   `get` on `nodes/proxy` is not read-only and quotes the warning that says so; what is open here is
   which of the two subresources this path consults, and whether the `create` half of the post's
   sentence is ever used.

   ```sh
   kubectl create sa logreader
   kubectl create clusterrole node-proxy-get --verb=get --resource=nodes/proxy
   kubectl create clusterrole node-log-get   --verb=get --resource=nodes/log
   kubectl create clusterrolebinding logreader-bind --clusterrole=node-proxy-get --serviceaccount=default:logreader
   SA=system:serviceaccount:default:logreader
   kubectl auth can-i get nodes/proxy --as=$SA; kubectl auth can-i get nodes/log --as=$SA
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=kubelet" --as=$SA | head -3
   kubectl delete clusterrolebinding logreader-bind
   kubectl create clusterrolebinding logreader-bind --clusterrole=node-log-get --serviceaccount=default:logreader
   kubectl auth can-i get nodes/proxy --as=$SA; kubectl auth can-i get nodes/log --as=$SA
   kubectl get --raw "/api/v1/nodes/$NODE/proxy/logs/?query=kubelet" --as=$SA | head -3 || echo "forbidden"
   ```

9. Ask which identity crosses the second hop, and read the certificate that makes the answer
   uninteresting on a kubeadm cluster. The last two prints settle `certificates.md:119` against the
   note at `:122-125`.

   ```sh
   sudo grep -n -A3 'authorization:' /var/lib/kubelet/config.yaml
   grep -n 'kubelet-client-certificate\|kubelet-client-key' /etc/kubernetes/manifests/kube-apiserver.yaml
   kubectl get clusterrole system:kubelet-api-admin -o jsonpath='{range .rules[*]}{.resources}{"\n"}{end}'
   kubectl get clusterrolebinding -o json \
     | python3 -c 'import sys,json; [print(b["metadata"]["name"], "->", [s.get("name") for s in b.get("subjects") or []]) for b in json.load(sys.stdin)["items"] if b["roleRef"]["name"]=="system:kubelet-api-admin"]'
   sudo openssl x509 -in /etc/kubernetes/pki/apiserver-kubelet-client.crt -noout -subject -issuer
   ```

10. Offline, in the pinned tree. Eight reads, in the order the argument was built.

    ```sh
    cd /path/to/kubernetes/website/content/en
    sed -n '244,256p' docs/concepts/cluster-administration/system-logs.md
    sed -n '1583,1599p' docs/reference/config-api/kubelet-config.v1beta1.md
    sed -n '68,75p;108,117p' docs/reference/access-authn-authz/kubelet-authn-authz.md
    sed -n '113,126p' docs/setup/best-practices/certificates.md
    sed -n '227p' blog/_posts/2026/kubernetes-v1-36-release/index.md
    grep -rl 'Get-WinEvent' --include='*.md' .
    grep -rl 'node-log-query-alpha' --include='*.md' .
    cat docs/reference/command-line-tools-reference/feature-gates/NodeLogQuery.md
    ```

**Expect**

Step 1 prints a v1.35 server. `featureGates` is empty — kubeadm sets none — and
`/var/lib/kubelet/config.yaml` has neither of the two keys the post names, so both values you read
come from the API type's defaults rather than from anything on this node. Expect
`enableSystemLogHandler: true` and `enableSystemLogQuery: false`, which makes
`kubelet-config.v1beta1.md:1587-1588` right and `system-logs.md:255-256` wrong about that default.
If your node prints `false` instead, that is the publishable result and the disagreement resolves
the other way; either way the running configuration is the tiebreak, because it is the only one of
the three sources that is not prose.

Step 2 is the split the post's `:25-26` describes and then never demonstrates. The bare
`/proxy/logs/` request succeeds and returns an HTML directory index of `/var/log` on the node — that
is the pre-existing viewer, enabled by `enableSystemLogHandler`, and it has nothing to do with this
feature. The `?query=kubelet` request fails. Record its wording; the useful part is that it comes
from the kubelet, not from the API server, so it arrives as a server error with a kubelet's message
inside it rather than as a `Forbidden`.

Step 3 is the measurement the second disagreement asks for, taken in the only direction a v1.35
cluster can take it. The gate is now in `featureGates` and the kubelet restarted cleanly, and
`?query=kubelet` still fails. On this release the gate is necessary and not sufficient, exactly as
`system-logs.md:246-248` says. What that does not tell you is whether `:250-253` is right about
v1.36, where the gate is no longer a variable; the release announcement at
`kubernetes-v1-36-release/index.md:227` says `enableSystemLogQuery` is still required there, the
concept page's second paragraph reads as though it is not, and nothing on this node can arbitrate
between them.

Step 4 is the post working. `?query=kubelet` returns journald lines for the kubelet unit — several
hundred to a few thousand, depending on how long the guest has been up — and the count from `wc -l`
is the whole unit log, because `system-logs.md:300` says `tailLines` defaults to fetching the whole
log. This is the post's `:61` with a real node name, and it has not changed in three years and five
months.

Step 5 produces three counts that should not all match. The case-sensitive `grep -c 'error'` count
is the smallest. The `pattern=error` count should equal or exceed the case-insensitive `grep -c -i`
count rather than the case-sensitive one, because `journalctl` treats an all-lowercase pattern as
case-insensitive — behaviour that `system-logs.md:296` does not mention, since its entire
documentation of `pattern` is the eleven words *pattern filters log entries by the provided
PERL-compatible regular expression*. `pattern=Error` carries an uppercase letter and should drop
back to case-sensitive matching. The finding is not the numbers; it is that a one-line table cell is
the complete reference for a filter whose semantics you can only discover by measuring them.

Step 6 walks the four options the post never names. `tailLines=5` returns five lines. `boot=0` is
the current boot and matches the unfiltered count. `boot=-1` asks for the previous boot and will
usually return nothing on a guest that has been rebooted once or not at all — journald on a fresh
Debian guest keeps a volatile journal unless `/var/log/journal` exists, so previous boots may not be
retained at all, which is a property of the node and not of this feature. `sinceTime` with an
RFC3339 timestamp ten minutes back returns a strict subset of the unfiltered count, and on a node
where you have just restarted the kubelet twice it will not be a small subset.

Step 7 walks the heuristic in all three of its branches. `?query=madeup` finds no journald unit by
that name, falls through to the file checks, and returns the three lines you wrote — that is
`/var/log/<servicename>/<servicename>.log`, the third and last branch of the post's heuristic at
`:33-34`. `?query=/madeup/madeup.log` returns the same three lines by the explicit path form the
post prints at `:72`, and the leading slash is what distinguishes the two. `?query=containerd`
returns journald lines, because containerd is a real unit on this node and the native logger is
checked first. `?query=nosuchservice` matches no unit and no file under any of the three names, and
fails.

Step 8 settles the post's `:39-40` in the post's favour, for the hop the reader can see. With only
`get` on `nodes/proxy`, `auth can-i` says yes for `nodes/proxy` and no for `nodes/log`, and the
impersonated request succeeds — so the API server authorizes this path on `proxy`, and `get` alone
is enough. Nothing in any of the post's three commands is an HTTP POST, so the `create` half of
`:39-40` is never exercised by anything the post asks you to do; `kubelet-authn-authz.md:56-64` maps
`create` to POST and the post issues none. With the binding swapped to `nodes/log`, the same request
is refused, which proves the API server never consults the subresource that the page the post links
assigns to `/logs/\*`.

Step 9 shows the hop the reader cannot see. The kubelet's own configuration has `authorization.mode:
Webhook`, so it does re-authorize, and the API server reaches it holding
`apiserver-kubelet-client.crt`. `system:kubelet-api-admin` lists `nodes/log` among its resources —
that ClusterRole exists for the second hop, and nothing on this cluster is bound to it. The
certificate subject prints `O = system:masters`, which means the identity crossing the second hop
bypasses RBAC entirely, which is why the `/logs/\*` → `nodes/log` row at `kubelet-authn-authz.md:72`
never bites here and why the post could collapse two authorizations into one clause without anybody
noticing. That also settles `certificates.md:119` against the note at `:122-125`: on a kubeadm
cluster at this version the table row is describing what actually happens and the note is describing
a different certificate.

Step 10, in order: the concept page's two adjacent paragraphs that disagree about whether
`enableSystemLogQuery` survives v1.36; the generated reference that disagrees with it about
`enableSystemLogHandler`, together with the security note the concept page compresses into one
clause; both authorization tables, printed back to back though forty lines separate them in the
file, agreeing with each other and with neither the post's sentence nor your step 8; the certificate
table and the note under it; the one line of the v1.36 announcement that is the third statement
about the recipe; and then the two greps that carry the *never absorbed* finding — `Get-WinEvent` in
one file, and `node-log-query-alpha` in one file, both of them this post. The gate file is
twenty-one lines with no `removed` key and no `locked` key.

**Read on**

1. `system-logs.md:286-300` — the heuristic and all six query options in one screen. Read the
   table's descriptions against what step 6 measured; `query` is the only one marked *(required)*,
   and it is the only one the post uses.

2. `kubelet-authn-authz.md:99-134` — fine-grained authorization in full. `KubeletFineGrainedAuthz`
   is beta and on by default at v1.35 and stable at v1.36, and it is what splits `/pods`, `/healthz`
   and `/configz` out of the `proxy` catch-all. `/logs/\*` was never in that catch-all, which is why
   this section changes nothing for this feature and everything for the rest of the kubelet API.

3. `certificates.md:113-126` — the whole certificate table and the note beneath it. It is worth
   reading for the general shape as much as for the disagreement: one row of that table is the
   reason the second authorization hop in step 9 has no visible effect.

4. `kubelet-config.v1beta1.md:1583-1599` — the generated reference for both options. It carries the
   sentence the concept page does not: enabling the query feature *has security implications* and
   the recommendation is to enable it on a need basis for debugging and disable it otherwise. That
   is the same advice `system-logs.md:255-256` attaches to the other option.

5. *Unanswerable from the pin:* whether `/logs/\*` ever mapped to `nodes/proxy`. The post says
   `nodes/proxy` at `:39-40` and the pin's tables say `nodes/log`, and both of the pin's tables are
   current-state documents with no history in them. The post's own `:49` records that the warning
   block was added in early 2026 without the sentence above it being touched, so an editor read that
   paragraph three years after publication and changed something else — but the pin cannot say
   whether the sentence was right when written, only that the page it now links disagrees with it.

**Teardown** — `sudo mv /var/lib/kubelet/config.yaml.bak /var/lib/kubelet/config.yaml;
sudo systemctl restart kubelet; sleep 10; systemctl is-active kubelet; kubectl delete
clusterrolebinding logreader-bind; kubectl delete clusterrole node-proxy-get node-log-get; kubectl
delete sa logreader; sudo rm -rf /var/log/madeup; rm -f /tmp/kubelet-all.log`. Restore the kubelet
configuration before anything else: a node left with `enableSystemLogQuery: true` serves every
service log on it to anyone who can reach the node proxy endpoint, which is the posture
`kubelet-config.v1beta1.md:1597-1598` tells you not to leave behind. Then
[tear the guest down](../../strands/lab-topologies.md#teardown).
