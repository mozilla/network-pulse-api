{ pkgs ? import (fetchTarball https://github.com/NixOS/nixpkgs-channels/archive/nixpkgs-18.09-darwin.tar.gz) {} }:

# To be replaced when the last version of pipenv is available
let pipenv = pkgs.pipenv.overrideAttrs (attrs: {name = "pipenv-2018-10-9"; src = pkgs.python3Packages.fetchPypi { pname = "pipenv"; version = "2018.10.9"; sha256 = "0b0safavjxq6malmv44acmgds21m2sp1wqa7gs0qz621v6gcgq4j";};}); in

  pkgs.mkShell {
    buildInputs = [ pkgs.python36 pipenv pkgs.python36Packages.invoke];
}
