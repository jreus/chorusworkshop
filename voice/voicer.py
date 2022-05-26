'''
An (in)audible Chorus :: Voicing
CTM Festival 2022

(c) J Chaim Reus 2022

run with: export FLASK_APP=server && export FLASK_ENV=development && flask run
'''

import sys
import os
import json
from pathlib import Path
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer
import torchaudio
from flask import Flask, request, jsonify, render_template, send_from_directory
from datetime import datetime


SERVE_PORT=5000
SERVE_HOST='0.0.0.0'
SERVE_DEBUG=True

RENDER_FOLDER = Path("/home/jon/Drive/KONTINUUM/chorusworkshop/voice/static/outputs/")
if not RENDER_FOLDER.exists():
  RENDER_FOLDER.mkdir()

VOICEPRINTS_FOLDER = Path("/home/jon/Drive/KONTINUUM/chorusworkshop/recorder/static/uploads/")
if not VOICEPRINTS_FOLDER.exists():
    VOICEPRINTS_FOLDER.mkdir()


app = Flask(__name__)

# Configure and download the pre-trained YourTTS model

# Path to TTS models.json use default...
#path = Path("/usr/local/lib/python3.7/dist-packages/TTS/.models.json")
manager = ModelManager()

model_name = "tts_models/multilingual/multi-dataset/your_tts"
#model_name = "tts_models/en/vctk/vits"
use_cuda = False
model_path = None
config_path = None
speakers_file_path = None
language_ids_file_path = None
vocoder_path = None
vocoder_config_path = None
encoder_path = None
encoder_config_path = None

model_path, config_path, model_item = manager.download_model(model_name)
vocoder_name = model_item["default_vocoder"]
if vocoder_name is not None:
  vocoder_path, vocoder_config_path, _ = manager.download_model(vocoder_name)

synth = Synthesizer(
    model_path,
    config_path,
    speakers_file_path,
    language_ids_file_path,
    vocoder_path,
    vocoder_config_path,
    encoder_path,
    encoder_config_path,
    use_cuda,
)

# Show available speakers / languages of current model.
if synth.tts_model.speaker_manager is not None:
  print("SPEAKERS",synth.tts_model.speaker_manager.ids)

if synth.tts_model.language_manager is not None:
  print("LANGUAGES", synth.tts_model.language_manager.ids)

history = dict()
available_languages = synth.tts_model.language_manager.ids.keys()

def get_voicedata():
    '''
    Get a dictionary of voice_name->voice_metadata - sort alphabetically
    '''
    print("Voiceprint Folder is", VOICEPRINTS_FOLDER)
    vps = VOICEPRINTS_FOLDER.glob('*.wav')
    voices = [v.stem for v in vps]
    voicedata = dict()
    for voice in voices: # We should have a metadata file for each voice.. if not fill metadata with nothing...
        mdpath = VOICEPRINTS_FOLDER.joinpath(f"{voice}.json")
        metadata = { 'filename': None, 'vpname': voice, 'wishes': '' }
        if mdpath.exists():
            # All good!
            with open(mdpath) as json_file:
                metadata = json.load(json_file)
        voicedata[voice] = metadata


    voicedata = dict(sorted(voicedata.items()))
    print("Got Voices", voicedata.keys())
    print("Data:", voicedata)

    return voicedata

print("Found voices:", get_voicedata().keys())


# Serve Static Files
@app.route("/<path:name>")
def fetch_static(name):
    return send_from_directory(
        "static/", name, as_attachment=False
    )

@app.route("/outputs/<path:name>")
def fetch_audiofile(name):
    print("Sending:", name)
    return send_from_directory(
        "static/outputs/", name, as_attachment=True
    )
#create our "home" route using the "index.html" page
@app.route('/')
def home():
    return render_template('index.html', voicedata=get_voicedata(), languages=available_languages)


# Request for updated app data and metadata
@app.route('/getdata', methods = ['POST'])
def getdata():
    command = request.form.get('command')
    print(f"Got command {command}")

    if command == 'voiceData':
        return get_voicedata()

    return f"Unknown command {command}"


#Set a post method to yield predictions on page
@app.route('/', methods = ['POST'])
def predict():
    voice = request.form.get('voice')
    phonetics = request.form.get('phonetics')
    text = request.form.get('text')
    fileslist = request.form.get('fileslist')
    if fileslist != "":
        if fileslist[0] == ';':
            fileslist=fileslist[1:]
        audiofiles = fileslist.split(';')
    else:
        audiofiles = list()

    # TODO: Data validation
    # VOICE EXISTS
    # LANGUAGE EXISTS
    # TEXT IS NOT TOO CRAZY (?)

    print(f"PREDICT>>> Got voice:{voice}  ph:{phonetics}  txt:{text}  files:{fileslist}")

    # Does voiceprint exist?
    speaker_wav = VOICEPRINTS_FOLDER.joinpath(f"{voice}.wav")
    if speaker_wav.exists():
        # If yes, do synthesis...

        if voice in history:
            vhistory = history[voice]
        else:
            vhistory = {'num': 0, 'outputs': list()}
            history[voice] = vhistory

        # Unique file name for synthesized output...
        timestamp = datetime.now().strftime("%H_%M_%S")
        save_filename = f"{timestamp}_{voice}_{vhistory['num']:03d}.wav"
        save_path = RENDER_FOLDER.joinpath(save_filename)

        language_name = phonetics
        speaker_name = None
        style_wav = None
        reference_wav = None
        reference_speaker_name = None
        wav = synth.tts(
            text,
            speaker_name,
            language_name,
            speaker_wav,
            style_wav,
            reference_wav,
            reference_speaker_name,
        )

        # save the results
        print(" > Saving output to {}".format(save_path))
        synth.save_wav(wav, save_path)
        del wav

        # Add to history...
        vhistory['num'] += 1
        vhistory['outputs'].append(save_path)

        audiofiles.append(os.path.join('/outputs/', save_path.name))
        print("Reply with Audiofiles:", audiofiles)

        return render_template('index.html', message="Synthesis Success!", audiofiles=audiofiles, voice=voice, text=text, phonetics=phonetics, voicedata=get_voicedata(), languages=available_languages)
    else:
        # If no, return an error...
        print(f"ERROR! No voiceprint {voice} found!")
        return render_template('index.html', message=f"Sorry! No voiceprint {voice} exists!")

if __name__ == '__main__':
    app.run(port=SERVE_PORT, host=SERVE_HOST, debug=SERVE_DEBUG)
