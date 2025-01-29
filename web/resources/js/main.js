Neutralino.init();
Neutralino.events.on("windowClose", () => Neutralino.app.exit());

let $app = document.querySelector("#app");

/**
 * Fetches the page from /pages/XXXX.html and
 * replaces the inside of #app with its content.
 * If name is empty, loads /pages/home.html
 *
 * It provides an unmount hook
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
        // TODO: let the browser do it
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
