import json
from datetime import datetime

# 仮の動画データ（あとでYouTube APIに変える）
video_id = "test123"
title = "テスト動画"

new_video = {
    "video_id": video_id,
    "title": title,
    "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "ranking": [
        {"author": "troll_user", "count": 3}
    ],
    "flagged_comments": [
        {"author": "troll_user", "text": "これは荒らしコメント"}
    ]
}

# report.json 読み込み
with open("report.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 重複チェック
exists = any(v["video_id"] == video_id for v in data["videos"])

if not exists:
    data["videos"].append(new_video)

# 保存
with open("report.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("分析完了")

