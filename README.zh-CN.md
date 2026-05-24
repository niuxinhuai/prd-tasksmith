# PRD Tasksmith

[![CI](https://github.com/niuxinhuai/prd-tasksmith/actions/workflows/ci.yml/badge.svg)](https://github.com/niuxinhuai/prd-tasksmith/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

[English](README.md)

把 PRD、需求说明或会议纪要整理成开发任务卡。

PRD Tasksmith 是本地优先工具：没有 API Key 时会用规则生成可用草稿；配置 `AI_API_KEY` 后，可以通过 OpenAI-compatible Chat Completions 接口做增强润色。

## 功能

- 提取目标、owner 建议、验收标准、风险和待确认问题
- 支持任务卡、GitHub issue 草稿、Linear 导入草稿、Markdown 表格和 JSON 输出
- 支持从文件或 stdin 读取
- 支持 `AI_BASE_URL`、`AI_MODEL`、`AI_API_KEY`，不绑定具体模型厂商
- 自带 unittest 测试和 GitHub Actions CI

## 安装

在包发布到 PyPI 之前，可以直接从 GitHub 安装：

```bash
pipx install git+https://github.com/niuxinhuai/prd-tasksmith.git
```

也可以使用 pip：

```bash
python3 -m pip install git+https://github.com/niuxinhuai/prd-tasksmith.git
```

本地开发安装：

```bash
python3 -m pip install -e .
```

也可以从最新 GitHub Release 下载 wheel 和 sdist： https://github.com/niuxinhuai/prd-tasksmith/releases/latest

## 使用

```bash
prd-tasksmith examples/sample_prd.md
prd-tasksmith examples/sample_prd.md --template github-issues
prd-tasksmith examples/sample_prd.md --template markdown-table
prd-tasksmith examples/sample_prd.md --format json
cat requirement.md | prd-tasksmith -
```

可以直接查看生成示例：[`examples/output.md`](examples/output.md) 和 [`examples/output.json`](examples/output.json)。

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

## 发布

推送 tag 后，GitHub Actions 会构建 Python 包并创建 GitHub Release。PyPI 发布默认关闭；若要发布到 PyPI，请先配置 Trusted Publishing，并设置仓库变量 `PUBLISH_TO_PYPI=true`，然后推送 tag：

```bash
git tag v0.1.0
git push origin v0.1.0
```

## License

MIT
