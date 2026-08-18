<a id="an-exec-that-writes-a-line-to-the-audit-log"></a>
# One `kubectl exec`, one audit-log line — the same event a Falco rule will catch at runtime

**Artifact** — an audit policy that logs `exec` and `attach` at `Metadata` level, and the single JSON line your own `kubectl exec` produces in the apiserver's audit log — with the user, the verb, the target pod and the subresource all present. This is the *control-plane* view of an exec: what the API server saw and recorded. [Exercise 24](24-a-falco-rule-that-names-the-container.md) will catch the *same act* from the kernel's view; seeing both is how you learn that audit and runtime detection answer different questions about one event.

**Rests on** — the apiserver you configured in [P3](../../phases/03-api-machinery.md); audit is another apiserver flag pointing at a policy file, wired the same way as [the encryption config](12-a-secret-that-is-no-longer-plaintext-on-disk.md) two exercises back.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — [the audit-policy reference](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/): a policy is an ordered list of rules; the first matching rule sets the level (`None`, `Metadata`, `Request`, `RequestResponse`). The question to answer: *why is `Metadata` the right level for exec* — what would `RequestResponse` capture that you specifically do not want in a log file, given what flows over an exec stream?

**Do** — write a policy that logs exec/attach at Metadata and drops everything else to None, wire the two apiserver flags, and trigger one exec:

```sh
ssh zain@10.10.10.130
sudo tee /etc/kubernetes/audit-policy.yaml >/dev/null <<'YAML'
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  verbs: ["create"]
  resources:
  - group: ""
    resources: ["pods/exec", "pods/attach"]
- level: None
YAML
# add the flags + a hostPath mount for the policy file and the log dir to the apiserver static pod:
#   --audit-policy-file=/etc/kubernetes/audit-policy.yaml
#   --audit-log-path=/var/log/kubernetes/audit.log
sudo mkdir -p /var/log/kubernetes
```

After the apiserver restarts, make one exec happen and read the line it wrote:

```sh
kubectl run target --image=busybox --restart=Never -- sleep 3600
kubectl wait --for=condition=Ready pod/target
kubectl exec target -- id
sudo tail -n 20 /var/log/kubernetes/audit.log | grep pods/exec | tail -1 | python3 -m json.tool
```

**Observe** — one JSON object whose `verb` is `create`, `objectRef.resource` is `pods`, `objectRef.subresource` is `exec`, `objectRef.name` is `target`, and `user.username` is you. That last field is why audit exists: it names *who*. Note what is absent at `Metadata` level — the command you ran (`id`) and its output are not in the line. That is the answer to the reading question: `RequestResponse` on an exec would tee the interactive stream, including anything typed or printed, into a plaintext log, which is a secret-leak liability, so exec is logged at `Metadata` — you record that an exec happened and by whom, not what crossed the wire.

**Expect** — one line, four identifying fields, no payload. If the log file is empty, the mount or the flag did not take; if every request appears, the `- level: None` catch-all is missing or mis-ordered.

**Write down** — the one audit line (fields only), and the sentence on why exec is `Metadata` and not `RequestResponse`.

**Teardown** — the audit config is a keeper; delete only the target pod; **the topology stays**:

```sh
kubectl delete pod target
```
