{
  description = "Application packaged using poetry2nix";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        inherit (poetry2nix.legacyPackages.${system}) mkPoetryApplication mkPoetryEnv defaultPoetryOverrides;
        pkgs = nixpkgs.legacyPackages.${system};

        p2n-overrides = defaultPoetryOverrides.extend (self: super: {
            pyaudio = super.pyaudio.overridePythonAttrs (
              old: {
                  buildInputs = (old.buildInputs or [ ]) ++ [ pkgs.portaudio ];
                }
            );
          });
      in
      {
        packages = {
          myapp = mkPoetryApplication { projectDir = self; overrides = p2n-overrides; };

          default = self.packages.${system}.devEnv;

          devEnv = mkPoetryEnv {
            projectDir = self;
            overrides = p2n-overrides;
          };
        };

        devShells.default = pkgs.mkShell {
            buildInputs = [
              self.packages.${system}.devEnv
              pkgs.portaudio
            ];
            packages = [
              poetry2nix.packages.${system}.poetry
            ];
          };
      });
}
