# A simple script to make comparing GameDB files easier for NetherSX2
# Just drag and drop the GameIndex.yaml file from PCSX2 on to it to process it
# Requires the ruamel.yaml library to be installed to work
# Type pip install ruamel.yaml in the terminal to install it
import re, sys, os
from ruamel.yaml import YAML

def my_represent_none(self, data):
    return self.represent_scalar(u'tag:yaml.org,2002:null', u'null')

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.default_flow_style = False
yaml.preserve_quotes = True
yaml.allow_duplicate_keys = True
yaml.width = 512
yaml.representer.add_representer(type(None), my_represent_none)

char_list = ['ß', 'à', 'á', 'â', 'ã', 'ä', 'å', 'æ', 'ç', 'è', 'é', 'ê', 'ë', 'ì', 'í', 'î', 'ï', 'ð', 'ñ', 'ò', 'ó', 'ô', 'õ', 'ö', 'ø', 'ù', 'ú', 'û', 'ü', 'ý', 'þ', 'ÿ', '¸', 'À', 'Á', 'Â', 'Ã', 'Ä', 'Å', 'Æ', 'Ç', 'È', 'É', 'Ê', 'Ë', 'Ì', 'Í', 'Î', 'Ï', 'Ð', 'Ñ', 'Ò', 'Ó', 'Ô', 'Õ', 'Ö', 'Ø', 'Ù', 'Ú', 'Û', 'Ü', 'Ý', 'Þ']
key_list = ['clampModes', 'dynaPatches', 'gameFixes', 'gsHWFixes', 'memcardFilters', 'patches', 'roundModes', 'speedHacks']
key_order = ['name', 'name-sort', 'name-en', 'region', 'compat', 'clampModes', 'roundModes', 'gameFixes', 'speedHacks', 'gsHWFixes', 'patches', 'dynaPatches', 'memcardFilters']
ignore_list = ['bilinearUpscale', 'cpuSpriteRenderLevel', 'eeCycleRate', 'GSC_DTGames', 'GSC_GuitarHero', 'GSC_HitmanBloodMoney', 'GSC_MetalGearSolid3', 'GSC_NFSUndercover', 'GSC_PolyphonyDigitalGames', 'name-sort', 'nativePaletteDraw', 'nativeScaling', 'OI_HauntingGround']
replace_dict = {'autoFlush: 2': 'autoFlush: 1', 'forceEvenSpritePosition:': 'wildArmsHack:', 'GSC_NamcoGames': 'GSC_Tekken5', 'halfPixelOffset: 4': 'halfPixelOffset: 2', 'halfPixelOffset: 5': 'halfPixelOffset: 2', 'instantVU1:': 'InstantVU1SpeedHack:', 'mtvu:': 'MTVUSpeedHack:', 'mvuFlag:': 'mvuFlagSpeedHack:', 'name-en:': 'name:', 'PlayStation2': 'PlayStation 2'}

def sort_keys(my_dict):
    sorted_data = {}
    for key, value in my_dict.items():
        if isinstance(value, dict):
            sorted_nested = {}
            for nested_key in key_order:
                if nested_key in value: sorted_nested[nested_key] = value[nested_key]
            sorted_data[key] = sorted_nested
        else: sorted_data[key] = value
    return sorted_data

def process_db(file_name, clean_name):
    if not file_name == 'GameIndex[temp3].yaml': print('Processing ' + os.path.basename(file_name) + '...')
    if os.path.isfile(clean_name) and clean_name == 'GameIndex[fixed].yaml': os.remove('GameIndex[fixed].yaml')
    if os.path.isfile('GameIndex[temp].yaml'): os.remove('GameIndex[temp].yaml')
    with open(file_name, encoding='utf8') as newfile, open('GameIndex[temp].yaml', 'w', encoding='utf8') as tempfile:
        prev_line = ''
        for line in newfile:
            if any(k := key for key in replace_dict if key in line): line = line.replace(k, replace_dict[k])
            if re.search(r'moveHandler: \".+\"', line):
                line = re.sub(r'moveHandler: \".+\"', 'textureInsideRT: 1', line)
            if line == prev_line: continue
            if 'name:' in line and ('"' not in line or re.search(r'[A-Z]+: ', line)): continue
            if not any(safe_char in line for safe_char in char_list) and not line.isascii(): continue
            if not any(ignore_word in line for ignore_word in ignore_list): tempfile.write(line)
            prev_line = line
    os.rename('GameIndex[temp].yaml', clean_name)

def restore_fix(file_name):
    req_sort = False
    print('Processing ' + os.path.basename(file_name) + '...')
    if os.path.isfile('GameIndex[temp3].yaml'): os.remove('GameIndex[temp3].yaml')
    with open(file_name, encoding='utf8') as newfile, open('GameIndex[temp3].yaml', 'w', encoding='utf8') as tempfile:
        my_dict = yaml.load(newfile)
        for key, value in my_dict.items():
            if 'roundModes' in value and 'eeDivRoundMode' in value['roundModes']:
                try:
                    del my_dict[key]['roundModes']['eeDivRoundMode']
                    if not value['roundModes']: del value['roundModes']
                    if 'gameFixes' in value:
                        if isinstance(value['gameFixes'], list): 
                            my_dict[key]['gameFixes'].append('FpuNegDivHack')
                    else:
                        if not req_sort: req_sort = True 
                        my_dict[key]['gameFixes'] = ['FpuNegDivHack']
                except KeyError: continue
        if req_sort: my_dict.update(sort_keys(my_dict))
        yaml.dump(my_dict, tempfile)
    process_db('GameIndex[temp3].yaml', 'GameIndex[fixed].yaml')

def process_dict(my_dict, new_dict):
    req_sort = False
    my_dict = {k: v for k, v in my_dict.items() if any(required_key in v for required_key in key_list)}
    for key, value in my_dict.items():
        if 'name' in value and key in new_dict:
            try:
                if not my_dict[key]['name'] in new_dict[key]['name']:
                    my_dict[key]['name'] = new_dict[key]['name'] 
            except KeyError: continue
    for key, value in new_dict.items():
        for nested_key in key_list:
            if nested_key in value and key in my_dict:
                try:
                    if not my_dict[key][nested_key]: continue 
                except KeyError:
                    if not req_sort: req_sort = True
                    my_dict[key][nested_key] = new_dict[key][nested_key]
    if req_sort: my_dict.update(sort_keys(my_dict))
    return my_dict

def fix_db(file_name):
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

restore_fix(gamedb_file)
print('Creating GameIndex[fixed].yaml...')
fix_db('GameIndex[fixed].yaml')
with open('GameIndex[fixed].yaml', encoding='utf8') as base, open('old/GameIndex[4248].yaml', encoding='utf8') as og, open('GameIndex[diff].yaml', encoding='utf8') as diff, open('GameIndex[merged].yaml', 'w', encoding='utf8') as merged:
    print('Loading GameDB entries to merge...')
    base_db = yaml.load(base)
    og_db = yaml.load(og)
    diff_db = yaml.load(diff)
    print('Processing older GameDB prior to merging...')
    og_db = process_dict(og_db, base_db)
    diff_db = process_dict(diff_db, base_db)
    print('Merging GameDB entries...')
    base_db.update(og_db)
    base_db.update(diff_db)
    print('Creating GameIndex[merged].yaml file...')
    yaml.dump(base_db, merged)
process_db('GameIndex[merged].yaml', 'GameIndex[temp2].yaml')
if os.path.isfile('GameIndex[temp3].yaml'): os.remove('GameIndex[temp3].yaml')
if os.path.isfile('GameIndex[merged].yaml'): os.remove('GameIndex[merged].yaml')
os.rename('GameIndex[temp2].yaml', 'GameIndex[merged].yaml')
fix_db('GameIndex[merged].yaml')
print('All Done!')