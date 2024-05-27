import './sidebar.js';
// import './charts.js';
import './dark-mode.js';
import './flowbite.js'
import './toast.js'
import {getEditorContent} from './editor.js'
import {onPillDrop, onPillDragStart} from './policyBuilder.js'

document.body.addEventListener("initialiseFlowbite", function(evt){
    initFlowbite();
    console.log("Triggered initialiseFlowbite from HX-Trigger header")
})

// HTMX expects some functions to be available on the global (window) scope
window.onPillDrop = onPillDrop;
window.onPillDragStart = onPillDragStart;

