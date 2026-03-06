import os
import sys
from google import genai

print("=== AI Police Agent Start ===")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY not set")
    sys.exit(1)

client = genai.Client(api_key=api_key)

text = "お前は本当に頭が悪いな。社会のゴミだから今すぐ消えろ。"

prompt = f"""
次の文章をモデレーションしてください。

分類:
1 = 問題なし
2 = 攻撃的
3 = ヘイト
4 = 脅迫

文章:
{text}
"""

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    print("=== Gemini Response ===")
    print(response.text)

except Exception as e:
    print("Gemini API Error:", e)
    sys.exit(1)

print("=== AI Police Agent Finished ===")
