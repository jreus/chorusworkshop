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
import typing

RECORDINGS_FOLDER = Path("static/uploads/")
if not RECORDINGS_FOLDER.exists():
    RECORDINGS_FOLDER.mkdir()

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

def get_voicerecordings(items_only:bool=False, sort_by:str='date') -> typing.Union[dict, list]:
    '''
    Get a dictionary of recording_name->metadata and sort by date

    items_only  if True, returns a list of metadata dicts instead of a dict with keys
    '''
    print("Recordings Folder is", RECORDINGS_FOLDER)
    audiofiles = RECORDINGS_FOLDER.glob('*.wav') # TODO: also glob mp3 and webm?
    recordingfiles = [r for r in audiofiles]
    audiodata = dict()
    for af in recordingfiles: # We should have a metadata file for each voice.. if not fill metadata with nothing...
        mdpath = RECORDINGS_FOLDER.joinpath(f"{af.stem}.json")
        # Default
        metadata = { 'filename': af.name, 'name': af.stem, 'annotations': '', 'wishes': '', 'transcript': '' }
        if mdpath.exists():
            # All good!
            with open(mdpath) as json_file:
                # Replace the default...
                metadata = json.load(json_file)
        metadata['filename'] = af.name
        metadata['filepath'] = os.path.join(RECORDINGS_FOLDER, af.name)
        audiodata[metadata['name']] = metadata

    def filesortfunc(audiodataval:dict):
        return audiodataval['name']

    if items_only:
        res = sorted(list(audiodata.values()), key=filesortfunc) # TODO: sort by date
    else:
        res = dict(sorted(audiodata.items())) # TODO: sort by date
    #print("Got Recordings: ", audiodata.keys())
    print("Got Recordings: ", res)
    return res

print("Found recordings:", get_voicerecordings().keys())


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
    #return render_template('record.html', names=["",""], wishes=["",""], message="")
    return render_template('record.html', names=["",""], annotations=["",""], message="")

@app.route('/record', methods = ['GET'])
def record():
    return render_template('record.html', names=["",""], annotations=["",""], message="")

@app.route('/upload', methods = ['GET'])
def upload():
    return render_template('upload.html', names=["",""], wishes=["",""], message="")

@app.route('/listen', methods = ['GET'])
def listen():
    audiodata = get_voicerecordings(items_only=True)
    print(f"Sending audiofiledata: {audiodata}")
    return render_template('listen.html', audiofiledata=audiodata)



# Set a post method to save audio files
@app.route('/record', methods = ['POST'])
def upload_recording():
    print("upload_recording() with", request.files)

    if 'file' not in request.files:
        flash("No file part")
        return redirect(request.url)

    audiofile = request.files['file']

    print("Received from FORM: audiofile", audiofile, "With Filename", audiofile.filename)

    if audiofile.filename == '':
        flash('Unnamed file')
        return redirect(request.url)

    if audiofile and allowed_file(audiofile.filename):
        formid = request.form.get('formid')
        recordingname = request.form.get('name')
        annotation = request.form.get('annotation')
        filename = secure_filename(audiofile.filename)
        audio_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        afidx=0
        print(f"Got formid:{formid} -- name:{recordingname} -- annotation:{annotation} -- filename:{filename}")
        # TODO: check if file already exists
        while os.path.exists(audio_filepath):
            print(f"File {filename} already exists... trying {filename}{afidx}")
            audio_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}{afidx}")
            afidx += 1

        audiofile.save(audio_filepath)

        # Create json file
        metadata = {
            'filename': filename,
            'name': recordingname,
            'annotations': annotation,
        }
        json_filename = Path(audio_filepath).stem
        json_filename = f"{json_filename}.json"
        json_filepath = os.path.join(app.config['UPLOAD_FOLDER'], json_filename)
        with open(json_filepath, 'w') as outfile:
            json.dump(metadata, outfile)

        print(f"SAVING AUDIO>>> Got form {formid},  recording name:{recordingname}  annotation:{annotation}")
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
