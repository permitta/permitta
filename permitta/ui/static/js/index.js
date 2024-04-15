// import './style.css';
// import './flowbite.js';
import './sidebar.js';
// import './charts.js';
import './dark-mode.js';

// import { Modal } from './flowbite';


document.body.addEventListener("initialiseFlowbite", function(evt){
    initFlowbite();
    console.log("Triggered initialiseFlowbite from HX-Trigger header")
})

// document.body.addEventListener("showDefaultModal", function(evt){
//     initFlowbite();
//     const $modalElement = document.querySelector('#default-modal-wrapper');
//     const modal = new Modal($modalElement);
//     modal.show();
//     console.log("Triggered showDefaultModal from HX-Trigger header")
// })
