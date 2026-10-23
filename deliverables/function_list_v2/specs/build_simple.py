"""XD02, XD03, XD04, XD09, XD13, XD15: same content as the first version, new function id / name and references."""
from v2lib import derive, load, replace_all, set_header, write

CALC_POST = [
    ('the Mapping Destination Calculation batch', 'process 2 (mapping destination) of the XD05 DAD Volume Calculation batch'),
    ('the scheduled Mapping Destination Calculation', 'the scheduled XD05 DAD Volume Calculation (process 2)'),
    ('Mapping Destination Calculation completed', 'Mapping calculation (XD05 process 2) completed'),
    ('the DAD Volume Calculation and the Mapping Destination Calculation', 'the XD05 DAD Volume Calculation (process 1 and 2)'),
    ('DAD Volume Calculation and Mapping Destination Calculation', 'XD05 DAD Volume Calculation (process 1 and 2)'),
    ('Mapping Destination Calculation', 'XD05 process 2 (mapping destination)'),
    ('Crossdock Master Setting', 'Cross Dock Part Master'),
]


def simple(src, fid, post=()):
    s = replace_all(derive(load(src)), list(post) + CALC_POST)
    return write(set_header(s, fid), fid)


def build():
    out = [simple('PartListUpload_v2_spec.json', 'XD02'),
           simple('MappingUpload_v3_spec.json', 'XD03'),
           simple('AdsSync_spec.json', 'XD04')]
    # XD09: the on-demand pre-mapping of [Search]; title of the list: Mapping Customer Order and PO
    out.append(simple('Instruction_spec.json', 'XD09', [
        ('Get Order', 'Mapping Customer Order and PO')]))
    out.append(simple('H0125Sync_spec.json', 'XD13'))
    out.append(simple('AsnInquiry_spec.json', 'XD15', [
        ('(refer XD08)', '(refer XD08 / XD11)')]))
    return out


if __name__ == '__main__':
    print('\n'.join(build()))
