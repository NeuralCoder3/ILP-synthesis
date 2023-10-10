{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    nativeBuildInputs = with pkgs.buildPackages; [ 
        minizinc
        gecode
        minizincide
    ];
}

# not working as intended use distrobox