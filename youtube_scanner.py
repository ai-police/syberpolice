import json

with open("report.json", "r", encoding="utf-8") as f:
    data = json.load(f)

new_video = {
    "video_id": "abc123",
    "title": "動画タイトル",
    "analyzed_at": "2026-03-08",
    "ranking": [],
    "flagged_comments": []
}

data["videos"].append(new_video)

with open("report.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
