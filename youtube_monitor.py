import os
import requests
from urllib.parse import urlparse, parse_qs
from google import genai

# 環境変数（GitHub Actionsから渡される）
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VIDEO_URL = os.getenv("VIDEO_URL")


# YouTube URLからVIDEO_IDを取得
def extract_video_id(url):

    parsed_url = urlparse(url)

    if "youtube.com" in parsed_url.netloc:
        return parse_qs(parsed_url.query).get("v", [None])[0]

    elif "youtu.be" in parsed_url.netloc:
        return parsed_url.path[1:]

    return None


# コメント取得
def get_comments(video_id):

    url = "https://www.googleapis.com/youtube/v3/commentThreads"

    params = {
        "part": "snippet",
        "videoId": video_id,
        "key": YOUTUBE_API_KEY,
        "maxResults": 20
    }

    res = requests.get(url, params=params)
    data = res.json()

    comments = []

    for item in data.get("items", []):
        text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(text)

    return comments


# AI判定
def analyze_comment(comment):

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
次のコメントが誹謗中傷・攻撃的・ヘイトか判定してください。

コメント:
{comment}

結果は必ず次のどちらかだけで答えてください

危険
安全
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text.strip()


def main():

    if not VIDEO_URL:
        print("VIDEO_URL が設定されていません")
        return

    video_id = extract_video_id(VIDEO_URL)

    if not video_id:
        print("動画URLが正しくありません")
        return

    print("動画ID:", video_id)
    print("コメント取得中...\n")

    comments = get_comments(video_id)

    if not comments:
        print("コメントが取得できませんでした")
        return

    print("危険コメント一覧\n")

    for comment in comments:

        try:

            result = analyze_comment(comment)

            if "危険" in result:
                print("⚠️", comment)
                print("----------------")

        except Exception as e:

            print("AI判定エラー:", e)


if __name__ == "__main__":
    main()

