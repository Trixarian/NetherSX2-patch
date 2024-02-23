:: --Manifest Cleanup--
lib\xml ed -L -d "manifest/uses-permission[@android:name='android.permission.ACCESS_NETWORK_STATE' or @android:name='com.google.android.gms.permission.AD_ID' or @android:name='android.permission.WAKE_LOCK' or @android:name='android.permission.FOREGROUND_SERVICE']" "4248\AndroidManifest.xml"
lib\xml ed -L -d "manifest/queries" "4248\AndroidManifest.xml"
lib\xml ed -L -d "manifest/application/service" "4248\AndroidManifest.xml"
lib\xml ed -L -d "manifest/application/receiver" "4248\AndroidManifest.xml"
lib\xml ed -L -d "manifest/application/meta-data[@android:name='com.google.android.gms.ads.APPLICATION_ID' or @android:name='com.google.android.gms.version']" "4248\AndroidManifest.xml"
lib\xml ed -L -d "manifest/application/provider/meta-data[@android:name='androidx.work.WorkManagerInitializer']" "4248\AndroidManifest.xml"
lib\xml ed -L -d "manifest/application/activity[@android:name='com.google.android.gms.ads.AdActivity' or @android:name='com.google.android.gms.version' or @android:name='com.google.android.gms.common.api.GoogleApiActivity' or @android:name='com.google.android.gms.ads.OutOfContextTestingActivity']" "4248\AndroidManifest.xml"
lib\xml ed -L -d "manifest/application/provider[@android:name='com.google.android.gms.ads.MobileAdsInitProvider']" "4248\AndroidManifest.xml"
lib\xml ed -L -d "manifest/application/activity/@android:preferMinimalPostProcessing" "4248\AndroidManifest.xml"
lib\xml ed -L -d "manifest/application/@android:extractNativeLibs" "4248\AndroidManifest.xml"

lib\xml ed -L -u "manifest/application/@android:label" -v "NetherSX2" "4248\AndroidManifest.xml"
lib\xml ed -L -u "manifest/application/activity[@android:label='AetherSX2']/@android:label" -v "NetherSX2" "4248\AndroidManifest.xml"
:: --End Manifest Cleanup--

:: --Main Activity Layout Cleanup--
lib\xml ed -L -d "androidx.drawerlayout.widget.DrawerLayout/androidx.coordinatorlayout.widget.CoordinatorLayout/RelativeLayout/FrameLayout/@android:layout_above" "4248\res\layout\activity_main.xml"
lib\xml ed -L -a "androidx.drawerlayout.widget.DrawerLayout/androidx.coordinatorlayout.widget.CoordinatorLayout/RelativeLayout/FrameLayout" -t attr -n "android:layout_alignParentBottom" -v "true" "4248\res\layout\activity_main.xml"
lib\xml ed -L -d "androidx.drawerlayout.widget.DrawerLayout/androidx.coordinatorlayout.widget.CoordinatorLayout/RelativeLayout/com.google.android.gms.ads.AdView" "4248\res\layout\activity_main.xml"
lib\xml ed -L -u "androidx.drawerlayout.widget.DrawerLayout/androidx.coordinatorlayout.widget.CoordinatorLayout/com.google.android.material.floatingactionbutton.FloatingActionButton/@android:layout_marginBottom" -v "16.0dip" "4248\res\layout\activity_main.xml"
:: --End Main Activity Layout Cleanup--

:: --Patch Native Library--
:: Patch signature checks
lib\hexalter 4248\lib\arm64-v8a\libemucore.so 0x838560=0x66,0x00,0x00,0x14 0x83B324=0x62,0x00,0x00,0x14
:: Patch BIOS type check
lib\hexalter 4248\lib\arm64-v8a\libemucore.so 0x829248=0x35,0x00,0x80,0x52

:: --Patch DEX--
:: Disable ads
lib\hexalter 4248\classes.dex 0x222264=0x0e,0x00 0x3C5B70=0x0e,0x00
:: Restore Launcher support
lib\hexalter 4248\classes.dex 0x3BDAA4=0x12,0x11 0x3BDAAA=0x04 0x3BDAAD=0x05 0x3BDAB2=0x15
lib\hexalter 4248\classes.dex 0x3BDAA6=0x6e,0x10,0x93,0x02,0x02,0x00,0x0c,0x03,0x71,0x20,0xb3,0x90,0x13,0x00
lib\hexalter 4248\classes.dex 0x3BDAB4=0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
:: Fix checksum
lib\hexalter 4248\classes.dex 0x8=0xdd,0xa2,0x21,0x3a
:: --End Patch Native Library--