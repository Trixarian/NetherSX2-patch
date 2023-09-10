# NetherSX2-patch
These are Unofficial companion scripts for NetherSX2 to expand on the amazing work already done by Anon and EZOnTheEyes

![NetherSX2-Patch in Action](http://trixarian.net/nethersx2-in-action2.jpg)

They aim to do the following:
* Remove the unnecessary ad services bloat left in the apk
* Fix the RetroAchievements Notifications
* Update the GameDB, Controller Support, and the Widescreen and No-Interlace Patches
* Add additional AetherSX2/NetherSX2 spesific fixes to the GameDB
* Resign the APK to Remove the Play Protect Warning

The Update Script can also be used to reupdate the GameDB, Controller Support, and Widescreen and No-Interlace Patches at a later date

Note: This **ONLY** works with NetherSX2. They will break AetherSX2 if used with it

## Prerequisites
Windows:
* Windows Vista or higher
* [The Java(TM) SE Development Kit](https://www.oracle.com/java/technologies/downloads/#jdk20-windows)

Linux:
* The OpenJDK package (this name my vary depending on your Linux Distro)
* Optional: The aapt and apksigner packages (the Linux version uses it's own binaries if these packages aren't installed)

All:
* A copy of the NetherSX2 APK (see below on how to build it)

The rest comes prepackaged for your convenience

## Getting a copy of the NetherSX2 APK
The best method is to use EZOnTheEyes' guide to build it yourself:

[![NetherSX2 Installation and Usage Guide](http://img.youtube.com/vi/2y3uRlYq4SY/0.jpg)](http://www.youtube.com/watch?v=2y3uRlYq4SY)

Alternatively, NetherSX2-builder and xdelta patch in the Downloads section can be used to create a copy of NetherSX2 with these changes pre-applied 

## Using these scripts
Once you have a copy of the NetherSX2 APK named 15210-v1.5-4248-noads.apk, drop it in the same folder as patch-apk.bat
1. Run patch-apk.bat to patch your NetherSX2 APK to the latest version. This will reduce the APK size by about 400KB 
2. Copy the now modified version of 15210-v1.5-4248-noads.apk back to your phone and install it using your File Manager

You can now use update-files.bat with the above APK to update the GameDB, Controller Support, and the Widescreen and No-Interlace Patches at a later date without needing to repatch it each time

**Linux version:**

Once you have a copy of the NetherSX2 APK named 15210-v1.5-4248-noads.apk, drop it in the same folder as patch-apk.sh and run these commands:
```bash
chmod +x patch-apk.sh update-files.sh
# then run sh file
./patch-apk.sh
# If your apk was already patched and you want to update it, then run it.
./update-files.sh
```
Credit: [TheKingFireS](https://github.com/TheKingFireS)

And there you go, you should now have an updated and bug fixed copy of NetherSX2 on your phone!

## Downloads
* [NetherSX2-builder.zip](https://github.com/Trixarian/NetherSX2-patch/releases/download/1.6/NetherSX2-builder.zip) - Alternate way to build the NetherSX2 APK for yourself with these fixes already pre-applied. It can be used with these scripts to update it's contents
* [NetherSX2-patch.zip](https://github.com/Trixarian/NetherSX2-patch/releases/download/1.6/NetherSX2-patch.zip) - Copy of these scripts. They're meant to be used with a NetherSX2's APK. See above on how to generate it
* [nethersx2.xdelta](https://github.com/Trixarian/NetherSX2-patch/releases/download/1.6/nethersx2.xdelta) - The xdelta patch that can be applied to the AetherSX2 4248 apk with any patching program that supports the format and comes with all the changes pre-applied. This allows the creation of NetherSX2 on systems other than Windows, including Android when using the UniPatcher application


NOTE: No APKs are provided due to licensing issues. You have to build it yourselves using the above methods

## Credits
* PCSX2: <https://github.com/PCSX2/pcsx2> 
* AetherSX2: <https://www.aethersx2.com/archive/> 
* EZOnTheEyes: <https://www.youtube.com/@EZOnTheEyes>
* cmdcolor: <https://github.com/alecmev/cmdcolor>
* Android Keystore: <https://github.com/jorfao/pkStore>
* Alternate Keystore: <https://github.com/tytydraco/public-keystore>
* Android build-tools: <https://androidsdkmanager.azurewebsites.net/Buildtools>
