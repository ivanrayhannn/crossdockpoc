# Tidy hand-edited F1 / F2 (27-Oct, file _7)

Excel positions shapes by their cell anchor, so connectors are re-computed from the anchors of the shapes they connect.

- `model.py`: column / row grid of a sheet (EMU), anchor helpers.
- `router.py`: `Drawing.route(connector, start, end, kind)` – straight, L (`bentConnector2`) or Z (`bentConnector3`) route,
  `kind` p = process flow (solid black), d = data flow (dashed blue); `move`, `text`, `clone`, `remove`.
- `tidy_f1_f2_v7.py <tidy dir> <unzipped xlsx dir>`: the fixes applied to Crossdock_BPF_Level2_7.xlsx.
- `debug_poly.py`: preview copy for LibreOffice (it re-routes connectors itself): connectors become polylines drawn like Excel.
