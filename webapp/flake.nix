{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";

  outputs = { nixpkgs, ... }:
    let pkgs = nixpkgs.legacyPackages."x86_64-linux";
        buildInputs = with pkgs; [
                  gtk3
                  glib
                  cairo
                  pango
                  gdk-pixbuf
                  atk
                  at-spi2-atk
                  at-spi2-core
                  dbus
                  libappindicator-gtk3
                  webkitgtk_4_1
                  xorg.libX11
                  xorg.libXext
                  xorg.libXrender
                  xorg.libXtst
                  xorg.libxcb
                  xorg.libXcomposite
                  xorg.libXdamage
                  xorg.libXfixes
                  xorg.libXrandr
                  xorg.libXi
                  xorg.libXcursor
                  xorg.libXinerama
                  libpng
                  libjpeg
                  libGL
                  libGLU
                  mesa
                  fontconfig
                  freetype
                  # Not needed
                  # stdenv.cc.cc.lib
                  # glibc
                  gst_all_1.gstreamer
                  gst_all_1.gst-plugins-base
                  gst_all_1.gst-plugins-good
                  gst_all_1.gst-plugins-bad
                  gst_all_1.gst-plugins-ugly
                ];
    in {
      devShells."x86_64-linux".default = pkgs.mkShell {
        nativeBuildInputs = [ pkgs.nodejs_24 pkgs.pnpm pkgs.git pkgs.jq   ];
        inherit buildInputs;
        shellHook = ''
          export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath buildInputs}:$LD_LIBRARY_PATH
          export GST_PLUGIN_PATH=${pkgs.gst_all_1.gstreamer}/lib/gstreamer-1.0:${pkgs.gst_all_1.gst-plugins-base}/lib/gstreamer-1.0:${pkgs.gst_all_1.gst-plugins-good}/lib/gstreamer-1.0:${pkgs.gst_all_1.gst-plugins-bad}/lib/gstreamer-1.0:${pkgs.gst_all_1.gst-plugins-ugly}/lib/gstreamer-1.0
        '';
      };
    };
}
