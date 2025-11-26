import os
import json
import urllib.request
import urllib.error

def list_available_models(api_key):
    """
    Calls the Gemini API to list all available models for the given API key.
    """
    # The endpoint for listing models is typically at the root of the API version
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

    print(f"正在向以下地址发出请求: {url}")

    try:
        # This is a GET request, so no data or method needs to be specified in the Request object
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                response_body = response.read().decode("utf-8")
                data = json.loads(response_body)
                print("\n--- 可用的模型列表 ---")
                # Pretty print the JSON for better readability
                print(json.dumps(data, indent=2))
                print("\n--------------------------")

                # Extract and suggest a model to use
                if 'models' in data and data['models']:
                    # Find a model that supports 'generateContent'
                    for model in data['models']:
                        if 'generateContent' in model.get('supportedGenerationMethods', []):
                            print(f"\n建议: 您可以尝试使用这个模型名称: '{model['name']}'")
                            # It returns 'models/gemini-1.0-pro', we need just 'gemini-1.0-pro'
                            model_id = model['name'].split('/')[-1]
                            print(f"在我们的脚本中，这意味着将 model_name 设置为: '{model_id}'")
                            return
                    print("\n警告: 找到了模型，但似乎没有一个明确支持 'generateContent'。")

            else:
                print(f"请求失败，HTTP 状态码: {response.status}")
                print(response.read().decode("utf-8"))

    except urllib.error.HTTPError as e:
        print(f"API 请求失败，HTTP 状态码: {e.code}")
        print(f"错误详情: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"发生未知错误: {e}")

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("错误：GEMINI_API_KEY 环境变量未设置。")
        print("请设置您的 API 密钥: export GEMINI_API_KEY='YOUR_API_KEY'")
        return
    list_available_models(api_key)

if __name__ == "__main__":
    main()
