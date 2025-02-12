# server.py

import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from app import roti_checker  # Import your roti_checker function

app = Flask(__name__)

# Create an 'uploads' folder if it doesn't exist
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Optional: limit upload size (e.g., 16 MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'roti_image' not in request.files:
            return render_template('index.html', error="No file part in request.")

        file = request.files['roti_image']
        if file.filename == '':
            return render_template('index.html', error="No file selected!")

        # Secure the filename (removes unsafe characters, etc.)
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Save file temporarily
        file.save(filepath)

        # Call the roti checker function
        results = roti_checker(filepath)
        if results is None:
            # roti_checker returned None => error or no roti found
            return render_template('index.html', error="No roti found or invalid image!")
        
        return render_template('index.html', 
                               filename=filename,
                               circularity=results["circularity"],
                               circularity_score=results["circularity_score"],
                               std_dev=results["std_dev"],
                               color_score=results["color_score"],
                               overall_score=results["overall_score"])

    # GET request => just show the upload form
    return render_template('index.html')

if __name__ == '__main__':
    # Run the flask app
    app.run(debug=True)