:: Fixes License Compliancy Issue
lib\aapt r 15210-v1.5-4248-noads.apk assets/3rdparty.html
lib\aapt a 15210-v1.5-4248-noads.apk assets/3rdparty.html

:: Updates No Interlace Patches
lib\aapt r 15210-v1.5-4248-noads.apk assets/cheats_ni.zip
lib\aapt a 15210-v1.5-4248-noads.apk assets/cheats_ni.zip

:: Updates Widescreen Patches
lib\aapt r 15210-v1.5-4248-noads.apk assets/cheats_ws.zip
lib\aapt a 15210-v1.5-4248-noads.apk assets/cheats_ws.zip

:: Updates Game Controller Database
lib\aapt r 15210-v1.5-4248-noads.apk assets/game_controller_db.txt
lib\aapt a 15210-v1.5-4248-noads.apk assets/game_controller_db.txt

:: Updates GameDB with removed features not supported by the libemucore.so from March 13th
lib\aapt r 15210-v1.5-4248-noads.apk assets/GameIndex.yaml
lib\aapt a 15210-v1.5-4248-noads.apk assets/GameIndex.yaml

:: Adds the placeholder file that makes RetroAchievements Notifications work
lib\aapt a 15210-v1.5-4248-noads.apk assets/placeholder.png

:: Resigns the APK before exiting
java -jar lib\apksigner.jar sign --ks lib\android.jks --ks-pass pass:android 15210-v1.5-4248-noads.apk
:: Alternate Key:
:: java -jar lib\apksigner.jar sign --ks lib\public.jks --ks-pass pass:public 15210-v1.5-4248-noads.apk
pause
