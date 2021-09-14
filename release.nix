{ pkgs ? null} @ args:

let
  pkgs = (import ./.nix/default.nix {}).ensurePkgs args;
in

with pkgs;

let
  default = callPackage ./. {};
  env = buildEnv {
    name = "${default.pname}-build-env";
    paths = [ default ];
  };

  defaultLocal = default.overrideAttrs (old: {
    version = "git";
    src = ../pseudo;
  });

  devPython = python3.withPackages (pp: with pp; [
    ipython
    mypy
    flake8
    pytest
    psutil
  ]);

  commonDeps = [
    nix
    gnumake
    devPython
    bashInteractive
    sqlite
  ];

in

{
  inherit default env;
  inherit defaultLocal;

  shell = {
    dev = mkShell rec {
      name = "${default.pname}-dev-shell";

      inputsFrom = [
        default
      ];

      buildInputs = [
      ] ++ commonDeps;

      shellHook = ''
        shell_dir="${toString ./.}"
        export PATH="${builtins.toString ./result/bin}:$PATH"
      '';
    };

    installed = mkShell rec {
      name = "${default.pname}-installed-shell";

      buildInputs = [
        env
      ] ++ commonDeps;

      shellHook = ''
      '';
    };
  };
}
