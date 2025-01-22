{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [ nodejs pnpm ];

        NIX_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (with pkgs; [
          gdk-pixbuf
          glib
          gtk3
          webkitgtk
          xorg.libX11
          xorg.libxcb
          xorg.libXrandr
          cairo
          stdenv.cc.cc.lib
          libpng
        ]);
      };
    };
}
