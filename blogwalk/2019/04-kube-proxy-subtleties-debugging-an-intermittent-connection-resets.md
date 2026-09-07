<a id="kube-proxy-subtleties-debugging-an-intermittent-connection-resets"></a>

# Kubernetes shipped one of this post's two mitigations, later found that it caused other problems, and now offers the other as a flag in the mode that will replace today's default, while the conntrack state the entire argument turns on is named exactly once in the pinned docs

**Post** — [kube-proxy Subtleties: Debugging an Intermittent Connection Reset](https://kubernetes.io/blog/2019/03/29/kube-proxy-subtleties-debugging-an-intermittent-connection-resets/),
29 March 2019, by Yongkun Gui (Google). 192 lines, 9,357 bytes. The frontmatter carries no
Kubernetes version; the post dates itself in its own body, where the fix it announces is
*"available in v1.15+"* (`:147`).

This is a debugging write-up, not an announcement, and it is the clearest packet-level account of
Service NAT anywhere in the archive. Almost all of its mechanism is still true. What has moved is
the ending. The post offers two ways to stop the resets, says the project has fixed the problem in
v1.15, and ships a DaemonSet for anyone who cannot wait. Seven years later the pin describes that
fix as something that *"was later found to cause other problems in some clusters"*, has the
successor proxy mode declining to install it at all, and offers the post's **other** suggestion —
the one the project did not ship — as a supported kube-proxy flag. The exercise is about that
reversal, and about how little of the post's diagnosis survived into the documentation that would
have to explain it.

**As written** — a user reports intermittent resets while serving large files over a `ClusterIP`
Service to Pods in the same cluster. Connectivity is fine and single downloads are fine; running
the workload *"in parallel across many clients"* reproduces it, and running the same workload on
VMs *"without Kubernetes"* does not (`:16-25`).

The background section builds the mechanism in three layers, because Kubernetes *"handles network
traffic from a pod very differently depending on different destinations"* (`:30-31`). Pod-to-Pod is
plain L3: *"every pod has its own IP address"*, Pods *"can ping each other"*, and CNI *"is the
standard that solves this problem for containers running on different hosts"* (`:35-41`).
Pod-to-external *"simply uses SNAT"* — *"replace the pod's internal source IP:port with the host's
IP:port"*, reversed on the way back, and *"transparent to the original pod, who doesn't know the
address translation at all"* (`:45-50`). Pod-to-Service goes to a Service, *"simply a L4 load
balancer in front of pods"*, whose most basic type is `ClusterIP`, with *"a unique VIP address that
is only routable inside the cluster"* (`:54-58`). The component that programs those rules is
kube-proxy, and *"the most important chains are `KUBE-SERVICES`, `KUBE-SVC-*` and `KUBE-SEP-*`"*
(`:60-65`): `KUBE-SERVICES` is *"the entry point for service packets"* and dispatches on
destination IP:port; `KUBE-SVC-*` *"acts as a load balancer"* and has *"the same number of
`KUBE-SEP-*` chains as the number of endpoints behind it"*; `KUBE-SEP-*` *"represents a Service
EndPoint"* and *"simply does DNAT"* (`:67-74`).

DNAT is what pulls conntrack in. Conntrack *"needs to remember the destination address it changed
to, and changed it back when the returning packet came back"*, and iptables can itself match on
conntrack state (`:76-79`). Four states are called out: *NEW*, *ESTABLISHED*, *RELATED*, and
*INVALID* — *"Something is wrong with the packet, and conntrack doesn't know how to deal with it.
This state plays a centric role in this Kubernetes issue"* (`:80-89`).

Then the good flow, in five bullets and a figure (`:91-105`): the client Pod sends to
`192.168.0.2:80`, iptables on the client node rewrites the destination to the Pod IP `10.0.1.2:80`,
the server replies to `10.0.0.2`, conntrack on the client node *"recognizes the packet and rewrites
the source address back to"* — and here the post gives `192.169.0.2:80` (`:100`), one digit away
from the address it opened with at `:95`.

The failure is packet 3 (`:107-134`). When conntrack cannot recognise a returning packet it marks
it *INVALID*; the post names two causes, *"conntrack cannot keep track of a connection because it
is out of capacity"* and *"the packet itself is out of a TCP window"*. And then the sentence the
whole post exists for: *"For those packets that have been marked as *INVALID* state by conntrack,
we don't have the iptables rule to drop it, so it will be forwarded to client pod, with source IP
address not rewritten"* (`:116-118`). The client sees a packet from the Pod IP rather than the
Service IP, does not recognise it, and RSTs the Pod IP directly. That RST is *"a totally legit
pod-to-pod packet"* (`:123`), the server has no idea any translation ever happened, and both ends
agree to close.

The remedy section (`:136-149`) lists *"at least 2 ways"*. Make conntrack more liberal, *"and don't
mark the packets as *INVALID*"*, which on Linux is `echo 1 >
/proc/sys/net/ipv4/netfilter/ip_conntrack_tcp_be_liberal` (`:141-143`). Or *"specifically add an
iptables rule to drop the packets that are marked as *INVALID*"* (`:144-145`). The fix, linked to a
pull request, is *"available in v1.15+"* (`:147`), and until then there is a DaemonSet (`:151-177`):
`apiVersion: extensions/v1beta1`, no `spec.selector`, `hostPID: true`, a `privileged: true`
container running `gcr.io/google-containers/startup-script:v1`, and a `STARTUP_SCRIPT` environment
variable whose value is a two-line shell script that writes the sysctl the first bullet named.

The summary is unusually candid: *"the bug has existed almost forever. I am surprised that it
hasn't been noticed until recently"*, because it *"happens more in a congested server serving large
payloads"* and *"the application layer handles the retry"* (`:181-185`).

**As it runs now** — take the two halves of the post separately, because they have had opposite
fates. The NAT half is still correct and the pin says most of it back in its own words. The
conntrack half is still correct and the pin says almost none of it at all.

**The pin restates the post's three-tier cascade in its own words, and names none of its chains.**
`virtual-ips.md:113-116`: kube-proxy *"installs a series of iptables rules which redirect from the
virtual IP address to more iptables rules, defined per Service. The per-Service rules link to
further rules for each backend endpoint, and the per-endpoint rules redirect traffic (using
destination NAT) to the backends."* That is `KUBE-SERVICES`, then `KUBE-SVC-*`, then `KUBE-SEP-*`,
in the same order and with the same job at each tier, described without a single chain name. The
next paragraph gives the post's other load-bearing fact — *"packets are redirected to the backend
without rewriting the client IP address"* (`:118-120`) — which is why the reply has to be
un-rewritten on the way back, which is why conntrack has to be in this story at all.

The chain names do exist in the pin, on exactly one page, and it is a debugging page rather than a
concept page. `debug-service.md:554-568` carries a literal `iptables-save` transcript and then the
cardinality rule the post gives in prose: *"For each port of each Service, there should be 1 rule
in `KUBE-SERVICES` and one `KUBE-SVC-<hash>` chain. For each Pod endpoint, there should be a small
number of rules in that `KUBE-SVC-<hash>` and one `KUBE-SEP-<hash>` chain."* This is the only file
in `content/en/docs` that names `KUBE-SEP` at all.

**The conntrack half has no counterpart anywhere in the documentation.** Search the whole
`content/en/docs` tree for the word `INVALID` and it occurs **once**: at
`kube-proxy-config.v1alpha1.md:804`, inside the description of a configuration field, in the
clause *"packets with out-of-window sequence numbers won't be marked INVALID"*. It is on no concept
page, no debugging page and no networking page. The four-state list, the state machine, the reply
tuple, the fact that a DNAT'd connection is only reversible because conntrack remembers it — none
of that is written down. The post is, at the pin, the documentation for the mechanism it is
debugging.

**The fix the post announces for v1.15 is now described as a liability, in a migration checklist.**
`virtual-ips.md:338-348` is the third bullet in a section called *"Migrating from `iptables` mode
to `nftables`"* (`:312`), listing things that *"work slightly differently"* in the new mode. Under
the heading *"Conntrack bug workarounds"*: *"Linux kernels prior to 6.1 have a bug that can result
in long-lived TCP connections to service IPs being closed with the error "Connection reset by
peer". The `iptables` mode of kube-proxy installs a workaround for this bug, but this workaround
was later found to cause other problems in some clusters. The `nftables` mode does not install any
workaround by default."* That is the post's second bullet — drop the *INVALID* packets — shipped,
regretted, and then not carried forward into the mode that `:83-87` says a future release will make
the default. The whole of this post's subject survives in the pinned tree as one bullet in a
checklist for people changing proxy mode, and the bullet does not explain the bug, name the state,
or say what the workaround looks like.

**The post's other suggestion — the one the project did not ship — is the supported one now.** The
same bullet finishes: *"you can run kube-proxy with the option `--conntrack-tcp-be-liberal` to work
around the problem in `nftables` mode"* (`:346-348`). That flag exists in the reference at
`kube-proxy.md:125-128`, described as *"Enable liberal mode for tracking TCP packets by setting
nf_conntrack_tcp_be_liberal to 1"*, and as a configuration field at
`kube-proxy-config.v1alpha1.md:798-804`, where `tcpBeLiberal` is a required member of
`KubeProxyConntrackConfiguration` alongside `maxPerCore`, `min`, `tcpEstablishedTimeout` and
`tcpCloseWaitTimeout`. So the post's first bullet — *"Make conntrack more liberal on packets"* — is
now a boolean in a ConfigMap, and the post's second bullet is the thing the pin warns you about.
The two mitigations have swapped places.

**One name in that bullet did move, and it is not the flag.** The post writes the sysctl as
`/proc/sys/net/ipv4/netfilter/ip_conntrack_tcp_be_liberal` (`:143`, and again inside the DaemonSet
at `:175`). The pin writes the same knob as `nf_conntrack_tcp_be_liberal` (`kube-proxy.md:128`).
The difference is not only the prefix: the post's is a path under `net/ipv4/netfilter/` and the
pin's is a name under `net/netfilter/`. Neither document mentions the other spelling, and only one
of the two is a file on a current kernel. A reader who pastes the post's line into a shell finds out
which; step 7 asks it deliberately instead.

**And the metric the pin tells you to use to make the decision is named two different ways in the
pin.** `virtual-ips.md:345` says to *"check kube-proxy's
`iptables_ct_state_invalid_dropped_packets_total` metric"*. The metrics reference at
`metrics.md:3087` gives the name as `kubeproxy_iptables_ct_state_invalid_dropped_packets_total`,
help text *"packets dropped by iptables to work around conntrack problems"*, stability ALPHA,
exported by kube-proxy on `/metrics`. Those are the only two occurrences of the string
`ct_state_invalid` in `content/en`, and they disagree about the component prefix. This one is
settled by a command rather than by reading, and the command is step 6. The reason it matters is
not pedantry: `virtual-ips.md:344-346` is the only instruction in the whole pinned tree that tells
you to make a decision about this bug from a measurement, and it gives you a string that may not
match anything.

**Two sentences on the same page leave a gap the page does not mention.** `virtual-ips.md:297-298`
says the `nftables` mode *"is only available on Linux nodes, and requires kernel 5.13 or later"*.
`virtual-ips.md:338-339` says the bug is in *"Linux kernels prior to 6.1"*. That is arithmetic, not
a claim the page makes, but the arithmetic is not subtle: a cluster on a 5.13-through-6.0 kernel can
run `nftables` mode, still has the bug, and by `:343` gets no workaround unless somebody passes the
flag. The page does not say this, and it is worth holding onto while reading the bullet's
instruction to go and look at a counter: the kernel range in which the migration is possible
overlaps the range in which the bug is live.

**The DaemonSet does not apply, for a reason that has nothing to do with conntrack.** The manifest
at `:151-177` is `apiVersion: extensions/v1beta1`, and it also has no `spec.selector`, and it pulls
from a registry that no longer serves. All three of those are somebody else's exercise; step 9 runs
the manifest once to see the first error and then stops.

**And one digit was wrong on the day it was published.** The good-flow list says the client sends
to `192.168.0.2:80` (`:95`) and, four bullets later, that conntrack *"rewrites the source address
back to 192.169.0.2:80"* (`:100`). Nothing in the mechanism changed; the second address is a typo
for the first. It is worth pointing at because of *where* it is: the entire failure mode is that in
the bad case the source is **not** rewritten back to the Service IP, so the one line in the post
that establishes what the correct Service IP is gives a different Service IP. The figure the list
introduces is at `:103-105`, and the exercise reads the prose rather than the image, because the
prose is the part a reader can check against a running cluster.

**What this exercise does not cover, and where it lives.** Proxy modes as a subject — the values of
`--proxy-mode`, IPVS, `nftables` as a mode rather than as a destination, the kube-proxy flag
inventory, the eleven `KUBE-*` ipsets, session affinity, and the fact that kube-proxy's mode is set
through a ConfigMap and not a command line — is
[the IPVS deep dive](../2018/04-ipvs-in-cluster-load-balancing.md), which also carries the
deprecation timeline for `ipvs`. Counting `KUBE-` chains as a *scale* measurement, and the
`NFTablesProxyMode` gate, are
[the 1.1 performance post](../2015/10-kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community.md);
step 3 reads specific chains for one Service rather than counting, which is a different act. The
`extensions/v1beta1` to `apps/v1` DaemonSet translation and the missing `spec.selector` are
[the DaemonSet post](../2017/04-kubernetes-statefulsets-daemonsets.md). The registry rename is
[the Deployment post](../2016/04-using-deployment-objects-with.md). What is left, and what this
file is for, is the conntrack half: the *INVALID* state, the two mitigations, and which of them the
project kept.

**The diff, and why** — five cases, and the interesting one is not the broken manifest.

**Still right, and unusually so.** The three-tier chain cascade, the DNAT, the reason conntrack has
to remember the translation, the four states, the un-rewritten reply, the client's RST, the server
agreeing to close: all of it holds at the pin, and the NAT half of it is restated on
`virtual-ips.md:113-120` in different words. A post from 2019 that needs almost no translation is
rare in this archive, and this one needs it in exactly one of its eight sections: the last, where it
says what to do.

**A plan the project abandoned.** The post gives two mitigations and reports that the project has
fixed the problem in v1.15. The pin says the shipped fix *"was later found to cause other problems
in some clusters"* and that the successor mode *"does not install any workaround by default"*
(`virtual-ips.md:341-343`). The remedy did not stop working; the project changed its mind about
whether it should be there. That is the abandoned-plan case in an unusual direction, because the
plan was not a forecast — it had already shipped.

**Overtaken by stasis, twice.** The sysctl the post writes by hand is spelled
`ip_conntrack_tcp_be_liberal` and the knob is now `nf_conntrack_tcp_be_liberal`
(`kube-proxy.md:128`); the metric the pin tells you to read is spelled one way on the concept page
(`virtual-ips.md:345`) and another in the metrics reference (`metrics.md:3087`). Neither is a change
in behaviour. Both are names that drifted while nobody was looking, and both cost a reader a failed
command.

**Wrong when it was published.** `:100` gives `192.169.0.2:80` where `:95` gives `192.168.0.2:80`.
One digit, in the one line that establishes what the correct rewritten source address is — the
address whose *absence* is the entire failure.

**And the post broke.** The mitigation DaemonSet is `extensions/v1beta1`, an API version
[the DaemonSet post](../2017/04-kubernetes-statefulsets-daemonsets.md) dates and cites from the
pin's deprecation guide. The reader who needed it most — someone on a pre-v1.15 cluster — is the
reader for whom it now cannot be applied at all, which is a closed loop of its own.

**No gate** — none of this was ever gated. Of the 488 feature-gate files in the pinned tree, **zero**
mention conntrack, liberal mode, or the *INVALID* state. Twelve gate files name kube-proxy, and
between them they govern proxy modes, endpoint handling, metrics endpoints, Windows behaviour and
the performance of rule-writing. None of them governs the workaround. The absence
is sharpest inside the migration checklist itself: the third bullet, the conntrack one
(`virtual-ips.md:338-348`), carries no `feature-state` shortcode, while the fourth bullet
immediately below it opens with one for `KubeProxyNFTablesLocalhostNodePorts` (`:350-352`). Two
adjacent behavioural differences in the same list, one gated and dated, one neither. Where a ladder
would have given release numbers, this exercise has to read the running machine instead: an
iptables rule and its counter, a metric endpoint, a sysctl, and a ConfigMap field. Steps 5 through 8
are that substitution.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair): a control-plane node at
`10.10.10.130` and a worker at `10.10.10.131`. Two nodes, because the post's mechanism is entirely
about the *client* node. The DNAT happens there, the conntrack entry lives there, the reply arrives
there and is rewritten there, and the RST is emitted from there. On one node the client and the
server share a host, so there is no way to tell whether the entry you are reading is the client's
bookkeeping or an artefact of locality, and the post's fourth bullet — *"the packet is going back
to the client node"* (`:99`) — has no referent. Bring it up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting `topology=pair`,
then [the node baseline](../../strands/lab-topologies.md#node-baseline-steps) on both, then
`ssh zain@10.10.10.130`. The control plane is where you stay; that is the client side.

Say plainly what this topology cannot show: **the reset itself.** The post reproduces the bug only
*"in parallel across many clients"* serving large files (`:20-21`), and its own author explains why
it stayed hidden for years — it *"happens more in a congested server serving large payloads"*
(`:182-184`). Out-of-window packets and a full conntrack table are what mark a reply *INVALID*, and
two 2-to-3 GB guests on a laptop will not produce either on demand. So nothing here reproduces the
symptom, and every counter this exercise reads will be zero. That is not a failed lab. The
machinery the bug rides on is completely visible at two nodes and one Service — the chains, the
DNAT, the conntrack entry and its reply tuple, the drop rule the project added and later regretted,
the metric that is supposed to tell you whether you need it, and the flag that replaces it — and
the state of the two mitigations is the thing this post's ending got wrong. Step 10 makes the
zero-counter problem explicit rather than hiding it.

**Do**

1. Establish what mode this kube-proxy is in, and read the pin's warning about that answer. The
   endpoint is the one `source-ip.md:82` names; the port is the `metricsBindAddress` default at
   `kube-proxy-config.v1alpha1.md:566-573`:

   ```sh
   curl -s http://127.0.0.1:10249/proxyMode; echo
   kubectl -n kube-system get cm kube-proxy -o jsonpath='{.data.config\.conf}' \
     | grep -nE '^mode:|^ *tcpBeLiberal:|^ *conntrack:'
   kubectl version -o json | grep gitVersion
   ```

   `virtual-ips.md:80-87` says the default *"In Kubernetes {{< skew currentVersion >}} … is
   `iptables`, but a future version of Kubernetes will change the default to `nftables`"*, and tells
   you to pin it. Note whether your `mode:` line is a pin or an empty string, because everything
   from step 5 onwards depends on which mode installs which workaround.

2. Put a Service across the node boundary, with the server on the worker and the client on the
   control plane you are sitting on. Derive the worker's node name from its address rather than
   guessing it:

   ```sh
   kubectl create deployment svr --image=registry.k8s.io/e2e-test-images/agnhost:2.53 \
     -- /agnhost netexec --http-port=8080
   W=$(kubectl get nodes -o json | python3 -c "
   import json,sys
   for n in json.load(sys.stdin)['items']:
     if any(a['address']=='10.10.10.131' for a in n['status']['addresses']):
       print(n['metadata']['name'])
   ")
   echo "worker=$W"
   kubectl patch deployment svr \
     -p "{\"spec\":{\"template\":{\"spec\":{\"nodeSelector\":{\"kubernetes.io/hostname\":\"$W\"}}}}}"
   kubectl rollout status deployment/svr --timeout=120s
   kubectl expose deployment svr --port=8080
   CIP=$(kubectl get svc svr -o jsonpath='{.spec.clusterIP}')
   POD=$(kubectl get pod -l app=svr -o jsonpath='{.items[0].status.podIP}')
   echo "clusterIP=$CIP podIP=$POD"
   curl -s -o /dev/null -w '%{http_code}\n' "http://$CIP:8080/"
   ```

   `$CIP`, `$POD` and `$W` carry through the rest of the exercise; if you open a new shell, set them
   again from the same three commands. The client here is the control-plane host rather than a Pod,
   which is a substitution worth naming: the chain traversal is identical, because kube-proxy's
   rules apply to host-originated traffic too, but the source address is the node's rather than a
   Pod's. Nothing in steps 3 to 8 depends on the difference.

3. Find the post's three chains for this one Service, and check the cardinality rule it states in
   prose against the one `debug-service.md:566-568` states in the pin:

   ```sh
   sudo iptables-save -t nat | grep -- "$CIP"
   SVC=$(sudo iptables-save -t nat | grep -- "$CIP" | grep -o 'KUBE-SVC-[A-Z0-9]*' | head -1)
   echo "svc chain=$SVC"
   sudo iptables-save -t nat | grep -- "-A $SVC"
   sudo iptables-save -t nat | grep -- "--to-destination $POD"
   kubectl scale deployment svr --replicas=3
   kubectl rollout status deployment/svr --timeout=120s
   sudo iptables-save -t nat | grep -c -- "-A $SVC .*KUBE-SEP-"
   ```

   The post claims *"Every `KUBE-SVC-*` has the same number of `KUBE-SEP-*` chains as the number of
   endpoints behind it"* (`:71-72`). You now have three endpoints. Compare the last number to three,
   and compare the `--to-destination` line to the post's description of `KUBE-SEP-*` as a chain that
   *"simply does DNAT, replacing service IP:port with pod's endpoint IP:Port"* (`:73-74`).

4. Read the conntrack entry — the thing packets 3 and 4 of the post turn on. The reply tuple is the
   rewrite, written down:

   ```sh
   sudo apt-get update && sudo apt-get install -y conntrack
   for i in $(seq 1 20); do curl -s -o /dev/null "http://$CIP:8080/"; done
   sudo conntrack -L -p tcp 2>/dev/null | grep -- "$CIP" | head -3
   sudo sysctl net.netfilter.nf_conntrack_count net.netfilter.nf_conntrack_max
   ```

   Each line has two tuples. The first is what you sent; the second is what conntrack expects back,
   and its `src=` is a Pod address while your `curl` was to a Service address. That asymmetry is the
   whole post: `virtual-ips.md:118-120` says *"packets are redirected to the backend without
   rewriting the client IP address"*, so the reply genuinely arrives from the Pod, and only the
   entry you are looking at makes it presentable to the client. Now re-read the post's `:95` and
   `:100` and decide which of the two addresses it gives is the typo.

5. Find the fix the post announces. `virtual-ips.md:341` says the `iptables` mode *"installs a
   workaround for this bug"* and nowhere says what it looks like, so look:

   ```sh
   sudo iptables-save | grep -i 'INVALID'
   sudo iptables-save -c | grep -i 'INVALID'
   sudo iptables -t filter -L -n -v | grep -B4 -i 'invalid'
   ```

   Write down three things: which chain the rule is in, what it matches on, and its packet counter.
   The post's second bullet asked for exactly *"an iptables rule to drop the packets that are marked
   as *INVALID*"* (`:144-145`); if you are in `iptables` mode you are looking at that request,
   granted. If you are in `nftables` mode you will find nothing here, and `virtual-ips.md:343` is
   why.

6. Settle the metric-name disagreement with a command instead of a page. `virtual-ips.md:345` and
   `metrics.md:3087` give the same metric two different names, and only one of them is what the
   process exports:

   ```sh
   M=ct_state_invalid_dropped_packets_total
   curl -s 127.0.0.1:10249/metrics | grep -c "^kubeproxy_iptables_$M"
   curl -s 127.0.0.1:10249/metrics | grep -c "^iptables_$M"
   curl -s 127.0.0.1:10249/metrics | grep 'ct_state_invalid'
   ```

   Three outcomes are possible and all three are informative: the prefixed name is there and the
   bare one is not, in which case `virtual-ips.md:345` hands you a string that matches nothing when
   anchored; neither is there, in which case the pin's only instruction for deciding about this bug
   has no instrument on your cluster; or the metric is present with a value, which on this lab it
   will not be. Record which.

7. Check the two spellings of the sysctl. The post writes one; the pin writes the other:

   ```sh
   ls -l /proc/sys/net/ipv4/netfilter/ip_conntrack_tcp_be_liberal 2>&1
   ls /proc/sys/net/ipv4/netfilter/ 2>/dev/null || echo 'no such directory'
   sudo sysctl net.netfilter.nf_conntrack_tcp_be_liberal
   ```

   The post's path is `:143`, repeated inside its DaemonSet at `:175`. The pin's name is in the flag
   description at `kube-proxy.md:128`. Only one of them is a file on this kernel.

8. Turn the post's *first* mitigation on through the path the project eventually built for it, and
   prove it reached the kernel on both nodes. Look before you substitute, because the inner document
   is a YAML string inside a ConfigMap and its indentation is not the outer file's:

   ```sh
   kubectl -n kube-system get cm kube-proxy -o yaml > /tmp/kp-orig.yaml
   sed -i '/resourceVersion:/d' /tmp/kp-orig.yaml
   cp /tmp/kp-orig.yaml /tmp/kp-liberal.yaml
   grep -n -A6 'conntrack:' /tmp/kp-liberal.yaml
   sed -i 's/^\( *\)tcpBeLiberal: false$/\1tcpBeLiberal: true/' /tmp/kp-liberal.yaml
   grep -n 'tcpBeLiberal' /tmp/kp-liberal.yaml
   ```

   If that last `grep` prints nothing the key was never serialised, and you add it under the block
   the first `grep` found instead:

   ```sh
   sed -i 's/^\( *\)conntrack:$/\1conntrack:\n\1  tcpBeLiberal: true/' /tmp/kp-liberal.yaml
   grep -n -A6 'conntrack:' /tmp/kp-liberal.yaml
   ```

   Then apply it, and check the knob rather than the log:

   ```sh
   kubectl -n kube-system replace -f /tmp/kp-liberal.yaml
   kubectl -n kube-system rollout restart ds kube-proxy
   kubectl -n kube-system rollout status ds kube-proxy --timeout=120s
   sudo sysctl net.netfilter.nf_conntrack_tcp_be_liberal
   ssh zain@10.10.10.131 'sudo sysctl net.netfilter.nf_conntrack_tcp_be_liberal'
   sudo iptables-save -c | grep -i 'INVALID'
   ```

   That last line is a question the pin does not answer: with liberal mode on, is the drop rule from
   step 5 still installed? `kube-proxy-config.v1alpha1.md:802-804` says only that *"packets with
   out-of-window sequence numbers won't be marked INVALID"*, which is about conntrack, not about the
   rule. Whatever you find, you found it here and not in the documentation.

9. Apply the post's mitigation DaemonSet, once, to see the first thing that stops it. Verbatim from
   `:151-177`:

   ```sh
   cat > /tmp/post-ds.yaml <<'EOF'
   apiVersion: extensions/v1beta1
   kind: DaemonSet
   metadata:
     name: startup-script
     labels:
       app: startup-script
   spec:
     template:
       metadata:
         labels:
           app: startup-script
       spec:
         hostPID: true
         containers:
         - name: startup-script
           image: gcr.io/google-containers/startup-script:v1
           imagePullPolicy: IfNotPresent
           securityContext:
             privileged: true
           env:
           - name: STARTUP_SCRIPT
             value: |
               #! /bin/bash
               echo 1 > /proc/sys/net/ipv4/netfilter/ip_conntrack_tcp_be_liberal
               echo done
   EOF
   kubectl apply --dry-run=server -f /tmp/post-ds.yaml
   ```

   One command, one error, and then stop. There are three separate reasons this manifest cannot
   work now and the API server only tells you about the first; the other two are named in the
   ceding paragraph above and belong to other files. What matters here is the last three lines of
   the manifest: a privileged container with `hostPID` whose entire job is to write the sysctl that
   step 8 just set with a boolean.

10. Make the decision the pin asks you to make, on both nodes, and then say why you cannot. This is
    the only instruction anywhere in the pinned tree that turns this bug into a number
    (`virtual-ips.md:344-346`):

    ```sh
    echo '== control plane 10.10.10.130'
    sudo iptables-save -c | grep -i 'INVALID'
    curl -s 127.0.0.1:10249/metrics | grep 'ct_state_invalid'
    echo '== worker 10.10.10.131'
    ssh zain@10.10.10.131 "sudo iptables-save -c | grep -i 'INVALID'"
    ssh zain@10.10.10.131 "curl -s 127.0.0.1:10249/metrics | grep 'ct_state_invalid'"
    ```

    Write the numbers down. On this lab they are zero, and zero is the answer to a different
    question than the one `virtual-ips.md:344-346` is asking. It says to check the metric *"to see
    if your cluster is depending on the workaround"*. A zero on an idle two-node cluster does not
    mean the cluster is not depending on it; it means nothing has been congested and no reply has
    arrived out of window. The instruction is sound and the instrument is honest — it is just that
    the measurement only becomes meaningful under the load the post describes at `:20-21`, which is
    the load this topology cannot generate. Note that as the exercise's limit, and note it as the
    reason the post existed: nobody found this bug by reading, and the pin's replacement for the
    post is a counter you have to have already been running.

**Expect**

Step 1: `iptables`, almost certainly, and a `mode:` line that is either absent or an empty string —
which is exactly the situation `virtual-ips.md:84-87` tells you to fix before an upgrade decides it
for you. Note whether `conntrack:` and `tcpBeLiberal:` appear at all; on a default kubeadm cluster
the ConfigMap is written from defaults and may carry neither.

Step 2: three commands' worth of setup and one `200`. The server Pod is on `10.10.10.131` and the
`curl` ran on `10.10.10.130`, so every rule and every conntrack entry you read from here on is the
client side of a cross-node Service connection — the left-hand half of the post's two figures.

Step 3: one rule in `KUBE-SERVICES` matching the ClusterIP and jumping to a `KUBE-SVC-` chain; that
chain containing one jump per endpoint; and a `--to-destination` line carrying the Pod IP and port.
After the scale to three, the count should be three. If it is not, wait for the rollout and count
again — the rules follow the EndpointSlice, not the Deployment. This is `debug-service.md:566-568`'s
rule confirmed on a live cluster, and it is also the post's `:71-72`, which is the same rule written
four years earlier and never contradicted.

Step 4: one or more lines, each with two tuples. The original tuple's `dst=` is the ClusterIP; the
reply tuple's `src=` is the Pod IP. That single line is packets 3 and 4 of the post, side by side:
the address conntrack will rewrite *from* and the address it will rewrite *to*. When it fails to
recognise a reply, the rewrite in the second half does not happen and the client sees the first
half's `src=`. The typo is at `:100` — the post's own good-flow narration puts the rewritten source
at `192.169.0.2`, one digit off the `192.168.0.2` the client sent to at `:95`.

Step 5: in `iptables` mode, a rule matching `INVALID` conntrack state with a drop or a jump to a drop,
and a counter of `0`. Record the chain name and the exact match, because the pin never gives either:
`virtual-ips.md:341` says only that a workaround is installed. You are looking at the granting of the
post's second request (`:144-145`), and at the thing `virtual-ips.md:342` says *"was later found to
cause other problems in some clusters"*. In `nftables` mode expect nothing, per `:343`.

Step 6: the two `grep -c` results should differ, and the difference is the defect.
`metrics.md:3087` gives the exported name with the `kubeproxy_` prefix, so an anchored search for the
string `virtual-ips.md:345` prints should find nothing. If both are zero, the metric is not being
exported on this build at all, and the pin's only decision procedure for this bug has no instrument
here. Either way the third command shows you the truth. This is the case where the pin disagrees
with itself and a command settles it; the answer is `metrics.md`, because a process's `/metrics`
output is what a metric's name *is*.

Step 7: the post's path does not exist. `/proc/sys/net/ipv4/netfilter/` is either absent or holds a
short list that does not include `ip_conntrack_tcp_be_liberal`; the live knob answers to
`net.netfilter.nf_conntrack_tcp_be_liberal` and reads `0`. Nothing about liberal mode changed. The
`ip_conntrack_*` compatibility names went away, and the post's mitigation instruction — the one it
gives as a bare shell line for a reader to paste — is the part of the post that a reader would hit
first and the part that no page in the pin corrects.

Step 8: `1`, on both nodes. If the first `sed` matched, you edited a field that was already there;
if you needed the second, you added a field the config API says is `[Required]`
(`kube-proxy-config.v1alpha1.md:798`) and the serialiser had still omitted. Either way the knob is
now set by a boolean in a ConfigMap, on every node, by the component that owns the rules — which is
the whole distance between this post and the pin. The last command is the open one: say whether the
INVALID drop rule is still installed alongside liberal mode. Both being present at once is not a
contradiction, since one changes what conntrack marks and the other changes what iptables does with
what is marked, but the pin never puts them in the same sentence and you now can.

Step 9: rejected, for the API version, which stops the request before the `spec` is ever read — so
the server never mentions the missing `selector` or the dead registry. The release that removed the
version, and the pinned line that records it, are in the DaemonSet post.
Note the shape of it: this is the one part of the post addressed to the reader in the worst
position, and it is the part that decayed hardest.

Step 10: zeros, twice, on both nodes, and the sentence you write about why. If the exercise leaves
one thing, let it be this: `virtual-ips.md:338-348` is a migration checklist that asks you to
consult a counter about a bug it does not explain, using a name it gets slightly wrong, to decide
whether to keep a workaround it says caused other problems, before moving to a mode that will not
install it — and the only document that explains any of it is a 2019 blog post whose own remedy
cannot be applied.

**Read on**

- [The IPVS deep dive](../2018/04-ipvs-in-cluster-load-balancing.md) works the same ConfigMap and
  the same `--proxy-mode` question from the mode side, and reads `virtual-ips.md` for the pin's
  deprecation dates. Take step 1's `proxyMode` answer to it and say which of the three Linux modes
  installs the workaround in step 5, which declines to, and which the pin never mentions in this
  connection at all.
- [The 1.1 performance post](../2015/10-kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community.md)
  counts `KUBE-` chains as a scale measurement and carries the `NFTablesProxyMode` gate. Read its
  gate against `virtual-ips.md:83-87` and give the release in which the default this exercise
  measured stops being the default.
- [The DaemonSet post](../2017/04-kubernetes-statefulsets-daemonsets.md) has the
  `extensions/v1beta1` to `apps/v1` translation and the `spec.selector` that became required. Take
  step 9's manifest there and finish it, then say what the finished DaemonSet would do that step 8
  did not.
- The pinned tree cannot answer one question this exercise raises: what the *"other problems in some
  clusters"* at `virtual-ips.md:342` were. No page names them, no gate dates them, and the only
  thing the documentation offers instead is the flag. Say what you would need in order to find out,
  and note that the answer is not in the pin — which is the same gap this post filled in 2019 and
  the reason it is still the best account of its own subject.

**Teardown**

```sh
kubectl -n kube-system replace -f /tmp/kp-orig.yaml
kubectl -n kube-system rollout restart ds kube-proxy
kubectl -n kube-system rollout status ds kube-proxy --timeout=120s
sudo sysctl net.netfilter.nf_conntrack_tcp_be_liberal
ssh zain@10.10.10.131 'sudo sysctl net.netfilter.nf_conntrack_tcp_be_liberal'
kubectl delete svc svr --ignore-not-found
kubectl delete deployment svr --ignore-not-found
rm -f /tmp/kp-orig.yaml /tmp/kp-liberal.yaml /tmp/post-ds.yaml
```

The ConfigMap is the only thing that must go back, and it is the one step here that is not
optional: a cluster left with `tcpBeLiberal: true` behaves differently from the one the next
exercise expects. Check the sysctl on both nodes afterwards and expect `0`. kube-proxy writes the
knob when liberal mode is on, and it has to write it back on restart; if it still reads `1` the
replace did not take, and `/tmp/kp-orig.yaml` is still there to try again. Nothing else
on either node changed. No packages were removed — `conntrack` from step 4 is a read-only tool and
`iptables` was already there — and no rule was added by hand, which is the point: every rule this
exercise read was installed by kube-proxy, and the one change it made was a field.
