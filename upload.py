from flask import Flask, request, redirect, flash, render_template, url_for, send_file
import os
import pandas as pd
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from werkzeug.utils import secure_filename
from matplotlib.figure import Figure
import io
import base64


# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'static/files'
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}

# Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#FORM.HTML
@app.route('/')
def home():
    # Render the main form page
    return render_template('form.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If user does not select a file, the browser submits an empty part without a filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Ensure the UPLOAD_FOLDER exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(file_path)
            flash('File successfully uploaded')
            return redirect(request.url)
    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)