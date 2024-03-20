#
# A simple script to make comparing GameDB files easier for NetherSX2
# Just drag and drop the GameIndex.yaml file from PCSX2 on to it to process it
#
import re, sys

if len(sys.argv) > 1: gamedb_file = sys.argv[1]
else: 
    print('Usage: gamedb-convert.py GameIndex.yaml')
    sys.exit()

ignore_list = ['bilinearUpscale', 'cpuSpriteRenderLevel', 'eeCycleRate', 'eeDivRoundMode', 'GSC_HitmanBloodMoney', 'GSC_MetalGearSolid3', 'GSC_NFSUndercover', 'GSC_PolyphonyDigitalGames', 'name-sort', 'nativePaletteDraw', 'OI_HauntingGround']
replace_dic = {'autoFlush: 2': 'autoFlush: 1', 'halfPixelOffset: 4': 'halfPixelOffset: 1', 'instantVU1:': 'InstantVU1SpeedHack:', 'minimumBlendingLevel:': 'recommendedBlendingLevel:', 'mtvu:': 'MTVUSpeedHack:', 'mvuFlag:': 'mvuFlagSpeedHack:', 'name-en:': 'name:'}

with open(gamedb_file, encoding='utf8') as oldfile, open('GameIndex[fixed].yaml', 'w', encoding='utf8') as newfile:
    prev_line = ''
    for line in oldfile:
        for key in replace_dic:
            if key in line: line = line.replace(key, replace_dic[key])
        if re.search(r'moveHandler: \".+\"', line): line = re.sub(r'moveHandler: \".+\"', 'textureInsideRT: 1', line)
        # We need the following three checks to fix ONE issue caused by an idiot that inconsistently added moonrunes to the GameDB
        if line == prev_line: continue
        if 'name:' in line and '"' not in line: continue
        if re.search(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]', line): continue
        if not any(ignore_word in line for ignore_word in ignore_list): newfile.write(line)
        prev_line = line