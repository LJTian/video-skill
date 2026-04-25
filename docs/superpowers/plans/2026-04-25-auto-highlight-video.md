# 自动剪辑高光视频 Skill 实现计划

> **给代理执行者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法跟踪。

**目标：** 创建一个 `auto-highlight-video` skill 源码包，用 AI 决策高光片段，并用本地脚本校验和导出多个短视频。

**架构：** `SKILL.md` 定义高光剪辑工作流和 AI 评分标准；`references/highlight-schema.md` 定义高光 JSON 格式；`scripts/validate_highlights.py` 做结构和时间码校验；`scripts/export_clips.py` 生成或执行 `ffmpeg` 导出命令。测试用 Python `unittest` 覆盖脚本行为。

**技术栈：** Codex skill Markdown、Python 3 标准库、`ffmpeg`/`ffprobe` 命令行。

---

### Task 1: 校验脚本

**Files:**
- Create: `tests/test_validate_highlights.py`
- Create: `scripts/validate_highlights.py`

- [ ] **Step 1: Write the failing test**

测试合法清单通过、缺字段失败、重复 id 失败、时长异常失败、重叠失败。

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_validate_highlights -v`
Expected: FAIL because `scripts.validate_highlights` does not exist.

- [ ] **Step 3: Write minimal implementation**

实现 JSON 读取、`HH:MM:SS(.mmm)` 和秒数解析、字段校验、分数和时间范围校验、重叠检测、CLI 退出码。

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_validate_highlights -v`
Expected: PASS.

### Task 2: 导出脚本

**Files:**
- Create: `tests/test_export_clips.py`
- Create: `scripts/export_clips.py`

- [ ] **Step 1: Write the failing test**

测试 dry-run 输出 `ffmpeg` 命令、安全文件名、默认 copy 模式、可选转码模式。

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_export_clips -v`
Expected: FAIL because `scripts.export_clips` does not exist.

- [ ] **Step 3: Write minimal implementation**

实现读取高光 JSON、构造 `ffmpeg` 参数、dry-run 打印命令、非 dry-run 调用 `subprocess.run`。

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_export_clips -v`
Expected: PASS.

### Task 3: Skill 文档和 schema

**Files:**
- Create: `SKILL.md`
- Create: `references/highlight-schema.md`
- Modify: `tests/test_validate_highlights.py`

- [ ] **Step 1: Write the failing test**

把 `references/highlight-schema.md` 中的示例 JSON 保存为临时文件并用校验器验证。

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest -v`
Expected: FAIL because `references/highlight-schema.md` does not exist.

- [ ] **Step 3: Write minimal implementation**

编写 `SKILL.md`、schema 文档和示例 JSON，确保 skill 要求先校验再导出。

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest -v`
Expected: PASS.

### Task 4: Skill 验证

**Files:**
- Existing: `SKILL.md`
- Existing: `scripts/*.py`
- Existing: `references/highlight-schema.md`

- [ ] **Step 1: Run tests**

Run: `python3 -m unittest -v`
Expected: PASS.

- [ ] **Step 2: Run skill validator**

Run: `python3 /Users/ljtian/.codex/skills/.system/skill-creator/scripts/quick_validate.py .`
Expected: PASS for frontmatter and naming.

- [ ] **Step 3: Run script CLI smoke checks**

Run: `python3 scripts/validate_highlights.py <sample-json>`
Expected: PASS for the schema sample.

Run: `python3 scripts/export_clips.py <video> <sample-json> --dry-run`
Expected: prints `ffmpeg` commands without writing output.
