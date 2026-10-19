#!/usr/bin/env bash
# Build the Business Process Flow level 2: prototype data, diagram PNGs (dev server of app/ on port 5179 must run) and the Excel.
# Run: bash deliverables/function_list_v2/bpf/build_bpf.sh
set -euo pipefail
cd "$(dirname "$0")"
python3 build_bpf.py ts
mkdir -p shots
node bpf_shots.mjs http://localhost:5179/crossdockpoc/ shots
python3 build_bpf.py xlsx
