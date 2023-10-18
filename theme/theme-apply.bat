@echo off
:: Allows for Terminal Colors to be used
set col=lib\cmdcolor.exe
set md5hash=c98b0e4152d3b02fbfb9f62581abada5

:: Display Banner
echo \033[91m============================== | %col%
echo \033[91m NetherSX2 Theme-o-Matic v1.7  | %col%
echo \033[91m============================== | %col%

:: Check if the NetherSX2 APK exists and if it's named correctly
if not exist 15210-v1.5-4248-noads.apk goto nofile
:: Check if the NetherSX2 APK isn't just a renamed AetherSX2 4248 APK
for /f %%f in ('""lib\md5sum.exe" "15210-v1.5-4248-noads.apk""') do (
  if %%f equ %md5hash% goto nofile
)

:: Adds UI Theme to APK
<nul set /p "=\033[96mApplying the \033[91mCustom UI Theme..." | %col%
for /r %%i in (res\drawable\*.png) do (
  lib\aapt r 15210-v1.5-4248-noads.apk res/drawable/%%~nxi > nul
  lib\aapt a 15210-v1.5-4248-noads.apk res/drawable/%%~nxi > nul
  lib\aapt r 15210-v1.5-4248-noads.apk res/drawable/%%~ni.xml > nul
)
echo \033[92m[Done] | %col%

:: Resigns the APK before exiting
<nul set /p "=\033[96mResigning the \033[91mNetherSX2 APK... " | %col%
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