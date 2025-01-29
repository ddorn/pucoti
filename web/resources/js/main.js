Neutralino.init();
Neutralino.events.on("windowClose", () => Neutralino.app.exit());

let $app = document.querySelector("#app");

/**
 * Fetches the page from /pages/XXXX.html and
 * replaces the inside of #app with its content.
 * If name is empty, loads /pages/home.html
 *
 * It provides an unmount hook, listen to the page-unmount event.
 *
 * This is hacky.
 * @param {string} name of the page
 */
async function loadPage(name) {
  name = name.replace(/[^a-z]+/g, "");
  if (name == "" || name == "index") {
    name = "home";
  }

  try {
    let response = await fetch(`/pages/${name}.html`);
    let html = await response.text();

    // dispatchEvent invokes event handlers synchronously
    window.dispatchEvent(new CustomEvent("page-unmount", { next: name }));

    let $tmpl = document.createElement("div");
    $tmpl.innerHTML = html;

    let scripts = [];
    for (const script of $tmpl.querySelectorAll("script")) {
      if (script.src !== "") {
        // TODO: let the browser do it, listen to the load event
        let src = await (await fetch(script.src)).text();

        scripts.push(src);
      } else {
        scripts.push(script.innerText);
      }

      script.remove();
    }

    $app.innerHTML = $tmpl.innerHTML;

    for (const src of scripts) {
      new Function(src)();
    }
  } catch (e) {
    console.error("Evaluated script errored, see below");
    console.error(e);
  }
}

loadPage(window.location.hash);
window.addEventListener("hashchange", () => loadPage(window.location.hash));

/**
 * Storage arbitrates between different file storage strategies,
 * like the local fs, or indexed db, or the Filesystem API (?)
 */
class Storage {
  async writeFile(name, data) {}
  async readFile(name) {}
}

class EntrepriseLocalFilesystemStrategy {
  async writeFile(name, data) {
    try {
      await Neutralino.filesystem.writeFile(name, data);
    } catch (e) {
      console.error(e);
      throw new Error(`Could not read file: ${name}`);
    }
  }
  async readFile(name) {}
}

window.Storage = new Storage([new EntrepriseLocalFilesystemStrategy()]);
