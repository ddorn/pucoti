/*
Neutralino.init();
Neutralino.events.on("windowClose", () => Neutralino.app.exit());
*/

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
 * isRunningInBrowser always return false for now,
 * running pucoti in a browser is not (yet) supported.
 */
function isRunningInBrowser() {
  return false;
}

/**
 * Storage arbitrates between different file storage strategies.
 * and exposes a common writeFile(name, data), readFile(name)
 * interface.
 */
class Storage {
  CONFIG_PATH = "~/.config/pucoti.json";
  DATA_PATH = "~/.config/data.json";

  constructor() {
    this.fs = new EntrepriseLocalFilesystemStrategy();
  }

  async writeFile(name, data) {
    if (isRunningInBrowser()) {
      throw new Error("Running in browser is not supported.");
    }

    return this.fs.writeFile(name, data);
  }

  async readFile(name) {
    if (isRunningInBrowser()) {
      throw new Error("Running in browser is not supported.");
    }

    return this.fs.readFile(name);
  }

  /**
   * writeConfig expects a Javascript object containing the config.
   */
  async writeConfig(data) {
    return await this.writeFile(this.CONFIG_PATH, JSON.stringify(data));
  }

  async config() {
    return JSON.parse(await this.readFile(this.CONFIG_PATH));
  }

  /**
   * writeData expects a Javascript object containing the data.
   */
  async writeData(data) {
    return await this.writeFile(this.DATA_PATH, JSON.stringify(data));
  }

  async data() {
    return JSON.parse(await this.readFile(this.DATA_PATH));
  }
}

/**
 * This entreprise-grade strategy uses Neutralino.filesystem
 * to read and write files.
 */
class EntrepriseLocalFilesystemStrategy {
  async writeFile(name, data) {
    try {
      await Neutralino.filesystem.writeFile(name, data);
    } catch (e) {
      console.error(e);
      throw new Error(`Could not write file ${name}`);
    }

    return name;
  }

  async readFile(name) {
    try {
      return await Neutralino.filesystem.readFile(name);
    } catch (e) {
      console.error(e);
      throw new Error(`Could not read file ${name}`);
    }
  }
}

window.Storage = new Storage();
