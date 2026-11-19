#!/usr/bin/env python3
"""Build this repository's test copy of a Home Assistant integration.

Takes the integration from a Home Assistant release, applies patches/*.patch in
order, adds the files in extras/, generates translations and writes the result
to custom_components/<domain>/ with a manifest version tied to the release.

Usage: tools/build.py --tag 2026.11.2 [--build 1]
Config: testbuild.json in the repository root, e.g.
  {"domain": "go2rtc", "repository": "owner/ha-go2rtc-homekit"}
"""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
HA_REPO = "https://github.com/home-assistant/core.git"


def run(*cmd: str, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def checkout(tag: str, domain: str, dest: Path) -> None:
    """Fetch only what the build needs from the release."""
    run("git", "clone", "--quiet", "--depth", "1", "--filter=blob:none",
        "--no-checkout", "--branch", tag, HA_REPO, str(dest))
    run("git", "sparse-checkout", "set", "--no-cone",
        f"/homeassistant/components/{domain}/",
        "/homeassistant/components/*/strings.json",
        "/homeassistant/strings.json",
        "/script/",
        "/requirements_all.txt",  # the translation script checks it exists
        cwd=dest)
    run("git", "checkout", "--quiet", tag, cwd=dest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True, help="Home Assistant release, e.g. 2026.11.2")
    parser.add_argument("--build", type=int, default=1, help="build number for this release")
    args = parser.parse_args()

    config = json.loads((ROOT / "testbuild.json").read_text())
    domain = config["domain"]
    with tempfile.TemporaryDirectory() as tmp:
        ha = Path(tmp) / "core"
        checkout(args.tag, domain, ha)
        component = ha / "homeassistant/components" / domain

        for patch in sorted((ROOT / "patches").glob("*.patch")):
            run("git", "apply", "--verbose", "--directory",
                f"homeassistant/components/{domain}", str(patch), cwd=ha)
        extras = ROOT / "extras"
        if extras.is_dir():
            shutil.copytree(extras, component, dirs_exist_ok=True)

        # Custom integrations do not get core's generated translations
        run("python3", "-m", "script.translations", "develop",
            "--integration", domain, cwd=ha)

        manifest_path = component / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        # The Marketplace requires a version, matching the release tag
        manifest["version"] = f"{args.tag}.{args.build}"
        # Point users at this repository, not Home Assistant, for this build
        repo_url = f"https://github.com/{config['repository']}"
        manifest["documentation"] = repo_url
        manifest["issue_tracker"] = f"{repo_url}/issues"
        manifest["codeowners"] = [f"@{config['repository'].split('/')[0]}"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

        out = ROOT / "custom_components" / domain
        shutil.rmtree(out, ignore_errors=True)
        shutil.copytree(component, out, ignore=shutil.ignore_patterns("__pycache__"))

    hacs_path = ROOT / "hacs.json"
    hacs = json.loads(hacs_path.read_text())
    hacs["homeassistant"] = args.tag
    hacs_path.write_text(json.dumps(hacs, indent=2) + "\n")
    print(f"built {domain} {manifest['version']}")


if __name__ == "__main__":
    main()
