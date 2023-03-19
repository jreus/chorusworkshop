const fileslist = document.querySelector('#fileslist');
const overlay = document.querySelector('#overlay')
const voicefile = document.querySelector('#voice-recording')

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


window.onresize = function() {}
window.onresize();
