import json
from flask import Flask, render_template_string

app = Flask(__name__)

html = """

<h1>CyberPolice Dashboard</h1>

<h2>悪質ユーザーランキング</h2>

{% for r in ranking %}

<p>
ユーザー: {{r.user}}  
違反数: {{r.count}}
</p>

{% endfor %}

<hr>

<h2>通報候補コメント</h2>

{% for c in comments %}

<div style="border:1px solid #ccc;padding:10px;margin:10px">

<p><b>ユーザー</b>: {{c.author}}</p>
<p><b>コメント</b>: {{c.text}}</p>

<a href="https://support.google.com/youtube/answer/2802027" target="_blank">
<button>通報ページを開く</button>
</a>

</div>

{% endfor %}

"""

@app.route("/")

def home():

    with open("report.json", encoding="utf-8") as f:
        data = json.load(f)

    return render_template_string(
        html,
        ranking=data["ranking"],
        comments=data["flagged_comments"]
    )

app.run(port=5000)
