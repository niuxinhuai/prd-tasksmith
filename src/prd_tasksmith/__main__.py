import argparse
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.request

from . import __version__

DEFAULT_MODEL = "gpt-4o-mini"


def read_text(path):
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_text(path, text):
    if not path:
        print(text)
        return
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def safe_slug(text):
    slug = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text.strip(), flags=re.UNICODE)
    slug = re.sub(r"-+", "-", slug).strip("-").lower()
    return slug or "task"


def bullet_lines(text):
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if re.match(r"^[-*]\s+", line):
            lines.append(re.sub(r"^[-*]\s+", "", line))
        elif re.match(r"^\d+[.)]\s+", line):
            lines.append(re.sub(r"^\d+[.)]\s+", "", line))
    return lines


def normalize_bullets(lines):
    seen = []
    for line in lines:
        item = re.sub(r"\s+", " ", line).strip()
        if item and item not in seen:
            seen.append(item)
    return seen


def find_section(text, names):
    pattern = r"(?ims)^#+\s*(" + "|".join(re.escape(name) for name in names) + r").*?\n(.*?)(?=^#+\s|\Z)"
    match = re.search(pattern, text)
    if match:
        return match.group(2).strip()
    label_pattern = r"(?ims)^(" + "|".join(re.escape(name) for name in names) + r")[:：]\s*\n(.*?)(?=^[\w\u4e00-\u9fff ]{2,20}[:：]\s*$|^#+\s|\Z)"
    label_match = re.search(label_pattern, text)
    return label_match.group(2).strip() if label_match else ""


def infer_owner(line):
    lowered = line.lower()
    if any(word in lowered for word in ["接口", "api", "server", "backend", "数据库"]):
        return "backend / service"
    if any(word in lowered for word in ["页面", "展示", "点击", "跳转", "按钮", "弹窗", "ui"]):
        return "frontend / app"
    if any(word in lowered for word in ["埋点", "统计", "track", "analytics"]):
        return "data / analytics"
    if any(word in lowered for word in ["测试", "验收", "case"]):
        return "qa"
    return "feature owner"


def risks_for(line):
    risks = []
    if any(word in line for word in ["登录", "权限", "未登录"]):
        risks.append("登录态和权限分支需要覆盖")
    if any(word in line for word in ["接口", "网络", "返回", "字段"]):
        risks.append("接口失败、字段缺失和兼容旧数据需要兜底")
    if any(word in line for word in ["跳转", "路由"]):
        risks.append("路由路径和参数需要联调确认")
    if any(word in line for word in ["时间", "过期", "倒计时", "expire"]):
        risks.append("时区、秒/毫秒单位和边界时间容易出错")
    return risks or ["需求边界不清时先补充验收样例"]


def build_tasks(text):
    title_match = re.search(r"(?m)^#\s+(.+)$", text)
    title = title_match.group(1).strip() if title_match else "Implementation Task Cards"
    requirement_text = find_section(text, ["需求", "功能", "Requirements", "Feature"]) or text
    acceptance_text = find_section(text, ["验收", "验收标准", "Acceptance", "AC"])
    requirements = normalize_bullets(bullet_lines(requirement_text) or [line.strip() for line in requirement_text.splitlines() if line.strip()][:6])
    acceptance = normalize_bullets(bullet_lines(acceptance_text))
    if acceptance:
        requirements = [item for item in requirements if item not in acceptance]
    tasks = []
    for index, item in enumerate(requirements, 1):
        tasks.append({
            "id": index,
            "title": item[:46],
            "goal": item,
            "owner_hint": infer_owner(item),
            "inputs_to_confirm": ["入口、接口字段、异常态和灰度范围"],
            "acceptance": acceptance[:4] or ["正常路径、边界路径、失败路径均可验证"],
            "risks": risks_for(item),
        })
    return {"title": title, "tasks": tasks, "acceptance": acceptance}


def render_markdown_table(plan):
    output = ["# Implementation Task Table", "", "| ID | Task | Owner | Risks |", "|---:|------|-------|-------|"]
    for task in plan["tasks"]:
        risks = "<br>".join(task["risks"])
        output.append("| %d | %s | %s | %s |" % (task["id"], task["title"], task["owner_hint"], risks))
    return "\n".join(output).rstrip() + "\n"


def render_github_issues(plan):
    output = ["# GitHub Issue Drafts", ""]
    for task in plan["tasks"]:
        output.extend([
            "## %s" % task["title"],
            "",
            "```markdown",
            "### Goal",
            task["goal"],
            "",
            "### Owner Hint",
            task["owner_hint"],
            "",
            "### Acceptance Criteria",
        ])
        output.extend("- [ ] %s" % item for item in task["acceptance"])
        output.extend(["", "### Risks"])
        output.extend("- %s" % item for item in task["risks"])
        output.extend(["```", ""])
    return "\n".join(output).rstrip() + "\n"


def render_task_issue(task):
    output = [
        "# %s" % task["title"],
        "",
        "## Goal",
        "",
        task["goal"],
        "",
        "## Owner Hint",
        "",
        task["owner_hint"],
        "",
        "## Acceptance Criteria",
        "",
    ]
    output.extend("- [ ] %s" % item for item in task["acceptance"])
    output.extend(["", "## Risks", ""])
    output.extend("- %s" % item for item in task["risks"])
    output.append("")
    return "\n".join(output)


def write_task_files(plan, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    paths = []
    for task in plan["tasks"]:
        filename = "%02d-%s.md" % (task["id"], safe_slug(task["title"]))
        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(render_task_issue(task))
        paths.append(path)
    return paths


def render_linear(plan):
    output = ["# Linear Import Draft", ""]
    for task in plan["tasks"]:
        output.append("- [%s] %s" % (task["owner_hint"], task["title"]))
        output.append("  - Goal: %s" % task["goal"])
        output.append("  - Acceptance: %s" % "; ".join(task["acceptance"]))
    return "\n".join(output).rstrip() + "\n"


def render_markdown(plan, template="task-cards"):
    if template == "markdown-table":
        return render_markdown_table(plan)
    if template == "github-issues":
        return render_github_issues(plan)
    if template == "linear":
        return render_linear(plan)
    output = ["# Implementation Task Cards", "", "## Source", "", "- Title: %s" % plan["title"], "- Generated by: prd-tasksmith", ""]
    for task in plan["tasks"]:
        output.extend([
            "## Task %d: %s" % (task["id"], task["title"]),
            "",
            "- Goal: %s" % task["goal"],
            "- Owner hint: %s" % task["owner_hint"],
            "- Inputs to confirm:",
        ])
        for item in task["inputs_to_confirm"]:
            output.append("  - %s" % item)
        output.extend([
            "- Acceptance:",
        ])
        for line in task["acceptance"]:
            output.append("  - %s" % line)
        output.append("- Risks:")
        for risk in task["risks"]:
            output.append("  - %s" % risk)
        output.append("")
    return "\n".join(output).rstrip() + "\n"


def heuristic_plan(text, output_format, template="task-cards"):
    plan = build_tasks(text)
    if output_format == "json":
        return json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
    return render_markdown(plan, template)


def call_ai(source, draft, model=None, base_url=None):
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        raise RuntimeError("AI_API_KEY is not set")
    base_url = (base_url or os.getenv("AI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
    model = model or os.getenv("AI_MODEL", DEFAULT_MODEL)
    prompt = """You are a senior product-engineering assistant.
Rewrite the draft into concise implementation task cards for developers.
Keep Markdown. Include goals, owners, risks, acceptance criteria, and questions.

PRD:
%s

Draft:
%s
""" % (source[:12000], draft[:12000])
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Return only Markdown."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base_url + "/chat/completions",
        data=data,
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError("AI request failed: %s" % exc)
    return body["choices"][0]["message"]["content"].strip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Turn a PRD into developer task cards.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
        Examples:
          python3 -m prd_tasksmith examples/sample_prd.md
          python3 -m prd_tasksmith PRD.md --ai --output TASKS.md
        """),
    )
    parser.add_argument("input", help="PRD file path, or '-' for stdin")
    parser.add_argument("--ai", action="store_true", help="Polish the local draft with an OpenAI-compatible model")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--template", choices=["task-cards", "github-issues", "linear", "markdown-table"], default="task-cards", help="Markdown template")
    parser.add_argument("--model", help="Override AI_MODEL for --ai")
    parser.add_argument("--base-url", help="Override AI_BASE_URL for --ai")
    parser.add_argument("--output", help="Write result to a file instead of stdout")
    parser.add_argument("--output-dir", help="Write one Markdown issue draft per task")
    parser.add_argument("--version", action="version", version="prd-tasksmith %s" % __version__)
    args = parser.parse_args(argv)

    source = read_text(args.input)
    plan = build_tasks(source)
    if args.output_dir:
        paths = write_task_files(plan, args.output_dir)
        sys.stdout.write("Wrote %d task file(s) to %s\n" % (len(paths), args.output_dir))
        return
    draft = json.dumps(plan, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else render_markdown(plan, args.template)
    result = call_ai(source, draft, args.model, args.base_url) if args.ai else draft
    write_text(args.output, result)


if __name__ == "__main__":
    main()
