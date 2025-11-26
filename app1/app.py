import os
import json
from datetime import datetime
from flask import Flask, render_template_string, request

app = Flask(__name__)

# ENV CONFIG
COLOR = os.environ.get("APP_COLOR", "blue")
NAME = os.environ.get("APP_NAME", "app")
PORT = int(os.environ.get("PORT", 5000))

# LOGGING DIRECTORY
LOG_DIR = f"/var/log/{NAME}"
LOG_FILE = os.path.join(LOG_DIR, f"{NAME}.log")
os.makedirs(LOG_DIR, exist_ok=True)

# IN-MEMORY click state
clicks = 0

# HTML Template
TEMPLATE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>{{name}} - {{color}}</title>
    <style>
      body { background: {{color}}; color: white; font-family: Arial; text-align:center; padding-top:40px;}
      .info { background: rgba(0,0,0,0.25); display:inline-block; padding:25px; border-radius:8px; }
      button { font-size:1.2rem; padding:10px 18px; margin-top:15px; border-radius:5px; }
    </style>
  </head>
  <body>
    <div class="info">
      <h1>{{name}} ({{color}})</h1>
      <p>Host: {{host}}</p>
      <p>Time: <span id="time">{{time}}</span></p>

      <p>Clicks until next page: <b><span id="target">{{target}}</span></b></p>
      <p>Button clicked: <b><span id="count">0</span></b></p>

      <button id="goBtn">Click me (wait 3:2:1)</button>
    </div>

    <script>
      const target = {{target}};
      const nextUrl = "{{next_url}}";

      document.getElementById('goBtn').addEventListener('click', async function() {
        const countEl = document.getElementById('count');
        let c = parseInt(countEl.textContent);
        c += 1;
        countEl.textContent = c;

        const btn = this;

        // countdown 3..2..1
        for (let i=3; i>=1; i--) {
          btn.textContent = i;
          await new Promise(r => setTimeout(r, 500));
        }
        btn.textContent = "Click me (wait 3:2:1)";

        if (c >= target) {
          fetch("/reset_count", {method:"POST"});
          window.location.href = nextUrl;
        } else {
          fetch("/log_click", {method:"POST"});
        }
      });
    </script>
  </body>
</html>
"""

# Write JSON log record
def write_log(event, extra=None):
    rec = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "app": NAME,
        "color": COLOR,
        "event": event,
    }
    if extra:
        rec.update(extra)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


# Routes -------------------------------------
@app.route("/")
def index():
    global clicks
    target_map = {"app1": 3, "app2": 2, "app3": 1}
    next_map = {"app1": "/app2/", "app2": "/app3/", "app3": "/app1/"}

    target = target_map.get(NAME, 3)
    next_url = next_map.get(NAME, "/")

    now = datetime.utcnow().isoformat() + "Z"
    write_log("page_view", {"host": request.host})

    return render_template_string(
        TEMPLATE,
        name=NAME,
        color=COLOR,
        host=request.host,
        time=now,
        target=target,
        next_url=next_url,
    )


@app.route("/log_click", methods=["POST"])
def log_click():
    global clicks
    clicks += 1
    write_log("click", {"count": clicks})
    return ("", 204)


@app.route("/reset_count", methods=["POST"])
def reset_count():
    global clicks
    clicks = 0
    write_log("reset", {"count": clicks})
    return ("", 204)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
