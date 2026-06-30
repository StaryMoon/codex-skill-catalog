import json
import tempfile
import unittest
from pathlib import Path

from codex_skill_catalog.render import render_html, render_markdown
from codex_skill_catalog.scanner import scan_catalog


class CatalogTest(unittest.TestCase):
    def test_scan_skill_root_and_render_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "skills"
            skill = root / "paper-helper"
            refs = skill / "references"
            refs.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "# Paper Helper\n\nUse when summarizing AI papers for a daily briefing.\n",
                encoding="utf-8",
            )
            config = Path(temp_dir) / "config.toml"
            config.write_text("[model]\nname = 'gpt-test'\n[mcp_servers.demo]\n", encoding="utf-8")

            catalog = scan_catalog([root], config_path=config)
            markdown = render_markdown(catalog)

            self.assertEqual(len(catalog.skills), 1)
            self.assertEqual(catalog.skills[0].name, "paper-helper")
            self.assertTrue(catalog.skills[0].has_references)
            self.assertIn("mcp_servers.demo", catalog.config_sections)
            self.assertIn("Paper Helper", markdown)
            self.assertIn("<table>", render_html(catalog))

    def test_json_output_is_serializable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            catalog = scan_catalog([Path(temp_dir) / "missing-root"])
            payload = json.loads(catalog.to_json())
            self.assertEqual(payload["skills"], [])
            self.assertTrue(payload["warnings"])

    def test_frontmatter_only_skill_uses_metadata_fallbacks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "skills"
            skill = root / "social-action-review"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: Social Action Review\n"
                "description: Use when reviewing approval-gated social posting skills.\n"
                "---\n",
                encoding="utf-8",
            )

            catalog = scan_catalog([root])

            self.assertEqual(catalog.skills[0].title, "Social Action Review")
            self.assertEqual(
                catalog.skills[0].description,
                "Use when reviewing approval-gated social posting skills.",
            )
            self.assertEqual(
                catalog.skills[0].trigger_hint,
                "Use when reviewing approval-gated social posting skills.",
            )


if __name__ == "__main__":
    unittest.main()
