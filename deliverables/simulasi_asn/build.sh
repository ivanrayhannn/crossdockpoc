#!/usr/bin/env bash
# Rebuild simulasi_asn_rev.xlsx (from the template of the user's simulasi_asn.xlsx), its hyperlinks, and the web data of ASN Simulation.
set -e
cd "$(dirname "$0")"
python3 sim_build.py simulasi_asn_template.xlsx ../simulasi_asn_rev.xlsx
python3 add_links.py ../simulasi_asn_rev.xlsx
python3 export_web.py ../simulasi_asn_rev.xlsx
