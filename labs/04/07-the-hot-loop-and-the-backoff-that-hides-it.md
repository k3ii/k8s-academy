<a id="the-hot-loop-and-the-backoff-that-hides-it"></a>
# The gap between retries, measured against the limiter that sets it

**Claim** — the intervals between retries of a permanently-failing key are not arbitrary: you can read the sequence off `default_rate_limiters.go`, predict the first eight gaps in milliseconds, and measure them to within a few milliseconds. You can then produce the hot loop by changing exactly one method call, and state the symptom an operator would see.

**Rests on** — [the dirty/processing measurement](06-the-same-key-a-hundred-times.md), on the same queue and the same probe program. This exercise adds the delaying and rate-limiting wrappers around it.

**Topology** — none. [`forge`](../../strands/lab-topologies.md#build-guest) only.

**Do**

1. Read the constructor the controllers actually use, and the two limiters it composes:

   ```sh
   cd ~/src/kubernetes && git grep -n 'func DefaultTypedControllerRateLimiter\|ItemExponentialFailureRateLimiter\|BucketRateLimiter' \
     -- staging/src/k8s.io/client-go/util/workqueue/default_rate_limiters.go
   ```

   Answer two things in writing before running anything: **what the base delay and the max delay are**, and **which of the two composed limiters wins for a single key failing on its own**. The second question is the one that catches people — the per-item limiter and the overall bucket limiter are combined by taking one of them, and which one is not a guess.

2. Predict the first eight gaps for one key that fails every time.

3. Measure. Change the probe from [exercise 6](06-the-same-key-a-hundred-times.md) to use a rate-limiting queue, and have the worker always fail:

   ```go
   q := workqueue.NewTypedRateLimitingQueue(workqueue.DefaultTypedControllerRateLimiter[string]())
   q.Add("a")
   last := time.Now()
   for i := 0; i < 8; i++ {
       k, _ := q.Get()
       fmt.Printf("%2d  +%v  requeues=%d\n", i, time.Since(last).Round(time.Millisecond), q.NumRequeues(k))
       last = time.Now()
       q.AddRateLimited(k)      // the failure path
       q.Done(k)
   }
   ```

4. Now build the bug. Replace `q.AddRateLimited(k)` with `q.Add(k)` — the line a tired person writes because it is shorter — and run it with a counter for two seconds.

**Observe** — the eight measured gaps against your eight predicted ones, and then the iteration count of the second version.

**Expect** — a doubling sequence starting at the base delay, capped at the maximum, matching your prediction. The measured gaps run slightly long, never short; the delaying queue's ticker is a floor, not a promise.

The second version does hundreds of thousands of iterations in two seconds. What matters is what it looks like from outside the process: **the API server sees a client hammering one object, and the controller's logs say the same true thing a hundred thousand times.** There is no error condition, nothing is down, and the object simply never becomes correct. That is the failure mode [module 4.2](../../phases/04-controllers.md#m4-2) asks you to be able to recognise, and the two symptoms to name are *CPU on the controller* and *request rate on one resource* — the second of which lands in [P3's](../../phases/03-api-machinery.md#m3-5) flow-control machinery as a priority level filling up with your own traffic.

One more thing to catch, because your own operator will need it: `NumRequeues` climbs forever unless something calls `Forget`. A key that eventually succeeds and is never forgotten carries its backoff into the next failure, so a controller that recovers still retries as slowly as it did at its worst. `Forget` on success is one line and its absence is invisible for weeks.

**Write down** — the predicted-versus-measured table, and the two-symptom description of the hot loop. [Exercise 18](18-forget-to-requeue.md) is the mirror of this one — that is the failure where retries are *too few* rather than too many, and the pair is worth keeping together in the journal.

**Footprint note** — one short-lived Go process, and one deliberate two-second CPU burn on `forge`. Do not run the second version against a real API server; it is a load generator.

**Teardown** — `rm -rf ~/probes/workqueue`. **The topology stays**, still untouched.
