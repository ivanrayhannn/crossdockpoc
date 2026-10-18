#!/usr/bin/env bash
# Build the UISS of the new function list (F01-F15) into deliverables/function_list_v2/uiss.
# The first-version specs in deliverables/uiss_specs are only read. Run from the repository root.
set -euo pipefail
V=deliverables/function_list_v2
( cd $V/specs && python3 build_simple.py && python3 build_f01.py && python3 build_f05.py && python3 build_if.py \
  && python3 build_h.py && python3 build_f11.py && python3 build_f10.py ) > /dev/null
python3 - <<'PY' > $V/specs/outputs.txt
import sys; sys.path.insert(0, 'deliverables/function_list_v2/specs')
from v2lib import FUNCS
for fid, (_, _, out) in FUNCS.items():
    print(fid, out)
PY
while read -r fid out; do
  python3 deliverables/uiss_specs/uiss_build.py "$V/specs/${fid}_spec.json" -o "$V/uiss/$out" > "$V/specs/${fid}_build.log"
  echo "built $V/uiss/$out"
done < $V/specs/outputs.txt
