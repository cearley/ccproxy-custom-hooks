#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Standalone installer for CCProxy configuration.

Usage:
    # From GitHub (one command!)
    uv run https://raw.githubusercontent.com/cearley/ccproxy-custom-hooks/main/install.py

    # From local directory
    uv run install.py

    # Custom installation directory
    CCPROXY_CONFIG_DIR=/custom/path uv run install.py
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


def extract_version(templates_dir: Path) -> str:
    """Extract version from custom_hooks.py."""
    custom_hooks_file = templates_dir / "ccproxy-custom-hooks" / "custom_hooks.py"
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
    """Download repository as ZIP from GitHub and extract templates."""
    print("📦 Downloading templates from GitHub...")

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

        # After extracting, the structure is: repo-branch/templates/
        extracted_dirs = list(Path(tmpdir).iterdir())
        if not extracted_dirs:
            print("✗ No files found in downloaded archive")
            return None

        repo_dir = [d for d in extracted_dirs if d.is_dir()][0]
        templates_dir = repo_dir / "templates"

        if not templates_dir.exists():
            print(f"✗ Templates directory not found at {templates_dir}")
            return None

        temp_templates = Path(tmpdir) / "templates_copy"
        shutil.copytree(templates_dir, temp_templates)

        return temp_templates


def get_local_templates() -> Path | None:
    """Get templates from local directory if running locally."""
    local_templates = Path(__file__).parent / "templates"
    if local_templates.exists():
        return local_templates
    return None


def install_config_files(templates_dir: Path, version: str):
    """Install configuration files to target directory."""
    target_dir = get_target_dir()

    print(f"\n{'=' * 60}")
    print(f"Installing CCProxy configuration to {target_dir}")
    print(f"{'=' * 60}\n")

    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created {target_dir}")

    for filename in ["config.yaml", "ccproxy.yaml"]:
        src = templates_dir / filename
        dst = target_dir / filename
        if src.exists():
            if dst.exists() or dst.is_symlink():
                dst.unlink()
            shutil.copy2(src, dst)
            print(f"✓ Copied {filename}")
        else:
            print(f"⚠ Warning: {filename} not found in templates")

    hooks_src = templates_dir / "ccproxy-custom-hooks"
    hooks_dst = target_dir / "ccproxy-custom-hooks"
    if hooks_src.exists():
        if hooks_dst.exists():
            shutil.rmtree(hooks_dst)
        shutil.copytree(hooks_src, hooks_dst)
        print("✓ Copied ccproxy-custom-hooks/")

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

    templates_dir = get_local_templates()

    if templates_dir:
        print("📁 Using local templates")
    else:
        templates_dir = download_from_github()
        if not templates_dir:
            print("\n✗ Installation failed: Could not get templates")
            sys.exit(1)

    version = extract_version(templates_dir)
    install_config_files(templates_dir, version)

    print("\n✨ Installation complete!")


if __name__ == "__main__":
    main()
