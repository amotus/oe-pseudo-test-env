#!/usr/bin/env bash
set -euf -o pipefail
mkdir -p "$IMAGE_ROOTFS/etc"

declare ldsoconf="$IMAGE_ROOTFS/etc/ld.so.conf"

declare ldsoconf_prelink="$IMAGE_ROOTFS/etc/ld.so.conf.prelink"
echo "content of ld.so.conf.prelink first pass" > "$ldsoconf_prelink"
# Target does not exist for the first pass.
mv "$ldsoconf_prelink" "$ldsoconf"

echo "content of ld.so.conf.prelink second pass" > "$ldsoconf_prelink"
# Target exists for the second pass.
mv "$ldsoconf_prelink" "$ldsoconf"
