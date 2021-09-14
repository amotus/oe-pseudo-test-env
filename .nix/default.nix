{ pkgs ? null
, workspaceDir ? null
, fromNixosModule ? false
}:

assert null == workspaceDir
  || (builtins.isPath workspaceDir)
  || ("/" == builtins.substring 0 1 workspaceDir);

let
  pinnedSrcsDir = ./pinned-src;
  nsfp = rec {
    localPath = /. + workspaceDir + "/nsf-pin";
    srcInfoJson = pinnedSrcsDir + "/nsf-pin/channel/default.json";
    srcInfo = builtins.fromJSON (builtins.readFile srcInfoJson);
    channels =
      assert srcInfo.type == "fetchFromGitHub";
      with srcInfo;
      {
        default = rec {
          version = {
            inherit ref rev;
            url = "https://github.com/${owner}/${repo}";
          };
          src = builtins.fetchTarball (with version; {
            url = "${url}/archive/${rev}.tar.gz";
            sha256 = "${srcInfo.sha256}";
          });
        };
      };

    pinnedSrcPath = channels.default.src;
    srcPath =
      if null != workspaceDir
          && builtins.pathExists localPath
        then localPath
        else pinnedSrcPath;

    nixLib = (import (srcPath + "/release.nix") { inherit pkgs; }).nix-lib;
  };
in

rec {
  srcs = nsfp.nixLib.mkSrcDir {
    inherit pinnedSrcsDir;
    inherit workspaceDir;
    srcPureIgnores = {};
    inherit pkgs;
  };

  nixosPickedSrcs = {
    nixpkgs =
      { src = <nixpkgs>; version = <nixpkgs-version>; };
    nsf-pin =
      { src = <nsf-pin>; version = <nsf-pin-version>; };
  };

  pickedSrcs =
    if fromNixosModule
      then nixosPickedSrcs
    else
      builtins.mapAttrs (k: v: v.default) srcs.localOrPinned;

  # This repo's publicly exposed overlay.
  overlay = import ./overlay.nix { inherit srcs pickedSrcs; };

  # This repo's overlay.
  overlayInternal = import ./overlay-internal.nix { inherit srcs pickedSrcs; };

  # The set of overlays used by this repo.
  overlays = [
    overlay
    overlayInternal
  ];


  # This constitutes our default nixpkgs.
  nixpkgsSrc = srcs.pinned.nixpkgs.default.src;
  nixpkgs = nixpkgsSrc;

  #
  # Both of the following can be used from release files.
  #
  importPkgs = { nixpkgs ? null } @ args:
      let
        nixpkgs =
          if args ? "nixpkgs" && null != args.nixpkgs
            then args.nixpkgs
            else nixpkgsSrc;  # From top level.
      in
    assert null != nixpkgs;
    import nixpkgs { inherit overlays; };


  ensurePkgs = { pkgs ? null, nixpkgs ? null }:
    if null != pkgs
      then
        if pkgs ? "has-overlay-oe-pseudo-test-env-internal"
            # Avoid extending a `pkgs` that already has our overlays.
          then pkgs
        else
          pkgs.appendOverlays overlays
    else
      importPkgs { inherit nixpkgs; };
}
