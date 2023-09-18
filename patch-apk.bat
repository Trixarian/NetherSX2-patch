@echo off
:: Allows for Terminal Colors to be used
set col=lib\cmdcolor.exe
set md5hash=c98b0e4152d3b02fbfb9f62581abada5

:: Display Banner
echo \033[91m======================== | %col%
echo \033[91m NetherSX2 Patcher v1.6  | %col%
echo \033[91m======================== | %col%

:: Check if the NetherSX2 APK exists and if it's named correctly
if not exist 15210-v1.5-4248-noads.apk goto nofile
:: Check if the NetherSX2 APK isn't just a renamed AetherSX2 4248 APK
for /f %%f in ('""lib\md5sum.exe" "15210-v1.5-4248-noads.apk""') do (
  if %%f equ %md5hash% goto nofile
)

:: Ad Services Cleanup
<nul set /p "=\033[96mRemoving the \033[91mAd Services leftovers...         " | %col%
lib\aapt r 15210-v1.5-4248-noads.apk user-messaging-platform.properties > nul
lib\aapt r 15210-v1.5-4248-noads.apk play-services-tasks.properties > nul
lib\aapt r 15210-v1.5-4248-noads.apk play-services-measurement-sdk-api.properties > nul
lib\aapt r 15210-v1.5-4248-noads.apk play-services-measurement-base.properties > nul
lib\aapt r 15210-v1.5-4248-noads.apk play-services-basement.properties > nul
lib\aapt r 15210-v1.5-4248-noads.apk play-services-base.properties > nul
lib\aapt r 15210-v1.5-4248-noads.apk play-services-appset.properties > nul
lib\aapt r 15210-v1.5-4248-noads.apk play-services-ads.properties > nul
lib\aapt r 15210-v1.5-4248-noads.apk play-services-ads-lite.properties > nul
lib\aapt r 15210-v1.5-4248-noads.apk play-services-ads-identifier.properties > nul
lib\aapt r 15210-v1.5-4248-noads.apk play-services-ads-base.properties > nul
echo \033[92m[Done] | %col%

:: Updates the FAQ to show that we're using the latest version of NetherSX2
<nul set /p "=\033[96mUpdating the \033[91mFAQ...                           " | %col%
lib\aapt r 15210-v1.5-4248-noads.apk assets/faq.html
lib\aapt a 15210-v1.5-4248-noads.apk assets/faq.html > nul
echo \033[92m[Done] | %col%

:: Updates to Latest GameDB with features removed that are not supported by the libemucore.so from March 13th
<nul set /p "=\033[96mUpdating the \033[91mGameDB...                        " | %col%
lib\aapt r 15210-v1.5-4248-noads.apk assets/GameIndex.yaml
lib\aapt a 15210-v1.5-4248-noads.apk assets/GameIndex.yaml  > nul
echo \033[92m[Done] | %col%

:: Updates the Game Controller Database
<nul set /p "=\033[96mUpdating the \033[91mController Database...           " | %col%
lib\aapt r 15210-v1.5-4248-noads.apk assets/game_controller_db.txt
lib\aapt a 15210-v1.5-4248-noads.apk assets/game_controller_db.txt  > nul
echo \033[92m[Done] | %col%

:: Updates the Widescreen Patches
<nul set /p "=\033[96mUpdating the \033[91mWidescreen Patches...            " | %col%
lib\aapt r 15210-v1.5-4248-noads.apk assets/cheats_ws.zip
lib\aapt a 15210-v1.5-4248-noads.apk assets/cheats_ws.zip  > nul
echo \033[92m[Done] | %col%

:: Updates the No-Interlacing Patches
<nul set /p "=\033[96mUpdating the \033[91mNo-Interlacing Patches...        " | %col%
lib\aapt r 15210-v1.5-4248-noads.apk assets/cheats_ni.zip
lib\aapt a 15210-v1.5-4248-noads.apk assets/cheats_ni.zip  > nul
echo \033[92m[Done] | %col%

:: Fixes License Compliancy Issue
<nul set /p "=\033[96mFixing the \033[91mLicense Compliancy Issue...        " | %col%
lib\aapt r 15210-v1.5-4248-noads.apk assets/3rdparty.html
lib\aapt a 15210-v1.5-4248-noads.apk assets/3rdparty.html > nul
echo \033[92m[Done] | %col%

:: Adds the placeholder file that makes RetroAchievements Notifications work
<nul set /p "=\033[96mFixing the \033[91mRetroAchievements Notifications... " | %col%
lib\aapt r 15210-v1.5-4248-noads.apk assets/placeholder.png > nul
lib\aapt a 15210-v1.5-4248-noads.apk assets/placeholder.png > nul
echo \033[92m[Done] | %col%

:: Resigns the APK before exiting
<nul set /p "=\033[96mResigning the \033[91mNetherSX2 APK...                " | %col%
java -jar lib\apksigner.jar sign --ks lib\android.jks --ks-pass pass:android 15210-v1.5-4248-noads.apk
:: Alternate Key:
:: java -jar lib\apksigner.jar sign --ks lib\public.jks --ks-pass pass:public 15210-v1.5-4248-noads.apk
echo \033[92m[Done] | %col%
goto end

:nofile
echo \033[31mError: No APK found or wrong one provided! | %col%
echo \033[31mPlease provide a copy of NetherSX2 named 15210-v1.5-4248-noads.apk! | %col%
goto end

:end
pause