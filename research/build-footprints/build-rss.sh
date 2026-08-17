#!/bin/bash
# Measure peak AGGREGATE RSS of a `go build`, with parallelism pinned to the
# target builder's core count. `/usr/bin/time -l` reports the max RSS of the
# largest single child, which undercounts badly for a build that forks dozens
# of `compile` processes -- what OOMs a 1536MB guest is the sum.
#
# usage: build-rss.sh <label> <dir> <build-target> [parallelism]
set -uo pipefail

LABEL="$1"; DIR="$2"; TARGET="$3"; P="${4:-2}"
OUT="$(cd "$(dirname "$0")" && pwd)/results-${LABEL}.txt"

cd "$DIR" || exit 1

sample() {
  local max=0 cur
  while :; do
    # sum RSS (KiB) of every process in the toolchain: the driver, the
    # compiler, the linker, the assembler, and `go mod download`'s children.
    cur=$(ps -Ao rss=,comm= 2>/dev/null \
      | awk '$2 ~ /(^|\/)(go|compile|link|asm|cgo|vet|gofmt|buildid)$/ {s+=$1} END{print s+0}')
    [ "$cur" -gt "$max" ] && max=$cur
    echo "$max" > /tmp/rss-peak-$$
    sleep 0.2
  done
}

sample & SAMPLER=$!
trap 'kill $SAMPLER 2>/dev/null' EXIT

START=$(date +%s)
env CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
  go build -p "$P" -o /dev/null "$TARGET" > "${OUT}.buildlog" 2>&1
RC=$?
END=$(date +%s)

kill $SAMPLER 2>/dev/null
PEAK_KB=$(cat /tmp/rss-peak-$$ 2>/dev/null || echo 0)
rm -f /tmp/rss-peak-$$

{
  echo "label:            $LABEL"
  echo "target:           $TARGET"
  echo "dir:              $DIR"
  echo "parallelism (-p): $P"
  echo "exit:             $RC"
  echo "wall seconds:     $((END - START))"
  echo "peak aggregate RSS (KiB): $PEAK_KB"
  echo "peak aggregate RSS (MiB): $((PEAK_KB / 1024))"
  echo "host: $(uname -srm), go $(go version | awk '{print $3}')"
} | tee "$OUT"
