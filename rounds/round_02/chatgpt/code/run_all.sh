#!/usr/bin/env bash
set -euo pipefail
TRAIN_DIR="${1:?Usage: bash code/run_all.sh /path/to/repo/data/train /path/to/output}"
OUT_DIR="${2:?Specify output directory}"
mkdir -p "$OUT_DIR"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python "$(dirname "$0")/run.py" --train-dir "$TRAIN_DIR" --out-dir "$OUT_DIR" --permutations 200
python "$(dirname "$0")/controls.py" --train-dir "$TRAIN_DIR" --out-dir "$OUT_DIR" --permutations 200
python "$(dirname "$0")/stress.py" --train-dir "$TRAIN_DIR" --out-dir "$OUT_DIR"
python "$(dirname "$0")/domain_shift.py" --train-dir "$TRAIN_DIR" --out-dir "$OUT_DIR"
python "$(dirname "$0")/postprocess.py" --train-dir "$TRAIN_DIR" --out-dir "$OUT_DIR"
HOLDOUT="$(dirname "$TRAIN_DIR")/holdout/genus_counts.tsv"
if [ -f "$HOLDOUT" ]; then python "$(dirname "$0")/predict_holdout.py" --train-dir "$TRAIN_DIR" --feature-file "$HOLDOUT" --out-dir "$OUT_DIR"; else echo 'No holdout feature table; no predictions.csv generated'; fi
