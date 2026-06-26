from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from .scanner import Catalog, SkillEntry


def render_markdown(catalog: Catalog, title: str = "Codex Skill Catalog") -> str:
    lines: List[str] = [
        f"# {title}",
        "",
        f"Generated: `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}`",
        "",
        "## Summary",
        "",
        f"- Skill roots scanned: **{len(catalog.roots)}**",
        f"- Skills found: **{len(catalog.skills)}**",
        f"- Config path: `{catalog.config_path or '-'}`",
        f"- Config sections detected: **{len(catalog.config_sections)}**",
        "",
    ]
    if catalog.warnings:
        lines.extend(["## Workspace Warnings", ""])
        lines.extend(f"- {warning}" for warning in catalog.warnings)
        lines.append("")

    if catalog.config_sections:
        lines.extend(["## Config Sections", ""])
        for section in catalog.config_sections:
            lines.append(f"- `{section}`")
        lines.append("")

    lines.extend(["## Skills", "", _skills_table(catalog.skills), ""])
    lines.extend(["## Detailed Notes", ""])
    for skill in catalog.skills:
        lines.extend(_skill_section(skill))
    lines.extend(
        [
            "## Privacy Notes",
            "",
            "- This report only lists local skill metadata and config section names.",
            "- It does not print tokens, API keys, cookies, auth files, or secret values.",
            "- Review generated reports before publishing because local paths may reveal usernames.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _skills_table(skills: List[SkillEntry]) -> str:
    rows = [
        "| Skill | Title | References | Lines | Warnings |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for skill in skills:
        rows.append(
            "| {name} | {title} | {refs} | {lines} | {warnings} |".format(
                name=f"`{skill.name}`",
                title=_cell(skill.title),
                refs="yes" if skill.has_references else "no",
                lines=skill.line_count,
                warnings=len(skill.warnings),
            )
        )
    return "\n".join(rows)


def _skill_section(skill: SkillEntry) -> List[str]:
    lines = [
        f"### `{skill.name}`",
        "",
        f"- Title: {skill.title}",
        f"- Path: `{skill.path}`",
        f"- Lines: {skill.line_count}",
        f"- Reference folders: {'yes' if skill.has_references else 'no'}",
    ]
    if skill.description:
        lines.append(f"- Description: {skill.description}")
    if skill.trigger_hint:
        lines.append(f"- Trigger hint: {skill.trigger_hint}")
    if skill.warnings:
        lines.append("- Warnings:")
        lines.extend(f"  - {warning}" for warning in skill.warnings)
    lines.append("")
    return lines


def _cell(text: str) -> str:
    return text.replace("|", "\\|").strip()
