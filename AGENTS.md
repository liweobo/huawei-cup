# Huawei Cup 2026

本仓库分为两部分：

- Skill 本体：[`skill/`](skill/)
- 开发与验证：[`development/`](development/)

修改 Skill 前先读 [`skill/SKILL.md`](skill/SKILL.md)。运行结构 smoke、回归和 Python 测试见 [`development/README.md`](development/README.md)。

Skill 编辑后的最低验证：

```text
python development/harness/smoke_test.py
```

Python 编辑后的最低验证：

```text
pytest -q
```

测试和真实运行输出只能写入 `.tmp`、pytest `tmp_path`、系统临时目录或明确的开发 artifacts 目录；不得写入 Skill 本体或冻结历史 fixture。
