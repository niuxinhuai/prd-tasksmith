import json
import unittest

from prd_tasksmith.__main__ import build_tasks, heuristic_plan, render_markdown


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


if __name__ == "__main__":
    unittest.main()
