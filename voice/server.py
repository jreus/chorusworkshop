'''
An (in)audible Chorus
CTM Festival 2022

(c) J Chaim Reus 2022

run with: export FLASK_APP=server && export FLASK_ENV=development && flask run
'''

import sys
import os
from pathlib import Path
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer
import torchaudio
from flask import Flask, request, jsonify, render_template, send_from_directory
from datetime import datetime



app = Flask(__name__)

# Configure and download the pre-trained YourTTS model
save_folder = Path("/home/jon/Drive/KONTINUUM/chorus/voice/static/outputs/")
if not save_folder.exists():
  save_folder.mkdir()

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
voiceprints_folder = Path("vp")
if not voiceprints_folder.exists():
    voiceprints_folder.mkdir()


def get_voices():
    print("Voiceprint Folder is", voiceprints_folder)
    vps = voiceprints_folder.glob('*.wav')
    voices = [v.stem for v in vps]
    print("Get Voices", voices)
    return voices

print("Found voices:", get_voices())


@app.route("/outputs/<path:name>")
def download_file(name):
    print("Sending:", name)
    return send_from_directory(
        "static/outputs/", name, as_attachment=True
    )
#create our "home" route using the "index.html" page
@app.route('/')
def home():
    return render_template('index.html', voices=get_voices(), languages=available_languages)

#Set a post method to yield predictions on page
@app.route('/', methods = ['POST'])
def predict():
    voice = request.form.get('voice')
    phonetics = request.form.get('phonetics')
    text = request.form.get('text')

    # TODO: Data validation
    # VOICE EXISTS
    # LANGUAGE EXISTS
    # TEXT IS NOT TOO CRAZY (?)

    print(f"Got voice:{voice}  ph:{phonetics}  txt:{text}")

    # Does voiceprint exist?
    speaker_wav = voiceprints_folder.joinpath(f"{voice}.wav")
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
        save_path = save_folder.joinpath(save_filename)

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

        audiofiles = [save_path]
        audiofiles = [os.path.join('/outputs/', sp.name) for sp in audiofiles]
        print("Reply with Audiofiles:", audiofiles)

        return render_template('vp.html', message="Success!", audiofiles=audiofiles, voice=voice, text=text, phonetics=phonetics, voices=get_voices(), languages=available_languages)
    else:
        # If no, return an error...
        print(f"ERROR! No voiceprint {voice} found!")
        return render_template('index.html', message=f"Sorry! No voiceprint {voice} exists!")

if __name__ == '__main__':
    app.run(port=5000, debug=True)
