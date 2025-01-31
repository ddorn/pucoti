import Neutralino from '@neutralinojs/lib';


export function hasNeutralino() {
  if (window.NL_PORT) {
    return true;
  }
  return false;
}

export function init() {
  if (hasNeutralino()) {
    Neutralino.init();
  }
}

export function runCmd(cmd: string) {
  if (hasNeutralino()) {
    Neutralino.os.spawnProcess(cmd);
  } else {
    console.error(`Neutralino not available, cannot run command: ${cmd}`);
  }
}
