function screenLogger(text, data) {
  let p = document.createElement('p');
  let t = document.createElement('span');
  let d = document.createElement('span');
  t.innerHTML = text;
  d.innerHTML = (data || '');
  t.classList.add('log-text');
  d.classList.add('log-data');

  p.appendChild(t);
  p.appendChild(d);
  log.appendChild(p);
}

const forms = [document.querySelector('#voiceform')];
const names = [document.querySelector('#name')];
const annotations = [document.querySelector('#annotation')];
const recordButtons = [document.querySelector('#recordButton')];
const stopButtons = [document.querySelector('#stopButton')];
const submitButtons = [document.querySelector('#submitButton')];
const soundClipsContainers = [document.querySelector('#soundclips')];
const canvases = [document.querySelector('#visualizer')];
const mainSection = document.querySelector('#controls');

// disable stop button while not recording
for(let i = 0; i < stopButtons.length; i++) {
  stopButtons[i].disabled = true;
}

// visualiser setup - create web audio api context and canvas
const canvasContexts = [canvases[0].getContext("2d")];
let app = {}

//main block for doing the audio recording
if (navigator.mediaDevices.getUserMedia) {
  console.log('getUserMedia supported.');

  const constraints = { audio: {
      optional: [{ echoCancellation: false }]
  } };
  let chunks = [];

  let onSuccess = function(stream) {
    app.stream = stream;
    console.log("Got Input Audio Stream", stream);

    if(!app.audioCtx) {
      app.audioCtx = new AudioContext();
    }

    app.streamSource = app.audioCtx.createMediaStreamSource(stream);
    app.channelSplitter = app.audioCtx.createChannelSplitter(2);
    app.signalLeft = new GainNode(app.audioCtx, {gain: 1.0, channelCount: 1});
    app.signalRight = new GainNode(app.audioCtx, {gain: 1.0, channelCount: 1});

    app.streamSource.connect(app.channelSplitter);
    app.channelSplitter.connect(app.signalLeft, 0);
    app.channelSplitter.connect(app.signalRight, 1);

    visualize(stream);

    // Set up audio Recorders
    app.recorders = [
      new Recorder({
        monitorGain: 0.0,
        recordingGain: 1.0,
        numberOfChannels: 1,
        wavBitDepth: 16,
        encoderPath: "/js/opusrecorder/encoderWorker.min.js",
        sourceNode: app.signalLeft
      }),
      // Just use the left channel to record
      // new Recorder({
      //   monitorGain: 0.0,
      //   recordingGain: 1.0,
      //   numberOfChannels: 1,
      //   wavBitDepth: 16,
      //   encoderPath: "/js/opusrecorder/encoderWorker.min.js",
      //   sourceNode: app.signalRight
      // })
    ];

    console.log("Set up recorders", app.recorders);

    // For each recorder, set up record controls & callbacks
    for(let i=0; i < app.recorders.length; i++) {
      let recorder = app.recorders[i];
      let nameInput = names[i];
      let annotationInput = annotations[i];

      // Set up recorder controls buttons...
      // TODO: Maybe create these buttons dynamically?
      let recordButton = recordButtons[i];
      let stopButton = stopButtons[i];
      let soundClips = soundClipsContainers[i];
      let form = forms[i];

      form.addEventListener('submit', (e)=>{
        // On form submission, prevent default
        e.preventDefault();

        console.log("SUBMITTING!...")

        // Fetch the audio object (if a recording has been made)
        let clipElement = soundClips.querySelector('.clip');
        let audioElement = clipElement.querySelector('audio');

        if(audioElement) {
          // Construct a FormData object
          let formData = new FormData(form);
          let formActionTarget = form.action;
          let formAction = "POST";
          let fileName = audioElement.clipName;
          console.log("Append audio data audioBlob and clipName from", audioElement);

          // Append the file data...
          formData.append('file', audioElement.audioBlob, fileName);

          // Submit the form via xhr
          let request = new XMLHttpRequest();

          // More detailed information about the xhr process
          // request.addEventListener('readystatechange', ()=>{ // Call a function when the state changes.
          //     console.log("Ready State Change", request);
          //     if (request.readyState === XMLHttpRequest.DONE && request.status === 200) {
          //         // Request finished. Do processing here.
          //         console.log("Request sent successfully, received response?", request)
          //     }
          // });

          request.addEventListener('load', ()=>{
            let response = request.response;
            console.log("XHR response", request.response);
            if(response == 'Success') {
              // Delete uploaded clip...
              soundClips.removeChild(clipElement);
              screenLogger("Uploaded ", fileName);

            } else {
              // Print error...
              screenLogger("Error uploading recording '"+fileName+"': ", response);
            }
          });

          request.open(formAction, formActionTarget);
          request.send(formData);


        } else {
          // Throw an error or something? Cannot do anything...
          screenLogger("You need to make a recording before you can save it to the list of voiceprints!")
          console.log("No audio recordings", audioRecordings);
          return;
        }

      });

      recordButton.addEventListener('click', ()=>{
        console.log("recorder "+i+" started");
        console.log("This is", this);

        recorder.start().catch(function(e){
          console.log('Error encountered:', e.message);
          screenLogger('Error encountered:', e.message );
        });

        recordButton.style.background = "red";
        stopButton.disabled = false;
        recordButton.disabled = true;
      });

      stopButton.addEventListener('click', ()=>{
        recorder.stop();
        console.log("recorder "+i+" stopped");
        recordButton.style.background = "";
        recordButton.style.color = "";
        stopButton.disabled = true;
        recordButton.disabled = false;
      });


      // Setup recorder state callbacks...
      recorder.onstart = function(){
        screenLogger("Recorder "+i+" is started");
        recordButton.disabled = true;
        stopButton.disabled = false;
      };

      recorder.onstop = function(){
        screenLogger("Recorder "+i+" is stopped");
        recordButton.disabled = false;
        stopButton.disabled = true;
      };

      recorder.onstreamerror = function(e){
        screenLogger('Error encountered: ', e.message );
      };

      recorder.ondataavailable = (typedArray) => {
        console.log("data available after #"+i+" Recorder.stop() called.");

        let clipName = nameInput.value;
        let annotationText = annotationInput.value;
        if(clipName == '') {
          // Auto generate a clip name?
          // clipName = "Anonymous_" + new Date().toISOString();
          clipName = "Recording-" + Math.round(Math.random() * 300);
          // clipName = prompt('Enter a memorable name for your voiceprint', clipName);
          nameInput.value = clipName;
          // wishesText = prompt('Enter your future wishes for your voice', wishesText);
          // wishInput.value = wishesText;
        }
        clipName = clipName + '.wav';

        const dataBlob = new Blob( [typedArray], { type: 'audio/wav' });
        const audioURL = window.URL.createObjectURL( dataBlob );

        const audio = document.createElement('audio');
        audio.setAttribute('controls', '');
        audio.src = audioURL;
        audio.audioBlob = dataBlob;

        const clipContainer = document.createElement('article');
        const clipLabel = document.createElement('p');
        const deleteButton = document.createElement('button');
        const link = document.createElement('a');

        clipContainer.classList.add('clip');
        deleteButton.textContent = 'Delete';
        deleteButton.className = 'delete';

        audio.clipName = clipName;
        link.href = audioURL;
        link.download = clipName;
        link.innerHTML = link.download;

        clipLabel.textContent = clipName;
        clipContainer.appendChild(audio);
        clipContainer.appendChild(clipLabel);
        clipContainer.appendChild(deleteButton);
        soundClips.appendChild(clipContainer);

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

          audio.clipName = clipLabel.textContent;
        }
      }; // end recorder.ondataavailable

    } // end for each recorder

  } // end onSuccess


  let onError = function(err) {
    screenLogger('The following error occured: ', err);
  }

  navigator.mediaDevices.getUserMedia(constraints).then(onSuccess, onError);

} else {
   screenLogger('getUserMedia not supported on your browser!');
}

function visualize(stream) {
  app.analyserLeft = app.audioCtx.createAnalyser();
  //app.analyserRight = app.audioCtx.createAnalyser();
  app.analyserLeft.fftSize = 2048;
  //app.analyserRight.fftSize = 2048;
  const bufferLength = app.analyserLeft.frequencyBinCount;
  app.dataArrays = [new Uint8Array(bufferLength)];

  console.log("Frequency Bin Count on Analyser", app.analyserLeft.frequencyBinCount);

  app.channelSplitter.connect(app.analyserLeft, 0);
  //app.channelSplitter.connect(app.analyserRight, 1);

  draw()

  function draw() {

    requestAnimationFrame(draw);

    app.analyserLeft.getByteTimeDomainData(app.dataArrays[0]);
    //app.analyserRight.getByteTimeDomainData(app.dataArrays[1]);

    let dataArray = app.dataArrays[0];
    const canvas = canvases[0];
    const canvasCtx = canvasContexts[0];
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

window.onresize = function() {
  //canvas.width = (mainSection.offsetWidth - 20) / 2;
}

window.onresize();
