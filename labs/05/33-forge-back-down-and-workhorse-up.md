<a id="forge-back-down-and-workhorse-up"></a>
# The revert: 2560MB back to 1536MB, and the third node it pays for

**Artifact** — the ceiling arithmetic written out **before** anything is provisioned, showing that [`workhorse` at 7.0GB](../../strands/lab-topologies.md#workhorse) plus `forge` at 1536MB fits and that the same sum with `forge` at 2560MB does not; then the revert, the teardown, the disk reclamation and the provision, in that order.

**Rests on** — [the resize](07-fifteen-thirty-six-will-not-link-a-scheduler.md), which is what is being undone, and [the pushed images](32-the-lease-changes-hands.md), which are the only thing that survives this exercise.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair) goes; [`workhorse`](../../strands/lab-topologies.md#workhorse) comes up. This is the phase's split point and [the strand explains why it exists](../../strands/build-mechanics.md#p5-split).

**Do**

1. **Do the arithmetic first, on paper.** Three sums, against [the ceiling](../../strands/lab-topologies.md#ceiling):

   | Configuration | Total | Margin |
   |---|---|---|
   | `workhorse` + `forge` at 2560MB | | |
   | `workhorse` + `forge` at 1536MB | | |
   | `workhorse` alone | | |

   Fill them in. The first row is the one that explains why this exercise is not optional, and the number in its margin column should be written down rather than described.

2. **Confirm the images are where you think they are.** This is the last moment when rebuilding is possible:

   ```sh
   curl -s http://forge.lab:5000/v2/_catalog
   curl -s http://forge.lab:5000/v2/academy/concentrate-scheduler/tags/list
   curl -s http://forge.lab:5000/v2/academy/toy-scheduler/tags/list
   ```

   If either is missing, go back to [exercise 28](28-the-out-of-tree-plugin.md) now. **Nothing in module 5.6 can compile a scheduler**, and discovering a missing tag after `pair` is destroyed costs a full round trip through this exercise.

3. **Reclaim disk on `forge` while it is still the machine that has it.** Two k/k-scale module graphs and a build cache have accumulated since [exercise 7](07-fifteen-thirty-six-will-not-link-a-scheduler.md); compare against the baseline you recorded there:

   ```sh
   ssh zain@10.10.10.125 'df -h /; du -sh ~/go/pkg/mod ~/.cache/go-build /var/lib/docker'
   ssh zain@10.10.10.125 'go clean -modcache && go clean -cache && docker system prune -af --volumes'
   ssh zain@10.10.10.125 'df -h /'
   ```

   Keep the registry's data: `docker system prune` does not touch a running registry's volume, but check that the catalog still answers after the prune rather than assuming it.

4. **Destroy `pair`**, [the standard way](../../strands/lab-topologies.md#teardown). Confirm it is gone before touching memory — a stopped-but-present guest still holds its allocation on the host.

5. **Revert `forge`**, the same operation as [exercise 7](07-fifteen-thirty-six-will-not-link-a-scheduler.md) with the numbers swapped:

   ```sh
   ssh hopper
   qm shutdown <forge-vmid> && sleep 20 && qm status <forge-vmid>
   qm set <forge-vmid> --memory 1536
   qm start <forge-vmid>
   ```

   Then verify from inside, because a `qm set` that silently did not apply is the failure mode this whole exercise exists to prevent:

   ```sh
   ssh zain@10.10.10.125 'free -m'
   ```

6. **Provision `workhorse`**, [the standard way](../../strands/lab-topologies.md#provision), and confirm the node count and the shape:

   ```sh
   kubectl get nodes -o custom-columns=NAME:.metadata.name,CPU:.status.allocatable.cpu,MEM:.status.allocatable.memory,TAINTS:.spec.taints
   ```

7. **Confirm the cluster can pull from the registry.** The nodes are new and nothing has told them where `forge.lab` is:

   ```sh
   kubectl run pulltest --image=forge.lab:5000/academy/toy-scheduler:v1 --restart=Never --command -- sleep 5
   kubectl describe pod pulltest | sed -n '/Events/,$p'
   ```

   If the pull fails, fix it now with [the registry conventions](../../strands/build-mechanics.md#registry) rather than in the middle of a drill.

**Observe** — the three sums, the reclaimed disk in gigabytes, `free -m` after the revert, and the three-node listing with **1 CPU per worker**, which is what makes contention on this topology real rather than arranged.

**Expect** — the first row of your table to be over the ceiling, and by enough that it is not a judgement call. Expect the disk reclamation to be substantial — a two-module-graph Go cache is measured in gigabytes, and [disk is the binding constraint on this phase rather than RAM](../../strands/build-mechanics.md#p5-split).

Expect the two workers to have **one core each** and expect that to be the whole reason module 5.6 works: a pod requesting a few hundred millicores is a meaningful fraction of a node, so scarcity is genuine and preemption has real victims rather than arranged ones.

Expect the control-plane node to be tainted and to stay that way. Three nodes with two schedulable is the topology; do not untaint it to make a drill easier, because a two-worker spread is what [5.C3](36-5c3-a-spread-nobody-can-satisfy.md) is built on.

**Write down** — the completed table, the reclaimed disk figure, and a one-line confirmation that both images pull on the new cluster.

**Footprint note — this exercise *is* the footprint work.** After it: `workhorse` 7.0GB plus `forge` 1536MB = **8.5GB against the 9.5GB ceiling, 1.0GB of margin** — the tightest configuration in the phase and the reason nothing compiles from here to the end of it. If a later exercise needs a rebuild, the honest sequence is: destroy `workhorse`, resize `forge` up, build, push, resize down, re-provision. That is fifteen minutes, which is why [exercise 28](28-the-out-of-tree-plugin.md) asked you to put every argument you might want into the image the first time.

**Teardown** — `kubectl delete pod pulltest`. **The topology stays** — [the rest of the phase](34-placement-that-differs-measurably.md) runs here, and it is destroyed at [the capstone](37-the-capstone-narrative.md).
