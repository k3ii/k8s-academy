<a id="nftables-kube-proxy"></a>

# The one incompatibility this post names by name now has an alpha gate that puts it back, the flag that expresses it carries three different value grammars across three pinned pages, and the config option that lowers its kernel floor is named in one sentence and in no reference at all

**Post** — [NFTables mode for kube-proxy](https://kubernetes.io/blog/2025/02/28/nftables-kube-proxy/),
2025-02-28.

12,940 bytes over 252 lines, the second-largest of the twelve 2025 walks by size, behind the sidecar
post's 13,166. One author, Dan Winship, writing from Red Hat. It is a page bundle, and the four SVG
charts beside the prose come to 483,202 bytes — thirty-seven times the text they illustrate. Three
of the four carry the first of the post's two arguments; the second argument gets the line
*"(Unfortunately I don't have cool graphs for this part.)"* at `:131` and no chart at all. The raw
numbers behind every chart live in a Google Sheets document linked at `:252`, outside the pin and
outside anything this exercise can check.

**As written**

The post announces that kube-proxy's nftables mode, alpha in 1.29 and beta at the time of writing,
*"is expected to be GA as of 1.33"*, and adds a parenthesis at `:14-15`: *"(For compatibility
reasons, even once nftables becomes GA, iptables will still be the default.)"* The two arguments for
the mode are structural. The first, at `:19-98`, is that the iptables ruleset kube-proxy writes
contains one top-level rule per Service IP and port, so first-packet latency is O(n) in the number
of Services; nftables writes one rule and a verdict map instead, and the charts show the percentile
curves flattening. The second, at `:100-131`, is that the iptables API forces an update proportional
to the number of Services on every sync even after the 1.26 partial-resync work, while the nftables
API allows updates proportional only to what changed.

Then four reasons not to switch, at `:133-177`. The code is new. The mode *"requires a 5.13 or newer
kernel"*, and you *"should not run kube-proxy in nftables mode on nodes that have an old (earlier
than 1.0.0) version of `nft` in the host filesystem"*. Other network components may not support it.
And, last, the mode is *"intentionally not 100% compatible"* with the iptables mode: there are old
defaults the project considered *"less secure, less performant, or less intuitive than we'd like"*,
and an opt-in mode was the chance to fix them without breaking anyone. The post names exactly one of
them, in a parenthesis at `:170-173`: *"with nftables mode, NodePort Services are now only reachable
on their nodes' default IPs, as opposed to being reachable on all IPs, including `127.0.0.1`, with
iptables mode."* For the rest it points at the migration section of the kube-proxy documentation,
which it says *"has more information about this, including information about metrics you can look at
to determine if you are relying on any of the changed functionality"*.

The closing section is a forecast. nftables is *"now the best kube-proxy mode"* but *"it is not the
default, and we do not yet have a plan for changing that"*; iptables will be supported *"for a long
time"*; IPVS has no immediate removal plan but is *"probably doomed in the long run"*.

**As it runs now**

**Both halves of the forecast held.** The gate reached stable at v1.33, the release the post named
three releases in advance, and `virtual-ips.md:83-84` still reads *"In Kubernetes {{< skew
currentVersion >}}, this is `iptables`"* at a pin whose newest release is v1.37. A post that
predicts a specific release for a specific graduation and gets it right is rare enough in this
archive to note. The gate's own ladder, and the question of what it means for a gate to be locked
while the default it governs does not move, are the 1.1 performance exercise's, and this file does
not restate them.

**The one incompatibility it names now has a gate that puts it back.** At `virtual-ips.md:352-361`
the migration checklist carries a fourth bullet the post could not have written: in the pinned
release *"you can enable localhost NodePorts in `nftables` mode by enabling the
`KubeProxyNFTablesLocalhostNodePorts` feature gate, and setting `--nodeport-addresses` to
`primary,localhost` rather than the default value of `primary`."* The gate file gives one stage,
alpha, defaulting to false, opening at v1.37 and closing nowhere. So the single behaviour the post
held up as the thing an opt-in mode let the project fix has, four releases after that mode went GA,
acquired a switch to un-fix it. `service.md:583-585` names the cost: the restored behaviour is
*"implemented by redirecting localhost NodePort connections through a userspace proxy, so it is not
as efficient as ordinary service proxying."*

**Three pinned pages give the flag three different value grammars.** `virtual-ips.md:322-325` says
the nftables mode defaults to `--nodeport-addresses primary` and that you override it with a CIDR,
offering `0.0.0.0/0` *"to listen on all (local) IPv4 IPs"*. `service.md:551-557` says the flag takes
IP blocks *or* one of three keywords, `primary`, `localhost` and `all`, and that `all` is the
default for the iptables and ipvs modes. The generated config reference at
`kube-proxy-config.v1alpha1.md:663-668` knows one keyword of the three: the field is *"a list of
CIDR ranges that contain valid node IPs, or alternatively, the single string 'primary'"*, and unset
means *"NodePort connections will be accepted on all local IPs"* — the iptables default stated as if
it were the field's, with no mention that the nftables mode overrides it. Step 2 asks the binary,
and step 8 tries all four spellings against it.

**The option that lowers the kernel floor is named once in the whole documentation tree.**
`kernel-version-requirements.md:51-52` says that *"for testing/development purposes, you can use
older kernels, as far back as 5.4 if you set the `nftables.skipKernelVersionCheck` option in the
kube-proxy config."* That names a field on `KubeProxyNFTablesConfiguration`. The generated reference
for that struct, at `kube-proxy-config.v1alpha1.md:978-1030`, lists exactly four fields —
`masqueradeBit`, `masqueradeAll`, `syncPeriod`, `minSyncPeriod` — and that is not one of them. The
string appears in one file in the pinned tree and in no reference page. Step 9 puts it in a
ConfigMap and reads what kube-proxy makes of it.

**Where the pin disagrees with itself: the kernel floor has an escape hatch on one page and none on
the other.** `virtual-ips.md:297-298` states the requirement flat, as a property of the mode: *"This
proxy mode is only available on Linux nodes, and requires kernel 5.13 or later."*
`kernel-version-requirements.md:46-52` states the same number and then gives the way underneath it,
down to 5.4, with the caveat that it *"is not recommended in production"*. Both are reference pages.
Neither links the other on this point, and a reader who arrives through the post's own link lands on
the one with no escape hatch. This exercise does not pick a winner; step 1 reads the node's kernel
against both, and step 9 tests whether the option that opens the escape hatch exists at all, which
is the half of the disagreement a command can reach.

**The `nft` floor moved by one patch release.** The post says not to run the mode on nodes carrying
an `nft` *"earlier than 1.0.0"*. `kernel-version-requirements.md:46-49` says the mode *"requires
version 1.0.1 or later of the nft command-line tool"*. The difference is one patch release wide and
it is the kind of number a reader copies into a preflight check, so it is worth knowing which of the
two a cluster is being held to. Step 1 reads the node's version against both.

**The phrase the post uses for the new behaviour is its own.** *"Their nodes' default IPs"* at
`:171-172` appears nowhere in the pinned documentation tree — not on the migration page, not in the
Service concept page, not in the generated reference. What those pages say instead is *"the node's
primary IPv4 and/or IPv6 address according to the Node object"*
(`kube-proxy-config.v1alpha1.md:666-668`), which is a different claim: it is the address the Node
object carries, not the address the node's routing table would choose. On a node with one interface
the two coincide, which is why the post's phrasing survived. Step 10 counts the occurrences.

**The promise about metrics is half kept, and the half that is missing is the dangerous one.** The
migration checklist has four bullets. Two of them hand you a metric to check before switching: the
conntrack bullet at `virtual-ips.md:345` and the localhost bullet at `:365`. The other two do not.
One of those two is the NodePort-interfaces change the post itself names, where the reader is left
to work out unaided which addresses their clients use. The other is the firewall bullet at
`:328-336`, which says the iptables mode adds accept rules for each NodePort *"in case that traffic
would otherwise be blocked by a firewall"* and that the nftables mode *"does not do anything here"*
— a change whose failure mode is traffic that silently stops arriving, and the one of the four for
which a metric would be worth most. Both metric names in the checklist are given without the prefix
the metrics reference carries; that disagreement is the connection-resets exercise's subject, but it
is worth recording that it happens twice, in adjacent bullets, which makes it a habit rather than a
slip.

**The nftables mode's own `minSyncPeriod` is documented as an iptables knob.** Inside
`KubeProxyNFTablesConfiguration`, the field's description at
`kube-proxy-config.v1alpha1.md:1024-1026` reads *"minSyncPeriod is the minimum period between
iptables rule resyncs"* and *"a value of 0 means every Service or EndpointSlice change will result
in an immediate iptables resync"*. The neighbouring `masqueradeBit` at `:999-1000` says iptables
too, but correctly — the fwmark space is shared. The `minSyncPeriod` text is the iptables struct's
copy, unedited, and it sits in the one struct whose existence answers the argument the post makes at
`:116-119`: that needing the knob at all is a symptom of the API the nftables mode exists to
replace. The knob itself is the IPVS deep dive's subject.

**Three typos, all on the two pages the post's own link reaches.** `virtual-ips.md:315-316` reads
*"some features work slightly differently the `nftables` mode"*, missing an "in".
`service.md:545-546` reads *"they are only available only on the node's primary IP"*, doubling the
"only". `service.md:551-552` offers *"one of more of the following keywords"* where it means "one or
more". None of them changes what a reader would do. They are here because a reader who has followed
the post's link and is reading these pages closely enough to run the exercise will notice them, and
it is better to have them counted than to wonder.

**What this exercise does not cover, and where it lives.** The `NFTablesProxyMode` gate's
ladder, the `SupportIPVSProxyMode` and `KubeProxyIPVS` ladders, the accepted values of
`--proxy-mode` as an inventory, counting `KUBE-` chains as a scale measurement, and the question
of what a *locked* gate means when the default it governs has not moved, are
[the 1.1 performance post](../2015/10-kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community.md).
Proxy modes as a subject — the ConfigMap that sets the mode, the kube-proxy flag inventory,
`minSyncPeriod` and `syncPeriod` as tuning knobs, and the IPVS deprecation timeline — is
[the IPVS deep dive](../2018/04-ipvs-in-cluster-load-balancing.md). The conntrack bullet, the
*INVALID* state, `--conntrack-tcp-be-liberal`, and the disagreement over whether the checklist's
metric names carry their `kubeproxy_` prefix are
[the connection-resets post](../2019/04-kube-proxy-subtleties-debugging-an-intermittent-connection-resets.md).
Which component put each chain in the table is
[the iptables-chains exercise](../2022/07-iptables-chains-not-api.md). Following a ClusterIP down to
a `KUBE-SEP` chain is
[the lab on that path](../../labs/07/16-a-clusterip-followed-to-its-kube-sep.md); reading the same
Service as a verdict map is
[the lab on verdict maps](../../labs/07/17-the-same-service-as-a-verdict-map.md); and comparing the
three backends in one sitting is
[the lab that puts them in one table](../../labs/07/22-three-backends-one-table.md).
What is left, and what this file is for, is one behaviour: which addresses a NodePort answers on,
what the pin says about changing that, and how many different accounts of it the pin holds at
once.

**The diff, and why** — four cases, and the one that matters arrived in the pin's newest release.

**Still right.** Both halves of the opening claim survived. GA landed in 1.33, exactly as forecast,
and iptables is still the default four releases later, exactly as the parenthesis at `:14-15`
promised. The structural argument survived too: nothing in the pin walks back the O(n) account of
the iptables ruleset or the claim that the nftables API updates incrementally, and the nftables
mode's section at `virtual-ips.md:305-310` repeats the reasoning in the project's own words.

**Broke.** Two of the post's four reasons not to switch have moved since it was published. The `nft`
floor is 1.0.1 at the pin, not 1.0.0. The kernel floor is still 5.13 on the page the post links to,
but a second reference page now lets a test cluster go to 5.4 with a config option the post could
not have mentioned. A reader following the post's preflight advice today would reject a node the pin
would accept, and accept an `nft` the pin would reject.

**Never absorbed.** The post's phrase for the new behaviour, *"their nodes' default IPs"*, never
entered the documentation; the pin says *primary address according to the Node object* instead,
which is a narrower and more accurate claim. Nor did the post's framing of the incompatibility as a
single parenthesised example: the pin's checklist has four entries, and the post's one is the only
one it names. The forward reference at `:174-177` — go and read the migration section, it lists the
metrics — is the load-bearing sentence of the post's whole compatibility argument, and it was
written against a section that half delivers on it.

**Overtaken by stasis.** *"We do not yet have a plan for changing that"*, at `:204-206`, is the
sentence the pin contradicts most directly and least usefully. `virtual-ips.md:83-87` now says that
*"a future version of Kubernetes will change the default to `nftables`"* and that you should
*"ensure that all clusters have a kube-proxy configuration that explicitly indicates which mode to
use"* to avoid the switch happening under you during an upgrade. A plan exists, then. It names no
release. Four releases after GA the documentation has moved from *no plan* to *a plan with no date*,
and the operational advice it hangs on that — pin your mode explicitly — is the same advice you
would give if there were no plan at all. Step 1 reads what the lab cluster's ConfigMap actually
says, which for most clusters is nothing.

**The ladder**

`KubeProxyNFTablesLocalhostNodePorts`

| stage | default | locked | releases |
|---|---|---|---|
| alpha | `false` | — | v1.37 – |

One row, and the right-hand column is open because the gate arrived in the newest release the pin
knows. It has never had a `lockToDefault`. The lab cluster runs v1.35, which is two releases before
this gate existed, so step 7 cannot enable it — and the refusal is the measurement, because what a
v1.35 kube-proxy says about a gate name it has never heard is a fact about how far the pin has
travelled past the cluster. The gate governing the mode itself, `NFTablesProxyMode`, is the 1.1
performance exercise's, and its ladder is not repeated here.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo). One node at `10.10.10.180`, and one is enough
because every measurement here is about which of a single node's own addresses answer on a port. The
second node a Service exercise usually wants would add nothing: the packet never leaves the box.
Bring the guest up with [the five provision steps](../../strands/lab-topologies.md#provision),
install Kubernetes with [the node baseline
procedure](../../strands/lab-topologies.md#node-baseline-steps), then `ssh zain@10.10.10.180`. The
cluster runs Kubernetes v1.35, two releases behind the pin, and steps 7 and 9 exist partly to
measure that gap. Everything is run on the node itself; there is nothing to do from the workstation
except read the pinned checkout in step 10.

**Do**

1. Record the starting position: the mode the cluster is actually in, and the two floors the post
   and the pin disagree about.

   ```sh
   kubectl -n kube-system get cm kube-proxy -o jsonpath='{.data.config\.conf}' \
     | grep -E '^ *(mode|nodePortAddresses|featureGates):'
   uname -r
   nft --version
   sysctl net.ipv4.conf.all.route_localnet
   kubectl version -o json | grep -m1 gitVersion
   ```

   Keep the whole ConfigMap for later, because every step from 5 onward edits it: `kubectl -n
   kube-system get cm kube-proxy -o yaml > /tmp/kp-orig.yaml`.

2. Ask the binary what the flag accepts. The three pinned pages give three different answers;
   kube-proxy's own help text is a fourth witness and the only one that ships with the code.

   ```sh
   KP=$(kubectl -n kube-system get pod -l k8s-app=kube-proxy -o name | head -1)
   kubectl -n kube-system exec $KP -- kube-proxy --help 2>&1 \
     | grep -A3 -E '^ +--(nodeport-addresses|proxy-mode|iptables-localhost-nodeports)'
   ```

   Write down, for `--nodeport-addresses`, whether the help text names `primary`, whether it names
   `localhost`, and whether it names `all`.

3. Stand up something that answers on a NodePort, and prove the iptables-mode behaviour the post
   describes: reachable on every local address, loopback included.

   ```sh
   kubectl create deployment svr --image=registry.k8s.io/e2e-test-images/agnhost:2.53 \
     -- /agnhost netexec --http-port=8080
   kubectl expose deployment svr --type=NodePort --port=8080
   kubectl rollout status deployment svr --timeout=120s
   NP=$(kubectl get svc svr -o jsonpath='{.spec.ports[0].nodePort}')
   echo "nodePort=$NP"
   curl -sS -m 5 http://10.10.10.180:$NP/hostname; echo
   curl -sS -m 5 http://127.0.0.1:$NP/hostname; echo
   ```

4. Read the metrics endpoint for the four names in play: the two the migration checklist gives you,
   and the two the metrics reference gives for the same counters.

   ```sh
   curl -sS 127.0.0.1:10249/metrics \
     | grep -E 'localhost_nodeports|ct_state_invalid' | grep -v '^#'
   curl -sS 127.0.0.1:10249/metrics | grep -c 'kubeproxy_sync_proxy_rules_nftables'
   ```

   The point is which spelling the endpoint answers to, not what the value is. Record the count from
   the second command as well, and take it again after step 5.

5. Switch the mode. This is the ConfigMap the IPVS exercise teaches; here it is only a lever.

   ```sh
   sed 's/^\( *\)mode: .*/\1mode: nftables/' /tmp/kp-orig.yaml > /tmp/kp-nft.yaml
   kubectl replace -f /tmp/kp-nft.yaml
   kubectl -n kube-system rollout restart ds kube-proxy
   kubectl -n kube-system rollout status ds kube-proxy --timeout=180s
   kubectl -n kube-system logs ds/kube-proxy | grep -i -m3 'proxy mode\|nftables'
   sudo nft list tables
   ```

6. Re-run step 3's two requests against the same Service, unchanged, on the same node.

   ```sh
   curl -sS -m 5 http://10.10.10.180:$NP/hostname; echo "  <- node IP"
   curl -sS -m 5 http://127.0.0.1:$NP/hostname; echo "  <- loopback"
   sysctl net.ipv4.conf.all.route_localnet
   sudo iptables-save | grep -c KUBE- || true
   ```

   That pair of requests is the whole exercise in two lines. Record the exact failure the loopback
   request gives, and whether the sysctl kube-proxy set in iptables mode is still set now that
   nothing uses it.

7. Try to get the loopback behaviour back the way the pinned migration section says to, on a cluster
   two releases older than the instruction.

   ```sh
   sed -e 's/^\( *\)mode: .*/\1mode: nftables/' \
       -e 's/^\( *\)nodePortAddresses: .*/\1nodePortAddresses: ["primary","localhost"]/' \
       -e 's/^\( *\)featureGates: {}/\1featureGates:\n\1  KubeProxyNFTablesLocalhostNodePorts: true/' \
       /tmp/kp-orig.yaml > /tmp/kp-localhost.yaml
   kubectl replace -f /tmp/kp-localhost.yaml
   kubectl -n kube-system rollout restart ds kube-proxy
   sleep 20
   kubectl -n kube-system logs ds/kube-proxy --tail=40
   kubectl -n kube-system get pod -l k8s-app=kube-proxy
   ```

   Record the message verbatim and which of the two changes it objects to — the gate name, the flag
   value, or both. If step 1 showed `featureGates` spelled as anything other than `{}`, the third
   `sed` will not match and the gate has to go in by hand before the replace.

8. Settle the value grammar against the running binary. Four spellings, one at a time; after each,
   restart kube-proxy and read whether it came up.

   ```sh
   for VAL in '["all"]' '["primary"]' '["0.0.0.0/0"]' 'primary'; do
     sed -e 's/^\( *\)mode: .*/\1mode: nftables/' \
         -e "s|^\( *\)nodePortAddresses: .*|\1nodePortAddresses: $VAL|" \
         /tmp/kp-orig.yaml > /tmp/kp-try.yaml
     kubectl replace -f /tmp/kp-try.yaml >/dev/null
     kubectl -n kube-system rollout restart ds kube-proxy >/dev/null
     sleep 20
     echo "$VAL -> $(kubectl -n kube-system get pod -l k8s-app=kube-proxy \
         -o jsonpath='{.items[0].status.containerStatuses[0].state}' | head -c 60)"
   done
   ```

   Four lines out. The interesting ones are `all`, which only one of the three pinned pages knows
   about, and the bare `primary` without brackets, which is how the generated reference phrases it.

9. Put in the option that no reference page lists, and see whether the binary has heard of it.

   ```sh
   sed -e 's/^\( *\)mode: .*/\1mode: nftables/' \
       -e 's/^\( *\)nftables:$/\1nftables:\n\1  skipKernelVersionCheck: true/' \
       /tmp/kp-orig.yaml > /tmp/kp-skip.yaml
   grep -A5 'nftables:' /tmp/kp-skip.yaml
   kubectl replace -f /tmp/kp-skip.yaml
   kubectl -n kube-system rollout restart ds kube-proxy
   sleep 20
   kubectl -n kube-system logs ds/kube-proxy --tail=30
   ```

10. Count the documentation, offline, in the pinned checkout. This is the step that turns the
    readings in this file into numbers you produced yourself.

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -rc 'default IPs' docs/ | grep -v ':0' || echo "default IPs: 0 files"
    grep -rln 'skipKernelVersionCheck' docs/
    grep -rln 'nodeport-addresses\|nodePortAddresses' docs/
    grep -rln 'KubeProxyNFTablesLocalhostNodePorts' docs/
    sed -n '978,1030p' docs/reference/config-api/kube-proxy-config.v1alpha1.md | grep -o '<code>[a-zA-Z]*</code>' | head -8
    ```

    Five counts. The last one is the field list of `KubeProxyNFTablesConfiguration`, and the thing
    to check is whether the option you just fed kube-proxy in step 9 appears in it.

**Expect**

Step 1 gives you a cluster in the default mode, which for a kubeadm install is the empty string —
not `iptables` spelled out, but nothing at all, which the binary resolves to the recommended
default. That is the configuration `virtual-ips.md:85-87` warns against keeping: a cluster with no
explicit mode is a cluster whose proxy backend changes when the project changes the default.
`nodePortAddresses` will be `null` and `featureGates` will be `{}`. The kernel will be well past
5.13 and `nft` well past 1.0.1, so the node clears both floors comfortably and neither the post's
numbers nor the pin's would have stopped you. `route_localnet` will read 1, because kube-proxy in
iptables mode sets it when the NodePort address set includes the loopback, which by default it does.
`kubectl version` will report v1.35.

Step 2 prints the flag's own account. Expect `--nodeport-addresses` to describe a list of CIDRs with
a documented special value, and compare what it names against the three pages: the generated
reference knows only `primary`, the Service concept page knows `primary`, `localhost` and `all`, and
the migration section knows `primary` and offers a raw CIDR for the rest. Whichever of those the
help text matches is the one written against the code. Note also that
`--iptables-localhost-nodeports` exists as a flag, which is the switch `service.md:571-573` names
for turning the old behaviour off in the mode that has it by default.

Step 3 gives two identical responses: the agnhost pod's hostname, once via `10.10.10.180` and once
via `127.0.0.1`. This is the iptables-mode behaviour the post calls *"less secure, less performant,
or less intuitive than we'd like"* — a Service you exposed on a node port is answering on the node's
loopback, where nothing outside the node can reach it and every process on the node can. Keep the
node port number; step 6 reuses it.

Step 4 is the first place the documentation's spelling is tested against the process. The checklist
at `virtual-ips.md:345` and `:365` names two counters without a prefix; the metrics reference names
the same two with `kubeproxy_`. Only one of those spellings will appear in the output, and the grep
is written loosely enough to catch either. Take the second count now and again after step 5. If it
is 0 here and non-zero there, the nftables sync counters are registered only by the backend that
owns them and the count is a cheap backend probe for the rest of the exercise; if it is non-zero in
both, the counters are registered unconditionally and `nft list tables` in step 5 is the check to
use instead.

Step 5 should roll cleanly. The log line names the mode, `nft list tables` shows a table called
`kube-proxy` that was not there before, and the DaemonSet comes back Ready within the timeout. If
the rollout stalls, the two floors from step 1 are the first thing to re-read — but on a node that
cleared them this is a routine restart. kube-proxy deletes its iptables rules on the way into
nftables mode, which is why the chain count in the next step is worth taking.

Step 6 is the measurement. The request to `10.10.10.180` still returns the hostname. The request to
`127.0.0.1` does not: expect a connection refused, immediately rather than after the five-second
timeout, because nothing is listening and nothing is redirecting. That is the post's one named
incompatibility, reproduced on one node in two lines, and it is the behaviour the alpha gate in the
ladder exists to restore. The sysctl will still read 1 — kube-proxy set it in iptables mode and does
not clear it on the way out — and the `KUBE-` chain count will have dropped to zero or near it,
because the rules that made the loopback work have been withdrawn.

Step 7 will not give you the loopback back, and the way it fails is the point. A v1.35 kube-proxy
has never heard of `KubeProxyNFTablesLocalhostNodePorts`, so expect the pod to fail to start with an
error naming the unrecognised gate, and the DaemonSet to sit in CrashLoopBackOff. If it complains
about the gate first, comment that line out and re-run to find out separately whether this release
accepts `localhost` as a `nodePortAddresses` value — `service.md:556` describes it as a keyword the
flag takes, and whether it takes it here is a release question, not a documentation question. Record
both answers; together they are the size of the gap between the pin and the cluster.

Step 8 prints four lines and settles the grammar question. `["primary"]` will be accepted; it is the
value all three pages agree on. Expect at least one of the other three to be rejected, and whichever
it is tells you which page was written against which release: `all` is named only by
`service.md:557`, `0.0.0.0/0` only by `virtual-ips.md:325`, and the unbracketed `primary` is how
`kube-proxy-config.v1alpha1.md:664` phrases it even though the field is typed as a list of strings.
A rejection shows up as a container state of `waiting` with a crash reason rather than `running`.

Step 9 answers the question the reference cannot. Either kube-proxy starts, in which case
`skipKernelVersionCheck` is a real field that the generated reference has not caught up with and
`kernel-version-requirements.md:51-52` is the only correct page about it; or kube-proxy refuses with
a strict-decoding error naming an unknown field, in which case the sentence on that page describes
an option this release does not have. One command distinguishes a documentation gap from a
documentation error, and this is the one place in the exercise where a command settles a
disagreement between two pinned pages rather than merely recording it.

Step 10 gives five counts to check against what you have read here: zero files containing the post's
phrase *"default IPs"*, one file containing `skipKernelVersionCheck`, four files naming the NodePort
address setting in one spelling or the other, and a short list for the gate. The last command prints
the field names of `KubeProxyNFTablesConfiguration` in source order; expect `masqueradeBit`,
`masqueradeAll`, `syncPeriod` and `minSyncPeriod`, and expect the option you fed the binary in step
9 not to be among them.

**Read on**

11. [The exercise on kube-proxy's chains](../2022/07-iptables-chains-not-api.md) — asks which
    component put each chain in the table. Take step 6's chain count there and say which of the
    chains it inventories survive the switch to nftables mode, and which table they move to.

12. [The exercise on the IPVS backend](../2018/04-ipvs-in-cluster-load-balancing.md) — works the
    same ConfigMap from the mode side and carries the deprecation timeline. Read its account of the
    third mode against this post's forecast that IPVS is *"probably doomed in the long run"*, and
    say what the pin has done about that in the four releases since.

13. [The exercise on the connection
    resets](../2019/04-kube-proxy-subtleties-debugging-an-intermittent-connection-resets.md) — owns
    the conntrack bullet of the same four-item checklist and the argument about whether its metric
    names carry their prefix. Its Read on asks for the release in which the default stops being
    `iptables`; take `virtual-ips.md:83-87` there and say whether the pin names one.

14. [The exercise on the 1.1 performance
    post](../2015/10-kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community.md)
    — carries the `NFTablesProxyMode` ladder and counts `KUBE-` chains as a scale measurement. Run
    its count on this node before and after step 5 and say what the nftables equivalent of that
    measurement would be.

15. [The lab that puts three backends in one table](../../labs/07/22-three-backends-one-table.md) —
    compares the modes side by side on one cluster. Take step 4's backend probe there and say which
    of the three it can tell apart without reading a ConfigMap.

**Teardown**

```sh
kubectl replace -f /tmp/kp-orig.yaml
kubectl -n kube-system rollout restart ds kube-proxy
kubectl -n kube-system rollout status ds kube-proxy --timeout=180s
kubectl delete svc svr --ignore-not-found
kubectl delete deployment svr --ignore-not-found
sudo nft list tables
rm -f /tmp/kp-orig.yaml /tmp/kp-nft.yaml /tmp/kp-localhost.yaml /tmp/kp-try.yaml /tmp/kp-skip.yaml
```

The ConfigMap must go back, and it is the one step here that is not optional: a cluster left in
nftables mode, or left with an explicit `nodePortAddresses`, behaves differently from the one the
next exercise expects. Confirm with `nft list tables` afterwards — the `kube-proxy` table should be
gone once kube-proxy has restarted in the original mode, because it withdraws its own table on the
way out exactly as it withdrew its iptables rules in step 5. Two things this exercise does not put
back, deliberately. `route_localnet` stays at 1 on the node; kube-proxy set it and kube-proxy will
set it again, and step 6 is the reason to have seen that it is not cleared. And the `agnhost` image
stays in the node's image store. Nothing else on the node changed: no packages installed, no kernel
parameters other than the one kube-proxy manages itself, and no files outside `/tmp`.
