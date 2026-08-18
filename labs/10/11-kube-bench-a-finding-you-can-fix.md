<a id="kube-bench-a-finding-you-can-fix"></a>
# A CIS finding, its file, its fix, and the re-run that clears it

**Artifact** — a kube-bench report against your own control plane, one `[FAIL]` line chosen from it, the exact file and flag that failing line names, the edit that satisfies it, and a second report where that same line reads `[PASS]`. The deliverable is the *loop*, not the score: find → locate → fix → re-run. A benchmark number nobody acted on is a screenshot; a number you moved is a skill.

**Rests on** — the cluster from [P1–P3](../../phases/03-api-machinery.md), whose apiserver, kubelet and etcd flags you set by hand. kube-bench audits exactly those flags, so this exercise reads back the decisions those phases made and grades them against CIS.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — [CIS benchmark structure](https://github.com/aquasecurity/kube-bench): each check has an ID (e.g. `1.2.x` for the apiserver), a remediation string naming a file and flag, and a scored/not-scored marker. The question to answer before running: *which component's checks read a static-pod manifest and which read a running process's flags* — because the fix location differs (edit the manifest file vs. edit the kubelet config), and kube-bench's remediation text tells you which.

**Do** — run the job as a pod so it sees the host's config, pick one FAIL, fix it, re-run:

```sh
kubectl create ns bench
kubectl -n bench apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl -n bench wait --for=condition=complete job/kube-bench --timeout=180s
kubectl -n bench logs job/kube-bench | tee /tmp/bench-before.txt
grep '\[FAIL\]' /tmp/bench-before.txt | head
```

Pick one FAIL with a manifest-level remediation — a strong candidate is the apiserver `--profiling` flag (CIS 1.2.x: it should be `false`). Read the remediation string, then apply it on the control-plane node:

```sh
ssh zain@10.10.10.130
sudo grep -n 'profiling' /etc/kubernetes/manifests/kube-apiserver.yaml || echo "flag absent (defaults true)"
# add the flag under the apiserver command list, then let the static pod restart
sudo sed -i '/- kube-apiserver/a\    - --profiling=false' /etc/kubernetes/manifests/kube-apiserver.yaml
```

Wait for the apiserver static pod to restart (the kubelet notices the manifest change), then re-run the job:

```sh
kubectl -n bench delete job kube-bench
kubectl -n bench apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl -n bench wait --for=condition=complete job/kube-bench --timeout=180s
kubectl -n bench logs job/kube-bench | tee /tmp/bench-after.txt
diff <(grep profiling /tmp/bench-before.txt) <(grep profiling /tmp/bench-after.txt)
```

**Observe** — the chosen line moves from `[FAIL]` to `[PASS]`, and the `diff` shows exactly that one line changing. Nothing else in the report should move — a fix that changes checks you did not touch is a fix that did something you did not intend, and that is worth chasing before you trust the report. Confirm the apiserver actually came back (`kubectl get --raw /healthz`) before declaring victory: a malformed sed edit that breaks the manifest takes the apiserver down, and the loop's whole value is that you can tell the difference between "passed" and "not answering".

**Expect** — one line flipped, apiserver healthy, and a report you moved by one check on purpose. Note that kube-bench versions track CIS versions, so the exact check ID for `--profiling` may differ from the number quoted here — the remediation string in *your* report is authoritative, not this file.

**Write down** — the check ID, its remediation string, the file and flag you edited, and the before/after status for that one line.

**Teardown** — the fix stays (it is a genuine hardening you want to keep); the benchmark namespace goes; **the topology stays**:

```sh
kubectl delete ns bench
```
