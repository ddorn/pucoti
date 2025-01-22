Neutralino.init();
Neutralino.events.on("windowClose", () => Neutralino.app.exit());

window.Router = {
  get: (page) => {
    window.location.hash = page;
  },
};

let $app = document.querySelector("#app");

async function loadPage(name) {
  name = name.replace(/[^a-z]+/g, "");
  if (name == "") {
    name = "index";
  }

  try {
    let response = await fetch(`/pages/${page}.html`);
    let html = await response.text();

    // dispatchEvent invokes event handlers synchronously
    window.dispatchEvent(new CustomEvent("page-unmount", { next: page }));

    let $tmpl = document.createElement("div");
    $tmpl.innerHTML = html;

    let scripts = [];
    $tmpl.querySelectorAll("script").forEach((script) => {
      scripts.push(script.src);
      script.remove();
    });

    $app.innerHTML = $tmpl.innerHTML;

    for (const scriptSource of scripts) {
      // TODO: Handle errors.
      let src = await (await fetch(scriptSource)).text();

      // TODO: Isolate the context with new Function(). Does it work?
      eval(src);
    }
  } catch (e) {
    console.error(e);
  }
}

async function loadPageFromFragment() {
  return await loadPage(window.location.hash);
}

window.addEventListener("hashchange", loadPageFromFragment);

loadPageFromFragment();
