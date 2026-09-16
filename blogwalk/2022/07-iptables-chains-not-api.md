<a id="iptables-chains-not-api"></a>

# The declaration this post exists to make reaches no page of documentation four years later, the chain it told third parties to stop depending on is still handed out in two working examples, and the one exception it never names is the only chain the reference now calls a hint

**Post** — [Kubernetes's IPTables Chains Are Not API](https://kubernetes.io/blog/2022/09/07/iptables-chains-not-api/),
2022-09-07.

8,732 bytes, 185 lines, one author: Dan Winship of Red Hat. Seventh of the thirteen `walk` verdicts
in 2022, and the first of them that announces a policy rather than a feature. There is no release in
its title and no version in its first paragraph. What it ships is a sentence about what other people
are allowed to assume.

**As written**

The post opens by naming the thing it wants to stop. Some Kubernetes components create iptables
chains as part of their operation; those chains were never intended to be part of any API or ABI
guarantee; and some external components use them anyway, `:10-15`, "in particular, using
`KUBE-MARK-MASQ` to mark packets as needing to be masqueraded". Then the declaration itself, at
`:17-22`: as part of the v1.25 release SIG Network made explicit that, with one exception, the
iptables chains Kubernetes creates are for Kubernetes's own internal use, and third-party components
should not assume any specific chain exists or that it contains any specific rules if it does.

The exception is never named. It is announced in a parenthesis at `:17` and the post moves on. The
only candidate it offers arrives at `:161`.

The reason the chains are now expendable is at `:40-44`: with the removal of dockershim in 1.24, the
kubelet "no longer ever uses any iptables rules for its own purposes", because hostPort mapping and
the rest are now the container runtime's or the network plugin's job. It nevertheless keeps creating
them, `:53-57`, despite no longer using them. Between those two facts sits the whole of KEP-3178.

`## Upcoming changes` is concrete, `:64-73`. The kubelet will stop creating `KUBE-MARK-DROP`,
`KUBE-MARK-MASQ` and `KUBE-POSTROUTING` in the `nat` table, and `KUBE-FIREWALL` in `filter` will
lose the functionality associated with `KUBE-MARK-DROP` and may eventually go away. This is phased
in through the `IPTablesOwnershipCleanup` feature gate, available for manual testing in 1.25. Then
the prediction, `:77-80`: "The current plan is that it will become enabled-by-default in Kubernetes
1.27, though this may be delayed to a later release. (It will not happen sooner than Kubernetes
1.27.)"

The back half is migration advice, one section per dependency. For `KUBE-MARK-MASQ`, `:90-93`, two
options: rewrite your rules to call `-j MASQUERADE` directly, or create your own alternative
mark-for-masquerade chain. The three paragraphs that follow explain why kube-proxy needs the
indirection at all — `DNAT` must run from `PREROUTING`, `MASQUERADE` from `POSTROUTING`, and
kube-proxy matches once rather than twice — and then say the quiet part, `:116-118`: many components
use `KUBE-MARK-MASQ` "because they copied kube-proxy's behavior without understanding why kube-proxy
was doing it that way". `KUBE-MARK-DROP` gets the same treatment in three shorter paragraphs,
`:127-142`.

The third section, `:144-178`, is the interesting one, and it is not about migrating away from
anything. Components that drive the host's iptables from inside a container need to know whether the
host is on `iptables-legacy` or `iptables-nft`. The `iptables-wrappers` module used to guess by
counting rules and assuming the kubelet had made a lot of them, a heuristic the cleanup breaks. So
the post offers a replacement, `:161-165`: since 1.24 the kubelet always creates a chain named
`KUBE-IPTABLES-HINT` in the `mangle` table of whichever subsystem it is using, and components can
look for that specific chain. A parenthesis at `:167-171` adds `KUBE-KUBELET-CANARY`, present since
1.17, as the older fallback.

Read those two halves together and the unnamed exception at `:17` has only one plausible referent.
The post never joins the sentences.

**As it runs now**

The prediction landed on the release it named. `IPTablesOwnershipCleanup` is alpha and off from
v1.25 to v1.26, beta and on at v1.27 and only v1.27, stable from v1.28 to v1.29, and its file
declares `removed: true`. There was no delay. The gate is one of 230 files under the pinned
feature-gates directory — out of 487 — that declare themselves removed, so it is also no longer
something you can set. Step 8 reads the ladder out of the file; the table itself, and the other
three removed gates it sits beside, belong to [The option this post buries in bullet two is still
the default eleven years later, and its replacement is locked
on](../2015/10-kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community.md).

The chain names survived the cleanup unevenly, and where they survived is the point. Across the
whole pinned content tree, `KUBE-POSTROUTING`, `KUBE-FIREWALL` and `KUBE-KUBELET-CANARY` appear only
in blog posts. `KUBE-MARK-DROP` and `KUBE-IPTABLES-HINT` appear in exactly one documentation file
each, and `KUBE-MARK-MASQ` in three. Those three files are the whole documented afterlife of the
chains this post was written about.

One of the three is the kubelet configuration reference, and it reads like a record of the cleanup.
`docs/reference/config-api/kubelet-config.v1beta1.md:1345-1347` describes `makeIPTablesUtilChains`
as causing the kubelet "to create the KUBE-IPTABLES-HINT chain in iptables as a hint to other
components about the configuration of iptables on the system" — the post's unnamed exception,
written down four years later as the field's entire purpose, in the reference rather than in a
concept page. Immediately below it, `:1355` and `:1365` document `iptablesMasqueradeBit` and
`iptablesDropBit` in the past tense: each "formerly controlled the creation of" its chain, each
"Deprecated: no longer has any effect", with the defaults 14 and 15 still printed beside them. The
fields outlived the chains because the configuration API could not drop them. The kubelet's
command-line flags could be dropped, and were: the flag reference lists exactly one iptables flag,
`--make-iptables-util-chains` at `:564`, and still describes it at `:567` as ensuring "iptables
utility rules are present on host" — plural, vague, and never updated. Meanwhile
`docs/reference/command-line-tools-reference/kube-proxy.md:209` still carries
`--iptables-masquerade-bit`, because kube-proxy still needs the bit the kubelet stopped setting.

The other two files are the ones this exercise is really about.
`docs/concepts/extend-kubernetes/compute-storage-net/network-plugins.md:101` and
`docs/tasks/administer-cluster/migrating-from-dockershim/troubleshooting-cni-plugin-related-errors.md:134`
both print a CNI plugin list in which the `portmap` entry carries `"externalSetMarkChain":
"KUBE-MARK-MASQ"`. That is a third-party component configured to depend on a Kubernetes-generated
chain: precisely the dependency the post exists to end, still offered as a working example on two
pages of the project's own documentation, one of them a troubleshooting page a reader arrives at
with something already broken.

Nothing anywhere under `docs/` repeats the declaration. KEP-3178 is named in three files at the pin,
every one of them a blog post: this one, the 1.25 deprecations round-up and the 1.28 release
announcement. No documentation page says the chains are not API, and the `nftables` migration list
at `docs/reference/networking/virtual-ips.md:314-350` names three behavioural differences between
the modes, none of which is that the chains a third party might be depending on do not exist there
at all. `:84` on the same page says a future version will change the default.

**What this exercise does not cover, and where it lives**

Following a ClusterIP through `KUBE-SERVICES`, `KUBE-SVC-`, `KUBE-SEP-` and out the far side of a
DNAT is [One ClusterIP, followed through four chains to a DNAT, and the chain name that is a hash of
the key](../../labs/07/16-a-clusterip-followed-to-its-kube-sep.md). That lab owns the walk, and owns
the conditional jump to `KUBE-MARK-MASQ` inside it. This exercise never follows a service. It only
asks which component put each chain there.

Comparing the backends is [Three backends, one table, and the one of them you will never
run](../../labs/07/22-three-backends-one-table.md), and replacing them entirely is [The same DNAT, a
third time: chains, then a verdict map, then a map entry with no netfilter in
it](../../labs/07/31-kube-proxy-replaced-by-map-lookups.md). IPVS as an announcement has its own
exercise in 2018. Nothing here changes `--proxy-mode`; every step below runs against whatever mode
the cluster already has, and reports it rather than setting it.

The `KubeProxyIPVS`, `MinimizeIPTablesRestore` and `SupportIPVSProxyMode` gates, and the
removed-gate set `IPTablesOwnershipCleanup` belongs to, are laddered in the 2015 exercise linked
above. Step 8 reads one file and does not reprint that table.

**The diff, and why**

**Still right, to the release number.** The post hedges in both directions — the plan is 1.27, it
may be delayed, and it will not be sooner — and then the gate goes to beta-on at v1.27 and nowhere
else. Stable at v1.28, gone after v1.29. A hedge that specific usually reads as a warning that the
date will slip; here it reads as a floor that held. Step 8 puts the sentence and the frontmatter
next to each other.

**Retired by being agreed with, and then kept as a fossil.** The cleanup happened. The kubelet no
longer creates the three `nat` chains, and the flags that controlled them are gone from the
kubelet's command line. But the configuration API is versioned, so `iptablesMasqueradeBit` and
`iptablesDropBit` could not simply be deleted; they are still there, still defaulted to 14 and 15,
documented in the past tense as having "formerly controlled" the creation of chains that no longer
get created. Two fields that do nothing, with defaults, in a stable API. Step 5 reads them off a
running kubelet.

**Right, and then named by the reference rather than by the post.** The exception at `:17` is never
spelled out. `kubelet-config.v1beta1.md:1345-1347` spells it out: the chain exists as "a hint to
other components". The post could only say that components *can now look for* the chain; the
reference says creating it for them is what the field is for. The same promotion did not reach the
flag reference, which at `:567` still describes the same setting as ensuring iptables utility rules
are present — the sentence from before there was one chain and a reason for it.

**Never absorbed.** The declaration is the post's whole payload, and four years on it exists only in
the post. No page under `docs/` says the chains are not API; KEP-3178 is cited in three blog posts
and no documentation page; and two documentation pages still hand the reader a `portmap`
configuration wired to `KUBE-MARK-MASQ`. The advice reached the code — `iptables-wrappers` was
updated before the post was even published, `:173-175` — and did not reach the prose. Step 7 shows
what the plugin does when nobody configures it that way, which is option (2) from `:92-93`, chosen
by the plugin on its own.

**The ladder**

`IPTablesOwnershipCleanup` has a feature-gate file at the pin even though the gate is gone: alpha
and `false` across v1.25 and v1.26, beta and `true` at v1.27 alone, stable and `true` across v1.28
and v1.29, then `removed: true`. Step 8 prints those four lines out of the frontmatter. The table
form, and the three other removed gates that sit with it, are already laddered in the 2015 exercise
named above, so this exercise reads the file and does not redraw it.

The gate you cannot set matters here in a specific way: because it is removed rather than merely
stable, there is no switch on the cluster that turns the old behaviour back on. The kubelet under
test has never created `KUBE-MARK-DROP`, and there is no way to ask it to. Everything step 3 finds
in the `nat` table was put there by something else.

**Topology**

[`solo`](../../strands/lab-topologies.md#solo) — one node, 4096MB, 4 cores, at `10.10.10.180`. Every
step needs a root shell on the node itself, because iptables is not something the API server will
show you: `ssh zain@10.10.10.180`. One pod is created, in a namespace of its own, and one chain is
deleted and allowed to come back. Nothing else on the node is modified.

**Do**

1. Establish the ground: the release, the node, and which backend kube-proxy is running. Nothing
   below changes it.

   ```sh
   ssh zain@10.10.10.180
   kubectl version
   kubectl get nodes -o wide
   kubectl -n kube-system get cm kube-proxy -o jsonpath='{.data.config\.conf}' | grep -E '^mode:|masqueradeBit|masqueradeAll'
   ```

2. Inventory what is actually on the node. Separate the per-service chains, which the post takes for
   granted, from the general-purpose ones, which are its subject.

   ```sh
   sudo iptables-save | sed -n 's/^:\([A-Z0-9-]*\) .*/\1/p' | grep '^KUBE' | sort -u > /tmp/kube-chains.txt
   wc -l < /tmp/kube-chains.txt
   grep -c 'KUBE-SVC-\|KUBE-SEP-\|KUBE-EXT-\|KUBE-FW-' /tmp/kube-chains.txt || true
   grep -v 'KUBE-SVC-\|KUBE-SEP-\|KUBE-EXT-\|KUBE-FW-' /tmp/kube-chains.txt
   for t in raw mangle nat filter; do
     printf '%-7s %s\n' "$t" "$(sudo iptables-save -t $t | grep -c '^:KUBE' || true)"
   done
   ```

3. Ask the four chains the post says will disappear whether they are there, in the tables it names,
   and count who jumps to each.

   ```sh
   for c in KUBE-MARK-DROP KUBE-MARK-MASQ KUBE-POSTROUTING; do
     echo "== nat $c"; sudo iptables -t nat -S "$c" 2>&1 | head -4
   done
   echo "== filter KUBE-FIREWALL"; sudo iptables -t filter -S KUBE-FIREWALL 2>&1 | head -4
   for c in KUBE-MARK-DROP KUBE-MARK-MASQ; do
     printf 'jumps to %-16s %s\n' "$c" "$(sudo iptables-save | grep -c -- "-j $c" || true)"
   done
   ```

4. Now the two chains in `mangle` the post offers as a replacement heuristic, and the subsystem they
   are a hint about.

   ```sh
   sudo iptables -V
   sudo iptables -t mangle -S KUBE-IPTABLES-HINT 2>&1
   sudo iptables -t mangle -S KUBE-KUBELET-CANARY 2>&1
   sudo iptables-save -t mangle | grep -c -- '-j KUBE-IPTABLES-HINT' || true
   ```

5. Read the surviving knobs off the running kubelet and off kube-proxy's configuration. This is the
   fossil layer.

   ```sh
   N=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
   kubectl get --raw "/api/v1/nodes/$N/proxy/configz" | tr ',' '\n' | grep -i iptables
   kubectl -n kube-system get cm kube-proxy -o jsonpath='{.data.config\.conf}' | grep -A4 '^iptables:'
   ```

6. Establish ownership the only way that is not an argument from documentation: delete the chain and
   see who puts it back. Nothing jumps to `KUBE-IPTABLES-HINT`, so removing it breaks no path.

   ```sh
   sudo iptables -t mangle -F KUBE-IPTABLES-HINT
   sudo iptables -t mangle -X KUBE-IPTABLES-HINT
   date +%T; sudo iptables -t mangle -S | grep -c 'KUBE-IPTABLES-HINT' || true
   sleep 90
   date +%T; sudo iptables -t mangle -S | grep -c 'KUBE-IPTABLES-HINT' || true
   sudo systemctl restart kubelet
   sleep 20
   date +%T; sudo iptables -t mangle -S | grep -c 'KUBE-IPTABLES-HINT' || true
   ```

7. Find out what the node's CNI plugin list actually asks for, then make it do some work and watch
   which chains it creates for itself.

   ```sh
   sudo ls /etc/cni/net.d/
   sudo grep -h 'type\|externalSetMarkChain' /etc/cni/net.d/*.conflist 2>/dev/null
   kubectl create ns ic
   kubectl -n ic apply -f - <<'EOF'
   apiVersion: v1
   kind: Pod
   metadata:
     name: hp
   spec:
     containers:
     - name: p
       image: registry.k8s.io/pause:3.10
       ports:
       - containerPort: 80
         hostPort: 31180
   EOF
   kubectl -n ic wait --for=condition=Ready pod/hp --timeout=90s
   sudo iptables -t nat -S | grep -- '-N CNI\|CNI-HOSTPORT'
   sudo iptables-save | grep -c -- '-j KUBE-MARK-MASQ' || true
   ```

8. Offline, against the pinned tree. Put the post's prediction next to the gate file that answered
   it.

   ```sh
   cd /path/to/kubernetes/website/content/en
   sed -n '77,80p' blog/_posts/2022/iptables-chains.md
   python3 - <<'PY'
   import yaml, glob, os
   G = "docs/reference/command-line-tools-reference/feature-gates"
   def front(path):
       return yaml.safe_load(open(path).read().split("---")[1])
   f = front(G + "/IPTablesOwnershipCleanup.md")
   for s in f["stages"]:
       print("%-7s default=%-5s %s - %s" % (s["stage"], s["defaultValue"],
             s["fromVersion"], s.get("toVersion", "")))
   print("removed:", f.get("removed"))
   n = tot = 0
   for path in sorted(glob.glob(G + "/*.md")):
       if os.path.basename(path) == "index.md":
           continue
       tot += 1
       if front(path).get("removed"):
           n += 1
   print("gate files: %d, declaring removed: %d" % (tot, n))
   PY
   ```

9. Offline. Count where each of the six chain names survives, split between documentation and blog.

   ```sh
   cd /path/to/kubernetes/website/content/en
   for c in KUBE-MARK-DROP KUBE-MARK-MASQ KUBE-POSTROUTING \
            KUBE-FIREWALL KUBE-IPTABLES-HINT KUBE-KUBELET-CANARY; do
     d=$(grep -rl "$c" --include='*.md' docs | wc -l | tr -d ' ')
     b=$(grep -rl "$c" --include='*.md' blog | wc -l | tr -d ' ')
     printf '%-22s docs %s  blog %s\n' "$c" "$d" "$b"
   done
   grep -rl 'KUBE-MARK\|KUBE-IPTABLES-HINT' --include='*.md' docs | sort
   ```

10. Offline. Run the declaration through the same test the other exercises in this archive use for
    absorption: does any page of documentation carry it, and does any page cite the post.

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -rl '3178' --include='*.md' docs | wc -l
    grep -rl 'iptables-chains-not-api' --include='*.md' docs | wc -l
    grep -rln 'iptables chains' --include='*.md' docs
    grep -rn '3178' --include='*.md' blog | cut -d: -f1 | sort -u
    sed -n '314,350p' docs/reference/networking/virtual-ips.md | grep '^- \*\*'
    ```

**Expect**

Step 1 reports a v1.35 server. The `mode:` line is almost certainly empty — kubeadm writes `mode:
""` into the ConfigMap and kube-proxy resolves an empty mode to `iptables` on Linux. An empty string
there is the default, not a missing value, and `masqueradeBit: 14` on the next line is the same 14
the kubelet still carries as a field that does nothing. Whatever the mode turns out to be, write it
down: every count below is a count for that backend, and a node running `nftables` will produce
almost none of them.

Step 2 finds that most of the `KUBE-` chains are per-service. On a cluster with only the default
services the split is roughly two thirds service-specific to one third general-purpose; add a
Service and two more chains appear. The general-purpose list is the post's real subject and it is
short — a dozen or so names across `nat`, `filter` and `mangle`, with `raw` usually at zero. Read it
before step 3 and mark which of the post's four names are in it. The per-table counts are the
cheapest way to see that this is not one table's problem: the cleanup the post describes spans
three.

Step 3 is the measurement the post set up. `KUBE-MARK-MASQ` and `KUBE-POSTROUTING` should both be
there, with rules in them and a non-zero jump count, because kube-proxy still needs the
mark-then-masquerade arrangement explained at `:104-112` — what the cleanup removed was the
kubelet's redundant copy, not kube-proxy's working one. `KUBE-MARK-DROP` is the one to watch. If
`iptables` answers `No chain/target/match by that name.` and the jump count is 0, that is KEP-3178
landed: nothing creates it and nothing wants it. If it is present, something on this node is still
asking for it and the jump count tells you how often. `KUBE-FIREWALL` may go either way; the post
only promises it will lose its function and says it "may eventually go away entirely", `:71-73`.
Report what you find rather than what this paragraph predicts.

Step 4 prints an `iptables` version string ending in `(nf_tables)` on any recent guest image, which
is the answer to the question the post's third section is about: this host is on `iptables-nft`.
`KUBE-IPTABLES-HINT` should exist in `mangle` and be empty — a bare `-N KUBE-IPTABLES-HINT` with no
rules under it and a jump count of 0. That emptiness is the whole design. It is not a chain that
does anything; it is a chain whose existence in one subsystem rather than the other is the message.
`KUBE-KUBELET-CANARY` may or may not still be there; the post itself says at `:168-169` that it may
go away.

Step 5 is the fossil layer, and the three lines the kubelet's `configz` returns are the point:
`makeIPTablesUtilChains` true, `iptablesMasqueradeBit` 14, `iptablesDropBit` 15. The first is the
only one that does anything, and what it does is create the empty chain from step 4. The other two
are live values, served by a running component, for settings the reference itself describes in the
past tense. Nothing is wrong. This is what a versioned configuration API looks like after a
behaviour is removed from underneath it. kube-proxy's block, printed underneath, carries a
`masqueradeBit` that is still connected to something.

Step 6 prints `0` immediately after the delete, then one of two things after ninety seconds. If it
prints `1`, the kubelet's periodic sync rebuilt the chain without being asked, which is the stronger
result. If it still prints `0`, the sync had not come round yet. Either way the third count, after
`systemctl restart kubelet`, prints `1`. That restart is the proof: no other component on this node
rebuilds this chain, and the one that does is the one whose configuration field in step 5 says it
will. If the third count is also `0`, check `makeIPTablesUtilChains` from step 5 before looking
anywhere else — a node with it set to `false` has no hint chain to delete and step 4 will have
failed first.

Step 7 lists the plugins the node actually runs and, on the `solo` build, prints `flannel` and
`portmap` and no `externalSetMarkChain` line at all. Then the hostPort pod makes `portmap` do work,
and the chains that appear are `CNI-HOSTPORT-DNAT`, `CNI-HOSTPORT-SETMARK` and `CNI-HOSTPORT-MASQ`.
`CNI-HOSTPORT-SETMARK` is the post's option (2) from `:92-93` — create your own alternative
mark-for-masquerade chain — chosen by the plugin, for itself, with no Kubernetes chain in the
picture. Compare that with the configuration on the two documentation pages named earlier, which
points the same plugin at `KUBE-MARK-MASQ` instead. The plugin has had a working answer for years.
The pages still print the other one. The final count is a control: it should match step 3's jump
count, unchanged, because nothing the pod did touched a `KUBE-` chain.

Step 8 puts four lines of hedged prose next to four lines of frontmatter. The post says the plan is
1.27, that it may be delayed, and that it will not be sooner. The gate file says `beta default=True
1.27 - 1.27`. Below that, `stable default=True 1.28 - 1.29` and `removed: True`, and the census of
the directory prints `gate files: 487, declaring removed: 230`. Nearly half the gates documented at
the pin are gates you can no longer set, which is worth knowing before the next exercise that greps
this directory.

Step 9 prints the table this exercise is built on. `KUBE-POSTROUTING`, `KUBE-FIREWALL` and
`KUBE-KUBELET-CANARY` come back `docs 0`. `KUBE-POSTROUTING` appears in two blog posts and the other
two in one each, which is this post. `KUBE-MARK-DROP` and `KUBE-IPTABLES-HINT` come back `docs 1`,
and `KUBE-MARK-MASQ` comes back `docs 3`. The listing underneath names the three files, and they are
the same three every time: the kubelet configuration reference, the network-plugins concept page and
the dockershim CNI troubleshooting page. Six chain names, three documentation files, and two of
those files are documentation telling you to depend on one of the names.

Step 10 prints zero, zero, nothing, three blog paths and three bullets. No documentation page
mentions KEP-3178, none links this post, and none contains the phrase `iptables chains` at all. The
three paths that do cite the KEP are all under `blog/`. The three bullets are the `nftables`
migration list, and reading them is the last thing to do: they are careful, specific and useful, and
not one of them mentions that the chains a third-party component might be depending on do not exist
in that mode. The post's declaration was correct, was acted on in code, and was never written down
anywhere a reader of the documentation would find it.

**Read on**

1. [The option this post buries in bullet two is still the default eleven years later, and its
   replacement is locked
   on](../2015/10-kubernetes-1-1-performance-upgrades-improved-tooling-and-a-growing-community.md) —
   read it for the ladder step 8 declines to redraw. `IPTablesOwnershipCleanup` is one of five gates
   laddered there, and four of the five declare `removed: true`. It is also where the claim that
   `iptables` is still the default and its replacement is locked on is established, which this
   exercise assumes in step 1 and never argues.

2. [One ClusterIP, followed through four chains to a DNAT, and the chain name that is a hash of the
   key](../../labs/07/16-a-clusterip-followed-to-its-kube-sep.md) — the inside of the chains this
   exercise only counts. Step 3 here reports that `KUBE-MARK-MASQ` has a non-zero jump count; that
   lab shows one of those jumps being taken, and why the rule that takes it is a conditional rather
   than an unconditional one.

3. [Kubernetes shipped one of this post's two mitigations, later found that it caused other
   problems, and now offers the other as a flag in the mode that will replace today's default, while
   the conntrack state the entire argument turns on is named exactly once in the pinned
   docs](../2019/04-kube-proxy-subtleties-debugging-an-intermittent-connection-resets.md) — three
   years earlier, the same table, and the opposite shape of outcome. That post's advice became a
   rule kube-proxy installs and then regrets; this post's advice became nothing anyone had to
   install, and was then not written down. The `nftables` migration bullets step 10 prints are where
   the two stories meet.

4. `docs/reference/config-api/kubelet-config.v1beta1.md:1341-1370` in the pinned tree, read as three
   consecutive entries rather than looked up one at a time. A field that creates a chain for other
   people's benefit, then two fields that used to create chains and now say so, with their defaults
   intact. Generated reference documentation is usually the least interesting thing in a docs tree;
   here it is the only place the cleanup is recorded at all.

5. Unanswerable from the pin: which chain the parenthesis at `:17` means. The post says the
   declaration holds "with one exception" and never returns to it. `KUBE-IPTABLES-HINT` is the only
   chain in the post that third parties are told to rely on, `:161-165`, and
   `kubelet-config.v1beta1.md:1345-1347` describes creating it as a hint to other components — which
   is as close to a confirmation as the pin offers. But the post was published in September 2022 and
   that field description could have been written at any time since, and the post never says the two
   are the same thing. Step 4 measures the chain. It cannot read the parenthesis.

**Teardown**

```sh
kubectl delete ns ic
rm -f /tmp/kube-chains.txt
```

Step 6 deleted a chain and restarted a kubelet, so check the chain is back before leaving: `sudo
iptables -t mangle -S KUBE-IPTABLES-HINT` should print one line. Nothing else on the node was
modified — every other command was a read — and the `CNI-HOSTPORT-` chains created in step 7 are
`portmap`'s to remove, which it does when the pod goes. If any of them survive `kubectl delete ns
ic`, give the kubelet a few seconds and look again rather than deleting them by hand; watching them
disappear on their own is the same ownership argument step 6 made, run by a different component.
