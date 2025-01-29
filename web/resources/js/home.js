(() => {
  let $app = document.getElementById("app");
  let $timer = document.getElementById("main-timer");
  let $intention = document.getElementById("intention");
  let $secondaryTimers = document.getElementById("secondary-timers");
  let $secondaryTimerTemplate = document.getElementById("timer-template");

  function setTimer(element, timer) {
    let time = fmtSeconds(timer.value).join(":");
    element.querySelector(".timer-value").innerText = time;
    // element.querySelector(".timer-label").innerText = timer.name;
    if (timer.value < 0) {
      element.style.color = "var(--timer-negative)";
    } else {
      element.style.color = timer.color;
    }
  }

  function redraw() {
    let timers = window.state.getTimers();

    // Main timer
    setTimer($timer, timers["Main timer"]);

    // Secondary timers.
    // Ensure there are enough timers in the row
    let numTimers = window.state.secondaryTimers.length;
    let numChildren = $secondaryTimers.children.length;
    for (let i = numChildren; i < numTimers; i++) {
      let $newTimer = $secondaryTimerTemplate.content.cloneNode(true);
      $secondaryTimers.appendChild($newTimer);
    }
    // Then set their content.
    for (let i = 0; i < numTimers; i++) {
      let timer = timers[window.state.secondaryTimers[i]];
      let $timer = $secondaryTimers.children[i];
      setTimer($timer, timer);
      $timer.style.width = `calc(100% / ${numTimers})`;
    }

    scaleMaxSizeAll();
  }

  let redrawHandle = setInterval(redraw, 1000);
  redraw();

  // When pressing J/K, add/subtract 1 minute. If shift is pressed, do 5 instead
  document.addEventListener("keydown", (e) => {
    switch (e.key) {
      case "j":
        window.state.ringTime -= MINUTE;
        break;
      case "J":
        window.state.ringTime -= 5 * MINUTE;
        break;
      case "k":
        window.state.ringTime += MINUTE;
        break;
      case "K":
        window.state.ringTime += 5 * MINUTE;
        break;
      case "r":
        window.state.ringTime =
          new Date().getTime() + window.state.countdownDuration;
        // Key corresponding to 0-9 -> set to that minute
        // + if shift is pressed, set to 10*key
        break;
      case "h":
        window.switchToPage("help");
        break;
      case "Enter":
        $intention.focus();
      default:
        if (e.code.startsWith("Digit")) {
          let digit = parseInt(e.code[5]);
          console.log(e.code, digit);
          if (e.shiftKey) {
            digit *= 10;
          }
          window.state.ringTime = new Date().getTime() + digit * MINUTE;
          window.state.countdownDuration = digit * MINUTE;
        } else {
          return;
        }
    }

    e.preventDefault();
    redraw();
  });

  window.addEventListener("page-unmount", () => {
    clearInterval(redrawHandle);
  });

  $intention.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      window.state.setIntention($intention.value);
      $intention.blur(); // Remove focus from intention
    }
    window.requestAnimationFrame(() => scaleMaxSize($intention));
    e.stopPropagation();
  });
})();
