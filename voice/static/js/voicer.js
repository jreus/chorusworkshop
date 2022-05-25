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

document.addEventListener('keydown', keyPressed);
document.addEventListener('keyup', keyReleased);

let pressedKeys = [];

function keyPressed(e) {
  if(e.code.includes("Digit")) {
    let num = parseInt(e.code[5]);
    if(num == 0) { num = 10 };
    if((num <= audioplayerDivs.length) && !pressedKeys[num]) {
      let audioDiv = audioplayerDivs[num-1];
      let audioElement = audioDiv.children[0];
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
      let audioElement = audioDiv.children[0];
      audioElement.pause();
      audioDiv.style.background = "gold";
    }
  }
}
