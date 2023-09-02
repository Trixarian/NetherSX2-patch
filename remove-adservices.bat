:: Ad Services Cleanup
lib\aapt r 15210-v1.5-4248-noads.apk user-messaging-platform.properties
lib\aapt r 15210-v1.5-4248-noads.apk play-services-tasks.properties
lib\aapt r 15210-v1.5-4248-noads.apk play-services-measurement-sdk-api.properties
lib\aapt r 15210-v1.5-4248-noads.apk play-services-measurement-base.properties
lib\aapt r 15210-v1.5-4248-noads.apk play-services-basement.properties
lib\aapt r 15210-v1.5-4248-noads.apk play-services-base.properties
lib\aapt r 15210-v1.5-4248-noads.apk play-services-appset.properties
lib\aapt r 15210-v1.5-4248-noads.apk play-services-ads.properties
lib\aapt r 15210-v1.5-4248-noads.apk play-services-ads-lite.properties
lib\aapt r 15210-v1.5-4248-noads.apk play-services-ads-identifier.properties
lib\aapt r 15210-v1.5-4248-noads.apk play-services-ads-base.properties

:: Resigns the APK before exiting
java -jar lib\apksigner.jar sign --ks lib\android.jks --ks-pass pass:android 15210-v1.5-4248-noads.apk
:: Alternate Key:
:: java -jar lib\apksigner.jar sign --ks lib\public.jks --ks-pass pass:public 15210-v1.5-4248-noads.apk
pause