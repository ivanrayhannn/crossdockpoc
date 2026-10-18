"""F02, F03, F04, F09, F13, F15: same content as the first version, new function id / name and references."""
from v2lib import derive, load, replace_all, set_header, write

CALC_POST = [
    ('the Mapping Destination Calculation batch', 'process 2 (mapping destination) of the F05 DAD Volume Calculation batch'),
    ('the scheduled Mapping Destination Calculation', 'the scheduled F05 DAD Volume Calculation (process 2)'),
    ('Mapping Destination Calculation completed', 'Mapping calculation (F05 process 2) completed'),
    ('the DAD Volume Calculation and the Mapping Destination Calculation', 'the F05 DAD Volume Calculation (process 1 and 2)'),
    ('DAD Volume Calculation and Mapping Destination Calculation', 'F05 DAD Volume Calculation (process 1 and 2)'),
    ('Mapping Destination Calculation', 'F05 process 2 (mapping destination)'),
    ('Crossdock Master Setting', 'Cross Dock Part Master'),
]


def simple(src, fid, post=()):
    s = replace_all(derive(load(src)), list(post) + CALC_POST)
    return write(set_header(s, fid), fid)


def build():
    out = [simple('PartListUpload_v2_spec.json', 'F02'),
           simple('MappingUpload_v3_spec.json', 'F03'),
           simple('AdsSync_spec.json', 'F04')]
    # F09: the on-demand pre-mapping of [Search]; title of the list: Mapping Customer Order and PO
    out.append(simple('Instruction_spec.json', 'F09', [
        ('Get Order', 'Mapping Customer Order and PO')]))
    out.append(simple('H0125Sync_spec.json', 'F13'))
    out.append(simple('AsnInquiry_spec.json', 'F15', [
        ('(refer F08)', '(refer F11 / F12)')]))
    return out


if __name__ == '__main__':
    print('\n'.join(build()))
