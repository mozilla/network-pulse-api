{ pkgs ? import (fetchTarball channel:nixpkgs-19.03-darwin) {} }:

pkgs.mkShell {
  buildInputs = [ pkgs.python37 pkgs.python37Packages.invoke];
}
