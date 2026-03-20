#!/usr/bin/env python3
"""
Skill Installer for knowledge2skills

Installs a generated skill into ~/.stepfun/skills/ directory.
Handles validation, conflict detection, and optional backup.

Usage:
    python3 install_skill.py <skill_dir> [--target <target_dir>] [--force]
"""

import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime


DEFAULT_TARGET = Path.home() / ".agents" / "skills"


def validate_skill(skill_dir: Path) -> list:
    """Validate skill directory structure. Returns list of errors."""
    errors = []

    if not skill_dir.is_dir():
        errors.append(f"Not a directory: {skill_dir}")
        return errors

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("Missing SKILL.md")
        return errors

    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter
    if not content.startswith("---"):
        errors.append("SKILL.md missing YAML frontmatter")
    else:
        parts = content.split("---", 2)
        if len(parts) < 3:
            errors.append("SKILL.md frontmatter not properly closed")
        else:
            fm = parts[1]
            if "name:" not in fm:
                errors.append("SKILL.md frontmatter missing 'name' field")
            if "description:" not in fm:
                errors.append("SKILL.md frontmatter missing 'description' field")

    return errors


def install_skill(skill_dir: str, target_dir: str = None, force: bool = False) -> bool:
    """
    Install a skill directory to the target location.
    Returns True on success.
    """
    skill_path = Path(skill_dir).resolve()
    target = Path(target_dir).resolve() if target_dir else DEFAULT_TARGET
    skill_name = skill_path.name
    dest = target / skill_name
    backup_path = None
    staging_path = target / f".{skill_name}_tmp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Validate
    errors = validate_skill(skill_path)
    if errors:
        print("Validation errors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return False

    # Ensure target directory exists
    target.mkdir(parents=True, exist_ok=True)

    # Handle existing skill
    if dest.exists():
        if not force:
            print(f"Skill '{skill_name}' already exists at {dest}", file=sys.stderr)
            print("Use --force to overwrite", file=sys.stderr)
            return False
        else:
            # Backup existing
            backup_name = f"{skill_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = target / backup_name
            shutil.move(str(dest), str(backup_path))
            print(f"Backed up existing skill to: {backup_path}", file=sys.stderr)

    try:
        if staging_path.exists():
            shutil.rmtree(staging_path)
        shutil.copytree(str(skill_path), str(staging_path))
        shutil.move(str(staging_path), str(dest))
        print(f"Installed skill '{skill_name}' to: {dest}", file=sys.stderr)
        return True
    except Exception as exc:
        if staging_path.exists():
            shutil.rmtree(staging_path, ignore_errors=True)
        if backup_path and backup_path.exists() and not dest.exists():
            shutil.move(str(backup_path), str(dest))
            print(f"Restored previous skill from backup after failure: {dest}", file=sys.stderr)
        print(f"Installation failed: {exc}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Install skill to ~/.agents/skills/")
    parser.add_argument("skill_dir", help="Path to the skill directory to install")
    parser.add_argument("--target", "-t", help=f"Target directory (default: {DEFAULT_TARGET})")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing skill")
    args = parser.parse_args()

    success = install_skill(args.skill_dir, args.target, args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
