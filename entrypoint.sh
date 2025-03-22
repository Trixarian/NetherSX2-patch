#!/bin/bash
cd /app
wget https://github.com/Trixarian/NetherSX2-patch/archive/refs/heads/main.zip
unzip *zip

cd /app/NetherSX2-patch-main
chmod +x ./patch-apk.sh
./patch-apk.sh

cp *4248*.apk* /output/
