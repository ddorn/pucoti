const MINUTE = 60 * 1000;

let timer = document.getElementById('main-timer');

function redraw() {
    let now = new Date().getTime();
    let timeToRing = window.state.ringTime - now;
    let seconds = Math.floor((timeToRing) / 1000);
    let minutes = Math.floor(seconds / 60);
    let hours = Math.floor(minutes / 60);
    let time = "";
    if (hours > 0) {
        time += hours + ":";
    }
    time += (minutes % 60).toString().padStart(2, '0') + ":";
    time += (seconds % 60).toString().padStart(2, '0');
    timer.innerHTML = time;

}

let redrawHandle = setInterval(redraw, 1000);
redraw();

window.addEventListener('page-unmount', () => {
    clearInterval(redrawHandle);
});

// When pressing J/K, add/subtract 1 minute. If shift is pressed, do 5 instead
document.addEventListener('keydown', (e) => {
    if (e.key === 'j') {
        window.state.ringTime -= MINUTE;
    } else if (e.key === 'J') {
        window.state.ringTime -= 5 * MINUTE;
    } else if (e.key === 'k') {
        window.state.ringTime += MINUTE;
    } else if (e.key === 'K') {
        window.state.ringTime += 5 * MINUTE;
    } else if (e.key === 'r') {
        window.state.ringTime = new Date().getTime() + window.state.countdownDuration;
    } else {
        return;
    }
    redraw();
});
