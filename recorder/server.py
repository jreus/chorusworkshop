'''
An (in)audible Chorus :: VoicePrinting
CTM Festival 2022

(c) J Chaim Reus 2022

Record and upload voice for use as voiceprints in synthesis.

run with: export FLASK_APP=server && export FLASK_ENV=development && flask run
'''

import sys
import os
from pathlib import Path
import numpy as np
from flask import Flask, request, redirect, jsonify, render_template, send_from_directory, flash, url_for
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "/home/jon/Drive/KONTINUUM/chorusworkshop/recorder/static/uploads"
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'webm'}
MAX_UPLOAD_SIZE = 100 * 1000 * 1000 # 100 MB max filesize
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
    return render_template('index.html', names=["The Voice of Authority","The Voice of Reason"], wishes=["I love you...","What is love?"], message="Test Message..")


# Set a post method to save audio files
@app.route('/', methods = ['POST'])
def save_audio():
    print("save_audio() with", request.files)

    if 'file' not in request.files:
        flash("No file part")
        return redirect(request.url)

    audiofile = request.files['file']

    print("We found audiofile", audiofile, "With Filename", audiofile.filename, "Is allowed?", allowed_file(audiofile.filename))

    if audiofile.filename == '':
        flash('Unnamed file')
        return redirect(request.url)

    if audiofile and allowed_file(audiofile.filename):
        print("Audiofile is allowed")
        names = [request.form.get('name1'), request.form.get('name2')]
        wishes = [request.form.get('wishes1'), request.form.get('wishes2')]
        filename = secure_filename(audiofile.filename)
        audiofile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(f"SAVING AUDIO>>> Got names:{names}  wishes:{wishes}")
        return "Success"

    return "Error"


if __name__ == '__main__':
    app.run(port=3000, debug=True, ssl_context='adhoc')
