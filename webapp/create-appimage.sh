#!/bin/bash
#
# create-appimage.sh
#
# Helper script to create AppImage from Neutralino Linux build
#
# Usage: ./create-appimage.sh <architecture>
# Example: ./create-appimage.sh arm64

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <architecture>"
    echo "Example: $0 arm64"
    exit 1
fi

ARCH="$1"
APP_NAME="Pucoti"
BUILD_DIR="dist/linux_${ARCH}/${APP_NAME}"
APPDIR="${APP_NAME}.AppDir"
BINARY_NAME="pucoti-linux_${ARCH}"

echo "Creating AppImage for ${APP_NAME} (${ARCH})"

# Check if build directory exists
if [ ! -d "${BUILD_DIR}" ]; then
    echo "Error: Build directory ${BUILD_DIR} not found"
    echo "Please run the Linux build first"
    exit 1
fi

# Clean up any previous AppDir
rm -rf "${APPDIR}"

# Create AppDir structure
echo "Creating AppDir structure..."
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/share/applications"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

# Copy application files
echo "Copying application files..."
cp "${BUILD_DIR}/${BINARY_NAME}" "${APPDIR}/usr/bin/"
cp "${BUILD_DIR}/resources.neu" "${APPDIR}/usr/bin/"

# Copy extensions if they exist
if [ -d "${BUILD_DIR}/extensions" ]; then
    echo "Copying extensions..."
    cp -r "${BUILD_DIR}/extensions" "${APPDIR}/usr/bin/"
fi

# Copy desktop file
echo "Copying desktop file..."
cp "${BUILD_DIR}/${APP_NAME}.desktop" "${APPDIR}/usr/share/applications/"

# Copy and setup icons
echo "Setting up icons..."
cp packaging/icons/pucoti.png "${APPDIR}/usr/share/icons/hicolor/256x256/apps/pucoti.png"
cp packaging/icons/pucoti.png "${APPDIR}/pucoti.png"

# Create AppRun script
echo "Creating AppRun script..."
cat > "${APPDIR}/AppRun" << EOF
#!/bin/bash
HERE="\$(dirname "\$(readlink -f "\${0}")")"
export PATH="\${HERE}/usr/bin:\${PATH}"
cd "\${HERE}/usr/bin"
exec "./${BINARY_NAME}" "\$@"
EOF
chmod +x "${APPDIR}/AppRun"

# Update desktop file for AppImage
echo "Updating desktop file..."
sed -i "s|{APP_NAME}|${APP_NAME}|g" "${APPDIR}/usr/share/applications/${APP_NAME}.desktop"
sed -i "s|{APP_ICON_PATH}|pucoti|g" "${APPDIR}/usr/share/applications/${APP_NAME}.desktop"
sed -i "s|{APP_EXEC}|${BINARY_NAME}|g" "${APPDIR}/usr/share/applications/${APP_NAME}.desktop"
sed -i "s|{APP_PATH}|/tmp|g" "${APPDIR}/usr/share/applications/${APP_NAME}.desktop"

# Copy desktop file to AppDir root
cp "${APPDIR}/usr/share/applications/${APP_NAME}.desktop" "${APPDIR}/"

echo "AppDir structure created successfully!"
echo "Contents of ${APPDIR}:"
find "${APPDIR}" -type f -exec ls -la {} \;

echo ""
echo "AppDir is ready for appimagetool"
echo "Run: appimagetool ${APPDIR} ${APP_NAME}-${ARCH}.AppImage"