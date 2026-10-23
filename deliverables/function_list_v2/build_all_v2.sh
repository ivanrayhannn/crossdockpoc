#!/usr/bin/env bash
# Build the UISS of the new function list (XD01-XD15) into deliverables/function_list_v2/uiss.
# The first-version specs in deliverables/uiss_specs are only read. Run from the repository root.
set -euo pipefail
V=deliverables/function_list_v2
( cd $V/specs && python3 build_simple.py && python3 build_xd01.py && python3 build_xd05.py && python3 build_if.py \
  && python3 build_h.py && python3 build_xd11.py && python3 build_xd10.py && python3 apply_1910.py && python3 apply_2010.py && python3 apply_2110.py && python3 apply_2310.py ) > /dev/null
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
