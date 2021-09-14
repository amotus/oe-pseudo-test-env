#!/usr/bin/env bash
#
# Allow one to quickly set up a pseudo
# ready test environement so that all controlled
# files ends under './pseudo-test-fs/'.
#
# This can be use for interractive cli experiments.
#
# Should match as much as possible our python pseudo
# test tool environment at 'test_lib/pseudo.py'
# (see the '_mk_pseudo_env_d' function).
#
declare repo_root_dir="$PWD"

declare pseudo_path
if ! pseudo_path="$(2>/dev/null command -v pseudo)"; then
  # Fallback to our dev env's target build dir. It might
  # be that user still has to build pseudo.
  pseudo_path=$repo_root_dir/result/bin/pseudo
fi

declare pseudo_bin_dir
pseudo_bin_dir="$(dirname "$pseudo_path")"
declare pseudo_prefix_dir
pseudo_prefix_dir="$(dirname "$pseudo_bin_dir")"

declare state_dir="$repo_root_dir/pseudo-test-fs/state"
mkdir -p "$state_dir"

declare rootfs_dir="$repo_root_dir/pseudo-test-fs/rootfs"
mkdir -p "$rootfs_dir"

declare tmp_dir="$repo_root_dir/pseudo-test-fs/tmp"
mkdir -p "$tmp_dir"

declare ignore_paths_a=(
  "/usr/"
  "/etc/"
  "/lib"
  "/dev/"
  # Not skipping '/run' same as our python test
  # tool.
  # "/run/"
  "$tmp_dir"
  "$state_dir"
)

function join_by { local IFS="$1"; shift; echo "$*"; }

declare ignore_paths
ignore_paths="$(join_by , "${ignore_paths_a[@]}")"

export "PSEUDO_BINDIR=$pseudo_bin_dir"
export "PSEUDO_PREFIX=$pseudo_prefix_dir"
export "PSEUDO_LIBDIR=$pseudo_prefix_dir/lib/pseudo/lib"
export "PSEUDO_IGNORE_PATHS=$ignore_paths"
export "PSEUDO_DISABLED=0"
export "PSEUDO_LOCALSTATEDIR=$state_dir"
export "PSEUDO_PASSWD=$rootfs_dir"
export "PSEUDO_NOSYMLINKEXP=1"
export "PSEUDO_DISABLED=0"


export "IMAGE_ROOTFS=$rootfs_dir"

export "TMP=$tmp_dir"
export "TEMP=$tmp_dir"
export "TEMPDIR=$tmp_dir"
export "TMPDIR=$tmp_dir"
export "XDG_RUNTIME_DIR=$tmp_dir"
