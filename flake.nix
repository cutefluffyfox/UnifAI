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

        pypkgs-build-requirements = {
          asyncio = [ "setuptools" ];
          fastapi-jwt-auth = [ "flit-core" ];
        };
        p2n-overrides = defaultPoetryOverrides.extend (self: super:
          builtins.mapAttrs (package: build-requirements:
            (builtins.getAttr package super).overridePythonAttrs (old: {
              buildInputs = (old.buildInputs or [ ]) ++ (builtins.map (pkg: if builtins.isString pkg then builtins.getAttr pkg super else pkg) build-requirements);
            })
          ) pypkgs-build-requirements
        );
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
            ];
            packages = [
              poetry2nix.packages.${system}.poetry
            ];
          };
      });
}
