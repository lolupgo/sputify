
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import socket
import requests

app = Flask(__name__)
CORS(app)

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Missing query'}), 400

    ydl_opts = {
        'quiet': True,
        'extract_flat': 'in_playlist',
        'format': 'bestaudio/best',
        'default_search': 'ytsearch5'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)

        entries = info['entries'] if 'entries' in info else [info]

        results = []
        for entry in entries:
            if entry.get('id') and entry.get('title'):
                results.append({
                    'title': entry['title'],
                    'id': entry['id']
                })

        return jsonify(results)

    except Exception as e:
        print(f"[ERROR] YouTube search failed: {e}")
        return jsonify({'error': 'Search failed'}), 500


@app.route('/stream/<video_id>')
def stream(video_id):
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'noplaylist': True,
        'default_search': 'ytsearch',
        'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept-Language': 'en-US,en;q=0.9',
         }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
            audio_url = info.get('url')

        if not audio_url:
            return jsonify({'error': 'Unable to extract audio URL'}), 500
        def generate():
            with requests.get(audio_url, stream=True) as r:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk

        return Response(generate(), content_type='audio/mpeg')

    except Exception as e:
        print(f"[ERROR] Proxy stream failed: {e}")
        return jsonify({'error': 'Stream failed'}), 500


if __name__ == '__main__':
    # Run on all IPs to support mobile on same WiFi
    app.run(host='0.0.0.0', port=5000, debug=False)
