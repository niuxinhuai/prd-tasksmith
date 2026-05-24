# PRD Tasksmith

把一段 PRD、需求说明或会议纪要，整理成可执行的开发任务卡。

它默认使用本地规则生成结构化草稿；配置 `AI_API_KEY` 后，会调用 OpenAI-compatible Chat Completions 接口做增强润色。适合开源项目、外包协作、AI 编程前的需求拆解。

## 特性

- 从 Markdown / 纯文本 PRD 中提取目标、模块、接口、验收标准和风险
- 输出面向开发的任务卡，方便贴到 GitHub Issue、Linear、飞书文档
- 不绑定具体模型厂商：支持 `AI_BASE_URL`、`AI_MODEL`、`AI_API_KEY`
- 无第三方依赖，Python 标准库即可运行

## 快速开始

```bash
python3 -m prd_tasksmith examples/sample_prd.md
```

启用 AI 增强：

```bash
export AI_API_KEY="your-key"
export AI_MODEL="gpt-4o-mini"
python3 -m prd_tasksmith examples/sample_prd.md --ai --output TASKS.md
```

## 输出示例

```markdown
# Implementation Task Cards

## Task 1: 用户登录态异常提示
- Goal: ...
- Owner hint: frontend / app
- Acceptance:
  - ...
- Risks:
  - ...
```

## 环境变量

- `AI_API_KEY`: 模型服务 API Key
- `AI_BASE_URL`: 默认 `https://api.openai.com/v1`
- `AI_MODEL`: 默认 `gpt-4o-mini`

## License

MIT
