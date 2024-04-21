import os
import re
import threading
from flask import Flask, render_template, request, send_file, url_for
from yt_dlp import YoutubeDL

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

def sanitize_filename(filename):
    return re.sub(r'[\/:*?"<>|]', '_', filename)

def delete_file_after_delay(file_path, delay_seconds):
    def delete_file():
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
    timer = threading.Timer(delay_seconds, delete_file)
    timer.start()

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['video_url']
    download_format = request.form['download_format']

    if download_format == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            }],
            'outtmpl': '%(title)s.%(ext)s',
        }
        file_extension = 'mp3'
    elif download_format == 'mp4':
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'EmbedThumbnail',
            }],
            'outtmpl': '%(title)s.%(ext)s',
        }
        file_extension = 'mp4'
    else:
        return "Invalid download format"

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)

    downloaded_file = ydl.prepare_filename(info)

    base_filename = os.path.splitext(downloaded_file)[0]
    final_filename = f"{base_filename}.{file_extension}"
    final_filename_sanitized = sanitize_filename(final_filename)

    os.rename(final_filename, final_filename_sanitized)

    delete_file_after_delay(final_filename_sanitized, 300)

    return send_file(final_filename_sanitized, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
