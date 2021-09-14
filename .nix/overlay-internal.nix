{ srcs
, pickedSrcs
}:
self: super:
let
  nsf-pin = import "${pickedSrcs.nsf-pin.src}/release.nix" {
    pkgs = self;
  };
in
{
  # Tag to check that our overlay is already available.
  has-overlay-oe-pseudo-test-env-internal = true;

  nsf-pin-cli = nsf-pin.cli;
  nsf-pin-nix-lib = nsf-pin.nix-lib;
}
