<a id="kubeadm-use-etcd-learner-mode"></a>

# The feature gate this post asks you to switch on graduated and was deleted two releases later, the only sentence in the pinned tree that still uses the word learner sits inside a list of removed gates, and the guide the post sends you to for the procedure never mentions any of it

**Post** — [kubeadm: Use etcd Learner to Join a Control Plane Node Safely](https://kubernetes.io/blog/2023/09/25/kubeadm-use-etcd-learner-mode/),
2023-09-25.

Paco Xu (DaoCloud), alone. 111 lines, 5,381 bytes — the third-shortest of this year's thirteen
walks, against 12,890 for the longest. Its subject is a feature gate that the census's main
instrument cannot see, and it is the census's first `etcd` exercise.

**As written**

The frame is one sentence of mechanism and one of provenance. kubeadm "now supports etcd learner
mode", leveraging the learner feature "introduced in etcd version 3.4" (`:10-13`), and "By default,
kubeadm runs a local etcd instance on each control plane node" (`:14-15`). Then: "In v1.27, kubeadm
introduced a new feature gate `EtcdLearnerMode`. With this feature gate enabled, when joining a new
control plane node, a new etcd member will be created as a learner and promoted to a voting member
only after the etcd data are fully aligned" (`:17-19`).

*What are the advantages of using etcd learner mode?* is four numbered claims, and they are claims
about failure rather than about features. Learner nodes "catch up with the leader's logs before
becoming fully operational. This prevents new cluster members from disrupting the quorum or causing
leader elections" (`:26-29`). Traditional member additions "often result in cluster unavailability
periods, especially in slow infrastructure or misconfigurations" (`:30-32`). Learners are "a safer
and reversible way to add or replace cluster members" (`:33-35`). And under network partition,
"Depending on the partition a new member lands, it can seamlessly integrate with the existing
cluster without causing disruptions" (`:36-38`).

*How nodes join a cluster that's using the new mode* is the procedure. It defers the general case to
[Creating Highly Available Clusters with
kubeadm](/docs/setup/production-environment/tools/kubeadm/high-availability/) (`:47-48`), then gives
two ways to turn the gate on: a commented-out `kubeadm init --feature-gates=EtcdLearnerMode=true`
above the command it actually recommends, and a four-line `ClusterConfiguration` carrying
`featureGates: EtcdLearnerMode: true` at `apiVersion: kubeadm.k8s.io/v1beta3` (`:52-64`). Before
joining, "ensure that the existing control plane nodes and all etcd members are healthy" (`:70-71`)
— checked with `etcdctl member list` against the local endpoint using the three PKI paths under
`/etc/kubernetes/pki/etcd/`, and a note that if `etcdctl` is not available you should run it in a
container through the runtime directly, "using a tool such as `crictl run` and not through
Kubernetes" (`:73-75`). One line of sample output is printed (`:85`), and a note recommends an odd
number of members (`:91-93`).

*What's next* forecasts one thing and links one: the gate "is alpha in v1.27 and we expect it to
graduate to beta in the next minor release of Kubernetes (v1.29)" (`:99-100`), and etcd has an open
issue that "may make the process more automatic" (`:101-102`). The last bullet points at the kubeadm
[configuration format](/docs/reference/config-api/kubeadm-config.v1beta3/) (`:103`). *Feedback*
names the SIG Cluster Lifecycle meeting, kubeadm office hours, `#kubeadm` on Slack and the mailing
list (`:105-111`).

**As it runs now**

The forecast was honoured exactly, and then overtaken. kubeadm's own removed-gates table records
`EtcdLearnerMode` as alpha 1.27, beta 1.29, GA 1.32, removed 1.33 (`kubeadm-init.md:170`) — beta in
v1.29, the release the post named, and gone eight releases before the pin. The same page states the
rule that governs it one section earlier: "Feature gates are removed after a feature graduates to
GA" (`:137`). So the post's central instruction, in both of the forms it offers, is now a command
that fails. There is nothing to enable, and the behaviour it enabled is what kubeadm does.

The word *learner* occurs exactly once under `content/en/docs` at the pin. Not once per page: once
in the tree. It is at `kubeadm-init.md:188`, inside the description block for a gate the same page
has just listed as removed: "When joining a new control plane node, a new etcd member will be
created as a learner and promoted to a voting member only after the etcd data are fully aligned."
That sentence is the post's `:17-19` almost verbatim, and it is now the tree's entire documentation
of kubeadm's unconditional behaviour, filed under *List of removed feature gates*.

The guide the post defers to says nothing about it. `high-availability.md` is 448 lines at the pin
and still teaches both topologies; its *Steps for the rest of the control plane nodes* (`:251-264`)
is the join the post is about, annotated with what `--control-plane` and `--certificate-key` do, and
it never mentions learners, never asks you to check whether the new member is voting, and never
tells you the safety property changed. `kubeadm-join.md:42` describes the same step as "Adding new
local etcd member" and stops there. A reader who learns the procedure from the pinned documentation
learns a procedure that is safer than the page describes, and is not told why.

The pinned reference disagrees with itself about what the phase is called. The generated page
`kubeadm_join_phase_etcd-join.md` gives the synopsis "Join etcd for control plane nodes" and the
invocation `kubeadm join phase etcd-join [flags]` (`:16-19`), and then its own *Examples* block,
three lines later, reads `kubeadm join phase control-plane-join-etcd all` (`:26`) — a different
command name, carrying an argument the synopsis does not take. The sibling page for
`control-plane-join` shows the matching-example form, so the divergence is in this file alone. The
phase named twice is the phase where the learner is added and promoted, so it is worth knowing which
name the binary answers to. Step 8 asks it.

Two of the post's incidentals aged in opposite directions. Its `etcdctl` invocation still works
verbatim, paths and all, because `/etc/kubernetes/pki/etcd/` has not moved — and its one line of
sample output (`:85`) already contains the answer to the post's own subject: the last field of an
`etcdctl member list` row is `IsLearner`, so the `false` printed there is the column this whole post
exists to change, shown without being named. Its configuration sample, by contrast, is written at an
API version whose fate is settled by the exercise linked below, and its *What's next* pointer to the
`v1beta3` reference page leads somewhere that is still generated but no longer current
(`kubeadm-init.md:141` points readers at `v1beta4`).

What cannot be settled from the pin is whether the etcd issue at `:101-102` was ever resolved. It is
a link to an `etcd-io/etcd` issue and not to anything in the Kubernetes tree, and nothing under
`content/en` refers to auto-promotion of learner members at all. The `kubernetes/website` pin can
say what kubeadm does; it cannot say what etcd decided.

**What this exercise does not cover, and where it lives**

Both of kubeadm's feature-gate tables are transcribed in full, and the one gate name that appears in
both registries is argued, by [the kubeadm-arrival
exercise](../2016/09-how-we-made-kubernetes-easy-to-install.md). That transcription is the ladder
for this post, and it is not repeated here. The attempt to join a control-plane node to a cluster
built without `controlPlaneEndpoint`, the load-balancer argument, and `kubeadm config migrate`
between config versions all belong to [the kubeadm HA exercise](../2019/07-kubeadm-ha-v115.md);
whether the `v1beta3` deprecation notice has outlived its own removal release belongs to [the swap
exercise earlier this year](08-swap-linux-beta.md). Adding and removing raw etcd members by hand,
and what quorum does when you get it wrong, is [the etcd phase's own
work](../../labs/02/24-the-on-disk-trio.md).

**The diff, and why**

This is the ***retired by being agreed with*** case in its plainest form, and it is worth being
careful about which case that is. The post did not forecast something the project then abandoned; it
forecast beta in v1.29 and got beta in v1.29, and the feature kept climbing until the gate that
carried it was deleted because there was no longer anything for it to switch. The thing the post
tells you to turn on stopped being a separate thing. Every reader instruction it gives is therefore
dead, and every behavioural claim it makes is live.

One half ***broke*** in the ordinary way. `kubeadm init --feature-gates=EtcdLearnerMode=true` and
the `featureGates` stanza both fail at the pin, and they fail with a message about an unknown gate
rather than about a removed one, which is a worse failure than it sounds: a reader who hits it has
no way to tell from the error whether they mistyped a live gate or typed a dead one correctly.

The rest is ***still right***, including the four advantage claims, which the pin's behaviour now
demonstrates without being asked. The pressure behind all of this is visible in one sentence of
kubeadm's own documentation — "Feature gates are removed after a feature graduates to GA"
(`kubeadm-init.md:137`) — a policy that the core feature-gates directory does not follow, since it
keeps 230 removed gates as files with full stage tables. kubeadm's registry forgets; the core
registry remembers. This post is the clearest case in the census of what that difference costs a
reader.

**No gate** — not in the sense that the subject has none, but in the sense that the census's
instrument cannot see it. None of the 487 gate files under
`content/en/docs/reference/command-line-tools-reference/feature-gates/` names `EtcdLearnerMode`, and
neither does the removed-gates page that accompanies them. kubeadm keeps its own registry, as two
markdown tables inside `kubeadm-init.md` (`:150-154` and `:166-177`), with a different schema: one
row per feature, stages as columns, no `default` column in the removed table and no `locked` column
in either. Both tables are transcribed losslessly by the kubeadm-arrival exercise linked above, so
there is no ladder to build here. What this exercise reads instead is the binary's exit status and
etcd's own member list.

**Topology**

[`ha`](../../strands/lab-topologies.md#ha) — three stacked control-plane nodes, 2560MB and 2 vCPU
each, untainted, at `10.10.10.150` to `10.10.10.152`. This is the one exercise in the census that
needs it: the subject is what happens to an etcd cluster *while* a second and third member are
joining, and that cannot be inspected on a cluster that never grows. Provision with the [standard
steps](../../strands/lab-topologies.md#provision), then run the [node
baseline](../../strands/lab-topologies.md#node-baseline-steps) on all three guests. The lab runs
Kubernetes v1.35, three releases past the one that deleted the gate.

One honest limitation, stated up front: `--control-plane-endpoint` here is the first node's own
address and not a load balancer, so this cluster is highly available in its etcd quorum and not in
its API endpoint. That is the right trade for this subject and the wrong one for production; the
exercise that reads the load-balancer requirement properly is linked above.

**Do**

1. Stand the first control plane up. The endpoint flag is not optional here even though there is no
   load balancer — a cluster initialised without it cannot be joined to at all.

   ```sh
   # on 10.10.10.150
   sudo kubeadm config images pull
   sudo kubeadm init \
     --control-plane-endpoint=10.10.10.150:6443 \
     --apiserver-advertise-address=10.10.10.150 \
     --pod-network-cidr=10.244.0.0/16 \
     --upload-certs | tee ~/kubeadm-init.log
   mkdir -p $HOME/.kube && sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
   sudo chown $(id -u):$(id -g) $HOME/.kube/config
   kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
   kubectl get nodes
   grep -n 'certificate-key' ~/kubeadm-init.log
   ```

2. Try the post's instruction, both ways it is offered. Neither should work, and the two failures
   are not identical.

   ```sh
   sudo kubeadm init --feature-gates=EtcdLearnerMode=true --dry-run 2>&1 | tail -5
   cat > /tmp/learner-config.yaml <<'EOF'
   apiVersion: kubeadm.k8s.io/v1beta4
   kind: ClusterConfiguration
   featureGates:
     EtcdLearnerMode: true
   EOF
   sudo kubeadm init --config=/tmp/learner-config.yaml --dry-run 2>&1 | tail -5
   kubeadm init --help | grep -A4 -- '--feature-gates'
   ```

3. Read the single member, and name the column the post prints without naming.

   ```sh
   E=$(kubectl -n kube-system get pod -l component=etcd -o name | head -1)
   kubectl -n kube-system exec "$E" -- etcdctl \
     --endpoints 127.0.0.1:2379 \
     --cert=/etc/kubernetes/pki/etcd/server.crt \
     --key=/etc/kubernetes/pki/etcd/server.key \
     --cacert=/etc/kubernetes/pki/etcd/ca.crt \
     member list
   kubectl -n kube-system exec "$E" -- etcdctl \
     --endpoints 127.0.0.1:2379 \
     --cert=/etc/kubernetes/pki/etcd/server.crt \
     --key=/etc/kubernetes/pki/etcd/server.key \
     --cacert=/etc/kubernetes/pki/etcd/ca.crt \
     member list -w table
   ```

4. Set two recorders going on the first node, then join the second control plane from the other
   terminal. The join takes long enough that a one-second sample catches the transition.

   ```sh
   cat > /tmp/watch-members.sh <<'EOF'
   #!/bin/sh
   E=$(kubectl -n kube-system get pod -l component=etcd -o name | head -1)
   while true; do
     printf '%s ' "$(date +%H:%M:%S)"
     kubectl -n kube-system exec "$E" -- etcdctl --endpoints 127.0.0.1:2379 \
       --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key \
       --cacert=/etc/kubernetes/pki/etcd/ca.crt member list 2>&1 | tr '\n' '|'
     echo
     sleep 1
   done
   EOF
   chmod +x /tmp/watch-members.sh
   /tmp/watch-members.sh > /tmp/members.log 2>&1 &
   while true; do
     printf '%s %s\n' "$(date +%H:%M:%S)" \
       "$(kubectl create cm probe-$(date +%s) --from-literal=k=v >/dev/null 2>&1 && echo ok || echo FAIL)"
     sleep 1
   done > /tmp/writes.log 2>&1 &
   # then, on 10.10.10.151, run the join line from ~/kubeadm-init.log with --control-plane
   ```

5. Stop the recorders and read what they caught.

   ```sh
   kill %1 %2
   grep -c 'FAIL' /tmp/writes.log || true
   awk '{print $1, gsub(/true/,"true"), gsub(/false/,"false")}' /tmp/members.log | uniq -f1 | head -20
   grep -n 'true' /tmp/members.log | head -3
   grep -n 'true' /tmp/members.log | tail -1
   ```

6. Ask etcd itself. The member it added logs the promotion, and so does the leader.

   ```sh
   for p in $(kubectl -n kube-system get pod -l component=etcd -o name); do
     echo "== $p"
     kubectl -n kube-system logs "$p" | grep -i -E 'learner|promote|added member|member promoted' | head -10
   done
   ```

7. Join the third node and put the cluster back to an odd number of members, which is what the
   post's note at `:91-93` asks for.

   ```sh
   # on 10.10.10.152, the same join line, then back on 10.10.10.150:
   kubectl get nodes -o wide
   E=$(kubectl -n kube-system get pod -l component=etcd -o name | head -1)
   kubectl -n kube-system exec "$E" -- etcdctl --endpoints 127.0.0.1:2379 \
     --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key \
     --cacert=/etc/kubernetes/pki/etcd/ca.crt member list -w table
   kubectl -n kube-system exec "$E" -- etcdctl --endpoints 10.10.10.150:2379,10.10.10.151:2379,10.10.10.152:2379 \
     --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key \
     --cacert=/etc/kubernetes/pki/etcd/ca.crt endpoint status -w table
   ```

8. Settle the phase-name disagreement by asking the binary rather than the page.

   ```sh
   kubeadm join phase --help | sed -n '/Available Commands/,/Flags/p'
   kubeadm join phase etcd-join --help | head -12
   kubeadm join phase control-plane-join-etcd all --help 2>&1 | head -3
   ```

9. Now go looking for the gate in the place gates live, and fail to find it in four different ways.

   ```sh
   kubectl get --raw /metrics | grep -i 'etcdlearner' || echo "not a core gate: no metric"
   kubeadm init --help | grep -i 'etcdlearner' || echo "not in the flag help either"
   sudo grep -ri 'EtcdLearnerMode' /etc/kubernetes/ || echo "nothing on disk names it"
   kubectl -n kube-system get cm kubeadm-config -o jsonpath='{.data.ClusterConfiguration}'
   ```

10. Offline, in a checkout of `kubernetes/website` at the pin, count the word the whole post is
    about.

    ```sh
    cd /path/to/kubernetes/website/content/en
    grep -rn 'learner' docs --include='*.md'
    grep -rln 'EtcdLearnerMode' docs/reference/command-line-tools-reference/feature-gates/ | wc -l
    sed -n '164,177p;186,188p' docs/reference/setup-tools/kubeadm/kubeadm-init.md
    sed -n '13,27p' docs/reference/setup-tools/kubeadm/generated/kubeadm_join/kubeadm_join_phase_etcd-join.md
    grep -c 'learner' docs/setup/production-environment/tools/kubeadm/high-availability.md || true
    ```

**Expect**

Step 1 takes several minutes and the `--upload-certs` line is the one to keep: it prints a
`--certificate-key` value that expires in two hours, and without it the control-plane joins in steps
4 and 7 cannot download the shared certificates. The node reaches `Ready` only after Flannel is
applied. If `kubeadm init` refuses because swap is on, the baseline was skipped on this guest.

Step 2 fails twice, and the difference between the two failures is the finding. The flag form should
be rejected with an unrecognised-feature-gate error naming the one gate kubeadm still knows,
`RootlessControlPlane`; the config form should be rejected during validation of
`ClusterConfiguration.featureGates`. Neither message says *removed*, and neither points at the table
that would explain it. A reader following the post gets no signal distinguishing a typo from a
correctly-typed dead gate — which is the failure mode the post's own audience is most likely to hit.

Step 3 prints one member, `started`, with the node's peer and client URLs, and a final field of
`false`. That field is the post's subject. The `-w table` form names it: the last column header
reads `IS LEARNER`. Compare the plain form against the post's sample output line and note that they
have the same shape, six fields, with the same `false` in the same position — the post shows you the
learner column while telling you it is checking cluster health.

Step 4 produces two log files and no output worth reading live. The join on the second node prints a
phase list; `etcd-join` is the phase that matters, and it is the one that takes the longest. Do not
skip the write loop: the post's first advantage claim is specifically that a new member does not
disrupt the quorum, and a claim about availability is only tested by trying to write during the
window.

Step 5 is the measurement. `/tmp/writes.log` should contain zero `FAIL` lines across the entire
join, including the seconds when the cluster had two members and therefore a quorum of two — the
moment at which a non-learner addition is most dangerous. `/tmp/members.log` should show three
states in order: one member; two members with the new one carrying `true` in the final field; two
members both carrying `false`. The interval between the second and third states is the catch-up the
post describes, and on an idle lab cluster it is short — a handful of seconds. If you never see a
`true`, your sample rate lost it; drop the `sleep 1` to `sleep 0.2` and repeat with the third node
in step 7.

Step 6 is etcd's own account of the same event. Expect lines from the leader recording a member
added with `isLearner:true`, followed by a promotion; the exact wording varies with the etcd version
bundled in the release, which is why the grep is broad. This is the only place in the whole exercise
where the word *learner* comes from the software rather than from the post.

Step 7 returns the cluster to three members, all `false`, and `endpoint status` should show one
leader and two followers with matching `RAFT INDEX` values, or values a revision or two apart. Note
what the post's odd-number note is really about: with two members the cluster tolerates zero
failures, which is worse than one member, and the window in step 5 is exactly that state. Learner
mode does not shorten that window; it only keeps the joining member from voting inside it.

Step 8 settles the disagreement in kubeadm's favour. `kubeadm join phase --help` lists `etcd-join`
as an available command, `kubeadm join phase etcd-join --help` prints the same synopsis as the
generated page, and `control-plane-join-etcd` is not a command at all — the third invocation should
fail with an unknown-command error. The page's *Examples* block is documenting a name the binary no
longer answers to, three lines below the name it does.

Step 9 is four dead ends, which is the point. The core metrics endpoint has no
`kubernetes_feature_enabled` series for this name, because it was never a core gate; `kubeadm init
--help` does not mention it; nothing under `/etc/kubernetes/` names it; and the cluster's own
`kubeadm-config` ConfigMap has no `featureGates` key at all. The behaviour you measured in steps 5
and 6 is running, and there is no switch anywhere in the system that records the decision to run it.

Step 10 is the count. `grep -rn 'learner' docs` should print exactly one line, at
`kubeadm-init.md:188`, in the description of a removed gate. The feature-gates directory yields zero
files. The two `sed` ranges print the removed-gates table and that description together, so the
single surviving sentence can be read in the context that files it. The final `grep -c` on the
448-line HA guide prints `0`.

**Read on**

1. `high-availability.md:251-271`, the join step this exercise ran, including the note about CoreDNS
   pods all landing on the first control-plane node. Run the rebalance it recommends and see whether
   your three-node cluster needed it.

2. `ha-topology.md`, on stacked versus external etcd. This exercise built the stacked form, which is
   the one kubeadm defaults to and the one where a control-plane join is also an etcd member
   addition.

3. `kubeadm-init.md:133-146`, the whole feature-gates section — three paragraphs that define a
   registry, a removal policy, and a refusal to accept core gates, in less space than a single core
   gate file uses for its stage table.

4. [The drill that stops two of three members](../../labs/02/27-lose-quorum.md), for what the second
   state in step 5 would cost you if the joining member had voted. Read it against your own
   `/tmp/members.log` timestamps.

5. *Unanswerable from the pin.* Whether etcd ever implemented auto-promotion of learner members, the
   open issue the post links at `:101-102`. Nothing under `content/en` refers to it, and the
   `kubernetes/website` pin cannot report on an `etcd-io/etcd` decision. The behaviour you measured
   is kubeadm promoting the member, not etcd promoting itself.

**Teardown**

```sh
kubectl delete cm -l '!kubernetes.io/bootstrapping' --field-selector 'metadata.name!=kube-root-ca.crt' 2>/dev/null
rm -f /tmp/watch-members.sh /tmp/members.log /tmp/writes.log /tmp/learner-config.yaml
```

The ConfigMaps the write loop created are named `probe-<epoch>` in `default`; delete them by name if
the selector above is too broad for your taste. Then, because this topology is the most expensive in
the curriculum at 7.5GB, give the three guests back:

```sh
just tofu labs destroy
```

Back to the [2023 census](README.md).
