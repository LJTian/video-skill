# 自动高光视频技能

**语言：** 简体中文 | [English](README.md)

用于从长视频、播客、课程、访谈、网络研讨会和带讲解录制内容中，
查找并导出高价值片段的 Codex 技能源码。

该技能使用 AI 进行编辑判断，并结合本地 Python 脚本完成确定性的校验、
字幕清理与 `ffmpeg` 执行。带时间戳的转录文本是高光选择的主要输入；
JSON 清单是 AI 决策与片段导出之间的契约。

## 能做什么

- 指导 Codex 获取 URL，或检查源视频与带时间戳的转录文本。
- 选择可独立观看的候选高光片段，通常每段 30-90 秒。
- 为每个候选片段评分，并记录原因、风险和剪辑说明。
- 在导出任何片段前校验高光清单。
- 使用 `ffmpeg` 导出片段，默认采用流拷贝；当需要更精确切点时可重编码。
- 渲染平台规格版本、生成视觉复核素材、导出合集视频，并生成可审阅发布文案资产。
- 校验导出媒体，并提供字幕、平台格式和凭据安全方面的指引。

## 仓库结构

```text
.
|-- SKILL.md
|-- references/
|   |-- highlight-schema.md
|   |-- output-verification.md
|   |-- platform-presets.md
|   |-- quality-review.md
|   `-- source-acquisition.md
|-- scripts/
|   |-- analyze_visual_signals.py
|   |-- clean_vtt.py
|   |-- export_compilation.py
|   |-- export_clips.py
|   |-- generate_publish_assets.py
|   |-- render_platform_clips.py
|   |-- review_clip_boundaries.py
|   `-- validate_highlights.py
`-- tests/
    |-- test_analyze_visual_signals.py
    |-- test_clean_vtt.py
    |-- test_export_compilation.py
    |-- test_export_clips.py
    |-- test_generate_publish_assets.py
    |-- test_render_platform_clips.py
    |-- test_skill_docs.py
    `-- test_validate_highlights.py
```

## 环境要求

- Python 3.10 或更新版本。
- 导出片段需要 `ffmpeg`。
- 推荐使用 `ffprobe` 进行视频检查。
- 当输入是公开视频 URL 时，推荐使用 `yt-dlp`。

这些 Python 脚本仅依赖标准库。

## 高光清单（Highlight Manifest）

创建一个符合
[`references/highlight-schema.md`](references/highlight-schema.md) 的 JSON 清单。
最小结构如下：

```json
{
  "version": 1,
  "source": {
    "video": "talk.mp4",
    "transcript": "talk.transcript.json"
  },
  "highlights": [
    {
      "id": "clip-01",
      "title": "Why latency budgets matter",
      "start": "00:03:12.000",
      "end": "00:04:18.500",
      "score": 8,
      "reason": "The speaker gives a complete explanation with a clear takeaway.",
      "risk": "Low risk. The clip is self-contained.",
      "edit_notes": "Start after the setup sentence and end before the next topic."
    }
  ]
}
```

## 校验清单

导出前先执行校验：

```bash
python3 scripts/validate_highlights.py highlights.json
```

校验器会检查必填字段、评分范围、时间码、默认时长边界、重复 ID 和片段重叠。

## 复核片段边界

导出前，结合 VTT 转录检查清单：

```bash
python3 scripts/review_clip_boundaries.py highlights.json captions.vtt
```

这一步可发现起止时间是否切在正在显示的字幕 cue 中，这常导致句子尚未结束就被截断。

## 导出片段

先预览生成的 `ffmpeg` 命令：

```bash
python3 scripts/export_clips.py input.mp4 highlights.json --output-dir highlight-clips --dry-run
```

确认 dry run 正确后，再执行导出：

```bash
python3 scripts/export_clips.py input.mp4 highlights.json --output-dir highlight-clips
```

如需更精确切点，使用 `--reencode`：

```bash
python3 scripts/export_clips.py input.mp4 highlights.json --output-dir highlight-clips --reencode
```

## 二期包装输出

基础片段导出并复核后，可以渲染平台规格版本：

```bash
python3 scripts/render_platform_clips.py highlights.json --input-dir highlight-clips --output-dir platform-clips --aspect vertical --dry-run
```

生成视觉复核命令和 JSON 报告：

```bash
python3 scripts/analyze_visual_signals.py input.mp4 highlights.json --dry-run --json
```

预览合集视频导出：

```bash
python3 scripts/export_compilation.py highlights.json --input-dir highlight-clips --output highlight-compilation.mp4 --dry-run
```

生成可审阅的发布文案资产：

```bash
python3 scripts/generate_publish_assets.py highlights.json --platform Shorts --audience "target viewers"
```

## 清理下载字幕

编辑审阅前先清理 WebVTT 字幕：

```bash
python3 scripts/clean_vtt.py captions.vtt -o captions.clean.txt
```

## 运行测试

```bash
python3 -m unittest discover -s tests -v
```

## 作为 Codex 技能使用

将本目录安装或复制到你的 Codex skills 目录，然后可用于如下请求：

- "Find the best clips from this interview."
- "Create highlight shorts from this lecture and transcript."
- "Validate this highlight manifest and export the clips."

Codex 应遵循 `SKILL.md`：获取或检查媒体，检查带时间戳转录，
生成结构化清单并完成校验，先 dry run 再正式导出，
最后校验导出的媒体文件后再声明交付完成。
