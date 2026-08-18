<a id="three-control-planes"></a>
# Three control planes, one comparison, written from your own notes

**Artifact** — [objective 8](../../phases/03-api-machinery.md#objectives)'s deliverable: a written comparison of the three control planes this phase put in front of you, each row answerable only from something you did rather than something you read.

**Rests on** — everything. The hand-wired cluster from [module 3.0](01-hand-wire-the-control-plane.md), the kubeadm cluster you ran modules 3.3 to 3.5 on, and [k0s](42-k0s-in-one-binary.md). Two of the three no longer exist, which is why this exercise is a write-up and why the write-downs were mandatory.

**Topology** — [`k0s-light`](../../strands/lab-topologies.md#k0s-light), for the last time — you need it running to check the k0s column rather than recall it.

**Do**

1. Fill this in. Every cell must be traceable to a note you took or a command you can still run:

   | | Very Hard Way | kubeadm | k0s |
   |---|---|---|---|
   | Processes in the control plane | | | |
   | What supervises them | | | |
   | Where etcd runs | | | |
   | Who signed the certificates | | | |
   | Number of flags you chose yourself | | | |
   | How a component is restarted | | | |
   | Smallest failure that takes it all down | | | |
   | Where the configuration lives on disk | | | |
   | Time from nothing to serving | | | |
   | What you would have to change to add a second control-plane node | | | |

2. The last row is the one you have not done. Answer it by reading, not by building — [`ha`](../../strands/lab-topologies.md#ha) is [P11](../../phases/11-synthesis.md)'s topology and this phase does not have room for it. For each of the three, name the specific thing: the flag, the command, or the config stanza.

3. Then answer the question the table is for, in a paragraph rather than a cell: **what does each of the three make easy, and what does each make invisible?** Every one of them hides something the next one down does not, and the ordering is not a straight line — k0s hides more than kubeadm in one respect and less in another. Find that respect.

4. Check one claim you are least sure of, live, on the cluster still running.

**Expect** — the flag-count row is the one that produces the argument. It is not a proxy for control; it is a proxy for *how many decisions you were required to have an opinion about*, and the Very Hard Way's number is high because you were made to have opinions about things that have one correct answer. That distinction — a decision worth making versus a decision worth defaulting — is the whole case for a distribution, and it is the case you are now in a position to argue on evidence.

The "makes invisible" answers are the ones that will matter in six months: what you cannot debug on each, because you were never shown the seam.

**Write down** — the table and the paragraph. This *is* the artifact; there is no separate write-down.

**Teardown** — nothing was created. **The topology goes:**

```sh
just tofu labs destroy
```

[The capstone](45-the-capstone-trace.md) is next and re-provisions its own cluster; see its footprint note for why that re-provision is the phase's one deliberate repeat.
