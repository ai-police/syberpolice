import os
import json
import time
from googleapiclient.discovery import build
import google.generativeai as genai


# ===== 環境変数 =====
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VIDEO_URL = os.getenv("VIDEO_URL")

# ===== Gemini設定 =====
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ===== YouTube API =====
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


# =========================
# 動画ID取得
# =========================
def extract_video_id(url):

    if "watch?v=" in url:
        video_id = url.split("watch?v=")[1]

    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1]

    else:
        video_id = url

    return video_id.split("&")[0]


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
# Geminiリトライ関数
# =========================
def gemini_request(prompt):

    retry = 0
    max_retry = 5

    while retry < max_retry:

        try:

            response = model.generate_content(prompt)

            return response.text.strip()

        except Exception as e:

            retry += 1

            print("Gemini APIエラー:", e)
            print("40秒待機して再試行...")

            time.sleep(40)

    print("最大リトライ回数に到達")
    return ""


# =========================
# AIコメント分析
# =========================
def analyze_comments(comments):

    texts = [c["text"] for c in comments]

    joined = "\n".join(
        [f"{i+1}. {t}" for i, t in enumerate(texts)]
    )

    prompt = f"""
次のYouTubeコメントから誹謗中傷を抽出してください。

{joined}

誹謗中傷と思われるコメントの番号だけを
カンマ区切りで出してください。

例:
2,5,8
"""

    result = gemini_request(prompt)

    return result


# =========================
# レポート作成
# =========================
def create_report(comments, result):

    indexes = []

    try:
        indexes = [int(x.strip()) - 1 for x in result.split(",")]

    except:
        indexes = []

    flagged = []

    for i in indexes:

        if i < len(comments):

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

    print("report.json作成完了")


# =========================
# メイン
# =========================
def main():

    if not VIDEO_URL:
        print("VIDEO_URLが設定されていません")
        return

    video_id = extract_video_id(VIDEO_URL)

    print("動画ID:", video_id)

    comments = get_comments(video_id)

    print("取得コメント数:", len(comments))

    if len(comments) == 0:
        print("コメントがありません")
        return

    result = analyze_comments(comments)

    print("AI解析結果:", result)

    create_report(comments, result)

    print("AI検知完了")


if __name__ == "__main__":
    main()
