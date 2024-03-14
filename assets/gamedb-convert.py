#
# A simple script to make comparing GameDB files easier for NetherSX2
# Just drag and drop the GameIndex.yaml file from PCSX2 on to it to process it
#

import re, sys

if len(sys.argv) > 1: gamedb_file = sys.argv[1]
else: 
    print("Usage: gamedb-convert.py GameIndex.yaml")
    sys.exit()
ignore_list = ["bilinearUpscale", "cpuSpriteRenderLevel", "eeCycleRate", "eeDivRoundMode", "GSC_PolyphonyDigitalGames", "GSC_HitmanBloodMoney", "GSC_NFSUndercover", "GSC_MetalGearSolid3", "name-sort", "nativePaletteDraw", "OI_HauntingGround"]
replace_dic = {"mtvu:": "MTVUSpeedHack:", "mvuFlag:": "mvuFlagSpeedHack:", "instantVU1:": "InstantVU1SpeedHack:", "autoFlush: 2": "autoFlush: 1", "minimumBlendingLevel:": "recommendedBlendingLevel:", "name-en:": "name:"}

with open(gamedb_file, encoding="utf8") as oldfile, open('GameIndex[fixed].yaml', 'w', encoding="utf8") as newfile:
    for line in oldfile:
        if re.search(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]', line): continue
        if re.search(r'moveHandler: \".+\"', line): line = re.sub(r'moveHandler: \".+\"', 'textureInsideRT: 1', line)
        for key in replace_dic:
            if key in line: line = line.replace(key, replace_dic[key])
        if not any(ignore_word in line for ignore_word in ignore_list): newfile.write(line)