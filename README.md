# Conversation Between AI and AI

这个小项目旨在让两个 AI 互相对话。AI 模型为 Gemini，通过 API 来调用。

> 注意：也可使用 llama.cpp 本地推理的模型进行互相对话，脚本为 `llamacpp_chat.py`

整个小项目中除 `llamacpp_chat.py` 外（包括说明文档 `CODE_EXPLANATION.md`）均由 Gemini 生成，我本人只做了微小的修改。

`llamacpp_chat.py` 为 GPT 基于 Gemini 编写的 `gemini_chat.py` 改写的脚本。

- `gemini_chat.py` 是主程序，用于实现两个模型的互相对话。
- `llamacpp_chat.py` 与 `gemini_chat.py` 功能一致，不同之处在于使用 llama.cpp 本地推理的模型
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
