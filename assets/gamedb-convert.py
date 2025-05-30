# A simple script to make comparing GameDB files easier for NetherSX2
# Just drag and drop the GameIndex.yaml file from PCSX2 on to it to process it
# Requires the ruamel.yaml library to be installed to work
# Type pip install ruamel.yaml in the terminal to install it
import re, sys, os
from ruamel.yaml import YAML

# Makes null show up so we can process it below
def my_represent_none(self, data):
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
key_list = ['clampModes', 'dynaPatches', 'gameFixes', 'gsHWFixes', 'memcardFilters', 'patches', 'roundModes', 'speedHacks']
ignore_list = ['bilinearUpscale', 'cpuSpriteRenderLevel', 'eeCycleRate', 'eeDivRoundMode', 'GSC_DTGames', 'GSC_GuitarHero', 'GSC_HitmanBloodMoney', 'GSC_MetalGearSolid3', 'GSC_NFSUndercover', 'GSC_PolyphonyDigitalGames', 'name-sort', 'nativePaletteDraw', 'nativeScaling', 'OI_HauntingGround']
replace_dic = {'autoFlush: 2': 'autoFlush: 1', 'forceEvenSpritePosition:': 'wildArmsHack:', 'GSC_NamcoGames': 'GSC_Tekken5', 'halfPixelOffset: 4': 'halfPixelOffset: 1', 'halfPixelOffset: 5': 'halfPixelOffset: 1', 'instantVU1:': 'InstantVU1SpeedHack:', 'mtvu:': 'MTVUSpeedHack:', 'mvuFlag:': 'mvuFlagSpeedHack:', 'name-en:': 'name:'}

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
            # Bruh... This is a really embarrasing typo you searched and replaced with: 
            if 'PlayStation2' in line: line = line.replace('PlayStation2', 'PlayStation 2')
            if re.search(r'moveHandler: \".+\"', line): line = re.sub(r'moveHandler: \".+\"', 'textureInsideRT: 1', line)
            # We need the following four checks to fix ONE issue caused by someone inconsistently adding moonrunes to the GameDB
            if line == prev_line: continue
            if 'name:' in line and '"' not in line: continue
            if 'name:' in line and re.search(r'[A-Z]+: ', line): continue
            if not any(safe_char in line for safe_char in char_list) and not line.isascii(): continue
            if not any(ignore_word in line for ignore_word in ignore_list): tempfile.write(line)
            prev_line = line
    os.rename('GameIndex[temp].yaml', clean_name)

# Allows us to keep the newer names
def process_dict(my_dict, new_dict):
    for key, value in my_dict.items():
        if 'name' in value and key in new_dict:
            try:
                if new_dict[key]['name']:
                    if not my_dict[key]['name'] == new_dict[key]['name']:
                        my_dict[key]['name'] = new_dict[key]['name']
            except KeyError:
                continue
    return my_dict

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

if len(sys.argv) > 1: gamedb_file = sys.argv[1]
else: 
    print('Usage: python gamedb-convert.py GameIndex.yaml')
    sys.exit()

# This is where the Magic Happens
process_db(gamedb_file, 'GameIndex[fixed].yaml')
print('Creating GameIndex[fixed].yaml...')
fix_db('GameIndex[fixed].yaml')
with open('GameIndex[fixed].yaml', encoding='utf8') as base, open('old/GameIndex[4248].yaml', encoding='utf8') as og, open('GameIndex[diff].yaml', encoding='utf8') as diff, open('GameIndex[merged].yaml', 'w', encoding='utf8') as merged:
    print('Loading GameDB entries to merge...')
    base_db = yaml.load(base)
    # Load in the two yaml files that will change the converted file and remove entries without any settings
    og_db = yaml.load(og)
    diff_db = yaml.load(diff)
    print('Pre-processing GameDBs prior to merging...')
    # Removing entries without settings from the two DBs we'll be merging into the converted one
    og_db = {k: v for k, v in og_db.items() if any(required_key in v for required_key in key_list)}
    diff_db = {k: v for k, v in diff_db.items() if any(required_key in v for required_key in key_list)}
    # Grabbing the newer name entries to use with the older and diff GameDB files
    og_db = process_dict(og_db, base_db)
    diff_db = process_dict(diff_db, base_db)
    print('Merging GameDB entries...')
    base_db.update(og_db)
    base_db.update(diff_db)
    print('Creating GameIndex[merged].yaml file...')
    yaml.dump(base_db, merged)
# Have to make sure there isn't any bad entries in the merged file
process_db('GameIndex[merged].yaml', 'GameIndex[temp2].yaml')
if os.path.isfile('GameIndex[merged].yaml'): os.remove('GameIndex[merged].yaml')
os.rename('GameIndex[temp2].yaml', 'GameIndex[merged].yaml')
fix_db('GameIndex[merged].yaml')
print('All Done!')