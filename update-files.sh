#!/bin/bash
# alias to display terminal header
display_header() {
	printf "\e[1;91m========================\n"
	printf " NetherSX2 Patcher v1.6\n"
	printf "========================\e[0m\n"
}

# alias to display [done] in green
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
display_header

# Check if the NetherSX2 APK exists and if it's named
if [ ! -f "15210-v1.5-4248-noads.apk" ]; then
	printf "\e[0;31mError: No APK found or wrong one provided!\e[0m\n"
	printf "\e[0;31mPlease provide a copy of NetherSX2 named 15210-v1.5-4248-noads.apk!\e[0m\n"
	exit 1
fi

if command -v "aapt" >/dev/null 2>&1; then
	# Updates to Latest GameDB with features removed that are not supported by the libemucore.so from March 13th
	display_cyan "Updating the "
	display_light_red "GameDB...                 "
	aapt r 15210-v1.5-4248-noads.apk assets/GameIndex.yaml
	aapt a 15210-v1.5-4248-noads.apk assets/GameIndex.yaml					> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	# Updates the Game Controller Database
	display_cyan "Updating the "
	display_light_red "Controller Database...    "
	aapt r 15210-v1.5-4248-noads.apk assets/game_controller_db.txt
	aapt a 15210-v1.5-4248-noads.apk assets/game_controller_db.txt				> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	# Updates the Widescreen Patches
	display_cyan "Updating the "
	display_light_red "Widescreen Patches...     "
	aapt r 15210-v1.5-4248-noads.apk assets/cheats_ws.zip
	aapt a 15210-v1.5-4248-noads.apk assets/cheats_ws.zip					> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	# Updates the No-Interlacing Patches
	display_cyan "Updating the "
	display_light_red "No-Interlacing Patches... "
	aapt r 15210-v1.5-4248-noads.apk assets/cheats_ni.zip
	aapt a 15210-v1.5-4248-noads.apk assets/cheats_ni.zip					> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi
else
	chmod +x lib/aapt
	display_cyan "Updating the "
	display_light_red "GameDB...                 "
	lib/aapt r 15210-v1.5-4248-noads.apk assets/GameIndex.yaml
	lib/aapt a 15210-v1.5-4248-noads.apk assets/GameIndex.yaml				> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	display_cyan "Updating the "
	display_light_red "Controller Database...    "
	lib/aapt r 15210-v1.5-4248-noads.apk assets/game_controller_db.txt
	lib/aapt a 15210-v1.5-4248-noads.apk assets/game_controller_db.txt			> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	display_cyan "Updating the "
	display_light_red "Widescreen Patches...     "
	lib/aapt r 15210-v1.5-4248-noads.apk assets/cheats_ws.zip
	lib/aapt a 15210-v1.5-4248-noads.apk assets/cheats_ws.zip				> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi

	display_cyan "Updating the "
	display_light_red "No-Interlacing Patches... "
	lib/aapt r 15210-v1.5-4248-noads.apk assets/cheats_ni.zip
	lib/aapt a 15210-v1.5-4248-noads.apk assets/cheats_ni.zip				> /dev/null 2>&1
	if [ $? -eq 0 ]; then
		display_done
	fi
fi

# Resigns the APK before exiting
if command -v "apksigner" >/dev/null 2>&1; then
	display_cyan "Resigning the "
	display_light_red "NetherSX2 APK...         "
	apksigner sign --ks lib/android.jks --ks-pass pass:android 15210-v1.5-4248-noads.apk
	if [ $? -eq 0 ]; then
		display_done
	fi
else
	display_cyan "Resigning the "
	display_light_red "NetherSX2 APK...         "
	java -jar lib/apksigner.jar sign --ks lib/android.jks --ks-pass pass:android 15210-v1.5-4248-noads.apk
	if [ $? -eq 0 ]; then
		display_done
	fi
fi
# Alternate Key:
# if command -v "apksigner" >/dev/null 2>&1; then
# 	display_cyan "Resigning the "
# 	display_light_red "NetherSX2 APK...         "
# 	apksigner sign --ks lib/public.jks --ks-pass pass:public 15210-v1.5-4248-noads.apk
# 	if [ $? -eq 0 ]; then
# 		display_done
# 	fi
# else
# 	display_cyan "Resigning the "
# 	display_light_red "NetherSX2 APK...         "
# 	java -jar lib/apksigner.jar sign --ks lib/public.jks --ks-pass pass:public 15210-v1.5-4248-noads.apk
# 	if [ $? -eq 0 ]; then
# 		display_done
# 	fi
# fi
