function screenLogger(text, data) {
  log.innerHTML += "\n" + text + " " + (data || '');
}

if (!Recorder.isRecordingSupported()) {
  screenLogger("Recording features are not supported in your browser.");
} else {
  screenLogger("Recording is supported... ");

  let state = {};


  state.constraints = { audio: {
      optional: [{ echoCancellation: false }]
  } };

  state.chunks = [];

  let onSuccess = function(stream) {
    console.log("Got Stream", stream);

    if(!state.audioCtx) {
      state.audioCtx = new AudioContext();
    }

    state.streamSource = state.audioCtx.createMediaStreamSource(stream);
    state.channelSplitter = state.audioCtx.createChannelSplitter(2);
    state.signalLeft = new GainNode(state.audioCtx, {gain: 1.0, channelCount: 1});
    state.signalRight = new GainNode(state.audioCtx, {gain: 1.0, channelCount: 1});
    state.bufferLength = 2048 * 2;
    state.dataArrays = [new Uint8Array(state.bufferLength), new Uint8Array(state.bufferLength)];

    console.log("Input Audio as a MediaStreamSource", state.streamSource);
    state.streamSource.connect(state.channelSplitter);
    state.channelSplitter.connect(state.signalLeft, 0);
    state.channelSplitter.connect(state.signalRight, 1);

  }

  let onError = function(err) {
    console.log('The following error occured: ' + err);
  }


  init.addEventListener( "click", function(){

    navigator.mediaDevices.getUserMedia(state.constraints).then(onSuccess, onError)
      .then(()=>{
        init.disabled = true;
        start.disabled = false;
        monitorGain.disabled = true;
        recordingGain.disabled = true;

        // Now we have two recorders...
        state.recorderLeft = new Recorder({
          monitorGain: parseInt(monitorGain.value, 10),
          recordingGain: parseInt(recordingGain.value, 10),
          numberOfChannels: 1,
          wavBitDepth: 16,
          encoderPath: "/js/opusrecorder/encoderWorker.min.js",
          sourceNode: state.signalLeft
        });

        state.recorderRight = new Recorder({
          monitorGain: parseInt(monitorGain.value, 10),
          recordingGain: parseInt(recordingGain.value, 10),
          numberOfChannels: 1,
          wavBitDepth: 16,
          encoderPath: "/js/opusrecorder/encoderWorker.min.js",
          sourceNode: state.signalRight
        });



        pause.addEventListener( "click", function(){ state.recorderLeft.pause(); });
        resume.addEventListener( "click", function(){ state.recorderLeft.resume(); });
        stopButton.addEventListener( "click", function(){ state.recorderLeft.stop(); });
        start.addEventListener( "click", function(){
          state.recorderLeft.start().catch(function(e){
            screenLogger('Error encountered:', e.message );
          });
        });

        state.recorderLeft.onstart = function(){
          screenLogger('Recorder Left is started');
          start.disabled = resume.disabled = true;
          pause.disabled = stopButton.disabled = false;
        };

        state.recorderLeft.onstop = function(){
          screenLogger('Recorder Left is stopped');
          start.disabled = false;
          pause.disabled = resume.disabled = stopButton.disabled = true;
        };

        state.recorderLeft.onpause = function(){
          screenLogger('Recorder Left is paused');
          pause.disabled = start.disabled = true;
          resume.disabled = stopButton.disabled = false;
        };

        state.recorderLeft.onresume = function(){
          screenLogger('Recorder Left is resuming');
          start.disabled = resume.disabled = true;
          pause.disabled = stopButton.disabled = false;
        };

        state.recorderLeft.onstreamerror = function(e){
          screenLogger('Error encountered: ' + e.message );
        };

        state.recorderLeft.ondataavailable = function( typedArray ){
          var dataBlob = new Blob( [typedArray], { type: 'audio/wav' } );
          var fileName = new Date().toISOString() + ".wav";
          var url = URL.createObjectURL( dataBlob );

          var audio = document.createElement('audio');
          audio.controls = true;
          audio.src = url;

          var link = document.createElement('a');
          link.href = url;
          link.download = fileName;
          link.innerHTML = link.download;

          var li = document.createElement('li');
          li.appendChild(link);
          li.appendChild(audio);

          recordingslist.appendChild(li);
        };
      });
    });


}
