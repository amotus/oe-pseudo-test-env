#!/usr/bin/env bash
set -euf -o pipefail
mkdir -p "$IMAGE_ROOTFS/etc"

declare ldsoconf_src="$IMAGE_ROOTFS/etc/ld.so.conf;613adfee"
echo "content of ld.so.conf source" > "$ldsoconf_src"

declare ldsoconf="$IMAGE_ROOTFS/etc/ld.so.conf"
mv "$ldsoconf_src" "$ldsoconf"

declare ldsoconf_prelink="$IMAGE_ROOTFS/etc/ld.so.conf.prelink"
echo "content of ld.so.conf.prelink first pass" > "$ldsoconf_prelink"
mv "$ldsoconf_prelink" "$ldsoconf"

declare ldsoconf_prelink="$IMAGE_ROOTFS/etc/ld.so.conf.prelink"
echo "content of ld.so.conf.prelink second pass" > "$ldsoconf_prelink"
mv "$ldsoconf_prelink" "$ldsoconf"
