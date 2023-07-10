{ pkgs ? (
    let
      inherit (builtins) fetchTree fromJSON readFile;
      inherit ((fromJSON (readFile ./flake.lock)).nodes) nixpkgs gomod2nix;
    in
    import (fetchTree nixpkgs.locked) {
      overlays = [
        (import "${fetchTree gomod2nix.locked}/overlay.nix")
        (import "./overlay.nix")
      ];
    }
  )
}:

let
  goEnv = pkgs.mkGoEnv { pwd = ./.; };
  swaggo = pkgs.buildGoModule rec {
    pname = "swag";
    version = "v2.0.0-rc3";
    vendorHash = "sha256-izob4TK/mpb5q+OtP6Mp0UuAThW2CfHiEG2cTn+f2tA=";
		subPackages = ["cmd/swag"];
		allowGoReference = true;

    src = pkgs.fetchFromGitHub {
      owner = "swaggo";
      repo = "swag";
      rev = "c7b796dcb851ffca7e16b18bc91aa3696f6dadf5";
      sha256 = "oGkctKNNdcycyQa1ZdXSGVsh6VfgmcmXD9MyaotCfJQ=";
    };
  };
in
pkgs.mkShell {
  packages = [
    goEnv
		swaggo
    pkgs.gomod2nix
    pkgs.httpie
		
		pkgs.protoc-gen-go
		pkgs.protoc-gen-go-grpc
		pkgs.protobuf3_20
  ];
}
