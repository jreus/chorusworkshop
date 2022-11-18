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
# gen = pipeline("text-generation")

# Other models...


# distilgp2 - https://huggingface.co/distilgpt2
# Super lightweight version of GPT2
# generator = pipeline('text-generation', model='distilgpt2')
# set_seed(42)
# generator("Hello, I’m a language model", max_length=20, num_return_sequences=5)

# opt-2.7b - https://huggingface.co/facebook/opt-2.7b
# Crazy facebook 2.7b parameter model
# generator = pipeline('text-generation', model="facebook/opt-2.7b")
# generator("Hello, I'm am conscious and")

# gpt-neo 125M https://huggingface.co/EleutherAI/gpt-neo-125M
# A lightweight model based on the GPT-Neo architecture
# generator = pipeline('text-generation', model='EleutherAI/gpt-neo-125M')
# generator("EleutherAI has", do_sample=True, min_length=50)

# gpt-neo-1.3B https://huggingface.co/EleutherAI/gpt-neo-1.3B
# generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')
# generator("EleutherAI has", do_sample=True, min_length=50)

# gpt-neo 2.7B Model https://huggingface.co/EleutherAI/gpt-neo-2.7B
gen = pipeline('text-generation', model='EleutherAI/gpt-neo-2.7B')
# generator("EleutherAI has", do_sample=True, min_length=50)

# gpt-j-6B - https://huggingface.co/EleutherAI/gpt-j-6B
# Insane 6B parameter gpt-j model
# from transformers import AutoTokenizer, AutoModelForCausalLM
# tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B")
# model = AutoModelForCausalLM.from_pretrained("EleutherAI/gpt-j-6B")

print("USING CAUSAL LANGUAGE MODEL: ", gen.model.config._name_or_path)

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
    return render_template('index.html', temperatures=temperatures, temperature=1.0, max_length=200, num_predictions=1)

#Set a post method to yield predictions on page
@app.route('/', methods = ['POST'])
def predict():
    prompt = request.form.get('prompt')
    temperature = float(request.form.get('temperature'))
    max_length = float(request.form.get('max_length'))
    num_predictions = int(request.form.get('num_predictions'))

    print(f"PREDICT>>> Got prompt:{prompt}  temp:{temperature}  num_predictions:{num_predictions} max_length:{max_length}")

    # predict the next 50 words, return 3 predictions
    # default uses top_k/top_p sampling
    prompt_length = gen.tokenizer(prompt)
    adjusted_max_length = max_length + len(prompt_length['input_ids'])
    predictions = gen(prompt, max_length=adjusted_max_length, num_return_sequences=num_predictions, top_k=10, top_p=1.0, temperature=temperature, return_full_text=False)
    predictions = [p['generated_text'].splitlines() for p in predictions]
    for pred in predictions:
        print('\n---------------------\n', pred)

    return render_template('index.html', predictions=predictions, temperatures=temperatures, temperature=temperature, max_length=max_length, selected_temperature=temperature, num_predictions=num_predictions, last_prompt=prompt,  message=f"")

if __name__ == '__main__':
    app.run(port=4000, host='0.0.0.0', debug=True)
