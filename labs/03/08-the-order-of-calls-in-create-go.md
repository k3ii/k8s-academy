<a id="the-order-of-calls-in-create-go"></a>
# Where validating admission is actually called from

**Claim** — `createHandler` does not call the validating admission chain. It builds a validation function and hands it to `storage.Create`, which invokes it. Mutating admission *is* called directly, before the handler ever reaches storage — so the two halves of admission are not two calls at the same level, and a trace that draws them that way is drawing a sequence rather than a call graph.

**Rests on** — [module 3.1's entry-point question](../../phases/03-api-machinery.md#m3-1), and [the running apiserver](05-hand-start-an-apiserver.md), which you are about to rebuild with instrumentation.

**Topology** — **none.** `forge`, the apiserver from [the hand-start](05-hand-start-an-apiserver.md).

**Do**

1. Before touching anything, **predict in writing** the order in which these five things happen for one `kubectl create -f pod.yaml`, and *which function calls which*:
   - the request body is decoded into an object
   - the mutating admission chain runs
   - `strategy.Validate` runs
   - the validating admission chain runs
   - a key appears in etcd

2. Read `staging/src/k8s.io/apiserver/pkg/endpoints/handlers/create.go` — the `createHandler` function — and answer two questions from it:
   - Which named local variable holds the thing that will run validating admission, and what type is it?
   - Which argument position of the `Create` call does it occupy?

   Then read `staging/src/k8s.io/apiserver/pkg/registry/rest/create.go` — `BeforeCreate` — and `staging/src/k8s.io/apiserver/pkg/registry/generic/registry/store.go` — `Create` — and find the line that calls that argument.

3. Now instrument. Add one `klog.Infof` at each of the five points, each tagged so they sort:

   ```go
   klog.Infof("ACADEMY 1-decoded %T", obj)
   klog.Infof("ACADEMY 2-mutating-admission-returned")
   klog.Infof("ACADEMY 3-strategy-validate")
   klog.Infof("ACADEMY 4-createValidation-invoked")
   klog.Infof("ACADEMY 5-storage-write")
   ```

   Put them in the file that owns each event, not all in one file — the point of the exercise is which file each event belongs to. Rebuild and restart:

   ```sh
   cd ~/src/kubernetes && GOGC=50 go build -gcflags=all="-N -l" -o ~/kube-apiserver ./cmd/kube-apiserver
   pkill -f 'kube-apiserver --etcd-servers' ; sleep 2
   # restart with the same flag block as before
   ```

4. Drive one create through it:

   ```sh
   kubectl --context=admin run trace --image=busybox --restart=Never -- sleep 3600
   ```

**Observe**

```sh
grep ACADEMY /tmp/apiserver.log
git -C ~/src/kubernetes diff --stat          # the instrumentation, as a patch
```

**Expect** — five lines in numeric order, which is the boring half. The interesting half is the **stack**, not the sequence: swap one `klog.Infof` for a `klog.InfoS` with `debug.Stack()` at point 4 and read who called it.

```go
klog.Infof("ACADEMY 4-createValidation-invoked\n%s", debug.Stack())
```

Expect the caller of point 4 to be inside the generic store's `Create`, *below* the handler in the stack — not the handler itself. That is the claim. If your prediction had validating admission as a sibling call of `storage.Create`, this is where it is corrected, and it is a correction worth making now: [the capstone trace](45-the-capstone-trace.md) is graded on citations surviving a hostile check, and *"validating admission is called by the handler"* is a citation that will not survive.

The likely stumble is the build: five edits across three files, and one of them is in a `staging/` package, so a mistyped import fails in a directory you did not edit. `go build ./staging/src/k8s.io/apiserver/...` narrows it fast.

**Write down** — the five-point ordered list, each with the `file:function` it happens in, plus **one sentence stating which pairs are sequential calls and which is a nested callback**. This is the skeleton [the capstone](45-the-capstone-trace.md) fills in with line numbers, and it is the phase's most reused note.

**Teardown** — `kubectl --context=admin delete pod trace`. **Keep the instrumented tree** — `git stash` it if you prefer a clean checkout for reading, but [the reinvocation exercise](23-reinvocation-observed.md) and [the CRD handler exercise](30-how-a-crd-gets-its-storage.md) both add to it. **The apiserver and etcd stay up. No topology is up.**
