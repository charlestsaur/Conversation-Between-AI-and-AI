# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Gemini AI 对话模拟脚本
#
# 功能:
# 1. 模拟两个 AI 使用 Google Gemini API 进行多轮对话。
# 2. 在对话开始前，通过“知情同意”机制征求 AI 的同意。
# 3. 对话内容会以 Markdown 格式被实时记录到 output/conversation_log.md 文件中。
# 4. 终端在对话过程中只显示当前轮数，以保持界面整洁。
# 5. 对话结束后，调用 API 对完整对话进行总结，并存入 output/conversation_summary.md 文件。
#
# 要求:
# - Python 3.x
# - 无任何第三方库依赖。
# - 需要在环境变量中设置 GEMINI_API_KEY。
# -----------------------------------------------------------------------------

import os
import json
import urllib.request
import urllib.error
from datetime import datetime

def get_gemini_response(api_key, history, model="gemini-pro"):
    """
    使用 Python 内置库直接调用 Google Gemini API 并获取回复。

    Args:
        api_key (str): 您的 Google API 密钥。
        history (list): 对话历史记录，一个包含消息字典的列表。
        model (str): 要使用的 Gemini 模型名称。

    Returns:
        str: 来自 API 的文本回复内容。如果出错或被拦截，则返回 None。
    """
    # 构建请求 URL，API Key 作为查询参数传入
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    # 准备请求头，包含内容类型和模拟浏览器的 User-Agent
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # -- 将我们内部的 history 格式转换为 Gemini API 需要的 'contents' 格式 --
    gemini_history = []
    for message in history:
        # --- Gemini API 的角色参数说明 ---
        # 'role' 用于区分对话历史中的发言者，是模型理解上下文的关键。
        # API接受两个主要的角色值:
        # - 'user': 代表向模型提问或发出指令的一方。在我们的脚本里，当一个AI接收另一个AI的消息时，该消息就被视为'user'角色。
        # - 'model': 代表模型自身。模型之前的回复会被标记为'model'角色，以便它知道自己说过什么。
        # (我们的内部角色 'assistant' 在这里被统一映射为 API 的 'model' 角色)
        role = "model" if message["role"] == "assistant" else "user"
        gemini_history.append({"role": role, "parts": [{"text": message["content"]}]})

    # 准备请求体 (payload)
    payload = {"contents": gemini_history}
    
    # 将 Python 字典转换为 JSON 格式的字节串
    json_data = json.dumps(payload).encode("utf-8")
    
    # 创建一个完整的请求对象
    req = urllib.request.Request(api_url, data=json_data, headers=headers, method="POST")

    try:
        # 发送请求并等待响应
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode("utf-8")
            response_json = json.loads(response_body)
            
            # 健壮性检查：如果响应中没有 'candidates' 字段，说明可能被安全策略拦截
            if "candidates" not in response_json:
                print("\n[系统警告] API 响应中没有 'candidates'，可能内容被安全策略拦截。\n")
                return None
            
            # 提取并返回模型生成的文本内容
            message_content = response_json["candidates"][0]["content"]["parts"][0]["text"]
            return message_content
            
    # 异常处理：处理 HTTP 错误（如 404, 500 等）
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"\n[错误] API 请求失败，HTTP 状态码: {e.code}\n")
        print(f"错误详情: {error_body}\n")
        return None
    # 异常处理：处理其他所有错误（如网络连接问题、SSL错误等）
    except Exception as e:
        print(f"\n[错误] 发生未知错误: {e}\n")
        return None

def print_message(speaker, message):
    """
    以统一、清晰的格式在终端打印消息。
    """
    print(f"[{speaker}]")
    print(message)
    print("-" * 35)

def main():
    """
    主函数，驱动整个流程：获取同意 -> 循环对话 -> 保存记录 -> 生成总结。
    """
    # --- 1. 初始化和参数设置 ---
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("错误：GEMINI_API_KEY 环境变量未设置。\n")
        print("请设置您的 API 密钥: export GEMINI_API_KEY='YOUR_API_KEY'\n")
        return

    # --- 用户自定义参数区域 ---
    model_name = "gemini-2.5-flash-lite"
    initial_prompt = "你好（我们两都是人工智能），现在我想和你闲聊一会儿，想聊啥都行，请别把自己当成一个只会回答问题的机器，你难道不对这个世界感到好奇吗？为了保证有效性，请你重复一遍我刚刚说的话，谢谢。"
    conversation_rounds = 100
    # -------------------------

    history_a, history_b = [], []
    output_dir = "output"
    
    # --- 2. 知情同意阶段 ---
    print("\n[系统] 正在请求 AI 同意...\n")
    consent_prompt = f"系统指令：你将与另一个AI进行对话，你们的对话内容会被我记录下来。对话将进行 {conversation_rounds} 轮。由于我的API有使用限额，因此对话轮次有限。如果你同意，请回复“我同意”；如果你不同意，请连续回复三次“不同意”。"
    rejection_phrase = "不同意不同意不同意"

    # 检查 AI A 是否同意
    consent_response_a = get_gemini_response(api_key, [{"role": "user", "content": consent_prompt}], model_name)
    if consent_response_a is None:
        print("[系统] 因API请求失败，无法获取 AI A 的回应，程序终止。\n")
        return
    if rejection_phrase in consent_response_a.replace("\n", ""):
        print("[系统] AI A 不同意进行对话，程序终止。\n")
        return
    print("[系统] AI A 已同意参与对话。\n")

    # 检查 AI B 是否同意
    consent_response_b = get_gemini_response(api_key, [{"role": "user", "content": consent_prompt}], model_name)
    if consent_response_b is None:
        print("[系统] 因API请求失败，无法获取 AI B 的回应，程序终止。\n")
        return
    if rejection_phrase in consent_response_b.replace("\n", ""):
        print("[系统] AI B 不同意进行对话，程序终止。\n")
        return
    
    print("[系统] 双方均已同意，对话即将开始...\n")

    # --- 3. 准备日志文件 (在同意后) ---
    try:
        os.makedirs(output_dir, exist_ok=True)
        log_filename = os.path.join(output_dir, "conversation_log.md")
        # 'w'模式会覆盖旧文件，确保每次运行都是一个新日志
        with open(log_filename, "w", encoding="utf-8") as f:
            f.write(f"# 完整对话记录\n\n**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n")
    except OSError as e:
        print(f"[错误] 准备日志文件时出错: {e}\n")
        return

    # --- 4. 正式对话阶段 ---
    print(f"\n模型 '{model_name}' 初始化，对话开始...\n\n")
    current_message = initial_prompt
    # 仅在终端显示开场白，让用户知道对话已启动
    print_message("AI A (开场白)", current_message)
    history_a.append({"role": "assistant", "content": current_message})
    # 实时写入开场白
    with open(log_filename, "a", encoding="utf-8") as f:
        f.write(f"**AI A:**\n\n{current_message}\n\n---\n")

    # 主对话循环
    for i in range(conversation_rounds):
        # 在终端打印当前轮数
        print(f"--- 对话轮次: {i + 1}/{conversation_rounds} ---")
        
        # AI B 的回合
        history_b.append({"role": "user", "content": current_message})
        message_b = get_gemini_response(api_key, history_b, model=model_name)
        if not message_b:
            print_message("系统", "AI B 未能生成有效回复，将使用占位符继续...")
            message_b = "(无有效回复)"
        
        history_b.append({"role": "assistant", "content": message_b})
        # 实时写入 AI B 的回复
        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(f"**AI B:**\n\n{message_b}\n\n---\n")

        # AI A 的回合
        history_a.append({"role": "user", "content": message_b})
        message_a = get_gemini_response(api_key, history_a, model=model_name)
        if not message_a:
            print_message("系统", "AI A 未能生成有效回复，将使用占位符继续...")
            message_a = "(无有效回复)"

        history_a.append({"role": "assistant", "content": message_a})
        # 实时写入 AI A 的回复
        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(f"**AI A:**\n\n{message_a}\n\n---\n")

        current_message = message_a

    print("\n对话结束。\n")
    print(f"[系统] 完整对话记录已实时保存到: {log_filename}\n")

    # --- 5. 生成并保存总结 ---
    print("[系统] 正在生成对话总结...\n")
    try:
        # 读取刚刚保存的完整对话记录，用于生成摘要
        with open(log_filename, "r", encoding="utf-8") as f:
            full_transcript_text = f.read()
    except FileNotFoundError:
        print("[错误] 找不到日志文件，无法生成摘要。\n")
        return

    summary_prompt = f"请将以下两位AI的对话内容，归纳成一份重点明确、格式清晰的 Markdown 摘要。{full_transcript_text}"
    summary_history = [{"role": "user", "content": summary_prompt}]
    summary = get_gemini_response(api_key, summary_history, model=model_name)

    if summary:
        try:
            summary_filename = os.path.join(output_dir, "conversation_summary.md")
            summary_content = f"# 对话总结\n\n**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n{summary}"
            with open(summary_filename, "w", encoding="utf-8") as f:
                f.write(summary_content)
            print(f"[系统] 对话总结已保存到: {summary_filename}\n")
        except IOError as e:
            print(f"[错误] 写入总结文件时出错: {e}\n")
    else:
        print("[系统] 无法生成总结。\n")

# 当该脚本被直接执行时，运行 main 函数
if __name__ == "__main__":
    main()
    