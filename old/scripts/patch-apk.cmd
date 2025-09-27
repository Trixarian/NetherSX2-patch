@echo off
:: Sets the window's title
Title NetherSX2 Patcher
:: Allows for Terminal Colors to be used
set col=lib\cmdcolor.exe
:: Setting base variables
set ver=v1.9
set patch=patch.xdelta
set vername=15210-%ver%-4248-noads
set md5hash=c98b0e4152d3b02fbfb9f62581abada5
set /A vercheck=0

:: Display Banner
echo \033[91m======================== | %col%
echo \033[91m NetherSX2 Patcher %ver% | %col%
echo \033[91m======================== | %col%

:: Makes sure Java is installed and in the PATH
java >nul 2>&1
if %errorlevel%==9009 goto nojava

:: Checks if there's a copy of 4248 in the folder and that it's named correctly
for /r %%i in (*.apk) do ( 
  for /f %%f in ('""lib\md5sum.exe" "%%i""') do (
    if %%f equ %md5hash% (
      ren "%%i" 15210-v1.5-4248.apk >nul 2>&1
    )
  )
)
:: Check if an NetherSX2 APK exists and if it's named correctly
if exist 15210-v1.5-4248-noads.apk set vername=15210-v1.5-4248-noads
if exist 15210-v1.8-4248-noads.apk (
  set /A vercheck=1
  set vername=15210-v1.8-4248-noads
)
if exist %vername%[patched].apk (
  set /A vercheck=1
  ren %vername%[patched].apk %vername%.apk >nul 2>&1
)
if not exist %vername%.apk (
  goto getapk 
) else (
  goto update
)

:patch
:: Check if the AetherSX2 APK is the right version
for /f %%f in ('""lib\md5sum.exe" "15210-v1.5-4248.apk""') do (
  if %%f neq %md5hash% goto wrongmd5
)
:: Check if we should use the Old UI
if exist old-ui.xdelta move old-ui.xdelta lib\ >nul 2>&1
if exist lib\old-ui.xdelta set patch=old-ui.xdelta
:: Patching the AetherSX2 into a copy of NetherSX2
set /A vercheck=1
if %patch% equ old-ui.xdelta (
  <nul set /p "=\033[96mPatching to \033[91mNetherSX2 with Old UI...          " | %col%
) else (
  <nul set /p "=\033[96mPatching to \033[91mNetherSX2 with New UI...          " | %col%
)
lib\xdelta -d -f -s 15210-v1.5-4248.apk lib\%patch% %vername%.apk
echo \033[92m[Done] | %col%
goto update

:update
:: Let's leave a backup copy of the NetherSX2 APK
copy %vername%.apk %vername%[patched].apk >nul 2>&1
:: Ad Services Cleanup
if %vercheck%==0 (
  <nul set /p "=\033[96mRemoving the \033[91mAd Services leftovers...         " | %col%
  lib\aapt r %vername%[patched].apk user-messaging-platform.properties >nul 2>&1
  lib\aapt r %vername%[patched].apk play-services-tasks.properties >nul 2>&1
  lib\aapt r %vername%[patched].apk play-services-measurement-sdk-api.properties >nul 2>&1
  lib\aapt r %vername%[patched].apk play-services-measurement-base.properties >nul 2>&1
  lib\aapt r %vername%[patched].apk play-services-basement.properties >nul 2>&1
  lib\aapt r %vername%[patched].apk play-services-base.properties >nul 2>&1
  lib\aapt r %vername%[patched].apk play-services-appset.properties >nul 2>&1
  lib\aapt r %vername%[patched].apk play-services-ads.properties >nul 2>&1
  lib\aapt r %vername%[patched].apk play-services-ads-lite.properties >nul 2>&1
  lib\aapt r %vername%[patched].apk play-services-ads-identifier.properties >nul 2>&1
  lib\aapt r %vername%[patched].apk play-services-ads-base.properties >nul 2>&1
  echo \033[92m[Done] | %col%
)

:: Updates the FAQ to show that we're using the latest version of NetherSX2
if %vercheck%==0 (
  <nul set /p "=\033[96mUpdating the \033[91mFAQ...                           " | %col%
  lib\aapt r %vername%[patched].apk assets/faq.html
  lib\aapt a %vername%[patched].apk assets/faq.html >nul 2>&1
  echo \033[92m[Done] | %col%
)

:: Updates to Latest GameDB with features removed that are not supported by the libemucore.so from March 13th
<nul set /p "=\033[96mUpdating the \033[91mGameDB...                        " | %col%
lib\aapt r %vername%[patched].apk assets/GameIndex.yaml
lib\aapt a %vername%[patched].apk assets/GameIndex.yaml >nul 2>&1
echo \033[92m[Done] | %col%

:: Updates the Game Controller Database
<nul set /p "=\033[96mUpdating the \033[91mController Database...           " | %col%
lib\aapt r %vername%[patched].apk assets/game_controller_db.txt
lib\aapt a %vername%[patched].apk assets/game_controller_db.txt >nul 2>&1
echo \033[92m[Done] | %col%

:: Updates the Widescreen Patches
<nul set /p "=\033[96mUpdating the \033[91mWidescreen Patches...            " | %col%
lib\aapt r %vername%[patched].apk assets/cheats_ws.zip
lib\aapt a %vername%[patched].apk assets/cheats_ws.zip >nul 2>&1
echo \033[92m[Done] | %col%

:: Updates the No-Interlacing Patches
<nul set /p "=\033[96mUpdating the \033[91mNo-Interlacing Patches...        " | %col%
lib\aapt r %vername%[patched].apk assets/cheats_ni.zip
lib\aapt a %vername%[patched].apk assets/cheats_ni.zip >nul 2>&1
echo \033[92m[Done] | %col%

:: Fixes License Compliancy Issue
if %vercheck%==0 (
  <nul set /p "=\033[96mFixing the \033[91mLicense Compliancy Issue...        " | %col%
  lib\aapt r %vername%[patched].apk assets/3rdparty.html
  lib\aapt a %vername%[patched].apk assets/3rdparty.html >nul 2>&1
  echo \033[92m[Done] | %col%
)

:: Adds the placeholder file that makes RetroAchievements Notifications work
if %vercheck%==0 (
  <nul set /p "=\033[96mFixing the \033[91mRetroAchievements Notifications... " | %col%
  lib\aapt r %vername%[patched].apk assets/placeholder.png >nul 2>&1
  lib\aapt a %vername%[patched].apk assets/placeholder.png >nul 2>&1
  echo \033[92m[Done] | %col%
)

:: Resigns the APK before exiting
<nul set /p "=\033[96mResigning the \033[91mNetherSX2 APK...                " | %col%
java -jar lib\apksigner.jar sign --ks lib\android.jks --ks-pass pass:android_sign --key-pass pass:android_sign_alias %vername%[patched].apk
:: Alternate Key:
:: java -jar lib\apksigner.jar sign --ks lib\public.jks --ks-pass pass:public %vername%[patched].apk
del %vername%[patched].apk.idsig >nul 2>&1
echo \033[92m[Done] | %col%
goto end

:getapk
set /A vercheck=1
<nul set /p "=\033[96mDownloading \033[94mAetherSX2...                      " | %col%
powershell -Command "(new-object System.Net.WebClient).DownloadFile('https://github.com/Trixarian/NetherSX2-patch/releases/download/0.0/15210-v1.5-4248.apk','15210-v1.5-4248.apk')"
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