<p align="center">
  <img width="312" height="312" src="/.github/assets/logo_light.png#gh-dark-mode-only">
  <img width="312" height="312" src="/.github/assets/logo_dark.png#gh-light-mode-only">
</p>

# NetherSX2-patch
These are Unofficial companion scripts for NetherSX2 to expand on the amazing work already done by Anon and EZOnTheEyes

They aim to do the following:
* Remove the unnecessary ad services bloat left in the apk
* Fix the RetroAchievements Notifications
* Expose more Global settings in the App Settings to the user
* Update the GameDB, Controller Support, and the Widescreen and No-Interlace Patches
* Add additional AetherSX2/NetherSX2 spesific fixes to the GameDB
* Resign the APK to Remove the Play Protect Warning

The Script can also be used to reupdate the GameDB, Controller Support, and Widescreen and No-Interlace Patches at a later date

## Prerequisites
Windows:
* Windows Vista or higher
* [The Java(TM) SE Development Kit](https://www.oracle.com/java/technologies/downloads/#jdk21-windows)

Linux:
* The xdelta3 package
* The OpenJDK package (this name my vary depending on your Linux Distro)
* Optional: The aapt and apksigner packages (the Linux version uses it's own binaries if these packages aren't installed)
* A copy of the NetherSX2 APK

The rest comes prepackaged for your convenience

## Using these scripts
1. Run patch-apk.bat to patch your self-provided copy of the AetherSX2 4248 apk or to download a copy for you
2. Allow it to finish patching, building and signing your copy of NetherSX2
3. This will produce two copies of NetherSX2: 
   - 15210-v1.8-4248-noads.apk - Comes with the Original GameDB
   - 15210-v1.8-4248-noads[patched].apk - Comes with the updated GameDB
4. Copy your prefered apk file to your phone and install it using your File Manager

You can now rerun patch-apk.bat with the above APK to update the GameDB, Controller Support, and the Widescreen and No-Interlace Patches at a later date without needing to repatch it each time
If you prefer the Older UI Design, drop the old-ui.xdelta file in the extras folder into the main folder (the one with patch-apk.bat) to make the script revert NetherSX2 to the Older UI design

**Linux version:**

Once you have a copy of the NetherSX2 APK named 15210-v1.5-4248-noads.apk, drop it in the same folder as patch-apk.sh and run these commands:
```bash
chmod +x patch-apk.sh
# then run sh file
./patch-apk.sh
```
Credit: [TheKingFireS](https://github.com/TheKingFireS)

And there you go, you should now have an updated and bug fixed copy of NetherSX2 on your phone!

## Downloads
### Stable
* [NetherSX2-builder.zip](https://github.com/Trixarian/NetherSX2-patch/releases/download/1.8/NetherSX2-builder.zip) - Alternate way to build the NetherSX2 APK for yourself with these fixes already pre-applied. It can be used with this script to update it's contents
* [NetherSX2-patch.zip](https://github.com/Trixarian/NetherSX2-patch/releases/download/1.8/NetherSX2-patch.zip) - Copy of this script
* [nethersx2.xdelta](https://github.com/Trixarian/NetherSX2-patch/releases/download/1.8/nethersx2.xdelta) - The xdelta patch that can be applied to the AetherSX2 4248 apk with any patching program that supports the format and comes with all the changes pre-applied. This allows the creation of NetherSX2 on systems other than Windows, including Android when using the UniPatcher application
* [nethersx2-oldui.xdelta](https://github.com/Trixarian/NetherSX2-patch/releases/download/1.8/nethersx2-oldui.xdelta) - Same as the above, but only using the classic AetherSX2 buttons
### Development Builds
--Coming Soon-


NOTE: No APKs are provided due to licensing issues. You have to build it yourselves using the above methods

## Credits
* PCSX2: <https://github.com/PCSX2/pcsx2> 
* AetherSX2: <https://www.aethersx2.com/archive/> 
* EZOnTheEyes: <https://www.youtube.com/@EZOnTheEyes>
* Xdelta-GPL: <https://github.com/jmacd/xdelta-gpl>
* cmdcolor: <https://github.com/alecmev/cmdcolor>
* md5sums: http://www.pc-tools.net/win32/md5sums
* Android Keystore: <https://github.com/jorfao/pkStore>
* Alternate Keystore: <https://github.com/tytydraco/public-keystore>
* Android build-tools: <https://androidsdkmanager.azurewebsites.net/Buildtools>
