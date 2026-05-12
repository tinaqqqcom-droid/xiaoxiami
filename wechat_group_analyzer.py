"""
wechat_group_analyzer.py
------------------------
小虾米技能：微信群聊分析器

功能：
- 解析微信群聊导出的 .txt 记录文件
- 统计各成员发言数量并生成排行榜
- 提取指定成员的全部发言记录
- 识别潜水成员（有群成员列表时）
- 输出 Top N 发言者画像数据

使用方式：
    python wechat_group_analyzer.py --file 群聊记录.txt --top 50
    python wechat_group_analyzer.py --file 群聊记录.txt --member 某人昵称 --export
    python wechat_group_analyzer.py --file 群聊记录.txt --members-xlsx 群成员列表.xlsx

依赖：
    pip install openpyxl
"""

import re
import os
import argparse
from collections import Counter
from datetime import datetime

# 可选：需要 openpyxl 才能读取群成员 xlsx
try:
    import openpyxl
    XLSX_SUPPORT = True
except ImportError:
    XLSX_SUPPORT = False

# 消息行正则：匹配 "2024-10-18 22:11:00  昵称" 格式
MSG_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(.+)$")


def parse_chat_file(filepath: str) -> list[dict]:
    """解析群聊 txt 文件，返回消息列表"""
    messages = []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        m = MSG_PATTERN.match(line)
        if m:
            ts = m.group(1)
            sender = m.group(2).strip().strip("'")
            content_lines = []
            j = i + 1
            while j < len(lines) and not MSG_PATTERN.match(lines[j]):
                content_lines.append(lines[j].rstrip())
                j += 1
            content = " ".join(content_lines).strip()
            messages.append({
                "timestamp": ts,
                "sender": sender,
                "content": content,
            })
            i = j
        else:
            i += 1
    return messages


def get_top_senders(messages: list[dict], top_n: int = 50) -> list[tuple]:
    """统计发言量，返回 Top N"""
    counter = Counter(m["sender"] for m in messages)
    return counter.most_common(top_n)


def get_member_messages(messages: list[dict], name: str) -> list[dict]:
    """提取指定成员的全部发言"""
    return [m for m in messages if name in m["sender"]]


def load_members_from_xlsx(filepath: str) -> list[str]:
    """从 xlsx 群成员列表提取昵称"""
    if not XLSX_SUPPORT:
        raise ImportError("需要安装 openpyxl：pip install openpyxl")
    wb = openpyxl.load_workbook(filepath)
    ws = wb.active
    members = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i < 3:  # 跳过表头
            continue
        # 微信昵称(col0)、备注(col1)、群昵称(col2)
        for col in [0, 1, 2]:
            v = str(row[col]).strip() if row[col] else ""
            if v and v != "None":
                members.append(v)
    return list(set(members))


def find_silent_members(messages: list[dict], members: list[str]) -> list[str]:
    """找出在成员列表中但没有发言记录的潜水成员"""
    speakers = set(m["sender"] for m in messages)
    silent = []
    for member in members:
        if not any(member in s or s in member for s in speakers):
            silent.append(member)
    return sorted(silent)


def export_member_messages(messages: list[dict], name: str, output_dir: str) -> str:
    """导出指定成员发言到 txt 文件"""
    os.makedirs(output_dir, exist_ok=True)
    safe_name = re.sub(r'[\\/:*?"<>|]', "_", name)
    filepath = os.path.join(output_dir, f"{safe_name}_messages.txt")
    member_msgs = get_member_messages(messages, name)
    with open(filepath, "w", encoding="utf-8") as f:
        for msg in member_msgs:
            f.write(f"[{msg['timestamp']}]\n{msg['content']}\n\n")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="小虾米微信群聊分析器")
    parser.add_argument("--file", required=True, help="群聊 txt 文件路径")
    parser.add_argument("--top", type=int, default=50, help="显示 Top N 发言者（默认 50）")
    parser.add_argument("--member", type=str, default="", help="提取指定成员发言")
    parser.add_argument("--export", action="store_true", help="导出发言记录到文件")
    parser.add_argument("--members-xlsx", type=str, default="", help="群成员 xlsx 文件，用于查找潜水成员")
    parser.add_argument("--output", type=str, default="./output", help="输出目录")
    args = parser.parse_args()

    print(f"正在解析：{args.file}")
    messages = parse_chat_file(args.file)
    print(f"共解析 {len(messages)} 条消息")

    # Top N 排行
    print(f"\n── Top {args.top} 发言排行 ──")
    for rank, (sender, count) in enumerate(get_top_senders(messages, args.top), 1):
        print(f"  {rank:3d}. {sender}  ({count} 条)")

    # 指定成员分析
    if args.member:
        member_msgs = get_member_messages(messages, args.member)
        print(f"\n── {args.member} 共发言 {len(member_msgs)} 条 ──")
        for msg in member_msgs[:10]:
            print(f"  [{msg['timestamp']}] {msg['content'][:60]}")
        if len(member_msgs) > 10:
            print(f"  ... 还有 {len(member_msgs) - 10} 条")
        if args.export:
            path = export_member_messages(messages, args.member, args.output)
            print(f"\n已导出至：{path}")

    # 潜水成员分析
    if args.members_xlsx:
        print(f"\n正在加载群成员列表：{args.members_xlsx}")
        members = load_members_from_xlsx(args.members_xlsx)
        print(f"群成员总数：{len(members)}")
        silent = find_silent_members(messages, members)
        print(f"潜水成员（{len(silent)} 人）：")
        for name in silent:
            print(f"  - {name}")


if __name__ == "__main__":
    main()
