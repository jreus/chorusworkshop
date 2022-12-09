'''
In Search of Good Ancestors / Ahnen in Arbeit
Voice Synthesis Server

(c) J Chaim Reus 2022

run from chorusworkshop root folder with: python voicesynthesizer/voicer.py
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

RENDER_FOLDER = Path("/home/jon/Dev/Ahnen/chorusworkshop/voicesynthesizer/static/renders/")
if not RENDER_FOLDER.exists():
  RENDER_FOLDER.mkdir()

#VOICEPRINTS_FOLDER = Path("/home/jon/Dev/Ahnen/chorusworkshop/voicerecorder/static/uploads/")
VOICEPRINTS_FOLDER = Path("/home/jon/Dev/Ahnen/chorusworkshop/uploader/static/uploads/")
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
#  print("SPEAKERS",synth.tts_model.speaker_manager.ids) # coqui < 0.8
  print("SPEAKERS",synth.tts_model.speaker_manager.speaker_names)

if synth.tts_model.language_manager is not None:
#  print("LANGUAGES", synth.tts_model.language_manager.ids) # coqui < 0.8
  print("LANGUAGES", synth.tts_model.language_manager.language_names)

voicehistory = dict() # dict of voices to history
filehistory = dict() # dict of filenames of generated files to their metadata
available_languages = synth.tts_model.language_manager.language_names

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

@app.route("/renders/<path:name>")
def fetch_audiofile(name):
    print("Sending:", name)
    return send_from_directory(
        "static/renders/", name, as_attachment=True
    )
#create our "home" route using the "index.html" page
@app.route('/')
def home():
    vd = get_voicedata()
    return render_template('index.html', selectedvoice=list(vd.keys())[0], voicedata=vd, speed=50, variation=50, languages=available_languages)


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

    voice = request.form.get('selectedvoice')
    phonetics = request.form.get('phonetics')
    text = request.form.get('text')
    fileslist = request.form.get('fileslist')
    speed = int(request.form.get('speedval'))
    variation = int(request.form.get('variationval'))
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

    print(f"PREDICT>>> Got voice:{voice}  ph:{phonetics}  txt:{text} spd:{speed} var:{variation} files:{fileslist}")

    # Does voiceprint exist?
    allvoicedata = get_voicedata()
    voicedata = allvoicedata[voice]
    speaker_wav = VOICEPRINTS_FOLDER.joinpath(voicedata['filename'])
    if speaker_wav.exists():
        # If yes, do synthesis...
        if voice in voicehistory:
            vhistory = voicehistory[voice]
        else:
            vhistory = {'num': 0, 'outputs': list()}
            voicehistory[voice] = vhistory

        # Unique file name for synthesized output...
        timestamp = datetime.now().strftime("%H_%M_%S")
        save_filename = f"{timestamp}_{voice}_{vhistory['num']:03d}.wav"
        save_path = RENDER_FOLDER.joinpath(save_filename)

        language_name = phonetics
        speaker_name = None
        style_wav = None
        reference_wav = None
        reference_speaker_name = None
        model = synth.tts_model

        tmp_model_vals = [ model.length_scale, model.inference_noise_scale_dp ]
        #model.inference_noise_scale
        scaled_speed = (((100-speed) / 100.0)**4.1 + 0.001) * 20.0
        scaled_var = (variation / 100.0)**1.5 * 1.7
        print(f"   >>> speed: {scaled_speed}  variation: {scaled_var}")
        model.length_scale = scaled_speed
        model.inference_noise_scale_dp = scaled_var
        wav = synth.tts(
            text,
            speaker_name,
            language_name,
            speaker_wav,
            style_wav,
            reference_wav,
            reference_speaker_name,
        )
        model.length_scale = tmp_model_vals[0]
        model.inference_noise_scale_dp = tmp_model_vals[1]

        # save the results
        print(" > Saving output to {}".format(save_path))
        synth.save_wav(wav, save_path)
        del wav

        # Add to history...
        vhistory['num'] += 1
        vhistory['outputs'].append(vhistory)

        filepath = os.path.join('/renders/', save_path.name)
        filemetadata = {'save_path': save_path, 'file_path': filepath, 'text': text, 'voice': voice, 'phonetics': phonetics}
        filehistory[filepath] = filemetadata
        audiofiles.append(filepath)
        print("Reply with Audiofiles:", audiofiles)

        audiofiledata = list()
        for fp in audiofiles:
            # For each audiofile, append audiofile meta data from history...
            audiofiledata.append(filehistory[fp])

        return render_template('index.html', message="Synthesis Success!", audiofiles=audiofiles, audiofiledata=audiofiledata, selectedvoice=voice, text=text, phonetics=phonetics, voicedata=allvoicedata, speed=speed, variation=variation, languages=available_languages)
    else:
        # If no, return an error...
        print(f"ERROR! No voiceprint {voice} found!")
        return render_template('index.html', message=f"Sorry! No voiceprint {voice} exists!")

if __name__ == '__main__':
    app.run(port=SERVE_PORT, host=SERVE_HOST, debug=SERVE_DEBUG)
