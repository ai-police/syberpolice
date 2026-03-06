import os
from google import genai
from google.genai import types

def main():
    # 1. APIキーを環境変数から取得
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY が設定されていません。")

    # 2. クライアントの初期化 (最新のSDK作法)
    client = genai.Client(api_key=api_key)

    # 3. プロンプトの内容 (監視対象の文章など)
    prompt = "この文章に不適切な表現が含まれているか判定してください: [ここに監視対象のテキスト]"

    # 4. モデルの指定と実行
    # 修正済み: モデル名を "gemini-2.0-flash" に固定
    model_name = "gemini-2.0-flash"
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        print("AIの分析結果:")
        print(response.text)
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
