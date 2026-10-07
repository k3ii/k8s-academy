<a id="w08"></a>
# W8 — ConfigMap as env and as volume: change it, see which one updates

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Workloads and Scheduling / ConfigMaps and Secrets

> **A mounted ConfigMap updates in place; an environment variable never does.** Env is read once at container start and is frozen for the life of that container. This single asymmetry explains most "I changed the config and nothing happened" incidents, and it is a two-minute experiment to prove.

**Do**

1. One ConfigMap, two keys. Consume it **both** ways in one pod: `envFrom` for the whole map, and a volume mount at `/etc/cfg`.
2. Confirm both before changing anything — `env | grep` and `cat /etc/cfg/<key>`.
3. **Edit the ConfigMap.** Watch the file under `/etc/cfg` change on its own, and the env var not. The file takes up to a kubelet sync period — around a minute — so wait rather than concluding too early.
4. **Then how a real rollout handles it**: there is no "reload" verb. Either the app watches the file, or you force new containers. `kubectl rollout restart deploy/web` is the one to have in your fingers.
5. **The mount-over trap.** Mount the ConfigMap at a path that already has files and watch the directory contents be *replaced*, not merged. Then do it properly with `subPath` for a single file — and discover that a `subPath` mount **does not receive updates**, which gives up the one advantage volumes had. Both halves matter.
6. `optional: true` for a key that does not exist: without it the pod stays `CreateContainerConfigError` waiting for a ConfigMap or key that is never coming. Create that state deliberately and read the message, because it looks nothing like a missing-config error.
7. Create a ConfigMap all four ways so none of them costs thinking time later: `--from-literal`, `--from-file`, `--from-file=key=path`, `--from-env-file`.

**Observe**

```sh
kubectl create cm app --from-literal=A=1 --from-file=app.conf
kubectl exec web -- env | grep ^A
kubectl exec web -- cat /etc/cfg/app.conf
kubectl edit cm app                       # then wait ~60s and re-cat
kubectl rollout restart deploy/web
kubectl describe pod web | sed -n '/Events/,$p'
```

**Done when** — you predict correctly which consumer updates and which does not, and can create a ConfigMap from a literal and a file without the help text.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Both consumers, the edit, `subPath`, the optional key. | 10 min |
| **2** | A Deployment already mounting a ConfigMap. Add a key and make it take effect. | 8 min |
| **3** | Cold, no notes. ConfigMap from a file, mounted, verified. | 5 min |

**Teardown** — delete the namespace.

**See also** — **W9** is the same shape for Secrets, with the differences that matter; **TS2** is a pod stuck on config that does not exist.
