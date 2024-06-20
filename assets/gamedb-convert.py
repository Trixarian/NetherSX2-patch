# A simple script to make comparing GameDB files easier for NetherSX2
# Just drag and drop the GameIndex.yaml file from PCSX2 on to it to process it
# Requires the ruamel.yaml library to be installed to work
# Type pip install ruamel.yaml in the terminal to install it

import re, sys, os
from ruamel.yaml import YAML

if len(sys.argv) > 1: gamedb_file = sys.argv[1]
else: 
    print('Usage: gamedb-convert.py GameIndex.yaml')
    sys.exit()

def my_represent_none(self, data):
    # Makes null show up so we can process it
    return self.represent_scalar(u'tag:yaml.org,2002:null', u'null')

# Set our YAML variables
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.default_flow_style = None
yaml.preserve_quotes = True
yaml.allow_duplicate_keys = True
yaml.width = 512
yaml.representer.add_representer(type(None), my_represent_none)

# Create filters to process the file with
char_list = ['ß', 'à', 'á', 'â', 'ã', 'ä', 'å', 'æ', 'ç', 'è', 'é', 'ê', 'ë', 'ì', 'í', 'î', 'ï', 'ð', 'ñ', 'ò', 'ó', 'ô', 'õ', 'ö', 'ø', 'ù', 'ú', 'û', 'ü', 'ý', 'þ', 'ÿ', '¸', 'À', 'Á', 'Â', 'Ã', 'Ä', 'Å', 'Æ', 'Ç', 'È', 'É', 'Ê', 'Ë', 'Ì', 'Í', 'Î', 'Ï', 'Ð', 'Ñ', 'Ò', 'Ó', 'Ô', 'Õ', 'Ö', 'Ø', 'Ù', 'Ú', 'Û', 'Ü', 'Ý', 'Þ']
ignore_list = ['bilinearUpscale', 'cpuSpriteRenderLevel', 'eeCycleRate', 'eeDivRoundMode', 'GSC_HitmanBloodMoney', 'GSC_MetalGearSolid3', 'GSC_NFSUndercover', 'GSC_PolyphonyDigitalGames', 'name-sort', 'nativePaletteDraw', 'nativeScaling', 'OI_HauntingGround']
replace_dic = {'autoFlush: 2': 'autoFlush: 1', 'forceEvenSpritePosition:': 'wildArmsHack:', 'halfPixelOffset: 4': 'halfPixelOffset: 1', 'instantVU1:': 'InstantVU1SpeedHack:', 'minimumBlendingLevel:': 'recommendedBlendingLevel:', 'mtvu:': 'MTVUSpeedHack:', 'mvuFlag:': 'mvuFlagSpeedHack:', 'name-en:': 'name:'}

# Process file to make it compatible with NetherSX2
print('Processing the GameDB file...')
with open(gamedb_file, encoding='utf8') as oldfile, open('GameIndex[fixed].yaml', 'w', encoding='utf8') as newfile:
    prev_line = ''
    for line in oldfile:
        for key in replace_dic:
            if key in line: line = line.replace(key, replace_dic[key])
        if re.search(r'moveHandler: \".+\"', line): line = re.sub(r'moveHandler: \".+\"', 'textureInsideRT: 1', line)
        # We need the following four checks to fix ONE issue caused by a moron that inconsistently added moonrunes to the GameDB
        if line == prev_line: continue
        if 'name:' in line and '"' not in line: continue
        if 'name:' in line and re.search(r'[A-Z]+: ', line): continue
        if not any(safe_char in line for safe_char in char_list) and not line.isascii(): continue
        if not any(ignore_word in line for ignore_word in ignore_list): newfile.write(line)
        prev_line = line

# Uses the Magic of YAML Processing to clean up empty keys
print('Removing the empty keys from the GameDB...')
with open('GameIndex[fixed].yaml', encoding='utf8') as newfile, open('GameIndex[temp].yaml', 'w', encoding='utf8') as tempfile:
    data = yaml.load(newfile)
    yaml.dump(data, tempfile)
with open('GameIndex[temp].yaml', encoding='utf8') as tempfile, open('GameIndex[fixed].yaml', 'w', encoding='utf8') as newfile:
    for line in tempfile:
        if '{' in line: line = line.replace('{', '{ ')
        if '}' in line: line = line.replace('}', ' }')
        if ': null' not in line: newfile.write(line)
print('All Done!')
os.remove('GameIndex[temp].yaml')