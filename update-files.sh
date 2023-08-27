#!/bin/bash
# Fixes License Compliancy Issue
aapt r 15210-v1.5-4248-noads.apk assets/3rdparty.html 
aapt a 15210-v1.5-4248-noads.apk assets/3rdparty.html

# Updates No Interlace Patches
aapt r 15210-v1.5-4248-noads.apk assets/cheats_ni.zip 
aapt a 15210-v1.5-4248-noads.apk assets/cheats_ni.zip

# Updates Widescreen Patches
aapt r 15210-v1.5-4248-noads.apk assets/cheats_ws.zip 
aapt a 15210-v1.5-4248-noads.apk assets/cheats_ws.zip

# Updates Game Controller Database
aapt r 15210-v1.5-4248-noads.apk assets/game_controller_db.txt
aapt a 15210-v1.5-4248-noads.apk assets/game_controller_db.txt

# Updates GameDB with removed features not supported by the libemucore.so from March 13th
aapt r 15210-v1.5-4248-noads.apk assets/GameIndex.yaml 
aapt a 15210-v1.5-4248-noads.apk assets/GameIndex.yaml

# Adds the placeholder file that makes RetroAchievements Notifications work
aapt a 15210-v1.5-4248-noads.apk assets/placeholder.png

# Resigns the APK before exiting
apksigner sign --ks lib/android.jks --ks-pass pass:android 15210-v1.5-4248-noads.apk
# Alternate Key:
# apksigner sign --ks lib/public.jks --ks-pass pass:public 15210-v1.5-4248-noads.apk
