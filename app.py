
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import socket

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
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
            audio_url = info.get('url')

        if not audio_url:
            return jsonify({'error': 'Unable to extract audio URL'}), 500

        return jsonify({'url': audio_url})

    except Exception as e:
        print(f"[ERROR] Stream fetch failed: {e}")
        return jsonify({'error': 'Stream failed'}), 500


if __name__ == '__main__':
    # Run on all IPs to support mobile on same WiFi
    app.run(host='0.0.0.0', port=5000, debug=False)
