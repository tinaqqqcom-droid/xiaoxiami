"""
article_assistant.py
--------------------
小虾米技能：公众号文章写作助手

功能：
- 从 Get笔记 API 读取指定日期的录音笔记
- 提取核心内容，生成公众号文章草稿
- 支持多种文章风格（日记体、观察体、产品体验）
- 输出 Markdown 格式，可直接粘贴到公众号排版工具

使用方式：
    python article_assistant.py --date 2026-05-08 --style product
    python article_assistant.py --date 2026-05-08 --style diary --output article.md

依赖：
    pip install requests openai
    （也可替换为其他大模型 API）
"""

import os
import json
import argparse
from datetime import datetime

import requests

# ── 配置区（使用前替换为你自己的值）──────────────────────────
BIJI_API_BASE = "https://openapi.biji.com/open/api/v1"
BIJI_API_KEY = "YOUR_GET_BIJI_API_KEY"       # 替换为你的 Get笔记 API Key
BIJI_CLIENT_ID = "YOUR_CLIENT_ID"            # 替换为你的 Client ID

LLM_API_KEY = "YOUR_LLM_API_KEY"             # 替换为大模型 API Key（如 Claude/GPT）
LLM_BASE_URL = "https://api.anthropic.com"   # 或替换为其他模型地址
LLM_MODEL = "claude-3-5-sonnet-20241022"     # 替换为你使用的模型
# ─────────────────────────────────────────────────────────────

BIJI_HEADERS = {
    "Authorization": BIJI_API_KEY,
    "X-Client-ID": BIJI_CLIENT_ID,
}

STYLE_PROMPTS = {
    "diary": "请用第一人称日记体，记录这一天真实的体验和感受，语言口语化，有温度，不要太正式。",
    "observation": "请以观察者视角，提炼这段内容中最有价值的洞察和规律，语言克制，有深度。",
    "product": "请以产品体验评测的风格，突出产品的使用场景、核心价值和真实感受，适合公众号发布。",
}


def fetch_notes_by_date(target_date: str, limit: int = 30) -> list:
    """拉取指定日期的笔记"""
    url = f"{BIJI_API_BASE}/resource/note/list"
    params = {"limit": limit, "since_id": 0}
    resp = requests.get(url, headers=BIJI_HEADERS, params=params, timeout=15)
    resp.raise_for_status()
    notes = resp.json().get("data", {}).get("notes", [])
    return [n for n in notes if n.get("created_at", "")[:10] == target_date]


def extract_text_from_notes(notes: list) -> str:
    """从笔记列表提取文本内容"""
    parts = []
    for note in notes:
        time_str = note.get("created_at", "")[:16]
        content = note.get("content", "").strip()
        if content:
            parts.append(f"[{time_str}]\n{content}")
    return "\n\n---\n\n".join(parts)


def generate_article(raw_text: str, style: str, date: str) -> str:
    """调用大模型生成文章草稿"""
    style_instruction = STYLE_PROMPTS.get(style, STYLE_PROMPTS["product"])

    prompt = f"""以下是 {date} 的录音笔记内容：

{raw_text}

---

{style_instruction}

请基于以上内容，写一篇适合微信公众号发布的文章。
要求：
1. 标题吸引人，不超过 20 字
2. 正文 800-1200 字
3. 使用 Markdown 格式（## 二级标题，> 引用块）
4. 结尾有一句有力的金句
5. 不要编造笔记中没有提到的内容
"""

    # 示例：使用 Claude API（可替换为其他模型）
    import anthropic
    client = anthropic.Anthropic(api_key=LLM_API_KEY)
    message = client.messages.create(
        model=LLM_MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def save_article(content: str, output_path: str) -> None:
    """保存文章到文件"""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"文章已保存至：{output_path}")


def main():
    parser = argparse.ArgumentParser(description="小虾米公众号文章写作助手")
    parser.add_argument("--date", type=str, default=datetime.now().strftime("%Y-%m-%d"),
                        help="笔记日期（格式：2026-05-08，默认今天）")
    parser.add_argument("--style", choices=["diary", "observation", "product"],
                        default="product", help="文章风格（默认 product）")
    parser.add_argument("--output", type=str, default="", help="输出文件路径（默认打印到终端）")
    parser.add_argument("--dry-run", action="store_true", help="只显示原始笔记，不生成文章")
    args = parser.parse_args()

    print(f"正在获取 {args.date} 的笔记...")
    notes = fetch_notes_by_date(args.date)
    if not notes:
        print(f"没有找到 {args.date} 的笔记。")
        return

    print(f"共找到 {len(notes)} 条笔记")
    raw_text = extract_text_from_notes(notes)

    if args.dry_run:
        print("\n── 原始笔记内容 ──")
        print(raw_text)
        return

    print(f"正在生成「{args.style}」风格文章...")
    article = generate_article(raw_text, args.style, args.date)

    if args.output:
        save_article(article, args.output)
    else:
        print("\n── 生成结果 ──\n")
        print(article)


if __name__ == "__main__":
    main()
