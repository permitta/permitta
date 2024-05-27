
// TODO these should probably be tied with events so they dont need to be exposed
function onPillDragStart(event) {
    event.dataTransfer.setData("text", event.target.id)
    // console.log("pill drag start")
    // console.log(event)
}

function onPillDrop(event) {
    event.preventDefault();
    const id = event.dataTransfer.getData("text")
    event.target.appendChild(document.getElementById(id))

    // console.log("pill drop ", id)
    // console.log(event)
}

export {onPillDrop, onPillDragStart}