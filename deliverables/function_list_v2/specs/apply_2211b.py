"""22-Nov: destination examples of XD01 as in the hand-tidied workbook of the user (Thailand / Philippines / Vietnam)."""
import json

with open('XD01_spec.json') as f:
    txt = f.read()
txt = txt.replace('(Japan, Taiwan, Korea) for the ongoing', '(Thailand, Philippines, Vietnam) for the ongoing')
txt = txt.replace('9722D10 - Japan, 9811110 - Taiwan, 9715310 - Korea', '9722D10 - Thailand, 9811110 - Philippines, 9715310 - Vietnam')
json.loads(txt)
with open('XD01_spec.json', 'w') as f:
    f.write(txt)
