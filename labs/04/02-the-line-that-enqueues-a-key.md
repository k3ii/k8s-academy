<a id="the-line-that-enqueues-a-key"></a>
# The line that enqueues a key, and the line that pays for it

**Claim** — in `sample-controller/controller.go` the event handler puts a `namespace/name` string on the workqueue and discards the object it was handed, and the worker then re-reads that object from the lister; you can cite both lines, and you can name the specific failure that the other design — enqueueing the object — produces.

**Rests on** — [module 4.1's](../../phases/04-controllers.md#m4-1) third reading question, which asks for exactly this line. This exercise makes the answer falsifiable and adds its consequence.

**Topology** — none. This is a reading exercise against the clone on [`forge`](../../strands/lab-topologies.md#build-guest), the same tree [P3](../../phases/03-api-machinery.md) left there.

**Setup**

```sh
ssh zain@10.10.10.125
cd ~/src/kubernetes && git log -1 --format='%H %cd' && git status --short
```

Record that sha. Every `file:line` below is only true against it, which is [the archaeology standard](../../strands/source-archaeology.md#drills) and the reason the capstone re-checks its citations.

**Do**

1. Find the enqueue:

   ```sh
   git grep -n 'MetaNamespaceKeyFunc\|workqueue.TypedRateLimitingInterface\|c.workqueue.Add' \
     -- staging/src/k8s.io/sample-controller/controller.go
   ```

2. Find the re-read. It is in `syncHandler`, and it is a lister call, not a client call:

   ```sh
   git grep -n 'Lister()\|\.Get(name)\|SplitMetaNamespaceKey' \
     -- staging/src/k8s.io/sample-controller/controller.go
   ```

3. Now find the line that makes step 2 *necessary rather than merely tidy*: the handler registered for updates receives both the old and the new object, and hands neither of them onward. Read what it does with them.

4. Write the claim out in full, in this shape, with real line numbers:

   > `controller.go:NNN` puts the key on the queue. `controller.go:NNN` reads the object back from the lister. Between those two lines the object may have changed ⟨how many⟩ times, and the worker will act on ⟨which version⟩.

**Expect** — the enqueue site converts through `cache.MetaNamespaceKeyFunc` and adds a string. The `syncHandler` splits that string and asks the lister. Nothing in between carries a pointer to an object.

The failure the other design produces has a name worth writing down: **the worker acts on a version of the object that no longer exists**. If the queue held objects, a burst of five updates would enqueue five objects and your handler would run five times, four of them on state that is already historical — and the fifth is not guaranteed to be last, because the queue is not ordered by object version. Enqueueing the key collapses those five into one unit of work whose input is read at the moment the work runs. That collapse is [exercise 6](06-the-same-key-a-hundred-times.md); the freshness is this one.

**Write down** — the two-line claim with its sha, into `journal/04-controllers.md`. It is [the checklist's](../../phases/04-controllers.md#checklist) first falsifiable claim and one of [the capstone's](../../phases/04-controllers.md#capstone) required citations, so write it once, here, in the form the capstone wants.

**Footprint note** — nothing running; `forge` is at its normal 1536MB and stays there for the whole phase.

**Teardown** — nothing to delete. **No topology yet.**
