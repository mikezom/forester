#!/usr/bin/env python3
"""Validate core consistency rules for this Forester project."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
TRANSCLUDE_PATTERN = re.compile(r"\\transclude(?:-unexpanded)?\{([^}]+)\}")
RELATION_PATTERN = re.compile(r"\\relation\{([^}]+)\}\{([^}]+)\}\{([^}]+)\}")
TAXON_PATTERN = re.compile(r"\\taxon\{([^}]+)\}")
TITLE_PATTERN = re.compile(r"\\title\{")


@dataclass
class Finding:
    level: str
    path: Path
    line: int
    message: str


def infer_project_root(start: Path) -> Optional[Path]:
    """Find the nearest directory that looks like this Forester project."""
    for candidate in (start, *start.parents):
        if (candidate / "forest.toml").exists() and (candidate / "trees").is_dir():
            return candidate
    return None


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def is_external_ref(target: str) -> bool:
    prefixes = ("http://", "https://", "mailto:", "vscode://", "#")
    return target.startswith(prefixes)


def normalize_local_ref(target: str) -> str:
    clean = target.strip().split("#", 1)[0].split("?", 1)[0]
    if not clean:
        return ""

    segments = [seg for seg in clean.split("/") if seg]
    if segments:
        clean = segments[-1]
        if clean in {"index.xml", "index.html"} and len(segments) >= 2:
            clean = segments[-2]

    for suffix in (".tree", ".xml", ".html"):
        if clean.endswith(suffix):
            clean = clean[: -len(suffix)]
    return clean


def find_unescaped_percent(text: str) -> Optional[int]:
    for idx, char in enumerate(text):
        if char != "%":
            continue
        if idx == 0 or text[idx - 1] != "\\":
            return idx
    return None


def collect_tree_ids(tree_files: Iterable[Path]) -> tuple[dict[str, Path], dict[str, list[Path]]]:
    mapping: dict[str, Path] = {}
    duplicates: dict[str, list[Path]] = {}
    for path in tree_files:
        tree_id = path.stem
        if tree_id in mapping:
            duplicates.setdefault(tree_id, [mapping[tree_id]]).append(path)
        else:
            mapping[tree_id] = path
    return mapping, duplicates


def validate(project_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    trees_dir = project_root / "trees"
    tree_files = sorted(trees_dir.rglob("*.tree"))

    id_map, duplicates = collect_tree_ids(tree_files)
    for dup_id, paths in sorted(duplicates.items()):
        findings.append(
            Finding(
                "ERROR",
                paths[0],
                1,
                f"Duplicate tree ID '{dup_id}' used by multiple files.",
            )
        )

    for path in tree_files:
        content = path.read_text(encoding="utf-8", errors="replace")

        if not TITLE_PATTERN.search(content):
            findings.append(Finding("ERROR", path, 1, "Missing \\title{...}."))

        percent_idx = find_unescaped_percent(content)
        if percent_idx is not None:
            findings.append(
                Finding(
                    "WARN",
                    path,
                    line_number(content, percent_idx),
                    "Found unescaped '%' (use \\%).",
                )
            )

        taxon_match = TAXON_PATTERN.search(content)
        if taxon_match:
            taxon = taxon_match.group(1).strip()
            if taxon and taxon[0].islower():
                findings.append(
                    Finding(
                        "WARN",
                        path,
                        line_number(content, taxon_match.start(1)),
                        f"Taxon '{taxon}' starts with lowercase; prefer capitalization.",
                    )
                )

        for match in LINK_PATTERN.finditer(content):
            raw_target = match.group(1).strip()
            if is_external_ref(raw_target):
                continue
            target = normalize_local_ref(raw_target)
            if target and target not in id_map:
                findings.append(
                    Finding(
                        "ERROR",
                        path,
                        line_number(content, match.start(1)),
                        f"Dangling local link target '{raw_target}'.",
                    )
                )

        for match in TRANSCLUDE_PATTERN.finditer(content):
            target = match.group(1).strip()
            if target.startswith("\\"):
                continue
            if target and target not in id_map:
                findings.append(
                    Finding(
                        "ERROR",
                        path,
                        line_number(content, match.start(1)),
                        f"Dangling transclusion target '{target}'.",
                    )
                )

        for match in RELATION_PATTERN.finditer(content):
            source = match.group(1).strip()
            relation = match.group(2).strip()
            target = match.group(3).strip()
            rel_line = line_number(content, match.start(0))

            if source and source not in id_map:
                findings.append(Finding("ERROR", path, rel_line, f"Relation source '{source}' does not exist."))
            if target and target not in id_map:
                findings.append(Finding("ERROR", path, rel_line, f"Relation target '{target}' does not exist."))
            if not relation:
                findings.append(Finding("ERROR", path, rel_line, "Relation label is empty."))
            elif " " in relation:
                findings.append(
                    Finding(
                        "WARN",
                        path,
                        rel_line,
                        f"Relation label '{relation}' contains spaces; prefer hyphenated labels.",
                    )
                )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Forester tree consistency.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root (defaults to current working directory).",
    )
    parser.add_argument(
        "--warnings-as-errors",
        action="store_true",
        help="Exit non-zero when warnings are present.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when errors are present (and with --warnings-as-errors for warnings).",
    )
    args = parser.parse_args()

    root = infer_project_root(args.root.resolve())
    if root is None:
        print("ERROR: Could not find project root containing forest.toml and trees/.")
        return 2

    findings = validate(root)
    errors = [f for f in findings if f.level == "ERROR"]
    warnings = [f for f in findings if f.level == "WARN"]

    for finding in findings:
        rel_path = finding.path.relative_to(root)
        print(f"{finding.level}: {rel_path}:{finding.line} {finding.message}")

    checked_count = len(list((root / "trees").rglob("*.tree")))
    print(f"Checked {checked_count} tree files in {root}.")
    print(f"Errors: {len(errors)} | Warnings: {len(warnings)}")

    if args.strict and errors:
        return 1
    if args.strict and args.warnings_as_errors and warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
