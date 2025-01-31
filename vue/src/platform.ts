import Neutralino from '@neutralinojs/lib';


export function hasNeutralino() {
  if (window.NL_PORT) {
    return true;
  }
  return false;
}

export function init() {
  if (hasNeutralino() && window.NL_TOKEN) {
    // We don't want to call init multiple times.
    // Once called, it moves NL_TOKEN to local storage, so we can check for that.
    // If we were to re-run init, it would not find the token anymore.
    Neutralino.init();

    Neutralino.events.on('spawnedProcess', (evt) => {
      switch(evt.detail.action) {
          case 'stdOut':
              console.log(evt.detail.data);
              break;
          case 'stdErr':
              console.error(evt.detail.data);
              break;
          case 'exit':
              console.log(`Process terminated with exit code: ${evt.detail.data}`);
              break;
      }
    });

    console.log('Neutralino initialized');
  }
}


export function runCmd(cmd: string) {
  if (hasNeutralino()) {
    console.log("Running command", cmd);
    Neutralino.os.spawnProcess(cmd);
  } else {
    console.error(`Neutralino not available, cannot run command: ${cmd}`);
  }
}
