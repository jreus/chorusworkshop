var tslider = document.querySelector("#temperatureSlider");
var tnumber = document.querySelector("#temperatureNumber");
tslider.numberbox = tnumber;
tslider.numberscale = 'log4';
tnumber.readOnly = true;
tslider.addEventListener('input', updateNumber);

var mlslider = document.querySelector("#maxLengthSlider");
var mlnumber = document.querySelector("#maxLengthNumber");
mlslider.numberbox = mlnumber;
mlslider.numberscale = 'lin';
mlnumber.readOnly = true;
mlslider.addEventListener('input', updateNumber);

var sliders = [tslider, mlslider];

const logBase = 4;

function updateNumber(ev) {
  let slider = ev.target;
  let numberbox = slider.numberbox;
  let numberval;

  switch(slider.numberscale) {
    case 'lin':
      numberval = slider.value;
    break;
    case 'log4':
      numberval = Math.pow(slider.value / 10.0, 4) / 100.0;
      numberval = Math.min((numberval + 0.01).toFixed(2), 100);
    break;
    default:
      console.log("Error: unknown numberscale "+slider.numberscale);
  };

  numberbox.value = numberval;
}

function updateSliders() {

  sliders.forEach((slider)=>{
    let numberbox = slider.numberbox;
    let numberval = numberbox.value;

    switch(slider.numberscale) {
      case 'lin':
        slider.value = numberval;
      break;
      case 'log4':
        numberval = Math.log((numberval - 0.01) * 100.0) / Math.log(4);
        slider.value = numberval * 10.0;
      break;
      default:
        console.log("Error: unknown numberscale "+slider.numberscale);
    };
  });
}

updateSliders();
