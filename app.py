import json
import os
import threading
import tkinter as tk
import uuid
from pathlib import Path
from tkinter import filedialog

from flask import (
    Flask, jsonify, redirect, render_template,
    request, send_file, session, url_for,
)

from organizer import (
    build_statistics,
    classify_all,
    clear_all_history,
    delete_run,
    generate_report,
    load_history,
    move_files,
    save_to_database,
    scan_directory,
)
from organizer.mover import undo_last_run

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Stats dicts contain a ~100 KB base64 chart — far too large for a 4 KB cookie.
# Write them to disk and store only a UUID key in the session cookie.
SESSIONS_DIR = Path("flask_sessions")
SESSIONS_DIR.mkdir(exist_ok=True)


def _make_serialisable(obj):
    """Recursively convert NumPy scalars to plain Python for json.dumps."""
    if isinstance(obj, dict):
        return {k: _make_serialisable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_make_serialisable(i) for i in obj]
    try:
        import numpy as np
        if isinstance(obj, np.integer):  return int(obj)
        if isinstance(obj, np.floating): return float(obj)
    except ImportError:
        pass
    return obj


def save_stats(stats: dict) -> str:
    key  = str(uuid.uuid4())
    path = SESSIONS_DIR / f"{key}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_make_serialisable(stats), f)
    return key


def load_stats(key: str) -> dict | None:
    if not key:
        return None
    path = SESSIONS_DIR / f"{key}.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── ROUTES ───────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/browse")
def browse():
    result = {"path": ""}

    def open_dialog():
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        result["path"] = filedialog.askdirectory(title="Select a Folder to Organize")
        root.destroy()

    t = threading.Thread(target=open_dialog)
    t.start()
    t.join()

    if result["path"]:
        return jsonify({"success": True, "path": result["path"]})
    return jsonify({"success": False, "path": ""})


@app.route("/organize", methods=["POST"])
def organize():
    data               = request.get_json()
    folder_path        = data.get("folder_path", "").strip()
    include_subfolders = data.get("include_subfolders", False)

    if not folder_path:
        return jsonify({"success": False, "error": "No folder selected."})

    try:
        files = scan_directory(folder_path, include_subfolders)
        if not files:
            return jsonify({"success": False, "error": "No files found in this folder."})

        classified  = classify_all(files)
        organized   = move_files(classified, folder_path)
        report_path = generate_report(organized)
        stats       = build_statistics(organized)

        stats["report_path"] = report_path
        stats["folder_path"] = folder_path

        session["stats_key"] = save_stats(stats)
        save_to_database(stats, folder_path)

        return jsonify({"success": True, "redirect": url_for("result")})

    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)})
    except NotADirectoryError as e:
        return jsonify({"success": False, "error": str(e)})
    except PermissionError:
        return jsonify({"success": False, "error": "Permission denied. Cannot access this folder."})
    except Exception as e:
        return jsonify({"success": False, "error": f"Something went wrong: {str(e)}"})


@app.route("/result")
def result():
    stats = load_stats(session.get("stats_key"))
    if not stats:
        return redirect(url_for("index"))
    return render_template("result.html", stats=stats)


@app.route("/download-report")
def download_report():
    stats = load_stats(session.get("stats_key"))
    if not stats or not stats.get("report_path"):
        return redirect(url_for("index"))
    return send_file(stats["report_path"], as_attachment=True, download_name="file_report.csv")


@app.route("/undo", methods=["POST"])
def undo():
    return jsonify(undo_last_run())


@app.route("/history")
def history():
    return render_template("history.html", runs=load_history())


@app.route("/delete-run/<int:run_id>", methods=["POST"])
def delete_run_route(run_id):
    if delete_run(run_id):
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Run not found."})


@app.route("/clear-history", methods=["POST"])
def clear_history():
    if clear_all_history():
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "No history found."})

import webbrowser
import threading

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(debug=False)