import os
import requests
from google import genai

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

VIDEO_ID = "dQw4w9WgXcQ"  # 監視したい動画ID


def get_comments():
    url = "https://www.googleapis.com/youtube/v3/commentThreads"

    params = {
        "part": "snippet",
        "videoId": VIDEO_ID,
        "key": YOUTUBE_API_KEY,
        "maxResults": 10
    }

    res = requests.get(url, params=params)
    data = res.json()

    comments = []

    for item in data["items"]:
        text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(text)

    return comments


def analyze_comment(comment):

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
次のコメントが攻撃的・ヘイト・暴言か判定してください。

コメント:
{comment}

危険なら「危険」
問題なければ「安全」
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text


def main():

    comments = get_comments()

    for c in comments:

        result = analyze_comment(c)

        print("コメント:", c)
        print("判定:", result)
        print("------------------")


if __name__ == "__main__":
    main()
