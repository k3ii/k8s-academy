<a id="three-queues-and-two-exits"></a>
# The queue state machine, written from the doc before any code is opened

**Artifact** — a state machine on one page: every queue a pod can be in, every transition between them, what causes each transition, and — the part that matters — **the two different ways a pod leaves the unschedulable set**, with the timing of each.

**Rests on** — [the located queue](18-find-the-queue-yourself.md) for where to check it afterwards. Draw it from `sig-scheduling/scheduler_queues.md` first: [the area says to read that before the source](../../strands/source-reading.md#area-3-scheduler), and at 7.2 KB it is a fraction of the code's size while carrying the whole model.

**Topology** — none.

**Do**

1. Read the doc end to end. Draw the machine. Do not open a `.go` file yet.

2. Mark on your drawing, in a different colour, the two exits from the unschedulable set. One is *event-driven* and one is *time-driven*, and conflating them is the mistake this module exists to prevent.

3. Now open the three small files [you inventoried](18-find-the-queue-yourself.md) and check the drawing against them:

   ```sh
   grep -n 'func .*flushUnschedulable\|func .*movePodsToActiveOrBackoffQueue\|func .*flushBackoffQCompleted' pkg/scheduler/backend/queue/*.go
   ```

4. Find the durations. All of them are constants or options with defaults; get the numbers, not the names:

   ```sh
   grep -rn 'DefaultPodInitialBackoffDuration\|DefaultPodMaxBackoffDuration\|podMaxInUnschedulablePodsDuration\|flushUnschedulable' pkg/scheduler/ pkg/scheduler/apis/config/ | head
   ```

5. Answer the module's question in one paragraph: **why is there a backoff queue at all, given that there is already an unschedulable set?** The two hold pods for different reasons and a pod can pass through both. Say what each is protecting against, and which one protects the *API server* rather than the scheduler.

6. Predict, in writing, three things you will check on a live cluster in [the next exercise](20-watch-a-pod-move.md):
   - how long after freeing resources an unschedulable pod is scheduled;
   - how long a pod that has failed repeatedly waits between attempts, at attempt 1, 3 and 6;
   - whether a pod that has been unschedulable for a long time is retried even if nothing in the cluster changed, and after how long.

**Expect** — three holding places and more transitions than you drew. Expect the time-driven exit to be on the order of minutes and the event-driven one to be on the order of milliseconds, and expect that gap of three or four orders of magnitude to be the single most important number in the module: **the periodic flush is a safety net for missed events, not the mechanism.** A cluster where pods routinely take minutes to schedule after resources free up is a cluster where the event path is broken and the net is catching everything.

Expect the backoff answer in step 5 to be about a pod that fails *repeatedly and quickly* — the same hot-loop shape [P4 measured on a workqueue](../../phases/04-controllers.md#m4-2), here protecting the API server and the scheduler's own throughput from one pathological pod.

**Write down** — the state machine, the durations with `file:line`, the paragraph from step 5, and the three predictions, dated, to be scored in the next two exercises.

**Footprint note** — reading only. No change to the 7.5GB.

**Teardown** — nothing created. **The topology stays.**
