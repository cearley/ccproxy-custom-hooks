#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Standalone installer for CCProxy configuration.

Behavior:
    - First install: Creates config.yaml and ccproxy.yaml from .example templates
    - Upgrades: Updates .example files, preserves your existing configs
    - Custom hooks: Always updated to latest version

Usage:
    # From GitHub (one command!)
    uv run https://raw.githubusercontent.com/cearley/ccproxy-custom-hooks/main/install.py

    # From local directory
    uv run install.py

    # Custom installation directory
    CCPROXY_CONFIG_DIR=/custom/path uv run install.py

    # After upgrade, compare configs to see what changed:
    diff ~/.ccproxy/config.yaml ~/.ccproxy/config.example.yaml
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

GITHUB_REPO = "cearley/ccproxy-custom-hooks"
GITHUB_BRANCH = "main"


def extract_version(source_dir: Path) -> str:
    """Extract version from custom_hooks.py."""
    custom_hooks_file = source_dir / "ccproxy-custom-hooks" / "custom_hooks.py"
    if not custom_hooks_file.exists():
        return "unknown"

    content = custom_hooks_file.read_text()
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if match:
        return match.group(1)
    return "unknown"


def get_target_dir() -> Path:
    """Get target directory from environment or default."""
    config_dir = os.environ.get("CCPROXY_CONFIG_DIR")
    if config_dir:
        return Path(config_dir).expanduser().resolve()
    return Path.home() / ".ccproxy"


def download_from_github():
    """Download repository as ZIP from GitHub and extract source files."""
    print("📦 Downloading from GitHub...")

    zip_url = f"https://github.com/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "repo.zip"

        try:
            urlretrieve(zip_url, zip_path)
        except Exception as e:
            print(f"✗ Failed to download from GitHub: {e}")
            print(f"  URL: {zip_url}")
            return None

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        # After extracting, the structure is: repo-branch/
        extracted_dirs = list(Path(tmpdir).iterdir())
        if not extracted_dirs:
            print("✗ No files found in downloaded archive")
            return None

        repo_dir = [d for d in extracted_dirs if d.is_dir()][0]

        # Verify essential files exist
        if not (repo_dir / "ccproxy-custom-hooks").exists():
            print(f"✗ Source files not found in {repo_dir}")
            return None

        # Copy repo to a persistent temp location before tmpdir is cleaned up
        import tempfile as tf

        persistent_temp = Path(tf.mkdtemp(prefix="ccproxy_source_"))
        shutil.copytree(repo_dir, persistent_temp / "source")

        return persistent_temp / "source"


def get_local_source() -> Path | None:
    """Get source files from local directory if running locally."""
    local_source = Path(__file__).parent
    # Verify essential files exist
    if (local_source / "ccproxy-custom-hooks").exists():
        return local_source
    return None


def install_config_files(source_dir: Path, version: str):
    """Install configuration files to target directory."""
    target_dir = get_target_dir()

    print(f"\n{'=' * 60}")
    print(f"Installing CCProxy configuration to {target_dir}")
    print(f"{'=' * 60}\n")

    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created {target_dir}")

    for base_filename in ["config.yaml", "ccproxy.yaml"]:
        example_filename = base_filename.replace(".yaml", ".example.yaml")
        src = source_dir / example_filename
        example_dst = target_dir / example_filename
        actual_dst = target_dir / base_filename

        if not src.exists():
            print(f"⚠ Warning: {example_filename} not found in source")
            continue

        # Always update .example file (remove existing first)
        if example_dst.exists() or example_dst.is_symlink():
            example_dst.unlink()
        shutil.copy2(src, example_dst)
        print(f"✓ Updated {example_filename}")

        # Only create actual config if it doesn't exist (first install)
        if not actual_dst.exists():
            shutil.copy2(src, actual_dst)
            print(f"✓ Created {base_filename} from example")
        else:
            print(f"✓ Preserved existing {base_filename} (compare with {example_filename})")

    hooks_src = source_dir / "ccproxy-custom-hooks"
    hooks_dst = target_dir / "ccproxy-custom-hooks"
    if hooks_src.exists():
        if hooks_dst.exists():
            shutil.rmtree(hooks_dst)
        shutil.copytree(hooks_src, hooks_dst)
        print("✓ Updated ccproxy-custom-hooks/")

        version_file = hooks_dst / "VERSION"
        version_file.write_text(f"{version}\n")
        print(f"✓ Wrote VERSION file (v{version})")
    else:
        print("⚠ Warning: ccproxy-custom-hooks/ not found in templates")

    print("\n📦 Installing custom hooks package...")
    try:
        subprocess.run(
            [
                "uv",
                "tool",
                "install",
                "--with",
                str(hooks_dst),
                "--force",
                "claude-ccproxy",
                "--with",
                "litellm[proxy]",
            ],
            check=True,
            capture_output=True,
        )
        print("✓ Custom hooks package installed")
    except subprocess.CalledProcessError as e:
        print(f"⚠ Warning: Could not install custom hooks: {e}")
        print("  You can install manually with:")
        print(
            f"  uv tool install --with {hooks_dst} --force claude-ccproxy --with 'litellm[proxy]'"
        )
    except FileNotFoundError:
        print("⚠ Warning: 'uv' command not found")
        print("  Install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh")

    print(f"\n{'=' * 60}")
    print(f"✅ Configuration installed to {target_dir}")
    print(f"{'=' * 60}\n")
    print("Next steps:")
    print("  1. Start ccproxy: ccproxy start --detach")
    print("  2. Check status: ccproxy status")
    print("  3. View logs: ccproxy logs -f")


def main():
    """Main entry point."""
    print("🚀 CCProxy Configuration Installer\n")

    source_dir = get_local_source()
    cleanup_needed = False

    if source_dir:
        print("📁 Using local source files")
    else:
        source_dir = download_from_github()
        cleanup_needed = True
        if not source_dir:
            print("\n✗ Installation failed: Could not get source files")
            sys.exit(1)

    try:
        version = extract_version(source_dir)
        install_config_files(source_dir, version)
        print("\n✨ Installation complete!")
    finally:
        # Clean up downloaded source files
        if cleanup_needed and source_dir and source_dir.exists():
            shutil.rmtree(source_dir.parent)


if __name__ == "__main__":
    main()
