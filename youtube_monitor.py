import os
import json
import google.generativeai as genai
from googleapiclient.discovery import build

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VIDEO_URL = os.getenv("VIDEO_URL")

genai.configure(api_key=GEMINI_API_KEY)

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


def extract_video_id(url):
    if "watch?v=" in url:
        video_id = url.split("watch?v=")[1]
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1]
    else:
        video_id = url

    return video_id.split("?")[0]


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


def analyze_comments(comments):

    texts = [c["text"] for c in comments]

    joined = "\n".join(
        [f"{i+1}. {t}" for i, t in enumerate(texts)]
    )

    prompt = f"""
次のYouTubeコメントから誹謗中傷を抽出してください

{joined}

番号だけ出してください
例: 2,5,8
"""

    response = model.generate_content(prompt)

    return response.text.strip()


def create_report(comments, result):

    indexes = []

    try:
        indexes = [int(x)-1 for x in result.split(",")]
    except:
        pass

    flagged = []

    for i in indexes:
        if i < len(comments):

            flagged.append({
                "author": comments[i]["author"],
                "comment": comments[i]["text"]
            })

    report = {
        "count": len(flagged),
        "comments": flagged
    }

    with open("report.json","w",encoding="utf-8") as f:
        json.dump(report,f,indent=2,ensure_ascii=False)


def main():

    video_id = extract_video_id(VIDEO_URL)

    comments = get_comments(video_id)

    result = analyze_comments(comments)

    create_report(comments,result)

    print("AI検知完了")


if __name__ == "__main__":
    main()
