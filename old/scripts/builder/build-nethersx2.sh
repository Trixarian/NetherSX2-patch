#!/bin/bash
# ********************************* CONFIG **********************************
patch_name="NetherSX2 Builder v1.9"
patch_author=""
md5hash="c98b0e4152d3b02fbfb9f62581abada5"
xdelta_name="nethersx2.xdelta"
patched_end="-noads"
# ***************************************************************************

# Setting Base Variables
p2f="$(dirname "$(readlink -f "$0")")"
input_path="$p2f/OriginalAPK"
output_path="$p2f/PatchedAPK"
xdelta_patch="$p2f/lib/$xdelta_name"

# Preparing to Start
titlen="${#patch_name}"
autlen="${#patch_author}"
autlen=$((autlen + 3))
if [ "$titlen" -ge "$autlen" ]; then
    result="$titlen"
else
    result="$autlen"
fi
bline="=="
index=1
while [ "$index" -le "$result" ]; do
    bline="$bline="
    index=$((index + 1))
done

# Opening Banner
echo -e "\e[91m$bline\e[0m"
echo -e "\e[91m $patch_name\e[0m"
if [ "$autlen" -gt 3 ]; then
    echo -e "\e[91m by $patch_author\e[0m"
fi
echo -e "\e[91m$bline\e[0m"

# Preparing Functions
patch() {
    # Checks if the output folder exists
    if [ ! -d "$output_path" ]; then
        mkdir -p "$output_path"
    fi

    # Patching the file
    echo -ne "\e[96mPatching to \e[0m\e[91mNetherSX2...\e[0m"
    for i in "$input_path"/*.apk; do
        if command -v xdelta3 &>/dev/null; then
            xdelta3 -d -f -s "$i" "$xdelta_patch" "$output_path/$(basename "$i" .apk)$patched_end.apk"
        else
            chmod +x "$p2f/lib/xdelta3"
            "$p2f/lib/xdelta3" -d -f -s "$i" "$xdelta_patch" "$output_path/$(basename "$i" .apk)$patched_end.apk"
        fi
    done
    echo -e "\e[92m[Done]\e[0m"
    read -p "Press Enter to exit..."
    cd "$output_path"
    exit 0
}

nofile() {
    echo -ne "\e[96mDownloading \e[0m\e[94mAetherSX2...\e[0m"
    curl -sL -o "$input_path/15210-v1.9-4248.apk" "https://github.com/Trixarian/NetherSX2-patch/releases/download/0.0/15210-v1.5-4248.apk"
    echo -e "\e[92m[Done]\e[0m"
    patch
}

wrongmd5() {
    echo -e "\e[31mError: APK found, but it's the wrong one!\e[0m"
    read -p "Press Enter to exit..."
    exit 1
}

# Checks if the input folder exists
if [ ! -d "$input_path" ]; then
    mkdir -p "$input_path"
    nofile
else
    # Checks if there's an apk to patch and if the md5 hash matches
    # Otherwise it downloads it from the AetherSX2 Archive
    if [ -z "$(find "$input_path" -name "*.apk" -type f)" ]; then
        nofile
    fi
fi

for i in "$input_path"/*.apk; do
    md5_checksum=$(md5sum "$i" | awk '{print $1}')
    if [ "$md5_checksum" = "$md5hash" ]; then
        patch
    else
        wrongmd5
    fi
done
