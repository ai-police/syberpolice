import os
import google.generativeai as genai
from googleapiclient.discovery import build

# =========================
# APIキー設定
# =========================

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

youtube = build(
    "youtube",
    "v3",
    developerKey=YOUTUBE_API_KEY
)

model = genai.GenerativeModel("gemini-2.5-flash")


# =========================
# URLから動画IDを取得
# =========================

def extract_video_id(url):

    if "watch?v=" in url:
        video_id = url.split("watch?v=")[1]

    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1]

    else:
        video_id = url

    # ?以降を削除
    video_id = video_id.split("?")[0]

    return video_id


# =========================
# コメント取得
# =========================

def get_comments(video_id, max_results=50):

    comments = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_results,
        textFormat="plainText"
    )

    response = request.execute()

    for item in response["items"]:

        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]

        comments.append(comment)

    return comments


# =========================
# AI誹謗中傷判定（まとめて）
# =========================

def analyze_comments(comments):

    joined_comments = "\n".join(
        [f"{i+1}. {c}" for i, c in enumerate(comments)]
    )

    prompt = f"""
次のYouTubeコメントの中から誹謗中傷・差別・攻撃的なコメントだけを抽出してください。

コメント一覧:
{joined_comments}

出力形式:
番号とコメントをそのまま出してください。
"""

    try:

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        return f"AI判定エラー: {e}"


# =========================
# メイン処理
# =========================

def main():

    url = os.getenv("VIDEO_URL")

    if not url:
        print("VIDEO_URL が設定されていません")
        return

    print("動画URL:", url)

    video_id = extract_video_id(url)

    print("動画ID:", video_id)

    print("コメント取得中...")

    comments = get_comments(video_id)

    print(f"{len(comments)}件のコメント取得")

    print("AI分析中...")

    result = analyze_comments(comments)

    print("\n===== 検出された問題コメント =====\n")

    print(result)


if __name__ == "__main__":
    main()




