<a id="overlayfs-by-hand"></a>
# Predict which layer a write lands in

**Claim** — you can predict, before looking, whether a given write lands in `upper` as a new file, in `upper` as a copy-up of a `lower` file, or as a whiteout — and the `lower` directory is never modified in any of the three cases.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root.

**Do**

1. Build the four directories: `mkdir -p /root/ovl/{lower,upper,work,merged}`.
2. Populate `lower` with three files — `keep`, `edit`, `remove` — each with distinct content. Make `lower` read-only in your head; you will verify it stayed untouched.
3. `mount -t overlay overlay -o lowerdir=/root/ovl/lower,upperdir=/root/ovl/upper,workdir=/root/ovl/work /root/ovl/merged`.
4. **Predict first, then act.** For each of these, write down where you expect the result to appear before running it:
   - `echo new > /root/ovl/merged/created`
   - `echo more >> /root/ovl/merged/edit`
   - `rm /root/ovl/merged/remove`
   - `cat /root/ovl/merged/keep`
5. Run all four. Then list `lower` and `upper` side by side and check your predictions.
6. Look closely at what `rm` produced in `upper`: `ls -l /root/ovl/upper/remove`.
7. Add a second lower layer — `lowerdir=/root/ovl/lower2:/root/ovl/lower` — and work out from the mount which one wins when a filename exists in both.

**Observe**

```sh
ls -laR /root/ovl/lower /root/ovl/upper
ls -l /root/ovl/upper/remove          # character device, 0:0
mount | grep overlay
cat /root/ovl/lower/edit              # unchanged, one line
```

**Expect** — `created` appears only in `upper`. `edit` is **copied up whole** on first write, so `upper/edit` holds the complete modified file while `lower/edit` is byte-for-byte what you wrote in step 2. `remove` becomes a **character device with major:minor 0:0** in `upper` — a whiteout, which is how a read-only layer's file is hidden without being touched. `keep` is served from `lower` and never appears in `upper` at all. With two lower dirs, the **leftmost wins**, which is why image layers are listed newest-first.

**Write down** — the four outcomes, and the copy-up cost in one line: modifying one byte of a 1GB file in a lower layer copies 1GB into the upper layer before the write completes. That is the mechanism under "why is my container image so big" and under [the disk-fill drill](16-fill-the-upper-layer.md) you will run shortly.

**Teardown** — `umount /root/ovl/merged`. Leave the four directories in place; [`pivot_root`](14-pivot-root-vs-chroot.md) and [the capstone](20-container-from-scratch.md) both build on this tree. Guest stays up.
