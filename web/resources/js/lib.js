const MINUTE = 60 * 1000;

// switchToPage is a global utility to redirect to another page
// Example:
// switchToPage('index')
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

// Log everything about spawned processes
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
