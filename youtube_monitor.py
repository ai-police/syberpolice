import os
import json
import time
import re
from googleapiclient.discovery import build
import google.generativeai as genai


# ===== 環境変数 =====
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VIDEO_URL = os.getenv("VIDEO_URL")


# ===== Gemini =====
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


# ===== YouTube API =====
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


# =========================
# 動画ID抽出（完全版）
# =========================
def extract_video_id(url):

    patterns = [
        r"v=([^&]+)",
        r"youtu\.be/([^?&]+)"
    ]

    for pattern in patterns:

        match = re.search(pattern, url)

        if match:
            return match.group(1)

    return url


# =========================
# コメント取得
# =========================
def get_comments(video_id):

    comments = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=50,
        textFormat="plainText"
    )

    response = request.execute()

    for item in response["items"]:

        snippet = item["snippet"]["topLevelComment"]["snippet"]

        comments.append({
            "author": snippet["authorDisplayName"],
            "text": snippet["textDisplay"]
        })

    return comments


# =========================
# Geminiリトライ
# =========================
def gemini_request(prompt):

    retry = 0

    while retry < 5:

        try:

            response = model.generate_content(prompt)

            return response.text.strip()

        except Exception as e:

            retry += 1

            print("Geminiエラー:", e)
            print("40秒待機...")

            time.sleep(40)

    return ""


# =========================
# AI分析
# =========================
def analyze_comments(comments):

    texts = [c["text"] for c in comments]

    joined = "\n".join(
        [f"{i+1}. {t}" for i, t in enumerate(texts)]
    )

    prompt = f"""
次のYouTubeコメントから誹謗中傷を抽出してください。

{joined}

番号だけをカンマ区切りで出してください
例: 2,5,8
"""

    return gemini_request(prompt)


# =========================
# レポート作成
# =========================
def create_report(comments, result):

    indexes = []

    try:
        indexes = [int(x.strip()) - 1 for x in result.split(",")]
    except:
        pass

    flagged = []

    for i in indexes:

        if 0 <= i < len(comments):

            flagged.append({
                "author": comments[i]["author"],
                "comment": comments[i]["text"]
            })

    report = {
        "flagged_count": len(flagged),
        "comments": flagged
    }

    with open("report.json", "w", encoding="utf-8") as f:

        json.dump(report, f, indent=2, ensure_ascii=False)


# =========================
# main
# =========================
def main():

    video_id = extract_video_id(VIDEO_URL)

    print("動画ID:", video_id)

    comments = get_comments(video_id)

    print("取得コメント:", len(comments))

    result = analyze_comments(comments)

    print("AI結果:", result)

    create_report(comments, result)

    print("完了")


if __name__ == "__main__":
    main()
