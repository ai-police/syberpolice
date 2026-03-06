import os
import requests
from urllib.parse import urlparse, parse_qs
from google import genai

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# YouTube URLからVIDEO_IDを取得
def extract_video_id(url):
    parsed_url = urlparse(url)
    if "youtube.com" in parsed_url.netloc:
        return parse_qs(parsed_url.query)["v"][0]
    elif "youtu.be" in parsed_url.netloc:
        return parsed_url.path[1:]
    else:
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

    for item in data["items"]:
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

結果は次のどちらかだけで答えてください

危険
安全
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text.strip()


def main():

    url = input("YouTube動画URLを入力してください: ")

    video_id = extract_video_id(url)

    if not video_id:
        print("URLが正しくありません")
        return

    comments = get_comments(video_id)

    print("\n危険コメント一覧\n")

    for c in comments:

        result = analyze_comment(c)

        if "危険" in result:
            print("⚠️", c)
            print("------------------")


if __name__ == "__main__":
    main()
