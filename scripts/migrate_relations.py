#!/usr/bin/env python3
"""Migrate all \\relation{a}{b}{c} calls to \\relation{a}{b}{c}{true}."""
import re
import sys
from pathlib import Path


def migrate_file(path: Path) -> int:
    content = path.read_text(encoding="utf-8")
    # Match \relation{...}{...}{...} that do NOT already have a 4th {arg}
    pattern = r'(\\relation\{[^}]+\}\{[^}]+\}\{[^}]+\})(?!\{)'
    new_content, count = re.subn(pattern, r'\1{true}', content)
    if count > 0:
        path.write_text(new_content, encoding="utf-8")
    return count


def main():
    root = Path(__file__).parent.parent
    total = 0
    for tree_file in sorted(root.rglob("*.tree")):
        count = migrate_file(tree_file)
        if count > 0:
            print(f"  {tree_file.relative_to(root)}: {count} relations migrated")
            total += count
    print(f"\nTotal: {total} relations migrated")


if __name__ == "__main__":
    main()
