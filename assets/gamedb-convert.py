#
# A simple script to make comparing GameDB files easier for NetherSX2
# Just drag and drop the GameIndex.yaml file from PCSX2 on to it to process it
# Requires the ruamel.yaml library work:
# pip install ruamel.yaml from your terminal
#
import re, sys, os
from ruamel.yaml import YAML

if len(sys.argv) > 1: gamedb_file = sys.argv[1]
else: 
    print('Usage: gamedb-convert.py GameIndex.yaml')
    sys.exit()

def my_represent_none(self, data):
    # Makes null show up so we can process it
    return self.represent_scalar(u'tag:yaml.org,2002:null', u'null')

# Setting our variables
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.default_flow_style = None
yaml.preserve_quotes = True
yaml.allow_duplicate_keys = True
yaml.width = 512
yaml.representer.add_representer(type(None), my_represent_none)
ignore_list = ['bilinearUpscale', 'cpuSpriteRenderLevel', 'eeCycleRate', 'eeDivRoundMode', 'GSC_HitmanBloodMoney', 'GSC_MetalGearSolid3', 'GSC_NFSUndercover', 'GSC_PolyphonyDigitalGames', 'name-sort', 'nativePaletteDraw', 'OI_HauntingGround']
replace_dic = {'autoFlush: 2': 'autoFlush: 1', 'halfPixelOffset: 4': 'halfPixelOffset: 1', 'instantVU1:': 'InstantVU1SpeedHack:', 'minimumBlendingLevel:': 'recommendedBlendingLevel:', 'mtvu:': 'MTVUSpeedHack:', 'mvuFlag:': 'mvuFlagSpeedHack:', 'name-en:': 'name:'}

with open(gamedb_file, encoding='utf8') as oldfile, open('GameIndex[fixed].yaml', 'w', encoding='utf8') as newfile:
    prev_line = ''
    for line in oldfile:
        for key in replace_dic:
            if key in line: line = line.replace(key, replace_dic[key])
        if re.search(r'moveHandler: \".+\"', line): line = re.sub(r'moveHandler: \".+\"', 'textureInsideRT: 1', line)
        # We need the following four checks to fix ONE issue caused by a moron that inconsistently added moonrunes to the GameDB
        if line == prev_line: continue
        if not line.isascii(): continue
        if 'name:' in line and '"' not in line: continue
        if 'name:' in line and re.search(r'[A-Z]+: ', line): continue
        if not any(ignore_word in line for ignore_word in ignore_list): newfile.write(line)
        prev_line = line

# Uses the Magic if YAML Processing to clean out empty keys
with open('GameIndex[fixed].yaml', encoding='utf8') as oldfile, open('GameIndex[fixed2].yaml', 'w', encoding='utf8') as newfile:
    data = yaml.load(oldfile)
    yaml.dump(data, newfile)
with open('GameIndex[fixed2].yaml', encoding='utf8') as oldfile, open('GameIndex[fixed].yaml', 'w', encoding='utf8') as newfile:
    for line in oldfile:
        if '{' in line: line = line.replace('{', '{ ')
        if '}' in line: line = line.replace('}', ' }')
        if ': null' not in line: newfile.write(line)
os.remove('GameIndex[fixed2].yaml')