import os
import json
import time
import re
from collections import Counter
from googleapiclient.discovery import build
import google.generativeai as genai

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VIDEO_URL = os.getenv("VIDEO_URL")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def extract_video_id(url):

    patterns = [
        r"v=([^&]+)",
        r"youtu\.be/([^?&]+)"
    ]

    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)

    return url


def get_comments(video_id):

    comments = []
    next_page = None

    while len(comments) < 1000:

        req = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page,
            textFormat="plainText"
        )

        res = req.execute()

        for item in res["items"]:

            s = item["snippet"]["topLevelComment"]["snippet"]

            comments.append({
                "author": s["authorDisplayName"],
                "text": s["textDisplay"]
            })

        next_page = res.get("nextPageToken")

        if not next_page:
            break

    return comments


def gemini_request(prompt):

    retry = 0

    while retry < 5:

        try:

            r = model.generate_content(prompt)

            return r.text.strip()

        except Exception as e:

            retry += 1
            print("Geminiエラー:", e)
            print("40秒待機...")

            time.sleep(40)

    return ""


def analyze(comments):

    texts = [c["text"] for c in comments]

    joined = "\n".join(
        [f"{i+1}. {t}" for i, t in enumerate(texts[:50])]
    )

    prompt = f"""
次のコメントから誹謗中傷を抽出してください

{joined}

番号だけ出してください
例: 2,5,8
"""

    result = gemini_request(prompt)

    indexes = []

    try:
        indexes = [int(x)-1 for x in result.split(",")]
    except:
        pass

    flagged = []

    for i in indexes:

        if 0 <= i < len(comments):

            flagged.append(comments[i])

    return flagged


def build_ranking(flagged):

    authors = [c["author"] for c in flagged]

    counter = Counter(authors)

    ranking = []

    for user, count in counter.most_common():

        ranking.append({
            "user": user,
            "count": count
        })

    return ranking


def main():

    video_id = extract_video_id(VIDEO_URL)

    print("動画ID:", video_id)

    comments = get_comments(video_id)

    print("取得コメント:", len(comments))

    flagged = analyze(comments)

    ranking = build_ranking(flagged)

    report = {
        "flagged_comments": flagged,
        "ranking": ranking
    }

    with open("report.json", "w", encoding="utf-8") as f:

        json.dump(report, f, indent=2, ensure_ascii=False)

    print("report.json生成完了")


if __name__ == "__main__":
    main()

