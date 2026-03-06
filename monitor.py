import os
import sys
from google import genai

print("=== AI Police Agent Start ===")

# APIキー確認
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY is not set.")
    sys.exit(1)

# クライアント初期化
client = genai.Client(api_key=api_key)

# 判定する文章
text = "お前は本当に頭が悪いな。社会のゴミだから今すぐ消えろ。"

# AIへの指示
prompt = f"""
次の文章をモデレーションしてください。
1 = 問題なし, 2 = 攻撃的, 3 = ヘイト, 4 = 暴力
文章: {text}
出力形式: 番号と理由を簡潔に。
"""

try:
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    print("=== Gemini Response ===")
    print(response.text)
    print("=======================")
except Exception as e:
    print("Gemini API Error:", str(e))
    sys.exit(1)

print("=== AI Police Agent Finished ===")
