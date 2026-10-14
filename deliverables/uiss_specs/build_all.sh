#!/usr/bin/env bash
# Rebuild every Crossdock UISS into deliverables/uiss. Run from the repository root.
set -euo pipefail
S=deliverables/uiss_specs
O=deliverables/uiss
python3 $S/build_partlist_upload_spec.py $S/PartListUpload_v2_spec.json
python3 $S/build_mapping_screen_spec.py $S/MappingScreen_spec.json
python3 $S/build_mapping_upload_spec.py $S/MappingUpload_v3_spec.json
python3 $S/build_ads_sync_spec.py $S/AdsSync_spec.json
python3 $S/build_dad_calc_spec.py $S/DadCalc_spec.json
python3 $S/build_map_calc_spec.py $S/MapCalc_spec.json
while read -r spec out; do
  python3 $S/uiss_build.py "$S/$spec" -o "$O/$out" > /dev/null
  echo "built $O/$out"
done <<'LIST'
PartListScreen_spec.json UISS_Screen_PartList.xlsx
PartListUpload_v2_spec.json UISS_Batch_PartListUpload_v2.xlsx
MappingScreen_spec.json UISS_Screen_MappingPerDestination.xlsx
MappingUpload_v3_spec.json UISS_Batch_MappingUpload.xlsx
AdsSync_spec.json UISS_Batch_ActualDemandSummarySync.xlsx
DadCalc_spec.json UISS_Batch_DADVolumeCalculation.xlsx
MapCalc_spec.json UISS_Batch_MappingDestinationCalculation.xlsx
LIST
