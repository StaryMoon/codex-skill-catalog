from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional


HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
TRIGGER_RE = re.compile(r"\b(use|trigger|when|invoke|call)\b", re.IGNORECASE)
FRONTMATTER_RE = re.compile(r"\A---\s*\n(?P<body>.*?)\n---\s*(?:\n|\Z)", re.DOTALL)


@dataclass
class SkillEntry:
    name: str
    path: str
    title: str
    description: str
    trigger_hint: str = ""
    line_count: int = 0
    has_references: bool = False
    warnings: List[str] = field(default_factory=list)


@dataclass
class Catalog:
    roots: List[str]
    skills: List[SkillEntry]
    config_path: str = ""
    config_sections: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


def scan_catalog(
    roots: Iterable[str | Path],
    config_path: str | Path = "~/.codex/config.toml",
) -> Catalog:
    expanded_roots = [str(Path(os.path.expanduser(str(root))).resolve()) for root in roots]
    warnings: List[str] = []
    skills: List[SkillEntry] = []

    for root_text in expanded_roots:
        root = Path(root_text)
        if not root.exists():
            warnings.append(f"Skill root does not exist: {root}")
            continue
        if not root.is_dir():
            warnings.append(f"Skill root is not a directory: {root}")
            continue
        skills.extend(_scan_root(root))

    seen: Dict[str, int] = {}
    for entry in skills:
        seen[entry.name] = seen.get(entry.name, 0) + 1
    for entry in skills:
        if seen[entry.name] > 1:
            entry.warnings.append("Duplicate skill directory name across roots")

    config = Path(os.path.expanduser(str(config_path)))
    sections = _read_toml_sections(config)
    if config.exists() and not sections:
        warnings.append(f"Config exists but no TOML sections were detected: {config}")

    return Catalog(
        roots=[_display_path(Path(root)) for root in expanded_roots],
        skills=sorted(skills, key=lambda item: item.name.lower()),
        config_path=_display_path(config),
        config_sections=sections,
        warnings=warnings,
    )


def _scan_root(root: Path) -> List[SkillEntry]:
    entries: List[SkillEntry] = []
    for skill_file in sorted(root.glob("*/SKILL.md")):
        entries.append(_read_skill(skill_file))
    return entries


def _read_skill(skill_file: Path) -> SkillEntry:
    warnings: List[str] = []
    try:
        text = skill_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = skill_file.read_text(encoding="utf-8", errors="replace")
        warnings.append("SKILL.md had invalid UTF-8 bytes and was decoded with replacement")

    body_text = _strip_frontmatter(text)
    frontmatter_name = _frontmatter_scalar(text, "name")
    frontmatter_description = _frontmatter_scalar(text, "description")
    title = _first_heading(body_text) or frontmatter_name or skill_file.parent.name
    description = _first_paragraph(body_text) or frontmatter_description
    trigger_hint = _first_triggerish_line(body_text) or frontmatter_description
    has_references = any(
        child.name.lower() in {"references", "templates", "examples", "scripts"}
        for child in skill_file.parent.iterdir()
        if child.is_dir()
    )
    if not description:
        warnings.append("No plain-language description paragraph detected")
    if not trigger_hint:
        warnings.append("No obvious trigger/use-case line detected")

    return SkillEntry(
        name=skill_file.parent.name,
        path=_display_path(skill_file),
        title=title,
        description=description,
        trigger_hint=trigger_hint,
        line_count=len(text.splitlines()),
        has_references=has_references,
        warnings=warnings,
    )


def _first_heading(text: str) -> str:
    match = HEADING_RE.search(text)
    return match.group(1).strip() if match else ""


def _strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


def _frontmatter_scalar(text: str, key: str) -> str:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return ""
    for raw_line in match.group("body").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        field, value = stripped.split(":", 1)
        if field.strip() == key:
            return value.strip().strip("\"'")
    return ""


def _first_paragraph(text: str) -> str:
    paragraphs = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    for block in paragraphs:
        if block.startswith("#"):
            continue
        cleaned = _clean_markdown_line(" ".join(line.strip() for line in block.splitlines()))
        if cleaned:
            return cleaned[:320]
    return ""


def _first_triggerish_line(text: str) -> str:
    for line in text.splitlines():
        cleaned = _clean_markdown_line(line.strip())
        if not cleaned:
            continue
        if TRIGGER_RE.search(cleaned):
            return cleaned[:240]
    return ""


def _clean_markdown_line(line: str) -> str:
    line = re.sub(r"^[-*]\s+", "", line)
    line = re.sub(r"`([^`]+)`", r"\1", line)
    line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def _read_toml_sections(path: Path) -> List[str]:
    if not path.exists():
        return []
    sections: List[str] = []
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if line.startswith("[") and line.endswith("]"):
            sections.append(line.strip("[]"))
    return sections


def _display_path(path: Path) -> str:
    text = str(path)
    home = str(Path.home())
    if text == home:
        return "~"
    if text.startswith(home + os.sep):
        return "~" + text[len(home) :]
    return text
