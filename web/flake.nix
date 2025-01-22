{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          nodejs
          pnpm

          gst_all_1.gstreamer
          gst_all_1.gst-plugins-base
          (gst_all_1.gst-plugins-good.override { gtkSupport = true; }) # gtksink
          gst_all_1.gst-plugins-bad
        ];

        NIX_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (with pkgs; [
          gdk-pixbuf
          glib
          gtk3
          webkitgtk_4_1
          xorg.libX11
          xorg.libxcb
          xorg.libXrandr
          cairo
          stdenv.cc.cc.lib
          libpng

          gst_all_1.gstreamer
          gst_all_1.gst-plugins-base
          (gst_all_1.gst-plugins-good.override { gtkSupport = true; }) # gtksink
          gst_all_1.gst-plugins-bad
          gst_all_1.gst-plugins-ugly
          gst_all_1.gst-libav
          gst_all_1.gst-vaapi
          fdk_aac
          fdk-aac-encoder
        ]);
      };
    };
}
