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
python3 $S/build_caseconsol_screen_spec.py $S/CaseConsolScreen_spec.json
while read -r spec out; do
  python3 $S/uiss_build.py "$S/$spec" -o "$O/$out" > /dev/null
  echo "built $O/$out"
done <<'LIST'
PartListScreen_spec.json X1_UISS_Screen_PartList.xlsx
PartListUpload_v2_spec.json X2_UISS_Batch_PartListUpload.xlsx
MappingScreen_spec.json X3_UISS_Screen_MappingPerDestination.xlsx
MappingUpload_v3_spec.json X4_UISS_Batch_MappingUpload.xlsx
AdsSync_spec.json X5_UISS_Batch_ActualDemandSummarySync.xlsx
DadCalc_spec.json X6_UISS_Batch_DADVolumeCalculation.xlsx
MapCalc_spec.json X7_UISS_Batch_MappingDestinationCalculation.xlsx
CaseConsolScreen_spec.json X8_UISS_Screen_DeliveryPlan_ASNDraft.xlsx
LIST
