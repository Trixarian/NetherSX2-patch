@echo off
:: Sets the window's title
Title NetherSX2 Builder
:: ********************************* CONFIG **********************************
set patch_name=NetherSX2 Builder v1.9
set patch_author=
set md5hash=c98b0e4152d3b02fbfb9f62581abada5
set xdelta_name=nethersx2.xdelta
set patched_end=-noads
:: ***************************************************************************

:: Setting Base Variables
set p2f=%~dp0
set input_path=%p2f%OriginalAPK
set output_path=%p2f%PatchedAPK
set xdelta_patch="%p2f%lib\%xdelta_name%"
set col="%p2f%lib\cmdcolor.exe"

:: Preparing to Start
call :strlen titlen patch_name
call :strlen autlen patch_author
set /A autlen=%autlen%+3
if %titlen% geq %autlen% ( 
  set /A result=%titlen%
) else (
  set /A result=%autlen%
)
set bline===
set /A index=1
:while
if %index% leq %result% (
   set /A index=index+1
   set bline=%bline%=
   goto :while
)

:: Opening Banner
echo \033[91m%bline% | %col%
echo \033[91m %patch_name% | %col%
if %autlen% gtr 3 echo \033[91m by %patch_author% | %col%
echo \033[91m%bline% | %col%

:: Preparing to Patch
:: Checks if the input folder exists
if not exist "%input_path%\" md "%input_path%"
cd "%input_path%"
:: Checks if there's an apk to patch and if the md5 hash matches
:: Otherwise it downloads it from the Discord
if not exist *.apk goto nofile
for /r %%i in (*.apk) do ( 
  for /f %%f in ('""%p2f%lib\md5sum.exe" "%%i""') do (
    if %%f equ %md5hash% (
      goto patch
    ) else (
      goto wrongmd5
    )   
  )
)

:patch
:: Checks if the output folder exists
if not exist "%output_path%\" md "%output_path%"
:: Patching the file
<nul set /p "=\033[96mPatching to \033[91mNetherSX2... " | %col%
for /r %%i in (*.apk) do "%p2f%lib\xdelta.exe" -d -f -s "%%i" %xdelta_patch% "%output_path%\%%~ni%patched_end%.apk"
ren "%output_path%\15210-v1.5-4248-noads.apk" 15210-v1.9-4248-noads.apk
echo \033[92m[Done] | %col%
timeout /t 3
cd "%output_path%"
explorer .
goto end

:strlen <Result> <String>
(
  setlocal EnableDelayedExpansion
  (set^ tmp=!%~2!)
  if defined tmp (
    set "len=1"
    for %%P in (4096 2048 1024 512 256 128 64 32 16 8 4 2 1) do (
      if "!tmp:~%%P,1!" NEQ "" ( 
        set /a "len+=%%P"
        set "tmp=!tmp:~%%P!"
      )
    )
  ) else (
    set len=0
  )
)
(
  endlocal
  set "%~1=%len%"
  exit /b
)

:nofile
<nul set /p "=\033[96mDownloading \033[94mAetherSX2... " | %col%
powershell -Command "(new-object System.Net.WebClient).DownloadFile('https://github.com/Trixarian/NetherSX2-patch/releases/download/0.0/15210-v1.5-4248.apk','15210-v1.5-4248.apk')"
echo \033[92m[Done] | %col%
goto patch

:wrongmd5
echo \033[31mError: APK found, but it's the wrong one! | %col%
pause
goto end

:end