# Building Pucoti for macOS

This document describes how to build the Pucoti Neutralino app for macOS, both locally and using GitHub Actions.

## Overview

Pucoti is built using NeutralinoJS, which creates cross-platform desktop applications. For macOS, we generate proper `.app` bundles that can be distributed, signed, and notarized.

## Prerequisites

### Local Development
- macOS (for building .app bundles)
- Node.js 22+
- pnpm
- jq (`brew install jq`)
- Neutralino CLI (`npm install -g @neutralinojs/neu`)

### GitHub Actions
The GitHub Actions workflow automatically handles all dependencies on `macos-latest` runners.

## Local Build Process

1. **Install dependencies:**
   ```bash
   cd www
   pnpm install
   cd ..
   ```

2. **Set up build scripts:**
   ```bash
   git clone https://github.com/hschneider/neutralino-build-scripts.git build-scripts
   cp build-scripts/build-mac.sh ./
   cp build-scripts/preproc-mac.sh ./
   cp build-scripts/postproc-mac.sh ./
   cp -r build-scripts/_app_scaffolds ./
   chmod +x build-mac.sh preproc-mac.sh postproc-mac.sh
   ```

3. **Build the app:**
   ```bash
   ./build-mac.sh
   ```

4. **Find your built apps:**
   The build process creates three variants:
   - `dist/mac_x64/pucoti.app` - Intel Macs
   - `dist/mac_arm64/pucoti.app` - Apple Silicon Macs (M1/M2/M3)
   - `dist/mac_universal/pucoti.app` - Universal binary (works on both)

## GitHub Actions Build

The GitHub Actions workflow is triggered on:
- Push to `main` or `develop` branches
- Pull requests to `main`
- Manual workflow dispatch

### Artifacts

The workflow produces several downloadable artifacts:
- `pucoti-mac-x64.zip` - Intel version
- `pucoti-mac-arm64.zip` - Apple Silicon version
- `pucoti-mac-universal.zip` - Universal version
- `pucoti-app-bundles` - All .app bundles in one artifact

## Configuration

The build configuration is defined in `neutralino.config.json`:

```json
{
  "buildScript": {
    "mac": {
      "architecture": ["x64", "arm64", "universal"],
      "minimumOS": "10.13.0",
      "appName": "pucoti",
      "appBundleName": "pucoti",
      "appIdentifier": "com.pucoti.app",
      "appIcon": "./packaging/icons/pucoti.icns"
    }
  }
}
```

## Build Process Details

1. **Frontend Build**: pnpm builds the Vue.js frontend in `www/dist/`
2. **Neutralino Build**: `neu build` creates the Neutralino binaries and resources
3. **App Bundle Creation**: The build script creates proper macOS .app bundles
4. **Icon Integration**: The .icns icon is copied into the app bundle
5. **Info.plist Processing**: App metadata is configured
6. **Extended Attributes**: Cleared for distribution

## Distribution

The resulting .app bundles are ready for:
- Direct distribution (users can drag to Applications folder)
- Code signing with Apple Developer certificates
- Notarization for distribution outside the Mac App Store
- Packaging into DMG installers

## Troubleshooting

### Common Issues

1. **Missing jq**: Install with `brew install jq`
2. **Permission denied**: Make sure build scripts are executable with `chmod +x build-mac.sh`
3. **Missing icon**: Ensure `packaging/icons/pucoti.icns` exists
4. **Neutralino CLI not found**: Install with `npm install -g @neutralinojs/neu`

### Build Script Customization

- **Pre-processing**: Add custom logic to `preproc-mac.sh`
- **Post-processing**: Add custom logic to `postproc-mac.sh`
- **Additional resources**: Copy to `${APP_RESOURCES}/` in post-processing

## Remote Build Testing

For testing on a remote macOS machine:

```bash
# Copy project (excluding large directories)
rsync -avz --exclude=node_modules --exclude=dist --exclude=build-scripts ./ user@mac-host:~/project/

# SSH and build
ssh user@mac-host "cd ~/project && source ~/.zprofile && pnpm install && ./build-mac.sh"
```

## Security Notes

- The build uses pre-built Neutralino binaries from the official repository
- Review the [Neutralino security policy](https://neutralino.js.org/docs/security/overview) before distribution
- Consider code signing for production releases
- Use notarization for apps distributed outside the Mac App Store