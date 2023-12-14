java -jar lib\apktool.jar b --use-aapt2 -o "1.apk" "NetherSX2"
lib\zipalign -f -v 4 "1.apk" "15210-v1.5-4248-noads-signed.apk"
del 1.apk
java -jar lib\apksigner.jar sign --ks lib\android.jks --ks-pass pass:android 15210-v1.5-4248-noads-signed.apk
del *.idsig
pause