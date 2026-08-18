<a id="draw-it-before-you-read-it"></a>
# Draw the pipeline before you open any of it

**Artifact** — a hand-drawn reflector → DeltaFIFO → indexer → workqueue diagram with a table naming the file that implements each stage, and **every entry you are guessing at marked with a question mark**. This drawing is deliberately made from the prose and the picture alone. [Exercise 13](13-the-same-drawing-corrected.md) draws it again after the source, and the difference between the two is the point.

**Rests on** — [module 4.1's](../../phases/04-controllers.md#m4-1) first two reading questions: the idempotency rule from `controllers.md`, and the `client-go-controller-interaction` diagram. Both are answered before anything below.

**Topology** — none. This runs wherever you take notes.

**Do**

1. Draw the five boxes and the arrows between them, left to right, starting at the API server and ending at your reconcile function. Put the *direction of data* on each arrow — several of them are not the direction you first expect.

2. Beside the drawing, fill in this table. Guess where you must, and mark the guess:

   | Stage | The `client-go` file you believe implements it | Sure? |
   |---|---|---|
   | The thing that LISTs then WATCHes | | |
   | The queue holding what changed | | |
   | The thing holding the current objects | | |
   | The queue holding keys to work on | | |
   | The thing calling your handlers | | |

3. Write two sentences underneath, in your own words:
   - the idempotency rule, as `controllers.md` states it;
   - why a reconcile that runs twice on the same object must produce the same result as running once.

**Expect** — three or four of the five rows carry a question mark. That is the correct outcome of this exercise and not a failure of it. The diagram in the `sample-controller` README names the *stages* clearly and the *files* barely at all, so the file column is mostly inference from names you have not read yet.

The one arrow most people draw backwards is between the indexer and the worker. The worker does not receive an object; it goes and asks. If your drawing has an arrow carrying an object into your handler, leave it wrong and see [exercise 2](02-the-line-that-enqueues-a-key.md).

**Write down** — the drawing and the table, in `journal/04-controllers.md`, dated. [Exercise 13](13-the-same-drawing-corrected.md) needs this exact version to diff against, so do not tidy it later.

**Footprint note** — nothing running.

**Teardown** — nothing to delete. **No topology yet** — the first one comes up at [exercise 3](03-sample-controller-against-a-real-cluster.md).
