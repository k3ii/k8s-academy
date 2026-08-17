#!/bin/bash
set -uo pipefail
DIR="$1"; TARGET="$2"; GOGCV="$3"; PROBE="$4"
cd "$DIR" || exit 1
max=0
( while :; do
    cur=$(ps -Ao rss=,comm= | awk '$2 ~ /(^|\/)(go|compile|link|asm)$/ {s+=$1} END{print s+0}')
    [ "$cur" -gt "$max" ] && { max=$cur; echo "$max" > /tmp/gp-$$; }
    sleep 0.2
  done ) & S=$!
trap 'kill $S 2>/dev/null' EXIT
T0=$(date +%s)
env CGO_ENABLED=0 GOOS=linux GOARCH=amd64 GOGC="$GOGCV" \
  go build -p 2 -ldflags "-X=main.probe=$PROBE" -o /dev/null "$TARGET" >/dev/null 2>&1
RC=$?; T1=$(date +%s)
kill $S 2>/dev/null
PK=$(cat /tmp/gp-$$ 2>/dev/null || echo 0); rm -f /tmp/gp-$$
printf 'GOGC=%-4s DWARF kept   exit=%d  %2ds  peak=%5d MiB\n' "$GOGCV" "$RC" "$((T1-T0))" "$((PK/1024))"
