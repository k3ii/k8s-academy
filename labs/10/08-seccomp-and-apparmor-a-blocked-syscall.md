<a id="seccomp-and-apparmor-a-blocked-syscall"></a>
# A syscall that returns EPERM and a file write that returns Permission denied — two kernel LSMs, two different refusals

**Claim** — a pod running under `seccompProfile: RuntimeDefault` gets `EPERM` from a syscall on the default deny list (`unshare` of a new user namespace), while the *same* pod without the profile succeeds; and a pod confined by an AppArmor profile that denies writes to `/etc` cannot `touch /etc/x` while an unconfined pod can. Two hardening controls, two enforcement points in the kernel, and each refusal names itself differently — `EPERM` from seccomp's BPF filter, `Permission denied` from AppArmor's LSM hook — which is how you tell in an incident which control fired.

**Rests on** — [exercise 6](06-restricted-rejects-a-pod-you-can-name.md) required `seccompProfile` as an admission control; this one shows what that control *does* at runtime, which is the [System Hardening](../../strands/certs.md#cks) half CKS weights separately.

**Topology** — [`pair`](../../strands/lab-topologies.md#pair), continued.

**Read** — [the phase's system-hardening line](../../phases/10-security.md#m10-2): seccomp and AppArmor as kernel hardening tools. The distinction to hold before you run this: seccomp filters *syscalls* by number and arguments; AppArmor mediates *resource access* (files, capabilities, network) by path and class. They overlap but answer different questions.

**Do — seccomp, the syscall that vanishes:**

```sh
kubectl create namespace hard
# without a profile: unshare succeeds
kubectl -n hard run free --image=busybox --restart=Never --rm -it --command -- \
  sh -c 'unshare -Ur id 2>&1; echo rc=$?'
# with RuntimeDefault: the same syscall is refused
kubectl -n hard apply -f - <<'YAML'
apiVersion: v1
kind: Pod
metadata: {name: seccomped, namespace: hard}
spec:
  securityContext: {seccompProfile: {type: RuntimeDefault}}
  containers:
  - {name: c, image: busybox, command: ["sleep","3600"]}
YAML
kubectl -n hard wait --for=condition=Ready pod/seccomped
kubectl -n hard exec seccomped -- sh -c 'unshare -Ur id 2>&1; echo rc=$?'
```

**Do — AppArmor, the file that will not open.** Load a profile on the worker node (AppArmor profiles are a node artifact, applied by reference from the pod):

```sh
WK=10.10.10.131
ssh zain@$WK 'sudo tee /etc/apparmor.d/k8s-deny-etc >/dev/null' <<'PROFILE'
#include <tunables/global>
profile k8s-deny-etc flags=(attach_disconnected) {
  #include <abstractions/base>
  file,
  deny /etc/** w,
}
PROFILE
ssh zain@$WK 'sudo apparmor_parser -r /etc/apparmor.d/k8s-deny-etc && sudo aa-status | grep k8s-deny-etc'

WORKER_NODE=$(kubectl get node -l '!node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].metadata.name}')
kubectl apply -f - <<YAML
apiVersion: v1
kind: Pod
metadata: {name: confined, namespace: hard}
spec:
  nodeName: $WORKER_NODE
  securityContext:
    appArmorProfile: {type: Localhost, localhostProfile: k8s-deny-etc}
  containers: [{name: c, image: busybox, command: ["sleep","3600"]}]
YAML
kubectl -n hard wait --for=condition=Ready pod/confined
kubectl -n hard exec confined -- sh -c 'touch /etc/x 2>&1; echo rc=$?'
```

The pod is pinned to the worker with `nodeName` because that is the node the profile was loaded on — an AppArmor profile a pod references but that is not loaded on the node it lands on fails admission with `cannot enforce AppArmor: profile not loaded`, which is itself worth seeing once if you have a spare minute.

**Observe** — `unshare` prints an id line with `rc=0` in the unprofiled pod and `Operation not permitted` with a non-zero `rc` under `RuntimeDefault`; `touch /etc/x` returns `Permission denied` in the AppArmor-confined pod. The seccomp refusal is `EPERM` from a BPF filter the kernel installed at exec time; the AppArmor refusal is the LSM hook rejecting the path. **Neither is a Kubernetes decision — both are the kernel — but Kubernetes chose which filter to install.**

**Expect** — two different error strings for two different mechanisms. In an incident, `EPERM` on a syscall points at seccomp and `Permission denied` on a path points at AppArmor (or DAC), and telling which narrows where the block lives. Note the pod-spec field names differ by Kubernetes version: `appArmorProfile` is the field-level form; older clusters used the `container.apparmor.security.beta.kubernetes.io/<container>` annotation, and which one your cluster honours is worth recording rather than assuming.

**Write down** — the two refusal strings side by side, and one sentence on which question each LSM answers (syscall vs resource access).

**Teardown** — the namespace goes, and the AppArmor profile is removed from the node so it does not confine a later pod by surprise; **the topology stays**:

```sh
kubectl delete namespace hard
ssh zain@10.10.10.131 'sudo apparmor_parser -R /etc/apparmor.d/k8s-deny-etc; sudo rm -f /etc/apparmor.d/k8s-deny-etc'
```
