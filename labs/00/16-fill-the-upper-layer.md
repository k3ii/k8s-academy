<a id="fill-the-upper-layer"></a>
# Chaos drill 0.C4 — the writable layer fills

**Claim** — when an overlay's `upper` directory runs out of backing space, writes fail with `ENOSPC` while reads from `lower` keep working. The process sees a filesystem that is simultaneously full and full of readable files, and nothing tells it which layer is which.

**Topology** — [`bare`](../../strands/lab-topologies.md#bare), still up, still as root.

**Footprint note** — **do not fill the guest's root filesystem.** `bare` has 20G and a genuinely full `/` may not recover without a reprovision, which costs you the rest of the phase's accumulated state. Put `upper` and `work` on a small loopback filesystem instead, as step 1 does: the fill is then contained to 64MB and `losetup -d` undoes it completely.

**Do**

1. Build a 64MB backing filesystem: `truncate -s 64M /root/upper.img`, `mkfs.ext4 /root/upper.img`, `mkdir /mnt/upperfs`, `mount -o loop /root/upper.img /mnt/upperfs`, then `mkdir /mnt/upperfs/{upper,work}`.
2. Mount the overlay with `lowerdir=/root/ovl/lower` from [the overlay exercise](13-overlayfs-by-hand.md) and the new `upper`/`work`.
3. Record `df -h` for both `/mnt/upperfs` and the merged mount **before** filling. Note what the merged mount reports as its size, and where that number came from.
4. `dd if=/dev/zero of=/root/ovl/merged/fill bs=1M` until it fails. Read the error and the exit status.
5. With the layer full, try each of these and record which succeed: `cat` a `lower` file, `cat` the partially written `fill`, `echo x > /root/ovl/merged/newfile`, `rm /root/ovl/merged/fill`, and — the interesting one — `echo more >> /root/ovl/merged/edit`, which needs a copy-up.
6. Free some space and confirm each failing operation starts working again.

**Observe**

```sh
df -h /mnt/upperfs /root/ovl/merged
dd if=/dev/zero of=/root/ovl/merged/fill bs=1M ; echo "exit=$?"
ls -l /root/ovl/lower /mnt/upperfs/upper
dmesg | tail                                   # overlayfs and ext4 complaints
```

**Expect** — `dd` stops with `No space left on device` and a non-zero exit. Reads from `lower` continue to work perfectly, because `lower` is on a different filesystem that is not full. **The copy-up in step 5 fails**: appending one byte to a `lower` file requires copying the whole file into `upper` first, so an operation whose apparent cost is one byte fails on a full layer. `df` on the merged mount reports the *upper* filesystem's numbers, which is why a container's `df` describes its writable layer and not its image.

**Write down** — the asymmetry (reads fine, writes `ENOSPC`, copy-up worst of all) and the one-line link forward: this is the primitive under [P6's](../../phases/06-kubelet-node.md) disk-pressure eviction, where the kubelet's `nodefs`/`imagefs` thresholds are watching exactly this filesystem.

**Teardown** — `umount /root/ovl/merged`, `umount /mnt/upperfs`, `losetup -D`, `rm /root/upper.img`. Confirm with `losetup -a` that no loop device survives and `df -h` is back to its starting figures. Guest stays up.
