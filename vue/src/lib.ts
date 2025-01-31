

/**
 * Send a clock tick event to all elements, to update all the displays at the same time.
 */
export function tickClock() {
  document.dispatchEvent(new Event("clock-tick"));
}

/**
 * Get the size metrics of a simple text element.
 *
 * @param {HTMLElement} el The element to get the text metrics for
 * @param {string} fontSizeOverride The font size to use, in CSS units (e.g. '16px')
 *
 * @see https://stackoverflow.com/questions/118241/calculate-text-width-with-javascript/21015393#21015393
 */
export function getTextMetrics(el: HTMLElement, fontSizeOverride: string) {
  // re-use canvas object for better performance
  const canvas = getTextMetrics.canvas || (getTextMetrics.canvas = document.createElement("canvas"));
  const context = canvas.getContext("2d");

  const fontWeight = getCssStyle(el, "font-weight") || "normal";
  const fontSize = fontSizeOverride || getCssStyle(el, "font-size");
  const fontFamily = getCssStyle(el, "font-family") || "Times New Roman";
  context.font = `${fontWeight} ${fontSize} ${fontFamily}`;

  const text = el.innerText || el.value || el.getAttribute("placeholder");

  const metrics = context.measureText(text);
  metrics.actualHeight =
    metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent;
  return metrics;
}

export function getCssStyle(element: HTMLElement, prop: string) {
  return window.getComputedStyle(element, null).getPropertyValue(prop);
}

/**
 * Scale the font size of the element to the maximum that fits inside the element.
 *
 * @param {HTMLElement} element
 */
export function scaleMaxSize(element: HTMLElement) {
  let fontSizeLower = 0;
  let fontSizeUpper = 2000;

  // Actual available, without the padding.lib.
  const width =
    element.clientWidth -
    parseFloat(getCssStyle(element, "padding-left")) -
    parseFloat(getCssStyle(element, "padding-right"));
  const height =
    element.clientHeight -
    parseFloat(getCssStyle(element, "padding-top")) -
    parseFloat(getCssStyle(element, "padding-bottom"));

  // Simple binary search to find the largest font size that fits
  while (fontSizeUpper > fontSizeLower + 1) {
    const fontSize = Math.floor((fontSizeUpper + fontSizeLower) / 2);
    const metrics = getTextMetrics(element, fontSize + "px");
    if (metrics.width > width || metrics.actualHeight > height) {
      fontSizeUpper = fontSize;
    } else {
      fontSizeLower = fontSize;
    }
  }

  // console.log(getTextMetrics(element, fontSizeLower + 'px'), element, "width", width, "height", height);

  element.style.fontSize = fontSizeLower + "px";
}

export function scaleMaxSizeAll() {
  document.querySelectorAll(".scale-max-size").forEach(scaleMaxSize);
}

// Run the scaling every time the window is resized
// window.addEventListener("resize", scaleMaxSizeAll);  // TODO
