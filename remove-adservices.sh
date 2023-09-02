#!/bin/bash
# Ad Services Cleanup
if command -v "aapt" >/dev/null 2>&1; then
	aapt r 15210-v1.5-4248-noads.apk user-messaging-platform.properties
	aapt r 15210-v1.5-4248-noads.apk play-services-tasks.properties
	aapt r 15210-v1.5-4248-noads.apk play-services-measurement-sdk-api.properties
	aapt r 15210-v1.5-4248-noads.apk play-services-measurement-base.properties
	aapt r 15210-v1.5-4248-noads.apk play-services-basement.properties
	aapt r 15210-v1.5-4248-noads.apk play-services-base.properties
	aapt r 15210-v1.5-4248-noads.apk play-services-appset.properties
	aapt r 15210-v1.5-4248-noads.apk play-services-ads.properties
	aapt r 15210-v1.5-4248-noads.apk play-services-ads-lite.properties
	aapt r 15210-v1.5-4248-noads.apk play-services-ads-identifier.properties
	aapt r 15210-v1.5-4248-noads.apk play-services-ads-base.properties
else
	chmod +x lib/aaptlinux
	lib/aaptlinux r 15210-v1.5-4248-noads.apk user-messaging-platform.properties
	lib/aaptlinux r 15210-v1.5-4248-noads.apk play-services-tasks.properties
	lib/aaptlinux r 15210-v1.5-4248-noads.apk play-services-measurement-sdk-api.properties
	lib/aaptlinux r 15210-v1.5-4248-noads.apk play-services-measurement-base.properties
	lib/aaptlinux r 15210-v1.5-4248-noads.apk play-services-basement.properties
	lib/aaptlinux r 15210-v1.5-4248-noads.apk play-services-base.properties
	lib/aaptlinux r 15210-v1.5-4248-noads.apk play-services-appset.properties
	lib/aaptlinux r 15210-v1.5-4248-noads.apk play-services-ads.properties
	lib/aaptlinux r 15210-v1.5-4248-noads.apk play-services-ads-lite.properties
	lib/aaptlinux r 15210-v1.5-4248-noads.apk play-services-ads-identifier.properties
	lib/aaptlinux r 15210-v1.5-4248-noads.apk play-services-ads-base.properties
fi

# Resigns the APK before exiting
if command -v "apksigner" >/dev/null 2>&1; then
	apksigner sign --ks lib/android.jks --ks-pass pass:android 15210-v1.5-4248-noads.apk
else
	exec java -jar lib/lib/apksigner.jar sign --ks lib/android.jks --ks-pass pass:android 15210-v1.5-4248-noads.apk
fi
# Alternate Key:
# if command -v "apksigner" >/dev/null 2>&1; then
# 	apksigner sign --ks lib/public.jks --ks-pass pass:public 15210-v1.5-4248-noads.apk
# else
# 	exec java -jar lib/lib/apksigner.jar sign --ks lib/public.jks --ks-pass pass:public 15210-v1.5-4248-noads.apk
# fi
