#!/usr/bin/env python3
"""Add a RetroAchievements host-override broadcast receiver to a NetherSX2/AetherSX2 APK.

This lets an external helper app (e.g. RAOfflineProxy) redirect the emulator's
RetroAchievements traffic to a local proxy by broadcasting an intent, without
needing file access to the emulator's private data directory.

Contract (mirrors the RAOfflineProxy sender):
  action  <pkg>.action.SET_RETROACHIEVEMENTS_HOST_OVERRIDE   extra "host" = base URL
  action  <pkg>.action.CLEAR_RETROACHIEVEMENTS_HOST_OVERRIDE

The override is written to RetroAchievements.ini (HostUrl) and the
Achievements/Host preference. This build's NativeLibraryLoader reads HostUrl
at process startup and binary-patches the RetroAchievements host into
libemucore.so before it is loaded (see fix_native_library_loader_default
below for why an empty HostUrl must NOT fall back to the local proxy). The
host is therefore bound once per process; SET/CLEAR take effect the next
time the app is fully restarted (not just the next game boot within the same
process), since libemucore.so is only loaded once per process lifetime.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

PKG = "xyz.aethersx2.android"
PKG_PATH = PKG.replace(".", "/")
RECEIVER_CLASS = f"{PKG}.RetroAchievementsHostOverrideReceiver"
RECEIVER_SMALI_PATH = f"{PKG_PATH}/RetroAchievementsHostOverrideReceiver.smali"
PENDING_RESTART_PREF_KEY = "RAHostOverridePendingRestart"

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BUNDLED_LIB_DIR = REPO_ROOT / "decomp/lib"

RECEIVER_MANIFEST_BLOCK = (
    f'        <receiver android:name="{RECEIVER_CLASS}" android:exported="true">\n'
    f'            <intent-filter>\n'
    f'                <action android:name="{PKG}.action.SET_RETROACHIEVEMENTS_HOST_OVERRIDE"/>\n'
    f'                <action android:name="{PKG}.action.CLEAR_RETROACHIEVEMENTS_HOST_OVERRIDE"/>\n'
    f'            </intent-filter>\n'
    f'        </receiver>\n'
)

RECEIVER_SMALI = f""".class public L{PKG_PATH}/RetroAchievementsHostOverrideReceiver;
.super Landroid/content/BroadcastReceiver;
.source "RetroAchievementsHostOverrideReceiver.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    invoke-direct {{p0}}, Landroid/content/BroadcastReceiver;-><init>()V

    return-void
.end method


# virtual methods
.method public onReceive(Landroid/content/Context;Landroid/content/Intent;)V
    .locals 5

    if-eqz p1, :ret

    if-eqz p2, :ret

    invoke-virtual {{p2}}, Landroid/content/Intent;->getAction()Ljava/lang/String;

    move-result-object v0

    if-eqz v0, :ret

    const-string v3, "RAHostOverride"

    invoke-static {{v3, v0}}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    const-string v1, "SET_RETROACHIEVEMENTS_HOST_OVERRIDE"

    invoke-virtual {{v0, v1}}, Ljava/lang/String;->endsWith(Ljava/lang/String;)Z

    move-result v2

    if-eqz v2, :cond_clear

    const-string v1, "host"

    invoke-virtual {{p2, v1}}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-static {{p1, v1}}, L{PKG_PATH}/RetroAchievementsIni;->setHostOverride(Landroid/content/Context;Ljava/lang/String;)V

    goto :ret

    :cond_clear
    const-string v1, "CLEAR_RETROACHIEVEMENTS_HOST_OVERRIDE"

    invoke-virtual {{v0, v1}}, Ljava/lang/String;->endsWith(Ljava/lang/String;)Z

    move-result v2

    if-eqz v2, :ret

    const/4 v1, 0x0

    invoke-static {{p1, v1}}, L{PKG_PATH}/RetroAchievementsIni;->setHostOverride(Landroid/content/Context;Ljava/lang/String;)V

    :ret
    return-void
.end method
"""

# The host is bound once per process by NativeLibraryLoader at native-load
# time (see fix_native_library_loader_default), not read live, so a config
# write alone only takes effect on the NEXT process start. Behaviour is
# chosen by current state, per explicit requirements:
#
#  1. No game active, app currently foreground (sitting on the game list) ->
#     visible relaunch RIGHT NOW (restartApp: startActivity then kill). Safe
#     because the app is already what's on screen — cannot steal focus.
#  2. No game active, backgrounded (NativeLibraryLoader.isLoaded() true —
#     process alive — but NativeLibrary.getContext() null, since onStop()
#     clears mMainActivity on every backgrounding, not just final teardown)
#     -> silent kill right now (Process.killProcess, no startActivity).
#     Confirmed on-device that calling startActivity() from the receiver
#     while genuinely backgrounded still succeeds and steals focus, so a
#     visible relaunch is never attempted in this state.
#  3. Game active -> never touch the process now. Record a pending-restart
#     flag; MainActivity.onStart() (fires when the game is quit and control
#     returns to the already-alive MainActivity below it) applies it as a
#     silent kill too, matching case 2 — not a visible relaunch.
SET_HOST_OVERRIDE_METHOD = f""".method private static setPendingRestart(Landroid/content/Context;)V
    .locals 3

    invoke-static {{p0}}, Landroidx/preference/PreferenceManager;->getDefaultSharedPreferences(Landroid/content/Context;)Landroid/content/SharedPreferences;

    move-result-object v0

    invoke-interface {{v0}}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    const-string v1, "{PENDING_RESTART_PREF_KEY}"

    const/4 v2, 0x1

    invoke-interface {{v0, v1, v2}}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    invoke-interface {{v0}}, Landroid/content/SharedPreferences$Editor;->commit()Z

    return-void
.end method

.method private static restartApp(Landroid/content/Context;)V
    .locals 3

    :try_start_r
    invoke-virtual {{p0}}, Landroid/content/Context;->getPackageManager()Landroid/content/pm/PackageManager;

    move-result-object v0

    invoke-virtual {{p0}}, Landroid/content/Context;->getPackageName()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {{v0, v1}}, Landroid/content/pm/PackageManager;->getLaunchIntentForPackage(Ljava/lang/String;)Landroid/content/Intent;

    move-result-object v0

    const-string v2, "RAHostOverride"

    if-nez v0, :have_intent

    const-string v1, "restartApp: getLaunchIntentForPackage returned null"

    invoke-static {{v2, v1}}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    goto :no_intent

    :have_intent
    const v1, 0x10008000

    invoke-virtual {{v0, v1}}, Landroid/content/Intent;->addFlags(I)Landroid/content/Intent;

    const-string v1, "restartApp: calling startActivity"

    invoke-static {{v2, v1}}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    invoke-virtual {{p0, v0}}, Landroid/content/Context;->startActivity(Landroid/content/Intent;)V

    invoke-static {{}}, Landroid/os/Process;->myPid()I

    move-result v1

    invoke-static {{v1}}, Landroid/os/Process;->killProcess(I)V

    :no_intent
    :try_end_r
    .catch Ljava/lang/Throwable; {{:try_start_r .. :try_end_r}} :catch_r

    return-void

    :catch_r
    move-exception v0

    const-string v1, "RAHostOverride"

    invoke-static {{v1, v0}}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/Throwable;)I

    return-void
.end method

# Called from MainActivity.onStart() (see inject_main_activity_restart_hook),
# which fires when a game is quit and control returns to the already-alive
# MainActivity below it (EmulationActivity finishing). Consumes a
# pending-restart flag left by setHostOverride while a game was active, and
# applies it as a silent kill — matching the backgrounded-CLEAR behaviour,
# not a visible relaunch (this path never calls restartApp(), so there is no
# double-restart risk: nothing here ever spawns a new process to loop on).
.method public static maybeApplyPendingHostRestart(Landroid/content/Context;)V
    .locals 3

    :try_start_p
    invoke-static {{p0}}, Landroidx/preference/PreferenceManager;->getDefaultSharedPreferences(Landroid/content/Context;)Landroid/content/SharedPreferences;

    move-result-object v0

    const-string v1, "{PENDING_RESTART_PREF_KEY}"

    const/4 v2, 0x0

    invoke-interface {{v0, v1, v2}}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z

    move-result v2

    if-eqz v2, :ret_p

    invoke-static {{}}, L{PKG_PATH}/NativeLibrary;->getEmulationActivity()L{PKG_PATH}/EmulationActivity;

    move-result-object v2

    if-nez v2, :ret_p

    invoke-interface {{v0}}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    const/4 v2, 0x0

    invoke-interface {{v0, v1, v2}}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    invoke-interface {{v0}}, Landroid/content/SharedPreferences$Editor;->commit()Z

    invoke-static {{}}, Landroid/os/Process;->myPid()I

    move-result v0

    invoke-static {{v0}}, Landroid/os/Process;->killProcess(I)V
    :try_end_p
    .catch Ljava/lang/Throwable; {{:try_start_p .. :try_end_p}} :catch_p

    :ret_p
    return-void

    :catch_p
    move-exception v0

    return-void
.end method

.method public static setHostOverride(Landroid/content/Context;Ljava/lang/String;)V
    .locals 4

    if-nez p1, :cond_trim

    const-string p1, ""

    goto :normalized

    :cond_trim
    invoke-virtual {{p1}}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object p1

    :normalized
    invoke-static {{p0}}, Landroidx/preference/PreferenceManager;->getDefaultSharedPreferences(Landroid/content/Context;)Landroid/content/SharedPreferences;

    move-result-object v0

    invoke-interface {{v0}}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    const-string v1, "Achievements/Host"

    invoke-interface {{v0, v1, p1}}, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    invoke-interface {{v0}}, Landroid/content/SharedPreferences$Editor;->apply()V

    invoke-static {{p0}}, L{PKG_PATH}/RetroAchievementsIni;->getIniFile(Landroid/content/Context;)Ljava/io/File;

    move-result-object v0

    if-eqz v0, :after_ini

    invoke-static {{v0}}, L{PKG_PATH}/RetroAchievementsIni;->ensureTemplate(Ljava/io/File;)V

    new-instance v1, Lq3/a2;

    invoke-virtual {{v0}}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0

    invoke-direct {{v1, v0}}, Lq3/a2;-><init>(Ljava/lang/String;)V

    const-string v0, "RetroAchievements/HostUrl"

    invoke-virtual {{v1, v0, p1}}, Lq3/a2;->i(Ljava/lang/String;Ljava/lang/String;)V

    :after_ini
    :try_start_a
    invoke-static {{}}, L{PKG_PATH}/NativeLibrary;->getEmulationActivity()L{PKG_PATH}/EmulationActivity;

    move-result-object v1

    const-string v2, "RAHostOverride"

    if-eqz v1, :no_game_active

    const-string v1, "setHostOverride: game active, deferring until quit"

    invoke-static {{v2, v1}}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    invoke-static {{p0}}, L{PKG_PATH}/RetroAchievementsIni;->setPendingRestart(Landroid/content/Context;)V

    goto :ret

    :no_game_active
    invoke-static {{}}, L{PKG_PATH}/NativeLibraryLoader;->isLoaded()Z

    move-result v1

    if-nez v1, :cond_process_alive

    const-string v1, "setHostOverride: native lib never loaded in this process, nothing to restart"

    invoke-static {{v2, v1}}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    goto :ret

    :cond_process_alive
    invoke-static {{}}, L{PKG_PATH}/NativeLibrary;->getContext()Landroid/content/Context;

    move-result-object v1

    if-eqz v1, :cond_backgrounded

    const-string v1, "setHostOverride: foreground, no game -> restartApp (visible relaunch)"

    invoke-static {{v2, v1}}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    invoke-static {{p0}}, L{PKG_PATH}/RetroAchievementsIni;->restartApp(Landroid/content/Context;)V

    goto :ret

    :cond_backgrounded
    const-string v1, "setHostOverride: backgrounded, no game -> killing process silently"

    invoke-static {{v2, v1}}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    invoke-static {{}}, Landroid/os/Process;->myPid()I

    move-result v1

    invoke-static {{v1}}, Landroid/os/Process;->killProcess(I)V
    :try_end_a
    .catch Ljava/lang/Throwable; {{:try_start_a .. :try_end_a}} :catch_a

    goto :ret

    :catch_a
    move-exception v1

    const-string v2, "RAHostOverride"

    invoke-static {{v2, v1}}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/Throwable;)I

    :ret
    return-void
.end method
"""


def patch_manifest(manifest: Path) -> None:
    text = manifest.read_text(encoding="utf-8")
    if RECEIVER_CLASS in text:
        print("manifest receiver already present")
        return
    if "</application>" not in text:
        raise SystemExit("Could not find </application> in AndroidManifest.xml")
    text = text.replace("</application>", RECEIVER_MANIFEST_BLOCK + "    </application>", 1)
    manifest.write_text(text, encoding="utf-8")


def find_smali_root(decoded: Path) -> Path:
    for candidate in sorted(decoded.glob("smali*")):
        if (candidate / f"{PKG_PATH}/RetroAchievementsIni.smali").exists():
            return candidate
    raise SystemExit(
        f"Could not find smali root containing {PKG_PATH}/RetroAchievementsIni.smali"
    )


def write_receiver_smali(smali_root: Path) -> None:
    path = smali_root / RECEIVER_SMALI_PATH
    if path.exists():
        print("receiver smali already present")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(RECEIVER_SMALI, encoding="utf-8")


def inject_set_host_override(smali_root: Path) -> None:
    path = smali_root / f"{PKG_PATH}/RetroAchievementsIni.smali"
    if not path.exists():
        raise SystemExit(f"RetroAchievementsIni.smali not found at {path}")

    text = path.read_text(encoding="utf-8")
    if "setHostOverride(" in text:
        print("setHostOverride already injected")
        return

    marker = "# direct methods\n"
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit("Could not find '# direct methods' in RetroAchievementsIni.smali")
    insert_at = idx + len(marker)
    text = text[:insert_at] + SET_HOST_OVERRIDE_METHOD + "\n" + text[insert_at:]
    path.write_text(text, encoding="utf-8")


def inject_main_activity_restart_hook(smali_root: Path) -> None:
    # MainActivity.onStart() fires on every genuinely-foreground transition
    # (cold launch, returning from background, AND quitting a game back to
    # the list — EmulationActivity finishing hands control back to the
    # already-alive MainActivity underneath, which was stopped, not
    # destroyed, while the game was showing) but is NEVER called while only
    # EmulationActivity itself is being resumed mid-game, so this is a safe,
    # naturally-gated place to apply a pending host-restart request.
    path = smali_root / f"{PKG_PATH}/MainActivity.smali"
    if not path.exists():
        raise SystemExit(f"MainActivity.smali not found at {path}")

    text = path.read_text(encoding="utf-8")
    if "maybeApplyPendingHostRestart(" in text:
        print("MainActivity restart hook already injected")
        return

    marker = (
        f"    invoke-static {{p0}}, L{PKG_PATH}/NativeLibrary;"
        "->setMainActivity(L" + f"{PKG_PATH}/MainActivity;)V\n"
    )
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit("Could not find NativeLibrary.setMainActivity() call in MainActivity.onStart()")
    insert_at = idx + len(marker)
    call = (
        f"\n    invoke-static {{p0}}, L{PKG_PATH}/RetroAchievementsIni;"
        "->maybeApplyPendingHostRestart(Landroid/content/Context;)V\n"
    )
    text = text[:insert_at] + call + text[insert_at:]
    path.write_text(text, encoding="utf-8")
    print("injected MainActivity.onStart() pending-restart hook")


def fix_native_library_loader_default(smali_root: Path) -> None:
    # NativeLibraryLoader.load() reads RetroAchievements.ini's HostUrl (or the
    # Achievements/Host preference) at process startup, binary-patches that host
    # into libemucore.so, and loads the patched copy — the RA host is bound once
    # per process and is NOT re-read later, so this only matters at app start.
    #
    # normalizeHost()'s existing default for an EMPTY host is
    # "http://127.0.0.1:8080" (a local proxy), not the real RetroAchievements
    # server. So clearing HostUrl does not restore the real server — it makes
    # every subsequent process start bind to a local proxy by default. Fix:
    # empty host must normalize to "" (no override), and prepareLoadPath must
    # treat an empty host as "load the stock libemucore.so unpatched" instead of
    # writing an empty host into the API endpoint string.
    path = smali_root / f"{PKG_PATH}/NativeLibraryLoader.smali"
    if not path.exists():
        print("NativeLibraryLoader.smali not present, skipping native host-default fix")
        return

    text = path.read_text(encoding="utf-8")
    if 'const-string v0, "http://127.0.0.1:8080"' not in text:
        print("NativeLibraryLoader proxy-default string not found, skipping native host-default fix")
        return

    text = text.replace(
        'const-string v0, "http://127.0.0.1:8080"',
        'const-string v0, ""',
        1,
    )

    marker = (
        "    invoke-static {v0, p1}, "
        f"L{PKG_PATH}/NativeLibraryLoader;->patchBytes([BLjava/lang/String;)Z\n"
    )
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit("Could not find patchBytes call in NativeLibraryLoader.prepareLoadPath")
    guard = (
        "    invoke-static {p1}, Landroid/text/TextUtils;->isEmpty(Ljava/lang/CharSequence;)Z\n\n"
        "    move-result v9\n\n"
        "    if-nez v9, :cond_0\n\n"
    )
    text = text[:idx] + guard + text[idx:]

    # Expose sLoaded (private, set once and never reset for the process's
    # lifetime) so setHostOverride can tell "process genuinely never loaded
    # the native lib" (nothing to restart, config alone is enough — the next
    # true cold start reads it fresh) apart from "app merely backgrounded
    # right now" (mMainActivity is cleared on every onStop(), NOT just final
    # teardown, so NativeLibrary.getContext()==null is unreliable for this —
    # confirmed: it returned null while the process was still alive, just
    # backgrounded, causing the pending-restart flag to never get set).
    if "public static isLoaded()Z" not in text:
        getter = (
            ".method public static isLoaded()Z\n"
            "    .locals 1\n\n"
            "    sget-boolean v0, "
            f"L{PKG_PATH}/NativeLibraryLoader;->sLoaded:Z\n\n"
            "    return v0\n"
            ".end method\n\n\n"
        )
        marker2 = "# direct methods\n"
        idx2 = text.find(marker2)
        if idx2 < 0:
            raise SystemExit("Could not find '# direct methods' in NativeLibraryLoader.smali")
        insert_at2 = idx2 + len(marker2)
        text = text[:insert_at2] + getter + text[insert_at2:]

    path.write_text(text, encoding="utf-8")
    print("fixed NativeLibraryLoader empty-host default (was local-proxy fallback)")
    print("added NativeLibraryLoader.isLoaded() accessor")


_METHOD_RE = re.compile(r"^\.method\s+(.*?)\s*(\S+\(.*?\).+?)\s*$")
_VIRTUAL_SKIP_FLAGS = {"static", "private", "constructor"}


def _scan_class(path: Path):
    cls = None
    sup = None
    methods = {}
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if cls is None and line.startswith(".class"):
            cls = line.split()[-1]
        elif sup is None and line.startswith(".super"):
            sup = line.split()[-1]
        elif line.startswith(".method"):
            m = _METHOD_RE.match(line)
            if not m:
                continue
            flags = set(m.group(1).split())
            sig = m.group(2)
            if sig.startswith("<"):
                continue
            methods[sig] = (flags, idx)
    return cls, sup, methods


def strip_conflicting_final(smali_roots) -> None:
    # apktool's dex recompile trips ART verification on R8-emitted invalid
    # overrides (a subclass overriding a method its ancestor declares `final`).
    # The original APK tolerates it via a matching AOT profile; the rebuilt dex
    # does not. Relax the ancestor's `final` so the override verifies. Removing
    # `final` from a method never changes runtime behaviour.
    by_class = {}
    for root in smali_roots:
        for path in root.rglob("*.smali"):
            cls, sup, methods = _scan_class(path)
            if cls is not None:
                by_class[cls] = (path, sup, methods)

    def is_virtual(flags):
        return not (_VIRTUAL_SKIP_FLAGS & flags)

    to_strip = {}  # class -> set(line_idx)
    for cls, (_, sup, methods) in by_class.items():
        for sig, (flags, _) in methods.items():
            if not is_virtual(flags):
                continue
            ancestor = sup
            seen = set()
            while ancestor in by_class and ancestor not in seen:
                seen.add(ancestor)
                a_path, a_sup, a_methods = by_class[ancestor]
                a_entry = a_methods.get(sig)
                if a_entry is not None:
                    a_flags, a_idx = a_entry
                    if is_virtual(a_flags) and "final" in a_flags:
                        to_strip.setdefault(ancestor, set()).add(a_idx)
                    break
                ancestor = a_sup

    for cls, line_idxs in to_strip.items():
        path = by_class[cls][0]
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        for idx in line_idxs:
            lines[idx] = lines[idx].replace(" final ", " ", 1)
        path.write_text("".join(lines), encoding="utf-8")

    if to_strip:
        total = sum(len(v) for v in to_strip.values())
        print(f"relaxed {total} illegal final override(s) across {len(to_strip)} class(es)")


def patch_decoded_dir(decoded_dir: Path) -> None:
    patch_manifest(decoded_dir / "AndroidManifest.xml")
    smali_root = find_smali_root(decoded_dir)
    inject_set_host_override(smali_root)
    write_receiver_smali(smali_root)
    inject_main_activity_restart_hook(smali_root)
    fix_native_library_loader_default(smali_root)
    strip_conflicting_final(sorted(decoded_dir.glob("smali*")))
    print(f"patched decoded APK directory {decoded_dir}")
    print(f"receiver: {RECEIVER_CLASS}")


def run(cmd: list[str]) -> None:
    print("+ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def default_output_path(input_apk: Path) -> Path:
    return input_apk.with_name(f"{input_apk.stem}-ra-host.apk")


def default_tool(name: str, bundled_jar: str) -> str:
    candidate = BUNDLED_LIB_DIR / bundled_jar
    if candidate.exists():
        return str(candidate)
    return name


def tool_cmd(tool: str, label: str) -> list[str]:
    path = Path(tool)
    if path.suffix == ".jar":
        if not path.exists():
            raise SystemExit(f"{label} jar not found: {path}")
        return ["java", "-jar", str(path.resolve())]
    if os.sep in tool or (os.altsep and os.altsep in tool):
        if not path.exists():
            raise SystemExit(f"{label} executable not found: {path}")
        return [str(path.resolve())]
    if shutil.which(tool) is None:
        raise SystemExit(f"{label} not found on PATH: {tool}")
    return [tool]


def align_apk(input_apk: Path, output_apk: Path, alignment: int = 4) -> None:
    # Minimal zipalign equivalent for STORED entries; apksigner requires
    # alignment to happen before v2/v3 signing.
    pad_header_id = 0xD935
    with zipfile.ZipFile(input_apk, "r") as zin, zipfile.ZipFile(output_apk, "w") as zout:
        for src in zin.infolist():
            info = zipfile.ZipInfo(src.filename, date_time=src.date_time)
            info.compress_type = src.compress_type
            info.comment = src.comment
            info.external_attr = src.external_attr
            info.internal_attr = src.internal_attr
            info.create_system = src.create_system
            info.extra = src.extra
            data = zin.read(src.filename)

            if src.compress_type == zipfile.ZIP_STORED:
                filename_len = len(src.filename.encode("utf-8"))
                data_offset = zout.fp.tell() + 30 + filename_len + len(info.extra)
                needed = (-data_offset) % alignment
                if needed:
                    total_extra = needed if needed >= 4 else needed + alignment
                    payload_len = total_extra - 4
                    info.extra += (
                        pad_header_id.to_bytes(2, "little")
                        + payload_len.to_bytes(2, "little")
                        + (b"\x00" * payload_len)
                    )

            zout.writestr(info, data)


def patch_apk(args: argparse.Namespace) -> None:
    input_apk = args.input.resolve()
    output_apk = (args.output or default_output_path(input_apk)).resolve()
    apktool = tool_cmd(args.apktool, "apktool")
    apksigner = None if args.unsigned else tool_cmd(args.apksigner, "apksigner")
    keystore = args.keystore.resolve() if args.keystore else None

    if not input_apk.exists():
        raise SystemExit(f"Input APK not found: {input_apk}")
    if input_apk.is_dir():
        raise SystemExit("Input must be an APK file, not a decoded directory")
    if not args.unsigned:
        if keystore is None:
            raise SystemExit("Signing requires --keystore, or pass --unsigned to leave the rebuilt APK unsigned")
        if not keystore.exists():
            raise SystemExit(f"Keystore not found: {keystore}")

    work_dir = Path(tempfile.mkdtemp(prefix="nethersx2-ra-host-"))
    work_dir = work_dir.resolve()
    decoded = work_dir / "decoded"
    unsigned = work_dir / "unsigned.apk"
    aligned = work_dir / "aligned.apk"

    try:
        run(apktool + ["d", "-f", "--frame-path", str(work_dir / "framework"), "-o", str(decoded), str(input_apk)])
        patch_decoded_dir(decoded)
        run(apktool + ["b", "--use-aapt2", "--frame-path", str(work_dir / "framework"), "-o", str(unsigned), str(decoded)])
        align_apk(unsigned, aligned)
        if args.unsigned:
            shutil.copyfile(aligned, output_apk)
        else:
            run(
                apksigner
                + [
                    "sign",
                    "--ks",
                    str(keystore),
                    "--ks-pass",
                    f"pass:{args.ks_pass}",
                    "--key-pass",
                    f"pass:{args.key_pass}",
                    "--out",
                    str(output_apk),
                    str(aligned),
                ]
            )
            run(apksigner + ["verify", "--verbose", str(output_apk)])
        print(f"patched APK: {output_apk}")
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    bundled_keystore = BUNDLED_LIB_DIR / "android.jks"
    parser = argparse.ArgumentParser(
        description=(
            "Add a RetroAchievements host-override broadcast receiver to a "
            "NetherSX2 APK."
        )
    )
    parser.add_argument("input", type=Path, help="Input APK")
    parser.add_argument("-o", "--output", type=Path, help="Output APK path")
    parser.add_argument("--apktool", default=default_tool("apktool", "apktool.jar"))
    parser.add_argument("--apksigner", default=default_tool("apksigner", "apksigner.jar"))
    parser.add_argument(
        "--keystore",
        type=Path,
        default=bundled_keystore if bundled_keystore.exists() else None,
        help="Signing keystore. Defaults to decomp/lib/android.jks when present.",
    )
    parser.add_argument("--ks-pass", default="android_sign")
    parser.add_argument("--key-pass", default="android_sign_alias")
    parser.add_argument("--unsigned", action="store_true", help="Write an unsigned APK")
    return parser.parse_args()


def main() -> None:
    patch_apk(parse_args())


if __name__ == "__main__":
    main()
