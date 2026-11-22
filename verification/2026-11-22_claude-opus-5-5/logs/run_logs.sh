#!/bin/bash
R=verification/2026-11-22_claude-opus-5-5
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$PWD/$R/tmp"
for ID in L1 L2 L3 LB1 L4 P1 P2 P3 P4 P5 P6 LA1 LA2 P7 P8 P9 F1 FB1 N1 N2 N3 N4 N5 N6; do
  s=$(date +%s)
  /opt/anaconda3/bin/python numerics/run.py -k $ID --report $R/logs/report_$ID.md > $R/logs/stdout_$ID.txt 2>&1
  echo "$ID exit=$? secs=$(( $(date +%s) - s ))" >> $R/logs/run_index.txt
done
echo DONE >> $R/logs/run_index.txt
