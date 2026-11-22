"""Bring the hand-tidied XD01 workbook (uiss/, listed in MANUAL.txt) up to date with the spec, keeping its hand work.
- Text sheets (all sheets of the generated workbook except Screen Layout) replace those of the hand file at XML level
  (deliverables/uiss_specs/add_sheets_xlsx.py), so images, the sample sheets and the layout of Screen Layout stay.
- Screen Layout captions are set from the spec; images 1-30 are replaced by the prototype shots
  (uiss_screens/part_list c_01..c_14, uiss_screens/mapping c_01..c_16; 1194 x 852, same frame as before).
Run from the repository root after the generated workbook is built:
  python3 deliverables/uiss_specs/uiss_build.py deliverables/function_list_v2/specs/XD01_spec.json -o deliverables/function_list_v2/specs/generated/XD01_UISS_Screen_CrossDockPartMaster.xlsx
  python3 deliverables/function_list_v2/specs/merge_xd01_hand.py"""
import glob, html, json, os, re, shutil, subprocess, sys, tempfile, zipfile
import openpyxl

V = 'deliverables/function_list_v2'
NAME = 'XD01_UISS_Screen_CrossDockPartMaster.xlsx'
HAND, GEN = f'{V}/uiss/{NAME}', f'{V}/specs/generated/{NAME}'
SHOTS = sorted(glob.glob('deliverables/uiss_screens/part_list/c_*.png')) + sorted(glob.glob('deliverables/uiss_screens/mapping/c_*.png'))
assert len(SHOTS) == 30, len(SHOTS)
spec = json.load(open(f'{V}/specs/XD01_spec.json'))
captions = [s['caption'] for s in spec['screen_layout']]

tmp = tempfile.mkdtemp()
src, merged = f'{tmp}/src.xlsx', f'{tmp}/merged.xlsx'
g = openpyxl.load_workbook(GEN)
del g['Screen Layout']
g.save(src)
subprocess.run([sys.executable, 'deliverables/uiss_specs/add_sheets_xlsx.py', HAND, src, merged], check=True, stdout=subprocess.DEVNULL)

z = zipfile.ZipFile(merged)
files = {i.filename: z.read(i.filename) for i in z.infolist()}
order = z.infolist()
wb, rels = files['xl/workbook.xml'].decode(), files['xl/_rels/workbook.xml.rels'].decode()
rid = re.search(r'<sheet [^>]*name="Screen Layout"[^>]*r:id="([^"]+)"', wb).group(1)
rel = next(r for r in re.findall(r'<Relationship [^>]*>', rels) if f'Id="{rid}"' in r)
sheet = 'xl/' + re.search(r'Target="([^"]+)"', rel).group(1).lstrip('/').replace('xl/', '', 1)
x = files[sheet].decode()
for k, cap in enumerate(captions):
    ref = f'D{8 + 40 * k}'
    m = re.search(rf'<c r="{ref}"(?: [^>]*)?(?:/>|>.*?</c>)', x, re.S)
    st = re.search(r' s="(\d+)"', m.group(0))
    x = x[:m.start()] + f'<c r="{ref}"{" s=" + chr(34) + st.group(1) + chr(34) if st else ""} t="inlineStr"><is><t xml:space="preserve">{html.escape(cap, quote=False)}</t></is></c>' + x[m.end():]
files[sheet] = x.encode()
# the drawing of Screen Layout anchors image n at row 8 + 40 (n - 1); media imageN.png is page N
for n, shot in enumerate(SHOTS, 1):
    files[f'xl/media/image{n}.png'] = open(shot, 'rb').read()
out = f'{tmp}/out.xlsx'
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as o:
    for i in order:
        o.writestr(i, files[i.filename])
subprocess.run([sys.executable, 'deliverables/uiss_specs/clean_uiss_xlsx.py', out], check=True, stdout=subprocess.DEVNULL)
shutil.copy(out, HAND)
print('updated', HAND)
