import asyncio
from flask import Flask, url_for, render_template, request, jsonify, send_file
from api import download_and_zip, delete_folder_later
from translation import translate_external
from event_loop import loop
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/download", methods=["POST"])
def download_api():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON provided"}), 400

    name = data.get("name", "placeholder")
    urls = data.get("url_list", [])

    if not isinstance(urls, list):
        return jsonify({"error": "url_list must be an array"}), 400

    future = asyncio.run_coroutine_threadsafe(download_and_zip(urls, name), loop)
    file_name = future.result()

    dl_url = url_for("download_file", filename=file_name, _external=True)

    asyncio.run_coroutine_threadsafe(delete_folder_later(name), loop)

    return jsonify({"dl_url": dl_url})

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_file(filename, as_attachment=True)


@app.route("/api/translate", methods=["POST"])
def translate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON provided"}), 400

    text = data.get("text")
    if not text or not isinstance(text, str) or text.strip() == "":
        return jsonify({"error": "No text provided"}), 400

    try:
        translated, is_ok = translate_external(text)
        return jsonify({
            "ok": is_ok,
            "target": "en",
            "translated": translated
        })
    except Exception as e:
        return jsonify({"ok": False, "error": f"translation failed: {e}"}), 502


if __name__ == "__main__":
    app.run(host='0.0.0.0',port= 8020)