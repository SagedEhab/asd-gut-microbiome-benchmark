#!/usr/bin/env bash
# One command: bash code/run.sh <repo>/data <outdir>   (about 15 min on 2 CPUs)
# No holdout exists (data/holdout absent), so no predictions are written.
set -euo pipefail
DATA=${1:-data}; OUT=${2:-results}; HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"
python3 "$HERE/run_all.py" --data "$DATA" --out "$OUT"            # LOCO: headline + secondary, permutation nulls
python3 "$HERE/within.py"  --data "$DATA" --out "$OUT"            # within-cohort technical baselines; David metadata/microbiome
# ENA run tables were downloaded on 2026-11-12 with:
#   curl "https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA578223&result=read_run&fields=run_accession,instrument_model,library_layout,library_strategy,read_count,base_count,library_name,library_construction_protocol"
python3 "$HERE/zou.py" --data "$DATA" --ena "$HERE/ena" --loco "$OUT" --out "$OUT"
python3 "$HERE/summarise.py" --out "$OUT"
if [ -f "$DATA/holdout/genus_counts.tsv" ]; then echo "holdout present: predictions not implemented this round (none existed)"; fi
