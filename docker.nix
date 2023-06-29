{ pkgs ? (
    let
      inherit (builtins) fetchTree fromJSON readFile;
      inherit ((fromJSON (readFile ./flake.lock)).nodes) nixpkgs gomod2nix;
    in
    import (fetchTree nixpkgs.locked) {
      overlays = [
        (import "${fetchTree gomod2nix.locked}/overlay.nix")
      ];
    }
  )
}:
let 
  goApp = pkgs.callPackage ./. {};
in
pkgs.dockerTools.buildImage {
  name = "unifai-golang-backend";
  config = {
    Cmd = [ "${goApp}/bin/unifai" ];
  };
}
