<a id="the-diff"></a>
# The diff: every generated file against the line you wrote by hand

**Artifact** — [the capstone's second artifact](../../phases/04-controllers.md#capstone) and the one exercise this phase cannot omit: a written mapping of **every file `kubebuilder` scaffolded** to its hand-written equivalent in artifact 1, with a verdict on each. Plus artifact 2's stage 2, because half the scaffold is deployment machinery and you cannot map what you have not run.

**Rests on** — [artifact 1 complete](19-stage-2-and-the-role-you-write-yourself.md) through its own stage 2, [artifact 2 running](31-scaffold-the-same-operator.md), and [the kill comparison](32-the-same-kill-a-different-graceful.md), which already mapped three of the runtime pieces.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Do**

1. **Ship artifact 2** — the same two-stage progression artifact 1 made, compressed into two `make` targets:

   ```sh
   cd ~/k8s-academy/build/04-operator-kubebuilder
   make docker-build docker-push IMG=forge.lab:5000/academy/operator-kubebuilder:v1
   make deploy IMG=forge.lab:5000/academy/operator-kubebuilder:v1
   kubectl -n 04-operator-kubebuilder-system get all
   ```

   Then read `Dockerfile` and `config/manager/manager.yaml` and note two deviations from the strand's conventions: the base image is `distroless`, not [`scratch`](../../strands/build-mechanics.md#base-image), and the namespace and Service Account are named for you rather than [written by you](../../strands/build-mechanics.md#identity). Decide whether each is a better default than the one you chose.

2. **Produce the file list mechanically**, so nothing is skipped because it was boring:

   ```sh
   cd ~/k8s-academy/build/04-operator-kubebuilder
   git ls-files | grep -v '^\.' | sort > /tmp/scaffold.txt ; wc -l /tmp/scaffold.txt
   ```

3. **Diff the two RBAC answers**, which is the single most informative comparison in the exercise:

   ```sh
   diff <(yq '.rules' config/rbac/role.yaml) <(yq '.rules' ~/k8s-academy/build/04-operator-clientgo/deploy/clusterrole.yaml)
   grep -rn 'kubebuilder:rbac' internal/controller/
   ```

4. **Write the table.** One row per file in `/tmp/scaffold.txt`, four columns:

   | Generated file | Hand-written equivalent | What it does that you did by hand | Verdict |

   The verdict column takes one of three values, and every row must get one:

   - **replaces** — you wrote this, it writes it better or the same;
   - **adds** — you did not do this at all;
   - **differs** — you did it deliberately differently, and you can say why.

   Files with no equivalent still get a row. `PROJECT`, `hack/boilerplate.go.txt` and `test/e2e/` are `adds`, and saying so out loud is more useful than leaving them off the list.

5. **Answer the four questions the table exists to make answerable**, in prose:
   - Which generated file replaces the most hand-written lines?
   - Which `adds` row would you have eventually needed anyway?
   - Which `adds` row is scaffolding you would delete on day one?
   - Is there a `differs` row where your hand-written version is better, and what does that say about the default?

**Expect** — roughly forty files, of which fewer than ten are the operator. That ratio is the first finding, and it is the honest answer to "what does `kubebuilder` do": mostly not the controller.

The rows that should come out clearly:

- `api/v1alpha1/zz_generated.deepcopy.go` and `config/crd/bases/…yaml` — **replaces**, exactly the output of [the generators you ran by hand](14-generate-the-clientset.md). Same tags, same tool, invoked from a `Makefile` instead of from `kube_codegen.sh`.
- `internal/controller/ensemble_controller.go` — **replaces** your `pkg/controller/{controller,sync}.go`, but only the sync half. There is no scaffolded equivalent of your queue wiring or your `WaitForCacheSync` because the manager holds them, which is a `replaces` that moved code rather than removing it.
- `cmd/main.go` — **replaces** your `cmd/operator/main.go`, and this is where the leader election you [added by hand](28-two-replicas-one-lease.md) is a `--leader-elect` flag that was always there.
- `config/rbac/role.yaml` — the interesting one. It is generated from `+kubebuilder:rbac` markers **you write**, so it is exactly as least-privilege as you make it, and the scaffold's default markers are wider than the role you [grew one 403 at a time](19-stage-2-and-the-role-you-write-yourself.md). Step 3's diff should show your hand-grown role is *tighter*. That is a `differs` where you win, and the reason is that a marker is written from intent while your role was written from evidence.
- Health probes, metrics binding, the metrics `Service`, the `ServiceMonitor` and the `NetworkPolicy` — **adds**, every one of them something you would have needed in production and did not build.

**The sentence to end on**: `kubebuilder` did not replace the loop. It replaced the wiring around the loop, the generation you were already invoking, and the operational furniture you had not got to. The loop — the enqueue, the re-read, the level-triggered write — is the part you wrote by hand in both, and it is the part that was the same in both.

**Write down** — the table, the four answers, the two `Dockerfile` deviations with your verdict on each, and the RBAC diff.

**Footprint note** — artifact 2's stage 2 puts a second small operator Deployment on the cluster; artifact 1 is still scaled to zero. To run both at once for a side-by-side, scale artifact 1 up only after scaling artifact 2 down — [not because of memory but because they fight](30-4c3-two-replicas-no-leader-election.md).

**Teardown** — nothing yet. Both trees, both images and the deployed artifact 2 are all needed for [the write-up](34-the-capstone-writeup.md), which is the last exercise. **The topology stays**, for one more exercise.
