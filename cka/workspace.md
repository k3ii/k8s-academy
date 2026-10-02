<a id="workspace"></a>
# The workspace — set this up before the diagnostic, keep it for the exam

> **Do this tonight, 2 Oct.** Not because it is urgent, but because [the diagnostic](plan.md#diagnostic) scores a task **pass only if it finished inside its time box**. You will have this setup on exam day, so a diagnostic run without it measures a workstation that will never exist again. Setting it up first makes tomorrow's score *more* honest, not less.

> **This is the one thing that is safe to do the night before.** It adds no domain knowledge, so it cannot inflate any of the five domain scores the [gap rule](plan.md#diagnostic) acts on.

---

<a id="shell"></a>
## 1. The shell

The exam desktop is Linux and `bash`. Your laptop is macOS and `zsh`. Set both up — you drill on one and sit on the other, and a reflex that only works in `zsh` is not a reflex.

```sh
alias k=kubectl
export do='--dry-run=client -o yaml'      # k run x --image=nginx $do > x.yaml
export now='--force --grace-period=0'     # k delete pod x $now
```

Completion, so `k get po<TAB>` works and resource names complete:

```sh
# bash -- this is what the exam gives you
source <(kubectl completion bash)
complete -o default -F __start_kubectl k

# zsh -- your laptop
source <(kubectl completion zsh)
compdef __start_kubectl k
```

Put the four lines in `~/.bashrc` on each lab node, and in `~/.zshrc` locally. **On exam day you type them yourself**, into a fresh shell, in the first minute. Practise that: the first thing you do in every drill from now on is set up the shell, until it costs no thought.

**Never work in the wrong namespace.** Set it once per task rather than typing `-n` forty times:

```sh
k config set-context --current --namespace=<ns>
k config view --minify | grep namespace    # confirm it took
```

---

<a id="vim"></a>
## 2. `vim`, for YAML

YAML and `vim`'s defaults disagree. Without this, every pasted block comes out stair-stepped and you lose minutes to indentation rather than to Kubernetes.

In `~/.vimrc`:

```vim
set expandtab
set tabstop=2
set shiftwidth=2
set number
```

Two more worth knowing cold, because you will need them under pressure and not before:

- `:set paste` before a middle-click paste, `:set nopaste` after. Without it, auto-indent compounds on every line.
- Visual-block indent: `Ctrl-v`, select lines, `>` or `<`. This is how you fix a whole mis-indented block in two seconds.

---

<a id="speed"></a>
## 3. The three habits that buy the most time

Not knowledge — mechanics. They apply to every task in all five domains.

1. **Generate, never type.** Almost nothing should be written from a blank file:

   ```sh
   k run pod --image=nginx $do > p.yaml
   k create deploy web --image=nginx --replicas=3 $do > d.yaml
   k create role r --verb=get,list --resource=pods $do > r.yaml
   k expose deploy web --port=80 --target-port=8080 $do > s.yaml
   ```

   Then edit the file. The imperative command gets the boilerplate right, which is where typed YAML fails.

2. **`kubectl explain` instead of the browser.** It is in the terminal, it needs no tab switch, and it is always the version you are running:

   ```sh
   k explain pod.spec.containers.livenessProbe
   k explain deploy.spec.strategy --recursive | head -30
   ```

3. **Read the event, not the logs, when an object will not start.** `k describe` first, `k logs` second. The habit saves a minute per troubleshooting task, and the exam has four or five of them.

---

<a id="logistics"></a>
## 4. Logistics — do these once, tonight

Nothing here is technical and all of it voids the attempt if it is wrong on the day.

- [ ] Booking confirmed on the Linux Foundation portal for **Fri 30 Oct**.
- [ ] The system/hardware check run on the machine you will actually sit at.
- [ ] Government ID ready, and the name on it matches the name on the booking.
- [ ] The desk cleared to whatever the handbook requires.
- [ ] **Read the current exam handbook yourself** — what documentation is permitted, how many browser tabs, what the desktop provides. Do not take anyone's recollection of the rules, including mine. The rules change between exam versions and this is cheap to verify.

> **[Thu 29 Oct](plan.md#calendar) is the last date to doubt.** Reservation changes lock 24 hours out, and a no-show voids **both** attempts.

---

<a id="tonight"></a>
## 5. What not to do tonight

Dated, and expires tomorrow.

Leave alone anything that touches the five domains: kubernetes.io task pages on troubleshooting, services, scheduling, storage or RBAC, and the bodies under [`drills/`](drills/) — several of which are tomorrow's tasks seen from the other side.

The whole 56-drill menu opens tomorrow afternoon, the moment the diagnostic is scored. That is under twenty-four hours away, and what you drill then is chosen by the score rather than by appetite — which is the entire point of measuring first.
