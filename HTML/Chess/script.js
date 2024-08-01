import { initialGame } from "./initialGame.config.js"

let selected;

for (const [cell, piece] of Object.entries(initialGame)) {
    var box = document.getElementById(cell)
    
    box.style.backgroundImage = "url(./images/" + piece + ".png)"
    box.style.backgroundSize = "cover"

    box.onclick = function() {
        if (box.style.backgroundImage !== null && selected == null) {
            selected = cell
            console.log(cell)
        }
    }
}