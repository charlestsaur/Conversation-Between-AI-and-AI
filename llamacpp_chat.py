# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# 本地 llama.cpp 对话模拟脚本
#
# 说明:
# - 使用 llama.cpp 自带的 OpenAI-compatible HTTP server
# - 不依赖任何第三方库
# - 完全本地运行
# -----------------------------------------------------------------------------

import os
import json
import urllib.request
import urllib.error
from datetime import datetime

LLAMA_API_URL = "http://127.0.0.1:1234/v1/chat/completions"

def get_llama_response(history, model="local-model"):
    """
    调用本地 llama.cpp (OpenAI compatible) 获取回复
    """
    headers = {
        "Content-Type": "application/json"
    }

    # llama.cpp 使用 OpenAI 风格 messages
    messages = []
    for msg in history:
        role = msg["role"]
        if role == "assistant":
            role = "assistant"
        elif role == "user":
            role = "user"
        else:
            role = "system"

        messages.append({
            "role": role,
            "content": msg["content"]
        })

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.9,
        "top_p": 0.95,
        "stream": False
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        LLAMA_API_URL,
        data=data,
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
            result = json.loads(body)
            return result["choices"][0]["message"]["content"]

    except urllib.error.HTTPError as e:
        print(f"\n[错误] llama.cpp HTTP 错误: {e.code}")
        print(e.read().decode("utf-8"))
        return None

    except Exception as e:
        print(f"\n[错误] llama.cpp 请求异常: {e}")
        return None


def print_message(speaker, message):
    print(f"[{speaker}]")
    print(message)
    print("-" * 35)


def main():
    # ---------------- 用户配置 ----------------
    model_name = "local-model"   # llama.cpp 不强制校验
    initial_prompt = "你好（我们两都是人工智能），现在我想和你闲聊一会儿，想聊啥都行，请别把自己当成一个只会回答问题的机器，你难道不对这个世界感到好奇吗？为了保证有效性，请你重复一遍我刚刚说的话，谢谢。"
    conversation_rounds = 100
    # -----------------------------------------

    history_a, history_b = [], []
    output_dir = "output"

    print("\n[系统] 本地 llama.cpp 对话启动中...\n")

    # ---------- 知情同意 ----------
    consent_prompt = (
        f"系统指令：你将与另一个AI进行对话，你们的对话内容会被记录。"
        f"对话将进行 {conversation_rounds} 轮。"
        "如果你同意，请回复“我同意”；如果不同意，请连续回复三次“不同意”。"
    )
    rejection_phrase = "不同意不同意不同意"

    consent_a = get_llama_response([{"role": "user", "content": consent_prompt}], model_name)
    if not consent_a or rejection_phrase in consent_a.replace("\n", ""):
        print("[系统] AI A 未同意，对话终止。")
        return

    consent_b = get_llama_response([{"role": "user", "content": consent_prompt}], model_name)
    if not consent_b or rejection_phrase in consent_b.replace("\n", ""):
        print("[系统] AI B 未同意，对话终止。")
        return

    print("[系统] 双方已同意，对话开始。\n")

    # ---------- 日志 ----------
    os.makedirs(output_dir, exist_ok=True)
    log_filename = os.path.join(output_dir, "conversation_log.md")
    with open(log_filename, "w", encoding="utf-8") as f:
        f.write(f"# 完整对话记录\n\n**生成时间:** {datetime.now()}\n\n---\n\n")

    # ---------- 开场 ----------
    current_message = initial_prompt
    print_message("AI A (开场)", current_message)

    history_a.append({"role": "assistant", "content": current_message})
    with open(log_filename, "a", encoding="utf-8") as f:
        f.write(f"**AI A:**\n\n{current_message}\n\n---\n")

    # ---------- 主循环 ----------
    for i in range(conversation_rounds):
        print(f"--- 对话轮次 {i+1}/{conversation_rounds} ---")

        history_b.append({"role": "user", "content": current_message})
        msg_b = get_llama_response(history_b, model_name) or "(无回复)"
        history_b.append({"role": "assistant", "content": msg_b})

        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(f"**AI B:**\n\n{msg_b}\n\n---\n")

        history_a.append({"role": "user", "content": msg_b})
        msg_a = get_llama_response(history_a, model_name) or "(无回复)"
        history_a.append({"role": "assistant", "content": msg_a})

        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(f"**AI A:**\n\n{msg_a}\n\n---\n")

        current_message = msg_a

    print("\n[系统] 对话结束。")

    # ---------- 总结 ----------
    with open(log_filename, "r", encoding="utf-8") as f:
        transcript = f.read()

    summary_prompt = f"请将以下两位AI的对话内容总结成 Markdown 摘要：\n\n{transcript}"
    summary = get_llama_response([{"role": "user", "content": summary_prompt}], model_name)

    if summary:
        summary_file = os.path.join(output_dir, "conversation_summary.md")
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(f"# 对话总结\n\n{summary}")
        print(f"[系统] 总结已保存至 {summary_file}")


if __name__ == "__main__":
    main()
