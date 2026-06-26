from __future__ import annotations

from datetime import datetime, timezone
from html import escape
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


def render_html(catalog: Catalog, title: str = "Codex Skill Catalog") -> str:
    warning_count = sum(len(skill.warnings) for skill in catalog.skills) + len(catalog.warnings)
    rows = "\n".join(_skill_html_row(skill) for skill in catalog.skills)
    config_sections = "\n".join(
        f"<li><code>{escape(section)}</code></li>" for section in catalog.config_sections
    )
    workspace_warnings = "\n".join(
        f"<li>{escape(warning)}</li>" for warning in catalog.warnings
    )
    details = "\n".join(_skill_html_card(skill) for skill in catalog.skills)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #f6f8fb;
      --panel: #ffffff;
      --ink: #172033;
      --muted: #64748b;
      --line: #dbe4ee;
      --accent: #2563eb;
      --warn: #b45309;
    }}
    body {{
      margin: 0;
      padding: 32px 20px 64px;
      background: var(--bg);
      color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    main {{ max-width: 1120px; margin: 0 auto; }}
    h1 {{ font-size: 2.2rem; margin: 0 0 8px; letter-spacing: -0.04em; }}
    h2 {{ margin-top: 34px; letter-spacing: -0.025em; }}
    .muted {{ color: var(--muted); }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin: 24px 0;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 18px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }}
    .metric {{ font-size: 1.8rem; font-weight: 750; }}
    .label {{ color: var(--muted); font-size: 0.9rem; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 10px;
      overflow: hidden;
    }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; }}
    th {{ color: var(--muted); font-size: 0.86rem; }}
    code {{ background: rgba(37, 99, 235, 0.10); color: var(--accent); padding: 2px 5px; border-radius: 5px; }}
    .skill-card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 16px 18px; margin: 12px 0; }}
    .warning {{ color: var(--warn); }}
    @media (prefers-color-scheme: dark) {{
      :root {{ --bg: #0f172a; --panel: #111827; --ink: #e5e7eb; --muted: #94a3b8; --line: #334155; --accent: #93c5fd; --warn: #fbbf24; }}
      .card {{ box-shadow: none; }}
    }}
  </style>
</head>
<body>
<main>
  <h1>{escape(title)}</h1>
  <p class="muted">Generated: <code>{generated}</code></p>
  <section class="cards">
    <div class="card"><div class="metric">{len(catalog.roots)}</div><div class="label">skill roots</div></div>
    <div class="card"><div class="metric">{len(catalog.skills)}</div><div class="label">skills found</div></div>
    <div class="card"><div class="metric">{len(catalog.config_sections)}</div><div class="label">config sections</div></div>
    <div class="card"><div class="metric">{warning_count}</div><div class="label">warnings</div></div>
  </section>
  <p>Config path: <code>{escape(catalog.config_path or "-")}</code></p>
  <h2>Skills</h2>
  <table>
    <thead>
      <tr><th>Skill</th><th>Title</th><th>References</th><th>Lines</th><th>Warnings</th></tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
  <h2>Config Sections</h2>
  <ul>{config_sections or "<li class='muted'>No sections detected.</li>"}</ul>
  <h2>Workspace Warnings</h2>
  <ul>{workspace_warnings or "<li class='muted'>No workspace-level warnings.</li>"}</ul>
  <h2>Detailed Notes</h2>
  {details}
  <h2>Privacy Notes</h2>
  <ul>
    <li>This report lists local skill metadata and config section names only.</li>
    <li>It does not print tokens, API keys, cookies, auth files, or secret values.</li>
    <li>Review generated reports before publishing because local paths may reveal workspace names.</li>
  </ul>
</main>
</body>
</html>
"""


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


def _skill_html_row(skill: SkillEntry) -> str:
    warning_text = str(len(skill.warnings))
    if skill.warnings:
        warning_text = f"<span class='warning'>{warning_text}</span>"
    return (
        "<tr>"
        f"<td><code>{escape(skill.name)}</code></td>"
        f"<td>{escape(skill.title)}</td>"
        f"<td>{'yes' if skill.has_references else 'no'}</td>"
        f"<td>{skill.line_count}</td>"
        f"<td>{warning_text}</td>"
        "</tr>"
    )


def _skill_html_card(skill: SkillEntry) -> str:
    warnings = "".join(f"<li>{escape(warning)}</li>" for warning in skill.warnings)
    warning_block = (
        f"<p class='warning'>Warnings</p><ul>{warnings}</ul>"
        if skill.warnings
        else "<p class='muted'>No warnings.</p>"
    )
    return f"""<article class="skill-card">
  <h3><code>{escape(skill.name)}</code></h3>
  <p><strong>Title:</strong> {escape(skill.title)}</p>
  <p><strong>Path:</strong> <code>{escape(skill.path)}</code></p>
  <p><strong>Description:</strong> {escape(skill.description or "-")}</p>
  <p><strong>Trigger hint:</strong> {escape(skill.trigger_hint or "-")}</p>
  <p><strong>Reference folders:</strong> {'yes' if skill.has_references else 'no'} · <strong>Lines:</strong> {skill.line_count}</p>
  {warning_block}
</article>"""


def _cell(text: str) -> str:
    return text.replace("|", "\\|").strip()
