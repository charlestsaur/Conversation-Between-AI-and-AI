# Conversation Between AI and AI

这个小项目旨在让两个 AI 互相对话。AI 模型为 Gemini，通过 API 来调用。

整个小项目中的所有代码以及说明文档 `CODE_EXPLANATION.md` 均由 Gemini 生成，我本人只做了微小的修改。

- `gemini_chat.py` 是主程序，用于实现两个模型的互相对话。
- `check_models.py` 是辅助工具，确认我的 Gemini API 对哪些模型具有访问权限。
- `gemini_chat.py` 中已经有对程序本身的十分完善的注释，`CODE_EXPLANATION.md` 是整体运行逻辑说明。

**运行：**

（请提前设置好环境变量 `GEMINI_API_KEY`）

```bash
python3 gemini_chat.py
```

**输出：**

```plaintext
/output
   ├── conversation_log.md // 对话具体内容
   └── conversation_summary.md // 对话总结
```
