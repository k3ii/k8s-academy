<a id="five-log-lines-five-stages"></a>
# One log line per stage, and the order they fire in

**Artifact** — a patched `sample-controller` printing exactly one line at each of the five stages in your [drawing](01-draw-it-before-you-read-it.md), plus a single annotated log excerpt covering the life of one `Foo` from creation to reconciled, with the stage names in the margin.

**Rests on** — [the running controller](03-sample-controller-against-a-real-cluster.md) and the drawing this instruments. The excerpt is what turns the drawing from a diagram you copied into a sequence you have watched.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. The controller still runs as `go run` on [`forge`](../../strands/lab-topologies.md#build-guest).

**Do**

1. Stop the controller. Add five `klog.Infof` calls, one per stage, each tagged so you can `grep` them out of the noise. Put them where the stage *acts*, not where it is constructed:

   | Tag | Where it goes |
   |---|---|
   | `STAGE/watch` | the informer's event handler for `Foo`, on add |
   | `STAGE/enqueue` | immediately after the key is added to the workqueue, printing the key |
   | `STAGE/dequeue` | in the worker, immediately after `Get`, printing the key and the queue length |
   | `STAGE/read` | immediately after the lister returns, printing the object's `resourceVersion` |
   | `STAGE/write` | immediately after each API call the reconcile makes, printing verb and target |

   Four of those five you can place from memory. The one that needs looking for is `STAGE/watch`: the handler for `Foo` and the handler for `Deployment` are different functions, and only one of them is on the path you are tracing here.

2. Rebuild, restart, and drive one object through it:

   ```sh
   go build -o ~/sample-controller . && ~/sample-controller -kubeconfig=$HOME/.kube/config -v=2 2>&1 | tee /tmp/trace.log
   kubectl delete foo example-foo; sleep 3; kubectl apply -f artifacts/examples/example-foo.yaml
   ```

3. Cut the excerpt:

   ```sh
   grep -n 'STAGE/' /tmp/trace.log | tail -40
   ```

**Observe** — the order of the tags, and the *count* of each tag for one `Foo` creation.

**Expect** — the counts do not match. One creation does not produce one of each. In particular:

- `STAGE/write` appears more than once for a single `Foo`, because creating the `Deployment` and updating the `Foo`'s status are two calls;
- `STAGE/watch` and `STAGE/enqueue` then fire *again*, triggered by the controller's own writes — the `Deployment` it just created is an object it is watching;
- `STAGE/dequeue` and `STAGE/read` follow, and the second reconcile finds nothing to do.

**A controller reacting to its own writes is normal and is the shape of every controller in the tree.** The rule it must therefore satisfy is the idempotency rule you wrote in [exercise 1](01-draw-it-before-you-read-it.md): the second pass must be a no-op, computed rather than remembered. If your instrumented run shows `STAGE/write` firing on every pass forever, the controller is writing something that differs each time — a timestamp, a re-ordered list — and that is a hot loop with a slow fuse. [Exercise 7](07-the-hot-loop-and-the-backoff-that-hides-it.md) builds the fast version of the same bug deliberately.

**Write down** — the annotated excerpt in `journal/04-controllers.md`, with the tag order down the left and, beside each, the file and line you put it on. Note the reconcile count for one create.

**Footprint note** — nothing new. One more `go build` on `forge`, which is [well inside](../../strands/build-mechanics.md#measurements) what the guest carries.

**Teardown** — keep the patched binary and the log; delete nothing. **The topology stays** — [the next exercise](05-stomp-it-back.md) needs this controller running.
