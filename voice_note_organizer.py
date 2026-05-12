"""
voice_note_organizer.py
-----------------------
小虾米技能：录音笔记整理器

功能：
- 从 Get笔记 OpenAPI 拉取最新录音笔记
- 提取智能总结内容
- 按日期归档到本地 Markdown 文件
- 支持关键词过滤

使用方式：
    python voice_note_organizer.py --days 7
    python voice_note_organizer.py --keyword 巡察 --output notes/

依赖：
    pip install requests
"""

import os
import json
import argparse
from datetime import datetime, timedelta

import requests

# ── 配置区（使用前替换为你自己的值）──────────────────────────
API_BASE_URL = "https://openapi.biji.com/open/api/v1"
API_KEY = "YOUR_GET_BIJI_API_KEY"           # 替换为你的 Get笔记 API Key
CLIENT_ID = "YOUR_CLIENT_ID"                # 替换为你的 Client ID
OUTPUT_DIR = "./voice_notes"                # 本地归档目录
# ─────────────────────────────────────────────────────────────

HEADERS = {
    "Authorization": API_KEY,
    "X-Client-ID": CLIENT_ID,
}


def fetch_notes(limit: int = 20, since_id: int = 0) -> list:
    """从 Get笔记 API 拉取笔记列表"""
    url = f"{API_BASE_URL}/resource/note/list"
    params = {"limit": limit, "since_id": since_id}
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", {}).get("notes", [])


def filter_audio_notes(notes: list) -> list:
    """只保留录音类型的笔记"""
    return [n for n in notes if n.get("note_type") == "recorder_audio"]


def filter_by_keyword(notes: list, keyword: str) -> list:
    """按关键词过滤笔记内容"""
    return [n for n in notes if keyword in n.get("content", "")]


def filter_by_days(notes: list, days: int) -> list:
    """只保留最近 N 天的笔记"""
    cutoff = datetime.now() - timedelta(days=days)
    result = []
    for n in notes:
        created = n.get("created_at", "")
        try:
            dt = datetime.fromisoformat(created[:19])
            if dt >= cutoff:
                result.append(n)
        except ValueError:
            pass
    return result


def export_to_markdown(notes: list, output_dir: str) -> None:
    """将笔记导出为按日期命名的 Markdown 文件"""
    os.makedirs(output_dir, exist_ok=True)
    grouped: dict = {}
    for note in notes:
        date_str = note.get("created_at", "")[:10]
        grouped.setdefault(date_str, []).append(note)

    for date_str, day_notes in sorted(grouped.items()):
        filepath = os.path.join(output_dir, f"{date_str}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# 录音笔记 {date_str}\n\n")
            for i, note in enumerate(day_notes, 1):
                time_str = note.get("created_at", "")[:16].replace("T", " ")
                f.write(f"## 录音 {i}（{time_str}）\n\n")
                f.write(note.get("content", "（无内容）"))
                f.write("\n\n---\n\n")
        print(f"已导出：{filepath}（共 {len(day_notes)} 条）")


def main():
    parser = argparse.ArgumentParser(description="小虾米录音笔记整理器")
    parser.add_argument("--days", type=int, default=7, help="拉取最近 N 天（默认 7）")
    parser.add_argument("--keyword", type=str, default="", help="关键词过滤")
    parser.add_argument("--output", type=str, default=OUTPUT_DIR, help="输出目录")
    parser.add_argument("--limit", type=int, default=50, help="最多拉取条数（默认 50）")
    args = parser.parse_args()

    print(f"正在拉取最近 {args.days} 天的录音笔记...")
    notes = fetch_notes(limit=args.limit)
    notes = filter_audio_notes(notes)
    notes = filter_by_days(notes, args.days)

    if args.keyword:
        notes = filter_by_keyword(notes, args.keyword)
        print(f"关键词「{args.keyword}」过滤后：{len(notes)} 条")
    else:
        print(f"共找到 {len(notes)} 条录音笔记")

    if not notes:
        print("没有符合条件的笔记。")
        return

    export_to_markdown(notes, args.output)
    print(f"\n完成！文件已保存至 {args.output}/")


if __name__ == "__main__":
    main()
