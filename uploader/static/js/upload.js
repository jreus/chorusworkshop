function logger(text, data) {
  console.log(text);
  let p = document.createElement('p');
  let t = document.createElement('span');
  let d = document.createElement('span');
  t.innerHTML = text;
  d.innerHTML = (data || '');
  t.classList.add('log-text');
  d.classList.add('log-data');

  p.appendChild(t);
  p.appendChild(d);
  logElement.appendChild(p);
}

const overlay = document.querySelector('#overlay')
const submitForm = document.querySelector('#uploadform')
const participantname = document.querySelector('#name');
const fileupload = document.querySelector('#audiofile');
const annotations = document.querySelector('#annotations');
const wishes = document.querySelector('#wishes');
const logElement = document.querySelector('#log')

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

submitForm.addEventListener('submit', (e)=>{
  // On form submission, prevent default
  e.preventDefault();
  // Check if a file upload has been selected...

  if(fileupload.files.length > 0) { // Construct a FormData object
    let formData = new FormData(submitForm);
    let fileName = participantname.value;
    // Submit the form via xhr
    let request = new XMLHttpRequest();
    console.log("Request status:", request.status);
    request.addEventListener('load', ()=>{
      let response = request.response;
      console.log("Got XHR response", request.response);
      if(response == 'Success') {
        // Delete uploaded clip...
        logger("Uploaded ", fileName);
        console.log("Request status:", request.status);
        setOverlay("<h1>Success! 👄</h1>",2000, 2000);
      } else {
        // Print error...
        logger("Error uploading recording '"+fileName+"'");
        console.log(request);
        console.log("Request status:", request.status);
        setOverlay("<h1>Upload Failed 💔</h1>", 2000, 2000);
      }
    });
    console.log("Sending Form Data!");
    setOverlay("<h1 class='gradient-glow'>uploading ...</h1>")
    request.open("POST", "/");
    request.send(formData);
  } else {
        // Throw an error or something? Cannot do anything...
        logger("You need to select an audiofile to upload!");
        setOverlay("<h2>You didn't select a voice recording file!</h2>", 0, 4000);
        console.log("No audio recordings :-( ");
        return;
  }

});

window.onresize = function() {}
window.onresize();
