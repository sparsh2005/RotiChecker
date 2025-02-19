# server.py

import os
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from app import roti_checker  # your CV logic

app = Flask(__name__)

# Folder to store uploads temporarily
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Limit upload size if desired (16 MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET'])
def index():
    # Serve our main page (templates/index.html)
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Handle AJAX file upload, run roti analysis, return JSON scores."""
    if 'roti_image' not in request.files:
        return jsonify({"error": "No file found"}), 400

    file = request.files['roti_image']
    if file.filename == '':
        return jsonify({"error": "File name is empty"}), 400

    # Create a temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file.save(tmp.name)
        # Run the roti checker
        results = roti_checker(tmp.name)
        # Clean up
        os.unlink(tmp.name)

    if results is None:
        return jsonify({"error": "Could not analyze roti image"}), 400

    # Extract the three scores we need
    roundness = results["circularity_score"]
    color = results["color_score"]
    overall = results["overall_score"]

    return jsonify({
        "roundness": roundness,
        "color": color,
        "overall": overall
    })

if __name__ == '__main__':
    app.run(debug=True)