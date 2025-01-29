(() => {
  let $timer = document.getElementById("main-timer");
  let $intention = document.getElementById("intention");

  function redraw() {
    let now = new Date().getTime();
    let timeToRing = window.state.ringTime - now;
    let isNegative = timeToRing < 0;
    let time = fmtSeconds(timeToRing).join(":");
    if (timeToRing >= 3600000) {
      $timer.parentNode.setAttribute("viewBox", "0 0 60 12.5");
    } else {
      $timer.parentNode.setAttribute("viewBox", "0 0 46 12.5");
    }
    $timer.innerHTML = time;
    $timer.classList.toggle("is-negative", isNegative);

    scaleMaxSizeAll();
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
      $intention.focus();
    } else {
      return;
    }
    e.preventDefault();
    redraw();
  });
  $intention.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      window.state.setIntention($intention.value);
      $intention.blur(); // Remove focus from intention
    }
    e.stopPropagation();
  });
})();
