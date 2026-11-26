#!/usr/bin/env bash
# Build the UISS of the new function list (XD01-XD15) into deliverables/function_list_v2/uiss.
# The first-version specs in deliverables/uiss_specs are only read. Run from the repository root.
set -euo pipefail
V=deliverables/function_list_v2
( cd $V/specs && python3 build_simple.py && python3 build_xd01.py && python3 build_xd05.py && python3 build_if.py \
  && python3 build_h.py && python3 build_xd11.py && python3 build_xd10.py && python3 apply_1910.py && python3 apply_2010.py && python3 apply_2110.py && python3 apply_2310.py && python3 apply_2710.py && python3 apply_2810.py && python3 apply_2910.py && python3 apply_3010.py && python3 apply_3010b.py && python3 apply_3010c.py && python3 apply_3010d.py && python3 apply_3110.py && python3 apply_3110b.py && python3 apply_0411.py && python3 apply_0511.py && python3 apply_0511c.py && python3 apply_0511d.py && python3 apply_0511e.py && python3 apply_0611.py && python3 apply_0611b.py && python3 apply_1111.py && python3 apply_1111b.py && python3 apply_1311.py && python3 apply_1311c.py && python3 apply_1611b.py && python3 apply_1611c.py && python3 apply_1611.py && python3 apply_1711.py && python3 apply_1711b.py && python3 apply_1711c.py && python3 apply_1711d.py && python3 apply_1711e.py && python3 apply_1811.py && python3 apply_1811b.py && python3 apply_1911.py && python3 apply_1911b.py && python3 apply_2011.py && python3 apply_2011b.py && python3 apply_2211.py && python3 apply_2211b.py && python3 apply_2211c.py && python3 apply_2211d.py && python3 apply_2311.py && python3 apply_2411.py && python3 apply_2411b.py && python3 apply_2611.py ) > /dev/null
python3 - <<'PY' > $V/specs/outputs.txt
import sys; sys.path.insert(0, 'deliverables/function_list_v2/specs')
from v2lib import FUNCS
for fid, (_, _, out) in FUNCS.items():
    print(fid, out)
PY
# workbooks listed in uiss/MANUAL.txt were tidied by hand: build them to specs/generated/ (not committed) instead
mkdir -p $V/specs/generated
while read -r fid out; do
  dest="$V/uiss/$out"
  if grep -qx "$out" $V/uiss/MANUAL.txt; then dest="$V/specs/generated/$out"; fi
  python3 deliverables/uiss_specs/uiss_build.py "$V/specs/${fid}_spec.json" -o "$dest" > "$V/specs/${fid}_build.log"
  echo "built $dest"
done < $V/specs/outputs.txt

# Markdown copy of the UISS for coding (prepare_code/)
python3 prepare_code/build_md.py > /dev/null
echo "built prepare_code (Markdown)"
python3 prepare_code/build_knowledge.py > /dev/null
echo "built prepare_code/knowledge (one file for Project knowledge)"
