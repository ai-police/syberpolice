import os
import re
from google import genai
from googleapiclient.discovery import build

# Geminiクライアント
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# YouTube API
youtube = build(
    "youtube",
    "v3",
    developerKey=os.environ["YOUTUBE_API_KEY"]
)


def get_video_id(url):
    """YouTube URLから動画IDを取得"""
    match = re.search(r"v=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    return None


def get_comments(video_id, max_results=20):
    """コメント取得"""
    comments = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_results,
        textFormat="plainText"
    )

    response = request.execute()

    for item in response["items"]:
        text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(text)

    return comments


def analyze_comments(comments):
    """Geminiでまとめて判定"""

    comment_block = "\n".join(
        [f"{i+1}. {c}" for i, c in enumerate(comments)]
    )

    prompt = f"""
あなたは誹謗中傷監視AIです。

以下のYouTubeコメントの中から
攻撃的・誹謗中傷・悪質なものを特定してください。

結果は以下形式で出してください

番号: 理由

コメント一覧
{comment_block}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def main():
    url = input("YouTube動画URLを入力してください: ")

    video_id = get_video_id(url)

    if not video_id:
        print("動画URLが正しくありません")
        return

    comments = get_comments(video_id)

    print("\n取得コメント:")
    for c in comments:
        print("-", c)

    print("\nAI判定中...\n")

    result = analyze_comments(comments)

    print("【判定結果】")
    print(result)


if __name__ == "__main__":
    main()
