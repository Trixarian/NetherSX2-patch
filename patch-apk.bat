@echo off
:: Sets the window's title
Title NetherSX2 Patcher
:: Allows for Terminal Colors to be used
set col=lib\cmdcolor.exe
set md5hash=c98b0e4152d3b02fbfb9f62581abada5

:: Display Banner
echo \033[91m======================== | %col%
echo \033[91m NetherSX2 Patcher v1.7  | %col%
echo \033[91m======================== | %col%

:: Makes sure Java is installed and in the PATH
java >nul 2>&1
if %errorlevel%==9009 goto nojava

:: Check if an NetherSX2 APK exists and if it's named correctly
if exist 15210-v1.5-4248-noads[patched].apk ren 15210-v1.5-4248-noads[patched].apk 15210-v1.5-4248-noads.apk >nul 2>&1
if exist 15210-v1.5-4248.apk goto patch
if not exist 15210-v1.5-4248-noads.apk ( goto getapk ) else ( goto update )

:patch
:: Check if the AetherSX2 APK is the right version
for /f %%f in ('""lib\md5sum.exe" "15210-v1.5-4248.apk""') do (
  if %%f neq %md5hash% goto wrongmd5
)
:: Patching the AetherSX2 into a copy of NetherSX2
<nul set /p "=\033[96mPatching to \033[91mNetherSX2...                      " | %col%
lib\xdelta -d -f -s 15210-v1.5-4248.apk lib\patch.xdelta 15210-v1.5-4248-noads.apk
echo \033[92m[Done] | %col%
goto update

:update
:: Let's leave a backup copy of the NetherSX2 APK
copy 15210-v1.5-4248-noads.apk 15210-v1.5-4248-noads[patched].apk >nul 2>&1
:: Ad Services Cleanup
<nul set /p "=\033[96mRemoving the \033[91mAd Services leftovers...         " | %col%
lib\aapt r 15210-v1.5-4248-noads[patched].apk user-messaging-platform.properties >nul 2>&1
lib\aapt r 15210-v1.5-4248-noads[patched].apk play-services-tasks.properties >nul 2>&1
lib\aapt r 15210-v1.5-4248-noads[patched].apk play-services-measurement-sdk-api.properties >nul 2>&1
lib\aapt r 15210-v1.5-4248-noads[patched].apk play-services-measurement-base.properties >nul 2>&1
lib\aapt r 15210-v1.5-4248-noads[patched].apk play-services-basement.properties >nul 2>&1
lib\aapt r 15210-v1.5-4248-noads[patched].apk play-services-base.properties >nul 2>&1
lib\aapt r 15210-v1.5-4248-noads[patched].apk play-services-appset.properties >nul 2>&1
lib\aapt r 15210-v1.5-4248-noads[patched].apk play-services-ads.properties >nul 2>&1
lib\aapt r 15210-v1.5-4248-noads[patched].apk play-services-ads-lite.properties >nul 2>&1
lib\aapt r 15210-v1.5-4248-noads[patched].apk play-services-ads-identifier.properties >nul 2>&1
lib\aapt r 15210-v1.5-4248-noads[patched].apk play-services-ads-base.properties >nul 2>&1
echo \033[92m[Done] | %col%

:: Adds Additional Options to App Settings
<nul set /p "=\033[96mAdding more options to \033[91mApp Settings...        " | %col%
lib\aapt r 15210-v1.5-4248-noads[patched].apk res/xml/advanced_preferences.xml
lib\aapt a 15210-v1.5-4248-noads[patched].apk res/xml/advanced_preferences.xml >nul 2>&1
lib\aapt r 15210-v1.5-4248-noads[patched].apk res/xml/graphics_preferences.xml
lib\aapt a 15210-v1.5-4248-noads[patched].apk res/xml/graphics_preferences.xml >nul 2>&1
echo \033[92m[Done] | %col%

:: Updates the FAQ to show that we're using the latest version of NetherSX2
<nul set /p "=\033[96mUpdating the \033[91mFAQ...                           " | %col%
lib\aapt r 15210-v1.5-4248-noads[patched].apk assets/faq.html
lib\aapt a 15210-v1.5-4248-noads[patched].apk assets/faq.html >nul 2>&1
echo \033[92m[Done] | %col%

:: Updates to Latest GameDB with features removed that are not supported by the libemucore.so from March 13th
<nul set /p "=\033[96mUpdating the \033[91mGameDB...                        " | %col%
lib\aapt r 15210-v1.5-4248-noads[patched].apk assets/GameIndex.yaml
lib\aapt a 15210-v1.5-4248-noads[patched].apk assets/GameIndex.yaml >nul 2>&1
echo \033[92m[Done] | %col%

:: Updates the Game Controller Database
<nul set /p "=\033[96mUpdating the \033[91mController Database...           " | %col%
lib\aapt r 15210-v1.5-4248-noads[patched].apk assets/game_controller_db.txt
lib\aapt a 15210-v1.5-4248-noads[patched].apk assets/game_controller_db.txt >nul 2>&1
echo \033[92m[Done] | %col%

:: Updates the Widescreen Patches
<nul set /p "=\033[96mUpdating the \033[91mWidescreen Patches...            " | %col%
lib\aapt r 15210-v1.5-4248-noads[patched].apk assets/cheats_ws.zip
lib\aapt a 15210-v1.5-4248-noads[patched].apk assets/cheats_ws.zip >nul 2>&1
echo \033[92m[Done] | %col%

:: Updates the No-Interlacing Patches
<nul set /p "=\033[96mUpdating the \033[91mNo-Interlacing Patches...        " | %col%
lib\aapt r 15210-v1.5-4248-noads[patched].apk assets/cheats_ni.zip
lib\aapt a 15210-v1.5-4248-noads[patched].apk assets/cheats_ni.zip >nul 2>&1
echo \033[92m[Done] | %col%

:: Fixes License Compliancy Issue
<nul set /p "=\033[96mFixing the \033[91mLicense Compliancy Issue...        " | %col%
lib\aapt r 15210-v1.5-4248-noads[patched].apk assets/3rdparty.html
lib\aapt a 15210-v1.5-4248-noads[patched].apk assets/3rdparty.html >nul 2>&1
echo \033[92m[Done] | %col%

:: Adds the placeholder file that makes RetroAchievements Notifications work
<nul set /p "=\033[96mFixing the \033[91mRetroAchievements Notifications... " | %col%
lib\aapt r 15210-v1.5-4248-noads[patched].apk assets/placeholder.png >nul 2>&1
lib\aapt a 15210-v1.5-4248-noads[patched].apk assets/placeholder.png >nul 2>&1
echo \033[92m[Done] | %col%

:: Resigns the APK before exiting
<nul set /p "=\033[96mResigning the \033[91mNetherSX2 APK...                " | %col%
java -jar lib\apksigner.jar sign --ks lib\android.jks --ks-pass pass:android 15210-v1.5-4248-noads[patched].apk  
:: Alternate Key:
:: java -jar lib\apksigner.jar sign --ks lib\public.jks --ks-pass pass:public 15210-v1.5-4248-noads[patched].apk
del 15210-v1.5-4248-noads[patched].apk.idsig >nul 2>&1
echo \033[92m[Done] | %col%
goto end

:getapk
<nul set /p "=\033[96mDownloading \033[94mAetherSX2...                      " | %col%
powershell -Command "(new-object System.Net.WebClient).DownloadFile('https://www.aethersx2.com/archive/android/alpha/15210-v1.5-4248.apk','15210-v1.5-4248.apk')"
echo \033[92m[Done] | %col%
goto patch

:wrongmd5
echo \033[91mError: Wrong APK provided! | %col%
echo \033[91mPlease provide a copy of AtherSX2 4248 or NetherSX2! | %col%
goto end

:nojava
echo \033[91mError: The Java Development Kit is not installed or a restart required! | %col%
echo \033[91mPlease download and install the JDK from https://www.oracle.com/java/technologies/downloads/#jdk21-windows | %col%
goto end

:end
pause