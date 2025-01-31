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

// window.Storage = new Storage();
