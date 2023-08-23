:: Ad Services Cleanup
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk user-messaging-platform.properties
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk play-services-tasks.properties
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk play-services-measurement-sdk-api.properties
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk play-services-measurement-base.properties
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk play-services-basement.properties
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk play-services-base.properties
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk play-services-appset.properties
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk play-services-ads.properties
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk play-services-ads-lite.properties
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk play-services-ads-identifier.properties
"%~dp0lib\aapt" r 15210-v1.5-4248-noads.apk play-services-ads-base.properties

:: Resigns the APK before exiting
"%~dp0lib\apksigner" sign --ks "%~dp0lib\android.jks" --ks-pass pass:android 15210-v1.5-4248-noads.apk
:: Alternate Key:
:: "%~dp0lib\apksigner" sign --ks "%~dp0lib\public.jks" --ks-pass pass:public 15210-v1.5-4248-noads.apk
pause