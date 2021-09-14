{ srcs
, pickedSrcs
}:
self: super:

{
  # Tag to check that our overlay is already available.
  has-overlay-oe-pseudo-test-env = true;

  oe-pseudo = (import
    ../release.nix {
      pkgs = self;
    }).default;
}
