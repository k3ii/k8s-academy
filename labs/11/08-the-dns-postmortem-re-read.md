<a id="the-dns-postmortem-re-read"></a>
# The DNS talk, re-watched for mechanism — its four-layer descent mapped to the phases that taught each layer

**Artifact** — the [DNS four-week-incident talk's](../../strands/talks.md#debugging) descent written as a **layer-to-phase table**: apparent DNS failure → conntrack overflow → martian-packet drops → kernel source → a gRPC reconnect bug, each row naming the phase that taught you to read that layer — plus a one-line statement of the transferable method it models, and a named list of the one layer, if any, this curriculum still leaves you unable to read. The talk was [planted in P1 for its *method*](../../phases/01-operate-shallow.md); you re-watch it here for its *mechanism*, because you have now read every layer it descends into.

**Rests on** — the whole trace above ([the joined trace](07-the-joined-trace-terminal-to-container.md)), and the layers the talk visits: conntrack is [P7](../../phases/07-networking.md), the kernel drop is [P0](../../phases/00-linux-primitives.md), the gRPC reconnect is a client [the apiserver work in P3 made legible](../../phases/03-api-machinery.md).

**Topology** — none for the write-up. [`pair`](../../strands/lab-topologies.md#pair) may be up and idle beside you; [the conntrack drill](09-11c3-a-rolling-update-under-conntrack-watch.md) that follows is what actually needs it.

**Read/watch** — [the debugging strand](../../strands/talks.md#debugging), the DNS talk first. Map its descent onto the phases; this is the curriculum's spine read backwards, the four-week descent compressed into a table.

> **Question to answer from the talk against your own trace:** the resolution was three lines of code, found four layers below the symptom. For each layer it descended, name the phase that taught you to read it — and name the one layer, if any, this curriculum still leaves you unable to read. An honest "none unreadable" is a claim; so is naming one. Both beat a table with no last row.

**Build** — watch the talk, then produce the table: one row per layer, each with the observable at that layer and the phase that made it readable. Then write the method in one line and answer the unreadable-layer question.

**Verify from outside** — a reader holds your table beside the talk and finds every descent step accounted for by a named phase, and your method-line matches the talk's actual shape rather than a generic slogan. The gate is that the table has a last row: the honest statement of the limit.

**Expect** — a descent that maps cleanly to P7, P0 and P3, and a method that reduces to **hypothesis → instrument → disconfirm → descend a layer**. Expect the unreadable-layer answer to be uncomfortable to write; write it anyway.

**Write down** — the layer-to-phase table, the one-line method, and the named unreadable layer (or the claim that there is none). This is [the phase's 11.5 written artifact](../../phases/11-synthesis.md#checklist).

**Footprint note** — none for the write-up; the [conntrack drill](09-11c3-a-rolling-update-under-conntrack-watch.md) carries the RAM.

**Teardown** — nothing created but the table, which you keep. **The topology stays** for [the conntrack drill](09-11c3-a-rolling-update-under-conntrack-watch.md).
