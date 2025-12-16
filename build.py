#!/usr/bin/env python3
"""Build script for VideoMorph using PyInstaller.

This script builds VideoMorph for the current platform using PyInstaller.
It works with uv package manager and supports macOS, Linux, and Windows.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from sys import platform

import tomllib

# Project root directory
ROOT = Path(__file__).parent.resolve()
BIN_DIR = ROOT / "bin"
DIST_DIR = ROOT / "dist"
PYINSTALLER_TMP_DIR = DIST_DIR / "pyinstaller_tmps"
MAC_DIST_DIR = DIST_DIR / "macOS"
HOMEBREW_DIST_DIR = MAC_DIST_DIR / "Homebrew"
DEBIAN_DIST_DIR = DIST_DIR / "Debian"
BUILD_DIR = ROOT / "build"
ENTRY_SCRIPT = ROOT / "videomorph" / "main.py"
DEB_TEMPLATE_DIR = ROOT / "videomorph_deb"

# Platform-specific configuration
PLATFORMS = {
    "darwin": {
        "name": "macos",
        "spec": "videomorph_macos.spec",
        "icon": "share/icons/icon.icns",
        "bundle_name": "VideoMorph.app",
        "bundle_identifier": "org.videomorph.VideoMorph",
    },
    "linux": {
        "name": "linux",
        "spec": "videomorph_linux64.spec",
        "icon": "share/icons/videomorph.png",
    },
    "win32": {
        "name": "windows",
        "spec": "videomorph_win64.spec",
        "icon": "share/icons/videomorph.ico",
    },
}


def _copytree(src: Path, dst: Path) -> None:
    """Copy directory trees with existing destination support."""
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)


def _move_artifact(source: Path, target_dir: Path) -> Path | None:
    """Move built artifacts into a target directory."""
    if not source.exists():
        return None

    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / source.name
    if destination.exists():
        if destination.is_dir():
            shutil.rmtree(destination)
        else:
            destination.unlink()
    shutil.move(str(source), destination)
    return destination


def _dir_size_kb(path: Path) -> int:
    """Return directory size in kilobytes."""
    total = 0
    for file_path in path.rglob("*"):
        if file_path.is_file():
            total += file_path.stat().st_size
    return max(1, total // 1024)


def _rewrite_control_file(control_path: Path, *, version: str, installed_size: int) -> None:
    """Update Debian control metadata with current values."""
    replacements = {
        "Version": version,
        "Installed-Size": str(installed_size),
        "Depends": "ffmpeg, python3 (>= 3.12), python3-pyqt6",
    }

    lines = control_path.read_text(encoding="utf-8").splitlines()
    found = {key: False for key in replacements}

    for idx, line in enumerate(lines):
        for key, value in replacements.items():
            if line.startswith(f"{key}:"):
                lines[idx] = f"{key}: {value}"
                found[key] = True

    for key, was_found in found.items():
        if not was_found:
            lines.append(f"{key}: {replacements[key]}")

    control_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _create_unix_launcher(target_dir: Path) -> None:
    """Create /usr/bin launcher for Unix packages."""
    bin_dir = target_dir / "usr/bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    launcher = bin_dir / "videomorph"
    launcher.write_text(
        "#!/bin/sh\nexec /opt/videomorph/videomorph \"$@\"\n", encoding="utf-8"
    )
    launcher.chmod(0o755)


def _copy_share_assets(target_dir: Path) -> None:
    """Copy shared resources (desktop file, icons, docs) into staging area."""
    share_src = ROOT / "share"
    if not share_src.exists():
        return

    for entry in share_src.iterdir():
        dest = target_dir / "usr/share" / entry.name
        if entry.is_dir():
            _copytree(entry, dest)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(entry, dest)

    doc_dir = target_dir / "usr/share/doc/videomorph"
    doc_dir.mkdir(parents=True, exist_ok=True)
    for name in ("README.md", "LICENSE", "changelog", "changelog.gz", "TODO"):
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, doc_dir / source.name)

    icon_src = ROOT / "share/icons/videomorph.png"
    if icon_src.exists():
        pixmap_dir = target_dir / "usr/share/pixmaps"
        pixmap_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(icon_src, pixmap_dir / "videomorph.png")


def _stage_unix_tree(package_root: Path, pyinstaller_dir: Path) -> None:
    """Populate the filesystem tree for Unix-like packages."""
    opt_dir = package_root / "opt"
    opt_dir.mkdir(parents=True, exist_ok=True)
    _copytree(pyinstaller_dir, opt_dir / "videomorph")
    _create_unix_launcher(package_root)
    _copy_share_assets(package_root)


def _build_deb_package(version: str) -> Path:
    """Create a Debian package that wraps the PyInstaller build output."""
    dpkg_bin = shutil.which("dpkg-deb")
    if not dpkg_bin:
        raise RuntimeError("dpkg-deb not found in PATH; install dpkg-dev.")

    pyinstaller_dir = PYINSTALLER_TMP_DIR / "videomorph"
    if not pyinstaller_dir.exists():
        raise RuntimeError(
            f"PyInstaller output not found: {pyinstaller_dir}. Run the build first."
        )

    staging_root = BUILD_DIR / "deb_staging"
    if staging_root.exists():
        shutil.rmtree(staging_root)

    package_root = staging_root / "videomorph"
    debian_dir = package_root / "DEBIAN"
    debian_dir.mkdir(parents=True, exist_ok=True)

    template_control = DEB_TEMPLATE_DIR / "DEBIAN" / "control"
    template_postinst = DEB_TEMPLATE_DIR / "DEBIAN" / "postinst"
    if not template_control.exists() or not template_postinst.exists():
        raise RuntimeError("Debian control templates are missing under videomorph_deb/DEBIAN.")

    shutil.copy2(template_control, debian_dir / "control")
    shutil.copy2(template_postinst, debian_dir / "postinst")
    (debian_dir / "postinst").chmod(0o755)

    _stage_unix_tree(package_root, pyinstaller_dir)

    installed_size = _dir_size_kb(package_root)
    _rewrite_control_file(
        debian_dir / "control",
        version=version,
        installed_size=installed_size,
    )

    output_deb = DIST_DIR / f"videomorph_{version}.deb"
    output_deb.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [dpkg_bin, "--build", str(package_root), str(output_deb)],
        check=True,
    )
    print(f"✓ Debian package created: {output_deb}")
    return output_deb




def _literal(value: Path | str) -> str:
    """Return a Python source literal for a filesystem path."""
    return repr(str(value))


def _format_data_files(data_files: list[tuple[str, str]]) -> str:
    """Format data files for inclusion in a spec file."""
    if not data_files:
        return "[]"

    lines = ["["]
    for src, dst in data_files:
        lines.append(f"    ({_literal(src)}, {_literal(dst)}),")
    lines.append("]")
    return "\n".join(lines)


def get_platform_config():
    """Get configuration for the current platform."""
    if platform == "darwin":
        return PLATFORMS["darwin"]
    elif platform.startswith("linux"):
        return PLATFORMS["linux"]
    elif platform == "win32":
        return PLATFORMS["win32"]
    else:
        raise RuntimeError(f"Unsupported platform: {platform}")


def ensure_pyinstaller():
    """Ensure PyInstaller is installed via uv."""
    print("Checking for PyInstaller...")
    try:
        result = subprocess.run(
            ["uv", "run", "pyinstaller", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"PyInstaller found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing PyInstaller via uv...")
        subprocess.run(
            ["uv", "pip", "install", "pyinstaller"],
            check=True,
        )
        return True


def get_data_files():
    """Get list of data files to include in the bundle."""
    base = ROOT
    data_files = [
        (base / "changelog.gz", "."),
        (base / "LICENSE", "."),
        (base / "README.md", "."),
        (base / "TODO", "."),
        (base / "screenshot.png", "."),
    ]

    share_dir = base / "share"
    if share_dir.exists():
        for file_path in share_dir.rglob("*"):
            if file_path.is_file():
                destination = file_path.parent.relative_to(base).as_posix()
                data_files.append((file_path, destination or "."))

    return [(src.as_posix(), dst) for src, dst in data_files if src.exists()]


def _get_project_version() -> str:
    """Read project version from pyproject.toml."""
    pyproject = ROOT / "pyproject.toml"
    if not pyproject.exists():
        return "0.0.0"

    with pyproject.open("rb") as f:
        try:
            data = tomllib.load(f)
            return str(data.get("project", {}).get("version", "0.0.0"))
        except (tomllib.TOMLDecodeError, AttributeError):
            return "0.0.0"


def _create_macos_pkg(config: dict) -> Path | None:
    """Create a distributable macOS .pkg installer."""
    bundle_name = config.get("bundle_name")
    if not bundle_name:
        return None

    app_path = PYINSTALLER_TMP_DIR / bundle_name
    if not app_path.exists():
        print(f"Skipping pkg creation: app bundle not found at {app_path}")
        return None

    pkgbuild_bin = shutil.which("pkgbuild")
    if not pkgbuild_bin:
        print("Warning: pkgbuild not found. Skipping macOS installer generation.")
        return None

    version = _get_project_version()
    pkg_basename = Path(bundle_name).stem
    pkg_name = f"{pkg_basename}-{version}.pkg"
    pkg_path = DIST_DIR / pkg_name

    identifier = config.get("bundle_identifier", "org.videomorph.VideoMorph")
    cmd = [
        pkgbuild_bin,
        "--component",
        str(app_path),
        "--install-location",
        "/Applications",
        "--identifier",
        identifier,
        "--version",
        version,
        str(pkg_path),
    ]

    print(f"Creating macOS installer: {pkg_path}")
    subprocess.run(cmd, check=True)
    print(f"✓ macOS installer created: {pkg_path}")
    return pkg_path


def _create_homebrew_archive(app_bundle: Path, version: str) -> Path | None:
    """Create a tarball suitable for Homebrew distribution."""
    if not app_bundle.exists():
        return None

    HOMEBREW_DIST_DIR.mkdir(parents=True, exist_ok=True)
    archive_base = HOMEBREW_DIST_DIR / f"{app_bundle.stem}-{version}"
    archive_path = shutil.make_archive(
        str(archive_base), "gztar", root_dir=app_bundle.parent, base_dir=app_bundle.name
    )
    return Path(archive_path)


def _resolve_icon(config: dict) -> Path | None:
    """Return a platform-compatible icon path or None."""
    icon_rel = config.get("icon")
    if not icon_rel:
        return None

    icon_path = ROOT / icon_rel
    if not icon_path.exists():
        print(f"Warning: icon file not found: {icon_path}")
        return None

    suffix = icon_path.suffix.lower()
    if config.get("name") == "macos" and suffix != ".icns":
        icns_fallback = icon_path.with_suffix(".icns")
        if icns_fallback.exists():
            print(f"Using macOS .icns icon: {icns_fallback}")
            return icns_fallback
        print(
            "Warning: macOS bundles require .icns icons. "
            f"Found {icon_path.name}; using default PyInstaller icon."
        )
        return None

    return icon_path


def create_spec_file(config: dict, *, reuse_existing: bool = False) -> Path:
    """Create or update PyInstaller spec file for the current platform."""
    spec_path = BIN_DIR / config["spec"]

    if reuse_existing and spec_path.exists():
        print(f"Using existing spec file: {spec_path}")
        return spec_path

    action = "Updating" if spec_path.exists() else "Creating"
    print(f"{action} spec file: {spec_path}")
    create_basic_spec(spec_path, config)
    return spec_path


def create_basic_spec(spec_path, config):
    """Create a basic PyInstaller spec file."""
    data_files = get_data_files()
    icon_path = _resolve_icon(config)
    icon_str = _literal(icon_path) if icon_path else "None"

    if not ENTRY_SCRIPT.exists():
        raise FileNotFoundError(
            f"Entry script not found: {ENTRY_SCRIPT}. " "Did the project layout change?"
        )

    script_path = _literal(ENTRY_SCRIPT)
    data_files_str = _format_data_files(data_files)
    pathex = _literal(ROOT)

    bundle_block = ""
    bundle_name = config.get("bundle_name")
    if bundle_name:
        bundle_lines = [
            "",
            "app = BUNDLE(",
            "    coll,",
            f"    name={_literal(bundle_name)},",
            f"    icon={icon_str},",
        ]
        bundle_identifier = config.get("bundle_identifier")
        if bundle_identifier:
            bundle_lines.append(
                f"    bundle_identifier={_literal(bundle_identifier)},"
            )
        bundle_lines.append(")")
        bundle_block = "\n".join(bundle_lines)

    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [{script_path}],
    pathex=[{pathex}],
    binaries=[],
    datas={data_files_str},
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='videomorph',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={icon_str},
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='videomorph',
)
{bundle_block}
"""

    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(spec_content, encoding="utf-8")


def clean_build_dirs():
    """Clean previous build artifacts."""
    print("Cleaning build directories...")
    for directory in [BUILD_DIR, DIST_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"Removed {directory}")


def build(config, clean=False, reuse_spec=False, build_deb=False):
    """Build the application using PyInstaller."""
    if clean:
        clean_build_dirs()

    ensure_pyinstaller()

    spec_file = create_spec_file(config, reuse_existing=reuse_spec)
    if PYINSTALLER_TMP_DIR.exists():
        shutil.rmtree(PYINSTALLER_TMP_DIR)
    PYINSTALLER_TMP_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nBuilding VideoMorph for {config['name']}...")
    print(f"Using spec file: {spec_file}")

    cmd = [
        "uv",
        "run",
        "pyinstaller",
        "--clean",
        "--noconfirm",
        "--distpath",
        str(PYINSTALLER_TMP_DIR),
        str(spec_file),
    ]

    try:
        subprocess.run(cmd, check=True, cwd=ROOT)
        print("\n✓ Build completed successfully!")
        print(f"  Temporary PyInstaller output: {PYINSTALLER_TMP_DIR}")
        print(f"  Final artifacts directory: {DIST_DIR}")
        if config["name"] == "macos":
            version = _get_project_version()
            pkg_path = _create_macos_pkg(config)
            app_path = PYINSTALLER_TMP_DIR / config.get("bundle_name", "")
            if app_path.exists():
                moved_app = _move_artifact(app_path, MAC_DIST_DIR)
                if moved_app:
                    print(f"  Moved app bundle to: {moved_app}")
                    hb_archive = _create_homebrew_archive(moved_app, version)
                    if hb_archive:
                        print(f"  Homebrew archive created: {hb_archive}")
            if pkg_path and pkg_path.exists():
                moved_pkg = _move_artifact(pkg_path, MAC_DIST_DIR)
                if moved_pkg:
                    print(f"  Moved pkg installer to: {moved_pkg}")
        if build_deb:
            if config["name"] != "linux":
                print("Skipping Debian package: only available for Linux builds.")
            else:
                try:
                    deb_path = _build_deb_package(_get_project_version())
                    moved_deb = _move_artifact(deb_path, DEBIAN_DIST_DIR)
                    if moved_deb:
                        print(f"  Moved Debian package to: {moved_deb}")
                except RuntimeError as exc:
                    print(f"\n✗ Debian packaging failed: {exc}", file=sys.stderr)
                    sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build VideoMorph using PyInstaller")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build directories before building",
    )
    parser.add_argument(
        "--reuse-spec",
        action="store_true",
        help="Use the existing spec file without regenerating it",
    )
    parser.add_argument(
        "--deb",
        action="store_true",
        help="Build a Debian package after PyInstaller completes (Linux only)",
    )

    args = parser.parse_args()

    try:
        config = get_platform_config()
        print(f"Platform: {config['name']}")
        build(
            config,
            clean=args.clean,
            reuse_spec=args.reuse_spec,
            build_deb=args.deb,
        )
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
