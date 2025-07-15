from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
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
        'default_search': 'ytsearch5',
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0',
            'Accept-Language': 'en-US,en;q=0.9'
        }
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
        'http_headers': {
            'User-Agent': 'Mozilla/5.0',
            'Accept-Language': 'en-US,en;q=0.9'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
            audio_url = info.get('url')
            if not audio_url:
                raise Exception("No audio URL found")
            print(f"[INFO] Streaming audio from: {audio_url}")

        def generate():
            with requests.get(audio_url, stream=True) as r:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk

        # Default to audio/mp4 (which covers most YouTube streams)
        return Response(generate(), content_type='audio/mp4')

    except yt_dlp.utils.DownloadError as e:
        print(f"[YT-DLP ERROR] Video not downloadable: {e}")
        return jsonify({'error': 'Video not available'}), 404

    except Exception as e:
        print(f"[ERROR] Proxy stream failed: {e}")
        return jsonify({'error': 'Stream failed'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
