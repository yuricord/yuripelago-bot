{
  description = "Archi-Bot V2 Devshell";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
  };
  outputs =
    { nixpkgs, ... }:
    let
      pkgs = import nixpkgs {
        allowUnfree = true;
        system = "x86_64-linux";
      };
    in
    {
      packages.x86_64-linux = {
      };
      apps.x86_64-linux = {
      };

      devShells.x86_64-linux.default = pkgs.mkShell {
        strictDeps = true;

        buildInputs = [
          pkgs.openssl
          pkgs.pkg-config
        ];
        nativeBuildInputs = [
          pkgs.bacon
          pkgs.just
          pkgs.rustup
          pkgs.rustPlatform.bindgenHook
          pkgs.nixfmt-rfc-style
          pkgs.sea-orm-cli
          pkgs.sqlite
          pkgs.pkg-config
        ];
      };
    };
}
