# NetherSX2-patch
These are Unofficial companion scripts for NetherSX2 to expand on the amazing work already done by Anon and EZOnTheEyes

They aim to do the following:
* Remove the unnecessary ad services bloat left in the apk
* Fix the RetroAchievements Notifications
* Update the GameDB (which auto-magically applies game fixes), Controller Support, and the Widescreen and No-Interlace Patches
* Resign the APK using the original keystore used by AetherSX2 to remove the Play Protect Warning

The Update Script can also be used to reupdate the GameDB, Controller Support, and Widescreen and No-Interlace Patches at a later date

Note: This **ONLY** works with NetherSX2. They will break AetherSX2 if used with it

## Prerequisites
You only need: 
* Windows Vista or higher
* [The Java(TM) SE Development Kit](https://www.oracle.com/java/technologies/downloads/#jdk20-windows)
* A copy of the NetherSX2 APK (see below on how to build it yourself)

The rest comes prepackaged for your convience

## Getting a copy of the NetherSX2 APK
The best method is to use EZOnTheEyes' guide to build it yourself: <https://youtu.be/2y3uRlYq4SY>

## Using these scripts
Once you have a copy of the NetherSX2 APK named 15210-v1.5-4248-noads.apk, drop it in the same folder as remove-adservices.bat and update-files.bat
1. Run remove-adservices.bat to remove the Google Ad Services left in the APK - this will reduce the APK size by about 400KB 
2. Run update-files.bat to apply the bug fixes and update the GameDB, Controller Support and Patches
3. Copy the now modified version of 15210-v1.5-4248-noads.apk back to your phone and install it using your File Manager

And there you go, you should now have an updated and bug fixed copy of NetherSX2 on your phone!

## Downloads
* [NetherSX2-builder.zip](https://github.com/Trixarian/NetherSX2-patch/releases/download/1.2/NetherSX2-patch.zip) - Alternate way to build the NetherSX2 APK for yourself with these fixes already pre-applied. It can be used with these scripts to update it's contents
* [NetherSX2-patch.zip](https://github.com/Trixarian/NetherSX2-patch/releases/download/1.2/NetherSX2-patch.zip) - Copy of these scripts. They're meant to be used with a copy of NetherSX2's APK. See Above on how to generate it
* [nethersx2.xdelta](https://github.com/Trixarian/NetherSX2-patch/releases/download/1.2/nethersx2.xdelta) - The xdelta patch that can be applied to the AetherSX2 4248 apk with any patching program that supports the format and comes with all the changes pre-applied. This allows the creation of NetherSX2 on systems other than Windows, including Android when using the UniPatcher application

NOTE: No APKs are provided due to licensing issues. You have to build them yourselves using the above methods

## Credits
* PCSX2: <https://github.com/PCSX2/pcsx2> 
* AetherSX2: <https://www.aethersx2.com/archive/> 
* EZOnTheEyes: <https://www.youtube.com/@EZOnTheEyes>
* Android Keystore: <https://github.com/jorfao/pkStore>
* Alternate Keystore: <https://github.com/tytydraco/public-keystore>
* Android build-tools: <https://androidsdkmanager.azurewebsites.net/Buildtools>
