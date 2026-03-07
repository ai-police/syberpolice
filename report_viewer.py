import json

with open("report.json","r",encoding="utf-8") as f:
    data = json.load(f)

print("\n===== 通報候補 =====\n")

for i,c in enumerate(data["flagged_comments"]):

    print(f"[{i}]")
    print("ユーザー:",c["author"])
    print("コメント:",c["text"])
    print("通報リンク:")
    print("https://support.google.com/youtube/answer/2802027")
    print()
