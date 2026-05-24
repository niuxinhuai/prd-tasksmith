# PRD Tasksmith

[English](README.md)

把 PRD、需求说明或会议纪要整理成开发任务卡。

PRD Tasksmith 是本地优先工具：没有 API Key 时会用规则生成可用草稿；配置 `AI_API_KEY` 后，可以通过 OpenAI-compatible Chat Completions 接口做增强润色。

## 功能

- 提取目标、owner 建议、验收标准、风险和待确认问题
- 支持 Markdown 和 JSON 输出
- 支持从文件或 stdin 读取
- 支持 `AI_BASE_URL`、`AI_MODEL`、`AI_API_KEY`，不绑定具体模型厂商
- 自带 unittest 测试和 GitHub Actions CI

## 安装

```bash
python3 -m pip install -e .
```

## 使用

```bash
prd-tasksmith examples/sample_prd.md
prd-tasksmith examples/sample_prd.md --format json
cat requirement.md | prd-tasksmith -
```

启用 AI 润色：

```bash
export AI_API_KEY="your-key"
export AI_MODEL="gpt-4o-mini"
prd-tasksmith examples/sample_prd.md --ai --output TASKS.md
```

## 配置

- `AI_API_KEY`：模型服务 API Key
- `AI_BASE_URL`：OpenAI-compatible 地址，默认 `https://api.openai.com/v1`
- `AI_MODEL`：模型名称，默认 `gpt-4o-mini`

也可以用 `--model` 和 `--base-url` 覆盖单次运行配置。

## 开发

```bash
python3 -m pip install -e .
python3 -m unittest discover -s tests
```

## License

MIT
