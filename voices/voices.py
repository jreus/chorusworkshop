'''
An (in)audible Chorus :: VoicePrinting
CTM Festival 2022

(c) J Chaim Reus 2022

Record and upload voice for use as voiceprints in synthesis.

run with: export FLASK_APP=server && export FLASK_ENV=development && flask run
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

SERVE_HOST = '0.0.0.0'
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
    #return render_template('index.html', names=["The Voice of Authority","The Voice of Reason"], wishes=["I love you...","What is love?"], message="Test Message..")
    return render_template('index.html', names=["",""], wishes=["",""], message="")


@app.route('/record', methods = ['GET'])
def record():
    return "RECORDING HERE!"

@app.route('/listen', methods = ['GET'])
def listen():
    return "LISTEN HERE!"


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
        formid = request.form.get('formid')
        vpname = request.form.get('name')
        wishes = request.form.get('wishes')
        transcript = request.form.get('transcript')
        speaker = request.form.get('speaker')
        filename = secure_filename(audiofile.filename)
        audio_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audiofile.save(audio_filepath)

        # Create json file
        metadata = {
            'filename': filename,
            'vpname': vpname,
            'wishes': wishes,
            'transcript': transcript,
            'speaker': speaker
        }
        json_filename = Path(audio_filepath).stem
        json_filename =  f"{json_filename}.json"
        json_filepath = os.path.join(app.config['UPLOAD_FOLDER'], json_filename)
        with open(json_filepath, 'w') as outfile:
            json.dump(metadata, outfile)

        print(f"SAVING AUDIO>>> Got form {formid},  voiceprint name:{vpname}  wishes:{wishes}")
        print(f"       SAVING: {filename} // {json_filename}")
        return "Success"

    return "Error"


if __name__ == '__main__':
    app.run(host='0.0.0.0')
