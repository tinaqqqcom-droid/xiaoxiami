# 🦐 小虾米 | XiaoXiaMi

> 一个基于 OpenClaw 的个人 AI 助手系统

## 简介

小虾米是一个个性化的 AI 助手框架，通过整合多种 AI 技能和自动化工具，帮助用户提升日常工作效率。

## 核心功能

### 🧠 智能对话
- 自然语言理解与生成
- 上下文记忆与连续对话
- 个性化回复风格

### 📄 文档处理
- 支持 Word/Excel/PDF 格式
- 自动生成专业文档
- 智能内容提取与总结

### 🌐 浏览器自动化
- 网页信息抓取
- 自动填表与操作
- 定时任务执行

### 📚 知识库管理
- 个人笔记归档
- 智能检索历史内容
- 结构化知识存储

### ⏰ 定时任务
- 自动化提醒
- 周期性任务调度
- 工作流自动化

## 技术栈

| 组件 | 说明 |
|------|------|
| OpenClaw | 核心运行框架 |
| Claude | 主要对话模型 |
| Skills | 可扩展技能系统 |

## 功能模块

### 🎙️ 录音笔记整理器
`voice_note_organizer.py` - 从 Get笔记 API 拉取录音笔记，按日期归档为 Markdown 文件

- 支持按天数过滤（最近 N 天）
- 支持关键词搜索过滤
- 自动按日期分组导出

```bash
python voice_note_organizer.py --days 7 --output ./notes
python voice_note_organizer.py --keyword 工作 --days 30
```

### 💬 微信群聊分析器
`wechat_group_analyzer.py` - 解析微信群聊导出记录，生成成员发言统计与画像

- Top N 发言排行榜
- 指定成员发言提取与导出
- 潜水成员识别（配合群成员 xlsx 使用）

```bash
python wechat_group_analyzer.py --file 群聊记录.txt --top 50
python wechat_group_analyzer.py --file 群聊记录.txt --member 某人 --export
python wechat_group_analyzer.py --file 群聊记录.txt --members-xlsx 群成员.xlsx
```

### 📝 公众号文章写作助手
`article_assistant.py` - 读取当天录音笔记，自动生成公众号文章草稿

- 三种写作风格：日记体 / 观察体 / 产品体验
- 自动提取核心内容，避免编造
- 输出标准 Markdown 格式

```bash
python article_assistant.py --date 2026-05-08 --style product --output article.md
python article_assistant.py --date 2026-05-08 --style diary
```

### 🎵 歌词时间轴工具
`examples/lyrics_timeline_tool.py` - 图形化标注歌词时间戳，输出 JSON 格式时间轴

```bash
python examples/lyrics_timeline_tool.py
```

## 特点

- 🔒 **隐私优先** - 本地部署，数据不离开你的设备
- 🎨 **个性化** - 可自定义助手性格与回复风格
- 🔧 **可扩展** - 模块化设计，易于添加新功能
- 🌍 **多平台** - 支持多种消息渠道接入

## 适用场景

- 📊 个人信息管理
- 📝 文档自动化生成
- 🔍 网页信息采集
- ⚡ 重复任务自动化
- 💡 技术调研辅助

## 开始使用

1. 安装 OpenClaw 框架
2. 配置 AI 模型 API
3. 添加所需技能模块
4. 开始对话！

## 许可证

MIT License

---

🦐 Made with ❤️ by XiaoXiaMi Team
