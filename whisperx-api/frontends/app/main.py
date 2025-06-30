from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# Get the backend URL from an environment variable, with a default for local testing
BACKEND_URL = os.environ.get("WHISPERX_API_URL", "http://whisperx-api:8000")

@app.route('/')
def index():
    return render_template('index.html')


from flask import send_file, Response
import tempfile
import json

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Prepare the data for the backend API call
    files = {'file': (file.filename, file.read(), file.content_type)}
    params = {
        'model_size': request.form.get('model_size', 'small'),
        'language': request.form.get('language', 'auto'),
        'diarize': request.form.get('diarize') == 'on',
    }

    # Only add speaker min/max if they are provided
    speaker_min = request.form.get('speaker_min')
    if speaker_min:
        params['speaker_min'] = speaker_min

    speaker_max = request.form.get('speaker_max')
    if speaker_max:
        params['speaker_max'] = speaker_max

    # Get output formats (can be multiple)
    output_formats = request.form.getlist('output_formats')
    if not output_formats:
        output_formats = ['json']

    try:
        # Forward the request to the backend service
        response = requests.post(f"{BACKEND_URL}/transcription/", params=params, files=files)
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()

        # Prepare downloadable files for each format
        temp_files = {}
        download_links = {}
        for fmt in output_formats:
            if fmt == 'json':
                tf = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w', encoding='utf-8')
                json.dump(result, tf, ensure_ascii=False, indent=2)
                tf.close()
                temp_files['json'] = tf.name
                download_links['json'] = f"/download?file={tf.name}&type=json"
            elif fmt == 'txt':
                tf = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8')
                tf.write(result.get('text', ''))
                tf.close()
                temp_files['txt'] = tf.name
                download_links['txt'] = f"/download?file={tf.name}&type=txt"
            elif fmt == 'srt':
                # Simple SRT export (for demo)
                tf = tempfile.NamedTemporaryFile(delete=False, suffix='.srt', mode='w', encoding='utf-8')
                for i, seg in enumerate(result.get('segments', []), 1):
                    start = seg['start']
                    end = seg['end']
                    text = seg['text']
                    tf.write(f"{i}\n{format_srt_time(start)} --> {format_srt_time(end)}\n{text}\n\n")
                tf.close()
                temp_files['srt'] = tf.name
                download_links['srt'] = f"/download?file={tf.name}&type=srt"

        return jsonify({
            'result': result,
            'download_links': download_links
        }), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500


def format_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

# Download endpoint for generated files
@app.route('/download')
def download():
    file = request.args.get('file')
    filetype = request.args.get('type', 'txt')
    if not file or not os.path.exists(file):
        return "File not found", 404
    mimetype = {
        'json': 'application/json',
        'txt': 'text/plain',
        'srt': 'application/x-subrip',
    }.get(filetype, 'text/plain')
    return send_file(file, as_attachment=True, mimetype=mimetype)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
