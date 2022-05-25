var tslider = document.querySelector("#temperatureSlider");
var tnumber = document.querySelector("#temperatureNumber");
//tnumber.disabled = true;
tnumber.readOnly = true;

tslider.addEventListener('input', updateNumber);

const logBase = 4;

function updateNumber() {
  var x = Math.pow(tslider.value / 10.0, logBase) / 100.0;
  tnumber.value = Math.min((x + 0.01).toFixed(2), 100);
}

function updateSlider() {
  var x = Math.log((tnumber.value - 0.01) * 100.0) / Math.log(logBase);
  x = x * 10.0;
  tslider.value = x;
  console.log(x);
}

updateSlider();
