import json
import os
import tempfile
import unittest

from prd_tasksmith.__main__ import build_tasks, heuristic_plan, render_markdown, write_task_files


class PrdTasksmithTest(unittest.TestCase):
    def test_build_tasks_skips_acceptance_as_tasks(self):
        text = """# Demo

## 需求
- Show a renewal banner
- Hide it for logged-out users

## 验收
- Banner appears for eligible users
"""
        plan = build_tasks(text)
        self.assertEqual(plan["title"], "Demo")
        self.assertEqual(len(plan["tasks"]), 2)
        self.assertEqual(plan["tasks"][0]["owner_hint"], "feature owner")

    def test_json_output(self):
        result = heuristic_plan("# Demo\n\n## 需求\n- 接口返回 expireTime", "json")
        data = json.loads(result)
        self.assertEqual(data["tasks"][0]["owner_hint"], "backend / service")

    def test_plain_label_acceptance_is_not_task(self):
        text = """# Demo
需求：
- 展示提醒条

验收：
- 提醒条出现
"""
        plan = build_tasks(text)
        self.assertEqual(len(plan["tasks"]), 1)
        self.assertEqual(plan["tasks"][0]["acceptance"], ["提醒条出现"])

    def test_markdown_table_template(self):
        plan = build_tasks("# Demo\n需求：\n- 展示提醒条")
        table = render_markdown(plan, template="markdown-table")
        self.assertIn("| ID | Task | Owner | Risks |", table)
        self.assertIn("| 1 | 展示提醒条 | frontend / app |", table)

    def test_write_task_files_creates_one_file_per_task(self):
        plan = build_tasks("# Demo\n需求：\n- 展示提醒条\n- 跳转续费页")
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_task_files(plan, tmp)
            names = sorted(os.path.basename(path) for path in paths)
        self.assertEqual(len(names), 2)
        self.assertTrue(names[0].startswith("01-"))


if __name__ == "__main__":
    unittest.main()
