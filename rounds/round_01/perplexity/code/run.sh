#!/usr/bin/env bash
# One command: bash code/run.sh /path/to/asd-gut-microbiome-benchmark/data
# Outputs (in current dir): loco_results.csv, harmonisation_log.csv, depth_by_label.csv, predictions.csv (only if data/holdout exists)
set -euo pipefail
DATA=${1:-data}
python code/run_all.py --data "$DATA" --perm 200
python code/diagnostics.py --data "$DATA"
