#!/bin/bash
# alias to display [Done] in green
display_done() {
	printf "\e[1;32m[Done]\e[0m\n"
}

# alias to display text in cyan
display_cyan() {
	printf "\e[1;36m%s\e[0m" "$1"
}

# alias to display text in light red
display_light_red() {
	printf "\e[1;91m%s\e[0m" "$1"
}

# start of script
clear
printf "\e[1;91m==========================\n"
printf " NetherSX2 Patcher v1.9\n"
printf "==========================\e[0m\n"

# Check if the NetherSX2 APK exists and if it's named
if [ ! -f "15210-v1.5-4248.apk" ]; then
	apk_url='https://github.com/Trixarian/NetherSX2-patch/releases/download/0.0/15210-v1.5-4248.apk'
	if [ "$(uname -s)" = 'Darwin' ]; then
		curl --location --silent --remote-name "${apk_url}"
	else
		wget "${apk_url}"
	fi
	if [ ! $? -eq 0 ]; then
		printf "Failed to download unmodified APK!\n"
		exit 1
	fi
fi

if [ ! -f "15210-v1.5-4248-noads.apk" ]; then
	xdelta3 -d -f -s 15210-v1.5-4248.apk lib/patch.xdelta 15210-v1.5-4248-noads.apk
	if [ ! $? -eq 0 ]; then
		printf "Failed to apply nethersx2 patch to APK!\n"
		exit 1
	fi
fi

if [ "$(md5sum "15210-v1.5-4248-noads.apk" | awk '{print $1}')" = "c98b0e4152d3b02fbfb9f62581abada5" ]; then
	printf "\e[0;31mError: Incorrect APK provided! Original unpatched APK should not be renamed -noads.\n"
	printf "Please provide a copy of NetherSX2 named 15210-v1.5-4248-noads.apk!\e[0m\n"
	exit 1
fi

cp 15210-v1.5-4248-noads.apk 15210-v1.5-4248-patched.apk

if command -v "aapt" >/dev/null 2>&1; then
	# Ad Services Cleanup
	display_cyan "Removing the "
	display_light_red "Ad Services leftovers...         "
	aapt r 15210-v1.5-4248-patched.apk user-messaging-platform.properties			> /dev/null 2>&1
	aapt r 15210-v1.5-4248-patched.apk play-services-tasks.properties				> /dev/null 2>&1
	aapt r 15210-v1.5-4248-patched.apk play-services-measurement-sdk-api.properties		> /dev/null 2>&1
	aapt r 15210-v1.5-4248-patched.apk play-services-measurement-base.properties		> /dev/null 2>&1
	aapt r 15210-v1.5-4248-patched.apk play-services-basement.properties			> /dev/null 2>&1
	aapt r 15210-v1.5-4248-patched.apk play-services-base.properties				> /dev/null 2>&1
	aapt r 15210-v1.5-4248-patched.apk play-services-appset.properties			> /dev/null 2>&1
	aapt r 15210-v1.5-4248-patched.apk play-services-ads.properties				> /dev/null 2>&1
	aapt r 15210-v1.5-4248-patched.apk play-services-ads-lite.properties			> /dev/null 2>&1
	aapt r 15210-v1.5-4248-patched.apk play-services-ads-identifier.properties		> /dev/null 2>&1
	aapt r 15210-v1.5-4248-patched.apk play-services-ads-base.properties			> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	else
		printf "\e[1;32m[Already removed]\e[0m\n"
	fi

	# Updates the FAQ to show that we're using the latest version of NetherSX2
	display_cyan "Updating the "
	display_light_red "FAQ...                           "
	aapt r 15210-v1.5-4248-patched.apk assets/faq.html
	aapt a 15210-v1.5-4248-patched.apk assets/faq.html					> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	# Updates to Latest GameDB with features removed that are not supported by the libemucore.so from March 13th
	display_cyan "Updating the "
	display_light_red "GameDB...                        "
	aapt r 15210-v1.5-4248-patched.apk assets/GameIndex.yaml
	aapt a 15210-v1.5-4248-patched.apk assets/GameIndex.yaml					> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	# Updates the Game Controller Database
	display_cyan "Updating the "
	display_light_red "Controller Database...           "
	aapt r 15210-v1.5-4248-patched.apk assets/game_controller_db.txt
	aapt a 15210-v1.5-4248-patched.apk assets/game_controller_db.txt				> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	# Updates the Widescreen Patches
	display_cyan "Updating the "
	display_light_red "Widescreen Patches...            "
	aapt r 15210-v1.5-4248-patched.apk assets/cheats_ws.zip
	aapt a 15210-v1.5-4248-patched.apk assets/cheats_ws.zip					> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	# Updates the No-Interlacing Patches
	display_cyan "Updating the "
	display_light_red "No-Interlacing Patches...        "
	aapt r 15210-v1.5-4248-patched.apk assets/cheats_ni.zip
	aapt a 15210-v1.5-4248-patched.apk assets/cheats_ni.zip					> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	# Fixes License Compliancy Issue
	display_cyan "Fixing the "
	display_light_red "License Compliancy Issue...        "
	aapt r 15210-v1.5-4248-patched.apk assets/3rdparty.html
	aapt a 15210-v1.5-4248-patched.apk assets/3rdparty.html					> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	# Adds the placeholder file that makes RetroAchievements Notifications work
	display_cyan "Fixing the "
	display_light_red "RetroAchievements Notifications... "
	aapt r 15210-v1.5-4248-patched.apk assets/placeholder.png					> /dev/null 2>&1
	aapt a 15210-v1.5-4248-patched.apk assets/placeholder.png					> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi
else
	display_light_red "aapt not found in \$PATH. Continuing with bundled aapt"
	chmod +x lib/aapt
	display_cyan "Removing the "
	display_light_red "Ad Services leftovers...         "
	lib/aapt r 15210-v1.5-4248-patched.apk user-messaging-platform.properties			> /dev/null 2>&1
	lib/aapt r 15210-v1.5-4248-patched.apk play-services-tasks.properties			> /dev/null 2>&1
	lib/aapt r 15210-v1.5-4248-patched.apk play-services-measurement-sdk-api.properties	> /dev/null 2>&1
	lib/aapt r 15210-v1.5-4248-patched.apk play-services-measurement-base.properties		> /dev/null 2>&1
	lib/aapt r 15210-v1.5-4248-patched.apk play-services-basement.properties			> /dev/null 2>&1
	lib/aapt r 15210-v1.5-4248-patched.apk play-services-base.properties			> /dev/null 2>&1
	lib/aapt r 15210-v1.5-4248-patched.apk play-services-appset.properties			> /dev/null 2>&1
	lib/aapt r 15210-v1.5-4248-patched.apk play-services-ads.properties			> /dev/null 2>&1
	lib/aapt r 15210-v1.5-4248-patched.apk play-services-ads-lite.properties			> /dev/null 2>&1
	lib/aapt r 15210-v1.5-4248-patched.apk play-services-ads-identifier.properties		> /dev/null 2>&1
	lib/aapt r 15210-v1.5-4248-patched.apk play-services-ads-base.properties			> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	else
		printf "\e[1;32m[Already removed]\e[0m\n"
	fi

	display_cyan "Updating the "
	display_light_red "FAQ...                           "
	lib/aapt r 15210-v1.5-4248-patched.apk assets/faq.html
	lib/aapt a 15210-v1.5-4248-patched.apk assets/faq.html					> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	display_cyan "Updating the "
	display_light_red "GameDB...                        "
	lib/aapt r 15210-v1.5-4248-patched.apk assets/GameIndex.yaml
	lib/aapt a 15210-v1.5-4248-patched.apk assets/GameIndex.yaml				> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	display_cyan "Updating the "
	display_light_red "Controller Database...           "
	lib/aapt r 15210-v1.5-4248-patched.apk assets/game_controller_db.txt
	lib/aapt a 15210-v1.5-4248-patched.apk assets/game_controller_db.txt			> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	display_cyan "Updating the "
	display_light_red "Widescreen Patches...            "
	lib/aapt r 15210-v1.5-4248-patched.apk assets/cheats_ws.zip
	lib/aapt a 15210-v1.5-4248-patched.apk assets/cheats_ws.zip				> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	display_cyan "Updating the "
	display_light_red "No-Interlacing Patches...        "
	lib/aapt r 15210-v1.5-4248-patched.apk assets/cheats_ni.zip
	lib/aapt a 15210-v1.5-4248-patched.apk assets/cheats_ni.zip				> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	display_cyan "Fixing the "
	display_light_red "License Compliancy Issue...        "
	lib/aapt r 15210-v1.5-4248-patched.apk assets/3rdparty.html
	lib/aapt a 15210-v1.5-4248-patched.apk assets/3rdparty.html				> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	display_cyan "Fixing the "
	display_light_red "RetroAchievements Notifications... "
	lib/aapt r 15210-v1.5-4248-patched.apk assets/placeholder.png				> /dev/null 2>&1
	lib/aapt a 15210-v1.5-4248-patched.apk assets/placeholder.png				> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi
fi

# Resigns the APK before exiting
if command -v "apksigner" >/dev/null 2>&1; then
	display_cyan "Resigning the "
	display_light_red "NetherSX2 APK...                "
	apksigner sign --ks lib/android.jks --ks-pass pass:android_sign --key-pass pass:android_sign_alias 15210-v1.5-4248-patched.apk
	if [ $? -eq 0 ]; then
		display_done
	fi
else
	display_cyan "Resigning the "
	display_light_red "NetherSX2 APK...                "
	java -jar lib/apksigner.jar sign --ks lib/android.jks --ks-pass pass:android_sign --key-pass pass:android_sign_alias 15210-v1.5-4248-patched.apk
	if [ $? -eq 0 ]; then
		display_done
	fi
fi
# Alternate Key:
# if command -v "apksigner" >/dev/null 2>&1; then
# 	display_cyan "Resigning the "
# 	display_light_red "NetherSX2 APK...                "
# 	apksigner sign --ks lib/public.jks --ks-pass pass:public 15210-v1.5-4248-patched.apk
# 	if [ $? -eq 0 ]; then
# 		display_done
# 	fi
# else
# 	display_cyan "Resigning the "
# 	display_light_red "NetherSX2 APK...                "
# 	java -jar lib/apksigner.jar sign --ks lib/public.jks --ks-pass pass:public 15210-v1.5-4248-patched.apk
# 	if [ $? -eq 0 ]; then
# 		display_done
# 	fi
# fi
