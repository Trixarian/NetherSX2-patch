:: Fixes License Compliancy Issue
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk assets/3rdparty.html 
"%~dp0lib\aapt" a 15210-v1.5-4248-noads.apk assets/3rdparty.html

:: Updates No Interlace Patches
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk assets/cheats_ni.zip 
"%~dp0lib\aapt" a 15210-v1.5-4248-noads.apk assets/cheats_ni.zip

:: Updates Widescreen Patches
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk assets/cheats_ws.zip 
"%~dp0lib\aapt" a 15210-v1.5-4248-noads.apk assets/cheats_ws.zip

:: Updates Game Controller Database
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk assets/game_controller_db.txt
"%~dp0lib\aapt" a 15210-v1.5-4248-noads.apk assets/game_controller_db.txt

:: Updates GameDB with removed features not supported by the libemucore.so from March 13th
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk assets/GameIndex.yaml 
"%~dp0lib\aapt" a 15210-v1.5-4248-noads.apk assets/GameIndex.yaml

:: Adds the placeholder file that makes RetroAchievements Notifications work
"%~dp0lib\aapt" a 15210-v1.5-4248-noads.apk assets/placeholder.png

:: Resigns the APK before exiting
"%~dp0lib\apksigner" sign --ks "%~dp0lib\platform.jks" --ks-pass pass:android 15210-v1.5-4248-noads.apk
pause