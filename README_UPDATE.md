## 功能模块

### 🎙️ 录音笔记整理器
`voice_note_organizer.py` - 从 Get笔记 API 拉取录音笔记，按日期归档为 Markdown 文件

- 支持按天数过滤（最近 N 天）
- 支持关键词搜索过滤
- 自动按日期分组导出

```shell
python voice_note_organizer.py --days 7 --output ./notes
python voice_note_organizer.py --keyword 工作 --days 30
```

### 💬 微信群聊分析器
`wechat_group_analyzer.py` - 解析微信群聊导出记录，生成成员发言统计与画像

- Top N 发言排行榜
- 指定成员发言提取与导出
- 潜水成员识别（配合群成员 xlsx 使用）

```shell
python wechat_group_analyzer.py --file 群聊记录.txt --top 50
python wechat_group_analyzer.py --file 群聊记录.txt --member 某人 --export
python wechat_group_analyzer.py --file 群聊记录.txt --members-xlsx 群成员.xlsx
```

### 📝 公众号文章写作助手
`article_assistant.py` - 读取当天录音笔记，自动生成公众号文章草稿

- 三种写作风格：日记体 / 观察体 / 产品体验
- 自动提取核心内容，避免编造
- 输出标准 Markdown 格式

```shell
python article_assistant.py --date 2026-05-08 --style product --output article.md
python article_assistant.py --date 2026-05-08 --style diary
```

### 🎵 歌词时间轴工具
`lyrics_timeline_tool.py` - 图形化标注歌词时间戳，输出 JSON 格式时间轴

```shell
python lyrics_timeline_tool.py
```
