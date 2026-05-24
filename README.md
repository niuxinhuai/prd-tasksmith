# PRD Tasksmith

[中文文档](README.zh-CN.md)

Turn a PRD, feature request, or meeting note into developer-ready task cards.

PRD Tasksmith is local-first: without an API key it uses deterministic rules to produce a useful draft; with `AI_API_KEY` it can polish the result through any OpenAI-compatible Chat Completions endpoint.

## Features

- Extracts goals, owner hints, acceptance criteria, risks, and follow-up questions.
- Supports Markdown and JSON output.
- Reads from a file or stdin.
- Works with OpenAI-compatible providers through `AI_BASE_URL`, `AI_MODEL`, and `AI_API_KEY`.
- Ships with tests and GitHub Actions CI.

## Install

```bash
python3 -m pip install -e .
```

## Usage

```bash
prd-tasksmith examples/sample_prd.md
prd-tasksmith examples/sample_prd.md --format json
cat requirement.md | prd-tasksmith -
```

Use AI polishing:

```bash
export AI_API_KEY="your-key"
export AI_MODEL="gpt-4o-mini"
prd-tasksmith examples/sample_prd.md --ai --output TASKS.md
```

## Configuration

- `AI_API_KEY`: API key for the model provider.
- `AI_BASE_URL`: OpenAI-compatible base URL. Defaults to `https://api.openai.com/v1`.
- `AI_MODEL`: model name. Defaults to `gpt-4o-mini`.

CLI flags `--model` and `--base-url` override the environment for one run.

## Development

```bash
python3 -m pip install -e .
python3 -m unittest discover -s tests
```

## License

MIT
