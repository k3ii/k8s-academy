<a id="some-things-you-didnt-know-about-kubectl_28"></a>
# Nine features, six fates, and the one command in the post that never ran at all

**Post** — [Some things you didn't know about
kubectl](https://kubernetes.io/blog/2015/10/some-things-you-didnt-know-about-kubectl_28/),
2015-10-28, Kubernetes 1.0.

**As written** — Brendan Burns lists things kubectl could do that people were not using, one per
section, and closes by calling them "nine new and exciting things". They are:

1. **Interactive run.** `kubectl run -i --tty busybox --image=busybox --restart=Never -- sh`,
   equivalent to `docker run -i -t busybox sh`, with two lines of `Waiting for pod
   default/busybox-tv9rm to be running…` before the shell. Plus an apology and a promise: "Sadly
   we mistakenly used `-t` for template in kubectl 1.0, so we need to retain backwards
   compatibility with existing CLI user. But the existing use of `-t` is deprecated and we'll
   eventually shorten `--tty` to `-t`."
2. **Logs.** `kubectl logs -f redis-izl09`, "just like tail -f".
3. **Attach.** `kubectl attach redis -i` — stderr, stdout, *and* stdin, "or even just sending
   ctrl-c to a misbehaving application", illustrated with the Redis 3.0.3 startup banner.
4. **Port forward.** `kubectl port-forward redis-izl09 6379`, which "opens port 6379 on your local
   machine and forwards communication to that port to the Pod or Service in your cluster", then
   `telnet localhost 6379` and two `INCR foo` commands.
5. **Exec.** `kubectl exec redis-izl09 -- ls /`, distinguished from `run` because it enters an
   *existing* container.
6. **Label.** `kubectl label pods redis-izl09 mylabel=awesome`.
7. **Annotate.** `kubectl annotate pods redis-izl09 icon-url=http://goo.gl/XXBTWq` — the example
   being "an icon for a GUI to use for displaying your pods".
8. **Custom output.** A two-line template file and
   `kubectl get pods redis-izl09 -o=custom-columns-file --template=cols.tmpl`.
9. **Contexts.** `kubectl config use-context`, then `kubectl config view`, then — because that
   "outputs a lot of text" — `kubectl config view -o jsonpath="{.context[*].name}"`. "Ahh, that's
   better." No output is shown.

**As it runs now** — take them in order, because the whole point of this exercise is that the fates
are all different and none of them is announced anywhere.

1. **Still works, and the promise was kept.** `kubectl run --help` at the pin lists `-t, --tty`.
   The short flag was taken away from `--template` and given to `--tty`, exactly as the post said
   it would be. But `kubectl run` itself is narrower than it was: the synopsis is
   `kubectl run NAME --image=image … -- [COMMAND]`, it creates a single Pod, and the generators
   that let it create replication controllers, deployments, jobs and services are gone. The
   `Waiting for pod …` lines are gone too.
2. **Unchanged.** `kubectl logs -f` is what it was.
3. **Unchanged, and superseded in practice.** `kubectl attach` is still there and still forwards
   stdin. What arrived beside it is `kubectl debug`, which the post could not have imagined,
   because it attaches a *new* container to a *running* pod — the thing `exec` cannot do when the
   image you need to debug with is not the image that is running.
4. **Still works; the documented shape changed.** The synopsis is now
   `kubectl port-forward TYPE/NAME [options] [LOCAL_PORT:]REMOTE_PORT`, and the examples are
   written `kubectl port-forward pod/mypod 5000 6000`. The post's bare `redis-izl09` is not in the
   documented form any more, and the post's parenthetical "the Pod or Service" has become an
   explicit `svc/` prefix.
5. **Unchanged.**
6. **Unchanged.**
7. **Unchanged.** Note what the *example* has become: `icon-url` pointing at a URL shortener, for a
   GUI to render. Annotations are now where controllers, admission policies and cloud providers
   keep configuration, and "an icon for a GUI" is the least load-bearing use anyone would think of
   today.
8. **Still available, by a different spelling.** `-o custom-columns-file` is still in the
   `kubectl get` output-format list. But the pin documents it as
   `-o custom-columns-file=<filename>` — the filename attached to the format — and the
   `--template` flag's help now reads "Template string or path to template file to use when
   `-o=go-template`, `-o=go-template-file`". The post's `-o=custom-columns-file --template=cols.tmpl`
   pairs a format with a flag that no longer claims to serve it. Step 8 finds out what that means
   in practice.
9. **This one never worked.** kubeconfig's field is `contexts`, not `context`, so
   `{.context[*].name}` selects nothing and prints nothing — which is why the post shows no
   output under it and says "Ahh, that's better." And `kubectl config use-context`, written bare
   with no context name, is not a command; it needs an argument. Two of the three commands in the
   post's last section are wrong, in a section short enough to read in one breath.

The pin publishes a working version of what section 9 was reaching for, inside its
`kubectl-whoami` plugin example:

```shell
kubectl config view --template='{{ range .contexts }}{{ if eq .name "'$(kubectl config current-context)'" }}Current user: {{ printf "%s\n" .context.user }}{{ end }}{{ end }}'
```

Note `.contexts` for the list and `.context` for the object inside each entry. The post's
expression is one letter and one nesting level away from correct, which is why nobody caught it.

**The diff, and why** — this is the post in 2015 where **most things are still right**, and it is
also the post that contains the corpus's clearest **wrong when published** case. Both readings
matter and they point at different things.

The stability is the real finding. Nine features, eleven years, and seven of them run today with
the flags the post typed. That is not luck; it is a CLI whose surface was frozen deliberately. What
changed is around the edges: a short flag reassigned as promised, a subcommand narrowed by removing
generators, a documented spelling tightened, a new sibling (`debug`) added rather than an old one
altered. If you were looking for the sweep's usual payload — a removal, a rename, a silent
behaviour change — kubectl is where you will not find it, and knowing which parts of Kubernetes
are like that is worth as much as knowing which parts are not.

Which throws the failure into relief. Section 9 was never tested. Not "worked then, broke later" —
`{.context[*].name}` could not have printed a context name on the day it was published, because
the field has always been `contexts`. The post hides it in the one way a blog post can: by
narrating the result instead of pasting it. Every other section shows terminal output, some of it
twenty lines of Redis ASCII art. Section 9 shows a command and then the words "Ahh, that's
better."

This is the third distinct shape of wrong-at-publication in the sweep so far, after the smart
quotes and [the logging post's unparseable manifest](04-cluster-level-logging-with-kubernetes.md),
and it is the most dangerous of the three, because the other two fail loudly. A YAML parse error
tells you it failed. A JSONPath expression that matches nothing exits 0 and prints an empty line,
so a reader copying the command gets silence and assumes an empty kubeconfig. The lesson is narrow
and reusable: **in this corpus, prose is reviewed and pasted output is not, and a section with no
pasted output is the section to distrust.** Post 08's invented IP address and this post's section 9
are the same failure seen from opposite sides — one pasted output that was edited into
impossibility, one command whose output was never pasted at all.

Release facts and the pressure behind each are in
[`research/blog-era-translation.md`](../../research/blog-era-translation.md).

**No gate** — none of the nine features is or ever was behind a feature gate; kubectl is a client
and gates govern servers. The instruments for every claim above are the generated command reference
at the pin — the synopsis line and the flag help for `kubectl run`, `kubectl get` and
`kubectl port-forward` — and, on your own cluster, `kubectl <command> --help` plus
`kubectl version`. Where the reference and your binary disagree, your binary is the answer, and the
version skew between them is the only thing that can make this exercise come out differently.

**Topology** — [`solo`](../../strands/lab-topologies.md#solo) — the guest from
[the namespaces exercise](08-using-kubernetes-namespaces-to-manage.md) is still up; keep it. If
you are starting here, bring it up with
[the five provision steps](../../strands/lab-topologies.md#provision), substituting
`topology=solo`, then `ssh zain@10.10.10.180`.

**Do**

1. Give yourself the post's subject, since every one of its examples is a Redis pod:

   ```sh
   kubectl run redis --image=redis:7-alpine
   kubectl wait --for=condition=Ready pod/redis --timeout=90s
   kubectl version --short 2>/dev/null || kubectl version
   ```

2. Run the post's section 1 verbatim, then test the promise it makes about `-t`:

   ```sh
   kubectl run busybox -i --tty --image=busybox --restart=Never --rm -- sh -c 'ls /; exit'
   kubectl run --help | grep -E '^\s+-[it],'
   kubectl run --help | grep -c generator
   ```

3. Sections 2, 3 and 5, in one pass — and note what each one gives you that the others do not:

   ```sh
   kubectl logs -f --tail=5 redis & sleep 3; kill %1
   timeout 5 kubectl attach redis -i ; echo "attach exit=$?"
   kubectl exec redis -- ls /
   ```

4. Section 4, both the post's spelling and the pin's:

   ```sh
   kubectl port-forward redis 6379 & sleep 2
   printf 'INCR foo\r\nINCR foo\r\n' | timeout 3 nc 127.0.0.1 6379; kill %1
   kubectl port-forward pod/redis 6380:6379 & sleep 2; kill %1
   kubectl port-forward svc/redis 6379 2>&1 | head -1
   ```

5. Sections 6 and 7, and then look at where annotations actually went:

   ```sh
   kubectl label pod redis mylabel=awesome
   kubectl annotate pod redis icon-url=http://goo.gl/XXBTWq
   kubectl get pod redis -o jsonpath='{.metadata.annotations}{"\n"}' | tr ',' '\n'
   ```

6. Section 8. Write the post's template file exactly as printed, then try its invocation and the
   pin's:

   ```sh
   printf 'RESTARTS\tNAME\n.status.containerStatuses[0].restartCount\t.metadata.name\n' > cols.tmpl
   kubectl get pod redis -o=custom-columns-file --template=cols.tmpl ; echo "post form exit=$?"
   kubectl get pod redis -o custom-columns-file=cols.tmpl ; echo "pin form exit=$?"
   kubectl get --help | grep -A1 -- '--template='
   ```

7. Section 9, the whole point of the exercise. Run all three of the post's commands and read the
   exit codes as carefully as the output:

   ```sh
   kubectl config use-context; echo "exit=$?"
   kubectl config view -o jsonpath="{.context[*].name}"; echo "exit=$?"
   kubectl config view -o jsonpath="{.contexts[*].name}"; echo "exit=$?"
   ```

8. Then find the two things kubectl grew that the post has no section for, and which cover the same
   ground better:

   ```sh
   kubectl debug --help | head -6
   kubectl debug pod/redis -it --image=busybox --target=redis -- sh -c 'ls /proc/1/root/; exit'
   kubectl events --for pod/redis | tail -5
   ```

**Expect** — step 2's shell opens and lists busybox's root, no `Waiting for pod …` lines. `--help`
shows `-i, --stdin` and `-t, --tty`: the post's promise, delivered. `grep -c generator` prints `0` —
the flag that made `kubectl run` create controllers is gone, so `--restart=Never` is no longer a
choice between object kinds but a `restartPolicy` on the only kind it makes.

Step 3: `logs -f` streams and stops when you kill it. `attach -i` connects to redis's stdout and
prints nothing new, because the banner the post pasted was already emitted before you attached —
attach is not `logs`, and this is the difference the post's Redis screenshot obscures by having
been taken at exactly the right moment. `exec` lists the container's root.

Step 4: the post's bare-name form still forwards; `nc` gets `:1` and `:2` back from `INCR foo`,
which is the post's `telnet` transcript reproduced eleven years later. The `pod/redis` form works
identically. `svc/redis` fails — you never created a service — and the error names what it looked
for, which is the point: the prefix is not decoration, it selects a resource type.

Step 5: both commands succeed and print `pod/redis labeled` / `pod/redis annotated`. The annotation
dump shows `icon-url` sitting alongside whatever your CNI, your runtime and the control plane have
written there. The post's "icon for a GUI" is the only annotation in that list that no software
reads.

Step 6 is where you find out what "still supported" is worth. The pin's form —
`-o custom-columns-file=cols.tmpl` — prints the two columns. Record what the post's form does, and
compare it against `--template`'s own help text, which now names only `go-template` and
`go-template-file`. Whatever your binary does with the post's spelling, the documented contract no
longer covers it, and a documented contract is the only thing that will still be true next release.

Step 7 is the finding. `kubectl config use-context` with no argument exits non-zero and tells you
it needs one. `{.context[*].name}` exits **0** and prints an empty line — success, no output, no
warning, nothing to indicate you asked for a field that does not exist. `{.contexts[*].name}`
prints your context name. One letter. The post published the wrong one and described the result in
prose instead of pasting it, and it has sat there since 2015.

Step 8: `kubectl debug` puts a busybox container into the running pod's namespaces and lets you
read redis's filesystem through `/proc/1/root` — a debugging story the post's `attach`/`exec`
sections cannot tell, because both require the tools to already be in the image. `kubectl events
--for` is the query the post would have written as `get events | grep`. Neither is a fix to
anything in the post; both are what "more things you didn't know about kubectl" would list now.

**Read on** — the [`text/template` package
overview](http://golang.org/pkg/text/template/#pkg-overview), which the pin's own `--template` flag
help cites as the format's definition. Read what it can express, then ask why `custom-columns`
exists at all when `go-template` subsumes it — and what that answer tells you about which of the
two the post should have taught.

**Teardown** — `kubectl delete pod redis busybox --ignore-not-found`, `rm -f cols.tmpl`, and check
`jobs` for a stray `port-forward` you did not kill. Leave the guest up; the next exercise in this
year reuses it.
