// import './style.css';
// import './flowbite.js';
import './sidebar.js';
// import './charts.js';
import './dark-mode.js';
import './editor.js'
import './policyBuilder.js'
import './flowbite.js'
import './toast.js'

document.body.addEventListener("initialiseFlowbite", function(evt){
    initFlowbite();
    console.log("Triggered initialiseFlowbite from HX-Trigger header")
})
