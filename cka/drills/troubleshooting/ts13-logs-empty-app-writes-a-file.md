<a id="ts13"></a>
# TS13 — `kubectl logs` is empty because the process writes to a file

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Troubleshooting / Manage container stdout and stderr logs

> **Kubernetes collects stdout and stderr, and nothing else.** An application logging to `/var/log/app.log` inside its container produces an empty `kubectl logs` while working perfectly. There is no cluster-side fix — the data never entered the pipeline. Recognising "empty logs, healthy pod" as a *logging configuration* problem rather than an application problem is the skill.

**Break it** — *pass 1 only.*

Run something that writes to a file and keeps the container alive — `sh -c 'while true; do date >> /var/log/app.log; sleep 2; done'`. `kubectl logs` is empty, the pod is `Running 1/1`, and nothing anywhere reports a problem.

**Work it**

- **First rule out the other empty-log causes**, because they are not this one and they are more urgent:
  - The container has not started yet, or is in an init container — `kubectl logs -c <init>` (**TS12**).
  - It crashed and restarted — the logs you want are `--previous`.
  - It was `SIGKILL`ed before writing anything (**TS11**).
  - Wrong container in a multi-container pod — the default is the first, silently.
- **Then confirm the file hypothesis**, which takes one command: `kubectl exec <pod> -- ls -la /var/log/` or `find / -name '*.log' -newermt '-5 minutes' 2>/dev/null`. Finding a file that is growing settles it.
- **Get the data out.** `kubectl exec -- tail -f` for live, `kubectl cp <ns>/<pod>:/var/log/app.log ./app.log` for the whole thing. Note `kubectl cp` needs `tar` in the container and fails obscurely without it — on a distroless image it will not work at all, and **N11**'s ephemeral container is the way through.
- **State the actual fixes**, in order of how correct they are:
  1. Configure the application to log to stdout. The right answer.
  2. Symlink the file to `/dev/stdout` — the common container-image trick. Do it and watch logs appear; this is worth having seen work.
  3. A sidecar tailing the file to its own stdout. The pattern to know when the application cannot be changed. Build one; it is six lines and it makes the model obvious: `kubectl logs -c sidecar` now has the data.
- **Finish with where it would have gone.** Had it used stdout, the content would be on the node under `/var/log/pods/<ns>_<pod>_<uid>/<container>/0.log` — **TS14** follows that chain. Confirm your file-logging container has an empty one there, which is the clean proof that nothing was collected.

**Observe**

```sh
kubectl logs app                       # empty
kubectl get pod app                    # Running 1/1 -- no fault anywhere
kubectl exec app -- ls -la /var/log/
kubectl exec app -- tail -5 /var/log/app.log
kubectl cp default/app:/var/log/app.log ./app.log
kubectl logs app -c log-sidecar
```

**Done when** — you rule out the four other causes, confirm the file, and build the sidecar from memory.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Confirm, extract, all three fixes. | 10 min |
| **2** | A multi-container pod where one logs correctly and one does not. | 8 min |
| **3** | Cold, no notes. Empty logs, cause named, data extracted. | 5 min |

**Teardown** — delete the namespace.

**See also** — **TS12** is the full flag surface this assumes; **TS14** is where stdout would have landed on disk; **N11** gets a shell into a container that has none.
