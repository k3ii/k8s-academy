<a id="s05"></a>
# S5 — Set and unset the default class, and watch a class-less PVC

**Reflex** · **Core** · **10 min** · [`pair`](../../../strands/lab-topologies.md#pair) · Storage / Storage classes

> **"Default StorageClass" is one annotation on one object**, `storageclass.kubernetes.io/is-default-class: "true"`. Nothing else makes a class default. Being able to set it, unset it, and recognise its absence turns a whole family of `Pending` PVCs into a ten-second fix.

> **On this cluster `local-path` is the default**, and it has not always been — it was annotated after the week-1 baseline, which is why [`baseline.md`](../../baseline.md) and the drills written against it disagree with a cluster you read today. Confirm the annotation yourself before starting; this drill both removes it and puts it back.

**Do**

1. Confirm the starting state: `kubectl get sc` prints `local-path (default)`, and that suffix comes from the annotation and nothing else. Read the annotation directly so you know what produces the suffix.
2. **Unset it** (`…is-default-class=false`, or remove it with a trailing dash) and confirm the suffix disappears.
3. Create a PVC with **no** `storageClassName`. It is `Pending` and no provisioner touches it. Read the event, or rather note how little it says — the absence of a default produces an absence of complaint, and that silence is the signature.
4. **Restore the annotation.** The PVC you already created does **not** necessarily rescue itself — check it, do not assume either way — while a *new* class-less PVC binds immediately. Whether the old one recovers is worth answering by looking rather than reasoning.
5. **Two defaults at once.** Make a second class default too. The API allows it; the behaviour is that the most recently created default wins and the rest are ignored, with a warning. Create a PVC in that state and see which class it got. This is an exam-flavoured trick and it is three commands.
6. Finally, note the field that overrides all of it: an explicit `storageClassName` on the PVC. Default class only ever answers "what if the PVC did not say".

**Observe**

```sh
kubectl get sc    # the "(default)" suffix comes from the annotation
kubectl annotate sc local-path storageclass.kubernetes.io/is-default-class=true
kubectl annotate sc local-path storageclass.kubernetes.io/is-default-class-
kubectl get pvc -w
kubectl describe pvc noclass | sed -n '/Events/,$p'
```

**Done when** — you set and unset the default from memory, and you know from measurement whether an already-`Pending` PVC recovers when a default appears.

**Passes**

| Pass | What changes | Target |
|---|---|---|
| **1** | Clean. Set, unset, two-defaults, the already-pending case. | 10 min |
| **2** | A cluster where the default is set to the wrong class. Move it. | 8 min |
| **3** | Cold, no notes. Make a class default and prove a class-less PVC binds. | 5 min |

**Teardown** — **leave `local-path` marked default.** Two things depend on it: **S2**'s "no default" case is meant to be induced rather than inherited, and fault **F12** removes the default class and `die`s if it cannot find one, so a drill that walks away with the annotation off silently disables a fault in the catalogue.

**See also** — **S2** lists the other reasons for `Pending`; **F12** in the fault catalogue removes the default class on purpose.
