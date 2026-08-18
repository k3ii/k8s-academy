<a id="a-malformed-result-at-the-cri-seam"></a>
# Break `ADD` on purpose and follow the error back across the seam P6 could only name

**Claim** — the error text your plugin writes to stdout appears in **containerd's** log first and in the kubelet's pod event second, in that order, with the kubelet never having executed your binary at all. Stating it that way round is the point: [P6](../../phases/06-kubelet-node.md) named `kubelet-cri-networking.md` as the seam it could not open, and the shape of this failure is what opens it.

**Rests on** — [exercise 11](11-two-nodes-two-pod-cidrs-no-route.md)'s working state. A break is only legible against something that worked ten minutes ago.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued. The break is confined to `.131`; the control plane keeps working, which is what lets you keep using `kubectl` while pod networking on the worker is dead.

**Read** — `kubelet-cri-networking.md`, and answer three questions before breaking anything:

| Question | Where the answer is |
|---|---|
| Which process executes the CNI binary — the kubelet or the container runtime? | the doc's division of responsibility |
| How does the pod's IP get from the plugin's result back to `pod.status.podIP`? | the CRI `PodSandboxStatus` network field |
| What is the kubelet's remaining networking responsibility, once the runtime owns CNI? | the short list at the end, and it is shorter than most people expect |

Write the three answers down now. The reason to answer them from the doc first is that the log evidence you are about to collect confirms or refutes them, and a prediction that survives is worth more than an observation you had no expectation about.

**Do — break it in the two distinct ways, and note that they are distinct.** First, a result that is well-formed JSON and not a valid CNI result:

```sh
cd ~/src/k8s-academy/build/07-cni-academy
# make ADD print `{"cniVersion":"1.0.0"}` and exit 0 — no interfaces, no ips
GOOS=linux GOARCH=amd64 go build -o /tmp/academy ./cmd/academy
scp /tmp/academy zain@10.10.10.131:/tmp/ && ssh zain@10.10.10.131 'sudo install -m0755 /tmp/academy /opt/cni/bin/academy'
kubectl -n mynet delete pod -l app=web
kubectl -n mynet get pods -o wide
kubectl -n mynet describe pod <one of them> | sed -n '/Events/,$p'
```

Then, a plugin that is not producing JSON at all — the failure a stray `fmt.Println` debugging line produces, which is why it is worth having seen:

```sh
# make ADD write "reserving address\n" to stdout before the result
```

**Observe** — collect in this order, and keep the timestamps:

```sh
ssh zain@10.10.10.131 'sudo journalctl -u containerd -o short-precise --since "-3 min" | grep -i -e cni -e network -e sandbox | tail -20'
ssh zain@10.10.10.131 'sudo journalctl -u kubelet    -o short-precise --since "-3 min" | grep -i -e "failed to setup network" -e sandbox | tail -20'
ssh zain@10.10.10.131 'sudo crictl pods | head; sudo crictl inspectp <the failing sandbox id> | jq .status.network'
```

**Expect** — pods stuck in `ContainerCreating`, an event on the pod naming the sandbox setup failure, and **your plugin's error text quoted inside containerd's log line**. Expect the kubelet's line to be a wrapper around a CRI `RunPodSandbox` error, with your text carried through it — the kubelet is repeating what it was told.

Expect the second break to be *worse than the first and to look the same from `kubectl`*. Extra bytes on stdout make the result unparseable, so the runtime reports a JSON error rather than your message, and the diagnostic path from the pod event to the actual cause gets one hop longer. **A plugin's stdout is a protocol, and logging is what stderr is for** — that is the whole lesson, and it costs one line of code to get wrong.

Expect `crictl inspectp`'s network stanza to be empty on the failing sandbox, and expect that to be the same absence you produced deliberately at [exercise 10](10-the-plugin-the-kubelet-calls.md) by omitting `ips`. One is a plugin that lied and one is a plugin that failed; from `pod.status.podIP` they are indistinguishable, which is worth a sentence.

**Do — fix it, and confirm the repair path is not blocked.** Unlike [P3's `caBundle` drill](../../phases/03-api-machinery.md#chaos), nothing here wedges the thing you need to fix it: the API server is on the other node and `kubectl` never stopped working.

```sh
# restore the correct ADD, rebuild, reinstall
kubectl -n mynet delete pod -l app=web
kubectl -n mynet get pods -o wide
```

**Write down** — the three predictions with the log evidence that confirmed or refuted each, and one sentence naming which process P6's trace would have had to instrument to see the CNI call at all. That sentence is the seam closed.

**Footprint note** — nothing. A rebuild and a `scp`.

**Teardown** — the plugin is back to working and the three pods are back. **The topology stays**; [exercise 13](13-a-second-plugin-in-the-chain.md) goes back to `forge` for one more thing artifact 1 needs.
