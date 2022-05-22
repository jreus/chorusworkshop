// set up basic variables for app

const record = document.querySelector('.record');
const stop = document.querySelector('.stop');
const soundClips = document.querySelector('.sound-clips');
const canvases = [document.querySelector('.visualizerL'), document.querySelector('.visualizerR')];
const mainSection = document.querySelector('.main-controls');

// disable stop button while not recording
stop.disabled = true;

// visualiser setup - create web audio api context and canvas
let audioCtx;
const canvasContexts = [canvases[0].getContext("2d"), canvases[1].getContext("2d")];

let vals = {}

//main block for doing the audio recording
if (navigator.mediaDevices.getUserMedia) {
  console.log('getUserMedia supported.');

  const constraints = { audio: {
      optional: [{ echoCancellation: false }]
  } };
  let chunks = [];

  let onSuccess = function(stream) {
    vals.stream = stream;
    console.log("Got Stream", stream);
    const audioChannels = stream.getTracks();
    console.log("With tracks", audioChannels);
    audioChannels.forEach((track) => { console.log(track) });

    const mediaRecorder = new MediaRecorder(stream);
    console.log("A MediaRecorder given the input stream", mediaRecorder);
    vals.recorder = mediaRecorder;

    if(!audioCtx) {
      audioCtx = new AudioContext();
    }

    visualize(stream);

    record.onclick = function() {
      mediaRecorder.start();
      console.log(mediaRecorder.state);
      console.log("recorder started");
      record.style.background = "red";

      stop.disabled = false;
      record.disabled = true;
    }

    stop.onclick = function() {
      mediaRecorder.stop();
      console.log(mediaRecorder.state);
      console.log("recorder stopped");
      record.style.background = "";
      record.style.color = "";
      // mediaRecorder.requestData();

      stop.disabled = true;
      record.disabled = false;
    }

    mediaRecorder.onstop = function(e) {
      console.log("data available after MediaRecorder.stop() called.");

      const clipName = prompt('Enter a name for your sound clip?','My unnamed clip');

      const clipContainer = document.createElement('article');
      const clipLabel = document.createElement('p');
      const audio = document.createElement('audio');
      const deleteButton = document.createElement('button');

      clipContainer.classList.add('clip');
      audio.setAttribute('controls', '');
      deleteButton.textContent = 'Delete';
      deleteButton.className = 'delete';

      if(clipName === null) {
        clipLabel.textContent = 'My unnamed clip';
      } else {
        clipLabel.textContent = clipName;
      }

      clipContainer.appendChild(audio);
      clipContainer.appendChild(clipLabel);
      clipContainer.appendChild(deleteButton);
      soundClips.appendChild(clipContainer);

      audio.controls = true;
      const blob = new Blob(chunks, { 'type' : 'audio/ogg; codecs=opus' });
      chunks = [];
      const audioURL = window.URL.createObjectURL(blob);
      audio.src = audioURL;
      console.log("recorder stopped");

      deleteButton.onclick = function(e) {
        let evtTgt = e.target;
        evtTgt.parentNode.parentNode.removeChild(evtTgt.parentNode);
      }

      clipLabel.onclick = function() {
        const existingName = clipLabel.textContent;
        const newClipName = prompt('Enter a new name for your sound clip?');
        if(newClipName === null) {
          clipLabel.textContent = existingName;
        } else {
          clipLabel.textContent = newClipName;
        }
      }
    }

    mediaRecorder.ondataavailable = function(e) {
      console.log("Some data", e);
      chunks.push(e.data);
    }
  }

  let onError = function(err) {
    console.log('The following error occured: ' + err);
  }

  navigator.mediaDevices.getUserMedia(constraints).then(onSuccess, onError);

} else {
   console.log('getUserMedia not supported on your browser!');
}

function visualize(stream) {
  if(!audioCtx) {
    audioCtx = new AudioContext();
  }

  const streamSource = audioCtx.createMediaStreamSource(stream);
  const channelSplitter = audioCtx.createChannelSplitter(2);

  const analyserLeft = audioCtx.createAnalyser();
  const analyserRight = audioCtx.createAnalyser();
  analyserLeft.fftSize = 2048;
  analyserRight.fftSize = 2048;
  const bufferLength = analyserLeft.frequencyBinCount;
  const dataArrays = [new Uint8Array(bufferLength), new Uint8Array(bufferLength)];

  vals.source = streamSource;
  console.log("Input Audio as a MediaStreamSource", streamSource);
  streamSource.connect(channelSplitter);
  const audioProcessorLeft = audioCtx.createScriptProcessor(1024, 1, 1);
  const audioProcessorRight = audioCtx.createScriptProcessor(1024, 1, 1);
  channelSplitter.connect(audioProcessorLeft, 0);
  channelSplitter.connect(audioProcessorRight, 1);

  channelSplitter.connect(analyserLeft, 0);
  channelSplitter.connect(analyserRight, 1);
  //streamSource.connect(analyser);
  //analyser.connect(audioCtx.destination);

  draw()

  function draw() {

    requestAnimationFrame(draw);

    analyserLeft.getByteTimeDomainData(dataArrays[0]);
    analyserRight.getByteTimeDomainData(dataArrays[1]);

    for(let idx=0; idx<canvases.length; idx++) {
      let canvasCtx = canvasContexts[idx];
      let canvas = canvases[idx];
      let dataArray = dataArrays[idx];

      const WIDTH = canvas.width
      const HEIGHT = canvas.height;

      canvasCtx.fillStyle = 'rgb(200, 200, 200)';
      canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);
      canvasCtx.lineWidth = 2;
      canvasCtx.strokeStyle = 'rgb(0, 0, 0)';
      canvasCtx.beginPath();

      let sliceWidth = WIDTH * 1.0 / bufferLength;
      let x = 0;

      for(let i = 0; i < bufferLength; i++) {

        let v = dataArray[i] / 128.0;
        let y = v * HEIGHT/2;

        if(i === 0) {
          canvasCtx.moveTo(x, y);
        } else {
          canvasCtx.lineTo(x, y);
        }

        x += sliceWidth;
      }

      canvasCtx.lineTo(canvas.width, canvas.height/2);
      canvasCtx.stroke();
    }
  }
}

window.onresize = function() {
  for(let i=0; i<canvases.length;i++) {
    canvases[i].width = mainSection.offsetWidth;
    canvases[i].width = mainSection.offsetWidth;
  }
}

window.onresize();
