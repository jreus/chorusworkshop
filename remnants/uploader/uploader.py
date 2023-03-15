'''
In Search of Good Ancestors / Ahnen in Arbeit

Uploader. A simple web interface for uploading audio voice recordings and
linked annotations / future wishes to a shared local webserver.

(c) J Chaim Reus 2022

Upload voice recordings and annotations/wishes to the local repository.

run with `python uploader/uploader.py`
'''

import sys
import os
import json
from pathlib import Path
import numpy as np
from flask import Flask, request, redirect, jsonify, render_template, send_from_directory, flash, url_for
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = "My Secret key"

SERVE_HOST = '0.0.0.0'
UPLOAD_FOLDER = "/home/jon/Dev/Ahnen/chorusworkshop/uploader/static/uploads"
MAX_UPLOAD_SIZE = 100 * 1000 * 1000 # 100 MB max filesize
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'webm'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Serve Static Files
@app.route("/<path:name>")
def fetch_static(name):
    return send_from_directory(
        "static/", name, as_attachment=False
    )

@app.route('/webaudio-demo')
def wademo():
    return render_template('webaudiorecorder-demo.html', names=["",""], wishes=["",""], message="")

@app.route('/opus-demo')
def opusdemo():
    return render_template('opusrecorder-demo.html', names=["",""], wishes=["",""], message="")

#create our "home" route using the "index.html" page
@app.route('/', methods = ['GET'])
def home():
    #return render_template('index.html', names=["The Voice of Authority","The Voice of Reason"], wishes=["I love you...","What is love?"], message="Test Message..")
    return render_template('index.html', name="", annotations="", wishes="", message="")

# Set a post method to save audio files
@app.route('/', methods = ['POST'])
def upload_voice_file():
    print("upload_voice_file() with form: ", request.form)
    print("         and files: ", request.files)
    if 'audiofile' not in request.files:
        flash("No file part")
        print("Error: No file part")
        return redirect(request.url)

    audiofile = request.files['audiofile']
    print("We found audiofile", audiofile, "With Filename", audiofile.filename, "Is allowed?", allowed_file(audiofile.filename))

    if audiofile.filename == '':
        flash('Unnamed file')
        print("Error: unnamed audio file!")
        return redirect(request.url)

    if audiofile and allowed_file(audiofile.filename):
        print("Audiofile is good! Checking other fields...")
        name = request.form.get('name')
        annotations = request.form.get('annotations')
        wishes = request.form.get('wishes')
        transcript = request.form.get('transcript')
        filename = secure_filename(audiofile.filename)
        audio_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audiofile.save(audio_filepath)

        # Create json metadata / annotations file
        metadata = {
            'filename': filename,
            'name': name,
            'annotations': annotations,
            'wishes': wishes,
            'transcript': transcript
        }
        json_filename = Path(audio_filepath).stem
        json_filename =  f"{json_filename}.json"
        json_filepath = os.path.join(app.config['UPLOAD_FOLDER'], json_filename)
        with open(json_filepath, 'w') as outfile:
            json.dump(metadata, outfile)
        print(f"SAVING AUDIO>>> name:{name}\n  annotations:{wishes}\n   wishes:{wishes}")
        print(f"       SAVING: {filename} // {json_filename}")
        return "Success"

    return "Error"


if __name__ == '__main__':
    app.run(port=3000, debug=True, host=SERVE_HOST, ssl_context='adhoc')
