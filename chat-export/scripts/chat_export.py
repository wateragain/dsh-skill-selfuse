# -*- coding: utf-8 -*-
"""DSH 会话导出：把 session.v4.jsonl.zstd 转成「我：/ 小鲸鱼：」对话记录。

用法
  python chat_export.py                    # 导出当前会话（读 DSH_SESSION_ID）
  python chat_export.py --session <id|路径>  # 导出指定会话
  python chat_export.py --list             # 列出所有会话（id / 标题 / 时间 / 目录）
  python chat_export.py --out <文件>        # 指定输出路径
  python chat_export.py --name 我 --bot 小鲸鱼   # 改称谓
  python chat_export.py --keep-partial     # 保留未完成轮次（默认丢弃）

默认输出到会话自己的工作区根目录：
  <工作区名>-<会话名>-<YYYYMMDD>.md，重名自动加 -2、-3。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from compression import zstd  # Python 3.14+
except ImportError:  # 3.14 以下没有内置 zstd
    zstd = None

ILLEGAL = r'[\\/:*?"<>|\r\n\t]'


def setup_io() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def dsh_home() -> Path:
    return Path(os.environ.get("DSH_HOME") or (Path.home() / ".dsh"))


def sessions_root() -> Path:
    return dsh_home() / "sessions"


def open_session_file(path: Path):
    """返回逐行迭代器；支持 .zstd 与裸 .jsonl。"""
    if path.suffix == ".zstd":
        if zstd is None:
            raise SystemExit("需要 Python 3.14+（内置 compression.zstd）或安装 zstandard")
        return zstd.open(path, "rb")
    return path.open("rb")


def iter_records(path: Path):
    with open_session_file(path) as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def locate(spec: str | None) -> Path:
    root = sessions_root()
    if spec:
        cand = Path(spec)
        if cand.is_file():
            return cand
        if cand.is_dir():
            hits = sorted(cand.glob("session*.zstd")) or sorted(cand.glob("session*.jsonl"))
            if hits:
                return hits[0]
            raise SystemExit(f"目录里没有会话文件: {cand}")
        hits = list(root.glob(f"*/{spec}*/session*.zstd")) + list(root.glob(f"*/{spec}*/session*.jsonl"))
        if hits:
            return hits[0]
        raise SystemExit(f"找不到会话: {spec}")

    sid = os.environ.get("DSH_SESSION_ID")
    if sid:
        hits = sorted(root.glob(f"*/{sid}/session*.zstd")) + sorted(root.glob(f"*/{sid}/session*.jsonl"))
        if hits:
            return hits[0]

    all_files = list(root.glob("*/session-*/session*.zstd"))
    if not all_files:
        raise SystemExit(f"没有找到任何会话文件，检查 {root}")
    return max(all_files, key=lambda p: p.stat().st_mtime)


def blocks_text(content) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "".join(
        b["text"] for b in content
        if isinstance(b, dict) and b.get("type") == "text" and b.get("text")
    )


def collect(path: Path, keep_partial: bool):
    """返回 (items, meta)。items 为 [{'who','text','turn'}] 交替序列。"""
    meta = {"id": path.parent.name, "cwd": "", "title": ""}
    items: list[dict] = []
    completed: set = set()

    for rec in iter_records(path):
        t = rec.get("type")
        d = rec.get("data") or {}

        if t == "session":
            meta["cwd"] = rec.get("cwd") or ""
            meta["id"] = rec.get("id") or meta["id"]
        elif t == "session/title":
            title = d.get("title")
            if isinstance(title, dict):
                title = title.get("title") or title.get("text")
            if isinstance(title, str) and title.strip():
                meta["title"] = title.strip()      # 取最后一条（用户改名优先）
        elif t == "turn/end":
            completed.add(d.get("turn"))
        elif t == "user/message":
            if (d.get("source") or {}).get("kind") != "user":
                continue                            # 跳过注入的指令/上下文/提醒
            txt = blocks_text(d.get("content")).strip()
            if txt:
                items.append({"who": "user", "text": txt, "turn": None})
        elif t == "assistant/message":
            txt = blocks_text((d.get("message") or {}).get("content")).strip()
            if not txt or not items:
                continue
            if items[-1]["who"] == "user":
                items.append({"who": "bot", "text": txt, "turn": d.get("turn")})
            else:
                items[-1]["text"] += "\n\n" + txt

    # 合并相邻同说话人（防御性）
    merged: list[dict] = []
    for it in items:
        if merged and merged[-1]["who"] == it["who"]:
            merged[-1]["text"] += "\n\n" + it["text"]
        else:
            merged.append(dict(it))

    if not keep_partial:
        merged = [i for i in merged if i["who"] == "user" or i.get("turn") in completed]
    return merged, meta


def clean(text: str) -> str:
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def safe_name(s: str, limit: int = 40) -> str:
    s = re.sub(ILLEGAL, " ", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s.strip(".-")[:limit] or "session"


def default_out(meta: dict, path: Path) -> Path:
    cwd = Path(meta["cwd"]) if meta["cwd"] else Path.cwd()
    ws = safe_name(cwd.name or "workspace", 24)
    title = safe_name(meta["title"] or meta["id"], 40)
    stamp = datetime.now().strftime("%Y%m%d")
    base = f"{ws}-{title}-{stamp}"
    return cwd / f"{base}.md"


def unique(path: Path) -> Path:
    if not path.exists():
        return path
    for n in range(2, 100):
        cand = path.with_name(f"{path.stem}-{n}{path.suffix}")
        if not cand.exists():
            return cand
    raise SystemExit(f"同名文件过多: {path}")


def build_text(items, user_name: str, bot_name: str) -> str:
    label = {"user": user_name, "bot": bot_name}
    return "\n\n".join(f"{label[i['who']]}：{clean(i['text'])}" for i in items) + "\n"


def cmd_list() -> None:
    rows = []
    for f in sessions_root().glob("*/session-*/session*.zstd"):
        try:
            meta = {"id": f.parent.name, "cwd": "", "title": ""}
            mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            for rec in iter_records(f):
                if rec.get("type") == "session":
                    meta["cwd"] = rec.get("cwd") or ""
                elif rec.get("type") == "session/title":
                    t = (rec.get("data") or {}).get("title")
                    if isinstance(t, dict):
                        t = t.get("title")
                    if isinstance(t, str) and t.strip():
                        meta["title"] = t.strip()
        except Exception:
            mtime, meta = "?", meta
        rows.append((f.stat().st_mtime, meta["id"], meta["title"] or "(无标题)", mtime, meta["cwd"]))
    for _, sid, title, mtime, cwd in sorted(rows, reverse=True):
        print(f"{mtime}  {sid}  {title}  [{cwd}]")


def main() -> None:
    setup_io()
    ap = argparse.ArgumentParser(add_help=True, description="导出 DSH 会话为对话文本")
    ap.add_argument("--session", help="会话 id 或 session.v4.jsonl.zstd 路径")
    ap.add_argument("--out", help="输出文件路径")
    ap.add_argument("--name", default="我", help="用户称谓")
    ap.add_argument("--bot", default="小鲸鱼", help="助手称谓")
    ap.add_argument("--list", action="store_true", help="列出会话")
    ap.add_argument("--keep-partial", action="store_true", help="保留未完成轮次")
    args = ap.parse_args()

    if args.list:
        cmd_list()
        return

    path = locate(args.session)
    items, meta = collect(path, args.keep_partial)
    if not items:
        raise SystemExit("该会话没有可导出的文本消息")

    out = Path(args.out) if args.out else default_out(meta, path)
    out = unique(out)
    out.write_text(build_text(items, args.name, args.bot), encoding="utf-8")

    users = sum(1 for i in items if i["who"] == "user")
    print(f"会话: {meta['id']}  标题: {meta['title'] or '(无)'}")
    print(f"输出: {out}")
    print(f"消息: 用户 {users} 条 / 助手 {len(items) - users} 条，{out.stat().st_size} 字节")


if __name__ == "__main__":
    main()
