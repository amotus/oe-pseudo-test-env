{ lib
, stdenv
, fetchgit
, makeWrapper
, python3
, sqlite
, attr
}:

let
  target = stdenv.targetPlatform;
  pseudoPlatform =
    if target.is64bit then {
      bits = "64";
      libDirSuffix = "64";
    }
    else if target.is32bit then {
      bits = "32";
      libDirSuffix = "";
    }
    else throw "Not supported on ${target.system}.";
in

stdenv.mkDerivation rec {
  version = "unstable-2021-09-10";
  pname = "oe-pseudo";

  src = fetchgit {
    url = "https://git.yoctoproject.org/git/pseudo";
    # From 'oe-core' branch.
    rev = "b988b0a6b8afd8d459bc9a2528e834f63a3d59b2";
    sha256 = "10qx9i1y8ddqhbsj9777920wqfgqpjmg2q6zzjm6yrqkf6bbd363";
  };

  nativeBuildInputs = [
    makeWrapper
    python3
    attr
  ];

  buildInputs = [
    sqlite
  ];

  postPatch = ''
    patchShebangs --build .
  '';

  configurePhase = ''
    runHook preConfigure
    ./configure \
      --enable-force-async --without-passwd-fallback --enable-epoll --enable-xattr \
      --prefix="$out" \
      --libdir="$out/lib/pseudo/lib${pseudoPlatform.libDirSuffix}" \
      --with-sqlite-lib="${sqlite.dev}/lib" \
      --with-sqlite="${sqlite.dev}" \
      --cflags="$CFLAGS" \
      --bits="${pseudoPlatform.bits}" \
      --without-rpath
    runHook postConfigure
  '';

  meta = with lib; {
    description = "pseudo -- an analogue to sudo";
  };
}
