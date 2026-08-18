<a id="the-same-key-a-hundred-times"></a>
# Add one key a hundred times, count the reconciles

**Claim** — you can predict, from `queue.go` alone and before running anything, exactly how many times a worker is handed a key that was added 100 times while that worker was busy with it. Write the number down first; the queue's two sets make it a single small integer, not "it depends".

**Rests on** — [module 4.2's](../../phases/04-controllers.md#m4-2) first reading question, on the dirty and processing sets. This is that answer, made falsifiable.

**Topology** — none. This runs on [`forge`](../../strands/lab-topologies.md#build-guest) as a standalone Go program and never contacts an API server. [`pair`](../../strands/lab-topologies.md#pair) is still up from [exercise 3](03-sample-controller-against-a-real-cluster.md) and is not used here.

**Setup**

```sh
mkdir -p ~/probes/workqueue && cd ~/probes/workqueue
go mod init probe && go get k8s.io/client-go@latest
```

**Do**

1. Predict. Read `Add`, `Get` and `Done` in `staging/src/k8s.io/client-go/util/workqueue/queue.go` and fill in this table *before* writing the program:

   | Scenario | Times `Get` returns that key |
   |---|---|
   | `Add("a")` ×100, nothing consuming, then one worker starts | |
   | `Add("a")` ×100 **while** a worker holds `a` and has not called `Done` | |
   | `Add("a")` ×100 while a worker holds `a`, and the worker never calls `Done` | |
   | `Add("a")`, `Get`, `Done`, `Add("a")` | |

2. Write ~40 lines that measure it. One worker goroutine that `Get`s, prints, sleeps two seconds, then `Done`s; a main goroutine that fires 100 `Add`s during that sleep:

   ```go
   q := workqueue.NewTyped[string]()          // older trees: workqueue.New()
   go func() {
       for {
           k, shut := q.Get()
           if shut { return }
           fmt.Println("GET", k, "len", q.Len())
           time.Sleep(2 * time.Second)
           q.Done(k)
       }
   }()
   time.Sleep(500 * time.Millisecond)
   for i := 0; i < 100; i++ { q.Add("a") }
   time.Sleep(6 * time.Second)
   ```

3. Run each of the four scenarios by moving the `Done` call, or removing it.

**Observe** — the `GET` lines and the `len` beside them.

**Expect** — two `GET`s in the second scenario, not 101 and not 2 hundred-ish. The 100 adds arriving while `a` is in the processing set mark it dirty exactly once; `Done` sees it dirty and re-queues it exactly once. In the third scenario there is **one** `GET` and then silence forever — the key is stuck in processing, and a worker that forgets `Done` does not deadlock the queue, it silently retires one key from it. That is a real controller bug with no error message and no metric, and it is worth having caused once.

The mechanism is the reason the two sets exist rather than one: `dirty` is *what needs doing*, `processing` is *what is being done*, and a key in both means work arrived during work. Their intersection is what gives you de-duplication and single-worker-per-key from the same structure, which is the answer [module 4.2](../../phases/04-controllers.md#m4-2) asks for.

**Write down** — the four predictions, the four measurements, and one sentence on the third scenario's symptom as an on-call would meet it: *one object stops reconciling and everything else is fine.*

**Footprint note** — a ~10MB Go process for a few seconds. Nothing else.

**Teardown** — nothing to delete; keep `~/probes/workqueue/`, [the next exercise](07-the-hot-loop-and-the-backoff-that-hides-it.md) edits this same program. **The topology stays**, untouched.
