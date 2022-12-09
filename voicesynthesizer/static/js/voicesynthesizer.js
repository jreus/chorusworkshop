const submitForm = document.querySelector('#synthesisform');
const textfield = document.querySelector('#text');
const voice = document.querySelector('#voice-dropdown');
const phonetic = document.querySelector('#phonetic');
const fileslist = document.querySelector('#fileslist');
const overlay = document.querySelector('#overlay')

const voicefile = document.querySelector('#voice-recording')
const annotations = document.querySelector('#annotations')
const wishes = document.querySelector('#wishes')

// sets the overlay inner HTML, and optionally pauses before showing, or hides it after a number of ms
function setOverlay(innerhtml, msPauseBefore=0, msHideAfter=0) {
  setTimeout(()=>{
    overlay.innerHTML = innerhtml;
    overlay.style.visibility = 'visible';
    if(msHideAfter > 0) {
      // Set a hide timeout...
      setTimeout(()=>{ overlay.style.visibility = 'hidden' }, msHideAfter);
    }
  }, msPauseBefore);
}

// Populate Voice Info
function voiceSelected(e) {
  let selected = voice.options[voice.selectedIndex];
  console.log("Voice Selected:", selected.value, selected.text);
  console.log(" MetaData:", voicedata[selected.value]);
  let recordingfile;
  recordingfile = voicedata[selected.value]['filepath']
  let annotationstext;
  annotationstext = voicedata[selected.value]['annotations'];
  let wishestext;
  wishestext = voicedata[selected.value]['wishes'];
  let transcripttext;
  transcripttext = voicedata[selected.value]['transcript'];

  if(e != null) {
    setOverlay("<h3>voice of "+selected.text+"</h3><br><h3>my wishes</h3><span class='wishes'>"+wishestext+"</span>", 0, 5000);
  }
  voicefile.src = "uploads/" + recordingfile;
  annotations.innerHTML = "<b>Description:</b> " + annotationstext;
  wishes.innerHTML = "<b>Wishes for use:</b> " + wishestext;
}
voice.addEventListener('change', voiceSelected);
voiceSelected(null); // refresh wishes list


function refreshData(e) {
  // Ask the server to give the latest voice data, then populate it here...
  let request = new XMLHttpRequest();
  request.addEventListener('load', ()=>{
    let response = request.response;
    try {
      let json = JSON.parse(response);
      console.log("Got json", json);

      // Clear current voices / select list
      voicedata = {};
      allvoices = [];

      while (voice.options.length > 0) {
          voice.remove(0);
      }

      // Iterate through json...
      // repopulate allvoices & voicedata while repopulating select list
      for (const [voiceid, metadata] of Object.entries(json)) {
        console.log(voiceid, metadata);
        voicedata[voiceid] = metadata;
        allvoices.push(voiceid);
        opt = document.createElement('option');
        opt.value = voiceid;
        opt.text = metadata['name'];
        voice.appendChild(opt);
      }

      voiceSelected(null); // refresh wishes list
      return true;

    } catch(e) {
      console.log("Error", e);
      console.log("Server Error: " + response);
      return false;
    };
  });

  let formData = new FormData();
  formData.append('command', 'voiceData');
  request.open("POST", "/getdata");
  request.send(formData);
}
refreshButton.addEventListener('click', refreshData);

var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
let audioplayerDivs = document.querySelectorAll('.player');
audioplayerDivs.forEach((apd)=>{
  // TODO: add ontouchstart / ontouchend event handlers?
  apd.onmousedown = function(e) {
      e.stopPropagation();
      e.preventDefault();
      var i = parseInt(this.innerHTML[0]) - 1;
      var audioElement = this.children[0];

      //console.log("THIS:", this, "CHILDREN:", this.children);
      //var audioElement = document.getElementsByTagName('audio')[i];

      audioElement.currentTime = 0; // other times possible?
      audioElement.play();
      this.style.background = "red";
    };

  apd.onmouseup = function() {
     this.style.background = "gold";
  };
});

let pressedKeys = [];

function keyPressed(e) {
  if(e.code.includes("Digit")) {
    let num = parseInt(e.code[5]);
    if(num == 0) { num = 10 };
    if((num <= audioplayerDivs.length) && !pressedKeys[num]) {
      let audioDiv = audioplayerDivs[num-1];
      let audioElement = audioDiv.children[1];
      console.log(num);
      pressedKeys[num] = true;
      audioElement.currentTime = 0;
      audioElement.play();
      audioDiv.style.background = "red";
    }
  }
}

function keyReleased(e) {
  if(e.code.includes("Digit")) {
    let num = parseInt(e.code[5]);
    if(num == 0) { num = 10 };
    pressedKeys[num] = false;
    if(num <= audioplayerDivs.length) {
      let audioDiv = audioplayerDivs[num-1];
      let audioElement = audioDiv.children[1];
      audioElement.pause();
      audioDiv.style.background = "gold";
    }
  }
}

document.addEventListener('keydown', keyPressed);
document.addEventListener('keyup', keyReleased);

submitForm.addEventListener('submit', (e)=>{

  // Data error checking...

  let text = textfield.value;

  if (text != "") {
    setOverlay("<h2>Synthesizing ...</h2><br><quote>"+text+"</quote>", 0, 2000);
    return true
  } {
    setOverlay("<h3>Enter some text to synthesize.</h3>", 0, 2000);
  }
  e.preventDefault();
  return false;
});

// Synthesis request submission...
// submitForm.addEventListener('submit', (e)=>{
//   // On form submission, prevent default
//   e.preventDefault();
//   console.log("Submit!");
//     let formData = new FormData(submitForm);
//     // Submit the form via xhr
//     let request = new XMLHttpRequest();
//     console.log("Request status:", request.status);
//     request.addEventListener('load', ()=>{
//       let response = request.response;
//       console.log("Got XHR response", request.response);
//       if(response == 'Success') {
//         console.log("Request status:", request.status);
//       } else {
//         console.log(request);
//         console.log("Request status:", request.status);
//       }
//     });
//     console.log("Sending Form Data!");
//     request.open("POST", "/");
//     request.send(formData);
//
// });

window.onresize = function() {}
window.onresize();
