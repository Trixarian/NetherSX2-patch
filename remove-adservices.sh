#!/bin/bash
# Ad Services Cleanup
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

# Resigns the APK before exiting
apksigner sign --ks lib/android.jks --ks-pass pass:android 15210-v1.5-4248-noads.apk
# Alternate Key:
# apksigner sign --ks lib/public.jks --ks-pass pass:public 15210-v1.5-4248-noads.apk
