const MINUTE = 60 * 1000;

let $timer = document.getElementById("main-timer");
let $intention = document.getElementById("intention");
let focusOnIntention = false;

// TODO: Move the following to a lib file

/**
 * Format a time in seconds to the parts of a string.
 *
 * Example: 3661 -> ["1", "01", "01"]
 * Example: 61 -> ["01", "01"]
 *
 * @param {number} time Duration in seconds
 * @returns {string[]} Array of strings representing the time in the format [hours, minutes, seconds]. Hours is there only if it's not 0
 */
function fmtSeconds(time) {
  let seconds = Math.floor(Math.abs(time) / 1000);
  let minutes = Math.floor(seconds / 60);
  let hours = Math.floor(minutes / 60);
  let parts = [];
  if (hours > 0) {
    parts.push(hours);
  }
  parts.push((minutes % 60).toString().padStart(2, "0"));
  parts.push((seconds % 60).toString().padStart(2, "0"));
  return parts;
}

function redraw() {
  let now = new Date().getTime();
  let timeToRing = window.state.ringTime - now;
  let isNegative = timeToRing < 0;
  let time = fmtSeconds(timeToRing).join(":");
  $timer.innerHTML = time;
  $timer.classList.toggle("is-negative", isNegative);
}

let redrawHandle = setInterval(redraw, 1000);
redraw();

window.addEventListener("page-unmount", () => {
  clearInterval(redrawHandle);
});

// When pressing J/K, add/subtract 1 minute. If shift is pressed, do 5 instead
document.addEventListener("keydown", (e) => {
  if (e.key === "j") {
    window.state.ringTime -= MINUTE;
  } else if (e.key === "J") {
    window.state.ringTime -= 5 * MINUTE;
  } else if (e.key === "k") {
    window.state.ringTime += MINUTE;
  } else if (e.key === "K") {
    window.state.ringTime += 5 * MINUTE;
  } else if (e.key === "r") {
    window.state.ringTime =
      new Date().getTime() + window.state.countdownDuration;
    // Key corresponding to 0-9 -> set to that minute
    // + if shift is pressed, set to 10*key
  } else if (e.code.startsWith("Digit")) {
    let digit = parseInt(e.code[5]);
    console.log(e.code, digit);
    if (e.shiftKey) {
      digit *= 10;
    }
    window.state.ringTime = new Date().getTime() + digit * MINUTE;
    window.state.countdownDuration = digit * MINUTE;
  } else if (e.key === "Enter") {
    // Toggle focus on intention
    focusOnIntention = !focusOnIntention;
    if (focusOnIntention) {
      $intention.focus();
    }
  } else {
    return;
  }
  e.preventDefault();
  redraw();
});
$intention.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    window.state.intention = $intention.value;
    console.log(window.state.intention);
  }
}
);
