#!/bin/bash
# Isolate the LINK step's peak RSS. The link is a single process, so build
# parallelism (-p) cannot reduce it -- if it does not fit, nothing about
# scheduling the build differently will make it fit.
set -uo pipefail
DIR="$1"; TARGET="$2"; LDF="$3"; LABEL="$4"
cd "$DIR" || exit 1
max=0
( while :; do
    cur=$(ps -Ao rss=,comm= | awk '$2 ~ /(^|\/)(go|compile|link|asm)$/ {s+=$1} END{print s+0}')
    [ "$cur" -gt "$max" ] && { max=$cur; echo "$max" > /tmp/lp-$$; }
    sleep 0.2
  done ) & S=$!
trap 'kill $S 2>/dev/null' EXIT
T0=$(date +%s)
env CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
  go build -p 2 -ldflags "$LDF" -o /dev/null "$TARGET" >/dev/null 2>&1
RC=$?; T1=$(date +%s)
kill $S 2>/dev/null
PK=$(cat /tmp/lp-$$ 2>/dev/null || echo 0); rm -f /tmp/lp-$$
printf '%-28s ldflags=%-24s exit=%d  %2ds  peak=%5d MiB\n' "$LABEL" "${LDF:-<none>}" "$RC" "$((T1-T0))" "$((PK/1024))"
