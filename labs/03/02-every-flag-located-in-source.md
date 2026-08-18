<a id="every-flag-located-in-source"></a>
# Every flag you passed, found being read

**Claim** — for each flag you gave `kube-apiserver`, there is a `file:line` in the tree where its value is *registered* and a second where it is *consumed*, and you can produce both. The flag you cannot locate is the one you do not actually control.

**Rests on** — [the hop table](01-hand-wire-the-control-plane.md), and specifically the flag you could not explain. This exercise is [module 3.0's source question](../../phases/03-api-machinery.md#m3-0) answered with a method rather than a guess.

**Topology** — **none.** [`forge`](../../strands/lab-topologies.md#build-guest), which is up regardless of any topology and which this phase now needs a `k/k` clone on.

**Setup**

Clone `k/k` [blobless](../../strands/source-archaeology.md#clone) on `forge`. This clone is load-bearing for the rest of the phase — every `file:line` in the capstone is true against *this* tree at *this* sha, and nothing else:

```sh
mkdir -p ~/src && cd ~/src
git clone --filter=blob:none https://github.com/kubernetes/kubernetes.git
cd kubernetes && git log -1 --format='%H %cd' --date=short
```

Record that sha in `journal/` now. `--depth 1` is the wrong shortcut for the same reason it was in [P2](../../phases/02-etcd.md#m2-0): [exercise 30](30-how-a-crd-gets-its-storage.md) and the capstone both need history.

**Do**

1. Take five flags: `--etcd-servers`, `--client-ca-file`, `--service-account-issuer`, `--authorization-mode`, and the one you could not explain.

2. Find where each is **registered**. Flags are declared as string literals, so grep for the literal, not for a Go identifier:

   ```sh
   cd ~/src/kubernetes
   grep -rn '"etcd-servers"' --include=*.go | grep -v _test.go
   ```

   Note which of the five are registered under `cmd/kube-apiserver/app/options/` and which are registered inside `staging/src/k8s.io/apiserver/pkg/server/options/`. **That split is the answer to a question you did not ask**: which flags belong to *an* apiserver and which belong to *the* Kubernetes apiserver.

3. Find where each is **consumed** — where the field the flag wrote is read to build something. Start at the `AddFlags` method that registered it, note the struct field it binds to, then follow that field:

   ```sh
   grep -rn 'ServerList' --include=*.go staging/src/k8s.io/apiserver/pkg/ | grep -v _test.go
   ```

   The chain to expect is *flag → an options struct field → a `Config` field → something constructed in `cmd/kube-apiserver/app/server.go`*. Name each of the four for at least two of your five flags.

4. Do the same for one flag you passed the **kubelet** and one you passed the **controller-manager**, so the method is not apiserver-specific. `--allocate-node-cidrs` is a good controller-manager choice: it is a flag whose effect you have already seen from the outside in [P1](../../phases/01-operate-shallow.md#m1-1).

**Observe** — for each of the seven, run the `grep` that produces the registration site and pipe the result through `git log -1 -L`, so you also have *when* it was last touched:

```sh
git log -1 --format='%h %cd %s' --date=short -L <line>,<line>:<path>
```

**Expect** — `--authorization-mode` is the flag with the longest distance between registration and effect, and the one where "consumed" is genuinely arguable: the value selects which authorizers are built, so the consumption site is a constructor, not a comparison. Say so rather than forcing it into the four-step chain.

`--service-account-issuer` is the trap: it is registered where you would not look for it, it is validated in a *different* place from where it is registered, and its value ends up in two consumers — the token signer and the token authenticator — which is exactly why a mismatched issuer produces a token nobody rejects at issue time and everybody rejects at use time.

**Write down** — the five-flag table with two `file:line`s each, the sha they are true at, and one sentence on the flag whose consumption site you could not pin down. A citation you have not opened does not count — [that standard is P2's and it is now assumed](../../strands/source-archaeology.md#drills).

**Teardown** — nothing created but the clone, and **the clone stays for the whole phase**. It is on `forge`, which no teardown reaches. **No topology is up.**
