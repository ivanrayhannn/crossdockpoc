from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

OUT = Path(__file__).resolve().parent
REG = Path('C:/Windows/Fonts/arial.ttf')
BOLD = Path('C:/Windows/Fonts/arialbd.ttf')

def ft(size, bold=False):
    try:
        return ImageFont.truetype(str(BOLD if bold else REG), size)
    except OSError:
        return ImageFont.load_default()

def wrap(draw, text, f, maxw):
    result, line = [], ''
    for word in text.split():
        test = (line + ' ' + word).strip()
        if line and draw.textbbox((0, 0), test, font=f)[2] > maxw:
            result.append(line)
            line = word
        else:
            line = test
    if line:
        result.append(line)
    return result

def box(draw, coords, text, fill='#FFFFFF', stroke='#26384A', size=22, bold=False):
    x1, y1, x2, y2 = coords
    draw.rounded_rectangle(coords, radius=17, fill=fill, outline=stroke, width=3)
    f = ft(size, bold)
    lines = []
    for para in text.split('\n'):
        lines.extend(wrap(draw, para, f, x2 - x1 - 28))
    heights = [draw.textbbox((0, 0), line, font=f)[3] for line in lines]
    y = y1 + ((y2 - y1) - sum(heights) - 5 * (len(lines) - 1)) / 2
    for line, h in zip(lines, heights):
        draw.text(((x1 + x2) / 2, y), line, font=f, fill='#17212B', anchor='ma')
        y += h + 5

def arrow(draw, a, b, label=None, label_pos=None):
    color, width = '#52677A', 4
    draw.line([a, b], fill=color, width=width)
    angle = math.atan2(b[1] - a[1], b[0] - a[0])
    size = 14
    p2 = (b[0] - size * math.cos(angle - math.pi / 6), b[1] - size * math.sin(angle - math.pi / 6))
    p3 = (b[0] - size * math.cos(angle + math.pi / 6), b[1] - size * math.sin(angle + math.pi / 6))
    draw.polygon([b, p2, p3], fill=color)
    if label:
        pos = label_pos or ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 16)
        draw.text(pos, label, font=ft(18, True), fill=color, anchor='mm')

def overview(title, labels, path):
    w, h, bw, gap = 1780, 460, 315, 34
    im = Image.new('RGB', (w, h), '#F7F9FB')
    d = ImageDraw.Draw(im)
    d.text((w / 2, 35), title, font=ft(30, True), fill='#17324D', anchor='ma')
    x0, y = 25, 165
    fills = ['#EAF2F8', '#FFFFFF', '#FFF7E5', '#E9F5EA', '#F1EDFA']
    for i, label in enumerate(labels):
        x = x0 + i * (bw + gap)
        box(d, (x, y, x + bw, y + 165), label, fills[i % len(fills)], size=22, bold=i in (0, 4))
        if i < len(labels) - 1:
            arrow(d, (x + bw + 3, y + 82), (x + bw + gap - 7, y + 82))
    im.save(path)

def flow(title, upload_file, source_text, temp, target, path):
    w, h = 2000, 1080
    im = Image.new('RGB', (w, h), '#FFFFFF')
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 96), fill='#F0F4F7')
    d.text((w / 2, 22), title, font=ft(29, True), fill='#17324D', anchor='ma')
    d.text((190, 69), 'Input Table / File', font=ft(21, True), fill='#26384A', anchor='mm')
    d.text((960, 69), 'Process', font=ft(21, True), fill='#26384A', anchor='mm')
    d.text((1770, 69), 'Output Table / File', font=ft(21, True), fill='#26384A', anchor='mm')
    d.line((390, 96, 390, h), fill='#A9B8C5', width=2)
    d.line((1530, 96, 1530, h), fill='#A9B8C5', width=2)
    box(d, (28, 150, 358, 278), upload_file, '#EAF2F8', size=20, bold=True)
    box(d, (28, 350, 358, 478), 'TB_R_CD_UPLOAD_LOG\nUpload ID and file path', '#F7F9FB', size=19)
    box(d, (28, 650, 358, 790), source_text, '#F7F9FB', size=19)
    box(d, (625, 116, 1295, 196), '1. Retrieve UPLOAD_ID and upload record', '#EAF2F8', size=21, bold=True)
    box(d, (625, 220, 1295, 300), '2. Check workbook, size, sheet, headers and rows', '#FFFFFF', size=20)
    # File-valid decision
    pts = [(960, 322), (1080, 382), (960, 442), (840, 382)]
    d.polygon(pts, fill='#FFF2CC')
    d.line(pts + [pts[0]], fill='#8A6D1D', width=3)
    d.text((960, 382), 'File valid?', font=ft(20, True), fill='#17212B', anchor='mm')
    box(d, (625, 474, 1295, 550), f'3. Load each row to {temp} as text', '#FFF7E5', size=20)
    box(d, (625, 574, 1295, 650), '4. Validate all rows and collect errors', '#FFFFFF', size=20)
    pts = [(960, 674), (1095, 738), (960, 802), (825, 738)]
    d.polygon(pts, fill='#FFF2CC')
    d.line(pts + [pts[0]], fill='#8A6D1D', width=3)
    d.text((960, 738), 'Any row errors?', font=ft(19, True), fill='#17212B', anchor='mm')
    box(d, (625, 828, 1295, 906), '5. Save valid changes in one transaction', '#E9F5EA', size=20, bold=True)
    box(d, (625, 930, 1295, 1010), '6. Build result report and update upload log', '#F1EDFA', size=20, bold=True)
    box(d, (1320, 340, 1510, 435), 'Reject file\nNo master write', '#FCE8E6', '#A8433B', size=17, bold=True)
    box(d, (1320, 693, 1510, 788), 'Reject upload\nNo master write', '#FCE8E6', '#A8433B', size=17, bold=True)
    arrow(d, (960, 196), (960, 220))
    arrow(d, (960, 300), (960, 322))
    arrow(d, (1080, 382), (1320, 382), 'No')
    arrow(d, (960, 442), (960, 474))
    d.text((1015, 456), 'Yes', font=ft(18, True), fill='#52677A', anchor='mm')
    arrow(d, (960, 550), (960, 574))
    arrow(d, (960, 650), (960, 674))
    arrow(d, (1095, 738), (1320, 738), 'Yes')
    arrow(d, (960, 802), (960, 828))
    d.text((1015, 815), 'No', font=ft(18, True), fill='#52677A', anchor='mm')
    arrow(d, (960, 906), (960, 930))
    # Both reject paths continue to result creation along the lane edge.
    d.line([(1510, 382), (1520, 382), (1520, 910), (1295, 970)], fill='#A8433B', width=3)
    d.polygon([(1295, 970), (1309, 965), (1304, 981)], fill='#A8433B')
    d.line([(1510, 738), (1520, 738), (1520, 910)], fill='#A8433B', width=3)
    # Read/write sources and outputs.
    arrow(d, (358, 214), (625, 156))
    arrow(d, (358, 414), (625, 156))
    arrow(d, (358, 720), (625, 612))
    box(d, (1648, 150, 1972, 282), f'{temp}\nRaw rows + validation', '#FFF7E5', size=18)
    target_size = 15 if len(target.splitlines()[0]) > 24 else 18
    box(d, (1648, 410, 1972, 542), target, '#E9F5EA', size=target_size, bold=True)
    box(d, (1648, 694, 1972, 840), 'TB_R_CD_UPLOAD_LOG\nStatus, counts, report path', '#F1EDFA', size=18)
    box(d, (1648, 930, 1972, 1040), 'Result report (.xlsx)\nSummary and row errors', '#F7F9FB', size=18)
    # Output tables are aligned to their writing steps in the output lane.
    im.save(path)

overview('Part List Upload - Operation Flow', [
    'Part List screen\nselects .xlsx file',
    'Batch reads upload ID\nand stored file',
    'Stage rows as text\nand validate',
    'Insert or update\nCandidate Part List',
    'Return report and\nstatus to screen',
], OUT / 'part_list_upload_overview.png')
flow('Part List Upload - Functional Flow', 'Part List workbook\n.xlsx; Upload sheet proposed',
     'TB_M_PART_MASTER\nMASTER_CANDIDATE_PART', 'TB_T_CD_UPLOAD_PART',
     'MASTER_CANDIDATE_PART\nAdd / Edit records', OUT / 'part_list_upload_flow.png')
overview('Mapping per Destination Upload - Operation Flow', [
    'Mapping screen\nselects .xlsx file',
    'Batch reads upload ID\nand stored file',
    'Stage, validate and\ngroup rows by part',
    'Replace mappings for\nchanged parts only',
    'Return report and\nstatus to screen',
], OUT / 'mapping_upload_overview.png')
flow('Mapping per Destination Upload - Functional Flow', 'Mapping workbook\n.xlsx; Upload sheet proposed',
     'MASTER_CANDIDATE_PART\nCurrent mapping + destination master (TBD)',
     'TB_T_CD_UPLOAD_MAPPING', 'MASTER_CANDIDATE_PART_DEST\nUpdate changed parts',
     OUT / 'mapping_upload_flow.png')
print('Created four UISS flow diagrams in', OUT)
