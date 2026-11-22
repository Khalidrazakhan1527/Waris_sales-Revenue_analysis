#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
build_dir=$(mktemp -d)
trap 'rm -rf "$build_dir"' EXIT

source_url='https://raw.githubusercontent.com/mohamednsafi/superstore-sales-analysis/5425786e63ab04dda96ffec0e7db14f1420f5812/data/raw/Sample_Superstore.csv'
curl --fail --silent --show-error --location --retry 3 "$source_url" -o "$build_dir/sales.csv"
python3 analysis.py "$build_dir/sales.csv" --output "$build_dir/output" --source 'Tableau Sample Superstore (2014–2017)'
mkdir -p dist
cp "$build_dir/output/Sales_Revenue_Dashboard.html" dist/index.html
