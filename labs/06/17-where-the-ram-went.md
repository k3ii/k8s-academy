<a id="where-the-ram-went"></a>
# Account for every megabyte between 2048MB of RAM and what a pod may request

**Artifact** — a five-line subtraction for the worker `.131` that starts at the guest's physical memory and ends at `status.allocatable.memory`, with each subtraction named and sourced — plus the same arithmetic done a second time after you change one setting, proving the formula rather than fitting it.

**Rests on** — [the eviction threshold you configured](12-an-eviction-you-configured.md), which is one of the terms and is the one people leave out.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. **The worker's 2048MB is the subject** — this is [objective 5](../../phases/06-kubelet-node.md#objectives), done on a node small enough that every term is a visible fraction of the total.

**Read** — the node-allocatable design document (item 15) for the four-way split — capacity, `kubeReserved`, `systemReserved`, eviction threshold — and the enforcement question: which of those reservations are *enforced* by a cgroup, and which are only arithmetic?

**Do**

1. Collect the terms:

   ```sh
   ssh zain@10.10.10.131 'awk "/MemTotal/ {print}" /proc/meminfo'
   kubectl get node pair-worker -o jsonpath='{.status.capacity.memory}{"\t"}{.status.allocatable.memory}{"\n"}'
   kubectl get --raw "/api/v1/nodes/pair-worker/proxy/configz" \
     | jq '.kubeletconfig | {kubeReserved, systemReserved, evictionHard, enforceNodeAllocatable, kubeReservedCgroup, systemReservedCgroup}'
   ```

2. **Write the subtraction out before comparing.** Five lines: `MemTotal` → `capacity` → minus `kubeReserved` → minus `systemReserved` → minus the `memory.available` hard threshold → `allocatable`. Predict each intermediate value.

3. Check the first line, which is the one that surprises people:

   ```sh
   ssh zain@10.10.10.131 'free -m; cat /proc/meminfo | head -3'
   ```

   `MemTotal` is already less than 2048MB before Kubernetes has done anything. Find out what took it — the kernel image, reserved regions, the virtio balloon — and note the amount.

4. **Now prove the formula.** Change the eviction threshold on the worker and watch `allocatable` follow:

   ```sh
   ssh zain@10.10.10.131 'sudo sed -i "s/memory.available: \"700Mi\"/memory.available: \"200Mi\"/" /var/lib/kubelet/config.yaml && sudo systemctl restart kubelet'
   sleep 20; kubectl get node pair-worker -o jsonpath='{.status.allocatable.memory}{"\n"}'
   ```

   Then put it back to `700Mi` and restart again — [exercise 20](20-the-node-refuses-what-the-scheduler-allowed.md) needs the aggressive value.

5. Cross-check against the scheduler's view, which is a different number again:

   ```sh
   kubectl describe node pair-worker | sed -n '/Allocated resources/,/^Events/p'
   ```

**Expect** — the subtraction to close exactly, and the eviction threshold to move `allocatable` by precisely the amount you changed it. That is the finding: **the eviction threshold is not only a runtime behaviour, it is a permanent tax on schedulable memory**, so a conservative threshold quietly shrinks the cluster's capacity and nobody attributes the missing gigabytes to it.

Expect `Allocated resources` in `describe node` to report *requests and limits*, not usage, and to bear no relation to what the node is actually using. Three numbers — capacity, allocatable, allocated — three different questions; [P5](../../phases/05-scheduler.md#m5-3) used the third and this phase uses the first two.

Expect `enforceNodeAllocatable` to name `pods`, which tells you the reservations for the kubelet and the system are enforced by arithmetic and by nothing else unless the corresponding cgroups are configured. On this node they are not — so an over-eager system daemon can take memory the kubelet believed it had reserved, and the eviction manager finds out afterwards like everyone else.

**Write down** — the five-line subtraction with sources, the before/after `allocatable` for the threshold change, and one sentence on the difference between a reservation that is enforced and one that is asserted. [The module's write-down](../../phases/06-kubelet-node.md#m6-4) is this arithmetic.

**Footprint note** — two kubelet restarts on the worker; pods keep running across them, which you may as well confirm while you are here, because it is [drill 6.C2's](22-6c2-the-kubelet-stops-the-pods-do-not.md) claim arriving early and for free.

**Teardown** — nothing created. **Confirm the threshold is back at `700Mi`.** **The topology stays.**
