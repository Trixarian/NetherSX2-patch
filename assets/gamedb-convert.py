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

# Makes null show up so we can process them blow
def my_represent_none(self, data):
    return self.represent_scalar(u'tag:yaml.org,2002:null', u'null')

# Process file to make it compatible with NetherSX2
def process_db(file_name, clean_name):
    print('Processing ' + file_name + '...')
    if os.path.isfile(clean_name) and clean_name == 'GameIndex[fixed].yaml': os.remove('GameIndex[fixed].yaml')
    if os.path.isfile('GameIndex[temp].yaml'): os.remove('GameIndex[temp].yaml')
    with open(file_name, encoding='utf8') as newfile, open('GameIndex[temp].yaml', 'w', encoding='utf8') as tempfile:
        prev_line = ''
        for line in newfile:
            for key in replace_dic:
                if key in line: line = line.replace(key, replace_dic[key])
            if re.search(r'moveHandler: \".+\"', line): line = re.sub(r'moveHandler: \".+\"', 'textureInsideRT: 1', line)
            # We need the following four checks to fix ONE issue caused by someone inconsistently adding moonrunes to the GameDB
            if line == prev_line: continue
            if 'name:' in line and '"' not in line: continue
            if 'name:' in line and re.search(r'[A-Z]+: ', line): continue
            if not any(safe_char in line for safe_char in char_list) and not line.isascii(): continue
            if not any(ignore_word in line for ignore_word in ignore_list): tempfile.write(line)
            prev_line = line
    os.rename('GameIndex[temp].yaml', clean_name)

# Fixes issues created by yaml processing and removes empty keys
def fix_db(file_name):
    # Uses the Dark Arts (YAML Processing) to work it's magic
    print('Removing empty keys from ' + file_name + '...')
    with open(file_name, encoding='utf8') as newfile, open('GameIndex[temp].yaml', 'w', encoding='utf8') as tempfile:
        data = yaml.load(newfile)
        yaml.dump(data, tempfile)
    with open('GameIndex[temp].yaml', encoding='utf8') as tempfile, open(file_name, 'w', encoding='utf8') as newfile:
        for line in tempfile:
            if '{' in line: line = line.replace('{', '{ ')
            if '}' in line: line = line.replace('}', ' }')
            if ': null' not in line: newfile.write(line)
    os.remove('GameIndex[temp].yaml')

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
replace_dic = {'autoFlush: 2': 'autoFlush: 1', 'forceEvenSpritePosition:': 'wildArmsHack:', 'halfPixelOffset: 4': 'halfPixelOffset: 1', 'instantVU1:': 'InstantVU1SpeedHack:', 'mtvu:': 'MTVUSpeedHack:', 'mvuFlag:': 'mvuFlagSpeedHack:', 'name-en:': 'name:'}

# This is where the Magic Happens
process_db(gamedb_file, 'GameIndex[fixed].yaml')
print('Creating GameIndex[fixed].yaml...')
fix_db('GameIndex[fixed].yaml')
with open('GameIndex[fixed].yaml', encoding='utf8') as base, open('old/GameIndex[4248].yaml', encoding='utf8') as og, open('GameIndex[diff].yaml', encoding='utf8') as diff, open('GameIndex[temp].yaml', 'w', encoding='utf8') as merged:
    print('Loading GameDB entries to merge...')
    base_db = yaml.load(base)
    og_db = yaml.load(og)
    diff_db = yaml.load(diff)
    print('Merging GameDB entries...')
    base_db.update(og_db)
    base_db.update(diff_db)
    print('Creating GameIndex[merged].yaml file...')
    yaml.dump(base_db, merged)
# Have to make sure there isn't any bad entries in the merged file
process_db('GameIndex[merged].yaml', 'GameIndex[temp2].yaml')
os.remove('GameIndex[merged].yaml')
os.rename('GameIndex[temp2].yaml', 'GameIndex[merged].yaml')
fix_db('GameIndex[merged].yaml')
print('All Done!')