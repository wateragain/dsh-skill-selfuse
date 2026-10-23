---
name: chat-export
description: 把当前或指定的 DSH 会话导出成「我：/ 小鲸鱼：」对话文本，自动命名为 <工作区>-<会话名>-<日期>.md 并自动去重。用户说"导出聊天""导出这段对话""聊天记录存文件""导出会话"时使用。
whenToUse: 需要把会话内容落地成可读文本、归档、或交给别人时；跨会话批量导出也用这个。
---

# 会话导出

## 一条命令，不要重写解析逻辑

```bash
python "$DSH_HOME/skills/chat-export/scripts/chat_export.py"
```

默认导出**当前会话**（读 `DSH_SESSION_ID`），输出到该会话自己的工作区根目录，命名 `<工作区名>-<会话名>-<YYYYMMDD>.md`，重名自动加 `-2`、`-3`。

## 参数

| 参数 | 用途 |
|---|---|
| `--list` | 列出所有会话（时间 / id / 标题 / 工作区） |
| `--session <id或路径>` | 导出别的会话 |
| `--out <文件>` | 指定输出路径（跨工作区导出必用） |
| `--name 我 --bot 小鲸鱼` | 改称谓 |
| `--keep-partial` | 保留未完成轮次（默认丢弃半截回复） |

## 输出规则（已内建，不要重复实现）

- 只收 `source.kind == "user"` 的用户消息；注入的 AGENTS.md、runtime context、system-reminder 全部过滤
- 助手侧只取 `text` 块，丢弃 reasoning 与 tool-call；同一轮多个 step 合并为一条
- 没有 `turn/end` 的轮次不导出，避免半截话
- 相邻同说话人自动合并，空行压缩

## 坑

- 需要 **Python 3.14+**（用内置 `compression.zstd`）；低版本得装 `zstandard`
- 会话文件位置：`$DSH_HOME/sessions/<工作区编码>/<session-id>/session.v4.jsonl.zstd`
- 工具沙箱只能写当前工作区，**跨工作区导出会被拦**，用 `--out` 指到工作区内
- 本轮还在生成时，最后一条回复不完整——等这轮结束再导
- 文件名里的会话名取会话的最后一条 title 记录（用户改名优先于自动生成）

## 验收

跑完看三行输出：会话 id、输出路径、用户/助手条数。条数应与对话轮数一致（用户 N 条 ↔ 助手 N 或 N-1 条）。
