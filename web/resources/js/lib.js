const MINUTE = 60 * 1000;

// switchToPage is a global utility to redirect to another page
// Example:
// switchToPage('home')
// switchToPage('settings')
function switchToPage(name) {
  // This change is picked up by the router.
  window.location.hash = name;
}

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

/**
 * Get the size metrics of a simple text element.
 *
 * @param {HTMLElement} el The element to get the text metrics for
 * @param {string} fontSizeOverride The font size to use, in CSS units (e.g. '16px')
 *
 * @see https://stackoverflow.com/questions/118241/calculate-text-width-with-javascript/21015393#21015393
 */
function getTextMetrics(el, fontSizeOverride) {
  // re-use canvas object for better performance
  let canvas =
    getTextMetrics.canvas ||
    (getTextMetrics.canvas = document.createElement("canvas"));
  let context = canvas.getContext("2d");

  let fontWeight = getCssStyle(el, "font-weight") || "normal";
  let fontSize = fontSizeOverride || getCssStyle(el, "font-size");
  let fontFamily = getCssStyle(el, "font-family") || "Times New Roman";
  context.font = `${fontWeight} ${fontSize} ${fontFamily}`;

  let text = el.innerText || el.value || el.getAttribute("placeholder");

  let metrics = context.measureText(text);
  metrics.actualHeight =
    metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent;
  return metrics;
}

function getCssStyle(element, prop) {
  return window.getComputedStyle(element, null).getPropertyValue(prop);
}

/**
 * Scale the font size of the element to the maximum that fits inside the element.
 *
 * @param {HTMLElement} element
 */
function scaleMaxSize(element) {
  let fontSizeLower = 0;
  let fontSizeUpper = 2000;

  // Actual available, without the padding.lib.
  let width =
    element.clientWidth -
    parseFloat(getCssStyle(element, "padding-left")) -
    parseFloat(getCssStyle(element, "padding-right"));
  let height =
    element.clientHeight -
    parseFloat(getCssStyle(element, "padding-top")) -
    parseFloat(getCssStyle(element, "padding-bottom"));

  // Simple binary search to find the largest font size that fits
  while (fontSizeUpper > fontSizeLower + 1) {
    let fontSize = Math.floor((fontSizeUpper + fontSizeLower) / 2);
    let metrics = getTextMetrics(element, fontSize + "px");
    if (metrics.width > width || metrics.actualHeight > height) {
      fontSizeUpper = fontSize;
    } else {
      fontSizeLower = fontSize;
    }
  }

  // console.log(getTextMetrics(element, fontSizeLower + 'px'), element, "width", width, "height", height);

  element.style.fontSize = fontSizeLower + "px";
}

function scaleMaxSizeAll() {
  document.querySelectorAll(".scale-max-size").forEach(scaleMaxSize);
}

// Run the scaling every time the window is resized
window.addEventListener("resize", scaleMaxSizeAll);

// Log everything about spawned processes
/*
Neutralino.events.on("spawnedProcess", (evt) => {
  switch (evt.detail.action) {
    case "stdOut":
      console.log(evt.detail.id, evt.detail.data);
      break;
    case "stdErr":
      console.error(evt.detail.id, evt.detail.data);
      break;
    case "exit":
      console.log(
        `Process ${evt.details.id} exited with code ${evt.detail.code}`,
      );
      break;
  }
});
*/

// Time utils

/**
 * Convert a human duration such as "1h 30m" to seconds.
 * @param {string} duration - The duration string to convert
 * @returns {number} The duration in miliseconds
 */
function humanTimeToMs(duration) {
  if (duration.startsWith("-")) {
    return -humanTimeToMs(duration.slice(1));
  }

  // Parse the duration.
  let total = 0;
  const multiplier = { s: 1, m: 60, h: 3600, d: 86400 };

  const parts = duration.split(" ");
  for (let part of parts) {
    try {
      const value = parseInt(part.slice(0, -1));
      const unit = part.slice(-1);

      if (isNaN(value) || !(unit in multiplier)) {
        throw new Error(`Invalid duration part: ${part}`);
      }

      total += value * multiplier[unit];
    } catch (error) {
      throw new Error(`Invalid duration part: ${part}`);
    }
  }

  return total * 1000;
}
