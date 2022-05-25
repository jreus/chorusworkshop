'''
An (in)audible Chorus :: Writing
CTM Festival 2022

(c) J Chaim Reus 2022

run with: export FLASK_APP=server && export FLASK_ENV=development && flask run
'''

import sys
import os
from pathlib import Path
from transformers import pipeline
import torch
import numpy as np
from flask import Flask, request, jsonify, render_template, send_from_directory
from datetime import datetime

app = Flask(__name__)

# Create a generic "text-generation" pipeline, this will download the default pretrained causal language model for generation
# which is OpenAI's GPT-2
gen = pipeline("text-generation")

temperatures = np.around(np.logspace(0.01, 1.0, 10, base=10) - 0.9, 1)[::-1]

# Serve Static Files
@app.route("/<path:name>")
def fetch_static(name):
    return send_from_directory(
        "static/", name, as_attachment=False
    )

#create our "home" route using the "index.html" page
@app.route('/')
def home():
    return render_template('index.html', temperatures=temperatures, temperature=1.0)

#Set a post method to yield predictions on page
@app.route('/', methods = ['POST'])
def predict():
    prompt = request.form.get('prompt')
    temperature = float(request.form.get('temperature'))

    print(f"PREDICT>>> Got prompt:{prompt}  temp:{temperature}")

    # predict the next 50 words, return 3 predictions
    # default uses top_k/top_p sampling
    predictions = gen(prompt, max_length=200, num_return_sequences=3, top_k=10, top_p=1.0, temperature=temperature, return_full_text=False)
    predictions = [p['generated_text'].splitlines() for p in predictions]
    for pred in predictions:
        print('\n---------------------\n', pred)

    return render_template('index.html', predictions=predictions, temperatures=temperatures, temperature=temperature, selected_temperature=temperature, last_prompt=prompt,  message=f"")

if __name__ == '__main__':
    app.run(port=4000, debug=True)
