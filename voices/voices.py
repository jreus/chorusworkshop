'''
Voices Record & Listen
General Interface

(c) Jonathan Reus 2023

Record and upload annotated voice recordings.

'''

import sys
import os
import json
from pathlib import Path
import numpy as np
from flask import Flask, request, redirect, jsonify, render_template, send_from_directory, flash, url_for
from werkzeug.utils import secure_filename
from datetime import datetime

VOICEPRINTS_FOLDER = Path("static/uploads/")
if not VOICEPRINTS_FOLDER.exists():
    VOICEPRINTS_FOLDER.mkdir()


app = Flask(__name__)

SERVE_HOST = '0.0.0.0'
UPLOAD_FOLDER = "static/uploads" # Relative to this file
#UPLOAD_FOLDER = "static/uploads" # alternatively...
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'webm'}
MAX_UPLOAD_SIZE = 100 * 1000 * 1000 # 100 MB max filesize
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_voicedata():
    '''
    Get a dictionary of voice_name->voice_metadata - sort alphabetically
    '''
    print("Voiceprint Folder is", VOICEPRINTS_FOLDER)
    vps = VOICEPRINTS_FOLDER.glob('*.wav')
    voicefiles = [v for v in vps]
    voicedata = dict()
    for vf in voicefiles: # We should have a metadata file for each voice.. if not fill metadata with nothing...
        mdpath = VOICEPRINTS_FOLDER.joinpath(f"{vf.stem}.json")
        # Default
        metadata = { 'filename': vf.name, 'name': vf.stem, 'annotations': '', 'wishes': '', 'transcript': '' }
        if mdpath.exists():
            # All good!
            with open(mdpath) as json_file:
                # Replace the default...
                metadata = json.load(json_file)
        metadata['filepath'] = vf.name
        voicedata[metadata['name']] = metadata

    voicedata = dict(sorted(voicedata.items()))
    print("Got Voices", voicedata.keys())
    #print("Data:", voicedata)
    return voicedata

print("Found voices:", get_voicedata().keys())


# Serve Static Files
@app.route("/<path:name>")
def fetch_static(name):
    return send_from_directory(
        "static/", name, as_attachment=False
    )


#create our "home" route using the "index.html" page
@app.route('/', methods = ['GET'])
def home():
    #return render_template('index.html', names=["The Voice of Authority","The Voice of Reason"], wishes=["I love you...","What is love?"], message="Test Message..")
    return render_template('index.html', names=["",""], wishes=["",""], message="")


@app.route('/record', methods = ['GET'])
def record():
    return render_template('record.html', names=["",""], wishes=["",""], message="")

@app.route('/upload', methods = ['GET'])
def upload():
    return render_template('upload.html', names=["",""], wishes=["",""], message="")

@app.route('/listen', methods = ['GET'])
def listen():
    vd = get_voicedata()
    if len(vd.keys()) > 0:
        selected = list(vd.keys())[0]
    else:
        selected = ''
    return render_template('listen.html', selectedvoice=selected, voicedata=vd)


# Set a post method to save audio files
@app.route('/saveaudio', methods = ['POST'])
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


# Set a post method to save audio files
@app.route('/uploadvoice', methods = ['POST'])
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
    app.run(host='0.0.0.0')
