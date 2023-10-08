@echo off
:: Allows for Terminal Colors to be used
set col=lib\cmdcolor.exe
set md5hash=c98b0e4152d3b02fbfb9f62581abada5

:: Display Banner
echo \033[91m============================ | %col%
echo \033[91m NetherSX2 Theme Reset v1.7  | %col%
echo \033[91m============================ | %col%

:: Check if the NetherSX2 APK exists and if it's named correctly
if not exist 15210-v1.5-4248-noads.apk goto nofile
:: Check if the NetherSX2 APK isn't just a renamed AetherSX2 4248 APK
for /f %%f in ('""lib\md5sum.exe" "15210-v1.5-4248-noads.apk""') do (
  if %%f equ %md5hash% goto nofile
)

:: Reset to the default UI Theme
<nul set /p "=\033[96mResetting \033[91mUI Theme...          " | %col%
:: Temporarially renaming folders to restore original UI
move res/drawable res/drawable-tmp > nul
move res/drawable-og res/drawable > nul
for /r %%i in (res\drawable\*.xml) do (
  lib\aapt r 15210-v1.5-4248-noads.apk res/drawable/%%~nxi > nul
  lib\aapt a 15210-v1.5-4248-noads.apk res/drawable/%%~nxi > nul
  lib\aapt r 15210-v1.5-4248-noads.apk res/drawable/%%~ni.png > nul
)
:: And moving them back
move res/drawable res/drawable-og > nul
move res/drawable-tmp res/drawable > nul
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