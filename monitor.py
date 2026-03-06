import os
import sys
from google import genai

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    # GitHub Actions の入力から文章を取得 (なければ引数から取得)
    # ※後で説明しますが、ここでは環境変数や引数で受け取ります
    text_to_check = os.getenv("TARGET_TEXT", "チェック対象なし")

    prompt = f"この文章に不適切な表現が含まれているか判定してください: {text_to_check}"
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    print(f"【判定結果】\n{response.text}")

if __name__ == "__main__":
    main()
