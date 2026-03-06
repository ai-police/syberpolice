from monitor import analyze_text

def get_youtube_comments():
    # 仮のコメント（テスト用）
    return [
        "この動画最高！",
        "消えろ",
        "お前バカだろ"
    ]

def main():
    comments = get_youtube_comments()

    for comment in comments:
        print("コメント:", comment)
        result = analyze_text(comment)
        print("AI判定:", result)
        print("------")

if __name__ == "__main__":
    main()
