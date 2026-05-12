#!/usr/bin/env python3
"""
歌词时间戳标注工具
====================

一个基于 Tkinter 的 GUI 工具，用于为歌词标注时间戳，
生成可用于 ASS/SRT 字幕文件的时间轴数据。

【功能特点】
- 图形界面，实时显示播放进度
- 快捷键操作：空格（标记）、回车（跳过）、R（回退）、S（保存）
- 自动生成 JSON 和 Python 格式的时间轴数据
- 支持暂停/继续计时

【依赖】
- Python 3.6+
- tkinter (通常随 Python 自带)
- mutagen (可选，用于自动获取音频时长: pip install mutagen)

【使用方法】
1. 将音乐文件放到脚本目录或修改 music_path
2. 修改 lyrics_list 为你的歌词
3. 运行脚本：python lyrics_timeline_tool.py
4. 在媒体播放器中播放歌曲
5. 按空格键标记每句歌词的开始时间
6. 完成后按 S 保存

【输出】
- lyrics_timestamps.json：JSON 格式时间轴
- lyrics_timestamps.py：Python 格式时间轴
"""

import os
import sys
import json
import time
import threading
from tkinter import *
from tkinter import ttk


class LyricsTimelineTool:
    def __init__(self, music_path=None, lyrics_list=None):
        """
        初始化工具
        
        Args:
            music_path: 音乐文件路径（可选）
            lyrics_list: 歌词列表（可选，默认使用示例歌词）
        """
        # 音乐文件路径（可自行修改）
        self.music_path = music_path or os.path.join(os.path.expanduser('~'), 'Downloads', 'song.mp3')
        
        # 歌词列表（可自行修改）
        self.lyrics_list = lyrics_list or [
            '示例歌词第一行',
            '示例歌词第二行',
            '示例歌词第三行',
        ]
        
        self.timestamps = []
        self.current_idx = 0
        self.state = 'stopped'   # 'stopped' | 'playing'
        self.start_time = 0
        self.paused_elapsed = 0
        
        # 获取音频时长
        self.duration = self._get_duration()
        
        # 创建窗口
        self.root = Tk()
        self.root.title('🎵 歌词时间戳标注工具')
        self.root.geometry('820x750')
        self.root.configure(bg='#1a1a2e')
        self._build_ui()
        
        # 键盘快捷键
        self.root.bind('<space>', lambda e: self.mark_timestamp())
        self.root.bind('<Return>', lambda e: self.skip_lyric())
        self.root.bind_all('<s>', lambda e: self.save_and_exit())
        self.root.bind_all('<S>', lambda e: self.save_and_exit())
        self.root.bind_all('<r>', lambda e: self.undo())
        self.root.bind_all('<R>', lambda e: self.undo())
        
        self.running = True
        threading.Thread(target=self._update_thread, daemon=True).start()
        self.root.mainloop()
    
    def _get_duration(self):
        """获取音频时长（需要 mutagen 库）"""
        try:
            import mutagen
            audio = mutagen.File(self.music_path)
            if audio and audio.info.length:
                return audio.info.length
        except:
            pass
        return 180.0  # 默认 3 分钟
    
    def _build_ui(self):
        """构建用户界面"""
        mf = Frame(self.root, bg='#1a1a2e')
        mf.pack(fill=BOTH, expand=True, padx=20, pady=15)
        
        # 标题
        hdr = Frame(mf, bg='#1a1a2e')
        hdr.pack(fill=X)
        Label(hdr, text='🎵 歌词时间戳标注工具',
              font=('Microsoft YaHei', 18, 'bold'),
              fg='white', bg='#1a1a2e').pack(side=LEFT)
        
        # 状态标签
        self.state_label = Label(mf, text='⏹ 准备就绪（请手动播放音乐）',
                                  font=('Microsoft YaHei', 12),
                                  fg='#fbbf24', bg='#1a1a2e')
        self.state_label.pack(pady=10)
        
        # 时间显示
        self.time_label = Label(mf, text='--:--.-- / --:--.--',
                                  font=('Consolas', 28, 'bold'),
                                  fg='#60a5fa', bg='#1a1a2e')
        self.time_label.pack(pady=10)
        
        # 当前歌词
        self.lyric_lbl = Label(mf, text=self.lyrics_list[0] if self.lyrics_list else '',
                                font=('Microsoft YaHei', 20, 'bold'),
                                fg='#fbbf24', bg='#1a1a2e', wraplength=760)
        self.lyric_lbl.pack(pady=20)
        
        # 操作提示
        tips = Frame(mf, bg='#16213e', bd=1)
        tips.pack(fill=X, pady=10)
        Label(tips, text='💡 操作提示: 空格=标记时间戳 | 回车=跳过本句 | R=回退 | S=保存退出',
              font=('Microsoft YaHei', 9),
              fg='#86efac', bg='#16213e').pack(pady=6)
        
        # 进度
        self.prog_lbl = Label(mf, text=f'已标注: 0 / {len(self.lyrics_list)}',
                               font=('Microsoft YaHei', 12),
                               fg='#a78bfa', bg='#1a1a2e')
        self.prog_lbl.pack()
    
    def fmt(self, s):
        """格式化时间为 MM:SS.CC"""
        if s < 0:
            return '--:--.--'
        return f'{int(s//60):02d}:{s%60:05.2f}'
    
    def elapsed(self):
        """获取已过去的时间"""
        if self.state == 'stopped':
            return self.paused_elapsed
        return time.time() - self.start_time + self.paused_elapsed
    
    def mark_timestamp(self):
        """标记当前时间戳"""
        if self.current_idx >= len(self.lyrics_list):
            return
        t = self.elapsed()
        self.timestamps.append((t, self.lyrics_list[self.current_idx]))
        self.current_idx += 1
        self._update_lyric_display()
    
    def skip_lyric(self):
        """跳过当前歌词"""
        if self.current_idx >= len(self.lyrics_list):
            return
        self.timestamps.append((self.elapsed(), f'[跳过] {self.lyrics_list[self.current_idx]}'))
        self.current_idx += 1
        self._update_lyric_display()
    
    def undo(self):
        """撤销上一次标记"""
        if self.timestamps:
            self.timestamps.pop()
            self.current_idx -= 1
            self._update_lyric_display()
    
    def _update_lyric_display(self):
        """更新歌词显示"""
        if self.current_idx < len(self.lyrics_list):
            self.lyric_lbl.config(text=f'{self.current_idx+1}. {self.lyrics_list[self.current_idx]}')
        else:
            self.lyric_lbl.config(text='✅ 全部标注完成！按 S 保存退出')
        self.prog_lbl.config(text=f'已标注: {self.current_idx} / {len(self.lyrics_list)}')
    
    def _update_thread(self):
        """更新线程"""
        while self.running:
            try:
                self.root.after(0, self._paint)
            except:
                pass
            time.sleep(0.08)
    
    def _paint(self):
        """更新界面显示"""
        t = self.elapsed()
        self.time_label.config(text=f'{self.fmt(t)} / {self.fmt(self.duration)}')
    
    def save_and_exit(self):
        """保存并退出"""
        self.running = False
        
        # 生成时间轴数据
        active = []
        for i, (t, lyric) in enumerate(self.timestamps):
            end_t = self.timestamps[i+1][0] if i+1 < len(self.timestamps) else t + 4.0
            clean = lyric.replace('[跳过] ', '')
            active.append({'lyric': clean, 'start': round(t, 2), 'end': round(end_t, 2)})
        
        # 保存为 JSON
        json_path = 'lyrics_timestamps.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(active, f, ensure_ascii=False, indent=2)
        
        # 保存为 Python 格式
        py_path = 'lyrics_timestamps.py'
        with open(py_path, 'w', encoding='utf-8') as f:
            f.write('# -*- coding: utf-8 -*-\n')
            f.write('# 歌词时间轴数据\n\n')
            f.write('LYRICS = [\n')
            for item in active:
                l = item['lyric'].replace("'", "\\'")
                f.write(f"    ('{l}', {item['start']}, {item['end']}),\n")
            f.write(']\n')
        
        print(f'✅ 已保存 {len(active)} 条歌词到:')
        print(f'   {json_path}')
        print(f'   {py_path}')
        
        self.root.destroy()
    
    def quit_no_save(self):
        """不保存退出"""
        self.running = False
        self.root.destroy()


if __name__ == '__main__':
    # 自定义歌词和音乐路径
    custom_lyrics = [
        '你的歌词第一行',
        '你的歌词第二行',
        # 添加更多...
    ]
    
    custom_music = os.path.join(os.path.expanduser('~'), 'Music', 'your_song.mp3')
    
    # 使用自定义歌词和音乐路径
    # tool = LyricsTimelineTool(music_path=custom_music, lyrics_list=custom_lyrics)
    
    # 或使用默认示例
    tool = LyricsTimelineTool()
