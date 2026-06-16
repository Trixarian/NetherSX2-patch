#!/usr/bin/env python3
"""Patch NetherSX2/AetherSX2 APK storage to prefer /storage/emulated/0/NetherSX2."""
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
ROOT_DIR = "/storage/emulated/0/NetherSX2"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BUNDLED_LIB_DIR = REPO_ROOT / "decomp/lib"

# Bypass native package-segment checks. Exact byte guards keep unknown builds from
# being patched blindly.
EMUCORE_PATCH_VARIANTS = {
    "4248": {
        0x83A3EC: ("e0c200b4", "ac000014"),
        0x83A430: ("06060014", "9b000014"),
        0x83A790: ("c0a500b4", "51000014"),
        0x83A7D4: ("1d050014", "40000014"),
    },
    "classic-3668": {
        0x82D0DC: ("00c300b4", "ac000014"),
        0x82D120: ("07060014", "9b000014"),
        0x82D480: ("e0a500b4", "51000014"),
        0x82D4C4: ("1e050014", "40000014"),
    },
}


def patch_manifest(manifest: Path) -> None:
    text = manifest.read_text(encoding="utf-8")
    permission = '<uses-permission android:name="android.permission.MANAGE_EXTERNAL_STORAGE" />'
    if "android.permission.MANAGE_EXTERNAL_STORAGE" not in text:
        text = text.replace("<application", f"    {permission}\n    <application", 1)
    manifest.write_text(text, encoding="utf-8")


def inject_main_activity_prompt(smali_root: Path) -> None:
    # Prompt before native initialization so first-run setup does not create
    # files in app-private storage when all-files access is about to be granted.
    path = smali_root / "xyz/aethersx2/android/MainActivity.smali"
    if not path.exists():
        raise SystemExit(f"MainActivity.smali not found at {path}")

    text = path.read_text(encoding="utf-8")
    if "maybePromptAllFilesAccess" in text:
        print("MainActivity prompt already injected")
        return

    method = f"""
.method private maybePromptAllFilesAccess()Z
    .locals 6

    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I
    const/4 v5, 0x0
    const/16 v1, 0x1e
    if-lt v0, v1, :no_prompt

    invoke-static {{}}, Landroid/os/Environment;->isExternalStorageManager()Z
    move-result v0
    if-nez v0, :no_prompt

    const-string v0, "RootStorage"
    invoke-virtual {{p0, v0, v5}}, Lxyz/aethersx2/android/MainActivity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;
    move-result-object v0

    const-string v2, "AllFilesPromptShown"
    invoke-interface {{v0, v2, v5}}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z
    move-result v3
    if-nez v3, :no_prompt

    invoke-interface {{v0}}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;
    move-result-object v0
    const/4 v3, 0x1
    invoke-interface {{v0, v2, v3}}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    move-result-object v0
    const-string v4, "AllFilesPromptPending"
    invoke-interface {{v0, v4, v3}}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    move-result-object v0
    const-string v4, "AllFilesPromptResumeCount"
    invoke-interface {{v0, v4, v5}}, Landroid/content/SharedPreferences$Editor;->putInt(Ljava/lang/String;I)Landroid/content/SharedPreferences$Editor;
    move-result-object v0
    invoke-interface {{v0}}, Landroid/content/SharedPreferences$Editor;->apply()V

    :try_start
    new-instance v0, Landroid/content/Intent;
    const-string v2, "android.settings.MANAGE_APP_ALL_FILES_ACCESS_PERMISSION"
    invoke-direct {{v0, v2}}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct {{v2}}, Ljava/lang/StringBuilder;-><init>()V
    const-string v4, "package:"
    invoke-virtual {{v2, v4}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {{p0}}, Lxyz/aethersx2/android/MainActivity;->getPackageName()Ljava/lang/String;
    move-result-object v4
    invoke-virtual {{v2, v4}}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {{v2}}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v2
    invoke-static {{v2}}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;
    move-result-object v2
    invoke-virtual {{v0, v2}}, Landroid/content/Intent;->setData(Landroid/net/Uri;)Landroid/content/Intent;
    invoke-virtual {{p0, v0}}, Lxyz/aethersx2/android/MainActivity;->startActivity(Landroid/content/Intent;)V
    :try_end
    .catch Landroid/content/ActivityNotFoundException; {{:try_start .. :try_end}} :fallback
    return v3

    :fallback
    new-instance v0, Landroid/content/Intent;
    const-string v2, "android.settings.MANAGE_ALL_FILES_ACCESS_PERMISSION"
    invoke-direct {{v0, v2}}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V
    invoke-virtual {{p0, v0}}, Lxyz/aethersx2/android/MainActivity;->startActivity(Landroid/content/Intent;)V
    return v3

    :no_prompt
    return v5
.end method

"""

    insert_at = text.find(".method protected onCreate")
    if insert_at < 0:
        insert_at = text.find(".method public onCreate")
    if insert_at < 0:
        insert_at = text.find(".method public final onCreate")
    if insert_at < 0:
        raise SystemExit("Could not find MainActivity.onCreate")
    text = text[:insert_at] + method + "\n" + text[insert_at:]

    on_create = re.search(r"(?s)(\.method (?:protected|public)(?: final)? onCreate\(Landroid/os/Bundle;\)V.*?\.end method)", text)
    if not on_create:
        raise SystemExit("Could not capture MainActivity.onCreate body")
    body = on_create.group(1)
    body2, replacements = re.subn(
        r"(invoke-super \{p0, p1\}, L[^;]+;->onCreate\(Landroid/os/Bundle;\)V\n)",
        rf"\1\n    invoke-direct {{p0}}, L{PKG.replace('.', '/')}/MainActivity;->maybePromptAllFilesAccess()Z\n\n    move-result p1\n\n    if-eqz p1, :after_all_files_prompt\n\n    return-void\n\n    :after_all_files_prompt\n",
        body,
        count=1,
    )
    if replacements != 1:
        raise SystemExit("Could not inject call after MainActivity super.onCreate")

    text = text[: on_create.start(1)] + body2 + text[on_create.end(1) :]

    # While Android Settings is in front, onStart can run again. Hold the app at
    # this point until permission is granted, or continue on the original path if
    # the user backs out twice.
    on_start = re.search(r"(?s)(\.method (?:protected|public)(?: final)? onStart\(\)V.*?\.end method)", text)
    if not on_start:
        raise SystemExit("Could not capture MainActivity.onStart body")
    start_body = on_start.group(1)
    start_body2, replacements = re.subn(
        r"(invoke-super \{p0\}, L[^;]+;->onStart\(\)V\n)",
        r"""\1
    const-string v0, "RootStorage"

    const/4 v1, 0x0

    invoke-virtual {p0, v0, v1}, Lxyz/aethersx2/android/MainActivity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;

    move-result-object v0

    const-string v2, "AllFilesPromptPending"

    invoke-interface {v0, v2, v1}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z

    move-result v3

    if-eqz v3, :after_all_files_prompt_start

    invoke-static {}, Landroid/os/Environment;->isExternalStorageManager()Z

    move-result v3

    if-nez v3, :recreate_after_all_files_prompt

    const-string v3, "AllFilesPromptResumeCount"

    invoke-interface {v0, v3, v1}, Landroid/content/SharedPreferences;->getInt(Ljava/lang/String;I)I

    move-result v4

    add-int/lit8 v4, v4, 0x1

    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v5

    invoke-interface {v5, v3, v4}, Landroid/content/SharedPreferences$Editor;->putInt(Ljava/lang/String;I)Landroid/content/SharedPreferences$Editor;

    move-result-object v5

    invoke-interface {v5}, Landroid/content/SharedPreferences$Editor;->apply()V

    const/4 v5, 0x2

    if-lt v4, v5, :wait_for_all_files_prompt

    :recreate_after_all_files_prompt
    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    invoke-interface {v0, v2, v1}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    invoke-interface {v0}, Landroid/content/SharedPreferences$Editor;->apply()V

    invoke-virtual {p0}, Landroid/app/Activity;->recreate()V

    :wait_for_all_files_prompt

    return-void

    :after_all_files_prompt_start
""",
        start_body,
        count=1,
    )
    if replacements != 1:
        raise SystemExit("Could not inject MainActivity.onStart all-files prompt guard")

    text = text[: on_start.start(1)] + start_body2 + text[on_start.end(1) :]
    path.write_text(text, encoding="utf-8")


def ensure_method_register_capacity(method_body: str, min_locals: int, min_registers: int) -> str:
    locals_match = re.search(r"(?m)^    \.locals (\d+)$", method_body)
    if locals_match:
        current = int(locals_match.group(1))
        if current < min_locals:
            return (
                method_body[: locals_match.start(1)]
                + str(min_locals)
                + method_body[locals_match.end(1) :]
            )
        return method_body

    registers_match = re.search(r"(?m)^    \.registers (\d+)$", method_body)
    if registers_match:
        current = int(registers_match.group(1))
        if current < min_registers:
            return (
                method_body[: registers_match.start(1)]
                + str(min_registers)
                + method_body[registers_match.end(1) :]
            )
        return method_body

    raise SystemExit("Could not find NativeLibrary.initializeOnce register declaration")


def patch_native_library(smali_root: Path) -> None:
    # NativeLibrary.mDataDirectory is the Java-side root passed into native init.
    # Android 11+ uses the shared root only after MANAGE_EXTERNAL_STORAGE is set;
    # otherwise the app keeps its original getExternalFilesDir/getDataDir fallback.
    path = smali_root / "xyz/aethersx2/android/NativeLibrary.smali"
    if not path.exists():
        raise SystemExit(f"NativeLibrary.smali not found at {path}")

    text = path.read_text(encoding="utf-8")
    if ROOT_DIR in text:
        print("NativeLibrary data dir already patched")
        return

    method = re.search(r"(?s)(\.method (?:public|private) static initializeOnce\(Landroid/content/Context;Z\)Z.*?\.end method)", text)
    if not method:
        raise SystemExit("Could not find NativeLibrary.initializeOnce(Context, boolean)")
    body = ensure_method_register_capacity(method.group(1), min_locals=6, min_registers=8)

    if "{p0, v0}, Landroid/content/Context;->getExternalFilesDir" in body:
        ctx = "p0"
    elif "{v6, v0}, Landroid/content/Context;->getExternalFilesDir" in body:
        ctx = "v6"
    else:
        raise SystemExit("Could not identify Context register in NativeLibrary.initializeOnce")

    pattern = re.compile(
        r"(?s)    const/4 v0, 0x0\s+"
        r"(?:    \.line \d+\s+)?"
        r"    invoke-virtual \{" + re.escape(ctx) + r", v0\}, Landroid/content/Context;->getExternalFilesDir\(Ljava/lang/String;\)Ljava/io/File;\s+"
        r"    move-result-object v2\s+"
        r"    if-nez v2, :cond_[0-9a-f]+\s+"
        r"(?:    \.line \d+\s+)?"
        r"    invoke-virtual \{" + re.escape(ctx) + r"\}, Landroid/content/Context;->getDataDir\(\)Ljava/io/File;\s+"
        r"    move-result-object v2\s+"
        r"(?:    \.line \d+\s+)?"
        r"    :cond_[0-9a-f]+\s+"
        r"    invoke-virtual \{v2\}, Ljava/io/File;->getAbsolutePath\(\)Ljava/lang/String;\s+"
        r"    move-result-object v2\s+"
        r"    sput-object v2, Lxyz/aethersx2/android/NativeLibrary;->mDataDirectory:Ljava/lang/String;"
    )
    replacement = f"""    sget v3, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v4, 0x1e

    if-lt v3, v4, :use_root_dir

    invoke-static {{}}, Landroid/os/Environment;->isExternalStorageManager()Z

    move-result v3

    if-nez v3, :use_root_dir

    const/4 v0, 0x0

    invoke-virtual {{{ctx}, v0}}, Landroid/content/Context;->getExternalFilesDir(Ljava/lang/String;)Ljava/io/File;

    move-result-object v2

    if-nez v2, :use_fallback_file

    invoke-virtual {{{ctx}}}, Landroid/content/Context;->getDataDir()Ljava/io/File;

    move-result-object v2

    :use_fallback_file
    invoke-virtual {{v2}}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v2

    goto :store_data_dir

    :use_root_dir
    const-string v2, "{ROOT_DIR}"

    new-instance v5, Ljava/io/File;

    invoke-direct {{v5, v2}}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {{v5}}, Ljava/io/File;->mkdirs()Z

    :store_data_dir
    sput-object v2, Lxyz/aethersx2/android/NativeLibrary;->mDataDirectory:Ljava/lang/String;

    const/4 v0, 0x0"""

    body2, replacements = pattern.subn(replacement, body, count=1)
    if replacements != 1:
        raise SystemExit("Could not patch NativeLibrary data-dir block; smali shape differs from expected target")

    text = text[: method.start(1)] + body2 + text[method.end(1) :]
    path.write_text(text, encoding="utf-8")


def patch_emucore_binary(decoded: Path) -> str:
    # libemucore rejects data roots that do not contain the package name segment.
    # Patch only known guarded branch instructions so an unknown build fails safe.
    path = decoded / "lib/arm64-v8a/libemucore.so"
    if not path.exists():
        raise SystemExit(f"libemucore.so not found at {path}")

    data = bytearray(path.read_bytes())
    selected_name = None
    selected_patches = None
    mismatch_notes = []
    for name, patches in EMUCORE_PATCH_VARIANTS.items():
        mismatches = []
        for offset, (expected_hex, replacement_hex) in patches.items():
            expected = bytes.fromhex(expected_hex)
            replacement = bytes.fromhex(replacement_hex)
            actual = bytes(data[offset : offset + len(expected)])
            if actual not in (expected, replacement):
                mismatches.append(f"0x{offset:x}: found {actual.hex()}, expected {expected_hex}")
        if not mismatches:
            selected_name = name
            selected_patches = patches
            break
        mismatch_notes.append(f"{name}: " + "; ".join(mismatches))

    if selected_patches is None:
        raise SystemExit(
            "libemucore.so does not match any known package-segment check pattern:\n"
            + "\n".join(mismatch_notes)
        )

    changed = False
    for offset, (expected_hex, replacement_hex) in selected_patches.items():
        expected = bytes.fromhex(expected_hex)
        replacement = bytes.fromhex(replacement_hex)
        actual = bytes(data[offset : offset + len(expected)])
        if actual == replacement:
            continue
        if actual != expected:
            raise SystemExit(
                f"Unexpected libemucore.so bytes at 0x{offset:x}: "
                f"found {actual.hex()}, expected {expected_hex}"
            )
        data[offset : offset + len(expected)] = replacement
        changed = True

    if changed:
        path.write_bytes(data)
    else:
        print(f"libemucore package-segment check already patched ({selected_name})")
    return selected_name


def find_smali_root(decoded: Path) -> Path:
    for candidate in sorted(decoded.glob("smali*")):
        if (candidate / "xyz/aethersx2/android/NativeLibrary.smali").exists():
            return candidate
    raise SystemExit("Could not find smali root containing xyz/aethersx2/android/NativeLibrary.smali")


def run(cmd: list[str]) -> None:
    print("+ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def default_output_path(input_apk: Path) -> Path:
    return input_apk.with_name(f"{input_apk.stem}-root-storage.apk")


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


def patch_decoded_dir(decoded_dir: Path) -> str:
    patch_manifest(decoded_dir / "AndroidManifest.xml")
    smali_root = find_smali_root(decoded_dir)
    patch_native_library(smali_root)
    native_variant = patch_emucore_binary(decoded_dir)
    inject_main_activity_prompt(smali_root)
    print(f"patched decoded APK directory {decoded_dir}")
    print(f"preferred data root: {ROOT_DIR}")
    print("fallback data root: original getExternalFilesDir(null), then getDataDir()")
    return native_variant


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

    work_dir = Path(tempfile.mkdtemp(prefix="nethersx2-root-storage-"))
    work_dir = work_dir.resolve()
    decoded = work_dir / "decoded"
    unsigned = work_dir / "unsigned.apk"
    aligned = work_dir / "aligned.apk"

    try:
        run(apktool + ["d", "-f", "--frame-path", str(work_dir / "framework"), "-o", str(decoded), str(input_apk)])
        variant = patch_decoded_dir(decoded)
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
        print(f"native patch variant: {variant}")
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    bundled_keystore = BUNDLED_LIB_DIR / "android.jks"
    parser = argparse.ArgumentParser(
        description=(
            "Patch a NetherSX2 APK to prefer /storage/emulated/0/NetherSX2 "
            "for live user data."
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
